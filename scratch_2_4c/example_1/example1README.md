# Example 1 — Disconfirming evidence is under-weighted when written, increasingly ignored when silent

**Task 2.4c · locked 2026-08-17 · anchor rebuilt 2026-08-17 (same session) · revised
2026-08-21 against checklist items 40 and 41 · paper section: §4**
All results reproduce from frozen data already on disk; this example spent **zero new API
calls**. Every statistic below re-ran on 2026-08-21 and reproduced; `v2_gates.json`,
`v2_banked_gates.json`, `w1_gates_live.json`, and `w1_lowside.json` all regenerate
byte-identically.

**Headline claim.** LLMs update toward disconfirming evidence too little and never too
much — **zero over-reads in 300 expressible draws, 150 attempted per arm across the gated
five** — the shortfall deepens when the evidence is only implied by silence, and, wherever
the instrument can tell the two apart, the under-use tracks the *ignore-point* `b_pos`
rather than a global shrinkage toward the prior.

**Denominator discipline.** Over-reading is expressible only in D1–D3, so ~2,900 is never the
denominator for a one-sidedness claim. The correct figures are **150 attempted, 150 usable,
per arm, gated five**, and the two arms are **not pooled** (§4).

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

## 2. Literature anchors: two directions to locate, not a disagreement to arbitrate

**Retired framing, 2026-08-21 (checklist item 34).** This section previously described the
two anchors as opposed and this example as arbitrating between them. That was wrong on the
merits, not merely risky: **BayesBench cites Imran et al. as complementary rather than
contradictory**, so the two were never opposed, and a paper built on arbitrating between them
would have been arguing with a disagreement that does not exist. The surviving and stronger
framing is **localization**: both directions of error are expressible on one closed-form
ruler, and we say where on the grid each one appears.

| source | method | claim |
|---|---|---|
| Edwards 1968, "Conservatism in human information processing" (with Phillips & Edwards 1966) | human probability-revision experiments | humans update in the correct direction but by too little; origin of the term "conservatism" |
| Imran et al. 2025, arXiv 2507.17951 (verified against the paper body 2026-08-17) | Bayesian Coherence Coefficient: correlation of expected updates (log-likelihood ratios) with observed updates (log-odds changes); credences read as cumulative token log-probabilities; separate model instances for prior/likelihood/posterior; five **pre-trained-only** families (Falcon 3, Llama 3, Qwen 2.5, GPT-2, Pythia), ≤14B; ~6,460 GPT-4o-generated tuples | "for all tested models, the gradient of observed vs. expected updates is less than 1" **in the main analysis** (appendix exceptions: GPT-2 Large/XL, Pythia 160M/1B); BCC rises with log-parameters (r = 0.906) |
| BayesBench, Samanta et al., arXiv 2606.30850v1, 29 Jun 2026 (**read in full 2026-08-21**) | multi-turn evidence accumulation, numeric elicitation; seven **instruction-tuned** Llama-3 / Qwen-2.5 models, 3B–70B | **Corrected 2026-08-21: the paper reports both directions, split by scale.** Smaller models stay near the middle; larger models push toward the extremes. MAE at θ=0.5 rises 8.3 (LLaMA-3B) → 36.7 (Qwen-32B) → 34.2 (LLaMA-70B). The earlier "over-confidence" one-line gloss in this file was wrong; `citation_ledger.md` §1.5 was already correct. Also relevant: BayesBench builds on the bookbag-and-poker-chip paradigm, so this design is a rule-conditioned variant of the classic conservatism paradigm |

