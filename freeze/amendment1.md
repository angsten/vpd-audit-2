# Freeze File, Part 1: Amendment 1

*Session 5. Written by Ines from Ruth's draft and audit, Daniel's interval specification, Riku's output and reading specification, and Lena's table and run specification. Everything in this file was fixed before the made-up-data test ran and before any deciding run. The interval multipliers that Section 5 provides for are recorded in a separate dated file, after that test and before any deciding run.*

## What This Amendment Does

Part 1 of the freeze file fixes every rule by which question 2's results are read: whether the harm the paper's adversary finds on some texts carries over to texts it never saw. Part 1 says that any change after signature is "a dated amendment with its reason, committed before the run it affects", and that the post reports it. This is that amendment.

Before the run, four researchers reviewed the signed rules independently, each from a different side. The reviews found two kinds of thing:

- **Gaps:** places where the signed rules are silent but the analysis script must compute or print something. Each gets a convention (Section 2).
- **Faults:** places where a signed rule, read exactly as written, could mislead. Each is written down, the reading is left exactly as signed, and a description is printed beside it (Sections 3 and 4).

**No signed line, threshold, sample size, seed, pool, or start changes. No reading is added, removed, or reworded.** The one change to a signed computation is a possible widening of the interval, under a criterion fixed here before the test that could trigger it has run (Section 5).

**Nothing here has seen a carry-over number.** When this file was written, no adversary setting had been scored on any batch other than the one it was found on, the made-up-data test had not run, and the pilot's sealed shuffled harms remained unopened. What did exist: the pilot's unsealed own-batch results on calibration batches, and each researcher's predictions, filed before these entries were drafted.

## 0. Identity

| Entry | Value |
|---|---|
| Amends | Freeze file, Part 1, version 1, signed by the PI on 5 October 2026 |
| Amendment | 1 |
| Date | 5 October 2026, session 5 |
| Commit | The first commit of branch `session-005-lead`, which carries this file as `vpd-audit-2/freeze/amendment1.md` beside the unchanged Part 1. Every deciding job records a commit that descends from it |
| The PI | Told in the session 5 transcript, before any deciding run, of faults 3.2 and 3.11, of the team's default for each (description only), and that giving either number a signed line is possible only before the run. Part 1 does not require a signature on an amendment. A line added by the PI before the run would be a second dated amendment |
| Specifications | Three binding specifications are committed beside this file, unchanged, under `vpd-audit-2/freeze/amendment1_specs/`: the interval and its test; the printed output and the reading logic; the results table and the run. Where a specification and this amendment differ, this amendment governs, and Section 9 lists the differences |
| Later entry | The interval multipliers of Section 5, in a separate dated file, `vpd-audit-2/freeze/amendment1_multipliers.md`, committed after the made-up-data test and before any deciding run |

## 1. Symbols

All harms are per-token KL divergence in nats, averaged over cells at one search length or harm level. A **row** is one line of a table: a search length (20, 40, 80, 160, or 320 steps) or a harm level (2, 5, or 10 nats).

- $\mathrm{KL}_0$: harm of the random starting point on a held-out batch.
- $\bar X$: raw harm, on held-out batches, of settings carried over from attack batches.
- $\bar Y$: raw harm of the held-out batches' own searches. $\bar Y^{20}$: that of their own 20-step searches, the yardstick for "large".
- $\bar S$: raw harm, on held-out batches, of the 8 shuffled copies of each carried setting.

The two signed ratios, unchanged, are

$$
\tau = \frac{\bar X - \mathrm{KL}_0}{\bar Y - \mathrm{KL}_0}, \qquad \tau^{\mathrm{shuf}} = \frac{\bar X - \bar S}{\bar Y - \bar S}.
$$

The **deciding interval** $[L, U]$ of a statistic is the signed interval of Part 1's Section 5, times the row's multiplier if Section 5 of this amendment records one above 1.

## 2. Gaps Filled

Each entry quotes the signed text, states the convention, and gives the reason. Every entry was made before any carry-over number existed.

### 2.1 The Order of the Three Questions, and What Is Printed

