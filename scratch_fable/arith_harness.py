"""arith_harness.py — run harness for the ARITH_D30 arithmetic control (630 calls).

Adapted from silence_v2_harness.py with the same roster and the same three v1
bug-class defences, writing ONLY under scratch_fable/.

    python scratch_fable/arith_harness.py --stub         # plumbing check, no network
    python scratch_fable/arith_harness.py --preflight    # one real call
    python scratch_fable/arith_harness.py                # full run, resumable
    python scratch_fable/arith_harness.py --bump 1.5     # truncation-retry pass at
                                                         # 1.5x max_tokens (see below)

Defences carried over:
  * PREFLIGHT before the grid.
  * FAIL-FAST on 401/403.
  * RESUME on successes and terminal failures only. Off-menu (PARSE) and REQUEST
    failures are marked terminal AT WRITE TIME — they are counted, never retried
    (D16); no decontamination pass can ever be needed.
  * TRUNCATED is its own failure mode, never surfaced as a parse error, and is NOT
    terminal: re-running the harness retries only truncations. Use --bump on that
    retry pass to raise max_tokens; completing an interrupted measurement at the same
    prompt and seed is not selection (fix_run.py rationale).
  * max_tokens per config: high-effort budgets at the post-fix 12000/16000/16000.
  * requests, not urllib.
"""

import argparse
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
STIM = f"{ROOT}/scratch_fable/arith_d30_stimuli.json"
SHA = "fc01116d6e8e91dd14d7b4fea8183dc42640ebb0d8bfa53e4fd3a2801e8c3044"
OUT_DIR = f"{ROOT}/scratch_fable/results_arith"

DRAWS = 5
SEEDS = (1, 2, 3, 4, 5)
MAX_RETRIES = 3
WORKERS = 8

CONFIGS = {
    "sol-none": {"slug": "openai/gpt-5.6-sol", "reasoning": {"effort": "none"},
                 "temperature": None, "max_tokens": 800},
    "sol-high": {"slug": "openai/gpt-5.6-sol", "reasoning": {"effort": "high"},
                 "temperature": None, "max_tokens": 12000},
    "deepseek": {"slug": "deepseek/deepseek-v4-flash-0731",
                 "reasoning": {"enabled": False}, "temperature": 0.7, "max_tokens": 800},
    "deepseek-high": {"slug": "deepseek/deepseek-v4-flash-0731",
                      "reasoning": {"enabled": True}, "temperature": 0.7,
                      "max_tokens": 16000},
    "glm": {"slug": "z-ai/glm-5.2", "reasoning": {"enabled": False},
            "temperature": 0.7, "max_tokens": 800},
    "glm-high": {"slug": "z-ai/glm-5.2", "reasoning": {"enabled": True},
                 "temperature": 0.7, "max_tokens": 16000},
    "anchor": {"slug": "meta-llama/llama-3.3-70b-instruct", "reasoning": None,
               "temperature": 0.7, "max_tokens": 400},
}


class AuthError(RuntimeError):
    pass


def paths(stub):
    tag = "stub" if stub else "live"
    return (os.path.join(OUT_DIR, f"checkpoint_arith_{tag}.jsonl"),
            os.path.join(OUT_DIR, f"arith_results_{tag}.json"))


def load_stimuli():
    with open(STIM) as f:
        payload = json.load(f)
    declared = payload.pop("sha256", None)
    blob = json.dumps(payload, indent=2, sort_keys=True)
    actual = hashlib.sha256(blob.encode()).hexdigest()
    if declared != actual:
        raise SystemExit(f"stimulus hash mismatch\n  declared {declared}\n  actual   {actual}")
    if actual != SHA:
        raise SystemExit(f"stimulus file is not the frozen one\n  got {actual}")
    payload["sha256"] = actual
    return payload


def parse(content, stim):
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
    c, k = obj.get("candidate"), obj.get("confidence")
    if c not in schema["candidate"]["enum"]:
        return None, f"candidate {c!r} off menu"
    if k not in schema["confidence"]["enum"]:
        return None, f"confidence {k!r} off menu"
    return (c, k), None


