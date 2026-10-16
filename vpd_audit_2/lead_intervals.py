"""Plan 1 of the research log, Section 5.2: the interval of every statistic of the lead experiment.

The rules: `freeze/part1.md`, Section 5 (signed); `freeze/amendment1.md`, entries 2.3 and 2.4 and Section 9; and the
binding specification `freeze/amendment1_specs/interval_spec.md`, Sections 2 to 5 ("the specification" below).

One routine, `interval`, serves every row and every statistic, complete tables and tables with missing searches alike.
A statistic is a mean, or a ratio of two means, where each "mean" is a sum of at most one mean of kind M_A and one of
kind M_H (`Combo`):

    M_A[f] = sum_{i,j,s} a_is f_ijs / C_A,  C_A = K sum_{i,s} a_is     over cells whose attack search has a setting
    M_H[g] = sum_{j,s} b_js g_js / C_H,     C_H = sum_{j,s} b_js       over held-out searches that have a setting

Steps, in the specification's order:

  - Batch part (4.2, general form 5.2). The table that is resampled is `lin_table`, the specification's Z_ij: for a
    mean, the centred sums E_ij; for a ratio, (E_ij[numerator] - estimate * E_ij[denominator]) / denominator, with the
    estimate and its denominator fixed from the whole table. Each bootstrap replicate is the mean of the K^2 entries of
    `lin_table` at K attack and K held-out indices drawn with replacement; it does not recompute the ratio.
    V_PB = K / (K - 1) * SE*^2, with SE*^2 the sample variance (divisor B - 1) of the replicates.
  - The closed form (4.2) is computed for every interval, and the bootstrap variance must agree with it within the band
    of plan 1 of the research log, Section 12.3: 1 +/- max(0.07, 5 sqrt((kurtosis - 1) / B)), the kurtosis being that of the B replicate
    values. A closed form of exactly zero requires a bootstrap variance of exactly zero. A miss raises.
  - Start part (4.3, with 5.1 item 4): the three-way analysis of variance of the linearized cells on the complete
    sub-table (all starts; attack batches with every search present; held-out batches with every search present).
  - Degrees of freedom and the interval (4.4); the percentile interval, each start's pooled value, and the
    denominator's distance from zero (4.5).

Names follow the specification's erratum, item 3: `lin_cell` is W_ijs, `lin_table` is Z_ij, `denom_z` is z_D, and
`half_width` is w. A cell's shuffled harm is called `shuf` by the callers.

Exact zeros. Two cases must give a variance of exactly zero and not rounding dust: an input that is the same number in
every cell (the reading specification's cases R10 and R11), and cells that do not depend on the start. So every mean is computed on the
cells minus one reference cell (which changes no mean, centred sum, or mean square), and the mean squares are computed
on the cells minus their first start's value (which changes none of the four mean squares, since each is built from
contrasts between starts).
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.special import stdtrit

MASTER_SEED = 20261001  # the manifest's master seed
BOOTSTRAP_STREAM = 5001  # this module's own stream under the master seed, fixed before any deciding run
BOOTSTRAP_B = 10_000  # signed, Section 5
T_PROBABILITY = 0.975  # a 95 percent two-sided interval
CLOSED_FORM_BAND_FLOOR = 0.07  # plan 1 of the research log, Section 12.3
CLOSED_FORM_BAND_STANDARD_ERRORS = 5.0
PERCENTILE_UNRELIABLE_SHARE = 0.001  # specification 4.5: 0.1 percent of replicates


class ClosedFormCheckError(Exception):
    """The bootstrap variance and its closed form disagree. The message names the check and carries no number."""

    def __init__(self) -> None:
        super().__init__("closed_form_check")


# ----------------------------------------------------------------------------- inputs


@dataclass(frozen=True)
class Combo:
    """A sum of at most one mean of kind M_A (`a_cells`, [K, K, n_s]) and one of kind M_H (`h_cells`, [K, n_s])."""

    a_cells: np.ndarray | None = None
    h_cells: np.ndarray | None = None


class Presence:
    """Which searches have a setting at the row: `a` [K_A, n_s] for attack searches, `b` [K_H, n_s] for held-out ones."""

    def __init__(self, a_present: np.ndarray, b_present: np.ndarray) -> None:
        a = np.asarray(a_present, dtype=bool)
        b = np.asarray(b_present, dtype=bool)
        assert a.ndim == 2 and b.ndim == 2 and a.shape[1] == b.shape[1], "presence masks must be [batches, starts]"
        self.a, self.b = a, b
        self.K_A, self.n_s = a.shape
        self.K_H = b.shape[0]
        self.a_count = a.sum(axis=1).astype(np.float64)  # searches present per attack batch
        self.b_count = b.sum(axis=1).astype(np.float64)
        self.a_per_start = a.sum(axis=0).astype(np.float64)
        self.b_per_start = b.sum(axis=0).astype(np.float64)
        self.C_A = float(self.K_H * a.sum())
        self.C_H = float(b.sum())
        self.sub_a = np.flatnonzero(a.all(axis=1))  # attack batches with every search present
        self.sub_h = np.flatnonzero(b.all(axis=1))
        fa = np.argwhere(a)
        fb = np.argwhere(b)
        self.first_a = (int(fa[0, 0]), int(fa[0, 1])) if fa.size else None
        self.first_b = (int(fb[0, 0]), int(fb[0, 1])) if fb.size else None

    @classmethod
    def complete(cls, K_A: int, K_H: int, n_s: int) -> Presence:
        return cls(np.ones((K_A, n_s), dtype=bool), np.ones((K_H, n_s), dtype=bool))


@dataclass(frozen=True)
class BootstrapIndices:
    """The drawn batch indices, one row per replicate, and how often each batch was drawn."""

    K: int
    B: int
    seed: tuple[int, ...] | None  # None for an enumeration
    idx_attack: np.ndarray  # [B, K] int64
    idx_heldout: np.ndarray
    counts_attack: np.ndarray  # [B, K] float64
    counts_heldout: np.ndarray
    sha256: str


def _counts(idx: np.ndarray, K: int) -> np.ndarray:
    out = np.zeros((idx.shape[0], K), dtype=np.float64)
    np.add.at(out, (np.arange(idx.shape[0])[:, None], idx), 1.0)
    return out


def _indices(K: int, seed: tuple[int, ...] | None, idx_a: np.ndarray, idx_h: np.ndarray) -> BootstrapIndices:
    idx_a = np.ascontiguousarray(idx_a, dtype="<i8")
    idx_h = np.ascontiguousarray(idx_h, dtype="<i8")
    sha = hashlib.sha256(idx_a.tobytes() + idx_h.tobytes()).hexdigest()
    return BootstrapIndices(K=K, B=int(idx_a.shape[0]), seed=seed, idx_attack=idx_a, idx_heldout=idx_h,
                            counts_attack=_counts(idx_a, K), counts_heldout=_counts(idx_h, K), sha256=sha)


def make_indices(K: int, B: int = BOOTSTRAP_B, stream: int = BOOTSTRAP_STREAM) -> BootstrapIndices:
    """The B x K attack indices and B x K held-out indices for one value of K, drawn once from one seeded generator
    (attack first) and reused for every row and statistic (specification 4.2)."""
    seed = (MASTER_SEED, stream, K, B)
    rng = np.random.default_rng(list(seed))
    idx_a = rng.integers(0, K, size=(B, K))
    idx_h = rng.integers(0, K, size=(B, K))
    return _indices(K, seed, idx_a, idx_h)


def enumerate_indices(K: int) -> BootstrapIndices:
    """Every outcome of the bootstrap, each once: K^K attack draws times K^K held-out draws. For small K only."""
    assert K**K <= 4096, "enumeration is for small tables"
    draws = np.array(np.meshgrid(*[np.arange(K)] * K, indexing="ij")).reshape(K, -1).T  # [K^K, K]
    n = draws.shape[0]
    idx_a = np.repeat(draws, n, axis=0)
    idx_h = np.tile(draws, (n, 1))
    return _indices(K, None, idx_a, idx_h)


# ----------------------------------------------------------------------------- the pieces


def t_quantile(nu: float) -> float:
    """t_{0.975, nu} at real nu."""
    return float(stdtrit(nu, T_PROBABILITY))


def closed_form_variance(lin_table: np.ndarray) -> float:
    """Specification 4.2: the exact bootstrap variance of the mean of a K by K table."""
    K = lin_table.shape[0]
    assert lin_table.shape == (K, K)
    grand = lin_table.mean()
    row = lin_table.mean(axis=1)
    col = lin_table.mean(axis=0)
    alpha = row - grand
    beta = col - grand
    gamma = lin_table - row[:, None] - col[None, :] + grand
    return float((alpha**2).sum() / K**2 + (beta**2).sum() / K**2 + (gamma**2).sum() / K**4)


def replicate_deviations(lin_table: np.ndarray, indices: BootstrapIndices) -> np.ndarray:
    """Each replicate's mean of the K^2 entries of `lin_table` at its drawn attack and held-out indices."""
    K = lin_table.shape[0]
    assert indices.K == K
    return ((indices.counts_attack @ lin_table) * indices.counts_heldout).sum(axis=1) / K**2


