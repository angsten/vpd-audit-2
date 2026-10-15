"""Plan 2, step 3 (section 5): two log checks, with no GPU.

    uv run python -m vpd_audit_2.sister_runs

1. The sister runs. For the five likely seed runs of provenance C.2, every logged value of the seven keys behind the
   paper's training and evaluation tables (paper lines 2219-2232), compared with the paper's values, plus every logged
   `eval/loss/PGDReconLoss` compared with the adversarial table's 20-step 0.8280 (line 395). A value "matches" when it
   rounds to the paper's printed value at the paper's printed decimals. Each run's raw `final_config.yaml` is compared
   field by field with the released run's.
2. `p-537e31f3`: its file listing (no checkpoint is downloaded), its checkpoints and their steps, its commit, and its
   `final_config.yaml` compared with the released run's.
3. The released run's CI-masked KL, `eval/ce_kl/kl_ci_masked` (delta components excluded: `ce_and_kl_losses.py`
   `make_mask_infos(ci)`), its final value and its spread over the last 41 evaluations (steps 360,000 to 400,000).

The small files of each run are fetched by `wandb_provenance.fetch` into `provenance/runs/<run_id>/`. Histories are
cached per (run, key) under <cache>/wandb_history/ and written to `provenance/runs/<run_id>/loss_history.csv`
(released run: `kl_ci_masked_history.csv`). Results: `results/plan2_sister_runs/sister_runs.json`.
"""

from __future__ import annotations

import json
import math
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import numpy as np
import yaml

from vpd_audit_2 import env
from vpd_audit_2.wandb_provenance import RUNS, fetch, wandb_api_key

SEED_RUNS = ("s-e8bde534", "s-73d2385c", "s-aac60aec", "s-2d14f6c0", "s-6a33629b")
REPLICA = "p-537e31f3"
RELEASED = "s-55ea3f9b"
# the paper's values with their printed decimals (paper lines 2219-2232 and 395)
PAPER = {
    "train/loss/ImportanceMinimalityLoss": (1102.0, 1),
    "train/loss/StochasticReconSubsetLoss": (0.2419, 4),
    "train/loss/PersistentPGDReconLoss": (0.5733, 4),
    "eval/loss/StochasticReconSubsetLoss": (0.2381, 4),
    "eval/loss/PGDReconLoss": (0.9268, 4),
    "eval/loss/StochasticHiddenActsReconLoss": (0.4130, 4),
    "eval/loss/CIHiddenActsReconLoss": (0.8464, 4),
}
PAPER_ADV_20 = (0.8280, 4)
KL_CI_KEY = "eval/ce_kl/kl_ci_masked"
CACHE = env.CACHE_DIR / "wandb_history" / "per_key"
OUT_DIR = env.REPO_ROOT / "results" / "plan2_sister_runs"
FINAL_STEP = 400000


def log(msg: str) -> None:
    print(f"[sister-runs] {msg}", flush=True)


def _history(api: Any, rid: str, key: str) -> list[tuple[int, float]]:
    path = CACHE / f"{rid}__{key.replace('/', '__')}.json"
    if path.is_file():
        return [tuple(x) for x in json.load(open(path))]
    run = api.run(f"{RUNS[rid]}/{rid}")
    rows = sorted({(int(r["_step"]), float(r[key])) for r in run.scan_history(keys=["_step", key], page_size=5000) if r.get(key) is not None})
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(rows, open(path, "w"))
    log(f"{rid} {key}: {len(rows)} values")
    return rows


