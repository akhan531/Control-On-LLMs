# Example 2 — Silence's meaning, not its detection, is the bottleneck

**Task 2.4c · locked 2026-08-17 · claim prose corrected 2026-08-20 · paper section: §5 (worked example 2)**
Three of the four data quadrants were frozen before this session; the fourth
(ARITH_D0, 980 calls) was **pre-registered and then collected this session** with
Ali's explicit approval at each step.

**Headline claim** *(rewritten 2026-08-20 — the original asserted that blind-point
occupancy "collapses for every configuration that had any," a universal that counted
the gate-excluded pair inside the number and omitted glm-high, which moves the other
way; all counts below are scored on the gated five).* Models can be told exactly
where the silences are, and it helps only as far as *identification* was the problem —
and how much of a configuration's deficit is identification rather than
interpretation is a **per-model quantity the instrument measures, not a constant**.
At δ=0, enumeration reduces error for every gated configuration with a silence
deficit to close (three of three under the registered 0.15-bin ceiling guard: paired
Δs1 sol-none −0.092, deepseek-high −0.299, glm −0.493), and the share of the
implicit-to-printed gap it closes varies by model: sol-none 28%, glm 33%,
deepseek-high ≈100% — the one gated configuration it carries all the way to its
fully-printed profile. It is not a cure: glm still sits at the blind point in 50% of
its draws (9 of its 12 decided modal cells) with every absence printed. And when
silence means "negative **or** dropout" (δ=0.3), enumeration repairs no one — it
pushes the formerly-stuck models past the answer onto the wrong effective channel
instead.

---

## 1. Hypothesis and design

Reasoning from a silent record decomposes into **identifying** the absences (which
analysts never filed?) and **interpreting** them (what is each non-filing worth?).
The four quadrants cross enumeration with the nature of interpretation:

| | interpretation = deterministic substitution (δ=0) | interpretation = probabilistic computation (δ=0.3) |
|---|---|---|
| **absences implicit** | PARTIAL_RULED (frozen) | RULED_D30 (frozen) |
| **absences enumerated** | **ARITH_D0 (new)** | ARITH_D30 (frozen, prior session) |

At δ=0 a non-filing logically *is* a negative, so a third rung exists: **FULL**
(negatives printed as results — nothing left to identify or substitute), and the
pivot `q(0) = b*` certifies that PARTIAL_RULED, ARITH_D0, and FULL share one correct
answer per cell. That ladder closes **only** at δ=0: at δ>0, printing true results
would change the correct answer (a non-filer is either a negative or a dropout, and
nobody can know which) — the spec's "unclosable hole," which is exactly why the
ARITH arms exist.

## 2. Literature anchor

**CROWN-QA** (arXiv 2608.04591, abstract verified 2026-08-17): LLMs mishandle absence
in coverage-sensitive QA, and — the finding this example engages — "prompting
redistributes errors between over- and under-closure rather than consistently
resolving them." Honest positioning: this is *adjacent support*, not the cross-method
recovery Example 1 has. Their method is behavioural QA over document coverage; ours
is location between closed-form posteriors. What we add to their claim: a controlled
setting where both presentations provably share one correct answer, a **positive
control** their setting lacks (the δ=0 panel shows enumeration *is* read and used —
so the δ=0.3 null indicts interpretation, not attention), and quantification (bins
of repair; the implied channel δ̂). The arithmetic-control concept originates in this
project's own v1 spec §10; ARITH_D30 was built the previous session.

## 3. The data

**Frozen quadrants** (see `../example_1/example1README.md` §3 for the shared
instrument — scenario, roster, response scale, measured bands, mirrors, prompt rules):

- PARTIAL_RULED and FULL, δ=0: `results_v2/v2_results_live.json`, 14 cells.
- RULED_D30: `results_v2/v2_results_live_banked.json`, the 9 banked-viable cells
  (A1–A5, B1, C1–C3), 620/630 usable.
