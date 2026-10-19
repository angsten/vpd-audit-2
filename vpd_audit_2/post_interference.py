"""Plans 4 and 7 of the research log: the post's Figure 3, the paper's interference picture as a toy, and two facts
measured on the released decomposition, drawn in the toy's terms.

    uv run python -m vpd_audit_2.post_interference

Rows (a) to (c) draw the paper's own toy picture (its lines 2017 to 2022 and the footnote at 1508): components inactive
on an input each contribute a little to the output; with all of them on the contributions cancel (a); an adversary that
keeps the contributions of one sign and switches off the rest makes them add up (b); on another input the contributions
point elsewhere, so the same switches cancel again (c), which is why the paper sets such masks aside.

Rows (d) and (e), under "Released Decomposition", are schematic: drawn in the toy's own terms, they stand for two facts
measured on the released decomposition, and no arrow in them is a measurement. Row (d) is row (b) again: the batch the
adversary searched, with its source applied. Row (e) is one unseen text with the same source: the same arrows, except
that one switched-off component (c4) flips its sign, tinted and marked by a pair of curved arrows, and the net arrow is
a little shorter. The two facts:
  - the sign agreement: 74 percent of the switched-off components keep their sign from the searched batch to unseen
    text, weighted by size (probe 1's deciding row, g-bar 0.7430, `results/s7_probe1/reading.txt`, line 9);
  - the kept share: at 320 steps a source keeps 95 percent of its own-batch damage on unseen text (the lead record's
    320-step retention pooled over all 80 settings, 0.9468, `results/s5_lead/analysis/lead_records.json`, printed as
    0.95 in `results/s5_lead/analysis/lead_tables.txt`, line 167). Row (e)'s net arrow is row (b)'s times that share,
    read by `kept_share()` and rounded to the two places the table prints.
An earlier form drew eight components sampled from probe 1's record, each at the toy's length; set in a row beside a net
arrow they read as a sum, which they were never meant to be, so the sample was dropped. The caption says the rows are
schematic; the chance level and the rest are in the caption too.

One PNG goes to `results/post/`, `figure3_interference.png`, with a copy at 50 percent of its pixel size, suffix _50, by
`post_small` (the post shows the copy). The figure has no footer: the caption carries its words.

The style is Figure 2's: its helpers and constants are imported from `post_schematic.py`, and `VERMILLION` from
`post_figure.py` (neither is changed). The figure is laid out at Figure 2's scale, so a data unit is the same size in the
saved image.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from vpd_audit_2.post_figure import VERMILLION
from vpd_audit_2.post_schematic import HEAD, INK, MUTED, OFF, OWN, RC, REFERENCE_INCHES_PER_UNIT, SPINE, _plt, arrow
from vpd_audit_2.post_small import save_small_copy, small_path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "results" / "post"
OUT_NAME = "figure3_interference.png"
COPY_SCALE = 0.5  # the reduced copy, as a share of the full size
LEAD_RECORD = REPO_ROOT / "results" / "s5_lead" / "analysis" / "lead_records.json"

# ----------------------------------------------------------------------------- the toy (the plan's table, one place)

CIRCUITS = [f"c{k}" for k in range(1, 9)]
PUSHES = {"input 1": [+1, -1, +1, -1, -1, +1, +1, -1], "input 2": [-1, +1, +1, -1, +1, +1, -1, -1]}
SWITCHES = [1, 0, 1, 0, 0, 1, 1, 0]  # the adversary's switches, found on input 1: the four + pushes on, the rest off
ALL_ON = [1] * 8
ROWS = {  # row: (input, switches)
    "a": ("input 1", ALL_ON),
    "b": ("input 1", SWITCHES),
    "c": ("input 2", SWITCHES),
}


def net_push(pushes: list[int], switches: list[int]) -> int:
    """The sum of the pushes of the circuits that are on."""
    return int(np.dot(pushes, switches))


def row_net_push(row: str) -> int:
    inp, sw = ROWS[row]
    return net_push(PUSHES[inp], sw)


# ----------------------------------------------------------------------------- the schematic rows (d) and (e)

FLIP = 3  # c4: the switched-off component whose sign flips between the searched batch (d) and the unseen text (e)
SCHEMATIC_SIGNS = {"d": list(PUSHES["input 1"]),  # row (b)'s arrows
                   "e": [+1 if j == FLIP else s for j, s in enumerate(PUSHES["input 1"])]}  # the same, c4 flipped
FLIP_FACE, FLIP_ARROW = "#deebf7", "#7fb2dc"  # the flipped cell's tint and arrow, and the curved arrows' colour


def kept_share(record_path: Path = LEAD_RECORD) -> dict:
    """The share of its own-batch added harm a source keeps on unseen text, pooled over all 80 of the lead run's 320-step
    sources: the lead record's 320-step retention, which `lead_tables.txt` prints in its 320-step row 9 (line 167) as
    "all 80 settings pooled 0.95". Returns the estimate and the value drawn, rounded to those two places."""
    steps = json.loads(Path(record_path).read_text())["main"]["step"]
    (step,) = [s for s in steps if s["key"] == 320]
    estimate = float(step["retention"]["pooled"]["estimate"])
    return {"estimate": estimate, "drawn": round(estimate, 2)}


# ----------------------------------------------------------------------------- the words

SECTIONS = ("The Paper's Picture", "Released Decomposition")
TITLES = {"a": "(a) Text A, Nothing\nSwitched Off", "b": "(b) Text A with Adversary's\nSource Applied",
          "c": "(c) Text B with Same\nSource Applied",
          "d": "(d) The Batch Searched with\nAdversary's Source Applied", "e": "(e) One Unseen Text with\nSame Source Applied"}
READINGS = {"a": "Contributions Cancel", "b": "Contributions Add Up", "c": "Contributions Cancel Again"}
NET_HEADER = "Net Contribution\nto the Output"
# Beside rows (d) and (e), as beside rows (a) to (c); the unseen text's in vermilion.
MEASURED_READINGS = {"d": "Contributions Add Up", "e": "Contributions Add Up"}
MEASURED_READING_COLOURS = {"d": MUTED, "e": VERMILLION}
LEGEND_A = [("on", "Component On"), ("off", "Switched Off by Adversary")]
LEGEND_B = [("push", "Contribution to the Output"), ("net", "Net Contribution")]

# ----------------------------------------------------------------------------- the layout (data units, Figure 2's scale)

CW3 = 0.9  # cell width (Figure 2's is 1.7: eight cells and the net column must fit the post's column)
RH = 1.0  # cell height, as Figure 2's
PUSH = 0.45  # a component's arrow, in data units; the net arrow is the net push times this
NET_X0 = 8 * CW3 + 0.35  # the net column
NET_W = 2.3
NET_ORIGIN = NET_X0 + 0.2  # every net arrow starts here; a zero net push is a dot here
NET_HEADER_INSET = 0.08  # the net column's header starts this far left of NET_ORIGIN, over the dots and arrow tails
READ_X = NET_X0 + NET_W + 0.35  # the readings, left-aligned
READ_W = 6.45  # the readings' column, which sets the figure's right edge
TITLE_X = -1.05  # the row titles, right-aligned
BRACKET_X = -7.55  # the section brackets at the far left
ROW_TOP = {"a": 0.0, "b": -1.5, "c": -3.0, "d": -6.45, "e": -7.95}  # each row's top edge
RULE_Y = -5.0  # the hairline between the paper's picture and the released decomposition, a full row below row (c)
SECTION_LABEL_Y = {SECTIONS[0]: 0.2, SECTIONS[1]: RULE_Y - 0.48}  # "Released Decomposition" below the rule, not touching it
D_BOTTOM = ROW_TOP["e"] - 1.3  # the bottom of the lower section's bracket
FLIP_INSET = 0.25  # the curved arrows run this far inside c4's column, one at each side
FLIP_GAP = 0.2  # and start and end this far from the two rows' middles
XLIM = (BRACKET_X - 0.1, READ_X + READ_W)
LEGEND_Y = D_BOTTOM - 0.85  # the first legend row's swatch bottom
LEGEND_X = (BRACKET_X + 0.6, BRACKET_X + 7.4)
BOTTOM_TOP = LEGEND_Y - 0.3  # just under the legend's first row, the top of the margin at the figure's foot (no footer)


def _cell(ax, x, y, on, glyph=None, push=0, face=None, arrow_colour=None):
    """One circuit's cell: the first post's on (grey) or off (light) shading, holding its push arrow (or a glyph, which no
    row uses). `face` and `arrow_colour`, if given, replace the shading and the arrow's colour (row (e)'s flipped cell)."""
    from matplotlib.patches import Rectangle

    ax.add_patch(Rectangle((x, y), CW3, RH, facecolor=face or (OWN if on else OFF), edgecolor="white", linewidth=2))
    cx, cy = x + CW3 / 2, y + RH / 2
    if glyph is not None:
        ax.text(cx, cy, glyph, ha="center", va="center", fontsize=12, color="white" if on else MUTED, fontweight="bold")
        return
    colour = arrow_colour or (INK if on else "#c8c8c8")
    arrow(ax, (cx - push * PUSH / 2, cy), (cx + push * PUSH / 2, cy), colour=colour, lw=1.6, scale=10)


def _net(ax, y, value):
    cy = y + RH / 2
    if value == 0:
        ax.plot([NET_ORIGIN], [cy], marker="o", markersize=6, color=VERMILLION, linestyle="none")
    else:
        arrow(ax, (NET_ORIGIN, cy), (NET_ORIGIN + value * PUSH, cy), colour=VERMILLION, lw=3.2, scale=20)


def _bracket(ax, x, y_top, y_bottom, colour, lw):
    ax.plot([x + 0.18, x, x, x + 0.18], [y_top, y_top, y_bottom, y_bottom], color=colour, linewidth=lw, solid_capstyle="butt")


def _legend(ax, x_a, x_b, y):
    """Two columns of swatches, as the first post's legend: cells at the left, the drawn quantities at the right."""
    from matplotlib.patches import Rectangle

    for k, (kind, label) in enumerate(LEGEND_A):
        yy = y - 0.6 * k
        fc = OFF if kind == "off" else OWN
        ax.add_patch(Rectangle((x_a, yy), 0.42, 0.42, facecolor=fc, edgecolor=SPINE, linewidth=0.6))
        ax.text(x_a + 0.6, yy + 0.21, label, va="center", fontsize=9.5, color=INK)
    for k, (kind, label) in enumerate(LEGEND_B):
        yy = y - 0.6 * k + 0.21
        if kind == "push":
            arrow(ax, (x_b, yy), (x_b + PUSH, yy), colour=INK, lw=1.6, scale=10)
        else:  # "net"
            arrow(ax, (x_b, yy), (x_b + 0.75, yy), colour=VERMILLION, lw=3.2, scale=16)
        ax.text(x_b + 0.95, yy, label, va="center", fontsize=9.5, color=INK)


