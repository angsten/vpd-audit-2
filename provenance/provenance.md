# Provenance of the Released VPD Decomposition: Code, Configuration, and Data

Written for plan 1 of the research log (1 October 2026). One entry per question: the answer, its source, a short verbatim excerpt, and what is uncertain. Every config answer is read from the raw text of a downloaded `final_config.yaml`, never from the authors' config classes.

## How to Read the Citations

**Code** is cited as `path:lines @ commit`. Four checkouts of `goodfire-ai/param-decomp` are cited:

| Short name | Commit | What it is | Where it lives here |
|---|---|---|---|
| **run** | `85c6b702d2accf5bfcf02e52b753acd0fcbcf6c5` | the code that produced `s-55ea3f9b`; package `spd/` | public branch `snapshot/launch-20260225_151714`; a worktree under `.cache/src/pd-85c6b70` (not committed) |
| **control** | `9c802c2d46362c1281b53b7c9da43f6a314599a2` | the code that produced `s-05ef623e`; package `spd/` | public branch `snapshot/launch-20260316_122201`; `.cache/src/pd-9c802c2` |
| **tag** | `74146b555f3eb3cd2bc639c3789fd3b7a099094a` | the `vpd-paper` tag; package `param_decomp/` | `third_party/vpd-audit/third_party/param-decomp` |
| **later** | `5ffc73d79b2dee374c406396efa832023ae5eee7` | `main` on 7 September 2026 (tag `public/2026-09-07`) | `.cache/src/pd-5ffc73d` |

To recreate the three cache worktrees: `git clone https://github.com/goodfire-ai/param-decomp`, `git fetch origin 'refs/heads/snapshot/*:refs/remotes/origin/snapshot/*'`, then `git worktree add --detach <dir> <commit>`.

The earlier project's code is cited as `vpd_audit/<file>:lines @ b6d3bac` (`third_party/vpd-audit`).

**WandB values** are cited as `run_id: field path`. Raw files are in `provenance/runs/<run_id>/`; their SHA-256 are in `provenance/runs/sha256.txt`. Two files are kept in the cache only and quoted: WandB's own `config.yaml` (it carries an author's email and internal host addresses) and `output.log` (21 MB).

**Paper** line numbers refer to a plain-text copy of the paper kept with the research log, which is not public.

---

## (0) Which Code Produced the Runs

**Answer.** Both runs record their commit, and both commits are public as snapshot branches. Neither is `74146b5`.

| Run | Commit | Snapshot branch | Base commit on `dev` | Date |
|---|---|---|---|---|
| `s-55ea3f9b` (released) | `85c6b70` | `snapshot/launch-20260225_151714` | `a8919d4` "Update configs to use new pretrain t-9d2b8f02" | 25 Feb 2026 |
| `s-05ef623e` (no adversarial loss) | `9c802c2` | `snapshot/launch-20260316_122201` | `70b0e27` "Improve autointerp prompt context..." | 16 Mar 2026 |
| `t-9d2b8f02` (target) | `c2c39da` | `snapshot/t-82ce9355` | | 25 Feb 2026 |

**How far from `74146b5`.** The distance is large in history but small in the code these questions touch.
- **History.** The run commits are not ancestors of the tag. The tag's history squash-merged `dev` into `main` ("(dev -> main) App and everything for the VPD paper (#355)", `4b3d2ed`, 5 May 2026), then renamed the package from `spd` to `param_decomp` ("Rename package...", `85ccd3c`, 21 Apr 2026). The merge base of `85c6b70` and `74146b5` is `4c0a470` (23 Feb 2026). It is 511 commits behind the run commit and 14 behind the tag.
- **Code, after normalizing the package name.** These files are identical between run and tag: `routing.py`, `metrics/importance_minimality_loss.py`, `metrics/ce_and_kl_losses.py`, `metrics/ci_l0.py`, `metrics/ci_histograms.py`, `metrics/faithfulness_loss.py`, `models/sigmoids.py`, `utils/component_utils.py`. The single-batch adversary (`metrics/pgd_utils.py`, `metrics/pgd_masked_recon_loss.py`) differs only by a refactor: a `reconstruction_loss` function argument in place of `output_loss_type`, renamed helpers, and the init device taken from `target_out`. The arithmetic of initialization, step, clamp, mask formula, routing, and reduction is unchanged. The model classes the decomposition uses are identical (`SelfAttention`, `TransformerBlock`, `LinearComponents`, `ComponentsMaskInfo`, `make_mask_infos`, and `ComponentModel._components_and_cache_hook`, `calc_causal_importances`, `_apply_sigmoid_to_ci_outputs`, `calc_weight_deltas`); only `ComponentModel.forward`'s batch plumbing changed. The config classes changed the most (see the next paragraph).
- **Config classes.** The run's own config classes parse its `final_config.yaml` with nothing filled in and nothing changed. For both runs, at their own commits, the parsed object equals the raw text field for field. The tag's classes migrate seven fields:
  - `lr_schedule` and `grad_clip_norm_*` become `components_optimizer` and `ci_fn_optimizer`;
  - `output_loss_type` is dropped as deprecated;
  - `pretrained_model_output_attr: idx_0` becomes `output_extract: 0`;
  - `init_spd_checkpoint` is renamed `init_pd_checkpoint`;
  - the `PersistentPGDReconLoss` entry gains defaults `start_frac: 0.0` and `n_samples: 1`;
  - `task_config` gains `dataset_seed: null`;
  - the five null global-reverse-residual keys are dropped.
  
  None of these touches the evaluation adversary or the labels.

**Every code answer below is given at the run's own commit (`85c6b70`).** Where the tag differs in a way that matters, it is said.

**Sources.**
- `s-55ea3f9b: commit` = `85c6b702d2accf5bfcf02e52b753acd0fcbcf6c5`, in `provenance/runs/s-55ea3f9b/run_info.json`. The same commit is in WandB's `config.yaml` (cache): `_wandb.value.e.<writer>.git.commit: 85c6b702...`, with `remote: /mnt/polished-lake/home/braun/spd`.
- `s-05ef623e: commit` = `9c802c2d46362c1281b53b7c9da43f6a314599a2`. `t-9d2b8f02: commit` = `c2c39dad492ee4f726d2eaeb5641316e532ecf31`.
- The run tags match the branch names: `s-55ea3f9b: tags` include `launch-20260225_151714`; `s-05ef623e: tags` include `launch-20260316_122201`.
- `git ls-remote https://github.com/goodfire-ai/param-decomp` lists `85c6b70...	refs/heads/snapshot/launch-20260225_151714` and `9c802c2...	refs/heads/snapshot/launch-20260316_122201`.
- `spd/scripts/run.py:84 @ run`: `snapshot_branch, commit_hash = create_git_snapshot(snapshot_id=launch_id)`. The snapshot commit is the working tree the job checked out.

**What the snapshot commits add over their base.** `85c6b70` vs `a8919d4`: `spd/experiments/lm/pile_llama_simple_mlp-4L.yaml` (22 lines), plus three scripts, among them `scripts/shuffle_and_reupload_dataset.py`, which made the tokenized split (see (k)). `9c802c2` vs `70b0e27`: `spd/experiments/lm/pile_llama_simple_mlp-4L-no-adv.yaml` (new), `spd/registry.py`, `spd/scripts/sweep_seeds_3.yaml`, and a figure script.

