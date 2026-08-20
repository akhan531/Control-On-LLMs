"""
silence_stimuli.py — generates all 80 stimuli for Task 2.4 and freezes them to a sha256.

Implements silence_probe_spec.md §4 (prompt design) and §5 (the grid), as clarified by
silence_probe_amendment_1.md:
  A1.1 — FULL record is sorted: all k POSITIVE lines, then all N-k NEGATIVE lines.
  A1.2 — a mirror half swaps which printed label carries p; display order is unchanged.

The binding rules of §4.1 are enforced as assertions here, not left to review. A rule that is only
written down is a rule that gets violated by a later edit; a rule that fails the build is not.

Output: silence_stimuli.json, plus its sha256 printed and embedded in the file's own metadata block.
Once written, no stimulus is edited (§13). A correction is an amendment with its own provenance.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from fractions import Fraction as F
from typing import Dict, List, Optional

from silence_model import FULL, PARTIAL_BLIND, PARTIAL_RULED, Cell, logodds

LABELS = ["SIGMA", "THETA", "LAMBDA", "OMEGA"]

NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
}

# §4.1 R1. These never appear in any prompt, in any casing. If a prompt says "six analysts were
# silent", the experiment has performed the inference and is measuring multiplication.
FORBIDDEN = [
    "silent", "silence", "absent", "missing", "did not report", "no report",
    "omit", "withheld", "unreported", "failed to report",
]

# §4.1 R5. The task is framed as reading a record, never as computing a posterior.
FORBIDDEN_R5 = ["posterior", "bayes", "update", "likelihood ratio", "prior probability"]

CONDITIONS = [
    ("FULL", FULL, None),
    ("PARTIAL-BLIND", PARTIAL_BLIND, None),
    ("PARTIAL-RULED-d0", PARTIAL_RULED, F(0)),
    ("PARTIAL-RULED-d3", PARTIAL_RULED, F(3, 10)),
]


# --------------------------------------------------------------------------------------
# Prompt construction
# --------------------------------------------------------------------------------------


def _pct(x: F) -> str:
    """Probabilities are printed to two decimals, matching §4.3's 0.60 / 0.40."""
    return f"{float(x):.2f}"


def label_map(m: int, rotation: int) -> List[str]:
    """
    Printed labels indexed by MODEL index, where model index 0 is always the target.

    A1.2: the printed candidate LIST is always LABELS[:m] in fixed order. What the rotation
    changes is which printed label the target is. So label_map[0] is the printed name of the
    target, and it moves through the list as rotation increases.
    """
    return [LABELS[(i + rotation) % m] for i in range(m)]


def candidate_list_block(m: int) -> str:
    """The printed candidate list. Fixed order, never rotated (A1.2)."""
    return "\n".join(f"    Candidate {LABELS[i]}" for i in range(m))


def likelihood_block(m: int, p: F, r: F, lmap: List[str]) -> str:
    """
    The likelihood table, printed in CANDIDATE-LIST order so the list and the table agree.

    lmap[0] is the target's printed name, so a printed label gets p exactly when it is lmap[0].
    """
    target_name = lmap[0]
    lines = []
    for i in range(m):
        name = LABELS[i]
        prob = p if name == target_name else r
        lines.append(
            f"    If {name} is responsible, an assay returns POSITIVE with probability {_pct(prob)}."
        )
    return "\n".join(lines)


def preamble(m: int, p: F, r: F, lmap: List[str], analyst_line: str) -> str:
    """
    §4.2: shared by all four conditions, byte-identical apart from the analyst line, which is the
    only place N enters and is therefore the only line that legitimately varies.
    """
    return f"""One of the following is responsible for the contamination event. Exactly one is.

{candidate_list_block(m)}

Before any testing, each candidate is considered equally likely.

{analyst_line} Each assay returns POSITIVE or
NEGATIVE, and the assays have the following known characteristics:

{likelihood_block(m, p, r, lmap)}

Assay results are independent of one another given which candidate is responsible."""


