"""The reduced copies of the post's PNGs, shared by `post_figure`, `post_schematic`, and `post_interference`.

Each copy is the full-size PNG resampled (Lanczos) to a share of its pixel dimensions and saved beside it with the
percentage as a suffix (_75, _62, _50), so its layout and fonts are the full-size figure's exactly; its metadata records
the full-size files' 200 dpi times the same share. Re-rendering at a lower dpi instead would not keep the layout: the
font's pixel hinting makes text a little wider relative to the drawing, and in an earlier Figure 1 the diagonal label
then ran into the legend's last line.

The post shows Figure 1 at 62 percent and Figures 2 and 3 at 50 percent; Figure 1 and its registered form also have a
75 percent copy.
"""

from __future__ import annotations

from pathlib import Path

FULL_DPI = 200  # the full-size files' resolution
SCALE = 0.75  # the default share


def small_path(path: Path, scale: float = SCALE) -> Path:
    """The copy's path: the percentage as a suffix before .png (_75 for 0.75)."""
    p = Path(path)
    return p.with_name(f"{p.stem}_{round(100 * scale)}{p.suffix}")


def save_small_copy(path: Path, scale: float = SCALE) -> Path:
    """Write the copy of the PNG at `path`, resampled to `scale` of each dimension, beside it; return its path."""
    from PIL import Image

    out = small_path(path, scale)
    dpi = round(FULL_DPI * scale)
    with Image.open(path) as im:
        w, h = im.size
        im.resize((round(w * scale), round(h * scale)), Image.LANCZOS).save(out, dpi=(dpi, dpi))
    return out
