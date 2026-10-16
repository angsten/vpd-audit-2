"""Plan 3 of the research log: the GPU work of Sections 4 and 7 in one launch, and its local side, with no cloud call in it
(plan 3 of the research log).

One stage of twelve containers, launched at once:

  - The first post's comparison rerun (Section 4; its rules are the research log's Appendix G.2 and the freeze
    file's Part 1, Section 7). Pool Q, the first post's 1,024 texts, as eight consecutive batches of 128 in the
    manifest's order (QB1 to QB8), each searched for 20 steps from starts 41 to 45 in two arms and scored on its own batch
    only. The searched arm runs `lead_run.search_unit`, the path of the run and the starts test, with the delta components
    searched. The held-at-0 arm runs `search_unit_frozen`: the same search with the 24 delta entries held at 0 through
    `adversary.Frozen.delta_entries(model, 0.0, ...)`, the held-at-0 path gate G2 proved bit-identical to the authors'.
    It is `lead_run.search_unit`'s delta-held path with the held value as an argument in place of its 1.0, and the
    start's delta entries at that value; at 1.0 it writes the same arrays as `lead_run.search_unit` with the delta
    entries held, bit for bit (tested). One container per batch, ten units: `search_<batch>_s<start>.npz` under
    `rerun/searched/` and `rerun/held_at_0/`. Each unit holds the setting after step 20 (and after 19), the per-text
    harms of the start and of each scored setting, and the harm record, as the run's units do.
  - Section 7's intact-background variants, added after the readings, as description. Cell set S4 (H1, H5, H9, H13), one
    container each: for each of the run's 80 attack searches, at each of the five lengths, V1, V2, and V3
    (`s6_build.zeros_alone`, `s6_build.variant_split_args`), scored through `s6_run`'s unit loop, after a check that the
    full setting reproduces the saved carried harm on both paths (the split's within the run's per-text tolerance with its
    bit equality recorded, as plan 2 of the research log checked it, and the flat path bit for bit).

The local side: `launch_command` (the commit and tree checks, the projection recorded as check C0, refused over either
cap, then `lead_launch.drive_stage`), and `collect_command` (every unit file off the volume as bytes, each checked
against the hash its container returned, to `.cache/s6_plan3/`, with the receipt `backup.json`).
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import pilot as P
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s6_plan3"
VOLUME = "/cache/s6_plan3"
LOCAL = REPO_ROOT / ".cache" / "s6_plan3"  # `.cache/` is ignored by git
RUN = "s6_plan3"  # the stop flag's name in the control dictionary
STARTS_JSON = REPO_ROOT / "results" / "s4_pilot" / "starts" / "starts_1_64.json"

# the comparison rerun (Section 4)
RERUN = "rerun"
POOL = "Q"
BATCH_SIZE = 128
BATCHES = tuple(f"QB{k}" for k in range(1, 9))
STARTS = (41, 42, 43, 44, 45)  # the freeze file, Part 1, Section 2: the rerun's starts
N_STEPS = 20
ARMS = ("searched", "held_at_0")
ARM_NAME = {"searched": "rerun_searched", "held_at_0": "rerun_held_at_0"}
HELD_VALUE = 0.0
RERUN_MODE = "s6_rerun"
RERUN_SIDE = "own"  # every search is scored on its own batch, and on no other
RERUN_SCORED_MAX = 4  # at 20 steps: the setting after step 20, and each harm level crossed by then

# the intact-background variants (Section 7)
VARIANTS = "variants"
VARIANT_BATCHES = B.S4
VARIANT_ARM = "s6_variants"

STAGE = LG.Stage("s6_plan3", "s6_plan3", "both", len(BATCHES) + len(VARIANT_BATCHES), 0, 0, 0, 0, 0, False)
DESIGN = (STAGE,)
RERUN_CAP = 6.0  # plan 3 of the research log, Section 4: stop above $6
CAP_DOLLARS = 11.0  # the rerun's $6 and the variants' estimated $5 (plan 3 of the research log, Section 7)
READING_FILES = ("vpd_audit_2/s6_plan3_run.py", "vpd_audit_2/modal_s6_plan3.py", "vpd_audit_2/s6_rerun.py", "vpd_audit_2/s6_variants.py",
                 "vpd_audit_2/s6_build.py", "vpd_audit_2/s6_run.py")
STARTS_TEST_RECORD = REPO_ROOT / "results" / "s6_starts" / "runs_starts_test.json"
PLAN2_RECORDS = (REPO_ROOT / "results" / "s6_followups" / "runs_s6_wave1.json", REPO_ROOT / "results" / "s6_followups" / "runs_s6_wave2.json")


# ----------------------------------------------------------------------------- the rerun's searches


@dataclass
class RerunContext(LR.Context):
    """The lead run's context, with the lead arm's scored settings (at 20 steps, the setting after step 20 and any harm
    level crossed by then) and the delta components searched, under an arm name of its own; `lead_run.ARMS` is not
    touched. The held-at-0 arm's units are written by `search_unit_frozen`, which takes the held value as an argument."""

    @property
    def settings(self) -> tuple[str, ...]:
        return LT.SETTINGS_LEAD

    @property
    def delta_held(self) -> bool:
        return False