def closed_form_band(replicates: np.ndarray) -> tuple[float, float]:
    """Plan 1 of the research log, Section 12.3: the half-width of the band on SE*^2 / V_closed, and the replicates' kurtosis."""
    d = replicates - replicates.mean()
    m2 = float((d**2).mean())
    m4 = float((d**4).mean())
    kurtosis = m4 / m2**2 if m2 > 0 else 3.0
    band = max(CLOSED_FORM_BAND_FLOOR, CLOSED_FORM_BAND_STANDARD_ERRORS * math.sqrt(max(kurtosis - 1.0, 0.0) / replicates.size))
    return band, kurtosis


def check_closed_form(se_star_sq: float, v_closed: float, replicates: np.ndarray) -> dict[str, Any]:
    """Raise unless the bootstrap variance agrees with its closed form."""
    if v_closed == 0.0:
        if se_star_sq != 0.0:
            raise ClosedFormCheckError()
        return {"ratio": None, "band": None, "kurtosis": None}
    band, kurtosis = closed_form_band(replicates)
    ratio = se_star_sq / v_closed
    if not abs(ratio - 1.0) <= band:
        raise ClosedFormCheckError()
    return {"ratio": ratio, "band": band, "kurtosis": kurtosis}


def mean_squares(lin_cells: np.ndarray) -> dict[str, float]:
    """Specification 4.3: the four mean squares of the three-way analysis of variance of [K_A, K_H, n_s] cells.

    Computed on the cells minus their first start's value, which leaves all four unchanged and makes them exactly zero
    when no cell depends on the start."""
    K_A, K_H, n_s = lin_cells.shape
    assert K_A >= 2 and K_H >= 2 and n_s >= 2
    w = lin_cells - lin_cells[:, :, :1]
    m = w.mean()
    m_s = w.mean(axis=(0, 1))
    m_i = w.mean(axis=(1, 2))
    m_j = w.mean(axis=(0, 2))
    m_is = w.mean(axis=1)
    m_js = w.mean(axis=0)
    m_ij = w.mean(axis=2)
    ms_s = K_A * K_H / (n_s - 1) * float(((m_s - m) ** 2).sum())
    ms_as = K_H / ((K_A - 1) * (n_s - 1)) * float(((m_is - m_i[:, None] - m_s[None, :] + m) ** 2).sum())
    ms_bs = K_A / ((K_H - 1) * (n_s - 1)) * float(((m_js - m_j[:, None] - m_s[None, :] + m) ** 2).sum())
    resid = (w - m_ij[:, :, None] - m_is[:, None, :] - m_js[None, :, :]
             + m_i[:, None, None] + m_j[None, :, None] + m_s[None, None, :] - m)
    ms_abs = float((resid**2).sum()) / ((K_A - 1) * (K_H - 1) * (n_s - 1))
    return {"S": ms_s, "AS": ms_as, "BS": ms_bs, "ABS": ms_abs}


