# The Interval Code and Its Made-Up-Data Test: Binding Specification

Daniel, session 5, round 2. Written before any deciding run, for the engineer.

## 1. Purpose and Scope

The lead experiment scores settings found by an adversary on 16 attack batches against 16 held-out batches, from 5 shared starting points. Every verdict in the post is read from an error bar ("interval") on a mean or a ratio of means over that table. The signed rules, `sessions/004/freeze_file_part1_q2.md`, Section 5, define the interval but leave several computational choices open. This note fixes them, so that the analysis script and its test can be written without further discussion. It has four parts:

1. the interval, step by step, for six statistics (Sections 2 to 4);
2. what to compute when some searches never reach a harm level (Section 5);
3. the generator of made-up experiments and the fixed list of scenarios (Sections 6 and 7);
4. the pass criterion, the repair, and what the test report prints (Sections 8 and 9).

Section 10 lists where I differ from Ines's draft, `sessions/005/prerun_decisions_draft_1.md`. This note does not define the verdict words; those are the signed rules' Section 4 and the draft's R1 to R8. It supersedes the generator in my round 1 note, `sessions/005/notes/daniel/interval_stress_test_design.md`.

## 2. Inputs and Notation

**Design.** $K$ batches per side ($K = 16$ in the lead, 8 in the delta-on run), indexed $i$ for attack batches and $j$ for held-out batches; $n_s = 5$ starts, indexed $s$. A **row** is one line of a table: a search length $n \in \{20, 40, 80, 160, 320\}$ or a harm level $h \in \{2, 5, 10\}$ nats.

**Raw harms at one row**, all per-token KL divergence in nats:

| Symbol | Meaning | In the draft |
|---|---|---|
| $x_{ijs}$ | harm on held-out batch $j$ of the setting found on attack batch $i$ from start $s$ | $X$ |
| $z_{ijs}$ | mean harm on held-out batch $j$ of that setting's 8 shuffled copies | $S$ |
| $y_{js}$ | harm on held-out batch $j$ of its own search's setting from start $s$ | $Y$ |
| $k_{js}$ | harm on held-out batch $j$ of the random starting point $s$ | $\mathrm{KL}_0$ |
| $q_{js}$ | harm on held-out batch $j$ of its own search after 20 steps from start $s$ | $Y^{20}$ |

**Presence.** $a_{is} = 1$ if attack search $(i, s)$ has a setting at this row, else 0; $b_{js}$ likewise for held-out search $(j, s)$. At a search-length row every search has a setting, so all are 1. At a harm level a search that never reaches the level has none. $x_{ijs}$ and $z_{ijs}$ exist when $a_{is} = 1$; $y_{js}$ exists when $b_{js} = 1$; $k_{js}$ and $q_{js}$ always exist.

**Two kinds of mean.** Every statistic is built from means of two kinds:

$$
M_A[f] = \frac{1}{C_A}\sum_{i,j,s} a_{is}\, f_{ijs}, \quad C_A = K\sum_{i,s} a_{is}; \qquad M_H[g] = \frac{1}{C_H}\sum_{j,s} b_{js}\, g_{js}, \quad C_H = \sum_{j,s} b_{js}.
$$

$M_A$ averages a quantity $f$ over every cell whose attack search has a setting, across all $K$ held-out batches. $M_H$ averages a quantity $g$ over every held-out search that has a setting. With nothing missing, $C_A = K^2 n_s$ and $C_H = K n_s$, and these are the plain means of the signed rules.

## 3. The Six Statistics

| Statistic | Definition | Kind |
|---|---|---|
| Carry-over ratio $\tau$ | $M_A[x - k] \,/\, M_H[y - k]$ | ratio |
| Shuffled ratio $\tau^{\mathrm{shuf}}$ | $M_A[x - z] \,/\, (M_H[y] - M_A[z])$ | ratio |
| Composition share $\kappa$ | $M_A[x - z] \,/\, M_A[x - k]$ | ratio |
| "Large" difference | $M_A[x - q]$ | mean |
| Carried minus shuffled, $\bar X - \bar S$ | $M_A[x - z]$ | mean |
| Own minus shuffled, $\bar Y - \bar S$ | $M_H[y] - M_A[z]$ | mean |

With a complete table these equal the signed definitions: $\tau = (\bar X - \mathrm{KL}_0)/(\bar Y - \mathrm{KL}_0)$ and $\tau^{\mathrm{shuf}} = (\bar X - \bar S)/(\bar Y - \bar S)$. The delta-on run's paired share (draft R11) is a seventh statistic of the same form: $M_A[x^{\Delta} - k^{\Delta}] / M_A[x - k]$ over the 8 by 8 by 5 cells the two runs share, where the superscript marks the delta-on run.

For a ratio, write $\hat\theta = \hat N / \hat D$ for its value, numerator, and denominator.

## 4. The Interval, Step by Step

This section assumes a complete table, which every search-length row has. Section 5 gives the general form, which reduces to this one.

### 4.1 The Linearized Cell

