"""Session 7, plan 5: probe 1 on the GPU, and its local side, with no cloud call in it (`modal_probe1.py` hands it the
cloud). The specification is `sessions/007/notes/daniel/probe1_spec.md` with the plan's six amendments.

Three stages, in this order, one commit for all of them:

  - "validation" (one container, H1): the note's Section 2 check on the setting of A1 from start 9 at 320 steps, the
    first attack search (session 6's check cell): eight texts of H1 drawn by a seed; every first-order push on them;
    200 off-set components, 20 from each decile of |p| (`probe1.validation_components`); the exact one-at-a-time
    moves of those 1,600 pairs. Then timing cells on the whole of H1 (A1's five searches, at both lengths, nothing kept)
    for the projection, and the rounded pattern's damage on H1 against session 6's control (d). The pass rule is applied
    locally (`validate_command`), and nothing else launches unless it passed.
  - "s320": the 80 attack searches' settings at 320 steps, each on its own attack batch and on the 16 held-out batches.
  - "s80": the same at 80 steps, as description.

A scoring container takes two held-out batches, or eight attack batches; it never receives the other side's token
ids. For each batch: its labels are prepared in the run's precision and checked against the run's fingerprint
(`prep_fp_H`, `prep_fp_A` of the lead table), cast to float32, and the weight deltas computed in float32; then for each
chunk of 64 texts, the intact model's forward is kept (`probe1.IntactGraph`) and checked against the target model, and
each setting is one unit: the pattern's forward, the reference direction, and one backward pass per point
(`probe1.cell`). Everything on the probe's side runs in float32, TF32 off, deterministic algorithms on.

A unit file `<stage>_<batch>_<attack>_s<start>_c<chunk>.npz` holds, for its 64 texts: every entry's push at each point
(float32, [64, 38,936]), sum_t |Delta(x, t)|, the count of positions with a zero direction, and the pattern's mean KL
from the intact model; its meta names the setting, its hashes, the batch's fingerprint, the commit, and the intact
model's check. Units are restartable: a finished unit is skipped after checking its commit and fingerprint. Nothing a
container returns holds a push: unit names, hashes, guard outcomes, counts, seconds, and timings.

Money (`lead_ledger.money`): before each stage, what has been spent plus the projection of every stage still to run,
against the cap of $20; over it, nothing launches. The validation stage is projected at a bound; the scoring stages from
the validation container's own timings.
"""

from __future__ import annotations

import gc
import hashlib
import json
import os
import sys
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import probe1 as P1
from vpd_audit_2 import probe1_read as RD
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s7_probe1"
VOLUME = "/cache/s7_probe1"
LOCAL = REPO_ROOT / ".cache" / "s7_probe1"  # `.cache/` is ignored by git
RUN = "s7_probe1"
PART = "probe1"
ARM = "s7_probe1"
MODE = "s7_probe1"
UNITS = "units"
TIMING = "timing"  # scratch for the validation container's write timings; emptied before it returns
CAP_DOLLARS = 20.0  # the plan: the GPU cap
CHUNK = 64
N_TEXTS = 128
COMMIT_EVERY = 20
INTACT_KL_GUARD = 1e-4  # nats: the intact model's largest per-text mean KL from the target model's own forward
ATTACK = SR.ATTACK
HELDOUT = SR.HELDOUT
STARTS = SR.STARTS
STAGE_ORDER = ("validation", "s320", "s80")
STAGE_ROW = {"validation": "n320", "s320": "n320", "s80": "n80"}
DEFAULT_POINTS = {"validation": ("intact", "pattern"), "s320": ("intact", "pattern"), "s80": ("intact",)}
ALLOWED_POINTS = (("intact",), ("intact", "pattern"))
VALIDATION = {"batch": "H1", "attack": "A1", "start": 9, "row": "n320"}
VALIDATION_TEXTS_LABEL = "probe1-validation-texts"
VALIDATION_COMPONENTS_LABEL = "probe1-validation-components"
VALIDATION_BOUND_SECONDS = 1500.0  # the validation stage's projection before it runs: 25 minutes of one container
READING_FILES = ("vpd_audit_2/probe1.py", "vpd_audit_2/probe1_run.py", "vpd_audit_2/modal_probe1.py", "vpd_audit_2/probe1_read.py")
RUN_UNITS_LOCAL = REPO_ROOT / ".cache" / "s5_lead_units" / "run" / "lead"
SPEC_KEYS = {"part", "arm", "stage", "side", "batch", "batches", "commit", "mode", "root", "units", "run", "row", "points", "attack_batches", "starts",
             "refs"}


def heldout_groups() -> tuple[tuple[str, ...], ...]:
    return tuple(tuple(HELDOUT[k : k + 2]) for k in range(0, len(HELDOUT), 2))


def attack_groups() -> tuple[tuple[str, ...], ...]:
    half = (len(ATTACK) + 1) // 2
    return (tuple(ATTACK[:half]), tuple(ATTACK[half:]))


def n_containers(stage: str) -> int:
    return 1 if stage == "validation" else len(heldout_groups()) + len(attack_groups())


