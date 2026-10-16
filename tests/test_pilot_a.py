"""Plan 6 of the research log, Part A: the extended starts, stage crossings, the frequency strata and shuffles, the no-carry-over guard, the
whole batch job on the tiny model (CPU), and A4's estimators on synthetic tables."""

from __future__ import annotations

import json
import math

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import diagnose as D
from vpd_audit_2 import g2
from vpd_audit_2 import pilot as P
from vpd_audit_2 import pilot_a
from vpd_audit_2 import pilot_a_tables as T

from tiny_model import tiny_component_model, tiny_ids


# ----------------------------------------------------------------------------- prerequisites


def test_extended_starts_equal_the_manifest_file_and_rebuild_byte_for_byte():
    from vpd_audit_2.manifest import deterministic_npz, load_start

    for s in range(1, 17):
        ref, ext = load_start(s), P.load_extended_start(s)
        assert list(ref) == list(ext) and all(np.array_equal(ref[k], ext[k]) for k in ref), s
    arrays, _ = P.make_extended_starts()
    assert deterministic_npz(arrays) == (P.STARTS_DIR / "starts_1_64.npz").read_bytes()
    assert len({P.load_extended_start(s)[P.layout()[0][0]].tobytes() for s in range(1, 65)}) == 64


def test_crossing_on_the_two_step_mean():
    rec = [0.5, 1.0, 1.4, 2.2, 1.6, 3.0, 11.0]  # two-step means 0.75, 1.2, 1.8, 1.9, 2.3, 7.0
    c = P.crossing(rec, 2.0)
    assert (c["k"], c["KL_k"], c["missing"]) == (5, 3.0, False) and c["m_k"] == pytest.approx(2.3)
    assert c["m_k"] >= 2.0 and all(0.5 * (rec[k] + rec[k - 1]) < 2.0 for k in range(1, c["k"]))
    assert P.crossing(rec, 100.0)["missing"]


def _synthetic_cache():
    rng = np.random.default_rng(0)
    order = ["a", "b"]
    m2c = {"a": 30, "b": 25}
    offsets = {"a": 0, "b": 30}
    n_pos = 2000
    rate = np.concatenate([rng.uniform(0, 0.5, 30), rng.uniform(0, 0.5, 25)])
    rate[[3, 4, 40]] = 0.0  # dead: never above zero
    rate[5] = 1e-4          # rare but alive if its labels are large enough
    rows = [np.flatnonzero(rng.uniform(size=55) < rate) for _ in range(n_pos)]
    cache = {"indptr": np.concatenate([[0], np.cumsum([r.size for r in rows])]).astype(np.int64),
             "indices": np.concatenate(rows).astype(np.uint16), "values": rng.uniform(0.5, 1, sum(r.size for r in rows)).astype(np.float32)}
    meta = {"n_subcomponents": 55, "module_order": order, "module_offsets": offsets, "module_to_c": m2c}
    return cache, meta


def test_strata_are_frequency_deciles_with_dead_apart():
    cache, meta = _synthetic_cache()
    s = P.strata_from_cache(cache, meta)
    assert set(np.flatnonzero(s["stratum"] == P.DEAD_STRATUM)) >= {3, 4, 40}
    assert np.all((s["mean_label"] <= 1e-6) == (s["stratum"] == P.DEAD_STRATUM))
    for k in meta["module_order"]:
        o, C = meta["module_offsets"][k], meta["module_to_c"][k]
        st, fr = s["stratum"][o : o + C], s["freq"][o : o + C]
        alive = st != P.DEAD_STRATUM
        counts = np.bincount(st[alive], minlength=10)
        assert counts.max() - counts.min() <= 1  # equal-count deciles
        for v in range(9):  # every decile's frequencies lie at or below the next one's
            if counts[v] and counts[v + 1]:
                assert fr[alive & (st == v)].max() <= fr[alive & (st == v + 1)].min()


def test_shuffle_keeps_each_stratum_multiset_and_the_deltas_and_is_keyed():
    lay = [("a", 30), ("b", 25)]
    rng = np.random.default_rng(1)
    strata = {"a": rng.integers(0, 11, 30), "b": rng.integers(0, 11, 25)}
    flat = rng.uniform(size=57).astype(np.float32)
    x = P.shuffle_source(flat, lay, strata, ("C1", 1, "n80", 1))
    assert x[30] == flat[30] and x[56] == flat[56]  # the deltas
    off = 0
    for k, C in lay:
        for v in np.unique(strata[k]):
            idx = off + np.flatnonzero(strata[k] == v)
            assert sorted(x[idx].tolist()) == sorted(flat[idx].tolist())
        off += C + 1
    assert np.array_equal(x, P.shuffle_source(flat, lay, strata, ("C1", 1, "n80", 1)))
    assert not np.array_equal(x, P.shuffle_source(flat, lay, strata, ("C1", 1, "n80", 2)))
    assert not np.array_equal(x, flat)


