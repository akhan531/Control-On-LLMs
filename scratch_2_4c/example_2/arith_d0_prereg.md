# ARITH_D0 pre-registration

**Date:** 2026-08-17, written and frozen BEFORE any ARITH_D0 API call.
**Approved by:** Ali (collection of 980 calls approved this session; run itself gated
on a separate explicit go).
**Stimuli:** `scratch_2_4c/arith_d0_stimuli.json`, sha256
`028d9be8f4809ecbdebf645a520ffaf4344e386d4fe9e75a809aea4dc60751d0`, 28 stimuli
(14 cells × 2 mirrors), all build-time assertions passed.
**Harness:** `scratch_2_4c/arith_d0_harness.py` — byte-parallel copy of the ARITH_D30
harness (same roster, budgets, defences: preflight, 401 fail-fast, resume on settled
draws, TRUNCATED retryable via `--bump`, PARSE terminal per D16). Output only under
`scratch_2_4c/results_arith_d0/`.

## Design

The only closable identification/interpretation ladder, all rungs sharing correct
answer `b*` per cell (pivot: `q(0) = b*` exactly):

| rung | shows | observer must | status |
|---|---|---|---|
| PARTIAL_RULED | k positives, N, rule | identify absences + substitute + aggregate | frozen, on disk |
| **ARITH_D0** | + one `Filed nothing at all` line per silent analyst | substitute + aggregate | **this run** |
| FULL | all N results printed as results | aggregate only | frozen, on disk |

At δ=0 a non-filing is a certain negative, so "interpretation" is deterministic
substitution — the δ=0.3 pair (RULED_D30/ARITH_D30, already on disk) holds the same
comparison with probabilistic interpretation. Record length: ARITH_D0 and FULL both
print N record lines (length-matched); RULED is the short arm — so any
length-degradation artifact runs AGAINST the null prediction P-null below.

R1 is deliberately violated (enumerated non-filings are silence vocabulary in
function), recorded, exactly as ARITH_D30.

## Population discipline (fixed before the run)

- **Gate:** δ=0 claims gate on the frozen FULL gate (mean s1 < 1.0, draw level, all
  14 cells): claim population {sol-none, sol-high, deepseek-high, glm, glm-high};
  deepseek and anchor computed and reported as context.
- **P4 exclusions inherited:** anchor loses B1, B3, D1–D3; sol-none loses B1.
- Failures counted per config; deepseek-family PARSE expected from history.

## Registered statistics

1. Draw-level `s1`, `s2` per config per arm on the matched 14-cell set (minus P4).
2. Paired per-cell Δ`s1` and Δ`s2`: ARITH_D0 − RULED_D0 and ARITH_D0 − FULL.
3. Location classes (OVER / COR / INT / POS / BEY, Example-1 definitions) and
   occupancies `π_cor`, `π_pos` across all three rungs. Expressibility ledger as in
   Example 1 (OVER only in D cells; BEY only where `l_pos = 2`).
4. **Localization index** per gated config:
   `λ = (s1_ARITH − s1_FULL) / (s1_RULED − s1_FULL)`, cell-weighted draw-level means.
   Descriptive index on unnormalized bin errors (NOT ordinal-s). **Ceiling guard:**
   a config with `s1_RULED − s1_FULL < 0.15` bins is declared uninformative for
   localization (expected: sol-high; possibly glm-high).
5. Secondary probes: D-cell OVER mass (ARITH_D0 vs RULED_D0) — does enumeration push
   answers below a correct mid-level answer even at δ=0; C/D count-control modal
   concordance within ARITH_D0 (P5 analogue); modal-level paired tables; mirror
   agreement; reasoning-token comparison across rungs for the three token-emitting
   configs (supporting exhibit only, per earlier ruling).

## Registered competing predictions (both outcomes usable; no directional bet)

- **P-null (transfer from δ=0.3):** enumeration does not help — λ ≈ 1 for the
  informative gated configs; ARITH_D0 ≈ RULED_D0 and both displaced from FULL. Reads
  as: the silence deficit lives in *using* absences (substitution/aggregation under
  an inference the model must own), not in *finding* them.
- **P-identify:** λ ≈ 0 — ARITH_D0 ≈ FULL. Reads as: the deficit at δ=0 was
  identification; enumeration repairs it, and the δ=0.3 null localizes to the
  probabilistic-interpretation step specific to stated dropout.
- Interior λ (≈ 0.3–0.7) or config-heterogeneous λ: reported as measured; no claim
  without a verification design.

## Analysis order

The δ=0.3 redistribution pattern was observed before this arm was proposed; ARITH_D0
is the out-of-regime test. After data lands: pattern reading, then verification
designs with pre-fixed kill conditions presented for approval BEFORE running them
(session protocol). Known confounds already named for that stage: per-line length
effects (N−k spans 2–9 across cells, testable within-arm), semantics of the
`Filed nothing at all` line, deepseek-family missingness.
