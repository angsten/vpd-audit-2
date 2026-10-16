"""Plan 5 of the research log: probe 1's computation (the probe's specification (research log), Sections 1 and 2, with the six
amendments of plan 5 of the research log). No GPU is assumed; the container calls these on a B200, the tests on
the tiny model.

Notation. A setting is flat: C_l + 1 float32 entries per module in the layout's order, the delta entry last. Its rounded
pattern is every entry rounded to 0 below one half and to 1 otherwise (`s6_build.rounded`), one source shared by every
text and position. Through the authors' `_construct_mask_infos_from_adv_sources` a component's mask is l + r (1 - l), l
its label and r its source, and a delta entry's mask is r itself.

The move. Entry e's move on text x is scaled by a[x, e], and its source is r = 1 - a. So a = 0 everywhere is the intact
model (every mask 1, the target model), and a = 1 moves a component's mask to its label (to 0 where the label is 0) and a
delta entry's mask to 0: the specification's move "from mask 1 to its pattern value" for every entry the pattern switches off.
The move is the same for every setting, so one backward pass gives every entry's push, kept components and delta entries
included (amendment 1). The full pattern is the point a = 1 on the entries it switches off and 0 elsewhere; its sources
are exactly the rounded setting.

  - `reference_direction`: Delta(x, t) = z_pattern - z_intact, centred over the vocabulary, scaled to unit length at each
    position. A position where it is exactly zero gets a zero direction and is counted.
  - `first_order_pushes`: p_e(x) = sum_t <dz(x, t) / da_e, Delta_hat(x, t)> for every entry, from one forward pass with
    the scales as leaves and one backward pass (a vector-Jacobian product with Delta_hat), at the intact model and, as the
    specification's description, at the full pattern. Texts do not interact, so text x's scale moves only text x's logits.
    `IntactGraph` keeps the intact forward so that several settings on one batch each cost one pattern forward and one
    backward: the Jacobian at a = 0 does not depend on the setting.
  - `exact_pushes`: for listed (entry, text) pairs, the exact one-at-a-time move at the intact model,
    sum_t <z(a_e = 1, every other a 0) - z_intact, Delta_hat>. Each pair is its own row of a forward pass; every chunk of
    rows also carries a null row (a = 0) for each of its texts, and a pair's push is taken against the null row of its own
    chunk, so that both logits come from the same kernels.

Sign: a positive push means switching the entry off pushes the output along the full pattern's shift. The push of a
component while it is on, which the figure draws, is the negative (amendment 6).

Everything here runs in the batch's dtype without autocast. The container hands it float32: the labels of the run's own
preparation (checked against the run's fingerprint by the caller) cast to float32, and the weight deltas recomputed in
float32 (`as_float32_batch`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

POINTS = ("intact", "pattern")
PASS_SIGN_SHARE = 0.90  # the specification's Section 2: the first-order sign matches the exact one for at least 90 percent
PASS_SPEARMAN = 0.80  # ... and the Spearman correlation is at least 0.8
VALIDATION_DECILES = 10
VALIDATION_PER_DECILE = 20  # 200 components
VALIDATION_TEXTS = 8


# ----------------------------------------------------------------------------- the layout


def n_entries(lay: list[tuple[str, int]]) -> int:
    return sum(c + 1 for _, c in lay)


def module_offsets(lay: list[tuple[str, int]]) -> np.ndarray:
    """Where each module's first entry sits in the flat layout."""
    return np.concatenate([[0], np.cumsum([c + 1 for _, c in lay])[:-1]]).astype(np.int64)


def delta_positions(lay: list[tuple[str, int]]) -> np.ndarray:
    return np.cumsum([c + 1 for _, c in lay]).astype(np.int64) - 1


def component_positions(lay: list[tuple[str, int]]) -> np.ndarray:
    out = np.ones(n_entries(lay), dtype=bool)
    out[delta_positions(lay)] = False
    return np.flatnonzero(out)


def entry_of(flat: int, lay: list[tuple[str, int]]) -> tuple[str, int]:
    """The module and the index within it (C_l for the delta entry) of a flat entry."""
    off = 0
    for name, c in lay:
        if flat < off + c + 1:
            return name, int(flat - off)
        off += c + 1
    raise IndexError(flat)


def rounded(flat: np.ndarray) -> np.ndarray:
    """`s6_build.rounded`: every entry to 0 below one half and to 1 otherwise."""
    return (np.asarray(flat) >= 0.5).astype(np.float32)


def pattern_point(flat: np.ndarray) -> np.ndarray:
    """The full pattern as a point of the scales: 1 on every entry the rounded setting switches off, 0 elsewhere."""
    return (1.0 - rounded(flat)).astype(np.float32)


# ----------------------------------------------------------------------------- the batch


