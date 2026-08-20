"""arith_analyze.py — reads the ARITH_D30 run against the banked PARTIAL_RULED_D30 arm.

    python scratch_fable/arith_analyze.py

The delta=0.30 coupling test, closing Candidate 3's structural hole: per config and
cell, does the RULED_D30 modal answer equal the same config's ARITH_D30 modal answer?
Discriminating pairs (ARITH modal != level(b_pos)) reported alongside the pooled
figure, per the item-2 discipline. Baselines: all-b_pos, all-q(0.3).
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
ARITH = f"{ROOT}/scratch_fable/results_arith/arith_results_live.json"
BANKED = f"{ROOT}/results_v2/v2_results_live_banked.json"
STIM_A = f"{ROOT}/scratch_fable/arith_d30_stimuli.json"
STIM_B = f"{ROOT}/silence_v2_stimuli_banked.json"
ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor")


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
        b[(r["config"], s["cell"])].append(
            S.target_level(r["candidate"], r["confidence"], s["target_label"]))
    return ({k: mode(v) for k, v in b.items()}, {k: len(v) for k, v in b.items()}, res)


def main():
    la, na, ra = levels(ARITH, STIM_A)
    lb, nb, rb = levels(BANKED, STIM_B)
    cells = [c for c in M.build() if M.banked_viable(c)]
    L = {c["id"]: (M.level(c["b_pos"]), M.level(c[f"q_{M.DELTA_BANKED}"])) for c in cells}
    ids = [c["id"] for c in cells]

    print(f"ARITH_D30: {ra['n_ok']}/{ra['n_records']} usable draws")
    print("EXPLORATORY extension, authorised 2026-08-16. Not pre-registered.\n")

    print("per-cell: ARITH_D30 modal / RULED_D30 modal   (l_pos, l_q3 in brackets)")
    print(f"  {'cell':<6}" + "".join(f"{c[:11]:>14}" for c in ORDER))
    for cid in ids:
        row = f"  {cid:<3}{str(L[cid]):<10}"
        for cfg in ORDER:
            a, b = la.get((cfg, cid)), lb.get((cfg, cid))
            row += f"{str(a) + '/' + str(b):>11}   "
        print(row)

    print("\ncoupling in the delta=0.30 arm: RULED_D30 == own ARITH_D30, vs baselines")
    print(f"  {'config':<15}{'all n':>7}{'coupl':>7}{'b_pos':>7}{'q3':>6}"
          f"{'   disc n':>9}{'coupl':>7}{'b_pos':>7}{'q3':>6}   ARITH accuracy")
    tot = Counter()
    for cfg in ORDER:
        h = Counter()
        acc = t_acc = 0
        for cid in ids:
            a, b = la.get((cfg, cid)), lb.get((cfg, cid))
            lp, lq3 = L[cid]
            if a is not None:
                t_acc += 1
                acc += a == lq3
            if a is None or b is None:
                continue
            h["n"] += 1
            h["c"] += a == b
            h["b"] += lp == b
            h["q"] += lq3 == b
            if a != lp:
                h["dn"] += 1
                h["dc"] += a == b
                h["db"] += lp == b
                h["dq"] += lq3 == b
        for k in h:
            tot[k] += h[k]
        print(f"  {cfg:<15}{h['n']:>7}{h['c']:>7}{h['b']:>7}{h['q']:>6}"
              f"{h['dn']:>9}{h['dc']:>7}{h['db']:>7}{h['dq']:>6}"
              f"   {acc}/{t_acc} at q(.3)")
    print(f"  {'POOLED':<15}{tot['n']:>7}{tot['c']:>7}{tot['b']:>7}{tot['q']:>6}"
          f"{tot['dn']:>9}{tot['dc']:>7}{tot['db']:>7}{tot['dq']:>6}")

    print("\nreading (corrected framing, 2026-08-16):")
    print("  ARITH_D30 removes only the IDENTIFICATION of absences; interpreting each")
    print("  enumerated absence under the stated dropout rate is still required, so it")
    print("  is NOT a FULL analogue and this coupling figure is not comparable to the")
    print("  delta=0 one. ARITH accuracy is the delta>0 competence gate: a config that")
    print("  fails it has floor-confounded D30 readings that cannot be read as")
    print("  silence-blindness. For configs that pass, coupling here is close to")
    print("  vacuous-by-correctness; the informative outputs are the gate itself and")
    print("  whether a config's DEVIATIONS match across the two conditions.")


if __name__ == "__main__":
    main()
