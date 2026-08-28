#!/usr/bin/env python
"""make_interior.py -- Figure 3b, COMPUTED from the draw records.

Interior mass (the fraction of usable draws strictly between the correct target
and the silence-blind belief), under the derivable-absences condition (RULED)
versus the enumerated one (ARITH). Deleting the identification step (RULED -> ARITH)
raises it: the mass freed off the silence-blind belief lands in the interior,
short of the target. It rises for all five admitted configurations, but only the
three with a genuine deficit carry the claim; the two ceiling configurations are
shown and set aside (their small increases carry no repair interpretation).

Population: cells minus the admission exclusions, delta = 0, EXCLUDING D1-D3.
D1-D3 are dropped for a structural reason, not a convenient one: there the target
and the silence-blind belief are one level apart, so no level lies between them
and interior mass is inexpressible (always 0). Including them would only dilute
the denominator.

Convention (shared with Figures 2b and 3a): filled marker = RULED, open = ARITH.

The data ingest is copied from make_results.py so this script is self-contained.

Output, written to paper/figures/:
  results_interior.pdf

Run from anywhere:  python paper/figures/make_interior.py
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "paper" / "figures"
sys.path.insert(0, str(ROOT))
import silence_v2_stimuli as S  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({
    "font.size": 10,
    "font.family": "sans-serif",
    "axes.linewidth": 0.6,
    "pdf.fonttype": 42,
})
FS_MIN, FS_LAB = 10.5, 11

ABBR = {"sol-high": "sol-hi", "sol-none": "sol-no", "glm-high": "glm-hi",
        "deepseek-high": "dsk-hi", "glm": "glm"}
# same population as make_results/make_residence, MINUS the D cells (interior is
# structurally inexpressible where target and b_pos are adjacent).
CELLS_NOND = ("A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3", "B1", "B2", "B3")
# rows grouped and ordered exactly as Figure 3a, so the two panels align by row
GROUPS = (
    ("non-ceiling", ("glm", "deepseek-high", "sol-none")),
    ("ceiling",     ("glm-high", "sol-high")),
)

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


def seg_pct(rows):
    n = len(rows)
    sc = Counter(CLASS_SEG[klass(lv, lc, lp)] for lv, lc, lp in rows)
    return {s: (round(100 * sc.get(s, 0) / n, 1) if n else 0.0) for s in SEG_ORDER}, n


def ingest(res_rel, stim_rel, cond_map, p4, draws):
    res = json.load(open(resolve(res_rel)))
    stim = {s["id"]: s for s in json.load(open(resolve(stim_rel)))["stimuli"]}
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        rung = cond_map.get(st["condition"])
        if rung is None:
            continue
        cfg, cell = r["config"], st["cell"]
        if cell in p4.get(cfg, []) or not r.get("ok"):
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(cfg, rung, cell)].append((lv, st["level_target"], st["l_pos_target"]))


def load():
    p4 = json.load(open(resolve("results_v2/v2_gates.json")))["P4_excluded"]
    draws = defaultdict(list)
    ingest("results_v2/v2_results_live.json", "silence_v2_stimuli.json",
           {"PARTIAL_RULED": "RULED"}, p4, draws)
    ingest("scratch_2_4c/example_2/results_arith_d0/arith_d0_results_live.json",
           "scratch_2_4c/example_2/arith_d0_stimuli.json",
           {"ARITH_D0": "ARITH"}, p4, draws)
    return draws


def rung_draws(draws, cfg, rung):
    return [x for c in CELLS_NOND for x in draws.get((cfg, rung, c), [])]


def interior(draws, cfg, rung):
    return seg_pct(rung_draws(draws, cfg, rung))[0]["interior"]


# --------------------------------------------------------------------------
# ASSERTIONS
# --------------------------------------------------------------------------
EXPECT_RULED = {"sol-none": 85.0, "deepseek-high": 36.5, "glm": 21.8,
                "sol-high": 14.5, "glm-high": 37.3}
EXPECT_ARITH = {"sol-none": 87.0, "deepseek-high": 54.1, "glm": 35.5,
                "sol-high": 20.0, "glm-high": 38.2}


def run_assertions(draws):
    for cfg in EXPECT_RULED:
        r = interior(draws, cfg, "RULED")
        a = interior(draws, cfg, "ARITH")
        check(r == EXPECT_RULED[cfg], f"{cfg} RULED interior {EXPECT_RULED[cfg]} (got {r})")
        check(a == EXPECT_ARITH[cfg], f"{cfg} ARITH interior {EXPECT_ARITH[cfg]} (got {a})")
        check(a > r, f"{cfg} interior should rise RULED->ARITH (all five do)")
    print("All interior assertions passed.")


# --------------------------------------------------------------------------
# DRAW -- dumbbell: RULED (filled) -> ARITH (open), grouped by the ceiling guard
# --------------------------------------------------------------------------
GAP_GROUP = 0.55


def draw(draws):
    order, ys = [], []
    y = 0.0
    group_spans = []
    for name, cfgs in GROUPS:
        top = y
        for cfg in cfgs:
            order.append(cfg)
            ys.append(y)
            y -= 1.0
        group_spans.append((name, top, len(cfgs)))
        y -= GAP_GROUP

    fig, ax = plt.subplots(figsize=(3.2, 2.9))
    ax.set_axisbelow(True)
    for i, yy in enumerate(ys):
        if i % 2 == 0:
            ax.axhspan(yy - 0.5, yy + 0.5, color="0.955", zorder=0)

    for cfg, yy in zip(order, ys):
        r = interior(draws, cfg, "RULED")
        a = interior(draws, cfg, "ARITH")
        ax.plot([r, a], [yy, yy], color="0.55", lw=1.3, zorder=1, solid_capstyle="round")
        ax.plot(a, yy, marker="o", ms=6.5, mfc="white", mec="black", mew=1.0, zorder=2)
        ax.plot(r, yy, marker="o", ms=6.5, mfc="black", mec="black", zorder=3)
        lo, hi = sorted((r, a))
        ax.text(lo - 2.4, yy, f"{lo:.1f}", ha="right", va="center",
                fontsize=FS_MIN - 2, color="0.4")
        ax.text(hi + 2.4, yy, f"{hi:.1f}", ha="left", va="center", fontsize=FS_MIN - 2)

    ax.set_yticks(ys)
    ax.set_yticklabels([ABBR[c] for c in order], fontsize=FS_MIN)
    ax.set_ylim(ys[-1] - 0.7, ys[0] + 0.7)
    ax.set_xlim(-13, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(axis="x", color="0.86", linewidth=0.6, zorder=0)
    ax.set_xlabel("interior mass (%)", fontsize=FS_LAB)
    ax.tick_params(labelsize=FS_MIN)
    ax.tick_params(axis="y", length=0)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)

    for name, top, nrow in group_spans:
        ymid = top - nrow / 2.0
        ax.annotate(name, xy=(-0.30, ymid), xycoords=("axes fraction", "data"),
                    ha="right", va="center", fontsize=FS_MIN - 1.5, color="0.35",
                    rotation=90)

    # Legend omitted: panel of Figure 3; convention is in the combined caption.
    fig.savefig(FIGDIR / "results_interior.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    draws = load()
    run_assertions(draws)
    draw(draws)
    print("\nWrote:\n  paper/figures/results_interior.pdf")


if __name__ == "__main__":
    main()