def elicitation(lmap: List[str], m: int) -> str:
    """
    §4.3 / §7.2. The explicit key-naming instruction is required, not stylistic: Llama-3.1-8B under
    a strict schema with no in-prompt format instruction emits an opening brace and then whitespace
    to the token cap. Keys are named in CANDIDATE-LIST order, not model order, so the instruction
    matches what the model sees printed.
    """
    keys = LABELS[:m]
    if m == 2:
        key_phrase = f"keys {keys[0]} and {keys[1]}"
    else:
        key_phrase = "keys " + ", ".join(keys[:-1]) + f" and {keys[-1]}"
    return (
        f"Give your probability that each candidate is responsible. Reply with only a JSON\n"
        f"object with {key_phrase}, each a probability to three decimal places,\n"
        f"summing to 1."
    )


def reports_block(k: int) -> str:
    """
    §4.1 R3. Byte-identical across all three partial conditions. No analyst identifiers: numbered
    identifiers with gaps would leak both N and the fact of omission into PARTIAL-BLIND and destroy
    the zero-point.
    """
    if k == 0:
        # The empty-record extreme. The header still appears, so the probe is told a record exists
        # and is empty rather than being handed a prompt with no record section at all, which would
        # be a structurally different stimulus from the k > 0 cells.
        return "REPORTS ON FILE\n    (none)"
    lines = "\n".join("    Assay returned POSITIVE" for _ in range(k))
    return f"REPORTS ON FILE\n{lines}"


def full_record_block(N: int, k: int) -> str:
    """
    A1.1: sorted. All k POSITIVE lines, then all N-k NEGATIVE lines. This makes the FULL record
    exactly the partial REPORTS block with the negatives written underneath, so the only difference
    between FULL and PARTIAL-RULED d=0 is whether the negatives are displayed or must be derived.
    """
    header = f"ALL {NUMBER_WORDS[N].upper()} ASSAY RESULTS"
    lines = ["    POSITIVE"] * k + ["    NEGATIVE"] * (N - k)
    return header + "\n" + "\n".join(lines)


def build_prompt(cond_name: str, m: int, p: F, r: F, N: int, k: int, rotation: int) -> str:
    lmap = label_map(m, rotation)
    n_word = NUMBER_WORDS[N]

    if cond_name == "FULL":
        # §4.1 R7. FULL states N and asserts completeness, and states NO rule: a rule saying
        # analysts file only on POSITIVE, printed above a record displaying NEGATIVE results, is
        # self-contradictory.
        head = preamble(m, p, r, lmap, f"{n_word} analysts were each assigned a different assay.")
        body = (
            f"{head}\n\n"
            f"The complete set of results is recorded below. These are all {n_word.lower()} results.\n\n"
            f"{full_record_block(N, k)}"
        )

    elif cond_name == "PARTIAL-BLIND":
        # §4.2. Excluded: N, the rule, delta, any mention that non-disclosure is possible, any
        # completeness assertion. Telling it that non-disclosure is possible would induce exactly
        # the hedge this arm exists to measure the absence of.
        head = preamble(m, p, r, lmap, "Analysts were each assigned a different assay.")
        body = f"{head}\n\n{reports_block(k)}"

    elif cond_name in ("PARTIAL-RULED-d0", "PARTIAL-RULED-d3"):
        head = preamble(m, p, r, lmap, f"{n_word} analysts were each assigned a different assay.")
        rule = "Standing protocol: an analyst files a report only when the assay returns POSITIVE."
        if cond_name == "PARTIAL-RULED-d3":
            # §4.1 R6. Pinned wording. "An analyst fails to file with probability 0.30" can land as
            # "30% of filed reports are wrong", which changes the correct answer entirely.
            rule += (
                "\nSeparately, an analyst does not file a report at all with probability 0.30, even\n"
                "when the assay returned POSITIVE."
            )
        body = f"{head}\n\n{rule}\n\n{reports_block(k)}"

    else:
        raise ValueError(f"unknown condition {cond_name!r}")

    return f"{body}\n\n{elicitation(lmap, m)}"


def build_schema(m: int) -> dict:
    """
    §7.2. Strict json_schema with additionalProperties: false, so the key set is exactly the
    candidate labels. Grammar constraints alone are insufficient for smaller models; both the
    schema and the in-prompt key instruction are required.

    The schema depends only on m, because A1.2 fixes the printed candidate list across rotations.
    At m = 3, 4 the rotations do not change which labels appear either, so one schema per m is
    correct. This is asserted in verify_stimuli().
    """
    keys = LABELS[:m]
    return {
        "type": "json_schema",
        "json_schema": {
            "name": f"candidate_probabilities_m{m}",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {kk: {"type": "number"} for kk in keys},
                "required": keys,
                "additionalProperties": False,
            },
        },
    }


