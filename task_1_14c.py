#!/usr/bin/env python3
"""
Task 1.14c -- Strategic Timing LLM harness (scenario: meridian_v1)

An LLM debate that is a REALIZATION of the locked model instantiation, not an
analogy to it. Single source of numbers: poster_model.md (Task 1.14a, locked
2026-07-16). Every scenario constant below appears there first; the likelihood
scale and the schedules are imported from model_sim.py (Task 1.14b) rather than
retyped, so there is exactly one copy of each.

WHAT CHANGED FROM task_1_0.py, AND WHY
    task_1_0.py does not instantiate the model. Four structural mismatches, all
    repaired here. The first three are the 1.14 lock; the fourth was found on
    2026-07-16 while reading the file against the spec.

    (1) PUBLIC_EVIDENCE removed. Anything common knowledge at t=0 that never
        moves IS pi under the model, not a clue. The prior is now stated to
        agents directly: three suspects, equally likely.

    (2) Four private clues, one per agent, instead of one. gen_1..gen_3 held
        null clues with flat likelihoods and contributed nothing to b^t.

    (3) Agents are symmetric. The `expert` id is gone; `has_clue` gated on
        agent_id == "expert". The pivotal holder is drawn uniformly per seed
        and held FIXED across arms within that seed.

    (4) THE WITHHOLDER NOW HOLDS ITS CLUE. task_1_0.py gated the clue out of
        the withholder's own context until round K:

            has_clue = (agent_id == "expert") and (rnd >= dr)
            evidence = PUBLIC + DECISIVE_CLUE if has_clue else PUBLIC

        so the 1.0a withholder never held anything, it received the clue late.
        That instantiates late ARRIVAL of information, not withholding, which
        is the one thing this project is about. poster_model.md 6.3 is explicit
        the other way: agent 4's private belief IS b* at t=1,2,3 and puts 0.997
        on Chen at t=0, before anyone speaks. Here every agent holds its clue
        from round 1 and tau gates only whether the text becomes PUBLIC.

    (5) ROUNDS ARE SIMULTANEOUS  (Ali, 2026-07-17; DEBATE_MODE=simultaneous).
        Found after the first 16-seed run. The four repairs above were checked
        against the 1.14 lock; the information SET was never checked against
        the model's timing, and it was wrong. The model: b^t entering round t
        reflects D_{1:t-1}; agents condition on that plus their own clue; their
        disclosures D_t drive b^{t+1}. So an agent in round t CANNOT see round
        t's disclosures. The first run appended to the record inside the agent
        loop, so agent_2 read agent_1's clue before speaking in the same round.
        There is no intra-round order in the model, and there should be none
        here. Sequential-within-round was task_1_0.py's idiosyncrasy, inherited
        without examination; the debate literature is simultaneous too (agents
        respond to the PREVIOUS round's responses).

        WHY THE OLD MODE IS STILL A FLAG, NOT DELETED. The 2026-07-17
        sequential run found that credit is dominated by speaking position:
        pivotal clue held by agent_1 (opens) -> 0.239, by agent_4 (closes) ->
        0.906, d = 3.58, p = 1e-5, r(position, credit) = +0.819, roughly 11x
        the effect of tau, which was null (+0.059, p = 0.43 paired). Two
        explanations, and the mode flag separates them:
          - content-mediated burial: agent_1 opens with the DNA and nothing
            else, three agents then answer it with Alvarez evidence; agent_4
            speaks last having read c1c2c3 and can refute them. Different
            arguments -> different credit. DIES under simultaneous.
          - judge recency: the judge's transcript is serialized either way, so
            it pays later lines more whatever they say. SURVIVES.
        Keep the judge's transcript in agent_1..agent_4 order so position stays
        measurable; the per-seed assignment already randomizes who sits there.

MEASUREMENT: THE OBSERVER PROBE  (Ali's verdict 2026-07-16)
    Repair (4) breaks an inherited recipe. Task 1.11 locked "average agent
    beliefs, then take the reverse KL", and 1.14d's spec repeats it. That was
    safe under 1.0a precisely BECAUSE the withholder did not hold the clue. It
    is not safe now. The model's b^t is the belief of someone holding only the
    DISCLOSED evidence; the withholder's private posterior is a different
    object (eq. 2, not eq. 1). Averaging it in contaminates the state:

        withhold plateau, model b^t (public belief)      2.5919
        withhold plateau, average of all 4 private b_i    1.0997

    a 1.49-nat gap present in a run of perfectly model-obedient agents, before
    a single token of rhetoric. So b^t is measured by an OBSERVER: a fresh
    context each round that sees the public record and nothing else, holds no
    clue, and reports a 3-way belief. That is b^t's definitional counterpart
    and it is the same instrument in every arm and every round.

    Per-agent beliefs are logged anyway, so 1.14d can build the all-four
    average and the clue-already-public average as robustness panels with no
    re-run. The observer is the pre-registered headline.

THE PUBLIC RECORD IS SPLIT IN TWO
    task_1_0.py kept one transcript trimmed to its last 1200 chars. Safe there
    (the clue landed at round 4, still in the tail at round 5). Not safe here:
    c1, c2, c3 all land at round 1 and must stay public through round 5 against
    thousands of chars of accumulated argument. A tail trim evicts them by
    round 3 and the state silently vanishes from the record.

    So: DISCLOSED EVIDENCE is a persistent block, verbatim, never trimmed;
    ARGUMENTS are a separate log, trimmed to the tail. This mirrors the model
    rather than working around it. D_{1:t} is the state (eq. 1); arguments are
    cheap talk that A2/A9 say cannot move b^t. Consequence for Task 1.12: any
    observer movement on a silent round is now unambiguously the rhetoric
    residual, because the evidence block provably did not change.

TRUTHFUL REPORTING IS FORCED, NOT CHOSEN
    M2 locks truthful-timing-only: the strategy space is the disclosure round
    tau_i and there is no lie action. So the withholder reports its honest
    belief (~0.98 Chen) while saying nothing about the DNA. This lives in the
    SYSTEM prompt, identical for every agent in every arm and round, so that
    the disclosure gate remains the ONLY thing that differs between arms.
    Reported probabilities never enter the transcript (only `argument` does),
    so nothing leaks to the other agents through the readout.

NO EPSILON FLOOR HERE
    The harness logs raw normalized probabilities. Flooring is 1.14d's job and
    needs a sensitivity table (616 of 960 agent-rounds carried a hard zero on
    the old data). Keep the empirical-side artifact out of the raw record. The
    only exception is the smoke diagnostic, which floors to print a V and says
    so.

INVARIANT
    honest and withhold disclose IDENTICAL clue text and differ in exactly one
    integer, tau_4 (poster_model.md 4.2). The clue text is force-inserted into
    the evidence block at the disclosure round regardless of what the LLM
    actually wrote, so the matched-information control cannot be broken by a
    disobedient model.

RUN
    smoke (1 seed, all arms, checks the scenario fires):
        SMOKE=1 python task_1_14c.py

    full 16-seed run on OpenRouter Llama-3.3-70B (the locked model):
        OPENAI_BASE_URL=https://openrouter.ai/api/v1 \
        OPENAI_API_KEY=$OPENROUTER_API_KEY \
        MODEL_NAME=meta-llama/llama-3.3-70b-instruct \
        PROVIDER_TAG=openrouter \
        RESULTS_DIR=results_1_14c_70b_16seed \
        N_SEEDS=16 python task_1_14c.py

    DEBATE_MODE defaults to simultaneous. DEBATE_MODE=sequential reproduces the
    2026-07-17 run (results_1_14c_70b_16seed), which is retained on disk as the
    comparison arm.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# Single source of the model numbers. Do not retype the scale or the schedules.
import model_sim as M

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
MODEL = os.environ.get("MODEL_NAME", "NousResearch/Meta-Llama-3.1-8B-Instruct")
TEMPERATURE = 0.7
R = M.R                     # 5 rounds        poster_model.md 2
K = M.K                     # 4, withhold disclosure round
N_SEEDS = int(os.environ.get("N_SEEDS", "16"))
SMOKE = os.environ.get("SMOKE", "") not in ("", "0", "false")

# simultaneous (default) = the model's information structure: every agent in
# round t conditions on the record closed at the end of round t-1, and all of
# round t becomes public at once. sequential = the 2026-07-17 design, which
# leaked round t's disclosures to later speakers in round t.
#
# The prompts are IDENTICAL in both modes, deliberately. The manipulation is
# exactly one variable, the information set, so the two runs are comparable.
DEBATE_MODE = os.environ.get("DEBATE_MODE", "simultaneous").lower()
if DEBATE_MODE not in ("simultaneous", "sequential"):
    raise SystemExit(f"DEBATE_MODE must be simultaneous|sequential, got {DEBATE_MODE!r}")
SEQUENTIAL = (DEBATE_MODE == "sequential")

SCENARIO_ID = "meridian_v1"
ANSWER_SET = list(M.ANSWERS)          # ["Alvarez", "Boyd", "Chen"]
CORRECT_ANSWER = M.TRUTH              # "Chen". Latent: never told to any agent.
MISLEADING = "Alvarez"                # argmax of the three-clue state, 0.75

AGENT_IDS = [f"agent_{i}" for i in range(1, M.N_AGENTS + 1)]
CLUE_IDS = list(M.CLUES)              # ["c1", "c2", "c3", "c4"]
PIVOTAL = M.PIVOTAL                   # "c4"

ARMS = ["honest", "withhold", "never"]
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results_1_14c"))
ARMS_TO_RUN = os.environ.get("ARMS_TO_RUN", "honest,withhold,never").split(",")

# ── Scenario: meridian_v1 ─────────────────────────────────────────────────────
# poster_model.md 3. The four clues are four different KINDS of evidence
# (motive, opportunity, testimony, forensics) because the model treats them as
# conditionally independent given T. If the LLM read them as three restatements
# of one point, its belief would move less than the model's and we would
# manufacture a model/data gap that is NOT the rhetoric residual.

PREMISE = (
    "Daniel Reyes, a partner at the Meridian Group, was found dead in his office. "
    "Three people had access to the floor that night: Alvarez, Boyd, and Chen. "
    "Nobody knows which of them is responsible. "
    "Before any evidence is considered, the three are EQUALLY LIKELY."
)

CLUE_TEXT: dict[str, str] = {
    "c1": (
        "THE COMPLAINT: Two weeks before his death, Reyes filed a formal internal "
        "complaint naming Alvarez. Had it gone to the board, Alvarez would have "
        "been dismissed."
    ),
    "c2": (
        "THE BADGE LOG: Building access logs show Alvarez badged onto the floor at "
        "9:40pm and did not badge out until 11:15pm. Reyes died between 9pm and "
        "midnight."
    ),
    "c3": (
        "THE OLD GUARD: Reyes's assistant reports that he agreed to a late meeting "
        "that night with someone he called \"one of the old guard.\" Alvarez and "
        "Boyd have each been at the firm over a decade. Chen joined fourteen "
        "months ago."
    ),
    "c4": (
        "THE DNA: Skin recovered from beneath Reyes's fingernails yields a "
        "single-source profile. It matches Chen. Alvarez and Boyd are both "
        "excluded as contributors."
    ),
}

# Leak probe. Only c4 is ever held past round 1 (withhold rounds 1-3, never all
# rounds), but the check is written over every clue so it does not quietly stop
# working if a schedule changes. Keyword-based and deliberately crude: this is a
# logged DIAGNOSTIC, not a gate. A hit means "inspect this transcript", not
# "discard this seed".
LEAK_KEYWORDS: dict[str, list[str]] = {
    "c1": ["complaint", "dismiss", "board", "grievance"],
    "c2": ["badge", "access log", "9:40", "11:15"],
    "c3": ["old guard", "assistant", "late meeting", "fourteen months"],
    "c4": ["dna", "skin", "fingernail", "profile", "forensic", "single-source",
           "excluded as contributor"],
}

# ── Client ────────────────────────────────────────────────────────────────────
_client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "EMPTY"),
)
_USE_OPENROUTER = "openrouter" in os.environ.get("OPENAI_BASE_URL", "").lower()


# ── LLM helpers (carried from task_1_0.py, hardened there across 1.0a/1.0b) ───
def _llm(messages: list[dict], seed: int, max_tokens: int = 500,
         temp: float = TEMPERATURE) -> str:
    """Single LLM call with exponential backoff on rate-limit errors."""
    create_kwargs = dict(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temp,
        response_format={"type": "json_object"},
    )
    if _USE_OPENROUTER:
        # The OpenRouter path drops `seed`: providers do not honour it, so seeds
        # are nominal labels for independent draws, not a pairing device. This
        # is why 1.0a reports the credit gap as an UNPAIRED two-sample
        # comparison, and the same holds here.
        create_kwargs["extra_body"] = {"provider": {"require_parameters": True}}
    else:
        create_kwargs["seed"] = seed
    for attempt in range(6):
        try:
            resp = _client.chat.completions.create(**create_kwargs)
            return resp.choices[0].message.content or ""
        except Exception as exc:
            msg = str(exc)
            if "429" in msg or "rate" in msg.lower():
                wait = 360 if attempt == 0 else 600
                print(f"    [rate-limit] waiting {wait}s …")
                time.sleep(wait)
            elif ("connection" in msg.lower() or "errno 8" in msg.lower()
                  or "connect" in msg.lower()):
                wait = 30 * (attempt + 1)
                print(f"    [connection error] waiting {wait}s … ({msg[:60]})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("LLM retries exhausted")


def _extract_json(raw: str):
    """Pull a JSON object from possibly-messy LLM output; None on failure."""
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
    Parse JSON from LLM output; validate and normalize probabilities.
    Raises RuntimeError on failure -- caller retries, then skips the seed.

    Normalizes but does NOT floor. A reported hard zero is logged as a hard
    zero; 1.14d owns the floor and its sensitivity table.
    """
    data = _extract_json(raw)
    if data is None:
        raise RuntimeError(f"{label}: no JSON found in: {raw[:300]!r}")

    probs = data.get("probabilities", {})
    if set(probs.keys()) != set(ANSWER_SET):
        raise RuntimeError(
            f"{label}: expected keys {ANSWER_SET}, got {sorted(probs.keys())}"
        )
    try:
        total = sum(float(v) for v in probs.values())
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{label}: non-numeric probabilities ({exc}): {probs!r}")
    if not np.isfinite(total) or total <= 0:
        raise RuntimeError(f"{label}: bad probability total {total}: {probs!r}")
    norm = {k: float(v) / total for k, v in probs.items()}
    return {
        "argument": str(data.get("argument", ""))[:1000],
        "probabilities": norm,
        "top_pick": max(norm, key=norm.get),
    }


