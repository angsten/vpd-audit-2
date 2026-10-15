"""Session 4, plan 4: why our 320-step runs end higher (`sessions/004/engineering/plan_4.md`).

All runs: bf16 autocast, constant step 0.1, 320 steps, labels, target, and weight deltas computed once on the (possibly
permuted) whole batch under bf16 autocast (`adversary.prepare`, the same calls as G1's `labels_once`). The plateau of a
run is the mean harm after steps 301 to 320 (record entries 301..320).

  D1 (H-code): our loop on the whole batch against the authors' loop, rerun here with its sources and gradients
     recorded (G2's wrapper and hooks), step by step; and both against G1's committed trajectory `A_c|C1|320`.
  D2 (H-micro's mechanism): at the sources our micro-batch-8 B200 run saved after steps 20, 40, and 80, the gradient
     four ways. The reference is float32 arithmetic on the whole batch with the bf16 run's own labels, target (cast to
     float32), and weight deltas, so it differs from the bf16 versions in arithmetic only; a second reference from a full
     float32 preparation (G2's setting) is reported beside it.
  D3: our loop at micro-batch 8 on C_j from start j, j = 2..8.
  D4: C1 from start 1 with its 128 texts permuted by `perm(128, "permute", k)`, k = 1..8, in the authors' loop (whole
     batch, as G1 ran it) and in ours at micro-batch 8 (micro-batches in the permuted order); the labels are computed
     on the permuted batch.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A
from vpd_audit_2 import g2

N_STEPS = 320
STEP = 0.1
PLATEAU = (301, 321)


def plateau(record: list[float]) -> float:
    return float(np.mean(record[PLATEAU[0] : PLATEAU[1]]))


def sources_sha256(sources: dict[str, np.ndarray]) -> str:
    """As G1 hashed its final sources (`g1.search`)."""
    import hashlib

    return hashlib.sha256(b"".join(np.ascontiguousarray(sources[k]).tobytes() for k in sources)).hexdigest()


def _empty_cache() -> None:
    import torch

    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def d1(model: Any, ids: np.ndarray, start: dict[str, np.ndarray], g1_record: list[float], g1_sha: str, log: Any = print,
       device: str = "cuda") -> dict[str, Any]:
    prep = A.prepare(model, ids, "bf16", device=device)
    theirs = g2.authors_loop(model, prep, start, N_STEPS, STEP, device=device)
    log(f"[d1] authors' loop: final {theirs['final']:.4f}; equals G1's record {theirs['record'] == g1_record}")
    ours = A.run(model, prep, start, N_STEPS, STEP, record_sources=True, record_grads=True, device=device)
    log(f"[d1] our loop, whole batch: final {ours['final']:.4f}")
    c = g2.compare_runs(theirs, ours)
    gdiff = [int((theirs["grad_record"][k].view(np.uint32) != ours["grad_record"][k].view(np.uint32)).sum()) for k in range(N_STEPS)]
    first_src = next((k for k, d in enumerate(c["entries_differing_per_step"]) if d), None)
    first_harm = next((k for k, (x, y) in enumerate(zip(theirs["record"], ours["record"])) if x != y), None)
    first_grad = next((k for k, d in enumerate(gdiff) if d), None)
    out = {"sources_bitwise_equal_every_step": c["sources_bitwise_equal_every_step"], "harm_bitwise_equal_every_step": c["harm_bitwise_equal_every_step"],
           "gradients_bitwise_equal_every_step": all(d == 0 for d in gdiff), "step1_gradient_bitwise_equal": gdiff[0] == 0,
           "first_step_sources_differ": first_src, "first_step_harm_differs": first_harm, "first_step_gradient_differs": first_grad,
           "authors_rerun_equals_G1_record": theirs["record"] == g1_record, "ours_equals_G1_record": ours["record"] == g1_record,
           "authors_rerun_final_sources_sha256_equals_G1": sources_sha256(theirs["sources"]) == g1_sha,
           "ours_final_sources_sha256_equals_G1": sources_sha256(ours["sources"]) == g1_sha,
           "authors_record": theirs["record"], "ours_record": ours["record"], "plateau": {"authors": plateau(theirs["record"]), "ours": plateau(ours["record"]),
                                                                                         "G1": plateau(g1_record)},
           "seconds": {"authors": theirs["seconds"], "ours": ours["seconds"]}}
    out["bitwise"] = bool(out["sources_bitwise_equal_every_step"] and out["harm_bitwise_equal_every_step"] and out["gradients_bitwise_equal_every_step"]
                          and out["ours_equals_G1_record"] and out["ours_final_sources_sha256_equals_G1"])
    return out


def _unflatten(flat: np.ndarray, model: Any, device: str) -> dict[str, Any]:
    import torch

    out, off = {}, 0
    for k in model.target_module_paths:
        n = model.module_to_c[k] + 1
        out[k] = torch.from_numpy(flat[off : off + n].reshape(1, 1, n).copy()).to(device)
        off += n
    assert off == flat.size
    return out


def _grad(model: Any, prep: A.Prepared, sources: dict[str, Any], precision: str, micro_batch: int | None) -> np.ndarray:
    import torch

    with torch.no_grad(), A.autocast_ctx(precision):
        _, g = A.loss_and_grad(model, prep, {k: v.clone().requires_grad_(True) for k, v in sources.items()}, None, micro_batch)
    return A.flatten(dict(zip(sources, g)))


def sign_accuracy(ref: np.ndarray, g: np.ndarray, model: Any) -> dict[str, Any]:
    """Over entries with a nonzero reference gradient: the fraction whose sign differs; the same among entries whose
    |reference| is above the median nonzero |reference| of its module."""
    nz = ref != 0
    above = np.zeros_like(nz)
    for _, a, b in g2.module_slices(model):
        mag = np.abs(ref[a:b])
        med = np.median(mag[mag > 0]) if (mag > 0).any() else np.inf
        above[a:b] = mag > med
    differ = np.sign(ref) != np.sign(g)
    return {"fraction_differing_nonzero_ref": float(differ[nz].mean()), "n_nonzero_ref": int(nz.sum()),
            "fraction_differing_above_module_median": float(differ[above].mean()), "n_above_module_median": int(above.sum()),
            "exact_zeros": int((g == 0).sum())}


def d2(model: Any, ids: np.ndarray, saved: dict[str, np.ndarray], steps: tuple[int, ...] = (20, 40, 80), log: Any = print,
       device: str = "cuda") -> dict[str, Any]:
    import torch

    prep = A.prepare(model, ids, "bf16", device=device)
    flat = {s: saved[f"step_{s}"] for s in steps}
    versions = {"bf16_whole": None, "bf16_micro8": 8, "bf16_micro16": 16}
    grads: dict[int, dict[str, np.ndarray]] = {s: {} for s in steps}
    for s in steps:
        src = _unflatten(flat[s], model, device)
        for name, mb in versions.items():
            grads[s][name] = _grad(model, prep, src, "bf16", mb)
    target32 = prep.target_out.float()
    prep32 = A.Prepared(ids=prep.ids, labels=prep.labels, target_out=target32, weight_deltas=prep.weight_deltas, precision="fp32")
    del prep
    _empty_cache()
    ref_mode = "whole batch"
    for s in steps:
        src = _unflatten(flat[s], model, device)
        try:
            grads[s]["fp32_ref_same_inputs"] = _grad(model, prep32, src, "fp32", None)
        except torch.OutOfMemoryError:
            _empty_cache()
            ref_mode = "chunks of 16 (out of memory on the whole batch)"
            grads[s]["fp32_ref_same_inputs"] = _grad(model, prep32, src, "fp32", 16)
    del prep32, target32
    _empty_cache()
    prepf = A.prepare(model, ids, "fp32", device=device)
    for s in steps:
        grads[s]["fp32_ref_full_float32"] = _grad(model, prepf, _unflatten(flat[s], model, device), "fp32", None)
    del prepf
    out: dict[str, Any] = {"steps": list(steps), "reference_mode": ref_mode, "per_step": {}}
    for s in steps:
        ref = grads[s]["fp32_ref_same_inputs"]
        row = {name: sign_accuracy(ref, grads[s][name], model) for name in versions}
        row["fp32_ref_full_float32_against_ref"] = sign_accuracy(ref, grads[s]["fp32_ref_full_float32"], model)
        row["against_full_float32_ref"] = {name: sign_accuracy(grads[s]["fp32_ref_full_float32"], grads[s][name], model) for name in versions}
        row["exact_zeros_reference"] = int((ref == 0).sum())
        out["per_step"][str(s)] = row
        log(f"[d2] step {s}: " + "; ".join(f"{n} {row[n]['fraction_differing_nonzero_ref']:.4f}" for n in versions))
    return out


def run_cell(model: Any, ids: np.ndarray, start: dict[str, np.ndarray], *, authors: bool, micro_batch: int | None, log: Any = print,
             tag: str = "", device: str = "cuda") -> dict[str, Any]:
    """One 320-step run, labels computed on the given (possibly permuted) batch; returns the record and, for the authors'
    loop, the per-step sources through step 40 (D4's void check)."""
    prep = A.prepare(model, ids, "bf16", device=device)
    if authors:
        r = g2.authors_loop(model, prep, start, N_STEPS, STEP, capture_grads=False, device=device)
        extra = {"source_record_to_40": r["source_record"][:41]}
    else:
        r = A.run(model, prep, start, N_STEPS, STEP, micro_batch=micro_batch, device=device)
        extra = {}
    log(f"[diag] {tag}: plateau {plateau(r['record']):.3f}, final {r['final']:.3f}, {r['seconds'] / N_STEPS:.3f} s per step")
    return {"record": r["record"], "plateau": plateau(r["record"]), "seconds": r["seconds"], "final_sources_sha256": sources_sha256(r["sources"]),
            "micro_batch": micro_batch, "loop": "authors" if authors else "ours", **extra}


def perturbed_start(start: dict[str, np.ndarray], k: int | tuple[Any, ...]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """A start with one entry, drawn uniformly over all 38,936 entries by default_rng(seed_of(*key)), moved by one bf16
    unit in the last place of its value (2^(e - 7) for a value in [2^e, 2^(e+1))): up, unless that reaches 1, then down.
    The perturbation is exactly representable in float32.

    `k` an int is D4's void-case key ("perturb-start", k); a tuple is the key's parts after the master seed, as the
    pilot's ("pilot-perturb", batch, start, r) (plan 6, Section 4, item 3)."""
    from vpd_audit_2.manifest import seed_of

    parts = ("perturb-start", k) if isinstance(k, int) else tuple(k)
    keys = list(start)
    sizes = [start[k_].size for k_ in keys]
    rng = np.random.default_rng(seed_of(*parts))
    idx = int(rng.integers(0, sum(sizes)))
    off = 0
    for name, n in zip(keys, sizes):
        if idx < off + n:
            break
        off += n
    out = {k_: v.copy() for k_, v in start.items()}
    flat = out[name].reshape(-1)
    x = float(flat[idx - off])
    assert 0 < x < 1, x
    ulp = 2.0 ** (np.floor(np.log2(x)) - 7)
    new = x + ulp if x + ulp < 1 else x - ulp
    flat[idx - off] = np.float32(new)
    assert float(flat[idx - off]) == new
    return out, {"seed_key": [20261001, *parts], "entry": idx, "module": name, "index_in_module": idx - off, "value": x, "new_value": new,
                 "bf16_ulp": float(ulp)}


def departure(perturbed: dict[str, Any], twin: dict[str, Any], perturbed_entry: int | None = None) -> dict[str, Any]:
    """Whether a perturbed run's trajectory departs from its unperturbed twin (plan 5, item 11), so the pilot can assert it.

    Each run is a dict with `record` (the harm after every step) and, optionally, `source_record` (the flattened sources
    at every step). The run departs at the first step where the harms differ, or where the sources differ at any entry
    other than `perturbed_entry` (the injected change). An entry that has no effect on the forward (for example, a
    component whose label is 1 at every position: mask fixed at 1, gradient zero) leaves both unchanged, and the run
    never departs."""
    a, b = perturbed["record"], twin["record"]
    assert len(a) == len(b), (len(a), len(b))
    first_harm = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), None)
    first_other = None
    if "source_record" in perturbed and "source_record" in twin:
        sa, sb = np.asarray(perturbed["source_record"]), np.asarray(twin["source_record"])
        assert sa.shape == sb.shape
        diff = sa.view(np.uint32) != sb.view(np.uint32)
        if perturbed_entry is not None:
            diff[:, perturbed_entry] = False
        rows = np.flatnonzero(diff.any(axis=1))
        first_other = int(rows[0]) if rows.size else None
    firsts = [k for k in (first_harm, first_other) if k is not None]
    return {"departs": bool(firsts), "first_departure_step": min(firsts) if firsts else None, "first_harm_difference": first_harm,
            "first_other_source_difference": first_other, "sources_compared": first_other is not None or "source_record" in perturbed}


