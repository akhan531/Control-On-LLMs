# Claims-to-evidence table

**Checklist item 24 · built 2026-08-21 · revised five times**
Rev 1 against `s3_ladder_summary.py`; rev 2 against `v2_gates.json`, `silence_v2_spec.md` §10,
`silence_v2_model.py`, and `s3_dial_summary.py`; rev 3 against the four literature anchors
(items 35–39) and the §5-filter sweep (items 30–33); **rev 4, 2026-08-21, against the item 40
pipeline re-run and the item 41 draw census** (`s4_dcell_split.py`, `s6_draw_census.py`,
`w1_analyze.py`, `w1_addendum_lowside.py`).
Section references resolve against `eiml_paper_outline.md`.

**Rev 5, 2026-08-28 — the δ removal.** The dropout conditions and the entire δ apparatus are
cut from the framework, §1–§5, and the appendix. `q_δ`, Proposition 1 (the pivot), the
`discount` operation, the `banked_viable` 14→9 reduction, and the credulous point are all
retired. `q_0` and `b*` **merge into the single target `b_tar`**; `l_cor` is renamed `l_tar`
(`b_pos`, `l_pos`, `l_obs` unchanged). Lemma 1 reduces to `b_pos ≻ b_tar` and its proof is now
written. The campaign total is the δ=0 subset, **5,808 usable of 5,950 attempted across three
arms** (`2,894 + 959 + 1,955` / `2,940 + 980 + 2,030`); the two δ=0.3 arms (620/630, 623/630)
are removed. **Phased: §6, §7, and the δ=0.3-scoped rows that back them (A7, C9, 4.6, 4.10,
4.12, 4.13, 5.11, 5.12) are NOT yet updated** — the §6/§7 rewrite is deferred, and those rows
still describe live paper claims until it lands. They are marked `[δ PENDING §6/§7]` below.

Every row states its population explicitly, per item 30a. A row whose evidence does not
reach its claim is marked and carried to the gap register in §6.

**Three verdicts, 2026-08-21, governing wording across §4, §5, and §6:**

- **V-24-1 (λ).** λ is retired **as a registered prediction target** — the ARITH_D0
  registration carried no numeric bounds, so no λ value could be scored against it — and
  **retained as a descriptive measured quantity**. Requires a dated amendment in
  `example2README.md` §5 and §11 before drafting.
- **V-24-2 (over-reads once enumerated).** Claim 2 is scoped to the **non-enumerated arms**
  (FULL and PARTIAL_RULED); the over-direction appears once the absences are enumerated
  (ARITH_D0), which is a property of the channel set, not of the instrument.
