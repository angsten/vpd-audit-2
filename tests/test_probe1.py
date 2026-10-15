"""Session 7, plan 5: probe 1's computation on the tiny model (`vpd_audit_2/probe1.py`).

  - The first-order push of an entry equals a central finite difference of the same move, at the intact model and at the
    full pattern, for components and delta entries (float64, so the difference is precise).
  - The intact forward kept across settings gives the same pushes as one setting at a time, and a chunk of texts the
    same as the whole batch.
  - The exact one-at-a-time pushes equal moves computed independently on the whole batch.
  - The reference direction is centred and of unit length; the pattern's forward is the authors' scoring path.
  - The validation's component draw and its pass rule, by hand.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import pilot as P
from vpd_audit_2 import probe1 as P1

from tiny_model import tiny_component_model, tiny_ids


def _setup(dtype: torch.dtype = torch.float64, n: int = 4, seed: int = 0):
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    if dtype == torch.float64:
        model = model.double()
    lay = [(k, int(model.module_to_c[k])) for k in model.target_module_paths]
    ids = tiny_ids(n, seed=7)
    prep = A.prepare(model, ids, "fp32", device="cpu")
    batch = P1.as_float32_batch(model, prep, lay)
    setting = np.random.default_rng(seed).random(P1.n_entries(lay)).astype(np.float32)
    return model, lay, prep, batch, setting


def _rms_norm_in_input_dtype(self, hidden_states):
    """The target's `LlamaRMSNorm.forward` without its cast to float32, so that the float64 model is float64 throughout
    and a finite difference is precise (the cast leaves float32 rounding of about 1e-7 in every logit)."""
    variance = hidden_states.pow(2).mean(-1, keepdim=True)
    return self.weight * (hidden_states * torch.rsqrt(variance + self.variance_epsilon))


@pytest.fixture(scope="module")
def f64():
    from param_decomp.pretrain.models.llama_simple_mlp import LlamaRMSNorm

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(LlamaRMSNorm, "forward", _rms_norm_in_input_dtype)
        yield _setup(torch.float64)


def _projection_at(model, batch, point, direction, x: int, e: int, h: float) -> float:
    """sum_t <z(x, t), direction(x, t)> with entry e of text x moved by h from the point."""
    sc = P1.scales_at(batch.n_texts, batch.lay, point, device="cpu", dtype=batch.dtype, requires_grad=False)
    name, local = P1.entry_of(e, batch.lay)
    sc[name][x, 0, local] += h
    with torch.no_grad():
        z = P1.logits_at(model, batch, {k: 1.0 - v for k, v in sc.items()})
    return float((z[x] * direction[x]).sum())


def test_layout_helpers(f64):
    _, lay, _, _, _ = f64
    n = P1.n_entries(lay)
    assert P1.delta_positions(lay).tolist() == (np.cumsum([c + 1 for _, c in lay]) - 1).tolist()
    assert P1.component_positions(lay).size == n - len(lay)
    for e in (0, 5, n - 1, int(P1.delta_positions(lay)[3])):
        name, local = P1.entry_of(e, lay)
        assert P1.module_offsets(lay)[[k for k, _ in lay].index(name)] + local == e
    assert P1.entry_of(int(P1.delta_positions(lay)[0]), lay) == (lay[0][0], lay[0][1])


def test_first_order_push_equals_a_central_difference(f64):
    model, lay, _, batch, setting = f64
    out = P1.first_order_pushes(model, batch, setting, ("intact", "pattern"))
    z_i, _ = P1.forward_at(model, batch, None, grad=False)
    z_p, _ = P1.forward_at(model, batch, P1.pattern_point(setting), grad=False)
    direction, _ = P1.reference_direction(z_p, z_i)
    rnd = P1.rounded(setting)
    off = np.flatnonzero(rnd == 0)
    kept = np.flatnonzero(rnd == 1)
    deltas = P1.delta_positions(lay)
    entries = [int(off[0]), int(off[len(off) // 2]), int(kept[0]), int(kept[-1]), int(deltas[0]), int(deltas[-1])]
    h = 2e-5
    checked = 0

    def central(point, x: int, e: int, step: float) -> float:
        return (_projection_at(model, batch, point, direction, x, e, step) - _projection_at(model, batch, point, direction, x, e, -step)) / (2 * step)

    for point_name, point in (("intact", None), ("pattern", P1.pattern_point(setting))):
        for x in (0, 3):
            for e in entries:
                fd = (4 * central(point, x, e, h / 2) - central(point, x, e, h)) / 3  # Richardson: the h^2 term cancels
                p = float(out[point_name][x, e])
                assert p == pytest.approx(fd, rel=1e-6, abs=1e-6), (point_name, x, e)
                checked += abs(p) > 1e-3
    assert checked >= 12  # most of the checked pushes are not trivially zero


def test_kept_intact_forward_equals_one_setting_at_a_time(f64):
    model, lay, _, batch, setting = f64
    other = np.random.default_rng(5).random(setting.size).astype(np.float32)
    graph = P1.IntactGraph(model, batch)
    both = [P1.cell(model, batch, graph, s, ("intact", "pattern")) for s in (setting, other)]
    graph.release()
    for s, got in zip((setting, other), both):
        alone = P1.first_order_pushes(model, batch, s, ("intact", "pattern"))
        for key in ("intact", "pattern", "delta_norm_sum", "pattern_kl", "zero_direction_positions"):
            np.testing.assert_allclose(got[key], alone[key], rtol=1e-12, atol=1e-14)
    assert not np.allclose(both[0]["intact"], both[1]["intact"])  # the direction depends on the setting


def test_a_chunk_of_texts_gives_the_whole_batchs_rows(f64):
    model, _, _, batch, setting = f64
    whole = P1.first_order_pushes(model, batch, setting, ("intact", "pattern"))
    for rows in (slice(0, 2), slice(2, 4)):
        part = P1.first_order_pushes(model, batch.take(rows), setting, ("intact", "pattern"))
        for key in ("intact", "pattern", "delta_norm_sum", "pattern_kl"):
            np.testing.assert_allclose(part[key], whole[key][rows], rtol=1e-11, atol=1e-13)


def test_exact_pushes_equal_moves_on_the_whole_batch(f64):
    model, lay, _, batch, setting = f64
    z_i, _ = P1.forward_at(model, batch, None, grad=False)
    z_p, _ = P1.forward_at(model, batch, P1.pattern_point(setting), grad=False)
    direction, _ = P1.reference_direction(z_p, z_i)
    off = np.flatnonzero(P1.rounded(setting) == 0)
    pairs = [(int(e), t) for t in (1, 2) for e in off[:5]] + [(int(P1.delta_positions(lay)[2]), 2)]
    got = P1.exact_pushes(model, batch, pairs, direction, chunk=3)  # several chunks per text
    for k, (e, t) in enumerate(pairs):
        want = _projection_at(model, batch, None, direction, t, e, 1.0) - _projection_at(model, batch, None, direction, t, e, 0.0)
        assert got["exact"][k] == pytest.approx(want, rel=1e-9, abs=1e-10)
    assert len(got["null_spread"]) == 3 + 3 and max(got["null_spread"]) < 1e-9  # two pairs per chunk: 5 pairs on text 1, 6 on text 2


def test_reference_direction_is_centred_and_of_unit_length():
    g = torch.Generator().manual_seed(3)
    z_i = torch.randn(2, 3, 7, generator=g, dtype=torch.float64)
    z_p = z_i + torch.randn(2, 3, 7, generator=g, dtype=torch.float64)
    z_p[1, 2] = z_i[1, 2] + 4.0  # a shift by a constant is no shift once centred
    d, norm = P1.reference_direction(z_p, z_i)
    assert torch.allclose(d.sum(dim=-1), torch.zeros(2, 3, dtype=torch.float64), atol=1e-12)
    n = torch.linalg.vector_norm(d, dim=-1)
    assert torch.allclose(n[norm > 0], torch.ones_like(n[norm > 0])) and norm[1, 2] == pytest.approx(0.0, abs=1e-12)
    assert float(n[1, 2]) <= 1.0  # exactly zero or rounding dust of a unit vector, never larger
    raw = (z_p - z_i)[0, 0]
    raw = raw - raw.mean()
    assert torch.allclose(d[0, 0], raw / torch.linalg.vector_norm(raw))


def test_the_patterns_forward_is_the_authors_scoring_path():
    model, lay, prep, batch, setting = _setup(torch.float32)
    rnd = P1.rounded(setting)
    z_p, _ = P1.forward_at(model, batch, P1.pattern_point(setting), grad=False)
    with torch.no_grad():
        z_r = P1.logits_at(model, batch, {k: torch.from_numpy(v) for k, v in P.unflatten(rnd, lay).items()})
    assert torch.equal(z_p, z_r)  # the pattern point's sources are exactly the rounded setting
    ours = float(P1.kl_per_text(prep.target_out, z_p).mean())
    authors = A.score(model, P.unflatten(rnd, lay), prep, device="cpu")
    assert ours == pytest.approx(authors, rel=1e-5) and authors > 0.01
    z_i, _ = P1.forward_at(model, batch, None, grad=False)
    chk = P1.intact_against_target(model, batch, z_i)
    assert chk["max_text_kl"] < 1e-6 and chk["max_abs_logit_difference"] < 0.05  # the tiny model's logits reach about 100


def test_validation_components_by_deciles():
    rng = np.random.default_rng(1)
    first = rng.normal(size=(8, 3000)) * np.exp(rng.normal(size=3000))
    first[:, 10:20] = 0.0  # null moves on every text
    off = np.arange(0, 3000, 2)
    a = P1.validation_components(first, off, seed=42)
    b = P1.validation_components(first, off, seed=42)
    assert np.array_equal(a["components"], b["components"]) and a["components"].size == 200 and np.unique(a["components"]).size == 200
    assert a["left_out_zero"] == 5 and a["candidates"] == 1495 and set(a["components"]) <= set(off) - set(range(10, 20))
    m = np.abs(first).mean(axis=0)
    by = [m[a["components"][a["decile"] == d]] for d in range(10)]
    assert all(by[d].size == 20 for d in range(10)) and all(by[d].max() <= by[d + 1].min() for d in range(9))


def test_the_pass_rule_by_hand():
    first = np.array([0.001, -0.002, 0.5, -0.6, 0.7, 0.8, -0.9, 1.0, 1.1, -1.2])
    exact = np.array([-0.001, 0.002, 0.45, -0.5, 0.75, 0.7, -1.0, 1.2, 1.0, -1.1])
    r = P1.pass_rule(first, exact)
    # the 10th percentile of |p| is 0.001 + 0.1 * (0.002 - 0.001) * 9 = 0.0019; the first pair is at or below it
    assert r["bottom_decile_cut"] == pytest.approx(0.0019) and r["pairs_above"] == 9
    assert r["sign_share_above"] == pytest.approx(8 / 9) and r["sign_share_all"] == pytest.approx(8 / 10)
    assert r["passes"] is False  # 8 of 9 is below 90 percent
    exact[1] = -0.002
    r = P1.pass_rule(first, exact)
    assert r["sign_share_above"] == 1.0 and r["spearman_all"] >= 0.8 and r["passes"] is True
    with pytest.raises(ValueError):
        P1.pass_rule(first, exact[:-1])
