"""Gate G2: our adversary loop (`adversary.py`) against the authors' (the gate specification (research log),
Sections 2.2 to 2.4, with the earlier plan 3 of the research log, Section 3, and the earlier plans 1 to 3 of the research log).

The authors' side is `_run_pgd_loop(adv_sources, PGDConfig(...), fwd)` with `fwd = functools.partial(_forward_with_adv_sources,
...)` built as `pgd_masked_recon_loss_update` builds it (`pgd_utils.py:95-126`), from a copy of the saved start. A wrapper
around `fwd` records, at each forward, `float(sum_loss.detach()) / n_examples` and a copy of the sources, and returns the
loop's own tensors. The authors' gradients are captured by tensor hooks on their source tensors: `torch.autograd.grad`
runs a leaf's hooks with the gradient it returns, and the hook returns None, so the gradient is unchanged.

Setting: batch C1 (128 texts), start (master, "start", 1), float32, no autocast, deterministic algorithms, one process;
labels, target, and float32 weight deltas computed once under no_grad and shared by both loops; delta components on;
routing all 24 matrices; step size 0.1; 20 steps.
"""

from __future__ import annotations

import functools
import time
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A

STEP = 0.1
N_STEPS = 20
HARM_TOL = 1e-5
MB_RATIO = 1e-4
MB_SHARE = 0.001


def authors_loop(model: Any, prep: A.Prepared, start: dict[str, np.ndarray], n_steps: int, step_size: float = STEP, *, with_delta: bool = True,
                 delta_value: float | None = None, capture_grads: bool = True, device: str = "cuda") -> dict[str, Any]:
    """The authors' `_run_pgd_loop` from a copy of the start. `with_delta=False` runs their weight_deltas=None path with the
    start's delta entries dropped. `delta_value` overwrites the start's delta entries (the frozen-at-1 check)."""
    import torch

    from param_decomp.configs import PGDConfig
    from param_decomp.metrics.pgd_utils import _forward_with_adv_sources, _run_pgd_loop
    from param_decomp.models.batch_and_loss_fns import recon_loss_kl
    from param_decomp.routing import AllLayersRouter

    t0 = time.time()
    st = {k: v.copy() for k, v in start.items()}
    if delta_value is not None:
        for v in st.values():
            v[..., -1] = delta_value
    record: list[float] = []
    sources_rec: list[np.ndarray] = []
    grads_rec: list[np.ndarray] = []
    pending: dict[str, Any] = {}
    with torch.no_grad(), A.autocast_ctx(prep.precision):
        batch_dims = next(iter(prep.labels.values())).shape[:-1]
        routing_masks = AllLayersRouter().get_masks(module_names=model.target_module_paths, mask_shape=batch_dims)
        adv_sources = A.start_tensors(st, model, device, with_delta=with_delta)
        wd = prep.weight_deltas if with_delta else None
        fwd = functools.partial(_forward_with_adv_sources, model=model, batch=prep.ids, adv_sources=adv_sources, ci=prep.labels, weight_deltas=wd,
                                routing_masks=routing_masks, target_out=prep.target_out, batch_dims=batch_dims, reconstruction_loss=recon_loss_kl)
        handles = []
        if capture_grads:
            for name, t in adv_sources.items():
                def hook(g: Any, _name: str = name) -> None:
                    pending[_name] = g.detach().clone()
                    if len(pending) == len(adv_sources):
                        grads_rec.append(A.flatten({k: pending[k] for k in adv_sources}))
                        pending.clear()
                handles.append(t.register_hook(hook))

        def recorded() -> tuple[Any, int]:
            sources_rec.append(A.flatten(adv_sources))
            sum_loss, n_examples = fwd()
            record.append(float(sum_loss.detach()) / n_examples)
            return sum_loss, n_examples

        cfg = PGDConfig(init="random", step_size=step_size, n_steps=n_steps, mask_scope="shared_across_batch")
        final_sum, final_n = _run_pgd_loop(adv_sources, cfg, recorded)
        for h in handles:
            h.remove()
    torch.cuda.synchronize() if device == "cuda" else None
    assert len(record) == n_steps + 1 and record[-1] == float(final_sum.detach()) / final_n
    out = {"record": record, "final": record[-1], "source_record": np.stack(sources_rec),
           "sources": {k: v.detach().float().cpu().numpy() for k, v in adv_sources.items()}, "seconds": time.time() - t0}
    if capture_grads:
        assert len(grads_rec) == n_steps, (len(grads_rec), n_steps)
        out["grad_record"] = np.stack(grads_rec)
    return out


