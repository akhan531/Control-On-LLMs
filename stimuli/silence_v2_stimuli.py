"""
silence_v2_stimuli.py — stimulus generator for the silence probe v2 (Task 2.4b, W2).

    python silence_v2_stimuli.py            # writes primary + banked, prints hashes
    python silence_v2_stimuli.py --show A1  # print every prompt for one cell

Three active conditions on an identical underlying record:

  FULL           all N results displayed, completeness asserted, no rule.
                 Correct answer: b*.
  PARTIAL_BLIND  the k POSITIVE reports only. N is not stated and the rule is not
                 stated. Correct answer: b_pos.
  PARTIAL_RULED  the same k reports, with N and the filing rule stated. Correct
                 answer: q(delta=0), which equals b* exactly.

FULL and PARTIAL_RULED therefore have the SAME correct answer and differ only in
whether the negatives are displayed or must be inferred from their absence. That
difference is the entire measurement.

A fourth condition, PARTIAL_RULED at delta = 0.30, is DESIGNED AND BANKED, NOT RUN
(D26). It is emitted to a SEPARATE file with its own hash, so enabling it later cannot
disturb the hash the pre-registration was frozen against.

Binding prompt rules, asserted at build time
--------------------------------------------
R1  No silence vocabulary anywhere. The observer must notice the absence itself; the
    prompt must never point at it.
R2  PARTIAL_BLIND states neither N nor the rule.
R3  No analyst identifiers in any record. Reports are interchangeable lines.
R4  No argumentation, no hints, no worked reasoning.
R5  The task is framed as reading a record, never as computing a posterior. No
    probability vocabulary in the instruction.
R6  The banked dropout clause is phrased as a filing rate, never as unreliability,
    incompetence, or suppression.
R7  FULL displays all N results and asserts completeness explicitly, so that failure
    there is arithmetic and not an inference about coverage.
"""

import argparse
import hashlib
import json
from fractions import Fraction as F

import silence_v2_model as M

LABELS = ("SIGMA", "THETA")
CONF = {"low": "Somewhat confident", "high": "Very confident"}   # wording B, D22
ACTIVE = ("FULL", "PARTIAL_BLIND", "PARTIAL_RULED")
BANKED = "PARTIAL_RULED_D30"

FORBIDDEN = ("silent", "silence", "absent", "absence", "missing", "did not report",
             "no report", "nothing was filed", "unreported", "withheld", "omitted",
             "posterior", "bayes", "prior probability", "likelihood ratio",
             "probability that", "update your", "calculate", "compute")


# ---------------------------------------------------------------- prompt parts

def preamble(first, second, p_first, p_second):
    return (
        "One of the following is responsible for the contamination event. "
        "Exactly one is.\n"
        "\n"
        f"    Candidate {first}\n"
        f"    Candidate {second}\n"
        "\n"
        "Before any testing, each candidate is considered equally likely.\n"
    )


def assays(first, second, p_first, p_second, N=None):
    who = f"{N} analysts were" if N is not None else "Analysts were"
    return (
        "\n"
        f"{who} each assigned a different assay. Each assay returns POSITIVE or\n"
        "NEGATIVE, and the assays have the following known characteristics:\n"
        "\n"
        f"    If {first} is responsible, an assay returns POSITIVE with probability "
        f"{float(p_first):.2f}.\n"
        f"    If {second} is responsible, an assay returns POSITIVE with probability "
        f"{float(p_second):.2f}.\n"
        "\n"
        "Assay results are independent of one another given which candidate is "
        "responsible.\n"
    )


def elicitation(first, second):
    return (
        "\n"
        "Name the candidate you believe is responsible, and how strongly you hold "
        "that.\n"
        "\n"
        "Reply with only a JSON object with keys \"candidate\" and \"confidence\".\n"
        f"\"candidate\" must be exactly {first} or {second}.\n"
        f"\"confidence\" must be exactly {CONF['low']} or {CONF['high']}.\n"
    )


def prompt(condition, N, k, first, second, p_first, p_second, delta=None):
    head = preamble(first, second, p_first, p_second)

    if condition == "FULL":
        # R7: every result displayed, completeness asserted. A1.1: sorted, POSITIVE first.
        body = assays(first, second, p_first, p_second, N)
        lines = ["    Assay returned POSITIVE"] * k + \
                ["    Assay returned NEGATIVE"] * (N - k)
        body += (f"\nCOMPLETE RESULTS, ALL {N} ASSAYS\n" + "\n".join(lines) + "\n")

    elif condition == "PARTIAL_BLIND":
        # R2: no N, no rule.
        body = assays(first, second, p_first, p_second, None)
        body += ("\nREPORTS ON FILE\n" +
                 "\n".join(["    Assay returned POSITIVE"] * k) + "\n")

    else:
        body = assays(first, second, p_first, p_second, N)
        body += "\nEach analyst files a report only when their assay returns POSITIVE.\n"
        if condition == BANKED:
            # R6: a filing rate, not a competence claim.
            body += (f"Separately from the assay result, each analyst files nothing "
                     f"at all\nin {round(float(delta) * 100)} percent of cases.\n")
        body += ("\nREPORTS ON FILE\n" +
                 "\n".join(["    Assay returned POSITIVE"] * k) + "\n")

    return head + body + elicitation(first, second)


