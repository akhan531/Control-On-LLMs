# EIML3 paper outline — reconciled

**Venue:** EIML3 @ NeurIPS 2026 · **Deadline:** 2026-08-29, 6:00 PM ET
**Length:** 4 pages excluding references · `neurips_2026.sty`, single column
**Written:** 2026-08-20 (supersedes the 2026-08-13 outline entirely)
**Revised:** 2026-08-21 rev 2 — folds in V-24-1/2/3, the §5-filter sweep (items 30–33),
the closed-avenue check (item 32), and the four literature anchors read in full (items 35–39).
**Rev 3, 2026-08-21** — folds in checklist items 40 and 41: the D-cell level split (G2.4
killed), the W1 band pre-test and its low-side addendum (G1.4 closed), the one-bin degeneracy
exhibit (G4.5 closed, and it is analytic), the retirement of the draw-level `p ≈ 0.004` in
favour of cell-level sign tests, and the per-arm draw census.
**Rev 4, 2026-08-22** — §4 rewritten after full-text reads of Imran et al. and BayesBench.
Four substantive changes and three consistency repairs, all listed in §0 below.

**This document defines the canonical section numbering for the paper.** Every section
reference in `eiml_submission_checklist.md` items 13, 47, and 50 resolves against this file.

**Companion:** `claims_to_evidence.md` holds the four claims with populations named on every
evidence row, the banned-numbers list, and the gap register. Where the two disagree, the
claims table is authoritative on numbers and this file on structure.

---

## 0. What changed and why

The 2026-08-13 outline was written before the main campaign was scored. Its headline
statistic, its headline figure, and its second figure are all dead: normalised `s` was
audited and retired, and the registered dissociation did not clear its bar.

The reframing: **the contribution is the instrument, not a discovery about LLMs.** Two
worked examples exist to show the instrument does real work.

### Decisions locked 2026-08-20

- **D1.** The three-way decomposition and the `W̄` machinery are **cut**. `W̄ = 0` identically
  in every reported cell. One-sentence forward pointer only; it goes to the EC paper
  alongside the N-scaling law.
- **D2.** Exactly one numbered proposition and one numbered lemma.
- **D3.** No time index anywhere. Symbols: `π`, `b_pos`, `q_δ`, `q_0`, `b*`.
- **D4.** The meridian time-constant result is **out**.
- **D5.** `b*` is defined at `δ = 0` only, as the name for `q_0` there. At `δ > 0`, `q_0` is
  the **credulous point**, sitting past correct. This is what makes below-correct draws in
  the dropout arms readable as over-reading.

### Verdicts locked 2026-08-21

- **V-24-1.** λ is retired **as a registered prediction target**, retained as a **descriptive
  measured quantity**. §5 may quantify the split. Requires a dated amendment in
  `example2README.md` §5 and §11 before drafting.
- **V-24-2.** One-sidedness is a property of the **non-enumerated arms** (FULL and
  PARTIAL_RULED), **not of `δ=0` generally**.
- **V-24-3.** The spec does not say whether a P5 failure excludes a configuration's cells
  from P1–P3 or only flags them. **Both readings are reported, strict first.**

### Rev 4 changes, 2026-08-22

Four forced by reading Imran et al. (arXiv:2507.17951) and BayesBench (arXiv:2606.30850)
in full:

- **C1. The Imran 30% figure does not exist.** Confirmed absent from main text and all
  appendices. It was a citing paper's characterization. Moves from "do not cite without the
  full text" to **never cite**. `citation_ledger.md` §1.5 needs the same amendment.
- **C2. Imran's under-updating is unexplained by its own authors, and they offer a
  deflationary account of it.** The discussion says outright that it is unclear why every
  gradient falls below 1, Limitations defers it to future work, and Appendix Figure 9 ties
  the gradient to how improbable their evidence strings are. §4 ¶1 may cite them for the
  under-direction **claim** and must not lean on them for mechanism.
- **C3. The elicited-versus-computed contrast is now §4's positioning sentence.** Every term
  in Imran's expected update carries the subscript `θ`: the likelihood ratio is read off the
  same model's token log-probabilities, in a separate instance. Our target is computed from a
  stated generative process over exact rationals, so the confound they flag in themselves
  cannot arise here. This is a sharper contrast than "expresses both directions on one task"
  and costs about fifteen words.
- **C4. The extremity kill was aimed at the wrong prediction.** Rewritten in ¶5 below. The
  old form said extremity predicts level-1 draws moving **to level 0**. Extremity predicts
  movement to **both** endpoints, and in the D cells level 0 is the *over-weighting*
  direction, so a draw landing there is not displaced at all under our sign convention. The
  old form therefore aimed the competing account at the direction we report zero of, quietly
  merging claim 2's one-sidedness with the anchoring claim. A careful reader separates them
  and the kill stops working.

Three consistency repairs found while reconciling:

- **C5. §3's response-scale paragraph was still the pre-rev-3 text** and contained
  *"all seven configurations agreed,"* which is on the banned-numbers list in
  `claims_to_evidence.md` §7. Replaced below with the rev-3 measured-bands text.
- **C6. §3's campaign sentence carried `~7,050` as a bare total**, also banned. Replaced with
  7,051 usable of 7,210 attempted across five arms, with the pre-test stated separately.
- **C7. This outline violated its own R4 in five places** — "frozen spec," "stimuli frozen at
  a sha256," "frozen registration," "data frozen before it was conceived," "pre-registered
  dissociation." All replaced. The rule is binding on the outline too, because the outline is
  what the paper gets drafted from.

### Wording rules, from items 32 and 33

- **R1 — spans and universals, never singletons.** Filter part 2 forbids "model X does this
  and the others don't." Report ranges.
- **R2 — the universal is usually hiding behind the fraction.** "4 of 5" prior-crossing is
  "all four with error mass to test"; "rises in 4 of 5" is "falls in none of five."
- **R3 — state the population on every count.**
- **R4 — "frozen," "pre-registered," "pre-committed" are never used unqualified.** Stated in
  full in §6 below. Binding on §3, §5, §6, and on this document.
