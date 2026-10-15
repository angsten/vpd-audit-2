"""Plan 1, section 6: the smoke test, on the GPU. Called by `modal_app.smoke`; nothing here runs an adversary.

Texts: the first post's recipients E (rows 0 to 1,023 of the `val` stream) for checks 5a to 5e, E rows 0 to 63
for the minimality readings, and E rows 0 to 127 for the stochastic readings. The donors D_unif (rows 1,024 to
2,047) are loaded and hashed only.

Check 5 (the decomposition on E, sub-batches of 64, the earlier project's own conditions and code):
  a. every mask at 1 with the delta components on (`unmasked_delta`), in float32 and in bf16 autocast;
  b. every mask at its label, the first post's delta treatment (`importances`, delta excluded), bf16 autocast;
  c. the same pass again, labels recomputed, compared bit for bit;
  d. labels per position above 0 and above 0.1 (the lower-leaky output, as the masks use it), bf16 and float32;
  e. every component mask and every delta mask at 0 (`zero_all`, delta excluded), bf16 autocast (the run's
     evaluation precision: `autocast_bf16: true`).
Check 6 (readings of logged values):
  minimality: the authors' `_importance_minimality_loss_update` / `_compute` at p = 0.4 (fraction of training 1.0) on
     the upper-leaky output under bf16 autocast, for {whole batch, 16 per-process shares} x {eps 1e-12, 0} x
     {beta 0.5, 0}; plus one reading the plan does not list: the whole-batch reading on 128 texts, the form the
     logged *evaluation* value takes (sums all-reduced, world size 1);
  stochastic: one draw of the configured uniform-k-subset routing and continuous sources (global seed 0, drawn
     in chunks of 8 texts as each of the run's 16 processes drew for its 8), unrouted matrices at their target
     weights (the code) and at their labels (the alternative), bf16 autocast, delta components on.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any

import numpy as np

SUBBATCH = 64
MASTER_SEED = 0
N_PROCESSES_RELEASED_RUN = 16  # provenance (i): 2 nodes x 8 GPUs
MINIMALITY_TEXTS = 64
STOCHASTIC_TEXTS = 128
EVAL_CHUNK = 8  # texts per process in the run's evaluation batch of 128 over 16 processes
STOCHASTIC_SEED = 0
LOGGED = {
    "paper_train_minimality_line_2224": 1102.0,
    "logged_train_minimality_step_400000": 1110.5545654296875,
    "logged_eval_minimality_step_400000": 1158.31591796875,
    "paper_eval_stochastic_line_2232": 0.2381,
    "logged_eval_stochastic_step_400000": 0.23516137897968292,
}


def _sha_rows(ids: np.ndarray) -> list[str]:
    return [hashlib.sha256(np.ascontiguousarray(r, dtype=np.int32).tobytes()).hexdigest() for r in ids]


def _within_10pct(x: float, target: float) -> bool:
    return abs(x - target) <= 0.1 * abs(target)


def run_smoke(device: str = "cuda", log: Any = print) -> dict[str, Any]:
    import torch

    from vpd_audit_2 import env
    from vpd_audit_2.run_config import CONFIG_SHA256, assert_run_config, load_raw

    from vpd_audit import artifacts
    from vpd_audit import env as vpd_env
    from vpd_audit.data import load_set
    from vpd_audit.importances import ImportanceSums, compute_importances
    from vpd_audit.reference import CONDITION_BY_NAME, evaluate_condition

    torch.use_deterministic_algorithms(True, warn_only=True)
    t_start = time.time()
    out: dict[str, Any] = {"timings_s": {}}
    out["environment"] = {
        "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "cuda": torch.version.cuda,
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "vpd_audit_2_commit": os.environ.get("VPD_AUDIT_2_COMMIT"), "vpd_audit_2_dirty": os.environ.get("VPD_AUDIT_2_DIRTY"),
        "cache_dir": str(env.CACHE_DIR), "vpd_audit_cache_dir": str(vpd_env.CACHE_DIR),
        "cache_inside_submodule": str(vpd_env.CACHE_DIR).startswith(str(env.VPD_AUDIT_DIR)),
    }

    # 2. loading
    t = time.time()
    verified = artifacts.verify_manifest(env.ARTIFACTS_DIR, ["s-55ea3f9b", "t-9d2b8f02"])
    man = artifacts.read_manifest(env.ARTIFACTS_DIR)
    out["artifacts"] = {rel: man["files"][rel] for rel in verified}
    out["checkpoints"] = {"decomposition": artifacts.decomp_checkpoint_path("main").name, "decomposition_step": 400000,
                          "target": artifacts.target_checkpoint_path("main").name, "target_step": 99999}
    fetched_cfg = env.ARTIFACTS_DIR / "s-55ea3f9b" / "final_config.yaml"
    assert_run_config(load_raw(fetched_cfg, CONFIG_SHA256))  # the fetched file is the committed one, byte for byte
    out["fetched_final_config_sha256_equals_committed"] = True
    model = artifacts.load_component_model("main", device)
    out["model"] = {"n_matrices": len(model.components), "n_subcomponents": int(sum(model.module_to_c.values()))}
    weight_deltas = model.calc_weight_deltas()
    out["timings_s"]["load"] = time.time() - t
    log(f"[smoke] loaded {out['checkpoints']} in {out['timings_s']['load']:.0f} s")

    # 4. texts
    ids_E, rows_E, rec_E = load_set("E")
    ids_D, rows_D, rec_D = load_set("D_unif")
    out["texts"] = {
        "E": {"rows": [int(rows_E[0]), int(rows_E[-1])], "sha256_ids": rec_E["sha256_ids"],
              "earlier_project_sha256": "81f8b75b4c31fc95836841062b0c49c4237b3e83dce43397b8ad7e927c18d103"},
        "D_unif": {"rows": [int(rows_D[0]), int(rows_D[-1])], "sha256_ids": rec_D["sha256_ids"],
                   "earlier_project_sha256": "1807c12e26c0baec8065381127ee9b049d22aa85670680e03ea5e9b56ac8ed20"},
    }
    for k in ("E", "D_unif"):
        out["texts"][k]["equal"] = out["texts"][k]["sha256_ids"] == out["texts"][k]["earlier_project_sha256"]
    out["row_hashes"] = {"E": list(zip(rows_E.tolist(), _sha_rows(ids_E))), "D_unif": list(zip(rows_D.tolist(), _sha_rows(ids_D)))}
    out["rows_used"] = {"check_5": [0, 1023], "minimality": [0, MINIMALITY_TEXTS - 1], "stochastic": [0, STOCHASTIC_TEXTS - 1],
                        "loaded_and_hashed_only": [1024, 2047]}

    # 5. the decomposition on E
    N = ids_E.shape[0]
    T = ids_E.shape[1]
    kl: dict[str, np.ndarray] = {}
    label_fp: dict[str, list[str]] = {}  # the earlier harness's on-device fingerprint of the applied masks, per sub-batch
    counts: dict[str, Any] = {}

    def pass_over_E(precision: str, conditions: tuple[str, ...], tag: str) -> None:
        sums = ImportanceSums.empty(model, thresholds=(0.0, 0.1))
        acc = {c: np.empty((N, T), dtype=np.float32) for c in conditions}
        fps: list[str] = []
        t0 = time.time()
        for i, s in enumerate(range(0, N, SUBBATCH)):
            batch = torch.from_numpy(ids_E[s : s + SUBBATCH].astype(np.int64))
            imp = compute_importances(model, batch, precision=precision)
            sums.update(imp.g)
            for c in conditions:
                res = evaluate_condition(model, CONDITION_BY_NAME[c], batch, imp, draw=0, subbatch_index=i, master_seed=MASTER_SEED,
                                         weight_deltas=weight_deltas, seq_index=np.arange(s, s + batch.shape[0]))
                acc[c][s : s + SUBBATCH] = res.kl.cpu().numpy()
                if c == "importances":  # its masks are the labels themselves
                    assert res.fp is not None
                    fps.append(res.fp["F"])
            del imp
        for c in conditions:
            kl[f"{tag}/{c}"] = acc[c]
        label_fp[tag] = fps
        n_pos = sums.n_positions
        counts[tag] = {"n_positions": n_pos,
                       "above_0": sum(sums.count_above["0.0"].values()) / n_pos,
                       "above_0.1": sum(sums.count_above["0.1"].values()) / n_pos}
        out["timings_s"][tag] = time.time() - t0
        log(f"[smoke] pass {tag} ({precision}, {conditions}) in {out['timings_s'][tag]:.0f} s")

    pass_over_E("fp32", ("unmasked_delta",), "fp32")
    pass_over_E("bf16", ("unmasked_delta", "importances", "zero_all"), "bf16_first")
    pass_over_E("bf16", ("importances",), "bf16_second")

    def mean(name: str) -> float:
        return float(kl[name].astype(np.float64).mean(axis=1).mean())  # per text over 512 positions, then over texts

    out["check_5"] = {
        "a_all_on_delta_on_fp32": {"value": mean("fp32/unmasked_delta"), "dtype": "float32", "delta": "on (mask 1)", "expected": "< 1e-5"},
        "a_all_on_delta_on_bf16": {"value": mean("bf16_first/unmasked_delta"), "dtype": "bf16 autocast", "delta": "on (mask 1)",
                                   "expected": "recorded; the earlier project allowed 1e-3"},
        "b_at_labels": {"value": mean("bf16_first/importances"), "dtype": "bf16 autocast", "delta": "excluded (the first post's)",
                        "expected": 0.3417},
        "c_repeat": {"value_second": mean("bf16_second/importances"),
                     "kl_bitwise_identical": bool(np.array_equal(kl["bf16_first/importances"].view(np.int32), kl["bf16_second/importances"].view(np.int32))),
                     "label_fingerprints_identical": label_fp["bf16_first"] == label_fp["bf16_second"],
                     "label_fingerprint_note": "vpd_audit/fingerprint.py level 3 (F) of the applied masks, per sub-batch of 64; for this condition the masks are the labels",
                     "max_abs_diff_per_position": float(np.abs(kl["bf16_first/importances"] - kl["bf16_second/importances"]).max())},
        "d_labels_per_position": {"bf16": counts["bf16_first"], "fp32": counts["fp32"], "expected": {"above_0": 205, "above_0.1": 170},
                                  "earlier_project_bf16_above_0": 203.42},
        "e_zero_ablate_all_24": {"value": mean("bf16_first/zero_all"), "dtype": "bf16 autocast", "delta": "mask 0 (excluded)",
                                 "expected": 67.2449, "earlier_project_bf16_on_E": 67.1046},
    }
    log(f"[smoke] check 5: {json.dumps({k: v.get('value', v.get('kl_bitwise_identical')) for k, v in out['check_5'].items()})}")

    # 6. readings of logged values
    out["check_6"] = {"minimality": readings_minimality(model, ids_E, device, log),
                      "stochastic": readings_stochastic(model, ids_E, weight_deltas, device, log)}
    out["timings_s"]["total"] = time.time() - t_start
    return out


def readings_minimality(model: Any, ids: np.ndarray, device: str, log: Any) -> dict[str, Any]:
    """The authors' own minimality functions (param_decomp/metrics/importance_minimality_loss.py at 74146b5, identical
    to spd/metrics/importance_minimality_loss.py at the run's commit 85c6b70), fed the upper-leaky output under bf16
    autocast, at p = 0.4 exactly (fraction of training 1.0)."""
    import torch

    from vpd_audit_2.run_config import loss_entry

    from param_decomp.metrics.importance_minimality_loss import (
        _get_linear_annealed_p,
        _importance_minimality_loss_compute,
        _importance_minimality_loss_update,
    )

    cfg = loss_entry("ImportanceMinimalityLoss")
    p_final = _get_linear_annealed_p(1.0, cfg["pnorm"], cfg["p_anneal_start_frac"], cfg["p_anneal_final_p"], cfg["p_anneal_end_frac"])
    assert p_final == 0.4, p_final
    t0 = time.time()

    def sums_for(texts: int, chunk: int, eps: float) -> list[tuple[dict[str, Any], int]]:
        """Per-chunk per-component sums of (upper_leaky + eps)^p, each chunk the authors' update on `chunk` texts."""
        out = []
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            for s in range(0, texts, chunk):
                batch = torch.from_numpy(ids[s : s + chunk].astype(np.int64)).to(device)
                o = model(batch, cache_type="input")
                ci = model.calc_causal_importances(o.cache, sampling="continuous", detach_inputs=False)
                sums, n = _importance_minimality_loss_update(ci_upper_leaky=ci.upper_leaky, pnorm=cfg["pnorm"], eps=eps,
                                                             p_anneal_start_frac=cfg["p_anneal_start_frac"], p_anneal_final_p=cfg["p_anneal_final_p"],
                                                             p_anneal_end_frac=cfg["p_anneal_end_frac"], current_frac_of_training=1.0)
                out.append(({k: v.detach().float().clone() for k, v in sums.items()}, n))
                del o, ci
        return out

    def whole(chunks: list[tuple[dict[str, Any], int]], beta: float) -> float:
        tot = {k: torch.zeros_like(v) for k, v in chunks[0][0].items()}
        n = 0
        for s, k_n in chunks:
            for k in tot:
                tot[k] += s[k]
            n += k_n
        return float(_importance_minimality_loss_compute(per_component_sums=tot, n_examples=n, beta=beta, world_size=1))

    def per_process(chunks: list[tuple[dict[str, Any], int]], beta: float, world_size: int) -> float:
        vals = [float(_importance_minimality_loss_compute(per_component_sums=s, n_examples=n, beta=beta, world_size=world_size)) for s, n in chunks]
        return float(np.mean(vals))

    share = MINIMALITY_TEXTS // N_PROCESSES_RELEASED_RUN
    readings = []
    for eps_name, eps in (("eps_1e-12", cfg["eps"]), ("eps_0", 0.0)):
        chunks = sums_for(MINIMALITY_TEXTS, share, eps)
        for beta_name, beta in (("beta_0.5", cfg["beta"]), ("beta_0", 0.0)):
            readings.append({"sum": "whole batch of 64 (world size 1)", "eps": eps_name, "beta": beta_name, "value": whole(chunks, beta)})
            readings.append({"sum": f"per process: 16 shares of {share} texts (world size 16), mean over shares", "eps": eps_name,
                             "beta": beta_name, "value": per_process(chunks, beta, N_PROCESSES_RELEASED_RUN)})
    for r in readings:
        for name in ("paper_train_minimality_line_2224", "logged_train_minimality_step_400000"):
            r[f"within_10pct_of_{name}"] = _within_10pct(r["value"], LOGGED[name])
            r[f"ratio_to_{name}"] = r["value"] / LOGGED[name]
    eval_chunks = sums_for(STOCHASTIC_TEXTS, EVAL_CHUNK, cfg["eps"])
    eval_reading = {"sum": "whole batch of 128 (world size 1), the logged evaluation's form", "eps": "eps_1e-12", "beta": "beta_0.5",
                    "value": whole(eval_chunks, cfg["beta"]), "texts": [0, STOCHASTIC_TEXTS - 1]}
    eval_reading["within_10pct_of_logged_eval_minimality_step_400000"] = _within_10pct(eval_reading["value"], LOGGED["logged_eval_minimality_step_400000"])
    eval_reading["ratio_to_logged_eval_minimality_step_400000"] = eval_reading["value"] / LOGGED["logged_eval_minimality_step_400000"]
    log(f"[smoke] minimality readings in {time.time() - t0:.0f} s: " + "; ".join(f"{r['sum'][:9]} {r['eps']} {r['beta']}: {r['value']:.2f}" for r in readings))
    return {"p": p_final, "texts": [0, MINIMALITY_TEXTS - 1], "precision": "bf16 autocast (training)", "ci_output": "upper_leaky",
            "readings": readings, "addition_eval_form": eval_reading, "targets": {k: v for k, v in LOGGED.items() if "minimality" in k},
            "seconds": time.time() - t0}


