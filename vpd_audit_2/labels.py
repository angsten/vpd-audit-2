"""Plan 2 of the research log, step 5 (section 7): fresh float32 labels for pool Q, and gate G4.

GPU part (`modal_gates.py::labels_q`):
  - `fresh_cache`: on Q's 1,024 texts, in chunks of 32, the target's forward pass and the causal importance function in
    float32, autocast off, TF32 off, deterministic algorithms on: `model(batch, cache_type="input")`, then
    `calc_causal_importances(cache, sampling="continuous", detach_inputs=False)`, as `evaluate()` calls it. Stored, in
    the earlier project's sparse layout (`vpd_audit/donors.py`: per position a CSR row over the global subcomponent
    index in `sorted(module_to_c)` order; `indptr` int64, `indices` uint16, `values` float32):
      block "pos": every entry with label > 0 (lower-leaky, which is clamp(z, 0, 1) on the forward pass), with `z`,
        the pre-sigmoid value, as a parallel float32 array;
      block "band": every entry whose pre-sigmoid value lies in (-0.001, 0] (label 0), with its `z`. The plan's
        (-0.05, 0] is dense on Q (about 29,000 of 38,912 entries per position, about 92 GB); it was narrowed on
        1 October. A histogram of z near zero is recorded in the cache's manifest.
    Written to the volume `vpd-audit-2-cache` at `labels/Q_fp32.npz` with a manifest `labels/Q_fp32.json`.
  - `authors_path_check`: the authors' own call sequence of `evaluate()` (`param_decomp/eval.py:408-413`) on Q rows 0 to
    7, one process's evaluation batch of the run, in float32; its lower-leaky and pre-sigmoid values compared with the
    stored cache entry by entry.
  - `reproduce`: the earlier project's own `vpd_audit.donors.build_cache` under the inherited caches' conditions: bf16
    autocast, float32 labels, deterministic algorithms, sub-batches of 64, chunks of 32. On DU it reproduces
    D_unif_main; on Q it reproduces E_main, the like-for-like reference for G4.
  - `paired_precision`: on each chunk of 32 Q texts, the float32 pass and the bf16 pass side by side on the GPU;
    the finding asked for on 1 October: |g32 - g16| and |z32 - z16| over every entry positive in either
    precision, overall and by bands of the float32 label; entries crossing 0 and 0.1; and the saturated labels
    (z > 1) in each precision. Each pass's sparse labels are hashed, to tie them to the stored caches.

CPU part (`modal_gates.py::g4_cpu`, which mounts the earlier volume `vpd-audit-cache` read-only):
  - `g4`: the inherited `donors/E_main.npz` (same texts, rows 0 to 1,023) against a cache of Q, over entries present
    in both: the 99.9th percentile of the absolute label difference (passes below 0.02) and the mean count of labels
    above zero per position (passes within 5 percent). Recorded, not gating: entries crossing 0 and crossing 0.1. Run
    across precisions (the fresh float32 cache) and like for like (the bf16 reproduction).
  - `compare_reproduction`: a reproduced cache against the inherited one: per-position label fingerprints (SHA-256 of
    each position's indices and values), the array hashes, and the mean count per position.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

CHUNK = 32
BAND = 0.001  # the plan's 0.05 gives a dense block (about 29,000 entries per position); narrowed 1 October
SEQ_LEN = 512
PERCENTILES = (50, 90, 99, 99.9)
LABEL_BANDS = ((0.0, 0.1), (0.1, 0.5), (0.5, 0.9), (0.9, 1.0))  # [lo, hi), the last closed: by the float32 label
G4_P999_MAX = 0.02
G4_MEAN_COUNT_TOL = 0.05
AUTHORS_PATH_ROWS = (0, 8)


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _global_matrix(d: dict[str, Any], keys: list[str]) -> Any:
    import torch

    B, T = d[keys[0]].shape[:2]
    return torch.cat([d[k].reshape(B * T, -1) for k in keys], dim=1)


Z_EDGES = (-0.05, -0.01, -1e-3, -1e-4)  # the near-zero histogram: (-inf, -0.05], (-0.05, -0.01], ..., (-1e-4, 0), {0}, (0, inf)


def fresh_cache(model: Any, ids: np.ndarray, out_path: Path, meta_extra: dict[str, Any], log: Any = print, band: bool = True) -> dict[str, Any]:
    """With `band=False` the band block is not stored (on the first run it held about 29,000 entries per position, about
    90 GB for Q); its size is recorded instead, with a histogram of z near zero and its share from components never
    positive on these texts."""
    import torch

    from vpd_audit.donors import module_offsets

    assert ids.ndim == 2 and ids.shape[1] == SEQ_LEN and ids.shape[0] % CHUNK == 0
    assert not torch.backends.cuda.matmul.allow_tf32 and torch.get_float32_matmul_precision() == "highest"
    device = next(model.parameters()).device
    keys = sorted(model.module_to_c)
    n_sub = sum(model.module_to_c.values())
    assert n_sub < 65536
    parts: dict[str, list[np.ndarray]] = {k: [] for k in ("cnt", "idx", "val", "z", "bcnt", "bidx", "bz")}
    above_01 = 0
    z_max = -np.inf
    hist = np.zeros(len(Z_EDGES) + 3, dtype=np.int64)
    pos_per_comp = torch.zeros(n_sub, dtype=torch.int64, device=device)
    band_per_comp = torch.zeros(n_sub, dtype=torch.int64, device=device)
    t0 = time.time()
    for s in range(0, ids.shape[0], CHUNK):
        batch = torch.from_numpy(ids[s : s + CHUNK].astype(np.int64)).to(device)
        with torch.no_grad():
            out = model(batch, cache_type="input")
            ci = model.calc_causal_importances(out.cache, sampling="continuous", detach_inputs=False)
            Z = _global_matrix(ci.pre_sigmoid, keys)
            L = _global_matrix(ci.lower_leaky, keys)
            assert Z.dtype == torch.float32 and L.dtype == torch.float32, (Z.dtype, L.dtype)
            assert torch.equal(L, Z.clamp(0, 1)), "lower-leaky is not clamp(z, 0, 1) on the forward pass"
            pos = L > 0
            idx = torch.nonzero(pos)
            parts["cnt"].append(pos.sum(1).cpu().numpy().astype(np.int64))
            parts["idx"].append(idx[:, 1].cpu().numpy().astype(np.uint16))
            parts["val"].append(L[idx[:, 0], idx[:, 1]].cpu().numpy().astype(np.float32))
            parts["z"].append(Z[idx[:, 0], idx[:, 1]].cpu().numpy().astype(np.float32))
            band_mask = (Z > -BAND) & (Z <= 0)
            parts["bcnt"].append(band_mask.sum(1).cpu().numpy().astype(np.int64))
            if band:
                bidx = torch.nonzero(band_mask)
                parts["bidx"].append(bidx[:, 1].cpu().numpy().astype(np.uint16))
                parts["bz"].append(Z[bidx[:, 0], bidx[:, 1]].cpu().numpy().astype(np.float32))
                del bidx
            pos_per_comp += pos.sum(0)
            band_per_comp += band_mask.sum(0)
            below = [int((Z <= e).sum()) for e in Z_EDGES]  # cumulative counts at each edge
            n_all, n_zero, n_pos = Z.numel(), int((Z == 0).sum()), int(pos.sum())
            hist += np.array([below[0]] + [below[i] - below[i - 1] for i in range(1, len(below))]
                             + [n_all - n_zero - n_pos - below[-1], n_zero, n_pos], dtype=np.int64)
            above_01 += int((L > 0.1).sum())
            z_max = max(z_max, float(Z.max()))
            del out, ci, Z, L, pos, idx, band_mask
        torch.cuda.empty_cache()
        if s == 0:
            log(f"[labels] chunk 0: {parts['cnt'][0].mean():.1f} labels > 0 and {parts['bcnt'][0].mean():.1f} band entries per position")
    cnt, bcnt = np.concatenate(parts["cnt"]), np.concatenate(parts["bcnt"])
    arrays = {"indptr": np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64), "indices": np.concatenate(parts["idx"]),
              "values": np.concatenate(parts["val"]), "z": np.concatenate(parts["z"])}
    if band:
        arrays.update({"band_indptr": np.concatenate([[0], np.cumsum(bcnt)]).astype(np.int64), "band_indices": np.concatenate(parts["bidx"]),
                       "band_z": np.concatenate(parts["bz"])})
    n_pos = ids.shape[0] * SEQ_LEN
    pos_c, band_c = pos_per_comp.cpu().numpy(), band_per_comp.cpu().numpy()
    alive = pos_c > 0
    names = ["(-inf, -0.05]", "(-0.05, -0.01]", "(-0.01, -0.001]", "(-0.001, -0.0001]", "(-0.0001, 0)", "0 exactly", "(0, inf)"]
    z_summary = {"histogram_entries_per_position": {n: float(h / n_pos) for n, h in zip(names, hist)},
                 "band_entries_per_position": float(bcnt.sum() / n_pos), "band_bytes_if_stored": int(bcnt.sum() * 6),
                 "components_positive_somewhere_on_these_texts": int(alive.sum()),
                 "band_entries_per_position_from_components_never_positive_here": float(band_c[~alive].sum() / n_pos),
                 "band_entries_per_position_from_components_positive_somewhere": float(band_c[alive].sum() / n_pos)}
    assert arrays["indptr"].size == n_pos + 1 and arrays["indptr"][-1] == arrays["indices"].size == arrays["values"].size == arrays["z"].size
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".npz.tmp")
    with open(tmp, "wb") as f:
        np.savez(f, **arrays)
    tmp.replace(out_path)
    meta = {**meta_extra, "n_sequences": int(ids.shape[0]), "seq_len": SEQ_LEN, "n_positions": n_pos, "n_subcomponents": n_sub,
            "module_order": keys, "module_offsets": module_offsets(model.module_to_c), "module_to_c": {k: int(model.module_to_c[k]) for k in keys},
            "precision": "fp32, autocast off, TF32 off, float32 matmul precision highest", "label_dtype": "float32", "chunk": CHUNK,
            "label": "lower_leaky = clamp(z, 0, 1) on the forward pass; upper_leaky recomputable as 1 + 0.01 (z - 1) for z > 1, else clamp(z, 0, 1)",
            "blocks": {"pos": "every entry with label > 0: indptr, indices, values (label), z",
                       "band": (f"every entry with z in (-{BAND}, 0]: band_indptr, band_indices, band_z" if band else
                                f"NOT STORED: z in (-{BAND}, 0] holds {bcnt.sum() / n_pos:.0f} entries per position; see z_near_zero")},
            "dtypes": {k: str(v.dtype) for k, v in arrays.items()}, "nnz": int(arrays["indptr"][-1]), "band_nnz": int(bcnt.sum()),
            "mean_count_above_0_per_position": float(arrays["indptr"][-1] / n_pos), "mean_count_above_0.1_per_position": above_01 / n_pos,
            "mean_band_entries_per_position": float(bcnt.sum() / n_pos), "z_near_zero": z_summary, "z_max": z_max,
            "count_z_above_1": int((arrays["z"] > 1).sum()),
            "sha256": {k: _sha(v) for k, v in arrays.items()}, "bytes": int(out_path.stat().st_size),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(), "seconds": time.time() - t0,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    with open(out_path.with_suffix(".json"), "w") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
    log(f"[labels] fresh cache: {meta['mean_count_above_0_per_position']:.4f} labels > 0 per position, {meta['mean_band_entries_per_position']:.1f} band entries, {meta['bytes'] / 1e9:.2f} GB")
    return meta


def load_fresh(path: Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    meta = json.load(open(path.with_suffix(".json")))
    with np.load(path) as z:
        arrays = {k: z[k] for k in z.files}
    for k, v in arrays.items():
        assert _sha(v) == meta["sha256"][k], f"{path.name}: {k} hash mismatch"
    return arrays, meta


def authors_path_check(model: Any, ids: np.ndarray, fresh: dict[str, np.ndarray]) -> dict[str, Any]:
    """The authors' evaluate() call sequence on Q rows 0 to 7 in float32, against the stored entries of those rows."""
    import torch

    from vpd_audit_2.run_config import RAW

    a, b = AUTHORS_PATH_ROWS
    device = next(model.parameters()).device
    keys = sorted(model.module_to_c)
    batch = torch.from_numpy(ids[a:b].astype(np.int64)).to(device)
    with torch.no_grad():
        target_output = model(batch, cache_type="input")
        ci = model.calc_causal_importances(pre_weight_acts=target_output.cache, detach_inputs=False, sampling=RAW["sampling"])
        Z = _global_matrix(ci.pre_sigmoid, keys).cpu().numpy()
        L = _global_matrix(ci.lower_leaky, keys).cpu().numpy()
    p0, p1 = a * SEQ_LEN, b * SEQ_LEN
    ip = fresh["indptr"]
    dense_l = np.zeros_like(L)
    dense_z = np.full_like(Z, np.nan)
    for r, p in enumerate(range(p0, p1)):
        s, e = ip[p], ip[p + 1]
        dense_l[r, fresh["indices"][s:e].astype(np.int64)] = fresh["values"][s:e]
        dense_z[r, fresh["indices"][s:e].astype(np.int64)] = fresh["z"][s:e]
    stored = ~np.isnan(dense_z)
    return {"rows": [a, b - 1], "batch_size": b - a, "call": "model(batch, cache_type='input'); calc_causal_importances(pre_weight_acts=..., detach_inputs=False, sampling=run_config.sampling)",
            "precision": "fp32", "max_abs_label_difference": float(np.abs(L - dense_l).max()),
            "max_abs_z_difference_on_stored_entries": float(np.abs(Z[stored] - dense_z[stored]).max()),
            "labels_bitwise_equal": bool(np.array_equal(L, dense_l)), "positive_sets_equal": bool(np.array_equal(L > 0, dense_l > 0))}


