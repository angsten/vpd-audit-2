"""The reading logic against its known-answer cases (plan 1, Section 6).

Layer one: the decision functions on intervals typed in by hand (boundaries B1 to B16, all 27 combinations of the three
verdicts, the tie-breaks). Layer two: the row function on made-up cells (cases R1 to R17 and the added R18).

Every expected value is copied from `freeze/amendment1_specs/output_and_reading_spec.md` (Sections 3 and 5),
`freeze/amendment1.md` (fault 3.1 and Section 9), or plan 1 (Sections 5.3 and 6). None is this code's output.
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest

import lead_cases as C
from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_reading as LR

VERDICTS = ("yes", "no", "undetermined")

# The signed sentences, typed from the output specification's Section 3.7.
SIGNED = {
    "a": "The carried-over harm depends on which components the adversary chose, beyond how often they are needed",
    "b": "Mostly harm from extreme masks on components of that usage, whichever ones receive them, with a small part that depends on the choice; the exploited-components count is reported with that caveat",
    "c": "The harm comes from extreme masks on components of that usage, whichever ones receive them; the exploited-components count is dropped from the post",
    "d": "Undetermined between the first two readings; this takes precedence when a wide interval also includes zero",
    "C-LD": "The search found a choice of components whose harm carries to text in general: by the paper's own test (lines 2019 to 2022), a systematic defect",
    "C-LN": "A random permitted setting that switches off and on as many components at each level of usage also hurts unseen text; the search's particular choice is fitted to its batch",
    "C-ND": "The choice carries over, at no more harm on unseen text than the 20-step adversary does to its own batch",
    "C-NN": "The harm carries over through extreme masks on components of that usage, within the 20-step level",
    "C-X": "The search's harm is fitted to its batch: the case line 2022 describes as noise-tuned (either column)",
}
CAVEAT = "Negative ones are reported with the bias of taking a setting at its first crossing stated: downward, of unknown size."
# The amendment's sentences for the collision flags (plan 1, Section 5.3, item 1).
F1_STEP = "Collision: the signed line \"'does not carry over' when the interval of tau_n lies below 0.2\" also applies to these data."
F1_LEVEL = "Collision: \"large\" is yes and \"carries over\" is no at this harm level."
F1B = "The carry-over ratio is undetermined against 0.2."


@pytest.fixture(scope="module")
def indices() -> LI.BootstrapIndices:
    return LI.make_indices(C.K)


# ----------------------------------------------------------------------------- layer one


@pytest.mark.parametrize("name,interval,expected", [
    ("B1", (0.01, 2), "yes"), ("B2", (0, 2), "undetermined"), ("B3", (-2, 0), "no"), ("B4", (-2, 0.01), "undetermined"),
])
def test_boundaries_large(name, interval, expected):
    assert LR.verdict_large(*interval) == expected


@pytest.mark.parametrize("name,interval,expected", [
    ("B5", (0.2, 0.9), "yes"), ("B6", (0.19, 0.9), "undetermined"), ("B7", (0.05, 0.2), "undetermined"), ("B8", (0.05, 0.19), "no"),
])
def test_boundaries_carries_over(name, interval, expected):
    assert LR.verdict_ratio(*interval) == expected


@pytest.mark.parametrize("name,interval,reading,verdict", [
    ("B9", (0.2, 0.5), "a", "yes"), ("B10", (0.05, 0.19), "b", "no"), ("B11", (0.1, 0.2), "d", "undetermined"),
    ("B12", (-0.05, 0.19), "c", "no"), ("B13", (-0.05, 0.3), "d", "undetermined"), ("B14", (0, 0.1), "c", "no"),
    ("B15", (-0.3, 0), "c", "no"), ("B16", (-0.3, -0.1), "none", "no"),
])
def test_boundaries_shuffled_ratio(name, interval, reading, verdict):
    assert LR.shuffled_reading(*interval) == reading
    assert LR.verdict_ratio(*interval) == verdict


def test_the_reading_goes_with_its_verdict_on_a_grid_of_intervals():
    """Section 3.2's last column: a with yes, d with undetermined, none, b, and c with no."""
    goes_with = {"a": "yes", "d": "undetermined", "none": "no", "b": "no", "c": "no"}
    grid = [-0.5, -0.1, 0.0, 0.1, 0.19, 0.2, 0.21, 0.5]
    for L, U in itertools.combinations_with_replacement(grid, 2):
        assert LR.verdict_ratio(L, U) == goes_with[LR.shuffled_reading(L, U)], (L, U)