def interval_from_parts(estimate: float, v_pb: float, ms: dict[str, float] | None, *, K: int, K_A: int, K_H: int, n_s: int,
                        multiplier: float = 1.0) -> dict[str, Any]:
    """From V_PB and the four mean squares to the interval (specification 4.3 and 4.4; signed Section 5, items 2 to 4).

    `K` is the full number of batches per side; `K_A`, `K_H`, and `n_s` are the sizes of the table the mean squares
    came from. `ms=None` means the start part cannot be estimated, and V_c is then zero."""
    assert K >= 2 and multiplier >= 1.0
    estimable = ms is not None
    if estimable:
        u = ms["S"] - ms["AS"] - ms["BS"] + ms["ABS"]
        sigma_untruncated: float | None = u / (K_A * K_H)
    else:
        u, sigma_untruncated = 0.0, None
    sigma_c_sq = max(0.0, sigma_untruncated) if sigma_untruncated is not None else 0.0
    v_c = sigma_c_sq / n_s
    nu_c_untruncated: float | None = None
    nu_c: float | None = None
    if estimable and u > 0.0:
        den = (ms["S"] ** 2 / (n_s - 1) + ms["AS"] ** 2 / ((K_A - 1) * (n_s - 1)) + ms["BS"] ** 2 / ((K_H - 1) * (n_s - 1))
               + ms["ABS"] ** 2 / ((K_A - 1) * (K_H - 1) * (n_s - 1)))
        nu_c_untruncated = u * u / den
        nu_c = min(max(nu_c_untruncated, 1.0), float(n_s - 1))
    total = v_pb + v_c
    if v_c == 0.0:
        nu = float(K - 1)
    else:
        assert nu_c is not None
        nu = total**2 / (v_pb**2 / (K - 1) + v_c**2 / nu_c)
    standard_error = math.sqrt(total)
    tq = t_quantile(nu)
    half_width = tq * standard_error
    wide = multiplier * half_width
    return {
        "estimate": estimate + 0.0,
        "v_pb": v_pb,
        "mean_squares": dict(ms) if estimable else None,
        "sigma_c_sq_untruncated": sigma_untruncated,
        "sigma_c_sq": sigma_c_sq,
        "v_c": v_c,
        "start_share": (v_c / total) if total > 0.0 else None,
        "nu_c_untruncated": nu_c_untruncated,
        "nu_c": nu_c,
        "nu": nu,
        "t_quantile": tq,
        "standard_error": standard_error,
        "half_width_unwidened": half_width,
        "interval_unwidened": [estimate - half_width + 0.0, estimate + half_width + 0.0],
        "multiplier": multiplier,
        "half_width": wide,
        "interval": [estimate - wide + 0.0, estimate + wide + 0.0],
        "zero_variance": total == 0.0,
        "start_part_not_estimable": not estimable,
    }


