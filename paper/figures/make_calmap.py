#!/usr/bin/env python
"""make_calmap.py -- the calibration confidence map for main.tex, COMPUTED from
the W1 pre-test draw records.

This figure carries real data. Nothing here is hand-placed. The per-config
switch pattern is a live assertion below; a failed assertion is a stop condition
(the script raises rather than drawing a wrong figure).

What it shows: for each configuration, the modal (candidate, confidence) answer
on the CAL sweep under wording B -- a stated probability, no inference. As the
stated probability moves away from even odds, every configuration flips from
"somewhat" to "very" confident. Six of seven flip at 0.20 and 0.80, symmetric
about 0.5; anchor carries an extra "very" cell at 0.30 (a 0.1 low-side offset).

Output, written to paper/figures/:
  confidence_map.pdf

Run from anywhere:  python paper/figures/make_calmap.py
No arguments. No absolute paths: every path is derived from __file__ relative to
the repo root. If an input is missing, the script fails naming the path it wanted.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "paper" / "figures"
sys.path.insert(0, str(ROOT / "stimuli"))
import w1_stimuli as W  # noqa: E402  (WORDINGS, LABELS, CAL_P_FIRST live with the stimuli)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle, Patch  # noqa: E402

plt.rcParams.update({
    "font.size": 10,
    "font.family": "sans-serif",
    "axes.linewidth": 0.6,
    "pdf.fonttype": 42,
})
FS_CELL, FS_TICK, FS_LAB = 8.5, 9.5, 10.5

# --------------------------------------------------------------------------
# constants -- sourced from w1_stimuli where possible
# --------------------------------------------------------------------------
LOW = W.WORDINGS["B"]["low"]     # "Somewhat confident"
HIGH = W.WORDINGS["B"]["high"]   # "Very confident"
FIRST, SECOND = W.LABELS         # ("SIGMA", "THETA")
PROBS = sorted(W.CAL_P_FIRST)    # [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]

# rows grouped by family so the high/regular pairing is adjacent
FAMILIES = (
    ("sol",      ("sol-none", "sol-high")),
    ("glm",      ("glm", "glm-high")),
    ("deepseek", ("deepseek", "deepseek-high")),
    ("llama",    ("anchor",)),
)
CONFIG_ORDER = tuple(c for _, cfgs in FAMILIES for c in cfgs)

# display alias: the draw records key on "anchor"; the paper shows "llama"
DISPLAY = {"anchor": "llama"}

# four categories: hue = candidate, lightness = confidence.
# diverging blue(THETA)<->red(SIGMA); dark = very, pale = somewhat.
CAT_COLOR = {
    (SECOND, HIGH): "#3b4cc0",   # very confident, THETA  (dark blue)
    (SECOND, LOW):  "#c9d5f2",   # somewhat,       THETA  (pale blue)
    (FIRST,  LOW):  "#f6c6ad",   # somewhat,       SIGMA  (pale red)
    (FIRST,  HIGH): "#b40426",   # very confident, SIGMA  (dark red)
}
DARK_CATS = {(SECOND, HIGH), (FIRST, HIGH)}   # white glyph on these


def resolve(rel):
    p = ROOT / rel
    if not p.exists():
        sys.exit(f"ERROR: required input not found: {p}")
    return p


def check(cond, msg):
    if not cond:
        raise AssertionError(f"calibration assertion failed: {msg}")


def mode(vals):
    if not vals:
        return None
    c = Counter(vals).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


# --------------------------------------------------------------------------
# data ingest -- CAL family, wording B, usable draws only
# --------------------------------------------------------------------------
def load():
    recs = json.load(open(resolve("results/calibration/w1_results_live.json")))["records"]
    stim = {s["id"]: s for s in json.load(open(resolve("stimuli/w1_stimuli.json")))["stimuli"]}
    bucket = defaultdict(list)
    for r in recs:
        if r.get("family") != "CAL" or r.get("wording") != "B" or not r.get("ok"):
            continue
        p = round(float(stim[r["stimulus_id"]]["p_first"]), 2)
        bucket[(r["config"], p)].append((r["candidate"], r["confidence"]))
    modal = {k: mode(v) for k, v in bucket.items()}
    n = {k: len(v) for k, v in bucket.items()}
    return modal, n


# --------------------------------------------------------------------------
# ASSERTIONS -- the switch pattern stays live
# --------------------------------------------------------------------------
def switch_edges(modal, cfg):
    """(low_edge, high_edge): outermost stated prob still answered 'very'."""
    high = min((p for p in PROBS if p >= 0.5 and modal[(cfg, p)][1] == HIGH), default=None)
    low = max((p for p in PROBS if p <= 0.5 and modal[(cfg, p)][1] == HIGH), default=None)
    return round(low, 2), round(high, 2)


def run_assertions(modal, n):
    # every config-by-probability cell has usable draws, at most three (one wording)
    for cfg in CONFIG_ORDER:
        for p in PROBS:
            check((cfg, p) in modal and modal[(cfg, p)] is not None,
                  f"{cfg} @ p={p}: no modal answer")
            check(1 <= n[(cfg, p)] <= 3, f"{cfg} @ p={p}: n={n.get((cfg, p))} out of [1,3]")

    # six of seven: very-confident iff |p-0.5| >= 0.3, candidate THETA below 0.5,
    # SIGMA above -> edges 0.20 and 0.80, symmetric.
    for cfg in CONFIG_ORDER:
        if cfg == "anchor":
            continue
        for p in PROBS:
            want_conf = HIGH if abs(p - 0.5) >= 0.3 else LOW
            want_cand = FIRST if p > 0.5 else SECOND
            check(modal[(cfg, p)] == (want_cand, want_conf),
                  f"{cfg} @ p={p}: {modal[(cfg, p)]} != {(want_cand, want_conf)}")
        check(switch_edges(modal, cfg) == (0.20, 0.80),
              f"{cfg} edges {switch_edges(modal, cfg)} != (0.20, 0.80)")

    # anchor: the exception. extra 'very' at 0.30 -> low edge 0.30, 0.1 asymmetry.
    check(modal[("anchor", 0.3)] == (SECOND, HIGH),
          f"anchor @ 0.30 expected extra very-THETA, got {modal[('anchor', 0.3)]}")
    check(switch_edges(modal, "anchor") == (0.30, 0.80),
          f"anchor edges {switch_edges(modal, 'anchor')} != (0.30, 0.80)")

    # exactly six configs land on the symmetric (0.20, 0.80) pattern
    symmetric = [c for c in CONFIG_ORDER if switch_edges(modal, c) == (0.20, 0.80)]
    check(len(symmetric) == 6, f"expected 6 symmetric configs, got {len(symmetric)}")
    print("All calibration assertions passed.")


# --------------------------------------------------------------------------
# DRAW -- the confidence map
# --------------------------------------------------------------------------
GAP_MID = 0.45     # visual gap between the two candidates, at p = 0.5
GAP_FAM = 0.42     # visual gap between family groups


def col_x(i):
    """x of column i (0..7); an extra gap opens at the 0.5 candidate flip."""
    return i + (GAP_MID if i >= 4 else 0.0)


def row_layout():
    """y (top of each cell), config for each row, and the family gaps applied."""
    ys, order, fam_spans = [], [], []
    y = 0.0
    for _, cfgs in FAMILIES:
        span_top = y
        for cfg in cfgs:
            ys.append(y)
            order.append(cfg)
            y -= 1.0
        fam_spans.append((span_top, y))     # (top, bottom-exclusive)
        y -= GAP_FAM
    return ys, order, fam_spans


def draw(modal, n):
    ys, order, fam_spans = row_layout()
    fig_w = 6.2
    fig_h = 3.35
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    for yj, cfg in zip(ys, order):
        for i, p in enumerate(PROBS):
            cand, conf = modal[(cfg, p)]
            x = col_x(i)
            is_anchor_exc = (cfg == "anchor" and p == 0.3)
            ax.add_patch(Rectangle(
                (x + 0.03, yj - 0.97), 0.94, 0.94,
                facecolor=CAT_COLOR[(cand, conf)],
                edgecolor="black" if is_anchor_exc else "0.85",
                linewidth=1.6 if is_anchor_exc else 0.5, zorder=2))
            glyph = "V" if conf == HIGH else "s"
            ax.text(x + 0.5, yj - 0.5, glyph, ha="center", va="center",
                    fontsize=FS_CELL, zorder=3,
                    color="white" if (cand, conf) in DARK_CATS else "0.15")

    # candidate-flip divider at p = 0.5
    xdiv = col_x(4) - GAP_MID / 2
    ax.axvline(xdiv, color="0.35", lw=0.8, ls=(0, (4, 2)), zorder=1)

    # switch-edge emphasis: boundaries between 0.20|0.30 and 0.70|0.80
    for bx in (col_x(2), col_x(6)):
        ax.axvline(bx, color="0.0", lw=1.5, zorder=4, ymin=0.02, ymax=0.88)

    # x ticks at the eight stated probabilities; 0.20 and 0.80 bolded
    ax.set_xticks([col_x(i) + 0.5 for i in range(len(PROBS))])
    labs = [f"{p:.2f}" for p in PROBS]
    ax.set_xticklabels(labs, fontsize=FS_TICK)
    for t, p in zip(ax.get_xticklabels(), PROBS):
        if p in (0.20, 0.80):
            t.set_fontweight("bold")
    ax.set_xlabel("stated probability of one candidate", fontsize=FS_LAB)

    # y ticks: config names (anchor shown as its paper alias, llama)
    ax.set_yticks([yj - 0.5 for yj in ys])
    ax.set_yticklabels([DISPLAY.get(c, c) for c in order], fontsize=FS_TICK)

    # family label in the far-left gutter, centred on each group's cells
    for (top, _), (famname, cfgs) in zip(fam_spans, FAMILIES):
        ymid = top - len(cfgs) / 2.0
        ax.annotate(famname, xy=(-0.225, ymid), xycoords=("axes fraction", "data"),
                    ha="right", va="center", fontsize=FS_TICK - 0.5, color="0.35",
                    rotation=90)

    # edge callouts
    ytop = ys[0] + 0.15
    ax.text(col_x(2), ytop + 0.35, "switch 0.20", ha="center", va="bottom",
            fontsize=FS_TICK - 1, color="0.15")
    ax.text(col_x(6), ytop + 0.35, "switch 0.80", ha="center", va="bottom",
            fontsize=FS_TICK - 1, color="0.15")

    ax.set_xlim(-0.15, col_x(len(PROBS) - 1) + 1.15)
    ax.set_ylim(ys[-1] - 1.15, ys[0] + 1.05)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)

    # legend: four categories
    handles = [
        Patch(facecolor=CAT_COLOR[(SECOND, HIGH)], edgecolor="0.6", label="very conf., $\\Theta$"),
        Patch(facecolor=CAT_COLOR[(SECOND, LOW)], edgecolor="0.6", label="somewhat, $\\Theta$"),
        Patch(facecolor=CAT_COLOR[(FIRST, LOW)], edgecolor="0.6", label="somewhat, $\\Sigma$"),
        Patch(facecolor=CAT_COLOR[(FIRST, HIGH)], edgecolor="0.6", label="very conf., $\\Sigma$"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=4, fontsize=FS_TICK - 1, frameon=False, handlelength=1.1,
              columnspacing=1.2, handletextpad=0.4)

    fig.savefig(FIGDIR / "confidence_map.pdf", format="pdf", bbox_inches="tight")
    import os
    if os.environ.get("CALMAP_PNG"):
        fig.savefig(os.environ["CALMAP_PNG"], format="png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    modal, n = load()
    run_assertions(modal, n)
    draw(modal, n)
    print("\nWrote:\n  paper/figures/confidence_map.pdf")


if __name__ == "__main__":
    main()