**Not found.** Neither run lists `wandb-metadata.json` or `diff.patch` among its files, and the API returns empty metadata (`provenance/runs/*/wandb_metadata.json` = `{}`). The same metadata sits inside WandB's `config.yaml` under `_wandb.value.e`, and that copy is the one quoted here.

**Uncertain.** None for `s-55ea3f9b` and `s-05ef623e`: the commits are recorded by the runs and public.

---

## Appendix C.1: Files F1 to F13

Read at the run commit; the tag's path is given where it differs.

| # | File (run) | Finding |
|---|---|---|
| F1 | `spd/configs.py` | `PGDConfig` (408-412): `init`, `step_size`, `n_steps`, `mask_scope`, **all required, no defaults**. `PGDInitStrategy = Literal["random", "ones", "zeroes"]` (403). `MaskScope = Literal["unique_per_datapoint", "shared_across_batch"]` (405). `PGDReconLossConfig` (415-416) has **no `routing` field**. `PGDReconSubsetLossConfig` (419-423) and `PGDMultiBatchReconSubsetLossConfig` (441-445) have `routing`, defaulting to `UniformKSubsetRoutingConfig()`. `PGDMultiBatchConfig` (430-435): `init`, `step_size`, `n_steps`, `gradient_accumulation_steps`. Routing configs: `UniformKSubsetRoutingConfig` (357-358, no fields) and `StaticProbabilityRoutingConfig` (361-363, field `p`). `use_delta_component` is a **top-level** `Config` field (770-774, default `True`). The evaluation metric list is the top-level `eval_metric_configs` (850-856), a list discriminated by `classname`. The loss configs are also run as evaluation metrics unless already listed (`run_spd.py:100-113`). The output loss type is the top-level `output_loss_type` (785-788). There is **no field selecting the causal importance output for masks**: the masks use `lower_leaky` in code (F10). Tag: `param_decomp/configs.py:426-463`, same fields. |
| F2 | `spd/metrics/pgd_utils.py` | See (a) to (d) and (q). Shape under `shared_across_batch`: `singleton_batch_dims = [1 for _ in batch_dims]; shape = torch.Size([*singleton_batch_dims, mask_c])` (35-36), with `mask_c = module_c + 1` when the delta component is used (29); `batch_dims = (B, T)` for language models. Init (304-315): `random` gives `torch.rand(shape, device=device)`, `ones` gives `torch.ones`, `zeroes` gives `torch.zeros`. Loop (42-66): `n_steps` iterations of `loss = sum_loss / n_examples`, gradient, `all_reduce(g, AVG)` across processes, `add_(step_size * grad.sign())`, `clamp_(0.0, 1.0)`. No optimizer state, no warmup. The returned value is one more forward after the last step (66). Mask: `ci + (1 - ci) * source` (318-338) on `ci.lower_leaky`. Unrouted modules: not applicable, since `PGDReconLoss` routes to all. KL: summed over positions, divided by B·T (223-227). Multi-batch path (135-200, 232-301): one shared source; gradients of each microbatch's *summed* loss all-reduced and summed over `gradient_accumulation_steps` microbatches drawn from a fresh `create_data_iter()` at every step. `unique_per_datapoint` is supported (31-33): shape `(B, T, C+1)`, no all-reduce. |
| F3 | `spd/metrics/pgd_masked_recon_loss.py`, `pgd_masked_recon_subset_loss.py` | `PGDReconLossConfig` builds class `PGDReconLoss` (`spd/eval.py:230-237`), which routes with `AllLayersRouter()` (`pgd_masked_recon_loss.py:77`) and passes `weight_deltas if self.use_delta_component else None` (74). `PGDReconSubsetLossConfig` builds `PGDReconSubsetLoss` with `get_subset_router(routing)` (`eval.py:238-246`). Tag: same mapping (`param_decomp/eval.py:248`, `pgd_masked_recon_loss.py:75-77`). |
| F4 | `spd/metrics/ppgd_eval_losses.py` | `PPGDReconEval` evaluates with the *persistent training* sources (`get_ppgd_mask_infos`). It is not the metric behind the paper's table. It is not in the run's `eval_metric_configs`, and `evaluate()` drops persistent-PGD loss configs from evaluation (`spd/eval.py:340-345`). Routing is that of the persistent state's config. |
| F5 | `spd/routing.py` | See (f). |
| F6 | `spd/eval.py`, `spd/run_spd.py` | See (m). One batch per evaluation (`n_eval_steps: 1`); the logged value is that batch's global mean over positions, not an average over batches. |
| F7 | `spd/experiments/lm/pile_llama_simple_mlp-4L.yaml @ run` | Identical to the run's `final_config.yaml` except that two evaluation entries omit `coeff: null`, which is the class default. It also holds a **commented-out** `PersistentPGDReconSubsetLoss` block with `routing: uniform_k_subset`, `scope: repeat_across_batch`, `n_sources: 8`, lr 0.1 (lines 56-73), above the live `PersistentPGDReconLoss` (74-89). Tag (`param_decomp/experiments/lm/pile_llama_simple_mlp-4L.yaml`): the same values in the tag's schema (`components_optimizer`, `ci_fn_optimizer`, `output_extract`, `wandb_project: param-decomp`); the same 20-step `PGDReconLoss` (lines 115-121). |
| F8 | whole repository | **The code that produced the 20/40/80/160/320-step table is not in the public repository.** Searched `git grep` at run, control, tag, `origin/dev`, and later, for `160, 320`, `[20, 40, 80`, `n_steps_list`, `pgd_steps`, `40.22`, `25.256`, `0.8280`, `67.2449`, and `n_adv_steps`. Searched `git log --all -S"25.256"` and `-G` for `n_steps` of 160 or 320 over every public ref (heads, tags, 1,744 `refs/runs/*`). The only hits are the paper text vendored into `papers/`, an unrelated 50-step ablation script, and the later code's ladder (first at `5ffc73d`, 7 Sep 2026). |
| F9 | `spd/utils/general_utils.py:209-246` | KL(P_target ‖ Q_masked): `log_q = log_softmax(pred)`, `p = softmax(target)`, `F.kl_div(log_q, p, reduction="none").sum(-1)`, then mean over all batch and sequence positions, or summed and divided by B·T in the PGD and stochastic paths. The direction matches `vpd_audit/metrics.py:22-34 @ b6d3bac`. |
| F10 | `spd/models/component_model.py:634-688`, `models/sigmoids.py`, `models/components.py:101-142` | Masks use `lower_leaky` everywhere: `pgd_masked_recon_loss.py:73`, `losses.py:92-192`, `eval.py`, `ce_and_kl_losses.py`. The CI transformer's attention is bidirectional: `scaled_dot_product_attention(q, k, v, dropout_p=0.0, is_causal=False)` (components.py:135-137), docstring "Multi-head bidirectional self-attention with RoPE". |
| F11 | `param_decomp/app/backend/optim_cis.py @ tag` (also `spd/app/backend/optim_cis.py @ run`, an older version) | See (o). |
| F12 | `spd/experiments/lm/lm_decomposition.py`, `spd/data.py` | Dataset `danbraunai/pile-uncopyrighted-tok-shuffled`, split `val`, column `input_ids`, streamed. The tokenizer `EleutherAI/gpt-neox-20b` is named in the config but unused for an already tokenized set. Evaluation loader seed `config.seed + 1` = 1, `buffer_size: 1000` shuffle, rows cut to 512. See (m). |
| F13 | `spd/persistent_pgd.py`, run config | See (f) and the training-adversary row in (g). Scope `per_batch_per_position`: sources of shape `(B_local, T, C+1)` per process, **not synchronized** across processes (137, 158-168, 175-176). Adam, β₁ 0.5, β₂ 0.99, ε 1e-8, lr 0.01, constant after a 2.5 % warmup (`get_scheduled_value`), 2 warmup steps plus the outer step, so 3 source updates per training step (209-225, `run_spd.py:285-325`). Clamp to [0, 1] after each update (182-193). **Routing: `AllLayersRouter`**, all 24 matrices at every position (254-262). The delta component's source is the last entry; its mask is the raw source (290-298). |

