"""Plan 1 of the research log, Section 5.1: the results table of the lead experiment.

The format is `freeze/amendment1_specs/table_and_run_spec.md`, Section 3 ("the table specification"), with one array added
by Amendment 1, Section 9, item 5 (`shuf_absmean_alive`) and the per-text file written as a list of parts (plan 1 of the research log,
Section 12.1, item 1). The real run and the made-up-data generator both write it, and the analysis reads nothing else.

A table is a dictionary of named arrays plus one metadata dictionary under the key "meta", in memory and on disk alike.
Every harm in it is raw, in nats per token. It holds no added harm, no ratio, and no mean over cells.

  - `validate(table)` runs every completeness check and raises `TableCheckError`, whose message is the name of the
    check and holds no number.
  - `row_arrays(table, row)` returns the arrays one row of the printed tables needs, in the names of the output
    specification's Section 2.1. It reads the re-scored arrays (`own_*`, `init_*`), not the search record; the record
    serves only what belongs to a search as a whole (level crossings, cycling, long-search levels).
  - `without_excluded(table)` returns the table recomputed without the overlapping held-out texts.
  - `save_table` and `load_table` write and read the files; `read_meta` reads the metadata alone, without any harm.

Indices: i attack batch, j held-out batch, s start, q scored setting, r shuffled copy, t text, k step.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

SETTINGS_LEAD = ("n20", "n40", "n80", "n160", "n320", "n159", "n319", "h2", "h5", "h10")
SETTINGS_DELTA_ON = ("n20", "n40", "n80", "n160", "n320")
STEP_ROWS = ("n20", "n40", "n80", "n160", "n320")
LEVEL_ROWS = ("h2", "h5", "h10")
STEP_BEFORE = {"n160": "n159", "n320": "n319"}
NO_SHUFFLES = ("n159", "n319")
FIXED_STEPS = {"n20": 20, "n40": 40, "n80": 80, "n160": 160, "n320": 320, "n159": 159, "n319": 319}
LEVELS = {"h2": 2.0, "h5": 5.0, "h10": 10.0}
N_SHUFFLES = 8
N_TEXTS = 128
N_RECORD = 321
PER_TEXT_RELATIVE_TOLERANCE = 1e-5  # the table specification's guard G5
CYCLING_SHARE = 0.10  # signed, Section 3: steps n and n - 1 differ by more than 10 percent of the larger
CORE_FILE = "table_core.npz"
PER_TEXT_FILE = "table_per_text_{:02d}.npz"
PER_TEXT_PART_BYTES = 40_000_000  # no committed file may exceed 45 MB (plan 2 of the research log, Section 5.2)

DESIGN_KEYS = ("K_A", "K_H", "n_s", "Q", "n_shuffles", "n_texts", "n_record")
PER_TEXT_ARRAYS = ("carried_text", "shuf_text", "own_A_text", "own_H_text", "init_A_text", "init_H_text")
PER_TEXT_WITH_ATTACK_AXIS = ("carried_text", "shuf_text", "own_A_text", "init_A_text")


class TableCheckError(Exception):
    """A completeness check failed. The message is the check's name and holds no number."""

    def __init__(self, check: str) -> None:
        assert not any(c.isdigit() for c in check), "a check's name holds no digit"
        self.check = check
        super().__init__(check)


STRUCTURAL_CHECKS = ("metadata", "arrays_present_with_declared_shapes")  # nothing after them can be evaluated
# Every check `validate` makes, in the order it first makes it, and the two `load_table` makes of the per-text parts:
# for a command that prints each name with pass or fail (plan 4 of the research log, Section 6, row 7).
CHECKS = ("metadata", "complete_flag", "arrays_present_with_declared_shapes", "axis_labels", "no_other_nan_or_infinite", "fixed_steps",
          "missing_steps_only_at_levels", "level_steps_equal_crossing_rule", "nan_exactly_where_setting_missing", "setting_hashes_present",
          "shuffle_hashes_present", "shuffle_descriptions", "scoring_pass_count", "block_ids_match_heldout_ids", "heldout_ids_differ_from_attack_ids",
          "own_equals_record_at_step", "init_equals_record_start", "per_text_matches_core", "carried_differs_from_own_batch_values")
LOADER_CHECKS = ("per_text_parts_in_attack_order", "per_text_files_match_core_metadata")
_collecting: list[str] | None = None


def _fail(check: str) -> None:
    if _collecting is None or check in STRUCTURAL_CHECKS:
        raise TableCheckError(check)
    if check not in _collecting:
        _collecting.append(check)


