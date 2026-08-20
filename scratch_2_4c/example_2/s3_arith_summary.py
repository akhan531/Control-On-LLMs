"""
s3_arith_summary.py — Step 3 for candidate 2B: RULED_D30 vs ARITH_D30 (2026-08-17).

Identical records, delta = 0.3, correct answer q(0.3) in BOTH arms:
  RULED_D30  absences implicit (rule + dropout clause stated, nothing enumerated)
  ARITH_D30  every non-filing printed as a line -> identification removed,
             interpretation left. R1 deliberately violated here, recorded.

Three-point ruler per cell (all closed-form, banked_viable-asserted distinct):
  l_pos = level(b_pos)    ignores absences
  l_cor = level(q(0.3))   prices absences under the stated leaky channel  (correct)
  l_q0  = level(q(0))     prices absences as if the channel were perfect  (over-read)

Classes per draw: BEY > l_pos | POS = l_pos | INTH in (l_cor, l_pos) | COR = l_cor |
                  LOW in (l_q0, l_cor) | ATQ0 = l_q0 | SUB < l_q0
Statistics: draw-level s1/s2 per arm; class occupancy per arm; PAIRED per-cell
s1/s2 differences (ARITH - RULED_D30) so spans cancel within each pair; modal pairs.
Frozen ARITH gate admits all seven (deepseek 0.988 marginal - flagged).
P4 exclusions inherited where banked cells overlap. Existing data only; stdout only.
"""

import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
ORDER = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high", "deepseek", "anchor")
ARMS = (("RULED_D30", "results_v2/v2_results_live_banked.json",
         "silence_v2_stimuli_banked.json"),
        ("ARITH_D30", "scratch_fable/results_arith/arith_results_live.json",
         "scratch_fable/arith_d30_stimuli.json"))
DB = M.DELTA_BANKED


