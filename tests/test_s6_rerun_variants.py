"""Plan 3 of the research log: the rerun's and the variants' readings on made-up units, before any GPU result exists.

The two-factor interval against an independent least-squares decomposition, in each truncation case; the clause's
boundaries; the delta components' share and its refusal to be called one when negative; the rerun's loader and its
refusals; and the variants' pooled shares on a design whose answers are known by hand.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import t as student

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_rerun as RR
from vpd_audit_2 import s6_variants as V

# ----------------------------------------------------------------------------- the interval


def _mean_squares(Y: np.ndarray) -> tuple[float, float, float]:
    """By least squares on dummy variables: the additive fit's residual, and the drop in fit from leaving out each factor."""
    K, ns = Y.shape
    y = Y.reshape(-1)
    rows = np.repeat(np.arange(K), ns)
    cols = np.tile(np.arange(ns), K)

    def rss(*factors):
        X = np.column_stack([np.ones(y.size)] + [(f == v).astype(float) for f, n in factors for v in range(1, n)])
        r = y - X @ np.linalg.lstsq(X, y, rcond=None)[0]
        return float(r @ r)

    full = rss((rows, K), (cols, ns))
    return (rss((cols, ns)) - full) / (K - 1), (rss((rows, K)) - full) / (ns - 1), full / ((K - 1) * (ns - 1))


@pytest.mark.parametrize("batch_scale,start_scale,surviving", [(1.0, 1.0, ["B", "S"]), (1.0, 0.0, ["B"]), (0.0, 1.0, ["S"]), (0.0, 0.0, [])])
def test_the_two_factor_interval_in_each_truncation_case(batch_scale, start_scale, surviving):
    rng = np.random.default_rng(3)
    Y = 0.8 + batch_scale * rng.normal(0, 0.3, (8, 1)) + start_scale * rng.normal(0, 0.3, (1, 5)) + rng.normal(0, 0.05, (8, 5))
    if not batch_scale:
        Y -= Y.mean(axis=1, keepdims=True) - Y.mean()  # no batch effect at all: MS_B is 0
    if not start_scale:
        Y -= Y.mean(axis=0, keepdims=True) - Y.mean()
    x = RR.interval(Y)
    ms_b, ms_s, ms_e = _mean_squares(Y)
    assert (x["MS_B"], x["MS_S"], x["MS_E"]) == pytest.approx((ms_b, ms_s, ms_e), rel=1e-9, abs=1e-12)
    assert x["surviving"] == surviving and x["mean"] == pytest.approx(Y.mean())
    assert x["variance_untruncated"] == pytest.approx((ms_b + ms_s - ms_e) / 40)
    ms, df = {"B": ms_b, "S": ms_s, "E": ms_e}, {"B": 7, "S": 4, "E": 28}
    if surviving == ["B", "S"]:
        v, nu = (ms_b + ms_s - ms_e) / 40, (ms_b + ms_s - ms_e) ** 2 / (ms_b ** 2 / 7 + ms_s ** 2 / 4 + ms_e ** 2 / 28)
    elif surviving:
        k = surviving[0]
        v, nu = ms[k] / 40, df[k]  # the other component truncated: its mean square drops out and MS_E cancels
    else:
        v, nu = ms_e / 40, 28
    assert x["variance"] == pytest.approx(v) and x["df_welch_satterthwaite"] == pytest.approx(nu)
    assert x["half_width"] == pytest.approx(student.ppf(0.975, nu) * np.sqrt(v))
    assert x["interval"] == pytest.approx([Y.mean() - x["half_width"], Y.mean() + x["half_width"]])


def test_the_variance_after_truncation_is_the_sum_of_the_truncated_components():
    rng = np.random.default_rng(9)
    Y = 1.0 + rng.normal(0, 0.2, (8, 1)) + rng.normal(0, 0.01, (1, 5)) + rng.normal(0, 0.1, (8, 5))
    x = RR.interval(Y)
    b, s = max(0.0, x["batch_component_untruncated"]), max(0.0, x["start_component_untruncated"])
    assert x["variance"] == pytest.approx(b / 8 + s / 5 + x["MS_E"] / 40)


# ----------------------------------------------------------------------------- the clause and the share


def test_the_clause_and_its_boundaries():
    assert RR.clause(0.80 / 1.0) == "about as much" and RR.clause(1 / 1.25) == "about as much" and RR.clause(1.25) == "about as much"
    assert RR.clause(0.7999) == "less" and RR.clause(1.2501) == "more"
    assert RR.clause(0.80 / 0.83) == "about as much" and RR.clause(0.80 / 2.0) == "less" and RR.clause(0.80 / 0.5) == "more"


