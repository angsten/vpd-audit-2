"""The Modal app for plan 1 of the research log (the earlier plan 3 of the research log, amended by plan 2 of the research log): label prices, gate G3, gate G2,
and the recorded 320-step runs.

The image, the volume `vpd-audit-2-cache`, and the cache paths are plan 1 of the research log's (`modal_app.py`). Token ids are passed in
from the local machine and re-hashed against the manifest's hashes on arrival.

    uv run modal run vpd_audit_2/modal_loop.py::prices      (bf16 labels of Q with z; price check 4; every price column and check)
    uv run modal run vpd_audit_2/modal_loop.py::g3          (gate G3 on CQ, after the prices)
    uv run modal run vpd_audit_2/modal_loop.py::g2          (gate G2 on C1, float32, B200)
    uv run modal run vpd_audit_2/modal_loop.py::recorded    (the three recorded 320-step bf16 runs on C1, and the scoring timings)

Results are written to `results/s4_plan1_{prices,g2,g3}/` by the local entrypoints.
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

app = modal.App("vpd-audit-2-loop", image=image)

PRICES_RESULTS = REPO_ROOT / "results" / "s4_plan1_prices"
G2_RESULTS = REPO_ROOT / "results" / "s4_plan1_g2"
G3_RESULTS = REPO_ROOT / "results" / "s4_plan1_g3"
LABELS_DIR = Path(CACHE) / "labels"
PRICES_DIR = Path(CACHE) / "prices"


def _manifest_sha() -> str:
    from vpd_audit_2.manifest import OUT_DIR as MAN_DIR

    return hashlib.sha256((MAN_DIR / "manifest.json").read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- prices


@app.function(volumes={CACHE: volume}, gpu="A100-40GB", timeout=3600, memory=65536)
def price_labels_gpu(q_ids: np.ndarray, q_sha512: list[str], ws_ids: np.ndarray, ws_sha512: list[str], e_main_sha: dict[str, str],
                     plan2_l0: dict[str, float]) -> dict:
    """Plan 2 of the research log, item 1: Q's bf16 labels with z (A100-40GB, the GPU of plan 2 of the research log's bf16 pass). Item 7: price check 4 on WS_W16
    (A100-40GB, the GPU of plan 2 of the research log's world-size test)."""
    t0 = time.time()
    from vpd_audit_2 import price_inputs

    assert _sha_rows(q_ids) == q_sha512, "Q: the ids received are not the manifest's"
    assert _sha_rows(ws_ids) == ws_sha512, "WS_W16: the ids received are not the manifest's"
    stored = json.load(open(LABELS_DIR / "reproduce" / "E_main.json"))["sha256"]
    assert stored == e_main_sha, "the volume's E_main is not the one plan 2 of the research log recorded"
    model, files = _load_model()
    env_rec = _environment()
    q_hash = hashlib.sha256(np.ascontiguousarray(q_ids, dtype=np.int32).tobytes()).hexdigest()
    out = {"environment": env_rec, "checkpoints": files}
    out["bf16_cache"] = price_inputs.bf16_cache(model, q_ids, LABELS_DIR / "Q_bf16.npz",
                                               {"pool": "Q", "texts": "manifest pool Q: v0 to v1023", "set_hash_ids_512": q_hash, "checkpoints": files,
                                                "code_commit": env_rec["vpd_audit_2_commit"], "code_dirty": env_rec["vpd_audit_2_dirty"], "environment": env_rec},
                                               e_main_sha, log=_log)
    volume.commit()
    out["check4"] = price_inputs.check4(model, ws_ids, plan2_l0, log=_log)
    out["seconds"] = time.time() - t0
    return out


@app.function(volumes={CACHE: volume}, gpu="A100-40GB", timeout=3 * 3600, memory=98304)
def prices_gpu() -> dict:
    """Every price column and check, on the float32 cache (deciding: checks 1 to 9) and the bf16 cache (checks 1, 5, 6)."""
    t0 = time.time()
    import torch

    from vpd_audit_2 import env, prices

    torch.use_deterministic_algorithms(True)  # strict (plan 5 of the research log, item 1)
    out = {"environment": _environment()}
    fp32, tuples = prices.price_cache(LABELS_DIR / "Q_fp32.npz", "Q_fp32", PRICES_DIR, "cuda", env.PROVENANCE_DIR, deciding=True, log=_log)
    volume.commit()
    bf16, tuples_b = prices.price_cache(LABELS_DIR / "Q_bf16.npz", "Q_bf16", PRICES_DIR, "cuda", env.PROVENANCE_DIR, deciding=False, log=_log)
    volume.commit()
    assert all(np.array_equal(tuples[k], tuples_b[k]) for k in tuples)
    out.update({"Q_fp32": fp32, "Q_bf16": bf16, "tuples": {k: v for k, v in tuples.items()}, "seconds": time.time() - t0})
    return out


@app.function(volumes={CACHE: volume}, cpu=4, memory=65536, timeout=3600)
def price_check7_diagnostic() -> dict:
    """Description of check 7's failure from the stored float32 prices and S; no price is recomputed."""
    from vpd_audit_2 import prices

    C = prices.constants()
    cache, meta = prices.load_cache(LABELS_DIR / "Q_fp32.npz")
    e, _ = prices.entries(cache, meta, C)
    S = np.load(PRICES_DIR / "Q_fp32_S.npy")
    with np.load(PRICES_DIR / "Q_fp32_prices.npz") as z:
        new, old = z["price_W16"], z["price_old_formula"]
    return prices.check7_diagnostic(e, S, new, old, C)


@app.local_entrypoint()
def check7_diagnostic() -> None:
    res = price_check7_diagnostic.remote()
    with open(PRICES_RESULTS / "check7_diagnostic.json", "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


@app.function(volumes={CACHE: volume}, gpu="A100-40GB", memory=65536, timeout=3600)
def price_check7_amended(tuples_sha256: str) -> dict:
    """Check 7 as amended (plan 3 of the research log, Section 2), from the stored float32 prices and S; check 3's reference calls
    for 7c on the GPU."""
    import torch

    from vpd_audit_2 import prices

    torch.use_deterministic_algorithms(True)  # strict (plan 5 of the research log, item 1)
    C = prices.constants()
    cache, meta = prices.load_cache(LABELS_DIR / "Q_fp32.npz")
    e, _ = prices.entries(cache, meta, C)
    S = np.load(PRICES_DIR / "Q_fp32_S.npy")
    with np.load(PRICES_DIR / "Q_fp32_prices.npz") as z:
        new, old = z["price_W16"], z["price_old_formula"]
    tuples = prices.tuple_sets(e.n_texts)["W16_K256"]
    assert prices.sha256_array(tuples) == tuples_sha256
    pricer = prices.Pricer(S, tuples, prices.W_RUN, C, "cuda")
    return {**prices.check7_amended(cache, e, S, new, old, pricer, meta, C, device="cuda"), "environment": _environment(),
            "inputs_sha256": {"S": prices.sha256_array(S), "price_W16": prices.sha256_array(new), "price_old_formula": prices.sha256_array(old)}}


@app.local_entrypoint()
def check7_amended() -> None:
    p = json.load(open(PRICES_RESULTS / "prices.json"))
    res = price_check7_amended.remote(p["companions_file"]["arrays_sha256"]["W16_K256"])
    stored = p["Q_fp32"]["files"]["sha256"]
    res["inputs_equal_the_recorded_outputs"] = all(res["inputs_sha256"][k] == stored[k] for k in ("S", "price_W16", "price_old_formula"))
    res["original_check7"] = {k: v for k, v in p["Q_fp32"]["check7"].items() if k != "components_outside"}
    with open(PRICES_RESULTS / "check7_amended.json", "w") as f:
        json.dump(res, f, indent=1)
    print(f"[local] inputs equal the recorded outputs: {res['inputs_equal_the_recorded_outputs']}")
    for k in ("7a", "7b"):
        print(f"[local] {k}: {json.dumps({kk: vv for kk, vv in res[k].items() if kk != 'components_outside'})}")
    print(f"[local] 7c: {json.dumps({g: {kk: vv for kk, vv in d.items() if kk != 'rows'} for g, d in res['7c']['groups'].items()})}")
    print(f"[local] description: {json.dumps(res['description'])}")
    print(f"[local] check 7 as amended passes: {res['passes']}")


def _deterministic_npz(arrays: dict[str, np.ndarray]) -> bytes:
    from vpd_audit_2.manifest import deterministic_npz

    return deterministic_npz(arrays)


def _price_reading(inputs: dict, res: dict) -> dict:
    """Plan 3 of the research log, Section 4: checks 1 to 5 and 7 pass (check 5 on the bf16 cache carries the rule; plan 1 of the research log, item 5)."""
    f, b = res["Q_fp32"], res["Q_bf16"]
    items = {
        "check1_fp32": f["check1"]["passes"], "check1_bf16": b["check1"]["passes"],
        "check2": f["check2"]["passes"], "check3": f["check3"]["passes"], "check4": inputs["check4"]["passes"],
        "check5_bf16": b["check5"]["within_0.2pct"], "check7": f["check7"]["passes"],
        "bf16_label_blocks_equal_E_main": all(inputs["bf16_cache"]["label_blocks_equal_E_main"].values()),
    }
    return {"items": items, "passes": all(items.values()),
            "reported": {"check5_fp32_within_0.2pct": f["check5"]["within_0.2pct"], "check6_gap_above_5pct": f["check6"]["gap_above_5pct"],
                         "check8_passes": f["check8"]["passes"], "check8_K_used": f["check8"]["K_used"],
                         "check9_median_below_0.1pct": f["check9"]["median_below_0.1pct"]},
            "pi_5": f["pi_5"]}


@app.local_entrypoint()
def prices(stage: str = "all") -> None:
    from vpd_audit_2.manifest import pool_ids

    PRICES_RESULTS.mkdir(parents=True, exist_ok=True)
    if stage in ("all", "inputs"):
        q_ids, q_texts, q_sha = pool_ids("Q")
        ws_ids, ws_texts, ws_sha = pool_ids("WS_W16")
        lab = json.load(open(REPO_ROOT / "results" / "plan2_labels" / "labels_gpu.json"))
        e_main_sha = lab["e_reproduction"]["sha256"]
        l0 = json.load(open(REPO_ROOT / "results" / "plan2_world_size" / "metrics.json"))["metrics"]["W16"]["l0"]
        plan2_l0 = {k: v for k, v in l0.items() if k.startswith("h.")}
        assert len(plan2_l0) == 24
        t0 = time.time()
        inputs = price_labels_gpu.remote(q_ids, q_sha, ws_ids, ws_sha, e_main_sha, plan2_l0)
        inputs["local_wall_seconds"] = time.time() - t0
        inputs["pools"] = {"Q": {"n": len(q_texts), "texts": [q_texts[0], q_texts[-1]]}, "WS_W16": {"n": len(ws_texts)}, "manifest_sha256": _manifest_sha()}
        with open(PRICES_RESULTS / "price_inputs.json", "w") as f:
            json.dump(inputs, f, indent=1, default=str)
        bc, c4 = inputs["bf16_cache"], inputs["check4"]
        print(f"[local] bf16 cache: label blocks equal E_main {bc['label_blocks_equal_E_main']}; {bc['mean_count_above_0_per_position']:.4f} per position")
        print(f"[local] check 4: bf16 whole {c4['bf16']['whole_batch_world_size_1']:.4f} ({c4['bf16']['relative_difference_whole']:+.5f}), "
              f"per-process {c4['bf16']['per_process_16_shares_of_8']:.4f} ({c4['bf16']['relative_difference_per_process']:+.5f}); "
              f"L0 tie {c4['bf16']['l0_tie']['passes']} (exact {c4['bf16']['l0_tie']['all_24_equal_exactly']}); passes {c4['passes']}")
        if not (all(bc["label_blocks_equal_E_main"].values()) and c4["passes"]):
            print("[local] STOP: the bf16 cache or check 4 failed")
            return
    if stage in ("all", "prices"):
        inputs = json.load(open(PRICES_RESULTS / "price_inputs.json"))
        t0 = time.time()
        res = prices_gpu.remote()
        res["local_wall_seconds"] = time.time() - t0
        tuples = {k: np.asarray(v) for k, v in res.pop("tuples").items()}
        npz = _deterministic_npz(tuples)
        (PRICES_RESULTS / "companions.npz").write_bytes(npz)
        res["companions_file"] = {"file": "companions.npz", "sha256": hashlib.sha256(npz).hexdigest(),
                                  "arrays_sha256": {k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest() for k, v in tuples.items()},
                                  "seeds": {"W16": "(master, 'price-companions', 16)", "W1": "(master, 'price-companions', 1)"}}
        res["reading"] = _price_reading(inputs, res)
        with open(PRICES_RESULTS / "prices.json", "w") as f:
            json.dump(res, f, indent=1, default=str)
        r = res["reading"]
        print(f"[local] prices: {json.dumps(r['items'])}")
        print(f"[local] reported: {json.dumps(r['reported'])}; pi_5 {r['pi_5']:.6g}; passes {r['passes']}")


# ----------------------------------------------------------------------------- G3


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=2 * 3600, memory=98304)
def g3_gpu(ids: np.ndarray, sha512: list[str], text_ids: list[str], line: float) -> dict:
    t0 = time.time()
    from vpd_audit_2 import g3

    assert _sha_rows(ids) == sha512, "CQ: the ids received are not the manifest's"
    model, files = _load_model()
    out = g3.run_g3(model, ids, text_ids, line, log=_log)
    if not out["backgrounds"]["all_on"]["below_line"]:
        _log("[g3] all-on fails in float32: rerunning it with float64 forward passes")
        out["all_on_float64"] = g3.run_all_on_float64(model, ids, line)
    out.update({"environment": _environment(), "checkpoints": files, "function_seconds": time.time() - t0})
    return out


@app.local_entrypoint()
def g3() -> None:
    from vpd_audit_2.manifest import pool_ids

    G3_RESULTS.mkdir(parents=True, exist_ok=True)
    pr = json.load(open(PRICES_RESULTS / "prices.json"))
    c7 = json.load(open(PRICES_RESULTS / "check7_amended.json"))
    assert pr["reading"]["items"]["check7"] is False and c7["passes"], "G3 runs only after the prices pass (check 7 as amended)"
    pi5 = pr["Q_fp32"]["pi_5"]
    ids, texts, sha = pool_ids("CQ")
    t0 = time.time()
    out = g3_gpu.remote(ids, sha, texts, pi5 / 100)
    out["local_wall_seconds"] = time.time() - t0
    out["pi_5"] = pi5
    out["pool"] = {"name": "CQ", "n": len(texts), "manifest_sha256": _manifest_sha()}
    with open(G3_RESULTS / "g3.json", "w") as f:
        json.dump(out, f, indent=1)
    for bg, v in out["backgrounds"].items():
        p = v["position0_summed_null"]
        print(f"[local] {bg} ({'gating' if v['gating'] else 'recorded'}): p99 |summed null| {p['p99_abs']:.3e}, max {p['max_abs']:.3e}, "
              f"line {v['line']:.3e}; below {v['below_line']}; base KL {v['base_kl_mean_nats']:.4g}")
    for bg, v in out["controls"]["backgrounds"].items():
        print(f"[local] control on {bg}: max |difference| {v['max_abs_difference']:.3e} against the floor {v['floor']:.3e}; all within {v['all_within_floor']}")
    if "all_on_float64" in out:
        print(f"[local] all-on in float64: {out['all_on_float64']['position0_summed_null']['p99_abs']:.3e}")
    print(f"[local] G3 passes: {out['passes']}")


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=2 * 3600, memory=98304)
def g3_float64_gpu(ids: np.ndarray, sha512: list[str], text_ids: list[str], line: float) -> dict:
    t0 = time.time()
    from vpd_audit_2 import g3

    assert _sha_rows(ids) == sha512, "CQ: the ids received are not the manifest's"
    model, files = _load_model()
    out = g3.run_float64_diagnostic(model, ids, text_ids, line, log=_log)
    out.update({"environment": _environment(), "checkpoints": files, "function_seconds": time.time() - t0})
    return out


