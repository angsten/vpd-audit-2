"""Session 7, plan 3: the post's Figure 2, a schematic of the carry-over test. A toy example; no data, no model runs.

    uv run python -m vpd_audit_2.post_schematic

The paper's adversary searches text A and finds one column of numbers, one per component (b); the column is copied
unchanged onto text B, which the search never saw, where B's own labels set each mask's floor (d). Every mask in (d) is
one B's labels permit, so any damage is the labels' failure. A shuffled copy of the column (b') is the control.

Two PNGs go to `results/post/` (each also as a copy at 75 percent of its pixel size, suffix _75, by `post_small`):
`figure2_carry_over_schematic.png`, with (b'), and
`figure2_carry_over_schematic_no_control.png`, identical but without (b'). Both have the same footer; the comparison
with B's own search and with the shuffled copy is in the caption.

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
OUT_NAMES = {True: "figure2_carry_over_schematic.png", False: "figure2_carry_over_schematic_no_control.png"}

# ----------------------------------------------------------------------------- copied from the first post's figure code

BLUE = "#0072B2"
GREEN = "#009E73"
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


def check_row(ax, x0, label, marks):
    """The delete schematic's check row (`ticks`): an italic question to the left of the grid and a mark under each token."""
    ax.text(x0 - 0.2, -0.45, label, ha="right", va="center", fontsize=9.5, color=MUTED, style="italic")
    for j, ok in enumerate(marks):
        ax.text(x0 + (j + 0.5) * CW, -0.45, "✓" if ok else "✗", ha="center", va="center", fontsize=14,
                color=GREEN if ok else "#E57373", fontweight="bold")


# The aggregation schematic's scale: its figure (12.5 x 8.8 inches) and limits fix the inches per data unit, set by its
# height (the default subplot box is 0.77 of the figure's height and 0.775 of its width).
REFERENCE_INCHES_PER_UNIT = 0.77 * 8.8 / ((NR + 3.8 + NR + 2.2) - (-2.4))
AXES_HEIGHT_SHARE, AXES_WIDTH_SHARE = 0.77, 0.775


def save(fig, ax, path, xlim, ylim):
    """The first post's `save`, with the 75 percent copy (`post_small`) added after the full-size file."""
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, facecolor="white", bbox_inches="tight", dpi=200)
    _plt().close(fig)
    save_small_copy(path)


# ----------------------------------------------------------------------------- the toy example

TOKENS_A = ["The", "sky", "is", "blue"]
TOKENS_B = ["The", "capital", "of", "France"]
LABELS_A = np.array([[0.8, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0.7, 1.0, 0.4], [0, 0, 0, 0]])  # the aggregation schematic's donor
LABELS_B = np.array([[0.9, 0, 0, 0], [0, 0.8, 0.6, 0], [0, 0, 0, 1.0], [0, 0, 0, 0], [0, 0, 0, 0]])  # its recipient
SETTING = np.array([1, 0, 1, 0, 1])  # on, off, on, off, on: two of five off, one of them (Sky Fact) a component A needs
SHUFFLED = np.array([1, 0, 1, 1, 0])  # the same numbers, the Sky Fact off and the Chemistry Fact on exchanged


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

TITLES = {"a": "(a) Text A's labels", "b": "(b) The setting the\nadversary found on A", "b2": "(b′) Shuffled copy,\na control",
          # (c) on two lines: on one it would end 0.13 units short of (d)'s title, and the two would read as one
          "c": "(c) Text B's labels, from a batch\nthe setting never saw", "d": "(d) Text B's masks under A's setting"}
NOTES = {"a": "one text stands for a batch of 128", "b": "found by search, not\nread from A's labels",
         "b_under": "one number per component,\nthe same at every token\nof every text",
         "b2": "same numbers, other\ncomponents in the\nsame weight matrix\nused about as often", "c": "one of 128 texts"}
ARROWS = {"search": "adversary's search:\nthe permitted masks\nthat damage A most", "copied": "copied unchanged\nto text B",
          "floors": "B's own labels\nset the floors", "floors_rule": "on → fully on;\noff → down to\nB's label"}
CHECK = "Permitted by\nB's labels?"  # on two lines, so that it stays in the gap between (c) and (d)
LEGEND = [(OWN, "on: setting on, fully on everywhere"), (PINK, "at its label: setting off, and B needs the component here"),
          (OFF, "0: setting off, and B's label is 0 here")]
