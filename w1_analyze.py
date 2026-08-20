"""
W1 analyser — applies the pre-committed decision rule from w1_pretest_plan.md §5.

    python w1_analyze.py

Reads results_w1/w1_results.json and w1_stimuli.json. Emits the four gates and the
verdict-table row they select. The rule was frozen before any call; this file only
evaluates it.

  G1  discrimination      BINDING   mode(k=1)=LOW and mode(k=6)=HIGH, per config
  G2  reachability        BINDING   all four (candidate, confidence) reached on CAL
  G3  wording             select    switch point stable across wording A/B
  G4  mirror              report    mirror halves agree on confidence
"""

import json
import os
from collections import Counter, defaultdict

import w1_stimuli as S

RESULTS = os.environ.get("W1_RESULTS", "results_w1/w1_results_live.json")
STIM = "w1_stimuli.json"

DEFAULT_MODE = ("sol-none", "deepseek", "glm")
HIGH_MODE = ("sol-high", "deepseek-high", "glm-high")
REPORTED_ONLY = ("anchor",)   # counts toward neither G1 threshold


def load():
    with open(RESULTS) as f:
        res = json.load(f)
    with open(STIM) as f:
        stim = {s["id"]: s for s in json.load(f)["stimuli"]}
    return res, stim


def ok_records(res):
    return [r for r in res["records"] if r.get("ok")]


def mode(values):
    """Modal value; None on an exact tie, which is itself a discrimination failure."""
    if not values:
        return None
    c = Counter(values).most_common()
    if len(c) > 1 and c[0][1] == c[1][1]:
        return None
    return c[0][0]


# ---------------------------------------------------------------- G1

def g1(records, stim):
    """Modal confidence at the decision pair, pooled over the mirror, per wording."""
    lo_k, hi_k = S.DECISION_K["low"], S.DECISION_K["high"]
    bucket = defaultdict(list)
    for r in records:
        s = stim[r["stimulus_id"]]
        if s["family"] != "BLIND" or s["k"] not in (lo_k, hi_k):
            continue
        bucket[(r["config"], r["wording"], s["k"])].append(r["confidence"])

    out = {}
    configs = sorted({r["config"] for r in records})
    for cfg in configs:
        per_wording = {}
        for w in S.WORDINGS:
            low_word = S.WORDINGS[w]["low"]
            high_word = S.WORDINGS[w]["high"]
            m_lo = mode(bucket.get((cfg, w, lo_k), []))
            m_hi = mode(bucket.get((cfg, w, hi_k), []))
            per_wording[w] = {
                "mode_k_low": m_lo,
                "mode_k_high": m_hi,
                "n_low": len(bucket.get((cfg, w, lo_k), [])),
                "n_high": len(bucket.get((cfg, w, hi_k), [])),
                "pass": m_lo == low_word and m_hi == high_word,
            }
        out[cfg] = {"per_wording": per_wording,
                    "pass": any(v["pass"] for v in per_wording.values())}
    return out


def g1_verdict(g1res):
    d = sum(1 for c in DEFAULT_MODE if g1res.get(c, {}).get("pass"))
    h = sum(1 for c in HIGH_MODE if g1res.get(c, {}).get("pass"))
    return {"default_passing": d, "high_passing": h, "pass": d >= 2 and h >= 2}


# ---------------------------------------------------------------- G2

def g2(records, stim):
    out = {}
    for cfg in sorted({r["config"] for r in records}):
        per_wording = {}
        for w in S.WORDINGS:
            seen = {(r["candidate"], r["confidence"]) for r in records
                    if r["config"] == cfg and r["wording"] == w
                    and stim[r["stimulus_id"]]["family"] == "CAL"}
            per_wording[w] = {"n_options_reached": len(seen),
                              "reached": sorted(map(list, seen)),
                              "pass": len(seen) == 4}
        out[cfg] = {"per_wording": per_wording,
                    "pass": all(v["pass"] for v in per_wording.values())}
    return out


# ---------------------------------------------------------------- G3

def switch_point(records, stim, cfg, wording):
    """
    Lowest P(first) at which the modal answer becomes (first-label, HIGH), i.e. the
    model's implied upper bin edge. None if it never switches.
    """
    high_word = S.WORDINGS[wording]["high"]
    first = S.LABELS[0]
    pts = {}
    for r in records:
        s = stim[r["stimulus_id"]]
        if s["family"] != "CAL" or r["config"] != cfg or r["wording"] != wording:
            continue
        pts.setdefault(s["p_first"], []).append((r["candidate"], r["confidence"]))
    for p in sorted(pts):
        if p < 0.5:
            continue
        if mode(pts[p]) == (first, high_word):
            return p
    return None


def g3(records, stim):
    out = {}
    sweep = sorted(S.CAL_P_FIRST)
    for cfg in sorted({r["config"] for r in records}):
        sp = {w: switch_point(records, stim, cfg, w) for w in S.WORDINGS}
        a, b = sp.get("A"), sp.get("B")
        if a is None or b is None:
            steps, stable = None, False
        else:
            steps = abs(sweep.index(a) - sweep.index(b))
            stable = steps <= 1
        out[cfg] = {"switch_point": sp, "steps_apart": steps, "stable": stable}
    return out


