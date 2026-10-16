"""Plan 6 of the research log: the breakout rule on constructed series, the readings on constructed outcomes, the extension
rule, the trend, and amendment 1's recomputation (`vpd_audit_2/three_arm_read.py`, `three_arm_run.extension_lengths`)."""

from __future__ import annotations

import numpy as np
import pytest

from vpd_audit_2 import three_arm_read as R
from vpd_audit_2 import three_arm_run as TR


@pytest.mark.parametrize("series,want", [
    ([1, 2, 3, 4], None),
    ([1, 9, 1, 1], 2),  # (1 + 9) / 2 = 5 at batch 2
    ([4.9, 5.0, 5.2], 3),  # (4.9 + 5.0) / 2 = 4.95; (5.0 + 5.2) / 2 = 5.1
    ([6.0], None),  # one batch has no pair
    ([0.5] * 10 + [4.0, 6.0, 6.0], 12),
])
def test_breakout_on_constructed_series(series, want):
    assert R.breakout(np.array(series)) == want == TR.breakout(np.array(series))


@pytest.mark.parametrize("arm1,yard,want", [
    ({1: 300, 2: 500}, {1: 100, 2: 90}, 3),
    ({1: 300, 2: 500}, {1: None, 2: None}, 3),  # arm 1 breaking out in both seeds reads 3 whatever the yardstick did
    ({1: None, 2: None}, {1: None, 2: None}, 1),
    ({1: None, 2: None}, {1: 120, 2: 140}, 2),
    ({1: None, 2: None}, {1: 120, 2: None}, 4),  # the yardstick's seeds disagree
    ({1: 400, 2: None}, {1: 120, 2: 140}, 4),  # arm 1's seeds disagree
    ({1: 400, 2: None}, {1: None, 2: None}, 4),
])
def test_each_reading_on_constructed_outcomes(arm1, yard, want):
    assert R.reading(arm1, yard) == want


def test_the_extension_rule():
    assert TR.extension_lengths(None, {"released": None, "per_document": None}) == {}
    assert TR.extension_lengths(80, {"released": None, "per_document": None}) == {}  # 10 b = 800 is within the run
    assert TR.extension_lengths(150, {"released": None, "per_document": 700}) == {"released": 1500}
    assert TR.extension_lengths(450, {"released": None, "per_document": None}) == {"released": 3000, "per_document": 3000}  # capped
    assert TR.extension_lengths(101, {"released": None, "per_document": None}) == {"released": 1010, "per_document": 1010}


def test_the_trend():
    h = np.concatenate([np.zeros(800), 0.01 * np.arange(200)])
    t = R.trend(h)
    assert t["slope_per_100_batches"] == pytest.approx(1.0) and t["mean_first"] == 0.0 and t["mean_last"] == pytest.approx(0.995) and t["batches"] == 1000


def test_amendment_1_from_the_committed_history():
    t = R.training_log()
    assert t["points"] == 2001 and t["reached_5"] is True and t["steps_at_or_above_5"] == [0] and t["max"] == pytest.approx(5.215, abs=1e-3)
    assert t["max_after_first_tenth"] == pytest.approx(1.814, abs=1e-3) and t["step_of_that_max"] == 360600
    assert t["points_above_2_after_first_tenth"] == 0 and 0.02 < t["share_above_2"] < 0.04 and len(t["mean_by_tenth"]) == 10


def test_the_sentences():
    assert "within 3000 batches" in R.SENTENCES[2].format(n=3000, b=150) and "cannot reach" in R.SENTENCES[2]
    assert "weakness per step alone does not explain" in R.SENTENCES[3].lower() and "stronger adversary" not in R.SENTENCES[3]
