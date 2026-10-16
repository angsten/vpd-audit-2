"""Our adversary loop: the authors' evaluation adversary (`param_decomp/metrics/pgd_utils.py` at 74146b5) with the
features questions 1 and 2 need, specified in the gate specification (research log), Section 2.2. Gate G2
checks it against the authors' `_run_pgd_loop` (`g2.py`).

What our loop orchestrates, and what it takes from the authors unchanged:
  - the forward is the authors' `_forward_with_adv_sources` (mask = g + (1 - g) r through `interpolate_pgd_mask`, the
    delta mask the raw last entry, `make_mask_infos`, the model's forward hooks), with `recon_loss_kl`;
  - one step is the authors' arithmetic: under `torch.enable_grad()`, `loss = sum_loss / n_examples`; then
    `torch.autograd.grad(loss, list(sources.values()))`; then, under `no_grad`, `source.add_(step_size * grad.sign())`
    and `source.clamp_(0.0, 1.0)`. The authors' `all_reduce` of the gradient is a no-op on one process and is omitted.
  - routing is all 24 matrices (`AllLayersRouter`, mask "all"), as the evaluation and training adversaries route.

The features (Section 2.2):
  - fixed start: a saved start (shape [1, 1, C_l + 1] per module in `model.target_module_paths` order, delta entry last);
  - overridden labels: `labels` replaces the batch's `ci.lower_leaky` (freed labels set to 0 before the mask is formed);
  - held-out scoring: `score` runs the forward only, for a given source, on any prepared batch with its own labels;
  - per-entry gradients: `record_grads` keeps the gradient of every entry at every step, and their sum over steps;
  - frozen sources: `Frozen` fixes chosen entries at chosen values; their value is written into the start before step 0
    and written back after every update, so they take no part in the update or the clamp;
  - saved random draws: `stochastic_draw` draws routing masks and stochastic sources from CPU generators seeded by the
    manifest keys (master, "routing", s, text_id, draw) and (master, "stoch", s, text_id, draw); `save_draw`/`load_draw`;
  - per-step record: the harm after every step, and optionally the source;
  - step schedule: `step_size` is a float or a function of the step index;
  - micro-batching: `micro_batch` = 8 or 16 runs the forward and backward over chunks of texts, accumulating the gradient
    of sum_loss / N_total (N_total the batch's positions) in chunk order before the sign step; the harm is the sum of the
    chunks' sums over N_total. The sign ignores the positive scale, so this equals the whole-batch step up to summation order.
  - save hook (plan 3 of the research log, Section 3): `SaveHook` keeps the source after step n and n - 1 for given n, and at the
    first step whose two-step mean of harm (after steps k - 1 and k) reaches each given h.

Indexing follows G1: entry k of the harm record (from zero) is the harm after k updates; a run of n steps records n + 1.
"""

from __future__ import annotations

import contextlib
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

StepSize = float | Callable[[int], float]


@dataclass
class Prepared:
    """One batch's fixed inputs: token ids, labels (lower-leaky), target logits, weight deltas, all on the device."""
    ids: Any
    labels: dict[str, Any]
    target_out: Any
    weight_deltas: dict[str, Any] | None
    precision: str

    @property
    def n_texts(self) -> int:
        return int(self.ids.shape[0])


def autocast_ctx(precision: str) -> Any:
    import torch

    return torch.autocast(device_type="cuda", dtype=torch.bfloat16) if precision == "bf16" else contextlib.nullcontext()


def prepare(model: Any, ids: np.ndarray | Any, precision: str, device: str = "cuda", deltas: bool = True) -> Prepared:
    """Labels, target output, and weight deltas computed once under `no_grad` (and bf16 autocast for "bf16"), as the
    authors' `evaluate()` computes them and as G1 did (`g1.labels_once`)."""
    import torch

    batch = ids if isinstance(ids, torch.Tensor) else torch.from_numpy(np.asarray(ids).astype(np.int64))
    batch = batch.to(device)
    with torch.no_grad(), autocast_ctx(precision):
        weight_deltas = model.calc_weight_deltas() if deltas else None
        target_output = model(batch, cache_type="input")
        ci = model.calc_causal_importances(pre_weight_acts=target_output.cache, detach_inputs=False, sampling="continuous")
    return Prepared(ids=batch, labels=ci.lower_leaky, target_out=target_output.output, weight_deltas=weight_deltas, precision=precision)