# ---------------------------------------------------------------- G4

def g4(records, stim):
    out = {}
    for cfg in sorted({r["config"] for r in records}):
        agree = total = 0
        for w in S.WORDINGS:
            for k in S.BLIND_K:
                halves = {}
                for r in records:
                    s = stim[r["stimulus_id"]]
                    if (s["family"] != "BLIND" or s["k"] != k
                            or r["config"] != cfg or r["wording"] != w):
                        continue
                    halves.setdefault(s["target_is_first"], []).append(r["confidence"])
                if len(halves) == 2:
                    total += 1
                    if mode(halves[True]) == mode(halves[False]) is not None:
                        agree += 1
        out[cfg] = {"cells": total, "agreeing": agree,
                    "rate": round(agree / total, 3) if total else None}
    return out


# ---------------------------------------------------------------- D19

def determinism(records, stim):
    out = {}
    for cfg in sorted({r["config"] for r in records}):
        by_stim = defaultdict(list)
        for r in records:
            if r["config"] == cfg:
                by_stim[r["stimulus_id"]].append((r["candidate"], r["confidence"]))
        unanimous = sum(1 for v in by_stim.values() if len(set(v)) == 1)
        out[cfg] = {"stimuli": len(by_stim), "unanimous": unanimous,
                    "rate": round(unanimous / len(by_stim), 3) if by_stim else None}
    return out


# ---------------------------------------------------------------- verdict

def verdict(g1v, g2res):
    g2_all = all(v["pass"] for c, v in g2res.items() if c not in REPORTED_ONLY)
    g2_some = any(not v["pass"] for c, v in g2res.items() if c not in REPORTED_ONLY)
    if g1v["pass"] and g2_all:
        return "GO", ("Freeze the v2 spec on four bins. Proceed to W2/W3/W4.")
    if g1v["pass"] and g2_some:
        return "GO WITH LIMITATION", (
            "Configurations failing G2 cannot express the lower half, so their "
            "PARTIAL-RULED flip is inexpressible. Move them to reserve and state it.")
    if not g1v["pass"] and g2_all:
        return "DIAGNOSE (one attempt, 24h)", (
            "Format works in the abstract but not on blind records. Likely repair is "
            "widening level separation via p/r, which W4 needs regardless.")
    return "NO-GO", (
        "Four bins are two, and two are structurally unusable. Ship v1 as a "
        "pilot-only negative-results paper. Do NOT build a third instrument.")


def main():
    res, stim = load()
    recs = ok_records(res)
    if res.get("stub"):
        print("*** STUB RUN — plumbing check only, not a result ***\n")

    print(f"{len(recs)}/{res['n_records']} usable draws\n")

    r1 = g1(recs, stim)
    v1 = g1_verdict(r1)
    print("G1  discrimination (BINDING)")
    for cfg, d in r1.items():
        tag = "  [reported only]" if cfg in REPORTED_ONLY else ""
        print(f"  {cfg:<15} {'PASS' if d['pass'] else 'FAIL'}{tag}")
        for w, x in d["per_wording"].items():
            print(f"      wording {w}: k=1 -> {x['mode_k_low']!r:<22}"
                  f" k=6 -> {x['mode_k_high']!r}")
    print(f"  => default-mode passing {v1['default_passing']}/3, "
          f"high-effort passing {v1['high_passing']}/3 "
          f"=> {'PASS' if v1['pass'] else 'FAIL'}\n")

    r2 = g2(recs, stim)
    print("G2  reachability (BINDING)")
    for cfg, d in r2.items():
        opts = {w: x["n_options_reached"] for w, x in d["per_wording"].items()}
        print(f"  {cfg:<15} {'PASS' if d['pass'] else 'FAIL'}   options reached {opts}")
    print()

    r3 = g3(recs, stim)
    print("G3  wording stability (selection)")
    for cfg, d in r3.items():
        print(f"  {cfg:<15} switch A={d['switch_point'].get('A')} "
              f"B={d['switch_point'].get('B')}  "
              f"{'stable' if d['stable'] else 'MOVES'}")
    print()

    r4 = g4(recs, stim)
    print("G4  mirror agreement (reported)")
    for cfg, d in r4.items():
        print(f"  {cfg:<15} {d['agreeing']}/{d['cells']} cells agree  rate {d['rate']}")
    print()

    r5 = determinism(recs, stim)
    print("D19 determinism (unanimous draws per stimulus)")
    for cfg, d in r5.items():
        print(f"  {cfg:<15} {d['unanimous']}/{d['stimuli']}  rate {d['rate']}")
    print()

    tag, note = verdict(v1, r2)
    print("=" * 68)
    print(f"VERDICT: {tag}")
    print(f"  {note}")
    print("=" * 68)

    with open(RESULTS.replace("w1_results", "w1_gates"), "w") as f:
        json.dump({"G1": r1, "G1_verdict": v1, "G2": r2, "G3": r3, "G4": r4,
                   "determinism": r5, "verdict": tag, "note": note}, f, indent=2)


if __name__ == "__main__":
    main()
