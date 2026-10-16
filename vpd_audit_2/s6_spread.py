"""Plan 2 of the research log: how the harm is spread over texts (`results/s6_followups/CONVENTIONS.md`, Section 6). Description;
no GPU.

    uv run python -m vpd_audit_2.s6_spread

The settled answers to the questions raised by the first wave's report: the Spearman correlations with another
attack batch and with another start use every other one, averaged within the cell, then the mean over cells, with the
count of partners printed beside each; statistics 1 and 2 are on the harm, the literal text (0.75 nats is a harm
level), and the two concentration measures on the added harm; the 11 held-out texts whose spans overlap attack rows are
kept, as "the batch's 128 texts" says, and one line gives their count and how much the lead analysis's intervals moved
when it recomputed without them (read from `results/s5_lead/analysis/lead_records.json`). Any other value of
`PARTNER_BATCHES`, `PARTNER_STARTS`, or `DROP_OVERLAPPING` is refused, not silently ignored.

For every carried cell (attack batch i, held-out batch j, start s) at each of the five search lengths and three harm
levels, a text's added harm is its harm under the carried setting minus its harm under the same start on the same text
(`carried_text - init_H_text`). Four statistics over the batch's texts:

  1. the share of texts whose harm exceeds the 0.75-nat benchmark;
  2. the harm of the 10th-percentile text, the 13th lowest of 128;
  3. the share of the cell's added harm carried by its 13 most-harmed texts, negative added harms counted as zero
     (0.10 is an even spread), undefined where every added harm is at most zero;
  4. the median text's added harm divided by the mean, negative values counted as zero in both, undefined likewise.

The share of texts with negative added harm is printed beside the last two. Each statistic is summarized over cells by
its median with the 10th and 90th percentiles (numpy's linear interpolation), with no interval; the same are printed for
the held-out batches' own searches and for the shuffled copies, as reference rows. A setting a search never reached (a
harm level it did not cross) has no cell.

Whether the same texts are hit: the mean over cells of the Spearman correlation over the texts (average ranks for ties)
between a carried setting's added harm and, in turn: the held-out batch's own search (same start, same row); a carried
setting from another attack batch (same start); the carried setting from the same attack batch and another start; and
the start's own per-text harm. A text's harm is a mean over 512 positions, so "most texts" does not imply "most
positions".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env
from vpd_audit_2 import lead_table as LT

TABLE = env.REPO_ROOT / "results" / "s5_lead" / "lead" / "sealed"
RECEIPT = env.REPO_ROOT / "results" / "s5_lead" / "lead" / "receipt.json"
LEAD_RECORDS = env.REPO_ROOT / "results" / "s5_lead" / "analysis" / "lead_records.json"
OVERLAP_JSON = env.REPO_ROOT / "data" / "manifest" / "heldout_span_overlap.json"
ROWS = ("n20", "n40", "n80", "n160", "n320", "h2", "h5", "h10")
BENCHMARK = 0.75
TOP_TEXTS = 13  # 10 percent of 128
PERCENTILE_TEXT = 13  # the 13th lowest
SUMMARY_PERCENTILES = (10, 50, 90)
OPEN_QUESTIONS_SETTLED = True  # settled after the first wave's report
PARTNER_BATCHES = "every_other"
PARTNER_STARTS = "every_other"
DROP_OVERLAPPING = False
STATS_1_2_ON = "harm"  # or "added"


class Refusal(Exception):
    pass


# ----------------------------------------------------------------------------- the four statistics, over the last axis


def share_above(harm: np.ndarray, benchmark: float = BENCHMARK) -> np.ndarray:
    return np.mean(np.asarray(harm, dtype=np.float64) > benchmark, axis=-1)


def kth_lowest(x: np.ndarray, k: int = PERCENTILE_TEXT) -> np.ndarray:
    return np.sort(np.asarray(x, dtype=np.float64), axis=-1)[..., k - 1]


def top_share(added: np.ndarray, n: int = TOP_TEXTS) -> np.ndarray:
    a = np.clip(np.asarray(added, dtype=np.float64), 0.0, None)
    total = a.sum(axis=-1)
    top = np.sort(a, axis=-1)[..., -n:].sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(total > 0, top / np.where(total > 0, total, 1.0), np.nan)


def median_over_mean(added: np.ndarray) -> np.ndarray:
    a = np.clip(np.asarray(added, dtype=np.float64), 0.0, None)
    mean = a.mean(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(mean > 0, np.median(a, axis=-1) / np.where(mean > 0, mean, 1.0), np.nan)


def share_negative(added: np.ndarray) -> np.ndarray:
    return np.mean(np.asarray(added, dtype=np.float64) < 0, axis=-1)


def four(harm: np.ndarray, added: np.ndarray) -> dict[str, np.ndarray]:
    """The four statistics and the share negative, per cell; every one undefined (NaN) for a cell whose harms are not all
    finite, as for a setting the search never reached."""
    if STATS_1_2_ON not in ("harm", "added"):
        raise Refusal("STATS_1_2_ON is 'harm' or 'added'")
    harm, added = np.asarray(harm, dtype=np.float64), np.asarray(added, dtype=np.float64)
    defined = np.isfinite(harm).all(axis=-1) & np.isfinite(added).all(axis=-1)
    on = harm if STATS_1_2_ON == "harm" else added
    with np.errstate(invalid="ignore"):
        stats = {"share_above_benchmark": share_above(on), "tenth_percentile_text": kth_lowest(on), "top_13_share": top_share(added),
                 "median_over_mean": median_over_mean(added), "share_negative": share_negative(added)}
    return {k: np.where(defined, v, np.nan) for k, v in stats.items()}


def summary(values: np.ndarray) -> dict[str, Any]:
    v = np.asarray(values, dtype=np.float64).ravel()
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"cells": 0, "p10": None, "median": None, "p90": None}
    p10, med, p90 = np.percentile(v, SUMMARY_PERCENTILES)
    return {"cells": int(v.size), "p10": float(p10), "median": float(med), "p90": float(p90)}


# ----------------------------------------------------------------------------- Spearman, over the last axis


def ranks(x: np.ndarray) -> np.ndarray:
    """Average ranks along the last axis (ties share the mean of their ranks), as scipy's `rankdata`."""
    from scipy.stats import rankdata

    return rankdata(np.asarray(x, dtype=np.float64), axis=-1)


