"""The Modal app for the starts test (`sessions/006/engineering/plan_1.md`, Section 2.3).

On the head's go, at the commit it names, in this order:

    uv run modal run vpd_audit_2/modal_starts.py::launch --commit <c>    (8 containers at once, one per calibration batch)
    uv run modal run vpd_audit_2/modal_starts.py::collect --commit <c>   (the 41 unit files, the guard, then records.json)
    uv run python -m vpd_audit_2.starts_test                             (the reading, committed before the job)
    uv run modal run vpd_audit_2/modal_starts.py::stop                   (sets the stop flag, and nothing else)

Each command is `starts_run`'s, which has no cloud call in it and is tested without the cloud; this module hands it the
cloud as plain functions. The image, the volume, and the model loader are the earlier stages'; the container settings,
the control dictionary, the bill's reader, and the listed prices are the lead run's (`modal_lead`): one B200, 32 GiB,
preemptible, single use. Nothing is sealed, but a container still returns only what `lead_run.job_return` allows, with
its timings, and an error reaches the launcher as a guard's name or an error's type with the place it was raised.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import modal
import numpy as np

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import modal_lead as ML
from vpd_audit_2 import starts_run as SR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-starts", image=image)
LOG = LR.Log()
assert SR.VOLUME == str(Path(CACHE) / "s6_starts")


def _container(spec: dict[str, Any], ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]], lay: list, t0: float) -> dict[str, Any]:
    SR.check_spec(spec)
    lives = ML._register_life(spec)
    model, files = _load_model()
    env = {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}
    out = SR.run_spec(model, spec, ids, rows, starts, lay, environment=env, log=LOG, commit_volume=volume.commit, should_stop=ML._should_stop(spec["run"]), t0=t0)
    volume.commit()
    out["attempts"] = lives
    return out


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=3 * 3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def starts_gpu(spec: dict, ids: np.ndarray, rows: list, starts: dict, lay: list) -> dict:
    """One calibration batch, on one B200: its searches from the starts it is handed, each scored on this batch only."""
    t0 = time.time()
    try:
        return _container(spec, ids, rows, starts, lay, t0)
    except LR.GuardFailure:
        raise
    except Exception as exc:  # noqa: BLE001
        raise LR.ContainerFailure(f"{type(exc).__name__} at {ML._where(exc)}", f"{spec['arm']}|{spec['side']}|{spec['batch']}") from None


def _no_guards_pass(spec: dict[str, Any]) -> dict[str, Any]:
    raise LL.LaunchRefusal("the starts test has no guards-only pass")  # the launcher asks for one only in a three-stage design


@app.local_entrypoint()
def launch(commit: str) -> None:
    """The one stage, at the commit named, after the checks and the projection (`starts_run.launch_command`)."""
    from vpd_audit_2 import pilot as P

    starts = SR.load_starts()
    lay = P.layout()

    def spawn(spec: dict[str, Any]) -> Any:
        ids, rows = SR.container_inputs(spec)  # this batch's token ids, and no other's
        return starts_gpu.spawn(spec, ids, rows, SR.starts_for_batch(starts, spec["batch"]), lay)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: ML._set_stop(SR.RUN, value), attempts=ML._lives_so_far, read_bill=ML._bill, guards=_no_guards_pass,
                     app_id=app.app_id, log=LOG)
    SR.launch_command(commit, cloud, listed_hourly_price=ML._listed_hourly_price())


@app.local_entrypoint()
def collect(commit: str) -> None:
    """The unit files to the local side as bytes, the guard, and the records (`starts_run.collect_command`)."""
    SR.collect_command(commit, read_file=ML._read_file, log=LOG)


@app.local_entrypoint()
def stop() -> None:
    """Set the test's stop flag, and nothing else. Every running container finishes the search it is on and returns
    `stopped`. The next launch clears the flag."""
    ML._set_stop(SR.RUN, True)
    LOG(event="stop_flag_set", container=SR.RUN, ok=ML.control.get(ML._stop_key(SR.RUN)) is True)
