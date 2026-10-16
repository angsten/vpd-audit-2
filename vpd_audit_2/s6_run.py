"""Plan 2 of the research log, Section 3: the GPU re-scoring of the run's saved settings, and its local side, with no cloud call.

What a container does (`heldout_job`, `attack_job`), for its batch, in units that a restart skips once finished:

  - Held-out batch H_j (16 containers): the token-level split of every carried setting (80 attack searches at five
    lengths, Part Z and Part P); exploited components and off or on for A_j's five searches at 40, 80, and 320 steps;
    one all-ones pass; (b1) and the sixteen (b2) settings; and on S4's batches the controls (a), (c), and (d).
  - Attack batches, two per container (8 containers): the split's own-batch version and (b1).

Every pass is scored through `adversary.score_per_text` on the run's prepared batch, as the run's scoring blocks were,
except the split's, whose setting differs by position: `score_sources` hands a source of shape texts by positions by
(C + 1) to the authors' path, which expands each source to the batch and takes the delta entry per position. Checks, each
a stop on failure:

  - the batch's labels are the run's: its fingerprint equals the table's (`prep_fp_H`, `prep_fp_A`);
  - the split's path, before any real pass: s at every position gives the saved carried (or own) harm, and s0 at every
    position the saved start harm, within the run's per-text tolerance (bit equality recorded beside);
  - exploited components: k = 0 gives the saved start harm and k = n the saved carried harm, bit for bit;
  - on H1 and H5, the starts with their delta entries reset to 1 give the delta-on arm's saved start harms bit for bit.

The settings are read from the run's search units on the volume, each checked against the hash the earlier backup
recorded; the starts against the signed file. Each unit file holds its passes' ids, batch harms, per-text harms, and
what each pass records beside its harm. Nothing is sealed.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import pilot as P
from vpd_audit_2 import s6_build as B

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s6_followups"
VOLUME = "/cache/s6_followups"
UNITS = "units"
RUN_UNITS = "/cache/s5_lead/lead/sealed/units"  # the run's search units on the volume
B2_FILE = "b2/b2_settings.npz"  # under VOLUME
LOCAL_UNITS = REPO_ROOT / ".cache" / "s6_followups" / "units"
LEAD_TABLE = REPO_ROOT / "results" / "s5_lead" / "lead" / "sealed"
LEAD_RECEIPT = REPO_ROOT / "results" / "s5_lead" / "lead" / "receipt.json"
DELTA_TABLE = REPO_ROOT / "results" / "s5_lead" / "delta_on" / "sealed"
DELTA_RECEIPT = REPO_ROOT / "results" / "s5_lead" / "delta_on" / "receipt.json"
RUN_BACKUP = REPO_ROOT / "results" / "s5_lead" / "backup.json"
B2_RECORD = RESULTS / "b2_settings.json"
ARM = "s6"
MODE = "s6"
RUN = "s6_followups"
ATTACK = tuple(f"A{i}" for i in range(1, 17))
HELDOUT = tuple(f"H{j}" for j in range(1, 17))
STARTS = LR.STARTS
ATTACK_PAIRS = tuple((ATTACK[2 * k], ATTACK[2 * k + 1]) for k in range(8))
DELTA_FREE_CHECK = ("H1", "H5")  # the delta-on arm saved its starts' harms on these S4 batches
CHECK_ROW = "n320"
COMMIT_EVERY = 10  # units between volume commits
CAP_DOLLARS = 45.0  # plan 2 of the research log, Section 5: over $45, do not launch
WAVES = {1: ("H1",), 2: tuple(h for h in HELDOUT if h != "H1") + tuple(f"{a}+{b}" for a, b in ATTACK_PAIRS)}
READING_FILES = ("vpd_audit_2/s6_build.py", "vpd_audit_2/s6_run.py", "vpd_audit_2/modal_s6.py", "vpd_audit_2/s6_split.py",
                 "vpd_audit_2/s6_exploited.py", "vpd_audit_2/s6_controls.py", "results/s6_followups/CONVENTIONS.md",
                 "results/s6_followups/b2_settings.json")
RUN_COMMIT = "8522c18156c6c9023aedffe9061a56838898e960"


class S6Failure(Exception):
    """A check failed; the message names it and the unit."""


# ----------------------------------------------------------------------------- scoring


def zero_masks(prep: A.Prepared) -> dict[str, Any]:
    """Per module, where the batch's label is exactly zero: [texts, positions, C] booleans."""
    return {k: (v == 0) for k, v in prep.labels.items()}