# ----------------------------------------------------------------------------- one mean


class _Evaluated:
    """A `Combo` on one row: its value, its centred sums E_ij, its cells for the start part, and its per-batch totals."""

    __slots__ = ("defined", "value", "centred", "cells", "parts", "start_values", "start_defined")


def _evaluate(combo: Combo, pres: Presence) -> _Evaluated:
    ev = _Evaluated()
    K_A, K_H, n_s = pres.K_A, pres.K_H, pres.n_s
    ev.defined = True
    ev.value = 0.0
    ev.centred = np.zeros((K_A, K_H))
    ev.cells = np.zeros((K_A, K_H, n_s))
    ev.parts = []
    ev.start_values = np.zeros(n_s)
    ev.start_defined = np.ones(n_s, dtype=bool)
    assert combo.a_cells is not None or combo.h_cells is not None, "a mean needs cells"
    if combo.a_cells is not None:
        f = np.broadcast_to(np.asarray(combo.a_cells, dtype=np.float64), (K_A, K_H, n_s))
        if pres.first_a is None:
            ev.defined = False
            return ev
        i0, s0 = pres.first_a
        ref = float(f[i0, 0, s0])
        f0 = np.where(pres.a[:, None, :], f - ref, 0.0)  # cells minus the reference cell; zero where no setting exists
        total = f0.sum(axis=2)  # [K_A, K_H]
        m0 = float(total.sum()) / pres.C_A
        ev.value += ref + m0
        ev.centred += (K_A * K_H / pres.C_A) * (total - pres.a_count[:, None] * m0)
        ev.cells += f0
        ev.parts.append(("A", ref, total))
        per_start = f0.sum(axis=(0, 1))
        ok = pres.a_per_start > 0
        ev.start_defined &= ok
        ev.start_values += ref + per_start / np.where(ok, K_H * pres.a_per_start, 1.0)
    if combo.h_cells is not None:
        g = np.broadcast_to(np.asarray(combo.h_cells, dtype=np.float64), (K_H, n_s))
        if pres.first_b is None:
            ev.defined = False
            return ev
        j0, s0 = pres.first_b
        ref = float(g[j0, s0])
        g0 = np.where(pres.b, g - ref, 0.0)
        total = g0.sum(axis=1)  # [K_H]
        m0 = float(total.sum()) / pres.C_H
        ev.value += ref + m0
        ev.centred += ((K_H / pres.C_H) * (total - pres.b_count * m0))[None, :]
        ev.cells += g0[None, :, :]
        ev.parts.append(("H", ref, total))
        per_start = g0.sum(axis=0)
        ok = pres.b_per_start > 0
        ev.start_defined &= ok
        ev.start_values += ref + per_start / np.where(ok, pres.b_per_start, 1.0)
    return ev


