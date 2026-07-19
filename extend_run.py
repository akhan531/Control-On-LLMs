#!/usr/bin/env python3
"""
Rebuild a task_1_14c checkpoint from a finished results JSON, so an extended run
resumes instead of re-running seeds it already has.

WHY THIS EXISTS
    The 2026-07-17 simultaneous run (n=16) is the PILOT that estimated the
    timing effect at dz ~ 0.47. Extending to n=40 needs seeds 16-39 only; seeds
    0-15 already exist and cost ~650 calls to reproduce for no reason.

WHY IT COPIES INSTEAD OF EXTENDING IN PLACE
    The pilot has to stay on disk, unmodified and separately citable, because
    the plan is to report the confirmation sample (seeds 16-39) on its own as
    well as pooled. If the extended run overwrote the pilot's results JSON, the
    n=16 numbers would exist only in a chat log, and "we chose n=40 after a
    pilot" becomes an unverifiable claim. So: copy, then extend the copy.

WHY IT GUARDS
    The harness keys the checkpoint on (arm, seed) and nothing else. It cannot
    tell that seed 3 came from a different DEBATE_MODE, a different model, or a
    different scenario. Point this at the wrong directory and you would splice
    sequential seeds 0-15 onto simultaneous seeds 16-39, pool them, and see
    nothing wrong in any output. Every field that could silently invalidate a
    pool is checked here.

USAGE
    python extend_run.py SRC_RESULTS_DIR DST_RESULTS_DIR [--seeds 40]

    then run the harness against DST with the SAME env as the pilot:

        OPENAI_BASE_URL=https://openrouter.ai/api/v1 \
        OPENAI_API_KEY=$OPENROUTER_API_KEY \
        MODEL_NAME=meta-llama/llama-3.3-70b-instruct \
        PROVIDER_TAG=openrouter \
        RESULTS_DIR=DST_RESULTS_DIR \
        N_SEEDS=40 \
        ARMS_TO_RUN=honest,withhold \
        python task_1_14c.py
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

RESULTS = "task_1_14c_results.json"
CHECKPOINT = "task_1_14c_checkpoint.json"

# Anything here differing between the pilot and the extension means the two
# samples are not the same experiment and must not share a checkpoint.
MUST_MATCH = [
    "debate_mode",
    "model",
    "provider",
    "temperature",
    "scenario_id",
    "n_agents",
    "n_rounds",
    "answer_set",
    "correct_answer",
    "misleading_answer",
    "clue_text",
    "arms_tau_by_clue",
    "group_belief_instrument",
    "epsilon_floor",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--seeds", type=int, default=40,
                    help="target N_SEEDS for the extended run (default 40)")
    ap.add_argument("--expect-mode", default="simultaneous")
    a = ap.parse_args()

    src, dst = Path(a.src), Path(a.dst)
    src_json = src / RESULTS
    if not src_json.exists():
        print(f"ERROR: no {RESULTS} in {src}")
        return 1

    d = json.loads(src_json.read_text())
    meta, runs = d["meta"], d["runs"]

    mode = meta.get("debate_mode")
    if mode != a.expect_mode:
        print(f"ERROR: source debate_mode is {mode!r}, expected {a.expect_mode!r}.")
        print("       Refusing: seeds from different modes must never be pooled.")
        return 1
    if meta.get("smoke"):
        print("ERROR: source is a SMOKE run (1 seed). Not a pilot.")
        return 1

    print(f"source : {src_json}")
    print(f"  mode={mode}  model={meta['model']}  temp={meta['temperature']}"
          f"  scenario={meta['scenario_id']}")
    for arm in ("honest", "withhold", "never"):
        got = sorted(r["seed"] for r in runs.get(arm, []))
        print(f"  {arm:<9} n={len(got):<3} seeds {got[0] if got else '-'}"
              f"..{got[-1] if got else '-'}")
        if len(set(got)) != len(got):
            print(f"ERROR: duplicate seeds in {arm}: {got}")
            return 1

    # Guard fingerprint travels with the checkpoint so a later extension of the
    # extension can check itself too.
    fingerprint = {k: meta.get(k) for k in MUST_MATCH}

    if dst.exists():
        dst_json = dst / RESULTS
        if dst_json.exists():
            dmeta = json.loads(dst_json.read_text())["meta"]
            bad = [k for k in MUST_MATCH if dmeta.get(k) != fingerprint[k]]
            if bad:
                print(f"ERROR: {dst} exists and differs from source on: {bad}")
                return 1
        print(f"\nWARNING: {dst} already exists, reusing it.")
    else:
        shutil.copytree(src, dst)
        print(f"\ncopied {src} -> {dst}   (pilot left untouched)")

    (dst / CHECKPOINT).write_text(json.dumps(runs))
    (dst / "PROVENANCE.json").write_text(json.dumps({
        "extended_from": str(src),
        "pilot_n_seeds": meta["n_seeds"],
        "pilot_timestamp": meta["timestamp"],
        "target_n_seeds": a.seeds,
        "confirmation_seeds": list(range(meta["n_seeds"], a.seeds)),
        "note": (
            "Seeds 0..{p} are the PILOT and estimated dz ~ 0.47 for the timing "
            "effect. Seeds {p}..{t} are the pre-specified CONFIRMATION sample: "
            "paired on the matched assignment, sign-flip permutation, "
            "two-sided, direction predicted positive. Report the confirmation "
            "on its own as well as pooled; if reporting pooled, state that n "
            "was chosen from a pilot."
        ).format(p=meta["n_seeds"], t=a.seeds),
        "fingerprint": fingerprint,
    }, indent=2))

    n = meta["n_seeds"]
    todo = {arm: [s for s in range(a.seeds)
                  if s not in {r["seed"] for r in runs.get(arm, [])}]
            for arm in ("honest", "withhold")}
    calls = sum(len(v) for v in todo.values()) * (4 * meta["n_rounds"] + meta["n_rounds"] + 2)

    print(f"wrote  {dst/CHECKPOINT}   ({sum(len(v) for v in runs.values())} runs preloaded)")
    print(f"wrote  {dst/'PROVENANCE.json'}")
    print(f"\nOn the next run the harness will SKIP seeds 0..{n-1} and execute:")
    for arm, v in todo.items():
        print(f"  {arm:<9} {len(v)} seeds: {v[0]}..{v[-1]}" if v else f"  {arm:<9} nothing")
    print(f"\n  ~{calls} LLM calls  (re-running 0..{n-1} would have cost ~"
          f"{2*n*(4*meta['n_rounds']+meta['n_rounds']+2)} more)")
    print("\n  NOTE: 'never' is not in ARMS_TO_RUN, so it stays at n="
          f"{len(runs.get('never', []))} and will carry no summary block in the")
    print("        extended JSON. Its raw runs are preserved. Use the pilot file for never.")
    return 0


if __name__ == "__main__":
    sys.exit(main())