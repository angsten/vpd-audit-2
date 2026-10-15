"""Session 7, plan 5: probe 1's reading, committed before the run (`sessions/007/notes/daniel/probe1_spec.md`, Sections 4
and 5, with the six amendments of `sessions/007/engineering/plan_5.md`). No GPU.

    uv run python -m vpd_audit_2.probe1_read results/s7_probe1

It reads the collected unit files (`.cache/s7_probe1/units/`, each checked against the receipt `backup.json` in the
folder named) and refuses unless the validation passed and every unit of the 320-step stage is present. It writes
`reading.txt` and `record.json` to that folder and prints the reading.

Settings and sets. The 80 attack searches at 320 steps decide; at 80 steps, the same is printed as description. For a
setting s: the off set O is its components (delta entries apart) below one half; the kept components are the rest; the
off delta entries are its delta entries below one half. Pushes are the intact model's unless named otherwise.

The statistic (the note's Section 4, amendment 2).
  - Batch push P_c(A) = sum over the attack batch's 128 texts of p_c(x), in float64.
  - Agreement on a held-out text y: g(y) = sum_{c in O} |p_c(y)| [sign p_c(y) = sign P_c(A)] / sum_{c in O} |p_c(y)|,
    signs by np.sign (a zero batch push agrees with nothing).
  - Chance (amendment 2): the same over matched kept components. In each (weight matrix, usage band) cell of the strata
    of `pilot.py` (`s6_build.cells_of`), as many kept components as O has there, or all of them if fewer, drawn
    uniformly without replacement, cells in ascending order, one generator seeded ("probe1-chance", attack batch,
    start, steps, draw); eight draws, as the note's eight permutations, and g0(y) is their mean.
  - Pooled over the 128 texts of each of the 1,280 held-out cells: g-bar and g0-bar; agreement beyond chance
    kappa = (g-bar - g0-bar) / (1 - g0-bar), a ratio of two cell means.
  - The interval: session 5's two-way bootstrap over attack and held-out batches with its start term
    (`lead_intervals.interval`, the run's indices, multiplier 1 as the lead's rows had).

The reading (amendments 3 and 4), on kappa's interval [lo, hi]: with g0-bar above 0.9, "undetermined (degenerate)" and
kappa is not read; else lo > 0.5 "mostly agree"; lo <= 0 (the interval covers 0 or lies below it) "do not agree";
0.2 <= lo and hi <= 0.5 "partly agree"; hi <= 0.2 "weakly agree"; anything else straddles 0.2 or 0.5,
"undetermined".

Beside it: the attack batch's sign balance (the share of the off set's batch-push mass that is positive); the
marginal positive share on held-out texts; the unweighted sign agreement and its chance; the within-batch agreement
(amendment 5: each attack text against the batch push of the other 127, kappa and its interval over attack batches
with the start term); the additivity ratio sum_{c in O} p_c(y) / sum_t |Delta(y, t)|, and with the off delta entries
added; kappa with the off delta entries counted in O; at the full pattern, the same statistic as description; and the
checks (the pattern's damage against session 6's rounded control, the intact model against the target).

Within-batch gate (amendment 5): if the reading is "do not agree" and the within-batch kappa is at or below the upper
end of the cross-batch interval, the licensed sentence is the input-specific one.

Row (d) (amendment 6): the setting whose kappa is the lower median of the 80, then the held-out text whose g is the
lower median of its 2,048; on it, four off-set components and four matched kept components (draw 1), each drawn
without replacement with probability proportional to |p_c(y)|, seeded ("probe1-row-d", attack, start, batch, text).
The drawn arrow is the push while on, the negative of the measured switch-off push.

Post hoc, added after the reading at the head's request and printed as such in the 320-step row (nothing above
changes): the kept components' sign balance on the attack batch; the positive share of push mass for the off set and
the matched kept set, on the attack batch and the held-out texts, with session 5's interval on the held-out difference;
and kappa against the note's original chance level, the off set's attack-batch signs permuted among the off set within
each (weight matrix, usage band) cell, 8 permutations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_intervals as LI

STAGE_ROWS = {"s320": "n320", "s80": "n80"}
STEPS = {"n320": 320, "n80": 80}
CHANCE_LABEL = "probe1-chance"
ROW_D_LABEL = "probe1-row-d"
CHANCE_DRAWS = 8
PERMUTATION_LABEL = "probe1-permutation"  # post hoc: the note's original chance level
PERMUTATIONS = 8
MULTIPLIER = 1.0
DEGENERATE_CHANCE = 0.9
LINES = (0.0, 0.2, 0.5)
ROW_D_OFF, ROW_D_ON = 4, 4
N_CHUNKS = 2
POST_HOC_NOTE = ("post hoc: added after the reading at the head's request (session 7), from the saved pushes; the kept components' "
                 "sign balance on the attack batch, computed as the off set's is")
POST_HOC_NOTE_3 = ("post hoc: added after the reading at the head's request (session 7), from the saved pushes; kappa with the chance "
                   "level of Daniel's note as first written: the off set's attack-batch signs permuted among the off set within each "
                   "(weight matrix, usage band) cell, 8 permutations, seeded ('probe1-permutation', attack, start, steps, r)")
POST_HOC_NOTE_2 = ("post hoc: added after the reading at the head's request (session 7), from the saved pushes; the share of push mass "
                   "that is positive (along the pattern's shift) for the off set and the matched kept set (mean of the 8 draws), on the "
                   "attack batch and pooled over the held-out texts, with session 5's interval on the held-out off-minus-kept difference")
READINGS = ("mostly agree", "partly agree", "weakly agree", "do not agree", "undetermined", "undetermined (degenerate)")
SENTENCES = {
    "mostly agree": ("We may say: \"the switched-off components push the same way on text the search never saw, contrary to the paper's "
                     "premise\". We may not say that this explains the damage, unless the additivity ratio is near 1."),
    "do not agree, other way": "We may say: \"what carries over is not a shared first-order push; the damage arises some other way\". We may not name that way.",
    "do not agree, input-specific": "We may say: \"first-order pushes are specific to each input while the damage still carries over\".",
    "partly agree": "Print the number and keep the question marks.",
    "undetermined": "Print the number and keep the question marks.",
    "undetermined (degenerate)": "Kappa is not read; the marginal positive shares are reported instead. Print the number and keep the question marks.",
    "weakly agree": ("No sentence is fixed for this reading: amendment 4 added the line, and neither the note nor the plan says what it "
                     "licenses. The head decides."),
}


class Refusal(Exception):
    """The inputs are not the run's complete, checked set."""