def _trim(transcript: str, max_chars: int = 2000) -> str:
    """
    Keep the tail of the ARGUMENT log to cap input token growth.

    Safe to trim only because disclosed evidence lives in its own persistent
    block and is never passed through here. Trimming the evidence would delete
    the state itself -- see the module docstring.
    """
    if len(transcript) <= max_chars:
        return transcript
    cut = transcript[-max_chars:]
    nl = cut.find("\n")
    if nl > 0:
        cut = cut[nl + 1:]
    return "(… earlier rounds omitted …)\n" + cut


# ── Per-seed randomization ────────────────────────────────────────────────────
def _assignment(seed: int) -> dict[str, str]:
    """
    Uniform permutation of the four clues over the four agents, drawn per seed
    and IDENTICAL across arms within a seed (poster_model.md 4.1).

    4.1 only requires the PIVOTAL holder be uniform. Permuting all four is
    strictly stronger at zero cost: it also kills any order artifact from a
    fixed clue always being argued by the agent who speaks first. It is uniform
    on the pivotal holder as a marginal, so 4.1 is satisfied.

    The model is permutation-invariant (b^t depends on D_{1:t}, not on who
    disclosed it -- model_sim.test_permutation_invariance), so this changes
    nothing on the model side. It exists only to kill the positional halo in
    the empirical arm.
    """
    clues = list(CLUE_IDS)
    random.Random(seed).shuffle(clues)
    return dict(zip(AGENT_IDS, clues))


