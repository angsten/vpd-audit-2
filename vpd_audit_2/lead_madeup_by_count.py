"""Description beside the made-up-data test of record: coverage split by the number of early-breakout batches.

    uv run python -m vpd_audit_2.lead_madeup_by_count [--processes N]

For every "large" core cell of the test of record (the amended generator, master seed 20261006), the coverage of the
unwidened interval split by the number of type-C5 held-out batches in the experiment (0, 1, 2, 3 or more); and for the
carry-over and shuffled ratios at 20 steps, the same split by the number of type-C5 attack batches. Type C5 is the
pilot's one batch in eight whose searches break out early.

The experiments are the record's own: the same seed, the same draws, and the same sample each cell was judged on (the
first 2,000 in which the row is read, or the rerun's 10,000 where the cell was rerun). Each cell's overall coverage is
checked against the committed report before anything is written, so the split is of the judged sample and nothing
else. Nothing is adjusted and no number of record changes. Written to `results/s5_madeup/by_early_breakout_count.{json,md}`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_madeup as M

OUT_DIR = M.OUT_DIR
BINS = ("0", "1", "2", "3 or more")
CELLS_LARGE = [(row, "large", "heldout") for row in M.ALL_ROWS if row != "n20"]
CELLS_20 = [("n20", "carries", "attack"), ("n20", "depends", "attack")]
WANTED = tuple(M.ALL_ROWS)


def _generate(task: tuple[str, int, int, int, int]) -> dict[str, Any]:
    """Experiments [e0, e1) of one core scenario under the record's seed: per experiment, the two C5 counts, and per row
    whether it is read and the estimate and half-width of the three signed readings."""
    scn_id, master, phase, e0, e1 = task
    st = M._worker_state()
    R, scn, pop = st["R"], st["scenarios"][scn_id], st["population"][scn_id]
    n = e1 - e0
    counts = np.zeros((n, 2), dtype=np.int64)
    read = np.zeros((n, len(WANTED)), dtype=bool)
    vals = np.full((n, len(WANTED), 3, 2), np.nan)
    for k, e in enumerate(range(e0, e1)):
        rng = M.experiment_rng(master, 1, phase, st["number"][scn_id], e)
        s = M.draw_searches(rng, R, scn, "amended")
        counts[k] = (s["types_H"] == M.C5).sum(), (s["types_A"] == M.C5).sum()
        for r, row in enumerate(scn.rows):
            arrays = M.row_cells(rng, scn, pop[row], s, row)
            read[k, r] = row in M.ROW_STEP or M.level_is_read(arrays)
            if read[k, r]:
                v = M.row_statistics(arrays, None)
                for j, stat in enumerate(M.SIGNED):
                    vals[k, r, j] = v[M.S[stat], M.F["est"]], v[M.S[stat], M.F["hw"]]
    return {"e0": e0, "counts": counts, "read": read, "vals": vals}


def judged_sample(pool: Any, scn_id: str, master: int, phase: int, n_target: int, rows_needed: list[str]) -> dict[str, Any]:
    """The experiments each row was judged on, by the harness's rule: generated in rounds of `n_target` until each
    harm-level row has `n_target` read, or ten times as many have been generated."""
    parts: list[dict[str, Any]] = []
    e0 = 0
    need = list(rows_needed)
    while need and e0 < M.GENERATED_CAP_FACTOR * n_target:
        tasks = [(scn_id, master, phase, a, min(a + M.CHUNK, e0 + n_target)) for a in range(e0, e0 + n_target, M.CHUNK)]
        parts += pool.map(_generate, tasks)
        e0 += n_target
        read = np.concatenate([p["read"] for p in parts])
        need = [row for row in need if row in M.ROW_LEVEL and read[:, WANTED.index(row)].sum() < n_target]
    counts = np.concatenate([p["counts"] for p in parts])
    read = np.concatenate([p["read"] for p in parts])
    vals = np.concatenate([p["vals"] for p in parts])
    out = {}
    for row in rows_needed:
        r = WANTED.index(row)
        keep = np.flatnonzero(read[:, r])[:n_target]
        out[row] = {"counts": counts[keep], "vals": vals[keep, r]}
    return out


def split(d: np.ndarray, w: np.ndarray, count: np.ndarray) -> dict[str, Any]:
    out = {}
    for label, pick in zip(BINS, (count == 0, count == 1, count == 2, count >= 3)):
        ok = pick & np.isfinite(d) & np.isfinite(w)
        n = int(ok.sum())
        out[label] = {"n": n, "share": float(pick.mean()), "coverage": float((np.abs(d[ok]) <= w[ok]).mean()) if n else None,
                      "above": float((d[ok] > w[ok]).mean()) if n else None, "below": float((d[ok] < -w[ok]).mean()) if n else None,
                      "mean_error": float(d[ok].mean()) if n else None, "median_half_width": float(np.median(w[ok])) if n else None}
    return out


def run(pool: Any, log: Any = None) -> dict[str, Any]:
    log = log or (lambda *a: None)
    record = json.load(open(OUT_DIR / "report.json"))
    assert record["version"] == "amended" and record["seeds"]["master"] == M.MASTER_SEED
    master = record["seeds"]["master"]
    n, n_rerun = record["sizes"]["experiments"], record["sizes"]["rerun"]
    by_cell = {(c["scenario"], c["row"], c["statistic"]): c for c in record["core_cells"]}
    truths = record["truths"]
    out: dict[str, Any] = {"what": "Coverage of the test of record's core cells, split by the number of type-C5 batches on one side. Description only; "
                                   "the experiments are the record's own and nothing is adjusted. Every number is made up.",
                           "seed": master, "version": "amended", "record_report_sha256": hashlib.sha256((OUT_DIR / "report.json").read_bytes()).hexdigest(),
                           "cells": []}
    for scn in M.scenarios():
        if scn.kind != "core":
            continue
        t0 = time.time()
        wanted = [(row, stat, side) for row, stat, side in CELLS_LARGE + CELLS_20]
        rerun_rows = sorted({row for row, stat, _ in wanted if by_cell[(scn.id, row, stat)]["rerun"]}, key=M.ALL_ROWS.index)
        first = judged_sample(pool, scn.id, master, 0, n, list(M.ALL_ROWS))
        rerun = judged_sample(pool, scn.id, master, 1, n_rerun, rerun_rows) if rerun_rows else {}
        for row, stat, side in wanted:
            c = by_cell[(scn.id, row, stat)]
            sample = rerun[row] if c["rerun"] else first[row]
            j = M.SIGNED.index(stat)
            d = sample["vals"][:, j, 0] - truths[scn.id][row]["truth"][stat]
            w = sample["vals"][:, j, 1]
            ok = np.isfinite(d) & np.isfinite(w)
            coverage = float((np.abs(d[ok]) <= w[ok]).mean())
            if int(ok.sum()) != c["judged_on"] or abs(coverage - c["coverage"]) > 1e-12:
                raise RuntimeError(f"the regenerated sample for {scn.id} {row} {stat} does not reproduce the record")
            count = sample["counts"][:, 0 if side == "heldout" else 1]
            out["cells"].append({"scenario": scn.id, "row": row, "statistic": stat, "side": side, "judged_on": c["judged_on"], "rerun": c["rerun"],
                                 "coverage": coverage, "fail": c["fail"], "by_count": split(d, w, count)})
        log(f"  {scn.id}: {time.time() - t0:.0f} s")
    return out


def _grid(cells: list[dict[str, Any]], stat: str, label: str, key: str = "coverage") -> list[str]:
    scns = [f"P{k}" for k in range(1, 14)]
    rows = [r for r in M.ALL_ROWS if any(c["row"] == r and c["statistic"] == stat for c in cells)]
    out = ["| Row | " + " | ".join(scns) + " |", "|---|" + "---|" * len(scns)]
    for row in rows:
        vals = []
        for s in scns:
            c = next((c for c in cells if c["scenario"] == s and c["row"] == row and c["statistic"] == stat), None)
            v = c["by_count"][label][key] if c else None
            vals.append("" if v is None else (f"{v:.3f}" if key != "n" else str(v)))
        out.append(f"| {row} | " + " | ".join(vals) + " |")
    return out


def markdown(out: dict[str, Any]) -> str:
    cells = out["cells"]
    lines = ["# Coverage by the Number of Early-Breakout Batches: the Test of Record", "",
             out["what"], "",
             f"Seed {out['seed']}, the amended generator; the judged sample of each cell (2,000 experiments, or the rerun's 10,000 where the cell "
             "was rerun), reproduced from the committed report and checked against it cell by cell. An early-breakout batch is one drawn as "
             "the pilot's type C5, whose own-search harm at 20 steps is twice the other types'. A side of 16 holds none with probability "
             "(7/8)^16 = 11.8 percent, one with 27.0 percent, two with 28.9 percent, three or more with 32.3 percent.", ""]
    lines += ["## The \"Large\" Difference, by the Number of Early-Breakout Held-Out Batches", "",
              "The yardstick for \"large\" is the held-out batches' own 20-step harm. Coverage of the unwidened interval, per core cell:", ""]
    for label in BINS:
        lines += [f"### {label} early-breakout held-out batch{'es' if label != '1' else ''}", ""] + _grid(cells, "large", label) + [""]
    lines += ["### Share of intervals wholly above the truth, with 0 early-breakout held-out batches", ""] + _grid(cells, "large", "0", "above") + [""]
    lines += ["## The Two Ratios at 20 Steps, by the Number of Early-Breakout Attack Batches", ""]
    for stat, word in (("carries", "Carry-over ratio"), ("depends", "Shuffled ratio")):
        lines += [f"### {word}", "", "| Scenario | Judged on | Coverage | " + " | ".join(f"{b}: n, coverage, below" for b in BINS) + " |",
                  "|---|---|---|" + "---|" * len(BINS)]
        for c in cells:
            if c["statistic"] == stat:
                parts = []
                for b in BINS:
                    v = c["by_count"][b]
                    parts.append(f"{v['n']}, {v['coverage']:.3f}, {v['below']:.3f}" if v["n"] else "none")
                lines.append(f"| {c['scenario']} | {c['judged_on']} | {c['coverage']:.4f} | " + " | ".join(parts) + " |")
        lines.append("")
    lines += ["## Every Cell in Full", "",
              "| Scenario | Row | Statistic | Split by | Judged on | Coverage | " + " | ".join(f"{b}: n, coverage, above, below, mean error, median half-width" for b in BINS) + " |",
              "|---|---|---|---|---|---|" + "---|" * len(BINS)]
    for c in cells:
        parts = []
        for b in BINS:
            v = c["by_count"][b]
            parts.append(f"{v['n']}, {v['coverage']:.3f}, {v['above']:.3f}, {v['below']:.3f}, {v['mean_error']:+.4f}, {v['median_half_width']:.4f}" if v["n"] else "none")
        lines.append(f"| {c['scenario']} | {c['row']} | {c['statistic']} | {c['side']} side | {c['judged_on']} | {c['coverage']:.4f} | " + " | ".join(parts) + " |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processes", type=int, default=max(1, (mp.cpu_count() or 2) - 2))
    args = ap.parse_args(argv)
    t0 = time.time()
    with mp.get_context("spawn").Pool(args.processes) as pool:
        out = run(pool, log=lambda *a: print(*a, file=sys.stderr, flush=True))
    out["seconds"] = round(time.time() - t0, 1)
    (OUT_DIR / "by_early_breakout_count.json").write_text(json.dumps(out, indent=1) + "\n")
    (OUT_DIR / "by_early_breakout_count.md").write_text(markdown(out))
    print(f"written in {out['seconds']} s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
