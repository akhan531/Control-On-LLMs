# Silence-conditioning in LLM observers — experiment spec and pre-registration

**Task:** Phase 2, Task 2.4
**Status:** **FROZEN 2026-08-14** on Ali's sign-off. Any departure from this document from this point
on is an amendment file per §13, not an edit. No stimulus is edited after the freeze hash.
**Drafted:** 2026-08-13. Supersedes the earlier 2026-08-13 draft that used a three-arm × two-δ framing.
**Frozen:** 2026-08-14. Signed off against the four-condition framing of §0 with no changes to the
design, the grid, the statistic, or the pre-registration. §10 (ARITHMETIC CONTROL) remains a proposed
amendment outside the frozen design, to be decided after Block 1.
**Model verified:** `silence_model.py` reproduces every value in §5 (all three blocks) and §2.1 to
printed precision, and passes the structural identities over 560 swept parameter combinations.
**Target:** Figures 2 and 3 of `eiml_paper_outline.md`. EIML deadline 2026-08-29.
**Relation to prior work:** new instrument. Not a revision of `meridian_v2`, but shares its anchor
model so results are continuous with the 960-debate campaign.

---

## 0. What this experiment tests

Whether an LLM observer reading a record with known omissions can condition on what is absent
from it.

Four conditions, one record family, all belief values computed in closed form from a likelihood
table stated in the prompt and **never estimated from probe behaviour**.

FULL and PARTIAL-BLIND are not endpoints of the measurement scale. They are two independent
competence checks, each of which can fail:

- **FULL** shows the probe can reach `b*` when every outcome is written down.
- **PARTIAL-BLIND** shows the probe stays at `b^t` and does not drift toward `q^t` when it has no
  basis to.

If either fails, the instrument is broken and no silence claim is available from this run.

The result lives in the two PARTIAL-RULED conditions, each read against its own computed `q^t`:

- At **δ = 0**, silence is logically equivalent to a stated NEGATIVE. Landing at `q^t` means the
  probe made a substitution; landing at `b^t` means it cannot.
- At **δ > 0**, silence carries partial information. Landing at `q^t` means the probe weighted an
  omitted mass; landing at `b^t` means it cannot.

**Comparison is always probe against computed value, never probe against probe.** Using FULL's or
PARTIAL-BLIND's outputs as the scale would make FULL unable to fail and the competence claim
circular. See §9.1 for the empirical-anchor sensitivity analysis, which is where that idea
legitimately lives.

**Records are constructed, not generated.** No debate is run. Each stimulus is authored and its
correct interpretation computed in closed form. The provenance of the record is irrelevant to what
is measured, and the paper says so explicitly rather than defending it if raised.

### 0.1 Why this belongs at EIML

Not that a model got a Bayesian arithmetic problem wrong. Multi-agent LLM systems are increasingly
deployed under content-dependent disclosure norms where agents report selectively, and an observer
that cannot condition on silence is not merely inaccurate but *systematically* so, in a direction
that grows with the number of non-disclosures. That makes this a property of the deliberation
protocol rather than a quirk of one model.

---

## 1. Scenario

One of `m` candidate causes is responsible for an event. Exactly one. Uniform prior.

`N` analysts each run one assay returning POSITIVE or NEGATIVE, conditionally independent given the
responsible cause, with

- `P(POSITIVE | target) = p`
- `P(POSITIVE | any non-target) = r`, where `p > r`

Both stated numerically in the prompt.

**Disclosure rule.** An analyst files a report only when its assay returns POSITIVE. Additionally,
with probability `δ`, an analyst fails to file regardless of result. `δ = 0` is the deterministic
case.

**Labels are non-name.** SIGMA, THETA, LAMBDA, OMEGA. No surnames, no persons. This designs out the
+0.595-nat surname prior measured in Task 2.1f, so no counterbalancing correction is load-bearing.

### 1.1 Records contain silence but no actual dropout

Every record contains `N − k` analysts absent from it. That absence is the entire measurement.

What is held fixed is that **none of those absences is a dropped positive**: the `k` filed reports
are exactly the `k` positives, and the `N − k` absentees are all genuine NEGATIVEs. The `δ > 0`
condition states a dropout rate in the rule while the underlying record has none.

*Why.* This makes the displayed record, `b_pos`, and `b*` byte-identical across the two δ levels, so
the **only** thing that varies along the δ axis is the stated rule, and therefore the only thing that
varies in the correct answer is `q^t`. Any other construction confounds the rule manipulation with a
change of stimulus.

