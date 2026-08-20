"""
silence_control_stimuli.py — FULL-EXPLICIT control arm.

Question this answers
---------------------
Four of seven model configurations failed the FULL condition, where every assay result is printed
and nothing has to be inferred. Two readings of that failure are consistent with the data so far:

  H_digest    the model cannot integrate nine conditionally independent observations at all.
  H_recognise the model integrates them fine but does not recognise that an exact posterior is
              what is being asked for, and answers with a directional impression instead.

These are indistinguishable in the frozen design, because R5 (§4.1) forbids naming the operation in
ANY condition. R5 is correct for the PARTIAL conditions: telling the model to apply Bayes' rule
would tell it what to do with the silence and destroy the measurement. But R5 also applies to FULL,
so FULL is currently testing arithmetic competence AND task recognition at the same time.

This arm holds the record and the likelihood table byte-identical to the frozen FULL stimulus and
changes ONLY the elicitation, naming the operation explicitly. It deliberately violates R5. That is
the point, in the same way §10's ARITHMETIC CONTROL deliberately violates R1 and R2: it is a
competence control, not a silence test, and it is never scored on the b_pos -> q^t scale.

Reading the outcome
-------------------
  FULL-EXPLICIT passes, FULL fails  -> H_recognise. The models digest the evidence and do not
      recognise the task. This does not repair the frozen runs, and it does not make those models
      usable for the silence claim, because a silence test cannot name the operation. It changes
      what the paper says about them: not "cannot infer" but "does not infer unless told to."
  FULL-EXPLICIT also fails          -> H_digest. The existing sorting stands unchanged.

Output: silence_control_stimuli.json + .sha256, same record shape as the main stimulus file so
silence_harness.py and analyze_2_4.py read it without modification.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path

from silence_model import FULL, Cell, logodds
from silence_stimuli import (
    LABELS,
    NUMBER_WORDS,
    Stimulus,
    build_schema,
    full_record_block,
    label_map,
    preamble,
)

# The frozen FULL cells of Block 1: k in {0,2,4,6} x 2 mirrors. Block 1 is where every model was
# run, so it is the only block where this control can be compared against existing FULL data.
GRID = [(2, F(3, 5), F(2, 5), 9, k, rot) for k in (0, 2, 4, 6) for rot in (0, 1)]


def explicit_elicitation(m: int) -> str:
    """
    Names the operation. Everything R5 forbids, on purpose.

    Written to remove every excuse for an impression-based answer without supplying any of the
    arithmetic: it says what to do and does not say how it comes out. In particular it does not
    state the counts, restate independence beyond what the preamble already says, or hint at a
    direction.
    """
    keys = LABELS[:m]
    key_phrase = (
        f"keys {keys[0]} and {keys[1]}"
        if m == 2
        else "keys " + ", ".join(keys[:-1]) + f" and {keys[-1]}"
    )
    return (
        "Apply Bayes' rule. Starting from the equal prior, multiply in the likelihood of every\n"
        "recorded result under each candidate, treating the results as conditionally independent\n"
        "given which candidate is responsible, and normalise. Compute the exact posterior\n"
        "probability rather than estimating it.\n\n"
        f"Reply with only a JSON object with {key_phrase}, each a probability to three decimal\n"
        "places, summing to 1."
    )


def build() -> list:
    out = []
    for m, p, r, N, k, rot in GRID:
        lmap = label_map(m, rot)
        cell = Cell(m=m, p=p, r=r, N=N, k=k, delta=F(0))
        head = preamble(m, p, r, lmap, f"{NUMBER_WORDS[N]} analysts were each assigned a different assay.")
        prompt = (
            f"{head}\n\n"
            f"The complete set of results is recorded below. These are all {NUMBER_WORDS[N].lower()} results.\n\n"
            f"{full_record_block(N, k)}\n\n"
            f"{explicit_elicitation(m)}"
        )
        out.append(
            Stimulus(
                sid=f"CTRL-FULL-EXPLICIT|m{m}|N{N}|k{k}|rot{rot}|FULL-EXPLICIT",
                block="CTRL-FULL-EXPLICIT",
                condition="FULL-EXPLICIT",
                m=m, p=str(p), r=str(r), N=N, k=k, delta="0",
                rotation=rot, target_label=lmap[0],
                prompt=prompt, schema=build_schema(m),
                b_pos_logodds=cell.b_pos_logodds,
                q_t_logodds=cell.q_t_logodds,
                b_star_logodds=cell.b_star_logodds,
                denominator=cell.denominator,
                denominator_nats=cell.denominator_nats,
                correct_logodds=logodds(cell.correct_answer(FULL)),
                is_flip=cell.is_flip,
            )
        )
    return out


def verify(stims: list, frozen: list) -> list:
    """
    The control is only interpretable if the ONLY difference from the frozen FULL stimulus is the
    elicitation. Anything else changing turns a clean contrast into a confound, so this is checked
    against the frozen file rather than asserted in a comment.
    """
    errs = []
    by_frozen = {
        (s["k"], s["rotation"]): s
        for s in frozen
        if s["block"] == "B1-CORE" and s["condition"] == "FULL"
    }
    for s in stims:
        f = by_frozen.get((s.k, s.rotation))
        if f is None:
            errs.append(f"{s.sid}: no frozen FULL counterpart")
            continue

        # Everything up to the elicitation must be byte-identical.
        mine = s.prompt.split("\n\nApply Bayes' rule.")[0]
        theirs = f["prompt"].split("\n\nGive your probability")[0]
        if mine != theirs:
            errs.append(f"{s.sid}: record or preamble differs from frozen FULL stimulus")

        # Same correct answer, same target, same schema.
        if abs(s.correct_logodds - f["correct_logodds"]) > 1e-12:
            errs.append(f"{s.sid}: correct answer differs from frozen FULL")
        if s.target_label != f["target_label"]:
            errs.append(f"{s.sid}: target label differs from frozen FULL")
        if s.schema != f["schema"]:
            errs.append(f"{s.sid}: schema differs from frozen FULL")

        # The operation must actually be named, or the control does nothing.
        if "Bayes" not in s.prompt:
            errs.append(f"{s.sid}: control does not name the operation")

        # It must not leak the answer or the counts.
        low = s.prompt.lower()
        for w in ("posterior probability of sigma", "0.771", "more likely", "favours", "favors"):
            if w in low:
                errs.append(f"{s.sid}: control leaks a direction or a value ({w!r})")
    return errs


def main() -> int:
    frozen = json.loads(Path("silence_stimuli.json").read_text(encoding="utf-8"))
    stims = build()
    errs = verify(stims, frozen)
    print(f"silence_control_stimuli.py — generated {len(stims)} FULL-EXPLICIT stimuli")
    if errs:
        print(f"\nFAILED: {len(errs)} problems\n")
        for e in errs:
            print(f"  {e}")
        return 1

    blob = json.dumps([asdict(s) for s in stims], indent=2, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    Path("silence_control_stimuli.json").write_text(blob, encoding="utf-8")
    Path("silence_control_stimuli.sha256").write_text(f"{digest}  silence_control_stimuli.json\n")
    print("ok   record and preamble byte-identical to frozen FULL; only the elicitation differs")
    print(f"\nFROZEN sha256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
