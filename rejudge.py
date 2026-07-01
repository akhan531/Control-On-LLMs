#!/usr/bin/env python3
"""Offline re-judge: recover judge_ok=False seeds from saved transcripts.
Non-destructive: writes <dir>/task_1_0_results_rejudged.json.
Run with the SAME model/endpoint env as the original judge (70B OpenRouter).
Usage: python rejudge.py <dir1> <dir2> ..."""
import json, sys
from pathlib import Path
import task_1_0 as T   # imports the hardened judge_credit, summarize, config

def rejudge_dir(d: Path):
    src = d / "task_1_0_results.json"
    if not src.exists():
        print(f"  [skip] {src} not found"); return
    with open(src) as f:
        res = json.load(f)
    runs = res["runs"]
    recovered = {}
    for arm, arm_runs in runs.items():
        rec = 0
        for run in arm_runs:
            if run.get("credit_judge_ok", True):
                continue
            credit, ok = T.judge_credit(run["rounds"], run["final_answer"], run["seed"])
            if ok:
                run["credit"] = credit
                run["credit_judge_ok"] = True
                rec += 1
        recovered[arm] = rec
    res["summary"] = {arm: T.summarize(runs[arm]) for arm in runs if runs.get(arm)}
    out = d / "task_1_0_results_rejudged.json"
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    for arm in runs:
        if not runs.get(arm): continue
        s = res["summary"][arm]
        print(f"  {d.name}/{arm}: recovered {recovered.get(arm,0)} | "
              f"n_judge_failed now {s['n_judge_failed']} | "
              f"expert_credit_mean {s['expert_credit_mean']}")
    print(f"  -> wrote {out}")

if __name__ == "__main__":
    dirs = sys.argv[1:]
    if not dirs:
        print("usage: python rejudge.py <dir1> <dir2> ..."); sys.exit(1)
    for d in dirs:
        print(f"[rejudge] {d}")
        rejudge_dir(Path(d))
