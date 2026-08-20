"""
sweep_stimuli.py — evidence-mixedness sweeps (Task 2.4b, exploratory extension).

    python sweep_stimuli.py              # build + freeze, prints hash and cell tables
    python sweep_stimuli.py --show P05   # print prompts for one cell

Question
--------
Does the MIXEDNESS of the evidence predict how badly a model reasons with it, and does
deriving absences cost more when the evidence is mixed?

Mixedness is k(N-k): zero when every assay agrees, maximal at k = N/2.

Three sweeps. Named for what they do, so they never collide with the statistics s1, s2, s3.

  PARABOLA    FULL only. p and N fixed, k swept 0..N.
              Prompt length is CONSTANT (FULL always prints N lines), so any effect is
              not a length effect. The raw shape: expect low s1 at both unanimous ends
              and a peak in the middle if mixedness matters.
              CONFOUND, deliberately left in: as k rises the correct answer marches from
              level 0 to level 3, so the middle of the sweep is exactly where the correct
              answer is a MIDDLE level. A model that simply avoids middle bins produces
              the same parabola with no mixedness effect at all. FULLCTRL exists to
              separate these.

  FULLCTRL    FULL. N fixed AND b* held at one level, with p compensating as k moves.
              Since log-odds(b*) = (2k - N) * ln(p/(1-p)), p can absorb the change in k.
              Length constant, correct level constant, mixedness varies. If PARABOLA's
              shape is bin-avoidance, this one is flat. If mixedness is real, it slopes.

  RULEDCTRL   PARTIAL_RULED. k fixed AND b* held at one level, with N and p moving.
              RULED prints only the k POSITIVE reports, so holding k fixed is what holds
              LENGTH fixed here — the opposite lever from FULLCTRL. Mixedness varies
              through N.

  JOINT       not a separate sweep: the FULLCTRL cells are also run in PARTIAL_RULED, so
              silence cost = s1(RULED) - s1(FULL) is measurable on identical cells as a
              function of mixedness. RULED's length DOES vary across those cells (it
              prints k lines), which is why RULEDCTRL exists as the clean RULED check.
              JOINT measures the difference; RULEDCTRL measures RULED's own slope.

Prompt wording, response schema, mirror convention and level bands are imported verbatim
from silence_v2_stimuli so these cells are directly comparable to the main campaign.
"""

import argparse
import hashlib
import json
import math
from fractions import Fraction as F

import silence_v2_model as M
import silence_v2_stimuli as S

# ---- sweep definitions ------------------------------------------------------
PARABOLA_P, PARABOLA_N = 62, 11          # 11/12 k values land in measured safe bands
FULLCTRL_N = 11
FULLCTRL_TARGET = math.log(9)            # b* ~ 0.90, level 3
FULLCTRL_K = (6, 7, 8, 9, 10, 11)
RULEDCTRL_K = 3
RULEDCTRL_TARGET = math.log(1 / 9)       # b* ~ 0.10, level 0
RULEDCTRL_N = (7, 9, 11, 13, 15)


def p_compensating(target_logodds, k, N):
    """Integer-percent p making log-odds(b*) closest to target for this (k, N)."""
    d = 2 * k - N
    if d == 0:
        return None
    want = target_logodds / d
    if want <= 0:
        return None
    best, err = None, None
    for pn in range(51, 96):
        L = math.log(F(pn, 100) / (1 - F(pn, 100)))
        e = abs(L - want)
        if err is None or e < err:
            best, err = pn, e
    return best