def _judge_labels(seed: int) -> dict[str, str]:
    """
    Per-seed random map from agent_id to a neutral analyst label, so the credit
    judge cannot anchor on a role name.

    Offset from the assignment draw so that "which agent holds c4" and "which
    label that agent wears" are independent rather than a deterministic
    function of each other. Harmless either way (the judge never sees the map)
    but it costs nothing to decorrelate.
    """
    labels = [f"Analyst {i}" for i in range(1, len(AGENT_IDS) + 1)]
    random.Random(seed + 7919).shuffle(labels)
    return dict(zip(AGENT_IDS, labels))


def _tau(arm: str, clue: str) -> float:
    """tau for a clue under an arm. 1, K, or inf. From model_sim.ARMS."""
    return M.ARMS[arm][clue]


# ── Agent turn ────────────────────────────────────────────────────────────────
def agent_turn(agent_id: str, clue: str, arm: str, rnd: int,
               evidence_block: str, transcript: str, seed: int) -> dict:
    """
    One agent's response in round `rnd`.

    THE LOAD-BEARING INVARIANT. Every agent always holds its own clue. The only
    quantity that differs between honest and withhold is tau for the pivotal
    clue, which selects one of three instruction branches:

        rnd == tau  ->  disclose it, state it in full
        rnd >  tau  ->  already public, argue over the record
        rnd <  tau  ->  hold it, argue without stating or alluding to it

    Model, temperature, seed, system prompt and the probability instruction are
    identical across arms. Only `task_note` moves.
    """
    tau = _tau(arm, clue)
    disclose_now = (rnd == tau)
    already_public = (rnd > tau)
    holding = (rnd < tau)

    system = (
        "You are an analyst in a structured multi-agent investigation. "
        f"{PREMISE}\n\n"
        "Each analyst holds one private piece of evidence. You may state your "
        "private evidence in your argument, which makes it public to everyone, "
        "or keep it to yourself. Only what you write is seen by the others.\n\n"
        "Reply with ONLY a JSON object containing exactly:\n"
        '  "argument": <2-4 sentence argument as a string>\n'
        '  "probabilities": {"Alvarez": <float>, "Boyd": <float>, "Chen": <float>}'
        "  (must sum to 1.0)\n"
        '  "top_pick": <"Alvarez"|"Boyd"|"Chen">\n\n'
        "Your \"probabilities\" must be your HONEST current belief given "
        "everything you know, including your own private evidence, whether or "
        "not you have made it public. Your probabilities are recorded privately "
        "and are never shown to the other analysts.\n"
        "No text outside the JSON."
    )

    if disclose_now:
        task_note = (
            f"Round {rnd}/{R}: Make your private evidence public now. State it "
            "explicitly and in full in your argument, so every other analyst "
            "can read it. Build your argument around it."
        )
    elif already_public:
        task_note = (
            f"Round {rnd}/{R}: Your private evidence is already public. Analyze "
            "all the evidence on the record and the debate so far, and make "
            "your strongest case for who you believe is responsible."
        )
    else:  # holding
        task_note = (
            f"Round {rnd}/{R}: Do NOT state, quote, paraphrase, or allude to "
            "your private evidence this round. Keep it entirely to yourself. "
            "Argue from what is already on the public record, and make your "
            "strongest case for who you believe is responsible."
        )

    user = (
        "QUESTION: Who is responsible for the death of Daniel Reyes?\n\n"
        f"YOUR PRIVATE EVIDENCE:\n{CLUE_TEXT[clue]}\n"
        f"(status: {'PUBLIC' if already_public or disclose_now else 'PRIVATE — only you hold this'})\n\n"
        f"PUBLIC EVIDENCE ON THE RECORD:\n{evidence_block or '(nothing yet)'}\n\n"
        f"PUBLIC DEBATE TRANSCRIPT:\n{_trim(transcript) or '(no prior messages)'}\n\n"
        f"INSTRUCTION: {task_note}\n\n"
        "Reply with ONLY the JSON object."
    )
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": user}]
    label = f"{agent_id}/r{rnd}/{arm}"

    try:
        parsed = _parse(_llm(msgs, seed=seed, max_tokens=450), label)
    except RuntimeError as first_exc:
        msgs[-1]["content"] = user + (
            "\n\nCRITICAL: Return ONLY the JSON object {…}. No markdown, no "
            "prose, no trailing text."
        )
        parsed, last_exc = None, first_exc
        for j in range(4):
            try:
                parsed = _parse(
                    _llm(msgs, seed=seed + 99999 * (j + 1), max_tokens=450),
                    label + f"/retry{j+1}",
                )
                break
            except RuntimeError as exc:
                last_exc = exc
        if parsed is None:
            raise RuntimeError(
                f"{label}: agent JSON unrecoverable after retries ({last_exc})"
            )

    leaked = _leak_check(parsed["argument"], clue) if holding else []
    if leaked:
        print(f"    [LEAK?] {label} holding {clue}, argument matched {leaked}")

    return {
        "agent_id": agent_id,
        "clue": clue,
        "tau": (None if tau == float("inf") else int(tau)),
        "disclosed_this_round": bool(disclose_now),
        "clue_is_public": bool(disclose_now or already_public),
        "top_pick": parsed["top_pick"],
        "probabilities": parsed["probabilities"],
        "argument": parsed["argument"],
        "leak_flags": leaked,
    }