@app.local_entrypoint()
def g3_float64() -> None:
    """The diagnostic of report 1 of the research log on plan 3 of the research log, follow-up 1: at labels and stochastic with float64 forward passes."""
    from vpd_audit_2.manifest import pool_ids

    g3r = json.load(open(G3_RESULTS / "g3.json"))
    ids, texts, sha = pool_ids("CQ")
    assert texts == g3r["texts"], "not G3's texts"
    t0 = time.time()
    out = g3_float64_gpu.remote(ids, sha, texts, g3r["line_pi5_over_100"])
    out["local_wall_seconds"] = time.time() - t0
    out["float32_floors_from_g3"] = {bg: g3r["backgrounds"][bg]["position0_summed_null"]["p99_abs"] for bg in out["float64"]}
    out["pool"] = {"name": "CQ", "n": len(texts), "manifest_sha256": _manifest_sha()}
    with open(G3_RESULTS / "g3_float64_diagnostic.json", "w") as f:
        json.dump(out, f, indent=1)
    for bg, v in out["float64"].items():
        p = v["position0_summed_null"]
        print(f"[local] {bg}: float64 p99 |summed null| {p['p99_abs']:.3e} (max {p['max_abs']:.3e}) against float32 {out['float32_floors_from_g3'][bg]:.3e}; "
              f"line {v['line']:.3e}; base KL {v['base_kl_mean_nats']:.6g} (float32 {g3r['backgrounds'][bg]['base_kl_mean_nats']:.6g})")
        print(f"[local] {bg}: per position {json.dumps(v['per_position'])}")
        print(f"[local] {bg}: float64 pass of 32 texts {v['timing']['grouping_32_pass_seconds']:.3f} s, one text {v['timing']['grouping_1_seconds_per_pass']:.3f} s; "
              f"float32 pass of 32 {out['float32_timing'][bg]['grouping_32_pass_seconds']:.3f} s, 32 single passes {out['float32_timing'][bg]['grouping_1_all_32_passes_seconds']:.3f} s")