# The head's footer after plan 3's report 1, the same in both variants (the comparison with B's own search and with the
# shuffled copy moved to the caption), with "from the original" dropped after "KL divergence", as the head said to if it
# still ran to five lines: with it the text is 3,884 px long at the footer's font, and five lines.
FOOTER = ('Run the model on "The capital of France" with (d); measure the KL divergence at each token. '
          "Every mask in (d) is permitted by B's labels, so if faithful, near zero is expected. "
          "Damage tuned to A does little on B; damage across B's texts is a systematic defect.")
# Characters per line: the widest wrap whose lines all fit the 950 px of text the box has left of the legend under (d)
# (measured: 68 characters, 4 lines, the widest 933 px).
FOOTER_WIDTH = 68


def footer_text() -> str:
    """The footer, in as few lines as fit `FOOTER_WIDTH`, made as even as that number of lines allows (no orphaned word)."""
    n, w = len(textwrap.wrap(FOOTER, FOOTER_WIDTH)), FOOTER_WIDTH
    while len(textwrap.wrap(FOOTER, w - 1)) == n:
        w -= 1
    return textwrap.fill(FOOTER, w)


# ----------------------------------------------------------------------------- the layout (data units; a cell is CW by 1)

TOP = NR + 4.4  # y of the top row of grids (the aggregation schematic's 3.8, raised to fit the notes and the blue arrow)
RX = W + 2.8  # x of the bottom right grid, (d), as in the aggregation schematic
BX = RX + W / 2 - CW / 2  # x of column (b), above the middle of (d), as in the aggregation schematic
B2_GAP, B2_WIDTH = 0.35, 1.2  # (b') beside (b), narrower
B2X = BX + CW + B2_GAP
B2_TEXT_X = B2X + B2_WIDTH + 0.35  # (b')'s title and note, to the right of its column
TITLE_DY = 1.5  # the grids' titles above their token rows, raised to leave room for a note under them
FOOTER_TOP = -1.05  # the footer box's top edge, below the check row's two-line question
LEGEND_XY = (RX, -1.5)


def setting_column(ax, x0, y0, setting, width=CW, faded=False):
    """A column of five on/off cells aligned with the component rows: "on" grey with white text, "off" light."""
    from matplotlib.patches import Rectangle

    alpha = 0.6 if faded else 1.0  # the shuffled copy's cells faded, their words still legible
    for i, on in enumerate(setting):
        fc, txt, tc = (OWN, "on", "white") if on else (OFF, "off", MUTED)
        ax.add_patch(Rectangle((x0, cell_y(i, y0)), width, 1, facecolor=fc, edgecolor="white", linewidth=2, alpha=alpha))
        ax.text(x0 + width / 2, cell_y(i, y0) + 0.5, txt, ha="center", va="center", fontsize=10, color=tc)


def mask_grid(ax, x0, y0, cells):
    """Panel (d) in the delete schematic's vocabulary: "on" grey, a value at its label pink, 0 light."""
    from matplotlib.patches import Rectangle

    for i in range(NR):
        for j in range(NC):
            v = cells[i][j]
            fc, tc = (OWN, "white") if v == "on" else ((OFF, MUTED) if v == "0" else (PINK, "white"))
            ax.add_patch(Rectangle((x0 + j * CW, cell_y(i, y0)), CW, 1, facecolor=fc, edgecolor="white", linewidth=2))
            ax.text(x0 + (j + 0.5) * CW, cell_y(i, y0) + 0.5, v, ha="center", va="center", fontsize=10, color=tc)
    tokens_row(ax, TOKENS_B, x0, y0)