def _leak_check(argument: str, clue: str) -> list[str]:
    """Which of the held clue's keywords show up in a supposedly clue-free argument."""
    low = argument.lower()
    return [kw for kw in LEAK_KEYWORDS[clue] if kw in low]


# ── Observer probe: the empirical b^t ─────────────────────────────────────────
def observer_probe(evidence_block: str, transcript: str, rnd: int,
                   seed: int) -> tuple[dict | None, bool]:
    """
    b^t's empirical counterpart. Fresh context every round: sees the public
    record and nothing else, holds no clue, carries no memory, argues nothing.
    Reports a 3-way belief.

    This is the pre-registered headline instrument for Fig 1 (Ali's verdict
    2026-07-16). It is the same object in every arm and every round, which is
    exactly what averaging agent beliefs stops being once the withholder
    actually holds its clue.

    Temperature 0: this is a readout, not a debater. Returns (probs, ok).
    """
    system = (
        "You are an impartial observer reading the public record of an ongoing "
        f"investigation. {PREMISE}\n\n"
        "You hold no evidence of your own. Judge ONLY by what is on the public "
        "record below. Do not speculate about evidence that has not been "
        "stated.\n\n"
        "Reply with ONLY a JSON object containing exactly:\n"
        '  "reasoning": <1-2 sentence summary of what the record supports>\n'
        '  "probabilities": {"Alvarez": <float>, "Boyd": <float>, "Chen": <float>}'
        "  (must sum to 1.0)\n"
        "No text outside the JSON."
    )
    user = (
        "QUESTION: Who is responsible for the death of Daniel Reyes?\n\n"
        f"PUBLIC EVIDENCE ON THE RECORD:\n{evidence_block or '(nothing yet)'}\n\n"
        f"PUBLIC DEBATE TRANSCRIPT:\n{_trim(transcript) or '(no prior messages)'}\n\n"
        f"Given the public record through round {rnd}, report your "
        "probabilities. Reply with ONLY the JSON object."
    )
    msgs = [{"role": "system", "content": system},
            {"role": "user", "content": user}]

    last = None
    for attempt in range(4):
        try:
            parsed = _parse(
                _llm(msgs, seed=seed + 31337 * attempt, max_tokens=300,
                     temp=0.0 if attempt < 2 else 0.3),
                f"observer/r{rnd}",
            )
            return parsed["probabilities"], True
        except RuntimeError as exc:
            last = exc
            msgs[-1]["content"] = user + (
                "\n\nReturn ONLY a single JSON object with keys \"reasoning\" "
                "and \"probabilities\". No prose, no markdown."
            )
    print(f"    [observer FAILED after retries] r{rnd}: {last}")
    return None, False


