# Part C / G — recompute of the PASS-LEDGER numbers (read-only)

Recomputed from scripts and formulas, not re-read from the ledger. Order as requested.
Verdict: all five groups **agree** across main.tex, ledger, and recompute — no new MISMATCH.
(Analytic groups were re-derived from the model's closed form; draw groups were re-run.)

## Group 1 — §5 recovery bounds (12.5 / 8.0 / 0.20-bin) — DRAW-DERIVED
Source: `s3_arith_summary.py` (per-arm s1, δ=0.3) + `s5_e2_tests.py` V-E2-4a.
Recovery = 1 − s1(ARITH_D30)/s1(RULED_D30).

| number | main.tex | ledger | recomputed | verdict |
|---|---|---|---|---|
| 12.5% (max, all seven) | 12.5 | 12.5 | anchor 1.000→0.875 = **12.5%** | agree |
| 8.0% (max, admitted) | 8.0 | 8.0 | sol-none 0.625→0.575 = **8.0%** | agree |
| 0.20 bins (worst-case missingness) | 0.20 | 0.20 | glm-high V-E2-4a range [−0.200, −0.033] = **0.200** | agree |

Nuance (not a mismatch): glm-high's raw recovery % is large (0.059→0.022 ≈ 63%) but its absolute
deficit is ~0.06 bins and it is ceiling-flagged; "no configuration recovers more than 12.5%"
holds over configs with a testable deficit, where anchor (12.5%) is the max.

## Group 2 — §6 dial nats (5.61 / 1.83 / 0.71) and p 0.90→0.56 — ANALYTIC
Source: `s3_dial_summary.py`, closed form over (N, N−k, p); no draws. Re-derived:

| cell | N | N−k | p | eps (nats) | main.tex |
|---|---|---|---|---|---|
| R07 | 7 | 4 | 0.90 | **5.61** | 5.61 |
| R09 | 9 | 6 | 0.68 | **1.83** | 1.83 |
| R15 | 15 | 12 | 0.56 | **0.71** | 0.71 |

N−k 4→12 and p 0.90→0.56 both reproduce. agree.

## Group 3 — §6 eps values (3.84; 0.065 / 0.080 / 0.064) — ANALYTIC
Source: `silence_v2_model.py` `eps0` column, closed form. Re-derived:

| cell | eps0 | main.tex |
|---|---|---|
| C1 | **3.839** | 3.84 |
| D1 | **0.065** | 0.065 |
| D2 | **0.080** | 0.080 |
| D3 | **0.064** | 0.064 |

agree. (Also confirms D-cell b* = 0.440/0.421/0.440.) The A5 ratio span: 3.839/0.080 = **48.0**
to 3.839/0.064 = **60.0** — so "between roughly fifty and sixty times" is right at the top (60)
and slightly loose at the bottom (48).

## Group 4 — §5 per-line effect (−0.89 to +0.17) and |r| 0.34 — DRAW-DERIVED
Source: `s5_e2_tests.py` V-E2-3.

| number | main.tex | recomputed | verdict |
|---|---|---|---|
| per-line partial r span | −0.89 to +0.17 | partial r(g,nk\|def): anchor **−0.886** … deepseek **+0.170** | agree |
| collinearity bound | 0.34 | max \|r(nk,def)\| = deepseek **0.339** | agree |

(Both endpoints come from gate-excluded configs; the claim is "per-line dies anywhere," all seven.)

## Group 5 — W1 pre-test (659/672) and asymmetry — DRAW-DERIVED
Source: `w1_analyze.py`, `w1_addendum_lowside.py`.

| number | main.tex | recomputed | verdict |
|---|---|---|---|
| usable | 659/672 | **659/672** | agree |
| asymmetry, six of seven | 0.000 at widest | 0.000 at widest | agree |
| anchor asymmetry | 0.1 | anchor B **0.1** (low 0.2, high 0.3) | agree |
| anchor reachability | 2 of 4 on wording A | **{A:2, B:4}**, switch A=0.6→B=0.8 MOVES | agree |
| switch edges | 0.20 / 0.80 | transitions at 0.20 (low) / 0.80 (high) | agree |

## Summary
- **No new MISMATCH.** Here the ledger and the data agree; the sol-high defect (Part B) remains
  the only ledger/data disagreement found.
- **Analytic vs draw-derived:** Groups 2 and 3 are analytic (re-derived from the model's closed
  form over cell parameters); Groups 1, 4, 5 are draw-derived (scripts re-run on draw records).
- Nothing here requires a main.tex edit.
