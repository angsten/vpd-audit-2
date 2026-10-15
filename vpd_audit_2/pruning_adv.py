"""Version (ii) of the freed-label test: the paper's pruning adversary (Lena's `sessions/004/notes/lena/version_ii_pruning_adversary.md`;
plan 6, Section 4, item 6).

The search mirrors the authors' `run_adv_pgd` (`param_decomp/app/backend/optim_cis.py:262-304`) line for line:
per-position sources [1, T, C_l] per layer in the labels dict's order, non-alive sources set to 0 before the first step and
after every step, the mask `interpolate_pgd_mask(ci, sources)` through `make_mask_infos` (no weight deltas: the delta
components are excluded), the loss the authors' `compute_recon_loss` with `MeanKLLossConfig` (mean KL over positions,
computed outside the autocast as theirs is), `torch.autograd.grad`, then `add_(step_size * grad.sign())`, `clamp_(0, 1)`,
and the re-zeroing. `DEFAULT_EVAL_PGD_CONFIG` (`compute.py:835`): 4 steps of size 1 from a uniform start.

Differences from theirs, by design: the start and the fill are drawn from explicit generators keyed
(master, "pruning-start", s, text_id) and (master, "pruning-fill", s, text_id), on the CPU in the deciding runs (any
device in the reference check); `alive` (original label > 0) is passed in, computed once per text and shared by every arm;
the forward runs in float32 (question 1's precision) or under bf16 autocast (the reference check); every step's sources
and gradients can be recorded.

Evaluation, per (text, arm, seed), as KL per position in float64 from the float32 logits, averaged over positions:
  - deciding form (`compute_intervention`, `compute.py:974-981`): the searched masks with the non-alive entries filled
    uniformly from the fill draw, the same draw in every arm, one forward;
  - beside it (`optimize_ci_values`' PGD term): the non-alive entries at zero;
  - J: at the original-label arm's endpoint, the freed entries' masks set to 0, rescored in each form.
"""

from __future__ import annotations

import contextlib
from typing import Any

import numpy as np

N_STEPS = 4
STEP_SIZE = 1.0


def autocast(precision: str) -> Any:
    """bf16: the authors' own `bf16_autocast()` (cuda if available, else cpu), as `run_adv_pgd` uses; fp32: none."""
    from param_decomp.utils.general_utils import bf16_autocast

    return bf16_autocast() if precision == "bf16" else contextlib.nullcontext()


def generator(seed: int, device: str) -> Any:
    import torch

    g = torch.Generator(device=device)
    g.manual_seed(seed)
    return g


def draw_start(labels: dict[str, Any], seed: int, gen_device: str = "cpu") -> dict[str, Any]:
    """U[0, 1) per layer in the labels dict's order, shape of the labels, float32, moved to the labels' device."""
    import torch

    g = generator(seed, gen_device)
    return {k: torch.rand(tuple(v.shape), generator=g, device=gen_device, dtype=torch.float32).to(v.device) for k, v in labels.items()}


def draw_fill(alive: dict[str, Any], seed: int, gen_device: str = "cpu") -> dict[str, Any]:
    """Per layer in order, rand(number of non-alive entries), as `compute_intervention` draws its fill."""
    import torch

    g = generator(seed, gen_device)
    out = {}
    for k, a in alive.items():
        n = int((~a).sum().item())
        out[k] = torch.rand(n, generator=g, device=gen_device, dtype=torch.float32).to(a.device)
    return out


