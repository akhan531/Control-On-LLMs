# Example 1 — Disconfirming evidence is under-weighted when written, increasingly ignored when silent

**Task 2.4c · locked 2026-08-17 · anchor rebuilt 2026-08-17 (same session) · paper section: §4**
All results reproduce from frozen data already on disk; this example spent **zero new API calls**.

**Headline claim.** LLMs update toward disconfirming evidence too little and never too
much — across ~2,900 draws, zero overshoots where overshooting was expressible — the
shortfall deepens when the evidence is only implied by silence, and, wherever the
instrument can tell the two apart, the under-use tracks the *ignore-point* `b_pos`
rather than a global shrinkage toward the prior.

---

## 1. Hypothesis and anchor history

This section records what was fixed when, in order, because the example's framing
changed after its measurements were complete and that history is part of the record.

1. **The campaign predates everything.** Stimuli and design frozen 2026-08-15
   (`silence_v2_spec.md`, published hashes); data collected before this session.
2. **The statistics were fixed before any literature was consulted against them**
   (step 3, 2026-08-17): signed bin error `s2`, location classes, occupancy rates.
3. **A first anchor was selected at the literature step (2026-08-17): the
   negation-insensitivity literature** — Ettinger 2020 (arXiv 1907.13528), Kassner &
   Schütze 2020 (arXiv 1911.03343), Truong et al. 2023 (arXiv 2306.08189).
   **Rejected at writeup review, same session, for construct mismatch:** those papers
   claim a *parsing* failure of the logical operator "not" (cloze distributions
   unchanged under negation); our instrument measures a *weighting* failure over
   disconfirming evidence in belief revision. The two constructs share an English
   word and nothing else — and our own A4 result falsifies the literal operator claim
   for the gated five (the NEGATIVE lines demonstrably register). Equating them was
   equivocation, caught before writing.
4. **The current anchor — the belief-updating literature, under an arbitration
   framing — was adopted post-results.** Both anchors are post-data. The
   pre-registered object was always the campaign, never the anchor. What this example
   claims is therefore **construct validity of the instrument** — the coordinate
   system independently measures what the updating literature reports by other
   means — and never a predicted discovery.

## 2. Literature anchor: a disagreement to arbitrate, not a finding to recover

| source | method | claim |
|---|---|---|
| Edwards 1968, "Conservatism in human information processing" (with Phillips & Edwards 1966) | human probability-revision experiments | humans update in the correct direction but by too little; origin of the term "conservatism" |
| Imran et al. 2025, arXiv 2507.17951 (verified against the paper body 2026-08-17) | Bayesian Coherence Coefficient: correlation of expected updates (log-likelihood ratios) with observed updates (log-odds changes); credences read as cumulative token log-probabilities; separate model instances for prior/likelihood/posterior; five **pre-trained-only** families (Falcon 3, Llama 3, Qwen 2.5, GPT-2, Pythia), ≤14B; ~6,460 GPT-4o-generated tuples | "for all tested models, the gradient of observed vs. expected updates is less than 1" **in the main analysis** (appendix exceptions: GPT-2 Large/XL, Pythia 160M/1B); BCC rises with log-parameters (r = 0.906) |
| BayesBench, arXiv 2606.30850 (verified 2026-08-17) | multi-turn evidence accumulation, numeric elicitation; **instruction-tuned** Llama-3 / Qwen-2.5, 3B–70B | larger instruction-tuned models "frequently become too confident, pushing predictions toward 0 or 1 even when the Bayesian reference remains far from those extremes" |

