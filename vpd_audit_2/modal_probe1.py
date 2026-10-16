"""The Modal app for probe 1 (plan 5 of the research log). Every command is `probe1_run`'s, tested
without the cloud; this module hands it the cloud as plain functions. The image, the volume, the model loader, the
container settings (one B200, 32 GiB, preemptible, single use), the control dictionary, and the bill's reader are the
lead run's (`modal_lead`).

    uv run modal run vpd_audit_2/modal_probe1.py::launch --stage validation --commit <c>
    uv run modal run vpd_audit_2/modal_probe1.py::collect --stage validation --commit <c>
    uv run python -m vpd_audit_2.probe1_run validate --commit <c>                          (the pass rule; nothing scores unless it passed)
    uv run modal run vpd_audit_2/modal_probe1.py::launch --stage s320 --commit <c> [--points intact,pattern]
    uv run modal run vpd_audit_2/modal_probe1.py::collect --stage s320 --commit <c>
    uv run modal run vpd_audit_2/modal_probe1.py::launch --stage s80 --commit <c> [--points intact]
    uv run modal run vpd_audit_2/modal_probe1.py::collect --stage s80 --commit <c>
    uv run python -m vpd_audit_2.probe1_read results/s7_probe1                              (the reading, committed before the launch)
    uv run modal run vpd_audit_2/modal_probe1.py::stop                                     (sets the stop flag, and nothing else)
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
from vpd_audit_2 import probe1_run as PR
from vpd_audit_2 import s6_run as SR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-s7-probe1", image=image)
LOG = LR.Log()
assert PR.VOLUME == str(Path(CACHE) / "s7_probe1")


def _read_run_unit(run_hashes: dict[str, str]):
    def read(attack: str, start: int) -> dict[str, np.ndarray]:
        p = Path(SR.RUN_UNITS) / f"search_{attack}_s{start}.npz"
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != run_hashes[p.name]:
            raise PR.ProbeFailure(f"{p.name} is not the run's unit")
        return SR.run_unit_from_bytes(data, attack, start)

    return read


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=3 * 3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def probe_gpu(spec: dict, batch_inputs: dict, lay: list, run_hashes: dict) -> dict:
    """One container of a stage, on one B200: the validation on H1, or a group of batches at one length."""
    t0 = time.time()
    try:
        PR.check_spec(spec)
        lives = ML._register_life(spec)
        model, files = _load_model()
        env = {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}
        ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=[tuple(x) for x in lay], environment=env, log=LOG,
                         commit_volume=volume.commit, should_stop=ML._should_stop(spec["run"]), t0=t0, mode=PR.MODE)
        out = PR.job(model, ctx, spec, batch_inputs, _read_run_unit(run_hashes), scratch=Path(spec["root"]) / PR.TIMING)
        volume.commit()
        out["attempts"] = lives
        return out
    except LR.GuardFailure:
        raise
    except PR.ProbeFailure as exc:
        raise LR.ContainerFailure(f"ProbeFailure: {exc}", f"{spec['arm']}|{spec['stage']}|{spec['batch']}") from None
    except Exception as exc:  # noqa: BLE001  (an error's own text can hold a value; its type and place cannot)
        raise LR.ContainerFailure(f"{type(exc).__name__} at {ML._where(exc)}", f"{spec['arm']}|{spec['stage']}|{spec['batch']}") from None


def _no_guards_pass(spec: dict[str, Any]) -> dict[str, Any]:
    raise LL.LaunchRefusal("probe 1 has no guards-only pass")


@app.local_entrypoint()
def launch(stage: str, commit: str, points: str = "") -> None:
    from vpd_audit_2 import pilot as P

    lay = [list(x) for x in P.layout()]
    run_hashes = SR.run_unit_hashes()

    def spawn(spec: dict[str, Any]) -> Any:
        return probe_gpu.spawn(spec, PR.container_inputs(spec), lay, run_hashes)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: ML._set_stop(PR.RUN, value), attempts=ML._lives_so_far, read_bill=ML._bill, guards=_no_guards_pass,
                     app_id=app.app_id, log=LOG)
    PR.launch_command(stage, commit, cloud, listed_hourly_price=ML._listed_hourly_price(), points=tuple(points.split(",")) if points else None)


@app.local_entrypoint()
def collect(stage: str, commit: str) -> None:
    PR.collect_command(stage, commit, read_file=ML._read_file, log=LOG)


@app.local_entrypoint()
def stop() -> None:
    ML._set_stop(PR.RUN, True)
    LOG(event="stop_flag_set", container=PR.RUN, ok=ML.control.get(ML._stop_key(PR.RUN)) is True)
