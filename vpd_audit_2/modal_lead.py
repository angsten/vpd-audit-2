"""The Modal app for the lead run (`sessions/005/engineering/plan_2.md`, as `plan_4.md` changes it).

The deciding run, on the head's go, at the commit it names, in this order:

    uv run modal run vpd_audit_2/modal_lead.py::stage --name lead_attack --commit <c>      (16 containers; then check C1)
    uv run modal run vpd_audit_2/modal_lead.py::stage --name lead_heldout_1 --commit <c>   (H1 alone; then check C2 and the guards-only pass)
    uv run modal run vpd_audit_2/modal_lead.py::stage --name lead_heldout_2 --commit <c>   (H2 to H16; then check C3)
    uv run modal run vpd_audit_2/modal_lead.py::stage --name delta_attack --commit <c>
    uv run modal run vpd_audit_2/modal_lead.py::stage --name delta_heldout --commit <c>
    uv run modal run vpd_audit_2/modal_lead.py::assemble --commit <c>                      (both arms' tables, copied as bytes, with receipts)
    uv run modal run vpd_audit_2/modal_lead.py::backup --commit <c>                        (the search units, as bytes, to a folder git ignores)
    uv run modal run vpd_audit_2/modal_lead.py::stop                                       (sets the stop flag, and nothing else)

A rehearsal runs the same commands with `--rehearsal <n>` on calibration batches C1 and C2, its stages named
`rehearsal_attack`, `rehearsal_heldout_1`, `rehearsal_heldout_2`, `rehearsal_delta_attack`, `rehearsal_delta_heldout`;
then `validate --rehearsal <n>` and `record --rehearsal <n>`.

One container handles one batch of one arm (`batch_gpu`, single use: a restart is always a new container). A held-out
container is handed its own batch's token ids and the attack batches' names; it reads the attack searches' saved
settings from the volume. What each container is handed is built by `lead_launch.container_inputs`.

Everything a container writes is sealed, under `/cache/s5_lead/<arm>/sealed/` on the volume. A container returns what
`lead_run.job_return` allows, with the count of its lives, and nothing else. Nothing here prints: the containers and
this launcher both write through `lead_run.Log`. An error in a container reaches the launcher as a guard's name with
its unit, or as an error's type with the place it was raised; never as an error's own text.

Each command is `lead_launch`'s, which has no cloud call in it and is tested without the cloud; this module hands it the
cloud as plain functions and does nothing else on the local side. The image, the volume, and the model loader are the
earlier stages'. Container settings are the pilot's (`gpu="B200"`, `memory=32768`), on which the spend projection rests.
"""

from __future__ import annotations

import datetime
import os
import signal
import time
import traceback
import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any

import modal
import numpy as np

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-lead", image=image)
control = modal.Dict.from_name("vpd-audit-2-lead-control", create_if_missing=True)
LOG = LR.Log()
assert LL.VOLUME_S5 == str(Path(CACHE) / "s5_lead")
# The provider's listed prices, read from https://modal.com/pricing on the day of the first rehearsal and again on the
# day this was written. Money is counted from them and from the pilot's billed rate (`lead_ledger.money`).
LISTED = {"read_on": "2026-10-06", "source": "https://modal.com/pricing", "gpu_b200_per_second": 0.001736, "cpu_core_per_second": 0.0000131,
          "memory_gib_per_second": 0.00000222,
          "notes": "base prices; the page lists a minimum of 0.125 cores per container, 1.15 to 1.75 times base for region selection, and 3 times "
                   "base for non-preemptible execution, none of which this run requests"}
# The container's configuration. No CPU is requested, so the provider's minimum of 0.125 cores is reserved; one process
# drives the GPU, and one core is counted here, the larger figure.
CONTAINER = {"gpu": "B200", "memory_mib": 32768, "cpu_cores_assumed": 1.0}
BILLS_SINCE = datetime.datetime(2026, 10, 6, tzinfo=datetime.timezone.utc)  # the day of the first rehearsal


def _listed_hourly_price() -> float:
    return 3600.0 * (LISTED["gpu_b200_per_second"] + CONTAINER["cpu_cores_assumed"] * LISTED["cpu_core_per_second"]
                     + CONTAINER["memory_mib"] / 1024.0 * LISTED["memory_gib_per_second"])


def _where(exc: BaseException) -> str:
    frames = traceback.extract_tb(exc.__traceback__)
    ours = [f for f in frames if "vpd_audit_2" in Path(f.filename).parts] or frames
    f = ours[-1]
    return f"{Path(f.filename).stem}.{f.name} line {f.lineno}"


# ----------------------------------------------------------------------------- the control dictionary