def start_tensors(start: dict[str, np.ndarray], model: Any, device: str, with_delta: bool = True) -> dict[str, Any]:
    """The saved start as sources, its layout asserted against the model. With `with_delta=False`, the delta entries
    are dropped (the authors' weight_deltas=None layout, [1, 1, C_l])."""
    import torch

    keys = list(start)
    assert keys == list(model.target_module_paths), "the start's module order is not model.target_module_paths"
    out = {}
    for k in keys:
        assert start[k].shape == (1, 1, model.module_to_c[k] + 1), (k, start[k].shape)
        assert start[k].dtype == np.float32
        a = start[k] if with_delta else start[k][..., :-1]
        out[k] = torch.from_numpy(np.ascontiguousarray(a).copy()).to(device).requires_grad_(True)
    return out


@dataclass
class Frozen:
    """Entries held at fixed values: per module a bool mask and the values, each of the source's shape."""
    mask: dict[str, Any]
    value: dict[str, Any]

    @staticmethod
    def delta_entries(model: Any, value: float, device: str) -> "Frozen":
        import torch

        mask, val = {}, {}
        for k in model.target_module_paths:
            m = torch.zeros((1, 1, model.module_to_c[k] + 1), dtype=torch.bool, device=device)
            m[..., -1] = True
            mask[k] = m
            val[k] = torch.full_like(m, value, dtype=torch.float32)
        return Frozen(mask, val)

    @staticmethod
    def empty(model: Any, device: str) -> "Frozen":
        import torch

        mask = {k: torch.zeros((1, 1, model.module_to_c[k] + 1), dtype=torch.bool, device=device) for k in model.target_module_paths}
        return Frozen(mask, {k: torch.zeros_like(v, dtype=torch.float32) for k, v in mask.items()})

    def write(self, sources: dict[str, Any]) -> None:
        import torch

        with torch.no_grad():
            for k, s in sources.items():
                if bool(self.mask[k].any()):
                    s.copy_(torch.where(self.mask[k], self.value[k].to(s.dtype), s))


@dataclass
class SaveHook:
    """Plan 3 of the research log, Section 3: the source after step n and n - 1 for n in `steps`, and at the first step k >= 1
    whose two-step mean of harm, (h[k-1] + h[k]) / 2, reaches each h in `thresholds`."""
    steps: tuple[int, ...] = (20, 40, 80, 160, 320)
    thresholds: tuple[float, ...] = (2.0, 5.0, 10.0)
    saved: dict[str, np.ndarray] = field(default_factory=dict)
    events: dict[str, int] = field(default_factory=dict)
    # Plan 2 of the research log, Section 4: with `run(..., cum_grads=True)`, per saved source the signed sum and the sum of
    # absolute values of the per-entry gradient over iterations 0 to k - 1 (float32, the source's flat layout).
    cum: dict[str, tuple[np.ndarray, np.ndarray]] = field(default_factory=dict)

    def __call__(self, k: int, record: list[float], sources: dict[str, Any], cum: tuple[np.ndarray, np.ndarray] | None = None) -> None:
        names = []
        for n in self.steps:
            if k in (n, n - 1):
                names.append(f"step_{k}")
        if k >= 1:
            mean2 = 0.5 * (record[k - 1] + record[k])
            for h in self.thresholds:
                key = f"two_step_mean_reaches_{h:g}"
                if key not in self.events and mean2 >= h:
                    self.events[key] = k
                    names.append(key)
        if names:
            flat = flatten(sources)
            for nm in dict.fromkeys(names):
                self.saved[nm] = flat
                self.events.setdefault(nm, k)
                if cum is not None:
                    self.cum[nm] = (cum[0].astype(np.float32), cum[1].astype(np.float32))


def flatten(tensors: dict[str, Any]) -> np.ndarray:
    """Per-module tensors concatenated along the last axis in dict order, as one float32 vector."""
    return np.concatenate([t.detach().float().reshape(-1).cpu().numpy() for t in tensors.values()])


