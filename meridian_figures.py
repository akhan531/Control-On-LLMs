"""
meridian_figures.py — figures for Task 2.1f (scenario section 4.5).

Reads results_2_1f/meridian_v2_results.json, writes PNG and PDF into
figures_2_1f/. Imports meridian_analyze for the estimators so the figures and
the tables cannot drift apart: every number plotted here is produced by the
same stratified recombination used in the analysis.

Figure 2 is the paper's headline. Figures 1 and 3 are supporting. Figure 4 is
the recovery panel. A fifth panel, not in the original spec, plots the surname
sensitivity, because the two counterbalanced halves disagree by enough that
reporting only their average would hide something real.
"""

from __future__ import annotations

import math
import os
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import meridian_analyze as A
import meridian_model as M

OUT = Path(os.environ.get("FIG_DIR", "figures_2_1f"))
GROUP_SIZES = A.GROUP_SIZES

MODEL_C = "#3b6ea5"      # model / theory
DATA_C = "#c1441e"       # measured
GREY = "#8a8a8a"


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT/name}.png and .pdf")


# ─────────────────────────────────────────────────────────────────────────────

def fig2_scaling(by, seeds):
    """The headline: paired gap against group size, with the theory overlaid."""
    xs, ys, es = [], [], []
    for N in GROUP_SIZES:
        r = A.gap_at(by, seeds, N)
        if r:
            xs.append(N); ys.append(r[0]); es.append(r[1])
    slope, sse = A.wls(xs, ys, es)

    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    ax.errorbar(xs, ys, yerr=[1.96 * e for e in es], fmt="o-", color=DATA_C,
                capsize=4, lw=2, ms=7, label="measured (LLM debate)", zorder=3)
    ax.plot(GROUP_SIZES, [A.EXACT_GAP[N] for N in GROUP_SIZES], "s--",
            color=MODEL_C, lw=2, ms=6, label="predicted (model)", zorder=2)

    bound = [A.EXACT_GAP[N] + M.dV_lower_bound(N) - M.exact_stats(N)["dV"]
             for N in GROUP_SIZES]
    ax.plot(GROUP_SIZES, [M.exact_stats(N)["I_TC"] + M.dV_lower_bound(N)
                          for N in GROUP_SIZES],
            ":", color=GREY, lw=1.6, label="Corollary 3b bound", zorder=1)

    ax.axhline(0, color="k", lw=0.8, alpha=0.4)
    ax.set_xlabel("group size $N$")
    ax.set_ylabel("paired gap  $V_{\\mathrm{sel}}(1) - V_{\\mathrm{hon}}(1)$   (nats)")
    ax.set_title("Selective-disclosure damage grows with group size")
    ax.set_xticks(GROUP_SIZES)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.text(0.97, 0.05,
            f"measured slope {slope:.3f}$\\pm${sse:.3f} nats/agent\n"
            f"predicted {A.PREDICTED_SLOPE:.3f}   ratio {slope/A.PREDICTED_SLOPE:.2f}$\\times$",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GREY, alpha=0.9))
    ax.grid(alpha=0.25, ls=":")
    save(fig, "fig2_scaling")


def fig1_trajectories(by, seeds):
    """Three arms over rounds, model panel beside measured panel."""
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2), sharey=True)
    arms = [("honest", "#2e7d32", "honest"),
            ("selective", DATA_C, "selective"),
            ("delayed", "#8e44ad", "delayed")]
    N = 9

    for arm, c, lab in arms:
        vals = [M.exact_stats(N, arm, t)["V"] for t in range(1, M.R + 1)]
        v0 = M.exact_stats(N, arm, 1)["I_TC"]
        axes[0].plot(range(0, M.R + 1), [v0] + vals, "o-", color=c, label=lab, lw=2)

    for arm, c, lab in arms:
        ys = []
        for t in range(1, M.R + 1):
            v = [A.kl_floored(by[(N, arm, i)]["b_star"],
                              by[(N, arm, i)]["rounds"][t - 1]["probe_b"]["slots"], 0)
                 for i in range(seeds) if (N, arm, i) in by]
            v = [x for x in v if x is not None]
            ys.append(st.fmean(v))
        v0 = st.fmean([M.kl(tuple(by[(N, arm, i)]["b_star"]), M.PI)
                       for i in range(seeds) if (N, arm, i) in by])
        axes[1].plot(range(0, M.R + 1), [v0] + ys, "o-", color=c, label=lab, lw=2)

    axes[0].set_title(f"model, $N={N}$")
    axes[1].set_title(f"measured, $N={N}$")
    for ax in axes:
        ax.set_xlabel("round $t$")
        ax.axhline(0, color="k", lw=0.8, alpha=0.4)
        ax.grid(alpha=0.25, ls=":")
        ax.set_xticks(range(0, M.R + 1))
    axes[0].set_ylabel("$V(t) = D(b^*\\,\\|\\,b^t)$   (nats)")
    axes[1].legend(frameon=False, fontsize=9)
    fig.suptitle("Belief error by round: honest recovers, selective is stranded, "
                 "delayed recovers late", fontsize=10.5)
    save(fig, "fig1_trajectories")