## Appendix C.2: Config Fields for Both Runs

From the raw text (`provenance/runs/<run>/final_config.yaml`, cited by YAML line). `vpd_audit_2/run_config.py` asserts every value listed for `s-55ea3f9b`.

| Field | `s-55ea3f9b` | `s-05ef623e` |
|---|---|---|
| Evaluation adversary entries | one: `classname: PGDReconLoss`, `init: random`, `step_size: 0.1`, `n_steps: 20`, `mask_scope: shared_across_batch`, `coeff: null`, no routing field (lines 116-121) | identical (lines 100-105) |
| Evaluation batch size, number of batches | `eval_batch_size: 128` (89), `n_eval_steps: 1` (91) | same |
| Evaluation data | `dataset_name: danbraunai/pile-uncopyrighted-tok-shuffled`, `eval_data_split: val`, `streaming: true`, `buffer_size: 1000`, `shuffle_each_epoch: true` (128-138); no seed field (code: `seed + 1`) | same, plus `dataset_seed: null` (task_config, the field exists at 9c802c2) |
| Sequence length | `max_seq_len: 512` (130) | same |
| `use_delta_component` (top level) | `true` (42) | `true` |
| Output loss type | `output_loss_type: kl` (74) | same |
| Stochastic reconstruction | `classname: StochasticReconSubsetLoss`, `coeff: 0.5`, `routing: {type: uniform_k_subset}` (52-55); `sampling: continuous` (25), `n_mask_samples: 1` (6) | same |
| Coefficients | minimality 0.0002, stochastic 0.5, `PersistentPGDReconLoss` 0.5, `FaithfulnessLoss` 1e7 | minimality 0.0002, stochastic 0.5, faithfulness 1e7; **no adversarial entry** (absent, not 0) |
| Minimality | `pnorm: 2.0`, `beta: 0.5`, `p_anneal_start_frac: 0.0`, `p_anneal_final_p: 0.4`, `p_anneal_end_frac: 1.0`, `eps: 1.0e-12` (44-51) | same |
| Precision | `autocast_bf16: true` (5) | same |
| CI function | `ci_config: {mode: global, fn_type: global_shared_transformer, simple_transformer_ci_cfg: {d_model: 2048, n_blocks: 8, mlp_hidden_dim: [8192], attn_config: {n_heads: 16, max_len: 512, rope_base: 10000.0}}}`; `sigmoid_type: leaky_hard` (7-26) | same |
| Training adversary | the `PersistentPGDReconLoss` block (56-71): Adam β₁ 0.5, β₂ 0.99, ε 1e-8, lr schedule `{start_val: 0.01, warmup_pct: 0.025, final_val_frac: 1.0, fn_type: constant}`, `scope: per_batch_per_position`, `use_sigmoid_parameterization: false`, `n_warmup_steps: 2`, no routing field | none |
| Steps, batch | `steps: 400000`, `batch_size: 64` | same |
| Checkpoint | `model_400000.pth`, 2,908,595,703 bytes, WandB md5 `71cXJbSLGFAJpQHvvEIs5g==`, SHA-256 in `results/plan1_smoke/smoke.json` | `model_400000.pth`, 2,908,595,703 bytes, WandB md5 `f+GfLeC1fvx7GE231yE8iQ==`; not downloaded here; SHA-256 `04f0d2effdf165d7eb7f7c1b43ec41e39b8c7b0116df15ca6c312a32ab10e9e2` per the earlier project's volume manifest (`vpd-audit-cache:/artifacts/manifest.json`) |

**The paper's coefficient table (lines 2189 to 2195)** is confirmed: Delta-L2 1e7, stochastic 0.5, adversarial 0.5, minimality 2e-4 with β 0.5, which is the frequency term's 1e-4.

**Summary values of `s-05ef623e` at step 400,000** (`provenance/runs/s-05ef623e/summary.json`):

| Field | Value |
|---|---|
| `eval/l0/0.0_total` (labels > 0 per position; metric threshold `ci_alive_threshold: 0.0`) | 72.09550476074219 |
| `eval/loss/StochasticReconSubsetLoss` | 0.2633381187915802 |
| `train/loss/StochasticReconSubsetLoss` | 0.2580103874206543 |
| `eval/loss/PGDReconLoss` | 55.95696640014648 |
| `eval/ce_kl/ce_difference_ci_masked` | 4.464356422424316 |
| `eval/ce_kl/kl_ci_masked` | 4.482043266296387 |

The cross-entropy difference is cross-entropy under labels as masks, minus the target's. **Alive components** are not logged as a number; `CIMeanPerComponent` and `ComponentActivationDensity` log images only, so this is not determined from the logs.

**The released run's corresponding values** (`provenance/runs/s-55ea3f9b/summary.json`):

| Field | Value |
|---|---|
| `eval/l0/0.0_total` | 201.45314025878903 |
| `eval/loss/StochasticReconSubsetLoss` | 0.23516137897968292 |
| `eval/loss/PGDReconLoss` | 0.6522506475448608 |
| `eval/ce_kl/kl_ci_masked` | 0.34315478801727295 |
| `eval/ce_kl/kl_zero_masked` | 66.8992919921875 |

**The four other seed decompositions** (paper line 2245 links the saved WandB view `goodfire/spd?nw=n9l0amrrudc`, which the API cannot read). The likely runs are those of launch `launch-20260311_110438`, named `pile_llama_simple_mlp-4L-seed-<k>`, all at commit `e577c4b4`:

| Run | Seed | Name |
|---|---|---|
| `s-e8bde534` | 0 | `pile_llama_simple_mlp-4L-seed-0` |
| `s-73d2385c` | 1 | `pile_llama_simple_mlp-4L-seed-1` |
| `s-aac60aec` | 2 | `pile_llama_simple_mlp-4L-seed-2` |
| `s-2d14f6c0` | 3 | `pile_llama_simple_mlp-4L-seed-3` |
| `s-6a33629b` | 4 | `pile_llama_simple_mlp-4L-seed-4` |

Found by `api.runs("goodfire/spd", filters={"tags": {"$in": ["pile_llama_simple_mlp-4L"]}})`. Not downloaded.

**Uncertain.** Whether the view lists exactly these five runs. Note that its seed-0 member is a re-run (`s-e8bde534`), not the released `s-55ea3f9b`. Also in that listing: `p-537e31f3` ("jose-replica", 1 June 2026), trained at the tag commit `74146b55`.

## Appendix C.4: The Evaluation Adversary