def _draw_rows(ax):
    # the header: component names over the cells, and the net column's, left-aligned with the dots and arrow tails below it
    for j, name in enumerate(CIRCUITS):
        ax.text((j + 0.5) * CW3, 0.15, name, ha="center", va="bottom", fontsize=11, color=INK, fontweight="bold")
    ax.text(NET_ORIGIN - NET_HEADER_INSET, 0.15, NET_HEADER, ha="left", va="bottom", fontsize=10.5, color=INK, linespacing=1.1)
    # the toy rows
    for row in ("a", "b", "c"):
        inp, sw = ROWS[row]
        y = ROW_TOP[row] - RH
        for j in range(8):
            _cell(ax, j * CW3, y, bool(sw[j]), push=PUSHES[inp][j])
        _net(ax, y, row_net_push(row))
        ax.text(READ_X, y + RH / 2, READINGS[row], ha="left", va="center", fontsize=9.5, color=MUTED)
        ax.text(TITLE_X, y + RH / 2, TITLES[row], ha="right", va="center", fontsize=10.5, color=INK, linespacing=1.1)
    # the schematic rows: (d) the searched batch, row (b)'s arrows; (e) one unseen text, the same with c4 flipped and
    # tinted; each with a net arrow (row (b)'s net push, times the kept share on the unseen text) and a reading
    share = {"d": 1.0, "e": kept_share()["drawn"]}
    for row in ("d", "e"):
        y = ROW_TOP[row] - RH
        for j, sign in enumerate(SCHEMATIC_SIGNS[row]):
            if row == "e" and j == FLIP:
                _cell(ax, j * CW3, y, False, push=sign, face=FLIP_FACE, arrow_colour=FLIP_ARROW)
            else:
                _cell(ax, j * CW3, y, bool(SWITCHES[j]), push=sign)
        _net(ax, y, row_net_push("b") * share[row])
        ax.text(READ_X, y + RH / 2, MEASURED_READINGS[row], ha="left", va="center", fontsize=9.5, color=MEASURED_READING_COLOURS[row])
        ax.text(TITLE_X, y + RH / 2 + 0.02, TITLES[row], ha="right", va="center", fontsize=10.5, color=INK, linespacing=1.1)
    # a pair of curved arrows between row (d)'s c4 and row (e)'s, inside the column: down at the left, up at the right
    xl, xr = FLIP * CW3 + FLIP_INSET, (FLIP + 1) * CW3 - FLIP_INSET
    y_top, y_bot = ROW_TOP["d"] - RH / 2 - FLIP_GAP, ROW_TOP["e"] - RH / 2 + FLIP_GAP
    arrow(ax, (xl, y_top), (xl, y_bot), colour=FLIP_ARROW, lw=1.2, rad=0.3, scale=8)
    arrow(ax, (xr, y_bot), (xr, y_top), colour=FLIP_ARROW, lw=1.2, rad=0.3, scale=8)
    # the section brackets and the hairline between them
    _bracket(ax, BRACKET_X, ROW_TOP["a"], RULE_Y + 0.25, MUTED, 1.0)
    _bracket(ax, BRACKET_X, ROW_TOP["d"], D_BOTTOM, MUTED, 1.0)
    ax.plot([BRACKET_X, READ_X + READ_W], [RULE_Y, RULE_Y], color=MUTED, linewidth=0.5)
    ax.text(BRACKET_X, SECTION_LABEL_Y[SECTIONS[0]], SECTIONS[0], ha="left", va="bottom", fontsize=HEAD, color=INK)
    ax.text(BRACKET_X, SECTION_LABEL_Y[SECTIONS[1]], SECTIONS[1], ha="left", va="top", fontsize=HEAD, color=INK)


