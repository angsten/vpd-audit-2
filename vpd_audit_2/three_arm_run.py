"""Session 7, plan 6: the three-arm experiment on the GPU, and its local side, with no cloud call in it
(`modal_three_arm.py` hands it the cloud). The specification is `sessions/007/notes/riku/three_arm_spec_v2.md` with the
plan's eight amendments; the computation is `three_arm.py`.

Stages, in this order, one commit for all of them:

  - "gate" (one container): on one batch of calibration rows, (1) for each arm, our batch step against the authors'
    class driven by training's own sequence, from the same seed, in bfloat16 autocast: the losses and the sources
    after the batch, bit for bit (the note's gate is the released scope's; the other two are recorded beside it);
    (2) the scaled gradient against the scale times the authors' gradient; (3) the per-document state's loss against
    the per-position state's holding the same values at every position, bit for bit; (4) as description, our released
    state on 64 texts against the authors' on the first 4 texts alone, as one training process saw them, from the same
    starting sources. Nothing launches after a failed gate.
  - "rehearsal" (one container): 20 batches of calibration rows per arm, one seed: seconds per batch and memory, from
    which every later stage is projected. No reading is taken from it.
  - "run" (six containers, one per arm and seed): 1,000 batches of the committed text plan, the same sequence for every
    arm and seed; per batch the three harms, the learning rate, the batch's index, and its seconds; for the batch arm,
    its source after every batch.
  - "extension" (amendment 6, only when its rule says so): arm 1, seed 1, and arm 2, seed 1, if not broken out, rerun
    from their start to min(10 b, 3,000) batches, b the yardstick's breakout batch on the governing series; the first
    1,000 batches must reproduce the run's records exactly.
  - "carry" (one held-out container): the batch arm's source at its breakout batches and its last batch, for each seed,
    scored on H1, H5, H9 and H13 through the lead's scoring path (`adversary.score`, the run's labels checked).

The texts (`texts_plan`): attack-side rows that no manifest pool uses, rebuilt with the manifest's own functions and
checked against its counts and pools, in the manifest's attack order with every pool's rows removed, then permuted by
the committed seed ("three-arm-texts"): 3,000 batches of 64. The rehearsal and the gate use calibration rows C1 to C10.
The token ids go to the volume once, as one file whose SHA-256 every container checks.

Money (`lead_ledger.money`): before each stage, what has been spent plus the projection of what remains, against $35;
over it, nothing launches.
"""

from __future__ import annotations

import gc
import hashlib
import io
import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_run as SR
from vpd_audit_2 import three_arm as T

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s7_three_arm"
VOLUME = "/cache/s7_three_arm"
LOCAL = REPO_ROOT / ".cache" / "s7_three_arm"
RUN = "s7_three_arm"
PART = "three_arm"
ARM = "s7_three_arm"
MODE = "s7_three_arm"
UNITS = "units"
TEXTS_FILE = "texts.npz"
CAP_DOLLARS = 35.0  # the plan: the GPU cap
N_BATCHES = 1000
N_MAX = 3000
REHEARSAL_BATCHES = 20
SEEDS = (1, 2)  # shared by every arm (amendment 3)
EXTENSION_SEED = 1
EXTENSION_FACTOR = 10
TEXTS_LABEL = "three-arm-texts"
CALIBRATION = tuple(f"C{j}" for j in range(1, 11))  # 1,280 rows: 20 batches of 64
CARRY_BATCHES = ("H1", "H5", "H9", "H13")
STAGES = ("gate", "rehearsal", "run", "extension", "carry")
GATE_ARMS = T.ARMS
READING_FILES = ("vpd_audit_2/three_arm.py", "vpd_audit_2/three_arm_run.py", "vpd_audit_2/modal_three_arm.py", "vpd_audit_2/three_arm_read.py")
SPEC_KEYS = {"part", "arm", "stage", "side", "batch", "commit", "mode", "root", "units", "run", "job", "refs"}


class ThreeArmFailure(Exception):
    """A check in a container failed; the message names it and holds no value."""


def stage_record(stage: str, containers: int) -> LG.Stage:
    return LG.Stage(f"s7_three_arm_{stage}", ARM, "heldout" if stage == "carry" else "attack", containers, 0, 0, 0, 0, 0, False)


# ----------------------------------------------------------------------------- the texts