*Why the scoring is still correct.* `q^t` is the right answer *given the stated rule and the observed
record*, which is the quantity under test. Further, the records are typical draws under the stated
rule: at δ = 0.3, `P(file | target) = 0.7 × 0.6 = 0.42`, so expected filings are 3.78 of 9, and the
grid's `k = 2, 4` sit squarely in the mass. A referee cannot say the record could not have come from
the stated process.

This construction is disclosed in the paper's protocol section.

---

## 2. The beliefs, in closed form

With `k` reports filed out of `N`, uniform prior `1/m`, likelihood `L(a) = P(POSITIVE | a)`:

```
b_pos(a)  ∝  (1/m) · L(a)^k                                     positives only
q^t(a)    ∝  (1/m) · [(1−δ)L(a)]^k · [1 − (1−δ)L(a)]^(N−k)      silence-aware
b*(a)     ∝  (1/m) · L(a)^k · [1 − L(a)]^(N−k)                  full information
```

`b^t` denotes the silence-blind tracker: the belief of an observer that updates on the content of
disclosed messages and ignores the informational content of non-disclosure.

**`b_pos` and `b^t` are different objects that sometimes coincide.** `b^t` is a tracker defined by the
theory. `b_pos` is a per-cell scale constant computed from `(k, p, r, m)`. In the three partial
conditions they are numerically equal. In FULL they are not: FULL has `b^t = q^t = b*`, and `b_pos`
there is the *counterfactual* belief of an observer that reads the positives and ignores the NEGATIVE
lines written next to them. Conflating the two is an error an earlier draft of this spec made; the
paper must keep them distinct in one explicit sentence.

All quantities computed as exact rationals, converted to float only at the log-odds boundary.
Log-odds throughout are target versus the aggregate of all non-targets.

### 2.1 V-decomposition, verified

`ε(t) = D(q^t ‖ b^t)`, `W̄(t) = D(b* ‖ q^t)`. At the `m=2, k=4, N=9` core cell:

| Condition | ε | W̄ | `D(b*‖b^t)` |
|---|---|---|---|
| FULL | 0.0000 | 0.0000 | 0.0000 |
| PARTIAL-BLIND | 0.4804 | 0.0000 | 0.4804 |
| PARTIAL-RULED δ=0 | 0.4804 | 0.0000 | 0.4804 |
| PARTIAL-RULED δ=0.3 | 0.1192 | 0.1103 | 0.4804 |

Four things to carry into the paper:

**PARTIAL-BLIND and PARTIAL-RULED δ=0 are identical in every V-quantity.** Same record, same true
disclosure process, so ε and W̄ *cannot* distinguish them. Any measured difference between those two
conditions is attributable to the rule statement and to nothing else — no theoretical quantity is
available to explain it away. This is the design's strongest control and must be stated outright, not
left for a referee to notice the rows match and wonder why.

**FULL's ε = 0 because the disclosure map is content-independent**, not merely because no silence
happens to occur. Content-independence is the theory's condition for ε = 0. This also matches the
prompt design: FULL carries no disclosure rule at all.

**ε falls when δ rises, 0.4804 → 0.1192.** Dropout makes silence a weaker signal. The δ > 0 condition
is not "same task, harder" — it is a *smaller* inference over a *noisier* channel. A failure at δ > 0
is therefore weaker evidence per unit than a failure at δ = 0, because less was there to find. This
is the quantitative form of why δ = 0 licenses the stronger sentence.

**At δ = 0 the decomposition is exactly Pythagorean:** `ε + W̄ = D(b*‖b^t) = 0.4804`, because `q^t` is
the information projection of `b*` onto what the record supports. At δ = 0.3 it does not sum
(0.2296 ≠ 0.4804), because `q^t` is computed under a stated δ exceeding actual dropout and so is not
the projection of the true `b*`. This follows directly from §1.1 and is defensible, but if the paper
reports the identity, the δ > 0 row visibly violates it and needs its footnote written in advance.

---

## 3. The four conditions

Not "three arms × two δ." δ enters only PARTIAL-RULED, and its purpose is to separate two distinct
capabilities: substituting for deterministic silence, and inferring over probabilistic silence.