def d3_reading(ours: dict[int, list[float]], g1: dict[int, list[float]]) -> dict[str, Any]:
    from scipy.stats import binomtest

    cells = sorted(ours)
    above = {j: plateau(ours[j]) > plateau(g1[j]) for j in cells}
    n = sum(above.values())
    reading = "micro-batching raises the plateau across cells" if n == 7 else ("suggestive; undetermined" if n == 6 else "not shown")
    return {"cells": [f"C{j}" for j in cells], "plateau": {f"C{j}": {"ours_micro8": plateau(ours[j]), "G1": plateau(g1[j])} for j in cells},
            "count_ours_above_G1": n, "one_sided_sign_test_p": float(binomtest(n, len(cells), 0.5, alternative="greater").pvalue), "reading": reading,
            "description": {f"step_{s}": {"count_ours_above_G1": sum(ours[j][s] > g1[j][s] for j in cells),
                                          "values": {f"C{j}": [ours[j][s], g1[j][s]] for j in cells}} for s in (80, 160)}}


def d4_reading(authors: list[dict[str, Any]], ours: list[dict[str, Any]]) -> dict[str, Any]:
    from scipy.stats import mannwhitneyu

    pa, po = [r["plateau"] for r in authors], [r["plateau"] for r in ours]
    p = float(mannwhitneyu(po, pa, alternative="greater", method="exact").pvalue)
    reading = "micro-batching raises the plateau within a cell" if (p < 0.05 and np.median(po) > np.median(pa)) else "no detectable effect"

    def rng(rs: list[dict[str, Any]], s: int | None) -> list[float]:
        v = [r["plateau"] if s is None else r["record"][s] for r in rs]
        return [float(min(v)), float(max(v))]

    srcs = [r["source_record_to_40"] for r in authors]
    sources_identical = all(np.array_equal(srcs[0].view(np.uint32), s.view(np.uint32)) for s in srcs[1:])
    harm_identical = all(a["record"][:41] == authors[0]["record"][:41] for a in authors[1:])
    # The void case: the permutations did not perturb the authors' loop, read on its sources. The harm readout sums the
    # KL in the permuted order, so it may differ in its last bits while the search itself is unchanged (the case that
    # occurred; the team's interpretation, registered after the result, session 4, plans 4 and 5).
    identical_to_40 = sources_identical
    return {"authors_sources_identical_through_step_40": bool(sources_identical), "authors_harm_identical_through_step_40": bool(harm_identical),
            "authors_distinct_final_sources": len({a["final_sources_sha256"] for a in authors}),
            "ours_distinct_final_sources": len({o["final_sources_sha256"] for o in ours}),
            "plateaus": {"authors_whole_batch": pa, "ours_micro8": po}, "mann_whitney_exact_one_sided_p": p,
            "medians": {"authors": float(np.median(pa)), "ours": float(np.median(po))}, "reading": reading,
            "ranges": {"authors": {"step_80": rng(authors, 80), "step_160": rng(authors, 160), "plateau": rng(authors, None)},
                       "ours_micro8": {"step_80": rng(ours, 80), "step_160": rng(ours, 160), "plateau": rng(ours, None)}},
            "authors_permutations_identical_through_step_40": bool(identical_to_40), "void": bool(identical_to_40)}