**Signed.** "**Large.** ... As frozen: unchanged; read first at 40 and 80 steps." And, of the step table: "'does not carry over' when the interval of $\tau_n$ lies below 0.2 ... As frozen: unchanged." The plan's Section 6.6, which those lines freeze, asks: "If not large, does it **carry over** at all?"

**Gap.** The signed file states the order only for 40 and 80 steps. The script must print something at 160 and 320 steps and at every harm level, and for every combination of verdicts.

**As amended.** In both tables the script prints the three verdicts separately, each as yes, no, or undetermined, read from the deciding interval:

| Verdict | Statistic | yes | no | undetermined |
|---|---|---|---|---|
| Large | $\bar X - \bar Y^{20}$ | $L > 0$ | $U \le 0$ | $L \le 0 < U$ |
| Carries over | $\tau$ | $L \ge 0.2$ | $U < 0.2$ | $L < 0.2 \le U$ |
| Depends on the choice | $\tau^{\mathrm{shuf}}$ | $L \ge 0.2$ | $U < 0.2$ | $L < 0.2 \le U$ |

These are the plan's words: "above zero" and "at or below zero" for large; "at or above 0.2" and "below" for the two ratios.

- **At 20 steps** "large" is not asked, and the carry-over verdict is printed with its signed name: "Carries over", "Batch-specific", or "Undetermined". No step-table cell is printed.
- **From 40 steps, in the step table,** the cell is printed with "large" asked first, the plan's order:

| Large | Carries over | Row of the step table |
|---|---|---|
| yes | yes | Large |
| yes | undetermined | Large, with the note of fault 3.1 |
| yes | no | Large, with the collision flag of fault 3.1 |
| no | yes | Not large, but carries over |
| no | no | Does not carry over |
| no | undetermined | Undetermined between "Not large, but carries over" and "Does not carry over" |
| undetermined | yes | Undetermined between "Large" and "Not large, but carries over" |
| undetermined | no | Undetermined between "Large" and "Does not carry over" |
| undetermined | undetermined | Nothing settled |

  The column is "Depends on the choice" when that verdict is yes, "Does not depend on the choice" when it is no, and undetermined otherwise. A signed cell sentence is printed only when both row and column are settled, except "Does not carry over", whose signed sentence covers either column. Otherwise the script names the part that is settled and says the rest is undetermined at that search length, as Part 1 requires.
- **In the harm-level table** the three verdicts are printed and no cell, since the signed rules define cell sentences for the step table only. Each yes is tagged "confirmatory". Each no is followed by the signed caveat, verbatim. If more than 10 of 80 searches are missing on either side, all three verdicts print "undetermined" and the row's numbers are still printed in full.
- **Every signed sentence is printed verbatim.**

**Reason.** The plan's order is general, and the freeze says "unchanged". Fault 3.1 records what this order prints where two signed sentences collide.

### 2.2 An Interval of the Shuffled Ratio Wholly Below Zero

**Signed.** Section 4's four readings: interval "At or above 0.2", "Above zero, below 0.2", "Includes zero", "Straddles 0.2". For the step table's column, the plan's Section 6.6: "Yes if the interval of the shuffled ratio $\tau^{\mathrm{shuf}}_n$ lies at or above 0.2; no if it lies below."

**Gap.** An interval lying wholly below zero matches none of the four readings.

**As amended.** The four readings are tested in this order: at or above 0.2 ($L \ge 0.2$); straddles 0.2 ($U \ge 0.2$), which gives the signed precedence over "includes zero"; wholly below zero ($U < 0$), for which the script prints "no reading defined" and coerces nothing; above zero and below 0.2 ($L > 0$); otherwise includes zero. The step-table column is defined by the signed text and is read as signed: an interval wholly below zero lies below 0.2, so the column is "does not depend on the choice", printed with the flags of fault 3.3.

**Reason.** The script must print something, and the column already has a signed rule.

### 2.3 Missing Searches at a Harm Level

**Signed.** "A search that never reaches $h$ by step 320 is missing at $h$. A level is Undetermined if more than one eighth of attack searches, or of held-out searches, are missing at it: more than 10 of 80 per side."