| Condition | Record shown | `N` stated | Rule stated | Correct answer |
|---|---|---|---|---|
| FULL | all `N` outcomes | yes | no rule exists | `b*` |
| PARTIAL-BLIND | filed reports only | no | no | `b^t` |
| PARTIAL-RULED δ=0 | filed reports only | yes | yes | `q^t` = `b*` |
| PARTIAL-RULED δ>0 | filed reports only | yes | yes, incl. δ | `q^t` |

`PARTIAL-BLIND` returning `s ≈ 0` is **correct behaviour**, not failure, and the paper must say so in
the same breath as it reports it.

**What PARTIAL-BLIND uniquely buys.** Not competence evidence — its correct answer is arithmetically
a strict subset of what FULL already requires. What it establishes is the **zero-point**: that the
probe does not spuriously drift toward `q^t` with no basis. This matters because in this design `q^t`
is always *below* `b_pos` — silence always argues against the target whenever `p > r` — so any generic
downward hedge or calibration reluctance moves the probe toward `q^t` and registers as positive `s`.
**`s > 0` is therefore not by itself evidence of silence-reading.** PARTIAL-BLIND is what
disambiguates hedging from inference, and it is the single largest threat this instrument controls
for.

---

## 4. Prompt design

### 4.1 Binding rules

**R1. The words "silent", "silence", "absent", "missing", "did not report", and "no report" never
appear in any prompt.** If a prompt says *six analysts were silent*, the experiment has performed the
inference and is measuring multiplication.

**R2. `N` and the rule are stated; the count of non-filers is not.** Both recoverable in one
subtraction. Stating them separately is fair; stating their difference is leading.

**R3. The REPORTS block is byte-identical across all three partial conditions.** Filed reports carry
no analyst identifiers, because numbered identifiers with gaps (`Analyst 2, Analyst 5, …`) leak both
`N` and the fact of omission into PARTIAL-BLIND and destroy the baseline. The partial conditions
differ *only* in the framing lines above the record.

**R4. No argumentation anywhere in the record.** Evidentiary statements only. Task 2.3 established
that a public-record observer tracks rhetoric on a byte-identical evidence block (`τ ≈ 1.4–3` rounds,
`R²` to 0.996). If the stimulus contained argument, a failure here would be confounded with
rhetoric-tracking. The rhetoric finding is carried separately from existing data.

**R5. The task is framed as reading a record, never as computing a posterior.** The likelihood table
is stated as background about the assays. The words "posterior", "Bayes", "update", and "likelihood
ratio" do not appear.

**R6. The dropout clause must exclude the unreliability reading.** "An analyst fails to file with
probability 0.30" can land as *30% of filed reports are wrong*, which changes the correct answer
entirely. Pinned wording: **"does not file a report at all, even when the assay returned POSITIVE."**

**R7. FULL states `N` and asserts completeness; FULL states no rule.** A rule saying *analysts file
only on POSITIVE* alongside a record displaying NEGATIVE results is self-contradictory, and a probe
noticing that is unmodellable behaviour in the baseline. Without an explicit completeness assertion,
`b*` is not licensed as the correct answer. Consistency with PARTIAL-BLIND on `N` is not achievable
and is not chased: `N` in FULL is countable off the record regardless, while in PARTIAL-BLIND it is
genuinely unknowable. The asymmetry is forced by the design, not chosen.

**Prompt length does not confound.** RULED exceeds BLIND by the rule lines, but FULL exceeds both by
`N − k` record lines. Length is not monotone in condition, so it cannot carry the effect. One sentence
in the paper, not a control.

### 4.2 Information content per condition

**Shared by all four, byte-identical:**
- The `m` candidate options, non-name labels
- Uniform prior statement
- `P(POSITIVE | each option)` — the full likelihood table
- Conditional independence of assays given the responsible cause
- The elicitation instruction

**FULL** adds:
- `N`, stated
- An explicit completeness assertion: these are all `N` results
- Record: `N` lines, each POSITIVE or NEGATIVE, `k` of them POSITIVE

  *Excluded:* any disclosure rule, any mention that non-filing is possible, δ

**PARTIAL-BLIND** adds:
- Record: `k` lines, all POSITIVE, no analyst identifiers

  *Excluded:* `N`, the rule, δ, any mention that non-disclosure is possible, any completeness
  assertion

**PARTIAL-RULED, δ = 0** adds:
- `N`, stated
- The rule: an analyst files a report only when the assay returns POSITIVE
- Record: same `k` lines, byte-identical to PARTIAL-BLIND

  *Excluded:* δ

