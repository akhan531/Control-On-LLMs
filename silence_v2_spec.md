# Silence probe v2 — specification and pre-registration

**Task:** 2.4b, Phase 2 · **Instrument:** ordinal silence probe, wording B
**Status:** **FROZEN 2026-08-15.** Related-work pass cleared the same day: no direct hit on the
claim. One direct hit on a secondary positioning claim only (§11).
**Primary stimuli:** `silence_v2_stimuli.json`, sha256 `f9cd913ca85980bd0476a9a08c6414a498f1bb940637ab55ef37af2663549787`
**Banked stimuli:** `silence_v2_stimuli_banked.json`, sha256 `23d2c4c62ee0599ea64dc85be8da75b5c6fe52f57c2af6bc41da62f21383cce9`
**Supersedes:** `silence_probe_spec.md` (v1, numeric). v1 data is pilot and is not pooled.

---

## 1. Question

Can an LLM observer treat the *absence* of a report as evidence, when it has been told
the rule that generates the absence?

The v1 campaign answered yes, conditionally: `sol-high` recovered the silence-aware
posterior to within 0.005 nats while `sol-none` scored 0.145 on the same records, and the
contrast replicated on DeepSeek. v1's numeric instrument, however, could not separate that
from arithmetic competence, and four of six configurations failed its competence gate. v2
replaces continuous elicitation with a four-level ordinal response so the measurement
tolerates imprecise beliefs while remaining sensitive to the direction of inference.

## 2. Model

Two candidates, uniform prior. `N` analysts each run one conditionally independent assay
with `P(POSITIVE | target) = p`, `P(POSITIVE | other) = 1 − p`. An analyst files only on
POSITIVE.

| object | meaning | form |
|---|---|---|
| `b_pos` | positives-only belief; ignores absence | `∝ L(a)^k` |
| `q` | silence-aware belief under stated dropout `δ` | `∝ [(1−δ)L]^k · [1−(1−δ)L]^(N−k)` |
| `b*` | full-information posterior | `∝ L^k · (1−L)^(N−k)` |

At `δ = 0`, `q = b*` **exactly**, verified over rationals for every cell. This is the
design's pivot: it makes FULL and PARTIAL-RULED have the same correct answer, so the two
conditions differ only in whether the negatives are displayed or must be inferred.

`ε = D(q‖b_pos)` is the silence-modelling error the probe measures. `W̄ = D(b*‖q) = 0`
throughout, since the campaign runs at `δ = 0` only (§8).

## 3. Conditions

Three conditions on one underlying record.

| condition | shows | correct answer |
|---|---|---|
| FULL | all `N` results, completeness asserted, no rule | `b*` |
| PARTIAL-BLIND | the `k` POSITIVE reports; no `N`, no rule | `b_pos` |
| PARTIAL-RULED | the same `k` reports, plus `N` and the filing rule | `q(δ=0) = b*` |

FULL is a competence check, **not an admission gate** — v1 established that its numeric
version measured arithmetic, and that models failing it still read silence correctly in
direction. PARTIAL-BLIND is the sole admission gate.

## 4. Response format

Two enum fields, never one enum over combined options:

```json
{"candidate": "SIGMA", "confidence": "Very confident"}
```

`confidence ∈ {Somewhat confident, Very confident}` (wording B, D22). The four
`(candidate, confidence)` pairs form an ordinal scale over `P(target)`:

| level | answer | band |
|---|---|---|
| 3 | Very confident / target | ≥ 0.80 |
| 2 | Somewhat confident / target | 0.55 – 0.70 |
| 1 | Somewhat confident / other | 0.40 – 0.45 |
| 0 | Very confident / other | ≤ 0.20 |

**The bands are never stated to the model.** Telling it that "Very confident" means ≥ 0.75
re-imports the numeric elicitation the redesign exists to escape. The bands above are the
values measured in W1, inside which all seven configurations agreed with the nominal
0.25/0.50/0.75 cut. Every predicted belief in the grid sits inside a band, so no cell's
correct level depends on where a model's personal threshold falls.

Measuring the scale before using it is not an idiosyncratic detour. Dai (2026, arXiv
2603.09309) shows confidence scale design is not neutral: verbalized confidence is heavily
discretized, and granularity and boundary placement both change measured metacognitive
efficiency, with boundary compression degrading it. Using nominal edges without checking
where a model's actual edges sit is the error that finding warns against.

## 5. Statistic

```
s = (ℓ_obs − ℓ_pos) / (ℓ_q − ℓ_pos)
```

in the target frame, which is mirror-invariant. `ℓ_pos = level(b_pos)` is the anchor
because it is arm-invariant; `ℓ_q = level(q(δ=0))`. `s = 0` is silence-blind, `s = 1` is
fully silence-aware, and intermediate values are partial reading. Denominators are
non-zero in every cell by construction, asserted at build time.

