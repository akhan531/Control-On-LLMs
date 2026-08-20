"""
s3_ladder_summary.py — ARITH_D0 ladder analysis, statistics per arith_d0_prereg.md.

Three rungs at delta = 0, identical cells, identical correct answer b*:
  RULED  (PARTIAL_RULED, frozen main campaign)   identify + substitute + aggregate
  ARITH  (ARITH_D0, new)                         substitute + aggregate
  FULL   (frozen main campaign)                  aggregate only

Ruler per cell: l_cor = level(b*), l_pos = level(b_pos). Classes as Example 1:
OVER < l_cor | COR | INT | POS = l_pos | BEY > l_pos.

Registered outputs:
  1. per config x rung: n, fails, s1, s2, class occupancy
  2. paired per-cell d_s1/d_s2: ARITH-RULED and ARITH-FULL
  3. localization lambda = (s1_A - s1_F)/(s1_R - s1_F), ceiling guard 0.15
  4. D-cell OVER probe per rung
  5. C/D count-control modal concordance within ARITH_D0
  6. modal paired RULED -> ARITH
  7. side-by-side with the delta=0.3 pair (RULED_D30 vs ARITH_D30): paired d_s1/d_s2
Gate: frozen FULL gate (gated five; deepseek/anchor context). P4 inherited.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
ORDER = GATED + ("deepseek", "anchor")
RUNGS = ("RULED", "ARITH", "FULL")
CELLS = ("A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3",
         "B1", "B2", "B3", "D1", "D2", "D3")


def klass(lv, lc, lp):
    if lv < lc:
        return "OVER"
    if lv == lc:
        return "COR"
    if lv < lp:
        return "INT"
    if lv == lp:
        return "POS"
    return "BEY"


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def ingest(res_path, stim_path, cond_map, draws, fails, p4):
    res = json.load(open(f"{ROOT}/{res_path}"))
    stim = {s["id"]: s for s in json.load(open(f"{ROOT}/{stim_path}"))["stimuli"]}
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        rung = cond_map.get(st["condition"])
        if rung is None:
            continue
        if st["cell"] in p4.get(r["config"], []):
            continue
        if not r.get("ok"):
            fails[(r["config"], rung)] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], rung, st["cell"])].append(
            (lv, st["level_target"], st["l_pos_target"]))


def cellmean(draws, cfg, rung, cid, signed=False):
    v = draws.get((cfg, rung, cid), [])
    if not v:
        return None
    if signed:
        return sum(lv - lc for lv, lc, lp in v) / len(v)
    return sum(abs(lv - lc) for lv, lc, lp in v) / len(v)


def main():
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]
    draws, fails = defaultdict(list), Counter()
    ingest("results_v2/v2_results_live.json", "silence_v2_stimuli.json",
           {"PARTIAL_RULED": "RULED", "FULL": "FULL"}, draws, fails, p4)
    ingest("scratch_2_4c/example_2/results_arith_d0/arith_d0_results_live.json",
           "scratch_2_4c/example_2/arith_d0_stimuli.json",
           {"ARITH_D0": "ARITH"}, draws, fails, p4)

    # ---- 1. per config x rung ----
    print("LADDER, draw level, 14 cells minus P4  "
          "(classes: OVER past b* | COR | INT | POS at b_pos | BEY)")
    print(f"  {'config':<15}{'rung':<7}{'n':>4}{'fl':>3}{'s1':>7}{'s2':>8}"
          f"{'%OVER':>7}{'%COR':>6}{'%INT':>6}{'%POS':>6}{'%BEY':>6}")
    for cfg in ORDER:
        for rung in ("RULED", "ARITH", "FULL"):
            v = [x for cid in CELLS for x in draws.get((cfg, rung, cid), [])]
            if not v:
                continue
            n = len(v)
            s1 = sum(abs(lv - lc) for lv, lc, lp in v) / n
            s2 = sum(lv - lc for lv, lc, lp in v) / n
            cl = Counter(klass(lv, lc, lp) for lv, lc, lp in v)
            pc = lambda k: 100 * cl.get(k, 0) / n
            tag = "" if cfg in GATED else "  [excl]"
            print(f"  {cfg:<15}{rung:<7}{n:>4}{fails.get((cfg,rung),0):>3}"
                  f"{s1:>7.3f}{s2:>+8.3f}{pc('OVER'):>7.1f}{pc('COR'):>6.1f}"
                  f"{pc('INT'):>6.1f}{pc('POS'):>6.1f}{pc('BEY'):>6.1f}{tag}")
        print()

    # ---- 2 + 3. paired deltas and lambda ----
    print("PAIRED PER CELL (draw-mean per cell) and LOCALIZATION lambda")
    print(f"  {'config':<15}{'d_s1 A-R':>9}{'d_s2 A-R':>9}{'d_s1 A-F':>9}"
          f"{'d_s2 A-F':>9}{'s1 R':>7}{'s1 A':>7}{'s1 F':>7}{'lambda':>8}")
    for cfg in ORDER:
        dar1, dar2, daf1, daf2 = [], [], [], []
        sR, sA, sF = [], [], []
        for cid in CELLS:
            r1 = cellmean(draws, cfg, "RULED", cid)
            a1 = cellmean(draws, cfg, "ARITH", cid)
            f1 = cellmean(draws, cfg, "FULL", cid)
            r2 = cellmean(draws, cfg, "RULED", cid, signed=True)
            a2 = cellmean(draws, cfg, "ARITH", cid, signed=True)
            f2 = cellmean(draws, cfg, "FULL", cid, signed=True)
            if None not in (r1, a1):
                dar1.append(a1 - r1)
                dar2.append(a2 - r2)
            if None not in (f1, a1):
                daf1.append(a1 - f1)
                daf2.append(a2 - f2)
            if None not in (r1, a1, f1):
                sR.append(r1)
                sA.append(a1)
                sF.append(f1)
        mR, mA, mF = (sum(x)/len(x) for x in (sR, sA, sF))
        lam = ("ceiling" if mR - mF < 0.15
               else f"{(mA - mF)/(mR - mF):.2f}")
        tag = "" if cfg in GATED else "  [excl]"
        print(f"  {cfg:<15}{sum(dar1)/len(dar1):>+9.3f}{sum(dar2)/len(dar2):>+9.3f}"
              f"{sum(daf1)/len(daf1):>+9.3f}{sum(daf2)/len(daf2):>+9.3f}"
              f"{mR:>7.3f}{mA:>7.3f}{mF:>7.3f}{lam:>8}{tag}")

    # ---- 4. D-cell OVER probe ----
    print("\nD-CELL OVER PROBE (l_cor=1: answering level 0 = overshoot; "
          "the only cells where OVER is expressible)")
    print(f"  {'config':<15}" + "".join(f"{r:>14}" for r in RUNGS))
    for cfg in ORDER:
        row = f"  {cfg:<15}"
        for rung in RUNGS:
            over = n = 0
            for cid in ("D1", "D2", "D3"):
                for lv, lc, lp in draws.get((cfg, rung, cid), []):
                    n += 1
                    over += (lv < lc)
            row += f"{over}/{n}".rjust(14)
        print(row)

    # ---- 5. C/D concordance within ARITH ----
    print("\nARITH_D0 COUNT-CONTROL CONCORDANCE (modal constant across k?)")
    for cfg in ORDER:
        parts = []
        for grp in (("C1", "C2", "C3"), ("D1", "D2", "D3")):
            ms = [mode([lv for lv, _, _ in draws.get((cfg, "ARITH", c), [])])
                  for c in grp if draws.get((cfg, "ARITH", c))]
            parts.append(f"{grp[0][0]}: " + "/".join(
                "t" if m is None else str(m) for m in ms))
        print(f"  {cfg:<15}" + "   ".join(parts))

    # ---- 6. modal paired ----
    print("\nMODAL PER CELL, RULED -> ARITH ('.'=tie)")
    print(f"  {'config':<15}" + "".join(f"{cid:>8}" for cid in CELLS))
    for cfg in ORDER:
        row = f"  {cfg:<15}"
        for cid in CELLS:
            mr = mode([lv for lv, _, _ in draws.get((cfg, "RULED", cid), [])])
            ma = mode([lv for lv, _, _ in draws.get((cfg, "ARITH", cid), [])])
            row += f"{('.' if mr is None else mr)}->{('.' if ma is None else ma)}".rjust(8)
        print(row)

    # ---- 7. side-by-side with delta=0.3 ----
    print("\nSIDE-BY-SIDE: paired ARITH-RULED deltas, delta=0 vs delta=0.3")
    d30draws, d30fails = defaultdict(list), Counter()
    ingest("results_v2/v2_results_live_banked.json", "silence_v2_stimuli_banked.json",
           {"PARTIAL_RULED_D30": "R30"}, d30draws, d30fails, p4)
    ingest("scratch_fable/results_arith/arith_results_live.json",
           "scratch_fable/arith_d30_stimuli.json",
           {"ARITH_D30": "A30"}, d30draws, d30fails, p4)
    cells30 = sorted({cid for (_, _, cid) in d30draws})
    print(f"  {'config':<15}{'d0: d_s1':>10}{'d0: d_s2':>10}"
          f"{'d30: d_s1':>11}{'d30: d_s2':>11}")
    for cfg in ORDER:
        d0_1, d0_2, d3_1, d3_2 = [], [], [], []
        for cid in CELLS:
            r1 = cellmean(draws, cfg, "RULED", cid)
            a1 = cellmean(draws, cfg, "ARITH", cid)
            if None not in (r1, a1):
                d0_1.append(a1 - r1)
                d0_2.append(cellmean(draws, cfg, "ARITH", cid, True)
                            - cellmean(draws, cfg, "RULED", cid, True))
        for cid in cells30:
            r1 = cellmean(d30draws, cfg, "R30", cid)
            a1 = cellmean(d30draws, cfg, "A30", cid)
            if None not in (r1, a1):
                d3_1.append(a1 - r1)
                d3_2.append(cellmean(d30draws, cfg, "A30", cid, True)
                            - cellmean(d30draws, cfg, "R30", cid, True))
        f = lambda v: f"{sum(v)/len(v):+.3f}" if v else "--"
        tag = "" if cfg in GATED else "  [excl]"
        print(f"  {cfg:<15}{f(d0_1):>10}{f(d0_2):>10}{f(d3_1):>11}{f(d3_2):>11}{tag}")


if __name__ == "__main__":
    main()
