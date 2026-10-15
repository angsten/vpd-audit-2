"""Session 6, plan 3, Section 9: the dose-response on the rounded off set, its launch without the cloud, and its reading
on made-up units.

The specs and their refusals; the f = 1 hash check, passing and refusing; the projection from Section 8's containers
and the refusal over $6; the whole launch on the tiny model through the commands the cloud module calls, with one pass
rebuilt and rescored independently; a failing check stopping the container; and the reading's pooled shares by hand.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_dose_rounded as RD
from vpd_audit_2 import s6_dose_rounded_run as D
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_run as SR

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504
COMMIT = "b" * 40
REFS = {h: {"prep_fp": "x"} for h in SR.HELDOUT}
ATT, RUN_STARTS = ("A1", "A2"), (9, 10)
PASS = lambda: {"all_equal": True, "compared": 1, "equal": 1}  # noqa: E731


def test_the_specs_four_s4_containers_and_their_refusals():
    specs = D.specs(COMMIT, REFS)
    assert [s["batch"] for s in specs] == ["H1", "H5", "H9", "H13"]
    for s in specs:
        D.check_spec(s)
        assert s["root"] == "/cache/s6_dose_rounded" and s["part"] == "dose_rounded"
    for change in ({"batch": "H2"}, {"part": "dose"}, {"root": "/cache/s6_dose"}, {"starts": [9]}, {"commit": "x"}, {"refs": {"H1": {}, "H5": {}}}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            D.check_spec({**specs[0], **change})
    assert len(D.expected_files()) == 4 * 81


def test_the_f1_hash_check_passes_and_refuses():
    rng = np.random.default_rng(2)
    units = {(a, s): {"hook_names": np.array([LR.SAVED[r] for r in B.SPLIT_ROWS]), "settings": rng.random((5, 40)).astype(np.float32),
                      "cum_signed": np.zeros((5, 40), dtype=np.float32)} for a in ATT for s in RUN_STARTS}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        rec = {(f"controls_{h}_{a}_s{s}", f"d|rounded|{row}"): {"setting_sha": B.sha(B.rounded(B.saved(units[(a, s)], row)[0]))}
               for h in D.BATCHES for a in ATT for s in RUN_STARTS for row in B.SPLIT_ROWS}
        hc = D.rounded_hash_check(read_run_unit=lambda a, s: units[(a, s)], recorded=lambda n, p: rec[(n, p)])
        assert hc["all_equal"] and hc["compared"] == 4 * 4 * 5 and hc["settings_equal_to_rounded"] == hc["settings"] == 20
        rec[("controls_H9_A2_s10", "d|rounded|n80")] = {"setting_sha": "0" * 64}
        hc = D.rounded_hash_check(read_run_unit=lambda a, s: units[(a, s)], recorded=lambda n, p: rec[(n, p)])
        assert not hc["all_equal"] and hc["mismatches"] == ["H9 A2 s10 n80"]


def test_the_f1_hash_check_on_the_real_settings():
    if not (D.RUN_UNITS_LOCAL / "search_A1_s9.npz").is_file() or not (SR.LOCAL_UNITS / "controls_H1_A1_s9.npz").is_file():
        pytest.skip("the run's and plan 2's unit files are on this machine only")
    hc = D.rounded_hash_check()
    assert hc["all_equal"] and hc["compared"] == 1600 and hc["settings_equal_to_rounded"] == 400


def test_the_projection_from_section_8s_containers():
    p = D.projection(LISTED)
    t = [c["timings"] for c in json.load(open(D.D.RESULTS / "runs_s6_dose.json"))["containers"]]
    per = np.mean([x["unit_dose"] / x["unit_dose_count"] for x in t])
    sec = 4 * (np.mean([x["to_ready"] for x in t]) + np.mean([x["unit_variants_check"] for x in t]) + 1600 * per
               + 9 * np.mean([x["volume_commit"] / x["volume_commit_count"] for x in t]))
    assert p["passes"] == 4 * 1603 and p["function_seconds"] == pytest.approx(sec)
    assert p["dollars"] == pytest.approx(max(sec / 3600 * 6.80, (sec + 200) / 3600 * LISTED)) and p["cap"] == 6.0 and p["exceeds_cap"] is False


def _cloud(spawned: list) -> LL.Cloud:
    return LL.Cloud(spawn=spawned.append, set_stop=lambda v: None, attempts=lambda s: 0, read_bill=lambda apps: {}, guards=lambda s: {}, app_id="ap-x",
                    log=lambda **f: None)


def test_over_six_dollars_or_a_hash_mismatch_nothing_launches(tmp_path, monkeypatch):
    record = json.load(open(D.D.RESULTS / "runs_s6_dose.json"))
    for c in record["containers"]:
        c["timings"]["unit_dose"] *= 3
    (tmp_path / "runs.json").write_text(json.dumps(record))
    monkeypatch.setattr(D, "RESULTS", tmp_path / "a")
    monkeypatch.setattr(D, "check_launch_commit", lambda commit: None)
    monkeypatch.setattr(D, "projection", lambda price, _p=D.projection: _p(price, dose_record=tmp_path / "runs.json"))
    spawned: list = []
    with pytest.raises(LL.LaunchRefusal, match="C0"):
        D.launch_command(COMMIT, _cloud(spawned), listed_hourly_price=LISTED, refs=REFS, hash_check=PASS)
    assert spawned == [] and json.load(open(tmp_path / "a" / "ledger.json"))["checks"][0]["dollars"] > 6.0
    monkeypatch.setattr(D, "RESULTS", tmp_path / "b")
    with pytest.raises(LL.LaunchRefusal, match="hash"):
        D.launch_command(COMMIT, _cloud(spawned), listed_hourly_price=LISTED, refs=REFS, hash_check=lambda: {"all_equal": False, "compared": 1, "equal": 0})
    assert spawned == [] and json.load(open(tmp_path / "b" / "rounded_check.json"))["all_equal"] is False
    assert not (tmp_path / "b" / "ledger.json").exists() or not json.load(open(tmp_path / "b" / "ledger.json"))["checks"]


class Tiny:
    def __init__(self) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, int(self.model.module_to_c[k])) for k in self.model.target_module_paths]
        self.n = sum(c + 1 for _, c in self.lay)
        rng = np.random.default_rng(13)
        self.ids = tiny_ids(8, seed=45).numpy()
        self.rows = LR.sha_rows(self.ids)
        self.flat_starts = {s: rng.random(self.n).astype(np.float32) for s in RUN_STARTS}
        self.strata = {k: rng.integers(0, 11, c) for k, c in self.lay}
        self.units = {}
        for a in ATT:
            for s in RUN_STARTS:
                self.units[(a, s)] = {"hook_names": np.array([LR.SAVED[r] for r in B.SPLIT_ROWS]), "settings": rng.random((5, self.n)).astype(np.float32),
                                      "cum_signed": np.zeros((5, self.n), dtype=np.float32)}
        self.prep = A.prepare(self.model, self.ids, "fp32", device="cpu")
        score = lambda flat: SR.score_flat(self.model, flat, self.prep, self.lay, "cpu")[0]  # noqa: E731
        self.refs = {"H1": {"prep_fp": LR.prep_fingerprint(self.prep), "own_attack": "A1", "check_attack": "A1",
                            "check_carried": score(B.saved(self.units[("A1", 9)], "n320")[0]), "check_start": score(self.flat_starts[9])}}

    def inputs(self) -> SR.Inputs:
        return SR.Inputs(starts=self.flat_starts, strata=self.strata, read_run_unit=lambda a, s: self.units[(a, s)], b2=None)

    def cloud(self) -> LL.Cloud:
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec

            def get(self, timeout: float) -> dict:
                D.check_spec(self.spec)
                ctx = SR.Context(commit=COMMIT, units=Path(self.spec["root"]) / self.spec["units"], lay=me.lay, device="cpu", precision="fp32", mode="test")
                out = D.job(me.model, ctx, self.spec, {"H1": (me.ids, me.rows)}, me.inputs())
                out["attempts"] = 1
                return out

        return LL.Cloud(spawn=Now, set_stop=lambda value: None, attempts=lambda spec: 1, read_bill=lambda apps: {"read_at": "x", "by_app": {}},
                        guards=lambda spec: {"outcomes": {}, "seconds": 0.0}, app_id="ap-tiny", log=lambda **f: None)


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("dose_rounded")
    t = Tiny()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(D, "RESULTS", tmp / "results")
        mp.setattr(D, "VOLUME", str(tmp / "volume"))
        mp.setattr(D, "LOCAL", tmp / "local")
        mp.setattr(D, "BATCHES", ("H1",))
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        mp.setattr(D, "check_launch_commit", lambda commit: None)
        mp.setattr(D, "tree_holds_only_this_plans_records", lambda: True)
        mp.setattr(LL, "head_commit", lambda: COMMIT)
        mp.setattr(D, "projection", lambda price: {"check": "C0", "projected_dollars": 0.0, "exceeds_cap": False})
        summary = D.launch_command(COMMIT, t.cloud(), listed_hourly_price=LISTED, refs=t.refs, hash_check=PASS)
        files = D.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes(), log=lambda **f: None)
    return {"tmp": tmp, "t": t, "summary": summary, "files": files}


def test_the_whole_launch_and_one_pass_rescored(tiny):
    s = tiny["summary"]
    assert s["complete"] is True and s["all_guards_true"] is True and s["finished_units"] == s["expected_units"] == 5 and len(tiny["files"]) == 5
    t = tiny["t"]
    with np.load(tiny["tmp"] / "local" / "units" / "dose_rounded_H1_A1_s10.npz", allow_pickle=False) as z:
        ids = [str(x) for x in z["pass_ids"]]
        harm, rec = z["harm"], SR.json_field(z, "recorded")
    assert ids == [f"R{B.dose_key(f)}|{row}" for row in B.SPLIT_ROWS for f in B.DOSE_ROUNDED_FRACTIONS]
    s_ = B.saved(t.units[("A1", 10)], "n40")[0]
    k = ids.index("R0.9|n40")
    flat, off, kk = B.dose_rounded_setting(s_, 0.9, B.dose_rounded_seed("A1", 10, "n40", 0.9))
    assert harm[k] == SR.score_flat(t.model, flat, t.prep, t.lay, "cpu")[0] and rec[k]["off_set"] == off and rec[k]["set_to_0"] == kk


def test_a_container_whose_check_fails_stops_before_any_pass(tiny, tmp_path):
    t = tiny["t"]
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        mp.setattr(D, "BATCHES", ("H1",))
        refs = {"H1": {**t.refs["H1"], "check_start": t.refs["H1"]["check_start"] * 1.01}}
        ctx = SR.Context(commit=COMMIT, units=tmp_path, lay=t.lay, device="cpu", precision="fp32", mode="test")
        with pytest.raises(SR.S6Failure, match="a path does not give the saved harm"):
            D.job(t.model, ctx, D.specs(COMMIT, refs)[0], {"H1": (t.ids, t.rows)}, t.inputs())
        assert not list(tmp_path.glob("dose_rounded_H1_*.npz"))


def _unit(folder: Path, name: str, passes: list[tuple[str, float, dict]]) -> None:
    arrays = {"pass_ids": np.array([p for p, _, _ in passes]), "harm": np.array([h for _, h, _ in passes], dtype=np.float64),
              "per_text": np.tile(np.array([[h] for _, h, _ in passes], dtype=np.float32), (1, 4)),
              "recorded": np.array(json.dumps([r for _, _, r in passes])), "meta": np.array(json.dumps({"unit": name}))}
    LR.write_unit(folder / f"{name}.npz", arrays)


def test_the_reading_pools_by_hand(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "BATCHES", ("H2", "H3"))
    att, held, starts = ("A1", "A2"), ("H1", "H2", "H3"), (9, 10)
    rng = np.random.default_rng(8)
    Q = len(LT.SETTINGS_LEAD)
    lead = {"attack_names": np.array(att), "heldout_names": np.array(held), "starts": np.array(starts), "setting_names": np.array(LT.SETTINGS_LEAD),
            "init_H": 0.2 + 0.01 * rng.random((3, 2)), "carried": 5 + 20 * rng.random((2, 3, 2, Q))}
    q = {n: k for k, n in enumerate(LT.SETTINGS_LEAD)}
    fold = {0.25: 0.05, 0.5: 0.1, 0.75: 0.3, 0.9: 0.6, 1.0: 1.0}
    du, p2 = tmp_path / "dose", tmp_path / "plan2"
    for j, h in enumerate(held):
        if h not in D.BATCHES:
            continue
        _unit(du, f"dose_rounded_check_{h}", [("check|flat", 1.5, {"reference": 1.5})])
        _unit(p2, f"ones_{h}", [("ones", 0.1 * j, {})])
        for i, a in enumerate(att):
            for k, s in enumerate(starts):
                base = lead["init_H"][j, k]
                full = {row: lead["carried"][i, j, k, q[row]] - base for row in B.SPLIT_ROWS}
                _unit(du, f"dose_rounded_{h}_{a}_s{s}", [(f"R{B.dose_key(f)}|{row}", base + fold[f] * full[row], {})
                                                         for row in B.SPLIT_ROWS for f in B.DOSE_ROUNDED_FRACTIONS])
                _unit(p2, f"controls_{h}_{a}_s{s}", [(f"d|rounded|{row}", base + fold[1.0] * full[row], {}) for row in B.SPLIT_ROWS])
    res = RD.dose_rounded(R.Units(du), R.Units(p2), lead)
    for row in B.SPLIT_ROWS:
        x = res["rows"][row]
        assert x["cells"] == 8 and all(x[B.dose_key(f)]["kept_share"] == pytest.approx(v) for f, v in fold.items())
        assert x["0"]["mean_harm"] == pytest.approx(np.mean([0.1, 0.2]))
    assert res["per_batch_at_320"]["H2"]["0.9"] == pytest.approx(0.6) and set(res["per_batch_at_320"]) == {"H2", "H3"}
    text = RD.report(res, RD.checks(R.Units(du)), {"equal": 1600, "compared": 1600, "settings_equal_to_rounded": 400, "settings": 400})
    assert RD.NOTE in text and "f = 0.9" in text and "in 1600 of 1600 cells" in text


def test_nothing_in_the_driver_prints():
    import re

    for module in ("s6_dose_rounded_run", "modal_s6_dose_rounded"):
        text = Path(D.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module
