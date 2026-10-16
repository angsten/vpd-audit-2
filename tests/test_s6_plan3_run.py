"""Plan 3 of the research log: the launch of Sections 4 and 7, without the cloud.

The held-at-0 search path against `lead_run.search_unit` (at 1.0 they write the same arrays bit for bit) and against
the plain loop (at 0.0); the specs and their refusals; the inputs a container is handed; the projection; the checks
before the launch, in a small repository; and the whole launch on the tiny model through the commands the cloud module
calls: the rerun's containers and a variants container, the copy, and the rerun's reading on what was copied.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
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
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_rerun as RR
from vpd_audit_2 import s6_run as SR

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504
COMMIT = "f" * 40
N_TEXTS = 8
GOOD_ENV = {"gpu": "NVIDIA B200", "deterministic_algorithms": True, "deterministic_warn_only": False, "allow_tf32_matmul": False, "allow_tf32_cudnn": False,
            "cublas_workspace_config": ":4096:8", "vpd_audit_2_commit": COMMIT, "vpd_audit_2_dirty": "0"}
REFS = {h: {"prep_fp": "x"} for h in SR.HELDOUT}


# ----------------------------------------------------------------------------- the held-at-0 path


@pytest.fixture(scope="module")
def model():
    torch.use_deterministic_algorithms(True)
    m = tiny_component_model()
    lay = [(k, int(m.module_to_c[k])) for k in m.target_module_paths]
    g = torch.Generator().manual_seed(5)
    start = {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay}
    ids = tiny_ids(N_TEXTS, seed=7).numpy()
    prep = A.prepare(m, ids, "fp32", device="cpu")
    return {"model": m, "lay": lay, "start": start, "ids": ids, "prep": prep, "fp": LR.prep_fingerprint(prep)}


def _ctx(arm: str, units: Path, lay, **kw) -> LR.Context:
    return LR.Context(arm=arm, units=units, commit=COMMIT, lay=lay, precision="fp32", device="cpu", n_steps=R3.N_STEPS, mode="test", **kw)


def _arrays(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def test_at_one_the_frozen_path_writes_what_lead_runs_delta_held_path_writes(model, tmp_path):
    m = model
    ctx = _ctx("rehearsal_delta_on", tmp_path / "lead_run", m["lay"])
    assert ctx.delta_held is True
    ours = _ctx("rehearsal_delta_on", tmp_path / "ours", m["lay"])
    ids_sha = LR.ids_sha256(m["ids"])
    a = LR.search_unit(m["model"], m["prep"], ctx, "attack", "C1", 1, m["start"], ids_sha, m["fp"])
    b = R3.search_unit_frozen(m["model"], m["prep"], ours, "attack", "C1", 1, m["start"], ids_sha, m["fp"], 1.0)
    assert a["guards"] == b["guards"] == {"G4": True, "G5": True, "G7": True, "wrapper_equals_authors": True, "delta_entries_held": True}
    x, y = _arrays(tmp_path / "lead_run" / "search_C1_s1.npz"), _arrays(tmp_path / "ours" / "search_C1_s1.npz")
    assert set(x) == set(y)
    for k in x:
        if k != "meta":
            assert x[k].dtype == y[k].dtype and x[k].shape == y[k].shape and x[k].tobytes() == y[k].tobytes(), k
    mx, my = json.loads(str(x["meta"].reshape(-1)[0])), json.loads(str(y["meta"].reshape(-1)[0]))
    assert my.pop("delta_value") == 1.0 and mx == my


def test_at_zero_the_record_is_the_plain_loops_and_the_delta_entries_stay_at_zero(model, tmp_path):
    m = model
    ctx = R3.RerunContext(arm=R3.ARM_NAME["held_at_0"], units=tmp_path / "held_at_0", commit=COMMIT, lay=m["lay"], precision="fp32", device="cpu",
                          n_steps=R3.N_STEPS, mode="test")
    u = R3.search_unit_frozen(m["model"], m["prep"], ctx, "own", "QB1", 41, m["start"], LR.ids_sha256(m["ids"]), m["fp"], 0.0)
    assert u["guards"]["delta_entries_held"] is True
    z = _arrays(tmp_path / "held_at_0" / "search_QB1_s41.npz")
    plain = A.run(m["model"], m["prep"], m["start"], R3.N_STEPS, 0.1, frozen=A.Frozen.delta_entries(m["model"], 0.0, "cpu"), device="cpu")
    assert np.asarray(plain["record"], dtype=np.float64).tobytes() == z["record"].tobytes() and len(z["record"]) == 21
    dpos = LR.delta_positions(m["lay"])
    assert (z["settings"][:, dpos] == 0).all()
    names = [str(n) for n in z["hook_names"]]
    assert "step_20" in names and "step_19" in names and "step_40" not in names
    assert z["settings"][names.index("step_20")].tobytes() == np.concatenate([plain["sources"][k].reshape(-1) for k, _ in m["lay"]]).tobytes()
    # the start the record begins from: the signed start with its delta entries at 0
    first = R3.held_start(m["start"], m["lay"], 0.0)
    assert (first[dpos] == 0).all() and np.array_equal(np.delete(first, dpos), np.delete(LR.flat_start(m["start"], m["lay"], False), dpos))
    assert A.score_per_text(m["model"], LR.P.unflatten(first, m["lay"]), m["prep"], device="cpu")[0] == z["init"][0] == z["record"][0]
    meta = json.loads(str(z["meta"].reshape(-1)[0]))
    assert meta["delta_held"] is True and meta["delta_value"] == 0.0 and meta["start_sha256"] == LR.setting_sha256(LR.flat_start(m["start"], m["lay"], False))
    # the searched arm differs: its delta entries move
    ctx_s = R3.RerunContext(arm=R3.ARM_NAME["searched"], units=tmp_path / "searched", commit=COMMIT, lay=m["lay"], precision="fp32", device="cpu",
                            n_steps=R3.N_STEPS, mode="test")
    LR.search_unit(m["model"], m["prep"], ctx_s, "own", "QB1", 41, m["start"], LR.ids_sha256(m["ids"]), m["fp"])
    s = _arrays(tmp_path / "searched" / "search_QB1_s41.npz")
    assert not (s["settings"][:, dpos] == 0).all() and s["record"].tobytes() != z["record"].tobytes()


# ----------------------------------------------------------------------------- the specs and the inputs


def test_the_specs_twelve_containers_of_two_parts():
    specs = R3.specs(COMMIT, REFS)
    assert [s["batch"] for s in specs] == [f"QB{k}" for k in range(1, 9)] + ["H1", "H5", "H9", "H13"]
    for s in specs[:8]:
        assert s == {"part": "rerun", "arm": "rerun", "side": "own", "batch": s["batch"], "commit": COMMIT, "mode": "s6_rerun", "root": "/cache/s6_plan3",
                     "units": "rerun", "run": "s6_plan3"}
    for s in specs[8:]:
        assert s["part"] == "variants" and s["batches"] == [s["batch"]] and s["refs"] == {s["batch"]: REFS[s["batch"]]} and s["mode"] == SR.MODE
        assert tuple(s["attack_batches"]) == SR.ATTACK and tuple(s["starts"]) == SR.STARTS
    for spec in specs:
        R3.check_spec(spec)
        R3.check_spec({**spec, "launch": "ap-x|s6_plan3|1"})
    assert R3.STARTS == (41, 42, 43, 44, 45) and R3.N_STEPS == 20 and R3.HELD_VALUE == 0.0 and len(R3.expected_files()) == 80 + 4 * 81


@pytest.mark.parametrize("which,change", [(0, {"batch": "QB9"}), (0, {"batch": "C1"}), (0, {"mode": "s6"}), (0, {"units": "variants"}), (0, {"root": "/cache/s6"}),
                                          (0, {"commit": "abc"}), (0, {"part": "pin"}), (0, {"extra": 1}), (0, {"arm": "lead"}), (8, {"batch": "H2"}),
                                          (8, {"batches": ["H1", "H5"]}), (8, {"starts": [9, 10]}), (8, {"attack_batches": ["A1"]}), (8, {"mode": "s6_rerun"}),
                                          (8, {"refs": {"H1": {}, "H5": {}}}), (8, {"units": "rerun"})])
def test_a_spec_that_is_not_this_launchs_is_refused(which, change):
    with pytest.raises(LR.GuardFailure, match="configuration"):
        R3.check_spec({**R3.specs(COMMIT, REFS)[which], **change})


def test_a_rerun_container_is_handed_its_own_128_texts_of_pool_q_in_order():
    texts = [f"v{i}" for i in range(1024)]
    ids = np.arange(1024 * 4, dtype=np.int32).reshape(1024, 4)
    rows = [f"r{i}" for i in range(1024)]
    pools = {"Q": {"pool": "Q", "texts": texts}, "H1": {"pool": "H"}}
    got_ids, got_rows = R3.rerun_inputs(R3.specs(COMMIT, REFS)[2], load_ids=lambda name: (ids, texts, rows), pools=pools)
    assert got_rows == rows[256:384] and np.array_equal(got_ids, ids[256:384])
    with pytest.raises(LL.LaunchRefusal, match="order"):
        R3.rerun_inputs(R3.specs(COMMIT, REFS)[0], load_ids=lambda name: (ids, texts[::-1], rows), pools=pools)
    with pytest.raises(LL.LaunchRefusal):
        R3.rerun_inputs({**R3.specs(COMMIT, REFS)[0], "batch": "H1"}, load_ids=lambda name: (ids, texts, rows), pools=pools)
    with pytest.raises(LL.LaunchRefusal):
        R3.rerun_inputs(R3.specs(COMMIT, REFS)[0], load_ids=lambda name: (ids, texts, rows), pools={"Q": {"pool": "Q", "texts": texts[:512]}})
    asked = []
    out = R3.variants_inputs(R3.specs(COMMIT, REFS)[9], load_ids=lambda name: asked.append(name) or (ids[:2], ["t0", "t1"], ["a", "b"]),
                             pools={"H5": {"pool": "H"}})
    assert asked == ["H5"] and list(out) == ["H5"] and out["H5"][1] == ["a", "b"]
    with pytest.raises(LL.LaunchRefusal):
        R3.variants_inputs({**R3.specs(COMMIT, REFS)[9], "batch": "H5"}, load_ids=lambda name: (ids, [], []), pools={"H5": {"pool": "A"}})


def test_q_in_the_manifest_is_1024_texts_and_the_starts_are_the_signed_ones():
    man = LL._manifest()
    assert man["pools"]["Q"]["pool"] == "Q" and man["pools"]["Q"]["texts"] == [f"v{i}" for i in range(1024)]
    meta = json.load(open(R3.STARTS_JSON))
    for s, st in R3.load_starts().items():
        assert LR.setting_sha256(LR.flat_start(st, LR.P.layout(), False)) == meta["starts"][str(s)]["sha256"]
        assert meta["starts"][str(s)]["seed_key"] == [20261001, "start", s]


def test_the_rerun_configuration_is_asserted_in_every_container(tmp_path):
    def contexts(**kw):
        spec = R3.specs(COMMIT, REFS)[0]
        return R3.rerun_contexts(spec, [], environment=dict(GOOD_ENV), log=lambda **f: None, commit_volume=lambda: None, should_stop=lambda: False,
                                 t0=0.0, device="cuda", precision="bf16", **kw)

    for arm, ctx in contexts().items():
        R3.check_configuration(ctx, arm, R3.STARTS)
        assert ctx.settings == LT.SETTINGS_LEAD and ctx.delta_held is False and ctx.units == Path("/cache/s6_plan3/rerun") / arm
    c = contexts()
    assert c["searched"].timings is c["held_at_0"].timings  # one container's timings
    for starts in ((41, 42, 43, 44), (9, 10, 11, 12, 13), (41, 42, 43, 44, 45, 46)):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            R3.check_configuration(c["searched"], "searched", starts)
    with pytest.raises(LR.GuardFailure, match="configuration"):
        R3.check_configuration(c["searched"], "held_at_0", R3.STARTS)
    for change in ({"gpu": "NVIDIA A100-80GB"}, {"deterministic_algorithms": False}, {"allow_tf32_matmul": True}, {"vpd_audit_2_dirty": "1"},
                   {"vpd_audit_2_commit": "0" * 40}):
        ctx = contexts()["searched"]
        ctx.environment = {**GOOD_ENV, **change}
        with pytest.raises(LR.GuardFailure, match="configuration"):
            R3.check_configuration(ctx, "searched", R3.STARTS)
    for kw in ({"mode": "deciding"}, {"mode": "s6"}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            R3.check_configuration(contexts(**kw)["searched"], "searched", R3.STARTS)


# ----------------------------------------------------------------------------- the projection


def test_the_projection_from_the_committed_records():
    p = R3.projection(LISTED)
    r, v = p["rerun"], p["variants"]
    assert r["containers"] == 8 and r["searches"] == 80 and v["containers"] == 4 and v["passes"] == 4 * (401 + 802) == 4812
    st = [c["timings"] for c in json.load(open(R3.STARTS_TEST_RECORD))["containers"]]

    def rate(key):
        return np.mean([t[key] / t[key + "_count"] for t in st])

    per = (rate("search_iteration_0") + 9 * rate("search_iterations_warm") + 10 * rate("search_iterations_after_warm") + rate("search_final_harm")
           + 10 * rate("scoring") + rate("volume_commit_after_search"))
    assert r["seconds_per_search"] == pytest.approx(per) and r["function_seconds"] == pytest.approx(8 * (np.mean([t["to_ready"] for t in st]) + 10 * per))
    assert 9.0 < per < 16.0  # 20 steps at about 0.38 seconds, and the re-scores
    sec = 4 * (v["seconds_to_ready"] + 401 * v["seconds_per_flat_pass"] + 802 * v["seconds_per_split_pass"] + 9 * v["seconds_per_volume_commit"])
    assert v["function_seconds"] == pytest.approx(sec) and 0.18 < v["seconds_per_flat_pass"] < 0.2 and 0.19 < v["seconds_per_split_pass"] < 0.21
    assert p["total"]["dollars"] == pytest.approx(max((r["function_seconds"] + v["function_seconds"]) / 3600 * 6.80,
                                                      (r["function_seconds"] + v["function_seconds"] + 12 * 50) / 3600 * LISTED))
    assert p["exceeds_cap"] is False and r["dollars"] < R3.RERUN_CAP and 3.0 < p["projected_dollars"] < 8.0


def test_over_either_cap_nothing_launches(tmp_path, monkeypatch):
    record = json.load(open(R3.STARTS_TEST_RECORD))
    for c in record["containers"]:
        for k in ("search_iterations_after_warm", "search_iterations_warm"):
            c["timings"][k] *= 4  # the rerun alone over $6
    (tmp_path / "starts.json").write_text(json.dumps(record))
    monkeypatch.setattr(R3, "STARTS_TEST_RECORD", tmp_path / "starts.json")
    monkeypatch.setattr(R3, "RESULTS", tmp_path / "s6_plan3")
    monkeypatch.setattr(R3, "check_launch_commit", lambda commit: None)
    spawned = []
    cloud = LL.Cloud(spawn=spawned.append, set_stop=lambda v: None, attempts=lambda s: 0, read_bill=lambda apps: {}, guards=lambda s: {}, app_id="ap-x",
                     log=lambda **f: None)
    with pytest.raises(LL.LaunchRefusal, match="C0"):
        R3.launch_command(COMMIT, cloud, listed_hourly_price=LISTED, refs=REFS)
    assert spawned == []
    c0 = json.load(open(tmp_path / "s6_plan3" / "ledger.json"))["checks"][0]
    assert c0["exceeds_cap"] is True and c0["rerun"]["dollars"] > 6.0 and c0["total"]["dollars"] < R3.CAP_DOLLARS


# ----------------------------------------------------------------------------- the checks before the launch, in a small repository


def _git(top: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(top), "-c", "user.name=t", "-c", "user.email=t@t", *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_the_launch_is_refused_unless_every_condition_holds(tmp_path, monkeypatch):
    top = tmp_path / "top"
    root = top / "vpd-audit-2"
    for rel in LL.RUN_FILES:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(f"# {rel}\n")
    _git(tmp_path, "init", "-q", str(top))
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "the run")
    run_commit = _git(top, "rev-parse", "HEAD")
    for rel in R3.READING_FILES:
        (root / rel).write_text(f"# {rel}\n")
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "the readings and the drivers")
    head = _git(top, "rev-parse", "HEAD")
    monkeypatch.setattr(LL, "REPO_ROOT", root)
    monkeypatch.setattr(R3, "RESULTS", root / "results" / "s6_plan3")
    monkeypatch.setattr(SR, "RUN_COMMIT", run_commit)
    R3.check_launch_commit(head)
    (root / "results" / "s6_plan3").mkdir(parents=True)
    (root / "results" / "s6_plan3" / "ledger.json").write_text("{}")
    R3.check_launch_commit(head)
    (root / "results" / "other.json").write_text("{}")
    with pytest.raises(LL.LaunchRefusal, match="not clean"):
        R3.check_launch_commit(head)
    (root / "results" / "other.json").unlink()
    with pytest.raises(LL.LaunchRefusal, match="not the one named"):
        R3.check_launch_commit(run_commit)
    (root / "vpd_audit_2" / "adversary.py").write_text("# the search path, changed\n")
    _git(top, "add", "vpd-audit-2/vpd_audit_2/adversary.py")
    _git(top, "commit", "-q", "-m", "a change to the search path")
    with pytest.raises(LL.LaunchRefusal, match="search path has changed.*adversary.py"):
        R3.check_launch_commit(_git(top, "rev-parse", "HEAD"))
    _git(top, "checkout", "-q", run_commit)
    with pytest.raises(LL.LaunchRefusal, match="not committed: vpd_audit_2/s6_plan3_run.py"):
        R3.check_launch_commit(run_commit)


# ----------------------------------------------------------------------------- the whole launch on the tiny model


ATT, RUN_STARTS = ("A1", "A2"), (9, 10)


class TinyCloud:
    """The cloud for the tiny model on a CPU: a folder for the volume, and containers that run the driver's job when
    asked for their result. Two rerun batches and one S4 batch, two attack batches and two run starts."""

    def __init__(self, volume: Path) -> None:
        torch.use_deterministic_algorithms(True)
        self.volume = volume
        self.model = tiny_component_model()
        self.lay = [(k, int(self.model.module_to_c[k])) for k in self.model.target_module_paths]
        self.n = sum(c + 1 for _, c in self.lay)
        g = torch.Generator().manual_seed(17)
        self.rerun_starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in self.lay} for s in R3.STARTS}
        self.ids = {b: tiny_ids(N_TEXTS, seed=40 + j).numpy() for j, b in enumerate(["QB1", "QB2", "H1"])}
        self.rows = {b: LR.sha_rows(x) for b, x in self.ids.items()}
        rng = np.random.default_rng(8)
        self.flat_starts = {s: rng.random(self.n).astype(np.float32) for s in RUN_STARTS}
        self.strata = {k: rng.integers(0, 11, c) for k, c in self.lay}  # the unit loop builds plan 2 of the research log's cells; the variants do not use them
        self.units = {}
        for a in ATT:
            for s in RUN_STARTS:
                settings = []
                for _ in B.SPLIT_ROWS:
                    u, v = rng.random(self.n), rng.random(self.n)
                    settings.append(np.where(u < 0.3, 0.0, np.where(u > 0.7, 1.0, v)).astype(np.float32))
                self.units[(a, s)] = {"hook_names": np.array([LR.SAVED[r] for r in B.SPLIT_ROWS]), "settings": np.stack(settings),
                                      "cum_signed": np.zeros((len(B.SPLIT_ROWS), self.n), dtype=np.float32)}
        self.prep_h = A.prepare(self.model, self.ids["H1"], "fp32", device="cpu")
        score = lambda flat: SR.score_flat(self.model, flat, self.prep_h, self.lay, "cpu")[0]  # noqa: E731
        self.refs = {"H1": {"prep_fp": LR.prep_fingerprint(self.prep_h), "own_attack": "A1", "check_attack": "A1",
                            "check_carried": score(B.saved(self.units[("A1", 9)], "n320")[0]), "check_start": score(self.flat_starts[9])}}
        self.lines: list = []
        self.control: dict = {}

    def starts_json(self) -> dict:
        return {"starts": {str(s): {"sha256": LR.setting_sha256(LR.flat_start(st, self.lay, False)), "seed_key": [20261001, "start", s]}
                           for s, st in self.rerun_starts.items()}}

    def run(self, spec: dict) -> dict:
        R3.check_spec(spec)
        b = spec["batch"]
        log = lambda **f: self.lines.append(LR.log_record(**f))  # noqa: E731
        stop = lambda: bool(self.control.get("stop"))  # noqa: E731
        if spec["part"] == R3.RERUN:
            out = R3.run_rerun_spec(self.model, spec, self.ids[b], self.rows[b], self.rerun_starts, self.lay, environment={"task": b}, log=log,
                                    commit_volume=lambda: None, should_stop=stop, device="cpu", precision="fp32", mode="test")
        else:
            ctx = SR.Context(commit=spec["commit"], units=Path(spec["root"]) / spec["units"], lay=self.lay, device="cpu", precision="fp32", mode="test", log=log,
                             should_stop=stop)
            inputs = SR.Inputs(starts=self.flat_starts, strata=self.strata, read_run_unit=lambda a, s: self.units[(a, s)], b2=None)
            out = R3.variants_job(self.model, ctx, spec, {b: (self.ids[b], self.rows[b])}, inputs)
        out["attempts"] = 1
        return out

    def cloud(self) -> LL.Cloud:
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec

            def get(self, timeout: float) -> dict:
                return me.run(self.spec)

        return LL.Cloud(spawn=Now, set_stop=lambda value: self.control.__setitem__("stop", bool(value)), attempts=lambda spec: 1,
                        read_bill=lambda apps: {"read_at": "2026-10-07T18:00:00+00:00", "by_app": {}}, guards=lambda spec: {"outcomes": {}, "seconds": 0.0},
                        app_id="ap-tiny", log=lambda **f: self.lines.append(LR.log_record(**f)))


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("plan3")
    tc = TinyCloud(tmp / "volume")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(R3, "RESULTS", tmp / "results" / "s6_plan3")
        mp.setattr(R3, "VOLUME", str(tmp / "volume"))
        mp.setattr(R3, "LOCAL", tmp / "local")
        mp.setattr(R3, "BATCHES", ("QB1", "QB2"))
        mp.setattr(R3, "VARIANT_BATCHES", ("H1",))
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        mp.setattr(R3, "check_launch_commit", lambda commit: None)
        mp.setattr(R3, "tree_holds_only_this_plans_records", lambda: True)
        mp.setattr(LL, "head_commit", lambda: COMMIT)
        mp.setattr(R3, "projection", lambda price: {"check": "C0", "projected_dollars": 0.0, "exceeds_cap": False})
        summary = R3.launch_command(COMMIT, tc.cloud(), listed_hourly_price=LISTED, refs=tc.refs)
        files = R3.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes(), log=lambda **f: tc.lines.append(LR.log_record(**f)))
        (tmp / "starts.json").write_text(json.dumps(tc.starts_json()))
        cells = RR.load(starts_json=tmp / "starts.json")
        expected = R3.expected_files()
        variant_names = [n for n, _, _ in B.variant_units("H1", list(ATT), list(RUN_STARTS))]
    return {"tmp": tmp, "tc": tc, "summary": summary, "files": files, "cells": cells, "expected": expected, "variant_names": variant_names,
            "results": tmp / "results" / "s6_plan3"}


def test_the_whole_launch_runs_through_its_commands(tiny):
    s = tiny["summary"]
    assert s["complete"] is True and s["containers"] == 3 and s["all_guards_true"] is True
    assert s["finished_units"] == s["expected_units"] == 2 * 10 + 1 + len(ATT) * len(RUN_STARTS)
    run = json.load(open(tiny["results"] / "runs_s6_plan3.json"))
    units = {u["unit"]: u for c in run["containers"] for u in c["units"]}
    for b in ("QB1", "QB2"):
        for st in R3.STARTS:
            assert units[f"search|rerun_searched|{b}|s{st}"]["guards"] == {"G4": True, "G5": True, "G7": True, "wrapper_equals_authors": True}
            assert units[f"search|rerun_held_at_0|{b}|s{st}"]["guards"] == {"G4": True, "G5": True, "G7": True, "wrapper_equals_authors": True,
                                                                               "delta_entries_held": True}
    assert units["variants_check_H1"]["guards"] == {"split_path_s_everywhere": True, "split_path_s0_everywhere": True, "flat_path_bits_equal": True}
    ledger = json.load(open(tiny["results"] / "ledger.json"))
    assert [c["check"] for c in ledger["checks"]] == ["C0", "C1"] and ledger["stages"]["s6_plan3"]["complete"] is True
    backup = json.load(open(tiny["results"] / "backup.json"))
    assert set(backup["files"]) == set(tiny["expected"].values()) and len(backup["files"]) == 20 + 1 + 4
    assert all(LT.sha256_file(tiny["tmp"] / "local" / rel) == sha for rel, sha in backup["files"].items())


def test_every_rerun_unit_is_its_search_of_twenty_steps_on_its_own_batch(tiny):
    for arm in R3.ARMS:
        for b in ("QB1", "QB2"):
            for st in R3.STARTS:
                z = _arrays(tiny["tmp"] / "local" / "rerun" / arm / f"search_{b}_s{st}.npz")
                meta = json.loads(str(z["meta"].reshape(-1)[0]))
                assert meta["batch"] == b and meta["start"] == st and meta["n_steps"] == 20 and meta["side"] == "own" and meta["arm"] == R3.ARM_NAME[arm]
                assert meta["ids_sha"] == LR.ids_sha256(tiny["tc"].ids[b]) and len(z["record"]) == 21 and z["own_text"].shape[1] == N_TEXTS
                scored = [str(x) for x in z["scored_names"]]
                assert scored[0] == "n20" and z["own"][0] == z["record"][20]
                assert (z["settings"][:, LR.delta_positions(tiny["tc"].lay)] == 0).all() == (arm == "held_at_0")


def test_the_variants_units_hold_the_three_variants_of_every_setting(tiny):
    tc = tiny["tc"]
    for name in tiny["variant_names"][1:]:
        z = _arrays(tiny["tmp"] / "local" / "variants" / f"{name}.npz")
        ids = [str(x) for x in z["pass_ids"]]
        assert ids == [f"{v}|{row}" for row in B.SPLIT_ROWS for v in B.VARIANTS] and z["per_text"].shape == (15, N_TEXTS)
    # one pass of each kind, rebuilt and rescored independently
    z = _arrays(tiny["tmp"] / "local" / "variants" / "variants_H1_A2_s10.npz")
    ids = [str(x) for x in z["pass_ids"]]
    s = B.saved(tc.units[("A2", 10)], "n80")[0]
    v1 = SR.score_flat(tc.model, B.zeros_alone(s), tc.prep_h, tc.lay, "cpu")[0]
    assert z["harm"][ids.index("V1|n80")] == v1
    zero = SR.zero_masks(tc.prep_h)
    for v in ("V2", "V3"):
        h = SR.score_sources(tc.model, SR.split_sources(zero, *B.variant_split_args(s)[v], tc.lay, "cpu"), tc.prep_h)[0]
        assert z["harm"][ids.index(f"{v}|n80")] == h


def test_the_rerun_reading_reads_what_was_copied(tiny):
    cells = tiny["cells"]
    assert set(cells) == {"searched", "held_at_0"}
    for arm, Y in cells.items():
        assert Y.shape == (2, 5) and np.isfinite(Y).all()
        for i, b in enumerate(("QB1", "QB2")):
            for k, st in enumerate(R3.STARTS):
                z = _arrays(tiny["tmp"] / "local" / "rerun" / arm / f"search_{b}_s{st}.npz")
                assert Y[i, k] == z["record"][20]


def test_the_copy_refuses_bytes_that_are_not_the_ones_returned(tiny, tmp_path):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(R3, "RESULTS", tiny["results"])
        mp.setattr(R3, "VOLUME", str(tiny["tmp"] / "volume"))
        mp.setattr(R3, "BATCHES", ("QB1", "QB2"))
        mp.setattr(R3, "VARIANT_BATCHES", ("H1",))
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        mp.setattr(R3, "tree_holds_only_this_plans_records", lambda: True)
        mp.setattr(LL, "head_commit", lambda: COMMIT)
        backup = (tiny["results"] / "backup.json").read_text()

        def read(remote: str) -> bytes:
            data = Path(remote).read_bytes()
            return data + b"x" if remote.endswith("held_at_0/search_QB2_s43.npz") else data

        with pytest.raises(LL.LaunchRefusal, match="held_at_0/search_QB2_s43.npz"):
            R3.collect_command(COMMIT, read_file=read, log=lambda **f: None, dest=tmp_path / "u")
        assert (tiny["results"] / "backup.json").read_text() == backup
        mp.setattr(LL, "head_commit", lambda: "e" * 40)
        with pytest.raises(LL.LaunchRefusal, match="commit"):
            R3.collect_command(COMMIT, read_file=read, log=lambda **f: None, dest=tmp_path / "u2")


def test_a_finished_launch_is_not_launched_again(tiny):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(R3, "RESULTS", tiny["results"])
        mp.setattr(R3, "check_launch_commit", lambda commit: None)
        with pytest.raises(LL.LaunchRefusal, match="already complete"):
            R3.launch_command(COMMIT, tiny["tc"].cloud(), listed_hourly_price=LISTED, refs=REFS)


def test_nothing_in_the_driver_prints():
    import re

    for module in ("s6_plan3_run", "modal_s6_plan3"):
        text = Path(R3.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module


def test_a_variants_container_whose_check_fails_stops_before_any_variant(tiny, tmp_path):
    tc = tiny["tc"]
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "ATTACK", ATT)
        mp.setattr(SR, "STARTS", RUN_STARTS)
        mp.setattr(R3, "VARIANT_BATCHES", ("H1",))
        for key, factor in (("check_carried", 1.0 + 1e-12), ("check_start", 1.001)):
            refs = {"H1": dict(tc.refs["H1"])}
            refs["H1"][key] = refs["H1"][key] * factor
            spec = [s for s in R3.specs(COMMIT, refs) if s["part"] == R3.VARIANTS][0]
            ctx = SR.Context(commit=COMMIT, units=tmp_path / key, lay=tc.lay, device="cpu", precision="fp32", mode="test")
            inputs = SR.Inputs(starts=tc.flat_starts, strata=tc.strata, read_run_unit=lambda a, s: tc.units[(a, s)], b2=None)
            with pytest.raises(SR.S6Failure, match="a path does not give the saved harm"):
                R3.variants_job(tc.model, ctx, spec, {"H1": (tc.ids["H1"], tc.rows["H1"])}, inputs)
            assert not list((tmp_path / key).glob("variants_H1_*.npz"))