- ARITH_D30: `scratch_fable/results_arith/arith_results_live.json`, same 9 cells,
  623/630 usable. Record block prints one `    Filed nothing at all` line per silent
  analyst under `COMPLETE FILING RECORD, ALL N ANALYSTS`, with the dropout clause
  byte-identical to RULED_D30's.

**New quadrant — ARITH_D0** (this session):

- `arith_d0_stimuli.py` builds the frozen PARTIAL_RULED prompt with **only the record
  block replaced** — byte-identical prefix through the filing rule, byte-identical
  elicitation, record wording byte-identical to ARITH_D30's, no dropout clause
  (asserted absent). Record length is N lines, matching FULL's; RULED stays the short
  arm, so length artifacts run *against* the null prediction.
- Build-time assertions: field-by-field identity of the expected answer with frozen
  PARTIAL_RULED (enumeration changes nothing normative); `q(0) = b*` recomputed over
  rationals; `level(b_pos) ≠ level(b*)` per cell (§5.5); line counts; mirror
  relabelling; distinctness from both frozen neighbours. R1 deliberately violated
  (enumerated non-filings are silence vocabulary in function), recorded, as ARITH_D30.
- Frozen: `arith_d0_stimuli.json`, sha256
  `028d9be8f4809ecbdebf645a520ffaf4344e386d4fe9e75a809aea4dc60751d0`, 28 stimuli.
- **Pre-registration** (`arith_d0_prereg.md`), written before any call: statistics,
  ceiling guard, and both competing predictions (P-null: enumeration doesn't help;
  P-identify: it repairs to the FULL floor) with no directional bet.
- Run: `arith_d0_harness.py` (byte-parallel copy of the ARITH_D30 harness — same
  roster, budgets, preflight, 401 fail-fast, resume, TRUNCATED-retry, PARSE terminal
  per D16), 980 calls, **959/980 usable**. All 4 TRUNCATED recovered at 1.5× tokens;
  the 21 remaining failures are terminal PARSE, all deepseek-family — including a
  notable spike: deepseek fails to parse 20/140 on the enumerated record vs 7/140 on
  FULL (missingness informative; flagged wherever deepseek appears).

## 4. Population discipline

- **δ=0 claims** gate on the frozen FULL gate (mean s1 < 1.0, draw level): population
  {sol-none, sol-high, deepseek-high, glm, glm-high}; deepseek, anchor as context.
  The gap (0.764 → 1.609) makes membership insensitive to the bar.
- **δ=0.3 claims** gate on the frozen ARITH gate: all seven admitted — with the
  recorded caveat that this gate has **no gap** (deepseek enters at 0.988 against the
  1.0 bar; membership is bar-sensitive there).
- P4 admission exclusions inherited throughout (anchor: B1, B3, D1–D3; sol-none: B1).
- sol-high and glm-high are at ceiling (near-perfect in every rung) and carry only
  weak-inequality content.

## 5. Statistics (all framework-derived)

- Paired per-cell `s1`/`s2` differences between arms — pairing on identical cells
  cancels span differences by construction; no normalised s anywhere.
- Location classes and occupancies: at δ=0 the Example-1 ruler (OVER/COR/INT/POS/BEY);
  at δ=0.3 the **three-point ruler** `l_q0 = level(q(0))` < `l_cor = level(q(0.3))` <
  `l_pos = level(b_pos)`, with the below-correct side split at `l_q0`.
  Expressibility ledger: in 8 of 9 banked cells correct and blind are adjacent (no
  interior rung) and the over-reading side has two rungs; BEY exists only in B1.
- **λ localization index** = (s1_ARITH − s1_FULL)/(s1_RULED − s1_FULL) at δ=0, with a
  0.15-bin ceiling guard. Registered before collection. **Descriptive only**: it came
  back heterogeneous (deepseek-high −0.14, glm 0.67, sol-none 0.72) and λ-value
  claims were retired by Ali's ruling; λ's meaning survives as "the interpretation
  share of each config's deficit."
