"""Plan 1 of the research log, Section 2.4: the starts test's reading script, checked before any GPU result exists.

  - On the pilot's 64 records alone it reproduces the research log's Appendix G figures. Four of the 25 printed
    there were rounded twice, to two decimals and then to one; the exact values are pinned here, and every figure equals
    the exact value rounded that way (see `APPENDIX_G` and the report).
  - Its analysis of variance on the pilot's 8 by 8 tables is the pilot's own (`results/s4_pilot/part_a/tables.json`).
  - The added-harm and final-level arithmetic, and the reading's thresholds, on tiny made-up records.
  - A complete made-up set of test records is read in the order fixed; a guard that differs by one bit stops the reading
    after the guard's line; an incomplete or misnamed set is refused.
"""

from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pytest

from vpd_audit_2 import starts_test as ST

# Appendix G of the research log: the pilot's by-start mean added harm, starts 1 to 8, and its mean at 320 steps.
APPENDIX_G = {80: [8.8, 6.8, 9.3, 11.1, 11.5, 9.3, 7.9, 13.5], 160: [23.4, 16.9, 23.1, 22.4, 24.3, 21.4, 24.2, 21.1],
              320: [27.4, 22.1, 27.5, 26.5, 25.0, 22.3, 29.5, 23.3]}
APPENDIX_G_MEAN_320 = 25.5
# The four figures whose single rounding to one decimal differs from the Appendix's: (step, start) to the exact value's first
# six decimals. Each lies within 0.0006 below a .x5 boundary; rounded to two decimals first, it rounds up.
DOUBLE_ROUNDED = {(80, 5): 11.449548, (160, 6): 21.345238, (320, 3): 27.449431}
PILOT_MEAN_320 = 25.448531


