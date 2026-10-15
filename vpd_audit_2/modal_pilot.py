"""The Modal app for session 4's plan 6, the pilot (`sessions/004/engineering/plan_6.md`).

    uv run modal run vpd_audit_2/modal_pilot.py::strata    (item 4's frequency strata from Q's float32 cache; CPU)
    uv run modal run vpd_audit_2/modal_pilot.py::part_a    (A1 to A3: one B200 per batch C1 to C8)

The image, the volume, and the model loader are the earlier stages'. Every GPU stage loads the model through
`modal_gates._load_model`, which sets strict deterministic algorithms (plan 5); each container's environment records it.
Raw per-run records go to `results/s4_pilot/part_a/`; the hook's sources stay on the volume, their SHA-256 recorded; A3's
shuffle harms go to `results/s4_pilot/part_a/sealed/` and are never printed.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import modal
import numpy as np

from vpd_audit_2.modal_app import CACHE, REPO_ROOT, image, volume
from vpd_audit_2.modal_gates import _environment, _load_model, _log, _sha_rows

app = modal.App("vpd-audit-2-pilot", image=image)
PILOT = REPO_ROOT / "results" / "s4_pilot"
PART_A = PILOT / "part_a"
VOL_PILOT = Path(CACHE) / "s4_pilot"


def _manifest_sha() -> str:
    from vpd_audit_2.manifest import OUT_DIR

    return hashlib.sha256((OUT_DIR / "manifest.json").read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- item 4: the strata


@app.function(volumes={CACHE: volume}, cpu=4, memory=16384, timeout=1800)
def strata_cpu() -> dict:
    from vpd_audit_2 import pilot as P
    from vpd_audit_2 import prices

    cache, meta = prices.load_cache(Path(CACHE) / "labels" / "Q_fp32.npz", keys=("indptr", "indices", "values"))
    s = P.strata_from_cache(cache, meta)
    return {**s, "cache_sha256": {k: meta["sha256"][k] for k in ("indptr", "indices", "values")}, "module_order": meta["module_order"],
            "module_offsets": meta["module_offsets"], "module_to_c": meta["module_to_c"]}


@app.local_entrypoint()
def strata() -> None:
    PART_A.mkdir(parents=True, exist_ok=True)
    res = strata_cpu.remote()
    arrays = {"freq": np.asarray(res["freq"]), "mean_label": np.asarray(res["mean_label"]), "stratum": np.asarray(res["stratum"])}
    from vpd_audit_2.manifest import deterministic_npz

    npz = deterministic_npz(arrays)
    (PART_A / "strata.npz").write_bytes(npz)
    st = arrays["stratum"]
    meta = {"definition": res["definition"], "n_positions": res["n_positions"], "cache_sha256": res["cache_sha256"],
            "global_index": "sorted module order with the cache's module_offsets", "module_offsets": res["module_offsets"],
            "module_to_c": res["module_to_c"], "file_sha256": hashlib.sha256(npz).hexdigest(),
            "counts": {str(v): int((st == v).sum()) for v in range(11)}, "dead_components": int((st == 10).sum())}
    with open(PART_A / "strata.json", "w") as f:
        json.dump(meta, f, indent=1)
    print(f"[local] strata: {meta['counts']}; file {meta['file_sha256'][:12]}")


# ----------------------------------------------------------------------------- Part A


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=3 * 3600, memory=32768)
def part_a_gpu(batch: str, ids: np.ndarray, sha512: list[str], j: int, starts: dict[int, dict[str, np.ndarray]], g1: dict,
               strata_by_module: dict[str, np.ndarray], lay: list) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_a

    assert _sha_rows(ids) == sha512, f"{batch}: the ids received are not the manifest's"
    model, files = _load_model()
    env_rec = _environment()
    assert env_rec["deterministic_algorithms"] and not env_rec["deterministic_warn_only"], env_rec
    out = pilot_a.batch_job(model, batch, ids, j, starts, g1, strata_by_module, [tuple(x) for x in lay], VOL_PILOT / "part_a" / "sources",
                            VOL_PILOT / "part_a" / "sealed" / f"a3_shuffles_{batch}.npz", log=_log)
    volume.commit()
    out.update({"environment": env_rec, "checkpoints": files, "function_seconds": time.time() - t0})
    return out


@app.local_entrypoint()
def part_a(batches: str = "C1,C2,C3,C4,C5,C6,C7,C8") -> None:
    from vpd_audit_2 import pilot as P
    from vpd_audit_2.manifest import load_start, pool_ids

    PART_A.mkdir(parents=True, exist_ok=True)
    (PART_A / "sealed").mkdir(exist_ok=True)
    lay = P.layout()
    starts = {s: P.load_extended_start(s) for s in P.PILOT_STARTS}
    for s in P.PILOT_STARTS:
        ref = load_start(s)
        assert all(np.array_equal(starts[s][k], ref[k]) for k in ref), f"extended start {s} differs from the manifest's"
    smeta = json.load(open(PART_A / "strata.json"))
    with np.load(PART_A / "strata.npz") as z:
        stratum = z["stratum"]
    assert hashlib.sha256((PART_A / "strata.npz").read_bytes()).hexdigest() == smeta["file_sha256"]
    by_module = P.strata_by_module(stratum, smeta, lay)
    g1 = json.load(open(REPO_ROOT / "results" / "plan2_g1" / "trajectories.json"))["runs"]
    calls = {}
    t0 = time.time()
    for b in batches.split(","):
        assert b in P.PILOT_BATCHES, b
        j = int(b[1:])
        ids, texts, sha = pool_ids(b)
        calls[b] = part_a_gpu.spawn(b, ids, sha, j, starts, {"record": g1[f"A_c|{b}|320"]["record"], "sources_sha256": g1[f"A_c|{b}|320"]["sources_sha256"]},
                                    by_module, lay)
    print(f"[local] app {app.app_id}: {len(calls)} containers spawned")
    path = PART_A / "runs.json"
    runs = json.load(open(path)) if path.is_file() else {"a1": {}, "a2": {}, "a3": {}, "containers": {}, "assertions": []}
    for b, c in calls.items():
        res = c.get()
        runs["containers"][b] = {k: res[k] for k in ("batch", "environment", "checkpoints", "function_seconds", "labels_target_seconds") if k in res}
        runs["containers"][b]["app_id"] = app.app_id
        runs["assertions"] += res["assertions"]
        runs["a1"][b] = res["a1"]
        if "stopped" in res:
            runs["containers"][b]["stopped"] = res["stopped"]
            print(f"[local] {b}: STOPPED: {res['stopped']}")
        else:
            runs["a2"][b] = res["a2"]
            runs["a3"][b] = res["a3"]
            # the sealed shuffle harms: copied from the volume as bytes, hash-checked, never loaded here (plan 7, item 5)
            data = b"".join(volume.read_file(str(Path(res["a3_sealed"]["file"]).relative_to(CACHE))))
            assert hashlib.sha256(data).hexdigest() == res["a3_sealed"]["sha256"], f"{b}: the sealed file's hash differs"
            (PART_A / "sealed" / Path(res["a3_sealed"]["file"]).name).write_bytes(data)
            runs.setdefault("a3_sealed_files", {})[b] = {"file": f"sealed/{Path(res['a3_sealed']['file']).name}", "sha256": res["a3_sealed"]["sha256"]}
            del data
        with open(path, "w") as f:
            json.dump(runs, f, indent=1)
        diag = res["a1"][str(int(b[1:]))]
        print(f"[local] {b} done after {time.time() - t0:.0f} s: diagonal equals G1 {diag.get('equals_G1_record')} / {diag.get('equals_G1_final_sources')}; "
              f"A2 {[(r0, v['redraws'], v['accepted'] is not None) for r0, v in res.get('a2', {}).items()]}")
    runs["manifest_sha256"] = _manifest_sha()
    runs["extended_starts_sha256"] = (PILOT / "starts" / "SHA256SUMS").read_text()
    runs["strata_sha256"] = smeta["file_sha256"]
    with open(path, "w") as f:
        json.dump(runs, f, indent=1)
    print(f"[local] Part A runs written: {path}")


# ----------------------------------------------------------------------------- Part B

PART_B = PILOT / "part_b"
CQ_PRICES = PILOT / "cq_prices"
VOL_CQ = VOL_PILOT / "cq"


def _cq() -> tuple[np.ndarray, list[str], list[str]]:
    from vpd_audit_2.manifest import pool_ids

    return pool_ids("CQ")


def _q_free(rows: list[int]) -> list[str]:
    """Q's text ids in the manifest's (and the stored S's) row order, after checking that Q texts `rows` lie outside Q1."""
    from vpd_audit_2.manifest import OUT_DIR

    pools = json.load(open(OUT_DIR / "manifest.json"))["pools"]
    q_texts = pools["Q"]["texts"]
    q1 = set(pools["Q1_set1"]["texts"]) | set(pools["Q1_set2"]["texts"])
    assert len(q1) == 32 and not {q_texts[i] for i in rows} & q1, "the price check's Q texts must lie outside Q1"
    return q_texts


def _partitions() -> dict[str, dict[str, list[int]]]:
    """Partition 1: CQ's first 16 and last 16 texts in manifest order; partitions 2 to 4 by (master, "pilot-partition", p)."""
    from vpd_audit_2.manifest import perm

    parts = {"1": {"set0": list(range(16)), "set1": list(range(16, 32))}}
    for p in (2, 3, 4):
        x = perm(32, "pilot-partition", p)
        parts[str(p)] = {"set0": sorted(int(v) for v in x[:16]), "set1": sorted(int(v) for v in x[16:])}
    return parts


def _env_check() -> dict:
    env_rec = _environment()
    assert env_rec["deterministic_algorithms"] and not env_rec["deterministic_warn_only"], env_rec
    return env_rec


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=3 * 3600, memory=65536)
def part_b_prep_gpu(ids: np.ndarray, sha512: list[str], texts: list[str], q_free: list[int], g3_controls: dict, start1: dict,
                    tuples_sha: str, q_text_ids: list[str]) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_b

    assert _sha_rows(ids) == sha512, "CQ: the ids received are not the manifest's"
    model, files = _load_model()
    env_rec = _env_check()
    out = pilot_b.prep_job(model, ids, texts, q_free, VOL_CQ, Path(CACHE), g3_controls, start1, tuples_sha, q_text_ids, log=_log)
    volume.commit()
    out.update({"environment": env_rec, "checkpoints": files, "function_seconds": time.time() - t0})
    return out


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=1800, memory=32768)
def part_b_n8_gpu(ids: np.ndarray, sha512: list[str], start1: dict) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_b

    assert _sha_rows(ids) == sha512
    model, _ = _load_model()
    env_rec = _env_check()
    return {**pilot_b.n8_job(model, ids, VOL_CQ, start1), "environment": env_rec, "function_seconds": time.time() - t0}


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=4 * 3600, memory=32768)
def part_b_partition_gpu(ids: np.ndarray, sha512: list[str], p: str, sets: list[list[int]], starts: dict, lay: list) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_b

    assert _sha_rows(ids) == sha512
    model, _ = _load_model()
    env_rec = _env_check()
    out = pilot_b.b1_partition_job(model, ids, sets, VOL_CQ, starts, [tuple(x) for x in lay], log=_log, tag=f"partition {p}")
    return {"partition": p, "result": out, "environment": env_rec, "function_seconds": time.time() - t0}


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=4 * 3600, memory=32768)
def part_b_v2_gpu(ids: np.ndarray, sha512: list[str], texts: list[str]) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_b

    assert _sha_rows(ids) == sha512
    model, _ = _load_model()
    env_rec = _env_check()
    out = pilot_b.b1_v2_stoch_job(model, ids, texts, VOL_CQ, log=_log)
    return {"result": out, "environment": env_rec, "function_seconds": time.time() - t0}


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=4 * 3600, memory=32768)
def part_b_b2_gpu(ids: np.ndarray, sha512: list[str], texts: list[str], alive_global: np.ndarray, strata: list, n_per: int) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_b

    assert _sha_rows(ids) == sha512
    model, _ = _load_model()
    env_rec = _env_check()
    out = pilot_b.b2_job(model, ids, texts, VOL_CQ, alive_global, strata, n_per, log=_log)
    return {**out, "environment": env_rec, "function_seconds": time.time() - t0}


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=1800, memory=65536)
def part_b_qprice_gpu(q_text_ids: list[str], q_free: list[int], tuples_sha: str, expected: dict, q_ids_sha256: str) -> dict:
    """Plan 7, item 8's test: Q texts outside Q1 priced from the stored path, against the pilot's stored-path values,
    on the GPU type that computed them (prep, A100-80GB). Prices only: no model is loaded."""
    t0 = time.time()
    from vpd_audit_2 import pilot_b, prices

    env_rec = _environment()
    C = prices.constants()
    tuples = prices.tuple_sets(1024)["W16_K256"]
    assert prices.sha256_array(tuples) == tuples_sha, "not the committed deciding tuples"
    S_Q = np.load(Path(CACHE) / "prices" / "Q_fp32_S.npy")
    out = pilot_b.q_stored_path_check(Path(CACHE), S_Q, tuples, C, q_text_ids, q_free, {int(k): v for k, v in expected.items()},
                                      ids_sha256=q_ids_sha256)
    return {**out, "environment": env_rec, "function_seconds": time.time() - t0}


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=1800, memory=32768)
def part_b_check_gpu(ids: np.ndarray, sha512: list[str], start: dict, lay: list, stored: dict, rows: list[int]) -> dict:
    t0 = time.time()
    from vpd_audit_2 import pilot_b

    assert _sha_rows(ids) == sha512
    model, _ = _load_model()
    env_rec = _env_check()
    out = pilot_b.original_arm_check(model, ids, VOL_CQ, start, [tuple(x) for x in lay], stored, rows, s=1, n=20)
    return {**out, "environment": env_rec, "function_seconds": time.time() - t0}


