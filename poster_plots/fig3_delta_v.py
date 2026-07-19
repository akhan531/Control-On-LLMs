"""Task 1.14d, Figure 3: the per-round increment of the Lyapunov function.

    python fig3_delta_v.py --results results_1_14c_sim_70b_40seed/task_1_14c_results.json

WHAT THE FIGURE CLAIMS
----------------------
ΔV(t) = V(t) - V(t-1), the backward difference (poster_model.md §5.2,
"corrected timing convention, close-of-round"). Two arms, honest vs
withhold, empirical | model, matching Fig 1's panel layout.

This is the figure Burlion reads first, because ΔV is literally the
increment of the candidate Lyapunov function. The sign is the entire story:

  ΔV(t) > 0  the state moved AWAY from b* this round, V rose, the decrease
             condition is violated.
  ΔV(t) < 0  the state descended toward b*.

The claim the panel makes, and the open item it closes (Task 1.11): the
withhold arm has ΔV(1) > 0. The round-1 disclosure of {c1,c2,c3} pushes the
public state toward the wrong consensus (Alvarez), away from b* (Chen), so V
RISES before it falls. This is Corollary 3 regime (a) -- the disclosure
points away from b* -- NOT an overshoot past b*. (The regime-(b) overshoot
gloss was corrected 2026-07-16 to the level-set reflection; the round-1 rise
is nowhere near it.) The model predicts +1.6201; the data shows +1.017. Same
sign, and that sign is the point.

The correction is deferred and violent: withhold ΔV(4) is the round the
pivotal clue finally lands, model -2.5919, data -2.242. honest, by contrast,
descends on round 1 and is done.

NOT A CONSERVATION-LAW FIGURE
-----------------------------
The model's increments sum to -D(b*||pi) = -0.9717 exactly for both arms
(eq. 12): timing reshapes the whole trajectory without changing the total
descent. The EMPIRICAL increments do not sum to -0.9717 -- honest sums to
about -0.67 -- because the LLM's final belief is not exactly b*. That
shortfall is the rhetoric residual (Task 1.12's object), not an error here,
so this figure does not draw or assert the conservation law. It is printed
for the record only.

WHY NO ERROR BARS BY DEFAULT
----------------------------
Same reasoning as Fig 1. Per-seed ΔV is a difference of two per-seed KLs,
each undefined on ~30% of seeds and quantized on the rest, so a seed-spread
error bar would render the report grid, not belief uncertainty. --bands
draws the coherent alternative: a PAIRED bootstrap that resamples seeds once
and recomputes V(t) and V(t-1) from the same resample before differencing.
It degenerates only where V(5) enters, i.e. withhold ΔV(5) = V(5) - V(4),
because the observer reports Chen = 1.000 exactly in some resamples; the
script omits that one error bar rather than dropping resamples and biasing
the interval. Every other increment, including the withhold ΔV(4) crash, has
a well-defined interval.
This bootstrap lives here, not in fig_common, so fig_common is untouched.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import fig_common as FC

ARMS = ["honest", "withhold"]  # spec: Fig 3 is honest vs withhold


def empirical_dV(runs: list[dict]) -> np.ndarray:
    """ΔV(t), t = 1..R, as the first difference of the average-then-KL curve."""
    return np.diff(FC.empirical_V(runs))


def model_dV(arm: str) -> np.ndarray:
    """ΔV(t), t = 1..R, from the frozen instantiation."""
    return np.diff(FC.model_V(arm))


def paired_bootstrap_dV(runs: list[dict], B: int = 4000, seed: int = 0):
    """Percentile CI on each ΔV(t) via a paired seed bootstrap.

    One resample of seeds is used to recompute the entire V(0..R) curve, then
    differenced, so V(t) and V(t-1) share the resample. A resample whose mean
    hits a zero coordinate at some t gives V(t) = +inf; any ΔV touching that t
    is undefined for that resample and the whole t-column is flagged.
    """
    rng = np.random.default_rng(seed)
    n = len(runs)
    obs = [FC.observer_matrix(runs, t) for t in range(FC.R + 1)]
    cols = [[] for _ in range(FC.R)]
    bad = np.zeros(FC.R, dtype=int)
    for _ in range(B):
        idx = rng.integers(0, n, n)
        Vs = []
        ok = True
        for t in range(FC.R + 1):
            m = obs[t][idx].mean(axis=0)
            if (m <= 0).any():
                Vs.append(np.inf)
            else:
                Vs.append(FC.kl(FC.B_STAR, m))
        dv = np.diff(Vs)
        for i in range(FC.R):
            if np.isfinite(dv[i]):
                cols[i].append(dv[i])
            else:
                bad[i] += 1
    lo = np.array([np.percentile(c, 2.5) if b == 0 else np.nan for c, b in zip(cols, bad)])
    hi = np.array([np.percentile(c, 97.5) if b == 0 else np.nan for c, b in zip(cols, bad)])
    return lo, hi, bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="1.14c results JSON (the 40-seed file)")
    ap.add_argument("--out", default="fig3_delta_v.png")
    ap.add_argument("--bands", action="store_true", help="paired-bootstrap CI as error bars")
    args = ap.parse_args()

    d = FC.load(args.results)
    plt.rcParams.update(FC.POSTER_RC)

    rounds = np.arange(1, FC.R + 1)
    emp, mod, ns = {}, {}, {}
    for arm in ARMS:
        runs = d["runs"][arm]
        assert FC.realized_matches_nominal(runs), f"{arm}: realized tau != nominal tau"
        emp[arm] = empirical_dV(runs)
        mod[arm] = model_dV(arm)
        ns[arm] = len(runs)

    allvals = np.concatenate([emp[a] for a in ARMS] + [mod[a] for a in ARMS])
    pad = 0.15 * (allvals.max() - allvals.min())
    ylim = (allvals.min() - pad, allvals.max() + pad * 1.4)

    w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True)

    for ax, src, title, is_emp in (
        (axes[0], emp, "LLM Debate (Llama-3.3-70B)", True),
        (axes[1], mod, "Modeled Debate", False),
    ):
        for j, arm in enumerate(ARMS):
            off = (j - 0.5) * w
            lab = FC.ARM_LABEL[arm]
            bars = ax.bar(
                rounds + off, src[arm], width=w, color=FC.ARM_COLOR[arm],
                label=lab, edgecolor="white", linewidth=0.6, zorder=3,
            )
            if args.bands and is_emp:
                lo, hi, bad = paired_bootstrap_dV(d["runs"][arm])
                for i, b in enumerate(bad):
                    if b == 0:
                        yv = src[arm][i]
                        ax.errorbar(
                            rounds[i] + off, yv, yerr=[[yv - lo[i]], [hi[i] - yv]],
                            fmt="none", ecolor="0.25", elinewidth=1.4, capsize=3, zorder=4,
                        )
                    else:
                        print(f"  [bands] {arm} ΔV(t={i+1}): CI unbounded, error bar omitted")

        ax.axhline(0, color="0.25", lw=1.4, zorder=2)
        ax.axvline(FC.K + 0.5, color="0.55", ls="--", lw=1.2, zorder=0)
        ax.text(FC.K + 0.5, ylim[1] * 0.94, " Disclosure", color="0.4", fontsize=11, va="top")
        ax.set_xticks(rounds)
        ax.set_xlabel("Round $t$")
        ax.set_title(title)
        ax.set_ylim(*ylim)
        ax.set_xlim(0.4, FC.R + 0.6)

    # value labels on the two load-bearing withhold bars (rise at t=1, crash at
    # t=4), both panels. No arrows: the sign is legible from the bar alone.
    woff = (ARMS.index("withhold") - 0.5) * w
    for ax, src in ((axes[0], emp), (axes[1], mod)):
        for t in (1, 4):
            v = src["withhold"][t - 1]
            va, dy = ("bottom", 0.06) if v > 0 else ("top", -0.06)
            ax.text(
                t + woff, v + dy, f"{v:+.2f}", ha="center", va=va,
                fontsize=10.5, color=FC.ARM_COLOR["withhold"], fontweight="bold",
            )

    axes[0].set_ylabel("$\\Delta V(t) = V(t) - V(t{-}1)$   (nats)")
    axes[0].legend(frameon=False, loc="upper left")

    fig.tight_layout()
    fig.savefig(args.out)
    print(f"wrote {args.out}")

    print("\n  arm        n   " + "  ".join(f"t={t}" for t in rounds) + "     Sum")
    for arm in ARMS:
        e, m = emp[arm], mod[arm]
        print(f"  {arm:9s} {ns[arm]:2d}   emp " + "  ".join(f"{v:+.2f}" for v in e) + f"   {e.sum():+.3f}")
        print(f"  {'':9s}      mod " + "  ".join(f"{v:+.2f}" for v in m) + f"   {m.sum():+.3f}")
    print("\n  model Sum = -0.9717 both arms (eq. 12); empirical Sum differs by the rhetoric residual.")


if __name__ == "__main__":
    main()
