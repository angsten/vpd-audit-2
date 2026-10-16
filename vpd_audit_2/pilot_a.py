"""Plan 6 of the research log, Part A: question 2's nuisance scales on C1 to C8 (plan 6 of the research log, Section 5).

One container per batch C_j, at the lead's configuration (our loop, `micro_batch=None`, bf16 autocast, one B200, step 0.1,
320 steps; labels, target, and weight deltas once per batch under bf16 autocast; strict deterministic algorithms):

  1. A1's diagonal cell first (start j), with every step's sources recorded: its harm record and final sources must
     equal G1's `A_c|C_j|320` bit for bit, or the container stops (Section 9).
  2. A1's other seven starts.
  3. A2: two perturbed starts, key ("pilot-perturb", C_j, j, r), r = 1, 2, each checked to depart from the diagonal run
     (`diagnose.departure`, which ignores the perturbed entry). A replicate that never departs is redrawn with r + 2, at
     most twice, every draw recorded.
  4. A3 (on the start-1 run): the sources the hook saved at 20, 40, 80, 160, and 320 steps and at stages 2, 5, and 10
     nats, each scored unshuffled (a check against the record) and in 8 frequency-stratified shuffles, keyed
     ("pilot-shuffle", C_j, 1, tag, r). The shuffles' harms are sealed: the job writes them to `sealed_path` itself and
     returns only that file's path and SHA-256 (plan 7 of the research log, item 5), so no caller holds them to print by accident.

Every run's harm after every step, the hook's events, seconds per step, the start's key, the GPU, and the determinism mode
are returned; the hook's sources are written to the volume, their SHA-256 returned.
"""

from __future__ import annotations

import hashlib
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A
from vpd_audit_2 import diagnose as D
from vpd_audit_2 import pilot as P

N_STEPS = 320
STEP = 0.1
SHUFFLES = 8
TAGS = {"n20": "step_20", "n40": "step_40", "n80": "step_80", "n160": "step_160", "n320": "step_320",
        "h2": "two_step_mean_reaches_2", "h5": "two_step_mean_reaches_5", "h10": "two_step_mean_reaches_10"}


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def _run(model: Any, prep: A.Prepared, start: dict[str, np.ndarray], record_sources: bool, device: str = "cuda") -> tuple[dict[str, Any], A.SaveHook, int]:
    hook = A.SaveHook(steps=P.BUDGETS, thresholds=P.STAGES)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        r = A.run(model, prep, start, N_STEPS, STEP, record_sources=record_sources, save_hook=hook, device=device)
    n_det = sum("deterministic" in str(w.message) for w in caught)
    return r, hook, n_det


def _summary(r: dict[str, Any], hook: A.SaveHook, n_det: int, batch: str, start_key: list, out_path: Path) -> dict[str, Any]:
    np.savez(out_path, **{k: v for k, v in hook.saved.items()}, final=np.concatenate([v.reshape(-1) for v in r["sources"].values()]))
    return {"batch": batch, "start_key": start_key, "record": r["record"], "seconds": r["seconds"], "seconds_per_step": r["seconds"] / N_STEPS,
            "hook_events": hook.events, "stage_crossings": {f"{h:g}": P.crossing(r["record"], h) for h in P.STAGES_A4},
            "final_sources_sha256": D.sources_sha256(r["sources"]), "saved_sources_file": str(out_path),
            "saved_sources_sha256": {k: _sha(v) for k, v in hook.saved.items()}, "determinism_warnings_caught": n_det}


