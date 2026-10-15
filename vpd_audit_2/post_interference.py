"""Session 7, plans 4 and 7: the post's Figure 3, the paper's interference picture as a toy, and what we measured.

    uv run python -m vpd_audit_2.post_interference

Rows (a) to (c) draw the paper's own toy picture (its lines 2017 to 2022 and the footnote at 1508): circuits inactive on
an input each push the output a little; with all of them on the pushes cancel (a); an adversary that keeps the pushes
pointing one way and switches off the rest makes them add up (b); on another input the pushes point elsewhere, so the
same switches cancel again (c), which is why the paper sets such masks aside. Row (d) is what we measured: the same
switches on text they never saw, its output's damage drawn as two blue bars on their own scale (session 5: 78 to 95
percent of the damage carries over), and, since plan 7, eight real components' first-order pushes measured by probe 1
(plan 5) on one unseen text, in place of the question marks.

Row (d)'s arrows (plan 7). The eight components, whether each is off or kept, and their signs are read from probe 1's
record (`results/s7_probe1/record.json`, "row_d"), never typed here: four from the setting's off set in its off cells,
four from the matched kept set in its on cells, in the record's order, placed in the toy's switch pattern so that row
(d) keeps "the same switches". Each arrow is drawn as the component's push while on, which is the NEGATIVE of the
measured switch-off push; every arrow has the toy's length, so only its direction is a measurement. Rightward points
along the full pattern's shift on that text, toward the damage. The three numbers beside them come from the same record
(the off set's raw agreement, the permutation chance level, the kept components' agreement, and the additivity ratio, at
320 steps), and a caption note with all of it goes to `results/post/figure3_row_d.txt`.

Two PNGs go to `results/post/` (each also as a copy at 75 percent of its pixel size, suffix _75, by `post_small`):
`figure3_interference.png` (variant A, the four rows) and
`figure3_interference_with_dose.png` (variant B, with a panel (e) of session 6's dose-response at 320 steps, read from
`results/s6_followups/record.json`).

The style is Figure 2's: its helpers and constants are imported from `post_schematic.py`, and `VERMILLION` and
`style_axes` from `post_figure.py` (neither is changed). The figure is laid out at Figure 2's scale, so a data unit is the
same size in the saved image.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import numpy as np

from vpd_audit_2.post_figure import VERMILLION, style_axes
from vpd_audit_2.post_schematic import BLUE, HEAD, INK, MUTED, OFF, OWN, RC, REFERENCE_INCHES_PER_UNIT, SPINE, _plt, arrow, footer
from vpd_audit_2.post_small import save_small_copy, small_path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "results" / "post"
OUT_NAMES = {"a": "figure3_interference.png", "b": "figure3_interference_with_dose.png"}
DOSE_RECORD = REPO_ROOT / "results" / "s6_followups" / "record.json"
PROBE_RECORD = REPO_ROOT / "results" / "s7_probe1" / "record.json"
ROW_D_NOTE_NAME = "figure3_row_d.txt"

# ----------------------------------------------------------------------------- the toy (the plan's table, one place)

CIRCUITS = [f"c{k}" for k in range(1, 9)]
PUSHES = {"input 1": [+1, -1, +1, -1, -1, +1, +1, -1], "input 2": [-1, +1, +1, -1, +1, +1, -1, -1]}
SWITCHES = [1, 0, 1, 0, 0, 1, 1, 0]  # the adversary's switches, found on input 1: the four + pushes on, the rest off
ALL_ON = [1] * 8
ROWS = {  # row: (input, switches, measured)
    "a": ("input 1", ALL_ON, False),
    "b": ("input 1", SWITCHES, False),
    "c": ("input 2", SWITCHES, False),
    "d": ("input 2", SWITCHES, True),
}


def net_push(pushes: list[int], switches: list[int]) -> int:
    """The sum of the pushes of the circuits that are on."""
    return int(np.dot(pushes, switches))


def row_net_push(row: str) -> int:
    inp, sw, _ = ROWS[row]
    return net_push(PUSHES[inp], sw)


# Row (d)'s two bars, in their own units: the damage where the pattern was found (1.0) and on text it never saw (0.9, within
# session 5's 78 to 95 percent). They do not depend on the toy's pushes.
MEASURED_BARS = (1.0, 0.9)


def measured_bar_lengths() -> tuple[float, float]:
    return MEASURED_BARS


# ----------------------------------------------------------------------------- row (d)'s measured pushes (plan 7)

FRACTION_WORDS = {0.25: "a quarter", 0.5: "a half", 0.75: "three quarters", 1.0: "all"}


def row_d_components(record_path: Path = PROBE_RECORD) -> list[dict]:
    """Probe 1's eight row-(d) components, from its record, each with its name, its cell ("off" or "on"), the measured
    switch-off push on the text, and the drawn sign: the push while on, the negative of the switch-off push. Refuses
    unless there are four of each kind and the record's own drawn sign is that negative."""
    rec = json.loads(Path(record_path).read_text())["row_d"]
    out = []
    for c in rec["components"]:
        sign = -int(np.sign(c["switch_off_push_on_text"]))
        if sign != int(c["drawn_arrow_on_text"]) or sign == 0:
            raise ValueError("the record's drawn sign is not the negative of its switch-off push")
        out.append({"name": f"{c['module']} {c['component']}", "cell": c["cell"], "switch_off_push": float(c["switch_off_push_on_text"]),
                    "drawn_sign": sign})
    if [c["cell"] for c in out].count("off") != 4 or [c["cell"] for c in out].count("on") != 4:
        raise ValueError("row (d) needs four off and four kept components")
    return out


