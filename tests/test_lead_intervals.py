"""The interval routine against the worked examples of its specification (plan 1, Section 6).

Every expected number here is copied from a document: `freeze/amendment1_specs/interval_spec.md` (Sections 4.1, 4.7,
5.3, and 7), `freeze/amendment1.md` (entry 2.3), `sessions/004/checkpoint.md` (Appendix D.1), and plan 1 (Section 12.3).
None was taken from this code's output.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.stats import t as student_t

from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_reading as LR
from vpd_audit_2.lead_intervals import Combo, Presence

# Daniel's Section 4.7: added harms, K = 2, n_s = 2.
OWN = np.array([[2.0, 4.0], [4.0, 6.0]])  # [held-out, start]
CARRIED = np.array([[[1.44, 2.04], [2.12, 2.88]], [[0.96, 1.72], [2.04, 2.80]]])  # [attack, held-out, start]


def _example_4_7() -> dict:
    return LI.interval(Combo(a_cells=CARRIED), Combo(h_cells=OWN), Presence.complete(2, 2, 2), indices=LI.enumerate_indices(2), batch_part="closed_form")


def test_daniel_4_7_ratio_and_cells():
    r = _example_4_7()
    assert r["estimate"] == pytest.approx(0.5, abs=1e-12)
    assert r["denominator"] == pytest.approx(4.0, abs=1e-12)
    # the four mean-over-starts cells
    assert r["lin_table"] == pytest.approx(np.array([[0.060, 0.000], [-0.040, -0.020]]), abs=1e-12)


def test_daniel_4_7_batch_part_equals_the_enumeration_of_all_16_outcomes():
    r = _example_4_7()
    idx = LI.enumerate_indices(2)
    assert idx.B == 16
    outcomes = LI.replicate_deviations(r["lin_table"], idx)
    assert r["v_closed"] == pytest.approx(0.0006, rel=1e-9)
    assert float(outcomes.var(ddof=0)) == pytest.approx(0.0006, rel=1e-9)
    assert float(outcomes.var(ddof=0)) == pytest.approx(r["v_closed"], rel=1e-12)
    assert r["v_pb"] == pytest.approx(0.0012, rel=1e-9)
    # row effects (0.03, -0.03), column effects (0.01, -0.01), residuals (0.02, -0.02, -0.02, 0.02)
    z = r["lin_table"]
    assert z.mean(axis=1) - z.mean() == pytest.approx([0.03, -0.03], abs=1e-12)
    assert z.mean(axis=0) - z.mean() == pytest.approx([0.01, -0.01], abs=1e-12)
    resid = z - z.mean(axis=1)[:, None] - z.mean(axis=0)[None, :] + z.mean()
    assert resid.ravel() == pytest.approx([0.02, -0.02, -0.02, 0.02], abs=1e-12)


def test_daniel_4_7_start_part_and_interval():
    r = _example_4_7()
    ms = r["mean_squares"]
    assert ms["S"] == pytest.approx(0.0098, rel=1e-9)
    assert ms["AS"] == pytest.approx(0.0002, rel=1e-9)
    assert ms["BS"] == pytest.approx(0.0002, rel=1e-9)
    assert ms["ABS"] == pytest.approx(0.0002, rel=1e-9)
    assert r["sigma_c_sq"] == pytest.approx(0.0024, rel=1e-9)
    assert r["v_c"] == pytest.approx(0.0012, rel=1e-9)
    assert r["nu_c_untruncated"] == pytest.approx(0.96, abs=0.005)
    assert r["nu_c"] == 1.0  # raised to 1
    assert r["nu"] == pytest.approx(2.0, abs=1e-9)
    assert r["t_quantile"] == pytest.approx(4.3027, abs=5e-5)
    assert r["half_width"] == pytest.approx(0.211, abs=5e-4)
    assert r["interval"] == pytest.approx([0.289, 0.711], abs=5e-4)
    assert r["interval_unwidened"] == r["interval"]


def test_daniel_4_7_beside_it():
    r = _example_4_7()
    assert r["per_start"] == pytest.approx([1.64 / 3, 2.36 / 5], abs=1e-12)
    assert r["per_start"] == pytest.approx([0.547, 0.472], abs=5e-4)
    # the replicate that draws attack batch 1 twice and held-out batch 1 twice
    idx = LI.enumerate_indices(2)
    k = next(n for n in range(idx.B) if (idx.idx_attack[n] == 0).all() and (idx.idx_heldout[n] == 0).all())
    linearized = r["estimate"] + LI.replicate_deviations(r["lin_table"], idx)[k]
    recomputed, used = LI.resampled_statistic(Combo(a_cells=CARRIED), Combo(h_cells=OWN), Presence.complete(2, 2, 2), idx)
    assert linearized == pytest.approx(0.56, abs=1e-12)
    assert used[k] and recomputed[k] == pytest.approx(0.58, abs=1e-12)  # 1.74 / 3: the two differ


def _example_5_3() -> dict:
    present = np.ones((2, 2), dtype=bool)
    present[1, 1] = False  # attack search (2, 2) never reaches the level
    carried = CARRIED.copy()
    carried[1, :, 1] = np.nan
    return LI.interval(Combo(a_cells=carried), Combo(h_cells=OWN), Presence(present, np.ones((2, 2), dtype=bool)),
                       indices=LI.enumerate_indices(2), batch_part="closed_form")


def test_daniel_5_3_one_attack_search_missing():
    r = _example_5_3()
    assert r["counts"] == {"C_A": 6.0, "C_H": 4.0}  # 6 carried cells, not 8; all 4 own searches (Amendment 1, entry 2.3)
    assert r["numerator"] == pytest.approx(11.48 / 6, abs=1e-12)
    assert r["numerator"] == pytest.approx(1.9133, abs=5e-5)
    assert r["denominator"] == pytest.approx(4.0, abs=1e-12)
    assert r["estimate"] == pytest.approx(0.4783, abs=5e-5)
    assert r["lin_table"] == pytest.approx(np.array([[0.0618, 0.0760], [-0.0393, -0.0985]]), abs=5e-5)
    assert float(r["lin_table"].sum()) == pytest.approx(0.0, abs=1e-12)
    z = r["lin_table"]
    assert np.abs(z.mean(axis=1) - z.mean()) == pytest.approx([0.0689, 0.0689], abs=5e-5)
    assert np.abs(z.mean(axis=0) - z.mean()) == pytest.approx([0.0113, 0.0113], abs=5e-5)
    resid = z - z.mean(axis=1)[:, None] - z.mean(axis=0)[None, :] + z.mean()
    assert np.abs(resid).ravel() == pytest.approx([0.0183] * 4, abs=5e-5)
    assert r["v_closed"] == pytest.approx(0.002520, abs=5e-7)
    assert r["v_pb"] == pytest.approx(0.005040, abs=5e-7)
    outcomes = LI.replicate_deviations(z, LI.enumerate_indices(2))
    assert float(outcomes.var(ddof=0)) == pytest.approx(r["v_closed"], rel=1e-12)
    # the sub-table has one attack batch, so the start part is not estimable
    assert r["start_part_not_estimable"] and r["v_c"] == 0.0 and r["subtable"]["K_A"] == 1


def test_checkpoint_appendix_d1():
    r = LI.interval_from_parts(0.0, 0.002857, {"S": 0.40, "AS": 0.10, "BS": 0.10, "ABS": 0.04}, K=8, K_A=8, K_H=8, n_s=3)
    assert r["sigma_c_sq"] == pytest.approx(0.00375, rel=1e-9)
    assert r["v_c"] == pytest.approx(0.00125, rel=1e-9)
    assert r["nu_c_untruncated"] == pytest.approx(0.71, abs=0.005)
    assert r["nu_c"] == 1.0  # raised to 1
    assert r["nu"] == pytest.approx(6.2, abs=0.05)
    assert r["v_pb"] + r["v_c"] == pytest.approx(0.004107, abs=5e-7)
    assert r["half_width"] == pytest.approx(0.156, abs=5e-4)


def _two_heldout_batches() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Daniel's Section 4.1: carried, own, and shuffled harms 0.5 x (0.70, 0.83, 0.60) on the first held-out batch and
    1.5 x (0.70, 0.83, 0.60) on the second."""
    scale = np.array([0.5, 1.5])
    carried = np.broadcast_to((0.70 * scale)[None, :, None], (2, 2, 2)).copy()
    shuf = np.broadcast_to((0.60 * scale)[None, :, None], (2, 2, 2)).copy()
    own = np.broadcast_to((0.83 * scale)[:, None], (2, 2)).copy()
    return carried, own, shuf


