"""Session 5, plan 1, Part D: the made-up-data test of the interval.

    uv run python -m vpd_audit_2.lead_madeup [--processes N]                          (the test of record, to results/s5_madeup/)
    uv run python -m vpd_audit_2.lead_madeup --version as_committed [--processes N]   (beside it, to results/s5_madeup/as_committed/)

Implements `freeze/amendment1_specs/interval_spec.md`, Sections 6 to 9, with its erratum, under Amendment 1
(`freeze/amendment1.md`, Section 5 and Section 9, item 7), Amendment 2 (`freeze/amendment2.md`), plan 1 (Sections 7
and 12.2), and plan 3.

Two versions of the generator, differing in a held-out batch's vulnerability alone (Amendment 2): "amended", the test
of record, in which it is log-normal noise; and "as_committed", the generator of Amendment 1, in which it also carries
the batch type's factor. Both use one master seed and the same draws. The version as committed is run in full and
printed in the same layout, with the multiplier each row would have required; it sets none.

Made-up experiments are built on the pilot's 64 real own-batch searches (`results/s4_pilot/part_a/runs.json`, key `a1`;
no other pilot file is read, and the sealed shuffle file stays sealed). Carried-over and shuffled harm are invented,
with a truth known by enumeration, never from a simulated sample:

  - at search-length rows the expectation over the start shift is exact, from the normal probability of each warped
    index (plan 1, Section 12.2, item 4);
  - at harm-level rows it is taken over a grid of 401 start shifts across +/- 4 sigma weighted by the normal density,
    every mean being the expected total over the expected count (the erratum, item 2).

The scenario list is closed: 13 core scenarios (P1 to P13), 8 stress scenarios (T1 to T8, T6 having one set of
experiments for each of its eight values of psi), and 2 checks (G1, G2). The same interval code as the analysis is
used (`lead_intervals.interval`), with the closed form in place of the bootstrap for the batch part, as the
specification's Section 8 lays down. Verdicts and readings come from `lead_reading`.

Pass and fail, the reruns, the repair, and its confirmation are applied mechanically (`judge_core`, `repair`). The
multipliers are written to the results folder only; nothing is written under `freeze/`.

Names follow the specification's erratum, item 3: `type_weight` is w_c, `shuf` is z_ijs, `half_width` is w.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from scipy.special import ndtr

from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_reading as LR
from vpd_audit_2.lead_intervals import Combo, Presence

REPO_ROOT = Path(__file__).resolve().parent.parent
PILOT_RUNS = REPO_ROOT / "results" / "s4_pilot" / "part_a" / "runs.json"
OUT_DIR = REPO_ROOT / "results" / "s5_madeup"

MASTER_SEED = 20261006  # the test of record's master seed (Amendment 2, Section 6); confirmation seeds are streams 2, 3, ... under it
# The generator's two versions (Amendment 2; plan 3, step 2). They differ in one line, a held-out batch's vulnerability:
# "amended", the test of record, has v_j = g_j; "as_committed", the generator of Amendment 1, has v_j = f_c(j) g_j.
# The as-committed version is run in full and printed beside the test of record, and sets no multiplier.
VERSIONS = ("amended", "as_committed")
PERCENTILE_STREAM = 5002  # the 1,000 bootstrap replicates of the percentile interval, fixed once per K
N_EXPERIMENTS = 2_000
N_RERUN = 10_000
GENERATED_CAP_FACTOR = 10  # harm-level rows: experiments are added until 2,000 are read or 20,000 have been generated
CHUNK = 250
N_TYPES, N_PILOT_STARTS, N_STARTS, N_RECORD = 8, 8, 5, 321
C5 = 4  # the early-breakout batch type, pilot batch C5
GRID_POINTS, GRID_SIGMAS = 401, 4.0
S0_DEFAULT = 0.40
SD_VULNERABILITY, SD_CELL, SD_SHUF = 0.1, 0.2, 0.05
JUMP_SEARCH, JUMP_CELL, JUMP_HARM = 0.02, 0.01, 40.0
MISSING_DIVISOR = 8  # a level is read only if at most one eighth of each side's searches are missing

STEP_ROWS = ("n20", "n40", "n80", "n160", "n320")
LEVEL_ROWS = ("h2", "h5", "h10")
ALL_ROWS = STEP_ROWS + LEVEL_ROWS
ROW_STEP = {"n20": 20, "n40": 40, "n80": 80, "n160": 160, "n320": 320}
ROW_LEVEL = {"h2": 2.0, "h5": 5.0, "h10": 10.0}

STATS = ("large", "carries", "depends", "carried_margin", "own_margin", "kappa", "shuffled_vs_yardstick", "carried_added", "pooled_retention")
SIGNED = ("large", "carries", "depends")
PLAIN_MEANS = ("large", "carried_margin", "own_margin", "shuffled_vs_yardstick", "carried_added")
RATIOS = ("carries", "depends", "kappa", "pooled_retention")
FIELDS = ("est", "hw", "vtot", "vc", "nu", "denom_z", "pct_lo", "pct_hi")
F = {name: k for k, name in enumerate(FIELDS)}
S = {name: k for k, name in enumerate(STATS)}

# Amendment 1, Section 5.2, and plan 1, Section 12.2.
COVERAGE_FLOOR, ONE_SIDED_CEILING = 0.925, 0.0375
RERUN_COVERAGE, RERUN_ONE_SIDED = 0.935, 0.0325
MULTIPLIER_GRID, MULTIPLIER_LIMIT = 0.05, 1.5
GUARD_STOP, GUARD_LIST = 5.0, 3.5
ZD_BINS = ((-math.inf, 2.0, "below 2"), (2.0, 3.0, "2 to 3"), (3.0, 5.0, "3 to 5"), (5.0, 8.0, "5 to 8"), (8.0, math.inf, "above 8"))


# ----------------------------------------------------------------------------- scenarios


@dataclass(frozen=True)
class Scenario:
    id: str
    kind: str  # "core", "stress", or "check"
    rho: str  # "const"; "large0", "shuf02", "shuf0" (set per row from the population); "mix5"; "c5"
    rho_value: float = 0.0
    sigma_delta: float = 0.0
    c5_weight: float = 1.0 / 8.0
    rows: tuple[str, ...] = ALL_ROWS
    K: int = 16
    psi: float | None = None  # T6: shuffled harm as a multiple of the own search's mean raw harm
    jump: bool = False  # T5
    forced_missing: bool = False  # T7
    delta_null: bool = False  # T8
    lines: dict[str, float] = field(default_factory=dict)  # signed readings whose truth sits on a line, and the line
    what: str = ""

    @property
    def type_weight(self) -> np.ndarray:
        w = np.full(N_TYPES, (1.0 - self.c5_weight) / (N_TYPES - 1))
        w[C5] = self.c5_weight
        return w


T6_PSI = (0.3, 0.5, 0.7, 0.85, 0.95, 1.0, 1.1, 1.25)


def scenarios() -> list[Scenario]:
    """The closed list of the specification's Section 7."""
    out = [
        Scenario("P1", "core", "const", 0.2, 0.0, lines={"carries": 0.2}, what="retention 0.2, no start effect; tau on its line"),
        Scenario("P2", "core", "const", 0.6, 0.0, what="retention 0.6, no start effect"),
        Scenario("P3", "core", "const", 0.9, 0.0, what="retention 0.9, no start effect"),
        Scenario("P4", "core", "const", 0.2, 0.09, lines={"carries": 0.2}, what="retention 0.2, realistic start effect; tau on its line"),
        Scenario("P5", "core", "const", 0.6, 0.09, what="retention 0.6, realistic start effect"),
        Scenario("P6", "core", "const", 0.9, 0.09, what="retention 0.9, realistic start effect"),
        Scenario("P7", "core", "large0", sigma_delta=0.0, lines={"large": 0.0}, what="\"large\" with its truth at zero"),
        Scenario("P8", "core", "large0", sigma_delta=0.09, lines={"large": 0.0}, what="\"large\" with its truth at zero, start effect"),
        Scenario("P9", "core", "shuf02", sigma_delta=0.0, lines={"depends": 0.2}, what="shuffled ratio with its truth at 0.2"),
        Scenario("P10", "core", "shuf02", sigma_delta=0.09, lines={"depends": 0.2}, what="shuffled ratio with its truth at 0.2, start effect"),
        Scenario("P11", "core", "shuf0", sigma_delta=0.0, lines={"depends": 0.0}, what="shuffled ratio and kappa with their truths at zero"),
        Scenario("P12", "core", "shuf0", sigma_delta=0.09, lines={"depends": 0.0}, what="shuffled ratio and kappa at zero, start effect"),
        Scenario("P13", "core", "mix5", sigma_delta=0.09, what="retention 0.3 under 5 nats of own harm, 0.9 from 5 nats"),
        Scenario("T1", "stress", "const", 0.6, 0.09, c5_weight=1.0 / 16.0, what="type C5 at weight 1/16"),
        Scenario("T2", "stress", "const", 0.6, 0.09, c5_weight=1.0 / 4.0, what="type C5 at weight 1/4"),
        Scenario("T3", "stress", "c5", sigma_delta=0.09, what="retention 0.4 on type-C5 attack batches, 0.8 otherwise"),
        Scenario("T4", "stress", "const", 0.6, 0.25, what="start effect 0.25"),
        Scenario("T5", "stress", "const", 0.6, 0.09, jump=True, what="carried-over cells that jump to 40 nats"),
    ]
    out += [Scenario(f"T6[{psi:g}]", "stress", "const", 0.7, 0.09, rows=("n20", "n80"), psi=psi, what=f"shuffled harm {psi:g} times the own search's")
            for psi in T6_PSI]
    out += [
        Scenario("T7", "stress", "const", 0.7, 0.09, rows=("h5",), forced_missing=True, what="batch-clustered missing searches at 5 nats"),
        Scenario("T8", "stress", "const", 0.7, 0.09, rows=STEP_ROWS, K=8, delta_null=True, what="delta-on run when the delta components do nothing"),
    ]
    return out