def row_d_cells(components: list[dict], switches: list[int] = SWITCHES) -> list[dict]:
    """The eight components in the toy's switch pattern: the kept ones, in the record's order, in the on cells, the off
    ones in the off cells."""
    on = [c for c in components if c["cell"] == "on"]
    off = [c for c in components if c["cell"] == "off"]
    if sum(switches) != len(on) or len(switches) - sum(switches) != len(off):
        raise ValueError("the switch pattern does not hold four on and four off")
    it_on, it_off = iter(on), iter(off)
    return [next(it_on) if s else next(it_off) for s in switches]


def _fraction_word(x: float) -> str:
    q = round(x * 4) / 4
    return FRACTION_WORDS.get(q, f"{round(100 * x)} percent")


def row_d_numbers(record_path: Path = PROBE_RECORD) -> dict:
    """The numbers printed beside row (d), from the record's 320-step row: the off set's raw agreement, the chance level of
    a permutation of the off set's signs (the post-hoc baseline), the kept components' agreement (the pre-registered
    chance level), and the additivity ratio, as percents and a fraction word."""
    r = json.loads(Path(record_path).read_text())["rows"]["n320"]
    raw = float(r["g_bar"])
    perm = float(r["post_hoc_permutation_baseline"]["g0_bar"])
    kept = float(r["g0_bar"])
    add = float(r["additivity"]["off_set"])
    return {"raw": raw, "permutation_chance": perm, "kept": kept, "additivity": add, "raw_pct": round(100 * raw), "perm_pct": round(100 * perm),
            "kept_pct": round(100 * kept), "additivity_word": _fraction_word(add)}


def row_d_lines(numbers: dict) -> tuple[str, str, str]:
    return (f"{numbers['raw_pct']}% keep their direction from the searched batch (chance about {numbers['perm_pct']}%)",
            f"components left on: also {numbers['kept_pct']}%" if numbers["kept_pct"] == numbers["raw_pct"] else f"components left on: {numbers['kept_pct']}%",
            f"their first-order sum: about {numbers['additivity_word']} of the shift")


D_LINES_WIDTH = 34  # characters: the readings' column, whose widest line is "damage where the pattern was found"