def test_daniel_4_1_per_cell_shuffled_form_gives_zero_on_both_batches():
    carried, own, shuf = _two_heldout_batches()
    pres = Presence.complete(2, 2, 2)
    r = LI.interval(Combo(a_cells=carried - shuf), Combo(a_cells=-shuf, h_cells=own), pres, indices=LI.enumerate_indices(2), batch_part="closed_form")
    assert r["estimate"] == pytest.approx(0.10 / 0.23, abs=1e-12)
    assert r["estimate"] == pytest.approx(0.435, abs=5e-4)
    assert np.abs(r["lin_table"]).max() < 1e-12  # W = 0 on both held-out batches
    assert r["half_width"] < 1e-12
    # subtracting the grand mean 0.60 instead gives W = -0.74 and +0.74, a large spurious variance
    wrong = LI.interval(Combo(a_cells=carried - 0.60), Combo(h_cells=own - 0.60), pres, indices=LI.enumerate_indices(2), batch_part="closed_form")
    assert wrong["estimate"] == pytest.approx(r["estimate"], abs=1e-12)  # the point estimate is the same either way
    assert wrong["lin_table"][0] == pytest.approx([-0.74, 0.74], abs=0.005)
    assert wrong["v_closed"] > 0.1


def _random_arrays(K: int, n_s: int, seed: int, a_missing: list[tuple[int, int]] = (), b_missing: list[tuple[int, int]] = ()) -> dict:
    rng = np.random.default_rng(seed)
    start = 0.2 + 0.02 * rng.random((K, n_s))
    own = start + 3.0 + 2.0 * rng.random((K, n_s)) + rng.random(K)[:, None] + rng.random(n_s)[None, :]
    own20 = start + 0.5 + 0.2 * rng.random((K, n_s))
    attack_start = 0.2 + 0.02 * rng.random((K, n_s))
    attack_own = attack_start + 3.0 + 2.0 * rng.random((K, n_s))
    carried = start[None] + 0.6 * (attack_own - attack_start)[:, None, :] * (1 + 0.2 * rng.standard_normal((K, K, n_s)))
    shuffled = 0.4 * (1 + 0.1 * rng.standard_normal((K, K, n_s, 8)))
    a = np.ones((K, n_s), dtype=bool)
    b = np.ones((K, n_s), dtype=bool)
    for i, s in a_missing:
        a[i, s] = False
    for j, s in b_missing:
        b[j, s] = False
    carried = np.where(a[:, None, :], carried, np.nan)
    shuffled = np.where(a[:, None, :, None], shuffled, np.nan)
    attack_own = np.where(a, attack_own, np.nan)
    own = np.where(b, own, np.nan)
    return {"table": "level", "key": 5.0, "start": start, "own": own, "own20": own20, "carried": carried, "shuffled": shuffled,
            "attack_start": attack_start, "attack_own": attack_own, "attack_present": a, "heldout_present": b}