# ----------------------------------------------------------------------------- sets and the matched chance draw


def setting_sets(flat: np.ndarray, lay: list[tuple[str, int]]) -> dict[str, np.ndarray]:
    """Flat indices: the off set O (components below one half), the kept components, and the off delta entries."""
    from vpd_audit_2 import probe1 as P1

    flat = np.asarray(flat, dtype=np.float32)
    comp = P1.component_positions(lay)
    delta = P1.delta_positions(lay)
    off = flat < np.float32(0.5)
    return {"off": comp[off[comp]], "kept": comp[~off[comp]], "off_delta": delta[off[delta]]}


def matched_kept(off: np.ndarray, kept: np.ndarray, codes: np.ndarray, seed: int) -> np.ndarray:
    """In each cell (code) that O occupies, min(|O there|, |kept there|) kept components, uniformly without replacement;
    cells in ascending order, one generator."""
    rng = np.random.default_rng(seed)
    cells, counts = np.unique(codes[np.asarray(off, dtype=np.int64)], return_counts=True)
    kcodes = codes[np.asarray(kept, dtype=np.int64)]
    picked = []
    for c, n in zip(cells, counts):
        pool = np.asarray(kept, dtype=np.int64)[kcodes == c]
        m = int(min(n, pool.size))
        if m:
            picked.append(rng.choice(pool, size=m, replace=False))
    return np.sort(np.concatenate(picked)).astype(np.int64) if picked else np.zeros(0, dtype=np.int64)


def chance_seed(attack: str, start: int, steps: int, draw: int) -> int:
    from vpd_audit_2.manifest import seed_of

    return seed_of(CHANCE_LABEL, attack, start, steps, draw)


def permuted_off_signs(sign_ref: np.ndarray, off: np.ndarray, codes: np.ndarray, seed: int) -> np.ndarray:
    """Post hoc (the note's original chance level): the reference signs with the off set's entries permuted among
    themselves within each (weight matrix, usage band) cell, cells in ascending order, one generator; every other entry
    unchanged."""
    rng = np.random.default_rng(seed)
    out = np.array(sign_ref, copy=True)
    off = np.asarray(off, dtype=np.int64)
    oc = codes[off]
    for c in np.unique(oc):
        idx = off[oc == c]
        out[idx] = sign_ref[idx[rng.permutation(idx.size)]]
    return out


def permutation_seed(attack: str, start: int, steps: int, r: int) -> int:
    from vpd_audit_2.manifest import seed_of

    return seed_of(PERMUTATION_LABEL, attack, start, steps, r)


# ----------------------------------------------------------------------------- the agreement of one table


def weighted_agreement(p: np.ndarray, ref_sign: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """Per text, the share of the push mass on the entries `idx` whose sign is the reference's: ref_sign is [E] (one
    reference) or [n, E] (one per text). NaN where the mass is zero."""
    q = np.asarray(p)[:, idx].astype(np.float64)
    r = ref_sign[idx] if ref_sign.ndim == 1 else ref_sign[:, idx]
    w = np.abs(q)
    agree = np.sign(q) == r
    den = w.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, (w * agree).sum(axis=1) / np.where(den > 0, den, 1.0), np.nan)


def unweighted_agreement(p: np.ndarray, ref_sign: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """Per text, the share of the entries `idx` with a nonzero push whose sign is the reference's."""
    q = np.asarray(p)[:, idx]
    r = ref_sign[idx] if ref_sign.ndim == 1 else ref_sign[:, idx]
    nz = q != 0
    n = nz.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, ((np.sign(q) == r) & nz).sum(axis=1) / np.where(n > 0, n, 1), np.nan)


def positive_share(p: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """Per row, the share of the push mass on `idx` that is positive."""
    q = np.asarray(p)[..., idx].astype(np.float64)
    den = np.abs(q).sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, np.clip(q, 0, None).sum(axis=-1) / np.where(den > 0, den, 1.0), np.nan)


def kappa(g_bar: float, g0_bar: float) -> float:
    return float((g_bar - g0_bar) / (1.0 - g0_bar)) if g0_bar != 1.0 else float("nan")


# ----------------------------------------------------------------------------- the reading


