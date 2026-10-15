"""Session 7, plan 2: the post's Figure 1, the carry-over scatter, read from the saved lead-experiment table. No model runs,
no GPU, no new measurement.

    uv run python -m vpd_audit_2.post_figure

For every mask the adversary found on an attack batch (one search, one attack batch and one start, read at a search length
or at a harm level), the figure plots the damage the mask does on the 16 held-out batches it never saw against the damage it
did on the batch it was found on, with the mask's shuffled copies beside it. Five files go to `results/post/`, and each
PNG also as a copy at 75 percent of its pixel size, named with the suffix _75 (`post_small`):

  - `figure1_carry_over.png`, the post's figure (variant B of plan 1): the five step rows as mask points, the `h2` and `h5`
    rows highlighted, and every drawn mask's shuffled copies; `h10` is left out. Raw harm, in nats per token.
  - `figure1_carry_over_a.png`, variant A, for comparison only: the five step rows and their shuffled copies.
  - `figure1_registered.png`, the scatter as session 4 registered it (freeze file Part 1, Section 8): all eight rows, in
    added harm (harm minus the random start's), one marker and colour per row. For the record and the appendix.
  - `figure1_carry_over.csv`, one row per point of the full set (637), the numbers behind all three figures.
  - `figure1_reference.json`, the reference values, the paper's table values, the counts, and the commits.

The data step (`figure_points`, `reference_values`) is kept apart from the drawing (`draw_carry_over`, `draw_registered`), as
the first post's figure code does. The palette, `RC`, `style_axes`, and `tight_layout_at_pixel_ratio` are copied from that
code (`third_party/vpd-audit/vpd_audit/figures_post.py`) rather than imported, so this module stands alone.

The points are 80 searches (16 attack batches by 5 starts) read at up to eight moments each, not 637 independent masks, and a
harm-level point can be the same setting as a step point when the level's crossing fell on a saved step.

Indices: i attack batch, j held-out batch, s start, q scored setting, r shuffled copy.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from vpd_audit_2 import lead_table as LT
from vpd_audit_2.post_small import save_small_copy, small_path

REPO_ROOT = Path(__file__).resolve().parent.parent
TABLE = REPO_ROOT / "results" / "s5_lead" / "lead" / "sealed"
OUT_DIR = REPO_ROOT / "results" / "post"
OUT_NAMES = {"b": "figure1_carry_over.png", "a": "figure1_carry_over_a.png", "registered": "figure1_registered.png",
             "csv": "figure1_carry_over.csv", "reference": "figure1_reference.json"}

# ----------------------------------------------------------------------------- copied from the first post's figure code

# The post's palette (Okabe-Ito), as in third_party/vpd-audit/vpd_audit/figures_post.py.
BLUE, BLUE_DARK = "#0072B2", "#003B66"
ORANGE, ORANGE_DARK = "#E69F00", "#8A5A00"
PURPLE = "#CC79A7"
VERMILLION = "#D55E00"
GREEN = "#009E73"
SKY = "#56B4E9"
INK, MUTED, SPINE = "#1a1a1a", "#6b6b6b", "#3a3a3a"
RC = {"font.size": 11, "font.family": "DejaVu Sans"}
LAYOUT_PIXEL_RATIO = 2


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def tight_layout_at_pixel_ratio(fig) -> None:
    """`fig.tight_layout()` computed at twice the figure's dpi, then the dpi restored before saving, as the first post's
    figures were laid out."""
    dpi = fig.dpi
    fig.set_dpi(dpi * LAYOUT_PIXEL_RATIO)
    fig.tight_layout()
    fig.set_dpi(dpi)


def style_axes(ax):
    for side in ("left", "bottom", "top", "right"):
        ax.spines[side].set_color(SPINE)
        ax.spines[side].set_linewidth(1.1)
    ax.tick_params(colors=INK, direction="in", length=5, width=1.1)


# ----------------------------------------------------------------------------- the data

STEP_ROWS = LT.STEP_ROWS  # n20, n40, n80, n160, n320
LEVEL_ROWS = LT.LEVEL_ROWS  # h2, h5, h10
POINT_ROWS = STEP_ROWS + LEVEL_ROWS  # every row but n159 and n319 (duplicates one step earlier, with no shuffles)
HIGHLIGHT_ROWS = ("h2", "h5")
POST_ROWS = STEP_ROWS + HIGHLIGHT_ROWS
COLUMNS = ("row", "attack_batch", "start", "step", "own_batch_harm", "unseen_harm_mean", "unseen_harm_min", "unseen_harm_max",
           "shuffled_harm_mean", "in_post_figure", "attack_start_harm")

# The paper's PGD table (KL divergence to the target model after n adversarial steps, on the authors' batch of 128 sequences
# of length 512): table `tab:vpd-pgd-ce`, literature/original/bushnaq2026_vpd.txt, lines 395-399; the same constants as
# vpd_audit_2/g1_readings.py.
PAPER_TABLE = {20: 0.8280, 40: 1.3539, 80: 3.8381, 160: 25.2560, 320: 40.2200}
PAPER_TABLE_SOURCE = "the paper's PGD table, tab:vpd-pgd-ce (literature/original/bushnaq2026_vpd.txt, lines 395-399)"
SEARCHES_NOTE = ("The points are 80 searches (16 attack batches by 5 starts) read at up to eight moments each (five search lengths "
                 "and three harm levels), not 637 independent masks. A harm-level point can be the same setting as a step point "
                 "when the level's crossing fell on a saved step.")


def figure_points(table: dict[str, Any]) -> pd.DataFrame:
    """One row per attack setting (i, s) present at each of the eight point rows: its harm on its own attack batch, its mean
    (and least and greatest) harm over the 16 held-out batches, and the mean harm of its 8 shuffled copies over the 16
    held-out batches. Raw harm, nats per token. `attack_start_harm` is the random start's harm on the attack batch, for the
    registered form's added harm."""
    names = [str(x) for x in table["setting_names"]]
    attack = [str(x) for x in table["attack_names"]]
    starts = [int(x) for x in table["starts"]]
    rows = []
    for row in POINT_ROWS:
        q = names.index(row)
        for i, a in enumerate(attack):
            for s, start in enumerate(starts):
                step = int(table["step_A"][i, s, q])
                if step == -1:  # the search never reached this harm level: no setting
                    continue
                unseen = table["carried"][i, :, s, q]  # [K_H]
                rows.append({"row": row, "attack_batch": a, "start": start, "step": step,
                             "own_batch_harm": float(table["own_A"][i, s, q]),
                             "unseen_harm_mean": float(unseen.mean()), "unseen_harm_min": float(unseen.min()),
                             "unseen_harm_max": float(unseen.max()),
                             "shuffled_harm_mean": float(table["shuf"][i, :, s, q, :].mean()),
                             "in_post_figure": row in POST_ROWS,
                             "attack_start_harm": float(table["init_A"][i, s])})
    points = pd.DataFrame(rows, columns=list(COLUMNS))
    harms = points[["own_batch_harm", "unseen_harm_mean", "unseen_harm_min", "unseen_harm_max", "shuffled_harm_mean", "attack_start_harm"]]
    if not np.isfinite(harms.to_numpy()).all():
        raise ValueError("a present setting has a harm that is NaN or infinite")
    return points


