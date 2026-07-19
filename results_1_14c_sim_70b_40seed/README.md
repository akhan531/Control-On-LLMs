# Task 1.14c — Strategic Timing, model-instantiating harness

This debate is a realization of the locked instantiation in `poster_model.md` (Task 1.14a). Four symmetric agents, one private clue each, uniform prior over three suspects, no public evidence.

The withholder is **instructed**, not self-discovered. The `honest` and `withhold` arms put **identical clue text** on the record and differ in exactly one integer, `tau` for the pivotal clue (`model_sim.ARMS`). Every agent holds its own clue from round 1; `tau` gates only when that text becomes public.

`b^t` is measured by the **observer probe** (fresh context, public record only, no clue). Per-agent beliefs are logged but are *not* `b^t`: the withholder's private posterior is `b_i^t` (eq. 2), a different object.

Model: `meta-llama/llama-3.3-70b-instruct`. Run date: 2026-07-18.