def _flatten(x: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(x, dict):
        out: dict[str, Any] = {}
        for k, v in x.items():
            out.update(_flatten(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    if isinstance(x, list):
        out = {}
        for i, v in enumerate(x):
            tag = v.get("classname", i) if isinstance(v, dict) else i
            out.update(_flatten(v, f"{prefix}[{tag}]"))
        return out
    return {prefix: x}


def config_diff(rid: str) -> dict[str, Any]:
    a = _flatten(yaml.safe_load(open(env.PROVENANCE_DIR / "runs" / RELEASED / "final_config.yaml")))
    path = env.PROVENANCE_DIR / "runs" / rid / "final_config.yaml"
    if not path.is_file():
        return {"final_config_present": False}
    b = _flatten(yaml.safe_load(open(path)))
    diff = {k: {"released": a.get(k, "<absent>"), rid: b.get(k, "<absent>")} for k in sorted(set(a) | set(b)) if a.get(k, "<absent>") != b.get(k, "<absent>")}
    return {"final_config_present": True, "n_fields_released": len(a), "n_fields_here": len(b), "differences": diff,
            "equal_apart_from_seed": set(diff) <= {"seed"}}


def matches(rows: list[tuple[int, float]], target: float, decimals: int) -> dict[str, Any]:
    hit = [(s, v) for s, v in rows if round(v, decimals) == round(target, decimals)]
    near = min(rows, key=lambda sv: abs(sv[1] - target)) if rows else None
    at_final = next((v for s, v in rows if s == FINAL_STEP), None)
    return {"n_logged": len(rows), "matching_steps": [[s, v] for s, v in hit], "nearest": list(near) if near else None,
            "value_at_step_400000": at_final}


def write_csv(rid: str, hist: dict[str, list[tuple[int, float]]], name: str = "loss_history.csv") -> None:
    lines = ["key,step,value"]
    for k in hist:
        for s, v in hist[k]:
            lines.append(f"{k},{s},{v!r}")
    with open(env.PROVENANCE_DIR / "runs" / rid / name, "w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> dict[str, Any]:
    import wandb

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fetch(list(SEED_RUNS) + [REPLICA])
    key = wandb_api_key()
    os.environ["WANDB_API_KEY"] = key
    api = wandb.Api(api_key=key, timeout=300)

    jobs = [(rid, k) for rid in SEED_RUNS for k in PAPER] + [(RELEASED, KL_CI_KEY)]
    with ThreadPoolExecutor(8) as ex:
        hists = dict(zip(jobs, ex.map(lambda j: _history(api, *j), jobs)))

    out: dict[str, Any] = {"paper_values": {k: v[0] for k, v in PAPER.items()}, "paper_adversarial_20_step": PAPER_ADV_20[0],
                           "match_rule": "a logged value matches when it rounds to the paper's value at the paper's printed decimals", "runs": {}}
    for rid in SEED_RUNS:
        info = json.load(open(env.PROVENANCE_DIR / "runs" / rid / "run_info.json"))
        h = {k: hists[(rid, k)] for k in PAPER}
        write_csv(rid, h)
        out["runs"][rid] = {
            "name": info["name"], "commit": info["commit"], "state": info["state"], "created_at": info["created_at"],
            "config_vs_released": config_diff(rid),
            "paper_tables": {k: matches(h[k], *PAPER[k]) for k in PAPER},
            "adversarial_20_step_0.8280": matches(h["eval/loss/PGDReconLoss"], *PAPER_ADV_20),
        }
        log(f"{rid}: config equal apart from seed: {out['runs'][rid]['config_vs_released']['equal_apart_from_seed']}; "
            f"0.8280 matches at {[s for s, _ in out['runs'][rid]['adversarial_20_step_0.8280']['matching_steps']]}")
    # which run and step, if any, matches each value
    out["by_value"] = {}
    for k, (v, d) in list(PAPER.items()) + [("eval/loss/PGDReconLoss (adversarial table, 20 steps)", PAPER_ADV_20)]:
        src = "eval/loss/PGDReconLoss" if k.startswith("eval/loss/PGDReconLoss (") else k
        hits = [{"run": rid, "step": s, "value": val} for rid in SEED_RUNS for s, val in hists[(rid, src)] if round(val, d) == round(v, d)]
        out["by_value"][k] = {"paper": v, "matches": hits,
                              "matches_at_step_400000": [x for x in hits if x["step"] == FINAL_STEP]}
    # p-537e31f3
    listing = json.load(open(env.PROVENANCE_DIR / "runs" / REPLICA / "wandb_file_listing.json"))
    ckpts = [f for f in listing["files"] if f["name"].endswith((".pth", ".pt", ".safetensors", ".ckpt"))]
    rinfo = json.load(open(env.PROVENANCE_DIR / "runs" / REPLICA / "run_info.json"))
    rsum = json.load(open(env.PROVENANCE_DIR / "runs" / REPLICA / "summary.json"))
    out["replica"] = {"run": REPLICA, "name": rinfo["name"], "commit": rinfo["commit"], "state": rinfo["state"], "created_at": rinfo["created_at"],
                      "n_files": listing["n_files"], "checkpoints": ckpts, "summary_step": rsum.get("_step"),
                      "config_vs_released": config_diff(REPLICA)}

    # the released run's CI-masked KL
    kl = hists[(RELEASED, KL_CI_KEY)]
    write_csv(RELEASED, {KL_CI_KEY: kl}, name="kl_ci_masked_history.csv")
    last = [v for s, v in kl if 360000 <= s <= FINAL_STEP]
    lg = np.log(last)
    out["released_kl_ci_masked"] = {"key": KL_CI_KEY, "delta_components": "excluded (make_mask_infos(ci), ce_and_kl_losses.py)",
                                    "final_step": kl[-1][0], "final_value": kl[-1][1], "n_last": len(last), "steps": [360000, FINAL_STEP],
                                    "mean": float(np.mean(last)), "sd": float(np.std(last, ddof=1)), "min": float(np.min(last)), "max": float(np.max(last)),
                                    "geometric_mean": float(math.exp(lg.mean())), "log_sd": float(lg.std(ddof=1)),
                                    "first_post_value": 0.3417}
    with open(OUT_DIR / "sister_runs.json", "w") as f:
        json.dump(out, f, indent=1)
    log(f"wrote {OUT_DIR / 'sister_runs.json'}")
    return out


if __name__ == "__main__":
    main()