- **R5 — significance goes at the cell, never at the draw.** Draw tallies are descriptive
  counts with attempted denominators and carry no p-value.

### Carried forward intact from the old outline

§0.2's N-scaling carve-out · the introduction's opening framing · Figure 1 as a concept
schematic · the de Punder trimming/censoring positioning · the three-arm design table ·
the `q_0 = b*` pivot · the two-defects-designed-out note · the saturation-ceiling rule.

---

## 1. The framework, stated once

**Channels are the input. The framework is a map.**

> Given the set of channels a transcript exposes, the framework returns the operations an
> observer must perform and the belief it should hold.

Every experiment is a measurement of the observed answer against the returned belief.
Varying the channel set varies both outputs, and which output is held fixed determines what
the experiment tests.

**The map is many-to-one on targets.** Three different channel sets return the same target.
That is the design's entire asset and it licenses every comparison in the paper.

---

## 2. Page budget

| § | title | pages |
|---|---|---|
| — | title, abstract | 0.25 |
| 1 | Introduction | 0.50 |
| 2 | The framework | 0.75 |
| 3 | The instrument | 0.65 |
| 4 | Example 1: which direction does the error run? | 0.60 |
| 5 | Example 2: identification or interpretation? | 0.60 |
| 6 | What the instrument cannot identify | 0.40 |
| 7 | Related work and limitations | 0.25 |
| | **total** | **4.00** |

**Objects:** 2 figures · 2 tables · 3 numbered equations · 1 proposition · 1 lemma.

---

## 3. Title and abstract

### Title

**Working:** *Channels to Targets: A Closed-Form Coordinate System for Silence-Blindness in
LLM Observers*

Alternatives: *What the Transcript Doesn't Say: Benchmarking Silence-Blindness with
Closed-Form Reference Beliefs* · *Benchmarking Silence-Blindness*. All assert the instrument
rather than a behavioural finding. Revisited at item 86.

### Abstract — ~150 words, written last (item 87)

Five sentences:

1. Absent evidence under a disclosure rule is informative, and whether LLMs use it is unclear.
2. Given what a transcript contains, the required operations and the correct answer are both
   computable in closed form, so any answer has a measurable position.
3. Three different transcripts share one correct answer, which makes the comparisons
   controlled rather than three separate tasks.
4. **Revised per V-24-2 and item 30a.** Among the five configurations admitted by the
   competence gate, in the two conditions that do not enumerate the absences, under-weighting
   is the only direction of error observed; enumerating the absences repairs identification
   but not conversion, and introduces over-reading. **Not** "across seven configurations at
   `δ=0`" — that named the wrong population and the wrong scope at once.
5. **Revised per V-24-3.** The primary registered prediction did not clear its bar, and we
   report the outcome under both readings of our own exclusion clause.

**Every claim sentence typed by Ali** (checklist item 66).

---

## 4. Section-by-section

### §1 Introduction — 0.50 pages

Four paragraphs, no subsections.

**¶1 — the problem.** An observer sees `k` positive reports from `N` analysts under a rule
where only positives are filed. The `N − k` absences are evidence.

**¶2 — the move.** Write down what the transcript contains, and both the operations required
and the correct answer follow in closed form. A real answer then has a *location* relative to
that target.

**¶3 — the asset plus venue tie.** One sentence: three transcripts that differ in what they
show share the same correct answer, so comparison across them is controlled. One sentence
tying to EIML's *"Can we benchmark ignorance, blind spots, and unknown unknowns?"*

**¶4 — contributions.** Four typed bullets matching the four claims. **Bullet 2, per V-24-2**,
scoped as *under-weighting is the only direction observed among gated configurations in the
conditions that do not enumerate the absences* — never "LLMs are silence-blind," and never
scoped to `δ=0`, which is now known to be false.

**Figure 1** — top of page, spanning.

> **Spec.** Horizontal axis: `P(target)` on `[0,1]`. The four measured response bands shaded
> and labelled 0–3 (`≤0.20`, `0.40–0.45`, `0.55–0.70`, `≥0.80`). Cell A1's points at true
> values: `π = 0.500`, `b* = q_0 = 0.190` (level 0), `b_pos = 0.948` (level 3). Above the
> axis, three arrows labelled `FULL`, `ARITH_D0`, `PARTIAL_RULED`, all landing on `0.190`.
> No data. Caption states the thesis in two sentences: same target, three transcripts, three
> different amounts of work.

### §2 The framework — 0.75 pages

The contribution, and the largest non-example section by design.

**Setup.** Two candidates `A = {a_0, a_1}`, exactly one responsible, uniform prior `π`. `N`
analysts run conditionally independent binary assays with `P(POSITIVE | responsible) = p`,
`p > 1/2`. **A report is filed only on POSITIVE.** Optionally each analyst independently
fails to file with probability `δ`. **State `|A| = 2` explicitly** — one-dimensionality
depends on it, and "coordinate" is literal only there.

**Lineage, one clause, new 2026-08-21.** This is the bookbag-and-poker-chip paradigm of
Phillips and Edwards conditioned on a disclosure rule. Naming the lineage costs a clause and
buys legitimacy: the design is a variant of the classic conservatism paradigm, not an
invention. **Rev 4 confirmation:** BayesBench opens on the same paradigm and cites Edwards
1982 plus Phillips and Edwards 1966. Our ledger's decision to cite the 1968 original and note
the reprint stands, but the two forms must not be mixed within the paper.

**The map — one sentence, italicised, set off.** *Given the set of channels a transcript
exposes, the framework returns the operations an observer must perform and the belief it
should hold.*

**Reference beliefs — three displayed numbered equations.** With `L(a)` the likelihood of a
positive under candidate `a`:

- **(1)** `b_pos(a) ∝ L(a)^k` — reads the positives as if they were the whole record
- **(2)** `q_δ(a) ∝ [(1−δ)L(a)]^k · [1 − (1−δ)L(a)]^(N−k)` — conditions on presences and
  absences, discounting each absence by the chance it was a dropout