def row_d_blocks(lines: tuple[str, str, str]) -> list[str]:
    """The three lines as drawn: each wrapped to the readings' column, so that the figure keeps its width."""
    return [textwrap.fill(x, D_LINES_WIDTH) for x in lines]


def row_d_note(record_path: Path = PROBE_RECORD) -> str:
    """The caption note for row (d): the arrows' convention, the eight components as drawn, and the numbers' sources."""
    rec = json.loads(Path(record_path).read_text())
    st, tx = rec["row_d"]["setting"], rec["row_d"]["text"]
    cells = row_d_cells(row_d_components(record_path))
    n = row_d_numbers(record_path)
    L = ["Figure 3, row (d): caption note (session 7, plan 7). Written by vpd_audit_2/post_interference.py from results/s7_probe1/record.json.",
         "",
         "Each arrow in row (d) is a real component's first-order push measured by probe 1 on one unseen text, drawn as the push",
         "WHILE ON: the negative of the measured effect of switching it off. Rightward points along the full pattern's shift on",
         "that text, toward the damage. Every arrow has the toy's length; only its direction is measured.",
         f"Setting: {st['attack']} from start {st['start']} at 320 steps (its kappa {st['kappa']:.4f}, the lower median of the 80); "
         f"text {tx['text_id']}, {tx['batch']} position {tx['index']} (its agreement {tx['g']:.4f}, the lower median of the setting's 2,048).",
         "Four switched-off components (off cells) and four kept components (on cells), drawn with probability proportional to",
         "their push on that text (plan 5, amendment 6).",
         "",
         "As drawn, left to right (cell, component, measured switch-off push, drawn arrow):"]
    for k, c in enumerate(cells, start=1):
        L.append(f"  {k}. {'off ' if c['cell'] == 'off' else 'kept'}  {c['name']:<22}  {c['switch_off_push']:+.4e}  {'right (+)' if c['drawn_sign'] > 0 else 'left (-)'}")
    L += ["",
          "Beside the arrows:"] + [f"  {x}" for x in row_d_lines(n)] + [
          "",
          f"Sources, 320-step row of the record: off-set agreement g_bar {n['raw']:.4f}; permutation chance (post hoc, "
          f"post_hoc_permutation_baseline.g0_bar) {n['permutation_chance']:.4f}; kept components' agreement (the pre-registered chance, "
          f"g0_bar) {n['kept']:.4f}; additivity ratio (additivity.off_set) {n['additivity']:.4f}."]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- the dose-response (variant B)

DOSE_FRACTIONS = (0.25, 0.5, 0.75, 0.9, 1.0)
# sessions/006/checkpoint.md, Section 6.3, "Share of the harm kept, by fraction of the off set switched off", 320-step row.
CHECKPOINT_DOSE_320 = (0.00, 0.01, 0.04, 0.42, 1.02)


def dose_response_320(record_path: Path = DOSE_RECORD) -> tuple[float, ...]:
    """Session 6's kept shares at 320 steps, at full precision, from its saved record ("dose_rounded", row "n320"). Each is a
    share of the unrounded setting's added harm; the fraction 1 is the rounded setting. Refuses if they do not round to the
    checkpoint's table."""
    rec = json.loads(Path(record_path).read_text())["dose_rounded"]["rows"]["n320"]
    keys = {0.25: "0.25", 0.5: "0.5", 0.75: "0.75", 0.9: "0.9", 1.0: "1"}
    values = tuple(float(rec[keys[f]]["kept_share"]) for f in DOSE_FRACTIONS)
    if tuple(round(v, 2) for v in values) != CHECKPOINT_DOSE_320:
        raise ValueError("the saved dose-response does not round to the checkpoint's table")
    return values


def dose_points(values: tuple[float, ...]) -> tuple[float, ...]:
    """The points the panel plots: the saved shares as recorded, none renormalized, the whole rounded set's 1.02 included
    (the head, after plan 4's report 1), so that every number matches the checkpoint's table."""
    return tuple(values)


