"""Candidate 1: two-endpoint model. A config is a single bit (blind|aware), fitted on
delta=0 PARTIAL_RULED only. Prediction for held-out delta=0.30 arm:
  blind -> level(b_pos)   aware -> level(q(0.3))
Baselines: everything b_pos, everything q(0.3). Exact-level hits, modal per cell.
"""
import json
from collections import Counter

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC, BC = T["primary_cells"], T["banked_cells"]

CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
ALLCELLS = list(L.keys())
BANKED_CELLS = sorted({k.split("|")[1] for k in BC})
COND_B = "PARTIAL_RULED_D30"

print("=== FIT: classify each config on delta=0 PARTIAL_RULED (14 cells) ===")
print("per-cell vote: modal level strictly closer to l_pos -> blind vote, closer to l_q0 -> aware vote, tie/neither -> counted separately")
cls = {}
for cfg in CONFIGS:
    votes = Counter()
    detail = []
    for cid in ALLCELLS:
        m = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not m or m["modal"] is None:
            votes["none"] += 1; detail.append(f"{cid}:--"); continue
        lp, lq = L[cid]["l_pos"], L[cid]["l_q0"]
        d_p, d_q = abs(m["modal"] - lp), abs(m["modal"] - lq)
        v = "blind" if d_p < d_q else "aware" if d_q < d_p else "tie"
        votes[v] += 1
        detail.append(f"{cid}:{m['modal']}({v[0]})")
    label = "aware" if votes["aware"] > votes["blind"] else "blind" if votes["blind"] > votes["aware"] else "tie"
    cls[cfg] = label
    print(f"  {cfg:<15} {label.upper():<6} votes={dict(votes)}")
    print(f"      {' '.join(detail)}")

print("\n=== PREDICT: held-out delta=0.30 arm, modal level per cell ===")
rows = []
tot = {"model": 0, "bpos": 0, "q": 0, "n": 0}
for cfg in CONFIGS:
    hit_m = hit_b = hit_q = n = 0
    misses = []
    for cid in BANKED_CELLS:
        m = BC.get(f"{cfg}|{cid}|{COND_B}")
        if not m or m["modal"] is None:
            continue
        obs = m["modal"]
        lp, lq3 = L[cid]["l_pos"], L[cid]["l_q3"]
        pred = lp if cls[cfg] == "blind" else lq3
        n += 1
        hit_m += pred == obs
        hit_b += lp == obs
        hit_q += lq3 == obs
        if pred != obs:
            misses.append(f"{cid}:pred{pred}obs{obs}")
    tot["model"] += hit_m; tot["bpos"] += hit_b; tot["q"] += hit_q; tot["n"] += n
    print(f"  {cfg:<15} [{cls[cfg]:<5}] model {hit_m}/{n}   all-b_pos {hit_b}/{n}   all-q {hit_q}/{n}"
          + (f"   misses: {' '.join(misses)}" if misses else ""))
print(f"  {'POOLED':<15}         model {tot['model']}/{tot['n']}   all-b_pos {tot['bpos']}/{tot['n']}   all-q {tot['q']}/{tot['n']}")

print("\n=== same test at the DRAW level (no modal pooling) ===")
tot = {"model": 0, "bpos": 0, "q": 0, "n": 0}
for cfg in CONFIGS:
    hit_m = hit_b = hit_q = n = 0
    for d in T["banked_draws"]:
        if d["config"] != cfg:
            continue
        cid = d["cell"]
        lp, lq3 = L[cid]["l_pos"], L[cid]["l_q3"]
        pred = lp if cls[cfg] == "blind" else lq3
        n += 1
        hit_m += pred == d["level"]
        hit_b += lp == d["level"]
        hit_q += lq3 == d["level"]
    tot["model"] += hit_m; tot["bpos"] += hit_b; tot["q"] += hit_q; tot["n"] += n
    print(f"  {cfg:<15} model {hit_m}/{n}   all-b_pos {hit_b}/{n}   all-q {hit_q}/{n}")
print(f"  {'POOLED':<15} model {tot['model']}/{tot['n']}   all-b_pos {tot['bpos']}/{tot['n']}   all-q {tot['q']}/{tot['n']}")

print("\n=== sign test on pooled modal hits: model vs best baseline ===")
# cells where model and baseline disagree in correctness
for base_name, base_pred in (("all-b_pos", "lp"), ("all-q", "lq3")):
    wins = losses = 0
    for cfg in CONFIGS:
        for cid in BANKED_CELLS:
            m = BC.get(f"{cfg}|{cid}|{COND_B}")
            if not m or m["modal"] is None:
                continue
            obs = m["modal"]
            lp, lq3 = L[cid]["l_pos"], L[cid]["l_q3"]
            pred = lp if cls[cfg] == "blind" else lq3
            bp = lp if base_pred == "lp" else lq3
            if (pred == obs) and (bp != obs):
                wins += 1
            elif (pred != obs) and (bp == obs):
                losses += 1
    from math import comb
    n = wins + losses
    p = sum(comb(n, i) for i in range(wins, n + 1)) / 2**n if n else 1.0
    print(f"  vs {base_name}: wins {wins}, losses {losses}, one-sided binomial p = {p:.4g}")