def reproduce(model: Any, ids: np.ndarray, set_name: str, out_dir: Path, set_hash: str, checkpoint_hashes: dict[str, str], log: Any = print) -> dict[str, Any]:
    """The earlier harness's own build_cache under the inherited caches' conditions; writes <set_name>_main.npz."""
    from vpd_audit.donors import build_cache

    out_dir.mkdir(parents=True, exist_ok=True)  # build_cache creates only its default directory
    return build_cache(model, ids, run="main", set_name=set_name, set_hash=set_hash, checkpoint_hashes=checkpoint_hashes, precision="bf16",
                       subbatch=64, chunk=32, alive_checkpoints=None, out_dir=out_dir, log=log)


def _summary(d: np.ndarray) -> dict[str, float]:
    if d.size == 0:
        return {"n": 0}
    q = np.percentile(d, PERCENTILES)
    return {"n": int(d.size), **{f"p{p:g}": float(v) for p, v in zip(PERCENTILES, q)}, "max": float(d.max()), "mean": float(d.mean())}


def _by_band(d: np.ndarray, g32: np.ndarray) -> dict[str, Any]:
    out = {}
    for lo, hi in LABEL_BANDS:
        m = (g32 >= lo) & ((g32 < hi) if hi < 1.0 else (g32 <= hi))
        out[f"[{lo}, {hi}{')' if hi < 1.0 else ']'}"] = _summary(d[m])
    return out


