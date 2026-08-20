"""Fold in the ARITH_D30 run, with the user's three corrections applied.

1. ARITH_D30 removes only the IDENTIFICATION of absences; interpretation under the
   stated dropout rate is still required (correct answer stays q(0.3)). It is NOT a
   FULL analogue and the delta=0.30 coupling is not comparable to the delta=0 one.
2. ARITH pass/fail is the delta>0 competence gate. Passers only for the coupling read.
3. Denominators everywhere; None-cell losses listed explicitly.
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
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
    return {k: mode(v) for k, v in b.items()}, {k: len(v) for k, v in b.items()}


la, na = levels(f"{ROOT}/scratch_fable/results_arith/arith_results_live.json",
                f"{ROOT}/scratch_fable/arith_d30_stimuli.json")
lb, nb = levels(f"{ROOT}/results_v2/v2_results_live_banked.json",
                f"{ROOT}/silence_v2_stimuli_banked.json")

cells = [c for c in M.build() if M.banked_viable(c)]
L = {c["id"]: (M.level(c["b_pos"]), M.level(c[f"q_{M.DELTA_BANKED}"])) for c in cells}
ids = [c["id"] for c in cells]

print("=== None-cell audit (modal tie or exclusion), per config ===")
for cfg in ORDER:
    lost_a = [f"{c}(n={na.get((cfg, c), 0)})" for c in ids if la.get((cfg, c)) is None]
    lost_b = [f"{c}(n={nb.get((cfg, c), 0)})" for c in ids if lb.get((cfg, c)) is None]
    print(f"  {cfg:<15} ARITH lost: {lost_a or '-'}   RULED_D30 lost: {lost_b or '-'}")

print("\n=== ARITH competence gate: cells at q(0.3), with denominators ===")
passers = []
for cfg in ORDER:
    n = sum(1 for c in ids if la.get((cfg, c)) is not None)
    h = sum(1 for c in ids if la.get((cfg, c)) == L[c][1])
    verdict = "PASS" if n and h / n > 0.5 else "FAIL"
    if verdict == "PASS":
        passers.append(cfg)
    print(f"  {cfg:<15} {h}/{n}  {verdict}")

print(f"\n=== coupling RULED_D30 == own ARITH_D30, ARITH-passers only: {passers} ===")
tot = Counter()
for cfg in passers:
    h = Counter()
    for cid in ids:
        a, b = la.get((cfg, cid)), lb.get((cfg, cid))
        if a is None or b is None:
            continue
        lp, lq3 = L[cid]
        h["n"] += 1; h["c"] += a == b; h["b"] += lp == b; h["q"] += lq3 == b
        if a != lp:
            h["dn"] += 1; h["dc"] += a == b; h["db"] += lp == b; h["dq"] += lq3 == b
    for k in h:
        tot[k] += h[k]
    print(f"  {cfg:<15} all {h['c']}/{h['n']} (b_pos {h['b']}/{h['n']}, q3 {h['q']}/{h['n']})"
          f"   disc {h['dc']}/{h['dn']} (b_pos {h['db']}/{h['dn']}, q3 {h['dq']}/{h['dn']})")
print(f"  {'POOLED':<15} all {tot['c']}/{tot['n']}   disc {tot['dc']}/{tot['dn']}"
      f" (baselines on disc: b_pos {tot['db']}/{tot['dn']}, q3 {tot['dq']}/{tot['dn']})")
print("  NOTE: for passers both conditions sit at q(0.3), so coupling here is close to")
print("  vacuous-by-correctness; the informative content of this run is the gate and")
print("  the sol-none localisation, not this figure.")

print("\n=== sol-none localisation: the confidence cap by condition family ===")
print("  cells where the answer routes through absence interpretation, 'Very confident'")
print("  (level 3 or 0) vs hedged (1/2), per arm:")
for arm, lv, nn, label in (("RULED d0", None, None, None),):
    pass
prim, _ = levels(f"{ROOT}/results_v2/v2_results_live.json", f"{ROOT}/silence_v2_stimuli.json")
# reuse tidy for full/ruled d0
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
PC = T["primary_cells"]
def extreme_count(getter, cs):
    ex = tot_ = 0
    out = []
    for cid in cs:
        m = getter(cid)
        if m is None:
            continue
        tot_ += 1
        if m in (0, 3):
            ex += 1
            out.append(f"{cid}:{m}")
    return ex, tot_, out
all14 = list(T["levels"].keys())
for name, g, cs in (
    ("FULL d0 (no absence step)", lambda c: PC.get(f"sol-none|{c}|FULL", {}).get("modal"), all14),
    ("RULED d0 (identify+interpret)", lambda c: PC.get(f"sol-none|{c}|PARTIAL_RULED", {}).get("modal"), all14),
    ("ARITH d30 (interpret only)", lambda c: la.get(("sol-none", c)), ids),
    ("RULED d30 (identify+interpret)", lambda c: lb.get(("sol-none", c)), ids),
):
    ex, t, out = extreme_count(g, cs)
    print(f"  {name:<32} extreme-confidence cells {ex}/{t}   {out}")