def search(model: Any, tokens: Any, ci: dict[str, Any], alive: dict[str, Any], target_out: Any, start: dict[str, Any], precision: str = "fp32",
           n_steps: int = N_STEPS, step_size: float = STEP_SIZE, record: bool = False) -> dict[str, Any]:
    import torch

    from param_decomp.app.backend.optim_cis import MeanKLLossConfig, compute_recon_loss
    from param_decomp.metrics.pgd_utils import interpolate_pgd_mask
    from param_decomp.models.components import make_mask_infos

    ci_detached = {k: v.detach() for k, v in ci.items()}
    adv_sources: dict[str, Any] = {}
    for layer_name in ci_detached:
        source = start[layer_name].clone()
        source[~alive[layer_name]] = 0.0
        source.requires_grad_(True)
        adv_sources[layer_name] = source
    source_list = list(adv_sources.values())
    rec_sources, rec_grads = [], []
    if record:
        rec_sources.append({k: v.detach().clone() for k, v in adv_sources.items()})
    for _ in range(n_steps):
        mask_infos = make_mask_infos(interpolate_pgd_mask(ci_detached, adv_sources))
        with autocast(precision):
            out = model(tokens, mask_infos=mask_infos)
        loss = compute_recon_loss(out, MeanKLLossConfig(), target_out, str(tokens.device))
        grads = torch.autograd.grad(loss, source_list)
        if record:
            rec_grads.append({k: g.detach().clone() for k, g in zip(adv_sources, grads)})
        with torch.no_grad():
            for (layer_name, source), grad in zip(adv_sources.items(), grads, strict=True):
                source.add_(step_size * grad.sign())
                source.clamp_(0.0, 1.0)
                source[~alive[layer_name]] = 0.0
        if record:
            rec_sources.append({k: v.detach().clone() for k, v in adv_sources.items()})
    out = {"sources": {k: v.detach() for k, v in adv_sources.items()}}
    if record:
        out["source_record"], out["grad_record"] = rec_sources, rec_grads
    return out


def masks(ci: dict[str, Any], sources: dict[str, Any], alive: dict[str, Any], fill: dict[str, Any] | None,
          off: dict[str, Any] | None = None) -> dict[str, Any]:
    """The evaluation masks: interpolate(ci, sources); non-alive entries filled (deciding form) or left at zero; the
    entries in `off` (J's freed entries) set to 0."""
    import torch

    from param_decomp.metrics.pgd_utils import interpolate_pgd_mask

    with torch.no_grad():
        m = interpolate_pgd_mask(ci, sources)
        for k in m:
            if fill is not None:
                m[k][~alive[k]] = fill[k]
            if off is not None:
                m[k] = m[k].masked_fill(off[k], 0.0)
    return m


def kl64_mean(logits: Any, target: Any) -> float:
    """Mean over positions of KL(P || Q) per position, float64 from the float32 (or bf16) logits."""
    import torch

    lp = torch.log_softmax(target.double(), dim=-1)
    lq = torch.log_softmax(logits.double(), dim=-1)
    return float((lp.exp() * (lp - lq)).sum(-1).mean())


def evaluate(model: Any, tokens: Any, m: dict[str, Any], target_out: Any, precision: str = "fp32") -> float:
    import torch

    from param_decomp.models.components import make_mask_infos

    with torch.no_grad(), autocast(precision):
        logits = model(tokens, mask_infos=make_mask_infos(m, routing_masks="all"))
    return kl64_mean(logits, target_out)


def text_run(model: Any, tokens: Any, labels_orig: dict[str, Any], arms: dict[str, dict[str, Any]], target_out: Any, start: dict[str, Any],
             fill: dict[str, Any], precision: str = "fp32") -> dict[str, Any]:
    """One text and one seed: every arm's search and both evaluations; J for each freed arm at the original arm's endpoint.
    `arms` maps a name to the arm's freed mask (bool per layer); "original" must be present with an empty mask."""
    alive = {k: v > 0 for k, v in labels_orig.items()}
    out: dict[str, Any] = {"harm": {}, "J": {}}
    ends = {}
    for name, fmask in arms.items():
        ci = {k: labels_orig[k].masked_fill(fmask[k], 0.0) for k in labels_orig}
        r = search(model, tokens, ci, alive, target_out, start, precision)
        ends[name] = (ci, r["sources"])
        out["harm"][name] = {"fill": evaluate(model, tokens, masks(ci, r["sources"], alive, fill), target_out, precision),
                             "zero": evaluate(model, tokens, masks(ci, r["sources"], alive, None), target_out, precision)}
    ci0, r0 = ends["original"]
    for name, fmask in arms.items():
        if name == "original":
            continue
        out["J"][name] = {"fill": evaluate(model, tokens, masks(ci0, r0, alive, fill, off=fmask), target_out, precision) - out["harm"]["original"]["fill"],
                          "zero": evaluate(model, tokens, masks(ci0, r0, alive, None, off=fmask), target_out, precision) - out["harm"]["original"]["zero"]}
    out["G"] = {name: {f: out["harm"][name][f] - out["harm"]["original"][f] for f in ("fill", "zero")} for name in arms if name != "original"}
    return out


