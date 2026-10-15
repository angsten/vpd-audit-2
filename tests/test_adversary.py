"""Our adversary loop against the authors' `_run_pgd_loop`, on the tiny stand-in (`tiny_model.py`), on the CPU in float32.

These are G2's checks in miniature: the identity checks plan 3 (session 3), Section 6, names (label override equal to the
labels, frozen set empty, held-out scoring of the batch the source was found on), bitwise equality with the authors' loop
in sources, harm and gradients, the frozen-at-0 reference against the authors' weight_deltas=None path, the frozen-at-1
check, micro-batching, the stochastic construction against the authors' function under explicit generators, the saved
draw's reload, and the save hook.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import g2

from tiny_model import tiny_component_model, tiny_ids

DEV = "cpu"
N = 16


@pytest.fixture(scope="module")
def setup():
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    prep = A.prepare(model, tiny_ids(N), "fp32", device=DEV)
    g = torch.Generator().manual_seed(5)
    start = {k: torch.rand((1, 1, model.module_to_c[k] + 1), generator=g).numpy() for k in model.target_module_paths}
    return model, prep, start


def test_ours_equals_the_authors_bitwise(setup):
    model, prep, start = setup
    theirs = g2.authors_loop(model, prep, start, 20, device=DEV)
    ours = A.run(model, prep, start, 20, 0.1, record_sources=True, record_grads=True, device=DEV)
    c = g2.compare_runs(theirs, ours)
    assert c["sources_bitwise_equal_every_step"] and c["harm_bitwise_equal_every_step"]
    assert np.array_equal(theirs["grad_record"].view(np.uint32), ours["grad_record"].view(np.uint32))
    assert theirs["record"][-1] > theirs["record"][0]  # the adversary does something
    moved = (theirs["source_record"][1:] != theirs["source_record"][:-1]).any(axis=1)
    assert moved.all()


def test_the_authors_loop_is_reproducible_and_its_hooks_see_their_gradient(setup):
    model, prep, start = setup
    a = g2.authors_loop(model, prep, start, 5, device=DEV)
    b = g2.authors_loop(model, prep, start, 5, device=DEV)
    assert g2.compare_runs(a, b)["sources_bitwise_equal_every_step"]
    for k in range(5):  # their own update is the sign of the gradient the hook captured
        expect = np.clip(a["source_record"][k] + np.float32(0.1) * np.sign(a["grad_record"][k]).astype(np.float32), 0, 1)
        assert np.allclose(expect, a["source_record"][k + 1], atol=1e-7)


def test_frozen_at_0_equals_the_authors_path_without_deltas(setup):
    model, prep, start = setup
    theirs = g2.authors_loop(model, prep, start, 20, with_delta=False, device=DEV)
    ours = A.run(model, prep, start, 20, 0.1, frozen=A.Frozen.delta_entries(model, 0.0, DEV), record_sources=True, device=DEV)
    comp = g2.component_positions(model)
    c = g2.compare_runs(theirs, {**ours, "source_record": ours["source_record"][:, comp]})
    assert c["sources_bitwise_equal_every_step"] and c["harm_bitwise_equal_every_step"]
    assert (ours["source_record"][:, g2.delta_positions(model)] == 0).all()


def test_frozen_at_1(setup):
    model, prep, start = setup
    theirs = g2.authors_loop(model, prep, start, 1, delta_value=1.0, device=DEV)
    ours = A.run(model, prep, start, 1, 0.1, frozen=A.Frozen.delta_entries(model, 1.0, DEV), record_sources=True, device=DEV)
    comp, dpos = g2.component_positions(model), g2.delta_positions(model)
    assert np.array_equal(theirs["source_record"][1][comp].view(np.uint32), ours["source_record"][1][comp].view(np.uint32))
    long = A.run(model, prep, start, 20, 0.1, frozen=A.Frozen.delta_entries(model, 1.0, DEV), record_sources=True, record_grads=True, device=DEV)
    assert (long["source_record"][:, dpos] == 1).all()
    for k in range(20):
        s, g = long["source_record"][k][comp], long["grad_record"][k][comp]
        expect = np.clip(s + np.float32(0.1) * np.sign(g).astype(np.float32), 0, 1)
        assert np.allclose(expect, long["source_record"][k + 1][comp], atol=1e-7)


def test_identity_checks(setup):
    model, prep, start = setup
    plain = A.run(model, prep, start, 5, 0.1, record_sources=True, device=DEV)
    override = A.run(model, prep, start, 5, 0.1, labels={k: v.clone() for k, v in prep.labels.items()}, record_sources=True, device=DEV)
    empty = A.run(model, prep, start, 5, 0.1, frozen=A.Frozen.empty(model, DEV), record_sources=True, device=DEV)
    for other in (override, empty):
        c = g2.compare_runs(plain, other)
        assert c["sources_bitwise_equal_every_step"] and c["harm_bitwise_equal_every_step"]
    assert A.score(model, plain["sources"], A.prepare(model, prep.ids, "fp32", device=DEV), device=DEV) == plain["final"]
    sched = A.run(model, prep, start, 5, lambda k: 0.1, record_sources=True, device=DEV)
    assert g2.compare_runs(plain, sched)["sources_bitwise_equal_every_step"]


def test_overridden_labels_form_the_mask_from_the_zeroed_labels(setup):
    model, prep, start = setup
    from param_decomp.metrics.pgd_utils import _construct_mask_infos_from_adv_sources

    k = model.target_module_paths[0]
    lab = {kk: v.clone() for kk, v in prep.labels.items()}
    lab[k][0, 3, :] = 0.0
    src = A.start_tensors(start, model, DEV)
    infos = _construct_mask_infos_from_adv_sources(src, lab, prep.weight_deltas, "all", lab[k].shape[:-1])
    r = src[k][..., :-1].expand(*lab[k].shape[:-1], -1)
    assert torch.equal(infos[k].component_mask, lab[k] + (1 - lab[k]) * r)
    assert torch.equal(infos[k].component_mask[0, 3], r[0, 3])


def test_micro_batching(setup):
    model, prep, start = setup
    whole = A.run(model, prep, start, 3, 0.1, device=DEV)
    for m in (4, 8):
        mb = A.run(model, prep, start, 3, 0.1, micro_batch=m, device=DEV)
        assert abs(mb["record"][0] - whole["record"][0]) <= 1e-6 * whole["record"][0]
    res, _ = g2.micro_validation(model, prep, start, sizes=(4, 8), n_steps=5, device=DEV)
    assert res["passes"], res["sizes"]


def test_stochastic_construction_against_the_authors_function_and_reload(setup, tmp_path):
    model, prep, start = setup
    ref = g2.stochastic_reference(model, prep, ["v1", "v2", "v3", "v4"], [0, 1, 2, 3], 1, 0)
    assert ref["passes"], ref["masks_bitwise_equal"]
    routed = torch.stack([ref["mask_infos"][k].routing_mask for k in ref["mask_infos"]])
    assert routed.any() and (~routed).any()
    rl = g2.reload_check(model, prep, ref, tmp_path / "draw.npz")
    assert rl["passes"]


def test_micro_batching_one_chunk_is_bitwise_and_smaller_chunks_keep_the_sources(setup):
    """Plan 5, item 2. One chunk of N texts (N = the batch, for N = 8 and 16) runs the micro-batched branch and equals the
    whole-batch path bit for bit in sources, harm, and gradients. Chunks smaller than the batch sum in another order:
    the sources and gradient signs stay bitwise equal, and the harm and gradient values agree to float32 rounding."""
    model, prep, start = setup
    for n in (8, 16):
        p = A.prepare(model, tiny_ids(n, seed=7), "fp32", device=DEV)
        whole = A.run(model, p, start, 10, 0.1, record_sources=True, record_grads=True, device=DEV)
        one = A.run(model, p, start, 10, 0.1, micro_batch=n, record_sources=True, record_grads=True, device=DEV)
        c = g2.compare_runs(whole, one)
        assert c["sources_bitwise_equal_every_step"] and c["harm_bitwise_equal_every_step"], n
        assert np.array_equal(whole["grad_record"].view(np.uint32), one["grad_record"].view(np.uint32)), n
    whole = A.run(model, prep, start, 10, 0.1, record_sources=True, record_grads=True, device=DEV)
    for n in (2, 4, 8):
        mb = A.run(model, prep, start, 10, 0.1, micro_batch=n, record_sources=True, record_grads=True, device=DEV)
        assert g2.compare_runs(whole, mb)["sources_bitwise_equal_every_step"], n
        assert np.array_equal(np.sign(whole["grad_record"]), np.sign(mb["grad_record"])), n
        assert max(abs(x / y - 1) for x, y in zip(mb["record"], whole["record"])) < 1e-6, n


def test_the_comparator_flags_an_altered_run(setup):
    """Plan 5, item 3: one source entry changed after step 1, by the smallest float32 step, is flagged; so is a harm
    changed in its last bit."""
    model, prep, start = setup
    theirs = g2.authors_loop(model, prep, start, 5, device=DEV)
    altered = {**theirs, "source_record": theirs["source_record"].copy(), "record": list(theirs["record"])}
    v = altered["source_record"][1, 7]
    altered["source_record"][1, 7] = np.nextafter(v, np.float32(2), dtype=np.float32)
    c = g2.compare_runs(theirs, altered)
    assert not c["sources_bitwise_equal_every_step"]
    assert c["entries_differing_per_step"] == [0, 1, 0, 0, 0, 0]
    assert c["harm_bitwise_equal_every_step"]
    altered["record"][3] = float(np.nextafter(np.float64(altered["record"][3]), np.inf))
    assert not g2.compare_runs(theirs, altered)["harm_bitwise_equal_every_step"]


def test_held_out_scoring_uses_the_scored_batch_own_labels(setup):
    """Plan 5, item 4: a source found on batch A, scored on batch B, equals a direct forward with B's labels and target,
    and differs from the same forward with A's labels, and from its score on A."""
    model, prep_a, start = setup
    prep_b = A.prepare(model, tiny_ids(N, seed=2), "fp32", device=DEV)
    found = A.run(model, prep_a, start, 5, 0.1, device=DEV)
    on_b = A.score(model, found["sources"], prep_b, device=DEV)
    src = {k: torch.from_numpy(v) for k, v in found["sources"].items()}
    with torch.no_grad():
        s, n = A._forward(model, prep_b.ids, src, prep_b.labels, prep_b.target_out, prep_b.weight_deltas)
        s_wrong, _ = A._forward(model, prep_b.ids, src, prep_a.labels, prep_b.target_out, prep_b.weight_deltas)
    assert on_b == float(s) / n
    assert on_b != float(s_wrong) / n
    assert on_b != A.score(model, found["sources"], prep_a, device=DEV)