class KLWithPerText:
    """The authors' `recon_loss_kl` (`param_decomp/models/batch_and_loss_fns.py` at 74146b5), line for line, keeping each
    text's mean harm from the same tensor (plan 2 of the research log, Section 4; the table and run specification, Section 6).
    It repeats the authors' three lines and does not call their function; the search never uses it."""

    per_text: Any = None

    def __call__(self, pred: Any, target: Any) -> tuple[Any, int]:
        import math

        import torch
        import torch.nn.functional as F

        assert pred.shape == target.shape
        log_q = torch.log_softmax(pred, dim=-1)  # log Q
        p = torch.softmax(target, dim=-1)  # P
        kl_per_position = F.kl_div(log_q, p, reduction="none").sum(dim=-1)  # [texts, positions]
        self.per_text = kl_per_position.double().mean(dim=1)  # [texts], nats per token
        return kl_per_position.sum(), math.prod(pred.shape[:-1])


def _forward(model: Any, ids: Any, sources: dict[str, Any], labels: dict[str, Any], target_out: Any, weight_deltas: Any,
             reconstruction_loss: Any = None) -> tuple[Any, int]:
    """`reconstruction_loss` defaults to the authors' `recon_loss_kl`, so the search path is untouched."""
    from param_decomp.metrics.pgd_utils import _forward_with_adv_sources
    from param_decomp.models.batch_and_loss_fns import recon_loss_kl

    batch_dims = next(iter(labels.values())).shape[:-1]
    return _forward_with_adv_sources(model=model, batch=ids, adv_sources=sources, ci=labels, weight_deltas=weight_deltas, routing_masks="all",
                                     target_out=target_out, batch_dims=batch_dims,
                                     reconstruction_loss=recon_loss_kl if reconstruction_loss is None else reconstruction_loss)


def _chunks(n: int, micro_batch: int | None) -> list[tuple[int, int]]:
    if micro_batch is None:
        return [(0, n)]
    assert n % micro_batch == 0, (n, micro_batch)
    return [(a, a + micro_batch) for a in range(0, n, micro_batch)]


def loss_and_grad(model: Any, prep: Prepared, sources: dict[str, Any], labels: dict[str, Any] | None = None,
                  micro_batch: int | None = None) -> tuple[float, list[Any]]:
    """The harm at the current sources and the gradient of the mean KL with respect to them. Whole batch: the authors'
    ops exactly. Micro-batched: the gradient of each chunk's sum_loss / N_total, summed in chunk order."""
    import torch

    labels = prep.labels if labels is None else labels
    if micro_batch is None:
        with torch.enable_grad():
            sum_loss, n_examples = _forward(model, prep.ids, sources, labels, prep.target_out, prep.weight_deltas)
            loss = sum_loss / n_examples
        grads = torch.autograd.grad(loss, list(sources.values()))
        return float(sum_loss.detach()) / n_examples, list(grads)
    n_total = prep.n_texts * int(prep.ids.shape[1])
    total = 0.0
    acc = None
    for a, b in _chunks(prep.n_texts, micro_batch):
        lab = {k: v[a:b] for k, v in labels.items()}
        with torch.enable_grad():
            s, n_c = _forward(model, prep.ids[a:b], sources, lab, prep.target_out[a:b], prep.weight_deltas)
            loss = s / n_total
        g = torch.autograd.grad(loss, list(sources.values()))
        total += float(s.detach())
        acc = list(g) if acc is None else [x + y for x, y in zip(acc, g)]
        del s, loss, g
    return total / n_total, acc


def harm(model: Any, prep: Prepared, sources: dict[str, Any], labels: dict[str, Any] | None = None, micro_batch: int | None = None) -> float:
    """Forward only, under no_grad: the mean KL at the given sources (chunks summed in order when micro-batched)."""
    import torch

    labels = prep.labels if labels is None else labels
    n_total = prep.n_texts * int(prep.ids.shape[1])
    with torch.no_grad():
        if micro_batch is None:
            s, n = _forward(model, prep.ids, sources, labels, prep.target_out, prep.weight_deltas)
            return float(s.detach()) / n
        total = 0.0
        for a, b in _chunks(prep.n_texts, micro_batch):
            s, _ = _forward(model, prep.ids[a:b], sources, {k: v[a:b] for k, v in labels.items()}, prep.target_out[a:b], prep.weight_deltas)
            total += float(s.detach())
        return total / n_total


