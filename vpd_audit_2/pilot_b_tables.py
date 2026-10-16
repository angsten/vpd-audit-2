"""Plan 6 of the research log, B4: Part B's derived tables (plan 6 of the research log, Section 6; the pre-registration check's amendments).

    uv run python -m vpd_audit_2.pilot_b_tables      (reads results/s4_pilot/part_b/ and cq_prices/, writes part_b/tables.json)

Sealing (Section 3): the output holds widths, variance components, prices (Pi, from labels), degrees of freedom, and yes or
no only. It never holds V-bar, V-bar minus Pi, a point estimate, an interval's ends, or a per-arm mean of V.

Per text i, for a version, a reading, and a freed arm a (paired with the original arm):
  - the adversarial difference X: G (freed minus original harm) or J, per seed s (and partition p for versions (i), (iii));
  - the stochastic difference St, per draw d;
  - V = 0.5 X + 0.5 St; V-bar_i averages X over seeds (and partitions) and St over draws.
sigma2_seed and sigma2_route are on V's scale (each half times 0.5, plan 6 of the research log answer 2).
"""

from __future__ import annotations

import json
import math
from typing import Any

import numpy as np

from vpd_audit_2 import env

PILOT = env.REPO_ROOT / "results" / "s4_pilot"
B_BOOT = 10_000
FORMS = ("V_G", "V_J")
VERSIONS = {"i@20": ("set", 20), "iii@40": ("set", 40), "iii@80": ("set", 80), "ii": ("text", None)}
ARMS = ("nominal", "saturated", "unsaturated")


def tq(nu: float) -> float:
    from scipy.stats import t

    return float(t.ppf(0.975, nu))


# ----------------------------------------------------------------------------- per-text arrays from the raw records


def arrays(raw: dict[str, Any], version: str, arm: str, form: str) -> dict[str, np.ndarray]:
    """X[i, p, s] (versions (i), (iii); p over 4 partitions) or X[i, 1, s] (version (ii)); St[i, d]."""
    kind, n = VERSIONS[version]
    st = raw["stochastic"]
    n_draws = len([k for k in st if k.startswith("original|d")])
    St = np.array([[st[f"{arm}|d{d}"][i] - st[f"original|d{d}"][i] for d in range(n_draws)] for i in range(32)])
    if kind == "set":
        seeds = sorted({int(k.split("|")[1][1:]) for k in raw["partitions"]["1"]["set0"]["harm"]})
        X = np.full((32, 4, len(seeds)), np.nan)
        for p in range(1, 5):
            for sk in ("set0", "set1"):
                sd = raw["partitions"][str(p)][sk]
                for r, i in enumerate(sd["texts"]):
                    for si, s in enumerate(seeds):
                        if form == "V_G":
                            X[i, p - 1, si] = sd["harm"][f"{arm}|s{s}|n{n}"][r] - sd["harm"][f"original|s{s}|n{n}"][r]
                        else:
                            X[i, p - 1, si] = sd["J"][f"{arm}|s{s}|n{n}"][r]
    else:
        seeds = sorted({int(k.split("|")[1][1:]) for k in raw["v2"] if k.startswith("t0|")})
        X = np.full((32, 1, len(seeds)), np.nan)
        for i in range(32):
            for si, s in enumerate(seeds):
                rec = raw["v2"][f"t{i}|s{s}"]
                X[i, 0, si] = rec["G"][arm]["fill"] if form == "V_G" else rec["J"][arm]["fill"]
    assert not np.isnan(X).any()
    return {"X": X, "St": St}


def v_bar(a: dict[str, np.ndarray]) -> np.ndarray:
    return 0.5 * a["X"].mean(axis=(1, 2)) + 0.5 * a["St"].mean(axis=1)


# ----------------------------------------------------------------------------- B4.1


def seed_route_text(a: dict[str, np.ndarray]) -> dict[str, Any]:
    s2_seed = float(np.mean(np.var(0.5 * a["X"], axis=2, ddof=1)))
    s2_route = float(np.mean(np.var(0.5 * a["St"], axis=1, ddof=1)))
    s2_text = float(np.var(v_bar(a), ddof=1))

    def smallest(s2: float) -> int | str:
        for n in (4, 8, 16):
            if s2 / n <= 0.25 * s2_text:
                return n
        return "above 16 (capped at 16)"

    return {"sigma2_seed": s2_seed, "sigma2_route": s2_route, "sigma2_text": s2_text, "n_s": smallest(s2_seed), "n_r": smallest(s2_route)}


