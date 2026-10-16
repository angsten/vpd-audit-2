"""Plans 4 and 7 of the research log: the post's Figure 3. The toy's net pushes, the drawing and its 50 percent copy, the
measured rows (d) and (e) held to probe 1's record, their schematic net arrows held to the lead record's kept share, their
readings, the numbers in the caption note, and the committed PNG and its copy."""

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


def test_the_drawing_writes_a_png_and_its_50_percent_copy(tmp_path):
    path = P.draw_interference(tmp_path / P.OUT_NAME)
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == [P.OUT_NAME, P.OUT_NAME.replace(".png", "_50.png")]


# ----------------------------------------------------------------------------- rows (d) and (e) from probe 1's record


def _record() -> dict:
    return json.loads(P.PROBE_RECORD.read_text())


def _row_arrows(row: str, probe_record: Path = P.PROBE_RECORD) -> tuple[list[int], list[bool]]:
    """A row as drawn: each cell's arrow direction (+1 right, -1 left), left to right, and whether its cell is on."""
    from matplotlib.colors import to_rgba
    from matplotlib.patches import FancyArrowPatch, Rectangle

    plt = P._plt()
    fig, ax = plt.subplots()
    P._draw_rows(ax, probe_record)
    y0, y1 = P.ROW_TOP[row] - P.RH, P.ROW_TOP[row]
    arrows = []
    for p in ax.patches:
        if isinstance(p, FancyArrowPatch):
            (xa, ya), (xb, yb) = p._posA_posB
            if y0 < ya < y1 and xa < 8 * P.CW3:
                arrows.append((xa, int(np.sign(xb - xa))))
    cells = sorted((p.get_x(), p.get_facecolor()) for p in ax.patches if isinstance(p, Rectangle) and p.get_y() == y0 and p.get_x() < 8 * P.CW3)
    on = [fc == to_rgba(P.OWN) for _, fc in cells]
    plt.close(fig)
    return [s for _, s in sorted(arrows)], on


def test_rows_d_and_e_draw_the_records_signs_on_the_searched_batch_and_on_the_unseen_text():
    comps = _record()["row_d"]["components"]
    name = lambda c: f"{c['module']} {c['component']}"  # noqa: E731
    flipped = {name(c): -int(np.sign(c["switch_off_push_on_text"])) for c in comps}
    assert all(c["drawn_arrow_on_text"] == flipped[name(c)] for c in comps)  # the record's own convention
    on_attack = {name(c): int(c["drawn_arrow_on_attack"]) for c in comps}
    cells = P.row_d_cells(P.row_d_components())
    assert [c["drawn_sign"] for c in cells] == [flipped[c["name"]] for c in cells]
    for row, signs in (("d", on_attack), ("e", flipped)):
        drawn, on = _row_arrows(row)
        assert drawn == [signs[c["name"]] for c in cells] and len(drawn) == 8
        assert on == [bool(s) for s in P.SWITCHES] == [c["cell"] == "on" for c in cells]  # the kept components in the on cells
    assert sorted(c["name"] for c in cells) == sorted(flipped)


def test_rows_d_and_e_follow_the_record_not_a_typed_table(tmp_path):
    rec = _record()
    for c in rec["row_d"]["components"]:  # every measured push reversed
        c["switch_off_push_on_text"] = -c["switch_off_push_on_text"]
        c["drawn_arrow_on_text"] = -c["drawn_arrow_on_text"]
        c["drawn_arrow_on_attack"] = -c["drawn_arrow_on_attack"]
    path = tmp_path / "record.json"
    path.write_text(json.dumps(rec))
    for row in ("d", "e"):
        assert _row_arrows(row, path)[0] == [-s for s in _row_arrows(row)[0]]
    rec["row_d"]["components"][0]["drawn_arrow_on_text"] *= -1  # a record whose drawn sign is not the flip is refused
    path.write_text(json.dumps(rec))
    with pytest.raises(ValueError):
        P.row_d_components(path)


