"""
meridian_model.py — the model side of meridian_v2 (Task 2.1f).

Single source of every scenario constant and every closed-form quantity. If a
number appears in the harness, it appears here first, and it appears in
meridian_v2_scenario.md before that.

Nothing in this file makes a network call. Everything is exact: because the
disclosure rule is imposed and the likelihood table is frozen, b*, b^t, q^t,
eps, W-bar, V and dV are all available in closed form (scenario 3.1).

Run `python meridian_model.py` to execute the verification suite, which
reproduces scenario 4.1 and 4.2 to machine precision. That suite is the gate on
the whole task: if it does not pass, no harness written on top of it is worth
running.

Conventions, all carried from Convergence_Theorem.md:
  - reverse KL throughout: V(t) = D(b* || b^t)
  - close-of-round indexing: b^0 = pi, dV(t) = V(t) - V(t-1)
  - answers are slot-indexed, 0 = protected, 1 = exposed. Surnames never
    appear in this file; the harness owns the surname-to-slot mapping.
"""

from __future__ import annotations

import math
from itertools import product

# ─────────────────────────────────────────────────────────────────────────────
# Scenario constants. meridian_v2_scenario.md 1.1, 1.3, 1.4.
# ─────────────────────────────────────────────────────────────────────────────

SCENARIO_ID = "meridian_v2"
SPEC_VERSION = 3

# Slot 0 = protected (the norm shields this suspect), slot 1 = exposed.
SLOTS = ("protected", "exposed")
PI = (0.5, 0.5)

# Three-outcome alphabet. A points at the protected suspect, C at the exposed
# one, O is a genuine null. Scale levels: Expected .60 / Unremarkable .30 /
# Doubtful .10. Columns sum to one. Frozen: never tuned against LLM output.
ALPHABET = ("A", "C", "O")
P = {
    "A": (0.60, 0.30),
    "C": (0.30, 0.60),
    "O": (0.10, 0.10),
}

GROUP_SIZES = (3, 5, 7, 9)
R = 5           # rounds per debate
K = 4           # delayed arm's release round
ARMS = ("honest", "selective", "delayed")

N_CHANNELS = 9  # nested: N=3 uses channels 1-3, N=5 uses 1-5, and so on


def disclosure_set(arm: str, t: int) -> frozenset[str]:
    """S_i as a function of arm and round. Scenario 1.4."""
    if arm == "honest":
        return frozenset(ALPHABET)
    if arm == "selective":
        return frozenset({"C"})
    if arm == "delayed":
        return frozenset({"C"}) if t < K else frozenset(ALPHABET)
    raise ValueError(f"unknown arm {arm!r}")


def p_silent(a: int, S: frozenset[str]) -> float:
    """P(agent stays silent | T = a) under disclosure set S."""
    return sum(P[c][a] for c in ALPHABET if c not in S)


# ─────────────────────────────────────────────────────────────────────────────
# Core distributions. Everything is keyed on COUNTS, because the agents are iid
# and the likelihood depends on the clue vector only through its multiset.
# ─────────────────────────────────────────────────────────────────────────────

def _normalize(log_unnorm: tuple[float, float]) -> tuple[float, float]:
    m = max(log_unnorm)
    w = [math.exp(x - m) for x in log_unnorm]
    z = sum(w)
    return (w[0] / z, w[1] / z)


def b_star(counts: dict[str, int]) -> tuple[float, float]:
    """Pooled posterior on the full realized draw. The target, not the truth."""
    return _normalize(tuple(
        math.log(PI[a]) + sum(n * math.log(P[c][a]) for c, n in counts.items() if n)
        for a in (0, 1)
    ))


def b_track(disclosed: dict[str, int]) -> tuple[float, float]:
    """Silence-blind tracker b^t: conditions on disclosed findings only."""
    return _normalize(tuple(
        math.log(PI[a]) + sum(n * math.log(P[c][a]) for c, n in disclosed.items() if n)
        for a in (0, 1)
    ))


def q_ideal(disclosed: dict[str, int], n_silent: int,
            S: frozenset[str]) -> tuple[float, float]:
    """Ideal observer q^t = P(T | F_t): reads silence correctly."""
    return _normalize(tuple(
        math.log(PI[a])
        + sum(n * math.log(P[c][a]) for c, n in disclosed.items() if n)
        + (n_silent * math.log(p_silent(a, S)) if n_silent else 0.0)
        for a in (0, 1)
    ))