def _resampled(ev: _Evaluated, pres: Presence, indices: BootstrapIndices) -> tuple[np.ndarray, np.ndarray]:
    """The mean recomputed in each replicate from the resampled batches' available cells, and where it has any."""
    value = np.zeros(indices.B)
    ok = np.ones(indices.B, dtype=bool)
    for kind, ref, total in ev.parts:
        if kind == "A":
            s = ((indices.counts_attack @ total) * indices.counts_heldout).sum(axis=1)
            c = (indices.counts_attack @ pres.a_count) * pres.K_H
        else:
            s = indices.counts_heldout @ total
            c = indices.counts_heldout @ pres.b_count
        has = c > 0
        ok &= has
        value += ref + s / np.where(has, c, 1.0)
    return value, ok


def _recomputed(n_ev: _Evaluated, d_ev: _Evaluated | None, pres: Presence, indices: BootstrapIndices) -> tuple[np.ndarray, np.ndarray, float | None]:
    """The statistic recomputed in each replicate (for a ratio, the resampled numerator mean over the resampled
    denominator mean), the replicates in which it exists, and the share of replicates whose denominator is zero or
    negative."""
    num, ok = _resampled(n_ev, pres, indices)
    nonpositive_share = None
    values = np.full(indices.B, np.nan)
    if d_ev is not None:
        den, ok_d = _resampled(d_ev, pres, indices)
        ok = ok & ok_d
        n_ok = int(ok.sum())
        nonpositive_share = float((den[ok] <= 0).sum() / n_ok) if n_ok else None
        ok = ok & (den != 0)  # a replicate whose denominator is exactly zero has no ratio and is left out
        values[ok] = num[ok] / den[ok]
    else:
        values[ok] = num[ok]
    return values, ok, nonpositive_share


def resampled_statistic(num: Combo, den: Combo | None, presence: Presence, indices: BootstrapIndices) -> tuple[np.ndarray, np.ndarray]:
    """The statistic recomputed in each replicate, and the replicates in which it exists (the percentile interval's
    raw material; a replicate in which a mean has no cells is left out)."""
    n_ev = _evaluate(num, presence)
    d_ev = _evaluate(den, presence) if den is not None else None
    values, ok, _ = _recomputed(n_ev, d_ev, presence, indices)
    return values, ok


def _percentile_interval(n_ev: _Evaluated, d_ev: _Evaluated | None, pres: Presence, indices: BootstrapIndices) -> dict[str, Any]:
    """Specification 4.5 and 5.2: the 2.5th and 97.5th percentiles of the statistic recomputed in each replicate."""
    all_values, ok, nonpositive_share = _recomputed(n_ev, d_ev, pres, indices)
    values = all_values[ok]
    used = int(values.size)
    if used:
        lo, hi = np.percentile(values, [2.5, 97.5])
        pct: list[float] | None = [float(lo) + 0.0, float(hi) + 0.0]
    else:
        pct = None
    return {
        "interval_percentile": pct,
        "percentile": {
            "replicates": indices.B,
            "replicates_used": used,
            "replicates_left_out": indices.B - used,
            "denominator_nonpositive_share": nonpositive_share,
            "unreliable": bool(nonpositive_share is not None and nonpositive_share > PERCENTILE_UNRELIABLE_SHARE),
        },
    }


# ----------------------------------------------------------------------------- the interval


def _undefined(kind: str, multiplier: float, pres: Presence, numerator: float | None, denominator: float | None) -> dict[str, Any]:
    return {
        "kind": kind, "defined": False, "estimate": None, "numerator": numerator, "denominator": denominator,
        "counts": {"C_A": pres.C_A, "C_H": pres.C_H}, "lin_table": None, "replicates": None,
        "v_closed": None, "se_star_sq": None, "closed_form": None, "batch_part": None,
        "v_pb": None, "mean_squares": None, "sigma_c_sq_untruncated": None, "sigma_c_sq": None, "v_c": None,
        "start_share": None, "nu_c_untruncated": None, "nu_c": None, "nu": None, "t_quantile": None,
        "standard_error": None, "half_width_unwidened": None, "interval_unwidened": None, "multiplier": multiplier,
        "half_width": None, "interval": None, "zero_variance": False, "start_part_not_estimable": False,
        "subtable": None, "interval_percentile": None, "percentile": None, "per_start": None, "denom_z": None,
    }


