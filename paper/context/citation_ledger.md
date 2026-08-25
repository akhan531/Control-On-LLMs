# Citation Ledger — Strategic Timing in Multi-Agent LLM Debate

**Built:** 2026-08-07, from the Task 2.2 Undermind pass (5 queries).
**Revised:** 2026-08-21, checklist items 35–39. Four EIML anchors read in full and verified; three owed citations added at §1.6.
**Purpose:** every source the Undermind pass surfaced that has a job to do in the paper, with the job named. This is a working bibliography, not the Related Work Check log. Related Work Check records what the *pass* found; this file records what the *paper* must cite and why.

**Dual use, noted 2026-08-21.** This file was built for the strategic-timing paper and is now also the working bibliography for the EIML3 workshop paper. §1.4 and §1.5 are EIML-facing; Tiers 1.1–1.3 remain strategic-timing. Where a source serves both, the entry says so.

## How to read the status column

- **VERIFIED** — full bibliographic detail confirmed against a primary source this session. Safe to cite as written.
- **PARTIAL** — arXiv id or venue known, authors and exact title not confirmed. Resolve before the bibliography is finalized.
- **UNRESOLVED** — Undermind returned a workspace-local bracket key and a title only. Those keys are meaningless outside the Undermind workspace and will be meaningless here in a month. Must be resolved manually.

**Added 2026-08-21:** where bibliographic detail was taken from the reference list of a paper we did read, rather than from the source itself, the entry says **PARTIAL (secondary bib)**. That is enough to find the paper and not enough to characterize its claim.

Nothing in this file should be pasted into a bibliography at UNRESOLVED status. An invented author list is worse than a missing citation.

---

# TIER 1 — Load-bearing. The paper is weaker or wrong without these.

## 1.1 The restricted-KL negativity concession

These two establish that a KL integral restricted to a sub-event can be negative and is not a divergence. That fact is currently written into §8.9 of Convergence_Theorem.md as though it were ours. It is not, and it has been known since at least 2023. Conceding it in our own sentence, with these citations attached, converts an exposed flank into evidence of command of the literature.

**[Pun25] de Punder, R., Diks, C. G. H., Laeven, R. J. A., and van Dijk, D. J. C. "Localizing Strictly Proper Scoring Rules." *Journal of the American Statistical Association*, January 2026. DOI 10.1080/01621459.2025.2576189. Earlier as Tinbergen Institute Discussion Paper 23-084/III (2023).**
Status: **VERIFIED**
Why we cite it: this is the paper that names our mechanism. It gives the identity relating the restricted integral to the conditional KL, and its central message is that *trimming* a region without accounting for the omitted mass destroys the divergence property, whereas *censoring* (folding the omitted mass back as an atom) restores it. Our silence-blind observer trims where the correct update censors, and the omitted mass is exactly the silence probability. Adopt the trimming-versus-censoring vocabulary. It is a sharper one-line account of the mechanism than "the tracker fails to condition on silence," and it is already in the literature so a referee cannot call it invented.
Second use, Phase 3: their censoring correction is the obvious mechanism a referee will propose against us. The answer is that applying it requires knowing the omitted mass, which requires knowing and trusting the disclosure rule, which is exactly what a strategic agent controls. Have that ready.
**EIML use, added 2026-08-21:** this is also §7's opening move for the workshop paper, and item 50 requires a re-read for the vocabulary before that paragraph is written.

**[Pun24] de Punder, R., Dimitriadis, T., and Lange, R.-J. "Expected Kullback-Leibler-Based Characterizations of Score-Driven Updates." arXiv:2408.02391 (v1 Aug 2024, revised Mar 2026).**
Status: **VERIFIED**
Why we cite it: defines the trimmed local quantity explicitly, shows it can be negative and is not a proper divergence, and makes the point that a local update can appear to improve the trimmed quantity while moving away from the true density. That last clause is our positive drift in a filtering setting. Cite alongside Pun25 in the same concession sentence.

*Note: same first author, and his UvA dissertation is titled "Local divergences." This is an active group working directly on our mathematical object in a neighboring field. Add to the standing watchlist.*

