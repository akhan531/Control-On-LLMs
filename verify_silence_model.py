"""
verify_silence_model.py — verification suite for silence_model.py.

Two jobs:
  1. Reproduce every published value in silence_probe_spec.md §5 (all three blocks) and §2.1.
  2. Assert the structural identities the design leans on, which is the part that matters:
     a table can be reproduced by a wrong model that happens to agree at eight points, but
     b* == q^t at delta = 0 for arbitrary (m, p, r, N, k) cannot.

Exit code 0 on success. Any failure is loud and names the cell.
"""

from __future__ import annotations

import itertools
import math
import sys
from fractions import Fraction as F

from silence_model import (
    FULL,
    PARTIAL_BLIND,
    PARTIAL_RULED,
    Cell,
    abs_error_nats,
    logodds,
    silence_coefficient,
)

TOL = 5e-4  # spec tables are printed to 3 decimal places


class Failures:
    def __init__(self) -> None:
        self.items: list[str] = []

    def check(self, label: str, got: float, want: float, tol: float = TOL) -> None:
        if math.isnan(got) or abs(got - want) > tol:
            self.items.append(f"  {label}: got {got:.6f}, spec says {want:.6f}")

    def check_true(self, label: str, cond: bool) -> None:
        if not cond:
            self.items.append(f"  {label}: assertion failed")

    def report(self, section: str) -> None:
        if self.items:
            print(f"FAIL {section}")
            for i in self.items:
                print(i)
        else:
            print(f"ok   {section}")


# ======================================================================================
# §5 Block 1 — CORE. m=2, p/r = 0.60/0.40, N=9
# ======================================================================================
# columns: k, delta, b_pos, q^t, b*, denom, P(tgt) b_pos, P(tgt) q^t, flip

BLOCK1 = [
    (0, F(0),      0.000, -3.649, -3.649, 3.649, 0.500, 0.025, False),
    (0, F(3, 10),  0.000, -1.946, -3.649, 1.946, 0.500, 0.125, False),
    (2, F(0),      0.811, -2.027, -2.027, 2.838, 0.692, 0.116, True),
    (2, F(3, 10),  0.811, -0.703, -2.027, 1.514, 0.692, 0.331, True),
    (4, F(0),      1.622, -0.405, -0.405, 2.027, 0.835, 0.400, True),
    (4, F(3, 10),  1.622,  0.541, -0.405, 1.081, 0.835, 0.632, False),
    (6, F(0),      2.433,  1.216,  1.216, 1.216, 0.919, 0.771, False),
    (6, F(3, 10),  2.433,  1.784,  1.216, 0.649, 0.919, 0.856, False),
]


def verify_block1() -> Failures:
    f = Failures()
    for k, d, b_pos, q_t, b_star, denom, p_bpos, p_qt, flip in BLOCK1:
        c = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=k, delta=d)
        tag = f"B1 k={k} d={float(d)}"
        f.check(f"{tag} b_pos", c.b_pos_logodds, b_pos)
        f.check(f"{tag} q^t", c.q_t_logodds, q_t)
        f.check(f"{tag} b*", c.b_star_logodds, b_star)
        f.check(f"{tag} denom", c.denominator_nats, denom)
        f.check(f"{tag} P(tgt) b_pos", float(c.b_pos[0]), p_bpos)
        f.check(f"{tag} P(tgt) q^t", float(c.q_t[0]), p_qt)
        f.check_true(f"{tag} flip={flip}", c.is_flip == flip)
    return f


# ======================================================================================
# §5 Block 2 — ALPHABET. m in {3,4}, p/r = 0.60/0.40, N=9, k in {2,6}
# ======================================================================================

BLOCK2 = [
    (3, 2, F(0),     0.118, -2.720, 2.838, True),
    (3, 2, F(3, 10), 0.118, -1.396, 1.514, True),
    (3, 6, F(0),     1.740,  0.523, 1.216, False),
    (3, 6, F(3, 10), 1.740,  1.091, 0.649, False),
    (4, 2, F(0),    -0.288, -3.126, 2.838, False),
    (4, 2, F(3, 10), -0.288, -1.801, 1.514, False),
    (4, 6, F(0),     1.334,  0.118, 1.216, False),
    (4, 6, F(3, 10), 1.334,  0.686, 0.649, False),
]