def interval(num: Combo, den: Combo | None, presence: Presence, *, multiplier: float = 1.0,
             indices: BootstrapIndices | None = None, batch_part: str = "bootstrap", percentile: bool = True,
             denominator_distance: bool = True) -> dict[str, Any]:
    """The estimate and its intervals for the mean `num`, or for the ratio `num / den`.

    `batch_part` is "bootstrap" (the signed rule, with `indices`, checked against the closed form) or "closed_form"
    (the made-up-data test, specification Section 8, which uses the closed form in place of the bootstrap).
    The deciding interval is the unwidened half-width times `multiplier`; `denom_z` always uses the unwidened
    standard error."""
    pres = presence
    assert pres.K_A == pres.K_H, "the batch part needs as many attack batches as held-out batches"
    assert batch_part in ("bootstrap", "closed_form")
    K, n_s = pres.K_A, pres.n_s
    kind = "mean" if den is None else "ratio"
    n_ev = _evaluate(num, pres)
    d_ev = _evaluate(den, pres) if den is not None else None
    if not n_ev.defined or (d_ev is not None and not d_ev.defined):
        return _undefined(kind, multiplier, pres, n_ev.value if n_ev.defined else None, None)
    if d_ev is None:
        estimate = n_ev.value
        lin_table = n_ev.centred
        lin_cells = n_ev.cells
        denominator = None
    else:
        denominator = d_ev.value
        if denominator == 0.0:
            return _undefined(kind, multiplier, pres, n_ev.value, denominator)
        estimate = n_ev.value / denominator
        lin_table = (n_ev.centred - estimate * d_ev.centred) / denominator
        lin_cells = (n_ev.cells - estimate * d_ev.cells) / denominator

    # the batch part
    v_closed = closed_form_variance(lin_table)
    replicates = None
    if batch_part == "closed_form":
        se_star_sq = v_closed
        closed = None
    else:
        assert indices is not None, "the bootstrap needs its indices"
        deviations = replicate_deviations(lin_table, indices)
        se_star_sq = float(deviations.var(ddof=1))
        closed = check_closed_form(se_star_sq, v_closed, deviations)
        replicates = estimate + deviations
    v_pb = K / (K - 1) * se_star_sq

    # the start part, on the complete sub-table
    sub_a, sub_h = pres.sub_a, pres.sub_h
    if sub_a.size >= 2 and sub_h.size >= 2 and n_s >= 2:
        ms: dict[str, float] | None = mean_squares(lin_cells[np.ix_(sub_a, sub_h)])
    else:
        ms = None
    out = interval_from_parts(estimate, v_pb, ms, K=K, K_A=int(sub_a.size), K_H=int(sub_h.size), n_s=n_s, multiplier=multiplier)
    out.update({
        "kind": kind, "defined": True, "numerator": n_ev.value + 0.0, "denominator": denominator,
        "counts": {"C_A": pres.C_A, "C_H": pres.C_H}, "lin_table": lin_table, "replicates": replicates,
        "v_closed": v_closed, "se_star_sq": se_star_sq, "closed_form": closed, "batch_part": batch_part,
        "subtable": {"K_A": int(sub_a.size), "K_H": int(sub_h.size), "n_s": n_s},
    })

    # beside it
    if percentile and indices is not None:
        out.update(_percentile_interval(n_ev, d_ev, pres, indices))
    else:
        out.update({"interval_percentile": None, "percentile": None})
    per_start: list[float | None] = []
    for s in range(n_s):
        if not n_ev.start_defined[s] or (d_ev is not None and (not d_ev.start_defined[s] or d_ev.start_values[s] == 0.0)):
            per_start.append(None)
        elif d_ev is None:
            per_start.append(float(n_ev.start_values[s]) + 0.0)
        else:
            per_start.append(float(n_ev.start_values[s] / d_ev.start_values[s]) + 0.0)
    out["per_start"] = per_start
    out["denom_z"] = None
    if den is not None and denominator_distance:
        d_int = interval(den, None, pres, indices=indices, batch_part=batch_part, percentile=False)
        se = d_int["standard_error"]
        out["denom_z"] = (denominator / se) if se and se > 0.0 else None
    return out


ARRAY_FIELDS = ("lin_table", "replicates")


def record_of(result: dict[str, Any]) -> dict[str, Any]:
    """The interval as plain numbers, for the JSON record: everything but the arrays."""
    return {k: v for k, v in result.items() if k not in ARRAY_FIELDS}