def twice(x: float) -> float:
    """Rounded to two decimals, then to one with halves up: how the Appendix's figures were rounded."""
    return float(Decimal(f"{x:.2f}").quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


@pytest.fixture(scope="module")
def pilot():
    return ST.pilot_searches()


def test_the_pilot_alone_reproduces_appendix_g(pilot):
    """Plan 1 of the research log, Section 2.4, the verification before any GPU result: the by-start means at 80, 160, and 320 steps and the
    pilot's mean at 320. 21 of the 24 by-start figures, rounded once to one decimal, equal the Appendix's; the three others
    and the mean are the Appendix's when rounded as it was, twice."""
    singles_differ = []
    for k, expected in APPENDIX_G.items():
        got = ST.by_start(pilot, ST.PILOT_STARTS, k)
        for s, e in zip(ST.PILOT_STARTS, expected):
            assert twice(got[s]) == e, (k, s, got[s])
            if round(got[s], 1) != e:
                singles_differ.append((k, s))
                assert got[s] == pytest.approx(DOUBLE_ROUNDED[(k, s)], abs=5e-7)
    assert sorted(singles_differ) == sorted(DOUBLE_ROUNDED)
    mean = ST.mean_added(pilot, [(b, s) for b in ST.BATCHES for s in ST.PILOT_STARTS], 320)
    assert mean == pytest.approx(PILOT_MEAN_320, abs=5e-7) and twice(mean) == APPENDIX_G_MEAN_320 and round(mean, 1) == 25.4
    assert ST.PILOT_REFERENCE == APPENDIX_G_MEAN_320 and ST.RUN_REFERENCE == 34.5  # the reference values are quoted, not computed


def test_the_pilot_only_printout(pilot, capsys):
    assert ST.main(["--pilot-only"]) == 0
    out = capsys.readouterr().out
    assert "over its 64 searches of C1 to C8 from starts 1 to 8: 25.4485 nats." in out and "Reading:" not in out
    assert "the pilot's 25.5 (C1 to C8 from starts 1 to 8; exactly 25.4485 from runs.json); the run's 34.5" in out
    assert "The earlier figure 25.5 was rounded twice (25.4485 to 25.45, then to 25.5); rounded once it is 25.4. The thresholds, 31 and 29, are untouched." in out
    # Section 7's 12.5 percent for the pilot is 8 of 64, by the harm after step 320; by the final level it is 7
    assert "by the harm after step 320 (as the research log's Section 7 counted its 12.5 and 31 percent): 8 of 64 (12.5 percent)." in out
    assert "At or above 40.2 nats, by the final level: 7 of 64 (10.9 percent)." in out
    assert out.index("5. Description") < out.index("6. Description: the breakout step.")
    assert "       C1      83       -      64      45      78      54      44       -\n" in out  # C1's breakout steps, starts 1 to 8
    assert "        2      96.5       1\n" in out and "        8        64       2\n" in out  # starts 2 and 8: median, never
    assert "        5       11.45       24.31       24.99" in out  # start 5's row, two decimals
    assert out.index("1. The pilot's mean") < out.index("2. Each start's") < out.index("3. Each batch's") < out.index("4. The pilot's 8 by 8") < out.index("5. Description")


def test_the_analysis_of_variance_is_the_pilots_own(pilot):
    stored = json.load(open(ST.env.REPO_ROOT / "results" / "s4_pilot" / "part_a" / "tables.json"))["variance_components"]["budgets"]
    for k in ST.STEPS:
        a = ST.anova(ST.table(pilot, ST.PILOT_STARTS, k))
        for key in ("mean", "MS_B", "MS_S", "MS_R", "sigma2_int", "sigma2_b", "sigma2_c", "sigma2_c_untruncated"):
            assert a[key] == pytest.approx(stored[str(k)][key], rel=1e-12, abs=1e-12), (k, key)
        assert a["df"] == {"B": 7, "S": 7, "R": 49}
        assert a["start_share"] == a["sigma2_c"] / (a["sigma2_b"] + a["sigma2_c"] + a["sigma2_int"])


def test_the_analysis_of_variance_on_a_table_built_by_hand():
    """Batch effects 0, 2, 4 and start effects 0, 6, with no residual: MS_B = 2 * 4 = 8, MS_S = 3 * 18 = 54, MS_R = 0."""
    Y = np.array([[0.0, 6.0], [2.0, 8.0], [4.0, 10.0]])
    a = ST.anova(Y)
    assert (a["MS_B"], a["MS_S"], a["MS_R"]) == (8.0, 54.0, 0.0)
    assert a["sigma2_b"] == 4.0 and a["sigma2_c"] == 18.0 and a["start_share"] == 18.0 / 22.0


def test_added_harm_and_final_level_on_a_tiny_made_up_record():
    rec = [0.25 + j for j in range(321)]  # harm 0.25 at the start, one nat more after every step
    assert ST.added(rec, 0) == 0.0 and ST.added(rec, 80) == 80.0 and ST.added(rec, 320) == 320.0
    assert ST.final_level(rec) == pytest.approx(0.25 + (301 + 320) / 2)  # steps 301 to 320: twenty values
    flat = [0.2] * 301 + [40.0, 41.0] * 10  # alternating over the last twenty steps
    assert ST.final_level(flat) == 40.5 and ST.added(flat, 320) == pytest.approx(40.8)
    assert ST.final_level([0.0] * 300 + [1000.0] + [2.0] * 20) == 2.0  # step 300 is not among the last twenty


def test_the_reading_thresholds():
    assert ST.reading(31.0) == "Starts" and ST.reading(34.5) == "Starts"
    assert ST.reading(29.0) == "Something else" and ST.reading(25.5) == "Something else"
    for x in (float(np.nextafter(31.0, 0.0)), 30.0, float(np.nextafter(29.0, 99.0))):
        assert ST.reading(x) == "Undetermined"


# ----------------------------------------------------------------------------- a complete made-up set of test records


def _made_up(pilot, guard=None, drop=None, extra=None) -> dict:
    """Test search (C_j, s): its harm rises linearly from 0.2 to 0.2 + 30 + j + (s - 9) / 2 at step 320, so its added
    harm at step k is (30 + j + (s - 9) / 2) * k / 320."""
    searches = []
    for j, b in enumerate(ST.BATCHES, start=1):
        for s in ST.TEST_STARTS:
            if (b, s) == drop:
                continue
            top = 30 + j + (s - 9) / 2
            searches.append({"batch": b, "start": s, "role": "test", "record": [0.2 + top * k / 320 for k in range(321)]})
    searches.append({"batch": "C1", "start": 1, "role": "guard", "record": list(pilot[("C1", 1)]) if guard is None else guard})
    searches += extra or []
    return {"searches": searches}


def test_a_complete_set_is_read_in_the_order_fixed(pilot, tmp_path, capsys):
    path = tmp_path / "records.json"
    path.write_text(json.dumps(_made_up(pilot)))
    assert ST.main(["--records", str(path)]) == 0
    out = capsys.readouterr().out
    # mean over j = 1..8 and s = 9..13 of 30 + j + (s - 9) / 2 = 30 + 4.5 + 1 = 35.5
    assert "1. The deciding statistic" in out and "   35.5000 nats. Reading: Starts." in out
    assert "the pilot's 25.5 (C1 to C8 from starts 1 to 8; exactly 25.4485 from runs.json); the run's 34.5" in out
    assert "was rounded twice (25.4485 to 25.45, then to 25.5)" in out
    assert "The guard: C1 from start 1, searched again in this test, equals the pilot's record" in out
    order = ["The guard:", "1. The deciding statistic", "2. Each start's", "3. Each batch's", "4. The 8 by 13 tables", "5. Description",
             "6. Description: the breakout step."]
    assert [out.index(x) for x in order] == sorted(out.index(x) for x in order)
    test, _ = ST.load_test_searches(path)
    bs = ST.by_start(test, ST.TEST_STARTS, 160)
    assert bs[9] == pytest.approx(34.5 / 2) and bs[13] == pytest.approx(36.5 / 2)  # start s: 30 + 4.5 + (s - 9) / 2, half of it at 160
    # batch C2 over starts 9 to 13: 30 + 2 + 1 = 33 at 320 steps, so 8.25 at 80 and 16.50 at 160, beside the pilot's own C2
    p = {k: ST.by_batch(pilot, ST.PILOT_STARTS, k)["C2"] for k in ST.STEPS}
    assert f"   {'C2':>6}{8.25:>12.2f}{p[80]:>12.2f}{16.5:>12.2f}{p[160]:>12.2f}{33.0:>12.2f}{p[320]:>12.2f}\n" in out
    joined = ST.table({**pilot, **test}, ST.PILOT_STARTS + ST.TEST_STARTS, 320)
    assert joined.shape == (8, 13) and joined[2, 12] == pytest.approx(30 + 3 + 2) and joined[0, 0] == ST.added(pilot[("C1", 1)], 320)
    assert out.count("Mean squares: batch") == 3 and "(df 7), start" in out and "(df 12), residual" in out and "(df 84)" in out
    f = ST.finals(test, [(b, s) for b in ST.BATCHES for s in ST.TEST_STARTS])
    assert f["n"] == 40 and f["at_or_above_paper_by_final"] == sum(1 for key in f["by_search"] if f["by_search"][key] >= 40.2)
    assert f["at_or_above_paper_by_320"] == sum(1 for key in test if test[key][320] >= 40.2)
    assert f"by the harm after step 320 (as the research log's Section 7 counted its 12.5 and 31 percent): {f['at_or_above_paper_by_320']} of 40" in out
    assert f"At or above 40.2 nats, by the final level: {f['at_or_above_paper_by_final']} of 40" in out


def test_the_breakout_step_on_tiny_made_up_records():
    rec = [0.2] + [0.2] * 49 + [4.0, 6.0] + [6.0] * 269  # steps 50 and 51 are 4 and 6: the two-step mean reaches 5 at k = 51
    assert len(rec) == 321 and ST.breakout(rec) == 51
    assert ST.breakout([0.2] * 100 + [9.8] + [0.2] * 220) == 100  # (0.2 + 9.8) / 2 = 5.0 at k = 100: reaching counts
    assert ST.breakout([4.9] * 321) is None
    assert ST.median_breakout([40, None, 60]) == 60.0 and ST.median_breakout([40, None, None, 60]) == float("inf")
    assert ST.median_breakout([10, 20, 30, 40]) == 25.0


def test_the_breakout_step_is_the_pilot_hooks_own_crossing(pilot):
    """The pilot's save hook recorded each search's 5-nat crossing as it ran; the reading's rule gives the same step."""
    a1 = json.load(open(ST.PILOT_RUNS))["a1"]
    for b in ST.BATCHES:
        for s in ST.PILOT_STARTS:
            assert ST.breakout(pilot[(b, s)]) == a1[b][str(s)]["hook_events"].get("two_step_mean_reaches_5"), (b, s)


def test_the_two_counts_at_40_2_differ_where_they_should():
    """By the harm after step 320 and by the final level: a search that ends high after alternating, and one that ends
    low after being high."""
    a = [0.2] * 301 + [38.0, 43.0] * 10  # step 320 is 43.0; the final level is 40.5
    b = [0.2] * 301 + [45.0] * 19 + [39.0]  # step 320 is 39.0; the final level is 44.7
    c = [0.2] * 301 + [30.0] * 20  # neither
    f = ST.finals({("C1", 9): a, ("C1", 10): b, ("C1", 11): c}, [("C1", 9), ("C1", 10), ("C1", 11)])
    assert f["at_or_above_paper_by_320"] == 1 and f["at_or_above_paper_by_final"] == 2


def test_a_guard_that_differs_by_one_bit_stops_the_reading(pilot, tmp_path, capsys):
    guard = list(pilot[("C1", 1)])
    guard[-1] = float(np.nextafter(guard[-1], 1e9))
    path = tmp_path / "records.json"
    path.write_text(json.dumps(_made_up(pilot, guard=guard)))
    assert ST.main(["--records", str(path)]) == 1
    out = capsys.readouterr().out
    assert "DOES NOT EQUAL" in out and "Nothing else is read" in out
    assert "1. The deciding statistic" not in out and "Reading:" not in out and "2. Each start's" not in out
    assert out.rstrip("\n").endswith("The guard failed. Nothing else is read. Stop and report.")


@pytest.mark.parametrize("change", ["missing", "twice", "another_guard", "short", "wrong_start", "unknown_role"])
def test_an_incomplete_or_misnamed_set_is_refused(pilot, tmp_path, change):
    data = {"missing": lambda: _made_up(pilot, drop=("C4", 11)),
            "twice": lambda: _made_up(pilot, extra=[{"batch": "C2", "start": 10, "role": "test", "record": [0.2] * 321}]),
            "another_guard": lambda: _made_up(pilot, extra=[{"batch": "C2", "start": 1, "role": "guard", "record": [0.2] * 321}]),
            "short": lambda: _made_up(pilot, drop=("C4", 11), extra=[{"batch": "C4", "start": 11, "role": "test", "record": [0.2] * 320}]),
            "wrong_start": lambda: _made_up(pilot, drop=("C4", 11), extra=[{"batch": "C4", "start": 14, "role": "test", "record": [0.2] * 321}]),
            "unknown_role": lambda: _made_up(pilot, extra=[{"batch": "C4", "start": 11, "role": "pilot", "record": [0.2] * 321}])}[change]()
    path = tmp_path / "records.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ST.ReadingRefusal):
        ST.load_test_searches(path)


def test_nothing_in_the_reading_script_is_collected_as_a_test():
    """pytest collects `vpd_audit_2/starts_test.py` by its name when run over the whole folder: none of its names may
    look like a test."""
    assert not [n for n in vars(ST) if n.startswith("test") or (n.startswith("Test") and isinstance(getattr(ST, n), type))]