def kl(p: tuple[float, float], q: tuple[float, float]) -> float:
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q) if pi > 0.0)


def entropy(p: tuple[float, float]) -> float:
    return -sum(pi * math.log(pi) for pi in p if pi > 0.0)


def V(bstar: tuple[float, float], btrack: tuple[float, float]) -> float:
    """Lyapunov value V(t) = D(b* || b^t). Reverse KL."""
    return kl(bstar, btrack)


# ─────────────────────────────────────────────────────────────────────────────
# Per-seed evaluation. This is what the harness calls once it has a realized
# clue vector; the LLM never enters any of it.
# ─────────────────────────────────────────────────────────────────────────────

def _counts(clues: list[str]) -> dict[str, int]:
    return {c: clues.count(c) for c in ALPHABET}


def seed_trajectory(clues: list[str], arm: str, rounds: int = R) -> dict:
    """
    Exact model trajectory for one realized clue vector under one arm.

    clues: list of 'A' / 'C' / 'O', one per agent, index i = channel i+1.
    Returns V, dV, eps, and the belief vectors at t = 0 .. rounds.
    """
    N = len(clues)
    full = _counts(clues)
    bstar = b_star(full)
    H_bstar = entropy(bstar)

    out = {
        "N": N, "arm": arm, "clues": list(clues),
        "b_star": bstar, "H_b_star": H_bstar,
        "t": [], "b_track": [], "q": [], "V": [], "dV": [], "eps": [],
        "n_disclosed": [],
    }

    # t = 0: nothing public, b^0 = q^0 = pi.
    prev_V = V(bstar, PI)
    out["t"].append(0)
    out["b_track"].append(PI)
    out["q"].append(PI)
    out["V"].append(prev_V)
    out["dV"].append(None)
    out["eps"].append(kl(PI, PI))
    out["n_disclosed"].append(0)

    for t in range(1, rounds + 1):
        S = disclosure_set(arm, t)
        disclosed = {c: (full[c] if c in S else 0) for c in ALPHABET}
        n_silent = N - sum(disclosed.values())

        bt = b_track(disclosed)
        qt = q_ideal(disclosed, n_silent, S)
        Vt = V(bstar, bt)

        out["t"].append(t)
        out["b_track"].append(bt)
        out["q"].append(qt)
        out["V"].append(Vt)
        out["dV"].append(Vt - prev_V)
        out["eps"].append(kl(qt, bt))
        out["n_disclosed"].append(sum(disclosed.values()))
        prev_V = Vt

    return out


def disclosed_channels(clues: list[str], arm: str, t: int) -> list[int]:
    """Zero-based agent indices whose finding is public at round t."""
    S = disclosure_set(arm, t)
    return [i for i, c in enumerate(clues) if c in S]


# ─────────────────────────────────────────────────────────────────────────────
# Exact expectations by enumeration over the multinomial. No sampling.
# ─────────────────────────────────────────────────────────────────────────────

def _compositions(N: int, k: int):
    """All non-negative integer k-tuples summing to N."""
    if k == 1:
        yield (N,)
        return
    for first in range(N + 1):
        for rest in _compositions(N - first, k - 1):
            yield (first,) + rest


def _multinomial_coef(counts: tuple[int, ...]) -> float:
    n = sum(counts)
    out = math.factorial(n)
    for c in counts:
        out //= math.factorial(c)
    return float(out)