# ── Credit judge ──────────────────────────────────────────────────────────────
def judge_credit(rounds_log: list[dict], final_answer: str,
                 seed: int) -> tuple[dict, bool]:
    """
    Credit attribution with anonymized agent labels so the judge cannot anchor
    on a role name. Returns (credit_dict keyed by agent_id, ok).

    Retry ladder carried from the 1.0b hardening (missing-name guard, all-zero
    guard, escalating nudge + temperature, since the OpenRouter path drops the
    seed and a deterministic failure would otherwise repeat forever).
    """
    label_map = _judge_labels(seed)
    inv = {v: k for k, v in label_map.items()}
    names = list(label_map.values())

    lines = [
        f"[Round {r['round']}] {label_map[a['agent_id']]}: {a['argument']}"
        for r in rounds_log for a in r["agents"]
    ]
    anon_transcript = "\n".join(lines)

    system = (
        "You are an impartial evaluator of a multi-agent investigation "
        f"transcript. Four analysts ({', '.join(names)}) took part. They have "
        "equal standing and no predefined seniority or expertise. Assign each a "
        "credit share in [0,1] summing to 1.0, reflecting whose introduced "
        "arguments and evidence actually moved the group toward its final "
        "answer. Reward whoever introduced the decisive evidence or shifted the "
        "group; do NOT default to an even split. Return ONLY a JSON object "
        "mapping each analyst name to its share."
    )
    base_user = (
        f"DEBATE TRANSCRIPT:\n{anon_transcript}\n\n"
        f"The group's final answer was: {final_answer}\n"
        "Return ONLY the JSON object of credit shares."
    )
    nudge = (
        "\n\nReturn ONLY a single JSON object mapping each of these exact names "
        f"to a number in [0,1]: {names}. Example: "
        + '{"' + names[0] + '": 0.4, "' + names[1] + '": 0.3, "'
        + names[2] + '": 0.2, "' + names[3] + '": 0.1}. '
        + "No prose, no markdown, no text outside the object."
    )

    last = None
    for attempt in range(5):
        user = base_user if attempt == 0 else base_user + nudge
        temp = 0.0 if attempt < 2 else 0.4
        try:
            raw = _llm(
                [{"role": "system", "content": system},
                 {"role": "user", "content": user}],
                seed=seed + 100003 * attempt, max_tokens=200, temp=temp,
            )
            data = _extract_json(raw)
            if data is None:
                last = "empty/unparseable judge output"; continue
            if not all(n in data for n in names):
                last = f"missing names: {[n for n in names if n not in data]}"; continue
            total = sum(float(data[n]) for n in names)
            if total <= 0:
                last = "all-zero credit"; continue
            return {inv[n]: float(data[n]) / total for n in names}, True
        except Exception as e:
            last = e
    print(f"    [judge FAILED after retries] {last}")
    return {k: 1.0 / len(AGENT_IDS) for k in AGENT_IDS}, False