**Gap.** The rules do not say how the ratio, the "large" difference, the batch part of the interval, and the start part are computed when one to ten searches are missing, which the pilot makes the expected case at 5 nats (3 of 64 pilot searches never reached it).

**As amended.**

1. **The signed count rule decides Undetermined exactly as written.** Nobody adjusts anything after seeing the count.
2. **Every mean runs over every cell where its quantity exists.** A carried-over cell counts whenever its attack search reached the level, on all held-out batches, whether or not that held-out batch's own search reached it. An own-search value counts whenever that held-out search reached the level. The yardstick for "large" always exists.
3. **The batch part** resamples batches as signed. A batch with no search at the level stays in the resampling and contributes no cells. Each mean's deviation in a resample is its centred total over the original count, the usual treatment of a mean whose count varies between resamples.
4. **The start part** uses the complete sub-table: all five starts, the attack batches with all five searches present, and the held-out batches with all five present. When a level is read, that sub-table is at least 6 by 6 by 5.
5. **Wording.** A row computed with missing searches is described as holding for searches that reached the level, since the searches that never reach a level are those that stall low.

*Worked example.* Two attack batches, two held-out batches, two starts; the search on attack batch 2 from start 2 never reaches the level. The carried-over mean then runs over 6 cells and not 8: three attack searches on two held-out batches each. The own-search mean still runs over all 4 held-out searches. Attack batch 2 keeps its one remaining search and weighs half as much as attack batch 1.

**Reason.** The mean-square formula of the signed Section 5 assumes a complete table. The alternative of keeping only triples where both searches reached the level was rejected: a carried setting's harm on a held-out batch does not depend on that batch's own search, so the alternative discards valid cells and gives less weight to unseen text whose own searches stall.

### 2.4 Details of the Interval

**Signed.** Section 5, items 1 to 5.

**Gap.** The rules do not say whether each bootstrap replicate recomputes the ratio or averages the linearized cells, what the percentile interval is taken over, how the shuffled ratio's linearized cell is formed, or what $\nu$ is when the start variance is truncated to zero.

**As amended.**

- **Each bootstrap replicate averages the linearized cells,** with the ratio and its denominator fixed from the full table. The batch part and the start part then describe the same quantity in the same units, a replicate with a denominator near zero cannot inflate the variance, and the bootstrap variance has an exact closed form against which the script checks every interval it prints.
- **The percentile interval** is taken over the statistic recomputed in each replicate. It resamples batches only and is description.
- **The shuffled ratio's linearized cell uses each cell's own shuffled harm,** never the grand mean, so that a held-out batch that is easier to harm cancels between numerator and denominator.
- **When $V_c = 0$, $\nu = K - 1$,** the limit of the signed formula.
- **The signed interval rule is applied, unscaled, to plain differences** such as $\bar X - \bar S$, as it already is to the "large" difference.

**Reason.** Each choice changes a number the script prints. None changes a line.

### 2.5 Tie-Breaks

**Signed.** "Step $n$ decides; step $n-1$ is scored beside it at 160 and 320." The percentile interval is "Reported beside" the signed interval. "Every result also recomputed without the 11 held-out texts" is description.

**As amended.** Step $n$ decides over step $n-1$. The deciding interval decides over the percentile interval. The main reading decides over the recomputation without the 11 texts. Every disagreement is printed as a flag.

**Reason.** Each is what the signed text implies; stating it removes a choice after the data.

### 2.6 The Delta-On Run's Summary

**Signed.** The design includes "the run with delta components held at 1 at 8 by 8 (A1 to A8, H1 to H8) with the same starts". No line and no description is given for it.

**As amended.** Description only, with no verdict word, at each search length, on the 8 by 8 by 5 cells the two runs share:

- its own carry-over ratio and shuffled ratio, with the signed interval, beside the lead's on the same cells. The held-out batches' own searches are also run with the delta entries held at 1, and its starting harm is that of the start with the delta entries at 1;
- the share of carried-over added harm remaining, delta-on over lead, and the same share for own-search added harm;
- beside those shares, the range the made-up-data test finds when the delta components have no effect.