RATIOS = ("carries", "depends", "kappa", "pooled_retention")
MEANS = ("large", "carried_margin", "own_margin", "shuffled_vs_yardstick", "carried_added")


def test_every_harm_times_100_leaves_ratios_unchanged_and_scales_plain_means_by_100():
    arrays = _random_arrays(6, 4, seed=1, a_missing=[(0, 1)], b_missing=[(2, 3)])
    scaled = {k: (v * 100.0 if isinstance(v, np.ndarray) and v.dtype == np.float64 else v) for k, v in arrays.items()}
    idx = LI.make_indices(6, B=2000)
    pres = LR.presence_of(arrays)
    one, hundred = LR.nine_statistics(arrays), LR.nine_statistics(scaled)
    assert set(one) == set(RATIOS) | set(MEANS)
    for name in one:
        r1 = LI.interval(*one[name], pres, indices=idx)
        r100 = LI.interval(*hundred[name], pres, indices=idx)
        factor = 1.0 if name in RATIOS else 100.0
        for field in ("interval", "interval_unwidened", "interval_percentile"):
            assert r100[field] == pytest.approx([factor * x for x in r1[field]], rel=1e-9), (name, field)
        assert r100["estimate"] == pytest.approx(factor * r1["estimate"], rel=1e-9)
        assert r100["nu"] == pytest.approx(r1["nu"], rel=1e-6)


