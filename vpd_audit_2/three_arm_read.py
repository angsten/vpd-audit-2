"""Plan 6 of the research log: the three-arm experiment's reading, committed before the run (the experiment's
specification (research log), its readings, with the plan's amendments 1 and 5 to 8). No GPU.

    uv run python -m vpd_audit_2.three_arm_read results/s7_three_arm

It reads the collected unit files (`.cache/s7_three_arm/units/`, each checked against the receipt `backup.json`),
refuses unless the gate passed and all six runs are present, and writes `reading.txt` and `record.json`.

Breakout (the earlier rule): the first batch b >= 2, batches numbered from 1, whose two-batch mean
(h[b - 1] + h[b]) / 2 reaches 5 nats. It is applied to three series per arm and seed:
  - "before": the harm on the fresh batch before its ascents. It governs the readings (amendment 5).
  - "loss": training's own loss, after the two warm-up ascents, on which the outer ascent is taken; this is the
    after-ascent series of amendment 5 and the specification, and it is reported beside the governing one.
  - "after": the harm after all three ascents, as description.
Where amendment 6's extension ran (seed 1), that arm and seed are read on the extended series, and its first 1,000
batches must equal the run's records exactly.

The readings, on the governing series, fixed now (the specification's, with amendments 6 to 8):
  - Reading 3 when arm 1 breaks out in both seeds: "co-training stopped the adversary, by the decomposition moving away
    or by its optimizer trapping it (the paper's line 2036); weakness per step alone does not explain the flaw".
  - Otherwise reading 1 when neither the yardstick (arm 3) nor arm 1 breaks out in either seed: undetermined; extend
    only with the author's approval.
  - Otherwise reading 2 when the yardstick breaks out in both seeds and arm 1 in neither: "within N batches, arm 1 did
    not reach the pattern that the yardstick reached at batch b", with N as a multiple of b, per seed; arm 2 then says
    whether sharing alone reaches it. The post never says "cannot reach": training had 400,000 batches.
  - Otherwise reading 4: the seeds disagree; undetermined.
Arm 4, the authors' newer recipe, was not run.

Beside them: amendment 1's pre-check, recomputed from the committed history `provenance/runs/s-55ea3f9b/
loss_history.csv`; arm 1's trend over its last 200 batches (amendment 6: the least-squares slope per 100 batches, and
the means of its first and last 200); the yardstick's settings carried to H1, H5, H9, H13; the gate and the rehearsal.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import three_arm as T

LEVEL = 5.0
SEEDS = (1, 2)
N_BATCHES = 1000
TREND_BATCHES = 200
TRAINING_KEY = "train/loss/PersistentPGDReconLoss"
TRAINING_STEPS = 400_000
EARLY_STEP = 40_000  # the first tenth of training
HISTORY = Path(__file__).resolve().parent.parent / "provenance" / "runs" / "s-55ea3f9b" / "loss_history.csv"
ARM_LABEL = {"released": "arm 1 (released: per text slot and position)", "per_document": "arm 2 (per document)",
             "batch": "arm 3 (yardstick: one source for the batch)"}
SENTENCES = {
    1: "Reading 1: the yardstick never broke out. Undetermined; extend only with the author's approval.",
    2: ("Reading 2: within {n} batches, arm 1 did not reach the pattern that the yardstick reached at batch {b}. Training had 400,000 "
        "batches; the post never says \"cannot reach\"."),
    3: ("Reading 3: arm 1 broke out. Co-training stopped the adversary, by the decomposition moving away or by its optimizer trapping "
        "the adversary (the paper's line 2036); this run cannot separate the two. Weakness per step alone does not explain the flaw."),
    4: "Reading 4: the seeds disagree. Undetermined.",
}


class Refusal(Exception):
    """The inputs are not the run's complete, checked set."""


def breakout(series: np.ndarray, level: float = LEVEL) -> int | None:
    """The first batch b >= 2 (numbered from 1) with (h[b-1] + h[b]) / 2 >= level; None if none."""
    h = np.asarray(series, dtype=np.float64)
    for b in range(2, h.size + 1):
        if 0.5 * (h[b - 2] + h[b - 1]) >= level:
            return b
    return None