# ----------------------------------------------------------------------------- G2


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=3 * 3600, memory=131072)
def g2_gpu(ids: np.ndarray, sha512: list[str], text_ids: list[str], start: dict[str, np.ndarray]) -> dict:
    """G2 on all 128 texts of C1; on an out-of-memory error, on its first 32 texts (plan 2 of the research log, item 8)."""
    t0 = time.time()
    import torch

    from vpd_audit_2 import g2

    assert _sha_rows(ids) == sha512, "C1: the ids received are not the manifest's"
    model, files = _load_model()
    torch.cuda.reset_peak_memory_stats()
    draw_path = Path(CACHE) / "g2" / "draw_C1_first4_s1_d0.npz"
    try:
        out = g2.protocol(model, ids, text_ids, start, draw_path=draw_path, log=_log)
        out["batch"] = "C1, all 128 texts"
    except torch.OutOfMemoryError as e:
        _log(f"[g2] out of memory on 128 texts: {str(e)[:200]}; rerunning on the first 32")
        torch.cuda.empty_cache()
        out = g2.protocol(model, ids[:32], text_ids[:32], start, draw_path=draw_path, log=_log)
        out["batch"] = "C1, first 32 texts (out of memory on 128)"
        out["out_of_memory_on_128"] = str(e)[:400]
    volume.commit()
    out.update({"peak_memory_gib": torch.cuda.max_memory_allocated() / 2**30, "environment": _environment(), "checkpoints": files,
                "function_seconds": time.time() - t0})
    return out


