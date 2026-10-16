"""The reading specification's row cases on made-up cells (`freeze/amendment1_specs/output_and_reading_spec.md`, Section 5.2), as inputs.

The recipe, unless a case says otherwise: 16 attack batches, 16 held-out batches, 5 starts, 8 shuffled copies; `start`
0.21 and `own20` 0.78; `attack_start` equal to the start mean and `attack_own` equal to the `own` mean; every array
equals its stated mean times (1 + 0.002 u), with u an independent standard normal draw per entry from a generator
seeded with the case number. A held-out pattern of size delta replaces the noise on `own` by adding delta (-1)^j to
held-out batch j.

Every expected value in the tests comes from the specification's table, never from this code's output.
"""

from __future__ import annotations

from typing import Any

import numpy as np

K, NS, R = 16, 5, 8


def arrays_for(seed: int, table: str, key: float, *, own: Any, carried: Any, shuffled: Any, start: Any = 0.21, own20: Any = 0.78,
               attack_start: Any = None, attack_own: Any = None, noise: float = 0.002, pattern: float | None = None,
               shuffled_equals_carried: bool = False, attack_missing: np.ndarray | None = None,
               heldout_missing: np.ndarray | None = None, past5: tuple[np.ndarray, np.ndarray] | None = None) -> dict[str, Any]:
    """One row's arrays in the names of the output specification's Section 2.1. Means may be numbers or arrays that
    broadcast to the array's shape ([j, s] for held-out arrays, [i, s] for attack arrays, [i, j, s] for cells)."""
    rng = np.random.default_rng(seed)

    def noisy(mean: Any, shape: tuple[int, ...]) -> np.ndarray:
        m = np.broadcast_to(np.asarray(mean, dtype=np.float64), shape)
        return m * (1.0 + noise * rng.standard_normal(shape))

    own_mean = np.broadcast_to(np.asarray(own, dtype=np.float64), (K, NS))
    out: dict[str, Any] = {"table": table, "key": key, "attack_names": [f"A{i + 1}" for i in range(K)],
                           "heldout_names": [f"H{j + 1}" for j in range(K)], "starts": [9, 10, 11, 12, 13]}
    out["start"] = noisy(start, (K, NS))
    own_noisy = noisy(own_mean, (K, NS))
    if pattern is not None:  # the pattern replaces the noise on `own`
        own_noisy = own_mean + pattern * ((-1.0) ** np.arange(1, K + 1))[:, None]
    out["own"] = own_noisy
    out["own20"] = noisy(own20, (K, NS))
    out["carried"] = noisy(carried, (K, K, NS))
    if shuffled_equals_carried:
        rng.standard_normal((K, K, NS, R))  # keep the generator's later draws where they would be
        out["shuffled"] = np.repeat(out["carried"][..., None], R, axis=-1)
    else:
        mean = np.asarray(shuffled, dtype=np.float64)
        out["shuffled"] = noisy(mean[..., None] if mean.ndim else mean, (K, K, NS, R))
    start_mean = float(np.mean(np.broadcast_to(np.asarray(start, dtype=np.float64), (K, NS))))
    out["attack_start"] = noisy(start_mean if attack_start is None else attack_start, (K, NS))
    out["attack_own"] = noisy(float(own_mean.mean()) if attack_own is None else attack_own, (K, NS))
    a_missing = np.zeros((K, NS), dtype=bool) if attack_missing is None else attack_missing
    b_missing = np.zeros((K, NS), dtype=bool) if heldout_missing is None else heldout_missing
    out["attack_present"], out["heldout_present"] = ~a_missing, ~b_missing
    out["attack_missing"], out["heldout_missing"] = a_missing, b_missing
    out["carried"] = np.where(a_missing[:, None, :], np.nan, out["carried"])
    out["shuffled"] = np.where(a_missing[:, None, :, None], np.nan, out["shuffled"])
    out["attack_own"] = np.where(a_missing, np.nan, out["attack_own"])
    out["own"] = np.where(b_missing, np.nan, out["own"])
    out["moved_share"] = np.full((K, NS), 0.41)
    out["mean_abs_change"] = np.full((K, NS), 0.43)
    if table == "step":
        for side, mean, k in (("attack", out["attack_own"], 0), ("heldout", out["own"], 1)):
            past = {level: np.nan_to_num(mean) >= level for level in (2.0, 5.0, 10.0)}
            if past5 is not None:
                past[5.0] = past5[k]
            out[f"{side}_past"] = past
            out[f"{side}_cycling"] = np.zeros((K, NS), dtype=bool)
    return out