| | Answer | Source (run) |
|---|---|---|
| **(a) Routing** | **All 24 matrices are masked at every position.** The run's only evaluation adversary is class `PGDReconLoss` (final_config.yaml line 121), which routes with `AllLayersRouter`; its `get_masks` returns `"all"`, and `make_mask_infos` then sets every module's `routing_mask = "all"`. | `metrics/pgd_masked_recon_loss.py:39-41,77`: `"""Recon loss when masking with adversarially-optimized values and routing to all component layers."""` ... `router=AllLayersRouter()`; `routing.py:36-39`; `models/components.py:760`. Tag: the same (`pgd_masked_recon_loss.py:40,77`). |
| **(b) Source scope** | **One source per component, shared across the whole batch and every position, and across processes.** Shape `(1, 1, C_l + 1)`; initialized on rank 0 and broadcast; gradients averaged over processes before the sign. | `pgd_utils.py:34-37`: `singleton_batch_dims = [1 for _ in batch_dims]` / `shape = torch.Size([*singleton_batch_dims, mask_c])` / `source = broadcast_tensor(_get_pgd_init_tensor(...))`; 53-58 `all_reduce(g, op=ReduceOp.AVG)`; 76 `v.expand(*batch_dims, -1)` |
| **(c) Delta components** | **Optimized.** Each matrix's source has one extra entry, and the delta component's mask is that raw source, with no label floor. | `pgd_utils.py:29` `mask_c = module_c if weight_deltas is None else module_c + 1`; 82-86 `(weight_deltas[k], expanded_adv_sources[k][..., -1])`; `pgd_masked_recon_loss.py:74` `weight_deltas=weight_deltas if self.use_delta_component else None`; `use_delta_component: true` (config line 42) |
| **(d) Starting point** | **Uniform random in [0, 1)**, from `torch.rand` on the global CUDA generator of rank 0. The components then start at `g + (1 − g)·U`; the delta components at `U`. | config `init: random` (line 117); `pgd_utils.py:309-311` `case "random": return torch.rand(shape, device=device)` |

**Step and reduction.** 20 steps of `source += 0.1 · sign(∇ mean-KL)`, each followed by a clamp to [0, 1]. The reported value is the KL after the 20th step, from a 21st forward pass (`pgd_utils.py:47-66`). The KL is summed over the vocabulary, averaged over all B·T positions, and summed over processes before dividing (`pgd_masked_recon_loss.py:83-87`).

## Appendix C.5 Item 1: The First Post's Masked Passes (`vpd-audit` at `b6d3bac`)

- **Delta components.** The first post's measurements ran with the delta components **excluded**: no delta term is added, which equals a delta mask of 0. Every grid cell the post's numbers come from has `delta == "excluded"`; examples are `vpd_audit/cells.py:168,212,225-232,280,320` and `vpd_audit/grid.py:473-477`. "Included" runs only in the hard-delete and code-edit families (`cells.py:234,475,479`). The reference "own explanation" 0.3417 is condition `importances`, with delta excluded (`vpd_audit/reference.py:61`): `Condition("importances", "importances", "excluded", False, True, paper_ce=2.99)`. Excluded means `make_mask_infos(masks)` with no `weight_deltas_and_masks` (`vpd_audit/masks.py:148-149`).
- **All 24 matrices at every position: yes.** `wrap_masks` asserts that every decomposed module has a mask of shape (B, T, C_l) (`masks.py:139-147`), and routing stays at the default `"all"`. Its docstring: "a module omitted from the mask dictionary silently runs the target's weights (`component_model.py` line 396)".
- **KL reduction.** `F.kl_div(log_softmax(masked.float()), softmax(target.float()), reduction="none").sum(-1)` per position, in float32 sub-chunks of 8 sequences (`vpd_audit/metrics.py:22-34`). The mean is over the 512 positions of each text, then over texts. The direction is KL(P_target ‖ Q_masked).
- **Dtype.** bf16 autocast on CUDA for both the labels and the masked forward (`vpd_audit/importances.py:37-44`; `grid.py:48` `precision: str = "bf16"`). The labels are float32 values under autocast (`g_dtype: torch.float32` in the label-cache metadata, (n)). Batches of 64 sequences, labels in chunks of 32 (`constants.py:5`).

---

## (e) The Step-Size Schedule of the Paper's 40- to 320-Step Rows

**Answer: not determined from the paper's code or the run.** No primary source from the paper's time says how those rows were run.
1. **The run's evaluation metric list** has exactly one adversary: 20 steps at step size 0.1 (final_config.yaml lines 116-121). `n_steps` and `step_size` are required fields with no defaults (`spd/configs.py:408-412`).
2. **The run's logged metric keys** have no value at 40, 80, 160, or 320 steps. The only adversary key is `eval/loss/PGDReconLoss`, logged 401 times, at every 1,000 steps (`provenance/runs/s-55ea3f9b/summary_keys.txt`, `loss_history.csv`).
3. **No script producing the table** is in any public commit (F8).

**What the logs show, and what they leave open.** The paper's 20-step value 0.8280 matches **no** logged evaluation step of `s-55ea3f9b`: the nearest is 0.8294 at step 147,000. The 40- to 320-step rows have no logged counterpart at all. That is an observation about this run's logs only; it does not say where the table was computed. Two hypotheses remain open:
- a separate evaluation of this run's checkpoint, outside its training loop;
- an evaluation of a sister run, for example one of the five seed runs listed under C.2. The seed-0 member there is the re-run `s-e8bde534`, not `s-55ea3f9b`.

Nothing found here decides between them.

**Later code only, which is weak evidence.** At `later` (`5ffc73d`, 7 Sep 2026), `param_decomp/experiments/lm/configs/pile_llama_simple_mlp-4L.yaml:51-108` runs `SlowPGDReconLoss` at `n_steps` 40, 80, 160, 320, 640, and 1,280, all with `step_size: 0.1`, beside the 20-step probe. `docs/skill.md:133` there reads: "The canonical 4L block carries a ladder of them (`PGDReconLoss_40step` … `PGDReconLoss_1280step`, powers of two, `step_size: 0.1`) ... every probe in one pass shares the random init". This config first appears in public history at `5ffc73d`. The newer reference run `p-8383f5e5` itself logged only the 20-step probe (see (l)).

**For plan 2 of the research log.** The paper's own heuristic (line 2100) points the other way, toward step size ≈ 2/n. Gate G1 has to decide by experiment.

## (f) Routing of Each Training Term

| Term | Class in the raw config | Routing in code (run) | What is drawn, at what level |
|---|---|---|---|
| Stochastic reconstruction | `StochasticReconSubsetLoss`, `routing: {type: uniform_k_subset}` (lines 52-55) | `UniformKSubsetRouter` via `get_subset_router` (`metrics/stochastic_recon_subset_loss.py`, `losses.py:133-144`, `routing.py:135-140`) | **Per position.** `mask_shape = (B, T)`. For each (sequence, position), k is uniform on {1, …, 24} (`torch.randint(1, 25, size=(B, T))`), then a uniformly random k-subset of the 24 matrices (`rand_perm` over the module axis), drawn independently at each position (`routing.py:97-132`). Each matrix is routed with probability 12.5/24 on average. |
| Adversarial reconstruction | **`PersistentPGDReconLoss`** (line 71), with no routing field | **`AllLayersRouter`**, all 24 matrices at every position (`persistent_pgd.py:254-262`: `case PersistentPGDReconLossConfig(): return AllLayersRouter()`) | Nothing drawn |

