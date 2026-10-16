"""Plan 3 of the research log: the post's Figure 2, a schematic of the carry-over test. A toy example; no data, no model runs.

    uv run python -m vpd_audit_2.post_schematic

The paper's adversary searches text A and finds one column of numbers, one per component, 1 or 0 (b); the column is
applied unchanged to text B, which the search never saw, where B's own labels set each mask's minimum (d). Every mask in
(d) is one B's labels permit, so any damage is the labels' failure.

One PNG goes to `results/post/`, `figure2_carry_over_schematic.png`, with a copy at 50 percent of its pixel size, suffix
_50, by `post_small` (the post shows the copy). The shuffled copy of the column, the control, is described in the
caption, not drawn.

The style is the first post's two schematics (`aggregation_schematic.png`, `delete_schematic.png`, drawn by
`third_party/vpd-audit/vpd_audit/figures_post.py`); the helpers this figure needs are copied from that file, some with an
optional argument added, so that this module stands alone. The figure is laid out at the aggregation schematic's scale
(the same inches per data unit), so its cells are the same size in the saved image.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import numpy as np

from vpd_audit_2.post_small import save_small_copy, small_path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "results" / "post"
OUT_NAME = "figure2_carry_over_schematic.png"
COPY_SCALE = 0.5  # the reduced copy, as a share of the full size

# ----------------------------------------------------------------------------- copied from the first post's figure code

BLUE = "#0072B2"
INK, MUTED, SPINE = "#1a1a1a", "#6b6b6b", "#3a3a3a"
PINK = "#CC79A7"  # at its label
OWN = "#7a7a7a"  # on
OFF = "#f0f0f0"  # 0, or off
RC = {"font.size": 11, "font.family": "DejaVu Sans"}
CW = 1.7  # cell width, so whole words fit above each column
COMPONENTS = ["Sentence Start", '"Capital of" Pattern', "Paris Fact", "Sky Fact", "Chemistry Fact"]
NR, NC = 5, 4
W = NC * CW
HEAD = 11.2  # the panel headings' size


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def grey(v):
    lo, hi = np.array([0.86, 0.86, 0.86]), np.array([0.22, 0.22, 0.22])
    return tuple(lo + (hi - lo) * v)


def cell_y(i, y0):
    return y0 + NR - 1 - i


def tokens_row(ax, tokens, x0, y0):
    for j, tok in enumerate(tokens):
        ax.text(x0 + (j + 0.5) * CW, y0 + NR + 0.15, tok, ha="center", va="bottom", fontsize=11, color=INK, fontweight="bold")


def row_names(ax, x0, y0, header=False):
    for i, comp in enumerate(COMPONENTS):
        ax.text(x0 - 0.2, cell_y(i, y0) + 0.5, comp, ha="right", va="center", fontsize=10.5, color=INK)
    if header:
        ax.text(x0 - 0.2, y0 + NR + 0.15, "Components ↓", ha="right", va="bottom", fontsize=9, color="#a6a6a6", style="italic")


def title(ax, text, x_centre, y0, colour=INK, size=HEAD, dy=1.0):
    ax.text(x_centre, y0 + NR + dy, text, ha="center", va="bottom", fontsize=size, color=colour)


def heat(ax, values, tokens, x0, y0):
    """A label grid, shaded dark-to-light by value (the aggregation schematic's, with no token greyed)."""
    from matplotlib.patches import Rectangle

    for i in range(NR):
        for j in range(NC):
            v = values[i, j]
            fc = "white" if v == 0 else grey(v)
            ax.add_patch(Rectangle((x0 + j * CW, cell_y(i, y0)), CW, 1, facecolor=fc, edgecolor="white", linewidth=2))
            txt = "0" if v == 0 else f"{v:.1f}"
            tc = MUTED if v == 0 else ("white" if v >= 0.5 else INK)
            ax.text(x0 + (j + 0.5) * CW, cell_y(i, y0) + 0.5, txt, ha="center", va="center", fontsize=10, color=tc)
    tokens_row(ax, tokens, x0, y0)


def legend_items(ax, x, y, items):
    from matplotlib.patches import Rectangle

    for k, (fc, lab) in enumerate(items):
        ax.add_patch(Rectangle((x, y - 0.6 * k), 0.42, 0.42, facecolor=fc, edgecolor=SPINE, linewidth=0.6))
        ax.text(x + 0.6, y - 0.6 * k + 0.21, lab, va="center", fontsize=9.5, color=INK)


def arrow(ax, a, b, colour=MUTED, lw=1.4, style="-|>", rad=0.0, scale=14):
    """`scale` (the arrow head's size) added; 14 is the first post's."""
    from matplotlib.patches import FancyArrowPatch

    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=scale, color=colour, linewidth=lw,
                                 connectionstyle=f"arc3,rad={rad}"))


