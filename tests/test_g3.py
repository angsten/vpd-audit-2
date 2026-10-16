"""G3's arithmetic: the effect formula against the direct difference of two KL divergences, and the gate's run on the
tiny stand-in (CPU, float32), its controls, and its float64 path."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import g3

from tiny_model import tiny_component_model, tiny_ids


def test_effect_is_the_difference_of_two_kl_divergences():
    g = torch.Generator().manual_seed(0)
    target = 5 * torch.randn((7, 50), generator=g)
    base = target + 0.5 * torch.randn((7, 50), generator=g)
    test = base + 0.01 * torch.randn((7, 50), generator=g)
    e = g3.effect(test, base, target)
    lp = torch.log_softmax(target.double(), -1)
    kl = lambda logits: (lp.exp() * (lp - torch.log_softmax(logits.double(), -1))).sum(-1)  # noqa: E731
    ref = kl(test) - kl(base)
    assert torch.allclose(e, ref, rtol=1e-9, atol=1e-15)
    assert torch.equal(g3.effect(base, base, target), torch.zeros(7, dtype=torch.float64))


def test_floor_takes_the_absolute_position0_sum():
    e = np.zeros((4, 3))
    e[0] = [1e-9, -3e-9, 0]
    e[1, 2] = 5e-10
    f = g3.floor(e, 1e-8)
    assert f["position0_summed_null"]["signed"][0] == pytest.approx(-2e-9)
    assert f["position0_summed_null"]["max_abs"] == pytest.approx(2e-9)
    assert f["below_line"]


@pytest.fixture(scope="module")
def tiny_run():
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    ids = tiny_ids(32).numpy()
    return model, ids, g3.run_g3(model, ids, [f"v{i}" for i in range(32)], line=1e-6, device="cpu", log=lambda *_: None)


def test_g3_runs_and_its_controls_are_label_zero_low_norm_and_causal(tiny_run):
    model, ids, out = tiny_run
    for bg in g3.GATING + g3.RECORDED:
        assert np.isfinite(out["backgrounds"][bg]["position0_summed_null"]["p99_abs"])
    assert out["backgrounds"]["all_on"]["base_kl_mean_nats"] < out["backgrounds"]["at_labels"]["base_kl_mean_nats"]
    for c in out["controls"]["chosen"]:
        assert c["candidates"] >= 1
    # Plan 5 of the research log, item 12: each control's label is exactly 0 at its position, and its weight norm ranks among the lowest
    # tenth of its own matrix (max(1, C_l // 10) smallest; on the tiny model, the single smallest).
    from vpd_audit.sources import module_offsets
    from vpd_audit.weight_norms import weight_norms

    from vpd_audit_2 import adversary as A

    prep = A.prepare(model, ids, "fp32", device="cpu")
    norms, _ = weight_norms(model)
    offsets = module_offsets(model.module_to_c)
    for c in out["controls"]["chosen"]:
        assert float(prep.labels[c["module"]][c["row"], c["position"], c["c"]]) == 0.0, c
        C = model.module_to_c[c["module"]]
        nk = norms[offsets[c["module"]] : offsets[c["module"]] + C]
        lowest = set(np.argsort(nk, kind="stable")[: max(1, C // 10)].tolist())
        assert c["c"] in lowest and c["weight_norm"] == nk[c["c"]], c
    for bg in g3.CONTROL_BACKGROUNDS:
        rows = out["controls"]["backgrounds"][bg]["rows"]
        assert all(r["before_position_exact_zero_32"] for r in rows)
        assert any(r["effect_grouping_32"] != 0 for r in rows)


def test_float64_path(tiny_run):
    model, ids, out = tiny_run
    r = g3.run_all_on_float64(model, ids, 1e-6, device="cpu")
    assert r["dtype"] == "float64" and np.isfinite(r["position0_summed_null"]["p99_abs"])
    assert next(model.parameters()).dtype == torch.float32


def test_float64_diagnostic_uses_the_same_masks_and_shrinks_the_floor(tiny_run):
    model, ids, out = tiny_run
    r = g3.run_float64_diagnostic(model, ids, [f"v{i}" for i in range(32)], 1e-6, device="cpu", log=lambda *_: None)
    assert r["model_restored_to_float32"]
    for bg in ("at_labels", "stochastic"):
        f32 = out["backgrounds"][bg]
        f64 = r["float64"][bg]
        assert f64["position0_summed_null"]["p99_abs"] < f32["position0_summed_null"]["p99_abs"]
        assert abs(f64["base_kl_mean_nats"] / f32["base_kl_mean_nats"] - 1) < 1e-4  # same masks, same base up to precision
