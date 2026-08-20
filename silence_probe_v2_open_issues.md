# Silence Probe v2 — design decisions and remaining work

**Status:** W1 complete and passed. Design decisions closed through D25. Remaining work is the spec,
pre-registration, and the run.
**Created:** 2026-08-14 · **Last updated:** 2026-08-15 (D1–D26 logged; W1, W4, W2 executed; primary and banked runs complete)
**Supersedes:** nothing. `silence_probe_spec.md` (frozen 2026-08-14) stays frozen and its runs remain
valid as **pilot data**; v2 is a new instrument, not an amendment to it.
**Target:** EIML3 @ NeurIPS 2026, Paris. Submission deadline **29 August 2026**.

---

## What happens next, in order

1. ~~**Ceiling pre-test.**~~ **DONE 2026-08-14. Verdict GO.** See D23.
2. ~~**Build the grid.**~~ **DONE 2026-08-14.** See D25. Moved ahead of the spec because the spec and
   the pre-registration are both written against it.
3. **Write and freeze the v2 spec**, stimulus file, hash, provenance.
4. **Write and freeze the pre-registration** (D12), rewritten as five predictions.
5. **Run**, seven configurations, roughly 3,600 calls.
6. **Write.**

**W9 (fresh related-work pass) still gates the freeze and has not been run.**

---

## Decisions log

### D1 — Response format: two-level confidence, four bins, uniform quarters

The probe reports **which candidate** it believes responsible and a **two-level confidence**. For
`m = 2` this is a four-point ordinal scale, equivalently the unit interval cut at 0.25 / 0.50 / 0.75.
Direction is always forced; no neutral option.

| level | P(named candidate) | label |
|---|---|---|
| 0 | 0.00 – 0.25 | Strongly OTHER |
| 1 | 0.25 – 0.50 | Slightly OTHER |
| 2 | 0.50 – 0.75 | Slightly TARGET |
| 3 | 0.75 – 1.00 | Strongly TARGET |

Chosen over binary and over a three-level (six-bin) scale on pilot evidence:

| scheme | informative cells | sol-high | other five | gap | worst non-sol-high |
|---|---|---|---|---|---|
| binary, 2 bins | 5/8 | +1.00 | +0.15 | 0.85 | +0.29 |
| **two-level, 4 bins** | **6/8** | **+1.00** | **+0.11** | **0.89** | **+0.23** |
| three-level, 6 bins | 7/8 | +1.00 | +0.21 | 0.79 | +0.40 |

- **Binary is structurally unusable.** Across 5,500 swept cells, `argmax(b_pos)` is the
  highest-likelihood candidate in *every* one — algebra, not cell selection, since the partial record
  is `k` identical POSITIVE reports and `b_pos ∝ L(a)^k` with `p > r`. Under a binary response,
  "always name the top candidate" is observationally identical to silence-blindness. The confidence
  dimension repairs this: a fixed response cannot track the blind belief's *level*, which moves
  across cells (0.692 → 0.919).
- **Binary would have misreported the pilot's best result.** sol-high at k=6, δ=0 scored `s = 1.000`,
  exactly the silence-aware posterior, and binary records it as "no flip."

**Declared limitation:** four bins produce a cleaner null partly by resolving less. hy3-none's partial
movement is visible at six bins (+0.40) and falls inside a bin at four. The paper must state that the
instrument cannot distinguish "flat" from "moving less than one bin."

**Methodological note for the writeup:** bin granularity was selected on pilot data and fixed *before*
the v2 run. Selection and reporting use disjoint data.

### D2 — v2 is the headline instrument

The frozen numeric campaign becomes pilot data, reported as an instrument run, diagnosed, and
superseded. The explicit-instruction control becomes the *motivation* for the switch rather than a
side result.

### D3 — The cell is the unit of analysis

Draws collapse to a per-cell mean ordinal-s; inference runs across cells. With 31 of 32 pilot cells
returning identical answers on all ten seeds, treating draws as independent inflates `n` by counting
the same bit repeatedly. The effect comes from consistency *across* cells — a sign test over ~14 cells
reaches roughly p = 0.0005 with no distributional assumptions.

