"""The Modal app for plan 2 of the research log: the world-size metrics, the fresh labels and gate G4, and gate G1.

The image, the volume `vpd-audit-2-cache`, and the cache paths are plan 1 of the research log's (`modal_app.py`). Token ids are passed
in from the local machine, and every function re-hashes what it receives against the hashes the caller records.
The earlier project's volume `vpd-audit-cache` is mounted read-only, and only for gate G4.

    uv run modal run vpd_audit_2/modal_gates.py::world_size      (section 4: the 25 values on each candidate's batch)

Every result is written back to `results/plan2_*` by the local entrypoint that launched it.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import modal
import numpy as np

from vpd_audit_2.modal_app import CACHE, REPO_ROOT, image, volume

app = modal.App("vpd-audit-2-gates", image=image)
OLD_VOLUME = modal.Volume.from_name("vpd-audit-cache").read_only()
OLD_MOUNT = "/old"


def _log(msg: str) -> None:
    print(msg, flush=True)


def _environment() -> dict:
    import torch

    return {"gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None, "torch": torch.__version__,
            "cuda": torch.version.cuda, "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "deterministic_warn_only": torch.is_deterministic_algorithms_warn_only_enabled(),
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "allow_tf32_matmul": torch.backends.cuda.matmul.allow_tf32, "allow_tf32_cudnn": torch.backends.cudnn.allow_tf32,
            "float32_matmul_precision": torch.get_float32_matmul_precision(),
            "vpd_audit_2_commit": os.environ.get("VPD_AUDIT_2_COMMIT"), "vpd_audit_2_dirty": os.environ.get("VPD_AUDIT_2_DIRTY")}


def _load_model():
    import torch

    from vpd_audit_2 import env  # noqa: F401  (cache paths first)

    from vpd_audit import artifacts

    # Strict: an operation with no deterministic implementation raises instead of warning (plan 5 of the research log, item 1).
    # Each result file's environment records deterministic_warn_only = False.
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    verified = artifacts.verify_manifest(env.ARTIFACTS_DIR, ["s-55ea3f9b", "t-9d2b8f02"])
    man = artifacts.read_manifest(env.ARTIFACTS_DIR)
    model = artifacts.load_component_model("main", "cuda")
    files = {rel: man["files"][rel] for rel in verified}
    return model, files


def _sha_rows(ids: np.ndarray) -> list[str]:
    return [hashlib.sha256(np.ascontiguousarray(r, dtype=np.int32).tobytes()).hexdigest() for r in ids]


# ----------------------------------------------------------------------------- section 4


@app.function(volumes={CACHE: volume}, gpu="A100-40GB", timeout=3600, memory=32768)
def world_size_metrics(batches: dict[str, np.ndarray], sha512: dict[str, list[str]]) -> dict:
    t0 = time.time()
    from vpd_audit_2.world_size import metrics_on_batches

    for name, ids in batches.items():
        assert _sha_rows(ids) == sha512[name], f"{name}: the ids received are not the ones recorded"
    model, files = _load_model()
    metrics = metrics_on_batches(model, batches, log_fn=_log)
    layout = [[k, int(model.module_to_c[k])] for k in model.target_module_paths]
    return {"metrics": metrics, "module_layout": layout, "checkpoints": files, "environment": _environment(),
            "precision": "bf16 autocast, no_grad", "seconds": time.time() - t0}


@app.local_entrypoint()
def world_size() -> None:
    from vpd_audit_2.world_size import OUT_DIR, decide

    meta = json.load(open(OUT_DIR / "batches.json"))
    z = np.load(OUT_DIR / "batches.npz")
    batches = {k: z[k] for k in z.files}
    sha512 = {f"W{W}": [t["sha256_512"] for t in meta["candidates"][str(W)]["texts"]] for W in (8, 16, 32)}
    t0 = time.time()
    res = world_size_metrics.remote(batches, sha512)
    res["local_wall_seconds"] = time.time() - t0
    res["decision"] = decide(res["metrics"])
    with open(OUT_DIR / "metrics.json", "w") as f:
        json.dump(res, f, indent=1)
    d = res["decision"]
    print(f"[local] agreeing: {d['agreeing']}; confirmed world size: {d['confirmed_world_size']}")
    for name, t in d["candidates"].items():
        print(f"[local] {name}: max |rel diff| L0 {t['max_abs_relative_difference_l0']:.5f}, kl {t['abs_relative_difference_kl']:.5f}")


# ----------------------------------------------------------------------------- section 7

LABELS_DIR = Path(CACHE) / "labels"
LABELS_RESULTS = REPO_ROOT / "results" / "plan2_labels"


@app.function(volumes={CACHE: volume}, gpu="A100-40GB", timeout=4 * 3600, memory=65536)
def labels_gpu(q_ids: np.ndarray, q_sha512: list[str], du_ids: np.ndarray, du_sha512: list[str]) -> dict:
    """Section 7 on the GPU: the fresh float32 cache of Q with its band (-0.001, 0]; the authors'-path check; the earlier
    harness's reproductions of D_unif_main (pool DU) and E_main (pool Q); the paired float32/bf16 pass over Q."""
    t0 = time.time()
    from vpd_audit_2 import labels as L

    assert _sha_rows(q_ids) == q_sha512, "Q: the ids received are not the manifest's"
    assert _sha_rows(du_ids) == du_sha512, "DU: the ids received are not the manifest's"
    model, files = _load_model()
    env_rec = _environment()
    q_hash = hashlib.sha256(np.ascontiguousarray(q_ids, dtype=np.int32).tobytes()).hexdigest()
    du_hash = hashlib.sha256(np.ascontiguousarray(du_ids, dtype=np.int32).tobytes()).hexdigest()
    meta = L.fresh_cache(model, q_ids, LABELS_DIR / "Q_fp32.npz",
                         {"pool": "Q", "texts": "manifest pool Q: v0 to v1023", "set_hash_ids_512": q_hash, "checkpoints": files,
                          "code_commit": env_rec["vpd_audit_2_commit"], "code_dirty": env_rec["vpd_audit_2_dirty"], "environment": env_rec},
                         log=_log, band=True)
    volume.commit()
    fresh, _ = L.load_fresh(LABELS_DIR / "Q_fp32.npz")
    out = {"fresh_cache": meta, "authors_path_check": L.authors_path_check(model, q_ids, fresh), "environment": env_rec}
    del fresh
    ck = {"decomp": files["s-55ea3f9b/model_400000.pth"]["sha256"], "target": files["t-9d2b8f02/ckpt/model_step_99999.pt"]["sha256"]}
    out["d_unif_reproduction"] = L.reproduce(model, du_ids, "D_unif", LABELS_DIR / "reproduce", du_hash, ck, log=_log)
    out["e_reproduction"] = L.reproduce(model, q_ids, "E", LABELS_DIR / "reproduce", q_hash, ck, log=_log)
    volume.commit()
    pp = L.paired_precision(model, q_ids, log=_log)
    pp["hashes_equal_stored"] = {
        "fp32_pass_vs_fresh_cache": all(pp["sparse_label_hashes"]["fp32"][k] == meta["sha256"][k] for k in ("indptr", "indices", "values")),
        "bf16_pass_vs_E_reproduction": pp["sparse_label_hashes"]["bf16"] == out["e_reproduction"]["sha256"]}
    out["paired_precision"] = pp
    out["seconds"] = time.time() - t0
    return out