def footer(ax, x, y, text, va="center"):
    """`va` added ("center" is the first post's), so the box can hang from a fixed top edge."""
    ax.text(x, y, text, ha="center", va=va, fontsize=10, color=INK,
            bbox=dict(boxstyle="square,pad=0.6", facecolor="#f0f0f0", edgecolor=INK, linewidth=1.0))


# The aggregation schematic's scale: its figure (12.5 x 8.8 inches) and limits fix the inches per data unit, set by its
# height (the default subplot box is 0.77 of the figure's height and 0.775 of its width).
REFERENCE_INCHES_PER_UNIT = 0.77 * 8.8 / ((NR + 3.8 + NR + 2.2) - (-2.4))
AXES_HEIGHT_SHARE, AXES_WIDTH_SHARE = 0.77, 0.775


def save(fig, ax, path, xlim, ylim):
    """The first post's `save`, with the 50 percent copy (`post_small`) added after the full-size file."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, facecolor="white", bbox_inches="tight", dpi=200)
    _plt().close(fig)
    save_small_copy(path, COPY_SCALE)


# ----------------------------------------------------------------------------- the toy example

TOKENS_A = ["The", "sky", "is", "blue"]
TOKENS_B = ["The", "capital", "of", "France"]
LABELS_A = np.array([[0.8, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0.7, 1.0, 0.4], [0, 0, 0, 0]])  # the aggregation schematic's donor
LABELS_B = np.array([[0.9, 0, 0, 0], [0, 0.8, 0.6, 0], [0, 0, 0, 1.0], [0, 0, 0, 0], [0, 0, 0, 0]])  # its recipient
SETTING = np.array([1, 0, 1, 0, 1])  # on, off, on, off, on: two of five off, one of them (Sky Fact) a component A needs


def masks(labels: np.ndarray, setting: np.ndarray) -> np.ndarray:
    """mask = label + setting x (1 - label), per component (row) and token (column): an "on" leaves the component fully
    on, an "off" turns it down to the text's label."""
    s = np.asarray(setting, dtype=np.float64)[:, None]
    lab = np.asarray(labels, dtype=np.float64)
    return lab + s * (1.0 - lab)


def mask_cells(labels: np.ndarray, setting: np.ndarray) -> list[list[str]]:
    """The masks as panel (d) prints them: "on" where the mask is 1, else its value to one decimal ("0" for 0)."""
    m = masks(labels, setting)
    return [["on" if np.isclose(v, 1.0) else ("0" if v == 0 else f"{v:.1f}") for v in row] for row in m]


# ----------------------------------------------------------------------------- the words

TITLES = {"a": "(a) Text A's Labels", "b": "(b) Adversarial\nSource for A", "c": "(c) Text B's Labels",
          "d": "(d) Text B's Masks Under A's Adversarial Source"}
ARROWS = {"search": "Adversary searches for\nthe source most\ndamaging to A", "copied": "Applied\nUnchanged"}
# The legend states the rule by which B's labels set the masks in (d), so the lower arrow carries no words.
LEGEND = [(OFF, "Source is 0, B doesn't need"), (OWN, "Source is 1, fully on regardless of B"),
          (PINK, "Source is 0, B's label sets min")]
# The comparison with B's own search and with the shuffled copy is in the caption.
FOOTER = ('Run the model on "The capital of France" with the masks in (d) and measure the KL divergence at each token. '
          "Little damage is expected if faithful. If damage transfers to unseen texts like B, the defect is systematic.")
FOOTER_WIDTH = 62  # characters per line: a narrow wrap, so that the box ends well clear of the legend


def footer_text() -> str:
    """The footer, in as few lines as fit `FOOTER_WIDTH`, made as even as that number of lines allows (no orphaned word)."""
    n, w = len(textwrap.wrap(FOOTER, FOOTER_WIDTH)), FOOTER_WIDTH
    while len(textwrap.wrap(FOOTER, w - 1)) == n:
        w -= 1
    return textwrap.fill(FOOTER, w)


# ----------------------------------------------------------------------------- the layout (data units; a cell is CW by 1)

TOP = NR + 4.4  # y of the top row of grids (the aggregation schematic's 3.8, raised to fit the blue arrow)
RX = W + 2.8  # x of the bottom right grid, (d), as in the aggregation schematic
BX = RX + W / 2 - CW / 2  # x of column (b), above the middle of (d), as in the aggregation schematic
TITLE_DY = 1.05  # the grids' titles above their token rows
B_TITLE_DY = 0.6  # (b)'s title, nearer its column, which has no token row
FOOTER_TOP = -0.35  # the footer box's top edge, just under (c)
FOOTER_X_SHIFT = -0.5  # the box's centre, left of the middle of the space left of the legend, so it ends clear of it
LEGEND_XY = (RX, -0.85)  # under (d)


