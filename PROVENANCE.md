# Provenance: what this record establishes, and what it does not

**Written 2026-08-21. Covers every campaign, pre-registration, and analysis artifact in this
repository.**

This file exists because the repository makes pre-registration claims, and a reader is
entitled to know precisely how much those claims are worth. The short version: **content
integrity is verifiable; temporal ordering is not.** Every claim below is stated so that a
reader can check it directly against the repository rather than take it on trust.

---

## 1. What is verifiable

**Content integrity.** The stimuli analysed are the stimuli registered. `silence_v2_spec.md`
records a sha256 over the stimulus set, and `silence_v2_stimuli.py`'s `verify()` re-asserts
the structural invariants (band membership, level assignments, the non-degenerate ordinal-`s`
denominator) at build time. Anyone can recompute the hash and re-run `verify()`.

**Deterministic regeneration.** The frozen analysis artifacts regenerate byte-identically
from the frozen draw records. Verified 2026-08-21 by re-running the pipeline and taking an
empty `git diff`: `results_v2/v2_gates.json`, `results_v2/v2_banked_gates.json`,
`results_w1/w1_gates_live.json`, and `results_w1/w1_lowside.json`.

**Arm arithmetic.** Every experimental arm's `configs × stimuli × draws` product closes
exactly against its record count, with no ragged arm and no file header disagreeing with its
own records. Five experimental arms hold **7,051 usable draws of 7,210 attempted**; the W1
pre-test holds a further **659 of 672** on a separate stimulus set at three draws per
stimulus rather than five. Reproduce with `s6_draw_census.py`.

**Decision rules as executable code.** Every gate, kill condition, threshold, and exclusion
rule is implemented in a committed script rather than described in prose only. A reader can
see exactly what was computed, whatever they conclude about when it was written.

---

## 2. What is not verifiable

**Ordering.** Nothing in this repository establishes that any registration predates the calls
it registers. Three independent reasons, all checkable:

1. **Version control begins after the fact.** The first commit touching the experimental code
   is dated **2026-08-20**. The W1 pre-test ran **2026-08-14**; the main v2 campaign ran
   **2026-08-15**. Git therefore cannot order any registration against any campaign, for any
   part of this project.

2. **Draw records carry no timestamps.** Records in `results_w1/`, `results_v2/`,
   `results_sweep/`, and the ARITH arms carry `config`, `slug`, `seed`, `stimulus_id`,
   `finish_reason`, and outcome fields, but no wall-clock field. There is no internal clock to
   check a registration against.

3. **Filesystem mtimes are weak, and one of them is actively unfavourable.**
   `silence_v2_spec.md`, which is where P1 through P5 are registered, has an mtime of
   **2026-08-16 03:25**, roughly five hours *after* `results_v2/v2_results_live.json` at
   **2026-08-15 22:13**. The spec was edited after the campaign it registers. Nothing in the
   record shows what that edit changed. We do not ask the reader to assume it was immaterial.

**One referenced artifact does not exist.** `w1_analyze.py`'s module docstring states that it
applies a decision rule pre-committed in `w1_pretest_plan.md` §5. **That file is not in this
repository and has never appeared in its history.** The rule itself is not lost: the four W1
gates and their thresholds are implemented in `w1_analyze.py`, which is what actually ran. But
the artifact the docstring cites as the freeze does not exist, and we have not reconstructed
it, because a file written now and presented as a pre-commitment would be backdating.

The one piece of corroboration available for W1 is weak and offered as such: mtimes place
`w1_analyze.py` at 21:18, its results at 21:24, and the low-side addendum at 21:39 on
2026-08-14, an ordering consistent with the docstring. Mtimes are trivially settable and move
on any edit. This is corroboration, not evidence.

---

## 3. The standard we hold ourselves to

We do not use "frozen," "pre-registered," or "pre-committed" as unqualified terms anywhere in
the paper or the READMEs. Where a prediction was fixed before its test, we say so and name
what backs the ordering; where the backing is an internal assertion, we say that instead.

Specifically:

- **Tiered pre-registration claims** (paper §6, Table 2) are labelled by tier, and the tier
  labels describe *where* something was registered, not *when* it was verified to have been.
  The section states in its own text that both tiers rest on an internal timestamp for
  ordering.
- **Kill conditions** are described as fixed at a checkpoint before their test ran. This is
  true as a description of the working process and is not independently verifiable. It is
  stated as a process claim, not as a provenance guarantee.
- **The band pre-test** is described as measured rather than assumed, which the data
  establishes, and is **not** described as operating under a frozen plan, which the record
  does not.
- **Literature anchors were selected after the data existed.** The campaigns were designed
  and run first; the related-work engagement came later. This is stated plainly in the paper
  rather than left to inference.

---

## 4. Why this is stated rather than quietly narrowed

A pre-registration claim that cannot be checked is worth less than an honest account of what
the record supports, and considerably less than nothing if a reader checks it and finds it
overstated. The substantive results here do not depend on ordering. They depend on closed-form
targets computed before any model saw a prompt, on decision rules visible in code, on
denominators stated with their populations, and on artifacts that regenerate exactly. Those
are the claims we make.

The remedy for the rest is procedural and applies to future work rather than this record:
commit the registration, tag it, and record the tag in the paper before the first call.
