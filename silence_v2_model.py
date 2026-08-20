"""
silence_v2_model.py — closed-form beliefs for the silence probe v2 grid (Task 2.4b).

Everything exact in Fractions; floats appear only at the reporting boundary.

Scenario (m = 2, uniform prior)
------------------------------
One of two candidates is responsible. N analysts each run one assay, conditionally
independent given the responsible candidate, with P(POSITIVE | target) = p and
P(POSITIVE | other) = 1 - p. An analyst files a report only on POSITIVE; additionally,
with probability delta an analyst files nothing regardless of result.

    b_pos(a)  ∝  (1/2) · L(a)^k                                  positives only
    q(a)      ∝  (1/2) · [(1-d)L(a)]^k · [1 - (1-d)L(a)]^(N-k)   silence-aware
    b*(a)     ∝  (1/2) · L(a)^k · [1 - L(a)]^(N-k)               full information

At d = 0, q == b* exactly. That identity is the design's pivot: FULL and
PARTIAL-RULED(d=0) then have the SAME correct answer, and differ only in whether the
negatives are displayed or must be derived from absence.

b_pos vs b^t
------------
b^t is the theory's silence-blind tracker; b_pos is a per-cell scale constant computed
from (p, k). They coincide in the three partial conditions and do NOT in FULL, where
b^t = q = b* and b_pos is the counterfactual belief of an observer that reads the
positives and ignores the NEGATIVE lines printed beside them. The ordinal-s anchor is
b_pos precisely because it is arm-invariant (D9).

Levels
------
Bands are the wording-B values MEASURED in W1, inside which all seven configurations
agreed with the nominal cut. Every predicted belief in the grid sits inside a band, so
no cell's correct level depends on where a model's personal threshold falls (D24).
"""

from fractions import Fraction as F
import math

# --- measured wording-B safe bands (D24) -------------------------------------
BANDS = {0: (0.00, 0.20), 1: (0.40, 0.45), 2: (0.55, 0.70), 3: (0.80, 1.00)}
NOMINAL_EDGES = (F(1, 4), F(1, 2), F(3, 4))
ALT_EDGES = (F(1, 5), F(1, 2), F(4, 5))          # D20 sensitivity

# delta > 0 is DESIGNED AND BANKED, NOT RUN (D26). The primary campaign is delta = 0
# only. Set RUN_BANKED = True to emit the extension; it is a separate stimulus file with
# its own hash, so enabling it never disturbs the frozen primary freeze.
DELTA_PRIMARY = F(0)
DELTA_BANKED = F(3, 10)
DELTAS = (DELTA_PRIMARY, DELTA_BANKED)
RUN_BANKED = False

# --- the frozen grid (D25) ---------------------------------------------------
# (id, p_numerator_over_100, N, k)   p = 0.60 excluded: reserved to W1.
GRID = [
    ("A1", 81,  5, 2), ("A2", 67,  8, 3), ("A3", 67, 10, 4),    # span-3 backbone, L3
    ("A4", 62, 13, 5), ("A5", 67, 14, 5),
    ("C1", 88,  6, 2), ("C2", 79,  8, 3), ("C3", 73, 11, 4),    # count control, L3
    ("B1", 57, 11, 3), ("B2", 62,  5, 1), ("B3", 59,  8, 2),    # span-2 backbone, L2
    ("D1", 56,  5, 2), ("D2", 54,  8, 3), ("D3", 53, 10, 4),    # count control, L2
]


def level(x, edges=NOMINAL_EDGES):
    lo, mid, hi = edges
    return 0 if x < lo else 1 if x < mid else 2 if x < hi else 3


def in_band(x):
    """Which measured safe band x falls in, or None if it sits in a dead zone."""
    xf = float(x)
    for l, (a, b) in BANDS.items():
        if a <= xf <= b:
            return l
    return None


def b_pos(p, k):
    return p**k / (p**k + (1 - p)**k)


def q(p, N, k, d):
    a = ((1 - d) * p)**k * (1 - (1 - d) * p)**(N - k)
    b = ((1 - d) * (1 - p))**k * (1 - (1 - d) * (1 - p))**(N - k)
    return a / (a + b)


def b_star(p, N, k):
    a = p**k * (1 - p)**(N - k)
    b = (1 - p)**k * p**(N - k)
    return a / (a + b)


