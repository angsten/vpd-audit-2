"""The table: its checks, its rows, and Lena's tests T3 to T13 on made-up inputs (plan 1, Section 6).

Expected values come from `freeze/amendment1_specs/table_and_run_spec.md` (Sections 3 and 10) and plan 1 (Sections 5.1
and 12.1). None is this code's output.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

import lead_cases as C
from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_reading as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import pilot as P


def _flat_then(values: list[float], last: float | None = None) -> np.ndarray:
    """A 321-entry record that begins with `values` and then stays at its last value (or at `last`)."""
    rec = np.full(LT.N_RECORD, values[-1] if last is None else last, dtype=np.float64)
    rec[: len(values)] = values
    return rec


def _record(table: dict, row: str, B: int = 2000) -> dict:
    arrays = LT.row_arrays(table, row)
    return LR.row_record(arrays, indices=LI.make_indices(arrays["carried"].shape[0], B=B))


@pytest.fixture(scope="module")
def table() -> dict:
    t = C.synthetic_table(K_=4, low_attack=2, low_heldout=1)
    LT.validate(t)
    return t


# ----------------------------------------------------------------------------- the checks


def _mutated(table: dict, **changes) -> dict:
    out = dict(table)
    out["meta"] = json.loads(json.dumps(table["meta"]))
    for k, v in changes.items():
        out[k] = v
    return out


def _with(arr: np.ndarray, index: tuple, value) -> np.ndarray:
    out = arr.copy()
    out[index] = value
    return out


def test_validate_passes_and_every_check_can_fail(table):
    t = table
    h10 = list(LT.SETTINGS_LEAD).index("h10")
    assert t["step_A"][0, 0, h10] == -1  # the first two attack searches never reach 10 nats
    one_up = np.nextafter(t["own_H"][2, 0, 0], np.inf)
    meta_incomplete = {**t["meta"], "complete": False}
    meta_passes = {**t["meta"], "n_scoring_passes": t["meta"]["n_scoring_passes"] - 1}
    meta_real = {**t["meta"], "kind": "real"}
    no_text = {k: v for k, v in t.items() if k not in LT.PER_TEXT_ARRAYS}
    cases = {
        "nan_exactly_where_setting_missing": [
            _mutated(t, carried=_with(t["carried"], (1, 2, 3, 0), np.nan)),  # a complete table with one cell set to NaN
            _mutated(t, carried=_with(t["carried"], (0, 2, 0, h10), 1.0)),  # a harm where the setting is missing
            _mutated(t, shuf=_with(t["shuf"], (1, 1, 1, 5, 0), 0.4)),  # a shuffled harm at a setting with no shuffled copies
            _mutated(t, own_H_text=_with(t["own_H_text"], (2, 0, 0, 7), np.nan)),
        ],
        "arrays_present_with_declared_shapes": [
            _mutated(t, carried=t["carried"].reshape(4, 4, 10, 5)),  # one array reshaped
            _mutated(t, own_A=t["own_A"].astype(np.float32)),
            {k: v for k, v in t.items() if k != "block_ids_sha"},
            {k: v for k, v in t.items() if k != "init_H_text"},  # some, but not all, of the per-text arrays
            {**no_text, "meta": meta_real},  # a real table carries its per-text harms
        ],
        "block_ids_match_heldout_ids": [_mutated(t, block_ids_sha=_with(t["block_ids_sha"], (3, 1, 2), "0" * 64))],
        "heldout_ids_differ_from_attack_ids": [_mutated(t, ids_sha_A=_with(t["ids_sha_A"], (2,), t["ids_sha_H"][1]),)],
        "own_equals_record_at_step": [_mutated(t, own_H=_with(t["own_H"], (2, 0, 0), one_up)),
                                      _mutated(t, own_A=_with(t["own_A"], (3, 4, 2), t["own_A"][3, 4, 3]))],
        "init_equals_record_start": [_mutated(t, init_A=_with(t["init_A"], (1, 1), t["init_A"][1, 2]))],
        "fixed_steps": [_mutated(t, step_H=_with(t["step_H"], (0, 0, 2), 79)), _mutated(t, step_A=_with(t["step_A"], (0, 0, 5), -1))],
        "level_steps_equal_crossing_rule": [_mutated(t, step_H=_with(t["step_H"], (3, 3, 7), t["step_H"][3, 3, 7] + 1))],
        "scoring_pass_count": [_mutated(t, meta=meta_passes)],
        "complete_flag": [_mutated(t, meta=meta_incomplete)],
        "setting_hashes_present": [_mutated(t, setting_sha_A=_with(t["setting_sha_A"], (2, 2, 2), ""))],
        "shuffle_hashes_present": [_mutated(t, shuf_sha=_with(t["shuf_sha"], (1, 0, 0, 3), ""))],
        "shuffle_descriptions": [_mutated(t, shuf_absmean_alive=_with(t["shuf_absmean_alive"], (1, 0, 0, 3), np.nan)),
                                 _mutated(t, shuf_moved=_with(t["shuf_moved"], (1, 0, 5, 3), 0.1))],
        "no_other_nan_or_infinite": [_mutated(t, rec_A=_with(t["rec_A"], (0, 0, 300), np.inf)),
                                     _mutated(t, init_H_text=_with(t["init_H_text"], (0, 0, 5), np.nan))],
        "per_text_matches_core": [_mutated(t, carried_text=_with(t["carried_text"], (1, 2, 3, 0, slice(None)), t["carried_text"][1, 2, 3, 0] * 1.001))],
        "axis_labels": [_mutated(t, has_shuffles=np.ones(10, dtype=bool)), _mutated(t, attack_names=_with(t["attack_names"], (1,), "A1"))],
        "metadata": [_mutated(t, meta={**t["meta"], "kind": "pilot"})],
    }
    for check, tables in cases.items():
        for bad in tables:
            with pytest.raises(LT.TableCheckError) as e:
                LT.validate(bad)
            assert e.value.check == check and str(e.value) == check, (check, str(e.value))
            assert not any(c.isdigit() for c in str(e.value))  # the name of the check and no number
    LT.validate(no_text)  # a made-up table may omit the per-text arrays


def test_scoring_pass_count_is_lenas(table):
    lead = C.synthetic_table(K_=16, low_attack=3, per_text=False)
    m = int((lead["step_A"] == -1).sum())  # missing level settings among the attack searches
    assert m == 6  # three searches that never reach 5 or 10 nats
    assert lead["meta"]["n_scoring_passes"] == 94_720 - 144 * m
    delta = C.synthetic_table(K_=8, arm="delta_on", setting_names=LT.SETTINGS_DELTA_ON, per_text=False)
    assert delta["meta"]["n_scoring_passes"] == 14_400
    LT.validate(lead)
    LT.validate(delta)


def test_steps_are_the_existing_crossing_rule(table):
    names = list(LT.SETTINGS_LEAD)
    assert [int(table["step_A"][0, 0, q]) for q in range(7)] == [20, 40, 80, 160, 320, 159, 319]
    for side in ("A", "H"):
        rec, step = table[f"rec_{side}"], table[f"step_{side}"]
        for b in range(rec.shape[0]):
            for s in range(rec.shape[1]):
                for row, h in LT.LEVELS.items():
                    k = P.crossing(rec[b, s].tolist(), h)["k"]
                    assert step[b, s, names.index(row)] == (-1 if k is None else k)


# ----------------------------------------------------------------------------- Lena's tests on made-up inputs


def _table_with_heldout_record(rec: np.ndarray, **kwargs) -> dict:
    """A made-up table whose held-out search (0, 0) has the given record."""
    rec_H = C.synthetic_records(4, 5, 1)
    rec_H[0, 0] = rec
    t = C.synthetic_table(K_=4, rec_H=rec_H, **kwargs)
    LT.validate(t)
    return t


def test_T3_the_denominator_is_the_harm_at_the_crossing_not_the_two_step_mean():
    t = _table_with_heldout_record(_flat_then([0.2, 1.0, 3.5, 1.5, 6.0]))
    h2 = list(LT.SETTINGS_LEAD).index("h2")
    assert t["step_H"][0, 0, h2] == 2  # the 2-nat crossing is at k = 2, where the two-step mean is 2.25
    assert 0.5 * (1.0 + 3.5) == 2.25
    assert LT.row_arrays(t, "h2")["own"][0, 0] == 3.5  # the denominator's raw harm is 3.5, not 2.25


def test_T4_a_crossing_on_the_down_step():
    t = _table_with_heldout_record(_flat_then([0.2, 0.05, 3.9, 0.5], last=0.6))
    names = list(LT.SETTINGS_LEAD)
    assert t["step_H"][0, 0, names.index("h2")] == 3  # (3.9 + 0.5) / 2 = 2.2 reaches the level; (0.05 + 3.9) / 2 does not
    assert LT.row_arrays(t, "h2")["own"][0, 0] == 0.5  # the setting's own harm is 0.5
    assert t["step_H"][0, 0, names.index("h5")] == -1 and bool(LT.row_arrays(t, "h5")["heldout_missing"][0, 0])


def test_T5_a_jump_from_1_to_40_nats_in_one_step():
    jump = np.broadcast_to(_flat_then([0.2, 1.0, 40.0]), (4, 5, LT.N_RECORD)).copy()
    jump[:, :, 0] += 0.001 * np.arange(20).reshape(4, 5)  # starts differ a little, as real ones do
    t = C.synthetic_table(K_=4, rec_A=jump, rec_H=jump + 0.0005)
    LT.validate(t)  # the script accepts it
    names = list(LT.SETTINGS_LEAD)
    for row in ("h2", "h5", "h10"):  # one setting with three names
        assert (t["step_H"][:, :, names.index(row)] == 2).all() and (t["step_A"][:, :, names.index(row)] == 2).all()
        assert LT.row_arrays(t, row)["own"] == pytest.approx(40.0, abs=0.001)  # each with own harm 40
    rec = _record(t, "h2")
    assert rec["level"]["heldout"]["own_harm_median"] == pytest.approx(40.0, abs=0.001)
    assert rec["level"]["attack"]["own_harm_max"] == pytest.approx(40.0, abs=0.001)
    line = next(ln for ln in LR._row_lines(rec) if "Own harm of the scored settings" in ln)  # and prints the overshoot
    assert "attack median 40.00, maximum 40.00; held-out median 40.00, maximum 40.00" in line


def _t6_arrays(offset: np.ndarray) -> dict:
    """Harms that depend on the batches, plus a per-start offset in every raw harm."""
    i = np.arange(4)[:, None, None]
    j = np.arange(4)[None, :, None]
    o = offset[None, None, :]
    held = lambda base: (base + 0.01 * np.arange(4)[:, None] + offset[None, :])  # noqa: E731
    return {"table": "step", "key": 40, "start": held(0.2), "own20": held(0.7), "own": held(5.0),
            "carried": 3.0 + 0.1 * i + 0.01 * j + o, "shuffled": np.broadcast_to((0.4 + 0.01 * j + o)[..., None], (4, 4, 5, 8)).copy(),
            "attack_start": 0.2 + 0.01 * np.arange(4)[:, None] + offset[None, :], "attack_own": 5.0 + 0.1 * np.arange(4)[:, None] + offset[None, :],
            "attack_present": np.ones((4, 5), dtype=bool), "heldout_present": np.ones((4, 5), dtype=bool)}


def _estimates(arrays: dict) -> dict:
    pres = LR.presence_of(arrays)
    return {name: LI.interval(num, den, pres, batch_part="closed_form", percentile=False)
            for name, (num, den) in LR.nine_statistics(arrays).items() if name in ("large", "carries", "carried_added")}


def test_T6_starting_harms_that_differ_by_whole_nats_between_starts():
    whole = np.arange(5, dtype=np.float64)  # start s adds s nats to every raw harm under it
    raw, added = _estimates(_t6_arrays(whole)), _estimates(_t6_arrays(np.zeros(5)))
    # "large" and the carry-over ratio are the same from raw harms as from added harms
    assert raw["large"]["estimate"] == pytest.approx(added["large"]["estimate"], abs=1e-12)
    assert raw["carries"]["estimate"] == pytest.approx(added["carries"]["estimate"], abs=1e-12)
    # any mismatch of starts changes them by whole nats: read the held-out batch's harms under one start for all
    wrong = _t6_arrays(whole)
    wrong["own20"] = np.repeat(wrong["own20"][:, 1:2], 5, axis=1)
    wrong["start"] = np.repeat(wrong["start"][:, 1:2], 5, axis=1)
    mismatched = _estimates(wrong)
    assert mismatched["large"]["estimate"] - raw["large"]["estimate"] == pytest.approx(1.0, abs=1e-12)  # mean(s) - 1
    assert mismatched["carried_added"]["estimate"] - raw["carried_added"]["estimate"] == pytest.approx(1.0, abs=1e-12)


def test_T7_the_worked_example_of_section_3_8():
    """Two attack batches, two held-out batches, one start, the 20-step row: 0.82, 0.50, 0.22."""
    rec_H = np.stack([np.linspace(0.20, 0.80, 21), np.linspace(0.24, 0.86, 21)])
    rec_H = np.concatenate([rec_H, np.repeat(rec_H[:, -1:], 300, axis=1)], axis=1)[:, None, :]  # [2, 1, 321]
    rec_H[:, 0, 0], rec_H[:, 0, 20] = [0.20, 0.24], [0.80, 0.86]
    rec_A = rec_H + 0.01
    carried = np.zeros((2, 2, 1, 10))
    shuf = np.zeros((2, 2, 1, 10, 8))
    carried[:, :, 0, 0] = [[0.70, 0.74], [0.66, 0.78]]  # carried[i, j] from attack batch i
    shuf[:, :, 0, 0, :] = np.array([[0.60, 0.62], [0.58, 0.64]])[:, :, None]
    t = LT.made_up_table(rec_A, rec_H, carried, shuf, starts=(9,))
    LT.validate(t)
    arrays = LT.row_arrays(t, "n20")
    rec = LR.row_record(arrays, batch_part="closed_form")
    m = rec["means_raw"]
    assert (m["start"], m["own"], m["carried"], m["shuffled"]) == pytest.approx((0.22, 0.83, 0.72, 0.61), abs=1e-12)
    assert rec["carries"]["estimate"] == pytest.approx(0.82, abs=0.005)
    assert rec["depends"]["estimate"] == pytest.approx(0.50, abs=0.005)
    assert rec["kappa"]["estimate"] == pytest.approx(0.22, abs=0.005)
    assert rec["carries"]["start_part_not_estimable"] is True  # one start: no start part
    # the row for attack batch 1 is unaffected by anything missing on attack batch 2
    assert arrays["carried"][0].ravel() == pytest.approx([0.70, 0.74])


def test_T8_a_setting_constant_within_every_stratum():
    lay = [("m0", 12), ("m1", 9)]
    strata = {"m0": np.array([0, 0, 0, 0, 1, 1, 1, 1, 10, 10, 10, 10]), "m1": np.array([0, 1, 0, 1, 0, 1, 10, 10, 10])}
    level = {0: 0.1, 1: 0.9, 10: 0.5}
    flat = np.concatenate([np.array([level[int(v)] for v in strata[name]] + [0.33]) for name, _ in lay]).astype(np.float32)
    for r in range(1, 9):
        copy = P.shuffle_source(flat, lay, strata, ("A1", 9, "n20", r))
        assert np.array_equal(copy, flat)  # every shuffled copy equals the setting
        assert LT.shuffle_displacement(flat, copy, lay, strata) == {"moved": 0.0, "moved_alive": 0.0, "absmean_alive": 0.0}
    # shuffled harm then equals carried harm, and the shuffled ratio is exactly 0
    t = C.synthetic_table(K_=4, shuffled_equals_carried=True)
    LT.validate(t)
    rec = _record(t, "n80")
    assert rec["depends"]["estimate"] == 0.0 and rec["depends"]["interval"] == [0.0, 0.0]
    assert rec["shuffle_moved"] == {"moved_share": 0.0, "mean_abs_change": 0.0}
    assert rec["depends"]["reading"] == "c" and rec["flags"] == []


def test_shuffle_displacement_on_a_hand_example():
    lay = [("m", 4)]
    strata = {"m": np.array([0, 0, 10, 10])}
    setting = np.array([0.0, 1.0, 0.2, 0.9, 0.5])
    assert LT.shuffle_displacement(setting, np.array([1.0, 0.0, 0.9, 0.2, 0.5]), lay, strata) == pytest.approx(
        {"moved": 1.0, "moved_alive": 1.0, "absmean_alive": 1.0})
    assert LT.shuffle_displacement(setting, np.array([0.0, 1.0, 0.9, 0.2, 0.5]), lay, strata) == pytest.approx(
        {"moved": 0.5, "moved_alive": 0.0, "absmean_alive": 0.0})
    assert LT.shuffle_displacement(setting, np.array([0.3, 0.7, 0.2, 0.9, 0.5]), lay, strata) == pytest.approx(
        {"moved": 0.0, "moved_alive": 0.0, "absmean_alive": 0.3})
    # a real shuffle keeps each stratum's values and the delta entry
    copy = P.shuffle_source(setting, lay, strata, ("A1", 9, "n20", 1))
    assert sorted(copy[:2]) == [0.0, 1.0] and sorted(copy[2:4]) == [0.2, 0.9] and copy[4] == 0.5


def test_T9_a_digits_table():
    """carried[i, j, s] = 1 + 0.1 i + 0.01 j + 0.001 s and rec_H[j, s, n] = 2 + 0.01 j + 0.001 s."""
    K, ns = 4, 5
    i, j, s = np.arange(K)[:, None, None], np.arange(K)[None, :, None], np.arange(ns)[None, None, :]
    digits = 1 + 0.1 * i + 0.01 * j + 0.001 * s
    rec_H = np.repeat((2 + 0.01 * np.arange(K)[:, None] + 0.001 * np.arange(ns)[None, :])[:, :, None], LT.N_RECORD, axis=2)
    carried = np.repeat(digits[..., None], 10, axis=-1)
    t = LT.made_up_table(C.synthetic_records(K, ns, 0), rec_H, carried, np.full((K, K, ns, 10, 8), 0.4))
    LT.validate(t)
    arrays = LT.row_arrays(t, "n80")
    assert arrays["carried"] == pytest.approx(digits, abs=1e-15) and arrays["own"] == pytest.approx(rec_H[:, :, 0], abs=1e-15)
    # every marginal mean in closed form
    assert arrays["carried"].mean(axis=(1, 2)) == pytest.approx(1 + 0.1 * np.arange(K) + 0.015 + 0.002, abs=1e-12)  # by attack batch
    assert arrays["carried"].mean(axis=(0, 2)) == pytest.approx(1 + 0.15 + 0.01 * np.arange(K) + 0.002, abs=1e-12)  # by held-out batch
    assert arrays["carried"].mean(axis=(0, 1)) == pytest.approx(1 + 0.15 + 0.015 + 0.001 * np.arange(ns), abs=1e-12)  # by start
    stats = LR.nine_statistics(arrays)
    pres = LR.presence_of(arrays)
    added = LI.interval(*stats["carried_added"], pres, batch_part="closed_form", percentile=False)
    assert added["estimate"] == pytest.approx(-1 + 0.15, abs=1e-12)  # (1 + 0.1 i + ...) - (2 + ...), the j and s digits cancel
    assert added["per_start"] == pytest.approx([-0.85] * ns, abs=1e-12)
    assert added["lin_table"] == pytest.approx(np.repeat((0.1 * (np.arange(K) - 1.5))[:, None], K, axis=1), abs=1e-12)
    points = LR.scatter_points(arrays)
    assert [p["carried_added"] for p in points] == pytest.approx([-1 + 0.1 * (n // ns) for n in range(K * ns)], abs=1e-12)
    # swapping two axes changes a known digit: the attack batch's marginal then moves by hundredths, not tenths
    swapped = arrays["carried"].transpose(1, 0, 2)
    assert swapped.mean(axis=(1, 2)) == pytest.approx(1 + 0.15 + 0.01 * np.arange(K) + 0.002, abs=1e-12)


def test_T10_one_heldout_denominator_near_zero():
    plain = C.arrays_for(110, "step", 320, own=10.21, carried=6.21, shuffled=0.43, noise=0.0)
    own = np.full((C.K, C.NS), 10.21)
    own[0, 0] = 0.21 + 0.01  # one own-search added harm of 0.01
    near_zero = C.arrays_for(110, "step", 320, own=own, carried=6.21, shuffled=0.43, noise=0.0)
    ratio = lambda arrays: LI.interval(*LR.nine_statistics(arrays)["carries"], LR.presence_of(arrays), batch_part="closed_form", percentile=False)["estimate"]  # noqa: E731
    assert ratio(plain) == pytest.approx(0.6, abs=1e-12)
    assert abs(ratio(near_zero) - ratio(plain)) < 0.01  # the ratio of means barely moves
    per_cell = (near_zero["carried"] - near_zero["start"][None]) / (near_zero["own"] - near_zero["start"])[None]
    assert per_cell.mean() > 5  # a mean of per-cell ratios would not


def test_T11_ten_against_eleven_missing_searches_on_one_side():
    idx = LI.make_indices(16, B=2000)
    names = [f"A{i}" for i in range(1, 17)]
    for low, undetermined in ((10, False), (11, True)):
        t = C.synthetic_table(K_=16, low_attack=low, per_text=False)
        LT.validate(t)
        for row in ("h5", "h10"):
            arrays = LT.row_arrays(t, row)
            assert int(arrays["attack_missing"].sum()) == low and arrays["attack_missing"][0].all()  # batch A1 at all five starts
            rec = LR.row_record(arrays, indices=idx)  # no crash
            assert rec["level"]["undetermined"] is undetermined
            assert (rec["flags"] == ["F10"]) is undetermined
            assert all(v == "undetermined" for v in rec["verdicts"].values()) is undetermined
            # no dropped batch without a printed count
            by_batch = rec["level"]["attack"]["missing_by_batch"]
            assert by_batch == {n: k for n, k in zip(names, [5, 5, low - 10]) if k}
            text = "\n".join(LR._row_lines(rec))
            assert f"Missing attack searches: {low} of 80 (allowance 10); batches: A1 (5), A2 (5)" in text
            assert rec["counts"]["carried_cells"] == 16 * (80 - low) and rec["counts"]["own_cells"] == 80
            assert rec["level"]["subtable"]["attack_batches"] == 16 - len(by_batch)
        assert LR.row_record(LT.row_arrays(t, "h2"), indices=idx)["level"]["attack"]["missing"] == 0
    t = C.synthetic_table(K_=16, low_heldout=11, per_text=False)
    rec = LR.row_record(LT.row_arrays(t, "h10"), indices=idx)
    assert rec["level"]["undetermined"] is True and rec["level"]["heldout"]["missing"] == 11
    assert rec["counts"]["carried_cells"] == 1280 and rec["counts"]["own_cells"] == 69  # a missing held-out search blanks no carried cell


def test_T12_validate_refuses_naming_the_check(table):
    t = table
    for bad, check in (
        (_mutated(t, carried=_with(t["carried"], (0, 0, 2, 1), np.nan)), "nan_exactly_where_setting_missing"),
        (_mutated(t, shuf=t["shuf"].reshape(4, 4, 5, 8, 10)), "arrays_present_with_declared_shapes"),
        (_mutated(t, block_ids_sha=_with(t["block_ids_sha"], (0, 0, 0), t["ids_sha_H"][1])), "block_ids_match_heldout_ids"),
    ):
        with pytest.raises(LT.TableCheckError, match=f"^{check}$"):
            LT.validate(bad)


def _all_harm_in_excluded_texts(core: dict) -> dict[str, np.ndarray]:
    """Per-text harms whose batch means are the core values, in which the kept texts of a held-out batch show only the
    start's harm under a carried setting: the excluded texts carry all the carried-over added harm."""
    out = {name: core[name].copy() for name in LT.PER_TEXT_ARRAYS}
    keep = ~core["excluded_H"]  # [K_H, texts]
    n_keep, n_out = keep.sum(axis=1), (~keep).sum(axis=1)
    start = core["init_H"].astype(np.float32).astype(np.float64)[None, :, :, None]  # [1, K_H, n_s, 1]
    rest = (LT.N_TEXTS * core["carried"] - n_keep[None, :, None, None] * start) / n_out[None, :, None, None]
    text = np.where(keep[None, :, None, None, :], start[..., None], rest[..., None])
    out["carried_text"] = np.where(np.isnan(core["carried"])[..., None], np.nan, text).astype(np.float32)
    return out