def test_the_delta_share_is_a_share_only_when_positive():
    d = RR.delta_share(1.0, 0.6)
    assert d["share"] == pytest.approx(0.4) and d["difference"] == pytest.approx(0.4) and d["holding_at_0_added_harm"] is False
    d = RR.delta_share(1.0, 1.2)
    assert d["share"] is None and d["difference"] == pytest.approx(-0.2) and d["holding_at_0_added_harm"] is True
    text = RR.report({"arms": {a: {**RR.interval(np.full((8, 5), m) + np.arange(5) * 0.01), "by_batch": {}, "by_start": {}, "ratio": 0.8 / m,
                                   "clause": RR.clause(0.8 / m)} for a, m in (("searched", 1.0), ("held_at_0", 1.2))},
                      "delta": {**d, "paired_difference": RR.interval(np.full((8, 5), -0.2) + np.arange(5) * 0.01)}})
    assert "Not a share: holding the delta components at 0 added harm; the difference is -0.200 nats." in text
    assert "0.80/A = 0.800; the clause is \"about as much\"" in text and "beside the paper's 0.83" in text


# ----------------------------------------------------------------------------- the rerun's loader


COMMIT = "d" * 40


def _write_rerun(folder: Path, cells: dict[str, np.ndarray], starts: dict) -> dict:
    files = {}
    for arm, Y in cells.items():
        for i, b in enumerate(R3.BATCHES):
            for k, s in enumerate(R3.STARTS):
                rec = np.linspace(0.2, Y[i, k], 21)
                rec[20] = Y[i, k]
                meta = {"kind": "search", "arm": R3.ARM_NAME[arm], "batch": b, "start": s, "side": "own", "n_steps": 20, "commit": COMMIT,
                        "start_sha256": starts[str(s)]["sha256"], "delta_held": arm == "held_at_0"}
                if arm == "held_at_0":
                    meta["delta_value"] = 0.0
                rel = f"rerun/{arm}/search_{b}_s{s}.npz"
                arrays = {"record": rec, "hook_names": np.array(["step_19", "step_20"]), "hook_steps": np.array([19, 20]),
                          "scored_names": np.array(["n20"]), "own": np.array([Y[i, k]]), "meta": np.array(json.dumps(meta))}
                files[rel] = LR.write_unit(folder / rel, arrays)
    return {"commit": COMMIT, "files": files}


@pytest.fixture()
def rerun_files(tmp_path):
    rng = np.random.default_rng(2)
    cells = {"searched": 0.9 + rng.normal(0, 0.1, (8, 5)), "held_at_0": 0.7 + rng.normal(0, 0.1, (8, 5))}
    starts = {str(s): {"sha256": f"{s:064x}"} for s in R3.STARTS}
    backup = _write_rerun(tmp_path / "local", cells, starts)
    (tmp_path / "backup.json").write_text(json.dumps(backup))
    (tmp_path / "starts.json").write_text(json.dumps({"starts": starts}))
    return {"tmp": tmp_path, "cells": cells, "backup": backup}


def _load(f, backup=None):
    if backup is not None:
        (f["tmp"] / "backup.json").write_text(json.dumps(backup))
    return RR.load(f["tmp"] / "local", f["tmp"] / "backup.json", f["tmp"] / "starts.json")


def test_the_loader_reads_each_arms_table_and_the_reading_follows(rerun_files):
    got = _load(rerun_files)
    for arm in R3.ARMS:
        assert np.array_equal(got[arm], rerun_files["cells"][arm])
    res = RR.rerun(got)
    s, h = res["arms"]["searched"], res["arms"]["held_at_0"]
    assert s["mean"] == pytest.approx(rerun_files["cells"]["searched"].mean()) and s["ratio"] == pytest.approx(0.80 / s["mean"])
    assert res["delta"]["share"] == pytest.approx(1 - h["mean"] / s["mean"])
    paired = res["delta"]["paired_difference"]
    assert paired["mean"] == pytest.approx(s["mean"] - h["mean"])
    assert paired == RR.interval(rerun_files["cells"]["searched"] - rerun_files["cells"]["held_at_0"])
    assert s["by_start"]["43"] == pytest.approx(rerun_files["cells"]["searched"][:, 2].mean())
    assert s["by_batch"]["QB8"] == pytest.approx(rerun_files["cells"]["searched"][7].mean())
    text = RR.report(res)
    assert "Their share, 1 - A_held / A_searched:" in text and "MS_B" in text and "Welch-Satterthwaite df" in text


def test_the_loader_refuses_a_file_the_receipt_does_not_record(rerun_files):
    b = json.loads(json.dumps(rerun_files["backup"]))
    b["files"]["rerun/held_at_0/search_QB3_s44.npz"] = "0" * 64
    with pytest.raises(RR.Refusal, match="held_at_0/search_QB3_s44.npz"):
        _load(rerun_files, b)


def test_the_loader_refuses_a_unit_of_another_commit_or_start(rerun_files):
    b = dict(rerun_files["backup"], commit="e" * 40)
    with pytest.raises(RR.Refusal, match="launch's commit"):
        _load(rerun_files, b)
    starts = json.load(open(rerun_files["tmp"] / "starts.json"))
    starts["starts"]["41"]["sha256"] = "1" * 64
    (rerun_files["tmp"] / "starts.json").write_text(json.dumps(starts))
    with pytest.raises(RR.Refusal, match="from start 41"):
        _load(rerun_files, rerun_files["backup"])