def _stop_key(run: str) -> str:
    return f"stop|{run}"


def _set_stop(run: str, value: bool) -> None:
    control[_stop_key(run)] = bool(value)


def _should_stop(run: str) -> Callable[[], bool]:
    def ask() -> bool:
        try:
            return bool(control.get(_stop_key(run), False))
        except Exception:  # noqa: BLE001  (a control that cannot be read never stops a paid container half way)
            return False

    return ask


def _lives_key(spec: dict[str, Any]) -> str:
    return f"lives|{spec['launch']}|{spec['arm']}|{spec['side']}|{spec['batch']}"


def _lives_so_far(spec: dict[str, Any]) -> int:
    try:
        return len(control.get(_lives_key(spec)) or [])
    except Exception:  # noqa: BLE001
        return 0


def _register_life(spec: dict[str, Any]) -> int:
    """A container's life, counted at its start: the provider reruns an input whose container died, and the launcher
    must count every life. Returns how many lives this container's call has now had, or 0 if the count cannot be kept."""
    try:
        lives = list(control.get(_lives_key(spec)) or []) + [os.environ.get("MODAL_TASK_ID", "unknown")]
        control[_lives_key(spec)] = lives
        return len(lives)
    except Exception:  # noqa: BLE001
        return 0


def _kill_once(spec: dict[str, Any]) -> Callable[[], None]:
    """A rehearsal's kill: once in the run, the container commits the volume, so that its restart finds what it had
    written, and kills its own process. The provider then reruns its input on a new container."""

    def kill() -> None:
        if control.get(spec["kill_key"]) is None:
            volume.commit()
            control[spec["kill_key"]] = os.environ.get("MODAL_TASK_ID", "unknown")
            os.kill(os.getpid(), signal.SIGKILL)

    return kill


# ----------------------------------------------------------------------------- in the cloud


def _container(spec: dict[str, Any], ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]], strata: dict[str, np.ndarray] | None,
               lay: list, t0: float) -> dict[str, Any]:
    trigger = LR.rehearsal_trigger(spec, set_stop=lambda: _set_stop(spec["run"], True), kill=_kill_once(spec))
    LR.check_spec(spec, trigger is not None)
    lives = _register_life(spec)
    model, files = _load_model()
    env = {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}
    out = LR.run_spec(model, spec, ids, rows, starts, strata, lay, environment=env, log=LOG, commit_volume=volume.commit, should_stop=_should_stop(spec["run"]),
                      fault=trigger, t0=t0)
    volume.commit()
    out["attempts"] = lives
    return out


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=3 * 3600, memory=32768, single_use_containers=True)
def batch_gpu(spec: dict, ids: np.ndarray, rows: list, starts: dict, strata: dict | None, lay: list) -> dict:
    """One batch of one arm, on one B200. The token ids it receives are those of `spec["batch"]` and of no other batch."""
    t0 = time.time()
    try:
        return _container(spec, ids, rows, starts, strata, lay, t0)
    except LR.GuardFailure:
        raise
    except Exception as exc:  # noqa: BLE001  (an error's own text can hold a value; its type and place cannot)
        raise LR.ContainerFailure(f"{type(exc).__name__} at {_where(exc)}", f"{spec['arm']}|{spec['side']}|{spec['batch']}") from None


@app.function(volumes={CACHE: volume}, cpu=4, memory=16384, timeout=3600)
def assemble_cpu(spec: dict) -> dict:
    """Build one arm's table from its unit files, on the volume. CPU only. Returns names, hashes, sizes of the axes,
    and guard outcomes (`lead_run.assemble_from_spec`), with its seconds."""
    t0 = time.time()
    try:
        out = LR.assemble_from_spec(spec)
        volume.commit()
        out["seconds"] = float(time.time() - t0)
        return out
    except LR.GuardFailure:
        raise
    except Exception as exc:  # noqa: BLE001
        raise LR.ContainerFailure(f"{type(exc).__name__} at {_where(exc)}", f"assemble|{spec['arm']}") from None


@app.function(volumes={CACHE: volume}, cpu=4, memory=16384, timeout=3600)
def guards_cpu(spec: dict) -> dict:
    """The guards-only pass (plan 4, Section 4.3): the assembler's cross-unit guards on the listed held-out batches'
    blocks against the attack searches. CPU only. Returns each guard's name with true or false, and its seconds."""
    t0 = time.time()
    try:
        return {"outcomes": LR.guards_from_spec(spec), "seconds": float(time.time() - t0)}
    except LR.GuardFailure:
        raise
    except Exception as exc:  # noqa: BLE001
        raise LR.ContainerFailure(f"{type(exc).__name__} at {_where(exc)}", f"guards|{spec['arm']}") from None


