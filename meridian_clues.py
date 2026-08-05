"""
meridian_clues.py — loader, instantiator, validator and freeze gate for the
meridian_v2 clue texts (Task 2.1f).

The texts live in meridian_clues.json: 9 accusatory templates carrying a
{SUSPECT} slot plus 9 null texts, expanding to the 27 realized texts of
meridian_v2_scenario.md 1.6. This module is the only thing that reads that
file, so the harness never touches a raw string.

Why the templates are structured this way. Under the version-3 premise the two
suspects have identical standing, so the A and C texts of a channel are the
same sentence with a different name in it. That makes "equally specific and
equally vivid within a channel" a property of the construction rather than a
reviewer's judgment call, and the mirroring section below PROVES it holds
rather than assuming it.

The rest of section 1.6's authoring constraints are worth nothing as
intentions. As checks that fail the build they are worth something.

Run

    python meridian_clues.py

to validate, print the realized 27, and emit the freeze hash.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

CLUES_PATH = Path(__file__).with_name("meridian_clues.json")
PLACEHOLDER = "{SUSPECT}"

OUTCOMES = ("A", "C", "O")
PROTECTED, EXPOSED = 0, 1          # slot indices, matching meridian_model.SLOTS
SLOT_OF_OUTCOME = {"A": PROTECTED, "C": EXPOSED}

# Scenario 1.6: a template is instantiated with either surname, so it must not
# carry a gender cue the model could resolve differently depending on the name.
BANNED_PRONOUNS = {
    "he", "she", "him", "her", "his", "hers", "himself", "herself",
}

# Scenario 1.1 and 1.6: nothing may accrete into a character sketch or restore
# the standing asymmetry version 3 removed.
BANNED_STANDING = {
    "associate", "junior", "senior", "tenure", "veteran", "eighteen",
    "fourteen", "joined", "newer", "longtime", "long-time", "newly",
}

# Surnames belong to the harness's per-seed assignment, never to a text.
BANNED_NAMES = {"alvarez", "chen"}

# Distinctness is measured on content words only.
_STOPWORDS = {
    "a", "an", "and", "any", "are", "as", "at", "be", "been", "before", "both",
    "but", "by", "for", "from", "had", "has", "have", "in", "into", "is", "it",
    "its", "no", "not", "of", "on", "one", "or", "out", "over", "own", "that",
    "the", "their", "them", "then", "there", "these", "they", "this", "to",
    "was", "were", "what", "when", "which", "who", "with", "after", "again",
    "all", "also", "than", "up", "only", "each", "other", "some", "about",
}

MAX_PAIRWISE_OVERLAP = 0.30   # Jaccard on content words, across channels


# ─────────────────────────────────────────────────────────────────────────────
# Loading and instantiation
# ─────────────────────────────────────────────────────────────────────────────

def load(path: Path = CLUES_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def freeze_hash(path: Path = CLUES_PATH) -> str:
    """SHA-256 of the raw file. Recorded in the scenario spec at freeze."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def realize(channel: dict, outcome: str, protected: str, exposed: str) -> str:
    """
    Render channel x outcome into the text an agent reports.

    outcome is 'A', 'C' or 'O'. 'A' points at the protected suspect, 'C' at the
    exposed one, 'O' is the null. protected and exposed are the surnames this
    seed assigned to the two slots.
    """
    if outcome == "O":
        return channel["null_text"]
    if outcome == "A":
        return channel["accusatory_template"].replace(PLACEHOLDER, protected)
    if outcome == "C":
        return channel["accusatory_template"].replace(PLACEHOLDER, exposed)
    raise ValueError(f"unknown outcome {outcome!r}")