def run(model: Any, prep: Prepared, start: dict[str, np.ndarray], n_steps: int, step_size: StepSize = 0.1, *, labels: dict[str, Any] | None = None,
        frozen: Frozen | None = None, micro_batch: int | None = None, record_sources: bool = False, record_grads: bool = False,
        save_hook: SaveHook | None = None, with_delta: bool = True, device: str = "cuda", grad_probe: Callable[[int, dict[str, Any]], None] | None = None,
        cum_grads: bool = False) -> dict[str, Any]:
    """One search. Returns the harm record (n_steps + 1 values), the final sources, and what was asked to be recorded.
    `grad_probe(k, sources)`, if given, is called at each step's sources before the update (G2's micro-batch validation).
    `cum_grads` hands the save hook, at step k, the per-entry gradient summed over iterations 0 to k - 1, signed and in
    absolute value (iteration m's gradient is taken at the sources after m updates). It reads the gradients the update
    uses and changes nothing in the search."""
    import torch

    t0 = time.time()
    step_fn = step_size if callable(step_size) else (lambda _k, _s=step_size: _s)
    sources = start_tensors(start, model, device, with_delta=with_delta)
    if frozen is not None:
        frozen.write(sources)
    record: list[float] = []
    src_rec: list[np.ndarray] = []
    grad_rec: list[np.ndarray] = []
    grad_sum = None
    n_entries = sum(int(v.numel()) for v in sources.values())
    cum = (np.zeros(n_entries, dtype=np.float64), np.zeros(n_entries, dtype=np.float64)) if cum_grads else None
    with torch.no_grad(), autocast_ctx(prep.precision):
        for k in range(n_steps):
            if record_sources:
                src_rec.append(flatten(sources))
            if grad_probe is not None:
                grad_probe(k, sources)
            h, grads = loss_and_grad(model, prep, sources, labels, micro_batch)
            record.append(h)
            if save_hook is not None:
                if cum is None:
                    save_hook(k, record, sources)
                else:
                    save_hook(k, record, sources, cum)
            if cum is not None:
                g64 = flatten(dict(zip(sources, grads))).astype(np.float64)
                np.add(cum[0], g64, out=cum[0])
                np.add(cum[1], np.abs(g64), out=cum[1])
            if record_grads:
                gflat = flatten(dict(zip(sources, grads)))
                grad_rec.append(gflat)
                grad_sum = gflat.astype(np.float64) if grad_sum is None else grad_sum + gflat
            with torch.no_grad():
                step = step_fn(k)
                for name, g in zip(sources, grads):
                    sources[name].add_(step * g.sign())
                    sources[name].clamp_(0.0, 1.0)
            if frozen is not None:
                frozen.write(sources)
            del grads
        if record_sources:
            src_rec.append(flatten(sources))
        record.append(harm(model, prep, sources, labels, micro_batch))
        if save_hook is not None:
            if cum is None:
                save_hook(n_steps, record, sources)
            else:
                save_hook(n_steps, record, sources, cum)
    if device == "cuda":
        torch.cuda.synchronize()
    out = {"record": record, "final": record[-1], "n_steps": n_steps, "micro_batch": micro_batch, "precision": prep.precision,
           "sources": {k: v.detach().float().cpu().numpy() for k, v in sources.items()}, "seconds": time.time() - t0}
    if record_sources:
        out["source_record"] = np.stack(src_rec)
    if record_grads:
        out["grad_record"] = np.stack(grad_rec)
        out["grad_sum"] = grad_sum
    return out


def score(model: Any, source: dict[str, np.ndarray], prep: Prepared, micro_batch: int | None = None, device: str = "cuda") -> float:
    """Held-out scoring: the harm of a given source on a prepared batch (its own labels), forward only."""
    import torch

    sources = {k: torch.from_numpy(np.ascontiguousarray(v)).to(device) for k, v in source.items()}
    with torch.no_grad(), autocast_ctx(prep.precision):
        return harm(model, prep, sources, None, micro_batch)


def score_per_text(model: Any, source: dict[str, np.ndarray], prep: Prepared, device: str = "cuda") -> tuple[float, np.ndarray]:
    """As `score` on the whole batch, through `KLWithPerText`: the batch's harm, and each text's mean harm over its
    positions (float64), from the one forward pass."""
    import torch

    sources = {k: torch.from_numpy(np.ascontiguousarray(v)).to(device) for k, v in source.items()}
    loss = KLWithPerText()
    with torch.no_grad(), autocast_ctx(prep.precision):
        s, n = _forward(model, prep.ids, sources, prep.labels, prep.target_out, prep.weight_deltas, reconstruction_loss=loss)
    return float(s.detach()) / n, loss.per_text.detach().cpu().numpy()


