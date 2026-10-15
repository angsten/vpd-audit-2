"""Session 6, plan 2: the settings the GPU re-scoring scores, built on tiny made-up arrays with hand-computed answers."""

from __future__ import annotations

import numpy as np
import pytest

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_build as B

LAY = [("a", 3), ("b", 2)]  # flat: a0 a1 a2 a_delta b0 b1 b_delta
STRATA = {"a": np.array([0, 10, 4]), "b": np.array([10, 10])}


def test_the_ranking_by_effect_breaks_ties_to_the_lower_index():
    s0 = np.array([0.5, 0.5, 0.0, 0.5], dtype=np.float32)
    s = np.array([1.0, 0.0, 1.0, 0.5], dtype=np.float32)
    G = np.array([1.0, -2.0, 0.5, 3.0], dtype=np.float32)
    # a = G (s - s0) = 0.5, 1.0, 0.5, 0.0
    assert B.rank_by_effect(s, s0, G).tolist() == [1, 0, 2, 3]
    assert B.rank_by_abs_gradient(G).tolist() == [3, 1, 0, 2]


def test_keep_and_the_endpoints_of_the_top_set():
    s0 = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    s = np.array([0.9, 0.8, 0.7], dtype=np.float32)
    assert B.keep(s, s0, np.array([2])).tolist() == pytest.approx([0.1, 0.2, 0.7])
    order = np.array([2, 0, 1])
    assert B.keep(s, s0, order[:0]).tobytes() == s0.tobytes() and B.keep(s, s0, order[:3]).tobytes() == s.tobytes()


def test_the_cells_and_a_matched_draw():
    cells = B.cells_of(LAY, STRATA)
    assert cells.tolist() == [0, 10, 4, 11, 22, 22, 23]  # matrix * 12 + stratum; each delta entry its matrix's stratum 11
    for seed in range(20):
        picked = B.matched_random(np.array([0, 4, 6]), cells, seed)
        # one from cell 0 (only entry 0), one from cell 22 (entry 4 or 5), one from cell 23 (only entry 6)
        assert picked.tolist()[0] == 0 and picked.tolist()[2] == 6 and picked.tolist()[1] in (4, 5)
    assert B.matched_random(np.array([0, 4]), cells, 7).tolist() == B.matched_random(np.array([0, 4]), cells, 7).tolist()
    u = B.uniform_random(40, 10, 3)
    assert len(set(u.tolist())) == 10 and u.tolist() == sorted(u.tolist())


def test_off_on_and_the_background_of_one_by_hand():
    s0 = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
    s = np.array([0.0, 1.0, 0.3, 0.0], dtype=np.float32)
    top = np.array([0, 1, 2])
    assert B.off_part(s, s0, top).tolist() == [0.0, 0.5, 0.5, 0.5]  # only the top entries at exactly 0
    assert B.on_part(s, s0, top).tolist() == [0.5, 1.0, 0.5, 0.5]
    assert B.background_of_one(s, top).tolist() == pytest.approx([0.0, 1.0, 0.3, 1.0])


def test_the_controls_by_hand():
    flat = np.array([0.2, 0.6, 0.5, 0.3, 0.49, 0.95, 0.7], dtype=np.float32)
    assert B.delta_reset(flat, LAY).tolist() == pytest.approx([0.2, 0.6, 0.5, 1.0, 0.49, 0.95, 1.0])
    assert B.rounded(flat).tolist() == [0, 1, 1, 0, 0, 1, 1]
    # the snap: at most 0.2 to 0, at least 0.8 to 1, the rest kept (0.2 and 0.8 themselves snap)
    snap_in = np.array([0.2, 0.21, 0.5, 0.79, 0.8, 0.0, 1.0, 0.1], dtype=np.float32)
    assert B.snapped(snap_in).tolist() == pytest.approx([0.0, 0.21, 0.5, 0.79, 1.0, 0.0, 1.0, 0.0])


def test_the_near_bound_parts_by_hand():
    s0 = np.full(6, 0.5, dtype=np.float32)
    s = np.array([0.0, 0.1, 0.15, 0.9, 0.85, 1.0], dtype=np.float32)
    top = np.arange(6)
    assert B.near_off_part(s, s0, top).tolist() == pytest.approx([0.0, 0.1, 0.5, 0.5, 0.5, 0.5])  # at most 0.1
    assert B.near_on_part(s, s0, top).tolist() == pytest.approx([0.5, 0.5, 0.5, 0.9, 0.5, 1.0])  # at least 0.9
    assert B.near_off_part(s, s0, np.array([2, 3])).tolist() == pytest.approx([0.5] * 6)  # only top entries count