Draws are retained, re-purposed as the within-cell stability measurement (D19). Cell count is the
binding cost driver.

### D4 — Cell construction constraints

1. The cell **set** must span at least two blind-predicted levels, or a model answering
   `Strongly TARGET` everywhere is again indistinguishable from silence-blindness.
2. Cell counts at each blind level must be roughly **balanced**, or a fixed-response heuristic scores
   well by matching the modal level.
3. Cells must sit a **minimum distance from bin edges**. Excludes k=0, where `b_pos = 0.500` lands
   exactly on an edge.

**Structural limit to state in the paper:** with `m = 2`, `b_pos ≥ 0.5` always, so the blind belief
occupies only 2 of the 4 bins and the falsification test is always a one-bin discrimination.

**Note for grid construction:** Block 1's k values cannot simply be reused. At k=6 both beliefs land
in level 3 at both δ values, so those cells carry no information under four bins.

### D5 — `m = 2` only

The ALPHABET block and its candidate-set-size axis are dropped. Bins stay on the unit interval with
chance at 0.5; no `1/m` rescaling needed. Revisit after Block 1 is built and validated.

### D6 — PARTIAL-BLIND is the sole admission gate; FULL is a reported condition

Under D4, PARTIAL-BLIND becomes the load-bearing control: its correct answer spans blind levels 2 and
3, so it *is* the naive-heuristic test.

FULL is **not** a gate. Its correct answer requires integrating the printed negatives, which stays
arithmetic-flavoured even in bins; gating on it would exclude exactly the models that failed it in the
pilot, and readmitting those models was the motivation for going qualitative. Gating on the capability
v2 exists to factor out is circular.

FULL is retained as a reported condition. The referee objection that PARTIAL-RULED failures are just
general incompetence is answered twice: PARTIAL-BLIND passing shows models track the right belief when
there is nothing to infer, and the explicit-instruction control independently establishes the
arithmetic story.

### D7 — Run scale

- **14–16 informative cells**, balanced across blind levels 2 and 3.
- **Mirror crossed**, 2 stimuli per cell. Under D3 the halves are the *same cell* and average into one
  unit, with disagreement reported separately per D18.
- **5 draws per stimulus.**
- **Confidence-option order not crossed into the grid**; tested as a separate small robustness arm.

### D8 — `N*` is out of scope for this paper

Not warranted at workshop length.

### D9 — The statistic: ordinal-s anchored on the positives-only level

$$s = \frac{\ell_{\text{obs}} - \ell_{\text{pos}}}{\ell_{q} - \ell_{\text{pos}}}$$

`ℓ_obs` is the level the model answered (it reports a level directly, so no binning of its output is
needed), `ℓ_pos` the level of the positives-only belief `b_pos`, `ℓ_q` the level of the silence-aware
posterior `q^t`.

**The anchor is `ℓ_pos`, not the condition-dependent `ℓ_b`.** This restores v1's structure — one
denominator per cell, shared across all four arms — and avoids a degeneracy: in FULL there is no
silence to ignore, so `b^t = q^t = b*`, and anchoring on `ℓ_b` would make the denominator zero.
`ℓ_pos` is arm-invariant.

FULL is scored on the **δ=0** cell's denominator, since `q^t = b*` only there. Same rule as v1.

| arm | expected `s` if silence-aware | if silence-blind |
|---|---|---|
| FULL | 1 | 0 |
| PARTIAL-BLIND | 0 | 0 |
| PARTIAL-RULED δ=0 | 1 | 0 |
| PARTIAL-RULED δ>0 | 1 | 0 |

PARTIAL-BLIND is 0 under both hypotheses by construction, which is exactly why it works as an
admission gate rather than as a test of the claim.

### D10 — Overshoot: average for now, monitor

`s > 1` means the model moved *past* the silence-aware belief — it read the silence and
over-corrected. Reachable only where `ℓ_q` is not at the scale floor or ceiling.

Included in the mean for now, but the analysis reports the count of overshooting cells separately. If
prevalent, revisit: averaging 1.5 with 0.0 produces a middle value that nothing in the data occupies.

### D11 — Roster: six configurations

