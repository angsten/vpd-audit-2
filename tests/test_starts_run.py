"""Session 6, plan 1, Section 2.3: the starts test's driver, without the cloud.

The specs, the checks a container makes, and that `lead_run`'s own refusals still hold against this test; the checks
before the launch, in a small repository; the cost projection; and the whole test on the tiny model through the same
commands the cloud module calls: eight containers, 41 searches, the copy, the guard against a plain-loop search, and the
records the reading script reads.
"""

from __future__ import annotations

import hashlib
import json
import shutil
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
from vpd_audit_2 import pilot as P
from vpd_audit_2 import starts_run as SR
from vpd_audit_2 import starts_test as ST

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504
COMMIT = "e" * 40
N_TEXTS = 16
GOOD_ENV = {"gpu": "NVIDIA B200", "deterministic_algorithms": True, "deterministic_warn_only": False, "allow_tf32_matmul": False, "allow_tf32_cudnn": False,
            "cublas_workspace_config": ":4096:8", "vpd_audit_2_commit": COMMIT, "vpd_audit_2_dirty": "0"}


# ----------------------------------------------------------------------------- the specs and a container's checks


def test_the_specs_one_container_per_calibration_batch():
    specs = SR.specs(COMMIT)
    assert [s["batch"] for s in specs] == [f"C{j}" for j in range(1, 9)]
    assert all(s == {"arm": "starts_test", "side": "own", "batch": s["batch"], "commit": COMMIT, "mode": "starts_test", "root": "/cache/s6_starts",
                     "units": "units", "run": "starts_test"} for s in specs)
    assert SR.starts_of("C1") == (1, 9, 10, 11, 12, 13) and all(SR.starts_of(f"C{j}") == (9, 10, 11, 12, 13) for j in range(2, 9))
    assert SR.n_searches() == 41 and SR.STAGE.containers == 8
    for spec in specs:
        SR.check_spec(spec)
        SR.check_spec({**spec, "launch": "ap-x|starts_test|1"})


@pytest.mark.parametrize("change", [{"arm": "lead"}, {"arm": "rehearsal"}, {"mode": "deciding"}, {"mode": "rehearsal"}, {"batch": "A1"}, {"batch": "H1"},
                                    {"batch": "C9"}, {"side": "attack"}, {"root": "/cache/s5_lead/lead"}, {"units": "sealed/units"}, {"allow_pool": "C1"},
                                    {"n_steps": 20}, {"commit": "abc"}])
def test_a_spec_that_is_not_this_tests_is_refused(change):
    with pytest.raises(LR.GuardFailure, match="configuration"):
        SR.check_spec({**SR.specs(COMMIT)[0], **change})


def test_a_container_is_handed_one_calibration_batch_and_no_other():
    pools = {"C1": {"pool": "C"}, "C2": {"pool": "C"}, "A1": {"pool": "A"}, "H1": {"pool": "H"}}
    asked = []

    def load(batch):
        asked.append(batch)
        return np.zeros((2, 4), dtype=np.int32), ["t0", "t1"], ["r0", "r1"]

    ids, rows = SR.container_inputs(SR.specs(COMMIT)[1], load_ids=load, pools=pools)
    assert asked == ["C2"] and rows == ["r0", "r1"] and ids.shape == (2, 4)
    for spec in ({**SR.specs(COMMIT)[0], "batch": "A1"}, {**SR.specs(COMMIT)[0], "batch": "H1"}, {**SR.specs(COMMIT)[0], "mode": "deciding"},
                 {**SR.specs(COMMIT)[0], "arm": "lead"}):
        with pytest.raises(LL.LaunchRefusal):
            SR.container_inputs(spec, load_ids=load, pools=pools)
    assert asked == ["C2"]


def _ctx(**kw) -> SR.Context:
    args = {"arm": "starts_test", "units": Path("/nonexistent"), "commit": COMMIT, "lay": [], "precision": "bf16", "device": "cuda", "mode": "starts_test",
            "environment": dict(GOOD_ENV), **kw}
    return SR.Context(**args)