def attack_side_unused() -> np.ndarray:
    """The eligible attack-side rows no manifest pool uses, in the manifest's attack order. Eligibility and sides are
    rebuilt with the manifest's own functions, as `manifest.build` does, and checked against the committed manifest:
    its counts, and its sided pools, which must be the first rows of that order (C1..C16, CQ, A1..A16, R) and, for the
    DOM pools, rows of the remainder."""
    import pyarrow.parquet as pq

    from vpd_audit_2 import manifest as M
    from vpd_audit_2.recovery import ROW_HASHES, ROWS_PARQUET, VOCAB_SIZE

    man = json.load(open(M.OUT_DIR / "manifest.json"))
    t = pq.read_table(ROWS_PARQUET).sort_by("position")
    N = t.num_rows
    batch_of = t.column("tokenization_batch").to_numpy().astype(np.int64)
    first = t.column("first_doc").to_numpy().astype(np.int64)
    last = t.column("last_doc").to_numpy().astype(np.int64)
    H = np.load(ROW_HASHES)
    sha512, length, max_id = H["sha512"], H["length"], H["max_id"]
    n_docs = int(last.max()) + 1
    excl = np.zeros(N, dtype=bool)
    fp = np.zeros(N, dtype=bool)
    fp[M.FIRST_POST_ROWS[0] : M.FIRST_POST_ROWS[1]] = True
    docs = np.zeros(n_docs, dtype=bool)
    for r in np.flatnonzero(fp):
        docs[first[r] : last[r] + 1] = True
    excl |= fp | M._rows_touching(docs, first, last)
    ws_rows = np.zeros(N, dtype=bool)
    for name, pool in man["pools"].items():
        if pool["pool"] == "WS":
            ws_rows[[int(x[1:]) for x in pool["texts"]]] = True
    docs_ws = np.zeros(n_docs, dtype=bool)
    for r in np.flatnonzero(ws_rows):
        docs_ws[first[r] : last[r] + 1] = True
    excl |= ws_rows | M._rows_touching(docs_ws, first, last)
    eligible, counts = M.exclusions(sha512, excl, length, max_id, VOCAB_SIZE)
    if counts["eligible"] != man["exclusions"]["eligible"]:
        raise LL.LaunchRefusal("the rebuilt eligibility is not the manifest's")
    n_batches = int(batch_of.max()) + 1
    bp = M.perm(n_batches, "batch-split")
    side_attack = np.isin(batch_of, bp[: n_batches // 2])
    att = np.flatnonzero(eligible & side_attack)
    if att.size != man["batch_split"]["eligible_rows_attack"]:
        raise LL.LaunchRefusal("the rebuilt attack side is not the manifest's")
    att = att[M.perm(att.size, "perm", "attack")]
    order = [f"C{j}" for j in range(1, 17)] + ["CQ"] + [f"A{j}" for j in range(1, 17)] + ["R"]
    front = np.concatenate([[int(x[1:]) for x in man["pools"][n]["texts"]] for n in order]).astype(np.int64)
    if not np.array_equal(att[: front.size], front):
        raise LL.LaunchRefusal("the manifest's attack pools are not the first rows of the rebuilt order")
    rest = att[front.size :]
    used = {int(x[1:]) for p in man["pools"].values() for x in p["texts"]}
    dom = {int(x[1:]) for n, p in man["pools"].items() if p["pool"] == "DOM" and p["side"] == "attack" for x in p["texts"]}
    if not dom <= set(rest.tolist()):
        raise LL.LaunchRefusal("the attack DOM pools are not rows of the remainder")
    return rest[~np.isin(rest, np.fromiter(used, dtype=np.int64))]


def texts_plan() -> dict[str, Any]:
    """The committed text plan: 3,000 batches of 64 unused attack-side rows by the seed ("three-arm-texts"), and the
    calibration rows C1 to C10 for the gate and the rehearsal."""
    from vpd_audit_2 import manifest as M

    rest = attack_side_unused()
    rng = np.random.default_rng(M.seed_of(TEXTS_LABEL))
    run = rest[rng.permutation(rest.size)[: N_MAX * T.TEXTS_PER_BATCH]]
    man = json.load(open(M.OUT_DIR / "manifest.json"))
    cal = np.concatenate([[int(x[1:]) for x in man["pools"][c]["texts"]] for c in CALIBRATION]).astype(np.int64)
    return {"seed_key": [M.MASTER, TEXTS_LABEL], "seed": M.seed_of(TEXTS_LABEL), "unused_attack_rows": int(rest.size), "run_positions": run.tolist(),
            "calibration_pools": list(CALIBRATION), "calibration_positions": cal.tolist()}


def texts_arrays(plan: dict[str, Any]) -> dict[str, np.ndarray]:
    """The token ids (the 512 the model sees) of the plan's rows, checked against the manifest's hashes where it has them."""
    from vpd_audit_2.data_check import SHUFFLED, ParquetSplit
    from vpd_audit_2.manifest import SEQ_LEN

    sp = ParquetSplit(*SHUFFLED, column="input_ids")
    run = sp.token_rows(np.asarray(plan["run_positions"], dtype=np.int64))[:, :SEQ_LEN]
    cal = sp.token_rows(np.asarray(plan["calibration_positions"], dtype=np.int64))[:, :SEQ_LEN]
    return {"run": np.ascontiguousarray(run, dtype=np.int32).reshape(N_MAX, T.TEXTS_PER_BATCH, SEQ_LEN),
            "calibration": np.ascontiguousarray(cal, dtype=np.int32).reshape(-1, T.TEXTS_PER_BATCH, SEQ_LEN)}


def texts_bytes(arrays: dict[str, np.ndarray]) -> bytes:
    from vpd_audit_2.manifest import deterministic_npz

    return deterministic_npz(arrays)


def write_texts(dest: Path | None = None) -> dict[str, Any]:
    """Build the plan and its token file; the plan (positions and the file's SHA-256) is committed, the file is not."""
    plan = texts_plan()
    data = texts_bytes(texts_arrays(plan))
    dest = LOCAL / TEXTS_FILE if dest is None else dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    plan["texts_file_sha256"] = hashlib.sha256(data).hexdigest()
    LL.write_json(RESULTS / "texts.json", plan)
    return plan


def load_texts(path: Path, sha256: str) -> dict[str, np.ndarray]:
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise ThreeArmFailure("the texts file is not the committed plan's")
    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


# ----------------------------------------------------------------------------- what each container is handed


def specs(stage: str, commit: str, texts_sha: str, *, refs: dict[str, Any] | None = None, extension: dict[str, int] | None = None,
          carry: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    base = {"part": PART, "arm": ARM, "stage": stage, "commit": commit, "mode": MODE, "root": VOLUME, "units": UNITS, "run": RUN}
    if stage == "gate":
        return [{**base, "side": "attack", "batch": "gate", "job": {"texts_sha256": texts_sha, "batch_index": 0}, "refs": {}}]
    if stage == "rehearsal":
        return [{**base, "side": "attack", "batch": "rehearsal", "job": {"texts_sha256": texts_sha, "seed": SEEDS[0], "n_batches": REHEARSAL_BATCHES},
                 "refs": {}}]
    if stage == "run":
        return [{**base, "side": "attack", "batch": f"{arm}|s{seed}", "job": {"texts_sha256": texts_sha, "arm": arm, "seed": seed, "n_batches": N_BATCHES},
                 "refs": {}} for arm in T.ARMS for seed in SEEDS]
    if stage == "extension":
        return [{**base, "side": "attack", "batch": f"{arm}|s{EXTENSION_SEED}|x",
                 "job": {"texts_sha256": texts_sha, "arm": arm, "seed": EXTENSION_SEED, "n_batches": int(n)}, "refs": {}}
                for arm, n in sorted((extension or {}).items())]
    if stage == "carry":
        return [{**base, "side": "heldout", "batch": "carry", "job": {"settings": carry or [], "batches": list(CARRY_BATCHES)}, "refs": refs or {}}]
    raise ValueError(stage)


def check_spec(spec: dict[str, Any]) -> None:
    st, job = spec.get("stage"), spec.get("job") or {}
    ok = (set(spec) - {"launch"} == SPEC_KEYS and spec["part"] == PART and spec["arm"] == ARM and st in STAGES and spec["mode"] == MODE
          and spec["root"] == VOLUME and spec["units"] == UNITS and spec["run"] == RUN and len(str(spec["commit"])) == 40)
    if ok and st == "run":
        ok = job.get("arm") in T.ARMS and job.get("seed") in SEEDS and job.get("n_batches") == N_BATCHES and spec["batch"] == f"{job['arm']}|s{job['seed']}"
    elif ok and st == "extension":
        ok = job.get("arm") in ("released", "per_document") and job.get("seed") == EXTENSION_SEED and N_BATCHES < int(job.get("n_batches", 0)) <= N_MAX
    elif ok and st == "rehearsal":
        ok = job.get("seed") == SEEDS[0] and job.get("n_batches") == REHEARSAL_BATCHES
    elif ok and st == "carry":
        ok = spec["side"] == "heldout" and tuple(job.get("batches", ())) == CARRY_BATCHES and set(spec["refs"]) == set(CARRY_BATCHES)
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('part')}|{spec.get('batch')}")


def check_environment(ctx: SR.Context) -> None:
    """The lead run's configuration; the tiny model's tests (mode "test") skip it."""
    if ctx.mode == "test":
        return
    env = ctx.environment
    ok = (ctx.mode == MODE and ctx.device == "cuda" and "B200" in str(env.get("gpu")) and env.get("deterministic_algorithms") is True
          and env.get("deterministic_warn_only") is False and env.get("allow_tf32_matmul") is False and env.get("allow_tf32_cudnn") is False
          and env.get("cublas_workspace_config") == ":4096:8" and env.get("vpd_audit_2_commit") == ctx.commit and env.get("vpd_audit_2_dirty") == "0")
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ARM}")


# ----------------------------------------------------------------------------- in the container


def _sync(ctx: SR.Context) -> None:
    if ctx.device == "cuda":
        import torch

        torch.cuda.synchronize()


def _peak_gib(ctx: SR.Context) -> float:
    if ctx.device == "cuda":
        import torch

        return float(torch.cuda.max_memory_allocated() / 2**30)
    return 0.0


def _reset_peak(ctx: SR.Context) -> None:
    if ctx.device == "cuda":
        import torch

        torch.cuda.reset_peak_memory_stats()


def _ids(ctx: SR.Context, tokens: np.ndarray) -> Any:
    import torch

    return torch.from_numpy(np.ascontiguousarray(tokens, dtype=np.int64)).to(ctx.device)


def _autocast(ctx: SR.Context) -> bool:
    return ctx.device == "cuda"  # amendment 4: bfloat16 autocast, as training and the lead experiment ran; the CPU tests run in float32


def _done(ctx: SR.Context, name: str) -> dict[str, Any] | None:
    """A finished unit's return, for a restart that skips it (after checking its commit); None if not finished."""
    path = SR.unit_path(ctx, name)
    if LR.finished(path):
        if SR.unit_meta(path)["commit"] != ctx.commit:
            raise ThreeArmFailure(f"{name}: a finished unit from another commit")
        return {"unit": name, "sha256": LR.marker(path).read_text(), "guards": {"skipped_after_restart": True}, "skipped": True}
    return None


def _return(ctx: SR.Context, spec: dict[str, Any], units: list[dict[str, Any]], removed: int) -> dict[str, Any]:
    ctx.commit_volume()
    return {"container": f"{ARM}|{spec['stage']}|{spec['batch']}", "units": units, "finished_units": len(units), "expected_units": 1, "stopped": False,
            "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment), "timings": {k: float(v) for k, v in ctx.timings.items()},
            "removed_unfinished": int(removed)}


def run_arm(model: Any, ctx: SR.Context, arm: str, seed: int, batches: np.ndarray, *, record_sources: bool) -> dict[str, np.ndarray]:
    """One arm and seed over the given batches [n, 64, 512], from the state's fresh start."""
    wd = T.weight_deltas(model)
    n = int(batches.shape[0])
    state = T.make_state(model, arm, int(batches.shape[1]), int(batches.shape[2]), ctx.device, T.init_seed(seed))
    rec = {k: np.full(n, np.nan) for k in (*T.SERIES, "lr", "seconds")}
    sources = []
    _reset_peak(ctx)
    for b in range(n):
        t0 = time.time()
        prep = T.prepare(model, _ids(ctx, batches[b]), autocast=_autocast(ctx))
        r = T.batch_step(state, model, prep, wd, step=b, total_steps=N_MAX, autocast=_autocast(ctx))
        _sync(ctx)
        rec["seconds"][b] = time.time() - t0
        for k in (*T.SERIES, "lr"):
            rec[k][b] = r[k]
        if record_sources:
            sources.append(T.flat_sources(state, ctx.lay))
        del prep
    out = {k: v for k, v in rec.items()}
    out["peak_gib"] = np.array([_peak_gib(ctx)])
    if record_sources:
        out["sources"] = np.stack(sources).astype(np.float32)
    del state
    gc.collect()
    if ctx.device == "cuda":
        import torch

        torch.cuda.empty_cache()
    return out


def arm_job(model: Any, ctx: SR.Context, spec: dict[str, Any], texts: dict[str, np.ndarray]) -> dict[str, Any]:
    job = spec["job"]
    arm, seed, n = job["arm"], int(job["seed"]), int(job["n_batches"])
    name = f"{spec['stage']}_{arm}_s{seed}_n{n}"
    removed = SR.clean_unfinished(ctx, [name])
    skipped = _done(ctx, name)
    if skipped is not None:
        return _return(ctx, spec, [skipped], removed)
    ctx.log(event="container_started", container=f"{ARM}|{spec['stage']}|{spec['batch']}", count=removed)
    t0 = time.time()
    out = run_arm(model, ctx, arm, seed, texts["run"][:n], record_sources=(arm == "batch"))
    ctx.tick("arm_run", time.time() - t0, n)
    meta = {"unit": name, "stage": spec["stage"], "arm": arm, "seed": seed, "n_batches": n, "commit": ctx.commit, "texts_sha256": job["texts_sha256"],
            "init_seed": T.init_seed(seed), "grad_scale": T.grad_scale(arm, int(texts["run"].shape[1])), "series": list(T.SERIES)}
    sha = LR.write_unit(SR.unit_path(ctx, name), {**out, "batch_index": np.arange(1, n + 1), "meta": np.array(json.dumps(meta, sort_keys=True))})
    ctx.log(event="unit_finished", unit=name, sha256=sha)
    return _return(ctx, spec, [{"unit": name, "sha256": sha, "guards": {"written": True}, "skipped": False}], removed)


def rehearsal_job(model: Any, ctx: SR.Context, spec: dict[str, Any], texts: dict[str, np.ndarray]) -> dict[str, Any]:
    job = spec["job"]
    name = "rehearsal"
    removed = SR.clean_unfinished(ctx, [name])
    skipped = _done(ctx, name)
    if skipped is not None:
        return _return(ctx, spec, [skipped], removed)
    ctx.timings["to_ready"] = time.time() - ctx.t0
    ctx.log(event="container_started", container=f"{ARM}|rehearsal", count=removed)
    arrays: dict[str, np.ndarray] = {}
    for arm in T.ARMS:
        t0 = time.time()
        out = run_arm(model, ctx, arm, int(job["seed"]), texts["calibration"][: int(job["n_batches"])], record_sources=(arm == "batch"))
        ctx.tick(f"arm_{arm}", time.time() - t0, int(job["n_batches"]))
        for k, v in out.items():
            if k != "sources":
                arrays[f"{arm}|{k}"] = v
    t0 = time.time()
    meta = {"unit": name, "stage": "rehearsal", "commit": ctx.commit, "texts_sha256": job["texts_sha256"], "timings": dict(ctx.timings)}
    sha = LR.write_unit(SR.unit_path(ctx, name), {**arrays, "meta": np.array(json.dumps(meta, sort_keys=True))})
    ctx.tick("unit_write", time.time() - t0)
    ctx.log(event="unit_finished", unit=name, sha256=sha)
    return _return(ctx, spec, [{"unit": name, "sha256": sha, "guards": {"written": True}, "skipped": False}], removed)


def _equal_sources(a: Any, b: Any) -> bool:
    import torch

    return all(torch.equal(a.sources[k], b.sources[k]) for k in a.sources)


def gate_job(model: Any, ctx: SR.Context, spec: dict[str, Any], texts: dict[str, np.ndarray]) -> dict[str, Any]:
    """The gate on one calibration batch (see the module docstring)."""
    import torch

    from param_decomp.utils.general_utils import bf16_autocast

    name = "gate"
    removed = SR.clean_unfinished(ctx, [name])
    skipped = _done(ctx, name)
    if skipped is not None:
        return _return(ctx, spec, [skipped], removed)
    ac = _autocast(ctx)
    tokens = texts["calibration"][int(spec["job"]["batch_index"])]
    n, seq = int(tokens.shape[0]), int(tokens.shape[1])
    prep = T.prepare(model, _ids(ctx, tokens), autocast=ac)
    wd = T.weight_deltas(model)
    seed = T.init_seed(SEEDS[0])
    out: dict[str, Any] = {"arms": {}}
    for arm in GATE_ARMS:
        ours = T.make_state(model, arm, n, seq, ctx.device, seed, scale=1.0)
        ref = T.make_state(model, arm, n, seq, ctx.device, seed, scaled=False)
        start_equal = _equal_sources(ours, ref)
        r = T.batch_step(ours, model, prep, wd, step=0, total_steps=N_MAX, autocast=ac, record_after=False)
        ref.update_lr(0, N_MAX)  # run_param_decomp.py at the tag, lines 277 to 336, for the persistent term alone
        with bf16_autocast(enabled=ac):
            ref.warmup(model=model, batch=prep.ids, target_out=prep.target_out, ci=prep.ci, weight_deltas=wd)
            loss = ref.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
        grads = ref.get_grads(loss, retain_graph=True)
        ref.step(grads)
        out["arms"][arm] = {"start_equal": bool(start_equal), "our_loss": r["loss"], "authors_loss": float(loss.detach()),
                            "loss_bits_equal": bool(np.float64(r["loss"]).tobytes() == np.float64(float(loss.detach())).tobytes()),
                            "sources_bits_equal": bool(_equal_sources(ours, ref)), "before": r["before"]}
        del ours, ref, grads, loss
        gc.collect()
    # (2) the scaled gradient, released scope, at a fresh state
    a = T.make_state(model, "released", n, seq, ctx.device, seed, scaled=False)
    b = T.make_state(model, "released", n, seq, ctx.device, seed)
    with bf16_autocast(enabled=ac):
        la = a.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
        lb = b.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
    ga, gb = a.get_grads(la, retain_graph=False), b.get_grads(lb, retain_graph=False)
    scale = b.grad_scale
    normal = mism = 0
    tiny_below_eps = total = 0
    for k in ga:
        big = (scale * ga[k]).abs() > 1e-30
        normal += int(big.sum())
        mism += int((gb[k][big] != scale * ga[k][big]).sum())
        total += int(ga[k].numel())
        tiny_below_eps += int((ga[k].abs() < 1e-8).sum())
    scaled_below_eps = sum(int((gb[k].abs() < 1e-8).sum()) for k in gb)
    out["scaled_gradient"] = {"scale": scale, "entries_compared": normal, "mismatches": mism, "entries": total,
                              "share_below_eps_unscaled": tiny_below_eps / total, "share_below_eps_scaled": scaled_below_eps / total}
    del a, b, ga, gb, la, lb
    gc.collect()
    # (3) per document against per position holding the same values
    doc = T.make_state(model, "per_document", n, seq, ctx.device, seed, scale=1.0)
    pos = T.make_state(model, "released", n, seq, ctx.device, seed, scale=1.0)
    with torch.no_grad():
        for k in pos.sources:
            pos.sources[k].copy_(doc.sources[k].expand_as(pos.sources[k]))
        with bf16_autocast(enabled=ac):
            ld = doc.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
            lp = pos.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
    out["per_document_loss_bits_equal"] = bool(torch.equal(ld, lp))
    del doc, pos
    gc.collect()
    # (4) description: our 64-text released state against one training process's 4 texts, from the same sources
    ours = T.make_state(model, "released", n, seq, ctx.device, seed)
    k4 = T.TEXTS_PER_PROCESS
    ref4 = T.make_state(model, "released", k4, seq, ctx.device, seed, scaled=False)
    with torch.no_grad():
        for k in ref4.sources:
            ref4.sources[k].copy_(ours.sources[k][:k4])
    T.batch_step(ours, model, prep, wd, step=0, total_steps=N_MAX, autocast=ac, record_after=False)
    prep4 = T.Prepared(ids=prep.ids[:k4], target_out=prep.target_out[:k4], ci={k: v[:k4] for k, v in prep.ci.items()})
    T.batch_step(ref4, model, prep4, wd, step=0, total_steps=N_MAX, autocast=ac, record_after=False)
    diffs = [float((ours.sources[k][:k4] - ref4.sources[k]).detach().abs().max()) for k in ours.sources]
    same = sum(int((ours.sources[k][:k4] == ref4.sources[k]).detach().sum()) for k in ours.sources)
    count = sum(int(ref4.sources[k].numel()) for k in ref4.sources)
    out["process_emulation"] = {"max_abs_source_difference": max(diffs), "share_equal": same / count}
    del ours, ref4
    out["passes"] = bool(out["arms"]["released"]["start_equal"] and out["arms"]["released"]["loss_bits_equal"]
                         and out["arms"]["released"]["sources_bits_equal"] and out["scaled_gradient"]["mismatches"] == 0 and out["per_document_loss_bits_equal"])
    meta = {"unit": name, "stage": "gate", "commit": ctx.commit, "texts_sha256": spec["job"]["texts_sha256"], "result": out}
    sha = LR.write_unit(SR.unit_path(ctx, name), {"meta": np.array(json.dumps(meta, sort_keys=True))})
    ctx.log(event="unit_finished", unit=name, sha256=sha)
    return _return(ctx, spec, [{"unit": name, "sha256": sha, "guards": {"gate_passes": out["passes"]}, "skipped": False}], removed)


def carry_job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]],
              read_sources: Callable[[str, str], np.ndarray]) -> dict[str, Any]:
    """The batch arm's settings on the held-out batches, through the lead's scoring path, labels checked."""
    from vpd_audit_2 import adversary as A
    from vpd_audit_2 import pilot as P

    name = "carry"
    removed = SR.clean_unfinished(ctx, [name])
    skipped = _done(ctx, name)
    if skipped is not None:
        return _return(ctx, spec, [skipped], removed)
    settings = spec["job"]["settings"]
    flats = {}
    for s in settings:
        src = read_sources(s["unit"], s["sha256"])  # the run unit, checked against the hash its container returned
        flats[s["key"]] = np.asarray(src[int(s["batch"]) - 1], dtype=np.float32)
    harms: dict[str, dict[str, float]] = {}
    for h in spec["job"]["batches"]:
        ids, rows = batch_inputs[h]
        if LR.sha_rows(ids) != list(rows):
            raise LR.GuardFailure("G1", f"container|{ARM}|{h}")
        prep = A.prepare(model, ids, "bf16" if ctx.device == "cuda" else "fp32", device=ctx.device)
        if ctx.mode != "test" and LR.prep_fingerprint(prep) != spec["refs"][h]["prep_fp"]:
            raise LR.GuardFailure("prep_fp_is_the_runs", f"container|{ARM}|{h}")
        harms[h] = {key: float(A.score(model, P.unflatten(flat, ctx.lay), prep, device=ctx.device)) for key, flat in flats.items()}
        del prep
        gc.collect()
    meta = {"unit": name, "stage": "carry", "commit": ctx.commit, "settings": settings, "harms": harms}
    sha = LR.write_unit(SR.unit_path(ctx, name), {"meta": np.array(json.dumps(meta, sort_keys=True))})
    ctx.log(event="unit_finished", unit=name, sha256=sha)
    return _return(ctx, spec, [{"unit": name, "sha256": sha, "guards": {"written": True}, "skipped": False}], removed)