A ratio of means is not a mean, so its variance is found by the standard linearization: near the estimate, $\hat\theta$ moves like the mean of the cells

$$
W_{ijs} = \frac{N_{ijs} - \hat\theta\, D_{ijs}}{\hat D},
$$

where $N_{ijs}$ and $D_{ijs}$ are the per-cell numerator and denominator. $\hat\theta$ and $\hat D$ are computed once from the whole table and held fixed. For a plain mean, $W_{ijs}$ is the cell's own value.

| Statistic | $N_{ijs}$ | $D_{ijs}$ | $W_{ijs}$ |
|---|---|---|---|
| $\tau$ | $x_{ijs} - k_{js}$ | $y_{js} - k_{js}$ | $(N - \hat\tau D)/\hat D$ |
| $\tau^{\mathrm{shuf}}$ | $x_{ijs} - z_{ijs}$ | $y_{js} - z_{ijs}$ | $(N - \hat\tau^{\mathrm{shuf}} D)/\hat D$ |
| $\kappa$ | $x_{ijs} - z_{ijs}$ | $x_{ijs} - k_{js}$ | $(N - \hat\kappa D)/\hat D$ |
| "Large" | | | $x_{ijs} - q_{js}$ |
| $\bar X - \bar S$ | | | $x_{ijs} - z_{ijs}$ |
| $\bar Y - \bar S$ | | | $y_{js} - z_{ijs}$ |

**The shuffled ratio uses each cell's own shuffled harm $z_{ijs}$, never the grand mean $\bar S$.** The point estimate is the same either way; the variance is not. Example: two held-out batches, one half as easy to harm as average and one half again as easy, so that carried, own, and shuffled harms are $0.5 \times (0.70, 0.83, 0.60)$ on the first and $1.5 \times (0.70, 0.83, 0.60)$ on the second. The ratio is $0.10/0.23 = 0.435$ on each batch. The per-cell form gives $W = 0$ on both, correctly reporting no variation between held-out batches. Subtracting the grand mean 0.60 instead gives $W = -0.74$ and $+0.74$, a large spurious variance.

### 4.2 The Batch Part

1. **Average over starts:** $\bar W_{ij} = \frac{1}{n_s}\sum_s W_{ijs}$, a $K$ by $K$ table.
2. **Resample.** For each of $B = 10{,}000$ replicates draw $K$ attack indices and, independently, $K$ held-out indices, each uniformly with replacement from $1..K$. The replicate's value is the mean of the $K^2$ entries $\bar W_{r c}$ over the drawn attack indices $r$ and held-out indices $c$.
3. **Variance:** $\mathrm{SE}^{*2}$ is the sample variance of the $B$ replicate values, and $V_{\mathrm{PB}} = \frac{K}{K-1}\,\mathrm{SE}^{*2}$.

**Each replicate averages the linearized cells; it does not recompute the ratio.** Three reasons. The start part (Section 4.3) is defined on linearized cells, so both parts then describe the same quantity in the same units. A replicate whose denominator comes near zero cannot blow the variance up. And the bootstrap variance of a table mean has an exact closed form, which checks the code on every statistic and every row:

$$
V_{\mathrm{closed}} = \frac{1}{K^2}\sum_i \alpha_i^2 + \frac{1}{K^2}\sum_j \beta_j^2 + \frac{1}{K^4}\sum_{i,j}\gamma_{ij}^2,
$$

with row effects $\alpha_i = \bar W_{i\bullet} - \bar W$, column effects $\beta_j = \bar W_{\bullet j} - \bar W$, and residuals $\gamma_{ij} = \bar W_{ij} - \bar W_{i\bullet} - \bar W_{\bullet j} + \bar W$, where $\bar W_{i\bullet}$, $\bar W_{\bullet j}$, and $\bar W$ are the row, column, and grand means of the table. This is Owen's Theorem 2 [`literature/text_only/owen2007_pigeonhole_bootstrap.md`] for a complete table, rearranged; I checked it against a direct derivation and against the enumeration in Section 4.7.

**Check in the script:** print $\mathrm{SE}^{*2}/V_{\mathrm{closed}}$ for every interval and raise an error if it is outside 0.90 to 1.10. At $B = 10{,}000$ its Monte Carlo standard error is about 1.4 percent.

**Indices and seeds.** Draw the $B \times K$ attack indices and $B \times K$ held-out indices once per value of $K$ from one seeded generator, and reuse them for every row and statistic. Save the seed, a hash of the index arrays, and each statistic's $B$ replicate values.

### 4.3 The Start Part

A three-way analysis of variance of the cells $W_{ijs}$, written here for $K_A$ attack batches and $K_H$ held-out batches so that Section 5 can reuse it; in a complete table $K_A = K_H = K$. A bar with a bullet is a mean over the bulleted index.