`sol-none`, `sol-high`, `deepseek`, `deepseek-high`, `glm`, `glm-high`. Two effort levels on three
labs, so the none/high contrast replicates across three independent model families.

`anchor` (Llama-3.3-70B) and `hy3-none` held in reserve. `hy3-high` stays dropped for the token-budget
reason.

### D12 — Pre-registration: five predictions

Replaces P1–P7. One admission gate (PARTIAL-BLIND tracks the blind level across both levels), one
primary prediction (`s ≈ 0` at δ=0 for default-mode configurations, `s ≈ 1` for high-effort), one
replication prediction across labs, one mirror-agreement check, one determinism prediction.

**Written after the ceiling pre-test**, so the format is confirmed before the claims are locked. Open
to further reduction if problems appear.

### D13 — No justification arm, no explicit abstention channel

**Justification cut.** The explicit-instruction control showed that touching the elicitation changes
behaviour — three of four models got worse. Noted as future work.

**Abstention cut** as a separate channel. It reintroduces the escape hatch that differentially
attracts weak models, and D1's inner bins already express near-indifference. The paper argues
`Slightly` is the abstention-adjacent signal, which also answers EIML3's interest in abstention.

### D14 — Schema: two separate `enum` fields

One field for the candidate, one for the confidence — not a single `enum` over the four combined
options. A combined enum bakes the ordinal structure into the option strings, inviting the model to
read them as a scale and anchor on the ends. Separate fields let the candidate choice happen first and
the confidence attach to it, and make D16's coding rule tractable by distinguishing a bad candidate
from a bad confidence.

### D15 — Confidence wording: `Slightly` / `Strongly`, A/B tested

Primary wording is `Slightly` / `Strongly`: the most nearly antonymic pair and the least loaded.
`Somewhat` / `Confident` mixes a hedge with a self-report about certainty, which are different things;
`Leaning` / `Clearly` reads as evidential rather than doxastic.

**Stability is tested against `Somewhat` / `Very confident`** on a subset, in the same calls as the
ceiling pre-test. The wording *is* the threshold, so this is not cosmetic.

### D16 — Off-menu coding rule

Any response that does not parse into a valid (candidate, confidence) pair is recorded as a failure
and **excluded from the cell mean, with the exclusion count reported per cell**. No inference is drawn
from partial responses: a valid candidate with missing confidence is not evidence for either level.

Under D3 this matters less than it would have, since cells with heavy exclusion are flagged rather
than quietly distorting an inflated `n`.

### D17 — Candidate print order is not crossed in

The mirror already moves the target between first and second print position as a side effect of
swapping which label carries `p`, so print-position bias is partially controlled. Crossing it fully
would quadruple stimuli to defend against a threat the mirror substantially covers. The partial
confound is noted in the limitations.

### D18 — Mirror threshold: mean `|Δs| < 0.25`, reported per condition

Under a quarter of the full blind-to-aware range. Looser than v1's 0.15 because the ordinal scale is
coarse enough that a single cell landing one bin apart already produces a sizable `Δs`. Reported per
condition rather than pooled, since the pilot showed the artifact concentrates in specific arms —
anchor's FULL mirror disagreement was 4.8 nats while sol-high's was exactly 0.000.

### D19 — Determinism metric: fraction of stimuli with unanimous draws

Per configuration, the fraction of stimuli whose five draws all agree. Needs no distributional
assumption and directly supports the finding that correct silence-reading is deterministic while
failure is incoherent. Reported paired with D18's mirror number, since together they are the coherence
story.

### D20 — Bin-edge sensitivity: reanalysis at 0.20 / 0.50 / 0.80

Primary edges 0.25 / 0.50 / 0.75 are pre-registered; the full result is additionally reported
recomputed at 0.20 / 0.50 / 0.80. Because the model reports a *level* rather than a probability,
alternative edges change only the predicted levels, not the responses — so this is a reanalysis of the
same data, not a rerun.

### D21 — The theory bridge: stated, not bridged

