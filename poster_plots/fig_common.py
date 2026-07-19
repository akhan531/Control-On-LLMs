"""Shared loader and style for the Task 1.14d poster figures.

Fig 1 (trajectory), Fig 2 (credit), Fig 3 (dV) all import from here so that
the group-belief instrument is defined in exactly one place.

THE INSTRUMENT (Ali's verdict 2026-07-16, logged in Task 1.14c)
--------------------------------------------------------------
b^t is the belief of someone holding only the DISCLOSED evidence. That is
what the model's eq. (1) computes, so it is what the empirical panel has to
measure. The per-agent beliefs are NOT that object: agent 4 holds the
pivotal clue privately through the plateau, so averaging the agents in
measures a mixture of public and private information. On the withhold
plateau the model's b^t gives V = 2.5919 while the average of four
model-obedient private beliefs gives 1.0997, a 1.49-nat gap opened before a
single token of rhetoric.

So the instrument is the OBSERVER PROBE: a fresh context each round, given
the public record only, no clue, no memory. It is pre-registered in the
harness (meta.group_belief_instrument == "observer_probe").

AVERAGE-THEN-KL, AND WHY THERE IS NO EPSILON FLOOR
--------------------------------------------------
We average the observer's probability vector across seeds and take ONE KL
against b*. We do not take per-seed KLs and average those. Two independent
reasons, both measured on the 40-seed data:

  1. Per-seed KL is undefined on ~30% of the data. 57/200 honest and 62/200
     withhold per-seed observer-rounds carry a hard zero on some coordinate,
     which sends D(b*||b) to +infinity. The seed-average has full support
     everywhere (smallest averaged coordinate anywhere = 0.005), so
     average-then-KL needs NO epsilon floor at all. The floor and its
     sensitivity table, required by the 1.14d spec on the basis of the old
     1.0a data, are simply not needed under this recipe. This module
     ASSERTS positivity rather than flooring it, so a future run that breaks
     the property fails loudly instead of silently absorbing a fudge factor.

  2. Per-seed V is mostly quantization. The LLM reports probabilities on a
     coarse ~0.05 grid and reverse-KL is hypersensitive to the Chen
     coordinate (b*(Chen) = 0.9756 dominates the sum). Near the plateau one
     0.05 report quantum is worth ~0.497 nats at the seed level. Across 40
     withhold seeds, round 5 takes only 2 distinct V values. Averaging the
     probability vector first dissolves this: the same quantum is worth
     0.016 nats on an n=40 mean.

CONVENTIONS
-----------
  t = 0..R, close-of-round (notation table + Q25, corrected 2026-07-16).
  b^0 = pi, so V(0) = D(b*||pi) = 0.9717 is SHARED by every arm and by both
  panels. Fig 1 anchors there.
  V in nats throughout.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import model_sim as M

ANSWERS = list(M.ANSWERS)  # ("Alvarez", "Boyd", "Chen")
B_STAR = np.array([float(x) for x in M.B_STAR])
R = M.R  # 5
K = M.K  # 4

# ----------------------------------------------------------------------
# Style. One place, so all three figures match at print size.
# ----------------------------------------------------------------------

ARM_COLOR = {
    "honest": "#1b7837",     # green
    "withhold": "#b2182b",   # red
    "never": "#4d4d4d",      # grey
}
ARM_LABEL = {
    "honest": "Honest ($\\tau_4=1$)",
    "withhold": "Withhold ($\\tau_4=4$)",
    "never": "Never ($\\tau_4=\\infty$)",
}

POSTER_RC = {
    "font.size": 13,
    "axes.titlesize": 15,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 110,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "lines.linewidth": 2.4,
    "lines.markersize": 7,
}


# ----------------------------------------------------------------------
# Core
# ----------------------------------------------------------------------


def kl(p: np.ndarray, q: np.ndarray) -> float:
    """D(p || q) in nats. Called as kl(B_STAR, b), i.e. reverse KL (L0)."""
    return float(np.sum(p * np.log(p / q)))


def load(path: str | Path) -> dict:
    """Load a 1.14c results JSON and check it is the run we think it is."""
    d = json.loads(Path(path).read_text())
    meta = d["meta"]
    assert meta["task"] == "1.14c", f"not a 1.14c results file: task={meta['task']}"
    assert meta["group_belief_instrument"] == "observer_probe", (
        "this loader measures the observer probe; "
        f"file declares instrument={meta['group_belief_instrument']}"
    )
    assert meta["epsilon_floor"] is None, (
        "harness applied a floor; the 1.14d recipe expects raw normalized probabilities"
    )
    got = np.array([meta["b_star"][a] for a in ANSWERS])
    assert np.allclose(got, B_STAR, atol=1e-12), (
        f"file b* {got} disagrees with model_sim b* {B_STAR}; "
        "the instantiation moved and the figure would be comparing two models"
    )
    return d


def observer_matrix(runs: list[dict], t: int) -> np.ndarray:
    """(n_seeds, 3) of the observer's probability vector at round t.

    t = 0 reads the pre-debate calibration probe; t >= 1 reads the round record.
    """
    if t == 0:
        rows = [[r["observer_t0"][a] for a in ANSWERS] for r in runs]
    else:
        rows = [
            [rd["observer"][a] for a in ANSWERS]
            for r in runs
            for rd in r["rounds"]
            if rd["round"] == t
        ]
    M_ = np.array(rows, dtype=float)
    assert M_.shape[0] == len(runs), f"missing observer rows at t={t}"
    assert np.allclose(M_.sum(axis=1), 1.0, atol=1e-6), f"unnormalized observer at t={t}"
    return M_


def empirical_V(runs: list[dict]) -> np.ndarray:
    """V(t) for t = 0..R by average-then-KL. No epsilon floor; positivity asserted."""
    out = []
    for t in range(R + 1):
        m = observer_matrix(runs, t).mean(axis=0)
        assert (m > 0).all(), (
            f"a seed-averaged coordinate hit zero at t={t}: {m}. "
            "Average-then-KL relies on the average having full support. "
            "Do not add a floor without re-deriving the sensitivity table."
        )
        out.append(kl(B_STAR, m))
    return np.array(out)


def model_V(arm: str) -> np.ndarray:
    """V(t) for t = 0..R from the frozen instantiation. Nominal arm schedule."""
    _, Vs, _ = M.trajectory(M.ARMS[arm])
    return np.array(Vs)


def bootstrap_V(runs: list[dict], B: int = 4000, seed: int = 0):
    """Percentile CI on the average-then-KL curve, resampling seeds.

    Returns (lo, hi, n_degenerate) each length R+1. A resample whose mean has
    a zero coordinate has V = +inf and is counted, not dropped: dropping it
    would bias the interval down. Where n_degenerate > 0 the upper limit is
    genuinely unbounded and the caller should not draw a band.
    """
    rng = np.random.default_rng(seed)
    n = len(runs)
    lo, hi, deg = [], [], []
    for t in range(R + 1):
        M_ = observer_matrix(runs, t)
        stats, bad = [], 0
        for _ in range(B):
            m = M_[rng.integers(0, n, n)].mean(axis=0)
            if (m <= 0).any():
                bad += 1
            else:
                stats.append(kl(B_STAR, m))
        deg.append(bad)
        if bad:
            lo.append(np.nan)
            hi.append(np.nan)
        else:
            a, b = np.percentile(stats, [2.5, 97.5])
            lo.append(a)
            hi.append(b)
    return np.array(lo), np.array(hi), np.array(deg)


def realized_matches_nominal(runs: list[dict]) -> bool:
    """The arms are scripted, so realized tau should equal nominal tau."""
    return all(r["realized_tau_by_clue"] == r["tau_by_clue"] for r in runs)
