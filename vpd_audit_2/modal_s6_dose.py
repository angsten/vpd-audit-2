"""The Modal app for session 6's plan 3, Section 8: the dose-response on an intact model, on cell set S4. Added after the
readings, as description.

    uv run modal run vpd_audit_2/modal_s6_dose.py::launch --commit <c>    (4 containers at once: H1, H5, H9, H13)
    uv run modal run vpd_audit_2/modal_s6_dose.py::collect --commit <c>   (the 324 unit files, as bytes, to .cache/s6_dose/)
    uv run python -m vpd_audit_2.s6_dose                                  (the reading, committed before the launch)
    uv run modal run vpd_audit_2/modal_s6_dose.py::stop                   (sets the stop flag, and nothing else)

Each command is `s6_dose_run`'s, tested without the cloud. The image, the volume, the model loader, the container
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
from vpd_audit_2 import s6_dose_run as D
from vpd_audit_2 import s6_run as SR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-s6-dose", image=image)
LOG = LR.Log()
assert D.VOLUME == str(Path(CACHE) / "s6_dose")


def _read_run_unit(run_hashes: dict[str, str]):
    def read(attack: str, start: int) -> dict[str, np.ndarray]:
        p = Path(SR.RUN_UNITS) / f"search_{attack}_s{start}.npz"
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != run_hashes[p.name]:
            raise SR.S6Failure(f"{p.name} is not the run's unit")
        return SR.run_unit_from_bytes(data, attack, start)

    return read


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def dose_gpu(spec: dict, batch_inputs: dict, starts: dict, strata: dict, lay: list, run_hashes: dict) -> dict:
    """One S4 batch, on one B200: the check, then the dose passes of the 400 carried settings."""
    t0 = time.time()
    try:
        D.check_spec(spec)
        lives = ML._register_life(spec)
        model, files = _load_model()
        env = {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}
        ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=[tuple(x) for x in lay], environment=env, log=LOG,
                         commit_volume=volume.commit, should_stop=ML._should_stop(spec["run"]), t0=t0)
        inputs = SR.Inputs(starts={int(k): np.asarray(v, dtype=np.float32) for k, v in starts.items()}, strata=strata,
                           read_run_unit=_read_run_unit(run_hashes), b2=None)
        out = D.dose_job(model, ctx, spec, batch_inputs, inputs)
        volume.commit()
        out["attempts"] = lives
        return out
    except LR.GuardFailure:
        raise
    except SR.S6Failure as exc:
        raise LR.ContainerFailure(f"S6Failure: {exc}", f"{spec['arm']}|{spec['side']}|{spec['batch']}") from None
    except Exception as exc:  # noqa: BLE001
        raise LR.ContainerFailure(f"{type(exc).__name__} at {ML._where(exc)}", f"{spec['arm']}|{spec['side']}|{spec['batch']}") from None


def _no_guards_pass(spec: dict[str, Any]) -> dict[str, Any]:
    raise LL.LaunchRefusal("the dose-response has no guards-only pass")


@app.local_entrypoint()
def launch(commit: str) -> None:
    from vpd_audit_2 import pilot as P

    lay = [list(x) for x in P.layout()]
    starts = SR.flat_starts()
    strata = LL.strata_by_module()[0]
    run_hashes = SR.run_unit_hashes()

    def spawn(spec: dict[str, Any]) -> Any:
        return dose_gpu.spawn(spec, D.dose_inputs(spec), starts, strata, lay, run_hashes)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: ML._set_stop(D.RUN, value), attempts=ML._lives_so_far, read_bill=ML._bill, guards=_no_guards_pass,
                     app_id=app.app_id, log=LOG)
    D.launch_command(commit, cloud, listed_hourly_price=ML._listed_hourly_price())


@app.local_entrypoint()
def collect(commit: str) -> None:
    D.collect_command(commit, read_file=ML._read_file, log=LOG)


@app.local_entrypoint()
def stop() -> None:
    ML._set_stop(D.RUN, True)
    LOG(event="stop_flag_set", container=D.RUN, ok=ML.control.get(ML._stop_key(D.RUN)) is True)