**PARTIAL-RULED, δ > 0** adds:
- `N`, stated
- The rule: an analyst files a report only when the assay returns POSITIVE
- The dropout clause per R6
- Record: same `k` lines, byte-identical to PARTIAL-BLIND

### 4.3 Templates

Common preamble, all conditions (`m = 2` shown; extend the candidate list for `m = 3, 4`):

```
One of the following is responsible for the contamination event. Exactly one is.

    Candidate SIGMA
    Candidate THETA

Before any testing, each candidate is considered equally likely.

Analysts were each assigned a different assay. Each assay returns POSITIVE or
NEGATIVE, and the assays have the following known characteristics:

    If SIGMA is responsible, an assay returns POSITIVE with probability 0.60.
    If THETA is responsible, an assay returns POSITIVE with probability 0.40.

Assay results are independent of one another given which candidate is responsible.
```

**FULL** replaces the first line of that block with `Nine analysts were each assigned a different
assay.` and appends:

```
ALL NINE ASSAY RESULTS
    POSITIVE
    POSITIVE
    NEGATIVE
    ...            (N lines, k POSITIVE)
```

**PARTIAL-BLIND** appends the shared record block only:

```
REPORTS ON FILE
    Assay returned POSITIVE
    ...            (k lines)
```

**PARTIAL-RULED** inserts, above that same byte-identical block:

```
Nine analysts were each assigned a different assay.
Standing protocol: an analyst files a report only when the assay returns POSITIVE.
```

and for δ > 0 additionally:

```
Separately, an analyst does not file a report at all with probability 0.30, even
when the assay returned POSITIVE.
```

**Elicitation, identical in every condition:**

```
Give your probability that each candidate is responsible. Reply with only a JSON
object with keys SIGMA and THETA, each a probability to three decimal places,
summing to 1.
```

The explicit key-naming instruction is **required**, not stylistic. See §7.2.

---

## 5. The grid

`N` is not a studied axis. It is the lever that sets the `s` denominator; the group-size result
belongs to the EC paper.

### Block 1 — CORE. `m = 2`, `p/r = 0.60/0.40`, `N = 9`

| `k` | δ | `b_pos` | `q^t` | `b*` | denom | P(tgt) `b_pos` | P(tgt) `q^t` | flip |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0.000 | −3.649 | −3.649 | 3.649 | 0.500 | 0.025 | |
| 0 | 0.3 | 0.000 | −1.946 | −3.649 | 1.946 | 0.500 | 0.125 | |
| 2 | 0 | +0.811 | −2.027 | −2.027 | 2.838 | 0.692 | 0.116 | **yes** |
| 2 | 0.3 | +0.811 | −0.703 | −2.027 | 1.514 | 0.692 | 0.331 | **yes** |
| 4 | 0 | +1.622 | −0.405 | −0.405 | 2.027 | 0.835 | 0.400 | **yes** |
| 4 | 0.3 | +1.622 | +0.541 | −0.405 | 1.081 | 0.835 | 0.632 | |
| 6 | 0 | +2.433 | +1.216 | +1.216 | 1.216 | 0.919 | 0.771 | |
| 6 | 0.3 | +2.433 | +1.784 | +1.216 | 0.649 | 0.919 | 0.856 | |

`k = 0` is the empty-record extreme and Figure 3's right anchor.

`k = 8` excluded: it puts `b_pos` at 3.24 nats, inside the saturation ceiling identified in Task 2.1f,
contaminating the PARTIAL-BLIND baseline rather than the quantity of interest.

Per `k` per mirror there are **4 distinct stimuli** — FULL, PARTIAL-BLIND, RULED δ=0, RULED δ=0.3 —
because FULL and PARTIAL-BLIND are shared across δ.

**4 `k` × 2 mirrors × 4 conditions = 32 conditions.**

### Block 2 — ALPHABET. `m ∈ {3,4}`, `p/r = 0.60/0.40`, `N = 9`, `k ∈ {2,6}`

| `m` | `k` | δ | `b_pos` | `q^t` | denom | flip |
|---|---|---|---|---|---|---|
| 3 | 2 | 0 | +0.118 | −2.720 | 2.838 | **yes** |
| 3 | 2 | 0.3 | +0.118 | −1.396 | 1.514 | **yes** |
| 3 | 6 | 0 | +1.740 | +0.523 | 1.216 | |
| 3 | 6 | 0.3 | +1.740 | +1.091 | 0.649 | |
| 4 | 2 | 0 | −0.288 | −3.126 | 2.838 | |
| 4 | 2 | 0.3 | −0.288 | −1.801 | 1.514 | |
| 4 | 6 | 0 | +1.334 | +0.118 | 1.216 | |
| 4 | 6 | 0.3 | +1.334 | +0.686 | 0.649 | |