def scenario_index() -> dict[str, int]:
    return {s.id: k for k, s in enumerate(scenarios())}


# ----------------------------------------------------------------------------- the pilot's records, and the truth


def load_pilot(path: Path = PILOT_RUNS) -> np.ndarray:
    """R[c, p, t]: the raw harm after t steps of the pilot search on calibration batch C(c+1) from pilot start p+1."""
    a1 = json.load(open(path))["a1"]
    R = np.array([[a1[f"C{c}"][str(p)]["record"] for p in range(1, N_PILOT_STARTS + 1)] for c in range(1, N_TYPES + 1)], dtype=np.float64)
    assert R.shape == (N_TYPES, N_PILOT_STARTS, N_RECORD) and np.isfinite(R).all()
    return R


def warp_index(delta: float) -> np.ndarray:
    """Specification Section 6, step 3: step t of a search under start shift delta reads entry min(320, round(t e^delta))."""
    return np.minimum(N_RECORD - 1, np.rint(np.arange(N_RECORD) * math.exp(delta))).astype(np.int64)


def crossing_step(rec: np.ndarray, level: float) -> np.ndarray:
    """For records [..., 321]: the first step t >= 1 with (rec[t] + rec[t - 1]) / 2 >= level, or -1."""
    hit = 0.5 * (rec[..., 1:] + rec[..., :-1]) >= level
    return np.where(hit.any(axis=-1), hit.argmax(axis=-1) + 1, -1)


def index_probabilities(n: int, sigma: float) -> np.ndarray:
    """P(min(320, round(n e^delta)) = m) for m = 0..320, with delta normal(0, sigma^2): exact."""
    p = np.zeros(N_RECORD)
    if sigma == 0.0:
        p[n] = 1.0
        return p
    edges = ndtr(np.log((np.arange(N_RECORD - 1) + 0.5) / n) / sigma)  # P(n e^delta < m + 0.5), m = 0..319
    p[0] = edges[0]
    p[1:-1] = np.diff(edges)
    p[-1] = 1.0 - edges[-1]
    return p


def type_factor(R: np.ndarray, type_weight: np.ndarray) -> np.ndarray:
    """f_c: a type's mean added harm at 20 steps (unwarped, over its 8 pilot starts) over the weighted mean over types."""
    mean20 = (R[:, :, 20] - R[:, :, 0]).mean(axis=1)
    return mean20 / float(type_weight @ mean20)


def _rho_cells(scn: Scenario, raw: np.ndarray) -> np.ndarray | None:
    """The retention of a setting from a search of each (type, pilot start), given its own raw harm [8, 8]; None when
    the scenario sets one retention per row from the population."""
    if scn.rho == "const":
        return np.full(raw.shape, scn.rho_value)
    if scn.rho == "mix5":
        return np.where(raw < 5.0, 0.3, 0.9)
    if scn.rho == "c5":
        out = np.full(raw.shape, 0.8)
        out[C5] = 0.4
        return out
    return None


def population(R: np.ndarray, scn: Scenario) -> dict[str, dict[str, Any]]:
    """Per row: the population means of the specification's Section 6 and the true value of every statistic."""
    w = (scn.type_weight / N_PILOT_STARTS)[:, None]  # the weight of each (type, pilot start)
    mu_k = float((w * R[:, :, 0]).sum())
    out: dict[str, dict[str, Any]] = {}
    for row in scn.rows:
        if row in ROW_STEP:
            p_n, p_20 = index_probabilities(ROW_STEP[row], scn.sigma_delta), index_probabilities(20, scn.sigma_delta)
            mu_Y = float((w * (R @ p_n)).sum())
            mu_q = float((w * (R @ p_20)).sum())
            mu_O = mu_Y - mu_k
            share = 1.0
            # the expectation of rho * (own added harm), index by index, since rho may depend on the own raw harm
            mu_C = 0.0
            if scn.rho in ("const", "mix5", "c5"):
                for m in np.flatnonzero(p_n):
                    raw = R[:, :, m]
                    mu_C += p_n[m] * float((w * _rho_cells(scn, raw) * (raw - R[:, :, 0])).sum())
        else:
            level = ROW_LEVEL[row]
            if scn.sigma_delta == 0.0:
                grid, weight = np.array([0.0]), np.array([1.0])
            else:
                grid = np.linspace(-GRID_SIGMAS * scn.sigma_delta, GRID_SIGMAS * scn.sigma_delta, GRID_POINTS)
                weight = np.exp(-0.5 * (grid / scn.sigma_delta) ** 2)
                weight /= weight.sum()
            count = tot_Y = tot_O = tot_C = tot_q = 0.0
            for d, wd in zip(grid, weight):
                Rw = R[:, :, warp_index(float(d))]
                step = crossing_step(Rw, level)
                there = step != -1
                raw = np.take_along_axis(Rw, np.where(there, step, 0)[..., None], axis=-1)[..., 0]
                present = float((w * there).sum())  # the share of searches present at this start shift
                count += wd * present
                tot_Y += wd * float((w * there * raw).sum())
                tot_O += wd * float((w * there * (raw - Rw[:, :, 0])).sum())
                rho = _rho_cells(scn, raw)
                if rho is not None:
                    tot_C += wd * float((w * there * rho * (raw - Rw[:, :, 0])).sum())
                tot_q += wd * present * float((w * Rw[:, :, 20]).sum())  # the yardstick, weighted by the share present
            share = count
            mu_Y, mu_O, mu_C, mu_q = tot_Y / count, tot_O / count, tot_C / count, tot_q / count
        S0 = S0_DEFAULT if scn.psi is None else scn.psi * mu_Y
        rho_row = None
        if scn.rho == "large0":
            rho_row = (mu_q - mu_k) / mu_O
        elif scn.rho == "shuf02":
            rho_row = (S0 + 0.2 * (mu_Y - S0) - mu_k) / mu_O
        elif scn.rho == "shuf0":
            rho_row = (S0 - mu_k) / mu_O
        if rho_row is not None:
            mu_C = rho_row * mu_O
        if scn.jump:  # plan 1, Section 7: the jump's effect on every truth that uses mu_C
            mu_C = (1 - JUMP_SEARCH) * (1 - JUMP_CELL) * mu_C + (1 - (1 - JUMP_SEARCH) * (1 - JUMP_CELL)) * (JUMP_HARM - mu_k)
        out[row] = {"mu_k": float(mu_k), "mu_q": float(mu_q), "mu_Y": float(mu_Y), "mu_O": float(mu_O), "mu_C": float(mu_C), "S0": float(S0),
                    "rho_row": None if rho_row is None else float(rho_row), "share_present": float(share),
                    "truth": true_values(float(mu_k), float(mu_q), float(mu_Y), float(mu_O), float(mu_C), float(S0))}
    return out


def true_values(mu_k: float, mu_q: float, mu_Y: float, mu_O: float, mu_C: float, S0: float) -> dict[str, float | None]:
    """The true value of each statistic from the population means (the specification's Section 6, and plan 1, Section 7,
    for the three statistics the output specification adds). `mu_O` is the mean own added harm, the specification's
    mu_{Y+}. Pooled retention has the carry-over ratio's truth, since the generator draws both sides from one population."""
    return {
        "large": mu_k + mu_C - mu_q,
        "carries": mu_C / mu_O,
        "depends": (mu_k + mu_C - S0) / (mu_Y - S0) if mu_Y != S0 else None,
        "carried_margin": mu_k + mu_C - S0,
        "own_margin": mu_Y - S0,
        "kappa": (mu_k + mu_C - S0) / mu_C,
        "shuffled_vs_yardstick": S0 - mu_q,
        "carried_added": mu_C,
        "pooled_retention": mu_C / mu_O,
    }


# ----------------------------------------------------------------------------- one made-up experiment


def lognormal_unit(rng: np.random.Generator, sd: float, size: Any) -> np.ndarray:
    """A log-normal with mean 1 and standard deviation `sd`: exp(N(-l^2 / 2, l^2)), l^2 = ln(1 + sd^2)."""
    l2 = math.log(1.0 + sd * sd)
    return np.exp(rng.normal(-0.5 * l2, math.sqrt(l2), size))


def experiment_rng(master: int, seed_no: int, phase: int, scenario_no: int, experiment: int) -> np.random.Generator:
    """One generator per experiment, so that a run does not depend on how experiments are shared among processes.
    `seed_no` 1 is the test's master seed, 2 and up its confirmation seeds; `phase` 0 is the 2,000, 1 the rerun.
    The generator's version is not part of the seed: both versions are compared on the same draws."""
    return np.random.default_rng([master, seed_no, phase, scenario_no, experiment])


def draw_searches(rng: np.random.Generator, R: np.ndarray, scn: Scenario, version: str = "amended") -> dict[str, Any]:
    """Steps 1 to 5 of the specification's Section 6: batch types, searches, the shared start effect, the warped
    records, and each held-out batch's vulnerability, which is the log-normal noise alone in the amended version and
    carries the batch type's factor in the version as committed."""
    assert version in VERSIONS
    K = scn.K
    types_A = rng.choice(N_TYPES, size=K, p=scn.type_weight)
    types_H = rng.choice(N_TYPES, size=K, p=scn.type_weight)
    starts_A = np.stack([rng.permutation(N_PILOT_STARTS)[:N_STARTS] for _ in range(K)])
    starts_H = np.stack([rng.permutation(N_PILOT_STARTS)[:N_STARTS] for _ in range(K)])
    delta = scn.sigma_delta * rng.standard_normal(N_STARTS)
    g = lognormal_unit(rng, SD_VULNERABILITY, K)
    idx = np.stack([warp_index(float(d)) for d in delta])  # [n_s, 321]
    v = g if version == "amended" else type_factor(R, scn.type_weight)[types_H] * g
    return {"types_A": types_A, "types_H": types_H, "starts_A": starts_A, "starts_H": starts_H, "delta": delta, "idx": idx,
            "rec_A": warped(R, types_A, starts_A, idx), "rec_H": warped(R, types_H, starts_H, idx), "v": v, "g": g}