def _saturation(g: np.ndarray, z: np.ndarray, n_pos: int) -> dict[str, Any]:
    pos, above = g > 0, g > 0.1
    zs = z[pos & (z > 1)]
    edges = [1, 1.5, 2, 4, 8, 16, np.inf]
    hist = np.histogram(zs, bins=edges)[0]
    return {"labels_above_0_per_position": float(pos.sum() / n_pos), "labels_above_0.1_per_position": float(above.sum() / n_pos),
            "share_of_labels_above_0_with_z_above_1": float((pos & (z > 1)).sum() / pos.sum()),
            "share_of_labels_above_0.1_with_z_above_1": float((above & (z > 1)).sum() / above.sum()),
            "saturated_per_position": float(zs.size / n_pos), "z_above_1_percentiles": _summary(zs),
            "z_above_1_histogram": {f"({a:g}, {b:g}]": int(h) for a, b, h in zip(edges[:-1], edges[1:], hist)}}


def paired_precision(model: Any, ids: np.ndarray, log: Any = print) -> dict[str, Any]:
    """Float32 and bf16 passes on each chunk of 32 texts, compared on the dense tensors. The float32 pass is the fresh
    cache's (autocast off, TF32 off); the bf16 pass is E_main's (bf16 autocast, the outputs float32)."""
    import torch

    assert not torch.backends.cuda.matmul.allow_tf32 and torch.get_float32_matmul_precision() == "highest"
    device = next(model.parameters()).device
    keys = sorted(model.module_to_c)
    cols = {k: [] for k in ("g32", "g16", "z32", "z16")}
    csr = {p: {"cnt": [], "idx": [], "val": []} for p in ("fp32", "bf16")}
    cross0 = cross01 = 0
    t0 = time.time()
    for s in range(0, ids.shape[0], CHUNK):
        batch = torch.from_numpy(ids[s : s + CHUNK].astype(np.int64)).to(device)
        dense = {}
        for prec in ("fp32", "bf16"):
            ctx = torch.autocast(device_type="cuda", dtype=torch.bfloat16) if prec == "bf16" else torch.autocast(device_type="cuda", enabled=False)
            with torch.no_grad(), ctx:
                out = model(batch, cache_type="input")
                ci = model.calc_causal_importances(out.cache, sampling="continuous", detach_inputs=False)
                Z, L = _global_matrix(ci.pre_sigmoid, keys), _global_matrix(ci.lower_leaky, keys)
            assert L.dtype == torch.float32, (prec, L.dtype)
            dense[prec] = (Z.float(), L)
            pos = L > 0
            idx = torch.nonzero(pos)
            csr[prec]["cnt"].append(pos.sum(1).cpu().numpy().astype(np.int64))
            csr[prec]["idx"].append(idx[:, 1].cpu().numpy().astype(np.uint16))
            csr[prec]["val"].append(L[idx[:, 0], idx[:, 1]].cpu().numpy().astype(np.float32))
            del out, ci, pos, idx
        (Z32, L32), (Z16, L16) = dense["fp32"], dense["bf16"]
        union = torch.nonzero((L32 > 0) | (L16 > 0))
        r, c = union[:, 0], union[:, 1]
        cols["g32"].append(L32[r, c].cpu().numpy())
        cols["g16"].append(L16[r, c].cpu().numpy())
        cols["z32"].append(Z32[r, c].cpu().numpy())
        cols["z16"].append(Z16[r, c].cpu().numpy())
        cross0 += int(((L32 > 0) != (L16 > 0)).sum())
        cross01 += int(((L32 > 0.1) != (L16 > 0.1)).sum())
        del dense, Z32, L32, Z16, L16, union
        torch.cuda.empty_cache()
    log(f"[labels] paired passes in {time.time() - t0:.0f} s")
    n_pos = ids.shape[0] * SEQ_LEN
    hashes = {}
    for prec, p in csr.items():
        cnt = np.concatenate(p["cnt"])
        arr = {"indptr": np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64), "indices": np.concatenate(p["idx"]), "values": np.concatenate(p["val"])}
        hashes[prec] = {k: _sha(v) for k, v in arr.items()}
    g32, g16, z32, z16 = (np.concatenate(cols[k]) for k in ("g32", "g16", "z32", "z16"))
    dg, dz = np.abs(g32.astype(np.float64) - g16), np.abs(z32.astype(np.float64) - z16)
    both = (g32 > 0) & (g16 > 0)
    return {
        "texts": "pool Q, all 1,024", "entries": "every entry positive in either precision (the union); the other precision's value there may be 0",
        "bands": "by the float32 label g32; entries positive in bf16 only have g32 = 0 and fall in the first band",
        "n_union_entries": int(g32.size), "n_entries_positive_in_both": int(both.sum()),
        "abs_label_difference": {"overall": _summary(dg), "positive_in_both": _summary(dg[both]), "by_float32_label": _by_band(dg, g32)},
        "abs_z_difference": {"overall": _summary(dz), "positive_in_both": _summary(dz[both]), "by_float32_label": _by_band(dz, g32)},
        "crossing_0_per_position": cross0 / n_pos, "crossing_0.1_per_position": cross01 / n_pos,
        "mean_count_above_0_per_position": {"fp32": float((g32 > 0).sum() / n_pos), "bf16": float((g16 > 0).sum() / n_pos)},
        "saturation": {"fp32": _saturation(g32, z32, n_pos), "bf16": _saturation(g16, z16, n_pos)},
        "sparse_label_hashes": hashes, "seconds": time.time() - t0,
    }


