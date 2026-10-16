"""Gate G3: precision (the gate specification (research log), Section 3, with the earlier plan 2 of the research log, items 3, 4,
and 13, and plan 3 of the research log, Section 3).

On the 32 calibration texts CQ, per background, the base pass is run at sub-batch size 32 and again at size 1 (32 passes
of one text), with identical masks. With d the logit difference (size 1 minus size 32), P the original model's
next-token distribution and Q the size-32 base pass's, the null effect at each position is
    e = log E_Q[exp(d)] - E_P[d],
evaluated as log1p(sum_i Q_i expm1(d_i)) - sum_i P_i d_i, in float64 after casting the float32 logits (P and Q are the
float64 softmax of the cast logits). The summed null of a text is the sum of e from a position to the end; its value at
position 0 is the floor for a label's summed effect.

Floor per background: the 99th percentile over the 32 texts of |position-0 summed null| (plan 2 of the research log, item 3), with the
maximum and the signed values beside it; per position, the median, 99th percentile, maximum, and fraction negative of e.

Backgrounds (all 24 matrices masked unless stated):
  - all_on: component masks 1, delta masks 1;
  - at_labels: component masks at the labels, delta masks 0;
  - stochastic: masks g + (1 - g) u and uniform delta masks, from key (master, "stoch", 1, text_id, 0) (gating);
  - stochastic_routed (recorded, not gating; plan 2 of the research log, item 4): the same draw under uniform-k-subset routing from
    (master, "routing", 1, text_id, 0), unrouted matrices at their target weights.
Pass, per gating background: the floor lies below pi_5 / 100.

Positive control (plan 2 of the research log, item 13; not gating): per CQ text, a position drawn with seed (master, "g3-control", text_id),
and a component drawn among those whose label is 0 there and whose weight norm ||U_c|| ||V_c|| (the harness's
`weight_norms`) is among the C_l // 10 smallest of its own matrix; its mask set to 0 at that position. Its effect, summed
from that position to the end, at both groupings, against the all-on and stochastic backgrounds. Every |difference| is
reported against that background's floor; any above it holds G3 until it has been read.
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A

GATING = ("all_on", "at_labels", "stochastic")
RECORDED = ("stochastic_routed",)
CONTROL_BACKGROUNDS = ("all_on", "stochastic")


def mask_infos(background: str, prep: A.Prepared, rows: list[int], draw: dict[str, Any] | None, controls: list[dict[str, Any]] | None = None) -> Any:
    import torch

    from param_decomp.models.components import make_mask_infos

    dev = prep.ids.device
    lab = {k: v[rows] for k, v in prep.labels.items()}
    T = lab[next(iter(lab))].shape[1]
    routing: Any = "all"
    if background == "all_on":
        comp = {k: torch.ones_like(v) for k, v in lab.items()}
        dm = {k: torch.ones((len(rows), T), dtype=v.dtype, device=dev) for k, v in lab.items()}
    elif background == "at_labels":
        comp = {k: v.clone() for k, v in lab.items()}
        dm = {k: torch.zeros((len(rows), T), dtype=v.dtype, device=dev) for k, v in lab.items()}
    elif background in ("stochastic", "stochastic_routed"):
        comp = {k: v + (1 - v) * draw["u"][k][rows].to(dev, v.dtype) for k, v in lab.items()}
        dm = {k: draw["delta"][k][rows].to(dev, v.dtype) for k, v in lab.items()}
        if background == "stochastic_routed":
            routing = {k: draw["routing"][k][rows].to(dev) for k in lab}
    else:
        raise ValueError(background)
    if controls:
        pos = {r: i for i, r in enumerate(rows)}
        for c in controls:
            if c["row"] in pos:
                comp[c["module"]][pos[c["row"]], c["position"], c["c"]] = 0.0
    wdm = {k: (prep.weight_deltas[k], dm[k]) for k in lab}
    return make_mask_infos(component_masks=comp, weight_deltas_and_masks=wdm, routing_masks=routing)


def logits(model: Any, prep: A.Prepared, background: str, draw: Any, grouping: int, controls: list[dict[str, Any]] | None = None) -> Any:
    """Float32 logits [32, T, V] of the background's pass, run in sub-batches of `grouping` texts."""
    import torch

    n = prep.n_texts
    outs = []
    with torch.no_grad():
        for a in range(0, n, grouping):
            rows = list(range(a, a + grouping))
            outs.append(model(prep.ids[rows], mask_infos=mask_infos(background, prep, rows, draw, controls)))
    return torch.cat(outs)


