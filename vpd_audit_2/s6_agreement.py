"""Plan 3 of the research log, Section 2: agreement between settings (`results/s6_followups/CONVENTIONS.md`, Section 7 and the
addendum's item 3; plan 3 of the research log, Section 2). Description, no line; no GPU.

    uv run python -m vpd_audit_2.s6_agreement > results/s6_followups/agreement.txt

The settings. Every search from starts 9 to 13: the run's 160 (A1 to A16 and H1 to H16; `.cache/s5_lead_units/run/lead/`,
each file checked against the earlier backup) and the starts test's 40 (C1 to C8; `.cache/s6_starts/units/`, loaded by
name and each file checked against the starts test's backup; the guard search of C1 from start 1 is not read). And the
pilot's 64 (C1 to C8 from starts 1 to 8; `.cache/s4_pilot_sources/`, fetched from the volume's `s4_pilot/part_a/sources/`,
every array checked against the SHA-256 the pilot's `runs.json` recorded), by value only: the pilot saved no gradients.
Rows: the settings saved after 20, 40, 80, 160, and 320 steps and at the harm levels 2, 5, and 10 nats; a search that
never reached a level has no setting there and is in no pair there.

Agreement. Two settings agree on an entry when both values are below one half or both are at or above one half. The
share is taken over the 38,912 rank-one entries, and apart over the alive entries, the never-needed entries, and the 24
delta entries.

Chance levels, each a sum over groups g of (n_g / N) [x_a x_b + (1 - x_a)(1 - x_b)] within the entries reported:
  - independence (pairs from different starts): x = p, the share of the setting's entries in g below one half; the groups
    are the shuffle's strata, (matrix, usage band) for alive entries and (matrix, never-needed), 264 in all, and the 24
    delta entries are one group of their own;
  - crossing (pairs from the same start): x = q, the share of entries in g on the other side of one half from their start
    value, over the same groups;
  - decile (pairs from the same start; the addendum's item 3 with our refinement): the crossing formula over cells
    of start-value decile crossed with alive or never-needed only. The deciles are ten equal-count bins of the start's
    38,912 rank-one entries by rank, ties to the lower index; the alive and never-needed rows use the same bins. Not
    defined for the 24 delta entries (printed n/a).
Agreement beyond chance is (mean agreement - mean chance) / (1 - mean chance) over a family's pairs, for each level.

The top-3,000 overlap, for pairs whose settings both have saved gradients (starts 9 to 13): each setting's top 3,000
entries under plan 2 of the research log's ranking a_c = G_c (s_c - s0_c) (`s6_build.rank_by_effect`, all 38,936 entries, the delta entries
ranked with the rest); O the count of entries in both; E = sum_c k_a,c k_b,c / n_c over plan 2 of the research log's matched-random cells
(matrix by stratum, each matrix's delta entry a cell of its own); beyond chance (mean O - mean E) / (3000 - mean E); and,
among overlapping entries, the share on the same side of one half, pooled: over a family's pairs, the sum of the
same-side counts over the sum of O.

The families: same start and different batches; different starts and the same batch; different starts and different
batches. No two searches share both a batch and a start (checked).

Untouched: an entry whose saved absolute gradient sum is exactly zero (the conventions, Section 3), checked to equal its
start. The pilot saved no gradients; an untouched entry equals its start at every step up to the one saved, so for a pilot
setting saved at step k the entries equal to their start in every pilot setting saved at a step of at most k bound its
untouched entries from above, and those are what the second same-start print leaves out for the pilot's pairs.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import pilot as P
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR

REPO_ROOT = env.REPO_ROOT
RUN_UNITS = REPO_ROOT / ".cache" / "s5_lead_units" / "run" / "lead"
STARTS_UNITS = REPO_ROOT / ".cache" / "s6_starts" / "units"
STARTS_BACKUP = REPO_ROOT / "results" / "s6_starts" / "backup.json"
PILOT_SOURCES = REPO_ROOT / ".cache" / "s4_pilot_sources"
PILOT_RUNS = REPO_ROOT / "results" / "s4_pilot" / "part_a" / "runs.json"

ROWS = ("n320", "n20", "n40", "n80", "n160", "h2", "h5", "h10")  # 320 steps first
ROW_LABEL = {"n20": "20 steps", "n40": "40 steps", "n80": "80 steps", "n160": "160 steps", "n320": "320 steps",
             "h2": "harm level 2 nats", "h5": "harm level 5 nats", "h10": "harm level 10 nats"}
RUN_STARTS = LR.STARTS  # 9 to 13
PILOT_STARTS = tuple(range(1, 9))
DECIDING = tuple(f"A{i}" for i in range(1, 17)) + tuple(f"H{j}" for j in range(1, 17))
CALIBRATION = tuple(f"C{j}" for j in range(1, 9))
STARTS_TEST_ARM = "starts_test"
TOP_K = B.TRIGGER_K  # 3,000
N_RANK_ONE = 38912
HALF = np.float32(0.5)

GROUPS = ("rank_one", "alive", "never_needed", "delta")
GROUP_LABEL = {"rank_one": "rank-one", "alive": "alive", "never_needed": "never-needed", "delta": "delta"}
FAMILIES = ("same_start", "same_batch", "different")
FAMILY_LABEL = {"same_start": "same start, different batches", "same_batch": "different starts, same batch",
                "different": "different starts, different batches"}
LEVELS = {"same_start": ("crossing", "decile"), "same_batch": ("independence",), "different": ("independence",)}


class Refusal(Exception):
    pass


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


# ----------------------------------------------------------------------------- the entries: groups, strata, cells


@dataclass(frozen=True)
class Entries:
    """The flat layout's groups (flat indices), each group's strata for the chance levels (codes 0..G-1 over the group's
    columns), the alive mask, and plan 2 of the research log's matched-random cells over all entries."""
    cols: dict[str, np.ndarray]
    codes: dict[str, np.ndarray]
    alive: np.ndarray
    is_delta: np.ndarray
    cells: np.ndarray
    n_cells: int