def kl(x, y):
    """D(x‖y) for a binary distribution, nats."""
    x, y = float(x), float(y)
    return x * math.log(x / y) + (1 - x) * math.log((1 - x) / (1 - y))


def cell(cid, pn, N, k):
    p = F(pn, 100)
    bp = b_pos(p, k)
    bs = b_star(p, N, k)
    out = {"id": cid, "p": p, "N": N, "k": k, "b_pos": bp, "b_star": bs}
    for d in DELTAS:
        qq = q(p, N, k, d)
        out[f"q_{d}"] = qq
        out[f"eps_{d}"] = kl(qq, bp)        # D(q‖b^t) on the partial record
        out[f"W_{d}"] = kl(bs, qq)          # D(b*‖q)
    return out


# --- the four conditions -----------------------------------------------------
# Correct answer per condition, and which delta supplies the ordinal-s denominator.
CONDITIONS = {
    "FULL":          {"denom_delta": DELTA_PRIMARY, "banked": False},
    "PARTIAL_BLIND": {"denom_delta": DELTA_PRIMARY, "banked": False},
    "RULED_D0":      {"denom_delta": DELTA_PRIMARY, "banked": False},
    "RULED_D3":      {"denom_delta": DELTA_BANKED,  "banked": True},
}


def active_conditions():
    return [c for c, v in CONDITIONS.items() if RUN_BANKED or not v["banked"]]


def banked_viable(c):
    """
    Can this cell carry the delta>0 extension? Requires q(delta_banked) to sit in a
    measured band at a level distinct from BOTH b_pos and q(0) -- otherwise stating a
    dropout rate cannot change the correct answer and the condition measures nothing.
    """
    qb = c[f"q_{DELTA_BANKED}"]
    if in_band(qb) is None:
        return False
    if level(qb) != level(qb, ALT_EDGES):
        return False
    return level(qb) not in (level(c["b_pos"]), level(c[f"q_{DELTA_PRIMARY}"]))


def targets(c):
    """Correct belief per condition for cell c."""
    return {
        "FULL": c["b_star"],
        "PARTIAL_BLIND": c["b_pos"],
        "RULED_D0": c[f"q_{F(0)}"],
        "RULED_D3": c[f"q_{F(3,10)}"],
    }


def s_endpoints(c, condition):
    """
    (l_pos, l_q) for ordinal-s. Anchor is ALWAYS the positives-only level, which is
    arm-invariant; FULL and PARTIAL-BLIND borrow the delta=0 upper endpoint, since
    q = b* there and all three sit on one ruler (D9).
    """
    l_pos = level(c["b_pos"])
    d = CONDITIONS[condition]["denom_delta"]
    l_q = level(c[f"q_{d}"])
    return l_pos, l_q


def ordinal_s(l_obs, c, condition):
    l_pos, l_q = s_endpoints(c, condition)
    return (l_obs - l_pos) / (l_q - l_pos)


def build():
    return [cell(*g) for g in GRID]


# --- verification ------------------------------------------------------------

