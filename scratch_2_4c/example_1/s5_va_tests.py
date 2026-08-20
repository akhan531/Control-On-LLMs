"""
s5_va_tests.py — Verification V-A for Pattern A (approved 2026-08-17): A1, A2, A4.

A1  kills symmetric confidence-hedging ("avoid Very confident"):
      FULL up-rate   = P(l_obs > 0) on the 11 cells with l_cor = 0
      BLIND in-rate  = P(l_obs < 3) on the 8 cells with l_cor = 3
    Hedging predicts inward drift at BOTH extremes. Pre-fixed kill condition:
    hedging STANDS (A dies) if BLIND in-rate >= 0.5 * FULL up-rate.

A2  kills directional lean toward the positives' candidate:
      BLIND up-rate (B u D, l_cor = 2)  = P(l_obs > 2)   drift above b_pos, no negatives
      FULL  up-rate (B u D, matched)    = P(l_obs > l_cor)
    Lean predicts comparable drift in both. Pre-fixed kill condition:
    lean STANDS if BLIND up-rate >= 0.5 * FULL up-rate on the matched cells.
    D-only pair reported as well (one-bin moves both sides).

A4  "negatives register" (anti-ignoring): per gated config, FULL C cells:
    PASS if modal level != 3 (= level(b_pos)) in >= 2 of 3 cells; a modal tie does
    not count toward the 2. Draw-level P(l_obs = 3) on C-FULL reported alongside.

P4 exclusions inherited everywhere. Gated five are the claim population; deepseek
and anchor computed and shown as excluded context. Existing data only.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
SHOWN = GATED + ("deepseek", "anchor")


def load():
    res = json.load(open(f"{ROOT}/results_v2/v2_results_live.json"))
    stim = {s["id"]: s for s in json.load(
        open(f"{ROOT}/silence_v2_stimuli.json"))["stimuli"]}
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]
    draws = defaultdict(list)          # (config, arm, cell) -> [(l_obs, l_cor)]
    fails = Counter()
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        if st["cell"] in p4.get(r["config"], []):
            continue
        if not r.get("ok"):
            fails[(r["config"], st["condition"])] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], st["condition"], st["cell"])].append(
            (lv, st["level_target"]))
    return draws, fails


def rate(draws, cfg, arm, want_cor, pred):
    obs = [(lo, lc) for (c, a, cell), v in draws.items()
           if c == cfg and a == arm
           for (lo, lc) in v if lc in want_cor]
    hit = sum(1 for lo, lc in obs if pred(lo, lc))
    return hit, len(obs)


def pct(h, n):
    return f"{h:>3}/{n:<3} {100*h/n:5.1f}%" if n else "   --"


def main():
    draws, fails = load()

    # ---------------- A1 ----------------
    print("A1  symmetric hedging: inward drift must appear at BOTH extremes if real")
    print(f"  {'config':<15}{'FULL up (l_cor=0)':>20}{'BLIND in (l_cor=3)':>22}"
          f"{'ratio':>8}   verdict on hedging")
    for cfg in SHOWN:
        fu = rate(draws, cfg, "FULL", (0,), lambda lo, lc: lo > lc)
        bi = rate(draws, cfg, "PARTIAL_BLIND", (3,), lambda lo, lc: lo < lc)
        r_full = fu[0] / fu[1] if fu[1] else float("nan")
        r_blind = bi[0] / bi[1] if bi[1] else float("nan")
        ratio = (r_blind / r_full) if r_full else float("inf")
        verdict = "hedging STANDS" if r_blind >= 0.5 * r_full else "hedging dies"
        tag = "" if cfg in GATED else "  [excluded]"
        print(f"  {cfg:<15}{pct(*fu):>20}{pct(*bi):>22}{ratio:>8.3f}   {verdict}{tag}")

    # ---------------- A2 ----------------
    print("\nA2  directional lean toward the positives' candidate (B u D matched cells)")
    print(f"  {'config':<15}{'FULL up (BuD)':>18}{'BLIND up (BuD)':>18}{'ratio':>8}"
          f"{'D-only FULL up':>16}{'D-only BLIND up':>17}   verdict on lean")
    bud = ("B1", "B2", "B3", "D1", "D2", "D3")
    for cfg in SHOWN:
        fu = rate({k: v for k, v in draws.items() if k[2] in bud},
                  cfg, "FULL", (0, 1), lambda lo, lc: lo > lc)
        bu = rate({k: v for k, v in draws.items() if k[2] in bud},
                  cfg, "PARTIAL_BLIND", (2,), lambda lo, lc: lo > lc)
        fd = rate({k: v for k, v in draws.items() if k[2] in bud[3:]},
                  cfg, "FULL", (1,), lambda lo, lc: lo > lc)
        bd = rate({k: v for k, v in draws.items() if k[2] in bud[3:]},
                  cfg, "PARTIAL_BLIND", (2,), lambda lo, lc: lo > lc)
        r_full = fu[0] / fu[1] if fu[1] else float("nan")
        r_blind = bu[0] / bu[1] if bu[1] else float("nan")
        ratio = (r_blind / r_full) if r_full else float("inf")
        verdict = "lean STANDS" if r_blind >= 0.5 * r_full else "lean dies"
        tag = "" if cfg in GATED else "  [excluded]"
        print(f"  {cfg:<15}{pct(*fu):>18}{pct(*bu):>18}{ratio:>8.3f}"
              f"{pct(*fd):>16}{pct(*bd):>17}   {verdict}{tag}")

    # ---------------- A4 ----------------
    print("\nA4  negatives register: FULL C cells, modal != 3 in >= 2/3 (tie never counts)")
    print(f"  {'config':<15}{'C1':>5}{'C2':>5}{'C3':>5}{'pass':>7}"
          f"{'draw P(l_obs=3) on C-FULL':>28}")
    for cfg in SHOWN:
        modal = {}
        for c in ("C1", "C2", "C3"):
            v = [lo for lo, _ in draws.get((cfg, "FULL", c), [])]
            cnt = Counter(v).most_common()
            modal[c] = (None if not cnt or (len(cnt) > 1 and cnt[0][1] == cnt[1][1])
                        else cnt[0][0])
        ok = sum(1 for c in modal.values() if c is not None and c != 3)
        p3 = rate({k: v for k, v in draws.items() if k[2].startswith("C")},
                  cfg, "FULL", (0,), lambda lo, lc: lo == 3)
        cellstr = "".join(f"{'tie' if modal[c] is None else modal[c]:>5}"
                          for c in ("C1", "C2", "C3"))
        tag = "" if cfg in GATED else "  [excluded]"
        print(f"  {cfg:<15}{cellstr}{'PASS' if ok >= 2 else 'FAIL':>7}"
              f"{pct(*p3):>28}{tag}")

    # ---------------- missingness in the arms used ----------------
    used = [(c, a) for (c, a) in fails if a in
            ("FULL", "PARTIAL_BLIND")]
    if used:
        print("\nfailures in arms used here (excluded from rates, reported per gate rule):")
        for (c, a), n in sorted(fails.items()):
            if a in ("FULL", "PARTIAL_BLIND"):
                print(f"  {c:<15}{a:<15}{n}")


if __name__ == "__main__":
    main()
