# The Results Table and the Run's Guards: Specification for the Run

The table and run specification. Written before any deciding run.

## 1. Purpose and Scope

The lead experiment (question 2) searches for damaging mask settings on some batches of text and scores them, unchanged, on batches the search never saw. Its results will be read by signed rules, `freeze/part1.md` ("the signed rules"), as amended by the pre-run decisions (research log; "the draft"). This note specifies three things:

1. **The table:** the one data format that the real run and the made-up-data generator both write, and the only data the analysis script reads (Section 3).
2. **The run:** what each cloud job computes and saves, the guards that stop it from silently computing the wrong thing, restarts, and sealing (Sections 4 to 8).
3. **Spend:** a realistic estimate with overhead, and the checks against the author's \$105 cap (Section 9).

How intervals are computed from the table is `interval_spec.md`. Where this note and the signed rules differ, the signed rules govern. Section 11 lists the points where this note departs from the draft or needed a decision.

File paths are relative to the project folder. Code lives in `vpd-audit-2/vpd_audit_2/`; we refer to `adversary.py` as `A` and `pilot.py` as `P`.

## 2. Terms

- **Harm:** per-token KL divergence from the original model's next-token distribution, in nats, averaged over the 512 positions of each text and over a batch's 128 texts. **Raw** harm is that number. **Added** harm is raw harm minus the raw harm of the search's random starting point on the same batch.
- **Setting:** one value in $[0, 1]$ per component, 38,936 values in all (38,912 rank-one components and 24 delta components), shared by every position of every text. The authors' code calls it a "source".
- **Search:** one run of the adversary on one batch from one starting point, 320 steps.
- **Arm:** the **lead** arm (16 attack batches A1 to A16, 16 held-out batches H1 to H16, delta components optimized) or the **delta-on** arm (A1 to A8, H1 to H8, delta components held at 1).
- **Unit:** the smallest piece of work a restart can skip: one search with its own-batch re-scores, or one scoring block (Section 4.1).

## 3. The Table

### 3.1 Design Principles

- **Raw harm only.** Every harm in the table is raw. The table holds no added harm, no ratio, and no mean over cells; the analysis script forms them. One convention removes the risk of subtracting the starting harm twice or not at all.
- **One table per arm.** The lead arm and the delta-on arm each get a table of the same format, with different sizes.
- **Two files per table.** `table_core.npz` holds everything the readings need and is small. `table_per_text.npz` holds per-text harms, about 60 MB for the lead arm, and is needed only for the recomputation without the 11 overlapping texts and for description. The core file records the per-text file's SHA-256.
- **In memory and on disk alike.** The table is a dictionary of named arrays plus one metadata dictionary. The analysis functions take that dictionary. The real run and the known-answer checks pass through the files; the coverage simulation, which builds thousands of made-up tables, may build the dictionary in memory and omit the per-text arrays.

### 3.2 Indices

| Index | Meaning | Lead arm | Delta-on arm |
|---|---|---|---|
| $i$ | Attack batch, in the order of `attack_names` | 16: A1 to A16 | 8: A1 to A8 |
| $j$ | Held-out batch, in the order of `heldout_names` | 16: H1 to H16 | 8: H1 to H8 |
| $s$ | Starting point, in the order of `starts` | 5: starts 9, 10, 11, 12, 13 | the same |
| $q$ | Scored setting, in the order of `setting_names` | 10 (below) | 5: `n20` to `n320` |
| $r$ | Shuffled copy | 8 | 8 |
| $t$ | Text within a batch, in the manifest's order | 128 | 128 |
| $k$ | Step of a search; entry $k$ is the state after $k$ updates | 0 to 320 | 0 to 320 |

The ten scored settings of the lead arm, in this fixed order:

| $q$ | Name | Which setting | Has shuffled copies |
|---|---|---|---|
| 0 to 4 | `n20`, `n40`, `n80`, `n160`, `n320` | After step 20, 40, 80, 160, 320 | Yes |
| 5, 6 | `n159`, `n319` | After step 159, 319 | No |
| 7, 8, 9 | `h2`, `h5`, `h10` | After the first step $k \ge 1$ at which the two-step mean of the search's own harm, $\tfrac12(\mathrm{KL}(k) + \mathrm{KL}(k-1))$, reaches 2, 5, 10 nats | Yes |

### 3.3 Arrays of the Core File

All harms are raw, in nats per token, stored as float64. The batch-level harms are the authors' own values, `float(sum_loss) / n_examples`, never a mean of per-text values.

**Searches on their own batches.** The `_A` arrays describe attack searches and the `_H` arrays held-out searches; only the first axis differs.