def label_stats(prep: A.Prepared) -> dict[str, float]:
    """Per position, the mean count of positive labels below 1e-3 and of labels exactly zero; and their totals."""
    small = zero = 0
    n_pos = None
    for v in prep.labels.values():
        small += int(((v > 0) & (v < 1e-3)).sum().item())
        zero += int((v == 0).sum().item())
        n_pos = int(v.shape[0] * v.shape[1])
    return {"positive_below_1e-3_per_position": small / n_pos, "zero_per_position": zero / n_pos, "positive_below_1e-3_total": small,
            "zero_total": zero, "positions": n_pos}


def split_sources(zero: dict[str, Any], a: np.ndarray, b: np.ndarray, delta_from: np.ndarray, lay: list[tuple[str, int]], device: str) -> dict[str, Any]:
    """Per-position sources: flat setting `a` where the label is zero and `b` elsewhere, each module's delta entry from
    `delta_from` at every position. Part Z is (s, s0, s); Part P is (s0, s, s0)."""
    import torch

    out, off = {}, 0
    for name, C in lay:
        z = zero[name]
        ta = torch.from_numpy(np.ascontiguousarray(a[off : off + C], dtype=np.float32)).to(device)
        tb = torch.from_numpy(np.ascontiguousarray(b[off : off + C], dtype=np.float32)).to(device)
        comps = torch.where(z, ta, tb)
        delta = torch.full((*z.shape[:-1], 1), float(delta_from[off + C]), dtype=torch.float32, device=device)
        out[name] = torch.cat([comps, delta], dim=-1)
        off += C + 1
    return out


def score_sources(model: Any, sources: dict[str, Any], prep: A.Prepared) -> tuple[float, np.ndarray]:
    """`adversary.score_per_text` for sources already shaped texts by positions by (C + 1)."""
    import torch

    loss = A.KLWithPerText()
    with torch.no_grad(), A.autocast_ctx(prep.precision):
        s, n = A._forward(model, prep.ids, sources, prep.labels, prep.target_out, prep.weight_deltas, reconstruction_loss=loss)
    return float(s.detach()) / n, loss.per_text.detach().cpu().numpy()


def score_flat(model: Any, flat: np.ndarray, prep: A.Prepared, lay: list[tuple[str, int]], device: str) -> tuple[float, np.ndarray]:
    return A.score_per_text(model, P.unflatten(np.asarray(flat, dtype=np.float32), lay), prep, device=device)


def score_split(model: Any, prep: A.Prepared, zero: dict[str, Any], part: str, s: np.ndarray, s0: np.ndarray, lay: list[tuple[str, int]],
                device: str) -> tuple[float, np.ndarray]:
    args = {"Z": (s, s0, s), "P": (s0, s, s0), "s_everywhere": (s, s, s), "s0_everywhere": (s0, s0, s0)}[part]
    return score_sources(model, split_sources(zero, *args, lay, device), prep)


def peak_reset(ctx: Any) -> None:
    if ctx.device == "cuda":
        import torch

        torch.cuda.reset_peak_memory_stats()


def peak_read(ctx: Any, kind: str) -> None:
    """The GPU memory peak while a unit of this kind was scored, allocated and reserved, in GiB; the largest over units."""
    if ctx.device == "cuda":
        import torch

        for name, value in (("allocated", torch.cuda.max_memory_allocated()), ("reserved", torch.cuda.max_memory_reserved())):
            key = f"peak_gib_{name}_{kind}"
            ctx.timings[key] = max(ctx.timings.get(key, 0.0), value / 2**30)


def within(x: float, ref: float) -> bool:
    return abs(x - ref) <= LT.PER_TEXT_RELATIVE_TOLERANCE * abs(ref)


def bits_equal(x: float, ref: float) -> bool:
    return np.float64(x).tobytes() == np.float64(ref).tobytes()


# ----------------------------------------------------------------------------- the container


@dataclass
class Context:
    commit: str
    units: Path
    lay: list[tuple[str, int]]
    device: str = "cuda"
    precision: str = "bf16"
    mode: str = MODE
    environment: dict[str, Any] = field(default_factory=dict)
    log: Callable[..., None] = field(default_factory=LR.Log)
    commit_volume: Callable[[], None] = lambda: None
    should_stop: Callable[[], bool] = lambda: False
    prepare: Callable[..., A.Prepared] = A.prepare
    t0: float = field(default_factory=time.time)
    timings: dict[str, float] = field(default_factory=dict)

    def tick(self, name: str, seconds: float, count: float = 1.0) -> None:
        self.timings[name] = self.timings.get(name, 0.0) + seconds
        self.timings[name + "_count"] = self.timings.get(name + "_count", 0.0) + count


