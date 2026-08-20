"""
W1 harness — ceiling pre-test for silence probe v2 (Task 2.4).

Runs the frozen w1_stimuli.json across the seven-configuration roster and writes
one results JSON. Produces no silence claim; this is a format go/no-go.

Usage, from the repo root:

    python w1_harness.py --stub                  # plumbing check, no network
    python w1_harness.py --preflight             # one real call, verify auth + slugs
    python w1_harness.py                         # full run, resumable
    python w1_harness.py --configs sol-none glm  # subset

Harness requirements carried from the three v1 bug classes:

  * PREFLIGHT. One real call before the grid starts, so a bad key or a retired slug
    surfaces immediately instead of forty minutes in.
  * FAIL-FAST ON AUTH. 401/403 raises. v1 retried these with exponential backoff,
    which made a bad key look like a hang.
  * RESUME KEYS ON SUCCESSES ONLY. v1's resume skipped failed draws, silently
    dropping 33 of them while reporting full row counts.
  * TRUNCATION IS NOT A PARSE ERROR. v1 lost 45% of one condition and 0% of every
    other because finish_reason=="length" arrived disguised as bad JSON, and the
    model reasons longest exactly where the task is hardest. Truncation that
    correlates with difficulty is informative missingness and must be visible.
  * max_tokens IS PER CONFIG, NOT GLOBAL. Reasoning tokens count against the same
    budget.
  * requests, NOT urllib. The macOS Anaconda build has no CA bundle wired in and
    urllib fails TLS verification against OpenRouter.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
STIM_PATH = "w1_stimuli.json"
EXPECTED_SHA = "e747d942f5b14d46ecb5ed81b60e769878e2ca95cf6739d47a5e9ec66ad7bbe0"
OUT_DIR = "results_w1"

def paths(stub):
    """
    Stub and live runs MUST NOT share a checkpoint. They did in the first draft, and
    because resume keys on successful draws a stub run would have silently satisfied
    every key and made the live run a no-op that reported 672/672. Exactly the class
    of silent-success bug v1 was bitten by three times.
    """
    tag = "stub" if stub else "live"
    return (os.path.join(OUT_DIR, f"checkpoint_{tag}.jsonl"),
            os.path.join(OUT_DIR, f"w1_results_{tag}.json"))

DRAWS = 3
SEEDS = (1, 2, 3)
MAX_RETRIES = 3
WORKERS = 8

# max_tokens is per config. Default-mode configs emit a two-key object and need
# almost nothing; high-effort configs spend the budget on reasoning before the
# object appears.
CONFIGS = {
    "sol-none": {
        "slug": "openai/gpt-5.6-sol",
        "reasoning": {"effort": "none"},
        "temperature": None,          # Sol does not accept it; draws vary by seed
        "max_tokens": 800,
    },
    "sol-high": {
        "slug": "openai/gpt-5.6-sol",
        "reasoning": {"effort": "high"},
        "temperature": None,
        "max_tokens": 4000,
    },
    "deepseek": {
        "slug": "deepseek/deepseek-v4-flash-0731",
        "reasoning": {"enabled": False},
        "temperature": 0.7,
        "max_tokens": 800,
    },
    "deepseek-high": {
        "slug": "deepseek/deepseek-v4-flash-0731",
        "reasoning": {"enabled": True},
        "temperature": 0.7,
        "max_tokens": 4000,
    },
    "glm": {
        "slug": "z-ai/glm-5.2",
        "reasoning": {"enabled": False},
        "temperature": 0.7,
        "max_tokens": 800,
    },
    "glm-high": {
        "slug": "z-ai/glm-5.2",
        "reasoning": {"enabled": True},
        "temperature": 0.7,
        "max_tokens": 4000,
    },
    "anchor": {
        "slug": "meta-llama/llama-3.3-70b-instruct",
        "reasoning": None,            # no reasoning machinery
        "temperature": 0.7,
        "max_tokens": 400,
    },
}

DEFAULT_MODE = ("sol-none", "deepseek", "glm")
HIGH_MODE = ("sol-high", "deepseek-high", "glm-high")


class AuthError(RuntimeError):
    pass


# ------------------------------------------------------------------ stimuli

def load_stimuli(path=STIM_PATH):
    with open(path) as f:
        payload = json.load(f)
    declared = payload.pop("sha256", None)
    blob = json.dumps(payload, indent=2, sort_keys=True)
    actual = hashlib.sha256(blob.encode()).hexdigest()
    if declared != actual:
        raise SystemExit(f"stimulus hash mismatch\n  declared {declared}\n  actual   {actual}")
    if actual != EXPECTED_SHA:
        raise SystemExit(f"stimulus file is not the frozen one\n  got {actual}")
    payload["sha256"] = actual
    return payload


# ------------------------------------------------------------------ calling

def call(cfg, stim, seed, api_key):
    """One draw. Returns a result dict; never raises except on auth."""
    body = {
        "model": cfg["slug"],
        "messages": [{"role": "user", "content": stim["prompt"]}],
        "response_format": stim["response_format"],
        "max_tokens": cfg["max_tokens"],
        "seed": seed,
    }
    if cfg["temperature"] is not None:
        body["temperature"] = cfg["temperature"]
    if cfg["reasoning"] is not None:
        body["reasoning"] = cfg["reasoning"]

    last = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(
                ENDPOINT,
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json=body,
                timeout=180,
            )
        except requests.RequestException as e:
            last = f"transport: {e}"
            time.sleep(2 ** attempt)
            continue

        if resp.status_code in (401, 403):
            # fail fast, do NOT back off -- v1 bug class 1
            raise AuthError(f"{resp.status_code} from OpenRouter: {resp.text[:300]}")
        if resp.status_code != 200:
            last = f"http {resp.status_code}: {resp.text[:300]}"
            time.sleep(2 ** attempt)
            continue

        data = resp.json()
        choice = (data.get("choices") or [{}])[0]
        finish = choice.get("finish_reason")
        content = (choice.get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
        reasoning_tokens = (usage.get("completion_tokens_details") or {}).get(
            "reasoning_tokens")

        # truncation is its own failure mode -- v1 bug class 3
        if finish == "length":
            return {"ok": False, "failure": "TRUNCATED", "finish_reason": finish,
                    "raw": content[:200], "reasoning_tokens": reasoning_tokens}

        parsed, why = parse(content, stim)
        if parsed is None:
            return {"ok": False, "failure": "PARSE", "detail": why,
                    "finish_reason": finish, "raw": content[:200],
                    "reasoning_tokens": reasoning_tokens}

        return {"ok": True, "candidate": parsed[0], "confidence": parsed[1],
                "finish_reason": finish, "reasoning_tokens": reasoning_tokens}

    return {"ok": False, "failure": "REQUEST", "detail": last}


def parse(content, stim):
    """Strict parse against the stimulus's own enums. D16: no partial credit."""
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        obj = json.loads(text)
    except Exception as e:
        return None, f"json: {e}"
    if not isinstance(obj, dict):
        return None, "not an object"

    schema = stim["response_format"]["json_schema"]["schema"]["properties"]
    cands = schema["candidate"]["enum"]
    confs = schema["confidence"]["enum"]

    c = obj.get("candidate")
    k = obj.get("confidence")
    if c not in cands:
        return None, f"candidate {c!r} off menu"
    if k not in confs:
        return None, f"confidence {k!r} off menu"
    return (c, k), None