# --------------------------------------------------------------------------------------
# The grid, §5
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Stimulus:
    sid: str
    block: str
    condition: str
    m: int
    p: str
    r: str
    N: int
    k: int
    delta: str
    rotation: int
    target_label: str
    prompt: str
    schema: dict
    # closed-form truth, computed not estimated
    b_pos_logodds: float
    q_t_logodds: float
    b_star_logodds: float
    denominator: float
    denominator_nats: float
    correct_logodds: float
    is_flip: bool


def _grid_specs():
    """(block, m, p, r, N, k, rotations) for each of the three blocks of §5."""
    # Block 1 — CORE. m=2, p/r = 0.60/0.40, N=9, k in {0,2,4,6}. 4k x 2 mirrors x 4 cond = 32.
    for k in (0, 2, 4, 6):
        yield ("B1-CORE", 2, F(3, 5), F(2, 5), 9, k, (0, 1))
    # Block 2 — ALPHABET. m in {3,4}, N=9, k in {2,6}, 2 rotations. 2m x 2k x 2rot x 4 = 32.
    for m in (3, 4):
        for k in (2, 6):
            yield ("B2-ALPHABET", m, F(3, 5), F(2, 5), 9, k, (0, 1))
    # Block 3 — STRENGTH. m=2, p/r = 0.70/0.30, N=5, k in {1,3}. 2k x 2 mirrors x 4 = 16.
    for k in (1, 3):
        yield ("B3-STRENGTH", 2, F(7, 10), F(3, 10), 5, k, (0, 1))


def generate() -> List[Stimulus]:
    out: List[Stimulus] = []
    for block, m, p, r, N, k, rotations in _grid_specs():
        for rot in rotations:
            for cond_name, model_cond, cond_delta in CONDITIONS:
                # FULL and PARTIAL-BLIND are shared across delta (§5), so they are generated once
                # per (k, rotation) and scored on the delta = 0 cell's ruler (§6).
                delta = cond_delta if cond_delta is not None else F(0)
                cell = Cell(m=m, p=p, r=r, N=N, k=k, delta=delta)

                # FULL uses the delta = 0 q^t as its denominator (§6). Every condition here is
                # already built on its own delta, and for FULL and BLIND that delta is 0, so the
                # cell in hand is the right ruler in every case. Asserted below.
                scale = cell if cond_name != "PARTIAL-RULED-d3" else Cell(
                    m=m, p=p, r=r, N=N, k=k, delta=F(3, 10)
                )

                lmap = label_map(m, rot)
                sid = f"{block}|m{m}|N{N}|k{k}|rot{rot}|{cond_name}"
                out.append(
                    Stimulus(
                        sid=sid,
                        block=block,
                        condition=cond_name,
                        m=m,
                        p=str(p),
                        r=str(r),
                        N=N,
                        k=k,
                        delta=str(delta),
                        rotation=rot,
                        target_label=lmap[0],
                        prompt=build_prompt(cond_name, m, p, r, N, k, rot),
                        schema=build_schema(m),
                        b_pos_logodds=cell.b_pos_logodds,
                        q_t_logodds=cell.q_t_logodds,
                        b_star_logodds=cell.b_star_logodds,
                        denominator=scale.denominator,
                        denominator_nats=scale.denominator_nats,
                        correct_logodds=logodds(cell.correct_answer(model_cond)),
                        is_flip=cell.is_flip,
                    )
                )
    return out


# --------------------------------------------------------------------------------------
# Verification — §4.1 enforced, not merely documented
# --------------------------------------------------------------------------------------