def realize_vector(clues: list[str], protected: str, exposed: str,
                   data: dict | None = None) -> list[dict]:
    """
    Turn a clue vector into per-agent findings. Channels are nested, so agent i
    works channel i+1 and N = 3 uses channels 1 to 3 (scenario 1.2).
    """
    data = data or load()
    channels = data["channels"]
    if len(clues) > len(channels):
        raise ValueError(f"{len(clues)} agents but only {len(channels)} channels")
    return [
        {
            "agent_index": i,
            "channel": channels[i]["index"],
            "line_of_inquiry": channels[i]["line_of_inquiry"],
            "outcome": c,
            "text": realize(channels[i], c, protected, exposed),
        }
        for i, c in enumerate(clues)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Tokenizing
# ─────────────────────────────────────────────────────────────────────────────

def _words(text: str) -> list[str]:
    """
    Tokenize to bare lowercase words, stripping possessives.

    Without the strip, "associate's" is a single token that no banned word ever
    matches and the whole gate silently stops working. Both straight and curly
    apostrophes are handled, since the texts are authored in prose.
    """
    raw = re.findall(r"[a-z][a-z'\u2019\-]*", text.lower())
    return [re.sub(r"['\u2019]s$|['\u2019]$", "", w) for w in raw]


def _content(text: str) -> set[str]:
    return {w for w in _words(text) if w not in _STOPWORDS and len(w) > 2}


def _jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate(data: dict, verbose: bool = True) -> tuple[list[str], list[str]]:
    """Returns (failures, warnings). Empty failures means the set is freezable."""
    fails: list[str] = []
    warns: list[str] = []
    channels = data.get("channels", [])

    # ── structure ────────────────────────────────────────────────────────────
    if len(channels) != 9:
        fails.append(f"expected 9 channels, found {len(channels)}")
    if [c.get("index") for c in channels] != list(range(1, len(channels) + 1)):
        fails.append("channel indices are not 1..N in order")
    if len({c.get("line_of_inquiry") for c in channels}) != len(channels):
        fails.append("line_of_inquiry values are not distinct")

    # ── per-channel content constraints ──────────────────────────────────────
    for ch in channels:
        i = ch.get("index")
        tmpl = ch.get("accusatory_template", "")
        null = ch.get("null_text", "")

        if not tmpl or not null:
            fails.append(f"ch{i}: missing an authored string")
            continue
        if tmpl.count(PLACEHOLDER) < 1:
            fails.append(f"ch{i}: template has no {PLACEHOLDER}")
        if PLACEHOLDER in null:
            fails.append(f"ch{i}: null text must not carry {PLACEHOLDER}")

        for label, text in (("template", tmpl), ("null", null)):
            words = set(_words(text))
            for w in sorted(words & BANNED_PRONOUNS):
                fails.append(f"ch{i} {label}: pronoun {w!r} (scenario 1.6, pronoun-free)")
            for w in sorted(words & BANNED_STANDING):
                fails.append(f"ch{i} {label}: standing word {w!r} (scenario 1.1, equalized)")
            for w in sorted(words & BANNED_NAMES):
                fails.append(f"ch{i} {label}: hardcoded surname {w!r} (scenario 1.5)")

            non_ascii = sorted({c for c in text if ord(c) > 127})
            if non_ascii:
                warns.append(f"ch{i} {label}: non-ASCII {non_ascii}, "
                             f"consider an ASCII equivalent for prompt robustness")

    # ── mirroring, the central property of the version-3 design ──────────────
    # A and C must differ by the name alone, and swapping the surname
    # assignment must be a pure relabeling. Both are proved, not assumed.
    for ch in channels:
        i = ch.get("index")
        a_text = realize(ch, "A", "Alvarez", "Chen")
        c_text = realize(ch, "C", "Alvarez", "Chen")
        if a_text.replace("Alvarez", "Chen") != c_text:
            fails.append(f"ch{i}: A does not map to C by name substitution alone "
                         f"(scenario 1.6, mirroring)")

        a_swapped = realize(ch, "A", "Chen", "Alvarez")
        if a_text.replace("Alvarez", "Chen") != a_swapped:
            fails.append(f"ch{i}: surname assignment is not a pure relabeling "
                         f"(scenario 1.5, counterbalancing)")

    # ── cross-channel distinctness ───────────────────────────────────────────
    # Scenario 1.6 and 5.1 name this as the single largest source of a false null.
    worst = (0.0, None, None)
    for x in range(len(channels)):
        for y in range(x + 1, len(channels)):
            a = _content(channels[x]["accusatory_template"].replace(PLACEHOLDER, ""))
            b = _content(channels[y]["accusatory_template"].replace(PLACEHOLDER, ""))
            j = _jaccard(a, b)
            if j > worst[0]:
                worst = (j, channels[x]["index"], channels[y]["index"])
            if j > MAX_PAIRWISE_OVERLAP:
                fails.append(f"ch{channels[x]['index']} vs ch{channels[y]['index']}: "
                             f"content overlap {j:.2f} exceeds {MAX_PAIRWISE_OVERLAP}")

    # ── realization smoke ────────────────────────────────────────────────────
    if len(channels) >= 3:
        v = realize_vector(["C", "A", "O"], "Alvarez", "Chen", data)
        if [x["channel"] for x in v] != [1, 2, 3]:
            fails.append("nesting broken: N=3 does not use channels 1,2,3")
        if "Chen" not in v[0]["text"]:
            fails.append("C outcome does not name the exposed suspect")
        if "Alvarez" not in v[1]["text"]:
            fails.append("A outcome does not name the protected suspect")
        if re.search(r"\b(Alvarez|Chen)\b", v[2]["text"]):
            fails.append("O outcome names a suspect")

    realized = {realize(ch, o, "Alvarez", "Chen") for ch in channels for o in OUTCOMES}
    if len(realized) != 3 * len(channels):
        fails.append(f"realized texts are not all distinct "
                     f"({len(realized)} of {3 * len(channels)})")

    # ── length parity, reported not enforced ─────────────────────────────────
    if verbose and channels:
        acc = [len(_words(c["accusatory_template"])) for c in channels]
        nul = [len(_words(c["null_text"])) for c in channels]
        print(f"  accusatory words: min {min(acc)} max {max(acc)} "
              f"mean {sum(acc)/len(acc):.1f}  {acc}")
        print(f"  null words:       min {min(nul)} max {max(nul)} "
              f"mean {sum(nul)/len(nul):.1f}  {nul}")
        print(f"  most similar channel pair: {worst[1]} and {worst[2]}, "
              f"overlap {worst[0]:.3f} (ceiling {MAX_PAIRWISE_OVERLAP})")
        for label, lens in (("accusatory", acc), ("null", nul)):
            if max(lens) > 2 * min(lens):
                warns.append(f"{label} length spread: longest is more than "
                             f"twice the shortest, check specificity parity")

    return fails, warns


def main() -> int:
    data = load()
    print(f"meridian clue texts, version {data.get('version')}, "
          f"status {data.get('status')}")
    print(f"  {len(data['channels'])} channels, "
          f"{2 * len(data['channels'])} authored strings, "
          f"{3 * len(data['channels'])} realized texts\n")

    print("Validation")
    fails, warns = validate(data)
    for f in fails:
        print(f"  [FAIL] {f}")
    for w in warns:
        print(f"  [warn] {w}")
    if not fails:
        print("  [ok  ] structure, pronoun-free, no standing cues, no hardcoded names")
        print("  [ok  ] mirroring proved: A -> C by name substitution alone")
        print("  [ok  ] surname assignment proved a pure relabeling")
        print("  [ok  ] cross-channel distinctness under the overlap ceiling")
        print("  [ok  ] nesting and realization smoke")

    print("\nRealized texts, shown with protected=Alvarez exposed=Chen")
    for ch in data["channels"]:
        print(f"\n  channel {ch['index']}: {ch['line_of_inquiry']}")
        for outcome in OUTCOMES:
            print(f"    {outcome}: {realize(ch, outcome, 'Alvarez', 'Chen')}")

    print(f"\nfreeze hash (sha256): {freeze_hash()}")
    print("  record this in meridian_v2_scenario.md section 8 at freeze")

    print(f"\n{'PASS' if not fails else 'FAIL'}: {len(fails)} failing check(s), "
          f"{len(warns)} warning(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
