"""Task 1.14d, Figure 1: the debate trajectory, empirical | model.

    python fig1_trajectory.py --results results_1_14c_sim_70b_40seed/task_1_14c_results.json

WHAT THE FIGURE CLAIMS
----------------------
Left panel: V(t) = D(b*||b^t) measured from the LLM debate via the observer
probe, three arms. Right panel: the same three arms under the frozen
instantiation of poster_model.md. Shared y-axis, shared round range, both
anchored at the shared V(0) = D(b*||pi) = 0.9717, disclosure round K=4 marked.

The claim is that the caricature reproduces the DYNAMICAL SIGNATURE:
wrong-consensus plateau, then a deferred and compressed correction. It is
NOT a validation claim and NOT a quantitative match (N8 guardrail). The two
panels are drawn side by side rather than overlaid for exactly that reason:
shape-matching, not number-matching.

Both b* and the latent truth T sit on Chen here, and they are different
objects. V is measured against b*, the full-information posterior, never
against T. Nothing in the figure knows what T is.

WHY NO ERROR BANDS BY DEFAULT
-----------------------------
--bands is available and off by default. Per-seed V is not a well-defined
quantity (about 30% of per-seed observer-rounds are +infinity, and round 5
of the withhold arm takes only 2 distinct values across 40 seeds), so a
seed-spread band would be plotting the report grid, not belief uncertainty.
The coherent band is a bootstrap of the averaged curve, which --bands draws,
but it degenerates at withhold t=5 (13% of resamples give +infinity, because
the observer reports Chen = 1.000 exactly) and the script refuses to draw a
band there rather than silently dropping those resamples.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import fig_common as FC

ARMS = ["honest", "withhold", "never"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="1.14c results JSON (the 40-seed file)")
    ap.add_argument("--out", default="fig1_trajectory.png")
    ap.add_argument("--bands", action="store_true", help="bootstrap CI on the averaged curve")
    args = ap.parse_args()

    d = FC.load(args.results)
    plt.rcParams.update(FC.POSTER_RC)

    ts = np.arange(FC.R + 1)
    emp, mod, ns = {}, {}, {}
    for arm in ARMS:
        runs = d["runs"][arm]
        assert FC.realized_matches_nominal(runs), f"{arm}: realized tau != nominal tau"
        emp[arm] = FC.empirical_V(runs)
        mod[arm] = FC.model_V(arm)
        ns[arm] = len(runs)

    # Both panels share V(0). Assert it rather than trust it.
    v0 = FC.kl(FC.B_STAR, np.array([1 / 3, 1 / 3, 1 / 3]))
    for arm in ARMS:
        assert abs(emp[arm][0] - v0) < 1e-6, f"{arm}: empirical t=0 probe is not the prior"
        assert abs(mod[arm][0] - v0) < 1e-9, f"{arm}: model t=0 is not the prior"

    hi = max(max(emp[a].max() for a in ARMS), max(mod[a].max() for a in ARMS))
    ylim = (-0.12, hi * 1.10)

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)

    for ax, src, title in (
        (axes[0], emp, "LLM Debate (Llama-3.3-70B)"),
        (axes[1], mod, "Modeled Debate"),
    ):
        for arm in ARMS:
            lab = FC.ARM_LABEL[arm]
            ax.plot(ts, src[arm], marker="o", color=FC.ARM_COLOR[arm], label=lab, zorder=3)

        if args.bands and src is emp:
            for arm in ARMS:
                lo, hh, deg = FC.bootstrap_V(d["runs"][arm])
                ok = ~np.isnan(lo)
                ax.fill_between(
                    ts[ok], lo[ok], hh[ok], color=FC.ARM_COLOR[arm], alpha=0.15, lw=0, zorder=1
                )
                for t in ts[~ok]:
                    print(f"  [bands] {arm} t={t}: CI unbounded, band omitted")

        ax.axvline(FC.K, color="0.55", ls="--", lw=1.2, zorder=0)
        ax.text(
            FC.K, ylim[1] * 0.97, " Disclosure", color="0.4", fontsize=11, va="top"
        )
        ax.axhline(0, color="0.8", lw=1, zorder=0)
        ax.set_xticks(ts)
        ax.set_xlabel("Round $t$")
        ax.set_title(title)
        ax.set_ylim(*ylim)
        ax.set_xlim(-0.25, FC.R + 0.25)

    axes[0].set_ylabel("$V(t) = D(b^\\ast \\,\\|\\, b^t)$   (nats)")
    axes[0].legend(frameon=False, loc="upper left")

    fig.tight_layout()
    fig.savefig(args.out)
    print(f"wrote {args.out}")

    print("\n  arm        n   " + "  ".join(f"t={t}" for t in ts))
    for arm in ARMS:
        print(f"  {arm:9s} {ns[arm]:2d}   emp " + "  ".join(f"{v:5.3f}" for v in emp[arm]))
        print(f"  {'':9s}      mod " + "  ".join(f"{v:5.3f}" for v in mod[arm]))
        print(f"  {'':9s}      total |emp-mod| over t=1..5 = {np.abs(emp[arm]-mod[arm])[1:].sum():.3f}")


if __name__ == "__main__":
    main()
