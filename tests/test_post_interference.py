"""Plans 4 and 7 of the research log: the post's Figure 3. The toy's net pushes, the drawing and its 50 percent copy, the
schematic rows (d) and (e) (row (b)'s arrows, and the same with c4 flipped), their net arrows held to the lead record's
kept share, their readings, the section label, and the committed PNG and its copy with no caption-note file."""

from __future__ import annotations

import json

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


def test_the_drawing_writes_a_png_and_its_50_percent_copy_only(tmp_path):
    path = P.draw_interference(tmp_path / P.OUT_NAME)
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == [P.OUT_NAME, P.OUT_NAME.replace(".png", "_50.png")]


# ----------------------------------------------------------------------------- the schematic rows (d) and (e)


def _drawn():
    plt = P._plt()
    fig, ax = plt.subplots()
    P._draw_rows(ax)
    patches, texts = list(ax.patches), list(ax.texts)
    plt.close(fig)
    return patches, texts


def _row(row: str) -> tuple[list[int], list[tuple]]:
    """A row as drawn: each cell's arrow direction (+1 right, -1 left), left to right, and each cell's (face, arrow colour)."""
    from matplotlib.colors import to_rgba
    from matplotlib.patches import FancyArrowPatch, Rectangle

    patches, _ = _drawn()
    y0, y1 = P.ROW_TOP[row] - P.RH, P.ROW_TOP[row]
    arrows = []
    for p in patches:
        if isinstance(p, FancyArrowPatch):
            (xa, ya), (xb, yb) = p._posA_posB
            if ya == yb and y0 < ya < y1 and xa < 8 * P.CW3:  # a cell's arrow is horizontal, inside the cells
                arrows.append((min(xa, xb), int(np.sign(xb - xa)), to_rgba(p.get_edgecolor())))
    cells = sorted((p.get_x(), to_rgba(p.get_facecolor())) for p in patches if isinstance(p, Rectangle) and p.get_y() == y0 and p.get_x() < 8 * P.CW3)
    arrows.sort()
    assert len(arrows) == 8 and len(cells) == 8
    return [s for _, s, _ in arrows], [(face, colour) for (_, face), (_, _, colour) in zip(cells, arrows)]


def test_row_d_draws_row_b_and_row_e_differs_from_it_in_c4_only():
    from matplotlib.colors import to_rgba

    signs_b, look_b = _row("b")
    signs_d, look_d = _row("d")
    signs_e, look_e = _row("e")
    assert signs_d == signs_b == P.PUSHES["input 1"] and look_d == look_b  # row (d) is row (b), cell for cell
    differs = [j for j in range(8) if signs_e[j] != signs_d[j]]
    assert differs == [3] and signs_e[3] == +1 and signs_d[3] == -1  # c4 flips, from left to right
    assert [j for j in range(8) if look_e[j] != look_d[j]] == [3]
    assert look_e[3] == (to_rgba(P.FLIP_FACE), to_rgba(P.FLIP_ARROW))  # the flipped cell's tint and arrow
    assert P.SWITCHES[3] == 0  # c4 is one of the switched-off components


def test_the_curved_arrows_join_c4_in_rows_d_and_e():
    from matplotlib.patches import FancyArrowPatch

    patches, _ = _drawn()
    vertical = sorted(p._posA_posB for p in patches if isinstance(p, FancyArrowPatch) and p._posA_posB[0][0] == p._posA_posB[1][0])
    y_top, y_bot = P.ROW_TOP["d"] - P.RH / 2 - 0.2, P.ROW_TOP["e"] - P.RH / 2 + 0.2
    xl, xr = 3 * P.CW3 + 0.25, 4 * P.CW3 - 0.25
    assert vertical == sorted([[(xl, y_top), (xl, y_bot)], [(xr, y_bot), (xr, y_top)]])  # down at the left, up at the right


def test_the_net_arrows_take_the_kept_share_and_the_readings_and_section_label_are_drawn():
    # the kept share: the lead record's 320-step retention pooled over all 80 settings, drawn at the table's two places
    steps = json.loads(P.LEAD_RECORD.read_text())["main"]["step"]
    estimate = [s for s in steps if s["key"] == 320][0]["retention"]["pooled"]["estimate"]
    assert P.kept_share() == {"estimate": estimate, "drawn": round(estimate, 2)} and round(estimate, 2) == 0.95
    from matplotlib.colors import to_rgba
    from matplotlib.patches import FancyArrowPatch

    patches, texts = _drawn()
    nets, readings = {}, {}
    for row in "abcde":
        y0 = P.ROW_TOP[row] - P.RH
        for p in patches:  # the net arrow starts at NET_ORIGIN
            if isinstance(p, FancyArrowPatch) and p._posA_posB[0] == (P.NET_ORIGIN, y0 + P.RH / 2):
                nets[row] = (p._posA_posB[1][0] - P.NET_ORIGIN) / P.PUSH
        # each reading hangs under its net arrow, left-aligned with the net column's header
        under = (P.READ_X, y0 + P.RH / 2 - P.READING_DROP)
        readings[row] = [(t.get_text(), t.get_color()) for t in texts if t.get_position() == under]
    words = [t.get_text() for t in texts]
    assert nets == pytest.approx({"b": 4.0, "d": 4.0, "e": 4 * 0.95}, abs=1e-9)  # (a) and (c) are dots: net push 0
    assert readings["d"] == [("Contributions Add Up", P.MUTED)] and readings["e"] == [("Contributions Add Up", P.VERMILLION)]
    assert to_rgba(readings["e"][0][1]) != to_rgba(readings["d"][0][1])
    assert all(P.TITLES[r] in words for r in "abcde") and all(P.READINGS[r] in words for r in "abc")
    assert P.SECTIONS == ("The Paper's Picture", "Released Decomposition") and all(s in words for s in P.SECTIONS)
    assert not any("74" in t for t in words)  # the 74 percent is in the caption, not on the figure


def test_the_committed_png_and_its_50_percent_copy_exist_and_no_other_figure_3_file():
    from PIL import Image

    from vpd_audit_2.post_small import small_path

    full = P.OUT_DIR / P.OUT_NAME
    w, h = Image.open(full).size
    assert Image.open(small_path(full, 0.5)).size == (round(0.5 * w), round(0.5 * h))
    assert {p.name for p in P.OUT_DIR.glob("figure3_*")} == {full.name, small_path(full, 0.5).name}  # no figure3_row_d.txt
