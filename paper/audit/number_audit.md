# Number audit — `main.tex`

Read-only audit per `number_audit_prompt.md`. Authorities: `context/claims_to_evidence.md`
(ledger), draw records, analysis scripts. Recomputed from data where possible (PASS-DATA);
otherwise matched to the ledger with a stated reason (PASS-LEDGER).

Verdict key: PASS-DATA · PASS-LEDGER · MISMATCH · UNTRACED · AMBIGUOUS · BANNED.
"L###" = line in `main.tex`. Numbers appearing **only in `%%` comments** are marked
`(comment)` and are not live copy.

## Verdict counts

| verdict | count |
|---|---|
| PASS-DATA | 41 |
| PASS-LEDGER | 38 |
| MISMATCH | 1 |
| AMBIGUOUS | 4 |
| BANNED (live) | 1 (contextualized; ledger-sanctioned) |
| UNTRACED | 0 |

---

## §1 Introduction (L202–256)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L242 | "Among the five configurations admitted by the competence gate" | 5 | gate recompute | 5 admitted | PASS-DATA | gate admits sol-high/sol-none/glm-high/deepseek-high/glm |
| L243 | "the two conditions that do not enumerate the absences" | 2 | ledger NE | FULL+PARTIAL_RULED | PASS-LEDGER | design (NE arms) |
| L240 | "three reference beliefs" | 3 | §2 eqs | b_pos,q_δ,q_0 | PASS-DATA | eqs (1)–(3) |
| L241 | "makes three conditions share one target" | 3 | Prop 1 | full/arith_d0/partial_ruled | PASS-DATA | pivot |

## Figure 1 (L279–331, tikz)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L282 | band 0 rectangle | 0.00–0.20 | BANDS/ledger 1.4 | 0.20 edge measured | PASS-LEDGER | measured high/low edges 0.20/0.80 |
| L282 | band 1 rectangle | 0.40–0.45 | BANDS | band 1 | PASS-LEDGER | narrowest band (ledger 5.8) |
| L282 | band 2 rectangle | 0.55–0.70 | BANDS | band 2 | PASS-LEDGER | model BANDS |
| L282 | band 3 rectangle | 0.80–1.00 | BANDS/ledger 1.4 | 0.80 edge measured | PASS-LEDGER | |
| L316 | `$\pi=0.500$` | 0.500 | uniform prior | 0.5 | PASS-DATA | uniform over 2 candidates |
| L311 | `$\bstar=\qz=0.190$` (A1) | 0.190 | recompute A1 | 0.19000 | PASS-DATA | p=0.81,N=5,k=2: q0(SIGMA)=0.190 |
| L313 | `$\bpos=0.948$` (A1) | 0.948 | recompute A1 | 0.94785 | PASS-DATA | b_pos(SIGMA)=0.81²/(0.81²+0.19²) |
| L302,307 | markers at level 0 / level 3 | 0,3 | ledger 1.3 | level(b*)=0, level(b_pos)=3 | PASS-DATA | A1 cell |
| axis | ticks 0,0.2,…,1.0 | — | axis labels | — | PASS-DATA | schematic axis |

## §2 The framework + Table 1 (L293–535)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L293 | `$\|A\|=2$`, `$p>1/2$` | symbolic | design | — | PASS-LEDGER | load-bearing assumption |
| L467 | "the $\delta = 0.3$ conditions" | 0.3 | design | δ=0.3 arm | PASS-LEDGER | banked/dropout rate |
| Table1 | operation sets {a},{c,a},{i,c,a} | — | ledger 1.5 | nested | PASS-DATA | matches §5 nesting |
| L437–L441 | six conditions / targets b_pos,b*,q_δ | — | Table 1 | — | PASS-LEDGER | design map |

