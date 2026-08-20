"""
s5_vb_tests.py — Verification V-B for Pattern B (approved 2026-08-17): B1, B2, B4.

Pattern B primary (already computed, step 3/4): pi_pos(RULED) >= pi_pos(FULL) for
every gated config, strict in 4/5. These tests attack its INTERPRETATION: that
answers stop specifically AT the positives-only posterior when negatives must be
derived from silence.

B1  kills generic-difficulty drift, with the A2 lean baseline added.
    On B u D cells (the only cells with a rung ABOVE b_pos), RULED draws:
      POS = at l_pos(=2)   BEY = at 3
    Pre-fixed kill: targeted stop DIES if BEY >= 1/3 * POS (gated aggregate).
    Lean baseline: per config, RULED BEY rate vs BLIND lean rate P(l_obs>2 | BuD)
    measured in A2. BEY <= lean -> escapes are baseline weak-evidence inflation,
    not silence-specific.

B2  kills "answers high in RULED" response bias.
    (a) D cells: among RULED draws displaced above l_cor, bias predicts L3,
        b_pos-computation predicts L2 (= level(b_pos)).
        Pre-fixed kill: bias STANDS unless >= 2/3 of displaced D draws sit at exactly 2.
    (b) RULEDCTRL sweep corroboration (prompt length pinned ~1009 chars, correct
        level 0, k=3, N=7..15): level(b_pos) VARIES across the five cells, so
        stop-at-b_pos predicts modal = level_b_pos per cell while answer-high bias
        predicts flat 3. Scored per config: cells matching level_b_pos vs matching 3
        (cells where both coincide are uninformative and skipped).

B4  worst-case missingness for the primary inequality.
    Per gated config: reassign ALL its RULED failures to COR (deflating RULED pi_pos)
    and ALL its FULL failures to POS (inflating FULL pi_pos); recheck
    pi_pos(RULED) >= pi_pos(FULL). Kill: any config that flips is dropped from the
    count and the claim downgraded.

P4 exclusions inherited. Gated five only (excluded pair shown where informative).
Existing data only: main campaign + sweep. Writes nothing outside stdout.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
BUD = ("B1", "B2", "B3", "D1", "D2", "D3")


def load_main():
    res = json.load(open(f"{ROOT}/results_v2/v2_results_live.json"))
    stim = {s["id"]: s for s in json.load(
        open(f"{ROOT}/silence_v2_stimuli.json"))["stimuli"]}
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]
    draws, fails = defaultdict(list), Counter()
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        if st["cell"] in p4.get(r["config"], []):
            continue
        if not r.get("ok"):
            fails[(r["config"], st["condition"])] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], st["condition"], st["cell"])].append(
            (lv, st["level_target"], st["l_pos_target"]))
    return draws, fails


def main():
    draws, fails = load_main()

    # ---------------- B1 ----------------
    print("B1  targeted stop vs generic drift, B u D cells, RULED; lean baseline from A2")
    print(f"  {'config':<15}{'POS(=2)':>8}{'BEY(=3)':>8}{'BEY/POS':>9}"
          f"{'RULED BEY rate':>15}{'BLIND lean':>12}   reading")
    tot_pos = tot_bey = 0
    for cfg in GATED:
        pos = bey = n = 0
        blean_h = blean_n = 0
        for cell in BUD:
            for lo, lc, lp in draws.get((cfg, "PARTIAL_RULED", cell), []):
                n += 1
                pos += (lo == lp)
                bey += (lo > lp)
            for lo, lc, lp in draws.get((cfg, "PARTIAL_BLIND", cell), []):
                blean_n += 1
                blean_h += (lo > lp)
        tot_pos += pos
        tot_bey += bey
        bey_r = bey / n if n else 0.0
        lean_r = blean_h / blean_n if blean_n else 0.0
        if bey == 0:
            reading = "no escapes"
        elif bey_r <= lean_r:
            reading = "escapes <= lean: baseline inflation"
        else:
            reading = "escapes > lean: silence-specific"
        print(f"  {cfg:<15}{pos:>8}{bey:>8}"
              f"{(bey/pos if pos else 0):>9.3f}{100*bey_r:>14.1f}%"
              f"{100*lean_r:>11.1f}%   {reading}")
    print(f"  AGGREGATE gated: POS {tot_pos}  BEY {tot_bey}  ratio "
          f"{tot_bey/tot_pos:.3f}  (kill bar 0.333) -> "
          f"{'targeted stop DIES' if tot_bey >= tot_pos/3 else 'generic drift dies'}")

    # ---------------- B2a ----------------
    print("\nB2a  D cells, RULED, draws displaced above l_cor=1: at 2 (=b_pos) vs at 3")
    print(f"  {'config':<15}{'at 2':>6}{'at 3':>6}{'share at 2':>12}   verdict on bias")
    for cfg in GATED:
        c2 = c3 = 0
        for cell in ("D1", "D2", "D3"):
            for lo, lc, lp in draws.get((cfg, "PARTIAL_RULED", cell), []):
                if lo > lc:
                    c2 += (lo == 2)
                    c3 += (lo == 3)
        disp = c2 + c3
        share = c2 / disp if disp else None
        verdict = ("no displaced draws" if not disp else
                   "bias dies" if share >= 2 / 3 else "bias STANDS")
        print(f"  {cfg:<15}{c2:>6}{c3:>6}"
              f"{('   --' if share is None else f'{100*share:10.1f}%'):>12}   {verdict}")

    # ---------------- B2b ----------------
    print("\nB2b  RULEDCTRL sweep (length pinned, correct level 0): "
          "modal vs level_b_pos vs flat-3")
    sres = json.load(open(f"{ROOT}/results_sweep/sweep_results_live.json"))
    sstim = {s["id"]: s for s in json.load(
        open(f"{ROOT}/sweep_stimuli.json"))["stimuli"]}
    sdraws, sfails = defaultdict(list), Counter()
    for r in sres["records"]:
        st = sstim[r["stimulus_id"]]
        if st["sweep"] != "RULEDCTRL":
            continue
        if not r.get("ok"):
            sfails[r["config"]] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        sdraws[(r["config"], st["cell"])].append(lv)
    rcells = sorted({c for _, c in sdraws})
    lbp = {c: next(s["level_b_pos"] for s in sstim.values()
                   if s["cell"] == c) for c in rcells}
    print("  level_b_pos per cell: " +
          "  ".join(f"{c}:{lbp[c]}" for c in rcells) + "   (flat-3 = bias)")
    print(f"  {'config':<15}" + "".join(f"{c:>6}" for c in rcells)
          + f"{'match b_pos':>13}{'match 3':>9}{'fails':>7}")
    for cfg in GATED:
        row, mb, m3 = "", 0, 0
        for c in rcells:
            v = sdraws.get((cfg, c), [])
            cnt = Counter(v).most_common()
            m = (None if not cnt or (len(cnt) > 1 and cnt[0][1] == cnt[1][1])
                 else cnt[0][0])
            row += f"{'tie' if v and m is None else m if m is not None else '--':>6}"
            if m is not None and lbp[c] != 3:          # informative cells only
                mb += (m == lbp[c])
                m3 += (m == 3)
        print(f"  {cfg:<15}{row}{mb:>13}{m3:>9}{sfails.get(cfg,0):>7}")
    print("  (informative = cells where level_b_pos != 3; both-match cells skipped)")

    # ---------------- B4 ----------------
    print("\nB4  worst-case missingness: RULED failures -> COR, FULL failures -> POS")
    print(f"  {'config':<15}{'pi_pos FULL':>12}{'worst FULL':>12}"
          f"{'pi_pos RULED':>13}{'worst RULED':>12}   inequality")
    for cfg in GATED:
        def pi(arm):
            obs = [(lo, lp) for (c, a, cell), v in draws.items()
                   if c == cfg and a == arm for (lo, lc, lp) in v]
            return sum(1 for lo, lp in obs if lo == lp), len(obs)
        pf, nf = pi("FULL")
        pr, nr = pi("PARTIAL_RULED")
        ff = fails.get((cfg, "FULL"), 0)
        fr = fails.get((cfg, "PARTIAL_RULED"), 0)
        wf = (pf + ff) / (nf + ff) if nf + ff else 0
        wr = pr / (nr + fr) if nr + fr else 0
        ok = wr >= wf
        print(f"  {cfg:<15}{100*pf/nf:>11.1f}%{100*wf:>11.1f}%"
              f"{100*pr/nr:>12.1f}%{100*wr:>11.1f}%   "
              f"{'holds' if ok else 'FLIPS'}  (fails F{ff}/R{fr})")


if __name__ == "__main__":
    main()