def cells():
    out = []
    for k in range(PARABOLA_N + 1):
        out.append(dict(id=f"P{k:02d}", sweep="PARABOLA", p=PARABOLA_P,
                        N=PARABOLA_N, k=k, arms=("FULL",)))
    for k in FULLCTRL_K:
        pn = p_compensating(FULLCTRL_TARGET, k, FULLCTRL_N)
        out.append(dict(id=f"F{k:02d}", sweep="FULLCTRL", p=pn, N=FULLCTRL_N, k=k,
                        arms=("FULL", "PARTIAL_RULED")))          # JOINT rides here
    for N in RULEDCTRL_N:
        pn = p_compensating(RULEDCTRL_TARGET, RULEDCTRL_K, N)
        out.append(dict(id=f"R{N:02d}", sweep="RULEDCTRL", p=pn, N=N, k=RULEDCTRL_K,
                        arms=("PARTIAL_RULED",)))
    for c in out:
        p = F(c["p"], 100)
        c["b_star"] = M.b_star(p, c["N"], c["k"])
        c["b_pos"] = M.b_pos(p, c["k"])
        c["level_correct"] = M.level(c["b_star"])       # FULL and RULED share b* at d=0
        c["level_b_pos"] = M.level(c["b_pos"])
        c["mixedness"] = c["k"] * (c["N"] - c["k"])
        c["in_band"] = M.in_band(c["b_star"]) is not None
        c["edge_distance"] = min(abs(float(c["b_star"]) - e)
                                 for e in (0.25, 0.50, 0.75))
    return out


def build(cs):
    stims = []
    for c in cs:
        p = F(c["p"], 100)
        for target_first in (True, False):
            first, second = S.LABELS
            target_label = first if target_first else second
            p_first = p if target_first else 1 - p
            for arm in c["arms"]:
                belief = c["b_star"] if arm in ("FULL", "PARTIAL_RULED") else c["b_pos"]
                pf = belief if target_first else 1 - belief
                cand, conf, _ = S.answer_from_p_first(pf)
                stims.append({
                    "id": f"{c['id']}-{arm}-m{0 if target_first else 1}",
                    "cell": c["id"], "sweep": c["sweep"], "condition": arm,
                    "group": c["id"][0],
                    "target_is_first": target_first, "target_label": target_label,
                    "p": c["p"] / 100, "N": c["N"], "k": c["k"],
                    "mixedness": c["mixedness"],
                    "level_correct": c["level_correct"],
                    "level_b_pos": c["level_b_pos"],
                    "b_star": round(float(c["b_star"]), 6),
                    "in_band": c["in_band"],
                    "edge_distance": round(c["edge_distance"], 4),
                    "expected_candidate": cand, "expected_confidence": conf,
                    "prompt": S.prompt(arm, c["N"], c["k"], first, second,
                                       p_first, 1 - p_first),
                    "response_format": S.schema(),
                })
    return stims


def check(cs, stims):
    assert len({s["id"] for s in stims}) == len(stims)

    # PARABOLA: prompt length constant across k (FULL prints N lines regardless)
    par = [s for s in stims if s["sweep"] == "PARABOLA" and s["target_is_first"]]
    lens = {len(s["prompt"]) for s in par}
    assert max(lens) - min(lens) <= 12, f"PARABOLA length varies: {sorted(lens)}"
    assert {c["k"] for c in cs if c["sweep"] == "PARABOLA"} == set(range(PARABOLA_N + 1))

    # FULLCTRL: length constant AND correct level constant
    fc = [c for c in cs if c["sweep"] == "FULLCTRL"]
    assert len({c["level_correct"] for c in fc}) == 1, "FULLCTRL level not constant"
    assert all(c["in_band"] for c in fc), "FULLCTRL cell outside a measured band"
    fl = {len(s["prompt"]) for s in stims
          if s["sweep"] == "FULLCTRL" and s["condition"] == "FULL" and s["target_is_first"]}
    assert max(fl) - min(fl) <= 12, f"FULLCTRL FULL length varies: {sorted(fl)}"
    assert len({c["mixedness"] for c in fc}) == len(fc), "FULLCTRL mixedness not varied"

    # RULEDCTRL: length constant (k fixed) AND correct level constant
    rc = [c for c in cs if c["sweep"] == "RULEDCTRL"]
    assert len({c["level_correct"] for c in rc}) == 1, "RULEDCTRL level not constant"
    assert all(c["in_band"] for c in rc), "RULEDCTRL cell outside a measured band"
    assert len({c["k"] for c in rc}) == 1
    rl = {len(s["prompt"]) for s in stims
          if s["sweep"] == "RULEDCTRL" and s["target_is_first"]}
    assert max(rl) - min(rl) <= 12, f"RULEDCTRL length varies: {sorted(rl)}"
    assert len({c["mixedness"] for c in rc}) == len(rc)

    # JOINT: FULLCTRL cells exist in both arms with the SAME correct answer
    for c in fc:
        pair = {s["condition"]: s for s in stims
                if s["cell"] == c["id"] and s["target_is_first"]}
        assert set(pair) == {"FULL", "PARTIAL_RULED"}
        assert (pair["FULL"]["expected_candidate"],
                pair["FULL"]["expected_confidence"]) == \
               (pair["PARTIAL_RULED"]["expected_candidate"],
                pair["PARTIAL_RULED"]["expected_confidence"]), \
               f"{c['id']}: FULL/RULED correct answers differ"
        assert pair["FULL"]["prompt"] != pair["PARTIAL_RULED"]["prompt"]

    # mirror is a pure relabelling
    for c in cs:
        for arm in c["arms"]:
            pr = [s for s in stims if s["cell"] == c["id"] and s["condition"] == arm]
            assert len(pr) == 2
            assert pr[0]["expected_confidence"] == pr[1]["expected_confidence"]
            assert pr[0]["expected_candidate"] != pr[1]["expected_candidate"]

    # record contents match k and N
    for s in stims:
        assert s["prompt"].count("Assay returned POSITIVE") == s["k"]
        if s["condition"] == "FULL":
            assert s["prompt"].count("Assay returned NEGATIVE") == s["N"] - s["k"]
    return True