def compare_runs(a: dict[str, Any], b: dict[str, Any], entries: slice | np.ndarray | None = None) -> dict[str, Any]:
    """Per step k = 0..n: whether the sources are bitwise equal (optionally on chosen entries), the number of entries
    that differ, and the harm difference."""
    sa, sb = a["source_record"], b["source_record"]
    if entries is not None:
        sa, sb = sa[:, entries], sb[:, entries]
    assert sa.shape == sb.shape, (sa.shape, sb.shape)
    differ = [int((sa[k].view(np.uint32) != sb[k].view(np.uint32)).sum()) for k in range(sa.shape[0])]
    dh = [abs(x - y) for x, y in zip(a["record"], b["record"])]
    return {"steps": len(differ) - 1, "sources_bitwise_equal_every_step": all(d == 0 for d in differ), "entries_differing_per_step": differ,
            "harm_bitwise_equal_every_step": all(x == y for x, y in zip(a["record"], b["record"])), "abs_harm_difference_per_step": dh,
            "max_abs_harm_difference": max(dh)}


def delta_positions(model: Any) -> np.ndarray:
    """Indices of the delta entries in the flattened [C_l + 1]-per-module layout."""
    pos, off = [], 0
    for k in model.target_module_paths:
        off += model.module_to_c[k] + 1
        pos.append(off - 1)
    return np.array(pos)


def component_positions(model: Any) -> np.ndarray:
    mask = np.ones(sum(model.module_to_c[k] + 1 for k in model.target_module_paths), dtype=bool)
    mask[delta_positions(model)] = False
    return np.flatnonzero(mask)


def module_slices(model: Any) -> list[tuple[str, int, int]]:
    out, off = [], 0
    for k in model.target_module_paths:
        n = model.module_to_c[k] + 1
        out.append((k, off, off + n))
        off += n
    return out


def sign_comparison(g_whole: np.ndarray, g_micro: np.ndarray, model: Any) -> dict[str, Any]:
    """Plan 1 of the research log, item 4: entries whose sign differs between the whole-batch and micro-batched gradients at the same source;
    for each, |g_whole| over the median nonzero |g_whole| of its module."""
    diff = np.sign(g_whole) != np.sign(g_micro)
    ratios = []
    for _, a, b in module_slices(model):
        mag = np.abs(g_whole[a:b])
        nz = mag[mag > 0]
        med = float(np.median(nz)) if nz.size else np.inf
        d = np.flatnonzero(diff[a:b])
        ratios.extend((mag[d] / med).tolist())
    n = int(diff.sum())
    return {"n_differing": n, "share": n / diff.size, "max_ratio": float(max(ratios)) if ratios else 0.0,
            "passes": bool(n < MB_SHARE * diff.size and all(r < MB_RATIO for r in ratios))}


def micro_validation(model: Any, prep: A.Prepared, start: dict[str, np.ndarray], sizes: tuple[int, ...] = (8, 16), n_steps: int = N_STEPS,
                     device: str = "cuda") -> dict[str, Any]:
    """Plan 1 of the research log, item 4: the whole-batch path for n_steps; at each step, the micro-batched gradient at the whole-batch path's
    source for that step (both sizes), compared sign by sign with the whole-batch gradient."""
    probes: dict[int, list[np.ndarray]] = {m: [] for m in sizes}

    def probe(k: int, sources: dict[str, Any]) -> None:
        for m in sizes:
            _, g = A.loss_and_grad(model, prep, sources, None, m)
            probes[m].append(A.flatten(dict(zip(sources, g))))
            del g

    whole = A.run(model, prep, start, n_steps, STEP, record_grads=True, record_sources=True, device=device, grad_probe=probe)
    out = {"whole_batch_record": whole["record"], "sizes": {}}
    for m in sizes:
        steps = [sign_comparison(whole["grad_record"][k], probes[m][k], model) for k in range(n_steps)]
        out["sizes"][str(m)] = {"per_step": steps, "n_differing_per_step": [s["n_differing"] for s in steps],
                                "largest_ratio": max(s["max_ratio"] for s in steps), "passes": all(s["passes"] for s in steps)}
    out["rule"] = ("at every step, every entry whose sign differs has |g_whole| below 1e-4 of its module's median nonzero |g_whole|, "
                   "and such entries are fewer than 0.1 percent of all entries")
    out["passes"] = all(v["passes"] for v in out["sizes"].values())
    return out, whole