@app.local_entrypoint()
def g2() -> None:
    from vpd_audit_2.manifest import load_start, pool_ids

    G2_RESULTS.mkdir(parents=True, exist_ok=True)
    ids, texts, sha = pool_ids("C1")
    t0 = time.time()
    out = g2_gpu.remote(ids, sha, texts, load_start(1))
    out["local_wall_seconds"] = time.time() - t0
    g1 = json.load(open(REPO_ROOT / "results" / "plan2_g1" / "trajectories.json"))["runs"]
    out["precision_gap"] = {"G1_bf16_20_step_harm": g1["A_c|C1|320"]["record"][20], "G1_float32_20_step_record": g1["A_c|C1|20|fp32"]["record"],
                            "authors_float32_20_step_harm_here": out["records"]["authors_record"][20],
                            "authors_float32_record_equals_G1_float32_record": out["records"]["authors_record"] == g1["A_c|C1|20|fp32"]["record"]}
    out["pool"] = {"name": "C1", "n": len(texts), "start_seed_key": [20261001, "start", 1], "manifest_sha256": _manifest_sha()}
    with open(G2_RESULTS / "g2.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"[local] batch: {out['batch']}; criterion {out['criterion']['name']}; peak {out['peak_memory_gib']:.1f} GiB")
    for k in ("step1", "step2", "step3", "frozen_at_1", "identity", "micro_batch_validation", "stochastic_routing_2_4", "saved_draw_reload"):
        print(f"[local] {k}: {out[k]['passes']}")
    print(f"[local] per-entry gradients bitwise: {out['per_entry_gradients']}")
    print(f"[local] micro-batch differing entries per step: { {m: v['n_differing_per_step'] for m, v in out['micro_batch_validation']['sizes'].items()} }; "
          f"largest ratio { {m: v['largest_ratio'] for m, v in out['micro_batch_validation']['sizes'].items()} }")
    print(f"[local] precision gap: {json.dumps({k: v for k, v in out['precision_gap'].items() if k != 'G1_float32_20_step_record'})}")
    print(f"[local] G2 passes: {out['passes']}")


# ----------------------------------------------------------------------------- the recorded 320-step runs


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=3 * 3600, memory=131072)
def recorded_gpu(ids: np.ndarray, sha512: list[str], start: dict[str, np.ndarray], sizes: list[int], tag: str) -> dict:
    t0 = time.time()
    from vpd_audit_2 import recorded

    assert _sha_rows(ids) == sha512, "C1: the ids received are not the manifest's"
    model, files = _load_model()
    out = recorded.runs(model, ids, start, tuple(sizes), Path(CACHE) / "s4_recorded", tag, log=_log)
    volume.commit()
    out.update({"environment": _environment(), "checkpoints": files, "function_seconds": time.time() - t0, "tag": tag})
    return out