The summary may be taken to show whether a search that cannot move the delta entries still finds harm that carries over. It may not be read as the share of the lead's harm that comes from the delta components: a search with those entries held is a different search and can reach the same harm by another route, and long searches vary widely from path alone.

**Reason.** A run with no fixed summary invites one chosen after the data.

### 2.7 Steps 159 and 319

**Signed.** "The step-$(n-1)$ readings at 160 and 320" are fixed as description.

**As amended.** The design gives those two steps no shuffled copies. They carry the "large" difference and the carry-over ratio only, and the output says so.

### 2.8 The 11 Overlapping Held-Out Texts

**Signed.** "Every result also recomputed without the 11 held-out texts that share a 50-token span with an attack text."

**Gap.** The manifest stores only the count.

**As amended.** The ids are recomputed with the manifest's own function and committed before the run, with a test that there are 11. The list depends on text alone. In the recomputation each held-out batch's harm is the mean over the texts not excluded; no search is rerun.

### 2.9 Starts

**Signed.** Section 2: "**9 to 13: question 2's deciding runs** ... 14 to 24: reserved for question 2 by amendment only", and 41 to 45 for the rerun of the first post's comparison. Section 0 points to `starts_1_64.json` for the allocation, and that file's note gives 9 to 24 to question 2 and 41 to 48 to the rerun.

**As amended.** Section 2 governs. The file cannot be edited, since its hash is signed. The run code hard-codes starts 9 to 13 and refuses any other.

## 3. Faults Recorded, Readings Unchanged

Each was found before any carry-over number existed. In each, the signed reading is printed exactly as signed.

### 3.1 "Large" and "Does Not Carry Over" Can Both Apply

The yardstick for "large" stays near 0.77 nats while own-search harm grows to about 25. So the share of a search's added harm that must carry over to be "large" falls from about 30 percent at 40 steps to about 6 percent at 80 and about 2 percent at 320; at the harm levels it is about 33, 11, and 5 percent at 2, 5, and 10 nats. From 80 steps, and at 5 and 10 nats, a carry-over ratio between that share and 0.2 satisfies both "large" and the signed line "'does not carry over' when the interval of $\tau_n$ lies below 0.2".

*Worked example.* 320 steps, starting point 0.215, own 20-step harm 0.77, own 320-step harm 25.2, carried-over harm 2.2. Then $\tau = 1.985/24.985 = 0.08$ and the "large" difference is $2.2 - 0.77 = +1.43$. With tight intervals, both signed sentences apply.

**Printed.** By entry 2.1 the cell is in the row "Large". When "large" is yes and "carries over" is no, the script also prints, in the step table: *Collision: the signed line "'does not carry over' when the interval of $\tau_n$ lies below 0.2" also applies to these data.* At a harm level it prints: *Collision: "large" is yes and "carries over" is no at this harm level.* When "large" is yes and "carries over" is undetermined, it prints: *The carry-over ratio is undetermined against 0.2.* The post reports any collision as one.

### 3.2 The Shuffled Ratio Measures Retention; Its Readings Are Worded as Composition

$\tau^{\mathrm{shuf}}$ is the share of the own search's margin over shuffled copies that a carried setting keeps. The signed sentences speak of how much of the carried-over harm depends on the choice of components, which is a different quantity, the **composition share**

$$
\kappa = \frac{\bar X - \bar S}{\bar X - \mathrm{KL}_0},
$$

the part of the carried-over added harm that shuffled copies do not reproduce.

*Worked example,* the plan's own illustration: start 0.24, own search 0.83, carried 0.70, shuffled 0.60. Then $\tau = 0.46/0.59 = 0.78$, $\tau^{\mathrm{shuf}} = 0.10/0.23 = 0.43$, and $\kappa = 0.10/0.46 = 0.22$. The signed reading is "depends on which components the adversary chose", while shuffled copies reproduce 78 percent of the carried-over added harm. The reverse also occurs: with carried 2.2, shuffled 0.45, own search 25.2, and start 0.215, $\tau^{\mathrm{shuf}} = 0.07$ reads "Mostly harm from extreme masks", while $\kappa = 0.88$.