def reading(interval: tuple[float, float] | list[float], chance: float) -> str:
    """The note's lines with amendments 3 and 4, on kappa's interval and the pooled chance level."""
    if chance > DEGENERATE_CHANCE:
        return "undetermined (degenerate)"
    lo, hi = float(interval[0]), float(interval[1])
    if lo > LINES[2]:
        return "mostly agree"
    if lo <= LINES[0]:
        return "do not agree"
    if lo >= LINES[1] and hi <= LINES[2]:
        return "partly agree"
    if hi <= LINES[1]:
        return "weakly agree"
    return "undetermined"


def licence(read: str, cross_interval: tuple[float, float] | list[float], within_kappa: float) -> dict[str, Any]:
    """What the reading licenses for Figure 3's row (d) (the note's Section 5, amendment 5's gate)."""
    if read == "do not agree":
        as_low = bool(within_kappa <= float(cross_interval[1]))
        key = "do not agree, input-specific" if as_low else "do not agree, other way"
        return {"key": key, "sentence": SENTENCES[key], "within_as_low_as_cross": as_low,
                "gate": "within-batch kappa at or below the upper end of the cross-batch interval"}
    return {"key": read, "sentence": SENTENCES[read], "within_as_low_as_cross": None, "gate": None}


def row_d_draws_allowed(read: str) -> bool:
    """Whether the note's Section 5 lets row (d) show the real components: on "mostly agree" and "do not agree"."""
    return read in ("mostly agree", "do not agree")


# ----------------------------------------------------------------------------- the inputs


@dataclass
class Inputs:
    lay: list[tuple[str, int]]
    codes: np.ndarray  # each flat entry's (matrix, stratum) cell, `s6_build.cells_of`
    strata_flat: np.ndarray  # each flat entry's stratum (11 for a delta entry)
    attack: list[str]
    heldout: list[str]
    starts: list[int]
    text_ids_H: np.ndarray  # [K_H, 128]
    settings: dict[tuple[str, int, str], np.ndarray]  # (attack, start, row) to the saved flat setting
    s6_rounded: dict[tuple[str, str, int, str], float] | None = None  # (held-out, attack, start, row) to session 6's rounded harm


def unit_name(stage: str, batch: str, attack: str, start: int, chunk: int) -> str:
    return f"{stage}_{batch}_{attack}_s{start}_c{chunk}"


def expected_units(stage: str, attack: list[str], heldout: list[str], starts: list[int]) -> list[str]:
    names = [unit_name(stage, a, a, s, c) for a in attack for s in starts for c in range(N_CHUNKS)]
    names += [unit_name(stage, h, a, s, c) for h in heldout for a in attack for s in starts for c in range(N_CHUNKS)]
    return names


class Cells:
    """The collected unit files, each checked against the receipt when first read; a cell is its chunks joined."""

    def __init__(self, folder: Path, receipt: dict[str, str], stage: str) -> None:
        self.folder, self.receipt, self.stage = Path(folder), receipt, stage

    def require(self, names: list[str]) -> None:
        missing = [n for n in names if f"units/{n}.npz" not in self.receipt or not (self.folder / f"{n}.npz").is_file()]
        if missing:
            raise Refusal(f"{len(missing)} units of {self.stage} missing, the first {missing[0]}")

    def _load(self, name: str) -> dict[str, Any]:
        data = (self.folder / f"{name}.npz").read_bytes()
        if hashlib.sha256(data).hexdigest() != self.receipt.get(f"units/{name}.npz"):
            raise Refusal(f"{name} is not the file the receipt records")
        import io

        with np.load(io.BytesIO(data), allow_pickle=False) as z:
            out = {k: z[k] for k in z.files if k != "meta"}
            out["meta"] = json.loads(str(np.asarray(z["meta"]).reshape(-1)[0]))
        return out

    def get(self, batch: str, attack: str, start: int) -> dict[str, Any]:
        parts = [self._load(unit_name(self.stage, batch, attack, start, c)) for c in range(N_CHUNKS)]
        texts = np.concatenate([p["texts"] for p in parts])
        if not np.array_equal(texts, np.arange(texts.size)):
            raise Refusal(f"{batch} {attack} s{start}: the chunks do not cover the batch's texts in order")
        out = {"texts": texts, "meta": [p["meta"] for p in parts]}
        for key in ("intact", "pattern", "delta_norm_sum", "pattern_kl", "zero_direction_positions"):
            if all(key in p for p in parts):
                out[key] = np.concatenate([p[key] for p in parts])
        return out


# ----------------------------------------------------------------------------- one row


def _interval(num: np.ndarray, den: np.ndarray, kind: str, indices: Any, K: int, n_s: int) -> dict[str, Any]:
    combo = (lambda x: LI.Combo(a_cells=x)) if kind == "a" else (lambda x: LI.Combo(h_cells=x))
    r = LI.interval(combo(num), combo(den), LI.Presence.complete(K, K, n_s), multiplier=MULTIPLIER, indices=indices)
    return LI.record_of(r)