def failed_checks(table: dict[str, Any]) -> list[str]:
    """Every check of `validate` that fails on this table, in order, not only the first. For the rehearsal, whose
    table must be refused on purpose (plan 2 of the research log, Section 7), and for nothing that decides a reading."""
    global _collecting
    _collecting = []
    try:
        validate(table)
        return list(_collecting)
    except TableCheckError as e:
        return list(_collecting) + [e.check]
    finally:
        _collecting = None


# ----------------------------------------------------------------------------- shapes


def core_shapes(design: dict[str, int]) -> dict[str, tuple[tuple[int, ...], str]]:
    """Every array of the core file: its shape and its kind ("f" float64, "i" integer, "U" text, "b" bool)."""
    KA, KH, ns, Q, R, T, N = (design[k] for k in DESIGN_KEYS)
    return {
        "rec_A": ((KA, ns, N), "f"), "rec_H": ((KH, ns, N), "f"),
        "step_A": ((KA, ns, Q), "i"), "step_H": ((KH, ns, Q), "i"),
        "own_A": ((KA, ns, Q), "f"), "own_H": ((KH, ns, Q), "f"),
        "init_A": ((KA, ns), "f"), "init_H": ((KH, ns), "f"),
        "setting_sha_A": ((KA, ns, Q), "U"), "setting_sha_H": ((KH, ns, Q), "U"),
        "prep_fp_A": ((KA,), "U"), "prep_fp_H": ((KH,), "U"),
        "ids_sha_A": ((KA,), "U"), "ids_sha_H": ((KH,), "U"),
        "carried": ((KA, KH, ns, Q), "f"),
        "shuf": ((KA, KH, ns, Q, R), "f"),
        "block_ids_sha": ((KA, KH, ns), "U"),
        "shuf_sha": ((KA, ns, Q, R), "U"),
        "shuf_moved": ((KA, ns, Q, R), "f"),
        "shuf_moved_alive": ((KA, ns, Q, R), "f"),
        "shuf_absmean_alive": ((KA, ns, Q, R), "f"),
        "attack_names": ((KA,), "U"), "heldout_names": ((KH,), "U"),
        "starts": ((ns,), "i"), "setting_names": ((Q,), "U"), "has_shuffles": ((Q,), "b"),
        "excluded_H": ((KH, T), "b"), "text_ids_H": ((KH, T), "U"),
    }


def per_text_shapes(design: dict[str, int]) -> dict[str, tuple[int, ...]]:
    """Every array of the per-text file (float32)."""
    KA, KH, ns, Q, R, T, _ = (design[k] for k in DESIGN_KEYS)
    return {
        "carried_text": (KA, KH, ns, Q, T),
        "shuf_text": (KA, KH, ns, Q, R, T),
        "own_A_text": (KA, ns, Q, T), "own_H_text": (KH, ns, Q, T),
        "init_A_text": (KA, ns, T), "init_H_text": (KH, ns, T),
    }


def has_per_text(table: dict[str, Any]) -> bool:
    return all(name in table for name in PER_TEXT_ARRAYS)


def is_recomputed(table: dict[str, Any]) -> bool:
    return bool(table["meta"].get("recomputed_without_excluded", False))


def crossing_steps(rec: np.ndarray, level: float) -> np.ndarray:
    """For every search of `rec` [K, n_s, steps]: the level-crossing step by the signed two-step-mean rule, as the
    existing `pilot.crossing` computes it, or -1 where it reports the level missing."""
    from vpd_audit_2 import pilot as P

    K, ns, _ = rec.shape
    out = np.full((K, ns), -1, dtype=np.int64)
    for b in range(K):
        for s in range(ns):
            c = P.crossing(rec[b, s].tolist(), level)
            if not c["missing"]:
                out[b, s] = int(c["k"])
    return out


def expected_scoring_passes(table: dict[str, Any]) -> int:
    """The table specification's Section 3.6: one unshuffled pass, and 8 shuffled passes where a setting has shuffled copies, for every
    setting an attack search has, on every held-out batch."""
    present = np.asarray(table["step_A"]) != -1  # [K_A, n_s, Q]
    per_setting = 1 + N_SHUFFLES * np.asarray(table["has_shuffles"], dtype=np.int64)  # [Q]
    return int(table["meta"]["design"]["K_H"]) * int((present * per_setting[None, None, :]).sum())


def _bits_equal(x: np.ndarray, y: np.ndarray) -> bool:
    return np.array_equal(np.ascontiguousarray(x, dtype=np.float64).view(np.uint64), np.ascontiguousarray(y, dtype=np.float64).view(np.uint64))


# ----------------------------------------------------------------------------- validate


