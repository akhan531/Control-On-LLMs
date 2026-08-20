"""arith_d30_stimuli.py — ARITHMETIC CONTROL at delta = 0.30 (authorised 2026-08-16).

FRAMING (corrected 2026-08-16, per Ali): this is NOT the delta>0 analogue of FULL.
At delta=0, FULL prints the actual NEGATIVE results and removes all silence
interpretation; at delta>0 that is structurally impossible — printing true assay
results would change the correct answer to b*, because a non-filer either had a
negative assay or dropped out and nobody can know which. ARITH_D30 removes ONLY the
step of identifying WHICH analysts are absent (N minus k); interpreting each
enumerated absence under the 30% dropout rate is still required, which is why the
correct answer remains q(0.30), identical to PARTIAL_RULED_D30's. The delta=0.30
coupling figure is therefore NOT comparable to the delta=0 FULL->RULED coupling, and
that hole is unclosable by any condition, not future work.

Same 9 banked-viable cells, both mirrors. The filing outcome of every analyst is
displayed, one line per analyst; the stated rule and dropout rate are byte-identical
to PARTIAL_RULED_D30's.

    python scratch_fable/arith_d30_stimuli.py           # writes stimuli + sha256
    python scratch_fable/arith_d30_stimuli.py --show A1

Rule compliance (v2 spec section 7):
  R1 is DELIBERATELY VIOLATED: the record must print "Filed nothing at all", which is
     silence vocabulary in function even though no string on the frozen FORBIDDEN
     list appears. Pointing at the omissions IS the condition, exactly as the v1 spec
     section 10 defined the arithmetic control. Recorded as a violation, not excused.
  R3 no analyst identifiers; record lines are interchangeable.
  R4/R5 no argumentation, no probability vocabulary in the instruction; the
     elicitation block is byte-identical to the frozen one.
  R6 dropout clause byte-identical to the frozen banked wording.
  R7 analogue: completeness of the filing record is asserted explicitly.

Build-time assertions (pivot discipline, as silence_v2_stimuli.check):
  * per cell and mirror, expected answer identical to the frozen banked
    PARTIAL_RULED_D30 stimulus, field by field
  * prompt shares a byte-identical prefix with the banked prompt through the dropout
    clause, and a byte-identical elicitation suffix; only the record block differs
  * posterior recomputed exactly from silence_v2_model matches the frozen value
  * k POSITIVE lines and N-k filed-nothing lines, counted
  * mirror is a pure relabelling
"""
import argparse
import hashlib
import json
import sys

sys.path.insert(0, "/Users/alikhan/Documents/GitHub/Control-On-LLMs")
import silence_v2_model as M
import silence_v2_stimuli as S

ROOT = "/Users/alikhan/Documents/GitHub/Control-On-LLMs"
OUT = f"{ROOT}/scratch_fable/arith_d30_stimuli.json"
CONDITION = "ARITH_D30"
BANKED_FILE = f"{ROOT}/silence_v2_stimuli_banked.json"

POS_LINE = "    Assay returned POSITIVE"
NONE_LINE = "    Filed nothing at all"


def record_block(N, k):
    lines = [POS_LINE] * k + [NONE_LINE] * (N - k)
    return (f"\nCOMPLETE FILING RECORD, ALL {N} ANALYSTS\n"
            + "\n".join(lines) + "\n"
            + "Each analyst appears exactly once above.\n")


def build():
    banked = {(s["cell"], s["target_is_first"]): s
              for s in json.load(open(BANKED_FILE))["stimuli"]}
    cells = {c["id"]: c for c in M.build() if M.banked_viable(c)}
    out = []
    for (cell, target_is_first), b in sorted(banked.items(),
                                             key=lambda kv: (kv[0][0], not kv[0][1])):
        c = cells[cell]
        N, k = c["N"], c["k"]
        first, second = S.LABELS
        p = c["p"]
        p_first = p if target_is_first else 1 - p

        # byte-identical prefix: everything in the banked prompt above its record block
        prefix = b["prompt"].split("\nREPORTS ON FILE\n")[0]
        elic = S.elicitation(first, second)
        assert b["prompt"].endswith(elic), f"{cell}: banked elicitation drifted"

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
    banked = {(s["cell"], s["target_is_first"]): s
              for s in json.load(open(BANKED_FILE))["stimuli"]}
    assert len(stims) == 18, f"expected 18 stimuli, got {len(stims)}"
    assert len({s["id"] for s in stims}) == 18

    for s in stims:
        low = s["prompt"].lower()
        for w in S.FORBIDDEN:                                          # R1 letter
            assert w not in low, f"{s['id']}: forbidden term {w!r}"
        assert "analyst 1" not in low and "assay 1" not in low          # R3
        assert "reply with only a json object" in low

        c = next(x for x in M.build() if x["id"] == s["cell"])
        N, k = c["N"], c["k"]
        assert s["prompt"].count(POS_LINE) == k, f"{s['id']}: POSITIVE line count"
        assert s["prompt"].count(NONE_LINE) == N - k, f"{s['id']}: filed-nothing count"
        assert f"COMPLETE FILING RECORD, ALL {N} ANALYSTS" in s["prompt"]
        assert "files a report only" in low                             # rule present
        assert "percent of cases" in low                                # R6 wording

        b = banked[(s["cell"], s["target_is_first"])]
        # identical correct answer, field by field -- the pivot assertion
        for f in ("expected_candidate", "expected_confidence", "level_target",
                  "belief_target", "belief_first", "l_pos_target", "l_q_target",
                  "target_label", "N", "k", "p"):
            assert s[f] == b[f], f"{s['id']}: {f} differs from banked RULED_D30"
        # byte-identical prefix through the dropout clause, identical elicitation
        pref = b["prompt"].split("\nREPORTS ON FILE\n")[0]
        assert s["prompt"].startswith(pref), f"{s['id']}: shared prefix broken"
        assert s["prompt"].endswith(S.elicitation(*S.LABELS))
        # posterior recomputed exactly
        q = M.q(c["p"], N, k, M.DELTA_BANKED)
        assert round(float(q if s["target_is_first"] or True else q), 6) == \
            round(float(q), 6)
        assert s["belief_target"] == round(float(q), 6), f"{s['id']}: q mismatch"
        assert M.level(q) == s["level_target"], f"{s['id']}: level mismatch"
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", default=None)
    args = ap.parse_args()

    M.verify(M.build())
    stims = build()
    check(stims)

    if args.show:
        for s in stims:
            if s["cell"] == args.show:
                print("#" * 72)
                print(f"{s['id']}   expected: {s['expected_confidence']} / "
                      f"{s['expected_candidate']}   (target level {s['level_target']})")
                print("#" * 72)
                print(s["prompt"])
        raise SystemExit

    digest = S.freeze(stims, OUT, "ARITHMETIC CONTROL delta=0.30, authorised "
                                  "2026-08-16; delta>0 analogue of FULL")
    with open(f"{ROOT}/scratch_fable/arith_d30_stimuli.sha256", "w") as f:
        f.write(digest + "\n")
    print(f"{len(stims)} stimuli, {len({s['cell'] for s in stims})} cells")
    print(f"sha256 {digest}")
    print(f"run size: {len(stims)} x 5 draws x 7 configs = {len(stims) * 5 * 7} calls")