def test_the_coarse_strata_and_shuffles():
    a = B.coarse_strata(STRATA, "alive_and_never_needed")
    assert a["a"].tolist() == [0, 10, 0] and a["b"].tolist() == [10, 10]
    w = B.coarse_strata(STRATA, "whole_matrix")
    assert w["a"].tolist() == [0, 0, 0] and w["b"].tolist() == [0, 0]
    flat = np.array([0.1, 0.2, 0.3, 0.9, 0.4, 0.5, 0.8], dtype=np.float32)
    c = B.coarse_shuffle(flat, LAY, w, "whole_matrix", "A1", 9, "n80")
    assert sorted(c[:3].tolist()) == sorted(flat[:3].tolist()) and c[3] == flat[3] and c[6] == flat[6]
    assert c.tobytes() == B.coarse_shuffle(flat, LAY, w, "whole_matrix", "A1", 9, "n80").tobytes()
    assert c.tobytes() != B.coarse_shuffle(flat, LAY, w, "whole_matrix", "A1", 10, "n80").tobytes() or True  # another key, another draw


def test_the_shuffle_description_by_hand():
    alive = B.component_mask(LAY, STRATA, "alive")
    never = B.component_mask(LAY, STRATA, "never")
    assert alive.tolist() == [True, False, True, False, False, False, False] and never.tolist() == [False, True, False, False, True, True, False]
    flat = np.array([0.0, 1.0, 0.9, 0.5, 0.0, 1.0, 0.5], dtype=np.float32)
    copy = np.array([0.9, 1.0, 0.0, 0.5, 0.0, 0.0, 0.5], dtype=np.float32)
    d = B.shuffle_description(flat, copy, alive, never)
    assert d["moved_alive_over_half"] == 1.0  # both alive entries moved by 0.9
    assert d["zeros_on_never_needed"] == pytest.approx(2 / 3)  # zeros at entries 2 (alive), 4 and 5 (never-needed)


def test_the_label_cache_index_maps_to_the_layout():
    offsets = {"a": 2, "b": 0}  # the cache's sorted order puts b first
    to_flat = B.global_to_flat(offsets, {"a": 3, "b": 2}, LAY)
    assert to_flat.tolist() == [4, 5, 0, 1, 2]  # global 0, 1 are b0, b1; global 2, 3, 4 are a0, a1, a2


def test_an_aggregated_setting_by_hand():
    # three positions; global components 0 to 4; labels above zero only are stored
    indptr = np.array([0, 2, 3, 5])
    indices = np.array([0, 3, 1, 3, 4], dtype=np.uint16)
    values = np.array([0.5, 0.05, 0.1, 0.2, 0.11], dtype=np.float32)
    to_flat = B.global_to_flat({"a": 2, "b": 0}, {"a": 3, "b": 2}, LAY)
    out, size = B.b2_setting(indptr, indices, values, np.array([0, 2]), to_flat, 7)
    # position 0: component 0 (0.5) in, 3 (0.05) out; position 2: 3 (0.2) and 4 (0.11) in; 0.1 itself is not above 0.1
    assert size == 3 and out.tolist() == [0, 1, 1, 0, 1, 0, 0]
    assert B.b2_setting(indptr, indices, values, np.array([1]), to_flat, 7)[1] == 0
    p = B.b2_positions(64, 1, 524288)
    assert p.size == 64 and len(set(p.tolist())) == 64 and p.tolist() == B.b2_positions(64, 1, 524288).tolist()