def stage_record(stage: str) -> LG.Stage:
    return LG.Stage(f"s7_probe1_{stage}", ARM, "heldout" if stage == "validation" else "both", n_containers(stage), 0, 0, 0, 0, 0, False)


class ProbeFailure(Exception):
    """A check in a container failed; the message names it and holds no value."""


# ----------------------------------------------------------------------------- what each container is handed


def specs(stage: str, commit: str, refs: dict[str, Any], points: tuple[str, ...]) -> list[dict[str, Any]]:
    base = {"part": PART, "arm": ARM, "stage": stage, "commit": commit, "mode": MODE, "root": VOLUME, "units": UNITS, "run": RUN, "row": STAGE_ROW[stage],
            "points": list(points), "attack_batches": list(ATTACK), "starts": list(STARTS)}
    if stage == "validation":
        h = VALIDATION["batch"]
        return [{**base, "side": "heldout", "batch": h, "batches": [h], "refs": {h: refs[h]}}]
    out = [{**base, "side": "heldout", "batch": "+".join(g), "batches": list(g), "refs": {b: refs[b] for b in g}} for g in heldout_groups()]
    out += [{**base, "side": "attack", "batch": "+".join(g), "batches": list(g), "refs": {b: refs[b] for b in g}} for g in attack_groups()]
    return out


def check_spec(spec: dict[str, Any]) -> None:
    stage = spec.get("stage")
    groups = {"heldout": heldout_groups(), "attack": attack_groups()}
    ok = (set(spec) - {"launch"} == SPEC_KEYS and spec["part"] == PART and spec["arm"] == ARM and stage in STAGE_ORDER and spec["mode"] == MODE
          and spec["root"] == VOLUME and spec["units"] == UNITS and spec["run"] == RUN and len(str(spec["commit"])) == 40 and spec["row"] == STAGE_ROW[stage]
          and tuple(spec["points"]) in ALLOWED_POINTS and tuple(spec["attack_batches"]) == ATTACK and tuple(spec["starts"]) == STARTS
          and set(spec["refs"]) == set(spec["batches"]) and spec["batch"] == "+".join(spec["batches"]))
    if ok and stage == "validation":
        ok = spec["side"] == "heldout" and spec["batches"] == [VALIDATION["batch"]] and tuple(spec["points"]) == DEFAULT_POINTS["validation"]
    elif ok:
        ok = spec["side"] in groups and tuple(spec["batches"]) in groups[spec["side"]]
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('part')}|{spec.get('batch')}")


def settings_for(spec: dict[str, Any], batch: str) -> list[tuple[str, int]]:
    """The attack searches whose settings a batch scores: all 80 on a held-out batch, its own five on an attack batch."""
    if spec["side"] == "heldout":
        return [(a, int(s)) for a in spec["attack_batches"] for s in spec["starts"]]
    return [(batch, int(s)) for s in spec["starts"]]


def container_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                     pools: dict[str, Any] | None = None) -> dict[str, tuple[np.ndarray, list[str]]]:
    """The token ids of the container's batches, each a pool of its side; no other batch's ids."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = LL._manifest()["pools"] if pools is None else pools
    want = {"heldout": "H", "attack": "A"}[spec["side"]]
    out = {}
    for b in spec["batches"]:
        if pools[b]["pool"] != want:
            raise LL.LaunchRefusal(f"batch {b} is not a pool of the {spec['side']} side")
        ids, _texts, rows = load_ids(b)
        out[b] = (ids, list(rows))
    return out


def references(lead: dict[str, Any], s6_rounded: float | None = None) -> dict[str, Any]:
    """Per batch, the run's label fingerprint; for the validation batch, the saved harms its check is read against."""
    att = [str(x) for x in lead["attack_names"]]
    held = [str(x) for x in lead["heldout_names"]]
    starts = [int(x) for x in lead["starts"]]
    out: dict[str, Any] = {h: {"prep_fp": str(lead["prep_fp_H"][j])} for j, h in enumerate(held)}
    out.update({a: {"prep_fp": str(lead["prep_fp_A"][i])} for i, a in enumerate(att)})
    names = [str(x) for x in lead["setting_names"]]
    v = VALIDATION
    i, j, k = att.index(v["attack"]), held.index(v["batch"]), starts.index(v["start"])
    out[v["batch"]] = {**out[v["batch"]], "lead_carried": float(lead["carried"][i, j, k, names.index(v["row"])]), "s6_rounded": s6_rounded}
    return out


# ----------------------------------------------------------------------------- in the container


def check_environment(ctx: SR.Context) -> None:
    """The lead run's configuration (B200, deterministic algorithms, TF32 off, the commit, a clean tree); the labels
    are prepared in the run's bfloat16. The tiny model's tests (mode "test") skip it."""
    if ctx.mode == "test":
        return
    env = ctx.environment
    ok = (ctx.mode == MODE and ctx.precision == "bf16" and ctx.device == "cuda" and "B200" in str(env.get("gpu")) and env.get("deterministic_algorithms") is True
          and env.get("deterministic_warn_only") is False and env.get("allow_tf32_matmul") is False and env.get("allow_tf32_cudnn") is False
          and env.get("cublas_workspace_config") == ":4096:8" and env.get("vpd_audit_2_commit") == ctx.commit and env.get("vpd_audit_2_dirty") == "0")
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ARM}")