$$
\begin{aligned}
\mathrm{MS}_S &= \frac{K_A K_H}{n_s - 1}\sum_s\left(\bar W_{\bullet\bullet s} - \bar W\right)^2,\\
\mathrm{MS}_{AS} &= \frac{K_H}{(K_A - 1)(n_s - 1)}\sum_{i,s}\left(\bar W_{i\bullet s} - \bar W_{i\bullet\bullet} - \bar W_{\bullet\bullet s} + \bar W\right)^2,\\
\mathrm{MS}_{BS} &= \frac{K_A}{(K_H - 1)(n_s - 1)}\sum_{j,s}\left(\bar W_{\bullet js} - \bar W_{\bullet j\bullet} - \bar W_{\bullet\bullet s} + \bar W\right)^2,\\
\mathrm{MS}_{ABS} &= \frac{1}{(K_A - 1)(K_H - 1)(n_s - 1)}\sum_{i,j,s}\left(W_{ijs} - \bar W_{ij\bullet} - \bar W_{i\bullet s} - \bar W_{\bullet js} + \bar W_{i\bullet\bullet} + \bar W_{\bullet j\bullet} + \bar W_{\bullet\bullet s} - \bar W\right)^2.
\end{aligned}
$$

Then, with $u = \mathrm{MS}_S - \mathrm{MS}_{AS} - \mathrm{MS}_{BS} + \mathrm{MS}_{ABS}$,

$$
\hat\sigma^2_c = \max\!\left(0, \frac{u}{K_A K_H}\right), \qquad V_c = \frac{\hat\sigma^2_c}{n_s}, \qquad \nu_c = \frac{u^2}{\dfrac{\mathrm{MS}_S^2}{n_s - 1} + \dfrac{\mathrm{MS}_{AS}^2}{(K_A-1)(n_s-1)} + \dfrac{\mathrm{MS}_{BS}^2}{(K_H-1)(n_s-1)} + \dfrac{\mathrm{MS}_{ABS}^2}{(K_A-1)(K_H-1)(n_s-1)}},
$$

with $\nu_c$ bounded to $[1, n_s - 1]$. $\nu_c$ is computed only when $u > 0$.

### 4.4 Degrees of Freedom and the Interval

- If $V_c = 0$: $\nu = K - 1$. This is the limit of the general formula, and it avoids a 0/0 when every mean square is zero.
- Otherwise: $\nu = (V_{\mathrm{PB}} + V_c)^2 \big/ \left(V_{\mathrm{PB}}^2/(K-1) + V_c^2/\nu_c\right)$.

The interval is

$$
\hat\theta \pm \lambda_r\, t_{0.975,\nu}\sqrt{V_{\mathrm{PB}} + V_c},
$$

with the $t$ quantile at non-integer $\nu$ (for example `scipy.stats.t.ppf(0.975, nu)`), and $\lambda_r$ the row's multiplier from Section 8, equal to 1 unless the test sets it. The script prints both the unwidened interval ($\lambda_r = 1$) and the widened one. $K$ here is always the full number of batches per side.

**Degenerate inputs.** If $\hat D = 0$ the ratio and its interval are printed as undefined. If $V_{\mathrm{PB}} + V_c = 0$ the half-width is zero and the output carries the flag `zero_variance`.

### 4.5 What Else Is Printed Beside Every Interval

- **The percentile interval:** the 2.5th and 97.5th percentiles of the statistic **recomputed** in each of the same $B$ replicates (for a ratio, the resampled numerator mean over the resampled denominator mean). It is labelled "batches only", since it has no start part. It is where skewness shows. The script also prints the share of replicates whose recomputed denominator is zero or negative, and marks the percentile interval unreliable if that share exceeds 0.1 percent.
- **Each start's pooled value:** the statistic computed from start $s$ alone, for each $s$.
- The four mean squares, $u/(K_A K_H)$ before truncation, $V_{\mathrm{PB}}$, $V_c$, the share $V_c/(V_{\mathrm{PB}} + V_c)$, $\nu_c$, and $\nu$.
- **For every ratio, its denominator's distance from zero:** $\hat D$ divided by the unwidened standard error $\sqrt{V_{\mathrm{PB}} + V_c}$ of the denominator treated as a plain mean. For the shuffled ratio this is the draft's $z_D$.

### 4.6 The Open Points, Settled

| Open point | Decision |
|---|---|
| What each bootstrap replicate computes | The mean of the linearized cells, with $\hat\theta$ and $\hat D$ fixed from the full table |
| What the percentile interval is taken over | The statistic recomputed in each replicate; batches only; description |
| The shuffled ratio's linearized cell | Per cell: $\left[(x_{ijs} - z_{ijs}) - \hat\tau^{\mathrm{shuf}}(y_{js} - z_{ijs})\right]/\hat D$ |
| $\nu$ when $V_c = 0$ | $K - 1$ |
| Which $\hat\theta$ enters the start part's cells | The same full-table value as in the batch part |
| Divisor in $\mathrm{SE}^{*2}$ | $B - 1$, around the replicates' own mean |

### 4.7 Worked Example

The carry-over ratio with $K = 2$ and $n_s = 2$. Added harms, that is $x - k$ and $y - k$:

| | $s = 1$ | $s = 2$ |
|---|---|---|
| Own search, held-out 1 | 2 | 4 |
| Own search, held-out 2 | 4 | 6 |
| Carried, attack 1 on held-out 1 | 1.44 | 2.04 |
| Carried, attack 1 on held-out 2 | 2.12 | 2.88 |
| Carried, attack 2 on held-out 1 | 0.96 | 1.72 |
| Carried, attack 2 on held-out 2 | 2.04 | 2.80 |

**The ratio.** The carried mean is $16.00/8 = 2.00$ and the own mean is $16/4 = 4$, so $\hat\tau = 0.5$ and $\hat D = 4$.

**The cells** $W_{ijs} = (N_{ijs} - 0.5\, D_{js})/4$:

| $(i, j)$ | $s = 1$ | $s = 2$ | Mean over starts $\bar W_{ij}$ |
|---|---|---|---|
| (1, 1) | 0.110 | 0.010 | 0.060 |
| (1, 2) | 0.030 | $-0.030$ | 0.000 |
| (2, 1) | $-0.010$ | $-0.070$ | $-0.040$ |
| (2, 2) | 0.010 | $-0.050$ | $-0.020$ |

**Batch part.** Row effects $\alpha = (0.03, -0.03)$; column effects $\beta = (0.01, -0.01)$; residuals $\gamma = (0.02, -0.02, -0.02, 0.02)$. So $V_{\mathrm{closed}} = 0.0018/4 + 0.0002/4 + 0.0016/16 = 0.0006$, and $V_{\mathrm{PB}} = 2 \times 0.0006 = 0.0012$. With $K = 2$ the bootstrap has only 16 equally likely outcomes, and enumerating them gives a variance of exactly 0.0006, which a test can assert.

**Start part.** The start means are $0.035$ and $-0.035$, so $\mathrm{MS}_S = 4 \times 2 \times 0.035^2 = 0.0098$. Every interaction deviation is $\pm 0.005$, so $\mathrm{MS}_{AS} = \mathrm{MS}_{BS} = \mathrm{MS}_{ABS} = 0.0002$. Then $u = 0.0096$, $\hat\sigma^2_c = 0.0096/4 = 0.0024$, and $V_c = 0.0024/2 = 0.0012$. $\nu_c = 0.0096^2/(0.0098^2 + 3 \times 0.0002^2) = 0.96$, raised to 1.

**Interval.** $\nu = 0.0024^2/(0.0012^2 + 0.0012^2) = 2$; $t_{0.975,2} = 4.3027$; half-width $4.3027 \times \sqrt{0.0024} = 0.211$. The interval is 0.289 to 0.711.

**Beside it.** Start 1 alone gives $1.64/3 = 0.547$ and start 2 gives $2.36/5 = 0.472$. In the replicate that draws attack batch 1 twice and held-out batch 1 twice, the linearized value is $0.5 + 0.06 = 0.56$ and the recomputed ratio is $1.74/3 = 0.58$: the two differ, which is why the percentile interval is a separate description.

The session 4 checkpoint's example (Appendix D.1: $K = 8$, $n_s = 3$, mean squares 0.40, 0.10, 0.10, 0.04, $V_{\mathrm{PB}} = 0.002857$, giving $\nu = 6.2$ and a half-width of 0.156) must also be reproduced. For that, the function that turns $V_{\mathrm{PB}}$ and four mean squares into an interval should be callable on its own.

## 5. Missing Searches at a Harm Level

### 5.1 The Convention

1. **Every mean runs over every cell where its quantity exists.** A carried-over cell counts whenever its attack search reached the level, on all 16 held-out batches, whether or not the held-out batch's own search reached it. An own-search value counts whenever that held-out search reached the level. These are exactly $M_A$ and $M_H$ of Section 2, so Section 3's definitions need no change.
2. **"Large" needs no own search at the level:** its yardstick $q_{js}$ always exists.
3. **The batch part** uses the table $Z_{ij}$ of Section 5.2 in place of $\bar W_{ij}$. A batch with no search at the level stays in the resampling and contributes no cells; nothing is dropped and nothing divides by zero.
4. **The start part** uses the complete sub-table: all five starts, the attack batches with all five searches present, and the held-out batches with all five present. Its cells are the $W_{ijs}$ of Section 4.1 with $\hat\theta$ and $\hat D$ from all available data, and its formulas are those of Section 4.3 with $K_A$ and $K_H$ the numbers of batches kept. $V_c = \hat\sigma^2_c / n_s$ as before.
5. **The count rule is untouched.** More than 10 of 80 searches missing on either side makes the level Undetermined, exactly as signed. The script prints the numbers all the same, labelled as such. Whenever a level is read, at most 10 batches per side have a missing search, so the sub-table is at least 6 by 6 by 5. If the sub-table has fewer than 2 batches on a side, $V_c$ is set to 0 with the flag `start_part_not_estimable`.
6. **Printed with every level row:** the number of missing searches per side, which batches they belong to, and the sub-table's size.

### 5.2 The General Formulas

Define two centred sums, one for each kind of mean:

$$
E^A_{ij}[f] = \frac{K^2}{C_A}\sum_s a_{is}\left(f_{ijs} - M_A[f]\right), \qquad E^H_{j}[g] = \frac{K}{C_H}\sum_s b_{js}\left(g_{js} - M_H[g]\right).
$$

Each averages to zero over the $K$ by $K$ table. The table that replaces $\bar W_{ij}$ in the batch part is:

| Statistic | $Z_{ij}$ |
|---|---|
| $\tau$ | $\left(E^A_{ij}[x - k] - \hat\tau\, E^H_j[y - k]\right) / M_H[y - k]$ |
| $\tau^{\mathrm{shuf}}$ | $\left(E^A_{ij}[x - z] - \hat\tau^{\mathrm{shuf}}\left(E^H_j[y] - E^A_{ij}[z]\right)\right) / \left(M_H[y] - M_A[z]\right)$ |
| $\kappa$ | $\left(E^A_{ij}[x - z] - \hat\kappa\, E^A_{ij}[x - k]\right) / M_A[x - k]$ |
| "Large" | $E^A_{ij}[x - q]$ |
| $\bar X - \bar S$ | $E^A_{ij}[x - z]$ |
| $\bar Y - \bar S$ | $E^H_j[y] - E^A_{ij}[z]$ |

The batch part then proceeds as in Section 4.2 with $Z_{ij}$: resample, take $\mathrm{SE}^{*2}$, compare with $V_{\mathrm{closed}}$ computed on $Z$, and multiply by $K/(K-1)$. With nothing missing, $Z_{ij} = \bar W_{ij}$ minus a constant, so one implementation serves every row, and the script should use this general form everywhere. This is the usual treatment of a mean whose count varies between resamples, which Owen applies in his Section 4.2: the deviation of a resampled mean is approximated by its centred total over the original count.

In a percentile replicate, each mean is recomputed from the resampled batches' available cells. A replicate in which a mean has no cells is counted and left out of the percentiles.

### 5.3 Worked Example

Take Section 4.7's table and suppose attack search $(i, s) = (2, 2)$ never reaches the level, so the carried values 1.72 and 2.80 do not exist. Then $C_A = 2 \times 3 = 6$, the carried mean is $11.48/6 = 1.9133$, the own mean is still 4, and $\hat\tau = 0.4783$.

| $(i, j)$ | $E^A_{ij} = \frac{4}{6}\sum_s a_{is}(N_{ijs} - 1.9133)$ | $E^H_j = \frac{2}{4}\sum_s (D_{js} - 4)$ | $Z_{ij} = (E^A_{ij} - 0.4783\, E^H_j)/4$ |
|---|---|---|---|
| (1, 1) | $-0.2311$ | $-1$ | $0.0618$ |
| (1, 2) | $0.7822$ | $1$ | $0.0760$ |
| (2, 1) | $-0.6356$ | $-1$ | $-0.0393$ |
| (2, 2) | $0.0844$ | $1$ | $-0.0985$ |

The $Z_{ij}$ sum to zero. Their row effects are $\pm 0.0689$, column effects $\pm 0.0113$, and residuals $\pm 0.0183$, so $V_{\mathrm{closed}} = 0.002373 + 0.000063 + 0.000084 = 0.002520$ and $V_{\mathrm{PB}} = 0.005040$. Attack batch 2 keeps its one remaining search and simply weighs half as much. In this toy the sub-table has one attack batch, so the start part is not estimable; in the real table it always is.

### 5.4 Why Not "Triples Where Both Searches Reached the Level"