def test_the_configuration_is_asserted_in_every_container():
    SR.check_configuration(_ctx(), "C1", (1, 9, 10, 11, 12, 13))
    SR.check_configuration(_ctx(), "C5", (9, 10, 11, 12, 13))
    assert _ctx().settings == LT.SETTINGS_LEAD and _ctx().delta_held is False  # the lead arm's settings, the delta components searched
    for batch, starts in (("C2", (1, 9, 10, 11, 12, 13)), ("C1", (9, 10, 11, 12, 13)), ("C3", (9, 10, 11, 12)), ("C3", (9, 10, 11, 12, 13, 14)),
                          ("C3", (1,)), ("C3", (2, 9, 10, 11, 12, 13))):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            SR.check_configuration(_ctx(), batch, starts)
    for change in ({"gpu": "NVIDIA A100-80GB"}, {"deterministic_algorithms": False}, {"deterministic_warn_only": True}, {"allow_tf32_matmul": True},
                   {"allow_tf32_cudnn": True}, {"cublas_workspace_config": None}, {"vpd_audit_2_dirty": "1"}, {"vpd_audit_2_commit": "0" * 40}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            SR.check_configuration(_ctx(environment={**GOOD_ENV, **change}), "C2", (9, 10, 11, 12, 13))
    for kw in ({"arm": "lead"}, {"n_steps": 20}, {"precision": "fp32"}, {"device": "cpu"}, {"mode": "deciding"}, {"mode": "rehearsal"},
               {"fault": lambda point: None}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            SR.check_configuration(_ctx(**kw), "C2", (9, 10, 11, 12, 13))


def test_lead_run_still_refuses_this_test_and_its_deciding_refusals_are_unchanged():
    """The driver goes round `lead_run`'s gates, not through them: they refuse this test's starts and mode as before."""
    assert LR.STARTS == (9, 10, 11, 12, 13) and LR.REHEARSAL_STARTS == (1,) and "starts_test" not in LR.ARMS
    deciding = LR.Context(arm="lead", units=Path("/nonexistent"), commit=COMMIT, lay=[], mode="deciding", environment=dict(GOOD_ENV))
    LR.check_configuration(deciding, (9, 10, 11, 12, 13))
    for starts in ((1, 9, 10, 11, 12, 13), (1,), (9, 10, 11, 12)):
        with pytest.raises(LR.GuardFailure):
            LR.check_configuration(deciding, starts)
    for mode in ("starts_test", "deciding", "rehearsal"):
        ours = SR.Context(arm="starts_test", units=Path("/nonexistent"), commit=COMMIT, lay=[], mode=mode, environment=dict(GOOD_ENV))
        with pytest.raises(LR.GuardFailure):
            LR.check_configuration(ours, (9, 10, 11, 12, 13))
    with pytest.raises(LR.GuardFailure):
        LR.check_spec(SR.specs(COMMIT)[0], False)
    with pytest.raises(LR.GuardFailure):  # nor does a C batch pass lead_run's own batch guard outside a rehearsal
        LR.guard_batch(deciding, "attack", "C1", np.zeros((1, 2), dtype=np.int32), LR.sha_rows(np.zeros((1, 2), dtype=np.int32)))


def test_the_start_hash_in_a_unit_is_the_signed_files_own():
    """`build_records` checks each unit's `start_sha256` against the starts file's json; they are one hash of one layout."""
    meta = json.load(open(SR.STARTS_JSON))
    lay = P.layout()
    for s in (1, 9, 13):
        assert LR.setting_sha256(LR.flat_start(P.load_extended_start(s), lay, False)) == meta["starts"][str(s)]["sha256"]


# ----------------------------------------------------------------------------- the projection


def test_the_projection_from_the_committed_records():
    p = SR.projection(LISTED)
    assert p["searches"] == 41 and p["containers"] == 8 and p["cap"] == 20.0 and p["exceeds_cap"] is False
    assert p["from_the_pilot_dollars"] == pytest.approx(41 * 19.20 / 64)
    # by hand from the committed inputs: 16 attack containers at 663.89 s, ready 20.37 s, a scoring pass 0.184 s
    i = p["inputs"]
    assert i["run_attack_containers"] == 16 and i["searches_per_run_attack_container"] == 5 and i["wrapper_passes_per_search"] == 11
    per_search = (i["run_attack_container_seconds_mean"] - i["rehearsal_seconds_to_ready"]) / 5
    total = 8 * i["rehearsal_seconds_to_ready"] + 41 * (per_search + 11 * i["rehearsal_seconds_per_scoring_pass"])
    assert p["from_the_run_at_the_mean"]["function_seconds"] == pytest.approx(total) and total == pytest.approx(5522.85, abs=0.01)
    assert p["from_the_run_at_the_mean"]["dollars"] == pytest.approx(max(total / 3600 * 6.80, (total + 8 * 50) / 3600 * LISTED))
    assert p["projected_dollars"] == max(p["from_the_run_at_the_mean"]["dollars"], p["from_the_run_at_the_largest"]["dollars"], p["from_the_pilot_dollars"])
    assert 10.0 < p["projected_dollars"] < 13.0


def test_a_projection_over_twenty_dollars_launches_nothing(tmp_path, monkeypatch):
    ledger = json.load(open(SR.RUN_LEDGER))
    for launch in ledger["stages"]["lead_attack"]["launches"]:
        for c in launch["calls"].values():
            c["returned_seconds"] = float(c["returned_seconds"]) * 3
    (tmp_path / "ledger.json").write_text(json.dumps(ledger))
    monkeypatch.setattr(SR, "RUN_LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(SR, "RESULTS", tmp_path / "s6_starts")
    monkeypatch.setattr(SR, "check_launch_commit", lambda commit: None)
    spawned = []
    cloud = LL.Cloud(spawn=spawned.append, set_stop=lambda v: None, attempts=lambda s: 0, read_bill=lambda apps: {}, guards=lambda s: {}, app_id="ap-x",
                     log=lambda **f: None)
    with pytest.raises(LL.LaunchRefusal, match="C0"):
        SR.launch_command(COMMIT, cloud, listed_hourly_price=LISTED)
    assert spawned == []
    c0 = json.load(open(tmp_path / "s6_starts" / "ledger.json"))["checks"][0]
    assert c0["check"] == "C0" and c0["exceeds_cap"] is True and c0["projected_dollars"] > 20.0


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
    for rel in SR.READING_FILES:
        (root / rel).write_text(f"# {rel}\n")
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "the reading and the driver")
    head = _git(top, "rev-parse", "HEAD")
    monkeypatch.setattr(LL, "REPO_ROOT", root)
    monkeypatch.setattr(SR, "RESULTS", root / "results" / "s6_starts")
    monkeypatch.setattr(SR, "RUN_COMMIT", run_commit)

    SR.check_launch_commit(head)
    with pytest.raises(LL.LaunchRefusal, match="not the one named"):
        SR.check_launch_commit(run_commit)
    (root / "results" / "s6_starts").mkdir(parents=True)
    (root / "results" / "s6_starts" / "ledger.json").write_text("{}")  # the test's own records may be there
    SR.check_launch_commit(head)
    (root / "results" / "other.json").write_text("{}")
    with pytest.raises(LL.LaunchRefusal, match="not clean"):
        SR.check_launch_commit(head)
    (root / "results" / "other.json").unlink()
    (root / "vpd_audit_2" / "starts_test.py").write_text("# changed and not committed\n")
    with pytest.raises(LL.LaunchRefusal, match="not clean"):
        SR.check_launch_commit(head)
    _git(top, "checkout", "-q", "--", ".")
    (root / "vpd_audit_2" / "lead_run.py").write_text("# the search path, changed\n")
    _git(top, "add", "vpd-audit-2/vpd_audit_2/lead_run.py")
    _git(top, "commit", "-q", "-m", "a change to the search path")
    with pytest.raises(LL.LaunchRefusal, match="search path has changed.*lead_run.py"):
        SR.check_launch_commit(_git(top, "rev-parse", "HEAD"))
    _git(top, "checkout", "-q", run_commit)  # a commit without the reading script
    with pytest.raises(LL.LaunchRefusal, match="not committed: vpd_audit_2/starts_test.py"):
        SR.check_launch_commit(run_commit)


# ----------------------------------------------------------------------------- the whole test on the tiny model


class TinyCloud:
    """The cloud, for the tiny model on a CPU: a folder for the volume, a dictionary for the control dictionary, and
    containers that run `starts_run.run_spec` when asked for their result."""

    def __init__(self) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, self.model.module_to_c[k]) for k in self.model.target_module_paths]
        g = torch.Generator().manual_seed(17)
        self.starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in self.lay} for s in (1,) + SR.TEST_STARTS}
        self.ids = {b: tiny_ids(N_TEXTS, seed=20 + j).numpy() for j, b in enumerate(SR.BATCHES, start=1)}
        self.rows = {b: LR.sha_rows(x) for b, x in self.ids.items()}
        self.control, self.lines, self.environments = {}, [], []

    def starts_meta(self) -> dict:
        return {"starts": {str(s): {"seed_key": [20261001, "start", s], "sha256": hashlib.sha256(b"".join(st[k].tobytes() for k, _ in self.lay)).hexdigest()}
                           for s, st in self.starts.items()}}

    def plain(self, batch: str, start: int) -> dict:
        """The same search by the plain loop and the plain hook, as the pilot ran it."""
        hook = A.SaveHook(steps=P.BUDGETS, thresholds=P.STAGES)
        r = A.run(self.model, A.prepare(self.model, self.ids[batch], "fp32", device="cpu"), self.starts[start], 320, 0.1, save_hook=hook, device="cpu")
        return {"record": r["record"], "saved_sources_sha256": {n: LR.setting_sha256(v) for n, v in hook.saved.items()}, "hook_events": dict(hook.events)}

    def run(self, spec: dict) -> dict:
        SR.check_spec(spec)
        b = spec["batch"]
        out = SR.run_spec(self.model, spec, self.ids[b], self.rows[b], SR.starts_for_batch(self.starts, b), self.lay, environment={"task": b},
                          log=lambda **f: self.lines.append(LR.log_record(**f)), commit_volume=lambda: None,
                          should_stop=lambda: bool(self.control.get("stop|starts_test")), device="cpu", precision="fp32")
        out["attempts"] = 1
        return out

    def cloud(self) -> LL.Cloud:
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec

            def get(self, timeout: float) -> dict:
                return me.run(self.spec)

        return LL.Cloud(spawn=Now, set_stop=lambda value: self.control.__setitem__("stop|starts_test", bool(value)), attempts=lambda spec: 1,
                        read_bill=lambda apps: {"read_at": "2026-10-07T18:00:00+00:00", "by_app": {}}, guards=lambda spec: {"outcomes": {}, "seconds": 0.0},
                        app_id="ap-tiny", log=lambda **f: self.lines.append(LR.log_record(**f)))


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("starts")
    tc = TinyCloud()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "RESULTS", tmp / "results" / "s6_starts")
        mp.setattr(SR, "VOLUME", str(tmp / "volume"))
        mp.setattr(SR, "LOCAL_UNITS", tmp / "local_units")
        mp.setattr(SR, "check_launch_commit", lambda commit: None)  # the repository's checks have their own test
        mp.setattr(SR, "check_environment", lambda ctx: None)  # nor is there a B200
        mp.setattr(SR, "tree_holds_only_this_tests_records", lambda: True)
        mp.setattr(LL, "head_commit", lambda: COMMIT)
        (tmp / "starts.json").write_text(json.dumps(tc.starts_meta()))
        mp.setattr(SR, "STARTS_JSON", tmp / "starts.json")
        summary = SR.launch_command(COMMIT, tc.cloud(), listed_hourly_price=LISTED)
        guard_pilot = tc.plain("C1", 1)
        records = SR.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes(), log=lambda **f: tc.lines.append(LR.log_record(**f)),
                                     pilot=guard_pilot)
    # the patches end here; a test that needs one sets its own
    return {"tmp": tmp, "tc": tc, "summary": summary, "records": records, "guard_pilot": guard_pilot, "results": tmp / "results" / "s6_starts"}