def draw_carry_over_schematic(path: Path, control: bool = True) -> Path:
    """The schematic; with `control` False, without (b')."""
    from matplotlib.patches import Rectangle

    plt = _plt()
    text = footer_text()
    pad = 0.6 * 10 / 72 / REFERENCE_INCHES_PER_UNIT  # the footer box's pad (0.6 of its 10-point font), in data units
    box = ((text.count("\n") + 1) * 10 * 1.2 / 72) / REFERENCE_INCHES_PER_UNIT + 2 * pad  # the box's height
    xlim = (-3.6, RX + W + 0.3)
    ylim = (FOOTER_TOP - box - 0.25, TOP + NR + 2.4)  # the bottom follows the footer, which is a line shorter without (b')
    height = (ylim[1] - ylim[0]) * REFERENCE_INCHES_PER_UNIT / AXES_HEIGHT_SHARE
    width = 1.05 * (xlim[1] - xlim[0]) * REFERENCE_INCHES_PER_UNIT / AXES_WIDTH_SHARE  # wide enough that the height sets the scale
    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(width, height))
        # (a) text A's labels, top left
        heat(ax, LABELS_A, TOKENS_A, 0, TOP)
        row_names(ax, 0, TOP, header=True)
        title(ax, TITLES["a"], W / 2, TOP, dy=TITLE_DY)
        ax.text(W / 2, TOP + NR + 1.0, NOTES["a"], ha="center", va="bottom", fontsize=9.5, color=MUTED, style="italic")
        # (b) the setting found on A, top right, one column aligned with the rows
        setting_column(ax, BX, TOP, SETTING)
        title(ax, TITLES["b"], BX + CW / 2, TOP, dy=1.05)
        ax.text(BX + CW / 2, TOP + NR + 0.15, NOTES["b"], ha="center", va="bottom", fontsize=9.5, color=MUTED, linespacing=1.15)
        # arrow (a) -> (b): the search
        y_search = TOP + 2.5
        arrow(ax, (W + 0.2, y_search), (BX - 0.2, y_search))
        ax.text((W + BX) / 2, y_search + 0.35, ARROWS["search"], ha="center", va="bottom", fontsize=9.5, color=MUTED, linespacing=1.15)
        # (b') the shuffled copy: narrower, faded, dashed outline, its muted words to its right
        if control:
            setting_column(ax, B2X, TOP, SHUFFLED, width=B2_WIDTH, faded=True)
            ax.add_patch(Rectangle((B2X - 0.08, TOP - 0.08), B2_WIDTH + 0.16, NR + 0.16, fill=False, edgecolor=MUTED,
                                   linewidth=1.2, linestyle=(0, (4, 3))))
            ax.text(B2_TEXT_X, TOP + NR, TITLES["b2"], ha="left", va="top", fontsize=HEAD, color=MUTED, linespacing=1.15)
            ax.text(B2_TEXT_X, TOP + NR - 1.15, NOTES["b2"], ha="left", va="top", fontsize=9.5, color=MUTED, linespacing=1.15)
        # arrow (b) -> (d): copied unchanged, blue, the most visible arrow; the column's blue note at its left, as the
        # aggregation schematic's "Copied to every recipient token", and the arrow's label at its right
        x_copy = BX + CW / 2
        y_from, y_to = TOP - 0.15, NR + TITLE_DY + 0.6
        arrow(ax, (x_copy, y_from), (x_copy, y_to), colour=BLUE, lw=3.0, scale=24)
        ax.text(x_copy - 0.3, TOP - 0.25, NOTES["b_under"], ha="right", va="top", fontsize=9.5, color=BLUE, linespacing=1.15)
        ax.text(x_copy + 0.3, (y_from + y_to) / 2, ARROWS["copied"], ha="left", va="center", fontsize=9.5, color=BLUE, linespacing=1.15)
        # (c) text B's labels, never searched, bottom left
        heat(ax, LABELS_B, TOKENS_B, 0, 0)
        row_names(ax, 0, 0, header=True)
        title(ax, TITLES["c"], W / 2, 0, dy=TITLE_DY)
        ax.text(W / 2, NR + 1.0, NOTES["c"], ha="center", va="bottom", fontsize=9.5, color=MUTED, style="italic")
        # (d) B's masks under A's setting, bottom right, with the check row
        mask_grid(ax, RX, 0, mask_cells(LABELS_B, SETTING))
        title(ax, TITLES["d"], RX + W / 2, 0, dy=TITLE_DY)
        check_row(ax, RX, CHECK, [True] * NC)
        # arrow (c) -> (d): B's labels set the floors
        y_floor = 2.5
        arrow(ax, (W + 0.2, y_floor), (RX - 0.2, y_floor))
        ax.text((W + RX) / 2, y_floor + 0.3, ARROWS["floors"], ha="center", va="bottom", fontsize=9.5, color=MUTED, linespacing=1.15)
        ax.text((W + RX) / 2, y_floor - 0.3, ARROWS["floors_rule"], ha="center", va="top", fontsize=8.5, color=MUTED, linespacing=1.15)
        # legend under (d), footer under (c)
        legend_items(ax, *LEGEND_XY, LEGEND)
        footer(ax, ((-4.1) + (RX - 0.3)) / 2, FOOTER_TOP - pad, text, va="top")  # centred left of the legend
        save(fig, ax, path, xlim, ylim)
    return Path(path)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for control in (True, False):
        p = draw_carry_over_schematic(OUT_DIR / OUT_NAMES[control], control=control)
        for q in (p, small_path(p)):
            print(f"wrote {q.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