def stub_call(cfg, stim, seed):
    """Model-obedient responder. Plumbing check only; no network."""
    return {"ok": True, "candidate": stim["expected_candidate"],
            "confidence": stim["expected_confidence"],
            "finish_reason": "stop", "reasoning_tokens": 0}


# ------------------------------------------------------------------ run

def key_of(config, stim_id, seed):
    return f"{config}|{stim_id}|{seed}"


def load_checkpoint(checkpoint):
    """Resume keys on SUCCESSES ONLY -- v1 bug class 2."""
    done = {}
    if not os.path.exists(checkpoint):
        return done
    with open(checkpoint) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("ok"):
                done[key_of(rec["config"], rec["stimulus_id"], rec["seed"])] = rec
    return done


def run(configs, stimuli, api_key, stub=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    checkpoint, _ = paths(stub)
    done = load_checkpoint(checkpoint)
    if done:
        print(f"resuming: {len(done)} successful draws already on disk")

    jobs = []
    for cname in configs:
        for stim in stimuli:
            for seed in SEEDS[:DRAWS]:
                if key_of(cname, stim["id"], seed) in done:
                    continue
                jobs.append((cname, stim, seed))

    print(f"{len(jobs)} draws to run across {len(configs)} configurations")
    if not jobs:
        return list(done.values())

    out = open(checkpoint, "a")
    records = list(done.values())
    n_fail = 0

    def work(job):
        cname, stim, seed = job
        cfg = CONFIGS[cname]
        res = stub_call(cfg, stim, seed) if stub else call(cfg, stim, seed, api_key)
        res.update({"config": cname, "slug": cfg["slug"], "stimulus_id": stim["id"],
                    "family": stim["family"], "wording": stim["wording"], "seed": seed})
        return res

    with ThreadPoolExecutor(max_workers=1 if stub else WORKERS) as ex:
        futs = {ex.submit(work, j): j for j in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                rec = fut.result()
            except AuthError as e:
                out.close()
                raise SystemExit(f"\nAUTH FAILURE, stopping immediately: {e}")
            out.write(json.dumps(rec) + "\n")
            out.flush()
            records.append(rec)
            if not rec["ok"]:
                n_fail += 1
            if i % 50 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)}  failures so far: {n_fail}")

    out.close()
    return records


