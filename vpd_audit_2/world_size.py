"""Plan 2 of the research log, step 2 (section 4): test the world-size inference of provenance (i).

Two parts.

1. Rebuild (CPU, local), with the authors' own data-loader code at the run's commit:

       PYTHONPATH=.cache/src/pd-85c6b70 uv run python -m vpd_audit_2.world_size

   For each candidate world size W in {8, 16, 32} and each rank r < W, `spd.data.create_data_loader` at 85c6b70 (the
   worktree under `.cache/src/pd-85c6b70`, see provenance.md for how to recreate it) is called exactly as
   `spd/experiments/lm/lm_decomposition.py:119-146` calls it for the evaluation loader: the run's task config, batch
   size 128 // W, buffer 1,000, `global_seed = config.seed + 1 = 1`, and a `DistributedState(rank=r, world_size=W)`.
   `spd.data.loop_dataloader` is iterated to its 401st batch (index 400), the batch evaluated at step 400,000
   (provenance (m)). Each candidate follows its own branch of the loader: with 12 files, W = 8 shards by file
   (`num_shards >= world_size`) and W = 16 and 32 filter by stream index. `datasets` is 4.4.2, the version in the
   run's `requirements.txt`. The loader streams the dataset's current revision; its parquet data were last uploaded
   on 24 February 2026, before the run, and only the README changed after (recorded in the output).

   Each rebuilt text (512 ids) is located in the `val` split by the SHA-256 of its ids, using the row hashes that
   `vpd_audit_2.recovery` caches. Writes `results/plan2_world_size/batches.json` and `batches.npz` (the ids).

2. Metrics (GPU, Modal; `modal_gates.py::world_size_metrics` calls `metrics_on_batches`): on each candidate's batch,
   in bf16 autocast under `no_grad` as `evaluate()` runs (`eval.py:365-435` at the tag), the authors' own `CI_L0`
   (threshold 0.0, the config's groups) and `CEandKLLosses` (rounding threshold 0.0) metrics, updated once per
   rank's share of 128 // W texts in rank order and then computed, as each process of the run did before the
   all-reduce. The 24 per-module L0 values and `kl_ci_masked` are compared with the run's logged step-400,000 values.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env

CANDIDATES = (8, 16, 32)
EVAL_BATCH = 128
BATCH_INDEX = 400  # the 401st evaluation: steps 0, 1,000, ..., 400,000
EVAL_SEED = 1  # config.seed + 1
BUFFER_SIZE = 1000
N_CTX = 512
RUN_COMMIT = "85c6b702d2accf5bfcf02e52b753acd0fcbcf6c5"
RUN_WORKTREE = env.CACHE_DIR / "src" / "pd-85c6b70"
DATASET = "danbraunai/pile-uncopyrighted-tok-shuffled"
EXPECTED_HEAD = "6f141f6e4edc32fea842f2ece0d3477b15c3dc90"
OUT_DIR = env.REPO_ROOT / "results" / "plan2_world_size"
L0_TOL = 0.001
KL_TOL = 0.01
SEPARATION = 0.01


def log(msg: str) -> None:
    print(f"[world-size] {msg}", flush=True)


# ----------------------------------------------------------------------------- part 1: rebuild (CPU)


def _rebuild_rank(args: tuple[int, int]) -> dict[str, Any]:
    """One rank's 401st evaluation batch through the authors' loader at the run's commit."""
    W, rank = args
    from spd.data import DatasetConfig, create_data_loader, loop_dataloader
    from spd.utils.distributed_utils import DistributedState

    t0 = time.time()
    cfg = DatasetConfig(name=DATASET, hf_tokenizer_path="EleutherAI/gpt-neox-20b", split="val", n_ctx=N_CTX, is_tokenized=True,
                        streaming=True, column_name="input_ids", shuffle_each_epoch=True, seed=None)
    loader, _ = create_data_loader(dataset_config=cfg, batch_size=EVAL_BATCH // W, buffer_size=BUFFER_SIZE, global_seed=EVAL_SEED,
                                   dist_state=DistributedState(rank=rank, world_size=W, local_rank=rank % 8, backend="nccl"))
    it = loop_dataloader(loader)
    first = None
    for i in range(BATCH_INDEX + 1):
        b = next(it)
        if i == 0:
            first = b["input_ids"].numpy().astype(np.int32)
    ids = b["input_ids"].numpy().astype(np.int32)
    assert ids.shape == (EVAL_BATCH // W, N_CTX), ids.shape
    return {"W": W, "rank": rank, "ids": ids, "first_batch_sha256": hashlib.sha256(first.tobytes()).hexdigest(), "seconds": time.time() - t0}


def _check_worktree() -> dict[str, str]:
    import subprocess

    head = subprocess.run(["git", "-C", str(RUN_WORKTREE), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(RUN_WORKTREE), "status", "--porcelain"], check=True, capture_output=True, text=True).stdout.strip()
    blob = subprocess.run(["git", "-C", str(RUN_WORKTREE), "hash-object", "spd/data.py"], check=True, capture_output=True, text=True).stdout.strip()
    assert head == RUN_COMMIT and not dirty, (head, dirty)
    import spd.data

    assert Path(spd.data.__file__).resolve().is_relative_to(RUN_WORKTREE.resolve()), spd.data.__file__
    return {"commit": head, "spd_data_py_blob": blob, "spd_data_py": str(Path(spd.data.__file__).resolve().relative_to(env.REPO_ROOT))}


def _dataset_revision() -> dict[str, Any]:
    from huggingface_hub import HfApi

    api = HfApi()
    info = api.dataset_info(DATASET)
    commits = [{"commit": c.commit_id, "created_at": str(c.created_at), "title": c.title} for c in api.list_repo_commits(DATASET, repo_type="dataset")]
    after_upload = [c for c in commits if not c["title"].startswith("Upload dataset") and c["title"] != "initial commit"]
    return {"head": info.sha, "head_is_expected": info.sha == EXPECTED_HEAD, "commits_not_uploading_data": after_upload,
            "last_data_upload": next(c for c in commits if c["title"].startswith("Upload dataset"))}


def rebuild() -> dict[str, Any]:
    import multiprocessing as mp

    import datasets

    from vpd_audit_2.recovery import ROW_HASHES

    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Any] = {"code": _check_worktree(), "datasets_version": datasets.__version__, "dataset_revision": _dataset_revision(),
                           "batch_index": BATCH_INDEX, "eval_seed": EVAL_SEED, "buffer_size": BUFFER_SIZE, "n_ctx": N_CTX}
    assert datasets.__version__ == "4.4.2", datasets.__version__  # provenance/runs/s-55ea3f9b/requirements.txt line 55
    jobs = [(W, r) for W in CANDIDATES for r in range(W)]
    ctx = mp.get_context("spawn")
    pool = ctx.Pool(8)  # workers stay alive between ranks: a finished stream can leave threads that block a worker's exit
    try:
        res = pool.map(_rebuild_rank, jobs, chunksize=1)
    finally:
        pool.terminate()
    log(f"rebuilt {len(res)} rank batches in {time.time() - t0:.0f} s")

    H = np.load(ROW_HASHES)
    sha512 = H["sha512"]
    index: dict[bytes, list[int]] = {}
    for i in range(sha512.shape[0]):
        index.setdefault(sha512[i].tobytes(), []).append(i)
    ids_out = {}
    out["candidates"] = {}
    for W in CANDIDATES:
        ranks = sorted((r for r in res if r["W"] == W), key=lambda r: r["rank"])
        ids = np.concatenate([r["ids"] for r in ranks])
        assert ids.shape == (EVAL_BATCH, N_CTX)
        ids_out[f"W{W}"] = ids
        texts = []
        for r in ranks:
            for k in range(r["ids"].shape[0]):
                h = hashlib.sha256(r["ids"][k].tobytes()).digest()
                texts.append({"rank": r["rank"], "index_in_rank_batch": k, "sha256_512": h.hex(), "positions": index.get(h, [])})
        out["candidates"][str(W)] = {
            "loader_branch": "shard by file (num_shards 12 >= W)" if 12 >= W else "filter by stream index mod W",
            "texts_per_rank": EVAL_BATCH // W, "texts": texts,
            "n_texts_located": sum(1 for t in texts if t["positions"]), "n_texts_with_several_positions": sum(1 for t in texts if len(t["positions"]) > 1),
            "first_batch_sha256_by_rank": [r["first_batch_sha256"] for r in ranks], "seconds_by_rank": [r["seconds"] for r in ranks],
            "sha256_ids": hashlib.sha256(ids.tobytes()).hexdigest(),
        }
        log(f"W={W}: {out['candidates'][str(W)]['n_texts_located']}/128 texts located; branch {out['candidates'][str(W)]['loader_branch']}")
    sets = {W: {tuple(t["positions"]) for t in out["candidates"][str(W)]["texts"]} for W in CANDIDATES}
    out["overlap_between_candidates"] = {f"{a}-{b}": len(sets[a] & sets[b]) for i, a in enumerate(CANDIDATES) for b in CANDIDATES[i + 1 :]}
    out["seconds"] = time.time() - t0
    np.savez(OUT_DIR / "batches.npz", **ids_out)
    with open(OUT_DIR / "batches.json", "w") as f:
        json.dump(out, f, indent=1)
    log(f"wrote {OUT_DIR / 'batches.json'}")
    return out