def check_environment(ctx: Context) -> None:
    """The run's configuration, as the deciding containers asserted it; the tiny model's tests (mode "test") skip it."""
    if ctx.mode == "test":
        return
    env = ctx.environment
    ok = (ctx.mode == MODE and ctx.precision == "bf16" and ctx.device == "cuda" and "B200" in str(env.get("gpu")) and env.get("deterministic_algorithms") is True
          and env.get("deterministic_warn_only") is False and env.get("allow_tf32_matmul") is False and env.get("allow_tf32_cudnn") is False
          and env.get("cublas_workspace_config") == ":4096:8" and env.get("vpd_audit_2_commit") == ctx.commit and env.get("vpd_audit_2_dirty") == "0")
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{ARM}")


def unit_path(ctx: Context, name: str) -> Path:
    return ctx.units / f"{name}.npz"


def clean_unfinished(ctx: Context, names: list[str]) -> int:
    removed = 0
    for name in names:
        p = unit_path(ctx, name)
        tmp = p.with_name(p.name + ".tmp")
        if tmp.is_file():
            tmp.unlink()
            removed += 1
        if p.is_file() and not LR.finished(p):
            p.unlink()
            removed += 1
        if LR.marker(p).is_file() and not p.is_file():
            LR.marker(p).unlink()
            removed += 1
    return removed


def write_scored(ctx: Context, name: str, kind: str, params: dict[str, Any], prep_fp: str, scored: list[tuple[str, float, np.ndarray, dict[str, Any]]],
                 extra: dict[str, Any] | None = None) -> str:
    meta = {"unit": name, "kind": kind, "params": params, "prep_fp": prep_fp, "commit": ctx.commit, **(extra or {})}
    arrays = {"pass_ids": np.array([p for p, _, _, _ in scored]), "harm": np.array([h for _, h, _, _ in scored], dtype=np.float64),
              "per_text": np.stack([np.asarray(t, dtype=np.float32) for _, _, t, _ in scored]),
              "recorded": np.array(json.dumps([r for _, _, _, r in scored], sort_keys=True)), "meta": np.array(json.dumps(meta, sort_keys=True))}
    return LR.write_unit(unit_path(ctx, name), arrays)


def json_field(z: Any, key: str) -> Any:
    """A JSON string stored in an npz: `deterministic_npz` writes a 0-d array as shape (1,), so take its one element."""
    return json.loads(str(np.asarray(z[key]).reshape(-1)[0]))