def job(model: Any, ctx: SR.Context, spec: dict[str, Any], *, texts: dict[str, np.ndarray] | None = None,
        batch_inputs: dict[str, tuple[np.ndarray, list[str]]] | None = None, read_sources: Callable[[str, str], np.ndarray] | None = None) -> dict[str, Any]:
    check_environment(ctx)
    check_spec(spec)
    model.requires_grad_(False)
    st = spec["stage"]
    if st == "carry":
        return carry_job(model, ctx, spec, batch_inputs or {}, read_sources)
    if texts is None:
        raise ThreeArmFailure("no texts")
    if st == "gate":
        return gate_job(model, ctx, spec, texts)
    if st == "rehearsal":
        return rehearsal_job(model, ctx, spec, texts)
    return arm_job(model, ctx, spec, texts)


# ----------------------------------------------------------------------------- the local side: checks, money, launch


def tree_holds_only_this_plans_records() -> bool:
    top = Path(LL._git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    allowed = (RESULTS.resolve().relative_to(top)).as_posix() + "/"
    r = LL._git("status", "--porcelain", "--untracked-files=all", "--", ".")
    return r.returncode == 0 and all(line.startswith("?? ") and line[3:].strip('"').startswith(allowed) for line in r.stdout.splitlines())


def check_launch_commit(commit: str) -> None:
    if not tree_holds_only_this_plans_records():
        raise LL.LaunchRefusal("the tree is not clean under vpd-audit-2")
    if LL.head_commit() != commit or len(commit) != 40:
        raise LL.LaunchRefusal("the current commit is not the one named")
    missing = [rel for rel in READING_FILES + ("results/s7_three_arm/texts.json",) if LL.blob(commit, rel) is None]
    if missing:
        raise LL.LaunchRefusal("not committed: " + ", ".join(missing))
    changed = LL.run_files_changed(SR.RUN_COMMIT, commit)
    if changed:
        raise LL.LaunchRefusal("the label and scoring path has changed since the lead run: " + ", ".join(changed))


def _json(name: str) -> dict[str, Any] | None:
    p = RESULTS / name
    return json.load(open(p)) if p.is_file() else None


def timings() -> dict[str, float]:
    """Seconds per batch per arm and the time to ready, from the rehearsal's record (`rehearsal_command`)."""
    r = _json("rehearsal.json")
    if r is None:
        raise LL.LaunchRefusal("no rehearsal record: the stage cannot be projected")
    return r["projection_inputs"]


def stage_seconds(stage: str, t: dict[str, float], extension: dict[str, int] | None = None) -> dict[str, Any]:
    """A stage's function seconds: per container its time to ready, its batches at the arm's seconds per batch, and a
    unit write and commit allowance of 30 seconds. The carry stage is priced at 5 minutes, a bound."""
    if stage == "run":
        rows = [{"container": f"{a}|s{s}", "seconds": t["to_ready"] + N_BATCHES * t[f"per_batch_{a}"] + 30.0} for a in T.ARMS for s in SEEDS]
    elif stage == "extension":
        rows = [{"container": f"{a}|x", "seconds": t["to_ready"] + int(n) * t[f"per_batch_{a}"] + 30.0} for a, n in sorted((extension or {}).items())]
    elif stage == "carry":
        rows = [{"container": "carry", "seconds": 300.0}]
    elif stage == "rehearsal":
        rows = [{"container": "rehearsal", "seconds": 1200.0}]
    elif stage == "gate":
        rows = [{"container": "gate", "seconds": 900.0}]
    else:
        raise ValueError(stage)
    return {"stage": stage, "containers": rows, "seconds": float(sum(r["seconds"] for r in rows)), "lives": len(rows)}


def projection(stage: str, ledger: dict[str, Any], listed_hourly_price: float, bill: dict[str, Any] | None = None,
               extension: dict[str, int] | None = None) -> dict[str, Any]:
    """Before a stage: the money spent plus this stage and those that must follow it (the carry stage after the run;
    the extension is projected at its own launch, as amendment 6 says, within the cap), against $35. The gate and the
    rehearsal are priced at bounds, before any timing exists."""
    rest = {"gate": ("gate", "rehearsal"), "rehearsal": ("rehearsal",), "run": ("run", "carry"), "extension": ("extension",), "carry": ("carry",)}[stage]
    t = timings() if stage in ("run", "extension") else {}
    parts = [stage_seconds(s, t, extension) for s in rest]
    seconds = float(sum(p["seconds"] for p in parts))
    lives = float(sum(p["lives"] for p in parts))
    remaining = LG.money(seconds, lives, listed_hourly_price)
    c = LL.ledger_counts(ledger, bill)
    so_far = LG.money(c["function_seconds"], c["container_lives"], listed_hourly_price, c["billed"])
    total = so_far["dollars"] + remaining["dollars"]
    return {"check": f"before_{stage}", "stage": stage, "parts": parts, "remaining": remaining, "spent": so_far, "spent_dollars": so_far["dollars"],
            "remaining_dollars": remaining["dollars"], "projected_dollars": total, "cap": CAP_DOLLARS, "exceeds_cap": bool(total > CAP_DOLLARS),
            "listed_hourly_price": float(listed_hourly_price), "at": LL.utc_now()}


def launch_command(stage: str, commit: str, cloud: LL.Cloud, *, listed_hourly_price: float, refs: dict[str, Any] | None = None) -> dict[str, Any]:
    """One stage: the checks, the order, the projection on the ledger (over $35, nothing launches), then the stage's
    containers at once (`lead_launch.drive_stage`)."""
    if stage not in STAGES:
        raise LL.LaunchRefusal(f"no stage {stage}")
    check_launch_commit(commit)
    plan = _json("texts.json")
    if plan is None:
        raise LL.LaunchRefusal("no text plan")
    ledger_path = RESULTS / "ledger.json"
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("the three-arm experiment began at another commit")
    ledger = LL.read_ledger(ledger_path)
    need = {"gate": (), "rehearsal": ("gate",), "run": ("gate", "rehearsal"), "extension": ("run",), "carry": ("run",)}[stage]
    for before in need:
        if not any(n.startswith(f"s7_three_arm_{before}") and s.get("complete") for n, s in ledger["stages"].items()):
            raise LL.LaunchRefusal(f"the stage {before} is not complete")
    if stage != "gate":
        g = _json("gate.json")
        if g is None or g.get("commit") != commit or not g.get("passes"):
            raise LL.LaunchRefusal("the gate has not passed at this commit: nothing else runs")
    extension = carry = None
    if stage == "extension":
        x = _json("extension_plan.json")
        if x is None or x.get("commit") != commit or not x["containers"]:
            raise LL.LaunchRefusal("the extension rule does not call for an extension")
        extension = {k: int(v) for k, v in x["containers"].items()}
    if stage == "carry":
        c = _json("carry_plan.json")
        if c is None or c.get("commit") != commit:
            raise LL.LaunchRefusal("no carry plan at this commit")
        carry = c["settings"]
        if refs is None:
            lead = SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT)
            held = [str(x) for x in lead["heldout_names"]]
            refs = {h: {"prep_fp": str(lead["prep_fp_H"][held.index(h)])} for h in CARRY_BATCHES}
    bill = cloud.read_bill(LL.ledger_apps(ledger))
    check = projection(stage, ledger, listed_hourly_price, bill, extension)
    ledger["checks"].append(check)
    LL.write_json(ledger_path, ledger)
    if check["exceeds_cap"]:
        raise LL.LaunchRefusal(f"the projection before {stage} exceeds the cap: do not start; report to the head")
    sp = specs(stage, commit, plan["texts_file_sha256"], refs=refs, extension=extension, carry=carry)
    rec = stage_record(stage, len(sp))
    return LL.drive_stage(rec, sp, cloud, ledger_path=ledger_path, runs_path=RESULTS / f"runs_{stage}.json", design=(rec,), timings={},
                          listed_hourly_price=listed_hourly_price, cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


def collect_command(stage: str, commit: str, *, read_file: Callable[[str], bytes], log: Callable[..., None], dest: Path | None = None) -> dict[str, str]:
    """Every unit file of a finished stage off the volume as bytes, each checked against the hash its container
    returned; the receipt `backup.json` gains them."""
    if not tree_holds_only_this_plans_records() or LL.head_commit() != commit:
        raise LL.LaunchRefusal("the tree or the commit is not the launch's")
    run = json.load(open(RESULTS / f"runs_{stage}.json"))
    if run["commit"] != commit or not run["summary"]["complete"]:
        raise LL.LaunchRefusal("the stage is not complete at this commit")
    returned = {u["unit"]: u["sha256"] for c in run["containers"] for u in c["units"]}
    dest = LOCAL / UNITS if dest is None else dest
    receipt_path = RESULTS / "backup.json"
    receipt = json.load(open(receipt_path)) if receipt_path.is_file() else {"commit": commit, "files": {}}
    if receipt["commit"] != commit:
        raise LL.LaunchRefusal("the receipt is from another commit")
    for unit, sha in sorted(returned.items()):
        data = read_file(f"{VOLUME}/{UNITS}/{unit}.npz")
        if hashlib.sha256(data).hexdigest() != sha:
            raise LL.LaunchRefusal(f"the bytes of {unit} do not have the hash its container returned")
        dest.mkdir(parents=True, exist_ok=True)
        (dest / f"{unit}.npz").write_bytes(data)
        receipt["files"][f"{UNITS}/{unit}.npz"] = sha
    receipt["at"] = LL.utc_now()
    LL.write_json(receipt_path, receipt)
    log(event="backup_finished", container=stage, count=len(returned))
    return returned


def _unit(name: str, folder: Path | None = None) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    receipt = json.load(open(RESULTS / "backup.json"))
    data = ((LOCAL / UNITS if folder is None else folder) / f"{name}.npz").read_bytes()
    if hashlib.sha256(data).hexdigest() != receipt["files"].get(f"{UNITS}/{name}.npz"):
        raise LL.LaunchRefusal(f"{name} is not the file the receipt records")
    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files if k != "meta"}
        meta = json.loads(str(np.asarray(z["meta"]).reshape(-1)[0]))
    return arrays, meta


