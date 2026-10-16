"""Plans 4 and 7 of the research log: the post's Figure 3, the paper's interference picture as a toy, and what we measured.

    uv run python -m vpd_audit_2.post_interference

Rows (a) to (c) draw the paper's own toy picture (its lines 2017 to 2022 and the footnote at 1508): components inactive
on an input each contribute a little to the output; with all of them on the contributions cancel (a); an adversary that
keeps the contributions of one sign and switches off the rest makes them add up (b); on another input the contributions
point elsewhere, so the same switches cancel again (c), which is why the paper sets such masks aside. Rows (d) and (e) are
what we measured: eight real components under the same switches, their first-order contributions measured by probe 1
(plan 5 of the research log), on the batch the adversary searched (d) and on one unseen text (e).

Rows (d) and (e)'s arrows. The eight components, whether each is off or kept, and their signs are read from probe 1's
record (`results/s7_probe1/record.json`, "row_d"), never typed here: four from the setting's off set in its off cells,
four from the matched kept set in its on cells, in the record's order, placed in the toy's switch pattern so that the
rows keep "the same switches". Row (d) draws the record's "drawn_arrow_on_attack" (the push while on, on the searched
batch), row (e) its "drawn_arrow_on_text" (the same, on the unseen text: the NEGATIVE of the measured switch-off push
there). Every arrow has the toy's length, so only its direction is a measurement.

Rows (d) and (e) also have a net arrow and a reading, as rows (a) to (c) do. The net arrows are schematic: row (d)'s has
row (b)'s length, and row (e)'s that length times the share of its own-batch damage a 320-step source keeps on unseen
text, pooled over the 80 sources the probe read, from the lead experiment's record (`results/s5_lead/analysis/
lead_records.json`) and rounded to the two places its table prints (0.95). Both readings say "Contributions Add Up", row
(e)'s in vermilion. The share of switched-off components that keep their sign (the record's 320-step `g_bar`, 74
percent) and the chance level are in the caption. The caption note, `results/post/figure3_row_d.txt` (`row_d_note`),
lists the eight components as drawn in rows (d) and (e), with their measured switch-off pushes on the unseen text, says
what the net arrows are, and gives the sources of the numbers.

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
PROBE_RECORD = REPO_ROOT / "results" / "s7_probe1" / "record.json"
LEAD_RECORD = REPO_ROOT / "results" / "s5_lead" / "analysis" / "lead_records.json"
ROW_D_NOTE_NAME = "figure3_row_d.txt"

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


# ----------------------------------------------------------------------------- the measured rows (plan 7 of the research log)

FRACTION_WORDS = {0.25: "a quarter", 0.5: "a half", 0.75: "three quarters", 1.0: "all"}
MEASURED_ROWS = {"d": "drawn_arrow_on_attack", "e": "drawn_arrow_on_text"}  # row: the record's field for its drawn sign


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


def measured_cells(record_path: Path, key: str) -> list[dict]:
    """The eight components as `row_d_cells` places them, each with its name, its cell, and the drawn sign read from the
    record's field `key` ("drawn_arrow_on_attack" for row (d), "drawn_arrow_on_text" for row (e))."""
    rec = json.loads(Path(record_path).read_text())["row_d"]["components"]
    signs = {f"{c['module']} {c['component']}": int(c[key]) for c in rec}
    cells = row_d_cells(row_d_components(record_path), SWITCHES)
    return [{"name": c["name"], "cell": c["cell"], "sign": signs[c["name"]]} for c in cells]


def kept_share(record_path: Path = LEAD_RECORD) -> dict:
    """The share of its own-batch added harm a source keeps on unseen text, pooled over all 80 of the lead run's 320-step
    sources (the settings probe 1 read): the lead record's 320-step retention, which `lead_tables.txt` prints in its
    320-step row 9 as "all 80 settings pooled 0.95". Returns the estimate and the value drawn, rounded to those two places."""
    steps = json.loads(Path(record_path).read_text())["main"]["step"]
    (step,) = [s for s in steps if s["key"] == 320]
    estimate = float(step["retention"]["pooled"]["estimate"])
    return {"estimate": estimate, "drawn": round(estimate, 2)}


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


