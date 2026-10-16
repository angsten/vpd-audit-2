"""The Modal app for the three-arm experiment (plan 6 of the research log). Every GPU command is
`three_arm_run`'s, tested without the cloud; this module hands it the cloud as plain functions. The image, the volume,
the model loader, the container settings (one B200, 32 GiB, preemptible, single use), the control dictionary, and the
bill's reader are the lead run's (`modal_lead`).

    uv run modal run vpd_audit_2/modal_three_arm.py::checkpoint                          (amendment 2; CPU)
    uv run python -m vpd_audit_2.three_arm_run texts                                    (the text plan, committed before any launch)
    uv run modal run vpd_audit_2/modal_three_arm.py::upload_texts
    uv run modal run vpd_audit_2/modal_three_arm.py::launch --stage gate --commit <c>        then collect, then `three_arm_run gate`
    uv run modal run vpd_audit_2/modal_three_arm.py::launch --stage rehearsal --commit <c>   then collect, then `three_arm_run rehearsal`
    uv run modal run vpd_audit_2/modal_three_arm.py::launch --stage run --commit <c>         then collect
    uv run python -m vpd_audit_2.three_arm_run extension --commit <c>                    (amendment 6's rule; launch `extension` if it calls for one)
    uv run python -m vpd_audit_2.three_arm_run carry --commit <c>                        then launch and collect `carry`
    uv run python -m vpd_audit_2.three_arm_read results/s7_three_arm                     (the reading, committed before the launch)
    uv run modal run vpd_audit_2/modal_three_arm.py::stop
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
from vpd_audit_2 import s6_run as SR
from vpd_audit_2 import three_arm_run as TR
from vpd_audit_2.modal_app import CACHE, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model

app = modal.App("vpd-audit-2-s7-three-arm", image=image)
LOG = LR.Log()
assert TR.VOLUME == str(Path(CACHE) / "s7_three_arm")


def _read_sources(unit: str, sha256: str) -> np.ndarray:
    data = (Path(TR.VOLUME) / TR.UNITS / f"{unit}.npz").read_bytes()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise TR.ThreeArmFailure(f"{unit} is not the run's unit")
    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        return z["sources"]


@app.function(volumes={CACHE: volume}, gpu=ML.CONTAINER["gpu"], timeout=4 * 3600, memory=ML.CONTAINER["memory_mib"], single_use_containers=True)
def arm_gpu(spec: dict, batch_inputs: dict, lay: list) -> dict:
    """One container of a stage, on one B200."""
    t0 = time.time()
    try:
        TR.check_spec(spec)
        lives = ML._register_life(spec)
        model, files = _load_model()
        env = {**_environment(), "checkpoints": files, "task": os.environ.get("MODAL_TASK_ID")}
        ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=[tuple(x) for x in lay], environment=env, log=LOG,
                         commit_volume=volume.commit, should_stop=ML._should_stop(spec["run"]), t0=t0, mode=TR.MODE)
        texts = None
        if spec["stage"] != "carry":
            texts = TR.load_texts(Path(TR.VOLUME) / TR.TEXTS_FILE, spec["job"]["texts_sha256"])
        out = TR.job(model, ctx, spec, texts=texts, batch_inputs=batch_inputs, read_sources=_read_sources)
        volume.commit()
        out["attempts"] = lives
        return out
    except LR.GuardFailure:
        raise
    except TR.ThreeArmFailure as exc:
        raise LR.ContainerFailure(f"ThreeArmFailure: {exc}", f"{spec['arm']}|{spec['stage']}|{spec['batch']}") from None
    except Exception as exc:  # noqa: BLE001  (an error's own text can hold a value; its type and place cannot)
        raise LR.ContainerFailure(f"{type(exc).__name__} at {ML._where(exc)}", f"{spec['arm']}|{spec['stage']}|{spec['batch']}") from None


@app.function(volumes={CACHE: volume}, cpu=4, memory=16384, timeout=1800)
def checkpoint_cpu() -> dict:
    """Amendment 2: whether the released checkpoint holds the persistent sources or their Adam state. Lists the
    checkpoint's keys (by name only), and every file of the released run's artifact folder."""
    import torch

    from vpd_audit_2 import env  # noqa: F401  (cache paths first)

    from vpd_audit import artifacts

    t0 = time.time()
    path = artifacts.decomp_checkpoint_path("main", env.ARTIFACTS_DIR)
    sd = torch.load(path, map_location="cpu", mmap=True, weights_only=True)
    keys = list(sd)
    words = ("ppgd", "pgd", "source", "adam", "exp_avg", "optim", "persistent", "_m.", "_v.")
    hits = [k for k in keys if any(w in k.lower() for w in words)]
    shapes = {k: list(v.shape) for k, v in sd.items() if hasattr(v, "shape")}
    by_prefix: dict[str, int] = {}
    for k in keys:
        p = ".".join(k.split(".")[:2])
        by_prefix[p] = by_prefix.get(p, 0) + 1
    folder = Path(path).parent
    files = sorted(str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file())
    any_source_shape = [k for k, s in shapes.items() if len(s) == 3 and s[1] == 512]
    return {"checkpoint": str(path), "bytes": Path(path).stat().st_size, "n_keys": len(keys), "keys_naming_an_adversary_or_optimizer": hits,
            "tensors_shaped_like_a_per_position_source": any_source_shape, "keys_by_prefix": by_prefix, "run_folder_files": files,
            "seconds": float(time.time() - t0)}


def _no_guards_pass(spec: dict[str, Any]) -> dict[str, Any]:
    raise LL.LaunchRefusal("the three-arm experiment has no guards-only pass")


@app.local_entrypoint()
def checkpoint() -> None:
    out = checkpoint_cpu.remote()
    out["at"] = LL.utc_now()
    out["holds_persistent_sources"] = bool(out["keys_naming_an_adversary_or_optimizer"] or out["tensors_shaped_like_a_per_position_source"])
    LL.write_json(TR.RESULTS / "checkpoint_check.json", out)
    LOG(event="checkpoint_checked", container="checkpoint", ok=not out["holds_persistent_sources"], count=int(out["n_keys"]))


@app.local_entrypoint()
def upload_texts() -> None:
    plan = json.load(open(TR.RESULTS / "texts.json"))
    local = TR.LOCAL / TR.TEXTS_FILE
    if hashlib.sha256(local.read_bytes()).hexdigest() != plan["texts_file_sha256"]:
        raise LL.LaunchRefusal("the local texts file is not the committed plan's")
    with volume.batch_upload(force=True) as batch:
        batch.put_file(str(local), f"/{Path(TR.VOLUME).name}/{TR.TEXTS_FILE}")
    back = ML._read_file(f"{TR.VOLUME}/{TR.TEXTS_FILE}")
    LOG(event="texts_uploaded", container="texts", ok=hashlib.sha256(back).hexdigest() == plan["texts_file_sha256"])


@app.local_entrypoint()
def launch(stage: str, commit: str) -> None:
    from vpd_audit_2 import pilot as P

    lay = [list(x) for x in P.layout()]

    def spawn(spec: dict[str, Any]) -> Any:
        inputs = {}
        if spec["stage"] == "carry":
            from vpd_audit_2.manifest import pool_ids

            pools = LL._manifest()["pools"]
            for h in spec["job"]["batches"]:
                if pools[h]["pool"] != "H":
                    raise LL.LaunchRefusal(f"{h} is not a held-out pool")
                ids, _t, rows = pool_ids(h)
                inputs[h] = (ids, list(rows))
        return arm_gpu.spawn(spec, inputs, lay)

    cloud = LL.Cloud(spawn=spawn, set_stop=lambda value: ML._set_stop(TR.RUN, value), attempts=ML._lives_so_far, read_bill=ML._bill, guards=_no_guards_pass,
                     app_id=app.app_id, log=LOG)
    TR.launch_command(stage, commit, cloud, listed_hourly_price=ML._listed_hourly_price())


@app.local_entrypoint()
def collect(stage: str, commit: str) -> None:
    TR.collect_command(stage, commit, read_file=ML._read_file, log=LOG)


@app.local_entrypoint()
def stop() -> None:
    ML._set_stop(TR.RUN, True)
    LOG(event="stop_flag_set", container=TR.RUN, ok=ML.control.get(ML._stop_key(TR.RUN)) is True)