**Citation discipline, binding.** "Epistemic conservatism" is never attributed to
Imran et al. — their word is "under-update," the construct's name belongs to the
Edwards lineage, and they themselves offer a partly deflationary dataset-level gloss
("the evidences used in our analysis being a lot less likely compared to the
classes"), which our citation must and does survive, since our claims rest on our own
measurements. No model count beyond "five families, ≤14B" is asserted. Footnote-only:
"Failing to Falsify" (arXiv 2604.02485) is confirmation bias in evidence-*seeking*
(which tests models propose), not evidence-*weighting* — adjacent construct, not an
anchor.

**The localization.** Both directions of error are expressible on one closed-form ruler, the
evidence channel is decomposed (positives fix `b_pos`; the disconfirming results move `b_pos`
to `b*`), and the roster is **seven open-weight configurations at two reasoning-effort
settings**, a peer roster to both anchors — BayesBench uses seven models across two families,
CROWN-QA three across three. **Never describe the roster as "frontier" (checklist item 80).**

What we find, with populations stated: **strictly one-sided under-use at δ=0**, zero
over-reads in **150 attempted PARTIAL_RULED draws and 150 attempted FULL draws** across the
gated five, in the only cells where over-reading is expressible. The over-direction appears
elsewhere on the same instrument with the same models — two over-reads in ARITH_D0, and the
wrong-channel result at δ=0.3 — which is what makes this a **localization** rather than an
absence, and what rules out "the roster is too small to produce it."

**Do not use the 176 denominator.** It is an all-seven, P4-inclusive pool. The same defect
one layer down produces **206** in `gate_and_recount.py`, whose `draw_errors()` takes no P4
argument and applies no gate: 150 gated + 26 deepseek + 30 anchor + 4 failures = 210 slots.
Both numbers are on the banned list in `claims_to_evidence.md` §7.

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
mirror-invariant target frame; bands were **measured on both sides** in pre-test W1 and its
low-side addendum, never stated to the model:

| level | answer | band over P(target) |
|---|---|---|
| 3 | Very confident / target | ≥ 0.80 |
| 2 | Somewhat confident / target | 0.55–0.70 |
| 1 | Somewhat confident / other | 0.40–0.45 |
| 0 | Very confident / other | ≤ 0.20 |

**How the bands were measured, restated 2026-08-21 (checklist item 40).** W1's switch-point
scan only covered `P(first) ≥ 0.5`, so it fixed the **high-side** edge and nothing else. The
low-side edge was initially a **mirror assumption**: the W4 grid rule excluded predicted
beliefs in `[0.15, 0.35]` by reflecting the measured high side. That mattered, because the
silence-aware posterior sits **below** 0.5 on every flip cell, which is where the entire
result lives. `w1_addendum_lowside.py` re-analysed the CAL sweep, which already contained
four sub-even points, and measured the low side directly. **The mirror assumption held:**
low-high asymmetry is **0.000 at the widest for six of seven configurations** on wording B,
the wording v2 runs, giving measured edges of 0.20 and 0.80 and a data-implied dead zone of
`[0.15, 0.45]` low and `[0.55, 0.85]` high.

**anchor is the sole exception, and it is the same configuration excluded everywhere
downstream.** It carries 0.1 asymmetry, it is the only configuration failing W1's
reachability gate (reaching **2 of 4** options on wording A), and the only one whose switch
point moves between wordings (0.6 → 0.8). It is also excluded by the δ=0 competence gate at
1.800 and stripped of D1–D3 by P4. Four independent instrument checks and one behavioural
gate select the same configuration. **Never write "all seven configurations agreed"** — it is
six of seven, and the exception is informative.

**Stated limitation on the invariance claim.** The CAL sweep samples at **0.10 resolution**,
so the nominal 0.25/0.75 cuts and the alternate 0.20/0.80 edges both fall inside the measured
interval. Invariance across the two is a **sampling-resolution fact, not a robustness
result**, and must be stated as such. No cell was placed where the distinction would matter.

**Provenance limitation (open, checklist gap G1.5).** `w1_analyze.py` states that it applies
a rule pre-committed in `w1_pretest_plan.md` §5, frozen before any call. **That file does not
exist on disk and has never appeared in git history.** The gates therefore rest on an
assertion inside the analyser for their temporal ordering, the same narrowing already taken
for the stimulus sha: content integrity is established, ordering is not. Do not use freeze
language the record cannot support.
**Grid.** 14 cells: A1–A5 (span-3 backbone), B1–B3 (span-2 backbone), C1–C3 and D1–D3
(count controls: `b_pos` pinned while `k` and `N` vary — C at 0.982/level 3, D at
0.618/level 2). Every cell asserts `level(b_pos) ≠ level(b*)` at build time. Each cell
runs in both mirrors (which printed label carries `p`) — a pure relabelling, asserted.

**Roster.** Seven open-weight configurations: three families at default and high reasoning
effort (`sol-none/sol-high`, `deepseek/deepseek-high`, `glm/glm-high`) plus one older
`anchor` model. 84 stimuli × 5 draws × 7 configs = 2,940 calls, **2,894 usable**. Model
identity, provider, and version for item 80 are carried per record in the `slug` field of the
frozen results.

**Failures, corrected 2026-08-21 (checklist item 41).** In *this campaign* all 46 failures
are PARSE in the deepseek family (deepseek 34, deepseek-high 12), spread across all 14 cells
and all three conditions at 18 BLIND / 18 RULED / 10 FULL, which is what non-differential
attrition looks like. **That sentence is true of the main campaign only and must not be
stated as a property of the work.** Across all six arms the distribution is deepseek 100,
deepseek-high 60, **glm-high 12**, and **zero for sol-none, sol-high, glm, and anchor** —
worth stating, since a reader assumes a four-of-seven zero is being hidden otherwise. There
are also **two failure modes, not one**: `TRUNCATED` does not occur in this campaign but is
the majority mode elsewhere (8 of 10 banked, 47 of 75 sweep), a `max_tokens` exhaustion
signature rather than a decoding pathology. Failed records carry `failure`, `detail`, `raw`,
and `note`, the last recording "off-menu; retry discarded per D16."

**Draw census across the whole project (item 41).** Five experimental arms total **7,051
usable of 7,210 attempted**: main 2,894/2,940, RULED_D30 620/630, ARITH_D30 623/630,
ARITH_D0 959/980, RULEDCTRL sweep 1,955/2,030. Every arm's config × stimulus × draw product
closes exactly against its record count, with no ragged arm and no file header disagreeing
with its own records. **W1's 659/672 sits outside that total**, on a different stimulus set
and at **3 draws per stimulus, not 5** — carve the pre-test out of any "five draws
throughout" sentence. **Never quote "~7,050" as a bare total.**

**Data files:** `results_v2/v2_results_live.json` (main campaign),
`silence_v2_stimuli.json` (stimuli + sha256), `results_v2/v2_gates.json` (P4),
`results_v2/v2_results_live_banked.json` (RULED_D30, used by the prior-crossing
test), `results_sweep/sweep_results_live.json` + `sweep_stimuli.json` (RULEDCTRL,
used in verification B2b only), `results_w1/w1_results_live.json` +
`results_w1/w1_lowside.json` (**the band pre-test and its low-side addendum, added to this
list 2026-08-21 — they were the empirical basis of the band table and were previously
uncited here**), and `results_v2/v2_dcell_split.json` (the D-cell level split).

**Naming trap for the repo README.** `scratch_fable/results_arith/` is **ARITH_D30**;
`scratch_2_4c/example_2/results_arith_d0/` is **ARITH_D0**. Different arms, similar names.

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

- Every gated FULL draw lies on the `b*`→`b_pos` segment. The single `OVER` draw in the
  record comes from **gate-excluded deepseek**; among the gated five it is **0 of 150
  attempted** in each arm. (The old "1/176" and "0/176" phrasings are banned: 176 is an
  all-seven pool.)
- **D-cell two-sided tally** (the fair symmetry test; both directions one bin away):
  FULL **9–0** toward under-weighting; RULED **47–0**. **150 attempted and 150 usable per
  arm, zero failures**, so the denominator is attempted draws. Same cells, same models, same
  opportunity — the direction never reverses.
- **Significance is computed at the pre-registered unit, not at draw level** (revised
  2026-08-21). The frozen spec makes the **cell** the replicate, pooling mirrors and draws to
  one modal level. Two-sided exact sign test over the 15 config-by-cell units: **RULED 8
  displaced under-weighting, 0 over, p = 0.008**; **FULL 5 and 0, p = 0.063**. The result arm
  survives at the registered grain; the control does not reach significance and does not need
  to. At config level both are 3 and 0, p = 0.25, which is a floor imposed by having five
  configurations rather than a finding. **The old draw-level `p ≈ 0.004` is retired** — it is
  `2 × 0.5^9`, computed at the wrong grain, treating 9 draws from 3 configurations as
  independent, and it collided with the paper's obligation to state that no independence
  assumption is used.
- **Where the displaced draws land** (`s4_dcell_split.py`, 2026-08-21). Of the 47 displaced
  RULED draws, **44 sit at level 2 = `level(b_pos)`, 3 at level 3, and 0 at level 0**; total
  endpoint mass is **3 of 150 attempted, 2.0%**. FULL is 9 at level 2 and 0 at level 3. In
  **all three configurations with displaced mass to test**, level 2 outnumbers level 3:
  deepseek-high 11 vs 0, glm 28 vs 2, glm-high 5 vs 1. The sol family produces no displaced
  mass in D cells, so the test is undefined there rather than failed. This is the same split
  B2a computed on 2026-08-17 under a different alternative's name, now independently
  reproduced.
- **Draw-level displacement rises with the number of silences**, pooled over the gated five:
  D1 12/50, D2 13/50, D3 22/50, against `N−k` = 3, 5, 6. The modal-cell table hides this. It
  is a draw-level instance of the count-against-weight coupling and is **not chased here** —
  the pooling means it could be glm-driven. Parked for the expanded version.
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
exact-`b_pos` mass in the RULED arms): **survived — all four configurations with error mass
to test** (R2). sol-high has 0 error draws, so the test is **undefined rather than failed**.
**Quote the δ=0 numerators from the PARTIAL_RULED column only** — 8/91, 50/80, 140/140,
17/52. The eligibility counts 27 / 79 / 197 / 22 in the rightmost column **pool δ=0 with
δ=0.3** and are on the banned list; the verdict survives on δ=0 alone. The by-group
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
| prior-crossing | symmetric global conservatism (one gradient `g < 1` toward the prior) as the full account of the displacement | frozen rule above; dies if < 2 gated configs show above-prior/exact-`b_pos` mass in the RULED arms | **survived — all four configurations with error mass to test**; sol-high undefined rather than failed; quote the δ=0 numerators, never the pooled eligibility counts; FULL-arm distinguishability limited to deepseek-high and glm (see §11 band-geometry limitation) |
| ordinal extremity | **added 2026-08-21.** BayesBench's triage result: models sharpen the extreme labels and collapse the middle two, pushing ambiguous cases outward on a four-level ordinal scale — structurally this one. None of A1, A2, B1, B2, B4, or prior-crossing rules it out | dies if the displaced D-cell draws sit at `level(b_pos)` rather than at the scale endpoint | **dead, and dead in the opposite direction from the one it predicts.** On this scale levels 1 and 2 *are* the middle two, so extremity predicts level-1 draws moving to level 0; observed, they move to level 2. 44 of 47 displaced RULED draws at `level(b_pos)`, 3 at the endpoint, 0 past `b*`; endpoint mass 3 of 150 attempted (2.0%). Level 2 outnumbers level 3 in all three configurations with displaced mass to test |