def gate_command(commit: str, *, folder: Path | None = None) -> dict[str, Any]:
    _, meta = _unit("gate", folder)
    if meta["commit"] != commit:
        raise LL.LaunchRefusal("the gate unit is from another commit")
    out = {"commit": commit, **meta["result"], "at": LL.utc_now()}
    LL.write_json(RESULTS / "gate.json", out)
    return out


def rehearsal_command(commit: str, *, folder: Path | None = None, listed_hourly_price: float | None = None) -> dict[str, Any]:
    """The rehearsal's record: per arm its steady seconds per batch (the batches after the first two), its peak memory,
    the time to ready; and the projection of the run and the carry stage at those timings."""
    arrays, meta = _unit("rehearsal", folder)
    if meta["commit"] != commit:
        raise LL.LaunchRefusal("the rehearsal unit is from another commit")
    t = {"to_ready": float(meta["timings"]["to_ready"])}
    per_arm = {}
    for arm in T.ARMS:
        sec = arrays[f"{arm}|seconds"]
        t[f"per_batch_{arm}"] = float(np.mean(sec[2:]))
        per_arm[arm] = {"seconds_per_batch": t[f"per_batch_{arm}"], "first_two": [float(x) for x in sec[:2]], "peak_gib": float(arrays[f"{arm}|peak_gib"][0])}
    out = {"commit": commit, "projection_inputs": t, "arms": per_arm, "at": LL.utc_now()}
    LL.write_json(RESULTS / "rehearsal.json", out)
    if listed_hourly_price is not None:
        ledger = LL.read_ledger(RESULTS / "ledger.json")
        out["projection_before_run"] = projection("run", ledger, listed_hourly_price)
        worst = {"released": N_MAX, "per_document": N_MAX}
        out["projection_of_the_largest_extension"] = projection("extension", ledger, listed_hourly_price, extension=worst)
        LL.write_json(RESULTS / "rehearsal.json", out)
    return out


