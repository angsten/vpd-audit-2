"""Plan 3 of the research log: the post's Figure 2, the schematic of the carry-over test. The drawing writes a PNG and its 50
percent copy; the masks of panel (d), computed from B's labels and A's source by mask = label + source x (1 - label), are
the plan's table, drawn with 1 for fully on; and the committed PNG and its copy."""

from __future__ import annotations

import numpy as np

from vpd_audit_2 import post_schematic as S

# The plan's panel (d), typed from plan 3 of the research log, row by row (components) and column by column (tokens).
PLAN_D = [["on", "on", "on", "on"],
          ["0", "0.8", "0.6", "0"],
          ["on", "on", "on", "on"],
          ["0", "0", "0", "0"],
          ["on", "on", "on", "on"]]


def test_the_drawing_writes_a_png_and_its_50_percent_copy(tmp_path):
    path = S.draw_carry_over_schematic(tmp_path / S.OUT_NAME)
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == [S.OUT_NAME, S.OUT_NAME.replace(".png", "_50.png")]


def test_the_masks_by_the_rule_are_the_plans_table_cell_for_cell():
    assert S.mask_cells(S.LABELS_B, S.SETTING) == PLAN_D
    m = S.masks(S.LABELS_B, S.SETTING)
    want = np.array([[1.0 if c == "on" else float(c) for c in row] for row in PLAN_D])
    assert m.shape == (5, 4)
    assert np.allclose(m, want, rtol=0, atol=1e-12)
    # the input is the plan's: the source on, off, on, off, on
    assert S.SETTING.tolist() == [1, 0, 1, 0, 1]


def test_the_source_and_panel_d_are_drawn_with_1_for_fully_on():
    plt = S._plt()
    fig, (ax_b, ax_d) = plt.subplots(1, 2)
    S.setting_column(ax_b, 0, 0, S.SETTING)
    S.mask_grid(ax_d, 0, 0, S.mask_cells(S.LABELS_B, S.SETTING))
    column = [t.get_text() for t in ax_b.texts]
    grid = [t.get_text() for t in ax_d.texts][: S.NR * S.NC]  # the cells, row by row, before the token row
    plt.close(fig)
    assert column == ["1", "0", "1", "0", "1"]
    assert grid == [("1" if c == "on" else c) for row in PLAN_D for c in row]


# The settled footer.
SETTLED_FOOTER = ('Run the model on "The capital of France" with the masks in (d) and measure the KL divergence at each token. '
                  "Little damage is expected if faithful. If damage transfers to unseen texts like B, the defect is systematic.")


def test_the_footer_is_the_settled_text_in_four_lines():
    text = S.footer_text()
    assert " ".join(text.split()) == SETTLED_FOOTER
    assert len(text.splitlines()) == 4


def test_the_committed_png_and_its_50_percent_copy_exist_and_no_other_figure_2_png():
    from PIL import Image

    from vpd_audit_2.post_small import small_path

    full = S.OUT_DIR / S.OUT_NAME
    w, h = Image.open(full).size
    assert Image.open(small_path(full, 0.5)).size == (round(0.5 * w), round(0.5 * h))
    assert {p.name for p in S.OUT_DIR.glob("figure2_*.png")} == {full.name, small_path(full, 0.5).name}