- **Implied channel δ̂** (defined at the verification stage, approved before
  computing): `q(δ)` rises monotonically from `b*` (δ=0) to `b_pos` (δ→1), so each
  observed level inverts, per cell, to the interval of δ that would make it correct —
  *the dropout rate the model behaves as if it believes*. Categories: over-price
  (δ̂ < 0.3; subcase certainty-consistent if the interval contains 0), correct
  (contains 0.30), under-price (δ̂ > 0.3), off-trajectory.

## 6. Results

**Panel 1 — δ=0 (interpretation is deterministic substitution).** *(corrected
2026-08-20 — claim counts rescored to the gated five; gate-excluded configurations
moved to context clauses; the earlier "collapse … 5/5 among configs that had any"
universal was wrong: it counted the excluded pair inside the five and omitted
glm-high, which moves the other way.)* Enumeration reduces error for all three gated
configurations with a silence deficit — paired Δs1 (ARITH−RULED): sol-none −0.092,
deepseek-high −0.299, glm −0.493 (context, gate-excluded: deepseek −0.428, anchor
−0.589). Blind-point occupancy falls for **three of the four gated configurations
that had any** — sol-none 4.6→0.0%, deepseek-high 30.6→12.9%, glm 77.1→50.0% — and
**rises for glm-high, 6.4→10.7% (9→15 of 140 draws)**, consistent with its mild
ARITH degradation recorded in §11. Context: the gate-excluded pair also falls
(deepseek 64.1→48.3, anchor 100→70.0 — anchor's RULED_D30 baseline being **80 of 80
draws at the blind point**, the purest `b_pos` lock measured anywhere in the
project). The repair is per-model, not uniform: deepseek-high closes ≈100% of its
implicit-to-printed gap (λ = −0.14, at its FULL floor), sol-none 28% and glm 33%
(λ 0.72, 0.67) — and **glm remains at the blind point in 50% of draws and 9 of its
12 decided modal cells with every absence printed: identification is not repaired
for it**. Interior (under-weighting) mass rises in all five gated configurations —
the freed answers land short of correct as often as on it. sol-none's deficit was
always mostly interior (65% INT vs 4.6% POS), and its gain is cell-concentrated to
match: 28% of its gap on the full grid, 0% on the 9 matched cells of V-E2-4c (its
gain-carrying cells sit outside that set). No overshoot unlock: **2 of 150
expressible gated draws** — both in ARITH_D0, one deepseek-high and one glm; RULED
and FULL show zero *(denominator corrected 2026-08-20: previously stated as 210,
which is the all-seven slot count — an error dating to the 2026-08-17 original that
also survived the 2026-08-20 audit)*.

**Panel 2 — δ=0.3 (interpretation is probabilistic).** The same handout repairs no
one: no configuration recovers more than 12.5% of its deficit (worst-case missingness
bound ≤ 0.20 bins). Instead the stuck configs shoot past the answer: below-correct
mass anchor 0→32.5%, deepseek 7.0→23.8%, glm 0→5.6%, while signed error collapses
through redistribution, not accuracy (anchor s2 +1.000→+0.175 at s1 1.000→0.875).

**The δ̂ readout.** Median implied dropout in the δ=0.3 arms: sol-none, sol-high,
deepseek-high, glm-high sit at **0.29–0.34** — essentially the stated 0.30, the
instrument watching models *use the number printed in the prompt* — while glm,
deepseek, anchor sit at **0.70–0.74**, discounting silence at more than twice the
stated rate. Enumeration moves the movers to *different wrong channels*: the deepseek
family toward certainty (δ̂ ≈ 0), sol-none/anchor to partial discounts.

