"""Audit reconciliation pass. Every number here is recomputed from raw files.
(a) 60 vs 620 denominators   (b) ARITH tie-loss count   (c) 623/630 reconciliation
(d) sol-none 4/7 vs 6/7 inclusion rules   (e) token-mean conventions, matched cells
Plus: frozen-channel emptiness as a descriptive count over ALL configs;
sol-none paired extreme-commitment test (McNemar exact + Fisher);
competence-confound check: FULL s vs RULED s per config, the off-diagonal residual.
"""
import json
import sys
from collections import Counter, defaultdict
from math import comb
from statistics import mean

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
L, PC, BC = T["levels"], T["primary_cells"], T["banked_cells"]
CONFIGS = ["sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor"]
BANKED_CELLS = sorted({k.split("|")[1] for k in BC})

print("=== (a) banked-arm denominators ===")
raw = json.load(open(f"{ROOT}/results_v2/v2_results_live_banked.json"))
fail = Counter((r["config"], r.get("failure")) for r in raw["records"] if not r.get("ok"))
print(f"  draws: {raw['n_records']} total = 9 cells x 2 mirrors x 5 draws x 7 configs; "
      f"usable {raw['n_ok']}; failures {dict(fail)}")
slots = 7 * 9
ties = [(k, v["dist"]) for k, v in BC.items() if v["modal"] is None]
print(f"  cell-units: {slots} slots; modal ties: {len(ties)} -> usable modal cells {slots - len(ties)}")
for k, d in ties:
    print(f"    tie: {k}  dist {d}")

print("\n=== (b)(c) ARITH_D30 denominators ===")
ra = json.load(open(f"{ROOT}/scratch_fable/results_arith/arith_results_live.json"))
fa = Counter((r["config"], r.get("failure")) for r in ra["records"] if not r.get("ok"))
print(f"  draws: {ra['n_records']}; usable {ra['n_ok']}; failures {dict(fa)}  "
      f"({ra['n_records']} - {sum(fa.values())} = {ra['n_records'] - sum(fa.values())})")
# rebuild arith cells
stim_a = {s["id"]: s for s in json.load(open(f"{ROOT}/scratch_fable/arith_d30_stimuli.json"))["stimuli"]}
b = defaultdict(list)
for r in ra["records"]:
    if r.get("ok"):
        s = stim_a[r["stimulus_id"]]
        b[(r["config"], s["cell"])].append(
            S.target_level(r["candidate"], r["confidence"], s["target_label"]))
def mode(v):
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]
la = {k: mode(v) for k, v in b.items()}
na = {k: len(v) for k, v in b.items()}
aties = [(k, dict(Counter(b[k]))) for k in b if la[k] is None]
print(f"  ARITH modal ties: {len(aties)} (correct count for the paper)")
for k, d in aties:
    print(f"    tie: {k}  n={na[k]}  dist {d}")
per_cfg = {cfg: sum(1 for c in BANKED_CELLS if la.get((cfg, c)) is not None) for cfg in CONFIGS}
print(f"  usable ARITH modal cells per config: {per_cfg}  total {sum(per_cfg.values())}/63")

print("\n=== (d) sol-none inclusion rules ===")
Lq3 = {c: L[c]["l_q3"] for c in BANKED_CELLS}
u = [c for c in BANKED_CELLS if la.get(("sol-none", c)) is not None]
gate = sum(1 for c in u if la[("sol-none", c)] == Lq3[c])
both = [c for c in u if BC.get(f"sol-none|{c}|PARTIAL_RULED_D30", {}).get("modal") is not None]
coup = sum(1 for c in both
           if la[("sol-none", c)] == BC[f"sol-none|{c}|PARTIAL_RULED_D30"]["modal"])
print(f"  gate 'correct at q(.3)': {gate}/{len(u)} over cells with usable ARITH modal: {u}")
print(f"  coupling 'ARITH == RULED_D30': {coup}/{len(both)} over cells with BOTH modals: {both}")

print("\n=== (e) token means, one convention, matched cells ===")
tok = defaultdict(list)
for d in T["primary_draws"]:
    tok[(d["config"], d["cell"], d["condition"])].append(d["reasoning_tokens"] or 0)
for d in T["banked_draws"]:
    tok[(d["config"], d["cell"], "D30")].append(d["reasoning_tokens"] or 0)