def unit_meta(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as z:
        return json_field(z, "meta")


def run_unit_from_bytes(data: bytes, attack: str, start: int) -> dict[str, np.ndarray]:
    """A run search unit's saved settings and gradients, after checking it is the lead search of that batch and start."""
    import io

    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        out = {k: z[k] for k in ("hook_names", "settings", "cum_signed")}
        meta = json_field(z, "meta")
    if (meta["batch"], meta["start"], meta["arm"], meta["delta_held"]) != (attack, start, "lead", False):
        raise S6Failure(f"the unit read for {attack} from start {start} is not that lead search")
    return out


@dataclass
class Inputs:
    """What a container is handed beside its batches' token ids."""

    starts: dict[int, np.ndarray]  # flat starts, float32
    strata: dict[str, np.ndarray]
    read_run_unit: Callable[[str, int], dict[str, np.ndarray]]  # (attack batch, start) to the run's search unit, checked
    b2: dict[str, np.ndarray] | None = None  # name to flat setting, checked


def _run_unit_cache(inputs: Inputs) -> Callable[[str, int], dict[str, np.ndarray]]:
    cache: dict[tuple[str, int], dict[str, np.ndarray]] = {}

    def get(attack: str, start: int) -> dict[str, np.ndarray]:
        key = (attack, start)
        if key not in cache:
            cache.clear()  # one search's unit at a time
            cache[key] = inputs.read_run_unit(attack, start)
        return cache[key]

    return get


def prepare_batch(model: Any, ctx: Context, batch: str, ids: np.ndarray, rows: list[str], expected_fp: str) -> tuple[A.Prepared, str, dict[str, Any]]:
    if LR.sha_rows(ids) != list(rows):
        raise LR.GuardFailure("G1", f"container|{ARM}|{batch}")
    t0 = time.time()
    prep = ctx.prepare(model, ids, ctx.precision, device=ctx.device)
    ctx.tick("labels_and_targets", time.time() - t0)
    t0 = time.time()
    fp = LR.prep_fingerprint(prep)
    ctx.tick("fingerprint", time.time() - t0)
    if fp != expected_fp:
        raise LR.GuardFailure("prep_fp_is_the_runs", f"container|{ARM}|{batch}")
    return prep, fp, zero_masks(prep)


def run_units(model: Any, ctx: Context, batch: str, units: list[tuple[str, str, dict[str, Any]]], prep: A.Prepared, prep_fp: str, zero: dict[str, Any],
              inputs: Inputs, refs: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    """Score every unit not already finished, in order; check as the module's docstring says; commit every few units."""
    lay = ctx.lay
    get = _run_unit_cache(inputs)
    cells = B.cells_of(lay, inputs.strata)
    alive, never = B.component_mask(lay, inputs.strata, "alive"), B.component_mask(lay, inputs.strata, "never")
    coarse = {kind: B.coarse_strata(inputs.strata, kind) for kind in B.COARSE_KINDS}
    out: list[dict[str, Any]] = []
    written = 0
    stopped = False
    for name, kind, params in units:
        path = unit_path(ctx, name)
        if LR.finished(path):
            m = unit_meta(path)
            if m["commit"] != ctx.commit or m["prep_fp"] != prep_fp:
                raise S6Failure(f"{name}: a finished unit from another commit or other labels")
            out.append({"unit": name, "sha256": LR.marker(path).read_text(), "guards": {"skipped_after_restart": True}, "skipped": True})
            continue
        if ctx.should_stop():
            stopped = True
            break
        t0 = time.time()
        peak_reset(ctx)
        scored: list[tuple[str, float, np.ndarray, dict[str, Any]]] = []
        guards: dict[str, bool] = {}
        extra: dict[str, Any] = {}

        def flat_pass(pid: str, flat: np.ndarray, rec: dict[str, Any]) -> float:
            h, t = score_flat(model, flat, prep, lay, ctx.device)
            scored.append((pid, h, t, {**rec, "setting_sha": B.sha(flat)}))
            return h

        if kind == "check":
            first = sorted(inputs.starts)[0]  # the check cell: the first start, at 320 steps
            s, _ = B.saved(get(refs["check_attack"], first), CHECK_ROW)
            s0 = inputs.starts[first]
            for part, ref_key in (("s_everywhere", "check_carried"), ("s0_everywhere", "check_start")):
                h, t = score_split(model, prep, zero, part, s, s0, lay, ctx.device)
                scored.append((f"check|{part}", h, t, {"reference": refs[ref_key], "bits_equal": bits_equal(h, refs[ref_key])}))
                guards[f"split_path_{part}"] = within(h, refs[ref_key])
                if not guards[f"split_path_{part}"]:
                    raise S6Failure(f"{name}: the split's path with {part} does not give the saved harm")
            extra["label_stats"] = label_stats(prep)
        elif kind == "split":
            unit = get(params["attack"], params["start"])
            s0 = inputs.starts[params["start"]]
            for row in B.SPLIT_ROWS:
                s, _ = B.saved(unit, row)
                for part in ("Z", "P"):
                    h, t = score_split(model, prep, zero, part, s, s0, lay, ctx.device)
                    scored.append((f"{part}|{row}", h, t, {"setting_sha": B.sha(s)}))
        elif kind == "exploit":
            a, st, row = params["attack"], params["start"], params["row"]
            s, G = B.saved(get(a, st), row)
            for pid, flat, rec in B.exploit_passes(s, inputs.starts[st], G, cells, a, st, row):
                h = flat_pass(pid, flat, rec)
                if pid == "top|0":
                    guards["k0_is_the_saved_start"] = bits_equal(h, refs["start"][str(st)])
                elif pid == f"top|{s.size}":
                    guards["kn_is_the_saved_carried"] = bits_equal(h, refs["exploit_carried"][f"{st}|{row}"])
            if not all(guards.values()):
                raise S6Failure(f"{name}: the builder's endpoints do not reproduce the saved harms bit for bit")
        elif kind == "ones":
            flat_pass("ones", np.ones(sum(c + 1 for _, c in lay), dtype=np.float32), {})
        elif kind in ("b", "b1"):
            flat_pass("b1", np.zeros(sum(c + 1 for _, c in lay), dtype=np.float32), {})
            if kind == "b":
                for key in sorted(inputs.b2):
                    flat_pass(f"b2|{key}", inputs.b2[key], {})
        elif kind == "controls":
            unit = get(params["attack"], params["start"])
            s_by_row = {row: B.saved(unit, row)[0] for row in B.SPLIT_ROWS}
            for pid, flat, rec in B.control_passes(s_by_row, inputs.starts[params["start"]], lay, coarse, alive, never, params["attack"], params["start"]):
                flat_pass(pid, flat, rec)
        elif kind == "variants_check":
            # plan 3 of the research log, Section 7: plan 2 of the research log's check of the split's path (the full setting and the start, within the run's
            # per-text tolerance, its bit equality recorded), and the flat path's: the full setting, bit for bit
            first = sorted(inputs.starts)[0]
            s, _ = B.saved(get(refs["check_attack"], first), CHECK_ROW)
            s0 = inputs.starts[first]
            for part, ref_key in (("s_everywhere", "check_carried"), ("s0_everywhere", "check_start")):
                h, t = score_split(model, prep, zero, part, s, s0, lay, ctx.device)
                scored.append((f"check|{part}", h, t, {"reference": refs[ref_key], "bits_equal": bits_equal(h, refs[ref_key])}))
                guards[f"split_path_{part}"] = within(h, refs[ref_key])
            h = flat_pass("check|flat", s, {"reference": refs["check_carried"]})
            guards["flat_path_bits_equal"] = bits_equal(h, refs["check_carried"])
            if not all(guards.values()):
                raise S6Failure(f"{name}: a path does not give the saved harm")
        elif kind == "variants":
            unit = get(params["attack"], params["start"])
            for row in B.SPLIT_ROWS:
                s, _ = B.saved(unit, row)
                flat_pass(f"V1|{row}", B.zeros_alone(s), {})
                for v, args in B.variant_split_args(s).items():
                    h, t = score_sources(model, split_sources(zero, *args, lay, ctx.device), prep)
                    scored.append((f"{v}|{row}", h, t, {"setting_sha": B.sha(s)}))
        elif kind == "dose":
            # plan 3 of the research log, Section 8: the dose-response on an intact model
            unit = get(params["attack"], params["start"])
            for row in B.SPLIT_ROWS:
                s, _ = B.saved(unit, row)
                for pid, flat, rec in B.dose_passes(s, params["attack"], params["start"], row):
                    flat_pass(pid, flat, rec)
        elif kind == "dose_rounded":
            # plan 3 of the research log, Section 9: the dose-response on the rounded off set
            unit = get(params["attack"], params["start"])
            for row in B.SPLIT_ROWS:
                s, _ = B.saved(unit, row)
                for pid, flat, rec in B.dose_rounded_passes(s, params["attack"], params["start"], row):
                    flat_pass(pid, flat, rec)
        elif kind == "control_starts":
            for pid, flat, rec in B.control_start_passes(inputs.starts, lay):
                h = flat_pass(pid, flat, rec)
                if pid.startswith("a_start|") and refs.get("delta_on_start") is not None:
                    st = pid.split("|")[1]
                    guards[f"reset_start_{st}_is_the_delta_on_arms"] = bits_equal(h, refs["delta_on_start"][st])
            if not all(guards.values()):
                raise S6Failure(f"{name}: a reset start does not reproduce the delta-on arm's saved start harm bit for bit")
        else:
            raise ValueError(kind)
        peak_read(ctx, kind)
        sha = write_scored(ctx, name, kind, params, prep_fp, scored, extra)
        ctx.tick(f"unit_{kind}", time.time() - t0, len(scored))
        ctx.log(event="unit_finished", unit=name, sha256=sha)
        out.append({"unit": name, "sha256": sha, "guards": guards or {"written": True}, "skipped": False})
        written += 1
        if written % COMMIT_EVERY == 0:
            t0 = time.time()
            ctx.commit_volume()
            ctx.tick("volume_commit", time.time() - t0)
    return out, stopped


def job(model: Any, ctx: Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]], inputs: Inputs) -> dict[str, Any]:
    """A container: its one held-out batch, or its two attack batches, one after the other."""
    import gc

    check_environment(ctx)
    if ctx.device == "cuda":
        import torch

        ctx.timings["device_gib"] = torch.cuda.get_device_properties(0).total_memory / 2**30
    refs_all = spec["refs"]
    units_out: list[dict[str, Any]] = []
    expected = 0
    stopped = False
    stats = {}
    for batch in spec["batches"]:
        refs = refs_all[batch]
        units = (B.heldout_units(batch, list(spec["attack_batches"]), list(spec["starts"]), refs["own_attack"]) if spec["side"] == "heldout"
                 else B.attack_units(batch, list(spec["starts"])))
        expected += len(units)
        removed = clean_unfinished(ctx, [u[0] for u in units])
        ids, rows = batch_inputs[batch]
        prep, fp, zero = prepare_batch(model, ctx, batch, ids, rows, refs["prep_fp"])
        ctx.tick("to_ready", time.time() - ctx.t0)
        ctx.log(event="container_started", container=f"{ARM}|{batch}", count=removed)
        done, stopped = run_units(model, ctx, batch, units, prep, fp, zero, inputs, refs)
        units_out += done
        stats[batch] = removed
        del prep, zero
        gc.collect()
        if ctx.device == "cuda":
            import torch

            torch.cuda.empty_cache()
        if stopped:
            break
    ctx.commit_volume()
    out = {"container": f"{ARM}|{spec['side']}|{spec['batch']}", "units": units_out, "finished_units": len(units_out), "expected_units": expected,
           "stopped": bool(stopped), "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment),
           "timings": {k: float(v) for k, v in ctx.timings.items()}, "removed_unfinished": stats}
    ctx.log(event="container_finished", container=out["container"], count=len(units_out), seconds=out["seconds"])
    return out