- **V-24-3 (P5's exclusion clause).** The spec does not say whether a P5 failure excludes
  a configuration's cells from P1–P3 or only flags them. **Both readings are reported,
  strict first.**

**Three wording rules, from items 32 and 33:**

- **R1 — spans and universals, never singletons.** "The closures span 28% to 114%" passes
  §5-filter part 2; "deepseek-high uniquely beats its floor" does not.
- **R2 — the universal is usually hiding behind the fraction.** "rises in 4 of 5" on
  blind-point occupancy is really "falls in none of the five." Lead with the universal.
- **R3 — state the population on every count.**

---

## 1. Population labels

| label | definition |
|---|---|
| **G5** | The five configurations admitted by the frozen competence gate (mean `s1` on FULL, draw level, all 14 cells, < 1.0 bin): sol-high 0.200, sol-none 0.421, glm-high 0.457, deepseek-high 0.752, glm 0.764. Excludes deepseek 1.609 and anchor 1.800. Gap 0.764→1.609, so membership is bar-insensitive. |
| **G3ncl** | The three **non-ceiling** members of G5: sol-none, deepseek-high, glm. sol-high and glm-high are flagged `ceiling` by the registered 0.15-bin guard. |
| **A7** | All seven configurations (pre-gate; the W1 pre-test population, row 1.4). `[δ PENDING §6/§7]` The δ=0.3 ARITH gate that also admits all seven has no gap (deepseek enters at 0.988 against a 1.0 bar), so membership there *is* bar-sensitive; that framing is retired with δ but still backs the deferred §6 rows. |
| **P4** | Pre-registration admission exclusions: anchor loses B1, B3, D1–D3; sol-none loses B1. |
| **C14** | All 14 cells. The ladder analysis runs over C14 minus P4. |
| **C8nc** | The eight non-control cells, A1–A5 and B1–B3. Correct denominator for P1 and P2; the spec's "11" was a miscount. |
| **C9** | `[δ PENDING §6/§7]` The 9 banked-viable cells (A1–A5, B1, C1–C3). The δ=0.3 arms live here. Retired with δ (all 14 cells are valid without dropout); still backs the deferred §6 rows. |
| **CD** | Cells D1–D3, both mirrors. The only cells where `l_tar = 1`, hence the only cells where over-reading is expressible. |
| **NE** | The **non-enumerated arms**: FULL (`{positives, printed negatives}`) and PARTIAL_RULED (`{positives, derivable absences}`). Excludes ARITH_D0. |
| **ERR** | Denominator is *error draws* (nonzero `s2`), not all draws. |

**Pairing note.** The paired per-cell block reports different arm means from the draw-level
block, because pairing restricts to cells present in both arms and averages cell means
rather than draws (deepseek-high FULL: 0.758 paired vs 0.752 draw-level). Never quote one
against the other.

**Dial note.** The RULEDCTRL dial is a **design exhibit only** and supplies no behavioural
evidence. Two of five cells are band-dead; four of five gated configurations are unusable.

**Selection note, new in rev 3 (item 30 part 1).** The competence gate selects on FULL, and
V-24-2 made FULL a claim-carrying arm. Rows 2.1 and 2.2 are therefore **not symmetric
evidence**: PARTIAL_RULED is the result (gate on FULL, outcome on RULED) and FULL is a
control. The 0/300 must never be presented as one homogeneous null.

---

## 2. Claim 1 — the framework is a coordinate system

> Given the channels a transcript exposes, the framework returns the operations an observer
> must perform and the belief it should hold; three different channel sets return the same
> target, and every observed answer therefore has a measurable position.

Lands in §2 and Figure 1. Analytic plus instrument-validity; no behavioural content.

| # | evidence | population | source | status |
|---|---|---|---|---|
| 1.1 | `b_tar` is the correct posterior, and FULL, ARITH_D0, PARTIAL_RULED share it because each conveys the same `N` results (§2 shared-target paragraph; Proposition 1 and the `q_0 = b*` framing retired with δ) | C14 plus the 28 ARITH_D0 stimuli. **No model draws.** | `silence_v2_model.py`, asserted over `Fraction` — exact rational equality, not a tolerance | verified (item 12) |
| 1.2 | Strict ordering `b_pos ≻ b_tar` in log-odds for `p > 1/2` (Lemma 1, reduced from the three-belief δ-ordering; the `q_δ` monotonicity clause is retired with δ) | Analytic. **Requires `\|A\| = 2`.** | closed form | **verified — reduced proof written into §2, 2026-08-28** (was G1.2) |
| 1.3 | `level(b_pos) ≠ level(b_tar)` at build: 3-vs-0 (A, C), 2-vs-0 (B), 2-vs-1 (D), **fourteen for fourteen** (the δ=0.3 nine-for-nine clause retired with δ) | C14 | `silence_v2_model.py` line 217, via `s_endpoints` | **verified 2026-08-21 (item 31)** |
| 1.4 | **Rewritten rev 4.** Response bands were **measured on both sides, and the low side was measured rather than mirrored**. W1 fixed the high-side switch; the low-side addendum re-analysed the same CAL draws because the W4 grid rule's low dead zone `[0.15, 0.35]` had been reflected from the high side rather than measured, and the low side is where `q` sits on every flip cell. Measured edges 0.20 and 0.80, **asymmetry 0.000 at the widest for six of seven configurations on wording B**, which is the wording v2 runs. **anchor is the sole exception** (asymmetry 0.1) and is also the only configuration failing W1's reachability gate, reaching 2 of 4 options on wording A, and the only one whose switch point moves between wordings. It is the configuration the competence gate excludes at 1.609/1.800 and P4 strips of D1–D3. | A7, pre-test (32 stimuli × **3 draws** × 7, 659/672 usable) | `w1_analyze.py`, `w1_addendum_lowside.py`, `results_w1/`; invariance separately asserted in `verify()` | **verified rev 4 (item 40), with one stated limitation** — CAL samples at 0.10 resolution, so the nominal 0.25/0.75 cuts and the alternate 0.20/0.80 edges both fall inside the measured interval. Invariance across the two is a **sampling-resolution fact, not a robustness result**, and must be stated as such. |
| 1.5 | The map is many-to-one on targets: FULL, ARITH_D0, PARTIAL_RULED expose different channels, require the nested sets `{a} ⊂ {c,a} ⊂ {i,c,a}`, and share one target | Design level, C14 | Table 1 | verified by 1.1 |
| 1.6 | Zero floating point anywhere in the model | Design level | `silence_v2_model.py` | verified |
| 1.7 | **Retired with δ (2026-08-28).** The `banked_viable` 14→9 reduction was a δ=0.3 viability filter (B2/B3 put `q_0.3` in the 0.20–0.40 gap; D1–D3 in the 0.45–0.55 gap). With δ gone, **all 14 cells are valid** and §3 no longer drops any. The band gaps themselves stay load-bearing (every cell places `b_pos` and `b_tar` inside a band; the 0.45–0.55 gap straddles the prior, row 2.6). | C14 | `banked_viable` at `silence_v2_model.py:137` (historical) | superseded |
| 1.8 | **Retired with δ (2026-08-28).** The stricter-than-item-31 `banked_viable` criterion applied only to cells carrying the δ=0.3 arms (`level(q_0.3)` distinct from both `level(b_pos)` and `level(b_tar)`); moot with no dropout rate. | C14 | same (historical) | superseded |

**Latent footgun, not a current defect.** `level()` extrapolates past the measured bands
while `in_band()` is strict, so any future arm calling `level()` without the viability check
would silently score against an unmeasured band.

---

## 3. Claim 2 — where absences are not enumerated, under-weighting is the only direction of error

> Among gated configurations, in the two conditions that do not enumerate the absences,
> under-weighting is the only direction of error observed; the error anchors on `b_pos`
> rather than on the prior; and the over-direction reported in the literature is expressible
> on this instrument but is not recovered in these conditions.

Lands in §4 and Figure 2(a).

| # | evidence | population | source | status |
|---|---|---|---|---|
| 2.1 | **The result.** D-cell two-sided tally, PARTIAL_RULED: **47–0** toward under-weighting. At the **pre-registered unit of analysis** (the cell, per D3), **8 of 15 config-by-cell units displaced toward under-weighting, 0 toward over, two-sided exact sign test p = 0.008**; the remaining 7 units carry no displaced mass and are undefined rather than failed. | G5 × CD × PARTIAL_RULED. **150 attempted, 150 usable, zero failures** — the denominator is attempted draws. Gate is on FULL, outcome on RULED, so this arm is unselected. | `s4_dcell_split.py`, `gate_and_recount.py`, `s3_location_summary.py` | verified; **draw counts reproduce exactly on re-run (item 40)** |
| 2.2 | **The control.** D-cell tally, FULL: **9–0**. At the pre-registered unit, **5 of 15 units displaced, 0 over, p = 0.063** — the control does **not** reach significance, and does not need to. **The draw-level p ≈ 0.004 is retired**: it is `2 × 0.5^9`, computed at the wrong grain, treating 9 draws from 3 configurations as independent when the frozen spec makes the cell the replicate (see 5.15). | G5 × CD × FULL. **150 attempted, 150 usable, zero failures.** **The gate selects on this arm**, and all five FULL over-reads across the roster come from anchor and deepseek, exactly the two excluded configurations. | `s4_dcell_split.py` | verified — **not independent corroboration**, and **no p-value at draw level** |
| 2.3 | 0 over-reads in 300 expressible draws across both non-enumerated arms | G5 × CD × NE | D-cell OVER probe, `s3_ladder_summary.py`: 0/30 per gated configuration per arm | verified — supporting clause only |
| 2.4 | Expressibility ledger: `b_tar < b_pos` in every cell, `l_tar = 0` in **11 of 14** cells, so `OVER` has expressible rungs only in D1–D3 and `BEY` only where `l_pos = 2` | C14, design level | `s3_location_summary.py` | verified — **ships with every one-sidedness statement** |
| 2.5 | **CUT from the paper 2026-08-27** — retired as weak: the prior-crossing contrast is structurally near-forced (no level sits at the prior, so every answer falls above or below it), and the per-configuration numerators (sol-none 8/91, glm-high 17/52) undercut the "four of five" framing. Superseded by the occupancy result (row 2.7, promoted to Figure 2b). Original claim kept for the record. Error is `b_pos`-anchored, not prior-anchored: error mass above the prior or exactly at `level(b_pos)`, unreachable by symmetric shrinkage toward π, in **all four configurations with mass in the tested region** (R2) — sol-none 8/91, deepseek-high 50/80, glm **140/140** (108 exactly at `l_pos`), glm-high 17/52. sol-high produces **16 error draws, all at level 1, none above the prior and none at `level(b_pos)`**, so it contributes no mass to the tested region and the universal is four of five (not zero error draws — corrected 2026-08-24 against `s5_prior_crossing.py`). Kill bar of 2 fixed before the test ran. | G5 × ERR × PARTIAL_RULED, **δ=0 only** | `s5_prior_crossing.py` | verified — quote these numerators, never the pooled totals (G2.2) |
| 2.6 | The prior-crossing test is well-defined for a stateable reason: **the uniform prior at 0.5 falls inside the 0.45–0.55 band gap, which straddles it exactly**, so levels 0 and 1 lie wholly below and 2 and 3 wholly above, with no level ambiguous | design level | `BANDS` | verified 2026-08-21 (item 30 part 3) — one clause in §4 ¶5 |
| 2.7 | Blind-point occupancy **falls in none of five** and rises in four: 0→4.6, 12.4→30.6, 6.4→77.1, 0.7→6.4; sol-high 0→0 at ceiling | G5 × C14 × NE, draw level | `s3_location_summary.py` | verified; survives worst-case missingness reassignment 5/5 (B4). **Lead with the universal (R2).** |
| 2.8 | Under-use is graded and count-sensitive, not binary: C-sweep tracked 5/5, 0 of 62 modal FULL cells at `b_pos` | G5 × C-cells × FULL | A4 | verified |
| 2.9 | Alternatives killed with pre-fixed kill conditions: symmetric hedging (A1), directional lean (A2), difficulty drift (B1), answer-high response bias (B2a, B2b at pinned prompt length), missingness (B4), symmetric global conservatism (prior-crossing) | G5 | `s5_va_tests.py`, `s5_vb_tests.py`, `s5_prior_crossing.py` | all dead; A2 marginal for glm (0.455) with a measured 16.7% BLIND lean, reported as secondary behaviour |
| 2.10 | The lean baseline replicates on an independent sweep sharing no cells with the main grid: gated configurations exceed `b_pos` in **2 of 234** RULEDCTRL draws against **16 of 96** for the excluded pair (anchor supplies 14) | G5 vs the excluded pair, RULEDCTRL | `s3_dial_summary.py` ceiling check | verified |
| 2.11 | **Rewritten rev 3.** The literature's over-direction is expressible here but not recovered in these conditions. **BayesBench reports both directions, split by scale** — smaller models stay near the middle, larger models push toward the extremes, with MAE at θ=0.5 rising 8.3 (LLaMA-3B) → 36.7 (Qwen-32B) → 34.2 (LLaMA-70B). **Imran et al. report under-updating universally** (gradient < 1 for every model), on **pre-trained-only** checkpoints via token log-probabilities. | G5 × CD × NE, against two anchors with disjoint populations | rows 2.1–2.4; `[Imr25]`, `[Sam26]` in `citation_ledger.md` §1.5 | **verified — anchors read in full, G2.3 closed.** The claim is now *localization*, not absence: we say where on our grid each direction appears. |
| 2.12 | The over-direction **is** recoverable on this instrument with these models: **2 over-reads in ARITH_D0** (row 4.11). This is the answer to "your roster is too small to produce it." (The δ=0.3 wrong-channel leg, old row 4.10, is retired with δ; the rebuttal stands on the ARITH_D0 over-reads alone.) | G3ncl × CD × ARITH_D0 | row 4.11 | verified — **required in §4**, since BayesBench makes over-updating a large-model behaviour |
| 2.13 | **New rev 4 (G2.4 killed).** The ordinal-extremity account is dead, and dead in the **opposite direction** from the one it predicts. BayesBench's triage result is that the middle two levels collapse outward toward the extremes; on this scale levels 1 and 2 **are** the middle two, so extremity predicts level-1 draws moving to level 0. Observed: level-1 draws move to **level 2**. Of the 47 displaced RULED draws, **44 at level 2 = `level(b_pos)`, 3 at level 3, 0 at level 0** — total endpoint mass **3 of 150 attempted, 2.0%**. In **all three configurations with displaced mass to test** (R2), level-2 draws outnumber level-3: glm-high 5 vs 1, deepseek-high 11 vs 0, glm 28 vs 2. The sol family produces no displaced mass, so the test is undefined there rather than failed. FULL is 9 at level 2, 0 at level 3. | G5 × CD × PARTIAL_RULED and × FULL, 150 attempted per arm | `s4_dcell_split.py`, `results_v2/v2_dcell_split.json` | **verified 2026-08-21 (item 40)** — a fourth killed alternative, belongs in §4 ¶5 beside prior-crossing |

---

## 4. Claim 3 — the identification/interpretation split is a per-model quantity

> How much of a configuration's silence deficit is failure to identify the absences rather
> than failure to interpret them is a quantity the instrument measures per configuration,
> not a constant: enumerating the absences reduces error for every non-ceiling gated
> configuration, by amounts that differ, and it does not repair interpretation.

Lands in §5 and Figure 2(b).

| # | evidence | population | source | status |
|---|---|---|---|---|
| 4.1 | **CUT from the paper body 2026-08-28 (P5 trim; λ retired).** Paired Δ`s1` (ARITH_D0 − PARTIAL_RULED): sol-none **−0.092**, deepseek-high **−0.299**, glm **−0.493** | G3ncl × C14 minus P4 | `s3_ladder_summary.py` | verified |
| 4.2 | **CUT from the paper body 2026-08-28 (P5/P7 trim).** The two ceiling configurations move the other way and trivially: sol-high **+0.043**, glm-high **+0.114** | G5 minus G3ncl | same | verified — consistent with a record-length cost, magnitude inside the 0.15-bin guard |
| 4.3 | **CUT from the paper body 2026-08-28 (λ retired).** Share of the RULED→FULL gap closed, as `1 − λ`: **the closures span 28% to 114%** (sol-none λ 0.72, glm 0.67, deepseek-high −0.14). The top of the range sits past the printed-negatives floor — deepseek-high's ARITH `s1` of 0.721 is below its FULL floor of 0.758. | G3ncl × C14 minus P4 | same | **verified, governed by V-24-1.** Phrased per R1: a span, never "deepseek-high uniquely beats its floor." Never "≈100%." |
| 4.3b | **Ceiling-guard table (Table `tab:ceiling`, §5, added 2026-08-27).** Cell-weighted mean `s1`, cells minus P4. FULL / RULED / (RULED−FULL): sol-none 0.431 / 0.762 / **0.331**; deepseek-high 0.758 / 1.020 / **0.261**; glm 0.764 / 2.243 / **1.479**; sol-high 0.200 / 0.114 / **−0.086**; glm-high 0.457 / 0.486 / **0.029**. The 0.15-bin guard falls in an **empty gap** — smallest non-ceiling gap 0.261 vs largest ceiling 0.029 — and sol-high is negative (better on RULED than FULL). **Cell-weighted (the λ method), not the draw-weighted gate score**, so deepseek-high's FULL reads 0.758 here vs 0.752 at the gate (G5). | G5 × C14 minus P4, cell-weighted | `s3_ladder_summary.py` (same `s1` as λ) | verified 2026-08-27 — FULL 0.758 and ARITH 0.721 for deepseek-high match row 4.3; Δs1 reconciles with 4.1 |
| 4.4 | Blind-point residence collapses for the stuck configurations: `π_pos` falls sol-none 4.6→0.0, deepseek-high 30.6→12.9, glm 77.1→50.0 — **3 of 3 non-ceiling**. glm-high **rises** 6.4→10.7 and must be reported. | G3ncl for the fall; glm-high is in G5 but ceiling-flagged | same | verified |
| 4.5 | **The §5 headline.** Interpretation is not repaired: interior mass **rises in every non-ceiling configuration** — sol-none 65.4→66.9, deepseek-high 28.4→42.4, glm 17.1→27.9. The freed answers land short of target. | G3ncl × C14 minus P4 | same | verified — a universal over the claim population with no fraction to defend |
| 4.6 | `[δ PENDING §6/§7]` **Already CUT from the paper body 2026-08-28 (P6, δ=0.3 null); fully retired with δ.** The same handout repaired no one at δ=0.3: no configuration recovered more than **12.5%** of its deficit, gated ≤ **8.0%**, worst-case missingness bound ≤ 0.20 bins, an interval containing **all seven** configurations. | A7 × C9 × δ=0.3 | `s3_arith_summary.py`, V-E2-4a | verified (historical) |
| 4.7 | The sentence that carries §5-filter part 2: **five of five admitted configurations receive a well-defined verdict** — three numeric positions, two adjudicated `ceiling`. This must appear before the numbers do. | G5 | rows 4.1–4.4 | verified (item 33) |
| 4.8 | Enumeration is read, not shape-matched or line-counted: mimicry cross-tab dies for every gated configuration; per-line effect dies everywhere (−0.89 to +0.17) after a collinearity audit at max \|r\| 0.34 | G5 | V-E2-1, V-E2-3 | verified; deepseek alone is line-counter-consistent and is gate-excluded |
| 4.9 | Robustness: worst-case missingness holds (deepseek-high in [−0.379, −0.229]); mirror split holds for all five non-ceiling gains | G5 | V-E2-4a, V-E2-4b | verified; glm's gain is mirror-asymmetric (−0.04/−0.94), sign-consistent |
| 4.10 | `[δ PENDING §6/§7]` **Retired with δ.** Under a stated noisy channel, enumeration lands models on wrong channels: below-correct mass anchor 0→32.5%, deepseek 7.0→23.8%, glm 0→5.6%; median implied δ̂ splits 0.29–0.34 against 0.70–0.74. **The 32.5% is anchor, gate-excluded; the gated peak is glm at 5.6%.** No longer cited (the row-2.12 leg it fed is retired). | A7 × C9 × δ=0.3 | `s3_arith_summary.py`, V-E2-2 | verified (historical) |
| 4.11 | Wrong-channel over-reads once the absences are enumerated: **2 over-reads in 150 expressible gated draws** in ARITH_D0 (deepseek-high 1/30, glm 1/30) against 0/300 in the non-enumerated arms. The two configurations are exactly the two with the largest repairs. | G3ncl × CD × ARITH_D0 | D-cell OVER probe | verified — the §4-to-§5 bridge |
| 4.12 | `[δ PENDING §6/§7]` **Retired with δ.** The positive control: because the enumerated rung showed the lines are read and used, the δ=0.3 null indicted interpretation rather than inattention. With δ gone, the interpretation-not-repaired point rests on the δ=0 interior-mass result (row 4.5) alone. | G5, A7 (historical) | rows 4.1–4.6 | verified (historical) |
| 4.13 | ~~Cross-regime contrast~~ | — | — | **CUT, not demoted (item 32); now fully retired with δ.** It brushed the δ=0-vs-δ=0.3 seam that no longer exists. Row 4.5 says what §5 needs. |

---

## 5. Claim 4 — the instrument's blind spots, including a failed pre-registration

> The instrument has identifiable limits: the primary pre-registered prediction did not
> hold, one registered contrast was retired, one registered check is defective, our own
> normalised statistic was withdrawn, and two structural quantities are welded by the
> geometry. All are reported as results.

Lands in §6 and Table 2.

### Table 2 as it should read

| item | tier / where registered | outcome |
|---|---|---|
| **P3 (primary)** — gap > 0.5 in ≥ 2 of 3 families | Tier 1, frozen spec, internal timestamp | **Falsified under a strict reading of our P5 exclusion clause (0 of 3); held in 1 of 3 under a loose one.** glm alone clears at 0.821 and glm also fails P5. Both reported, per V-24-3. |
| P1 / P2 — the two halves | Tier 1, same | 1 of 3 each, **in different families**: P1 glm, P2 sol-high. No family carries both halves. |
| Non-control cell bar | Tier 1, **amended** | Spec text says 8 of 11; executed as **6 of 8**. The non-control set is A1–A5 and B1–B3, so "11" was a miscount. Proportion 0.727 → 0.75. |
| ARITH_D0 λ predictions | Tier 2, sha256 `028d9be8…` | Directional, no numeric bounds. Scored as directional. |
| ARITH_D0 ceiling guard | Tier 2, same | Sharp 0.15-bin threshold, scored cleanly. |
| 5/5 cross-regime contrast | **Tier 3, checkpoint-fixed**, absent from the frozen registration | Died at 4/5; gated, 2 of 3. Retired rather than rescued. |

### Evidence rows

| # | evidence | population | source | status |
|---|---|---|---|---|
| 5.1 | P3, the primary: gap > 0.5 required in ≥ 2 of 3 families. Measured sol **0.417**, deepseek **0.405**, glm **0.821**. `pass: false`. | A7 families × C8nc | `v2_gates.json` | verified |
| 5.2 | The spec pre-committed a **three-band** outcome space: ≥2 passes; **0 is falsification**, with the registered consequence that the paper becomes a negative-results report; 1 is neither. | design level | `silence_v2_spec.md` §10 | verified — naming the bands is what makes V-24-3's dual reporting legible |
| 5.3 | P1 held for glm alone, P2 for sol-high alone — **different families**. The family that cleared P3 did so without its high-effort configuration clearing P2, so its gap is blind → less blind, not blind → reads silence. | A7 × C8nc | `v2_gates.json` | verified — the sharpest statement of what the registration returned |
| 5.4 | The 5/5 cross-regime universal was **checkpoint-fixed**, despite `example2README.md` calling it pre-registered; died at 4/5, retired rather than rescued | C9 | V-E2-4c | verified (item 13) |
| 5.5 | Provenance: **both** tiers rest on an internal timestamp for ordering. The sha establishes that the stimuli analysed are the stimuli registered; it does not establish that the registration predates the calls. `arith_d0_prereg.md` was committed three days after collection. | design level | items 0, 13, 60 | verified — narrows item 60. Open question at G4.6. |
| 5.6 | **Blind spot 1: count and weight are anti-correlated by construction.** Pinning the target while raising `N−k` from 4 to 12 forces `p` from 0.90 to 0.56, and the evidence the silences carry falls **5.61 → 1.83 → 0.71 nats**. Tripling the count drops the evidence roughly eightfold. Closed form, no draws. | C14 design level | `s3_dial_summary.py` | verified — the one blind spot a reviewer cannot argue with |
| 5.7 | **Blind spot 2: over-reading is testable only in the weak-evidence corner, and the coupling is forced.** The D cells carry `eps0` of 0.065 / 0.080 / 0.064 against 3.84 for C1 — **fifty times weaker** — and are the only cells where over-reading is expressible. Over-reading needs headroom below `b_tar`, headroom needs `b_tar` high, and `b_tar` high means the silences carried little. | C14 | `silence_v2_model.py` output | **verified 2026-08-21, new** |
| 5.8 | **Blind spot 3: the scale makes over-reads harder to see than under-reads.** In the D cells `b_tar` sits at 0.440 / 0.421 / 0.440, inside band 1, which spans 0.40–0.45 and is the narrowest band in the instrument. The gap below is **0.20 wide**; the gap above is **0.10**. Registering an over-read requires roughly twice the excursion in probability. | CD | `BANDS` plus the cell table | **verified 2026-08-21, new.** Must ship with claim 2's zero. |
| 5.9 | **Blind spot 4: P5 does not measure what it names.** It requires the modal answer constant across `k`, but in the C group `b_pos` is pinned while `l_tar` varies, so a tracking configuration fails and one parked at the blind point passes. anchor's C row is 3/3/3, perfectly constant and maximally silence-blind; sol-none's is 0/1/1. | C-group cells, A7 | `v2_gates.json` P5; concordance block | verified. **P5's 2-of-7 must not be reported as "five configurations respond to record length."** |
| 5.10 | **Blind spot 5: our normalised `s` is span-dependent** — spans run 3,3,3,2,2 across the control sweep and the script refuses to pool rows. Retired, and reported rather than quietly dropped. | C14 | `s3_dial_summary.py` | span-dependence verified; **the one-bin degeneracy is a separate claim needing its own exhibit** — G4.5 |
| 5.11 | `[δ PENDING §6/§7]` Blind spot (§6 Non-instance 6): δ > 0 is mechanically *easier* under an ordinal statistic, so it cannot serve as the harder test it appears to be. **Deletes with δ when §6/§7 are rewritten** (the objection it answers vanishes once there is no δ>0 regime). | design level | spec §8 / D26 | verified — pending §6 removal |
| 5.12 | `[δ PENDING §6/§7]` Blind spot: one-sidedness is a property of the non-enumerated arms. The δ=0 half survives (enumeration produces over-reading, row 4.11); **the stated-dropout half — 39/620 (6.3%) and 91/623 (14.6%) below correct — deletes with δ.** | Over-reads: G3ncl × CD × ARITH_D0 (survives). Dropout: **A7** × C9 × δ=0.3 (pending removal). | row 4.11; §6 | verified — pending §6 removal |
| 5.13 | Blind spot: over-reading is structurally inexpressible outside D1–D3, so no "zero over-reads" claim can be pooled across the grid | C14 | row 2.4 | verified |
| 5.14 | Blind spot: the RULEDCTRL dial has **two band-dead cells of five** and four of five gated configurations contribute nothing usable — sol-high and glm-high flat 10/0/0/0, deepseek-high lost **15 of 50 slots** to failures | RULEDCTRL | `s3_dial_summary.py` | verified — design exhibit only |
| 5.15 | **Resolved rev 4, not a blind spot.** Draws within a cell share seeds and mirrors, so draw-level sign counts carry within-cell correlation. The frozen spec already fixes the remedy: the **cell is the unit of analysis** (D3), mirrors and draws pooled to one modal level, cells as replicates. Every sign test is now computed at that grain (rows 2.1, 2.2); draw counts are reported as descriptive tallies with attempted denominators and carry **no** p-value. | all | `silence_v2_analyze.py` module docstring; `s4_dcell_split.py` | verified — **this is what item 78's "no independence assumption" sentence rests on** |
| 5.16 | Blind spot: answers respond to record length within ARITH_D0 for sol-none, glm, and deepseek | G5 | V-E2-4d | verified, **but inherits 5.9's caveat** — the constancy criterion is confounded in the C group and clean in the D group. Say which half is which. |

**The §6 pattern, worth naming rather than listing.** Blind spots 1, 2, and 3 are the same
shape: two properties you would want to vary independently, fused by the geometry. Count
against weight; evidence strength against over-read expressibility; over-read visibility
against under-read visibility. Naming the pattern is a better §6 than three unrelated
caveats, and it costs no extra space.

---

## 6. Gap register

### Closed

**2026-08-28:** §5 trimmed to the identification/interpretation **dichotomy**
(Figure 3, rows 4.4/4.5). **Cut from the paper body:** P5 (the λ localization
split), P6 (the δ=0.3 null), and P7 (the record-length rebuttal). λ is fully
retired from the body — a fit descriptive quantity with no robustness evidence
and no numeric registration; the §6 registration table keeps the honest record
("directional, no numeric bounds"). The contributions bullet now claims only the
dichotomy, not a "per-configuration quantity." **Now unsurfaced in the paper:**
rows 4.1 (paired Δs1), 4.2 (ceiling s1 moves), 4.3 (λ closures 28–114%), 4.6
(δ=0.3 null; its bounds were driven by the two gate-excluded configs, deepseek
and anchor). **Still live:** 4.4 (residence, Fig 3a), 4.5 (interior, Fig 3b,
D-excluded), 4.11 (over-reading, P8), 4.3b (ceiling-guard table, Table 2).

**2026-08-27:** Row 2.5 (`b_pos`-anchored / prior-crossing claim) **cut from the paper**,
retired as weak — the contrast is structurally near-forced and the per-configuration
numerators (8/91, 17/52) undercut the universal; superseded by the occupancy result
(row 2.7, promoted to Figure 2b). Rows 2.6 (band-gap fact, kept in the §4 body) and 2.7
(occupancy) stay live. The four-way mass split moved from Figure 2b to a standalone
Figure 3 in §5 (`fig:mass`).

**2026-08-21 rev 2:** G3.1 (V-24-1) · G3.2 (sol-none's −0.092 reproduced) · G3.3
(occupancy narrowed to 3 of 3 non-ceiling) · G2.5 (V-24-2, promoted to row 4.11) ·
G4.1 (item 29a confirmed at 5.6) · G4.3 · G4.4 · the P5 ambiguity (V-24-3).

**2026-08-21 rev 3:** G3.4 (cross-regime cut, not restated) · G2.3 (both anchors read in
full; row 2.11 rewritten) · G3.5 (row 4.5 makes the two senses of "deficit" legible).

**2026-08-21 rev 4, items 40 and 41:** **G2.4** (ordinal extremity killed, row 2.13) ·
**G1.4** (W1 and its low-side addendum located and run, row 1.4 rewritten and upgraded) ·
**G4.5** (one-bin degeneracy exhibit found, and it is analytic — see below) · **5.15**
(resolved by recomputing every sign test at the pre-registered unit) · **G1.5**, closed by
writing the narrowing rather than by finding the artifact — see immediately below.

**G1.5, and why it is project-wide rather than a W1 gap.** `w1_analyze.py` cites a decision
rule pre-committed in `w1_pretest_plan.md` §5. **That file is not in the repository and has
never appeared in its history.** Chasing it turned up the general fact: **no artifact in this
project has externally verifiable pre-commitment ordering.** Three checkable reasons. (i) The
first commit touching experimental code is **2026-08-20**, after the W1 run on 08-14 and the
v2 campaign on 08-15, so git cannot order anything against anything. (ii) Draw records carry
`config`, `slug`, `seed`, `stimulus_id`, and outcome fields but **no wall-clock field**, so
there is no internal clock to check against. (iii) mtimes are weak and **one is actively
unfavourable**: `silence_v2_spec.md`, where P1–P5 are registered, has mtime **2026-08-16
03:25**, about five hours *after* `results_v2/v2_results_live.json` at **2026-08-15 22:13**.
The registration file was edited after the campaign it registers, and nothing shows what
changed.

**Closed by writing `PROVENANCE.md`** (repo root, dated 2026-08-21), which states what the
record establishes — content integrity via sha and `verify()`, byte-identical regeneration of
four artifacts, arm arithmetic closing exactly, decision rules visible as executable code —
and what it does not, namely ordering. **The plan file was deliberately not reconstructed:** a
file written now and presented as a pre-commitment would be backdating. The only corroboration
for W1 is weak and labelled as such — mtimes place `w1_analyze.py` at 21:18, results at 21:24,
addendum at 21:39 on 08-14, consistent with the docstring.

**Binding consequence for drafting.** "Frozen," "pre-registered," and "pre-committed" are
**never used unqualified** in the paper or the READMEs. Table 2's tier labels say *where*
something was registered, not that ordering was verified; §6 states the ordering concession in
its own text and it covers **the spec, the stimuli, and the band pre-test together**, not the
stimulus sha alone. Kill conditions are described as fixed at a checkpoint before their test
ran, which is a **process claim**, not a provenance guarantee, and is labelled as one.

**G4.5, how it closed.** The exhibit is not empirical and was never going to come from the
dial, because the degeneracy does not live in the span dial at all. `silence_probe_v2_open_issues.md`
D4 states it as a structural limit, written before the campaign ran: with `m = 2`,
`b_pos ≥ 0.5` always, so the blind belief occupies only **2 of the 4 bins** and the
falsification test is **always a one-bin discrimination**. The same passage records the
companion degeneracy: at k=6 both beliefs land in level 3, so those cells
carry no information under four bins, which is why Block 1's k values could not be reused.
Blind spot 5.10's two halves are therefore evidenced from opposite directions — span
dependence empirically by the dial (5.61 → 1.83 → 0.71 nats), one-bin degeneracy
analytically by `m = 2`. Neither needs a draw. **The fix is already scoped:** D5 dropped the
alphabet-size axis deliberately and marked it "revisit after Block 1 is built and
validated," so §6 states a limitation whose repair is a named axis rather than an open
problem, and it seeds §7. **Today's D-cell result is an instance of it:** D cells run
`l_pos = 2` against `l_tar = 1`, span 1, so `INT` is structurally empty and the 47–0 test
lives entirely on a one-bin discrimination. `verify()` guards a zero ordinal-`s` denominator
but not a one-bin one (item 12's footgun), which is the same fact from the code side.

### HIGH

**G2.1 — the 176 denominator is ungated and still in the record.**
`example1README.md` §2 and §8 claim 1 cite "0 overshoots in 176 expressible RULED draws;
1 in FULL, from a gate-excluded config." 176 reconstructs as 210 D-cell slots minus 30 for
anchor's P4 exclusion minus 4 failures — an all-seven pool. Correct figures are 150 / 150 /
300, **and per the selection note the two arms must not be pooled at all.**

**G2.2 — Moot (2026-08-28, δ removal).** Row 2.5 (prior-crossing) is cut and the δ=0.3 arm
is gone, so the old "27 / 79 / 197 / 22" cross-δ pool (PARTIAL_RULED + RULED_D30) no longer
exists to be miscounted.

**G2.6 — NEW rev 4. The record's failure characterization is wrong in three ways.**
`example1README.md` §3 says all failures are PARSE in the deepseek family. Across the full
record that is wrong on **family** (glm-high contributes 12, five of them in the banked arm
Example 2 reports on), on **mode** (`TRUNCATED` does not exist in the main campaign but is
the majority mode elsewhere — 8 of 10 banked, 47 of 75 sweep — a `max_tokens` exhaustion
signature, a different phenomenon from a decoding pathology), and on **arm** (the sentence is
true of the main campaign only and is stated as a property of the work). Correct
distribution across all six arms: deepseek 100, deepseek-high 60, glm-high 12, and **zero for
sol-none, sol-high, glm, and anchor**. That four-of-seven zero is worth stating, since a
reader assumes it is being hidden otherwise. Failed records carry `failure`, `detail`, `raw`,
and `slug`; the raw text shows tokenizer artifacts, and `note` records "off-menu; retry
discarded per D16," so there is a frozen retry policy behind the count. **`slug` also carries
full model identity, which is item 80's answer sitting in the frozen data.**

**G2.7 — NEW rev 4. Sweep attrition is differential, and the exhibit that uses it is clean
anyway.** `results_sweep` runs 3.7% attrition against the main campaign's 1.6%, asymmetric by
condition (30 FULL, 45 RULED), and concentrated in six `FULLCTRL` cells, F06–F11, which take
42 of 75 failures. Row 2.10's lean-baseline denominators were checked against this and are
**clear**: RULEDCTRL splits exactly 234 gated usable and 96 excluded usable, a different
sweep and a different arm from the F-block. **Retained as a limitation to state, not a defect
to fix.**

### MEDIUM

**G4.7 — Moot (2026-08-28, δ removal).** Zhang et al., *Large Language Models as Discounted
Bayesian Filters* (arXiv:2512.18489), collided with Table 1's fourth operation (`discount`)
and `q_δ`. Both are gone, so there is no vocabulary collision and the read is no longer
blocking §2.

### LOW

**G4.6** — was the sha256 published anywhere external before the calls, or only written into
the local file? Decides whether the word "published" can be used at all.

**G4.2** — `[δ PENDING §6/§7]` row 5.12's dropout denominators (620, 623) are all-seven under
a gapless gate. Deletes with the stated-dropout half of 5.12 in the §6 rewrite.

**G1.2 — Closed 2026-08-28.** The reduced Lemma 1 (`b_pos ≻ b_tar`) and its proof, carrying
the `|A| = 2` precondition, are now written into §2.

**G3.6** — V-E2-4d's count-sensitivity caveat applies to all three configurations carrying
claim 3's cell-level numbers, and inherits 5.9's C-group confound. Travels with row 4.1, and
should say the D-group half is clean.

**G4.8 — deferred, not open.** Imran et al. report the update gradient is inversely
proportional to the negative evidence log-likelihood, so under-updating worsens as evidence
strengthens. That is a prediction about our grid, where `eps` ranges over fifty-fold. Testing
it needs `π_pos` rather than `s1`, since `s1` is a bin distance and higher `eps` mechanically
means more bins of separation. **EC paper or 6-page branch, not EIML.**

---

## 7. What this hands to item 69

**Four claims, populations named on every row.** Claim 2 is scoped to the non-enumerated
arms and is now a *localization* claim rather than an absence claim. Claim 4 says the primary
prediction "did not hold," reported under both readings.

**Numbers that must never appear:** 962 · 176 · "5/5" occupancy · pooled 27/79/197/22 ·
"≈100%" gap closure · "8 of 11 non-control cells" · "five configurations respond to record
length" · "4 of 5" cross-regime · **206** · **p ≈ 0.004** · **"all failures are PARSE in the
deepseek family"** · **"~7,050", 7,051, and 7,210** as campaign totals (superseded by the
δ=0 subset 5,808 / 5,950) · **"all seven configurations agreed"** on the W1 bands.

**Five added rev 4, with what each one actually is:**
- **206** — `gate_and_recount.py`'s D-cell denominator. Its `draw_errors()` takes no P4
  argument and applies no gate, so it is an all-seven, P4-inclusive pool: 150 gated + 26
  deepseek + 30 anchor + 4 failures = 210 slots. Same defect as 176, one layer down. **Correct
  figures are 150 attempted and 150 usable, per arm, gated five.**
- **p ≈ 0.004** — the draw-level sign test. Retired; see rows 2.2 and 5.15.
- **the failure sentence** — wrong on family, mode, and arm. See G2.6.
- **The campaign total** — superseded by δ removal. Now the **δ=0 subset: 5,808 usable of
  5,950 attempted across three arms** (2,894 + 959 + 1,955 usable / 2,940 + 980 + 2,030
  attempted); the two δ=0.3 arms (620/630, 623/630) are removed. The old **7,051 / 7,210**
  (five arms) and "~7,050" are banned. **W1's 659 of 672 sits outside that total**, on a
  different stimulus set and at **3 draws per stimulus, not 5**. Any sentence saying the work
  uses five draws throughout must carve out the pre-test.
- **"all seven configurations agreed"** on W1 — six of seven, anchor the exception. See
  row 1.4.

**Banned language, added rev 4.** "Frozen," "pre-registered," and "pre-committed" never
appear unqualified. See G1.5 and `PROVENANCE.md`. Also never assert that the registration
predates the calls: the record cannot support it for **any** artifact, including
`silence_v2_spec.md`, whose only timestamp postdates its own campaign.

**One number collision, same species as λ.** Row 2.10 reads "2 of 234 gated against **16** of
96 excluded," where 16 counts BEY escapes among the excluded pair. The RULEDCTRL arm also has
**16 gated failures**. Two different 16s, one line apart, in the same table. Disambiguate at
first use or drop one.

**Eight edits to the record, before drafting.** Four were owed before today; four are new.
1. The V-24-1 amendment into `example2README.md` §5 and §11, dated.
2. The occupancy restatement (3 of 3 non-ceiling, glm-high rises) into §6 and §8 claim 1.
3. `example1README.md` §2's BayesBench characterization — it says over-confidence; the paper
   reports both directions split by scale. `citation_ledger.md` §1.5 has the correct text.
4. Item 30b's stale §9 sentence in `example2README.md`, same pass as 1 and 2.
5. **NEW.** `example1README.md` §6 and outline §4 ¶4: strike `p ≈ 0.004`, substitute the
   cell-level tests (RULED p = 0.008, FULL p = 0.063) and lead with the universal.
6. **NEW.** `example1README.md` §3's failure sentence, per G2.6.
7. **NEW.** `example1README.md` §3's band sentence, per row 1.4, including the
   sampling-resolution limitation and the anchor exception.
8. **NEW.** Wherever "~7,050" appears: five arms, 7,051 of 7,210, W1 stated separately at 3
   draws.

**Three new assets.**
Row 4.11 gives §4 and §5 one shared spine: the direction of error flips exactly when the
channel set gains enumerated absences.
Row 5.6 turns blind spot 1 from a hedge into a closed-form impossibility result.
Rows 5.6–5.8 form a nameable pattern rather than three caveats.

**Nothing outstanding but one read (G4.7, Zhang et al. on discounted Bayesian filters).**
The script run closed as row 2.13, the exhibit closed analytically at G4.5, and the pipeline
reproduces: `v2_gates.json`, `v2_banked_gates.json`, `w1_gates_live.json`, and
`w1_lowside.json` all regenerate byte-identically under `git diff`, and every arm's
config × stimulus × draw product closes exactly against its record count with no ragged arm
and no header disagreeing with its own records (item 41).

**Two new assets from rev 4.**
Row 2.13 is a fourth killed alternative that costs one clause and answers the strongest
anchor-derived objection to claim 2.
**anchor is the exception in four independent places** — W1 reachability, W1 wording
stability, W1 low-high asymmetry, and the competence gate — plus P4 on D1–D3. Four
instrument checks and one behavioural gate select the same configuration. That is a
consistency result, not five separate caveats, and it is one sentence in §3.