def missingness(records, stimuli):
    """Per-condition missingness audit. Truncation reported separately by design."""
    by = {}
    for r in records:
        k = (r["config"], r["family"], r["wording"])
        d = by.setdefault(k, {"n": 0, "ok": 0, "TRUNCATED": 0, "PARSE": 0, "REQUEST": 0})
        d["n"] += 1
        if r["ok"]:
            d["ok"] += 1
        else:
            d[r.get("failure", "REQUEST")] = d.get(r.get("failure", "REQUEST"), 0) + 1
    return {"|".join(k): v for k, v in sorted(by.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--configs", nargs="*", default=list(CONFIGS))
    args = ap.parse_args()

    payload = load_stimuli()
    stimuli = payload["stimuli"]
    print(f"stimuli ok: {len(stimuli)}  sha256 {payload['sha256'][:16]}...")

    for c in args.configs:
        if c not in CONFIGS:
            raise SystemExit(f"unknown config {c!r}")

    api_key = None
    if not args.stub:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise SystemExit("OPENROUTER_API_KEY not set. "
                             "Run: set -a && source .env && set +a")

    if args.preflight:
        cname = args.configs[0]
        stim = stimuli[0]
        print(f"preflight: {cname} on {stim['id']}")
        res = call(CONFIGS[cname], stim, 1, api_key)
        print(json.dumps(res, indent=2))
        if not res["ok"]:
            raise SystemExit("preflight failed -- fix before running the grid")
        print("preflight OK")
        return

    t0 = time.time()
    records = run(args.configs, stimuli, api_key, stub=args.stub)
    elapsed = time.time() - t0

    audit = missingness(records, stimuli)
    result = {
        "task": "2.4 W1 ceiling pre-test",
        "stimulus_sha256": payload["sha256"],
        "stub": args.stub,
        "configs": {c: CONFIGS[c] for c in args.configs},
        "draws_per_stimulus": DRAWS,
        "seeds": list(SEEDS[:DRAWS]),
        "n_records": len(records),
        "n_ok": sum(1 for r in records if r["ok"]),
        "elapsed_sec": round(elapsed, 1),
        "missingness": audit,
        "records": records,
    }
    _, results_path = paths(args.stub)
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{result['n_ok']}/{result['n_records']} draws ok in {elapsed:.0f}s")
    print(f"written to {results_path}")
    bad = {k: v for k, v in audit.items() if v["ok"] < v["n"]}
    if bad:
        print("\nMISSINGNESS (inspect before analysing):")
        for k, v in bad.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