@app.function(volumes={CACHE: volume, OLD_MOUNT: OLD_VOLUME}, cpu=4, memory=98304, timeout=3600)
def g4_cpu() -> dict:
    """Gate G4 across precisions and like for like, and the two reproductions, on the CPU. The earlier volume is
    mounted read-only."""
    from vpd_audit_2 import env  # noqa: F401
    from vpd_audit_2 import labels as L

    from vpd_audit.donors import load_cache

    old = Path(OLD_MOUNT) / "donors"
    inherited = load_cache("E_main", out_dir=old)
    fresh, fmeta = L.load_fresh(LABELS_DIR / "Q_fp32.npz")
    assert inherited[3]["set_hash"] == fmeta["set_hash_ids_512"], "the inherited E cache is not on Q's texts"
    out = {"g4_across_precisions": L.g4(inherited, fresh, fmeta)}
    del fresh
    repro = load_cache("E_main", out_dir=LABELS_DIR / "reproduce")
    assert repro[3]["set_hash"] == inherited[3]["set_hash"]
    out["g4_like_for_like"] = L.g4(inherited, {"indptr": repro[0], "indices": repro[1], "values": repro[2]}, repro[3],
                                   fresh_name="vpd-audit-2-cache:labels/reproduce/E_main.npz (bf16, the earlier harness's build_cache)")
    out["e_reproduction"] = L.compare_reproduction(inherited, repro, "E_main")
    del inherited, repro
    out["d_unif"] = L.compare_reproduction(load_cache("D_unif_main", out_dir=old), load_cache("D_unif_main", out_dir=LABELS_DIR / "reproduce"), "D_unif_main")
    out["g4_reading"] = ("passes like for like; across precisions, the value difference is large" if out["g4_like_for_like"]["passes"]
                         else "fails like for like: stop and report")
    return out