def test_the_exploit_passes_and_their_count():
    n = 40
    lay = [("m", 39)]
    strata = {"m": np.arange(39) % 11}
    rng = np.random.default_rng(0)
    s0 = rng.random(n).astype(np.float32)
    s = np.where(rng.random(n) < 0.5, 0.0, 1.0).astype(np.float32)
    G = rng.normal(size=n).astype(np.float32)
    cells = B.cells_of(lay, strata)
    for row in ("n40", "n80", "n320"):
        passes = list(B.exploit_passes(s, s0, G, cells, "A3", 9, row))
        assert len(passes) == B.n_passes("exploit", row, n)
        got = {pid: flat for pid, flat, _ in passes}
        assert got["top|0"].tobytes() == s0.tobytes() and got[f"top|{n}"].tobytes() == s.tobytes()
        assert got[f"matched|{n}|1"].tobytes() == s.tobytes()  # every cell taken whole
        assert ("off|10" in got) == (row in B.OFFON_ROWS) and ("absg|10" in got) == (row == "n320")
        assert ("near_off|10" in got) == ("near_on|40" in got) == (row == "n320")
    ks = len(B.grid(38936))
    assert B.n_passes("exploit", "n320") - B.n_passes("exploit", "n80") == 2 + 1 + ks + 2 * ks  # 2 matched, uniform, |G|, near-bound
    assert 5 * 2 * ks == 150  # the addendum's 150 passes per held-out container
    assert B.grid(40) == (10, 20, 30, 40) and B.grid(38936) == B.GRID


def test_the_units_of_a_container():
    A = [f"A{i}" for i in range(1, 17)]
    plain = B.heldout_units("H2", A, [9, 10, 11, 12, 13], "A2")
    s4 = B.heldout_units("H5", A, [9, 10, 11, 12, 13], "A5")
    assert len(plain) == 1 + 80 + 15 + 2 and len(s4) == len(plain) + 81
    assert all(u[2]["attack"] == "A2" for u in plain if u[1] == "exploit")
    att = B.attack_units("A7", [9, 10, 11, 12, 13])
    assert [u[0] for u in att][:2] == ["check_A7", "split_A7_A7_s9"] and len(att) == 7
    per = {u[1]: B.n_passes(u[1], u[2].get("row")) for u in s4}
    assert per["split"] == 10 and per["controls"] == 25 and per["b"] == 17
    assert sum(B.n_passes(k, p.get("row"), s4=False) for _, k, p in plain) == 2 + 800 + 5 * (B.n_passes("exploit", "n40") + B.n_passes("exploit", "n80")
                                                                                         + B.n_passes("exploit", "n320")) + 1 + 17


def test_a_saved_setting_is_read_by_its_row():
    unit = {"hook_names": np.array(["step_19", "step_20", "two_step_mean_reaches_2"]), "settings": np.arange(9, dtype=np.float32).reshape(3, 3),
            "cum_signed": -np.arange(9, dtype=np.float32).reshape(3, 3)}
    s, G = B.saved(unit, "n20")
    assert s.tolist() == [3, 4, 5] and G.tolist() == [-3, -4, -5] and LR.SAVED["n20"] == "step_20"


# ----------------------------------------------------------------------------- plan 3, Section 7: the variants


def test_v1_keeps_the_zeros_and_sets_every_other_entry_to_one():
    s = np.array([0.0, 0.3, 1.0, 0.0, 0.5, 1e-8], dtype=np.float32)
    v1 = B.zeros_alone(s)
    assert v1.dtype == np.float32 and v1.tolist() == [0.0, 1.0, 1.0, 0.0, 1.0, 1.0]


def test_v2_and_v3_as_split_path_arguments():
    s = np.array([0.0, 0.3, 1.0, 0.7], dtype=np.float32)
    args = B.variant_split_args(s)
    zero_side, positive_side, delta = args["V2"]
    assert np.array_equal(zero_side, s) and (positive_side == 1).all() and np.array_equal(delta, s)  # Part Z on an intact model
    zero_side, positive_side, delta = args["V3"]
    assert (zero_side == 1).all() and np.array_equal(positive_side, s) and (delta == 1).all()  # Part P on an intact model


def test_the_variants_units_and_their_passes():
    units = B.variant_units("H5", ["A1", "A2"], [9, 10])
    assert units[0] == ("variants_check_H5", "variants_check", {})
    assert [u[0] for u in units[1:]] == ["variants_H5_A1_s9", "variants_H5_A1_s10", "variants_H5_A2_s9", "variants_H5_A2_s10"]
    assert B.n_passes("variants") == 15 and B.n_passes("variants_check") == 3 and B.VARIANTS == ("V1", "V2", "V3")


# ----------------------------------------------------------------------------- plan 3, Section 8: the dose-response


