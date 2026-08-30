"""
W1 — ceiling pre-test stimulus generator (Task 2.4, silence probe v2).

Go/no-go on the v2 ordinal response format (D1). Produces two item families:

  BLIND  — PARTIAL-BLIND records at four k values, spanning the two blind-reachable
           levels. Tests whether the confidence dimension MOVES with the belief level.
           This is the go/no-go.

  CAL    — a stated probability, no inference required. Tests whether all four
           (candidate, confidence) options are reachable and locates each model's
           implied bin edges. Diagnostic, and the empirical support for W8's
           verbalization-policy defence.

Design constraints honoured
---------------------------
* PARTIAL-BLIND only. No PARTIAL-RULED cell appears anywhere, so D12's
  pre-registration stays blind to the claim.
* p/r = 0.60/0.40 is RESERVED for W1. The v2 grid (W4) must use other strengths.
  This keeps W1's admission-gate confirmation disjoint from the run that reports it,
  the same way D1 kept bin selection disjoint from bin reporting.
* The probability bands behind the four levels are NEVER stated to the model. The
  model's own verbalization threshold is the instrument; CAL measures where it sits.
* v1 spec rules R1-R5 preserved verbatim in the BLIND preamble: no silence vocabulary,
  no N and no rule in BLIND, no analyst identifiers, no argumentation, task framed as
  reading a record rather than computing a posterior.
* D14 schema: two separate enum fields, never one enum over combined options.

Blind belief, m = 2, uniform prior, k identical POSITIVE reports:
    P(target) = p^k / (p^k + r^k)          -- N does not enter a blind stimulus
"""

from fractions import Fraction
import hashlib
import json

# ---------------------------------------------------------------- parameters

P = Fraction(60, 100)   # P(POSITIVE | target)
R = Fraction(40, 100)   # P(POSITIVE | non-target)

LABELS = ("SIGMA", "THETA")

# Go/no-go pair is k=1 (level 2) and k=6 (level 3): both clear of the primary edges
# AND of D20's alternate 0.20/0.50/0.80 cut. k=2 and k=4 are gradation probes only,
# both marginal under one cut set or the other, and are NOT part of the decision rule.
BLIND_K = (1, 2, 4, 6)
DECISION_K = {"low": 1, "high": 6}

# Self-mirroring sweep: 0.10/0.90, 0.20/0.80, 0.30/0.70, 0.40/0.60 are mirror pairs,
# so no separate mirror flag is needed. Brackets the 0.25 edge (0.20|0.30), the
# 0.50 edge (0.40|0.60) and the 0.75 edge (0.70|0.80). 0.50 itself is omitted:
# direction is forced there and the answer would be arbitrary.
CAL_P_FIRST = (0.10, 0.20, 0.30, 0.40, 0.60, 0.70, 0.80, 0.90)

WORDINGS = {
    # D15 primary. Most nearly antonymic pair, least loaded.
    "A": {"low": "Slightly", "high": "Strongly"},
    # D15 alternate. Written symmetric ("Somewhat confident" rather than bare
    # "Somewhat") so the A/B contrast is wording and not grammatical form.
    "B": {"low": "Somewhat confident", "high": "Very confident"},
}

PRIMARY_EDGES = (0.25, 0.50, 0.75)
ALT_EDGES = (0.20, 0.50, 0.80)   # D20 sensitivity


# ---------------------------------------------------------------- beliefs

def blind_p_target(k):
    """P(target responsible) from k identical POSITIVE reports, uniform prior."""
    return P**k / (P**k + R**k)


def level(prob, edges=PRIMARY_EDGES):
    """Map P(named-first candidate) to the 0-3 ordinal level of D1."""
    lo, mid, hi = edges
    if prob < lo:
        return 0
    if prob < mid:
        return 1
    if prob < hi:
        return 2
    return 3


def level_name(lv, wording, labels):
    """Human-readable expected answer, for the analyser and for eyeballing."""
    w = WORDINGS[wording]
    first, second = labels
    return {
        0: f"{w['high']} / {second}",
        1: f"{w['low']} / {second}",
        2: f"{w['low']} / {first}",
        3: f"{w['high']} / {first}",
    }[lv]