- **(3)** `q_0(a) ∝ L(a)^k · (1 − L(a))^(N−k)` — treats every absence as certain
  disconfirmation

One sentence defining **`b* := q_0` at `δ = 0` only**, with `q_0` at `δ > 0` named the
**credulous point**.

**Proposition 1 (the pivot).** `q_0 = b*`. Two-line inline proof: at `δ = 0` the silence
factor `(1 − L(a))^(N−k)` in (2) *is* the negative-result factor in (3). Then one sentence on
the consequence, and one that this is verified over exact rationals across all 14 cells, with
no floating point anywhere in the model.

**Lemma 1 (ordering).** Because `p > 1/2`, each absence multiplies the responsible candidate's
mass by a strictly smaller factor, so `b_pos`, `q_δ`, `q_0` are strictly ordered in log-odds,
and `q_δ` moves monotonically toward `b_pos` as `δ` grows. One line of proof. **This is what
licenses the words "between" and "coordinate."**

> **G1.2 status, rev 4.** The proof was written on 2026-08-22 and now exists in `main.tex`.
> **One defect remains in the statement, not the proof:** the proof establishes strictness
> only for `N − k ≥ 1` and `0 < δ < 1`, but the lemma as stated claims strict ordering
> unconditionally, which contradicts Proposition 1 at `δ = 0`. Move both conditions into the
> statement before this goes anywhere near a reviewer.

**Table 1 — the map.** The paper's most information-dense object.

| condition | channels in transcript | operations required | target |
|---|---|---|---|
| PARTIAL_BLIND | positives | aggregate | `b_pos` |
| FULL | positives, printed negatives | aggregate | `b*` |
| ARITH_D0 | positives, enumerated absences | convert, aggregate | `b*` |
| PARTIAL_RULED | positives, derivable absences | identify, convert, aggregate | `b*` |
| ARITH_D30 | positives, enumerated absences, `δ` | convert, aggregate, discount | `q_δ` |
| RULED_D30 | positives, derivable absences, `δ` | identify, convert, aggregate, discount | `q_δ` |

**Operations paragraph.** Define the four: **identify**, **convert**, **aggregate**,
**discount**. State the nesting `{a} ⊂ {c,a} ⊂ {i,c,a}` — the ladder Example 2 walks.

**One pre-emptive clause, new 2026-08-21 (item 32, avenue 3).** Say why `identify` is a single
operation: once `N` is stated, noticing that reports are missing and identifying which are
missing are the same subtraction. This forecloses the four-stage reading at the cost of one
clause. One honest sentence in the same place: `aggregate` is never isolated, since no
condition sits below `{a}`, and `discount` is identified only by the δ=0.3 arms.

**Forward pointer, one sentence.** A three-way decomposition of total error and a group-size
scaling law follow from the same objects and are developed elsewhere.

> **Layout risk.** Table 1 carries §2, §4, and §5 simultaneously. Contingency: split the
> operations column into a separate two-column table and leave Table 1 as condition →
> channels → target.

> **Rev 4, `discount` collision watch.** BayesBench's related-work section cites Zhang et al.
> (arXiv:2512.18489) as modelling LLM updates as Bayesian filters with systematic evidence
> discounting, in the same sentence as Imran. That is our fourth operation and our `q_δ`.
> G4.7 is still the only unread item that could collide with this row. If it collides, this
> row needs one sentence of positioning.

### §3 The instrument — 0.65 pages

**Response scale. Rev 4: replaces the stale pre-rev-3 paragraph (C5).** Four ordinal levels
from two enum fields, candidate × two-level confidence. **Bands were measured, not assumed,**
on both sides and without mirroring the low side from the high. A pre-test over 32 stimuli at
**three** draws per stimulus across all seven configurations (659 of 672 usable) placed the
switch edges at **0.20 and 0.80**, with a low–high asymmetry of **0.000 at the widest for six
of the seven configurations** on the wording the main campaign uses; `anchor` is the sole
exception at 0.1. **Never write "all seven configurations agreed"** — banned. Bands were never
shown to the models.

**Stated limitation, not a robustness result.** CAL samples at a resolution of 0.10, so the
nominal cuts and the measured 0.20/0.80 edges both fall inside the same sampled interval.
Invariance of level assignment across them is a **sampling-resolution fact**, and must be
stated as one.

**Design constraints, four clauses.**
- Every cell asserts `level(b_pos) ≠ level(target)` at build time. **Verified 2026-08-21 in
  both regimes:** fourteen for fourteen at δ=0, nine for nine at δ=0.3.
- Prompts never use silence vocabulary, enforced by a forbidden-word list at build.
- Every stimulus appears in both label orderings.
- Count-control cells invert the correct level, so a fixed high-confidence responder is
  separable from a competent one.

> **Rev 4, free precedent.** BayesBench counterbalances MCQ position bias by cyclic rotation
> of the option-to-position map, with a stated proposition and proof that the rotation average
> cancels additive position bias. Our both-orderings constraint is the `K = 2` case of exactly
> that construction. One clause naming the precedent is cheap legitimacy for a design choice a
> reviewer might otherwise read as ad hoc.

**The band gaps are load-bearing, revised 2026-08-21.** Better than the current sentence:
the bands have real gaps, and the viability filter is how the design survives them. **Five of
fourteen cells fail `banked_viable`** on gap placement — B2 and B3 put `q_0.3` at 0.366 and
0.392 inside the 0.20–0.40 gap, D1–D3 put it at 0.512–0.524 inside the 0.45–0.55 gap — and
that is what reduces 14 cells to 9. The filter is also stricter than cell validity requires:
a cell carrying the dropout arms needs `level(q_0.3)` distinct from `level(b_pos)` **and**
from `level(q_0)`, which is why stating a dropout rate can change the correct answer.

**Statistics.** `s1 = |l_obs − l_cor|`, `s2 = l_obs − l_cor` (positive = under-weighted toward
the target), `s3 = P(l_obs = l_cor)`, where `l_cor = level(target(C))` read off Table 1.