def row_statistics(cells: Cells, inp: Inputs, row: str, *, indices: Any) -> dict[str, Any]:
    """Every number of one row (n320 or n80): per cell means, the pooled values, kappa with its interval, the
    descriptions, and what row (d) needs."""
    att, held, starts = inp.attack, inp.heldout, inp.starts
    KA, KH, S = len(att), len(held), len(starts)
    steps = STEPS[row]
    shape = (KA, KH, S)
    cm = {k: np.full(shape, np.nan) for k in ("g", "g0", "g0p", "u", "u0", "pos", "pos0", "add", "add_delta", "g_delta", "kl", "zero_ref")}
    att_pos = {k: np.full((KA, S), np.nan) for k in ("off", "matched")}  # post hoc: per-text positive share on the attack texts
    pat = {k: np.full(shape, np.nan) for k in ("g", "g0")}
    within = {k: np.full((KA, S), np.nan) for k in ("g", "g0", "u", "u0", "add")}
    balance = np.full((KA, S), np.nan)
    balance_kept = np.full((KA, S), np.nan)  # post hoc (see POST_HOC_NOTE)
    balance_matched = np.full((KA, S), np.nan)  # post hoc
    balance_pattern = np.full((KA, S), np.nan)
    g_text: np.ndarray | None = None  # [KA, KH, S, texts], allocated at the first held-out cell
    sizes = {k: np.zeros((KA, S), dtype=np.int64) for k in ("off", "kept", "off_delta", "matched")}
    has_pattern = None
    checks = {"intact_max_abs_logit_difference": 0.0, "intact_max_text_kl": 0.0, "zero_direction_positions": 0}
    s6_pairs: list[tuple[float, float]] = []
    for i, a in enumerate(att):
        for k, s in enumerate(starts):
            sets = setting_sets(inp.settings[(a, s, row)], inp.lay)
            O, kept, od = sets["off"], sets["kept"], sets["off_delta"]
            K = [matched_kept(O, kept, inp.codes, chance_seed(a, s, steps, d)) for d in range(1, CHANCE_DRAWS + 1)]
            sizes["off"][i, k], sizes["kept"][i, k], sizes["off_delta"][i, k], sizes["matched"][i, k] = O.size, kept.size, od.size, K[0].size
            Od = np.concatenate([O, od])
            A_cell = cells.get(a, a, s)
            pa = A_cell["intact"].astype(np.float64)
            P = pa.sum(axis=0)
            sP = np.sign(P)
            O_zero = O[P[O] == 0]  # off-set components with a batch push of exactly zero: they agree with nothing
            balance[i, k] = float(positive_share(P[None, :], O)[0])
            balance_kept[i, k] = float(positive_share(P[None, :], kept)[0])
            balance_matched[i, k] = float(np.mean([positive_share(P[None, :], Kd)[0] for Kd in K]))
            perm_signs = [permuted_off_signs(sP, O, inp.codes, permutation_seed(a, s, steps, r)) for r in range(1, PERMUTATIONS + 1)]
            att_pos["off"][i, k] = float(np.mean(positive_share(pa, O)))
            att_pos["matched"][i, k] = float(np.mean([np.mean(positive_share(pa, Kd)) for Kd in K]))
            loo = np.sign(P[None, :] - pa)
            within["g"][i, k] = float(np.mean(weighted_agreement(pa, loo, O)))
            within["g0"][i, k] = float(np.mean([np.mean(weighted_agreement(pa, loo, Kd)) for Kd in K]))
            within["u"][i, k] = float(np.mean(unweighted_agreement(pa, loo, O)))
            within["u0"][i, k] = float(np.mean([np.mean(unweighted_agreement(pa, loo, Kd)) for Kd in K]))
            within["add"][i, k] = float(np.mean(pa[:, O].sum(axis=1) / A_cell["delta_norm_sum"]))
            if has_pattern is None:
                has_pattern = "pattern" in A_cell
            if has_pattern:
                PP = A_cell["pattern"].astype(np.float64).sum(axis=0)
                sPP = np.sign(PP)
                balance_pattern[i, k] = float(positive_share(PP[None, :], O)[0])
            for j, h in enumerate(held):
                c = cells.get(h, a, s)
                p = c["intact"]
                g = weighted_agreement(p, sP, O)
                if g_text is None:
                    g_text = np.full(shape + (p.shape[0],), np.nan)
                g_text[i, j, k] = g
                cm["g"][i, j, k] = float(np.mean(g))
                cm["g0"][i, j, k] = float(np.mean([np.mean(weighted_agreement(p, sP, Kd)) for Kd in K]))
                cm["g0p"][i, j, k] = float(np.mean([np.mean(weighted_agreement(p, sp, O)) for sp in perm_signs]))  # post hoc
                cm["u"][i, j, k] = float(np.mean(unweighted_agreement(p, sP, O)))
                cm["u0"][i, j, k] = float(np.mean([np.mean(unweighted_agreement(p, sP, Kd)) for Kd in K]))
                cm["pos"][i, j, k] = float(np.mean(positive_share(p, O)))
                cm["pos0"][i, j, k] = float(np.mean([np.mean(positive_share(p, Kd)) for Kd in K]))  # post hoc
                p64 = p.astype(np.float64)
                cm["add"][i, j, k] = float(np.mean(p64[:, O].sum(axis=1) / c["delta_norm_sum"]))
                cm["add_delta"][i, j, k] = float(np.mean(p64[:, Od].sum(axis=1) / c["delta_norm_sum"]))
                cm["g_delta"][i, j, k] = float(np.mean(weighted_agreement(p, sP, Od)))
                cm["kl"][i, j, k] = float(np.mean(c["pattern_kl"]))
                mass = np.abs(p64[:, O]).sum(axis=1)
                cm["zero_ref"][i, j, k] = float(np.mean(np.abs(p64[:, O_zero]).sum(axis=1) / mass)) if O_zero.size else 0.0
                for m in c["meta"]:
                    chk = m.get("intact_against_target", {})
                    checks["intact_max_abs_logit_difference"] = max(checks["intact_max_abs_logit_difference"], float(chk.get("max_abs_logit_difference", 0.0)))
                    checks["intact_max_text_kl"] = max(checks["intact_max_text_kl"], float(chk.get("max_text_kl", 0.0)))
                checks["zero_direction_positions"] += int(np.sum(c["zero_direction_positions"]))
                if inp.s6_rounded is not None and (h, a, s, row) in inp.s6_rounded:
                    s6_pairs.append((cm["kl"][i, j, k], inp.s6_rounded[(h, a, s, row)]))
                if has_pattern:
                    pp = c["pattern"]
                    pat["g"][i, j, k] = float(np.mean(weighted_agreement(pp, sPP, O)))
                    pat["g0"][i, j, k] = float(np.mean([np.mean(weighted_agreement(pp, sPP, Kd)) for Kd in K]))
    for name, arr in list(cm.items()) + [("within_" + k, v) for k, v in within.items()]:
        if not np.isfinite(arr).all():
            raise Refusal(f"{row}: a cell's {name} is not a number")

    if g_text is None or not np.isfinite(g_text).all():
        raise Refusal(f"{row}: a text's agreement is not a number")
    out: dict[str, Any] = {"row": row, "cells": int(KA * KH * S), "texts_per_cell": int(g_text.shape[-1])}
    gb, g0b = float(cm["g"].mean()), float(cm["g0"].mean())
    out["g_bar"], out["g0_bar"], out["kappa"] = gb, g0b, kappa(gb, g0b)
    out["interval"] = _interval(cm["g"] - cm["g0"], 1.0 - cm["g0"], "a", indices, KA, S)
    out["reading"] = reading(out["interval"]["interval"], g0b)
    wgb, wg0b = float(within["g"].mean()), float(within["g0"].mean())
    out["within"] = {"g_bar": wgb, "g0_bar": wg0b, "kappa": kappa(wgb, wg0b),
                     "interval": _interval(within["g"] - within["g0"], 1.0 - within["g0"], "h", indices, KA, S),
                     "unweighted": float(within["u"].mean()), "unweighted_chance": float(within["u0"].mean()),
                     "additivity": float(within["add"].mean())}
    out["licence"] = licence(out["reading"], out["interval"]["interval"], out["within"]["kappa"])
    out["sign_balance_attack"] = {"mean": float(balance.mean()), "min": float(balance.min()), "max": float(balance.max())}
    out["post_hoc_sign_balance_attack_kept"] = {"note": POST_HOC_NOTE, "all_kept": {"mean": float(balance_kept.mean()), "min": float(balance_kept.min()),
                                                                                   "max": float(balance_kept.max())},
                                                "matched_kept_mean_of_draws": {"mean": float(balance_matched.mean()), "min": float(balance_matched.min()),
                                                                               "max": float(balance_matched.max())}}
    diff = LI.interval(LI.Combo(a_cells=cm["pos"] - cm["pos0"]), None, LI.Presence.complete(KA, KH, S), multiplier=MULTIPLIER, indices=indices)
    out["post_hoc_positive_share"] = {
        "note": POST_HOC_NOTE_2,
        "attack_batch_push_mass": {"off": float(balance.mean()), "matched_kept": float(balance_matched.mean())},
        "attack_texts": {"off": float(att_pos["off"].mean()), "matched_kept": float(att_pos["matched"].mean())},
        "heldout_texts": {"off": float(cm["pos"].mean()), "matched_kept": float(cm["pos0"].mean())},
        "heldout_off_minus_matched_kept": LI.record_of(diff)}
    g0p = float(cm["g0p"].mean())
    perm_iv = _interval(cm["g"] - cm["g0p"], 1.0 - cm["g0p"], "a", indices, KA, S)
    out["post_hoc_permutation_baseline"] = {"note": POST_HOC_NOTE_3, "g_bar": gb, "g0_bar": g0p, "kappa": kappa(gb, g0p), "interval": perm_iv,
                                            "lines_would_read": reading(perm_iv["interval"], g0p)}
    out["positive_share_heldout"] = float(cm["pos"].mean())
    out["unweighted"] = {"agreement": float(cm["u"].mean()), "chance": float(cm["u0"].mean())}
    out["additivity"] = {"off_set": float(cm["add"].mean()), "off_set_and_off_delta": float(cm["add_delta"].mean()),
                         "off_set_min_cell": float(cm["add"].min()), "off_set_max_cell": float(cm["add"].max())}
    gdb = float(cm["g_delta"].mean())
    out["with_off_delta"] = {"g_bar": gdb, "kappa_against_the_same_chance": kappa(gdb, g0b),
                             "interval": _interval(cm["g_delta"] - cm["g0"], 1.0 - cm["g0"], "a", indices, KA, S)}
    out["per_setting_kappa"] = ((cm["g"] - cm["g0"]).mean(axis=1) / (1.0 - cm["g0"]).mean(axis=1)).tolist()
    out["sizes"] = {k: {"mean": float(v.mean()), "min": int(v.min()), "max": int(v.max())} for k, v in sizes.items()}
    out["mass_on_zero_batch_push"] = float(cm["zero_ref"].mean())
    out["pattern_kl_mean"] = float(cm["kl"].mean())
    if s6_pairs:
        ours, theirs = np.array(s6_pairs).T
        out["check_s6_rounded"] = {"cells": int(ours.size), "ratio_of_means": float(ours.mean() / theirs.mean()),
                                   "max_relative_difference": float(np.max(np.abs(ours - theirs) / theirs))}
    out["checks"] = checks
    if has_pattern:
        pgb, pg0b = float(pat["g"].mean()), float(pat["g0"].mean())
        out["full_pattern"] = {"g_bar": pgb, "g0_bar": pg0b, "kappa": kappa(pgb, pg0b),
                               "interval": _interval(pat["g"] - pat["g0"], 1.0 - pat["g0"], "a", indices, KA, S),
                               "sign_balance_attack_mean": float(balance_pattern.mean())}
    out["_g_text"] = g_text
    out["_cell_g"] = cm["g"]
    out["_cell_g0"] = cm["g0"]
    return out