No discrete analogue of the drift identity will be attempted. The paper states plainly that the theory
predicts a direction and a mechanism (silence-blind trackers accumulate error growing with the number
of non-disclosures), that the experiment tests whether observers implement the conditioning at all,
and that the ordinal result licenses the qualitative claim but not the nats-valued magnitude. EIML3's
foundations theme suits a paper explicit about the gap between a formal object and its measurement.

### D22 — Wording B is primary, superseding D15

`Somewhat confident` / `Very confident`, not `Slightly` / `Strongly`. Ali's verdict 2026-08-14, on
two independent lines of W1 evidence:

- **B reproduces the nominal bins; A does not.** Under B, six of seven configurations returned the
  exact string `0.10:TS 0.20:TS 0.30:Ts 0.40:Ts 0.60:Ss 0.70:Ss 0.80:SS 0.90:SS` on the CAL sweep —
  the correct answer at all eight points under edges 0.25/0.50/0.75. Wording A switches near
  0.30/0.70, so its inner bins are narrower than the cut `ordinal-s` predicts with.
- **Anchor can only express a lower-half answer under B.** Under A it reached 2 of 4 options and
  failed G2. Since `q^t` sits below 0.5 on every flip cell, anchor under A literally cannot emit a
  correct PARTIAL-RULED answer.

D15's argument for A was that `Slightly`/`Strongly` is the most nearly antonymic and least loaded
pair. That reasoning was sound a priori and is simply outvoted by measurement. The A/B contrast is
retained in the writeup as an instrument finding: **verbalization wording moves the effective bin
edges by roughly 0.05 in probability, systematically and in the same direction across seven
configurations from four labs.**

Wording B is written symmetric (`Somewhat confident`, not bare `Somewhat`) so the contrast is wording
rather than grammatical form.

### D23 — W1 outcome: GO, and what it established beyond the format

**Verdict GO.** G1 passed 7/7 configurations on both wordings against a rule requiring 2/3
default-mode and 2/3 high-effort. The ceiling risk that could have killed the instrument is absent.

Three findings beyond the go/no-go:

- **Anchor passed G1 with 32/32 determinism and 8/8 mirror agreement.** In v1 that model failed FULL
  by 3.83 nats and was excluded from every silence claim. This is direct confirmation that the v1
  failure was arithmetic, not reasoning, and it vindicates D6's removal of FULL as a gate. Anchor is
  readmitted under wording B.
- **CAL is not redundant with G1.** `k=1` versus `k=6` differ in report count, so a model running
  "more lines → high confidence" passes G1 without tracking belief. CAL has no reports at all and the
  confidence still tracks the stated probability, which rules the heuristic out per configuration.
  This is why D25 embeds a count control in the main grid as well.
- **What the ordinal format actually buys is tolerance, not a new capability.** CAL shows
  verbalization is near-perfect, so the format does not help models compute. It lowers the resolution
  demanded: a three-bin move survives a belief error that a 0.35-nat numeric target does not. The
  paper must say this plainly — the redesign does not rescue a model whose belief is directionally
  wrong.

### D24 — Bin edges are the MEASURED bands, not the nominal cut

Grid construction uses the wording-B bands measured in W1, inside which all seven configurations
agree with the nominal level:

| level | safe band |
|---|---|
| 0 | ≤ 0.20 |
| 1 | 0.40 – 0.45 |
| 2 | 0.55 – 0.70 |
| 3 | ≥ 0.80 |

Every predicted belief in the grid — `b_pos` and `q^t` at both δ — sits inside a band, so no cell's
correct level depends on where a model's personal threshold falls. This supersedes D4.3's
"minimum distance from bin edges," which was stated against nominal edges that had not yet been
measured.

**One asymmetry, and it constrains the δ axis rather than the headline.** Anchor calls 0.30
`Very confident OTHER` where the other six say `Somewhat confident OTHER`, putting its lower edge near
0.35 rather than 0.25. Level-1 targets are therefore fragile and level-0 targets safe. Since `q^t` is
level 0 at δ=0 and often level 1 at δ=0.3, this bites δ>0 specifically.

