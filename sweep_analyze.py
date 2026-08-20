"""
sweep_analyze.py — mixedness sweeps, per arm.

    python sweep_analyze.py                      # all sweeps, all cells
    python sweep_analyze.py --drop-dead-zone     # exclude cells outside a measured band
    python sweep_analyze.py --sweep PARABOLA     # one sweep only

Statistics (l_cor is the level the probe SHOULD be at; FULL and RULED both use
level(b*), since q(0) = b* exactly):

    s1 = |l_obs - l_cor|     magnitude of error, in bins
    s2 =  l_obs - l_cor      signed error; + = under-updated toward the target candidate
    s3 = P(l_obs == l_cor)   exact-hit rate

Reported at draw level (every usable draw) and modal level (10 draws pooled per cell,
ties dropped). Draw level is primary here: with 12 cells a single modal tie removes 8%
of the curve, and the sweeps are about shape.

Confound accounting, printed alongside every slope:

  PARABOLA   prompt length is constant to the character (FULL prints N lines whatever
             k is), so length cannot produce the shape. The correct LEVEL does move
             with k, so bin-avoidance can. FULLCTRL is the control for that.
  FULLCTRL   length constant AND correct level constant. If a slope survives here, it
             is mixedness.
  RULEDCTRL  same, with k fixed to hold RULED's length constant instead of N.

edge_distance is reported per cell because two PARABOLA cells sit 0.063 from a bin
boundary, where the correct level is least secure.
"""

import argparse
import json
import os
from collections import Counter, defaultdict

import silence_v2_stimuli as S

RESULTS = os.environ.get("SWEEP_RESULTS", "results_sweep/sweep_results_live.json")
STIM = "sweep_stimuli.json"
ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor")


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def load():
    res = json.load(open(RESULTS))
    stim = {s["id"]: s for s in json.load(open(STIM))["stimuli"]}
    errs = defaultdict(list)                  # (config, cell, arm) -> [signed error]
    for r in res["records"]:
        if not r.get("ok"):
            continue
        s = stim[r["stimulus_id"]]
        lv = S.target_level(r["candidate"], r["confidence"], s["target_label"])
        errs[(r["config"], s["cell"], s["condition"])].append(lv - s["level_correct"])
    meta = {}
    for s in stim.values():
        meta[s["cell"]] = {kk: s[kk] for kk in
                           ("sweep", "N", "k", "mixedness", "level_correct",
                            "in_band", "edge_distance", "p", "b_star")}
    return res, errs, meta


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / (sxx * syy) ** 0.5


def curve(errs, meta, cells, arm, configs, granularity):
    """-> {config: {cell: (s1, s2, s3, n)}}"""
    out = {}
    for cfg in configs:
        row = {}
        for cid in cells:
            v = errs.get((cfg, cid, arm), [])
            if not v:
                continue
            if granularity == "modal":
                m = mode(v)
                if m is None:
                    continue
                v = [m]
            row[cid] = (sum(abs(x) for x in v) / len(v),
                        sum(v) / len(v),
                        sum(1 for x in v if x == 0) / len(v),
                        len(v))
        out[cfg] = row
    return out