## §3 The instrument (L558–672)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L561 | "$32$ stimuli at three draws … all seven" | 32/3/7 | ledger 1.4 (W1) | 32×3×7 | PASS-LEDGER | W1 pre-test; separate stimulus set |
| L562 | "$659$ of $672$ usable" | 659/672 | ledger 1.4 | 659/672 | PASS-LEDGER | W1; outside the 7,051 total |
| L563 | "switch edges at $0.20$ and $0.80$" | 0.20/0.80 | ledger 1.4 | measured edges | PASS-LEDGER | measured both sides |
| L563 | "low-high asymmetry of $0.000$ … six of the seven" | 0.000 / 6 of 7 | ledger 1.4 | 0.000, 6/7 | PASS-LEDGER | anchor is the exception |
| L565 | "single exception is anchor, at $0.1$" | 0.1 | ledger 1.4 | anchor 0.1 | PASS-LEDGER | |
| L566 | "resolution of $0.10$" | 0.10 | ledger 1.4 | CAL 0.10 | PASS-LEDGER | sampling-resolution fact |
| L583 | "fourteen for fourteen at $\delta=0$ and nine for nine at $\delta=0.3$" | 14/14, 9/9 | ledger 1.3 | 14/14, 9/9 | PASS-LEDGER | build-time, silence_v2_model |
| L601 | "Five of the fourteen cells fail" | 5/14 | ledger 1.7 | 5/14 | PASS-LEDGER | banked_viable |
| L602 | "dropout target at $0.366$ and $0.392$" | 0.366/0.392 | ledger 1.7 | in 0.20–0.40 gap | PASS-LEDGER | B2,B3 |
| L603 | "between $0.512$ and $0.524$" | 0.512/0.524 | ledger 1.7 | in 0.45–0.55 gap | PASS-LEDGER | D1–D3 |
| L604 | "reduces fourteen cells to the nine" | 14→9 | ledger | 14→9 | PASS-DATA | 14−5=9 |
| L632 | "Five of seven configurations are admitted" | 5/7 | gate recompute | 5 of 7 | PASS-DATA | |
| L633 | mean s1 "$0.200$,$0.421$,$0.457$,$0.752$,$0.764$" | 5 values | **recomputed FULL s1, 14 cells, no P4** | 0.200/0.421/0.457/0.752/0.764 | PASS-DATA | exact match |
| L634 | excluded "$1.609$ (deepseek) and $1.800$ (anchor)" | 1.609/1.800 | recompute | 1.609/1.800 | PASS-DATA | exact |
| L635 | "gap between $0.764$ and $1.609$" | gap | recompute | 0.764→1.609 | PASS-DATA | bar-insensitive |
| L646 | "excludes at $1.800$ … four instrument checks and one behavioural gate" | 1.800; 4+1 | ledger 1.4/rev4 | anchor exception ×4 | PASS-LEDGER | consistency asset |
| L661 | "$7{,}051$ usable draws of $7{,}210$ attempted, at five draws" | 7051/7210 | ledger §7 + arithmetic | 2894+620+623+959+1955=7051; 2940+…=7210 | PASS-LEDGER | totals only in body; per-arm in comments; identities hold |
| L663 | "$659$ of $672$ … three draws" | 659/672 | ledger 1.4 | 659/672 | PASS-LEDGER | pre-test carved out |

## §4 Example 1 (L700–870)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L737 | "bottom level in eleven of the fourteen" | 11/14 | stimuli l_cor | l_cor=0 in 11 cells | PASS-DATA | A(5)+C(3)+B(3) |
| L738 | "outside the three cells where the target sits one level up" | 3 | stimuli | D1–D3 l_cor=1 | PASS-DATA | 11+3=14 |
| L772 | "runs $47$ to $0$ toward under-weighting" | 47–0 | v2_dcell_split | 47 displaced,0 over | PASS-DATA | |
| L773 | "$150$ attempted … $150$ were usable" | 150/150 | records | 150/150,0 fail | PASS-DATA | 5 gated ×30 |
| L777 | "eight of the fifteen … units … displaced" | 8/15 | recompute net-sign | 8 disp,0 over | PASS-DATA | sign-test grain |
| L779 | "$p = 0.008$" | 0.008 | 2·0.5⁸ | 0.0078→0.008 | PASS-DATA | cell-level |
| L779 | "the remaining seven carry no displaced mass" | 7 | recompute | 15−8=7 | PASS-DATA | |
| L781 | "runs $9$ to $0$ on the same $150$" | 9–0/150 | v2_dcell_split | FULL 9 disp | PASS-DATA | control arm |
| L782 | "five of fifteen units displaced, $p = 0.063$" | 5/15, 0.063 | recompute; 2·0.5⁵ | 5 disp; 0.0625→0.063 | PASS-DATA | cell-level |
| L823 | "$8$ of $91$ … $50$ of $80$ … $140$ of $140$ with $108$ … $17$ of $52$" | 8/91,50/80,140/140(108),17/52 | **s5_prior_crossing.py** | exact | PASS-DATA | pop. not stated in body → see AMBIGUOUS |
| L823–L825 | "The fifth admitted configuration produces no error draws at all" | 0 error draws | s5_prior_crossing | **sol-high n_err=16** (0 above-prior) | **MISMATCH** | 16 error draws exist, all below-prior; script excludes for 0 *above-prior* mass. Matches ledger 2.5 wording, not data. Correct: "no above-prior error draws." |
| L827 | "uniform prior at $0.5$ falls inside the band gap" | 0.5 | ledger 2.6 | 0.45–0.55 gap | PASS-LEDGER | straddles prior |
| L829 | "falls in none of the five and rises in four" | 0/5, 4 | ledger 2.7 | occupancy pattern | PASS-LEDGER | arms not named → AMBIGUOUS |
| L830 | "on a four-level scale the two middle levels" | 4/2 | design | levels | PASS-DATA | |
| L832 | "Of the $47$ displaced draws, $44$ … $3$ … none" | 47=44+3+0 | v2_dcell_split | 44 L2,3 L3,0 L0 | PASS-DATA | |
| L835 | "$3$ in $150$ attempted draws" | 3/150 | recompute | endpoint mass 3 | PASS-DATA | |