def setting_column(ax, x0, y0, setting, width=CW):
    """A column of five cells aligned with the component rows: 1 grey with white text, 0 light."""
    from matplotlib.patches import Rectangle

    for i, on in enumerate(setting):
        fc, txt, tc = (OWN, "1", "white") if on else (OFF, "0", MUTED)
        ax.add_patch(Rectangle((x0, cell_y(i, y0)), width, 1, facecolor=fc, edgecolor="white", linewidth=2, alpha=1.0))
        ax.text(x0 + width / 2, cell_y(i, y0) + 0.5, txt, ha="center", va="center", fontsize=10, color=tc)


def mask_grid(ax, x0, y0, cells):
    """Panel (d) in the delete schematic's vocabulary: fully on (1) grey, a value at its label pink, 0 light."""
    from matplotlib.patches import Rectangle

    for i in range(NR):
        for j in range(NC):
            v = cells[i][j]
            fc, tc = (OWN, "white") if v == "on" else ((OFF, MUTED) if v == "0" else (PINK, "white"))
            ax.add_patch(Rectangle((x0 + j * CW, cell_y(i, y0)), CW, 1, facecolor=fc, edgecolor="white", linewidth=2))
            ax.text(x0 + (j + 0.5) * CW, cell_y(i, y0) + 0.5, "1" if v == "on" else v, ha="center", va="center", fontsize=10,
                    color=tc)
    tokens_row(ax, TOKENS_B, x0, y0)


def draw_carry_over_schematic(path: Path) -> Path:
    """The schematic, and its 50 percent copy beside it."""
    plt = _plt()
    text = footer_text()
    pad = 0.6 * 10 / 72 / REFERENCE_INCHES_PER_UNIT  # the footer box's pad (0.6 of its 10-point font), in data units
    box = ((text.count("\n") + 1) * 10 * 1.2 / 72) / REFERENCE_INCHES_PER_UNIT + 2 * pad  # the box's height
    xlim = (-3.6, RX + W + 0.3)
    ylim = (FOOTER_TOP - box - 0.25, TOP + NR + 2.4)  # the bottom follows the footer
    height = (ylim[1] - ylim[0]) * REFERENCE_INCHES_PER_UNIT / AXES_HEIGHT_SHARE
    width = 1.05 * (xlim[1] - xlim[0]) * REFERENCE_INCHES_PER_UNIT / AXES_WIDTH_SHARE  # wide enough that the height sets the scale
    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(width, height))
        # (a) text A's labels, top left
        heat(ax, LABELS_A, TOKENS_A, 0, TOP)
        row_names(ax, 0, TOP, header=True)
        title(ax, TITLES["a"], W / 2, TOP, dy=TITLE_DY)
        # (b) the source found on A, top right, one column aligned with the rows
        setting_column(ax, BX, TOP, SETTING)
        title(ax, TITLES["b"], BX + CW / 2, TOP, dy=B_TITLE_DY)
        # arrow (a) -> (b): the search
        y_search = TOP + 2.5
        arrow(ax, (W + 0.2, y_search), (BX - 0.2, y_search))
        ax.text((W + BX) / 2, y_search + 0.35, ARROWS["search"], ha="center", va="bottom", fontsize=9.5, color=MUTED, linespacing=1.15)
        # arrow (b) -> (d): applied unchanged, blue, the most visible arrow, its label at its right
        x_copy = BX + CW / 2
        y_from, y_to = TOP - 0.15, NR + TITLE_DY + 0.6
        arrow(ax, (x_copy, y_from), (x_copy, y_to), colour=BLUE, lw=3.0, scale=24)
        ax.text(x_copy + 0.3, (y_from + y_to) / 2, ARROWS["copied"], ha="left", va="center", fontsize=9.5, color=BLUE, linespacing=1.15)
        # (c) text B's labels, never searched, bottom left
        heat(ax, LABELS_B, TOKENS_B, 0, 0)
        row_names(ax, 0, 0, header=True)
        title(ax, TITLES["c"], W / 2, 0, dy=TITLE_DY)
        # (d) B's masks under A's source, bottom right
        mask_grid(ax, RX, 0, mask_cells(LABELS_B, SETTING))
        title(ax, TITLES["d"], RX + W / 2, 0, dy=TITLE_DY)
        # arrow (c) -> (d): B's labels set the minimums (the legend says how)
        y_floor = 2.5
        arrow(ax, (W + 0.2, y_floor), (RX - 0.2, y_floor))
        # legend under (d), footer under (c)
        legend_items(ax, *LEGEND_XY, LEGEND)
        footer(ax, ((-4.1) + (RX - 0.3)) / 2 + FOOTER_X_SHIFT, FOOTER_TOP - pad, text, va="top")  # left of the legend
        save(fig, ax, path, xlim, ylim)
    return Path(path)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = draw_carry_over_schematic(OUT_DIR / OUT_NAME)
    for q in (p, small_path(p, COPY_SCALE)):
        print(f"wrote {q.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