def row_d_note(record_path: Path = PROBE_RECORD) -> str:
    """The caption note for rows (d) and (e): the arrows' convention, the eight components as drawn in both rows, what the
    net arrows are, and the numbers' sources. (The name is the file's, `figure3_row_d.txt`, from when the measured row was
    row (d).)"""
    rec = json.loads(Path(record_path).read_text())
    st, tx = rec["row_d"]["setting"], rec["row_d"]["text"]
    cells = row_d_cells(row_d_components(record_path))
    on_batch = measured_cells(record_path, MEASURED_ROWS["d"])
    n = row_d_numbers(record_path)
    kept = kept_share()
    arrow_word = lambda s: "right (+)" if s > 0 else "left (-)"  # noqa: E731
    L = ["Figure 3, rows (d) and (e): caption note (plan 7 of the research log). Written by vpd_audit_2/post_interference.py from results/s7_probe1/record.json.",
         "",
         "Rows (d) and (e) show the same eight real components under the same switches. Each arrow in a cell is a component's",
         "first-order push measured by probe 1, drawn as the push WHILE ON: the negative of the measured effect of switching it off. Row (e)",
         "takes the push on one unseen text; row (d) takes it summed over the texts of the batch the adversary searched.",
         "Rightward points along the full pattern's shift, toward the damage. Every arrow has the toy's length; only its",
         "direction is measured.",
         f"Setting: {st['attack']} from start {st['start']} at 320 steps (its kappa {st['kappa']:.4f}, the lower median of the 80); "
         f"text {tx['text_id']}, {tx['batch']} position {tx['index']} (its agreement {tx['g']:.4f}, the lower median of the setting's 2,048).",
         "Four switched-off components (off cells) and four kept components (on cells), drawn with probability proportional to",
         "their push on that text (plan 5 of the research log, amendment 6).",
         "",
         "As drawn, left to right (cell, component, measured switch-off push on the unseen text, arrow in row (e), arrow in row (d)):"]
    for k, (c, d) in enumerate(zip(cells, on_batch), start=1):
        L.append(f"  {k}. {'off ' if c['cell'] == 'off' else 'kept'}  {c['name']:<22}  {c['switch_off_push']:+.4e}  {arrow_word(c['drawn_sign']):<9}  "
                 f"{arrow_word(d['sign'])}")
    L += ["",
          "The net arrows in rows (d) and (e) are schematic, not measured: row (d)'s has row (b)'s length, and row (e)'s that",
          f"length times {kept['drawn']:.2f}, the share of its own-batch damage a source keeps on unseen text at 320 steps.",
          "",
          f"Sources, 320-step row of the record: off-set agreement g_bar {n['raw']:.4f} (the caption's {n['raw_pct']} percent); permutation chance (post hoc, "
          f"post_hoc_permutation_baseline.g0_bar) {n['permutation_chance']:.4f}; kept components' agreement (the pre-registered chance, "
          f"g0_bar) {n['kept']:.4f}; additivity ratio (additivity.off_set) {n['additivity']:.4f}.",
          f"Kept share for row (e)'s net arrow: the lead experiment's record (lead_records.json), 320 steps, retention pooled over all "
          f"80 settings, {kept['estimate']:.4f}, drawn as {kept['drawn']:.2f}."]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- the words

SECTIONS = ("The Paper's Picture", "What We Measured")
TITLES = {"a": "(a) Text A, Nothing\nSwitched Off", "b": "(b) Text A with Adversary's\nSource Applied",
          "c": "(c) Text B with Same\nSource Applied",
          "d": "(d) The Batch Searched with\nAdversary's Source Applied", "e": "(e) One Unseen Text with\nSame Source Applied"}
