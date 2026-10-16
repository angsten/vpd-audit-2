"""The reduced copies of the post's PNGs. The naming, the size and resolution, and that a drawing writes its copy."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from vpd_audit_2 import post_schematic as S
from vpd_audit_2 import post_small as M


def test_the_copy_is_named_with_its_percentage_before_png():
    assert M.small_path(Path("results/post/figure1_carry_over.png")) == Path("results/post/figure1_carry_over_75.png")
    assert M.small_path(Path("results/post/figure1_carry_over.png"), 0.62).name == "figure1_carry_over_62.png"
    assert M.small_path(Path("x/figure2_carry_over_schematic.png"), 0.5).name == "figure2_carry_over_schematic_50.png"


@pytest.mark.parametrize("scale, size, dpi", [(0.75, (945, 750), 150), (0.62, (781, 620), 124), (0.5, (630, 500), 100)])
def test_the_copy_is_its_share_of_each_dimension(tmp_path, scale, size, dpi):
    full = tmp_path / "f.png"
    Image.new("RGBA", (1260, 1000), "white").save(full)
    out = M.save_small_copy(full, scale)
    assert out == tmp_path / f"f_{round(100 * scale)}.png"
    with Image.open(out) as im:
        assert im.size == size
        assert tuple(round(v) for v in im.info["dpi"]) == (dpi, dpi)  # 200 dpi times the share, as the scripts recorded it
    with Image.open(full) as im:
        assert im.size == (1260, 1000)  # the full-size file is left as it was


def test_a_drawing_writes_its_50_percent_copy(tmp_path):
    path = S.draw_carry_over_schematic(tmp_path / S.OUT_NAME)
    with Image.open(path) as full, Image.open(M.small_path(path, 0.5)) as small:
        assert small.size == (round(full.size[0] * 0.5), round(full.size[1] * 0.5))