@app.local_entrypoint()
def recorded() -> None:
    from vpd_audit_2 import recorded as R
    from vpd_audit_2.manifest import load_start, pool_ids

    g2r = json.load(open(G2_RESULTS / "g2.json"))
    assert g2r["passes"], "the recorded runs use our loop, which counts only once G2 passes"
    ids, texts, sha = pool_ids("C1")
    start = load_start(1)
    calls = {"B200": recorded_gpu.spawn(ids, sha, start, [8, 16], "B200"),
             "A100-80GB": recorded_gpu.with_options(gpu="A100-80GB").spawn(ids, sha, start, [16], "A100-80GB")}
    res = {k: c.get() for k, c in calls.items()}
    g1 = json.load(open(REPO_ROOT / "results" / "plan2_g1" / "trajectories.json"))["runs"]["A_c|C1|320"]["record"]
    named = {f"ours, {gpu}, micro-batch {m}": r["record"] for gpu, v in res.items() for m, r in v["runs"].items()}
    out = {"containers": res, "readings": R.readings(named, g1), "G1_run": "A_c|C1|320 (results/plan2_g1/trajectories.json)",
           "pool": {"name": "C1", "n": len(texts), "start_seed_key": [20261001, "start", 1], "manifest_sha256": _manifest_sha()}}
    with open(G2_RESULTS / "recorded_320.json", "w") as f:
        json.dump(out, f, indent=1)
    rd = out["readings"]
    for name, h in rd["harm"].items():
        print(f"[local] {name}: " + ", ".join(f"{k}: {v:.4g}" for k, v in h.items()) + f"; first above 5 nats: {rd['first_step_above_5_nats'][name]}")
    print(f"[local] first step differing from G1 by 1 percent: {rd['first_step_differing_from_G1_by_1pct']}")
    print(f"[local] pairs: {rd['pairs']}")
    for gpu, v in res.items():
        print(f"[local] {gpu} ({v['environment']['gpu']}): " + "; ".join(f"mb{m} {r['seconds_per_step']:.3f} s per step, hook {r['save_hook_events']}" for m, r in v["runs"].items()))
        print(f"[local] {gpu} scoring: {json.dumps({k: s.get('mean_seconds_of_5', s.get('out_of_memory', '')[:60]) for k, s in v['scoring'].items()})}; "
              f"labels and target {v['labels_target_seconds']['mean_of_5']:.3f} s")


