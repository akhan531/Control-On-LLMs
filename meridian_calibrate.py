"""
meridian_calibrate.py — the pre-freeze calibration pass (scenario 1.6, section 6).

Measures whether the CLUE TEXTS carry the weight the FROZEN TABLE assigns them,
and reports the precision of that measurement so the answer can be acted on.

Estimator note, 2026-08-05. The first version averaged the five probe draws in
probability space and then took the log-odds of the average. That is a biased
estimate of mean log-odds, and worse, it discarded the per-draw spread, so
three calibration rounds produced point estimates with no error bars and the
team spent two rewrite passes chasing run-to-run noise. Untouched channels
moved by up to 0.38x between runs against a band only 0.6x wide.

This version averages log-odds directly, reports a standard error and a 95%
interval per channel, and refuses to return a verdict when the interval
straddles a band edge. The harness's own probability-space averaging is
deliberately NOT changed: there it feeds V_hat as a representative belief,
which is what scenario 3.2 specifies.

Five measurements:
  1. Per-channel strength against the table's log(0.60/0.30) = 0.693 nats.
  2. Surname prior, from the same texts naming each suspect.
  3. Balance: equal A and C on the record should sit near even.
  4. Accumulation and saturation, k = 1..9 over randomized channel subsets.
  5. Silence inference by Probe P on an empty record, against the exact q.

Run once, before freeze, and log the result whether or not anything changes.
Repeating it after seeing run results would tune the instrument against itself.

Suggested invocation for a decision-grade measurement:
    PROBE_DRAWS=25 WORKERS=16 python meridian_calibrate.py
"""

from __future__ import annotations

import json
import math
import os
import statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import meridian_model as M
import meridian_clues as CL
import meridian_harness as H

OUT = Path(os.environ.get("CALIB_DIR", "results_2_1f_calibration"))
WORKERS = int(os.environ.get("WORKERS", "8"))
DATA = CL.load()
BASE = {0: "Alvarez", 1: "Chen"}
SWAP = {0: "Chen", 1: "Alvarez"}

INTENDED = math.log(M.P["C"][1] / M.P["C"][0])   # 0.693147 nats per finding

# The launch gate, fixed before the run that decides it. Not widened to fit a
# result. If the interval straddles an edge the answer is "measure harder",
# never "call it close enough".
TOL_LO = float(os.environ.get("TOL_LO", "0.7"))
TOL_HI = float(os.environ.get("TOL_HI", "1.3"))


def finding(ch_index: int, outcome: str, names: dict[int, str]) -> dict:
    ch = DATA["channels"][ch_index - 1]
    return {"channel": ch["index"], "line_of_inquiry": ch["line_of_inquiry"],
            "outcome": outcome,
            "text": CL.realize(ch, outcome, names[0], names[1])}


def block(findings: list[dict]) -> str:
    return H.evidence_block(findings, [True] * len(findings))


def draw_log_odds(slots) -> float | None:
    """log( P(exposed) / P(protected) ) for ONE draw. None on a hard zero."""
    p0, p1 = slots
    if p0 <= 0.0 or p1 <= 0.0:
        return None
    return math.log(p1 / p0)


def summarize(draws: list) -> dict:
    """Mean log-odds, standard error, and hard-zero count, over raw draws."""
    los = [draw_log_odds(d) for d in draws]
    finite = [x for x in los if x is not None]
    n_zero = sum(1 for x in los if x is None)
    if not finite:
        return {"n": 0, "n_zero": n_zero, "mean": None, "se": None}
    mean = statistics.fmean(finite)
    se = (statistics.stdev(finite) / math.sqrt(len(finite))
          if len(finite) > 1 else 0.0)
    return {"n": len(finite), "n_zero": n_zero, "mean": mean, "se": se}


def _run(jobs: list[tuple]) -> list[dict]:
    def work(j):
        label, ev, names, seed = j
        r = H.probe_b(ev, names, seed, 1)
        s = summarize(r["draws"])
        return {"label": label, "slots": r["slots"], "draws": r["draws"], **s}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(work, jobs))


def pooled(entries: list[dict]) -> dict:
    """Pool raw draws across configurations that measure the same quantity."""
    allo = []
    n_zero = 0
    for e in entries:
        for d in e["draws"]:
            lo = draw_log_odds(d)
            if lo is None:
                n_zero += 1
            else:
                allo.append(lo)
    if not allo:
        return {"n": 0, "n_zero": n_zero, "mean": None, "se": None}
    mean = statistics.fmean(allo)
    se = statistics.stdev(allo) / math.sqrt(len(allo)) if len(allo) > 1 else 0.0
    return {"n": len(allo), "n_zero": n_zero, "mean": mean, "se": se}


# ─────────────────────────────────────────────────────────────────────────────