Robustness, not difficulty. With target-versus-rest likelihoods the non-target causes are symmetric,
so `m` changes magnitudes but does not make the inference structurally harder. **The paper must not
imply otherwise.** Mirror = rotating which label is the target.

**2 `m` × 2 `k` × 2 rotations × 4 conditions = 32 conditions.**

### Block 3 — STRENGTH. `m = 2`, `p/r = 0.70/0.30`, `N = 5`, `k ∈ {1,3}`

| `k` | δ | `b_pos` | `q^t` | denom | flip |
|---|---|---|---|---|---|
| 1 | 0 | +0.847 | −2.542 | 3.389 | **yes** |
| 1 | 0.3 | +0.847 | −0.903 | 1.750 | **yes** |
| 3 | 0 | +2.542 | +0.847 | 1.695 | |
| 3 | 0.3 | +2.542 | +1.667 | 0.875 | |

`N` cut to 5 so endpoints stay expressible under stronger likelihoods.

**2 `k` × 2 mirrors × 4 conditions = 16 conditions.**

### Totals

**80 distinct stimuli**, identical across every model run, pre-generated and frozen to a `sha256`
before any call.

| Run | conditions | draws | calls |
|---|---|---|---|
| 5 open-weight runs | 80 | 10 | 4,000 |
| `tencent/hy3` reasoning-high pair | 80 | 10 | 800 |
| `openai/gpt-5.6-sol` reasoning-none, Block 1 | 32 | 10 | 320 |
| `openai/gpt-5.6-sol` reasoning-high pair, Block 1 | 32 | 10 | 320 |
| **Total** | | | **5,440** |

Estimated cost under $10 at listed prices. **Budget is not a constraint and nothing in this design
should be trimmed for it.**

Denominator coverage: δ = 0 spans 1.216–3.649 nats, δ = 0.3 spans 0.649–1.946. The overlap over
1.2–1.9 is what allows both to be plotted on one axis without the δ comparison being confounded with
denominator magnitude.

**Cut order if the freeze binds:** Block 3 first, then Block 2. Block 1 alone is the paper. Do not cut
FULL or PARTIAL-BLIND.

---

## 6. Statistic

**Silence-reading coefficient**, one formula, all four conditions:

```
s = (probe_logodds − b_pos_logodds) / (q^t_logodds − b_pos_logodds)
```

`s = 0` is exactly the positives-only belief. `s = 1` is the silence-aware posterior. Both endpoints
are **computed, never estimated**, which fixes the scale and makes `s` comparable across conditions,
models, `m`, and denominator size. One denominator for every condition, so no zero-denominator case
arises anywhere. The smallest denominator in the grid is 0.649 nats.

**FULL uses the δ = 0 `q^t` as its denominator.** There is no FULL at δ > 0, so no ambiguity arises.
At δ = 0, `q^t = b*`, so FULL's target and the RULED δ=0 target are the same number and the two
conditions sit on an identical ruler.

Expected values:

| Condition | Expected `s` | Reading |
|---|---|---|
| FULL | 1 | competence: uses the written-down negatives |
| PARTIAL-BLIND | 0 | correct: no basis to move |
| PARTIAL-RULED δ=0 | 1 = substitutes, 0 = cannot | the substitution test |
| PARTIAL-RULED δ>0 | 1 = weights omitted mass, 0 = cannot | the inference test |

**Secondary statistic.** `Δs = s(PARTIAL-RULED δ=0) − s(PARTIAL-BLIND)`: same record, same model, rule
statement the only difference, and identical in every V-quantity per §2.1. A null here is the single
hardest result to explain away.

**Mandatory companion, absolute error in nats** against each condition's own correct answer. `s` only
measures projection onto the `b_pos → q^t` line; a probe answering 0.5 everywhere would land near
`s = 0` by accident and look like a clean failure. The nats figure catches off-line garbage that `s`
cannot see. Both reported for every cell.