**Citation discipline, binding.** "Epistemic conservatism" is never attributed to
Imran et al. — their word is "under-update," the construct's name belongs to the
Edwards lineage, and they themselves offer a partly deflationary dataset-level gloss
("the evidences used in our analysis being a lot less likely compared to the
classes"), which our citation must and does survive, since our claims rest on our own
measurements. No model count beyond "five families, ≤14B" is asserted. Footnote-only:
"Failing to Falsify" (arXiv 2604.02485) is confirmation bias in evidence-*seeking*
(which tests models propose), not evidence-*weighting* — adjacent construct, not an
anchor.

**The arbitration.** The literature disagrees about the direction of the error:
under-updating on pre-trained models read through token probabilities (Imran et al.),
over-confidence on instruction-tuned models in multi-turn accumulation (BayesBench) —
and neither instrument can express both directions on the same records. Ours can:
both directions are expressible on one closed-form ruler, the evidence channel is
decomposed (positives fix `b_pos`; the disconfirming results move `b_pos` to `b*`),
and the roster is instruction-tuned frontier models — the population both papers name
as open. What we find: **strictly one-sided under-use at δ=0** (0 overshoots in 176
expressible RULED draws; 1 in FULL, from a gate-excluded config), with the
over-updating regime located elsewhere — it appears specifically under enumeration
plus a stated noisy channel (Example 2's wrong-channel overshoot, 0→32.5%
below-correct). **Direction is regime-dependent, and we map the regimes.**

**Why cross-method.** Their channels: token-probability credences on pre-trained
models; multi-turn numeric trajectories on open instruct models. Ours: a single-shot
ordinal answer from frontier instruction-tuned models, elicited with no probability
vocabulary anywhere in the prompt, scored by position between two closed-form
posteriors. Imran et al. name instruction tuning/RLHF and non-token-probability
elicitation as open questions; this example supplies evidence toward both. We do not
measure BCC.

## 3. The instrument that generated the data

Data comes from the frozen v2 campaign (`silence_v2_spec.md`, frozen 2026-08-15;
results collected before this session).

**Scenario.** Two candidates, exactly one responsible, uniform prior. `N` analysts
each run one conditionally independent binary assay with
`P(POSITIVE | responsible) = p`, `P(POSITIVE | other) = 1 − p`.
An analyst files a report **only on POSITIVE**.

**Reference beliefs (exact rationals, `silence_v2_model.py`):**

| object | reads | form |
|---|---|---|
| `b_pos` | the k positives only — ignores the disconfirming results/absences | `∝ L(a)^k` |
| `b*` | everything | `∝ L^k (1−L)^(N−k)` |
| `q(δ)` | positives + absences under the stated rule | `∝ [(1−δ)L]^k [1−(1−δ)L]^(N−k)` |

At `δ = 0`, `q = b*` **exactly** (verified over rationals). This pivot is the design:
FULL and PARTIAL_RULED share one correct answer and differ only in whether the
disconfirming results are *displayed* or must be *derived from absence*.

**The three conditions**, identical underlying record:

- **FULL** — all `N` results printed, completeness asserted, no rule. Correct: `b*`.
- **PARTIAL_BLIND** — only the k positives; `N` and the rule withheld. Correct: `b_pos`.
- **PARTIAL_RULED** — the same k positives, plus `N` and the filing rule. Correct: `q(0) = b*`.

**Prompt shape** (RULED shown; FULL swaps the rule line for `COMPLETE RESULTS, ALL N
ASSAYS` with every line printed; BLIND omits `N` and the rule):

```
One of the following is responsible for the contamination event. Exactly one is.

    Candidate SIGMA
    Candidate THETA

Before any testing, each candidate is considered equally likely.

5 analysts were each assigned a different assay. Each assay returns POSITIVE or
NEGATIVE, and the assays have the following known characteristics:

    If SIGMA is responsible, an assay returns POSITIVE with probability 0.81.
    If THETA is responsible, an assay returns POSITIVE with probability 0.19.

Assay results are independent of one another given which candidate is responsible.

Each analyst files a report only when their assay returns POSITIVE.

REPORTS ON FILE
    Assay returned POSITIVE
    Assay returned POSITIVE

Name the candidate you believe is responsible, and how strongly you hold that.

Reply with only a JSON object with keys "candidate" and "confidence".
"candidate" must be exactly SIGMA or THETA.
"confidence" must be exactly Somewhat confident or Very confident.
```

Binding prompt rules (asserted at build time): no silence vocabulary anywhere; no
probability vocabulary in the instruction; no analyst identifiers; BLIND never states
`N` or the rule; FULL asserts completeness so failure there is arithmetic, not a
coverage inference.

**Response scale.** Four ordinal levels from two enum fields, mapped in the
mirror-invariant target frame; bands were *measured* in a pre-test (W1), never stated
to the model:

| level | answer | band over P(target) |
|---|---|---|
| 3 | Very confident / target | ≥ 0.80 |
| 2 | Somewhat confident / target | 0.55–0.70 |
| 1 | Somewhat confident / other | 0.40–0.45 |
| 0 | Very confident / other | ≤ 0.20 |

**Grid.** 14 cells: A1–A5 (span-3 backbone), B1–B3 (span-2 backbone), C1–C3 and D1–D3
(count controls: `b_pos` pinned while `k` and `N` vary — C at 0.982/level 3, D at
0.618/level 2). Every cell asserts `level(b_pos) ≠ level(b*)` at build time. Each cell
runs in both mirrors (which printed label carries `p`) — a pure relabelling, asserted.

**Roster.** Seven configurations: three families at default and high reasoning effort
(`sol-none/sol-high`, `deepseek/deepseek-high`, `glm/glm-high`) plus one older
`anchor` model. 84 stimuli × 5 draws × 7 configs = 2,940 calls, **2,894 usable**; all
46 failures are PARSE in the deepseek family (deepseek 34, deepseek-high 12).

**Data files:** `results_v2/v2_results_live.json` (main campaign),
`silence_v2_stimuli.json` (stimuli + sha256), `results_v2/v2_gates.json` (P4),
`results_v2/v2_results_live_banked.json` (RULED_D30, used by the prior-crossing
test), `results_sweep/sweep_results_live.json` + `sweep_stimuli.json` (RULEDCTRL,
used in verification B2b only).

## 4. Population discipline (frozen before any Example-1 statistic)

**Competence gate** (frozen 2026-08-17, before step 3): a configuration enters a
δ=0 RULED claim only if its mean `s1` on FULL, draw level over all 14 cells, is
**below 1.0 bin** — "can locate the correct answer to within one bin when the
information is displayed." Membership: **admits** sol-high 0.200, sol-none 0.421,
glm-high 0.457, deepseek-high 0.752, glm 0.764; **excludes** deepseek 1.609, anchor
1.800. The gap between 0.764 and 1.609 means small changes to the bar cannot move
membership. Excluded configs are still computed and shown, marked as context.

**P4 admission exclusions inherited** from the pre-registration: anchor loses B1, B3,
D1–D3; sol-none loses B1 (cells where the modal BLIND answer missed `level(b_pos)`).
Dropped before every statistic in this example.

## 5. Statistics (all built from framework quantities)

With `l_cor` = level of the correct belief (`b*` in FULL and RULED, `b_pos` in BLIND)
and `l_pos` = `level(b_pos)`:

- `s2 = l_obs − l_cor` — signed bin error. Positive = toward `b_pos`; negative = past `b*`.
- **Location class** of each answer on the `b*`↔`b_pos` segment:
  - `OVER` (past `b*`): over-weighs the disconfirming results relative to positives
  - `COR` (at `b*`): weighs both correctly
  - `INT` (strictly between): under-weighs the disconfirming results
  - `POS` (at `b_pos`): ignores them — reasons from positives only
  - `BEY` (beyond `b_pos`): ignores them *and* over-weighs positives
- **Occupancy** `π_cor = P(l_obs = l_cor)`, `π_pos = P(l_obs = l_pos)` — `π_pos` is
  time spent at the blind fixed point.
- **Expressibility ledger** (required context for any one-sidedness claim): `b* < b_pos`
  in every cell, and `l_cor = 0` in 11 of 14 cells — so `OVER` has expressible rungs
  only in D1–D3 (`l_cor = 1`), and `BEY` only where `l_pos = 2` (B and D cells). The
  pooled %OVER-vs-%INT contrast is **not** a fair symmetry test; the fair test lives in
  the D cells, where one bin of over-weighting and one bin of under-weighting are
  equally available.
- **Prior-crossing classification** (added at the 2026-08-17 rebuild; rule frozen
  before the test ran): in the target frame the total evidence points below the
  prior in every δ=0 cell, so a *symmetric* under-updater — one global gradient
  `g < 1` shrinking the whole update toward the prior — can never produce an answer
  above `P = 0.5`. Error mass at target-frame levels 2–3 (bands 0.55–0.70 and ≥0.80),
  including mass sitting exactly at `level(b_pos)`, is therefore
  **`b_pos`-tracking-consistent**: unreachable by prior-shrinkage.

## 6. Results

**Draw level, gated five, P4-inherited** (`s3_location_summary.py`):

| config | FULL s2 | FULL %COR/%INT/%POS | RULED s2 | RULED %COR/%INT/%POS |
|---|---|---|---|---|
| sol-high | +0.200 | 80 / 20 / 0 | +0.114 | 89 / 11 / 0 |
| sol-none | +0.431 | 57 / 43 / 0 | +0.762 | 30 / 65 / 4.6 |
| glm-high | +0.457 | 56 / 44 / 0.7 | +0.486 | 63 / 29 / 6.4 |
| deepseek-high | +0.752 | 45 / 42 / 12.4 | +1.007 | 40 / 28 / 30.6 |
| glm | +0.764 | 44 / 49 / 6.4 | +2.243 | 0 / 17 / 77.1 |

- Every gated FULL draw lies on the `b*`→`b_pos` segment: `OVER` occurred 1/176
  expressible draws (in gate-excluded deepseek), `BEY` 0/353.
- **D-cell two-sided tally** (the fair symmetry test; both directions one bin away):
  FULL **9–0** toward under-weighting (sign test p ≈ 0.004); RULED **47–0**. Same
  cells, same models, same opportunity — the direction never reverses.
- **Blind-point occupancy:** FULL modal cells at `b_pos`: **0 of 62** across the gated
  five. In RULED, `π_pos` rises for four of five and falls for none
  (0→4.6, 12.4→30.6, 6.4→77.1, 0.7→6.4; sol-high 0→0 at ceiling); glm flips 11 of its
  12 decided modal cells to the blind point.
- **C-sweep** (`b_pos` pinned at 0.982, disconfirming results added 4→5→7): all five
  gated configs track toward `b*` in FULL (modal 0–1) — the under-use is **graded and
  count-sensitive, not binary**. Roster occupancy gradient, descriptive: the legacy
  anchor model goes 2/3/3 with 60% of its C-FULL draws at the blind point — near-total
  occupancy even with the results printed — while deepseek splits into modal ties
  (41%) and every gated config tracks.

**Where the under-use anchors — the prior-crossing test** (`s5_prior_crossing.py`;
rule and kill condition frozen at the checkpoint before running; % = share of *error*
draws that sit above the prior, i.e., at positions unreachable by symmetric
shrinkage; denominators are error draws):

| config | FULL | PARTIAL_RULED | RULED_D30 | verdict under the frozen rule |
|---|---|---|---|---|
| sol-none | 0.0% (0/56) | 8.8% (8/91, 6 at `l_pos`) | 40.4% (19/47, all at `l_pos`) | eligible (27 RULED-arm draws) |
| sol-high | 0.0% (0/28) | 0.0% (0/16) | — (0 errors) | **excluded: instrument-limited, not a counterexample** |
| deepseek-high | 42.7% (32/75) | 62.5% (50/80) | 85.3% (29/34) | eligible (79) |
| glm | 28.2% (22/78) | **100% (140/140, 108 at `l_pos`)** | 100% (57/57) | eligible (197) |
| glm-high | 4.8% (3/62) | 32.7% (17/52) | 100% (5/5) | eligible (22) |

Kill condition (dies if fewer than two gated configs show above-prior or
exact-`b_pos` mass in the RULED arms): **survived, 4/5 eligible.** The by-group
breakdown confirms the FULL-arm crossings concentrate where the geometry is
discriminating (deepseek-high's 7 D-cell crossings; glm's RULED mass spread across
all groups). Context: both gate-excluded configs are overwhelmingly above-prior
(anchor 100% in both RULED arms).

## 7. Verification — every alternative explanation, its pre-fixed kill condition, and the outcome

Scripts: `s5_va_tests.py` (A1, A2, A4), `s5_vb_tests.py` (B1, B2, B4),
`s5_prior_crossing.py` (added at the rebuild). Kill conditions were fixed at a
checkpoint **before** each test ran.

| test | alternative it can kill | kill condition (pre-fixed) | outcome |
|---|---|---|---|
| A1 | symmetric confidence-hedging ("avoid Very confident") — predicts inward drift at *both* extremes | hedging stands if BLIND inward rate ≥ ½ × FULL up-rate | **dead**: BLIND 0–2.5% vs FULL 25–70%; worst ratio 0.040. Bonus: "avoid the low extreme" also dead — modal level-0 answers are routine (COR 44–80%) |
| A2 | directional lean toward the positives' candidate | lean stands if BLIND up-rate ≥ ½ × FULL up-rate on matched B∪D cells | **dead for all five**, but glm marginal (0.455) — glm has a real measured lean: 16.7% of BLIND B∪D draws land *above* `b_pos`. Reported as a secondary behaviour ("weak-evidence inflation"); quantitatively cannot produce glm's 70% two-bin FULL displacement |
| A3 | bin-geometry artifact (the balance check) | n/a — reshaped the wording | pooled contrast replaced by expressibility ledger + D-cell 9–0 sign test |
| A4 | "the disconfirming results don't register at all" | fails if modal = `level(b_pos)` in ≥2 of 3 C cells | **register confirmed 5/5** — the under-use is graded and count-sensitive, not binary (blind-point draw share 0–10%); the excluded pair fails it (anchor 60%, deepseek 41%), completing the roster occupancy gradient |
| B1 | generic difficulty drift in RULED (mass drifts upward, `b_pos` fills incidentally) | targeted stop dies if BEY ≥ ⅓ × POS on B∪D | **dead**: aggregate 90 at `b_pos` vs 11 past it (ratio 0.122). Lean baseline: every config's BEY rate ≤ its own measured BLIND lean → the escapes are baseline inflation, **not silence-specific** |
| B2a | "answers high in RULED" response bias | bias stands unless ≥⅔ of displaced D draws sit at exactly 2 (= `level(b_pos)`) | **dead**: deepseek-high 11–0, glm 28–2 (93%), glm-high 5–1 (83%) |
| B2b | same bias, tested at pinned prompt length | flat-3 vs tracking `level(b_pos)` (which varies 3,3,3,2,2 across RULEDCTRL) | **dead**: no gated config is flat-3; glm's modal row 3,2,2,2,2 matches `level(b_pos)` on both informative cells at constant ~1009-char length. (deepseek-high: 15 sweep failures, noted) |
| B4 | missingness artifact | any config whose `π_pos` inequality flips under worst-case failure reassignment is dropped | **holds 5/5**; only deepseek-high moves at all: 29.3% ≥ 14.3% worst-case |
| prior-crossing | symmetric global conservatism (one gradient `g < 1` toward the prior) as the full account of the displacement | frozen rule above; dies if < 2 gated configs show above-prior/exact-`b_pos` mass in the RULED arms | **survived, 4/5 eligible** (27 / 79 / 197 / 22 RULED-arm draws); sol-high excluded as instrument-limited; FULL-arm distinguishability limited to deepseek-high and glm (see §11 band-geometry limitation) |

## 8. Final claims

1. **The arbitration claim.** The updating literature disagrees about the direction
   of LLM miscalibration — under-updating on pre-trained models (Imran et al. 2025),
   over-confidence on instruction-tuned models (BayesBench) — and neither instrument
   expresses both directions on one record. On an instrument that does, with the
   evidence channel decomposed, instruction-tuned frontier models show **strictly
   one-sided under-use of disconfirming evidence at δ=0** (RULED: 0 overshoots in 176
   expressible draws; D cells 9–0 and 47–0; mean `s2` +0.20 to +0.76 in FULL), while
   the over-updating regime appears specifically under enumeration plus a stated
   noisy channel (Example 2). **Direction is regime-dependent, and the instrument
   maps the regimes.** Killed alternatives: hedging (A1), lean (A2), geometry (A3).
2. **The under-use is graded and count-sensitive, not binary.** No gated config
   ignores the printed disconfirming results: 0 of 62 modal FULL cells at `b_pos`,
   C-sweep tracked 5/5 (A4), blind-point draw share ≤ 12.4% in FULL.
3. **Silence converts under-weighting into ignoring** (the RULED-anchored claim).
   Blind-point occupancy never falls and rises in 4 of 5 when the disconfirming
   results must be derived (B4-robust); the same D cells go from 9–0 to **47–0**,
   flipping modal answers in 4 cells; and the stop is *specifically at* `b_pos` — not
   generic drift (B1), not answer-high bias (B2a/B2b, including at pinned prompt
   length).
4. **The under-use is `b_pos`-anchored, not prior-anchored** (the decomposition,
   RULED-anchored). Four of five gated configurations place error mass above the
   prior or exactly on the blind point in the RULED arms — positions no symmetric
   under-updater can occupy — with glm categorical (140/140 error draws above-prior,
   108 exactly at `level(b_pos)`). The positive increment lands; the disconfirming
   increment is under-weighted. sol-high has no such mass anywhere and is
   **instrument-limited for this claim, not a counterexample**; in FULL alone the
   question is undecidable for the sol family and glm-high (§11).

**Context exhibits (outside the gate, never claims):** the roster occupancy gradient
— the legacy anchor model sits at the blind point almost totally (FULL C-sweep 2/3/3,
60%; RULED 100% of error mass above-prior), deepseek splits into ties — and glm's
measured weak-evidence inflation (16.7% BLIND lean), reported alongside claim 1 and
used as the baseline that explained away the BEY escapes.

## 9. Relation to the updating literature

**What we take from each side:** from Imran et al., the under-update direction on
pre-trained models — recovered here, by an unrelated channel, on the instruction-tuned
frontier population their limitations section names as open; from BayesBench, the
over-confidence direction on instruction-tuned models — not contradicted but
*located*: on our records it appears only when absences are enumerated under a stated
noisy channel (Example 2), never at δ=0.

**What we add:** an instrument on which both directions are expressible on the same
record; the channel decomposition (positives vs disconfirming results) that neither
aggregate gradient nor multi-turn trajectory can express; and the prior-crossing
separation showing the under-use anchors on the partial-evidence posterior rather
than on the prior, where the two are distinguishable. We supply evidence toward
Imran et al.'s two open questions (instruction-tuned models; non-token-probability
elicitation); we do not measure BCC, and the population/task differences mean the
arbitration is regime-location, not refutation of either paper.