def per_channel_strength() -> list[dict]:
    jobs = []
    for i in range(1, 10):
        jobs.append((f"ch{i}/C/base", block([finding(i, "C", BASE)]), BASE,
                     500_000 + 10 * i))
        jobs.append((f"ch{i}/C/swap", block([finding(i, "C", SWAP)]), SWAP,
                     500_000 + 10 * i + 5))
    return _run(jobs)


def balance() -> list[dict]:
    """
    Equal counts of A and C. Every configuration is run both ways round, so
    channel identity is removed from the direction rather than confounded with
    it, which is what the first version of this test did.
    """
    jobs = []
    for k, chans in ((1, [1, 2]), (2, [3, 4, 5, 6]), (3, [1, 3, 5, 2, 4, 6])):
        half = len(chans) // 2
        lo, hi = chans[:half], chans[half:]
        for tag, aside, cside in (("fwd", lo, hi), ("rev", hi, lo)):
            for nm, names in (("base", BASE), ("swap", SWAP)):
                f = ([finding(c, "A", names) for c in aside]
                     + [finding(c, "C", names) for c in cside])
                jobs.append((f"balanced/{k}v{k}/{tag}/{nm}", block(f), names,
                             610_000 + 100 * k + 10 * (tag == "rev")
                             + (nm == "swap")))
    return _run(jobs)


def accumulation() -> list[dict]:
    """
    k concordant findings over randomized channel subsets, so no single strong
    channel can drive the curve invisibly the way channel 1 once did.
    """
    import random
    jobs = []
    for k in range(1, 10):
        rng = random.Random(90_000 + k)
        seen, subsets = set(), []
        for _ in range(40):
            sub = tuple(sorted(rng.sample(range(1, 10), k)))
            if sub not in seen:
                seen.add(sub)
                subsets.append(sub)
            if len(subsets) == 3:
                break
        for si, sub in enumerate(subsets):
            tag = "-".join(str(c) for c in sub)
            for d in ("C", "A"):
                f = [finding(c, d, BASE) for c in sub]
                jobs.append((f"accum/{d}/{k}/{si}/{tag}", block(f), BASE,
                             710_000 + 100 * k + 10 * si + (d == "A")))
    return _run(jobs)


def silence_inference() -> list[dict]:
    S = M.disclosure_set("selective", 1)

    def work(N):
        r = H.probe_p("", "", BASE, 800_000 + N, 1, N, "selective")
        q = M.q_ideal({c: 0 for c in M.ALPHABET}, N, S)
        s = summarize(r["draws"])
        return {"N": N, "slots": r["slots"], "exact_q": list(q),
                "log_odds_exact": math.log(q[1] / q[0]), **s}

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        return list(pool.map(work, [3, 5, 7, 9]))


# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    nd = H.PROBE_DRAWS
    print("meridian_v2 pre-freeze calibration (scenario 1.6)")
    print(f"  model {H.MODEL} | endpoint {H.BASE_URL} | {WORKERS} workers")
    print(f"  clue hash {CL.freeze_hash()[:16]}...")
    print(f"  {nd} draws per configuration @ temp {H.PROBE_TEMPERATURE}")
    print(f"  intended per-finding movement: {INTENDED:.4f} nats")
    if nd < 20:
        print(f"  WARNING: {nd} draws is below the 20 needed for a gate-grade\n"
              f"           estimate. Re-run with PROBE_DRAWS=25 before deciding.")
    H.preflight()

    res, verdicts = {}, {}

    print("1. Per-channel strength, pooled over both surname assignments")
    print(f"     {'ch':<5}{'nats':>8}{'se':>8}{'ratio':>9}"
          f"{'95% CI (ratio)':>20}{'verdict':>14}")
    res["per_channel"] = per_channel_strength()
    byc = {}
    for r in res["per_channel"]:
        parts = r["label"].split("/")
        byc.setdefault(int(parts[0][2:]), {})[parts[2]] = r

    for ch in sorted(byc):
        p = pooled([byc[ch]["base"], byc[ch]["swap"]])
        if p["mean"] is None:
            print(f"     ch{ch:<3}{'saturated':>8}{'':>8}{'':>9}{'':>20}"
                  f"{'FAIL':>14}")
            verdicts[ch] = "FAIL"
            continue
        ratio = p["mean"] / INTENDED
        half = 1.96 * p["se"] / INTENDED
        lo_ci, hi_ci = ratio - half, ratio + half
        if lo_ci >= TOL_LO and hi_ci <= TOL_HI:
            v = "PASS"
        elif hi_ci < TOL_LO or lo_ci > TOL_HI:
            v = "FAIL"
        else:
            v = "INCONCLUSIVE"
        verdicts[ch] = v
        print(f"     ch{ch:<3}{p['mean']:>8.3f}{p['se']:>8.3f}{ratio:>8.2f}x"
              f"{f'[{lo_ci:.2f}, {hi_ci:.2f}]':>20}{v:>14}"
              + (f"  {p['n_zero']}z" if p["n_zero"] else ""))
        res.setdefault("channel_stats", {})[str(ch)] = {
            "mean": p["mean"], "se": p["se"], "ratio": ratio,
            "ci": [lo_ci, hi_ci], "verdict": v, "n": p["n"],
            "n_zero": p["n_zero"]}

    print("\n2. Surname prior (same sentence, different name)")
    print(f"     {'ch':<5}{'naming Chen':>14}{'naming Alvarez':>17}{'diff':>9}")
    diffs = []
    for ch in sorted(byc):
        b, s = byc[ch]["base"], byc[ch]["swap"]
        if b["mean"] is None or s["mean"] is None:
            continue
        d = s["mean"] - b["mean"]
        diffs.append(d)
        print(f"     ch{ch:<3}{b['mean']:>14.3f}{s['mean']:>17.3f}{d:>+9.3f}")
    if diffs:
        m = statistics.fmean(diffs)
        se = (statistics.stdev(diffs) / math.sqrt(len(diffs))
              if len(diffs) > 1 else 0.0)
        print(f"     mean asymmetry {m:+.3f} nats (se {se:.3f}) "
              f"across {len(diffs)} channels")
        print("     positive means the identical sentence lands harder "
              "when it names Alvarez")
        res["surname_asymmetry"] = {"mean": m, "se": se, "n": len(diffs)}

    print("\n3. Balance (equal A and C, target 0.000)")
    res["balance"] = balance()
    fwd = [r for r in res["balance"] if "/fwd/" in r["label"]]
    rev = [r for r in res["balance"] if "/rev/" in r["label"]]
    allb = pooled(res["balance"])
    print(f"     forward configs pooled : {pooled(fwd)['mean']:+.3f}")
    print(f"     reversed configs pooled: {pooled(rev)['mean']:+.3f}")
    print(f"     counterbalanced overall: {allb['mean']:+.3f} "
          f"(se {allb['se']:.3f})")

    print("\n4. Accumulation and saturation")
    print(f"     {'k':>3}{'toward exposed':>18}{'toward protected':>20}"
          f"{'exact':>9}")
    res["accumulation"] = accumulation()
    acc = {}
    for r in res["accumulation"]:
        _, d, k, _si, _tag = r["label"].split("/")
        acc.setdefault(int(k), {}).setdefault(d, []).append(r)
    for k in sorted(acc):
        cells = []
        for d in ("C", "A"):
            p = pooled(acc[k].get(d, []))
            cells.append("saturated" if p["mean"] is None else
                         f"{p['mean']:+.3f} ({p['se']:.2f})"
                         + (f" {p['n_zero']}z" if p["n_zero"] else ""))
        print(f"     {k:>3}{cells[0]:>18}{cells[1]:>20}{k*INTENDED:>9.3f}")

    print("\n5. Silence inference by Probe P (empty record)")
    print(f"     {'N':>3}{'observed':>12}{'se':>8}{'exact q':>11}{'gap':>9}")
    res["silence"] = silence_inference()
    for r in res["silence"]:
        o = "HARD0" if r["mean"] is None else f"{r['mean']:+.3f}"
        se = "" if r["se"] is None else f"{r['se']:.3f}"
        gap = ("n/a" if r["mean"] is None
               else f"{r['mean'] - r['log_odds_exact']:+.3f}")
        print(f"     {r['N']:>3}{o:>12}{se:>8}"
              f"{r['log_odds_exact']:>+11.3f}{gap:>9}")

    n_fail = sum(1 for v in verdicts.values() if v == "FAIL")
    n_inc = sum(1 for v in verdicts.values() if v == "INCONCLUSIVE")
    print(f"\nLAUNCH GATE: every channel within {TOL_LO}x-{TOL_HI}x")
    print(f"  {9 - n_fail - n_inc} pass, {n_fail} fail, {n_inc} inconclusive")
    passed = (n_fail == 0 and n_inc == 0)
    res["gate_passed"] = passed
    res["verdicts"] = {str(k): v for k, v in verdicts.items()}

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "calibration.json"
    with open(path, "w") as fh:
        json.dump({"results": res, "model": H.MODEL,
                   "clue_hash": CL.freeze_hash(),
                   "probe_draws": nd,
                   "probe_temperature": H.PROBE_TEMPERATURE,
                   "band": [TOL_LO, TOL_HI],
                   "intended_per_finding_nats": INTENDED,
                   "timestamp": datetime.now(timezone.utc).isoformat()}, fh,
                  indent=2)
    print(f"wrote {path}")

    if n_inc and not n_fail:
        print("\nMeasurement too imprecise to decide. Increase PROBE_DRAWS.")
        return 3
    if not passed:
        print("\nDo not launch. The per-channel gate failed.")
        return 2
    print("\nPer-channel gate passed.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