def validate(table: dict[str, Any]) -> None:
    """Every completeness check of the table specification's Section 3.6, the three rules of 3.5, the checks of the steps themselves
    (plan 1 of the research log, Section 5.1), and the per-text arrays against their core values (plan 1 of the research log, Section 12.1, item 1).

    For the table recomputed without the overlapping texts, the equality of `own_H` and of `init_H` with the record is
    skipped, since both are recomputed; everything else runs."""
    meta = table.get("meta")
    if not isinstance(meta, dict) or meta.get("kind") not in ("real", "made_up") or not isinstance(meta.get("arm"), str):
        _fail("metadata")
    design = meta.get("design")
    if not isinstance(design, dict) or any(not isinstance(design.get(k), int) or design[k] < 1 for k in DESIGN_KEYS):
        _fail("metadata")
    if design["n_shuffles"] != N_SHUFFLES or not isinstance(meta.get("n_scoring_passes"), int):
        _fail("metadata")
    if meta.get("complete") is not True:
        _fail("complete_flag")

    # every array is present with exactly the declared shape
    for name, (shape, kind) in core_shapes(design).items():
        arr = table.get(name)
        if not isinstance(arr, np.ndarray) or arr.shape != shape:
            _fail("arrays_present_with_declared_shapes")
        ok = {"f": arr.dtype == np.float64, "i": arr.dtype.kind == "i", "U": arr.dtype.kind == "U", "b": arr.dtype == np.bool_}[kind]
        if not ok:
            _fail("arrays_present_with_declared_shapes")
    some_per_text = any(name in table for name in PER_TEXT_ARRAYS)
    if some_per_text and not has_per_text(table):
        _fail("arrays_present_with_declared_shapes")
    if not some_per_text and meta["kind"] == "real":
        _fail("arrays_present_with_declared_shapes")
    if some_per_text:
        for name, shape in per_text_shapes(design).items():
            arr = table[name]
            if not isinstance(arr, np.ndarray) or arr.shape != shape or arr.dtype != np.float32:
                _fail("arrays_present_with_declared_shapes")

    names = tuple(str(x) for x in table["setting_names"])
    if names not in (SETTINGS_LEAD, SETTINGS_DELTA_ON):
        _fail("axis_labels")
    if [bool(x) for x in table["has_shuffles"]] != [n not in NO_SHUFFLES for n in names]:
        _fail("axis_labels")
    # rule 3 of Section 3.5, for the arrays that have no missing entries: nothing is NaN or infinite
    finite_everywhere = [table["rec_A"], table["rec_H"], table["init_A"], table["init_H"]]
    if some_per_text:
        finite_everywhere += [table["init_A_text"], table["init_H_text"]]
    if any(not np.isfinite(arr).all() for arr in finite_everywhere):
        _fail("no_other_nan_or_infinite")
    for key in ("attack_names", "heldout_names", "starts"):
        vals = table[key].tolist()
        if len(set(vals)) != len(vals):
            _fail("axis_labels")
    if set(table["attack_names"].tolist()) & set(table["heldout_names"].tolist()):
        _fail("axis_labels")

    present = {"A": table["step_A"] != -1, "H": table["step_H"] != -1}  # [K, n_s, Q]
    level_q = np.array([n in LEVELS for n in names])
    for side in ("A", "H"):
        step, rec = table[f"step_{side}"], table[f"rec_{side}"]
        # the steps themselves
        for q, n in enumerate(names):
            if n in FIXED_STEPS and not (step[:, :, q] == FIXED_STEPS[n]).all():
                _fail("fixed_steps")
        # rule 1 of Section 3.5: a step is missing only at a level setting
        if (~present[side])[:, :, ~level_q].any() or ((step < 1) & present[side]).any() or (step >= design["n_record"]).any():
            _fail("missing_steps_only_at_levels")
        for q, n in enumerate(names):
            if n in LEVELS and not np.array_equal(step[:, :, q], crossing_steps(rec, LEVELS[n])):
                _fail("level_steps_equal_crossing_rule")

    # rule 2: a harm is NaN exactly where its setting is missing
    shuffled_q = np.asarray(table["has_shuffles"], dtype=bool)
    carried_present = np.broadcast_to(present["A"][:, None, :, :], table["carried"].shape)
    shuf_present = np.broadcast_to((present["A"] & shuffled_q[None, None, :])[:, None, :, :, None], table["shuf"].shape)
    nan_rules = [(table["own_A"], present["A"]), (table["own_H"], present["H"]), (table["carried"], carried_present), (table["shuf"], shuf_present)]
    if some_per_text:
        nan_rules += [
            (table["own_A_text"], np.broadcast_to(present["A"][..., None], table["own_A_text"].shape)),
            (table["own_H_text"], np.broadcast_to(present["H"][..., None], table["own_H_text"].shape)),
            (table["carried_text"], np.broadcast_to(carried_present[..., None], table["carried_text"].shape)),
            (table["shuf_text"], np.broadcast_to(shuf_present[..., None], table["shuf_text"].shape)),
        ]
    for arr, there in nan_rules:
        if not np.array_equal(np.isnan(arr), ~there):
            _fail("nan_exactly_where_setting_missing")
    # rule 3: no other entry of any harm array is NaN or infinite
    if any(np.isinf(arr).any() for arr, _ in nan_rules):
        _fail("no_other_nan_or_infinite")

    for side in ("A", "H"):
        if not np.array_equal(table[f"setting_sha_{side}"] != "", present[side]):
            _fail("setting_hashes_present")
    shuffles_there = present["A"] & shuffled_q[None, None, :]  # [K_A, n_s, Q]
    if (table["shuf_sha"][shuffles_there] == "").any():
        _fail("shuffle_hashes_present")
    for name in ("shuf_moved", "shuf_moved_alive", "shuf_absmean_alive"):
        arr = table[name]
        if not np.array_equal(np.isnan(arr), np.broadcast_to(~shuffles_there[..., None], arr.shape)) or np.isinf(arr).any():
            _fail("shuffle_descriptions")

    if meta["n_scoring_passes"] != expected_scoring_passes(table):
        _fail("scoring_pass_count")
    if not (table["block_ids_sha"] == table["ids_sha_H"][None, :, None]).all():
        _fail("block_ids_match_heldout_ids")
    if set(table["ids_sha_H"].tolist()) & set(table["ids_sha_A"].tolist()):
        _fail("heldout_ids_differ_from_attack_ids")

    # guard G4: the scoring path reproduces the search, bit for bit
    for side in ("A", "H"):
        if side == "H" and is_recomputed(table):
            continue
        step, rec, own = table[f"step_{side}"], table[f"rec_{side}"], table[f"own_{side}"]
        at_step = np.take_along_axis(rec, np.clip(np.where(present[side], step, 0), 0, design["n_record"] - 1).astype(np.int64), axis=2)
        if not _bits_equal(own[present[side]], at_step[present[side]]):
            _fail("own_equals_record_at_step")
        if not _bits_equal(table[f"init_{side}"], rec[:, :, 0]):
            _fail("init_equals_record_start")

    if some_per_text:
        _check_per_text(table)
        if not is_recomputed(table):
            _check_carried_is_neither_own(table, present["A"], present["H"])