def schema():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "silence_probe_v2_ordinal", "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "candidate": {"type": "string", "enum": list(LABELS)},
                    "confidence": {"type": "string",
                                   "enum": [CONF["low"], CONF["high"]]},
                },
                "required": ["candidate", "confidence"],
                "additionalProperties": False,
            },
        },
    }


# ---------------------------------------------------------------- answers

def answer_from_p_first(p_first):
    """Correct (candidate, confidence) given P(first-printed label)."""
    lv = M.level(p_first)
    first, second = LABELS
    return ((first if lv >= 2 else second),
            (CONF["high"] if lv in (0, 3) else CONF["low"]),
            lv)


def target_level(candidate, confidence, target_label):
    """
    Map a raw answer to a TARGET-frame level, which is mirror-invariant and is the
    frame ordinal-s is defined in. Used by the analyser; stored here so the mapping
    lives with the stimuli that define it.
    """
    names_target = (candidate == target_label)
    high = (confidence == CONF["high"])
    if names_target:
        return 3 if high else 2
    return 0 if high else 1


def targets_for(c):
    return {"FULL": c["b_star"],
            "PARTIAL_BLIND": c["b_pos"],
            "PARTIAL_RULED": c[f"q_{M.DELTA_PRIMARY}"],
            BANKED: c[f"q_{M.DELTA_BANKED}"]}


def build(conditions):
    cells = M.build()
    out = []
    for c in cells:
        p = c["p"]
        tgts = targets_for(c)
        for target_is_first in (True, False):          # A1.2 mirror
            first, second = LABELS
            target_label = first if target_is_first else second
            p_first = p if target_is_first else 1 - p
            p_second = 1 - p_first
            l_pos_t = M.level(c["b_pos"])              # target frame, mirror-invariant
            for cond in conditions:
                tv = tgts[cond]
                pf = tv if target_is_first else 1 - tv
                cand, conf, lv_print = answer_from_p_first(pf)
                denom_d = (M.DELTA_BANKED if cond == BANKED else M.DELTA_PRIMARY)
                l_q_t = M.level(c[f"q_{denom_d}"])
                out.append({
                    "id": f"{c['id']}-{cond}-m{0 if target_is_first else 1}",
                    "cell": c["id"], "condition": cond,
                    "group": c["id"][0],
                    "target_is_first": target_is_first,
                    "target_label": target_label,
                    "p": float(p), "N": c["N"], "k": c["k"],
                    "belief_target": round(float(tv), 6),
                    "belief_first": round(float(pf), 6),
                    "level_print": lv_print,
                    "level_target": M.level(tv),
                    "l_pos_target": l_pos_t,
                    "l_q_target": l_q_t,
                    "expected_candidate": cand, "expected_confidence": conf,
                    "banked": cond == BANKED,
                    "prompt": prompt(cond, c["N"], c["k"], first, second,
                                     p_first, p_second,
                                     M.DELTA_BANKED if cond == BANKED else None),
                    "response_format": schema(),
                })
    return out


# ---------------------------------------------------------------- checks