ROW_STATE = {  # Section 3.4, "Row state"
    ("yes", "yes"): ["Large"], ("yes", "undetermined"): ["Large"], ("yes", "no"): ["Large"],
    ("no", "yes"): ["Not large, but carries over"], ("no", "no"): ["Does not carry over"],
    ("no", "undetermined"): ["Not large, but carries over", "Does not carry over"],
    ("undetermined", "yes"): ["Large", "Not large, but carries over"],
    ("undetermined", "no"): ["Large", "Does not carry over"],
    ("undetermined", "undetermined"): ["Large", "Not large, but carries over", "Does not carry over"],
}
COLUMN = {"yes": "Depends on the choice", "no": "Does not depend on the choice", "undetermined": None}
SENTENCE = {("Large", "yes"): "C-LD", ("Large", "no"): "C-LN", ("Not large, but carries over", "yes"): "C-ND",
            ("Not large, but carries over", "no"): "C-NN"}


@pytest.mark.parametrize("large,carries,depends", list(itertools.product(VERDICTS, repeat=3)))
def test_all_27_combinations_of_the_three_verdicts(large, carries, depends):
    cell = LR.step_cell(large, carries, depends)
    rows, column = ROW_STATE[(large, carries)], COLUMN[depends]
    if len(rows) == 1 and rows[0] == "Does not carry over":
        assert cell["sentence_code"] == "C-X" and cell["printed"] == SIGNED["C-X"]  # any column, settled or not
    elif len(rows) == 1 and column is not None:
        assert cell["sentence_code"] == SENTENCE[(rows[0], depends)] and cell["printed"] == SIGNED[cell["sentence_code"]]
    elif len(rows) == 1:
        assert cell["sentence_code"] is None
        assert cell["printed"] == f"Row: {rows[0]}. Column undetermined at this search length."
    elif column is not None:
        assert cell["sentence_code"] is None
        assert cell["printed"].startswith(f"Column: {column}. Row undetermined between ") and cell["printed"].endswith(".")
        candidates = cell["printed"].split("Row undetermined between ")[1]
        for name in ROW_STATE[("undetermined", "undetermined")]:
            assert (f'"{name}"' in candidates) == (name in rows)
    else:
        assert cell["sentence_code"] is None and cell["printed"] == "Undetermined at this search length."
    if len(rows) == 1:
        assert cell["row_state"] == rows[0] and cell["row_settled"]
    else:
        assert cell["row_state"].startswith("Unsettled between") and not cell["row_settled"]
    # F1 exactly for (yes, no, any), F1b exactly for (yes, undetermined, any)
    flags = LR.collision_flags("step", large, carries)
    assert ("F1" in flags) == (large == "yes" and carries == "no")
    assert ("F1b" in flags) == (large == "yes" and carries == "undetermined")


def test_collision_flags_print_the_amendments_sentences():
    assert LR.collision_flags("step", "yes", "no") == {"F1": F1_STEP}
    assert LR.collision_flags("level", "yes", "no") == {"F1": F1_LEVEL}
    assert LR.collision_flags("step", "yes", "undetermined") == {"F1b": F1B}
    assert LR.collision_flags("level", "yes", "undetermined") == {"F1b": F1B}
    every_text = " ".join(str(v) for v in LR.FLAG_TEXTS.values())
    assert "large, with low retention" not in every_text and "large; carry-over ratio undetermined" not in every_text


def test_signed_sentences_are_verbatim():
    assert LR.SENTENCES == SIGNED
    assert LR.SIGNED_CAVEAT == CAVEAT
    assert LR.STEP_FOOTER == "A straddling 40- or 80-step cell stays Undetermined, and nothing outside the step table resolves it."
    assert LR.LEVEL_FOOTERS == ("Only positive verdicts are confirmatory.", "The harm-level table is printed in full and never resolves a step-table cell.")
    assert LR.DELTA_ON_CAUTION == ("The delta-on searches follow different paths from the lead's, so a share differs from 1 by chance. "
                                   "Compare it with the range on line 7 before reading it as the delta components' contribution.")