# ----------------------------------------------------------------------------- the words

TITLES = {"a": "(a) Input 1, every\ninactive circuit on", "b": "(b) Input 1, the\nadversary's switches",
          "c": "(c) Input 2, the same switches,\nas the paper expects", "d": "(d) Input 2, the same switches,\nas we measured"}
D_NOTE = "first-order pushes, measured on one unseen text"
D_NOTE_DRAWN = "first-order pushes, measured\non one unseen text"  # on two lines: on one it runs into the section bracket
READINGS = {"a": "the small pushes cancel", "b": "keep the pushes that point one way,\ndrop the rest: they add up",
            "c": "the pushes point elsewhere now, so\nthe same switches cancel again", "d": "the output is damaged\nnearly as much"}
QUOTES = {"b": "“ablate all inactive circuits which contribute noise with a negative sign,\nbut keep all ... with a positive sign”",
          "c": "“not a very effective adversarial mask on other inputs”;\n“exponentially rare edge cases”"}
BAR_LABELS = ("damage where the pattern was found", "damage on text it never saw:\n78 to 95 percent of that (Figure 1)")
NET_HEADER = "net push on\nthe output"
MEASURED_HEADER = "measured damage"  # row (d)'s bars' own heading, in the net column just below the hairline
SECTIONS = ("The paper's picture", "What we measured")
BRACE = "same switches"
LEGEND_A = [("on", "circuit on"), ("off", "switched off by the adversary"),
            ("measured", "a component's first-order push, measured,\ndrawn as the push while on")]
LEGEND_B = [("push", "a circuit's push on the output, in the paper's toy picture"), ("net", "net push, the toy's quantity"),
            ("bar", "damage we measured, KL from the original model, a different quantity")]
FOOTER = ("The paper's picture (a to c): a switch pattern tuned to one input does little on another: an exponentially "
          "rare edge case, not a flaw. Measured on the released decomposition (d): the same pattern damages text it never saw "
          "nearly as much, and its components' pushes mostly keep their direction there.")
FOOTER_LINES = 3
PANEL_TITLE = "(e) How the damage builds, measured at the output (post hoc)"
PANEL_X = "fraction of the pattern's switch-offs applied, chosen at random,\nthe rest of the model fully on"
PANEL_Y = "share of the\nsetting's damage"  # on two lines: on one it is longer than the half-height axes
PANEL_SERIES = "measured, 320-step patterns"
PANEL_BAND = ("if the pushes simply added", "shift in proportion to the count;\ndamage between linear and square\nin the shift")
PANEL_NOTE = "Three quarters of the pattern does 4 percent of the damage; it arrives almost all at once."
DOSE_TICKS = (0.25, 0.5, 0.75, 0.9, 1.0)


def footer_text() -> str:
    """The footer in `FOOTER_LINES` lines, as even as that allows."""
    w = len(FOOTER)
    while len(textwrap.wrap(FOOTER, w - 1)) <= FOOTER_LINES:
        w -= 1
    return textwrap.fill(FOOTER, w)


# ----------------------------------------------------------------------------- the layout (data units, Figure 2's scale)