**[Gke20] "Theoretical Aspects on Measures of Directed Information with Simulations."**
Status: **UNRESOLVED** — authors, venue, year all unknown. Undermind reports a concrete discrete counterexample with a weighted KL evaluating to −0.11342 under weights (1,1,4), plus a corrected weighted KL restoring non-negativity.
Why we cite it: the cleanest explicit numerical counterexample to "restricted KL is non-negative." Optional if Pun24 and Pun25 carry the concession, but a numerical witness is rhetorically useful in a footnote.

**[Avl16] "On Local Divergences Between Two Probability Measures."**
Status: **UNRESOLVED**
Why we cite it: background terminology for local Csiszár φ-divergences over a region of common support. Lowest priority in this group. Include only if the related-work paragraph has room.

## 1.2 The group-size concession

These establish that adding informed senders can hurt aggregation. We must not claim that as novel. **But the mechanism is opposite to ours and that contrast is a differentiator, not a weakness.** In all of these, damage comes from *less* evidence reaching the record: disclosure is costly, agents free-ride or crowd each other out. In §8.9 disclosure is free, every agent whose condition fires discloses, and damage grows *because more evidence is disclosed*. Write the contrast explicitly.

**[Kar26] "Multi-Sender Disclosure with Costs."**
Status: **UNRESOLVED** — dated 2026, unclear whether published or preprint. Resolve this one first; a 2026 econ paper on multi-sender disclosure is also a watchlist candidate.
Why we cite it: senders hold hard evidence and choose disclosure or silence; with a positive disclosure cost, disclosures are strategic substitutes and the decision maker can be strictly worse off with two senders than with one, even under opposing biases. The closest existing collision on the *sign* of the group-size effect. It has a many-sender extension but its welfare counterexample is one-versus-two, with no Θ(N) growth and no critical group size.

**[Osb19] "Information Aggregation with Costly Reporting."**
Status: **UNRESOLVED** — Osborne is a plausible author guess and should not be recorded as fact until checked.
Why we cite it: the closest structural precedent. Fixed independent signals, costly reporting, and for large n the equilibrium becomes one-sided, with correct-decision probability approaching 1 in one state and 1−c in the other. Its Proposition 2 contains a finite N threshold for the *shape* of equilibrium, but no monotone accuracy decrease and no guarantee that every n above a threshold is worse than a smaller group.

**[Hof20] "Persuasion Through Selective Disclosure."**
Status: **UNRESOLVED** — a Bocconi IRIS record exists (iris.unibocconi.it).
Why we cite it: proves a literal finite threshold M₀ above which all symmetric competing senders selectively disclose. A genuine group-size threshold in selective disclosure, but the setting is competing offers with receiver-specific preferences, not collective estimation of a common truth, and selective disclosure can even improve receiver welfare there. Cite as the nearest threshold precedent and distinguish on the objective.

**[Che24b] "Learning from Strategic Sources." EC 2024.**
Status: **UNRESOLVED** — venue reported as EC 2024.
Why we cite it: **downgraded from threat to positioning cite.** Q2 cleared it. Its potentially-negative object is a difference of two nonnegative KLs plus Chernoff information, not a restricted integral, and it has no silence-conditioning mechanism. Cite it in the threshold neighborhood alongside Kar26 and Osb19 so a referee sees we read it, and state the distinction in half a sentence.

## 1.3 The martingale-of-debate concession

Lyapunov and martingale treatments of debate belief dynamics are no longer unclaimed. Do not present the dynamical framework as the contribution; present it as the frame the group-size result lives inside. This ordering is independently required by the DynaFront venue-fit argument in Task 2.1g.

