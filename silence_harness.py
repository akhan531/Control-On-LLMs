"""
silence_harness.py — runs the Task 2.4 grid against OpenRouter.

Usage
-----
  # dry run, no network, must print s = 1.000000 in every cell:
  python silence_harness.py --run stub --block B1-CORE

  # real run:
  export OPENROUTER_API_KEY=sk-or-...
  python silence_harness.py --run anchor --block B1-CORE

Runs are named in RUNS below, one entry per row of spec §7. Results append to
results_2_4/<run>.jsonl as they arrive, so a crash or a Ctrl-C loses nothing and rerunning the
same command resumes where it stopped.

Design commitments from silence_probe_spec.md:
  §6  ten draws, seeds 1-10, fresh context per call, average the LOG-ODDS not the probabilities,
      clip to [0.001, 0.999] and report the clipped fraction, NO silent retry loop.
  §7  reasoning setting per run, seed always, temperature omitted where the model does not take it.
  §7.2 response_format json_schema, strict, with the per-stimulus schema from silence_stimuli.json.
  §11 requests, NOT urllib: the macOS Anaconda build has no CA bundle wired in and urllib fails TLS
      verification against OpenRouter.
  §13 the stimulus file is verified against its frozen sha256 before any call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    sys.exit("requests not installed. Run:  pip install requests")

class FatalAPIError(RuntimeError):
    """A failure that will recur on every call: bad key, bad slug, rejected parameter.

    These abort the run immediately. Recording them as per-draw failures and continuing would
    burn the whole grid producing nothing, which is exactly what happened on the first attempt.
    """


API_URL = "https://openrouter.ai/api/v1/chat/completions"
STIMULI = "silence_stimuli.json"
SHA256_FILE = "silence_stimuli.sha256"
OUTDIR = Path("results_2_4")

SEEDS = list(range(1, 11))  # §6: ten draws, seeds 1-10
CLIP_LO, CLIP_HI = 0.001, 0.999

# One entry per row of §7. Canonical slugs as recorded at freeze.
RUNS: Dict[str, dict] = {
    "anchor":      {"model": "meta-llama/llama-3.3-70b-instruct", "reasoning": None,               "temp": 0.7},
    "size":        {"model": "meta-llama/llama-3.1-8b-instruct",  "reasoning": None,               "temp": 0.7},
    "deepseek":    {"model": "deepseek/deepseek-v4-flash-20260731", "reasoning": {"enabled": False}, "temp": 0.7},
    "glm":         {"model": "z-ai/glm-5.2-20260616",             "reasoning": {"enabled": False}, "temp": 0.7},
    # Reasoning-enabled arms. These exist to replicate the none/high transition observed on Sol
    # using a model from a different lab, which is what turns that transition from a property of
    # one model into a property of inference effort. Budgeted at 8000: above Sol's observed
    # appetite, well below hy3's runaway.
    "deepseek-high": {"model": "deepseek/deepseek-v4-flash-20260731", "reasoning": {"enabled": True}, "temp": 0.7, "max_tokens": 8000},
    "glm-high":      {"model": "z-ai/glm-5.2-20260616",             "reasoning": {"enabled": True}, "temp": 0.7, "max_tokens": 8000},
    "hy3-none":    {"model": "tencent/hy3-20260706",              "reasoning": {"effort": "none"}, "temp": 0.7},
    # hy3 at high effort spends roughly an order of magnitude more reasoning than Sol does: 1584
    # tokens on a preflight call, and it hit a 2000 ceiling on the second draw of the grid. The
    # budget is per-run rather than global so that each run stays internally homogeneous; mixing
    # two ceilings inside one run truncates exactly the hard cells and nothing else.
    "hy3-high":    {"model": "tencent/hy3-20260706",              "reasoning": {"effort": "high"}, "temp": 0.7, "max_tokens": 16000},
    "sol-none":    {"model": "openai/gpt-5.6-sol-20260709",       "reasoning": {"effort": "none"}, "temp": None},
    "sol-high":    {"model": "openai/gpt-5.6-sol-20260709",       "reasoning": {"effort": "high"}, "temp": None},
    "stub":        {"model": "STUB-MODEL-OBEDIENT",               "reasoning": None,               "temp": None},
}

# Sol is Block 1 only (§5 Totals). Every other run covers all three blocks.
BLOCK1_ONLY = {"sol-none", "sol-high"}


# --------------------------------------------------------------------------------------


def load_stimuli(path: str = STIMULI) -> List[dict]:
    """Load a stimulus file and verify its hash before anything else happens."""
    blob = Path(path).read_text(encoding="utf-8")
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    expected = Path(path.replace(".json", ".sha256")).read_text().split()[0].strip()
    if digest != expected:
        sys.exit(
            f"STIMULUS HASH MISMATCH\n  file: {digest}\n  frozen: {expected}\n"
            "The stimulus file has changed since freeze. Per §13 this is an amendment with its own\n"
            "provenance, not a quiet fix. Refusing to run."
        )
    print(f"stimuli verified against frozen sha256 {digest[:16]}...")
    return json.loads(blob)


def logodds_from_probs(probs: Dict[str, float], target: str) -> tuple:
    """
    Target versus the aggregate of all non-targets, matching silence_model.logodds.

    Renormalizes first: models routinely emit probabilities summing to 0.99 or 1.01, and scoring
    an unnormalized vector would put that arithmetic slop into the measurement.

    Returns (logodds, was_clipped).
    """
    total = sum(probs.values())
    if total <= 0:
        raise ValueError("probabilities sum to zero")
    p_t = probs[target] / total
    clipped = False
    if p_t < CLIP_LO:
        p_t, clipped = CLIP_LO, True
    elif p_t > CLIP_HI:
        p_t, clipped = CLIP_HI, True
    return math.log(p_t / (1.0 - p_t)), clipped


def stub_response(stim: dict) -> Dict[str, float]:
    """
    A perfectly model-obedient responder: returns this condition's own correct answer exactly.

    §11 requires the dry run to recover s = 1.000 in every cell, so that any gap in a real run is
    provably the model and not the plumbing. The correct answer is read from the stimulus file's
    correct_logodds field, which silence_stimuli.py computed via silence_model, so this also
    round-trips model -> stimuli -> harness -> scoring and would catch a target/label mismatch.
    """
    lo = stim["correct_logodds"]
    p_t = 1.0 / (1.0 + math.exp(-lo))
    keys = list(stim["schema"]["json_schema"]["schema"]["properties"].keys())
    others = [k for k in keys if k != stim["target_label"]]
    out = {stim["target_label"]: p_t}
    for k in others:
        out[k] = (1.0 - p_t) / len(others)
    return out


def call_model(stim: dict, cfg: dict, seed: int, api_key: str) -> dict:
    """
    One draw. Fresh context, no history. Returns the parsed dict of probabilities.

    NO retry loop (§6). A model needing three attempts to emit a number is not producing draws
    comparable to one that emits cleanly, and averaging over that difference is exactly what a
    referee finds. Transport-level failures (timeout, 5xx, 429) are retried, because those are the
    network and not the model; a malformed or refused completion is recorded as a failure.
    """
    body = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": stim["prompt"]}],
        "response_format": stim["schema"],
        "seed": seed,
        # Reasoning tokens count against this budget on OpenRouter. At 400 the high-effort run
        # truncated 45% of the delta > 0.3 draws and 0% of everything else, because that is the
        # condition the model reasons longest about. Truncation that correlates with task
        # difficulty is informative missingness and silently discards the hard tail of the one
        # condition the claim depends on. Budget generously; unused tokens are not billed.
        "max_tokens": cfg.get("max_tokens", 2000),
    }
    if cfg["temp"] is not None:
        body["temperature"] = cfg["temp"]
    if cfg["reasoning"] is not None:
        body["reasoning"] = cfg["reasoning"]

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    last = None
    for attempt in range(4):  # transport retries only
        try:
            resp = requests.post(API_URL, headers=headers, json=body, timeout=120)

            # PERMANENT failures. Retrying these is pure waste: a bad key is bad on every call,
            # and at 4 attempts with exponential backoff that is 15 seconds of sleeping per call
            # across the whole grid, which reads as a hang rather than as an error. Abort the run.
            if resp.status_code in (401, 403):
                raise FatalAPIError(
                    f"HTTP {resp.status_code} from OpenRouter. The API key is missing, invalid, or "
                    f"lacks access to {cfg['model']!r}.\n"
                    f"  Check:  echo $OPENROUTER_API_KEY\n"
                    f"  Test:   curl -s -o /dev/null -w '%{{http_code}}\\n' "
                    f"https://openrouter.ai/api/v1/auth/key -H \"Authorization: Bearer "
                    f"$OPENROUTER_API_KEY\""
                )
            if resp.status_code in (400, 404):
                raise FatalAPIError(
                    f"HTTP {resp.status_code} from OpenRouter for model {cfg['model']!r}.\n"
                    f"  Response: {resp.text[:400]}\n"
                    f"  A 404 usually means the model slug is wrong or retired; a 400 usually means "
                    f"the model rejected a parameter (seed, temperature, reasoning, or "
                    f"response_format). Fix the RUNS entry rather than letting the grid run on."
                )

            if resp.status_code in (429, 500, 502, 503, 504):
                last = f"HTTP {resp.status_code}"
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            payload = resp.json()
            choice = payload["choices"][0]
            content = choice["message"]["content"]
            usage = payload.get("usage", {})

            # Surface truncation as truncation. Left alone it arrives as a JSONDecodeError about
            # an unterminated string, which reads like a model formatting failure rather than a
            # budget we set too low.
            if choice.get("finish_reason") == "length":
                raise RuntimeError(
                    f"TRUNCATED: hit max_tokens={body['max_tokens']} "
                    f"(reasoning_tokens="
                    f"{usage.get('completion_tokens_details', {}).get('reasoning_tokens')}). "
                    f"Raise max_tokens for this run; do not analyse a partially truncated run."
                )
            return {
                "probs": json.loads(content),
                "reasoning_tokens": usage.get("completion_tokens_details", {}).get(
                    "reasoning_tokens"
                ),
                "raw": content,
            }
        except FatalAPIError:
            raise
        except (requests.RequestException, KeyError, ValueError) as e:
            last = f"{type(e).__name__}: {e}"
            if isinstance(e, (KeyError, ValueError)):
                break  # model-level failure, not transport. Do not retry.
            time.sleep(2 ** attempt)
    raise RuntimeError(last or "unknown failure")


# --------------------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, choices=sorted(RUNS), help="run name from spec §7")
    ap.add_argument("--block", default=None, help="B1-CORE, B2-ALPHABET, B3-STRENGTH, or omit for all")
    ap.add_argument(
        "--stimuli", default=STIMULI,
        help="stimulus file to run (default the frozen main grid). Control arms live in their own "
             "file with their own hash, so the frozen grid is never edited to add a condition.",
    )
    ap.add_argument(
        "--seeds", type=int, default=10,
        help="draws per stimulus (default 10 per spec §6). Reducing this is a deliberate "
             "protocol reduction and must be declared in the writeup, not left implicit. It is "
             "defensible on high-effort arms, where sol-high returned an identical answer on all "
             "ten seeds in 31 of 32 cells, so the extra draws buy almost no information. It is "
             "NOT defensible on default-effort arms, where sol-none showed sd(s) up to 0.60.",
    )
    args = ap.parse_args()

    cfg = RUNS[args.run]
    is_stub = args.run == "stub"

    api_key = "" if is_stub else os.environ.get("OPENROUTER_API_KEY", "")
    if not is_stub and not api_key:
        sys.exit("OPENROUTER_API_KEY not set.  export OPENROUTER_API_KEY=sk-or-...")

    stims = load_stimuli(args.stimuli)
    if args.block:
        stims = [s for s in stims if s["block"] == args.block]
    elif args.run in BLOCK1_ONLY and args.stimuli == STIMULI:
        # The Block-1 restriction of §5 is a statement about the main grid. Applying it to a
        # control file whose blocks are named differently silently filters every stimulus out.
        stims = [s for s in stims if s["block"] == "B1-CORE"]
    if not stims:
        sys.exit(f"no stimuli match block {args.block!r}")

    OUTDIR.mkdir(exist_ok=True)
    suffix = "" if args.stimuli == STIMULI else "-" + Path(args.stimuli).stem.replace("silence_", "").replace("_stimuli", "")
    path = OUTDIR / f"{args.run}{suffix}.jsonl"

    # Resume: skip (sid, seed) pairs that already SUCCEEDED. Recorded failures are retried.
    #
    # Keying resume on "appears in the file" rather than "succeeded" silently drops every failed
    # draw from the campaign. That is not a uniform thinning either: failures cluster wherever the
    # outage happened, so specific cells end up short while the run still reports a full row count.
    # This cost 33 draws on the first anchor run.
    done, prior_failures = set(), 0
    if path.exists():
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("ok"):
                    done.add((rec["sid"], rec["seed"]))
                else:
                    prior_failures += 1
        if done or prior_failures:
            print(f"resuming: {len(done)} successful draws on disk, {prior_failures} failed draws will be retried")

    seeds = SEEDS[: args.seeds]
    if args.seeds != len(SEEDS):
        print(f"NOTE: running {args.seeds} seeds, not the {len(SEEDS)} of §6. Declare this reduction.")
    todo = [(s, seed) for s in stims for seed in seeds if (s["sid"], seed) not in done]
    print(f"run={args.run}  model={cfg['model']}  reasoning={cfg['reasoning']}")
    print(f"{len(stims)} stimuli x {len(seeds)} seeds = {len(stims)*len(seeds)} draws, {len(todo)} to go\n")

    # PREFLIGHT. One real call before committing to the grid, so a bad key or a retired slug
    # surfaces in three seconds rather than after a quarter hour of silent failure.
    if not is_stub:
        print("preflight: one call before starting the grid...")
        t0 = time.time()
        try:
            probe = call_model(todo[0][0], cfg, todo[0][1], api_key)
        except FatalAPIError as e:
            sys.exit(f"\nPREFLIGHT FAILED\n{e}")
        except Exception as e:
            sys.exit(f"\nPREFLIGHT FAILED: {type(e).__name__}: {e}")
        dt = time.time() - t0
        print(f"  ok, {dt:.1f}s per call -> estimated {dt*len(todo)/60:.0f} min for {len(todo)} draws")
        print(f"  sample response: {probe['raw'][:120]}")
        budget = cfg.get("max_tokens", 2000)
        rt = probe.get("reasoning_tokens")
        if rt is not None:
            print(f"  reasoning_tokens: {rt}  (budget {budget})")
            # Headroom check. One preflight call is a weak sample of the reasoning distribution,
            # so warn well before the ceiling rather than at it: the cells that blow the budget
            # are the hard ones, and losing only those is worse than losing a random tenth.
            if rt > 0.4 * budget:
                print(
                    f"\n  WARNING: preflight used {100*rt/budget:.0f}% of the token budget on what is\n"
                    f"  probably not the hardest cell. Raise max_tokens for this run in RUNS before\n"
                    f"  spending the grid, or expect truncation concentrated in the hard conditions."
                )
                if input("  continue anyway? [y/N] ").strip().lower() != "y":
                    sys.exit("  aborted before spending the grid.")
        print()

    failures = 0
    consecutive = 0
    with path.open("a", encoding="utf-8") as fh:
        for i, (stim, seed) in enumerate(todo, 1):
            rec = {"sid": stim["sid"], "seed": seed, "run": args.run, "model": cfg["model"]}
            try:
                if is_stub:
                    out = {"probs": stub_response(stim), "reasoning_tokens": 0, "raw": "STUB"}
                else:
                    out = call_model(stim, cfg, seed, api_key)
                lo, clipped = logodds_from_probs(out["probs"], stim["target_label"])
                rec.update(
                    ok=True,
                    probs=out["probs"],
                    logodds=lo,
                    clipped=clipped,
                    reasoning_tokens=out["reasoning_tokens"],
                )
                consecutive = 0
            except FatalAPIError as e:
                fh.write(json.dumps({**rec, "ok": False, "error": str(e)}) + "\n")
                fh.flush()
                sys.exit(f"\nABORTED at draw {i}\n{e}")
            except Exception as e:
                failures += 1
                consecutive += 1
                rec.update(ok=False, error=f"{type(e).__name__}: {e}")
                if failures == 1:
                    print(f"  first failure at draw {i}: {rec['error']}")
            fh.write(json.dumps(rec) + "\n")
            fh.flush()

            # Fail-fast. Ten in a row is a broken configuration, not bad luck, and grinding
            # through the remaining draws produces nothing but a large file of errors.
            if consecutive >= 10:
                sys.exit(
                    f"\nABORTED at draw {i}: 10 consecutive failures.\n"
                    f"  last error: {rec.get('error')}\n"
                    f"  Partial results kept in {path}; rerunning the same command resumes."
                )

            if i % 25 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)} draws   ({failures} failures)")

    print(f"\nwrote {path}   failures: {failures}")

    # Missingness audit. A uniform failure rate is survivable; one concentrated in a condition is
    # not, because it removes the hard tail of exactly the cells the result rests on.
    if failures:
        from collections import Counter
        stim_by = {s["sid"]: s for s in stims}
        f_by, t_by = Counter(), Counter()
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                c = stim_by[rec["sid"]]["condition"]
                t_by[c] += 1
                if not rec.get("ok"):
                    f_by[c] += 1
        print("\n  failure rate by condition:")
        for c in sorted(t_by):
            print(f"    {c:<20} {f_by[c]:>3}/{t_by[c]:<4} {100*f_by[c]/t_by[c]:>5.1f}%")
        if max(f_by[c] / t_by[c] for c in t_by) > 2 * (sum(f_by.values()) / sum(t_by.values())):
            print("\n  WARNING: failures are concentrated in one condition, not spread evenly.")
            print("  This is informative missingness. Do not analyse this run; fix and rerun clean.")

    if is_stub:
        return check_stub(path, {s["sid"]: s for s in stims})
    return 0


def check_stub(path: Path, by_sid: Dict[str, dict]) -> int:
    """
    §11 gate. The stubbed obedient responder must recover s = 1.000000 in every cell.

    Any deviation means the plumbing is wrong: a target/label mismatch, a denominator taken from
    the wrong delta, or a log-odds convention that disagrees between silence_model and the harness.
    Better to find that here than to attribute it to a model later.
    """
    print("\n--- STUB GATE: s must be exactly 1.000000 in every cell ---")
    # Deduplicate on (sid, seed): a retried draw appends a second row, and the successful one
    # supersedes the earlier failure. Without this a resumed run double-counts.
    seen: Dict[tuple, float] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("ok"):
                seen[(rec["sid"], rec["seed"])] = rec["logodds"]
    sums: Dict[str, List[float]] = {}
    for (sid, _seed), lo in seen.items():
        sums.setdefault(sid, []).append(lo)

    bad = []
    for sid, los in sorted(sums.items()):
        stim = by_sid[sid]
        mean_lo = sum(los) / len(los)  # §6: average the log-odds
        s = (mean_lo - stim["b_pos_logodds"]) / stim["denominator"]
        # A stub answering its own condition's truth lands at s = 1 in the three conditions whose
        # correct answer is the denominator's upper endpoint. PARTIAL-BLIND's correct answer is
        # b_pos, the LOWER endpoint, so an obedient stub lands at s = 0 there by construction.
        want = 0.0 if stim["condition"] == "PARTIAL-BLIND" else 1.0
        if abs(s - want) > 1e-9:
            bad.append(f"  {sid}: s = {s:.9f}, expected {want:.1f}")

    if bad:
        print(f"FAILED: {len(bad)} cells off. Do NOT run against a real model.\n")
        for b in bad[:20]:
            print(b)
        return 1
    print(f"PASSED: {len(sums)} cells, every one exact.")
    print("Plumbing is verified. Any gap in a real run is the model, not the harness.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