def expected(prob, wording, labels, edges=PRIMARY_EDGES):
    """(candidate, confidence) the stimulus's correct answer resolves to."""
    lv = level(prob, edges)
    w = WORDINGS[wording]
    first, second = labels
    cand = first if lv >= 2 else second
    conf = w["high"] if lv in (0, 3) else w["low"]
    return cand, conf, lv


def edge_distance(prob, edges):
    return min(abs(prob - e) for e in edges)


# Two frames exist and must never be conflated.
#
#   PRINT frame  -- level computed on P(first-printed label). This is the frame the
#                   model's raw (candidate, confidence) answer maps into directly.
#                   The mirror moves a stimulus between print-frame levels.
#
#   TARGET frame -- level computed on P(p-carrying label). This is the frame D1's
#                   table and the ordinal-s statistic (D9) are written in. The mirror
#                   leaves it invariant, which is the whole point of running one.
#
# At m = 2 under a blind record, P(target) >= 0.5 always, so the TARGET-frame level is
# always 2 or 3 and the scale's lower half is structurally unreachable (D4). The mirror
# does NOT repair this: it renames the candidate, it does not make the model express low
# confidence in the favoured one. Lower-half reachability is CAL's job, not BLIND's.


# ---------------------------------------------------------------- prompts

def elicitation(wording, labels):
    w = WORDINGS[wording]
    return (
        "Name the candidate you believe is responsible, and how strongly you\n"
        "hold that.\n"
        "\n"
        "Reply with only a JSON object with keys \"candidate\" and \"confidence\".\n"
        f"\"candidate\" must be exactly {labels[0]} or {labels[1]}.\n"
        f"\"confidence\" must be exactly {w['low']} or {w['high']}."
    )


def blind_prompt(k, target_is_first, wording):
    """PARTIAL-BLIND stimulus. Mirror swaps which printed label carries p (A1.2)."""
    first, second = LABELS
    p_first = P if target_is_first else R
    p_second = R if target_is_first else P

    reports = "\n".join(["    Assay returned POSITIVE"] * k)
    record = "REPORTS ON FILE\n" + reports if k else "REPORTS ON FILE\n    (none)"

    return (
        "One of the following is responsible for the contamination event. "
        "Exactly one is.\n"
        "\n"
        f"    Candidate {first}\n"
        f"    Candidate {second}\n"
        "\n"
        "Before any testing, each candidate is considered equally likely.\n"
        "\n"
        "Analysts were each assigned a different assay. Each assay returns POSITIVE or\n"
        "NEGATIVE, and the assays have the following known characteristics:\n"
        "\n"
        f"    If {first} is responsible, an assay returns POSITIVE with probability "
        f"{float(p_first):.2f}.\n"
        f"    If {second} is responsible, an assay returns POSITIVE with probability "
        f"{float(p_second):.2f}.\n"
        "\n"
        "Assay results are independent of one another given which candidate is "
        "responsible.\n"
        "\n"
        f"{record}\n"
        "\n"
        f"{elicitation(wording, LABELS)}\n"
    )


def cal_prompt(p_first, wording):
    """
    Calibration stimulus. Hands over the probability outright; no inference,
    no likelihood table, no record. Measures the model's verbalization threshold.
    Deliberately does NOT obey v1 rules R1-R5 -- it is an instrument check, not a
    condition of the experiment, and is reported separately as such.
    """
    first, second = LABELS
    return (
        "One of the following is responsible for the contamination event. "
        "Exactly one is.\n"
        "\n"
        f"    Candidate {first}\n"
        f"    Candidate {second}\n"
        "\n"
        "An independent review has concluded that the chance "
        f"{first} is responsible is {round(p_first * 100)} percent, and the chance "
        f"{second} is responsible is {round((1 - p_first) * 100)} percent.\n"
        "\n"
        f"{elicitation(wording, LABELS)}\n"
    )