def _check_carried_is_neither_own(table: dict[str, Any], present_A: np.ndarray, present_H: np.ndarray) -> None:
    """Guards G6 and G11 of the run, repeated by the program that reads the table (plan 4 of the research log, Section 4.4).

    For every carried cell that exists, its per-text harms are not all equal to the same setting's on its attack
    batch (a setting scored on the batch it was found on), and not all equal to the held-out batch's own setting's for
    the same start and setting, where that exists (a held-out batch scored with its own setting). Either error gives
    the predicted carry-over ratio with no carry-over in it. Skipped by the caller for the copy recomputed without the
    overlapping texts, whose per-text arrays are this table's."""
    carried = table["carried_text"]  # [K_A, K_H, n_s, Q, T]
    exists = np.broadcast_to(present_A[:, None, :, :], carried.shape[:-1])
    same_as_attack = (carried == table["own_A_text"][:, None]).all(axis=-1)
    same_as_heldout = (carried == table["own_H_text"][None]).all(axis=-1) & present_H[None]
    if (exists & (same_as_attack | same_as_heldout)).any():
        _fail("carried_differs_from_own_batch_values")


def _kept_mean(per_text: np.ndarray, keep: np.ndarray | None, batch_axis: int | None) -> np.ndarray:
    """The float64 mean of float32 per-text harms over the kept texts of each held-out batch (all texts if `keep` is
    None). `batch_axis` is the axis of the held-out batch in `per_text`."""
    x = per_text.astype(np.float64)
    if keep is None:
        return x.sum(axis=-1) / x.shape[-1]
    shape = [1] * x.ndim
    shape[batch_axis] = keep.shape[0]
    shape[-1] = keep.shape[1]
    k = keep.reshape(shape)
    n = k.sum(axis=-1)
    return np.where(k, x, 0.0).sum(axis=-1) / n


