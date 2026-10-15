"""Session 7, plans 4 and 7: the post's Figure 3. The toy's net pushes, both drawings, the dose-response values against
the checkpoint, row (d)'s bars on their own scale, and (plan 7) row (d)'s measured arrows and numbers held to probe 1's
record."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from vpd_audit_2 import post_interference as P


def test_the_net_pushes_are_0_4_0_for_rows_a_b_c():
    assert [P.row_net_push(r) for r in ("a", "b", "c")] == [0, 4, 0]
    # the table itself, typed from the plan: pushes on inputs 1 and 2 and the adversary's switches
    assert P.PUSHES["input 1"] == [+1, -1, +1, -1, -1, +1, +1, -1]
    assert P.PUSHES["input 2"] == [-1, +1, +1, -1, +1, +1, -1, -1]
    assert P.SWITCHES == [1, 0, 1, 0, 0, 1, 1, 0]
    assert P.net_push(P.PUSHES["input 2"], P.ALL_ON) == 0  # input 2 with everything on cancels too


@pytest.mark.parametrize("variant", ["a", "b"])
def test_each_drawing_writes_a_png(tmp_path, variant):
    path = P.draw_interference(tmp_path / P.OUT_NAMES[variant], variant)
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_the_dose_response_values_equal_the_checkpoints():
    # sessions/006/checkpoint.md, Section 6.3, the 320-step row of "Share of the harm kept, by fraction of the off set switched off"
    assert P.CHECKPOINT_DOSE_320 == (0.00, 0.01, 0.04, 0.42, 1.02)
    values = P.dose_response_320()
    assert tuple(round(v, 2) for v in values) == (0.00, 0.01, 0.04, 0.42, 1.02)
    assert P.DOSE_FRACTIONS == (0.25, 0.5, 0.75, 0.9, 1.0)
    # plotted as recorded, none renormalized: the whole rounded set at its 1.0215, so every number matches the checkpoint
    assert P.dose_points(values) == values
    assert P.PANEL_Y.replace("\n", " ") == "share of the setting's damage"


def _drawn_bar_widths() -> list[float]:
    """The widths, in data units, of the bars row (d) draws."""
    from matplotlib.patches import Rectangle

    plt = P._plt()
    fig, ax = plt.subplots()
    P._bars(ax, 0.0)
    widths = [p.get_width() for p in ax.patches if isinstance(p, Rectangle)]
    plt.close(fig)
    return widths


def test_row_d_bars_are_1_and_0_9_whatever_the_toy(monkeypatch):
    assert P.measured_bar_lengths() == (1.0, 0.9)
    before = _drawn_bar_widths()
    assert before == pytest.approx([1.0 * P.BAR_SCALE, 0.9 * P.BAR_SCALE])
    # change the toy so row (b)'s net push is no longer 4: neither the lengths nor the drawn bars move
    monkeypatch.setitem(P.PUSHES, "input 1", [-1] * 8)
    assert P.row_net_push("b") == -4
    assert P.measured_bar_lengths() == (1.0, 0.9)
    assert _drawn_bar_widths() == before


# ----------------------------------------------------------------------------- plan 7: row (d) from probe 1's record


def _record() -> dict:
    return json.loads(P.PROBE_RECORD.read_text())


def _row_d_arrows(probe_record: Path = P.PROBE_RECORD) -> tuple[list[int], list[bool]]:
    """Row (d) as drawn: each cell's arrow direction (+1 right, -1 left), left to right, and whether its cell is on."""
    from matplotlib.patches import FancyArrowPatch, Rectangle

    plt = P._plt()
    fig, ax = plt.subplots()
    P._draw_rows(ax, probe_record)
    y0, y1 = P.ROW_TOP["d"] - P.RH, P.ROW_TOP["d"]
    arrows = []
    for p in ax.patches:
        if isinstance(p, FancyArrowPatch):
            (xa, ya), (xb, yb) = p._posA_posB
            if y0 < ya < y1 and xa < 8 * P.CW3:
                arrows.append((xa, int(np.sign(xb - xa))))
    cells = sorted((p.get_x(), p.get_facecolor()) for p in ax.patches if isinstance(p, Rectangle) and p.get_y() == y0 and p.get_x() < 8 * P.CW3)
    from matplotlib.colors import to_rgba

    on = [fc == to_rgba(P.OWN) for _, fc in cells]
    plt.close(fig)
    return [s for _, s in sorted(arrows)], on