# ----------------------------------------------------------------------------- the local side: what each container is handed


def specs(commit: str, refs: dict[str, Any], wave: int | None = None) -> list[dict[str, Any]]:
    """One spec per container: the 16 held-out batches, then the 8 pairs of attack batches; `wave` narrows to a wave."""
    out = []
    for h in HELDOUT:
        out.append({"arm": ARM, "side": "heldout", "batch": h, "batches": [h], "commit": commit, "mode": MODE, "root": VOLUME, "units": UNITS,
                    "run": RUN, "attack_batches": list(ATTACK), "starts": list(STARTS), "refs": {h: refs[h]}})
    for a, b in ATTACK_PAIRS:
        out.append({"arm": ARM, "side": "attack", "batch": f"{a}+{b}", "batches": [a, b], "commit": commit, "mode": MODE, "root": VOLUME, "units": UNITS,
                    "run": RUN, "attack_batches": list(ATTACK), "starts": list(STARTS), "refs": {a: refs[a], b: refs[b]}})
    return [s for s in out if wave is None or s["batch"] in WAVES[wave]]


SPEC_KEYS = {"arm", "side", "batch", "batches", "commit", "mode", "root", "units", "run", "attack_batches", "starts", "refs"}


def check_spec(spec: dict[str, Any]) -> None:
    ok = (set(spec) - {"launch"} == SPEC_KEYS and spec["arm"] == ARM and spec["mode"] == MODE and spec["root"] == VOLUME and spec["units"] == UNITS
          and spec["run"] == RUN and len(str(spec["commit"])) == 40 and tuple(spec["starts"]) == STARTS and tuple(spec["attack_batches"]) == ATTACK
          and ((spec["side"] == "heldout" and spec["batches"] == [spec["batch"]] and spec["batch"] in HELDOUT)
               or (spec["side"] == "attack" and tuple(spec["batches"]) in ATTACK_PAIRS and spec["batch"] == "+".join(spec["batches"]))))
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('arm')}|{spec.get('batch')}")