@dataclass
class Batch:
    """A batch as the probe uses it: token ids [n, T], labels per module [n, T, C_l], and the weight deltas, all in one
    dtype on one device, with the layout."""

    ids: Any
    labels: dict[str, Any]
    weight_deltas: dict[str, Any]
    lay: list[tuple[str, int]]

    @property
    def n_texts(self) -> int:
        return int(self.ids.shape[0])

    @property
    def dtype(self) -> Any:
        return next(iter(self.labels.values())).dtype

    @property
    def device(self) -> Any:
        return self.ids.device

    def take(self, rows: Any) -> "Batch":
        """The texts at `rows` (a slice, or a 1-d index tensor or list, repeats allowed)."""
        import torch

        if not isinstance(rows, slice):
            rows = torch.as_tensor(rows, dtype=torch.long, device=self.device)
        return Batch(self.ids[rows], {k: v[rows] for k, v in self.labels.items()}, self.weight_deltas, self.lay)


def as_float32_batch(model: Any, prep: Any, lay: list[tuple[str, int]]) -> Batch:
    """A prepared batch (`adversary.prepare`) for the probe: its ids, its labels cast to the model's parameter dtype
    (float32 on the real model), and the weight deltas recomputed in that dtype under `no_grad`, without autocast. The
    labels are the preparation's own: on the GPU, the run's bfloat16 labels, cast exactly."""
    import torch

    if [k for k, _ in lay] != list(model.target_module_paths):
        raise ValueError("the layout's module order is not model.target_module_paths")
    dtype = next(model.parameters()).dtype
    with torch.no_grad():
        labels = {k: prep.labels[k].to(dtype) for k, _ in lay}
        wd = {k: v.to(dtype) for k, v in model.calc_weight_deltas().items()}
    for k, c in lay:
        if labels[k].shape[-1] != c:
            raise ValueError(f"{k}: labels of width {labels[k].shape[-1]}, layout {c}")
    return Batch(prep.ids, labels, wd, list(lay))


# ----------------------------------------------------------------------------- the forward


def scales_at(n: int, lay: list[tuple[str, int]], point: np.ndarray | None, *, device: Any, dtype: Any, requires_grad: bool) -> dict[str, Any]:
    """Per module the scales [n, 1, C_l + 1]: zeros (the intact model) or a flat point shared by the n texts."""
    import torch

    out, off = {}, 0
    for name, c in lay:
        if point is None:
            a = torch.zeros((n, 1, c + 1), dtype=dtype, device=device)
        else:
            row = torch.as_tensor(np.ascontiguousarray(point[off : off + c + 1]), dtype=dtype, device=device)
            a = row.reshape(1, 1, c + 1).expand(n, 1, c + 1).clone()
        out[name] = a.requires_grad_(requires_grad)
        off += c + 1
    if point is not None and off != np.asarray(point).size:
        raise ValueError("the point is not in the layout")
    return out


def logits_at(model: Any, batch: Batch, sources: dict[str, Any]) -> Any:
    """The masked model's logits [n, T, V] through the authors' mask construction and forward (`pgd_utils` at 74146b5):
    the sources are expanded to every position, a component's mask is l + r (1 - l), a delta entry's mask is r."""
    from param_decomp.metrics.pgd_utils import _construct_mask_infos_from_adv_sources

    batch_dims = next(iter(batch.labels.values())).shape[:-1]
    mask_infos = _construct_mask_infos_from_adv_sources(adv_sources=sources, ci=batch.labels, weight_deltas=batch.weight_deltas, routing_masks="all",
                                                        batch_dims=batch_dims)
    return model(batch.ids, mask_infos=mask_infos)


def forward_at(model: Any, batch: Batch, point: np.ndarray | None, *, grad: bool) -> tuple[Any, dict[str, Any]]:
    """The logits at a point of the scales (None: the intact model), with the scales as leaves when `grad`."""
    import torch

    scales = scales_at(batch.n_texts, batch.lay, point, device=batch.device, dtype=batch.dtype, requires_grad=grad)
    ctx = torch.enable_grad() if grad else torch.no_grad()
    with ctx:
        z = logits_at(model, batch, {k: 1.0 - v for k, v in scales.items()})
    return z, scales


def reference_direction(z_pattern: Any, z_intact: Any) -> tuple[Any, Any]:
    """Delta = z_pattern - z_intact, centred over the vocabulary, and Delta_hat, Delta at unit length per position (zero
    where Delta is exactly zero). Returns (Delta_hat [n, T, V], |Delta| [n, T])."""
    import torch

    with torch.no_grad():
        d = z_pattern.detach() - z_intact.detach()
        d -= d.mean(dim=-1, keepdim=True)
        norm = torch.linalg.vector_norm(d, dim=-1)
        d /= torch.where(norm > 0, norm, torch.ones_like(norm)).unsqueeze(-1)
        d *= (norm > 0).unsqueeze(-1).to(d.dtype)
    return d, norm


