"""B4's estimators on synthetic tables: the set and seed terms recover known components, the widening reduces to
(t/1.96) h when both terms are zero, and the tables write no point estimate of V-bar or V-bar - Pi (plan 6, Section 9)."""

from __future__ import annotations

import json

import numpy as np

from vpd_audit_2 import env  # noqa: F401
from vpd_audit_2 import pilot_b_tables as T


def _partitions(rng: np.random.Generator) -> dict:
    parts = {"1": {"set0": list(range(16)), "set1": list(range(16, 32))}}
    for p in (2, 3, 4):
        perm = rng.permutation(32)
        parts[str(p)] = {"set0": sorted(perm[:16].tolist()), "set1": sorted(perm[16:].tolist())}
    return parts


def _synthetic_raw(rng: np.random.Generator, s2_text=1.0, s2_set=0.0, s2_seed=0.0, noise=0.5, n_seeds=8, n_draws=8, shift=0.0) -> dict:
    parts = _partitions(rng)
    a = rng.normal(0, np.sqrt(s2_text), 32)
    seed_eff = rng.normal(0, np.sqrt(s2_seed), n_seeds)
    raw = {"partitions": {}, "v2": {}, "stochastic": {}}
    for p, sets in parts.items():
        raw["partitions"][p] = {}
        for sk, texts in sets.items():
            b = rng.normal(0, np.sqrt(s2_set))
            harm, J = {}, {}
            for s in range(1, n_seeds + 1):
                for n in (20, 40, 80):
                    harm[f"original|s{s}|n{n}"] = [1.0] * 16
                    for arm in T.ARMS:
                        g = [1.0 + shift + 2 * (a[i] + b + seed_eff[s - 1]) + rng.normal(0, noise) for i in texts]
                        harm[f"{arm}|s{s}|n{n}"] = g
                        J[f"{arm}|s{s}|n{n}"] = [x - 1.0 for x in g]
            raw["partitions"][p][sk] = {"texts": texts, "harm": harm, "J": J}
    for d in range(n_draws):
        raw["stochastic"][f"original|d{d}"] = [0.0] * 32
        for arm in T.ARMS:
            raw["stochastic"][f"{arm}|d{d}"] = (rng.normal(0, noise, 32)).tolist()
    for i in range(32):
        for s in range(1, n_seeds + 1):
            g = 2 * (a[i] + seed_eff[s - 1]) + rng.normal(0, noise) + shift
            raw["v2"][f"t{i}|s{s}"] = {"G": {arm: {"fill": g} for arm in T.ARMS}, "J": {arm: {"fill": g} for arm in T.ARMS}}
    return raw


def test_set_and_seed_terms_recover_known_components():
    rng = np.random.default_rng(0)
    est_set, est_seed = [], []
    for _ in range(150):
        raw = _synthetic_raw(rng, s2_text=1.0, s2_set=0.2, s2_seed=0.1, noise=0.3)
        a = T.arrays(raw, "i@20", "nominal", "V_G")
        parts = {p: {sk: raw["partitions"][p][sk]["texts"] for sk in ("set0", "set1")} for p in raw["partitions"]}
        est_set.append(T.set_term(a, parts)["sigma2_set_untruncated"])
        est_seed.append(T.seed_term(a, parts)["sigma2_seed_set_means_untruncated"])
    # on V's scale the set and seed effects carry 0.5 x 2 = 1, so the true components are 0.2 and 0.1
    assert abs(np.mean(est_set) - 0.2) < 0.06
    assert abs(np.mean(est_seed) - 0.1) < 0.035


def test_widening_reduces_when_the_terms_vanish():
    w = T.widened(0.1, None, None)
    assert abs(w["h_prime"] - T.tq(31) / 1.96 * 0.1) < 1e-15
    w2 = T.widened(0.1, {"sigma2_set": 0.0, "nu_set": 2.0}, {"sigma2_seed_set_means": 0.0, "n_s": 8, "nu_seed": 3.0})
    assert abs(w2["h_prime"] - T.tq(31) * 0.1 / 1.96) < 1e-12