def held_start(start: dict[str, np.ndarray], lay: list[tuple[str, int]], value: float) -> np.ndarray:
    """The start as a search with its delta entries held at `value` begins from it: flat, the delta entries at `value`."""
    flat = LR.flat_start(start, lay, False).copy()
    flat[LR.delta_positions(lay)] = np.float32(value)
    return flat


def search_unit_frozen(model: Any, prep: A.Prepared, ctx: LR.Context, side: str, batch: str, start_index: int, start: dict[str, np.ndarray],
                       batch_ids_sha: str, prep_fp: str, value: float) -> dict[str, Any]:
    """One search with the 24 delta entries held at `value`, and its own-batch re-scores: `lead_run.search_unit`'s
    delta-held path, line for line, with `value` in place of its 1.0."""
    unit = f"search|{ctx.arm}|{batch}|s{start_index}"
    path = LR.search_file(ctx.units, batch, start_index)
    if LR.finished(path):
        return LR._skip(ctx, path, unit, prep_fp)
    t_unit = time.time()
    hook = LR.TimedHook(steps=tuple(n for n in LR.HOOK_STEPS if n <= ctx.n_steps), thresholds=LR.LEVELS)
    frozen = A.Frozen.delta_entries(model, value, ctx.device)
    t0 = time.time()
    ctx.timings.setdefault("to_first_search_step", t0 - ctx.t0)
    r = ctx.run(model, prep, start, ctx.n_steps, LR.STEP, frozen=frozen, save_hook=hook, cum_grads=True, device=ctx.device)
    LR._tick_search(ctx, t0, time.time(), hook.at)
    record = [float(x) for x in r["record"]]

    # G7: the hook and the crossing rule agree, and are missing together
    for h in LR.LEVELS:
        if hook.events.get(f"two_step_mean_reaches_{h:g}") != P.crossing(record, h)["k"]:
            raise LR.GuardFailure("G7", unit)
    dpos = LR.delta_positions(ctx.lay)
    if any(not (flat[dpos] == np.float32(value)).all() for flat in hook.saved.values()):
        raise LR.GuardFailure("delta_entries_held", unit)

    # the starting point and every scored setting, re-scored on this batch through the per-text path
    LR._peak_reset(ctx)
    t0 = time.time()
    first = held_start(start, ctx.lay, value)
    init, init_text = A.score_per_text(model, P.unflatten(first, ctx.lay), prep, device=ctx.device)
    if LR._bits(init) != LR._bits(record[0]):
        raise LR.GuardFailure("G4", unit)
    LR._g5(init, init_text, unit)
    scored = [name for name in ctx.settings if LR.SAVED[name] in hook.saved]
    own, own_text = [], []
    for name in scored:
        h, per_text = A.score_per_text(model, P.unflatten(hook.saved[LR.SAVED[name]], ctx.lay), prep, device=ctx.device)
        if LR._bits(h) != LR._bits(record[hook.events[LR.SAVED[name]]]):
            raise LR.GuardFailure("G4", unit)
        LR._g5(h, per_text, unit)
        own.append(h)
        own_text.append(per_text)
    ctx.tick("scoring", time.time() - t0, 1 + len(scored))
    ctx.tick("scoring_in_search_units", time.time() - t0, 1 + len(scored))
    LR._peak_read(ctx)
    guards = {"G4": True, "G5": True, "G7": True}
    if ctx.mode != "deciding":
        flats = [first] + [hook.saved[LR.SAVED[name]] for name in scored]
        t0 = time.time()
        for flat, ours in zip(flats, [init] + own):
            if LR._bits(A.score(model, P.unflatten(flat, ctx.lay), prep, device=ctx.device)) != LR._bits(ours):
                raise LR.GuardFailure("wrapper_equals_authors", unit)
        ctx.tick("wrapper_check", time.time() - t0, len(flats))
        guards["wrapper_equals_authors"] = True
    guards["delta_entries_held"] = True

    names = sorted(hook.saved)
    meta = {"unit": unit, "kind": "search", "arm": ctx.arm, "side": side, "batch": batch, "start": start_index,
            "start_sha256": LR.setting_sha256(LR.flat_start(start, ctx.lay, False)), "ids_sha": batch_ids_sha, "prep_fp": prep_fp, "commit": ctx.commit,
            "n_steps": ctx.n_steps, "delta_held": True, "delta_value": float(value), "precision": ctx.precision, "environment": ctx.environment}
    arrays = {
        "record": np.asarray(record, dtype=np.float64),
        "hook_names": np.array(names), "hook_steps": np.array([hook.events[n] for n in names], dtype=np.int64),
        "settings": np.stack([hook.saved[n] for n in names]).astype(np.float32),
        "cum_signed": np.stack([hook.cum[n][0] for n in names]).astype(np.float32),
        "cum_abs": np.stack([hook.cum[n][1] for n in names]).astype(np.float32),
        "scored_names": np.array(scored), "own": np.asarray(own, dtype=np.float64),
        "own_text": np.asarray(own_text, dtype=np.float32).reshape(len(scored), prep.n_texts),
        "init": np.asarray([init], dtype=np.float64), "init_text": np.asarray(init_text, dtype=np.float32),
        "meta": np.array(json.dumps(meta, sort_keys=True)),
    }
    sha = LR.write_unit(path, arrays, ctx.fault)
    ctx.tick("search_unit_whole", time.time() - t_unit)
    ctx.log(event="unit_finished", unit=unit, sha256=sha)
    return {"unit": unit, "sha256": sha, "guards": guards, "skipped": False}