# ----------------------------------------------------------------------------- part 2: metrics (GPU)


def logged_values() -> dict[str, float]:
    """The run's step-400,000 values: the summary's last evaluation (`_step` 400,000)."""
    s = json.load(open(env.PROVENANCE_DIR / "runs" / "s-55ea3f9b" / "summary.json"))
    assert s["_step"] == 400000, s["_step"]
    out = {k[len("eval/l0/0.0_"):]: float(v) for k, v in s.items() if k.startswith("eval/l0/0.0_h.")}
    assert len(out) == 24, len(out)
    out["kl_ci_masked"] = float(s["eval/ce_kl/kl_ci_masked"])
    return out


def metrics_on_batches(model: Any, batches: dict[str, np.ndarray], device: str = "cuda", log_fn: Any = print) -> dict[str, Any]:
    """The 24 per-module L0 values and kl_ci_masked on each candidate's batch, with the authors' metric classes."""
    import torch

    from vpd_audit_2.run_config import RAW, eval_entry

    from param_decomp.metrics.ce_and_kl_losses import CEandKLLosses
    from param_decomp.metrics.ci_l0 import CI_L0

    l0_cfg, cekl_cfg = eval_entry("CI_L0"), eval_entry("CEandKLLosses")
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        weight_deltas = model.calc_weight_deltas()  # inside the autocast, as evaluate() computes them (run_spd.py:355)
    out: dict[str, Any] = {}
    for name, ids in batches.items():
        W = int(name[1:])
        share = EVAL_BATCH // W
        l0 = CI_L0(model=model, device=device, ci_alive_threshold=RAW["ci_alive_threshold"], groups=l0_cfg["groups"])
        cekl = CEandKLLosses(model=model, device=device, sampling=RAW["sampling"], rounding_threshold=cekl_cfg["rounding_threshold"])
        t0 = time.time()
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            for r in range(W):
                batch = torch.from_numpy(ids[r * share : (r + 1) * share].astype(np.int64)).to(device)
                target_output = model(batch, cache_type="input")
                ci = model.calc_causal_importances(pre_weight_acts=target_output.cache, detach_inputs=False, sampling=RAW["sampling"])
                l0.update(ci=ci)
                cekl.update(batch=batch, target_out=target_output.output, ci=ci, weight_deltas=weight_deltas)
                del target_output, ci
        l0_out = {k[len("0.0_"):]: float(v) for k, v in l0.compute().items() if k.startswith("0.0_")}
        kl = cekl.compute()
        out[name] = {"l0": l0_out, "kl_ci_masked": float(kl["kl_ci_masked"]), "kl_zero_masked": float(kl["kl_zero_masked"]),
                     "per_rank_share": share, "seconds": time.time() - t0}
        log_fn(f"[world-size] {name}: L0 total {l0_out.get('total')}, kl_ci_masked {kl['kl_ci_masked']:.6f}")
    return out


