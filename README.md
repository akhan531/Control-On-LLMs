# Channels to Targets: A Closed-Form Coordinate System for Silence-Blindness in LLM Observers

Code, stimuli, and draw records for the EIML3 @ NeurIPS 2026 workshop paper.
The paper is in [`paper/main.pdf`](paper/main.pdf).

## What the paper does

Large language models are usually evaluated on evidence that is written in their
input. This paper studies a complementary question: can a model reason from
evidence that is **not** written, but is derivable from a known disclosure rule?
An observer reads a transcript in which `N` analysts each ran a binary assay, but
under some conditions only the positive reports are filed and the `N - k`
negatives are left as absences to be recovered. Writing down which channels a
transcript exposes fixes, in closed form, both the operations a correct observer
must perform and the target posterior it should hold. Every elicited answer
therefore has a measurable position between two reference beliefs: the
silence-blind belief `b_pos` (positives only) and the target `b_tar` (the
correct posterior once the silence is read).

Across the five configurations that clear a competence gate, the error runs one
way: among 150 draws where over-weighting could register, 103 reach the target
and 47 miss it, every miss under-weighting the silence rather than over-weighting
it. Enumerating the absences repairs a model's failure to *identify* them without
repairing its failure to *interpret* them.

## Repository layout

```
paper/            the submitted paper and its figures
  main.pdf          the paper
  main.tex          LaTeX source
  figures/          the five figure PDFs + the generators that produce them
design/           the instrument
  cells.csv         the 14 cells: N, k, p, b_pos, target, and their ordinal levels
  spec.md           conditions, the 4-level response scale, band gaps, forbidden-word list
  models.md         the 7 configurations / model roster (draw-weighted gate scores)
stimuli/          prompt generation (Appendix C)
  silence_v2_model.py     the belief math (b_pos, b_tar, levels)
  silence_v2_stimuli.py   generates FULL, BLIND, RULED  -> silence_v2_stimuli.json
  arith_d0_stimuli.py     generates ARITH               -> arith_d0_stimuli.json
  w1_stimuli.py           generates the calibration pre-test -> w1_stimuli.json
harness/          runs the models over the stimuli via the OpenRouter API
  silence_v2_harness.py   the FULL/BLIND/RULED campaign
  arith_d0_harness.py     the ARITH arm
  w1_harness.py           the calibration pre-test
results/          the draw records (the raw data)
  campaign/         v2_results_live.json (FULL/BLIND/RULED), v2_gates.json (competence gate)
  arith/            arith_d0_results_live.json (the enumerated-absences arm)
  calibration/      w1_results_live.json and the derived gate/low-side files
```

## Reproducing the results

Requirements: Python 3 with `numpy` and `matplotlib` (for the figures), and
`pypdf` only if you want to inspect the PDF. No other dependencies.

**The draw records are included, so every number and figure in the paper
reproduces offline, without re-running any model or holding an API key.** Each
figure generator recomputes the paper's numbers from `results/`, asserts them
(a mismatch is a hard failure, not a silent redraw), and then plots:

```
python paper/figures/make_results.py     # Fig 1a: signed error on the D-cells (47-0)
python paper/figures/make_occupancy.py   # Fig 1b: silence-blind occupancy
python paper/figures/make_residence.py   # Fig 2a: occupancy collapse (identification repaired)
python paper/figures/make_interior.py    # Fig 2b: interior mass (interpretation not repaired)
python paper/figures/make_calmap.py      # Appendix B: the calibration confidence map
```

To regenerate the stimuli themselves:

```
python stimuli/silence_v2_stimuli.py     # -> stimuli/silence_v2_stimuli.json
python stimuli/arith_d0_stimuli.py       # -> stimuli/arith_d0_stimuli.json
python stimuli/w1_stimuli.py             # -> stimuli/w1_stimuli.json
```

Re-collecting the draws (only needed to reproduce from scratch) requires an
OpenRouter API key and runs `harness/*.py` over the stimuli; the roster and
decoding settings are in [`design/models.md`](design/models.md).

## Draw records

Each record in a `*_results_live.json` file carries the stimulus id, the
configuration, the model's parsed `candidate` and `confidence`, and an `ok` flag
(false for truncated, unparseable, or transport failures). Counts: the main
campaign holds 5,808 usable draws of 5,950 attempted; the ARITH arm 959 of 980;
the calibration pre-test 659 of 672.

## Provenance and licensing

The exact analysis snapshot cited in the paper is tagged
[`eiml3-submission`](https://github.com/akhan531/Control-On-LLMs/releases/tag/eiml3-submission)
(commit `9ade4d4`). The repository records model slugs, not their terms of use;
model access was through the OpenRouter API. No `LICENSE` file is included.