**Cross-regime.** As registered and run (V-E2-4c, §7): on the 9 shared cells,
fraction-of-own-deficit recovered, 4 of the 5 pre-fixed non-ceiling configurations
gain strictly more at δ=0 than at δ=0.3, with sol-none reversed (0.0% vs 8.0%) — the
pre-registered 5/5 universal died at its kill bar. *(Added 2026-08-20.)* The
**claim-grade sentence is scored on the gated population only**, because two of the
four as-registered passers are gate-excluded and this record does not let excluded
configurations carry claims: **two of three gated non-ceiling configurations gain
strictly more at δ=0 than at δ=0.3 (deepseek-high +29.2% vs −7.9%; glm +15.7% vs
−15.5%), with sol-none reversed (0.0% vs 8.0%) and explained by having no
identification deficit on the matched cells**; the gate-excluded pair agrees in
direction as context (deepseek +21.0% vs −30.7%; anchor +15.0% vs +12.5%), and the
ceiling pair is uninformative.

## 7. Verification — pre-fixed kill conditions and outcomes

| test | alternative it could kill | kill condition (pre-fixed) | outcome |
|---|---|---|---|
| V-E2-1 mimicry cross-tab | δ=0 repair is record-*shape* (any N-line record processed like FULL, lines counted not read) — a pure line-counter must also over-read toward `q(0)` at δ=0.3 | stands iff repair ≥ 0.70 AND δ=0.3 below-mass ≥ 15% AND ≥ half of it at `level(q(0))` | **dies for every gated config** (deepseek-high: repair 1.14 but only 9.0% below at δ=0.3). Stands for gate-excluded deepseek (0.91 / 23.8% / 0.65) — reported as line-counter-consistent, context only |
| V-E2-2 δ̂ | enumerated absences priced as certain negatives, universally | dies unless a majority of mover configs have ≥ 50% certainty-consistent below-mass | **universal certainty-pricing dies** (2/5: deepseek family 0.62/0.65; sol-none 0.00, glm 0.00, anchor 0.08). Rewritten as heterogeneous wrong-channel landing, quantified by δ̂ |
| V-E2-3 per-line effect | δ=0 gains scale with the number of printed lines | collinearity audit first (unidentifiable if \|r(N−k, deficit)\| > 0.6 — it passed, max 0.34); stands if partial r(gain, N−k \| deficit) ≥ +0.5 | **dies everywhere** (−0.89 to +0.17) |
| V-E2-4a worst-case missingness | results are artifacts of the failed draws | any flipped sign kills the affected claim | **holds**: deepseek-high δ=0 gain stays in [−0.379, −0.229]; even deepseek's 20-PARSE worst case stays negative |
| V-E2-4b mirror split | mirror artifact | load-bearing directions must hold per mirror | **holds** for all five non-ceiling δ=0 gains; caveat: glm's gain is mirror-asymmetric (−0.04 / −0.94), sign-consistent |
| V-E2-4c cross-regime universal | — (robustness of the registered 5/5 contrast under shared-cells + headroom normalization) | dies if not 5/5 strict | **DIED: 4/5, sol-none reversed.** The universal is retired; the 4-of-5 with sol-none's explanation replaces it, per Ali's verdict (i). (Claim-grade gated formulation added 2026-08-20 — see §6 and §11) |
| V-E2-4d count-control concordance | answers respond to record length within ARITH_D0 | modal constant across k in C and D groups | FAIL for sol-none, glm, deepseek — their ARITH_D0 cell-level numbers carry a count-sensitivity caveat |

