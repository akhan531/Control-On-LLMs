"""Build tidy per-draw and per-cell tables from both arms. Writes scratch_fable/tidy.json."""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"

CELLS = {c["id"]: c for c in M.build()}
LEVELS = {cid: {
    "l_pos": M.level(c["b_pos"]),
    "l_q0": M.level(c[f"q_{M.DELTA_PRIMARY}"]),
    "l_q3": M.level(c[f"q_{M.DELTA_BANKED}"]),
} for cid, c in CELLS.items()}


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def load(results, stimuli):
    res = json.load(open(f"{ROOT}/{results}"))
    stim = {s["id"]: s for s in json.load(open(f"{ROOT}/{stimuli}"))["stimuli"]}
    draws = []
    for r in res["records"]:
        if not r.get("ok"):
            continue
        s = stim[r["stimulus_id"]]
        lv = S.target_level(r["candidate"], r["confidence"], s["target_label"])
        draws.append({
            "config": r["config"], "cell": s["cell"], "condition": s["condition"],
            "mirror": r["stimulus_id"].rsplit("-", 1)[-1], "seed": r["seed"],
            "level": lv, "reasoning_tokens": r.get("reasoning_tokens"),
        })
    return draws


primary = load("results_v2/v2_results_live.json", "silence_v2_stimuli.json")
banked = load("results_v2/v2_results_live_banked.json", "silence_v2_stimuli_banked.json")

# per (config, cell, condition): modal level pooling mirrors+draws, n, unanimity
def cellify(draws):
    b = defaultdict(list)
    for d in draws:
        b[(d["config"], d["cell"], d["condition"])].append(d["level"])
    out = {}
    for k, v in b.items():
        out["|".join(k)] = {
            "modal": mode(v), "n": len(v),
            "unanimous": len(set(v)) == 1,
            "dist": dict(Counter(v)),
        }
    return out


tidy = {
    "levels": LEVELS,
    "cells_meta": {cid: {"p": float(c["p"]), "N": c["N"], "k": c["k"],
                         "b_pos": float(c["b_pos"]), "q0": float(c[f"q_{M.DELTA_PRIMARY}"]),
                         "q3": float(c[f"q_{M.DELTA_BANKED}"])}
                   for cid, c in CELLS.items()},
    "primary_cells": cellify(primary),
    "banked_cells": cellify(banked),
    "primary_draws": primary,
    "banked_draws": banked,
}
json.dump(tidy, open(f"{ROOT}/scratch_fable/tidy.json", "w"))
print(f"primary draws {len(primary)}, banked draws {len(banked)}")
print(f"primary cell-units {len(tidy['primary_cells'])}, banked {len(tidy['banked_cells'])}")

# sanity: reproduce gates for two known numbers
NONCONTROL = [c for c in CELLS if c[0] in "AB"]
for cfg, expect in (("sol-none", 0.542), ("glm", -0.071), ("sol-high", 0.958)):
    vals = []
    for cid in NONCONTROL:
        m = tidy["primary_cells"].get(f"{cfg}|{cid}|PARTIAL_RULED")
        if m and m["modal"] is not None:
            lp, lq = LEVELS[cid]["l_pos"], LEVELS[cid]["l_q0"]
            vals.append((m["modal"] - lp) / (lq - lp))
    print(cfg, "mean s RULED:", round(sum(vals) / len(vals), 3), "expect ~", expect)