def test_the_loader_refuses_an_own_harm_that_is_not_the_records(rerun_files):
    rel = "rerun/searched/search_QB2_s42.npz"
    path = rerun_files["tmp"] / "local" / rel
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    arrays["own"] = np.array([np.nextafter(arrays["own"][0], 9.0)])
    b = json.loads(json.dumps(rerun_files["backup"]))
    b["files"][rel] = LR.write_unit(path, arrays)
    with pytest.raises(RR.Refusal, match="not the record's"):
        _load(rerun_files, b)


# ----------------------------------------------------------------------------- the variants


def _unit(folder: Path, name: str, passes: list[tuple[str, float, dict]]) -> str:
    arrays = {"pass_ids": np.array([p for p, _, _ in passes]), "harm": np.array([h for _, h, _ in passes], dtype=np.float64),
              "per_text": np.tile(np.array([[h] for _, h, _ in passes], dtype=np.float32), (1, 4)),
              "recorded": np.array(json.dumps([r for _, _, r in passes])), "meta": np.array(json.dumps({"unit": name}))}
    return LR.write_unit(folder / f"{name}.npz", arrays)


def test_the_variants_pooled_shares_and_mean_harms(tmp_path, monkeypatch):
    monkeypatch.setattr(R3, "VARIANT_BATCHES", ("H1", "H3"))
    att, held, starts = ("A1", "A2"), ("H1", "H2", "H3"), (9, 10)
    rng = np.random.default_rng(6)
    Q = len(LT.SETTINGS_LEAD)
    lead = {"attack_names": np.array(att), "heldout_names": np.array(held), "starts": np.array(starts), "setting_names": np.array(LT.SETTINGS_LEAD),
            "init_H": 0.2 + 0.01 * rng.random((3, 2)), "carried": 5 + 20 * rng.random((2, 3, 2, Q))}
    q = {n: k for k, n in enumerate(LT.SETTINGS_LEAD)}
    fold = {"V1": 0.5, "V2": 0.2, "V3": 1.1}
    folder, p2 = tmp_path / "variants", tmp_path / "plan2"
    receipt, receipt2 = {}, {}
    want_harm = {row: {v: [] for v in B.VARIANTS} for row in B.SPLIT_ROWS}
    for j, h in enumerate(held):
        if h not in R3.VARIANT_BATCHES:
            continue
        receipt[f"variants/variants_check_{h}.npz"] = _unit(folder, f"variants_check_{h}", [("check|s_everywhere", 1.5, {"reference": 1.5}),
                                                                                           ("check|s0_everywhere", 0.2, {"reference": 0.2000001}),
                                                                                           ("check|flat", 1.5, {"reference": 1.5})])
        receipt2[f"ones_{h}.npz"] = _unit(p2, f"ones_{h}", [("ones", 0.01 * (j + 1), {})])
        for i, a in enumerate(att):
            for k, s in enumerate(starts):
                passes = []
                for row in B.SPLIT_ROWS:
                    base, full = lead["init_H"][j, k], lead["carried"][i, j, k, q[row]] - lead["init_H"][j, k]
                    for v in B.VARIANTS:
                        passes.append((f"{v}|{row}", base + fold[v] * full, {}))
                        want_harm[row][v].append(base + fold[v] * full)
                receipt[f"variants/variants_{h}_{a}_s{s}.npz"] = _unit(folder, f"variants_{h}_{a}_s{s}", passes)
    names = [n[len("variants/"):-4] for n in receipt]
    units = V.checked_units(folder, receipt, names, prefix="variants/")
    plan2 = V.checked_units(p2, receipt2, ["ones_H1", "ones_H3"])
    res = V.variants(units, plan2, lead)
    assert res["all_ones_harm"] == pytest.approx(np.mean([0.01, 0.03]))
    for row in B.SPLIT_ROWS:
        assert res["rows"][row]["cells"] == 2 * 2 * 2
        for v in B.VARIANTS:
            assert res["rows"][row][v]["kept_share"] == pytest.approx(fold[v]) and res["rows"][row][v]["mean_harm"] == pytest.approx(np.mean(want_harm[row][v]))
    chk = V.checks(units)
    assert chk["H1"]["check|s_everywhere"]["bits_equal"] is True and chk["H1"]["check|s0_everywhere"]["bits_equal"] is False
    text = V.report(res, chk)
    assert text.startswith("Three intact-background variants") and V.NOTE in text and "added after the readings, as description" in V.NOTE.lower()
    receipt["variants/variants_H3_A2_s10.npz"] = "0" * 64
    with pytest.raises(R.Refusal, match="variants_H3_A2_s10"):
        V.checked_units(folder, receipt, names, prefix="variants/")