def _starts() -> np.ndarray:
    return np.arange(1, NS + 1, dtype=np.float64)


def _missing(batches: list[int], extra: list[tuple[int, int]] = ()) -> np.ndarray:
    m = np.zeros((K, NS), dtype=bool)
    for b in batches:
        m[b, :] = True
    for b, s in extra:
        m[b, s] = True
    return m


def _broken_out() -> np.ndarray:
    """Case R16: search (b, s) is broken out when (b + s) mod 5 = 0, with b from 1 to 16 and s from 1 to 5."""
    b = np.arange(1, K + 1)[:, None]
    s = np.arange(1, NS + 1)[None, :]
    return (b + s) % 5 == 0


def case(name: str) -> dict[str, Any]:
    """The inputs of one case: `arrays`, and for R17 also `before` (the setting after step 319)."""
    if name == "R1":
        return {"arrays": arrays_for(1, "step", 320, own=25.5, carried=23.0, shuffled=0.43)}
    if name == "R2":
        return {"arrays": arrays_for(2, "step", 320, own=25.0, carried=3.0, shuffled=0.5)}
    if name == "R3":
        return {"arrays": arrays_for(3, "step", 20, own=0.78, carried=0.70, shuffled=0.62)}
    if name == "R4":
        return {"arrays": arrays_for(4, "step", 20, own=0.78, carried=0.74, shuffled=0.76)}
    if name == "R5":
        return {"arrays": arrays_for(5, "step", 20, own=0.78, carried=0.74, shuffled=0.76, pattern=0.2)}
    if name == "R6":
        return {"arrays": arrays_for(6, "step", 40, own=0.80, carried=0.70, shuffled=1.00)}
    if name == "R7":
        return {"arrays": arrays_for(7, "step", 40, own=0.80, carried=0.25, shuffled=0.40)}
    if name == "R8":
        return {"arrays": arrays_for(8, "step", 320, own=25.0, carried=5.168, shuffled=0.43, pattern=8.0)}
    if name == "R9":
        return {"arrays": arrays_for(9, "step", 40, own=0.80, carried=0.60, shuffled=0.58)}
    if name == "R10":
        return {"arrays": arrays_for(10, "step", 40, own=0.80, carried=0.60, shuffled=None, shuffled_equals_carried=True)}
    if name == "R11":
        return {"arrays": arrays_for(11, "step", 20, own=0.83, carried=0.70, shuffled=0.60, start=0.24, noise=0.0)}
    if name == "R12":
        s = _starts()
        return {"arrays": arrays_for(12, "step", 320, own=s[None, :] + 10, carried=s[None, None, :] + 6, shuffled=s[None, None, :] + 0.2,
                                     start=s[None, :], own20=s[None, :] + 0.5)}
    if name == "R13":
        own = np.full((K, NS), 10.21)
        own[0, 0] = 0.22
        return {"arrays": arrays_for(13, "step", 320, own=own, carried=6.21, shuffled=0.43)}
    if name == "R14":
        return {"arrays": arrays_for(14, "level", 2.0, own=40.0, carried=36.0, shuffled=0.43)}
    if name == "R15a":
        return {"arrays": arrays_for(15, "level", 10.0, own=10.8, carried=8.48, shuffled=0.41, attack_missing=_missing([0, 1]))}
    if name == "R15b":
        return {"arrays": arrays_for(15, "level", 10.0, own=10.8, carried=8.48, shuffled=0.41, attack_missing=_missing([0, 1], [(2, 0)]))}
    if name == "R15c":
        return {"arrays": arrays_for(15, "level", 10.0, own=10.8, carried=8.48, shuffled=0.41, heldout_missing=_missing([0, 1], [(2, 0)]))}
    if name == "R16":
        out_ = _broken_out()
        own = np.where(out_, 20.21, 3.21)
        carried = np.broadcast_to(np.where(out_, 18.21, 1.11)[:, None, :], (K, K, NS))
        return {"arrays": arrays_for(16, "step", 80, own=own, carried=carried, shuffled=0.40, attack_own=own, past5=(out_, out_))}
    if name == "R17":
        main = arrays_for(17, "step", 320, own=25.5, carried=23.0, shuffled=0.43)
        prev = arrays_for(1700, "step", 319, own=25.0, carried=3.0, shuffled=0.43)
        prev["start"], prev["own20"], prev["attack_start"] = main["start"], main["own20"], main["attack_start"]
        prev["shuffled"] = None
        return {"arrays": main, "before": prev}
    if name == "R18":
        return {"arrays": arrays_for(18, "level", 10.0, own=10.8, carried=1.5, shuffled=0.41)}
    raise KeyError(name)