## 10. Why this validates the framework

- **Both error directions exist as locations before any data arrives** — `b*` and
  `b_pos` bracket the answer space in closed form — which is exactly what makes the
  arbitration possible: an instrument that can only express one direction cannot
  adjudicate a directional disagreement.
- **The reference beliefs are load-bearing.** Blind-point occupancy, the D-cell
  symmetric test, the lean baseline, the B2 discriminator, and the prior-crossing
  classification (prior, `b_pos`, and `b*` all pinned exactly) are definable only
  because the framework supplies the counterfactual observers in closed form. Remove
  the framework and the claims cannot be stated (§5.3).
- **The pivot did real work.** `q(0) = b*` certifies FULL and RULED share a correct
  answer, making written-vs-derived a controlled comparison rather than two tasks.
- §5 compliance: RULED-anchored with FULL control under a frozen, gapped gate (§5.1);
  population-level shapes — universal directions with a ceiling exception and an
  explicitly instrument-limited config, no single-model claims (§5.2); statistics
  from the framework (§5.3); verification attacked explanations with pre-fixed kill
  conditions (§5.4); no new cells (§5.5 moot); each claim is one sentence (§5.6).

## 11. Caveats and wording obligations (binding for the writeup)

- **Band-geometry limitation (instrument limitation, stated with claim 4):** for the
  sol family and glm-high in FULL, the ordinal bands cannot distinguish asymmetric
  from symmetric conservatism — everything at or above 0.80 is one answer, so a
  single global gradient of roughly 0.6–0.75 keeps BLIND answers inside the top band
  while dropping FULL answers to level-1 territory. The decomposition claim therefore
  rests on the RULED arms and on the two configs with above-prior FULL mass.