def verify_block2() -> Failures:
    f = Failures()
    for m, k, d, b_pos, q_t, denom, flip in BLOCK2:
        c = Cell(m=m, p=F(3, 5), r=F(2, 5), N=9, k=k, delta=d)
        tag = f"B2 m={m} k={k} d={float(d)}"
        f.check(f"{tag} b_pos", c.b_pos_logodds, b_pos)
        f.check(f"{tag} q^t", c.q_t_logodds, q_t)
        f.check(f"{tag} denom", c.denominator_nats, denom)
        f.check_true(f"{tag} flip={flip}", c.is_flip == flip)
    return f


# ======================================================================================
# §5 Block 3 — STRENGTH. m=2, p/r = 0.70/0.30, N=5, k in {1,3}
# ======================================================================================

BLOCK3 = [
    (1, F(0),      0.847, -2.542, 3.389, True),
    (1, F(3, 10),  0.847, -0.903, 1.750, True),
    (3, F(0),      2.542,  0.847, 1.695, False),
    (3, F(3, 10),  2.542,  1.667, 0.875, False),
]


def verify_block3() -> Failures:
    f = Failures()
    for k, d, b_pos, q_t, denom, flip in BLOCK3:
        c = Cell(m=2, p=F(7, 10), r=F(3, 10), N=5, k=k, delta=d)
        tag = f"B3 k={k} d={float(d)}"
        f.check(f"{tag} b_pos", c.b_pos_logodds, b_pos)
        f.check(f"{tag} q^t", c.q_t_logodds, q_t)
        f.check(f"{tag} denom", c.denominator_nats, denom)
        f.check_true(f"{tag} flip={flip}", c.is_flip == flip)
    return f


# ======================================================================================
# §2.1 V-decomposition at the core cell m=2, k=4, N=9
# ======================================================================================

VDEC = [
    # condition, delta, epsilon, W-bar, D(b*||b^t)
    (FULL,          F(0),     0.0000, 0.0000, 0.0000),
    (PARTIAL_BLIND, F(0),     0.4804, 0.0000, 0.4804),
    (PARTIAL_RULED, F(0),     0.4804, 0.0000, 0.4804),
    (PARTIAL_RULED, F(3, 10), 0.1192, 0.1103, 0.4804),
]


def verify_vdecomposition() -> Failures:
    f = Failures()
    for cond, d, eps, wbar, dstar in VDEC:
        c = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=4, delta=d)
        tag = f"V {cond} d={float(d)}"
        f.check(f"{tag} epsilon", c.epsilon(cond), eps)
        f.check(f"{tag} W-bar", c.w_bar(cond), wbar)
        f.check(f"{tag} D(b*||b^t)", c.d_star_to_tracker(cond), dstar)

    # PARTIAL-BLIND and PARTIAL-RULED delta=0 identical in every V-quantity.
    # This is the design's strongest control (spec §2.1) and must hold exactly, not to tolerance.
    c0 = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=4, delta=F(0))
    f.check_true(
        "V BLIND == RULED(d=0) in every V-quantity",
        c0.epsilon(PARTIAL_BLIND) == c0.epsilon(PARTIAL_RULED)
        and c0.w_bar(PARTIAL_BLIND) == c0.w_bar(PARTIAL_RULED)
        and c0.d_star_to_tracker(PARTIAL_BLIND) == c0.d_star_to_tracker(PARTIAL_RULED),
    )

    # epsilon falls as delta rises: the delta>0 condition is a smaller inference over a noisier
    # channel, not the same task made harder.
    c3 = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=4, delta=F(3, 10))
    f.check_true(
        "V epsilon falls when delta rises",
        c3.epsilon(PARTIAL_RULED) < c0.epsilon(PARTIAL_RULED),
    )
    return f


# ======================================================================================
# Structural identities — the part a coincidentally-agreeing wrong model cannot pass
# ======================================================================================

SWEEP = [
    (m, F(pn, 10 if pn < 10 else 100), F(rn, 10 if rn < 10 else 100), N, k)
    for m in (2, 3, 4, 5)
    # includes a near-degenerate narrow-gap pair (0.55 vs 0.45), where silence is barely
    # informative and the denominator is small, and a wide pair (0.9 vs 0.1) where q^t runs to
    # tens of nats. Both are outside the design grid and are here precisely to stress the model
    # where the grid does not.
    for pn, rn in ((6, 4), (7, 3), (9, 1), (55, 45))
    for N in (1, 2, 5, 9, 13)
    for k in range(0, N + 1)
]


