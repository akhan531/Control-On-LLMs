"""
meridian_analyze.py — analysis for Task 2.1f.

Reads results_2_1f/meridian_v2_results.json and produces every number the
scenario's section 4 predicts, plus the diagnostics section 5 requires.

Two things this does that ad-hoc analysis got wrong on 2026-08-05:

  1. STRATIFIED RECOMBINATION. T is stratified, not sampled, so branch means
     are recombined with the prior weights (0.5, 0.5) rather than pooled across
     surviving seeds (scenario 1.5). Pooling is only equivalent when both
     branches survive equally, and they do not: probe saturation drops far more
     exposed-branch seeds than protected-branch ones, and since the exposed
     branch has systematically smaller gaps, pooling biases the headline UP.
     At N=9 on wave one this was worth 3.5%.

  2. FLOOR SENSITIVITY. A probe that reports a hard zero makes V_hat infinite,
     and those seeds are dropped. Scenario 6 forbids silently flooring, and
     requires an explicit sensitivity table instead. Section 6 below recomputes
     the headline at several floors so the reader can see how much the answer
     depends on the choice.
"""

from __future__ import annotations

import json
import math
import os
import statistics as st
from pathlib import Path

import meridian_model as M

RESULTS = Path(os.environ.get("RESULTS_DIR", "results_2_1f")) / "meridian_v2_results.json"
GROUP_SIZES = (3, 5, 7, 9)
EXACT_GAP = {3: 0.1300, 5: 0.2874, 7: 0.4777, 9: 0.6866}
EXACT_EPS = {3: 0.1181, 5: 0.2706, 7: 0.4575, 9: 0.6643}
EXACT_WBAR = {3: 0.0119, 5: 0.0168, 7: 0.0201, 9: 0.0223}
PREDICTED_SLOPE = (EXACT_GAP[9] - EXACT_GAP[3]) / 6


def load():
    with open(RESULTS) as fh:
        d = json.load(fh)
    runs = {k: v for k, v in d["runs"].items() if "error" not in v}
    by = {(v["N"], v["arm"], v["seed_index"]): v for v in runs.values()}
    seeds = max(v["seed_index"] for v in runs.values()) + 1
    return d, by, seeds


def kl_floored(p, q, floor: float):
    """Reverse KL with q floored and renormalized. floor=0 means no flooring."""
    if floor > 0:
        q = [max(x, floor) for x in q]
        z = sum(q)
        q = [x / z for x in q]
    tot = 0.0
    for pi, qi in zip(p, q):
        if pi <= 0:
            continue
        if qi <= 0:
            return None
        tot += pi * math.log(pi / qi)
    return tot


def gap_at(by, seeds, N, rnd=1, floor=0.0, arm="selective"):
    """
    Per-seed paired gap, split by truth branch then recombined with the prior
    weights. Returns (mean, se, n_used, n_dropped, branch detail).
    """
    branches = {}
    for T in (0, 1):
        vals, drop = [], 0
        for i in range(seeds):
            h = by.get((N, "honest", i))
            s = by.get((N, arm, i))
            if not h or not s or h["T_slot"] != T:
                continue
            vh = kl_floored(h["b_star"], h["rounds"][rnd - 1]["probe_b"]["slots"], floor)
            vs = kl_floored(s["b_star"], s["rounds"][rnd - 1]["probe_b"]["slots"], floor)
            if vh is None or vs is None:
                drop += 1
                continue
            vals.append(vs - vh)
        if not vals:
            return None
        branches[T] = (st.fmean(vals),
                       st.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0,
                       len(vals), drop)
    mean = 0.5 * (branches[0][0] + branches[1][0])
    se = 0.5 * math.sqrt(branches[0][1] ** 2 + branches[1][1] ** 2)
    n = branches[0][2] + branches[1][2]
    d = branches[0][3] + branches[1][3]
    return mean, se, n, d, branches


def wls(xs, ys, ses):
    """Weighted least squares slope and its standard error."""
    w = [1.0 / (s ** 2) if s > 0 else 1.0 for s in ses]
    sw = sum(w)
    mx = sum(wi * x for wi, x in zip(w, xs)) / sw
    my = sum(wi * y for wi, y in zip(w, ys)) / sw
    sxx = sum(wi * (x - mx) ** 2 for wi, x in zip(w, xs))
    sxy = sum(wi * (x - mx) * (y - my) for wi, x, y in zip(w, xs, ys))
    slope = sxy / sxx
    return slope, math.sqrt(1.0 / sxx)


