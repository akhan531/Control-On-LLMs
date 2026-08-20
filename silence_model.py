"""
silence_model.py — closed-form beliefs for Task 2.4 (silence-conditioning in LLM observers).

Implements the three beliefs of silence_probe_spec.md §2 plus the V-decomposition of §2.1.

Design commitments carried from the spec:
  - All belief mass computed as exact rationals (fractions.Fraction). Floats appear only at the
    log-odds / KL boundary, where a log is unavoidable.
  - Log-odds are target versus the AGGREGATE of all non-targets, so the statistic is scalar for
    every m.
  - b_pos and b^t are distinct objects. b_pos is a per-cell scale constant computed from
    (m, p, r, k). b^t is the silence-blind tracker. They coincide in the three partial conditions
    and do not in FULL. See Cell.b_t_logodds.

Scenario (spec §1): one of m candidate causes is responsible, uniform prior. N analysts each run
one assay; P(POSITIVE | target) = p, P(POSITIVE | non-target) = r, with p > r. An analyst files a
report only on POSITIVE, and additionally fails to file with probability delta regardless of result.

No network, no model calls. Pure arithmetic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

__all__ = [
    "Cell",
    "Condition",
    "FULL",
    "PARTIAL_BLIND",
    "PARTIAL_RULED",
    "logodds",
    "kl",
    "silence_coefficient",
]

# --------------------------------------------------------------------------------------
# Conditions
# --------------------------------------------------------------------------------------

FULL = "FULL"
PARTIAL_BLIND = "PARTIAL-BLIND"
PARTIAL_RULED = "PARTIAL-RULED"

Condition = str


# --------------------------------------------------------------------------------------
# Core numerics
# --------------------------------------------------------------------------------------


def _normalize(weights: Sequence[Fraction]) -> List[Fraction]:
    """Exact normalization of a non-negative weight vector."""
    total = sum(weights, Fraction(0))
    if total == 0:
        raise ValueError("degenerate belief: all weights zero")
    return [w / total for w in weights]


def logodds(dist: Sequence[Fraction], target: int = 0) -> float:
    """
    Log-odds of `target` against the aggregate of all other outcomes.

    Exact until the log. Returns +inf / -inf on a degenerate distribution rather than raising,
    so a caller sweeping a grid gets a diagnosable value instead of a traceback; the grid in
    spec §5 contains no such cell and the verification suite asserts that.
    """
    p_t = dist[target]
    p_rest = Fraction(1) - p_t
    if p_t == 0:
        return float("-inf")
    if p_rest == 0:
        return float("inf")
    return math.log(p_t / p_rest)


def kl(p: Sequence[Fraction], q: Sequence[Fraction]) -> float:
    """
    KL divergence D(p || q) in nats over the full m-ary simplex.

    Not the binarized target-vs-rest version: the V-decomposition of spec §2.1 is a statement
    about the full belief, and for m > 2 the two differ. At m = 2 they coincide, which is why
    the §2.1 table reproduces either way.
    """
    if len(p) != len(q):
        raise ValueError("KL over distributions of different support size")
    total = 0.0
    for pi, qi in zip(p, q):
        if pi == 0:
            continue
        if qi == 0:
            return float("inf")
        total += float(pi) * math.log(float(pi) / float(qi))
    return total


# --------------------------------------------------------------------------------------
# The cell
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Cell:
    """
    One point of the design grid: a scenario plus an observed record.

    Attributes
    ----------
    m : number of candidate causes, uniform prior 1/m. Index 0 is the target by convention;
        label assignment (which printed label is index 0) is a stimulus-level concern and is
        handled in silence_stimuli.py, not here.
    p : P(POSITIVE | target)
    r : P(POSITIVE | non-target)
    N : number of analysts
    k : number of filed reports in the record. Per spec §1.1 these are exactly the k positives
        and the N-k absentees are all genuine NEGATIVEs: the record contains silence but no
        actual dropout.
    delta : stated dropout rate in the disclosure rule. Enters q^t only. Note this is the
        STATED delta; actual dropout in the constructed record is always zero (§1.1). This is
        deliberate and is why the Pythagorean identity holds at delta = 0 and not at delta > 0.
    """

    m: int
    p: Fraction
    r: Fraction
    N: int
    k: int
    delta: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        if self.m < 2:
            raise ValueError("m must be at least 2")
        if not (0 < self.p < 1) or not (0 < self.r < 1):
            raise ValueError("p and r must lie strictly in (0, 1)")
        if self.p <= self.r:
            raise ValueError("spec §1 requires p > r; silence must argue against the target")
        if not (0 <= self.k <= self.N):
            raise ValueError("k must lie in [0, N]")
        if not (0 <= self.delta < 1):
            raise ValueError("delta must lie in [0, 1)")

    # -- likelihood table ---------------------------------------------------------------

    @property
    def likelihoods(self) -> List[Fraction]:
        """L(a) = P(POSITIVE | a), index 0 the target."""
        return [self.p] + [self.r] * (self.m - 1)

    # -- the three beliefs, spec §2 -----------------------------------------------------

    @property
    def b_pos(self) -> List[Fraction]:
        """Positives-only belief: b_pos(a) proportional to (1/m) L(a)^k."""
        w = [L**self.k for L in self.likelihoods]
        return _normalize(w)

    @property
    def q_t(self) -> List[Fraction]:
        """
        Silence-aware posterior under the STATED rule:
            q^t(a) proportional to (1/m) [(1-delta)L(a)]^k [1 - (1-delta)L(a)]^(N-k)
        """
        c = Fraction(1) - self.delta
        w = [(c * L) ** self.k * (Fraction(1) - c * L) ** (self.N - self.k) for L in self.likelihoods]
        return _normalize(w)

    @property
    def b_star(self) -> List[Fraction]:
        """
        Full-information posterior: every outcome written down.
            b*(a) proportional to (1/m) L(a)^k [1 - L(a)]^(N-k)
        Equals q^t exactly when delta = 0.
        """
        w = [L**self.k * (Fraction(1) - L) ** (self.N - self.k) for L in self.likelihoods]
        return _normalize(w)

    def b_t(self, condition: Condition) -> List[Fraction]:
        """
        The silence-blind tracker b^t, which is CONDITION-DEPENDENT and is not b_pos.

        In the three partial conditions the observer sees only the filed reports, so an observer
        ignoring the informational content of non-disclosure holds b_pos.

        In FULL there is no non-disclosure to ignore: every outcome is displayed, so the
        silence-blind tracker and the full-information posterior are the same object, b*. This
        is the distinction an earlier draft of the spec collapsed, and it is why FULL's
        epsilon is 0.
        """
        if condition == FULL:
            return self.b_star
        if condition in (PARTIAL_BLIND, PARTIAL_RULED):
            return self.b_pos
        raise ValueError(f"unknown condition: {condition!r}")

    # -- log-odds views -----------------------------------------------------------------

    @property
    def b_pos_logodds(self) -> float:
        return logodds(self.b_pos)

    @property
    def q_t_logodds(self) -> float:
        return logodds(self.q_t)

    @property
    def b_star_logodds(self) -> float:
        return logodds(self.b_star)

    def b_t_logodds(self, condition: Condition) -> float:
        return logodds(self.b_t(condition))

    # -- the statistic, spec §6 ---------------------------------------------------------

    @property
    def denominator(self) -> float:
        """
        q^t_logodds - b_pos_logodds. One denominator for every condition.

        Negative throughout this design, because q^t always sits BELOW b_pos whenever p > r
        (spec §3): silence always argues against the target. The sign is preserved rather than
        taken in absolute value, so that s = 1 means "at q^t" in every cell regardless of
        direction. `denominator_nats` below is the magnitude used as Figure 3's x-axis.
        """
        return self.q_t_logodds - self.b_pos_logodds

    @property
    def denominator_nats(self) -> float:
        """Magnitude of the denominator. Figure 3's x-axis."""
        return abs(self.denominator)

    @property
    def is_flip(self) -> bool:
        """
        True when b_pos and q^t fall on opposite sides of even.

        These cells are reported separately and never averaged in (spec §12): the positives-only
        belief and the silence-aware posterior name different causes as most likely from an
        identical record.
        """
        return (self.b_pos_logodds > 0) != (self.q_t_logodds > 0)

    def correct_answer(self, condition: Condition) -> List[Fraction]:
        """The belief a competent observer holds in this condition (spec §3)."""
        if condition == FULL:
            return self.b_star
        if condition == PARTIAL_BLIND:
            return self.b_pos
        if condition == PARTIAL_RULED:
            return self.q_t
        raise ValueError(f"unknown condition: {condition!r}")

    # -- V-decomposition, spec §2.1 -----------------------------------------------------

    def epsilon(self, condition: Condition) -> float:
        """eps = D(q^t || b^t). Zero in FULL because the disclosure map is content-independent."""
        if condition == FULL:
            return kl(self.b_star, self.b_star)
        return kl(self.q_t, self.b_t(condition))

    def w_bar(self, condition: Condition) -> float:
        """W-bar = D(b* || q^t). Zero at delta = 0, where q^t = b* exactly."""
        if condition == FULL:
            return 0.0
        return kl(self.b_star, self.q_t)

    def d_star_to_tracker(self, condition: Condition) -> float:
        """D(b* || b^t). At delta = 0 this equals eps + W-bar exactly (Pythagorean)."""
        return kl(self.b_star, self.b_t(condition))