def readings_stochastic(model: Any, ids: np.ndarray, weight_deltas: dict[str, Any], device: str, log: Any) -> dict[str, Any]:
    """One draw (global seed 0, drawn chunk by chunk of 8 texts) of the authors' `calc_stochastic_component_mask_info`
    with the configured uniform-k-subset router; two readings from the same draw. The authors'
    `_stochastic_recon_subset_loss_update` is run on the same seed as a check that the first reading is theirs."""
    import torch

    from vpd_audit_2.run_config import loss_entry

    from param_decomp.configs import UniformKSubsetRoutingConfig
    from param_decomp.metrics.stochastic_recon_subset_loss import _stochastic_recon_subset_loss_update
    from param_decomp.models.batch_and_loss_fns import recon_loss_kl
    from param_decomp.models.components import make_mask_infos
    from param_decomp.routing import get_subset_router
    from param_decomp.utils.component_utils import calc_stochastic_component_mask_info

    cfg = loss_entry("StochasticReconSubsetLoss")
    assert cfg["routing"] == {"type": "uniform_k_subset"}
    router = get_subset_router(UniformKSubsetRoutingConfig(), device)
    t0 = time.time()
    tot = {"target_weights": 0.0, "labels": 0.0, "authors_function": 0.0}
    n_tot = 0
    routed_frac = []

    torch.manual_seed(STOCHASTIC_SEED)
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        for s in range(0, STOCHASTIC_TEXTS, EVAL_CHUNK):
            batch = torch.from_numpy(ids[s : s + EVAL_CHUNK].astype(np.int64)).to(device)
            o = model(batch, cache_type="input")
            ci = model.calc_causal_importances(o.cache, sampling="continuous", detach_inputs=False).lower_leaky
            st = torch.cuda.get_rng_state()
            infos = calc_stochastic_component_mask_info(causal_importances=ci, component_mask_sampling="continuous",
                                                        weight_deltas=weight_deltas, router=router)
            after = torch.cuda.get_rng_state()
            out_t = model(batch, mask_infos=infos)
            loss_t, n = recon_loss_kl(out_t, o.output)
            alt_masks, alt_deltas = {}, {}
            for k, info in infos.items():
                rm = info.routing_mask
                assert not isinstance(rm, str)
                routed_frac.append(float(rm.float().mean()))
                alt_masks[k] = torch.where(rm[..., None], info.component_mask, ci[k])
                wd, dm = info.weight_delta_and_mask
                alt_deltas[k] = (wd, torch.where(rm, dm, torch.zeros_like(dm)))
            alt = make_mask_infos(component_masks=alt_masks, routing_masks="all", weight_deltas_and_masks=alt_deltas)
            out_l = model(batch, mask_infos=alt)
            loss_l, n_l = recon_loss_kl(out_l, o.output)
            torch.cuda.set_rng_state(st)  # the same draw again, through the authors' metric function
            loss_a, n_a = _stochastic_recon_subset_loss_update(model=model, sampling="continuous", n_mask_samples=1, batch=batch,
                                                               target_out=o.output, ci=ci, weight_deltas=weight_deltas, router=router,
                                                               reconstruction_loss=recon_loss_kl)
            assert torch.equal(torch.cuda.get_rng_state(), after), "the authors' function drew differently"
            assert n == n_l == n_a
            tot["target_weights"] += float(loss_t)
            tot["labels"] += float(loss_l)
            tot["authors_function"] += float(loss_a)
            n_tot += n
            del o, ci, infos, alt, out_t, out_l
    readings = []
    for name, desc in (("target_weights", "unrouted matrices at their target weights (the code's torch.where)"),
                       ("labels", "unrouted matrices at their labels: component masks g, delta mask 0")):
        v = tot[name] / n_tot
        r = {"unrouted": desc, "value": v}
        for target in ("paper_eval_stochastic_line_2232", "logged_eval_stochastic_step_400000"):
            r[f"within_10pct_of_{target}"] = _within_10pct(v, LOGGED[target])
            r[f"ratio_to_{target}"] = v / LOGGED[target]
        readings.append(r)
    res = {"texts": [0, STOCHASTIC_TEXTS - 1], "seed": STOCHASTIC_SEED, "draw_chunk_texts": EVAL_CHUNK, "precision": "bf16 autocast (evaluation)",
           "delta_components": "on, uniform source per position", "routing": "uniform_k_subset", "readings": readings,
           "authors_function_value": tot["authors_function"] / n_tot,
           "authors_function_equals_target_weights_reading": tot["authors_function"] == tot["target_weights"],
           "mean_fraction_of_matrices_routed_per_position": float(np.mean(routed_frac)),
           "targets": {k: v for k, v in LOGGED.items() if "stochastic" in k}, "seconds": time.time() - t0}
    log(f"[smoke] stochastic readings: target weights {readings[0]['value']:.4f}, labels {readings[1]['value']:.4f}, authors' function {res['authors_function_value']:.4f}")
    return res