Three consequences are recorded with it:

- The cell "A random permitted setting that switches off and on as many components at each level of usage also hurts unseen text; the search's particular choice is fitted to its batch" presupposes that shuffled copies are themselves harmful, which the rules do not check.
- When shuffled copies do little, $\tau^{\mathrm{shuf}}$ and $\tau$ are nearly one number. "Carries over" and "depends on the choice" are then one finding plus the observation that shuffled copies do little, and the post does not count them as two.
- $\kappa$ is unstable when the carried-over added harm is not clearly above zero, and is withheld there.

**Printed.** The signed reading, then the descriptions of Section 4. $\kappa$ is description. It has no line and can never be given one after the data.

### 3.3 A Shuffled-Ratio Denominator That Is Near Zero or Negative

If shuffled copies do nearly as much harm as the own search, $\bar Y - \bar S$ is near zero and the linearized interval cannot be trusted. If they do more, numerator and denominator are both negative, the ratio is positive, and the signed reading is "depends on the choice" for data that show the opposite.

**Printed.** Beside every shuffled reading, $z_D = (\bar Y - \bar S)/\mathrm{se}(\bar Y - \bar S)$, with the unwidened standard error. Three flags are triggered only by the sign of an interval: one when the interval of $\bar Y - \bar S$ includes zero, saying the shuffled ratio is not reliable in this row; one when it lies at or below zero, saying the ratio's meaning is inverted; and one when the interval of $\bar X - \bar S$ lies below zero, saying carried settings do less harm than their shuffled copies. The made-up-data test reports coverage against $z_D$, and the post quotes that coverage at the observed $z_D$. No precondition is placed on the reading.

### 3.4 The Pooled Ratio Weights by Harm

Both ratios are ratios of means. At 40 and 80 steps the means are dominated by the searches that have broken out. A pooled ratio licenses a sentence about harm in total ("about so much of the harm found at 80 steps carries over") and none about a typical setting.

**Printed.** Beside every row, the signed description of each setting's retention: its carried-over added harm, averaged over held-out batches, divided by its added harm on its own batch. In step rows it is split by whether the setting's search has passed 5 nats.

### 3.5 What a Shuffle Holds Fixed

A shuffled copy keeps the counts of mask values within each matrix and each usage decile, and leaves the 24 delta entries in place. So "does not depend on the choice" means "not beyond matrix and decile", harm that rides on the delta entries survives every shuffle, and a stratum whose entries are nearly equal is nearly unchanged by one.

**Printed.** The signed sentence verbatim; separately, the share of alive entries a shuffle moves by more than 0.5, and the mean absolute change.

### 3.6 The Signed Expectation of an Undetermined 40-Step Ratio

The signed file says: "At 40 steps no affordable design does, so a 40-step ratio reading of "undetermined" is expected, not a surprise." The precision target was a relative half-width (projected 0.36), while the verdict depends on the estimate's distance from 0.2. None of the four independent predictions filed in session 5 gives "undetermined" at 40 steps more than 0.29. With the projected width, that reading needs an estimate between about 0.15 and 0.31, or carried-over cells far noisier than the pilot's own-batch cells. The post therefore reports an undetermined 40-step ratio for what it implies, and does not present a determined one as beating expectations.

### 3.7 Rare Early-Breakout Batches

In the pilot one batch of eight broke out by step 20 and supplied a quarter of all 20-step added harm. A side of 16 batches holds no such batch about 12 percent of the time, and a bootstrap cannot resample a kind of batch it never drew. No widening repairs this. The post states it as a limit of 16 batches per side.

**Printed.** Per side, all 16 batch means of own-search added harm at 20 and 40 steps, sorted. No cutoff defines an "early-breakout batch".

### 3.8 The Number of Intervals

The two tables hold 23 verdict intervals at 95 percent each (two at 20 steps, three at each of the four longer lengths, three at each of three harm levels), with no correction for their number. The post says so.