def test_T13_recomputation_without_the_excluded_texts():
    excluded = np.zeros((4, LT.N_TEXTS), dtype=bool)
    excluded[:, :8] = True
    t = C.synthetic_table(K_=4, float32_exact=True, excluded_H=excluded, per_text=_all_harm_in_excluded_texts)
    LT.validate(t)
    second = LT.without_excluded(t)
    LT.validate(second)
    main_rec, second_rec = _record(t, "n80"), _record(second, "n80")
    q = list(LT.SETTINGS_LEAD).index("n80")
    by_hand = float((t["carried"][:, :, :, q] - t["init_H"][None]).mean() / (t["own_H"][:, :, q] - t["init_H"]).mean())
    assert main_rec["carries"]["estimate"] == pytest.approx(by_hand, rel=1e-12) and by_hand > 0.5
    assert second_rec["carries"]["estimate"] == pytest.approx(0.0, abs=1e-5)  # a known, very different recomputed ratio
    assert second["meta"]["recomputed_without_excluded"] is True and second["meta"]["n_excluded_texts"] == 32
    # no search is rerun: records and steps stay as they were, and so does the attack side
    for name in ("rec_A", "rec_H", "step_A", "step_H", "own_A", "init_A"):
        assert np.array_equal(second[name], t[name], equal_nan=True)
    # an empty exclusion list gives exactly the main result
    plain = C.synthetic_table(K_=4, float32_exact=True)
    again = LT.without_excluded(plain)
    for name in ("carried", "shuf", "own_H", "init_H"):
        assert np.array_equal(again[name], plain[name], equal_nan=True)
    for row in ("n20", "n320", "h5"):
        a, b = _record(plain, row), _record(again, row)
        for stat in ("carries", "depends", "kappa", "carried_added"):
            assert a[stat]["estimate"] == b[stat]["estimate"] and a[stat]["interval"] == b[stat]["interval"]
        assert a["verdicts"] == b["verdicts"]


