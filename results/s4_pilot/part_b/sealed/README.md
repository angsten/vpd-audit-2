# Sealed: Do Not Open

This folder holds values sealed under the pilot's discipline (plan 6 of the research log, Section 3). **No one may open, load, print, or summarize them** until the part of the freeze file named below is signed. After that, the freeze file's own rules govern their use.

| File | What it holds | Governed by |
|---|---|---|
| `b1_raw.json` | B1: every per-text harm and $J$ of question 1's freed-label guard, versions (i) to (iii), all four arms, 8 seeds; the stochastic half's 8 draws | Freeze file, **Part 2** (question 1) |
| `v2_reference_check_freed_harm.json` | Version (ii)'s reference check: the nominal arm's harm on CQ text 0, seed 1, bf16, ours and the authors'. It was moved here from `../prerequisites.json` (plan 7 of the research log, item 1) | Freeze file, **Part 2** (question 1) |

**The only permitted readers before signature** are code that writes widths, variance components, prices, and yes/no answers (`vpd_audit_2/pilot_b_tables.py`), and code that reads the original-label arm alone, under a separate ruling recorded in the research log (`vpd_audit_2/pilot_b_original.py`, and the `check` stage of `modal_pilot.part_b`). No centre or sign of $\bar V - \Pi$, no $\bar V$ per arm, and no freed arm's harm may be reported.
