"""Session 6, plan 1, Section 2.3: the starts test on the GPU, and its local side, with no cloud call in it.

What runs: 41 searches of 320 steps, each scored on its own batch only.

  - The test: the pilot's calibration batches C1 to C8, each from the run's starts 9, 10, 11, 12, and 13. 40 searches.
  - The guard: C1 from start 1 once more. Its record must equal the pilot's (`results/s4_pilot/part_a/runs.json`, key
    `a1`, `C1`, `"1"`) bit for bit; `collect_command` checks it before anything else is read, and stops if it does not.

One container per batch: C1's runs six searches, the others five. Each search is a unit file in the run's format
(`search_<batch>_s<start>.npz`) under `/cache/s6_starts/units/` on the volume; a restarted container skips the units it
finished. The configuration is the lead experiment's exactly: our loop, the whole batch in one pass, bf16 autocast, one
B200, step 0.1, strict deterministic algorithms, labels and targets and weight deltas prepared once per batch, the delta
components searched.

This is a separate small driver, not a third mode of `lead_run`. It calls `lead_run.search_unit`, the search path both of
session 5's rehearsals showed bit-identical to the pilot's (the hook saving settings at 20, 40, 80, 160, and 320 steps and
one step earlier, cumulative gradients, and per-text own harms), with a context of its own (`Context`), its own checks of
the batch and the configuration, and its own specs. `lead_run` is unchanged, and so are its deciding-mode refusals: it
still refuses any starts but 9 to 13 in deciding mode and allows only start 1 in rehearsal mode. Outside deciding mode
`search_unit` also checks, on every scored setting, that the per-text wrapper equals the authors' function bit for bit,
as the rehearsals did; that costs 11 forward passes a search and does not touch the search.

Nothing is sealed. The local side:

  - `launch_command`: the checks before the job (the commit, the tree, the reading script committed, the search path
    unchanged since the run), the cost projection against the $20 at which the plan stops (`projection`, recorded on the
    ledger as check C0), then `lead_launch.drive_stage`, which launches the eight containers at once and keeps the ledger
    and the stage's record as it did for the run.
  - `collect_command`: every unit file off the volume as bytes, each checked against the hash its container returned,
    to `.cache/s6_starts/units/` (ignored by git), with a receipt (`backup.json`); then the guard (`guard.json`); then,
    only if the guard holds, `records.json`: every search's full record, its start key, its batch, the hook's events,
    and the per-text own harms at the saved steps.

`vpd_audit_2.starts_test` reads `records.json`; it was committed before this job ran.
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

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import starts_test as ST

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s6_starts"
VOLUME = "/cache/s6_starts"  # the test's folder on the cloud volume
UNITS = "units"
LOCAL_UNITS = REPO_ROOT / ".cache" / "s6_starts" / "units"  # `.cache/` is ignored by git
STARTS_JSON = REPO_ROOT / "results" / "s4_pilot" / "starts" / "starts_1_64.json"
ARM = "starts_test"
MODE = "starts_test"
SIDE = "own"  # every search is scored on its own batch, and on no other
RUN = "starts_test"  # the name of its stop flag in the cloud's control dictionary
BATCHES = ST.BATCHES
TEST_STARTS = ST.TEST_STARTS
GUARD_BATCH, GUARD_START = ST.GUARD
N_STEPS = LR.N_STEPS
STAGE = LG.Stage("starts_test", ARM, SIDE, len(BATCHES), len(TEST_STARTS), N_STEPS, len(LT.SETTINGS_LEAD), 8, 0, False)
DESIGN = (STAGE,)
CAP_DOLLARS = 20.0  # plan 1, Section 2.3: if the projection exceeds $20, do not launch
RUN_COMMIT = "8522c18156c6c9023aedffe9061a56838898e960"  # the lead run's commit: the search path must be unchanged since it
READING_FILES = ("vpd_audit_2/starts_test.py", "vpd_audit_2/starts_run.py", "vpd_audit_2/modal_starts.py")
# The projection's inputs (plan 1, Section 2.3): the pilot's question 2 part cost $19.20 for its 64 searches; the run's
# attack containers held five searches each, and the rehearsal measured the time to ready and a scoring pass.
PILOT_DOLLARS, PILOT_SEARCHES = 19.20, 64
RUN_LEDGER = LL.RESULTS / "ledger.json"
REHEARSAL_RECORD = LL.RESULTS / "rehearsal_2" / "rehearsal.json"
WRAPPER_PASSES = 1 + len(LT.SETTINGS_LEAD)  # the start and each scored setting, once more through the authors' function


def starts_of(batch: str) -> tuple[int, ...]:
    """The starts a batch's container searches from: 9 to 13, and for C1 start 1 first, the guard."""
    return ((GUARD_START,) if batch == GUARD_BATCH else ()) + TEST_STARTS


