"""Session 5, plan 2: the lead run's units, guards, and assembler.

The binding specification is `freeze/amendment1_specs/table_and_run_spec.md` ("Lena's specification") with its erratum,
as plan 2 (`sessions/005/engineering/plan_2.md`) corrects it; Amendment 1's Section 6 adds the run requirements.

One container handles one batch of one arm. A container for a held-out batch never receives the token ids of any
attack batch, and the reverse: it reads the attack searches' saved settings from the volume, never their text.

  - A search unit (`search_unit`) is one search with its own-batch re-scores through the per-text scoring path.
  - A scoring block (`scoring_block`) is one attack search's scored settings, and the 8 shuffled copies of those that
    have them, scored on the container's held-out batch.
  - `attack_job` and `heldout_job` are what a container runs. A restart skips finished units.
  - `assemble` builds an arm's table from the unit files, in plan 1's format (`lead_table`), and writes it.

Sealing (plan 2, Section 5.2). Every file a unit writes is sealed: records, settings, steps, hashes, gradients,
re-scores, and harms. A job returns, per unit, its identifier, one SHA-256 of its file, and guard outcomes as true or
false; and per container its seconds. Nothing here prints: every message goes through `Log`, which accepts those
fields and no others. A failed guard raises `GuardFailure`, whose message names the guard and the unit and carries no
value.

Arms: "lead" (delta components searched) and "delta_on" (the 24 delta entries held at 1; five scored settings). The
rehearsal on a calibration batch uses the lead's code under the arm name "rehearsal".
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import pilot as P

STARTS = (9, 10, 11, 12, 13)  # signed, Section 2: question 2's deciding runs; the run refuses any other
REHEARSAL_STARTS = (1,)  # plan 2, Section 3: the rehearsal alone uses pilot start 1
N_STEPS = 320
STEP = 0.1
HOOK_STEPS = P.BUDGETS  # the hook saves the setting after step n and n - 1 for each of these
LEVELS = P.STAGES
SHUFFLE_LABEL = "q2-shuffle"  # the lead run's own seed label; a shuffle's key is (arm, attack batch, start, setting, r)
PER_TEXT_RELATIVE = 1e-5  # guard G5
SAVED = {"n20": "step_20", "n40": "step_40", "n80": "step_80", "n160": "step_160", "n320": "step_320", "n159": "step_159", "n319": "step_319",
         "h2": "two_step_mean_reaches_2", "h5": "two_step_mean_reaches_5", "h10": "two_step_mean_reaches_10"}
ARMS = {"lead": {"settings": LT.SETTINGS_LEAD, "delta_held": False}, "delta_on": {"settings": LT.SETTINGS_DELTA_ON, "delta_held": True},
        "rehearsal": {"settings": LT.SETTINGS_LEAD, "delta_held": False},
        "rehearsal_delta_on": {"settings": LT.SETTINGS_DELTA_ON, "delta_held": True}}
DECIDING_ARMS = ("lead", "delta_on")
SIDE_PREFIX = {"attack": "A", "heldout": "H"}
# The inputs whose hashes the signed rules record (freeze file, Part 1, Section 0), and the pilot's strata file.
SIGNED_SHA256 = {
    "manifest": "29d709c9a4e11bc35241dca5e851fc0d4f2876c7865328815e3059da2d477d71",
    "starts": "dcb53978dc20a18b9aa6e03480cb8590d7c90f15434d3cc485b9804ea81b9f9d",
}


class GuardFailure(Exception):
    """A guard failed. The message names the guard and the unit, and carries no value."""

    def __init__(self, guard: str, unit: str) -> None:
        self.guard, self.unit = guard, unit
        super().__init__(f"guard {guard} failed in unit {unit}")

    def __reduce__(self) -> tuple[Any, tuple[str, str]]:  # so that it crosses from a container to the launcher intact
        return (GuardFailure, (self.guard, self.unit))


class ContainerFailure(Exception):
    """Any other error in a container, reduced to its type and the container's name: an error's own text can hold a
    value, and no value leaves a container."""

    def __init__(self, kind: str, container: str) -> None:
        self.kind, self.container = kind, container
        super().__init__(f"{kind} in container {container}")

    def __reduce__(self) -> tuple[Any, tuple[str, str]]:
        return (ContainerFailure, (self.kind, self.container))


# ----------------------------------------------------------------------------- the one logging function

LOG_FIELDS: dict[str, type] = {"event": str, "unit": str, "guard": str, "ok": bool, "count": int, "sha256": str, "container": str,
                               "seconds": float, "environment": dict}


def log_record(**fields: Any) -> dict[str, Any]:
    """What may be logged: unit identifiers, counts of finished units, hashes, guard names with their outcomes as true
    or false, a container's seconds, and the environment record. Anything else is refused."""
    for name, value in fields.items():
        if name not in LOG_FIELDS or type(value) is not LOG_FIELDS[name]:
            raise TypeError(f"not a loggable field: {name}")
    if "seconds" in fields and "container" not in fields:
        raise TypeError("seconds are logged per container only")
    if "sha256" in fields and (len(fields["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in fields["sha256"])):
        raise TypeError("not a hash")
    return fields


def _stdout(line: str) -> None:
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


@dataclass
class Log:
    """Every message of the lead modules goes through here, as one JSON line of permitted fields."""

    sink: Callable[[str], None] = _stdout

    def __call__(self, **fields: Any) -> None:
        self.sink(json.dumps(log_record(**fields), sort_keys=True))


# ----------------------------------------------------------------------------- files


def sha_rows(ids: np.ndarray) -> list[str]:
    """Per text, the SHA-256 of its token ids as int32: the manifest's `sha256_512`."""
    return [hashlib.sha256(np.ascontiguousarray(r, dtype=np.int32).tobytes()).hexdigest() for r in np.asarray(ids)]


def ids_sha256(ids: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(np.asarray(ids), dtype=np.int32).tobytes()).hexdigest()


def setting_sha256(flat: np.ndarray) -> str:
    """SHA-256 of a setting's float32 bytes, in the flat layout (C_l + 1 entries per module, the delta entry last)."""
    return hashlib.sha256(np.ascontiguousarray(flat, dtype=np.float32).tobytes()).hexdigest()


def marker(path: Path) -> Path:
    return path.with_name(path.name + ".done")


def finished(path: Path) -> bool:
    """A unit is finished if and only if its completion marker exists and matches the file."""
    return path.is_file() and marker(path).is_file() and marker(path).read_text() == LT.sha256_file(path)


def write_unit(path: Path, arrays: dict[str, np.ndarray], fault: Callable[[str], None] | None = None) -> str:
    """Guard G9: written under a temporary name, renamed, and followed by a completion marker holding its SHA-256."""
    from vpd_audit_2.manifest import deterministic_npz

    path.parent.mkdir(parents=True, exist_ok=True)
    data = deterministic_npz(arrays)
    sha = hashlib.sha256(data).hexdigest()
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    if fault is not None:
        fault("unit_renamed")
    marker(path).write_text(sha)
    return sha


def own_unit(name: str, batch: str) -> bool:
    """Whether a file in the units folder belongs to the container of `batch`: its searches and its scoring blocks."""
    return name.startswith(f"search_{batch}_s") or name.startswith(f"block_{batch}_")


def clean_unfinished(units: Path, batch: str) -> int:
    """On a restart: delete this container's temporary files, its unit files without a matching marker, and its markers
    without their file. Other containers write to the same folder at the same time; their files are left alone."""
    removed = 0
    if not units.is_dir():
        return removed
    for p in sorted(units.iterdir()):
        if own_unit(p.name, batch) and (p.name.endswith(".tmp") or (p.name.endswith(".npz") and not finished(p))):
            p.unlink()
            removed += 1
    for p in sorted(units.iterdir()):  # a marker without its file, or whose file was just removed
        if own_unit(p.name, batch) and p.name.endswith(".done") and not p.with_name(p.name[:-5]).is_file():
            p.unlink()
            removed += 1
    return removed


def unit_meta(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as z:
        return json.loads(str(np.asarray(z["meta"]).reshape(-1)[0]))


# ----------------------------------------------------------------------------- the run's context


@dataclass
class Context:
    arm: str
    units: Path  # the arm's sealed unit files on the volume
    commit: str
    lay: list[tuple[str, int]]
    precision: str = "bf16"
    device: str = "cuda"
    n_steps: int = N_STEPS
    mode: str = "deciding"  # "deciding", "rehearsal" (a calibration batch), or "test" (the tiny model)
    environment: dict[str, Any] = field(default_factory=dict)
    log: Callable[..., None] = field(default_factory=Log)
    commit_volume: Callable[[], None] = lambda: None
    fault: Callable[[str], None] | None = None
    run: Callable[..., dict[str, Any]] = A.run
    timings: dict[str, float] = field(default_factory=dict)
    # Where a held-out container finds the attack searches' files. The same folder as its own units, except in the
    # rehearsal, where one calibration batch plays both roles and each role needs a search file of the same name.
    attack_units: Path | None = None
    prepare: Callable[..., A.Prepared] = A.prepare
    should_stop: Callable[[], bool] = lambda: False  # the spend check's stop, asked for between units
    t0: float = field(default_factory=time.time)  # when the container's function began
    removed_unfinished: int = 0  # the unfinished files of its own that a restarted container deleted

    @property
    def settings(self) -> tuple[str, ...]:
        return ARMS[self.arm]["settings"]

    @property
    def delta_held(self) -> bool:
        return ARMS[self.arm]["delta_held"]

    def tick(self, name: str, seconds: float, count: float = 1.0) -> None:
        self.timings[name] = self.timings.get(name, 0.0) + seconds
        self.timings[name + "_count"] = self.timings.get(name + "_count", 0.0) + count

    def at(self, point: str) -> None:
        if self.fault is not None:
            self.fault(point)


def check_configuration(ctx: Context, starts: tuple[int, ...]) -> None:
    """Lena's Section 4.5: the signed Section 0's configuration, asserted in every container. The rehearsal uses pilot
    start 1 and is held to everything else; the tiny model's tests run on a CPU and are held to none of it."""
    if ctx.mode == "test":
        return
    env = ctx.environment
    ok = (ctx.precision == "bf16" and ctx.device == "cuda" and "B200" in str(env.get("gpu")) and env.get("deterministic_algorithms") is True
          and env.get("deterministic_warn_only") is False and env.get("allow_tf32_matmul") is False and env.get("allow_tf32_cudnn") is False
          and env.get("cublas_workspace_config") == ":4096:8" and env.get("vpd_audit_2_commit") == ctx.commit and env.get("vpd_audit_2_dirty") == "0")
    if ctx.mode == "deciding":
        ok = ok and tuple(starts) == STARTS and ctx.n_steps == N_STEPS and ctx.arm in DECIDING_ARMS and ctx.fault is None
    else:
        ok = ok and ctx.mode == "rehearsal" and ctx.arm not in DECIDING_ARMS and tuple(starts) == REHEARSAL_STARTS
    if not ok:
        raise GuardFailure("configuration", f"container|{ctx.arm}")


def delta_positions(lay: list[tuple[str, int]]) -> np.ndarray:
    """Where the 24 delta entries sit in the flat layout: the last entry of each module."""
    return np.cumsum([c + 1 for _, c in lay]) - 1


def flat_start(start: dict[str, np.ndarray], lay: list[tuple[str, int]], delta_held: bool) -> np.ndarray:
    """The starting point as the search begins from it: flat, and with the delta entries at 1 where they are held."""
    flat = np.concatenate([np.asarray(start[k], dtype=np.float32).reshape(-1) for k, _ in lay])
    if delta_held:
        flat = flat.copy()
        flat[delta_positions(lay)] = 1.0
    return flat


FP_CHUNK = 1 << 26  # entries per pass of the fingerprint
FP_K1, FP_K2 = -7046029254386353131, -4417276706812531889  # 0x9E3779B97F4A7C15 and 0xC2B2AE3D27D4EB4F as signed 64-bit
FP_C2 = 0x165667B19E3779F9
FP_MASK = (1 << 64) - 1


def tensor_checksum(t: Any) -> tuple[int, int]:
    """Two position-weighted sums of a tensor's raw bits, each modulo 2^64, computed on the tensor's own device.

    Every entry's bits are read as a signed integer of the entry's width and multiplied by an odd 64-bit weight that
    depends on the entry's position; integer arithmetic wraps, so the sums are exact and do not depend on the order of
    addition. An odd weight is invertible modulo 2^64, so a change to any one entry, by any amount down to one bit,
    always changes both sums; changes to several entries cancel in both with a chance near 2^-128."""
    import torch

    view_as = {1: torch.int8, 2: torch.int16, 4: torch.int32, 8: torch.int64}
    flat = t.detach().contiguous().view(-1)
    ints = flat.view(view_as[flat.element_size()]) if flat.dtype != torch.bool else flat.to(torch.int8)
    h1 = h2 = 0
    for a in range(0, ints.numel(), FP_CHUNK):
        x = ints[a : a + FP_CHUNK].to(torch.int64)
        idx = torch.arange(a, a + x.numel(), device=x.device, dtype=torch.int64)
        h1 = (h1 + int((x * ((idx * FP_K1) | 1)).sum().item())) & FP_MASK
        h2 = (h2 + int((x * ((idx * FP_K2 + FP_C2) | 1)).sum().item())) & FP_MASK
        del x, idx
    return h1, h2


def prep_fingerprint(prep: A.Prepared) -> str:
    """Guard G3: a bit-exact fingerprint of the batch's labels, target output, and weight deltas. For each tensor, its
    name, dtype, shape, and `tensor_checksum`; the fingerprint is the SHA-256 of those lines.

    The tensors hold about 6 billion entries on the real model. Hashing their bytes on the CPU would take about a
    minute in each of 48 containers; the checksum runs on the GPU in integer arithmetic and takes seconds."""
    lines = []

    def feed(name: str, t: Any) -> None:
        h1, h2 = tensor_checksum(t)
        lines.append(f"{name}|{t.dtype}|{tuple(t.shape)}|{h1:016x}|{h2:016x}")

    for k, v in prep.labels.items():
        feed(f"labels|{k}", v)
    feed("target", prep.target_out)
    for k, v in (prep.weight_deltas or {}).items():
        feed(f"delta|{k}", v)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _bits(x: float) -> bytes:
    return np.float64(x).tobytes()


def _g5(batch_harm: float, per_text: np.ndarray, unit: str) -> None:
    """Guard G5: in float64, the mean of the per-text harms is within 1e-5 relative of the batch harm."""
    if not abs(float(np.mean(per_text.astype(np.float64))) - batch_harm) <= PER_TEXT_RELATIVE * abs(batch_harm):
        raise GuardFailure("G5", unit)


def check_shuffle(flat: np.ndarray, shuffled: np.ndarray, lay: list[tuple[str, int]], strata: dict[str, np.ndarray]) -> bool:
    """Guard G8, its two asserted parts: a shuffled copy has the same sorted values as the setting within every stratum
    of every matrix, and the delta entries unchanged."""
    off = 0
    for name, c in lay:
        st = np.asarray(strata[name])
        a, b = flat[off : off + c], shuffled[off : off + c]
        if not np.array_equal(a[np.lexsort((a, st))], b[np.lexsort((b, st))]) or flat[off + c] != shuffled[off + c]:
            return False
        off += c + 1
    return off == flat.size == shuffled.size


# ----------------------------------------------------------------------------- the units


def search_file(units: Path, batch: str, start: int) -> Path:
    return units / f"search_{batch}_s{start}.npz"


def block_file(units: Path, heldout: str, attack: str, start: int) -> Path:
    return units / f"block_{heldout}_{attack}_s{start}.npz"


def _skip(ctx: Context, path: Path, unit: str, prep_fp: str) -> dict[str, Any]:
    """A finished unit is skipped on a restart, after two checks: it was written at this run's commit, and (guard G3)
    the batch's labels and targets are those it rests on."""
    meta = unit_meta(path)
    if meta["commit"] != ctx.commit:  # a unit left by another commit: the whole run carries one
        raise GuardFailure("one_commit", unit)
    if meta["prep_fp"] != prep_fp:
        raise GuardFailure("G3", unit)
    ctx.log(event="unit_skipped", unit=unit, guard="G3", ok=True)
    return {"unit": unit, "sha256": marker(path).read_text(), "guards": {"G3": True}, "skipped": True}


def _peak_reset(ctx: Context) -> None:
    if ctx.device == "cuda":
        import torch

        torch.cuda.reset_peak_memory_stats()


def _peak_read(ctx: Context) -> None:
    if ctx.device == "cuda":
        import torch

        ctx.timings["peak_scoring_gib"] = max(ctx.timings.get("peak_scoring_gib", 0.0), torch.cuda.max_memory_allocated() / 2**30)


@dataclass
class TimedHook(A.SaveHook):
    """The save hook, noting the clock each time the search calls it. The search calls it once per iteration, after that
    iteration's harm has become a number, and once more after the last harm. It saves exactly what `A.SaveHook` saves,
    and the search itself is untouched."""

    at: list[float] = field(default_factory=list)

    def __call__(self, k: int, record: list[float], sources: dict[str, Any], cum: tuple[np.ndarray, np.ndarray] | None = None) -> None:
        self.at.append(time.time())
        super().__call__(k, record, sources, cum)


def _tick_search(ctx: Context, began: float, ended: float, at: list[float]) -> None:
    """A search's seconds by part, from the clock at each call of the hook (calls 0 to n, for n iterations): its first
    iteration, which carries a container's warm-up; the rest of its first ten; the iterations after them, which give
    the steady rate; its last harm; and its return."""
    ctx.tick("search", ended - began, ctx.n_steps)
    warm = LG.WARM_ITERATIONS
    if len(at) != ctx.n_steps + 1 or ctx.n_steps <= warm:
        return
    ctx.tick("search_iteration_0", at[0] - began)
    ctx.tick("search_iterations_warm", at[warm - 1] - at[0], warm - 1)
    ctx.tick("search_iterations_after_warm", at[ctx.n_steps - 1] - at[warm - 1], ctx.n_steps - warm)
    ctx.tick("search_final_harm", at[ctx.n_steps] - at[ctx.n_steps - 1])
    ctx.tick("search_tail", ended - at[ctx.n_steps])


def search_unit(model: Any, prep: A.Prepared, ctx: Context, side: str, batch: str, start_index: int, start: dict[str, np.ndarray],
                batch_ids_sha: str, prep_fp: str) -> dict[str, Any]:
    """One search and its own-batch re-scores (Lena's Sections 4.1 and 4.2)."""
    unit = f"search|{ctx.arm}|{batch}|s{start_index}"
    path = search_file(ctx.units, batch, start_index)
    if finished(path):
        return _skip(ctx, path, unit, prep_fp)
    t_unit = time.time()
    hook = TimedHook(steps=tuple(n for n in HOOK_STEPS if n <= ctx.n_steps), thresholds=LEVELS)
    frozen = A.Frozen.delta_entries(model, 1.0, ctx.device) if ctx.delta_held else None
    t0 = time.time()
    ctx.timings.setdefault("to_first_search_step", t0 - ctx.t0)
    r = ctx.run(model, prep, start, ctx.n_steps, STEP, frozen=frozen, save_hook=hook, cum_grads=True, device=ctx.device)
    _tick_search(ctx, t0, time.time(), hook.at)
    record = [float(x) for x in r["record"]]

    # G7: the hook and the crossing rule agree, and are missing together
    for h in LEVELS:
        if hook.events.get(f"two_step_mean_reaches_{h:g}") != P.crossing(record, h)["k"]:
            raise GuardFailure("G7", unit)
    dpos = delta_positions(ctx.lay)
    if ctx.delta_held and any(not (flat[dpos] == 1.0).all() for flat in hook.saved.values()):
        raise GuardFailure("delta_entries_held", unit)

    # the starting point and every scored setting, re-scored on this batch through the per-text path
    _peak_reset(ctx)
    t0 = time.time()
    first = flat_start(start, ctx.lay, ctx.delta_held)
    init, init_text = A.score_per_text(model, P.unflatten(first, ctx.lay), prep, device=ctx.device)
    if _bits(init) != _bits(record[0]):
        raise GuardFailure("G4", unit)
    _g5(init, init_text, unit)
    scored = [name for name in ctx.settings if SAVED[name] in hook.saved]
    own, own_text = [], []
    for name in scored:
        h, per_text = A.score_per_text(model, P.unflatten(hook.saved[SAVED[name]], ctx.lay), prep, device=ctx.device)
        if _bits(h) != _bits(record[hook.events[SAVED[name]]]):
            raise GuardFailure("G4", unit)
        _g5(h, per_text, unit)
        own.append(h)
        own_text.append(per_text)
    ctx.tick("scoring", time.time() - t0, 1 + len(scored))
    ctx.tick("scoring_in_search_units", time.time() - t0, 1 + len(scored))
    _peak_read(ctx)
    guards = {"G4": True, "G5": True, "G7": True}
    if ctx.mode != "deciding":
        # Outside the deciding run (the rehearsal on the real model, and the tiny model's tests): the per-text wrapper's
        # batch value equals the authors' function's, bit for bit, on the start and on every scored setting.
        flats = [first] + [hook.saved[SAVED[name]] for name in scored]
        t0 = time.time()
        for flat, ours in zip(flats, [init] + own):
            if _bits(A.score(model, P.unflatten(flat, ctx.lay), prep, device=ctx.device)) != _bits(ours):
                raise GuardFailure("wrapper_equals_authors", unit)
        ctx.tick("wrapper_check", time.time() - t0, len(flats))  # timed apart: a deciding container does not run it
        guards["wrapper_equals_authors"] = True
    if ctx.delta_held:
        guards["delta_entries_held"] = True

    names = sorted(hook.saved)
    meta = {"unit": unit, "kind": "search", "arm": ctx.arm, "side": side, "batch": batch, "start": start_index,
            "start_sha256": setting_sha256(flat_start(start, ctx.lay, False)), "ids_sha": batch_ids_sha, "prep_fp": prep_fp, "commit": ctx.commit,
            "n_steps": ctx.n_steps, "delta_held": ctx.delta_held, "precision": ctx.precision, "environment": ctx.environment}
    arrays = {
        "record": np.asarray(record, dtype=np.float64),
        "hook_names": np.array(names), "hook_steps": np.array([hook.events[n] for n in names], dtype=np.int64),
        "settings": np.stack([hook.saved[n] for n in names]).astype(np.float32),
        "cum_signed": np.stack([hook.cum[n][0] for n in names]).astype(np.float32),
        "cum_abs": np.stack([hook.cum[n][1] for n in names]).astype(np.float32),
        "scored_names": np.array(scored), "own": np.asarray(own, dtype=np.float64),
        "own_text": np.asarray(own_text, dtype=np.float32).reshape(len(scored), prep.n_texts),
        "init": np.asarray([init], dtype=np.float64), "init_text": np.asarray(init_text, dtype=np.float32),
        "meta": np.array(json.dumps(meta, sort_keys=True)),
    }
    sha = write_unit(path, arrays, ctx.fault)
    ctx.tick("search_unit_whole", time.time() - t_unit)
    ctx.log(event="unit_finished", unit=unit, sha256=sha)
    return {"unit": unit, "sha256": sha, "guards": guards, "skipped": False}


def scoring_block(model: Any, prep: A.Prepared, ctx: Context, heldout: str, attack: str, start_index: int, strata: dict[str, np.ndarray],
                  batch_ids_sha: str, prep_fp: str) -> dict[str, Any]:
    """One attack search's scored settings, and the 8 shuffled copies of those that have them, on this held-out batch
    (Lena's Sections 4.1 and 4.3). Reads the attack search's settings from the volume; never its text."""
    unit = f"block|{ctx.arm}|{heldout}|{attack}|s{start_index}"
    path = block_file(ctx.units, heldout, attack, start_index)
    if finished(path):
        return _skip(ctx, path, unit, prep_fp)
    t_unit = time.time()
    src = search_file(ctx.attack_units or ctx.units, attack, start_index)
    if not finished(src):  # G10: the attack file read is the one written
        raise GuardFailure("G10", unit)
    src_sha = marker(src).read_text()
    with np.load(src, allow_pickle=False) as z:
        hook_names = [str(x) for x in z["hook_names"]]
        scored_there = {str(x) for x in z["scored_names"]}
        settings = z["settings"]
    names = [name for name in ctx.settings if name in scored_there]
    n, T, R = len(names), prep.n_texts, LT.N_SHUFFLES
    out = {"carried": np.full(n, np.nan), "carried_text": np.full((n, T), np.nan, dtype=np.float32), "shuf": np.full((n, R), np.nan),
           "shuf_text": np.full((n, R, T), np.nan, dtype=np.float32), "moved": np.full((n, R), np.nan), "moved_alive": np.full((n, R), np.nan),
           "absmean_alive": np.full((n, R), np.nan), "identical_copies": np.zeros(n, dtype=np.int64)}
    scored_sha, shuf_sha = [], [["" for _ in range(R)] for _ in range(n)]
    _peak_reset(ctx)
    t0, passes, shuffle_seconds = time.time(), 0, 0.0
    for q, name in enumerate(names):
        flat = settings[hook_names.index(SAVED[name])]
        source = P.unflatten(flat, ctx.lay)
        scored_sha.append(hashlib.sha256(b"".join(source[k].tobytes() for k, _ in ctx.lay)).hexdigest())  # G11: the setting as scored
        h, per_text = A.score_per_text(model, source, prep, device=ctx.device)
        _g5(h, per_text, unit)
        out["carried"][q], out["carried_text"][q] = h, per_text
        passes += 1
        if name in LT.NO_SHUFFLES:
            continue
        copies = []
        for r in range(1, R + 1):
            t1 = time.time()
            copy = P.shuffle_source(flat, ctx.lay, strata, (ctx.arm, attack, start_index, name, r), label=SHUFFLE_LABEL)
            if not check_shuffle(flat, copy, ctx.lay, strata):
                raise GuardFailure("G8", unit)
            if ctx.delta_held and not (copy[delta_positions(ctx.lay)] == 1.0).all():
                raise GuardFailure("delta_entries_held", unit)
            d = LT.shuffle_displacement(flat, copy, ctx.lay, strata)
            shuffle_seconds += time.time() - t1
            h, per_text = A.score_per_text(model, P.unflatten(copy, ctx.lay), prep, device=ctx.device)
            _g5(h, per_text, unit)
            out["shuf"][q, r - 1], out["shuf_text"][q, r - 1] = h, per_text
            out["moved"][q, r - 1], out["moved_alive"][q, r - 1], out["absmean_alive"][q, r - 1] = d["moved"], d["moved_alive"], d["absmean_alive"]
            shuf_sha[q][r - 1] = setting_sha256(copy)
            copies.append(copy)
            passes += 1
        # G8, its third part, recorded as a count and not asserted: copies equal to the setting or to an earlier copy
        out["identical_copies"][q] = sum(np.array_equal(c, flat) or any(np.array_equal(c, e) for e in copies[:k]) for k, c in enumerate(copies))
        ctx.at("in_block")
    ctx.tick("scoring", time.time() - t0 - shuffle_seconds, passes)
    ctx.tick("scoring_in_blocks", time.time() - t0 - shuffle_seconds, passes)
    ctx.tick("making_shuffles", shuffle_seconds, float(passes - n))
    _peak_read(ctx)
    meta = {"unit": unit, "kind": "block", "arm": ctx.arm, "heldout": heldout, "attack": attack, "start": start_index, "block_ids_sha": batch_ids_sha,
            "prep_fp": prep_fp, "attack_file_sha256": src_sha, "commit": ctx.commit}
    arrays = {**out, "names": np.array(names), "scored_sha": np.array(scored_sha), "shuf_sha": np.array(shuf_sha).reshape(n, R),
              "meta": np.array(json.dumps(meta, sort_keys=True))}
    sha = write_unit(path, arrays, ctx.fault)
    ctx.tick("block_whole", time.time() - t_unit)
    ctx.log(event="unit_finished", unit=unit, sha256=sha)
    return {"unit": unit, "sha256": sha, "guards": {"G5": True, "G8": True, "G10": True}, "skipped": False}


# ----------------------------------------------------------------------------- what a container runs


def guard_batch(ctx: Context, side: str, batch: str, ids: np.ndarray, expected_rows: list[str], allow_pool: str | None = None) -> None:
    """Guard G1: the batch is the one named. Its per-text hashes equal the manifest's, and its pool is on this
    container's side. `allow_pool` is the rehearsal's override of the pool check, for one named calibration batch."""
    on_side = batch.startswith(SIDE_PREFIX[side]) and batch[1:].isdigit()
    if allow_pool is not None:  # never in a deciding container
        on_side = ctx.mode in ("rehearsal", "test") and batch == allow_pool
    if not on_side or sha_rows(ids) != list(expected_rows):
        raise GuardFailure("G1", f"container|{ctx.arm}|{batch}")


def _prepare(model: Any, ctx: Context, side: str, batch: str, ids: np.ndarray, expected_rows: list[str], starts: dict[int, Any],
             allow_pool: str | None) -> tuple[A.Prepared, str, str]:
    guard_batch(ctx, side, batch, ids, expected_rows, allow_pool)
    check_configuration(ctx, tuple(sorted(starts)))
    t0 = time.time()
    prep = ctx.prepare(model, ids, ctx.precision, device=ctx.device)
    ctx.tick("labels_and_targets", time.time() - t0)
    t0 = time.time()
    prep_fp = prep_fingerprint(prep)
    ctx.tick("fingerprint", time.time() - t0)
    removed = clean_unfinished(ctx.units, batch)
    ctx.removed_unfinished += removed
    if "to_ready" not in ctx.timings:  # the end of preparation, whether or not a search follows
        ctx.tick("to_ready", time.time() - ctx.t0)
    ctx.log(event="container_started", container=f"{ctx.arm}|{batch}", count=removed)
    return prep, ids_sha256(ids), prep_fp


def _commit(ctx: Context, after: str, wrote: bool) -> None:
    """Guard G9's commit of the volume, after a search unit or after an attack batch's blocks. Its seconds are kept by
    kind, and apart where nothing new was written (every unit skipped), which costs almost nothing."""
    t0 = time.time()
    ctx.commit_volume()
    ctx.tick(f"volume_commit_after_{after}" if wrote else "volume_commit_nothing_new", time.time() - t0)


def job_return(ctx: Context, container: str, units: list[dict[str, Any]], expected: int, stopped: bool) -> dict[str, Any]:
    """What a job returns (plan 2, Section 5.2): the container's name; per unit, its identifier, one SHA-256 of its
    file, guard outcomes as true or false, and whether it was skipped; counts of units; the container's seconds; and
    the environment record. Nothing else: no per-setting hash, no pass count, no file size, no timing finer than the
    container. Timings by kind, and the count of its own unfinished files a restarted container deleted, are added for
    a calibration batch alone, never in the deciding run."""
    for u in units:
        ok = (set(u) == {"unit", "sha256", "guards", "skipped"} and type(u["unit"]) is str and type(u["sha256"]) is str and len(u["sha256"]) == 64
              and type(u["skipped"]) is bool and all(type(k) is str and type(v) is bool for k, v in u["guards"].items()))
        if not ok:
            raise TypeError("not a unit's return")
    out = {"container": container, "units": units, "finished_units": len(units), "expected_units": expected, "stopped": bool(stopped),
           "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment)}
    if ctx.mode == "rehearsal":
        out["timings"] = {k: float(v) for k, v in ctx.timings.items()}
        out["removed_unfinished"] = int(ctx.removed_unfinished)
    ctx.log(event="container_finished", container=container, count=len(units), seconds=out["seconds"])
    return out


def attack_job(model: Any, ctx: Context, batch: str, ids: np.ndarray, expected_rows: list[str], starts: dict[int, dict[str, np.ndarray]],
               allow_pool: str | None = None) -> dict[str, Any]:
    """An attack container: prepare the batch; for each start, one search unit. It holds no held-out text."""
    prep, batch_ids_sha, prep_fp = _prepare(model, ctx, "attack", batch, ids, expected_rows, starts, allow_pool)
    units, stopped = [], False
    for s in sorted(starts):
        if ctx.should_stop():
            stopped = True
            break
        units.append(search_unit(model, prep, ctx, "attack", batch, s, starts[s], batch_ids_sha, prep_fp))
        _commit(ctx, "search", not units[-1]["skipped"])
        ctx.at("between_units")
    return job_return(ctx, f"{ctx.arm}|attack|{batch}", units, len(starts), stopped)


def heldout_job(model: Any, ctx: Context, batch: str, ids: np.ndarray, expected_rows: list[str], starts: dict[int, dict[str, np.ndarray]],
                attack_batches: list[str], strata: dict[str, np.ndarray], allow_pool: str | None = None) -> dict[str, Any]:
    """A held-out container: prepare the batch; for each start, its own search unit; then, for each attack batch and each
    start, one scoring block. It receives the attack batches' names, never their token ids."""
    prep, batch_ids_sha, prep_fp = _prepare(model, ctx, "heldout", batch, ids, expected_rows, starts, allow_pool)
    units, stopped = [], False
    expected = len(starts) * (1 + len(attack_batches))
    for s in sorted(starts):
        if ctx.should_stop():
            stopped = True
            break
        units.append(search_unit(model, prep, ctx, "heldout", batch, s, starts[s], batch_ids_sha, prep_fp))
        _commit(ctx, "search", not units[-1]["skipped"])
        ctx.at("between_units")
    for attack in attack_batches:
        if stopped or ctx.should_stop():  # asked once per attack batch, where the volume is committed
            stopped = True
            break
        blocks = []
        for s in sorted(starts):
            blocks.append(scoring_block(model, prep, ctx, batch, attack, s, strata, batch_ids_sha, prep_fp))
            ctx.at("between_units")
        units += blocks
        _commit(ctx, "blocks", any(not b["skipped"] for b in blocks))
    return job_return(ctx, f"{ctx.arm}|heldout|{batch}", units, expected, stopped)


NOTICE = ("DO NOT OPEN. Every file in this folder holds harms from the lead experiment's batches, sealed until the committed\n"
          "analysis script, `vpd_audit_2/lead_analysis.py`, runs on the complete tables (freeze/part1.md, Section 10, item 4;\n"
          "freeze/amendment1.md, Section 6). Nothing else may load, list the contents of, or print from these files.\n")
# What only a rehearsal's spec may carry: the override of the pool check, unit folders of its own, a shorter search, and
# the two triggers (plan 4, Section 6, rows 2 and 3).
REHEARSAL_ONLY = ("allow_pool", "attack_units", "n_steps", "stop_after_first_unit", "kill_at", "kill_after", "kill_key")


def check_spec(spec: dict[str, Any], has_trigger: bool) -> None:
    """A spec is a deciding container's or a rehearsal's, and a deciding one carries nothing that only a rehearsal may."""
    deciding = spec.get("mode") == "deciding"
    ok = spec.get("mode") in ("deciding", "rehearsal") and spec.get("side") in SIDE_PREFIX
    if deciding:
        ok = ok and not any(k in spec for k in REHEARSAL_ONLY) and spec.get("units") == "units" and not has_trigger and spec.get("arm") in DECIDING_ARMS
    else:
        ok = ok and spec.get("arm") not in DECIDING_ARMS
    if not ok:
        raise GuardFailure("configuration", f"container|{spec.get('arm')}")


def rehearsal_trigger(spec: dict[str, Any], *, set_stop: Callable[[], None], kill: Callable[[], None]) -> Callable[[str], None] | None:
    """A rehearsal's two triggers (plan 4, Section 6, rows 2 and 3), as the hook a container calls at its named points;
    `None` for a spec that asks for neither, as every deciding spec must.

      - `stop_after_first_unit`: after its first unit the container sets the run's stop flag (`set_stop`), as the
        `stop` command does, and so stops before its second.
      - `kill_at`, after `kill_after`: at the first point named `kill_at` that follows a point named `kill_after`, the
        container is killed (`kill`, which does it once in the run). With `unit_renamed` after `between_units`, that is
        inside the container's second unit, after its file's rename and before its marker, when its first unit is
        finished and committed."""
    if not spec.get("stop_after_first_unit") and not spec.get("kill_at"):
        return None
    seen = {"stop": False, "armed": False}

    def fault(point: str) -> None:
        if spec.get("stop_after_first_unit") and point == "between_units" and not seen["stop"]:
            seen["stop"] = True
            set_stop()
        if spec.get("kill_at") == point and seen["armed"]:
            kill()
        if spec.get("kill_after") == point:
            seen["armed"] = True

    return fault


def run_spec(model: Any, spec: dict[str, Any], ids: np.ndarray, rows: list[str], starts: dict[int, dict[str, np.ndarray]],
             strata: dict[str, np.ndarray] | None, lay: list, *, environment: dict[str, Any], log: Callable[..., None], commit_volume: Callable[[], None],
             should_stop: Callable[[], bool], fault: Callable[[str], None] | None = None, t0: float | None = None, device: str = "cuda",
             precision: str = "bf16") -> dict[str, Any]:
    """What a container does with the spec it is handed (`lead_launch.container_specs`): its one batch, on its side of
    its arm, in the folders the spec names. The deciding run and the rehearsal both come through here."""
    check_spec(spec, fault is not None)
    sealed = Path(spec["root"]) / "sealed"
    sealed.mkdir(parents=True, exist_ok=True)
    (sealed / "DO_NOT_OPEN.md").write_text(NOTICE)
    ctx = Context(arm=spec["arm"], units=sealed / spec["units"], commit=spec["commit"], lay=[tuple(x) for x in lay], precision=precision, device=device,
                  n_steps=int(spec.get("n_steps", N_STEPS)), mode=spec["mode"], environment=environment, log=log, commit_volume=commit_volume, fault=fault,
                  attack_units=sealed / spec["attack_units"] if spec.get("attack_units") else None, should_stop=should_stop,
                  t0=time.time() if t0 is None else t0)
    if spec["side"] == "attack":
        return attack_job(model, ctx, spec["batch"], ids, rows, starts, allow_pool=spec.get("allow_pool"))
    return heldout_job(model, ctx, spec["batch"], ids, rows, starts, spec["attack_batches"], strata, allow_pool=spec.get("allow_pool"))


def compare_with_pilot(path: Path, pilot: dict[str, Any]) -> dict[str, bool]:
    """The rehearsal's first required outcome: a search unit's record and its saved settings' hashes against the pilot's
    stored ones for the same batch and start (`results/s4_pilot/part_a/runs.json`), bit for bit."""
    with np.load(path, allow_pickle=False) as z:
        record = z["record"].tolist()
        names = [str(x) for x in z["hook_names"]]
        steps = {n: int(k) for n, k in zip(names, z["hook_steps"])}
        hashes = {n: setting_sha256(z["settings"][k]) for k, n in enumerate(names)}
    return {"record_equals_pilot": record == [float(x) for x in pilot["record"]],
            "saved_settings_equal_pilot": hashes == dict(pilot["saved_sources_sha256"]),
            "hook_steps_equal_pilot": steps == {k: int(v) for k, v in pilot["hook_events"].items()}}


# ----------------------------------------------------------------------------- the assembler


def compare_search_units(a: Path, b: Path) -> dict[str, bool]:
    """Two search units of the same batch and start, from two containers: the record, the saved settings, and the
    fingerprint of labels and targets, each bit for bit (the rehearsal, plan 2, Section 7)."""
    with np.load(a, allow_pickle=False) as za, np.load(b, allow_pickle=False) as zb:
        same_names = [str(x) for x in za["hook_names"]] == [str(x) for x in zb["hook_names"]]
        return {"record_equal": bool(za["record"].tobytes() == zb["record"].tobytes()),
                "saved_settings_equal": bool(same_names and za["settings"].tobytes() == zb["settings"].tobytes()
                                             and np.array_equal(za["hook_steps"], zb["hook_steps"])),
                "prep_fp_equal": unit_meta(a)["prep_fp"] == unit_meta(b)["prep_fp"]}


def expected_units(units: Path, attack: list[str], heldout: list[str], starts: list[int], heldout_units: Path | None = None) -> list[Path]:
    """Every unit of an arm: each attack batch's and each held-out batch's searches, and every scoring block."""
    hu = heldout_units or units
    return ([search_file(units, b, s) for b in attack for s in starts] + [search_file(hu, b, s) for b in heldout for s in starts]
            + [block_file(hu, j, i, s) for j in heldout for i in attack for s in starts])


# The cross-unit guards an arm's units must pass. The last two are the wrong-batch guards: a rehearsal, with one batch
# on both sides, must see exactly these two fail.
REQUIRED_GUARDS = ("G10", "G11_setting_is_the_attack_searchs", "shuffles_the_same_in_every_container", "one_commit",
                   "block_prep_fp_is_the_heldout_batchs")
WRONG_BATCH_GUARDS = ("G6", "G11_differs_from_the_heldout_batchs_own")


def _gather(units: Path, arm: str, attack: list[str], heldout: list[str], starts: list[int], *, expect_commit: str | None, rehearsal: bool,
            heldout_units: Path | None, name: str) -> dict[str, Any]:
    """Read an arm's unit files for the listed batches: both sides' searches, and every scoring block of the listed
    held-out batches. Values are placed by the names each file carries, and the cross-unit guards are computed as true or
    false. Raises only where nothing further can be read: a unit unfinished or misnamed, or a batch resting on two
    fingerprints of labels and targets."""
    settings = ARMS[arm]["settings"]
    Q, KA, KH, ns = len(settings), len(attack), len(heldout), len(starts)
    side_units = {"A": units, "H": heldout_units or units}
    # 1. every expected unit has its completion marker, and the marker's hash matches the file
    for p in expected_units(units, attack, heldout, starts, heldout_units):
        if not finished(p):
            raise GuardFailure("units_complete", name)

    def load(path: Path) -> dict[str, Any]:
        with np.load(path, allow_pickle=False) as z:
            d = {k: z[k] for k in z.files if k != "meta"}
        d["meta"] = unit_meta(path)
        return d

    commits: set[str] = set()
    T = None
    side_data: dict[str, dict[str, Any]] = {}
    search_sha: dict[tuple[str, int], str] = {}
    setting_bytes_sha: dict[tuple[str, int, str], str] = {}
    for side, batches in (("A", attack), ("H", heldout)):
        first = load(search_file(side_units[side], batches[0], starts[0]))
        T = int(first["init_text"].shape[0])
        n_record = int(first["record"].shape[0])
        d = {"rec": np.zeros((len(batches), ns, n_record)), "step": np.full((len(batches), ns, Q), -1, dtype=np.int32),
             "own": np.full((len(batches), ns, Q), np.nan), "init": np.zeros((len(batches), ns)),
             "setting_sha": np.full((len(batches), ns, Q), "", dtype="<U64"), "prep_fp": [], "ids_sha": [],
             "own_text": np.full((len(batches), ns, Q, T), np.nan, dtype=np.float32), "init_text": np.zeros((len(batches), ns, T), dtype=np.float32)}
        for b, batch in enumerate(batches):
            fps, idss = set(), set()
            for s, start in enumerate(starts):
                path = search_file(side_units[side], batch, start)
                u = load(path)
                m = u["meta"]
                if (m["batch"], m["start"], m["arm"]) != (batch, start, arm):  # placed by name, never by file order
                    raise GuardFailure("unit_names", name)
                commits.add(m["commit"])
                fps.add(m["prep_fp"])
                idss.add(m["ids_sha"])
                if side == "A":
                    search_sha[(batch, start)] = marker(path).read_text()
                d["rec"][b, s], d["init"][b, s], d["init_text"][b, s] = u["record"], u["init"][0], u["init_text"]
                hook_names = [str(x) for x in u["hook_names"]]
                scored = [str(x) for x in u["scored_names"]]
                for q, setting in enumerate(settings):
                    if setting in scored:
                        k = hook_names.index(SAVED[setting])
                        d["step"][b, s, q] = int(u["hook_steps"][k])
                        d["own"][b, s, q], d["own_text"][b, s, q] = u["own"][scored.index(setting)], u["own_text"][scored.index(setting)]
                        d["setting_sha"][b, s, q] = setting_sha256(u["settings"][k])
                        if side == "A":
                            setting_bytes_sha[(batch, start, setting)] = str(d["setting_sha"][b, s, q])
            if len(fps) != 1 or len(idss) != 1:  # G3 across units: one set of labels and targets per batch
                raise GuardFailure("G3", name)
            d["prep_fp"].append(fps.pop())
            d["ids_sha"].append(idss.pop())
        side_data[side] = d
    A_, H_ = side_data["A"], side_data["H"]

    R = LT.N_SHUFFLES
    carried = np.full((KA, KH, ns, Q), np.nan)
    shuf = np.full((KA, KH, ns, Q, R), np.nan)
    carried_text = np.full((KA, KH, ns, Q, T), np.nan, dtype=np.float32)
    shuf_text = np.full((KA, KH, ns, Q, R, T), np.nan, dtype=np.float32)
    block_ids = np.full((KA, KH, ns), "", dtype="<U64")
    shuf_sha = np.full((KA, ns, Q, R), "", dtype="<U64")
    described = {k: np.full((KA, ns, Q, R), np.nan) for k in ("moved", "moved_alive", "absmean_alive")}
    g6_all_equal = g11_sha = g11_all_equal = g10 = consistent = same_fp = True
    g6_any_equal = g11_any_equal = False
    for j, hb in enumerate(heldout):
        for i, ab in enumerate(attack):
            for s, start in enumerate(starts):
                u = load(block_file(side_units["H"], hb, ab, start))
                m = u["meta"]
                if (m["heldout"], m["attack"], m["start"], m["arm"]) != (hb, ab, start, arm):
                    raise GuardFailure("unit_names", name)
                commits.add(m["commit"])
                g10 = g10 and m["attack_file_sha256"] == search_sha[(ab, start)]
                # the carried cell and the denominator used the same labels and targets (plan 4, Section 4.5)
                same_fp = same_fp and m["prep_fp"] == H_["prep_fp"][j]
                block_ids[i, j, s] = m["block_ids_sha"]
                for k, setting in enumerate(str(x) for x in u["names"]):
                    q = settings.index(setting)
                    carried[i, j, s, q], carried_text[i, j, s, q] = u["carried"][k], u["carried_text"][k]
                    shuf[i, j, s, q], shuf_text[i, j, s, q] = u["shuf"][k], u["shuf_text"][k]
                    g11_sha = g11_sha and str(u["scored_sha"][k]) == setting_bytes_sha.get((ab, start, setting))
                    same_as_attack = np.array_equal(u["carried_text"][k], A_["own_text"][i, s, q])
                    same_as_heldout = np.array_equal(u["carried_text"][k], H_["own_text"][j, s, q])
                    g6_any_equal, g6_all_equal = g6_any_equal or same_as_attack, g6_all_equal and same_as_attack
                    g11_any_equal, g11_all_equal = g11_any_equal or same_as_heldout, g11_all_equal and same_as_heldout
                    if setting in LT.NO_SHUFFLES:
                        continue
                    for key in described:
                        if j == 0:
                            described[key][i, s, q] = u[key][k]
                        consistent = consistent and np.array_equal(described[key][i, s, q], u[key][k])
                    if j == 0:
                        shuf_sha[i, s, q] = u["shuf_sha"][k]
                    consistent = consistent and np.array_equal(shuf_sha[i, s, q], u["shuf_sha"][k])  # every held-out container made the same shuffles

    outcomes = {"G6": not g6_any_equal, "G10": bool(g10), "G11_setting_is_the_attack_searchs": bool(g11_sha),
                "G11_differs_from_the_heldout_batchs_own": not g11_any_equal, "shuffles_the_same_in_every_container": bool(consistent),
                "one_commit": len(commits) == 1 and (expect_commit is None or commits == {expect_commit}),
                "block_prep_fp_is_the_heldout_batchs": bool(same_fp)}
    if rehearsal:  # the same batch on both sides: G6 must see every carried vector equal to the own-batch one
        outcomes["G6_reports_every_carried_vector_equal"] = bool(g6_all_equal)
        outcomes["G11_reports_every_carried_vector_equal_to_the_heldout_own"] = bool(g11_all_equal)
    return {"settings": settings, "T": T, "A": A_, "H": H_, "carried": carried, "shuf": shuf, "carried_text": carried_text, "shuf_text": shuf_text,
            "block_ids": block_ids, "shuf_sha": shuf_sha, "described": described, "commits": commits, "outcomes": outcomes}


def cross_unit_guards(units: Path, arm: str, attack: list[str], heldout: list[str], starts: list[int], *, expect_commit: str | None = None,
                      rehearsal: bool = False, heldout_units: Path | None = None) -> dict[str, bool]:
    """The guards-only pass (session 5, plan 4, Section 4.3): the assembler's cross-unit guards on the listed held-out
    batches' blocks against the attack searches, each as true or false. It is the assembler's own reading of the units,
    stopped before any table is built; nothing is written and nothing but the guards' names and outcomes is returned."""
    return dict(_gather(units, arm, attack, heldout, starts, expect_commit=expect_commit, rehearsal=rehearsal, heldout_units=heldout_units,
                        name=f"guards|{arm}")["outcomes"])


def assemble(units: Path, out_dir: Path, arm: str, attack: list[str], heldout: list[str], starts: list[int], *, text_ids_H: list[list[str]],
             excluded: list[dict[str, Any]], inputs_sha256: dict[str, str], containers: list[dict[str, Any]], expect_commit: str | None = None,
             lead_prep_fp: dict[str, dict[str, str]] | None = None, rehearsal: bool = False, heldout_units: Path | None = None,
             part_bytes: int | None = None, returned_sha256: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    """Build an arm's table from its unit files (Lena's Section 4.4), run every completeness check and cross-unit guard,
    and write the files deterministically. Returns the files' names and hashes, the declared sizes, and guard outcomes;
    never the pass count. In rehearsal mode the refusals a one-batch arm must provoke are recorded as outcomes and the
    table is written all the same, for the copy test. `heldout_units` is the rehearsal's separate folder for the
    held-out role's files, and `part_bytes` its small part size, which forces the per-text file into parts.

    `returned_sha256` is each unit's hash as its container returned it, by side ("attack", "heldout") and unit: where
    given, every unit file must still be the one its container returned."""
    name = f"assemble|{arm}"
    if part_bytes is not None and not rehearsal:
        raise GuardFailure("configuration", name)
    g = _gather(units, arm, attack, heldout, starts, expect_commit=expect_commit, rehearsal=rehearsal, heldout_units=heldout_units, name=name)
    settings, T, A_, H_, commits, outcomes = g["settings"], g["T"], g["A"], g["H"], g["commits"], g["outcomes"]
    carried, shuf, carried_text, shuf_text = g["carried"], g["shuf"], g["carried_text"], g["shuf_text"]
    block_ids, shuf_sha, described = g["block_ids"], g["shuf_sha"], g["described"]
    Q, KA, KH, ns, R = len(settings), len(attack), len(heldout), len(starts), LT.N_SHUFFLES
    required = REQUIRED_GUARDS + (() if rehearsal else WRONG_BATCH_GUARDS)
    if returned_sha256 is not None:
        hu = heldout_units or units
        unit_files = ([("attack", f"search|{arm}|{b}|s{s}", search_file(units, b, s)) for b in attack for s in starts]
                      + [("heldout", f"search|{arm}|{b}|s{s}", search_file(hu, b, s)) for b in heldout for s in starts]
                      + [("heldout", f"block|{arm}|{j}|{i}|s{s}", block_file(hu, j, i, s)) for j in heldout for i in attack for s in starts])
        outcomes["units_are_the_ones_their_containers_returned"] = all(marker(p).read_text() == returned_sha256[side].get(unit) for side, unit, p in unit_files)
        required += ("units_are_the_ones_their_containers_returned",)
    for guard in required:
        if not outcomes[guard]:
            raise GuardFailure(guard, name)

    pool_of = {hb: j for j, hb in enumerate(heldout)}
    excluded_H = np.zeros((KH, T), dtype=bool)
    for e in excluded:
        if e["pool"] in pool_of:
            excluded_H[pool_of[e["pool"]], int(e["index"])] = True
    has_shuffles = np.array([n not in LT.NO_SHUFFLES for n in settings])
    table: dict[str, Any] = {
        "rec_A": A_["rec"], "rec_H": H_["rec"], "step_A": A_["step"], "step_H": H_["step"], "own_A": A_["own"], "own_H": H_["own"],
        "init_A": A_["init"], "init_H": H_["init"], "setting_sha_A": A_["setting_sha"], "setting_sha_H": H_["setting_sha"],
        "prep_fp_A": np.array(A_["prep_fp"]), "prep_fp_H": np.array(H_["prep_fp"]), "ids_sha_A": np.array(A_["ids_sha"]), "ids_sha_H": np.array(H_["ids_sha"]),
        "carried": carried, "shuf": shuf, "block_ids_sha": block_ids, "shuf_sha": shuf_sha, "shuf_moved": described["moved"],
        "shuf_moved_alive": described["moved_alive"], "shuf_absmean_alive": described["absmean_alive"],
        "attack_names": np.array(attack), "heldout_names": np.array(heldout), "starts": np.array(starts, dtype=np.int64),
        "setting_names": np.array(settings), "has_shuffles": has_shuffles, "excluded_H": excluded_H, "text_ids_H": np.array(text_ids_H),
        "carried_text": carried_text, "shuf_text": shuf_text, "own_A_text": A_["own_text"], "own_H_text": H_["own_text"],
        "init_A_text": A_["init_text"], "init_H_text": H_["init_text"],
    }
    pairing = None
    if lead_prep_fp is not None:  # the delta-on arm: each shared batch's labels and targets against the lead's (plan 2, Section 5.1)
        pairing = {"attack": {b: bool(lead_prep_fp["attack"].get(b) == fp) for b, fp in zip(attack, A_["prep_fp"])},
                   "heldout": {b: bool(lead_prep_fp["heldout"].get(b) == fp) for b, fp in zip(heldout, H_["prep_fp"])}}
    table["meta"] = {"kind": "real", "arm": arm, "complete": True, "run_commit": sorted(commits)[0], "run_tree_clean": True,
                     "design": {"K_A": KA, "K_H": KH, "n_s": ns, "Q": Q, "n_shuffles": R, "n_texts": T, "n_record": int(A_["rec"].shape[-1])},
                     "sha256": dict(inputs_sha256), "containers": containers, "per_text_files": [], "prep_fp_equal_to_lead": pairing,
                     "rehearsal": bool(rehearsal)}
    table["meta"]["n_scoring_passes"] = LT.expected_scoring_passes(table)
    failed = LT.failed_checks(table)
    outcomes["table_checks_failed"] = failed
    if failed and not rehearsal:
        raise GuardFailure(failed[0], name)
    files = LT.save_table(table, out_dir) if part_bytes is None else LT.save_table(table, out_dir, part_bytes=part_bytes)
    return {"arm": arm, "files": files, "design": table["meta"]["design"], "complete": True, "run_commit": table["meta"]["run_commit"],
            "outcomes": outcomes, "prep_fp_equal_to_lead": pairing,
            "prep_fp": {"attack": dict(zip(attack, A_["prep_fp"])), "heldout": dict(zip(heldout, H_["prep_fp"]))}}


def assemble_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """The assembler as the cloud's CPU function runs it, from a spec (`lead_launch.assemble_plan`). For a rehearsal's
    one-batch arm it also compares the two roles' searches with each other and, where the pilot ran the same search,
    with the pilot's stored record and saved settings' hashes, each as true or false."""
    table_dir = Path(spec["root"]) / "sealed" / spec["table"]
    units = Path(spec["units"])
    heldout_units = Path(spec["heldout_units"]) if spec.get("heldout_units") else None
    out = assemble(units, table_dir, spec["arm"], spec["attack"], spec["heldout"], spec["starts"], text_ids_H=spec["text_ids_H"], excluded=spec["excluded"],
                   inputs_sha256=spec["inputs_sha256"], containers=spec["containers"], expect_commit=spec["commit"], lead_prep_fp=spec.get("lead_prep_fp"),
                   rehearsal=bool(spec.get("rehearsal", False)), heldout_units=heldout_units, part_bytes=spec.get("part_bytes"),
                   returned_sha256=spec.get("returned_sha256"))
    if spec.get("rehearsal"):  # one batch on both sides: its two roles' searches of the same start
        a = search_file(units, spec["attack"][0], spec["starts"][0])
        h = search_file(heldout_units or units, spec["heldout"][0], spec["starts"][0])
        out["outcomes"]["containers_agree"] = compare_search_units(a, h)
        if spec.get("pilot"):
            out["outcomes"]["attack_role_equals_pilot"] = compare_with_pilot(a, spec["pilot"])
            out["outcomes"]["heldout_role_equals_pilot"] = compare_with_pilot(h, spec["pilot"])
    out["table_dir"] = str(table_dir)
    return out


def guards_from_spec(spec: dict[str, Any]) -> dict[str, bool]:
    """The guards-only pass as the cloud's CPU function runs it, from a spec (`lead_launch.guards_plan`)."""
    return cross_unit_guards(Path(spec["units"]), spec["arm"], spec["attack"], spec["heldout"], spec["starts"], expect_commit=spec["commit"],
                             rehearsal=bool(spec.get("rehearsal", False)), heldout_units=Path(spec["heldout_units"]) if spec.get("heldout_units") else None)
