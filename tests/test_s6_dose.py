"""Session 6, plan 3, Section 8: the dose-response's launch without the cloud, and its reading on made-up units.

The specs and their refusals; the projection from plan 3's variants containers and the refusal over $8; the whole
launch on the tiny model (one S4 batch, two attack batches, two starts) through the commands the cloud module calls,
with a dose pass rebuilt and rescored independently; a failing check stopping the container; the copy; and the
reading's pooled shares on a design whose answers are known by hand.
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
from vpd_audit_2 import s6_dose as DR
from vpd_audit_2 import s6_dose_run as D
from vpd_audit_2 import s6_run as SR
from vpd_audit_2 import s6_variants as V

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504
COMMIT = "a" * 40
REFS = {h: {"prep_fp": "x"} for h in SR.HELDOUT}
ATT, RUN_STARTS = ("A1", "A2"), (9, 10)


def test_the_specs_four_s4_containers_and_their_refusals():
    specs = D.specs(COMMIT, REFS)
    assert [s["batch"] for s in specs] == ["H1", "H5", "H9", "H13"]
    for s in specs:
        D.check_spec(s)
        D.check_spec({**s, "launch": "ap-x|s6_dose|1"})
        assert s["refs"] == {s["batch"]: REFS[s["batch"]]} and s["units"] == "units" and s["root"] == "/cache/s6_dose"
    for change in ({"batch": "H2"}, {"part": "variants"}, {"units": "variants"}, {"root": "/cache/s6_plan3"}, {"starts": [9]}, {"commit": "x"},
                   {"refs": {"H1": {}, "H5": {}}}, {"extra": 1}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            D.check_spec({**specs[0], **change})
    assert len(D.expected_files()) == 4 * 81


def test_the_projection_from_plan_3s_variants_containers():
    p = D.projection(LISTED)
    t = [c["timings"] for c in json.load(open(D.R3.RESULTS / "runs_s6_plan3.json"))["containers"] if c["container"].startswith("s6_variants|")]
    assert len(t) == 4 and p["passes"] == 4 * 1203
    per = np.mean([x["unit_variants"] / x["unit_variants_count"] for x in t])
    sec = 4 * (np.mean([x["to_ready"] for x in t]) + np.mean([x["unit_variants_check"] for x in t]) + 1200 * per
               + 9 * np.mean([x["volume_commit"] / x["volume_commit_count"] for x in t]))
    assert p["function_seconds"] == pytest.approx(sec) and p["dollars"] == pytest.approx(max(sec / 3600 * 6.80, (sec + 200) / 3600 * LISTED))
    assert p["exceeds_cap"] is False and p["cap"] == 8.0 and 1.0 < p["projected_dollars"] < 4.0


def test_over_eight_dollars_nothing_launches(tmp_path, monkeypatch):
    record = json.load(open(D.R3.RESULTS / "runs_s6_plan3.json"))
    for c in record["containers"]:
        if "unit_variants" in c["timings"]:  # the variants containers; the rerun's have none
            c["timings"]["unit_variants"] *= 5
    (tmp_path / "runs.json").write_text(json.dumps(record))
    monkeypatch.setattr(D, "RESULTS", tmp_path / "s6_dose")
    monkeypatch.setattr(D, "check_launch_commit", lambda commit: None)
    monkeypatch.setattr(D, "projection", lambda price, _p=D.projection: _p(price, plan3_record=tmp_path / "runs.json"))
    spawned = []
    cloud = LL.Cloud(spawn=spawned.append, set_stop=lambda v: None, attempts=lambda s: 0, read_bill=lambda apps: {}, guards=lambda s: {}, app_id="ap-x",
                     log=lambda **f: None)
    with pytest.raises(LL.LaunchRefusal, match="C0"):
        D.launch_command(COMMIT, cloud, listed_hourly_price=LISTED, refs=REFS)
    assert spawned == [] and json.load(open(tmp_path / "s6_dose" / "ledger.json"))["checks"][0]["dollars"] > 8.0


class Tiny:
    def __init__(self) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, int(self.model.module_to_c[k])) for k in self.model.target_module_paths]
        self.n = sum(c + 1 for _, c in self.lay)
        rng = np.random.default_rng(12)
        self.ids = tiny_ids(8, seed=44).numpy()
        self.rows = LR.sha_rows(self.ids)
        self.flat_starts = {s: rng.random(self.n).astype(np.float32) for s in RUN_STARTS}
        self.strata = {k: rng.integers(0, 11, c) for k, c in self.lay}
        self.units = {}
        for a in ATT:
            for s in RUN_STARTS:
                settings = []
                for _ in B.SPLIT_ROWS:
                    u, v = rng.random(self.n), rng.random(self.n)
                    settings.append(np.where(u < 0.4, 0.0, np.where(u > 0.7, 1.0, v)).astype(np.float32))
                self.units[(a, s)] = {"hook_names": np.array([LR.SAVED[r] for r in B.SPLIT_ROWS]), "settings": np.stack(settings),
                                      "cum_signed": np.zeros((len(B.SPLIT_ROWS), self.n), dtype=np.float32)}
        self.prep = A.prepare(self.model, self.ids, "fp32", device="cpu")
        score = lambda flat: SR.score_flat(self.model, flat, self.prep, self.lay, "cpu")[0]  # noqa: E731
        self.refs = {"H1": {"prep_fp": LR.prep_fingerprint(self.prep), "own_attack": "A1", "check_attack": "A1",
                            "check_carried": score(B.saved(self.units[("A1", 9)], "n320")[0]), "check_start": score(self.flat_starts[9])}}

    def inputs(self) -> SR.Inputs:
        return SR.Inputs(starts=self.flat_starts, strata=self.strata, read_run_unit=lambda a, s: self.units[(a, s)], b2=None)

    def run(self, spec: dict) -> dict:
        D.check_spec(spec)
        ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=self.lay, device="cpu", precision="fp32", mode="test")
        out = D.dose_job(self.model, ctx, spec, {"H1": (self.ids, self.rows)}, self.inputs())
        out["attempts"] = 1
        return out

    def cloud(self) -> LL.Cloud:
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec

            def get(self, timeout: float) -> dict:
                return me.run(self.spec)

        return LL.Cloud(spawn=Now, set_stop=lambda value: None, attempts=lambda spec: 1, read_bill=lambda apps: {"read_at": "x", "by_app": {}},
                        guards=lambda spec: {"outcomes": {}, "seconds": 0.0}, app_id="ap-tiny", log=lambda **f: None)


def _patches(mp, tmp: Path) -> None:
    mp.setattr(D, "RESULTS", tmp / "results" / "s6_dose")
    mp.setattr(D, "VOLUME", str(tmp / "volume"))
    mp.setattr(D, "LOCAL", tmp / "local")
    mp.setattr(D, "BATCHES", ("H1",))
    mp.setattr(SR, "ATTACK", ATT)
    mp.setattr(SR, "STARTS", RUN_STARTS)
    mp.setattr(D, "check_launch_commit", lambda commit: None)
    mp.setattr(D, "tree_holds_only_this_plans_records", lambda: True)
    mp.setattr(LL, "head_commit", lambda: COMMIT)


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("dose")
    t = Tiny()
    with pytest.MonkeyPatch.context() as mp:
        _patches(mp, tmp)
        mp.setattr(D, "projection", lambda price: {"check": "C0", "projected_dollars": 0.0, "exceeds_cap": False})
        summary = D.launch_command(COMMIT, t.cloud(), listed_hourly_price=LISTED, refs=t.refs)
        files = D.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes(), log=lambda **f: None)
    return {"tmp": tmp, "t": t, "summary": summary, "files": files}


def test_the_whole_launch_runs_through_its_commands(tiny):
    s = tiny["summary"]
    assert s["complete"] is True and s["all_guards_true"] is True and s["finished_units"] == s["expected_units"] == 1 + 4
    assert len(tiny["files"]) == 5 and all(rel.startswith("units/") for rel in tiny["files"])
    run = json.load(open(tiny["tmp"] / "results" / "s6_dose" / "runs_s6_dose.json"))
    units = {u["unit"]: u for c in run["containers"] for u in c["units"]}
    assert units["dose_check_H1"]["guards"] == {"split_path_s_everywhere": True, "split_path_s0_everywhere": True, "flat_path_bits_equal": True}


def test_a_dose_pass_is_its_seeded_setting_scored(tiny):
    t = tiny["t"]
    with np.load(tiny["tmp"] / "local" / "units" / "dose_H1_A2_s10.npz", allow_pickle=False) as z:
        ids = [str(x) for x in z["pass_ids"]]
        harm, rec = z["harm"], SR.json_field(z, "recorded")
    assert ids == [f"D{B.dose_key(f)}|{row}" for row in B.SPLIT_ROWS for f in B.DOSE_FRACTIONS]
    s = B.saved(t.units[("A2", 10)], "n160")[0]
    k = ids.index("D0.5|n160")
    flat, zeros, kept = B.dose_setting(s, 0.5, B.dose_seed("A2", 10, "n160", 0.5))
    assert harm[k] == SR.score_flat(t.model, flat, t.prep, t.lay, "cpu")[0]
    assert rec[k]["zeros"] == zeros and rec[k]["kept_at_0"] == kept and rec[k]["setting_sha"] == B.sha(flat)


def test_a_dose_container_whose_check_fails_stops_before_any_dose(tiny, tmp_path):
    t = tiny["t"]
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        mp.setattr(D, "BATCHES", ("H1",))
        refs = {"H1": {**t.refs["H1"], "check_carried": t.refs["H1"]["check_carried"] * (1 + 1e-12)}}
        spec = D.specs(COMMIT, refs)[0]
        ctx = SR.Context(commit=COMMIT, units=tmp_path, lay=t.lay, device="cpu", precision="fp32", mode="test")
        with pytest.raises(SR.S6Failure, match="a path does not give the saved harm"):
            D.dose_job(t.model, ctx, spec, {"H1": (t.ids, t.rows)}, t.inputs())
        assert not list(tmp_path.glob("dose_H1_*.npz"))


def test_the_copy_refuses_bytes_that_are_not_the_ones_returned(tiny, tmp_path):
    with pytest.MonkeyPatch.context() as mp:
        _patches(mp, tiny["tmp"])

        def read(remote: str) -> bytes:
            data = Path(remote).read_bytes()
            return data + b"x" if remote.endswith("dose_H1_A1_s10.npz") else data

        with pytest.raises(LL.LaunchRefusal, match="dose_H1_A1_s10.npz"):
            D.collect_command(COMMIT, read_file=read, log=lambda **f: None, dest=tmp_path / "u")


# ----------------------------------------------------------------------------- the reading


def _unit(folder: Path, name: str, passes: list[tuple[str, float, dict]]) -> str:
    arrays = {"pass_ids": np.array([p for p, _, _ in passes]), "harm": np.array([h for _, h, _ in passes], dtype=np.float64),
              "per_text": np.tile(np.array([[h] for _, h, _ in passes], dtype=np.float32), (1, 4)),
              "recorded": np.array(json.dumps([r for _, _, r in passes])), "meta": np.array(json.dumps({"unit": name}))}
    return LR.write_unit(folder / f"{name}.npz", arrays)


def test_the_reading_pools_by_hand(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "BATCHES", ("H1", "H3"))
    att, held, starts = ("A1", "A2"), ("H1", "H2", "H3"), (9, 10)
    rng = np.random.default_rng(7)
    Q = len(LT.SETTINGS_LEAD)
    lead = {"attack_names": np.array(att), "heldout_names": np.array(held), "starts": np.array(starts), "setting_names": np.array(LT.SETTINGS_LEAD),
            "init_H": 0.2 + 0.01 * rng.random((3, 2)), "carried": 5 + 20 * rng.random((2, 3, 2, Q))}
    q = {n: k for k, n in enumerate(LT.SETTINGS_LEAD)}
    fold = {0.25: 0.1, 0.5: 0.3, 0.75: 0.6, 1.0: 0.9}
    du, vu, p2 = tmp_path / "dose", tmp_path / "variants", tmp_path / "plan2"
    for j, h in enumerate(held):
        if h not in D.BATCHES:
            continue
        _unit(du, f"dose_check_{h}", [("check|flat", 1.5, {"reference": 1.5})])
        _unit(p2, f"ones_{h}", [("ones", 0.2 + 0.1 * j, {})])
        for i, a in enumerate(att):
            for k, s in enumerate(starts):
                base = lead["init_H"][j, k]
                full = {row: lead["carried"][i, j, k, q[row]] - base for row in B.SPLIT_ROWS}
                _unit(du, f"dose_{h}_{a}_s{s}", [(f"D{B.dose_key(f)}|{row}", base + fold[f] * full[row], {}) for row in B.SPLIT_ROWS for f in B.DOSE_FRACTIONS])
                _unit(vu, f"variants_{h}_{a}_s{s}", [(f"V1|{row}", base + fold[1.0] * full[row], {}) for row in B.SPLIT_ROWS])
    from vpd_audit_2 import s6_read as R

    res = DR.dose(R.Units(du), R.Units(vu), R.Units(p2), lead)
    for row in B.SPLIT_ROWS:
        x = res["rows"][row]
        assert x["cells"] == 8
        for f, v in fold.items():
            assert x[B.dose_key(f)]["kept_share"] == pytest.approx(v)
        # f = 0: the all-ones harm on every cell of its batch
        den = sum(lead["carried"][i, j, k, q[row]] - lead["init_H"][j, k] for i in range(2) for j in (0, 2) for k in range(2))
        num = sum((0.2 + 0.1 * j) - lead["init_H"][j, k] for i in range(2) for j in (0, 2) for k in range(2))
        assert x["0"]["kept_share"] == pytest.approx(num / den) and x["0"]["mean_harm"] == pytest.approx(np.mean([0.2, 0.4]))
    assert res["per_batch_at_320"]["H3"]["0.5"] == pytest.approx(0.3) and set(res["per_batch_at_320"]) == {"H1", "H3"}
    text = DR.report(res, DR.checks(R.Units(du)))
    assert DR.NOTE in text and "added after the readings, as description" in DR.NOTE.lower() and "f = 0.25" in text and "f = 1" in text
    assert "At 320 steps, the kept share per batch" in text


def test_nothing_in_the_driver_prints():
    import re

    for module in ("s6_dose_run", "modal_s6_dose"):
        text = Path(D.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module
