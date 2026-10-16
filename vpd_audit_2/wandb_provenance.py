"""Fetch the raw WandB sources behind provenance/provenance.md (small text files only; no checkpoints).

    uv run python -m vpd_audit_2.wandb_provenance              (files, summary, listing)
    uv run python -m vpd_audit_2.wandb_provenance --history    (selected loss histories; see fetch_history)

For each run it writes, under provenance/runs/<run_id>/:
- `wandb_file_listing.json`: every file WandB lists for the run (name, bytes, md5, updated_at);
- the small text files the run has among SMALL_FILES, byte for byte as WandB serves them (WandB's own
  `config.yaml` is fetched to the cache only; see CACHE_ONLY_FILES);
- `wandb_metadata.json`: the run's metadata as the API returns it (git commit, remote, host count, GPU count);
- `run_info.json`: the run's id, name, project, state, tags, creation time, and commit;
- `summary.json`: the run summary as the API returns it, with full float precision;
- `summary_keys.txt`: the sorted keys of the summary, one per line.
`output.log` (too large) and `config.yaml` (personal metadata) go to <cache>/wandb_logs/<run_id>/ instead.

`provenance/runs/sha256.txt` lists the SHA-256 of every downloaded file, committed or not.

For p-8383f5e5 (project goodfire/param-decomp) only the listing, metadata, run info, summary, and the
config are fetched; its checkpoints are never downloaded.

The key is read from the environment or a `.env` file (this repository's, then its parent's) and is
never printed or written.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

from vpd_audit_2 import env

RUNS: dict[str, str] = {
    "s-55ea3f9b": "goodfire/spd",  # the released decomposition
    "s-05ef623e": "goodfire/spd",  # trained without the adversarial loss
    "t-9d2b8f02": "goodfire/spd",  # the target model
    "p-8383f5e5": "goodfire/param-decomp",  # the authors' newer reference run (listing and logs only)
    # plan 2 of the research log, section 5: the five likely seed runs of provenance C.2 and the tag-commit replica (listing and logs only)
    "s-e8bde534": "goodfire/spd",
    "s-73d2385c": "goodfire/spd",
    "s-aac60aec": "goodfire/spd",
    "s-2d14f6c0": "goodfire/spd",
    "s-6a33629b": "goodfire/spd",
    "p-537e31f3": "goodfire/spd",
}
SMALL_FILES = ("final_config.yaml", "requirements.txt", "wandb-summary.json", "sweep_params.yaml",
               "model_config.yaml", "wandb-metadata.json", "diff.patch")
# output.log is too large to commit; config.yaml holds WandB's machine metadata (git commit, GPU count, Slurm
# layout) but also an author's email and internal host addresses, so it is kept out of the repository and quoted.
CACHE_ONLY_FILES = ("output.log", "config.yaml")
NEVER_DOWNLOAD_SUFFIXES = (".pth", ".pt", ".safetensors", ".ckpt", ".npz", ".msgpack", ".orbax")


def wandb_api_key() -> str:
    key = os.environ.get("WANDB_API_KEY")
    if key:
        return key
    from dotenv import dotenv_values

    for p in (env.REPO_ROOT / ".env", env.REPO_ROOT.parent / ".env"):
        if p.is_file():
            key = dotenv_values(p).get("WANDB_API_KEY")
            if key:
                return key
    raise RuntimeError("WANDB_API_KEY is neither in the environment nor in a .env file")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 23), b""):
            h.update(block)
    return h.hexdigest()


def _download(file_obj: Any, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    scratch = env.CACHE_DIR / "_wandb_dl"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    file_obj.download(root=str(scratch), replace=True)
    got = scratch / file_obj.name
    assert got.is_file(), got
    os.replace(got, dest)
    shutil.rmtree(scratch)


def _jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)


def fetch(run_ids: list[str] | None = None) -> dict[str, dict[str, str]]:
    import wandb

    key = wandb_api_key()
    os.environ["WANDB_API_KEY"] = key  # this process only: `File.download` builds its own client from the environment
    api = wandb.Api(api_key=key, timeout=120)
    hashes: dict[str, dict[str, str]] = {}
    for rid in run_ids or list(RUNS):
        project = RUNS[rid]
        out = env.PROVENANCE_DIR / "runs" / rid
        out.mkdir(parents=True, exist_ok=True)
        run = api.run(f"{project}/{rid}")
        files = list(run.files())
        listing = [{"name": f.name, "bytes": int(f.size), "md5": getattr(f, "md5", None),
                    "updated_at": str(getattr(f, "updated_at", ""))} for f in files]
        with open(out / "wandb_file_listing.json", "w") as fh:
            json.dump({"run": f"{project}/{rid}", "n_files": len(listing), "files": sorted(listing, key=lambda d: d["name"])},
                      fh, indent=2, sort_keys=True)
        hashes[rid] = {}
        by_name = {f.name: f for f in files}
        for name in SMALL_FILES:
            if name in by_name:
                _download(by_name[name], out / name)
                hashes[rid][f"provenance/runs/{rid}/{name}"] = sha256_file(out / name)
        for name in CACHE_ONLY_FILES:
            if name in by_name:
                dest = env.CACHE_DIR / "wandb_logs" / rid / name
                _download(by_name[name], dest)
                hashes[rid][f".cache/wandb_logs/{rid}/{name} (not committed)"] = sha256_file(dest)
        for name in by_name:
            assert not (name in SMALL_FILES and name.endswith(NEVER_DOWNLOAD_SUFFIXES))
        meta = _jsonable(run.metadata or {})
        info = {"id": run.id, "name": run.name, "project": project, "state": run.state, "tags": list(run.tags),
                "created_at": str(run.created_at), "commit": getattr(run, "commit", None), "url": run.url}
        summary = _jsonable(dict(run.summary._json_dict))
        for fname, obj in (("wandb_metadata.json", meta), ("run_info.json", info), ("summary.json", summary)):
            with open(out / fname, "w") as fh:
                json.dump(obj, fh, indent=2, sort_keys=True)
            hashes[rid][f"provenance/runs/{rid}/{fname} (API, written here)"] = sha256_file(out / fname)
        with open(out / "summary_keys.txt", "w") as fh:
            fh.write("\n".join(sorted(summary)) + "\n")
        print(f"[provenance] {project}/{rid}: {len(files)} files listed; downloaded {sorted(n for n in SMALL_FILES if n in by_name)}",
              flush=True)
    write_sha256_list(hashes)
    return hashes


SHA256_LIST = env.PROVENANCE_DIR / "runs" / "sha256.txt"


def _run_of(path: str) -> str:
    """The run a listed path belongs to: `provenance/runs/<run>/...` or `.cache/wandb_logs/<run>/...`."""
    parts = path.split("/")
    if path.startswith("provenance/runs/") or path.startswith(".cache/wandb_logs/"):
        return parts[2]
    raise ValueError(f"unexpected path in {SHA256_LIST.name}: {path}")


def write_sha256_list(fetched: dict[str, dict[str, str]]) -> None:
    """Merge the hashes of the runs just fetched into `sha256.txt`: every entry of those runs is replaced (so a file
    no longer downloaded drops out), every entry of the other runs is kept as it was. Runs are written in RUNS order,
    then any others, each run's paths sorted."""
    by_run: dict[str, dict[str, str]] = {}
    if SHA256_LIST.is_file():
        for line in SHA256_LIST.read_text().splitlines():
            if not line.strip():
                continue
            digest, path = line.split("  ", 1)
            by_run.setdefault(_run_of(path), {})[path] = digest
    for rid, entries in fetched.items():
        assert all(_run_of(p) == rid for p in entries), (rid, sorted(entries))
        by_run[rid] = dict(entries)
    order = [r for r in RUNS if r in by_run] + sorted(r for r in by_run if r not in RUNS)
    lines = [f"{by_run[rid][p]}  {p}" for rid in order for p in sorted(by_run[rid])]
    SHA256_LIST.write_text("\n".join(lines) + "\n")


