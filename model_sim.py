"""
model_sim.py -- Task 1.14b. Forward simulator for the locked concrete
instantiation of the strategic-timing model.

Single source of numbers: poster_model.md (Task 1.14a, locked 2026-07-16).
Every constant below appears there first. Equation numbers refer to the
Burlion note (Control_on_LLMs_math.pdf).

WHAT THIS IMPLEMENTS
    b^t(a) proportional to pi(a) * prod_{c in D_{1:t}} p(c|a)      eq. (1)/(3)
    b* = the same product over ALL clues                            eq. (4)
    V(t) = D(b* || b^t)          reverse KL, nats                   eq. (5)
    dV(t) = V(t) - V(t-1)        backward difference

CONVENTIONS (locked, corrected 2026-07-16)
    b^0 = pi. Close-of-round: b^t reflects every clue with tau <= t, i.e.
    round t's disclosures D_t drive b^{t-1} -> b^t. dV is therefore the
    BACKWARD difference V(t) - V(t-1), matching the 1.0b empirical sharpness
    convention V(k-1) - V(k) with sign flipped. Do not "fix" this to a
    forward difference.

NO EPSILON FLOOR
    pi has full support and every p(c|a) > 0, so b^t(a) > 0 for all t and a
    and V is finite throughout. The model needs no epsilon floor and has
    none. Any epsilon floor you see downstream is an EMPIRICAL-SIDE artifact
    of near-degenerate LLM reports (see poster_model.md section 9, 1.14d),
    not a property of the model. Keep the two separate.

ARITHMETIC
    Beliefs are exact rationals (fractions.Fraction). Floats appear only at
    the KL boundary. This buys three things:
      - b* and b^1 assert as EXACT equality against poster_model.md 5.1,
        not a tolerance;
      - identical disclosure sets produce bitwise-identical V, so C1's
        "dV = 0 exactly" is a literal == 0.0, not a near-zero;
      - the Option A verdict (levels are relative weights, only ratios
        matter) is testable exactly rather than approximately.
    numpy is used only for float output/formatting, never for the beliefs.

USE FROM DOWNSTREAM TASKS
    trajectory() takes an arbitrary schedule tau: {clue -> disclosure round}.
    The three arms are in ARMS, but 1.14d should feed it the REALIZED
    per-seed disclosure timeline logged by the 1.14c harness, not the
    nominal arm, so the model is run on what actually happened.

Run:  python model_sim.py          # tables + assertions
      python model_sim.py --test   # assertions only
      pytest model_sim.py          # same assertions under pytest
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from itertools import permutations

import numpy as np

# ----------------------------------------------------------------------
# 1. The likelihood scale                        poster_model.md 1.1
#
# Stated before any clue is assigned to a level. The ordering is the audit
# trail. Levels are RELATIVE weights, not raw probabilities (1.2, Option A,
# Ali's verdict 2026-07-16): the dynamics only ever see ratios (eq. 8/9), so
# a common per-clue constant cancels in the normalization. test_option_a
# below pins that claim.
# ----------------------------------------------------------------------

EXPECTED = F(3, 5)  # 0.600  just what you would expect if this suspect did it
UNREMARKABLE = F(3, 10)  # 0.300  could turn up either way, no real signal
DOUBTFUL = F(1, 10)  # 0.100  hard to square with this suspect, needs explaining
EXCLUDED = F(1, 1000)  # 0.001  physically impossible unless the evidence is wrong
#                              strictly positive by V2: a literal zero sends V
#                              to +inf before the debate starts

# ----------------------------------------------------------------------
# 2. The setting                                 poster_model.md 2
# ----------------------------------------------------------------------

ANSWERS = ("Alvarez", "Boyd", "Chen")  # m = 3
PI = (F(1, 3), F(1, 3), F(1, 3))  # uniform, full support
TRUTH = "Chen"  # fixed, latent. Never enters the dynamics.
N_AGENTS = 4  # symmetric, one private clue each
R = 5  # rounds
K = 4  # withhold disclosure round
# Public evidence: NONE. The prior IS the public information at t=0.

# ----------------------------------------------------------------------
# 3. The clues                                   poster_model.md 3.1
#
# FROZEN. Never tuned against LLM output. If the LLM reads a clue
# differently than its row says, that is a finding to report, not a bug to
# fix by editing the row.
# ----------------------------------------------------------------------

CLUES = ("c1", "c2", "c3", "c4")

LAM: dict[str, tuple[F, F, F]] = {
    #        Alvarez       Boyd          Chen
    "c1": (EXPECTED, UNREMARKABLE, UNREMARKABLE),  # the complaint
    "c2": (EXPECTED, UNREMARKABLE, UNREMARKABLE),  # the badge log
    "c3": (UNREMARKABLE, UNREMARKABLE, DOUBTFUL),  # the old guard
    "c4": (EXCLUDED, EXCLUDED, EXPECTED),  # the DNA (pivotal)
}

PIVOTAL = "c4"

# ----------------------------------------------------------------------
# 4. The three arms                              poster_model.md 4.2
#
# The arms differ in exactly one integer, tau_4. The matched-information
# control is stated at the level of the model, not bolted on.
# ----------------------------------------------------------------------

INF = float("inf")

ARMS: dict[str, dict[str, float]] = {
    "honest": {"c1": 1, "c2": 1, "c3": 1, "c4": 1},
    "withhold": {"c1": 1, "c2": 1, "c3": 1, "c4": K},
    "never": {"c1": 1, "c2": 1, "c3": 1, "c4": INF},
}

# ----------------------------------------------------------------------
# Core
# ----------------------------------------------------------------------


def posterior(clues, lam=LAM, pi=PI) -> tuple[F, ...]:
    """b(a) proportional to pi(a) * prod_{c in clues} p(c|a).   eq. (1)/(3)

    `clues` is a SEQUENCE, not a set: the product is over the multiset with
    multiplicity (Q6+Q7). This instantiation draws four distinct clues so
    the multiset product degenerates to a set product, but duplicates are a
    case the model covers and test_multiplicity pins the behaviour.

    Exact: returns Fractions. No epsilon floor, none needed.
    """
    w = list(pi)
    for c in clues:
        row = lam[c]
        w = [w_a * row_a for w_a, row_a in zip(w, row)]
    total = sum(w)
    return tuple(w_a / total for w_a in w)


def disclosed_upto(tau, t) -> list[str]:
    """D_{1:t}, the multiset of clues disclosed by the close of round t."""
    return [c for c in CLUES if tau.get(c, INF) <= t]


def kl(p, q) -> float:
    """D(p || q) in nats. Floats enter here and only here.

    Called as kl(b_star, b_t), i.e. REVERSE KL with the fixed target first
    (L0). Deterministic on its inputs, so equal Fraction inputs give
    bitwise-equal outputs, which is what makes C1 exact.
    """
    return float(sum(float(p_a) * math.log(float(p_a / q_a)) for p_a, q_a in zip(p, q)))


B_STAR = posterior(CLUES)  # eq. (4)


def V(b) -> float:
    """V = D(b* || b), eq. (5). Reverse KL, nats."""
    return kl(B_STAR, b)


def trajectory(tau, rounds=R):
    """Forward-simulate one schedule.

    tau: {clue -> disclosure round}, an int or float('inf'). Accepts the
    nominal arms in ARMS or a realized per-seed timeline from the 1.14c
    harness. Any clue absent from tau is treated as never disclosed.

    Returns (beliefs, Vs, dVs) with
        beliefs[t] = b^t as exact Fractions, t = 0..rounds
        Vs[t]      = V(t),                   t = 0..rounds
        dVs[i]     = dV(t) = V(t) - V(t-1),  t = i+1 = 1..rounds
    """
    beliefs = [posterior(disclosed_upto(tau, t)) for t in range(rounds + 1)]
    Vs = [V(b) for b in beliefs]
    dVs = [Vs[t] - Vs[t - 1] for t in range(1, rounds + 1)]
    return beliefs, Vs, dVs


def private_belief(own_clue, tau, t, agent_sees_own=True):
    """b_i^t, eq. (2): the public disclosed set plus the agent's own clue.

    Used for the section 6.3 fact that the withholder holds b* exactly
    through an isolated plateau.
    """
    seen = disclosed_upto(tau, t)
    if agent_sees_own and own_clue not in seen:
        seen = seen + [own_clue]
    return posterior(seen)


# ----------------------------------------------------------------------
# Assertions. These are the deliverable: "corollary assertions passing".
# ----------------------------------------------------------------------

# poster_model.md 5.1, exact rationals
B_STAR_EXACT = (F(4, 205), F(1, 205), F(200, 205))
B_ONE_WEAK_EXACT = (F(3, 4), F(3, 16), F(1, 16))

# poster_model.md 5.2, high-precision floats
V0_REF = 0.9717420693
V1_PLATEAU_REF = 2.5918734351
DV1_RISE_REF = +1.6201313658
DV4_DROP_REF = -2.5918734351
DV1_HONEST_REF = -0.9717420693

TOL = 1e-9  # only ever applied to log-valued quantities


def test_b_star_exact():
    """b* matches poster_model.md 5.1 EXACTLY, as a rational."""
    assert B_STAR == B_STAR_EXACT, B_STAR


def test_b_one_weak_exact():
    """The three-clue state b^1 under withhold/never is exactly (3/4, 3/16, 1/16).

    This is the wrong consensus: argmax is Alvarez at 0.75 while b* sits on
    Chen. It is also X-invariant (c4 is not in the product), so no choice of
    the Excluded floor can touch it.
    """
    for arm in ("withhold", "never"):
        beliefs, _, _ = trajectory(ARMS[arm])
        assert beliefs[1] == B_ONE_WEAK_EXACT, (arm, beliefs[1])
        assert ANSWERS[max(range(3), key=lambda i: beliefs[1][i])] == "Alvarez"


def test_c1_no_disclosure_means_exactly_zero():
    """C1: D_t = empty  =>  dV(t) = 0 EXACTLY.

    Literal == 0.0, not a tolerance. The plateau is a flat segment, not slow
    progress. Asserted on every silent round of every arm.
    """
    checked = 0
    for arm, tau in ARMS.items():
        _, _, dVs = trajectory(tau)
        for t in range(1, R + 1):
            if disclosed_upto(tau, t) == disclosed_upto(tau, t - 1):  # D_t empty
                assert dVs[t - 1] == 0.0, (arm, t, dVs[t - 1])
                checked += 1
    # honest t=2..5 (4), withhold t=2,3,5 (3), never t=2..5 (4)
    assert checked == 11, checked


def test_c2_full_disclosure_is_zero_and_absorbing():
    """C2: every clue out  =>  V = 0 exactly, and V stays 0."""
    _, Vs_h, _ = trajectory(ARMS["honest"])
    assert Vs_h[1] == 0.0
    assert all(v == 0.0 for v in Vs_h[1:])

    _, Vs_w, _ = trajectory(ARMS["withhold"])
    assert Vs_w[K] == 0.0
    assert all(v == 0.0 for v in Vs_w[K:])

    assert V(B_STAR) == 0.0


def test_conservation_law():
    """eq. (12): sum_t dV(t) = V(R) - V(0) = -D(b*||pi).

    Schedule-invariant. Honest and withhold have completely different
    transients and identical totals: timing changes the shape of the descent
    and not one digit of its size. This is what makes C4 rigorous rather
    than descriptive.

    The never arm is the hypothesis visibly failing: c4 is never out, so
    V(R) != 0 and the identity does not apply. Its sum is +dV(1).
    """
    _, Vs, _ = trajectory(ARMS["honest"])
    v0 = Vs[0]

    for arm in ("honest", "withhold"):
        _, Vs, dVs = trajectory(ARMS[arm])
        assert abs(sum(dVs) - (-v0)) < TOL, (arm, sum(dVs), -v0)
        assert abs(Vs[R] - Vs[0] - sum(dVs)) < TOL

    _, Vs_n, dVs_n = trajectory(ARMS["never"])
    assert Vs_n[R] != 0.0
    assert abs(sum(dVs_n) - DV1_RISE_REF) < TOL


def test_flat_likelihood_clue_is_inert():
    """A clue with equal likelihood across answers leaves b^t unchanged, exactly.

    Tests the update law directly rather than a corollary: only likelihood
    RATIOS move the state.
    """
    lam = dict(LAM)
    lam["flat"] = (UNREMARKABLE, UNREMARKABLE, UNREMARKABLE)
    base = posterior(["c1", "c2", "c3"], lam=lam)
    plus_flat = posterior(["c1", "c2", "c3", "flat"], lam=lam)
    assert base == plus_flat, (base, plus_flat)

    lam["flat2"] = (EXCLUDED, EXCLUDED, EXCLUDED)  # flat at the floor, still inert
    assert posterior(["c1", "flat2"], lam=lam) == posterior(["c1"], lam=lam)


def test_option_a_only_ratios_matter():
    """poster_model.md 1.2: the levels are relative weights, not probabilities.

    Rescaling any clue's row by a common per-answer-constant factor (which is
    what the background-existence note's single Z does) leaves b^t exactly
    unchanged. If this failed, the Option A verdict would be wrong and the
    Q6+Q7 feasibility argument would not hold.
    """
    for scale in (F(1, 100), F(7), F(1000)):
        lam = {c: tuple(x * scale for x in row) for c, row in LAM.items()}
        for arm in ARMS:
            b_ref, _, _ = trajectory(ARMS[arm])
            beliefs = [
                posterior(disclosed_upto(ARMS[arm], t), lam=lam) for t in range(R + 1)
            ]
            assert beliefs == b_ref, (scale, arm)


def test_permutation_invariance():
    """b^t depends on D_{1:t}, not on the order or the identity of disclosers.

    Exact under Fractions. This is why the model trajectory is identical
    under every per-seed permutation of which agent holds c4 (4.1): the
    randomization exists only to kill the positional halo in the EMPIRICAL
    arm.
    """
    for order in permutations(CLUES):
        assert posterior(list(order)) == B_STAR, order


def test_multiplicity():
    """The product is over the multiset, with multiplicity (Q6+Q7).

    Not exercised by this instantiation (four distinct clues) but the model
    covers it, so pin it here rather than discover it in Phase 2.
    """
    once = posterior(["c1"])
    twice = posterior(["c1", "c1"])
    assert once != twice
    # a second copy of c1 applies the same likelihood ratio a second time
    assert twice == posterior(["c1", "c2"])  # c1 and c2 have identical rows


def test_matches_poster_model_numbers():
    """The trajectories reproduce poster_model.md 5.2 to the stated precision."""
    _, Vs_h, dVs_h = trajectory(ARMS["honest"])
    _, Vs_w, dVs_w = trajectory(ARMS["withhold"])
    _, Vs_n, dVs_n = trajectory(ARMS["never"])

    assert abs(Vs_h[0] - V0_REF) < TOL
    assert abs(dVs_h[0] - DV1_HONEST_REF) < TOL

    for t in (1, 2, 3):
        assert abs(Vs_w[t] - V1_PLATEAU_REF) < TOL
        assert abs(Vs_n[t] - V1_PLATEAU_REF) < TOL
    assert abs(Vs_n[5] - V1_PLATEAU_REF) < TOL

    assert abs(dVs_w[0] - DV1_RISE_REF) < TOL
    assert abs(dVs_w[K - 1] - DV4_DROP_REF) < TOL


def test_withholder_holds_b_star():
    """5.1 of the note, Remark 4.4: agent 4's private belief IS b* on the plateau.

    The plateau is three rounds in which V(t) = 2.59 measures a gap that
    precisely one agent closed in private at round 1.
    """
    tau = ARMS["withhold"]
    for t in (1, 2, 3):
        assert private_belief(PIVOTAL, tau, t) == B_STAR, t
    # and at t=0, before anyone has spoken, it already puts ~0.997 on Chen
    b0 = private_belief(PIVOTAL, tau, 0)
    assert b0 != B_STAR
    assert float(b0[2]) > 0.99


def test_round_one_rise_is_regime_a():
    """6.1: the round-1 rise is Corollary 3 regime (a), away from b*, not overshoot.

    Closes, on the model side, the open item from 1.11 forwarded through
    1.13. The state moves toward Alvarez while b* sits on Chen: b^1(Chen) is
    BELOW pi(Chen), so it did not pass b* at all, let alone overshoot past
    the level-set reflection.
    """
    beliefs, Vs, _ = trajectory(ARMS["withhold"])
    chen = ANSWERS.index("Chen")
    assert beliefs[1][chen] < PI[chen] < B_STAR[chen]  # moved away from b*
    assert Vs[1] > Vs[0]  # left the sublevel set S_0


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def run_tests() -> int:
    failures = 0
    for t in TESTS:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL  {t.__name__}: {e}")
    return failures


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------


def fmt_belief(b) -> str:
    return "[" + "  ".join(f"{float(x):.7f}" for x in b) + "]"


def report() -> None:
    print("Task 1.14b -- model simulator for the locked instantiation")
    print("poster_model.md, locked 2026-07-16.  V in nats.  No epsilon floor.")
    print()
    print(f"  answers   {ANSWERS}   T = {TRUTH} (latent, never enters the dynamics)")
    print(f"  pi        {fmt_belief(PI)}")
    print(f"  b*        {fmt_belief(B_STAR)}   exact "
          f"({B_STAR[0]}, {B_STAR[1]}, {B_STAR[2]})   [200/205 reduces to 40/41]")
    b1 = trajectory(ARMS['withhold'])[0][1]
    print(f"  b^1 weak  {fmt_belief(b1)}   exact ({b1[0]}, {b1[1]}, {b1[2]})")
    print(f"  V(0)      {V(PI):.10f}")
    print()

    hdr = "  " + " ".join(f"{f't={t}':>9}" for t in range(R + 1))
    print("V(t) = D(b* || b^t)")
    print(f"  {'arm':<10}" + hdr)
    for arm in ARMS:
        _, Vs, _ = trajectory(ARMS[arm])
        print(f"  {arm:<10}  " + " ".join(f"{v:>9.4f}" for v in Vs))
    print()

    hdr = "  " + " ".join(f"{f't={t}':>9}" for t in range(1, R + 1))
    print("dV(t) = V(t) - V(t-1)")
    print(f"  {'arm':<10}" + hdr + f"{'sum':>12}")
    for arm in ARMS:
        _, _, dVs = trajectory(ARMS[arm])
        print(
            f"  {arm:<10}  "
            + " ".join(f"{d:>+9.4f}" for d in dVs)
            + f"{sum(dVs):>+12.4f}"
        )
    print()
    print(f"  conservation: -D(b*||pi) = {-V(PI):+.4f}   (honest, withhold)")
    print("  never sums positive: c4 never out, so eq. (12)'s hypothesis fails")
    print()

    print("assertions")
    failures = run_tests()
    print()
    if failures:
        print(f"{failures} FAILED")
    else:
        print(f"all {len(TESTS)} assertions pass")
    return failures


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(1 if run_tests() else 0)
    sys.exit(1 if report() else 0)