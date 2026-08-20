"""
sweep_joint.py — silence cost as a function of evidence mixedness.

    python sweep_joint.py
    python sweep_joint.py --drop-dead-zone

Runs on the FULLCTRL cells only, which are the ones collected in BOTH arms. Those cells
hold the correct answer fixed at level 3 (b* ~ 0.90) and vary mixedness k(N-k) from 30
down to 0, so:

    silence cost  =  s1(PARTIAL_RULED)  -  s1(FULL)

is a difference measured on identical cells with the same correct answer. FULL prints
every assay result; RULED prints only the k positives and states the rule, so the same
negatives must be derived. FULL's length is constant at 1181 characters throughout.

The question: does deriving absences get harder when the evidence is mixed?

One confound, and it runs in our favour. RULED's prompt length varies 1094 to 1234
across these cells, and it moves OPPOSITE to mixedness -- the least mixed cell (k = 11,
mixedness 0) has the LONGEST RULED prompt. So a positive slope of silence cost against
mixedness is working against length, not produced by it. RULEDCTRL, where k is fixed and
RULED length is constant, is the clean check on RULED's own slope.
"""

import argparse
import json
import os
from collections import Counter, defaultdict

import silence_v2_stimuli as S

RESULTS = os.environ.get("SWEEP_RESULTS", "results_sweep/sweep_results_live.json")
STIM = "sweep_stimuli.json"
ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor")


def mode(v):
    c = Counter(v).most_common()
    return None if not v or (len(c) > 1 and c[0][1] == c[1][1]) else c[0][0]


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return None if sxx == 0 or syy == 0 else sxy / (sxx * syy) ** 0.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-dead-zone", action="store_true")
    a = ap.parse_args()

    res = json.load(open(RESULTS))
    stim = {s["id"]: s for s in json.load(open(STIM))["stimuli"]}

    errs = defaultdict(list)
    for r in res["records"]:
        if not r.get("ok"):
            continue
        s = stim[r["stimulus_id"]]
        if s["sweep"] != "FULLCTRL":
            continue
        lv = S.target_level(r["candidate"], r["confidence"], s["target_label"])
        errs[(r["config"], s["cell"], s["condition"])].append(lv - s["level_correct"])

    meta = {s["cell"]: s for s in stim.values() if s["sweep"] == "FULLCTRL"}
    cells = sorted(meta, key=lambda c: -meta[c]["mixedness"])
    if a.drop_dead_zone:
        cells = [c for c in cells if meta[c]["in_band"]]
    configs = [c for c in ORDER if any(k[0] == c for k in errs)]

    print(f"{res['n_ok']}/{res['n_records']} usable draws")
    print("FULLCTRL cells: correct answer fixed at level 3 (b* ~ 0.90); "
          "FULL length fixed at 1181 chars")
    print(f"\n  {'cell':<6}{'k':>3}{'mix':>5}{'RULEDch':>9}   "
          + "".join(f"{c[:9]:>11}" for c in configs))

    def s1(cfg, cid, arm):
        v = errs.get((cfg, cid, arm), [])
        return None if not v else sum(abs(x) for x in v) / len(v)

    rows = {}
    for cid in cells:
        m = meta[cid]
        rl = len([s for s in stim.values()
                  if s["cell"] == cid and s["condition"] == "PARTIAL_RULED"
                  and s["target_is_first"]][0]["prompt"])
        line = f"  {cid:<6}{m['k']:>3}{m['mixedness']:>5}{rl:>9}   "
        for cfg in configs:
            f, r = s1(cfg, cid, "FULL"), s1(cfg, cid, "PARTIAL_RULED")
            line += f"{'--':>11}" if None in (f, r) else f"{r - f:>+11.2f}"
            rows.setdefault(cfg, {})[cid] = (
                None if None in (f, r) else r - f)
        print(line)
    print("  values are SILENCE COST = s1(RULED) - s1(FULL), in bins. "
          "Positive = deriving costs more.")

    print(f"\n  {'config':<15}{'mean cost':>11}{'r(cost, mix)':>14}"
          f"{'r(cost, RULEDlen)':>19}{'n':>5}")
    out = {}
    for cfg in configs:
        pts = [(meta[c]["mixedness"],
                len([s for s in stim.values() if s["cell"] == c
                     and s["condition"] == "PARTIAL_RULED"
                     and s["target_is_first"]][0]["prompt"]),
                rows[cfg][c]) for c in cells if rows[cfg].get(c) is not None]
        if not pts:
            continue
        mean = sum(p[2] for p in pts) / len(pts)
        rm = pearson([p[0] for p in pts], [p[2] for p in pts])
        rl = pearson([p[1] for p in pts], [p[2] for p in pts])
        f = lambda x: "  --" if x is None else f"{x:+.3f}"
        print(f"  {cfg:<15}{mean:>+11.3f}{f(rm):>14}{f(rl):>19}{len(pts):>5}")
        out[cfg] = {"mean_cost": mean, "r_mixedness": rm, "r_ruled_length": rl,
                    "n": len(pts), "per_cell": rows[cfg]}

    print("\n  Read r(cost, mix) against r(cost, RULEDlen): RULED length runs OPPOSITE")
    print("  to mixedness here, so if both correlations are positive, length is not")
    print("  driving the mixedness result. RULEDCTRL is the clean check.")

    os.makedirs("results_sweep", exist_ok=True)
    json.dump(out, open("results_sweep/sweep_joint.json", "w"), indent=2)
    print("\nwritten to results_sweep/sweep_joint.json")


if __name__ == "__main__":
    main()