## 8. Final claims

1. **The localization claim** (rewritten 2026-08-21; the arbitration framing is retired,
   see §2). Both directions of error are expressible on one closed-form ruler, and the
   instrument says where each appears. Where absences are **not enumerated**, seven
   open-weight configurations show **strictly one-sided under-use at δ=0**: **0 over-reads in
   150 attempted draws per arm** across the gated five, in the only cells where over-reading
   is expressible; D cells 47–0 in RULED (cell-level sign test p = 0.008) and 9–0 in FULL
   (p = 0.063, control); mean `s2` +0.20 to +0.76 in FULL. The over-direction **is**
   recoverable on the same instrument with the same models once the channel set changes —
   two over-reads in ARITH_D0, and the wrong-channel result at δ=0.3 — which is what makes
   this a localization rather than an absence, and what answers "the roster is too small."
   Killed alternatives: hedging (A1), lean (A2), geometry (A3), **ordinal extremity**.
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

**What we take from each side** (rewritten 2026-08-21): from Imran et al., the under-update
direction on pre-trained models — recovered here, by an unrelated channel, on the
instruction-tuned population their limitations section names as open; from BayesBench, **both
directions split by scale**, with the extreme-pushing behaviour concentrated in larger
models. Neither is contradicted; both are *located*. On these records the over-direction
appears where absences are enumerated, never in the non-enumerated arms at δ=0.