def entries(lay: list[tuple[str, int]], strata: dict[str, np.ndarray]) -> Entries:
    fine, m = [], 0
    for name, C in lay:
        st = np.asarray(strata[name], dtype=np.int64)
        assert st.shape == (C,) and st.min() >= 0 and st.max() <= P.DEAD_STRATUM
        fine.append(m * (P.DEAD_STRATUM + 1) + st)
        fine.append(np.array([-1]))
        m += 1
    fine_flat = np.concatenate(fine)
    is_delta = fine_flat < 0
    assert np.array_equal(np.flatnonzero(is_delta), LR.delta_positions(lay))
    alive = B.component_mask(lay, strata, "alive")
    never = B.component_mask(lay, strata, "never")
    cols = {"rank_one": np.flatnonzero(~is_delta), "alive": np.flatnonzero(alive), "never_needed": np.flatnonzero(never),
            "delta": np.flatnonzero(is_delta)}
    codes = {g: np.unique(fine_flat[cols[g]], return_inverse=True)[1].astype(np.int64) for g in ("rank_one", "alive", "never_needed")}
    codes["delta"] = np.zeros(cols["delta"].size, dtype=np.int64)
    cells = B.cells_of(lay, strata)
    return Entries(cols=cols, codes=codes, alive=alive, is_delta=is_delta, cells=cells, n_cells=int(cells.max()) + 1)


def deciles(values: np.ndarray) -> np.ndarray:
    """Ten equal-count bins by rank, ties to the lower index: bin = rank * 10 // n."""
    values = np.asarray(values)
    order = np.argsort(values, kind="stable")
    rank = np.empty(values.size, dtype=np.int64)
    rank[order] = np.arange(values.size)
    return rank * 10 // values.size


def decile_codes(s0: np.ndarray, ent: Entries) -> dict[str, np.ndarray]:
    """For one start, each group's decile cells over its columns: decile by alive or never-needed for the rank-one
    entries, the decile alone within the alive and within the never-needed entries; the deciles are the start's
    rank-one entries'."""
    d = np.full(s0.size, -1, dtype=np.int64)
    d[ent.cols["rank_one"]] = deciles(np.asarray(s0)[ent.cols["rank_one"]])
    never = ~ent.alive & ~ent.is_delta
    out = {"rank_one": d[ent.cols["rank_one"]] * 2 + never[ent.cols["rank_one"]].astype(np.int64),
           "alive": d[ent.cols["alive"]], "never_needed": d[ent.cols["never_needed"]]}
    return {g: np.unique(v, return_inverse=True)[1].astype(np.int64) for g, v in out.items()}


# ----------------------------------------------------------------------------- the arithmetic


def below(s: np.ndarray) -> np.ndarray:
    return np.asarray(s, dtype=np.float32) < HALF