def draw_interference(path: Path) -> Path:
    """The figure: the toy rows (a) to (c), the schematic rows (d) and (e), and the legend; and its 50 percent copy
    beside it."""
    plt = _plt()
    s = REFERENCE_INCHES_PER_UNIT
    # the frame's foot: below BOTTOM_TOP, the height of a one-line text box at 10 points with a 0.6 pad and 0.25 more,
    # which clears the legend's second row (the figure has no footer; the caption carries its words)
    margin = (10 * 1.2 / 72) / s + 2 * (0.6 * 10 / 72 / s)
    ylim = (BOTTOM_TOP - margin - 0.25, 1.3)
    width = (XLIM[1] - XLIM[0]) * s
    height = (ylim[1] - ylim[0]) * s
    with plt.rc_context(RC):
        fig = plt.figure(figsize=(width, height))
        ax = fig.add_axes([0, 0, 1, 1])  # one data unit = s inches
        ax.set_xlim(*XLIM)
        ax.set_ylim(*ylim)
        ax.axis("off")
        _draw_rows(ax)
        _legend(ax, *LEGEND_X, LEGEND_Y)
        fig.savefig(path, facecolor="white", bbox_inches="tight", dpi=200)
        plt.close(fig)
    save_small_copy(path, COPY_SCALE)
    return Path(path)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = draw_interference(OUT_DIR / OUT_NAME)
    for q in (p, small_path(p, COPY_SCALE)):
        print(f"wrote {q.relative_to(REPO_ROOT).as_posix()}")
    print("net pushes:", {r: row_net_push(r) for r in ("a", "b", "c")}, "| schematic signs:", SCHEMATIC_SIGNS,
          "| kept share:", kept_share())
    return 0


if __name__ == "__main__":
    sys.exit(main())
