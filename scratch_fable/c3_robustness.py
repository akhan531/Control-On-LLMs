"""Robustness: (a) reverse fit d30 -> predict d0 RULED; (b) config-level label-transfer count;
(c) coupling excluding anchor + per-config discriminating cells; (d) token ordering across configs."""
import json
from collections import Counter

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC, BC = T["primary_cells"], T["banked_cells"]
CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
ALLCELLS = list(L.keys())
BANKED_CELLS = sorted({k.split("|")[1] for k in BC})

print("=== (a) REVERSE: classify on d30, predict d0 PARTIAL_RULED (14 cells) ===")
cls_rev = {}
for cfg in CONFIGS:
    votes = Counter()
    for cid in BANKED_CELLS:
        m = BC.get(f"{cfg}|{cid}|PARTIAL_RULED_D30")
        if not m or m["modal"] is None:
            continue
        lp, lq3 = L[cid]["l_pos"], L[cid]["l_q3"]
        d_p, d_q = abs(m["modal"] - lp), abs(m["modal"] - lq3)
        if d_p < d_q:
            votes["blind"] += 1
        elif d_q < d_p:
            votes["aware"] += 1
    cls_rev[cfg] = "aware" if votes["aware"] > votes["blind"] else "blind"
tot = Counter()
for cfg in CONFIGS:
    h = Counter(); n = 0
    for cid in ALLCELLS:
        m = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not m or m["modal"] is None:
            continue
        obs = m["modal"]
        lp, lq0 = L[cid]["l_pos"], L[cid]["l_q0"]
        n += 1
        h["model"] += (lp if cls_rev[cfg] == "blind" else lq0) == obs
        h["bpos"] += lp == obs
        h["q0"] += lq0 == obs
    for k in h:
        tot[k] += h[k]
    tot["n"] += n
    print(f"  {cfg:<15} [{cls_rev[cfg]:<5}] model {h['model']}/{n}  all-b_pos {h['bpos']}/{n}  all-q0 {h['q0']}/{n}")
print(f"  POOLED                  model {tot['model']}/{tot['n']}  all-b_pos {tot['bpos']}/{tot['n']}  all-q0 {tot['q0']}/{tot['n']}")

print("\n=== (b) label agreement between arms ===")
cls_fwd = {}
for cfg in CONFIGS:
    votes = Counter()
    for cid in ALLCELLS:
        m = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not m or m["modal"] is None:
            continue
        lp, lq = L[cid]["l_pos"], L[cid]["l_q0"]
        if abs(m["modal"] - lp) < abs(m["modal"] - lq):
            votes["blind"] += 1
        elif abs(m["modal"] - lq) < abs(m["modal"] - lp):
            votes["aware"] += 1
    cls_fwd[cfg] = "aware" if votes["aware"] > votes["blind"] else "blind"
agree = sum(cls_fwd[c] == cls_rev[c] for c in CONFIGS)
print(f"  labels agree {agree}/7: " + " ".join(f"{c}:{cls_fwd[c][0]}/{cls_rev[c][0]}" for c in CONFIGS))

print("\n=== (c) coupling excluding anchor ===")
pooled = Counter()
for cfg in CONFIGS:
    if cfg == "anchor":
        continue
    for cid in ALLCELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL")
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not mf or not mr or mf["modal"] is None or mr["modal"] is None:
            continue
        pooled["n"] += 1
        pooled["coupl"] += mf["modal"] == mr["modal"]
        pooled["bpos"] += L[cid]["l_pos"] == mr["modal"]
        pooled["q0"] += L[cid]["l_q0"] == mr["modal"]
print(f"  six main configs: coupling {pooled['coupl']}/{pooled['n']}  all-b_pos {pooled['bpos']}/{pooled['n']}  all-q0 {pooled['q0']}/{pooled['n']}")
pooled2 = Counter()
for cfg in ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm-high"]:
    for cid in ALLCELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL")
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not mf or not mr or mf["modal"] is None or mr["modal"] is None:
            continue
        pooled2["n"] += 1
        pooled2["coupl"] += mf["modal"] == mr["modal"]
print(f"  five coupled configs (excl glm, anchor): {pooled2['coupl']}/{pooled2['n']}")

print("\n=== (c2) discriminating cells: coupling right where b_pos wrong, per config ===")
for cfg in CONFIGS:
    disc = []
    for cid in ALLCELLS:
        mf = PC.get(f"{cfg}|{cid}|FULL")
        mr = PC.get(f"{cfg}|{cid}|PARTIAL_RULED")
        if not mf or not mr or mf["modal"] is None or mr["modal"] is None:
            continue
        if mf["modal"] == mr["modal"] != L[cid]["l_pos"]:
            disc.append(cid)
    print(f"  {cfg:<15} {len(disc)} cells where RULED=FULL != b_pos: {disc}")

print("\n=== (d) token cost ordering BLIND < FULL < RULED (d0) and RULED < D30, per reasoning config ===")
from collections import defaultdict
agg = defaultdict(list)
for d in T["primary_draws"]:
    agg[(d["config"], d["condition"])].append(d["reasoning_tokens"] or 0)
for d in T["banked_draws"]:
    agg[(d["config"], "D30")].append(d["reasoning_tokens"] or 0)
for cfg in ["sol-high", "deepseek-high", "glm-high"]:
    m = {c: sum(agg[(cfg, c)]) / len(agg[(cfg, c)]) for c in ("PARTIAL_BLIND", "FULL", "PARTIAL_RULED", "D30")}
    ok = m["PARTIAL_BLIND"] < m["FULL"] < m["PARTIAL_RULED"] < m["D30"]
    print(f"  {cfg:<15} BLIND {m['PARTIAL_BLIND']:.0f} < FULL {m['FULL']:.0f} < RULED {m['PARTIAL_RULED']:.0f} < D30 {m['D30']:.0f}  -> {ok}")