**Also corrected: D4's claim that the falsification test is always a one-bin discrimination is
false.** Level-3 cells reach `q^t` at level 0 — a three-bin move from confident blame to confident
exculpation. Level-2 cells reach two bins at most. Discrimination difficulty therefore varies
systematically with blind level, which is W7's non-exchangeability item with numbers attached.

### D25 — Grid principle: span backbone plus count control

Ali's verdict 2026-08-14, over three alternatives (fixed `(p,N)` families; fixed `b_pos` trading `p`
against `k`; mixed-span stratified).

**Reasoning.** The fragile half of the headline is not the null. `q^t` always sits below `b_pos`, so
generic downward hedging pushes `s` *up*, and a default-mode null survives that pressure. The fragile
half is a high-effort configuration landing on `s ≈ 1`. On a span-1 cell that is one bin and reachable
by chance; on a span-3 cell it is three bins in the right direction on a record to which nothing was
added. Maximising span is therefore what makes the positive half of the dissociation unattributable
to noise.

**Backbone**: highest-span cells available at each blind level. Level 3 gives span 3; level 2 cannot
exceed span 2.

**Count control**: cells holding `b_pos` near-constant while `k` varies. A count-driven model must
then contradict itself across cells whose correct answer is identical — falsifiable rather than
argued. This closes the hole that the fixed-`(p,N)` alternative would have built into the main grid.

**Selected cells** (`m = 2`, uniform prior, `p/r` symmetric, `p = 0.60` excluded as reserved to W1):

| id | p | N | k | `b_pos` | L | `q(δ=0)` | L | `q(δ=.3)` | L | span |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | 0.83 | 5 | 1 | 0.830 | 3 | 0.009 | 0 | 0.200 | 0 | 3 |
| A2 | 0.71 | 9 | 2 | 0.857 | 3 | 0.011 | 0 | 0.193 | 0 | 3 |
| A3 | 0.70 | 12 | 3 | 0.927 | 3 | 0.006 | 0 | 0.198 | 0 | 3 |
| B1 | 0.66 | 7 | 1 | 0.660 | 2 | 0.035 | 0 | 0.194 | 0 | 2 |
| B2 | 0.58 | 14 | 2 | 0.656 | 2 | 0.038 | 0 | 0.194 | 0 | 2 |
| C1 | 0.88 | 5 | 1 | 0.880 | 3 | 0.003 | 0 | 0.185 | 0 | 3 |
| C2 | 0.73 | 9 | 2 | 0.880 | 3 | 0.007 | 0 | 0.175 | 0 | 3 |
| C3 | 0.66 | 13 | 3 | 0.880 | 3 | 0.010 | 0 | 0.184 | 0 | 3 |
| D1 | 0.68 | 7 | 1 | 0.680 | 2 | 0.023 | 0 | 0.168 | 0 | 2 |
| D2 | 0.59 | 13 | 2 | 0.674 | 2 | 0.036 | 0 | 0.196 | 0 | 2 |
| D3 | 0.57 | 11 | 3 | 0.700 | 2 | 0.196 | 0 | 0.410 | 1 | 2 |

C1–C3 are the level-3 count control (`b_pos = 0.880` at `k = 1, 2, 3`); D1–D3 the level-2 control
(0.680 / 0.674 / 0.700 at `k = 1, 2, 3`). 11 cells, 6 at level 3 and 5 at level 2.

**Balance is structural and short of D7's 14–16.** Level 2 occupies a 0.15-wide window against level
3's 0.20 plus every strong-likelihood configuration, so level-2 cells are genuinely scarce under the
dual-δ band requirement. Adding more means relaxing the band rule or dropping δ=0.3 informativeness;
neither is worth it. A sign test over 11 concordant cells still reaches p ≈ 0.001.

**Run size**: 11 cells × 2 mirrors × 4 conditions = 88 stimuli; 5 draws × 7 configurations = 3,080
calls.

### D26 — PARTIAL-RULED at δ > 0 is designed, generated, and NOT run in the primary campaign

Ali's verdict 2026-08-15. The primary campaign is δ = 0 only. The δ = 0.30 arm is fully
specified, generated to `silence_v2_stimuli_banked.json` (sha256 `23d2c4c6…`), and enabled by
`RUN_BANKED = True` plus `--banked`.