def klass(lv, lp, lc, l0):
    if lv > lp:
        return "BEY"
    if lv == lp:
        return "POS"
    if lv > lc:
        return "INTH"
    if lv == lc:
        return "COR"
    if lv == l0:
        return "ATQ0"
    if lv > l0:
        return "LOW"
    return "SUB"


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def main():
    cells = {c["id"]: c for c in M.build()}
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]

    draws, fails, cellsets = {}, {}, {}
    for arm, rpath, spath in ARMS:
        res = json.load(open(f"{ROOT}/{rpath}"))
        stim = {s["id"]: s for s in json.load(open(f"{ROOT}/{spath}"))["stimuli"]}
        d, fl = defaultdict(list), Counter()
        p4drop = 0
        for r in res["records"]:
            st = stim[r["stimulus_id"]]
            if st["cell"] in p4.get(r["config"], []):
                p4drop += 1
                continue
            if not r.get("ok"):
                fl[r["config"]] += 1
                continue
            lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
            d[(r["config"], st["cell"])].append(lv)
        draws[arm], fails[arm] = d, fl
        cellsets[arm] = sorted({s["cell"] for s in stim.values()})
        print(f"{arm}: cells {cellsets[arm]}  P4-dropped draws {p4drop}  "
              f"failures {dict(fl) or 0}")
    assert cellsets["RULED_D30"] == cellsets["ARITH_D30"], "cell sets differ"
    cids = cellsets["RULED_D30"]

    print("\nTHREE-POINT RULER (target frame; correct answer identical in both arms)")
    print(f"  {'cell':<5}{'p':>6}{'N':>4}{'k':>3}{'b_pos':>8}{'Lpos':>5}"
          f"{'q(.3)':>8}{'Lcor':>5}{'q(0)':>8}{'Lq0':>5}")
    geom = {}
    for cid in cids:
        c = cells[cid]
        bp, q3, q0 = c["b_pos"], c[f"q_{DB}"], c[f"q_{F(0)}"]
        lp, lc, l0 = M.level(bp), M.level(q3), M.level(q0)
        geom[cid] = (lp, lc, l0)
        print(f"  {cid:<5}{float(c['p']):>6.2f}{c['N']:>4}{c['k']:>3}"
              f"{float(bp):>8.3f}{lp:>5}{float(q3):>8.3f}{lc:>5}"
              f"{float(q0):>8.3f}{l0:>5}")

    print("\nDRAW LEVEL, PER ARM  (class %: BEY/POS/INTH | COR | LOW/ATQ0/SUB)")
    print(f"  {'config':<15}{'arm':<7}{'n':>4}{'s1':>7}{'s2':>8}"
          f"{'%BEY':>6}{'%POS':>6}{'%INTH':>7}{'%COR':>6}{'%LOW':>6}{'%ATQ0':>7}{'%SUB':>6}")
    for cfg in ORDER:
        for arm, _, _ in ARMS:
            v = [(lv, *geom[cid]) for cid in cids
                 for lv in draws[arm].get((cfg, cid), [])]
            if not v:
                continue
            n = len(v)
            s1 = sum(abs(lv - lc) for lv, lp, lc, l0 in v) / n
            s2 = sum(lv - lc for lv, lp, lc, l0 in v) / n
            cl = Counter(klass(lv, lp, lc, l0) for lv, lp, lc, l0 in v)
            pc = lambda k: 100 * cl.get(k, 0) / n
            print(f"  {cfg:<15}{arm[:5]:<7}{n:>4}{s1:>7.3f}{s2:>+8.3f}"
                  f"{pc('BEY'):>6.1f}{pc('POS'):>6.1f}{pc('INTH'):>7.1f}"
                  f"{pc('COR'):>6.1f}{pc('LOW'):>6.1f}{pc('ATQ0'):>7.1f}{pc('SUB'):>6.1f}")

    print("\nPAIRED PER CELL (ARITH - RULED_D30, draw-mean per cell; spans cancel in pair)")
    print(f"  {'config':<15}{'mean d_s1':>10}{'mean d_s2':>10}"
          f"{'cells s1: worse/equal/better':>30}{'s2 down/same/up':>18}")
    for cfg in ORDER:
        d1, d2 = [], []
        for cid in cids:
            a = draws["ARITH_D30"].get((cfg, cid), [])
            r = draws["RULED_D30"].get((cfg, cid), [])
            if not a or not r:
                continue
            lc = geom[cid][1]
            d1.append(sum(abs(x - lc) for x in a) / len(a)
                      - sum(abs(x - lc) for x in r) / len(r))
            d2.append(sum(x - lc for x in a) / len(a)
                      - sum(x - lc for x in r) / len(r))
        w = sum(1 for x in d1 if x > 0.05)
        e = sum(1 for x in d1 if abs(x) <= 0.05)
        b = sum(1 for x in d1 if x < -0.05)
        dn = sum(1 for x in d2 if x < -0.05)
        sm = sum(1 for x in d2 if abs(x) <= 0.05)
        up = sum(1 for x in d2 if x > 0.05)
        print(f"  {cfg:<15}{sum(d1)/len(d1):>+10.3f}{sum(d2)/len(d2):>+10.3f}"
              f"{f'{w}/{e}/{b}':>30}{f'{dn}/{sm}/{up}':>18}")

    print("\nMODAL PER CELL, PAIRED  (RULED_D30 modal -> ARITH modal; '.'=tie)")
    print(f"  {'config':<15}" + "".join(f"{cid:>8}" for cid in cids))
    for cfg in ORDER:
        row = f"  {cfg:<15}"
        for cid in cids:
            mr = mode(draws["RULED_D30"].get((cfg, cid), []))
            ma = mode(draws["ARITH_D30"].get((cfg, cid), []))
            row += f"{('.' if mr is None else mr)}->{('.' if ma is None else ma)}".rjust(8)
        print(row)
    print("  (correct level per cell: " +
          ", ".join(f"{cid}:{geom[cid][1]}" for cid in cids) + ")")


if __name__ == "__main__":
    main()