# ----------------------------------------------------------------------------- B4.2


def bootstrap_h(vbar: np.ndarray, T: np.ndarray, key: tuple) -> dict[str, Any]:
    """The percentile bootstrap over the 32 texts of mean(V-bar_i - T_i / 512), resampling pairs; only h is returned."""
    from vpd_audit_2.manifest import MASTER, seed_of

    d = vbar - T / 512.0
    rng = np.random.default_rng(seed_of("pilot-b4-bootstrap", *key))
    idx = rng.integers(0, d.size, size=(B_BOOT, d.size))
    reps = d[idx].mean(axis=1)
    lo, hi = np.percentile(reps, [2.5, 97.5])
    point = d.mean()
    return {"h": float(max(point - lo, hi - point)), "B": B_BOOT, "seed_key": [MASTER, "pilot-b4-bootstrap", *key]}


def set_term(a: dict[str, np.ndarray], partitions: dict[str, Any]) -> dict[str, Any]:
    """Q1-SS-2 with amendment 3's degrees of freedom: within-partition differences of the two set means of V."""
    vip = 0.5 * a["X"].mean(axis=2) + 0.5 * a["St"].mean(axis=1)[:, None]  # [i, p]
    diffs, within = [], []
    for p in range(1, 5):
        sets = [partitions[str(p)][sk] for sk in ("set0", "set1")]
        m = [vip[s, p - 1].mean() for s in sets]
        diffs.append(0.5 * (m[0] - m[1]) ** 2)
        within += [np.var(vip[s, p - 1], ddof=1) for s in sets]
    A_ = float(np.mean(diffs))
    s2w = float(np.mean(within))
    B_ = s2w / 16
    s2set_u = A_ - B_
    nu = (A_ - B_) ** 2 / (A_ ** 2 / 4 + B_ ** 2 / 30) if (A_ or B_) else 1.0
    return {"sigma2_set": max(0.0, s2set_u), "sigma2_set_untruncated": s2set_u, "sigma2_w": s2w, "nu_set": float(min(4.0, max(1.0, nu)))}


def seed_term(a: dict[str, np.ndarray], partitions: dict[str, Any]) -> dict[str, Any]:
    """Q1-SS-3 as amended: the two-way analysis of variance of the 8 set means of V by seed."""
    ns = a["X"].shape[2]
    st_mean = a["St"].mean(axis=1)
    rows = []
    for p in range(1, 5):
        for sk in ("set0", "set1"):
            s_idx = partitions[str(p)][sk]
            rows.append([float((0.5 * a["X"][s_idx, p - 1, s] + 0.5 * st_mean[s_idx]).mean()) for s in range(ns)])
    Y = np.array(rows)  # [8 sets, ns seeds]
    mu = Y.mean()
    ms_seed = Y.shape[0] * ((Y.mean(axis=0) - mu) ** 2).sum() / (ns - 1)
    resid = Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + mu
    ms_int = (resid ** 2).sum() / ((Y.shape[0] - 1) * (ns - 1))
    u = (ms_seed - ms_int) / Y.shape[0]
    nu = (ms_seed - ms_int) ** 2 / (ms_seed ** 2 / (ns - 1) + ms_int ** 2 / (7 * (ns - 1))) if (ms_seed or ms_int) else 1.0
    return {"sigma2_seed_set_means": max(0.0, u), "sigma2_seed_set_means_untruncated": float(u), "MS_seed": float(ms_seed),
            "MS_set_x_seed": float(ms_int), "nu_seed": float(min(ns - 1, max(1.0, nu))), "n_s": ns}


def guard_exceeds(h_primes: dict[str, float], pi: float) -> bool:
    """B4.2's comparison: whether the larger widened half-width (over V_G and V_J) exceeds Pi_nominal, strictly."""
    return bool(max(h_primes.values()) > pi)


def escalates(st: dict[str, Any]) -> bool:
    """B4.3's flag: 16 sigma2_set / (4 sigma2_w) > 1; no flag when the within-set variance is zero."""
    return bool(16 * st["sigma2_set"] / (4 * st["sigma2_w"]) > 1) if st["sigma2_w"] > 0 else False