# ----------------------------------------------------------------------------- tie-breaks


def test_tie_break_percentile_interval_gives_a_different_verdict(indices):
    """The carry-over ratio depends on the start alone: the deciding interval, with its start part, straddles 0.2,
    while the percentile interval, which resamples batches only, lies above it. The deciding one is printed."""
    ratio_by_start = np.array([0.15, 0.20, 0.25, 0.30, 0.35])
    carried = 0.21 + 10.0 * ratio_by_start[None, None, :]
    rec = LR.row_record(C.arrays_for(101, "step", 320, own=10.21, carried=carried, shuffled=0.43), indices=indices)
    assert rec["carries"]["verdict"] == "undetermined"
    assert LR.verdict_ratio(*rec["carries"]["interval_percentile"]) == "yes"
    assert "F7" in rec["flags"]
    assert rec["flag_texts"]["F7"].startswith("percentile interval gives a different verdict for: ")
    assert "carries over" in rec["flag_texts"]["F7"] and rec["flag_texts"]["F7"].endswith("; the signed interval decides")


def test_tie_break_unwidened_interval_gives_a_different_verdict(indices):
    """A multiplier above 1: the verdict is read from the widened interval, and F11 names what the unwidened one says."""
    arrays = C.arrays_for(102, "step", 320, own=25.0, carried=0.21 + 0.25 * 24.79, shuffled=0.43, pattern=8.0)
    plain = LR.row_record(arrays, indices=indices)
    wide = LR.row_record(arrays, indices=indices, multiplier=1.5)
    assert plain["carries"]["verdict"] == "yes" and "F11" not in plain["flags"]
    assert wide["carries"]["verdict"] == "undetermined"
    assert wide["carries"]["interval_unwidened"] == plain["carries"]["interval"]
    assert wide["flag_texts"]["F11"].startswith("interval widened by 1.50 under the pre-run amendment; unwidened interval gives a different verdict for: ")
    assert "carries over" in wide["flag_texts"]["F11"]
    # every statistic's deciding interval takes the multiplier; z_D alone uses the unwidened standard error
    for name in ("large", "carries", "depends", "carried_margin", "own_margin", "kappa", "shuffled_vs_yardstick", "carried_added"):
        w, p = wide[name], plain[name]
        assert w["interval"][1] - w["interval"][0] == pytest.approx(1.5 * (p["interval"][1] - p["interval"][0]), rel=1e-9), name
    pooled_w, pooled_p = wide["retention"]["pooled"], plain["retention"]["pooled"]
    assert pooled_w["interval"][1] - pooled_w["interval"][0] == pytest.approx(1.5 * (pooled_p["interval"][1] - pooled_p["interval"][0]), rel=1e-9)
    assert wide["own_margin"]["z"] == plain["own_margin"]["z"]
    # a multiplier that changes no verdict prints the first half alone
    calm = LR.row_record(C.case("R1")["arrays"], indices=indices, multiplier=1.15)
    assert calm["flag_texts"]["F11"] == "interval widened by 1.15 under the pre-run amendment"


def test_tie_break_recomputed_row_gives_a_different_verdict(indices):
    main = LR.row_record(C.case("R1")["arrays"], indices=indices)
    recomputed = LR.row_record(C.case("R2")["arrays"], indices=indices)
    before = dict(main["verdicts"])
    LR.mark_recomputed(main, recomputed)
    assert main["verdicts"] == before  # the main reading decides
    assert main["flags"] == ["F9"]
    assert main["flag_texts"]["F9"] == ("recomputation without the 11 overlapping texts gives a different verdict for: "
                                        "carries over, depends on the choice; the main reading decides")
    same = LR.row_record(C.case("R1")["arrays"], indices=indices)
    LR.mark_recomputed(same, LR.row_record(C.case("R1")["arrays"], indices=indices))
    assert same["flags"] == []


# ----------------------------------------------------------------------------- layer two


def _close(got: float, expected: float, tolerance: float | None = None) -> bool:
    """Estimates must match within 0.02, or within 1 percent if larger, unless a case states otherwise."""
    tol = tolerance if tolerance is not None else max(0.02, 0.01 * abs(expected))
    return abs(got - expected) <= tol