READINGS = {"a": "Contributions Cancel", "b": "Contributions Add Up", "c": "Contributions Cancel Again"}
NET_HEADER = "Net Contribution\nto the Output"
# Beside the measured rows, as beside rows (a) to (c); the unseen text's in vermilion.
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
RULE_Y = -5.0  # the hairline between the paper's picture and the measurement, a full row below row (c)
SECTION_LABEL_Y = {SECTIONS[0]: 0.2, SECTIONS[1]: RULE_Y - 0.48}  # "What We Measured" below the rule, not touching it
D_BOTTOM = ROW_TOP["e"] - 1.3  # the bottom of the measured section's bracket
XLIM = (BRACKET_X - 0.1, READ_X + READ_W)
LEGEND_Y = D_BOTTOM - 0.85  # the first legend row's swatch bottom
LEGEND_X = (BRACKET_X + 0.6, BRACKET_X + 7.4)
BOTTOM_TOP = LEGEND_Y - 0.3  # just under the legend's first row, the top of the margin at the figure's foot (no footer)


def _cell(ax, x, y, on, glyph=None, push=0):
    """One circuit's cell: the first post's on (grey) or off (light) shading, holding its push arrow (or a glyph, which no
    row uses since plan 7 of the research log replaced row (d)'s question marks with measured pushes)."""
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


def _draw_rows(ax, record_path: Path = PROBE_RECORD):
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
    # the measured rows: (d) on the searched batch, (e) on the unseen text, each with a schematic net arrow (row (b)'s
    # net push, times the kept share on the unseen text) and a reading
    share = {"d": 1.0, "e": kept_share()["drawn"]}
    for row, key in MEASURED_ROWS.items():
        y = ROW_TOP[row] - RH
        for j, c in enumerate(measured_cells(record_path, key)):
            _cell(ax, j * CW3, y, c["cell"] == "on", push=c["sign"])
        _net(ax, y, row_net_push("b") * share[row])
        ax.text(READ_X, y + RH / 2, MEASURED_READINGS[row], ha="left", va="center", fontsize=9.5, color=MEASURED_READING_COLOURS[row])
        ax.text(TITLE_X, y + RH / 2 + 0.02, TITLES[row], ha="right", va="center", fontsize=10.5, color=INK, linespacing=1.1)
    # the section brackets and the hairline between them
    _bracket(ax, BRACKET_X, ROW_TOP["a"], RULE_Y + 0.25, MUTED, 1.0)
    _bracket(ax, BRACKET_X, ROW_TOP["d"], D_BOTTOM, MUTED, 1.0)
    ax.plot([BRACKET_X, READ_X + READ_W], [RULE_Y, RULE_Y], color=MUTED, linewidth=0.5)
    ax.text(BRACKET_X, SECTION_LABEL_Y[SECTIONS[0]], SECTIONS[0], ha="left", va="bottom", fontsize=HEAD, color=INK)
    ax.text(BRACKET_X, SECTION_LABEL_Y[SECTIONS[1]], SECTIONS[1], ha="left", va="top", fontsize=HEAD, color=INK)


def draw_interference(path: Path, probe_record: Path = PROBE_RECORD) -> Path:
    """The figure: the toy rows (a) to (c), the measured rows (d) and (e), and the legend; and its 50 percent copy beside
    it. Rows (d) and (e) come from probe 1's record."""
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
        _draw_rows(ax, probe_record)
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
    note = OUT_DIR / ROW_D_NOTE_NAME
    note.write_text(row_d_note())
    print(f"wrote {note.relative_to(REPO_ROOT).as_posix()}")
    for row, key in MEASURED_ROWS.items():
        print(f"row ({row}), as drawn:", [(c["name"], c["cell"], "+" if c["sign"] > 0 else "-") for c in measured_cells(PROBE_RECORD, key)])
    print("net pushes:", {r: row_net_push(r) for r in ("a", "b", "c")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