| Array | Shape | Content |
|---|---|---|
| `rec_A`, `rec_H` | $[K, n_s, 321]$ | The search's own harm record: entry $k$ is the harm of the setting after $k$ updates on the batch searched. Entry 0 is the starting point's harm |
| `step_A`, `step_H` | $[K, n_s, Q]$, int32 | The step of each scored setting: 20, 40, 80, 160, 320, 159, 319, then the three level-crossing steps. $-1$ where a level was never reached |
| `own_A`, `own_H` | $[K, n_s, Q]$ | Each scored setting re-scored on its own batch by the scoring path. NaN where the step is $-1$ |
| `init_A`, `init_H` | $[K, n_s]$ | The starting point re-scored on the batch by the scoring path |
| `setting_sha_A`, `setting_sha_H` | $[K, n_s, Q]$, text | SHA-256 of each saved setting's float32 bytes; empty where the step is $-1$ |
| `prep_fp_A`, `prep_fp_H` | $[K]$, text | Fingerprint of the batch's labels, target output, and weight deltas (Section 5, guard G3) |
| `ids_sha_A`, `ids_sha_H` | $[K]$, text | SHA-256 of the batch's token ids, $128 \times 512$ |

**Settings carried to held-out batches.**

| Array | Shape | Content |
|---|---|---|
| `carried` | $[K_A, K_H, n_s, Q]$ | Harm on held-out batch $j$ of setting $q$ of the search on attack batch $i$ from start $s$. NaN where `step_A[i, s, q]` is $-1$ |
| `shuf` | $[K_A, K_H, n_s, Q, 8]$ | Harm on held-out batch $j$ of each shuffled copy of that setting. NaN where the setting is missing or has no shuffled copies |
| `block_ids_sha` | $[K_A, K_H, n_s]$, text | SHA-256 of the token ids of the batch the scoring job actually held when it produced these values |

**Shuffles, described.** These depend on the setting only, not on any harm.

| Array | Shape | Content |
|---|---|---|
| `shuf_sha` | $[K_A, n_s, Q, 8]$, text | SHA-256 of each shuffled setting |
| `shuf_moved` | $[K_A, n_s, Q, 8]$ | Share of the 38,912 rank-one entries that the shuffle changed by more than 0.5 |
| `shuf_moved_alive` | $[K_A, n_s, Q, 8]$ | The same share among the 9,948 entries in strata 0 to 9 (components that are not dead) |

**Labels of the axes.** `attack_names`, `heldout_names` (text), `starts` (int), `setting_names` (text), `has_shuffles` $[Q]$ (bool), `excluded_H` $[K_H, 128]$ (bool: true for a held-out text that shares a 50-token span with an attack text, Section 7), `text_ids_H` $[K_H, 128]$ (text).

### 3.4 Arrays of the Per-Text File

Per-text harm is the mean over a text's 512 positions, in nats per token, stored as float32. Each array is the per-text counterpart of a core array, with a last axis $t$ of length 128.

| Array | Shape | Counterpart |
|---|---|---|
| `carried_text` | $[K_A, K_H, n_s, Q, 128]$ | `carried` |
| `shuf_text` | $[K_A, K_H, n_s, Q, 8, 128]$ | `shuf` |
| `own_A_text`, `own_H_text` | $[K, n_s, Q, 128]$ | `own_A`, `own_H` |
| `init_A_text`, `init_H_text` | $[K, n_s, 128]$ | `init_A`, `init_H` |

### 3.5 How Missing Level Settings Are Marked

A search whose two-step mean never reaches a level by step 320 has no setting at that level. Three rules mark it, and the analysis script asserts all three before computing anything:

1. `step` is $-1$ at that $(\text{batch}, s, q)$, and only $q \in \{$`h2`, `h5`, `h10`$\}$ may be $-1$.
2. A harm is NaN exactly where its setting is missing: `own[b, s, q]`; and, for an attack search, `carried[i, :, s, q]` and `shuf[i, :, s, q, :]`. `shuf` is also NaN for `n159` and `n319`, which have no shuffled copies.
3. No other entry of any harm array is NaN or infinite.