# case: (large verdict, estimate), (carries verdict, estimate[, tolerance]), (depends verdict, estimate, reading[, tolerance]),
#       cell (a sentence code, a printed line, a 20-step word, or None for "none printed"), flags
ROW_CASES = {
    "R1": (("yes", 22.22), ("yes", 0.90), ("yes", 0.90, "a"), "C-LD", []),
    "R2": (("yes", 2.22), ("no", 0.11), ("no", 0.10, "b"), "C-LN", ["F1"]),
    "R3": (None, ("yes", 0.86), ("yes", 0.50, "a"), "Carries over", []),
    "R4": (None, ("yes", 0.93), ("no", -1.0, "none", 0.05), "Carries over", ["F2", "F5"]),
    "R5": (None, ("yes", 0.93), ("undetermined", -1.0, "d", 0.05), "Carries over", ["F3", "F5"]),
    "R6": (("no", -0.08), ("yes", 0.83), ("yes", 1.50, "a"), "C-ND", ["F4", "F5"]),
    "R7": (("no", -0.53), ("no", 0.07), ("no", -0.38, "none"), "C-X", ["F2", "F5"]),
    "R8": (("yes", 4.39), ("undetermined", 0.200), ("undetermined", 0.19, "d"), "Row: Large. Column undetermined at this search length.", ["F1b"]),
    "R9": (("no", -0.18), ("yes", 0.66), ("no", 0.09, "b"), "C-NN", []),
    "R10": (("no", None), ("yes", 0.66), ("no", 0.0, "c"), "C-NN", []),
    "R11": (None, ("yes", 0.78), ("yes", 0.43, "a"), "Carries over", []),
    "R12": (("yes", 5.50), ("yes", 0.60), ("yes", 0.59, "a"), "C-LD", []),
    "R13": (("yes", None), ("yes", 0.608, 0.005), ("yes", 0.60, "a"), "C-LD", []),
    "R14": (("yes", None), ("yes", 0.90), ("yes", 0.90, "a"), None, []),
    "R15a": (("yes", None), ("yes", 0.78), ("yes", 0.78, "a"), None, []),
    "R15b": (("undetermined", None), ("undetermined", None), ("undetermined", None, "not read"), None, ["F10"]),
    "R15c": (("undetermined", None), ("undetermined", None), ("undetermined", None, "not read"), None, ["F10"]),
    "R16": (("yes", None), ("yes", 0.675), ("yes", 0.67, "a"), "C-LD", []),
    "R17": (("yes", None), ("yes", 0.90), ("yes", 0.90, "a"), "C-LD", ["F8"]),
    "R18": (("yes", 0.72), ("no", 0.12), ("no", 0.10, "b"), None, ["F1"]),
}
KAPPA = {"R1": (0.99, None), "R2": (0.90, None), "R3": (0.16, None), "R6": (-0.61, None), "R7": (-3.75, 0.1), "R9": (0.05, None),
         "R11": (0.22, None), "R12": (0.97, None)}
D3 = {"R1": "do not exceed", "R2": "do not exceed", "R6": "exceed"}


@pytest.fixture(scope="module")
def records(indices) -> dict[str, dict]:
    out = {}
    for name in ROW_CASES:
        c = C.case(name)
        out[name] = LR.row_record(c["arrays"], indices=indices, before=c.get("before"))
    return out


