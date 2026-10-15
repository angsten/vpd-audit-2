"""Session 6, plan 2: every setting the GPU re-scoring scores, built on the CPU from saved data
(`results/s6_followups/CONVENTIONS.md`, Sections 2, 4, 5, and 8; `sessions/006/engineering/plan_2.md`, Section 3).

A setting is flat: C_l + 1 float32 entries per module in the layout's order, the delta entry last (`pilot.layout`). The
start s0 is the search's own starting setting; s is the setting the search saved at a step; G is its saved signed
cumulative gradient at that step. Nothing here touches a GPU or a harm; the container scores what this module builds,
and the reading scripts rebuild the same settings where they need to know what was scored.

  - Exploited components (Section 4): entries ranked by a_c = G_c (s_c - s0_c), largest first, ties to the lower entry
    index, the delta entries ranked with the rest; the top k keep their final values and every other entry sits at the
    start. k = 0 is the start and k = n the saved setting, bit for bit. The matched random set: in each (matrix,
    stratum) cell, as many entries as the top set has there, drawn uniformly without replacement, each matrix's delta
    entry its own twelfth stratum; one draw per (search, length, k, draw). The uniform draw: k entries of all n. The
    |G| ranking: by |G_c|, largest first, ties to the lower index.
  - Off or on (Section 5): the off part keeps only the top entries at exactly 0, the on part only those at exactly 1;
    the background of 1 sets every entry to 1 except the top set, which keeps its final values. At 320 steps only
    (the conventions' addendum, item 1), beside them: the near-off part keeps the top entries at most 0.1, the near-on
    part those at least 0.9.
  - Controls (Section 8): (a) the 24 delta entries set to 1; (c) a shuffle within alive and never-needed (the ten
    bands merged) or over the whole matrix, delta entries in place, seed ("s6-coarse-shuffle", kind, batch, start,
    length); (d) every entry rounded to 0 below 0.5 and to 1 otherwise, and the snap (the addendum, item 2, replacing
    the moved-only variant): entries at most 0.2 to 0, at least 0.8 to 1, every other entry kept; (b1) every entry 0;
    (b2) 1 on the union of components whose label is above 0.1 at any of a seeded draw of positions, 0 elsewhere,
    delta entries 0.

What a unit scores is listed here too (`heldout_units`, `attack_units`), so the container and the readers share one list.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from typing import Any

import numpy as np

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import pilot as P

GRID = (10, 20, 30, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 38936)
SPLIT_ROWS = ("n20", "n40", "n80", "n160", "n320")
EXPLOIT_ROWS = ("n40", "n80", "n320")
OFFON_ROWS = ("n80", "n320")
TRIGGER_K = 3000
EXTRA_MATCHED_DRAWS = (2, 3)  # at 320 steps and k = 3,000, beside draw 1
LENGTH = {"n20": 20, "n40": 40, "n80": 80, "n160": 160, "n320": 320}
S4 = ("H1", "H5", "H9", "H13")
DELTA_STRATUM = 11  # the delta entries: a twelfth group, one per matrix
COARSE_KINDS = ("alive_and_never_needed", "whole_matrix")
COARSE_LABEL = "s6-coarse-shuffle"
MATCHED_LABEL = "s6-matched"
UNIFORM_LABEL = "s6-uniform"
AGGREGATE_LABEL = "s6-aggregate"
B2_RUNGS = ((64, 8), (16, 8))  # positions per draw, draws
B2_THRESHOLD = 0.1
NEAR_ROWS = ("n320",)  # the addendum, item 1: near-bound parts at 320 steps only
NEAR_OFF, NEAR_ON = 0.1, 0.9
SNAP_LOW, SNAP_HIGH = 0.2, 0.8  # the addendum, item 2


def sha(flat: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(flat, dtype=np.float32).tobytes()).hexdigest()


def grid(n: int) -> tuple[int, ...]:
    """The grid of k, capped at the number of entries (the real layout has 38,936, the grid's last point)."""
    return tuple(sorted({min(k, n) for k in GRID}))


def saved(unit: dict[str, np.ndarray], row: str) -> tuple[np.ndarray, np.ndarray]:
    """A run search unit's saved setting and signed cumulative gradient at a row (`n20` ... `n320`)."""
    names = [str(x) for x in unit["hook_names"]]
    k = names.index(LR.SAVED[row])
    return np.asarray(unit["settings"][k], dtype=np.float32), np.asarray(unit["cum_signed"][k], dtype=np.float32)


# ----------------------------------------------------------------------------- Section 4: rankings and kept sets


def rank_by_effect(s: np.ndarray, s0: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Entries by a_c = G_c (s_c - s0_c) in float64, largest first, ties to the lower entry index."""
    a = np.asarray(G, dtype=np.float64) * (np.asarray(s, dtype=np.float64) - np.asarray(s0, dtype=np.float64))
    return np.lexsort((np.arange(a.size), -a))


def rank_by_abs_gradient(G: np.ndarray) -> np.ndarray:
    g = np.abs(np.asarray(G, dtype=np.float64))
    return np.lexsort((np.arange(g.size), -g))


def keep(s: np.ndarray, s0: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """The start, with the listed entries at the setting's values."""
    out = np.array(s0, dtype=np.float32, copy=True)
    out[idx] = np.asarray(s, dtype=np.float32)[idx]
    return out


def cells_of(lay: list[tuple[str, int]], strata: dict[str, np.ndarray]) -> np.ndarray:
    """Each flat entry's (matrix, stratum) cell as one integer, matrix * 12 + stratum; a delta entry is its matrix's
    stratum 11."""
    out, m = [], 0
    for name, C in lay:
        st = np.asarray(strata[name], dtype=np.int64)
        assert st.shape == (C,) and st.min() >= 0 and st.max() < DELTA_STRATUM
        out.append(m * 12 + st)
        out.append(np.array([m * 12 + DELTA_STRATUM]))
        m += 1
    return np.concatenate(out)


def matched_random(top: np.ndarray, cells: np.ndarray, seed: int) -> np.ndarray:
    """As many entries per cell as `top` has there, drawn uniformly without replacement from the whole cell; cells in
    ascending order, one generator."""
    rng = np.random.default_rng(seed)
    codes, counts = np.unique(cells[np.asarray(top, dtype=np.int64)], return_counts=True)
    picked = [rng.choice(np.flatnonzero(cells == c), size=int(n), replace=False) for c, n in zip(codes, counts)]
    return np.sort(np.concatenate(picked)) if picked else np.zeros(0, dtype=np.int64)


def uniform_random(n: int, k: int, seed: int) -> np.ndarray:
    return np.sort(np.random.default_rng(seed).choice(n, size=k, replace=False))


def matched_seed(attack: str, start: int, row: str, k: int, draw: int) -> int:
    from vpd_audit_2.manifest import seed_of

    return seed_of(MATCHED_LABEL, attack, start, LENGTH[row], k, draw)


def uniform_seed(attack: str, start: int, row: str, k: int) -> int:
    from vpd_audit_2.manifest import seed_of

    return seed_of(UNIFORM_LABEL, attack, start, LENGTH[row], k)


# ----------------------------------------------------------------------------- Section 5: off, on, and a background of 1


def off_part(s: np.ndarray, s0: np.ndarray, top: np.ndarray) -> np.ndarray:
    top = np.asarray(top, dtype=np.int64)
    return keep(s, s0, top[np.asarray(s)[top] == 0])


def on_part(s: np.ndarray, s0: np.ndarray, top: np.ndarray) -> np.ndarray:
    top = np.asarray(top, dtype=np.int64)
    return keep(s, s0, top[np.asarray(s)[top] == 1])


def near_off_part(s: np.ndarray, s0: np.ndarray, top: np.ndarray) -> np.ndarray:
    top = np.asarray(top, dtype=np.int64)
    return keep(s, s0, top[np.asarray(s)[top] <= np.float32(NEAR_OFF)])


def near_on_part(s: np.ndarray, s0: np.ndarray, top: np.ndarray) -> np.ndarray:
    top = np.asarray(top, dtype=np.int64)
    return keep(s, s0, top[np.asarray(s)[top] >= np.float32(NEAR_ON)])


def background_of_one(s: np.ndarray, top: np.ndarray) -> np.ndarray:
    out = np.ones(np.asarray(s).size, dtype=np.float32)
    out[top] = np.asarray(s, dtype=np.float32)[top]
    return out


# ----------------------------------------------------------------------------- Section 8: the controls


def delta_reset(flat: np.ndarray, lay: list[tuple[str, int]]) -> np.ndarray:
    out = np.array(flat, dtype=np.float32, copy=True)
    out[LR.delta_positions(lay)] = 1.0
    return out


def coarse_strata(strata: dict[str, np.ndarray], kind: str) -> dict[str, np.ndarray]:
    """Alive and never-needed: the ten bands merged into one stratum, the never-needed kept as another. Whole matrix:
    one stratum per matrix."""
    if kind == "alive_and_never_needed":
        return {k: np.where(np.asarray(v) == P.DEAD_STRATUM, P.DEAD_STRATUM, 0).astype(np.int64) for k, v in strata.items()}
    if kind == "whole_matrix":
        return {k: np.zeros(np.asarray(v).shape, dtype=np.int64) for k, v in strata.items()}
    raise ValueError(kind)


def coarse_shuffle(flat: np.ndarray, lay: list[tuple[str, int]], strata_kind: dict[str, np.ndarray], kind: str, attack: str, start: int,
                   row: str) -> np.ndarray:
    copy = P.shuffle_source(np.asarray(flat, dtype=np.float32), lay, strata_kind, (kind, attack, start, LENGTH[row]), label=COARSE_LABEL)
    if not LR.check_shuffle(np.asarray(flat, dtype=np.float32), copy, lay, strata_kind):
        raise AssertionError("a coarse shuffle is not a permutation within its strata")
    return copy


def component_mask(lay: list[tuple[str, int]], strata: dict[str, np.ndarray], which: str) -> np.ndarray:
    """Flat booleans: the alive components, or the never-needed ones; delta entries are neither."""
    out = []
    for name, C in lay:
        st = np.asarray(strata[name])
        out.append(st != P.DEAD_STRATUM if which == "alive" else st == P.DEAD_STRATUM)
        out.append(np.array([False]))
    return np.concatenate(out)


def shuffle_description(flat: np.ndarray, copy: np.ndarray, alive: np.ndarray, never: np.ndarray) -> dict[str, float]:
    """The share of alive entries moved by more than 0.5, and the share of the copy's zeros on components that land on
    never-needed components."""
    moved = np.abs(np.asarray(copy, dtype=np.float64) - np.asarray(flat, dtype=np.float64)) > 0.5
    zeros = (np.asarray(copy) == 0) & (alive | never)
    return {"moved_alive_over_half": float(moved[alive].mean()) if alive.any() else float("nan"),
            "zeros_on_never_needed": float((zeros & never).sum() / zeros.sum()) if zeros.any() else float("nan")}


def rounded(flat: np.ndarray) -> np.ndarray:
    return (np.asarray(flat) >= 0.5).astype(np.float32)


def snapped(flat: np.ndarray) -> np.ndarray:
    """Entries at most 0.2 to 0, at least 0.8 to 1, every other entry kept (the thresholds as float32 values)."""
    flat = np.asarray(flat, dtype=np.float32)
    return np.where(flat <= np.float32(SNAP_LOW), np.float32(0.0), np.where(flat >= np.float32(SNAP_HIGH), np.float32(1.0), flat)).astype(np.float32)


# ----------------------------------------------------------------------------- (b2): the first post's aggregated explanations


def global_to_flat(module_offsets: dict[str, int], module_to_c: dict[str, int], lay: list[tuple[str, int]]) -> np.ndarray:
    """For each global component index of the label cache (sorted module order, the cache's offsets), its flat index."""
    n_global = sum(int(c) for c in module_to_c.values())
    out = np.full(n_global, -1, dtype=np.int64)
    off = 0
    for name, C in lay:
        assert int(module_to_c[name]) == C
        g = int(module_offsets[name])
        out[g : g + C] = off + np.arange(C)
        off += C + 1
    assert (out >= 0).all()
    return out


def b2_positions(rung: int, draw: int, n_positions: int) -> np.ndarray:
    from vpd_audit_2.manifest import seed_of

    return np.sort(np.random.default_rng(seed_of(AGGREGATE_LABEL, rung, draw)).choice(n_positions, size=rung, replace=False))


def b2_setting(indptr: np.ndarray, indices: np.ndarray, values: np.ndarray, positions: np.ndarray, to_flat: np.ndarray, n_flat: int) -> tuple[np.ndarray, int]:
    """1 on the union of components whose label is strictly above 0.1 at any of the positions, 0 elsewhere (delta
    entries 0); and the union's size."""
    union: set[int] = set()
    for p in positions:
        a, b = int(indptr[p]), int(indptr[p + 1])
        union.update(int(i) for i in np.asarray(indices[a:b])[np.asarray(values[a:b]) > B2_THRESHOLD])
    out = np.zeros(n_flat, dtype=np.float32)
    if union:
        out[to_flat[np.fromiter(union, dtype=np.int64)]] = 1.0
    return out, len(union)


# ----------------------------------------------------------------------------- what each unit scores


def exploit_passes(s: np.ndarray, s0: np.ndarray, G: np.ndarray, cells: np.ndarray, attack: str, start: int, row: str) -> Iterator[tuple[str, np.ndarray, dict[str, Any]]]:
    """One setting's passes for Sections 4 and 5, each as (pass id, flat setting, what to record beside its harm)."""
    n = s.size
    order = rank_by_effect(s, s0, G)
    ks = grid(n)
    yield "top|0", keep(s, s0, order[:0]), {"k": 0}
    for k in ks:
        top = order[:k]
        yield f"top|{k}", keep(s, s0, top), {"k": k}
        draws = (1,) + (EXTRA_MATCHED_DRAWS if row == "n320" and k == min(TRIGGER_K, n) else ())
        for d in draws:
            idx = matched_random(top, cells, matched_seed(attack, start, row, k, d))
            yield f"matched|{k}|{d}", keep(s, s0, idx), {"k": k, "draw": d, "sha": sha(idx.astype(np.float32))}
    if row == "n320":
        k = min(TRIGGER_K, n)
        idx = uniform_random(n, k, uniform_seed(attack, start, row, k))
        yield f"uniform|{k}", keep(s, s0, idx), {"k": k, "sha": sha(idx.astype(np.float32))}
        gorder = rank_by_abs_gradient(G)
        for k in ks:
            yield f"absg|{k}", keep(s, s0, gorder[:k]), {"k": k}
    if row in OFFON_ROWS:
        for k in ks:
            top = order[:k]
            yield f"off|{k}", off_part(s, s0, top), {"k": k}
            yield f"on|{k}", on_part(s, s0, top), {"k": k}
            yield f"bg1|{k}", background_of_one(s, top), {"k": k}
    if row in NEAR_ROWS:
        for k in ks:
            top = order[:k]
            yield f"near_off|{k}", near_off_part(s, s0, top), {"k": k}
            yield f"near_on|{k}", near_on_part(s, s0, top), {"k": k}


def control_passes(s_by_row: dict[str, np.ndarray], s0: np.ndarray, lay: list[tuple[str, int]], coarse: dict[str, dict[str, np.ndarray]],
                   alive: np.ndarray, never: np.ndarray, attack: str, start: int) -> Iterator[tuple[str, np.ndarray, dict[str, Any]]]:
    """One attack search's 25 control passes on an S4 batch: (a) delta reset, (c) two coarser shuffles, (d) rounded and
    snapped, at each of the five lengths."""
    for row in SPLIT_ROWS:
        s = s_by_row[row]
        yield f"a|{row}", delta_reset(s, lay), {}
        for kind in COARSE_KINDS:
            copy = coarse_shuffle(s, lay, coarse[kind], kind, attack, start, row)
            yield f"c|{kind}|{row}", copy, {"sha": sha(copy), **shuffle_description(s, copy, alive, never)}
        yield f"d|rounded|{row}", rounded(s), {}
        yield f"d|snapped|{row}", snapped(s), {}


def control_start_passes(starts: dict[int, np.ndarray], lay: list[tuple[str, int]]) -> Iterator[tuple[str, np.ndarray, dict[str, Any]]]:
    for s, s0 in sorted(starts.items()):
        yield f"a_start|{s}", delta_reset(s0, lay), {}
        yield f"d_start|{s}", rounded(s0), {}


def heldout_units(batch: str, attack_batches: list[str], starts: list[int], own_attack: str) -> list[tuple[str, str, dict[str, Any]]]:
    """A held-out container's units, in order: (unit name, kind, parameters). `own_attack` is the attack batch of the
    same index (Section 4 scores A_j on H_j)."""
    units: list[tuple[str, str, dict[str, Any]]] = [(f"check_{batch}", "check", {})]
    units += [(f"split_{batch}_{a}_s{s}", "split", {"attack": a, "start": s}) for a in attack_batches for s in starts]
    units += [(f"exploit_{batch}_s{s}_{row}", "exploit", {"attack": own_attack, "start": s, "row": row}) for s in starts for row in EXPLOIT_ROWS]
    units += [(f"ones_{batch}", "ones", {}), (f"b_{batch}", "b", {})]
    if batch in S4:
        units += [(f"controls_{batch}_{a}_s{s}", "controls", {"attack": a, "start": s}) for a in attack_batches for s in starts]
        units += [(f"control_starts_{batch}", "control_starts", {})]
    return units


def attack_units(batch: str, starts: list[int]) -> list[tuple[str, str, dict[str, Any]]]:
    return ([(f"check_{batch}", "check", {})] + [(f"split_{batch}_{batch}_s{s}", "split", {"attack": batch, "start": s}) for s in starts]
            + [(f"b1_{batch}", "b1", {})])


# ----------------------------------------------------------------------------- plan 3, Section 7: intact-background variants
# Added after the readings, as description. On cell set S4, three variants of each carried setting with an intact
# background, per length; V1 is a flat setting, V2 and V3 per-position sources built by `s6_run.split_sources`.

VARIANTS = ("V1", "V2", "V3")


def zeros_alone(flat: np.ndarray) -> np.ndarray:
    """V1, the zeros alone on an intact model: every entry at exactly 0 stays 0 and every other entry is set to 1, the
    delta entries included."""
    flat = np.asarray(flat, dtype=np.float32)
    return np.where(flat == 0, np.float32(0.0), np.float32(1.0)).astype(np.float32)


def variant_split_args(s: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """V2 and V3 as `split_sources` arguments: (the source where the label is zero, the source where it is positive, the
    delta entries' source). A mask is l + source (1 - l), so a source of 1 gives a mask of 1 at any label.
      - V2, Part Z on an intact model: s where the label is zero, 1 where it is positive; the delta entries s, as in Part Z.
      - V3, Part P on an intact model: s where the label is positive (the mask l + s (1 - l)), 1 where it is zero; the
        delta entries 1."""
    s = np.asarray(s, dtype=np.float32)
    ones = np.ones_like(s)
    return {"V2": (s, ones, s), "V3": (ones, s, ones)}


def variant_units(batch: str, attack_batches: list[str], starts: list[int]) -> list[tuple[str, str, dict[str, Any]]]:
    """An S4 batch's units for the variants: the check, then one unit per carried setting's search (its five lengths)."""
    return ([(f"variants_check_{batch}", "variants_check", {})]
            + [(f"variants_{batch}_{a}_s{s}", "variants", {"attack": a, "start": s}) for a in attack_batches for s in starts])


# ----------------------------------------------------------------------------- plan 3, Section 8: the dose-response
# Added after the readings, as description. On cell set S4, for each carried setting, length, and fraction f, a random
# fraction f of the setting's entries at exactly 0 stays 0 and every other entry is 1; f = 1 is V1, f = 0 all ones.

DOSE_FRACTIONS = (0.25, 0.5, 0.75)
DOSE_LABEL = "s6-dose"


def dose_key(f: float) -> str:
    """The fraction as it enters a seed and a pass id: `seed_of` takes ints and strings only, so "0.25", "0.5", "0.75"."""
    return f"{f:g}"


def dose_seed(attack: str, start: int, row: str, f: float) -> int:
    """One draw per (setting, length, fraction): the setting is the attack search's, so its four S4 batches share it."""
    from vpd_audit_2.manifest import seed_of

    return seed_of(DOSE_LABEL, attack, start, LENGTH[row], dose_key(f))


def dose_setting(flat: np.ndarray, f: float, seed: int) -> tuple[np.ndarray, int, int]:
    """A uniformly random subset of the setting's entries at exactly 0 (the delta entries included, as V1 treats them),
    of f times their number rounded half up, stays 0; every other entry is 1. Returns the setting, the count of zeros,
    and the count kept at 0."""
    flat = np.asarray(flat, dtype=np.float32)
    zeros = np.flatnonzero(flat == 0)
    k = int(np.floor(f * zeros.size + 0.5))
    kept = np.random.default_rng(seed).choice(zeros, size=k, replace=False)
    out = np.ones_like(flat)
    out[kept] = np.float32(0.0)
    return out, int(zeros.size), k


def dose_passes(s: np.ndarray, attack: str, start: int, row: str) -> Iterator[tuple[str, np.ndarray, dict[str, Any]]]:
    for f in DOSE_FRACTIONS:
        seed = dose_seed(attack, start, row, f)
        flat, zeros, kept = dose_setting(s, f, seed)
        yield f"D{dose_key(f)}|{row}", flat, {"f": f, "zeros": zeros, "kept_at_0": kept, "seed": seed}


def dose_units(batch: str, attack_batches: list[str], starts: list[int]) -> list[tuple[str, str, dict[str, Any]]]:
    """An S4 batch's units for the dose-response: the variants' check unit, then one unit per carried setting's search."""
    return ([(f"dose_check_{batch}", "variants_check", {})]
            + [(f"dose_{batch}_{a}_s{s}", "dose", {"attack": a, "start": s}) for a in attack_batches for s in starts])


# ----------------------------------------------------------------------------- plan 3, Section 9: the dose-response on the rounded off set
# Added at the PI's request, as description. The off set is every entry below one half (the delta entries included); a
# random fraction f of it is set to 0 and every other entry to 1. At f = 1 this is the rounded setting of control (d).

DOSE_ROUNDED_FRACTIONS = (0.25, 0.5, 0.75, 0.9)
DOSE_ROUNDED_LABEL = "s6-dose-rounded"


def dose_rounded_seed(attack: str, start: int, row: str, f: float) -> int:
    """One draw per (setting, step, fraction), shared by the setting's four S4 batches; f as a string, as Section 8."""
    from vpd_audit_2.manifest import seed_of

    return seed_of(DOSE_ROUNDED_LABEL, attack, start, LENGTH[row], dose_key(f))


def dose_rounded_setting(flat: np.ndarray, f: float, seed: int) -> tuple[np.ndarray, int, int]:
    """A uniformly random subset of the setting's entries below one half (the delta entries included), of f times their
    number rounded half up, is set to 0; every other entry is 1. Returns the setting, the size of the off set, and the
    count set to 0. At f = 1 it is `rounded(flat)`."""
    flat = np.asarray(flat, dtype=np.float32)
    off = np.flatnonzero(flat < np.float32(0.5))
    k = int(np.floor(f * off.size + 0.5))
    chosen = np.random.default_rng(seed).choice(off, size=k, replace=False)
    out = np.ones_like(flat)
    out[chosen] = np.float32(0.0)
    return out, int(off.size), k


def dose_rounded_passes(s: np.ndarray, attack: str, start: int, row: str) -> Iterator[tuple[str, np.ndarray, dict[str, Any]]]:
    for f in DOSE_ROUNDED_FRACTIONS:
        seed = dose_rounded_seed(attack, start, row, f)
        flat, off, k = dose_rounded_setting(s, f, seed)
        yield f"R{dose_key(f)}|{row}", flat, {"f": f, "off_set": off, "set_to_0": k, "seed": seed}


def dose_rounded_units(batch: str, attack_batches: list[str], starts: list[int]) -> list[tuple[str, str, dict[str, Any]]]:
    """An S4 batch's units: the variants' check unit, then one unit per carried setting's search."""
    return ([(f"dose_rounded_check_{batch}", "variants_check", {})]
            + [(f"dose_rounded_{batch}_{a}_s{s}", "dose_rounded", {"attack": a, "start": s}) for a in attack_batches for s in starts])


def n_passes(kind: str, row: str | None = None, n: int = 38936, s4: bool = False, n_starts: int = 5) -> int:
    """How many passes a unit of each kind scores (for the cost projection)."""
    ks = len(grid(n))
    if kind == "check":
        return 2
    if kind == "split":
        return 2 * len(SPLIT_ROWS)
    if kind == "exploit":
        extra = (len(EXTRA_MATCHED_DRAWS) + 1 + ks) if row == "n320" else 0
        return 1 + 2 * ks + extra + (3 * ks if row in OFFON_ROWS else 0) + (2 * ks if row in NEAR_ROWS else 0)
    if kind in ("ones", "b1"):
        return 1
    if kind == "b":
        return 1 + sum(d for _, d in B2_RUNGS)
    if kind == "controls":
        return 5 * len(SPLIT_ROWS)
    if kind == "control_starts":
        return 2 * n_starts
    if kind == "variants":
        return len(VARIANTS) * len(SPLIT_ROWS)
    if kind == "variants_check":
        return 3
    if kind == "dose":
        return len(DOSE_FRACTIONS) * len(SPLIT_ROWS)
    if kind == "dose_rounded":
        return len(DOSE_ROUNDED_FRACTIONS) * len(SPLIT_ROWS)
    raise ValueError(kind)