# ----------------------------------------------------------------------------- CPU comparisons


def _keys(indptr: np.ndarray, indices: np.ndarray, n_sub: int) -> np.ndarray:
    pos = np.repeat(np.arange(indptr.size - 1, dtype=np.int64), np.diff(indptr))
    return pos * n_sub + indices.astype(np.int64)


def _member(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """For sorted unique a, b: mask over b of members of a, and their index in a."""
    j = np.searchsorted(a, b)
    jc = np.minimum(j, a.size - 1)
    found = (j < a.size) & (a[jc] == b)
    return found, jc


def g4(inherited: tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]], fresh: dict[str, np.ndarray], fresh_meta: dict[str, Any],
       fresh_name: str = "vpd-audit-2-cache:labels/Q_fp32.npz") -> dict[str, Any]:
    ip_a, ix_a, v_a, meta_a = inherited
    assert meta_a["module_order"] == fresh_meta["module_order"] and meta_a["n_subcomponents"] == fresh_meta["n_subcomponents"]
    assert meta_a["n_positions"] == fresh_meta["n_positions"]
    n_sub, n_pos = fresh_meta["n_subcomponents"], fresh_meta["n_positions"]
    ka = _keys(ip_a, ix_a, n_sub)
    kb = _keys(fresh["indptr"], fresh["indices"], n_sub)
    assert np.all(np.diff(ka) > 0) and np.all(np.diff(kb) > 0)
    found, j = _member(ka, kb)
    diff = np.abs(fresh["values"][found].astype(np.float64) - v_a[j[found]].astype(np.float64))
    p999 = float(np.percentile(diff, 99.9))
    mean_a, mean_b = ka.size / n_pos, kb.size / n_pos
    rel = mean_b / mean_a - 1
    a01, b01 = ka[v_a > 0.1], kb[fresh["values"] > 0.1]
    f01, _ = _member(a01, b01)
    both01 = int(f01.sum())
    res = {
        "inherited": {"cache": "vpd-audit-cache:donors/E_main.npz", "sha256": meta_a["sha256"], "precision": meta_a["precision"],
                      "set_hash": meta_a["set_hash"], "commits": meta_a.get("commits")},
        "fresh": {"cache": fresh_name, "sha256": fresh_meta["sha256"], "precision": fresh_meta["precision"]},
        "entries_inherited": int(ka.size), "entries_fresh": int(kb.size), "entries_in_both": int(found.sum()),
        "abs_label_difference_in_both": {"p99.9": p999, "p99": float(np.percentile(diff, 99)), "p50": float(np.percentile(diff, 50)),
                                         "max": float(diff.max()), "mean": float(diff.mean())},
        "mean_count_above_0_per_position": {"inherited": mean_a, "fresh": mean_b, "relative_difference": rel},
        "crossing_0": {"inherited_only": int(ka.size - found.sum()), "fresh_only": int(kb.size - found.sum()),
                       "total": int(ka.size - found.sum() + kb.size - found.sum()), "per_position": (ka.size + kb.size - 2 * int(found.sum())) / n_pos},
        "crossing_0.1": {"inherited_only": int(a01.size - both01), "fresh_only": int(b01.size - both01),
                         "total": int(a01.size + b01.size - 2 * both01), "per_position": (a01.size + b01.size - 2 * both01) / n_pos},
        "rule": f"passes if the 99.9th percentile of |label difference| over entries in both is below {G4_P999_MAX} and the mean count of labels > 0 per position agrees within {G4_MEAN_COUNT_TOL:.0%}",
    }
    res["passes"] = bool(p999 < G4_P999_MAX and abs(rel) <= G4_MEAN_COUNT_TOL)
    return res


