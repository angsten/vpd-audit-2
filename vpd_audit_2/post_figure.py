"""Plan 2 of the research log: the post's Figure 1, the carry-over scatter, read from the saved lead-experiment table. No model runs,
no GPU, no new measurement.

    uv run python -m vpd_audit_2.post_figure

For every source the adversary found on an attack batch (one search, one attack batch and one start, read at a search
length), the figure plots the damage the source does on the 16 held-out batches it never saw against the damage it did on
the batch it was found on, with the source's shuffled copies beside it. Four files go to `results/post/`, each PNG also as
reduced copies (`post_small`):

  - `figure1_carry_over.png`, the post's figure, with copies at 75 and 62 percent (the post shows the 62): the five step
    rows as points coloured by search length, with a key; every drawn source's shuffled copies as dots at the parent's
    own-batch damage; the diagonal and the benchmark line. Raw harm, in nats per token. The benchmark's value is in the
    caption, not on the figure.
  - `figure1_registered.png`, with a 75 percent copy: the scatter as registered in freeze file Part 1, Section 8: all
    eight rows, in added harm (harm minus the random start's), one marker and colour per row. For the record and the
    appendix.
  - `figure1_carry_over.csv`, one row per point of the full set (637), the numbers behind both figures. Its column
    `in_post_figure` marks the five step rows and `h2` and `h5`, the set an earlier form of the post's figure drew.
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
OUT_NAMES = {"carry_over": "figure1_carry_over.png", "registered": "figure1_registered.png",
             "csv": "figure1_carry_over.csv", "reference": "figure1_reference.json"}
COPIES = {"carry_over": (0.75, 0.62), "registered": (0.75,)}  # the reduced copies of each PNG, as shares of its size

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
# of length 512): table `tab:vpd-pgd-ce`; the same constants as
# vpd_audit_2/g1_readings.py.
PAPER_TABLE = {20: 0.8280, 40: 1.3539, 80: 3.8381, 160: 25.2560, 320: 40.2200}
PAPER_TABLE_SOURCE = "the paper's PGD table, tab:vpd-pgd-ce"
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
# The post's figure, in its settled words. The line breaks are a drawing decision (on one line the labels are wider than
# the axes).
X_LABEL = "Damage to the Batch Searched\nKL from Original Model (nats)"
Y_LABEL = "Damage to Unseen Text\nKL from Original Model (nats)"
X_LABEL_ADDED = "Added damage on the batch the mask was found on\n(KL from original model less the random start's, nats)"
Y_LABEL_ADDED = "Added damage on unseen text\n(KL from original model less the random start's, nats)"
LABELS = {"mask": "Source the Adversary Found",
          "shuffled": "Same Source, Randomly Shuffled",
          "diagonal_added": "Same added damage as on the batch searched",
          # the benchmark's value is in the caption; on two lines the label clears the points at the right
          "benchmark": "Paper's 20-Step Search,\nRun on the Unseen Text"}
# The benchmark's label is below its line at the right, where no point lies (at the left it would cross the 20-step
# points); the legend, on a card, is in the empty upper left, above the search lengths' colour key.
BENCHMARK_LABEL_X = 75.0  # the label's right end
STEP_ORDER = (20, 40, 80, 160, 320)  # the step rows' search lengths, one colour each
STEP_CMAP = "YlGnBu"
STEP_SHADES = (0.3, 0.45, 0.6, 0.78, 0.95)  # where on the colour map each search length's colour is taken
KEY_BOX = (0.06, 0.70, 0.30, 0.025)  # axes fraction: x, y, width, height of the colour key
KEY_LABEL = "Search Steps"
LEGEND_FACE = "#fbfbfb"  # just off white, so that it reads as a card on the white axes
LEGEND_EDGE = MUTED
CARRY_OVER_LEGEND = {"loc": "upper left", "bbox_to_anchor": (0.055, 0.945), "borderaxespad": 0.0}
REGISTERED_DIAGONAL_LABEL_X = 60.0  # the registered form's own, unchanged by the carry-over figure's label changes
REGISTERED_LEGEND = {"loc": "lower right"}
REGISTERED_STYLE = {  # row: (colour, marker, legend label)
    "n20": (SKY, "o", "20 steps"), "n40": (BLUE, "s", "40 steps"), "n80": (GREEN, "^", "80 steps"),
    "n160": (ORANGE, "D", "160 steps"), "n320": (PURPLE, "v", "320 steps"),
    "h2": (VERMILLION, "P", "2 nats"), "h5": (INK, "X", "5 nats"), "h10": (ORANGE_DARK, "*", "10 nats")}


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


def draw_carry_over(points: pd.DataFrame, refs: dict[str, float], path: Path) -> Path:
    """The post's figure, in raw harm: a point for each source of the five step rows, coloured by search length, with a
    key; its shuffled copies as dots at the parent's own-batch harm; the diagonal and the benchmark line. Writes the
    reduced copies of `COPIES["carry_over"]` beside it."""
    import matplotlib
    from matplotlib.colors import BoundaryNorm, ListedColormap
    from matplotlib.lines import Line2D

    plt = _plt()
    steps = points[points["row"].isin(STEP_ROWS)]
    for col in ("own_batch_harm", "unseen_harm_mean", "shuffled_harm_mean"):
        _within(steps[col].to_numpy(), RAW_LIMITS, col)
    _within(np.array([refs["benchmark"]]), RAW_LIMITS, "the benchmark")
    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), dpi=DPI)
        _log_axes(ax, RAW_LIMITS, RAW_TICKS)
        # the reference lines: the diagonal, unlabelled, and the benchmark
        ax.plot(RAW_LIMITS, RAW_LIMITS, color=MUTED, linewidth=1.3, linestyle="-", zorder=1)
        ax.axhline(refs["benchmark"], color=MUTED, linewidth=1.0, linestyle=(0, (5, 3)), zorder=1)
        _label_below(ax, BENCHMARK_LABEL_X, refs["benchmark"], LABELS["benchmark"], ha="right")
        # the shuffled copies, then the sources above them, one colour per search length
        ax.scatter(steps["own_batch_harm"], steps["shuffled_harm_mean"], s=22, marker="o", color=VERMILLION, alpha=0.55,
                   linewidths=0, zorder=2)
        shades = [matplotlib.colormaps[STEP_CMAP](v) for v in STEP_SHADES]
        norm = BoundaryNorm([i - 0.5 for i in range(len(STEP_ORDER) + 1)], len(STEP_ORDER))
        idx = steps["step"].map({s: i for i, s in enumerate(STEP_ORDER)})
        sc = ax.scatter(steps["own_batch_harm"], steps["unseen_harm_mean"], s=22, marker="o", c=idx, cmap=ListedColormap(shades),
                        norm=norm, alpha=0.75, linewidths=0, zorder=3)
        cb = fig.colorbar(sc, cax=ax.inset_axes(KEY_BOX), orientation="horizontal", ticks=range(len(STEP_ORDER)))
        cb.ax.set_xticklabels([str(s) for s in STEP_ORDER])
        cb.ax.tick_params(colors=MUTED, labelsize=8, length=0, pad=2)
        cb.outline.set_edgecolor(MUTED)
        cb.outline.set_linewidth(0.6)
        cb.set_label(KEY_LABEL, color=MUTED, fontsize=9, labelpad=3)
        cb.solids.set_alpha(1.0)
        ax.set_xlabel(X_LABEL, color=INK)
        ax.set_ylabel(Y_LABEL, color=INK)
        style_axes(ax)
        # the legend's source dot in the 80-step shade, the key's middle, so that legend and key agree
        mask = Line2D([], [], linestyle="none", marker="o", markersize=6, color=shades[2], markeredgewidth=0)
        shuf = Line2D([], [], linestyle="none", marker="o", markersize=6, color=VERMILLION, markeredgewidth=0)
        leg = ax.legend([mask, shuf], [LABELS["mask"], LABELS["shuffled"]], frameon=True, fontsize=9, handlelength=1.0,
                        handletextpad=0.5, labelspacing=0.6, borderpad=0.7, fancybox=False, framealpha=1.0,
                        facecolor=LEGEND_FACE, edgecolor=LEGEND_EDGE, **CARRY_OVER_LEGEND)
        leg.get_frame().set_linewidth(0.8)
        for t in leg.get_texts():
            t.set_color(INK)
        tight_layout_at_pixel_ratio(fig)
        fig.savefig(path, facecolor="white")
        plt.close(fig)
    for scale in COPIES["carry_over"]:
        save_small_copy(path, scale)
    return Path(path)


def draw_registered(points: pd.DataFrame, refs: dict[str, float], path: Path) -> Path:
    """The scatter as registered in freeze file Part 1, Section 8: all eight rows, in added harm on both axes (own-batch harm less the search's
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
    for scale in COPIES["registered"]:
        save_small_copy(path, scale)
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
    paths = {"carry_over": draw_carry_over(points, refs, out_dir / OUT_NAMES["carry_over"]),
             "registered": draw_registered(points, refs, out_dir / OUT_NAMES["registered"])}
    for key in ("carry_over", "registered"):  # each drawing also wrote its reduced copies
        for scale in COPIES[key]:
            paths[f"{key}_{round(100 * scale)}"] = small_path(paths[key], scale)
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
