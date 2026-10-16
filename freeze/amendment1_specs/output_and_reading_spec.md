# What the Analysis Script Prints, and How Intervals Become Verdict Words

*The output and reading specification, binding, written before any deciding run. It implements the signed rules, `freeze/part1.md`, and the pre-run decisions (research log; items R1 to R12). Where this note and the signed rules differ, the signed rules govern.*

## 1. Purpose and Scope

The lead experiment applies mask settings that an adversary found on attack batches to held-out batches it never saw. The analysis script turns the resulting table of harms into two printed tables: the **step table**, with one row per search length (20, 40, 80, 160, 320 steps), and the **harm-level table**, with one row per level of own-batch harm (2, 5, 10 nats). Each row carries verdict words fixed by the signed rules and raw numbers beside them.

This note specifies four things:

1. the decision logic from intervals to verdict words (Section 3);
2. the printed row: which numbers appear, in what order (Section 4);
3. known-answer cases to turn into tests (Section 5);
4. the delta-on run's printed summary (Section 6).

Two neighbouring specifications cover the rest. `interval_spec.md` defines how every estimate and interval is computed, including the convention for missing searches. `table_and_run_spec.md` defines the file the script reads. This note states only what it needs from each (Section 2).

**Two design rules run through everything below.**

- **Signed sentences are printed verbatim.** Section 3.7 lists them. The script never rewords, shortens, or merges them.
- **Everything added beside them is description with no line.** Warnings are triggered only by the signed lines themselves (zero and 0.2) or by the sign of an interval. No new threshold appears anywhere in this note.

## 2. Inputs

### 2.1 The Arrays One Row Needs

A **row** is one search length or one harm level. All harms are raw per-token KL divergence in nats. Index $i$ runs over attack batches, $j$ over held-out batches, $s$ over starting points, and $r$ over the 8 shuffled copies.

| Name | Index | Meaning |
|---|---|---|
| `start` | $j, s$ | Harm of starting point $s$ on held-out batch $j$ |
| `own` | $j, s$ | Harm on held-out batch $j$ of the scored setting of its own search from start $s$ |
| `own20` | $j, s$ | Harm on held-out batch $j$ of its own search after 20 steps: the yardstick for "large" |
| `carried` | $i, j, s$ | Harm on held-out batch $j$ of the scored setting found on attack batch $i$ from start $s$ |
| `shuffled` | $i, j, s, r$ | Harm on held-out batch $j$ of shuffled copy $r$ of that same setting |
| `attack_start` | $i, s$ | Harm of starting point $s$ on attack batch $i$ |
| `attack_own` | $i, s$ | Harm on attack batch $i$ of the scored setting found on it from start $s$ |
| `attack_past`, `heldout_past` | level, then $i, s$ or $j, s$ | Whether the search's first crossing of 2, 5, or 10 nats, by the signed two-step-mean rule, falls at or before the row's step |
| `attack_cycling`, `heldout_cycling` | $i, s$ or $j, s$ | Whether own harm at steps $n$ and $n - 1$ differs by more than 10 percent of the larger |
| `moved_share`, `mean_abs_change` | $i, s$ | Over alive entries and the 8 shuffled copies: the share of entries a shuffle moves by more than 0.5, and the mean absolute change |
| `attack_missing`, `heldout_missing` | $i, s$ or $j, s$ | Harm-level rows only: the search never reached the level by step 320 |

The "scored setting" is the setting after step $n$ in a step row, and the setting at the first crossing of the level in a harm-level row. In a harm-level row, `own` and `attack_own` are the harm of that scored setting itself, never the level and never the two-step mean.

**The script must expose one function that maps these arrays to a printed row,** so that the cases of Section 5.2 can call it directly without building a whole table.

### 2.2 The Statistics and Their Intervals

Write a bar for a mean over the row's cells, and $S_{ijs}$ for the mean of the 8 shuffled harms of one cell. The row needs nine statistics. Each comes from the interval specification's interval routine, which takes the cell-level numerator, and for a ratio the cell-level denominator, and returns an estimate and intervals.

| # | Statistic | Formula | Cell-level numerator | Cell-level denominator |
|---|---|---|---|---|
| 1 | "Large" difference | $\bar X - \bar Y^{20}$ | `carried` $-$ `own20` | none |
| 2 | Carry-over ratio $\tau$ | $(\bar X - \mathrm{KL}_0)/(\bar Y - \mathrm{KL}_0)$ | `carried` $-$ `start` | `own` $-$ `start` |
| 3 | Shuffled ratio $\tau^{\mathrm{shuf}}$ | $(\bar X - \bar S)/(\bar Y - \bar S)$ | `carried` $- S_{ijs}$ | `own` $- S_{ijs}$ |
| 4 | Carried margin over shuffled copies | $\bar X - \bar S$ | `carried` $- S_{ijs}$ | none |
| 5 | Own search's margin over shuffled copies | $\bar Y - \bar S$ | `own` $- S_{ijs}$ | none |
| 6 | Composition share $\kappa$ | $(\bar X - \bar S)/(\bar X - \mathrm{KL}_0)$ | `carried` $- S_{ijs}$ | `carried` $-$ `start` |
| 7 | Shuffled copies against the yardstick | $\bar S - \bar Y^{20}$ | $S_{ijs} -$ `own20` | none |
| 8 | Carried-over added harm | $\bar X - \mathrm{KL}_0$ | `carried` $-$ `start` | none |
| 9 | Pooled retention of settings | $\sum(\bar X - \mathrm{KL}_0)\big/\sum(\text{attack own added})$ | `carried` $-$ `start` | `attack_own` $-$ `attack_start`, repeated over $j$ |