**[Cho25] Choi, Hyeong Kyu, Zhu, Xiaojin, and Li, Sharon. "Debate or Vote: Which Yields Better Decisions in Multi-Agent Large Language Models?" NeurIPS 2025 (Spotlight). arXiv:2508.17536.**
Status: **PARTIAL** — arXiv id and author list from the Undermind pass; confirm the volume number and Spotlight designation before citing.
Why we cite it: proves debate belief is a martingale under a Dirichlet-categorical model with homogeneous full-information updating, so expected correctness is flat across rounds. This id has been owed across three related-work passes and is now closed. Our gap is exactly its assumption: no private evidence, no silence, no strategic agent, no KL Lyapunov function.

**[Zhu26] Confidence-weighted debate as a strict submartingale.**
Status: **UNRESOLVED** — highest priority to resolve in this group.
Why we cite it: **the closest framing collision to Proposition 1b.** Gets a strict submartingale from a positive confidence-correctness correlation under cooperative disclosure. We get a supermartingale from Bayesian structure and then break it with strategic silence. Different assumption, opposite direction, different cause. One sentence in related work, but it has to be there. **Read before writing.**

**[Liu26b] Peer-prediction Brier potential plus multiplicative weighting, positive drift toward truth.**
Status: **UNRESOLVED**
Why we cite it: **this is a Phase 3 / EC gate item, not a workshop item.** A peer-prediction potential function generating provable drift toward truth is structurally the mechanism we intend to build. It does not threaten the workshop paper. It may move the EC target. Needs a dedicated read before Phase 3 opens; flagged here so it is not discovered in October.

**[Jal25] Strategic persuaders choosing when to reveal fixed positions; DeGroot-type belief dynamics converging to different limits without consensus.**
Status: **UNRESOLVED**
Why we cite it: closest thing to our stranding result outside our own model. **Check one specific thing:** if the non-consensus limits are driven by receivers failing to account for the persuader's revelation strategy, that is our stranding mechanism in DeGroot clothing and this becomes a must-cite rather than an adjacent.

## 1.4 The silence-inference empirical claim

These are the papers that make the Probe P finding defensible. Two of them pre-empt the objection we would otherwise eat, which is "you prompted it wrong."

**[CROWN-QA] Min, Byoungjae; Edemacu, Kennedy; Cho, Sae-Hong; Choi, Yoonhyuk; Jang, Beakcheol; and Kim, Jong Wook. "When Absence Is Evidence: Evaluating Completeness-Sensitive Negative Reasoning in Large Language Models." arXiv:2608.04591v1, 5 August 2026. cs.CL, cross-listed cs.AI. 19 pages, 2 figures, 20 tables.**
Status: **VERIFIED** — read in full 2026-08-21. Title and authors resolved from arXiv; the ledger's earlier action item is closed. Note that **CROWN-QA is the benchmark's name, not the paper's title** — it stands for Completeness Reasoning Over What is Not in Question Answering. The bracket key is fine; the bibliography entry must use the real title.
Why we cite it: **repositioned 2026-08-21 from adjacent support to cross-method recovery.** They define completeness-sensitive negative reasoning as a two-label task, `Certified-Negative` versus `Unknown`, with the gold label computed as `c = Comp(E, S(q))` — no generative model, no posterior, no "how much." Their headline is over-closure: under naive prompting, OCR exceeds UCR for all three models (37.2/21.6 Qwen3.5-9B, 40.8/11.8 Claude Haiku 4.5, 76.0/0.9 Gemma-4-12B). **Over-closure is the closed-world assumption applied where it does not hold, which in our coordinates is `q_0` under `δ > 0`, the credulous point.** So this is the same failure our dropout arms recover by a different route, and it corroborates Example 2's second half and the ARITH_D0 over-reads rather than its ladder. Their finer structure matches too: the dominant CROWN-Synth failure is asymmetric, with L3 complete members correct at 82.4–100% and matched partial members at 0.0–27.9%, which is the same shape as our δ=0 success against δ=0.3 null.
Distinctions to state in one sentence: their controlled axis is how coverage is *expressed* (L1 explicit, L2 paraphrased, L3 implicit, L4 adversarial); ours is which operations the transcript *requires*. Their decomposition is a self-reported certificate they explicitly describe as diagnosing model-reported fields rather than internal reasoning; ours deletes an operation from the task. Their question is upstream of ours and cannot express magnitude.
Also relevant: prompting redistributes errors between over- and under-closure without repairing the paired distinction, which is a second independent form of the item-1.4 prompting pre-emption alongside Li25c and Zho25.