def test_the_recomputed_table_skips_only_the_heldout_equality_with_the_record(table):
    second = LT.without_excluded(_mutated(table, excluded_H=_with(table["excluded_H"], (slice(None), slice(0, 3)), True)))
    assert not np.array_equal(second["own_H"], table["own_H"], equal_nan=True)  # float32 per-text means, kept texts only
    LT.validate(second)
    assert LT.row_arrays(second, "n80")["own"] is not None
    assert np.array_equal(LT.row_arrays(second, "n80")["own"], second["own_H"][:, :, 2])  # the re-scored array, not the record
    assert np.array_equal(LT.row_arrays(second, "n80")["start"], second["init_H"])
    with pytest.raises(LT.TableCheckError, match="^own_equals_record_at_step$"):  # the attack side is still checked
        LT.validate(_mutated(second, own_A=_with(second["own_A"], (0, 0, 0), second["own_A"][0, 0, 1])))
    with pytest.raises(LT.TableCheckError, match="^per_text_matches_core$"):  # and so is everything else
        LT.validate(_mutated(second, carried=table["carried"] * 1.001))
    with pytest.raises(LT.TableCheckError, match="^per_text_arrays_needed$"):
        LT.without_excluded({k: v for k, v in table.items() if k not in LT.PER_TEXT_ARRAYS})