def compare_reproduction(inherited: tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]], fresh: tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]],
                         name: str) -> dict[str, Any]:
    ip_a, ix_a, v_a, meta_a = inherited
    ip_b, ix_b, v_b, meta_b = fresh
    n_pos = meta_a["n_positions"]
    assert n_pos == meta_b["n_positions"]
    equal = 0
    first_unequal = None
    for p in range(n_pos):
        a = ix_a[ip_a[p] : ip_a[p + 1]].tobytes() + v_a[ip_a[p] : ip_a[p + 1]].tobytes()
        b = ix_b[ip_b[p] : ip_b[p + 1]].tobytes() + v_b[ip_b[p] : ip_b[p + 1]].tobytes()
        if hashlib.sha256(a).digest() == hashlib.sha256(b).digest():
            equal += 1
        elif first_unequal is None:
            first_unequal = p
    return {"inherited": {"cache": f"vpd-audit-cache:donors/{name}.npz", "sha256": meta_a["sha256"], "commits": meta_a.get("commits"),
                          "mean_nnz_per_position": meta_a["mean_nnz_per_position"], "set_hash": meta_a["set_hash"]},
            "reproduced": {"sha256": meta_b["sha256"], "mean_nnz_per_position": meta_b["mean_nnz_per_position"], "set_hash": meta_b["set_hash"],
                           "commits": meta_b.get("commits"), "gpu_name": meta_b.get("gpu_name"), "torch_version": meta_b.get("torch_version")},
            "arrays_identical": meta_a["sha256"] == meta_b["sha256"], "positions": n_pos, "positions_with_identical_fingerprint": equal,
            "first_unequal_position": first_unequal, "fingerprint": "SHA-256 of a position's uint16 indices then float32 values"}