@app.local_entrypoint()
def labels() -> None:
    """Section 7 on pools Q and DU: the fresh cache, the authors'-path check, the reproductions, the paired precision
    pass, then G4 across precisions and like for like."""
    from vpd_audit_2.manifest import OUT_DIR as MAN_DIR
    from vpd_audit_2.manifest import pool_ids

    LABELS_RESULTS.mkdir(parents=True, exist_ok=True)
    prev = LABELS_RESULTS / "labels_gpu.json"
    prev_sha = json.load(open(prev))["fresh_cache"]["sha256"] if prev.is_file() else None
    man_sha = hashlib.sha256((MAN_DIR / "manifest.json").read_bytes()).hexdigest()
    q_ids, q_texts, q_sha = pool_ids("Q")
    du_ids, du_texts, du_sha = pool_ids("DU")
    t0 = time.time()
    gpu = labels_gpu.remote(q_ids, q_sha, du_ids, du_sha)
    gpu["local_wall_seconds"] = time.time() - t0
    gpu["pools"] = {"Q": {"texts": [q_texts[0], q_texts[-1]], "n": len(q_texts)}, "DU": {"texts": [du_texts[0], du_texts[-1]], "n": len(du_texts)},
                    "manifest_sha256": man_sha}
    if prev_sha:
        gpu["labels_block_equals_previous_run"] = all(gpu["fresh_cache"]["sha256"][k] == prev_sha[k] for k in ("indptr", "indices", "values", "z"))
    with open(LABELS_RESULTS / "labels_gpu.json", "w") as f:
        json.dump(gpu, f, indent=1, default=str)
    pp = gpu["paired_precision"]
    print(f"[local] fresh cache: {gpu['fresh_cache']['mean_count_above_0_per_position']:.4f} per position, band {gpu['fresh_cache']['mean_band_entries_per_position']:.2f}; "
          f"same labels block as before: {gpu.get('labels_block_equals_previous_run')}; hashes tie: {pp['hashes_equal_stored']}")
    print(f"[local] precision: |g32-g16| {pp['abs_label_difference']['overall']}; crossing 0 {pp['crossing_0_per_position']:.3f}, 0.1 {pp['crossing_0.1_per_position']:.3f} per position")
    t1 = time.time()
    cpu = g4_cpu.remote()
    cpu["local_wall_seconds"] = time.time() - t1
    with open(LABELS_RESULTS / "g4.json", "w") as f:
        json.dump(cpu, f, indent=1)
    for k in ("g4_across_precisions", "g4_like_for_like"):
        g = cpu[k]
        print(f"[local] {k}: passes {g['passes']}; p99.9 {g['abs_label_difference_in_both']['p99.9']:.6f}; mean count {g['mean_count_above_0_per_position']}")
    for k in ("e_reproduction", "d_unif"):
        print(f"[local] {k}: identical arrays {cpu[k]['arrays_identical']}; identical fingerprints {cpu[k]['positions_with_identical_fingerprint']}/{cpu[k]['positions']}")
    print(f"[local] G4: {cpu['g4_reading']}")


