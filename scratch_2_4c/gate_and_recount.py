"""
gate_and_recount.py — two checks ordered at checkpoint 1 verdicts (2026-08-17).

1. GATE (frozen): config enters a claim on arm X only if mean s1 < 1.0 bin at draw
   level on the matched control arm, all cells of that campaign, failures excluded
   and counted.
     PARTIAL_RULED (d=0)      -> gate on FULL          (main campaign, 14 cells)
     RULED_D30 / ARITH_D30    -> gate on ARITH_D30     (9 banked-viable cells)
   This script reproduces the FULL gate numbers Ali quoted (sanity) and computes the
   ARITH gate, reporting membership and the gap around 1.0.

2. RECOUNT for the corrected zero-over-read bullet:
   - RULED d=0, cells D1-D3 (the only cells with l_q = 1, where l_obs < l_cor is
     expressible): exact usable-draw denominator and count of s2 < 0.
   - FULL, same three cells: same counts (expected 5 overshoot draws).
   - banked RULED_D30: draws with l_obs < level(q(0.3)) out of usable (audit said
     7/620); ARITH_D30 same, as a companion line.

Reads frozen files only; writes nothing outside stdout.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor")
DCELLS = ("D1", "D2", "D3")


def load(results_path, stim_path):
    res = json.load(open(f"{ROOT}/{results_path}"))
    stim = {s["id"]: s for s in json.load(open(f"{ROOT}/{stim_path}"))["stimuli"]}
    return res, stim


def draw_errors(res, stim, condition=None, cells=None):
    """(config) -> list of s2 = l_obs - level_target over usable draws; plus failure counts."""
    errs, fails = defaultdict(list), Counter()
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        if condition and st["condition"] != condition:
            continue
        if cells and st["cell"] not in cells:
            continue
        if not r.get("ok"):
            fails[r["config"]] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        errs[r["config"]].append(lv - st["level_target"])
    return errs, fails


def gate_table(title, errs, fails, bar=1.0):
    print(f"\n{title}")
    print(f"  {'config':<15}{'n':>5}{'fail':>6}{'s1 mean':>9}   verdict")
    rows = []
    for cfg in ORDER:
        v = errs.get(cfg, [])
        if not v:
            continue
        s1 = sum(abs(x) for x in v) / len(v)
        rows.append((cfg, len(v), fails.get(cfg, 0), s1))
        print(f"  {cfg:<15}{len(v):>5}{fails.get(cfg,0):>6}{s1:>9.3f}   "
              f"{'ADMIT' if s1 < bar else 'EXCLUDE'}")
    admitted = sorted([r[3] for r in rows if r[3] < bar])
    excluded = sorted([r[3] for r in rows if r[3] >= bar])
    if admitted and excluded:
        print(f"  gap around bar: highest admitted {admitted[-1]:.3f} -> "
              f"lowest excluded {excluded[0]:.3f}")
    elif not excluded:
        print("  no configuration excluded")
    return rows


def main():
    # ---------- 1a. FULL gate, main campaign (sanity against Ali's numbers) ----------
    res, stim = load("results_v2/v2_results_live.json", "silence_v2_stimuli.json")
    errs, fails = draw_errors(res, stim, condition="FULL")
    gate_table("GATE for PARTIAL_RULED(d=0) claims: FULL, draw level, all 14 cells",
               errs, fails)

    # ---------- 1b. ARITH gate ----------
    ares, astim = load("scratch_fable/results_arith/arith_results_live.json",
                       "scratch_fable/arith_d30_stimuli.json")
    aerrs, afails = draw_errors(ares, astim)
    gate_table("GATE for RULED_D30/ARITH_D30 claims: ARITH_D30, draw level, 9 cells",
               aerrs, afails)

    # ---------- 2a. D-cell recount, RULED d=0 and FULL ----------
    print("\nRECOUNT: cells D1-D3, the only cells where l_obs < l_cor is expressible")
    for cond in ("PARTIAL_RULED", "FULL"):
        errs, fails = draw_errors(res, stim, condition=cond, cells=DCELLS)
        n = sum(len(v) for v in errs.values())
        neg = {cfg: [x for x in v if x < 0] for cfg, v in errs.items()}
        nneg = sum(len(v) for v in neg.values())
        detail = {cfg: len(v) for cfg, v in neg.items() if v}
        print(f"  {cond:<15} usable {n:>4}  failures {sum(fails.values()):>2}  "
              f"s2<0 draws {nneg}" + (f"  {detail}" if detail else ""))

    # ---------- 2b. banked RULED_D30 and ARITH_D30 below-l_cor ----------
    print("\nRECOUNT: delta=0.3 arms, draws with l_obs < level(q(0.3))")
    for label, rpath, spath in (
        ("RULED_D30", "results_v2/v2_results_live_banked.json",
         "silence_v2_stimuli_banked.json"),
        ("ARITH_D30", "scratch_fable/results_arith/arith_results_live.json",
         "scratch_fable/arith_d30_stimuli.json"),
    ):
        bres, bstim = load(rpath, spath)
        berrs, bfails = draw_errors(bres, bstim)
        n = sum(len(v) for v in berrs.values())
        below = {cfg: [x for x in v if x < 0] for cfg, v in berrs.items()}
        nbelow = sum(len(v) for v in below.values())
        detail = {cfg: sorted(v) for cfg, v in below.items() if v}
        print(f"  {label:<10} usable {n:>4}  failures {sum(bfails.values()):>2}  "
              f"below-l_cor draws {nbelow} ({100*nbelow/n:.1f}%)"
              + (f"  {detail}" if detail else ""))


if __name__ == "__main__":
    main()
