"""The 75 percent copies of the post's PNGs (the PI, session 7), shared by `post_figure`, `post_schematic`, and
`post_interference`.

Each copy is the full-size PNG resampled (Lanczos) to 75 percent of its pixel dimensions and saved beside it with the
suffix _75, so its layout and fonts are the full-size figure's exactly. Re-rendering at 150 dpi instead would not keep
the layout: the font's pixel hinting makes text a little wider relative to the drawing at 150 dpi, and in Figure 1's
post variant the diagonal label then runs into the legend's last line.
"""

from __future__ import annotations

from pathlib import Path

SCALE = 0.75
SMALL_DPI = 150  # recorded in the copy's metadata: 75 percent of the full-size files' 200


def small_path(path: Path) -> Path:
    """The 75 percent copy's path: the suffix _75 before .png."""
    p = Path(path)
    return p.with_name(f"{p.stem}_75{p.suffix}")


def save_small_copy(path: Path) -> Path:
    """Write the 75 percent copy of the PNG at `path` beside it; return its path."""
    from PIL import Image

    out = small_path(path)
    with Image.open(path) as im:
        w, h = im.size
        im.resize((round(w * SCALE), round(h * SCALE)), Image.LANCZOS).save(out, dpi=(SMALL_DPI, SMALL_DPI))
    return out
