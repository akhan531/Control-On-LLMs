"""
s5_e2_tests.py — Verification V-E2-1..4 for Example 2 (approved 2026-08-17).

V-E2-1  record-shape mimicry cross-tab. A pure line-counter repairs fully at d=0 AND
        over-reads toward q(0) at d=0.3. STANDS for a config iff repair-fraction
        (1 - lambda) >= 0.70 AND ARITH_D30 below-cor mass >= 15% AND the level-q(0)
        component of that mass >= half of it.
V-E2-2  implied channel d_hat: per draw, invert the observed level's measured band to
        the interval of delta making q(delta) land there (q monotone b* -> b_pos).
        Categories: OVER-price (interval < 0.3; subcase CERTAINTY if it contains 0),
        CORRECT (contains 0.3), UNDER-price (interval > 0.3), OFF (unreachable).
        Universal certainty-pricing DIES unless a majority of mover configs have
        >= 50% of their below-cor ARITH_D30 draws certainty-consistent.
V-E2-3  per-line vs semantic gain at d=0. Collinearity audit first: if
        |r(N-k, per-cell silence deficit)| > 0.6 the test is UNIDENTIFIABLE and
        reported as such. Else partial r(gain, N-k | deficit) >= +0.5 -> per-line
        account STANDS.
V-E2-4  robustness: (a) worst-case missingness reassignment for both panels;
        (b) mirror split; (c) cross-regime contrast on the 9 shared cells as
        fraction-of-own-deficit (kill: not 5/5 strict); (d) ARITH_D0 count-control
        concordance table.

Data: the four quadrants + FULL, all on disk. Gate: FULL gate (gated five) for d=0;
all-seven under the frozen ARITH gate at d=0.3. P4 inherited. Stdout only.
"""

import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
GATED = ("sol-none", "sol-high", "deepseek-high", "glm", "glm-high")
ORDER = GATED + ("deepseek", "anchor")
CELLS14 = ("A1", "A2", "A3", "A4", "A5", "C1", "C2", "C3",
           "B1", "B2", "B3", "D1", "D2", "D3")
SHARED9 = ("A1", "A2", "A3", "A4", "A5", "B1", "C1", "C2", "C3")
CEILING = ("sol-high", "glm-high")
NONCEIL = ("sol-none", "deepseek-high", "glm", "deepseek", "anchor")


def mode(v):
    if not v:
        return None
    c = Counter(v).most_common()
    return None if len(c) > 1 and c[0][1] == c[1][1] else c[0][0]


def ingest(res_path, stim_path, cond_map, draws, fails, p4):
    res = json.load(open(f"{ROOT}/{res_path}"))
    stim = {s["id"]: s for s in json.load(open(f"{ROOT}/{stim_path}"))["stimuli"]}
    for r in res["records"]:
        st = stim[r["stimulus_id"]]
        rung = cond_map.get(st["condition"])
        if rung is None:
            continue
        if st["cell"] in p4.get(r["config"], []):
            continue
        if not r.get("ok"):
            fails[(r["config"], rung)] += 1
            continue
        lv = S.target_level(r["candidate"], r["confidence"], st["target_label"])
        draws[(r["config"], rung, st["cell"], st["target_is_first"])].append(
            (lv, st["level_target"]))


def pool(draws, cfg, rung, cid):
    out = []
    for m in (True, False):
        out.extend(draws.get((cfg, rung, cid, m), []))
    return out


def cellmean(draws, cfg, rung, cid):
    v = pool(draws, cfg, rung, cid)
    return None if not v else sum(abs(lv - lc) for lv, lc in v) / len(v)


def arm_s1(draws, cfg, rung, cells):
    vals = [x for cid in cells for x in pool(draws, cfg, rung, cid)]
    return None if not vals else sum(abs(lv - lc) for lv, lc in vals) / len(vals)


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return None if sxx == 0 or syy == 0 else sxy / (sxx * syy) ** 0.5


