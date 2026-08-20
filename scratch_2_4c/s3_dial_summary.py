"""
s3_dial_summary.py — Step 3 for candidate 2A: the N-k dial in RULEDCTRL (2026-08-17).

Statistic justification (per checkpoint):
  The framework supplies BOTH reference curves per cell in closed form:
    floor      l_cor = level(b*) = 0, held constant by design (p compensates)
    staircase  l_pos = level(b_pos(p, k)), which moves as p falls with N
  The dial statistic is the same location machinery as Example 1, indexed by N-k:
  per-cell location class (COR / INT / POS / BEY; OVER inexpressible, l_cor = 0) and
  per-cell bin distances to the two curves. Pooled normalised s is NOT used: spans
  differ along the dial (3,3,3,2,2) and the audit found mean-s span-dependent.
  epsilon = D(b*||b_pos) is printed per cell: the true evidential weight of the
  silences in nats.

Outputs:
  1. dial geometry: p, b_pos exact, its nominal level, MEASURED-band status
     (dead zones flagged), b*, span, epsilon
  2. per config x cell draw-level level distributions, mean level, failures
  3. credit table: bins below the staircase (and /span with caveat)
  4. ceiling check: draws ABOVE the staircase (BEY), gated vs excluded
Existing data only; stdout only.
"""

import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
ORDER = GATED + ("deepseek", "anchor")


def main():
    res = json.load(open(f"{ROOT}/results_sweep/sweep_results_live.json"))
    stim = {s["id"]: s for s in json.load(
        open(f"{ROOT}/sweep_stimuli.json"))["stimuli"]}

    cells = {}
    for s in stim.values():
        if s["sweep"] != "RULEDCTRL":
            continue
        cid = s["cell"]
        if cid in cells:
            continue
        pn = round(s["p"] * 100)
        p = F(pn, 100)
        bp = M.b_pos(p, s["k"])
        bs = M.b_star(p, s["N"], s["k"])
        cells[cid] = {
            "N": s["N"], "k": s["k"], "nk": s["N"] - s["k"], "p": pn,
            "b_pos": float(bp), "l_pos": M.level(bp),
            "band_pos": M.in_band(bp),
            "b_star": float(bs), "l_cor": M.level(bs),
            "eps": M.kl(bs, bp),
        }
    order = sorted(cells)

    print("DIAL GEOMETRY (k = 3 fixed; p compensates to pin b*; both curves closed-form)")
    print(f"  {'cell':<6}{'N':>3}{'N-k':>5}{'p':>6}{'b_pos':>8}{'L_pos':>6}"
          f"{'band':>6}{'b*':>7}{'L_cor':>6}{'span':>6}{'eps(nats)':>10}")
    for c in order:
        m = cells[c]
        band = "ok" if m["band_pos"] is not None else "DEAD"
        print(f"  {c:<6}{m['N']:>3}{m['nk']:>5}{m['p']/100:>6.2f}{m['b_pos']:>8.3f}"
              f"{m['l_pos']:>6}{band:>6}{m['b_star']:>7.3f}{m['l_cor']:>6}"
              f"{m['l_pos']-m['l_cor']:>6}{m['eps']:>10.2f}")

    draws, fails = defaultdict(list), Counter()
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        if st["sweep"] != "RULEDCTRL":
            continue
        if not r.get("ok"):
            fails[(r["config"], st["cell"])] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], st["cell"])].append(lv)

    print("\nDRAW-LEVEL DISTRIBUTIONS  (per cell: counts at L0/L1/L2/L3 | mean | fails)")
    print(f"  {'config':<15}" + "".join(f"{c:>19}" for c in order))
    for cfg in ORDER:
        row = f"  {cfg:<15}"
        for c in order:
            v = draws.get((cfg, c), [])
            cnt = Counter(v)
            mean = sum(v) / len(v) if v else float("nan")
            row += (f"{cnt.get(0,0)}/{cnt.get(1,0)}/{cnt.get(2,0)}/{cnt.get(3,0)}"
                    f" {mean:4.1f}f{fails.get((cfg,c),0)}").rjust(19)
        tag = "" if cfg in GATED else "  [excluded]"
        print(row + tag)

    print("\nCREDIT: bins below the staircase, mean per cell "
          "(span printed; spans differ, so rows are not pooled)")
    print(f"  {'config':<15}" + "".join(f"{c:>10}" for c in order)
          + "     span: " + "/".join(str(cells[c]["l_pos"] - cells[c]["l_cor"])
                                     for c in order))
    for cfg in ORDER:
        row = f"  {cfg:<15}"
        for c in order:
            v = draws.get((cfg, c), [])
            cr = (sum(cells[c]["l_pos"] - x for x in v) / len(v)) if v else float("nan")
            row += f"{cr:>10.2f}"
        tag = "" if cfg in GATED else "  [excluded]"
        print(row + tag)

    print("\nCEILING CHECK: draws ABOVE the staircase (l_obs > l_pos)")
    for grp, cfgs in (("gated", GATED), ("excluded", ("deepseek", "anchor"))):
        above = n = 0
        detail = defaultdict(int)
        for cfg in cfgs:
            for c in order:
                for lv in draws.get((cfg, c), []):
                    n += 1
                    if lv > cells[c]["l_pos"]:
                        above += 1
                        detail[(cfg, c)] += 1
        print(f"  {grp:<9} {above}/{n} draws above"
              + (f"   {dict(detail)}" if detail else ""))

    print("\nfailures per config (RULEDCTRL, of 50 slots):",
          {cfg: sum(v for (c, _), v in fails.items() if c == cfg) for cfg in ORDER})


if __name__ == "__main__":
    main()
