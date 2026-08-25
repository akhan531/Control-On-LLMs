# Citation audit — `main.tex`

Read-only, per `number_audit_prompt.md` §4. Characterizations are **flagged for human
comparison, not verified** (source PDFs not held).

## 4.1 Mechanical

### Cite ↔ bibitem (both directions)

Ten `\bibitem`s; ten distinct cite keys. **Every key resolves to a bibitem, and every
bibitem is cited at least once.** No dangling cites, no uncited bibitems.

| key | cited at | bibitem |
|---|---|---|
| phillips1966 | §2 L305 (`\citet`) | L1435 |
| imran2025 | §4 L702 | L1419 |
| bayesbench2026 | §4 L706 | L1447 |
| edwards1968 | §4 L711 | L1405 |
| crownqa2026 | §5 L1063, §7 L1298 | L1427 |
| depunder2026 | §7 L1284 | L1397 |
| depunder2024 | §7 L1286 | L1390 |
| razniewski2024 | §7 L1289 | L1440 |
| absencebench2025 | §7 L1298 | L1413 |
| choi2025 | §7 L1307 | L1383 |

### `\ref` / `\label`

All `\ref`/`\eqref` targets resolve (no undefined references). Labels defined and **never
referenced**:

- `fig:schematic` (Figure 1) — label L328, **0 refs**. Figure 1 is never cross-referenced
  from the body. A pointer belongs in §1 P2/P3 or §2 (the setup paragraph already names the
  three FULL/ARITH_D0/PARTIAL_RULED arrows the figure draws).
- `fig:results` (Figure 2) — label L903, **0 refs**. Figure 2 is never cross-referenced from
  the body. Pointers belong in §4 (panel a, the 47–0 result) and §5 (panel b, the ladder).
- `lem:order` (Lemma 1, "Ordering") — label L433, **0 refs**. The lemma is stated and proved
  but never invoked; §2's ordering/"between"/"coordinate" language and §6's "credulous point"
  are where a `\ref{lem:order}` would go.
- `sec:instrument` (§3) — label L537, **0 refs** (minor; section labels are often unused).

### Bibliography digit-check vs `citation_ledger.md`

All ten entries match the ledger exactly (arXiv id / DOI / year / volume / pages). See
`number_audit.md` for the list. Note (not an error): the paper cites `edwards1968` (1968
original); the ledger records the 1982 reprint as an alternate and asks for one form used
consistently — the paper uses 1968 only, which is consistent.

---

## 4.2 Characterizations — HUMAN-CHECK (compare against `citation_ledger.md` §§1.4–1.6)

Risk flag: **HIGH RISK** = attributes a mechanism, cause, or quantitative finding; lower =
direction or topic only.

| key | `main.tex` characterization | ledger entry to compare | risk |
|---|---|---|---|
| **imran2025** | L702–705: "pre-trained-only checkpoints update less than Bayes requires, with the shortfall shrinking as models scale, measured over token log-probabilities; they describe the shortfall itself as unexplained…" | §1.5 [Imr25]: gradient <1 for every model, larger models closer to 1; pre-trained-only, five families, token log-probabilities; population caveat load-bearing. **Caution in ledger: do NOT cite the 30% figure** (not present in body — good). | **HIGH RISK** — quantitative direction + population + method |
| **bayesbench2026** | L706–710: "evaluate instruction-tuned models across turns and report both directions, with the tendency shifting across scale: smaller models stay near the middle… larger ones can push toward its extremes when the evidence is skewed." | §1.5 [Sam26]: both directions split by scale; smaller too close to middle, larger push to 0/1; 7 instruction-tuned models 3B–70B. **Ledger: never characterize as an over-confidence result** (body does not — good). MAE 8.3/36.7/34.2 not in body. | **HIGH RISK** — direction + scale mechanism |
| **crownqa2026** | L1063–1065: "the failure … report as over-closure: treating missing support as settled is the closed-world assumption applied where it does not hold, which in our coordinates is the credulous point." | §1.4 [CROWN-QA]: over-closure headline (OCR>UCR all three models); closed-world where it doesn't hold = our q_0 under δ>0. | **HIGH RISK** — attributes a named finding ("over-closure") |
| **depunder2026 + depunder2024** | L1283–1287: "trims the record where the correct update censors it … that a divergence restricted to a sub-event loses its non-negativity is established there and in [depunder2024]." | §1.1 [Pun25]/[Pun24]: trimming-vs-censoring; restricted KL can be negative / not a divergence. **Item 50 asks for a re-read of Pun25 for this vocabulary before the paragraph is finalized — confirm it happened.** | **HIGH RISK** — attributes a mathematical result to the works |
| **choi2025** | L1306–1307: "Belief dynamics in multi-agent settings already admit martingale and Lyapunov treatments." | §1.3 [Cho25]: debate belief is a martingale under Dirichlet-categorical, homogeneous full-information updating. "Lyapunov" is not attributed to Cho25 specifically in the ledger — check the plural doesn't over-claim. | MEDIUM — names a mechanism (martingale); "Lyapunov" attribution loose |
| **razniewski2024** | L1287–1289: "the gap between closed-world and open-world readings of a missing fact." | §1.6 [Raz24]: closed-world treats missing as false, open-world as unknown (survey). PARTIAL (secondary bib). | LOW — topic/vocabulary |
| **absencebench2025** | L1297–1298: "That language models mishandle absent evidence is known." | §1.6 [Fu25]: models can't detect what's missing (identify operation). PARTIAL (secondary bib). | LOW — direction/topic |
| **edwards1968** | L710–711: "Under-use relative to Bayes has been called conservatism since [edwards1968]." | §1.5 [Edw68]: construct name only. | LOW — construct name |

### Ledger-flagged provenance risks that touch these cites (not verifiable here)

- **crownqa2026, absencebench2025, razniewski2024** are `PARTIAL`/`PARTIAL (secondary bib)` in
  the ledger — bibliographic detail taken from other papers' reference lists. Ledger rule:
  enough to find, not enough to characterize. The characterizations above should be checked
  against the primary PDFs before submission.
- Ledger action list still open: read Zha25 (discounted Bayesian filters) before §2 asserts
  the operation set is novel; re-read Pun25 for the trimming/censoring vocabulary.