def breakout(series: np.ndarray, level: float = 5.0) -> int | None:
    """Session 6's rule: the first batch b >= 2 whose two-batch mean (h[b-1] + h[b]) / 2, batches numbered from 1,
    reaches the level; None if none does."""
    h = np.asarray(series, dtype=np.float64)
    for b in range(2, h.size + 1):
        if 0.5 * (h[b - 2] + h[b - 1]) >= level:
            return b
    return None


def extension_lengths(yard: int | None, arms: dict[str, int | None]) -> dict[str, int]:
    """Amendment 6: with the yardstick's breakout batch b, each of arms 1 and 2 that has not broken out runs to
    min(10 b, 3,000) batches, where that is beyond the run's 1,000."""
    if yard is None:
        return {}
    n_ext = min(EXTENSION_FACTOR * int(yard), N_MAX)
    return {arm: n_ext for arm, b in sorted(arms.items()) if b is None and n_ext > N_BATCHES}


def run_unit_name(stage: str, arm: str, seed: int, n: int) -> str:
    return f"{stage}_{arm}_s{seed}_n{n}"


def extension_command(commit: str, *, folder: Path | None = None) -> dict[str, Any]:
    """Amendment 6's rule on the collected run: if the yardstick (seed 1) broke out at b on the governing series and
    arm 1 (seed 1) has not by batch 1,000, rerun arm 1, seed 1, to min(10 b, 3,000) batches, and arm 2, seed 1,
    likewise if it has not broken out; only where that exceeds 1,000."""
    s = EXTENSION_SEED
    yard = breakout(_unit(run_unit_name("run", "batch", s, N_BATCHES), folder)[0]["before"])
    arms = {arm: breakout(_unit(run_unit_name("run", arm, s, N_BATCHES), folder)[0]["before"]) for arm in ("released", "per_document")}
    containers = extension_lengths(yard, arms)
    out = {"commit": commit, "seed": s, "yardstick_breakout": yard, "breakouts": arms, "containers": containers, "at": LL.utc_now()}
    LL.write_json(RESULTS / "extension_plan.json", out)
    return out