def guard_batch(batch: str, ids: np.ndarray, rows: list[str]) -> None:
    """The batch is the one named: one of the rerun's eight, whose per-text hashes equal the manifest's."""
    if batch not in BATCHES or LR.sha_rows(ids) != list(rows):
        raise LR.GuardFailure("G1", f"container|{RERUN}|{batch}")


def check_environment(ctx: LR.Context) -> None:
    """The signed configuration, as the run's deciding containers asserted it."""
    env = ctx.environment
    ok = (ctx.precision == "bf16" and ctx.device == "cuda" and "B200" in str(env.get("gpu")) and env.get("deterministic_algorithms") is True
          and env.get("deterministic_warn_only") is False and env.get("allow_tf32_matmul") is False and env.get("allow_tf32_cudnn") is False
          and env.get("cublas_workspace_config") == ":4096:8" and env.get("vpd_audit_2_commit") == ctx.commit and env.get("vpd_audit_2_dirty") == "0")
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ctx.arm}")


def check_configuration(ctx: RerunContext, arm: str, starts: tuple[int, ...]) -> None:
    """The rerun's shape in every container: the arm's name and folder, 20 steps, the lead arm's scored settings, starts
    41 to 45, no fault trigger; and the environment, except on the tiny model's tests (mode "test")."""
    ok = (ctx.arm == ARM_NAME[arm] and ctx.units.name == arm and ctx.n_steps == N_STEPS and tuple(starts) == STARTS and ctx.fault is None
          and ctx.delta_held is False and ctx.settings == LT.SETTINGS_LEAD and ctx.mode in (RERUN_MODE, "test"))
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ctx.arm}")
    if ctx.mode != "test":
        if ctx.mode != RERUN_MODE:
            raise LR.GuardFailure("configuration", f"container|{ctx.arm}")
        check_environment(ctx)