def stochastic_reference(model: Any, prep: A.Prepared, text_ids: list[str], rows: list[int], s: int, draw: int) -> dict[str, Any]:
    """Section 2.4: per text, the authors' `calc_stochastic_component_mask_info` on the CPU with the global RNG seeded from
    the stoch key, and a Router that hands the routing generator to the authors' `sample_uniform_k_subset_routing_masks`
    (and changes nothing else); against our `stochastic_draw` + `stochastic_mask_infos`. Masks compared bitwise; harm
    from one forward of each set of masks on the same texts."""
    import torch

    from vpd_audit_2.manifest import seed_of

    from param_decomp.models.batch_and_loss_fns import recon_loss_kl
    from param_decomp.models.components import make_mask_infos
    from param_decomp.routing import Router, sample_uniform_k_subset_routing_masks
    from param_decomp.utils.component_utils import calc_stochastic_component_mask_info

    class GeneratorRouter(Router):
        def __init__(self, generator: Any):
            self.generator = generator

        def get_masks(self, module_names: list[str], mask_shape: tuple[int, ...]) -> dict[str, Any]:
            return sample_uniform_k_subset_routing_masks(mask_shape, module_names, "cpu", generator=self.generator)

    device = prep.ids.device
    order = list(prep.labels)
    T = int(prep.ids.shape[1])
    labels = {k: v[rows] for k, v in prep.labels.items()}
    ours_draw = A.stochastic_draw(order, model.module_to_c, text_ids, s, draw, T, routing=True)
    ours = A.stochastic_mask_infos(labels, ours_draw, prep.weight_deltas, str(device))
    theirs_parts = []
    state = torch.random.get_rng_state()
    for r, tid in zip(rows, text_ids):
        ci_cpu = {k: v[r : r + 1].detach().cpu() for k, v in prep.labels.items()}
        torch.manual_seed(seed_of("stoch", s, tid, draw))
        g_route = torch.Generator(device="cpu")
        g_route.manual_seed(seed_of("routing", s, tid, draw))
        theirs_parts.append(calc_stochastic_component_mask_info(causal_importances=ci_cpu, component_mask_sampling="continuous",
                                                                weight_deltas=prep.weight_deltas, router=GeneratorRouter(g_route)))
    torch.random.set_rng_state(state)
    eq = {"component_masks": True, "delta_masks": True, "routing_masks": True}
    for k in order:
        tc = torch.cat([p[k].component_mask for p in theirs_parts]).to(device)
        td = torch.cat([p[k].weight_delta_and_mask[1] for p in theirs_parts]).to(device)
        tr = torch.cat([p[k].routing_mask for p in theirs_parts]).to(device)
        eq["component_masks"] &= bool(torch.equal(tc, ours[k].component_mask))
        eq["delta_masks"] &= bool(torch.equal(td, ours[k].weight_delta_and_mask[1]))
        eq["routing_masks"] &= bool(torch.equal(tr, ours[k].routing_mask))
    theirs = make_mask_infos(component_masks={k: torch.cat([p[k].component_mask for p in theirs_parts]).to(device) for k in order},
                             weight_deltas_and_masks={k: (prep.weight_deltas[k], torch.cat([p[k].weight_delta_and_mask[1] for p in theirs_parts]).to(device)) for k in order},
                             routing_masks={k: torch.cat([p[k].routing_mask for p in theirs_parts]).to(device) for k in order})
    with torch.no_grad(), A.autocast_ctx(prep.precision):
        h_ours = recon_loss_kl(model(prep.ids[rows], mask_infos=ours), prep.target_out[rows])
        h_theirs = recon_loss_kl(model(prep.ids[rows], mask_infos=theirs), prep.target_out[rows])
    ho, ht = float(h_ours[0]) / h_ours[1], float(h_theirs[0]) / h_theirs[1]
    return {"texts": text_ids, "masks_bitwise_equal": eq, "harm_ours": ho, "harm_authors": ht, "harm_bitwise_equal": ho == ht,
            "passes": all(eq.values()) and ho == ht, "draw": ours_draw, "mask_infos": ours, "harm_rows": rows,
            "draw_order": ("per text: stoch generator (master, 'stoch', s, text_id, draw): rand((T, C_l)) for each module in the labels "
                           "dict's order, then rand((T,)) for each module; routing generator (master, 'routing', s, text_id, draw): the "
                           "authors' sample_uniform_k_subset_routing_masks((T,), modules, 'cpu', generator): randint, then rand-argsort")}


