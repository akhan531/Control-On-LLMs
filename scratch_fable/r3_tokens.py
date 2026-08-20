"""Item 3: falsification-test the reasoning-token ordering.

PREDICTION (stated before fitting, from the c3 result): within a reasoning-enabled
config, per-cell mean reasoning tokens satisfy BLIND < FULL < RULED at delta=0, and
RULED < RULED_D30 on the nine banked cells; and the FULL<RULED step is NOT explained
by prompt length, because RULED prompts are SHORTER than FULL prompts.

Fit/selection subset: deepseek-high, delta=0 arm.
Held-out: sol-high and glm-high (other families), and the D30 arm (all).
Baseline: prompt length (chars). If tokens track length, ordering should be
BLIND < RULED < FULL and D30 ~ RULED.
"""
import json
from collections import defaultdict
from statistics import mean

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
T = json.load(open(f"{ROOT}/scratch_fable/tidy.json"))
CELLS = list(T["levels"].keys())

stim_p = {s["id"]: s for s in json.load(open(f"{ROOT}/silence_v2_stimuli.json"))["stimuli"]}
stim_b = {s["id"]: s for s in json.load(open(f"{ROOT}/silence_v2_stimuli_banked.json"))["stimuli"]}

# prompt length per (cell, condition), averaged over mirrors
plen = defaultdict(list)
for s in list(stim_p.values()) + list(stim_b.values()):
    plen[(s["cell"], s["condition"])].append(len(s["prompt"]))
plen = {k: mean(v) for k, v in plen.items()}

# tokens per (config, cell, condition), mean over draws+mirrors
tok = defaultdict(list)
for d in T["primary_draws"] + T["banked_draws"]:
    tok[(d["config"], d["cell"], d["condition"])].append(d["reasoning_tokens"] or 0)
tok = {k: mean(v) for k, v in tok.items()}

print("=== prompt length baseline (chars, mean over mirrors) ===")
for cond in ("PARTIAL_BLIND", "PARTIAL_RULED", "FULL"):
    v = [plen[(c, cond)] for c in CELLS]
    print(f"  {cond:<15} mean {mean(v):.0f}  range {min(v):.0f}-{max(v):.0f}")
v = [plen[(c, "PARTIAL_RULED_D30")] for c in CELLS if (c, "PARTIAL_RULED_D30") in plen]
print(f"  {'RULED_D30':<15} mean {mean(v):.0f}  range {min(v):.0f}-{max(v):.0f}")
print("  -> length ordering is BLIND < RULED < RULED_D30(+1 sentence) << FULL")

REASONING = ["sol-high", "deepseek-high", "glm-high"]
BLIND_CFG = ["sol-none", "deepseek", "glm", "anchor"]

print("\n=== per-cell paired comparisons, delta=0 (14 cells each) ===")
print(f"{'config':<15}{'RULED>FULL':>11}{'FULL>BLIND':>11}{'RULED>BLIND':>12}   (cells, paired within cell)")
for cfg in REASONING + BLIND_CFG:
    a = sum(1 for c in CELLS if tok[(cfg, c, "PARTIAL_RULED")] > tok[(cfg, c, "FULL")])
    b = sum(1 for c in CELLS if tok[(cfg, c, "FULL")] > tok[(cfg, c, "PARTIAL_BLIND")])
    d = sum(1 for c in CELLS if tok[(cfg, c, "PARTIAL_RULED")] > tok[(cfg, c, "PARTIAL_BLIND")])
    print(f"{cfg:<15}{a:>8}/14{b:>8}/14{d:>9}/14")

print("\n=== held-out D30 arm: RULED_D30 > RULED per cell (9 banked cells) ===")
BANKED_CELLS = sorted({k[1] for k in tok if k[2] == "PARTIAL_RULED_D30"})
for cfg in REASONING + BLIND_CFG:
    a = sum(1 for c in BANKED_CELLS if tok[(cfg, c, "PARTIAL_RULED_D30")] > tok[(cfg, c, "PARTIAL_RULED")])
    r = mean([tok[(cfg, c, "PARTIAL_RULED_D30")] for c in BANKED_CELLS])
    r0 = mean([tok[(cfg, c, "PARTIAL_RULED")] for c in BANKED_CELLS])
    print(f"  {cfg:<15} {a}/9 cells   mean RULED {r0:.0f} -> D30 {r:.0f}"
          f"   (prompt is only ~{plen[(BANKED_CELLS[0], 'PARTIAL_RULED_D30')] - plen[(BANKED_CELLS[0], 'PARTIAL_RULED')]:.0f} chars longer)")

print("\n=== length-vs-load: correlation of mean tokens with prompt chars vs with N-k ===")
def pearson(x, y):
    mx, my = mean(x), mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    dx = sum((a - mx) ** 2 for a in x) ** 0.5
    dy = sum((b - my) ** 2 for b in y) ** 0.5
    return num / (dx * dy) if dx and dy else float("nan")

meta = T["cells_meta"]
for cfg in REASONING:
    # across the 42 (cell, condition) points at delta=0
    pts = [(c, cond) for c in CELLS for cond in ("PARTIAL_BLIND", "FULL", "PARTIAL_RULED")]
    x_len = [plen[p] for p in pts]
    y = [tok[(cfg, *p)] for p in pts]
    r_len = pearson(x_len, y)
    # within RULED only: tokens vs N-k (inferential load), and vs prompt chars
    x_nk = [meta[c]["N"] - meta[c]["k"] for c in CELLS]
    y_r = [tok[(cfg, c, "PARTIAL_RULED")] for c in CELLS]
    x_lenr = [plen[(c, "PARTIAL_RULED")] for c in CELLS]
    print(f"  {cfg:<15} r(tokens, prompt_chars) all-conds = {r_len:+.2f}   "
          f"within RULED: r(tokens, N-k) = {pearson(x_nk, y_r):+.2f}, r(tokens, chars) = {pearson(x_lenr, y_r):+.2f}")

print("\n=== FIT on deepseek-high d0: which orderings hold? then PREDICT held-out ===")
def orderings(cfg):
    bl = mean([tok[(cfg, c, "PARTIAL_BLIND")] for c in CELLS])
    fu = mean([tok[(cfg, c, "FULL")] for c in CELLS])
    ru = mean([tok[(cfg, c, "PARTIAL_RULED")] for c in CELLS])
    return bl, fu, ru
bl, fu, ru = orderings("deepseek-high")
print(f"  deepseek-high (fit): BLIND {bl:.0f} < FULL {fu:.0f} < RULED {ru:.0f} -> selected prediction: BLIND<FULL<RULED, and RULED>FULL despite shorter prompt")
for cfg in ["sol-high", "glm-high"]:
    bl, fu, ru = orderings(cfg)
    ok = bl < fu < ru
    print(f"  {cfg:<15} (held out): BLIND {bl:.0f}, FULL {fu:.0f}, RULED {ru:.0f} -> ordering {'HOLDS' if ok else 'FAILS'}")

print("\n=== does token spend on RULED predict silence-reading? (blind vs aware configs) ===")
for cfg in REASONING + BLIND_CFG:
    ru = mean([tok[(cfg, c, "PARTIAL_RULED")] for c in CELLS])
    print(f"  {cfg:<15} mean RULED reasoning tokens {ru:>6.0f}")