def _check_per_text(table: dict[str, Any]) -> None:
    """Each per-text array against its core value: the same NaN pattern (checked by the caller's rule 2) and a mean over
    the texts within 1e-5 relative. In the table recomputed without the overlapping texts, the held-out side's mean
    runs over the kept texts."""
    keep = ~table["excluded_H"] if is_recomputed(table) else None
    pairs = [
        ("carried_text", "carried", 1, True), ("shuf_text", "shuf", 1, True),
        ("own_H_text", "own_H", 0, True), ("init_H_text", "init_H", 0, True),
        ("own_A_text", "own_A", None, False), ("init_A_text", "init_A", None, False),
    ]
    for text_name, core_name, batch_axis, heldout in pairs:
        mean = _kept_mean(table[text_name], keep if heldout else None, batch_axis)
        core = table[core_name]
        there = ~np.isnan(core)
        if not (np.abs(mean[there] - core[there]) <= PER_TEXT_RELATIVE_TOLERANCE * np.abs(core[there])).all():
            _fail("per_text_matches_core")


# ----------------------------------------------------------------------------- the rows


def row_kind(row: str) -> tuple[str, int | float]:
    """("step", n) for a search-length setting, ("level", h) for a harm level."""
    if row in FIXED_STEPS:
        return "step", FIXED_STEPS[row]
    return "level", LEVELS[row]


def row_arrays(table: dict[str, Any], row: str) -> dict[str, Any]:
    """The arrays of the output specification's Section 2.1 for one scored setting, with presence masks."""
    names = [str(x) for x in table["setting_names"]]
    q = names.index(row)
    q20 = names.index("n20")
    kind, key = row_kind(row)
    a_present = table["step_A"][:, :, q] != -1
    b_present = table["step_H"][:, :, q] != -1
    has_shuffles = bool(table["has_shuffles"][q])
    out: dict[str, Any] = {
        "table": kind, "key": key, "setting": row,
        "attack_names": [str(x) for x in table["attack_names"]],
        "heldout_names": [str(x) for x in table["heldout_names"]],
        "starts": [int(x) for x in table["starts"]],
        "start": table["init_H"],
        "own": table["own_H"][:, :, q],
        "own20": table["own_H"][:, :, q20],
        "carried": table["carried"][:, :, :, q],
        "shuffled": table["shuf"][:, :, :, q, :] if has_shuffles else None,
        "attack_start": table["init_A"],
        "attack_own": table["own_A"][:, :, q],
        "attack_present": a_present,
        "heldout_present": b_present,
        "attack_missing": ~a_present,
        "heldout_missing": ~b_present,
        "moved_share": table["shuf_moved_alive"][:, :, q, :].mean(axis=-1) if has_shuffles else None,
        "mean_abs_change": table["shuf_absmean_alive"][:, :, q, :].mean(axis=-1) if has_shuffles else None,
    }
    if kind == "step":
        n = int(key)
        for side, rec in (("attack", table["rec_A"]), ("heldout", table["rec_H"])):
            past = {}
            for level in (2.0, 5.0, 10.0):
                k = crossing_steps(rec, level)
                past[level] = (k != -1) & (k <= n)
            out[f"{side}_past"] = past
            hi = np.maximum(rec[:, :, n], rec[:, :, n - 1])
            out[f"{side}_cycling"] = np.abs(rec[:, :, n] - rec[:, :, n - 1]) > CYCLING_SHARE * hi
    return out


def batch_means_added_harm(table: dict[str, Any]) -> dict[str, dict[str, list[float]]]:
    """Per side, each batch's mean own-search added harm at 20 and at 40 steps, sorted (Amendment 1, fault 3.7)."""
    names = [str(x) for x in table["setting_names"]]
    out: dict[str, dict[str, list[float]]] = {}
    for side, label in (("A", "attack"), ("H", "heldout")):
        out[label] = {}
        for row in ("n20", "n40"):
            added = table[f"own_{side}"][:, :, names.index(row)] - table[f"init_{side}"]
            out[label][row] = sorted(float(x) for x in added.mean(axis=1))
    return out


def long_search_levels(table: dict[str, Any]) -> dict[str, Any]:
    """Signed Section 8: long-search levels as a distribution. Over all searches of the table, the mean harm over
    steps 301 to 320, and the share of searches at or above the paper's 40.2 after step 320."""
    rec = np.concatenate([table["rec_A"].reshape(-1, table["rec_A"].shape[-1]), table["rec_H"].reshape(-1, table["rec_H"].shape[-1])])
    plateau = rec[:, 301:321].mean(axis=1)
    q = np.percentile(plateau, [0, 25, 50, 75, 100])
    return {
        "searches": int(rec.shape[0]),
        "plateau_definition": "mean harm over steps 301 to 320, raw nats",
        "min": float(q[0]), "lower_quartile": float(q[1]), "median": float(q[2]), "upper_quartile": float(q[3]), "max": float(q[4]),
        "paper_level": 40.2,
        "share_at_or_above_paper_level_after_step_320": float((rec[:, 320] >= 40.2).mean()),
    }


# ----------------------------------------------------------------------------- without the overlapping texts


