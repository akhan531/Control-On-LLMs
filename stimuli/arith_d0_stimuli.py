"""arith_d0_stimuli.py — ARITHMETIC CONTROL at delta = 0 (approved by Ali 2026-08-17).

Completes the only closable identification/interpretation ladder in the design:

    PARTIAL_RULED (frozen, on disk)   identify the absences + substitute + aggregate
    ARITH_D0      (this file)         substitute + aggregate      (absences enumerated)
    FULL          (frozen, on disk)   aggregate only              (negatives printed)

All three share the correct answer b* per cell: q(0) = b* exactly (the pivot), and
enumerating non-filings changes nothing normative because at delta = 0 a non-filing
IS a certain negative. At delta > 0 no FULL rung can exist (printing true results
would change the correct answer) — this ladder closes at delta = 0 only.

Construction: the frozen PARTIAL_RULED prompt with ONLY the record block replaced —
byte-identical prefix through the filing rule, byte-identical elicitation, record
lines byte-identical in wording to ARITH_D30's ("Filed nothing at all"), record
header and completeness sentence byte-identical to ARITH_D30's. Record length is N
lines, matching FULL's record length; RULED remains the short arm.

Rule compliance (v2 spec section 7):
  R1 DELIBERATELY VIOLATED, recorded, exactly as ARITH_D30: the record points at the
     omissions, which is the condition. No string on the frozen FORBIDDEN list occurs.
  R3/R4/R5 hold; elicitation byte-identical to frozen.
  R7 analogue: completeness of the filing record asserted explicitly.
  NO dropout clause — this is delta = 0; asserted absent.

Build-time assertions:
  * 28 stimuli (14 cells x 2 mirrors), unique ids
  * per cell and mirror, expected answer identical FIELD BY FIELD to the frozen
    PARTIAL_RULED stimulus (correct answer b*, unchanged by enumeration)
  * byte-identical prefix and elicitation; k POSITIVE lines; N-k filed-nothing lines;
    record block totals N lines; differs from both frozen RULED and FULL prompts
  * posterior recomputed exactly from silence_v2_model: q(p,N,k,0) == b_star as
    rationals, matches frozen belief_target and level_target
  * section 5.5: level(b_pos) != level(b_star) for every cell, asserted here again
  * mirror is a pure relabelling

    python scratch_2_4c/example_2/arith_d0_stimuli.py            # build + freeze, prints sha256
    python scratch_2_4c/example_2/arith_d0_stimuli.py --show A1  # print prompts for one cell
"""

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
RULED_FILE = f"{ROOT}/silence_v2_stimuli.json"
OUT = f"{ROOT}/scratch_2_4c/example_2/arith_d0_stimuli.json"
CONDITION = "ARITH_D0"

POS_LINE = "    Assay returned POSITIVE"
NONE_LINE = "    Filed nothing at all"


def record_block(N, k):
    # byte-identical wording to arith_d30_stimuli.record_block
    lines = [POS_LINE] * k + [NONE_LINE] * (N - k)
    return (f"\nCOMPLETE FILING RECORD, ALL {N} ANALYSTS\n"
            + "\n".join(lines) + "\n"
            + "Each analyst appears exactly once above.\n")


def load_frozen():
    stims = json.load(open(RULED_FILE))["stimuli"]
    ruled = {(s["cell"], s["target_is_first"]): s
             for s in stims if s["condition"] == "PARTIAL_RULED"}
    full = {(s["cell"], s["target_is_first"]): s
            for s in stims if s["condition"] == "FULL"}
    return ruled, full


def build():
    ruled, _ = load_frozen()
    cells = {c["id"]: c for c in M.build()}
    out = []
    for (cell, target_is_first), b in sorted(
            ruled.items(), key=lambda kv: (kv[0][0], not kv[0][1])):
        c = cells[cell]
        N, k = c["N"], c["k"]
        prefix = b["prompt"].split("\nREPORTS ON FILE\n")[0]
        elic = S.elicitation(*S.LABELS)
        assert b["prompt"].endswith(elic), f"{cell}: frozen elicitation drifted"

        stim = dict(b)   # inherit every frozen field, then override what differs
        stim.update({
            "id": f"{cell}-{CONDITION}-m{0 if target_is_first else 1}",
            "condition": CONDITION,
            "prompt": prefix + record_block(N, k) + elic,
            "response_format": S.schema(),
        })
        out.append(stim)
    return out