def write_sealed(path: Path, arrays: dict[str, np.ndarray]) -> dict[str, str]:
    """Write sealed arrays to their file and return only the file's path and SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **arrays)
    return {"file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def batch_job(model: Any, batch: str, ids: np.ndarray, j: int, starts: dict[int, dict[str, np.ndarray]], g1: dict[str, Any],
              strata: dict[str, np.ndarray], lay: list[tuple[str, int]], out_dir: Path, sealed_path: Path, log: Any = print,
              device: str = "cuda") -> dict[str, Any]:
    import torch

    assert batch in P.PILOT_BATCHES and batch == f"C{j}" and set(starts) == set(P.PILOT_STARTS), (batch, j, sorted(starts))
    t0 = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    prep = A.prepare(model, ids, "bf16", device=device)
    out: dict[str, Any] = {"batch": batch, "labels_target_seconds": time.time() - t0, "a1": {}, "a2": {}, "assertions": []}

    def note(kind: str, start: int, key: list) -> None:
        out["assertions"].append({"run": kind, "batch": batch, "start": start, "key": key, "batch_in_C1_to_C8": batch in P.PILOT_BATCHES,
                                  "start_in_1_to_8": start in P.PILOT_STARTS})

    # 1. the diagonal cell, against G1
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    diag, hook, n_det = _run(model, prep, starts[j], record_sources=True, device=device)
    note("A1 diagonal", j, [20261001, "start", j])
    s = _summary(diag, hook, n_det, batch, [20261001, "start", j], out_dir / f"{batch}_s{j}.npz")
    s["equals_G1_record"] = diag["record"] == g1["record"]
    s["equals_G1_final_sources"] = s["final_sources_sha256"] == g1["sources_sha256"]
    s["peak_memory_gib"] = torch.cuda.max_memory_allocated() / 2**30 if device == "cuda" else None
    out["a1"][str(j)] = s
    saved_by_start = {j: hook.saved}
    log(f"[pilot-a] {batch} s{j} (diagonal): equals G1 {s['equals_G1_record'] and s['equals_G1_final_sources']}; {s['seconds_per_step']:.3f} s per step")
    if not (s["equals_G1_record"] and s["equals_G1_final_sources"]):
        out["stopped"] = "the diagonal cell does not equal G1's run bit for bit (Section 9): stop"
        return out

    # 2. the other seven starts
    for st in P.PILOT_STARTS:
        if st == j:
            continue
        r, hook, n_det = _run(model, prep, starts[st], record_sources=False, device=device)
        note("A1", st, [20261001, "start", st])
        out["a1"][str(st)] = _summary(r, hook, n_det, batch, [20261001, "start", st], out_dir / f"{batch}_s{st}.npz")
        log(f"[pilot-a] {batch} s{st}: {out['a1'][str(st)]['seconds_per_step']:.3f} s per step")
        if st == 1:
            saved_by_start[1] = hook.saved
        del r
    start1_hook_saved = saved_by_start[1]

    # 3. A2: the arithmetic replicates
    for r0 in (1, 2):
        draws = []
        for rr in (r0, r0 + 2, r0 + 4):
            pstart, info = D.perturbed_start(starts[j], ("pilot-perturb", batch, j, rr))
            pr, hook, n_det = _run(model, prep, pstart, record_sources=True, device=device)
            note("A2", j, [20261001, "pilot-perturb", batch, j, rr])
            dep = D.departure(pr, diag, perturbed_entry=info["entry"])
            first_1pct = next((k for k, (x, y) in enumerate(zip(pr["record"], diag["record"])) if abs(x / y - 1) > 0.01), None)
            summ = _summary(pr, hook, n_det, batch, [20261001, "pilot-perturb", batch, j, rr], out_dir / f"{batch}_s{j}_perturb{rr}.npz")
            summ.update({"perturbation": info, "departure": dep, "first_step_harm_differs_by_1pct": first_1pct})
            draws.append(summ)
            log(f"[pilot-a] {batch} s{j} perturb r={rr}: departs {dep['departs']} at {dep['first_other_source_difference']}; "
                f"1 percent at {first_1pct}")
            del pr
            if dep["first_other_source_difference"] is not None:
                break
        out["a2"][str(r0)] = {"accepted": draws[-1] if draws[-1]["departure"]["first_other_source_difference"] is not None else None,
                              "draws": draws, "redraws": len(draws) - 1}
    del diag

    # 4. A3: shuffles of the start-1 run's saved sources, scored on this batch only
    a3: dict[str, Any] = {}
    sealed: dict[str, np.ndarray] = {}
    rec1 = out["a1"]["1"]["record"]
    for tag, name in TAGS.items():
        if name not in start1_hook_saved:
            a3[tag] = {"missing": True}
            continue
        flat = start1_hook_saved[name]
        own = P.score_own(model, P.unflatten(flat, lay), prep, batch, batch, device=device)
        k = out["a1"]["1"]["hook_events"][name]
        harms = np.array([P.score_own(model, P.unflatten(P.shuffle_source(flat, lay, strata, (batch, 1, tag, r)), lay), prep, batch, batch, device=device)
                          for r in range(1, SHUFFLES + 1)])
        sealed[f"{batch}|{tag}|own"] = np.array([own])
        sealed[f"{batch}|{tag}|shuffles"] = harms
        a3[tag] = {"missing": False, "step": k, "own_score_equals_record": own == rec1[k], "n_shuffles": SHUFFLES,
                   "shuffle_keys": [[20261001, "pilot-shuffle", batch, 1, tag, r] for r in range(1, SHUFFLES + 1)]}
    log(f"[pilot-a] {batch}: A3 scored {sum(1 for v in a3.values() if not v['missing'])} source types x {SHUFFLES} shuffles (sealed)")
    out["a3"] = a3
    out["a3_sealed"] = write_sealed(sealed_path, sealed)
    del sealed
    out["seconds"] = time.time() - t0
    return out