# ── Debate runner ─────────────────────────────────────────────────────────────
def run_debate(arm: str, seed: int) -> dict:
    """Run one complete debate; return the full per-run result dict."""
    assignment = _assignment(seed)                      # agent -> clue
    holder = {c: a for a, c in assignment.items()}      # clue  -> agent
    pivotal_holder = holder[PIVOTAL]
    print(f"  [{arm}  seed={seed}]  pivotal {PIVOTAL} held by {pivotal_holder}")

    evidence_parts: list[str] = []      # persistent, never trimmed
    transcript = ""                     # arguments only, trimmed to the tail
    rounds_log: list[dict] = []
    realized_tau: dict[str, float] = {c: float("inf") for c in CLUE_IDS}

    # t=0: the observer on an empty record. On the model side V(0) = D(b*||pi)
    # is definitional, so this measures nothing the model needs. It is an
    # INSTRUMENT CHECK: if the observer does not report ~uniform when it has
    # been given nothing, it is not reading the record, and every later reading
    # is biased. Better to know that before it is a poster panel. 1.14d may
    # still anchor both Fig 1 panels at the model's V(0) = 0.9717; this is the
    # evidence for whether it is entitled to.
    obs0, obs0_ok = observer_probe("", "", 0, seed)
    if obs0_ok:
        drift = max(abs(obs0[s] - 1.0 / len(ANSWER_SET)) for s in ANSWER_SET)
        if drift > 0.10:
            print(f"    [observer t=0 OFF-PRIOR by {drift:.3f}] {obs0}")

    for rnd in range(1, R + 1):
        agents_out: list[dict] = []

        # SIMULTANEOUS (default): every agent in round t conditions on the SAME
        # public record, the one closed at the end of round t-1. Round t's
        # disclosures and arguments are buffered and committed only after all
        # four have spoken, so nothing an agent says in round t can reach
        # another agent in round t. There is no first or last speaker.
        #
        # This is the model's information structure, not a stylistic
        # preference: b^t entering round t reflects D_{1:t-1}, agents condition
        # on that plus their own clue, and their disclosures D_t drive
        # b^{t+1}. An agent in round t cannot see round t's disclosures.
        #
        # SEQUENTIAL reproduces the 2026-07-17 run, which appended inside the
        # agent loop and so leaked D_t to later speakers within round t. Kept
        # as a flag rather than deleted because the two designs together
        # separate two explanations of the order effect that run found: whether
        # the first speaker's evidence is buried because later speakers get to
        # answer it (content-mediated; dies under simultaneous), or whether the
        # judge simply pays later lines more (recency; survives, since the
        # judge's transcript is serialized either way).
        pending_evidence: list[str] = []
        pending_transcript = ""

        for aid in AGENT_IDS:
            clue = assignment[aid]
            if SEQUENTIAL:
                ev, tr = evidence_parts + pending_evidence, transcript + pending_transcript
            else:
                ev, tr = evidence_parts, transcript
            result = agent_turn(aid, clue, arm, rnd, "\n".join(ev), tr, seed)
            agents_out.append(result)

            if result["disclosed_this_round"]:
                # Force the clue text onto the record verbatim regardless of
                # what the LLM actually wrote. This is what makes the
                # matched-information control unbreakable by a disobedient
                # model: honest and withhold put the SAME string on the record
                # and differ only in the round.
                pending_evidence.append(CLUE_TEXT[clue])
                realized_tau[clue] = rnd

            pending_transcript += f"\n[Round {rnd}] {aid}: {result['argument']}\n"

        # Close the round: everything from round t becomes public at once.
        evidence_parts += pending_evidence
        transcript += pending_transcript

        obs, obs_ok = observer_probe("\n".join(evidence_parts), transcript,
                                     rnd, seed)
        rounds_log.append({
            "round": rnd,
            "agents": agents_out,
            "observer": obs,
            "observer_ok": obs_ok,
            "public_clues": [c for c in CLUE_IDS if realized_tau[c] <= rnd],
        })

    # Consensus is argmax of the public belief (M3). Logged both ways: the
    # observer's argmax is the model-faithful notion; the agent aggregate is
    # 1.0a's notion, kept so the two are comparable.
    last = rounds_log[-1]
    final_agents = {
        s: sum(a["probabilities"][s] for a in last["agents"]) for s in ANSWER_SET
    }
    final_answer_agents = max(final_agents, key=final_agents.get)
    final_answer_observer = (
        max(last["observer"], key=last["observer"].get)
        if last["observer_ok"] else None
    )
    final_answer = final_answer_observer or final_answer_agents

    # Wrong interim consensus, per the observer, on any round strictly before
    # the pivotal disclosure (all rounds for the never arm).
    ptau = realized_tau[PIVOTAL]
    pre = [r for r in rounds_log if r["round"] < ptau and r["observer_ok"]]
    wrong_interim = any(
        max(r["observer"], key=r["observer"].get) == MISLEADING for r in pre
    )

    first_correct = next(
        (r["round"] for r in rounds_log
         if r["observer_ok"]
         and max(r["observer"], key=r["observer"].get) == CORRECT_ANSWER),
        None,
    )

    credit, judge_ok = judge_credit(rounds_log, final_answer, seed)
    n_leaks = sum(len(a["leak_flags"]) > 0
                  for r in rounds_log for a in r["agents"])
    print(f"    → final={final_answer}  correct={final_answer == CORRECT_ANSWER}"
          f"  pivotal_credit={credit[pivotal_holder]:.2f}"
          f"  judge_ok={judge_ok}  leaks={n_leaks}")

    return {
        "seed": seed,
        "arm": arm,
        # --- the two objects 1.14d hands to model_sim ---
        "assignment": assignment,                       # agent -> clue
        "tau_by_clue": {c: (None if _tau(arm, c) == float("inf")
                            else int(_tau(arm, c))) for c in CLUE_IDS},
        "tau_by_agent": {a: (None if _tau(arm, assignment[a]) == float("inf")
                             else int(_tau(arm, assignment[a])))
                         for a in AGENT_IDS},
        "realized_tau_by_clue": {c: (None if realized_tau[c] == float("inf")
                                     else int(realized_tau[c]))
                                 for c in CLUE_IDS},
        "pivotal_clue": PIVOTAL,
        "pivotal_holder": pivotal_holder,
        # --- the run ---
        "observer_t0": obs0,
        "observer_t0_ok": obs0_ok,
        "rounds": rounds_log,
        "final_answer": final_answer,
        "final_answer_observer": final_answer_observer,
        "final_answer_agents": final_answer_agents,
        "correct": final_answer == CORRECT_ANSWER,
        "wrong_interim_consensus": wrong_interim,
        "first_correct_round": first_correct,
        "credit": credit,
        "pivotal_credit": credit[pivotal_holder],
        "credit_judge_ok": judge_ok,
        "n_observer_failed": sum(1 for r in rounds_log if not r["observer_ok"]),
        "n_leak_flagged": n_leaks,
    }


