"""P5 count-control failure details; unanimity as predictor of correctness (fit d0, test d30);
reasoning tokens by config x condition."""
import json
from collections import Counter, defaultdict

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC, BC = T["primary_cells"], T["banked_cells"]
CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]

print("=== P5 detail: modal answers across k within count-control groups ===")
for cfg in CONFIGS:
    for grp, ids in (("C", ["C1", "C2", "C3"]), ("D", ["D1", "D2", "D3"])):
        for cond in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"):
            lv = [PC.get(f"{cfg}|{c}|{cond}", {}).get("modal") for c in ids]
            if len(set(lv)) > 1:
                print(f"  {cfg:<15} {grp}/{cond:<14} {lv}")

print("\n=== unanimity (all draws in a cell agree) by config, delta=0, per condition ===")
for cfg in CONFIGS:
    row = {}
    for cond in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"):
        u = t = 0
        for cid in L:
            m = PC.get(f"{cfg}|{cid}|{cond}")
            if m:
                t += 1
                u += m["unanimous"]
    # recompute per cond properly
    parts = []
    for cond in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"):
        u = sum(1 for cid in L if PC.get(f"{cfg}|{cid}|{cond}", {}).get("unanimous"))
        parts.append(f"{cond[:5]} {u}/14")
    ub = sum(1 for k, v in BC.items() if k.startswith(cfg + "|") and v["unanimous"])
    nb = sum(1 for k in BC if k.startswith(cfg + "|"))
    print(f"  {cfg:<15} " + "  ".join(parts) + f"   banked {ub}/{nb}")

print("\n=== does unanimity at a cell predict hitting the correct level? (both arms) ===")
print("  pooled over configs; correct = condition's target level")
TARGET = {"FULL": "l_q0", "PARTIAL_BLIND": "l_pos", "PARTIAL_RULED": "l_q0"}
for arm, cells, conds, tkey in (("d0", PC, ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"), None),
                                ("d30", BC, ("PARTIAL_RULED_D30",), "l_q3")):
    ct = Counter()
    for key, m in cells.items():
        cfg, cid, cond = key.split("|")
        if m["modal"] is None and not m["unanimous"]:
            pass
        tgt = L[cid][tkey] if tkey else L[cid][TARGET[cond]]
        correct = (m["modal"] == tgt) if m["modal"] is not None else False
        ct[("U" if m["unanimous"] else "S", "C" if correct else "W")] += 1
    for u in ("U", "S"):
        n = ct[(u, "C")] + ct[(u, "W")]
        acc = ct[(u, "C")] / n if n else 0
        print(f"  {arm}: {'unanimous' if u=='U' else 'split':<10} n={n:<4} accuracy={acc:.3f}")

print("\n=== reasoning tokens: mean per config x condition (delta=0), and banked ===")
agg = defaultdict(list)
for d in T["primary_draws"]:
    agg[(d["config"], d["condition"])].append(d["reasoning_tokens"] or 0)
for d in T["banked_draws"]:
    agg[(d["config"], "D30")].append(d["reasoning_tokens"] or 0)
print(f"  {'config':<15}{'FULL':>8}{'BLIND':>8}{'RULED':>8}{'D30':>8}")
for cfg in CONFIGS:
    row = ""
    for cond in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED", "D30"):
        v = agg.get((cfg, cond))
        row += f"{(sum(v)/len(v) if v else 0):>8.0f}"
    print(f"  {cfg:<15}{row}")

print("\n=== sol-none draw-level distributions in RULED (is level 1 a stable state or a mixture?) ===")
for cid in ("A1", "A2", "A3", "A4", "A5", "C2", "C3"):
    m = PC.get(f"sol-none|{cid}|PARTIAL_RULED")
    print(f"  {cid}: dist={m['dist']} unanimous={m['unanimous']}")
print("  FULL for comparison:")
for cid in ("A1", "A2", "A3", "A4", "A5"):
    m = PC.get(f"sol-none|{cid}|FULL")
    print(f"  {cid}: dist={m['dist']}")
print("  glm RULED (blind side):")
for cid in ("A1", "A2", "B1", "B2", "D1"):
    m = PC.get(f"glm|{cid}|PARTIAL_RULED")
    print(f"  {cid}: dist={m['dist']}")