# ----------------------------------------------------------------------------- the reference check (Lena's Section 5)


def authors_run(model: Any, tokens: Any, ci: dict[str, Any], alive: dict[str, Any], target_out: Any, seed: int) -> dict[str, Any]:
    """The authors' `run_adv_pgd` with DEFAULT_EVAL_PGD_CONFIG from a seeded global RNG, its sources and gradients
    captured at every step by wrapping the `interpolate_pgd_mask` it calls (the sources it receives) and by tensor hooks
    on those sources (the gradients `torch.autograd.grad` returns)."""
    import torch

    from param_decomp.app.backend import optim_cis
    from param_decomp.app.backend.compute import DEFAULT_EVAL_PGD_CONFIG
    from param_decomp.app.backend.optim_cis import MeanKLLossConfig

    rec_sources: list[dict[str, Any]] = []
    rec_grads: list[dict[str, Any]] = []
    pending: dict[str, Any] = {}
    hooked: set[int] = set()
    original = optim_cis.interpolate_pgd_mask

    def wrapped(ci_: dict[str, Any], adv_sources: dict[str, Any]) -> dict[str, Any]:
        rec_sources.append({k: v.detach().clone() for k, v in adv_sources.items()})
        for name, t in adv_sources.items():
            if id(t) not in hooked:
                hooked.add(id(t))

                def hook(g: Any, _n: str = name, _all: tuple = tuple(adv_sources)) -> None:
                    pending[_n] = g.detach().clone()
                    if len(pending) == len(_all):
                        rec_grads.append({k: pending[k] for k in _all})
                        pending.clear()
                t.register_hook(hook)
        return original(ci_, adv_sources)

    torch.manual_seed(seed)
    optim_cis.interpolate_pgd_mask = wrapped
    try:
        final = optim_cis.run_adv_pgd(model=model, tokens=tokens, ci=ci, alive_masks=alive, adv_config=DEFAULT_EVAL_PGD_CONFIG,
                                      target_out=target_out, loss_config=MeanKLLossConfig())
    finally:
        optim_cis.interpolate_pgd_mask = original
    rec_sources.append({k: v.detach().clone() for k, v in final.items()})
    return {"sources": final, "source_record": rec_sources, "grad_record": rec_grads, "config": DEFAULT_EVAL_PGD_CONFIG.model_dump()}


def authors_fill(adv_masks: dict[str, Any], alive: dict[str, Any], seed: int, device: str) -> dict[str, Any]:
    """`compute_intervention`'s fill (`compute.py:976-979`), from a seeded global RNG, on a copy of the masks."""
    import torch

    torch.manual_seed(seed)
    m = {k: v.clone() for k, v in adv_masks.items()}
    with torch.no_grad():
        for layer in m:
            non_alive = ~alive[layer]
            m[layer][non_alive] = torch.rand(int(non_alive.sum().item()), device=device)
    return m


def _equal(a: dict[str, Any], b: dict[str, Any]) -> bool:
    import torch

    return all(torch.equal(a[k], b[k]) for k in a)


