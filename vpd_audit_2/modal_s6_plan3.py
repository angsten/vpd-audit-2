"""The Modal app for session 6's plan 3: the first post's comparison rerun (Section 4) and the intact-background variants
(Section 7, added after the readings, as description), in one launch (`sessions/006/engineering/plan_3.md`).

On the head's go, at the commit it names, in this order:

    uv run modal run vpd_audit_2/modal_s6_plan3.py::launch --commit <c>    (12 containers at once: QB1 to QB8, and H1, H5, H9, H13)
    uv run modal run vpd_audit_2/modal_s6_plan3.py::collect --commit <c>   (the 404 unit files, as bytes, to .cache/s6_plan3/)
    uv run python -m vpd_audit_2.s6_rerun                                  (the readings, committed before the launch)
    uv run python -m vpd_audit_2.s6_variants
    uv run modal run vpd_audit_2/modal_s6_plan3.py::stop                   (sets the stop flag, and nothing else)

Each command is `s6_plan3_run`'s, tested without the cloud. The image, the volume, the model loader, the container
settings, the control dictionary, and the bill's reader are the lead run's (`modal_lead`): one B200, 32 GiB,
preemptible, single use.
"""

from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any

import modal
import numpy as np

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import modal_lead as ML
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_run as SR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-s6-plan3", image=image)
LOG = LR.Log()
assert R3.VOLUME == str(Path(CACHE) / "s6_plan3")


def _read_run_unit(run_hashes: dict[str, str]):
    def read(attack: str, start: int) -> dict[str, np.ndarray]:
        p = Path(SR.RUN_UNITS) / f"search_{attack}_s{start}.npz"
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != run_hashes[p.name]:
            raise SR.S6Failure(f"{p.name} is not the run's unit")
        return SR.run_unit_from_bytes(data, attack, start)

    return read


def _model_and_environment() -> tuple[Any, dict[str, Any]]:
    model, files = _load_model()
    return model, {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}


def _failure(spec: dict[str, Any], exc: BaseException) -> Exception:
    where = f"{spec['arm']}|{spec['side']}|{spec['batch']}"
    if isinstance(exc, SR.S6Failure):
        return LR.ContainerFailure(f"S6Failure: {exc}", where)
    return LR.ContainerFailure(f"{type(exc).__name__} at {ML._where(exc)}", where)


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def rerun_gpu(spec: dict, ids: np.ndarray, rows: list, starts: dict, lay: list) -> dict:
    """One batch of pool Q, on one B200: its ten searches of 20 steps, each scored on this batch only."""
    t0 = time.time()
    try:
        R3.check_spec(spec)
        lives = ML._register_life(spec)
        model, env = _model_and_environment()
        out = R3.run_rerun_spec(model, spec, ids, rows, starts, lay, environment=env, log=LOG, commit_volume=volume.commit,
                                should_stop=ML._should_stop(spec["run"]), t0=t0)
        volume.commit()
        out["attempts"] = lives
        return out
    except LR.GuardFailure:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _failure(spec, exc) from None


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def variants_gpu(spec: dict, batch_inputs: dict, starts: dict, strata: dict, lay: list, run_hashes: dict) -> dict:
    """One S4 batch, on one B200: the check, then the three variants of the 400 carried settings."""
    t0 = time.time()
    try:
        R3.check_spec(spec)
        lives = ML._register_life(spec)
        model, env = _model_and_environment()
        ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=[tuple(x) for x in lay], environment=env, log=LOG,
                         commit_volume=volume.commit, should_stop=ML._should_stop(spec["run"]), t0=t0)
        inputs = SR.Inputs(starts={int(k): np.asarray(v, dtype=np.float32) for k, v in starts.items()}, strata=strata,
                           read_run_unit=_read_run_unit(run_hashes), b2=None)
        out = R3.variants_job(model, ctx, spec, batch_inputs, inputs)
        volume.commit()
        out["attempts"] = lives
        return out
    except LR.GuardFailure:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _failure(spec, exc) from None


def _no_guards_pass(spec: dict[str, Any]) -> dict[str, Any]:
    raise LL.LaunchRefusal("plan 3 has no guards-only pass")  # the launcher asks for one only in a three-stage design


@app.local_entrypoint()
def launch(commit: str) -> None:
    """The one stage, at the commit named, after the checks and the projection (`s6_plan3_run.launch_command`)."""
    from vpd_audit_2 import pilot as P

    lay = [list(x) for x in P.layout()]
    rerun_starts = R3.load_starts()
    flat_starts = SR.flat_starts()
    strata = LL.strata_by_module()[0]
    run_hashes = SR.run_unit_hashes()

    def spawn(spec: dict[str, Any]) -> Any:
        if spec["part"] == R3.RERUN:
            ids, rows = R3.rerun_inputs(spec)  # this batch's token ids, and no other's
            return rerun_gpu.spawn(spec, ids, rows, rerun_starts, lay)
        return variants_gpu.spawn(spec, R3.variants_inputs(spec), flat_starts, strata, lay, run_hashes)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: ML._set_stop(R3.RUN, value), attempts=ML._lives_so_far, read_bill=ML._bill, guards=_no_guards_pass,
                     app_id=app.app_id, log=LOG)
    R3.launch_command(commit, cloud, listed_hourly_price=ML._listed_hourly_price())


@app.local_entrypoint()
def collect(commit: str) -> None:
    """The unit files to the local side as bytes, each checked against its container's hash (`s6_plan3_run.collect_command`)."""
    R3.collect_command(commit, read_file=ML._read_file, log=LOG)


@app.local_entrypoint()
def stop() -> None:
    """Set the launch's stop flag, and nothing else. Every running container finishes the unit it is on and returns
    `stopped`. The next launch clears the flag."""
    ML._set_stop(R3.RUN, True)
    LOG(event="stop_flag_set", container=R3.RUN, ok=ML.control.get(ML._stop_key(R3.RUN)) is True)
