"""Versions (i) and (iii) of the freed-label test, and its stochastic half (plan 6, Section 4, item 7; plan Section 5.4).

The adversarial half: one source shared across a set of 16 texts, all 24 matrices masked, delta components on (the
evaluation adversary's form), our G2-validated loop at constant step 0.1 in float32, run once to 80 steps from shared start
s; the hook keeps the source after 20, 40, and 80 steps (version (i) reads 20; version (iii) reads 40 and 80). The labels
are an arm's: the CQ cache's float32 labels with the arm's freed entries at zero (the override G2 checks).

Per text, as a position mean in nats per token, with each position's KL in float64 from the float32 logits:
  - the adversarial harm of each arm's source at each reading, on the arm's own labels; G = freed minus original, paired
    by seed;
  - J: at the original-label search's source, the freed entries' masks set to 0 (every other mask as at that endpoint,
    the delta masks included), rescored, minus the endpoint's own harm;
  - the stochastic half: masks g + (1 - g) u under uniform-k-subset routing, unrouted matrices at their target weights,
    delta masks uniform, from the keys (master, "stoch", 1, text_id, d) and (master, "routing", 1, text_id, d), d = 0..7,
    the same draw in every arm (`adversary.stochastic_draw`, the construction G2's Section 2.4 checked).
"""

from __future__ import annotations

import time
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A

READINGS = (20, 40, 80)
N_STEPS = 80
STEP = 0.1


def kl64_per_text(logits: Any, target: Any) -> np.ndarray:
    """Per text, the mean over positions of KL(P || Q), float64 from the float32 logits."""
    import torch

    out = []
    for r in range(logits.shape[0]):
        lp = torch.log_softmax(target[r].double(), dim=-1)
        lq = torch.log_softmax(logits[r].double(), dim=-1)
        out.append(float((lp.exp() * (lp - lq)).sum(-1).mean()))
    return np.array(out)


def prepare(model: Any, ids: np.ndarray, labels: dict[str, Any], device: str) -> A.Prepared:
    """Float32 target and weight deltas computed on this batch; the labels given (the cache's)."""
    import torch

    batch = torch.from_numpy(np.asarray(ids).astype(np.int64)).to(device)
    with torch.no_grad():
        wd = model.calc_weight_deltas()
        target = model(batch)
    return A.Prepared(ids=batch, labels=labels, target_out=target, weight_deltas=wd, precision="fp32")


def adv_logits(model: Any, prep: A.Prepared, labels: dict[str, Any], source: dict[str, Any], off: dict[str, Any] | None = None) -> Any:
    """Logits with a shared source's masks built as `_forward_with_adv_sources` builds them, optionally with entries off."""
    import torch

    from param_decomp.metrics.pgd_utils import interpolate_pgd_mask
    from param_decomp.models.components import make_mask_infos

    dev = prep.ids.device
    batch_dims = next(iter(labels.values())).shape[:-1]
    with torch.no_grad():
        src = {k: torch.as_tensor(v).to(dev) for k, v in source.items()}
        expanded = {k: v.expand(*batch_dims, -1) for k, v in src.items()}
        comps = interpolate_pgd_mask(labels, {k: v[..., :-1] for k, v in expanded.items()})
        if off is not None:
            comps = {k: v.masked_fill(off[k], 0.0) for k, v in comps.items()}
        wdm = {k: (prep.weight_deltas[k], expanded[k][..., -1]) for k in prep.weight_deltas}
        return model(prep.ids, mask_infos=make_mask_infos(component_masks=comps, weight_deltas_and_masks=wdm, routing_masks="all"))


def set_job(model: Any, prep: A.Prepared, labels_orig: dict[str, Any], arm_masks: dict[str, dict[str, Any]], starts: dict[int, dict[str, np.ndarray]],
            lay: list[tuple[str, int]], device: str, log: Any = print, tag: str = "") -> dict[str, Any]:
    """One set of texts: for every seed and arm, the 80-step search on the arm's labels, the per-text harm at each reading,
    and J for each freed arm at the original search's sources."""
    from vpd_audit_2 import pilot as P

    out: dict[str, Any] = {"harm": {}, "J": {}, "search_seconds": {}, "records": {}}
    for s, start in starts.items():
        ends = {}
        for name, fmask in arm_masks.items():
            labels = {k: labels_orig[k].masked_fill(fmask[k], 0.0) for k in labels_orig}
            hook = A.SaveHook(steps=READINGS, thresholds=())
            t0 = time.time()
            r = A.run(model, prep, start, N_STEPS, STEP, labels=labels, save_hook=hook, device=device)
            out["search_seconds"][f"{name}|s{s}"] = time.time() - t0
            out["records"][f"{name}|s{s}"] = r["record"]
            for n in READINGS:
                src = P.unflatten(hook.saved[f"step_{n}"], lay)
                out["harm"][f"{name}|s{s}|n{n}"] = kl64_per_text(adv_logits(model, prep, labels, src), prep.target_out).tolist()
                if name == "original":
                    ends[n] = src
        for name, fmask in arm_masks.items():
            if name == "original":
                continue
            for n in READINGS:
                j = kl64_per_text(adv_logits(model, prep, labels_orig, ends[n], off=fmask), prep.target_out)
                out["J"][f"{name}|s{s}|n{n}"] = (j - np.array(out["harm"][f"original|s{s}|n{n}"])).tolist()
        log(f"[b1] {tag} seed {s}: {len(arm_masks)} arms searched")
    return out


def stochastic_job(model: Any, prep: A.Prepared, labels_orig: dict[str, Any], arm_masks: dict[str, dict[str, Any]], text_ids: list[str],
                   n_draws: int, device: str, s_label: int = 1) -> dict[str, Any]:
    """Every arm under each of the draws d = 0..n_draws-1, the same draw in every arm; per-text harm."""
    import torch

    out: dict[str, Any] = {}
    order = list(labels_orig)
    T = int(prep.ids.shape[1])
    m2c = {k: int(v.shape[-1]) for k, v in labels_orig.items()}
    for d in range(n_draws):
        draw = A.stochastic_draw(order, m2c, text_ids, s_label, d, T, routing=True)
        for name, fmask in arm_masks.items():
            labels = {k: labels_orig[k].masked_fill(fmask[k], 0.0) for k in labels_orig}
            with torch.no_grad():
                logits = model(prep.ids, mask_infos=A.stochastic_mask_infos(labels, draw, prep.weight_deltas, device))
            out[f"{name}|d{d}"] = kl64_per_text(logits, prep.target_out).tolist()
        del draw
    return out
