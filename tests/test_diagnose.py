"""Plan 4's diagnostics on the tiny stand-in, on the CPU (where CUDA autocast is disabled, so "bf16" runs in float32):
D1's comparison, D2's four gradients, the run of one cell, the readings of D3 and D4, and D5's trace."""

from __future__ import annotations

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import diagnose as D
from vpd_audit_2 import g2, g3

from tiny_model import tiny_component_model, tiny_ids

DEV = "cpu"


@pytest.fixture(scope="module")
def setup():
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    ids = tiny_ids(16).numpy()
    g = torch.Generator().manual_seed(5)
    start = {k: torch.rand((1, 1, model.module_to_c[k] + 1), generator=g).numpy() for k in model.target_module_paths}
    return model, ids, start


def test_d1_is_bitwise_on_the_tiny_model(setup):
    model, ids, start = setup
    ref = g2.authors_loop(model, A.prepare(model, ids, "bf16", device=DEV), start, D.N_STEPS, D.STEP, capture_grads=False, device=DEV)
    out = D.d1(model, ids, start, ref["record"], D.sources_sha256(ref["sources"]), log=lambda *_: None, device=DEV)
    assert out["bitwise"] and out["step1_gradient_bitwise_equal"] and out["first_step_sources_differ"] is None
    assert out["plateau"]["ours"] == D.plateau(ref["record"])


def test_d2_gives_four_gradients(setup):
    model, ids, start = setup
    hook = A.SaveHook(steps=(20, 40, 80), thresholds=())
    A.run(model, A.prepare(model, ids, "bf16", device=DEV), start, 80, 0.1, micro_batch=8, save_hook=hook, device=DEV)
    out = D.d2(model, ids, hook.saved, log=lambda *_: None, device=DEV)
    for s in ("20", "40", "80"):
        row = out["per_step"][s]
        for name in ("bf16_whole", "bf16_micro8", "bf16_micro16"):
            assert 0 <= row[name]["fraction_differing_nonzero_ref"] <= 1
        assert row["fp32_ref_full_float32_against_ref"]["fraction_differing_nonzero_ref"] == 0  # on the CPU both are float32


def test_run_cell_and_readings(setup):
    model, ids, start = setup
    a = D.run_cell(model, ids, start, authors=True, micro_batch=None, log=lambda *_: None, device=DEV)
    o = D.run_cell(model, ids, start, authors=False, micro_batch=8, log=lambda *_: None, device=DEV)
    assert len(a["record"]) == len(o["record"]) == 321 and a["source_record_to_40"].shape[0] == 41
    base = [float(k) for k in range(321)]
    up = [x + 1 for x in base]
    r3 = D.d3_reading({j: up for j in range(2, 9)}, {j: base for j in range(2, 9)})
    assert r3["count_ours_above_G1"] == 7 and r3["reading"].startswith("micro-batching raises") and abs(r3["one_sided_sign_test_p"] - 0.0078125) < 1e-12
    authors = [{"record": [x + 0.01 * k for x in base], "plateau": 310.5 + 0.01 * k, "source_record_to_40": np.full((41, 3), float(k), np.float32),
                "final_sources_sha256": str(k)} for k in range(8)]
    ours = [{"record": [x + 5 + 0.01 * k for x in base], "plateau": 315.5 + 0.01 * k, "final_sources_sha256": str(k)} for k in range(8)]
    r4 = D.d4_reading(authors, ours)
    assert r4["mann_whitney_exact_one_sided_p"] < 0.001 and r4["reading"].startswith("micro-batching raises") and not r4["void"]
    assert not r4["authors_sources_identical_through_step_40"] and r4["authors_distinct_final_sources"] == 8


def test_perturbed_start_moves_one_entry_by_one_bf16_ulp(setup):
    model, ids, start = setup
    s2, info = D.perturbed_start(start, 3)
    diff = [(k, np.flatnonzero(s2[k] != start[k])) for k in start]
    changed = [(k, d) for k, d in diff if d.size]
    assert len(changed) == 1 and changed[0][1].size == 1 and changed[0][0] == info["module"]
    x, y = info["value"], info["new_value"]
    assert torch.tensor(x).to(torch.bfloat16).item() != torch.tensor(y).to(torch.bfloat16).item()
    assert abs(y - x) == info["bf16_ulp"]