def effect(test: Any, base: Any, target: Any) -> Any:
    """Per position e = log1p(sum Q expm1(d)) - sum P d, float64, for one text's [T, V] float32 logits."""
    import torch

    d = test.double() - base.double()
    q = torch.softmax(base.double(), dim=-1)
    p = torch.softmax(target.double(), dim=-1)
    return torch.log1p((q * torch.expm1(d)).sum(-1)) - (p * d).sum(-1)


def per_text_effects(test: Any, base: Any, target: Any) -> np.ndarray:
    return np.stack([effect(test[i], base[i], target[i]).cpu().numpy() for i in range(test.shape[0])])


def floor(e: np.ndarray, line: float) -> dict[str, Any]:
    summed = np.flip(np.cumsum(np.flip(e, axis=1), axis=1), axis=1)
    s0 = summed[:, 0]
    p99 = float(np.percentile(np.abs(s0), 99))
    return {"position0_summed_null": {"p99_abs": p99, "max_abs": float(np.abs(s0).max()), "signed": s0.tolist(),
                                      "signed_p99": float(np.percentile(s0, 99)), "signed_min": float(s0.min()), "signed_max": float(s0.max())},
            "per_position": {"median": float(np.median(e)), "p99": float(np.percentile(e, 99)), "max": float(e.max()), "min": float(e.min()),
                             "fraction_negative": float((e < 0).mean())},
            "line": line, "below_line": bool(p99 < line), "max_below_line": bool(np.abs(s0).max() < line)}