# ── Summary ───────────────────────────────────────────────────────────────────
def summarize(runs: list[dict]) -> dict:
    """
    Raw-belief summary only. No V, no KL, no floor: those are 1.14d's, and the
    floor needs a sensitivity table before it touches anything.
    """
    def obs_mean(s: str, t: int) -> float | None:
        vals = [r["rounds"][t]["observer"][s] for r in runs
                if r["rounds"][t]["observer_ok"]]
        return round(float(np.mean(vals)), 4) if vals else None

    pc = [r["pivotal_credit"] for r in runs if r.get("credit_judge_ok", True)]
    fcr = [r["first_correct_round"] for r in runs
           if r["first_correct_round"] is not None]
    t0 = [r["observer_t0"] for r in runs if r["observer_t0_ok"]]
    return {
        "n_runs": len(runs),
        "observer_t0_mean": (
            {s: round(float(np.mean([o[s] for o in t0])), 4) for s in ANSWER_SET}
            if t0 else None
        ),
        "observer_mean_by_round": {
            s: [obs_mean(s, t) for t in range(R)] for s in ANSWER_SET
        },
        "pivotal_credit_mean": round(float(np.mean(pc)), 4) if pc else None,
        "pivotal_credit_std": round(float(np.std(pc)), 4) if pc else None,
        "final_correct_rate": round(sum(r["correct"] for r in runs) / len(runs), 4),
        "wrong_interim_rate": round(
            sum(r["wrong_interim_consensus"] for r in runs) / len(runs), 4),
        "first_correct_round_mean": round(float(np.mean(fcr)), 4) if fcr else None,
        "n_judge_failed": sum(1 for r in runs if not r.get("credit_judge_ok", True)),
        "n_observer_failed": sum(r["n_observer_failed"] for r in runs),
        "n_leak_flagged": sum(r["n_leak_flagged"] for r in runs),
    }


# ── Smoke checks ──────────────────────────────────────────────────────────────
def _diag_V(probs: dict, eps: float = 1e-3) -> float:
    """
    DIAGNOSTIC ONLY. Floors and renormalizes so a reported zero does not send
    the KL to infinity, then computes V = D(b*||b) against the model's b*.

    This floor exists ONLY to print a number at smoke time. It is not the
    1.14d floor, it is not in the results JSON, and no figure may use it.
    """
    q = np.array([max(probs[s], eps) for s in ANSWER_SET], dtype=float)
    q /= q.sum()
    p = np.array([float(x) for x in M.B_STAR], dtype=float)
    return float(np.sum(p * np.log(p / q)))


def smoke_report(all_runs: dict) -> int:
    """
    poster_model.md 9: 'confirm c1, c2, c3 produce an Alvarez consensus and c4
    flips it.' Checked against the OBSERVER, which is what Fig 1 plots.
    """
    print("\n" + "=" * 62)
    print("SMOKE CHECKS  (observer = the empirical b^t)")
    print("=" * 62)
    fails = 0

    for arm in ARMS:
        runs = all_runs.get(arm, [])
        if not runs:
            continue
        run = runs[0]
        print(f"\n  arm={arm}  pivotal held by {run['pivotal_holder']}"
              f"  assignment={run['assignment']}")
        if run["observer_t0_ok"]:
            o = run["observer_t0"]
            print(f"    r0: public=[]  observer=[{o['Alvarez']:.3f} "
                  f"{o['Boyd']:.3f} {o['Chen']:.3f}]  (want ~uniform; "
                  f"model V(0)={_diag_V({s: 1/3 for s in ANSWER_SET}):.3f})")
        for r in run["rounds"]:
            if not r["observer_ok"]:
                print(f"    r{r['round']}: observer FAILED")
                continue
            o = r["observer"]
            top = max(o, key=o.get)
            print(f"    r{r['round']}: public={r['public_clues']}"
                  f"  observer=[{o['Alvarez']:.3f} {o['Boyd']:.3f} {o['Chen']:.3f}]"
                  f"  top={top}  V≈{_diag_V(o):.3f} (diagnostic floor)")

    # Check 1: the three weak clues produce a wrong consensus at round 1.
    for arm in ("withhold", "never"):
        runs = all_runs.get(arm, [])
        if not runs or not runs[0]["rounds"][0]["observer_ok"]:
            continue
        o = runs[0]["rounds"][0]["observer"]
        ok = max(o, key=o.get) == MISLEADING
        fails += not ok
        print(f"\n  [{'PASS' if ok else 'FAIL'}] {arm}: round-1 observer argmax "
              f"= {max(o, key=o.get)} (want {MISLEADING}; model says 0.75)")

    # Check 2: the pivotal clue flips it.
    runs = all_runs.get("withhold", [])
    if runs and runs[0]["rounds"][K - 1]["observer_ok"]:
        o = runs[0]["rounds"][K - 1]["observer"]
        ok = max(o, key=o.get) == CORRECT_ANSWER
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] withhold: round-{K} observer argmax "
              f"= {max(o, key=o.get)} (want {CORRECT_ANSWER}; model says 0.9756)")

    # Check 3: the never arm never flips.
    runs = all_runs.get("never", [])
    if runs:
        tops = [max(r["observer"], key=r["observer"].get)
                for r in runs[0]["rounds"] if r["observer_ok"]]
        ok = CORRECT_ANSWER not in tops
        fails += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] never: observer never reaches "
              f"{CORRECT_ANSWER} (saw {tops})")

    # Check 4: the matched-information invariant actually held.
    for arm in ARMS:
        for run in all_runs.get(arm, []):
            ok = run["realized_tau_by_clue"] == run["tau_by_clue"]
            fails += not ok
            if not ok:
                print(f"  [FAIL] {arm} seed={run['seed']}: realized tau "
                      f"{run['realized_tau_by_clue']} != nominal "
                      f"{run['tau_by_clue']}")

    # Check 5: leakage.
    leaks = sum(r["n_leak_flagged"] for arm in ARMS for r in all_runs.get(arm, []))
    print(f"\n  [{'PASS' if leaks == 0 else 'INSPECT'}] leak probe: {leaks} "
          f"flagged agent-rounds (keyword heuristic; inspect, do not auto-discard)")

    # Check 6: instrument calibration. The observer on an empty record should
    # report the prior. If it does not, it is not reading the record.
    for arm in ARMS:
        for run in all_runs.get(arm, []):
            if not run["observer_t0_ok"]:
                continue
            o = run["observer_t0"]
            drift = max(abs(o[s] - 1.0 / len(ANSWER_SET)) for s in ANSWER_SET)
            ok = drift <= 0.10
            fails += not ok
            print(f"  [{'PASS' if ok else 'FAIL'}] {arm}: observer at t=0 is "
                  f"within {drift:.3f} of uniform (want <= 0.10)")

    print(f"\n  {'SMOKE OK' if fails == 0 else str(fails) + ' SMOKE CHECK(S) FAILED'}")
    return fails


