"""
test_attenuation.py — is the silence update a damped move from b_pos toward q?

    python test_attenuation.py

No new calls. Reads the primary and banked results already on disk.

The claim
---------
A model is neither silence-blind (b_pos) nor silence-aware (q), but sits at a fixed
fraction of the way between them, in log-odds:

    logit m(lam) = (1 - lam) * logit b_pos  +  lam * logit q

lam = 0 is fully blind, lam = 1 is fully aware. The claim is that lam is a MODEL
property: one constant explains a model's answers across cells of different difficulty
AND across both delta arms.

Why this is testable on ordinal data
------------------------------------
One four-level answer does not pin lam down, but it constrains it to an interval: the
set of lam whose mixture falls in the observed bin. Intersecting those intervals across
23 cell-observations per model is a strong test. An empty intersection falsifies
constant-lam attenuation outright.

Three things are reported, in increasing order of how much they should convince you:

  1. BEST-lam FIT      how many of the 23 observations one lam can explain, against the
                       two endpoint baselines lam=0 (blind) and lam=1 (aware). If the
                       best lam beats both by a wide margin, the model genuinely lives
                       in the interior.

  2. CONSISTENCY       whether the intersection is non-empty, and if not, which cells
                       conflict. This is the falsification test.

  3. CROSS-ARM         fit lam on the delta=0 cells ONLY, then predict the delta=0.30
                       answers. Those cells have a different correct answer and were
                       never seen by the fit, so this is the honest test. Chance is
                       25% on a four-level scale; the blind and aware baselines are
                       also reported for comparison.

Caveat carried into any writeup: this is exploratory and post-hoc. It was not
pre-registered, and the delta arm was cut at freeze (D26).
"""

import json
import math
import os
from collections import Counter, defaultdict

import silence_v2_model as M
import silence_v2_stimuli as S

PRIMARY = os.environ.get("V2_RESULTS", "results_v2/v2_results_live.json")
BANKED = os.environ.get("V2_BANKED", "results_v2/v2_results_live_banked.json")
GRID = 2001                      # lam resolution over [0, 1]
ORDER = ("sol-none", "sol-high", "deepseek", "deepseek-high", "glm", "glm-high",
         "anchor")


def logit(p):
    p = min(max(float(p), 1e-12), 1 - 1e-12)
    return math.log(p / (1 - p))


def inv(z):
    return 1 / (1 + math.exp(-z))


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def load(path, stim_path):
    res = json.load(open(path))
    stim = {s["id"]: s for s in json.load(open(stim_path))["stimuli"]}
    b = defaultdict(list)
    for r in res["records"]:
        if r.get("ok"):
            s = stim[r["stimulus_id"]]
            b[(r["config"], s["cell"], s["condition"])].append(
                S.target_level(r["candidate"], r["confidence"], s["target_label"]))
    return {k: mode(v) for k, v in b.items()}


def predicted_levels(cell, delta):
    """level of the mixture at each lam on the grid, for one cell."""
    zb = logit(cell["b_pos"])
    zq = logit(cell[f"q_{delta}"])
    return [M.level(inv(zb + (i / (GRID - 1)) * (zq - zb))) for i in range(GRID)]