def n_searches() -> int:
    return sum(len(starts_of(b)) for b in BATCHES)


@dataclass
class Context(LR.Context):
    """The lead run's context, with the lead arm's ten scored settings and the delta components searched, under an arm
    name of its own; `lead_run.ARMS` is not touched."""

    @property
    def settings(self) -> tuple[str, ...]:
        return LT.SETTINGS_LEAD

    @property
    def delta_held(self) -> bool:
        return False


# ----------------------------------------------------------------------------- what a container is handed, and checks


def specs(commit: str) -> list[dict[str, Any]]:
    return [{"arm": ARM, "side": SIDE, "batch": b, "commit": commit, "mode": MODE, "root": VOLUME, "units": UNITS, "run": RUN} for b in BATCHES]


SPEC_KEYS = {"arm", "side", "batch", "commit", "mode", "root", "units", "run"}


def check_spec(spec: dict[str, Any]) -> None:
    """A spec is one of this test's: its arm, side, mode, and folders, one calibration batch, and nothing else
    (`launch` is added by the launcher)."""
    ok = (set(spec) - {"launch"} == SPEC_KEYS and spec["arm"] == ARM and spec["side"] == SIDE and spec["mode"] == MODE and spec["batch"] in BATCHES
          and spec["root"] == VOLUME and spec["units"] == UNITS and spec["run"] == RUN and len(str(spec["commit"])) == 40)
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('arm')}|{spec.get('batch')}")


def container_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                     pools: dict[str, Any] | None = None) -> tuple[np.ndarray, list[str]]:
    """The token ids of the container's one calibration batch, with each text's SHA-256 from the manifest; no other
    batch's ids are loaded."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = LL._manifest()["pools"] if pools is None else pools
    batch = spec["batch"]
    if not (batch in BATCHES and pools[batch]["pool"] == "C" and spec.get("arm") == ARM and spec.get("mode") == MODE):
        raise LL.LaunchRefusal(f"batch {batch} is not one of the test's calibration batches")
    ids, _texts, rows = load_ids(batch)
    return ids, list(rows)


def load_starts() -> dict[int, dict[str, np.ndarray]]:
    """Starts 1 and 9 to 13 from the signed file, checked against its signed SHA-256 and each start's own; start 1 also
    equal to the manifest's copy of it, as the rehearsal required."""
    from vpd_audit_2.manifest import load_start

    starts = LL.starts_for((GUARD_START,) + TEST_STARTS)
    reference = load_start(GUARD_START)
    if not all(np.array_equal(starts[GUARD_START][k], reference[k]) for k in reference):
        raise LL.LaunchRefusal("start 1 is not the signed one")
    return starts


def starts_for_batch(starts: dict[int, dict[str, np.ndarray]], batch: str) -> dict[int, dict[str, np.ndarray]]:
    return {s: starts[s] for s in starts_of(batch)}


