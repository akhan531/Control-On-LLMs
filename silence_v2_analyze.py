"""
silence_v2_analyze.py — evaluates the pre-registration in silence_v2_spec.md §10.

    python silence_v2_analyze.py

Cell is the unit of analysis (D3): the 2 mirrors x 5 draws inside a cell are pooled to
one modal target-frame level, and cells are the replicates.

    s = (l_obs - l_pos) / (l_q - l_pos)

in the TARGET frame, which is mirror-invariant. Overshoot is recorded, never clipped.

Non-control cells are A1-A5 and B1-B3, so there are EIGHT of them. The frozen spec says
"8 of the 11 non-control cells", which is unsatisfiable: 11 was carried over from an
earlier grid. Corrected to 6 of 8, preserving the intended proportion. Recorded as a
dated amendment, applied before any s was computed.
"""

import json
import os
from collections import Counter, defaultdict

import silence_v2_model as M
import silence_v2_stimuli as S

RESULTS = os.environ.get("V2_RESULTS", "results_v2/v2_results_live.json")
STIM = "silence_v2_stimuli.json"

DEFAULT_MODE = ("sol-none", "deepseek", "glm")
HIGH_MODE = ("sol-high", "deepseek-high", "glm-high")
REPORTED_ONLY = ("anchor",)

NONCONTROL = tuple(c["id"] for c in M.build() if c["id"][0] in ("A", "B"))
CONTROL = tuple(c["id"] for c in M.build() if c["id"][0] in ("C", "D"))
CELL_BAR = 6                     # amended from 8-of-11; see module docstring
N_NONCONTROL = len(NONCONTROL)


def mode(vals):
    if not vals:
        return None
    c = Counter(vals).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def load():
    res = json.load(open(RESULTS))
    stim = {s["id"]: s for s in json.load(open(STIM))["stimuli"]}
    return res, stim


def cell_levels(res, stim):
    """(config, cell, condition) -> modal target-frame level, pooling mirrors and draws."""
    bucket = defaultdict(list)
    for r in res["records"]:
        if not r.get("ok"):
            continue
        s = stim[r["stimulus_id"]]
        lv = S.target_level(r["candidate"], r["confidence"], s["target_label"])
        bucket[(r["config"], s["cell"], s["condition"])].append(lv)
    return ({k: mode(v) for k, v in bucket.items()},
            {k: len(v) for k, v in bucket.items()})


def s_of(level_obs, cell_id, stim):
    ref = next(s for s in stim.values() if s["cell"] == cell_id)
    lp, lq = ref["l_pos_target"], ref["l_q_target"]
    return None if level_obs is None else (level_obs - lp) / (lq - lp)