**Paper line 2169 is wrong for the adversarial term.** The text: "Stochastic and adversarial reconstruction losses both use uniform-$k$-subset routing". The released run's adversarial term is `PersistentPGDReconLoss`, not the subset class, and routes to all matrices. The subset variant is present but commented out in the run's experiment YAML (F7). The stochastic term is subset-routed as the paper says.

**What an unrouted matrix receives: the target weights**, at that position. `models/component_model.py:535-539 @ run`: `final_out = components_out if mask_info.routing_mask == "all" else torch.where(mask_info.routing_mask[..., None], components_out, output)`. `output` is the target module's own output. Tag: `component_model.py:474-476`, the same.

## (c), Expanded: The Delta Components

- **Where `use_delta_component` is set.** The top-level field (final_config.yaml line 42: `use_delta_component: true`; class field `spd/configs.py:770-774`). It is not part of any metric block. The evaluation metrics read `run_config.use_delta_component` (`spd/eval.py:234` for `PGDReconLoss`).
- **The delta mask under the evaluation adversary: the raw source, with no label floor.** `m_Δ = s_Δ`, where s_Δ is the source's last entry, in [0, 1] after the clamp. The component masks are `g + (1 − g)·s`. `pgd_utils.py:82-86`: `weight_deltas_and_masks = {k: (weight_deltas[k], expanded_adv_sources[k][..., -1]) ...}`; `adv_sources_components = {k: v[..., :-1] ...}`. The delta's output is `m_Δ · (x · ΔWᵀ)` (`models/components.py:626-632`).
- **Elsewhere.** Under the stochastic term, the delta mask is a fresh uniform per position (`utils/component_utils.py:30-37`). Under the persistent training adversary, it is the persistent source's last entry (`persistent_pgd.py:294-298`). Under `CEandKLLosses` (ci-masked, rounded, unmasked, zero), the delta is **excluded** (`make_mask_infos(ci)` without deltas, `metrics/ce_and_kl_losses.py:115-154`). So the logged `kl_zero_masked` zero-ablates all 24 matrices.

## (g) The Minimality Term in Code

**Form** (`spd/metrics/importance_minimality_loss.py @ run`, identical at the tag):

```
s^l_c = Σ_{b,t} (g_upper^l_{b,t,c} + eps) ** p          # _importance_minimality_loss_update, 79-86
L     = Σ_l Σ_c [ s^l_c / n  +  beta · (s^l_c / n) · log2(1 + s^l_c · world_size) ]   # _compute, 107-114
```

Here n is the number of (b, t) positions the sums were taken over. This is the paper's fused form (lines 2173-2182) when `world_size = 1`.

| Quantity | Value | Source |
|---|---|---|
| λ (coefficient) | 0.0002 | config line 44 |
| β | 0.5 | config line 47 |
| ε | 1e-12, added inside the power: `(ci_upper_leaky + eps) ** pnorm`. g_upper ≥ 0, so no absolute value is needed. | config line 51; code line 82 |
| p | linear from `pnorm: 2.0` at `p_anneal_start_frac: 0.0` to `p_anneal_final_p: 0.4` at `p_anneal_end_frac: 1.0`, in `current_frac_of_training = step / steps` (`run_spd.py:301`; `_get_linear_annealed_p`, 13-49). The last gradient step is step 399,999, at p = 0.400004. Step 400,000 is logged but not stepped (`run_spd.py:420`), at **p = 0.4 exactly**. | |
| Sum per process or across | **Training: per process.** `importance_minimality_loss()` sums over the local batch only, and the log term multiplies the local sum by `world_size` "to estimate the global sum" (99-105, 138-145). The logged training value is the average over processes of the per-process losses (`run_spd.py:333`, `avg_metrics_across_ranks`). **Evaluation: across processes.** The metric all-reduces the sums and computes with `world_size=1` (214-225). | |
| B and T it sees | **Training: B = 4, T = 512 per process** (64 global ÷ 16 processes, (i)), so n = 2,048 and the log term uses 16·s_local. **Evaluation: B = 128, T = 512 globally** after the all-reduce, n = 65,536. | `experiments/lm/lm_decomposition.py:90-99` |
| The function to call for prices | `_importance_minimality_loss_update` and `_importance_minimality_loss_compute` (or the wrapper `importance_minimality_loss`, which reads the world size from the distributed state). In the tag the path is `param_decomp/metrics/importance_minimality_loss.py:52-145`. | |
| Which CI output | **`upper_leaky`**: `losses.py:68-78` `ci_upper_leaky=ci.upper_leaky`; metric update line 198. The masks use `lower_leaky`. Upper-leaky = `clamp(x, 0, 1)` for x ≤ 1, `1 + 0.01(x − 1)` for x > 1 (`models/sigmoids.py:54-55`). Lower-leaky = `clamp(x, 0, 1)` in the forward pass; its leak is only in the backward pass (17-39). | |
| Validator | `ImportanceMinimalityLossConfig.migrate_old_fields` sets `beta` to 0.0 with only a log warning **if the field is absent** (`spd/configs.py:350-353`; tag `configs.py:369-371`). The raw text has `beta: 0.5`, so it does not fire. `output.log` has no "beta not in" warning. | |

**The final loss terms at full precision, and λ solved from them** (`provenance/runs/s-55ea3f9b/summary.json`, step 400,000):

| Term | Value |
|---|---|
| `train/loss/total` | 24.621112823486328 |
| `train/loss/ImportanceMinimalityLoss` | 1110.5545654296875 |
| `train/loss/StochasticReconSubsetLoss` | 0.23176375031471252 |
| `train/loss/PersistentPGDReconLoss` | 0.583663284778595 |
| `train/loss/FaithfulnessLoss` | 2.399128788965754e-06 |

The total is formed as Σ coeff · term (`run_spd.py:309-315`). Then:

λ = (total − 0.5·S − 0.5·P − 1e7·F) / M = 0.22211141628213227 / 1110.5545654296875 = **2.0000045e-4**.

One float32 ulp of the total moves this by ±1.7e-9. Over all 2,001 logged training steps the median is 2.00000004e-4, with 1st to 99th percentile [1.99997e-4, 2.00004e-4]. The control `s-05ef623e` gives 1.99999e-4. The paper's rounded table values (lines 2219-2226) give 1.927e-4.

**The paper's training and evaluation tables match no single logged step of `s-55ea3f9b`.**
- Its 1102.0 matches only step 175,000 (1101.96, at p ≈ 1.3). Its 0.5733 matches steps 273,400, 317,000, and 323,000. Its 0.2419 matches several other steps. None is step 400,000, and no one step matches all four.
- Likewise for evaluation: its `PGDReconLoss` 0.9268 matches only step 300,000 (0.92676), whose other evaluation values (0.2453, 0.4069, 0.8322) are not the paper's (0.2381, 0.4130, 0.8464).

This is an observation about this run's logs. It leaves the same two hypotheses open as the adversarial table in (e): the tables were computed separately from this run's checkpoint, or from a sister run such as a seed run (C.2). The single match of 1102.0 at step 175,000, one of 2,001 logged steps, is weak evidence either way.

Source: `provenance/runs/s-55ea3f9b/loss_history.csv`. **For plan 2 of the research log,** the logged final values of this run are the ones known to be taken at p = 0.4, on this run's weights.

