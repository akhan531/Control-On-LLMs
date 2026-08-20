# Amendment 1 to `silence_probe_spec.md`

**Date:** 2026-08-14
**Applies to:** §4.3 (Templates) and §5 (The grid)
**Type:** clarification. Resolves two points the frozen spec left underdetermined. **Does not change
the design, the grid, the statistic, the conditions, or the pre-registration.** No value in §2.1 or
§5 changes, and `silence_model.py` is unaffected.
**Raised by:** construction of `silence_stimuli.py`, which cannot emit a stimulus without both.

Filed per §13, which requires that any departure from or extension of the frozen spec be recorded
with its reason and what it changes, in the manner of `meridian_v2_amendment_1.md`.

---

## A1.1 FULL record ordering

**Resolution: the FULL record lists all `k` POSITIVE lines first, then all `N − k` NEGATIVE lines.
Deterministic, no interleaving, no per-cell shuffle.**

§4.3 shows `POSITIVE / POSITIVE / NEGATIVE / ...`, which reads as sorted but does not say so, and the
alternative — a per-cell deterministic interleave — was live.

**Reason.** The spec's central pivot (§0, §6) is that FULL and PARTIAL-RULED δ=0 have the same
correct answer, reached by the same expression `L^k (1−L)^(N−k)`, and differ *only* in whether the
`N − k` negatives are displayed or must be derived from absence. Sorting makes that identity hold at
the byte level: the FULL record is exactly the partial REPORTS block with the negatives written
underneath it. An interleaved record would differ from the partial record in ordering *as well as* in
content, introducing a second uncontrolled difference into the one comparison the paper rests on.
This is the same discipline that §1.1 applies to the δ axis and R3 applies to the partials.

**The objection this invites, and why it does not bite.** A sorted record makes the counting step
trivial. It does not make the inference trivial: the correct answer still requires a posterior from
`p`, `r`, `k`, `N`, and the counting step is equally trivial in the partial conditions, where the
record is `k` byte-identical POSITIVE lines. More directly, FULL is a validity gate the design
*wants* to pass (P1). If FULL is easy and PARTIAL-RULED still fails, the contrast is strengthened,
because the failure cannot be attributed to arithmetic difficulty — the arithmetic is the same
expression.

**The residual threat, and where it is already handled.** Negatives always occupy the tail of the
FULL record, so a model with a recency bias shades FULL downward relative to `b*`. This is not
controlled by the mirror halves, which swap labels and not record order. It is, however, directly
measured: the mandatory absolute-error-in-nats companion (§6) reports FULL's signed departure from
`b*` in every cell, and §9.1 is exactly the machinery for the case where FULL shows systematic
shading. No new control is added. If FULL's error is systematically negative across models, that is
reported and the §9.1 sensitivity analysis is run as specified.

---

## A1.2 The meaning of "mirror" at `m = 2`

**Resolution: a mirror half swaps which printed label carries `p`. The candidate list is printed in
the same order (SIGMA, THETA) in both halves; in half A, SIGMA carries `p` and is the target, and in
half B, THETA does.**

§5 Block 2 defines the mirror as rotating which label is the target. Blocks 1 and 3 say only that
cells are run "mirrored with the label roles swapped," which at `m = 2` is ambiguous between swapping
the likelihood assignment and swapping the display order at fixed assignment.

**Reason, primary.** Block 2's definition generalizes directly to `m = 2` and the alternative does
not. Adopting the display-order reading would make the word "mirror" name two different operations in
one methods section, which is a defect a referee finds and which no result justifies.

**Reason, on the merits.** The bias the mirror exists to detect is a preference for a label token or
a list position that is independent of evidence — the non-name labels of §1 were chosen precisely to
design out the +0.595-nat surname prior of Task 2.1f, and the mirror is what verifies that they did.
Swapping the `p`-carrier moves the target from the first printed slot to the second *and* changes
which token names it, so it detects token preference and list-position preference jointly. Holding
SIGMA at `p` and swapping display order tests position preference only and leaves token preference
entirely unchecked, which is strictly weaker against the specific threat.

**What this cannot do.** It detects such a bias but cannot attribute it to token or to position.
That is accepted. §12 records the mirror as a validation rather than something the headline leans on,
so detection is the requirement; attribution is needed only if the halves disagree, and a
disagreement is itself the finding that would license a follow-up.

**Invariance the construction relies on.** Because all beliefs are computed target-versus-aggregate
with the target at index 0, both mirror halves have *identical* correct answers in log-odds. Only the
printed label mapping differs. That identity is what makes half-agreement a meaningful check, and
`silence_stimuli.py` asserts it per cell rather than assuming it.

**Interaction with §7.2.** At `m = 2` both halves print the same two candidate labels, so the strict
JSON schema key set is unchanged between halves and no per-half schema regeneration is required. The
§7.2 requirement to regenerate the schema per label assignment continues to bind at `m = 3, 4`, where
the rotations change which labels appear.

---

## A1.3 Not changed

The 80-stimulus count, the 5,440-call total, the cut order, the four conditions, the statistic, and
P1–P7 are unaffected. Neither resolution adds or removes a cell.

A four-half mirror (both the label swap and the display-order swap, run separately) was considered
and rejected. It would double Block 1's stimuli in order to decompose a bias the design expects to be
absent, at a point in the schedule where the harness is unwritten and the figure freeze is current.
Cost was not the reason; budget is not a constraint per §5. The reason is that decomposition is
conditional on detection, and detection is what A1.2 already provides.