def unit_name(stage: str, batch: str, attack: str, start: int, chunk: int) -> str:
    return RD.unit_name(stage, batch, attack, start, chunk)


def validation_unit_name() -> str:
    v = VALIDATION
    return f"validation_{v['batch']}_{v['attack']}_s{v['start']}_{v['row']}"


def _sync(ctx: SR.Context) -> None:
    if ctx.device == "cuda":
        import torch

        torch.cuda.synchronize()


def _peak(ctx: SR.Context) -> None:
    if ctx.device == "cuda":
        import torch

        ctx.timings["peak_gib_allocated"] = max(ctx.timings.get("peak_gib_allocated", 0.0), torch.cuda.max_memory_allocated() / 2**30)
        ctx.timings["peak_gib_reserved"] = max(ctx.timings.get("peak_gib_reserved", 0.0), torch.cuda.max_memory_reserved() / 2**30)


def prepare_checked(model: Any, ctx: SR.Context, batch: str, ids: np.ndarray, rows: list[str], expected_fp: str) -> tuple[P1.Batch, str]:
    """The batch's labels in the run's precision, checked against the run's fingerprint; then the probe's float32 batch."""
    if LR.sha_rows(ids) != list(rows):
        raise LR.GuardFailure("G1", f"container|{ARM}|{batch}")
    t0 = time.time()
    prep = ctx.prepare(model, ids, ctx.precision, device=ctx.device)
    fp = LR.prep_fingerprint(prep)
    if fp != expected_fp:
        raise LR.GuardFailure("prep_fp_is_the_runs", f"container|{ARM}|{batch}")
    full = P1.as_float32_batch(model, prep, ctx.lay)
    del prep
    gc.collect()
    _sync(ctx)
    ctx.tick("prep_batch", time.time() - t0)
    return full, fp


def unit_arrays(out: dict[str, Any], texts: np.ndarray, meta: dict[str, Any]) -> dict[str, np.ndarray]:
    arrays = {"texts": np.asarray(texts, dtype=np.int64), "delta_norm_sum": np.asarray(out["delta_norm_sum"], dtype=np.float64),
              "zero_direction_positions": np.asarray(out["zero_direction_positions"], dtype=np.int64),
              "pattern_kl": np.asarray(out["pattern_kl"], dtype=np.float64), "meta": np.array(json.dumps(meta, sort_keys=True))}
    for p in P1.POINTS:
        if p in out:
            arrays[p] = np.ascontiguousarray(out[p], dtype=np.float32)
    return arrays


def _setting_reader(read_run_unit: Callable[[str, int], dict[str, np.ndarray]], row: str) -> Callable[[str, int], np.ndarray]:
    cache: dict[tuple[str, int], np.ndarray] = {}

    def get(attack: str, start: int) -> np.ndarray:
        if (attack, start) not in cache:
            cache[(attack, start)] = B.saved(read_run_unit(attack, start), row)[0]
        return cache[(attack, start)]

    return get