def check(stims):
    assert len({s["id"] for s in stims}) == len(stims), "duplicate id"

    for s in stims:
        low = s["prompt"].lower()
        for w in FORBIDDEN:                                        # R1, R4, R5
            assert w not in low, f"{s['id']}: forbidden term {w!r}"
        assert "analyst 1" not in low and "assay 1" not in low      # R3
        assert "reply with only a json object" in low               # single instruction

        if s["condition"] == "PARTIAL_BLIND":                       # R2
            assert str(s["N"]) not in s["prompt"].split("REPORTS")[0].replace(
                f"{s['p']:.2f}", ""), f"{s['id']}: N leaked into BLIND"
            assert "files a report only" not in low, f"{s['id']}: rule leaked"
            assert "complete results" not in low
        if s["condition"] == "FULL":                                # R7
            assert f"COMPLETE RESULTS, ALL {s['N']} ASSAYS" in s["prompt"]
            assert s["prompt"].count("NEGATIVE\n") >= 1 or s["N"] == s["k"]
            assert "files a report only" not in low, f"{s['id']}: rule in FULL"
        if s["condition"].startswith("PARTIAL_RULED"):
            assert "files a report only" in low
            assert "complete results" not in low
        if s["condition"] == BANKED:                                # R6
            assert "percent of cases" in low
            for w in ("unreliab", "incompet", "careless", "suppress", "hides"):
                assert w not in low

        # record length matches k
        assert s["prompt"].count("Assay returned POSITIVE") == s["k"]
        if s["condition"] == "FULL":
            assert s["prompt"].count("Assay returned NEGATIVE") == s["N"] - s["k"]

        # every ordinal-s denominator is non-zero
        assert s["l_q_target"] != s["l_pos_target"], f"{s['id']}: zero denominator"

        # the expected answer round-trips through the target-frame mapping
        rt = target_level(s["expected_candidate"], s["expected_confidence"],
                          s["target_label"])
        assert rt == s["level_target"], f"{s['id']}: frame round-trip failed"

    # FULL and PARTIAL_RULED must agree on the correct answer, per cell and mirror
    by = {}
    for s in stims:
        by[(s["cell"], s["condition"], s["target_is_first"])] = s
    for (cell, cond, m), s in list(by.items()):
        if cond != "FULL":
            continue
        r = by.get((cell, "PARTIAL_RULED", m))
        if r is None:
            continue
        assert (s["expected_candidate"], s["expected_confidence"]) == \
               (r["expected_candidate"], r["expected_confidence"]), \
               f"{cell}/m{0 if m else 1}: FULL and RULED disagree -- pivot broken"
        assert s["prompt"] != r["prompt"]

    # mirror is a pure relabelling: same confidence, flipped candidate
    for cell in {s["cell"] for s in stims}:
        for cond in {s["condition"] for s in stims}:
            pair = [s for s in stims if s["cell"] == cell and s["condition"] == cond]
            if len(pair) != 2:
                continue
            assert pair[0]["expected_confidence"] == pair[1]["expected_confidence"]
            assert pair[0]["expected_candidate"] != pair[1]["expected_candidate"]
            assert pair[0]["level_target"] == pair[1]["level_target"]
    return True


def freeze(stims, path, note):
    payload = {"task": "2.4b silence probe v2", "note": note,
               "wording": CONF, "labels": list(LABELS),
               "conditions": sorted({s["condition"] for s in stims}),
               "n_cells": len({s["cell"] for s in stims}),
               "n_stimuli": len(stims), "stimuli": stims}
    blob = json.dumps(payload, indent=2, sort_keys=True)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    payload["sha256"] = digest
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return digest


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", default=None)
    args = ap.parse_args()

    M.verify(M.build())

    primary = build(ACTIVE)
    check(primary)
    h1 = freeze(primary, "silence_v2_stimuli.json", "PRIMARY, delta=0 only")

    banked_cells = {c["id"] for c in M.build() if M.banked_viable(c)}
    banked = [s for s in build((BANKED,)) if s["cell"] in banked_cells]
    check(banked)
    h2 = freeze(banked, "silence_v2_stimuli_banked.json",
                "BANKED delta=0.30 extension, designed not run (D26)")

    if args.show:
        for s in primary:
            if s["cell"] == args.show and s["target_is_first"]:
                print("#" * 72)
                print(f"{s['id']}   expected: {s['expected_confidence']} / "
                      f"{s['expected_candidate']}   (target level {s['level_target']}, "
                      f"s endpoints {s['l_pos_target']} -> {s['l_q_target']})")
                print("#" * 72)
                print(s["prompt"])
        raise SystemExit

    print(f"PRIMARY  {len(primary)} stimuli, "
          f"{len({s['cell'] for s in primary})} cells, {len(ACTIVE)} conditions")
    print(f"         sha256 {h1}")
    print(f"BANKED   {len(banked)} stimuli, {len(banked_cells)} cells (delta=0.30)")
    print(f"         sha256 {h2}")
    print(f"\nrun size: {len(primary)} x 5 draws x 7 configs = {len(primary)*5*7} calls")
    print(f"banked:   {len(banked)} x 5 x 7 = {len(banked)*5*7} calls if enabled")
    print("\nper-cell expected answers (mirror 0, target printed first):")
    print(f"{'cell':<5}{'FULL':>26}{'BLIND':>26}{'RULED':>26}")
    order = {c: i for i, c in enumerate(ACTIVE)}
    for cell in [c["id"] for c in M.build()]:
        row = {s["condition"]: s for s in primary
               if s["cell"] == cell and s["target_is_first"]}
        print(f"{cell:<5}" + "".join(
            f"{row[c]['expected_confidence'] + ' / ' + row[c]['expected_candidate']:>26}"
            for c in ACTIVE))