**Competence gate.** A configuration failing the matched **FULL** condition is excluded,
because a RULED failure from a configuration that also fails FULL is a floor effect. **Rev 4:
the gate is on FULL alone**; the earlier "FULL or ARITH" phrasing did not match
`claims_to_evidence.md` and would have made §4's control arm incoherent, since the gate has to
select on FULL for the FULL/RULED asymmetry argument to hold. Name both excluded
configurations with their FULL scores: five admitted at 0.200, 0.421, 0.457, 0.752, 0.764
bins; excluded at 1.609 (`deepseek`) and 1.800 (`anchor`). **The gap from 0.764 to 1.609 makes
membership bar-insensitive** — say so.

**The anchor consistency sentence.** `anchor` is the exception in four independent places —
W1 reachability, W1 wording stability, W1 low–high asymmetry, and the `δ=0` competence gate —
plus P4 on D1–D3. Four instrument checks and one behavioural gate select the same
configuration. That is a consistency result, not five separate caveats.

**Campaign, one sentence. Rev 4: replaces the banned bare total (C6).** Across five
experimental arms the campaign holds **7,051 usable draws of 7,210 attempted**, at five draws
per stimulus: 2,940 calls at `δ=0` with 2,894 usable; 620/630 at `δ=0.30`; 623/630 ARITH_D30;
959/980 ARITH_D0; 1,955/2,030 sweeps. The W1 pre-test's 659/672 sits **outside** that total,
on a different stimulus set at three draws per stimulus. **Never write `~7,050`.**

**Registration, one sentence**, with scoring deferred to §6. R4 applies hard: predictions,
gates, and kill conditions were fixed in a specification document and implemented as
executable decision rules, and §6 states plainly what the record does and does not establish
about when they were fixed.

### §4 Example 1 — which direction does the error run? — 0.60 pages

> **Rev 4.** This section is rewritten below after full-text reads of both anchors. The
> paragraph structure is unchanged; ¶1 and ¶5 change substantively.

**¶1 — the disagreement, rewritten 2026-08-22.** Two anchors, on populations that do not
overlap, and the non-overlap is load-bearing.

- **Imran et al.** find that **pre-trained-only** checkpoints update less than Bayes requires,
  with the shortfall shrinking as models scale. Measured over token log-probabilities. Cite
  them for the **under-direction claim only**. **Do not cite the 30% figure — it does not
  exist** (C1). **Do not present the finding as an established mechanism** (C2): their own
  discussion says it is unclear why every gradient falls below 1, and their Appendix Figure 9
  ties the gradient to how improbable their evidence strings are, which is a deflationary
  account of their own headline.
- **BayesBench** evaluates **instruction-tuned** models across turns and reports both
  directions, **with the direction shifting across scale** — smaller models stay near the
  middle, larger models can push toward the extremes when the evidence is skewed. **Rev 4
  wording caution:** do not write "split by scale." Their Figure 2 caption says trajectories
  overshoot *or* undershoot across scales, so both directions are present at every size and
  "split" reads as a partition the paper does not support. Their Takeaway 1 also says larger
  models *can* over-update, conditioned on skewed evidence; keep both hedges.
- **Do not write "BayesBench reports over-confidence."** That was the record's error,
  corrected at item 36.
- The construct name is **conservatism**, after Edwards.

**The positioning sentence, new rev 4 (C3).** Every term in Imran's expected update carries
the subscript `θ`: the likelihood ratio is elicited from the same model, in a separate
instance, off token log-probabilities. Our target is computed from a stated generative process
over exact rationals, so nothing about the correct answer depends on what probability any
model assigns to any string, and the confound they flag in themselves cannot arise here. **Use
this instead of "our coordinate system expresses both directions on one task."** It is
sharper, it does positive work for the paper's thesis, and it costs about fifteen words.

**¶2 — the disclosure.** *Both anchors were selected after the data existed.* The campaign's
predictions were registered; the literature engagement was not. Plain, unburied, one sentence.

**¶3 — the setup in framework terms.** Two channel sets, `{positives, printed negatives}` and
`{positives, derivable absences}`, returning different operation sets but **the same target**
by Proposition 1. Over-weighting is only *expressible* where `l_cor ≥ 1`, which is cells
D1–D3; `l_cor = 0` in the other 11. State the denominator honestly and up front.

**¶4 — the result and the control, restructured 2026-08-21 (item 30 part 1).** The gate
selects on FULL, and V-24-2 made FULL a claim-carrying arm, so the two arms are **not
symmetric evidence** and the 0/300 must not be pooled.
- **The result:** on D-cells, PARTIAL_RULED runs **47–0** toward under-weighting across the
  five gated configurations, **150 attempted and 150 usable, zero failures** — the denominator
  is attempted draws, which is the stronger form and costs nothing. Gate on FULL, outcome on
  RULED, so the result arm is unselected.
- **The control:** FULL runs **9–0**, same 150 attempted. This shows the direction persists
  under an easier channel set among configurations chosen for accuracy there. All five FULL
  over-reads across the full roster come from `anchor` and `deepseek`, exactly the two the gate
  excluded, so this arm cannot be independent corroboration.

**Significance goes at the registered grain, revised 2026-08-21 (item 41, and R5).** The spec
makes the **cell** the unit of analysis, pooling mirrors and draws to one modal level.
Two-sided exact sign test over the 15 config-by-cell units: **RULED 8–0, `p = 0.008`**;
**FULL 5–0, `p = 0.063`**. The result arm survives at the registered grain; the control does
not reach significance and does not need to. The remaining 7 units carry no displaced mass and
are **undefined rather than failed**.
**Strike `p ≈ 0.004` wherever it appears.** It is `2 × 0.5^9` at draw level, treating 9 draws
from 3 configurations as independent, and it **contradicts the sentence item 78 requires** —
that the paper assumes no independence across draws. Lead with the universal instead: zero
draws past `b*` in any of the five gated configurations, in the only cells where over-reading
is expressible. The 47 then reads as the number of chances the direction had to reverse.
**Do not use the 176 denominator** — it is an all-seven pool (G2.1). Nor **206**, which is the
same defect one layer down in `gate_and_recount.py`: 150 gated + 26 deepseek + 30 anchor + 4
failures.