def test_d4_reading_is_void_when_the_sources_match_and_the_harm_differs_in_its_last_bits():
    """Plan 5, item 8: the case that occurred. The authors' sources are identical across permutations, while the harm
    readout differs in its last bits; the reading must be the void case, with the two flags reported apart."""
    base = [1.0 + 0.1 * k for k in range(321)]
    src = np.full((41, 5), 0.25, np.float32)
    authors = []
    for k in range(8):
        rec = [float(np.nextafter(x, np.inf)) if (k and j >= 3) else x for j, x in enumerate(base)]
        authors.append({"record": rec, "plateau": D.plateau(rec), "source_record_to_40": src.copy(), "final_sources_sha256": "same"})
    ours = [{"record": [x + 9 for x in base], "plateau": D.plateau(base) + 9 + 0.01 * k, "final_sources_sha256": str(k % 3)} for k in range(8)]
    r = D.d4_reading(authors, ours)
    assert r["authors_sources_identical_through_step_40"] and not r["authors_harm_identical_through_step_40"]
    assert r["void"] and r["authors_distinct_final_sources"] == 1 and r["ours_distinct_final_sources"] == 3


def test_d3_reading_at_six_and_five_of_seven():
    """Plan 5, item 9."""
    base = [float(k) for k in range(321)]
    g1 = {j: base for j in range(2, 9)}
    for n_up, reading in ((6, "suggestive; undetermined"), (5, "not shown")):
        ours = {j: ([x + 1 for x in base] if j < 2 + n_up else [x - 1 for x in base]) for j in range(2, 9)}
        r = D.d3_reading(ours, g1)
        assert r["count_ours_above_G1"] == n_up and r["reading"] == reading


def test_perturbed_start_moves_down_when_up_would_reach_1(setup):
    """Plan 5, item 10: every entry at 0.999, so x + ulp >= 1 and the entry moves down by its bf16 ulp, 2^-8."""
    model, _, _ = setup
    high = {k: np.full((1, 1, model.module_to_c[k] + 1), 0.999, np.float32) for k in model.target_module_paths}
    s2, info = D.perturbed_start(high, 1)
    x, y = info["value"], info["new_value"]
    assert info["bf16_ulp"] == 2.0 ** -8 and y == x - 2.0 ** -8 and y < x
    flat = s2[info["module"]].reshape(-1)
    assert float(flat[info["index_in_module"]]) == y
    assert sum(int((s2[k] != high[k]).sum()) for k in high) == 1


def test_departure_from_the_unperturbed_twin(setup):
    """Plan 5, item 11: a one-ulp perturbed start departs from its twin, at a recorded step; a twin against itself does
    not; and a change confined to the perturbed entry, with the harm unchanged, is not a departure."""
    model, ids, start = setup
    prep = A.prepare(model, ids, "bf16", device=DEV)
    twin = g2.authors_loop(model, prep, start, 40, D.STEP, capture_grads=False, device=DEV)
    pert_start, info = D.perturbed_start(start, 2)
    pert = g2.authors_loop(model, prep, pert_start, 40, D.STEP, capture_grads=False, device=DEV)
    d = D.departure(pert, twin, perturbed_entry=info["entry"])
    assert d["departs"] and d["first_departure_step"] is not None and d["first_departure_step"] <= 40
    assert not D.departure(twin, twin)["departs"]
    inert = {"record": list(twin["record"]), "source_record": twin["source_record"].copy()}
    inert["source_record"][:, info["entry"]] += np.float32(2.0 ** -8)
    assert not D.departure(inert, twin, perturbed_entry=info["entry"])["departs"]
    assert D.departure(inert, twin)["first_departure_step"] == 0  # without naming the entry, the injected change shows


def test_d5_traces_and_sees_the_float32_norm(setup):
    model, _, _ = setup
    ids = tiny_ids(32).numpy()
    out = g3.float64_oddity(model, ids, [f"v{i}" for i in range(32)], top=1, device=DEV, log=lambda *_: None)
    assert out["model_restored_to_float32"]
    top = out["backgrounds"]["stochastic"]["top_positions"][0]
    assert top["modules_in_forward_order"]
    rel = [v["max_relative_difference_from_float64_formula"] for v in top["rms_norms"].values()]
    assert rel and max(rel) > 1e-12  # the authors' LlamaRMSNorm computes in float32 even in a float64 model