def _valid(m: int, p: F, r: F, N: int, k: int) -> bool:
    return 0 < r < p < 1 and 0 <= k <= N and m >= 2


def verify_identities() -> Failures:
    f = Failures()
    tested = 0

    for m, p, r, N, k in SWEEP:
        if not _valid(m, p, r, N, k):
            continue
        tested += 1

        c0 = Cell(m=m, p=p, r=r, N=N, k=k, delta=F(0))

        # (1) At delta = 0, q^t IS b*, exactly, as rationals. Not to tolerance.
        if c0.q_t != c0.b_star:
            f.items.append(f"  identity q^t==b* at delta=0 broken at m={m} p={p} r={r} N={N} k={k}")

        # (2) Pythagorean decomposition at delta = 0: eps + W-bar == D(b*||b^t).
        lhs = c0.epsilon(PARTIAL_RULED) + c0.w_bar(PARTIAL_RULED)
        rhs = c0.d_star_to_tracker(PARTIAL_RULED)
        if abs(lhs - rhs) > 1e-12:
            f.items.append(
                f"  Pythagorean identity broken at m={m} p={p} r={r} N={N} k={k}: "
                f"{lhs:.12f} != {rhs:.12f}"
            )

        # (3) FULL has zero epsilon and zero W-bar: the disclosure map is content-independent.
        if c0.epsilon(FULL) != 0.0 or c0.w_bar(FULL) != 0.0:
            f.items.append(f"  FULL V-quantities nonzero at m={m} p={p} r={r} N={N} k={k}")

        # (4) Silence argues against the target whenever p > r and some analyst is absent.
        #     Equality only when k == N (nothing is absent).
        if k < N:
            if not c0.q_t_logodds < c0.b_pos_logodds:
                f.items.append(f"  q^t not below b_pos at m={m} p={p} r={r} N={N} k={k}")
        elif c0.q_t != c0.b_pos:
            f.items.append(f"  q^t != b_pos when k==N at m={m} p={p} r={r} N={N} k={k}")

        # (5) b_pos does not depend on N or delta. It is a per-cell scale constant of (m,p,r,k).
        for N2 in (N, N + 1, N + 4):
            for d2 in (F(0), F(3, 10), F(1, 2)):
                if k <= N2:
                    c2 = Cell(m=m, p=p, r=r, N=N2, k=k, delta=d2)
                    if c2.b_pos != c0.b_pos:
                        f.items.append(f"  b_pos varies with N or delta at m={m} k={k}")

        # (6) Empty record, k = 0: b_pos is exactly uniform, so its log-odds is log(1/(m-1)).
        if k == 0:
            want = math.log(1.0 / (m - 1))
            if abs(c0.b_pos_logodds - want) > 1e-12:
                f.items.append(f"  b_pos at k=0 not uniform at m={m}")

        # (7) delta = 0 is the limit of delta -> 0, checked by CONVERGENCE RATE rather than by a
        #     fixed epsilon. A fixed tolerance is the wrong instrument here: dq^t/ddelta scales
        #     with N/(1-p), so at p=0.9, N=13 the cell sits near -28 nats and a correct model
        #     legitimately moves ~1e-4 for delta=1e-6. What actually distinguishes continuity
        #     from a sign error in the (1-delta) factor is that the gap shrinks LINEARLY in
        #     delta; a sign error leaves an O(1) offset that does not shrink at all.
        gaps = [
            abs(Cell(m=m, p=p, r=r, N=N, k=k, delta=F(1, 10**e)).q_t_logodds - c0.q_t_logodds)
            for e in (7, 8)
        ]
        if gaps[0] > 1e-12 and not gaps[1] < 0.2 * gaps[0]:
            f.items.append(
                f"  q^t not first-order continuous at delta=0 for m={m} p={p} r={r} N={N} k={k}: "
                f"gap {gaps[0]:.3e} -> {gaps[1]:.3e} (expected ~10x shrink)"
            )

    # (8) Monotonicity in delta: more stated dropout means weaker evidence from silence, so q^t
    #     moves back toward b_pos. Checked on the core cell family.
    for k in (0, 2, 4, 6):
        prev = None
        for dn in (0, 1, 2, 3, 4, 5):
            c = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=k, delta=F(dn, 10))
            gap = c.b_pos_logodds - c.q_t_logodds
            if prev is not None and gap > prev + 1e-12:
                f.items.append(f"  denominator not shrinking in delta at k={k}, delta={dn/10}")
            prev = gap

    # (9) The statistic recovers its endpoints exactly.
    c = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=4, delta=F(3, 10))
    f.check("s at b_pos", silence_coefficient(c, c.b_pos_logodds), 0.0, 1e-12)
    f.check("s at q^t", silence_coefficient(c, c.q_t_logodds), 1.0, 1e-12)

    # (10) Absolute error is zero at each condition's own correct answer.
    for cond, ans in (
        (FULL, c.b_star_logodds),
        (PARTIAL_BLIND, c.b_pos_logodds),
        (PARTIAL_RULED, c.q_t_logodds),
    ):
        f.check(f"abs_error zero at {cond} truth", abs_error_nats(c, cond, ans), 0.0, 1e-12)

    print(f"     ({tested} parameter combinations swept)")
    return f