def decide(metrics: dict[str, Any]) -> dict[str, Any]:
    """Section 4's reading: W is confirmed if its 25 values agree (each L0 within 0.1 percent, kl_ci_masked within
    1 percent) and every other candidate misses at least one value by more than 1 percent."""
    logged = logged_values()
    modules = sorted(k for k in logged if k != "kl_ci_masked")
    table: dict[str, Any] = {}
    for name, m in metrics.items():
        rel = {k: m["l0"][k] / logged[k] - 1 for k in modules}
        rel["kl_ci_masked"] = m["kl_ci_masked"] / logged["kl_ci_masked"] - 1
        agree = all(abs(rel[k]) <= L0_TOL for k in modules) and abs(rel["kl_ci_masked"]) <= KL_TOL
        table[name] = {"values": {**{k: m["l0"][k] for k in modules}, "kl_ci_masked": m["kl_ci_masked"]}, "relative_difference": rel,
                       "max_abs_relative_difference_l0": max(abs(rel[k]) for k in modules), "abs_relative_difference_kl": abs(rel["kl_ci_masked"]),
                       "agrees": agree, "misses_some_value_by_more_than_1pct": any(abs(v) > SEPARATION for v in rel.values())}
    agreeing = [n for n, t in table.items() if t["agrees"]]
    confirmed = None
    if len(agreeing) == 1 and all(table[n]["misses_some_value_by_more_than_1pct"] for n in table if n != agreeing[0]):
        confirmed = int(agreeing[0][1:])
    return {"logged": logged, "candidates": table, "agreeing": agreeing, "confirmed_world_size": confirmed,
            "rule": "each L0 within 0.1 percent and kl_ci_masked within 1 percent; every other candidate misses at least one value by more than 1 percent"}


if __name__ == "__main__":
    rebuild()
    os._exit(0)  # streaming threads can keep the interpreter from exiting
