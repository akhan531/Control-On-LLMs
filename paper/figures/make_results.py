#!/usr/bin/env python
"""make_results.py -- the results figure for main.tex, COMPUTED from the draw records.

This figure carries real data. Nothing here is hand-placed. Every Section 2
number the figure touches is a live assertion below; a failed assertion is a
stop condition (the script raises rather than drawing a wrong figure).

Outputs, written to paper/figures/:
  results_signed_error.pdf    panel (a): signed s2 on the D-cells, result vs control
  results_mass.pdf            panel (b) variant 1: four-way mass split
  results_abs_error.pdf       panel (b) variant 2: the s1 ladder
  results_geometry_check.txt  diagnostic (not a figure): mass split by distance class

Run from anywhere:  python paper/figures/make_results.py
No arguments. No absolute paths: every path is derived from __file__ relative to
the repo root. If an input is missing, the script fails naming the path it wanted.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "paper" / "figures"
sys.path.insert(0, str(ROOT / "stimuli"))
import silence_v2_stimuli as S  # noqa: E402  (target_level lives with the stimuli)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

plt.rcParams.update({
    "font.size": 10,
    "font.family": "sans-serif",
    "axes.linewidth": 0.6,
    "hatch.linewidth": 0.5,
    "pdf.fonttype": 42,
})
# Panels are placed at 0.48\textwidth = 0.48 * 5.5in = 2.64in, so a figure whose
# natural width is ~3.3in shrinks to ~0.8x on inclusion. Fonts are sized here so
# that after that shrink NOTHING falls below 7pt at final size (spec section 6).
# Minimum source font is 9.5pt -> ~7.1pt final at the ~0.75x worst case.
FS_MIN, FS_LAB, FS_AXIS = 10.5, 11, 11

# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
# panel (a) row order: ascending mean s1 on FULL, best-gated first (== G5 order)
ROW_ORDER = ("sol-high", "sol-none", "glm-high", "deepseek-high", "glm")
# lambda-ceiling configs, adjudicated out by the registered 0.15-bin guard
CEILING = ("sol-high", "glm-high")
NONCEIL = tuple(c for c in GATED if c not in CEILING)  # sol-none, deepseek-high, glm
ALL_ORDER = GATED + ("deepseek", "anchor")  # gated first, then the two excluded
# One abbreviation set used in BOTH panels (audit A2); keyed once in the caption.
ABBR = {"sol-high": "sol-hi", "sol-none": "sol-no", "glm-high": "glm-hi",
        "deepseek-high": "dsk-hi", "glm": "glm"}
DCELLS = ("D1", "D2", "D3")
CELLS14 = ("A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3",
           "B1", "B2", "B3", "D1", "D2", "D3")

# four mass-split segments, ordered LEFT -> RIGHT by distance from target
SEG_ORDER = ("beyond", "at_bpos", "interior", "at_past")
SEG_LABEL = {"beyond": "beyond $b_{\\mathrm{pos}}$", "at_bpos": "at $b_{\\mathrm{pos}}$",
             "interior": "interior", "at_past": "at or past target"}
# 5-class scheme -> 4 segments. BEY is its OWN segment (Ali item 1): do not fold.
CLASS_SEG = {"BEY": "beyond", "POS": "at_bpos", "INT": "interior",
             "COR": "at_past", "OVER": "at_past"}


def resolve(rel):
    p = ROOT / rel
    if not p.exists():
        sys.exit(f"ERROR: required input not found: {p}")
    return p


def check(cond, msg):
    """A failed Section 2 assertion stops the run rather than drawing a wrong figure."""
    if not cond:
        raise AssertionError(f"Section 2 assertion failed: {msg}")


def cell_dist(cell):
    """|level(b_pos) - l_cor| by cell family: D=1, B=2, A/C=3 (verified in recon)."""
    return {"A": 3, "C": 3, "B": 2, "D": 1}[cell[0]]


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


def mode(vals):
    if not vals:
        return None
    c = Counter(vals).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


# --------------------------------------------------------------------------
# data ingest -- mirror of s3_ladder_summary.ingest, self-contained, relative paths
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
        if cell in p4.get(cfg, []):        # P4 excludes whole cells for a config
            continue
        attempted[(cfg, rung, cell)] += 1
        if not r.get("ok"):
            fails[(cfg, rung, cell)] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(cfg, rung, cell)].append((lv, st["level_target"], st["l_pos_target"]))
        usable[(cfg, rung, cell)] += 1


def load():
    p4 = json.load(open(resolve("results/campaign/v2_gates.json")))["P4_excluded"]
    draws = defaultdict(list)
    usable, attempted, fails = Counter(), Counter(), Counter()
    # RULED and FULL rungs, delta=0 main campaign
    ingest("results/campaign/v2_results_live.json", "stimuli/silence_v2_stimuli.json",
           {"PARTIAL_RULED": "RULED", "FULL": "FULL"}, p4, draws, usable, attempted, fails)
    # ARITH rung, the enumerated-absences campaign
    ingest("results/arith/arith_d0_results_live.json",
           "stimuli/arith_d0_stimuli.json",
           {"ARITH_D0": "ARITH"}, p4, draws, usable, attempted, fails)
    return draws, usable, attempted, fails


# --------------------------------------------------------------------------
# aggregation helpers
# --------------------------------------------------------------------------
def rung_draws(draws, cfg, rung, cells=CELLS14):
    return [x for c in cells for x in draws.get((cfg, rung, c), [])]


def seg_counts(rows):
    """rows: list of (lv, lc, lp). Return Counter over the four segments."""
    out = Counter()
    for lv, lc, lp in rows:
        out[CLASS_SEG[klass(lv, lc, lp)]] += 1
    return out


def seg_pct(rows):
    n = len(rows)
    sc = seg_counts(rows)
    return {s: (round(100 * sc.get(s, 0) / n, 1) if n else 0.0) for s in SEG_ORDER}, n


def s1_stats(rows):
    if not rows:
        return float("nan"), float("nan"), 0
    a = np.array([abs(lv - lc) for lv, lc, lp in rows], dtype=float)
    n = len(a)
    se = a.std(ddof=1) / np.sqrt(n) if n > 1 else 0.0
    return a.mean(), se, n


# --------------------------------------------------------------------------
# ASSERTIONS -- every Section 2 number stays live (item 6)
# --------------------------------------------------------------------------
def run_assertions(draws, usable, attempted, fails):
    # ---- panel (a): D-cells, delta=0, five gated, RULED (result) and FULL (control)
    a_counts = {}   # (arm, cfg) -> Counter over s2 in {-1,0,1,2}
    for arm in ("RULED", "FULL"):
        for cfg in GATED:
            c = Counter()
            for lv, lc, lp in rung_draws(draws, cfg, arm, DCELLS):
                c[lv - lc] += 1           # l_cor == 1 in D-cells, so s2 = lv - lc
            a_counts[(arm, cfg)] = c

    def arm_total(arm, key):
        return sum(a_counts[(arm, cfg)][key] for cfg in GATED)

    def arm_usable(arm):
        return sum(sum(a_counts[(arm, cfg)].values()) for cfg in GATED)

    def arm_attempted(arm):
        cond = "PARTIAL_RULED" if arm == "RULED" else "FULL"  # noqa: F841 (doc)
        return sum(attempted[(cfg, arm, c)] for cfg in GATED for c in DCELLS)

    # displaced toward under = s2 > 0; over = s2 < 0
    ruled_disp = arm_total("RULED", 1) + arm_total("RULED", 2)
    full_disp = arm_total("FULL", 1) + arm_total("FULL", 2)
    check(ruled_disp == 47, f"RULED D-cell displaced == 47 (got {ruled_disp})")
    check(arm_total("RULED", -1) == 0, "RULED D-cell over-weighted == 0")
    check(full_disp == 9, f"FULL D-cell displaced == 9 (got {full_disp})")
    check(arm_total("FULL", -1) == 0, "FULL D-cell over-weighted == 0")
    check(arm_usable("RULED") == 150 and arm_attempted("RULED") == 150,
          "RULED D-cell 150 attempted / 150 usable")
    check(arm_usable("FULL") == 150 and arm_attempted("FULL") == 150,
          "FULL D-cell 150 attempted / 150 usable")
    # displaced RULED breakdown: 44 at level 2 (s2=+1), 3 at level 3 (s2=+2), 0 level 0
    check(arm_total("RULED", 1) == 44, f"RULED 44 at level 2 (got {arm_total('RULED',1)})")
    check(arm_total("RULED", 2) == 3, f"RULED 3 at level 3 (got {arm_total('RULED',2)})")

    # cell-level sign-test grain (per D3): a config-by-cell unit is "displaced
    # toward under-weighting" when its net displacement is positive
    # (n_above > n_below); units with no net displaced mass (n_above == n_below,
    # including all-correct) are excluded. This reproduces the two-sided exact
    # sign test p = 2 * 0.5^8 = 0.008 for RULED (8 vs 0) and 5 vs 0 for FULL.
    for arm, exp in (("RULED", 8), ("FULL", 5)):
        disp = over = 0
        for cfg in GATED:
            for c in DCELLS:
                v = draws.get((cfg, arm, c), [])
                na = sum(1 for lv, lc, lp in v if lv > lc)
                nb = sum(1 for lv, lc, lp in v if lv < lc)
                if na > nb:
                    disp += 1
                elif nb > na:
                    over += 1
        check(disp == exp and over == 0,
              f"{arm} cell-level sign-test units: {exp} displaced / 0 over (got {disp}/{over})")

    # ---- panel (b): mass split, bound to the RULED->ARITH transition only (item 2)
    expect_pos = {"sol-none": (4.6, 0.0), "deepseek-high": (30.6, 12.9), "glm": (77.1, 50.0)}
    expect_int = {"sol-none": (65.4, 66.9), "deepseek-high": (28.4, 42.4), "glm": (17.1, 27.9)}
    for cfg in NONCEIL:
        pr, _ = seg_pct(rung_draws(draws, cfg, "RULED"))
        ar, _ = seg_pct(rung_draws(draws, cfg, "ARITH"))
        check((pr["at_bpos"], ar["at_bpos"]) == expect_pos[cfg],
              f"{cfg} at-b_pos RULED->ARITH {expect_pos[cfg]} "
              f"(got {(pr['at_bpos'], ar['at_bpos'])})")
        check((pr["interior"], ar["interior"]) == expect_int[cfg],
              f"{cfg} interior RULED->ARITH {expect_int[cfg]} "
              f"(got {(pr['interior'], ar['interior'])})")
    # the ceiling config that moves the wrong way
    pr, _ = seg_pct(rung_draws(draws, "glm-high", "RULED"))
    ar, _ = seg_pct(rung_draws(draws, "glm-high", "ARITH"))
    check((pr["at_bpos"], ar["at_bpos"]) == (6.4, 10.7),
          f"glm-high at-b_pos RULED->ARITH (6.4, 10.7) (got {(pr['at_bpos'], ar['at_bpos'])})")

    # four segments sum to 100% of usable, every gated config-rung (Ali item 1)
    for cfg in GATED:
        for rung in ("RULED", "ARITH", "FULL"):
            rows = rung_draws(draws, cfg, rung)
            sc = seg_counts(rows)
            check(sum(sc.values()) == len(rows) == sum(usable[(cfg, rung, c)] for c in CELLS14),
                  f"{cfg}/{rung} four segments sum to usable count")
    # BEY == 0.0 for sol-none and sol-high at RULED and ARITH (Ali item 1)
    for cfg in ("sol-none", "sol-high"):
        for rung in ("RULED", "ARITH"):
            p, _ = seg_pct(rung_draws(draws, cfg, rung))
            check(p["beyond"] == 0.0, f"{cfg}/{rung} BEY == 0.0 (got {p['beyond']})")

    # ARITH_D0 campaign denominators: 980 attempted / 959 usable (whole campaign)
    araw = json.load(open(resolve(
        "results/arith/arith_d0_results_live.json")))["records"]
    check(len(araw) == 980, f"ARITH_D0 980 calls (got {len(araw)})")
    check(sum(1 for r in araw if r.get("ok")) == 959, "ARITH_D0 959 usable")

    print("All Section 2 assertions passed.")


# --------------------------------------------------------------------------
# DIAGNOSTIC (item 4): four-way mass split broken out by distance class
# --------------------------------------------------------------------------
def diagnostic(draws, usable, attempted, fails):
    lines = []
    w = lines.append
    w("=" * 78)
    w("FIGURE 2b GEOMETRY CHECK -- four-way mass split by distance class")
    w("(diagnostic only; NOT drawn in the figure)")
    w("")
    w("Distance = |level(b_pos) - l_cor| per cell.  Ladder cell coverage and")
    w("distance distribution (PARTIAL_BLIND excluded; that arm's target IS b_pos):")
    w("    dist = 1 : D1, D2, D3            (interior structurally EMPTY here)")
    w("    dist = 2 : B1, B2, B3")
    w("    dist = 3 : A1-A5, C1-C3")
    w("No b_pos reference line is drawn in variant 2 because this varies (1..3).")
    w("=" * 78)

    # per config x rung x dist: segment counts + usable/attempted
    for cfg in ALL_ORDER:
        tag = "" if cfg in GATED else "   [excluded from claim population]"
        star = " *ceiling" if cfg in CEILING else ""
        w("")
        w(f"CONFIG: {cfg}{star}{tag}")
        w(f"  {'rung':<6}{'dist':>5}{'beyond':>8}{'at_bpos':>8}{'interior':>9}"
          f"{'at_past':>8}{'usable':>8}{'attempt':>8}")
        for rung in ("RULED", "ARITH", "FULL"):
            for dist in (1, 2, 3):
                cells = [c for c in CELLS14 if cell_dist(c) == dist]
                rows = [x for c in cells for x in draws.get((cfg, rung, c), [])]
                us = sum(usable[(cfg, rung, c)] for c in cells)
                at = sum(attempted[(cfg, rung, c)] for c in cells)
                if at == 0:
                    continue
                sc = seg_counts(rows)
                w(f"  {rung:<6}{dist:>5}{sc.get('beyond',0):>8}{sc.get('at_bpos',0):>8}"
                  f"{sc.get('interior',0):>9}{sc.get('at_past',0):>8}{us:>8}{at:>8}")

    # ---- the load-bearing question: does interior mass RISE within each distance
    # ---- class separately (RULED->ARITH), or only in the pool?
    w("")
    w("=" * 78)
    w("INTERIOR-MASS RISE, RULED -> ARITH, per non-ceiling admitted config")
    w("(Section 5 headline: interior mass rises in every non-ceiling admitted config)")
    w("Interior % within a distance class = interior draws / usable draws in that class.")
    w("dist=1 (D-cells) is omitted: interior is structurally empty there (always 0).")
    w("=" * 78)
    verdicts = []
    for cfg in NONCEIL:
        w("")
        w(f"CONFIG: {cfg}")
        # pooled
        pr, _ = seg_pct(rung_draws(draws, cfg, "RULED"))
        ar, _ = seg_pct(rung_draws(draws, cfg, "ARITH"))
        w(f"  pooled (14 cells) : interior {pr['interior']:>5.1f} -> {ar['interior']:>5.1f}"
          f"   {'RISE' if ar['interior'] > pr['interior'] else 'no rise'}")
        for dist in (2, 3):
            cells = [c for c in CELLS14 if cell_dist(c) == dist]
            r_rows = [x for c in cells for x in draws.get((cfg, "RULED", c), [])]
            a_rows = [x for c in cells for x in draws.get((cfg, "ARITH", c), [])]
            r_int = 100 * seg_counts(r_rows).get("interior", 0) / len(r_rows) if r_rows else float("nan")
            a_int = 100 * seg_counts(a_rows).get("interior", 0) / len(a_rows) if a_rows else float("nan")
            rose = a_int > r_int
            verdicts.append((cfg, dist, rose))
            w(f"  dist={dist} ({'B' if dist==2 else 'A/C'} cells) : "
              f"interior {r_int:>5.1f} -> {a_int:>5.1f}   "
              f"[n {len(r_rows)}->{len(a_rows)}]   {'RISE' if rose else 'no rise'}")

    w("")
    w("VERDICT:")
    pooled_all = all(
        seg_pct(rung_draws(draws, cfg, "ARITH"))[0]["interior"]
        > seg_pct(rung_draws(draws, cfg, "RULED"))[0]["interior"] for cfg in NONCEIL)
    w(f"  Pooled rise holds for all three non-ceiling admitted configs: {pooled_all}")
    by_class_ok = all(rose for _, _, rose in verdicts)
    w(f"  Rise holds WITHIN EVERY distance class (dist=2 and dist=3) for all three: "
      f"{by_class_ok}")
    if not by_class_ok:
        w("  -> The pooled rise is NOT uniform across distance classes. Offending cells:")
        for cfg, dist, rose in verdicts:
            if not rose:
                w(f"       {cfg}  dist={dist}  interior does not rise")
        w("  -> Section 5's headline is materially weaker than a per-class reading.")
    else:
        w("  -> Section 5's headline survives a per-distance-class reading, not just the pool.")

    text = "\n".join(lines)
    (FIGDIR / "results_geometry_check.txt").write_text(text + "\n")
    print(text)
    return by_class_ok, verdicts


# --------------------------------------------------------------------------
# PANEL (a): signed s2 on D-cells, result (RULED) vs control (FULL)
# --------------------------------------------------------------------------
A_FILL = {
    -1: dict(facecolor="white", hatch="////", edgecolor="black"),
    0: dict(facecolor="0.85", edgecolor="0.3"),
    1: dict(facecolor="0.55", edgecolor="0.3"),
    2: dict(facecolor="0.25", edgecolor="0.3"),
}
A_LEGEND = {-1: "$s_2=-1$ (over)", 0: "$s_2=0$ (correct)",
            1: "$s_2=+1$", 2: "$s_2=+2$"}


def panel_a(draws):
    fig, ax = plt.subplots(figsize=(3.2, 2.85))
    gap_cfg, gap_arm, barh = 1.0, 0.44, 0.34
    yt, ytl = [], []
    for i, cfg in enumerate(ROW_ORDER):
        base = -i * gap_cfg
        for arm, dy in (("RULED", gap_arm / 2), ("FULL", -gap_arm / 2)):
            y = base + dy
            rows = rung_draws(draws, cfg, arm, DCELLS)
            cnt = Counter(lv - lc for lv, lc, lp in rows)
            left = 0.0
            for s2 in (-1, 0, 1, 2):
                wdt = cnt.get(s2, 0)
                style = dict(A_FILL[s2])
                if arm == "FULL":
                    style["alpha"] = 0.6            # subordinate the control arm
                ax.barh(y, wdt, left=left, height=barh, linewidth=0.5, **style)
                left += wdt
        yt.append(base)
        ytl.append(ABBR[cfg])                  # same abbreviations as panel (b) (A2)
    # label result/control once, on the top configuration's pair
    top = 0.0
    ax.text(30.7, top + gap_arm / 2, "result", va="center", ha="left",
            fontsize=FS_MIN, style="italic")
    ax.text(30.7, top - gap_arm / 2, "control", va="center", ha="left",
            fontsize=FS_MIN, style="italic", color="0.35")
    # the zero line: boundary between s2=-1 and the rest; sits flush at x=0
    ax.axvline(0, color="black", lw=0.9)
    ax.annotate("expressible,\nunobserved", xy=(0, gap_arm / 2), xytext=(4.5, top + 0.98),
                fontsize=FS_MIN, va="center", ha="left",
                arrowprops=dict(arrowstyle="->", lw=0.6, color="0.3"))
    ax.set_yticks(yt)
    ax.set_yticklabels(ytl, fontsize=FS_MIN)
    ax.set_ylim(-(len(ROW_ORDER) - 1) * gap_cfg - 0.6, 1.45)
    ax.set_xlim(0, 41)                        # headroom so result/control sit INSIDE
    ax.set_xticks([0, 10, 20, 30])
    ax.set_xlabel("draws (30 per configuration-arm)", fontsize=FS_LAB)
    ax.tick_params(labelsize=FS_MIN)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    handles = [Patch(label=A_LEGEND[s], **A_FILL[s]) for s in (-1, 0, 1, 2)]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.20),
              ncol=2, fontsize=FS_MIN, frameon=False, handlelength=1.1,
              columnspacing=1.0, handletextpad=0.4)
    fig.savefig(FIGDIR / "results_signed_error.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# PANEL (b) variant 1: four-way mass split
# --------------------------------------------------------------------------
B_FILL = {
    "beyond": dict(facecolor="white", hatch="xxxx", edgecolor="black"),
    "at_bpos": dict(facecolor="0.25", edgecolor="0.3"),
    "interior": dict(facecolor="0.60", edgecolor="0.3"),
    "at_past": dict(facecolor="white", edgecolor="black"),
}
RUNG_LABEL = {"RULED": "RULED $\\{i,c,a\\}$", "ARITH": "ARITH\\_D0 $\\{c,a\\}$",
              "FULL": "FULL $\\{a\\}$"}


def panel_b_mass(draws, usable, attempted):
    # Config name is a rotated label in a thin left gutter (keeps the figure
    # narrow so fonts stay >=7pt at 0.48\textwidth); each bar is tagged only by
    # its rung, which is short.
    fig, ax = plt.subplots(figsize=(3.05, 3.75))
    # Rungs are single-letter ticks (R/A/F, keyed in the legend) and configs are
    # abbreviated once per group (module-level ABBR, shared with panel (a) per A2).
    barh, gap_rung, gap_cfg = 0.62, 0.72, 1.05
    y = 0.0
    yt, ytl = [], []
    for cfg in ROW_ORDER:                    # best-gated at top, matching panel (a)
        grp_ys = []
        for rung in ("RULED", "ARITH", "FULL"):
            rows = rung_draws(draws, cfg, rung)
            n = len(rows)
            sc = seg_counts(rows)
            left = 0.0
            for seg in SEG_ORDER:
                wdt = 100 * sc.get(seg, 0) / n if n else 0.0
                ax.barh(y, wdt, left=left, height=barh, linewidth=0.5, **B_FILL[seg])
                left += wdt
            yt.append(y)
            ytl.append(rung[0])                          # R / A / F, keyed in legend
            grp_ys.append(y)
            y -= gap_rung
        star = "*" if cfg in CEILING else ""
        ax.text(-0.10, sum(grp_ys) / len(grp_ys), f"{ABBR[cfg]}{star}", ha="right",
                va="center", fontsize=FS_MIN,
                transform=ax.get_yaxis_transform())     # abbreviated config once per group
        y -= (gap_cfg - gap_rung)
    ax.set_yticks(yt)
    ax.set_yticklabels(ytl, fontsize=FS_MIN)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("percent of usable draws", fontsize=FS_LAB)
    ax.tick_params(labelsize=FS_MIN)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_ylim(y + gap_rung - 0.5, barh + 0.15)
    handles = [Patch(label=SEG_LABEL[s], **B_FILL[s]) for s in SEG_ORDER]
    leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.13),
                    ncol=2, fontsize=FS_MIN, frameon=False, handlelength=1.1,
                    columnspacing=1.0, handletextpad=0.4,
                    title="rows R / A / F = RULED / ARITH / FULL\n"
                          "* at ceiling; outside the claim population")
    leg.get_title().set_fontsize(FS_MIN - 1)
    leg.get_title().set_color("0.3")
    fig.savefig(FIGDIR / "results_mass.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------
# PANEL (b) variant 2: the s1 ladder. NO b_pos reference line (distance varies).
# --------------------------------------------------------------------------
def panel_b_s1(draws):
    fig, ax = plt.subplots(figsize=(3.35, 2.75))
    rungs = ("RULED", "ARITH", "FULL")
    xs = np.arange(len(rungs))
    finals = []                              # (cfg, final-rung mean, ceiling?)
    for cfg in ROW_ORDER:
        means, ses = [], []
        for rung in rungs:
            m, se, n = s1_stats(rung_draws(draws, cfg, rung))
            means.append(m)
            ses.append(se)
        ceil = cfg in CEILING
        ax.errorbar(xs, means, yerr=ses, marker="o", ms=3.2, lw=1.1,
                    color="0.45" if ceil else "black",
                    linestyle="--" if ceil else "-",
                    capsize=1.8, elinewidth=0.6, zorder=3)
        finals.append([cfg, means[-1], ceil])
    ymax = max(f[1] for f in finals + [[None, max(s1_stats(rung_draws(draws, c, "RULED"))[0]
                                                   for c in ROW_ORDER), None]])
    ax.set_ylim(0, ymax * 1.10)
    ax.set_xlim(-0.25, len(rungs) - 1 + 1.55)     # room so right-end labels sit INSIDE
    # de-collide the right-end direct labels: push apart to a minimum vertical gap
    gap = 0.09 * ymax
    finals.sort(key=lambda t: t[1])
    for i in range(1, len(finals)):
        if finals[i][1] - finals[i - 1][1] < gap:
            finals[i][1] = finals[i - 1][1] + gap
    for cfg, ylab, ceil in finals:
        ax.text(xs[-1] + 0.07, ylab, f"{cfg}{'*' if ceil else ''}", va="center",
                ha="left", fontsize=FS_MIN, color="0.4" if ceil else "black")
    ax.set_xticks(xs)
    ax.set_xticklabels(["RULED\n$\\{i,c,a\\}$", "ARITH_D0\n$\\{c,a\\}$", "FULL\n$\\{a\\}$"],
                       fontsize=FS_MIN)
    ax.set_ylabel("mean $s_1$ (bins)", fontsize=FS_LAB)
    ax.tick_params(labelsize=FS_MIN)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.text(0.9, ymax * 1.06, "* at ceiling (0.15-bin guard)",
            fontsize=FS_MIN - 1, style="italic", color="0.3", va="top", ha="left")
    fig.savefig(FIGDIR / "results_abs_error.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    FIGDIR.mkdir(parents=True, exist_ok=True)
    draws, usable, attempted, fails = load()
    run_assertions(draws, usable, attempted, fails)
    diagnostic(draws, usable, attempted, fails)
    panel_a(draws)
    panel_b_mass(draws, usable, attempted)
    panel_b_s1(draws)
    print("\nWrote:")
    for f in ("results_signed_error.pdf", "results_mass.pdf", "results_abs_error.pdf",
              "results_geometry_check.txt"):
        print(f"  paper/figures/{f}")


if __name__ == "__main__":
    main()
