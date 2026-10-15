"""Session 6, plan 3, Section 2: agreement between settings on tiny made-up settings with hand-computed answers,
including the worked examples of Riku's note (`sessions/006/notes/riku/conventions.md`, Section 4.3)."""

from __future__ import annotations

import hashlib
import itertools
import json

import numpy as np
import pytest

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_agreement as G

# ----------------------------------------------------------------------------- the worked examples


def test_riku_first_example_independence_against_the_same_start_level():
    # 20 entries in one stratum; the start has 10 below one half and 10 above. Each setting crosses one half from the
    # start on 4 entries (q = 0.2), two from below and two from above, so each keeps 10 below (p = 0.5). They cross
    # together on one entry, so they disagree on 6 and agree on 14: A = 0.70.
    s0 = np.array([0.3] * 10 + [0.7] * 10, dtype=np.float32)
    a, b = s0.copy(), s0.copy()
    a[[0, 1]], a[[10, 11]] = 0.6, 0.4
    b[[1, 2]], b[[12, 13]] = 0.6, 0.4
    Ba, Bb = G.below(a), G.below(b)
    Ca, Cb = G.crossed(a, s0), G.crossed(b, s0)
    codes = np.zeros(20, dtype=np.int64)
    assert Ca.mean() == Cb.mean() == 0.2 and Ba.mean() == Bb.mean() == 0.5
    A = G.agreement(Ba[None], Bb[None])[0, 0]
    assert A == pytest.approx(0.70)
    p, n = G.shares(np.stack([Ba, Bb]), codes)
    q, _ = G.shares(np.stack([Ca, Cb]), codes)
    w = n / n.sum()
    independence, crossing = G.chance(p[:1], p[1:], w)[0, 0], G.chance(q[:1], q[1:], w)[0, 0]
    assert independence == pytest.approx(0.50) and crossing == pytest.approx(0.68)
    assert G.kappa(A, independence) == pytest.approx(0.40)
    assert G.kappa(A, crossing) == pytest.approx(0.02 / 0.32) and f"{G.kappa(A, crossing):.2f}" == "0.06"
    r = G.pair(Ba, Bb, Ca, Cb, codes)  # the direct count agrees
    assert (r["agreement"], r["independence"], r["crossing"]) == pytest.approx((0.70, 0.50, 0.68))


def test_riku_two_stratum_example():
    # Alive: 3 of 4 below in each, agreeing on all 4. Never-needed: 2 of 4 below in each, agreeing on 2 of 4.
    codes = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    Ba = np.array([1, 1, 1, 0, 1, 1, 0, 0], dtype=bool)
    Bb = np.array([1, 1, 1, 0, 1, 0, 1, 0], dtype=bool)
    A = G.agreement(Ba[None], Bb[None])[0, 0]
    p, n = G.shares(np.stack([Ba, Bb]), codes)
    C = G.chance(p[:1], p[1:], n / n.sum())[0, 0]
    assert A == 0.75 and C == pytest.approx(0.5 * 0.625 + 0.5 * 0.50) and C == pytest.approx(0.5625)
    assert G.kappa(A, C) == pytest.approx(0.1875 / 0.4375) and f"{G.kappa(A, C):.2f}" == "0.43"
    assert G.pair(Ba, Bb, Ba, Bb, codes)["independence"] == pytest.approx(0.5625)


def test_the_expected_overlap_formula_and_the_notes_scale():
    assert G.expected_overlap(np.array([2, 1]), np.array([5, 3]), np.array([10, 30])) == pytest.approx(2 * 5 / 10 + 1 * 3 / 30)
    assert G.expected_overlap(np.array([3000]), np.array([3000]), np.array([10000])) == pytest.approx(900.0)
    assert G.expected_overlap(np.array([3000]), np.array([3000]), np.array([38912])) == pytest.approx(231.3, abs=0.05)
    assert G.expected_overlap(np.array([2, 0]), np.array([1, 0]), np.array([4, 0])) == 0.5  # an empty cell adds nothing
    with pytest.raises(ValueError):
        G.expected_overlap(np.array([2, 1]), np.array([1, 1]), np.array([4, 0]))


def test_kappa_is_undefined_when_chance_is_one():
    assert np.isnan(G.kappa(1.0, 1.0)) and G.kappa(0.5, 0.5) == 0.0 and G.kappa(1.0, 0.3) == pytest.approx(1.0)


# ----------------------------------------------------------------------------- deciles, groups, crossing