@pytest.mark.parametrize("name", list(ROW_CASES))
def test_row_case(name, records):
    large, carries, depends, cell, flags = ROW_CASES[name]
    rec = records[name]
    if large is None:
        assert rec["large"]["verdict"] == "not asked" and rec["large"]["printed"] == "not asked at 20 steps"
    else:
        assert rec["large"]["verdict"] == large[0]
        if large[1] is not None:
            assert _close(rec["large"]["estimate"], large[1]), rec["large"]["estimate"]
    assert rec["carries"]["verdict"] == carries[0]
    if carries[1] is not None:
        assert _close(rec["carries"]["estimate"], carries[1], carries[2] if len(carries) > 2 else None), rec["carries"]["estimate"]
    assert rec["depends"]["verdict"] == depends[0]
    assert rec["depends"]["reading"] == depends[2]
    if depends[1] is not None:
        assert _close(rec["depends"]["estimate"], depends[1], depends[3] if len(depends) > 3 else None), rec["depends"]["estimate"]
    if cell is None:
        assert rec["cell"] is None  # none printed: a harm-level row
    elif cell in SIGNED:
        assert rec["cell"]["sentence_code"] == cell and rec["cell"]["printed"] == SIGNED[cell]
    elif cell in ("Carries over", "Batch-specific", "Undetermined"):
        assert rec["cell"] is None and rec["carries"]["word"] == cell  # the 20-step row: the signed word, no cell
    else:
        assert rec["cell"]["sentence_code"] is None and rec["cell"]["printed"] == cell  # no sentence printed
    assert rec["flags"] == flags
    if depends[2] in SIGNED:
        assert rec["depends"]["sentence"] == SIGNED[depends[2]]
    if name in KAPPA:
        assert rec["kappa"]["defined"] and _close(rec["kappa"]["estimate"], *KAPPA[name]), rec["kappa"]["estimate"]
    if name in D3:
        assert rec["shuffled_vs_yardstick"]["relation"] == D3[name]


def test_also_check_r4_r5_own_margin(records):
    r4, r5 = records["R4"]["own_margin"], records["R5"]["own_margin"]
    assert _close(r4["estimate"], 0.02) and r4["interval"][0] > 0  # +0.02, interval above zero
    assert r5["interval"][0] <= 0 < r5["interval"][1] and abs(r5["z"]) < 1  # includes zero; |z_D| < 1
    assert records["R4"]["depends"]["sentence"] == "no reading defined"


def test_also_check_r10_zero_variance_gives_no_0_over_0(records):
    dep = records["R10"]["depends"]
    assert dep["estimate"] == 0.0 and dep["interval"] == [0.0, 0.0]  # exactly 0, interval [0, 0]
    assert dep["zero_variance"] is True and dep["nu"] == C.K - 1
    assert "zero_variance" not in records["R10"]["flags"]  # a field of the interval, not one of the row's flags
    assert records["R10"]["carried_margin"]["interval"] == [0.0, 0.0]
    assert "Flags: none" in "\n".join(LR._row_lines(records["R10"]))


def test_also_check_r11_all_intervals_of_zero_width(records):
    rec = records["R11"]
    assert rec["means_raw"]["start"] == pytest.approx(0.24, abs=1e-12)
    blocks = [rec[n] for n in ("carries", "depends", "carried_margin", "own_margin", "kappa", "carried_added")] + [rec["retention"]["pooled"]]
    for blk in blocks:
        for field in ("interval", "interval_unwidened", "interval_percentile"):
            assert blk[field][0] == blk[field][1] == blk["estimate"]
        assert blk["zero_variance"] is True


def test_also_check_r12_harms_that_depend_on_the_start(records):
    rec = records["R12"]
    assert rec["means_raw"]["start"] == pytest.approx(3.0, abs=0.01)  # start = s, s from 1 to 5
    assert rec["means_raw"]["own20"] == pytest.approx(3.5, abs=0.01)


def test_also_check_r13_a_mean_of_ratios_would_give_about_8(records):
    arrays = C.case("R13")["arrays"]
    mean_of_ratios = float(np.mean((arrays["carried"] - arrays["start"][None]) / (arrays["own"] - arrays["start"])[None]))
    assert 6 < mean_of_ratios < 10 and _close(records["R13"]["carries"]["estimate"], 0.608, 0.005)


def test_also_check_r14_a_search_that_jumps_past_the_level(records):
    rec = records["R14"]
    assert rec["large"]["tag"] == rec["carries"]["tag"] == rec["depends"]["tag"] == "confirmatory"
    for side in ("attack", "heldout"):
        assert _close(rec["level"][side]["own_harm_median"], 40.0)  # line 2: median own harm 40.0 per side
    assert not _close(rec["carries"]["estimate"], 20.0)  # using the level as denominator would give 20
    assert "(confirmatory)" in "\n".join(LR._row_lines(rec))


