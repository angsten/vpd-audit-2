"""Session 7, plan 5: probe 1's reading (`vpd_audit_2/probe1_read.py`) on made-up numbers.

  - The weighted and unweighted agreement, the positive share, and kappa, by hand.
  - The matched draw of kept components: per cell, as many as the off set has there or all of them if fewer.
  - The reading returns each of its lines on constructed intervals, and the within-batch gate picks the sentence.
  - A whole row on made-up unit files: the pooled agreement and its chance equal a brute-force loop over texts and
    components, kappa is the interval's estimate, and row (d) draws four off and four kept components with the arrow
    flipped.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import probe1 as P1
from vpd_audit_2 import probe1_read as RD
from vpd_audit_2 import s6_build as B


def test_agreement_by_hand():
    p = np.array([[0.5, -0.2, 0.0, 0.3, -1.0], [-0.4, 0.1, 0.2, 0.0, 0.5]])
    ref = np.sign(np.array([1.0, -2.0, 3.0, 0.0, -1.0]))  # +, -, +, 0, -
    idx = np.array([0, 1, 2, 3])
    # text 0: masses 0.5, 0.2, 0, 0.3; agreeing 0.5 and 0.2 (a zero reference agrees with nothing): 0.7 of 1.0
    # text 1: masses 0.4, 0.1, 0.2, 0; agreeing 0.2: 0.2 of 0.7
    np.testing.assert_allclose(RD.weighted_agreement(p, ref, idx), [0.7, 0.2 / 0.7])
    # unweighted, over nonzero pushes: text 0 entries 0, 1, 3, of which 0 and 1 agree; text 1 entries 0, 1, 2, of which 2
    np.testing.assert_allclose(RD.unweighted_agreement(p, ref, idx), [2 / 3, 1 / 3])
    # a reference per text (the within-batch case)
    ref2 = np.vstack([ref, -ref])
    np.testing.assert_allclose(RD.weighted_agreement(p, ref2, idx), [0.7, 0.5 / 0.7])
    np.testing.assert_allclose(RD.positive_share(p, idx), [0.8 / 1.0, 0.3 / 0.7])
    assert RD.kappa(0.6, 0.5) == pytest.approx(0.2) and RD.kappa(0.5, 0.5) == 0.0
    assert np.isnan(RD.weighted_agreement(np.zeros((1, 5)), ref, idx)[0])


def test_matched_kept_draw():
    codes = np.array([0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 3])
    off = np.array([0, 1, 4, 7, 8, 9])  # cell 0: 2, cell 1: 1, cell 2: 2, cell 3: 1
    kept = np.array([2, 3, 5, 6, 10, 11])  # cell 0: 2, cell 1: 2, cell 2: 0, cell 3: 2
    a = RD.matched_kept(off, kept, codes, seed=3)
    assert set(a) <= set(kept)
    counts = {c: int((codes[a] == c).sum()) for c in range(4)}
    assert counts == {0: 2, 1: 1, 2: 0, 3: 1}  # cell 2 has no kept component: all of none
    assert np.array_equal(a, RD.matched_kept(off, kept, codes, seed=3))
    draws = {tuple(RD.matched_kept(off, kept, codes, seed=s)) for s in range(20)}
    assert len(draws) > 1


@pytest.mark.parametrize("interval,chance,want", [
    ((0.55, 0.80), 0.5, "mostly agree"),
    ((0.25, 0.45), 0.5, "partly agree"),
    ((0.20, 0.50), 0.5, "partly agree"),
    ((0.05, 0.15), 0.5, "weakly agree"),
    ((0.01, 0.20), 0.5, "weakly agree"),
    ((-0.10, 0.30), 0.5, "do not agree"),
    ((-0.30, -0.10), 0.5, "do not agree"),
    ((0.00, 0.10), 0.5, "do not agree"),
    ((0.10, 0.30), 0.5, "undetermined"),
    ((0.40, 0.60), 0.5, "undetermined"),
    ((0.05, 0.60), 0.5, "undetermined"),
    ((0.55, 0.80), 0.95, "undetermined (degenerate)"),
    ((-0.30, -0.10), 0.91, "undetermined (degenerate)"),
])
def test_each_reading_on_constructed_intervals(interval, chance, want):
    assert RD.reading(interval, chance) == want


def test_the_within_batch_gate_and_the_licences():
    low = RD.licence("do not agree", (-0.05, 0.04), within_kappa=0.03)
    high = RD.licence("do not agree", (-0.05, 0.04), within_kappa=0.30)
    assert low["key"] == "do not agree, input-specific" and "specific to each input" in low["sentence"] and low["within_as_low_as_cross"] is True
    assert high["key"] == "do not agree, other way" and "some other way" in high["sentence"] and high["within_as_low_as_cross"] is False
    assert "contrary to the paper's premise" in RD.licence("mostly agree", (0.6, 0.7), 0.0)["sentence"]
    assert "question marks" in RD.licence("partly agree", (0.3, 0.4), 0.0)["sentence"]
    assert "head decides" in RD.licence("weakly agree", (0.05, 0.1), 0.0)["sentence"]
    assert RD.row_d_draws_allowed("mostly agree") and RD.row_d_draws_allowed("do not agree") and not RD.row_d_draws_allowed("undetermined")


def test_lower_median_index():
    assert RD.lower_median_index(np.array([3.0, 1.0, 2.0, 4.0]), [(0,), (1,), (2,), (3,)]) == 2  # sorted 1, 2, 3, 4: the second
    assert RD.lower_median_index(np.array([1.0, 1.0, 1.0]), [(2,), (0,), (1,)]) == 2  # ties by key: keys 0, 1, 2, middle is key 1 at position 2


# ----------------------------------------------------------------------------- a whole row on made-up units

LAY = [("m0", 12), ("m1", 10), ("m2", 8)]
ATT, HELD, STARTS = ["A1", "A2", "A3"], ["H1", "H2", "H3"], [9, 10]
N, CH = 6, 3  # texts per batch, per chunk
STAGE = "s320"


def _made_up(tmp: Path) -> tuple[RD.Inputs, RD.Cells, dict]:
    rng = np.random.default_rng(11)
    E = P1.n_entries(LAY)
    strata = {"m0": np.array([0, 0, 0, 1, 1, 1, 2, 2, 2, 10, 10, 10]), "m1": np.array([0, 0, 1, 1, 2, 2, 3, 3, 10, 10]),
              "m2": np.array([0, 0, 0, 0, 1, 1, 1, 1])}
    codes = B.cells_of(LAY, strata)
    settings = {(a, s, "n320"): rng.random(E).astype(np.float32) for a in ATT for s in STARTS}
    units = tmp / "units"
    files = {}
    pushes = {}
    for a in ATT:
        for s in STARTS:
            for b in [a] + HELD:
                p = rng.normal(size=(N, E)) * np.exp(rng.normal(size=E))
                p[:, 5] = 0.0  # a component with a null move everywhere
                pp = rng.normal(size=(N, E))
                pushes[(b, a, s)] = (p.astype(np.float32), pp.astype(np.float32))
                for c in range(N // CH):
                    rows = slice(c * CH, (c + 1) * CH)
                    name = RD.unit_name(STAGE, b, a, s, c)
                    meta = {"unit": name, "intact_against_target": {"max_abs_logit_difference": 1e-5, "max_text_kl": 1e-9}}
                    arrays = {"texts": np.arange(c * CH, (c + 1) * CH), "intact": p[rows].astype(np.float32), "pattern": pp[rows].astype(np.float32),
                              "delta_norm_sum": 50.0 + rng.random(CH), "pattern_kl": 30.0 + rng.random(CH), "zero_direction_positions": np.zeros(CH, dtype=np.int64),
                              "meta": np.array(json.dumps(meta))}
                    files[f"units/{name}.npz"] = LR.write_unit(units / f"{name}.npz", arrays)
    inp = RD.Inputs(lay=LAY, codes=codes, strata_flat=codes % 12, attack=ATT, heldout=HELD, starts=STARTS,
                    text_ids_H=np.array([[f"t{j}_{t}" for t in range(N)] for j in range(len(HELD))]), settings=settings, s6_rounded=None)
    return inp, RD.Cells(units, files, STAGE), {"pushes": pushes, "files": files, "settings": settings}


def _brute_g(p: np.ndarray, P: np.ndarray, idx: np.ndarray) -> float:
    out = []
    for x in range(p.shape[0]):
        num = den = 0.0
        for c in idx:
            w = abs(float(p[x, c]))
            den += w
            if np.sign(p[x, c]) == np.sign(P[c]):
                num += w
        out.append(num / den)
    return float(np.mean(out))


@pytest.fixture(scope="module")
def made_up(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("probe1_read")
    inp, cells, extra = _made_up(tmp)
    res = RD.row_statistics(cells, inp, "n320", indices=LI.make_indices(len(ATT)))
    return {"tmp": tmp, "inp": inp, "cells": cells, "res": res, **extra}


def test_a_row_pools_as_a_brute_force_loop(made_up):
    inp, res, pushes = made_up["inp"], made_up["res"], made_up["pushes"]
    g, g0, gin = [], [], []
    for a in ATT:
        for s in STARTS:
            sets = RD.setting_sets(inp.settings[(a, s, "n320")], LAY)
            K = [RD.matched_kept(sets["off"], sets["kept"], inp.codes, RD.chance_seed(a, s, 320, d)) for d in range(1, RD.CHANCE_DRAWS + 1)]
            P = pushes[(a, a, s)][0].astype(np.float64).sum(axis=0)
            for h in HELD:
                p = pushes[(h, a, s)][0]
                g.append(_brute_g(p, P, sets["off"]))
                g0.append(np.mean([_brute_g(p, P, Kd) for Kd in K]))
            pa = pushes[(a, a, s)][0].astype(np.float64)
            gin.append(np.mean([_brute_g(pa[x : x + 1], P - pa[x], sets["off"]) for x in range(N)]))
    assert res["g_bar"] == pytest.approx(np.mean(g), rel=1e-12) and res["g0_bar"] == pytest.approx(np.mean(g0), rel=1e-12)
    assert res["kappa"] == pytest.approx((np.mean(g) - np.mean(g0)) / (1 - np.mean(g0)), rel=1e-12)
    assert res["interval"]["estimate"] == pytest.approx(res["kappa"], rel=1e-12)
    lo, hi = res["interval"]["interval"]
    assert lo < res["kappa"] < hi and res["reading"] == RD.reading((lo, hi), res["g0_bar"])
    assert res["within"]["g_bar"] == pytest.approx(np.mean(gin), rel=1e-12)
    assert res["cells"] == 3 * 3 * 2 and res["texts_per_cell"] == N
    assert "full_pattern" in res and res["sizes"]["off"]["min"] > 0 and res["sizes"]["matched"]["min"] > 0


def test_the_additivity_ratio_and_the_sign_balance(made_up):
    inp, res, pushes = made_up["inp"], made_up["res"], made_up["pushes"]
    cells = made_up["cells"]
    add, bal, bal_kept, bal_matched = [], [], [], []
    for a in ATT:
        for s in STARTS:
            sets = RD.setting_sets(inp.settings[(a, s, "n320")], LAY)
            P = pushes[(a, a, s)][0].astype(np.float64).sum(axis=0)
            bal.append(np.clip(P[sets["off"]], 0, None).sum() / np.abs(P[sets["off"]]).sum())
            bal_kept.append(np.clip(P[sets["kept"]], 0, None).sum() / np.abs(P[sets["kept"]]).sum())
            K = [RD.matched_kept(sets["off"], sets["kept"], inp.codes, RD.chance_seed(a, s, 320, d)) for d in range(1, RD.CHANCE_DRAWS + 1)]
            bal_matched.append(np.mean([np.clip(P[Kd], 0, None).sum() / np.abs(P[Kd]).sum() for Kd in K]))
            for h in HELD:
                c = cells.get(h, a, s)
                add.append(np.mean(c["intact"].astype(np.float64)[:, sets["off"]].sum(axis=1) / c["delta_norm_sum"]))
    assert res["additivity"]["off_set"] == pytest.approx(np.mean(add), rel=1e-12)
    assert res["sign_balance_attack"]["mean"] == pytest.approx(np.mean(bal), rel=1e-12)
    ph = res["post_hoc_sign_balance_attack_kept"]
    assert ph["all_kept"]["mean"] == pytest.approx(np.mean(bal_kept), rel=1e-12) and ph["all_kept"]["max"] == pytest.approx(max(bal_kept), rel=1e-12)
    assert ph["matched_kept_mean_of_draws"]["mean"] == pytest.approx(np.mean(bal_matched), rel=1e-12) and "post hoc" in ph["note"]
    text = RD.report({"n320": res}, None, {"passes": True, "sign_share_above": 0.95, "spearman_all": 0.9, "pairs": 1600})
    assert "POST HOC" in text and f"{ph['all_kept']['mean']:.4f}" in text


def test_the_permutation_baseline_post_hoc(made_up):
    inp, res, pushes = made_up["inp"], made_up["res"], made_up["pushes"]
    num, den, g0s = 0.0, 0.0, []
    for a in ATT:
        for s in STARTS:
            sets = RD.setting_sets(inp.settings[(a, s, "n320")], LAY)
            O = sets["off"]
            P = pushes[(a, a, s)][0].astype(np.float64).sum(axis=0)
            perms = []
            for r in range(1, RD.PERMUTATIONS + 1):  # the permutation written again: within each cell, among the off set
                rng = np.random.default_rng(RD.permutation_seed(a, s, 320, r))
                q = np.sign(P).copy()
                for c in sorted(set(inp.codes[O].tolist())):
                    idx = O[inp.codes[O] == c]
                    q[idx] = np.sign(P)[idx[rng.permutation(idx.size)]]
                perms.append(q)
            for h in HELD:
                p = pushes[(h, a, s)][0]
                g = _brute_g(p, P, O)
                g0 = np.mean([_brute_g(p, q, O) for q in perms])
                num += g - g0
                den += 1 - g0
                g0s.append(g0)
            assert sorted(perms[0][O].tolist()) == sorted(np.sign(P)[O].tolist())  # a permutation of the off set's signs
            assert np.array_equal(np.delete(perms[0], O), np.delete(np.sign(P), O))  # nothing else moves
    pb = res["post_hoc_permutation_baseline"]
    assert pb["g0_bar"] == pytest.approx(np.mean(g0s), rel=1e-12) and pb["kappa"] == pytest.approx(num / den, rel=1e-12)
    assert pb["interval"]["estimate"] == pytest.approx(pb["kappa"], rel=1e-12) and pb["lines_would_read"] == RD.reading(pb["interval"]["interval"], pb["g0_bar"])
    assert pb["g_bar"] == res["g_bar"]


def test_the_positive_shares_post_hoc(made_up):
    inp, res, pushes = made_up["inp"], made_up["res"], made_up["pushes"]

    def pos(p: np.ndarray, idx: np.ndarray) -> float:
        q = p[:, idx].astype(np.float64)
        return float(np.mean(np.clip(q, 0, None).sum(axis=1) / np.abs(q).sum(axis=1)))

    off_h, kept_h, off_a, kept_a, d = [], [], [], [], []
    for a in ATT:
        for s in STARTS:
            sets = RD.setting_sets(inp.settings[(a, s, "n320")], LAY)
            K = [RD.matched_kept(sets["off"], sets["kept"], inp.codes, RD.chance_seed(a, s, 320, r)) for r in range(1, RD.CHANCE_DRAWS + 1)]
            pa = pushes[(a, a, s)][0]
            off_a.append(pos(pa, sets["off"]))
            kept_a.append(np.mean([pos(pa, Kd) for Kd in K]))
            for h in HELD:
                p = pushes[(h, a, s)][0]
                off_h.append(pos(p, sets["off"]))
                kept_h.append(np.mean([pos(p, Kd) for Kd in K]))
                d.append(off_h[-1] - kept_h[-1])
    ps = res["post_hoc_positive_share"]
    assert ps["heldout_texts"]["off"] == pytest.approx(np.mean(off_h), rel=1e-12) == res["positive_share_heldout"]
    assert ps["heldout_texts"]["matched_kept"] == pytest.approx(np.mean(kept_h), rel=1e-12)
    assert ps["attack_texts"]["off"] == pytest.approx(np.mean(off_a), rel=1e-12) and ps["attack_texts"]["matched_kept"] == pytest.approx(np.mean(kept_a), rel=1e-12)
    assert ps["attack_batch_push_mass"]["off"] == res["sign_balance_attack"]["mean"]
    iv = ps["heldout_off_minus_matched_kept"]
    assert iv["estimate"] == pytest.approx(np.mean(d), rel=1e-10, abs=1e-14) and iv["interval"][0] <= iv["estimate"] <= iv["interval"][1]
    text = RD.report({"n320": res}, None, {"passes": True, "sign_share_above": 0.95, "spearman_all": 0.9, "pairs": 1600})
    assert text.count("POST HOC") == 3 and "Not the reading" in text


def test_row_d(made_up):
    inp, res, cells = made_up["inp"], made_up["res"], made_up["cells"]
    d = RD.row_d(res, cells, inp, "n320")
    ks = np.array(res["per_setting_kappa"])
    order = sorted([(ks[i, k], (i, k)) for i in range(3) for k in range(2)])
    i, k = order[(6 - 1) // 2][1]
    assert (d["setting"]["attack"], d["setting"]["start"]) == (ATT[i], STARTS[k])
    assert [c["cell"] for c in d["components"]] == ["off"] * 4 + ["on"] * 4
    sets = RD.setting_sets(inp.settings[(ATT[i], STARTS[k], "n320")], LAY)
    for c in d["components"]:
        assert c["drawn_arrow_on_text"] == -int(np.sign(c["switch_off_push_on_text"]))  # amendment 6: the arrow is the push while on
        assert (c["flat_entry"] in set(sets["off"])) == (c["cell"] == "off") and c["flat_entry"] != 5
        assert c["agrees"] == (np.sign(c["switch_off_push_on_text"]) == np.sign(c["batch_push_on_attack"]))
    assert d == RD.row_d(res, cells, inp, "n320")  # seeded
    g = res["_g_text"][i, :, k, :]
    assert d["text"]["g"] == sorted(g.reshape(-1))[(g.size - 1) // 2]


def test_a_changed_unit_file_is_refused(made_up, tmp_path):
    cells = made_up["cells"]
    bad = dict(cells.receipt)
    key = f"units/{RD.unit_name(STAGE, 'H2', 'A1', 9, 1)}.npz"
    bad[key] = "0" * 64
    with pytest.raises(RD.Refusal, match="receipt"):
        RD.Cells(cells.folder, bad, STAGE).get("H2", "A1", 9)
    with pytest.raises(RD.Refusal, match="missing"):
        RD.Cells(tmp_path, cells.receipt, STAGE).require(RD.expected_units(STAGE, ATT, HELD, STARTS))


def test_compute_and_the_report(made_up, tmp_path):
    results = tmp_path / "results"
    results.mkdir()
    (results / "validation.json").write_text(json.dumps({"commit": "c" * 40, "passes": True, "sign_share_above": 0.97, "spearman_all": 0.93, "pairs": 1600}))
    (results / "backup.json").write_text(json.dumps({"commit": "c" * 40, "files": made_up["files"]}))
    out = RD.compute(results, units_folder=made_up["cells"].folder, inputs=made_up["inp"], indices=LI.make_indices(len(ATT)))
    assert set(out["rows"]) == {"n320"} and out["rows"]["n320"]["kappa"] == pytest.approx(made_up["res"]["kappa"])
    text = RD.report(out["rows"], out["row_d"], out["validation"])
    assert "THE DECIDING ROW" in text and "Reading:" in text and "NEGATIVE of the measured switch-off push" in text and "Validation" in text
    json.dumps(RD._jsonable(out))  # the record is plain JSON
    (results / "validation.json").write_text(json.dumps({"commit": "c" * 40, "passes": False}))
    with pytest.raises(RD.Refusal, match="validation"):
        RD.compute(results, units_folder=made_up["cells"].folder, inputs=made_up["inp"])