def reference_values(table: dict[str, Any]) -> dict[str, float]:
    """The benchmark, what the paper's 20-step adversary does to the unseen batches when run on them directly (the held-out
    batches' own 20-step searches, mean over batches and starts), and the random start's harm on the unseen batches."""
    names = [str(x) for x in table["setting_names"]]
    q20 = names.index("n20")
    return {"benchmark": float(table["own_H"][:, :, q20].mean()), "random_start": float(table["init_H"].mean())}


def same_setting_counts(table: dict[str, Any]) -> dict[str, int]:
    """Per harm-level row, how many of its points are the same setting (by setting hash) as one of the same search's step
    points, i.e. the level's crossing fell on a saved step."""
    names = [str(x) for x in table["setting_names"]]
    sha = table["setting_sha_A"]
    step_q = [names.index(r) for r in STEP_ROWS]
    out = {}
    for row in LEVEL_ROWS:
        q = names.index(row)
        present = table["step_A"][:, :, q] != -1
        same = np.zeros(present.shape, dtype=bool)
        for qq in step_q:
            same |= sha[:, :, q] == sha[:, :, qq]
        out[row] = int((same & present).sum())
    return out


# ----------------------------------------------------------------------------- the drawing

WIDTH, HEIGHT, DPI = 6.3, 5.0, 200
RAW_LIMITS = (0.15, 80.0)
RAW_TICKS = (0.2, 0.5, 1, 2, 5, 10, 20, 50)
ADDED_LIMITS = (0.05, 80.0)
ADDED_TICKS = (0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50)
BAND = (PAPER_TABLE[20], PAPER_TABLE[160])
# On one line each, centred on their ticks, the two labels overlap (the ticks are about 0.9 inches apart): two lines each.
BAND_TICKS = ((PAPER_TABLE[40], "paper's\n40 steps"), (PAPER_TABLE[80], "paper's\n80 steps"))
BAND_COLOUR = "#f0f0f0"
# The plan's words; the line breaks are a drawing decision (on one line the labels and legend entries are wider than the axes).
X_LABEL = "Damage on the batch the mask was found on\n(KL from original model, nats)"
Y_LABEL = "Damage on unseen text\n(KL from original model, nats)"
X_LABEL_ADDED = "Added damage on the batch the mask was found on\n(KL from original model less the random start's, nats)"
Y_LABEL_ADDED = "Added damage on unseen text\n(KL from original model less the random start's, nats)"
LABELS = {"mask": "Mask the adversary found,\napplied to unseen text",
          "highlight": "The same searches, read when they had\ndone 2 or 5 nats on their own batch",
          "shuffled": "Same mask with its components shuffled\nwithin weight matrix and usage band,\nplotted at the mask's own-batch damage",
          "diagonal": "Same damage as on the batch searched",
          "diagonal_added": "Same added damage as on the batch searched",
          "benchmark": "Paper's 20-step adversary, our run\non the unseen batch itself ({:.2f})",  # the benchmark's value, from the table
          "random_start": "Random starting point",
          "band": "Paper's table: the range where it neither\nclaims nor concedes robustness"}