def scoring_job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]],
                read_run_unit: Callable[[str, int], dict[str, np.ndarray]], *, chunk: int = CHUNK) -> dict[str, Any]:
    stage, row, points = spec["stage"], spec["row"], tuple(spec["points"])
    setting = _setting_reader(read_run_unit, row)
    out_units: list[dict[str, Any]] = []
    expected, written, removed, stopped = 0, 0, 0, False
    for batch in spec["batches"]:
        ids, rows = batch_inputs[batch]
        n = int(np.asarray(ids).shape[0])
        if n % chunk:
            raise ProbeFailure(f"{batch}: {n} texts are not whole chunks of {chunk}")
        chunks = list(range(n // chunk))
        settings = settings_for(spec, batch)
        names = {(a, s, c): unit_name(stage, batch, a, s, c) for c in chunks for a, s in settings}
        expected += len(names)
        removed += SR.clean_unfinished(ctx, list(names.values()))
        if all(LR.finished(SR.unit_path(ctx, nm)) for nm in names.values()):
            todo_any = False
        else:
            todo_any = True
        full, fp = prepare_checked(model, ctx, batch, ids, rows, spec["refs"][batch]["prep_fp"]) if todo_any else (None, spec["refs"][batch]["prep_fp"])
        if "to_ready" not in ctx.timings:
            ctx.timings["to_ready"] = time.time() - ctx.t0
        ctx.log(event="container_started", container=f"{ARM}|{stage}|{batch}", count=removed)
        for c in chunks:
            todo = []
            for a, s in settings:
                path = SR.unit_path(ctx, names[(a, s, c)])
                if LR.finished(path):
                    m = SR.unit_meta(path)
                    if m["commit"] != ctx.commit or m["prep_fp"] != fp:
                        raise ProbeFailure(f"{names[(a, s, c)]}: a finished unit from another commit or other labels")
                    out_units.append({"unit": names[(a, s, c)], "sha256": LR.marker(path).read_text(), "guards": {"skipped_after_restart": True}, "skipped": True})
                else:
                    todo.append((a, s))
            if not todo:
                continue
            if ctx.should_stop():
                stopped = True
                break
            texts = np.arange(c * chunk, (c + 1) * chunk)
            sub = full.take(slice(c * chunk, (c + 1) * chunk))
            t0 = time.time()
            graph = P1.IntactGraph(model, sub)
            _sync(ctx)
            ctx.tick("intact_graph", time.time() - t0)
            chk = P1.intact_against_target(model, sub, graph.logits)
            if not chk["max_text_kl"] <= INTACT_KL_GUARD:
                raise ProbeFailure(f"{batch} chunk {c}: the intact model is not the target model")
            for a, s in todo:
                if ctx.should_stop():
                    stopped = True
                    break
                flat = setting(a, s)
                t0 = time.time()
                res = P1.cell(model, sub, graph, flat, points)
                _sync(ctx)
                ctx.tick("cell_" + "_".join(points), time.time() - t0)
                name = names[(a, s, c)]
                meta = {"unit": name, "stage": stage, "batch": batch, "attack": a, "start": s, "row": row, "chunk": c, "points": list(points),
                        "setting_sha": B.sha(flat), "rounded_sha": B.sha(P1.rounded(flat)), "prep_fp": fp, "commit": ctx.commit,
                        "intact_against_target": chk, "dtype": "float32", "n_entries": int(flat.size)}
                t0 = time.time()
                sha = LR.write_unit(SR.unit_path(ctx, name), unit_arrays(res, texts, meta))
                ctx.tick("unit_write", time.time() - t0)
                ctx.log(event="unit_finished", unit=name, sha256=sha)
                out_units.append({"unit": name, "sha256": sha, "guards": {"intact_is_the_target": True, "prep_fp_is_the_runs": True}, "skipped": False})
                written += 1
                if written % COMMIT_EVERY == 0:
                    t0 = time.time()
                    ctx.commit_volume()
                    ctx.tick("volume_commit", time.time() - t0)
                del res
            _peak(ctx)
            graph.release()
            del graph, sub
            gc.collect()
            if stopped:
                break
        del full
        gc.collect()
        if ctx.device == "cuda":
            import torch

            torch.cuda.empty_cache()
        if stopped:
            break
    t0 = time.time()
    ctx.commit_volume()
    ctx.tick("volume_commit", time.time() - t0)
    return {"container": f"{ARM}|{stage}|{spec['side']}|{spec['batch']}", "units": out_units, "finished_units": len(out_units), "expected_units": expected,
            "stopped": bool(stopped), "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment),
            "timings": {k: float(v) for k, v in ctx.timings.items()}, "removed_unfinished": int(removed)}


def validation_texts(n_batch: int, n: int) -> np.ndarray:
    from vpd_audit_2.manifest import seed_of

    return np.sort(np.random.default_rng(seed_of(VALIDATION_TEXTS_LABEL, VALIDATION["batch"])).choice(n_batch, size=n, replace=False)).astype(np.int64)


def validation_job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]],
                   read_run_unit: Callable[[str, int], dict[str, np.ndarray]], *, chunk: int = CHUNK, scratch: Path | None = None,
                   n_texts: int = P1.VALIDATION_TEXTS, per_decile: int = P1.VALIDATION_PER_DECILE) -> dict[str, Any]:
    """The note's Section 2 check and the timing cells; one unit."""
    from vpd_audit_2.manifest import seed_of

    v = VALIDATION
    batch = v["batch"]
    name = validation_unit_name()
    path = SR.unit_path(ctx, name)
    removed = SR.clean_unfinished(ctx, [name])
    ids, rows = batch_inputs[batch]
    ref = spec["refs"][batch]
    if LR.finished(path):
        m = SR.unit_meta(path)
        if m["commit"] != ctx.commit or m["prep_fp"] != ref["prep_fp"]:
            raise ProbeFailure("the finished validation unit is from another commit or other labels")
        units = [{"unit": name, "sha256": LR.marker(path).read_text(), "guards": {"skipped_after_restart": True}, "skipped": True}]
        return {"container": f"{ARM}|validation|heldout|{batch}", "units": units, "finished_units": 1, "expected_units": 1, "stopped": False,
                "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment), "timings": {k: float(v) for k, v in ctx.timings.items()},
                "removed_unfinished": int(removed)}
    ctx.timings["to_job"] = time.time() - ctx.t0
    full, fp = prepare_checked(model, ctx, batch, ids, rows, ref["prep_fp"])
    ctx.timings["to_ready"] = time.time() - ctx.t0
    ctx.log(event="container_started", container=f"{ARM}|validation|{batch}", count=removed)
    flat = B.saved(read_run_unit(v["attack"], v["start"]), v["row"])[0]
    lay = ctx.lay

    # the check: first-order pushes on the validation texts, 200 components, their exact moves
    t0 = time.time()
    texts = validation_texts(full.n_texts, n_texts)
    sub = full.take(texts.tolist())
    graph = P1.IntactGraph(model, sub)
    z_p, _ = P1.forward_at(model, sub, P1.pattern_point(flat), grad=False)
    direction, _norm = P1.reference_direction(z_p, graph.logits)
    first = graph.pushes(direction).detach().double().cpu().numpy()
    graph.release()
    del z_p, graph
    sets = RD.setting_sets(flat, lay)
    pick = P1.validation_components(first, sets["off"], seed_of(VALIDATION_COMPONENTS_LABEL, v["attack"], v["start"], RD.STEPS[v["row"]]),
                                    per_decile=per_decile)
    pairs = [(int(e), t) for t in range(len(texts)) for e in pick["components"]]
    ex = P1.exact_pushes(model, sub, pairs, direction, chunk=chunk)
    _sync(ctx)
    ctx.tick("validation_check", time.time() - t0)
    del sub, direction
    gc.collect()

    # timing cells on the whole batch, A1's five searches at both lengths; nothing is kept but their seconds, and the
    # rounded pattern's damage for the validation's own setting against session 6's control (d)
    unit_shape = (chunk, P1.n_entries(lay))
    kl_own: list[np.ndarray] = []
    chk_all: list[dict[str, float]] = []
    readers = {r: _setting_reader(read_run_unit, r) for r in ("n320", "n80")}
    for c in range(full.n_texts // chunk):
        sub = full.take(slice(c * chunk, (c + 1) * chunk))
        t0 = time.time()
        graph = P1.IntactGraph(model, sub)
        _sync(ctx)
        ctx.tick("intact_graph", time.time() - t0)
        chk_all.append(P1.intact_against_target(model, sub, graph.logits))
        for r, pts in (("n320", ("intact", "pattern")), ("n80", ("intact",))):
            for s in spec["starts"]:
                t0 = time.time()
                res = P1.cell(model, sub, graph, readers[r](v["attack"], int(s)), pts)
                _sync(ctx)
                ctx.tick("cell_" + "_".join(pts), time.time() - t0)
                if r == v["row"] and int(s) == v["start"]:
                    kl_own.append(res["pattern_kl"])
                if scratch is not None:
                    t0 = time.time()
                    tmp = Path(scratch) / f"timing_c{c}_{r}_s{s}.npz"
                    LR.write_unit(tmp, {"intact": np.zeros(unit_shape, dtype=np.float32), **({"pattern": np.zeros(unit_shape, dtype=np.float32)}
                                                                                           if "pattern" in pts else {})})
                    ctx.tick("unit_write_" + "_".join(pts), time.time() - t0)
                del res
        _peak(ctx)
        graph.release()
        del graph, sub
        gc.collect()
    if scratch is not None:
        t0 = time.time()
        ctx.commit_volume()
        ctx.tick("volume_commit", time.time() - t0)
        for p in sorted(Path(scratch).glob("timing_*")):
            p.unlink()
    for chk in chk_all:
        if not chk["max_text_kl"] <= INTACT_KL_GUARD:
            raise ProbeFailure("the intact model is not the target model")
    pattern_kl = float(np.mean(np.concatenate(kl_own)))
    meta = {"unit": name, "stage": "validation", "batch": batch, "attack": v["attack"], "start": v["start"], "row": v["row"], "prep_fp": fp,
            "commit": ctx.commit, "setting_sha": B.sha(flat), "rounded_sha": B.sha(P1.rounded(flat)), "texts": texts.tolist(),
            "left_out_zero": pick["left_out_zero"], "candidates": pick["candidates"], "pattern_kl_whole_batch": pattern_kl,
            "lead_carried": ref.get("lead_carried"), "s6_rounded": ref.get("s6_rounded"), "intact_against_target": chk_all,
            "timings": {k: float(x) for k, x in ctx.timings.items()}}
    arrays = {"texts": texts, "components": pick["components"], "decile": pick["decile"], "first": first.astype(np.float32),
              "pairs": np.asarray(pairs, dtype=np.int64), "first_at_pairs": np.array([first[t, e] for e, t in pairs], dtype=np.float64),
              "exact": ex["exact"], "null_spread": np.asarray(ex["null_spread"], dtype=np.float64), "meta": np.array(json.dumps(meta, sort_keys=True))}
    sha = LR.write_unit(path, arrays)
    ctx.log(event="unit_finished", unit=name, sha256=sha)
    ctx.commit_volume()
    units = [{"unit": name, "sha256": sha, "guards": {"prep_fp_is_the_runs": True, "intact_is_the_target": True}, "skipped": False}]
    return {"container": f"{ARM}|validation|heldout|{batch}", "units": units, "finished_units": 1, "expected_units": 1, "stopped": False,
            "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment), "timings": {k: float(x) for k, x in ctx.timings.items()},
            "removed_unfinished": int(removed)}


def job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]],
        read_run_unit: Callable[[str, int], dict[str, np.ndarray]], *, chunk: int = CHUNK, scratch: Path | None = None, **validation: Any) -> dict[str, Any]:
    """What a container runs: the validation, or one group of batches at one length."""
    check_environment(ctx)
    check_spec(spec)
    model.requires_grad_(False)
    if ctx.device == "cuda":
        import torch

        ctx.timings["device_gib"] = torch.cuda.get_device_properties(0).total_memory / 2**30
        torch.cuda.reset_peak_memory_stats()
    if spec["stage"] == "validation":
        return validation_job(model, ctx, spec, batch_inputs, read_run_unit, chunk=chunk, scratch=scratch, **validation)
    return scoring_job(model, ctx, spec, batch_inputs, read_run_unit, chunk=chunk)