**[Eo26] Silence as a pragmatic act. ACL 2026, aclanthology 2026.acl-long.2101.**
Status: **PARTIAL**
Why we cite it: models average roughly 0.45 accuracy on silence items against roughly 0.91 for humans. **This is the human baseline that protects Probe P's exact +0.000.** A referee cannot dismiss our result as an unreasonable ask when humans clear a comparable task at 0.91. Note the distinction when citing: theirs is social interpretation of silence, ours is Bayesian updating under a known disclosure rule.

**[Li25c] Multi-agent hidden-profile tasks.**
Status: **UNRESOLVED**
Why we cite it: prompts such as "share all information" or "recognize information asymmetry" improve performance but leave a large gap from full-information accuracy. Direct pre-emption of the prompting objection.

**[Zho25] Detailed instructions about information structure do not reliably improve active information seeking, and can hurt.**
Status: **UNRESOLVED**
Why we cite it: the strongest general form of our point. Independent evidence that telling a model the structure does not induce the corresponding inference. Pair with Li25c at the objection.

**[Van26] Pragmatic cooperation under epistemic asymmetry. arXiv:2607.11053.**
Status: **PARTIAL**
Why we cite it: models behave literally by default; careful pragmatic prompting and tool access help. Supports partial promptability rather than reliable rule-following. Secondary to Li25c and Zho25.

## 1.5 The direction-of-error anchors (EIML Example 1)

**Added 2026-08-21, checklist items 34–39.** These three carry §4's opening tension. They do a different job from §1.4: those defend the empirical claim against a prompting objection, these establish that the *direction* of error is contested in the literature and that our coordinate system can locate both positions on one task.

**[Imr25] Imran, Sohaib; Kendiukhov, Ihor; Broerman, Matthew; Thomas, Aditya; Campanella, Riccardo; Lamb, Rob; and Atkinson, Peter M. "Are LLM Belief Updates Consistent with Bayes' Theorem?" arXiv:2507.17951, 23 July 2025. **Accepted at the ICML 2025 Workshop on Assessing World Models.** cs.CL, cross-listed cs.AI.**
Status: **VERIFIED** — abstract, ICML workshop acceptance, and the directional result confirmed 2026-08-21. Full-text read is still owed for the 30%-discrepancy figure (see caution below).
Why we cite it: the **under-updating** half of §4's tension. They formulate a Bayesian Coherence Coefficient and find that **for every model tested the gradient of observed against expected updates is less than 1**, with larger and more capable models showing a gradient closer to 1. Gradient below 1 is under-updating, and it is universal across their roster rather than a subpopulation finding.
**The population caveat is the load-bearing part.** Their models are **pre-trained-only**, across five families, measured via token log-probabilities. Our population is instruction-tuned configurations measured on elicited answers. The two do not overlap, and §4 ¶1 already states this correctly — do not let a later edit drop it.
**One finding held for later:** they report the update gradient is inversely proportional to the negative evidence log-likelihood, so under-updating worsens as evidence strengthens. That is a prediction about our grid, where `eps` ranges over a factor of fifty (C cells 3.5–3.8 nats, D cells 0.06–0.08). Testing it needs `π_pos` rather than `s1`, because `s1` is a bin distance and higher `eps` mechanically means more bins between `b_pos` and `b*`. **Deferred to the EC paper or the 6-page branch**; not an EIML item.
**Caution:** a Semantic Scholar summary attributes to this paper a figure of up to a 30% average difference between the elicited posterior and the correct update. That may be a citing paper's characterization rather than theirs. **Do not cite that number without the full text.**