# Where the carry-over figure's labels sit (drawing decisions; see the plan's report). The benchmark's label is below its
# line at the right, where no point lies (at the left it would cross the 20-step points), and the legend is in the empty
# upper left, below the band's label (lower right it would cover the shuffled copies and the random start's label).
BENCHMARK_LABEL_X = 75.0  # the label's right end
RANDOM_START_LABEL_X = 0.23  # the label's left end, right of where the diagonal and the 0.2 tick would cross it
DIAGONAL_LABEL_X = 62.0  # the diagonal label's right end, near the top right corner and inside the axes
CARRY_OVER_LEGEND = {"loc": "upper left", "bbox_to_anchor": (0.0, 0.91), "borderaxespad": 0.3}
REGISTERED_DIAGONAL_LABEL_X = 60.0  # the registered form's own, unchanged by the carry-over figure's label changes
REGISTERED_LEGEND = {"loc": "lower right"}
REGISTERED_STYLE = {  # row: (colour, marker, legend label)
    "n20": (SKY, "o", "20 steps"), "n40": (BLUE, "s", "40 steps"), "n80": (GREEN, "^", "80 steps"),
    "n160": (ORANGE, "D", "160 steps"), "n320": (PURPLE, "v", "320 steps"),
    "h2": (VERMILLION, "P", "2 nats"), "h5": (INK, "X", "5 nats"), "h10": (ORANGE_DARK, "*", "10 nats")}
VARIANTS = ("b", "a")


def _within(values: np.ndarray, limits: tuple[float, float], what: str) -> None:
    """Log axes drop a value at or below zero, and the limits clip a value outside them, both silently: refuse instead."""
    v = np.asarray(values, dtype=np.float64)
    if not (np.isfinite(v).all() and (v > limits[0]).all() and (v < limits[1]).all()):
        raise ValueError(f"{what}: a value lies outside the axes ({limits[0]} to {limits[1]})")