def freeze(stims, path="sweep_stimuli.json"):
    payload = {"task": "2.4b mixedness sweeps", "wording": S.CONF,
               "sweeps": sorted({s["sweep"] for s in stims}),
               "n_stimuli": len(stims), "stimuli": stims}
    blob = json.dumps(payload, indent=2, sort_keys=True)
    d = hashlib.sha256(blob.encode()).hexdigest()
    payload["sha256"] = d
    json.dump(payload, open(path, "w"), indent=2, sort_keys=True)
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", default=None)
    a = ap.parse_args()

    cs = cells()
    stims = build(cs)
    check(cs, stims)
    d = freeze(stims)

    if a.show:
        for s in stims:
            if s["cell"] == a.show and s["target_is_first"]:
                print("#" * 70)
                print(f"{s['id']}  expected {s['expected_confidence']} / "
                      f"{s['expected_candidate']}  (level {s['level_correct']}, "
                      f"mixedness {s['mixedness']}, {len(s['prompt'])} chars)")
                print("#" * 70)
                print(s["prompt"])
        raise SystemExit

    for sw in ("PARABOLA", "FULLCTRL", "RULEDCTRL"):
        print(f"\n{sw}")
        print(f"  {'cell':<6}{'p':>6}{'N':>4}{'k':>4}{'mix':>6}{'b*':>8}"
              f"{'Lcor':>6}{'band':>6}{'edge':>7}{'FULLch':>8}{'RULEDch':>9}")
        for c in cs:
            if c["sweep"] != sw:
                continue
            ch = {s["condition"]: len(s["prompt"]) for s in stims
                  if s["cell"] == c["id"] and s["target_is_first"]}
            print(f"  {c['id']:<6}{c['p']/100:>6.2f}{c['N']:>4}{c['k']:>4}"
                  f"{c['mixedness']:>6}{float(c['b_star']):>8.3f}"
                  f"{c['level_correct']:>6}{'ok' if c['in_band'] else 'DEAD':>6}"
                  f"{c['edge_distance']:>7.3f}"
                  f"{ch.get('FULL', '-'):>8}{ch.get('PARTIAL_RULED', '-'):>9}")

    n = len(stims)
    print(f"\n{len(cs)} cells, {n} stimuli   sha256 {d}")
    print(f"{n} x 5 draws x 7 configs = {n*5*7} calls")
    print(f"  JOINT rides on FULLCTRL: {len(FULLCTRL_K)} cells in both arms")
    dead = [c['id'] for c in cs if not c['in_band']]
    print(f"  dead-zone cells (analyser has a lever to drop these): {dead or 'none'}")
