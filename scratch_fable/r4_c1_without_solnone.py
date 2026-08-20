"""Item 4a: Candidate 1 with sol-none classified interior (excluded from the binary claim).
Six remaining configs, banked-arm prediction, baselines, exact permutation over 64."""
import json
from collections import Counter

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
BC = T["banked_cells"]
SIX = ["sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
FIT = {"sol-high": "aware", "deepseek": "blind", "deepseek-high": "aware",
       "glm": "blind", "glm-high": "aware", "anchor": "blind"}
BANKED_CELLS = sorted({k.split("|")[1] for k in BC})

def hits(assign, cfgs):
    h = n = 0
    for cfg in cfgs:
        for cid in BANKED_CELLS:
            m = BC.get(f"{cfg}|{cid}|PARTIAL_RULED_D30")
            if not m or m["modal"] is None:
                continue
            n += 1
            pred = L[cid]["l_pos"] if assign[cfg] == "blind" else L[cid]["l_q3"]
            h += pred == m["modal"]
    return h, n

obs, n = hits(FIT, SIX)
hb = sum(L[k.split('|')[1]]["l_pos"] == v["modal"] for k, v in BC.items()
         if k.split('|')[0] in SIX and v["modal"] is not None)
hq = sum(L[k.split('|')[1]]["l_q3"] == v["modal"] for k, v in BC.items()
         if k.split('|')[0] in SIX and v["modal"] is not None)
print(f"six configs (sol-none excluded): model {obs}/{n}   all-b_pos {hb}/{n}   all-q3 {hq}/{n}")

all_h = []
for mask in range(64):
    a = {cfg: ("aware" if (mask >> i) & 1 else "blind") for i, cfg in enumerate(SIX)}
    all_h.append(hits(a, SIX)[0])
all_h.sort(reverse=True)
ge = sum(1 for h in all_h if h >= obs)
print(f"permutation over 64 assignments: {ge} >= observed (p = {ge}/64 = {ge/64:.4f}); "
      f"max {all_h[0]}, median {all_h[32]}")

print("\nsol-none reported separately (the graded exception):")
for cid in BANKED_CELLS:
    m = BC.get(f"sol-none|{cid}|PARTIAL_RULED_D30")
    print(f"  {cid}: obs {m['modal']} dist {m['dist']}  l_pos {L[cid]['l_pos']} l_q0 {L[cid]['l_q0']} l_q3 {L[cid]['l_q3']}")