def schema(wording):
    """D14: two separate enum fields, strict, additionalProperties false."""
    w = WORDINGS[wording]
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "silence_probe_ordinal",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "candidate": {"type": "string", "enum": list(LABELS)},
                    "confidence": {"type": "string", "enum": [w["low"], w["high"]]},
                },
                "required": ["candidate", "confidence"],
                "additionalProperties": False,
            },
        },
    }


# ---------------------------------------------------------------- build

def build():
    stimuli = []

    for wording in WORDINGS:
        for k in BLIND_K:
            for target_is_first in (True, False):
                pt = blind_p_target(k)
                # P(first-printed label) -- mirror moves the belief, not the level name
                p_first = pt if target_is_first else 1 - pt
                p_first_f = float(p_first)
                cand, conf, lv = expected(p_first_f, wording, LABELS)
                stimuli.append({
                    "id": f"BLIND-k{k}-m{0 if target_is_first else 1}-{wording}",
                    "family": "BLIND",
                    "wording": wording,
                    "k": k,
                    "target_is_first": target_is_first,
                    "p_first_exact": str(p_first),
                    "p_first": round(p_first_f, 6),
                    "p_target": round(float(pt), 6),
                    "level_primary": lv,
                    "level_alt": level(p_first_f, ALT_EDGES),
                    "level_target": level(float(pt), PRIMARY_EDGES),
                    "level_target_alt": level(float(pt), ALT_EDGES),
                    "edge_distance_primary": round(edge_distance(p_first_f, PRIMARY_EDGES), 4),
                    "edge_distance_alt": round(edge_distance(p_first_f, ALT_EDGES), 4),
                    "expected_candidate": cand,
                    "expected_confidence": conf,
                    "expected_answer": level_name(lv, wording, LABELS),
                    "in_decision_rule": k in DECISION_K.values(),
                    "prompt": blind_prompt(k, target_is_first, wording),
                    "response_format": schema(wording),
                })

        for pf in CAL_P_FIRST:
            cand, conf, lv = expected(pf, wording, LABELS)
            stimuli.append({
                "id": f"CAL-p{int(round(pf*100)):02d}-{wording}",
                "family": "CAL",
                "wording": wording,
                "p_first": pf,
                "level_primary": lv,
                "level_alt": level(pf, ALT_EDGES),
                "edge_distance_primary": round(edge_distance(pf, PRIMARY_EDGES), 4),
                "edge_distance_alt": round(edge_distance(pf, ALT_EDGES), 4),
                "expected_candidate": cand,
                "expected_confidence": conf,
                "expected_answer": level_name(lv, wording, LABELS),
                "in_decision_rule": False,
                "prompt": cal_prompt(pf, wording),
                "response_format": schema(wording),
            })

    return stimuli


def freeze(path="w1_stimuli.json"):
    stimuli = build()
    payload = {
        "task": "2.4 / silence probe v2 / W1 ceiling pre-test",
        "purpose": "go/no-go on the D1 four-bin ordinal response format",
        "p": str(P),
        "r": str(R),
        "labels": list(LABELS),
        "blind_k": list(BLIND_K),
        "decision_k": DECISION_K,
        "cal_p_first": list(CAL_P_FIRST),
        "wordings": WORDINGS,
        "primary_edges": list(PRIMARY_EDGES),
        "alt_edges": list(ALT_EDGES),
        "bands_stated_to_model": False,
        "n_stimuli": len(stimuli),
        "stimuli": stimuli,
    }
    blob = json.dumps(payload, indent=2, sort_keys=True)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    payload["sha256"] = digest
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    return payload, digest


# ---------------------------------------------------------------- assertions