**The reason is not cost.** Under an ordinal statistic the δ > 0 arm is mechanically *easier*,
not harder, which is the opposite of what it was introduced to do. Dropout weakens the silence
signal, so `q(δ>0)` always sits between `b_pos` and `q(0)`; the ordinal denominator is
therefore always shorter there, and identical partial movement scores higher. In a cell with
`ℓ_pos = 3`, `ℓ_q(0) = 0`, `ℓ_q(0.3) = 2`, one bin of movement scores 0.33 at δ = 0 and 1.00 at
δ = 0.3. The v1 spec had already recorded the underlying fact — ε falls 0.4804 → 0.1192 when δ
rises, so δ > 0 is a *smaller inference over a noisier channel* — but the "higher bar"
intuition survived alongside it for two months.

The original motivation was insurance against a ceiling at δ = 0, where silence is logically
equivalent to a stated negative and substitution was expected to be easy. **The v1 data had
already falsified that premise**: `sol-none` scored 0.145 at δ = 0. There was no ceiling to
insure against.

**Costs, recorded rather than omitted.** The trimming-versus-censoring bridge to de Punder is
lost. And since `W̄ = D(b*‖q) = 0` identically at δ = 0, the primary campaign only ever tests
whether the full-information posterior can be recovered, never whether residual uncertainty is
correctly represented. Any claim about `W̄` requires the banked arm or new cells.

**Run afterwards as exploratory work, 2026-08-15**, 630 calls, on 9 viable cells. Not
pre-registered, and reported as exploratory. Its result is recorded in D27.

### D27 — the δ arm's finding: the intermediate epistemic state is empty

Exploratory, from the banked run.

Configurations either move with the stated dropout rate or do not. Of those that do not,
**every single one is anchored at `b_pos`** — deepseek 5/5 stuck cells, glm 4/4, anchor 8/9.
**Not one is anchored at `q(0)`.**

That state was the interesting hypothesis: a system that reads silence correctly but assumes a
perfect disclosure channel, i.e. that everyone who could report did. It is empirically empty
here. Systems either condition on the disclosure structure — in which case they also respond
to the dropout rate — or they ignore it entirely and sit at the positives-only belief.

Movement counts are near-monotone in δ = 0 performance: sol-high 9/9, glm-high 7/9,
deepseek-high 7/9, sol-none 7/9, glm 2/9, deepseek 2/9, anchor 0/9.

**Do not use mean `s` in this arm.** Every banked cell has a one-bin denominator, so overshoot
and undershoot cancel: `sol-none` returns a mean `s` of exactly 1.000 while getting 5 of 9
cells right. Use movement and per-cell accuracy. This is itself a reportable methodological
result — a normalised ordinal error statistic can report perfect performance for a system that
is merely unbiased around the target.

### D28 — constant-λ attenuation is falsified

Exploratory, 2026-08-15. Hypothesis: each model sits at a fixed fraction λ of the way from
`b_pos` to `q` in log-odds, with λ a model property.

**Killed by out-of-sample test.** λ fitted on the δ = 0 cells predicts the held-out δ = 0.30
arm *worse than assuming λ = 1*: glm-high 3/8 against 8/8, deepseek-high 4/8 against 7/8,
sol-none 3/9 against 5/9. Only `sol-high` is internally consistent (23/23). Two cells are
`IMPOSSIBLE` — no λ explains them, because the answer fell outside the range spanned by both
endpoints.

λ tracks how much updating the cell demands, not a property of the model. **The endpoints are
real and the interior is not a stable place.**

Standing rule from this: any successor hypothesis must be fitted on one subset and predict a
held-out subset, and must beat both the `b_pos` and `q` baselines out of sample, before it goes
near a paper.

---

## Remaining work

**W1 — Ceiling pre-test. DONE 2026-08-14, verdict GO.** See D23. Artifacts: `w1_stimuli.py`,
`w1_stimuli.json` (sha256 `e747d942…`), `w1_pretest_plan.md`, `w1_harness.py`, `w1_analyze.py`,
`test_w1_gates.py`, `w1_addendum_lowside.py`, `results_w1/`.