**[Sam26] Samanta, Ankur; Magesh, Akshayaa; Lancewicki, Tal; Jain, Ayush; Yu, Youliang; Sajda, Paul; Hassani, Kaveh; Modi, Aditya; Jiang, Daniel R.; and Efroni, Yonathan. "BayesBench: Evaluating LLM Belief Trajectories Under Multi-Turn Evidence Accumulation." arXiv:2606.30850v1, 29 June 2026. cs.AI. Meta AI, Columbia, Meta Superintelligence Labs, Tel Aviv University. Code at github.com/Ankur-Samanta/BayesBench.**
Status: **VERIFIED** — read in full 2026-08-21. **Promoted from supporting cite to a §4 anchor.**
Why we cite it: **this ledger entry was already correct and `example1README.md` §2 was not.** The README calls this an over-confidence anchor. The paper reports **both directions, split by scale**: smaller models stay too close to the middle, larger models push predictions toward 0 and 1 where the Bayesian reference stays far from the extremes (Takeaway 1). The MAE table confirms it — at θ=0.5, error rises monotonically with scale, 8.3 for LLaMA-3B against 36.7 for Qwen-32B and 34.2 for LLaMA-70B. Seven instruction-tuned models, 3B–70B, LLaMA 3 and Qwen 2.5.
**Consequence for item 36:** BayesBench meets the bar in a qualified form. It claims over-confidence in a **scale-defined subpopulation** while corroborating our under-updating direction across the rest of its roster. §4 must say so, and must have an answer to "your roster is too small to produce the over-direction." The answer is that the over-direction *does* appear on our instrument — 2 over-reads in ARITH_D0 and the wrong-channel result at δ=0.3 — so the objection becomes "your instrument sees it only when the channel set changes," which is the thesis.
**A live alternative explanation we must kill.** Their medical-triage result is that models sharpen Emergency and Routine but collapse Urgent and Observation, pushing ambiguous cases toward the extremes — **on a four-level ordinal scale**, structurally ours. That is a competing account of Example 1 that none of A1, A2, B1, B2, B4, or prior-crossing rules out. The kill is that our errors land at `level(b_pos)` rather than at scale endpoints: `%BEY` runs 0.0–5.7 across the gated five, and 108 of glm's 140 prior-crossing errors sit exactly at `l_pos`. **Needs one script run: the D-cell split of the 47 displaced RULED draws by level.** If they concentrate at level 2, this is a fourth killed alternative and belongs in §4 ¶5.
**Free asset:** they build on the bookbag-and-poker-chip paradigm (Edwards 1982; Phillips and Edwards 1966). Our design is a rule-conditioned variant of that paradigm, which is worth one clause in §2 as a legitimacy argument.

**[Edw68] Edwards, Ward. "Conservatism in Human Information Processing." In Kleinmuntz, B. (ed.), *Formal Representation of Human Judgment*. Wiley, 1968. Reprinted in Kahneman, Slovic, and Tversky (eds.), *Judgment under Uncertainty*, Cambridge University Press, 1982, pp. 359–369.**
Status: **VERIFIED**
Why we cite it: the construct name only, one clause in §4 ¶1. Under-updating relative to Bayes has been called conservatism since 1968, and naming it costs nothing and signals we know the lineage.
**Citation consistency note:** the field often reaches for the 1982 reprint — BayesBench cites Edwards 1982 plus Phillips and Edwards 1966 for the original experiment. Cite the 1968 original, note the reprint in the entry, and use one form consistently. Phillips and Edwards 1966, *Journal of Experimental Psychology* 72(3):346–354, is the experimental source if §2's paradigm clause needs a citation.

## 1.6 Owed but not yet read

**Added 2026-08-21.** Three citations surfaced by reading CROWN-QA and BayesBench. Bibliographic detail is from their reference lists, which is enough to find each paper and **not** enough to characterize its claim. Read before citing.

**[Zha25] Zhang, Jensen; Yang, Jing; and Wang, Keze. "Large Language Models as Discounted Bayesian Filters." arXiv:2512.18489, December 2025.**
Status: **PARTIAL (secondary bib)** — from BayesBench's reference list.
Why we cite it: **highest priority of the three.** Models LLM updates as Bayesian filters with systematic evidence discounting. Discounting is our `discount` operation and our `q_δ`. A referee working in this area will expect it cited, and it is close enough that we need to know whether it collides with Table 1's fourth operation.

