"""Report 3's printout of B1's original-label arm reads the original arm only: its output does not change when every
freed-arm, J, G, and stochastic value changes, and its set means and SDs are what they say."""

from __future__ import annotations

import json

import numpy as np

from vpd_audit_2 import env  # noqa: F401
from vpd_audit_2 import pilot_b_original as O

ARMS = ("original", "nominal", "saturated", "unsaturated")


def _raw(rng: np.random.Generator, freed_value=None) -> dict:
    parts = {"1": {"set0": list(range(16)), "set1": list(range(16, 32))}}
    for p in (2, 3, 4):
        perm = rng.permutation(32)
        parts[str(p)] = {"set0": sorted(perm[:16].tolist()), "set1": sorted(perm[16:].tolist())}
    other = (lambda: freed_value) if freed_value is not None else (lambda: float(rng.normal()))
    raw = {"partitions": {}, "partition_definition": parts, "v2": {}, "stochastic": {}}
    for p, sets in parts.items():
        raw["partitions"][p] = {}
        for sk, texts in sets.items():
            harm, J = {}, {}
            for s in range(1, 9):
                for n in (20, 40, 80):
                    harm[f"original|s{s}|n{n}"] = [1.0 + 0.01 * i + 0.1 * s + 0.001 * n for i in texts]
                    for arm in ARMS[1:]:
                        harm[f"{arm}|s{s}|n{n}"] = [other() for _ in texts]
                        J[f"{arm}|s{s}|n{n}"] = [other() for _ in texts]
            raw["partitions"][p][sk] = {"texts": texts, "harm": harm, "J": J, "records": {}}
    for i in range(32):
        for s in range(1, 9):
            raw["v2"][f"t{i}|s{s}"] = {"harm": {a: {"fill": (0.5 + 0.01 * i + 0.02 * s) if a == "original" else other(),
                                                    "zero": (0.4 + 0.01 * i) if a == "original" else other()} for a in ARMS},
                                       "G": {a: {"fill": other(), "zero": other()} for a in ARMS[1:]},
                                       "J": {a: {"fill": other(), "zero": other()} for a in ARMS[1:]}}
    for d in range(8):
        for a in ARMS:
            raw["stochastic"][f"{a}|d{d}"] = [other() for _ in range(32)]
    return raw


def test_output_is_blind_to_every_other_arm():
    a = O.original_arm(_raw(np.random.default_rng(0)))
    b = O.original_arm(_raw(np.random.default_rng(0), freed_value=1e300))
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert "1e+300" not in json.dumps(b)


def test_set_means_and_sds():
    out = O.original_arm(_raw(np.random.default_rng(1)))
    s20 = out["versions_i_iii"]["20"]
    # partition 1, set 0: texts 0..15, harm 1 + 0.01 i + 0.1 s + 0.02; the set mean per seed is 1.095 + 0.1 s
    m = np.array(s20["per_set"]["p1|set0"]["mean_per_seed"])
    assert np.allclose(m, 1.095 + 0.1 * np.arange(1, 9))
    assert abs(s20["per_set"]["p1|set0"]["sd_over_seeds"] - np.std(0.1 * np.arange(1, 9), ddof=1)) < 1e-12
    assert np.allclose(s20["sd_over_seeds_per_text_pooled"], np.std(0.1 * np.arange(1, 9), ddof=1))
    v2 = out["version_ii"]["fill"]
    assert np.allclose(v2["sd_over_seeds_per_text"], np.std(0.02 * np.arange(1, 9), ddof=1))
    assert np.allclose(out["version_ii"]["zero"]["sd_over_seeds_per_text"], 0.0)