# ----------------------------------------------------------------------------- plan 4 of the research log: why our 320-step runs end higher

PLAN4_RESULTS = REPO_ROOT / "results" / "s4_plan4"


@app.function(volumes={CACHE: volume}, gpu="B200", timeout=2 * 3600, memory=131072)
def diag_gpu(task: dict) -> dict:
    """One task of plan 4 of the research log on a B200: 'd1', 'd2', or 'cell' (one or two 320-step runs on a possibly permuted batch)."""
    t0 = time.time()
    import torch

    from vpd_audit_2 import diagnose as D

    assert _sha_rows(task["ids"]) == task["sha512"], f"{task['name']}: the ids received are not the manifest's"
    model, files = _load_model()
    torch.cuda.reset_peak_memory_stats()
    out: dict = {"name": task["name"]}
    if task["kind"] == "d1":
        out["d1"] = D.d1(model, task["ids"], task["start"], task["g1_record"], task["g1_sha"], log=_log)
    elif task["kind"] == "d2":
        with np.load(Path(CACHE) / "s4_recorded" / "B200_mb8.npz") as z:
            saved = {k.split("|", 1)[1]: z[k] for k in z.files if k.startswith("saved|")}
        out["d2"] = D.d2(model, task["ids"], saved, log=_log)
    else:
        out["runs"] = {}
        for loop in task["loops"]:
            r = D.run_cell(model, task["ids"], task["start"], authors=(loop == "authors"), micro_batch=None if loop == "authors" else 8,
                           log=_log, tag=f"{task['name']} {loop}")
            out["runs"][loop] = r
    out.update({"peak_memory_gib": torch.cuda.max_memory_allocated() / 2**30, "environment": _environment(), "checkpoints": files,
                "function_seconds": time.time() - t0})
    return out


@app.function(volumes={CACHE: volume}, gpu="A100-80GB", timeout=3600, memory=98304)
def d5_gpu(ids: np.ndarray, sha512: list[str], text_ids: list[str]) -> dict:
    t0 = time.time()
    from vpd_audit_2 import g3

    assert _sha_rows(ids) == sha512, "CQ: the ids received are not the manifest's"
    model, files = _load_model()
    out = g3.float64_oddity(model, ids, text_ids, log=_log)
    out.update({"environment": _environment(), "checkpoints": files, "function_seconds": time.time() - t0})
    return out


def _cell_task(name: str, batch: str, start: int, loops: list[str], perm_k: int | None = None) -> dict:
    from vpd_audit_2.manifest import load_start, perm, pool_ids

    ids, texts, sha = pool_ids(batch)
    task = {"kind": "cell", "name": name, "batch": batch, "start_index": start, "start": load_start(start), "loops": loops}
    if perm_k is not None:
        p = perm(len(texts), "permute", perm_k)
        ids, texts, sha = ids[p], [texts[i] for i in p], [sha[i] for i in p]
        task.update({"permutation_key": [20261001, "permute", perm_k], "permutation": [int(i) for i in p]})
    task.update({"ids": np.ascontiguousarray(ids), "sha512": sha, "texts": texts})
    return task