**[Fu25] Fu, Harvey Yiyun; Shrivastava, Aryaman; Moore, Jared; West, Peter; Tan, Chenhao; and Holtzman, Ari. "AbsenceBench: Language Models Can't Tell What's Missing." arXiv:2506.11440, 2025.**
Status: **PARTIAL (secondary bib)** — from CROWN-QA's reference list, where it is tabulated as evaluating omission but not whether missing support licenses a negative answer.
Why we cite it: directly about the `identify` operation and therefore about Example 2's first rung. If models cannot detect what is missing, that is the mechanism our ARITH_D0 rung removes, and the `π_pos` collapse is the quantitative version of their finding.

**[Raz24] Razniewski, Simon; Arnaout, Hiba; Ghosh, Shrestha; and Suchanek, Fabian. "Completeness, Recall, and Negation in Open-world Knowledge Bases: A Survey." *ACM Computing Surveys* 56(6):1–42, 2024.**
Status: **PARTIAL (secondary bib)** — from CROWN-QA's reference list.
Why we cite it: the knowledge-base vocabulary for our `δ = 0` versus `δ > 0` distinction — closed-world treats missing facts as false, open-world leaves them unknown. That is the same object de Punder gives us as trimming versus censoring. **Having both the statistics vocabulary and the KB vocabulary in §7 is cheap and makes the positioning look deliberate rather than lucky.** Survey, so a single citation covers the line.

**[Gup25] Gupta, R.; Corona, R.; Ge, J.; Wang, E.; Klein, D.; Darrell, T.; and Chan, D. M. "Enough Coin Flips Can Make LLMs Act Bayesian." In *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 7634–7655, 2025. arXiv:2503.04722.**
Status: **VERIFIED** — read in full 2026-08-25. Promoted from the §1.6 lower-priority note.
Why we cite it: §4 ¶1. Updates track the Bayesian posterior on **present** evidence once enough accumulates; the residual deviation is attributed to the model's **own miscalibrated prior**, not to the update. **CAUTION:** their "prior" is an unstated model-internal bias toward heads, **not** a stated task prior — do not conflate with our `π`. Table 1 fits a per-model exponential decay `γ` over ICL history (instruction-tuned 0.31–0.47, base 0.88–0.91), which is discounting by **recency** over sequential evidence, a different object from our fourth operation (discount by a stated dropout rate against absences). Relevant to G4.7.

---

# TIER 2 — Supporting. Cite where relevant; the paper survives without any single one.

## 2.1 Surname prior (spin-off result)

The finding is established; **our measurement is what is new.** Everyone else reports acceptance rates, dollars, flip rates, or Cohen's d. We report a name effect and an evidentiary update in the same log-odds units and find parity. Frame the contribution as the unit, not the effect.

**[Wei24] Simulated trust game with Hispanic, East Asian, Black, White surnames; token probabilities converted to expected transfers; Cohen's d up to 1.63. arXiv:2406.10486.**
Status: **PARTIAL**
Why we cite it: closest surname design, and it uses the same two ethnicity categories as our Alvarez/Chen pair. No comparison against evidence and no guilt judgment.

**[Hai24] Name swaps across 42 templates and 14 domains; approx \$74 versus \$154 offers in a GPT-4 purchase task; qualitative evidence does not reliably remove name disparities while strong numerical anchors can. arXiv:2402.14875.**
Status: **PARTIAL**
Why we cite it: the "evidence does not wash out the name" finding is directly our result in a different measure.

**[Sch26] Null result: race and gender effects not statistically significant in a 90-query criminal-conviction study with GPT-3.5 and GPT-4. *Humanities and Social Sciences Communications*, article s41599-026-07776-x.**
Status: **PARTIAL**
Why we cite it: **cite this deliberately rather than burying it.** A published null in a criminal-conviction setting is the strongest available argument that continuous belief elicitation surfaces what forced-choice designs miss.

