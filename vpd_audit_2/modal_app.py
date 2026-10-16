"""The Modal app for plan 1 of the research log's smoke test.

One image: Debian slim with Python 3.13; this repository's `pyproject.toml` and `uv.lock`, and the `vpd-audit`
submodule (with the authors' code inside it) copied in and installed from the lockfile with `uv sync --frozen`
(the two path dependencies editable, as locally); `vpd_audit_2` and `provenance/` added at run time.
`VPD_AUDIT_2_CACHE_DIR=/cache`, so `vpd_audit_2.env` points every cache at the volume `vpd-audit-2-cache`, never
inside the submodule. The earlier project's volume `vpd-audit-cache` is not mounted or written.

    uv run modal run vpd_audit_2/modal_app.py::prepare     (CPU: fetch t-9d2b8f02 and s-55ea3f9b, build E and D_unif)
    uv run modal run vpd_audit_2/modal_app.py::main        (GPU: the smoke test; writes results/plan1_smoke/)

The WandB key reaches only `prepare`, as an ephemeral secret read from the `.env` of this repository or the folder
above it; it is never printed or stored.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parent.parent
REMOTE = "/root"
CACHE = "/cache"
VOLUME_NAME = "vpd-audit-2-cache"
GPU = "A100-40GB"  # the earlier project's card, so the first post's numbers compare like for like
GPU_MEMORY_MIB = 32768
RESULTS_DIR = REPO_ROOT / "results" / "plan1_smoke"


def _local_commit() -> dict[str, str]:
    if not modal.is_local():
        return {k: os.environ.get(k, "unknown") for k in ("VPD_AUDIT_2_COMMIT", "VPD_AUDIT_2_DIRTY")}
    try:
        commit = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--untracked-files=no", "--", "."],
                               check=True, capture_output=True, text=True).stdout.strip()
    except Exception:
        return {"VPD_AUDIT_2_COMMIT": "unknown", "VPD_AUDIT_2_DIRTY": "unknown"}
    return {"VPD_AUDIT_2_COMMIT": commit, "VPD_AUDIT_2_DIRTY": "1" if dirty else "0"}


OWN_RESULTS = REPO_ROOT / "results"  # this repository's results: never in the image
IGNORED_NAMES = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".cache", ".venv", "tests", "papers", "logs",
                 "node_modules", "param_decomp.egg-info", "vpd_audit.egg-info"}


def _ignore_under(base: Path):
    """An `ignore` callable for `add_local_dir(base, ...)`. Modal passes it paths relative to `base`. Leaves out of the
    image: git links, caches, tests, the authors' papers and logs, virtual environments, build metadata, any credentials
    file at any depth, and this repository's own `results/` only. Every other `results/` directory, such as the earlier
    harness's `third_party/vpd-audit/results/` with its labelled-set manifest, is kept."""
    base = base.resolve()

    def ignore(p: Path) -> bool:
        if set(p.parts) & IGNORED_NAMES:
            return True
        if any(part == ".env" or part.startswith(".env.") for part in p.parts):
            return True
        return (base / p).resolve().is_relative_to(OWN_RESULTS)

    return ignore


def _dotenv_dir() -> Path:
    for d in (REPO_ROOT, REPO_ROOT.parent):
        if (d / ".env").is_file():
            return d
    return REPO_ROOT


image = (
    modal.Image.debian_slim(python_version="3.13")
    .apt_install("git")
    .pip_install("uv==0.11.26")
    .add_local_file(REPO_ROOT / "pyproject.toml", f"{REMOTE}/pyproject.toml", copy=True)
    .add_local_file(REPO_ROOT / "uv.lock", f"{REMOTE}/uv.lock", copy=True)
    .add_local_dir(REPO_ROOT / "third_party" / "vpd-audit", f"{REMOTE}/third_party/vpd-audit", copy=True,
                   ignore=_ignore_under(REPO_ROOT / "third_party" / "vpd-audit"))
    .workdir(REMOTE)
    .run_commands("UV_PROJECT_ENVIRONMENT=/usr/local uv sync --frozen --no-dev --no-install-project --compile-bytecode --no-progress")
    .env({
        "VPD_AUDIT_2_CACHE_DIR": CACHE,
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        "PYTHONUNBUFFERED": "1",
        **_local_commit(),
    })
    .add_local_dir(REPO_ROOT / "provenance", f"{REMOTE}/provenance")
    .add_local_python_source("vpd_audit_2")
)

app = modal.App("vpd-audit-2", image=image)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


def _log(msg: str) -> None:
    print(msg, flush=True)


@app.function(volumes={CACHE: volume}, secrets=[modal.Secret.from_dotenv(_dotenv_dir())], timeout=2 * 3600, cpu=4, memory=16384)
def prepare() -> dict:
    """The earlier project's own fetch (vpd_audit/artifacts.py) for the target and the released decomposition, and its
    own `prepare_stream_sets` (vpd_audit/data.py) for E and D_unif, into the volume."""
    t0 = time.time()
    from vpd_audit_2 import env  # noqa: F401  (cache paths first)

    from vpd_audit.artifacts import fetch_artifacts
    from vpd_audit.data import load_set, prepare_stream_sets

    manifest = fetch_artifacts(["t-9d2b8f02", "s-55ea3f9b"], log=_log)
    volume.commit()
    prepare_stream_sets(log=_log)
    volume.commit()
    sets = {name: {k: v for k, v in load_set(name)[2].items() if k in ("sha256_ids", "row_indices_first", "row_indices_last", "shape")}
            for name in ("E", "D_unif")}
    files = {k: v for k, v in manifest["files"].items() if k.split("/")[0] in ("t-9d2b8f02", "s-55ea3f9b")}
    return {"files": files, "sets": sets, "seconds": time.time() - t0}


@app.function(volumes={CACHE: volume}, gpu=GPU, timeout=2 * 3600, memory=GPU_MEMORY_MIB)
def smoke() -> dict:
    t0 = time.time()
    from vpd_audit_2 import env  # noqa: F401  (cache paths first)
    from vpd_audit_2.smoke import run_smoke

    out = run_smoke(device="cuda", log=_log)
    out["wall_seconds_in_function"] = time.time() - t0
    with open(Path(CACHE) / "results_plan1_smoke.json", "w") as f:
        json.dump(out, f, indent=1)
    volume.commit()
    return out


@app.local_entrypoint()
def main(stage: str = "smoke") -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if stage in ("prepare", "all"):
        res = prepare.remote()
        with open(RESULTS_DIR / "prepare.json", "w") as f:
            json.dump({**res, "local_wall_seconds": time.time() - t0}, f, indent=1)
        print(f"[local] prepare: {json.dumps(res['sets'])}")
    if stage in ("smoke", "all"):
        t1 = time.time()
        res = smoke.remote()
        res["local_wall_seconds"] = time.time() - t1
        rows = res.pop("row_hashes")
        with open(RESULTS_DIR / "smoke.json", "w") as f:
            json.dump(res, f, indent=1)
        with open(RESULTS_DIR / "first_post_rows.csv", "w") as f:
            f.write("set,row,sha256_int32_512\n")
            for name in ("E", "D_unif"):
                for row, h in rows[name]:
                    f.write(f"{name},{row},{h}\n")
        print(f"[local] smoke: {json.dumps({k: res[k] for k in ('check_5', 'timings_s')}, indent=1)}")
