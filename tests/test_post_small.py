"""Session 7: the 75 percent copies of the post's PNGs. The naming, the size, and that a drawing writes its copy."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from vpd_audit_2 import post_schematic as S
from vpd_audit_2 import post_small as M


def test_the_copy_is_named_with_75_before_png():
    assert M.small_path(Path("results/post/figure1_carry_over.png")) == Path("results/post/figure1_carry_over_75.png")
    assert M.small_path(Path("x/figure1_carry_over_a.png")).name == "figure1_carry_over_a_75.png"


def test_the_copy_is_75_percent_of_each_dimension(tmp_path):
    full = tmp_path / "f.png"
    Image.new("RGBA", (1260, 1000), "white").save(full)
    out = M.save_small_copy(full)
    assert out == tmp_path / "f_75.png"
    with Image.open(out) as im:
        assert im.size == (945, 750)
    with Image.open(full) as im:
        assert im.size == (1260, 1000)  # the full-size file is left as it was


def test_a_drawing_writes_its_75_percent_copy(tmp_path):
    path = S.draw_carry_over_schematic(tmp_path / S.OUT_NAMES[False], control=False)
    with Image.open(path) as full, Image.open(M.small_path(path)) as small:
        assert small.size == (round(full.size[0] * 0.75), round(full.size[1] * 0.75))