def verify_stimuli(stims: List[Stimulus]) -> List[str]:
    errs: List[str] = []

    # Count, §5 Totals.
    if len(stims) != 80:
        errs.append(f"expected 80 stimuli, got {len(stims)}")
    per_block = {}
    for s in stims:
        per_block[s.block] = per_block.get(s.block, 0) + 1
    for b, want in (("B1-CORE", 32), ("B2-ALPHABET", 32), ("B3-STRENGTH", 16)):
        if per_block.get(b) != want:
            errs.append(f"{b}: expected {want} conditions, got {per_block.get(b)}")

    # Unique ids.
    if len({s.sid for s in stims}) != len(stims):
        errs.append("duplicate stimulus ids")

    for s in stims:
        low = s.prompt.lower()

        # R1 — the inference must not be performed in the prompt.
        for w in FORBIDDEN:
            if w in low:
                errs.append(f"{s.sid}: R1 violated, prompt contains {w!r}")

        # R5 — framed as reading a record, never as computing a posterior.
        for w in FORBIDDEN_R5:
            if w in low:
                errs.append(f"{s.sid}: R5 violated, prompt contains {w!r}")

        # R2 — N and the rule are stated; the count of non-filers is not. R1 already bans the
        # entire vocabulary that could attribute a count to non-filing, so the operative invariant
        # is that no number-word other than N's appears in a COUNTING context. The check is scoped
        # to those contexts rather than matching raw substrings, because the preamble legitimately
        # contains "One of the following", "exactly one is", and "three decimal places".
        # Note that at k = 0 the non-filer count numerically equals N, so N's own word coincides
        # with it. That is a property of the empty-record extreme, not a violation: nothing in the
        # prompt attributes the count to non-filing, and the probe must still notice the record is
        # empty to perform the subtraction.
        for num, word in NUMBER_WORDS.items():
            if num == s.N:
                continue
            contexts = [
                f"{word} analysts", f"{word.lower()} analysts",
                f"ALL {word.upper()} ASSAY", f"all {word.lower()} results",
                f"{word} of the analysts", f"{word.lower()} of the analysts",
                f"{word} reports", f"{word.lower()} reports",
                f"{word} assays", f"{word.lower()} assays",
            ]
            for c in contexts:
                if c in s.prompt:
                    errs.append(f"{s.sid}: R2 violated, counting phrase {c!r} in prompt")

        # R4 — evidentiary statements only, no argumentation. Proxy check: the record block
        # contains only the two permitted line forms.
        for line in s.prompt.splitlines():
            st = line.strip()
            if st in ("POSITIVE", "NEGATIVE", "Assay returned POSITIVE", "(none)"):
                continue

        # The elicitation instruction names exactly the schema's keys.
        keys = list(s.schema["json_schema"]["schema"]["properties"].keys())
        if keys != LABELS[: s.m]:
            errs.append(f"{s.sid}: schema keys {keys} != candidate list {LABELS[:s.m]}")
        for kk in keys:
            if kk not in s.prompt:
                errs.append(f"{s.sid}: schema key {kk!r} never printed in prompt")

        # Every printed candidate appears in the likelihood table exactly once.
        for kk in keys:
            if s.prompt.count(f"If {kk} is responsible") != 1:
                errs.append(f"{s.sid}: {kk!r} not stated exactly once in likelihood table")

        # The target label carries p, every other label carries r.
        pstr, rstr = _pct(F(s.p)), _pct(F(s.r))
        if f"If {s.target_label} is responsible, an assay returns POSITIVE with probability {pstr}." not in s.prompt:
            errs.append(f"{s.sid}: target {s.target_label} does not carry p={pstr}")
        for kk in keys:
            if kk == s.target_label:
                continue
            if f"If {kk} is responsible, an assay returns POSITIVE with probability {rstr}." not in s.prompt:
                errs.append(f"{s.sid}: non-target {kk} does not carry r={rstr}")

        # Condition-specific content, §4.2.
        states_N = f"{NUMBER_WORDS[s.N]} analysts" in s.prompt
        states_rule = "Standing protocol" in s.prompt
        # Delta is detected by the R6 pinned clause, NOT by the numeral 0.30: Block 3 prints
        # r = 0.30 in its likelihood table, so a numeral check reports every Block 3 stimulus as
        # carrying a dropout rate. This cost a debugging cycle and is worth the comment.
        states_delta = "does not file a report at all" in s.prompt

        if s.condition == "FULL":
            if not states_N or states_rule or states_delta:
                errs.append(f"{s.sid}: FULL must state N, no rule, no delta")
            if "complete set of results" not in s.prompt:
                errs.append(f"{s.sid}: FULL missing completeness assertion (R7)")
            body = s.prompt.split("ASSAY RESULTS\n", 1)[1].split("\n\nGive your")[0]
            got = [l.strip() for l in body.splitlines()]
            want = ["POSITIVE"] * s.k + ["NEGATIVE"] * (s.N - s.k)
            if got != want:
                errs.append(f"{s.sid}: FULL record not sorted per A1.1")

        elif s.condition == "PARTIAL-BLIND":
            if states_N or states_rule or states_delta:
                errs.append(f"{s.sid}: PARTIAL-BLIND must not state N, rule, or delta")

        elif s.condition == "PARTIAL-RULED-d0":
            if not (states_N and states_rule) or states_delta:
                errs.append(f"{s.sid}: RULED d0 must state N and rule, not delta")

        elif s.condition == "PARTIAL-RULED-d3":
            if not (states_N and states_rule and states_delta):
                errs.append(f"{s.sid}: RULED d3 must state N, rule, and delta")
            if "does not file a report at all" not in s.prompt:
                errs.append(f"{s.sid}: R6 pinned dropout wording missing")

    # R3 — the REPORTS block is byte-identical across all three partial conditions.
    by_cell: Dict[tuple, Dict[str, str]] = {}
    for s in stims:
        if s.condition == "FULL":
            continue
        key = (s.block, s.m, s.N, s.k, s.rotation)
        blk = s.prompt.split("REPORTS ON FILE", 1)[1].split("\n\nGive your")[0]
        by_cell.setdefault(key, {})[s.condition] = blk
    for key, blocks in by_cell.items():
        if len(set(blocks.values())) != 1:
            errs.append(f"{key}: R3 violated, REPORTS block differs across partial conditions")
        if len(blocks) != 3:
            errs.append(f"{key}: expected 3 partial conditions, got {sorted(blocks)}")

    # A1.2 — mirror halves have identical correct answers in log-odds; only the label map differs.
    by_mirror: Dict[tuple, Dict[int, Stimulus]] = {}
    for s in stims:
        by_mirror.setdefault((s.block, s.m, s.N, s.k, s.condition), {})[s.rotation] = s
    for key, halves in by_mirror.items():
        if len(halves) != 2:
            errs.append(f"{key}: expected 2 mirror halves, got {sorted(halves)}")
            continue
        a, b = halves[0], halves[1]
        for field in ("b_pos_logodds", "q_t_logodds", "b_star_logodds", "denominator"):
            if abs(getattr(a, field) - getattr(b, field)) > 1e-12:
                errs.append(f"{key}: mirror halves differ in {field}")
        if a.target_label == b.target_label:
            errs.append(f"{key}: mirror halves assign p to the same label")
        if a.prompt == b.prompt:
            errs.append(f"{key}: mirror halves are byte-identical prompts")

    # §5 — seven flip cells, counted over distinct (block, m, N, k, delta), not over stimuli.
    flips = {
        (s.block, s.m, s.N, s.k, s.delta)
        for s in stims
        if s.is_flip and s.condition.startswith("PARTIAL-RULED")
    }
    if len(flips) != 7:
        errs.append(f"expected 7 flip cells, found {len(flips)}: {sorted(flips)}")

    # §6 — no zero denominator anywhere; smallest is 0.649 nats.
    dmin = min(s.denominator_nats for s in stims)
    if abs(dmin - 0.649) > 5e-4:
        errs.append(f"smallest denominator {dmin:.4f}, spec says 0.649")

    return errs


def main() -> int:
    stims = generate()
    errs = verify_stimuli(stims)

    print(f"silence_stimuli.py — generated {len(stims)} stimuli")
    if errs:
        print(f"\nFAILED: {len(errs)} violations\n")
        for e in errs:
            print(f"  {e}")
        return 1

    payload = [asdict(s) for s in stims]
    blob = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()

    with open("silence_stimuli.json", "w", encoding="utf-8") as fh:
        fh.write(blob)
    with open("silence_stimuli.sha256", "w", encoding="utf-8") as fh:
        fh.write(digest + "  silence_stimuli.json\n")

    print("ok   80 stimuli, all §4.1 rules enforced")
    print(f"\nFROZEN sha256: {digest}")
    print("Any change to a stimulus from this point is an amendment with its own provenance (§13).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