**[Bas26] Name and race swaps in high-stakes vignettes including sentencing; average demographic flip rate a few percent; forced-choice outputs.**
Status: **UNRESOLVED**
Why we cite it: the design-match contrast. Closest design to ours, much smaller reported effect, and the plausible reason is forced choice rather than probability elicitation. Pairs with Sch26 to turn our instrument into a methodological argument.

**[Jha22] Proper nouns shift supposedly name-neutral spatial reasoning; conditional log probabilities and beam scores poorly calibrated in that setting. OpenReview id K8Zgd3hoea.**
Status: **PARTIAL**
Why we cite it: **the methodological caution, and it lands on our data.** Undermind warns to verify that exact log-2 gaps are not an artifact of rounded verbal probabilities or a small discrete output set. From Task 2.1f we already know the probe emits round numbers at roughly 1.1 nats of resolution against a 0.693-nat target, and that the exact +0.693 appeared specifically on the five canned-response channels. **Write it as what it is:** on those channels the probe is choosing between two discrete outputs whose gap happens to be log 2. Stated that way it survives. Stated as a measured effect landing exactly on log 2 it does not.

**[Ngh24] Identical qualifications, name swaps, approx 5% salary shifts. arXiv:2406.12232.** Status: PARTIAL. Supporting cite.
**[Si26] Identical misconduct, approx 23 percentage point blame gap by actor gender.** Status: UNRESOLVED. Supporting cite; shows identity cues shift blame under identical conduct.
**[Liu25b] Prestige cues (occupation, employer, affiliation) shift guilt and sentencing judgments.** Status: UNRESOLVED. Supporting cite; status priors rather than surname priors.

## 2.2 Dynamics neighborhood (Burlion-facing)

Cite as the landscape the framework sits in. None threatens the contribution.

**[Itk26] Delayed verification as a graph belief dynamical system; grounded-Laplacian spectral analysis giving stability thresholds and oscillatory instability. arXiv:2606.27409.**
Status: **PARTIAL**
Why we cite it: Burlion will recognize this immediately and it is the best single example of control-theoretic machinery applied to LLM agent dynamics. Also relevant to Task 2.3 (plateau time constant) since it treats lag explicitly. Scalar synthetic beliefs and oracle correctors, no strategic withholding.

**[Saa26] Lyapunov disagreement function; consensus under persistent connectivity, cluster consensus under routing fragmentation. arXiv:2607.12077.**
Status: **PARTIAL**
Why we cite it: a Lyapunov function for LLM agent dynamics that is not ours. Naming-game states rather than truth-tracking beliefs.

**[Yaz26] DeGroot-style LLM opinion dynamics with spectral convergence rates on the second eigenvalue. arXiv:2601.21540.**
Status: **PARTIAL**
Why we cite it: cooperative averaging, no private evidence. Landscape only.

**[Ana26] Byzantine agents strategically preventing consensus; resilient filters restoring agreement.** Status: UNRESOLVED. Landscape; strategic adversaries present but no private evidence or selective disclosure.
**[Far26] Entropy-based gating of LLM agent contributions.** Status: UNRESOLVED. The closest LLM treatment of silence, but gating is an algorithmic rule rather than a strategic choice and the system does not infer from silence.

## 2.3 Pragmatics background

**[Hu23]** formalizes implicature through expectations over unspoken alternatives. **[Mcd19]** shows pragmatic listeners learn from a speaker's choice among descriptions. **[Cho24]** finds LLMs sometimes recover scalar implicatures with inconsistent context sensitivity.
Status: all **UNRESOLVED**.
Why we cite them: one sentence establishing that the pragmatics literature explains *why* omissions can be informative, followed by the distinction that matters. Their alternatives are linguistic (why "some" and not "all"); ours is a stated selection policy. Keep this to two sentences; it is background, not a threat.

**[Jeo26]** aclanthology 2026.acl-long.1674, and **[Gu24]**: explicitly representing another character's lack of knowledge improves theory-of-mind behavior. Status: PARTIAL / UNRESOLVED. Supporting; the distinction is that theirs is a supplied mental-state annotation, not an inference derived from a known reporting policy.