def test_the_whole_test_runs_through_its_commands(tiny):
    res = tiny["results"]
    s = tiny["summary"]
    assert s["complete"] is True and s["containers"] == 8 and s["finished_units"] == s["expected_units"] == 41 and s["all_guards_true"] is True
    run = json.load(open(res / "runs_starts_test.json"))
    units = [u for c in run["containers"] for u in c["units"]]
    assert sorted(u["unit"] for u in units) == sorted(SR.unit_id(b, st) for b in SR.BATCHES for st in SR.starts_of(b))
    assert all(u["guards"] == {"G4": True, "G5": True, "G7": True, "wrapper_equals_authors": True} and u["skipped"] is False for u in units)
    assert all("timings" in c and c["timings"]["search_count"] == 320 * len(SR.starts_of(c["container"].split("|")[2])) for c in run["containers"])
    ledger = json.load(open(res / "ledger.json"))
    assert [c["check"] for c in ledger["checks"]] == ["C0", "C1"] and not any(c["exceeds_cap"] for c in ledger["checks"])
    assert ledger["stages"]["starts_test"]["complete"] is True and ledger["stages"]["starts_test"]["launches"][0]["container_lives"] == 8
    backup = json.load(open(res / "backup.json"))
    assert len(backup["files"]) == 41
    assert all(LT.sha256_file(tiny["tmp"] / "local_units" / name) == sha for name, sha in backup["files"].items())
    assert json.load(open(res / "guard.json"))["all_equal"] is True