def _log_axes(ax, limits: tuple[float, float], ticks: tuple[float, ...]) -> None:
    from matplotlib.ticker import FixedFormatter, FixedLocator, NullLocator

    for axis, set_scale, set_lim in ((ax.xaxis, ax.set_xscale, ax.set_xlim), (ax.yaxis, ax.set_yscale, ax.set_ylim)):
        set_scale("log")
        set_lim(*limits)
        axis.set_major_locator(FixedLocator(list(ticks)))
        axis.set_major_formatter(FixedFormatter([f"{t:g}" for t in ticks]))
        axis.set_minor_locator(NullLocator())


def _diagonal(ax, limits: tuple[float, float], label: str, at: float) -> None:
    """The line y = x, thin, solid, `MUTED`, with its label along it, just above, ending at x = `at`."""
    import matplotlib.transforms as mtransforms

    ax.plot(limits, limits, color=MUTED, linewidth=1.0, linestyle="-", zorder=1)
    above = mtransforms.offset_copy(ax.transData, fig=ax.figure, x=-2.0, y=2.0, units="points")
    ax.text(at, at, label, color=MUTED, fontsize=9, ha="right", va="bottom", rotation=45, rotation_mode="anchor",
            transform_rotates_text=True, transform=above, zorder=1)


def _label_below(ax, x: float, y: float, text: str, ha: str = "left") -> None:
    """A reference line's label, just below the line, starting (ha "left") or ending (ha "right") at `x`."""
    import matplotlib.transforms as mtransforms

    below = mtransforms.offset_copy(ax.transData, fig=ax.figure, x=0.0, y=-2.0, units="points")
    ax.text(x, y, text, color=MUTED, fontsize=9, ha=ha, va="top", multialignment=ha, linespacing=1.15, transform=below, zorder=1)


def _legend(ax, handles: list[Any], labels: list[str], placement: dict[str, Any]) -> None:
    leg = ax.legend(handles, labels, frameon=False, fontsize=9, handlelength=1.0, handletextpad=0.5, labelspacing=0.6, **placement)
    for t in leg.get_texts():
        t.set_color(INK)