def guard_batch(ctx: Context, batch: str, ids: np.ndarray, rows: list[str]) -> None:
    """The batch is the one named: a calibration batch of the test, whose per-text hashes equal the manifest's."""
    if batch not in BATCHES or LR.sha_rows(ids) != list(rows):
        raise LR.GuardFailure("G1", f"container|{ctx.arm}|{batch}")


def check_environment(ctx: Context) -> None:
    """The signed configuration, as `lead_run.check_configuration` asserts it in a deciding container."""
    env = ctx.environment
    ok = (ctx.mode == MODE and ctx.precision == "bf16" and ctx.device == "cuda" and "B200" in str(env.get("gpu")) and env.get("deterministic_algorithms") is True
          and env.get("deterministic_warn_only") is False and env.get("allow_tf32_matmul") is False and env.get("allow_tf32_cudnn") is False
          and env.get("cublas_workspace_config") == ":4096:8" and env.get("vpd_audit_2_commit") == ctx.commit and env.get("vpd_audit_2_dirty") == "0")
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ctx.arm}")


def check_configuration(ctx: Context, batch: str, starts: tuple[int, ...]) -> None:
    """This test's shape in every container: its arm, 320 steps, the delta components searched, no trigger, and exactly
    the starts of `starts_of(batch)`; and the environment, except on the tiny model's tests (mode "test")."""
    ok = (ctx.arm == ARM and ctx.n_steps == N_STEPS and tuple(starts) == starts_of(batch) and ctx.fault is None and ctx.delta_held is False
          and ctx.settings == LT.SETTINGS_LEAD and ctx.mode in (MODE, "test"))
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ctx.arm}|{batch}")
    if ctx.mode != "test":
        check_environment(ctx)


# ----------------------------------------------------------------------------- what a container runs


def job(model: Any, ctx: Context, batch: str, ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]]) -> dict[str, Any]:
    """One calibration batch: prepare it once, then one search unit per start, committing the volume after each."""
    guard_batch(ctx, batch, ids, rows)
    check_configuration(ctx, batch, tuple(sorted(starts)))
    t0 = time.time()
    prep = ctx.prepare(model, ids, ctx.precision, device=ctx.device)
    ctx.tick("labels_and_targets", time.time() - t0)
    t0 = time.time()
    prep_fp = LR.prep_fingerprint(prep)
    ctx.tick("fingerprint", time.time() - t0)
    ctx.removed_unfinished += LR.clean_unfinished(ctx.units, batch)
    ctx.tick("to_ready", time.time() - ctx.t0)
    ctx.log(event="container_started", container=f"{ctx.arm}|{batch}", count=ctx.removed_unfinished)
    ids_sha = LR.ids_sha256(ids)
    units: list[dict[str, Any]] = []
    stopped = False
    for s in sorted(starts):
        if ctx.should_stop():
            stopped = True
            break
        units.append(LR.search_unit(model, prep, ctx, SIDE, batch, s, starts[s], ids_sha, prep_fp))
        t0 = time.time()
        ctx.commit_volume()
        ctx.tick("volume_commit_after_search" if not units[-1]["skipped"] else "volume_commit_nothing_new", time.time() - t0)
    out = LR.job_return(ctx, f"{ctx.arm}|{SIDE}|{batch}", units, len(starts), stopped)
    out["timings"] = {k: float(v) for k, v in ctx.timings.items()}  # nothing is sealed
    out["removed_unfinished"] = int(ctx.removed_unfinished)
    return out


def run_spec(model: Any, spec: dict[str, Any], ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]], lay: list, *,
             environment: dict[str, Any], log: Callable[..., None], commit_volume: Callable[[], None], should_stop: Callable[[], bool],
             t0: float | None = None, device: str = "cuda", precision: str = "bf16") -> dict[str, Any]:
    """What a container does with the spec it is handed (`specs`)."""
    check_spec(spec)
    ctx = Context(arm=spec["arm"], units=Path(spec["root"]) / spec["units"], commit=spec["commit"], lay=[tuple(x) for x in lay], precision=precision,
                  device=device, n_steps=N_STEPS, mode=spec["mode"], environment=environment, log=log, commit_volume=commit_volume,
                  should_stop=should_stop, t0=time.time() if t0 is None else t0)
    return job(model, ctx, spec["batch"], ids, rows, starts)