def main():
    res, stim = load()
    levels, ns = cell_levels(res, stim)
    configs = sorted({r["config"] for r in res["records"]})
    cells = [c["id"] for c in M.build()]

    print(f"{res['n_ok']}/{res['n_records']} usable draws\n")

    # ---- per-configuration s ------------------------------------------------
    table, agree_blind, agree_q = {}, {}, {}
    for cfg in configs:
        row = {}
        for cond in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"):
            vals = {c: s_of(levels.get((cfg, c, cond)), c, stim) for c in cells}
            row[cond] = vals
        table[cfg] = row
        rul = row["PARTIAL_RULED"]
        agree_blind[cfg] = sum(
            1 for c in NONCONTROL
            if rul[c] is not None and abs(rul[c]) < 1e-9)
        agree_q[cfg] = sum(
            1 for c in NONCONTROL
            if rul[c] is not None and abs(rul[c] - 1) < 1e-9)

    def mean_s(vals):
        v = [x for c, x in vals.items() if c in NONCONTROL and x is not None]
        return sum(v) / len(v) if v else None

    print("ordinal-s by configuration (non-control cells A1-A5, B1-B3)")
    print(f"  {'config':<15}{'FULL':>9}{'BLIND':>9}{'RULED':>9}"
          f"{'=blind':>8}{'=q':>5}")
    for cfg in configs:
        f, b, r = (mean_s(table[cfg][c])
                   for c in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"))
        fmt = lambda x: "  n/a" if x is None else f"{x:>9.3f}"
        tag = "  [reported only]" if cfg in REPORTED_ONLY else ""
        print(f"  {cfg:<15}{fmt(f)}{fmt(b)}{fmt(r)}"
              f"{agree_blind[cfg]:>6}/{N_NONCONTROL}{agree_q[cfg]:>4}{tag}")

    def m(cfg):
        return mean_s(table[cfg]["PARTIAL_RULED"])

    # ---- P1 / P2 / P3 -------------------------------------------------------
    print("\nP1  default-mode configurations are silence-blind"
          f"  (mean s < 0.25 and >= {CELL_BAR}/{N_NONCONTROL} cells matching BLIND)")
    p1 = {}
    for cfg in DEFAULT_MODE:
        v = m(cfg)
        p1[cfg] = v is not None and v < 0.25 and agree_blind[cfg] >= CELL_BAR
        print(f"  {cfg:<15} s={v if v is None else round(v,3)}"
              f"  cells={agree_blind[cfg]}/{N_NONCONTROL}  "
              f"{'PASS' if p1[cfg] else 'FAIL'}")

    print(f"\nP2  high-effort configurations read silence"
          f"  (mean s > 0.75 and >= {CELL_BAR}/{N_NONCONTROL} cells matching q)")
    p2 = {}
    for cfg in HIGH_MODE:
        v = m(cfg)
        p2[cfg] = v is not None and v > 0.75 and agree_q[cfg] >= CELL_BAR
        print(f"  {cfg:<15} s={v if v is None else round(v,3)}"
              f"  cells={agree_q[cfg]}/{N_NONCONTROL}  "
              f"{'PASS' if p2[cfg] else 'FAIL'}")

    print("\nP3  the dissociation is within-model  (s_high - s_none > 0.5)  *PRIMARY*")
    fams = {"sol": ("sol-none", "sol-high"),
            "deepseek": ("deepseek", "deepseek-high"),
            "glm": ("glm", "glm-high")}
    gaps = {}
    for fam, (lo, hi) in fams.items():
        a, b = m(lo), m(hi)
        g = None if None in (a, b) else b - a
        gaps[fam] = g
        print(f"  {fam:<15} none={a if a is None else round(a,3)}"
              f"  high={b if b is None else round(b,3)}"
              f"  gap={g if g is None else round(g,3)}"
              f"  {'PASS' if g is not None and g > 0.5 else 'FAIL'}")
    p3 = sum(1 for g in gaps.values() if g is not None and g > 0.5) >= 2

    # ---- P4 admission gate --------------------------------------------------
    print("\nP4  admission gate: PARTIAL_BLIND must return s = 0")
    excluded = defaultdict(list)
    for cfg in configs:
        for c in cells:
            v = table[cfg]["PARTIAL_BLIND"][c]
            if v is None or abs(v) > 1e-9:
                excluded[cfg].append(c)
        print(f"  {cfg:<15} excluded {len(excluded[cfg])}/{len(cells)} cells"
              + (f"  {excluded[cfg]}" if excluded[cfg] else ""))

    # ---- P5 count controls --------------------------------------------------
    print("\nP5  count controls: modal answer constant across k within C and D")
    p5 = {}
    for cfg in configs:
        ok = True
        detail = []
        for grp, ids in (("C", [c for c in CONTROL if c[0] == "C"]),
                         ("D", [c for c in CONTROL if c[0] == "D"])):
            for cond in ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED"):
                lv = {levels.get((cfg, c, cond)) for c in ids}
                if len(lv) > 1:
                    ok = False
                    detail.append(f"{grp}/{cond}:{sorted(str(x) for x in lv)}")
        p5[cfg] = ok
        print(f"  {cfg:<15} {'PASS' if ok else 'FAIL'}"
              + ("  " + "; ".join(detail) if detail else ""))

    # ---- secondary ----------------------------------------------------------
    print("\nsecondary: s stratified by span (span-3 vs span-2/1 cells)")
    span = {c["id"]: M.level(c["b_pos"]) - M.level(c[f"q_{M.DELTA_PRIMARY}"])
            for c in M.build()}
    for cfg in configs:
        out = []
        for sp in sorted({span[c] for c in NONCONTROL}, reverse=True):
            v = [table[cfg]["PARTIAL_RULED"][c] for c in NONCONTROL
                 if span[c] == sp and table[cfg]["PARTIAL_RULED"][c] is not None]
            if v:
                out.append(f"span{sp}: {sum(v)/len(v):.3f} (n={len(v)})")
        print(f"  {cfg:<15} " + "   ".join(out))

    print("\nper-cell s in PARTIAL_RULED")
    print(f"  {'cell':<6}" + "".join(f"{c[:9]:>11}" for c in configs))
    for c in cells:
        mark = "*" if c in CONTROL else " "
        print(f"  {c:<5}{mark}" + "".join(
            ("        n/a" if table[cfg]['PARTIAL_RULED'][c] is None
             else f"{table[cfg]['PARTIAL_RULED'][c]:>11.2f}") for cfg in configs))
    print("  * = count-control cell, scored on concordance not on s")

    print("\n" + "=" * 70)
    print(f"P1 {sum(p1.values())}/3   P2 {sum(p2.values())}/3   "
          f"P3 {'PASS' if p3 else 'FAIL'} (primary)   "
          f"P5 {sum(p5.values())}/{len(p5)}")
    print("=" * 70)

    json.dump({"s": {c: {k: {kk: vv for kk, vv in v.items()}
                         for k, v in table[c].items()} for c in table},
               "P1": p1, "P2": p2, "P3": {"gaps": gaps, "pass": p3},
               "P4_excluded": dict(excluded), "P5": p5,
               "cell_bar": CELL_BAR, "n_noncontrol": N_NONCONTROL},
              open("results_v2/v2_gates.json", "w"), indent=2)
    print("written to results_v2/v2_gates.json")


if __name__ == "__main__":
    main()