def crossed(s: np.ndarray, s0: np.ndarray) -> np.ndarray:
    """On the other side of one half from the start value."""
    return below(s) != below(s0)


def shares(X: np.ndarray, codes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per row of X (settings by entries, booleans), the share of True within each code; and each code's entry count."""
    X = np.atleast_2d(np.asarray(X))
    codes = np.asarray(codes, dtype=np.int64)
    counts = np.bincount(codes)
    if not (counts > 0).all():
        raise ValueError("a code with no entries")
    order = np.argsort(codes, kind="stable")
    bounds = np.concatenate([[0], np.cumsum(counts)[:-1]])
    sums = np.add.reduceat(X[:, order].astype(np.float64), bounds, axis=1)
    return sums / counts, counts


def chance(Xa: np.ndarray, Xb: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """sum_g w_g [x_a,g x_b,g + (1 - x_a,g)(1 - x_b,g)] for every row of Xa against every row of Xb."""
    w = np.asarray(weights, dtype=np.float64)
    return (Xa * w) @ Xb.T + ((1.0 - Xa) * w) @ (1.0 - Xb).T


def agreement(Ba: np.ndarray, Bb: np.ndarray) -> np.ndarray:
    """The share of entries on which each row of Ba and each row of Bb are on the same side (booleans: below one half)."""
    X, Y = np.asarray(Ba, dtype=np.float64), np.asarray(Bb, dtype=np.float64)
    return (X @ Y.T + (1.0 - X) @ (1.0 - Y).T) / X.shape[1]


def kappa(a: float, c: float) -> float:
    return float((a - c) / (1.0 - c)) if 1.0 - c != 0 else float("nan")


def expected_overlap(ka: np.ndarray, kb: np.ndarray, n: np.ndarray) -> float:
    """E = sum_g k_a,g k_b,g / n_g, over the groups that have entries (an empty group holds no top entry)."""
    return float(np.sum(np.asarray(ka, dtype=np.float64) * per_entry(kb, n)))


def per_entry(k: np.ndarray, n: np.ndarray) -> np.ndarray:
    """k_g / n_g, and 0 where a group has no entries, which must then hold none of the top set."""
    k, n = np.asarray(k, dtype=np.float64), np.asarray(n, dtype=np.float64)
    if (k[..., n == 0] != 0).any():
        raise ValueError("a top entry in a cell with no entries")
    return np.divide(k, n, out=np.zeros(np.broadcast(k, n).shape), where=n > 0)


def pair(below_a: np.ndarray, below_b: np.ndarray, crossed_a: np.ndarray, crossed_b: np.ndarray, codes: np.ndarray,
         keep: np.ndarray | None = None, decile: np.ndarray | None = None) -> dict[str, float]:
    """One pair over one group's entries by direct counting (the reference the matrix path is tested against, and the
    path the untouched-in-both print takes): agreement and the independence, crossing, and decile levels, over the kept
    entries, each group's n_g and shares counted over the kept entries only."""
    keep = np.ones(len(codes), dtype=bool) if keep is None else np.asarray(keep, dtype=bool)
    a, b, ca, cb, g = (np.asarray(x)[keep] for x in (below_a, below_b, crossed_a, crossed_b, codes))
    out = {"agreement": float(np.mean(a == b)) if a.size else float("nan")}

    def level(xa: np.ndarray, xb: np.ndarray, cells: np.ndarray) -> float:
        total = 0.0
        for c in np.unique(cells):
            m = cells == c
            pa, pb = xa[m].mean(), xb[m].mean()
            total += m.sum() / cells.size * (pa * pb + (1 - pa) * (1 - pb))
        return float(total)

    out["independence"] = level(a, b, g)
    out["crossing"] = level(ca, cb, g)
    out["decile"] = level(ca, cb, np.asarray(decile)[keep]) if decile is not None else float("nan")
    return out


# ----------------------------------------------------------------------------- the settings


@dataclass
class Search:
    source: str  # "run", "starts_test", or "pilot"
    batch: str
    start: int
    below: dict[str, np.ndarray] = field(default_factory=dict)  # row -> bool over the 38,936 entries
    crossed: dict[str, np.ndarray] = field(default_factory=dict)
    untouched: dict[str, np.ndarray] = field(default_factory=dict)  # for the pilot, the upper bound
    top: dict[str, np.ndarray] = field(default_factory=dict)  # row -> the top 3,000 entries; empty for the pilot


def _add_row(x: Search, row: str, s: np.ndarray, s0: np.ndarray, untouched: np.ndarray, G: np.ndarray | None) -> None:
    s = np.asarray(s, dtype=np.float32)
    if s.shape != s0.shape:
        raise Refusal(f"{x.source} {x.batch} s{x.start} {row}: a setting of shape {s.shape}")
    x.below[row] = below(s)
    x.crossed[row] = crossed(s, s0)
    x.untouched[row] = np.asarray(untouched, dtype=bool)
    if G is not None:
        x.top[row] = np.sort(B.rank_by_effect(s, s0, G)[:TOP_K])


def read_unit(path: Path, expected_sha: str, batch: str, start: int, arm: str, s0: np.ndarray, source: str) -> Search:
    """A search unit (the run's or the starts test's), after checking its file against the recorded SHA-256 and its meta
    against the batch, the start, the arm, and the start's own SHA-256."""
    data = path.read_bytes()
    if _sha_bytes(data) != expected_sha:
        raise Refusal(f"{path.name} does not match its recorded SHA-256")
    with np.load(io.BytesIO(data), allow_pickle=False) as z:
        names = [str(v) for v in z["hook_names"]]
        settings, signed, absolute = z["settings"], z["cum_signed"], z["cum_abs"]
        meta = SR.json_field(z, "meta")
    if (meta["kind"], meta["batch"], meta["start"], meta["arm"], meta["delta_held"]) != ("search", batch, start, arm, False):
        raise Refusal(f"{path.name} is not the {arm} search of {batch} from start {start}")
    if meta["start_sha256"] != LR.setting_sha256(s0):
        raise Refusal(f"{path.name} did not begin from start {start}")
    x = Search(source, batch, start)
    for row in ROWS:
        if LR.SAVED[row] in names:
            k = names.index(LR.SAVED[row])
            untouched = absolute[k] == 0
            if not np.array_equal(settings[k][untouched], s0[untouched]):
                raise Refusal(f"{path.name} {row}: an untouched entry differs from its start")
            _add_row(x, row, settings[k], s0, untouched, signed[k])
    return x


def read_pilot(path: Path, record: dict[str, Any], batch: str, start: int, s0: np.ndarray) -> Search:
    """A pilot search's saved settings, every array checked against the SHA-256 `runs.json` recorded for it."""
    if list(record["start_key"])[1:] != ["start", start] or record["batch"] != batch:
        raise Refusal(f"the pilot's record for {batch} s{start} is another search's")
    recorded, events = record["saved_sources_sha256"], record["hook_events"]
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    if set(arrays) != set(recorded) | {"final"} or set(events) != set(recorded):
        raise Refusal(f"{path.name} does not hold the arrays the pilot recorded")
    for k, h in recorded.items():
        if _sha_array(arrays[k]) != h:
            raise Refusal(f"{path.name} {k} does not match its recorded SHA-256")
    x = Search("pilot", batch, start)
    for row in ROWS:
        name = LR.SAVED[row]
        if name in recorded:
            bound = np.ones(s0.size, dtype=bool)
            for m, k in events.items():
                if k <= events[name]:
                    bound &= np.asarray(arrays[m], dtype=np.float32) == s0
            _add_row(x, row, arrays[name], s0, bound, None)
    return x


def pilot_starts_sha256(listing: str) -> str | None:
    """The starts file's SHA-256 from the pilot's record, which holds `sha256sum` lines ("<hash>  <file name>")."""
    found = [line.split()[0] for line in listing.splitlines() if line.split()[1:] == [LL.STARTS_NPZ.name]]
    return found[0] if len(found) == 1 else None


def load(lay: list[tuple[str, int]] | None = None) -> tuple[list[Search], dict[str, Any]]:
    lay = P.layout() if lay is None else lay
    starts = {s: LR.flat_start(st, lay, False) for s, st in LL.starts_for(PILOT_STARTS + RUN_STARTS).items()}
    run_hashes = SR.run_unit_hashes()
    backup = json.load(open(STARTS_BACKUP))
    if backup["folder"] != ".cache/s6_starts/units":
        raise Refusal("the starts test's backup is of another folder")
    pilot_runs = json.load(open(PILOT_RUNS))
    if pilot_starts_sha256(pilot_runs["extended_starts_sha256"]) != LR.SIGNED_SHA256["starts"]:
        raise Refusal("the pilot's starts are not the signed ones")
    out: list[Search] = []
    for batch in DECIDING:
        for s in RUN_STARTS:
            name = f"search_{batch}_s{s}.npz"
            out.append(read_unit(RUN_UNITS / name, run_hashes[name], batch, s, "lead", starts[s], "run"))
    for batch in CALIBRATION:
        for s in RUN_STARTS:
            name = f"search_{batch}_s{s}.npz"
            out.append(read_unit(STARTS_UNITS / name, backup["files"][name], batch, s, STARTS_TEST_ARM, starts[s], "starts_test"))
    for batch in CALIBRATION:
        for s in PILOT_STARTS:
            out.append(read_pilot(PILOT_SOURCES / f"{batch}_s{s}.npz", pilot_runs["a1"][batch][str(s)], batch, s, starts[s]))
    counts = {src: sum(x.source == src for x in out) for src in ("run", "starts_test", "pilot")}
    if counts != {"run": 160, "starts_test": 40, "pilot": 64}:
        raise Refusal(f"the settings read are not the 264: {counts}")
    return out, {"counts": counts, "starts": starts}


# ----------------------------------------------------------------------------- per row: every pair, then the families


@dataclass
class RowPairs:
    """One row's pairs (i < j over the searches present) and each pair's numbers."""
    searches: list[Search]
    i: np.ndarray
    j: np.ndarray
    family: dict[str, np.ndarray]
    values: dict[str, dict[str, np.ndarray]]  # group -> {"agreement", "independence", "crossing", "decile"} over pairs
    overlap: dict[str, np.ndarray]  # "valid", "observed", "expected", "same_side" over pairs
    untouched: dict[str, Any]  # the same-start family with entries untouched in both left out


def families(start: np.ndarray, batch: np.ndarray, i: np.ndarray, j: np.ndarray) -> dict[str, np.ndarray]:
    same_start, same_batch = start[i] == start[j], batch[i] == batch[j]
    if (same_start & same_batch).any():
        raise Refusal("two searches of one batch from one start")
    return {"same_start": same_start & ~same_batch, "same_batch": ~same_start & same_batch, "different": ~same_start & ~same_batch}


def row_pairs(searches: list[Search], row: str, ent: Entries, dec: dict[int, dict[str, np.ndarray]]) -> RowPairs:
    present = [x for x in searches if row in x.below]
    n = len(present)
    i, j = np.triu_indices(n, 1)
    start = np.array([x.start for x in present])
    batch = np.array([x.batch for x in present])
    fam = families(start, batch, i, j)
    Bel = np.stack([x.below[row] for x in present])
    Cr = np.stack([x.crossed[row] for x in present])
    U = np.stack([x.untouched[row] for x in present])
    values: dict[str, dict[str, np.ndarray]] = {}
    for g in GROUPS:
        cols, codes = ent.cols[g], ent.codes[g]
        X, Y = Bel[:, cols], Cr[:, cols]
        p, counts = shares(X, codes)
        q, _ = shares(Y, codes)
        w = counts / counts.sum()
        v = {"agreement": agreement(X, X)[i, j], "independence": chance(p, p, w)[i, j],
             "crossing": np.where(start[i] == start[j], chance(q, q, w)[i, j], np.nan)}
        D = np.full((n, n), np.nan)
        if g != "delta":
            for s in np.unique(start):
                ix = np.flatnonzero(start == s)
                qd, cd = shares(Y[ix], dec[int(s)][g])
                D[np.ix_(ix, ix)] = chance(qd, qd, cd / cd.sum())
        v["decile"] = D[i, j]
        values[g] = v

    # the top-3,000 overlap, where both settings have saved gradients
    has = np.array([row in x.top for x in present])
    T = np.zeros(Bel.shape, dtype=bool)
    K = np.zeros((n, ent.n_cells), dtype=np.float64)
    for k, x in enumerate(present):
        if has[k]:
            T[k, x.top[row]] = True
            K[k] = np.bincount(ent.cells[x.top[row]], minlength=ent.n_cells)
    n_cell = np.bincount(ent.cells, minlength=ent.n_cells).astype(np.float64)
    Tf, Tb, Ta = T.astype(np.float64), (T & Bel).astype(np.float64), (T & ~Bel).astype(np.float64)
    overlap = {"valid": has[i] & has[j], "observed": (Tf @ Tf.T)[i, j], "expected": (per_entry(K, n_cell) @ K.T)[i, j],
               "same_side": (Tb @ Tb.T + Ta @ Ta.T)[i, j]}

    # the same-start family with the entries untouched in both settings left out
    ss = np.flatnonzero(fam["same_start"])
    left_out = {g: (U[:, ent.cols[g]].astype(np.float64) @ U[:, ent.cols[g]].T.astype(np.float64))[i[ss], j[ss]] for g in GROUPS}
    untouched = {"pairs": int(ss.size), "entries_left_out": {g: int(left_out[g].sum()) for g in GROUPS},
                 "pairs_affected": {g: int((left_out[g] > 0).sum()) for g in GROUPS}, "values": {}}
    for g in GROUPS:
        v = {k: values[g][k][ss].copy() for k in ("agreement", "crossing", "decile")}
        for m in np.flatnonzero(left_out[g] > 0):
            a, b = i[ss[m]], j[ss[m]]
            cols = ent.cols[g]
            keep = ~(U[a, cols] & U[b, cols])
            r = pair(Bel[a, cols], Bel[b, cols], Cr[a, cols], Cr[b, cols], ent.codes[g], keep,
                     dec[int(start[a])][g] if g != "delta" else None)
            v["agreement"][m], v["crossing"][m] = r["agreement"], r["crossing"]
            if g != "delta":
                v["decile"][m] = r["decile"]
        untouched["values"][g] = v
    return RowPairs(present, i, j, fam, values, overlap, untouched)


def summarize(values: dict[str, dict[str, np.ndarray]], mask: np.ndarray, levels: tuple[str, ...]) -> dict[str, Any]:
    out: dict[str, Any] = {"pairs": int(mask.sum())}
    for g in GROUPS:
        a = float(np.mean(values[g]["agreement"][mask])) if mask.any() else float("nan")
        d: dict[str, Any] = {"agreement": a}
        for lv in levels:
            if lv == "decile" and g == "delta":
                d["chance_decile"], d["kappa_decile"] = None, None
                continue
            c = float(np.mean(values[g][lv][mask])) if mask.any() else float("nan")
            d[f"chance_{lv}"], d[f"kappa_{lv}"] = c, kappa(a, c)
        out[g] = d
    return out


def summarize_overlap(overlap: dict[str, np.ndarray], mask: np.ndarray) -> dict[str, Any]:
    m = mask & overlap["valid"]
    if not m.any():
        return {"pairs": 0}
    O, E = float(np.mean(overlap["observed"][m])), float(np.mean(overlap["expected"][m]))
    total = float(np.sum(overlap["observed"][m]))
    return {"pairs": int(m.sum()), "observed": O, "expected": E, "beyond_chance": (O - E) / (TOP_K - E),
            "same_side": float(np.sum(overlap["same_side"][m]) / total) if total > 0 else float("nan")}


def row_summary(rp: RowPairs) -> dict[str, Any]:
    out: dict[str, Any] = {"searches": len(rp.searches), "families": {}}
    for f in FAMILIES:
        out["families"][f] = summarize(rp.values, rp.family[f], LEVELS[f])
        out["families"][f]["overlap"] = summarize_overlap(rp.overlap, rp.family[f])
    u = rp.untouched
    every = np.ones(u["pairs"], dtype=bool)
    second = summarize(u["values"], every, LEVELS["same_start"])
    first = summarize(rp.values, rp.family["same_start"], LEVELS["same_start"])
    out["same_start_untouched_left_out"] = {"entries_left_out": u["entries_left_out"], "pairs_affected": u["pairs_affected"],
                                           "rows": second, "equals_first": same(second, first)}
    return out


def same(a: Any, b: Any) -> bool:
    """Equal, value for value, with an undefined value equal to another undefined value."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, float) and isinstance(b, float):
        return a == b or (np.isnan(a) and np.isnan(b))
    return a == b


def breakdowns(rp: RowPairs) -> dict[str, Any]:
    """At one row: the same-start family by start and split by batch set; the same-batch family by start pair."""
    start = np.array([x.start for x in rp.searches])
    batch = np.array([x.batch for x in rp.searches])
    si, sj, bi, bj = start[rp.i], start[rp.j], batch[rp.i], batch[rp.j]
    ss, sb = rp.family["same_start"], rp.family["same_batch"]

    def both(m: np.ndarray, f: str) -> dict[str, Any]:
        d = summarize(rp.values, m, LEVELS[f])
        d["overlap"] = summarize_overlap(rp.overlap, m)
        return d

    by_start = {str(s): both(ss & (si == s), "same_start") for s in sorted(set(start.tolist()))}
    pairs = sorted({(min(a, b), max(a, b)) for a, b in zip(si[sb].tolist(), sj[sb].tolist())})
    by_pair = {f"{a}-{b}": both(sb & (np.minimum(si, sj) == a) & (np.maximum(si, sj) == b), "same_batch") for a, b in pairs}
    in_d_i, in_d_j = np.isin(bi, DECIDING), np.isin(bj, DECIDING)
    in_c_i, in_c_j = np.isin(bi, CALIBRATION), np.isin(bj, CALIBRATION)
    run = np.isin(si, RUN_STARTS)
    split = {"within_deciding": both(ss & in_d_i & in_d_j, "same_start"),
             "within_calibration": both(ss & in_c_i & in_c_j & run, "same_start"),
             "across": both(ss & ((in_d_i & in_c_j) | (in_c_i & in_d_j)), "same_start"),
             "within_calibration_pilot_starts": both(ss & in_c_i & in_c_j & ~run, "same_start")}
    return {"same_start_by_start": by_start, "same_batch_by_start_pair": by_pair, "same_start_by_batch_set": split}


# ----------------------------------------------------------------------------- the report


def _f(x: Any, nd: int = 3) -> str:
    if x is None:
        return "n/a"
    x = float(x)
    return "undef" if not np.isfinite(x) else f"{x:.{nd}f}"


def _family_lines(f: str, d: dict[str, Any]) -> list[str]:
    L = []
    for k, g in enumerate(GROUPS):
        x = d[g]
        head = f"  {FAMILY_LABEL[f]:<36} {d['pairs']:>6}" if k == 0 else " " * 45
        if f == "same_start":
            L.append(f"{head}  {GROUP_LABEL[g]:<13} {_f(x['agreement'])}   crossing {_f(x['chance_crossing'])}  kappa {_f(x['kappa_crossing'])}"
                     f"   decile {_f(x['chance_decile'])}  kappa {_f(x['kappa_decile'])}")
        else:
            L.append(f"{head}  {GROUP_LABEL[g]:<13} {_f(x['agreement'])}   independence {_f(x['chance_independence'])}  kappa {_f(x['kappa_independence'])}")
    return L


def _overlap_line(label: str, o: dict[str, Any]) -> str:
    if o["pairs"] == 0:
        return f"  {label:<36} {0:>6}  no pair with saved gradients"
    return (f"  {label:<36} {o['pairs']:>6}  O {o['observed']:7.1f}  E {o['expected']:7.1f}  beyond chance {_f(o['beyond_chance'])}"
            f"  same side among overlapping {_f(o['same_side'])}")


def _breakdown_line(label: str, d: dict[str, Any], f: str) -> str:
    r = d["rank_one"]
    if f == "same_start":
        core = (f"{_f(r['agreement'])}  crossing {_f(r['chance_crossing'])} kappa {_f(r['kappa_crossing'])}  decile {_f(r['chance_decile'])}"
                f" kappa {_f(r['kappa_decile'])}  | kappa (crossing): alive {_f(d['alive']['kappa_crossing'])}, never-needed "
                f"{_f(d['never_needed']['kappa_crossing'])}, delta {_f(d['delta']['kappa_crossing'])}")
    else:
        core = (f"{_f(r['agreement'])}  independence {_f(r['chance_independence'])} kappa {_f(r['kappa_independence'])}  | kappa: alive "
                f"{_f(d['alive']['kappa_independence'])}, never-needed {_f(d['never_needed']['kappa_independence'])}, delta "
                f"{_f(d['delta']['kappa_independence'])}")
    o = d["overlap"]
    ov = (f"  | top 3,000: {o['pairs']} pairs, O {o['observed']:.1f}, E {o['expected']:.1f}, beyond {_f(o['beyond_chance'])}, same side "
          f"{_f(o['same_side'])}") if o["pairs"] else "  | top 3,000: no pair with gradients"
    return f"    {label:<34} {d['pairs']:>5}  {core}{ov}"


def report(rows: dict[str, Any], split: dict[str, Any], inputs: dict[str, Any]) -> str:
    c = inputs["counts"]
    L = ["Agreement between settings (conventions, Section 7, and the addendum's item 3). Description; no line.",
         f"Settings read: {c['run']} run searches (A1-A16, H1-H16 from starts 9-13), {c['starts_test']} starts-test searches "
         f"(C1-C8 from starts 9-13, loaded by name; the guard search not read), {c['pilot']} pilot searches (C1-C8 from starts 1-8, "
         "values only); every file or array matched its recorded SHA-256.",
         f"Entries: {inputs['entries']['rank_one']:,} rank-one ({inputs['entries']['alive']:,} alive, {inputs['entries']['never_needed']:,} "
         f"never-needed) and {inputs['entries']['delta']} delta. Strata file SHA-256 {inputs['strata_sha256']}.",
         "Agree: both below one half or both at or above. Chance levels: independence within the shuffle's 264 strata (different "
         "starts); crossing from the start within the same strata (same start); crossing within start-value decile by alive or "
         "never-needed (same start; the addendum's level, not defined for the 24 delta entries). The delta entries are one group "
         "for the chance levels. Kappa = (mean agreement - mean chance) / (1 - mean chance) over a family's pairs.",
         "Top 3,000: plan 2 of the research log's ranking a_c = G_c (s_c - s0_c) over all 38,936 entries, pairs whose settings both have saved "
         "gradients (starts 9-13); O and E are means over pairs, beyond chance = (O - E)/(3000 - E), the same-side share "
         "pooled over the family's overlapping entries.",
         ""]
    for row in ROWS:
        r = rows[row]
        L.append(f"{ROW_LABEL[row]} ({row}): {r['searches']} settings")
        L.append(f"  {'family':<36} {'pairs':>6}  {'entries':<13} agree   chance level and kappa")
        for f in FAMILIES:
            L += _family_lines(f, r["families"][f])
        L.append("  Top-3,000 overlap:")
        for f in FAMILIES:
            L.append(_overlap_line(FAMILY_LABEL[f], r["families"][f]["overlap"]))
        u = r["same_start_untouched_left_out"]
        left = sum(u["entries_left_out"].values())
        L.append(f"  Same start, entries untouched in both settings left out: {left} entries left out over "
                 f"{r['families']['same_start']['pairs']} pairs ({sum(u['pairs_affected'].values())} pair-groups affected); "
                 + ("these rows equal the first:" if u["equals_first"] else "these rows differ from the first:"))
        d = dict(u["rows"])
        d["pairs"] = r["families"]["same_start"]["pairs"]
        L += _family_lines("same_start", d)
        if row == "n320":
            b = split
            L.append("")
            L.append("  At 320 steps, the same-start family by start (rank-one entries in full; kappa by group; the overlap where defined):")
            for s, d in b["same_start_by_start"].items():
                L.append(_breakdown_line(f"start {s}", d, "same_start"))
            L.append("  At 320 steps, the same-start family by batch set:")
            names = {"within_deciding": "within deciding (starts 9-13)", "within_calibration": "within calibration (starts 9-13)",
                     "across": "across the two (starts 9-13)", "within_calibration_pilot_starts": "within calibration (starts 1-8)"}
            for k, label in names.items():
                L.append(_breakdown_line(label, b["same_start_by_batch_set"][k], "same_start"))
            L.append("  At 320 steps, the different-starts, same-batch family by start pair:")
            for p, d in b["same_batch_by_start_pair"].items():
                L.append(_breakdown_line(f"starts {p}", d, "same_batch"))
        L.append("")
    return "\n".join(L)


def run(searches: list[Search], ent: Entries, starts: dict[int, np.ndarray]) -> tuple[dict[str, Any], dict[str, Any]]:
    dec = {s: decile_codes(s0, ent) for s, s0 in starts.items()}
    rows, split = {}, {}
    for row in ROWS:
        rp = row_pairs(searches, row, ent, dec)
        rows[row] = row_summary(rp)
        if row == "n320":
            split = breakdowns(rp)
    return rows, split


def main() -> int:
    from vpd_audit_2 import s6_record

    lay = P.layout()
    strata, strata_sha = LL.strata_by_module()
    ent = entries(lay, strata)
    sizes = {g: int(ent.cols[g].size) for g in GROUPS}
    if sizes["rank_one"] != N_RANK_ONE or sizes["delta"] != 24 or sizes["alive"] + sizes["never_needed"] != N_RANK_ONE:
        raise Refusal(f"the layout's groups are not the expected sizes: {sizes}")
    searches, inputs = load(lay)
    rows, split = run(searches, ent, inputs["starts"])
    info = {"counts": inputs["counts"], "entries": sizes, "strata_sha256": strata_sha}
    sys.stdout.write(report(rows, split, info) + "\n")
    s6_record.update("agreement", {"inputs": info, "rows": rows, "n320_breakdowns": split})
    return 0


if __name__ == "__main__":
    sys.exit(main())