def rerun_job(model: Any, contexts: dict[str, RerunContext], batch: str, ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]]) -> dict[str, Any]:
    """One batch: prepare it once; then from each start, the searched arm's unit and the held-at-0 arm's, committing the
    volume after each."""
    guard_batch(batch, ids, rows)
    if set(contexts) != set(ARMS):
        raise LR.GuardFailure("configuration", f"container|{RERUN}|{batch}")
    for arm, ctx in contexts.items():
        check_configuration(ctx, arm, tuple(sorted(starts)))
    ctx0 = contexts[ARMS[0]]
    t0 = time.time()
    prep = ctx0.prepare(model, ids, ctx0.precision, device=ctx0.device)
    ctx0.tick("labels_and_targets", time.time() - t0)
    t0 = time.time()
    prep_fp = LR.prep_fingerprint(prep)
    ctx0.tick("fingerprint", time.time() - t0)
    removed = sum(LR.clean_unfinished(ctx.units, batch) for ctx in contexts.values())
    ctx0.tick("to_ready", time.time() - ctx0.t0)
    ctx0.log(event="container_started", container=f"{RERUN}|{batch}", count=removed)
    ids_sha = LR.ids_sha256(ids)
    units: list[dict[str, Any]] = []
    stopped = False
    for s in sorted(starts):
        for arm in ARMS:
            if ctx0.should_stop():
                stopped = True
                break
            ctx = contexts[arm]
            if arm == "searched":
                u = LR.search_unit(model, prep, ctx, RERUN_SIDE, batch, s, starts[s], ids_sha, prep_fp)
            else:
                u = search_unit_frozen(model, prep, ctx, RERUN_SIDE, batch, s, starts[s], ids_sha, prep_fp, HELD_VALUE)
            units.append(u)
            t0 = time.time()
            ctx.commit_volume()
            ctx.tick("volume_commit_after_search" if not u["skipped"] else "volume_commit_nothing_new", time.time() - t0)
        if stopped:
            break
    out = LR.job_return(ctx0, f"{RERUN}|{RERUN_SIDE}|{batch}", units, len(starts) * len(ARMS), stopped)
    out["timings"] = {k: float(v) for k, v in ctx0.timings.items()}  # nothing is sealed
    out["removed_unfinished"] = int(removed)
    return out


def rerun_contexts(spec: dict[str, Any], lay: list, *, environment: dict[str, Any], log: Callable[..., None], commit_volume: Callable[[], None],
                   should_stop: Callable[[], bool], t0: float, device: str, precision: str, mode: str | None = None) -> dict[str, RerunContext]:
    timings: dict[str, float] = {}  # one container's timings, shared by its two arms
    return {arm: RerunContext(arm=ARM_NAME[arm], units=Path(spec["root"]) / spec["units"] / arm, commit=spec["commit"], lay=[tuple(x) for x in lay],
                              precision=precision, device=device, n_steps=N_STEPS, mode=spec["mode"] if mode is None else mode, environment=environment,
                              log=log, commit_volume=commit_volume, should_stop=should_stop, t0=t0, timings=timings) for arm in ARMS}