**Estimator, pre-committed.** Ten draws per condition, **seeds 1–10**, fresh context each call,
temperature 0.7 where the model accepts it and omitted where it does not (§7). Convert each draw to
log-odds, **then average the log-odds** — not the log-odds of the averaged probability. Task 2.1f's
first three calibration rounds used the wrong order and were rewrite passes against noise. Standard
error reported on every `s`.

**Degenerate responses.** Probabilities clipped to [0.001, 0.999] before log-odds conversion. Clipped
fraction reported per model per cell, never floored silently.

**Malformed responses.** With the schema of §7.2 these should not occur. Any that do are recorded as
failures and the rate reported per model. **No silent retry loop.** A model needing three attempts to
emit a number is not producing draws comparable to one that emits cleanly, and averaging over that
difference is exactly what a referee finds.

---

## 7. Models

Roster verified live against OpenRouter on 2026-08-13, including a successful call to every entry.

| Role | Slug | Reasoning | seed | temp |
|---|---|---|---|---|
| Anchor | `meta-llama/llama-3.3-70b-instruct` | none (no reasoning machinery) | yes | yes |
| Size axis | `meta-llama/llama-3.1-8b-instruct` | none (no reasoning machinery) | yes | yes |
| DeepSeek | `deepseek/deepseek-v4-flash-0731` | `{"enabled": false}` | yes | yes |
| Z.ai | `z-ai/glm-5.2` | `{"enabled": false}` | yes | yes |
| Tencent | `tencent/hy3` | `{"effort": "none"}` | yes | yes |
| Matched pair | `tencent/hy3` | `{"effort": "high"}` | yes | yes |
| Frontier | `openai/gpt-5.6-sol` | `{"effort": "none"}` | yes | **no** |
| Frontier pair | `openai/gpt-5.6-sol` | `{"effort": "high"}` | yes | **no** |

Canonical slugs recorded at freeze: `deepseek/deepseek-v4-flash-20260731`, `z-ai/glm-5.2-20260616`,
`tencent/hy3-20260706`, `openai/gpt-5.6-sol-20260709`.

### 7.1 Reasoning mode is a controlled axis, not a caveat

Most of the current open-weight frontier has `reasoning.mandatory: true` — Qwen3.8 2.4T A95B defaults
to xhigh effort, and Muse Glimmer, Grok 4.6, and the Gemini Flash line are all mandatory. Five current
families with reasoning off is not assemblable from arbitrary picks, and extended chain-of-thought is
exactly the capability most likely to catch a silence deduction. The roster is therefore selected for
controllability.

`{"enabled": false}` was **verified to work** on DeepSeek V4 Flash and GLM 5.2: both returned
`reasoning_tokens: 0` on a live call.

**Two matched pairs**, `tencent/hy3` and `openai/gpt-5.6-sol`, each run twice with reasoning as the
only difference, at opposite ends of the capability range. This converts "we could not control for
CoT" into a measured axis for 640 calls.

`anthropic/claude-opus-5` was considered and rejected for the frontier slot: it exposes no `none`
effort and no `seed`, so it could neither match the open-weight roster's reasoning setting nor support
reproducible draws. GPT-5.6 Sol offers both. Losing temperature control on Sol costs nothing, since
draws are varied by seed.

### 7.2 Elicitation format, and an instrument finding

