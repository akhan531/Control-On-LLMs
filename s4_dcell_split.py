"""
s4_dcell_split.py: G2.4, the D-cell split of the displaced draws, by observed level.

Two accounts predict the same displacement in D1-D3 and are told apart by where the
displaced draws land:

  b_pos-anchoring     displaced draws sit at level 2 = level(b_pos)
  ordinal extremity   displaced draws sit at level 3, the top of the scale
                      (BayesBench: models sharpen the extreme labels and collapse
                      the middle two on a four-level ordinal scale)

In D1-D3 the two accounts are disjoint and one bin apart, because l_cor = 1 and
l_pos = 2 there. Both facts are asserted at load rather than assumed.

Population discipline, per the frozen competence gate and P4:
  - the gated five carry the claim; the gate-excluded pair is printed as context
    and never pooled into a claim number
  - P4 cell exclusions are inherited from results_v2/v2_gates.json
  - PARTIAL_RULED is the result arm, FULL the control arm. The gate selects on
    FULL, so the two are never pooled.

Run from the repository root. Reads frozen files only; writes
results_v2/v2_dcell_split.json plus stdout.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import silence_v2_stimuli as S  # noqa: E402

RESULTS = ROOT / "results_v2" / "v2_results_live.json"
STIM = ROOT / "silence_v2_stimuli.json"
GATES = ROOT / "results_v2" / "v2_gates.json"

GATED = ("sol-high", "sol-none", "glm-high", "deepseek-high", "glm")
UNGATED = ("deepseek", "anchor")
DCELLS = ("D1", "D2", "D3")
LEVELS = (0, 1, 2, 3)


def load():
    res = json.load(open(RESULTS))
    stim = {s["id"]: s for s in json.load(open(STIM))["stimuli"]}
    p4 = json.load(open(GATES))["P4_excluded"]
    return res, stim, p4


def check_geometry(stim):
    """The whole test rests on l_cor = 1 and l_pos = 2 in the D cells. Assert it."""
    seen = set()
    for s in stim.values():
        if s["cell"] not in DCELLS:
            continue
        if s["condition"] in ("FULL", "PARTIAL_RULED"):
            assert s["level_target"] == 1, f"{s['id']}: l_cor {s['level_target']} != 1"
        assert s["l_pos_target"] == 2, f"{s['id']}: l_pos {s['l_pos_target']} != 2"
        assert s["l_q_target"] == 1, f"{s['id']}: l_q {s['l_q_target']} != 1"
        seen.add((s["cell"], s["condition"]))
    print("geometry asserted in D1-D3: l_cor = 1, l_pos = 2, so level 2 is the "
          "b_pos point and level 3 is the scale endpoint, one bin apart")
    return seen


def tally(res, stim, p4, condition):
    """(config) -> Counter over observed target-frame level; plus failures, per cell."""
    hist = defaultdict(Counter)
    per_cell = defaultdict(Counter)
    fails = Counter()
    for r in res["records"]:
        s = stim[r["stimulus_id"]]
        if s["cell"] not in DCELLS or s["condition"] != condition:
            continue
        cfg = r["config"]
        if s["cell"] in p4.get(cfg, []):
            continue
        if not r.get("ok"):
            fails[cfg] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], s["target_label"])
        hist[cfg][lv] += 1
        per_cell[(cfg, s["cell"])][lv] += 1
    return hist, per_cell, fails


def row(cfg, c, fails):
    n = sum(c.values())
    over = c[0]
    at_cor = c[1]
    at_pos = c[2]
    beyond = c[3]
    disp = at_pos + beyond
    return (f"  {cfg:<15}{n:>5}{fails.get(cfg, 0):>6}"
            f"{over:>7}{at_cor:>7}{at_pos:>7}{beyond:>7}"
            f"{disp:>11}{over:>7}")


def block(title, hist, fails, configs):
    print(f"\n{title}")
    print(f"  {'config':<15}{'n':>5}{'fail':>6}"
          f"{'lv0':>7}{'lv1':>7}{'lv2':>7}{'lv3':>7}"
          f"{'displaced':>11}{'over':>7}")
    tot = Counter()
    for cfg in configs:
        c = hist.get(cfg)
        if not c:
            continue
        print(row(cfg, c, fails))
        tot.update(c)
    n = sum(tot.values())
    if n:
        print(f"  {'POOLED':<15}{n:>5}{sum(fails.get(c, 0) for c in configs):>6}"
              f"{tot[0]:>7}{tot[1]:>7}{tot[2]:>7}{tot[3]:>7}"
              f"{tot[2] + tot[3]:>11}{tot[0]:>7}")
    return tot


def main():
    res, stim, p4 = load()
    check_geometry(stim)
    print(f"\n{res['n_ok']}/{res['n_records']} usable draws in the campaign overall")

    out = {}
    for cond in ("PARTIAL_RULED", "FULL"):
        hist, per_cell, fails = tally(res, stim, p4, cond)
        arm = "result arm" if cond == "PARTIAL_RULED" else "control arm (gate selects here)"
        tot = block(f"{cond}: D1-D3, gated five, P4-inherited  [{arm}]",
                    hist, fails, GATED)
        block(f"{cond}: D1-D3, gate-excluded pair, context only, never pooled",
              hist, fails, UNGATED)

        disp = tot[2] + tot[3]
        n = sum(tot.values())
        print(f"\n  displaced draws, gated five: {disp} of {n}")
        if disp:
            print(f"    at level 2 = level(b_pos):        {tot[2]:>4}  "
                  f"({100 * tot[2] / disp:.1f}% of displaced)")
            print(f"    at level 3 = scale endpoint:      {tot[3]:>4}  "
                  f"({100 * tot[3] / disp:.1f}% of displaced)")
        print(f"    past b* (level 0), the over-read: {tot[0]:>5}")
        if not hist.get("anchor"):
            print("    note: anchor contributes nothing above, because P4 excludes it on "
                  "D1-D3, so its absence is the pre-registration, not a bug")

        # per-configuration universals: R2, the universal behind the fraction
        univ_no_bey = [c for c in GATED if hist.get(c) and hist[c][3] == 0]
        univ_no_over = [c for c in GATED if hist.get(c) and hist[c][0] == 0]
        present = [c for c in GATED if hist.get(c)]
        print(f"    configurations with zero level-3 draws: "
              f"{len(univ_no_bey)} of {len(present)}  {univ_no_bey}")
        print(f"    configurations with zero level-0 draws: "
              f"{len(univ_no_over)} of {len(present)}  {univ_no_over}")

        print(f"\n  per cell (gated five pooled), {cond}")
        print(f"    {'cell':<6}{'n':>5}{'lv0':>7}{'lv1':>7}{'lv2':>7}{'lv3':>7}")
        for cell in DCELLS:
            c = Counter()
            for cfg in GATED:
                c.update(per_cell.get((cfg, cell), Counter()))
            print(f"    {cell:<6}{sum(c.values()):>5}"
                  f"{c[0]:>7}{c[1]:>7}{c[2]:>7}{c[3]:>7}")

        out[cond] = {
            "gated": {c: {str(k): hist[c][k] for k in LEVELS} for c in GATED if hist.get(c)},
            "ungated_context": {c: {str(k): hist[c][k] for k in LEVELS}
                                for c in UNGATED if hist.get(c)},
            "gated_pooled": {str(k): tot[k] for k in LEVELS},
            "failures": dict(fails),
            "per_cell_gated": {f"{cell}": {str(k): sum(per_cell.get((cfg, cell), Counter())[k]
                                                       for cfg in GATED) for k in LEVELS}
                               for cell in DCELLS},
        }

    (ROOT / "results_v2" / "v2_dcell_split.json").write_text(json.dumps(out, indent=2))
    print("\nwritten to results_v2/v2_dcell_split.json")


if __name__ == "__main__":
    main()