# ----------------------------------------------------------------------------- whole made-up tables


def synthetic_records(K_: int, ns: int, seed: int, low: int = 0) -> np.ndarray:
    """Own-batch harm records [K_, ns, 321] that rise smoothly from a start near 0.2 to a plateau between 12 and 30
    nats, so that every level is crossed; the first `low` searches (in batch order, start 0 first) plateau near 4 nats
    and never reach 5 or 10."""
    rng = np.random.default_rng(seed)
    k = np.arange(321, dtype=np.float64)
    start = 0.2 + 0.02 * rng.random((K_, ns))
    plateau = 12.0 + 18.0 * rng.random((K_, ns))
    flat = np.zeros(K_ * ns, dtype=bool)
    flat[:low] = True
    plateau = np.where(flat.reshape(K_, ns), 4.0, plateau)
    rate = 30.0 + 40.0 * rng.random((K_, ns))
    return start[..., None] + plateau[..., None] * (1.0 - np.exp(-k[None, None, :] / rate[..., None]))


def synthetic_table(K_: int = 4, ns: int = 5, seed: int = 0, *, retention: float = 0.6, shuffled: float = 0.4, low_attack: int = 0,
                    low_heldout: int = 0, arm: str = "lead", setting_names: tuple[str, ...] | None = None, per_text: Any = True,
                    float32_exact: bool = False, excluded_H: np.ndarray | None = None, shuffled_equals_carried: bool = False,
                    rec_A: np.ndarray | None = None, rec_H: np.ndarray | None = None) -> dict[str, Any]:
    """A complete made-up table: carried-over harm is the held-out start's harm plus `retention` times the attack
    setting's added harm, and shuffled copies do `shuffled` nats, each with 1 percent noise.

    `float32_exact` rounds every harm to a float32 value, so that the mean of 128 equal per-text harms is exactly the
    batch harm. `per_text` may be a function of the finished core table that returns the six per-text arrays."""
    from vpd_audit_2 import lead_table as LT

    def exact(x: np.ndarray) -> np.ndarray:
        return x.astype(np.float32).astype(np.float64) if float32_exact else x

    names = LT.SETTINGS_LEAD if setting_names is None else setting_names
    rng = np.random.default_rng(seed + 1000)
    rec_A = exact(synthetic_records(K_, ns, seed, low_attack) if rec_A is None else np.asarray(rec_A, dtype=np.float64))
    rec_H = exact(synthetic_records(K_, ns, seed + 1, low_heldout) if rec_H is None else np.asarray(rec_H, dtype=np.float64))
    Q = len(names)
    probe = LT.made_up_table(rec_A, rec_H, np.zeros((K_, K_, ns, Q)), np.zeros((K_, K_, ns, Q, LT.N_SHUFFLES)), setting_names=names)
    added = np.nan_to_num(probe["own_A"] - probe["init_A"][:, :, None])  # [K_A, ns, Q]
    carried = exact(probe["init_H"][None, :, :, None] + retention * added[:, None, :, :] * (1.0 + 0.01 * rng.standard_normal((K_, K_, ns, Q))))
    shuf = exact(shuffled * (1.0 + 0.01 * rng.standard_normal((K_, K_, ns, Q, LT.N_SHUFFLES))))
    if shuffled_equals_carried:
        shuf = np.repeat(carried[..., None], LT.N_SHUFFLES, axis=-1)
    kwargs: dict[str, Any] = {"arm": arm, "setting_names": names, "scenario": "synthetic", "seed": seed, "excluded_H": excluded_H}
    if shuffled_equals_carried:
        kwargs.update(moved_alive=0.0, absmean_alive=0.0)
    if callable(per_text):
        core = LT.made_up_table(rec_A, rec_H, carried, shuf, per_text=True, **kwargs)
        return LT.made_up_table(rec_A, rec_H, carried, shuf, per_text=per_text(core), **kwargs)
    return LT.made_up_table(rec_A, rec_H, carried, shuf, per_text=per_text, **kwargs)