def run_rerun_spec(model: Any, spec: dict[str, Any], ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]], lay: list, *,
                   environment: dict[str, Any], log: Callable[..., None], commit_volume: Callable[[], None], should_stop: Callable[[], bool],
                   t0: float | None = None, device: str = "cuda", precision: str = "bf16", mode: str | None = None) -> dict[str, Any]:
    """What a rerun container does with the spec it is handed."""
    check_spec(spec)
    contexts = rerun_contexts(spec, lay, environment=environment, log=log, commit_volume=commit_volume, should_stop=should_stop,
                              t0=time.time() if t0 is None else t0, device=device, precision=precision, mode=mode)
    return rerun_job(model, contexts, spec["batch"], ids, rows, starts)


# ----------------------------------------------------------------------------- the variants' containers


def variants_job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]], inputs: SR.Inputs) -> dict[str, Any]:
    """One S4 batch: its labels checked to be the run's, the check unit, then the 80 searches' variants."""
    SR.check_environment(ctx)
    batch = spec["batch"]
    refs = spec["refs"][batch]
    units = B.variant_units(batch, list(spec["attack_batches"]), list(spec["starts"]))
    removed = SR.clean_unfinished(ctx, [u[0] for u in units])
    ids, rows = batch_inputs[batch]
    prep, fp, zero = SR.prepare_batch(model, ctx, batch, ids, rows, refs["prep_fp"])
    ctx.tick("to_ready", time.time() - ctx.t0)
    ctx.log(event="container_started", container=f"{VARIANT_ARM}|{batch}", count=removed)
    done, stopped = SR.run_units(model, ctx, batch, units, prep, fp, zero, inputs, refs)
    ctx.commit_volume()
    out = {"container": f"{VARIANT_ARM}|heldout|{batch}", "units": done, "finished_units": len(done), "expected_units": len(units), "stopped": bool(stopped),
           "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment), "timings": {k: float(v) for k, v in ctx.timings.items()},
           "removed_unfinished": int(removed)}
    ctx.log(event="container_finished", container=out["container"], count=len(done), seconds=out["seconds"])
    return out


# ----------------------------------------------------------------------------- the specs, and what each container is handed


def specs(commit: str, refs: dict[str, Any]) -> list[dict[str, Any]]:
    """The eight rerun containers, then the four variants' containers."""
    out: list[dict[str, Any]] = [{"part": RERUN, "arm": RERUN, "side": RERUN_SIDE, "batch": b, "commit": commit, "mode": RERUN_MODE, "root": VOLUME,
                                  "units": RERUN, "run": RUN} for b in BATCHES]
    out += [{"part": VARIANTS, "arm": VARIANT_ARM, "side": "heldout", "batch": h, "batches": [h], "commit": commit, "mode": SR.MODE, "root": VOLUME,
             "units": VARIANTS, "run": RUN, "attack_batches": list(SR.ATTACK), "starts": list(SR.STARTS), "refs": {h: refs[h]}} for h in VARIANT_BATCHES]
    return out


RERUN_KEYS = {"part", "arm", "side", "batch", "commit", "mode", "root", "units", "run"}
VARIANT_KEYS = RERUN_KEYS | {"batches", "attack_batches", "starts", "refs"}


def check_spec(spec: dict[str, Any]) -> None:
    """A spec is one of this launch's, of one of its two parts, and nothing else (`launch` is added by the launcher)."""
    keys = set(spec) - {"launch"}
    common = spec.get("root") == VOLUME and spec.get("run") == RUN and len(str(spec.get("commit"))) == 40
    if spec.get("part") == RERUN:
        ok = (common and keys == RERUN_KEYS and spec["arm"] == RERUN and spec["side"] == RERUN_SIDE and spec["batch"] in BATCHES and spec["mode"] == RERUN_MODE
              and spec["units"] == RERUN)
    elif spec.get("part") == VARIANTS:
        ok = (common and keys == VARIANT_KEYS and spec["arm"] == VARIANT_ARM and spec["side"] == "heldout" and spec["batch"] in VARIANT_BATCHES
              and spec["batches"] == [spec["batch"]] and spec["mode"] == SR.MODE and spec["units"] == VARIANTS and tuple(spec["attack_batches"]) == SR.ATTACK
              and tuple(spec["starts"]) == SR.STARTS and set(spec["refs"]) == {spec["batch"]})
    else:
        ok = False
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('part')}|{spec.get('batch')}")


