"""Item 2: coupling on discriminating pairs only.
Discriminating (config, cell): FULL modal exists, RULED modal exists, and
FULL modal != level(b_pos) -- i.e. coupling and b_pos make different predictions."""
import json
from collections import Counter

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC = T["primary_cells"]
CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
CELLS = list(L.keys())

print(f"{'config':<15}{'disc':>5}{'coupling':>10}{'all-b_pos':>10}{'all-q0':>8}   mismatch direction on disc cells")
tot = Counter()
for cfg in CONFIGS:
    disc = []
    for cid in CELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL", {})
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED", {})
        if mf.get("modal") is None or mr.get("modal") is None:
            continue
        if mf["modal"] != L[cid]["l_pos"]:
            disc.append((cid, mf["modal"], mr["modal"]))
    n = len(disc)
    hits_c = sum(1 for _, f, r in disc if f == r)
    hits_b = sum(1 for cid, f, r in disc if L[cid]["l_pos"] == r)
    hits_q = sum(1 for cid, f, r in disc if L[cid]["l_q0"] == r)
    # direction of mismatches: RULED further from q than FULL (deficit) or closer (RULED better)
    dirs = Counter()
    for cid, f, r in disc:
        if f == r:
            continue
        lq = L[cid]["l_q0"]
        dirs["RULED_lags" if abs(r - lq) > abs(f - lq) else "RULED_ahead"] += 1
    tot["n"] += n; tot["c"] += hits_c; tot["b"] += hits_b; tot["q"] += hits_q
    print(f"{cfg:<15}{n:>5}{hits_c:>7}/{n:<3}{hits_b:>7}/{n:<3}{hits_q:>5}/{n:<3}   {dict(dirs)}")
print(f"{'POOLED':<15}{tot['n']:>5}{tot['c']:>7}/{tot['n']:<3}{tot['b']:>7}/{tot['n']:<3}{tot['q']:>5}/{tot['n']:<3}")

print("\npooled excluding glm and anchor (the two decouplers):")
tot2 = Counter()
for cfg in ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm-high"]:
    for cid in CELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL", {})
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED", {})
        if mf.get("modal") is None or mr.get("modal") is None or mf["modal"] == L[cid]["l_pos"]:
            continue
        tot2["n"] += 1
        tot2["c"] += mf["modal"] == mr["modal"]
        tot2["b"] += L[cid]["l_pos"] == mr["modal"]
        tot2["q"] += L[cid]["l_q0"] == mr["modal"]
print(f"  coupling {tot2['c']}/{tot2['n']}   all-b_pos {tot2['b']}/{tot2['n']}   all-q0 {tot2['q']}/{tot2['n']}")