**One obligation this creates.** Because the over-direction is a **large-model** behaviour in
BayesBench, the null here must be shown not to be a scale artifact. It is not: the direction
is recoverable on this instrument with these same models once the channel set changes
(ARITH_D0 over-reads, and the δ=0.3 wrong-channel result). State this wherever the null is
stated.

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
- **Localization caveat** (was "arbitration caveat"): we do not measure BCC; pre-trained vs
  instruction-tuned and single-shot vs multi-turn differences mean we locate regimes and do
  not refute either paper on its own terms. The anchors were **selected after the data
  existed** — the campaign was pre-registered, the literature engagement was not. State that
  plainly and unburied.
- Claims are behavioural (**under-use**), never mechanistic ("didn't read") — the
  instrument cannot separate partial weighting from imperfect aggregation.
- Claim 1's one-sidedness is scoped to δ=0; at stated dropout, over-reading exists
  and is Example 2's subject (39/620 and 91/623 below-correct draws).
- Any one-sidedness statement ships with the expressibility ledger (§5).
- **Within-cell correlation is handled, not merely noted** (revised 2026-08-21). Draws
  within a cell share seeds and mirrors, so draw-level sign counts are correlated. The frozen
  spec already fixes the remedy: the **cell is the unit of analysis**, and every sign test is
  computed at that grain. Draw tallies are reported as descriptive counts with attempted
  denominators and carry **no p-value**. The FULL 9–0 lives in dispersion around correct modal
  answers; the RULED 47–0 additionally flips 4 modal cells.