CW3 = 0.9  # cell width (Figure 2's is 1.7: eight cells and the net column must fit the post's column)
RH = 1.0  # cell height, as Figure 2's
PUSH = 0.45  # a circuit's push arrow, in data units; the net arrow is the net push times this
NET_X0 = 8 * CW3 + 0.35  # the net column
NET_W = 2.3
NET_ORIGIN = NET_X0 + 0.2  # every net arrow starts here; a zero net push is a dot here
BAR_SCALE = 1.95  # data units per unit of row (d)'s bars (their own scale, not the pushes')
BAR_H = 0.28
BAR_CENTRES = (-0.2, -0.85)  # row (d)'s two bars, below the row's top edge
READ_X = NET_X0 + NET_W + 0.35  # the readings, left-aligned
READ_W = 6.45  # the readings' column: its widest line, "damage where the pattern was found", is 6.4 units
TITLE_X = -1.05  # the row titles, right-aligned
BRACE_X = -0.4  # the blue "same switches" bracket
BRACKET_X = -7.55  # the section brackets at the far left
ROW_TOP = {"a": 0.0, "b": -1.5, "c": -3.65, "d": -6.75}  # each row's top edge
QUOTE_GAP = 0.15  # the quotes' top below their row
RULE_Y = -5.8  # the hairline between the paper's picture and the measurement
SECTION_LABEL_Y = {"The paper's picture": 0.2, "What we measured": RULE_Y - 0.12}
D_BOTTOM = ROW_TOP["d"] - 4.7  # the bottom of row (d)'s words: its reading under the bar labels, then the three measured lines
D_LINES_GAP = 0.2  # between row (d)'s reading and its three measured lines
D_ITEM_GAP = 0.08  # between those three lines, each wrapped to the column
LINE_9 = 9 * 1.15 / 72 / REFERENCE_INCHES_PER_UNIT  # one 9-point line at spacing 1.15, in data units


def _cell(ax, x, y, on, glyph=None, push=0):
    """One circuit's cell: the first post's on (grey) or off (light) shading, holding its push arrow (or a glyph, which no
    row uses since plan 7 replaced row (d)'s question marks with measured pushes)."""
    from matplotlib.patches import Rectangle

    ax.add_patch(Rectangle((x, y), CW3, RH, facecolor=OWN if on else OFF, edgecolor="white", linewidth=2))
    cx, cy = x + CW3 / 2, y + RH / 2
    if glyph is not None:
        ax.text(cx, cy, glyph, ha="center", va="center", fontsize=12, color="white" if on else MUTED, fontweight="bold")
        return
    colour = INK if on else "#c8c8c8"
    arrow(ax, (cx - push * PUSH / 2, cy), (cx + push * PUSH / 2, cy), colour=colour, lw=1.6, scale=10)


def _net(ax, y, value):
    cy = y + RH / 2
    if value == 0:
        ax.plot([NET_ORIGIN], [cy], marker="o", markersize=6, color=VERMILLION, linestyle="none")
    else:
        arrow(ax, (NET_ORIGIN, cy), (NET_ORIGIN + value * PUSH, cy), colour=VERMILLION, lw=3.2, scale=20)


def _bars(ax, y):
    """Row (d)'s measurement: two blue bars on their own scale, labelled at their right."""
    from matplotlib.patches import Rectangle

    full, carried = measured_bar_lengths()
    ys = tuple(y + RH + c for c in BAR_CENTRES)  # the bars' centres
    for (length, alpha), yc, label in zip(((full, 0.35), (carried, 1.0)), ys, BAR_LABELS):
        ax.add_patch(Rectangle((NET_ORIGIN, yc - BAR_H / 2), length * BAR_SCALE, BAR_H, facecolor=BLUE, alpha=alpha, linewidth=0))
        ax.text(READ_X, yc, label, ha="left", va="center", fontsize=9, color=BLUE, linespacing=1.15)


def _bracket(ax, x, y_top, y_bottom, colour, lw):
    ax.plot([x + 0.18, x, x, x + 0.18], [y_top, y_top, y_bottom, y_bottom], color=colour, linewidth=lw, solid_capstyle="butt")


