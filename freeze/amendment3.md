# Freeze File, Part 1: Amendment 3

*Session 5. Written by Ines from the team's review of the made-up-data test of record, and recording the PI's decision on it. Written after that test had run and before any deciding run.*

## What This Amendment Does

Amendment 1 fixed, before any test, how the lead experiment's error bars would be tested on made-up experiments with known answers, and how they would be widened if found too narrow: one multiplier per row, computed from the test, confirmed on fresh experiments, and capped at 1.5, with any row needing more going to the PI. The test of record has run. Every row's computed need exceeds 1.5, so by that rule every row went to the PI. This amendment records the PI's decision and what the record must carry with it.

**No signed line, threshold, sample size, seed, pool, or start of Part 1 changes.** The multipliers of Amendment 1's Section 5.3 are 1 in every row, by the PI's decision and not by the rule, for the reason in Section 3.

**No carry-over number existed when this was written.** No adversary setting had been scored on any batch other than the one it was found on.

## 0. Identity

| Entry | Value |
|---|---|
| Amends | Amendment 1, Section 5.3, as committed at `c1d256c` on branch `session-005-lead`, and the multipliers file it provides for |
| Amendment | 3 |
| Date | 6 October 2026, session 5 |
| Commit | A commit of its own on `session-005-lead`, carrying this file as `vpd-audit-2/freeze/amendment3.md` and the multipliers file `vpd-audit-2/freeze/amendment1_multipliers.md` with its machine-readable copy, pushed before any deciding run |
| The PI's decision | "B sounds good", in the session 5 transcript on 6 October 2026, choosing option B of four put to the PI: (A) widen every row as the rule computes; (B) widen nothing and state the limit; (C) widen "large" alone; (D) change the yardstick |
| A correction before commit | When the PI chose B, Ines had told the PI that option A "would probably have turned the 80-step reading undetermined". Daniel showed that statement unsupported (Section 3 gives the correct figures). Ines corrected it with the PI before this file was committed and asked whether B still stood. The PI replied: "Yes, B still stands" |
| A decision after a look | This is the second. Amendment 2 was written after a 100-experiment plumbing run of the test; this amendment is written after the test of record itself, which is what it rules on |

## 1. What the Test of Record Found

The test and its results are in `vpd-audit-2/results/s5_madeup/` and the engineer's reports, `sessions/005/engineering/plan_1.report_1.md` and `plan_1.report_2.md`; the test ran at commit `7c30101`, and the split by count below at `155df44`. Master seed 20261006; 2,000 experiments per scenario, 10,000 for a rerun. The two checks with exact known answers passed: coverage 0.9505 against 0.95; bootstrap variance 2.9316 times the true variance against 2.9375.

**Of 299 core cells, 50 failed:** 37 of the "large" difference, 10 of the shuffled ratio, 3 of the carry-over ratio.

| Statistic | Coverage | Where it failed | Largest multiplier its cells would need |
|---|---|---|---|
| Carry-over ratio | 0.95 to 0.98 from 80 steps and at every harm level | 20 steps, with the truth on the line; 40 steps in one scenario | 1.26 |
| Shuffled ratio | 0.94 to 0.99 from 80 steps and at every harm level | 20 steps; 40 steps where the truth is on the line | 1.89, at 20 steps only |
| "Large" difference | 0.71 to 0.97 in the four scenarios whose carried harm is 0.2 to 0.6 nats, lowest at 10 nats; 0.87 to 0.98 elsewhere | From 40 steps and at every harm level, mostly in those four scenarios; at 2 and 5 nats in most others | 3.17, at 10 nats |

The multiplier each row would need by Amendment 1's rule: 1.90, 1.65, 1.85, 2.15, 2.15 at 20, 40, 80, 160, and 320 steps; 2.55, 2.60, 3.20 at 2, 5, and 10 nats. Every row exceeds 1.5.

**The generator as committed in Amendment 1,** run beside it on the same seed and printed in full, failed 200 of 299 cells and would have required 1.50 to 3.00 per row. It set no multiplier, as Amendment 2 fixed.

## 2. What the Failures Are

The engineer identified one mechanism behind nearly every failing cell. Daniel, the interval's author, confirmed the arithmetic and the diagnosis, and the rest of the team reviewed it.

The yardstick for "large" is the held-out batches' own 20-step harm. In the pilot, one calibration batch in eight (type C5) took twice the others' harm at 20 steps, and the made-up experiments keep that measured fact. A held-out side of 16 batches holds no such batch with probability $(7/8)^{16} = 11.8$ percent. In those experiments the yardstick is low by about $(1.18 - 0.51)/8 = 0.084$ nats, the "large" estimate is high by the same amount, and the interval is narrow, because no held-out batch stands out to resample. The variance estimate is close to right on average: in 48 of the 50 failing cells the estimated variance over the true variance lies between 0.94 and 1.14. In the other two, both "large" at 10 nats, it is about 1.6, because the experiments judged there are a selected fifth; those two cells still have the lowest coverage of the 299 core cells, 0.735 and 0.713. So the fault is not the size of the variance estimate. It is small exactly in the samples where the estimate is biased, and no interval built by resampling 16 units can see a kind of unit the sample does not hold.

**The split by count, on the record's seed,** pooled over the 91 "large" core cells:

| Early-breakout batches on the held-out side | 0 | 1 | 2 | 3 or more |
|---|---|---|---|---|
| Coverage of "large" | 0.527 | 0.928 | 0.982 | 0.977 |