## Figure 2 (panels, L888–893)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| 2(a) | per-config-arm counts, s2∈{−1,0,+1,+2} | — | make_fig2 asserts | matches 47/9, 44/3/0 | PASS-DATA | s2=−1 zero-width all bars |
| 2(a) | "30 per configuration-arm" | 30 | records | 150/5 | PASS-DATA | |
| 2(b) mass | four segments sum 100%/config-rung | — | make_fig2 asserts | sums hold; BEY=0 sol-none/sol-high | PASS-DATA | |
| 2(b) mass | at-b_pos 4.6→0.0, 30.6→12.9, 77.1→50.0 | — | asserts | match | PASS-DATA | |
| 2(b) mass | interior 65.4→66.9, 28.4→42.4, 17.1→27.9 | — | asserts | match | PASS-DATA | |
| 2(b) s1 | mean s1 per config-rung | — | ladder | match ledger 4.1 | PASS-DATA | |

## §5 Example 2 (L917–1069)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L938 | "$980$ calls, $959$ usable" | 980/959 | records | 980 attempted,959 ok | PASS-DATA | ARITH_D0 campaign |
| L956 | "from $4.6$ to $0.0$ … $30.6$ … $12.9$ … $77.1$ … $50.0$ percent" | occupancy | make_fig2 asserts | match | PASS-DATA | cells/usable not stated → AMBIGUOUS |
| L959 | "from $65.4$ to $66.9$, $28.4$ to $42.4$, $17.1$ to $27.9$" | interior | asserts | match | PASS-DATA | |
| L962 | "from $6.4$ to $10.7$" (ceiling config) | 6.4→10.7 | asserts | glm-high | PASS-DATA | |
| L981 | "All five admitted configurations … three numeric positions and two … at ceiling" | 5, 3+2 | ledger 4.7 | 5=3+2 | PASS-LEDGER | |
| L985 | "closures span $28$ to $114$ percent" | 28–114 | ladder λ | sol-none λ0.72→28%; deepseek-high λ−0.14→114% | PASS-DATA | 1−λ |
| L1002 | "no configuration recovers more than $12.5$ percent" | 12.5 | ledger 4.6 | s3_arith_summary | PASS-LEDGER | not recomputed |
| L1003 | "admitted five recover at most $8.0$ percent" | 8.0 | ledger 4.6 | same | PASS-LEDGER | |
| L1004 | "no more than $0.20$ bins" | 0.20 | ledger 4.6 | worst-case missingness | PASS-LEDGER | |
| L1004 | "contains all seven configurations" | 7 | ledger 4.6 | A7 | PASS-LEDGER | |
| L1028 | "concordance fails for three configurations" | 3 | ledger 5.16 | sol-none,glm,deepseek | PASS-LEDGER | |
| L1029 | "the wrong way … by $0.043$ and $0.114$ bins" | 0.043/0.114 | ladder paired Δs1 | sol-high +0.043, glm-high +0.114 | PASS-DATA | ceiling configs |
| L1031 | "a gain of $0.493$ bins" | 0.493 | ladder | glm |Δs1|=0.493 | PASS-DATA | |
| L1032 | "ranging from $-0.89$ to $+0.17$" | −0.89/+0.17 | ledger 4.8 | per-line effect | PASS-LEDGER | V-E2-3 |
| L1033 | "bounding the … correlation at $0.34$" | 0.34 | ledger 4.8 | max \|r\| | PASS-LEDGER | collinearity audit |
| L1047 | "two over-reads in $150$ … against none in $300$" | 2/150, 0/300 | D-cell OVER probe | deepseek-high 1/30, glm 1/30 ARITH; 0/300 NE | PASS-DATA | make_fig2 diagnostic |