def silence_coefficient(cell: Cell, probe_logodds: float) -> float:
    """
    Silence-reading coefficient, spec §6:

        s = (probe_logodds - b_pos_logodds) / (q^t_logodds - b_pos_logodds)

    s = 0 is exactly the positives-only belief; s = 1 is the silence-aware posterior. Both
    endpoints computed, never estimated.

    FULL is scored with the delta = 0 cell's denominator, since q^t = b* there and the two
    conditions then sit on an identical ruler. Callers must pass the delta = 0 Cell for FULL;
    this function does not silently substitute one, because doing so would hide a caller bug.
    """
    denom = cell.denominator
    if denom == 0:
        raise ValueError("zero denominator: b_pos and q^t coincide; not a valid measurement cell")
    return (probe_logodds - cell.b_pos_logodds) / denom


def abs_error_nats(cell: Cell, condition: Condition, probe_logodds: float) -> float:
    """
    Mandatory companion statistic (spec §6): absolute error in nats against this condition's
    OWN correct answer.

    s measures only projection onto the b_pos -> q^t line, so a probe answering 0.5 everywhere
    lands near s = 0 by accident and looks like a clean failure. This catches off-line garbage
    that s cannot see.
    """
    return abs(probe_logodds - logodds(cell.correct_answer(condition)))
