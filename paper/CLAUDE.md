# paper/ — EIML3 workshop submission

Working directory for "Channels to Targets: A Closed-Form Coordinate System for
Silence-Blindness in LLM Observers." EIML3 @ NeurIPS 2026, non-archival.
Deadline 2026-08-29, 6:00 PM ET. Four pages excluding references.

Build: `tectonic -X compile main.tex`

## Read these before editing prose

Read in this precedence order. Where two disagree, the higher one wins.

1. `context/claims_to_evidence.md` — authoritative on every number, and on the
   population each number is scoped to. Revision 4.
2. `context/eiml_paper_outline.md` — authoritative on section numbering,
   paragraph order, and what each paragraph is for. Revision 3.
3. `../PROVENANCE.md` — authoritative on what may be claimed about
   registration and ordering.
4. `context/citation_ledger.md` — the bibliography, with a status flag on
   every entry.

`main.tex` carries the structural comments inline. Its header block holds the
wording rules, the banned-numbers list, the page budget, and the cut order.
Read the header block before the first edit of a session.

## Response mode

Two modes. Infer which one from the request.

**Edit mode.** Anything of the form "change X," "tighten Y," "cut Z," "move
this paragraph." Make the edit and reply in one or two sentences saying what
changed. No preamble, no summary of the file, no restating the edit back. If
the edit forces a consequence somewhere else in the file, say so in one
clause. Speed matters more than completeness here.

**Reasoning mode.** Anything of the form "should we," "does this hold," "is
this the right way to set up," "what breaks if." These are research questions
about the framework, the mathematics, the claims, or the design. Answer them
at full length and at graduate research level. Find the gap before agreeing.
Do not make an edit to the file while in this mode unless asked. Ali holds all
verdicts on modeling, scope, and incentive-compatibility questions.

When a request is ambiguous between the two, ask which, in one line.

## Rules binding on every prose edit

- **Never write a number that is not traceable to
  `context/claims_to_evidence.md`.** If a number is needed and is not there,
  say so rather than producing one. An invented number is worse than a gap.
- **State the population on every count.** A count without its population is
  not a result.
- **Spans and universals, never singletons.** Report ranges across
  configurations. Never "model X does this and the others do not."
- **The universal usually hides behind the fraction.** "4 of 5" is often "all
  four with mass to test." Lead with the universal.
- **"Frozen," "pre-registered," and "pre-committed" never appear unqualified.**
  Ordering is not established for any artifact in this project. Decision rules
  were fixed at a checkpoint before their test ran, which is a claim about
  process, not about verified ordering. See `../PROVENANCE.md`.
- **Significance is reported at the cell, never at the draw.** Draw tallies are
  descriptive counts with attempted denominators and carry no p-value.
- **No em dashes anywhere in the paper body.**
- **Banned numbers.** The list is in `main.tex`'s header block. Grep it before
  any edit that adds a figure to the prose.

## Item 66

Claim sentences and related-work characterizations are Ali's to type. Strawman
text under item 66 is tagged `%% <ITEM66>` in `main.tex`. Do not silently
polish tagged text into something that reads final. If an edit lands on tagged
text, either keep the tag or say plainly that the tag should come off.

## Git

Commit before and after an editing session, and diff the result. The paper
directory sits inside the `Control-On-LLMs` repository and inherits its
history; there is no separate version control on the paper.