def show(title, cur, cells, meta, configs, xkey):
    print(f"\n{title}")
    hdr = "  " + f"{'cell':<6}{'k':>3}{'N':>4}{'mix':>5}{'Lcor':>5}{'edge':>7}  "
    print(hdr + "".join(f"{c[:9]:>11}" for c in configs))
    for cid in cells:
        m = meta[cid]
        flag = "" if m["in_band"] else "*"
        line = (f"  {cid + flag:<6}{m['k']:>3}{m['N']:>4}{m['mixedness']:>5}"
                f"{m['level_correct']:>5}{m['edge_distance']:>7.3f}  ")
        for cfg in configs:
            v = cur[cfg].get(cid)
            line += f"{'--':>11}" if v is None else f"{v[0]:>11.2f}"
        print(line)
    print("  values are s1 (mean |error| in bins).  * = outside a measured band")

    print(f"\n  correlation of s1 with {xkey}, and with the other axis:")
    print(f"  {'config':<15}{'r(s1, mix)':>12}{'r(s1, k)':>10}{'r(s1, edge)':>13}{'n':>5}")
    for cfg in configs:
        pts = [(meta[c]["mixedness"], meta[c]["k"], meta[c]["edge_distance"],
                cur[cfg][c][0]) for c in cells if c in cur[cfg]]
        if len(pts) < 3:
            print(f"  {cfg:<15}{'--':>12}{'--':>10}{'--':>13}{len(pts):>5}")
            continue
        rm = pearson([p[0] for p in pts], [p[3] for p in pts])
        rk = pearson([p[1] for p in pts], [p[3] for p in pts])
        re = pearson([p[2] for p in pts], [p[3] for p in pts])
        f = lambda x: "  --" if x is None else f"{x:+.3f}"
        print(f"  {cfg:<15}{f(rm):>12}{f(rk):>10}{f(re):>13}{len(pts):>5}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-dead-zone", action="store_true")
    ap.add_argument("--sweep", default=None)
    ap.add_argument("--modal", action="store_true", help="modal instead of draw level")
    a = ap.parse_args()

    res, errs, meta = load()
    configs = [c for c in ORDER if any(k[0] == c for k in errs)]
    gran = "modal" if a.modal else "draw"

    print(f"{res['n_ok']}/{res['n_records']} usable draws   granularity: {gran}")
    if a.drop_dead_zone:
        dropped = [c for c in meta if not meta[c]["in_band"]]
        print(f"dropping dead-zone cells: {dropped}")

    plan = [("PARABOLA", "FULL",
             "PARABOLA / FULL  -- length constant to the character; correct LEVEL moves"),
            ("FULLCTRL", "FULL",
             "FULLCTRL / FULL  -- length AND correct level constant; slope here is mixedness"),
            ("FULLCTRL", "PARTIAL_RULED",
             "FULLCTRL / RULED -- same cells, RULED arm (length varies 1094-1234, "
             "opposite to mixedness)"),
            ("RULEDCTRL", "PARTIAL_RULED",
             "RULEDCTRL / RULED -- k fixed so RULED length is constant; level constant")]

    out = {}
    for sw, arm, title in plan:
        if a.sweep and sw != a.sweep:
            continue
        cells = sorted(c for c in meta if meta[c]["sweep"] == sw
                       and (meta[c]["in_band"] or not a.drop_dead_zone))
        cur = curve(errs, meta, cells, arm, configs, gran)
        if not any(cur[c] for c in configs):
            print(f"\n{title}\n  no usable data")
            continue
        show(title, cur, cells, meta, configs, "mixedness")
        out[f"{sw}|{arm}"] = {c: {k: list(v) for k, v in cur[c].items()}
                              for c in configs}

    print("\nsigned error s2 and hit rate s3, pooled per sweep and arm")
    print(f"  {'sweep/arm':<26}{'config':<15}{'s1':>7}{'s2':>8}{'s3':>7}{'n':>6}")
    for sw, arm, _ in plan:
        if a.sweep and sw != a.sweep:
            continue
        cells = [c for c in meta if meta[c]["sweep"] == sw
                 and (meta[c]["in_band"] or not a.drop_dead_zone)]
        for cfg in configs:
            v = [x for c in cells for x in errs.get((cfg, c, arm), [])]
            if not v:
                continue
            print(f"  {sw + '/' + arm.replace('PARTIAL_', ''):<26}{cfg:<15}"
                  f"{sum(abs(x) for x in v)/len(v):>7.3f}"
                  f"{sum(v)/len(v):>+8.3f}"
                  f"{sum(1 for x in v if x == 0)/len(v):>7.3f}{len(v):>6}")

    os.makedirs("results_sweep", exist_ok=True)
    json.dump(out, open("results_sweep/sweep_curves.json", "w"), indent=2)
    print("\nwritten to results_sweep/sweep_curves.json")


if __name__ == "__main__":
    main()
