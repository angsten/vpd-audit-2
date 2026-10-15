"""Session 4, plan 1: the GPU label computations the prices need (plan 2, items 1 and 7).

  - `bf16_cache`: Q's labels in bf16 autocast, with their pre-sigmoid values z, in chunks of 32: the bf16 pass of plan 2's
    `labels.paired_precision`, whose sparse labels hash-matched the earlier harness's bf16 cache `E_main` bit for bit.
    The label blocks (indptr, indices, values) must hash equal to `labels/reproduce/E_main.npz`; z is stored beside them.
    Written as `labels/Q_bf16.npz` with a manifest, in fresh_cache's layout.
  - `check4`: price check 4 on the rebuilt step-400,000 evaluation batch `WS_W16`. The labels are recomputed as plan 2's
    world-size test computed them (bf16 autocast, no_grad, rank shares of 8 texts in rank order, the authors' `CI_L0`), and
    tied to plan 2's by the 24 L0 values. The minimality in two forms through the authors' `_update` and `_compute` on
    the upper-leaky output: the whole batch at world size 1 (the evaluation's form) and the per-process form, 16 shares of
    8 texts at world size 16, the mean over shares. Float32 labels are computed beside the bf16 ones.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import numpy as np

CHUNK = 32
SEQ_LEN = 512
L0_EXACT_OR_TOL = 0.0005  # plan 2, item 7: equal, or each within 0.05 percent


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def bf16_cache(model: Any, ids: np.ndarray, out_path: Path, meta_extra: dict[str, Any], reference_sha256: dict[str, str], log: Any = print) -> dict[str, Any]:
    import json

    import torch

    from vpd_audit_2.labels import _global_matrix

    from vpd_audit.donors import module_offsets

    assert ids.ndim == 2 and ids.shape[1] == SEQ_LEN and ids.shape[0] % CHUNK == 0
    assert not torch.backends.cuda.matmul.allow_tf32 and torch.get_float32_matmul_precision() == "highest"
    device = next(model.parameters()).device
    keys = sorted(model.module_to_c)
    parts: dict[str, list[np.ndarray]] = {k: [] for k in ("cnt", "idx", "val", "z")}
    t0 = time.time()
    for s in range(0, ids.shape[0], CHUNK):
        batch = torch.from_numpy(ids[s : s + CHUNK].astype(np.int64)).to(device)
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            out = model(batch, cache_type="input")
            ci = model.calc_causal_importances(out.cache, sampling="continuous", detach_inputs=False)
            Z, L = _global_matrix(ci.pre_sigmoid, keys), _global_matrix(ci.lower_leaky, keys)
        assert L.dtype == torch.float32, L.dtype
        Zf = Z.float()
        assert torch.equal(L, Zf.clamp(0, 1)), "lower-leaky is not clamp(z, 0, 1) in the bf16 pass"
        pos = L > 0
        idx = torch.nonzero(pos)
        parts["cnt"].append(pos.sum(1).cpu().numpy().astype(np.int64))
        parts["idx"].append(idx[:, 1].cpu().numpy().astype(np.uint16))
        parts["val"].append(L[idx[:, 0], idx[:, 1]].cpu().numpy().astype(np.float32))
        parts["z"].append(Zf[idx[:, 0], idx[:, 1]].cpu().numpy().astype(np.float32))
        del out, ci, Z, L, Zf, pos, idx
        torch.cuda.empty_cache()
    cnt = np.concatenate(parts["cnt"])
    arrays = {"indptr": np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64), "indices": np.concatenate(parts["idx"]),
              "values": np.concatenate(parts["val"]), "z": np.concatenate(parts["z"])}
    sha = {k: _sha(v) for k, v in arrays.items()}
    equal = {k: sha[k] == reference_sha256[k] for k in ("indptr", "indices", "values")}
    log(f"[prices] bf16 pass over {ids.shape[0]} texts in {time.time() - t0:.0f} s; label blocks equal E_main: {equal}")
    n_pos = ids.shape[0] * SEQ_LEN
    meta = {**meta_extra, "n_sequences": int(ids.shape[0]), "seq_len": SEQ_LEN, "n_positions": n_pos, "n_subcomponents": int(sum(model.module_to_c.values())),
            "module_order": keys, "module_offsets": module_offsets(model.module_to_c), "module_to_c": {k: int(model.module_to_c[k]) for k in keys},
            "precision": "bf16 autocast (the earlier harness's E_main conditions), labels and z stored as float32", "chunk": CHUNK,
            "label": "lower_leaky = clamp(z, 0, 1); upper_leaky recomputable from z", "blocks": {"pos": "every entry with label > 0: indptr, indices, values, z"},
            "dtypes": {k: str(v.dtype) for k, v in arrays.items()}, "nnz": int(arrays["indptr"][-1]),
            "mean_count_above_0_per_position": float(arrays["indptr"][-1] / n_pos), "count_z_above_1": int((arrays["z"] > 1).sum()),
            "sha256": sha, "label_blocks_equal_E_main": equal, "E_main_sha256": reference_sha256,
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(), "seconds": time.time() - t0,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if all(equal.values()):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = out_path.with_suffix(".npz.tmp")
        with open(tmp, "wb") as f:
            np.savez(f, **arrays)
        tmp.replace(out_path)
        meta["bytes"] = int(out_path.stat().st_size)
        with open(out_path.with_suffix(".json"), "w") as f:
            json.dump(meta, f, indent=1, sort_keys=True)
    return meta


def check4(model: Any, ids: np.ndarray, plan2_l0: dict[str, float], log: Any = print) -> dict[str, Any]:
    """Price check 4. Pass: either bf16 form within 0.1 percent of the logged 1158.32, with the labels tied to plan 2's."""
    import torch

    from vpd_audit_2.prices import LOGGED_EVAL_MINIMALITY, authors_compute, authors_update, constants
    from vpd_audit_2.run_config import RAW, eval_entry

    from param_decomp.metrics.ci_l0 import CI_L0

    C = constants()
    W, share = 16, ids.shape[0] // 16
    assert ids.shape == (128, SEQ_LEN)
    device = next(model.parameters()).device
    l0_cfg = eval_entry("CI_L0")
    out: dict[str, Any] = {"texts": "manifest pool WS_W16 (the rebuilt step-400,000 evaluation batch), 128 texts, rank shares of 8 in rank order",
                           "logged": LOGGED_EVAL_MINIMALITY}
    for prec in ("bf16", "fp32"):
        l0 = CI_L0(model=model, device=str(device), ci_alive_threshold=RAW["ci_alive_threshold"], groups=l0_cfg["groups"])
        sums64: list[dict[str, Any]] = []
        sums32: list[dict[str, Any]] = []
        n_rank = None
        ctx = torch.autocast(device_type="cuda", dtype=torch.bfloat16) if prec == "bf16" else torch.autocast(device_type="cuda", enabled=False)
        for r in range(W):
            batch = torch.from_numpy(ids[r * share : (r + 1) * share].astype(np.int64)).to(device)
            with torch.no_grad(), ctx:
                target_output = model(batch, cache_type="input")
                ci = model.calc_causal_importances(pre_weight_acts=target_output.cache, detach_inputs=False, sampling=RAW["sampling"])
                l0.update(ci=ci)
            up = {k: v.float() for k, v in ci.upper_leaky.items()}
            s64, n = authors_update({k: v.double() for k, v in up.items()}, C)
            s32, _ = authors_update(up, C)  # the evaluation's own arithmetic: float32
            sums64.append({k: v.detach().cpu() for k, v in s64.items()})
            sums32.append({k: v.detach().cpu() for k, v in s32.items()})
            n_rank = n
            del target_output, ci, up
        l0_out = {k[len("0.0_"):]: float(v) for k, v in l0.compute().items() if k.startswith("0.0_") and not k.startswith("0.0_layer") and k != "0.0_total"}
        keys = list(sums64[0])
        tot64 = {k: sum(s[k] for s in sums64) for k in keys}
        whole = float(authors_compute(tot64, n_rank * W, 1, C))
        per = float(np.mean([float(authors_compute(s, n_rank, W, C)) for s in sums64]))
        tot32 = {k: sum(s[k] for s in sums32) for k in keys}
        whole32 = float(_compute_default(tot32, n_rank * W, 1, C.beta))
        per32 = float(np.mean([float(_compute_default(s, n_rank, W, C.beta)) for s in sums32]))
        rec = {"whole_batch_world_size_1": whole, "per_process_16_shares_of_8": per,
               "relative_difference_whole": whole / LOGGED_EVAL_MINIMALITY - 1, "relative_difference_per_process": per / LOGGED_EVAL_MINIMALITY - 1,
               "float32_arithmetic_as_evaluation": {"whole": whole32, "per_process": per32}, "l0": l0_out}
        if prec == "bf16":
            diffs = {k: l0_out[k] / plan2_l0[k] - 1 for k in plan2_l0}
            exact = all(l0_out[k] == plan2_l0[k] for k in plan2_l0)
            rec["l0_tie"] = {"all_24_equal_exactly": exact, "relative_differences": diffs, "max_abs_relative_difference": max(abs(v) for v in diffs.values()),
                             "all_within_0.05pct": all(abs(v) <= L0_EXACT_OR_TOL for v in diffs.values()),
                             "rule": "the 24 L0 values equal plan 2's exactly, or each lies within 0.05 percent (plan 2, item 7)"}
            rec["l0_tie"]["passes"] = bool(exact or rec["l0_tie"]["all_within_0.05pct"])
            within = {"whole": abs(rec["relative_difference_whole"]) <= 0.001, "per_process": abs(rec["relative_difference_per_process"]) <= 0.001}
            rec["within_0.1pct"] = within
        out[prec] = rec
        log(f"[prices] check 4 ({prec}): whole {whole:.4f}, per-process {per:.4f} against {LOGGED_EVAL_MINIMALITY:.4f}")
    b = out["bf16"]
    out["forms_within_0.1pct"] = [k for k, v in b["within_0.1pct"].items() if v]
    out["rule"] = "either bf16 form within 0.1 percent of the logged 1158.32, the labels tied to plan 2's by the 24 L0 values"
    out["passes"] = bool(b["l0_tie"]["passes"] and out["forms_within_0.1pct"])
    return out


def _compute_default(sums: dict[str, Any], n: int, W: int, beta: float) -> Any:
    """The authors' `_compute` in the default dtype (float32), as the evaluation ran it; description only."""
    from param_decomp.metrics.importance_minimality_loss import _importance_minimality_loss_compute

    return _importance_minimality_loss_compute(per_component_sums=sums, n_examples=n, beta=beta, world_size=W)