def reference_check(model: Any, tokens: Any, labels_orig: dict[str, Any], freed_mask: dict[str, Any], target_out: Any, seed: int,
                    fill_seed: int) -> dict[str, Any]:
    """Lena's Section 5, bf16 autocast on both sides, on one text. The freed arm's harms (ours and theirs) are returned
    under "sealed" only, never in the "freed" record: beside the original arm they would give the text's G (plan 7)."""
    import torch

    dev = str(tokens.device)
    alive = {k: v > 0 for k, v in labels_orig.items()}
    ci_freed = {k: labels_orig[k].masked_fill(freed_mask[k], 0.0) for k in labels_orig}
    out: dict[str, Any] = {}
    for name, ci in (("freed", ci_freed), ("original", labels_orig)):
        theirs = authors_run(model, tokens, ci, alive, target_out, seed)
        theirs2 = authors_run(model, tokens, ci, alive, target_out, seed)
        ours = search(model, tokens, ci, alive, target_out, draw_start(ci, seed, gen_device=dev), precision="bf16", record=True)
        rec = {"authors_reproducible": all(_equal(a, b) for a, b in zip(theirs["source_record"], theirs2["source_record"]))
               and all(_equal(a, b) for a, b in zip(theirs["grad_record"], theirs2["grad_record"])),
               "start_equal": _equal({k: torch.where(alive[k], v, torch.zeros_like(v)) for k, v in draw_start(ci, seed, gen_device=dev).items()},
                                     theirs["source_record"][0]),
               "sources_equal_each_step": [_equal(a, b) for a, b in zip(ours["source_record"][1:], theirs["source_record"][1:])],
               "grads_equal_each_step": [_equal(a, b) for a, b in zip(ours["grad_record"], theirs["grad_record"])],
               "n_steps": len(ours["grad_record"])}
        rec["passes"] = bool(rec["start_equal"] and all(rec["sources_equal_each_step"]) and all(rec["grads_equal_each_step"])
                             and len(rec["sources_equal_each_step"]) == 4 and len(rec["grads_equal_each_step"]) == 4)
        if name == "freed":
            start_t = theirs["source_record"][0]
            after1 = ours["source_record"][1]
            moved = any(bool((after1[k][freed_mask[k]] != start_t[k][freed_mask[k]]).any()) for k in after1)
            nonalive_zero = all(bool((s[k][~alive[k]] == 0).all()) for s in ours["source_record"] for k in s)
            rec.update({"freed_entries": int(sum(int(m.sum()) for m in freed_mask.values())), "a_freed_entry_moves_after_step_1": moved,
                        "non_alive_sources_zero_every_step": nonalive_zero})
            rec["passes"] = bool(rec["passes"] and moved and nonalive_zero)
            m_theirs = authors_fill(torch_interp(ci_freed, theirs["sources"]), alive, fill_seed, dev)
            m_ours = masks(ci_freed, ours["sources"], alive, draw_fill(alive, fill_seed, gen_device=dev))
            rec["fill_equal"] = _equal(m_ours, m_theirs)
            h_ours = evaluate(model, tokens, m_ours, target_out, "bf16")
            h_theirs = evaluate(model, tokens, m_theirs, target_out, "bf16")
            # a freed-arm harm: sealed (plan 7, item 1). Only the difference and the flag stay in the open record.
            out["sealed"] = {"freed_arm_harm": {"harm_ours": h_ours, "harm_theirs": h_theirs, "precision": "bf16", "form": "fill"}}
            rec["harm_difference_ours_minus_theirs"] = h_ours - h_theirs
            rec["passes"] = bool(rec["passes"] and rec["fill_equal"] and abs(h_ours - h_theirs) <= 1e-5)
        out[name] = rec
    fill = draw_fill(alive, fill_seed, gen_device=dev)
    empty = {k: torch.zeros_like(v) for k, v in freed_mask.items()}
    tr = text_run(model, tokens, labels_orig, {"original": empty, "empty": empty}, target_out, draw_start(labels_orig, seed, gen_device=dev), fill, "bf16")
    out["identity_empty_freed_set"] = {"G": tr["G"]["empty"], "J": tr["J"]["empty"],
                                       "passes": all(v == 0.0 for v in list(tr["G"]["empty"].values()) + list(tr["J"]["empty"].values()))}
    out["passes"] = bool(out["freed"]["passes"] and out["original"]["passes"] and out["identity_empty_freed_set"]["passes"])
    return out


def torch_interp(ci: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    import torch

    from param_decomp.metrics.pgd_utils import interpolate_pgd_mask

    with torch.no_grad():
        return interpolate_pgd_mask(ci, sources)