def load_table_checked(folder: Path, receipt: Path) -> dict[str, Any]:
    rec = json.load(open(receipt))
    for f in rec["files"]:
        if LT.sha256_file(Path(folder) / f["name"]) != f["sha256"]:
            raise LL.LaunchRefusal(f"{f['name']} is not the file the receipt records")
    return LT.load_table(Path(folder))


def references(lead: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    """Per batch, the saved values its checks compare with, from the run's tables."""
    names = [str(x) for x in lead["setting_names"]]
    att = [str(x) for x in lead["attack_names"]]
    held = [str(x) for x in lead["heldout_names"]]
    dheld = [str(x) for x in delta["heldout_names"]]
    starts = [int(x) for x in lead["starts"]]
    q = {row: names.index(row) for row in B.SPLIT_ROWS}
    out: dict[str, Any] = {}
    for j, h in enumerate(held):
        a = att[j]  # A_j on H_j
        out[h] = {"prep_fp": str(lead["prep_fp_H"][j]), "own_attack": a, "check_attack": a,
                  "check_carried": float(lead["carried"][j, j, 0, q[CHECK_ROW]]), "check_start": float(lead["init_H"][j, 0]),
                  "start": {str(s): float(lead["init_H"][j, k]) for k, s in enumerate(starts)},
                  "exploit_carried": {f"{s}|{row}": float(lead["carried"][j, j, k, q[row]]) for k, s in enumerate(starts) for row in B.EXPLOIT_ROWS},
                  "delta_on_start": ({str(s): float(delta["init_H"][dheld.index(h), k]) for k, s in enumerate(starts)} if h in DELTA_FREE_CHECK else None)}
    for i, a in enumerate(att):
        out[a] = {"prep_fp": str(lead["prep_fp_A"][i]), "own_attack": a, "check_attack": a,
                  "check_carried": float(lead["own_A"][i, 0, q[CHECK_ROW]]), "check_start": float(lead["init_A"][i, 0]),
                  "start": {str(s): float(lead["init_A"][i, k]) for k, s in enumerate(starts)}, "exploit_carried": {}, "delta_on_start": None}
    return out


def container_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                     pools: dict[str, Any] | None = None) -> dict[str, tuple[np.ndarray, list[str]]]:
    """The token ids of the container's batches, each a pool of its side; no other batch's ids."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = LL._manifest()["pools"] if pools is None else pools
    want = {"heldout": "H", "attack": "A"}[spec["side"]]
    out = {}
    for b in spec["batches"]:
        if pools[b]["pool"] != want:
            raise LL.LaunchRefusal(f"batch {b} is not a pool of the {spec['side']} side")
        ids, _texts, rows = load_ids(b)
        out[b] = (ids, list(rows))
    return out


def flat_starts() -> dict[int, np.ndarray]:
    lay = P.layout()
    return {s: LR.flat_start(st, lay, False) for s, st in LL.starts_for(STARTS).items()}


def run_unit_hashes() -> dict[str, str]:
    """Each run search unit's SHA-256 as the earlier backup recorded it, by file name."""
    return {k.split("/", 1)[1]: v for k, v in json.load(open(RUN_BACKUP))["files"].items() if k.startswith("lead/")}