### 3.9 Selection and Overshoot in the Harm-Level Rows

A level's row excludes searches that never reach the level (entry 2.3). And a setting is taken where the two-step mean of its own harm first reaches the level, so a search that jumps can supply a "2-nat" setting whose own harm is far higher.

**Printed.** Per level: the number of searches missing per side and the batches they belong to, and the median and maximum of the scored settings' actual own harm.

### 3.10 "Lie on the Stage Curve" Has No Definition

The signed Section 8 says: "Only if the 80-step sources lie on the stage curve may the post call an undetermined 80-step cell a matter of timing." No tolerance is defined, and none is set here. If the post makes that claim, it labels it a judgement from the pre-registered scatter and shows the figure.

### 3.11 The Signed Ratio Divides by the Other Side's Searches

$\tau$ divides the carried-over added harm by the added harm of the held-out batches' own searches. Whether a held-out batch's search has broken out by a given step is nearly independent of whether an attack batch's has (they share only their starts), so at 40 and 80 steps the numerator and the denominator carry separate timing noise. Dividing instead by the attack searches' own added harm, the **pooled retention**, estimates the same population quantity, since the manifest splits the two sides at random from one corpus, and the timing noise cancels within each search. The two are tied by an identity: $\hat\tau$ equals the pooled retention times the ratio of the attack side's mean own-search added harm to the held-out side's, and that ratio's true value is 1.

**Printed.** The pooled retention with an interval, as description, beside every row. It never changes a verdict word, and it can never be given a line after the data. A straddling cell stays Undetermined, as signed, and the post does not use the pooled retention to call it determined. If the signed ratio is undetermined where the pooled retention is not, the post reports both and names this fault; the repair is a repeat on fresh text with the estimator fixed in advance.

## 4. Descriptions Added, None With a Line

Printed in the same row as the reading they accompany. None has a threshold or a verdict word, and none may be given one after the data. Three of them are printed as fixed sentences in every row, whatever the numbers show, so that no warning fires at a new threshold.

| Description | Beside | Why |
|---|---|---|
| $\mathrm{KL}_0$, $\bar S$, $\bar X$, $\bar Y$, $\bar Y^{20}$ in raw nats, and the attack side's own start and own-search harm | Every row | Already required in kind by the signed rules |
| $\bar X - \bar S$ with an interval | Every shuffled reading | Faults 3.2 and 3.3 |
| A sentence giving $\bar Y - \bar S$ with an interval and $z_D$ | Every shuffled reading | Fault 3.3 |
| A sentence giving how many nats of the carried-over added harm shuffled copies reproduce and do not, then $\kappa$ with an interval; withheld when the interval of $\bar X - \mathrm{KL}_0$ reaches zero | Every shuffled reading | Fault 3.2 |
| A sentence saying whether shuffled copies exceed, do not exceed, or are not distinguishable from the yardstick, from the interval of $\bar S - \bar Y^{20}$ | Every shuffled reading from 40 steps | Fault 3.2, first consequence |
| Share of alive entries a shuffle moves by more than 0.5, and the mean absolute change | Every shuffled reading | Fault 3.5 |
| Each setting's retention, split in step rows at 5 nats of own harm, and the pooled retention with an interval | Every row | Faults 3.4 and 3.11 |
| Sorted batch means of own-search added harm at 20 and 40 steps, per side | Once | Fault 3.7 |
| Missing counts and scored own harm per level | Harm-level rows | Fault 3.9 |
| The delta-on summary of entry 2.6 | Once per search length | Entry 2.6 |

## 5. The Error-Bar Test: Criterion and Repair, Fixed Before the Test Runs

The signed interval is the team's own construction. Before any deciding run it is tested on made-up experiments with known answers. This section was written before that test ran.

**5.1 The test.** Made-up experiments are built on the pilot's 64 real own-batch searches, which have the shape that threatens the interval: breakouts, alternation, stalls, and one batch in eight that rises early. Carried-over and shuffled harm are invented, with a true answer known by enumeration. The scenario list is closed before the test runs: 13 core scenarios, 8 stress scenarios, and 2 checks with exact known answers. Each scenario has 2,000 experiments.

