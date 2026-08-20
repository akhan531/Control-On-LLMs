"""
s_competence.py — un-normalised views of FULL / BLIND / RULED performance.

    python s_competence.py

Reads the same frozen results the existing table came from. No new calls, nothing
written outside stdout and results_v2/v2_competence.json.

Why this exists
---------------
The published table reports  s = (l_obs - l_pos) / (l_q - l_pos), then takes a plain
unweighted mean over the 8 non-control cells. That mean pools cells with different
spans. Writing D = l_q - l_pos (negative, magnitude 3 for A cells and 2 for B cells):

    FULL / RULED :  l_obs - l_cor  =  |D| * (1 - s)        with l_cor = l_q
    BLIND        :  l_obs - l_cor  = -|D| * s              with l_cor = l_pos

So one bin of error in a span-2 cell contributes 1.5x as much to mean s as one bin of
error in a span-3 cell. Two configurations with identical bin-level behaviour can post
different mean s purely from cell mix. These tables remove the normalisation.

  l_cor   the level the probe SHOULD be at in that arm
          FULL  -> level(b*)  = l_q   (since q(0) = b* exactly)
          BLIND -> level(b_pos) = l_pos
          RULED -> level(q(0)) = l_q

  s1 = |l_obs - l_cor|      magnitude of error, in bins
  s2 =  l_obs - l_cor       signed error. Positive = too far toward the target
                            candidate (under-updated). Negative = overshot past the
                            correct answer.
  s3 = P(l_obs == l_cor)    exact-hit rate

A mean s2 near zero is ambiguous on its own: it means either accurate, or overshooting
as often as undershooting. The s2 DISTRIBUTION disambiguates, so it is printed too.

Two granularities and two cell scopes, all four combinations:
  modal  one pooled level per cell (matches the published table; drops modal ties)
  draw   every usable draw (10x the data; recovers the cells lost to ties)
  noncontrol  A1-A5, B1-B3 only, comparable to the published table
  all         plus C1-C3, D1-D3, which are structurally identical stimuli

Note for BLIND: s3 is arithmetically the same quantity as the P4 admission gate. s1 and
s2 are not - they say how far off, not merely whether.
"""

import json
import os
from collections import Counter, defaultdict

import silence_v2_model as M
import silence_v2_stimuli as S

RESULTS = os.environ.get("V2_RESULTS", "results_v2/v2_results_live.json")
STIM = "silence_v2_stimuli.json"
ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high", "anchor")
ARMS = ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED")
SHORT = {"FULL": "FULL", "PARTIAL_BLIND": "BLIND", "PARTIAL_RULED": "RULED"}


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def build():
    res = json.load(open(RESULTS))
    stim = {s["id"]: s for s in json.load(open(STIM))["stimuli"]}
    cells = {c["id"]: c for c in M.build()}

    l_pos = {cid: M.level(c["b_pos"]) for cid, c in cells.items()}
    l_q = {cid: M.level(c[f"q_{M.DELTA_PRIMARY}"]) for cid, c in cells.items()}
    # l_cor per arm: FULL is scored against b*, and q(0) = b* exactly
    l_cor = {"FULL": l_q, "PARTIAL_BLIND": l_pos, "PARTIAL_RULED": l_q}

    draws = defaultdict(list)          # (config, cell, arm) -> [level, ...]
    for r in res["records"]:
        if not r.get("ok"):
            continue
        s = stim[r["stimulus_id"]]
        draws[(r["config"], s["cell"], s["condition"])].append(
            S.target_level(r["candidate"], r["confidence"], s["target_label"]))
    return draws, l_pos, l_q, l_cor, cells, res


def collect(draws, l_cor, configs, arm, cell_ids, granularity):
    """-> {config: [signed error, ...]}"""
    out = {}
    for cfg in configs:
        vals = []
        for cid in cell_ids:
            obs = draws.get((cfg, cid, arm), [])
            if not obs:
                continue
            if granularity == "modal":
                m = mode(obs)
                if m is None:
                    continue           # modal tie: no defensible single level
                vals.append(m - l_cor[arm][cid])
            else:
                vals.extend(o - l_cor[arm][cid] for o in obs)
        out[cfg] = vals
    return out