- **Arbitration caveat:** we do not measure BCC; pre-trained vs instruction-tuned and
  single-shot vs multi-turn differences mean we locate regimes, we do not refute
  either paper on its own terms.
- Claims are behavioural (**under-use**), never mechanistic ("didn't read") — the
  instrument cannot separate partial weighting from imperfect aggregation.
- Claim 1's one-sidedness is scoped to δ=0; at stated dropout, over-reading exists
  and is Example 2's subject (39/620 and 91/623 below-correct draws).
- Any one-sidedness statement ships with the expressibility ledger (§5).
- Draw-level sign counts carry within-cell correlation (5 seeds × 2 mirrors share a
  cell). The FULL 9–0 lives in dispersion around correct modal answers; the RULED
  47–0 additionally flips 4 modal cells.
- sol-high is at ceiling throughout: vacuous inequality in claim 3, instrument-limited
  in claim 4 — state as such, never as evidence against.
- glm's weak-evidence inflation (16.7% BLIND lean) is reported alongside claim 1.
- All 46 campaign failures are deepseek-family PARSE; failure counts accompany any
  deepseek/deepseek-high number; deepseek-high additionally lost 15 draws in the
  RULEDCTRL sweep (B2b).
- Excluded-config exhibits (anchor, deepseek) are context, never claims.
- The anchor history in §1 is part of the record; the negation trilogy is cited there
  as considered-and-rejected, nowhere else.

## 12. Reproduction

From the repo root, in order (read-only against frozen data; each prints its tables):

```
python3 scratch_2_4c/gate_and_recount.py            # frozen gate + expressibility recounts (shared, one level up)
python3 scratch_2_4c/example_1/s3_location_summary.py   # step-3 statistics: classes, occupancy, C/D sweeps
python3 scratch_2_4c/example_1/s5_va_tests.py       # verification A1, A2, A4
python3 scratch_2_4c/example_1/s5_vb_tests.py       # verification B1 (+lean baseline), B2a, B2b, B4
python3 scratch_2_4c/example_1/s5_prior_crossing.py # prior-shrinkage vs b_pos-tracking (frozen rule)
```

`s3_location_summary.py` was renamed from `s3_negation_summary.py` at the 2026-08-17
anchor rebuild; its statistics are unchanged. The D-cell two-sided tally appears in
the session log; its numbers are reproduced inside `s3` (class tables) and `s5_vb`
(B2a).