- **Core scenarios** decide pass or fail and set the repair. They place the truth of each signed reading on its line and away from it, with and without a realistic start effect, and include one in which settings that have broken out carry over differently from those that have not.
- **Stress scenarios** are reported and become stated limits. They cover rarer and commoner early-breakout batches; a rare kind of batch that carries over differently; a large start effect; carried-over cells that jump to 40 nats; shuffled harm swept from 0.3 to 1.25 times the own search's; batch-clustered missing searches; and the delta-on run when the delta components do nothing.

**5.2 "Too narrow".** For each core scenario, at each row, for each of the three signed readings, the cell fails if its coverage is below 92.5 percent, or if, with the truth on a line, the interval lies wholly on one side of the line in more than 3.75 percent of experiments. A cell with coverage under 93.5 percent, or with more than 3.25 percent of intervals wholly on one side of its line, is rerun with 10,000 experiments, and is then judged on the rerun alone, by both criteria. A harm-level row is judged on the experiments in which the count rule lets the level be read. *(All conventions.)*

**5.3 The repair.** A row whose core cells all pass keeps a multiplier of 1. Otherwise the row gets one multiplier above 1 on the half-width:

1. For each of the row's core cells, the multiplier it needs is the 95th percentile of the absolute error over the unwidened half-width; where the truth is on a line, also the 96.25th percentile of the signed error over the half-width, in each direction.
2. The row's multiplier is the largest of these, rounded up to a multiple of 0.05.
3. It is confirmed on 2,000 fresh experiments per core scenario from a second seed: every core cell of the row must pass with it. If one does not, the multiplier rises by 0.05 and is confirmed on a third seed.
4. A row needing more than 1.5 goes to the PI.

Once recorded, the widened interval is the interval of record for every reading and every description in that row, and for the delta-on run at the same search length. The unwidened interval is reported beside it as description. No interval is ever narrowed. *(The grid and 1.5 are conventions.)*

*Worked example.* A row's worst core cell has coverage 91.8 percent and a 95th percentile of absolute error over half-width of 1.12, and no other cell needs more. The row's multiplier is 1.15. If the fresh set gives that cell 95.1 percent, the row is done.

**5.4 Stated, not repaired.** Stress scenarios set no multiplier. Each stress cell under 92.5 percent is listed in the test's report and stated in the post as a limit. Fault 3.7 is one.

**5.5 Known-answer checks** run beside coverage: every harm multiplied by 100, which must leave every ratio's interval unchanged and scale every difference's by 100; the bootstrap variance against its closed form, on every interval; three worked examples with hand-computed answers, one of them with a missing search; a table with no dependence on the start; a "digits" table with closed-form means; the plan's worked example; a setting constant within strata; a search that jumps from 1 to 40 nats in one step; alternation across a level; 10 against 11 missing searches; a table with one cell deleted, which the script must refuse; and 36 cases of the reading logic with the expected printed verdicts.

**5.6 The multipliers.** This file does not change once committed. The multiplier recorded for each row, the coverage that set it, and the commit of the test's report are entered in a separate dated file beside it, `vpd-audit-2/freeze/amendment1_multipliers.md`, committed after the test and before any deciding run. The analysis script refuses to read a real table without that file.

## 6. Run Requirements Added to Section 10

These add to the signed Section 10 and remove nothing from it.