def test_seed_route_text_on_v_scale():
    rng = np.random.default_rng(1)
    raw = _synthetic_raw(rng, s2_text=1.0, noise=0.4)
    a = T.arrays(raw, "ii", "nominal", "V_G")
    r = T.seed_route_text(a)
    assert abs(r["sigma2_seed"] - 0.25 * 0.16) < 0.02 and abs(r["sigma2_route"] - 0.25 * 0.16) < 0.02


def test_guard_comparison_each_branch():
    """Plan 7, item 10: the guard says yes when the larger h' exceeds Pi, strictly, whichever form it comes from."""
    assert T.guard_exceeds({"V_G": 0.05, "V_J": 0.01}, 0.02)
    assert T.guard_exceeds({"V_G": 0.01, "V_J": 0.05}, 0.02)
    assert not T.guard_exceeds({"V_G": 0.01, "V_J": 0.015}, 0.02)
    assert not T.guard_exceeds({"V_G": 0.02, "V_J": 0.01}, 0.02)  # equal is not above


def test_escalation_flag_each_branch():
    """Plan 7, item 10: 16 sigma2_set / (4 sigma2_w) > 1 flags; equal to 1, below 1, or a zero within-set variance does not."""
    assert T.escalates({"sigma2_set": 0.3, "sigma2_w": 1.0})  # ratio 1.2
    assert not T.escalates({"sigma2_set": 0.25, "sigma2_w": 1.0})  # ratio 1
    assert not T.escalates({"sigma2_set": 0.1, "sigma2_w": 1.0})
    assert not T.escalates({"sigma2_set": 0.0, "sigma2_w": 1.0})
    assert not T.escalates({"sigma2_set": 5.0, "sigma2_w": 0.0})


def test_guard_and_escalation_through_the_tables():
    """Plan 7, item 10, end to end on synthetic tables: a large Pi keeps the guard at no and a tiny one turns it to yes; a
    large set effect raises the escalation flag and no set effect leaves it down."""
    rng = np.random.default_rng(3)
    raw = _synthetic_raw(rng, s2_text=1.0, s2_set=4.0, noise=0.3)
    big = {str(i): {a: 1e4 for a in T.ARMS} for i in range(32)}
    tiny = {str(i): {a: 1e-6 for a in T.ARMS} for i in range(32)}
    out_big, out_tiny = T.tables(raw, big, None), T.tables(raw, tiny, None)
    for ver in T.VERSIONS:
        assert out_big["b4_2"][f"{ver}|nominal"]["larger_h_prime_exceeds_pi_nominal"] is False
        assert out_tiny["b4_2"][f"{ver}|nominal"]["larger_h_prime_exceeds_pi_nominal"] is True
    assert out_big["escalation_any"] and all(out_big["b4_3"].values())
    calm = T.tables(_synthetic_raw(np.random.default_rng(4), s2_text=1.0, s2_set=0.0, noise=0.3), tiny, None)
    assert not calm["escalation_any"]


def test_tables_write_no_point_estimate():
    rng = np.random.default_rng(2)
    raw = _synthetic_raw(rng, shift=0.0123456789)
    Tp = {str(i): {a: 0.05 + 0.001 * i for a in T.ARMS} for i in range(32)}
    out = T.tables(raw, Tp, None)
    text = json.dumps(out)
    for ver in T.VERSIONS:
        for form in T.FORMS:
            for arm in T.ARMS:
                vb = T.v_bar(T.arrays(raw, ver, arm, form))
                for x in (vb.mean(), vb.mean() - np.mean([Tp[str(i)][arm] for i in range(32)]) / 512):
                    assert f"{x:.8g}"[:9] not in text and repr(float(x)) not in text
    assert "point" not in text and "mean_V" not in text
    assert set(out["b4_2"]["i@20|nominal"]) == {"pi", "V_G", "V_J", "larger_h_prime_exceeds_pi_nominal"}