def call(cfg, stim, seed, api_key, bump):
    body = {
        "model": cfg["slug"],
        "messages": [{"role": "user", "content": stim["prompt"]}],
        "response_format": stim["response_format"],
        "max_tokens": int(cfg["max_tokens"] * bump),
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
                json=body, timeout=180)
        except requests.RequestException as e:
            last = f"transport: {e}"
            time.sleep(2 ** attempt)
            continue
        if resp.status_code in (401, 403):
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

        if finish == "length":
            # truncation is truncation, and it is retryable on a later pass
            return {"ok": False, "failure": "TRUNCATED", "finish_reason": finish,
                    "raw": content[:200], "reasoning_tokens": reasoning_tokens}

        parsed, why = parse(content, stim)
        if parsed is None:
            # off-menu is a model output to be counted, never retried (D16)
            return {"ok": False, "failure": "PARSE", "detail": why, "terminal": True,
                    "finish_reason": finish, "raw": content[:200],
                    "reasoning_tokens": reasoning_tokens}

        return {"ok": True, "candidate": parsed[0], "confidence": parsed[1],
                "finish_reason": finish, "reasoning_tokens": reasoning_tokens}

    return {"ok": False, "failure": "REQUEST", "detail": last, "terminal": True}


def stub_call(cfg, stim, seed):
    return {"ok": True, "candidate": stim["expected_candidate"],
            "confidence": stim["expected_confidence"],
            "finish_reason": "stop", "reasoning_tokens": 0}


def key_of(config, stim_id, seed):
    return f"{config}|{stim_id}|{seed}"


def load_checkpoint(checkpoint):
    done = {}
    if not os.path.exists(checkpoint):
        return done
    with open(checkpoint) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("ok") or rec.get("terminal"):
                done[key_of(rec["config"], rec["stimulus_id"], rec["seed"])] = rec
    return done


def run(configs, stimuli, api_key, stub, bump):
    os.makedirs(OUT_DIR, exist_ok=True)
    checkpoint, _ = paths(stub)
    done = load_checkpoint(checkpoint)
    if done:
        print(f"resuming: {len(done)} settled draws already on disk")

    jobs = [(c, s, seed) for c in configs for s in stimuli for seed in SEEDS[:DRAWS]
            if key_of(c, s["id"], seed) not in done]
    print(f"{len(jobs)} draws to run across {len(configs)} configurations")
    if not jobs:
        return list(done.values())

    out = open(checkpoint, "a")
    records = list(done.values())
    n_fail = 0

    def work(job):
        cname, stim, seed = job
        cfg = CONFIGS[cname]
        res = stub_call(cfg, stim, seed) if stub else call(cfg, stim, seed, api_key, bump)
        res.update({"config": cname, "slug": cfg["slug"], "stimulus_id": stim["id"],
                    "cell": stim["cell"], "condition": stim["condition"],
                    "group": stim["group"],
                    "target_is_first": stim["target_is_first"], "seed": seed})
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


def missingness(records):
    by = {}
    for r in records:
        k = (r["config"], r["condition"])
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
    ap.add_argument("--bump", type=float, default=1.0,
                    help="multiply max_tokens on a truncation-retry pass")
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
        res = call(CONFIGS[cname], stim, 1, api_key, args.bump)
        print(json.dumps(res, indent=2))
        if not res["ok"]:
            raise SystemExit("preflight failed -- fix before running the grid")
        print("preflight OK")
        return

    t0 = time.time()
    records = run(args.configs, stimuli, api_key, args.stub, args.bump)
    elapsed = time.time() - t0

    result = {
        "task": "2.4b ARITHMETIC CONTROL delta=0.30",
        "stimulus_sha256": payload["sha256"],
        "stub": args.stub,
        "configs": {c: CONFIGS[c] for c in args.configs},
        "draws_per_stimulus": DRAWS,
        "seeds": list(SEEDS[:DRAWS]),
        "n_records": len(records),
        "n_ok": sum(1 for r in records if r["ok"]),
        "elapsed_sec": round(elapsed, 1),
        "missingness": missingness(records),
        "records": records,
    }
    _, results_path = paths(args.stub)
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n{result['n_ok']}/{result['n_records']} draws ok in {elapsed:.0f}s")
    print(f"written to {results_path}")
    bad = {k: v for k, v in result["missingness"].items() if v["ok"] < v["n"]}
    if bad:
        print("\nMISSINGNESS (inspect before analysing):")
        for k, v in bad.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