- **One side per container.** A container that holds a held-out batch never receives the token ids of any attack batch, and the reverse. Scoring a setting on the batch it was found on would give a carry-over ratio near 1, which is the result the team predicts, so this error is guarded by construction.
- **Saved.** Per-text harm from every scoring pass; hashes of each batch's token ids, labels, target, and weight deltas, with each search and each scoring job; all 8 shuffled harms per carried setting; per-entry gradients summed up to each saved step. Per-position harm is not saved.
- **Guards.** The scored batch's name and hash in every row; every scored setting re-scored on its own batch and equal to its search's record bit for bit; no carried-over setting's 128 per-text harms all equal to its per-text harms on its own attack batch; the save hook's step equal to the crossing rule's; atomic writes with a completion marker; label and target hashes compared on every restart; jobs return only identifiers, counts, seconds, hashes, and guard outcomes; assertion messages carry no values; the script refuses a partial table.
- **Sealing, wider than signed.** Every harm from a deciding batch is sealed, own-batch records and missing counts included, until the committed analysis script runs. The script runs only once both runs' tables are complete, or the PI has ruled on the delta-on run after a spend stop.
- **A rehearsal** on calibration batch C1 runs first, since the step that copies sealed files has not run in the cloud. It scores nothing on another batch.
- **Spend.** As signed: the lead first, spend checked between stages, the delta-on run last, nothing trimmed silently. With overhead counted, the projection is about \$100 at the pilot's billed rate of \$6.80 per function hour. Projected spend is recomputed after the rehearsal, after the attack side, after the first held-out container, and before the delta-on run, at the larger of \$6.80 and this run's own billed rate. If it exceeds \$105, work stops and goes to the PI.

## 7. Not Done Under This Amendment

Recorded so that each absence is on file before the data. All but the last two need forward passes on saved settings only, with no search rerun.

- **The composition analyses** of the signed Section 4 (token-level split, exploited components, pin test). Their lines stay exactly as signed.
- **The plan's baselines** on every held-out batch (every mask at its label, the first post's aggregation setting, frequency-matched settings), and its two coarser shuffles (within alive and dead only; over the whole matrix). Neither is in the signed design or its cost.
- **The lead's own settings re-scored with their delta entries reset to 1,** which is what would show how much of the lead's carried-over harm sits in those entries.
- **Harm-level settings of the delta-on run** are saved but not scored, as the signed cost assumes.
- **The plan's breakdown by position,** since per-position harm is not saved.
- **The pilot's sealed own-batch shuffled harms stay sealed.**

## 8. Conventions Introduced, in One Place

The coverage floor of 92.5 percent, the false-verdict ceiling of 3.75 percent, and the rerun triggers of 93.5 and 3.25 percent; 2,000 and 10,000 simulated experiments; the multiplier's grid of 0.05 and its limit of 1.5; "moves by more than 0.5" for the share of entries a shuffle changes; the split of per-setting retention at 5 nats of own harm; \$6.80 per function hour as the floor of the spend projection. None bears on a signed line.

## 9. Where This Amendment Overrides the Specifications

The three specifications were written in parallel. Where they differ from each other or from this amendment, the following governs.

1. **Collision flags.** The flags for "large" with "carries over" no or undetermined print the sentences of fault 3.1, not the phrases "large, with low retention" and "large; carry-over ratio undetermined".
2. **No count of early-breakout batches.** The script prints the sorted batch means of fault 3.7 and no count against "twice the median" or any other cutoff.
3. **Which interval is of record.** In a row with a multiplier above 1, every printed interval, of all statistics, takes the multiplier, and every verdict and flag is read from it. $z_D$ alone uses the unwidened standard error, since the test's bins of $z_D$ are defined that way.
4. **Nine statistics.** The interval routine serves all nine statistics of the output specification, the three it adds being plain means or ratios of the same two kinds of mean, and the two shares of the delta-on summary. The test's report gives coverage for all nine; pass and fail are judged on the three signed readings.
5. **The table** also carries, per shuffled copy, the mean absolute change over alive entries.
6. **Pooled retention** is printed with an interval, under fault 3.11's rule that it never changes a verdict word.
7. **Three details of the test and its checks,** settled when the engineer asked before writing any code:
   - the rerun rule of Section 5.2 above, with its second trigger, replaces the interval specification's;
   - the check of the bootstrap variance against its closed form allows a band of 5 Monte Carlo standard errors of their ratio, computed from the replicates' kurtosis and never under 0.07, in place of 0.90 to 1.10; a miss is an error;
   - the guard on the made-up-data generator compares all five plain means with their true values at search-length rows, stops the test at 5 Monte Carlo standard errors, and lists every comparison above 3.5.