def reload_check(model: Any, prep: A.Prepared, ref: dict[str, Any], path: Any) -> dict[str, Any]:
    """Saved draws: the draw saved and reloaded gives bitwise-identical masks and harm."""
    import torch

    from param_decomp.models.batch_and_loss_fns import recon_loss_kl

    A.save_draw(ref["draw"], path)
    loaded = A.load_draw(path)
    rows = ref["harm_rows"]
    labels = {k: v[rows] for k, v in prep.labels.items()}
    infos = A.stochastic_mask_infos(labels, loaded, prep.weight_deltas, str(prep.ids.device))
    eq = all(bool(torch.equal(infos[k].component_mask, ref["mask_infos"][k].component_mask))
             and bool(torch.equal(infos[k].weight_delta_and_mask[1], ref["mask_infos"][k].weight_delta_and_mask[1]))
             and bool(torch.equal(infos[k].routing_mask, ref["mask_infos"][k].routing_mask)) for k in labels)
    with torch.no_grad(), A.autocast_ctx(prep.precision):
        h = recon_loss_kl(model(prep.ids[rows], mask_infos=infos), prep.target_out[rows])
    hv = float(h[0]) / h[1]
    return {"masks_bitwise_equal": eq, "harm": hv, "harm_bitwise_equal": hv == ref["harm_ours"], "passes": bool(eq and hv == ref["harm_ours"])}


def entries_at_bounds(sources: dict[str, np.ndarray]) -> dict[str, int]:
    flat = np.concatenate([v.reshape(-1) for v in sources.values()])
    return {"at_0": int((flat == 0).sum()), "at_1": int((flat == 1).sum()), "strictly_between": int(((flat > 0) & (flat < 1)).sum()), "total": int(flat.size)}