# ----------------------------------------------------------------------------- the local side: checks, money, launch


def read_run_unit_local(attack: str, start: int) -> dict[str, np.ndarray]:
    """A run search unit from session 5's local copy, checked against the hash its backup recorded."""
    hashes = SR.run_unit_hashes()
    data = (RUN_UNITS_LOCAL / f"search_{attack}_s{start}.npz").read_bytes()
    if hashlib.sha256(data).hexdigest() != hashes[f"search_{attack}_s{start}.npz"]:
        raise LL.LaunchRefusal(f"search_{attack}_s{start}.npz is not the run's unit")
    return SR.run_unit_from_bytes(data, attack, start)


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
    missing = [rel for rel in READING_FILES if LL.blob(commit, rel) is None]
    if missing:
        raise LL.LaunchRefusal("not committed: " + ", ".join(missing))
    changed = LL.run_files_changed(SR.RUN_COMMIT, commit)
    if changed:
        raise LL.LaunchRefusal("the label and scoring path has changed since the lead run: " + ", ".join(changed))


def _rate(t: dict[str, float], key: str) -> float:
    n = t.get(key + "_count", 0.0)
    if n <= 0:
        raise LL.LaunchRefusal(f"the validation container has no timing of the kind {key}")
    return float(t[key] / n)