HISTORY_KEYS = ("eval/loss/PGDReconLoss", "eval/loss/StochasticReconSubsetLoss", "eval/loss/StochasticHiddenActsReconLoss",
                "eval/loss/CIHiddenActsReconLoss", "train/loss/total", "train/loss/ImportanceMinimalityLoss",
                "train/loss/StochasticReconSubsetLoss", "train/loss/PersistentPGDReconLoss", "train/loss/FaithfulnessLoss",
                "eval/l0/0.0_total", "eval/ce_kl/kl_zero_masked")
HISTORY_CACHE = env.CACHE_DIR / "wandb_history" / "loss_histories.json"


def fetch_history(run_ids: tuple[str, ...] = ("s-55ea3f9b", "s-05ef623e"), refresh: bool = False) -> dict[str, dict[str, list]]:
    """Every logged (step, value) of HISTORY_KEYS, one `scan_history` per key (keys are logged at different cadences, and a
    scan over several keys returns only the rows holding all of them). Slow (about 30 minutes for both runs), so the raw
    result is cached at HISTORY_CACHE and reused unless `refresh`. Writes provenance/runs/<run_id>/loss_history.csv:
    one row per (key, step), values at full precision."""
    if HISTORY_CACHE.is_file() and not refresh:
        with open(HISTORY_CACHE) as fh:
            raw = json.load(fh)
    else:
        import wandb

        key = wandb_api_key()
        os.environ["WANDB_API_KEY"] = key
        api = wandb.Api(api_key=key, timeout=300)
        raw = {}
        for rid in run_ids:
            run = api.run(f"{RUNS[rid]}/{rid}")
            raw[rid] = {k: sorted(set((r["_step"], r[k]) for r in run.scan_history(keys=["_step", k], page_size=2000))) for k in HISTORY_KEYS}
        HISTORY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_CACHE, "w") as fh:
            json.dump(raw, fh)
    for rid in run_ids:
        lines = ["key,step,value"]
        for k in HISTORY_KEYS:
            for step, value in sorted((int(s), v) for s, v in raw[rid].get(k, [])):
                lines.append(f"{k},{step},{value!r}")
        with open(env.PROVENANCE_DIR / "runs" / rid / "loss_history.csv", "w") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"[provenance] {rid}: {len(lines) - 1} logged values of {len(HISTORY_KEYS)} keys", flush=True)
    return raw


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--history":
        fetch_history(refresh="--refresh" in args)
    else:
        fetch(args or None)
