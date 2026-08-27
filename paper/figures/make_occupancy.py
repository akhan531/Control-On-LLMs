#!/usr/bin/env python
"""make_occupancy.py -- Figure 2b, COMPUTED from the draw records.

Panel (b) of the results figure: how much of each configuration's answer mass
lands exactly at the silence-blind level, under the printed-negatives condition
(FULL) versus the derivable-absences condition (RULED). The point is that
occupancy of the silence-blind belief RISES when the silence must be inferred:
it rises in four of the five admitted configurations and falls in none.

Population: all fourteen cells minus the P4 admission exclusions, delta = 0, the
five gated configurations. Occupancy = percent of usable draws whose level
equals that cell's silence-blind level.

The data ingest is copied from make_results.py so this script is self-contained.
Every number the figure touches is a live assertion below; a failed assertion is
a stop condition (the script raises rather than drawing a wrong figure).

Output, written to paper/figures/:
  results_occupancy.pdf

Run from anywhere:  python paper/figures/make_occupancy.py
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "paper" / "figures"
sys.path.insert(0, str(ROOT))
import silence_v2_stimuli as S  # noqa: E402  (target_level lives with the stimuli)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

plt.rcParams.update({
    "font.size": 10,
    "font.family": "sans-serif",
    "axes.linewidth": 0.6,
    "pdf.fonttype": 42,
})
# Placed at 0.48\textwidth beside panel (a); fonts sized so nothing falls below
# 7pt after the shrink, matching make_results.py.
FS_MIN, FS_LAB = 10.5, 11

# --------------------------------------------------------------------------
# constants -- shared with make_results.py (same order and abbreviations, A2)
# --------------------------------------------------------------------------
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
ROW_ORDER = ("sol-high", "sol-none", "glm-high", "deepseek-high", "glm")
ABBR = {"sol-high": "sol-hi", "sol-none": "sol-no", "glm-high": "glm-hi",
        "deepseek-high": "dsk-hi", "glm": "glm"}
CELLS14 = ("A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3",
           "B1", "B2", "B3", "D1", "D2", "D3")

SEG_ORDER = ("beyond", "at_bpos", "interior", "at_past")
CLASS_SEG = {"BEY": "beyond", "POS": "at_bpos", "INT": "interior",
             "COR": "at_past", "OVER": "at_past"}


def resolve(rel):
    p = ROOT / rel
    if not p.exists():
        sys.exit(f"ERROR: required input not found: {p}")
    return p


def check(cond, msg):
    if not cond:
        raise AssertionError(f"assertion failed: {msg}")


def klass(lv, lc, lp):
    if lv < lc:
        return "OVER"
    if lv == lc:
        return "COR"
    if lv < lp:
        return "INT"
    if lv == lp:
        return "POS"
    return "BEY"


def seg_counts(rows):
    out = Counter()
    for lv, lc, lp in rows:
        out[CLASS_SEG[klass(lv, lc, lp)]] += 1
    return out


def seg_pct(rows):
    n = len(rows)
    sc = seg_counts(rows)
    return {s: (round(100 * sc.get(s, 0) / n, 1) if n else 0.0) for s in SEG_ORDER}, n


# --------------------------------------------------------------------------
# data ingest -- copied from make_results.py, self-contained, relative paths
# --------------------------------------------------------------------------
def ingest(res_rel, stim_rel, cond_map, p4, draws, usable, attempted, fails):
    res = json.load(open(resolve(res_rel)))
    stim = {s["id"]: s for s in json.load(open(resolve(stim_rel)))["stimuli"]}
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        rung = cond_map.get(st["condition"])
        if rung is None:
            continue
        cfg, cell = r["config"], st["cell"]
        if cell in p4.get(cfg, []):
            continue
        attempted[(cfg, rung, cell)] += 1
        if not r.get("ok"):
            fails[(cfg, rung, cell)] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(cfg, rung, cell)].append((lv, st["level_target"], st["l_pos_target"]))
        usable[(cfg, rung, cell)] += 1


def load():
    p4 = json.load(open(resolve("results_v2/v2_gates.json")))["P4_excluded"]
    draws = defaultdict(list)
    usable, attempted, fails = Counter(), Counter(), Counter()
    ingest("results_v2/v2_results_live.json", "silence_v2_stimuli.json",
           {"PARTIAL_RULED": "RULED", "FULL": "FULL"}, p4, draws, usable, attempted, fails)
    return draws, usable, attempted, fails


def rung_draws(draws, cfg, rung, cells=CELLS14):
    return [x for c in cells for x in draws.get((cfg, rung, c), [])]


def occupancy(draws, cfg, rung):
    """Percent of usable draws landing exactly at the silence-blind level."""
    return seg_pct(rung_draws(draws, cfg, rung))[0]["at_bpos"]


# --------------------------------------------------------------------------
# ASSERTIONS -- every number the figure shows stays live
# --------------------------------------------------------------------------
EXPECT_FULL = {"sol-none": 0.0, "sol-high": 0.0, "deepseek-high": 12.4,
               "glm": 6.4, "glm-high": 0.7}
EXPECT_RULED = {"sol-none": 4.6, "sol-high": 0.0, "deepseek-high": 30.6,
                "glm": 77.1, "glm-high": 6.4}


def run_assertions(draws):
    rises = falls = 0
    for cfg in GATED:
        f = occupancy(draws, cfg, "FULL")
        r = occupancy(draws, cfg, "RULED")
        check(f == EXPECT_FULL[cfg], f"{cfg} FULL occupancy {EXPECT_FULL[cfg]} (got {f})")
        check(r == EXPECT_RULED[cfg], f"{cfg} RULED occupancy {EXPECT_RULED[cfg]} (got {r})")
        if r > f:
            rises += 1
        elif r < f:
            falls += 1
    check(rises == 4, f"expected occupancy to rise in 4 configs (got {rises})")
    check(falls == 0, f"expected occupancy to fall in 0 configs (got {falls})")
    print("All occupancy assertions passed.")


# --------------------------------------------------------------------------
# DRAW -- the dumbbell: FULL (open) -> RULED (filled) per configuration
# --------------------------------------------------------------------------
def draw(draws):
    fig, ax = plt.subplots(figsize=(3.2, 2.85))
    ax.set_axisbelow(True)
    ys = [-i for i in range(len(ROW_ORDER))]
    # subtle alternating row bands so each dumbbell is seated in its row
    for i, y in enumerate(ys):
        if i % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="0.955", zorder=0)
    for i, cfg in enumerate(ROW_ORDER):
        y = ys[i]
        f = occupancy(draws, cfg, "FULL")
        r = occupancy(draws, cfg, "RULED")
        ax.plot([f, r], [y, y], color="0.55", lw=1.3, zorder=1, solid_capstyle="round")
        ax.plot(f, y, marker="o", ms=6.5, mfc="white", mec="black", mew=1.0, zorder=2)
        ax.plot(r, y, marker="o", ms=6.5, mfc="black", mec="black", zorder=3)
        # value labels: FULL to the left of the open dot, RULED to the right of
        # the filled dot; collapse to one label when the two coincide.
        if abs(r - f) < 0.05:
            ax.text(r + 2.2, y, f"{r:.1f}", ha="left", va="center", fontsize=FS_MIN - 2)
        else:
            ax.text(f - 2.2, y, f"{f:.1f}", ha="right", va="center",
                    fontsize=FS_MIN - 2, color="0.4")
            ax.text(r + 2.2, y, f"{r:.1f}", ha="left", va="center", fontsize=FS_MIN - 2)

    ax.set_yticks(ys)
    ax.set_yticklabels([ABBR[c] for c in ROW_ORDER], fontsize=FS_MIN)
    ax.set_ylim(-(len(ROW_ORDER) - 1) - 0.7, 0.7)
    ax.set_xlim(-13, 104)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(axis="x", color="0.86", linewidth=0.6, zorder=0)
    ax.set_xlabel("silence-blind level occupancy (%)", fontsize=FS_LAB)
    ax.tick_params(labelsize=FS_MIN)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)

    handles = [
        Line2D([0], [0], marker="o", color="0.55", mfc="white", mec="black",
               mew=1.0, ms=6.5, lw=1.3, label="FULL (printed negatives)"),
        Line2D([0], [0], marker="o", color="0.55", mfc="black", mec="black",
               lw=1.3, ms=6.5, label="RULED (derivable absences)"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.20),
              ncol=1, fontsize=FS_MIN - 1, frameon=False, handlelength=1.6,
              handletextpad=0.5, borderaxespad=0.2)

    fig.savefig(FIGDIR / "results_occupancy.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    draws, usable, attempted, fails = load()
    run_assertions(draws)
    draw(draws)
    print("\nWrote:\n  paper/figures/results_occupancy.pdf")


if __name__ == "__main__":
    main()