def batch_slice(batch: str) -> slice:
    k = BATCHES.index(batch)
    return slice(BATCH_SIZE * k, BATCH_SIZE * (k + 1))


def rerun_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                 pools: dict[str, Any] | None = None) -> tuple[np.ndarray, list[str]]:
    """A rerun container's one batch of pool Q, the manifest's texts in order: its token ids, and each text's SHA-256."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = LL._manifest()["pools"] if pools is None else pools
    if spec.get("part") != RERUN or spec["batch"] not in BATCHES or pools[POOL]["pool"] != POOL or len(pools[POOL]["texts"]) != BATCH_SIZE * len(BATCHES):
        raise LL.LaunchRefusal(f"batch {spec.get('batch')} is not one of the rerun's batches of pool Q")
    ids, texts, rows = load_ids(POOL)
    if list(texts) != list(pools[POOL]["texts"]) or len(ids) != BATCH_SIZE * len(BATCHES):
        raise LL.LaunchRefusal("pool Q's texts are not the manifest's, in its order")
    sl = batch_slice(spec["batch"])
    return np.ascontiguousarray(ids[sl]), list(rows)[sl]


def variants_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                    pools: dict[str, Any] | None = None) -> dict[str, tuple[np.ndarray, list[str]]]:
    """A variants container's one S4 batch, a held-out pool; no other batch's ids."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = LL._manifest()["pools"] if pools is None else pools
    h = spec["batch"]
    if spec.get("part") != VARIANTS or h not in VARIANT_BATCHES or pools[h]["pool"] != "H":
        raise LL.LaunchRefusal(f"batch {h} is not one of S4's held-out batches")
    ids, _texts, rows = load_ids(h)
    return {h: (ids, list(rows))}


def load_starts() -> dict[int, dict[str, np.ndarray]]:
    """Starts 41 to 45 from the signed file, checked against its signed SHA-256 and each start's own."""
    return LL.starts_for(STARTS)


# ----------------------------------------------------------------------------- before the launch: the commit and the cost