def test_also_check_r15_ten_against_eleven_missing(records):
    a, b, c = records["R15a"], records["R15b"], records["R15c"]
    assert a["level"]["attack"]["missing"] == 10 and a["level"]["attack"]["missing_by_batch"] == {"A1": 5, "A2": 5}
    assert a["level"]["undetermined"] is False and a["level"]["subtable"] == {"attack_batches": 14, "heldout_batches": 16, "starts": 5}
    assert a["level"]["wording"] == LR.MISSING_WORDING
    assert b["level"]["attack"]["missing"] == 11 and b["level"]["attack"]["missing_by_batch"] == {"A1": 5, "A2": 5, "A3": 1}
    assert c["level"]["heldout"]["missing"] == 11 and c["level"]["attack"]["missing"] == 0
    for rec in (b, c):
        assert rec["level"]["undetermined"] is True
        assert rec["depends"]["sentence"] == "not read: level Undetermined"
        # the numbers are still printed, computed from the available cells
        assert _close(rec["carries"]["estimate"], 0.78) and rec["carries"]["interval"] is not None
    assert b["flag_texts"]["F10"] == "level Undetermined: 11 of 80 attack searches and 0 of 80 held-out searches missing; allowance 10 per side"
    assert c["flag_texts"]["F10"] == "level Undetermined: 0 of 80 attack searches and 11 of 80 held-out searches missing; allowance 10 per side"


def test_also_check_r16_retention_split(records):
    rec = records["R16"]
    groups = rec["retention"]["groups"]
    assert groups["past_5_nats"]["settings"] == 16 and groups["not_past_5_nats"]["settings"] == 64
    assert _close(groups["past_5_nats"]["pooled"], 0.90) and _close(groups["past_5_nats"]["median"], 0.90)
    assert _close(groups["not_past_5_nats"]["pooled"], 0.30) and _close(groups["not_past_5_nats"]["median"], 0.30)
    assert _close(rec["retention"]["pooled"]["estimate"], 0.675, 0.005)
    assert rec["past_levels"]["attack"]["5"] == pytest.approx(0.20) and rec["past_levels"]["heldout"]["5"] == pytest.approx(0.20)


def test_also_check_r17_step_319_disagrees(records):
    rec = records["R17"]
    sub = rec["step_before"]
    assert sub["label"] == "step n - 1: description; step n decides"
    assert sub["large"]["verdict"] == "yes" and sub["carries"]["verdict"] == "no"
    assert rec["carries"]["verdict"] == "yes"  # step n decides
    assert rec["flag_texts"]["F8"] == "step n - 1 gives a different verdict for: carries over; step n decides"
    assert "depends" not in sub  # those settings have no shuffled copies
    assert records["R1"]["step_before"] is None


def test_overridden_flag_texts_in_rows(records):
    assert records["R2"]["flag_texts"] == {"F1": F1_STEP}
    assert records["R18"]["flag_texts"] == {"F1": F1_LEVEL}
    assert records["R8"]["flag_texts"] == {"F1b": F1B}
    assert records["R18"]["carries"]["caveat"] == CAVEAT and records["R18"]["depends"]["caveat"] == CAVEAT
    assert records["R18"]["large"]["tag"] == "confirmatory"
    text = "\n".join("\n".join(LR._row_lines(rec)) for rec in records.values())
    assert "large, with low retention" not in text and "large; carry-over ratio undetermined" not in text
    assert F1_STEP in text and F1_LEVEL in text and F1B in text and CAVEAT in text


# ----------------------------------------------------------------------------- the printed row


def _prefixes(lines: list[str]) -> list[str]:
    return [ln[:3].strip() for ln in lines[1:] if ln[:3].strip()]


def test_printed_step_row_has_its_lines_in_order(records):
    lines = LR._row_lines(records["R1"])
    assert lines[0] == "STEP TABLE: 320 steps"
    assert _prefixes(lines) == ["1", "2", "2b", "3", "4", "5", "6a", "6b", "6c", "6d", "7", "8", "9", "9b", "10", "11", "12"]
    text = "\n".join(lines)
    assert f'"{SIGNED["a"]}"' in text and f'"{SIGNED["C-LD"]}"' in text
    assert "Step-table cell: Large x Depends on the choice" in text
    k = next(n for n, ln in enumerate(lines) if "settings           pooled" in ln)
    assert lines[k + 1].strip() == "Description: resolves no cell."  # always after the pooled retention's interval
    assert "[" in lines[k] and "]" in lines[k]
    assert _prefixes(LR._row_lines(records["R17"]))[-1] == "13"