def stage_seconds(stage: str, points: tuple[str, ...], timings: dict[str, float]) -> dict[str, Any]:
    """A scoring stage's function seconds at the validation container's timings. Per container: its time to ready less
    its one batch's preparation (the model's load); per batch, a preparation and, per chunk, the intact forward; per
    unit, a cell at the stage's points and the write of a unit file of its size; and a volume commit every COMMIT_EVERY
    units and once at the end."""
    t = timings
    key = "_".join(points)
    load = float(t["to_ready"]) - _rate(t, "prep_batch")
    prep, graph = _rate(t, "prep_batch"), _rate(t, "intact_graph")
    per_unit = _rate(t, f"cell_{key}") + _rate(t, f"unit_write_{key}")
    commit = _rate(t, "volume_commit")
    n_chunks = N_TEXTS // CHUNK
    rows = []
    for side, groups in (("heldout", heldout_groups()), ("attack", attack_groups())):
        for g in groups:
            per_batch = len(ATTACK) * len(STARTS) if side == "heldout" else len(STARTS)
            units = len(g) * per_batch * n_chunks
            sec = load + len(g) * (prep + n_chunks * graph) + units * per_unit + (units // COMMIT_EVERY + 1) * commit
            rows.append({"container": "+".join(g), "units": units, "seconds": sec})
    return {"stage": stage, "points": list(points), "containers": rows, "seconds": float(sum(r["seconds"] for r in rows)),
            "units": int(sum(r["units"] for r in rows)), "per_unit_seconds": per_unit, "load_seconds": load}


def spent(ledger: dict[str, Any], listed_hourly_price: float, bill: dict[str, Any] | None) -> dict[str, Any]:
    c = LL.ledger_counts(ledger, bill)
    return LG.money(c["function_seconds"], c["container_lives"], listed_hourly_price, c["billed"])


def validation_record() -> dict[str, Any] | None:
    p = RESULTS / "validation.json"
    return json.load(open(p)) if p.is_file() else None


def projection(stage: str, points: tuple[str, ...], ledger: dict[str, Any], listed_hourly_price: float, bill: dict[str, Any] | None = None) -> dict[str, Any]:
    """Before a stage: the money spent, plus every stage still to run (this one at the points asked for, a later one at
    its default), against the cap. The validation stage is priced at its bound; the scoring stages at the validation
    container's timings, scaled up by the 320-step stage's measured over projected seconds once it has run."""
    rest = STAGE_ORDER[STAGE_ORDER.index(stage):]
    stages: list[dict[str, Any]] = []
    val = validation_record()
    scale = 1.0
    for st in rest:
        pts = points if st == stage else DEFAULT_POINTS[st]
        if st == "validation":
            stages.append({"stage": st, "seconds": VALIDATION_BOUND_SECONDS, "containers": [{"container": VALIDATION["batch"]}], "bound": True})
            continue
        if val is None:
            stages.append({"stage": st, "seconds": None, "note": "priced after the validation, from its timings"})
            continue
        s = stage_seconds(st, pts, val["timings"])
        done = ledger["stages"].get(stage_record("s320").name, {})
        if st == "s80" and done.get("complete"):
            measured = LL.stage_seconds_on(ledger, stage_record("s320").name)
            predicted = stage_seconds("s320", tuple(done.get("points", DEFAULT_POINTS["s320"])), val["timings"])["seconds"]
            scale = max(1.0, measured / predicted) if predicted > 0 else 1.0
            s["scaled_by_the_320_step_stage"] = scale
            s["seconds"] *= scale
        stages.append(s)
    seconds = float(sum(s["seconds"] for s in stages if s["seconds"] is not None))
    lives = float(sum(len(s["containers"]) for s in stages if s["seconds"] is not None))
    remaining = LG.money(seconds, lives, listed_hourly_price)
    so_far = spent(ledger, listed_hourly_price, bill)
    total = so_far["dollars"] + remaining["dollars"]
    return {"check": f"before_{stage}", "stage": stage, "points": list(points), "stages": stages, "remaining": remaining, "spent": so_far,
            "spent_dollars": so_far["dollars"], "remaining_dollars": remaining["dollars"], "projected_dollars": total, "cap": CAP_DOLLARS,
            "exceeds_cap": bool(total > CAP_DOLLARS), "listed_hourly_price": float(listed_hourly_price), "at": LL.utc_now()}


def launch_command(stage: str, commit: str, cloud: LL.Cloud, *, listed_hourly_price: float, points: tuple[str, ...] | None = None,
                   refs: dict[str, Any] | None = None) -> dict[str, Any]:
    """One stage: the commit and tree checks; the order (the validation passed before any scoring, the 320-step stage
    complete before the 80-step one); the projection against the cap, recorded on the ledger (over it, nothing
    launches); then the stage's containers at once (`lead_launch.drive_stage`)."""
    if stage not in STAGE_ORDER:
        raise LL.LaunchRefusal(f"no stage {stage}")
    points = DEFAULT_POINTS[stage] if points is None else tuple(points)
    if points not in ALLOWED_POINTS or (stage == "validation" and points != DEFAULT_POINTS["validation"]):
        raise LL.LaunchRefusal(f"points {points} are not allowed for {stage}")
    check_launch_commit(commit)
    ledger_path = RESULTS / "ledger.json"
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("probe 1 began at another commit")
    ledger = LL.read_ledger(ledger_path)
    for before in STAGE_ORDER[: STAGE_ORDER.index(stage)]:
        if not ledger["stages"].get(stage_record(before).name, {}).get("complete"):
            raise LL.LaunchRefusal(f"the stage {before} is not complete")
    if stage != "validation":
        val = validation_record()
        if val is None or val.get("commit") != commit or not val.get("passes"):
            raise LL.LaunchRefusal("the validation has not passed at this commit: nothing is scored (the note's fallback is the head's call)")
    bill = cloud.read_bill(LL.ledger_apps(ledger))
    check = projection(stage, points, ledger, listed_hourly_price, bill)
    ledger["checks"].append(check)
    LL.write_json(ledger_path, ledger)
    if check["exceeds_cap"]:
        raise LL.LaunchRefusal(f"the projection before {stage} exceeds the cap: do not start; report to the head")
    if refs is None:
        lead = SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT)
        refs = references(lead, s6_rounded_reference())
    ledger["stages"].setdefault(stage_record(stage).name, {"launches": [], "complete": False, "summary": None})["points"] = list(points)
    LL.write_json(ledger_path, ledger)
    return LL.drive_stage(stage_record(stage), specs(stage, commit, refs, points), cloud, ledger_path=ledger_path,
                          runs_path=RESULTS / f"runs_{stage}.json", design=(stage_record(stage),), timings={}, listed_hourly_price=listed_hourly_price,
                          cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


def s6_rounded_reference() -> float:
    v = VALIDATION
    return RD.s6_rounded_harms([v["batch"]], [v["attack"]], [v["start"]], [v["row"]])[(v["batch"], v["attack"], v["start"], v["row"])]


# ----------------------------------------------------------------------------- after a stage: the copy, and the validation's verdict


def expected_files(stage: str) -> dict[str, str]:
    if stage == "validation":
        return {validation_unit_name(): f"{UNITS}/{validation_unit_name()}.npz"}
    return {n: f"{UNITS}/{n}.npz" for n in RD.expected_units(stage, list(ATTACK), list(HELDOUT), list(STARTS))}


def collect_command(stage: str, commit: str, *, read_file: Callable[[str], bytes], log: Callable[..., None], dest: Path | None = None,
                    workers: int = 8) -> dict[str, str]:
    """Every unit file of a finished stage off the volume as bytes, each checked against the hash its container
    returned, to a folder git ignores; the receipt `backup.json` gains the stage's files."""
    if not tree_holds_only_this_plans_records() or LL.head_commit() != commit:
        raise LL.LaunchRefusal("the tree or the commit is not the launch's")
    run = json.load(open(RESULTS / f"runs_{stage}.json"))
    if run["commit"] != commit or not run["summary"]["complete"]:
        raise LL.LaunchRefusal("the stage is not complete at this commit")
    returned = {u["unit"]: u["sha256"] for c in run["containers"] for u in c["units"]}
    expected = expected_files(stage)
    if set(returned) != set(expected):
        raise LL.LaunchRefusal(f"the stage's record holds {len(returned)} units; the plan has {len(expected)}")
    dest = LOCAL if dest is None else dest
    receipt_path = RESULTS / "backup.json"
    receipt = json.load(open(receipt_path)) if receipt_path.is_file() else {"commit": commit, "files": {}}
    if receipt["commit"] != commit:
        raise LL.LaunchRefusal("the receipt is from another commit")

    def one(unit: str) -> tuple[str, str]:
        rel = expected[unit]
        target = dest / rel
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == returned[unit]:
            return rel, returned[unit]
        data = read_file(f"{VOLUME}/{rel}")
        if hashlib.sha256(data).hexdigest() != returned[unit]:
            raise LL.LaunchRefusal(f"the bytes of {rel} do not have the hash its container returned")
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, target)
        return rel, returned[unit]

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        files = dict(pool.map(one, sorted(expected)))
    receipt["files"].update(files)
    receipt["at"] = LL.utc_now()
    receipt["folder"] = str(dest.relative_to(REPO_ROOT)) if dest.is_relative_to(REPO_ROOT) else str(dest)
    LL.write_json(receipt_path, receipt)
    log(event="backup_finished", container=stage, count=len(files))
    return files