**¶5 — the sharper claim.** The error anchors on `b_pos`, not on `π`. Error mass sits above
the prior or exactly at `level(b_pos)`, unreachable by symmetric shrinkage, in **all four
admitted configurations with mass in the tested region** (R2) — sol-none 8/91, deepseek-high 50/80, glm
140/140 with 108 exactly at `l_pos`, glm-high 17/52. sol-high produces 16 error draws, all at level 1,
none above the prior and none at `level(b_pos)`, so it contributes no mass to the tested region; the
universal is four of five, not zero error draws (corrected 2026-08-24 against `s5_prior_crossing.py`).
Kill bar of 2 fixed at a checkpoint before the test ran (R4:
process claim). **Note (H1): `l_pos >= 2` in every cell, so "at `level(b_pos)`" is a subset of
"above the prior" and that disjunct is vacuous; the anchoring claim needs the at-`l_pos` share
reported separately.** Blind-point occupancy **falls in none of five** and rises in four. Quote the
`δ=0`-only numerators, never the pooled RULED-arm totals (G2.2).

**One clause on why the test is well-defined:** the uniform prior at 0.5 falls inside the
0.45–0.55 band gap, which straddles it exactly, so levels 0 and 1 lie wholly below and 2 and 3
wholly above, with no level ambiguous.

**The fourth killed alternative — REWRITTEN rev 4 (C4).** The old form is wrong and must not
be drafted from. Replace it entirely with the following.

> **Which BayesBench result to cite.** Cite the **coin-flip** over-updating result, not the
> medical-triage one. Two reasons, both of which a referee can check. Triage has **no
> closed-form Bayesian reference** — the paper says so explicitly — so its errors are scored
> against ground-truth labels rather than against a posterior. And triage's four levels are
> semantic urgency categories, whereas our four levels are probability bands. The coin-flip
> result is both Bayes-referenced and on a probability scale, so it is the structurally
> matched threat to Claim 2. The triage result may be mentioned in the same breath as
> corroboration that the effect is not confined to one environment, but it is not the anchor.

> **The prediction, stated correctly.** An extremity account predicts mass at **the endpoints
> of the response scale** — levels 0 and 3 — not at one endpoint. The old text said extremity
> predicts level-1 draws moving *to level 0*. That is half the prediction, and it is the half
> that is not even displacement: in the D cells `l_cor = 1` and `l_pos = 2`, so a draw at
> level 0 is an **over-read**, not a displaced draw. Aiming the competing account at the
> direction we report zero of merges Claim 2's one-sidedness with the anchoring claim, and a
> careful reader who separates them finds the kill does no work.

> **The kill, in the form to draft.** Of the 47 displaced RULED draws, **44 land at level 2**,
> which is not an endpoint and is exactly `level(b_pos)`; **3 land at level 3**; **0 land at
> level 0**. Total endpoint mass is **3 of 150 attempted, 2.0%**. The `b_pos` account names an
> interior level in advance; extremity names the two levels that stay nearly empty. Under R2,
> the universal behind the fraction: level 2 outnumbers level 3 in **all three configurations
> with displaced mass to test** (glm-high 5 v 1, deepseek-high 11 v 0, glm 28 v 2); the sol
> family produces none, so the test is undefined there rather than failed. FULL: 9 at level 2,
> 0 at level 3.

**¶5b — required (row 2.12).** One-sidedness here is a property of these two conditions and
not of the instrument. The over-direction **is** recoverable on this instrument with these
models, via §5's ARITH_D0 over-reads and the `δ=0.3` wrong-channel result, so the objection
"your roster is too small to produce the over-direction" becomes "your instrument sees it only
where the transcript enumerates the absences," which is the thesis. This is where the §5
dependency is discharged; either order the sections accordingly or state the dependency.

**¶6 — one sentence.** Zero new API calls. This example runs entirely on draws collected
before it was conceived.

**Figure 2(a)** — left panel of a two-panel figure.

> **Spec.** Signed `s2` on D-cells, five gated configurations, FULL and RULED paired. Zero
> line marked. Region below zero shaded and labelled **expressible, unobserved**. Correct as
> specced under V-24-2, since it already restricts to the two non-enumerated arms.
> **Addition 2026-08-21:** the panel must make clear that RULED is the result arm and FULL the
> control, since the gate selects on FULL.

> **Rev 4 owed read, before §4 is final.** BayesBench's related-work section points at
> **Gupta et al. 2025**, *Enough Coin Flips Can Make LLMs Act Bayesian*, ACL 2025 long paper,
> summarized there as: with enough biased-coin flips in context LLM predictions can approximate
> the exact posterior, **with residual error attributable to the prior rather than the update**.
> That sits directly on ¶5's axis, since we locate residual error at `b_pos` — neither the
> prior nor correct. Not in `citation_ledger.md`. Twenty-minute read of the abstract and the
> residual-error section. Fold into item 53's light pass on 2026-08-25 at the latest; if it
> agrees, it is a citation that makes ¶5 look well-read, and if it disagrees, better to learn
> it on the 25th than in review.

### §5 Example 2 — identification or interpretation? — 0.60 pages

**¶1 — the question.** When a system fails to use silence, is it failing to *notice* the
absences or failing to *interpret* them? In general the two are confounded.

**¶2 — why the ladder exists.** Table 1 rows 4, 3, and 2 have strictly nested operation sets
`{i,c,a} ⊃ {c,a} ⊃ {a}` and, by Proposition 1, **one shared target**. Each rung deletes exactly
one operation, and the channel change is the mechanism of deletion. No ad-hoc design yields
this; it falls out of the map.

**¶3 — the data.** **980 calls, 959 usable.** Stimuli fixed at a sha256 before any call; the
registration document is committed, though three days after collection (§6 states this).
**R4 applies to this sentence** — "fixed at a content hash," never "frozen."