# ----------------------------------------------------------------------------- before the job: the commit and the cost


def tree_holds_only_this_tests_records() -> bool:
    """No change to a tracked file under `vpd-audit-2/`, and no untracked file there but this test's own records under
    `results/s6_starts/`, which the launcher writes as it goes."""
    top = Path(LL._git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    allowed = (RESULTS.resolve().relative_to(top)).as_posix() + "/"
    r = LL._git("status", "--porcelain", "--untracked-files=all", "--", ".")
    return r.returncode == 0 and all(line.startswith("?? ") and line[3:].strip('"').startswith(allowed) for line in r.stdout.splitlines())


def check_launch_commit(commit: str) -> None:
    """The current commit is the one named, the tree is clean under `vpd-audit-2/` but for this test's records, the
    reading script and this driver are committed, and no file the search path runs has changed since the lead run's
    commit."""
    if not tree_holds_only_this_tests_records():
        raise LL.LaunchRefusal("the tree is not clean under vpd-audit-2")
    if LL.head_commit() != commit or len(commit) != 40:
        raise LL.LaunchRefusal("the current commit is not the one named")
    missing = [rel for rel in READING_FILES if LL.blob(commit, rel) is None]
    if missing:
        raise LL.LaunchRefusal("not committed: " + ", ".join(missing))
    changed = LL.run_files_changed(RUN_COMMIT, commit)
    if changed:
        raise LL.LaunchRefusal("the search path has changed since the lead run: " + ", ".join(changed))


def projection(listed_hourly_price: float, *, ledger_path: Path | None = None, rehearsal_path: Path | None = None) -> dict[str, Any]:
    """The test's cost before it launches, three ways, priced as Amendment 4 prices money (`lead_ledger.money`), and the
    largest taken against the $20 cap:

      - from the run: the lead's attack containers, five 320-step searches each with their own-batch re-scores, at their
        mean seconds and at their largest; less the rehearsal's time to ready, over five, is a search's seconds. Each of
        the 41 searches adds the wrapper check (11 scoring passes at the rehearsal's rate), and each of the 8 containers
        its time to ready and, as boot, 50 seconds;
      - from the pilot: its $19.20 for 64 searches, per search, times 41."""
    ledger = json.load(open(RUN_LEDGER if ledger_path is None else ledger_path))
    timings = json.load(open(REHEARSAL_RECORD if rehearsal_path is None else rehearsal_path))["timings"]
    calls = [c for launch in ledger["stages"]["lead_attack"]["launches"] for c in launch["calls"].values()]
    seconds = [float(c["returned_seconds"]) for c in calls if c["outcome"] == "returned" and c["attempts"] == 1]
    per_container_searches = LG.stage_named("lead_attack").starts
    ready, per_pass = float(timings["seconds_to_ready"]), float(timings["seconds_per_scoring_pass"])
    n, containers = n_searches(), len(BATCHES)

    def from_run(container_seconds: float) -> dict[str, Any]:
        per_search = (container_seconds - ready) / per_container_searches
        total = containers * ready + n * (per_search + WRAPPER_PASSES * per_pass)
        return {"container_seconds": container_seconds, "seconds_per_search": per_search, **LG.money(total, containers, listed_hourly_price)}

    mean_run, max_run = from_run(float(np.mean(seconds))), from_run(float(np.max(seconds)))
    pilot = n * PILOT_DOLLARS / PILOT_SEARCHES
    projected = max(mean_run["dollars"], max_run["dollars"], pilot)
    return {"check": "C0", "searches": n, "containers": containers, "listed_hourly_price": float(listed_hourly_price),
            "inputs": {"run_attack_containers": len(seconds), "run_attack_container_seconds_mean": float(np.mean(seconds)),
                       "run_attack_container_seconds_max": float(np.max(seconds)), "searches_per_run_attack_container": per_container_searches,
                       "rehearsal_seconds_to_ready": ready, "rehearsal_seconds_per_scoring_pass": per_pass, "wrapper_passes_per_search": WRAPPER_PASSES,
                       "pilot_dollars": PILOT_DOLLARS, "pilot_searches": PILOT_SEARCHES},
            "from_the_run_at_the_mean": mean_run, "from_the_run_at_the_largest": max_run, "from_the_pilot_dollars": pilot,
            "projected_dollars": projected, "cap": CAP_DOLLARS, "exceeds_cap": projected > CAP_DOLLARS}


def launch_command(commit: str, cloud: LL.Cloud, *, listed_hourly_price: float) -> dict[str, Any]:
    """The `launch` command: the checks, the projection recorded as check C0 (over $20, nothing launches), then the one
    stage: eight containers at once, the ledger kept as the run kept it. A relaunch after a stage that did not finish
    resumes it at the same commit; its finished units are skipped."""
    check_launch_commit(commit)
    ledger_path = RESULTS / "ledger.json"
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("the test began at another commit")
    if earlier is None:
        LL.record_c0(ledger_path, projection(listed_hourly_price))
    return LL.drive_stage(STAGE, specs(commit), cloud, ledger_path=ledger_path, runs_path=RESULTS / f"runs_{STAGE.name}.json", design=DESIGN, timings={},
                          listed_hourly_price=listed_hourly_price, cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


# ----------------------------------------------------------------------------- after the job: the copy, the guard, the records


def unit_id(batch: str, start: int) -> str:
    return f"search|{ARM}|{batch}|s{start}"


def copy_units(run: dict[str, Any], *, read_file: Callable[[str], bytes], dest: Path, out_path: Path, commit: str, log: Callable[..., None]) -> dict[str, str]:
    """Every unit file off the volume, as bytes, each checked against the hash its container returned, to a local folder
    that git ignores; with the receipt."""
    returned = {u["unit"]: u["sha256"] for c in run["containers"] for u in c["units"]}
    expected = {unit_id(b, s): (b, s) for b in BATCHES for s in starts_of(b)}
    if set(returned) != set(expected):
        raise LL.LaunchRefusal("the stage's record does not hold the test's 41 units")
    dest.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for unit in sorted(expected):
        name = LR.search_file(Path("."), *expected[unit]).name
        data = read_file(f"{VOLUME}/{UNITS}/{name}")
        if hashlib.sha256(data).hexdigest() != returned[unit]:
            raise LL.LaunchRefusal(f"the bytes of {name} do not have the hash its container returned")
        (dest / name).write_bytes(data)
        hashes[name] = returned[unit]
    LL.write_json(out_path, {"commit": commit, "at": LL.utc_now(), "folder": str(dest.relative_to(REPO_ROOT)) if dest.is_relative_to(REPO_ROOT) else str(dest),
                             "files": hashes})
    log(event="backup_finished", container="units", count=len(hashes))
    return hashes


def build_records(units: Path, commit: str, starts_meta: dict[str, Any]) -> dict[str, Any]:
    """Every search's full record, its start key, its batch, the hook's events, and the per-text own harms at the saved
    steps (and at the start), from the unit files; each unit checked to be the search it is named for, at this commit,
    from the signed start of its index."""
    searches = []
    for b in BATCHES:
        for s in starts_of(b):
            path = LR.search_file(units, b, s)
            meta = LR.unit_meta(path)
            ok = (meta["batch"] == b and meta["start"] == s and meta["arm"] == ARM and meta["side"] == SIDE and meta["commit"] == commit
                  and meta["n_steps"] == N_STEPS and meta["delta_held"] is False and meta["start_sha256"] == starts_meta["starts"][str(s)]["sha256"])
            if not ok:
                raise LL.LaunchRefusal(f"{path.name} is not the search of {b} from start {s} at this commit")
            with np.load(path, allow_pickle=False) as z:
                record = [float(x) for x in z["record"]]
                events = {str(n): int(k) for n, k in zip(z["hook_names"], z["hook_steps"])}
                scored = [str(x) for x in z["scored_names"]]
                own, own_text = z["own"], z["own_text"]
                init, init_text = float(z["init"][0]), z["init_text"]
            harms = {"start": {"step": 0, "harm": init, "per_text": [float(x) for x in init_text]}}
            for q, name in enumerate(scored):
                harms[name] = {"step": events[LR.SAVED[name]], "harm": float(own[q]), "per_text": [float(x) for x in own_text[q]]}
            searches.append({"batch": b, "start": s, "role": "guard" if (b, s) == (GUARD_BATCH, GUARD_START) else "test",
                             "start_key": starts_meta["starts"][str(s)]["seed_key"], "start_sha256": meta["start_sha256"], "unit_file": path.name,
                             "unit_sha256": LT.sha256_file(path), "prep_fp": meta["prep_fp"], "ids_sha": meta["ids_sha"], "record": record,
                             "hook_events": events, "own_harms_at_saved_steps": harms})
    return {"what": "The starts test (sessions/006/engineering/plan_1.md, Section 2.3): C1 to C8 from starts 9 to 13, each searched for 320 steps and "
                    "scored on its own batch only, and C1 from start 1 as the guard. Harms in nats; a search's record holds its harm at the start and "
                    "after each of its 320 steps; the own harms are its own-batch re-scores, per text, at the start and at each saved setting.",
            "commit": commit, "volume_folder": f"{VOLUME}/{UNITS}", "searches": searches}


def collect_command(commit: str, *, read_file: Callable[[str], bytes], log: Callable[..., None], pilot: dict[str, Any] | None = None,
                    dest: Path | None = None) -> dict[str, Any]:
    """The `collect` command, after the stage is complete: the copy and its receipt; then the guard, which must hold
    before anything else is read; then the records."""
    if not tree_holds_only_this_tests_records() or LL.head_commit() != commit:
        raise LL.LaunchRefusal("the tree or the commit is not the test's")
    run = json.load(open(RESULTS / f"runs_{STAGE.name}.json"))
    if run["commit"] != commit or not run["summary"]["complete"]:
        raise LL.LaunchRefusal("the stage is not complete at this commit")
    dest = LOCAL_UNITS if dest is None else dest
    copy_units(run, read_file=read_file, dest=dest, out_path=RESULTS / "backup.json", commit=commit, log=log)
    pilot = LL.pilot_search(GUARD_BATCH, GUARD_START) if pilot is None else pilot
    guard = LR.compare_with_pilot(LR.search_file(dest, GUARD_BATCH, GUARD_START), pilot)
    held = all(guard.values())
    LL.write_json(RESULTS / "guard.json", {"search": f"{GUARD_BATCH} from start {GUARD_START}", "against": "results/s4_pilot/part_a/runs.json, a1, C1, 1",
                                           "outcomes": guard, "all_equal": held, "at": LL.utc_now()})
    log(event="guard_checked", unit=unit_id(GUARD_BATCH, GUARD_START), guard="equals_the_pilots_search", ok=bool(held))
    if not held:
        raise LL.LaunchRefusal("the guard search does not equal the pilot's bit for bit: nothing else is read. Report to the head")
    records = build_records(dest, commit, json.load(open(STARTS_JSON)))
    LL.write_json(RESULTS / "records.json", records)
    log(event="records_written", count=len(records["searches"]))
    return records
