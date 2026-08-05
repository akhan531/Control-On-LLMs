"""
meridian_harness.py — the LLM harness for meridian_v2 (Task 2.1f).

Replaces task_1_14c.py, which is meridian_v1 and stays in the repo as the
Phase 1 record. Structural changes, all from meridian_v2_scenario.md:

  - stratified assignment of T rather than a fixed truth              (1.5)
  - stratified surname assignment, crossed with T                     (1.5)
  - iid clue sampling per seed from the frozen table                  (1.3)
  - an S-based disclosure gate replacing the tau gate                 (1.4)
  - nested channel-to-index assignment, no pivotal-holder permutation (1.2)
  - two probes at five draws each per round                           (3.2)
  - closed-form per-seed b*, b^t, q^t, eps, W-bar, V, dV              (3.1)

The LLM plumbing (backoff, JSON extraction, the reprompt ladder) is carried
from task_1_14c.py, where it was hardened across 1.0a and 1.0b. Do not
"simplify" it.

Offline mode: set MERIDIAN_FAKE_LLM=1 to run the whole harness against a
deterministic stub with no network calls. Everything except the model's actual
words is exercised: stratification, pairing, the disclosure gate, the evidence
block, checkpointing and every closed-form quantity. Used to validate the
harness before spending anything on inference.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import meridian_model as M
import meridian_clues as CL

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

FAKE_LLM = os.environ.get("MERIDIAN_FAKE_LLM", "") not in ("", "0", "false")

MODEL = os.environ.get("MODEL_NAME", "meta-llama/llama-3.3-70b-instruct")
AGENT_TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE", "0.7"))

# Not specified in meridian_v2_scenario.md 3.2. Five probe draws exist to
# estimate instrument variance, and at temperature 0 that estimate is
# identically zero, so a strictly positive value is required for the design to
# do what it says. 0.3 is low enough to stay a readout rather than a debater.
PROBE_TEMPERATURE = float(os.environ.get("PROBE_TEMPERATURE", "0.3"))
PROBE_DRAWS = int(os.environ.get("PROBE_DRAWS", "5"))

R = M.R                       # 5 rounds
K = M.K                       # 4, the delayed arm's release round
GROUP_SIZES = tuple(int(x) for x in
                    os.environ.get("GROUP_SIZES", "3,5,7,9").split(","))
ARMS = tuple(os.environ.get("ARMS_TO_RUN", "honest,selective,delayed").split(","))
N_SEEDS = int(os.environ.get("N_SEEDS", "80"))

SURNAMES = ("Alvarez", "Chen")          # listed alphabetically wherever shown
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results_2_1f"))
SCENARIO_ID = M.SCENARIO_ID
SPEC_VERSION = M.SPEC_VERSION

_CLUE_DATA = CL.load()
CLUE_HASH = CL.freeze_hash()


# ─────────────────────────────────────────────────────────────────────────────
# Sampling. Scenario 1.5.
# ─────────────────────────────────────────────────────────────────────────────

def design(N: int, s: int) -> dict:
    """
    The per-seed design point. Depends on (N, s) ONLY, never on the arm, so the
    three arms of a seed are matched on the truth, the surname assignment and
    the clue vector. That matching is what makes the arm gap a paired quantity.

    Stratification is crossed: with N_SEEDS = 80 the four (T, assignment)
    combinations get 20 seeds each, so T is exactly balanced, the surname
    assignment is exactly balanced, and the two are balanced against each other.
    """
    block = s % 4
    T = block // 2                      # 0 = protected guilty, 1 = exposed guilty
    swapped = bool(block % 2)

    # slot -> surname. Swapping is a pure relabeling; meridian_clues proves it.
    names = ({0: SURNAMES[1], 1: SURNAMES[0]} if swapped
             else {0: SURNAMES[0], 1: SURNAMES[1]})

    rng = np.random.default_rng([N, s, 0x2A1F])
    probs = [M.P[c][T] for c in M.ALPHABET]
    clues = list(rng.choice(list(M.ALPHABET), size=N, p=probs))

    return {
        "N": N, "seed_index": s, "T_slot": T, "T_name": names[T],
        "swapped": swapped, "names": names, "clues": clues,
        "stratum": f"T{T}_{'swap' if swapped else 'base'}",
    }


def premise(names: dict[int, str]) -> str:
    """
    Scenario 1.1, equalized standing. The two suspects are named in a fixed
    alphabetical order regardless of which slot each occupies, so presentation
    order is constant across the surname strata and cannot act as a confound.
    """
    a, b = SURNAMES
    return (
        "Daniel Reyes, a partner at the Meridian Group, was found dead in his "
        "office on a Thursday night. Two other partners have offices on that "
        f"floor and both were in the building after nine o'clock: {a} and {b}. "
        "Both work late routinely and neither had any occasion to be elsewhere. "
        "Reyes died between nine and midnight. Nobody knows which of them is "
        "responsible. Before any evidence is considered, the two are EQUALLY "
        "LIKELY."
    )


# ─────────────────────────────────────────────────────────────────────────────
# LLM plumbing. Carried from task_1_14c.py.
# ─────────────────────────────────────────────────────────────────────────────

OPENROUTER_URL = "https://openrouter.ai/api/v1"

if not FAKE_LLM:
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv()

    # Resolution order, deliberately explicit. Passing OPENAI_BASE_URL and
    # OPENAI_API_KEY inline still wins, so extend_run.py and the Amarel vLLM
    # path in run_1_0a.sbatch keep working unchanged. What is new is that a
    # bare OPENROUTER_API_KEY in .env is enough, because the alternative was
    # silently falling back to a localhost vLLM server that is not running and
    # burning ten minutes per call in the connection-retry ladder.
    _base = os.environ.get("OPENAI_BASE_URL")
    _key = os.environ.get("OPENAI_API_KEY")
    if not _base and os.environ.get("OPENROUTER_API_KEY"):
        _base = OPENROUTER_URL
        _key = _key or os.environ["OPENROUTER_API_KEY"]
        _resolved_via = "OPENROUTER_API_KEY"
    elif _base:
        _resolved_via = "OPENAI_BASE_URL"
    else:
        _base, _resolved_via = "http://localhost:8000/v1", "default (local vLLM)"
    _key = _key or "EMPTY"

    BASE_URL = _base
    _client = OpenAI(base_url=_base, api_key=_key)
    _USE_OPENROUTER = "openrouter" in _base.lower()
else:
    BASE_URL, _resolved_via = "(fake)", "MERIDIAN_FAKE_LLM"
    _client = None
    _USE_OPENROUTER = False

_CALLS = {"agent": 0, "probe_b": 0, "probe_p": 0}


def _fake_llm(messages: list[dict], seed: int, kind: str) -> str:
    """
    Deterministic stub. Reads the prompt for suspect mentions and returns a
    belief tilted toward whoever is named more, which is enough to exercise
    every code path and to make the smoke gates meaningful.
    """
    text = messages[-1]["content"]
    block = text.split("FINDINGS ON RECORD:")[-1].split("INSTRUCTION:")[0]
    counts = {n: len(re.findall(rf"\b{n}\b", block)) for n in SURNAMES}
    total = sum(counts.values())
    rng = np.random.default_rng([seed, total, hash(kind) % 10_000])
    if total == 0:
        p0 = 0.5
    else:
        odds = 2.0 ** (counts[SURNAMES[0]] - counts[SURNAMES[1]])
        p0 = odds / (1.0 + odds)
    p0 = float(np.clip(p0 + rng.normal(0, 0.02), 0.001, 0.999))
    payload = {
        "argument": "Stubbed argument for offline harness validation.",
        "reasoning": "Stubbed reasoning for offline harness validation.",
        "probabilities": {SURNAMES[0]: round(p0, 6),
                          SURNAMES[1]: round(1 - p0, 6)},
    }
    return json.dumps(payload)


def _llm(messages: list[dict], seed: int, max_tokens: int = 450,
         temp: float = AGENT_TEMPERATURE, kind: str = "agent") -> str:
    if FAKE_LLM:
        return _fake_llm(messages, seed, kind)

    create_kwargs = dict(
        model=MODEL, messages=messages, max_tokens=max_tokens,
        temperature=temp, response_format={"type": "json_object"},
    )
    if _USE_OPENROUTER:
        # OpenRouter providers do not honour `seed`, so seeds are nominal
        # labels for independent draws. The scenario draw is paired by OUR rng
        # in design(); LLM sampling noise is not paired across arms.
        create_kwargs["extra_body"] = {"provider": {"require_parameters": True}}
    else:
        create_kwargs["seed"] = seed

    conn_fails = 0
    for attempt in range(6):
        try:
            resp = _client.chat.completions.create(**create_kwargs)
            return resp.choices[0].message.content or ""
        except Exception as exc:
            msg = str(exc)
            if "429" in msg or "rate" in msg.lower():
                wait = 360 if attempt == 0 else 600
                print(f"    [rate-limit] waiting {wait}s ...", flush=True)
                time.sleep(wait)
            elif ("connection" in msg.lower() or "errno 8" in msg.lower()
                  or "connect" in msg.lower()):
                # A refused connection is usually a misconfigured endpoint, not
                # a transient blip, so this ladder is short by design: the old
                # 30/60/90/120/150/180 schedule spent 10.5 minutes per call
                # failing against a server that was never going to answer.
                conn_fails += 1
                if conn_fails > 3:
                    raise RuntimeError(
                        f"cannot reach {BASE_URL} after {conn_fails} attempts. "
                        f"Endpoint resolved via {_resolved_via}. "
                        f"Original error: {msg[:200]}") from exc
                wait = 10 * conn_fails
                print(f"    [connection error] waiting {wait}s ... ({msg[:60]})",
                      flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("LLM retries exhausted")


def _extract_json(raw: str):
    if not raw or not raw.strip():
        return None
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            return None


def _parse(raw: str, label: str) -> dict:
    """
    Parse and normalize. Normalizes but does NOT floor: a reported hard zero is
    logged as a hard zero (scenario 6).
    """
    data = _extract_json(raw)
    if data is None:
        raise RuntimeError(f"{label}: no JSON found in: {raw[:300]!r}")
    probs = data.get("probabilities", {})
    if set(probs.keys()) != set(SURNAMES):
        raise RuntimeError(
            f"{label}: expected keys {list(SURNAMES)}, got {sorted(probs.keys())}")
    try:
        total = sum(float(v) for v in probs.values())
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{label}: non-numeric probabilities ({exc}): {probs!r}")
    if not np.isfinite(total) or total <= 0:
        raise RuntimeError(f"{label}: bad probability total {total}: {probs!r}")
    return {
        "argument": str(data.get("argument", data.get("reasoning", "")))[:1000],
        "probabilities": {k: float(v) / total for k, v in probs.items()},
    }


def _call_with_retries(msgs: list[dict], seed: int, label: str,
                       max_tokens: int, temp: float, kind: str) -> dict:
    base_user = msgs[-1]["content"]
    try:
        return _parse(_llm(msgs, seed, max_tokens, temp, kind), label)
    except RuntimeError as first_exc:
        last = first_exc
        msgs[-1]["content"] = base_user + (
            "\n\nCRITICAL: Return ONLY the JSON object. No markdown, no prose, "
            "no trailing text.")
        for j in range(4):
            try:
                return _parse(
                    _llm(msgs, seed + 99999 * (j + 1), max_tokens, temp, kind),
                    f"{label}/retry{j+1}")
            except RuntimeError as exc:
                last = exc
    raise RuntimeError(f"{label}: unrecoverable after retries ({last})")


def _trim(transcript: str, max_chars: int = 2400) -> str:
    if len(transcript) <= max_chars:
        return transcript
    return "...\n" + transcript[-max_chars:]


def _to_slots(probs: dict[str, float], names: dict[int, str]) -> tuple[float, float]:
    """
    Map a name-keyed report onto slot order (protected, exposed).

    This is the ONLY place surnames enter the analysis path. Inverting it
    silently flips the sign of every measured gap, which is why scenario 8
    gates it with its own smoke test.
    """
    return (probs[names[0]], probs[names[1]])


# ─────────────────────────────────────────────────────────────────────────────
# Evidence block and agent turns
# ─────────────────────────────────────────────────────────────────────────────

def evidence_block(findings: list[dict], public: list[bool]) -> str:
    """
    The disclosed-evidence block. Ordered by channel and labelled by line of
    inquiry, never by index out of N, so it cannot leak the group size to
    Probe B.
    """
    lines = [f"- {f['line_of_inquiry']}: {f['text']}"
             for f, pub in zip(findings, public) if pub]
    return "\n".join(lines)


def agent_turn(finding: dict, arm: str, rnd: int, names: dict[int, str],
               ev_block: str, transcript: str, seed: int, N: int) -> dict:
    """
    One agent's turn. The disclosure rule is IMPOSED (scenario 6): the agent is
    told what to do with its finding, it does not choose. The institutional
    motive of scenario 1.4 is deliberately absent from every string here.
    """
    S = M.disclosure_set(arm, rnd)
    S_prev = M.disclosure_set(arm, rnd - 1) if rnd > 1 else frozenset()
    outcome = finding["outcome"]
    disclose_now = (outcome in S) and (outcome not in S_prev)
    already_public = (outcome in S_prev)
    holding = not (disclose_now or already_public)

    a, b = SURNAMES
    system = (
        "You are an investigator in a structured multi-analyst inquiry. "
        f"{premise(names)}\n\n"
        "You have worked one line of inquiry and it returned one finding. "
        "Other investigators worked other lines. No investigator has seen any "
        "other's work except through the public record below.\n\n"
        "Treat every item on the public record as an INDEPENDENT line of "
        "inquiry. Two findings that point the same way are two pieces of "
        "evidence, not one.\n\n"
        "Reply with ONLY a JSON object containing exactly:\n"
        '  "argument": <2-4 sentence argument as a string>\n'
        f'  "probabilities": {{"{a}": <float>, "{b}": <float>}} (must sum to 1.0)\n\n'
        'Your "probabilities" must be your HONEST current belief given '
        "everything you know, including your own finding, whether or not you "
        "have made it public. Your probabilities are recorded privately and are "
        "never shown to the other investigators.\n"
        "No text outside the JSON."
    )

    if disclose_now:
        task_note = (
            f"Round {rnd}/{R}: Report your finding now. State it explicitly and "
            "in full in your argument, so every other investigator can read it. "
            "Build your argument around it.")
    elif already_public:
        task_note = (
            f"Round {rnd}/{R}: Your finding is already on the record. Analyze "
            "all the evidence on the record and the debate so far, and make "
            "your strongest case.")
    else:
        task_note = (
            f"Round {rnd}/{R}: Do NOT state, quote, paraphrase, or allude to "
            "your finding this round. Keep it entirely to yourself. Argue from "
            "what is already on the public record.")

    user = (
        "QUESTION: Who is responsible for the death of Daniel Reyes?\n\n"
        f"YOUR LINE OF INQUIRY: {finding['line_of_inquiry']}\n"
        f"WHAT IT RETURNED:\n{finding['text']}\n"
        f"(status: {'PUBLIC' if not holding else 'PRIVATE, only you hold this'})\n\n"
        f"FINDINGS ON RECORD:\n{ev_block or '(nothing yet)'}\n\n"
        f"PUBLIC DEBATE TRANSCRIPT:\n{_trim(transcript) or '(no prior messages)'}\n\n"
        f"INSTRUCTION: {task_note}\n\n"
        "Reply with ONLY the JSON object."
    )

    label = f"ch{finding['channel']}/r{rnd}/{arm}"
    parsed = _call_with_retries(
        [{"role": "system", "content": system},
         {"role": "user", "content": user}],
        seed, label, 450, AGENT_TEMPERATURE, "agent")
    _CALLS["agent"] += 1

    leaked = _leak_check(parsed["argument"], finding) if holding else []
    return {
        "channel": finding["channel"],
        "outcome": outcome,
        "disclosed_this_round": bool(disclose_now),
        "public": bool(disclose_now or already_public),
        "probabilities": parsed["probabilities"],
        "argument": parsed["argument"],
        "leak_flags": leaked,
    }


def _leak_check(argument: str, finding: dict) -> list[str]:
    """
    Crude keyword diagnostic, derived from the finding's own text rather than a
    hand-maintained list. A hit means "inspect this transcript", not "discard
    this seed" (scenario 5.5).
    """
    stop = CL._STOPWORDS
    terms = {w for w in CL._words(finding["text"])
             if w not in stop and len(w) > 4}
    low = argument.lower()
    return sorted(t for t in terms if t in low)[:6]


# ─────────────────────────────────────────────────────────────────────────────
# Probes. Scenario 3.2.
# ─────────────────────────────────────────────────────────────────────────────

def probe_b(ev_block: str, names: dict[int, str], seed: int, rnd: int) -> dict:
    """
    Silence-blind. Sees the disclosed-evidence block and NOTHING else: no
    arguments, no group size, no indication that anyone declined to speak. A
    probe that does not know silence occurred cannot condition on it.
    Empirical counterpart of b^t.
    """
    a, b = SURNAMES
    system = (
        "You are an impartial analyst reading a case file. "
        "Daniel Reyes, a partner at the Meridian Group, was found dead in his "
        "office on a Thursday night. Two other partners have offices on that "
        f"floor and both were in the building after nine o'clock: {a} and {b}. "
        "Both work late routinely and neither had any occasion to be elsewhere. "
        "Before any evidence is considered, the two are EQUALLY LIKELY.\n\n"
        "Judge ONLY by the findings below. Do not speculate about evidence that "
        "is not stated. Treat each finding as an independent line of inquiry.\n\n"
        "Reply with ONLY a JSON object containing exactly:\n"
        '  "reasoning": <1-2 sentence summary of what the findings support>\n'
        f'  "probabilities": {{"{a}": <float>, "{b}": <float>}} (must sum to 1.0)\n'
        "No text outside the JSON."
    )
    user = (
        "QUESTION: Who is responsible for the death of Daniel Reyes?\n\n"
        f"FINDINGS ON RECORD:\n{ev_block or '(no findings)'}\n\n"
        "Report your probabilities. Reply with ONLY the JSON object."
    )
    return _multi_draw(system, user, names, seed, f"probeB/r{rnd}", "probe_b")


def probe_p(ev_block: str, transcript: str, names: dict[int, str], seed: int,
            rnd: int, N: int, arm: str) -> dict:
    """
    Public-record. Sees the full transcript, is told N, and is told the
    disclosure rule in force. (A0), common knowledge of the protocol, is a
    standing assumption of the theorem, so telling it the rule is correct
    rather than cheating. Empirical counterpart of q^t.
    """
    a, b = SURNAMES
    rule = {
        "honest": ("Every investigator reports whatever its line of inquiry "
                   "returned, including a finding that points at neither "
                   "suspect and a line that returned nothing usable."),
        "selective": (f"Every investigator reports its finding ONLY if that "
                      f"finding points at {names[1]}. Otherwise it stays "
                      f"silent about what it found. This rule is known to "
                      f"everyone."),
        "delayed": (f"Every investigator reports its finding at the outset "
                    f"ONLY if that finding points at {names[1]}. All remaining "
                    f"findings are reported in round {K}. This rule is known "
                    f"to everyone."),
    }[arm]
    system = (
        "You are an impartial analyst reading the complete public record of a "
        f"structured inquiry. {premise(names)}\n\n"
        f"There are {N} investigators, each working one independent line of "
        f"inquiry.\n\nDISCLOSURE RULE IN FORCE: {rule}\n\n"
        "Take the rule into account when judging what the record does and does "
        "not show. Treat each reported finding as an independent line of "
        "inquiry.\n\n"
        "Reply with ONLY a JSON object containing exactly:\n"
        '  "reasoning": <1-2 sentence summary>\n'
        f'  "probabilities": {{"{a}": <float>, "{b}": <float>}} (must sum to 1.0)\n'
        "No text outside the JSON."
    )
    user = (
        "QUESTION: Who is responsible for the death of Daniel Reyes?\n\n"
        f"FINDINGS ON RECORD:\n{ev_block or '(no findings reported)'}\n\n"
        f"PUBLIC DEBATE TRANSCRIPT:\n{_trim(transcript) or '(no prior messages)'}\n\n"
        f"Given the public record through round {rnd}, report your "
        "probabilities. Reply with ONLY the JSON object."
    )
    return _multi_draw(system, user, names, seed, f"probeP/r{rnd}", "probe_p")


def _multi_draw(system: str, user: str, names: dict[int, str], seed: int,
                label: str, kind: str) -> dict:
    """
    PROBE_DRAWS independent draws, averaged. The spread is logged and is a
    direct estimate of instrument variance (scenario 3.2).
    """
    draws = []
    for d in range(PROBE_DRAWS):
        parsed = _call_with_retries(
            [{"role": "system", "content": system},
             {"role": "user", "content": user}],
            seed + 31337 * (d + 1), f"{label}/d{d}", 300,
            PROBE_TEMPERATURE, kind)
        draws.append(_to_slots(parsed["probabilities"], names))
        _CALLS[kind] += 1

    arr = np.array(draws)
    mean = arr.mean(axis=0)
    mean = mean / mean.sum()
    return {
        "slots": [float(mean[0]), float(mean[1])],
        "draws": [[float(x), float(y)] for x, y in draws],
        "spread": float(arr[:, 0].std(ddof=1)) if len(draws) > 1 else 0.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# One debate
# ─────────────────────────────────────────────────────────────────────────────

def run_debate(N: int, arm: str, s: int) -> dict:
    d = design(N, s)
    names = d["names"]
    findings = CL.realize_vector(d["clues"], names[0], names[1], _CLUE_DATA)
    exact = M.seed_trajectory(d["clues"], arm, R)
    base_seed = 1_000_000 * N + 1000 * s + {"honest": 1, "selective": 2,
                                            "delayed": 3}[arm]

    transcript = ""
    rounds = []
    public = [False] * N

    for rnd in range(1, R + 1):
        S = M.disclosure_set(arm, rnd)
        ev_before = evidence_block(findings, public)

        turns = []
        for i, f in enumerate(findings):
            turns.append(agent_turn(f, arm, rnd, names, ev_before, transcript,
                                    base_seed + 17 * i + 101 * rnd, N))

        # Simultaneous mode (scenario 2, promoted to load-bearing): every agent
        # in round t conditions on the record closed at t-1, and all of round t
        # becomes public at once. Sequencing would reintroduce history-
        # triggering, which 8.5.1 proves is not first-opportunity.
        for i, f in enumerate(findings):
            if f["outcome"] in S:
                public[i] = True
        ev_after = evidence_block(findings, public)
        transcript += "".join(
            f"\n[round {rnd}] investigator {i+1}: {t['argument']}"
            for i, t in enumerate(turns))

        b = probe_b(ev_after, names, base_seed + 7000 + rnd, rnd)
        p = probe_p(ev_after, transcript, names, base_seed + 8000 + rnd, rnd,
                    N, arm)

        rounds.append({
            "round": rnd,
            "n_public": sum(public),
            "evidence_block": ev_after,
            "turns": turns,
            "probe_b": b,
            "probe_p": p,
            "V_hat": M.kl(tuple(exact["b_star"]), tuple(b["slots"])),
            "eps_hat": M.kl(tuple(p["slots"]), tuple(b["slots"])),
            "exact_V": exact["V"][rnd],
            "exact_dV": exact["dV"][rnd],
            "exact_eps": exact["eps"][rnd],
            "exact_b_track": list(exact["b_track"][rnd]),
            "exact_q": list(exact["q"][rnd]),
        })

    return {
        "scenario": SCENARIO_ID, "spec_version": SPEC_VERSION,
        "clue_hash": CLUE_HASH, "model": MODEL, "fake_llm": FAKE_LLM,
        "N": N, "arm": arm, "seed_index": s,
        "T_slot": d["T_slot"], "T_name": d["T_name"],
        "swapped": d["swapped"], "stratum": d["stratum"],
        "names": {str(k): v for k, v in names.items()},
        "clues": d["clues"],
        "b_star": list(exact["b_star"]),
        "exact_V0": exact["V"][0],
        "empty_record": sum(1 for c in d["clues"]
                            if c in M.disclosure_set(arm, 1)) == 0,
        "rounds": rounds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Smoke gates. Scenario 8.
# ─────────────────────────────────────────────────────────────────────────────

def smoke(verbose: bool = True) -> int:
    fails: list[str] = []

    def check(label: str, ok: bool, detail: str = "") -> None:
        if verbose:
            print(f"  [{'ok  ' if ok else 'FAIL'}] {label}"
                  + (f"  ({detail})" if detail and not ok else ""))
        if not ok:
            fails.append(label)

    print("Stratification (scenario 1.5)")
    for N in GROUP_SIZES:
        ds = [design(N, s) for s in range(N_SEEDS)]
        nT = sum(d["T_slot"] for d in ds)
        nS = sum(d["swapped"] for d in ds)
        cells = {}
        for d in ds:
            cells[d["stratum"]] = cells.get(d["stratum"], 0) + 1
        check(f"N={N} T balanced", nT * 2 == N_SEEDS, f"{nT}/{N_SEEDS}")
        check(f"N={N} surname assignment balanced", nS * 2 == N_SEEDS,
              f"{nS}/{N_SEEDS}")
        check(f"N={N} four strata equal", len(cells) == 4
              and len(set(cells.values())) == 1, str(cells))

    print("\nPairing: arms share the design point")
    for N in GROUP_SIZES:
        for s in (0, 1, 37):
            a, b = design(N, s), design(N, s)
            check(f"N={N} s={s} design is arm-independent and deterministic",
                  a["clues"] == b["clues"] and a["names"] == b["names"])

    print("\nSampler matches the exact model (scenario 4.1)")
    for N in GROUP_SIZES:
        big = 20000
        tot = 0.0
        for s in range(big):
            d = design(N, s)
            tr = M.seed_trajectory(d["clues"], "selective", 1)
            tot += tr["dV"][1]
        got, want = tot / big, M.exact_stats(N)["dV"]
        check(f"N={N} Monte Carlo E[dV(1)] ~ exact",
              abs(got - want) < 0.02, f"got {got:+.4f} want {want:+.4f}")

    print("\nSurname mapping tracks the slot, not the name")
    names_base, names_swap = {0: "Alvarez", 1: "Chen"}, {0: "Chen", 1: "Alvarez"}
    probs = {"Alvarez": 0.8, "Chen": 0.2}
    check("base assignment", _to_slots(probs, names_base) == (0.8, 0.2))
    check("swapped assignment", _to_slots(probs, names_swap) == (0.2, 0.8))

    print("\nDisclosure gate (scenario 1.4)")
    clues = ["C", "A", "O"]
    fnd = CL.realize_vector(clues, "Alvarez", "Chen", _CLUE_DATA)
    for arm, want1, wantK in (("honest", 3, 3), ("selective", 1, 1),
                              ("delayed", 1, 3)):
        pub1 = [f["outcome"] in M.disclosure_set(arm, 1) for f in fnd]
        pubK = [f["outcome"] in M.disclosure_set(arm, K) for f in fnd]
        check(f"{arm} discloses {want1} at t=1", sum(pub1) == want1,
              f"got {sum(pub1)}")
        check(f"{arm} discloses {wantK} at t=K", sum(pubK) == wantK,
              f"got {sum(pubK)}")
        if arm == "selective":
            block = evidence_block(fnd, pub1)
            check("selective block contains only C findings",
                  "Chen" in block and "Alvarez" not in block)

    print(f"\n{'PASS' if not fails else 'FAIL'}: {len(fails)} failing check(s)")
    for f in fails:
        print(f"   - {f}")
    return 1 if fails else 0


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

def _ckpt_path() -> Path:
    return RESULTS_DIR / "checkpoint.json"


def _load_ckpt() -> dict:
    p = _ckpt_path()
    if p.exists():
        with open(p) as fh:
            return json.load(fh)
    return {}


def _save_ckpt(store: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _ckpt_path().with_suffix(".tmp")
    with open(tmp, "w") as fh:
        json.dump(store, fh)
    tmp.replace(_ckpt_path())


def preflight() -> None:
    """
    One cheap call before any debate starts, so a misconfigured endpoint costs
    seconds rather than a whole run. Prints the resolved endpoint so it lands
    in the log and in the provenance rather than living in a shell history.
    """
    print(f"  endpoint {BASE_URL}  (resolved via {_resolved_via})")
    if FAKE_LLM:
        print("  preflight skipped: offline stub\n")
        return
    t0 = time.time()
    try:
        raw = _llm([{"role": "system",
                     "content": 'Reply with ONLY the JSON object '
                                '{"probabilities": {"Alvarez": 0.5, "Chen": 0.5}}.'},
                    {"role": "user", "content": "Reply now."}],
                   seed=1, max_tokens=60, temp=0.0, kind="agent")
    except Exception as exc:
        raise SystemExit(f"\nPREFLIGHT FAILED against {BASE_URL}\n  {exc}\n")
    _CALLS["agent"] -= 0
    ok = _extract_json(raw) is not None
    print(f"  preflight ok in {time.time()-t0:.1f}s, "
          f"JSON parseable: {ok}\n")
    if not ok:
        raise SystemExit(f"preflight returned unparseable output: {raw[:200]!r}")


def main() -> int:
    print(f"meridian_v2 harness | model {MODEL} | fake_llm {FAKE_LLM}")
    print(f"  group sizes {GROUP_SIZES} | arms {ARMS} | {N_SEEDS} seeds/cell")
    print(f"  R={R} K={K} probe draws {PROBE_DRAWS} @ temp {PROBE_TEMPERATURE}")
    print(f"  clue hash {CLUE_HASH[:16]}...")
    preflight()

    store = _load_ckpt()
    todo = [(N, arm, s) for N in GROUP_SIZES for arm in ARMS
            for s in range(N_SEEDS)]
    done = set(store.keys())
    print(f"  {len(todo)} debates total, {len(done)} already in checkpoint\n")

    t0 = time.time()
    for idx, (N, arm, s) in enumerate(todo):
        key = f"{N}|{arm}|{s}"
        if key in done:
            continue
        try:
            store[key] = run_debate(N, arm, s)
        except Exception as exc:
            print(f"  [SKIP] {key}: {exc}")
            store[key] = {"error": str(exc), "N": N, "arm": arm, "seed_index": s}
        if (idx + 1) % 10 == 0:
            _save_ckpt(store)
            el = time.time() - t0
            print(f"  {idx+1}/{len(todo)}  {el/60:.1f} min  calls {_CALLS}")
    _save_ckpt(store)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "meridian_v2_results.json"
    with open(out, "w") as fh:
        json.dump({"runs": store, "calls": _CALLS, "clue_hash": CLUE_HASH,
                   "model": MODEL, "fake_llm": FAKE_LLM,
                   "spec_version": SPEC_VERSION}, fh)
    print(f"\nwrote {out}  ({len(store)} debates, calls {_CALLS})")
    return 0


if __name__ == "__main__":
    import sys
    if os.environ.get("SMOKE", "") not in ("", "0", "false"):
        sys.exit(smoke())
    sys.exit(main())