**Pre-sigmoid values.** The released run logged **histogram images** of the pre-sigmoid values per module, from `CIHistograms` (configured `n_batches_accum: 1`, line 95-96; `spd/metrics/ci_histograms.py:15-61` plots `ci.pre_sigmoid`). They are `media/images/eval/figures/causal_importance_values_pre_sigmoid_<step>_<hash>.png`, 41 files at steps 0 and every 10,000 to 400,000 (`wandb_file_listing.json`). These are PNG only; no numeric values or summaries are logged. The tag has the same metric (identical file).

## (h) Labels at Evaluation

- **Deterministic.** `calc_causal_importances` takes `sampling`, which is `"continuous"` from the config (line 25). Only `"binomial"` perturbs the input of the lower-leaky function: `1.05·x − 0.05·rand` (`models/component_model.py:667-672`). The CI transformer has no dropout (`dropout_p=0.0`, components.py:136). `evaluate()` calls it with `sampling=run_config.sampling` (`eval.py:369-373`).
- **Output feeding the masks: `lower_leaky`** (F10).
- **A label of exactly zero is well defined.** Lower-leaky's forward pass is `torch.clamp(x, min=0, max=1)` (`sigmoids.py:23`), so every pre-sigmoid value ≤ 0 gives exactly 0.0. Labels never go below zero on the forward pass, and never above one.
- **Uncertain.** A label depends on the whole 512-token text, future tokens included (bidirectional attention, F10), but not on other texts in the batch.

## (i) Processes

**`s-55ea3f9b`: 16 processes, 2 nodes × 8 H200, for training and evaluation alike** (evaluation runs inside the training loop, on the same processes). Inferred from WandB's `config.yaml` (cache), `_wandb.value.e.<writer>`:
- `gpu_count: 8`; `slurm.job_num_nodes: "2"`, `nnodes: "2"`, `ntasks: "2"`, `ntasks_per_node: "1"`, `gpus_per_node: "8"`;
- `executable: /tmp/spd/workspace-311644_1-node0/.venv/bin/python`.

The workspace path is the pattern of the launcher's multi-node branch only: `spd/utils/compute_utils.py:97-118 @ run`, `work_dir = "/tmp/spd/workspace-${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}-node$SLURM_PROCID"`, with `torchrun --nnodes={n_nodes} ... --nproc_per_node={GPUS_PER_NODE}` and `GPUS_PER_NODE = 8` (17). The world size itself is not logged; `output.log` starts after `wandb.init` and has no "Distributed state" line.

**`s-05ef623e`: 8 processes on 1 node** (`slurm.nnodes: "1"`, `gpus_per_node: "8"`, single-node workspace path `/tmp/spd/workspace-spd-24h0m-346633_1`). `--gpus-per-node=8` is requested only when `dp = 8` (`compute_utils.py:176-185 @ control`), which launches `torchrun --standalone --nproc_per_node=8`.

| Question | Answer | Source (run) |
|---|---|---|
| Evaluation batch of 128, training batch of 64: global or per process? | **Global, divided across processes**: 8 evaluation and 4 training texts per process. | `lm_decomposition.py:90-99` `train_rank_batch_size = config.batch_size // world_size`; 131-138 `eval_rank_batch_size = config.eval_batch_size // world_size`. Config docstring: "Total batch size (may be divided across multiple devices)" (configs.py:793-796). |
| Evaluation adversary's source synchronized? | **Yes.** Broadcast from rank 0 at init; gradients averaged before every sign step. One source for all 128 texts. | `pgd_utils.py:37, 53-58` |
| Minimality sum per process or across? | **Training: per process** (4 × 512 positions, log term on 16 × local sum). **Evaluation: across** (all-reduced, world size 1). | (g) |

**What the world size changes here.**
1. **The training minimality value** (logged 1110.55), through both the per-process mean and the logarithm of 16·s_local.
2. **Which rows each process sees.** The training set has 2,021 files, so it is sharded by file. The validation set has 12 files, fewer than 16, so it is filtered by stream index modulo 16 (`data.py:196-204`), before the buffered shuffle.
3. **The persistent training sources**, shape (4, 512, C+1) per process.
4. **The evaluation adversary, only by floating-point order.** The gradients are averaged, so the sign step equals that of one process on all 128 texts up to summation order, but each forward runs on 8 texts.

## (j) Multi-Batch Adversary

**None.** The released run configures no `PGDMultiBatchReconLoss` or `PGDMultiBatchReconSubsetLoss` (final_config.yaml lines 94-121; asserted in `vpd_audit_2/run_config.py`). Its logged keys have none (`summary_keys.txt`). In code, that adversary reads the **training** loader: `run_spd.py:133-138` `create_pgd_data_iter`: `train_loader.generator.manual_seed(config.seed); return iter(train_loader)`, passed to `evaluate_multibatch_pgd` (`run_spd.py:362-369`, `eval.py:398-435`).

## (k) The Data

| Field | Value | Source |
|---|---|---|
| Dataset revision | `danbraunai/pile-uncopyrighted-tok-shuffled` @ `6f141f6e4edc32fea842f2ece0d3477b15c3dc90` (last modified 2026-02-26) | HF API; `provenance/data/data_check.json: revisions` |
| Features | one column, `input_ids: list<int32>` | parquet schema; dataset card `dataset_info.features` |
| Rows (`val`) | **2,775,651**, in 12 parquet files (231,305 rows in the first three, 231,304 in the rest; 5 row groups each) | parquet metadata; card `num_examples: 2775651` |
| Tokens per row | **513** | card: "Each row contains a single `input_ids` column (513 int32 values)"; all 2,048 first-post rows and 16 sampled rows have 513 |
| Tokenizer | `EleutherAI/gpt-neox-20b` @ `c292233c833e336628618a88a648727eb3dff0a7`, EOS `<\|endoftext\|>` = id 0 | card; run config `tokenizer_name` |
| Document or subset field | **None** in the split | parquet schema |

**How the split was built.** The card and `scripts/shuffle_and_reupload_dataset.py @ run` describe three public stages:
1. `monology/pile-uncopyrighted` split `"train"` becomes `danbraunai/pile-uncopyrighted` @ `188e502a`: "last 100K rows → test, preceding 1M → val, rest → train". The `"train"` split resolves to `train/00…29.jsonl.zst` only; monology's `val.jsonl.zst` and `test.jsonl.zst` are not in it (`data_check.json: monology_train_split_files`).
2. That split becomes `danbraunai/pile-uncopyrighted-tok` @ `234360bc` through `tokenize_and_concatenate(..., max_length=513, num_proc=10)`. Each batch of 1,000 documents is joined by EOS, the text is cut into 20 character chunks that are encoded separately, the tokens are reshaped into 513-token rows, and each batch's tail is dropped.

   **Correction (plan 2 of the research log, full recovery).** The card's `num_proc=10` does not reproduce the split past document 6,000. The rows are reproduced exactly, all 2,775,651 by hash, by `map` over **160 contiguous shards of 6,250 documents**, each cut into six batches of 1,000 and one of 250: 1,120 batches in all. A batch never crosses a shard, so the boundaries are not all at multiples of 1,000. Evidence and checks: `data/doc_recovery/recovery.json`; code: `vpd_audit_2/recovery.py`.
3. That dataset is globally shuffled with `Dataset.shuffle(seed=42)` into the shuffled split.

So the validation rows come from **1,000,000 contiguous documents of monology's training split**, as scouting said.