# ----------------------------------------------------------------------------- section 8

G1_RESULTS = REPO_ROOT / "results" / "plan2_g1"


@app.function(volumes={CACHE: volume}, gpu="H200", timeout=1800, memory=65536)
def g1_probe(n_steps: int = 3) -> dict:
    """Memory and time per step of one G1 search, on random token ids (no text of any pool): 128 x 512, bf16."""
    import torch

    from vpd_audit_2 import g1

    model, _ = _load_model()
    g = torch.Generator().manual_seed(0)
    ids = torch.randint(0, 50277, (128, 512), generator=g).numpy().astype(np.int32)
    start = {k: torch.rand((1, 1, model.module_to_c[k] + 1), generator=g).numpy() for k in model.target_module_paths}
    out = {"environment": _environment(), "n_steps": n_steps, "texts": "random token ids, generator seed 0"}
    torch.cuda.reset_peak_memory_stats()
    try:
        t0 = time.time()
        r = g1.search(model, ids, start, n_steps, 0.1, precision="bf16")
        out.update({"ok": True, "seconds": r["seconds"], "record": r["record"], "wall_seconds": time.time() - t0})
    except torch.OutOfMemoryError as e:
        out.update({"ok": False, "error": str(e)[:400]})
    out["peak_memory_gib"] = torch.cuda.max_memory_allocated() / 2**30
    out["device_memory_gib"] = torch.cuda.get_device_properties(0).total_memory / 2**30
    return out


@app.local_entrypoint()
def probe(gpus: str = "A100-80GB,H200") -> None:
    G1_RESULTS.mkdir(parents=True, exist_ok=True)
    path = G1_RESULTS / "probe.json"
    res = json.load(open(path)) if path.is_file() else {}
    for gpu in gpus.split(","):
        t0 = time.time()
        r = g1_probe.with_options(gpu=gpu).remote(3)
        r["local_wall_seconds"] = time.time() - t0
        res[gpu] = r
        print(f"[local] {gpu}: ok {r['ok']}, peak {r['peak_memory_gib']:.1f} of {r['device_memory_gib']:.0f} GiB, seconds {r.get('seconds')}")
    with open(G1_RESULTS / "probe.json", "w") as f:
        json.dump(res, f, indent=1)


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=6 * 3600, memory=65536)  # 128 x 512 in one process needs ~140 GiB (probe.json)
def g1_gpu(batch_name: str, ids: np.ndarray, sha512: list[str], jobs: list[dict], starts: dict[int, dict[str, np.ndarray]],
           checks: bool = False) -> dict:
    """G1's searches on one batch: labels once, then each job (candidate, start, n_steps, step size, precision)."""
    t0 = time.time()
    import torch

    from vpd_audit_2 import g1

    assert _sha_rows(ids) == sha512, f"{batch_name}: the ids received are not the manifest's"
    model, files = _load_model()
    out: dict = {"batch": batch_name, "environment": _environment(), "checkpoints": files, "runs": {}}
    batch = torch.from_numpy(ids.astype(np.int64)).to("cuda")
    if checks:
        out["one_minute_checks"] = g1.one_minute_checks(model, ids, starts[jobs[0]["start"]])
        _log(f"[g1] checks: {json.dumps({k: v for k, v in out['one_minute_checks'].items() if k not in ('layout', 'record_wrapped')})}")
        if not out["one_minute_checks"]["bit_identical_final_harm"]:
            out["stopped"] = "wrapped and unwrapped loops differ; no search run"
            return out
    labels = {}
    for job in jobs:
        prec = job["precision"]
        try:
            if prec not in labels:
                labels[prec] = g1.labels_once(model, batch, prec)
            r = g1.search(model, ids, starts[job["start"]], job["n_steps"], job["step_size"], precision=prec, labels=labels[prec])
        except torch.OutOfMemoryError as e:
            out["runs"][job["name"]] = {**job, "out_of_memory": str(e)[:400], "peak_memory_gib": torch.cuda.max_memory_allocated() / 2**30}
            _log(f"[g1] {job['name']}: out of memory")
            labels.clear()
            torch.cuda.empty_cache()
            continue
        src = r.pop("sources")
        src_dir = Path(CACHE) / "g1" / "final_sources"
        src_dir.mkdir(parents=True, exist_ok=True)
        np.savez(src_dir / f"{job['name'].replace('|', '__')}.npz", **src)
        r["final_sources_file"] = f"vpd-audit-2-cache:g1/final_sources/{job['name'].replace('|', '__')}.npz"
        out["runs"][job["name"]] = {**job, **r, "peak_memory_gib": torch.cuda.max_memory_allocated() / 2**30}
        _log(f"[g1] {job['name']}: final {r['final']:.4f} after {job['n_steps']} steps in {r['seconds']:.0f} s")
    volume.commit()
    out["seconds"] = time.time() - t0
    return out