# ----------------------------------------------------------------------------- rows from the record, and files


def test_past_levels_and_cycling_come_from_the_record():
    rec_H = C.synthetic_records(4, 5, 1)
    rec_H[0, 0, 79], rec_H[0, 0, 80] = 20.0, 10.0  # steps 79 and 80 differ by half of the larger
    rec_H[1, 0] = _flat_then([0.2, 0.3], last=0.4)  # never past any level
    t = C.synthetic_table(K_=4, rec_H=rec_H)
    a = LT.row_arrays(t, "n80")
    assert bool(a["heldout_cycling"][0, 0]) and int(a["heldout_cycling"].sum()) == 1
    assert not a["heldout_past"][2.0][1, 0] and a["heldout_past"][2.0].sum() == 19
    for level in (2.0, 5.0, 10.0):
        k = LT.crossing_steps(t["rec_A"], level)
        assert np.array_equal(a["attack_past"][level], (k != -1) & (k <= 80))
    assert "heldout_past" not in LT.row_arrays(t, "h5")


def test_header_and_long_search_descriptions(table):
    means = LT.batch_means_added_harm(table)
    for side, label in (("A", "attack"), ("H", "heldout")):
        for row, q in (("n20", 0), ("n40", 1)):
            expected = sorted((table[f"own_{side}"][:, :, q] - table[f"init_{side}"]).mean(axis=1))
            assert means[label][row] == pytest.approx(expected) and len(means[label][row]) == 4
    rec = np.zeros((2, 2, LT.N_RECORD))
    rec[0, 0, 301:] = 50.0
    rec[0, 1, 301:] = 30.0
    rec[1, 0, 320] = 40.2
    t = dict(table, rec_A=rec, rec_H=rec * 0.5)
    ls = LT.long_search_levels(t)
    assert ls["searches"] == 8 and ls["max"] == pytest.approx(50.0) and ls["min"] == 0.0
    assert ls["share_at_or_above_paper_level_after_step_320"] == pytest.approx(2 / 8)  # 50 and 40.2; not 30, 25, 20.1