for cfg in ("sol-high", "deepseek-high", "glm-high"):
    # cell-weighted means on the SAME 9 banked-viable cells, all four conditions
    def cm(cond, cells):
        return mean(mean(tok[(cfg, c, cond)]) for c in cells if tok.get((cfg, c, cond)))
    m9 = {cond: cm(cond, BANKED_CELLS) for cond in ("PARTIAL_BLIND", "FULL", "PARTIAL_RULED", "D30")}
    m14 = {cond: cm(cond, list(L.keys())) for cond in ("PARTIAL_BLIND", "FULL", "PARTIAL_RULED")}
    print(f"  {cfg:<15} 9-cell matched: BLIND {m9['PARTIAL_BLIND']:.0f}  FULL {m9['FULL']:.0f}"
          f"  RULED {m9['PARTIAL_RULED']:.0f}  D30 {m9['D30']:.0f}   (14-cell FULL {m14['FULL']:.0f})")

print("\n=== frozen-channel emptiness, ALL configs, descriptive ===")
hits = [(k, v["modal"]) for k, v in BC.items()
        if v["modal"] is not None and v["modal"] == L[k.split("|")[1]]["l_q0"]]
print(f"  banked cells with modal == level(q(0)): {len(hits)}/{slots - len(ties)}")
for k, m in hits:
    print(f"    {k} -> {m}")
draw_hits = sum(1 for d in T["banked_draws"] if d["level"] == L[d["cell"]]["l_q0"])
print(f"  draw level: {draw_hits}/{len(T['banked_draws'])} draws at level(q(0))")

print("\n=== sol-none extreme-commitment, paired, delta=0 only ===")
ext_cells = [c for c in L if L[c]["l_q0"] in (0, 3)]
print(f"  cells whose correct RULED/FULL answer is an extreme level: {len(ext_cells)}")
disc_fr = disc_rf = conc = 0
rows = []
for c in ext_cells:
    f = PC.get(f"sol-none|{c}|FULL", {}).get("modal")
    r = PC.get(f"sol-none|{c}|PARTIAL_RULED", {}).get("modal")
    fe, re = f in (0, 3), r in (0, 3)
    rows.append(f"{c}:F{f}/R{r}")
    if fe and not re:
        disc_fr += 1
    elif re and not fe:
        disc_rf += 1
    else:
        conc += 1
print("  " + " ".join(rows))
n = disc_fr + disc_rf
p_mcnemar = sum(comb(n, i) for i in range(max(disc_fr, disc_rf), n + 1)) / 2 ** n * 2
print(f"  FULL-extreme-only {disc_fr}, RULED-extreme-only {disc_rf}, concordant {conc}")
print(f"  McNemar exact, two-sided: p = {min(p_mcnemar, 1):.4f}")
def fisher(a, b_, c, d):
    def hyp(a):
        return comb(a + b_, a) * comb(c + d, c) / comb(a + b_ + c + d, a + c)
    tot_ = 0.0
    obs = hyp(a)
    for x in range(0, min(a + b_, a + c) + 1):
        aa, bb, cc, dd = x, a + b_ - x, a + c - x, d - a + x
        if min(aa, bb, cc, dd) < 0:
            continue
        p = comb(aa + bb, aa) * comb(cc + dd, cc) / comb(aa + bb + cc + dd, aa + cc)
        if p <= obs + 1e-12:
            tot_ += p
    return tot_
fe_full = sum(1 for c in ext_cells if PC.get(f"sol-none|{c}|FULL", {}).get("modal") in (0, 3))
fe_rul = sum(1 for c in ext_cells if PC.get(f"sol-none|{c}|PARTIAL_RULED", {}).get("modal") in (0, 3))
ne = len(ext_cells)
print(f"  unpaired Fisher {fe_full}/{ne} vs {fe_rul}/{ne}: two-sided p = "
      f"{fisher(fe_full, ne - fe_full, fe_rul, ne - fe_rul):.4f}")
print(f"  note: at delta=0.30 the correct answer is level 2 (8 cells) or 1 (B1) --")
print(f"  never extreme -- so the d30 arms cannot test commitment to a correct extreme.")

print("\n=== competence-confound check: FULL s vs RULED s per config (non-control) ===")
NC = [c for c in L if c[0] in "AB"]
for cfg in CONFIGS:
    def ms(cond):
        v = []
        for c in NC:
            m = PC.get(f"{cfg}|{c}|{cond}", {}).get("modal")
            if m is None:
                continue
            lp, lq = L[c]["l_pos"], L[c]["l_q0"]
            v.append((m - lp) / (lq - lp))
        return sum(v) / len(v) if v else None
    f_, r_ = ms("FULL"), ms("PARTIAL_RULED")
    resid = None if None in (f_, r_) else r_ - f_
    print(f"  {cfg:<15} FULL {f_:+.3f}   RULED {r_:+.3f}   residual {resid:+.3f}")