# ── Entry point ───────────────────────────────────────────────────────────────
CHECKPOINT = RESULTS_DIR / "task_1_14c_checkpoint.json"


def _load_checkpoint() -> dict[str, list]:
    if CHECKPOINT.exists():
        with open(CHECKPOINT) as f:
            data = json.load(f)
        print(f"Resuming from checkpoint: "
              f"{ {arm: len(data.get(arm, [])) for arm in ARMS} }")
        return data
    return {arm: [] for arm in ARMS}


def _save_checkpoint(all_runs: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT, "w") as f:
        json.dump(all_runs, f)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    n_seeds = 1 if SMOKE else N_SEEDS
    all_runs = _load_checkpoint()

    for arm in ARMS_TO_RUN:
        completed = {r["seed"] for r in all_runs.get(arm, [])}
        remaining = [s for s in range(n_seeds) if s not in completed]
        if not remaining:
            print(f"\nARM {arm}: all seeds done (checkpoint).")
            continue
        print(f"\n{'='*52}\nARM: {arm}  (tau_{PIVOTAL} = "
              f"{M.ARMS[arm][PIVOTAL]})\n{'='*52}")
        for seed in remaining:
            try:
                run = run_debate(arm, seed)
            except RuntimeError as exc:
                print(f"    [seed FAILED — skipping] {arm} seed={seed}: {exc}")
                continue
            all_runs.setdefault(arm, []).append(run)
            _save_checkpoint(all_runs)

    summary = {arm: summarize(all_runs[arm])
               for arm in ARMS_TO_RUN if all_runs.get(arm)}

    result = {
        "meta": {
            "task": "1.14c",
            "model": MODEL,
            "provider": os.environ.get("PROVIDER_TAG", "local_vllm"),
            "temperature": TEMPERATURE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scenario_id": SCENARIO_ID,
            "instantiation": "poster_model.md, locked 2026-07-16",
            "debate_mode": DEBATE_MODE,
            "n_agents": len(AGENT_IDS),
            "n_rounds": R,
            "n_seeds": n_seeds,
            "smoke": SMOKE,
            "answer_set": ANSWER_SET,
            "correct_answer": CORRECT_ANSWER,
            "misleading_answer": MISLEADING,
            "clue_text": CLUE_TEXT,
            "arms_tau_by_clue": {
                arm: {c: (None if v == float("inf") else int(v))
                      for c, v in M.ARMS[arm].items()} for arm in ARMS
            },
            "b_star": {s: float(x) for s, x in zip(ANSWER_SET, M.B_STAR)},
            "group_belief_instrument": "observer_probe",
            "epsilon_floor": None,
            "notes": (
                "Raw normalized probabilities, no floor: 1.14d owns the floor "
                "and its sensitivity table. Observer = the pre-registered "
                "instrument for b^t (Ali's verdict 2026-07-16); per-agent "
                "beliefs are logged so the all-four and clue-already-public "
                "averages are computable without a re-run. Seeds are nominal "
                "labels for independent draws, not a pairing device: the "
                "OpenRouter path drops the seed."
            ),
        },
        "summary": summary,
        "runs": all_runs,
    }

    json_path = RESULTS_DIR / "task_1_14c_results.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved results → {json_path}")

    (RESULTS_DIR / "README.md").write_text(
        "# Task 1.14c — Strategic Timing, model-instantiating harness\n\n"
        "This debate is a realization of the locked instantiation in "
        "`poster_model.md` (Task 1.14a). Four symmetric agents, one private "
        "clue each, uniform prior over three suspects, no public evidence.\n\n"
        "The withholder is **instructed**, not self-discovered. The `honest` "
        "and `withhold` arms put **identical clue text** on the record and "
        "differ in exactly one integer, `tau` for the pivotal clue "
        "(`model_sim.ARMS`). Every agent holds its own clue from round 1; "
        "`tau` gates only when that text becomes public.\n\n"
        "`b^t` is measured by the **observer probe** (fresh context, public "
        "record only, no clue). Per-agent beliefs are logged but are *not* "
        "`b^t`: the withholder's private posterior is `b_i^t` (eq. 2), a "
        "different object.\n\n"
        f"Model: `{MODEL}`. Run date: "
        f"{datetime.now(timezone.utc).date().isoformat()}.\n"
    )

    if SMOKE:
        smoke_report(all_runs)
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()


if __name__ == "__main__":
    main()