def without_excluded(table: dict[str, Any]) -> dict[str, Any]:
    """The table recomputed without the overlapping held-out texts (the table specification's Section 11.2): every harm scored on a
    held-out batch (`carried`, `shuf`, `own_H`, `init_H`) becomes the mean of its per-text harms over the texts not
    excluded. No search is rerun: the records and the level-crossing steps stay as they were."""
    if not has_per_text(table):
        _fail("per_text_arrays_needed")
    keep = ~np.asarray(table["excluded_H"], dtype=bool)
    if (keep.sum(axis=1) == 0).any():
        _fail("excluded_texts")
    out = dict(table)
    out["carried"] = _kept_mean(table["carried_text"], keep, 1)
    out["shuf"] = _kept_mean(table["shuf_text"], keep, 1)
    out["own_H"] = _kept_mean(table["own_H_text"], keep, 0)
    out["init_H"] = _kept_mean(table["init_H_text"], keep, 0)
    out["meta"] = {**table["meta"], "recomputed_without_excluded": True, "n_excluded_texts": int((~keep).sum())}
    return out


# ----------------------------------------------------------------------------- shuffles, described


def shuffle_displacement(setting: np.ndarray, shuffled: np.ndarray, lay: list[tuple[str, int]], strata: dict[str, np.ndarray],
                         dead_stratum: int = 10) -> dict[str, float]:
    """How far a shuffled copy is from its setting (both flattened, C_l + 1 entries per module, the delta entry last):
    `moved`, the share of rank-one entries changed by more than 0.5; `moved_alive`, the same among the entries that are
    not dead; and `absmean_alive`, the mean absolute change over those."""
    diffs, alive = [], []
    off = 0
    for name, C in lay:
        diffs.append(np.abs(shuffled[off : off + C].astype(np.float64) - setting[off : off + C].astype(np.float64)))
        alive.append(np.asarray(strata[name]) != dead_stratum)
        off += C + 1
    assert off == setting.size == shuffled.size
    d = np.concatenate(diffs)
    a = np.concatenate(alive)
    return {"moved": float((d > 0.5).mean()), "moved_alive": float((d[a] > 0.5).mean()), "absmean_alive": float(d[a].mean())}


# ----------------------------------------------------------------------------- files


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def is_real(meta: dict[str, Any], paths: list[Path]) -> bool:
    """A table is real if its metadata says so, or if any of its files lies under a folder named `sealed`, whatever
    its metadata says."""
    if meta.get("kind") != "made_up":
        return True
    for p in paths:
        for q in (Path(p), Path(p).resolve()):
            if "sealed" in q.parent.parts:
                return True
    return False


def _meta_of(z: Any) -> dict[str, Any]:
    """The metadata entry of an open core file: one JSON string (the archive stores it as an array of one entry)."""
    return json.loads(str(np.asarray(z["meta"]).reshape(-1)[0]))


def read_meta(core_path: Path) -> dict[str, Any]:
    """The metadata of a core file. Reads no harm: an .npz archive is read entry by entry."""
    with np.load(core_path, allow_pickle=False) as z:
        return _meta_of(z)


def table_files(folder: Path) -> list[Path]:
    """The core file and the per-text parts its metadata lists, in order."""
    core = Path(folder) / CORE_FILE
    meta = read_meta(core)
    return [core] + [Path(folder) / part["name"] for part in meta.get("per_text_files", [])]