def verify(cells):
    for c in cells:
        p, N, k = c["p"], c["N"], c["k"]

        # q at delta=0 IS b*, exactly, as rationals -- the design's pivot
        assert c[f"q_{F(0)}"] == c["b_star"], f"{c['id']}: q(0) != b*"

        # therefore FULL and RULED_D0 share a correct answer
        t = targets(c)
        assert t["FULL"] == t["RULED_D0"], f"{c['id']}: pivot broken"

        # W(0) = 0 and the decomposition is exactly Pythagorean at delta=0
        assert abs(c[f"W_{F(0)}"]) < 1e-12, f"{c['id']}: W(0) != 0"
        lhs = c[f"eps_{F(0)}"] + c[f"W_{F(0)}"]
        assert abs(lhs - kl(c["b_star"], c["b_pos"])) < 1e-9, \
            f"{c['id']}: eps + W != D(b*‖b_pos) at delta=0"

        # BANKED extension only. delta>0 does NOT sum, because q is computed under a
        # stated delta exceeding actual dropout and so is not the projection of b*.
        lhs3 = c[f"eps_{DELTA_BANKED}"] + c[f"W_{DELTA_BANKED}"]
        assert abs(lhs3 - kl(c["b_star"], c["b_pos"])) > 1e-6, \
            f"{c['id']}: delta banked unexpectedly Pythagorean"

        # eps FALLS as delta rises. This is why delta>0 was cut (D26): dropout weakens
        # the silence signal, so q(delta>0) sits between b_pos and q(0), the ordinal
        # denominator is always shorter there, and partial movement always scores
        # HIGHER. The arm intended as the harder test is mechanically the easier one.
        assert c[f"eps_{DELTA_BANKED}"] < c[f"eps_{DELTA_PRIMARY}"], \
            f"{c['id']}: eps did not fall"

        # every predicted belief sits inside a MEASURED band, not merely a nominal one
        for name, v in [("b_pos", c["b_pos"]), ("b*", c["b_star"]),
                        ("q0", c[f"q_{DELTA_PRIMARY}"])]:
            assert in_band(v) is not None, f"{c['id']}: {name}={float(v):.3f} in a dead zone"
            assert in_band(v) == level(v), f"{c['id']}: {name} band/level disagree"

        # levels agree under D20's alternate edges -- no cell's answer is cut-dependent
        for name, v in [("b_pos", c["b_pos"]), ("q0", c[f"q_{DELTA_PRIMARY}"])]:
            assert level(v) == level(v, ALT_EDGES), \
                f"{c['id']}: {name} changes level under alternate edges"

        # no ordinal-s denominator is zero, in any condition
        for cond in active_conditions():
            l_pos, l_q = s_endpoints(c, cond)
            assert l_q != l_pos, f"{c['id']}/{cond}: zero denominator"

        # b_pos >= 1/2 always at m=2 -- the structural limit of D4
        assert c["b_pos"] >= F(1, 2)

    # count controls: b_pos near-constant while k varies
    for tag, tol in (("C", 0.001), ("D", 0.001)):
        grp = [c for c in cells if c["id"].startswith(tag)]
        bs = [float(c["b_pos"]) for c in grp]
        ks = [c["k"] for c in grp]
        assert len(set(ks)) == len(ks), f"{tag}: k not varied"
        assert max(bs) - min(bs) <= tol, f"{tag}: b_pos spread {max(bs)-min(bs):.4f}"
        assert len({level(c['b_pos']) for c in grp}) == 1, f"{tag}: level not constant"
        # controls must share a target level too, or identical answers score differently
        assert len({level(c[f'q_{DELTA_PRIMARY}']) for c in grp}) == 1, \
            f"{tag}: target level not constant -> denominators differ"
        assert len({c['N'] for c in grp}) == len(grp), f"{tag}: N not varied"

    # blind-level balance
    n3 = sum(1 for c in cells if level(c["b_pos"]) == 3)
    assert (n3, len(cells) - n3) == (8, 6), f"balance drifted: {n3}/{len(cells)-n3}"
    assert len({(c["N"], c["k"]) for c in cells}) >= 10, "too many duplicated (N,k)"
    return True


if __name__ == "__main__":
    cells = build()
    verify(cells)
    print(f"{len(cells)} cells verified\n")
    hdr = (f"{'id':<4}{'p':>6}{'N':>4}{'k':>3}{'b_pos':>8}{'L':>3}"
           f"{'q(0)=b*':>9}{'L':>3}{'q(.3)':>8}{'L':>3}"
           f"{'span0':>7}{'span3':>7}{'eps0':>8}{'eps.3':>8}")
    print(hdr)
    for c in cells:
        lp = level(c["b_pos"]); l0 = level(c[f"q_{F(0)}"]); l3 = level(c[f"q_{F(3,10)}"])
        print(f"{c['id']:<4}{float(c['p']):>6.2f}{c['N']:>4}{c['k']:>3}"
              f"{float(c['b_pos']):>8.3f}{lp:>3}{float(c[f'q_{F(0)}']):>9.3f}{l0:>3}"
              f"{float(c[f'q_{F(3,10)}']):>8.3f}{l3:>3}{lp-l0:>7}{lp-l3:>7}"
              f"{c[f'eps_{F(0)}']:>8.3f}{c[f'eps_{F(3,10)}']:>8.3f}")
    print("\nordinal-s endpoints (l_pos -> l_q) by condition:")
    for c in cells:
        e = {k: s_endpoints(c, k) for k in CONDITIONS}
        print(f"  {c['id']:<4} " + "  ".join(
            f"{k}:{v[0]}->{v[1]}" for k, v in e.items()))