def test_scoring_refuses_another_batch():
    with pytest.raises(AssertionError, match="carry-over"):
        P.score_own(None, {}, None, "C1", "C2")


# ----------------------------------------------------------------------------- the batch job on the tiny model


@pytest.fixture(scope="module")
def tiny_job(tmp_path_factory):
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    lay = [(k, model.module_to_c[k]) for k in model.target_module_paths]
    g = torch.Generator().manual_seed(11)
    starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay} for s in P.PILOT_STARTS}
    ids = tiny_ids(16, seed=3).numpy()
    ref = g2.authors_loop(model, A.prepare(model, ids, "bf16", device="cpu"), starts[1], 320, 0.1, capture_grads=False, device="cpu")
    strata = {k: np.random.default_rng(5).integers(0, 3, C) for k, C in lay}
    out = pilot_a.batch_job(model, "C1", ids, 1, starts, {"record": ref["record"], "sources_sha256": D.sources_sha256(ref["sources"])},
                            strata, lay, tmp_path_factory.mktemp("src"), tmp_path_factory.mktemp("sealed") / "a3_shuffles_C1.npz",
                            log=lambda *_: None, device="cpu")
    return out, ref


def test_batch_job_runs_every_part_and_checks_the_diagonal(tiny_job):
    out, ref = tiny_job
    assert "stopped" not in out
    assert out["a1"]["1"]["equals_G1_record"] and out["a1"]["1"]["equals_G1_final_sources"]
    assert sorted(out["a1"], key=int) == [str(s) for s in P.PILOT_STARTS]
    assert all(len(r["record"]) == 321 for r in out["a1"].values())
    for r0 in ("1", "2"):
        acc = out["a2"][r0]["accepted"]
        assert acc is not None and acc["departure"]["first_other_source_difference"] is not None
        assert acc["start_key"][:4] == [20261001, "pilot-perturb", "C1", 1]
    assert all(a["batch_in_C1_to_C8"] and a["start_in_1_to_8"] for a in out["assertions"])
    assert len(out["assertions"]) == 8 + sum(len(v["draws"]) for v in out["a2"].values())
    # plan 7 of the research log, item 5: the sealed harms are in their file only; the job returns the file's path and hash
    import hashlib
    from pathlib import Path

    assert set(out["a3_sealed"]) == {"file", "sha256"}
    sealed_file = Path(out["a3_sealed"]["file"])
    assert hashlib.sha256(sealed_file.read_bytes()).hexdigest() == out["a3_sealed"]["sha256"]
    with np.load(sealed_file) as z:
        for tag, v in out["a3"].items():
            assert v["missing"] or (v["own_score_equals_record"] and z[f"C1|{tag}|shuffles"].shape == (8,) and z[f"C1|{tag}|own"].shape == (1,))
    assert set(out) <= {"batch", "labels_target_seconds", "a1", "a2", "assertions", "a3", "a3_sealed", "seconds"}


def test_batch_job_stops_when_the_diagonal_differs(tmp_path):
    model = tiny_component_model()
    lay = [(k, model.module_to_c[k]) for k in model.target_module_paths]
    g = torch.Generator().manual_seed(11)
    starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay} for s in P.PILOT_STARTS}
    out = pilot_a.batch_job(model, "C1", tiny_ids(16, seed=3).numpy(), 1, starts, {"record": [0.0] * 321, "sources_sha256": "x"},
                            {k: np.zeros(C, int) for k, C in lay}, lay, tmp_path, tmp_path / "sealed" / "a3_shuffles_C1.npz",
                            log=lambda *_: None, device="cpu")
    assert "stopped" in out and list(out["a1"]) == ["1"] and not (tmp_path / "sealed").exists()


# ----------------------------------------------------------------------------- A4's estimators