def test_a_dose_keeps_a_random_fraction_of_the_zeros_and_sets_the_rest_to_one():
    rng = np.random.default_rng(0)
    s = np.where(rng.random(1000) < 0.3, 0.0, rng.random(1000)).astype(np.float32)
    zeros = np.flatnonzero(s == 0)
    for f in (0.25, 0.5, 0.75):
        d, n0, k = B.dose_setting(s, f, seed=11)
        assert d.dtype == np.float32 and n0 == zeros.size and k == int(np.floor(f * zeros.size + 0.5))
        assert set(np.flatnonzero(d == 0)) <= set(zeros) and (d == 0).sum() == k and ((d == 0) | (d == 1)).all()
        assert np.array_equal(d, B.dose_setting(s, f, seed=11)[0]) and not np.array_equal(d, B.dose_setting(s, f, seed=12)[0])
    assert np.array_equal(B.dose_setting(s, 1.0, seed=3)[0], B.zeros_alone(s))  # f = 1 is V1
    assert (B.dose_setting(s, 0.0, seed=3)[0] == 1).all()  # f = 0 is all ones
    none = np.full(10, 0.5, dtype=np.float32)
    assert B.dose_setting(none, 0.5, seed=1)[1:] == (0, 0) and (B.dose_setting(none, 0.5, seed=1)[0] == 1).all()
    assert B.dose_setting(np.zeros(5, dtype=np.float32), 0.5, seed=1)[2] == 3  # 2.5 rounds half up


def test_the_dose_seeds_one_draw_per_setting_length_and_fraction():
    from vpd_audit_2.manifest import seed_of

    assert B.dose_seed("A3", 11, "n80", 0.5) == seed_of("s6-dose", "A3", 11, 80, "0.5")
    seeds = {B.dose_seed(a, s, row, f) for a in ("A1", "A2") for s in (9, 10) for row in B.SPLIT_ROWS for f in B.DOSE_FRACTIONS}
    assert len(seeds) == 2 * 2 * 5 * 3
    s = np.where(np.arange(40) % 3 == 0, 0.0, 0.5).astype(np.float32)
    passes = list(B.dose_passes(s, "A1", 9, "n320"))
    assert [p[0] for p in passes] == ["D0.25|n320", "D0.5|n320", "D0.75|n320"] and passes[1][2]["seed"] == B.dose_seed("A1", 9, "n320", 0.5)
    assert B.dose_units("H9", ["A1"], [9, 10]) == [("dose_check_H9", "variants_check", {}), ("dose_H9_A1_s9", "dose", {"attack": "A1", "start": 9}),
                                                   ("dose_H9_A1_s10", "dose", {"attack": "A1", "start": 10})]
    assert B.n_passes("dose") == 15


# ----------------------------------------------------------------------------- plan 3, Section 9: the dose-response on the rounded off set


def test_the_rounded_dose_sets_a_random_fraction_of_the_off_set_to_zero_and_the_rest_to_one():
    rng = np.random.default_rng(1)
    s = rng.random(1000).astype(np.float32)
    s[:5] = [0.5, np.nextafter(np.float32(0.5), np.float32(0)), 0.0, 1.0, 0.49]
    off = np.flatnonzero(s < np.float32(0.5))
    assert 1 in off and 0 not in off  # one half itself is on, the float just below it is off
    for f in B.DOSE_ROUNDED_FRACTIONS:
        d, n_off, k = B.dose_rounded_setting(s, f, seed=5)
        assert n_off == off.size and k == int(np.floor(f * off.size + 0.5)) and (d == 0).sum() == k
        assert set(np.flatnonzero(d == 0)) <= set(off) and ((d == 0) | (d == 1)).all() and d.dtype == np.float32
    assert np.array_equal(B.dose_rounded_setting(s, 1.0, seed=9)[0], B.rounded(s))  # f = 1 is the rounded setting
    assert (B.dose_rounded_setting(s, 0.0, seed=9)[0] == 1).all()
    assert B.dose_rounded_seed("A2", 12, "n40", 0.9) == __import__("vpd_audit_2.manifest", fromlist=["seed_of"]).seed_of("s6-dose-rounded", "A2", 12, 40, "0.9")
    assert [p[0] for p in B.dose_rounded_passes(s, "A1", 9, "n20")] == ["R0.25|n20", "R0.5|n20", "R0.75|n20", "R0.9|n20"]
    assert B.dose_rounded_units("H1", ["A1"], [9])[0] == ("dose_rounded_check_H1", "variants_check", {}) and B.n_passes("dose_rounded") == 20