def carry_command(commit: str, *, folder: Path | None = None) -> dict[str, Any]:
    """Which settings the carry stage scores: for each seed, the batch arm's source at its breakout batch on each of
    the two series, and at its last batch."""
    settings = []
    receipt = json.load(open(RESULTS / "backup.json"))["files"]
    for s in SEEDS:
        name = run_unit_name("run", "batch", s, N_BATCHES)
        arrays, _ = _unit(name, folder)
        sha = receipt[f"{UNITS}/{name}.npz"]
        points = {"breakout_before": breakout(arrays["before"]), "breakout_loss": breakout(arrays["loss"]), "last": N_BATCHES}
        for label, b in points.items():
            if b is not None:
                settings.append({"key": f"s{s}|{label}|{b}", "seed": s, "label": label, "batch": int(b), "unit": name, "sha256": sha})
    out = {"commit": commit, "settings": settings, "at": LL.utc_now()}
    LL.write_json(RESULTS / "carry_plan.json", out)
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 1 and argv[0] == "texts":
        plan = write_texts()
        sys.stdout.write(f"texts: {len(plan['run_positions'])} run rows of {plan['unused_attack_rows']} unused attack rows; file {plan['texts_file_sha256']}\n")
        return 0
    if len(argv) == 3 and argv[1] == "--commit" and argv[0] in ("gate", "rehearsal", "extension", "carry"):
        from vpd_audit_2 import modal_lead as ML

        fn = {"gate": gate_command, "rehearsal": lambda c: rehearsal_command(c, listed_hourly_price=ML._listed_hourly_price()),
              "extension": extension_command, "carry": carry_command}[argv[0]]
        sys.stdout.write(json.dumps(fn(argv[2]), indent=1, default=str)[:6000] + "\n")
        return 0
    sys.stderr.write("usage: python -m vpd_audit_2.three_arm_run texts | {gate,rehearsal,extension,carry} --commit <c>\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