def _legend(ax, x_a, x_b, y):
    """Two columns of swatches, as the first post's legend: cells at the left, the drawn quantities at the right."""
    from matplotlib.patches import Rectangle

    for k, (kind, label) in enumerate(LEGEND_A):
        yy = y - 0.6 * k
        fc = OFF if kind == "off" else OWN
        ax.add_patch(Rectangle((x_a, yy), 0.42, 0.42, facecolor=fc, edgecolor=SPINE, linewidth=0.6))
        if kind == "measured":  # a small arrow, as row (d) draws them
            arrow(ax, (x_a + 0.07, yy + 0.21), (x_a + 0.35, yy + 0.21), colour=INK, lw=1.3, scale=8)
        if "\n" in label:  # a two-line label hangs from its swatch's top, clear of the row above
            ax.text(x_a + 0.6, yy + 0.42, label, va="top", fontsize=9.5, color=INK, linespacing=1.1)
        else:
            ax.text(x_a + 0.6, yy + 0.21, label, va="center", fontsize=9.5, color=INK)
    for k, (kind, label) in enumerate(LEGEND_B):
        yy = y - 0.6 * k + 0.21
        if kind == "push":
            arrow(ax, (x_b, yy), (x_b + PUSH, yy), colour=INK, lw=1.6, scale=10)
        elif kind == "net":
            arrow(ax, (x_b, yy), (x_b + 0.75, yy), colour=VERMILLION, lw=3.2, scale=16)
        else:
            ax.add_patch(Rectangle((x_b, yy - BAR_H / 2), 0.75, BAR_H, facecolor=BLUE, linewidth=0))
        ax.text(x_b + 0.95, yy, label, va="center", fontsize=9.5, color=INK)


def _draw_rows(ax, record_path: Path = PROBE_RECORD):
    # the header: circuit names over the cells, and the net column's
    for j, name in enumerate(CIRCUITS):
        ax.text((j + 0.5) * CW3, 0.15, name, ha="center", va="bottom", fontsize=11, color=INK, fontweight="bold")
    ax.text(NET_X0 + NET_W / 2, 0.15, NET_HEADER, ha="center", va="bottom", fontsize=10.5, color=INK, linespacing=1.1)
    for row, (inp, sw, measured) in ROWS.items():
        y = ROW_TOP[row] - RH
        if measured:  # plan 7: the probe's eight components, their drawn sign the push while on (the record's, flipped)
            cells = row_d_cells(row_d_components(record_path), sw)
            for j, c in enumerate(cells):
                _cell(ax, j * CW3, y, c["cell"] == "on", push=c["drawn_sign"])
        else:
            for j in range(8):
                _cell(ax, j * CW3, y, bool(sw[j]), push=PUSHES[inp][j])
        if measured:
            _bars(ax, y)
            ax.text(READ_X, y - 0.45, READINGS[row], ha="left", va="top", fontsize=9, color=MUTED, linespacing=1.15)
            yy = y - 0.45 - (READINGS[row].count("\n") + 1) * LINE_9 - D_LINES_GAP
            for block in row_d_blocks(row_d_lines(row_d_numbers(record_path))):
                ax.text(READ_X, yy, block, ha="left", va="top", fontsize=9, color=MUTED, linespacing=1.15)
                yy -= (block.count("\n") + 1) * LINE_9 + D_ITEM_GAP
            # the title a little below the row's middle, clear of the section bracket's top, with the note under it
            ax.text(TITLE_X, y + RH / 2 + 0.02, TITLES[row], ha="right", va="center", fontsize=10.5, color=INK, linespacing=1.1)
            ax.text(TITLE_X, y - 0.06, D_NOTE_DRAWN, ha="right", va="top", fontsize=9, color=MUTED, style="italic", linespacing=1.1)
        else:
            _net(ax, y, row_net_push(row))
            ax.text(READ_X, y + RH / 2, READINGS[row], ha="left", va="center", fontsize=9, color=MUTED, linespacing=1.15)
            ax.text(TITLE_X, y + RH / 2, TITLES[row], ha="right", va="center", fontsize=10.5, color=INK, linespacing=1.1)
        if row in QUOTES:
            ax.text(0, y - QUOTE_GAP, QUOTES[row], ha="left", va="top", fontsize=8.5, color=MUTED, linespacing=1.15)
    # the blue "same switches" bracket over the switch rows (b) to (d)
    top, bottom = ROW_TOP["b"], ROW_TOP["d"] - RH
    _bracket(ax, BRACE_X, top, bottom, BLUE, 2.2)
    ax.text(BRACE_X - 0.18, (top + bottom) / 2, BRACE, ha="right", va="center", rotation=90, fontsize=9.5, color=BLUE)
    # the section brackets and the hairline between them, broken where the blue bracket and its words cross it
    _bracket(ax, BRACKET_X, ROW_TOP["a"], RULE_Y + 0.25, MUTED, 1.0)
    _bracket(ax, BRACKET_X, ROW_TOP["d"], D_BOTTOM, MUTED, 1.0)
    for x0, x1 in ((BRACKET_X, BRACE_X - 0.75), (BRACE_X + 0.3, READ_X + READ_W)):
        ax.plot([x0, x1], [RULE_Y, RULE_Y], color=MUTED, linewidth=0.5)
    # row (d)'s bars get their own heading, so they do not sit under "net push on the output"
    ax.text(NET_X0 + NET_W / 2, RULE_Y - 0.15, MEASURED_HEADER, ha="center", va="top", fontsize=10, color=BLUE)
    ax.text(BRACKET_X, SECTION_LABEL_Y[SECTIONS[0]], SECTIONS[0], ha="left", va="bottom", fontsize=HEAD, color=INK)
    ax.text(BRACKET_X, SECTION_LABEL_Y[SECTIONS[1]], SECTIONS[1], ha="left", va="top", fontsize=HEAD, color=INK)


