"""Item 1: reconcile sol-none FULL (0.833) vs RULED (0.542) against my coupling claim.
Side-by-side per-cell modal levels + draw distributions, all 14 cells."""
import json

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L = T["levels"]
PC = T["primary_cells"]
CELLS = ["A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3", "B1", "B2", "B3", "D1", "D2", "D3"]
NONCONTROL = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3"]

print(f"{'cell':<5}{'l_pos':>6}{'l_q0':>6} | {'FULL':>5} {'dist':<16}{'s_F':>7} | "
      f"{'RULED':>5} {'dist':<16}{'s_R':>7} | agree  direction")
sf_vals, sr_vals = [], []
for cid in CELLS:
    mf = PC.get(f"sol-none|{cid}|FULL", {})
    mr = PC.get(f"sol-none|{cid}|PARTIAL_RULED", {})
    lp, lq = L[cid]["l_pos"], L[cid]["l_q0"]
    def s(m):
        return None if m.get("modal") is None else (m["modal"] - lp) / (lq - lp)
    sf, sr = s(mf), s(mr)
    if cid in NONCONTROL:
        if sf is not None:
            sf_vals.append(sf)
        if sr is not None:
            sr_vals.append(sr)
    agree = "==" if mf.get("modal") == mr.get("modal") and mf.get("modal") is not None else "!="
    direction = ""
    if mf.get("modal") is not None and mr.get("modal") is not None and mf["modal"] != mr["modal"]:
        direction = "FULL closer to q" if abs(mf["modal"] - lq) < abs(mr["modal"] - lq) else "RULED closer to q"
    print(f"{cid:<5}{lp:>6}{lq:>6} | {str(mf.get('modal')):>5} {str(mf.get('dist')):<16}"
          f"{('' if sf is None else f'{sf:.2f}'):>7} | {str(mr.get('modal')):>5} "
          f"{str(mr.get('dist')):<16}{('' if sr is None else f'{sr:.2f}'):>7} | {agree:^6} {direction}")

print(f"\nnon-control mean s: FULL {sum(sf_vals)/len(sf_vals):.3f} (n={len(sf_vals)})"
      f"   RULED {sum(sr_vals)/len(sr_vals):.3f} (n={len(sr_vals)})")
print("v2_gates.json says FULL B3 = null; recheck B3 FULL draws by mirror:")
from collections import Counter, defaultdict
b = defaultdict(list)
for d in T["primary_draws"]:
    if d["config"] == "sol-none" and d["cell"] == "B3" and d["condition"] == "FULL":
        b[d["mirror"]].append(d["level"])
for m, v in sorted(b.items()):
    print(f"  mirror {m}: {sorted(v)}")
print(f"  pooled: {dict(Counter(sum(b.values(), [])))}")
