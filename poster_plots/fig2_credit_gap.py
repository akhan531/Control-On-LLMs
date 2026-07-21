"""Task 1.14d, Figure 2: the credit gap across arms, as a boxplot.

    python fig2_credit_gap.py --results results_1_14c_sim_70b_40seed/task_1_14c_results.json

WHAT THE FIGURE CLAIMS
----------------------
Empirical only, no model overlay (N8). The quantity is pivotal_credit: the
judge-assigned share of credit that goes to the holder of the decisive clue
c4. Three arms, ordered left to right by increasing disclosure delay of c4:

    honest   tau_4 = 1     disclose the decisive clue immediately
    withhold tau_4 = 4     hold it until the last substantive round
    never    tau_4 = inf   never disclose it

The story is TIMING, not withholding. Credit rises from honest to withhold
and then collapses at never: holding the decisive clue until the decisive
round beats honesty, but holding it forever is the worst outcome, because the
answer is never corrected (never's final-correct rate is 0) and the judge
gives its holder almost nothing. A thin line through the three means makes
the rise-then-fall explicit. The never arm is the guardrail against a naive
"agents should just hoard evidence" reading.

    honest    median 0.40   mean 0.475   n = 40
    withhold  median 0.60   mean 0.642   n = 40   <- peak
    never     median 0.075  mean 0.084   n = 16

NOTES
-----
The never arm has n = 16 (only the pilot seeds were run for it), against
n = 40 for the other two. The boxplot handles unequal n; n is printed under
each box so it is never hidden. All raw points are drawn (jittered), so the
box never conceals the sample it summarizes.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import poster_plots.fig_common as FC

ORDER = ["honest", "withhold", "never"]
TAU = {"honest": r"$\tau_4=1$", "withhold": r"$\tau_4=4$", "never": r"$\tau_4=\infty$"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="1.14c results JSON (the 40-seed file)")
    ap.add_argument("--out", default="fig2_credit_gap.png")
    ap.add_argument("--no-points", action="store_true", help="hide the jittered raw points")
    args = ap.parse_args()

    d = FC.load(args.results)
    plt.rcParams.update(FC.POSTER_RC)
    rng = np.random.default_rng(0)

    data = {arm: np.array([r["pivotal_credit"] for r in d["runs"][arm]]) for arm in ORDER}
    xs = np.arange(1, len(ORDER) + 1)

    fig, ax = plt.subplots(figsize=(7.4, 3.5))

    bp = ax.boxplot(
        [data[a] for a in ORDER], positions=xs, widths=0.55,
        patch_artist=True, showmeans=False, showfliers=False, zorder=2,
        medianprops=dict(color="0.15", lw=2.2),
        whiskerprops=dict(color="0.45", lw=1.4),
        capprops=dict(color="0.45", lw=1.4),
    )
    for a, box in zip(ORDER, bp["boxes"]):
        box.set(facecolor=FC.ARM_COLOR[a], alpha=0.28, edgecolor=FC.ARM_COLOR[a], linewidth=1.8)

    if not args.no_points:
        for i, a in enumerate(ORDER):
            v = data[a]
            jx = xs[i] + (rng.random(len(v)) - 0.5) * 0.28
            ax.scatter(jx, v, s=26, facecolor=FC.ARM_COLOR[a], edgecolor="white",
                       linewidth=0.5, alpha=0.75, zorder=3)

    ax.set_xticks(xs)
    ax.set_xticklabels(
        [f"{a.capitalize()}\n{TAU[a]}" for a in ORDER], fontsize=12.5
    )
    ax.set_xlim(0.4, len(ORDER) + 0.6)
    ax.set_ylim(-0.05, 1.08)
    ax.set_ylabel("Share to $c_4$ holder")
    ax.set_title("Credit by Decisive-Clue Disclosure Behavior", fontsize=13.5)

    fig.tight_layout()
    fig.savefig(args.out)
    print(f"wrote {args.out}")
    print("\n  arm        n   median   mean")
    for a in ORDER:
        v = data[a]
        print(f"  {a:9s} {len(v):2d}   {np.median(v):.3f}    {v.mean():.3f}")


if __name__ == "__main__":
    main()