XLIM = (BRACKET_X - 0.1, READ_X + READ_W)
LEGEND_Y = D_BOTTOM - 0.85  # the first legend row's swatch bottom
LEGEND_X = (BRACKET_X + 0.6, BRACKET_X + 9.4)  # plan 7: the right column 1.8 units further right, clear of the measured-push label
FOOTER_TOP = LEGEND_Y - 1.2 - 0.75  # plan 7: 0.3 lower, under the legend's two-line last label
# inches: panel (e) under the footer, its axes half the height of report 1's (2.5) so that it does not outweigh the rows
PANEL = {"title_gap": 0.45, "axes_w": 5.6, "axes_h": 1.25, "below": 1.2}
PANEL_NOTE_BELOW_PT = 50  # the note's top, in points below the axes: under the tick labels and the two-line x label


def _panel(fig, x_in, y_in, values):
    """Panel (e), in Figure 1's axis style: the measured dose-response and the band of what adding pushes would give."""
    w, h = PANEL["axes_w"], PANEL["axes_h"]
    W, H = fig.get_size_inches()
    ax = fig.add_axes([x_in / W, y_in / H, w / W, h / H])
    f = np.linspace(0.2, 1.0, 200)
    ax.fill_between(f, f ** 2, f, color="#e6e6e6", linewidth=0, zorder=0)
    pts = dose_points(values)
    ax.plot(DOSE_FRACTIONS, pts, color=BLUE, linewidth=2, marker="o", markersize=6, markeredgewidth=0, zorder=3)
    ax.text(0.45, 0.06, PANEL_SERIES, ha="left", va="bottom", fontsize=9, color=BLUE)  # between the curve's flat part and the band
    ax.text(0.22, 1.05, PANEL_BAND[0], ha="left", va="top", fontsize=9, color=MUTED)
    ax.text(0.22, 0.91, PANEL_BAND[1], ha="left", va="top", fontsize=8, color=MUTED, linespacing=1.15)
    ax.plot([0.37, 0.42], [0.53, 0.30], color=MUTED, linewidth=0.6)  # a leader from the band's words into the band
    ax.set_xlim(0.2, 1.03)
    ax.set_ylim(0, 1.1)  # the whole rounded set's 1.02 and its marker inside the axes
    ax.set_xticks(list(DOSE_TICKS))
    ax.set_xticklabels([f"{t:g}" for t in DOSE_TICKS])
    ax.set_yticks([0, 0.5, 1.0])  # three ticks on the half-height axes
    ax.set_yticklabels(["0", "0.5", "1"])
    ax.set_xlabel(PANEL_X, color=INK, fontsize=10.5, linespacing=1.15)
    ax.set_ylabel(PANEL_Y, color=INK, fontsize=10.5)
    style_axes(ax)
    return ax