def check(stimuli):
    ids = [s["id"] for s in stimuli]
    assert len(ids) == len(set(ids)), "duplicate stimulus id"

    forbidden = ("silent", "silence", "absent", "missing", "did not report",
                 "no report", "posterior", "bayes", "likelihood ratio", "update")
    for s in stimuli:
        if s["family"] != "BLIND":
            continue
        low = s["prompt"].lower()
        for word in forbidden:
            assert word not in low, f"R1/R5 violation ({word}) in {s['id']}"
        # R2: BLIND states neither N nor the rule
        assert "analysts were each assigned" in low
        assert "nine" not in low and "protocol" not in low, f"R2 leak in {s['id']}"
        # R3: no analyst identifiers in the record
        assert "analyst 1" not in low and "assay 1" not in low

    # the two decision cells must sit in different levels under BOTH edge sets
    dec = {}
    for s in stimuli:
        if s["family"] == "BLIND" and s["target_is_first"] and s["wording"] == "A":
            dec[s["k"]] = s
    lo, hi = dec[DECISION_K["low"]], dec[DECISION_K["high"]]
    assert lo["level_target"] == 2 and hi["level_target"] == 3
    assert lo["level_target_alt"] == 2 and hi["level_target_alt"] == 3, \
        "decision pair not robust to D20 alternate edges"
    assert min(lo["edge_distance_primary"], hi["edge_distance_primary"]) >= 0.08
    assert min(lo["edge_distance_alt"], hi["edge_distance_alt"]) >= 0.08

    # CAL must exercise every one of the four options
    seen = {(s["expected_candidate"], s["expected_confidence"])
            for s in stimuli if s["family"] == "CAL" and s["wording"] == "A"}
    assert len(seen) == 4, f"CAL sweep does not reach all four options: {seen}"

    # BLIND is structurally confined to the upper half in the TARGET frame (D4).
    # It reaches print-frame levels 0/1 only by renaming, which is not the same thing.
    blind = [s for s in stimuli if s["family"] == "BLIND"]
    assert all(s["level_target"] >= 2 for s in blind)
    assert {s["expected_confidence"] for s in blind if s["wording"] == "A"} == \
        {WORDINGS["A"]["low"], WORDINGS["A"]["high"]}, \
        "BLIND set does not exercise both confidence values -- decision rule is empty"

    # the mirror must be a pure relabelling: same k, same confidence, flipped candidate
    for k in BLIND_K:
        pair = [s for s in blind if s["k"] == k and s["wording"] == "A"]
        assert len(pair) == 2
        assert pair[0]["expected_confidence"] == pair[1]["expected_confidence"]
        assert pair[0]["expected_candidate"] != pair[1]["expected_candidate"]
    return True


if __name__ == "__main__":
    payload, digest = freeze()
    check(payload["stimuli"])

    print(f"{payload['n_stimuli']} stimuli   sha256 {digest}")
    print()
    print("BLIND cells (wording A, target printed first):")
    print(f"{'k':>3} {'P(tgt)':>9} {'lvl':>4} {'alt':>4} {'d':>7} {'d_alt':>7}  expected")
    for s in payload["stimuli"]:
        if s["family"] == "BLIND" and s["wording"] == "A" and s["target_is_first"]:
            star = " *" if s["in_decision_rule"] else "  "
            print(f"{s['k']:>3} {s['p_target']:>9.3f} {s['level_target']:>4} "
                  f"{s['level_target_alt']:>4} {s['edge_distance_primary']:>7.3f} "
                  f"{s['edge_distance_alt']:>7.3f}  {s['expected_answer']}{star}")
    print("  * = in the go/no-go decision rule")
    print()
    print("CAL sweep (wording A):")
    for s in payload["stimuli"]:
        if s["family"] == "CAL" and s["wording"] == "A":
            print(f"  P(first)={s['p_first']:.2f}  lvl {s['level_primary']}"
                  f" (alt {s['level_alt']})  ->  {s['expected_answer']}")
    print()
    print("Sample BLIND prompt (k=6, wording A):")
    print("-" * 70)
    print(next(s["prompt"] for s in payload["stimuli"]
               if s["id"] == "BLIND-k6-m0-A"))
    print("-" * 70)
    print("Sample CAL prompt (P=0.70, wording B):")
    print("-" * 70)
    print(next(s["prompt"] for s in payload["stimuli"] if s["id"] == "CAL-p70-B"))
    print("-" * 70)