def protocol(model: Any, ids: np.ndarray, text_ids: list[str], start: dict[str, np.ndarray], device: str = "cuda", draw_path: Any = None,
             log: Any = print) -> dict[str, Any]:
    """G2 on one batch: step 0 (the authors' reproducibility), steps 1 to 3, the feature checks of Section 2.2, the
    micro-batch validation (plan 1 of the research log, item 4; sizes 8 and 16), the stochastic routing check of Section 2.4 and the reload
    check on the first 4 texts, and the records Section 2.3 asks for."""
    import torch

    t0 = time.time()
    prep = A.prepare(model, ids, "fp32", device=device)
    out: dict[str, Any] = {"texts": len(text_ids), "precision": "float32, no autocast; weight deltas float32", "step_size": STEP, "n_steps": N_STEPS}
    comp, dpos = component_positions(model), delta_positions(model)

    a = authors_loop(model, prep, start, N_STEPS, device=device)
    b = authors_loop(model, prep, start, N_STEPS, device=device)
    s0 = compare_runs(a, b)
    s0["gradients_bitwise_equal_every_step"] = bool(np.array_equal(a["grad_record"].view(np.uint32), b["grad_record"].view(np.uint32)))
    reproducible = s0["sources_bitwise_equal_every_step"] and s0["harm_bitwise_equal_every_step"]
    s0["bitwise_reproducible"] = reproducible
    out["step0"] = s0
    if reproducible:
        crit = {"name": "bitwise", "harm_tol": HARM_TOL, "entries_tol": 0,
                "rule": "sources bitwise equal at every step, and harm within 1e-5 nats at every step"}
    else:
        crit = {"name": "self-calibrated", "harm_tol": s0["max_abs_harm_difference"], "entries_tol": max(s0["entries_differing_per_step"]),
                "rule": "harm within the largest difference of the authors' two runs, and no more differing entries than they show"}
    out["criterion"] = crit
    log(f"[g2] step 0: reproducible {reproducible}; criterion {crit['name']}")

    def judge(c: dict[str, Any]) -> bool:
        return bool(max(c["entries_differing_per_step"]) <= crit["entries_tol"] and c["max_abs_harm_difference"] <= crit["harm_tol"])

    a1 = authors_loop(model, prep, start, 1, device=device)
    o1 = A.run(model, prep, start, 1, STEP, record_sources=True, device=device)
    c1 = compare_runs(a1, o1)
    out["step1"] = {**c1, "rule": "after one update, every source entry (delta included) and the harm bitwise equal",
                    "passes": bool(c1["entries_differing_per_step"][1] == 0 and a1["record"][1] == o1["record"][1])}

    ours = A.run(model, prep, start, N_STEPS, STEP, record_sources=True, record_grads=True, device=device)
    c2 = compare_runs(a, ours)
    out["step2"] = {**c2, "passes": judge(c2)}
    out["per_entry_gradients"] = {"bitwise_equal_every_step": bool(np.array_equal(a["grad_record"].view(np.uint32), ours["grad_record"].view(np.uint32))),
                                  "grad_sum_equals_sum_of_steps": bool(np.allclose(ours["grad_sum"], ours["grad_record"].astype(np.float64).sum(0), rtol=1e-12, atol=0))}
    log(f"[g2] steps 1 and 2: {out['step1']['passes']}, {out['step2']['passes']}; gradients bitwise {out['per_entry_gradients']['bitwise_equal_every_step']}")

    a0 = authors_loop(model, prep, start, N_STEPS, with_delta=False, capture_grads=False, device=device)
    f0 = A.run(model, prep, start, N_STEPS, STEP, frozen=A.Frozen.delta_entries(model, 0.0, device), record_sources=True, device=device)
    c3 = compare_runs(a0, {**f0, "source_record": f0["source_record"][:, comp]})
    out["step3"] = {**c3, "delta_entries_at_0_every_step": bool((f0["source_record"][:, dpos] == 0).all()), "passes": judge(c3)}
    out["step3"]["passes"] = bool(out["step3"]["passes"] and out["step3"]["delta_entries_at_0_every_step"])

    a_one = authors_loop(model, prep, start, 1, delta_value=1.0, capture_grads=False, device=device)
    f_one = A.run(model, prep, start, 1, STEP, frozen=A.Frozen.delta_entries(model, 1.0, device), record_sources=True, device=device)
    f_long = A.run(model, prep, start, N_STEPS, STEP, frozen=A.Frozen.delta_entries(model, 1.0, device), record_sources=True, record_grads=True, device=device)
    rule_ok = []
    for k in range(N_STEPS):
        s, g = f_long["source_record"][k][comp], f_long["grad_record"][k][comp]
        expect = np.clip(s + np.float32(STEP) * np.sign(g).astype(np.float32), np.float32(0), np.float32(1))
        rule_ok.append(bool(np.array_equal(expect, f_long["source_record"][k + 1][comp])))
    out["frozen_at_1"] = {"one_step_component_entries_bitwise_equal": bool(np.array_equal(a_one["source_record"][1][comp].view(np.uint32),
                                                                                       f_one["source_record"][1][comp].view(np.uint32))),
                          "authors_delta_entries_after_one_step": a_one["source_record"][1][dpos].tolist(),
                          "frozen_entries_unchanged_20_steps": bool((f_long["source_record"][:, dpos] == 1).all()),
                          "others_follow_the_sign_rule_every_step": all(rule_ok), "steps_following_the_rule": int(sum(rule_ok))}
    out["frozen_at_1"]["passes"] = bool(out["frozen_at_1"]["one_step_component_entries_bitwise_equal"] and out["frozen_at_1"]["frozen_entries_unchanged_20_steps"]
                                        and out["frozen_at_1"]["others_follow_the_sign_rule_every_step"])

    plain = A.run(model, prep, start, 3, STEP, record_sources=True, device=device)
    override = A.run(model, prep, start, 3, STEP, labels={k: v.clone() for k, v in prep.labels.items()}, record_sources=True, device=device)
    empty = A.run(model, prep, start, 3, STEP, frozen=A.Frozen.empty(model, device), record_sources=True, device=device)
    held = A.score(model, ours["sources"], A.prepare(model, ids, "fp32", device=device), device=device)
    co, ce = compare_runs(plain, override), compare_runs(plain, empty)
    k0 = model.target_module_paths[0]
    lab = {k: v.clone() for k, v in prep.labels.items()}
    lab[k0][0, :8, :] = 0.0
    from param_decomp.metrics.pgd_utils import _construct_mask_infos_from_adv_sources

    srcs = A.start_tensors(start, model, device)
    with torch.no_grad():
        infos = _construct_mask_infos_from_adv_sources(srcs, lab, prep.weight_deltas, "all", lab[k0].shape[:-1])
        r = srcs[k0][..., :-1].expand(*lab[k0].shape[:-1], -1)
        unit = bool(torch.equal(infos[k0].component_mask, lab[k0] + (1 - lab[k0]) * r))
    del infos, lab, srcs
    out["identity"] = {"label_override_equal_to_the_labels_3_steps": bool(co["sources_bitwise_equal_every_step"] and co["harm_bitwise_equal_every_step"]),
                       "frozen_set_empty_3_steps": bool(ce["sources_bitwise_equal_every_step"] and ce["harm_bitwise_equal_every_step"]),
                       "held_out_scoring_of_C1_equals_the_final_harm": held == ours["final"], "held_out_score": held,
                       "mask_with_zeroed_labels_equals_g_plus_1_minus_g_r": unit}
    out["identity"]["passes"] = all(v for k, v in out["identity"].items() if isinstance(v, bool))
    log(f"[g2] step 3 {out['step3']['passes']}; frozen at 1 {out['frozen_at_1']['passes']}; identity {out['identity']['passes']}")

    mv, whole = micro_validation(model, prep, start, (8, 16), N_STEPS, device=device)
    mv["whole_path_equals_step2_run"] = whole["record"] == ours["record"]
    indep = {str(m): A.run(model, prep, start, N_STEPS, STEP, micro_batch=m, record_sources=True, device=device) for m in (8, 16)}
    mv["independent_trajectories"] = {m: {"record": r["record"], "entries_differing_from_whole_per_step":
                                          [int((r["source_record"][k] != ours["source_record"][k]).sum()) for k in range(N_STEPS + 1)],
                                          "seconds": r["seconds"]} for m, r in indep.items()}
    out["micro_batch_validation"] = mv
    log(f"[g2] micro-batch validation: {mv['passes']} ({ {m: v['n_differing_per_step'] for m, v in mv['sizes'].items()} })")

    rows = [0, 1, 2, 3]
    ref = stochastic_reference(model, prep, text_ids[:4], rows, 1, 0)
    out["stochastic_routing_2_4"] = {k: v for k, v in ref.items() if k not in ("draw", "mask_infos")}
    out["saved_draw_reload"] = reload_check(model, prep, ref, draw_path) if draw_path is not None else {"passes": False, "note": "no path"}
    log(f"[g2] 2.4: {ref['passes']}; reload {out['saved_draw_reload']['passes']}")

    out["records"] = {"authors_record": a["record"], "ours_record": ours["record"], "frozen0_record": f0["record"], "authors_no_delta_record": a0["record"],
                      "entries_after_20_steps": entries_at_bounds(ours["sources"]), "seconds": {"authors_20": a["seconds"], "ours_20": ours["seconds"]}}
    out["passes"] = bool(out["step1"]["passes"] and out["step2"]["passes"] and out["step3"]["passes"] and mv["passes"] and ref["passes"]
                         and out["saved_draw_reload"]["passes"] and out["per_entry_gradients"]["bitwise_equal_every_step"]
                         and out["frozen_at_1"]["passes"] and out["identity"]["passes"])
    out["seconds"] = time.time() - t0
    return out