# ----------------------------------------------------------------------------- row (d)


def lower_median_index(values: np.ndarray, keys: list[tuple[Any, ...]]) -> int:
    """The position of the lower median: sort ascending by value, ties by the keys, take entry (n - 1) // 2."""
    order = sorted(range(len(values)), key=lambda q: (float(values[q]), keys[q]))
    return order[(len(values) - 1) // 2]


def row_d(res: dict[str, Any], cells: Cells, inp: Inputs, row: str = "n320") -> dict[str, Any]:
    from vpd_audit_2 import probe1 as P1
    from vpd_audit_2.manifest import seed_of

    att, held, starts = inp.attack, inp.heldout, inp.starts
    ks = np.array(res["per_setting_kappa"])  # [KA, S]
    flat_keys = [(i, k) for i in range(len(att)) for k in range(len(starts))]
    q = lower_median_index(np.array([ks[i, k] for i, k in flat_keys]), flat_keys)
    i, k = flat_keys[q]
    a, s = att[i], starts[k]
    g = res["_g_text"][i, :, k, :]  # [KH, 128]
    tkeys = [(j, t) for j in range(len(held)) for t in range(g.shape[1])]
    qt = lower_median_index(np.array([g[j, t] for j, t in tkeys]), tkeys)
    j, t = tkeys[qt]
    h = held[j]
    sets = setting_sets(inp.settings[(a, s, row)], inp.lay)
    K1 = matched_kept(sets["off"], sets["kept"], inp.codes, chance_seed(a, s, STEPS[row], 1))
    p_y = cells.get(h, a, s)["intact"][t].astype(np.float64)
    P = cells.get(a, a, s)["intact"].astype(np.float64).sum(axis=0)
    rng = np.random.default_rng(seed_of(ROW_D_LABEL, a, s, h, int(t)))
    drawn = []
    for kind, pool, n in (("off", sets["off"], ROW_D_OFF), ("on", K1, ROW_D_ON)):
        w = np.abs(p_y[pool])
        n = min(n, int((w > 0).sum()))  # fewer only if the pool has fewer components with a push (never on the real layout)
        pick = rng.choice(pool, size=n, replace=False, p=w / w.sum()) if n else np.zeros(0, dtype=np.int64)
        for e in pick:
            name, local = P1.entry_of(int(e), inp.lay)
            drawn.append({"cell": kind, "flat_entry": int(e), "module": name, "component": local, "stratum": int(inp.strata_flat[e]),
                          "switch_off_push_on_text": float(p_y[e]), "drawn_arrow_on_text": int(-np.sign(p_y[e])),
                          "batch_push_on_attack": float(P[e]), "drawn_arrow_on_attack": int(-np.sign(P[e])),
                          "agrees": bool(np.sign(p_y[e]) == np.sign(P[e]))})
    return {"setting": {"attack": a, "start": int(s), "row": row, "kappa": float(ks[i, k])}, "text": {"batch": h, "index": int(t),
            "text_id": str(inp.text_ids_H[j, t]), "g": float(g[j, t])}, "components": drawn, "pooled_kappa": res["kappa"],
            "licensed_to_draw": row_d_draws_allowed(res["reading"])}


# ----------------------------------------------------------------------------- the report


def _iv(r: dict[str, Any]) -> str:
    lo, hi = r["interval"]
    return f"{r['estimate']:.4f} [{lo:.4f}, {hi:.4f}] (start share {r['start_share'] if r['start_share'] is None else round(r['start_share'], 3)})"


def report(rows: dict[str, dict[str, Any]], d: dict[str, Any] | None, validation: dict[str, Any]) -> str:
    L = ["Probe 1: do the pattern's pushes point the same way on text it never saw? (session 7, plan 5; Daniel's specification",
         "with the plan's six amendments). Pushes are first-order, at the intact model, projected on the full rounded pattern's",
         "logit shift and summed over positions; a positive push means switching the component off moves the output along the",
         "pattern's shift.", "",
         f"Validation (the note's Section 2): {'passed' if validation['passes'] else 'FAILED'}. Sign share above the bottom decile "
         f"{validation['sign_share_above']:.4f} (at least 0.9), Spearman {validation['spearman_all']:.4f} (at least 0.8), over "
         f"{validation['pairs']} pairs.", ""]
    for row, r in rows.items():
        if row == "n320":
            L += [f"THE DECIDING ROW: settings at {STEPS[row]} steps, {r['cells']} held-out cells of 128 texts.",
                  f"  g-bar (agreement) {r['g_bar']:.4f}; g0-bar (chance, matched kept components) {r['g0_bar']:.4f}.",
                  f"  Agreement beyond chance kappa: {_iv(r['interval'])}.",
                  f"  Reading: {r['reading'].upper()}.",
                  f"  Licensed: {r['licence']['sentence']}"]
            pb = r["post_hoc_permutation_baseline"]
            L.append(f"  POST HOC (added after the reading, at the head's request), baseline = the note's original chance level, the off set's "
                     f"attack-batch signs permuted within weight matrix and usage band (8 permutations): g0-bar {pb['g0_bar']:.4f}; kappa "
                     f"{_iv(pb['interval'])}; the pre-registered lines would read: {pb['lines_would_read']}. Not the reading.")
        else:
            L += [f"Description (the note's Section 3): settings at {STEPS[row]} steps, {r['cells']} held-out cells of 128 texts.",
                  f"  g-bar (agreement) {r['g_bar']:.4f}; g0-bar (chance, matched kept components) {r['g0_bar']:.4f}.",
                  f"  Agreement beyond chance kappa: {_iv(r['interval'])}.",
                  f"  The lines would read: {r['reading']} (description only; nothing is licensed by this row)."]
        if r["licence"]["within_as_low_as_cross"] is not None:
            L.append(f"  Within-batch gate (amendment 5): within-batch kappa {r['within']['kappa']:.4f}; at or below the cross-batch interval's "
                     f"upper end: {r['licence']['within_as_low_as_cross']}.")
        L += ["  Beside it:",
              f"    attack batch's sign balance (positive share of the off set's batch-push mass): mean {r['sign_balance_attack']['mean']:.4f}, "
              f"range {r['sign_balance_attack']['min']:.4f} to {r['sign_balance_attack']['max']:.4f};"]
        if row == "n320":
            ph = r["post_hoc_sign_balance_attack_kept"]
            L.append(f"    POST HOC (added after the reading, at the head's request): the kept components' sign balance on the attack batch, "
                     f"computed the same way: all kept, mean {ph['all_kept']['mean']:.4f}, range {ph['all_kept']['min']:.4f} to {ph['all_kept']['max']:.4f}; "
                     f"matched kept (mean of the 8 draws), mean {ph['matched_kept_mean_of_draws']['mean']:.4f}, range "
                     f"{ph['matched_kept_mean_of_draws']['min']:.4f} to {ph['matched_kept_mean_of_draws']['max']:.4f};")
            ps = r["post_hoc_positive_share"]
            dd = ps["heldout_off_minus_matched_kept"]
            L.append(f"    POST HOC (added after the reading, at the head's request): share of push mass that is positive (along the pattern's "
                     f"shift), off set against matched kept (mean of the 8 draws): attack batch, of the batch push {ps['attack_batch_push_mass']['off']:.4f} "
                     f"against {ps['attack_batch_push_mass']['matched_kept']:.4f}; attack texts, per text {ps['attack_texts']['off']:.4f} against "
                     f"{ps['attack_texts']['matched_kept']:.4f}; held-out texts, per text {ps['heldout_texts']['off']:.4f} against "
                     f"{ps['heldout_texts']['matched_kept']:.4f}; held-out off minus kept {_iv(dd)};")
        L += [f"    marginal positive share on held-out texts: {r['positive_share_heldout']:.4f};",
              f"    unweighted sign agreement {r['unweighted']['agreement']:.4f}, its chance {r['unweighted']['chance']:.4f};",
              f"    within the attack batch (each text against the other 127): g-bar {r['within']['g_bar']:.4f}, chance {r['within']['g0_bar']:.4f}, "
              f"kappa {_iv(r['within']['interval'])}; unweighted {r['within']['unweighted']:.4f} against {r['within']['unweighted_chance']:.4f};",
              f"    additivity ratio (first-order sum over O / sum_t |Delta|): held-out {r['additivity']['off_set']:.4f} (cells "
              f"{r['additivity']['off_set_min_cell']:.4f} to {r['additivity']['off_set_max_cell']:.4f}), with the off delta entries "
              f"{r['additivity']['off_set_and_off_delta']:.4f}; on the attack batch {r['within']['additivity']:.4f};",
              f"    with the off delta entries counted in O: g-bar {r['with_off_delta']['g_bar']:.4f}, kappa {_iv(r['with_off_delta']['interval'])};",
              f"    share of the held-out push mass on O at components whose batch push is exactly zero (counted as disagreeing): "
              f"{r['mass_on_zero_batch_push']:.2e};",
              f"    set sizes per setting (mean, min, max): off {r['sizes']['off']}, kept {r['sizes']['kept']}, off delta {r['sizes']['off_delta']}, "
              f"matched kept (draw 1) {r['sizes']['matched']};"]
        if "full_pattern" in r:
            fp = r["full_pattern"]
            L.append(f"    at the full pattern (description; circular on the attack batch): g-bar {fp['g_bar']:.4f}, chance {fp['g0_bar']:.4f}, "
                     f"kappa {_iv(fp['interval'])}; attack sign balance {fp['sign_balance_attack_mean']:.4f};")
        L.append(f"    checks: the pattern's mean KL from the intact model {r['pattern_kl_mean']:.3f} nats"
                 + (f"; against session 6's rounded control on {r['check_s6_rounded']['cells']} S4 cells, ratio of means "
                    f"{r['check_s6_rounded']['ratio_of_means']:.4f}, largest relative difference {r['check_s6_rounded']['max_relative_difference']:.4f}"
                    if "check_s6_rounded" in r else "")
                 + f"; intact against target: largest logit difference {r['checks']['intact_max_abs_logit_difference']:.2e}, largest text KL "
                 f"{r['checks']['intact_max_text_kl']:.2e}; positions with a zero direction {r['checks']['zero_direction_positions']}.")
        L.append("")
    if d is not None:
        L += ["Row (d) (amendment 6): eight real components, on the held-out text with the lower-median g in the setting with the lower-median kappa.",
              f"  Setting {d['setting']['attack']} from start {d['setting']['start']} at {STEPS[d['setting']['row']]} steps (its kappa "
              f"{d['setting']['kappa']:.4f}); text {d['text']['text_id']}, {d['text']['batch']} position {d['text']['index']} (its g {d['text']['g']:.4f}).",
              f"  Pooled kappa to print beside them: {d['pooled_kappa']:.4f}. The reading licenses drawing them: {d['licensed_to_draw']}.",
              "  The drawn arrow is the component's push while on: the NEGATIVE of the measured switch-off push. + points along the",
              "  full pattern's shift on that text (toward the damage), - against it.",
              "    cell  module               comp  band  switch-off push on text   arrow  batch push on attack   arrow on A  agrees"]
        for c in d["components"]:
            L.append(f"    {c['cell']:<4}  {c['module']:<19}  {c['component']:>4}  {c['stratum']:>4}  {c['switch_off_push_on_text']:>+23.4e}  "
                     f"{'+' if c['drawn_arrow_on_text'] > 0 else '-' if c['drawn_arrow_on_text'] < 0 else '0':>5}  {c['batch_push_on_attack']:>+20.4e}  "
                     f"{'+' if c['drawn_arrow_on_attack'] > 0 else '-' if c['drawn_arrow_on_attack'] < 0 else '0':>10}  {c['agrees']}")
    return "\n".join(L) + "\n"


def _jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    return x


# ----------------------------------------------------------------------------- the real inputs


def load_inputs(rows: list[str]) -> Inputs:
    from vpd_audit_2 import lead_launch as LL
    from vpd_audit_2 import pilot as P
    from vpd_audit_2 import probe1_run as PR
    from vpd_audit_2 import s6_build as B
    from vpd_audit_2 import s6_run as SR

    lay = P.layout()
    strata, _ = LL.strata_by_module()
    codes = B.cells_of(lay, strata)
    lead = SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT)
    attack = [str(x) for x in lead["attack_names"]]
    heldout = [str(x) for x in lead["heldout_names"]]
    starts = [int(x) for x in lead["starts"]]
    settings = {}
    for a in attack:
        for s in starts:
            unit = PR.read_run_unit_local(a, s)
            for row in rows:
                settings[(a, s, row)] = B.saved(unit, row)[0]
    s6 = s6_rounded_harms(heldout, attack, starts, rows)
    return Inputs(lay=lay, codes=codes, strata_flat=codes % 12, attack=attack, heldout=heldout, starts=starts, text_ids_H=np.asarray(lead["text_ids_H"]),
                  settings=settings, s6_rounded=s6)


