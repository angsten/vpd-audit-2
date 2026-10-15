"""Plan 2, step 6 (section 8): gate G1, the step-size schedule. The GPU part; the readings are in `g1_readings.py`.

One search is the authors' own evaluation adversary loop, called directly:
  - the labels, the target output, and the weight deltas are computed once, under `no_grad` (and bf16 autocast unless
    float32 is asked for), as `evaluate()` does (`param_decomp/eval.py:402-413` at the tag);
  - the routing masks come from `AllLayersRouter().get_masks` and the forward function is
    `functools.partial(_forward_with_adv_sources, ...)` with `recon_loss_kl`, exactly as `pgd_masked_recon_loss_update`
    builds them (`param_decomp/metrics/pgd_utils.py:95-126`), with the delta components on;
  - the sources are a saved start (shape [1, 1, C_l + 1] per module in `model.target_module_paths` order, delta entry
    last) cloned to the device with `requires_grad_(True)`, in place of `_init_adv_sources`' global `torch.rand`;
  - `_run_pgd_loop(adv_sources, PGDConfig(init="random", step_size, n_steps, mask_scope="shared_across_batch"), fwd)`
    runs the loop (`pgd_utils.py:42-66`): `n_steps` sign steps and clamps, then one final forward.

Internal functions called: `param_decomp.metrics.pgd_utils._run_pgd_loop`, `_forward_with_adv_sources`;
`param_decomp.routing.AllLayersRouter`; `param_decomp.models.batch_and_loss_fns.recon_loss_kl`;
`ComponentModel.calc_causal_importances`, `calc_weight_deltas`.

The recording wrapper returns the loop's own (sum_loss, n_examples), not copies, after appending
`float(sum_loss.detach()) / n_examples`. Entry k of the record (from zero) is the harm after k updates; the last entry,
from the final forward, is the harm after the last update. A run of n steps therefore records n + 1 values.
"""

from __future__ import annotations

import contextlib
import functools
import hashlib
import time
from typing import Any

import numpy as np

STEP_SIZE_C = 0.1
BUDGETS = (20, 40, 80, 160, 320)


def start_tensors(start: dict[str, np.ndarray], model: Any, device: str) -> dict[str, Any]:
    """The saved start as the loop's sources, after asserting its layout matches the model."""
    import torch

    keys = list(start)
    assert keys == list(model.target_module_paths), "the start's module order is not model.target_module_paths"
    for k in keys:
        assert start[k].shape == (1, 1, model.module_to_c[k] + 1), (k, start[k].shape, model.module_to_c[k])
        assert start[k].dtype == np.float32
    return {k: torch.from_numpy(start[k].copy()).to(device).requires_grad_(True) for k in keys}


def labels_once(model: Any, batch: Any, precision: str) -> tuple[Any, Any, Any]:
    import torch

    ctx = torch.autocast(device_type="cuda", dtype=torch.bfloat16) if precision == "bf16" else contextlib.nullcontext()
    with torch.no_grad(), ctx:
        weight_deltas = model.calc_weight_deltas()
        target_output = model(batch, cache_type="input")
        ci = model.calc_causal_importances(pre_weight_acts=target_output.cache, detach_inputs=False, sampling="continuous")
    return ci.lower_leaky, target_output.output, weight_deltas


def search(model: Any, ids: np.ndarray, start: dict[str, np.ndarray], n_steps: int, step_size: float, *, precision: str = "bf16",
           wrap: bool = True, device: str = "cuda", labels: tuple[Any, Any, Any] | None = None) -> dict[str, Any]:
    """One search on one batch from one saved start. Returns the record (n_steps + 1 harms when wrapped), the final harm
    from the loop's return value, the final sources, and the wall time."""
    import torch

    from param_decomp.configs import PGDConfig
    from param_decomp.metrics.pgd_utils import _forward_with_adv_sources, _run_pgd_loop
    from param_decomp.models.batch_and_loss_fns import recon_loss_kl
    from param_decomp.routing import AllLayersRouter

    t0 = time.time()
    batch = torch.from_numpy(ids.astype(np.int64)).to(device)
    ci, target_out, weight_deltas = labels if labels is not None else labels_once(model, batch, precision)
    ctx = torch.autocast(device_type="cuda", dtype=torch.bfloat16) if precision == "bf16" else contextlib.nullcontext()
    record: list[float] = []
    with torch.no_grad(), ctx:
        batch_dims = next(iter(ci.values())).shape[:-1]
        routing_masks = AllLayersRouter().get_masks(module_names=model.target_module_paths, mask_shape=batch_dims)
        adv_sources = start_tensors(start, model, device)
        fwd = functools.partial(_forward_with_adv_sources, model=model, batch=batch, adv_sources=adv_sources, ci=ci,
                                weight_deltas=weight_deltas, routing_masks=routing_masks, target_out=target_out,
                                batch_dims=batch_dims, reconstruction_loss=recon_loss_kl)

        def recorded() -> tuple[Any, int]:
            sum_loss, n_examples = fwd()
            record.append(float(sum_loss.detach()) / n_examples)
            return sum_loss, n_examples

        cfg = PGDConfig(init="random", step_size=step_size, n_steps=n_steps, mask_scope="shared_across_batch")
        final_sum, final_n = _run_pgd_loop(adv_sources, cfg, recorded if wrap else fwd)
        final = float(final_sum.detach()) / final_n
    torch.cuda.synchronize()
    sources = {k: v.detach().float().cpu().numpy() for k, v in adv_sources.items()}
    if wrap:
        assert len(record) == n_steps + 1 and record[-1] == final, (len(record), n_steps)
    return {"record": record, "final": final, "final_sum_bits": float(final_sum.detach().float()), "sources": sources,
            "sources_sha256": hashlib.sha256(b"".join(np.ascontiguousarray(sources[k]).tobytes() for k in sources)).hexdigest(),
            "n_steps": n_steps, "step_size": step_size, "precision": precision, "seconds": time.time() - t0}


def one_minute_checks(model: Any, ids: np.ndarray, start: dict[str, np.ndarray], n_steps: int = 3) -> dict[str, Any]:
    """Section 8.2's two checks: (1) wrapped and unwrapped from the same copied start give bit-identical final harm;
    (2) the start's layout matches the model (asserted in `start_tensors`). Also records peak memory and time per step."""
    import torch

    torch.cuda.reset_peak_memory_stats()
    a = search(model, ids, start, n_steps, STEP_SIZE_C, wrap=True)
    b = search(model, ids, start, n_steps, STEP_SIZE_C, wrap=False)
    return {"n_steps": n_steps, "wrapped_final": a["final"], "unwrapped_final": b["final"],
            "bit_identical_final_harm": a["final_sum_bits"] == b["final_sum_bits"] and a["final"] == b["final"],
            "bit_identical_final_sources": a["sources_sha256"] == b["sources_sha256"],
            "layout": [[k, list(start[k].shape)] for k in start], "layout_matches_model": True,
            "peak_memory_gib": torch.cuda.max_memory_allocated() / 2**30, "seconds_wrapped": a["seconds"], "seconds_unwrapped": b["seconds"],
            "record_wrapped": a["record"]}