def test_files_round_trip_in_parts_with_hashes(table, tmp_path):
    files = LT.save_table(table, tmp_path / "t", part_bytes=1_200_000)  # one attack batch's per-text harms are about 0.9 MB
    assert [f["name"] for f in files] == ["table_core.npz"] + [f"table_per_text_0{k}.npz" for k in (1, 2, 3, 4)]
    assert all((tmp_path / "t" / f["name"]).stat().st_size < 1_200_000 for f in files[1:])
    assert [f["name"] for f in LT.save_table(table, tmp_path / "two", part_bytes=2_100_000)] == ["table_core.npz", "table_per_text_01.npz", "table_per_text_02.npz"]
    assert len(LT.save_table(table, tmp_path / "one")) == 2  # under the default limit this small table needs one part
    meta = LT.read_meta(tmp_path / "t" / "table_core.npz")
    assert [p["sha256"] for p in meta["per_text_files"]] == [f["sha256"] for f in files[1:]]
    assert sum((p["attack_names"] for p in meta["per_text_files"]), []) == ["A1", "A2", "A3", "A4"]
    assert all(LT.sha256_file(tmp_path / "t" / f["name"]) == f["sha256"] for f in files)
    assert LT.table_files(tmp_path / "t") == [tmp_path / "t" / f["name"] for f in files]
    back = LT.load_table(tmp_path / "t")
    LT.validate(back)
    assert set(back) == set(table)
    for k in table:
        if k != "meta":
            assert back[k].dtype == table[k].dtype and np.array_equal(back[k], table[k], equal_nan=table[k].dtype.kind == "f"), k
    # the same table always gives the same bytes
    again = LT.save_table(table, tmp_path / "u", part_bytes=1_200_000)
    assert again == files