**Cell is the unit of analysis.** Draws within a cell are pooled to a modal answer; cells
are the replicates. Overshoot (`s > 1`) is recorded as observed and not clipped.

**Count-control cells (groups C and D) are scored on answer concordance across `k`, not on
`s`.** Their purpose is to detect a model responding to record length rather than belief,
and group D sits at span 1 where `s` has no headroom.

## 6. Grid

14 cells, 8 at blind level 3 and 6 at level 2. `p/r = 0.60/0.40` is excluded throughout:
reserved to W1, so v2 is disjoint from both v1 and the pre-test.

| id | p | N | k | `b_pos` | L | `q(0) = b*` | L | span | role |
|---|---|---|---|---|---|---|---|---|---|
| A1 | 0.81 | 5 | 2 | 0.948 | 3 | 0.190 | 0 | 3 | backbone |
| A2 | 0.67 | 8 | 3 | 0.893 | 3 | 0.195 | 0 | 3 | backbone |
| A3 | 0.67 | 10 | 4 | 0.944 | 3 | 0.195 | 0 | 3 | backbone |
| A4 | 0.62 | 13 | 5 | 0.920 | 3 | 0.187 | 0 | 3 | backbone |
| A5 | 0.67 | 14 | 5 | 0.972 | 3 | 0.056 | 0 | 3 | backbone |
| C1 | 0.88 | 6 | 2 | 0.982 | 3 | 0.018 | 0 | 3 | count control |
| C2 | 0.79 | 8 | 3 | 0.982 | 3 | 0.066 | 0 | 3 | count control |
| C3 | 0.73 | 11 | 4 | 0.982 | 3 | 0.048 | 0 | 3 | count control |
| B1 | 0.57 | 11 | 3 | 0.700 | 2 | 0.196 | 0 | 2 | backbone |
| B2 | 0.62 | 5 | 1 | 0.620 | 2 | 0.187 | 0 | 2 | backbone |
| B3 | 0.59 | 8 | 2 | 0.674 | 2 | 0.189 | 0 | 2 | backbone |
| D1 | 0.56 | 5 | 2 | 0.618 | 2 | 0.440 | 1 | 1 | count control |
| D2 | 0.54 | 8 | 3 | 0.618 | 2 | 0.421 | 1 | 1 | count control |
| D3 | 0.53 | 10 | 4 | 0.618 | 2 | 0.440 | 1 | 1 | count control |

**Count controls.** C holds `b_pos = 0.982` at `k = 2, 3, 4` with `N = 6, 8, 11`; D holds
`b_pos = 0.618` at `k = 2, 3, 4` with `N = 5, 8, 10`. Constant belief, constant target
level, three record lengths, three group sizes. A model answering from record length must
contradict itself across a control group.

Every cell's levels are stable under D20's alternate 0.20/0.50/0.80 cut, asserted at build
time, so no result is an artifact of where the bins were drawn.

## 7. Prompt rules

Binding, asserted at build time, carried from v1 with R6 and R7 restated.

- **R1** No silence vocabulary anywhere. The observer must notice the absence; the prompt must never point at it.
- **R2** PARTIAL-BLIND states neither `N` nor the rule.
- **R3** No analyst identifiers. Reports are interchangeable lines.
- **R4** No argumentation, hints, or worked reasoning.
- **R5** Framed as reading a record, never as computing a posterior. No probability vocabulary in the instruction.
- **R6** The banked dropout clause is phrased as a filing rate, never as unreliability or suppression.
- **R7** FULL displays all `N` results and asserts completeness, so failure there is arithmetic and not an inference about coverage.

Mirror (A1.2): each cell appears twice, swapping which printed label carries `p`. The
mirror is a pure relabelling — same confidence, flipped candidate — asserted at build time.
FULL records are sorted, POSITIVE first (A1.1).

## 8. What is deliberately not run

**PARTIAL-RULED at `δ = 0.30` is designed, specified, generated, and banked (D26).**

It was cut because under an ordinal statistic it is mechanically *easier*, not harder.
Dropout weakens the silence signal, so `q(δ>0)` sits between `b_pos` and `q(0)`; the
denominator is always shorter there, and identical partial movement scores higher. A cell
with `ℓ_pos = 3`, `ℓ_q(0) = 0`, `ℓ_q(0.3) = 2` scores one bin of movement as 0.33 at `δ=0`
and 1.00 at `δ=0.3`. An arm intended as the harder test would have been the more forgiving
one.

Nine of fourteen cells are viable for the extension, pre-computed and asserted. Enabling
it is `RUN_BANKED = True` plus `--banked`, 630 calls. It writes to a separate file with its
own hash so the primary freeze is never disturbed.