def draw_carry_over(points: pd.DataFrame, refs: dict[str, float], path: Path, variant: str = "b") -> Path:
    """The post's figure (`variant` "b") or its comparison (`variant` "a"), in raw harm: mask points for the five step rows,
    their shuffled copies at the parent mask's own-batch harm, and in "b" the h2 and h5 rows highlighted with their shuffled
    copies; the paper's range as a band, the diagonal, the benchmark, and the random start."""
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    from matplotlib.lines import Line2D
    from matplotlib.ticker import NullLocator

    plt = _plt()
    steps = points[points["row"].isin(STEP_ROWS)]
    high = points[points["row"].isin(HIGHLIGHT_ROWS)] if variant == "b" else points.iloc[0:0]
    drawn = pd.concat([steps, high])
    for col in ("own_batch_harm", "unseen_harm_mean", "shuffled_harm_mean"):
        _within(drawn[col].to_numpy(), RAW_LIMITS, col)
    _within(np.array([refs["benchmark"], refs["random_start"]]), RAW_LIMITS, "reference values")
    hi = RAW_LIMITS[1]
    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), dpi=DPI)
        _log_axes(ax, RAW_LIMITS, RAW_TICKS)
        # the paper's table: the range where it neither claims nor concedes robustness, with its 40- and 80-step values
        ax.axvspan(*BAND, color=BAND_COLOUR, linewidth=0, zorder=0)
        ax.text(float(np.sqrt(BAND[0] * BAND[1])), hi / 1.12, LABELS["band"], color=MUTED, fontsize=9, ha="center", va="top",
                linespacing=1.15, zorder=1)
        top = ax.secondary_xaxis("top")  # two small ticks on the top axis, labelled above it
        top.set_xticks([x for x, _ in BAND_TICKS], labels=[t for _, t in BAND_TICKS])
        top.xaxis.set_minor_locator(NullLocator())
        top.tick_params(colors=MUTED, direction="in", length=4, width=1.1, labelsize=8, pad=2)
        top.spines["top"].set_visible(False)  # the main axes' top spine stays
        # the reference lines
        _diagonal(ax, RAW_LIMITS, LABELS["diagonal"], at=DIAGONAL_LABEL_X)
        ax.axhline(refs["benchmark"], color=MUTED, linewidth=1.0, linestyle=(0, (5, 3)), zorder=1)
        _label_below(ax, BENCHMARK_LABEL_X, refs["benchmark"], LABELS["benchmark"].format(refs["benchmark"]), ha="right")
        ax.axhline(refs["random_start"], color=MUTED, linewidth=1.0, linestyle=(0, (1, 2)), zorder=1)
        _label_below(ax, RANDOM_START_LABEL_X, refs["random_start"], LABELS["random_start"])
        # the points: shuffled copies, then the masks above the lines, then the highlighted rows above the others
        ax.scatter(drawn["own_batch_harm"], drawn["shuffled_harm_mean"], s=12, marker="s", color=VERMILLION, alpha=0.55,
                   linewidths=0, zorder=2)
        ax.scatter(steps["own_batch_harm"], steps["unseen_harm_mean"], s=14, marker="o", color=BLUE, alpha=0.55,
                   linewidths=0, zorder=3)
        if len(high):
            ax.scatter(high["own_batch_harm"], high["unseen_harm_mean"], s=16, marker="o", facecolor=BLUE_DARK,
                       edgecolor="black", linewidths=0.4, alpha=0.8, zorder=4)
        ax.set_xlabel(X_LABEL, color=INK)
        ax.set_ylabel(Y_LABEL, color=INK)
        style_axes(ax)
        mask = Line2D([], [], linestyle="none", marker="o", markersize=5, color=BLUE, markeredgewidth=0)
        dark = Line2D([], [], linestyle="none", marker="o", markersize=5.5, markerfacecolor=BLUE_DARK, markeredgecolor="black",
                      markeredgewidth=0.4)
        shuf = Line2D([], [], linestyle="none", marker="s", markersize=4.5, color=VERMILLION, markeredgewidth=0)
        if variant == "b":
            _legend(ax, [mask, dark, shuf], [LABELS["mask"], LABELS["highlight"], LABELS["shuffled"]], CARRY_OVER_LEGEND)
        else:
            _legend(ax, [mask, shuf], [LABELS["mask"], LABELS["shuffled"]], CARRY_OVER_LEGEND)
        tight_layout_at_pixel_ratio(fig)
        fig.savefig(path, facecolor="white")
        plt.close(fig)
    save_small_copy(path)
    return Path(path)


def draw_registered(points: pd.DataFrame, refs: dict[str, float], path: Path) -> Path:
    """The scatter as session 4 registered it: all eight rows, in added harm on both axes (own-batch harm less the search's
    own start's harm on its attack batch; mean unseen harm less the random start's mean harm on the unseen batches), one
    marker and colour per row, with the diagonal and no other reference."""
    from matplotlib.lines import Line2D

    plt = _plt()
    x = points["own_batch_harm"].to_numpy() - points["attack_start_harm"].to_numpy()
    y = points["unseen_harm_mean"].to_numpy() - refs["random_start"]
    _within(x, ADDED_LIMITS, "added own-batch harm")
    _within(y, ADDED_LIMITS, "added unseen harm")
    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), dpi=DPI)
        _log_axes(ax, ADDED_LIMITS, ADDED_TICKS)
        _diagonal(ax, ADDED_LIMITS, LABELS["diagonal_added"], at=REGISTERED_DIAGONAL_LABEL_X)
        handles, labels = [], []
        for z, row in enumerate(POINT_ROWS):
            colour, marker, label = REGISTERED_STYLE[row]
            sel = (points["row"] == row).to_numpy()
            ax.scatter(x[sel], y[sel], s=14, marker=marker, color=colour, alpha=0.55, linewidths=0, zorder=2 + z)
            handles.append(Line2D([], [], linestyle="none", marker=marker, markersize=5, color=colour, markeredgewidth=0))
            labels.append(label)
        ax.set_xlabel(X_LABEL_ADDED, color=INK)
        ax.set_ylabel(Y_LABEL_ADDED, color=INK)
        style_axes(ax)
        _legend(ax, handles, labels, REGISTERED_LEGEND)
        tight_layout_at_pixel_ratio(fig)
        fig.savefig(path, facecolor="white")
        plt.close(fig)
    save_small_copy(path)
    return Path(path)


