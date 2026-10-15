"""Session 7, plan 6: the three-arm launch without the cloud (`vpd_audit_2/three_arm_run.py`), on the tiny model.

  - The specs and their refusals.
  - The whole experiment through the commands the cloud module calls: the gate and its verdict, the rehearsal and its
    projection, the six runs, the extension rule, the carry plan and stage, each collected; one run recomputed
    independently; the reading on the collected units.
  - Nothing runs after a failed gate or before the stages it needs, and nothing launches over the cap.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_run as SR
from vpd_audit_2 import three_arm as T
from vpd_audit_2 import three_arm_read as R
from vpd_audit_2 import three_arm_run as TR

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504
COMMIT = "d" * 40
NB, NMAX, NREH, NT = 6, 12, 3, 8


def test_the_specs_and_their_refusals():
    sp = TR.specs("run", COMMIT, "f" * 64)
    assert [s["batch"] for s in sp] == [f"{a}|s{s}" for a in T.ARMS for s in TR.SEEDS] and all(s["job"]["n_batches"] == 1000 for s in sp)
    for s in sp + TR.specs("gate", COMMIT, "f" * 64) + TR.specs("rehearsal", COMMIT, "f" * 64) + TR.specs("extension", COMMIT, "f" * 64, extension={"released": 1500}):
        TR.check_spec(s)
    refs = {h: {"prep_fp": "x"} for h in TR.CARRY_BATCHES}
    TR.check_spec(TR.specs("carry", COMMIT, "f" * 64, refs=refs, carry=[])[0])
    for change in ({"job": {**sp[0]["job"], "n_batches": 999}}, {"job": {**sp[0]["job"], "seed": 3}}, {"root": "/cache/x"}, {"commit": "x"}, {"batch": "batch|s1"}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            TR.check_spec({**sp[0], **change})
    with pytest.raises(LR.GuardFailure):
        TR.check_spec(TR.specs("extension", COMMIT, "f" * 64, extension={"batch": 1500})[0])
    with pytest.raises(LR.GuardFailure):
        TR.check_spec(TR.specs("extension", COMMIT, "f" * 64, extension={"released": 900})[0])


class Tiny:
    def __init__(self) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, int(self.model.module_to_c[k])) for k in self.model.target_module_paths]
        self.texts = {"run": tiny_ids(NMAX * NT, seed=31).numpy().reshape(NMAX, NT, -1), "calibration": tiny_ids(NREH * NT, seed=32).numpy().reshape(NREH, NT, -1)}
        self.held = {h: tiny_ids(NT, seed=40 + q).numpy() for q, h in enumerate(TR.CARRY_BATCHES)}

    def cloud(self, spawned: list | None = None) -> LL.Cloud:
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec
                if spawned is not None:
                    spawned.append(spec)

            def get(self, timeout: float) -> dict:
                TR.check_spec(self.spec)
                root = Path(self.spec["root"])
                ctx = SR.Context(commit=COMMIT, units=root / self.spec["units"], lay=me.lay, device="cpu", precision="fp32", mode="test")

                def read_sources(unit: str, sha: str) -> np.ndarray:
                    import hashlib
                    import io

                    data = (root / TR.UNITS / f"{unit}.npz").read_bytes()
                    assert hashlib.sha256(data).hexdigest() == sha
                    with np.load(io.BytesIO(data)) as z:
                        return z["sources"]

                inputs = {h: (ids, LR.sha_rows(ids)) for h, ids in me.held.items()}
                out = TR.job(me.model, ctx, self.spec, texts=me.texts, batch_inputs=inputs, read_sources=read_sources)
                out["attempts"] = 1
                return out

        return LL.Cloud(spawn=Now, set_stop=lambda value: None, attempts=lambda spec: 1, read_bill=lambda apps: {"read_at": "x", "by_app": {}},
                        guards=lambda spec: {"outcomes": {}, "seconds": 0.0}, app_id="ap-tiny", log=lambda **f: None)


def _patch(mp: pytest.MonkeyPatch, tmp: Path) -> None:
    mp.setattr(TR, "RESULTS", tmp / "results")
    mp.setattr(TR, "VOLUME", str(tmp / "volume"))
    mp.setattr(TR, "LOCAL", tmp / "local")
    mp.setattr(TR, "N_BATCHES", NB)
    mp.setattr(TR, "N_MAX", NMAX)
    mp.setattr(TR, "REHEARSAL_BATCHES", NREH)
    mp.setattr(R, "N_BATCHES", NB)
    mp.setattr(R, "TREND_BATCHES", 3)
    mp.setattr(TR, "check_launch_commit", lambda commit: None)
    mp.setattr(TR, "tree_holds_only_this_plans_records", lambda: True)
    mp.setattr(LL, "head_commit", lambda: COMMIT)
    (tmp / "results").mkdir(parents=True, exist_ok=True)
    (tmp / "results" / "texts.json").write_text(json.dumps({"texts_file_sha256": "f" * 64}))


@pytest.fixture(scope="module")
def tiny_run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("three_arm")
    t = Tiny()
    read = lambda remote: Path(remote).read_bytes()  # noqa: E731
    log = lambda **f: None  # noqa: E731
    refs = {h: {"prep_fp": "x"} for h in TR.CARRY_BATCHES}
    out = {"tmp": tmp, "t": t}
    with pytest.MonkeyPatch.context() as mp:
        _patch(mp, tmp)
        out["gate_stage"] = TR.launch_command("gate", COMMIT, t.cloud(), listed_hourly_price=LISTED)
        TR.collect_command("gate", COMMIT, read_file=read, log=log)
        out["gate"] = TR.gate_command(COMMIT)
        TR.launch_command("rehearsal", COMMIT, t.cloud(), listed_hourly_price=LISTED)
        TR.collect_command("rehearsal", COMMIT, read_file=read, log=log)
        out["rehearsal"] = TR.rehearsal_command(COMMIT, listed_hourly_price=LISTED)
        out["run_stage"] = TR.launch_command("run", COMMIT, t.cloud(), listed_hourly_price=LISTED)
        TR.collect_command("run", COMMIT, read_file=read, log=log)
        out["extension"] = TR.extension_command(COMMIT)
        out["carry_plan"] = TR.carry_command(COMMIT)
        TR.launch_command("carry", COMMIT, t.cloud(), listed_hourly_price=LISTED, refs=refs)
        TR.collect_command("carry", COMMIT, read_file=read, log=log)
        out["ledger"] = json.load(open(tmp / "results" / "ledger.json"))
        out["read"] = R.compute(tmp / "results", units_folder=tmp / "local" / "units")
        out["text"] = R.report(out["read"])
    return out


def test_the_gate(tiny_run):
    g = tiny_run["gate"]
    assert g["passes"] is True
    for arm in T.ARMS:
        a = g["arms"][arm]
        assert a["start_equal"] and a["loss_bits_equal"] and a["sources_bits_equal"], arm
    assert g["scaled_gradient"]["scale"] == 2.0 and g["scaled_gradient"]["mismatches"] == 0 and g["scaled_gradient"]["entries_compared"] > 0
    assert g["per_document_loss_bits_equal"] is True and 0.0 <= g["process_emulation"]["share_equal"] <= 1.0


def test_the_rehearsal_and_its_projection(tiny_run):
    r = tiny_run["rehearsal"]
    assert set(r["arms"]) == set(T.ARMS) and all(x["seconds_per_batch"] > 0 for x in r["arms"].values())
    p = r["projection_before_run"]
    assert p["cap"] == 35.0 and [x["stage"] for x in p["parts"]] == ["run", "carry"] and len(p["parts"][0]["containers"]) == 6
    assert r["projection_of_the_largest_extension"]["parts"][0]["containers"][0]["container"] == "per_document|x"


def test_the_runs_and_one_recomputed(tiny_run):
    s = tiny_run["run_stage"]
    assert s["complete"] is True and s["finished_units"] == s["expected_units"] == 6
    t = tiny_run["t"]
    ctx = SR.Context(commit=COMMIT, units=tiny_run["tmp"] / "x", lay=t.lay, device="cpu", precision="fp32", mode="test")
    again = TR.run_arm(t.model, ctx, "per_document", 2, t.texts["run"][:NB], record_sources=False)
    with np.load(tiny_run["tmp"] / "local" / "units" / f"{TR.run_unit_name('run', 'per_document', 2, NB)}.npz") as z:
        for k in T.SERIES:
            assert np.array_equal(z[k], again[k]), k
        assert np.all(z["lr"] == 0.01) and json.loads(str(z["meta"].reshape(-1)[0]))["grad_scale"] == 2.0
    with np.load(tiny_run["tmp"] / "local" / "units" / f"{TR.run_unit_name('run', 'batch', 1, NB)}.npz") as z:
        assert z["sources"].shape == (NB, sum(c + 1 for _, c in t.lay))
    checks = [c["check"] for c in tiny_run["ledger"]["checks"] if c["check"].startswith("before_")]
    assert checks == ["before_gate", "before_rehearsal", "before_run", "before_carry"]


def test_the_carry_stage_and_the_reading(tiny_run):
    r = tiny_run["read"]
    assert set(r["arms"]) == {f"{a}|s{s}" for a in T.ARMS for s in TR.SEEDS} and r["reading"]["number"] in (1, 2, 3, 4)
    b = r["reading"]["breakouts"]
    assert r["reading"]["number"] == R.reading(b["released"], b["batch"])
    carry = r["carry"]
    assert carry["settings"] == tiny_run["carry_plan"]["settings"] and set(carry["harms"]) == set(TR.CARRY_BATCHES)
    assert all(len(v) == len(carry["settings"]) for v in carry["harms"].values())
    assert "THE READING" in tiny_run["text"] and "Amendment 1" in tiny_run["text"] and "Arm 4" in tiny_run["text"]


def test_refusals(tiny_run, tmp_path):
    t = tiny_run["t"]
    with pytest.MonkeyPatch.context() as mp:
        _patch(mp, tmp_path)
        spawned: list = []
        with pytest.raises(LL.LaunchRefusal, match="gate is not complete"):
            TR.launch_command("rehearsal", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED)
        ledger = {"stages": {"s7_three_arm_gate": {"launches": [], "complete": True, "summary": None}}, "checks": [], "bills": [], "guards_pass": None,
                  "stopped_by": None, "stops": []}
        (tmp_path / "results" / "ledger.json").write_text(json.dumps(ledger))
        (tmp_path / "results" / "gate.json").write_text(json.dumps({"commit": COMMIT, "passes": False}))
        with pytest.raises(LL.LaunchRefusal, match="gate has not passed"):
            TR.launch_command("rehearsal", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED)
        (tmp_path / "results" / "gate.json").write_text(json.dumps({"commit": COMMIT, "passes": True}))
        ledger["stages"]["s7_three_arm_rehearsal"] = {"launches": [], "complete": True, "summary": None}
        (tmp_path / "results" / "ledger.json").write_text(json.dumps(ledger))
        slow = {"projection_inputs": {"to_ready": 60.0, "per_batch_released": 5000.0, "per_batch_per_document": 1.0, "per_batch_batch": 1.0}}  # 6 batches here
        (tmp_path / "results" / "rehearsal.json").write_text(json.dumps(slow))
        with pytest.raises(LL.LaunchRefusal, match="exceeds the cap"):
            TR.launch_command("run", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED)
        assert spawned == []
        with pytest.raises(LL.LaunchRefusal, match="does not call for an extension|run is not complete"):
            TR.launch_command("extension", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED)


def test_nothing_in_the_driver_prints():
    import re

    for module in ("three_arm", "three_arm_run", "modal_three_arm"):
        text = Path(TR.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module
