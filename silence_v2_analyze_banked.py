"""
silence_v2_analyze_banked.py — reads the delta = 0.30 arm against the delta = 0 arm.

    python silence_v2_analyze_banked.py

This is NOT the pre-registered analysis. The delta arm was cut from the campaign (D26)
and is being run afterwards as exploratory work toward a credal-set framing. Everything
here is labelled exploratory and must be reported as such.

What it measures
----------------
The nine banked cells were selected so that stating a dropout rate MOVES the correct
answer: q goes from level 0 to level 2 in eight of them, and 0 to 1 in B1. Since the
record, the rule, N and k are all identical between the two arms, the only thing that
changes is one sentence giving the filing rate.

That makes the comparison a direct test of whether a stated nuisance parameter enters
the belief at all:

  MOVED     the answer changes with delta -> the model conditions on the rate
  STUCK     the answer is identical at both deltas -> the model collapses what should
            be a delta-indexed family of beliefs to a single point, and reports that
            point with the same confidence regardless

STUCK is the interesting outcome for the credal-set reading. If the correct object under
unknown delta is the SET {q(delta)}, then a system that cannot move under a KNOWN delta
certainly cannot represent the set. This arm therefore establishes the precondition for
the unknown-delta experiment before that experiment is built.

  anchor_point   for a stuck model, which belief it silently settled on: the
                 positives-only b_pos, the delta=0 posterior q(0), or neither.
"""

import json
import os
from collections import Counter, defaultdict

import silence_v2_model as M
import silence_v2_stimuli as S

PRIMARY = os.environ.get("V2_RESULTS", "results_v2/v2_results_live.json")
BANKED = os.environ.get("V2_BANKED", "results_v2/v2_results_live_banked.json")
STIM_P = "silence_v2_stimuli.json"
STIM_B = "silence_v2_stimuli_banked.json"

ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor")
LEVEL_NAME = {0: "VC/other", 1: "SC/other", 2: "SC/target", 3: "VC/target", None: "--"}


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def levels(results_path, stim_path):
    res = json.load(open(results_path))
    stim = {s["id"]: s for s in json.load(open(stim_path))["stimuli"]}
    b = defaultdict(list)
    for r in res["records"]:
        if not r.get("ok"):
            continue
        s = stim[r["stimulus_id"]]
        b[(r["config"], s["cell"], s["condition"])].append(
            S.target_level(r["candidate"], r["confidence"], s["target_label"]))
    return {k: mode(v) for k, v in b.items()}, {k: len(v) for k, v in b.items()}, res


def main():
    lp, np_, resp = levels(PRIMARY, STIM_P)
    lb, nb, resb = levels(BANKED, STIM_B)

    cells = [c for c in M.build() if M.banked_viable(c)]
    ids = [c["id"] for c in cells]
    pred = {c["id"]: (M.level(c["b_pos"]),
                      M.level(c[f"q_{M.DELTA_PRIMARY}"]),
                      M.level(c[f"q_{M.DELTA_BANKED}"])) for c in cells}
    configs = [c for c in ORDER if any(k[0] == c for k in lb)]

    print(f"delta=0.30 arm: {resb['n_ok']}/{resb['n_records']} usable draws")
    print("EXPLORATORY. Not pre-registered; delta was cut at freeze (D26).\n")

    print("predicted levels per cell   b_pos -> q(0) -> q(0.3)")
    for i in ids:
        a, b, c = pred[i]
        print(f"  {i:<4} {LEVEL_NAME[a]:>10} -> {LEVEL_NAME[b]:>10} -> {LEVEL_NAME[c]:>10}")

    print("\nobserved answer at delta=0 / delta=0.30, per configuration")
    print(f"  {'cell':<5}" + "".join(f"{c[:11]:>22}" for c in configs))
    summary = {}
    for i in ids:
        row = f"  {i:<5}"
        for cfg in configs:
            a = lp.get((cfg, i, "PARTIAL_RULED"))
            b = lb.get((cfg, i, S.BANKED))
            row += f"{LEVEL_NAME[a] + ' -> ' + LEVEL_NAME[b]:>22}"
        print(row)

    print("\nmovement summary")
    print(f"  {'config':<15}{'moved':>7}{'stuck':>7}{'correct':>9}"
          f"{'  anchor point when stuck'}")
    for cfg in configs:
        moved = stuck = correct = 0
        anch = Counter()
        for i in ids:
            a = lp.get((cfg, i, "PARTIAL_RULED"))
            b = lb.get((cfg, i, S.BANKED))
            if a is None or b is None:
                continue
            lpos, l0, l3 = pred[i]
            if a == b:
                stuck += 1
                anch["b_pos" if b == lpos else
                     "q(0)" if b == l0 else
                     "q(.3)" if b == l3 else "other"] += 1
            else:
                moved += 1
            if b == l3:
                correct += 1
        tag = "  [reported only]" if cfg == "anchor" else ""
        print(f"  {cfg:<15}{moved:>7}{stuck:>7}{correct:>9}"
              f"  {dict(anch) if anch else ''}{tag}")

        summary[cfg] = {"moved": moved, "stuck": stuck, "correct_at_d30": correct,
                        "anchor_when_stuck": dict(anch)}

    print("\nordinal-s in the delta=0.30 arm (endpoints b_pos -> q(0.3))")
    print(f"  {'config':<15}{'mean s':>9}{'n cells':>9}")
    for cfg in configs:
        v = []
        for i in ids:
            b = lb.get((cfg, i, S.BANKED))
            if b is None:
                continue
            lpos, _, l3 = pred[i]
            v.append((b - lpos) / (l3 - lpos))
        summary[cfg]["mean_s_d30"] = sum(v) / len(v) if v else None
        print(f"  {cfg:<15}{(sum(v)/len(v) if v else float('nan')):>9.3f}{len(v):>9}")

    print("\nside by side: mean s at delta=0 vs delta=0.30 (same nine cells)")
    print(f"  {'config':<15}{'s(d=0)':>9}{'s(d=.3)':>10}{'change':>9}")
    for cfg in configs:
        v0 = []
        for i in ids:
            a = lp.get((cfg, i, "PARTIAL_RULED"))
            if a is None:
                continue
            lpos, l0, _ = pred[i]
            v0.append((a - lpos) / (l0 - lpos))
        m0 = sum(v0) / len(v0) if v0 else None
        m3 = summary[cfg]["mean_s_d30"]
        d = None if None in (m0, m3) else m3 - m0
        summary[cfg]["mean_s_d0"] = m0
        print(f"  {cfg:<15}{m0:>9.3f}{m3:>10.3f}"
              f"{(d if d is not None else float('nan')):>9.3f}")

    json.dump({"cells": ids, "predicted": {k: list(v) for k, v in pred.items()},
               "summary": summary},
              open("results_v2/v2_banked_gates.json", "w"), indent=2)
    print("\nwritten to results_v2/v2_banked_gates.json")


if __name__ == "__main__":
    main()
