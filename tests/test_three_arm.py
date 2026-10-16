"""Plan 6 of the research log: the three-arm computation (`vpd_audit_2/three_arm.py`) on the tiny model.

  - The configs: the released values, the warm-up removed, the three scopes.
  - The per-document scope's source shape, and its gradient pooled over positions: the sum of the per-position
    gradients when the per-position sources hold the per-document source at every position.
  - The scaled gradient is exactly the scale times the authors' gradient.
  - Our batch step reproduces the authors' class driven by training's own sequence, bit for bit (the gate's logic).
  - A saved state, restored, continues exactly as the original.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import three_arm as T

from tiny_model import SEQ, tiny_component_model, tiny_ids


@pytest.fixture(scope="module")
def tiny():
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    model.requires_grad_(False)
    lay = [(k, int(model.module_to_c[k])) for k in model.target_module_paths]
    ids = tiny_ids(8, seed=5)
    return {"model": model, "lay": lay, "ids": ids, "prep": T.prepare(model, ids, autocast=False), "wd": T.weight_deltas(model)}


def test_the_configs():
    for arm in T.ARMS:
        c = T.arm_config(arm)
        assert c.optimizer.beta1 == 0.5 and c.optimizer.beta2 == 0.99 and c.optimizer.eps == 1e-8 and c.n_warmup_steps == 2
        assert c.optimizer.lr_schedule.start_val == 0.01 and c.optimizer.lr_schedule.warmup_pct == 0.0 and c.optimizer.lr_schedule.fn_type == "constant"
        assert c.use_sigmoid_parameterization is False and c.n_samples == 1 and c.start_frac == 0.0
    assert T.arm_config("released").scope.type == "per_batch_per_position" and T.arm_config("batch").scope.type == "single_source"
    assert T.released_entry()["optimizer"]["lr_schedule"]["warmup_pct"] == 0.025  # the run's own, untouched
    assert T.grad_scale("released", 64) == T.grad_scale("per_document", 64) == 16.0 and T.grad_scale("batch", 64) == 1.0


def test_source_shapes(tiny):
    model, lay = tiny["model"], tiny["lay"]
    shapes = {arm: {k: tuple(v.shape) for k, v in T.make_state(model, arm, 8, SEQ, "cpu", 1).sources.items()} for arm in T.ARMS}
    for k, c in lay:
        assert shapes["released"][k] == (8, SEQ, c + 1) and shapes["per_document"][k] == (8, 1, c + 1) and shapes["batch"][k] == (1, 1, c + 1)


def test_the_per_document_gradient_is_pooled_over_positions(tiny):
    model, prep, wd = tiny["model"], tiny["prep"], tiny["wd"]
    doc = T.make_state(model, "per_document", 8, SEQ, "cpu", 3, scale=1.0)
    pos = T.make_state(model, "released", 8, SEQ, "cpu", 3, scale=1.0)
    with torch.no_grad():
        for k in pos.sources:
            pos.sources[k].copy_(doc.sources[k].expand_as(pos.sources[k]))
    ld = doc.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
    lp = pos.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
    assert torch.equal(ld, lp)  # the same masks, so the same loss, bit for bit
    gd, gp = doc.get_grads(ld, retain_graph=False), pos.get_grads(lp, retain_graph=False)
    for k in gd:
        assert torch.allclose(gd[k], gp[k].sum(dim=1, keepdim=True), rtol=1e-5, atol=1e-9)
        assert gp[k].abs().sum() > 0


def test_the_scaled_gradient_is_exactly_the_scale_times_the_authors(tiny):
    model, prep, wd = tiny["model"], tiny["prep"], tiny["wd"]
    a = T.make_state(model, "released", 8, SEQ, "cpu", 4, scaled=False)
    b = T.make_state(model, "released", 8, SEQ, "cpu", 4, scale=2.0)
    for k in a.sources:
        assert torch.equal(a.sources[k], b.sources[k])
    ga = a.get_grads(a.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd), retain_graph=False)
    gb = b.get_grads(b.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd), retain_graph=False)
    normal = 0
    for k in ga:
        big = (2.0 * ga[k]).abs() > 1e-30  # below that, an intermediate product can underflow
        assert torch.equal(gb[k][big], 2.0 * ga[k][big]) and torch.allclose(gb[k], 2.0 * ga[k], rtol=0, atol=1e-30)
        normal += int(big.sum())
    assert normal > 1000


@pytest.mark.parametrize("arm", T.ARMS)
def test_our_step_is_the_authors_training_sequence_bit_for_bit(tiny, arm):
    from param_decomp.utils.general_utils import bf16_autocast

    model, prep, wd = tiny["model"], tiny["prep"], tiny["wd"]
    ours = T.make_state(model, arm, 8, SEQ, "cpu", 9, scale=1.0)
    ref = T.make_state(model, arm, 8, SEQ, "cpu", 9, scaled=False)
    rec = [T.batch_step(ours, model, prep, wd, step=s, total_steps=100, autocast=False) for s in range(3)]
    losses = []
    for s in range(3):  # run_param_decomp.py at the tag, lines 277 to 336, for the persistent term alone
        ref.update_lr(s, 100)
        with bf16_autocast(enabled=False):
            ref.warmup(model=model, batch=prep.ids, target_out=prep.target_out, ci=prep.ci, weight_deltas=wd)
            loss = ref.compute_recon_loss(model, prep.ids, prep.target_out, prep.ci, wd)
        grads = ref.get_grads(loss, retain_graph=True)
        ref.step(grads)
        losses.append(float(loss))
    assert [r["loss"] for r in rec] == losses
    for k in ours.sources:
        assert torch.equal(ours.sources[k], ref.sources[k])
    assert all(r["lr"] == 0.01 for r in rec) and ours.optimizer._step_count == 9  # three ascents per batch
    assert rec[0]["before"] < rec[0]["loss"] and rec[1]["before"] < rec[1]["after"]  # the ascents raise the harm on their own batch


def test_a_saved_state_continues_exactly(tiny):
    model, prep, wd = tiny["model"], tiny["prep"], tiny["wd"]
    a = T.make_state(model, "released", 8, SEQ, "cpu", 11)
    T.batch_step(a, model, prep, wd, step=0, total_steps=10, autocast=False)
    saved = T.state_arrays(a)
    b = T.make_state(model, "released", 8, SEQ, "cpu", 99)
    T.load_state_arrays(b, saved)
    ra = T.batch_step(a, model, prep, wd, step=1, total_steps=10, autocast=False)
    rb = T.batch_step(b, model, prep, wd, step=1, total_steps=10, autocast=False)
    assert ra == rb
    for k in a.sources:
        assert torch.equal(a.sources[k], b.sources[k])


def test_flat_sources_of_the_batch_arm(tiny):
    s = T.make_state(tiny["model"], "batch", 8, SEQ, "cpu", 2)
    flat = T.flat_sources(s, tiny["lay"])
    assert flat.shape == (sum(c + 1 for _, c in tiny["lay"]),) and flat.dtype == np.float32
    with pytest.raises(ValueError):
        T.flat_sources(T.make_state(tiny["model"], "per_document", 8, SEQ, "cpu", 2), tiny["lay"])