def _g1_jobs(batch: str, start: int, start_key: list, *, check_a: bool = False) -> list[dict]:
    base = {"batch": batch, "start": start, "start_seed_key": start_key, "precision": "bf16"}
    if check_a:
        return [{**base, "name": f"A_c|{batch}|20|s{start}", "candidate": "A_c", "n_steps": 20, "step_size": 0.1}]
    jobs = [{**base, "name": f"A_c|{batch}|320", "candidate": "A_c", "n_steps": 320, "step_size": 0.1}]
    jobs += [{**base, "name": f"A_s|{batch}|{n}", "candidate": "A_s", "n_steps": n, "step_size": 2 / n} for n in (40, 80, 160, 320)]
    return jobs


@app.local_entrypoint()
def g1_run(phase: str = "check_a") -> None:
    """phase check_a: the two one-minute checks and the 20-step adversary on WS_W16 from starts 1 to 8 (section 8.3).
    phase main: C1 to C8, start s = j on C_j; A_c 320 steps, A_s 40/80/160/320; plus the float32 rerun of C1 at 20 steps.
    phase escalate: C9 to C16 likewise. Results accumulate in results/plan2_g1/trajectories.json."""
    from vpd_audit_2 import g1_readings
    from vpd_audit_2.manifest import OUT_DIR as MAN_DIR
    from vpd_audit_2.manifest import load_start, pool_ids

    G1_RESULTS.mkdir(parents=True, exist_ok=True)
    path = G1_RESULTS / "trajectories.json"
    traj = json.load(open(path)) if path.is_file() else {"runs": {}, "containers": {}}
    traj["manifest_sha256"] = hashlib.sha256((MAN_DIR / "manifest.json").read_bytes()).hexdigest()
    man = json.load(open(MAN_DIR / "manifest.json"))
    key = lambda s: man["draws"]["adversary_starts"]["starts"][str(s)]["seed_key"]  # noqa: E731
    t0 = time.time()
    if phase == "check_a":
        ids, texts, sha = pool_ids("WS_W16")
        jobs = [j for s in range(1, 9) for j in _g1_jobs("WS_W16", s, key(s), check_a=True)]
        res = g1_gpu.remote("WS_W16", ids, sha, jobs, {s: load_start(s) for s in range(1, 9)}, checks=True)
        res["local_wall_seconds"] = time.time() - t0
        traj["containers"]["check_a|WS_W16"] = {k: v for k, v in res.items() if k != "runs"}
        traj["runs"].update(res["runs"])
        if "stopped" not in res:
            traj["check_a_anchor_harms"] = [res["runs"][f"A_c|WS_W16|20|s{s}"]["record"][20] for s in range(1, 9)]
            traj["check_a_anchor"] = {"pool": "WS_W16", "texts": "manifest pool WS_W16 (the confirmed step-400,000 evaluation batch)", "starts": list(range(1, 9))}
        json.dump(traj, open(path, "w"), indent=1)
        if "stopped" in res:
            print(f"[local] STOP: {res['stopped']}")
            return
        ca = g1_readings.check_a_anchor(traj["check_a_anchor_harms"])
        print(f"[local] checks: {json.dumps({k: v for k, v in res['one_minute_checks'].items() if k not in ('layout', 'record_wrapped')})}")
        print(f"[local] Check A: harms {[round(x, 4) for x in ca['harms']]}; geometric mean {ca['geometric_mean']:.4f} vs logged {ca['logged']:.4f}; "
              f"|gap| {ca['abs_log_gap']:.4f} <= {ca['half_width_used']:.4f}: {ca['passes']}")
        return
    if phase == "start_spread":  # the follow-up: starts 1 to 8 at 20 steps on C1, C2, C3
        spread = {}
        for b in g1_readings.SPREAD_BATCHES:
            ids, texts, sha = pool_ids(b)
            jobs = [j for s in g1_readings.SPREAD_STARTS for j in _g1_jobs(b, s, key(s), check_a=True)]
            spread[b] = g1_gpu.spawn(b, ids, sha, jobs, {s: load_start(s) for s in g1_readings.SPREAD_STARTS})
        for b, call in spread.items():
            res = call.get()
            traj["containers"][f"start_spread|{b}"] = {k: v for k, v in res.items() if k != "runs"}
            traj["runs"].update(res["runs"])
            json.dump(traj, open(path, "w"), indent=1)
            print(f"[local] {b}: {[(n, round(r['final'], 4)) for n, r in res['runs'].items()]} in {res['seconds']:.0f} s")
        g1_readings.main_spread(path)
        return
    batches = {"main": [f"C{j}" for j in range(1, 9)], "escalate": [f"C{j}" for j in range(9, 17)]}[phase]
    calls = {}
    for b in batches:
        j = int(b[1:])
        ids, texts, sha = pool_ids(b)
        calls[b] = g1_gpu.spawn(b, ids, sha, _g1_jobs(b, j, key(j)), {j: load_start(j)})
    if phase == "main":
        ids, texts, sha = pool_ids("C1")
        fjob = [{"batch": "C1", "start": 1, "start_seed_key": key(1), "precision": "fp32", "name": "A_c|C1|20|fp32", "candidate": "A_c",
                 "n_steps": 20, "step_size": 0.1}]
        calls["C1|fp32"] = g1_gpu.spawn("C1", ids, sha, fjob, {1: load_start(1)})
    for b, call in calls.items():
        res = call.get()
        traj["containers"][f"{phase}|{b}"] = {k: v for k, v in res.items() if k != "runs"}
        traj["runs"].update(res["runs"])
        json.dump(traj, open(path, "w"), indent=1)
        print(f"[local] {b}: {[(n, round(r['final'], 4)) if 'final' in r else (n, 'OOM') for n, r in res['runs'].items()]} in {res['seconds']:.0f} s")
    done = [f"C{j}" for j in range(1, 17) if f"A_c|C{j}|320" in traj["runs"]]
    traj["calibration_batches"] = done
    json.dump(traj, open(path, "w"), indent=1)
    print(f"[local] {phase} done in {time.time() - t0:.0f} s; readings over {done}")
    g1_readings.main(path)