def test_row_d_draws_the_records_signs_flipped():
    comps = _record()["row_d"]["components"]
    flipped = {f"{c['module']} {c['component']}": -int(np.sign(c["switch_off_push_on_text"])) for c in comps}
    assert all(c["drawn_arrow_on_text"] == flipped[f"{c['module']} {c['component']}"] for c in comps)  # the record's own convention
    cells = P.row_d_cells(P.row_d_components())
    assert [c["drawn_sign"] for c in cells] == [flipped[c["name"]] for c in cells]
    drawn, on = _row_d_arrows()
    assert drawn == [c["drawn_sign"] for c in cells] and len(drawn) == 8
    assert on == [bool(s) for s in P.SWITCHES] == [c["cell"] == "on" for c in cells]  # the kept components in the on cells, as row (b)'s switches
    assert sorted(c["name"] for c in cells) == sorted(flipped)


def test_row_d_follows_the_record_not_a_typed_table(tmp_path):
    rec = _record()
    for c in rec["row_d"]["components"]:  # every measured push reversed
        c["switch_off_push_on_text"] = -c["switch_off_push_on_text"]
        c["drawn_arrow_on_text"] = -c["drawn_arrow_on_text"]
    path = tmp_path / "record.json"
    path.write_text(json.dumps(rec))
    assert _row_d_arrows(path)[0] == [-s for s in _row_d_arrows()[0]]
    rec["row_d"]["components"][0]["drawn_arrow_on_text"] *= -1  # a record whose drawn sign is not the flip is refused
    path.write_text(json.dumps(rec))
    with pytest.raises(ValueError):
        P.row_d_components(path)


def test_the_three_numbers_are_the_records_rounded():
    r = _record()["rows"]["n320"]
    n = P.row_d_numbers()
    assert n["raw_pct"] == round(100 * r["g_bar"]) == 74 and n["perm_pct"] == round(100 * r["post_hoc_permutation_baseline"]["g0_bar"]) == 55
    assert n["kept_pct"] == round(100 * r["g0_bar"]) == 74 and round(4 * r["additivity"]["off_set"]) / 4 == 0.25
    assert P.row_d_lines(n) == ("74% keep their direction from the searched batch (chance about 55%)", "components left on: also 74%",
                                "their first-order sum: about a quarter of the shift")
    plt = P._plt()
    fig, ax = plt.subplots()
    P._draw_rows(ax)
    drawn = " ".join(t.get_text().replace("\n", " ") for t in ax.texts)
    plt.close(fig)
    for line in P.row_d_lines(n):
        assert line in drawn
    assert P.D_NOTE == "first-order pushes, measured on one unseen text" and P.D_NOTE_DRAWN.replace("\n", " ") == P.D_NOTE
    assert P.D_NOTE in drawn and "pushes inside not measured" not in drawn and "?" not in [t.strip() for t in drawn.split()]


def test_the_words_plan_7_sets():
    assert P.LEGEND_A[-1] == ("measured", "a component's first-order push, measured,\ndrawn as the push while on")
    assert P.FOOTER.endswith("Measured on the released decomposition (d): the same pattern damages text it never saw nearly as much, and its "
                             "components' pushes mostly keep their direction there.")
    assert P.footer_text().count("\n") + 1 == P.FOOTER_LINES == 3
    note = P.row_d_note()
    assert "WHILE ON" in note and "negative of the measured effect of switching it off" in note
    assert all(c["name"] in note for c in P.row_d_components())


@pytest.mark.parametrize("name", list(P.OUT_NAMES.values()))
def test_the_committed_pngs_and_their_75_percent_copies_exist(name):
    from PIL import Image

    from vpd_audit_2.post_small import small_path

    full, small = P.OUT_DIR / name, small_path(P.OUT_DIR / name)
    assert full.is_file() and small.is_file()
    w, h = Image.open(full).size
    assert Image.open(small).size == (round(0.75 * w), round(0.75 * h))
    assert (P.OUT_DIR / P.ROW_D_NOTE_NAME).read_text() == P.row_d_note()