def spearman(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Spearman's correlation along the last axis: Pearson's on average ranks; NaN where either side is constant or
    undefined."""
    x, y = np.broadcast_arrays(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64))
    bad = ~(np.isfinite(x).all(axis=-1) & np.isfinite(y).all(axis=-1))
    rx, ry = ranks(np.where(np.isfinite(x), x, 0.0)), ranks(np.where(np.isfinite(y), y, 0.0))
    rx = rx - rx.mean(axis=-1, keepdims=True)
    ry = ry - ry.mean(axis=-1, keepdims=True)
    den = np.sqrt((rx ** 2).sum(axis=-1) * (ry ** 2).sum(axis=-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where(den > 0, (rx * ry).sum(axis=-1) / np.where(den > 0, den, 1.0), np.nan)
    return np.where(bad, np.nan, r)


def mean_partner_correlation(added: np.ndarray, axis: int) -> tuple[np.ndarray, np.ndarray]:
    """For each cell, the mean of its Spearman correlations with every other cell along `axis` (the other attack
    batches, or the other starts), the rest of its index the same, undefined partners left out; and how many partners
    each cell's mean is over (0 where the cell itself is undefined)."""
    n = added.shape[axis]
    means, counts = [], []
    for i in range(n):
        own = np.take(added, i, axis=axis)
        rs = np.stack([spearman(own, np.take(added, k, axis=axis)) for k in range(n) if k != i])
        k = np.isfinite(rs).sum(axis=0)
        with np.errstate(invalid="ignore"):
            means.append(np.where(k > 0, np.nansum(rs, axis=0) / np.maximum(k, 1), np.nan))
        counts.append(k)
    return np.stack(means, axis=axis), np.stack(counts, axis=axis)


def partner_counts(corr: np.ndarray, counts: np.ndarray) -> dict[str, Any]:
    """The partners each defined cell's correlation is over: least, most, and mean."""
    k = np.asarray(counts)[np.isfinite(corr)]
    if k.size == 0:
        return {"min": None, "max": None, "mean": None}
    return {"min": int(k.min()), "max": int(k.max()), "mean": float(k.mean())}


def overlap_effect(records: Path | None = None, overlap: Path | None = None) -> dict[str, Any]:
    """The overlapping held-out texts' count, and how far the lead analysis's interval ends moved when it recomputed both
    tables without them: the largest change over the intervals of means (in nats) and of ratios, unrounded."""
    r = json.load(open(LEAD_RECORDS if records is None else records))
    n = len(json.load(open(OVERLAP_JSON if overlap is None else overlap))["texts"])
    main, without = r["main"], r["without_overlapping_texts"]["tables"]
    moved: dict[str, list[float]] = {"mean": [], "ratio": []}

    def walk(a: Any, b: Any, key: str, kind: str | None) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            kind = a["kind"] if isinstance(a.get("kind"), str) else kind
            for k in a:
                if k in b:
                    walk(a[k], b[k], k, kind)
        elif isinstance(a, list) and isinstance(b, list):
            if "interval" in key and len(a) == len(b) == 2 and all(isinstance(x, (int, float)) for x in a + b):
                if kind in moved:
                    moved[kind].append(max(abs(a[0] - b[0]), abs(a[1] - b[1])))
            else:
                for x, y in zip(a, b):
                    walk(x, y, key, kind)

    walk(main, without, "", None)
    return {"texts": n, "excluded_in_lead_analysis": int(r["without_overlapping_texts"]["excluded_texts"]),
            "intervals_of_means": len(moved["mean"]), "largest_move_means_nats": max(moved["mean"]),
            "intervals_of_ratios": len(moved["ratio"]), "largest_move_ratios": max(moved["ratio"])}


# ----------------------------------------------------------------------------- the table


def load(table_dir: Path | None = None, receipt: Path | None = None) -> dict[str, Any]:
    """The lead table, each file checked against the run's receipt before it is read."""
    table_dir = TABLE if table_dir is None else Path(table_dir)
    rec = json.load(open(RECEIPT if receipt is None else receipt))
    for f in rec["files"]:
        if LT.sha256_file(table_dir / f["name"]) != f["sha256"]:
            raise Refusal(f"{f['name']} is not the file the receipt records")
    table = LT.load_table(table_dir)
    if not LT.has_per_text(table):
        raise Refusal("the table has no per-text values")
    return table


def spread(table: dict[str, Any]) -> dict[str, Any]:
    if (PARTNER_BATCHES, PARTNER_STARTS, DROP_OVERLAPPING) != ("every_other", "every_other", False):
        raise Refusal("only every other partner, with every text kept, is implemented")
    names = [str(x) for x in table["setting_names"]]
    init = table["init_H_text"].astype(np.float64)  # [KH, ns, T]
    out: dict[str, Any] = {}
    for row in ROWS:
        q = names.index(row)
        harm = table["carried_text"][:, :, :, q, :].astype(np.float64)  # [KA, KH, ns, T]
        added = harm - init[None]
        own_harm = table["own_H_text"][:, :, q, :].astype(np.float64)  # [KH, ns, T]
        own_added = own_harm - init
        res: dict[str, Any] = {"carried": {k: summary(v) for k, v in four(harm, added).items()},
                               "own_searches": {k: summary(v) for k, v in four(own_harm, own_added).items()}}
        if bool(table["has_shuffles"][q]):
            sh = table["shuf_text"][:, :, :, q, :, :].astype(np.float64)  # [KA, KH, ns, R, T]
            res["shuffled_copies"] = {k: summary(v) for k, v in four(sh, sh - init[None, :, :, None, :]).items()}
        own_c = spearman(added, own_added[None])
        start_c = spearman(added, init[None])
        batch_c, batch_k = mean_partner_correlation(added, axis=0)
        starts_c, starts_k = mean_partner_correlation(added, axis=2)
        corr = {"own_search": (own_c, np.isfinite(own_c).astype(np.int64)), "another_attack_batch_same_start": (batch_c, batch_k),
                "same_attack_batch_another_start": (starts_c, starts_k), "start_own_harm": (start_c, np.isfinite(start_c).astype(np.int64))}
        # the conventions ask for the mean over cells; the spread over cells and the partner counts are kept beside it
        res["spearman"] = {k: {"mean": float(np.nanmean(c)) if np.isfinite(c).any() else None, **summary(c), "partners": partner_counts(c, n)}
                           for k, (c, n) in corr.items()}
        out[row] = res
    return out


STAT_LABELS = (("share_above_benchmark", "share of texts above 0.75 nats"), ("tenth_percentile_text", "harm of the 13th lowest text"),
               ("top_13_share", "share carried by the 13 most-harmed texts"), ("median_over_mean", "median over mean added harm"),
               ("share_negative", "share of texts with negative added harm"))
CORR_LABELS = (("own_search", "the held-out batch's own search"), ("another_attack_batch_same_start", "another attack batch, same start"),
               ("same_attack_batch_another_start", "the same attack batch, another start"), ("start_own_harm", "the start's own harm"))


def _cell(s: dict[str, Any]) -> str:
    if not s["cells"]:
        return "no cells"
    return f"{s['median']:.2f} ({s['p10']:.2f} to {s['p90']:.2f}), {s['cells']} cells"


def _partners(p: dict[str, Any]) -> str:
    if p["min"] is None:
        return "no partners"
    if p["min"] == p["max"]:
        return f"{p['min']} partner{'s' if p['min'] != 1 else ''} per cell"
    return f"{p['min']} to {p['max']} partners per cell, mean {p['mean']:.2f}"


def report(out: dict[str, Any], overlap: dict[str, Any]) -> str:
    L = ["How the harm is spread over texts (plan 2 of the research log; conventions, Section 6). Description only; no interval.",
         "Each statistic: its median over cells, with the 10th and 90th percentiles over cells in parentheses. Added harm is the",
         "text's harm under the setting less its harm under the same start. Statistics 1 and 2 are on the harm (0.75 nats is a",
         "harm level); the two concentration measures are on the added harm, negative values counted as zero. A text's harm is",
         "a mean over 512 positions, so \"most texts\" does not imply \"most positions\".",
         f"The {overlap['texts']} held-out texts whose spans overlap attack rows are kept, as the batch's 128 texts. The lead analysis",
         f"recomputed both tables without them: its {overlap['intervals_of_ratios']} intervals of ratios moved by at most "
         f"{overlap['largest_move_ratios']:.4f} at either end, and its {overlap['intervals_of_means']} intervals in nats by at most "
         f"{overlap['largest_move_means_nats']:.3f} nats.", ""]
    for row, res in out.items():
        L.append(f"{row}:")
        for kind, title in (("carried", "carried settings"), ("own_searches", "reference: the held-out batches' own searches"),
                            ("shuffled_copies", "reference: the shuffled copies")):
            if kind not in res:
                continue
            L.append(f"  {title}")
            for key, label in STAT_LABELS:
                L.append(f"    {label}: {_cell(res[kind][key])}")
        L.append("  Spearman correlation over texts, mean over cells, of a carried setting's added harm with:")
        for key, label in CORR_LABELS:
            c = res["spearman"][key]
            L.append(f"    {label}: {'undefined' if c['mean'] is None else format(c['mean'], '.2f')} ({_partners(c['partners'])}; "
                     f"{c['cells']} cells)")
        L.append("")
    return "\n".join(L)


def main() -> int:
    from vpd_audit_2 import s6_record

    if not OPEN_QUESTIONS_SETTLED:
        raise Refusal("the conventions' open questions for Section 6 are not settled (see this module's docstring)")
    overlap = overlap_effect()
    out = spread(load())
    sys.stdout.write(report(out, overlap))
    s6_record.update("spread", {"overlapping_texts": overlap, "rows": out})
    return 0


if __name__ == "__main__":
    sys.exit(main())
