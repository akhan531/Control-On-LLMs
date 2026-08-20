"""(a) frozen-channel competitor on the banked arm: aware -> level(q(0)) instead of level(q(0.3)).
(b) FULL->RULED coupling at delta=0: predict RULED modal from same config's FULL modal.
"""
import json
from collections import Counter
from math import comb

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC, BC = T["primary_cells"], T["banked_cells"]
CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
ALLCELLS = list(L.keys())
BANKED_CELLS = sorted({k.split("|")[1] for k in BC})

# classification from c1 (recompute identically)
def classify(cfg):
    votes = Counter()
    for cid in ALLCELLS:
        m = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not m or m["modal"] is None:
            continue
        lp, lq = L[cid]["l_pos"], L[cid]["l_q0"]
        d_p, d_q = abs(m["modal"] - lp), abs(m["modal"] - lq)
        if d_p < d_q:
            votes["blind"] += 1
        elif d_q < d_p:
            votes["aware"] += 1
    return "aware" if votes["aware"] > votes["blind"] else "blind"

cls = {c: classify(c) for c in CONFIGS}

print("=== (a) banked arm: binary+tracking vs binary+frozen-q0 vs baselines ===")
tot = Counter()
for cfg in CONFIGS:
    h = Counter(); n = 0
    for cid in BANKED_CELLS:
        m = BC.get(f"{cfg}|{cid}|PARTIAL_RULED_D30")
        if not m or m["modal"] is None:
            continue
        obs = m["modal"]
        lp, lq0, lq3 = L[cid]["l_pos"], L[cid]["l_q0"], L[cid]["l_q3"]
        n += 1
        h["track"] += (lp if cls[cfg] == "blind" else lq3) == obs
        h["frozen"] += (lp if cls[cfg] == "blind" else lq0) == obs
        h["bpos"] += lp == obs
        h["q3"] += lq3 == obs
    for k in h:
        tot[k] += h[k]
    tot["n"] += n
    print(f"  {cfg:<15} [{cls[cfg]:<5}] track {h['track']}/{n}  frozen-q0 {h['frozen']}/{n}  all-b_pos {h['bpos']}/{n}  all-q3 {h['q3']}/{n}")
print(f"  POOLED                  track {tot['track']}/{tot['n']}  frozen-q0 {tot['frozen']}/{tot['n']}  all-b_pos {tot['bpos']}/{tot['n']}  all-q3 {tot['q3']}/{tot['n']}")

print("\n=== (b) FULL->RULED coupling, delta=0: pred RULED = own FULL modal ===")
print("  hits/n on cells where both modals exist; baselines all-b_pos, all-q0; per config")
tot = Counter()
for cfg in CONFIGS:
    h = Counter(); n = 0
    rows = []
    for cid in ALLCELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL")
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not mf or not mr or mf["modal"] is None or mr["modal"] is None:
            continue
        obs, pred = mr["modal"], mf["modal"]
        lp, lq0 = L[cid]["l_pos"], L[cid]["l_q0"]
        n += 1
        h["coupl"] += pred == obs
        h["bpos"] += lp == obs
        h["q0"] += lq0 == obs
        if pred != obs:
            rows.append(f"{cid}:FULL{pred}RULED{obs}")
    for k in h:
        tot[k] += h[k]
    tot["n"] += n
    print(f"  {cfg:<15} coupling {h['coupl']}/{n}  all-b_pos {h['bpos']}/{n}  all-q0 {h['q0']}/{n}"
          + (f"   mismatch: {' '.join(rows)}" if rows else ""))
print(f"  POOLED          coupling {tot['coupl']}/{tot['n']}  all-b_pos {tot['bpos']}/{tot['n']}  all-q0 {tot['q0']}/{tot['n']}")

print("\n=== (b2) coupling with selection/held-out split: select on A cells, evaluate on B+C+D ===")
for cfg in CONFIGS:
    def agree(cells):
        a = t = 0
        for cid in cells:
            mf = PC.get(f"{cfg}|{cid}|FULL")
            mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
            if not mf or not mr or mf["modal"] is None or mr["modal"] is None:
                continue
            t += 1
            a += mf["modal"] == mr["modal"]
        return a, t
    fa, ft = agree([c for c in ALLCELLS if c[0] == "A"])
    ha, ht = agree([c for c in ALLCELLS if c[0] != "A"])
    print(f"  {cfg:<15} A-cells {fa}/{ft}   held-out B/C/D {ha}/{ht}")

print("\n=== (b3) does coupling beat the binary-endpoint model on delta=0 RULED? ===")
for cfg in CONFIGS:
    h = Counter(); n = 0
    for cid in ALLCELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL")
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not mf or not mr or mf["modal"] is None or mr["modal"] is None:
            continue
        obs = mr["modal"]
        lp, lq0 = L[cid]["l_pos"], L[cid]["l_q0"]
        n += 1
        h["coupl"] += mf["modal"] == obs
        h["endpoint"] += (lp if cls[cfg] == "blind" else lq0) == obs
    print(f"  {cfg:<15} coupling {h['coupl']}/{n}   endpoint({cls[cfg]}) {h['endpoint']}/{n}")