def test_save_hook_threshold_crossed_mid_run(setup):
    """Plan 5, item 5: a threshold first crossed by the two-step mean at step 5 saves the source after step 5, and
    nothing at an earlier step."""
    model, prep, start = setup
    ref = A.run(model, prep, start, 12, 0.1, record_sources=True, device=DEV)
    r = np.array(ref["record"])
    mean2 = 0.5 * (r[:-1] + r[1:])  # mean2[k - 1] is the two-step mean at step k
    k_star = 5
    below = mean2[: k_star - 1].max()
    assert mean2[k_star - 1] > below, "the fixture's harm must first reach the threshold at step 5"
    h = float(0.5 * (below + mean2[k_star - 1]))
    hook = A.SaveHook(steps=(), thresholds=(h,))
    out = A.run(model, prep, start, 12, 0.1, save_hook=hook, device=DEV)
    assert out["record"] == ref["record"]
    assert list(hook.events.values()) == [k_star] and len(hook.saved) == 1
    assert np.array_equal(next(iter(hook.saved.values())), ref["source_record"][k_star])


def test_save_hook(setup):
    model, prep, start = setup
    hook = A.SaveHook(steps=(4, 8), thresholds=(0.0, 1e9))
    out = A.run(model, prep, start, 8, 0.1, save_hook=hook, record_sources=True, device=DEV)
    assert set(hook.saved) == {"step_3", "step_4", "step_7", "step_8", "two_step_mean_reaches_0"}
    assert hook.events["two_step_mean_reaches_0"] == 1
    for k in (3, 4, 7, 8):
        assert np.array_equal(hook.saved[f"step_{k}"], out["source_record"][k])