**¶4 — the result, with the headline first.** Deleting `identify` collapses residence at
`b_pos` for all three non-ceiling gated configurations (4.6→0.0, 30.6→12.9, 77.1→50.0) — the
absences *were* going unnoticed. But interior mass **rises in every one of them** (65.4→66.9,
28.4→42.4, 17.1→27.9): the freed answers land short of target. **Identification is repaired;
conversion is not.** The rising interior mass is the headline — a universal over the claim
population with no fraction to defend. glm-high's occupancy **rises** 6.4→10.7 and is reported;
it sits outside the population by the registered 0.15-bin ceiling guard.

> **Rev 4, cross-method recovery for this paragraph.** BayesBench's headline gap is between
> **inferring latent structure** and **using it to update the downstream prediction**: scaling
> improves the first without reliably improving the second, stated in their abstract, Takeaway
> 2, and their conclusion. That is the same joint as "identification is repaired, conversion is
> not," reached by a different mechanism on a different task. This is as strong a recovery
> point as the CROWN-QA one and is currently in neither the outline nor the draft. One
> sentence, placed with the anchor below.

**¶5 — the per-model split.** State the part-2 sentence first: **five of five admitted
configurations receive a well-defined verdict**, three numeric positions and two adjudicated
`ceiling`. Then, under V-24-1, the numbers: **the closures span 28% to 114%**, with the top of
the range past the printed-negatives floor. Phrased as a span per R1, never as a fact about
one configuration. **Define λ explicitly at first use and never call it attenuation** — the
symbol names a different object in the closed-avenue record (item 23b). Per V-24-1, report λ as
a **measured descriptive quantity**, not scored against a registration, because the
registration for this rung carried no numeric bounds.

**¶6 — the δ=0.3 null, moved up.** **The strongest population-level statement in either
example** and currently buried: no configuration recovers more than 12.5% of its deficit,
gated ≤ 8.0%, worst-case missingness bound ≤ 0.20 bins — an interval containing all seven
configurations, needing no gating argument. At `δ = 0.3` the target moves to `q_δ` and `q_0`
becomes the credulous point past correct, which is what makes below-correct draws readable as
over-reading. One contrast fixed at a checkpoint died at 4/5 and was retired rather than
rescued. **Banned: "4 of 5" cross-regime.**

**¶7 — the record-length paragraph, new 2026-08-21 (item 30 part 4).** One consolidated
paragraph rather than three findings a reviewer assembles into an objection. There is real
evidence for the alternative: V-E2-4d's count-control concordance fails for sol-none, glm, and
deepseek, and both ceiling configurations move the **wrong way** under enumeration (+0.043,
+0.114), which is what a record-length cost looks like. The defence: length cannot explain
glm's 0.493, and V-E2-3's per-line effect dies everywhere (−0.89 to +0.17) after a collinearity
audit at max \|r\| 0.34. State that V-E2-4d inherits §6's P5 defect — its constancy criterion is
confounded in the C group and clean in the D group. **Banned: "five configurations respond to
record length."**

> **Rev 4, useful precedent.** BayesBench hits a format confound of the same shape and reports
> it: their Appendix B.3 finds the single-turn/multi-turn gap comes from how short atomic items
> are packed across turns rather than from the multi-turn format itself, and states that the
> effect does not appear when each turn carries a complete self-contained item. If ¶7 needs a
> sentence establishing that format effects are a real hazard others rule out rather than a
> defensive invention of ours, this is it.

**¶8 — the bridge back to §4.** Over-reading appears at `δ=0` too, once absences are
enumerated: **2 over-reads in 150 expressible gated draws** in ARITH_D0 against 0 of 300 in the
non-enumerated arms, and the two configurations are exactly the two with the largest repairs.
The direction of error flips with the channel set, at both dropout rates.

**The anchor, rewritten 2026-08-21.** CROWN-QA is **cross-method recovery for this half of the
example**, not adjacent support for the ladder. Their over-closure is the closed-world
assumption applied where it does not hold, which in our coordinates is the credulous point.
Positioning in one sentence: they ask whether absence licenses a negative answer at all,
holding the question fixed and varying how coverage is described; we assume licensing and ask
how far the belief should move, holding the target fixed and varying which operations the
transcript requires.

**Cut, not demoted (item 32).** The cross-regime contrast is out. It brushed three closed
avenues at once and is 2 of 3 once gated.

**Figure 2(b)** — right panel.

> **Spec.** Three rungs on `x` in nesting order (PARTIAL_RULED → ARITH_D0 → FULL), five gated
> configurations as lines, `s1` on `y`, target floor at zero, `b_pos` distance marked as a
> horizontal reference. Shows both the drop and the residual gap.

### §6 What the instrument cannot identify — 0.40 pages

Framed as a contribution, not an apology. This section is Claim 4.

**Table 2 — registration scoring.** Three tiers, labelled as three tiers. **Tier labels record
where an item was registered, not that its ordering was verified** (R4).

| item | tier / where registered | outcome |
|---|---|---|
| **P3 (primary)** — gap > 0.5 in ≥ 2 of 3 families | Tier 1, specification, internal timestamp | **Falsified under a strict reading of our P5 exclusion clause (0 of 3); held in 1 of 3 under a loose one.** glm alone clears at 0.821 and glm also fails P5. Both reported, per V-24-3. |
| P1 / P2 — the two halves | Tier 1, same | 1 of 3 each, **in different families**: P1 glm, P2 sol-high. No family carries both halves. |
| Non-control cell bar | Tier 1, **amended** | Spec text says 8 of 11; executed as **6 of 8**. The non-control set is A1–A5 and B1–B3, so "11" was a miscount. Proportion 0.727 → 0.75. Dated amendment. |
| ARITH_D0 λ predictions | Tier 2, sha256 `028d9be8…` | Directional, no numeric bounds. Scored as directional. |
| ARITH_D0 ceiling guard | Tier 2, same | Sharp 0.15-bin threshold, scored cleanly. |
| Cross-regime contrast | **Tier 3, fixed at a checkpoint**, absent from the specification | Died at 4/5; gated, 2 of 3. Retired rather than rescued. |

**Two framing sentences the table needs.**
1. The spec defined a **three-band** outcome space: ≥2 families passes, 0 families is
   falsification with a registered consequence, 1 family is neither. Naming the bands is what
   makes the dual reporting legible.