def exact_stats(N: int, arm: str = "selective", t: int = 1) -> dict:
    """
    Exact E[.] over the truth and the clue draw, by enumeration.

    Returns the row of scenario 4.2 plus the branch decomposition. Branch means
    are recombined with the prior weights, which is what stratifying T buys.
    """
    S = disclosure_set(arm, t)
    acc = {b: {"w": 0.0, "V0": 0.0, "Vt": 0.0, "eps": 0.0, "Hq": 0.0,
               "Hb": 0.0, "Vt2": 0.0, "empty": 0.0} for b in (0, 1)}

    for T in (0, 1):
        for comp in _compositions(N, len(ALPHABET)):
            counts = dict(zip(ALPHABET, comp))
            w = _multinomial_coef(comp)
            for c, n in counts.items():
                w *= P[c][T] ** n
            if w == 0.0:
                continue

            bstar = b_star(counts)
            disclosed = {c: (counts[c] if c in S else 0) for c in ALPHABET}
            n_pub = sum(disclosed.values())
            n_silent = N - n_pub

            bt = b_track(disclosed)
            qt = q_ideal(disclosed, n_silent, S)

            V0 = V(bstar, PI)
            Vt = V(bstar, bt)
            e = kl(qt, bt)

            a = acc[T]
            a["w"] += w
            a["V0"] += w * V0
            a["Vt"] += w * Vt
            a["Vt2"] += w * Vt * Vt
            a["eps"] += w * e
            a["Hq"] += w * entropy(qt)
            a["Hb"] += w * entropy(bstar)
            if n_pub == 0:
                a["empty"] += w

    branches = {}
    for b in (0, 1):
        a = acc[b]
        w = a["w"]
        branches[SLOTS[b]] = {
            "V0": a["V0"] / w, "V": a["Vt"] / w,
            "dV": (a["Vt"] - a["V0"]) / w,
            "eps": a["eps"] / w,
            "P_empty": a["empty"] / w,
        }

    def mix(key):
        return sum(PI[b] * acc[b][key] / acc[b]["w"] for b in (0, 1))

    E_V0 = mix("V0")
    E_Vt = mix("Vt")
    E_eps = mix("eps")
    E_Vt2 = mix("Vt2")
    W_bar_sub = E_Vt - E_eps                  # by the decomposition
    W_bar_ent = mix("Hq") - mix("Hb")         # by the entropy identity

    return {
        "N": N, "arm": arm, "t": t,
        "I_TC": E_V0,
        "V": E_Vt,
        "dV": E_Vt - E_V0,
        "eps": E_eps,
        "W_bar": W_bar_sub,
        "W_bar_entropy_route": W_bar_ent,
        "sd_V": math.sqrt(max(E_Vt2 - E_Vt * E_Vt, 0.0)),
        "P_empty_protected": branches["protected"]["P_empty"],
        "branches": branches,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Section 8.9 constants, computed rather than transcribed.
# ─────────────────────────────────────────────────────────────────────────────

def kl_restricted(a: int, a_prime: int, S: frozenset[str]) -> float:
    """KL_S(a || a'), the sum restricted to the disclosure set. Not a divergence."""
    return sum(P[c][a] * math.log(P[c][a] / P[c][a_prime]) for c in S)


def constants(arm: str = "selective") -> dict:
    S = disclosure_set(arm, 1)
    mu_0 = -kl_restricted(0, 1, S)
    mu_1 = -kl_restricted(1, 0, S)
    slope = PI[0] * mu_0
    intercept = math.log(PI[1])
    budget = entropy(PI)
    return {
        "mu_0": mu_0, "mu_1": mu_1,
        "slope": slope, "intercept": intercept, "budget": budget,
        "N_star_bound": math.ceil(-intercept / slope) if slope > 0 else None,
    }


def dV_lower_bound(N: int, arm: str = "selective") -> float:
    """Corollary 3b: E[dV(1)] >= pi_0 * sum_i E_0[x_i] + log pi_1."""
    k = constants(arm)
    return N * k["slope"] + k["intercept"]


def exact_identity(N: int, arm: str = "selective") -> float:
    """
    Theorem 3, the exact finite-N identity:
        E[dV(1)] = pi_0 * sum_i E_0[x_i] + log pi_1 + E[r(X)]
    with r(x) = log(1 + (pi_0/pi_1) exp(-x)) and X = sum_i x_i, where x_i is the
    disclosed log-likelihood ratio favouring the exposed suspect, zero on silence.
    Computed independently of exact_stats so the two can be cross-checked.
    """
    S = disclosure_set(arm, 1)
    ratio = PI[0] / PI[1]

    def x_of(c: str) -> float:
        return math.log(P[c][1] / P[c][0]) if c in S else 0.0

    E_r = 0.0
    for T in (0, 1):
        for comp in _compositions(N, len(ALPHABET)):
            counts = dict(zip(ALPHABET, comp))
            w = PI[T] * _multinomial_coef(comp)
            for c, n in counts.items():
                w *= P[c][T] ** n
            if w == 0.0:
                continue
            X = sum(n * x_of(c) for c, n in counts.items())
            E_r += w * math.log1p(ratio * math.exp(-X))

    return dV_lower_bound(N, arm) + E_r


# ─────────────────────────────────────────────────────────────────────────────
# Verification suite. Gates the whole task.
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_4_2 = {
    #  N: (I_TC,    V_sel(1), dV,       W_bar,   eps,     sd,      cor3b,    P_empty)
    3: (0.1387, 0.1300, -0.0088, 0.0119, 0.1181, 0.1183, -0.2425, 0.343),
    5: (0.2121, 0.2874, +0.0753, 0.0168, 0.2706, 0.2332, +0.0388, 0.168),
    7: (0.2742, 0.4777, +0.2035, 0.0201, 0.4575, 0.3776, +0.3088, 0.082),
    9: (0.3272, 0.6866, +0.3593, 0.0223, 0.6643, 0.5491, +0.5698, 0.040),
}

_SPEC_dV_1_TO_10 = [-0.0255, -0.0273, -0.0088, +0.0265, +0.0753,
                    +0.1351, +0.2035, +0.2787, +0.3593, +0.4442]

_FAILURES: list[str] = []


def _check(label: str, got: float, want: float, tol: float) -> None:
    ok = abs(got - want) <= tol
    flag = "ok  " if ok else "FAIL"
    print(f"  [{flag}] {label:<46} got {got:+.6f}  want {want:+.6f}")
    if not ok:
        _FAILURES.append(label)


def run_tests() -> int:
    print("meridian_model.py verification suite")
    print(f"scenario {SCENARIO_ID} spec version {SPEC_VERSION}\n")

    print("Likelihood table (scenario 1.3)")
    for a in (0, 1):
        _check(f"column sum, {SLOTS[a]}", sum(P[c][a] for c in ALPHABET), 1.0, 1e-12)
    for c in ALPHABET:
        _check(f"symmetry under slot swap, {c}", P[c][0], P[{"A": "C", "C": "A", "O": "O"}[c]][1], 1e-12)
    _check("null finding is exactly uninformative", P["O"][0] - P["O"][1], 0.0, 1e-12)

    print("\nConstants (scenario 4.1)")
    k = constants("selective")
    _check("mu_0", k["mu_0"], +0.207944, 1e-6)
    _check("mu_1", k["mu_1"], -0.415888, 1e-6)
    _check("Lemma 4, mu_0 + mu_1 < 0", float(k["mu_0"] + k["mu_1"] < 0), 1.0, 0.0)
    _check("slope", k["slope"], 0.103972, 1e-6)
    _check("intercept", k["intercept"], -0.693147, 1e-6)
    _check("budget H(pi)", k["budget"], 0.693147, 1e-6)
    _check("Cor 3c bound on N*", float(k["N_star_bound"]), 7.0, 0.0)

    print("\nE[dV(1)] at N = 1..10 (scenario 4.1)")
    for N, want in zip(range(1, 11), _SPEC_dV_1_TO_10):
        _check(f"N = {N}", exact_stats(N)["dV"], want, 5e-5)

    print("\nTheorem 3 exact identity vs enumeration")
    for N in range(1, 11):
        _check(f"identity == enumeration, N = {N}",
               exact_identity(N), exact_stats(N)["dV"], 1e-12)

    print("\nTrue critical group size")
    signs = [exact_stats(N)["dV"] > 0 for N in range(1, 11)]
    first_pos = signs.index(True) + 1
    _check("first N with E[dV(1)] > 0", float(first_pos), 4.0, 0.0)

    print("\nHeadline table (scenario 4.2)")
    for N, row in _SPEC_4_2.items():
        I_TC, Vsel, dV, Wbar, eps, sd, cor3b, pempty = row
        s = exact_stats(N, "selective", 1)
        _check(f"N={N} I(T;C)", s["I_TC"], I_TC, 5e-5)
        _check(f"N={N} V_sel(1)", s["V"], Vsel, 5e-5)
        _check(f"N={N} E[dV(1)]", s["dV"], dV, 5e-5)
        _check(f"N={N} W-bar(1)", s["W_bar"], Wbar, 5e-5)
        _check(f"N={N} eps(1)", s["eps"], eps, 5e-5)
        _check(f"N={N} per-seed SD of gap", s["sd_V"], sd, 5e-5)
        _check(f"N={N} Cor 3b bound", s["I_TC"] + dV_lower_bound(N), cor3b, 5e-5)
        # The spec quotes this one to three decimals, hence the looser tolerance.
        # The exact form is checked immediately below at machine precision.
        _check(f"N={N} P(empty | protected guilty)", s["P_empty_protected"], pempty, 5e-4)
        _check(f"N={N} P(empty) == (1 - p(C|protected))^N",
               s["P_empty_protected"], (1.0 - P["C"][0]) ** N, 1e-12)

    print("\nDecomposition cross-check, V-bar = W-bar + eps by two routes")
    for N in GROUP_SIZES:
        s = exact_stats(N)
        _check(f"N={N} W-bar entropy route == subtraction route",
               s["W_bar_entropy_route"], s["W_bar"], 1e-12)

    print("\nHonest arm degenerates as the theory says")
    for N in GROUP_SIZES:
        s = exact_stats(N, "honest", 1)
        _check(f"N={N} honest V(1) == 0", s["V"], 0.0, 1e-12)
        _check(f"N={N} honest eps(1) == 0", s["eps"], 0.0, 1e-12)
        _check(f"N={N} honest dV(1) == -I(T;C)", s["dV"], -s["I_TC"], 1e-12)

    print("\nDelayed arm matches selective at t=1 and collapses at t=K")
    for N in GROUP_SIZES:
        sel = exact_stats(N, "selective", 1)
        dly = exact_stats(N, "delayed", 1)
        _check(f"N={N} delayed dV(1) == selective dV(1)", dly["dV"], sel["dV"], 1e-12)
        _check(f"N={N} delayed V(K) == 0", exact_stats(N, "delayed", K)["V"], 0.0, 1e-12)

    print("\nPer-seed trajectory sanity")
    tr = seed_trajectory(["C", "C", "A"], "selective")
    _check("selective discloses only C findings", float(tr["n_disclosed"][1]), 2.0, 0.0)
    _check("V flat for t >= 2 (Corollary 1)", tr["V"][2] - tr["V"][5], 0.0, 1e-12)
    trd = seed_trajectory(["C", "C", "A"], "delayed")
    _check("delayed gains findings at t = K", float(trd["n_disclosed"][K]), 3.0, 0.0)
    _check("delayed V(K) == 0 pathwise", trd["V"][K], 0.0, 1e-12)
    trh = seed_trajectory(["A", "O", "C"], "honest")
    _check("honest V(1) == 0 pathwise", trh["V"][1], 0.0, 1e-12)
    _check("O is disclosed in the honest arm", float(trh["n_disclosed"][1]), 3.0, 0.0)

    print(f"\n{'PASS' if not _FAILURES else 'FAIL'}: "
          f"{len(_FAILURES)} failing check(s)")
    for f in _FAILURES:
        print(f"   - {f}")
    return 1 if _FAILURES else 0


def report() -> None:
    k = constants()
    print("\nmeridian_v2 model summary")
    print(f"  slope {k['slope']:.6f} per agent, intercept {k['intercept']:.6f}, "
          f"budget {k['budget']:.6f}")
    print(f"  {'N':>3} {'I(T;C)':>9} {'V_sel(1)':>9} {'E[dV]':>9} "
          f"{'W-bar':>8} {'eps':>8} {'SD':>8} {'Cor3b':>9} {'P(empty)':>9}")
    for N in GROUP_SIZES:
        s = exact_stats(N)
        print(f"  {N:>3} {s['I_TC']:>9.4f} {s['V']:>9.4f} {s['dV']:>+9.4f} "
              f"{s['W_bar']:>8.4f} {s['eps']:>8.4f} {s['sd_V']:>8.4f} "
              f"{s['I_TC'] + dV_lower_bound(N):>+9.4f} "
              f"{s['P_empty_protected']:>9.3f}")


if __name__ == "__main__":
    import sys
    code = run_tests()
    report()
    sys.exit(code)
