"""
s6_draw_census.py: item 41, per-arm draw census against what the paper claims.

Counts every live results file that carries a reported number, arm by arm, and
reconciles the totals. Read-only: opens nothing for writing, makes no calls.

For each arm it reports the record count, the usable count, the failure count and
its distribution over configurations, the number of distinct stimuli and
configurations, and the implied draws per stimulus per configuration. A mismatch
between the implied product and the record count means the arm is ragged, which
is a finding rather than an error.

Run from the repository root.
"""

import json
import os
from collections import Counter, defaultdict

ARMS = (
    ("main campaign (FULL/BLIND/RULED, delta=0)",
     "results_v2/v2_results_live.json"),
    ("RULED_D30 banked (delta=0.3)",
     "results_v2/v2_results_live_banked.json"),
    ("ARITH_D30",
     "scratch_fable/results_arith/arith_results_live.json"),
    ("ARITH_D0",
     "scratch_2_4c/example_2/results_arith_d0/arith_d0_results_live.json"),
    ("RULEDCTRL sweep",
     "results_sweep/sweep_results_live.json"),
    ("W1 pre-test",
     "results_w1/w1_results_live.json"),
)


def census(path):
    with open(path) as f:
        res = json.load(f)
    recs = res.get("records", [])
    ok = [r for r in recs if r.get("ok")]
    fails = Counter(r["config"] for r in recs if not r.get("ok"))
    reasons = Counter(str(r.get("error") or r.get("fail_reason") or "unlabelled")[:24]
                      for r in recs if not r.get("ok"))
    cfgs = sorted({r["config"] for r in recs})
    stims = {r.get("stimulus_id") for r in recs}
    per = defaultdict(int)
    for r in recs:
        per[(r["config"], r.get("stimulus_id"))] += 1
    draws = Counter(per.values())
    return {
        "n_records": len(recs),
        "n_ok": len(ok),
        "declared_ok": res.get("n_ok"),
        "declared_records": res.get("n_records"),
        "fails": fails,
        "reasons": reasons,
        "n_cfg": len(cfgs),
        "cfgs": cfgs,
        "n_stim": len(stims),
        "draws": draws,
    }


def main():
    grand_rec = grand_ok = 0
    print(f"{'arm':<44}{'records':>9}{'usable':>8}{'fail':>6}"
          f"{'cfgs':>6}{'stim':>6}{'draws/cell':>12}")
    print("-" * 91)
    detail = {}
    for label, path in ARMS:
        if not os.path.exists(path):
            print(f"{label:<44}{'MISSING':>9}   {path}")
            continue
        c = census(path)
        detail[label] = c
        d = ",".join(f"{k}x{v}" for k, v in sorted(c["draws"].items()))
        print(f"{label:<44}{c['n_records']:>9}{c['n_ok']:>8}"
              f"{sum(c['fails'].values()):>6}{c['n_cfg']:>6}{c['n_stim']:>6}{d:>12}")
        grand_rec += c["n_records"]
        grand_ok += c["n_ok"]
    print("-" * 91)
    print(f"{'TOTAL':<44}{grand_rec:>9}{grand_ok:>8}")

    print("\nper-arm detail")
    for label, c in detail.items():
        print(f"\n  {label}")
        exp = c["n_cfg"] * c["n_stim"] * max(c["draws"], key=c["draws"].get)
        flag = "" if exp == c["n_records"] else "  <-- RAGGED, product does not match"
        print(f"    {c['n_cfg']} configs x {c['n_stim']} stimuli x "
              f"{max(c['draws'], key=c['draws'].get)} draws = {exp}{flag}")
        if c["declared_records"] not in (None, c["n_records"]) or \
           c["declared_ok"] not in (None, c["n_ok"]):
            print(f"    HEADER DISAGREES: file declares "
                  f"{c['declared_ok']}/{c['declared_records']}, "
                  f"records give {c['n_ok']}/{c['n_records']}")
        if c["fails"]:
            print(f"    failures by config: {dict(c['fails'])}")
            print(f"    failure labels: {dict(c['reasons'])}")
        else:
            print("    zero failures")
        print(f"    configs: {c['cfgs']}")


if __name__ == "__main__":
    main()