def s6_rounded_harms(heldout: list[str], attack: list[str], starts: list[int], rows: list[str]) -> dict[tuple[str, str, int, str], float]:
    """Session 6's control (d), the rounded setting's harm on the S4 batches, from its checked unit files."""
    from vpd_audit_2 import s6_build as B
    from vpd_audit_2 import s6_run as SR
    from vpd_audit_2 import s6_variants as V

    receipt = json.load(open(SR.RESULTS / "units_receipt.json"))["files"]
    names = [f"controls_{h}_{a}_s{s}" for h in B.S4 if h in heldout for a in attack for s in starts]
    units = V.checked_units(SR.LOCAL_UNITS, receipt, names)
    return {(h, a, s, row): units.harm(f"controls_{h}_{a}_s{s}", f"d|rounded|{row}") for h in B.S4 if h in heldout for a in attack for s in starts
            for row in rows}


def compute(results: Path, *, units_folder: Path | None = None, inputs: Inputs | None = None, indices: Any = None) -> dict[str, Any]:
    from vpd_audit_2 import probe1_run as PR

    results = Path(results)
    validation = json.load(open(results / "validation.json"))
    if not validation.get("passes"):
        raise Refusal("the validation did not pass: the note's fallback decides, not this reading")
    receipt = json.load(open(results / "backup.json"))
    files = receipt["files"]
    folder = Path(units_folder) if units_folder is not None else PR.LOCAL / PR.UNITS
    if receipt.get("commit") != validation.get("commit"):
        raise Refusal("the units and the validation are not from one commit")
    stages = [st for st in STAGE_ROWS if any(name.startswith(f"units/{st}_") for name in files)]
    if "s320" not in stages:
        raise Refusal("the 320-step stage is not collected")
    rows = [STAGE_ROWS[st] for st in stages]
    inp = load_inputs(rows) if inputs is None else inputs
    K = len(inp.attack)
    indices = LI.make_indices(K) if indices is None else indices
    out: dict[str, Any] = {"validation": validation, "commit": receipt.get("commit"), "rows": {}}
    cells_by_row = {}
    for st in stages:
        cells = Cells(folder, files, st)
        names = expected_units(st, inp.attack, inp.heldout, inp.starts)
        cells.require(names)
        out["rows"][STAGE_ROWS[st]] = row_statistics(cells, inp, STAGE_ROWS[st], indices=indices)
        cells_by_row[STAGE_ROWS[st]] = cells
    out["row_d"] = row_d(out["rows"]["n320"], cells_by_row["n320"], inp, "n320")
    return out


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.stderr.write("usage: python -m vpd_audit_2.probe1_read results/s7_probe1\n")
        return 2
    results = Path(argv[0])
    out = compute(results)
    text = report(out["rows"], out["row_d"], out["validation"])
    (results / "reading.txt").write_text(text)
    (results / "record.json").write_text(json.dumps(_jsonable(out), indent=1, sort_keys=True) + "\n")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