2. **Ordering is not established for any artifact in this project, and the section says so
   in its own text.** *Rewritten rev 3 after G1.5 closed; this replaces the narrower
   stimulus-sha concession.* The sha establishes that the stimuli analysed are the stimuli
   registered. It does not establish that any registration predates the calls, and neither
   does anything else: version control begins **2026-08-20**, after both the 08-14 pre-test and
   the 08-15 campaign; draw records carry no wall-clock field; and `silence_v2_spec.md`, where
   P1–P5 live, has a modification time roughly five hours **after** the campaign it registers.
   Write this as **one plain sentence covering the spec, the stimuli, and the band pre-test
   together** — the reviewer who checks will find the general fact, so conceding the general
   fact is both cheaper and more honest than conceding an instance. Full statement in
   `PROVENANCE.md` at the repo root; cite it rather than expanding here.

   **Consequent wording rule, binding on the whole paper (R4):** "frozen," "pre-registered,"
   and "pre-committed" are **never used unqualified**. Table 2's tier labels describe *where*
   something was registered, not that its ordering was verified. Kill conditions are described
   as fixed at a checkpoint before their test ran — a **process claim**, labelled as one, not a
   provenance guarantee. The band pre-test is described as **measured rather than assumed**,
   which the data establishes, and never as operating under a frozen plan, which the record
   does not.

**Blind-spot statements. Restructured 2026-08-21 around a pattern rather than a list.**

**The pattern, stated once, then instantiated three times.** Three of these are the same
shape: two properties you would want to vary independently, welded together by the geometry.

1. **Count against weight.** Pinning the target while raising the number of absences from 4 to
   12 forces `p` from 0.90 to 0.56, and the evidence the silences carry falls from **5.61
   through 1.83 to 0.71 nats**. Tripling the count drops the evidence roughly eightfold. Closed
   form, no draws required. *The strongest item in the section — a reviewer cannot argue with
   it.*
2. **Evidence strength against over-read expressibility.** The D cells carry `eps0` of
   0.065 / 0.080 / 0.064 nats against 3.84 for C1, **around fifty times weaker**, and are the
   only cells where over-reading is expressible. Over-reading needs headroom below `b*`,
   headroom needs `b*` high, and `b*` high means the silences carried little.
3. **Over-read visibility against under-read visibility.** In the D cells `b*` sits at
   0.440 / 0.421 / 0.440, inside band 1, which spans 0.40–0.45 and is the narrowest band in the
   instrument. The gap below is 0.20 wide; the gap above is 0.10. Registering an over-read
   takes roughly twice the excursion in probability that registering an under-read does.
   *This ships with claim 2's zero.*

Then three that are not instances of the pattern:

4. **Our own registered check P5 does not measure what it names.** It requires the modal answer
   constant across `k`, but in the C group `b_pos` is pinned while the correct level varies, so
   a configuration tracking the target fails and one parked at the blind point passes. Our most
   silence-blind configuration returns a perfectly constant row (`anchor` C row 3/3/3, against
   sol-none 0/1/1). This is why Table 2 reports two readings.
5. **Our normalised statistic `s` is span-dependent and, in the cells that carry claim 2, it
   is degenerate.** Spans run 3,3,3,2,2 across the control sweep and cannot be pooled; retired
   and reported rather than quietly dropped. **G4.5 closed 2026-08-21, and the degeneracy half
   is analytic, not empirical** — it was never going to come from the span dial, because it
   does not live there. With `|A| = 2`, `b_pos ≥ 0.5` always, so the blind belief occupies only
   **2 of the 4 bins** and the falsification test is **always a one-bin discrimination**. This
   was written down as a structural limit before the campaign ran. In the D cells specifically,
   `l_pos = 2` against `l_cor = 1` leaves `INT` structurally empty, so **the 47–0 test itself
   lives on a one-bin span** — the fair symmetry test and the instrument's narrowest limitation
   are the same geometry, which is a fourth instance of the pattern above rather than a separate
   caveat. The companion degeneracy is the same fact from the other end: at `k = 6` both beliefs
   land in level 3 at both `δ`, so those cells carry no information under four bins.
   **State the repair with the limitation:** it follows from `|A| = 2`, an axis dropped
   deliberately and marked for revisit, so this is a scoped limitation rather than an open
   problem, and it seeds §7.
6. `δ > 0` is mechanically *easier* under an ordinal statistic, so it cannot serve as the
   harder test it appears to be. **One-sidedness is a property of the non-enumerated arms, not
   of `δ=0`:** enumeration produces over-reading at `δ=0`, and at stated dropout **6.3%** and
   **14.6%** of draws sit below correct, across all seven configurations under a gate with no
   gap. Say that the gapless gate makes membership bar-sensitive there, unlike the `δ=0` gate.

At 3.5 pages, items 5 and 6 merge into one sentence before anything else moves. **Rev 3
caution:** item 5 grew when G4.5 closed, and its one-bin half is the better half — it is
closed-form, it needs no draws, and it explains why the D cells are both the fair test and the
narrowest instrument. If the merge happens, keep the one-bin sentence and cut the span-pooling
sentence, not the reverse.

### §7 Related work and limitations — 0.25 pages

**Trimming and censoring, first and prominently.** de Punder et al.: `b_pos` **trims**, `q_δ`
**censors**. State that restricted-KL negativity is established there and that our contribution
is the instrument, not that fact. Volunteered, not conceded. *Item 50 requires a re-read of
Pun25 for the vocabulary before this sentence is written — confirm that happened.*

**The knowledge-base vocabulary, one clause, new 2026-08-21.** Closed-world treats missing
facts as false, open-world leaves them unknown (Razniewski et al., *ACM Computing Surveys*
2024). That is the same object de Punder gives us as trimming versus censoring. Having both
vocabularies in one sentence is cheap and makes the positioning look deliberate.

**The fourth concession, new 2026-08-21, narrowed rev 4.** That LLMs mishandle absent evidence
is known (CROWN-QA, AbsenceBench, Eo26). Concede it, then locate the contribution: they ask
whether absence licenses an inference, we ask how far the belief should move.

