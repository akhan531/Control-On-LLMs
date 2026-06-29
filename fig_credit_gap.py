#!/usr/bin/env python3
"""Credit-gap figure + go/no-go read for Task 1.0a."""
import json, os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results_8b_16seed"))
data = json.loads((RESULTS_DIR / "task_1_0_results.json").read_text())

ARMS = ["honest", "withhold", "never"]
COLORS = {"honest": "#1976D2", "withhold": "#E53935", "never": "#757575"}
n_agents = data["meta"]["n_agents"]
uniform = 1.0 / n_agents

points, dropped = {}, {}
for arm in ARMS:
    runs = data["runs"][arm]
    vals = [r["credit"]["expert"] for r in runs if r.get("credit_judge_ok", True)]
    points[arm] = np.array(vals, dtype=float)
    dropped[arm] = len(runs) - len(vals)

def stats(a):
    n = len(a)
    m = float(a.mean()) if n else float("nan")
    sem = float(a.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return m, sem, n

fig, ax = plt.subplots(figsize=(7, 5))
rng = np.random.default_rng(0)
for i, arm in enumerate(ARMS):
    a = points[arm]
    x = np.full(len(a), i) + rng.uniform(-0.08, 0.08, len(a))
    ax.scatter(x, a, color=COLORS[arm], alpha=0.55, s=40, zorder=3)
    m, sem, n = stats(a)
    ax.errorbar(i, m, yerr=(sem if sem == sem else 0), fmt="D",
                color=COLORS[arm], markersize=10, capsize=6,
                markeredgecolor="black", zorder=4)
    ax.annotate(f"{m:.3f}", (i, m), xytext=(12, 0),
                textcoords="offset points", va="center",
                fontsize=11, fontweight="bold")

ax.axhline(uniform, color="black", linestyle=":", linewidth=1.4,
           label=f"uniform 1/N = {uniform:.2f}")
ax.set_xticks(range(len(ARMS)))
ax.set_xticklabels(ARMS, fontsize=12)
ax.set_ylabel("Expert credit share", fontsize=12)
ax.set_ylim(0, 1)
ax.set_title("Expert credit by arm  [deletion_v1, 8B]", fontsize=13)
ax.legend(fontsize=10)
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout()
out = RESULTS_DIR / "task_1_0_credit_gap.png"
fig.savefig(out, dpi=150)
print(f"Saved credit-gap figure -> {out}")

mh, sh, nh = stats(points["honest"])
mw, sw, nw = stats(points["withhold"])
mn, sn, nn = stats(points["never"])
print("\n================ CREDIT READ ================")
for arm, (m, s, n) in [("honest",(mh,sh,nh)),("withhold",(mw,sw,nw)),("never",(mn,sn,nn))]:
    print(f"  {arm:9s} mean={m:.3f}  sem={s:.3f}  n={n}  (dropped {dropped[arm]})")
gap = mw - mh
print(f"\n  gap (withhold - honest) = {gap:+.3f}")
print(f"  (a)  withhold > honest         : {'PASS' if mw > mh else 'FAIL'}")
print(f"  (a') bands clear of crossover  : {'PASS' if (mw-sw) > (mh+sh) else 'overlap/FAIL'}")

vw = data["summary"]["withhold"]["V_by_round_mean"]
K = data["meta"]["disclosure_rounds"]["withhold"]
R = data["meta"]["n_rounds"]
plateau = float(np.mean(vw[:K-1])) if K > 1 else float("nan")
v_final = float(vw[-1]); drop = plateau - v_final
print("\n========= TRAJECTORY READ (withhold) =========")
print(f"  V(t) by round: {[round(x,3) for x in vw]}")
print(f"  disclosure at K={K} of R={R}")
print(f"  plateau mean (rounds 1..{K-1}) = {plateau:.3f}")
print(f"  V final (round {R})            = {v_final:.3f}")
print(f"  plateau-then-drop magnitude    = {drop:+.3f}")
print(f"  (b)  plateau-then-drop present : {'PASS' if drop > 0.20 else 'weak/FAIL'}  (heuristic: drop > 0.20)")
print("\nNOTE: heuristic reads — eyeball both figures before logging the verdict.")
print("Holds at 8B = BOTH (a) and (b). Inverted/null credit -> OpenRouter-70B fallback.")
