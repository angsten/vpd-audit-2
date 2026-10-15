"""Session 6, plan 1, Section 2.2: the starts check. The hash recomputation on the committed starts, a changed entry
caught, the Kolmogorov-Smirnov distance against known answers and against scipy, and the flag rule."""

from __future__ import annotations

import json

import numpy as np
import pytest
from scipy import stats as sps

from vpd_audit_2 import starts_check as SC


@pytest.fixture(scope="module")
def committed():
    return SC.load()


def test_every_committed_start_hashes_to_its_recorded_sha256(committed):
    arrays, meta = committed
    h = SC.hash_check(arrays, meta)
    assert h == {"checked": 64, "matched": 64, "mismatched": []}
    with np.load(SC.MANIFEST_STARTS, allow_pickle=False) as z:
        manifest_arrays = {k: z[k] for k in z.files}
    assert SC.manifest_check(arrays, manifest_arrays, meta["layout"]) == {"checked": 16, "equal": 16, "differing": []}


def test_one_changed_entry_is_caught_by_both_checks(committed):
    arrays, meta = committed
    layout = meta["layout"]
    name = layout[5][0]
    changed = dict(arrays)
    x = arrays[f"s3|{name}"].copy()
    x.reshape(-1)[7] = np.nextafter(x.reshape(-1)[7], np.float32(2.0))  # one bit of one entry
    changed[f"s3|{name}"] = x
    assert SC.hash_check(changed, meta)["mismatched"] == [3]
    m = SC.manifest_check(changed, arrays, layout)
    assert m["differing"] == [f"s3|{name}"] and m["equal"] == 15


def test_every_committed_start_is_redrawn_from_its_seed_bit_for_bit(committed):
    arrays, meta = committed
    d = SC.redraw(arrays, meta)
    assert (d["checked"], d["identical"], d["differing"], d["seed_differs"]) == (64, 64, [], [])


def test_the_redraw_catches_one_changed_bit_and_a_wrong_seed(committed):
    arrays, meta = committed
    name = meta["layout"][-1][0]
    changed = dict(arrays)
    x = arrays[f"s12|{name}"].copy()
    x.reshape(-1)[-1] = np.nextafter(x.reshape(-1)[-1], np.float32(0.0))  # the last module's delta entry, one bit
    changed[f"s12|{name}"] = x
    wrong = json.loads(json.dumps(meta))
    wrong["starts"]["10"]["seed"] += 1
    d = SC.redraw(changed, wrong, n=13)
    assert d["differing"] == [12] and d["seed_differs"] == [10] and d["identical"] == 12


def test_the_delta_entries_are_the_last_entry_of_each_module():
    layout = [["a", 2], ["b", 1]]
    arrays = {"s1|a": np.array([[[0.1, 0.2, 0.9]]], dtype=np.float32), "s1|b": np.array([[[0.3, 0.05]]], dtype=np.float32)}
    d = SC.delta_entries(arrays, layout, 1)
    assert d.tolist() == [float(np.float32(0.9)), float(np.float32(0.05))]


def test_the_delta_entries_of_a_committed_start_are_where_the_search_holds_them(committed):
    from vpd_audit_2 import lead_run as LR

    arrays, meta = committed
    lay = [(k, int(c)) for k, c in meta["layout"]]
    flat = np.concatenate([p.reshape(-1) for p in SC.module_arrays(arrays, meta["layout"], 9)])
    assert np.array_equal(SC.delta_entries(arrays, meta["layout"], 9), flat[LR.delta_positions(lay)].astype(np.float64))
    assert SC.delta_entries(arrays, meta["layout"], 9).size == 24


def test_the_hash_is_the_one_pilot_recorded():
    """The recomputation is the recorder's own: the bytes of each module array, concatenated in the layout's order."""
    parts = [np.arange(3, dtype=np.float32).reshape(1, 1, 3), np.ones((1, 1, 2), dtype=np.float32)]
    import hashlib

    assert SC.start_sha256(parts) == hashlib.sha256(parts[0].tobytes() + parts[1].tobytes()).hexdigest()