def test_printed_20_step_row(records):
    lines = LR._row_lines(records["R3"])
    assert lines[0] == "STEP TABLE: 20 steps"
    assert _prefixes(lines) == ["1", "2", "2b", "3", "4", "5", "6a", "6b", "6c", "8", "9", "9b", "10", "11", "12"]  # no 6d, no cell
    text = "\n".join(lines)
    assert " 3  Large: not asked at 20 steps" in text and "yes (Carries over)" in text
    assert "yardstick" not in next(ln for ln in lines if ln.lstrip().startswith("start "))  # omitted at 20 steps


def test_printed_harm_level_row(records):
    lines = LR._row_lines(records["R15a"])
    assert lines[0] == "HARM-LEVEL TABLE: settings taken where each search's own harm first reaches 10 nats"
    assert _prefixes(lines) == ["1", "2", "2b", "3", "4", "5", "6a", "6b", "6c", "6d", "8", "9", "9b", "11", "12"]  # no cell, no line 10
    text = "\n".join(lines)
    assert "Missing attack searches: 10 of 80 (allowance 10); batches: A1 (5), A2 (5)" in text
    assert "Missing held-out searches: 0 of 80 (allowance 10); batches: none" in text
    assert "14 attack x 16 held-out batches x 5 starts" in text and LR.MISSING_WORDING in text
    assert "settings that reached the level" in text and "own harm past 5 nats" not in text  # not split
    assert "Own harm of the scored settings: attack median" in text
    undetermined = "\n".join(LR._row_lines(records["R15b"]))
    assert "not read: level Undetermined" in undetermined and undetermined.count("    undetermined") == 3


def test_f6_withholds_the_composition_share(indices):
    """Carried-over added harm not distinguishable from zero: D1 and kappa are replaced by F6's text."""
    arrays = C.arrays_for(103, "step", 40, own=0.80, carried=0.21, shuffled=0.40)
    rec = LR.row_record(arrays, indices=indices)
    assert "F6" in rec["flags"] and rec["kappa"]["defined"] is False
    line = next(ln for ln in LR._row_lines(rec) if ln.startswith(" 6c"))
    assert line == " 6c carried-over added harm is not distinguishable from zero; composition share not defined"


def test_heldout_batch_means_when_one_batch_takes_twice_the_carried_harm_of_the_rest(indices):
    """Amendment 2, Section 7, on a made-up table with a known answer: 15 held-out batches take 3 nats of carried-over
    added harm and one takes 6. Their mean is 51/16, so the 15 stand at 16/17 of it and the one at 32/17."""
    added = np.where(np.arange(C.K) == 5, 6.0, 3.0)  # held-out batch H6 takes twice the carried harm of the rest
    carried = 0.21 + np.broadcast_to(added[None, :, None], (C.K, C.K, C.NS))
    for table, key in (("step", 80), ("level", 5.0)):
        arrays = C.arrays_for(104, table, key, own=9.5, carried=carried, shuffled=0.40, noise=0.0)
        rec = LR.row_record(arrays, indices=indices)
        hb = rec["heldout_batch_means"]
        assert hb["mean_of_batch_means"] == pytest.approx(51 / 16, abs=1e-12)
        assert [b["relative"] for b in hb["sorted"]] == pytest.approx([16 / 17] * 15 + [32 / 17], abs=1e-12)  # sorted, relative to their mean
        assert hb["sorted"][-1] == {"batch": "H6", "relative": pytest.approx(32 / 17), "mean": pytest.approx(6.0)}
        assert sorted(b["batch"] for b in hb["sorted"]) == sorted(arrays["heldout_names"])
        lines = LR._row_lines(rec)
        k = next(n for n, ln in enumerate(lines) if ln.startswith(" 9b"))
        assert lines[k - 1].strip() == "Description: resolves no cell."  # printed after line 9
        assert lines[k + 1].strip().endswith("H6 1.88") and lines[k + 1].count("0.94") == 15
        assert lines[k + 2].strip() == "Description, with no line: whether a batch sits far above the rest is a judgement."
    # it never changes an interval of record or a verdict word
    plain = LR.row_record(C.case("R1")["arrays"], indices=indices)
    assert plain["verdicts"] == {"large": "yes", "carries": "yes", "depends": "yes"} and plain["flags"] == []
    assert [b["relative"] for b in plain["heldout_batch_means"]["sorted"]] == sorted(b["relative"] for b in plain["heldout_batch_means"]["sorted"])
    assert max(abs(b["relative"] - 1) for b in plain["heldout_batch_means"]["sorted"]) < 0.01
    # with searches missing at a level, the means run over the carried settings that exist
    missing = LR.row_record(C.case("R15a")["arrays"], indices=indices)["heldout_batch_means"]
    assert len(missing["sorted"]) == 16 and missing["mean_of_batch_means"] == pytest.approx(8.48 - 0.21, abs=0.02)