def reading(arm1: dict[int, int | None], yard: dict[int, int | None]) -> int:
    """The reading's number from the breakout batches on the governing series, per seed."""
    if all(arm1[s] is not None for s in SEEDS):
        return 3
    if all(yard[s] is None for s in SEEDS) and all(arm1[s] is None for s in SEEDS):
        return 1
    if all(yard[s] is not None for s in SEEDS) and all(arm1[s] is None for s in SEEDS):
        return 2
    return 4


def trend(series: np.ndarray, last: int | None = None) -> dict[str, float]:
    """The least-squares slope over the last `last` batches (default 200), in nats per 100 batches, and the means of
    the first and last `last` batches."""
    last = TREND_BATCHES if last is None else last
    h = np.asarray(series, dtype=np.float64)
    x = np.arange(h.size - last, h.size, dtype=np.float64)
    slope = float(np.polyfit(x, h[-last:], 1)[0]) * 100.0
    return {"slope_per_100_batches": slope, "mean_last": float(h[-last:].mean()), "mean_first": float(h[:last].mean()), "batches": int(h.size)}


def training_log(path: Path = HISTORY) -> dict[str, Any]:
    """Amendment 1, recomputed from the committed history: the series' maximum, whether and where it reached 5 nats,
    its maximum after the first tenth of training, its mean by tenth, and its share of points above 2 nats."""
    steps, vals = [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["key"] == TRAINING_KEY:
                steps.append(int(r["step"]))
                vals.append(float(r["value"]))
    s, v = np.array(steps), np.array(vals)
    late = s >= EARLY_STEP
    tenths = [float(v[(s >= k * EARLY_STEP) & (s < (k + 1) * EARLY_STEP + (1 if k == 9 else 0))].mean()) for k in range(10)]
    above2 = v > 2.0
    return {"points": int(v.size), "max": float(v.max()), "step_of_max": int(s[v.argmax()]), "reached_5": bool((v >= 5.0).any()),
            "steps_at_or_above_5": s[v >= 5.0].tolist(), "max_after_first_tenth": float(v[late].max()), "step_of_that_max": int(s[late][v[late].argmax()]),
            "mean_by_tenth": tenths, "share_above_2": float(above2.mean()), "points_above_2_after_first_tenth": int((above2 & late).sum()),
            "last": float(v[-1])}


# ----------------------------------------------------------------------------- inputs


class Units:
    def __init__(self, folder: Path, receipt: dict[str, str]) -> None:
        self.folder, self.receipt = Path(folder), receipt

    def has(self, name: str) -> bool:
        return f"units/{name}.npz" in self.receipt

    def get(self, name: str) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        data = (self.folder / f"{name}.npz").read_bytes()
        if hashlib.sha256(data).hexdigest() != self.receipt.get(f"units/{name}.npz"):
            raise Refusal(f"{name} is not the file the receipt records")
        with np.load(io.BytesIO(data), allow_pickle=False) as z:
            arrays = {k: z[k] for k in z.files if k != "meta"}
            meta = json.loads(str(np.asarray(z["meta"]).reshape(-1)[0]))
        return arrays, meta


def run_name(stage: str, arm: str, seed: int, n: int) -> str:
    return f"{stage}_{arm}_s{seed}_n{n}"


def compute(results: Path, *, units_folder: Path | None = None) -> dict[str, Any]:
    from vpd_audit_2 import three_arm_run as TR

    results = Path(results)
    gate = json.load(open(results / "gate.json"))
    if not gate.get("passes"):
        raise Refusal("the gate did not pass")
    receipt = json.load(open(results / "backup.json"))
    if receipt.get("commit") != gate.get("commit"):
        raise Refusal("the units and the gate are not from one commit")
    units = Units(TR.LOCAL / TR.UNITS if units_folder is None else units_folder, receipt["files"])
    out: dict[str, Any] = {"commit": receipt["commit"], "gate": gate, "arms": {}}
    for arm in T.ARMS:
        for s in SEEDS:
            name = run_name("run", arm, s, N_BATCHES)
            if not units.has(name):
                raise Refusal(f"{name} is missing")
            arrays, meta = units.get(name)
            rec = {k: np.asarray(arrays[k], dtype=np.float64) for k in T.SERIES}
            entry: dict[str, Any] = {"batches_run": N_BATCHES, "extended": False}
            ext = [n for n in receipt["files"] if n.startswith(f"units/extension_{arm}_s{s}_n")]
            if ext:
                xname = ext[0][len("units/") : -len(".npz")]
                xa, xm = units.get(xname)
                same = all(np.array_equal(np.asarray(xa[k], dtype=np.float64)[:N_BATCHES], rec[k]) for k in T.SERIES)
                if not same:
                    raise Refusal(f"{xname}: its first {N_BATCHES} batches do not reproduce the run's records")
                rec = {k: np.asarray(xa[k], dtype=np.float64) for k in T.SERIES}
                entry.update(batches_run=int(xm["n_batches"]), extended=True, extension_reproduces_the_run=True)
            entry["breakout"] = {k: breakout(rec[k]) for k in T.SERIES}
            entry["final"] = {k: float(rec[k][-1]) for k in T.SERIES}
            entry["max"] = {k: float(rec[k].max()) for k in T.SERIES}
            entry["trend"] = {k: trend(rec[k]) for k in ("before", "loss")}
            entry["lr"] = sorted({float(x) for x in np.asarray(arrays["lr"]).tolist()})
            entry["seconds_per_batch"] = float(np.mean(arrays["seconds"][2:]))
            entry["peak_gib"] = float(arrays["peak_gib"][0])
            entry["grad_scale"] = meta["grad_scale"]
            out["arms"][f"{arm}|s{s}"] = entry
    b = {arm: {s: out["arms"][f"{arm}|s{s}"]["breakout"]["before"] for s in SEEDS} for arm in T.ARMS}
    n = reading(b["released"], b["batch"])
    out["reading"] = {"number": n, "on": "before", "breakouts": b}
    if n == 2:
        out["reading"]["per_seed"] = [{"seed": s, "batches": out["arms"][f"released|s{s}"]["batches_run"], "yardstick": b["batch"][s],
                                       "multiple": out["arms"][f"released|s{s}"]["batches_run"] / b["batch"][s]} for s in SEEDS]
    bl = {arm: {s: out["arms"][f"{arm}|s{s}"]["breakout"]["loss"] for s in SEEDS} for arm in T.ARMS}
    out["reading_on_the_loss_series"] = {"number": reading(bl["released"], bl["batch"]), "breakouts": bl}
    out["training_log"] = training_log()
    for name in ("rehearsal.json", "checkpoint_check.json", "extension_plan.json", "carry_plan.json"):
        p = results / name
        out[name.split(".")[0]] = json.load(open(p)) if p.is_file() else None
    if units.has("carry"):
        _, cm = units.get("carry")
        out["carry"] = cm
    return out


# ----------------------------------------------------------------------------- the report


def _b(x: int | None) -> str:
    return "never" if x is None else f"batch {x}"


def report(r: dict[str, Any]) -> str:
    L = ["The three-arm experiment (plan 6 of the research log; the experiment's specification with the plan's eight amendments): training's persistent",
         "adversary against the released decomposition held frozen, 1,000 batches of 64 unused attack-side texts per arm and seed.",
         "Breakout: the two-batch mean of the harm reaches 5 nats. The governing series is the harm on the fresh batch before its",
         "ascents (amendment 5); training's own loss is beside it.", ""]
    g = r["gate"]
    L.append(f"Gate: {'passed' if g['passes'] else 'FAILED'}. Released scope, our step against the authors' training sequence: loss bit for bit "
             f"{g['arms']['released']['loss_bits_equal']}, sources bit for bit {g['arms']['released']['sources_bits_equal']}; scaled gradient "
             f"mismatches {g['scaled_gradient']['mismatches']} of {g['scaled_gradient']['entries_compared']}; per-document loss bit for bit "
             f"{g['per_document_loss_bits_equal']}.")
    L.append("")
    rd = r["reading"]
    L.append(f"THE READING (governing series): {SENTENCES[rd['number']].split(':')[0].upper()}.")
    if rd["number"] == 2:
        for x in rd["per_seed"]:
            L.append("  " + SENTENCES[2].format(n=x["batches"], b=x["yardstick"]) + f" ({x['batches']} batches = {x['multiple']:.1f} times {x['yardstick']}; seed {x['seed']}.)")
        pd = rd["breakouts"]["per_document"]
        L.append(f"  Arm 2 (per document): {', '.join(f'seed {s} {_b(pd[s])}' for s in SEEDS)}; arm 4 was not run.")
    else:
        L.append("  " + SENTENCES[rd["number"]])
    L.append(f"  On training's own loss series instead, the rule would give reading {r['reading_on_the_loss_series']['number']} (beside it, not the reading).")
    L += ["", "Breakout batch by arm and seed (governing series before; training's loss; after all three ascents), and the run's length:"]
    for key, e in r["arms"].items():
        arm, s = key.split("|")
        L.append(f"  {ARM_LABEL[arm]}, seed {s[1:]}: before {_b(e['breakout']['before'])}; loss {_b(e['breakout']['loss'])}; after "
                 f"{_b(e['breakout']['after'])}; {e['batches_run']} batches{' (extended; its first 1,000 reproduce the run)' if e['extended'] else ''}; "
                 f"final before {e['final']['before']:.3f}, loss {e['final']['loss']:.3f}; max before {e['max']['before']:.3f}.")
    L += ["", "Arm 1's trend over its last 200 batches (amendment 6):"]
    for s in SEEDS:
        e = r["arms"][f"released|s{s}"]
        for k in ("before", "loss"):
            t = e["trend"][k]
            L.append(f"  seed {s}, {k}: slope {t['slope_per_100_batches']:+.4f} nats per 100 batches; mean of the first 200 {t['mean_first']:.4f}, "
                     f"of the last 200 {t['mean_last']:.4f} (of {t['batches']}).")
    tl = r["training_log"]
    L += ["", "Amendment 1, recomputed from the committed training history (`train/loss/PersistentPGDReconLoss`, every 200 steps):",
          f"  {tl['points']} points; maximum {tl['max']:.3f} at step {tl['step_of_max']}; reached 5 nats: {tl['reached_5']} "
          f"(steps {tl['steps_at_or_above_5']}); after step 40,000 the maximum is {tl['max_after_first_tenth']:.3f} at step {tl['step_of_that_max']}; "
          f"share of points above 2 nats {tl['share_above_2']:.3f}, of them after step 40,000: {tl['points_above_2_after_first_tenth']}; last {tl['last']:.3f}.",
          "  Mean by tenth of training: " + ", ".join(f"{x:.3f}" for x in tl["mean_by_tenth"]) + "."]
    if r.get("carry"):
        L += ["", "Arm 3's settings carried to H1, H5, H9 and H13 (description; the lead's scoring path):"]
        harms = r["carry"]["harms"]
        for st in r["carry"]["settings"]:
            vals = [harms[h][st["key"]] for h in sorted(harms)]
            own = r["arms"][f"batch|s{st['seed']}"]
            L.append(f"  seed {st['seed']}, {st['label']} (batch {st['batch']}): " + ", ".join(f"{h} {harms[h][st['key']]:.3f}" for h in sorted(harms))
                     + f"; mean {np.mean(vals):.3f} nats.")
    if r.get("rehearsal"):
        L += ["", "Rehearsal (calibration rows, 20 batches per arm): " + "; ".join(
            f"{a} {x['seconds_per_batch']:.3f} s per batch, peak {x['peak_gib']:.1f} GiB" for a, x in r["rehearsal"]["arms"].items()) + "."]
    if r.get("checkpoint_check"):
        c = r["checkpoint_check"]
        L.append(f"Checkpoint check (amendment 2): the released checkpoint holds persistent sources or their Adam state: {c['holds_persistent_sources']} "
                 f"({c['n_keys']} keys); so arm 1 has {'a resumed start' if c['holds_persistent_sources'] else 'no resumed start'}.")
    if r.get("extension_plan"):
        x = r["extension_plan"]
        L.append(f"Extension (amendment 6): yardstick seed 1 breakout {_b(x['yardstick_breakout'])}; extended: {x['containers'] or 'nothing'}.")
    L.append("Arm 4 (the authors' newer pooled-particle recipe): not run; nothing we hold fixes its mechanics.")
    return "\n".join(L) + "\n"


def _jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    return x


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.stderr.write("usage: python -m vpd_audit_2.three_arm_read results/s7_three_arm\n")
        return 2
    results = Path(argv[0])
    out = compute(results)
    text = report(out)
    (results / "reading.txt").write_text(text)
    (results / "record.json").write_text(json.dumps(_jsonable(out), indent=1, sort_keys=True) + "\n")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