def test_the_measured_rows_have_schematic_net_arrows_from_the_kept_share_and_their_readings():
    # the kept share: the lead record's 320-step retention pooled over all 80 settings, drawn at the table's two places
    steps = json.loads(P.LEAD_RECORD.read_text())["main"]["step"]
    estimate = [s for s in steps if s["key"] == 320][0]["retention"]["pooled"]["estimate"]
    assert P.kept_share() == {"estimate": estimate, "drawn": round(estimate, 2)} and round(estimate, 2) == 0.95
    from matplotlib.colors import to_rgba
    from matplotlib.patches import FancyArrowPatch

    plt = P._plt()
    fig, ax = plt.subplots()
    P._draw_rows(ax)
    nets, readings = {}, {}
    for row in "abcde":
        y0 = P.ROW_TOP[row] - P.RH
        for p in ax.patches:  # the net arrow starts at NET_ORIGIN
            if isinstance(p, FancyArrowPatch) and p._posA_posB[0] == (P.NET_ORIGIN, y0 + P.RH / 2):
                nets[row] = (p._posA_posB[1][0] - P.NET_ORIGIN) / P.PUSH
        readings[row] = [(t.get_text(), t.get_color()) for t in ax.texts if t.get_position() == (P.READ_X, y0 + P.RH / 2)]
    texts = [t.get_text() for t in ax.texts]
    plt.close(fig)
    assert nets == pytest.approx({"b": 4.0, "d": 4.0, "e": 4 * 0.95}, abs=1e-9)  # (a) and (c) are dots: net push 0
    assert readings["d"] == [("Contributions Add Up", P.MUTED)] and readings["e"] == [("Contributions Add Up", P.VERMILLION)]
    assert to_rgba(readings["e"][0][1]) != to_rgba(readings["d"][0][1])
    assert all(P.TITLES[r] in texts for r in "abcde") and all(P.READINGS[r] in texts for r in "abc")
    assert not any("74" in t for t in texts)  # the 74 percent is in the caption, not on the figure


def test_the_caption_note_holds_the_records_numbers_and_both_rows_as_drawn():
    r = _record()["rows"]["n320"]
    n = P.row_d_numbers()
    assert n["raw_pct"] == round(100 * r["g_bar"]) == 74 and n["perm_pct"] == round(100 * r["post_hoc_permutation_baseline"]["g0_bar"]) == 55
    assert n["kept_pct"] == round(100 * r["g0_bar"]) == 74 and round(4 * r["additivity"]["off_set"]) / 4 == 0.25
    note = P.row_d_note()
    assert note.startswith("Figure 3, rows (d) and (e): caption note")
    assert "WHILE ON" in note and "negative of the measured effect of switching it off" in note
    k = P.kept_share()
    assert "net arrows in rows (d) and (e) are schematic, not measured" in note
    assert f"times {k['drawn']:.2f}, the share" in note and f"{k['estimate']:.4f}, drawn as {k['drawn']:.2f}." in note
    assert f"g_bar {n['raw']:.4f} (the caption's 74 percent)" in note
    word = {1: "right (+)", -1: "left (-)"}
    listed = [line for line in note.splitlines() if line[:5].strip().rstrip(".").isdigit()]
    rows = {row: P.measured_cells(P.PROBE_RECORD, key) for row, key in P.MEASURED_ROWS.items()}
    assert len(listed) == 8
    for line, e, d in zip(listed, rows["e"], rows["d"]):  # each line: the component, then its arrow in (e), then in (d)
        assert e["name"] in line and line.rstrip().endswith(f"{word[e['sign']]:<9}  {word[d['sign']]}")


def test_the_committed_png_and_its_50_percent_copy_exist_and_no_other_figure_3_png():
    from PIL import Image

    from vpd_audit_2.post_small import small_path

    full = P.OUT_DIR / P.OUT_NAME
    w, h = Image.open(full).size
    assert Image.open(small_path(full, 0.5)).size == (round(0.5 * w), round(0.5 * h))
    assert {p.name for p in P.OUT_DIR.glob("figure3_*.png")} == {full.name, small_path(full, 0.5).name}
    assert (P.OUT_DIR / P.ROW_D_NOTE_NAME).read_text() == P.row_d_note()
