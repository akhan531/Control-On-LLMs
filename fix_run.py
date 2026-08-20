"""
fix_run.py — repairs the botched fix_truncation.py pass, then prepares a clean retry.

    python fix_run.py
    python silence_v2_harness.py     # retries ONLY the remaining truncated draws
    python silence_v2_analyze.py

What went wrong
---------------
fix_truncation.py crashed on its first regex, so patch_harness() never finished and
mark_terminal() never ran. The subsequent re-run therefore executed with:

  * the ORIGINAL token budget, so truncation was retried but not actually fixed
    (49 -> 22 by luck of the draw, not by design); and
  * NO terminal marking, so 33 off-menu draws were retried until they parsed.

The second is the serious one. D16 says an off-menu response is excluded and counted.
Retrying it until it parses is selection on the outcome: a draw that failed the schema
once gets a second chance that a draw which passed never gets. The deepseek family lost
34 PARSE failures down to 1 that way, which is ~8% of its draws replaced by resampled
ones.

The regex bug: `[^}]*?` cannot cross the nested `"reasoning": {...}` dict that sits
between the config name and max_tokens, so it never matched. Fixed with a non-greedy
DOTALL span.

What this script does
---------------------
1. Rewrites the checkpoint. For any draw whose history is PARSE-then-success, the
   success is DISCARDED and the original off-menu failure restored and marked terminal.
   A TRUNCATED-then-success history is kept: completing an interrupted measurement at
   the same prompt and seed is not selection.
2. Marks every remaining off-menu / request failure terminal so the next run skips them.
3. Raises the reasoning budget for the high-effort configs.
4. Teaches resume to honour terminal.

After this, the only draws still outstanding are genuine truncations, and those are the
only ones the re-run will attempt.
"""

import json
import os
import re
from collections import defaultdict

CHECKPOINT = "results_v2/checkpoint_live.jsonl"
HARNESS = "silence_v2_harness.py"

NEW_MAX_TOKENS = {"sol-high": 12000, "deepseek-high": 16000, "glm-high": 16000}


def key(r):
    return f"{r['config']}|{r['stimulus_id']}|{r['seed']}"


def decontaminate(path=CHECKPOINT):
    if not os.path.exists(path):
        raise SystemExit(f"no checkpoint at {path}")
    recs = [json.loads(l) for l in open(path) if l.strip()]
    print(f"  read {len(recs)} records")

    hist = defaultdict(list)
    for i, r in enumerate(recs):
        hist[key(r)].append(i)

    drop, restored = set(), 0
    for k, idxs in hist.items():
        if len(idxs) < 2:
            continue
        saw_parse = None
        for i in idxs:
            r = recs[i]
            if not r.get("ok") and r.get("failure") in ("PARSE", "REQUEST"):
                saw_parse = i
            elif r.get("ok") and saw_parse is not None:
                # success that only exists because an off-menu draw was retried
                drop.add(i)
                recs[saw_parse]["terminal"] = True
                recs[saw_parse]["note"] = "off-menu; retry discarded per D16"
                restored += 1
                saw_parse = None

    by_cfg = defaultdict(int)
    for i in drop:
        by_cfg[recs[i]["config"]] += 1
    print(f"  discarding {len(drop)} retry-until-parse successes: {dict(by_cfg)}")
    print(f"  restoring {restored} off-menu failures as terminal")

    kept = [r for i, r in enumerate(recs) if i not in drop]
    n_term = 0
    for r in kept:
        if not r.get("ok") and r.get("failure") in ("PARSE", "REQUEST"):
            r["terminal"] = True
            n_term += 1

    # drop any stale failure record for a key that legitimately succeeded later
    ok_keys = {key(r) for r in kept if r.get("ok")}
    final = [r for r in kept if r.get("ok") or key(r) not in ok_keys]

    with open(path, "w") as f:
        for r in final:
            f.write(json.dumps(r) + "\n")

    ok = sum(1 for r in final if r.get("ok"))
    term = sum(1 for r in final if r.get("terminal"))
    trunc = sum(1 for r in final
                if not r.get("ok") and r.get("failure") == "TRUNCATED")
    print(f"  checkpoint now: {ok} ok, {term} terminal (excluded), "
          f"{trunc} truncated -> to retry")
    return trunc


def patch_harness(path=HARNESS):
    src = open(path).read()
    for cfg, val in NEW_MAX_TOKENS.items():
        # non-greedy DOTALL span: the nested "reasoning": {...} dict contains '}',
        # which is what defeated the previous [^}]*? pattern.
        pat = re.compile(r'("' + re.escape(cfg) + r'":\s*\{.*?"max_tokens":\s*)(\d+)',
                         re.S)
        m = pat.search(src)
        assert m, f"could not locate max_tokens for {cfg}"
        old = m.group(2)
        src = src[:m.start()] + m.group(1) + str(val) + src[m.end():]
        print(f"  {cfg}: max_tokens {old} -> {val}")

    if '"terminal"' not in src:
        old = '''            rec = json.loads(line)
            if rec.get("ok"):
                done[key_of(rec["config"], rec["stimulus_id"], rec["seed"])] = rec
    return done'''
        new = '''            rec = json.loads(line)
            # Successes are done. So are TERMINAL failures: an off-menu response is a
            # model output to be counted (D16), not a draw to retry until it parses.
            if rec.get("ok") or rec.get("terminal"):
                done[key_of(rec["config"], rec["stimulus_id"], rec["seed"])] = rec
    return done'''
        assert old in src, "resume block not found"
        src = src.replace(old, new)
        print("  resume logic: terminal failures now skipped")
    open(path, "w").write(src)


if __name__ == "__main__":
    print("decontaminating checkpoint:")
    n = decontaminate()
    print("patching harness:")
    patch_harness()
    print(f"\n{n} truncated draws outstanding.")
    print("now run:  python silence_v2_harness.py")
