"""
W1 addendum — extract the LOW-SIDE confidence threshold from data already collected.

No new calls. Reads results_w1/w1_results_live.json.

Why this is needed
------------------
w1_analyze.py's switch_point() only scanned P(first) >= 0.5, so it measured the
threshold between "Slightly TARGET" and "Strongly TARGET" and nothing else. The
symmetric lower threshold -- between "Slightly OTHER" and "Strongly OTHER" -- was
never extracted.

That gap matters more than the one that was filled. In the real v2 experiment the
silence-aware posterior q^t sits BELOW 0.5 on every flip cell, which is where the
entire result lives. The W4 grid rule currently excludes predicted beliefs in
[0.15, 0.35] on the low side, and that interval is a MIRROR ASSUMPTION from the
measured high-side switch, not a measurement. If models are asymmetric -- and
"Strongly OTHER" is a different speech act from "Strongly TARGET" -- the assumed
dead zone is in the wrong place, and cells will be selected that sit exactly where
the level prediction is unreliable.

The CAL sweep already contains four sub-even points (0.10, 0.20, 0.30, 0.40), so
this is a reanalysis, not a rerun.

    python w1_addendum_lowside.py
"""

import json
import os
from collections import Counter

import w1_stimuli as S

RESULTS = os.environ.get("W1_RESULTS", "results_w1/w1_results_live.json")


def mode(vals):
    if not vals:
        return None
    c = Counter(vals).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return None
    return c[0][0]


def main():
    res = json.load(open(RESULTS))
    stim = {s["id"]: s for s in json.load(open("w1_stimuli.json"))["stimuli"]}
    recs = [r for r in res["records"] if r.get("ok")]

    sweep = sorted(S.CAL_P_FIRST)
    low_pts = [p for p in sweep if p < 0.5]
    high_pts = [p for p in sweep if p > 0.5]
    second = S.LABELS[1]
    first = S.LABELS[0]

    print(f"{RESULTS}\nCAL sweep, modal (candidate, confidence) at each point\n")

    rows = {}
    for cfg in sorted({r["config"] for r in recs}):
        for w in S.WORDINGS:
            lo_w, hi_w = S.WORDINGS[w]["low"], S.WORDINGS[w]["high"]
            pts = {}
            for r in recs:
                s = stim[r["stimulus_id"]]
                if s["family"] != "CAL" or r["config"] != cfg or r["wording"] != w:
                    continue
                pts.setdefault(s["p_first"], []).append((r["candidate"], r["confidence"]))
            modes = {p: mode(v) for p, v in pts.items()}

            # low side: highest P(first) at which the answer is still (second, HIGH),
            # i.e. the model is still Strongly-OTHER. The threshold lies just above it.
            low_thr = None
            for p in sorted(low_pts):
                if modes.get(p) == (second, hi_w):
                    low_thr = p
            # high side: lowest P(first) at which the answer becomes (first, HIGH)
            high_thr = None
            for p in sorted(high_pts):
                if modes.get(p) == (first, hi_w):
                    high_thr = p
                    break

            # implied edges, expressed as distance from even
            lo_dist = None if low_thr is None else round(0.5 - low_thr, 3)
            hi_dist = None if high_thr is None else round(high_thr - 0.5, 3)
            sym = (None if (lo_dist is None or hi_dist is None)
                   else round(hi_dist - lo_dist, 3))

            rows[(cfg, w)] = dict(low_thr=low_thr, high_thr=high_thr,
                                  lo_dist=lo_dist, hi_dist=hi_dist, asym=sym,
                                  modes={p: modes.get(p) for p in sweep})

            seq = "  ".join(
                f"{p:.2f}:{'--' if modes.get(p) is None else modes[p][0][0] + ('S' if modes[p][1] == hi_w else 's')}"
                for p in sweep)
            print(f"  {cfg:<15} {w}  {seq}")

    print("\nImplied thresholds, as distance from even (0.50):")
    print(f"  {'config':<15}{'w':<3}{'low edge':>10}{'high edge':>11}{'asymmetry':>12}")
    for (cfg, w), d in sorted(rows.items()):
        print(f"  {cfg:<15}{w:<3}{str(d['lo_dist']):>10}{str(d['hi_dist']):>11}"
              f"{str(d['asym']):>12}")

    # what W4 should actually exclude
    los = [d["lo_dist"] for d in rows.values() if d["lo_dist"] is not None]
    his = [d["hi_dist"] for d in rows.values() if d["hi_dist"] is not None]
    if los and his:
        print("\nW4 dead-zone rule implied by the data (rather than by mirror assumption):")
        print(f"  high side: exclude predicted belief in "
              f"[{0.5 + min(his) - 0.05:.2f}, {0.5 + max(his) + 0.05:.2f}]")
        print(f"  low side:  exclude predicted belief in "
              f"[{0.5 - max(los) - 0.05:.2f}, {0.5 - min(los) + 0.05:.2f}]")
        print(f"  asymmetric by {abs(max(his) - max(los)):.3f} at the widest.")

    json.dump({f"{c}|{w}": v for (c, w), v in rows.items()},
              open("results_w1/w1_lowside.json", "w"), indent=2, default=str)
    print("\nwritten to results_w1/w1_lowside.json")


if __name__ == "__main__":
    main()
