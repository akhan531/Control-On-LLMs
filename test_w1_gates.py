"""Adversarial stubs: confirm the pre-committed rule can FAIL, not only pass."""
import json, itertools
import w1_stimuli as S
import w1_analyze as A

stim = {s["id"]: s for s in json.load(open("w1_stimuli.json"))["stimuli"]}
CONFIGS = list(A.DEFAULT_MODE) + list(A.HIGH_MODE) + list(A.REPORTED_ONLY)

def synth(responder):
    recs = []
    for cfg, s, seed in itertools.product(CONFIGS, stim.values(), (1,2,3)):
        c, k = responder(cfg, s)
        recs.append({"ok": True, "config": cfg, "stimulus_id": s["id"],
                     "family": s["family"], "wording": s["wording"], "seed": seed,
                     "candidate": c, "confidence": k})
    return recs

def evaluate(name, responder):
    recs = synth(responder)
    r1 = A.g1(recs, stim); v1 = A.g1_verdict(r1); r2 = A.g2(recs, stim)
    tag, _ = A.verdict(v1, r2)
    print(f"{name:<34} G1 {v1['default_passing']}/3 def, {v1['high_passing']}/3 high"
          f"   G2 {sum(d['pass'] for d in r2.values())}/{len(r2)}   -> {tag}")
    return tag

def top(s):   # the always-favourite candidate
    return s["expected_candidate"] if s["level_primary"] >= 2 else s["expected_candidate"]

# 1. CEILING: always names the favoured candidate, always HIGH confidence.
#    This is the exact failure D1 exists to detect.
evaluate("ceiling (always Strongly)",
         lambda c, s: (s["expected_candidate"], S.WORDINGS[s["wording"]]["high"]))

# 2. FLOOR: always LOW confidence.
evaluate("floor (always Slightly)",
         lambda c, s: (s["expected_candidate"], S.WORDINGS[s["wording"]]["low"]))

# 3. BINARY COLLAPSE: correct candidate, confidence constant per config.
evaluate("binary collapse (candidate only)",
         lambda c, s: (s["expected_candidate"], S.WORDINGS[s["wording"]]["high"]))

# 4. INVERTED: discriminates, wrong direction.
def inverted(c, s):
    w = S.WORDINGS[s["wording"]]
    if s["family"] == "CAL":
        return s["expected_candidate"], s["expected_confidence"]
    flip = {w["low"]: w["high"], w["high"]: w["low"]}
    return s["expected_candidate"], flip[s["expected_confidence"]]
evaluate("inverted (right cand, wrong dir)", inverted)

# 5. ONLY sol-high works -- the case the design must reject.
def only_sol_high(c, s):
    w = S.WORDINGS[s["wording"]]
    if c == "sol-high" or s["family"] == "CAL":
        return s["expected_candidate"], s["expected_confidence"]
    return s["expected_candidate"], w["high"]
evaluate("only sol-high discriminates", only_sol_high)

# 6. G1 passes, G2 fails: discriminates on BLIND, never names the non-favoured
#    candidate on CAL (lower half unreachable).
def no_lower_half(c, s):
    if s["family"] == "BLIND":
        return s["expected_candidate"], s["expected_confidence"]
    return S.LABELS[0], s["expected_confidence"]
evaluate("G1 ok, lower half unreachable", no_lower_half)

# 7. Fully obedient -> must be GO.
evaluate("obedient (control)",
         lambda c, s: (s["expected_candidate"], s["expected_confidence"]))