# ----------------------------------------------------------------------------- the local side: the launch and the cost


def tree_holds_only_this_plans_records() -> bool:
    top = Path(LL._git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    allowed = (RESULTS.resolve().relative_to(top)).as_posix() + "/"
    r = LL._git("status", "--porcelain", "--untracked-files=all", "--", ".")
    return r.returncode == 0 and all(line.startswith("?? ") and line[3:].strip('"').startswith(allowed) for line in r.stdout.splitlines())


def check_launch_commit(commit: str) -> None:
    if not tree_holds_only_this_plans_records():
        raise LL.LaunchRefusal("the tree is not clean under vpd-audit-2")
    if LL.head_commit() != commit or len(commit) != 40:
        raise LL.LaunchRefusal("the current commit is not the one named")
    missing = [rel for rel in READING_FILES if LL.blob(commit, rel) is None]
    if missing:
        raise LL.LaunchRefusal("not committed: " + ", ".join(missing))
    changed = LL.run_files_changed(RUN_COMMIT, commit)
    if changed:
        raise LL.LaunchRefusal("the scoring path has changed since the lead run: " + ", ".join(changed))


def passes_of(spec: dict[str, Any]) -> dict[str, int]:
    """The passes a container scores: those of the split (per position) and the rest."""
    split = flat = 0
    for batch in spec["batches"]:
        units = (B.heldout_units(batch, list(ATTACK), list(STARTS), "A1") if spec["side"] == "heldout" else B.attack_units(batch, list(STARTS)))
        for _, kind, params in units:
            n = B.n_passes(kind, params.get("row"))
            if kind in ("check", "split"):
                split += n
            else:
                flat += n
    return {"split": split, "flat": flat}


def projection(listed_hourly_price: float, *, split_factor: float = 2.0, wave: int | None = None, ledger_path: Path | None = None,
               rehearsal_path: Path | None = None) -> dict[str, Any]:
    """The cost before launch (plan 2 of the research log, Section 5), from the run's per-pass timing: the held-out containers of the lead's
    second wave (first lives only), each 5 searches and 80 scoring blocks of 74 passes (5,920), less the time to ready
    and the 5 searches at the attack containers' measured rate (each with its own 11 re-scores), over the blocks' passes. A split pass, whose source is built per position, is taken at
    `split_factor` times a flat one, since nothing has measured it. Per container: the time to ready, once per batch,
    and a volume commit every ten units; per life 50 seconds of boot."""
    ledger = json.load(open(LL.RESULTS / "ledger.json" if ledger_path is None else ledger_path))
    t = json.load(open(LL.RESULTS / "rehearsal_2" / "rehearsal.json" if rehearsal_path is None else rehearsal_path))["timings"]
    ready, commit_s = float(t["seconds_to_ready"]), float(t["seconds_per_commit_after_search"])

    def returned(stage: str) -> list[float]:
        return [float(c["returned_seconds"]) for x in ledger["stages"][stage]["launches"] for c in x["calls"].values()
                if c["outcome"] == "returned" and c["attempts"] == 1]

    per_search = (float(np.mean(returned("lead_attack"))) - ready) / 5
    held = returned("lead_heldout_2")
    passes_per_heldout = 80 * (10 + 8 * 8)  # each block: 10 carried settings and the shuffled copies of 8
    per_pass = (float(np.mean(held)) - ready - 5 * per_search) / passes_per_heldout
    containers = specs("0" * 40, {b: {} for b in HELDOUT + ATTACK}, wave)
    total = 0.0
    rows = []
    for spec in containers:
        p = passes_of(spec)
        n_units = sum(len(B.heldout_units(b, list(ATTACK), list(STARTS), "A1") if spec["side"] == "heldout" else B.attack_units(b, list(STARTS)))
                      for b in spec["batches"])
        sec = len(spec["batches"]) * ready + per_pass * (p["flat"] + split_factor * p["split"]) + commit_s * (n_units / COMMIT_EVERY + 1)
        rows.append({"batch": spec["batch"], **p, "units": n_units, "seconds": sec})
        total += sec
    money = LG.money(total, len(containers), listed_hourly_price)
    return {"check": "C0", "per_pass_seconds": per_pass, "per_search_seconds": per_search, "seconds_to_ready": ready, "split_factor": split_factor,
            "containers": rows, "function_seconds": total, "passes": sum(r["flat"] + r["split"] for r in rows), **{"money": money},
            "projected_dollars": money["dollars"], "cap": CAP_DOLLARS, "exceeds_cap": money["dollars"] > CAP_DOLLARS}


STAGES = {w: LG.Stage(f"s6_wave{w}", ARM, "both", len(WAVES[w]), 0, 0, 0, 0, 0, False) for w in WAVES}


def launch_command(commit: str, wave: int, cloud: LL.Cloud, *, listed_hourly_price: float) -> dict[str, Any]:
    """One wave: the checks, the projection of every wave still to run recorded as check C0 before the first (over $45,
    nothing launches), then the wave's containers at once. Wave 2 waits for wave 1 to be complete."""
    check_launch_commit(commit)
    ledger_path = RESULTS / "ledger.json"
    ledger = LL.read_ledger(ledger_path)
    if wave == 2 and not ledger["stages"].get(STAGES[1].name, {}).get("complete"):
        raise LL.LaunchRefusal("wave 1 is not complete")
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("plan 2 of the research log's run began at another commit")
    if earlier is None:
        LL.record_c0(ledger_path, projection(listed_hourly_price))
    lead = load_table_checked(LEAD_TABLE, LEAD_RECEIPT)
    delta = load_table_checked(DELTA_TABLE, DELTA_RECEIPT)
    refs = references(lead, delta)
    return LL.drive_stage(STAGES[wave], specs(commit, refs, wave), cloud, ledger_path=ledger_path, runs_path=RESULTS / f"runs_{STAGES[wave].name}.json",
                          design=(STAGES[wave],), timings={}, listed_hourly_price=listed_hourly_price, cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


# ----------------------------------------------------------------------------- after the run: the copy


def collect_command(commit: str, *, read_file: Callable[[str], bytes], log: Callable[..., None], dest: Path | None = None) -> dict[str, str]:
    """Every unit file off the volume as bytes, each checked against the hash its container returned, to a folder git
    ignores, with the receipt."""
    if not tree_holds_only_this_plans_records() or LL.head_commit() != commit:
        raise LL.LaunchRefusal("the tree or the commit is not the run's")
    dest = LOCAL_UNITS if dest is None else dest
    returned: dict[str, str] = {}
    for w in WAVES:
        run = json.load(open(RESULTS / f"runs_{STAGES[w].name}.json"))
        if run["commit"] != commit or not run["summary"]["complete"]:
            raise LL.LaunchRefusal(f"wave {w} is not complete at this commit")
        returned.update({u["unit"]: u["sha256"] for c in run["containers"] for u in c["units"]})
    expected = {u[0] for h in HELDOUT for u in B.heldout_units(h, list(ATTACK), list(STARTS), "A1")}
    expected |= {u[0] for a in ATTACK for u in B.attack_units(a, list(STARTS))}
    if set(returned) != expected:
        raise LL.LaunchRefusal(f"the stages' records hold {len(returned)} units; the plan has {len(expected)}")
    dest.mkdir(parents=True, exist_ok=True)
    for name in sorted(returned):
        data = read_file(f"{VOLUME}/{UNITS}/{name}.npz")
        if hashlib.sha256(data).hexdigest() != returned[name]:
            raise LL.LaunchRefusal(f"the bytes of {name} do not have the hash its container returned")
        (dest / f"{name}.npz").write_bytes(data)
    LL.write_json(RESULTS / "units_receipt.json", {"commit": commit, "at": LL.utc_now(), "folder": str(dest.relative_to(REPO_ROOT)) if dest.is_relative_to(REPO_ROOT)
                                                    else str(dest), "files": {f"{k}.npz": v for k, v in sorted(returned.items())}})
    log(event="backup_finished", container="units", count=len(returned))
    return returned