def test_deciles_are_ten_equal_count_bins_by_rank_ties_to_the_lower_index():
    v = np.arange(40, dtype=np.float32)[::-1].copy()
    d = G.deciles(v)
    assert np.bincount(d).tolist() == [4] * 10 and d[0] == 9 and d[-1] == 0
    ties = np.zeros(20, dtype=np.float32)  # all tied: the lower index ranks first
    assert G.deciles(ties).tolist() == [k // 2 for k in range(20)]
    # bin k holds ranks ceil(3891.2 k) to ceil(3891.2 (k + 1)) - 1
    assert np.bincount(G.deciles(np.random.default_rng(0).random(38912))).tolist() == [3892, 3891, 3891, 3891, 3891, 3892, 3891, 3891, 3891, 3891]


def test_below_and_crossing_use_one_half_exactly():
    s0 = np.array([0.5, 0.49, 0.2, 0.9], dtype=np.float32)
    s = np.array([0.49, 0.5, 0.3, 0.5], dtype=np.float32)
    assert G.below(s).tolist() == [True, False, True, False]
    assert G.crossed(s, s0).tolist() == [True, True, False, False]


LAY = [("m0", 6), ("m1", 4)]
STRATA = {"m0": np.array([0, 0, 1, 10, 10, 1]), "m1": np.array([10, 2, 2, 10])}


def test_the_groups_and_strata_of_a_small_layout():
    ent = G.entries(LAY, STRATA)
    assert ent.cols["delta"].tolist() == [6, 11]
    assert ent.cols["rank_one"].tolist() == [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]
    assert ent.cols["alive"].tolist() == [0, 1, 2, 5, 8, 9] and ent.cols["never_needed"].tolist() == [3, 4, 7, 10]
    # rank-one strata: (m0, 0), (m0, 1), (m0, 10), (m1, 2), (m1, 10): five groups
    assert ent.codes["rank_one"].tolist() == [0, 0, 1, 2, 2, 1, 4, 3, 3, 4]
    assert ent.codes["alive"].tolist() == [0, 0, 1, 1, 2, 2] and ent.codes["never_needed"].tolist() == [0, 0, 1, 1]
    assert ent.codes["delta"].tolist() == [0, 0]
    # plan 2's cells: matrix * 12 + stratum, each delta its matrix's stratum 11
    assert ent.cells.tolist() == [0, 0, 1, 10, 10, 1, 11, 22, 14, 14, 22, 23]


def test_decile_cells_cross_the_start_deciles_with_alive_or_never_needed():
    ent = G.entries(LAY, STRATA)
    s0 = np.zeros(12, dtype=np.float32)
    s0[ent.cols["rank_one"]] = np.arange(10, dtype=np.float32) / 10  # ten entries: one per decile, in order
    d = G.decile_codes(s0, ent)
    never = [False, False, False, True, True, False, True, False, False, True]
    raw = [k * 2 + int(nv) for k, nv in enumerate(never)]
    assert d["rank_one"].tolist() == np.unique(raw, return_inverse=True)[1].tolist()
    assert d["alive"].tolist() == [0, 1, 2, 3, 4, 5]  # deciles 0, 1, 2, 5, 7, 8, renumbered
    assert d["never_needed"].tolist() == [0, 1, 2, 3]  # deciles 3, 4, 6, 9


# ----------------------------------------------------------------------------- the matrix path against direct counts


BIG_LAY = [("m0", 30), ("m1", 25), ("m2", 20)]


def _big_strata(rng):
    return {k: rng.integers(0, 11, size=C) for k, C in BIG_LAY}


def _search(rng, source, batch, start, s0, rows=("n320",), grads=True, untouched=None):
    x = G.Search(source, batch, start)
    for row in rows:
        s = np.clip(s0 + rng.normal(0, 0.3, s0.size), 0, 1).astype(np.float32)
        u = np.zeros(s0.size, dtype=bool) if untouched is None else untouched
        s[u] = s0[u]
        G._add_row(x, row, s, s0, u, rng.normal(size=s0.size).astype(np.float32) if grads else None)
    return x


def _setup(seed=0, top_k=7):
    rng = np.random.default_rng(seed)
    strata = _big_strata(rng)
    ent = G.entries(BIG_LAY, strata)
    n = sum(C + 1 for _, C in BIG_LAY)
    starts = {s: rng.random(n).astype(np.float32) for s in (1, 9, 10)}
    dec = {s: G.decile_codes(s0, ent) for s, s0 in starts.items()}
    return rng, ent, starts, dec


def test_the_matrix_path_equals_direct_counting_for_every_pair(monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 7)
    rng, ent, starts, dec = _setup()
    searches = [_search(rng, "run", b, s, starts[s]) for b in ("A1", "A2", "H1") for s in (9, 10)]
    searches += [_search(rng, "pilot", b, 1, starts[1], grads=False) for b in ("C1", "C2")]
    rp = G.row_pairs(searches, "n320", ent, dec)
    assert len(rp.i) == 28
    for m, (a, b) in enumerate(zip(rp.i, rp.j)):
        xa, xb = rp.searches[a], rp.searches[b]
        for g in G.GROUPS:
            cols = ent.cols[g]
            r = G.pair(xa.below["n320"][cols], xb.below["n320"][cols], xa.crossed["n320"][cols], xb.crossed["n320"][cols], ent.codes[g],
                       decile=dec[xa.start][g] if g != "delta" else None)
            v = rp.values[g]
            assert v["agreement"][m] == pytest.approx(r["agreement"], abs=1e-12)
            assert v["independence"][m] == pytest.approx(r["independence"], abs=1e-12)
            if xa.start == xb.start:
                assert v["crossing"][m] == pytest.approx(r["crossing"], abs=1e-12)
                if g != "delta":
                    assert v["decile"][m] == pytest.approx(r["decile"], abs=1e-12)
            else:
                assert np.isnan(v["crossing"][m]) and np.isnan(v["decile"][m])
            if g == "delta":
                assert np.isnan(v["decile"][m])
        # the overlap, counted directly
        if xa.top and xb.top:
            ta, tb = set(xa.top["n320"].tolist()), set(xb.top["n320"].tolist())
            both = sorted(ta & tb)
            ka = np.bincount(ent.cells[list(ta)], minlength=ent.n_cells)
            kb = np.bincount(ent.cells[list(tb)], minlength=ent.n_cells)
            nc = np.bincount(ent.cells, minlength=ent.n_cells)
            assert rp.overlap["valid"][m]
            assert rp.overlap["observed"][m] == len(both)
            assert rp.overlap["expected"][m] == pytest.approx(G.expected_overlap(ka, kb, nc))
            assert rp.overlap["same_side"][m] == sum(xa.below["n320"][c] == xb.below["n320"][c] for c in both)
        else:
            assert not rp.overlap["valid"][m]


def test_the_top_set_is_plan_2s_ranking(monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 3)
    s0 = np.array([0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32)
    s = np.array([0.0, 1.0, 0.4, 0.5, 0.9], dtype=np.float32)
    Gr = np.array([-1.0, 0.5, -2.0, 9.0, 1.0], dtype=np.float32)  # a_c = 0.5, 0.25, 0.2, 0, 0.4
    x = G.Search("run", "A1", 9)
    G._add_row(x, "n320", s, s0, np.zeros(5, dtype=bool), Gr)
    assert x.top["n320"].tolist() == [0, 1, 4]


def test_family_summaries_and_kappa_from_the_family_means(monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 7)
    rng, ent, starts, dec = _setup(seed=3)
    searches = [_search(rng, "run", b, s, starts[s]) for b in ("A1", "A2", "H1", "H2") for s in (9, 10)]
    rp = G.row_pairs(searches, "n320", ent, dec)
    out = G.row_summary(rp)
    ss = rp.family["same_start"]
    a = rp.values["rank_one"]["agreement"][ss].mean()
    c = rp.values["rank_one"]["crossing"][ss].mean()
    d = out["families"]["same_start"]["rank_one"]
    assert out["families"]["same_start"]["pairs"] == 12 and out["families"]["same_batch"]["pairs"] == 4
    assert out["families"]["different"]["pairs"] == 12
    assert d["agreement"] == pytest.approx(a) and d["kappa_crossing"] == pytest.approx((a - c) / (1 - c))
    assert out["families"]["same_start"]["delta"]["chance_decile"] is None
    assert "chance_crossing" not in out["families"]["different"]["rank_one"]
    o = out["families"]["different"]["overlap"]
    m = rp.family["different"]
    O, E = rp.overlap["observed"][m].mean(), rp.overlap["expected"][m].mean()
    assert o["beyond_chance"] == pytest.approx((O - E) / (7 - E))
    assert o["same_side"] == pytest.approx(rp.overlap["same_side"][m].sum() / rp.overlap["observed"][m].sum())


# ----------------------------------------------------------------------------- the untouched-in-both print


def test_with_nothing_untouched_the_second_print_equals_the_first(monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 7)
    rng, ent, starts, dec = _setup(seed=1)
    searches = [_search(rng, "run", b, 9, starts[9]) for b in ("A1", "A2", "A3")]
    out = G.row_summary(G.row_pairs(searches, "n320", ent, dec))
    u = out["same_start_untouched_left_out"]
    assert sum(u["entries_left_out"].values()) == 0 and u["equals_first"]


def test_entries_untouched_in_both_are_left_out_and_the_levels_recounted(monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 7)
    rng, ent, starts, dec = _setup(seed=2)
    n = starts[9].size
    u1 = np.zeros(n, dtype=bool)
    u1[[0, 1, 2, 3, 40, 41]] = True
    u2 = np.zeros(n, dtype=bool)
    u2[[2, 3, 4, 41, 50]] = True
    searches = [_search(rng, "run", "A1", 9, starts[9], untouched=u1), _search(rng, "run", "A2", 9, starts[9], untouched=u2)]
    rp = G.row_pairs(searches, "n320", ent, dec)
    u = rp.untouched
    both = u1 & u2  # entries 2, 3, 41: all rank-one; 2 and 3 in m0, 41 in m1
    for g in G.GROUPS:
        cols = ent.cols[g]
        assert u["entries_left_out"][g] == int(both[cols].sum())
        keep = ~both[cols]
        r = G.pair(searches[0].below["n320"][cols], searches[1].below["n320"][cols], searches[0].crossed["n320"][cols],
                   searches[1].crossed["n320"][cols], ent.codes[g], keep, dec[9][g] if g != "delta" else None)
        assert u["values"][g]["agreement"][0] == pytest.approx(r["agreement"])
        assert u["values"][g]["crossing"][0] == pytest.approx(r["crossing"])
    assert u["entries_left_out"]["rank_one"] == 3 and u["entries_left_out"]["delta"] == 0
    # the untouched entries all agree: leaving them out lowers the agreement
    assert u["values"]["rank_one"]["agreement"][0] < rp.values["rank_one"]["agreement"][0]
    assert not G.row_summary(rp)["same_start_untouched_left_out"]["equals_first"]


def test_same_treats_undefined_values_as_equal():
    assert G.same({"a": float("nan"), "b": {"c": 1.0}}, {"a": float("nan"), "b": {"c": 1.0}})
    assert not G.same({"a": 1.0}, {"a": 1.0 + 1e-12})


# ----------------------------------------------------------------------------- the design's families and breakdowns


def _design():
    return ([(b, s) for b in G.DECIDING for s in G.RUN_STARTS] + [(b, s) for b in G.CALIBRATION for s in G.RUN_STARTS]
            + [(b, s) for b in G.CALIBRATION for s in G.PILOT_STARTS])


def test_the_real_designs_family_counts():
    d = _design()
    start = np.array([s for _, s in d])
    batch = np.array([b for b, _ in d])
    i, j = np.triu_indices(len(d), 1)
    fam = G.families(start, batch, i, j)
    assert len(d) == 264 and len(i) == 34716
    assert fam["same_start"].sum() == 5 * 780 + 8 * 28 == 4124
    assert fam["same_batch"].sum() == 32 * 10 + 8 * 78 == 944
    assert fam["different"].sum() == 34716 - 4124 - 944


def test_one_batch_from_one_start_twice_is_refused():
    with pytest.raises(G.Refusal):
        G.families(np.array([9, 9]), np.array(["A1", "A1"]), np.array([0]), np.array([1]))


def test_the_breakdowns_pair_counts_on_the_real_design(monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 3)
    rng = np.random.default_rng(4)
    lay = [("m0", 8), ("m1", 6)]
    strata = {"m0": np.array([0, 1, 10, 10, 2, 2, 10, 0]), "m1": np.array([10, 3, 3, 10, 10, 1])}
    ent = G.entries(lay, strata)
    starts = {s: rng.random(16).astype(np.float32) for s in G.PILOT_STARTS + G.RUN_STARTS}
    dec = {s: G.decile_codes(s0, ent) for s, s0 in starts.items()}
    searches = [_search(rng, "pilot" if s < 9 else "run", b, s, starts[s], grads=s >= 9) for b, s in _design()]
    rp = G.row_pairs(searches, "n320", ent, dec)
    b = G.breakdowns(rp)
    assert b["same_start_by_start"]["9"]["pairs"] == 780 and b["same_start_by_start"]["1"]["pairs"] == 28
    assert b["same_start_by_start"]["9"]["overlap"]["pairs"] == 780 and b["same_start_by_start"]["1"]["overlap"]["pairs"] == 0
    split = b["same_start_by_batch_set"]
    assert split["within_deciding"]["pairs"] == 5 * 496 and split["within_calibration"]["pairs"] == 5 * 28
    assert split["across"]["pairs"] == 5 * 32 * 8 and split["within_calibration_pilot_starts"]["pairs"] == 8 * 28
    by_pair = b["same_batch_by_start_pair"]
    assert len(by_pair) == 78 and by_pair["9-10"]["pairs"] == 40 and by_pair["1-2"]["pairs"] == 8 and by_pair["1-9"]["pairs"] == 8
    assert by_pair["9-10"]["overlap"]["pairs"] == 40 and by_pair["1-9"]["overlap"]["pairs"] == 0
    text = G.report({row: G.row_summary(rp) for row in G.ROWS}, b,
                    {"counts": {"run": 160, "starts_test": 40, "pilot": 64}, "entries": {g: int(ent.cols[g].size) for g in G.GROUPS},
                     "strata_sha256": "x"})
    assert "these rows equal the first" in text and "starts 12-13" in text


# ----------------------------------------------------------------------------- reading the files, and refusing


def _unit(tmp_path, batch, start, s0, arm="lead", start_sha=None):
    settings = np.stack([np.clip(s0 + 0.1, 0, 1), np.clip(s0 - 0.1, 0, 1)]).astype(np.float32)
    meta = {"kind": "search", "batch": batch, "start": start, "arm": arm, "delta_held": False,
            "start_sha256": start_sha or LR.setting_sha256(s0)}
    path = tmp_path / f"search_{batch}_s{start}.npz"
    np.savez(path, hook_names=np.array(["step_20", "step_320"]), settings=settings, cum_signed=np.ones_like(settings),
             cum_abs=np.ones_like(settings), meta=np.array(json.dumps(meta)))
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_a_unit_is_read_only_against_its_recorded_hash_and_meta(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "TOP_K", 3)
    s0 = np.random.default_rng(5).random(10).astype(np.float32)
    path, sha = _unit(tmp_path, "A1", 9, s0)
    x = G.read_unit(path, sha, "A1", 9, "lead", s0, "run")
    assert sorted(x.below) == ["n20", "n320"] and x.top["n320"].size == 3
    with pytest.raises(G.Refusal, match="SHA-256"):
        G.read_unit(path, "0" * 64, "A1", 9, "lead", s0, "run")
    with pytest.raises(G.Refusal, match="is not the"):
        G.read_unit(path, sha, "A1", 10, "lead", s0, "run")
    with pytest.raises(G.Refusal, match="is not the"):
        G.read_unit(path, sha, "A1", 9, "starts_test", s0, "starts_test")
    with pytest.raises(G.Refusal, match="did not begin"):
        G.read_unit(path, sha, "A1", 9, "lead", s0 * 0.5, "run")


def test_a_pilot_file_is_checked_array_by_array_and_bounds_its_untouched_entries(tmp_path):
    s0 = np.array([0.2, 0.4, 0.6, 0.8], dtype=np.float32)
    arrays = {"step_19": np.array([0.2, 0.5, 0.6, 0.7], dtype=np.float32),  # entries 0 and 2 still at the start
              "step_20": np.array([0.2, 0.4, 0.7, 0.8], dtype=np.float32),  # entries 0, 1 and 3 at the start
              "two_step_mean_reaches_2": np.array([0.3, 0.4, 0.6, 0.8], dtype=np.float32)}  # at step 25
    arrays["final"] = arrays["step_20"]
    path = tmp_path / "C1_s1.npz"
    np.savez(path, **arrays)
    record = {"batch": "C1", "start_key": [20261001, "start", 1], "hook_events": {"step_19": 19, "step_20": 20, "two_step_mean_reaches_2": 25},
              "saved_sources_sha256": {k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest() for k, v in arrays.items() if k != "final"}}
    x = G.read_pilot(path, record, "C1", 1, s0)
    assert sorted(x.below) == ["h2", "n20"] and not x.top
    assert x.untouched["n20"].tolist() == [True, False, False, False]  # equal at 19 and at 20: entry 0 only
    assert x.untouched["h2"].tolist() == [False, False, False, False]
    bad = dict(record, saved_sources_sha256=dict(record["saved_sources_sha256"], step_20="0" * 64))
    with pytest.raises(G.Refusal, match="SHA-256"):
        G.read_pilot(path, bad, "C1", 1, s0)
    with pytest.raises(G.Refusal, match="another search"):
        G.read_pilot(path, record, "C1", 2, s0)


def test_the_pilots_starts_hash_is_read_from_its_sha256sum_lines():
    listing = "abc  starts_1_64.npz\ndef  starts_1_64.json\n"
    assert G.pilot_starts_sha256(listing) == "abc"
    assert G.pilot_starts_sha256("def  starts_1_64.json\n") is None
    assert G.pilot_starts_sha256("abc  starts_1_64.npz\nabd  starts_1_64.npz\n") is None
