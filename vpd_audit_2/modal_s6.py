"""The Modal app for plan 2 of the research log, Section 3.

In this order, the GPU waves on the go-ahead:

    uv run modal run vpd_audit_2/modal_s6.py::build_b2                         (CPU: the sixteen (b2) settings, before the hold)
    uv run modal run vpd_audit_2/modal_s6.py::launch --commit <c> --wave 1     (H1 alone, an S4 batch: every kind of unit)
    uv run modal run vpd_audit_2/modal_s6.py::launch --commit <c> --wave 2     (the other 15 held-out batches and 8 attack pairs)
    uv run modal run vpd_audit_2/modal_s6.py::collect --commit <c>             (the unit files, as bytes, to .cache/s6_followups/units/)
    uv run modal run vpd_audit_2/modal_s6.py::stop                             (sets the stop flag, and nothing else)

Each command is `s6_run`'s, tested without the cloud. The image, the volume, the model loader, the container settings,
the control dictionary, and the bill's reader are the lead run's (`modal_lead`): one B200, 32 GiB, preemptible, single use.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import time
from pathlib import Path
from typing import Any

import modal
import numpy as np

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import modal_lead as ML
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-s6", image=image)
LOG = LR.Log()
assert SR.VOLUME == str(Path(CACHE) / "s6_followups")
LABEL_CACHE = Path(CACHE) / "labels" / "Q_fp32.npz"


def _read_run_unit(run_hashes: dict[str, str]):
    def read(attack: str, start: int) -> dict[str, np.ndarray]:
        p = Path(SR.RUN_UNITS) / f"search_{attack}_s{start}.npz"
        data = p.read_bytes()
        if hashlib.sha256(data).hexdigest() != run_hashes[p.name]:
            raise SR.S6Failure(f"{p.name} is not the run's unit")
        return SR.run_unit_from_bytes(data, attack, start)

    return read


def _b2(sha: str) -> dict[str, np.ndarray]:
    p = Path(SR.VOLUME) / SR.B2_FILE
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise SR.S6Failure("the (b2) settings are not the ones built")
    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        return {k: np.asarray(z[k], dtype=np.float32) for k in z.files}


def _container(spec: dict[str, Any], batch_inputs: dict, starts: dict, strata: dict, lay: list, run_hashes: dict, b2_sha: str, t0: float) -> dict[str, Any]:
    SR.check_spec(spec)
    lives = ML._register_life(spec)
    model, files = _load_model()
    env = {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}
    ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=[tuple(x) for x in lay], environment=env, log=LOG,
                     commit_volume=volume.commit, should_stop=ML._should_stop(spec["run"]), t0=t0)
    inputs = SR.Inputs(starts={int(k): np.asarray(v, dtype=np.float32) for k, v in starts.items()}, strata=strata, read_run_unit=_read_run_unit(run_hashes),
                       b2=_b2(b2_sha) if spec["side"] == "heldout" else None)
    out = SR.job(model, ctx, spec, batch_inputs, inputs)
    volume.commit()
    out["attempts"] = lives
    return out


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=3 * 3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def s6_gpu(spec: dict, batch_inputs: dict, starts: dict, strata: dict, lay: list, run_hashes: dict, b2_sha: str) -> dict:
    """One held-out batch, or two attack batches, on one B200."""
    t0 = time.time()
    try:
        return _container(spec, batch_inputs, starts, strata, lay, run_hashes, b2_sha, t0)
    except LR.GuardFailure:
        raise
    except SR.S6Failure as exc:
        raise LR.ContainerFailure(f"S6Failure: {exc}", f"{spec['arm']}|{spec['side']}|{spec['batch']}") from None
    except Exception as exc:  # noqa: BLE001
        raise LR.ContainerFailure(f"{type(exc).__name__} at {ML._where(exc)}", f"{spec['arm']}|{spec['side']}|{spec['batch']}") from None


@app.function(volumes={CACHE: volume}, cpu=4, memory=16384, timeout=1800)
def b2_cpu(lay: list) -> dict:
    """The sixteen (b2) settings from the first post's float32 label cache, written to the volume as one file."""
    from vpd_audit_2 import prices
    from vpd_audit_2.manifest import deterministic_npz

    t0 = time.time()
    cache, meta = prices.load_cache(LABEL_CACHE, keys=("indptr", "indices", "values"))
    lay = [tuple(x) for x in lay]
    to_flat = B.global_to_flat(meta["module_offsets"], meta["module_to_c"], lay)
    n_flat = sum(c + 1 for _, c in lay)
    settings, record = {}, {}
    for rung, draws in B.B2_RUNGS:
        for d in range(1, draws + 1):
            pos = B.b2_positions(rung, d, int(meta["n_positions"]))
            flat, size = B.b2_setting(cache["indptr"], cache["indices"], cache["values"], pos, to_flat, n_flat)
            key = f"r{rung}_d{d}"
            settings[key] = flat
            record[key] = {"rung": rung, "draw": d, "union_size": size, "setting_sha256": B.sha(flat),
                           "positions_sha256": hashlib.sha256(pos.astype(np.int64).tobytes()).hexdigest()}
    data = deterministic_npz(settings)
    p = Path(SR.VOLUME) / SR.B2_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    volume.commit()
    return {"file": SR.B2_FILE, "file_sha256": hashlib.sha256(data).hexdigest(), "settings": record, "cache_sha256": meta["sha256"],
            "n_positions": int(meta["n_positions"]), "threshold": B.B2_THRESHOLD, "seconds": time.time() - t0}


def _no_guards_pass(spec: dict[str, Any]) -> dict[str, Any]:
    raise LL.LaunchRefusal("plan 2 of the research log has no guards-only pass")


@app.local_entrypoint()
def build_b2() -> None:
    """Build the (b2) settings on the volume and record their hashes and union sizes in results/s6_followups/b2_settings.json."""
    from vpd_audit_2 import pilot as P

    out = b2_cpu.remote([list(x) for x in P.layout()])
    LL.write_json(SR.B2_RECORD, {**out, "app_id": app.app_id, "at": LL.utc_now()})
    LOG(event="b2_built", count=len(out["settings"]), sha256=out["file_sha256"])


@app.local_entrypoint()
def launch(commit: str, wave: int) -> None:
    from vpd_audit_2 import pilot as P

    lay = [list(x) for x in P.layout()]
    starts = {s: v for s, v in SR.flat_starts().items()}
    strata = LL.strata_by_module()[0]
    run_hashes = SR.run_unit_hashes()
    b2_sha = json.load(open(SR.B2_RECORD))["file_sha256"]

    def spawn(spec: dict[str, Any]) -> Any:
        return s6_gpu.spawn(spec, SR.container_inputs(spec), starts, strata, lay, run_hashes, b2_sha)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: ML._set_stop(SR.RUN, value), attempts=ML._lives_so_far, read_bill=ML._bill, guards=_no_guards_pass,
                     app_id=app.app_id, log=LOG)
    SR.launch_command(commit, int(wave), cloud, listed_hourly_price=ML._listed_hourly_price())


@app.local_entrypoint()
def collect(commit: str) -> None:
    SR.collect_command(commit, read_file=ML._read_file, log=LOG)


@app.local_entrypoint()
def stop() -> None:
    ML._set_stop(SR.RUN, True)
    LOG(event="stop_flag_set", container=SR.RUN, ok=ML.control.get(ML._stop_key(SR.RUN)) is True)