def test_eight_equal_shuffled_harms_average_to_exactly_that_harm():
    rng = np.random.default_rng(5)
    x = rng.random((16, 16, 5)) * 37.0
    assert np.array_equal(LR.shuffled_mean(np.repeat(x[..., None], 8, axis=-1)), x)


# ----------------------------------------------------------------------------- the delta-on summary and the scatter


def test_delta_on_block_is_description_with_no_verdict_word(indices):
    lead = C.arrays_for(201, "step", 80, own=9.5, carried=7.6, shuffled=0.40)
    delta = C.arrays_for(202, "step", 80, own=7.5, carried=4.0, shuffled=0.30, start=0.25)
    null = {s: {v: [0.8, 1.0, 1.25] for v in ("a", "b")} for s in ("carried_share", "own_share")}
    block = LR.delta_on_block(lead, delta, indices=indices, null_range=null)
    assert block["carried_share"]["estimate"] == pytest.approx((4.0 - 0.25) / (7.6 - 0.21), abs=0.01)
    assert block["own_share"]["estimate"] == pytest.approx((7.5 - 0.25) / (9.5 - 0.21), abs=0.01)
    assert block["delta_on"]["means_raw"]["start"] == pytest.approx(0.25, abs=0.001)
    assert block["delta_on"]["carries"]["estimate"] == pytest.approx(3.75 / 7.25, abs=0.01)

    def keys(x):
        if isinstance(x, dict):
            for k, v in x.items():
                yield k
                yield from keys(v)
    assert "verdict" not in set(keys(block))
    lines = LR._delta_lines(block)
    assert [ln[:3].strip() for ln in lines[1:] if ln[:3].strip()] == ["1", "2", "3", "4", "5", "6", "7", "8"]
    assert lines[-1].endswith(LR.DELTA_ON_CAUTION)
    text = "\n".join(lines)
    assert "carried-over share: same searches, fresh cell noise 0.80 to 1.25; every search redrawn 0.80 to 1.25" in text
    assert "own-search share: same searches" in text
    for word in ("yes", "undetermined", "Carries over", "Batch-specific"):
        assert word not in text


def test_matched_arrays_pick_the_shared_cells_by_name():
    lead = C.arrays_for(203, "step", 80, own=9.5, carried=7.6, shuffled=0.40)
    delta = {"attack_names": ["A3", "A1"], "heldout_names": ["H2", "H5", "H1"], "starts": [13, 9]}
    m = LR.matched_arrays(lead, delta)
    assert m["carried"].shape == (2, 3, 2) and m["shuffled"].shape == (2, 3, 2, 8)
    assert m["carried"][0, 1, 0] == lead["carried"][2, 4, 4] and m["carried"][1, 2, 1] == lead["carried"][0, 0, 0]
    assert m["own"][1, 0] == lead["own"][4, 4] and m["attack_own"][0, 1] == lead["attack_own"][2, 0]


def test_scatter_points_one_per_scored_setting(records):
    arrays = C.case("R15a")["arrays"]
    pts = LR.scatter_points(arrays)
    assert len(pts) == 70 and {p["attack_batch"] for p in pts} == {f"A{i}" for i in range(3, 17)}
    p = pts[0]
    i, s = arrays["attack_names"].index(p["attack_batch"]), arrays["starts"].index(p["start"])
    assert p["carried_added"] == pytest.approx(float((arrays["carried"][i, :, s] - arrays["start"][:, s]).mean()))
    assert p["own_added"] == pytest.approx(float(arrays["attack_own"][i, s] - arrays["attack_start"][i, s]))
