# Freeze File, Part 1: Amendment 2

*Written from the generator author's ruling, the review's conditions, a check of the pilot's data, and the accompanying analysis. It corrects one factor in the made-up-data generator that Amendment 1 binds. It was written after a partial look at how the test behaves and before the test of record had run, and it says exactly what had been seen.*

## What This Amendment Does

Amendment 1 fixed, before any test, how the lead experiment's error bars would be tested on made-up experiments with known answers, and how they would be widened if the test found them too narrow. We built that test and, before running it for the record, found that one invented factor in the generator of made-up experiments would decide its outcome. This amendment removes that factor from the test of record, keeps the as-committed version as a second run printed in full, and adds one description to the real analysis.

**No signed line, threshold, sample size, seed, pool, or start of Part 1 changes. The test's scenario list, its pass criterion, its repair, and every threshold of Amendment 1 are unchanged.**

**No carry-over number existed when this was written.** No adversary setting had been scored on any batch other than the one it was found on.

## 0. Identity

| Entry | Value |
|---|---|
| Amends | Amendment 1 to the freeze file, Part 1, as committed at `c1d256c` on branch `session-005-lead` |
| Amendment | 2 |
| Date | 5 October 2026 |
| Commit | A commit of its own on branch `session-005-lead`, carrying this file as `freeze/amendment2.md`, pushed before either version of the test of record runs |
| The author | Told of the finding (research log) before this file was written. The results of both versions of the test go to the author before any deciding run |

## 1. What Had Been Seen

The test of record had not run. Four things had:

1. **A plumbing run of the whole harness at 100 experiments per scenario,** 200 for reruns, under master seed 20261005, in a scratch folder. It showed coverage near 0.90 in most core cells, with nearly all misses on one side, and near 0.76 at the 10-nat level. Its output is committed beside the test's report, as it was.
2. **A diagnostic on plain means** at search-length rows, on other seeds and with no intervals: the generator matched its enumerated truths (largest gap 2.6 Monte Carlo standard errors over 40,000 experiments).
3. **A diagnostic at the 10-nat level** in one core scenario, over 40,000 experiments:

| Carry-over ratio at 10 nats | Value |
|---|---|
| Truth by enumeration | 0.600 |
| All experiments | 0.600 |
| The experiments in which the level is read (7,855 of 40,000) | 0.560 |

4. **The two checks with exact known answers, at 400 experiments each:** coverage 0.950 against 0.95, and a bootstrap variance 2.940 times the true variance against 2.9375, with coverage 1.000. Neither check uses the vulnerability.

So this amendment is not blind to how the as-committed generator behaves. Its reason, in Section 3, rests on text and measurements that were on file before the generator was written, and can be checked without running anything.

## 2. The Finding

The generator of the interval specification, Section 6, step 5, gives each held-out batch a **vulnerability** that multiplies its carried-over and shuffled harm:

$$
v_j = f_{c(j)}\, g_j,
$$

where $c(j)$ is the pilot batch type the held-out batch was drawn as, $g_j$ is log-normal noise with mean 1 and standard deviation 0.1, and $f_c$ is that type's mean own-search added harm at 20 steps divided by the mean over the eight types. The factor applies at every row.

| Pilot type | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 |
|---|---|---|---|---|---|---|---|---|
| $f_c$ | 1.00 | 0.96 | 0.84 | 0.87 | 1.99 | 0.79 | 0.76 | 0.78 |

Type C5, the pilot's one batch whose searches break out early, is thus twice as vulnerable to every carried setting, at every search length. Two consequences follow.

- **In every core scenario, at every row.** A held-out side of 16 batches holds no C5 batch with probability $(7/8)^{16} = 11.8$ percent. The other seven factors average 0.858, so in those experiments carried-over harm is 14 percent below its true value, and the interval is narrow because the sample holds no vulnerable batch to resample. Wherever the interval's half-width is well under 14 percent of the estimate, coverage cannot then exceed about 88 percent, with every miss on one side.
- **At the 10-nat level.** Type C5 is also the type whose searches most often never reach 10 nats. The experiments in which that level is read therefore hold few C5 batches, and their carry-over ratio sits 6.7 percent below the truth, as the third diagnostic shows.

## 3. Why the Factor Is Removed