def main():
    p4 = json.load(open(f"{ROOT}/results_v2/v2_gates.json"))["P4_excluded"]
    d0, f0 = defaultdict(list), Counter()
    ingest("results_v2/v2_results_live.json", "silence_v2_stimuli.json",
           {"PARTIAL_RULED": "R", "FULL": "F"}, d0, f0, p4)
    ingest("scratch_2_4c/example_2/results_arith_d0/arith_d0_results_live.json",
           "scratch_2_4c/example_2/arith_d0_stimuli.json",
           {"ARITH_D0": "A"}, d0, f0, p4)
    d3, f3 = defaultdict(list), Counter()
    ingest("results_v2/v2_results_live_banked.json", "silence_v2_stimuli_banked.json",
           {"PARTIAL_RULED_D30": "R"}, d3, f3, p4)
    ingest("scratch_fable/results_arith/arith_results_live.json",
           "scratch_fable/arith_d30_stimuli.json", {"ARITH_D30": "A"}, d3, f3, p4)

    cells = {c["id"]: c for c in M.build()}
    l30 = {cid: M.level(cells[cid][f"q_{F(3,10)}"]) for cid in SHARED9}
    lq0 = {cid: M.level(cells[cid][f"q_{F(0)}"]) for cid in SHARED9}

    # ================= V-E2-1 =================
    print("V-E2-1  RECORD-SHAPE MIMICRY CROSS-TAB")
    print(f"  {'config':<15}{'repair(1-l)':>12}{'d30 below%':>11}"
          f"{'ATQ0 share':>11}   verdict on mimicry")
    for cfg in ORDER:
        sR, sA, sF = [], [], []
        for cid in CELLS14:
            r, a, f = (cellmean(d0, cfg, x, cid) for x in ("R", "A", "F"))
            if None not in (r, a, f):
                sR.append(r); sA.append(a); sF.append(f)
        mR, mA, mF = (sum(x)/len(x) for x in (sR, sA, sF))
        if mR - mF < 0.15:
            rep = None
        else:
            rep = (mR - mA) / (mR - mF)
        below = atq0 = n = 0
        for cid in SHARED9:
            for lv, lc in pool(d3, cfg, "A", cid):
                n += 1
                if lv < lc:
                    below += 1
                    atq0 += (lv == lq0[cid])
        bpct = 100 * below / n
        ashare = (atq0 / below) if below else 0.0
        if rep is None:
            verdict = "n/a (ceiling at d=0)"
        elif rep >= 0.70 and bpct >= 15 and ashare >= 0.5:
            verdict = "mimicry STANDS"
        else:
            verdict = "mimicry dies"
        tag = "" if cfg in GATED else "  [excl]"
        print(f"  {cfg:<15}{('--' if rep is None else f'{rep:.2f}'):>12}"
              f"{bpct:>10.1f}%{ashare:>11.2f}   {verdict}{tag}")

    # ================= V-E2-2 =================
    print("\nV-E2-2  IMPLIED CHANNEL d_hat (delta=0.3 arms; stated channel 0.30)")

    def qf(cid, d):
        c = cells[cid]
        p, N, k = float(c["p"]), c["N"], c["k"]
        a = ((1 - d) * p) ** k * (1 - (1 - d) * p) ** (N - k)
        b = ((1 - d) * (1 - p)) ** k * (1 - (1 - d) * (1 - p)) ** (N - k)
        return a / (a + b)

    def solve(cid, target):
        lo, hi = 0.0, 0.999
        if qf(cid, lo) >= target:
            return 0.0
        if qf(cid, hi) <= target:
            return None
        for _ in range(60):
            mid = (lo + hi) / 2
            if qf(cid, mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    def dhat_interval(cid, lv):
        lo_b, hi_b = M.BANDS[lv]
        a = solve(cid, lo_b)
        b = solve(cid, hi_b)
        if a is None:
            return None                       # band above trajectory: unreachable
        b = 0.999 if b is None else b
        if qf(cid, 0.0) > hi_b:
            return None                       # band below trajectory start
        return (a, b)

    print(f"  {'config':<15}{'arm':<5}{'%over':>7}{'(cert)':>8}{'%corr':>7}"
          f"{'%under':>8}{'%off':>6}{'median mid':>11}")
    cert_share = {}
    for cfg in ORDER:
        for arm in ("R", "A"):
            cats = Counter()
            mids = []
            below_cert = below_n = 0
            for cid in SHARED9:
                for lv, lc in pool(d3, cfg, arm, cid):
                    iv = dhat_interval(cid, lv)
                    if iv is None:
                        cats["off"] += 1
                        continue
                    a, b = iv
                    mids.append((a + b) / 2)
                    if a <= 0.30 <= b:
                        cats["corr"] += 1
                    elif b < 0.30:
                        cats["over"] += 1
                        if a <= 0.02:
                            cats["cert"] += 1
                    else:
                        cats["under"] += 1
                    if lv < lc:
                        below_n += 1
                        below_cert += (a <= 0.02)
            n = sum(cats[k] for k in ("over", "corr", "under", "off"))
            mids.sort()
            med = mids[len(mids)//2] if mids else float("nan")
            if arm == "A":
                cert_share[cfg] = (below_cert / below_n) if below_n else None
            print(f"  {cfg:<15}{'RULED' if arm=='R' else 'ARITH':<5}"
                  f"{100*cats['over']/n:>7.1f}{100*cats['cert']/n:>8.1f}"
                  f"{100*cats['corr']/n:>7.1f}{100*cats['under']/n:>8.1f}"
                  f"{100*cats['off']/n:>6.1f}{med:>11.2f}")
    movers = ("sol-none", "deepseek-high", "glm", "deepseek", "anchor")
    maj = [cfg for cfg in movers
           if cert_share.get(cfg) is not None and cert_share[cfg] >= 0.5]
    print(f"  movers with >=50% certainty-consistent below-cor mass: {maj} "
          f"({len(maj)}/{len(movers)}) -> universal certainty-pricing "
          f"{'STANDS' if len(maj) > len(movers)/2 else 'DIES'}")
    print("  cert-share detail: " + ", ".join(
        f"{c}: {'--' if cert_share.get(c) is None else f'{cert_share[c]:.2f}'}"
        for c in movers))

    # ================= V-E2-3 =================
    print("\nV-E2-3  PER-LINE VS SEMANTIC GAIN AT d=0")
    print(f"  {'config':<15}{'r(nk,def)':>10}{'identifiable':>13}"
          f"{'partial r(g,nk|def)':>20}   verdict on per-line")
    for cfg in ("sol-none", "deepseek-high", "glm", "deepseek", "anchor"):
        pts = []
        for cid in CELLS14:
            r, a, f = (cellmean(d0, cfg, x, cid) for x in ("R", "A", "F"))
            if None in (r, a, f):
                continue
            c = cells[cid]
            pts.append((c["N"] - c["k"], r - f, r - a))    # nk, deficit, gain
        nk = [p[0] for p in pts]
        de = [p[1] for p in pts]
        g = [p[2] for p in pts]
        r_nd = pearson(nk, de)
        if r_nd is not None and abs(r_nd) > 0.6:
            print(f"  {cfg:<15}{r_nd:>+10.3f}{'NO':>13}{'--':>20}   UNIDENTIFIABLE")
            continue
        r_gn, r_gd, r_nd2 = pearson(g, nk), pearson(g, de), r_nd
        if None in (r_gn, r_gd, r_nd2):
            print(f"  {cfg:<15}{'--':>10}{'--':>13}{'--':>20}   n/a")
            continue
        den = ((1 - r_gd**2) * (1 - r_nd2**2)) ** 0.5
        pr = (r_gn - r_gd * r_nd2) / den if den else float("nan")
        verdict = "per-line STANDS" if pr >= 0.5 else "per-line dies"
        tag = "" if cfg in GATED else "  [excl]"
        print(f"  {cfg:<15}{r_nd:>+10.3f}{'yes':>13}{pr:>+20.3f}   {verdict}{tag}")

    # ================= V-E2-4 =================
    print("\nV-E2-4a  WORST-CASE MISSINGNESS (d=0 panel: d_s1 A-R must stay < 0 "
          "for non-ceiling; d=0.3 panel: improvement bound)")
    for regime, dd, ff, cellset in (("d0", d0, f0, CELLS14), ("d30", d3, f3, SHARED9)):
        for cfg in ORDER:
            fr, fa = ff.get((cfg, "R"), 0), ff.get((cfg, "A"), 0)
            if fr == 0 and fa == 0:
                continue
            vR = [x for cid in cellset for x in pool(dd, cfg, "R", cid)]
            vA = [x for cid in cellset for x in pool(dd, cfg, "A", cid)]
            worst = 3  # max |lv - l_cor| given l_cor <= 2 everywhere
            # direction 1: make ARITH look worst (A fails -> max error, R fails -> 0)
            a_hi = (sum(abs(a - b) for a, b in vA) + fa * worst) / (len(vA) + fa)
            r_lo = sum(abs(a - b) for a, b in vR) / (len(vR) + fr)
            # direction 2: make ARITH look best
            a_lo = sum(abs(a - b) for a, b in vA) / (len(vA) + fa)
            r_hi = (sum(abs(a - b) for a, b in vR) + fr * worst) / (len(vR) + fr)
            print(f"  {regime:<4}{cfg:<15}fails R{fr}/A{fa}   "
                  f"d_s1 range [{a_lo - r_hi:+.3f}, {a_hi - r_lo:+.3f}]")

    print("\nV-E2-4b  MIRROR SPLIT (sign of d_s1 A-R per mirror)")
    for regime, dd, cellset in (("d0", d0, CELLS14), ("d30", d3, SHARED9)):
        row = f"  {regime:<5}"
        for cfg in ORDER:
            signs = []
            for m in (True, False):
                vR = [x for cid in cellset for x in dd.get((cfg, "R", cid, m), [])]
                vA = [x for cid in cellset for x in dd.get((cfg, "A", cid, m), [])]
                sr = sum(abs(a - b) for a, b in vR) / len(vR)
                sa = sum(abs(a - b) for a, b in vA) / len(vA)
                signs.append(sa - sr)
            row += f"  {cfg[:8]}:{signs[0]:+.2f}/{signs[1]:+.2f}"
        print(row)

    print("\nV-E2-4c  CROSS-REGIME CONTRAST, 9 SHARED CELLS, FRACTION OF OWN DEFICIT")
    print(f"  {'config':<15}{'d0 s1 R':>9}{'d0 gain%':>9}{'d30 s1 R':>10}"
          f"{'d30 gain%':>10}   strict?")
    strict = 0
    for cfg in NONCEIL:
        r0 = arm_s1(d0, cfg, "R", SHARED9)
        a0 = arm_s1(d0, cfg, "A", SHARED9)
        r3 = arm_s1(d3, cfg, "R", SHARED9)
        a3 = arm_s1(d3, cfg, "A", SHARED9)
        g0 = (r0 - a0) / r0
        g3 = (r3 - a3) / r3
        ok = g0 > g3
        strict += ok
        tag = "" if cfg in GATED else "  [excl]"
        print(f"  {cfg:<15}{r0:>9.3f}{100*g0:>8.1f}%{r3:>10.3f}{100*g3:>9.1f}%"
              f"   {'yes' if ok else 'NO'}{tag}")
    print(f"  strict in {strict}/{len(NONCEIL)}  -> contrast "
          f"{'holds' if strict == len(NONCEIL) else 'DIES'} "
          "(kill bar: 5/5)")

    print("\nV-E2-4d  ARITH_D0 COUNT-CONTROL CONCORDANCE (modal across k; t=tie)")
    for cfg in ORDER:
        parts = []
        ok = True
        for grp in (("C1", "C2", "C3"), ("D1", "D2", "D3")):
            ms = []
            for c in grp:
                if c in p4.get(cfg, []):
                    ms.append("x")
                    continue
                m = mode([lv for lv, _ in pool(d0, cfg, "A", c)])
                ms.append("t" if m is None else m)
            real = [m for m in ms if isinstance(m, int)]
            if len(set(real)) > 1:
                ok = False
            parts.append(f"{grp[0][0]}:" + "/".join(str(m) for m in ms))
        print(f"  {cfg:<15}{'PASS' if ok else 'FAIL':<6}" + "   ".join(parts))


if __name__ == "__main__":
    main()
