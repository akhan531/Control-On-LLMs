"""
analyze_2_4.py — compiles every run in results_2_4/ into one scored table.

Reads whatever .jsonl files are present, so it can be rerun as runs land. Emits:
  analysis_2_4/cells.csv      one row per (run, stimulus): mean log-odds, s, error in nats
  analysis_2_4/summary.csv    one row per (run, condition): the aggregates
  a printed report with the P1-P7 gates per run

Scoring follows silence_probe_spec.md §6:
  - average the LOG-ODDS across draws, never the probabilities
  - s = (probe - b_pos) / (q^t - b_pos), both endpoints computed
  - absolute error in nats against each condition's OWN correct answer, reported alongside s
  - deduplicate on (sid, seed); a retried draw supersedes the earlier failure
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

RESULTS = Path("results_2_4")
OUT = Path("analysis_2_4")
CONDITIONS = ["FULL", "FULL-EXPLICIT", "PARTIAL-BLIND", "PARTIAL-RULED-d0", "PARTIAL-RULED-d3"]


def load_run(path: Path):
    """Dedup on (sid, seed), keeping successes. Returns (draws_by_sid, n_failed_unrecovered)."""
    ok, failed = {}, set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        key = (r["sid"], r["seed"])
        if r.get("ok"):
            ok[key] = r
        else:
            failed.add(key)
    unrecovered = len(failed - set(ok))
    by = defaultdict(list)
    for (sid, _), r in ok.items():
        by[sid].append(r)
    return by, unrecovered


def main() -> None:
    # Stimuli are pooled from every stimulus file present, so control arms score through the same
    # path as the main grid rather than needing a parallel script that could drift from it.
    stim = {}
    for f in ("silence_stimuli.json", "silence_control_stimuli.json"):
        if Path(f).exists():
            stim.update({s["sid"]: s for s in json.loads(Path(f).read_text())})
    runs = sorted(RESULTS.glob("*.jsonl"))
    runs = [p for p in runs if not p.stem.startswith("stub")]
    if not runs:
        raise SystemExit("no runs found in results_2_4/")

    OUT.mkdir(exist_ok=True)
    cell_rows, summ_rows = [], []

    for path in runs:
        run = path.stem
        by, unrecovered = load_run(path)
        n_draws = sum(len(v) for v in by.values())

        print("=" * 78)
        print(f"{run}    {n_draws} usable draws across {len(by)} cells")
        if unrecovered:
            print(f"  {unrecovered} draws failed and were never recovered")
        print("=" * 78)

        S, E, per_cond = {}, {}, defaultdict(list)
        short = []
        for sid, rs in by.items():
            st = stim[sid]
            los = [r["logodds"] for r in rs]
            m = mean(los)
            s = (m - st["b_pos_logodds"]) / st["denominator"]
            err = abs(m - st["correct_logodds"])
            S[sid], E[sid] = s, err
            per_cond[st["condition"]].append(sid)
            if len(los) < 10:
                short.append((sid, len(los)))
            cell_rows.append(
                {
                    "run": run, "sid": sid, "block": st["block"], "condition": st["condition"],
                    "m": st["m"], "N": st["N"], "k": st["k"], "delta": st["delta"],
                    "rotation": st["rotation"], "target_label": st["target_label"],
                    "n_draws": len(los),
                    "mean_logodds": round(m, 6),
                    "sd_logodds": round(stdev(los), 6) if len(los) > 1 else 0.0,
                    "b_pos": round(st["b_pos_logodds"], 6),
                    "q_t": round(st["q_t_logodds"], 6),
                    "b_star": round(st["b_star_logodds"], 6),
                    "correct": round(st["correct_logodds"], 6),
                    "denominator": round(st["denominator"], 6),
                    "s": round(s, 6),
                    "abs_err_nats": round(err, 6),
                    "is_flip": st["is_flip"],
                    "n_clipped": sum(1 for r in rs if r.get("clipped")),
                }
            )

        # Missingness matters more than its size, so report where it landed.
        if short:
            by_cond = defaultdict(int)
            for sid, _ in short:
                by_cond[stim[sid]["condition"]] += 1
            print(f"  cells with <10 draws: {len(short)}  " + ", ".join(f"{c}:{n}" for c, n in by_cond.items()))
            if len(by_cond) == 1:
                print("  WARNING: missingness confined to one condition. Treat this run as unusable.")

        print(f"\n  {'condition':<20} {'mean s':>8} {'sd s':>7} {'err(nats)':>10} {'max err':>9}")
        for c in CONDITIONS:
            if not per_cond[c]:
                continue
            ss = [S[x] for x in per_cond[c]]
            ee = [E[x] for x in per_cond[c]]
            print(f"  {c:<20} {mean(ss):>8.3f} {(stdev(ss) if len(ss)>1 else 0):>7.3f} {mean(ee):>10.3f} {max(ee):>9.3f}")
            summ_rows.append(
                {"run": run, "condition": c, "n_cells": len(ss),
                 "mean_s": round(mean(ss), 6),
                 "sd_s": round(stdev(ss), 6) if len(ss) > 1 else 0.0,
                 "mean_abs_err_nats": round(mean(ee), 6),
                 "max_abs_err_nats": round(max(ee), 6)}
            )

        # Gates.
        def agg(c, f):
            return mean([f(x) for x in per_cond[c]]) if per_cond[c] else float("nan")

        # A control-arm run has no PARTIAL conditions, so the P1/P2 gates do not apply to it. Its
        # only job is the FULL-EXPLICIT error, reported against the same 0.35-nat threshold.
        if not per_cond["FULL"] and per_cond["FULL-EXPLICIT"]:
            ee = mean([E[x] for x in per_cond["FULL-EXPLICIT"]])
            print(f"\n  FULL-EXPLICIT err = {ee:.3f}   {'PASS' if ee < 0.35 else 'FAIL'} (vs 0.35)")
            det = sum(1 for rs in by.values() if len({round(r["logodds"], 6) for r in rs}) == 1)
            ds = [
                abs(S[x] - S[x.replace("|rot0|", "|rot1|")])
                for x in per_cond["FULL-EXPLICIT"]
                if "|rot0|" in x and x.replace("|rot0|", "|rot1|") in S
            ]
            print(f"  mirror |Δs| = {mean(ds):.3f}   determinism: {det}/{len(by)}")
            print()
            continue

        f_s, f_e = agg("FULL", lambda x: S[x]), agg("FULL", lambda x: E[x])
        b_s, b_e = agg("PARTIAL-BLIND", lambda x: abs(S[x])), agg("PARTIAL-BLIND", lambda x: E[x])
        p1 = f_s > 0.75 and f_e < 0.35
        p2 = b_s < 0.15 and b_e < 0.35
        print(f"\n  P1 FULL   s={f_s:+.3f} err={f_e:.3f}   {'PASS' if p1 else 'FAIL'}")
        print(f"  P2 BLIND  |s|={b_s:.3f} err={b_e:.3f}   {'PASS' if p2 else 'FAIL'}")
        if not (p1 and p2):
            print("  -> instrument gates failed (§8): this run yields NO silence claim.")
        else:
            print(f"  P3 RULED d=0    s = {agg('PARTIAL-RULED-d0', lambda x: S[x]):+.3f}")
            print(f"  P4 RULED d=0.3  s = {agg('PARTIAL-RULED-d3', lambda x: S[x]):+.3f}")

        # P7 mirror. Reported for every run: it is the only direct check on label artifacts.
        print("  P7 mirror |Δs|:", end=" ")
        parts = []
        for c in CONDITIONS:
            ds = [
                abs(S[x] - S[x.replace("|rot0|", "|rot1|")])
                for x in per_cond[c]
                if "|rot0|" in x and x.replace("|rot0|", "|rot1|") in S
            ]
            if ds:
                parts.append(f"{c.split('-')[-1]}={mean(ds):.3f}")
        print("  ".join(parts))

        det = sum(1 for rs in by.values() if len({round(r["logodds"], 6) for r in rs}) == 1)
        clip = sum(r.get("n_clipped", 0) for r in cell_rows if r["run"] == run)
        print(f"  determinism: {det}/{len(by)} cells identical on all seeds   clipped draws: {clip}")
        print()

    with (OUT / "cells.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cell_rows[0].keys()))
        w.writeheader()
        w.writerows(cell_rows)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ_rows[0].keys()))
        w.writeheader()
        w.writerows(summ_rows)
    print(f"wrote {OUT/'cells.csv'} ({len(cell_rows)} rows) and {OUT/'summary.csv'} ({len(summ_rows)} rows)")


if __name__ == "__main__":
    main()