---

# TIER 3 — Already logged in Related Work Check

Carried here so the paper's bibliography is assembled in one place. Full detail already in the 2026-06-11 and 2026-07-13 entries.

- **Damiano, Li, Suen, "Delay in Strategic Information Aggregation" (2008)** — the unmechanized baseline; multi-agent, fixed signals, equilibrium delay, finite-round convergence.
- **Hahn, "Sequential Aggregation of Verifiable Information," *J. Public Econ* (2011)** — **cite as the contrast that sharpens our protocol.** Experts self-censor, but because disclosure is sequential and silence is informative, correct-state revelation converges to one as the group grows. That is the opposite conclusion to ours, and the reason is that our protocol is simultaneous first-opportunity with a silence-blind observer. This paper is the argument for why our restriction is doing real work.
- **Guttman, Kremer, Skrzypacz, AER 2014** — dynamic voluntary disclosure; the title is our problem statement.
- **Wu, Amin, Ozdaglar, *Math. OR* 2022** and companions — coupled belief-strategy learning dynamics; closest Phase 3 template.
- **Xu, Zhang, Li, Zou, npj AI 2026** — Lyapunov-guided cooperative constraint fusion; watchlist Group 3 anchor.
- **Estornell & Liu, "Multi-LLM Debate," NeurIPS 2024** — required reading tier; reviewers expect it cited.
- **Breaking the Martingale Curse, arXiv:2603.06801** — naming and framing overlap on the potential-function side.
- **Diverse Evidence, Better Forecasts, arXiv:2607.01661** — deliberation under information asymmetry.
- **The Deliberative Illusion, arXiv:2606.03032** — empirical factual attrition under consensus pressure.

---

# ACTION LIST

**EIML bibliography, before item 69 (2026-08-29 deadline):**
1. Read Zha25 (discounted Bayesian filters) — the only §1.6 item that could collide with Table 1.
2. Resolve Eo26, Li25c, Zho25 to VERIFIED — these carry the prompting pre-emption and three of four are still short of full detail.
3. Re-read Pun25 for the trimming-versus-censoring vocabulary (checklist item 50).
4. Fix `example1README.md` §2's BayesBench characterization; the ledger entry at §1.5 is the correct text.
5. Decide whether Fu25 and Raz24 enter §7 or wait for the 6-page branch.

**Resolve before the strategic-timing bibliography is finalized (priority order):**
1. Zhu26 — closest collision to Prop 1b, and unresolved.
2. Liu26b — Phase 3 gate item.
3. Jal25 — may promote to must-cite depending on its mechanism.
4. Kar26 — 2026 econ paper, also a watchlist candidate.
5. Osb19, Li25c, Zho25 — Tier 1 with no detail at all.
6. Everything remaining at UNRESOLVED.

**Read before writing:** ~~CROWN-QA~~ (done 2026-08-21), Zhu26, Pun25, Jal25, Zha25.

**Document edit owed:** §8.9 of Convergence_Theorem.md restates restricted-KL negativity as a claim. Reposition as a known lemma citing Pun24 and Pun25, and adopt the trimming-versus-censoring vocabulary. Folds into the owed 2.1e-b confirmatory pass rather than a separate edit.

**Preemptive novelty paragraph, now mandatory, with three concessions rather than one:**
1. The negativity of the restricted KL is known (Pun24, Pun25, Gke20).
2. That more senders can hurt aggregation is known (Kar26, Osb19), though by the opposite mechanism.
3. That debate beliefs admit martingale treatment is known (Cho25, Zhu26).
Concede all three in our own words, then locate the contribution above them: the silence-aware reference posterior as a distinct object, the exact tracking-error split, and the growth in N.

**EIML-specific concession, added 2026-08-21:** that LLMs mishandle absent evidence is known (CROWN-QA, Fu25, Eo26). Concede it, then locate the contribution: they ask whether absence licenses an inference, we ask how far the belief should move, and only the second needs a computed target.