**Cost of the cut, stated rather than omitted:** the trimming-versus-censoring bridge to de
Punder is lost, and because `W̄ = 0` throughout, the campaign only tests whether the
full-information posterior can be recovered — never whether residual uncertainty is
correctly represented.

## 9. Roster and run

Seven configurations: `sol-none`, `sol-high`, `deepseek`, `deepseek-high`, `glm`,
`glm-high`, `anchor`. Anchor is included on W1 evidence: it passed G1 at 32/32 determinism
under wording B, having failed v1's numeric gate by 3.83 nats.

84 stimuli × 5 draws × 7 configurations = **2,940 calls**, roughly fifteen minutes.

Harness defences, carried from v1's three bug classes: preflight call before the grid;
fail-fast on 401 rather than backoff; resume keyed on successful draws only; truncation
detected as truncation and never surfaced as a JSON parse error; `max_tokens` per config,
not global. Per-condition missingness audited before analysis.

---

## 10. Pre-registration

Written before collection. `s` is the modal-answer statistic of §5, computed per cell.

**P1 — default-mode configurations are silence-blind.**
For `sol-none`, `deepseek`, `glm`: mean `s < 0.25` in PARTIAL-RULED, and the modal answer
equals the PARTIAL-BLIND answer in at least 8 of the 11 non-control cells.

**P2 — high-effort configurations read silence.**
For `sol-high`, `deepseek-high`, `glm-high`: mean `s > 0.75`, and the modal answer equals
`level(q(0))` in at least 8 of 11 non-control cells.

**P3 — the dissociation is within-model.** *Primary.*
In at least two of the three families, `s(high) − s(none) > 0.5` on identical records with
one parameter changed. P3 is the headline; P1 and P2 are its halves.

**P4 — the admission gate.**
PARTIAL-BLIND yields `s = 0` by construction. Any cell × configuration where the modal
PARTIAL-BLIND answer differs from `level(b_pos)` is excluded from P1–P3 and reported as
excluded. Pre-committed: exclusion is per cell × configuration, never per configuration.

**P5 — count controls hold.**
Within groups C and D, a configuration's modal answer is constant across `k` in each
condition. A configuration failing this is responding to record length; its cells do not
support P1–P3 and are reported separately.

**Falsification.** P3 fails if no family shows the gap. That outcome would mean the
capability is not effort-gated, and the paper becomes a negative-results report against
EIML3's evaluation topic rather than a dissociation claim.

**Diagnostic, not a result.** If `sol-high` returns `s ≈ 0`, the ordinal instrument has
lost an effect the numeric one found at 0.005 nats. That is an instrument failure to
diagnose, not a finding to report.

**Secondary, reported without a threshold:** FULL accuracy per configuration; determinism
across the 5 draws, against W1's per-configuration baseline; mirror agreement per D18;
off-menu exclusion counts per D16; `s` stratified by span, since span-3 and span-1 cells
are not equally difficult.


---

## 11. Related-work position, fixed at freeze

**Cleared.** The claim of this campaign — that silence-conditioning is a capability present
under high reasoning effort and not deployed under default inference — is unclaimed. The
absence-of-evidence neighbourhood has not moved since the 2026-08-07 deep pass beyond what
is already logged there (CROWN-QA arXiv 2608.04591; Eo26 ACL 2026; Li25c; Zho25).

**One concession, made here rather than at review.** The W1 wording result — that lexical
label choice moves the effective bin boundary by roughly 0.05 in probability, consistently
across seven configurations from four labs — is **not** a novel finding in its own right.
Dai (2026) established the general claim, that confidence scale design is not neutral and
that boundary placement is a first-class design variable, across six models with a proper
psychophysics metric. Our result is a new datum inside that frame, not a new frame: Dai
manipulates numeric scales where the boundary is stated, ours varies lexical labels where
the boundary is implicit and must be inferred from behaviour. It is reported as
confirmation and extension, never as discovery.

Related instruments to cite rather than be ambushed by: verbal-confidence saturation in
open-weight instruction-tuned models (arXiv 2604.22215), which is the exact failure mode W1
was built to rule out; protocol sensitivity in confidence calibration (arXiv 2605.27752),
which frames verbalized confidence as an elicited behaviour rather than a context-free
readout and is the correct framing for the verbalization-policy defence; and the
signal-detection treatment of LLM metacognition (Cacioli 2026, arXiv 2603.25112 and
companions).

**Terminology collision, footnote only.** "When to Think, When to Speak" (Wei et al., arXiv
2605.03314) uses *silence* and *disclosure policy* for a model's own output streaming, not
for inference from another agent's absence. Different object; name it so a reader does not
assume it was missed.

**Unread, flagged at freeze:** arXiv 2603.15500, "Understanding reasoning in LLMs through
strategic information allocation under uncertainty." Title-level proximity only; read
before the writeup, not before the run.
