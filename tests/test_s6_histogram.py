"""Session 6, plan 2: the on-or-off histogram's arithmetic on tiny made-up arrays, with hand-computed answers, and its
refusals."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from vpd_audit_2 import s6_histogram as H
from vpd_audit_2 import s6_record


def test_a_float32_value_at_a_decimal_edge_falls_by_its_own_value():
    """float32 0.9 is 0.89999998: bin (0.8, 0.9). The rule is floor(10 v) on the stored value, nothing rounder."""
    assert H.bin_counts(np.array([0.9], dtype=np.float32)).tolist() == [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
    assert H.bin_counts(np.array([0.9], dtype=np.float64)).tolist() == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]


def test_the_twelve_bins_by_hand():
    v = np.array([0.0, 1.0, 0.05, 0.1, 0.5, 0.95, 0.999, 0.25, 1.0, 0.0, 0.0], dtype=np.float32)
    # exactly 0: three; exactly 1: two; interior by floor(10 v): 0.05 -> 0, 0.1 -> 1, 0.25 -> 2, 0.5 -> 5, 0.95 -> 9, 0.999 -> 9
    assert H.bin_counts(v).tolist() == [3, 1, 1, 1, 0, 0, 1, 0, 0, 0, 2, 2]
    assert H.bin_counts(v).sum() == v.size
    with pytest.raises(H.Refusal):
        H.bin_counts(np.array([1.5]))


def test_the_groups_of_a_tiny_layout():
    lay = [("a", 3), ("b", 2)]  # flat: a0 a1 a2 a_delta b0 b1 b_delta
    strata = {"a": np.array([0, 10, 4]), "b": np.array([10, 10])}
    g = H.groups_of(lay, strata)
    assert g["never_needed"].tolist() == [1, 4, 5] and g["ever_needed"].tolist() == [0, 2] and g["delta"].tolist() == [3, 6]


def test_untouched_and_turned_by_hand():
    groups = {"never_needed": np.array([0, 1]), "ever_needed": np.array([2, 3, 4]), "delta": np.array([5])}
    start = np.array([0.3, 0.6, 0.2, 0.7, 0.4, 0.9], dtype=np.float32)
    setting = np.array([0.3, 0.0, 0.2, 1.0, 0.55, 0.9], dtype=np.float32)
    cum_abs = np.array([0.0, 2.0, 0.0, 1.0, 3.0, 0.0], dtype=np.float32)
    o = H.one_setting(setting, start, cum_abs, groups, "made up")
    assert (o["never_needed"]["untouched"], o["never_needed"]["turned"]) == (1, 0)  # entry 0 untouched; entry 1 at exactly 0
    assert (o["ever_needed"]["untouched"], o["ever_needed"]["turned"]) == (1, 1)  # entry 2 untouched; 3 at 1; 4 turned
    assert (o["delta"]["untouched"], o["delta"]["turned"]) == (1, 0)
    # ever-needed values 0.2, 1.0, 0.55: bin (0.2, 0.3), exactly 1, bin (0.5, 0.6)
    assert o["ever_needed"]["bins"].tolist() == [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]
    bad = setting.copy()
    bad[2] = 0.25  # untouched, yet not at its start
    with pytest.raises(H.Refusal, match="untouched"):
        H.one_setting(bad, start, cum_abs, groups, "made up")


def _unit(path: Path, batch: str, start: int, start_flat: np.ndarray, setting: np.ndarray, cum_abs: np.ndarray) -> None:
    from vpd_audit_2 import lead_run as LR
    from vpd_audit_2.manifest import deterministic_npz

    names = [name for _, name in H.ROWS]
    meta = {"batch": batch, "start": start, "arm": "lead", "delta_held": False, "start_sha256": LR.setting_sha256(start_flat)}
    path.write_bytes(deterministic_npz({"hook_names": np.array(names), "settings": np.stack([setting] * len(names)).astype(np.float32),
                                        "cum_abs": np.stack([cum_abs] * len(names)).astype(np.float32), "meta": np.array(json.dumps(meta))}))


def test_the_counts_over_two_tiny_searches_by_hand(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "SIDES", {"attack": ("A1",), "heldout": ("H1",)})
    lay = [("a", 3), ("b", 2)]  # flat: a0 a1 a2 a_delta b0 b1 b_delta
    groups = H.groups_of(lay, {"a": np.array([0, 10, 4]), "b": np.array([10, 10])})  # never: 1, 4, 5; ever: 0, 2; delta: 3, 6
    start = np.array([0.3, 0.6, 0.2, 0.7, 0.4, 0.95, 0.5], dtype=np.float32)
    a_set = np.array([0.0, 0.6, 1.0, 0.75, 0.0, 0.95, 1.0], dtype=np.float32)
    a_cum = np.array([1.0, 0.0, 2.0, 1.0, 1.0, 0.0, 3.0], dtype=np.float32)
    h_set = np.array([0.3, 1.0, 0.25, 0.0, 0.45, 0.0, 0.5], dtype=np.float32)
    h_cum = np.array([0.0, 1.0, 1.0, 2.0, 1.0, 1.0, 0.0], dtype=np.float32)
    _unit(tmp_path / "a.npz", "A1", 9, start, a_set, a_cum)
    _unit(tmp_path / "h.npz", "H1", 9, start, h_set, h_cum)
    h = H.histogram({("attack", "A1", 9): tmp_path / "a.npz", ("heldout", "H1", 9): tmp_path / "h.npz"}, {9: start}, groups)
    assert h["searches"] == {"attack": 1, "heldout": 1}
    a = h["counts"]["attack"]["n320"]
    # attack, never-needed entries 1, 4, 5: 0.6 untouched (bin 6), 0.0 moved, 0.95 untouched (bin 9)
    assert a["never_needed"]["bins"].tolist() == [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
    assert (a["never_needed"]["untouched"], a["never_needed"]["turned"]) == (2, 0)
    # attack, delta entries 3 and 6: 0.75 turned (bin 7), 1.0
    assert a["delta"]["bins"].tolist() == [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1] and (a["delta"]["untouched"], a["delta"]["turned"]) == (0, 1)
    k = h["counts"]["heldout"]["n159"]
    # held-out, ever-needed entries 0 and 2: 0.3 untouched (bin 3), 0.25 turned (bin 2)
    assert k["ever_needed"]["bins"].tolist() == [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0] and (k["ever_needed"]["untouched"], k["ever_needed"]["turned"]) == (1, 1)
    assert all(h["counts"][side][row][g]["entries"] == {"never_needed": 3, "ever_needed": 2, "delta": 2}[g]
               for side in ("attack", "heldout") for row, _ in H.ROWS for g in H.GROUPS)
    text = H.report(h)
    assert "never-needed, 3 entries: exactly 0 1 (0.33)" in text and "untouched 2 (0.67); turned 0 (0.00)" in text
    rec = H.record_of(h)
    assert json.loads(json.dumps(rec))["counts"]["attack"]["n320"]["delta"]["bins"][8] == 1


def test_a_unit_from_another_start_is_refused(tmp_path):
    lay = [("a", 3), ("b", 2)]
    groups = H.groups_of(lay, {"a": np.array([0, 10, 4]), "b": np.array([10, 10])})
    start = np.full(7, 0.5, dtype=np.float32)
    _unit(tmp_path / "a.npz", "A1", 9, start + np.float32(0.1), start, np.zeros(7, dtype=np.float32))
    with pytest.raises(H.Refusal, match="not the lead search of A1 from start 9"):
        H.histogram({("attack", "A1", 9): tmp_path / "a.npz"}, {9: start}, groups)


def test_an_incomplete_or_changed_set_of_units_is_refused_by_name(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "SIDES", {"attack": ("A1",), "heldout": ("H1",)})
    monkeypatch.setattr(H, "STARTS", (9, 10))
    files = {}
    for b in ("A1", "H1"):
        for s in (9, 10):
            p = tmp_path / f"search_{b}_s{s}.npz"
            p.write_bytes(f"{b}{s}".encode())
            files[f"lead/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    (tmp_path / "backup.json").write_text(json.dumps({"files": files}))
    assert len(H.unit_paths(tmp_path, tmp_path / "backup.json")) == 4
    (tmp_path / "search_H1_s10.npz").unlink()
    (tmp_path / "search_A1_s9.npz").write_bytes(b"changed")
    with pytest.raises(H.Refusal, match=r"missing: search_H1_s10.npz; not the recorded hash: search_A1_s9.npz"):
        H.unit_paths(tmp_path, tmp_path / "backup.json")


def test_the_record_keeps_other_sections(tmp_path):
    path = tmp_path / "record.json"
    s6_record.update("a", {"x": 1}, path)
    s6_record.update("b", [1, 2], path)
    s6_record.update("a", {"x": 2}, path)
    assert json.loads(path.read_text()) == {"a": {"x": 2}, "b": [1, 2]}


@pytest.mark.skipif(not H.UNITS.is_dir(), reason="the run's unit files are on this machine only")
def test_the_runs_units_are_all_here_and_the_ones_recorded():
    assert len(H.unit_paths()) == 160
