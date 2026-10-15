"""Session 7, plan 2: the post's Figure 1. The point set and the reference values on the real lead table (read only), and
each drawing function on six made-up points. Fast; no GPU."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import post_figure as PF


@pytest.fixture(scope="module")
def table():
    return LT.load_table(PF.TABLE)


@pytest.fixture(scope="module")
def points(table):
    return PF.figure_points(table)


def test_the_point_set_has_637_rows_eighty_per_step_row_and_80_79_78_at_the_levels(points):
    assert len(points) == 637
    counts = points["row"].value_counts().to_dict()
    assert counts == {"n20": 80, "n40": 80, "n80": 80, "n160": 80, "n320": 80, "h2": 80, "h5": 79, "h10": 78}
    assert not (points["step"] == -1).any()
    assert set(points["row"]) == set(PF.POINT_ROWS)  # n159 and n319 are left out
    assert int(points["in_post_figure"].sum()) == 559
    assert points["in_post_figure"].equals(points["row"].isin(("n20", "n40", "n80", "n160", "n320", "h2", "h5")))
    assert points[["attack_batch", "start"]].drop_duplicates().shape[0] == 80


@pytest.mark.parametrize("row", ["n20", "h2", "n320"])
def test_three_points_equal_their_values_recomputed_by_hand(table, points, row):
    names = [str(x) for x in table["setting_names"]]
    i = [str(x) for x in table["attack_names"]].index("A1")
    s = [int(x) for x in table["starts"]].index(9)
    q = names.index(row)
    assert table["step_A"][i, s, q] != -1
    got = points[(points["row"] == row) & (points["attack_batch"] == "A1") & (points["start"] == 9)]
    assert len(got) == 1
    got = got.iloc[0]
    K_H, R = table["carried"].shape[1], table["shuf"].shape[-1]
    unseen = np.array([table["carried"][i, j, s, q] for j in range(K_H)])
    shuffled = np.array([table["shuf"][i, j, s, q, r] for j in range(K_H) for r in range(R)])
    assert got["own_batch_harm"] == table["own_A"][i, s, q]
    assert got["step"] == table["step_A"][i, s, q]
    assert got["unseen_harm_mean"] == pytest.approx(unseen.sum() / K_H, rel=1e-12, abs=0)
    assert got["unseen_harm_min"] == unseen.min() and got["unseen_harm_max"] == unseen.max()
    assert got["shuffled_harm_mean"] == pytest.approx(shuffled.sum() / (K_H * R), rel=1e-12, abs=0)
    assert got["attack_start_harm"] == table["init_A"][i, s]


def test_the_reference_values_are_the_held_out_searches_at_20_steps_and_the_random_start(table):
    refs = PF.reference_values(table)
    q20 = [str(x) for x in table["setting_names"]].index("n20")
    assert refs["benchmark"] == table["own_H"][:, :, q20].mean()
    assert refs["random_start"] == table["init_H"].mean()


def _six_points() -> pd.DataFrame:
    rows = [("n20", 0.7, 0.6, 0.30), ("n80", 4.0, 3.5, 0.31), ("n320", 40.0, 38.0, 0.29),
            ("h2", 2.1, 1.9, 0.32), ("h5", 5.4, 5.0, 0.30), ("h10", 11.0, 10.0, 0.28)]
    return pd.DataFrame([{"row": r, "attack_batch": "A1", "start": 9, "step": k + 10, "own_batch_harm": own, "unseen_harm_mean": unseen,
                          "unseen_harm_min": unseen * 0.9, "unseen_harm_max": unseen * 1.1, "shuffled_harm_mean": shuf,
                          "in_post_figure": r != "h10", "attack_start_harm": 0.22}
                         for k, (r, own, unseen, shuf) in enumerate(rows)], columns=list(PF.COLUMNS))


@pytest.mark.parametrize("variant", PF.VARIANTS)
def test_the_carry_over_figure_writes_a_png(tmp_path, variant):
    path = PF.draw_carry_over(_six_points(), {"benchmark": 0.75, "random_start": 0.22}, tmp_path / f"{variant}.png", variant)
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_the_registered_figure_writes_a_png(tmp_path):
    path = PF.draw_registered(_six_points(), {"benchmark": 0.75, "random_start": 0.22}, tmp_path / "registered.png")
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_point_outside_the_axes_is_refused_not_clipped(tmp_path):
    pts = _six_points()
    pts.loc[0, "unseen_harm_mean"] = 0.1  # below the raw axes' 0.15
    with pytest.raises(ValueError):
        PF.draw_carry_over(pts, {"benchmark": 0.75, "random_start": 0.22}, tmp_path / "x.png", "b")
    pts = _six_points()
    pts.loc[0, "own_batch_harm"] = 0.2  # added harm 0.2 - 0.22 is negative: a log axis would drop it
    with pytest.raises(ValueError):
        PF.draw_registered(pts, {"benchmark": 0.75, "random_start": 0.22}, tmp_path / "y.png")