def check(stims):
    ruled, full = load_frozen()
    cells = {c["id"]: c for c in M.build()}
    assert len(stims) == 28, f"expected 28 stimuli, got {len(stims)}"
    assert len({s["id"] for s in stims}) == 28

    for s in stims:
        low = s["prompt"].lower()
        for w in S.FORBIDDEN:                                       # R1 letter
            assert w not in low, f"{s['id']}: forbidden term {w!r}"
        assert "analyst 1" not in low and "assay 1" not in low       # R3
        assert "reply with only a json object" in low

        c = cells[s["cell"]]
        N, k = c["N"], c["k"]
        assert s["prompt"].count(POS_LINE) == k, f"{s['id']}: POSITIVE line count"
        assert s["prompt"].count(NONE_LINE) == N - k, f"{s['id']}: filed-nothing count"
        assert f"COMPLETE FILING RECORD, ALL {N} ANALYSTS" in s["prompt"]
        assert "Each analyst appears exactly once above." in s["prompt"]
        assert "files a report only" in low                          # rule present
        assert "percent of cases" not in low                         # NO dropout: d=0
        assert "complete results" not in low                         # not FULL's header

        b = ruled[(s["cell"], s["target_is_first"])]
        # identical correct answer, field by field -- the pivot assertion
        for fld in ("expected_candidate", "expected_confidence", "level_target",
                    "belief_target", "belief_first", "l_pos_target", "l_q_target",
                    "target_label", "N", "k", "p", "group", "banked"):
            assert s[fld] == b[fld], f"{s['id']}: {fld} differs from frozen RULED"
        # byte-identical prefix through the rule line, identical elicitation
        pref = b["prompt"].split("\nREPORTS ON FILE\n")[0]
        assert s["prompt"].startswith(pref), f"{s['id']}: shared prefix broken"
        assert s["prompt"].endswith(S.elicitation(*S.LABELS))
        # differs from both neighbours on the ladder
        assert s["prompt"] != b["prompt"], f"{s['id']}: identical to RULED"
        f_stim = full[(s["cell"], s["target_is_first"])]
        assert s["prompt"] != f_stim["prompt"], f"{s['id']}: identical to FULL"
        # posterior recomputed exactly: q(0) == b* over rationals, matches frozen
        q0 = M.q(c["p"], N, k, F(0))
        assert q0 == c["b_star"], f"{s['id']}: pivot broken"
        assert s["belief_target"] == round(float(q0), 6), f"{s['id']}: q(0) mismatch"
        assert M.level(q0) == s["level_target"], f"{s['id']}: level mismatch"
        # section 5.5, asserted explicitly for every cell in this arm
        assert M.level(c["b_pos"]) != M.level(c["b_star"]), \
            f"{s['id']}: non-discriminating cell"
        # frame round-trip
        assert S.target_level(s["expected_candidate"], s["expected_confidence"],
                              s["target_label"]) == s["level_target"]

    # mirror is a pure relabelling
    for cell in {s["cell"] for s in stims}:
        pair = [s for s in stims if s["cell"] == cell]
        assert len(pair) == 2
        assert pair[0]["expected_confidence"] == pair[1]["expected_confidence"]
        assert pair[0]["expected_candidate"] != pair[1]["expected_candidate"]
        assert pair[0]["level_target"] == pair[1]["level_target"]
    return True


def freeze(stims):
    payload = {"task": "2.4c ARITH_D0 arithmetic control at delta=0",
               "note": ("enumerated non-filings, delta=0; correct answer b* "
                        "identical to frozen PARTIAL_RULED and FULL; approved "
                        "2026-08-17"),
               "wording": S.CONF, "labels": list(S.LABELS),
               "conditions": [CONDITION],
               "n_cells": len({s["cell"] for s in stims}),
               "n_stimuli": len(stims), "stimuli": stims}
    blob = json.dumps(payload, indent=2, sort_keys=True)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    payload["sha256"] = digest
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with open(OUT.replace(".json", ".sha256"), "w") as f:
        f.write(f"{digest}  arith_d0_stimuli.json\n")
    return digest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", default=None)
    args = ap.parse_args()

    M.verify(M.build())
    stims = build()
    check(stims)
    digest = freeze(stims)

    if args.show:
        for s in stims:
            if s["cell"] == args.show:
                print("#" * 72)
                print(f"{s['id']}   expected: {s['expected_confidence']} / "
                      f"{s['expected_candidate']}   (target level {s['level_target']})")
                print("#" * 72)
                print(s["prompt"])
        raise SystemExit

    print(f"ARITH_D0: {len(stims)} stimuli, "
          f"{len({s['cell'] for s in stims})} cells, frozen")
    print(f"sha256 {digest}")
    print(f"run size: {len(stims)} x 5 draws x 7 configs = {len(stims)*5*7} calls")