def draw_interference(path: Path, variant: str = "a", record_path: Path = DOSE_RECORD, probe_record: Path = PROBE_RECORD) -> Path:
    """Variant "a": the four rows, legend, and footer. Variant "b": the same plus panel (e) under the footer. Row (d)'s
    pushes and numbers come from probe 1's record."""
    if variant not in OUT_NAMES:
        raise ValueError(f"variant must be one of {tuple(OUT_NAMES)}")
    values = dose_response_320(record_path) if variant == "b" else None
    plt = _plt()
    s = REFERENCE_INCHES_PER_UNIT
    text = footer_text()
    box = ((text.count("\n") + 1) * 10 * 1.2 / 72) / s + 2 * (0.6 * 10 / 72 / s)
    ylim = (FOOTER_TOP - box - 0.25, 1.3)
    width = (XLIM[1] - XLIM[0]) * s
    rows_h = (ylim[1] - ylim[0]) * s
    panel_h = PANEL["title_gap"] + PANEL["axes_h"] + PANEL["below"] if variant == "b" else 0.0
    with plt.rc_context(RC):
        fig = plt.figure(figsize=(width, rows_h + panel_h))
        ax = fig.add_axes([0, panel_h / (rows_h + panel_h), 1, rows_h / (rows_h + panel_h)])  # one data unit = s inches
        ax.set_xlim(*XLIM)
        ax.set_ylim(*ylim)
        ax.axis("off")
        _draw_rows(ax, probe_record)
        _legend(ax, *LEGEND_X, LEGEND_Y)
        footer(ax, sum(XLIM) / 2, FOOTER_TOP - 0.6 * 10 / 72 / s, text, va="top")
        if variant == "b":
            x_in = (width - PANEL["axes_w"]) / 2 + 0.3
            y_in = PANEL["below"]
            pax = _panel(fig, x_in, y_in, values)
            fig.text((x_in + PANEL["axes_w"] / 2) / width, (y_in + PANEL["axes_h"] + 0.12) / (rows_h + panel_h), PANEL_TITLE,
                     ha="center", va="bottom", fontsize=HEAD, color=INK)
            import matplotlib.transforms as mtransforms

            under = mtransforms.offset_copy(pax.transAxes, fig=fig, x=0, y=-PANEL_NOTE_BELOW_PT, units="points")
            pax.text(0.5, 0, PANEL_NOTE, transform=under, ha="center", va="top", fontsize=9, color=MUTED)
        fig.savefig(path, facecolor="white", bbox_inches="tight", dpi=200)
        plt.close(fig)
    save_small_copy(path)  # the 75 percent copy
    return Path(path)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for variant in OUT_NAMES:
        p = draw_interference(OUT_DIR / OUT_NAMES[variant], variant)
        for q in (p, small_path(p)):
            print(f"wrote {q.relative_to(REPO_ROOT).as_posix()}")
    note = OUT_DIR / ROW_D_NOTE_NAME
    note.write_text(row_d_note())
    print(f"wrote {note.relative_to(REPO_ROOT).as_posix()}")
    print("row (d), as drawn:", [(c["name"], c["cell"], "+" if c["drawn_sign"] > 0 else "-") for c in row_d_cells(row_d_components())],
          "| beside it:", list(row_d_lines(row_d_numbers())))
    print("net pushes:", {r: row_net_push(r) for r in ("a", "b", "c")}, "| dose-response at 320 steps:",
          [round(v, 4) for v in dose_response_320()])
    return 0


if __name__ == "__main__":
    sys.exit(main())