def validate_command(commit: str, *, units_folder: Path | None = None) -> dict[str, Any]:
    """The note's pass rule on the collected validation unit, written to `validation.json`, with the timings the
    scoring stages are projected from and the checks beside it."""
    receipt = json.load(open(RESULTS / "backup.json"))
    rel = f"{UNITS}/{validation_unit_name()}.npz"
    folder = (LOCAL if units_folder is None else Path(units_folder))
    data = (folder / rel).read_bytes()
    if receipt.get("commit") != commit or hashlib.sha256(data).hexdigest() != receipt["files"].get(rel):
        raise LL.LaunchRefusal("the validation unit is not the one collected at this commit")
    import io

    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files if k != "meta"}
        meta = json.loads(str(np.asarray(z["meta"]).reshape(-1)[0]))
    rule = P1.pass_rule(arrays["first_at_pairs"], arrays["exact"])
    by_decile = {}
    first, exact = arrays["first_at_pairs"], arrays["exact"]
    n_t = len(meta["texts"])
    dec = np.repeat(arrays["decile"][None, :], n_t, axis=0).reshape(-1)
    for d in sorted(set(dec.tolist())):
        sel = dec == d
        by_decile[str(d)] = {"pairs": int(sel.sum()), "sign_share": float((np.sign(first[sel]) == np.sign(exact[sel])).mean()),
                             "median_abs_first": float(np.median(np.abs(first[sel]))), "median_abs_exact": float(np.median(np.abs(exact[sel])))}
    out = {"commit": commit, **rule, "by_component_decile": by_decile, "null_spread_max": float(arrays["null_spread"].max()),
           "texts": meta["texts"], "components_left_out_as_zero": meta["left_out_zero"], "candidates": meta["candidates"],
           "pattern_kl_whole_batch_fp32": meta["pattern_kl_whole_batch"], "s6_rounded_bf16": meta["s6_rounded"], "lead_carried_bf16": meta["lead_carried"],
           "intact_against_target": meta["intact_against_target"], "timings": meta["timings"], "setting_sha": meta["setting_sha"], "at": LL.utc_now()}
    LL.write_json(RESULTS / "validation.json", out)
    (RESULTS / "validation.txt").write_text(validation_text(out))
    return out