**The principle.** Core scenarios set the repair. They may hold only structure the pilot measured, plus invented carry-over that adds no rare or heavy-tailed structure of its own. An invented structure that can by itself decide the test belongs in the stress scenarios, which are reported and set nothing.

**The factor contradicts the amendment that governs it.** Amendment 1 records this mechanism as fault 3.7 and says of it: "No widening repairs this." Its Section 5.1 assigns "a rare kind of batch that carries over differently" to the stress scenarios, and its Section 5.4 says stress scenarios set no multiplier. The generator nonetheless placed the mechanism in every core cell.

**The pilot's measurements do not support it.** Both were on file before the generator was written.

- **A random setting harms every batch about equally.** The pilot scored 8 fixed settings, its random starting points, on each of 8 calibration batches. The batch means of that harm vary by 3.4 percent, and batch C5 sits at 0.97 of the average. No searched setting was scored across batches, so this is the nearest measurement on file and not a measurement of carried-over harm.
- **C5's excess is a property of short searches run on it.** Its own-search added harm, relative to the average of the eight batches, is 1.99 at 20 steps, 1.69 at 40, 0.85 at 80, and 0.58 at 160 and at 320, where it is the least harmed batch.

At 320 steps, in a scenario where 0.9 of a search's harm carries over, a factor of 1.99 gives a C5-type held-out batch a mean carried-over harm near 45 nats, and about 31 nats where 0.6 carries over. The largest batch mean the pilot recorded for a batch's own search is 30.3 nats.

**How it came about.** The factor was added so that carried, shuffled, and own-search harm would share a held-out batch's effect, which the test needs in order to show whether that effect cancels inside a ratio. Tying it to a batch type's 20-step harm met that aim and, unnoticed, also made one type in eight twice as vulnerable everywhere.

## 4. The Change

In the generator, in every scenario of the test of record, a held-out batch's vulnerability is

$$
v_j = g_j,
$$

log-normal with mean 1 and standard deviation 0.1, independent of batch type. The type factor $f_c$ is deleted. Carried and shuffled harm still share $g_j$. Every true value of the specification's Section 6 is unchanged, since $v_j$ still has mean 1.

*Worked example.* A held-out side whose 16 batches are all of types other than C5: under the committed generator its mean vulnerability is 0.858, and its carried-over harm reads 14 percent low. Under the amended generator its mean vulnerability is 1 whatever its types, and its carried-over harm is unbiased.

**The pilot's real early-breakout type stays in the core.** Batch types are still drawn from the pilot's eight, and a C5-type batch still has twice the own-search harm at 20 steps, on both sides, because that is measured. So the 20- and 40-step rows may still fall short, and the rule of Amendment 1 then applies as written.

## 5. What Does Not Change

- The scenario list: 13 core, 8 stress, 2 checks.
- The criterion of Amendment 1's Section 5.2, including that a harm-level row is judged on the experiments in which the count rule lets the level be read. An interval is judged where it will be used.
- The repair of Section 5.3: a multiplier of at most 1.5 from the core cells, and a row needing more goes to the author.
- Every threshold.

**One correction only.** If core cells fail under the amended generator, Section 5.3 applies as written. The generator is not changed again.

## 6. Reported Beside the Test of Record

- **The generator as committed in Amendment 1,** run in full on the same scenarios and printed in full, labelled as such, with the multiplier each row would have required. It sets no multiplier. It shows what the intervals would do if one held-out batch in eight were twice as vulnerable to carried settings.
- **For every harm-level cell,** coverage over all experiments as well as over those in which the level is read, as description.
- **The plumbing run's output,** committed as it was.

**Seed.** Both versions use one new master seed, 20261006, so that none of their experiments has been seen and the two are compared on the same draws.

## 7. One Description Added to the Real Analysis

The real table measures what the generator had to guess: it scores every carried setting on 16 held-out batches. So the script prints, per row and as description with no line, the 16 held-out batch means of carried-over added harm, sorted, each relative to their mean. A spread of about 10 percent or less, the amended generator's own, would mean the core scenarios resemble the data. One batch far above the rest would mean the as-committed version applies, and the post would say so and quote that version's coverage. If no such batch is among the 16, the table cannot show that one exists; that is fault 3.7, stated and not repaired. This description never changes an interval of record or a verdict word, and whether a batch sits far above the rest is a judgement, labelled as one.