def test_a_table_with_no_dependence_on_the_start_gives_nu_k_minus_1_with_no_error():
    K, n_s = 16, 5
    rng = np.random.default_rng(3)
    cells = np.repeat((1.0 + rng.random((K, K)))[:, :, None], n_s, axis=2)
    own = np.repeat((2.0 + rng.random(K))[:, None], n_s, axis=1)
    pres = Presence.complete(K, K, n_s)
    idx = LI.make_indices(K, B=2000)
    for den in (None, Combo(h_cells=own)):
        r = LI.interval(Combo(a_cells=cells), den, pres, indices=idx)
        assert r["mean_squares"] == {"S": 0.0, "AS": 0.0, "BS": 0.0, "ABS": 0.0}
        assert r["v_c"] == 0.0
        assert r["nu"] == K - 1
        assert math.isfinite(r["half_width"]) and r["half_width"] > 0


def test_one_batch_with_no_searches_at_a_level():
    K, n_s = 6, 5
    arrays = _random_arrays(K, n_s, seed=4, a_missing=[(0, s) for s in range(n_s)], b_missing=[(1, s) for s in range(n_s)])
    pres = LR.presence_of(arrays)
    assert pres.C_A == K * (K - 1) * n_s and pres.C_H == (K - 1) * n_s
    idx = LI.make_indices(K, B=2000)
    for name, (num, den) in LR.nine_statistics(arrays).items():
        r = LI.interval(num, den, pres, indices=idx)
        assert r["defined"] and all(math.isfinite(x) for x in r["interval"]), name
        assert r["subtable"] == {"K_A": K - 1, "K_H": K - 1, "n_s": n_s}
        assert r["percentile"]["replicates_used"] + r["percentile"]["replicates_left_out"] == idx.B
    # the batch stays in the resampling and contributes no cells: its row of the resampled table is zero
    r = LI.interval(*LR.nine_statistics(arrays)["large"], pres, indices=idx)
    assert (r["lin_table"][0] == 0.0).all() and np.abs(r["lin_table"][1:]).max() > 0
    cells = arrays["carried"] - arrays["own20"][None]
    assert r["estimate"] == pytest.approx(float(np.nanmean(cells[1:])), rel=1e-12)


def test_a_mean_with_no_cells_in_a_replicate_is_counted_and_left_out():
    present = np.ones((2, 2), dtype=bool)
    present[1, :] = False  # attack batch 2 has no search at the level
    carried = CARRIED.copy()
    carried[1] = np.nan
    idx = LI.enumerate_indices(2)
    r = LI.interval(Combo(a_cells=carried), None, Presence(present, np.ones((2, 2), dtype=bool)), indices=idx, batch_part="closed_form")
    # of the 16 outcomes, the 4 that draw attack batch 2 twice have no cell
    assert r["percentile"] == {"replicates": 16, "replicates_used": 12, "replicates_left_out": 4,
                               "denominator_nonpositive_share": None, "unreliable": False}
    assert r["per_start"] == pytest.approx([(1.44 + 2.12) / 2, (2.04 + 2.88) / 2], abs=1e-12)


def test_undefined_inputs_are_reported_and_not_divided():
    pres = Presence.complete(2, 2, 2)
    r = LI.interval(Combo(a_cells=CARRIED), Combo(h_cells=OWN - 4.0), pres, indices=LI.enumerate_indices(2), batch_part="closed_form")
    assert r["defined"] is False and r["estimate"] is None and r["interval"] is None  # the denominator is exactly zero
    nothing = Presence(np.zeros((2, 2), dtype=bool), np.ones((2, 2), dtype=bool))
    r = LI.interval(Combo(a_cells=CARRIED), None, nothing, indices=LI.enumerate_indices(2), batch_part="closed_form")
    assert r["defined"] is False


def test_zero_variance_gives_a_zero_width_interval_and_the_marker():
    pres = Presence.complete(4, 4, 3)
    idx = LI.make_indices(4, B=500)
    r = LI.interval(Combo(a_cells=np.full((4, 4, 3), 0.46)), Combo(h_cells=np.full((4, 3), 0.59)), pres, indices=idx)
    assert r["zero_variance"] and r["v_closed"] == 0.0 and r["se_star_sq"] == 0.0
    assert r["interval"][0] == r["interval"][1] == r["estimate"]
    assert r["interval_percentile"][0] == r["interval_percentile"][1] == r["estimate"]
    assert r["nu"] == 3 and r["denom_z"] is None


