"""(a) exact test: pooled banked hits for all 128 label assignments; rank of fitted one.
(b) viability of new delta values per cell under measured bands (for REQUIRES NEW DATA item)."""
import json
import sys
from collections import Counter
from fractions import Fraction as F

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC, BC = T["primary_cells"], T["banked_cells"]
CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
BANKED_CELLS = sorted({k.split("|")[1] for k in BC})

FITTED = {"sol-none": "aware", "sol-high": "aware", "deepseek": "blind",
          "deepseek-high": "aware", "glm": "blind", "glm-high": "aware", "anchor": "blind"}

def hits(assign):
    h = 0
    for cfg in CONFIGS:
        for cid in BANKED_CELLS:
            m = BC.get(f"{cfg}|{cid}|PARTIAL_RULED_D30")
            if not m or m["modal"] is None:
                continue
            pred = L[cid]["l_pos"] if assign[cfg] == "blind" else L[cid]["l_q3"]
            h += pred == m["modal"]
    return h

obs = hits(FITTED)
all_h = []
for mask in range(128):
    a = {cfg: ("aware" if (mask >> i) & 1 else "blind") for i, cfg in enumerate(CONFIGS)}
    all_h.append(hits(a))
all_h.sort(reverse=True)
ge = sum(1 for h in all_h if h >= obs)
print(f"fitted assignment hits {obs}/60; rank among 128 assignments: {ge} assignments >= it "
      f"(p = {ge}/128 = {ge/128:.4f}); max possible {all_h[0]}, median {all_h[64]}")

print("\n=== (b) delta-sweep viability: q(delta) level under measured bands, alt edges ===")
print("cell: level(q(d)) for d in 0.1,0.2,0.3,0.4,0.5 [x = dead zone or edge-unstable]")
for c in M.build():
    row = f"  {c['id']:<4} l_pos={M.level(c['b_pos'])} l_q0={M.level(c[f'q_{F(0)}'])}  "
    for dn in (1, 2, 3, 4, 5):
        d = F(dn, 10)
        qq = M.q(c["p"], c["N"], c["k"], d)
        band = M.in_band(qq)
        stable = M.level(qq) == M.level(qq, M.ALT_EDGES)
        row += f" d.{dn}:{'x' if band is None or not stable else band}"
    print(row + f"   (q values: " + " ".join(f"{float(M.q(c['p'], c['N'], c['k'], F(dn,10))):.2f}" for dn in (1, 2, 3, 4, 5)) + ")")
