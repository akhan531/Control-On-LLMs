"""
s3_location_summary.py — Step 3 for Example 1: location classes and occupancy
(2026-08-17; renamed from s3_negation_summary.py at the 2026-08-17 anchor rebuild —
the statistics are construct-neutral and unchanged, only the self-description moved
from "negation" to "disconfirming evidence").

Statistic set (all framework-built, per checkpoint ruling):
  s2   = l_obs - l_cor        signed bin error; + = toward b_pos, - = past b*
  class: where l_obs sits on the b* <-> b_pos segment
         OVER   l_obs < l_cor            past the correct answer (expressible iff l_cor > 0)
         COR    l_obs = l_cor            at b*
         INT    l_cor < l_obs < l_pos    interior: negatives read but under-weighted
         POS    l_obs = l_pos            at the blind fixed point b_pos (ignores
                                         the disconfirming results entirely)
         BEY    l_obs > l_pos            beyond b_pos (expressible iff l_pos < 3)
  pi_cor = P(l_obs = l_cor), pi_pos = P(l_obs = l_pos)

Arms: FULL (printed negatives; the literature-recovery arm) and PARTIAL_RULED
(derived negatives; the extension arm). Both share l_cor = level(b*) by the pivot.

Discipline applied:
  - P4 exclusions inherited from results_v2/v2_gates.json (cell x config dropped, reported)
  - frozen FULL gate membership marked (deepseek, anchor excluded from claims; still shown)
  - failures counted per config x arm
Reads frozen files only; writes nothing outside stdout.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
ORDER = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high", "deepseek", "anchor")
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")   # FULL gate, frozen
ARMS = ("FULL", "PARTIAL_RULED")
CELLS = ("A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3",
         "B1", "B2", "B3", "D1", "D2", "D3")


def klass(lo, lc, lp):
    if lo < lc:
        return "OVER"
    if lo == lc:
        return "COR"
    if lo < lp:
        return "INT"
    if lo == lp:
        return "POS"
    return "BEY"


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def main():
    res = json.load(open(f"{ROOT}/results_v2/v2_results_live.json"))
    stim = {s["id"]: s for s in json.load(
        open(f"{ROOT}/silence_v2_stimuli.json"))["stimuli"]}
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]

    # (config, cell, arm) -> draw levels; failures per (config, arm)
    draws, fails, p4_dropped = defaultdict(list), Counter(), Counter()
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        if st["condition"] not in ARMS:
            continue
        if st["cell"] in p4.get(r["config"], []):
            p4_dropped[(r["config"], st["condition"])] += 1
            continue
        if not r.get("ok"):
            fails[(r["config"], st["condition"])] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], st["cell"], st["condition"])].append(
            (lv, st["level_target"], st["l_pos_target"]))

    print("P4 exclusions inherited (cell x config dropped before any statistic):")
    for cfg, cells in sorted(p4.items()):
        if cells:
            print(f"  {cfg}: {cells}")

    # ---------------- draw level ----------------
    for arm in ARMS:
        print(f"\n{'='*78}\n{arm}  |  draw level  |  14 cells minus P4 exclusions")
        print(f"  {'config':<14}{'n':>4}{'fl':>3}{'s2':>7}{'s1':>6}"
              f"{'%OVER':>7}{'%COR':>6}{'%INT':>6}{'%POS':>6}{'%BEY':>6}   note")
        for cfg in ORDER:
            obs = [o for c in CELLS for o in draws.get((cfg, c, arm), [])]
            if not obs:
                continue
            n = len(obs)
            s2 = sum(o[0] - o[1] for o in obs) / n
            s1 = sum(abs(o[0] - o[1]) for o in obs) / n
            cl = Counter(klass(*o) for o in obs)
            pct = lambda k: 100 * cl.get(k, 0) / n
            tag = "" if cfg in GATED else "EXCLUDED by FULL gate"
            print(f"  {cfg:<14}{n:>4}{fails.get((cfg,arm),0):>3}{s2:>+7.3f}{s1:>6.3f}"
                  f"{pct('OVER'):>7.1f}{pct('COR'):>6.1f}{pct('INT'):>6.1f}"
                  f"{pct('POS'):>6.1f}{pct('BEY'):>6.1f}   {tag}")
        # expressibility denominators
        n_over = sum(1 for cfg in ORDER for c in CELLS
                     for o in draws.get((cfg, c, arm), []) if o[1] > 0)
        n_bey = sum(1 for cfg in ORDER for c in CELLS
                    for o in draws.get((cfg, c, arm), []) if o[2] < 3)
        over = sum(1 for cfg in ORDER for c in CELLS
                   for o in draws.get((cfg, c, arm), [])
                   if o[1] > 0 and o[0] < o[1])
        bey = sum(1 for cfg in ORDER for c in CELLS
                  for o in draws.get((cfg, c, arm), [])
                  if o[2] < 3 and o[0] > o[2])
        print(f"  expressibility: OVER possible in {n_over} draws, occurs {over}; "
              f"BEY possible in {n_bey}, occurs {bey}")

    # ---------------- modal cell level ----------------
    print(f"\n{'='*78}\nmodal cell classes (ties dropped)   "
          "O=OVER C=COR I=INT P=POS B=BEY")
    print(f"  {'config':<14}" + "".join(f"{a:>26}" for a in
                                        ("FULL O/C/I/P/B(ties)", "RULED O/C/I/P/B(ties)")))
    for cfg in ORDER:
        row = f"  {cfg:<14}"
        for arm in ARMS:
            cl, ties = Counter(), 0
            for c in CELLS:
                obs = draws.get((cfg, c, arm), [])
                if not obs:
                    continue
                m = mode([o[0] for o in obs])
                if m is None:
                    ties += 1
                    continue
                cl[klass(m, obs[0][1], obs[0][2])] += 1
            row += f"{cl.get('OVER',0)}/{cl.get('COR',0)}/{cl.get('INT',0)}" \
                   f"/{cl.get('POS',0)}/{cl.get('BEY',0)} ({ties})".rjust(26)
        print(row)

    # ---------------- C and D sweeps: the ignore-vs-underweight signature ------
    print(f"\n{'='*78}\ncount-control sweeps, modal level per cell "
          "(b_pos pinned; negatives added left to right)")
    print("  C group: b_pos=0.982 (L3), b*: L0.  N-k = 4, 5, 7.  "
          "ignore-signature = flat at 3")
    print("  D group: b_pos=0.618 (L2), b*: L1.  N-k = 3, 5, 6.  "
          "ignore-signature = flat at 2")
    hdr = f"  {'config':<14}{'arm':<7}" + "".join(
        f"{c:>5}" for c in ("C1", "C2", "C3")) + "   " + "".join(
        f"{c:>5}" for c in ("D1", "D2", "D3"))
    print(hdr)
    for cfg in ORDER:
        for arm in ARMS:
            cells_out = []
            for c in ("C1", "C2", "C3", "D1", "D2", "D3"):
                if c in p4.get(cfg, []):
                    cells_out.append("  p4x")
                    continue
                obs = draws.get((cfg, c, arm), [])
                m = mode([o[0] for o in obs]) if obs else None
                cells_out.append(f"{'tie' if obs and m is None else m if m is not None else '--':>5}")
            print(f"  {cfg:<14}{'FULL' if arm=='FULL' else 'RULED':<7}"
                  + "".join(cells_out[:3]) + "   " + "".join(cells_out[3:]))


if __name__ == "__main__":
    main()