def test_the_ks_distance_against_known_answers_and_scipy():
    assert SC.ks_uniform(np.array([0.5])) == 0.5
    assert SC.ks_uniform(np.array([0.6, 0.1])) == pytest.approx(0.4, abs=1e-15)  # order does not matter
    assert SC.ks_uniform(np.array([0.0, 0.25, 0.5, 0.75])) == pytest.approx(0.25, abs=1e-15)
    rng = np.random.default_rng(0)
    for x in (rng.random(1000), rng.random(1000) ** 1.3, rng.random(38936).astype(np.float32)):
        assert SC.ks_uniform(x) == pytest.approx(sps.kstest(x.astype(np.float64), "uniform").statistic, abs=1e-12)


def test_describe_on_a_tiny_sample():
    d = SC.describe(np.array([0.1, 0.2, 0.6, 0.9], dtype=np.float32))
    assert d["n"] == 4 and d["mean"] == pytest.approx(0.45) and d["min"] == pytest.approx(0.1) and d["max"] == pytest.approx(0.9)
    assert d["sd"] == pytest.approx(np.std([0.1, 0.2, 0.6, 0.9])) and d["below_half"] == 0.5


def test_the_flag_rule():
    """Outside the range of starts 1 to 8 by more than its width: below lo - w or above hi + w; on the edge is not flagged."""
    base = {s: {"mean": 0.50 + 0.001 * (s - 1), "ks": 0.004} for s in range(1, 9)}  # mean spans [0.500, 0.507], width 0.007
    base[1]["ks"], base[2]["ks"] = 0.003, 0.005  # ks spans [0.003, 0.005], width 0.002
    run = {9: {"mean": 0.5, "ks": 0.004}, 10: {"mean": 0.5141, "ks": 0.004}, 11: {"mean": 0.4929, "ks": 0.004}, 12: {"mean": 0.5, "ks": 0.0071},
           13: {"mean": 0.5, "ks": 0.0009}}
    f = SC.flags({**base, **run})
    assert f["mean"]["width"] == pytest.approx(0.007) and f["mean"]["flagged"] == [10, 11]
    assert f["ks"]["flagged"] == [12, 13]
    # values exact in binary: starts 1 to 8 span [0.5, 0.625], width 0.125; the edges 0.375 and 0.75 are not flagged
    exact = {s: {"mean": 0.5 if s % 2 else 0.625, "ks": 0.25 if s % 2 else 0.5} for s in range(1, 9)}
    exact.update({9: {"mean": 0.75, "ks": 0.75}, 10: {"mean": 0.375, "ks": 0.0}, 11: {"mean": float(np.nextafter(0.75, 1.0)), "ks": 0.5},
                  12: {"mean": float(np.nextafter(0.375, 0.0)), "ks": 0.5}, 13: {"mean": 0.5, "ks": float(np.nextafter(0.75, 1.0))}})
    f = SC.flags(exact)
    assert (f["mean"]["lo"], f["mean"]["hi"], f["mean"]["width"]) == (0.5, 0.625, 0.125)
    assert f["mean"]["flagged"] == [11, 12] and f["ks"]["flagged"] == [13]


def test_the_report_says_what_it_found():
    r = SC.check()
    text = SC.report(r)
    assert "Starts checked: 64. Matching: 64. Mismatched: none." in text
    assert "equal: 16 of 16. Differing arrays: none." in text
    assert "with s the start's own index: yes." in text
    assert "bit-identical: 64 of 64. Differing: none." in text and "Recorded `seed` equal to seed_of(\"start\", s): 64 of 64." in text
    for s in SC.PILOT + SC.RUN:
        assert f"   {s:>5}  {24:>7}  {r['deltas'][s]['mean']:>9.6f}  {r['deltas'][s]['min']:>11.8f}" in text
    assert r["seeds"][9]["seed_key"] == [20261001, "start", 9] and json.dumps(r["seeds"][13]["seed_key"]) in text
    assert r["modules"] == 24 and set(r["entries_per_start"].values()) == {38936} == {r["entries_per_start_json"]}
    for s in SC.RUN:
        assert f"   {s:>5}  {38936:>7}  {r['stats'][s]['mean']:>9.6f}" in text