For each statistic the interval routine returns: the estimate; the **deciding interval** $[L, U]$, which is the signed $t$ interval times any widening recorded before the run; the unwidened signed interval; the percentile interval; and the standard error. Every verdict below is read from the deciding interval. One more number is derived: the own search's margin in standard errors, $z_D = (\bar Y - \bar S)/\mathrm{se}$, from statistic 5.

## 3. The Decision Logic

All comparisons are exact comparisons of the stored double-precision numbers, with no tolerance.

### 3.1 The Three Verdicts

Each is printed separately as `yes`, `no`, or `undetermined` (R1).

| Verdict | Statistic | `yes` | `no` | `undetermined` |
|---|---|---|---|---|
| Large | 1 | $L > 0$ | $U \le 0$ | $L \le 0 < U$ |
| Carries over | 2 | $L \ge 0.2$ | $U < 0.2$ | $L < 0.2 \le U$ |
| Depends on the choice | 3 | $L \ge 0.2$ | $U < 0.2$ | $L < 0.2 \le U$ |

These follow the plan's Section 6.6 wording: "above zero" and "at or below zero" for large; "at or above 0.2" and "below" for the two ratios.

### 3.2 The Four Shuffled Readings, and "No Reading Defined"

The shuffled ratio also gets one of the four signed readings, tested in this order on its deciding interval:

| Order | Condition | Reading | Verdict of 3.1 that goes with it |
|---|---|---|---|
| 1 | $L \ge 0.2$ | (a) At or above 0.2 | yes |
| 2 | $U \ge 0.2$ | (d) Straddles 0.2 | undetermined |
| 3 | $U < 0$ | none: print `no reading defined` (R4) | no |
| 4 | $L > 0$ | (b) Above zero, below 0.2 | no |
| 5 | otherwise | (c) Includes zero | no |

Testing (d) before (c) gives the signed precedence: a wide interval that includes both zero and 0.2 reads (d). In case 3 the three-way verdict is `no`, because the interval does lie below 0.2, which is the plan's literal condition; the script prints `no reading defined` in place of a sentence and raises flag F2.

### 3.3 The 20-Step Row

"Large" is not asked: the script prints `not asked at 20 steps`. The carry-over verdict is printed with the signed word for it: `yes` as "Carries over", `no` as "Batch-specific", `undetermined` as "Undetermined". The shuffled verdict and reading are as in 3.1 and 3.2. No step-table cell is printed.

### 3.4 The Step-Table Cell, From 40 Steps

"Large" is asked first at every search length from 40 steps (R1). The cell has a row state and a column state.

**Row state.**

| Large | Carries over | Row state |
|---|---|---|
| yes | yes | **Large** |
| yes | undetermined | **Large**, with flag F1b |
| yes | no | **Large**, with flag F1 |
| no | yes | **Not large, but carries over** |
| no | no | **Does not carry over** |
| no | undetermined | Unsettled between "Not large, but carries over" and "Does not carry over" |
| undetermined | yes | Unsettled between "Large" and "Not large, but carries over" |
| undetermined | no | Unsettled between "Large" and "Does not carry over" |
| undetermined | undetermined | Unsettled between all three |

**Column state.** Depends on the choice `yes` gives **Depends on the choice**; `no` gives **Does not depend on the choice**; `undetermined` gives unsettled.

**What is printed.**

| Row state | Column state | Printed |
|---|---|---|
| Large | Depends on the choice | Sentence C-LD |
| Large | Does not depend on the choice | Sentence C-LN |
| Not large, but carries over | Depends on the choice | Sentence C-ND |
| Not large, but carries over | Does not depend on the choice | Sentence C-NN |
| Does not carry over | Any, settled or not | Sentence C-X |
| Large, or Not large, but carries over | Unsettled | `Row: <row name>. Column undetermined at this search length.` |
| Unsettled | Settled | `Column: <column name>. Row undetermined between <the candidates>.` |
| Unsettled | Unsettled | `Undetermined at this search length.` |

This is the signed rule that a straddling interval "names only the part of the table it settles". No sentence is printed for a cell that is not fully settled, except C-X, which the signed table gives for either column.