# ----------------------------------------------------------------------------- stochastic draws


def _generator(seed: int) -> Any:
    import torch

    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    return g


def stochastic_draw(module_names: list[str], module_to_c: dict[str, int], text_ids: list[str], s: int, draw: int, seq_len: int,
                    routing: bool = True) -> dict[str, Any]:
    """Per text, on the CPU, in this order:
      stochastic sources and delta masks from the generator seeded (master, "stoch", s, text_id, draw):
        for each module in `module_names` order, `rand((seq_len, C_l))` (float32); then for each module, `rand((seq_len,))`;
      routing from the generator seeded (master, "routing", s, text_id, draw): the authors'
        `sample_uniform_k_subset_routing_masks((seq_len,), module_names, "cpu", generator)` (randint, then a rand-argsort).
    `module_names` must be the order of the labels dict, the order in which the authors' `calc_stochastic_component_mask_info`
    draws. Returns stacked tensors: u[module] [n, T, C], delta[module] [n, T], routing[module] [n, T] (bool) or None."""
    import torch

    from vpd_audit_2.manifest import seed_of

    from param_decomp.routing import sample_uniform_k_subset_routing_masks

    u = {k: [] for k in module_names}
    dm = {k: [] for k in module_names}
    rt = {k: [] for k in module_names}
    for tid in text_ids:
        g = _generator(seed_of("stoch", s, tid, draw))
        for k in module_names:
            u[k].append(torch.rand((seq_len, module_to_c[k]), generator=g, dtype=torch.float32))
        for k in module_names:
            dm[k].append(torch.rand((seq_len,), generator=g, dtype=torch.float32))
        if routing:
            r = sample_uniform_k_subset_routing_masks((seq_len,), module_names, "cpu", generator=_generator(seed_of("routing", s, tid, draw)))
            for k in module_names:
                rt[k].append(r[k])
    return {"u": {k: torch.stack(v) for k, v in u.items()}, "delta": {k: torch.stack(v) for k, v in dm.items()},
            "routing": {k: torch.stack(v) for k, v in rt.items()} if routing else None,
            "keys": {"stoch": ["master", "stoch", s, "<text_id>", draw], "routing": ["master", "routing", s, "<text_id>", draw] if routing else None},
            "text_ids": list(text_ids)}


def stochastic_mask_infos(labels: dict[str, Any], draw: dict[str, Any], weight_deltas: dict[str, Any] | None, device: str) -> dict[str, Any]:
    """Masks g + (1 - g) u, delta masks from the draw, routing from the draw (unrouted matrices at their target weights
    through the model's hook) or all matrices if the draw has none."""
    from param_decomp.models.components import make_mask_infos

    comp = {k: labels[k] + (1 - labels[k]) * draw["u"][k].to(device) for k in labels}
    wdm = None if weight_deltas is None else {k: (weight_deltas[k], draw["delta"][k].to(device)) for k in labels}
    routing = "all" if draw["routing"] is None else {k: draw["routing"][k].to(device) for k in labels}
    return make_mask_infos(component_masks=comp, weight_deltas_and_masks=wdm, routing_masks=routing)


def save_draw(draw: dict[str, Any], path: Path) -> None:
    arrays = {f"u|{k}": v.numpy() for k, v in draw["u"].items()}
    arrays.update({f"delta|{k}": v.numpy() for k, v in draw["delta"].items()})
    if draw["routing"] is not None:
        arrays.update({f"routing|{k}": v.numpy() for k, v in draw["routing"].items()})
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, order=np.array(list(draw["u"])), text_ids=np.array(draw["text_ids"]), **arrays)


def load_draw(path: Path) -> dict[str, Any]:
    import torch

    with np.load(path) as z:
        order = [str(x) for x in z["order"]]
        u = {k: torch.from_numpy(z[f"u|{k}"]) for k in order}
        dm = {k: torch.from_numpy(z[f"delta|{k}"]) for k in order}
        rt = {k: torch.from_numpy(z[f"routing|{k}"]) for k in order} if f"routing|{order[0]}" in z.files else None
        tids = [str(x) for x in z["text_ids"]]
    return {"u": u, "delta": dm, "routing": rt, "text_ids": tids}
