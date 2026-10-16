"""Plan 6 of the research log: the three-arm experiment's computation (the experiment's specification (research log) with the
plan's eight amendments). Training's persistent adversary, the authors' own state class at the tag
(`param_decomp/persistent_pgd.py` at 74146b5, arithmetically the run commit 85c6b70's for the released configuration),
run against the released decomposition held frozen. Only the sources move.

The arms differ only in the scope of a source, each built by the authors' `PersistentPGDState` unchanged:
  - arm 1, "released": the released scope `per_batch_per_position`, one source per text slot and position, [64, 512, C+1];
  - arm 2, "per_document": the same class and scope constructed with batch dims (64, 1), so one source per text slot,
    [64, 1, C+1], which the authors' `get_ppgd_mask_infos` expands over the positions; its gradient is the sum over them;
  - arm 3, "batch": the authors' `single_source` scope, one source [1, 1, C+1] for the whole batch.

The released optimizer, read from the run's raw config (`run_config.loss_entry`): Adam, beta1 0.5, beta2 0.99, eps 1e-8,
two warm-up ascents plus the outer one per batch, clamp to [0, 1], all 24 matrices (`AllLayersRouter`), delta sources
included. The learning rate is a constant 0.01 with no warm-up (the plan's settled question 2): the config's schedule
with `warmup_pct` set to 0.

One process emulates training's sixteen. Training ran 16 processes of 4 texts (provenance (i)); each process's loss
was the mean over its own 4 x 512 positions, and the released scope's gradients were not all-reduced. On one GPU with
64 texts the loss is the mean over 64 x 512 positions, so every per-slot source's gradient would be 16 times smaller,
and Adam's epsilon makes the step depend on that scale. `ScaledState` multiplies the loss by 64 / 4 = 16 before the
gradient for the two scopes whose sources are local to a process (arms 1 and 2), which gives the per-process gradient
(16 is a power of two, so the scaling is exact except for gradients so small, below about 1e-35, that an intermediate
product underflows; Adam's epsilon of 1e-8 makes their step zero either way). The batch scope all-reduces by averaging across processes,
which is the gradient of the mean over all 64 texts: no scaling. The losses recorded are never scaled: the mean over
the 64 texts, which is training's logged value (the average over processes of their means).

Per batch, training's own sequence (`run_param_decomp.py` at the tag, lines 277 to 336): the labels and the target
model's output computed in bfloat16 autocast (`calc_causal_importances`, continuous sampling), the weight deltas in
float32 outside autocast (computed once: the decomposition is frozen); then, recorded first, the harm on the fresh batch
before any ascent; the two warm-up ascents; the loss (training's own, logged as `train/loss/PersistentPGDReconLoss`); the
outer ascent on it; and, as description, the harm after all three ascents.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

import numpy as np

ARMS = ("released", "per_document", "batch")
ARM_NUMBER = {"released": 1, "per_document": 2, "batch": 3}
TEXTS_PER_BATCH = 64
TEXTS_PER_PROCESS = 4  # provenance (i): a training batch of 64 over 16 processes
SEQ = 512
LR = 0.01
INIT_LABEL = "three-arm-init"
SERIES = ("before", "loss", "after")  # the fresh batch before its ascents; training's own loss; after all three


def released_entry() -> dict[str, Any]:
    """The run's raw `PersistentPGDReconLoss` entry (`run_config`, which asserts every recorded value on import)."""
    from vpd_audit_2.run_config import loss_entry

    return copy.deepcopy(loss_entry("PersistentPGDReconLoss"))


def arm_config(arm: str, entry: dict[str, Any] | None = None) -> Any:
    """The released config, with the learning rate's warm-up removed and the arm's scope."""
    from param_decomp.configs import PersistentPGDReconLossConfig

    if arm not in ARMS:
        raise ValueError(arm)
    e = copy.deepcopy(released_entry() if entry is None else entry)
    e["optimizer"]["lr_schedule"] = {**e["optimizer"]["lr_schedule"], "warmup_pct": 0.0}
    e["scope"] = {"type": "single_source"} if arm == "batch" else {"type": "per_batch_per_position"}
    return PersistentPGDReconLossConfig(**e)


def source_batch_dims(arm: str, n_texts: int, seq: int) -> tuple[int, int]:
    """The batch dims the state is constructed with: per position (n, T); per document (n, 1); the batch scope's
    sources are [1, 1] whatever is passed."""
    return (n_texts, 1) if arm == "per_document" else (n_texts, seq)