def main():
    cells = {c["id"]: c for c in M.build()}
    obs = load(PRIMARY, "silence_v2_stimuli.json")
    have_banked = os.path.exists(BANKED)
    if have_banked:
        obs.update(load(BANKED, "silence_v2_stimuli_banked.json"))

    # (cell, delta, condition-key) for every observation we can score
    tasks = [(cid, M.DELTA_PRIMARY, "PARTIAL_RULED") for cid in cells]
    if have_banked:
        tasks += [(c["id"], M.DELTA_BANKED, S.BANKED)
                  for c in M.build() if M.banked_viable(c)]

    pred = {(cid, d): predicted_levels(cells[cid], d) for cid, d, _ in tasks}
    lams = [i / (GRID - 1) for i in range(GRID)]

    print(f"attenuation test: {len(tasks)} cell-observations per configuration")
    print(f"  {len([t for t in tasks if t[1] == M.DELTA_PRIMARY])} at delta=0, "
          f"{len([t for t in tasks if t[1] != M.DELTA_PRIMARY])} at delta=0.30")
    print("EXPLORATORY, post-hoc, not pre-registered.\n")

    configs = [c for c in ORDER if any(k[0] == c for k in obs)]
    out = {}

    print("1. BEST SINGLE lam   (cells explained, out of those with an answer)")
    print(f"  {'config':<15}{'n':>4}{'blind':>8}{'aware':>8}{'best':>8}{'lam*':>8}"
          f"{'lam range':>16}")
    for cfg in configs:
        scored = [(cid, d, k) for cid, d, k in tasks
                  if obs.get((cfg, cid, k)) is not None]
        n = len(scored)
        if not n:
            continue
        hits = []
        for i in range(GRID):
            h = sum(1 for cid, d, k in scored if pred[(cid, d)][i] == obs[(cfg, cid, k)])
            hits.append(h)
        best = max(hits)
        blind, aware = hits[0], hits[-1]
        good = [lams[i] for i in range(GRID) if hits[i] == best]
        out[cfg] = {"n": n, "blind": blind, "aware": aware, "best": best,
                    "lam_lo": min(good), "lam_hi": max(good),
                    "lam_star": (min(good) + max(good)) / 2}
        print(f"  {cfg:<15}{n:>4}{blind:>8}{aware:>8}{best:>8}"
              f"{out[cfg]['lam_star']:>8.3f}"
              f"{f'[{min(good):.2f}, {max(good):.2f}]':>16}")

    print("\n2. CONSISTENCY   can ONE lam explain every observation?")
    for cfg in configs:
        if cfg not in out:
            continue
        d = out[cfg]
        exact = d["best"] == d["n"]
        print(f"  {cfg:<15}{'CONSISTENT' if exact else 'INCONSISTENT':<14}"
              f" {d['best']}/{d['n']} at best lam"
              + ("" if exact else f"  -> {d['n'] - d['best']} cell(s) conflict"))

    if not have_banked:
        print("\n3. CROSS-ARM: skipped, no banked results found.")
        return

    print("\n3. CROSS-ARM   fit lam on delta=0 only, predict delta=0.30")
    print(f"  {'config':<15}{'lam(fit)':>10}{'predicted':>11}{'blind':>8}{'aware':>8}"
          f"{'chance':>8}")
    fit_tasks = [t for t in tasks if t[1] == M.DELTA_PRIMARY]
    test_tasks = [t for t in tasks if t[1] != M.DELTA_PRIMARY]
    for cfg in configs:
        f_s = [(c, d, k) for c, d, k in fit_tasks if obs.get((cfg, c, k)) is not None]
        t_s = [(c, d, k) for c, d, k in test_tasks if obs.get((cfg, c, k)) is not None]
        if not f_s or not t_s:
            continue
        hits = [sum(1 for c, d, k in f_s if pred[(c, d)][i] == obs[(cfg, c, k)])
                for i in range(GRID)]
        bi = max(range(GRID), key=lambda i: hits[i])
        lam = lams[bi]
        got = sum(1 for c, d, k in t_s if pred[(c, d)][bi] == obs[(cfg, c, k)])
        bl = sum(1 for c, d, k in t_s if pred[(c, d)][0] == obs[(cfg, c, k)])
        aw = sum(1 for c, d, k in t_s if pred[(c, d)][-1] == obs[(cfg, c, k)])
        out.setdefault(cfg, {}).update(
            {"lam_fit_d0": lam, "cross_hits": got, "cross_n": len(t_s),
             "cross_blind": bl, "cross_aware": aw})
        print(f"  {cfg:<15}{lam:>10.3f}{f'{got}/{len(t_s)}':>11}"
              f"{f'{bl}/{len(t_s)}':>8}{f'{aw}/{len(t_s)}':>8}"
              f"{len(t_s)/4:>8.1f}")

    print("\n4. PER-CELL lam intervals   (delta=0 arm, where a single lam must live)")
    print(f"  {'cell':<6}" + "".join(f"{c[:9]:>12}" for c in configs))
    for cid, d, k in fit_tasks:
        row = f"  {cid:<6}"
        for cfg in configs:
            o = obs.get((cfg, cid, k))
            if o is None:
                row += f"{'--':>12}"
                continue
            ok = [lams[i] for i in range(GRID) if pred[(cid, d)][i] == o]
            row += f"{f'{min(ok):.2f}-{max(ok):.2f}' if ok else 'IMPOSSIBLE':>12}"
        print(row)

    json.dump(out, open("results_v2/v2_attenuation.json", "w"), indent=2)
    print("\nwritten to results_v2/v2_attenuation.json")


if __name__ == "__main__":
    main()