def _pinned(stage: str, gpu: str, fixed: str) -> None:
    """A stage whose GPU type is fixed by its design refuses any other `--gpu` rather than ignoring it."""
    if gpu != fixed:
        raise ValueError(f"stage {stage} runs on {fixed} by design; --gpu {gpu} was given")


@app.local_entrypoint()
def part_b(gpu: str, stage: str = "prep", n_per: int = 20) -> None:
    """`--gpu` is required, with no default (plan 7, item 7): no stage takes a GPU type silently.

    stage prep: CQ's labels and prices, the price-path test, version (ii)'s reference check, G3's controls, B3's timings;
    A100-80GB by design. stage n8: [N8], the other GPU type's step time; B200 by design. stage b1: B1 on `--gpu`.
    stage b2: B2 with n_per removals per stratum, on `--gpu`. stage check: report 3's check of the harness's original arm
    against the plain loop, partition 1's first set, seed 1; `--gpu` must be the GPU type B1 recorded (reads only the
    original arm's stored values from the sealed file). stage qprice: plan 7, item 8's test, Q texts 0 and 1 from the stored
    path against the pilot's stored-path values; A100-80GB, where those were computed."""
    from vpd_audit_2 import pilot as P
    from vpd_audit_2.manifest import load_start

    for d in (PART_B, PART_B / "sealed", CQ_PRICES):
        d.mkdir(parents=True, exist_ok=True)
    ids, texts, sha = _cq()
    print(f"[local] app {app.app_id}; GPU {gpu}")
    if stage == "prep":
        _pinned(stage, gpu, "A100-80GB")
        pr = json.load(open(REPO_ROOT / "results" / "s4_plan1_prices" / "prices.json"))
        g3r = json.load(open(REPO_ROOT / "results" / "s4_plan1_g3" / "g3.json"))
        assert g3r["texts"] == texts
        res = part_b_prep_gpu.remote(ids, sha, texts, [0, 1], g3r["controls"], load_start(1), pr["companions_file"]["arrays_sha256"]["W16_K256"],
                                     _q_free([0, 1]))
        T = res.pop("T")
        with open(CQ_PRICES / "T_per_arm.json", "w") as f:
            json.dump(T, f, indent=1)
        b3 = res.pop("b3")
        with open(PART_B / "b3_timings.json", "w") as f:
            json.dump({**b3, "environment": res["environment"]}, f, indent=1)
        with open(CQ_PRICES / "prep.json", "w") as f:
            json.dump({k: res[k] for k in ("cq_cache", "nominal", "prices_cq", "price_path_test", "environment", "function_seconds")}, f, indent=1)
        from vpd_audit_2 import pilot_b
        prereq, sealed = pilot_b.seal_prerequisites(
            {k: res[k] for k in ("v2_reference_check", "v2_precision_gap_original_arm", "g3_controls_reproduced", "environment")},
            {"arm": "nominal", "text": texts[0], "cq_row": 0, "seed": 1})
        with open(PART_B / "sealed" / pilot_b.SEALED_PREREQ, "w") as f:
            json.dump(sealed, f, indent=1)
        with open(PART_B / "prerequisites.json", "w") as f:
            json.dump(prereq, f, indent=1)
        print(f"[local] CQ cache: dense equals prepare labels {res['cq_cache']['dense_equals_prepare_labels']}; nominal {res['nominal']['total']}")
        print(f"[local] price-path test: {res['price_path_test']['passes']}; version (ii) reference check: {res['v2_reference_check']['passes']}; "
              f"G3 controls reproduced: {res['g3_controls_reproduced']['passes']}")
        print(f"[local] B3: {json.dumps({k: v for k, v in b3.items() if k != 'b3_3_float64'})}")
        return
    if stage == "n8":
        _pinned(stage, gpu, "B200")
        res = part_b_n8_gpu.remote(ids, sha, load_start(1))
        b3 = json.load(open(PART_B / "b3_timings.json"))
        b3["n8_B200"] = res
        with open(PART_B / "b3_timings.json", "w") as f:
            json.dump(b3, f, indent=1)
        print(f"[local] N8: A100-80GB {b3['n8']['seconds_per_step']:.3f} s per step; B200 {res['seconds_per_step']:.3f} s per step")
        return
    if stage == "b1":
        prereq = json.load(open(PART_B / "prerequisites.json"))
        prep = json.load(open(CQ_PRICES / "prep.json"))
        assert prereq["v2_reference_check"]["passes"] and prep["price_path_test"]["passes"], "B1 waits on its prerequisites"
        parts = _partitions()
        starts = {s: P.load_extended_start(s) for s in P.PILOT_STARTS}
        lay = P.layout()
        t0 = time.time()
        calls = {p: part_b_partition_gpu.with_options(gpu=gpu).spawn(ids, sha, p, [sets["set0"], sets["set1"]], starts, lay) for p, sets in parts.items()}
        v2 = part_b_v2_gpu.with_options(gpu=gpu).spawn(ids, sha, texts)
        raw = {"partitions": {}, "partition_definition": parts, "gpu": gpu}
        meta = {"containers": {}}
        for p, c in calls.items():
            r = c.get()
            raw["partitions"][p] = r["result"]
            meta["containers"][f"partition{p}"] = {"environment": r["environment"], "function_seconds": r["function_seconds"]}
            print(f"[local] partition {p} done after {time.time() - t0:.0f} s")
        r = v2.get()
        raw["v2"], raw["stochastic"] = r["result"]["v2"], r["result"]["stochastic"]
        meta["containers"]["v2_stochastic"] = {"environment": r["environment"], "function_seconds": r["function_seconds"],
                                               "v2_seconds": r["result"]["v2_seconds"], "stochastic_seconds": r["result"]["stochastic_seconds"]}
        meta["search_seconds"] = {p: {f"{sk}|{k}": t for sk in ("set0", "set1") for k, t in v[sk]["search_seconds"].items()}
                                  for p, v in raw["partitions"].items()}
        meta["app_id"] = app.app_id
        with open(PART_B / "sealed" / "b1_raw.json", "w") as f:
            json.dump(raw, f)
        with open(PART_B / "b1_runs.json", "w") as f:
            json.dump(meta, f, indent=1)
        print(f"[local] B1 written (sealed) after {time.time() - t0:.0f} s")
        return
    if stage == "b2":
        with np.load(PART_A / "strata.npz") as z:
            alive = z["stratum"] != 10
        mods = sorted(json.load(open(PART_A / "strata.json"))["module_to_c"])
        strata = {flag: [[flag, k, d, b] for k in mods for d in range(10) for b in range(4)] for flag in (1, 0)}
        t0 = time.time()
        calls = {flag: part_b_b2_gpu.with_options(gpu=gpu).spawn(ids, sha, texts, alive, st, n_per) for flag, st in strata.items()}
        out = {"n_per_stratum": n_per, "gpu": gpu, "triples": {}, "effects": {}, "containers": {}}
        for flag, c in calls.items():
            r = c.get()
            out["triples"].update(r["triples"])
            out["effects"].update(r["effects"])
            out["containers"]["alive" if flag else "dead"] = {"environment": r["environment"], "function_seconds": r["function_seconds"],
                                                              "seconds": r["seconds"], "weight_norms": r["weight_norms"]}
            print(f"[local] B2 {'alive' if flag else 'dead'} strata done after {time.time() - t0:.0f} s")
        out["app_id"] = app.app_id
        with open(PART_B / "b2.json", "w") as f:
            json.dump(out, f)
        return
    if stage == "qprice":
        _pinned(stage, gpu, "A100-80GB")  # where the pilot's stored-path values were computed
        prep = json.load(open(CQ_PRICES / "prep.json"))
        old = {t["q_text"]: t["T_stored"] for t in prep["price_path_test"]["texts"]}
        pr = json.load(open(REPO_ROOT / "results" / "s4_plan1_prices" / "prices.json"))
        from vpd_audit_2.manifest import pool_ids

        q_ids, q_texts, _ = pool_ids("Q")  # the ids' hash proves Q's cache rows are the manifest's texts in order
        assert q_texts == _q_free(sorted(old))
        q_sha = hashlib.sha256(np.ascontiguousarray(q_ids, dtype=np.int32).tobytes()).hexdigest()
        res = part_b_qprice_gpu.remote(q_texts, sorted(old), pr["companions_file"]["arrays_sha256"]["W16_K256"], old, q_sha)
        res["app_id"] = app.app_id
        with open(CQ_PRICES / "q_stored_path_check.json", "w") as f:
            json.dump(res, f, indent=1)
        print(f"[local] Q texts from the stored path: passes {res['passes']}; "
              + "; ".join(f"text {t['q_text']}: equals the pilot's {t['equals_expected']}, Delta full = sub-cache {t['delta_full_equals_sub_cache']}"
                          for t in res["texts"]))
        return
    if stage == "check":
        rows = _partitions()["1"]["set0"]
        raw = json.load(open(PART_B / "sealed" / "b1_raw.json"))
        _pinned(stage, gpu, raw["gpu"])  # the check is bitwise only on B1's GPU type
        d = raw["partitions"]["1"]["set0"]
        assert d["texts"] == rows
        stored = {"harm": {f"n{m}": d["harm"][f"original|s1|n{m}"] for m in (20, 40, 80)}, "record": d["records"]["original|s1"]}
        del raw, d
        res = part_b_check_gpu.with_options(gpu=gpu).remote(ids, sha, P.load_extended_start(1), P.layout(), stored, rows)
        res["app_id"] = app.app_id
        with open(PART_B / "original_arm_check.json", "w") as f:
            json.dump(res, f, indent=1)
        print(f"[local] check: as stated {res['passes_as_stated']}; given the cache's labels {res['passes_given_cache_labels']}; "
              f"inputs {res['inputs']}; rerun equals B1 {res.get('rerun_equals_b1')}")
        return
    raise ValueError(stage)