Thirty-six of the 37 failing "large" cells cover at or above 0.925 whenever the held-out side holds two or more such batches. The 20-step ratios fail by the same mechanism on the attack side: the carry-over ratio covers 0.767 with no early-breakout attack batch and 0.96 or better otherwise; the shuffled ratio 0.477, then 0.94 or better.

The mechanism is not shown for six failing cells:
- **The shuffled ratio at 40 steps where its truth is on a line** (three cells). They were not split by count. They miss below, as the 20-step ratios do, and are presumed to share the mechanism.
- **Scenario P13 at 40 steps** (three cells, one for each reading). P13 mixes settings that have broken out with settings that have not and gives them different retention. Its "large" cell was split by count and covers 0.946, 0.944, 0.932, and 0.887 with 0, 1, 2, and 3 or more early-breakout held-out batches. Coverage falls as the count rises, so the yardstick is not what fails that cell; the mixture is. Its two ratio cells were not split.

**The direction.** Thirty-six of the 37 failing "large" cells miss above the truth: the false verdict this flaw produces is "large = yes", a systematic defect by the paper's own test, which is also the finding every member of the team predicted. The failing 20- and 40-step ratio cells miss below.

**The size on real data,** from the pilot: 0.084 nats is 11 to 17 percent of the predicted "large" difference at 40 steps and at 2 nats, 1.3 percent at 80 steps, under 0.5 percent at 160 and 320, and 3 percent at 5 nats. On the team's predictions it can move a "large" verdict only at 40 steps and at 2 nats, and only in the one sample in eight that holds no early-breakout held-out batch.

**The assumption.** The amended generator makes carried harm independent of the held-out batch's type. If real held-out batches differ in how much carried harm they take, the as-committed version, printed beside the test of record, is the other bracket.

## 3. The Decision, and Its Reason

**No row is widened. Every multiplier is 1.**

**The reason.** A multiplier repairs a shortfall present in every sample: an interval whose shape is right and whose scale is off. The test found no shortfall of that kind. It found a shortfall confined to samples that happen to hold none of a rare kind of batch, in which the estimate is biased and the interval cannot know. Amendment 1 named that mechanism before the test, as fault 3.7, and said of it: "No widening repairs this." Its Section 5.4 assigns it to the stress scenarios, which are stated and set no multiplier. The test shows the mechanism reaching, through a 20-step yardstick, every "large" cell whose carried term is small. Widening every statistic in every row by 1.65 to 3.2 would blur the two ratios, whose intervals the same test shows are the right size, for a reason the test does not support.

**What widening would have cost, stated without exaggeration.** A ratio reads "carries over" only if its interval clears 0.2. On the widths projected in Part 1, the smallest ratio that could be read as carrying over would rise from about 0.27 to about 0.37 at 80 steps, and from about 0.31 to about 0.49 at 40 steps. The five filed best guesses are 0.75 to 0.80 at 80 steps and 0.60 to 0.75 at 40 steps. So on the best guesses widening would not have changed a verdict at either length, though at 40 steps it would have raised the chance of an undetermined cell. The decision therefore rests on the principle above, not on a forecast of what widening would have done to the result.

*Worked example.* At 80 steps the projected relative half-width is 0.247, so a ratio $\tau$ has an interval reaching down to $0.753\,\tau$, which clears 0.2 when $\tau \ge 0.27$. With the rule's multiplier of 1.85 the half-width is $0.457\,\tau$, the interval reaches down to $0.543\,\tau$, and it clears 0.2 when $\tau \ge 0.37$.

**What the post must say beside every "large" verdict,** as description with no line:
- the flaw's size and direction: when the held-out side holds no batch that breaks out early at 20 steps, the yardstick is about 0.08 nats low, so the "large" estimate is about 0.08 nats high;
- the test's coverage of "large" with and without such a batch on the held-out side, 0.53 against 0.93 or better;
- the interval's lower end in nats, so a reader can see whether 0.08 nats could change the verdict;
- each side's 16 batch means of own-search added harm at 20 steps, sorted, which the analysis already prints. Whether a batch "breaks out early" is a judgement from those means, with no cutoff, labelled as one;
- that the post claims no 95 percent coverage for "large" whatever the sample.

**Beside the 20-step readings:** the same, with the attack side's batch means, and the direction reversed: the ratios read low when the attack side holds no early-breakout batch.

**Beside every shuffled reading:** the observed $z_D$ and the test's coverage in its bin. In the stress scenario that sweeps shuffled harm, the reading covered 0.96 above $z_D = 8$ at 20 steps and 0.955 to 0.967 above 5 at 80; below 5 it is mostly "straddles", and the post reads the two margins.

These quantities come from the committed test report and the analysis's existing output. No change to the analysis script is needed.

**Recorded for a repeat on fresh text, not adopted now:** a yardstick with a variance floor from the pilot's 20-step batch variance, or a yardstick pooled over both sides' 32 batches. Either targets the mechanism; either would be a new rule after the test.

## 4. What Had Been Seen

Before Amendment 2: a 100-experiment plumbing run and two diagnostics, as that amendment states. Before this amendment: the test of record in both versions, in full; the engineer's diagnostic of the mechanism on seed 777 (4,000 experiments of two scenarios); and the split by count on the record's seed. No carry-over number. The multipliers the rule computed are printed in the test's report and quoted in Section 1, so a reader can see what the rule would have done.

## 5. What Does Not Change

The signed readings and their lines; the scenario list and the criterion; every description Amendments 1 and 2 add; the design, the pools, the starts, and the cap. The multipliers file reads 1.0 in every row, so the analysis script's deciding interval equals the signed interval.