def first_order(z: Any, scales: dict[str, Any], direction: Any, lay: list[tuple[str, int]], *, retain_graph: bool = False) -> Any:
    """One backward pass: the gradient of sum_{x, t} <z(x, t), direction(x, t)> with respect to every scale, flat in the
    layout's order, [n, n_entries]. The direction is centred, so this is the gradient of the centred logits' projection."""
    import torch

    grads = torch.autograd.grad(z, [scales[k] for k, _ in lay], grad_outputs=direction, retain_graph=retain_graph)
    return torch.cat([g.reshape(g.shape[0], -1) for g in grads], dim=1)


def kl_per_text(z_reference: Any, z_moved: Any) -> np.ndarray:
    """Per text, the mean over positions of KL(softmax(z_reference) || softmax(z_moved)), in float64, one text at a time."""
    import torch

    out = np.zeros(int(z_reference.shape[0]), dtype=np.float64)
    with torch.no_grad():
        for i in range(out.size):
            lp = torch.log_softmax(z_reference[i].detach(), dim=-1)
            lq = torch.log_softmax(z_moved[i].detach(), dim=-1)
            out[i] = float((lp.exp() * (lp - lq)).sum(dim=-1).double().mean())
    return out


class IntactGraph:
    """The intact model's forward on a batch, with the scales as leaves and the graph kept, so that each setting's pushes
    at the intact model take one backward pass (`pushes`)."""

    def __init__(self, model: Any, batch: Batch) -> None:
        self.batch = batch
        self.z, self.scales = forward_at(model, batch, None, grad=True)

    @property
    def logits(self) -> Any:
        return self.z.detach()

    def pushes(self, direction: Any) -> Any:
        return first_order(self.z, self.scales, direction, self.batch.lay, retain_graph=True)

    def release(self) -> None:
        self.z = None
        self.scales = None


def cell(model: Any, batch: Batch, intact: IntactGraph, setting: np.ndarray, points: tuple[str, ...]) -> dict[str, Any]:
    """One setting on one batch: the full rounded pattern's forward (with its graph if the full-pattern point is asked
    for), the reference direction, and one backward pass per point. Returns the pushes per point as float32 arrays
    [n, n_entries], and per text: sum_t |Delta(x, t)|, the count of positions with a zero direction, and the pattern's
    mean KL from the intact model."""
    import torch

    unknown = set(points) - set(POINTS)
    if unknown or "intact" not in points:
        raise ValueError(f"points: {points}")
    z_p, sc_p = forward_at(model, batch, pattern_point(setting), grad="pattern" in points)
    kl = kl_per_text(intact.logits, z_p)
    direction, norm = reference_direction(z_p, intact.logits)
    out: dict[str, Any] = {"intact": intact.pushes(direction).detach().float().cpu().numpy()}
    if "pattern" in points:
        out["pattern"] = first_order(z_p, sc_p, direction, batch.lay).detach().float().cpu().numpy()
    with torch.no_grad():
        out["delta_norm_sum"] = norm.double().sum(dim=-1).cpu().numpy()
        out["zero_direction_positions"] = (norm == 0).sum(dim=-1).to(torch.int64).cpu().numpy()
    out["pattern_kl"] = kl
    del z_p, sc_p, direction, norm
    return out


def first_order_pushes(model: Any, batch: Batch, setting: np.ndarray, points: tuple[str, ...] = ("intact",)) -> dict[str, Any]:
    """The plan's function: every entry's first-order push for one setting on one batch, from one forward and one
    backward pass per point (the intact forward also gives z_intact, and the pattern forward z_pattern)."""
    intact = IntactGraph(model, batch)
    try:
        return cell(model, batch, intact, setting, points)
    finally:
        intact.release()


def intact_against_target(model: Any, batch: Batch, z_intact: Any) -> dict[str, float]:
    """The intact model against the target model's own forward: the largest absolute difference of the logits, and the
    largest per-text mean KL(target || intact)."""
    import torch

    with torch.no_grad():
        target = model(batch.ids)
        diff = float((target - z_intact.detach()).abs().max())
        kl = kl_per_text(target, z_intact)
    return {"max_abs_logit_difference": diff, "max_text_kl": float(kl.max())}


# ----------------------------------------------------------------------------- the exact one-at-a-time pushes