# ======================================================================================
# Grid-level facts the spec asserts in prose
# ======================================================================================


def verify_grid_facts() -> Failures:
    f = Failures()

    def cells():
        for k in (0, 2, 4, 6):
            for d in (F(0), F(3, 10)):
                yield Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=k, delta=d)
        for m in (3, 4):
            for k in (2, 6):
                for d in (F(0), F(3, 10)):
                    yield Cell(m=m, p=F(3, 5), r=F(2, 5), N=9, k=k, delta=d)
        for k in (1, 3):
            for d in (F(0), F(3, 10)):
                yield Cell(m=2, p=F(7, 10), r=F(3, 10), N=5, k=k, delta=d)

    all_cells = list(cells())

    # "Seven cells put b_pos and q^t on opposite sides of even."
    flips = [c for c in all_cells if c.is_flip]
    f.check_true(f"seven flip cells (found {len(flips)})", len(flips) == 7)

    # "The smallest denominator in the grid is 0.649 nats."
    smallest = min(c.denominator_nats for c in all_cells)
    f.check("smallest denominator", smallest, 0.649)

    # "delta = 0 spans 1.216-3.649 nats, delta = 0.3 spans 0.649-1.946."
    d0 = [c.denominator_nats for c in all_cells if c.delta == 0]
    d3 = [c.denominator_nats for c in all_cells if c.delta != 0]
    f.check("delta=0 min denom", min(d0), 1.216)
    f.check("delta=0 max denom", max(d0), 3.649)
    f.check("delta=0.3 min denom", min(d3), 0.649)
    f.check("delta=0.3 max denom", max(d3), 1.946)

    # "k = 8 excluded: it puts b_pos at 3.24 nats, inside the 2.1f saturation ceiling."
    c8 = Cell(m=2, p=F(3, 5), r=F(2, 5), N=9, k=8, delta=F(0))
    f.check("k=8 b_pos (excluded cell)", c8.b_pos_logodds, 3.243, 5e-3)

    # No cell in the grid has a zero or infinite denominator.
    f.check_true(
        "all denominators finite and nonzero",
        all(math.isfinite(c.denominator) and c.denominator != 0 for c in all_cells),
    )

    # Every |q^t| stays within roughly 3 nats, per the 2.1f expressibility ceiling.
    worst = max(abs(c.q_t_logodds) for c in all_cells)
    f.check_true(f"|q^t| within 3.7 nats (worst {worst:.3f})", worst < 3.7)
    return f


# ======================================================================================

def main() -> int:
    print("verify_silence_model.py — against silence_probe_spec.md\n")
    results = [
        ("§5 Block 1 CORE", verify_block1()),
        ("§5 Block 2 ALPHABET", verify_block2()),
        ("§5 Block 3 STRENGTH", verify_block3()),
        ("§2.1 V-decomposition", verify_vdecomposition()),
        ("§5 grid-level facts", verify_grid_facts()),
        ("structural identities", verify_identities()),
    ]
    for name, f in results:
        f.report(name)
    failed = sum(len(f.items) for _, f in results)
    print()
    if failed:
        print(f"FAILED: {failed} discrepancies. Nothing downstream may be built on this model.")
        return 1
    print("PASSED: model reproduces the spec exactly. Safe to build stimuli against.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