def save_table(table: dict[str, Any], folder: Path, part_bytes: int = PER_TEXT_PART_BYTES) -> list[dict[str, str]]:
    """Write the table under `folder`, deterministically: the per-text parts first, split along the attack axis so that
    no part exceeds `part_bytes`, then the core file, whose metadata records each part's name, hash, and attack names.
    The arrays with no attack axis go in the first part with its attack batches; where they and one attack batch's
    arrays do not fit in one part together, they go in a part of their own, which holds no attack batch (plan 2 of the research log,
    Section 5.2; plan 4 of the research log, Section 6.1). Returns each file's name and SHA-256, the core file first."""
    from vpd_audit_2.manifest import deterministic_npz

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    meta = dict(table["meta"])
    design = meta["design"]
    attack_names = [str(x) for x in table["attack_names"]]
    parts: list[dict[str, Any]] = []
    if has_per_text(table):
        K_A = design["K_A"]
        per_batch = sum(int(table[n].nbytes) for n in PER_TEXT_WITH_ATTACK_AXIS) / K_A
        no_attack_axis = int(table["own_H_text"].nbytes) + int(table["init_H_text"].nbytes)
        alone = no_attack_axis + per_batch > part_bytes  # the arrays with no attack axis in a part of their own
        per_part = max(1, int((part_bytes - (0 if alone else no_attack_axis)) // per_batch))  # attack batches per part
        bounds = list(range(0, K_A, per_part)) + [K_A]
        slices: list[tuple[int, int] | None] = ([None] if alone else []) + [(bounds[p], bounds[p + 1]) for p in range(len(bounds) - 1)]
        for p, held in enumerate(slices):
            i0, i1 = held if held is not None else (0, 0)
            arrays = {n: table[n][i0:i1] for n in PER_TEXT_WITH_ATTACK_AXIS} if held is not None else {}
            if p == 0:  # the arrays with no attack axis go in the first part
                arrays["own_H_text"] = table["own_H_text"]
                arrays["init_H_text"] = table["init_H_text"]
            arrays["part_attack_names"] = np.array(attack_names[i0:i1]) if held is not None else np.array([], dtype="<U1")
            name = PER_TEXT_FILE.format(p + 1)
            data = deterministic_npz(arrays)
            (folder / name).write_bytes(data)
            parts.append({"name": name, "sha256": hashlib.sha256(data).hexdigest(), "attack_names": attack_names[i0:i1]})
    meta["per_text_files"] = parts
    core = {n: table[n] for n in core_shapes(design)}
    core["meta"] = np.array(json.dumps(meta, sort_keys=True))
    data = deterministic_npz(core)
    (folder / CORE_FILE).write_bytes(data)
    return [{"name": CORE_FILE, "sha256": hashlib.sha256(data).hexdigest()}] + [{"name": p["name"], "sha256": p["sha256"]} for p in parts]


def load_table(folder: Path) -> dict[str, Any]:
    """Read a table from `folder`. Each per-text part must have the hash the core file's metadata records, and the
    parts' attack batches, joined in order, must be the core file's `attack_names`."""
    folder = Path(folder)
    with np.load(folder / CORE_FILE, allow_pickle=False) as z:
        table: dict[str, Any] = {k: z[k] for k in z.files if k != "meta"}
        table["meta"] = _meta_of(z)
    parts = table["meta"].get("per_text_files", [])
    if parts:
        joined: dict[str, list[np.ndarray]] = {n: [] for n in PER_TEXT_WITH_ATTACK_AXIS}
        # the parts' attack batches, joined in the metadata's order, must be the core file's `attack_names`
        listed = [str(n) for part in parts for n in part["attack_names"]]
        if listed != [str(x) for x in table["attack_names"]]:
            _fail("per_text_parts_in_attack_order")
        for part in parts:
            path = folder / part["name"]
            if not path.is_file() or sha256_file(path) != part["sha256"]:
                _fail("per_text_files_match_core_metadata")
            with np.load(path, allow_pickle=False) as z:
                if [str(x) for x in z["part_attack_names"]] != list(part["attack_names"]):
                    _fail("per_text_parts_in_attack_order")
                if part["attack_names"]:  # a part may hold the arrays with no attack axis alone
                    for n in PER_TEXT_WITH_ATTACK_AXIS:
                        joined[n].append(z[n])
                if "own_H_text" in z.files:  # the arrays with no attack axis, in the part that holds them
                    table["own_H_text"] = z["own_H_text"]
                    table["init_H_text"] = z["init_H_text"]
        if "own_H_text" not in table or "init_H_text" not in table:
            _fail("arrays_present_with_declared_shapes")
        for n in PER_TEXT_WITH_ATTACK_AXIS:
            table[n] = np.concatenate(joined[n], axis=0)
    return table


# ----------------------------------------------------------------------------- made-up tables


def _fake_sha(*parts: Any) -> str:
    return hashlib.sha256(repr(parts).encode()).hexdigest()


def made_up_table(rec_A: np.ndarray, rec_H: np.ndarray, carried: np.ndarray, shuf: np.ndarray, *, arm: str = "lead",
                  setting_names: tuple[str, ...] = SETTINGS_LEAD, starts: tuple[int, ...] | None = None,
                  per_text: bool | dict[str, np.ndarray] = False, excluded_H: np.ndarray | None = None,
                  moved_alive: float = 0.4, absmean_alive: float = 0.4, scenario: str = "", seed: int = 0) -> dict[str, Any]:
    """A complete made-up table (`meta["kind"] = "made_up"`) from own-batch records and invented cross-batch harms.

    `rec_A` [K_A, n_s, 321] and `rec_H` [K_H, n_s, 321] are the searches' own harm records; the steps of the scored
    settings, the own-batch harms, and the starting harms are read from them, as the real run's guards require.
    `carried` [K_A, K_H, n_s, Q] and `shuf` [K_A, K_H, n_s, Q, 8] give the cross-batch harms; entries at settings that
    do not exist, or that have no shuffled copies, are ignored and stored as NaN.
    `per_text=True` gives every text its batch's value; a dictionary supplies the six per-text arrays as they are."""
    rec_A = np.asarray(rec_A, dtype=np.float64)
    rec_H = np.asarray(rec_H, dtype=np.float64)
    K_A, n_s, n_record = rec_A.shape
    K_H = rec_H.shape[0]
    Q = len(setting_names)
    design = {"K_A": K_A, "K_H": K_H, "n_s": n_s, "Q": Q, "n_shuffles": N_SHUFFLES, "n_texts": N_TEXTS, "n_record": n_record}
    has_shuffles = np.array([n not in NO_SHUFFLES for n in setting_names])
    attack_names = np.array([f"A{i + 1}" for i in range(K_A)])
    heldout_names = np.array([f"H{j + 1}" for j in range(K_H)])
    t: dict[str, Any] = {"rec_A": rec_A, "rec_H": rec_H, "attack_names": attack_names, "heldout_names": heldout_names,
                         "starts": np.array(starts if starts is not None else tuple(range(9, 9 + n_s)), dtype=np.int64),
                         "setting_names": np.array(setting_names), "has_shuffles": has_shuffles}
    for side, rec in (("A", rec_A), ("H", rec_H)):
        K = rec.shape[0]
        step = np.zeros((K, n_s, Q), dtype=np.int32)
        for q, n in enumerate(setting_names):
            step[:, :, q] = FIXED_STEPS[n] if n in FIXED_STEPS else crossing_steps(rec, LEVELS[n])
        there = step != -1
        own = np.take_along_axis(rec, np.where(there, step, 0).astype(np.int64), axis=2)
        t[f"step_{side}"] = step
        t[f"own_{side}"] = np.where(there, own, np.nan)
        t[f"init_{side}"] = rec[:, :, 0].copy()
        sha = np.array([[[_fake_sha("setting", arm, side, b, s, n) if there[b, s, q] else "" for q, n in enumerate(setting_names)]
                         for s in range(n_s)] for b in range(K)])
        t[f"setting_sha_{side}"] = sha
        t[f"prep_fp_{side}"] = np.array([_fake_sha("prep", side, b) for b in range(K)])
        t[f"ids_sha_{side}"] = np.array([_fake_sha("ids", side, b) for b in range(K)])
    a_there = t["step_A"] != -1  # [K_A, n_s, Q]
    t["carried"] = np.where(a_there[:, None, :, :], np.asarray(carried, dtype=np.float64), np.nan)
    shuf_there = (a_there & has_shuffles[None, None, :])[:, None, :, :, None]
    t["shuf"] = np.where(shuf_there, np.asarray(shuf, dtype=np.float64), np.nan)
    t["block_ids_sha"] = np.broadcast_to(t["ids_sha_H"][None, :, None], (K_A, K_H, n_s)).copy()
    desc_there = (a_there & has_shuffles[None, None, :])[..., None] & np.ones(N_SHUFFLES, dtype=bool)
    t["shuf_sha"] = np.array([[[[_fake_sha("shuffle", arm, i, s, n, r) if desc_there[i, s, q, r] else "" for r in range(N_SHUFFLES)]
                                for q, n in enumerate(setting_names)] for s in range(n_s)] for i in range(K_A)])
    t["shuf_moved"] = np.where(desc_there, 0.25 * moved_alive, np.nan)
    t["shuf_moved_alive"] = np.where(desc_there, moved_alive, np.nan)
    t["shuf_absmean_alive"] = np.where(desc_there, absmean_alive, np.nan)
    t["excluded_H"] = np.zeros((K_H, N_TEXTS), dtype=bool) if excluded_H is None else np.asarray(excluded_H, dtype=bool)
    t["text_ids_H"] = np.array([[f"m{j}_{k}" for k in range(N_TEXTS)] for j in range(K_H)])
    if isinstance(per_text, dict):
        for name in PER_TEXT_ARRAYS:
            t[name] = np.asarray(per_text[name], dtype=np.float32)
    elif per_text:
        for name, core in (("carried_text", "carried"), ("shuf_text", "shuf"), ("own_A_text", "own_A"), ("own_H_text", "own_H"),
                           ("init_A_text", "init_A"), ("init_H_text", "init_H")):
            t[name] = np.repeat(t[core][..., None], N_TEXTS, axis=-1).astype(np.float32)
    t["meta"] = {"kind": "made_up", "arm": arm, "design": design, "complete": True, "scenario": scenario, "seed": seed,
                 "run_commit": "made-up", "run_tree_clean": True, "per_text_files": [],
                 "sha256": {"manifest": "made-up", "starts": "made-up", "strata": "made-up"}, "containers": []}
    t["meta"]["n_scoring_passes"] = expected_scoring_passes(t)
    return t