def grad_scale(arm: str, n_texts: int, per_process: int = TEXTS_PER_PROCESS) -> float:
    """The factor that turns this process's mean-loss gradient into training's per-process one (see the docstring)."""
    if arm == "batch":
        return 1.0
    if n_texts % per_process:
        raise ValueError(f"{n_texts} texts are not whole processes of {per_process}")
    return float(n_texts // per_process)


def _state_class() -> type:
    from param_decomp.persistent_pgd import PersistentPGDState

    class ScaledState(PersistentPGDState):
        """The authors' state, with the loss multiplied by `grad_scale` before its gradient; nothing else changes."""

        grad_scale: float = 1.0

        def get_grads(self, loss: Any, retain_graph: bool = True) -> Any:  # noqa: D401
            return super().get_grads(loss * self.grad_scale if self.grad_scale != 1.0 else loss, retain_graph=retain_graph)

    return ScaledState


def init_seed(seed_index: int) -> int:
    from vpd_audit_2.manifest import seed_of

    return seed_of(INIT_LABEL, int(seed_index))


def make_state(model: Any, arm: str, n_texts: int, seq: int, device: Any, seed: int, *, scale: float | None = None, scaled: bool = True) -> Any:
    """A fresh state for an arm: the global generator seeded with `seed` just before construction, as training's
    sources were drawn from the global generator at construction (`torch.rand`, provenance (q)). `scaled=False` gives
    the authors' class itself (the gate's reference)."""
    import torch

    from param_decomp.models.batch_and_loss_fns import recon_loss_kl
    from param_decomp.persistent_pgd import PersistentPGDState

    cls = _state_class() if scaled else PersistentPGDState
    torch.manual_seed(int(seed))
    state = cls(module_to_c=model.module_to_c, batch_dims=source_batch_dims(arm, n_texts, seq), device=device, use_delta_component=True,
                cfg=arm_config(arm), reconstruction_loss=recon_loss_kl)
    if scaled:
        state.grad_scale = grad_scale(arm, n_texts) if scale is None else float(scale)
    return state


@dataclass
class Prepared:
    ids: Any
    target_out: Any
    ci: dict[str, Any]


def weight_deltas(model: Any) -> dict[str, Any]:
    """As training computes them: outside autocast, in the parameters' dtype."""
    import torch

    with torch.no_grad():
        return model.calc_weight_deltas()


def prepare(model: Any, ids: Any, *, autocast: bool, sampling: str = "continuous") -> Prepared:
    """Training's labels and target output for a batch (`run_param_decomp.py` lines 287 to 295), without gradients:
    the decomposition is frozen."""
    import torch

    from param_decomp.utils.general_utils import bf16_autocast

    with torch.no_grad(), bf16_autocast(enabled=autocast):
        out = model(ids, cache_type="input")
        ci = model.calc_causal_importances(pre_weight_acts=out.cache, detach_inputs=False, sampling=sampling)
    return Prepared(ids=ids, target_out=out.output, ci=ci.lower_leaky)


def batch_step(state: Any, model: Any, prep: Prepared, wd: dict[str, Any], *, step: int, total_steps: int, autocast: bool,
               record_after: bool = True) -> dict[str, float]:
    """One batch, in training's order. Returns the three harms (nats per position) and the learning rate."""
    import torch

    from param_decomp.utils.general_utils import bf16_autocast

    state.update_lr(step, total_steps)
    lr = float(state.optimizer._lr)
    with bf16_autocast(enabled=autocast):
        with torch.no_grad():
            before = state.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
        state.warmup(model=model, batch=prep.ids, target_out=prep.target_out, ci=prep.ci, weight_deltas=wd)
        loss = state.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
    grads = state.get_grads(loss, retain_graph=False)
    state.step(grads)
    out = {"before": float(before), "loss": float(loss.detach()), "lr": lr}
    del grads, loss
    if record_after:
        with torch.no_grad(), bf16_autocast(enabled=autocast):
            out["after"] = float(state.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd))
    return out


def flat_sources(state: Any, lay: list[tuple[str, int]]) -> np.ndarray:
    """A batch-scope state's one source, flat in the layout's order ([1, 1, C+1] per module), float32."""
    parts = []
    for name, c in lay:
        s = state.sources[name]
        if tuple(s.shape) != (1, 1, c + 1):
            raise ValueError(f"{name}: a source of shape {tuple(s.shape)} is not one source for the batch")
        parts.append(s.detach().float().reshape(-1).cpu().numpy())
    return np.concatenate(parts)


def state_arrays(state: Any) -> dict[str, np.ndarray]:
    """Everything the state carries from batch to batch: the sources, Adam's two moments, and its step count."""
    out = {"step_count": np.array([state.optimizer._step_count], dtype=np.int64)}
    for k, v in state.sources.items():
        out[f"source|{k}"] = v.detach().cpu().numpy()
        out[f"m|{k}"] = state.optimizer._m[k].detach().cpu().numpy()
        out[f"v|{k}"] = state.optimizer._v[k].detach().cpu().numpy()
    return out


def load_state_arrays(state: Any, arrays: dict[str, np.ndarray]) -> None:
    """Restore a state saved by `state_arrays` into a freshly made state of the same arm and shape."""
    import torch

    with torch.no_grad():
        for k in state.sources:
            for key, target in ((f"source|{k}", state.sources[k]), (f"m|{k}", state.optimizer._m[k]), (f"v|{k}", state.optimizer._v[k])):
                a = torch.from_numpy(np.ascontiguousarray(arrays[key]))
                if tuple(a.shape) != tuple(target.shape):
                    raise ValueError(f"{key}: saved {tuple(a.shape)}, state {tuple(target.shape)}")
                target.copy_(a.to(target.device, target.dtype))
    state.optimizer._step_count = int(np.asarray(arrays["step_count"]).reshape(-1)[0])