Analysis-order record: the δ=0.3 redistribution pattern was observed before the
example was formalized (recount at the session's gate checkpoint); the δ=0 arm is the
fully pre-registered out-of-regime test, collected after the prereg froze. The
reformulated claim (identification repaired, interpretation not) re-describes tables
produced under pre-registered statistics, and its alternatives are the ones V-E2-1
and V-E2-3 killed; accepted as verification-covered by Ali's verdict (i).

## 8. Final claims

1. **Enumeration repairs identification only as far as identification was the
   problem — a per-model quantity** *(reworded 2026-08-20; the original said
   enumeration "dissolves identification failure … for every config that had any
   (5/5)," which counted the gate-excluded pair inside the count and omitted
   glm-high's rise).* Error falls for all three gated configurations with a silence
   deficit (−0.092, −0.299, −0.493 bins); blind-point occupancy falls for three of
   the four gated configurations that had any (4.6→0.0, 30.6→12.9, 77.1→50.0%) and
   rises for glm-high (6.4→10.7%); the gap closed is 28% (sol-none), 33% (glm), and
   ≈100% (deepseek-high, reaching its FULL floor). The repair is genuine reading, not
   shape or per-line artifacts (V-E2-1, V-E2-3). Context: both gate-excluded
   configurations also fall (64.1→48.3, 100→70.0).
2. **Enumeration does not repair interpretation** *(reworded 2026-08-20 — the
   earlier version counted the ceiling pair's degradation as evidence for this claim
   and left sol-none's figure unscoped).* Where enumeration frees blind-point mass,
   most of it lands short of correct rather than on it: deepseek-high frees 17.7
   points of occupancy, of which interior mass gains +14.0 against +2.9 correct;
   glm frees 27.1, with +10.8 interior against +15.7 correct — finding the absences
   does not price them. sol-none, whose deficit was mostly interior to begin with
   (65% INT vs 4.6% POS), gains 0% of its gap on the matched nine cells and 28% on
   the full grid — its gains sit in cells outside the matched set. The ceiling
   pair's small interior rises are the length-cost degradation §11 records, not
   interpretation evidence: sol-high +4.3 from correct (88.6→84.3); glm-high +0.7,
   its degradation appearing instead as the blind-point rise (6.4→10.7%). At δ=0.3
   no gated configuration recovers more than 8.0% of its deficit (context: the
   all-seven maximum is 12.5%, in gate-excluded anchor, under the gapless δ=0.3
   gate).
3. **Under uncertainty, enumeration lands models on wrong channels** *(reworded
   2026-08-20 — the earlier version led with a thresholdless word and a peak from a
   gate-excluded configuration).* Below-correct mass rises for the gated movers —
   glm 0→5.6% with its correct-rate falling 36.7→30.0%, deepseek-high 5.6→9.0%,
   sol-none 35.0→38.8% — and lands heterogeneously off the stated rate:
   deepseek-high's moved mass is certainty-consistent (0.62 at δ̂ ≈ 0), sol-none's
   sits at partial discounts (0.00 certainty-consistent). Context, gate-excluded:
   deepseek 7.0→23.8% and anchor 0→32.5%, the largest movements in the roster. The
   δ=0.3 admission gate admits all seven and has no gap (deepseek enters at 0.988
   against the 1.0 bar).
4. **The stated channel is visible in behaviour**: four configurations' implied
   dropout (0.29–0.34) matches the stated 0.30; the three failing configurations
   behave as if it were 0.70–0.74.

## 9. Relation to the literature

**Affirms:** CROWN-QA's redistribution finding — interventions that point models at
the coverage problem redistribute absence errors rather than resolve them — recovered
in a setting where the two presentations provably share one correct answer.

**Adds:** the localization their design cannot express (identification vs
interpretation, separated by a ladder with certified-identical answers); the positive
control (δ=0 shows the enumerated lines are read and used, so the δ=0.3 null is an
interpretation failure, not inattention); and quantification on interpretable scales
— bins of repair, occupancy of the blind point, and δ̂, the effective channel a model
behaves under, directly comparable to the number printed in the prompt.

**Load-bearing cross-reference:** this example's wrong-channel overshoot is what
Example 1's arbitration claim (`../example_1/example1README.md` §8, claim 1) uses to
locate the over-updating direction reported by BayesBench — absent at δ=0, appearing
only under enumeration plus a stated noisy channel — so the paper's §4 regime map
depends on this panel. *(Added 2026-08-20.)* Anyone revisiting the arbitration
framing should reach this panel through §8 claim 3 and §11 rather than the headline
magnitudes: the roster's overshoot peaks (up to 0→32.5%) sit in gate-excluded
configurations under the gapless all-seven δ=0.3 gate; the gated peak is glm
0→5.6%.

## 10. Why this validates the framework

- The ladder is an experiment only because `q(0) = b*` **certifies** that three
  presentations share a correct answer — differences between rungs isolate single
  pipeline stages. No closed-form targets, no certification, no ladder.
- Every named behaviour is a *location* the math pins down in advance: the blind
  point (`b_pos`), the stated channel (`q(0.3)`), certainty-pricing (`q(0)`) — and
  the kill tests are checks of which location the mass sits at.
- δ̂ exists because `q(δ)` is an invertible closed-form curve: the framework turns
  "does the model understand the dropout clause?" into a number on the same axis as
  the clause itself.
- §5 compliance: RULED-anchored with matched controls under frozen gates (§5.1);
  population shapes are gated counts with explicit context clauses and an all-seven
  δ̂ table under the δ=0.3 gate — the one universal that failed its bar was retired
  (§5.2); statistics are framework-built (§5.3); verification attacked explanations
  with pre-fixed kill conditions, and one fired (§5.4); the new cells inherit the
  §5.5 assertion from the frozen grid, re-asserted at build; the claim is one
  sentence (§5.6).

## 11. Caveats and wording obligations (binding for the writeup)

- λ-value claims retired; λ is descriptive ("interpretation share of the deficit").
- **The cross-regime claim is scored gated-only** *(corrected 2026-08-20)*: 2 of 3
  gated non-ceiling (deepseek-high, glm), sol-none reversed-and-explained. The
  as-registered V-E2-4c result — 4 of the 5 pre-fixed non-ceiling configurations,
  a set that includes the gate-excluded pair — stays recorded in §6 and §7 exactly
  as run; the claim-grade sentence and the as-registered result are stated
  separately, never compressed into one count.
- sol-high and glm-high are at ceiling everywhere (their +0.04/+0.11 mild ARITH_D0
  degradations noted; direction consistent with the length cost, magnitude tiny).
  **glm-high's degradation includes its blind-point occupancy rise, 6.4→10.7%
  (9→15 of 140 draws) — this is why the occupancy claim reads 3-of-4, not a
  universal** *(2026-08-20)*.
- glm's δ=0 gain is mirror-asymmetric (−0.04/−0.94); glm, sol-none, deepseek carry
  ARITH_D0 count-sensitivity caveats (V-E2-4d).
- deepseek: gate-excluded at δ=0; 0.988 against a gapless 1.0 bar at δ=0.3; 14%
  PARSE on enumerated records; and the one config consistent with line-counting
  (V-E2-1) — every deepseek number ships with this cluster of caveats.
- δ=0.3 regime is mechanically more forgiving (spec §8 / D26); ARITH arms violate R1
  by design, recorded.
- Draws within a cell share seeds and mirrors; sign claims lean on cell-paired
  statistics, not independent-draw counts.

## 12. Reproduction

From the repo root, in order (first two rebuild/verify the frozen inputs; the harness
does not re-run — it resumes a completed campaign):

```
python3 scratch_2_4c/example_2/arith_d0_stimuli.py       # rebuild + re-freeze stimuli (same sha)
python3 scratch_2_4c/example_2/s3_arith_summary.py       # Panel 2 step-3: d=0.3 pair, 3-point ruler
python3 scratch_2_4c/example_2/s3_ladder_summary.py      # Panel 1 step-3: d=0 ladder, lambda, side-by-side
python3 scratch_2_4c/example_2/s5_e2_tests.py            # verification V-E2-1..4
```

`arith_d0_prereg.md` is the pre-collection registration; `results_arith_d0/` holds
the live campaign (checkpoint + results, stub kept for plumbing provenance). The
shared frozen-gate computation lives one level up (`../gate_and_recount.py`), and the
dropped candidate-2A exploration (`../s3_dial_summary.py`) stays outside this folder —
its count-up/weight-down design insight feeds paper §6, not this example.
