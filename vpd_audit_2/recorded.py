"""The recorded 320-step runs of session 4 (plan 1, item 6; plan 2, item 5; plan 3, Section 3). Not gating.

Our micro-batched loop in bf16 autocast on all 128 texts of C1 from start (master, "start", 1), step 0.1, labels, target,
and weight deltas computed once on the whole batch under bf16 autocast (as G1 computed them), then sliced per micro-batch.
Two runs on a B200 (micro-batch 8 and 16) and one on an A100-80GB (16). Each saves the harm after every step, the wall
time, and, through the save hook, the source after steps n - 1 and n for n in {20, 40, 80, 160, 320} and at the first step
whose two-step mean of harm reaches 2, 5, and 10 nats.

The scoring timing: one forward-only bf16 pass over C1's 128 texts with C1's own source (the last run's final source),
the labels and target precomputed: the mean of 5 repeats after one warm-up, for the whole batch and in chunks of 16; and
the time to compute the labels and target (the mean of 5 repeats after the run's own computation).

The readings against G1's trajectory `A_c|C1|320` are made locally by `readings`.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A

N_STEPS = 320
STEP = 0.1
BUDGETS = (20, 40, 80, 160, 320)
ODD = (19, 39, 79, 159, 319)


def _sync(device: str) -> None:
    import torch

    if device == "cuda":
        torch.cuda.synchronize()


def runs(model: Any, ids: np.ndarray, start: dict[str, np.ndarray], sizes: tuple[int, ...], out_dir: Path, tag: str, device: str = "cuda",
         log: Any = print) -> dict[str, Any]:
    import torch

    t = time.time()
    prep = A.prepare(model, ids, "bf16", device=device)
    _sync(device)
    out: dict[str, Any] = {"labels_target_seconds_first": time.time() - t, "runs": {}}
    out_dir.mkdir(parents=True, exist_ok=True)
    for m in sizes:
        torch.cuda.reset_peak_memory_stats() if device == "cuda" else None
        hook = A.SaveHook()
        r = A.run(model, prep, start, N_STEPS, STEP, micro_batch=m, save_hook=hook, device=device)
        path = out_dir / f"{tag}_mb{m}.npz"
        np.savez(path, **{f"saved|{k}": v for k, v in hook.saved.items()}, **{f"final|{k}": v for k, v in r["sources"].items()})
        out["runs"][str(m)] = {"micro_batch": m, "record": r["record"], "seconds": r["seconds"], "seconds_per_step": r["seconds"] / N_STEPS,
                               "save_hook_events": hook.events, "saved_file": str(path), "final": r["final"],
                               "peak_memory_gib": torch.cuda.max_memory_allocated() / 2**30 if device == "cuda" else None}
        last_sources = r["sources"]
        log(f"[recorded] {tag} mb{m}: final {r['final']:.4f}, {r['seconds'] / N_STEPS:.3f} s per step; hook {hook.events}")
    out["scoring"] = scoring_timing(model, prep, last_sources, device)
    times = []
    for _ in range(5):
        _sync(device)
        t = time.time()
        p = A.prepare(model, ids, "bf16", device=device)
        _sync(device)
        times.append(time.time() - t)
        del p
    out["labels_target_seconds"] = {"mean_of_5": float(np.mean(times)), "all": times}
    return out


def scoring_timing(model: Any, prep: A.Prepared, source: dict[str, np.ndarray], device: str) -> dict[str, Any]:
    import torch

    res = {}
    for name, mb in (("whole_batch", None), ("chunks_of_16", 16)):
        try:
            A.score(model, source, prep, micro_batch=mb, device=device)  # warm-up
            times, vals = [], []
            for _ in range(5):
                _sync(device)
                t = time.time()
                vals.append(A.score(model, source, prep, micro_batch=mb, device=device))
                _sync(device)
                times.append(time.time() - t)
            res[name] = {"mean_seconds_of_5": float(np.mean(times)), "all": times, "harm": vals[0], "repeats_identical": len(set(vals)) == 1}
        except torch.OutOfMemoryError as e:
            res[name] = {"out_of_memory": str(e)[:300]}
            torch.cuda.empty_cache()
    return res


def first_above(record: list[float], h: float) -> int | None:
    return next((k for k, v in enumerate(record) if v > h), None)


def first_relative_difference(a: list[float], b: list[float], tol: float = 0.01) -> int | None:
    return next((k for k, (x, y) in enumerate(zip(a, b)) if abs(x / y - 1) > tol), None)


def readings(runs_by_name: dict[str, list[float]], g1: list[float]) -> dict[str, Any]:
    """Plan 1, item 6, and plan 2's odd steps: harm at the budgets and at the steps before them; the first step above
    5 nats; the first step each run differs from G1's by more than 1 percent; and the first step the runs differ from each
    other by more than 1 percent."""
    allr = {"G1 (authors' loop, whole batch, B200)": g1, **runs_by_name}
    out: dict[str, Any] = {"harm": {}, "first_step_above_5_nats": {}, "first_step_differing_from_G1_by_1pct": {}, "pairs": {}}
    for name, rec in allr.items():
        out["harm"][name] = {str(k): rec[k] for k in sorted(BUDGETS + ODD)}
        out["first_step_above_5_nats"][name] = first_above(rec, 5.0)
        if not name.startswith("G1"):
            out["first_step_differing_from_G1_by_1pct"][name] = first_relative_difference(rec, g1)
    names = list(runs_by_name)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            out["pairs"][f"{a} vs {b}"] = first_relative_difference(runs_by_name[a], runs_by_name[b])
    return out