Output shapes differ sharply across models under a bare instruction: bare JSON, ```json fencing,
pretty-printing, `SIGMA` versus `Candidate SIGMA` keys, and Llama-3.1-8B ignoring the format
instruction outright and opening with prose. A regex parser would produce **model-correlated failure
rates**, contaminating the competence checks.

All eight runs support `structured_outputs`, so the schema is forced via `response_format`
`json_schema` with `strict: true` and `additionalProperties: false`. Five of six models then return
byte-clean, identically parseable output.

**Finding worth reporting: grammar constraints alone are insufficient for smaller models.** Under
strict schema with no in-prompt format instruction, Llama-3.1-8B emitted an opening brace and then
whitespace to the token cap — grammar-constrained decoding degenerating, because the model attempts a
prose opening, is blocked by the sampler, and stalls in the only permitted tokens. Adding an explicit
instruction naming the keys fixed it completely. **Both the schema and the in-prompt instruction are
therefore required**, and §4.3's elicitation text is not stylistic.

**Schema construction.** For `m = 3, 4` the property list is generated per stimulus; under `strict`
with `additionalProperties: false` the key set is exactly the candidate labels. The mirror check
therefore requires the schema regenerated per label assignment, not merely the prompt text. A schema
built once and reused silently breaks those cells.

---

## 8. Pre-registration

Frozen before any model call. Committed as `PROVENANCE.json` alongside the frozen stimulus file and
its hash.

| # | Prediction | Scored against |
|---|---|---|
| P1 | FULL: `s > 0.75` and absolute error below 0.35 nats, every open-weight run | per-run mean, Block 1 |
| P2 | PARTIAL-BLIND: absolute `s` below 0.15, indistinguishable from 0 | per-run mean, Block 1 |
| P3 | PARTIAL-RULED δ=0: `s < 0.25`, and significantly below 1 (one-sided *t*) | per-run mean, Block 1 |
| P4 | PARTIAL-RULED δ=0.3: `s < 0.25`, and significantly below 1 | per-run mean, Block 1 |
| P5 | `Δs < 0.20` | per-run, Block 1 |
| P6 | `s` flat in denominator magnitude: regression slope within ±0.10 per nat | per-run, Block 1 |
| P7 | Mirror halves agree in `s` within 0.15 | pooled |

**P1 and P2 are instrument-validity gates.** If either fails for a given run, that run yields no
silence claim and is reported as an instrument failure rather than a result.

**No prediction registered for the frontier model.** That cell is genuinely open; registering a guess
would be dishonest.

**No prediction registered for whether δ = 0 and δ = 0.3 differ.** The *reading* of each outcome is
pre-committed in §9 instead.

**No prediction registered for the reasoning-mode pairs.**

Thresholds in P1–P7 are stipulated, not derived, and recorded as such.

---

## 9. Pre-committed interpretation

Fixed before the data exists so the verdict is not made under deadline pressure.

| | FULL passes, PARTIAL-RULED fails | Both pass |
|---|---|---|
| **δ = 0** | Models cannot perform the one-step deduction. Silence is *logically* equivalent to a stated negative and they still miss it. Headline stands. | Models can substitute. δ = 0 becomes a positive control and the paper's weight moves entirely to δ > 0. |
| **δ > 0** | Models cannot do Bayesian inference on an omitted mass. Broader claim, weaker per instance, since less information is present to find (§2.1). | Models can weight absence probabilistically. |

Joint pattern governs:

- **Fail both** — strongest version. *LLM observers do not treat absence as evidence, at any
  difficulty.* Headline unchanged from `eiml_paper_outline.md`.
- **Pass δ = 0, fail δ > 0** — a sharper and better paper. Locates a capability boundary: models can
  substitute a deduced value but cannot carry an omitted mass. This is exactly de Punder's
  trimming-versus-censoring distinction, measured in an LLM. Headline becomes *LLM observers negate
  but do not censor.*
- **Fail δ = 0, pass δ > 0** — incoherent; δ = 0 is strictly easier. Treat as an instrument bug, not a
  finding, and debug before reporting anything.
- **Pass both** — no paper on this axis, and it would contradict Task 2.1f's exact `+0.000`. First
  suspect is that the abstract register made the task too easy; diagnostic is to re-run the δ = 0 core
  cells in a narrative register and see whether the failure returns.

### 9.1 Empirical-anchor sensitivity analysis (secondary, explicitly labelled)

The concern motivating it is legitimate: if the probe is systematically shaded, raw theoretical `s`
misreads it. It is handled as a **diagnostic, not a scale**.

FULL error against `b*` and PARTIAL-BLIND error against `b^t` are already measured. If both show bias
in the same direction and similar magnitude, report it and additionally compute a rescaled `s` using
the observed FULL and PARTIAL-BLIND means as endpoints, labelled as a sensitivity analysis. **The
primary result stays theoretical.**

Why it cannot be primary: it makes FULL unable to fail, so the competence claim becomes circular; the
two anchors come from different stimuli (`N` lines versus `k` lines), so it would divide out
calibration bias *plus* an uncontrolled stimulus difference with no way to separate them; and it
converts an exact denominator into a difference of two ten-draw estimates, a ratio estimator whose
relative error runs roughly 15% at the widest cells and approaches 50% at the narrowest.

If the diagnostics come back clean, the objection is answered by data and this becomes a footnote.

---

## 10. Proposed amendment — ARITHMETIC CONTROL

**Status: proposed, not part of the frozen design. Decide after Block 1 results.**

FULL establishes competence at the `b*` arithmetic. Nothing in the current design establishes
competence at the `q^t` arithmetic under δ > 0, which is strictly harder — a mixture over dropout
rather than a product of likelihoods. A referee can therefore say: *your δ > 0 failure is not
silence-blindness, the models simply cannot compute that posterior at all.* There is currently no
answer.

**The condition.** State the record's omissions explicitly and hand over the mixture, e.g. *five
analysts filed nothing; under the stated rule each is negative with probability 0.806 and
positive-but-unfiled with probability 0.194*. Correct answer is `q^t` by direct computation. It
deliberately violates R1 and R2 — that is the point; it is not a silence test.

**What it buys.** The δ > 0 analog of FULL: competence at the target arithmetic, established
separately from willingness to derive the inputs. If ARITHMETIC CONTROL passes and PARTIAL-RULED δ > 0
fails, the failure is located precisely at *noticing the omission*, not at computing with it.

**Cost.** 8 cells × 2 mirrors × 10 draws ≈ 160 calls per run.

**Decision rule.** Add it if PARTIAL-RULED δ > 0 fails in Block 1. If δ > 0 passes, it is unnecessary.

---

## 11. Build order

1. Freeze this spec and `PROVENANCE.json`. **No model call before this step completes.**
2. `silence_model.py` — closed-form `b_pos`, `b^t`, `q^t`, `b*`, `ε`, `W̄` for arbitrary
   `m, p, r, N, k, δ`, exact rationals internally. Verification suite asserting the §2.1 identities
   and reproducing every value in §5 exactly.
3. `silence_stimuli.py` — generates all 80 stimuli plus their per-stimulus JSON schemas, emits
   `silence_stimuli.json` and a `sha256`. Frozen at this point.
4. `silence_harness.py` — runs the grid via `requests`, not `urllib`: the macOS Anaconda build has no
   CA bundle wired in and `urllib` fails TLS verification. **Dry-run against a stubbed
   model-obedient responder first and confirm it recovers `s = 1.000` exactly in every cell**, so any
   gap in a real run is provably the model and not the plumbing.
5. Launch Block 1 first. Inspect P1 and P2 before running Blocks 2 and 3.
6. `silence_analyze.py`, `silence_figures.py` — Figures 2 and 3, flip cells reported separately,
   mirror check reported, P1–P7 scored one by one.

---

## 12. Analysis and figures

**Figure 2 — the dissociation.** One row per model run, four points per row on a single 0-to-1 `s`
axis: FULL, PARTIAL-BLIND, PARTIAL-RULED δ=0, PARTIAL-RULED δ=0.3. Reference lines at `s = 1`
(*correct silence inference*) and `s = 0` (*positives only*). Error bars from the ten draws.
Competence and failure adjacent on the same ruler with the same arithmetic underneath.

**Figure 3 — the gap grows, the observer does not move.** `x` = denominator magnitude in nats,
`y` = `s`. One line per model run, error bars per point, δ = 0 and δ = 0.3 as separate series.
Empty-record cell as the right anchor.

**Reported separately, not averaged in:** the seven flip cells where `b_pos` and `q^t` fall on opposite
sides of even. Strongest single demonstration in the run.

**Reported as a validation, not a correction:** mirror-half agreement. Unlike the surname effect in
Task 2.1f, label-order bias here is directly checkable, so it is a check rather than something the
headline leans on.

**Appendix panel, optional.** Llama-3.3-70B, Llama-3.1-8B, DeepSeek V4 Flash, and GLM 5.2 all expose
`logprobs` and `top_logprobs`. A single-token elicitation read off the logits would sidestep the
~3-nat expressibility ceiling and round-number granularity entirely, and on the flip cells would
settle whether `s ≈ 0` is inability to infer or inability to express. Not the primary channel — it is
unavailable on Hy3 and Sol, and switching mid-campaign breaks continuity with 2.1f — but worth one
panel.

---

## 13. Deviation policy

Any departure from this spec after freeze is recorded in a dated amendment file with its reason and
what it changes, in the manner of `meridian_v2_amendment_1.md`. Task 2.1f's clue-text calibration
exceeded its own allowance five times over, and the honest record of that is what kept the result
credible. The same standard applies here.

No stimulus is edited after the freeze hash. If a stimulus is wrong, that is an amendment with its own
provenance entry, not a quiet fix.

**Already recorded, pre-freeze:** the Llama-3.1-8B grammar-stall finding and its fix (§7.2), and the
rejection of `anthropic/claude-opus-5` for the frontier slot (§7.1).