@app.local_entrypoint()
def diagnose(stage: str = "d1") -> None:
    """stage d1: D1, which must be bitwise before anything else runs. stage d234: D2, D3, and D4 in parallel. stage d5: D5."""
    from vpd_audit_2 import diagnose as D
    from vpd_audit_2.manifest import load_start, pool_ids

    PLAN4_RESULTS.mkdir(parents=True, exist_ok=True)
    g1 = json.load(open(REPO_ROOT / "results" / "plan2_g1" / "trajectories.json"))["runs"]
    if stage == "d1":
        ids, texts, sha = pool_ids("C1")
        task = {"kind": "d1", "name": "D1", "ids": ids, "sha512": sha, "start": load_start(1), "g1_record": g1["A_c|C1|320"]["record"],
                "g1_sha": g1["A_c|C1|320"]["sources_sha256"]}
        t0 = time.time()
        res = diag_gpu.remote(task)
        res["local_wall_seconds"] = time.time() - t0
        res["pool"] = {"name": "C1", "start_seed_key": [20261001, "start", 1], "manifest_sha256": _manifest_sha()}
        with open(PLAN4_RESULTS / "d1.json", "w") as f:
            json.dump(res, f, indent=1)
        d = res["d1"]
        print(f"[local] D1: {json.dumps({k: v for k, v in d.items() if k not in ('authors_record', 'ours_record', 'seconds')})}")
        print(f"[local] D1 bitwise: {d['bitwise']}; peak {res['peak_memory_gib']:.1f} GiB")
        return
    if stage == "d234":
        d1r = json.load(open(PLAN4_RESULTS / "d1.json"))
        assert d1r["d1"]["bitwise"], "D1 is not bitwise: D3 and D4 wait"
        ids, texts, sha = pool_ids("C1")
        tasks = {"D2": {"kind": "d2", "name": "D2", "ids": ids, "sha512": sha}}
        tasks.update({f"D3|C{j}": _cell_task(f"D3|C{j}", f"C{j}", j, ["ours"]) for j in range(2, 9)})
        tasks.update({f"D4|perm{k}": _cell_task(f"D4|perm{k}", "C1", 1, ["authors", "ours"], perm_k=k) for k in range(1, 9)})
        t0 = time.time()
        calls = {name: diag_gpu.spawn(t) for name, t in tasks.items()}
        res = {}
        for name, c in calls.items():
            res[name] = c.get()
            print(f"[local] {name} done after {time.time() - t0:.0f} s")
        d2 = {**res["D2"]["d2"], "environment": res["D2"]["environment"], "function_seconds": res["D2"]["function_seconds"], "peak_memory_gib": res["D2"]["peak_memory_gib"]}
        with open(PLAN4_RESULTS / "d2.json", "w") as f:
            json.dump(d2, f, indent=1)
        ours3 = {j: res[f"D3|C{j}"]["runs"]["ours"]["record"] for j in range(2, 9)}
        g13 = {j: g1[f"A_c|C{j}|320"]["record"] for j in range(2, 9)}
        rec = json.load(open(G2_RESULTS / "recorded_320.json"))
        c1_ours = rec["containers"]["B200"]["runs"]["8"]["record"]
        d3 = {"reading": D.d3_reading(ours3, g13), "C1_reported_not_counted": {"ours_micro8_B200_plateau": D.plateau(c1_ours), "G1_plateau": D.plateau(g1["A_c|C1|320"]["record"])},
              "records": {f"C{j}": ours3[j] for j in ours3},
              "containers": {f"C{j}": {k: v for k, v in res[f"D3|C{j}"].items() if k != "runs"} | {"seconds": res[f"D3|C{j}"]["runs"]["ours"]["seconds"]} for j in range(2, 9)}}
        with open(PLAN4_RESULTS / "d3.json", "w") as f:
            json.dump(d3, f, indent=1)
        authors = [{**res[f"D4|perm{k}"]["runs"]["authors"], "source_record_to_40": np.asarray(res[f"D4|perm{k}"]["runs"]["authors"]["source_record_to_40"])} for k in range(1, 9)]
        ours4 = [res[f"D4|perm{k}"]["runs"]["ours"] for k in range(1, 9)]
        d4 = {"reading": D.d4_reading(authors, ours4), "permutation_keys": [[20261001, "permute", k] for k in range(1, 9)],
              "records": {f"perm{k}": {"authors": authors[k - 1]["record"], "ours_micro8": ours4[k - 1]["record"]} for k in range(1, 9)},
              "final_sources_sha256": {f"perm{k}": {"authors": authors[k - 1]["final_sources_sha256"], "ours": ours4[k - 1]["final_sources_sha256"]} for k in range(1, 9)},
              "seconds": {f"perm{k}": {"authors": authors[k - 1]["seconds"], "ours": ours4[k - 1]["seconds"]} for k in range(1, 9)},
              "G1_C1_plateau": D.plateau(g1["A_c|C1|320"]["record"]), "recorded_runs_plateaus": {f"{g} mb{m}": D.plateau(r["record"]) for g, v in rec["containers"].items() for m, r in v["runs"].items()},
              "environments": {f"perm{k}": res[f"D4|perm{k}"]["environment"] for k in range(1, 9)}}
        with open(PLAN4_RESULTS / "d4.json", "w") as f:
            json.dump(d4, f, indent=1)
        r3, r4 = d3["reading"], d4["reading"]
        print(f"[local] D3: ours above G1 in {r3['count_ours_above_G1']} of 7 cells (p {r3['one_sided_sign_test_p']:.4f}): {r3['reading']}")
        print(f"[local] D3 plateaus: {json.dumps(r3['plateau'])}")
        print(f"[local] D4: Mann-Whitney p {r4['mann_whitney_exact_one_sided_p']:.4f}, medians {r4['medians']}: {r4['reading']}; void {r4['void']}")
        print(f"[local] D4 ranges: {json.dumps(r4['ranges'])}")
        for s, row in d2["per_step"].items():
            print(f"[local] D2 step {s}: " + "; ".join(f"{n} {row[n]['fraction_differing_nonzero_ref']:.4f} / {row[n]['fraction_differing_above_module_median']:.4f}"
                                                        for n in ("bf16_whole", "bf16_micro8", "bf16_micro16")))
        return
    if stage == "d4void":
        d4 = json.load(open(PLAN4_RESULTS / "d4.json"))
        distinct = {v["authors"] for v in d4["final_sources_sha256"].values()}
        assert distinct == {g1["A_c|C1|320"]["sources_sha256"]}, "the permutations did perturb the authors' loop: no void case"
        tasks, infos = {}, {}
        for k in range(1, 9):
            t = _cell_task(f"D4void|start1+ulp{k}", "C1", 1, ["authors"])
            t["start"], infos[k] = D.perturbed_start(t["start"], k)
            tasks[k] = t
        t0 = time.time()
        calls = {k: diag_gpu.spawn(t) for k, t in tasks.items()}
        res = {k: c.get() for k, c in calls.items()}
        print(f"[local] void-case runs done after {time.time() - t0:.0f} s")
        authors = [{**res[k]["runs"]["authors"], "source_record_to_40": np.asarray(res[k]["runs"]["authors"]["source_record_to_40"])} for k in range(1, 9)]
        ours4 = [{"record": d4["records"][f"perm{k}"]["ours_micro8"], "plateau": D.plateau(d4["records"][f"perm{k}"]["ours_micro8"]),
                  "final_sources_sha256": d4["final_sources_sha256"][f"perm{k}"]["ours"]} for k in range(1, 9)]
        reading = D.d4_reading(authors, ours4)
        out = {"reading": reading, "perturbations": {str(k): infos[k] for k in infos},
               "records": {f"start1+ulp{k}": authors[k - 1]["record"] for k in range(1, 9)},
               "final_sources_sha256": {f"start1+ulp{k}": authors[k - 1]["final_sources_sha256"] for k in range(1, 9)},
               "G1_final_sources_sha256": g1["A_c|C1|320"]["sources_sha256"], "seconds": {str(k): authors[k - 1]["seconds"] for k in range(1, 9)},
               "environments": {str(k): res[k]["environment"] for k in range(1, 9)},
               "note": "the authors'-loop group of D4's void case, against D4's eight micro-batch-8 permutation runs"}
        with open(PLAN4_RESULTS / "d4_void_case.json", "w") as f:
            json.dump(out, f, indent=1)
        r = reading
        print(f"[local] D4 void case: Mann-Whitney p {r['mann_whitney_exact_one_sided_p']:.4f}, medians {r['medians']}: {r['reading']}")
        print(f"[local] D4 void case: authors' distinct final sources {r['authors_distinct_final_sources']}; plateaus {r['plateaus']['authors_whole_batch']}")
        print(f"[local] D4 void case ranges: {json.dumps(r['ranges'])}")
        return
    if stage == "d5":
        g3r = json.load(open(G3_RESULTS / "g3.json"))
        ids, texts, sha = pool_ids("CQ")
        assert texts == g3r["texts"]
        res = d5_gpu.remote(ids, sha, texts)
        with open(PLAN4_RESULTS / "d5.json", "w") as f:
            json.dump(res, f, indent=1)
        for bg, v in res["backgrounds"].items():
            for r in v["top_positions"]:
                first = r["first_module_over_1e-12"]
                print(f"[local] D5 {bg} {r['text_id']} pos {r['position']}: e {r['e']:.3e}, max |d| {r['max_abs_d']:.3e}; first module over 1e-12: "
                      f"{first['module'] if first else None}; norms vs float64 formula: {max(x['max_relative_difference_from_float64_formula'] for x in r['rms_norms'].values()):.2e}")