def warped(R: np.ndarray, types: np.ndarray, starts: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """The warped record of every search: [K, n_s, 321]."""
    return R[types[:, None, None], starts[:, :, None], idx[None, :, :]]


def setting_of(rec: np.ndarray, row: str) -> tuple[np.ndarray, np.ndarray]:
    """Each search's setting at a row: whether it has one, and its own raw harm (NaN where it has none)."""
    if row in ROW_STEP:
        return np.ones(rec.shape[:2], dtype=bool), rec[:, :, ROW_STEP[row]].copy()
    step = crossing_step(rec, ROW_LEVEL[row])
    there = step != -1
    raw = np.take_along_axis(rec, np.where(there, step, 0)[..., None], axis=-1)[..., 0]
    return there, np.where(there, raw, np.nan)


def row_cells(rng: np.random.Generator, scn: Scenario, pop_row: dict[str, Any], s: dict[str, Any], row: str,
              rec_A: np.ndarray | None = None, rec_H: np.ndarray | None = None) -> dict[str, Any]:
    """Steps 4, 6, and 7: one row's arrays in the names of the output specification's Section 2.1, with the mean of a
    cell's shuffled copies given directly (`shuffled_mean`)."""
    K = scn.K
    rec_A = s["rec_A"] if rec_A is None else rec_A
    rec_H = s["rec_H"] if rec_H is None else rec_H
    a, own_A = setting_of(rec_A, row)
    b, own = setting_of(rec_H, row)
    start, own20, attack_start = rec_H[:, :, 0], rec_H[:, :, 20], rec_A[:, :, 0]
    added_A = own_A - attack_start
    if scn.rho == "mix5":
        rho = np.where(own_A < 5.0, 0.3, 0.9)
    elif scn.rho == "c5":
        rho = np.where(s["types_A"] == C5, 0.4, 0.8)[:, None] * np.ones((1, N_STARTS))
    elif scn.rho == "const":
        rho = np.full((K, N_STARTS), scn.rho_value)
    else:
        rho = np.full((K, N_STARTS), pop_row["rho_row"])
    cell_noise = lognormal_unit(rng, SD_CELL, (K, K, N_STARTS))
    shuf_noise = lognormal_unit(rng, SD_SHUF, (K, K, N_STARTS))
    v = s["v"][None, :, None]
    carried = start[None, :, :] + v * cell_noise * (rho * added_A)[:, None, :]
    if scn.jump:
        whole = rng.random((K, N_STARTS)) < JUMP_SEARCH  # an attack search that carries 40 raw nats to every held-out batch
        single = rng.random((K, K, N_STARTS)) < JUMP_CELL  # each remaining cell
        carried = np.where(whole[:, None, :] | single, JUMP_HARM, carried)
    shuf = pop_row["S0"] * v * shuf_noise
    carried = np.where(a[:, None, :], carried, np.nan)
    shuf = np.where(a[:, None, :], shuf, np.nan)
    out = {"table": "step" if row in ROW_STEP else "level", "key": ROW_STEP.get(row, ROW_LEVEL.get(row)),
           "start": start, "own": own, "own20": own20, "carried": carried, "shuffled_mean": shuf, "shuffled": None,
           "attack_start": attack_start, "attack_own": own_A, "attack_present": a, "heldout_present": b}
    if scn.forced_missing:  # T7: one attack batch, and the 5 held-out searches with the lowest mean carried-over harm
        a = a.copy()
        a[int(rng.integers(K))] = False
        there = a[:, None, :] & np.ones((1, K, 1), dtype=bool)
        mean_carried = np.where(there, carried, 0.0).sum(axis=0) / np.maximum(there.sum(axis=0), 1)  # [K_H, n_s]
        lowest = np.argsort(mean_carried, axis=None, kind="stable")[:5]
        b = b.copy()
        b.reshape(-1)[lowest] = False
        out.update(attack_present=a, heldout_present=b, carried=np.where(a[:, None, :], carried, np.nan),
                   shuffled_mean=np.where(a[:, None, :], shuf, np.nan), attack_own=np.where(a, own_A, np.nan), own=np.where(b, own, np.nan))
    return out


def level_is_read(arrays: dict[str, Any]) -> bool:
    """The signed count rule: a level is read unless more than one eighth of either side's searches are missing."""
    a, b = arrays["attack_present"], arrays["heldout_present"]
    return bool((~a).sum() * MISSING_DIVISOR <= a.size and (~b).sum() * MISSING_DIVISOR <= b.size)


def row_statistics(arrays: dict[str, Any], indices: LI.BootstrapIndices | None) -> np.ndarray:
    """Every statistic's estimate and interval for one row, [9, 8] in the order of STATS and FIELDS, by the analysis's
    own code with the closed form for the batch part. NaN where a statistic is undefined."""
    pres = LR.presence_of(arrays)
    stats = LR.nine_statistics(arrays)
    out = np.full((len(STATS), len(FIELDS)), np.nan)
    res = {}
    for name in STATS:
        r = LI.interval(*stats[name], pres, indices=indices, batch_part="closed_form", percentile=indices is not None, denominator_distance=False)
        res[name] = r
        if not r["defined"]:
            continue
        k = S[name]
        out[k, F["est"]], out[k, F["hw"]] = r["estimate"], r["half_width_unwidened"]
        out[k, F["vtot"]], out[k, F["vc"]], out[k, F["nu"]] = r["v_pb"] + r["v_c"], r["v_c"], r["nu"]
        if r["interval_percentile"] is not None:
            out[k, F["pct_lo"]], out[k, F["pct_hi"]] = r["interval_percentile"]
    # each ratio's denominator over its unwidened standard error, as a plain mean
    dens = {"depends": res["own_margin"], "kappa": res["carried_added"],
            "carries": LI.interval(stats["carries"][1], None, pres, batch_part="closed_form", percentile=False),
            "pooled_retention": LI.interval(stats["pooled_retention"][1], None, pres, batch_part="closed_form", percentile=False)}
    for name, d in dens.items():
        if d["defined"] and d["standard_error"] > 0:
            out[S[name], F["denom_z"]] = d["estimate"] / d["standard_error"]
    return out


def both_reached(arrays: dict[str, Any]) -> tuple[float, float]:
    """The draft's alternative, which the specification's Section 5.4 rejects and scenario T7 prints beside the
    convention: the carry-over ratio and the "large" difference over the triples where both searches reached the level."""
    both = arrays["attack_present"][:, None, :] & arrays["heldout_present"][None, :, :]
    n = both.sum()
    if n == 0:
        return float("nan"), float("nan")
    k, q, y = arrays["start"][None], arrays["own20"][None], arrays["own"][None]
    num = np.where(both, arrays["carried"] - k, 0.0).sum() / n
    den = np.where(both, y - k, 0.0).sum() / n
    large = np.where(both, arrays["carried"] - q, 0.0).sum() / n
    return (float(num / den) if den != 0 else float("nan")), float(large)


def delta_null_shares(rng: np.random.Generator, R: np.ndarray, scn: Scenario, pop: dict[str, Any], s: dict[str, Any], row: str,
                      lead: dict[str, Any], redraw: dict[str, np.ndarray]) -> np.ndarray:
    """T8: the two paired shares, delta-on over lead, under a null in which the delta components do nothing, in two
    versions: (a) the same searches with fresh cell noise; (b) every search redrawn from its batch type's pilot
    starts. Returns [version, share, (estimate, half-width)], shares in the order carried-over, own-search."""
    out = np.full((2, 2, 2), np.nan)
    pres = LR.presence_of(lead)
    for v, (rec_A, rec_H) in enumerate(((None, None), (redraw["rec_A"], redraw["rec_H"]))):
        delta = row_cells(rng, scn, pop[row], s, row, rec_A, rec_H)
        shares = (
            (Combo(a_cells=delta["carried"] - delta["start"][None]), Combo(a_cells=lead["carried"] - lead["start"][None])),
            (Combo(h_cells=delta["own"] - delta["start"]), Combo(h_cells=lead["own"] - lead["start"])),
        )
        for k, (num, den) in enumerate(shares):
            r = LI.interval(num, den, pres, batch_part="closed_form", percentile=False, denominator_distance=False)
            if r["defined"]:
                out[v, k] = r["estimate"], r["half_width_unwidened"]
    return out


_WORKER: dict[str, Any] = {}


def _worker_state() -> dict[str, Any]:
    if not _WORKER:
        R = load_pilot()
        scns = scenarios()
        _WORKER.update(R=R, scenarios={s.id: s for s in scns}, number={s.id: k for k, s in enumerate(scns)},
                       population={s.id: population(R, s) for s in scns},
                       percentile={K: LI.make_indices(K, B=1000, stream=PERCENTILE_STREAM) for K in (16,)})
    return _WORKER


def simulate(task: tuple[str, str, int, int, int, int, int, tuple[str, ...], int]) -> dict[str, Any]:
    """Experiments [e0, e1) of one scenario in one version of the generator, under one seed and phase, with the
    intervals of the rows asked for. Every row's cells are always drawn, in the scenario's row order, so an experiment
    is the same whatever is asked. A harm-level row's intervals are computed where the level is read and, for the
    experiments numbered below `all_below`, also where it is not (plan 3, step 7)."""
    scn_id, version, master, seed_no, phase, e0, e1, wanted, all_below = task
    st = _worker_state()
    R, scn, pop = st["R"], st["scenarios"][scn_id], st["population"][scn_id]
    indices = st["percentile"].get(scn.K) if scn.kind == "core" else None
    n = e1 - e0
    out: dict[str, Any] = {"task": task, "rows": {}}
    for row in wanted:  # `vals` holds one entry per experiment marked in `has`, in order
        out["rows"][row] = {"vals": [], "has": np.zeros(n, dtype=bool), "read": np.zeros(n, dtype=bool), "missing": np.zeros((n, 2), dtype=np.int32)}
    if scn.id == "T3":
        out["c5_counts"] = np.zeros((n, 2), dtype=np.int32)
    if scn.forced_missing:
        out["both_reached"] = np.full((n, 2), np.nan)
    if scn.delta_null:
        out["shares"] = {row: np.full((n, 2, 2, 2), np.nan) for row in wanted}
    for k, e in enumerate(range(e0, e1)):
        rng = experiment_rng(master, seed_no, phase, st["number"][scn_id], e)
        s = draw_searches(rng, R, scn, version)
        if scn.id == "T3":
            out["c5_counts"][k] = (s["types_A"] == C5).sum(), (s["types_H"] == C5).sum()
        redraw = None
        if scn.delta_null:
            starts_A = np.stack([rng.permutation(N_PILOT_STARTS)[:N_STARTS] for _ in range(scn.K)])
            starts_H = np.stack([rng.permutation(N_PILOT_STARTS)[:N_STARTS] for _ in range(scn.K)])
            redraw = {"rec_A": warped(R, s["types_A"], starts_A, s["idx"]), "rec_H": warped(R, s["types_H"], starts_H, s["idx"])}
        for row in scn.rows:
            arrays = row_cells(rng, scn, pop[row], s, row)
            if row in wanted:
                slot = out["rows"][row]
                slot["missing"][k] = (~arrays["attack_present"]).sum(), (~arrays["heldout_present"]).sum()
                slot["read"][k] = row in ROW_STEP or level_is_read(arrays)
                if slot["read"][k] or e < all_below:
                    slot["has"][k] = True
                    slot["vals"].append(row_statistics(arrays, indices))
                if slot["read"][k] and scn.forced_missing:
                    out["both_reached"][k] = both_reached(arrays)
            if scn.delta_null:  # drawn for every row, asked for or not, so that an experiment is always the same
                shares = delta_null_shares(rng, R, scn, pop, s, row, arrays, redraw)
                if row in wanted:
                    out["shares"][row][k] = shares
    for slot in out["rows"].values():
        slot["vals"] = np.stack(slot["vals"]) if slot["vals"] else np.zeros((0, len(STATS), len(FIELDS)))
    return out


# ----------------------------------------------------------------------------- samples


@dataclass
class RowSample:
    """One scenario's row under one seed and phase: the experiments it is judged on, in order."""

    vals: np.ndarray  # [n, 9, 8]: the experiments the row is judged on
    generated: int
    read: int
    mean_missing: tuple[float, float]
    experiments: np.ndarray  # the experiment numbers judged
    vals_all: np.ndarray  # [n_target, 9, 8]: the first experiments generated, whether the level is read or not
    extra: dict[str, np.ndarray] = field(default_factory=dict)


def collect(pool: Any, scn: Scenario, version: str, master: int, seed_no: int, phase: int, n_target: int,
            rows: tuple[str, ...] | None = None) -> dict[str, RowSample]:
    """Run a scenario until each row asked for has `n_target` experiments in which it is read, or, for a harm-level
    row, until `GENERATED_CAP_FACTOR * n_target` experiments have been generated. The first `n_target` experiments
    serve every row; further ones are generated in rounds of `n_target` for the level rows still short."""
    rows = scn.rows if rows is None else rows
    parts: dict[str, list[dict[str, Any]]] = {row: [] for row in rows}
    chunks: dict[str, list[dict[str, Any]]] = {row: [] for row in rows}
    need = list(rows)
    e0 = 0
    while need and e0 < GENERATED_CAP_FACTOR * n_target:
        tasks = [(scn.id, version, master, seed_no, phase, a, min(a + CHUNK, e0 + n_target), tuple(need), n_target)
                 for a in range(e0, e0 + n_target, CHUNK)]
        for res in pool.map(simulate, tasks):
            for row in need:
                parts[row].append(res["rows"][row])
                chunks[row].append(res)
        e0 += n_target
        need = [row for row in need if row in ROW_LEVEL and sum(int(p["read"].sum()) for p in parts[row]) < n_target]
    out: dict[str, RowSample] = {}
    for row in rows:
        read = np.concatenate([p["read"] for p in parts[row]])
        has = np.concatenate([p["has"] for p in parts[row]])
        vals = np.concatenate([p["vals"] for p in parts[row]])  # one entry per experiment marked in `has`, in order
        where = np.cumsum(has) - 1  # an experiment's place in `vals`
        missing = np.concatenate([p["missing"] for p in parts[row]])
        keep = np.flatnonzero(read)[:n_target]  # the experiments the row is judged on
        first = np.flatnonzero(has[:n_target])  # the first experiments generated, read or not
        generated = int(keep[-1]) + 1 if keep.size == n_target else int(read.size)
        extra: dict[str, np.ndarray] = {}
        for name in ("c5_counts", "both_reached"):
            if name in chunks[row][0]:
                extra[name] = np.concatenate([res[name] for res in chunks[row]])[keep]
        if "shares" in chunks[row][0]:
            extra["shares"] = np.concatenate([res["shares"][row] for res in chunks[row]])[keep]
        out[row] = RowSample(vals=vals[where[keep]], generated=generated, read=int(read[:generated].sum()),
                             mean_missing=(float(missing[:generated, 0].mean()), float(missing[:generated, 1].mean())),
                             experiments=keep, vals_all=vals[where[first]], extra=extra)
    return out


# ----------------------------------------------------------------------------- the criterion and the repair


def cell_errors(sample: RowSample, stat: str, truth: float, every_experiment: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """d = estimate - truth and the unwidened half-width w, over the experiments in which the statistic is defined:
    those the row is judged on, or, with `every_experiment`, the first experiments generated whether or not the count
    rule lets the level be read (description only; plan 3, step 7)."""
    vals = sample.vals_all if every_experiment else sample.vals
    est, hw = vals[:, S[stat], F["est"]], vals[:, S[stat], F["hw"]]
    ok = np.isfinite(est) & np.isfinite(hw)
    return est[ok] - truth, hw[ok]


def judge(d: np.ndarray, w: np.ndarray, multiplier: float = 1.0) -> dict[str, float]:
    """Coverage, and the shares of intervals lying wholly above and wholly below the truth."""
    n = d.size
    return {"n": int(n), "coverage": float((np.abs(d) <= multiplier * w).mean()), "above": float((d > multiplier * w).mean()),
            "below": float((d < -multiplier * w).mean())}


def needs_rerun(j: dict[str, float], on_line: bool) -> bool:
    """Amendment 1, Section 5.2: coverage under 93.5 percent, or more than 3.25 percent wholly on one side of the line."""
    return j["coverage"] < RERUN_COVERAGE or (on_line and (j["above"] > RERUN_ONE_SIDED or j["below"] > RERUN_ONE_SIDED))


def fails(j: dict[str, float], on_line: bool) -> bool:
    """Coverage below 92.5 percent, or, with the truth on a line, more than 3.75 percent wholly on one side of it."""
    return j["coverage"] < COVERAGE_FLOOR or (on_line and (j["above"] > ONE_SIDED_CEILING or j["below"] > ONE_SIDED_CEILING))


def multiplier_needed(d: np.ndarray, w: np.ndarray, on_line: bool) -> float:
    """Step 1 of the repair: the 95th percentile of |d| / w and, with the truth on a line, also the 96.25th percentiles
    of d / w and of -d / w; the largest."""
    ok = w > 0
    r = d[ok] / w[ok]
    need = float(np.percentile(np.abs(r), 95.0))
    if on_line:
        need = max(need, float(np.percentile(r, 96.25)), float(np.percentile(-r, 96.25)))
    return need


def round_up_to_grid(x: float) -> float:
    return round(math.ceil(x / MULTIPLIER_GRID - 1e-9) * MULTIPLIER_GRID, 2)


def core_cells(scns: list[Scenario]) -> list[tuple[str, str, str]]:
    """Each core scenario, at each row, for each of the three signed readings ("large" not at 20 steps)."""
    return [(s.id, row, stat) for s in scns if s.kind == "core" for row in s.rows for stat in SIGNED if not (stat == "large" and row == "n20")]


class Test:
    """The samples of one run, generated on demand and kept: (seed, phase, scenario) -> row -> RowSample."""

    def __init__(self, pool: Any, n: int = N_EXPERIMENTS, n_rerun: int = N_RERUN, log: Any = None, version: str = "amended",
                 master: int = MASTER_SEED) -> None:
        assert version in VERSIONS
        self.pool, self.n, self.n_rerun, self.version, self.master = pool, n, n_rerun, version, master
        self.scenarios = {s.id: s for s in scenarios()}
        R = load_pilot()
        self.population = {s.id: population(R, s) for s in self.scenarios.values()}
        self.samples: dict[tuple[int, int, str], dict[str, RowSample]] = {}
        self.log = log or (lambda *a: None)

    def truth(self, scn_id: str, row: str, stat: str) -> float | None:
        return self.population[scn_id][row]["truth"][stat]

    def sample(self, seed_no: int, phase: int, scn_id: str, rows: tuple[str, ...] | None = None) -> dict[str, RowSample]:
        key = (seed_no, phase, scn_id)
        have = self.samples.setdefault(key, {})
        scn = self.scenarios[scn_id]
        want = tuple(r for r in (scn.rows if rows is None else rows) if r not in have)
        if want:
            t0 = time.time()
            have.update(collect(self.pool, scn, self.version, self.master, seed_no, phase, self.n if phase == 0 else self.n_rerun, want))
            self.log(f"  {scn_id} seed {seed_no} {'rerun' if phase else 'first'} rows {','.join(want)}: {time.time() - t0:.0f} s")
        return have

    def judge_cells(self, seed_no: int, cells: list[tuple[str, str, str]], multiplier: dict[str, float] | None = None) -> list[dict[str, Any]]:
        """Judge core cells under one seed, each row at its multiplier. The first experiments of every scenario and row
        involved are generated together, then every rerun a scenario needs, so that no experiment is generated twice."""
        multiplier = multiplier or {}
        by_scenario: dict[str, set[str]] = {}
        for scn_id, row, _ in cells:
            by_scenario.setdefault(scn_id, set()).add(row)
        for scn_id, rows in by_scenario.items():
            self.sample(seed_no, 0, scn_id, tuple(r for r in self.scenarios[scn_id].rows if r in rows))
        rerun: dict[str, set[str]] = {}
        for scn_id, row, stat in cells:
            d, w = cell_errors(self.samples[(seed_no, 0, scn_id)][row], stat, self.truth(scn_id, row, stat))
            if needs_rerun(judge(d, w, multiplier.get(row, 1.0)), stat in self.scenarios[scn_id].lines):
                rerun.setdefault(scn_id, set()).add(row)
        for scn_id, rows in rerun.items():
            self.sample(seed_no, 1, scn_id, tuple(r for r in self.scenarios[scn_id].rows if r in rows))
        return [self.judged(seed_no, scn_id, row, stat, multiplier.get(row, 1.0)) for scn_id, row, stat in cells]

    def judged(self, seed_no: int, scn_id: str, row: str, stat: str, multiplier: float = 1.0) -> dict[str, Any]:
        """One core cell under one seed: judged on its 2,000, or, if that triggers a rerun, on the rerun's 10,000 alone,
        by both criteria. The multiplier a cell needs comes from the sample it was judged on."""
        on_line = stat in self.scenarios[scn_id].lines
        truth = self.truth(scn_id, row, stat)
        sample = self.sample(seed_no, 0, scn_id, (row,))[row]
        d, w = cell_errors(sample, stat, truth)
        first = judge(d, w, multiplier)
        rerun = needs_rerun(first, on_line)
        final = first
        if rerun:
            sample = self.sample(seed_no, 1, scn_id, (row,))[row]
            d, w = cell_errors(sample, stat, truth)
            final = judge(d, w, multiplier)
        out = {"scenario": scn_id, "row": row, "statistic": stat, "line": self.scenarios[scn_id].lines.get(stat), "seed": seed_no,
               "multiplier": multiplier, "first": first, "rerun": rerun, "judged_on": final["n"], **{k: final[k] for k in ("coverage", "above", "below")},
               "fail": fails(final, on_line), "multiplier_needed": multiplier_needed(d, w, on_line)}
        if row in ROW_LEVEL:  # description beside the criterion: every experiment of the same sample, read or not
            out["all_experiments"] = judge(*cell_errors(sample, stat, truth, every_experiment=True), multiplier)
            out["share_read"] = sample.read / sample.generated
        return out


def repair(test: Test, cells: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Amendment 1, Section 5.3: a row whose core cells all pass keeps a multiplier of 1; otherwise the largest
    multiplier its core cells need, rounded up to a multiple of 0.05, confirmed on fresh experiments from a second
    seed, raised by 0.05 with a fresh seed each time a cell still fails, until every core cell of the row passes or
    the multiplier exceeds 1.5, when the row goes to the PI."""
    rows: dict[str, dict[str, Any]] = {}
    first_try: dict[str, float] = {}
    for row in ALL_ROWS:
        mine = [c for c in cells if c["row"] == row]
        if any(c["fail"] for c in mine):
            first_try[row] = max(round_up_to_grid(max(c["multiplier_needed"] for c in mine)), 1.0 + MULTIPLIER_GRID)
    # the second seed's experiments for every failing row, generated together
    test.judge_cells(2, [(c["scenario"], c["row"], c["statistic"]) for c in cells if c["row"] in first_try and first_try[c["row"]] <= MULTIPLIER_LIMIT + 1e-9],
                     first_try)
    for row in ALL_ROWS:
        mine = [c for c in cells if c["row"] == row]
        failed = [f"{c['scenario']} {c['statistic']}" for c in mine if c["fail"]]
        entry: dict[str, Any] = {"multiplier": 1.0, "failed_cells": failed, "largest_needed": max(c["multiplier_needed"] for c in mine),
                                 "confirmation": [], "to_pi": False}
        if failed:
            lam = first_try[row]
            seed_no = 2
            while True:
                if lam > MULTIPLIER_LIMIT + 1e-9:
                    entry["to_pi"] = True
                    break
                again = test.judge_cells(seed_no, [(c["scenario"], row, c["statistic"]) for c in mine], {row: lam})
                still = [f"{c['scenario']} {c['statistic']}" for c in again if c["fail"]]
                entry["confirmation"].append({"seed": seed_no, "multiplier": lam, "passed": not still, "failed_cells": still,
                                              "lowest_coverage": min(c["coverage"] for c in again),
                                              "cells": [{k: c[k] for k in ("scenario", "statistic", "coverage", "above", "below", "rerun", "judged_on", "fail")} for c in again]})
                if not still:
                    break
                lam = round(lam + MULTIPLIER_GRID, 2)
                seed_no += 1
            entry["multiplier"] = lam
        rows[row] = entry
    return rows


# ----------------------------------------------------------------------------- the report's lines


def _pct(x: np.ndarray, q: float) -> float | None:
    return float(np.percentile(x, q)) if x.size else None


def report_line(scn: Scenario, row: str, stat: str, sample: RowSample, truth: float | None) -> dict[str, Any]:
    """One line of the specification's Section 9 for a scenario, row, and statistic."""
    v = sample.vals[:, S[stat], :]
    ok = np.isfinite(v[:, F["est"]]) & np.isfinite(v[:, F["hw"]])
    est, hw, vtot, vc, nu = (v[ok, F[name]] for name in ("est", "hw", "vtot", "vc", "nu"))
    line: dict[str, Any] = {"scenario": scn.id, "kind": scn.kind, "row": row, "statistic": stat, "truth": truth, "n": int(ok.sum()),
                            "undefined": int((~ok).sum()), "judged_for_pass": scn.kind == "core" and stat in SIGNED and not (stat == "large" and row == "n20"),
                            "line": scn.lines.get(stat)}
    if row in ROW_LEVEL:
        line.update(generated=sample.generated, share_read=sample.read / sample.generated,
                    mean_missing_attack=sample.mean_missing[0], mean_missing_heldout=sample.mean_missing[1])
    if not ok.any():
        return line
    mc_var = float(est.var(ddof=1)) if est.size > 1 else float("nan")
    line.update(mean_estimate=float(est.mean()), mc_sd=math.sqrt(mc_var) if mc_var == mc_var else None,
                variance_ratio=float(vtot.mean() / mc_var) if mc_var and mc_var == mc_var else None,
                half_width_p5=_pct(hw, 5), half_width_p50=_pct(hw, 50), half_width_p95=_pct(hw, 95),
                share_vc_zero=float((vc == 0).mean()), share_start_over_half=float((vc > 0.5 * vtot).mean()), mean_nu=float(nu.mean()))
    if stat in RATIOS:
        z = v[ok, F["denom_z"]]
        line["median_denominator_distance"] = float(np.median(z[np.isfinite(z)])) if np.isfinite(z).any() else None
    if truth is None:
        line.update(bias=None, coverage=None, above=None, below=None, multiplier_needed=None)
    else:
        d = est - truth
        on_line = stat in scn.lines
        j = judge(d, hw)
        line.update(bias=float(d.mean()), coverage=j["coverage"], above=j["above"], below=j["below"], multiplier_needed=multiplier_needed(d, hw, on_line))
        if row in ROW_LEVEL:  # description: every one of the first experiments, whether the level is read or not
            d_all, w_all = cell_errors(sample, stat, truth, every_experiment=True)
            if d_all.size:
                ja = judge(d_all, w_all)
                line.update(all_experiments={"n": ja["n"], "coverage": ja["coverage"], "above": ja["above"], "below": ja["below"],
                                             "bias": float(d_all.mean())})
        if scn.kind == "core":
            lo, hi = v[ok, F["pct_lo"]], v[ok, F["pct_hi"]]
            has = np.isfinite(lo) & np.isfinite(hi)
            line["percentile_coverage"] = float(((lo[has] <= truth) & (truth <= hi[has])).mean()) if has.any() else None
    L, U = est - hw, est + hw
    if stat in scn.lines:
        verdict = np.array([LR.verdict_large(a, b) if stat == "large" else LR.verdict_ratio(a, b) for a, b in zip(L, U)])
        line["verdict_frequency"] = {word: float((verdict == word).mean()) for word in ("yes", "no", "undetermined")}
    if stat == "depends":
        line["reading_frequency"] = reading_frequency(L, U)
    return line


def reading_frequency(L: np.ndarray, U: np.ndarray) -> dict[str, float]:
    """The frequency of each of the four signed readings and of "no reading defined"."""
    reading = np.array([LR.shuffled_reading(a, b) for a, b in zip(L, U)])
    return {code: float((reading == code).mean()) if reading.size else 0.0 for code in ("a", "b", "c", "d", "none")}


def guard_comparisons(test: Test, seed_no: int = 1) -> list[dict[str, Any]]:
    """The guard on the generator (specification Section 6; plan 1, Section 12.2, item 4): every scenario's five plain
    means at search-length rows against their true values, in Monte Carlo standard errors."""
    out = []
    for (s_no, phase, scn_id), rows in test.samples.items():
        if s_no != seed_no:
            continue
        for row, sample in rows.items():
            if row not in ROW_STEP:
                continue
            for stat in PLAIN_MEANS:
                est = sample.vals[:, S[stat], F["est"]]
                est = est[np.isfinite(est)]
                truth = test.truth(scn_id, row, stat)
                se = float(est.std(ddof=1) / math.sqrt(est.size))
                out.append({"scenario": scn_id, "phase": "rerun" if phase else "first", "row": row, "statistic": stat, "n": int(est.size),
                            "truth": truth, "mean": float(est.mean()), "standard_errors": float((est.mean() - truth) / se) if se > 0 else 0.0})
    return out


# ----------------------------------------------------------------------------- the checks with exact known answers


def check_g1(n: int = N_EXPERIMENTS, K: int = 16, seed_no: int = 1, master: int = MASTER_SEED) -> dict[str, Any]:
    """G1, as the erratum corrects it: Gaussian attack-batch effects only. V_PB is then the classical s^2 / K, V_c is
    zero, nu is K - 1, and the interval is the textbook t interval: coverage exactly 95 percent."""
    pres = Presence.complete(K, K, N_STARTS)
    covered = 0
    exact = True
    for e in range(n):
        rng = np.random.default_rng([master, seed_no, 9001, e])
        effect = rng.standard_normal(K)
        r = LI.interval(Combo(a_cells=np.broadcast_to(effect[:, None, None], (K, K, N_STARTS))), None, pres, batch_part="closed_form", percentile=False)
        covered += abs(r["estimate"]) <= r["half_width_unwidened"]
        exact &= r["v_c"] == 0.0 and r["nu"] == K - 1 and abs(r["v_pb"] - effect.var(ddof=1) / K) <= 1e-12 * r["v_pb"]
    coverage = covered / n
    se = math.sqrt(0.95 * 0.05 / n)
    return {"experiments": n, "coverage": coverage, "expected": 0.95, "monte_carlo_se": se, "standard_errors": (coverage - 0.95) / se,
            "v_pb_is_classical_and_nu_is_k_minus_1": bool(exact), "passes": bool(abs(coverage - 0.95) <= 3 * se and exact)}


def check_g2(n: int = N_EXPERIMENTS, K: int = 16, seed_no: int = 1, master: int = MASTER_SEED) -> dict[str, Any]:
    """G2: Gaussian independent cell noise only. V_PB averages 2.94 times the true variance at K = 16, and coverage
    exceeds 99 percent."""
    pres = Presence.complete(K, K, N_STARTS)
    true_variance = 1.0 / (K * K * N_STARTS)
    ratio, covered = [], 0
    for e in range(n):
        rng = np.random.default_rng([master, seed_no, 9002, e])
        r = LI.interval(Combo(a_cells=rng.standard_normal((K, K, N_STARTS))), None, pres, batch_part="closed_form", percentile=False)
        ratio.append(r["v_pb"] / true_variance)
        covered += abs(r["estimate"]) <= r["half_width_unwidened"]
    mean = float(np.mean(ratio))
    se = float(np.std(ratio, ddof=1) / math.sqrt(n))
    expected = (K - 1) * (3 * K - 1) / K**2 * K / (K - 1)  # 2.9375 at K = 16
    return {"experiments": n, "mean_v_pb_over_true_variance": mean, "expected": expected, "monte_carlo_se": se, "coverage": covered / n,
            "passes": bool(abs(mean - expected) <= 4 * se and covered / n > 0.99)}


# ----------------------------------------------------------------------------- the run


def _git_commit() -> dict[str, Any]:
    top = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0:
        return {"commit": None, "code_clean": None}
    head = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "--verify", "HEAD^{commit}"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", "vpd_audit_2", "freeze"], capture_output=True, text=True).stdout.strip()
    return {"commit": head, "code_clean": dirty == ""}


VERSION_LABEL = {
    "amended": "The test of record: the generator as amended by Amendment 2 (a held-out batch's vulnerability is its log-normal noise alone).",
    "as_committed": ("Not the test of record: the generator as committed in Amendment 1 (a held-out batch's vulnerability carries its pilot "
                     "type's factor). Printed beside the test of record; it sets no multiplier, and its multipliers are those each row "
                     "would have required."),
}


def run(pool: Any, n: int = N_EXPERIMENTS, n_rerun: int = N_RERUN, log: Any = None, version: str = "amended",
        master: int = MASTER_SEED, guard_stop: float = GUARD_STOP) -> dict[str, Any]:
    """The whole test in one version of the generator, as one record. Stops after the checks if G1 or G2 misses, and
    after the first samples if the guard on the generator finds a plain mean more than 5 Monte Carlo standard errors
    from its truth. (`guard_stop` is for the unit tests alone, whose dozen experiments per scenario are too few for a
    threshold in standard errors to mean anything; the command always uses 5, and the report records what was used.)"""
    assert version in VERSIONS
    log = log or (lambda *a: None)
    scns = scenarios()
    report: dict[str, Any] = {
        "what": "The made-up-data test of the lead experiment's interval (plan 1, Part D; plan 3). Every number here is made up; none is a result.",
        "version": version, "version_label": VERSION_LABEL[version], "sets_multipliers": version == "amended",
        "seeds": {"master": master, "experiment_generator": "numpy.random.default_rng([master, seed, phase, scenario, experiment])",
                  "seed": "1 for the test, 2 and up for the confirmations", "phase": "0 for the first experiments, 1 for a rerun",
                  "percentile_indices": [LI.MASTER_SEED, PERCENTILE_STREAM, 16, 1000], "checks": "numpy.random.default_rng([master, 1, 9001 or 9002, experiment])"},
        "sizes": {"experiments": n, "rerun": n_rerun, "generated_cap": GENERATED_CAP_FACTOR * n, "rerun_generated_cap": GENERATED_CAP_FACTOR * n_rerun,
                  "percentile_replicates": 1000},
        "criterion": {"coverage_floor": COVERAGE_FLOOR, "one_sided_ceiling": ONE_SIDED_CEILING, "rerun_coverage": RERUN_COVERAGE,
                      "rerun_one_sided": RERUN_ONE_SIDED, "multiplier_grid": MULTIPLIER_GRID, "multiplier_limit": MULTIPLIER_LIMIT},
        "code": _git_commit(),
        "scenarios": [{"id": s.id, "kind": s.kind, "what": s.what, "rows": list(s.rows), "K": s.K, "sigma_delta": s.sigma_delta,
                       "lines": s.lines} for s in scns],
    }
    log("checks G1 and G2")
    report["g1"], report["g2"] = check_g1(n, master=master), check_g2(n, master=master)
    report["stopped"] = None
    if not (report["g1"]["passes"] and report["g2"]["passes"]):
        report["stopped"] = "G1 or G2 misses its known answer: the code is wrong, and no scenario is interpreted"
        return report

    test = Test(pool, n, n_rerun, log, version, master)
    report["truths"] = {s.id: {row: {**{k: test.population[s.id][row][k] for k in ("mu_k", "mu_q", "mu_Y", "mu_O", "mu_C", "S0", "rho_row", "share_present")},
                                     "truth": test.population[s.id][row]["truth"]} for row in s.rows} for s in scns}
    log("first experiments of every scenario")
    for s in scns:
        test.sample(1, 0, s.id)

    def guard() -> dict[str, Any]:
        comps = guard_comparisons(test)
        worst = max(abs(c["standard_errors"]) for c in comps)
        return {"comparisons": len(comps), "largest_standard_errors": worst, "stop_at": guard_stop, "list_above": GUARD_LIST,
                "above_list_threshold": [c for c in comps if abs(c["standard_errors"]) > GUARD_LIST], "stopped": worst > guard_stop}

    report["guard"] = guard()
    if report["guard"]["stopped"]:
        report["stopped"] = "the guard on the generator: a plain mean is more than 5 Monte Carlo standard errors from its truth"
        return report

    log("core cells: pass or fail, with reruns")
    cells = test.judge_cells(1, core_cells(scns))
    report["core_cells"] = cells
    log("the repair")
    report["rows"] = repair(test, cells)
    report["guard"] = guard()  # the reruns are guarded too; the confirmations' samples are fresh draws of the same generator
    if report["guard"]["stopped"]:
        report["stopped"] = "the guard on the generator: a plain mean is more than 5 Monte Carlo standard errors from its truth"
        return report

    log("the report's lines")
    lines = []
    for s in scns:
        first = test.sample(1, 0, s.id)
        for row in s.rows:
            for stat in STATS:
                lines.append(report_line(s, row, stat, first[row], test.truth(s.id, row, stat)))
    report["lines"] = lines
    report["stress_cells_under_floor"] = [{k: ln[k] for k in ("scenario", "row", "statistic", "coverage", "n")} for ln in lines
                                          if ln["kind"] == "stress" and ln.get("coverage") is not None and ln["coverage"] < COVERAGE_FLOOR]
    report["t3_by_c5_batches"] = t3_breakdown(test)
    report["t6_by_denominator_distance"] = t6_bins(test)
    report["t7"] = t7_summary(test)
    report["t8"], report["t8_null"] = t8_summary(test)
    return report


def t3_breakdown(test: Test) -> list[dict[str, Any]]:
    """T3: coverage of the three signed readings by the number of type-C5 batches on each side (0, 1, 2, 3 or more)."""
    out = []
    first = test.sample(1, 0, "T3")
    for row, sample in first.items():
        counts = np.minimum(sample.extra["c5_counts"], 3)
        for stat in SIGNED:
            truth = test.truth("T3", row, stat)
            est, hw = sample.vals[:, S[stat], F["est"]], sample.vals[:, S[stat], F["hw"]]
            covered = np.abs(est - truth) <= hw
            for side, col in (("attack", 0), ("heldout", 1)):
                for k in range(4):
                    pick = (counts[:, col] == k) & np.isfinite(est)
                    out.append({"row": row, "statistic": stat, "side": side, "c5_batches": "3 or more" if k == 3 else str(k),
                                "n": int(pick.sum()), "coverage": float(covered[pick].mean()) if pick.any() else None})
    return out


def t6_bins(test: Test) -> list[dict[str, Any]]:
    """T6: the shuffled ratio's coverage and reading frequencies in bins of z_D, pooled over the eight values of psi.
    At psi = 1 the ratio's truth divides by zero, so that value enters the reading frequencies and not the coverage."""
    out = []
    for row in ("n20", "n80"):
        zs, cov, has_truth, Ls, Us = [], [], [], [], []
        for psi in T6_PSI:
            scn_id = f"T6[{psi:g}]"
            sample = test.sample(1, 0, scn_id)[row]
            est, hw = sample.vals[:, S["depends"], F["est"]], sample.vals[:, S["depends"], F["hw"]]
            own = sample.vals[:, S["own_margin"], :]
            z = own[:, F["est"]] / np.sqrt(own[:, F["vtot"]])  # z_D, with the unwidened standard error
            ok = np.isfinite(est) & np.isfinite(hw) & np.isfinite(z)
            truth = test.truth(scn_id, row, "depends")
            zs.append(z[ok]); Ls.append((est - hw)[ok]); Us.append((est + hw)[ok])
            has_truth.append(np.full(int(ok.sum()), truth is not None))
            cov.append(np.abs(est[ok] - (truth if truth is not None else 0.0)) <= hw[ok])
        z, covered, known, L, U = (np.concatenate(x) for x in (zs, cov, has_truth, Ls, Us))
        for lo, hi, label in ZD_BINS:
            pick = (z >= lo) & (z < hi)
            out.append({"row": row, "bin": label, "n": int(pick.sum()), "n_with_a_truth": int((pick & known).sum()),
                        "coverage": float(covered[pick & known].mean()) if (pick & known).any() else None,
                        "reading_frequency": reading_frequency(L[pick], U[pick])})
    return out


def t7_summary(test: Test) -> dict[str, Any]:
    """T7: the convention's estimates are in the report's lines; here, beside them, the mean of the "both reached"
    estimate of the carry-over ratio and of the "large" difference."""
    sample = test.sample(1, 0, "T7")["h5"]
    br = sample.extra["both_reached"]
    out: dict[str, Any] = {"row": "h5", "n": int(sample.vals.shape[0])}
    for k, stat in enumerate(("carries", "large")):
        est = sample.vals[:, S[stat], F["est"]]
        truth = test.truth("T7", "h5", stat)
        out[stat] = {"truth": truth, "convention_mean": float(np.nanmean(est)), "convention_bias": float(np.nanmean(est) - truth),
                     "both_reached_mean": float(np.nanmean(br[:, k])), "both_reached_bias": float(np.nanmean(br[:, k]) - truth)}
    return out


def t8_summary(test: Test) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """T8: the spread of the two paired shares at each search length when the delta components do nothing, and how
    often each share's interval covers 1. The second value is what the analysis prints beside the delta-on summary."""
    first = test.sample(1, 0, "T8")
    lines, null = [], {}
    for row in STEP_ROWS:
        shares = first[row].extra["shares"]  # [n, version, share, (estimate, half-width)]
        null[row] = {}
        for k, share in enumerate(("carried_share", "own_share")):
            null[row][share] = {}
            for v, version in enumerate(("a", "b")):
                est, hw = shares[:, v, k, 0], shares[:, v, k, 1]
                ok = np.isfinite(est)
                p = [float(x) for x in np.percentile(est[ok], [2.5, 50.0, 97.5])]
                null[row][share][version] = p
                lines.append({"row": row, "share": share, "version": version, "n": int(ok.sum()), "p2_5": p[0], "p50": p[1], "p97_5": p[2],
                              "coverage_of_1": float((np.abs(est[ok] - 1.0) <= hw[ok]).mean())})
    return lines, null


# ----------------------------------------------------------------------------- writing


def _fmt(x: Any, digits: int = 3) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return "yes" if x else "no"
    return f"{x:.{digits}f}"


def summary_markdown(report: dict[str, Any]) -> str:
    """The summary in the layout of the specification's Section 9. Every number in it is made up; none is a result."""
    amended = report["version"] == "amended"
    out = ["# The Made-Up-Data Test of the Interval: Summary" + ("" if amended else " of the Generator as Committed in Amendment 1"), "",
           f"**{report['version_label']}**", "",
           "Every number in this file comes from made-up experiments built on the pilot's own-batch searches. None is a result of the lead experiment.", ""]
    g1, g2 = report["g1"], report["g2"]
    out += ["## Checks With Exact Known Answers", "",
            f"- **G1** (attack-batch effects only): coverage {_fmt(g1['coverage'], 4)} over {g1['experiments']} experiments; expected 0.95; "
            f"{_fmt(g1['standard_errors'], 2)} Monte Carlo standard errors from it; V_PB is the classical s^2/K and nu is K - 1 in every experiment: "
            f"{_fmt(g1['v_pb_is_classical_and_nu_is_k_minus_1'])}. Passes: {_fmt(g1['passes'])}.",
            f"- **G2** (independent cell noise only): mean of V_PB over the true variance {_fmt(g2['mean_v_pb_over_true_variance'], 4)} "
            f"(expected {_fmt(g2['expected'], 4)}, Monte Carlo standard error {_fmt(g2['monte_carlo_se'], 4)}); coverage {_fmt(g2['coverage'], 4)}. "
            f"Passes: {_fmt(g2['passes'])}.", ""]
    if report["stopped"] and "guard" not in report:
        return "\n".join(out + [f"**The test stopped: {report['stopped']}.**", ""])
    gd = report["guard"]
    out += ["## The Guard on the Generator", "",
            f"{gd['comparisons']} comparisons of a plain mean with its true value at search-length rows. The largest is "
            f"{_fmt(gd['largest_standard_errors'], 2)} Monte Carlo standard errors; the test stops at {gd['stop_at']:g}. "
            f"Comparisons above {gd['list_above']:g}: {len(gd['above_list_threshold'])}.", ""]
    if gd["above_list_threshold"]:
        out += ["| Scenario | Experiments | Row | Statistic | Truth | Mean | Standard errors |", "|---|---|---|---|---|---|---|"]
        out += [f"| {c['scenario']} | {c['phase']} | {c['row']} | {c['statistic']} | {_fmt(c['truth'], 4)} | {_fmt(c['mean'], 4)} | {_fmt(c['standard_errors'], 2)} |"
                for c in gd["above_list_threshold"]] + [""]
    if report["stopped"]:
        return "\n".join(out + [f"**The test stopped: {report['stopped']}.**", ""])

    out += ["## Each Core Cell: Pass or Fail", "",
            "A cell is one core scenario, one row, and one signed reading. Coverage is of the unwidened interval. A cell under 93.5 percent, or with "
            "more than 3.25 percent of its intervals wholly on one side of its line, is rerun with 10,000 experiments and judged on the rerun alone.", "",
            "| Scenario | Row | Reading | Line | Judged on | Coverage | Wholly above | Wholly below | Rerun | Multiplier needed | Result |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in report["core_cells"]:
        out.append(f"| {c['scenario']} | {c['row']} | {c['statistic']} | {_fmt(c['line'], 1) if c['line'] is not None else ''} | {c['judged_on']} | "
                   f"{_fmt(c['coverage'], 4)} | {_fmt(c['above'], 4)} | {_fmt(c['below'], 4)} | {_fmt(c['rerun'])} | {_fmt(c['multiplier_needed'], 3)} | "
                   f"{'FAIL' if c['fail'] else 'pass'} |")
    out += ["", "## Each Row's Multiplier" if amended else "## The Multiplier Each Row Would Have Required (It Sets None)", "",
            "| Row | Failing core cells | Largest multiplier needed | Multiplier | Confirmation | Goes to the PI |", "|---|---|---|---|---|---|"]
    for row, r in report["rows"].items():
        conf = "; ".join(f"seed {c['seed']} at {c['multiplier']:.2f}: {'passed' if c['passed'] else 'failed'} (lowest coverage {_fmt(c['lowest_coverage'], 4)})"
                         for c in r["confirmation"]) or "not needed"
        out.append(f"| {row} | {', '.join(r['failed_cells']) or 'none'} | {_fmt(r['largest_needed'], 3)} | {r['multiplier']:.2f} | {conf} | {_fmt(r['to_pi'])} |")
    out += ["", "## Harm-Level Core Cells: Coverage Where the Level Is Read, and Over All Experiments", "",
            "The criterion judges a harm-level row on the experiments in which the count rule lets the level be read (the first three columns "
            "of numbers). Beside it, as description, the same intervals over every experiment of the same sample, read or not.", "",
            "| Scenario | Row | Reading | Share read | Judged on | Coverage, level read | Experiments, all | Coverage, all | Wholly above, all | Wholly below, all |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for c in report["core_cells"]:
        if "all_experiments" in c:
            a = c["all_experiments"]
            out.append(f"| {c['scenario']} | {c['row']} | {c['statistic']} | {_fmt(c['share_read'])} | {c['judged_on']} | {_fmt(c['coverage'], 4)} | "
                       f"{a['n']} | {_fmt(a['coverage'], 4)} | {_fmt(a['above'], 4)} | {_fmt(a['below'], 4)} |")
    out += ["", "## Stress Cells Under 92.5 Percent (Stated, Not Repaired)", ""]
    if report["stress_cells_under_floor"]:
        out += ["| Scenario | Row | Statistic | Coverage | Experiments |", "|---|---|---|---|---|"]
        out += [f"| {c['scenario']} | {c['row']} | {c['statistic']} | {_fmt(c['coverage'], 4)} | {c['n']} |" for c in report["stress_cells_under_floor"]]
    else:
        out.append("None.")
    out += ["", "## The Shuffled Ratio by Its Denominator's Distance From Zero (T6)", "",
            "Pooled over the eight values of psi. Coverage leaves out psi = 1, where the ratio's truth divides by zero.", "",
            "| Row | z_D | Experiments | Coverage | a | b | c | d | no reading defined |", "|---|---|---|---|---|---|---|---|---|"]
    for b in report["t6_by_denominator_distance"]:
        f = b["reading_frequency"]
        out.append(f"| {b['row']} | {b['bin']} | {b['n']} | {_fmt(b['coverage'], 4)} | {_fmt(f['a'])} | {_fmt(f['b'])} | {_fmt(f['c'])} | {_fmt(f['d'])} | {_fmt(f['none'])} |")
    out += ["", "## The Delta-On Shares When the Delta Components Do Nothing (T8)", "",
            "Version a: the same searches with fresh cell noise. Version b: every search redrawn from its batch type's pilot starts.", "",
            "| Row | Share | Version | 2.5th percentile | Median | 97.5th percentile | Interval covers 1 |", "|---|---|---|---|---|---|---|"]
    out += [f"| {t['row']} | {t['share']} | {t['version']} | {_fmt(t['p2_5'])} | {_fmt(t['p50'])} | {_fmt(t['p97_5'])} | {_fmt(t['coverage_of_1'], 4)} |" for t in report["t8"]]
    t7 = report["t7"]
    out += ["", "## Batch-Clustered Missing Searches (T7), at 5 Nats", "",
            "| Statistic | Truth | Convention, mean | Convention, bias | \"Both reached\", mean | \"Both reached\", bias |", "|---|---|---|---|---|---|"]
    out += [f"| {s} | {_fmt(t7[s]['truth'], 4)} | {_fmt(t7[s]['convention_mean'], 4)} | {_fmt(t7[s]['convention_bias'], 4)} | "
            f"{_fmt(t7[s]['both_reached_mean'], 4)} | {_fmt(t7[s]['both_reached_bias'], 4)} |" for s in ("carries", "large")]
    out += ["", "## Coverage by the Number of Type-C5 Batches (T3)", "", "| Row | Reading | Side | Type-C5 batches | Experiments | Coverage |", "|---|---|---|---|---|---|"]
    out += [f"| {t['row']} | {t['statistic']} | {t['side']} | {t['c5_batches']} | {t['n']} | {_fmt(t['coverage'], 4)} |" for t in report["t3_by_c5_batches"]]
    out += ["", "## Every Scenario, Row, and Statistic", "",
            "Coverage is of the unwidened interval; \"above\" and \"below\" are the shares of intervals lying wholly above and wholly below the truth; "
            "\"variance ratio\" is the mean of V_PB + V_c over the Monte Carlo variance of the estimate; the half-width is its median.", "",
            "| Scenario | Row | Statistic | Truth | Mean | Bias | MC sd | Coverage | Above | Below | Variance ratio | Half-width | V_c = 0 | Start share > 0.5 | Mean nu | "
            "Multiplier needed | Percentile coverage | Denominator's distance | Share read | Coverage, all experiments |", "|" + "---|" * 20]
    for ln in report["lines"]:
        if ln["n"] == 0:
            continue
        out.append(f"| {ln['scenario']} | {ln['row']} | {ln['statistic']} | {_fmt(ln['truth'], 4)} | {_fmt(ln['mean_estimate'], 4)} | {_fmt(ln['bias'], 4)} | "
                   f"{_fmt(ln['mc_sd'], 4)} | {_fmt(ln['coverage'], 4)} | {_fmt(ln['above'], 4)} | {_fmt(ln['below'], 4)} | {_fmt(ln['variance_ratio'], 3)} | "
                   f"{_fmt(ln['half_width_p50'], 4)} | {_fmt(ln['share_vc_zero'])} | {_fmt(ln['share_start_over_half'])} | {_fmt(ln['mean_nu'], 1)} | "
                   f"{_fmt(ln['multiplier_needed'], 3)} | {_fmt(ln.get('percentile_coverage'), 4)} | {_fmt(ln.get('median_denominator_distance'), 1)} | "
                   f"{_fmt(ln.get('share_read'), 3)} | {_fmt((ln.get('all_experiments') or {}).get('coverage'), 4)} |")
    out += ["", "## Verdict and Reading Frequencies", "",
            "Where a signed reading's truth sits on a line, how often each verdict is printed; for the shuffled ratio always, how often each reading.", "",
            "| Scenario | Row | Statistic | Line | yes | no | undetermined | a | b | c | d | no reading defined |", "|" + "---|" * 12]
    for ln in report["lines"]:
        if "verdict_frequency" not in ln and "reading_frequency" not in ln:
            continue
        v, r = ln.get("verdict_frequency", {}), ln.get("reading_frequency", {})
        out.append(f"| {ln['scenario']} | {ln['row']} | {ln['statistic']} | {_fmt(ln['line'], 1) if ln['line'] is not None else ''} | {_fmt(v.get('yes'))} | "
                   f"{_fmt(v.get('no'))} | {_fmt(v.get('undetermined'))} | {_fmt(r.get('a'))} | {_fmt(r.get('b'))} | {_fmt(r.get('c'))} | {_fmt(r.get('d'))} | {_fmt(r.get('none'))} |")
    out += ["", "## In Words", ""]
    failed = [c for c in report["core_cells"] if c["fail"]]
    out.append(f"- **Core cells:** {len(report['core_cells'])} judged, {len(failed)} failing"
               + (": " + ", ".join(f"{c['scenario']} {c['row']} {c['statistic']}" for c in failed) if failed else "") + ".")
    if not amended:
        out.append("- **This version sets no multiplier.** What follows is what each row would have required under the generator as committed.")
    for row, r in report["rows"].items():
        if r["multiplier"] == 1.0 and not r["failed_cells"]:
            out.append(f"- **{row}:** every core cell passes; the multiplier stays 1.")
        elif r["to_pi"]:
            out.append(f"- **{row}:** needs more than {MULTIPLIER_LIMIT}; the row goes to the PI.")
        else:
            last = r["confirmation"][-1]
            out.append(f"- **{row}:** multiplier {r['multiplier']:.2f}, confirmed on seed {last['seed']} (lowest coverage {_fmt(last['lowest_coverage'], 4)}).")
    out.append(f"- **Stress cells under 92.5 percent:** {len(report['stress_cells_under_floor'])}, listed above"
               + (" as limits for the post." if amended else "."))
    out.append(f"- **G1:** {_fmt(g1['passes'])}. **G2:** {_fmt(g2['passes'])}.")
    out.append(f"- **Seeds:** master {report['seeds']['master']}. **Commit:** {report['code']['commit']} (code as committed: {_fmt(report['code']['code_clean'])}).")
    return "\n".join(out) + "\n"


def _plain(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, np.ndarray):
        return _plain(x.tolist())
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return float(x) if math.isfinite(float(x)) else None
    return x


def write_report(report: dict[str, Any], out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plain = _plain(report)
    (out_dir / "report.json").write_text(json.dumps(plain, indent=1, allow_nan=False) + "\n")
    (out_dir / "summary.md").write_text(summary_markdown(plain))
    # The multipliers as the analysis reads them, from the test of record only: the version as committed sets none,
    # so it writes no such file for anyone to copy.
    if "rows" in plain and plain["version"] == "amended":
        (out_dir / "multipliers.json").write_text(json.dumps({"rows": {row: r["multiplier"] for row, r in plain["rows"].items()},
                                                              "to_pi": [row for row, r in plain["rows"].items() if r["to_pi"]]}, indent=1) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The made-up-data test of the lead experiment's interval.")
    ap.add_argument("--version", choices=VERSIONS, default="amended",
                    help="amended: the test of record; as_committed: the generator of Amendment 1, printed beside it")
    ap.add_argument("--out", type=Path, default=None, help="default: results/s5_madeup, or results/s5_madeup/as_committed")
    ap.add_argument("--processes", type=int, default=max(1, (mp.cpu_count() or 2) - 2))
    ap.add_argument("--experiments", type=int, default=N_EXPERIMENTS)
    ap.add_argument("--rerun", type=int, default=N_RERUN)
    ap.add_argument("--master-seed", type=int, default=MASTER_SEED)
    args = ap.parse_args(argv)
    out_dir = args.out if args.out is not None else (OUT_DIR if args.version == "amended" else OUT_DIR / "as_committed")
    t0 = time.time()
    with mp.get_context("spawn").Pool(args.processes) as pool:
        report = run(pool, args.experiments, args.rerun, log=lambda *a: print(*a, file=sys.stderr, flush=True), version=args.version,
                     master=args.master_seed)
    write_report(report, out_dir)
    seconds = time.time() - t0
    (Path(out_dir) / "runtime.json").write_text(json.dumps({"seconds": round(seconds, 1), "processes": args.processes}) + "\n")
    print(f"{args.version}: written to {out_dir} in {seconds:.0f} s; stopped: {report['stopped']}", file=sys.stderr)
    return 0 if report["stopped"] is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