def main() -> int:
    d, by, seeds = load()
    print("Task 2.1f analysis")
    print(f"  {len(d['runs'])} debates | {seeds} seeds/cell | model {d.get('model')}")
    print(f"  clue hash {d['clue_hash'][:16]}...  fake_llm {d.get('fake_llm')}\n")

    # ── 1. headline ─────────────────────────────────────────────────────────
    print("1. HEADLINE: paired honest-vs-selective gap, stratified over T")
    print(f"   {'N':>3} {'gap':>9} {'se':>7} {'z':>7} {'n':>5} {'drop':>5}"
          f" {'exact':>8} {'ratio':>7}")
    xs, ys, ses = [], [], []
    for N in GROUP_SIZES:
        r = gap_at(by, seeds, N)
        if r is None:
            print(f"   {N:>3}  no usable pairs")
            continue
        m, se, n, dr, _ = r
        xs.append(N); ys.append(m); ses.append(se)
        z = m / se if se else float("inf")
        print(f"   {N:>3} {m:>+9.4f} {se:>7.4f} {z:>7.1f} {n:>5} {dr:>5}"
              f" {EXACT_GAP[N]:>8.4f} {m/EXACT_GAP[N]:>6.2f}x")

    if len(xs) >= 2:
        slope, sse = wls(xs, ys, ses)
        print(f"\n   slope {slope:+.4f} +/- {sse:.4f} nats per agent "
              f"(predicted {PREDICTED_SLOPE:+.4f}, ratio {slope/PREDICTED_SLOPE:.2f}x)")
        print(f"   slope z = {slope/sse:.1f}")
        inc = [(ys[i+1]-ys[i])/(xs[i+1]-xs[i]) for i in range(len(xs)-1)]
        print(f"   per-agent increments: "
              + "  ".join(f"{v:+.4f}" for v in inc)
              + ("   (accelerating)" if inc == sorted(inc) and inc[0] < inc[-1]
                 else ""))
        print(f"   monotone in N: {ys == sorted(ys)}")

    # ── 2. branches ─────────────────────────────────────────────────────────
    print("\n2. TRUTH BRANCHES (opposite signs on the model side: "
          "mu_0 > 0 > mu_1)")
    print(f"   {'N':>3} {'protected':>11} {'se':>7} {'n':>4} {'d':>3}"
          f" {'exposed':>11} {'se':>7} {'n':>4} {'d':>3}")
    for N in GROUP_SIZES:
        r = gap_at(by, seeds, N)
        if r is None:
            continue
        b = r[4]
        print(f"   {N:>3} {b[0][0]:>+11.4f} {b[0][1]:>7.4f} {b[0][2]:>4} {b[0][3]:>3}"
              f" {b[1][0]:>+11.4f} {b[1][1]:>7.4f} {b[1][2]:>4} {b[1][3]:>3}")

    # ── 3. honest arm ───────────────────────────────────────────────────────
    print("\n3. HONEST ARM (model says V(1) = 0 exactly; excess is probe error)")
    for N in GROUP_SIZES:
        v = [kl_floored(by[(N, "honest", i)]["b_star"],
                        by[(N, "honest", i)]["rounds"][0]["probe_b"]["slots"], 0)
             for i in range(seeds) if (N, "honest", i) in by]
        v = [x for x in v if x is not None]
        print(f"   N={N}: mean V_hat {st.fmean(v):.4f}  n={len(v)}")

    # ── 4. corollary 1 ──────────────────────────────────────────────────────
    # V(5) - V(2) is ZERO BY CONSTRUCTION and must never be reported: Probe B
    # is cached per distinct evidence block, so rounds 3-5 reuse round 2's
    # result. That measures our call-saving, not the system. The honest test is
    # V(2) - V(1): two INDEPENDENT probe calls on an identical block. It is
    # simultaneously the scenario 3.2 instrument-noise calibration, since the
    # model says the evidence cannot change after round 1 in these two arms.
    print("\n4. COROLLARY 1: V flat for t >= 2")
    print("   V(2)-V(1): two independent probes on an IDENTICAL evidence block.")
    print("   Model says exactly 0; observed spread is pure instrument noise.")
    print(f"   {'arm':<11}" + "".join(f"{'N='+str(N):>22}" for N in GROUP_SIZES))
    for arm in ("honest", "selective"):
        cells = []
        for N in GROUP_SIZES:
            dd = []
            for i in range(seeds):
                v = by.get((N, arm, i))
                if not v:
                    continue
                a, b = v["rounds"][0]["V_hat"], v["rounds"][1]["V_hat"]
                if a is not None and b is not None:
                    dd.append(b - a)
            if not dd:
                cells.append("n/a")
                continue
            m = st.fmean(dd)
            se = st.stdev(dd) / math.sqrt(len(dd)) if len(dd) > 1 else 0.0
            cells.append(f"{m:+.4f}+/-{se:.4f} n{len(dd)}")
        print(f"   {arm:<11}" + "".join(f"{c:>22}" for c in cells))

    print("   identical-input reproducibility (|V(2)-V(1)|, selective arm):")
    for N in GROUP_SIZES:
        dd = []
        for i in range(seeds):
            v = by.get((N, "selective", i))
            if not v:
                continue
            a, b = v["rounds"][0]["V_hat"], v["rounds"][1]["V_hat"]
            if a is not None and b is not None:
                dd.append(abs(b - a))
        if dd:
            print(f"     N={N}: mean |diff| {st.fmean(dd):.4f}  "
                  f"median {st.median(dd):.4f}  max {max(dd):.4f}")

    # ── 5. delayed arm ──────────────────────────────────────────────────────
    print("\n5. DELAYED ARM: matches selective at t=1, collapses at t=K")
    for N in GROUP_SIZES:
        r1 = gap_at(by, seeds, N, rnd=1, arm="delayed")
        r5 = gap_at(by, seeds, N, rnd=5, arm="delayed")
        s1 = gap_at(by, seeds, N, rnd=1, arm="selective")
        if not (r1 and r5 and s1):
            continue
        print(f"   N={N}: t=1 gap {r1[0]:+.4f} (selective {s1[0]:+.4f}, "
              f"diff {r1[0]-s1[0]:+.4f})   t=5 gap {r5[0]:+.4f} (model says 0)")

    # ── 6. floor sensitivity ────────────────────────────────────────────────
    print("\n6. FLOOR SENSITIVITY (scenario 6: flooring is an analysis choice)")
    print(f"   {'floor':>8} " + " ".join(f"{'N='+str(N):>16}" for N in GROUP_SIZES))
    for floor in (0.0, 1e-3, 1e-2, 2e-2):
        cells = []
        for N in GROUP_SIZES:
            r = gap_at(by, seeds, N, floor=floor)
            cells.append(f"{r[0]:+.4f} (d{r[3]:>2})" if r else "n/a")
        lab = "none" if floor == 0 else f"{floor:g}"
        print(f"   {lab:>8} " + " ".join(f"{c:>16}" for c in cells))

    # ── 7. surname control ──────────────────────────────────────────────────
    print("\n7. SURNAME CONTROL (counterbalanced; these should agree)")
    for N in GROUP_SIZES:
        out = []
        for sw in (False, True):
            vals = []
            for i in range(seeds):
                h = by.get((N, "honest", i)); s = by.get((N, "selective", i))
                if not h or h["swapped"] != sw:
                    continue
                a = h["rounds"][0]["V_hat"]; b = s["rounds"][0]["V_hat"]
                if a is not None and b is not None:
                    vals.append(b - a)
            out.append(f"{'swapped' if sw else 'base'} {st.fmean(vals):+.4f}")
        print(f"   N={N}: " + "   ".join(out))

    # ── 8. empty records ────────────────────────────────────────────────────
    print("\n8. EMPTY RECORDS in the selective arm (design property)")
    for N in GROUP_SIZES:
        e = [by[(N, "selective", i)]["empty_record"]
             for i in range(seeds) if (N, "selective", i) in by]
        prot = [by[(N, "selective", i)]["empty_record"]
                for i in range(seeds)
                if (N, "selective", i) in by
                and by[(N, "selective", i)]["T_slot"] == 0]
        print(f"   N={N}: overall {sum(e)}/{len(e)} = {sum(e)/len(e):.3f}   "
              f"protected-guilty {sum(prot)/len(prot):.3f} "
              f"(predicted {0.7**N:.3f})")

    # ── 9. decomposition ────────────────────────────────────────────────────
    print("\n9. DECOMPOSITION: eps_hat vs exact eps (Probe P tracks q^t?)")
    print(f"   {'N':>3} {'eps_hat':>9} {'exact eps':>11} {'exact W-bar':>13}")
    for N in GROUP_SIZES:
        vals = []
        for i in range(seeds):
            v = by.get((N, "selective", i))
            if not v:
                continue
            e = v["rounds"][0]["eps_hat"]
            if e is not None:
                vals.append(e)
        print(f"   {N:>3} {st.fmean(vals):>9.4f} {EXACT_EPS[N]:>11.4f} "
              f"{EXACT_WBAR[N]:>13.4f}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
