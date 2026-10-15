# Freeze File, Part 1: Question 2 and the Settings Both Questions Share

*Session 4. Written by Ines from Riku's skeleton, with the team's decisions and the PI's approvals of this session. Version 1. Part 2, question 1's lines, sample sizes, and versions, is frozen next session after the safeguard re-test the PI approved.*

## What You Are Signing

This file fixes, before any outcome exists, every rule by which question 2's results will be read: what counts as "carries over", how large the experiment is, which random seeds it uses, and how its error bars are computed. Question 2 is the post's lead result: whether the harm the paper's adversary finds on some texts also hurts texts it never saw, at search lengths from 20 to 320 steps.

After signature, any change is a dated amendment with its reason, committed before the run it affects, and the post reports it. Nothing here has seen a carry-over number: no adversary setting has yet been scored on any batch other than the one it was found on.

The essentials:

1. **The experiment.** The paper's evaluation adversary, run as our loop, which is bit-identical to the authors' own code. 16 attack batches and 16 held-out batches of 128 texts, each searched from 5 shared starting points, for 320 steps, read at 20, 40, 80, 160, and 320 steps. Cap \$105 (the PI's).
2. **Two pre-registered tables.** The step table, read at fixed search lengths, is the lead. The stage table reads each search where its own harm first reaches 2, 5, or 10 nats; it is printed in full and never resolves an undetermined step reading.
3. **Three questions at each length or level.** Is the carried-over harm larger than the paper's standard 20-step adversary does to its own batch? Does at least a fifth of the search's added harm carry over? Does that depend on which components the search chose, beyond how often they are used?
4. **Expected precision, stated in advance.** At 80 steps the design meets its precision target, just. At 40 steps no affordable design does, so a 40-step ratio reading of "undetermined" is expected, not a surprise.
5. **Two sealing slips, both in question 1's pilot, neither touching question 2.** They are recorded in Section 12.

The PI's signature is at the end of Section 0.

## 0. Identity and Sign-Off

| Entry | Value |
|---|---|
| Freeze file | Part 1, version 1 |
| Manifest | `vpd-audit-2/data/manifest/manifest.json`, SHA-256 `29d709c9…7d71`; master seed 20261001 |
| Starts | `vpd-audit-2/results/s4_pilot/starts/starts_1_64.npz`, SHA-256 `dcb53978dc20a18b9aa6e03480cb8590d7c90f15434d3cc485b9804ea81b9f9d`; allocation in `starts_1_64.json`, SHA-256 `c9c83d15…289a`. Starts 1 to 16 equal the manifest's original `starts.npz` entry for entry, by a committed test |
| Harness on `main` | `583c819`, the merge of `session-004-pilot`, which follows `983193f`, the merge of `session-004-loop`. Every deciding run records the commit it ran at, with a clean tree |
| Configuration | Our loop with `micro_batch=None` (the whole batch in one pass), bfloat16 autocast, one NVIDIA B200 per search, constant step 0.1, strict deterministic algorithms (no `warn_only`), TF32 off, `CUBLAS_WORKSPACE_CONFIG=:4096:8`. This path equals the authors' loop bit for bit on the real model (diagnostic D1), and reproduced session 3's eight runs bit for bit in the pilot. **No deciding measurement mixes configurations** |
| Software | torch 2.8.0+cu128, CUDA 12.8, `datasets` 4.4.2, as locked in `vpd-audit-2/uv.lock` |
| Labels, target, and weight deltas for question 2 | Computed once per batch, on the whole batch of 128, under bfloat16 autocast, as session 3's G1 and diagnostic D1 did. A held-out batch's own search and every carried-over setting scored on it use that same tensor |
| Labels for any run touching question 1's texts | From the committed float32 label cache, never recomputed from a different batch grouping (pilot report 3: regrouping moves 0.23 percent of label entries by up to $1.2 \times 10^{-4}$) |
| Date of commit | The session 4 finalize commit, which carries this file |
| PI's signature | Signed by the PI in the session 4 transcript on 5 October 2026 ("All looks good - please proceed", in answer to the request for signature) |

## 1. What Passed Before the Freeze

These are outcomes the rules depend on, not lines.

| Check | Outcome |
|---|---|
| G1, step size (session 3) | Constant step 0.1 at every budget |
| G2, our loop | Bit-identical to the authors' loop on all 128 texts of a calibration batch, in float32 and, by D1, in bfloat16 over 320 steps |
| G3, precision | All-on passes in float32 (floor $3.6 \times 10^{-8}$ against $4.54 \times 10^{-6}$); the at-labels and stochastic settings pass in float64. Question 2 runs in bfloat16 as the authors' evaluation did and is unaffected |
| G5, data (session 3) | Attack and held-out sides share no document |
| Long-search diagnostics | A single long search is a wide draw: one smallest-unit change in one starting value moves one batch's plateau from 28 to 50 nats. "About 22 nats, not the paper's 40" is withdrawn |
| Pilot, question 2's part | 80 own-batch searches on calibration batches; the diagonal reproduced session 3's runs bit for bit; every nudged replicate departed at step 1; no forbidden pool or start touched; strict determinism with no warning; shuffled harms sealed |

## 2. Pools, Texts, and Starts

| Pool | Use under this file |
|---|---|
| A1 to A16 | Attack batches, 128 texts each |
| H1 to H16 | Held-out batches, 128 texts each, sharing no document with any attack batch |
| C1 to C8, CQ | Gates and pilot only; never used for a deciding reading |
| Q | The rerun of the first post's comparison (Section 7), after Part 2 is committed |
| Q1 | Question 1's deciding sets: untouched under this file |

**Starts.** 1 to 8: gates and pilot. **9 to 13: question 2's deciding runs** ($n_s = 5$), each shared by every attack and held-out batch under that seed. 14 to 24: reserved for question 2 by amendment only. 25 to 40: question 1. 41 to 45: the rerun of the first post's comparison. 46 to 64: reserve, by recorded amendment only.

**The run with delta components held fixed** uses A1 to A8 against H1 to H8, with starts 9 to 13, so each of its cells has an exact counterpart in the lead.

## 3. Definitions

| Term | Definition |
|---|---|
| Harm | Per-token KL divergence from the original model's next-token distribution, averaged over 512 positions |
| Search | One adversary run: one batch from one start, 320 steps |
| Source after $n$ steps | The setting after the $n$-th update. Step $n$ decides; step $n-1$ is scored beside it at 160 and 320 |
| Two-step mean | $m_k = \tfrac12(\mathrm{KL}(k) + \mathrm{KL}(k-1))$, own-batch harm |
| Stage-$h$ source | The source after the first step $k \ge 1$ with $m_k \ge h$, for $h \in \{2, 5, 10\}$ nats; the same rule on attack and held-out batches |
| Carried-over cell | $X_{ijs} = \mathrm{KL}_{H_j}(r^{A_i,s,n}) - \mathrm{KL}_{H_j}(r^{\mathrm{init}}_s)$ |
| Denominator cell | $Y_{js} = \mathrm{KL}_{H_j}(r^{H_j,s,n}) - \mathrm{KL}_{H_j}(r^{\mathrm{init}}_s)$, the held-out batch's own search |
| Carry-over ratio | A ratio of means, pooled over all cells: $\tau_n = \bar X / \bar Y$, with $\bar X = \frac{1}{K^2 n_s}\sum_{i,j,s} X_{ijs}$ over the $K^2 n_s$ carried-over cells and $\bar Y = \frac{1}{K n_s}\sum_{j,s} Y_{js}$ over the $K n_s$ denominator cells |
| Shuffled ratio | $\tau^{\mathrm{shuf}}_n$, the same ratio of means with the mean harm of 8 stratified shuffles of $r^{A_i,s,n}$ in place of the starting harm in both numerator and denominator |
| Shuffle strata | Within each matrix, alive components in ten equal-count deciles of how often their label is above zero on Q; dead components (mean label at most $10^{-6}$) a stratum of their own. The 24 delta entries stay in place |
| Plateau (description) | Mean harm over steps 301 to 320 |
| Cycling source (description) | Own-batch harm at steps $n$ and $n - 1$ differs by more than 10 percent of the larger *(convention)* |

## 4. The Lines

Each line quotes the plan's Section 9 [plan], then states it as frozen. *(Convention)* marks a line chosen because some line had to be.

**Carries over, at 20 steps.** Plan: "Interval of the pooled $\tau_{20}$ at or above 0.2." As frozen: unchanged, with Section 5's interval. Verdicts: Carries over (interval at or above 0.2), Batch-specific (below), Undetermined (straddling). *(0.2 is a convention.)*

**Shuffled ratio.** Plan: "The same 0.2 line, plus zero; shuffles stratified by needed-frequency decile, with dead components as their own stratum." As frozen: unchanged; 8 shuffles; read at every budget and stage:

| Interval of $\tau^{\mathrm{shuf}}_n$ | Reading (plan Section 6.5, verbatim) |
|---|---|
| At or above 0.2 | The carried-over harm depends on which components the adversary chose, beyond how often they are needed |
| Above zero, below 0.2 | Mostly harm from extreme masks on components of that usage, whichever ones receive them, with a small part that depends on the choice; the exploited-components count is reported with that caveat |
| Includes zero | The harm comes from extreme masks on components of that usage, whichever ones receive them; the exploited-components count is dropped from the post |
| Straddles 0.2 | Undetermined between the first two readings; this takes precedence when a wide interval also includes zero |

**Large.** Plan: "Interval of the carried-over harm minus the held-out batch's own 20-step harm above zero; not asked at 20 steps." As frozen: unchanged; read first at 40 and 80 steps.

**The step table, the lead.** Plan: "The table of Section 6.6 at every budget from 40 steps; 'does not carry over' when the interval of $\tau_n$ lies below 0.2." As frozen: unchanged. At each budget:

| At budget $n$ (plan Section 6.6, verbatim) | Depends on the choice | Does not depend on the choice |
|---|---|---|
| **Large** | The search found a choice of components whose harm carries to text in general: by the paper's own test (lines 2019 to 2022), a systematic defect | A random permitted setting that switches off and on as many components at each level of usage also hurts unseen text; the search's particular choice is fitted to its batch |
| **Not large, but carries over** | The choice carries over, at no more harm on unseen text than the 20-step adversary does to its own batch | The harm carries over through extreme masks on components of that usage, within the 20-step level |
| **Does not carry over** | The search's harm is fitted to its batch: the case line 2022 describes as noise-tuned (either column) | |

When an interval straddles its line, the reading names only the part of the table it settles, and the rest is undetermined at that budget. The carry-over ratio $\tau_n$, the raw nats, and the shuffled harm are always reported beside the reading. A straddling 40- or 80-step cell stays Undetermined, and nothing outside the step table resolves it.

**The stage table** *(levels and missing allowance are conventions)*.
- Levels 2, 5, and 10 nats. At each level, the same three questions: Large, with the held-out batch's own 20-step harm as yardstick; Carries over, $\tau_h \ge 0.2$, with the held-out batch's own stage-$h$ search as denominator; Depends on the choice, $\tau^{\mathrm{shuf}}_h \ge 0.2$.
- Only positive verdicts are confirmatory. Negative ones are reported with the bias of taking a setting at its first crossing stated: downward, of unknown size. The rule relies only on its direction. For scale, the pilot's overshoot above the level at the first crossing had a median of about 9 percent and a maximum of 44 percent at 10 nats.
- Worded by own-batch harm, never by step count; printed in full; never resolves a step-table cell.
- A search that never reaches $h$ by step 320 is missing at $h$. A level is Undetermined if more than one eighth of attack searches, or of held-out searches, are missing at it: more than 10 of 80 per side. **Expected from the pilot: 10 nats is likely Undetermined** (9 of 64 pilot searches missed it); 2 nats complete; 5 nats about 5 percent missing.

**Composition.** Plan: token-level split, "more than half of the carried-over added harm, each part read separately"; exploited components, "90 percent of added harm, on the held-out batch"; pin test trigger, "top 3,000 keep at least 90 percent; a random 3,000 keep under half". As frozen: unchanged. *(Conventions.)*

## 5. The Interval

Plan: "two-way over batches for question 2". As frozen, 95 percent, $B = 10{,}000$, every replicate's seed saved, applied identically to $\tau_n$, $\tau^{\mathrm{shuf}}_n$, the "large" difference, and every stage reading:

1. **Batch part.** Seeds averaged within each cell; the pigeonhole bootstrap over attack and held-out batches resampled independently; $V_{\mathrm{PB}} = \frac{K}{K-1}\,\mathrm{SE}^{*2}$.
2. **Start part.** From the three-way analysis of variance of the linearized cells, one per (attack batch, held-out batch, start). For the ratios $\tau_n$, $\tau^{\mathrm{shuf}}_n$, and every stage ratio, the cell is scaled into the ratio's units, $W_{ijs} = (X_{ijs} - \hat\tau\, Y_{js})/\bar Y$; for the "large" difference it is the plain difference, unscaled. Then:
$$
\hat\sigma^2_c = \max\!\left(0,\ \frac{\mathrm{MS}_S - \mathrm{MS}_{AS} - \mathrm{MS}_{BS} + \mathrm{MS}_{ABS}}{K^2}\right), \qquad V_c = \frac{\hat\sigma^2_c}{n_s}.
$$
3. **Degrees of freedom.** $\nu_c$ by Welch–Satterthwaite on the mean squares, bounded to $[1, n_s - 1]$; $\nu = (V_{\mathrm{PB}} + V_c)^2 / \left(V_{\mathrm{PB}}^2/(K-1) + V_c^2/\nu_c\right)$.
4. **Interval.** $\hat\tau \pm t_{0.975,\nu}\sqrt{V_{\mathrm{PB}} + V_c}$.
5. **Reported beside it:** the untruncated $\hat\sigma^2_c$, the full mean-square table, the share $V_c/(V_{\mathrm{PB}} + V_c)$, each seed's pooled value, and the percentile interval.

The deciding runs store every cell per seed, never only averages.

## 6. The Design

**The rule, fixed before the pilot.** From the pilot's two-way analysis of variance of own-batch added harm at each budget $n$, with mean $\hat\mu$ and components truncated at zero (batch $\hat\sigma^2_b$, start $\hat\sigma^2_c$, pairing $\hat\sigma^2_{\mathrm{int}}$), the projected relative half-width is

$$
w_n(K, n_s) = t_{0.975,\,\nu}\ \frac{1}{\hat\mu}\sqrt{\frac{2\hat\sigma^2_b}{K} + \frac{2\hat\sigma^2_{\mathrm{int}}}{K n_s} + \frac{\hat\sigma^2_c}{n_s}}, \qquad \nu = \frac{(P + S)^2}{P^2/(K-1) + S^2/(n_s - 1)},
$$

where $P$ is the sum of the first two terms under the root and $S$ the third. Among $K \in \{8, 16\}$ batches per side and $n_s \in \{3, 5, 8\}$ starts, choose the cheapest design with $w_{40} \le 0.25$ and $w_{80} \le 0.25$, and with $n_s \ge 5$ whenever $\hat\sigma^2_c > 0.1 \times 2\hat\sigma^2_{\mathrm{int}}/K$ at any budget, using each candidate's own $K$. If none qualifies under the PI's cap, take the smallest $w_{80}$ under the cap, where "under the cap" means the upper end of the design's total cost estimate. *(0.25 and one-tenth are conventions.)*

**Applied, from the pilot:**

| Batches per side, starts | $w_{40}$ | $w_{80}$ | $w_{320}$ | Cost, with the delta-frozen run |
|---|---|---|---|---|
| 8, 8 | 0.51 | 0.31 | 0.23 | \$75 to \$89 |
| **16, 5** | **0.36** | **0.247, just under 0.25** | **0.17** | **\$86 to \$103** |
| 16, 8 | 0.33 | 0.20 | 0.15 | \$138 to \$165 |

No design meets the 40-step target: the batch-to-batch term alone gives about 0.29 even at 16 batches, the most the manifest holds. The start floor excludes 3 starts. Under the PI's \$105 cap the fallback chooses **16 batches per side with 5 starts**, which the team recommended unanimously.

**Frozen:** attack batches A1 to A16, held-out batches H1 to H16, starts 9 to 13, 8 shuffles per scored source; the run with delta components held at 1 at 8 by 8 (A1 to A8, H1 to H8) with the same starts.

## 7. The Rerun of the First Post's Comparison

Frozen here; it runs after Part 2 is committed, since it touches question 1's texts.

| Entry | As frozen |
|---|---|
| Arms | Delta components optimized, as the paper does; delta components held at 0, as the first post's aggregations did |
| Configuration | Section 0's, 20 steps |
| Texts | Q as eight consecutive batches of 128; scored only on the batch searched |
| Starts | 41 to 45 |
| The number beside 0.80 | The mean $A$ over cells. Its variance comes from the two-way analysis of variance's batch, start, and residual components, each truncated at zero. Untruncated it is $(\mathrm{MS}_B + \mathrm{MS}_S - \mathrm{MS}_E)/(K n_s)$; after truncation $\widehat V$ is built from the mean squares that survive, with Welch–Satterthwaite degrees of freedom on those mean squares |
| The clause | "About as much" if $0.80/A$ lies within a factor of 1.25 of 1, otherwise "less" or "more" *(convention)* |
| The delta share | $(A - A_\Delta)/A$, with the paired difference's interval |

## 8. Description Fixed in Advance

Not lines; reported whatever they show.

- Beside every step reading, the share of attack and held-out searches past 2, 5, and 10 nats.
- For every scored source: retention (carried-over over own-batch added harm), and a scatter of carried-over against own-batch harm, marked by budget and stage. Only if the 80-step sources lie on the stage curve may the post call an undetermined 80-step cell a matter of timing.
- The step-$(n-1)$ readings at 160 and 320, and the share of cycling sources per budget.
- Long-search levels as a distribution under Section 0's configuration, with the one-unit spread of a single search and the paper's 40.2 placed against it.
- Every result also recomputed without the 11 held-out texts that share a 50-token span with an attack text.
- Everything not listed as a line is exploratory.

## 9. Nuisance Scales Recorded

From the pilot (own-batch added harm, 8 calibration batches by 8 starts; components truncated at zero):

| Budget | Mean | Batch | Start | Pairing | Path noise, share of pairing |
|---|---|---|---|---|---|
| 20 | 0.593 | 0.050 | 0.0001 | 0.072 | 0.01% |
| 40 | 1.949 | 0.581 | 0.082 | 0.819 | 1.8% |
| 80 | 9.764 | 0 | 0 | 51.15 | 2.5% |
| 160 | 22.10 | 7.44 | 0 | 107.5 | 27% |
| 320 | 25.45 | 8.97 | 0 | 124.2 | 46% |

Stage crossings, median steps: 44 at 2 nats, 70 at 5 (3 missing of 64), 83 at 10 (9 missing). Stage 2's denominator: mean 1.91 nats, standard deviation 0.095. Shuffle noise ratio at most 0.0013. Timing on a B200: 0.38 to 0.40 seconds per search step, 0.18 seconds per scoring pass.

## 10. Requirements for the Lead's Engineering Plan

1. **Resumability.** Every search writes its record, with its saved sources' hashes, the moment it finishes; a restart skips finished searches and cells. A test kills a job mid-run and checks that the restart's outputs equal an uninterrupted run's bit for bit.
2. **One configuration.** If a B200 is unavailable, the run waits; it never falls back to another GPU type or to chunking.
3. **Spend against the cap.** The lead's searches and scoring run before the delta-frozen run. Spend is checked between stages; if projected spend would exceed \$105, work stops and goes to the PI. Nothing is trimmed silently.
4. **Sealing until the analysis.** No carry-over number is printed before the analysis script, committed in advance, runs on the complete table.
5. **Provenance.** Every result records its commit (clean tree), GPU, environment, and seed keys.

## 11. Conventions, in One Place

The 0.2 line for both ratios; the "large" yardstick of the held-out batch's own 20-step harm; the stage levels 2, 5, and 10 nats and the one-eighth missing allowance; the 10 percent cycling threshold; the composition lines (half; 90 percent; 3,000); the design target 0.25 and the start floor's one-tenth; 8 shuffles and the 0.1 noise-ratio rule that set it; the start blocks; the rerun's 1.25 band.

## 12. Amendments Made Before This Freeze

All registered in the session 4 checkpoint, Appendix F, and the session 3 checkpoint, Appendix E. Those made after a result are: price check 7's narrowing (question 1 only); G3's remedy; diagnostic D4's void-case reading; the withdrawal of "about 22 nats"; and the design chosen by the fallback after the pilot.

Two sealing slips, both in question 1's pilot and neither touching question 2:
- **An unrecorded comparison.** The engineer computed a comparison that could hint at the sealed sign, recognized it, and did not record it.
- **One freed-arm harm outside the seal.** One freed-arm harm, for one calibration text and one seed on a random nominal set, was written to an unsealed results file. It was also quoted in the engineering report on the pilot's second part, beside the original arm's value. It is in the pushed history of the pilot branch, and it is sealed going forward.

Neither is a deciding measurement.

## 13. What Part 2 Will Freeze

Question 1's lines (Minimal, Padded, At the price, Adversarially needed), the versions kept in the Padded condition after the safeguard re-test on pruned sets from calibration texts, question 1's seeds and routing draws, the GPU type for its freed-label runs, the first stage's reference sizes, and question 1's interval rule. Until Part 2 is committed, question 1's deciding sets stay untouched.