# ----------------------------------------------------------------------------- the local side


def _bill(app_ids: list[str]) -> dict[str, Any]:
    """What the provider has billed each of the named apps so far, with the time of the reading. Billing posts by the
    hour and late; no check waits for it, and a reading that fails is recorded as one that found nothing."""
    out: dict[str, Any] = {"read_at": LL.utc_now(), "latest_interval_posted": None, "by_app": {}, "error": None}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            items = [dict(it) for it in modal.billing.workspace_billing_report(start=BILLS_SINCE, resolution="h")]
        if items:
            out["latest_interval_posted"] = str(max(d["interval_start"] for d in items))
        for d in items:
            if d.get("object_id") in app_ids:
                out["by_app"][d["object_id"]] = out["by_app"].get(d["object_id"], 0.0) + float(d["cost"])
    except Exception as exc:  # noqa: BLE001
        out["error"] = type(exc).__name__
    return out


def _read_file(remote: str) -> bytes:
    """A file of the volume, as bytes. Nothing here parses it."""
    return b"".join(volume.read_file(str(Path(remote).relative_to(CACHE))))


@app.local_entrypoint()
def stage(name: str, commit: str, rehearsal: int = 0, trigger: str = "", accept_expected_refusals: bool = False) -> None:
    """One stage, at the commit named: every container of it at once, then its spend check, and after wave 1 the
    guards-only pass (`lead_launch.stage_command`). Refuses unless the earlier stages are complete and nothing has
    stopped the run. With `--rehearsal <n>` the stage is the rehearsal's, on calibration batches; `--trigger` and
    `--accept-expected-refusals` are a rehearsal's alone."""
    from vpd_audit_2 import pilot as P

    side = LG.stage_named(name, LL.design_of(rehearsal)).side
    starts = LL.rehearsal_starts() if rehearsal else LL.starts_for()
    strata = LL.strata_by_module()[0] if side == "heldout" else None
    lay = P.layout()
    run = LL.run_key(rehearsal)

    def spawn(spec: dict[str, Any]) -> Any:
        ids, rows = LL.container_inputs(spec)  # this batch's token ids, and no other's
        return batch_gpu.spawn(spec, ids, rows, starts, strata, lay)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: _set_stop(run, value), attempts=_lives_so_far, read_bill=_bill, guards=guards_cpu.remote,
                     app_id=app.app_id, log=LOG)
    LL.stage_command(name, commit, rehearsal, cloud, listed_hourly_price=_listed_hourly_price(), trigger=trigger or None,
                     accept_expected_refusals=accept_expected_refusals)


@app.local_entrypoint()
def assemble(commit: str, rehearsal: int = 0) -> None:
    """Assemble each arm's table on the volume from the units the stages recorded, copy it to the local side as bytes,
    and write its receipt (`lead_launch.assemble_command`)."""
    LL.assemble_command(commit, rehearsal, assemble=assemble_cpu.remote, read_file=_read_file, app_id=app.app_id, log=LOG)


@app.local_entrypoint()
def backup(commit: str, rehearsal: int = 0) -> None:
    """One copy of every search unit's file off the volume, as bytes, unopened, to a local folder that git ignores,
    with a do-not-open notice (`lead_launch.backup_command`): the saved settings and gradients are on the volume alone,
    and a lost volume would force a rerun of searches that must reproduce bit for bit."""
    LL.backup_command(commit, rehearsal, read_file=_read_file, log=LOG)


@app.local_entrypoint()
def stop(rehearsal: int = 0) -> None:
    """Set the run's stop flag, and nothing else. Every running container finishes the search it is on, or the attack
    batch's blocks it is on, and returns `stopped`. The next launch of a stage clears the flag."""
    run = LL.run_key(rehearsal)
    _set_stop(run, True)
    LOG(event="stop_flag_set", container=run, ok=control.get(_stop_key(run)) is True)


@app.local_entrypoint()
def validate(rehearsal: int) -> None:
    """Load each of a rehearsal's copied tables with plan 1's loader, run plan 1's checks, and give every check's name
    with pass or fail and no value (`lead_launch.validate_command`). It reads a rehearsal's tables and refuses any other."""
    LL.validate_command(rehearsal, log=LOG)


@app.local_entrypoint()
def record(rehearsal: int) -> None:
    """The rehearsal's record (`lead_launch.record_command`): each required outcome as met or not, its timings, and
    check C0 for the run."""
    LL.record_command(rehearsal, listed={**LISTED, "container": CONTAINER, "hourly_price_of_the_configuration": _listed_hourly_price()},
                      listed_hourly_price=_listed_hourly_price(), read_bill=_bill, killed=control.get, log=LOG)