def test_bootstrap_agrees_with_the_closed_form_and_follows_its_definition():
    K = 16
    rng = np.random.default_rng(7)
    table = rng.standard_normal((K, K)) + rng.standard_normal(K)[:, None] + rng.standard_normal(K)[None, :]
    idx = LI.make_indices(K)
    assert idx.B == 10_000 and idx.idx_attack.shape == (10_000, K)
    dev = LI.replicate_deviations(table, idx)
    for b in (0, 17, 9_999):  # the mean of the K^2 entries at the drawn attack and held-out indices
        direct = table[np.ix_(idx.idx_attack[b], idx.idx_heldout[b])].mean()
        assert dev[b] == pytest.approx(direct, abs=1e-12)
    out = LI.check_closed_form(float(dev.var(ddof=1)), LI.closed_form_variance(table), dev)
    assert abs(out["ratio"] - 1.0) < 0.05
    again = LI.make_indices(K)
    assert again.sha256 == idx.sha256 and again.seed == (LI.MASTER_SEED, LI.BOOTSTRAP_STREAM, K, 10_000)
    assert LI.make_indices(8).sha256 != idx.sha256


def test_closed_form_band_is_plan_12_3():
    rng = np.random.default_rng(8)
    normal = rng.standard_normal(10_000)
    band, kurtosis = LI.closed_form_band(normal)
    assert kurtosis == pytest.approx(3.0, abs=0.2)
    assert band == pytest.approx(0.0707, abs=0.004)  # 5 sqrt(2 / 10,000)
    two_point = np.array([1.0, -1.0] * 5_000)  # kurtosis 1: the floor of 0.07 applies
    assert LI.closed_form_band(two_point) == (0.07, pytest.approx(1.0))
    heavy = np.concatenate([np.zeros(9_990), np.full(10, 50.0)])  # one cell dominating: a wide band, not a false refusal
    assert LI.closed_form_band(heavy)[0] > 0.3


def test_closed_form_check_raises_on_a_miss_with_no_number_in_the_message():
    rng = np.random.default_rng(9)
    dev = rng.standard_normal(10_000)
    v = float(dev.var(ddof=1))
    LI.check_closed_form(v, v * 1.05, dev)
    for wrong in (v * 1.10, v * 0.90, v * 2.0):
        with pytest.raises(LI.ClosedFormCheckError) as e:
            LI.check_closed_form(v, wrong, dev)
        assert str(e.value) == "closed_form_check" and not any(c.isdigit() for c in str(e.value))
    # a closed form of exactly zero requires a bootstrap variance of exactly zero
    assert LI.check_closed_form(0.0, 0.0, np.zeros(100)) == {"ratio": None, "band": None, "kurtosis": None}
    with pytest.raises(LI.ClosedFormCheckError):
        LI.check_closed_form(1e-30, 0.0, dev)


def test_multiplier_widens_the_deciding_interval_only():
    r1 = LI.interval_from_parts(0.5, 0.0012, {"S": 0.0098, "AS": 0.0002, "BS": 0.0002, "ABS": 0.0002}, K=2, K_A=2, K_H=2, n_s=2)
    r2 = LI.interval_from_parts(0.5, 0.0012, {"S": 0.0098, "AS": 0.0002, "BS": 0.0002, "ABS": 0.0002}, K=2, K_A=2, K_H=2, n_s=2, multiplier=1.15)
    assert r2["interval_unwidened"] == r1["interval"]
    assert r2["half_width"] == pytest.approx(1.15 * r1["half_width"], rel=1e-12)
    assert r2["standard_error"] == r1["standard_error"]  # z_D uses the unwidened standard error


def test_t_quantile_at_real_degrees_of_freedom():
    for nu in (1.0, 2.0, 6.2, 12.9, 15.0):
        assert LI.t_quantile(nu) == pytest.approx(float(student_t.ppf(0.975, nu)), rel=1e-12)


def test_denominator_distance_is_the_denominator_over_its_unwidened_standard_error():
    arrays = _random_arrays(6, 4, seed=11)
    pres = LR.presence_of(arrays)
    idx = LI.make_indices(6, B=2000)
    stats = LR.nine_statistics(arrays)
    ratio = LI.interval(*stats["depends"], pres, indices=idx, multiplier=1.3)
    own_margin = LI.interval(*stats["own_margin"], pres, indices=idx)
    assert ratio["denom_z"] == pytest.approx(own_margin["estimate"] / own_margin["standard_error"], rel=1e-12)