def exact_pushes(model: Any, batch: Batch, pairs: list[tuple[int, int]], direction: Any, *, chunk: int = 64) -> dict[str, Any]:
    """For each (flat entry, text index) pair, the exact move of that entry alone on that text, at the intact model:
    sum_t <z(a_e = 1) - z_null, Delta_hat(text)>, z_null the same text with a = 0 in the same chunk. Rows are grouped by
    text; each chunk holds one text's null row and up to chunk - 1 of its pairs. Returns the pushes (float64, in the
    pairs' order) and, per chunk, the largest |logit| difference between its null row and the first null row of its text."""
    import torch

    lay = batch.lay
    offs = module_offsets(lay)
    names = [k for k, _ in lay]
    out = np.full(len(pairs), np.nan, dtype=np.float64)
    null_spread: list[float] = []
    by_text: dict[int, list[int]] = {}
    for k, (_, t) in enumerate(pairs):
        by_text.setdefault(int(t), []).append(k)
    with torch.no_grad():
        for t, ks in sorted(by_text.items()):
            first_null = None
            for a in range(0, len(ks), chunk - 1):
                part = ks[a : a + chunk - 1]
                rows = [t] * (1 + len(part))
                sub = batch.take(rows)
                sources = {k: torch.ones((len(rows), 1, c + 1), dtype=batch.dtype, device=batch.device) for k, c in lay}
                for r, k in enumerate(part, start=1):
                    e = int(pairs[k][0])
                    m = int(np.searchsorted(offs, e, side="right") - 1)
                    sources[names[m]][r, 0, e - int(offs[m])] = 0.0
                z = logits_at(model, sub, sources)
                d = direction[t]
                proj = ((z[1:] - z[0:1]) * d.unsqueeze(0)).sum(dim=-1).double().sum(dim=-1)
                out[np.asarray(part)] = proj.cpu().numpy()
                if first_null is None:
                    first_null = z[0].clone()
                null_spread.append(float((z[0] - first_null).abs().max()))
                del z, sub, sources
    return {"exact": out, "null_spread": null_spread}


# ----------------------------------------------------------------------------- the validation sample and the pass rule


def validation_components(first_order_texts: np.ndarray, off_components: np.ndarray, seed: int, *, deciles: int = VALIDATION_DECILES,
                          per_decile: int = VALIDATION_PER_DECILE) -> dict[str, Any]:
    """The specification's 200 components, stratified by deciles of |p|: each off-set component's |p| is its mean over the
    validation texts of |p(x)|; components whose |p| is exactly zero on every text are left out (their move is null);
    the rest fall into ten equal-count deciles by rank (ties by flat index), and 20 are drawn uniformly without
    replacement from each, deciles in ascending order, one generator."""
    m = np.abs(np.asarray(first_order_texts, dtype=np.float64)[:, off_components]).mean(axis=0)
    keep = m > 0
    cand = np.asarray(off_components)[keep]
    mc = m[keep]
    order = np.lexsort((cand, mc))
    n = order.size
    if n < deciles * per_decile:
        raise ValueError("fewer off-set components with a push than the sample")
    decile = np.empty(n, dtype=np.int64)
    decile[order] = (deciles * np.arange(n)) // n
    rng = np.random.default_rng(seed)
    picked, which = [], []
    for d in range(deciles):
        pool = cand[decile == d]
        picked.append(np.sort(rng.choice(pool, size=per_decile, replace=False)))
        which.append(np.full(per_decile, d, dtype=np.int64))
    return {"components": np.concatenate(picked).astype(np.int64), "decile": np.concatenate(which), "left_out_zero": int((~keep).sum()),
            "candidates": int(n)}


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    from scipy.stats import spearmanr

    return float(spearmanr(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)).statistic)


def pass_rule(first: np.ndarray, exact: np.ndarray) -> dict[str, Any]:
    """The specification's pass rule on the validation pairs. The bottom decile is that of |first-order p| over all pairs (the
    10th percentile, numpy's default interpolation); a pair is above it if its |p| is strictly greater. The sign share
    is over those pairs (np.sign, so an exact zero matches only a zero); the Spearman correlation is over all pairs."""
    first = np.asarray(first, dtype=np.float64).reshape(-1)
    exact = np.asarray(exact, dtype=np.float64).reshape(-1)
    if first.shape != exact.shape or not np.isfinite(first).all() or not np.isfinite(exact).all():
        raise ValueError("the validation pairs are not complete")
    cut = float(np.percentile(np.abs(first), 10.0))
    above = np.abs(first) > cut
    share = float((np.sign(first[above]) == np.sign(exact[above])).mean())
    rho = spearman(first, exact)
    return {"pairs": int(first.size), "bottom_decile_cut": cut, "pairs_above": int(above.sum()), "sign_share_above": share,
            "sign_share_all": float((np.sign(first) == np.sign(exact)).mean()), "spearman_all": rho, "spearman_above": spearman(first[above], exact[above]),
            "pearson_all": float(np.corrcoef(first, exact)[0, 1]) if first.size > 1 else math.nan,
            "rule": {"sign_share_at_least": PASS_SIGN_SHARE, "spearman_at_least": PASS_SPEARMAN},
            "passes": bool(share >= PASS_SIGN_SHARE and rho >= PASS_SPEARMAN)}