def choose_controls(prep: A.Prepared, text_ids: list[str], norms: np.ndarray, offsets: dict[str, int], module_to_c: dict[str, int]) -> list[dict[str, Any]]:
    from vpd_audit_2.manifest import seed_of

    low = {}
    for k in sorted(module_to_c):
        nk = norms[offsets[k] : offsets[k] + module_to_c[k]]
        low[k] = np.sort(np.argsort(nk, kind="stable")[: max(1, module_to_c[k] // 10)])  # max(1, .) only matters for tiny test models
    T = int(prep.ids.shape[1])
    out = []
    for row, tid in enumerate(text_ids):
        rng = np.random.default_rng(seed_of("g3-control", tid))
        t = int(rng.integers(0, T))
        cands = []
        for k in sorted(module_to_c):
            lab = prep.labels[k][row, t].detach().cpu().numpy()
            for c in low[k]:
                if lab[c] == 0:
                    cands.append((k, int(c)))
        assert cands, f"{tid}: no lowest-decile component with label 0 at position {t}"
        k, c = cands[int(rng.integers(0, len(cands)))]
        out.append({"row": row, "text_id": tid, "position": t, "module": k, "c": c, "global_index": offsets[k] + c,
                    "weight_norm": float(norms[offsets[k] + c]), "candidates": len(cands)})
    return out


def run_g3(model: Any, ids: np.ndarray, text_ids: list[str], line: float, device: str = "cuda", log: Any = print) -> dict[str, Any]:
    import torch

    from vpd_audit.sources import module_offsets
    from vpd_audit.weight_norms import weight_norms

    from param_decomp.models.batch_and_loss_fns import recon_loss_kl

    t0 = time.time()
    prep = A.prepare(model, ids, "fp32", device=device)
    with torch.no_grad():
        target = model(prep.ids)
    order = list(prep.labels)
    draw = A.stochastic_draw(order, model.module_to_c, text_ids, 1, 0, int(prep.ids.shape[1]), routing=True)
    out: dict[str, Any] = {"line_pi5_over_100": line, "texts": text_ids, "backgrounds": {}, "timings_s": {}}
    base = {}
    for bg in GATING + RECORDED:
        t = time.time()
        b32 = logits(model, prep, bg, draw, 32)
        t32 = time.time() - t
        t = time.time()
        b1 = logits(model, prep, bg, draw, 1)
        t1 = time.time() - t
        e = per_text_effects(b1, b32, target)
        with torch.no_grad():
            kl_sum, kl_n = recon_loss_kl(b32, target)
        out["backgrounds"][bg] = {**floor(e, line), "gating": bg in GATING, "base_kl_mean_nats": float(kl_sum) / kl_n}
        out["timings_s"][bg] = {"grouping_32": t32, "grouping_1": t1}
        if bg in CONTROL_BACKGROUNDS:
            base[bg] = (b32, b1)
        else:
            del b32, b1
        log(f"[g3] {bg}: p99 |summed null| {out['backgrounds'][bg]['position0_summed_null']['p99_abs']:.3e} against {line:.3e}")
    norms, nmeta = weight_norms(model)
    controls = choose_controls(prep, text_ids, norms, module_offsets(model.module_to_c), model.module_to_c)
    out["controls"] = {"weight_norms_sha256": nmeta["sha256"], "chosen": controls, "backgrounds": {}}
    for bg in CONTROL_BACKGROUNDS:
        b32, b1 = base[bg]
        t32 = logits(model, prep, bg, draw, 32, controls)
        t1 = logits(model, prep, bg, draw, 1, controls)
        e32 = per_text_effects(t32, b32, target)
        e1 = per_text_effects(t1, b1, target)
        fl = out["backgrounds"][bg]["position0_summed_null"]["p99_abs"]
        rows = []
        for c in controls:
            r, p = c["row"], c["position"]
            s32, s1 = float(e32[r, p:].sum()), float(e1[r, p:].sum())
            rows.append({"text_id": c["text_id"], "effect_grouping_32": s32, "effect_grouping_1": s1, "abs_difference": abs(s32 - s1),
                         "within_floor": abs(s32 - s1) <= fl, "before_position_exact_zero_32": bool((e32[r, :p] == 0).all())})
        out["controls"]["backgrounds"][bg] = {"floor": fl, "rows": rows, "all_within_floor": all(x["within_floor"] for x in rows),
                                              "max_abs_difference": max(x["abs_difference"] for x in rows),
                                              "effects_grouping_32": {"min": min(x["effect_grouping_32"] for x in rows), "median": float(np.median([x["effect_grouping_32"] for x in rows])),
                                                                      "max": max(x["effect_grouping_32"] for x in rows)}}
        del b32, b1, t32, t1
        log(f"[g3] control on {bg}: all within the floor {out['controls']['backgrounds'][bg]['all_within_floor']}")
    gating_pass = {bg: out["backgrounds"][bg]["below_line"] for bg in GATING}
    out["gating"] = gating_pass
    out["controls_within_floor"] = all(v["all_within_floor"] for v in out["controls"]["backgrounds"].values())
    out["passes"] = bool(all(gating_pass.values()) and out["controls_within_floor"])
    out["seconds"] = time.time() - t0
    return out


def _timed_logits(model: Any, prep: A.Prepared, background: str, draw: Any, grouping: int, device: str) -> tuple[Any, float]:
    import torch

    sync = torch.cuda.synchronize if device == "cuda" else (lambda: None)
    sync()
    t = time.time()
    out = logits(model, prep, background, draw, grouping)
    sync()
    return out, time.time() - t


def run_float64_diagnostic(model: Any, ids: np.ndarray, text_ids: list[str], line: float, backgrounds: tuple[str, ...] = ("at_labels", "stochastic"),
                           device: str = "cuda", log: Any = print) -> dict[str, Any]:
    """Report 1 of the research log on plan 3 of the research log, follow-up 1 (a diagnostic, not a remedy): the named backgrounds with float64 forward
    passes, same texts, same null construction (sub-batch 32 against 1), same draws, and the same masks: the labels are the
    float32 labels G3 used (computed once at sub-batch 32), cast to float64; u and the delta masks are the same draw, cast.
    The target, the weight deltas, and every forward pass are float64. The float32 passes are timed beside, with a
    synchronize, for the cost ratio."""
    import torch

    from param_decomp.models.batch_and_loss_fns import recon_loss_kl

    prep32 = A.prepare(model, ids, "fp32", device=device)
    order = list(prep32.labels)
    draw = A.stochastic_draw(order, model.module_to_c, text_ids, 1, 0, int(prep32.ids.shape[1]), routing=True)
    out: dict[str, Any] = {"line_pi5_over_100": line, "texts": text_ids, "float32_timing": {}, "float64": {}}
    for bg in backgrounds:
        _, t32 = _timed_logits(model, prep32, bg, draw, 32, device)
        b32, t32b = _timed_logits(model, prep32, bg, draw, 32, device)
        _, t1 = _timed_logits(model, prep32, bg, draw, 1, device)
        out["float32_timing"][bg] = {"grouping_32_pass_seconds": t32b, "grouping_32_first_pass_seconds": t32, "grouping_1_all_32_passes_seconds": t1}
        del b32
    labels64 = {k: v.double() for k, v in prep32.labels.items()}
    del prep32
    torch.cuda.empty_cache() if device == "cuda" else None
    model.to(torch.float64)
    try:
        batch = torch.from_numpy(np.asarray(ids).astype(np.int64)).to(device)
        with torch.no_grad():
            wd64 = model.calc_weight_deltas()
            target = model(batch)
        prep64 = A.Prepared(ids=batch, labels=labels64, target_out=target, weight_deltas=wd64, precision="fp32")
        assert target.dtype == torch.float64 and next(iter(wd64.values())).dtype == torch.float64
        for bg in backgrounds:
            _, tw = _timed_logits(model, prep64, bg, draw, 32, device)  # warm-up, also timed
            b32, t32 = _timed_logits(model, prep64, bg, draw, 32, device)
            b1, t1 = _timed_logits(model, prep64, bg, draw, 1, device)
            assert b32.dtype == torch.float64
            e = per_text_effects(b1, b32, target)
            with torch.no_grad():
                kl_sum, kl_n = recon_loss_kl(b32, target)
            out["float64"][bg] = {**floor(e, line), "base_kl_mean_nats": float(kl_sum) / kl_n,
                                  "timing": {"grouping_32_pass_seconds": t32, "grouping_32_first_pass_seconds": tw, "grouping_1_all_32_passes_seconds": t1,
                                             "grouping_1_seconds_per_pass": t1 / prep64.n_texts}}
            del b32, b1
            log(f"[g3-f64] {bg}: p99 |summed null| {out['float64'][bg]['position0_summed_null']['p99_abs']:.3e}; "
                f"pass of 32 texts {t32:.3f} s (float32 {out['float32_timing'][bg]['grouping_32_pass_seconds']:.3f} s)")
    finally:
        model.to(torch.float32)
    out["model_restored_to_float32"] = next(model.parameters()).dtype == torch.float32
    return out


def _trace(model: Any, prep: A.Prepared, background: str, draw: Any, rows: list[int], row: int, upto: int) -> dict[str, Any]:
    """One forward of `rows` with forward hooks on every non-decomposed module of the target (norms, attention and MLP
    blocks, blocks, embedding, head), keeping the input and output of `row` (its index in the full batch) at positions
    0..upto. The decomposed linear layers are seen through their parents' outputs, which carry the replaced outputs."""
    import torch

    target_paths = set(model.target_module_paths)
    keep: dict[str, Any] = {}
    handles = []
    idx = rows.index(row)
    for name, mod in model.target_model.named_modules():
        if name == "" or name in target_paths:
            continue

        def hook(m: Any, args: Any, out: Any, _n: str = name) -> None:
            x = args[0] if args and isinstance(args[0], torch.Tensor) else None
            o = out[0] if isinstance(out, tuple) else out
            if isinstance(o, torch.Tensor) and o.dim() >= 2 and o.shape[0] == len(rows):
                keep[_n] = {"out": o[idx, : upto + 1].detach().clone(),
                            "in": x[idx, : upto + 1].detach().clone() if x is not None and x.is_floating_point() and x.shape[0] == len(rows) else None}
        handles.append(mod.register_forward_hook(hook))
    try:
        with torch.no_grad():
            model(prep.ids[rows], mask_infos=mask_infos(background, prep, rows, draw))
    finally:
        for h in handles:
            h.remove()
    return keep


def float64_oddity(model: Any, ids: np.ndarray, text_ids: list[str], backgrounds: tuple[str, ...] = ("at_labels", "stochastic"), top: int = 3,
                   device: str = "cuda", log: Any = print) -> dict[str, Any]:
    """Plan 4 of the research log, D5 (not blocking): at the positions where the float64 null effect is largest, the two groupings' logits
    and every non-decomposed module's input and output compared, in forward order; the first module whose relative
    output difference exceeds 1e-12, and whether the norm layers compute in float32 (their output against a float64
    recomputation of the same formula). Same setup as `run_float64_diagnostic`. Changes nothing."""
    import torch

    prep32 = A.prepare(model, ids, "fp32", device=device)
    order = list(prep32.labels)
    draw = A.stochastic_draw(order, model.module_to_c, text_ids, 1, 0, int(prep32.ids.shape[1]), routing=True)
    labels64 = {k: v.double() for k, v in prep32.labels.items()}
    del prep32
    model.to(torch.float64)
    out: dict[str, Any] = {"backgrounds": {}}
    try:
        batch = torch.from_numpy(np.asarray(ids).astype(np.int64)).to(device)
        with torch.no_grad():
            wd64 = model.calc_weight_deltas()
            target = model(batch)
        prep = A.Prepared(ids=batch, labels=labels64, target_out=target, weight_deltas=wd64, precision="fp32")
        n = prep.n_texts
        for bg in backgrounds:
            b32 = logits(model, prep, bg, draw, 32)
            b1 = logits(model, prep, bg, draw, 1)
            e = per_text_effects(b1, b32, target)
            flat = np.argsort(-np.abs(e), axis=None)[:top]
            rows_out = []
            for fi in flat:
                r, t = divmod(int(fi), e.shape[1])
                d = (b1[r, t] - b32[r, t]).double()
                q = torch.softmax(b32[r, t].double(), -1)
                j = int(torch.argmax(d.abs()))
                t32 = _trace(model, prep, bg, draw, list(range(n)), r, t)
                t1 = _trace(model, prep, bg, draw, [r], r, t)
                mods = []
                for name in t32:
                    if name not in t1:
                        continue
                    o32, o1 = t32[name]["out"], t1[name]["out"]
                    scale = float(o32.abs().max()) or 1.0
                    rec = {"module": name, "out_dtype": str(o32.dtype), "max_abs_diff": float((o32 - o1).abs().max()), "relative": float((o32 - o1).abs().max()) / scale}
                    i32, i1 = t32[name]["in"], t1[name]["in"]
                    if i32 is not None and i1 is not None:
                        rec["in_relative"] = float((i32 - i1).abs().max()) / (float(i32.abs().max()) or 1.0)
                    mods.append(rec)
                first = next((m for m in mods if m["relative"] > 1e-12), None)
                norms = {}
                for name, mod in model.target_model.named_modules():
                    if type(mod).__name__ == "LlamaRMSNorm" and name in t32 and t32[name]["in"] is not None:
                        x = t32[name]["in"].double()
                        exact = mod.weight * (x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + mod.variance_epsilon))
                        got = t32[name]["out"]
                        rec = {"max_relative_difference_from_float64_formula": float((got - exact).abs().max() / exact.abs().max()),
                               "output_relative_difference_between_groupings": float((t32[name]["out"] - t1[name]["out"]).abs().max() / t32[name]["out"].abs().max())}
                        if t1.get(name, {}).get("in") is not None:
                            rec["input_relative_difference_between_groupings"] = float((t32[name]["in"] - t1[name]["in"]).abs().max() / t32[name]["in"].abs().max())
                        norms[name] = rec
                rows_out.append({"text_id": text_ids[r], "row": r, "position": t, "e": float(e[r, t]), "max_abs_d": float(d.abs().max()), "token_of_max_d": j,
                                 "logit_at_that_token_32": float(b32[r, t, j]), "q_at_that_token": float(q[j]), "max_abs_logit": float(b32[r, t].abs().max()),
                                 "first_module_over_1e-12": first, "modules_in_forward_order": mods, "rms_norms": norms})
                log(f"[d5] {bg} {text_ids[r]} pos {t}: e {e[r, t]:.3e}, max |d| {float(d.abs().max()):.3e}; first module over 1e-12: "
                    f"{first['module'] if first else None}")
            out["backgrounds"][bg] = {"top_positions": rows_out, "per_position_quantiles": {
                "p50": float(np.percentile(e, 50)), "p99": float(np.percentile(e, 99)), "p99.9": float(np.percentile(e, 99.9)), "max": float(e.max())},
                "positions_above_1e-12": int((np.abs(e) > 1e-12).sum()), "positions": int(e.size)}
            del b32, b1
    finally:
        model.to(torch.float32)
    out["model_restored_to_float32"] = next(model.parameters()).dtype == torch.float32
    return out


def run_all_on_float64(model: Any, ids: np.ndarray, line: float, device: str = "cuda") -> dict[str, Any]:
    """The fallback (Section 3.3): the all-on background with float64 forward passes; reports the forward time on CQ."""
    import torch

    model64 = model.to(torch.float64)
    prep = A.prepare(model64, ids, "fp32", device=device)
    sync = torch.cuda.synchronize if device == "cuda" else (lambda: None)
    with torch.no_grad():
        target = model64(prep.ids)
    sync()
    t = time.time()
    b32 = logits(model64, prep, "all_on", None, 32)
    sync()
    t32 = time.time() - t
    b1 = logits(model64, prep, "all_on", None, 1)
    e = per_text_effects(b1, b32, target)
    model.to(torch.float32)
    return {**floor(e, line), "dtype": "float64", "forward_seconds_grouping_32_on_CQ": t32}