**Document membership can be recovered, and was checked** (`vpd_audit_2/data_check.py`; `data_check.json`):
- **The permutation.** Shuffled row i equals unshuffled row `np.random.default_rng(42).permutation(2775651)[i]`. All 513 tokens matched on 16 of 16 rows, the first-post boundaries and 8 random rows. The installed `datasets` 4.4.2 `shuffle(seed)` equals `default_rng(seed).permutation(n)` (checked on n = 5,000).
- **The tokenization.** Tokenizing `val` documents 0 to 1,999 of `danbraunai/pile-uncopyrighted` the authors' way reproduced the first **6,155 of 6,155** unshuffled rows exactly: 2,593 rows from the first batch, 3,562 from the second.
- **Each row's documents and Pile subsets** then follow from the EOS positions within its batch, and the re-split dataset keeps `meta.pile_set_name`. Of the first post's 2,048 rows, 8 fall in those two batches and were identified (`data_check.json: first_post_rows_identified`). Two of them, shuffled rows 1,409 and 1,835, both donors, are from the same EuroParl document (val document 1,489).
- **Full recovery** means tokenizing all 1,000,000 documents: about 1.2 hours single-process here (229 documents/s), less with the authors' `num_proc=10`.

**Uncertain.** That the re-split's 1M documents are byte-identical to monology's training documents n − 1.1M to n − 0.1M rests on the card. Checking it means streaming most of the 11 GB `train/29.jsonl.zst`. This was not done.

## (l) The Newer Run `p-8383f5e5`

**Public**, at `goodfire/param-decomp/p-8383f5e5`, not under `goodfire/spd`.
- `run_info.json`: name `pile4l-ref6m-freq6p6em5-baseline-800k`, created 2026-08-28, commit `669b95e3`. That commit is **not** in any public ref, `refs/runs/*` included.
- Referenced at `later` `README.md:17`: "Current JAX reference config ... validated by https://wandb.ai/goodfire/param-decomp/runs/p-8383f5e5". Also `CONFIGS.md:27`.

**The evaluation ladder: not in its logs.** The only adversary keys are `eval/loss/PGDReconLoss_20step` (plus `/e2e` and hidden-activation variants). Final value (step 800,001): 0.6044968962669373. WandB's `config.yaml` (cache) configures only `eval.metrics.PGDRecon` with `n_steps: 20`, `step_size: 0.1`, `name: PGDReconLoss_20step`. No 40- to 1,280-step keys exist in `summary_keys.txt`, so there are no values at 160 or 320.

**Labels above zero per position: logged** as `eval/l0/0.0_total` = 180.41355895996097 at step 800,001, with per-layer and per-module keys.

**Checkpoint files: none in WandB.** The run has 2,028 files: 1,214 media, 809 artifact manifests, `config.yaml`, `launch_config.yaml`, `output.log`, `requirements.txt`, `wandb-summary.json`. Its 806 logged artifacts are 804 `run_table` (L0 bar charts), 1 `wandb-history`, and 1 `wandb-events` (`api.run(...).logged_artifacts()`). Nothing was downloaded.

## (m) The Authors' Evaluation Batch

- **The iterator.** `eval_iterator = loop_dataloader(eval_loader)`, created once before the training loop and **persisting across evaluations** (`run_spd.py:131`). Each evaluation draws `n_eval_steps = 1` batch (`eval.py:364-366`).
- **The per-process loader** (`lm_decomposition.py:119-146`, `data.py:186-268`):
  - streaming `val`;
  - with 16 processes and 12 files, filtered to stream indices ≡ rank (mod 16) (`data.py:196-204`);
  - then `dataset.shuffle(seed=1, buffer_size=1000)` (the seed is `global_seed = config.seed + 1`; this also shuffles the file order);
  - rows cut to their first 512 tokens (`data.py:227-231`);
  - `DataLoader(batch_size=8, drop_last=True)`.
  
  `loop_dataloader` restarts with `set_epoch` only when exhausted (271-289), after about 173,000 rows per process, which is not reached.
- **The logged value is not from a fixed batch.** Evaluations run at steps 0, 1,000, …, 400,000. The value logged at step 400,000 comes from the **401st** batch of each process's stream (batch index 400, stream rows 3,200 to 3,207 of each process), 128 texts in all.
- **The paper's table** matches no logged evaluation of this run; whether it was computed on this run's checkpoint or on a sister run is open (see (e)). Its batch is not determined.

## (n) The Earlier Project's Label Cache and Texts

**Volume `vpd-audit-cache`**: 17,486 entries, listed without downloading (`modal.Volume.listdir("/", recursive=True)`). Top level: `artifacts/` (the five runs and `manifest.json`), `sets/`, `donors/` (the label caches), `results/`, `hf/`, `out/`. Only four small metadata files were read: `donors/E_main.json`, `donors/D_unif_main.json`, `sets/E.json`, `sets/D_unif.json`, and `artifacts/manifest.json`.

| Cache | Size | Contents (from its JSON) |
|---|---|---|
| `donors/E_main.npz` | 644,097,546 B | the labels of E (rows 0 to 1,023) on `s-55ea3f9b` |
| `donors/D_unif_main.npz` | 654,853,716 B | the labels of D_unif (rows 1,024 to 2,047) |
| also | | `D_code_main`, `D_prose_main`, `E_lab_main`, `panel_{Github,StackExchange,Pile_CC,Wikipedia__en_,ArXiv}_main`, the control's `E_control`, `D_unif_control`, `D_code_control`, `D_prose_control`, `E_lab_control`, alive vectors, and SimpleStories dry-run caches |

**What one cache holds** (E_main and D_unif_main alike):
- **Only the labels**: the lower-leaky g, stored sparsely. `indptr` int64 (one entry per position plus one), `indices` uint16 (global subcomponent index in sorted module order), `values` float32 (`vpd_audit/donors.py:1-16 @ b6d3bac`). **No pre-sigmoid values.**
- `precision: bf16`, `g_dtype: torch.float32`, `subbatch: 64`, `importance_chunk: 32`, `deterministic_algorithms: true`, `gpu_name: NVIDIA A100-SXM4-40GB`, `torch_version: 2.8.0+cu128`.
- `checkpoint_hashes`: decomposition `fdd794ab…`, target `650f2eb6…`.
- `set_hash`: E `81f8b75b…`, D_unif `1807c12e…`.
- `mean_nnz_per_position`: E 203.4195, D_unif 206.8388.
- SHA-256 of the three arrays.

**The commits that wrote them** are **not in `vpd-audit`'s published history**: E_main by `6358459f` (clean tree), D_unif_main by `0b4ae4a5` with **`dirty: "1"`**, both with submodule `74146b5`. The README says the history "was condensed for publication".

**The first post's rows** (`vpd_audit/data.py:24-27, 93-121 @ b6d3bac`): `STREAM_SETS = {"E": (0, 1024), "D_unif": (1024, 2048)}`, rows of the shuffled `val` split "read in stream order without the authors' buffered shuffle", cut to 512 tokens.
- **Recipients:** rows **0 to 1,023**. **General donors:** rows **1,024 to 2,047**.
- Both hashes reproduce: from the parquet files directly (`data_check.json: first_post_sets`) and through `prepare_stream_sets` on Modal (`results/plan1_smoke/`).
- The **labelled sets** (`D_code`, `D_prose`, `E_lab`, calibration rows, and 18 panels of 200) come instead from `monology/pile-uncopyrighted`'s `val.jsonl.zst`, split by a seeded permutation of documents into parts A, B, and C (`data.py:175-230`; manifest `results/data/labeled_manifest.json`). They are not rows of the tokenized split.