def test_the_records_hold_what_the_plan_asks_and_the_reading_script_reads_them(tiny):
    rec = json.load(open(tiny["results"] / "records.json"))
    assert rec == json.loads(json.dumps(tiny["records"]))
    searches = rec["searches"]
    assert len(searches) == 41 and sum(x["role"] == "guard" for x in searches) == 1
    for x in searches:
        assert x["start_key"] == [20261001, "start", x["start"]] and len(x["record"]) == 321
        path = tiny["tmp"] / "local_units" / x["unit_file"]
        with np.load(path) as z:
            assert np.asarray(x["record"], dtype=np.float64).tobytes() == z["record"].tobytes()
        harms = x["own_harms_at_saved_steps"]
        assert harms["start"]["step"] == 0 and harms["start"]["harm"] == x["record"][0]
        for name, h in harms.items():
            assert len(h["per_text"]) == N_TEXTS and (name == "start" or h["step"] == x["hook_events"][LR.SAVED[name]])
            assert h["harm"] == x["record"][h["step"]]  # guard G4, as recorded
        assert {"step_19", "step_20", "step_159", "step_160", "step_319", "step_320"} <= set(x["hook_events"])
    test, guard = ST.load_test_searches(tiny["results"] / "records.json")
    assert len(test) == 40 and ST.bit_equal(guard, tiny["guard_pilot"]["record"])