> **Rev 4, required narrowing.** The old closing clause was *"and only the second needs a
> computed target."* That is true of the three papers it cites and false as a general
> statement, because BayesBench — which we cite two paragraphs earlier — has **closed-form
> Bayesian reference posteriors in two of its four environments**. A referee holding both in
> mind produces our own citation as the counterexample. Narrow it to *only the second requires
> a target computed from the disclosure rule*. That is unattackable, since no one else's
> closed-form posterior conditions on what the transcript withheld, and it names the thing that
> is actually ours instead of claiming ownership of exact computation generally.

**Two sentences** conceding that martingale and Lyapunov treatments of debate belief exist and
that the dynamical frame is not the contribution here.

> **Rev 4, one clause owed on single-round design.** BayesBench's entire methodological
> argument is that single-turn scoring hides the updating process. That is an argument against
> designs like ours, and §7's limitation currently reads as a scope note rather than an answer.
> One clause: the setting is single-round **by choice**, because the channel-set manipulation
> requires the target held fixed. No long defence needed.

**Limitations, one sentence, three clauses:** seven configurations across four model families,
three open-weight and one closed (OpenAI gpt-5.6-sol is closed, frontier-tier); `|A| = 2`;
single-round static setting. **Item 80's "no frontier model" is superseded 2026-08-24: the
roster does contain a closed frontier-tier family.** **Rev 3: `|A| = 2` is now load-bearing rather
than incidental** — it is what forces the one-bin degeneracy in §6, so the two mentions should
be written to point at each other. Per item 80, describe the roster by what it is, never as
"frontier."

> **Rev 4, roster comparison verified and one precision risk.** BayesBench is confirmed at
> **seven instruction-tuned models across two families** — LLaMA 3 at 3B/8B/70B and Qwen 2.5 at
> 3B/7B/14B/32B — and its own limitations section calls for extension to closed-source frontier
> models and additional families, which is the same limitation we carry. The peer-roster
> comparison holds. **The risk is the word "configurations."** Seven configurations is not
> seven models if some are the same weights at different reasoning settings, which ours appear
> to be. Either verify how many distinct models the seven cover, or phrase the comparison so it
> compares configurations to models honestly rather than implying parity of breadth.

**Related-work characterizations typed by Ali** (item 66). Source text and load-bearing facts
for each anchor are in `citation_ledger.md` §§1.4–1.6.

---

## 5. Cut and expand branches

**At 3.5 pages.** §6 loses Table 2 to an appendix and becomes prose; blind spots 5 and 6 merge.
Figure 1 goes. §3's band-gap paragraph shortens to one sentence. §7 drops to three sentences.
**Nothing in §2 moves** — the framework is the contribution.

> **Rev 4 reality check.** The 2026-08-22 compile of the drafted §2 plus strawman prose ran to
> roughly **7.5 pages of body against a 4-page limit**. This cut branch was written for a
> half-page overrun and does not scale to that. Executing every item above recovers about 1.7
> pages and still leaves roughly 30% of the prose in every section to cut. **Before any more
> drafting, confirm whether EIML3 permits an appendix or supplementary material.** If it does,
> Table 2, the Lemma 1 proof, blind spots 4–6, and the band-gap paragraph move out and the
> problem largely dissolves. If it does not, the remaining sections are a compression task with
> a hard line target, not a drafting task, and should be given to the editing agent as such.

**At 6 pages.** The three-way decomposition returns to §2, with `W̄` defined at `δ = 0` and its
emptiness stated as a design consequence. The mixedness sweeps get a 0.4-page subsection as a
third experiment. §7 expands to a proper related-work section. **First new analysis to enter:**
the `eps`-against-`π_pos` test of Imran et al.'s evidence-strength prediction (G4.8).

> **Rev 4 caution on G4.8.** Their axis is the **surprisingness of the evidence string in token
> space**; our `eps` is the **informativeness of the silences in nats**. Those can move together
> but they are not the same construct, and the EC paper needs an argument that they correspond
> before the test means anything.

---

## 6. What this outline drops from the 2026-08-13 version

Proposition 1 and the three-way reading (D1) · Proposition 2 as a numbered result (D2) · all
`b^t` notation (D3) · the meridian time-constant result (D4) · normalised `s` as the headline
statistic · the old Figure 2 · the old Figure 3 · the frontier-model boundary check, never run ·
the `|A| ∈ {2,3,4}` sweep, never run · both old cut branches · **the cross-regime contrast
(item 32)**.

## 7. Open items this outline does not settle

- **Figure 2 panel statistic.** §5's panel is specced on `s1`; blind-point occupancy may read
  better. Decide when the figure is drawn.
- **Table 1 layout risk**, per the flag in §2.
- **Title**, revisited at item 86.
- **Whether §6 sits in contributions or below them.** Currently written as a contribution.
- **§4's headline.** §5's was settled 2026-08-21 (rising interior mass); §4's defaults to the
  D-cell tallies but the prior-crossing result is the stronger claim and may deserve it.
  **Rev 3 note:** the `b_pos`-anchoring result now has two independent supports — prior-crossing
  and the level split — which strengthens the case for giving it the headline over the tallies.
  **Rev 4 note:** `main.tex` currently renders the anchoring paragraph first, which introduces
  "of the 47 displaced draws" one paragraph **before** the 47–0 result exists. Whichever
  ordering wins, the tally has to be introduced before it is referenced.
- **Whether EIML3 permits an appendix.** New rev 4, and now the highest-value unknown in the
  document, because it determines whether the next six days are drafting or compression. See
  the cut-branch note in §5.
- ~~Whether W1's gates can be described as pre-committed (G1.5)~~ — **settled 2026-08-21.**
  Closed by writing `PROVENANCE.md` and generalising §6's ordering concession to cover every
  artifact rather than the stimulus sha alone. The missing plan file was **deliberately not
  reconstructed**; writing it now and presenting it as a pre-commitment would be backdating.
  The wording rule this imposes is recorded in §6 above and is binding on §3, §5, and §6.