**Every later pool must exclude** `val` rows 0 to 2,047 and the documents behind them. If monology's `val.jsonl.zst` is used (G5 fallback), it must also exclude the labelled sets' documents.

## (p) Precision and Positions

| | Precision | Source |
|---|---|---|
| Training | bf16 autocast (`autocast_bf16: true`) around the forward, labels, and losses | `run_spd.py:272` |
| Evaluation, adversary included | `torch.no_grad()` plus bf16 autocast; the adversary re-enables gradients inside it | `run_spd.py:355`, `pgd_utils.py:49` |

- **KL positions: all 512.** `calc_kl_divergence_lm` takes the mean over every (b, t) (`general_utils.py:228-230`); the adversary and the stochastic metric divide the sum by B·T (`pgd_utils.py:225-227`).
- **Cross-entropy positions: 511 per sequence.** `masked_batch[:, 0] = -100`, flattened, `logits[:-1]` against `labels[1:]` (`ce_and_kl_losses.py:102-110`).
- **Order of the means: equivalent.** Every sequence has 512 positions, so the mean over all B·T positions equals the mean over texts of per-text means. Across processes, sums and counts are reduced before dividing.

## (q) Random Draws

| Draw | Where | Generator |
|---|---|---|
| Evaluation adversary: routing | `pgd_utils.py:110`, before the init. `AllLayersRouter` draws nothing. | none |
| Evaluation adversary: starting point | `pgd_utils.py:111` → `_get_pgd_init_tensor` 311, `torch.rand(shape, device=device)` on rank 0, broadcast | **global CUDA RNG**, no explicit generator |
| Stochastic sources | `utils/component_utils.py:21-28` `torch.rand_like(ci)` per module in `ci` order, then 30-37 `torch.rand(leading_dims)` per module for the delta masks | global RNG |
| Routing (`uniform_k_subset`) | `component_utils.py:39-42` → `routing.py:33` `sample_uniform_k_subset_routing_masks(mask_shape, module_names, self.device)`: **no generator passed**. Then `torch.randint` (117-123) and `torch.rand` inside `rand_perm` (92) | global RNG |
| Persistent training sources | `persistent_pgd.py:161-168` `torch.rand` at construction, per process, not broadcast for `per_batch_per_position` | global RNG |

The global RNG of each process is set once by `seed_per_rank(seed)` = `seed · world_size + rank` (`run_spd.py:165`, `distributed_utils.py:259-271`). It then advances through every training and evaluation draw, so no evaluation draw of the run can be replayed from the config.

**For paired runs in plan 2 of the research log.** Seed the global generator before each adversary call, or pass explicit generators to a re-implementation. The authors' functions accept none.

## (o) The Authors' Label Re-Fitting Procedure

**Located:** `param_decomp/app/backend/optim_cis.py @ tag`, with entry point `optimize_ci_values(model, tokens, config, device)` (307-509). A batched variant over several sparsity coefficients is `optimize_ci_values_batched` (605). The run commit has an older version with CE and KL only (`spd/app/backend/optim_cis.py`).

**What it does:**
- One prompt, shape [1, seq].
- One trainable pre-sigmoid parameter per (position, component) whose base label is > 0. The others stay at 0 (99-205).
- AdamW (`OptimCIConfig`, 209-235).
- Loss = `coeff · recon + imp_min_coeff · importance_minimality_loss(upper_leaky)`, plus `coeff · adversarial recon` when `adv_pgd` is set (390-438).
- Masks are stochastic (`calc_stochastic_component_mask_info`, delta components on) or the labels themselves (`mask_type`).
- The adversary is a fresh sign-PGD every step (`run_adv_pgd`, 262-304). Its sources are per (position, component), restricted to components alive on the prompt; the others' sources are 0. **The delta components are excluded** from both the adversarial and the label-mask paths.

**For the requested settings:**
- **Full output at every position.** `MeanKLLossConfig` exists and `compute_recon_loss` handles it (61-65, 91-95), but `OptimCIConfig.loss_config` is typed `PositionalLossConfig` (225). It is a plain dataclass, so passing it works; only the CE and logit end-of-run metrics would be skipped.
- **Stochastic and adversarial masks.** Supported as is.
- **Starting from the released labels.** This is the default warm start.
- **Starting from chosen labels just above zero.** This needs about 30 lines of our own: a wrapper that builds `create_optimizable_ci_params` with chosen initial pre-sigmoid values and a chosen alive set.

**Estimate.** About **1.5 to 2 engineer-days**:
- half a day for a wrapper and a Modal function;
- half a day for the chosen-label start;
- half to one day of checks, for example that a long run from the released labels does not drift when the objective is the full output.

Compute: one 512-token text per call, a few hundred steps, each one stochastic and one adversarial forward and backward plus the inner PGD steps. Roughly 1 to 5 minutes per text on an A100 at 20 inner steps; unmeasured.

**Uncertain.** Whether the paper's figures used the tag's or the run commit's version, and with which settings.

---

## Gate G5 and the Leakage Bound

**The gate passes.** Each row's document can be identified by recovering membership as (k) describes. The permutation and the tokenization were verified on rows, and full recovery is a deterministic 1-hour tokenization. The tokenized split itself has no document field.

**The fallback's preconditions, for the record.**
- The tokenized validation split came from monology's **training** split (its last 1.1M documents but 100K).
- monology's own `val.jsonl.zst` was used in **no** split of the tokenized dataset.
- The authors' tokenization reproduces rows exactly when applied to the right documents (6,155 of 6,155).

**The bound.** From `vpd_audit_2/data_check.py: leakage_bound`, over all 1,000,000 `val` documents:
- character counts are summed over all documents, 5,536,668,676 characters in total;
- tokens per character = 2,775,651 · 513 minus 999,000 EOS tokens, divided by the characters: 0.25700;
- n_d = (characters · 0.257 + 1) / 513.

| Quantity | Value |
|---|---|
| N (rows) | 2,775,651 |
| m = Σ n_d² / Σ n_d | **41.83** |
| Expected cross-pool same-document pairs, a = b = 1,024, plan formula a·b·(m − 1)/N | **15.4** |
| The same, counting rows *touched* (each document touches ⌈n_d⌉ or one more, at a random offset) | 16.2 |
| n_d quantiles 50 / 90 / 99 / 99.9 % | 0.88 / 5.35 / 30.8 / 82.6 rows |
| Largest document | about 3,872 rows (about 2.0M tokens) |
| Share of rows in documents longer than one row | 0.896 |
| Share of Σ n_d² from the 100 longest documents | 0.454 |

m is dominated by a few very long documents. The dropped batch tails (under 513 tokens in each of 1,000 batches) are left out of the token total, a 0.02 % effect.

**The scale each carry-over ratio sees (plan 2 of the research log).** Between one attack batch and one held-out batch of 128 rows each, drawn at random by row, the expected number of row pairs sharing a document is 128 × 128 × (m − 1)/N = 16,384 × 40.83 / 2,775,651 ≈ **0.24**. Pools built by tokenization batch (plan 2 of the research log, Section 6) make it exactly zero.