A missing held-out search does **not** blank `carried`: every attack setting is still scored on that batch. Which cells enter a level's ratio when the held-out search is missing is the interval specification's convention (the draft's R9); the table keeps everything so that any convention can be computed.

Nothing is ever substituted for a missing setting. In particular the final setting, which the pilot's files also stored, never stands in for a level setting.

### 3.6 What Counts as Complete

The assembler (Section 4.4) sets `meta["complete"] = true` only if every unit of the arm has finished. The analysis script trusts nothing and re-checks:

- every array is present with exactly the shape that `meta["design"]` declares;
- the three rules of Section 3.5 hold;
- `meta["n_scoring_passes"]` equals the number computed from `step_A` (below);
- `block_ids_sha[i, j, s]` equals `ids_sha_H[j]` for every block, and no entry of `ids_sha_H` equals any entry of `ids_sha_A`;
- `own` equals `rec` at `step`, and `init` equals `rec[..., 0]`, bit for bit (guard G4);
- `shuf_sha` has no empty entry where a setting exists and has shuffled copies.

If any check fails the script prints the name of the check and exits without printing a harm.

**Expected number of carried scoring passes.** With $m$ the number of missing level settings among the arm's attack searches, the lead arm has $16 \times [\,80 \times (10 + 8 \times 8) - 9m\,] = 94{,}720 - 144\,m$ passes, since each missing level setting removes 1 unshuffled and 8 shuffled passes on each of 16 held-out batches. The delta-on arm has $8 \times 40 \times 45 = 14{,}400$.

### 3.7 Metadata

`meta` is one JSON string in the core file: `kind` (`"real"` or `"made_up"`), `arm`, `design` (the sizes of every axis), `complete`, `n_scoring_passes`, the commit of the run code with a clean-tree flag, the SHA-256 of the manifest, of `starts_1_64.npz`, of `strata.npz`, and of the per-text file, the GPU and environment record of every container, and each container's function seconds. A made-up table carries its scenario's name and seed and may use any text in the hash fields, subject to the checks of Section 3.6.

### 3.8 Reading the Signed Quantities From the Table, With a Worked Example

For one table row, a search length or a level with setting index $q$, the per-cell quantities of the signed rules are:

$$
\begin{aligned}
\mathrm{KL}_0[j,s] &= \texttt{rec\_H}[j, s, 0] && \text{starting harm on the held-out batch} \\
X[i,j,s] &= \texttt{carried}[i, j, s, q] && \text{carried-over harm} \\
Y[j,s] &= \texttt{rec\_H}\big[j, s, \texttt{step\_H}[j,s,q]\big] && \text{the held-out batch's own search} \\
Y^{20}[j,s] &= \texttt{rec\_H}[j, s, 20] && \text{the yardstick for ``large''} \\
S[i,j,s] &= \tfrac18 \textstyle\sum_r \texttt{shuf}[i, j, s, q, r] && \text{shuffled copies}
\end{aligned}
$$

Note that $Y$ at a level is the harm of the setting at the crossing step, $\mathrm{KL}(k)$, not the two-step mean that defined the crossing.

**Worked example.** Two attack batches, two held-out batches, one start, the 20-step row:

| | Held-out 1 | Held-out 2 |
|---|---|---|
| `rec_H[j, 0, 0]`, starting harm | 0.20 | 0.24 |
| `rec_H[j, 0, 20]`, own search | 0.80 | 0.86 |
| `carried[0, j, 0, n20]`, from attack batch 1 | 0.70 | 0.74 |
| `carried[1, j, 0, n20]`, from attack batch 2 | 0.66 | 0.78 |
| Mean of `shuf[0, j, 0, n20, :]` | 0.60 | 0.62 |
| Mean of `shuf[1, j, 0, n20, :]` | 0.58 | 0.64 |

The means over cells are $\overline{\mathrm{KL}_0} = 0.22$, $\bar Y = 0.83$, $\bar X = (0.70 + 0.74 + 0.66 + 0.78)/4 = 0.72$, and $\bar S = 0.61$. Then the carry-over ratio is $(0.72 - 0.22)/(0.83 - 0.22) = 0.82$, the shuffled ratio is $(0.72 - 0.61)/(0.83 - 0.61) = 0.50$, and the composition share $\kappa$ of the draft's Section 2 is $(0.72 - 0.61)/(0.72 - 0.22) = 0.22$.

Read back: every number came from raw harms, the starting harm was subtracted once on each side of the carry-over ratio, and the shuffled ratio never used it. If the search on attack batch 2 had never reached 5 nats, then at the `h5` row `step_A[1, 0, 8]` would be $-1$ and `carried[1, :, 0, 8]` NaN, while the row for attack batch 1 would be unaffected.

## 4. The Run

### 4.1 Jobs and Units

One cloud container handles one batch of one arm. **A container for a held-out batch never receives the token ids of any attack batch, and the reverse.** This is the main structural defence against the error we most fear: scoring a setting on the batch it was found on, which would produce a carry-over ratio near 1, the very result we expect.

| Stage | Containers | Each container's work, in order |
|---|---|---|
| 0. Rehearsal | 1, on calibration batch C1 | Section 8 |
| 1. Lead, attack side | 16, one per attack batch | Prepare the batch; for each start, one **search unit** |
| 2. Lead, held-out side | 16, one per held-out batch | Prepare the batch; for each start, one search unit; then, for each attack batch and each start, one **scoring block** |
| Spend check | | Section 9 |
| 3. Delta-on, attack side | 8 | As stage 1, with the delta components held at 1 |
| 4. Delta-on, held-out side | 8 | As stage 2, with the delta-on settings |
| 5. Assemble and copy | 1, CPU only | Section 4.4 |

**A search unit** is one search plus its own-batch re-scores:

1. Run `A.run` for 320 steps from the hash-checked start, with the save hook and cumulative gradients (Section 4.2).
2. Re-score, on the same batch through the per-text scoring path (Section 6), the starting point and every saved setting that is scored.
3. Check guards G4 and G5, write the unit's files, and mark it done.

**A scoring block** is one (attack batch $i$, start $s$) pair scored on the container's held-out batch: every scored setting of that attack search, unshuffled, and its 8 shuffled copies where it has them. That is at most 74 passes, about 13 seconds.

### 4.2 What a Search Unit Saves

| Item | Where | Notes |
|---|---|---|
| Harm record, 321 values | Sealed area | From `A.run`, unchanged |
| Every hooked setting: after steps $n$ and $n - 1$ for $n \in \{20, 40, 80, 160, 320\}$, and at each level crossing; with its step and SHA-256 | Open area | Settings are mask values, not harms. Save all the hook produces, including the five the lead does not score (steps 19, 39, 79 and so on) |
| Cumulative gradients at each hooked setting | Open area | Two float32 vectors of 38,936 entries per setting: the signed sum and the sum of absolute values of the per-entry gradient over iterations $0$ to $k - 1$, where iteration $m$'s gradient is taken at the setting after $m$ updates. For the deferred exploited-components analysis; no reading uses them now |
| Own-batch re-scores: batch harm and 128 per-text harms for the start and each scored setting | Sealed area | |
| The start's index and SHA-256; the batch's name, `ids_sha`, and `prep_fp`; the commit, GPU, environment, determinism mode, and seconds | Open area | |

Recording gradients must not change the search. The requirement is tested twice: on the tiny model a search with gradient recording equals one without, bit for bit; and in the rehearsal the search on C1 from start 1 reproduces the pilot's stored record and saved-setting hashes bit for bit (`results/s4_pilot/part_a/runs.json`).

### 4.3 What a Scoring Block Saves

For each scored setting present in the attack search's file: the batch harm and 128 per-text harms of the unshuffled setting and of each of its 8 shuffled copies; the SHA-256 of each shuffled setting and its two moved shares; the block's `block_ids_sha` and `prep_fp`; and the SHA-256 of the attack search file it read. All harms go to the sealed area.

**Shuffles.** `P.shuffle_source` with the committed strata, `results/s4_pilot/part_a/strata.npz`, loaded and checked against its recorded SHA-256 (`12ce9067…0af2`), never recomputed. The key of a shuffle is (arm, attack batch, start, setting name, $r$) with $r = 1, \dots, 8$, under a seed label of its own such as `"q2-shuffle"`. The key does not include the held-out batch: the same 8 shuffled copies of a setting are scored on every held-out batch. The assembler asserts that every held-out container reported the same `shuf_sha` for the same shuffle.

### 4.4 Assembling the Table

A CPU-only cloud function builds each arm's table from the unit files:

1. Refuse to start unless every expected unit has its completion marker and the marker's hash matches the unit file.
2. Fill the arrays by name: each unit file carries its batch name, start index, and setting names, and the assembler places values by those names, never by file order.
3. Run every check of Section 3.6 and the cross-unit guards of Section 5.
4. Write both files with `manifest.deterministic_npz`, so that the same units always give the same bytes.
5. Return only the two paths, their SHA-256, the declared shapes, and `complete`.

### 4.5 Fixed Configuration, Asserted in Every Container

Section 0 of the signed rules, as code: `micro_batch=None`; precision `"bf16"`; the GPU's name contains "B200"; deterministic algorithms on with `warn_only` off; TF32 off; `CUBLAS_WORKSPACE_CONFIG=:4096:8`; a clean tree at the recorded commit; the manifest's and the starts file's SHA-256 as signed. The set of starts is a constant, `(9, 10, 11, 12, 13)`, and the run refuses any other. A container refuses a batch whose pool is not the side it serves. If a B200 is unavailable the run waits.

## 5. Guards

Each guard is a requirement with a test. A failed guard stops the container with a message that names the guard and the unit and carries no value (Section 7).

| # | Guard | Where it runs | Test with a made-up input |
|---|---|---|---|
| G1 | **The batch is the one named.** The token ids' per-row hashes equal the manifest's; the pool name is on the container's side | Container start | Hand a held-out container an attack pool's name or ids: it refuses |
| G2 | **No container holds both sides.** A held-out container's inputs include no attack ids | By construction; a test inspects the job's arguments | |
| G3 | **One set of labels and targets per batch.** `prep_fp` is a bit-exact fingerprint of the labels, target output, and weight deltas. Every unit file stores it; a restarted container recomputes it and stops if it differs from any finished unit's | Container start and every unit | Perturb one label by one unit after a restart: the container stops |
| G4 | **The scoring path reproduces the search.** `own` equals the record at the setting's step, and `init` equals record entry 0, bit for bit | Every search unit; again in the assembler and the analysis script | On the tiny model, save the setting of the wrong step under a name: the guard fails |
| G5 | **Per-text values agree with the batch value.** In float64, the mean of the 128 per-text harms is within $10^{-5}$ relative of the batch harm | Every scoring pass | Return per-position sums along the wrong axis: the guard fails |
| G6 | **A carried value is not an own-batch value.** For every block and setting, the 128 per-text harms of the carried setting are not all equal to the 128 per-text harms of the same setting on its attack batch | Assembler | Build a table in which `carried[i, j]` is copied from `own_A[i]`: the assembler refuses |
| G7 | **The hook and the crossing rule agree.** For every search and level, the step the save hook recorded equals `P.crossing(record, h)["k"]`, and both are missing together | Every search unit | A record that alternates across a level (Section 10) |
| G8 | **Shuffles are shuffles.** Each shuffled copy has the same sorted values as the setting within every stratum of every matrix, has the 24 delta entries unchanged, and differs from the setting and from the other 7 copies | Where shuffles are made | A setting constant within every stratum must fail the "differs" part, so that part is recorded as a count and not asserted; the first two parts are asserted |
| G9 | **Files are whole.** Every file is written under a temporary name, renamed, and followed by a completion marker holding its SHA-256; the volume is committed after each search unit and after each attack batch's five scoring blocks | Every write | Section 5.1 |
| G10 | **The attack file read is the one written.** A scoring block checks the attack search file's completion marker and hash before use and records the hash | Every scoring block | Truncate a search file: the block refuses |

G6 compares per-text vectors and not the two batch means because two unrelated batch means can agree by chance to the last bit about once in a million comparisons, while 128 values cannot.

### 5.1 Restarts

- A unit is finished if and only if its completion marker exists and matches the file. A restart reloads the volume, deletes temporary files and any file without a matching marker, and skips finished units.
- A search is never resumed in the middle. An unfinished search starts again from step 0; at most two minutes are lost.
- A restarted container recomputes the batch's labels and targets and applies G3. If G3 fails, the container stops and the matter is reviewed; there is no automatic recovery, because the finished units of that batch then rest on a tensor that can no longer be reproduced.

**The kill-and-restart test** (signed rules, Section 10, item 1), on the tiny model on a CPU: run a small arm (2 attack batches, 2 held-out batches, 2 starts) once without interruption, and again with the job killed at each of three points and restarted: between units; after a unit's file is renamed but before its marker is written; and during a scoring block. The assembled table's two files must have the same SHA-256 in every case. The rehearsal repeats the between-units kill once in the cloud, because a cloud volume loses uncommitted writes, which no local test can show.

## 6. The Per-Text Readout

**The idea works, with one change.** `_forward_with_adv_sources` (the authors' `param_decomp/metrics/pgd_utils.py`, line 204) builds the masks, runs the model once, and ends with `sum_loss, n_examples = reconstruction_loss(out, target_out)`. So a callable object passed as `reconstruction_loss` sees the logits of that one forward pass and can keep per-text values as a side effect. No extra model pass is needed.

**The change.** The wrapper should not call the authors' `recon_loss_kl` and then compute the KL a second time. The KL runs over a tensor of $128 \times 512 \times 50{,}277$ logits, about 13 GB in float32, and we expect it to be a large part of the 0.18 seconds a scoring pass takes. A second copy of that work on each of about 110,000 passes could cost \$10 or more, which the cap cannot absorb. Instead the wrapper repeats the authors' three lines exactly and adds one cheap line:

```python
class KLWithPerText:
    """The authors' recon_loss_kl, line for line, keeping each text's mean harm from the same tensor."""
    def __call__(self, pred, target):
        assert pred.shape == target.shape
        log_q = torch.log_softmax(pred, dim=-1)
        p = torch.softmax(target, dim=-1)
        kl_per_position = F.kl_div(log_q, p, reduction="none").sum(dim=-1)   # [texts, positions]
        self.per_text = kl_per_position.double().mean(dim=1)                 # [texts], nats per token
        return kl_per_position.sum(), math.prod(pred.shape[:-1])
```

`A._forward` gains a `reconstruction_loss` argument whose default is the authors' function, so the search path is untouched, and a new `A.score_per_text` passes the wrapper. The search itself never uses the wrapper.

**How it is verified.**

1. **Same batch value as the authors' function.** On the tiny model, and in the rehearsal on the real model under bfloat16 autocast, the wrapper's returned sum equals `recon_loss_kl`'s on the same logits, bit for bit.
2. **Same batch value as the search, on every setting of the real run.** Guard G4: each own-batch re-score through the wrapper must equal the search's record, which came from the authors' function. That is about 2,600 bitwise comparisons across the two arms, and one failure stops the run.
3. **The per-text values are per text.** On the tiny model, each text's value equals the harm of that text scored alone as a batch of one, within $10^{-5}$ relative; and reordering the batch's texts reorders the vector the same way. A fixture with one constant-token text gives one value very different from the rest, so a sum along the wrong axis cannot pass.
4. **Per-text and batch values agree.** Guard G5, on every pass.

The rehearsal also measures the seconds per scoring pass with the wrapper, which the spend projection uses.

## 7. Sealing

**What is sealed.** Every harm produced from a deciding batch: carried and shuffled harms, and also the searches' own records, own-batch re-scores, starting harms, and level-crossing steps. The signed rules seal only carry-over numbers. We seal the own-batch values too because it costs nothing and because the count of searches that never reach 10 nats decides whether that level reads undetermined; nobody should see it before the script prints it.

**Where sealed values live.** On the cloud volume under one folder per arm, for example `/cache/s5_lead/<arm>/sealed/`, with a do-not-open notice. Settings, gradients, hashes, and timings live beside it under `open/`.

**What a job may return or log.** Only: unit identifiers; counts of finished units; seconds; hashes; the names and outcomes of guards as true or false; and the environment record. The return value is a typed record with fields of those kinds and no free-form dictionary. All logging goes through one function that accepts only those fields.

**What a job may not do.** Print or return any harm, per-text harm, crossing step, or count of missing settings. Use `numpy.testing` assertions or any assertion whose message formats a tensor or a float; messages name the guard and the unit only. When a guard fails, debugging is done on the tiny model or a calibration batch, never by opening deciding values.

**Copying.** The assembler writes the two table files on the volume. The local side copies each as bytes with `volume.read_file`, checks the SHA-256 against the one the assembler returned, and writes it under `results/s5_lead/<arm>/sealed/`. Nothing on the local side loads the files. This is the pilot's pattern (`modal_pilot.py`, lines 131 to 135), which was written after the pilot's question 2 part ran and has not yet run in the cloud; the rehearsal runs it first.

**Lifting the seal.** The committed analysis script, at a recorded commit with a clean tree, is the first program to load a table. We recommend it run only once both arms' tables are complete, or the author has ruled on the delta-on arm after a spend stop, so that no decision about the delta-on arm is taken with the lead's results in view.

**Tests.** On the tiny model, run a whole small arm and capture everything printed, logged, and returned. Assert that the captured text contains no floating-point number outside the `seconds` fields, and that the lead modules contain no bare `print`.

## 8. The Rehearsal

One B200 container on calibration batch C1 with pilot start 1, before any deciding batch is touched. It scores nothing on another batch, so it reveals no carry-over number. It costs about \$0.60.

1. Run the search unit for C1 from start 1 with the deciding run's exact code. **Required:** the record and the saved settings' hashes equal the pilot's, bit for bit.
2. Re-score through the per-text wrapper. **Required:** guards G4 and G5 pass, and the wrapper's batch value equals the authors' function's.
3. Score the eight shuffled copies of each setting on C1 itself, as the pilot did, to exercise the block code and time it.
4. Kill the container after the first unit and restart it. **Required:** the unit is skipped and G3 passes.
5. Write the sealed files, run the assembler on this one-batch arm, and copy the table to the local side as bytes. **Required:** hashes match.
6. Record: seconds per search step, seconds per scoring pass, seconds from container start to the first search step, seconds per volume commit, and the fingerprint's cost.

The rehearsal's sealed values are own-batch values on a calibration batch. They stay sealed all the same, since the pilot's own-batch shuffles are sealed.

## 9. Spend

### 9.1 A Realistic Estimate

The cost model in `pilot_a_tables.cost` counts search steps and scoring passes only. The pilot gives a billed rate that includes start-up: its question 2 part ran 8 containers with 10,170 function seconds in all and was billed \$19.20, which is **\$6.80 per function hour**. Each pilot container spent about 36 seconds outside searches and scoring. A search took 122.2 seconds.

| Stage | Search seconds | Scoring seconds | Overhead seconds | Total hours |
|---|---|---|---|---|
| Rehearsal | 250 | 20 | 120 | 0.11 |
| Lead, 16 attack containers | 9,776 | 160 | 720 | 2.96 |
| Lead, 16 held-out containers | 9,776 | 17,210 | 1,480 | 7.91 |
| Delta-on, 8 attack containers | 4,888 | 45 | 360 | 1.47 |
| Delta-on, 8 held-out containers | 4,888 | 2,640 | 560 | 2.25 |
| **All** | | | | **14.7** |

Scoring seconds take 0.18 seconds per pass and include the own-batch re-scores this note adds (about 2,200 passes over both arms). Overhead is 45 seconds per container for loading and preparing, plus, for a held-out container, our guesses of 15 seconds to make shuffles and 30 seconds for volume commits.

At \$6.80 per function hour the whole run is about **\$100**. At the \$7.50 upper rate of the signed estimate it is about **\$110**. So the picture is not "\$2 under the cap": with overhead counted, the run fits only if the pilot's billed rate holds, with about \$5 to spare. Scoring is 45 percent of the time, so a scoring pass 10 percent slower than 0.18 seconds uses \$3.50 of that.

### 9.2 The Checks

The run keeps a ledger: each container's function seconds and the billed dollars of each stage, read from the provider. Billing lags; the pilot's first reading was 2.4 percent below the settled figure. So **spent** is the larger of the billed figure times 1.03 and the function hours times \$6.80, and **projected** is spent plus the remaining stages' hours at this run's own measured timings and the larger of \$6.80 and this run's own billed rate.

| Check | When | If projected spend exceeds \$105 |
|---|---|---|
| C0 | After the rehearsal, with its measured timings | Do not start; report |
| C1 | After stage 1 | Do not start stage 2; report |
| C2 | After the first held-out container of stage 2 finishes | Let running containers finish their current unit, then stop; report |
| C3 | After stage 2, before the delta-on arm | Do not start stage 3; report. The lead's units are complete and stay sealed |

A stop goes to the author, as Section 10, item 3 of the signed rules requires. Nothing is trimmed, and no design choice is made except by the author.

## 10. Tests on Made-Up Inputs

These belong in the test suite before the run. Each line names the input and the known answer. The interval's own tests are in the interval specification.

| # | Input | Known answer |
|---|---|---|
| T1 | The tiny model, a small arm run end to end through search, scoring, assembly, and the script's loader, with one batch made of a single repeated token | The table equals a brute-force reference written as plain loops in the test; `carried` differs from `own_A` everywhere |
| T2 | A record with entry $k$ equal to $k$ and settings whose first entry encodes the step | Every saved setting's first entry equals its `step` |
| T3 | The record 0.2, 1.0, 3.5, 1.5, 6.0 | The 2-nat crossing is at $k = 2$ (two-step mean 2.25); the denominator's raw harm is 3.5, not 2.25 |
| T4 | A record that goes 3.9 then 0.5 across the 2-nat level | The crossing is on the down-step and the setting's own harm is 0.5 |
| T5 | A record that jumps from 1 to 40 nats in one step | The 2-, 5-, and 10-nat settings are one setting with three names, each with own harm 40; the script accepts it and prints the overshoot |
| T6 | Starting harms that differ by whole nats between starts | "Large" and the carry-over ratio are unchanged when computed from raw or from added harms; any mismatch of starts changes them by whole nats |
| T7 | The worked example of Section 3.8 | 0.82, 0.50, 0.22 |
| T8 | A setting constant within every stratum | Every shuffled copy equals the setting; shuffled harm equals carried harm; the shuffled ratio is exactly 0; `shuf_moved` is 0 |
| T9 | A "digits" table, $\texttt{carried}[i,j,s] = 1 + 0.1\,i + 0.01\,j + 0.001\,s$ and $\texttt{rec\_H}[j,s,n] = 2 + 0.01\,j + 0.001\,s$ | Every marginal mean in closed form; swapping two axes changes a known digit |
| T10 | One held-out denominator near zero (0.01) | The ratio of means barely moves |
| T11 | Level tables with 10 and with 11 of 80 searches missing on one side; one batch missing at all five starts | The level is read at 10 and undetermined at 11; no crash and no dropped batch without a printed count |
| T12 | A complete table with one cell set to NaN; with one array reshaped; with one block's `block_ids_sha` altered | The script refuses each, naming the check |
| T13 | Per-text harms in which the excluded texts carry all the harm; and an empty exclusion list | A known, very different recomputed ratio; and exactly the main result |
| T14 | The kill-and-restart test of Section 5.1 | Identical table bytes |
| T15 | The sealing capture of Section 7 | No harm in any output |
| T16 | Delta-on on the tiny model | Every saved and shuffled setting has its 24 delta entries equal to 1; the starting harm is that of the start with delta entries at 1 |

## 11. The Delta-On Arm and the Overlapping Texts

### 11.1 The Delta-On Arm

- **Searches.** Attack batches A1 to A8 and held-out batches H1 to H8, starts 9 to 13, with `frozen=A.Frozen.delta_entries(model, 1.0, device)`. The loop writes 1 into the 24 delta entries before step 0 and after every update, so record entry 0 is the harm of the start with the delta entries at 1. That is this arm's starting harm.
- **Scored settings.** `n20`, `n40`, `n80`, `n160`, `n320`, each unshuffled and in 8 shuffled copies: 45 passes per cell, as the cost model assumes. The hook's other settings, including level settings, are saved but not scored; scoring them later needs forward passes only.
- **Shuffles** move rank-one entries only, so the delta entries stay at 1. Guard: every saved and shuffled setting of this arm has all 24 delta entries exactly 1.
- **Its table** has the format of Section 3 with $K_A = K_H = 8$ and $Q = 5$. Its cells match the lead's by batch name and start.
- **Its summary** (the draft's R11), from the two tables: its own carry-over ratio with the signed interval; and the paired share, the mean carried-over added harm in the delta-on table divided by the lead's mean over the same $8 \times 8 \times 5$ cells, each arm's added harm taken from its own starting harm.

### 11.2 The 11 Overlapping Held-Out Texts

`manifest.span_overlap` finds the held-out texts that share a 50-token span with an attack text and keeps only their count. Before the run:

1. Add a function that repeats its computation, on all A and H pools as the manifest did, and returns the flagged texts.
2. Commit the result, for example as `vpd-audit-2/data/manifest/heldout_span_overlap.json`: the span length, the manifest's SHA-256, and for each text its id, pool, and index within the pool.
3. Test that the list has 11 entries, that this equals the manifest's recorded count, and that every text is in a held-out pool.

The assembler turns the list into `excluded_H`. The delta-on table uses the same list restricted to H1 to H8.

**What "recomputed without them" means.** Each held-out batch harm (carried, shuffled, the batch's own settings, its starting harm, its 20-step yardstick) is replaced by the mean of the per-text harms over the texts not excluded, and every reading is recomputed. The searches are not rerun: a held-out batch's own search saw all 128 texts, and its level-crossing steps stay as they were. The script states this beside the recomputed numbers.

## 12. Points Decided Before the Run

1. **Cost (the draft's S5).** With overhead counted, the estimate is about \$100 at the pilot's billed rate and about \$110 at the signed estimate's upper rate (Section 9.1). The checks of Section 9.2 need a rate to project with; we propose the larger of \$6.80 per function hour and this run's own billed rate. The author may want to know now that the delta-on arm is where a shortfall would land.
2. **The per-text readout must not compute the KL twice** (Section 6). This changes how the draft's S1 is implemented, not what it saves.
3. **Guard G6 compares per-text vectors,** where the draft's S2 says "zero carried-over values equal to the attack search's own record". Batch means can coincide by chance; 128 values cannot.
4. **Sealing is wider than the signed rules require** (Section 7): own-batch records and missing counts are sealed too. Keeping to the signed scope was the alternative.
5. **A rehearsal on C1** (Section 8) is not in the draft. It is the only place the sealed-copy step, the volume's commit behaviour, and the modified loop's bit-identity are tested in the cloud before a deciding batch is touched.
6. **The analysis should wait for both arms,** or for the author's ruling on the delta-on arm (Section 7).
7. **The level settings of the delta-on arm are not scored.** The signed cost model assumes this; we note it so that nobody expects a delta-on harm-level table.
8. **Per-position harm is not saved,** as proposed. The project plan's by-position breakdown "from the passes already run" (research log, line 329) will therefore need new forward passes on saved settings when it is taken up.