def widened(h: float, st: dict[str, Any] | None, sd: dict[str, Any] | None, P: int = 4) -> dict[str, Any]:
    v1 = (h / 1.96) ** 2
    if st is None:
        return {"h_prime": tq(31) / 1.96 * h, "nu": 31.0, "v": [v1, 0.0, 0.0]}
    v2 = st["sigma2_set"] / (2 * P)
    v3 = sd["sigma2_seed_set_means"] / sd["n_s"]
    parts = [(v1, 31.0), (v2, st["nu_set"]), (v3, sd["nu_seed"])]
    tot = sum(v for v, _ in parts)
    nu = tot ** 2 / sum(v ** 2 / n for v, n in parts if v > 0)
    return {"h_prime": tq(nu) * math.sqrt(tot), "nu": float(nu), "v": [v1, v2, v3]}


# ----------------------------------------------------------------------------- B4.4


def reference_sizes(b2: dict[str, Any], seed: int = 0) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    out = {}
    for key, per_bg in b2["effects"].items():
        out[key] = {}
        for bg, vals in per_bg.items():
            v = np.array([x for x in vals if x is not None])
            if v.size < 2:
                out[key][bg] = {"n": int(v.size)}
                continue
            p95 = float(np.percentile(v, 95))
            reps = np.percentile(v[rng.integers(0, v.size, size=(2000, v.size))], 95, axis=1)
            se = float(np.std(reps, ddof=1))
            need = 200 if p95 == 0 else int(min(200, math.ceil(v.size * (se / (0.1 * abs(p95))) ** 2)))
            out[key][bg] = {"n": int(v.size), "p95": p95, "bootstrap_se": se, "removals_needed": max(need, 1)}
    return out


# ----------------------------------------------------------------------------- the tables


def tables(raw: dict[str, Any], T: dict[str, dict[str, float]], b2: dict[str, Any] | None) -> dict[str, Any]:
    parts = {p: {sk: raw["partitions"][p][sk]["texts"] for sk in ("set0", "set1")} for p in raw["partitions"]}
    Tarr = {a: np.array([T[str(i)][a] for i in range(32)]) for a in ARMS}
    out: dict[str, Any] = {"pi": {a: float(Tarr[a].mean() / 512) for a in ARMS}, "b4_1": {}, "b4_2": {}, "b4_3": {}}
    for ver, (kind, _) in VERSIONS.items():
        for form in FORMS:
            a = arrays(raw, ver, "nominal", form)
            out["b4_1"][f"{ver}|{form}"] = seed_route_text(a)
        for arm in ARMS:
            hp = {}
            for form in FORMS:
                a = arrays(raw, ver, arm, form)
                b = bootstrap_h(v_bar(a), Tarr[arm], (ver, form, arm))
                stt = set_term(a, parts) if kind == "set" else None
                sdt = seed_term(a, parts) if kind == "set" else None
                w = widened(b["h"], stt, sdt)
                rec = {"h": b["h"], "h_prime": w["h_prime"], "nu": w["nu"], "variance_parts": w["v"], "bootstrap": {k: b[k] for k in ("B", "seed_key")}}
                if kind == "set":
                    rec.update({"set_term": stt, "seed_term": sdt})
                    out["b4_3"][f"{ver}|{form}|{arm}"] = escalates(stt)
                hp[form] = rec
            entry = {"pi": out["pi"][arm], "V_G": hp["V_G"], "V_J": hp["V_J"]}
            if arm == "nominal":
                entry["larger_h_prime_exceeds_pi_nominal"] = guard_exceeds({f: hp[f]["h_prime"] for f in FORMS}, out["pi"]["nominal"])
            out["b4_2"][f"{ver}|{arm}"] = entry
    out["escalation_any"] = any(out["b4_3"].values())
    if b2 is not None:
        out["b4_4"] = reference_sizes(b2)
    out["sealed"] = "widths, variance components, Pi, degrees of freedom, and yes/no only; no V-bar, no V-bar - Pi, no interval ends"
    return out


def main() -> None:
    pb = PILOT / "part_b"
    raw = json.load(open(pb / "sealed" / "b1_raw.json"))
    T = json.load(open(PILOT / "cq_prices" / "T_per_arm.json"))
    b2 = json.load(open(pb / "b2.json")) if (pb / "b2.json").is_file() else None
    out = tables(raw, T, b2)
    with open(pb / "tables.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {pb / 'tables.json'}")


if __name__ == "__main__":
    main()