**W2 — v2 spec, stimulus file, hash, provenance. DONE 2026-08-15.** `silence_v2_spec.md`,
FROZEN. Primary stimuli sha256 `f9cd913c…`, banked `23d2c4c6…`.

**W3 — Pre-registration written and frozen. DONE 2026-08-15**, as §10 of the spec rather than
a separate document, so the spec could not be frozen ahead of its own predictions.

**W5 — Run. DONE 2026-08-15.** 2894/2940 usable primary, 620/630 banked. Primary predictions
P1 1/3, P2 1/3, P3 (primary) FAILED. See D27, D28.

**W9 — Related-work pass. DONE 2026-08-15.** No direct hit on the claim; one direct hit on the
secondary wording claim (Dai 2026). Recorded as §11 of the spec.

**W4 — Grid construction. DONE 2026-08-14.** See D25. `w4_grid.py`, `w4_grid.json`.

**W5 — The run.** Roughly 640 calls per configuration × 6 ≈ 3,800 calls.

**W6 — Degeneracy detectors.** With probabilities gone, clipping rate and per-draw spread no longer
exist. D19's unanimity fraction and D16's exclusion count partly replace them; whether anything
further is needed can be settled from W1's output.

**W7 — Cells are not exchangeable beyond the edge-distance rule (§2.4).** Whether to weight or
stratify by how far apart the two beliefs' levels are. Deferrable to analysis; note it now.

**W8 — Writing tasks carried from the switch.** The pilot-as-superseded-instrument section; the
verbalization-policy defence (`Strongly` does not denote the same probability across models — the
primary comparison is within model, across arms on identical records, so a stable per-model threshold
cancels); and what claim, if any, still connects v2 to the 960-debate campaign, which is in nats on a
model that fails every numeric competence gate.

**W9 — Fresh related-work pass before v2 freezes.** The standing watchlist was built for the numeric
framing; ordinal-confidence silence-conditioning is a different neighbourhood.

---

## EIML3 fit (from eiml.cc, fetched 2026-08-14)

**Venue is asking for this.** The CFP's "Evaluation and negative results" topic asks "Can we benchmark
ignorance, blind spots, and unknown unknowns?" and "Which existing approaches fail under carefully
designed stress tests?" It welcomes submissions that challenge prevailing assumptions or propose novel
benchmarks. Frame v2 as a benchmark contribution, not only an experiment.

**"Representations of ignorance"** asks which mathematical objects should represent epistemic
uncertainty and what their failure modes are. `b^t` versus `q^t` is a representation question with a
measured failure mode.

**Theme is foundations**, explicitly not a broad uncertainty workshop. Lead with the conceptual claim
about acting under ignorance of what was not said, not a model leaderboard.

**Abstention** is a listed topic — answered by D13's argument that `Slightly` is the
abstention-adjacent signal.

**Dates.** Deadline 29 Aug · notification 29 Sep · camera-ready 18 Oct · workshop 12 Dec, Paris. At
least one author per submission is asked to review; Ali should plan to volunteer.


---

## Protocol notes carried from W1

**A decision rule that cannot fail is not a decision rule.** W1's obedient stub passed every gate,
which established only that the plumbing worked. `test_w1_gates.py` runs seven adversarial responders
— ceiling, floor, binary-collapse, inverted, only-one-config-discriminates, lower-half-unreachable,
obedient — and confirms each routes to its intended verdict. It was that test, not the obedient stub,
that surfaced a harness bug in which stub and live runs shared a checkpoint: because resume keys on
successful draws, a stub run would have satisfied every key and made the live run a silent no-op
reporting full counts. v1's stub gate caught none of its three harness bugs for exactly this reason.
**Build the adversarial stub before the real run, not after.**

**Measure both halves of any scale before selecting against it.** W1's first analyser scanned only
`P ≥ 0.5` and measured the upper threshold alone. The lower threshold — where `q^t` lives on every
flip cell, and therefore where the entire result is scored — went unmeasured, and the grid was
briefly selected against a mirror assumption instead. The reanalysis cost one command and moved the
usable level-2 band from the assumed 0.55–0.65 to the measured 0.55–0.70.
