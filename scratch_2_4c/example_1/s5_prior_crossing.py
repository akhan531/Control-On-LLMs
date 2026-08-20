"""
s5_prior_crossing.py — prior-shrinkage vs b_pos-tracking test (rule frozen by Ali
2026-08-17, before this script was written or run).

Question: is the under-use of disconfirming evidence ASYMMETRIC (positive increment
lands, disconfirming increment under-weighted -> answers track/occupy b_pos) or is it
consistent with SYMMETRIC conservatism (one global gradient g < 1 shrinking the whole
update toward the prior)? In the target frame the total evidence points below the
prior in every delta=0 cell, so a symmetric under-updater can NEVER produce an answer
above P = 0.5: target-frame levels 2 (band 0.55-0.70) and 3 (band >= 0.80) are
unreachable by prior-shrinkage. Error mass at those levels — including mass sitting
exactly at level(b_pos) — is b_pos-tracking-consistent.

FROZEN RULE (verbatim from the checkpoint):
  * classify each gated configuration's error mass as PRIOR-SHRINKAGE-CONSISTENT
    (all mass at or below P = 0.5 in the target frame) versus B_POS-TRACKING-
    CONSISTENT (mass strictly above P = 0.5, or sitting exactly at level(b_pos))
  * a configuration with ZERO above-prior mass is EXCLUDED from the asymmetry claim,
    not counted as evidence against it; reported as instrument-limited
  * report per arm (FULL, PARTIAL_RULED, RULED_D30) and per configuration, with
    denominators
  * KILL CONDITION: the asymmetry claim dies if fewer than two gated configurations
    show above-prior or exact-b_pos mass in the RULED arms

Note printed with the D30 table: in RULED_D30 the correct level is itself above the
prior (q(0.3) in band 2), and the stated-channel evidence points UP, so below-prior
errors there are not symmetric-reachable either; the frozen rule is applied as
written, which makes the kill condition conservative.

Existing data only. P4 exclusions inherited. Stdout only.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
ORDER = GATED + ("deepseek", "anchor")
ARMS = ("FULL", "PARTIAL_RULED", "RULED_D30")


def ingest(res_path, stim_path, cond_map, draws, p4):
    res = json.load(open(f"{ROOT}/{res_path}"))
    stim = {s["id"]: s for s in json.load(open(f"{ROOT}/{stim_path}"))["stimuli"]}
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        arm = cond_map.get(st["condition"])
        if arm is None or not r.get("ok"):
            continue
        if st["cell"] in p4.get(r["config"], []):
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], arm)].append(
            (lv, st["level_target"], st["l_pos_target"], st["group"], st["cell"]))


def main():
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]
    draws = defaultdict(list)
    ingest("results_v2/v2_results_live.json", "silence_v2_stimuli.json",
           {"FULL": "FULL", "PARTIAL_RULED": "PARTIAL_RULED"}, draws, p4)
    ingest("results_v2/v2_results_live_banked.json", "silence_v2_stimuli_banked.json",
           {"PARTIAL_RULED_D30": "RULED_D30"}, draws, p4)

    print("PRIOR-CROSSING TEST  (above-prior = target-frame level >= 2, i.e. P > 0.5;")
    print("unreachable by any symmetric under-updater since evidence points below the")
    print("prior in every delta=0 cell)\n")

    eligible = {}
    print(f"  {'config':<15}{'arm':<14}{'n_ok':>6}{'n_err':>7}{'above':>7}"
          f"{'@l_pos':>8}{'>l_pos':>8}{'below':>7}{'%above':>8}")
    for cfg in ORDER:
        ruled_above = 0
        for arm in ARMS:
            v = draws.get((cfg, arm), [])
            if not v:
                continue
            err = [(lv, lc, lp) for lv, lc, lp, g, c in v if lv != lc]
            above = [e for e in err if e[0] >= 2]
            at_lp = sum(1 for lv, lc, lp in above if lv == lp)
            bey = sum(1 for lv, lc, lp in above if lv > lp)
            below = len(err) - len(above)
            pct = 100 * len(above) / len(err) if err else float("nan")
            if arm != "FULL":
                ruled_above += len(above)
            note = ""
            if arm == "RULED_D30":
                note = "  (below-prior not symmetric-reachable here either)"
            print(f"  {cfg:<15}{arm:<14}{len(v):>6}{len(err):>7}{len(above):>7}"
                  f"{at_lp:>8}{bey:>8}{below:>7}"
                  f"{('    --' if not err else f'{pct:7.1f}%')}"
                  + (note if cfg == ORDER[0] else ""))
        eligible[cfg] = ruled_above
        print()

    print("BY-GROUP breakdown of above-prior ERROR draws (delta=0 arms; the D column")
    print("is the equidistant-crossing geometry; C is the count-control group)")
    print(f"  {'config':<15}{'arm':<14}{'A':>5}{'B':>5}{'C':>5}{'D':>5}")
    for cfg in ORDER:
        for arm in ("FULL", "PARTIAL_RULED"):
            v = draws.get((cfg, arm), [])
            byg = Counter(g for lv, lc, lp, g, c in v if lv != lc and lv >= 2)
            print(f"  {cfg:<15}{arm:<14}"
                  + "".join(f"{byg.get(g, 0):>5}" for g in "ABCD"))

    print("\nFROZEN-RULE VERDICTS (gated five; excluded pair shown as context)")
    n_pass = 0
    for cfg in ORDER:
        tag = "" if cfg in GATED else "  [excl]"
        if eligible[cfg] > 0:
            verdict = f"b_pos-tracking mass in RULED arms: {eligible[cfg]} draws -> ELIGIBLE"
            if cfg in GATED:
                n_pass += 1
        else:
            verdict = ("zero above-prior mass anywhere in RULED arms -> EXCLUDED "
                       "(instrument-limited, not a counterexample)")
        print(f"  {cfg:<15}{verdict}{tag}")
    print(f"\nKILL CONDITION: dies if < 2 gated configs eligible. "
          f"Eligible gated: {n_pass}/5 -> asymmetry claim "
          f"{'SURVIVES' if n_pass >= 2 else 'DIES'}")


if __name__ == "__main__":
    main()