The draft's starting proposal drops a carried-over cell when the held-out batch's own search from the same start stalled. But a carried setting's harm on a held-out batch does not depend on the start of that batch's own search. Dropping the cell therefore discards a valid measurement, and it gives less weight to held-out batches whose own searches often stall. The ratio would then describe carry-over onto unseen text that itself breaks out easily, a selected subset, when the post's question is about unseen text in general. Because a level's own-search harm is nearly constant by construction (the pilot's standard deviation at 2 nats is 5 percent), the denominator barely depends on which held-out searches are kept; the selection acts on the numerator. Scenario T7 below prints both versions, so the choice is tested and not just argued.

"The largest complete sub-table" is also ambiguous: it does not say whether to drop a start or to drop batches, and finding the largest is a search. Rule 4 above is deterministic.

## 6. The Generator of Made-Up Experiments

**Why this design.** The interval's weak points come from the shape of real searches: breakouts, alternation, stalls, and one batch in eight that rises early. The pilot's 64 searches have that shape and are calibration data. Carried-over harm does not exist yet, so it is invented, with a truth known exactly.

**Source.** `vpd-audit-2/results/s4_pilot/part_a/runs.json`, key `a1`: for each pilot batch $c \in \{\mathrm{C1}, \dots, \mathrm{C8}\}$ and pilot start $p \in \{1, \dots, 8\}$, the list `record` of 321 raw harms $R_{cp}[0..320]$, entry $t$ being the harm after $t$ steps. No other pilot file is read; the sealed shuffle file stays sealed.

**One made-up experiment** ($K = 16$, $n_s = 5$):

1. **Batch types.** Each of the 16 attack and 16 held-out batches independently draws a pilot batch type, with probabilities $w_c$ (all $1/8$ unless a scenario says otherwise).
2. **Searches.** Each batch draws 5 distinct pilot starts, uniformly and independently of every other batch, and assigns them to starts 1 to 5. Start $s$ of a batch of type $c$ thus has a pilot record $R_{cp}$.
3. **A shared start effect.** Draw $\delta_s \sim \mathcal N(0, \sigma_\delta^2)$ for each start. Every search under start $s$, on both sides, is read through the warped record $R'[t] = R[\min(320, \mathrm{round}(t\, e^{\delta_s}))]$, $t = 0..320$. A positive $\delta_s$ makes every search under that start break out earlier. With $\sigma_\delta = 0$ there is exactly no start effect.
4. **The setting at a row.** At a search length $n$ it is step $n$ of the warped record. At a level $h$ it is the first step $t \ge 1$ with $\tfrac12(R'[t] + R'[t-1]) \ge h$, and the search is missing if there is none. From the setting's step $t^*$: own raw harm $R'[t^*]$ and own added harm $O = R'[t^*] - R'[0]$. Also $k = R'[0]$ and $q = R'[20]$.
5. **A held-out batch's vulnerability.** $v_j = f_{c(j)}\, g_j$, where $c(j)$ is the batch's type, $f_c$ is the type's mean added harm at 20 steps (unwarped, over its 8 pilot starts) divided by the $w$-weighted mean over types, and $g_j$ is log-normal with mean 1 and standard deviation 0.1. For reference, the type means are 0.594, 0.569, 0.500, 0.517, 1.183, 0.470, 0.452, and 0.463, so with equal weights $f$ runs from 0.76 to 1.99. This factor multiplies both carried and shuffled harm, so they share the held-out batch's effect with its own search, as real data will.
6. **Carried-over harm.** $x_{ijs} = k_{js} + v_j\, e_{ijs}\, \rho\, O_{is}$, where $O_{is}$ is the attack setting's own added harm, $e_{ijs}$ is log-normal with mean 1 and standard deviation 0.2, and $\rho$ is the scenario's retention. $\rho$ may depend on the row, on the attack batch's type, or on whether the attack setting's own raw harm is at least 5 nats.
7. **Shuffled harm.** $z_{ijs} = S_0\, v_j\, u_{ijs}$, with $u_{ijs}$ log-normal with mean 1 and standard deviation 0.05, and $S_0$ the scenario's shuffled level in raw nats.

A log-normal with mean 1 and standard deviation $\sigma$ is $\exp(\mathcal N(-\tfrac12\ell^2, \ell^2))$ with $\ell^2 = \ln(1 + \sigma^2)$.

**The truth, by enumeration.** Population means are taken over batch types with weights $w_c$, the 8 pilot starts equally, and $\delta$ over a fixed grid of 401 points across $\pm 4\sigma_\delta$ weighted by the normal density. Write $\mu_k$, $\mu_q$ for the means of $k$ and $q$ over all searches; $\mu_Y$ and $\mu_{Y+}$ for the means of own raw and own added harm over searches that have a setting at the row; and $\mu_C$ for the mean of $\rho\, O$ over those searches. Since $v$, $e$, and $u$ have mean 1 and the two sides are independent:

| Statistic | True value |
|---|---|
| $\tau$ | $\mu_C / \mu_{Y+}$ |
| $\tau^{\mathrm{shuf}}$ | $(\mu_k + \mu_C - S_0)/(\mu_Y - S_0)$ |
| $\kappa$ | $(\mu_k + \mu_C - S_0)/\mu_C$ |
| "Large" | $\mu_k + \mu_C - \mu_q$ |
| $\bar X - \bar S$ | $\mu_k + \mu_C - S_0$ |
| $\bar Y - \bar S$ | $\mu_Y - S_0$ |

Worked example: at a row where $\mu_k = 0.215$, $\mu_{Y+} = 0.59$, $\mu_Y = 0.805$, constant $\rho = 0.6$, and $S_0 = 0.40$: $\mu_C = 0.354$, $\tau = 0.6$, $\tau^{\mathrm{shuf}} = 0.169/0.405 = 0.417$, and $\kappa = 0.169/0.354 = 0.477$.

**A guard on the generator itself.** The three plain means are unbiased at search-length rows. If the average of any of them over a scenario's experiments differs from its truth by more than 3.5 Monte Carlo standard errors, the enumeration or the generator is wrong, and the test stops.

## 7. The Scenario List, Fixed

No scenario is added once the test has run; a new idea waits for a later session. Unless stated, $w_c = 1/8$, $S_0 = 0.40$ raw nats (the team's central prediction), and all eight rows are evaluated.

**Core scenarios** decide pass or fail and set the repair.

| ID | Retention $\rho$ | $\sigma_\delta$ | What it tests |
|---|---|---|---|
| P1, P2, P3 | 0.2, 0.6, 0.9 | 0 | Coverage on real tails with no start effect; P1 puts $\tau$ on its line |
| P4, P5, P6 | 0.2, 0.6, 0.9 | 0.09 | The same with a realistic start effect |
| P7, P8 | per row, $(\mu_q - \mu_k)/\mu_{O}$ | 0, 0.09 | "Large" with its truth at zero |
| P9, P10 | per row, $\left(S_0 + 0.2(\mu_Y - S_0) - \mu_k\right)/\mu_O$ | 0, 0.09 | $\tau^{\mathrm{shuf}}$ with its truth at 0.2 |
| P11, P12 | per row, $(S_0 - \mu_k)/\mu_O$ | 0, 0.09 | $\tau^{\mathrm{shuf}}$ and $\kappa$ with their truths at zero |
| P13 | 0.3 if the attack setting's own raw harm is under 5 nats, else 0.9 | 0.09 | Two kinds of setting carrying over differently (Riku's mixture, Lena's two kinds) |

Here $\mu_O$ is the population mean of own added harm at the row. The value 0.09 is the square root of the pilot's start component for the log of the 2-nat crossing step.

**Stress scenarios** are reported and become stated caveats. They never set the repair.

| ID | Change from P5 ($\rho = 0.6$, $\sigma_\delta = 0.09$) | What it tests |
|---|---|---|
| T1, T2 | Type C5's weight is $1/16$, then $1/4$, the other types sharing the rest equally | Rarer and commoner early-breakout batches |
| T3 | $\rho = 0.4$ for settings found on type-C5 attack batches, 0.8 otherwise | Ruth's item 4. Coverage is reported by the number of type-C5 batches on each side (0, 1, 2, 3 or more) |
| T4 | $\sigma_\delta = 0.25$ | The truncated start term at its worst |
| T5 | Each attack search, with probability 0.02, carries 40 raw nats to every held-out batch; each remaining cell, with probability 0.01, is set to 40 raw nats. The truth's $\mu_k + \mu_C$ becomes $0.9702(\mu_k + \mu_C) + 0.0298 \times 40$ | Carried-over cells that jump to very large harm |
| T6 | $\rho = 0.7$; $S_0 = \psi\,\mu_Y$ for $\psi \in \{0.3, 0.5, 0.7, 0.85, 0.95, 1.0, 1.1, 1.25\}$; rows 20 and 80 only | Riku's sweep of shuffled harm. Results are reported in bins of $z_D$ |
| T7 | Level 5 only, $\rho = 0.7$. After generation, all 5 searches of one attack batch chosen at random are made missing, and so are the 5 held-out searches with the lowest mean carried-over harm | Ruth's item 3. The report prints the bias and coverage of Section 5's convention and, beside them, the mean of the "both reached" estimate |
| T8 | $K = 8$, $\rho = 0.7$, search-length rows. A second "delta-on" table is generated for the same batch types under a null in which the delta components do nothing, in two versions: (a) the same searches with fresh cell noise; (b) every search redrawn from its batch type's pilot starts | Ruth's item 12. Real path noise lies between the two versions. The report prints the spread of the paired share |

**Check scenarios** have exact known answers and are not built on the pilot.

| ID | Data | Known answer |
|---|---|---|
| G1 | Gaussian attack-batch and held-out-batch effects only | Coverage of a plain mean is 95 percent within Monte Carlo error |
| G2 | Gaussian independent cell noise only | $V_{\mathrm{PB}}$ averages 2.94 times the true variance at $K = 16$, and coverage exceeds 99 percent |

The deterministic checks of the draft's E5 are separate from these. Those that exercise this note's code are: Section 4.7's example with its enumerated bootstrap, Section 5.3's example, the checkpoint's Appendix D.1 example, the scale check (every harm times 100 leaves every ratio's interval unchanged and scales every plain mean's by 100), a table with no dependence on the start (which must give $\nu = K - 1$ without error), the two-batch example of Section 4.1, and one batch with no searches at a level.

## 8. The Criterion and the Repair

**Size.** 2,000 experiments per scenario from a recorded master seed. A harm-level row is judged on the experiments in which the count rule lets the level be read; experiments are added until 2,000 are read or 20,000 have been generated, and the share read is reported. Inside the test the batch part uses $V_{\mathrm{closed}}$ in place of the 10,000-replicate bootstrap, which it equals up to Monte Carlo error; percentile intervals, for core scenarios only, use 1,000 replicates.

**Cells judged.** Each core scenario, at each row, for each of the three signed readings: $\tau$, $\tau^{\mathrm{shuf}}$, and "large" (not at 20 steps). Write $d = \hat\theta - \theta$ for the error and $w$ for the unwidened half-width.

**"Too narrow" (draft E2).** A cell fails if either holds:
- its coverage, the share of experiments with $|d| \le w$, is below 92.5 percent;
- its truth sits on a line (P1 and P4 for $\tau$; P7 and P8 for "large"; P9 to P12 for $\tau^{\mathrm{shuf}}$) and the interval lies wholly above the line in more than 3.75 percent of experiments, or wholly below it in more than 3.75 percent.

A cell under 93.5 percent is rerun with 10,000 experiments and fails only if the rerun is under 92.5.

**The repair (draft E3).** A row whose core cells all pass keeps $\lambda_r = 1$. For a row with a failing cell:

1. For each of the row's core cells compute the multiplier it needs: the 95th percentile of $|d|/w$ and, where the truth is on a line, also the 96.25th percentiles of $d/w$ and of $-d/w$; take the largest.
2. $\lambda_r$ is the largest of these over the row's core cells, rounded up to a multiple of 0.05.
3. Confirm on 2,000 fresh experiments per core scenario from a second master seed, with $\lambda_r$ applied: every core cell of the row must now pass. If one does not, raise $\lambda_r$ by 0.05 and confirm again on a third seed.
4. If $\lambda_r$ would exceed 1.5, stop: the row goes to the PI.
5. Record every $\lambda_r$ as part of the dated amendment before any real run. $\lambda_r$ applies to all six statistics of the row, and to the delta-on run at the same search length.

Worked example: a row's worst cell has coverage 91.8 percent and a 95th percentile of $|d|/w$ of 1.12, and no other cell needs more. Then $\lambda_r = 1.15$. If the fresh set gives that cell 95.1 percent, the row is done.

**Stated, not repaired (draft E4).** No multiplier repairs an interval from a sample that holds none of a rare kind of batch, or none of a rare jump in carried-over cells. T1 to T3 and T5 measure how bad that is, and the post states the result as a limit of 16 batches. The real analysis prints, per side, the number of batches whose 20-step added harm exceeds twice the median batch's.

## 9. What the Test Report Prints

One line per scenario, row, and statistic (all six), in a machine-readable file and a summary table:

- the truth; the mean estimate and its difference from the truth; the Monte Carlo standard deviation of the estimate;
- coverage of the unwidened interval; the share of experiments with the interval wholly above the truth, and wholly below it;
- the mean of $V_{\mathrm{PB}} + V_c$ divided by the Monte Carlo variance of the estimate;
- the 5th, 50th, and 95th percentiles of the half-width;
- the share of experiments with $V_c = 0$, the share with $V_c/(V_{\mathrm{PB}} + V_c) > 0.5$, and the mean $\nu$ (Ruth's item 6);
- the multiplier needed, as in step 1 of the repair;
- for core scenarios, coverage of the percentile interval;
- where the truth is on a line, the frequency of each verdict; for $\tau^{\mathrm{shuf}}$ always, the frequency of each of the four signed readings and of "no reading defined";
- for every ratio, the median of its denominator's distance from zero; for $\tau^{\mathrm{shuf}}$ in T6, coverage and reading frequencies in bins of $z_D$: below 2, 2 to 3, 3 to 5, 5 to 8, above 8;
- for harm-level rows, the mean number of missing searches per side and the share of experiments read;
- for T3, coverage by the number of type-C5 batches per side; for T7, the two estimates' means; for T8, the 2.5th, 50th, and 97.5th percentiles of the paired share at each search length, and its interval's coverage of 1.

Then, in words: each core cell's pass or fail; each row's $\lambda_r$ with its confirmation; every stress cell under 92.5 percent, as the list of caveats for the post; G1 and G2 against their known answers; the seeds and the commit.

## 10. Where I Differ From the Draft

- **R9, replaced** by Section 5: every mean over every cell where its quantity exists, a table that handles missing and empty batches without a special case, and a deterministic sub-table for the start part. Reasons in Section 5.4.
- **R10, agreed.** It is the limit of the signed formula.
- **E2, one addition:** harm-level rows are judged on the experiments in which the level is read.
- **E3, three additions:** a row that passes keeps $\lambda_r = 1$; the multiplier is computed from percentiles of $|d|/w$, not searched for; "confirmed" means every core cell of the row passes on a fresh seed.
- **E5, stronger:** because replicates average linearized cells, the closed form checks every statistic on every row, not only the "large" difference.
- **R3 and R5, a detail:** $z_D$ and the intervals of the plain differences use the unwidened standard error, so that a multiplier cannot make a denominator look further from zero than it is.
- **R11, a detail:** the paired share takes the same interval machinery with $K = 8$; T8 supplies the null spread to read it against.

## 11. What I Am Unsure Of

- **The carried-over model is invented.** Cell noise of 0.2, a vulnerability tied to a batch type's 20-step harm, and shuffled harm that ignores which setting was shuffled are guesses. The test can show under-coverage caused by real own-search tails and by the scenarios' structure, not by structure in real carried-over cells that nobody has imagined.
- **The generator's batch types repeat.** With 16 batches drawn from 8 types, same-type batches share searches, which makes type effects somewhat stronger and pairing noise somewhat weaker than in real data. Rows are still independent draws, so the interval's assumptions hold as well as they do in reality.
- **The start part under missing searches** is estimated on batches whose searches all reached the level, a selected set. I judge this second-order, since the start term is a small share of the variance at harm levels, but it is untested outside T7.
- I have not run any of this. Hand arithmetic in Sections 4.7 and 5.3 was checked twice; an implementation that disagrees with it should be compared line by line before either is trusted.