def validation_text(v: dict[str, Any]) -> str:
    L = [f"Probe 1, validation (the note's Section 2): {'PASSED' if v['passes'] else 'FAILED'}.",
         f"  {v['pairs']} pairs; the bottom decile of |first-order p| is at {v['bottom_decile_cut']:.3e}; {v['pairs_above']} pairs above it.",
         f"  Sign share above the bottom decile {v['sign_share_above']:.4f} (rule: at least 0.9); over all pairs {v['sign_share_all']:.4f}.",
         f"  Spearman over all pairs {v['spearman_all']:.4f} (rule: at least 0.8); above the bottom decile {v['spearman_above']:.4f}; Pearson {v['pearson_all']:.4f}.",
         f"  Null rows: the largest logit difference between a text's null rows in different chunks {v['null_spread_max']:.2e}.",
         "  By component decile of |p| (sign share, median |first-order|, median |exact|):"]
    for d, x in v["by_component_decile"].items():
        L.append(f"    {d}: {x['sign_share']:.3f}, {x['median_abs_first']:.3e}, {x['median_abs_exact']:.3e}")
    L.append(f"  The rounded pattern's damage on H1 for the validation setting, float32 against the intact model: {v['pattern_kl_whole_batch_fp32']:.4f} nats; "
             f"session 6's rounded control (bfloat16, against the target) {v['s6_rounded_bf16']}; the lead's carried harm (unrounded) {v['lead_carried_bf16']}.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 3 and argv[0] == "validate" and argv[1] == "--commit":
        v = validate_command(argv[2])
        sys.stdout.write(validation_text(v))
        return 0 if v["passes"] else 1
    sys.stderr.write("usage: python -m vpd_audit_2.probe1_run validate --commit <c>\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