### 3.5 Harm-Level Rows

The same three verdicts and the same shuffled reading are computed from the level's scored settings, by the interval specification's convention for missing searches. No step-table cell is printed; the signed rules define cell sentences for the step table only. Three additions:

- **The missing count decides first.** If more than 10 of the 80 attack searches, or more than 10 of the 80 held-out searches, are missing at the level, all three verdicts print `undetermined`, the shuffled reading prints `not read: level Undetermined`, and flag F10 is raised. Exactly 10 missing on a side is read normally; 11 is Undetermined. The row's numbers and intervals are still printed in full, computed from the available cells.
- **Each `yes` is tagged** `confirmatory`.
- **Each `no` is followed by the signed caveat,** verbatim: "Negative ones are reported with the bias of taking a setting at its first crossing stated: downward, of unknown size."

Flags F1 and F1b apply at harm levels as they do in the step table.

### 3.6 Steps 159 and 319

At 160 and 320 steps the row carries a sub-row for the setting after step $n - 1$. It holds statistics 1 and 2 and their two verdicts only, since those settings have no shuffled copies (R12). It is labelled `step n - 1: description; step n decides`. If either verdict differs from step $n$'s, flag F8 is raised on the main row.

### 3.7 The Signed Sentences

Printed exactly as below, including capitalization, with no closing full stop added.

| Code | Where | Sentence |
|---|---|---|
| a | Shuffled reading | The carried-over harm depends on which components the adversary chose, beyond how often they are needed |
| b | Shuffled reading | Mostly harm from extreme masks on components of that usage, whichever ones receive them, with a small part that depends on the choice; the exploited-components count is reported with that caveat |
| c | Shuffled reading | The harm comes from extreme masks on components of that usage, whichever ones receive them; the exploited-components count is dropped from the post |
| d | Shuffled reading | Undetermined between the first two readings; this takes precedence when a wide interval also includes zero |
| C-LD | Cell: large, depends | The search found a choice of components whose harm carries to text in general: by the paper's own test (lines 2019 to 2022), a systematic defect |
| C-LN | Cell: large, does not depend | A random permitted setting that switches off and on as many components at each level of usage also hurts unseen text; the search's particular choice is fitted to its batch |
| C-ND | Cell: not large but carries over, depends | The choice carries over, at no more harm on unseen text than the 20-step adversary does to its own batch |
| C-NN | Cell: not large but carries over, does not depend | The harm carries over through extreme masks on components of that usage, within the 20-step level |
| C-X | Cell: does not carry over | The search's harm is fitted to its batch: the case line 2022 describes as noise-tuned (either column) |

### 3.8 Flags

A flag is a fixed string printed on the row's flag line. None changes a verdict.

| Code | Raised when | Printed text |
|---|---|---|
| F1 | Large is `yes` and carries over is `no` | `large, with low retention` |
| F1b | Large is `yes` and carries over is `undetermined` | `large; carry-over ratio undetermined` |
| F2 | The shuffled ratio's interval has $U < 0$ | `no reading defined: the shuffled ratio's interval lies wholly below zero` |
| F3 | Statistic 5 has $L \le 0 < U$ | `the own search's margin over shuffled copies is not distinguishable from zero; the shuffled ratio is not reliable in this row; read the two margins` |
| F4 | Statistic 5 has $U \le 0$ | `shuffled copies do at least as much harm as the own search; the shuffled ratio's meaning is inverted in this row; read the two margins` |
| F5 | Statistic 4 has $U < 0$ | `carried-over settings do less harm than their shuffled copies` |
| F6 | Statistic 8 has $L \le 0$ | `carried-over added harm is not distinguishable from zero; composition share not defined` |
| F7 | Any verdict differs when read from the percentile interval | `percentile interval gives a different verdict for: <names>; the signed interval decides` |
| F8 | 160 and 320 steps: a verdict differs at step $n - 1$ | `step n - 1 gives a different verdict for: <names>; step n decides` |
| F9 | Any verdict differs in the recomputation without the 11 overlapping texts | `recomputation without the 11 overlapping texts gives a different verdict for: <names>; the main reading decides` |
| F10 | A harm level exceeds its missing allowance | `level Undetermined: <a> of 80 attack searches and <b> of 80 held-out searches missing; allowance 10 per side` |
| F11 | A widening multiplier above 1 was recorded for this row | `interval widened by <multiplier> under the pre-run amendment`, and, if any verdict differs under the unwidened interval, `; unwidened interval gives a different verdict for: <names>` |

## 4. The Printed Row

### 4.1 Lines, in Order

Every row prints the lines below in this order. "Interval" means the deciding interval, printed in square brackets after its estimate.