def test_a_search_is_the_plain_loops_bit_for_bit(tiny):
    """The guard's equality, and one test search's: the driver's path is the pilot's search."""
    rec = {(x["batch"], x["start"]): x for x in tiny["records"]["searches"]}
    plain = tiny["tc"].plain("C6", 12)
    assert ST.bit_equal(rec[("C6", 12)]["record"], plain["record"]) and rec[("C6", 12)]["hook_events"] == plain["hook_events"]
    assert LR.compare_with_pilot(tiny["tmp"] / "local_units" / "search_C6_s12.npz", plain) == {
        "record_equals_pilot": True, "saved_settings_equal_pilot": True, "hook_steps_equal_pilot": True}


def test_a_finished_test_is_not_launched_again(tiny):
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "RESULTS", tiny["results"])
        mp.setattr(SR, "check_launch_commit", lambda commit: None)
        with pytest.raises(LL.LaunchRefusal, match="already complete"):
            SR.launch_command(COMMIT, tiny["tc"].cloud(), listed_hourly_price=LISTED)


def test_a_guard_that_differs_by_one_bit_stops_before_the_records(tiny, tmp_path):
    results = tmp_path / "s6_starts"
    results.mkdir()
    shutil.copy(tiny["results"] / "runs_starts_test.json", results / "runs_starts_test.json")
    pilot = dict(tiny["guard_pilot"])
    pilot["record"] = list(pilot["record"])
    pilot["record"][200] = float(np.nextafter(pilot["record"][200], 1e9))
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "RESULTS", results)
        mp.setattr(SR, "VOLUME", str(tiny["tmp"] / "volume"))
        mp.setattr(SR, "tree_holds_only_this_tests_records", lambda: True)
        mp.setattr(LL, "head_commit", lambda: COMMIT)
        with pytest.raises(LL.LaunchRefusal, match="guard"):
            SR.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes(), log=lambda **f: None, pilot=pilot, dest=tmp_path / "units")
    g = json.load(open(results / "guard.json"))
    assert g["all_equal"] is False and g["outcomes"]["record_equals_pilot"] is False
    assert not (results / "records.json").exists()


def test_the_copy_refuses_bytes_that_are_not_the_ones_returned(tiny, tmp_path):
    run = json.load(open(tiny["results"] / "runs_starts_test.json"))

    def read(remote: str) -> bytes:
        data = Path(remote).read_bytes()
        return data + b"x" if remote.endswith("search_C4_s11.npz") else data

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(SR, "VOLUME", str(tiny["tmp"] / "volume"))
        with pytest.raises(LL.LaunchRefusal, match="search_C4_s11.npz"):
            SR.copy_units(run, read_file=read, dest=tmp_path / "u", out_path=tmp_path / "backup.json", commit=COMMIT, log=lambda **f: None)
    short = {**run, "containers": run["containers"][1:]}
    with pytest.raises(LL.LaunchRefusal, match="41 units"):
        SR.copy_units(short, read_file=read, dest=tmp_path / "u2", out_path=tmp_path / "backup2.json", commit=COMMIT, log=lambda **f: None)


def test_a_unit_from_another_start_or_commit_is_refused(tiny):
    meta = tiny["tc"].starts_meta()
    swapped = json.loads(json.dumps(meta))
    swapped["starts"]["9"]["sha256"] = meta["starts"]["10"]["sha256"]
    with pytest.raises(LL.LaunchRefusal, match="search_C1_s9.npz"):
        SR.build_records(tiny["tmp"] / "local_units", COMMIT, swapped)
    with pytest.raises(LL.LaunchRefusal, match="at this commit"):
        SR.build_records(tiny["tmp"] / "local_units", "d" * 40, meta)


def test_nothing_in_the_driver_prints():
    import re

    for module in ("starts_run", "modal_starts"):
        text = Path(SR.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module