def test_parts_in_the_wrong_order_or_changed_are_refused(table, tmp_path):
    from vpd_audit_2.manifest import deterministic_npz

    LT.save_table(table, tmp_path / "t", part_bytes=1_200_000)
    core_path = tmp_path / "t" / "table_core.npz"
    with np.load(core_path) as z:
        core = {k: z[k] for k in z.files}
    meta = LT.read_meta(core_path)
    meta["per_text_files"] = [meta["per_text_files"][k] for k in (0, 2, 1, 3)]
    core["meta"] = np.array(json.dumps(meta, sort_keys=True))
    (tmp_path / "t" / "table_core.npz").write_bytes(deterministic_npz(core))
    with pytest.raises(LT.TableCheckError, match="^per_text_parts_in_attack_order$"):
        LT.load_table(tmp_path / "t")
    LT.save_table(table, tmp_path / "v", part_bytes=1_200_000)
    part = tmp_path / "v" / "table_per_text_02.npz"
    data = bytearray(part.read_bytes())
    data[len(data) // 2] ^= 1  # one bit of one harm
    part.write_bytes(bytes(data))
    with pytest.raises(LT.TableCheckError, match="^per_text_files_match_core_metadata$"):
        LT.load_table(tmp_path / "v")


def test_a_table_is_real_by_its_metadata_or_by_a_folder_named_sealed(tmp_path):
    made_up, real = {"kind": "made_up"}, {"kind": "real"}
    assert LT.is_real(real, [tmp_path / "t" / "table_core.npz"]) is True
    assert LT.is_real(made_up, [tmp_path / "t" / "table_core.npz"]) is False
    assert LT.is_real(made_up, [tmp_path / "sealed" / "table_core.npz"]) is True
    assert LT.is_real(made_up, [tmp_path / "t" / "table_core.npz", tmp_path / "x" / "sealed" / "deep" / "table_per_text_01.npz"]) is True
    assert LT.is_real({}, [tmp_path / "t" / "table_core.npz"]) is True  # anything not marked made up is real


# ----------------------------------------------------------------------------- session 5, plan 4: what the reviews added


def test_the_arrays_with_no_attack_axis_go_in_a_part_of_their_own_when_they_do_not_fit(tmp_path):
    """Plan 4, Section 6.1: where the arrays with no attack axis and one attack batch's arrays do not fit in one part
    together, the first part holds the arrays with no attack axis alone. So a table of one attack batch can be written
    in two parts, and plan 1's loader reads it back."""
    one = C.synthetic_table(K_=1, ns=1)
    LT.validate(one)
    files = LT.save_table(one, tmp_path / "one", part_bytes=1_000)
    assert [f["name"] for f in files] == ["table_core.npz", "table_per_text_01.npz", "table_per_text_02.npz"]
    meta = LT.read_meta(tmp_path / "one" / "table_core.npz")
    assert [p["attack_names"] for p in meta["per_text_files"]] == [[], ["A1"]]
    with np.load(tmp_path / "one" / "table_per_text_01.npz") as z:
        assert sorted(z.files) == ["init_H_text", "own_H_text", "part_attack_names"] and z["part_attack_names"].size == 0
    with np.load(tmp_path / "one" / "table_per_text_02.npz") as z:
        assert sorted(z.files) == sorted(LT.PER_TEXT_WITH_ATTACK_AXIS + ("part_attack_names",)) and z["part_attack_names"].tolist() == ["A1"]
    back = LT.load_table(tmp_path / "one")
    LT.validate(back)
    for k in one:
        if k != "meta":
            assert back[k].dtype == one[k].dtype and np.array_equal(back[k], one[k], equal_nan=one[k].dtype.kind == "f"), k
    assert len(LT.save_table(one, tmp_path / "whole")) == 2  # under the default limit everything is in one part, as before
    # with more attack batches the same rule holds: the part with no attack batch, then the batches in order
    two = C.synthetic_table(K_=2, ns=1)
    assert [p["attack_names"] for p in (LT.save_table(two, tmp_path / "two", part_bytes=1_000) and LT.read_meta(tmp_path / "two" / "table_core.npz")["per_text_files"])] == [
        [], ["A1"], ["A2"]]
    back = LT.load_table(tmp_path / "two")
    assert np.array_equal(back["carried_text"], two["carried_text"]) and np.array_equal(back["own_H_text"], two["own_H_text"])
    # a part that holds no attack batch and is listed out of place does not change the joined order; a part that does, does
    from vpd_audit_2.manifest import deterministic_npz

    with np.load(tmp_path / "two" / "table_core.npz") as z:
        core = {k: z[k] for k in z.files}
    meta = LT.read_meta(tmp_path / "two" / "table_core.npz")
    meta["per_text_files"] = [meta["per_text_files"][k] for k in (0, 2, 1)]
    core["meta"] = np.array(json.dumps(meta, sort_keys=True))
    (tmp_path / "two" / "table_core.npz").write_bytes(deterministic_npz(core))
    with pytest.raises(LT.TableCheckError, match="^per_text_parts_in_attack_order$"):
        LT.load_table(tmp_path / "two")


def test_validate_repeats_the_two_wrong_batch_comparisons(table):
    """Plan 4, Section 4.4 (Riku's review, Section 4). The program that reads the table checks for itself that no
    carried cell's per-text harms are all equal to the same setting's on its attack batch, or to the held-out batch's
    own setting's. First his example, with three texts; then whole tables through `validate`."""
    one = np.ones((1, 1, 1), dtype=bool)
    own_A = np.array([0.9, 1.1, 1.0], dtype=np.float32).reshape(1, 1, 1, 3)
    own_H = np.array([0.7, 0.8, 0.6], dtype=np.float32).reshape(1, 1, 1, 3)

    def check(carried: list[float], present_H: np.ndarray = one) -> str | None:
        t = {"carried_text": np.array(carried, dtype=np.float32).reshape(1, 1, 1, 1, 3), "own_A_text": own_A, "own_H_text": own_H}
        try:
            LT._check_carried_is_neither_own(t, one, present_H)
        except LT.TableCheckError as e:
            return e.check
        return None

    assert check([0.5, 0.6, 0.4]) is None  # sound: equal to neither
    assert check([0.7, 0.8, 0.6]) == "carried_differs_from_own_batch_values"  # the held-out batch scored with its own setting
    assert check([0.9, 1.1, 1.0]) == "carried_differs_from_own_batch_values"  # the setting scored on its attack batch
    assert check([0.7, 0.8, 0.5]) is None and check([0.9, 1.1, 0.6]) is None  # all but one value equal is not equal
    assert check([0.7, 0.8, 0.6], present_H=~one) is None  # the held-out batch has no such setting: nothing to equal

    # whole tables: the made-up table gives every text its batch's value, so a carried cell set to an own value is equal in all 128
    t = table
    LT.validate(t)
    q = 2
    as_heldout = _mutated(t, carried=_with(t["carried"], (1, 2, 3, q), t["own_H"][2, 3, q]),
                          carried_text=_with(t["carried_text"], (1, 2, 3, q, slice(None)), t["own_H_text"][2, 3, q]))
    as_attack = _mutated(t, carried=_with(t["carried"], (1, 2, 3, q), t["own_A"][1, 3, q]),
                         carried_text=_with(t["carried_text"], (1, 2, 3, q, slice(None)), t["own_A_text"][1, 3, q]))
    for bad in (as_heldout, as_attack):
        with pytest.raises(LT.TableCheckError) as e:
            LT.validate(bad)
        assert e.value.check == "carried_differs_from_own_batch_values"
        assert LT.failed_checks(bad) == ["carried_differs_from_own_batch_values"]
    # the other held-out batch's own value in the cell is not this error, and nothing else catches it: the check is by batch
    other = _mutated(t, carried=_with(t["carried"], (1, 2, 3, q), t["own_H"][0, 3, q]),
                     carried_text=_with(t["carried_text"], (1, 2, 3, q, slice(None)), t["own_H_text"][0, 3, q]))
    LT.validate(other)
    # skipped for a made-up table without per-text arrays, and for the copy recomputed without the overlapping texts
    LT.validate({k: v for k, v in as_heldout.items() if k not in LT.PER_TEXT_ARRAYS})
    recomputed = LT.without_excluded(_mutated(as_heldout, excluded_H=_with(t["excluded_H"], (slice(None), slice(0, 3)), True)))
    LT.validate(recomputed)
    # a level setting missing on the held-out side leaves nothing to compare with there; the cell is still checked against the attack batch
    h10 = list(LT.SETTINGS_LEAD).index("h10")
    assert t["step_H"][0, 0, h10] == -1 and t["step_A"][3, 0, h10] != -1 and np.isnan(t["own_H_text"][0, 0, h10]).all()
    with pytest.raises(LT.TableCheckError, match="^carried_differs_from_own_batch_values$"):
        LT.validate(_mutated(t, carried=_with(t["carried"], (3, 0, 0, h10), t["own_A"][3, 0, h10]),
                             carried_text=_with(t["carried_text"], (3, 0, 0, h10, slice(None)), t["own_A_text"][3, 0, h10])))


def test_the_list_of_checks_names_every_check_validate_makes():
    import inspect
    import re

    source = "".join(inspect.getsource(f) for f in (LT.validate, LT._check_per_text, LT._check_carried_is_neither_own))
    made = list(dict.fromkeys(re.findall(r'_fail\("([a-z_]+)"\)', source)))
    assert made == list(LT.CHECKS)  # every name, in the order `validate` first makes it
    loader = set(re.findall(r'_fail\("([a-z_]+)"\)', inspect.getsource(LT.load_table)))
    assert set(LT.LOADER_CHECKS) <= loader and loader - set(LT.LOADER_CHECKS) == {"arrays_present_with_declared_shapes"}
    assert not any(c.isdigit() for name in LT.CHECKS + LT.LOADER_CHECKS for c in name)