| Line | Content | Step rows | Harm-level rows |
|---|---|---|---|
| 0 | Header | `STEP TABLE: <n> steps` | `HARM-LEVEL TABLE: settings taken where each search's own harm first reaches <h> nats` |
| 1 | Counts | Attack batches, held-out batches, starts, carried-over cells, own-search cells | The same, then missing searches per side against the allowance of 10 |
| 2 | Mean raw harm on held-out batches, in this order: start; shuffled copies; carried over; own search; own 20-step search (the yardstick) | The yardstick is omitted at 20 steps, where it is the own search | As step rows, then the median and maximum own harm of the level's scored settings, per side |
| 2b | Attack side on its own batches: mean start harm and mean own-search harm | Yes | Yes |
| 3 | Large: statistic 1 with interval; verdict | `not asked at 20 steps` in the 20-step row | Verdict with its tag or caveat |
| 4 | Carries over: statistic 2 with interval; its two added harms; verdict | With the signed word at 20 steps | Verdict with its tag or caveat |
| 5 | Depends on the choice: statistic 3 with interval; verdict; then the signed reading's sentence on its own line | Yes | Verdict with its tag or caveat; sentence |
| 6a | Carried margin over shuffled copies: statistic 4 with interval | Yes | Yes |
| 6b | Description sentence D2 (own search's margin, statistic 5, with $z_D$) | Yes | Yes |
| 6c | Description sentence D1 (composition), then $\kappa$ with interval | Yes | Yes |
| 6d | Description sentence D3 (shuffled copies against the yardstick, statistic 7) | From 40 steps | Yes |
| 7 | Step-table cell, by Section 3.4 | From 40 steps | Not printed |
| 8 | Flags, or `none` | Yes | Yes |
| 9 | Each setting against itself: retention, by Section 4.3 | Split by whether own harm has passed 5 nats | Not split |
| 10 | Share of searches past 2, 5, and 10 nats by this step, per side; share of cycling settings, per side | Yes | Not printed |
| 11 | Shuffle: mean `moved_share` and mean `mean_abs_change` over the row's settings | Yes | Yes |
| 12 | For statistics 1 to 3: the percentile interval, the unwidened interval, the start term's share of the variance, and the degrees of freedom | Yes | Yes |
| 13 | Sub-row for step $n - 1$, by Section 3.6 | 160 and 320 steps | Not printed |

A harm-level row never prints a step count, in any line. The signed rules require that table to be worded by own-batch harm.

### 4.2 The Three Description Sentences

These are printed in every row where they apply, whatever the numbers show. Printing them always, and not only when something looks wrong, is what keeps them free of any threshold.

**D1, composition.** With $a = \bar X - \mathrm{KL}_0$, $b = \bar S - \mathrm{KL}_0$, and $c = \bar X - \bar S$:

> Of the carried-over added harm of $a$ nats, shuffled copies reproduce $b$ nats ($100(1 - \kappa)$ percent) and do not reproduce $c$ nats ($100\kappa$ percent).

The numbers are printed as they are, with no clipping, even when negative or above 100. When flag F6 is raised, D1 and $\kappa$ are replaced by F6's text.

**D2, the own search's margin.**

> The own search beats its shuffled copies by $\bar Y - \bar S$ nats [interval], $z_D$ standard errors from zero.

**D3, shuffled copies against the yardstick.** From statistic 7's interval: "exceed" if $L > 0$, "do not exceed" if $U \le 0$, and "are not distinguishable from" otherwise.

> Shuffled copies do $\bar S$ nats against a 20-step yardstick of $\bar Y^{20}$ nats: they \<exceed | do not exceed | are not distinguishable from\> the yardstick.

D3 exists because sentence C-LN, "A random permitted setting … also hurts unseen text", presupposes that shuffled copies are themselves large, and the signed rules do not check it.

### 4.3 Retention

For each scored attack setting $(i, s)$ in the row, retention is its carried-over added harm, averaged over held-out batches, divided by its added harm on its own batch:

$$
\rho_{is} = \frac{\frac{1}{K}\sum_j \left(\texttt{carried}_{ijs} - \texttt{start}_{js}\right)}{\texttt{attack\_own}_{is} - \texttt{attack\_start}_{is}}.
$$

A step row prints, for the settings whose search has passed 5 nats by this step and for those whose search has not: the number of settings; the pooled retention, which is the sum of numerators over the sum of denominators; the median; and the 10th and 90th percentiles. It then prints the pooled retention over all settings with its interval (statistic 9). A harm-level row prints one unsplit group and the pooled value with its interval.

Retention compares a setting with itself, so the timing of breakouts cancels within it. It is description: it never resolves a verdict.

### 4.4 Worked Example: A Benign Row

The numbers are invented, for layout only.

```
STEP TABLE: 80 steps
 1  Cells: 16 attack x 16 held-out batches x 5 starts; 1280 carried-over cells, 80 own-search cells
 2  Mean harm on held-out batches (raw nats):
      start 0.21 | shuffled copies 0.40 | carried over 7.60 | own search 9.50 | own 20-step search (yardstick) 0.78
 2b Attack side on its own batches: start 0.21 | own search 9.62
 3  Large: carried over - yardstick = +6.82 [4.90, 8.74]                              yes
 4  Carries over: ratio 0.80 [0.61, 0.99]  (added harm 7.39 over 9.29)                yes
 5  Depends on the choice: shuffled ratio 0.79 [0.60, 0.98]                           yes
      "The carried-over harm depends on which components the adversary chose, beyond how often they are needed"
 6a Carried over - shuffled copies = +7.20 [5.30, 9.10] nats
 6b The own search beats its shuffled copies by 9.10 nats [7.40, 10.80], 11.4 standard errors from zero.
 6c Of the carried-over added harm of 7.39 nats, shuffled copies reproduce 0.19 nats (3 percent) and do not
    reproduce 7.20 nats (97 percent).  Composition share 0.97 [0.96, 0.98]
 6d Shuffled copies do 0.40 nats against a 20-step yardstick of 0.78 nats: they do not exceed the yardstick.
 7  Step-table cell: Large x Depends on the choice
      "The search found a choice of components whose harm carries to text in general: by the paper's own
       test (lines 2019 to 2022), a systematic defect"
 8  Flags: none
 9  Each setting against itself (carried-over added harm / added harm on its own batch):
      own harm past 5 nats      46 settings | pooled 0.83 | median 0.84 | 10th to 90th percentile 0.70 to 0.93
      own harm not past 5 nats  34 settings | pooled 0.52 | median 0.50 | 10th to 90th percentile 0.31 to 0.72
      all 80 settings           pooled 0.80 [0.74, 0.86]
10  Searches past 2 / 5 / 10 nats by this step: attack 0.96 / 0.58 / 0.44; held-out 0.95 / 0.55 / 0.41
    Cycling settings: attack 0.05; held-out 0.04
11  Shuffle: a shuffled copy moves 41 percent of alive entries by more than 0.5; mean absolute change 0.43
12  Percentile intervals: large [4.7, 8.9]; carries over [0.60, 1.02]; depends [0.59, 1.01]
    Unwidened: identical (no widening recorded). Start term's share of variance: 0.08, 0.11, 0.11. Degrees of freedom: 14.2, 12.9, 12.9
```

### 4.5 Worked Example: Case A, Where the Verdict Words Alone Would Mislead

Carried harm 3.0, shuffled 0.5, own search 25.0, at 320 steps (case R2 of Section 5.2). Lines 3 to 8 read:

```
 3  Large: carried over - yardstick = +2.22 [...]                                     yes
 4  Carries over: ratio 0.11 [...]  (added harm 2.79 over 24.79)                      no
 5  Depends on the choice: shuffled ratio 0.10 [...]                                  no
      "Mostly harm from extreme masks on components of that usage, whichever ones receive them, with a small
       part that depends on the choice; the exploited-components count is reported with that caveat"
 6a Carried over - shuffled copies = +2.50 [...] nats
 6b The own search beats its shuffled copies by 24.50 nats [...], ... standard errors from zero.
 6c Of the carried-over added harm of 2.79 nats, shuffled copies reproduce 0.29 nats (10 percent) and do not
    reproduce 2.50 nats (90 percent).  Composition share 0.90 [...]
 6d Shuffled copies do 0.50 nats against a 20-step yardstick of 0.78 nats: they do not exceed the yardstick.
 7  Step-table cell: Large x Does not depend on the choice
      "A random permitted setting that switches off and on as many components at each level of usage also
       hurts unseen text; the search's particular choice is fitted to its batch"
 8  Flags: large, with low retention
```

The signed sentences stand as written. A reader of the row sees beside them that shuffled copies reproduce a tenth of the carried harm and do not exceed the yardstick. In case D (R6), lines 6b and 8 carry the correction: the margin is negative, and flags F4 and F5 say so.

### 4.6 Headers and Footers

**Once, above the step table:**
- the provenance the signed rules require (commit, clean tree, GPU, environment, seed keys);
- per side, each batch's mean own-search added harm at 20 steps, sorted, so a reader can see whether any batch breaks out early; and the count of early-breakout batches per side, by whatever definition the interval specification fixes (E4).

**Under the step table,** verbatim from the signed rules: "A straddling 40- or 80-step cell stays Undetermined, and nothing outside the step table resolves it."

**Under the harm-level table,** two fixed lines built from the signed rules' words: `Only positive verdicts are confirmatory.` and `The harm-level table is printed in full and never resolves a step-table cell.`

**A second copy of both tables** is computed without the 11 overlapping held-out texts and printed after the main copy under its own header. The main copy decides; flag F9 on a main row marks any difference in verdict.

### 4.7 The Machine-Readable Form

The script writes every row as a record in one JSON file and builds the printed text from that file alone. Tests assert on the record, not on formatted text. Each record holds at least:

- `table` (`step` or `level`) and `key` (the search length or the level);
- `counts`, `means_raw`, and `attack_side`;
- `large`, `carries`, `depends`: each with `estimate`, `interval`, `interval_unwidened`, `interval_percentile`, `verdict`; `carries` also holds `word` at 20 steps; `depends` also holds `reading` (`a`, `b`, `c`, `d`, `none`, or `not read`) and `sentence`;
- `carried_margin`, `own_margin` (with `z`), `kappa` (with `defined`), `shuffled_vs_yardstick` (with `relation`);
- `cell`: `row_state`, `column_state`, `sentence_code`, `printed`;
- `flags`: the list of codes;
- `retention`, `past_levels`, `cycling`, `shuffle_moved`;
- `step_before`, at 160 and 320 steps.

Numbers are stored at full precision. In print, harms and differences take two decimals, ratios two decimals, and $z_D$ one.

## 5. Known-Answer Cases

There are two layers. The first tests the decision function alone, on intervals typed in by hand, because a boundary cannot be hit reliably through noise. The second runs the row function on made-up cell arrays.

### 5.1 Layer One: The Decision Function on Given Intervals

**Boundaries.** Each line gives an interval and the expected output.

| # | Statistic | Interval $[L, U]$ | Expected |
|---|---|---|---|
| B1 | Large | $[0.01, 2]$ | yes |
| B2 | Large | $[0, 2]$ | undetermined |
| B3 | Large | $[-2, 0]$ | no |
| B4 | Large | $[-2, 0.01]$ | undetermined |
| B5 | Carries over | $[0.2, 0.9]$ | yes |
| B6 | Carries over | $[0.19, 0.9]$ | undetermined |
| B7 | Carries over | $[0.05, 0.2]$ | undetermined |
| B8 | Carries over | $[0.05, 0.19]$ | no |
| B9 | Shuffled ratio | $[0.2, 0.5]$ | reading a; yes |
| B10 | Shuffled ratio | $[0.05, 0.19]$ | reading b; no |
| B11 | Shuffled ratio | $[0.1, 0.2]$ | reading d; undetermined |
| B12 | Shuffled ratio | $[-0.05, 0.19]$ | reading c; no |
| B13 | Shuffled ratio | $[-0.05, 0.3]$ | reading d; undetermined |
| B14 | Shuffled ratio | $[0, 0.1]$ | reading c; no |
| B15 | Shuffled ratio | $[-0.3, 0]$ | reading c; no |
| B16 | Shuffled ratio | $[-0.3, -0.1]$ | `no reading defined`; no; flag F2 |

**The cell.** A test enumerates all 27 combinations of the three verdicts and checks the printed cell against the tables of Section 3.4, and checks that F1 is raised exactly for (yes, no, any) and F1b exactly for (yes, undetermined, any).

**Tie-breaks.** Given a deciding interval and a percentile interval that give different verdicts, the deciding one is printed and F7 names the verdict. The same for an unwidened interval and F11, and for a recomputed row and F9.

### 5.2 Layer Two: Row Cases on Made-Up Cells

**The recipe.** Unless a case says otherwise: 16 attack batches, 16 held-out batches, 5 starts, 8 shuffled copies; `start` 0.21 and `own20` 0.78; `attack_start` equal to the start mean and `attack_own` equal to the `own` mean; every array equals its stated mean times $(1 + 0.002\,u)$, with $u$ an independent standard normal draw per entry from a generator seeded with the case number. That noise keeps every interval within about 1 percent of its estimate. A **held-out pattern** of size $\delta$ replaces the noise on `own` by adding $\delta(-1)^j$ to held-out batch $j$, which gives a large, exactly balanced batch effect.

**Tolerances.** Verdicts, readings, cell output, and flags must match exactly. Estimates must match within 0.02, or within 1 percent if larger, unless a case states otherwise.

| Case | Row | `own` | `carried` | `shuffled` | Large | Carries over ($\tau$) | Depends ($\tau^{\mathrm{shuf}}$) and reading | Cell or word | Flags | Also check |
|---|---|---|---|---|---|---|---|---|---|---|
| R1. Benign | 320 | 25.5 | 23.0 | 0.43 | yes (+22.22) | yes (0.90) | yes (0.90), a | C-LD | none | $\kappa = 0.99$; D3 "do not exceed" |
| R2. Low retention of a very large harm | 320 | 25.0 | 3.0 | 0.5 | yes (+2.22) | no (0.11) | no (0.10), b | C-LN | F1 | $\kappa = 0.90$; D3 "do not exceed" |
| R3. High generic share | 20 | 0.78 | 0.70 | 0.62 | not asked | yes (0.86) | yes (0.50), a | "Carries over" | none | $\kappa = 0.16$ |
| R4. Shuffled copies as harmful as the own search, tight | 20 | 0.78 | 0.74 | 0.76 | not asked | yes (0.93) | no ($-1.0$, tolerance 0.05), none | "Carries over" | F2, F5 | Own margin $+0.02$, interval above zero |
| R5. The same with a held-out pattern, $\delta = 0.2$ | 20 | 0.78 | 0.74 | 0.76 | not asked | yes (0.93) | undetermined ($-1.0$, tolerance 0.05), d | "Carries over" | F3, F5 | Own margin's interval includes zero; $\lvert z_D \rvert < 1$ |
| R6. Shuffled copies more harmful than the own search | 40 | 0.80 | 0.70 | 1.00 | no ($-0.08$) | yes (0.83) | yes (1.50), a | C-ND | F4, F5 | $\kappa = -0.61$; D3 "exceed" |
| R7. Carried below its shuffled copies | 40 | 0.80 | 0.25 | 0.40 | no ($-0.53$) | no (0.07) | no ($-0.38$), none | C-X | F2, F5 | $\kappa = -3.75$, tolerance 0.1 |
| R8. Large, ratio straddling; held-out pattern, $\delta = 8$ | 320 | 25.0 | 5.168 | 0.43 | yes (+4.39) | undetermined (0.200) | undetermined (0.19), d | `Row: Large. Column undetermined at this search length.` | F1b | No sentence printed |
| R9. Not large, carries over, small choice-dependent part | 40 | 0.80 | 0.60 | 0.58 | no ($-0.18$) | yes (0.66) | no (0.09), b | C-NN | none | $\kappa = 0.05$ |
| R10. Every shuffled copy equals its setting | 40 | 0.80 | 0.60 | equal to `carried`, cell by cell | no | yes (0.66) | no (exactly 0, interval $[0, 0]$), c | C-NN | none | Zero variance must not give 0/0 |
| R11. The plan's worked example, no noise at all | 20 | 0.83 | 0.70 | 0.60 | not asked | yes (0.78) | yes (0.43), a | "Carries over" | none | `start` 0.24; $\kappa = 0.22$; all intervals of zero width |
| R12. Harms that depend on the start | 320 | $s + 10$ | $s + 6$ | $s + 0.2$ | yes (+5.50) | yes (0.60) | yes (0.59), a | C-LD | none | `start` $= s$, `own20` $= s + 0.5$; $\kappa = 0.97$ |
| R13. One denominator cell near zero | 320 | 10.21, except 0.22 at $j = 1, s = 1$ | 6.21 | 0.43 | yes | yes (0.608, tolerance 0.005) | yes (0.60), a | C-LD | none | A mean of ratios would give about 8 |
| R14. A search that jumps past the level | level 2 | 40.0 | 36.0 | 0.43 | yes, confirmatory | yes (0.90), confirmatory | yes (0.90), a | none printed | none | Line 2 shows median own harm 40.0 per side; using the level as denominator would give 20 |
| R15a. Ten attack searches missing | level 10 | 10.8 | 8.48 | 0.41 | yes | yes (0.78) | yes (0.78), a | none printed | none | Missing: attack batches 1 and 2 at all five starts |
| R15b. Eleven attack searches missing | level 10 | 10.8 | 8.48 | 0.41 | undetermined | undetermined | undetermined, `not read` | none printed | F10 | Add batch 3 at start 1; numbers still printed |
| R15c. Eleven held-out searches missing | level 10 | 10.8 | 8.48 | 0.41 | undetermined | undetermined | undetermined, `not read` | none printed | F10 | The same pattern on the held-out side |
| R16. Mixture of broken-out and other settings | 80 | see below | see below | 0.40 | yes | yes (0.675) | yes (0.67), a | C-LD | none | Retention split, below |
| R17. Step 319 disagrees | 320 | 25.5; at step 319, 25.0 | 23.0; at step 319, 3.0 | 0.43 | yes | yes (0.90) | yes (0.90), a | C-LD | F8 | Sub-row: large yes, carries over no |

**Case R16 in full.** Attack search $(i, s)$ is "broken out" when $(i + s) \bmod 5 = 0$, with $i$ from 1 to 16 and $s$ from 1 to 5: 16 of the 80 searches, one per batch. Held-out search $(j, s)$ likewise when $(j + s) \bmod 5 = 0$.

| Search | `attack_own` or `own` | `carried` from it | `attack_past` or `heldout_past` at 5 nats |
|---|---|---|---|
| Broken out | 20.21 | 18.21 | true |
| Not broken out | 3.21 | 1.11 | false |

Expected: carry-over ratio $(0.2 \times 18 + 0.8 \times 0.9)/(0.2 \times 20 + 0.8 \times 3) = 4.32/6.40 = 0.675$. Retention: 16 settings past 5 nats with pooled value and median 0.90; 64 settings not past with pooled value and median 0.30; all 80 pooled at 0.675. Share past 5 nats: 0.20 on each side. The pooled ratio reads "carries over" at 0.675 while four settings in five keep 0.30, and the row must show both.

**Where these cases come from.** R2 to R7 are cases A to E of the shuffled-ratio analysis (research log), and R2 and R8 are the review's collision case. R3 stands for its case 2A. R14 covers one review's item 10 and another's items 4.3 and 4.4 (research log). R10 to R13 are that review's items 4.4 to 4.8. R15 is its item 4.10 with the review's batch-clustered missing searches. R17 is review item 9. Coverage under realistic noise, the digits table, and the transposition checks belong to the interval and table specifications and are not repeated here.

## 6. The Delta-On Run's Printed Summary

The delta-on run repeats searches with the 24 delta entries held at 1, on attack batches A1 to A8, held-out batches H1 to H8, and starts 9 to 13. It has no signed line, so its summary carries **no verdict word** (R11). It prints one block per search length, computed on those 8 by 8 by 5 cells for both runs, so that every delta-on cell has its exact counterpart in the lead.

| Line | Content |
|---|---|
| 1 | Lead, on the matched cells, mean raw harm: start; shuffled copies; carried over; own search |
| 2 | Delta-on, mean raw harm in the same order. Its start harm is that of the starting point with the delta entries at 1 |
| 3 | Carry-over ratio with interval: lead on the matched cells; delta-on |
| 4 | Shuffled ratio with interval: lead on the matched cells; delta-on |
| 5 | Share of carried-over harm remaining: delta-on carried-over added harm over the lead's, with interval |
| 6 | Share of own-search harm remaining: delta-on own-search added harm over the lead's, with interval |
| 7 | The range of line 5's share when the delta components do nothing, from the made-up-data test |
| 8 | The fixed caution below |

**Line 5** is a ratio of means over paired cells: the numerator cell is the delta-on `carried` minus the delta-on `start`, the denominator cell the lead's `carried` minus the lead's `start`, for the same $(i, j, s)$. Its interval is the signed rule with 8 batches per side. **Line 6** is the same with `own` in place of `carried`, each $(j, s)$ value repeated over $i$.

**Line 8, printed always:**

> The delta-on searches follow different paths from the lead's, so a share differs from 1 by chance. Compare it with the range on line 7 before reading it as the delta components' contribution.

The script reads line 7's range from the committed report of the made-up-data test and refuses to print the summary without it. Line 4 is there because shuffled copies leave the delta entries in place: if shuffled copies did much less harm in the delta-on run than in the lead, the lead's shuffled harm would be coming from the delta entries.

## 7. Signed Descriptions That Are Not Rows

So that nothing in the signed rules' Section 8 is lost, the script also writes:

- **The scatter's data:** for every scored setting, its carried-over added harm averaged over held-out batches and its added harm on its own batch, marked by search length or harm level. Whether the 80-step settings lie on the harm-level curve is a judgement made from this file.
- **Long-search levels as a distribution:** over all 160 lead searches, the mean harm over steps 301 to 320, with its minimum, quartiles, and maximum, and the share of searches at or above the paper's 40.2 after step 320.

The share of searches past each level, the share of cycling settings, and the step $n - 1$ readings are in the rows (lines 10 and 13).

## 8. Choices Made Here That the Draft Leaves Open

Each was put for confirmation before the specification bound; where Amendment 1 differs, Amendment 1 governs (its Section 9).

1. **R2 is narrowed.** The draft prints "large, with low retention" when the ratio's interval lies below or straddles 0.2. A straddling interval does not show low retention, so this note prints that phrase only when the interval lies below (F1), and "large; carry-over ratio undetermined" when it straddles (F1b).
2. **R4 needs a three-way verdict.** With the shuffled interval wholly below zero, the reading is `no reading defined`, and "depends on the choice" is `no`, since the interval lies below 0.2 as the plan's wording requires. The alternative, leaving the column unsettled, would be the script choosing against the literal rule.
3. **The composition share needs its own guard.** $\kappa$ divides by the carried-over added harm, which is near zero exactly when nothing carries over. Flag F6 withholds it there.
4. **A harm level made Undetermined still prints its numbers.** Its verdict words are all `undetermined`. Suppressing the numbers would contradict "printed in full".
5. **Three sentences are printed always, in place of warnings that fire at a threshold.** D1 to D3 put the composition, the own search's margin, and the yardstick comparison in words in every row. A warning triggered by, say, $\kappa$ above one half would have been a new line.
6. **Two additions beyond the draft.** Line 2b shows the attack side's own-search harm, so a reader can see when one side has broken out more than the other. Line 9 gives the pooled retention an interval (statistic 9). Both are description. The second deserves a deliberate yes or no: it is likely the steadiest number at 40 and 80 steps, and for that reason it could tempt a reader to resolve an undetermined cell with it, which the signed rules forbid.
7. **What this note needs from the others.** From the table specification's table: `attack_own` and `attack_start` for every scored setting, and the two shuffle-displacement numbers per setting, over alive entries. From the interval specification's routine: intervals for all nine statistics of Section 2.2, including plain differences and the ratio whose denominator varies with the attack batch.