# ----------------------------------------------------------------------------- the files


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True)


def analysis_commit() -> dict[str, Any]:
    """The commit the figures are drawn at, and whether this module on disk is the one in that commit."""
    head = _git("rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    status = _git("status", "--porcelain", "--", str(Path(__file__).resolve()))
    return {"analysis_commit": head.stdout.strip() if head.returncode == 0 else None,
            "analysis_module_as_committed": status.returncode == 0 and status.stdout.strip() == ""}


def reference_record(table: dict[str, Any], points: pd.DataFrame, refs: dict[str, float], core_path: Path) -> dict[str, Any]:
    per_row = {row: int((points["row"] == row).sum()) for row in POINT_ROWS}
    searches = int(points[["attack_batch", "start"]].drop_duplicates().shape[0])
    return {
        "benchmark": {"value": refs["benchmark"],
                      "definition": "own_H[:, :, n20].mean(): the paper's 20-step adversary run on each unseen (held-out) batch "
                                    "itself, mean over the 16 held-out batches and 5 starts, raw nats per token"},
        "random_start": {"value": refs["random_start"],
                         "definition": "init_H.mean(): the random starting point's harm on the unseen batches, mean over the 16 "
                                       "held-out batches and 5 starts, raw nats per token"},
        "paper_table": {"source": PAPER_TABLE_SOURCE, "kl_after_steps": {str(k): v for k, v in PAPER_TABLE.items()}},
        "points": int(len(points)),
        "points_per_row": per_row,
        "points_in_post_figure": int(points["in_post_figure"].sum()),
        "points_in_variant_a": int(points["row"].isin(STEP_ROWS).sum()),
        "distinct_searches": searches,
        "note": SEARCHES_NOTE,
        "level_points_same_setting_as_a_step_point": same_setting_counts(table),
        "table": core_path.parent.relative_to(REPO_ROOT).as_posix(),
        "run_commit": LT.read_meta(core_path).get("run_commit"),
        **analysis_commit(),
    }


def write_all(table_dir: Path = TABLE, out_dir: Path = OUT_DIR) -> dict[str, Any]:
    table = LT.load_table(table_dir)
    points = figure_points(table)
    refs = reference_values(table)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {v: draw_carry_over(points, refs, out_dir / OUT_NAMES[v], v) for v in VARIANTS}
    paths["registered"] = draw_registered(points, refs, out_dir / OUT_NAMES["registered"])
    for key in (*VARIANTS, "registered"):  # each drawing also wrote its 75 percent copy
        paths[f"{key}_75"] = small_path(paths[key])
    paths["csv"] = out_dir / OUT_NAMES["csv"]
    points.to_csv(paths["csv"], index=False, lineterminator="\n")
    record = reference_record(table, points, refs, Path(table_dir) / LT.CORE_FILE)
    paths["reference"] = out_dir / OUT_NAMES["reference"]
    paths["reference"].write_text(json.dumps(record, indent=2) + "\n")
    return {"paths": paths, "record": record}


def main() -> int:
    out = write_all()
    r = out["record"]
    print(f"points: {r['points']} ({', '.join(f'{k} {v}' for k, v in r['points_per_row'].items())}); "
          f"in the post's figure {r['points_in_post_figure']}; distinct searches {r['distinct_searches']}")
    print(f"benchmark {r['benchmark']['value']:.6f}; random start {r['random_start']['value']:.6f}")
    print(f"run commit {r['run_commit']}; analysis commit {r['analysis_commit']} (module as committed: {r['analysis_module_as_committed']})")
    for p in out["paths"].values():
        print(f"wrote {Path(p).relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