def table(title, per_cfg, configs, note=""):
    print(f"\n{title}")
    if note:
        print(f"  {note}")
    print(f"  {'config':<15}{'n':>5}{'s1 mean':>9}{'s2 mean':>9}{'s3':>8}"
          f"{'s1 max':>8}")
    for cfg in configs:
        v = per_cfg.get(cfg, [])
        if not v:
            print(f"  {cfg:<15}{0:>5}{'--':>9}{'--':>9}{'--':>8}{'--':>8}")
            continue
        s1 = sum(abs(x) for x in v) / len(v)
        s2 = sum(v) / len(v)
        s3 = sum(1 for x in v if x == 0) / len(v)
        print(f"  {cfg:<15}{len(v):>5}{s1:>9.3f}{s2:>+9.3f}{s3:>8.3f}"
              f"{max(abs(x) for x in v):>8}")


def dist(title, per_cfg, configs):
    lo = min((min(v) for v in per_cfg.values() if v), default=0)
    hi = max((max(v) for v in per_cfg.values() if v), default=0)
    span = list(range(lo, hi + 1))
    print(f"\n{title}")
    print("  signed error s2 = l_obs - l_cor;  + = under-updated toward target, "
          "- = overshot")
    print(f"  {'config':<15}" + "".join(f"{x:>+6}" for x in span) + f"{'n':>6}")
    for cfg in configs:
        v = per_cfg.get(cfg, [])
        c = Counter(v)
        print(f"  {cfg:<15}" + "".join(f"{c.get(x, 0):>6}" for x in span)
              + f"{len(v):>6}")


def main():
    draws, l_pos, l_q, l_cor, cells, res = build()
    configs = [c for c in ORDER if any(k[0] == c for k in draws)]

    noncontrol = [c for c in cells if c[0] in ("A", "B")]
    allcells = list(cells)

    print(f"{res['n_ok']}/{res['n_records']} usable draws")
    print("l_cor: FULL -> level(b*) = l_q  |  BLIND -> level(b_pos) = l_pos  |  "
          "RULED -> level(q(0)) = l_q")
    print(f"\nspans (l_pos -> l_q), which mean-s normalises away:")
    for cid in allcells:
        tag = "  control" if cid[0] in ("C", "D") else ""
        print(f"  {cid:<4} {l_pos[cid]} -> {l_q[cid]}   span {l_pos[cid]-l_q[cid]}{tag}")

    out = {}
    for scope, ids in (("non-control (A1-A5, B1-B3)", noncontrol),
                       ("all 14 cells", allcells)):
        for gran in ("modal", "draw"):
            for arm in ARMS:
                per = collect(draws, l_cor, configs, arm, ids, gran)
                table(f"{SHORT[arm]}  |  {scope}  |  {gran}", per, configs)
                out[f"{SHORT[arm]}|{scope}|{gran}"] = {
                    k: {"n": len(v),
                        "s1": (sum(abs(x) for x in v) / len(v)) if v else None,
                        "s2": (sum(v) / len(v)) if v else None,
                        "s3": (sum(1 for x in v if x == 0) / len(v)) if v else None,
                        "dist": dict(Counter(v))}
                    for k, v in per.items()}

    print("\n" + "=" * 74)
    print("SIGNED-ERROR DISTRIBUTIONS (draw level, all 14 cells)")
    print("A mean s2 near zero is ambiguous: accurate, or symmetric overshoot.")
    print("=" * 74)
    for arm in ARMS:
        per = collect(draws, l_cor, configs, arm, allcells, "draw")
        dist(f"{SHORT[arm]}", per, configs)

    print("\n" + "=" * 74)
    print("SPAN STRATIFICATION (RULED, modal, non-control)")
    print("span-3 cells are A1-A5, span-2 are B1-B3. Mean s pools them; this does not.")
    print("=" * 74)
    a = [c for c in noncontrol if c[0] == "A"]
    b = [c for c in noncontrol if c[0] == "B"]
    for label, ids in (("span-3 (A cells)", a), ("span-2 (B cells)", b)):
        table(label, collect(draws, l_cor, configs, "PARTIAL_RULED", ids, "modal"),
              configs)

    json.dump(out, open("results_v2/v2_competence.json", "w"), indent=2)
    print("\nwritten to results_v2/v2_competence.json")


if __name__ == "__main__":
    main()