def test_anova_recovers_known_components():
    rng = np.random.default_rng(0)
    est = []
    for _ in range(400):
        Y = 10 + rng.normal(0, 2, (8, 1)) + rng.normal(0, 1, (1, 8)) + rng.normal(0, 3, (8, 8))
        a = T.anova_two_way(Y)
        est.append((a["sigma2_b_untruncated"], a["sigma2_c_untruncated"], a["sigma2_int"]))
    m = np.mean(est, axis=0)
    assert abs(m[0] - 4) < 0.6 and abs(m[1] - 1) < 0.4 and abs(m[2] - 9) < 0.3


def test_width_and_cost_reproduce_the_plans_worked_numbers():
    # amendment's worked example: mu 10, sigma2_int 37.5, the others 0, so w80 = t(K-1) sqrt(75 / (K ns)) / 10
    for (K, ns), w in {(8, 3): 0.42, (8, 5): 0.32, (16, 3): 0.27, (8, 8): 0.26, (16, 5): 0.21, (16, 8): 0.16}.items():
        assert abs(T.width(10.0, 0.0, 37.5, 0.0, K, ns)["w"] - w) < 0.006, (K, ns)
    for (K, ns), h in {(8, 3): 2.4, (8, 5): 4.0, (8, 8): 6.3, (16, 3): 6.2, (16, 5): 10.3, (16, 8): 16.5}.items():
        assert abs(T.cost(K, ns)["B200_hours"] - h) < 0.06, (K, ns)
    assert abs(T.cost(8, 3)["delta_frozen_cost"][0] - 13.1) < 0.1


def test_width_with_a_nonzero_start_term():
    """Plan 7 of the research log, item 9: the pilot's 40-step components (batch 0.5806, pairing 0.8194, start 0.0820, mean
    1.9487) at 16 batches and 5 starts give w40 = 0.356 with nu = 18.59, the start term in play; the committed design row
    for 16 by 5 agrees."""
    w = T.width(1.9487, 0.5806, 0.8194, 0.0820, 16, 5)
    assert w["S"] == pytest.approx(0.0164) and w["P"] == pytest.approx(0.0931, abs=5e-5)
    assert abs(w["w"] - 0.356) < 5e-4 and abs(w["nu"] - 18.59) < 5e-3
    rows = json.load(open(T.PART_A / "tables.json"))["design_table"]["rows"]
    row = next(r for r in rows if r["K"] == 16 and r["n_s"] == 5)
    assert round(row["w"]["40"], 3) == 0.356 and round(row["nu"]["40"], 2) == 18.59


def test_pooled_path_noise_and_alternation_onset():
    pv = T.pooled_variance([[1.0, 2.0, 3.0], [2.0, 2.0, 5.0]])
    assert pv["pooled"] == pytest.approx((1.0 + 3.0) / 2) and pv["df"] == 4
    rec = [float(k) for k in range(30)] + [30.0 + (0.5 if k % 2 else -0.5) for k in range(291)]
    onset = T.alternation_onset(rec)
    assert onset is not None and 29 <= onset <= 32
    assert T.alternation_onset([float(k) for k in range(321)]) is None


def test_tables_write_no_sealed_value():
    rng = np.random.default_rng(2)

    def rec(base: float) -> list[float]:
        return [base + 0.1 * k + rng.normal(0, 0.01) for k in range(321)]

    runs = {"a1": {b: {str(s): {"record": rec(0.2 + 0.01 * s)} for s in P.PILOT_STARTS} for b in P.PILOT_BATCHES},
            "a2": {b: {r0: {"accepted": {"record": rec(0.25), "start_key": [20261001, "pilot-perturb", b, int(b[1:]), int(r0)]}} for r0 in ("1", "2")}
                   for b in P.PILOT_BATCHES}}
    sealed = {}
    for b in P.PILOT_BATCHES:
        for tag in pilot_a.TAGS:
            sealed[f"{b}|{tag}|own"] = np.array([7.0])
            sealed[f"{b}|{tag}|shuffles"] = rng.normal(3.0, 0.1, 8)
    out = T.tables({"runs": runs, "sealed": sealed})
    sh = out["shuffle_noise_ratio"]["ratios"]
    assert set(sh) == set(pilot_a.TAGS) and all(set(v) == {"median_over_batches", "batches"} for v in sh.values())
    text = str(out)
    assert "3.0" not in text.split("shuffle_noise_ratio")[1][:400]  # no shuffled mean near 3 in the shuffle section
    assert out["path_noise"]["20"]["df"] == 16 and len(out["design_table"]["rows"]) == 6
