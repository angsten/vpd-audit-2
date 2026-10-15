"""Session 7, plan 3: the post's Figure 2, the schematic of the carry-over test. Both drawings write a PNG, and the masks
of panel (d), computed from B's labels and A's setting by mask = label + setting x (1 - label), are the plan's table."""

from __future__ import annotations

import numpy as np
import pytest

from vpd_audit_2 import post_schematic as S

# The plan's panel (d), typed from sessions/007/engineering/plan_3.md, row by row (components) and column by column (tokens).
PLAN_D = [["on", "on", "on", "on"],
          ["0", "0.8", "0.6", "0"],
          ["on", "on", "on", "on"],
          ["0", "0", "0", "0"],
          ["on", "on", "on", "on"]]


@pytest.mark.parametrize("control", [True, False])
def test_each_drawing_writes_a_png(tmp_path, control):
    path = S.draw_carry_over_schematic(tmp_path / S.OUT_NAMES[control], control=control)
    assert path.is_file() and path.stat().st_size > 0
    assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_the_masks_by_the_rule_are_the_plans_table_cell_for_cell():
    assert S.mask_cells(S.LABELS_B, S.SETTING) == PLAN_D
    m = S.masks(S.LABELS_B, S.SETTING)
    want = np.array([[1.0 if c == "on" else float(c) for c in row] for row in PLAN_D])
    assert m.shape == (5, 4)
    assert np.allclose(m, want, rtol=0, atol=1e-12)
    # the inputs are the plan's: setting on, off, on, off, on; the shuffled copy on, off, on, on, off
    assert S.SETTING.tolist() == [1, 0, 1, 0, 1] and S.SHUFFLED.tolist() == [1, 0, 1, 1, 0]
    assert sorted(S.SHUFFLED.tolist()) == sorted(S.SETTING.tolist())  # the same numbers, dealt out differently


# The head's footer after plan 3's report 1, for both variants, typed from the head's message.
HEAD_FOOTER = ('Run the model on "The capital of France" with (d); measure the KL divergence from the original at each token. '
               "Every mask in (d) is permitted by B's labels, so if faithful, near zero is expected. "
               "Damage tuned to A does little on B; damage across B's texts is a systematic defect.")


def test_the_footer_is_the_heads_text_less_from_the_original_in_four_lines():
    text = S.footer_text()
    assert " ".join(text.split()) == HEAD_FOOTER.replace(" from the original", "")
    assert len(text.splitlines()) == 4
