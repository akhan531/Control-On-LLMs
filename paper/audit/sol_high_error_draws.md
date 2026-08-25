# B1 — sol-high's error draws (diagnostic, read-only)

Population: **PARTIAL_RULED (derivable-absences), δ = 0, all cells minus P4**, five admitted
configurations. Source: `s5_prior_crossing.py` logic recomputed against `results_v2/v2_results_live.json`.
The paper's claim region is **"above the prior OR exactly at level(b_pos)."** In the target
frame, above-prior = level ≥ 2 (P > 0.5); level(b_pos) = l_pos is 2 or 3 in every cell, so
"at l_pos" is a subset of "above prior" and the claim-region count equals the above-prior count.

## sol-high, the config in question

- **Error draws (level ≠ l_cor): 16** — the paper's "produces no error draws at all" is wrong;
  it has 16.
- **At level(b_pos): 0.**
- **Level distribution of the 16 error draws:** level 0 → **0**, level 1 → **16**, level 2 → **0**,
  level 3 → **0**. All 16 sit at level 1, which is below the prior and reachable by symmetric
  shrinkage.
- **In the claim region (above prior OR at l_pos): 0.**

## The exclusion condition, quoted from `s5_prior_crossing.py`

> "classify each gated configuration's error mass as PRIOR-SHRINKAGE-CONSISTENT … or
> CONSISTENT (mass strictly above P = 0.5, or sitting exactly at level(b_pos))
> * a configuration with ZERO above-prior mass is EXCLUDED from the asymmetry claim,
>   not counted as evidence against it; reported as instrument-limited"

The runtime line printed for sol-high: `sol-high  zero above-prior mass anywhere in RULED arms
-> EXCLUDED (instrument-limited, not a counterexample)`.

So the exclusion is **specifically on the above-prior (level ≥ 2, or exactly at level(b_pos))
criterion** — not on having zero error draws. sol-high is excluded because none of its 16
error draws land in the claim region, not because it produced none.

## The five admitted configurations on the same criterion

PARTIAL_RULED, δ = 0, all cells minus P4. `claim` = error draws with level ≥ 2 **or** at l_pos.

| config | n | error draws | level 0/1/2/3 | at l_pos | claim region | paper cites |
|---|---|---|---|---|---|---|
| sol-hi (sol-high) | 140 | **16** | 0 / 16 / 0 / 0 | 0 | **0** | "no error draws at all" |
| sol-no (sol-none) | 130 | 91 | 0 / 83 / 8 / 0 | 6 | 8 | 8 of 91 |
| glm-hi (glm-high) | 140 | 52 | 0 / 35 / 12 / 5 | 9 | 17 | 17 of 52 |
| dsk-hi (deepseek-high) | 134 | 80 | 0 / 30 / 34 / 16 | 41 | 50 | 50 of 80 |
| glm | 140 | 140 | 0 / 0 / 76 / 64 | 108 | 140 | 140 of 140 (108 at l_pos) |

## What this means for the sentence (not resolved here, per instruction)

- The universal "displaced mass sits above the prior or exactly at level(b_pos)" holds across
  **four of five** admitted configs (sol-none, glm-high, deepseek-high, glm), each with
  claim-region mass 8 / 17 / 50 / 140.
- **sol-high has error mass (16 draws) but none of it in the claim region** — all 16 are at
  level 1, below the prior. So it is neither a numerator entry nor a config "with no error
  draws." The correct framing is "no error draws in the claim region" (equivalently, all its
  error mass is below the prior and symmetric-shrinkage-reachable), which makes the statement
  a four-of-five universal, not a five-of-five one.

## Propagation of the "0 error draws" error

The same wrong wording appears in two other places (both read-only for this audit):

- `paper/context/claims_to_evidence.md` row 2.5 (line 106): "sol-high has 0 error draws, so the
  test is undefined rather than failed."
- `scratch_2_4c/example_1/example1README.md` line 359: "sol-high has 0 error draws, so the test
  is undefined rather than failed."

The ledger is therefore not a safe backstop for this sentence; the data is authoritative.