- **One-bin degeneracy is structural and is stated, not hedged.** With `m = 2`,
  `b_pos ≥ 0.5` always, so the blind belief occupies only 2 of the 4 bins and the
  falsification test is **always a one-bin discrimination**. In D cells specifically,
  `l_pos = 2` against `l_cor = 1` means `INT` is structurally empty and the entire 47–0 test
  lives on a one-bin span. `verify()` guards a zero ordinal-`s` denominator but not a one-bin
  one. The repair is the alphabet-size axis deliberately dropped at D5.
- sol-high is at ceiling throughout: vacuous inequality in claim 3, instrument-limited
  in claim 4 — state as such, never as evidence against.
- glm's weak-evidence inflation (16.7% BLIND lean) is reported alongside claim 1.
- **Failure counts accompany any deepseek/deepseek-high number**, and the failure sentence
  is scoped to this campaign: all 46 here are deepseek-family PARSE, but across the project
  glm-high contributes 12 and `TRUNCATED` is the majority mode outside this campaign (§3).
  deepseek-high additionally lost 15 draws in the RULEDCTRL sweep (B2b).
- **Sweep attrition is differential and must be stated where the sweep is used.** RULEDCTRL
  and FULLCTRL together run 3.7% attrition against this campaign's 1.6%, asymmetric by
  condition (30 FULL, 45 RULED), concentrated in six `FULLCTRL` cells F06–F11, which take 42
  of 75 failures. The **lean baseline is clear of it**: RULEDCTRL splits exactly 234 gated
  usable and 96 excluded usable, a different sweep and a different arm.
- **Number collision to disambiguate at first use.** The lean-baseline line reads "2 of 234
  gated against **16** of 96 excluded," where 16 counts BEY escapes. RULEDCTRL also has **16
  gated failures**. Two different 16s in the same neighbourhood.
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
python3 s4_dcell_split.py                           # D-cell level split; kills ordinal extremity
python3 s6_draw_census.py                           # per-arm draw census (item 41)
python3 w1_analyze.py                               # band pre-test gates
python3 w1_addendum_lowside.py                      # low-side band edge, measured not mirrored
```

**Path note.** The five scripts above the line live under `scratch_2_4c/` and hardcode an
absolute `ROOT`, so they run from anywhere on this machine and **fail on any other**. The four
below the line resolve paths relative to the repo root. Fixing the first five is checklist
item 63.

`s3_location_summary.py` was renamed from `s3_negation_summary.py` at the 2026-08-17
anchor rebuild; its statistics are unchanged. The D-cell two-sided tally appears in
the session log; its numbers are reproduced inside `s3` (class tables) and `s5_vb`
(B2a).