def tree_holds_only_this_plans_records() -> bool:
    top = Path(LL._git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    allowed = (RESULTS.resolve().relative_to(top)).as_posix() + "/"
    r = LL._git("status", "--porcelain", "--untracked-files=all", "--", ".")
    return r.returncode == 0 and all(line.startswith("?? ") and line[3:].strip('"').startswith(allowed) for line in r.stdout.splitlines())


def check_launch_commit(commit: str) -> None:
    """The current commit is the one named, the tree is clean under `vpd-audit-2/` but for this launch's records, the
    readings and the drivers are committed, and no file of the search and scoring path has changed since the lead run."""
    if not tree_holds_only_this_plans_records():
        raise LL.LaunchRefusal("the tree is not clean under vpd-audit-2")
    if LL.head_commit() != commit or len(commit) != 40:
        raise LL.LaunchRefusal("the current commit is not the one named")
    missing = [rel for rel in READING_FILES if LL.blob(commit, rel) is None]
    if missing:
        raise LL.LaunchRefusal("not committed: " + ", ".join(missing))
    changed = LL.run_files_changed(SR.RUN_COMMIT, commit)
    if changed:
        raise LL.LaunchRefusal("the search path has changed since the lead run: " + ", ".join(changed))


def _mean_rate(timings: list[dict[str, float]], key: str) -> float:
    return float(np.mean([t[key] / t[key + "_count"] for t in timings]))


def projection(listed_hourly_price: float, *, starts_record: Path | None = None, plan2_records: tuple[Path, ...] | None = None) -> dict[str, Any]:
    """The launch's cost before it starts, priced as Amendment 4 prices money (`lead_ledger.money`), against the rerun's
    $6 and the launch's cap.

      - The rerun, from the starts test's eight containers (plan 1 of the research log): their mean time to ready, and per search, the first
        iteration, the nine warm iterations, the ten after them at the steady rate, the final harm, a volume commit, and
        2 (1 + 4) scoring passes at their rate (the start and up to four scored settings, each once more through the
        authors' function). Ten searches per container, eight containers.
      - The variants, from plan 2 of the research log's four S4 containers: their mean time to ready, a flat pass and a split pass at their
        rates (`unit_controls` and `unit_split`), and a volume commit every ten units. Per container 80 units of 5 flat
        and 10 split passes, and the check's 1 flat and 2 split.
    Every container life adds 50 seconds of boot."""
    st = [c["timings"] for c in json.load(open(STARTS_TEST_RECORD if starts_record is None else starts_record))["containers"]]
    ready_r = float(np.mean([t["to_ready"] for t in st]))
    warm = LG.WARM_ITERATIONS
    per_pass_r = _mean_rate(st, "scoring")
    passes_r = 2 * (1 + RERUN_SCORED_MAX)
    per_search = (_mean_rate(st, "search_iteration_0") + (warm - 1) * _mean_rate(st, "search_iterations_warm")
                  + (N_STEPS - warm) * _mean_rate(st, "search_iterations_after_warm") + _mean_rate(st, "search_final_harm")
                  + passes_r * per_pass_r + _mean_rate(st, "volume_commit_after_search"))
    n_rerun = len(STARTS) * len(ARMS)
    rerun_seconds = len(BATCHES) * (ready_r + n_rerun * per_search)

    s4 = []
    for path in (PLAN2_RECORDS if plan2_records is None else plan2_records):
        s4 += [c["timings"] for c in json.load(open(path))["containers"] if c["container"].split("|")[2] in VARIANT_BATCHES]
    if len(s4) != len(VARIANT_BATCHES):
        raise LL.LaunchRefusal("plan 2 of the research log's records do not hold its four S4 containers")
    ready_v = float(np.mean([t["to_ready"] for t in s4]))
    flat_pass, split_pass, commit_s = _mean_rate(s4, "unit_controls"), _mean_rate(s4, "unit_split"), _mean_rate(s4, "volume_commit")
    n_units = 1 + len(SR.ATTACK) * len(SR.STARTS)
    flat_n = (len(SR.ATTACK) * len(SR.STARTS)) * len(B.SPLIT_ROWS) + 1
    split_n = (len(SR.ATTACK) * len(SR.STARTS)) * 2 * len(B.SPLIT_ROWS) + 2
    variant_seconds = len(VARIANT_BATCHES) * (ready_v + flat_n * flat_pass + split_n * split_pass + commit_s * (n_units // SR.COMMIT_EVERY + 1))

    rerun = LG.money(rerun_seconds, len(BATCHES), listed_hourly_price)
    variants = LG.money(variant_seconds, len(VARIANT_BATCHES), listed_hourly_price)
    total = LG.money(rerun_seconds + variant_seconds, len(BATCHES) + len(VARIANT_BATCHES), listed_hourly_price)
    return {"check": "C0", "listed_hourly_price": float(listed_hourly_price),
            "rerun": {"containers": len(BATCHES), "searches": len(BATCHES) * n_rerun, "seconds_to_ready": ready_r, "seconds_per_search": per_search,
                      "scoring_passes_per_search_at_most": passes_r, "seconds_per_scoring_pass": per_pass_r, **rerun},
            "variants": {"containers": len(VARIANT_BATCHES), "passes": len(VARIANT_BATCHES) * (flat_n + split_n), "flat_passes_per_container": flat_n,
                         "split_passes_per_container": split_n, "seconds_to_ready": ready_v, "seconds_per_flat_pass": flat_pass,
                         "seconds_per_split_pass": split_pass, "seconds_per_volume_commit": commit_s, **variants},
            "total": total, "projected_dollars": total["dollars"], "rerun_cap": RERUN_CAP, "cap": CAP_DOLLARS,
            "exceeds_cap": bool(total["dollars"] > CAP_DOLLARS or rerun["dollars"] > RERUN_CAP)}


def launch_command(commit: str, cloud: LL.Cloud, *, listed_hourly_price: float, refs: dict[str, Any] | None = None) -> dict[str, Any]:
    """The `launch` command: the checks, the projection recorded as check C0 (over either cap, nothing launches), then the
    one stage, twelve containers at once, the ledger kept as the run kept it. A relaunch after a stage that did not
    finish resumes it at the same commit; its finished units are skipped."""
    check_launch_commit(commit)
    ledger_path = RESULTS / "ledger.json"
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("plan 3 of the research log's launch began at another commit")
    if earlier is None:
        LL.record_c0(ledger_path, projection(listed_hourly_price))
    if refs is None:
        refs = SR.references(SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT), SR.load_table_checked(SR.DELTA_TABLE, SR.DELTA_RECEIPT))
    return LL.drive_stage(STAGE, specs(commit, refs), cloud, ledger_path=ledger_path, runs_path=RESULTS / f"runs_{STAGE.name}.json", design=DESIGN,
                          timings={}, listed_hourly_price=listed_hourly_price, cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


# ----------------------------------------------------------------------------- after the launch: the copy


def expected_files() -> dict[str, str]:
    """Each unit's identifier, as its container returns it, to its file under the volume folder (and the local copy)."""
    out = {f"search|{ARM_NAME[arm]}|{b}|s{s}": f"{RERUN}/{arm}/search_{b}_s{s}.npz" for arm in ARMS for b in BATCHES for s in STARTS}
    out.update({name: f"{VARIANTS}/{name}.npz" for h in VARIANT_BATCHES for name, _, _ in B.variant_units(h, list(SR.ATTACK), list(SR.STARTS))})
    return out


def collect_command(commit: str, *, read_file: Callable[[str], bytes], log: Callable[..., None], dest: Path | None = None) -> dict[str, str]:
    """Every unit file off the volume as bytes, each checked against the hash its container returned, to a folder git
    ignores, with the receipt."""
    if not tree_holds_only_this_plans_records() or LL.head_commit() != commit:
        raise LL.LaunchRefusal("the tree or the commit is not the launch's")
    run = json.load(open(RESULTS / f"runs_{STAGE.name}.json"))
    if run["commit"] != commit or not run["summary"]["complete"]:
        raise LL.LaunchRefusal("the stage is not complete at this commit")
    returned = {u["unit"]: u["sha256"] for c in run["containers"] for u in c["units"]}
    expected = expected_files()
    if set(returned) != set(expected):
        raise LL.LaunchRefusal(f"the stage's record holds {len(returned)} units; the plan has {len(expected)}")
    dest = LOCAL if dest is None else dest
    files: dict[str, str] = {}
    for unit in sorted(expected):
        rel = expected[unit]
        data = read_file(f"{VOLUME}/{rel}")
        if hashlib.sha256(data).hexdigest() != returned[unit]:
            raise LL.LaunchRefusal(f"the bytes of {rel} do not have the hash its container returned")
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_bytes(data)
        files[rel] = returned[unit]
    LL.write_json(RESULTS / "backup.json", {"commit": commit, "at": LL.utc_now(),
                                            "folder": str(dest.relative_to(REPO_ROOT)) if dest.is_relative_to(REPO_ROOT) else str(dest), "files": files})
    log(event="backup_finished", container="units", count=len(files))
    return files