def fig3_decomposition(by, seeds):
    """
    The decomposition, plotted honestly: the measured tracking error does NOT
    follow the exact one, because Probe P does no silence inference. This
    figure exists to show that gap, not to hide it.
    """
    exact_eps = [A.EXACT_EPS[N] for N in GROUP_SIZES]
    exact_w = [A.EXACT_WBAR[N] for N in GROUP_SIZES]
    meas = []
    for N in GROUP_SIZES:
        v = [by[(N, "selective", i)]["rounds"][0]["eps_hat"]
             for i in range(seeds) if (N, "selective", i) in by]
        v = [x for x in v if x is not None]
        meas.append(st.fmean(v))

    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    ax.plot(GROUP_SIZES, exact_eps, "s--", color=MODEL_C, lw=2,
            label="$\\epsilon(1)$ exact (tracking error)")
    ax.plot(GROUP_SIZES, exact_w, "^--", color="#2e7d32", lw=2,
            label="$\\bar{W}(1)$ exact")
    ax.plot(GROUP_SIZES, meas, "o-", color=DATA_C, lw=2,
            label="$\\hat{\\epsilon}(1)$ measured")
    ax.axhline(M.entropy(M.PI), color=GREY, ls=":", lw=1.6,
               label="budget $H(\\pi)=0.693$")
    ax.set_xlabel("group size $N$")
    ax.set_ylabel("nats")
    ax.set_xticks(GROUP_SIZES)
    ax.set_title("Almost all error is tracking error, but the probe does not see it")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(alpha=0.25, ls=":")
    ax.text(0.97, 0.05,
            "measured $\\hat{\\epsilon}$ is flat: Probe P\nperforms no silence inference",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GREY, alpha=0.9))
    save(fig, "fig3_decomposition")


def fig4_recovery(by, seeds):
    """Delayed arm: matches selective at t=1, collapses at t=K."""
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for arm, c, lab in (("selective", DATA_C, "selective"),
                        ("delayed", "#8e44ad", "delayed")):
        ys, es = [], []
        for N in GROUP_SIZES:
            r = A.gap_at(by, seeds, N, rnd=5, arm=arm)
            ys.append(r[0]); es.append(r[1])
        ax.errorbar(GROUP_SIZES, ys, yerr=[1.96 * e for e in es], fmt="o-",
                    color=c, lw=2, capsize=4, label=f"{lab}, $t=5$")
    ax.axhline(0, color="k", lw=0.9, alpha=0.5)
    ax.set_xlabel("group size $N$")
    ax.set_ylabel("paired gap at $t=5$   (nats)")
    ax.set_xticks(GROUP_SIZES)
    ax.set_title("Releasing withheld findings restores the group at every size")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.25, ls=":")
    save(fig, "fig4_recovery")


def fig5_surname(by, seeds):
    """
    Not in the original spec. The two counterbalanced surname assignments give
    materially different magnitudes, so reporting only their average would hide
    a real sensitivity. Both halves are independently monotone, which is the
    point: the phenomenon does not depend on which name is suppressed, only its
    size does.
    """
    fig, ax = plt.subplots(figsize=(6.2, 4.2))
    for sw, c, lab in ((False, "#1b6ca8", "Chen in suppressed slot"),
                       (True, "#e08214", "Alvarez in suppressed slot")):
        ys = []
        for N in GROUP_SIZES:
            vals = []
            for i in range(seeds):
                h = by.get((N, "honest", i)); s = by.get((N, "selective", i))
                if not h or not s or h["swapped"] != sw:
                    continue
                a, b = h["rounds"][0]["V_hat"], s["rounds"][0]["V_hat"]
                if a is not None and b is not None:
                    vals.append(b - a)
            ys.append(st.fmean(vals))
        ax.plot(GROUP_SIZES, ys, "o-", color=c, lw=2, label=lab)

    ys_all = []
    for N in GROUP_SIZES:
        r = A.gap_at(by, seeds, N)
        ys_all.append(r[0])
    ax.plot(GROUP_SIZES, ys_all, "k--", lw=1.6, label="counterbalanced mean")
    ax.set_xlabel("group size $N$")
    ax.set_ylabel("paired gap   (nats)")
    ax.set_xticks(GROUP_SIZES)
    ax.set_title("Both surname assignments grow with $N$; only the size differs")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(alpha=0.25, ls=":")
    save(fig, "fig5_surname_sensitivity")


def main() -> int:
    _d, by, seeds = A.load()
    print(f"figures from {seeds} seeds/cell")
    fig2_scaling(by, seeds)
    fig1_trajectories(by, seeds)
    fig3_decomposition(by, seeds)
    fig4_recovery(by, seeds)
    fig5_surname(by, seeds)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