## §6 What the instrument cannot identify + Table 2 (L1098–1262)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L1098 | "at least two of three families" | 2/3 | ledger 5.2 | design | PASS-LEDGER | outcome bands |
| T2 L1129 | "gap $>0.5$ in $\ge 2$ of $3$" | 0.5, 2/3 | ledger 5.1 | design | PASS-LEDGER | P3 |
| T2 L1132 | "$0$ of $3$ … $1$ of $3$ … clears it at $0.821$" | 0/3,1/3,0.821 | v2_gates.json 5.1 | glm 0.821 | PASS-LEDGER | strict/loose readings |
| T2 L1136 | "$1$ of $3$ each, in different families" | 1/3 | ledger 5.3 | P1 glm,P2 sol-high | PASS-LEDGER | body omits which (fine) |
| T2 L1140 | "Specification text says $8$ of $11$; executed as $6$ of $8$ … $0.727 \to 0.75$" | 8/11,6/8,0.727,0.75 | ledger Table-2 | 8/11=0.727,6/8=0.75 | BANNED(live)/PASS-LEDGER | "8 of 11" is on banned list but here it is the **explicitly-corrected miscount**, sanctioned by ledger "Table 2 as it should read". Arithmetic holds. |
| T2 L1148 | "Sharp $0.15$-bin threshold" | 0.15 | ledger | ceiling guard | PASS-LEDGER | |
| L1183 | "raising the number of absences from four to twelve forces … from $0.90$ to $0.56$" | 4→12, 0.90→0.56 | ledger 5.6 | s3_dial closed-form | PASS-LEDGER | analytic |
| L1184 | "falls from $5.61$ through $1.83$ to $0.71$ nats … eightfold" | 5.61/1.83/0.71 | ledger 5.6 | dial | PASS-LEDGER | 5.61/0.71≈7.9× |
| L1188 | "around fifty times weaker" | ~50 | ledger 5.7 (3.84 vs 0.065/0.080/0.064) | **ratio span 48.0–60.0** | PASS-LEDGER | see §3.2: true span 48–60, mid ≈54; "~fifty" understates top slightly |
| L1193 | "gap of $0.20$ below it and $0.10$ above" | 0.20/0.10 | BANDS | 0.20–0.40 / 0.45–0.55 | PASS-DATA | band-gap widths |
| L1194 | "roughly twice the excursion" | 2× | derive | 0.20/0.10=2 | PASS-DATA | |
| L1240 | "at least $0.5$ … only two of the four bins" | 0.5, 2/4 | ledger 5.10 | \|A\|=2 ⇒ b_pos≥0.5 | PASS-LEDGER | analytic |
| L1261 | "$6.3$ and $14.6$ percent … across all seven" | 6.3/14.6 | ledger 5.12 (39/620, 91/623) | 39/620=6.3%,91/623=14.6% | PASS-LEDGER | arms not attributed, raw counts absent → AMBIGUOUS |

## §7 Related work & limitations, Reproduction (L1283–1342)

| loc | fragment | value | source | found | verdict | note |
|---|---|---|---|---|---|---|
| L1321 | "roster is seven open-weight configurations" | 7 | roster | 7 configs | PASS-DATA | |
| L1323 | "candidate set is fixed at two" | 2 | design | \|A\|=2 | PASS-LEDGER | points to §6 |
| L1341 | "available at commit $9ade4d4$" | 9ade4d4 | git | exists on main, 221 files, **NOT pushed** | see §6 report | commit reachable locally only |

## Bibliography (L1383–1454) — digit-check vs `citation_ledger.md`

All ten entries match the ledger digit-for-digit (arXiv id, DOI, year, volume, pages). PASS-LEDGER:
choi2025 arXiv:2508.17536; depunder2024 arXiv:2408.02391; depunder2026 DOI 10.1080/01621459.2025.2576189;
edwards1968 Kleinmuntz/Wiley 1968; absencebench2025 arXiv:2506.11440; imran2025 arXiv:2507.17951;
crownqa2026 arXiv:2608.04591; phillips1966 JEP 72(3):346–354, 1966; razniewski2024 ACM CSUR 56(6):1–42, 2024;
bayesbench2026 arXiv:2606.30850.

---

## Note on numbers living only in comments (not live copy)

The per-arm campaign breakdown (2,894 / 620 / 623 / 959 / 1,955 and 2,940 / 630 / 630 / 980 / 2,030),
84 = 14×3×2, the MAE figures 8.3/36.7/34.2, eps 3.84 and 0.065/0.080/0.064, spans 3,3,3,2,2,
per-config level splits (glm-high 5 vs 1 etc.), 3/3/3 and 0/1/1, and every banned figure appear
**only in `%%` comments**. They are correct where checkable but are not printed in the paper.
