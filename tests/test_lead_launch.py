"""Plans 2 and 4 of the research log: what each container is handed, the checks before a deciding job, the launcher and its
ledger, the tables' arrival as bytes, and the spend arithmetic. No cloud call is made: the launcher is handed a cloud
made of plain functions. The last test runs the whole repeat rehearsal on the tiny model, through the same commands the
cloud module calls.

Known answers for the ledger come from the table and run specification's Section 9.1
(`freeze/amendment1_specs/table_and_run_spec.md`), from Amendment 4 (`freeze/amendment4.md`), and from the spend
review (research log, Section 2). None is this code's output.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import pilot as P

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504  # dollars per hour for one B200, 32 GiB, and one core, at the provider's listed prices
DECIDING = {"lead_attack": [f"A{n}" for n in range(1, 17)], "lead_heldout_1": ["H1"], "lead_heldout_2": [f"H{n}" for n in range(2, 17)],
            "delta_attack": [f"A{n}" for n in range(1, 9)], "delta_heldout": [f"H{n}" for n in range(1, 9)]}


# ----------------------------------------------------------------------------- one side per container (guard G2)


def test_G2_no_heldout_container_is_handed_attack_token_ids():
    """Every container's inputs, for both arms and both waves: one batch's token ids, of the container's own side. A
    held-out container's spec names the attack batches; nothing in its inputs is an attack batch's ids."""
    pools = LL._manifest()["pools"]
    loaded: list[str] = []

    def load_ids(name: str):
        loaded.append(name)
        texts = pools[name]["texts"]
        return np.full((len(texts), 512), int(name[1:]), dtype=np.int32), texts, [f"row-hash-{t}" for t in texts]

    assert [s.name for s in LG.DESIGN] == list(DECIDING) and sum(len(v) for v in DECIDING.values()) == 48
    for stage, batches in DECIDING.items():
        s = LG.stage_named(stage)
        specs = LL.container_specs(stage, "c" * 40)
        assert [x["batch"] for x in specs] == batches and len(batches) == s.containers  # one container per batch
        for spec in specs:
            loaded.clear()
            ids, rows = LL.container_inputs(spec, load_ids=load_ids, pools=pools)
            assert loaded == [spec["batch"]]  # this batch's ids were loaded, and no other's
            assert ids.shape == (128, 512) and len(rows) == 128 and rows[0] == f"row-hash-{pools[spec['batch']]['texts'][0]}"
            assert pools[spec["batch"]]["pool"] == {"attack": "A", "heldout": "H"}[s.side] == spec["batch"][0]
            assert (spec["mode"], spec["units"], spec["run"], spec["root"]) == ("deciding", "units", "run", f"/cache/s5_lead/{s.arm}")
            assert not any(k in spec for k in LR.REHEARSAL_ONLY)
            LR.check_spec(spec, False)
            if s.side == "heldout":
                assert spec["attack_batches"] == LL.BATCHES[s.arm]["attack"] and len(spec["attack_batches"]) == s.attack_batches  # names, to find their files
                assert all(isinstance(v, (str, list)) for v in spec.values()) and "ids" not in spec
            else:
                assert "attack_batches" not in spec
    # the two waves of the lead's held-out side are its sixteen batches, each once
    assert DECIDING["lead_heldout_1"] + DECIDING["lead_heldout_2"] == LL.BATCHES["lead"]["heldout"]
    # a spec that names a batch of the other side, or a calibration batch, is refused before anything is loaded
    loaded.clear()
    base = {"commit": "c" * 40, "mode": "deciding", "units": "units"}
    for bad in ({"arm": "lead", "side": "heldout", "batch": "A3"}, {"arm": "lead", "side": "attack", "batch": "H3"},
                {"arm": "lead", "side": "attack", "batch": "C1"}, {"arm": "delta_on", "side": "heldout", "batch": "H9"},
                {"arm": "lead", "side": "attack", "batch": "A3", "allow_pool": "A3"}):
        with pytest.raises(LL.LaunchRefusal):
            LL.container_inputs({**base, **bad}, load_ids=load_ids, pools=pools)
    assert loaded == []
    with pytest.raises(LL.LaunchRefusal, match="rehearsal alone"):  # a trigger is a rehearsal's
        LL.container_specs("lead_attack", "c" * 40, trigger="stop")


def test_a_rehearsals_specs_score_each_calibration_batch_on_itself_only():
    """Plan 4 of the research log, Section 6.1: five stages on C1 and C2, each batch playing both roles and scored on itself alone."""
    pools = LL._manifest()["pools"]
    commit = "ab" * 20
    root = "/cache/s5_lead/rehearsal/abababababab_2"
    expected = {"rehearsal_attack": ("rehearsal", "attack", ["C1", "C2"], "units_attack"), "rehearsal_heldout_1": ("rehearsal", "heldout", ["C1"], "units_heldout"),
                "rehearsal_heldout_2": ("rehearsal", "heldout", ["C2"], "units_heldout"),
                "rehearsal_delta_attack": ("rehearsal_delta_on", "attack", ["C1", "C2"], "units_delta_attack"),
                "rehearsal_delta_heldout": ("rehearsal_delta_on", "heldout", ["C1", "C2"], "units_delta_heldout")}
    assert [s.name for s in LG.REHEARSAL_DESIGN] == list(expected)
    for stage, (arm, side, batches, units) in expected.items():
        s = LG.stage_named(stage, LG.REHEARSAL_DESIGN)
        specs = LL.container_specs(stage, commit, rehearsal=2)
        assert [x["batch"] for x in specs] == batches and len(batches) == s.containers and (s.arm, s.side) == (arm, side)
        for spec in specs:
            assert (spec["mode"], spec["arm"], spec["side"], spec["units"], spec["root"], spec["run"]) == ("rehearsal", arm, side, units, root, "rehearsal_2")
            assert spec["allow_pool"] == spec["batch"]  # the override of the pool check, for this one batch
            assert spec.get("attack_batches", [spec["batch"]]) == [spec["batch"]]  # nothing is scored on a batch other than its own
            assert ("attack_units" in spec) == (side == "heldout") and spec.get("n_steps") == (20 if s.delta_held else None)
            assert not any(k in spec for k in ("stop_after_first_unit", "kill_at", "kill_after", "kill_key"))
            LR.check_spec(spec, False)
            with pytest.raises(LR.GuardFailure):  # and none of it passes for a deciding container's
                LR.check_spec({**spec, "mode": "deciding"}, False)
            ids, rows = LL.container_inputs(spec, load_ids=lambda name: (np.zeros((128, 512), dtype=np.int32), pools[name]["texts"], ["h"] * 128), pools=pools)
            assert ids.shape == (128, 512)
    assert LL.container_specs("rehearsal_heldout_1", commit, rehearsal=2)[0]["attack_units"] == "units_attack"
    # the two triggers: every container sets the stop flag after its first unit; the first batch's is killed inside its second
    stop = LL.container_specs("rehearsal_delta_heldout", commit, rehearsal=2, trigger="stop")
    assert [x.get("stop_after_first_unit") for x in stop] == [True, True] and not any("kill_at" in x for x in stop)
    kill = LL.container_specs("rehearsal_delta_heldout", commit, rehearsal=2, trigger="kill")
    assert (kill[0]["kill_at"], kill[0]["kill_after"]) == ("unit_renamed", "between_units") and "kill_at" not in kill[1]
    assert kill[0]["kill_key"] == "killed|rehearsal_2|abababababab|rehearsal_delta_heldout|C1" and not any("stop_after_first_unit" in x for x in kill)
    with pytest.raises(LL.LaunchRefusal):
        LL.container_specs("rehearsal_attack", commit, rehearsal=2, trigger="pause")
    # a rehearsal's inputs are a calibration batch's, named as its own override, and no other's
    good = LL.container_specs("rehearsal_attack", commit, rehearsal=2)[0]
    for bad in ({**good, "batch": "A1", "allow_pool": "A1"}, {**good, "batch": "C3", "allow_pool": "C3"}, {**good, "allow_pool": "C2"},
                {k: v for k, v in good.items() if k != "allow_pool"}, {**good, "arm": "lead"}):
        with pytest.raises(LL.LaunchRefusal):
            LL.container_inputs(bad, load_ids=lambda name: 1 / 0, pools=pools)
    with pytest.raises(LL.LaunchRefusal):  # the first rehearsal's record is not a repeat's folder
        LL.rehearsal_folder(1)
    assert LL.rehearsal_folder(2) == LL.RESULTS / "rehearsal_2" and LL.results_folder(0) == LL.RESULTS


def test_the_trigger_stops_after_the_first_unit_and_kills_inside_the_second():
    calls: list[str] = []
    assert LR.rehearsal_trigger({"arm": "lead"}, set_stop=lambda: calls.append("stop"), kill=lambda: calls.append("kill")) is None
    stop = LR.rehearsal_trigger({"stop_after_first_unit": True}, set_stop=lambda: calls.append("stop"), kill=lambda: calls.append("kill"))
    for point in ("unit_renamed", "between_units", "unit_renamed", "between_units"):
        stop(point)
    assert calls == ["stop"]  # once, after the first unit
    calls.clear()
    kill = LR.rehearsal_trigger({"kill_at": "unit_renamed", "kill_after": "between_units", "kill_key": "k"}, set_stop=lambda: calls.append("stop"),
                                kill=lambda: calls.append("kill"))
    kill("unit_renamed")  # the first unit's own file: not yet
    assert calls == []
    kill("between_units")
    kill("in_block")
    kill("unit_renamed")  # the second unit's file, renamed and without its marker
    assert calls == ["kill"]
    calls.clear()
    skipped_first = LR.rehearsal_trigger({"kill_at": "unit_renamed", "kill_after": "between_units", "kill_key": "k"}, set_stop=lambda: None, kill=lambda: calls.append("kill"))
    skipped_first("between_units")  # a first unit that was skipped writes no file
    skipped_first("unit_renamed")
    assert calls == ["kill"]


def test_the_cloud_function_takes_one_batch_of_ids():
    """The container's function has one `ids` argument, and the cloud module builds it from `container_inputs` alone."""
    src = (Path(LL.__file__).with_name("modal_lead.py")).read_text()
    signature = re.search(r"def batch_gpu\((.*?)\) -> dict:", src, re.S).group(1)
    assert [a.split(":")[0].strip() for a in signature.split(",")] == ["spec", "ids", "rows", "starts", "strata", "lay"]
    assert src.count("LL.container_inputs(spec)") == 1 and "pool_ids" not in src and src.count("batch_gpu.spawn(") == 1
    body = src[src.index("def stage(") : src.index("def assemble(")]
    assert "LL.container_inputs(spec)" in body and "batch_gpu.spawn(spec, ids, rows, starts, strata, lay)" in body
    # each command hands its work to the launcher's module, which the tests below drive without the cloud
    for command in ("stage_command", "assemble_command", "backup_command", "validate_command", "record_command"):
        assert src.count(f"LL.{command}(") == 1, command
    assert "LR.run_spec(" in src and "LR.assemble_from_spec(spec)" in src and "LR.guards_from_spec(spec)" in src and "LR.rehearsal_trigger(" in src
    # no bare print in any lead module (T15)
    for module in ("lead_run", "lead_launch", "lead_ledger", "modal_lead"):
        text = Path(LL.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module


def test_the_inputs_are_the_signed_ones():
    sha = LL.inputs_sha256()
    assert sha["manifest"].startswith("29d709c9") and sha["manifest"].endswith("7d71")
    assert sha["starts"] == "dcb53978dc20a18b9aa6e03480cb8590d7c90f15434d3cc485b9804ea81b9f9d"
    strata, strata_sha = LL.strata_by_module()
    assert strata_sha.startswith("12ce9067") and strata_sha.endswith("0af2") and strata_sha == sha["strata"]
    assert len(strata) == 24 and sum(v.size for v in strata.values()) == 38_912 and sum(int((v != 10).sum()) for v in strata.values()) == 9_948
    starts = LL.starts_for()
    assert tuple(sorted(starts)) == LR.STARTS == (9, 10, 11, 12, 13) and len(starts[9]) == 24
    texts, excluded = LL.heldout_texts(LL.BATCHES["delta_on"]["heldout"])
    assert len(texts) == 8 and all(len(t) == 128 for t in texts) and len(excluded) == 11
    assert sum(e["pool"] in LL.BATCHES["delta_on"]["heldout"] for e in excluded) == 8  # H1 twice, H3 twice, H4, H5, H7, H8
    # the rehearsal alone uses pilot start 1, and compares its searches with the pilot's stored ones
    one = LL.rehearsal_starts()
    assert tuple(one) == LR.REHEARSAL_STARTS == (1,) and all(np.array_equal(one[1][k], P.load_extended_start(1)[k]) for k in one[1])
    for batch in LL.REHEARSAL_BATCHES:
        pilot = LL.pilot_search(batch, 1)
        assert sorted(pilot) == ["hook_events", "record", "saved_sources_sha256"] and len(pilot["record"]) == 321
        assert set(pilot["saved_sources_sha256"]) == set(pilot["hook_events"]) and {f"step_{n}" for n in (19, 20, 319, 320)} <= set(pilot["hook_events"])
    texts, _ = LL.heldout_texts(["C1"])
    assert len(texts) == 1 and len(texts[0]) == 128


# ----------------------------------------------------------------------------- the checks before a job


def _git(top: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(top), "-c", "user.name=t", "-c", "user.email=t@t", *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """A small repository with this one's layout, in which Part A is the first commit."""
    top = tmp_path / "top"
    root = top / "vpd-audit-2"
    (root / "vpd_audit_2").mkdir(parents=True)
    (root / "freeze").mkdir()
    (root / "freeze" / "part1.md").write_text("the signed rules\n")
    _git(tmp_path, "init", "-q", str(top))
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "Part A")
    part_a = _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    for rel in LL.RUN_FILES:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# {rel}\n")
    (root / "freeze" / "amendment1_multipliers.md").write_text("multipliers\n")
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "the run's code and the multipliers")
    monkeypatch.setattr(LL, "REPO_ROOT", root)
    monkeypatch.setattr(LL, "RESULTS", root / "results" / "s5_lead")
    monkeypatch.setattr(LL, "PART_A_COMMIT", part_a)
    monkeypatch.setattr(LL, "MULTIPLIERS_MD", root / "freeze" / "amendment1_multipliers.md")
    return top, root


def test_a_job_is_refused_unless_every_condition_holds(repo):
    top, root = repo
    head = _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    LL.check_deciding_commit(head, head)  # clean, at the named commit, descending from Part A, covered by the rehearsal
    LL.check_rehearsal_commit(head, None)
    LL.check_rehearsal_commit(head, head)
    with pytest.raises(LL.LaunchRefusal, match="not the one named"):
        LL.check_deciding_commit("0" * 40, head)
    with pytest.raises(LL.LaunchRefusal, match="not the one named"):
        LL.check_rehearsal_commit("0" * 40, None)
    with pytest.raises(LL.LaunchRefusal, match="began at another commit"):
        LL.check_rehearsal_commit(head, "1" * 40)
    # the run's own records are the one thing the tree may hold: its stages write them as they go, under one commit
    (root / "results" / "s5_lead" / "rehearsal_2").mkdir(parents=True)
    (root / "results" / "s5_lead" / "ledger.json").write_text("{}")
    (root / "results" / "s5_lead" / "rehearsal_2" / "a file with a space.json").write_text("{}")
    assert LL.tree_holds_only_the_runs_records() and not LL.tree_is_clean()
    LL.check_deciding_commit(head, head)
    LL.check_rehearsal_commit(head, head)
    # any other untracked file, or an uncommitted edit, under the code folder
    for stray in (root / "scratch.txt", root / "results" / "s5_other.json", root / "vpd_audit_2" / "new_module.py"):
        stray.write_text("x")
        assert not LL.tree_holds_only_the_runs_records()
        with pytest.raises(LL.LaunchRefusal, match="not clean"):
            LL.check_deciding_commit(head, head)
        with pytest.raises(LL.LaunchRefusal, match="not clean"):
            LL.check_rehearsal_commit(head, head)
        stray.unlink()
    (root / "vpd_audit_2" / "lead_run.py").write_text("# an edit not committed\n")
    with pytest.raises(LL.LaunchRefusal, match="not clean"):
        LL.check_rehearsal_commit(head, head)
    _git(top, "checkout", "--", "vpd-audit-2/vpd_audit_2/lead_run.py")
    shutil.rmtree(root / "results")
    # an analysis module may differ from the rehearsal's commit; a module the run imports may not
    (root / "vpd_audit_2" / "lead_reading.py").write_text("# an analysis module, changed after the rehearsal\n")
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "analysis only")
    later = _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    LL.check_deciding_commit(later, head)
    (root / "vpd_audit_2" / "adversary.py").write_text("# the search, changed after the rehearsal\n")
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "a change to the search")
    changed = _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    assert LL.run_files_changed(head, changed) == ["vpd_audit_2/adversary.py"]
    with pytest.raises(LL.LaunchRefusal, match="rehearsal does not cover.*adversary.py"):
        LL.check_deciding_commit(changed, head)
    LL.check_deciding_commit(changed, changed)  # a rehearsal repeated at the new commit covers it
    # the multipliers file must be committed
    (root / "freeze" / "amendment1_multipliers.md").unlink()
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", "no multipliers")
    gone = _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    with pytest.raises(LL.LaunchRefusal, match="multipliers"):
        LL.check_deciding_commit(gone, gone)


def test_a_commit_that_does_not_descend_from_part_a_is_refused(repo, monkeypatch):
    top, _ = repo
    head = _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    monkeypatch.setattr(LL, "PART_A_COMMIT", "1" * 40)
    with pytest.raises(LL.LaunchRefusal, match="Part A"):
        LL.check_deciding_commit(head, head)


def test_the_real_branch_descends_from_part_a_and_the_run_files_exist():
    here = Path(LL.__file__).resolve().parent.parent
    known = subprocess.run(["git", "-C", str(here), "cat-file", "-e", f"{LL.PART_A_COMMIT}^{{commit}}"], capture_output=True)
    if known.returncode != 0:
        pytest.skip("Part A's commit is in the research log's history only, not in this copy's")
    r = subprocess.run(["git", "-C", str(here), "merge-base", "--is-ancestor", LL.PART_A_COMMIT, "HEAD^{commit}"], capture_output=True)
    assert r.returncode == 0
    for rel in LL.RUN_FILES:
        assert (here / rel).exists(), rel


def test_a_deciding_stage_rests_on_the_latest_rehearsal_having_met_every_outcome(tmp_path):
    with pytest.raises(LL.LaunchRefusal, match="no repeat rehearsal"):
        LL.rehearsal_of_record(tmp_path)
    (tmp_path / "rehearsal").mkdir()  # the first rehearsal's record is not a repeat's
    (tmp_path / "rehearsal" / "rehearsal.json").write_text("{}")
    with pytest.raises(LL.LaunchRefusal, match="no repeat rehearsal"):
        LL.rehearsal_of_record(tmp_path)
    for n, met in ((2, True), (3, False)):
        (tmp_path / f"rehearsal_{n}").mkdir()
        (tmp_path / f"rehearsal_{n}" / "ledger.json").write_text("{}")
        if n == 2:
            (tmp_path / f"rehearsal_{n}" / "rehearsal.json").write_text(json.dumps({"all_required_outcomes_met": met, "commit": "c" * 40}))
    with pytest.raises(LL.LaunchRefusal, match="no record"):  # the latest attempt began and wrote no record
        LL.rehearsal_of_record(tmp_path)
    (tmp_path / "rehearsal_3" / "rehearsal.json").write_text(json.dumps({"all_required_outcomes_met": False, "commit": "d" * 40}))
    with pytest.raises(LL.LaunchRefusal, match="did not meet"):  # and an earlier attempt that passed does not stand in for it
        LL.rehearsal_of_record(tmp_path)
    (tmp_path / "rehearsal_3" / "rehearsal.json").write_text(json.dumps({"all_required_outcomes_met": True, "commit": "d" * 40}))
    assert LL.rehearsal_of_record(tmp_path) == (3, {"all_required_outcomes_met": True, "commit": "d" * 40})


# ----------------------------------------------------------------------------- sealed tables, as bytes, and the receipt


def test_a_table_arrives_as_bytes_checked_against_the_assemblers_hash(tmp_path):
    arm_dir = tmp_path / "lead"
    core, part = b"the core file's bytes", b"a per-text part's bytes"
    files = [{"name": "table_core.npz", "sha256": hashlib.sha256(core).hexdigest()}, {"name": "table_per_text_01.npz", "sha256": hashlib.sha256(part).hexdigest()}]
    with pytest.raises(LL.LaunchRefusal, match="table_core.npz"):
        LL.receive_table(arm_dir, "table_core.npz", core + b"x", files[0]["sha256"])  # bytes that are not the assembler's
    assert not (arm_dir / "sealed" / "table_core.npz").exists()
    LL.receive_table(arm_dir, "table_core.npz", core, files[0]["sha256"])
    LL.receive_table(arm_dir, "table_per_text_01.npz", part, files[1]["sha256"])
    assert (arm_dir / "sealed" / "table_core.npz").read_bytes() == core  # written as they came; they are not a table and were never parsed
    assert (arm_dir / "sealed" / "DO_NOT_OPEN.md").read_text().startswith("DO NOT OPEN.")
    assembled = {"arm": "lead", "files": files, "design": {"K_A": 16}, "complete": True, "run_commit": "c" * 40, "outcomes": {}, "prep_fp": {}}
    receipt = LL.write_receipt(arm_dir, assembled)
    assert receipt == json.loads((arm_dir / "receipt.json").read_text())
    assert receipt == {"arm": "lead", "files": files, "shapes": {"K_A": 16}, "complete": True, "run_commit": "c" * 40}
    # the receipt is where the analysis's entry point looks for it, and in the form it reads
    from vpd_audit_2 import lead_analysis as LA

    assert LA._receipt_path(arm_dir / "sealed") == arm_dir / "receipt.json"
    (arm_dir / "sealed" / "table_per_text_01.npz").write_bytes(b"changed after the copy")
    with pytest.raises(LL.LaunchRefusal, match="table_per_text_01.npz"):
        LL.write_receipt(arm_dir, assembled)


def _unit(name: str, ok: bool = True, skipped: bool = False) -> dict:
    return {"unit": name, "sha256": hashlib.sha256(name.encode()).hexdigest(), "guards": {"G4": ok}, "skipped": skipped}


def _job(container: str, units: list[dict], expected: int, stopped: bool = False, seconds: float = 700.0, attempts: int = 1) -> dict:
    return {"container": container, "units": units, "finished_units": len(units), "expected_units": expected, "stopped": stopped, "seconds": seconds,
            "environment": {}, "attempts": attempts}


def test_a_stages_record_holds_counts_hashes_seconds_and_outcomes():
    done = LL.stage_summary("lead_attack", [_job("lead|attack|A1", [_unit("u1"), _unit("u2")], 2), _job("lead|attack|A2", [_unit("u3"), _unit("u4", skipped=True)], 2)])
    assert done == {"stage": "lead_attack", "containers": 2, "finished_units": 4, "expected_units": 4, "stopped": False, "function_seconds": 1400.0,
                    "all_guards_true": True, "complete": True}
    short = LL.stage_summary("lead_attack", [_job("lead|attack|A1", [_unit("u1")], 2, stopped=True)])
    assert short["complete"] is False and short["stopped"] is True and (short["finished_units"], short["expected_units"]) == (1, 2)


# ----------------------------------------------------------------------------- the ledger's arithmetic


# The table specification's Section 9.1: a search in 122.2 seconds, a scoring pass in 0.18, and 45 seconds per container to load and prepare.
SPEC_TIMINGS = {"seconds_per_search_step": 122.2 / 320, "seconds_per_search_step_delta_on": 122.2 / 320, "seconds_per_scoring_pass": 0.18, "seconds_to_ready": 45.0,
        "seconds_first_search_extra": 0.0, "seconds_per_search_fixed": 0.0, "seconds_per_commit_after_search": 0.0, "seconds_per_commit_after_blocks": 0.0,
        "seconds_per_shuffle": 0.0, "seconds_per_search_unit_other": 0.0, "seconds_per_block_other": 0.0}


def test_stage_work_is_the_design():
    assert LG.stage_work("lead_attack") == {"containers": 16, "searches": 80, "search_steps": 25_600, "scoring_passes": 880, "shuffles_made": 0,
                                            "blocks": 0, "commits": 80, "commits_after_search": 80, "commits_after_blocks": 0}
    one, rest = LG.stage_work("lead_heldout_1"), LG.stage_work("lead_heldout_2")
    assert (one["containers"], rest["containers"]) == (1, 15) and one["blocks"] == 80  # wave 1: H1's five starts against sixteen attack batches
    lead = {k: one[k] + rest[k] for k in one}  # the two waves together are the lead's held-out side
    assert lead["blocks"] == 1_280 and lead["shuffles_made"] == 1_280 * 64 and lead["commits"] == 80 + 16 * 16
    assert lead["scoring_passes"] - 880 == 94_720  # the table specification's Section 3.6: the lead's carried passes with nothing missing
    delta = LG.stage_work("delta_heldout")
    assert delta["scoring_passes"] - 40 * 6 == 14_400 and delta["blocks"] == 320 and delta["commits"] == 40 + 8 * 8  # and the delta-on arm's
    assert LG.stage_work("delta_attack")["scoring_passes"] == 240
    # the own-batch re-scores: 160 searches with the start and 10 settings, 80 with the start and 5 (the erratum's 2,240)
    assert 2 * 880 + 2 * 240 == 2_240
    # the run as Amendment 4's Section 1 counts it
    total = {k: sum(LG.stage_work(s)[k] for s in LG.DESIGN) for k in one}
    assert total == {"containers": 48, "searches": 240, "search_steps": 76_800, "scoring_passes": 111_360, "shuffles_made": 94_720, "blocks": 1_600,
                     "commits": 560, "commits_after_search": 240, "commits_after_blocks": 320}
    # the rehearsal: one start, each held-out role scoring one attack batch; 74 passes to a lead block
    r = {s.name: LG.stage_work(s) for s in LG.REHEARSAL_DESIGN}
    assert (r["rehearsal_attack"]["searches"], r["rehearsal_heldout_1"]["blocks"], r["rehearsal_heldout_1"]["scoring_passes"]) == (2, 1, 11 + 74)
    assert r["rehearsal_delta_heldout"]["search_steps"] == 40 and r["rehearsal_delta_heldout"]["scoring_passes"] == 2 * (6 + 45)
    assert sum(s.containers for s in LG.REHEARSAL_DESIGN) == 8


def test_stage_seconds_reproduce_table_spec_table():
    """Section 9.1: search seconds 9,776, 9,776, 4,888, 4,888; scoring seconds 160, 17,210, 45, 2,640; 45 seconds per container."""
    waves = [LG.stage_seconds(s, SPEC_TIMINGS) for s in ("lead_heldout_1", "lead_heldout_2")]
    heldout = {k: sum(w[k] for w in waves) for k in waves[0]}
    got = {"lead_attack": LG.stage_seconds("lead_attack", SPEC_TIMINGS), "lead_heldout": heldout, "delta_attack": LG.stage_seconds("delta_attack", SPEC_TIMINGS),
           "delta_heldout": LG.stage_seconds("delta_heldout", SPEC_TIMINGS)}
    expected = {"lead_attack": (9_776, 160, 720), "lead_heldout": (9_776, 17_210, 720), "delta_attack": (4_888, 45, 360), "delta_heldout": (4_888, 2_640, 360)}
    for stage, (search, scoring, overhead) in expected.items():
        s = got[stage]
        assert s["search"] == pytest.approx(search, abs=0.5) and s["scoring"] == pytest.approx(scoring, abs=5.5) and s["overhead"] == pytest.approx(overhead)
        assert s["total"] == pytest.approx(s["search"] + s["scoring"] + s["overhead"])
    # each kind of overhead is counted where the stage has it, and a delta-on stage's steps at the delta-on arm's own rate
    extra = {**SPEC_TIMINGS, "seconds_first_search_extra": 2.0, "seconds_per_search_fixed": 0.25, "seconds_per_commit_after_search": 4.0, "seconds_per_commit_after_blocks": 5.0,
             "seconds_per_shuffle": 0.01, "seconds_per_search_unit_other": 0.05, "seconds_per_block_other": 0.5, "seconds_per_search_step_delta_on": 0.5}
    assert LG.stage_seconds("lead_heldout_2", extra)["overhead"] == pytest.approx(15 * (45 + 2.0) + 75 * (0.25 + 0.05) + 75 * 4.0 + 240 * 5.0 + 76_800 * 0.01 + 1_200 * 0.5)
    assert LG.stage_seconds("lead_attack", extra)["overhead"] == pytest.approx(16 * 47.0 + 80 * 0.3 + 80 * 4.0)
    assert LG.stage_seconds("delta_attack", extra)["search"] == pytest.approx(12_800 * 0.5) and LG.stage_seconds("lead_attack", extra)["search"] == pytest.approx(9_776)


def test_money_is_counted_as_amendment_4_says():
    """The larger of function hours at $6.80 and the listed price times function seconds plus 50 seconds of boot for
    every container life; a posted bill enters times 1.03. Known answers: the spend review, Section 2, and Amendment 4."""
    assert (LG.CAP_DOLLARS, LG.FLAT_RATE, LG.BOOT_SECONDS, LG.BILLING_LAG) == (150.0, 6.80, 50.0, 1.03)
    # the spend review's table: the lead's attack stage, 16 containers; the flat rate understates it
    attack = LG.money(11_008.7, 16, LISTED)
    assert attack["at_the_flat_rate"] == pytest.approx(20.79, abs=0.005) and attack["at_the_listed_price_with_boot"] == pytest.approx(21.49, abs=0.005)
    assert attack["dollars"] == attack["at_the_listed_price_with_boot"] and attack["billed"] is None
    # and the lead's held-out side, 16 containers, where the flat rate is the larger
    heldout = LG.money(30_252.8, 16, LISTED)
    assert heldout["at_the_flat_rate"] == pytest.approx(57.14, abs=0.005) and heldout["at_the_listed_price_with_boot"] == pytest.approx(56.52, abs=0.005)
    assert heldout["dollars"] == heldout["at_the_flat_rate"]
    # the whole run on the first rehearsal's corrected reading: $104.39 flat; with boot, the spend review has $104.96, and
    # (55,263 + 48 x 50) / 3600 x 6.552504 is 104.9547, a cent below it
    run = LG.money(55_263, 48, LISTED)
    assert run["at_the_flat_rate"] == pytest.approx(104.39, abs=0.005) and run["dollars"] == pytest.approx(104.9547, abs=0.0001)
    assert run["dollars"] == pytest.approx(104.96, abs=0.01)
    # Amendment 4, Section 3, item 2: the first rehearsal, three container lives; its bill is below both figures
    first = LG.money(428.6, 3, LISTED, billed=0.7509)
    assert first["at_the_flat_rate"] == pytest.approx(0.81, abs=0.005) and first["at_the_listed_price_with_boot"] == pytest.approx(1.05, abs=0.005)
    assert first["dollars"] == first["at_the_listed_price_with_boot"] and 0.7509 * 1.03 < first["at_the_flat_rate"]
    # the pilot: $19.20 billed for 10,170 function seconds in 8 containers; here the bill times 1.03 is the largest
    pilot = LG.money(10_170, 8, LISTED, billed=19.20)
    assert pilot["at_the_flat_rate"] == pytest.approx(19.21, abs=0.005) and pilot["dollars"] == pytest.approx(19.20 * 1.03)
    # sums over runs: a bill counts where it has posted, and a part of the whole can only be too low
    both = LG.add({"function_seconds": 428.6, "container_lives": 3, "billed": 0.7509}, {"function_seconds": 1_000.0, "container_lives": 11, "billed": None})
    assert both == {"function_seconds": 1_428.6, "container_lives": 14.0, "billed": 0.7509}
    assert LG.add({"function_seconds": 1.0, "container_lives": 1, "billed": None})["billed"] is None


def test_check_c0_prices_the_run_on_top_of_the_rehearsals():
    spec_overhead = {**SPEC_TIMINGS, "seconds_to_ready": 65.0}  # its overhead column sums to 3,120 seconds over 48 containers
    spent = {"function_seconds": 1_600.0, "container_lives": 14, "billed": 0.7509}
    c0 = LG.check_c0(spec_overhead, LISTED, spent)
    assert c0["function_hours"] == pytest.approx(14.6, abs=0.15) and c0["run"]["container_lives"] == 48
    assert c0["run_dollars"] == pytest.approx(max(6.80 * c0["function_hours"], LISTED * (c0["function_hours"] + 48 * 50 / 3600)))
    assert c0["run_dollars"] == pytest.approx(100, abs=1.5)  # Section 9.1: about $100
    assert c0["spent_dollars"] == pytest.approx(LISTED * (1_600 + 14 * 50) / 3600) and c0["spent_dollars"] > 6.80 * 1_600 / 3600
    assert c0["projected_dollars"] == pytest.approx(c0["run_dollars"] + c0["spent_dollars"]) and c0["cap"] == 150.0 and c0["exceeds_cap"] is False
    assert LG.check_c0(spec_overhead, LISTED, spent, cap=100.0)["exceeds_cap"] is True
    dear = LG.check_c0(spec_overhead, LISTED, {"function_seconds": 1_600.0, "container_lives": 14, "billed": 60.0})  # a bill, once posted, counts times 1.03
    assert dear["spent_dollars"] == pytest.approx(61.8) and dear["exceeds_cap"] is True and dear["run_dollars"] == c0["run_dollars"]
    assert set(c0["stages"]) == set(DECIDING) and c0["assemble_seconds"] == 0.0
    assert LG.check_c0(spec_overhead, LISTED, spent, assemble_seconds=3_600.0)["function_hours"] == pytest.approx(c0["function_hours"] + 1.0)


def test_what_remains_is_projected_at_the_runs_own_measured_timings():
    predicted = {s.name: LG.stage_seconds(s, SPEC_TIMINGS)["total"] for s in LG.DESIGN}
    rest = LG.DESIGN[1:]
    assert LG.remaining_seconds(rest, SPEC_TIMINGS, {}) == pytest.approx(sum(predicted[s.name] for s in rest))  # nothing measured yet
    # stage 1 ran 10 percent slow: every later stage is scaled by it until a held-out stage has run
    slow = {"lead_attack": 1.1 * predicted["lead_attack"]}
    assert LG.remaining_seconds(rest, SPEC_TIMINGS, slow) == pytest.approx(1.1 * sum(predicted[s.name] for s in rest))
    # the held-out side ran 20 percent slow over both waves: the delta-on held-out stage takes that, its attack stage stage 1's
    both = {**slow, "lead_heldout_1": 1.5 * predicted["lead_heldout_1"], "lead_heldout_2": 1.18 * predicted["lead_heldout_2"]}
    side = (both["lead_heldout_1"] + both["lead_heldout_2"]) / (predicted["lead_heldout_1"] + predicted["lead_heldout_2"])
    assert side == pytest.approx(1.2, abs=0.001)
    assert LG.remaining_seconds(LG.DESIGN[3:], SPEC_TIMINGS, both) == pytest.approx(1.1 * predicted["delta_attack"] + side * predicted["delta_heldout"])
    # check C2 (plan 4 of the research log, Section 4.3): wave 2 at the larger of the first container's seconds and the projection for a container
    per = predicted["lead_heldout_2"] / 15
    later = lambda measured: LG.remaining_seconds(LG.DESIGN[3:], SPEC_TIMINGS, measured)  # noqa: E731
    fast = {**slow, "lead_heldout_1": 0.8 * per}
    assert LG.remaining_after_first_heldout(LG.DESIGN, SPEC_TIMINGS, fast, 0.8 * per) == pytest.approx(15 * per + later(fast))  # a fast first container does not lower it
    late = {**slow, "lead_heldout_1": 1.3 * per}
    assert LG.remaining_after_first_heldout(LG.DESIGN, SPEC_TIMINGS, late, 1.3 * per) == pytest.approx(15 * 1.3 * per + later(late))
    check = LG.check_later("C2", spent_so_far={"function_seconds": 12_000.0, "container_lives": 31, "billed": None}, remaining_seconds=36_000.0,
                           remaining_lives=31, listed_hourly_price=LISTED)
    assert check["spent_dollars"] == pytest.approx(LISTED * (12_000 + 1_550) / 3600) and check["spent"]["at_the_flat_rate"] == pytest.approx(22.6667, abs=1e-4)
    # what remains is priced as the larger of the two figures as well: 68.00 flat, 68.35 with 31 boots
    assert check["remaining"]["at_the_flat_rate"] == pytest.approx(68.0) and check["remaining_dollars"] == pytest.approx(LISTED * (36_000 + 1_550) / 3600)
    assert check["projected_dollars"] == pytest.approx(check["spent_dollars"] + check["remaining_dollars"]) and check["exceeds_cap"] is False and check["cap"] == 150.0
    over = LG.check_later("C3", spent_so_far={"function_seconds": 0.0, "container_lives": 0, "billed": 132.0}, remaining_seconds=7_200.0, remaining_lives=16,
                          listed_hourly_price=LISTED)
    assert over["spent_dollars"] == pytest.approx(135.96) and over["remaining_dollars"] == pytest.approx(14.56, abs=0.005) and over["exceeds_cap"] is True
    assert LG.check_later("C3", spent_so_far={"function_seconds": 0.0, "container_lives": 0, "billed": 130.0}, remaining_seconds=7_200.0, remaining_lives=16,
                          listed_hourly_price=LISTED)["exceeds_cap"] is False  # 133.90 and 14.56: under the cap by 1.54


def test_timings_from_the_rehearsals_containers():
    """Every container that returned is used; each timing is a mean over what was observed. The figures are made up."""
    search = {"search": 124.0, "search_count": 320.0, "search_iteration_0": 2.4, "search_iteration_0_count": 1.0, "search_iterations_warm": 3.6,
              "search_iterations_warm_count": 9.0, "search_iterations_after_warm": 117.8, "search_iterations_after_warm_count": 310.0,
              "search_final_harm": 0.18, "search_final_harm_count": 1.0, "search_tail": 0.02, "search_tail_count": 1.0}
    attack = {"arm": "rehearsal", "timings": {**search, "to_ready": 40.0, "to_ready_count": 1.0, "scoring": 2.2, "scoring_count": 11.0, "scoring_in_search_units": 2.2,
                                               "wrapper_check": 2.0, "search_unit_whole": 128.3, "search_unit_whole_count": 1.0,
                                               "volume_commit_after_search": 4.0, "volume_commit_after_search_count": 1.0}}
    heldout = {"arm": "rehearsal", "timings": {**search, "to_ready": 60.0, "to_ready_count": 1.0, "scoring": 17.8, "scoring_count": 89.0, "scoring_in_search_units": 2.2,
                                                "wrapper_check": 2.0, "search_unit_whole": 128.3, "search_unit_whole_count": 1.0, "scoring_in_blocks": 14.8,
                                                "making_shuffles": 0.64, "making_shuffles_count": 64.0, "block_whole": 15.94, "block_whole_count": 1.0,
                                                "volume_commit_after_search": 6.0, "volume_commit_after_search_count": 1.0, "volume_commit_after_blocks": 5.0,
                                                "volume_commit_after_blocks_count": 1.0, "volume_commit_nothing_new": 0.07, "volume_commit_nothing_new_count": 1.0}}
    skipped = {"arm": "rehearsal", "timings": {"to_ready": 50.0, "to_ready_count": 1.0, "volume_commit_nothing_new": 0.06, "volume_commit_nothing_new_count": 1.0}}
    delta = {"arm": "rehearsal_delta_on", "timings": {"to_ready": 30.0, "to_ready_count": 1.0, "search": 10.0, "search_count": 20.0, "search_iteration_0": 2.6,
                                                       "search_iteration_0_count": 1.0, "search_iterations_warm": 3.5, "search_iterations_warm_count": 9.0,
                                                       "search_iterations_after_warm": 3.9, "search_iterations_after_warm_count": 10.0, "search_final_harm": 0.2,
                                                       "search_final_harm_count": 1.0, "search_tail": 0.0, "search_tail_count": 1.0,
                                                       "volume_commit_after_search": 2.0, "volume_commit_after_search_count": 1.0}}
    t = LG.timings_from_rehearsal([attack, heldout, skipped, delta])
    assert set(LG.TIMING_KEYS) <= set(t)
    assert t["seconds_per_search_step"] == pytest.approx(0.38) and t["seconds_per_search_step_delta_on"] == pytest.approx(0.39)  # the steady rates, each arm's own
    assert t["seconds_to_ready"] == pytest.approx(45.0)  # every container, the one that skipped its search too
    # the first ten iterations beyond ten at the steady rate: 6.0 - 3.8 twice, and 6.1 - 3.9
    assert t["observations"]["seconds_first_search_extra"] == pytest.approx([2.2, 2.2, 2.2]) and t["seconds_first_search_extra"] == pytest.approx(2.2)
    assert t["seconds_per_search_fixed"] == pytest.approx(0.2) and t["seconds_per_scoring_pass"] == pytest.approx(0.2)
    assert t["seconds_per_commit_after_search"] == pytest.approx(4.0) and t["seconds_per_commit_after_blocks"] == pytest.approx(5.0)  # those that wrote; none that did not
    assert t["seconds_per_shuffle"] == pytest.approx(0.01) and t["seconds_per_block_other"] == pytest.approx(15.94 - 14.8 - 0.64)
    assert t["seconds_per_search_unit_other"] == pytest.approx(128.3 - 124.0 - 2.2 - 2.0)  # without the check only a rehearsal runs
    assert t["observations"]["seconds_to_ready"] == [40.0, 60.0, 50.0, 30.0] and t["observations"]["of_the_delta_on_arm"] == [False, False, True]
    with pytest.raises(ValueError, match="search_iterations_after_warm"):  # no delta-on search: the delta-on arm's rate cannot be guessed
        LG.timings_from_rehearsal([attack, heldout, skipped])


# ----------------------------------------------------------------------------- the launcher, with a cloud made of plain functions


class Clock:
    def __init__(self) -> None:
        self.now = 1_000.0

    def __call__(self) -> float:
        return self.now


class Call:
    """A container's call, scripted: ready `after` seconds from its spawn, when it returns `result` or raises it."""

    def __init__(self, clock: Clock, after: float, result) -> None:
        self.clock, self.ready, self.result = clock, clock.now + after, result

    def get(self, timeout: float):
        self.clock.now += max(0.0, min(timeout, self.ready - self.clock.now))
        if self.clock.now < self.ready:
            raise TimeoutError
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


class Scripted:
    """A cloud made of plain functions, whose containers do what a script says."""

    def __init__(self, script: dict[str, tuple[float, object]], *, guards: dict | Exception | None = None, bill: dict | None = None, lives: dict | None = None) -> None:
        self.clock, self.script, self.stops, self.lines, self.specs = Clock(), script, [], [], []
        self.guard_outcomes, self.bill, self.lives, self.guards_asked = guards, bill or {}, lives or {}, []

    def cloud(self, app_id: str = "ap-one") -> LL.Cloud:
        def spawn(spec):
            self.specs.append(spec)
            self.clock.now += 1.0
            return Call(self.clock, *self.script[spec["batch"]])

        def guards(spec):
            self.guards_asked.append(spec)
            if isinstance(self.guard_outcomes, Exception):
                raise self.guard_outcomes
            return {"outcomes": dict(self.guard_outcomes), "seconds": 3.0}

        return LL.Cloud(spawn=spawn, set_stop=self.stops.append, attempts=lambda spec: self.lives.get(spec["batch"], 0), guards=guards, app_id=app_id,
                        read_bill=lambda apps: {"read_at": "2026-10-06T18:00:00+00:00", "by_app": {a: v for a, v in self.bill.items() if a in apps}},
                        log=lambda **f: self.lines.append(LR.log_record(**f)), clock=self.clock)


def _stage(name: str, arm: str, side: str, containers: int, attack_batches: int = 0) -> LG.Stage:
    return LG.Stage(name, arm, side, containers, 1, 320, 10, 8, attack_batches, False)


def _design(prefix: str = "") -> tuple[LG.Stage, ...]:
    return (_stage("one", prefix + "lead", "attack", 2), _stage("two", prefix + "lead", "heldout", 1, 2), _stage("three", prefix + "lead", "heldout", 1, 2),
            _stage("four", prefix + "delta_on", "attack", 2), _stage("five", prefix + "delta_on", "heldout", 2, 2))


def _specs(stage: LG.Stage, batches: list[str]) -> list[dict]:
    return [{"arm": stage.arm, "side": stage.side, "batch": b, "mode": "deciding"} for b in batches]


ALL_TRUE = {g: True for g in LR.REQUIRED_GUARDS + LR.WRONG_BATCH_GUARDS}
ONE_BATCH_ON_BOTH_SIDES = {**ALL_TRUE, "G6": False, "G11_differs_from_the_heldout_batchs_own": False, "G6_reports_every_carried_vector_equal": True,
                           "G11_reports_every_carried_vector_equal_to_the_heldout_own": True}


def _drive(tmp: Path, design, stage, batches, scripted: Scripted, *, app_id: str = "ap-one", cap: float = 150.0, outside=LL.no_spend_outside, **kw) -> dict:
    return LL.drive_stage(stage, _specs(stage, batches), scripted.cloud(app_id), ledger_path=tmp / "ledger.json", runs_path=tmp / f"runs_{stage.name}.json", design=design,
                          timings=SPEC_TIMINGS, listed_hourly_price=LISTED, cap=cap, outside=outside, commit="c" * 40, guards_spec={"arm": stage.arm}, **kw)


def test_a_stage_launches_its_containers_at_once_and_the_ledger_counts_them(tmp_path):
    design = _design()
    one = design[0]
    done = Scripted({"A1": (600.0, _job("lead|attack|A1", [_unit("u1")], 1, seconds=580.0)), "A2": (700.0, _job("lead|attack|A2", [_unit("u2")], 1, seconds=690.0))},
                    bill={"ap-one": 1.25, "ap-other": 99.0})
    summary = _drive(tmp_path, design, one, ["A1", "A2"], done)
    assert summary["complete"] is True and summary["finished_units"] == 2 and summary["errors"] == {}
    assert done.stops == [False] and len(done.specs) == 2 and all(s["launch"] == "ap-one|one|1" for s in done.specs)  # the flag cleared, and both launched before any wait
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    launch = ledger["stages"]["one"]["launches"][0]
    assert ledger["stages"]["one"]["complete"] is True and len(ledger["stages"]["one"]["launches"]) == 1 and launch["ended"] is not None
    assert launch["spawned"]["A2"] - launch["spawned"]["A1"] == 1.0 and sorted(launch["calls"]) == ["A1", "A2"]
    a1 = launch["calls"]["A1"]
    assert (a1["outcome"], a1["returned_seconds"], a1["counted_seconds"], a1["lives"], a1["attempts"], a1["error"]) == ("returned", 580.0, 580.0, 1, 1, None)
    assert a1["wait_seconds"] >= 600.0 and (a1["stopped"], a1["finished_units"], a1["expected_units"]) == (False, 1, 1)
    assert launch["function_seconds"] == 580.0 + 690.0 and launch["container_lives"] == 2  # each first life returned: the containers' own seconds
    # check C1 follows the design's first stage, on the run's own clocks, with the bill as it stood and when it was read
    (c1,) = ledger["checks"]
    assert (c1["check"], c1["after_stage"], c1["bill_read_at"], c1["exceeds_cap"]) == ("C1", "one", "2026-10-06T18:00:00+00:00", False)
    assert c1["spent"]["function_seconds"] == 1_270.0 and c1["spent"]["container_lives"] == 2 and c1["spent"]["billed"] == 1.25
    assert c1["spent_dollars"] == pytest.approx(max(6.80 * 1_270 / 3600, LISTED * 1_370 / 3600, 1.25 * 1.03))
    predicted = LG.stage_seconds(one, SPEC_TIMINGS)["total"]
    assert c1["remaining"]["function_seconds"] == pytest.approx(LG.remaining_seconds(design[1:], SPEC_TIMINGS, {"one": 1_270.0}, design))
    assert c1["remaining"]["function_seconds"] == pytest.approx(1_270.0 / predicted * sum(LG.stage_seconds(s, SPEC_TIMINGS)["total"] for s in design[1:]))
    assert c1["remaining"]["container_lives"] == 6 and c1["projected_dollars"] == pytest.approx(c1["spent_dollars"] + c1["remaining_dollars"])
    assert ledger["bills"] == [{"read_at": "2026-10-06T18:00:00+00:00", "by_app": {"ap-one": 1.25}}] and ledger["stopped_by"] is None and ledger["stops"] == []
    # the stage's record: the containers' returns, under the launch's number as well
    runs = json.loads((tmp_path / "runs_one.json").read_text())
    assert runs == json.loads((tmp_path / "runs_one_launch_1.json").read_text())
    assert [c["container"] for c in runs["containers"]] == ["lead|attack|A1", "lead|attack|A2"] and runs["launch"] == "ap-one|one|1"
    assert [ln["event"] for ln in done.lines] == ["stage_started", "stage_finished"] and done.lines[-1]["ok"] is True
    # a stage that is complete is not launched again, and a later stage waits for the earlier ones
    with pytest.raises(LL.LaunchRefusal, match="already complete"):
        _drive(tmp_path, design, one, ["A1", "A2"], done)
    with pytest.raises(LL.LaunchRefusal, match="earlier stage"):
        _drive(tmp_path, design, design[2], ["H2"], done)
    assert len(done.specs) == 2  # neither refusal launched anything


def test_a_containers_error_is_recorded_by_type_and_the_others_finish(tmp_path):
    """Plan 4 of the research log, Section 4.1: any container's error is recorded and the other containers finish; and a relaunched stage
    adds to its ledger entry."""
    design = (_stage("one", "lead", "attack", 4),) + _design()[1:]
    one = design[0]
    batches = ["A1", "A2", "A3", "A4"]
    script = {"A1": (100.0, LR.GuardFailure("G4", "search|lead|A1|s9")), "A2": (200.0, LR.ContainerFailure("ValueError at lead_run.search_unit line 400", "lead|attack|A2")),
              "A3": (300.0, RuntimeError("a provider's own error, whose text 3.14159 is not kept")), "A4": (900.0, _job("lead|attack|A4", [_unit("u4")], 1, seconds=880.0))}
    first = Scripted(script, lives={"A1": 1, "A2": 1, "A3": 2})
    with pytest.raises(LL.LaunchRefusal, match="did not finish cleanly") as e:
        _drive(tmp_path, design, one, batches, first)
    assert not re.search(r"\d+\.\d+", str(e.value))
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    entry = ledger["stages"]["one"]
    launch = entry["launches"][0]
    assert entry["complete"] is False and entry["summary"]["errors"] == {
        "A1": "guard G4 failed in unit search|lead|A1|s9", "A2": "ValueError at lead_run.search_unit line 400 in container lead|attack|A2",
        "A3": "RuntimeError outside the container's own code"}
    assert "3.14159" not in (tmp_path / "ledger.json").read_text()
    assert {b: c["outcome"] for b, c in launch["calls"].items()} == {"A1": "error", "A2": "error", "A3": "error", "A4": "returned"}  # the fourth finished
    assert launch["calls"]["A4"]["counted_seconds"] == 880.0
    for b, wait in (("A1", 100.0), ("A2", 200.0), ("A3", 300.0)):  # a container that returned nothing is counted by the launcher's wait for it
        c = launch["calls"][b]
        assert c["returned_seconds"] is None and c["counted_seconds"] == c["wait_seconds"] and wait <= c["wait_seconds"] <= wait + 30
    assert launch["calls"]["A3"]["lives"] == 2 and launch["container_lives"] == 5  # every life counted, the rerun's too
    assert ledger["checks"] == [] and first.lines[-1]["ok"] is False  # no check after a stage that is not complete
    assert [c["container"] for c in json.loads((tmp_path / "runs_one_launch_1.json").read_text())["containers"]] == ["lead|attack|A4"]
    # the relaunch: every container again; the finished ones skip; the stage's seconds are both launches' added together
    again = Scripted({b: (60.0, _job(f"lead|attack|{b}", [_unit(f"u{b}", skipped=b == "A4")], 1, seconds=50.0 if b == "A4" else 500.0)) for b in batches})
    summary = _drive(tmp_path, design, one, batches, again, app_id="ap-two")
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    entry = ledger["stages"]["one"]
    assert summary["complete"] is True and entry["complete"] is True and [x["launch"] for x in entry["launches"]] == ["ap-one|one|1", "ap-two|one|2"]
    assert entry["launches"][0] == launch  # the first launch's entry is as it was
    assert entry["launches"][1]["function_seconds"] == 3 * 500.0 + 50.0
    assert LL.stage_seconds_on(ledger, "one") == launch["function_seconds"] + 1_550.0
    counts = LL.ledger_counts(ledger)
    assert counts == {"function_seconds": launch["function_seconds"] + 1_550.0, "container_lives": 9.0, "billed": None} and LL.ledger_apps(ledger) == ["ap-one", "ap-two"]
    (c1,) = ledger["checks"]
    assert c1["spent"]["function_seconds"] == counts["function_seconds"] and c1["measured_seconds"] == {"one": counts["function_seconds"]}
    assert (tmp_path / "runs_one_launch_1.json").is_file() and len(json.loads((tmp_path / "runs_one_launch_2.json").read_text())["containers"]) == 4
    assert json.loads((tmp_path / "runs_one.json").read_text())["launch"] == "ap-two|one|2"


def test_a_container_whose_first_life_did_not_return_is_counted_by_the_launchers_wait(tmp_path):
    """Plan 4 of the research log, Section 4.1, and Amendment 4: a container that died and was rerun by the provider returns its second
    life's seconds. The launcher counts its whole wait for it, and both lives' boots."""
    design = _design()
    rerun = Scripted({"A1": (400.0, _job("lead|attack|A1", [_unit("u1")], 1, seconds=380.0)), "A2": (900.0, _job("lead|attack|A2", [_unit("u2", skipped=True)], 1, seconds=70.0, attempts=2))})
    _drive(tmp_path, design, design[0], ["A1", "A2"], rerun)
    launch = json.loads((tmp_path / "ledger.json").read_text())["stages"]["one"]["launches"][0]
    a2 = launch["calls"]["A2"]
    assert (a2["attempts"], a2["lives"], a2["returned_seconds"]) == (2, 2, 70.0) and a2["counted_seconds"] == a2["wait_seconds"] >= 900.0
    assert launch["calls"]["A1"]["counted_seconds"] == 380.0 and launch["container_lives"] == 3
    assert launch["function_seconds"] == 380.0 + a2["wait_seconds"]
    assert LL.counted(500.0, {"attempts": 1, "seconds": 80.0}) == 80.0 and LL.counted(500.0, {"attempts": 2, "seconds": 80.0}) == 500.0
    assert LL.counted(500.0, {"attempts": 0, "seconds": 80.0}) == 500.0 and LL.counted(500.0, None) == 500.0  # a count that could not be kept is not trusted
    spent = LG.money(launch["function_seconds"], launch["container_lives"], LISTED)
    assert spent["at_the_listed_price_with_boot"] == pytest.approx(LISTED * (launch["function_seconds"] + 150.0) / 3600)  # three boots


def test_a_launcher_that_is_interrupted_or_dies_still_counts_what_it_launched(tmp_path):
    design = _design()
    one = design[0]
    interrupted = Scripted({"A1": (300.0, _job("lead|attack|A1", [_unit("u1")], 1, seconds=280.0)), "A2": (500.0, KeyboardInterrupt())})
    with pytest.raises(KeyboardInterrupt):
        _drive(tmp_path, design, one, ["A1", "A2"], interrupted)
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    launch = ledger["stages"]["one"]["launches"][0]
    assert launch["ended"] is not None and launch["calls"]["A1"]["outcome"] == "returned" and launch["calls"]["A2"]["outcome"] == "unreturned"
    assert launch["calls"]["A2"]["counted_seconds"] == launch["calls"]["A2"]["wait_seconds"] >= 500.0 and launch["function_seconds"] == 280.0 + launch["calls"]["A2"]["wait_seconds"]
    assert ledger["stages"]["one"]["complete"] is False
    # a launcher that died outright wrote no end: the next launch closes its entry from its last sign of life
    launch.update(ended=None, function_seconds=None, container_lives=None, last_alive=launch["spawned"]["A2"] + 240.0)
    del launch["calls"]["A2"]
    LL.write_json(tmp_path / "ledger.json", ledger)
    again = Scripted({b: (60.0, _job(f"lead|attack|{b}", [_unit(b)], 1, seconds=50.0)) for b in ("A1", "A2")})
    _drive(tmp_path, design, one, ["A1", "A2"], again, app_id="ap-two")
    closed = json.loads((tmp_path / "ledger.json").read_text())["stages"]["one"]["launches"][0]
    assert closed["ended"] == "closed by a later launch" and closed["calls"]["A2"]["outcome"] == "unreturned"
    assert closed["calls"]["A2"]["counted_seconds"] == 240.0 + 20.0 and closed["function_seconds"] == 280.0 + 260.0 and closed["container_lives"] == 2


def test_wave_1_is_followed_by_check_C2_and_the_guards_only_pass(tmp_path):
    """Plan 4 of the research log, Section 4.3: one held-out container runs to completion; check C2 takes the rest of the held-out side at
    the larger of its seconds and the projection; the guards-only pass must find every guard true before wave 2."""
    design = _design()
    one, two, three = design[:3]
    ok = lambda b, seconds: {b: (seconds + 5.0, _job(f"lead|x|{b}", [_unit(b)], 1, seconds=seconds))}  # noqa: E731
    _drive(tmp_path, design, one, ["A1", "A2"], Scripted({**ok("A1", 500.0), **ok("A2", 500.0)}))
    wave_1 = Scripted(ok("H1", 9_000.0), guards=ALL_TRUE)
    _drive(tmp_path, design, two, ["H1"], wave_1, app_id="ap-two")
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert [c["check"] for c in ledger["checks"]] == ["C1", "C2"] and wave_1.guards_asked == [{"arm": "lead"}]
    c2 = ledger["checks"][1]
    measured = {"one": 1_000.0, "two": 9_000.0}
    assert c2["measured_seconds"] == measured and c2["remaining"]["container_lives"] == 1 + 2 + 2
    assert c2["remaining"]["function_seconds"] == pytest.approx(LG.remaining_after_first_heldout(design, SPEC_TIMINGS, measured, 9_000.0))
    assert c2["remaining"]["function_seconds"] >= 9_000.0  # wave 2's one container at this container's seconds, which exceed the projection
    assert ledger["guards_pass"]["outcomes"] == ALL_TRUE and ledger["guards_pass"]["seconds"] == 3.0 and ledger["guards_pass"]["error"] is None
    assert LL.ledger_counts(ledger)["function_seconds"] == 1_000.0 + 9_000.0 + 3.0  # the pass's seconds are counted
    _drive(tmp_path, design, three, ["H2"], Scripted(ok("H2", 8_000.0)), app_id="ap-three")  # wave 2 goes, and check C3 follows it
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert [c["check"] for c in ledger["checks"]] == ["C1", "C2", "C3"] and ledger["checks"][2]["remaining"]["container_lives"] == 4
    assert ledger["checks"][2]["measured_seconds"] == {"one": 1_000.0, "two": 9_000.0, "three": 8_000.0}
    _drive(tmp_path, design, design[3], ["A1", "A2"], Scripted({**ok("A1", 500.0), **ok("A2", 500.0)}), app_id="ap-four")  # no check falls inside the delta-on arm
    assert [c["check"] for c in json.loads((tmp_path / "ledger.json").read_text())["checks"]] == ["C1", "C2", "C3"]


@pytest.mark.parametrize("found, named", [
    ({**ALL_TRUE, "G6": False}, "G6"),
    ({**ALL_TRUE, "G11_differs_from_the_heldout_batchs_own": False}, "G11_differs_from_the_heldout_batchs_own"),
    ({**ALL_TRUE, "G11_setting_is_the_attack_searchs": False}, "G11_setting_is_the_attack_searchs"),
    ({**ALL_TRUE, "G10": False, "shuffles_the_same_in_every_container": False}, "G10, shuffles_the_same_in_every_container"),
    ({k: v for k, v in ALL_TRUE.items() if k != "block_prep_fp_is_the_heldout_batchs"}, "block_prep_fp_is_the_heldout_batchs"),
    (LR.GuardFailure("units_complete", "guards|lead"), "guard units_complete failed in unit guards|lead"),
])
def test_a_guard_found_false_stops_the_run_before_wave_2(tmp_path, found, named):
    design = _design()
    ok = lambda b: {b: (105.0, _job(f"lead|x|{b}", [_unit(b)], 1, seconds=100.0))}  # noqa: E731
    _drive(tmp_path, design, design[0], ["A1", "A2"], Scripted({**ok("A1"), **ok("A2")}))
    with pytest.raises(LL.LaunchRefusal) as e:
        _drive(tmp_path, design, design[1], ["H1"], Scripted(ok("H1"), guards=found), app_id="ap-two")
    assert str(e.value) == f"the run stops here: the guards-only pass: {named}. Stop and report"  # the guard's name, and no value
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["stages"]["two"]["complete"] is True and ledger["stopped_by"] == [f"the guards-only pass: {named}"]  # the container's work stands; the run does not go on
    assert ledger["stops"][0]["after_stage"] == "two" and ledger["stops"][0]["by"] == ledger["stopped_by"]
    wave_2 = Scripted(ok("H2"))
    with pytest.raises(LL.LaunchRefusal, match="guards-only pass has not passed"):
        _drive(tmp_path, design, design[2], ["H2"], wave_2, app_id="ap-three")
    with pytest.raises(LL.LaunchRefusal):  # and the run has no flag that would let it through
        _drive(tmp_path, design, design[2], ["H2"], wave_2, app_id="ap-three", accept_expected_refusals=True)
    assert wave_2.specs == []


def test_a_guards_only_pass_that_failed_to_run_is_taken_again_before_wave_2(tmp_path):
    """The pass's own failure is no finding about the units. It stops the run by name, and the next launch of wave 2
    takes the pass again before any container starts."""
    design = _design()
    ok = lambda b: {b: (105.0, _job(f"lead|x|{b}", [_unit(b)], 1, seconds=100.0))}  # noqa: E731
    _drive(tmp_path, design, design[0], ["A1", "A2"], Scripted({**ok("A1"), **ok("A2")}))
    with pytest.raises(LL.LaunchRefusal) as e:
        _drive(tmp_path, design, design[1], ["H1"], Scripted(ok("H1"), guards=ConnectionError("the provider's text, 0.25")), app_id="ap-two")
    assert str(e.value) == "the run stops here: the guards-only pass: ConnectionError outside the pass's own code. Stop and report"
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["guards_pass"]["error"] == "ConnectionError outside the pass's own code" and ledger["guards_pass"]["outcomes"] == {}
    still = Scripted(ok("H2"), guards={**ALL_TRUE, "G6": False})  # taken again, and this time it finds a guard false
    with pytest.raises(LL.LaunchRefusal, match="has not passed"):
        _drive(tmp_path, design, design[2], ["H2"], still, app_id="ap-three")
    assert still.specs == [] and len(still.guards_asked) == 1 and json.loads((tmp_path / "ledger.json").read_text())["guards_pass"]["outcomes"]["G6"] is False
    found = Scripted(ok("H2"), guards=ALL_TRUE)  # a finding stands: the pass is not taken a third time
    with pytest.raises(LL.LaunchRefusal, match="has not passed"):
        _drive(tmp_path, design, design[2], ["H2"], found, app_id="ap-three")
    assert found.guards_asked == [] and found.specs == []
    # in another run, the pass that failed to run is taken again, passes, and wave 2 goes
    tmp = tmp_path / "again"
    tmp.mkdir()
    _drive(tmp, design, design[0], ["A1", "A2"], Scripted({**ok("A1"), **ok("A2")}))
    with pytest.raises(LL.LaunchRefusal):
        _drive(tmp, design, design[1], ["H1"], Scripted(ok("H1"), guards=ConnectionError()), app_id="ap-two")
    wave_2 = Scripted(ok("H2"), guards=ALL_TRUE)
    assert _drive(tmp, design, design[2], ["H2"], wave_2, app_id="ap-three")["complete"] is True
    assert len(wave_2.guards_asked) == 1 and json.loads((tmp / "ledger.json").read_text())["guards_pass"]["error"] is None


def test_a_rehearsal_accepts_exactly_the_refusals_one_batch_on_both_sides_must_give(tmp_path):
    """Plan 4 of the research log, Section 6.1: with each batch on both sides the pass reports G6 and G11 false and the launcher stops; wave
    2 then launches under a rehearsal-only flag that accepts exactly those refusals and no other."""
    design = _design("rehearsal_")
    ok = lambda b: {b: (105.0, _job(f"rehearsal|x|{b}", [_unit(b)], 1, seconds=100.0))}  # noqa: E731
    patterns = {"as expected": (ONE_BATCH_ON_BOTH_SIDES, True), "only G6 false": ({**ONE_BATCH_ON_BOTH_SIDES, "G11_differs_from_the_heldout_batchs_own": True}, False),
                "another guard false as well": ({**ONE_BATCH_ON_BOTH_SIDES, "G10": False}, False),
                "not every vector equal": ({**ONE_BATCH_ON_BOTH_SIDES, "G6_reports_every_carried_vector_equal": False}, False), "all true": (ALL_TRUE, False)}
    for k, (name, (found, accepted)) in enumerate(patterns.items()):
        tmp = tmp_path / str(k)
        tmp.mkdir()
        _drive(tmp, design, design[0], ["C1", "C2"], Scripted({**ok("C1"), **ok("C2")}))
        if name == "all true":
            _drive(tmp, design, design[1], ["C1"], Scripted(ok("C1"), guards=found), app_id="ap-two")
        else:
            with pytest.raises(LL.LaunchRefusal, match="the run stops here: the guards-only pass"):
                _drive(tmp, design, design[1], ["C1"], Scripted(ok("C1"), guards=found), app_id="ap-two")
        assert LL.guards_acceptable(found, True) is accepted, name
        wave_2 = Scripted(ok("C2"))
        if accepted:
            with pytest.raises(LL.LaunchRefusal, match="has not passed"):  # without the flag it stays stopped
                _drive(tmp, design, design[2], ["C2"], wave_2, app_id="ap-three")
            _drive(tmp, design, design[2], ["C2"], wave_2, app_id="ap-three", accept_expected_refusals=True)
            launches = json.loads((tmp / "ledger.json").read_text())["stages"]["three"]["launches"]
            assert [x["accepted_expected_refusals"] for x in launches] == [True]
        else:
            with pytest.raises(LL.LaunchRefusal, match="has not passed"):
                _drive(tmp, design, design[2], ["C2"], wave_2, app_id="ap-three", accept_expected_refusals=True)
            assert wave_2.specs == [], name
    # in the run, the flag is refused whatever the pass found, and so is a trigger
    run = _design()
    tmp = tmp_path / "run"
    tmp.mkdir()
    ok = lambda b: {b: (105.0, _job(f"lead|x|{b}", [_unit(b)], 1, seconds=100.0))}  # noqa: E731
    _drive(tmp, run, run[0], ["A1", "A2"], Scripted({**ok("A1"), **ok("A2")}))
    _drive(tmp, run, run[1], ["H1"], Scripted(ok("H1"), guards=ALL_TRUE), app_id="ap-two")
    for kw in ({"accept_expected_refusals": True}, {"trigger": "stop"}):
        with pytest.raises(LL.LaunchRefusal, match="rehearsal alone"):
            _drive(tmp, run, run[2], ["H2"], Scripted(ok("H2")), app_id="ap-three", **kw)


def test_a_check_over_the_cap_stops_the_run(tmp_path):
    design = _design()
    ok = lambda b, seconds=100.0: {b: (seconds + 5.0, _job(f"lead|x|{b}", [_unit(b)], 1, seconds=seconds))}  # noqa: E731
    cheap = {**ok("A1"), **ok("A2")}
    with pytest.raises(LL.LaunchRefusal, match=r"^the run stops here: C1\. Stop and report$"):
        _drive(tmp_path, design, design[0], ["A1", "A2"], Scripted(cheap), cap=2.0)  # about 55 cents spent and 1.75 dollars to come
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert ledger["checks"][0]["exceeds_cap"] is True and ledger["checks"][0]["cap"] == 2.0 and ledger["stopped_by"] == ["C1"]
    assert 2.0 < ledger["checks"][0]["projected_dollars"] < 2.6 and ledger["stages"]["one"]["complete"] is True  # the stage's work stands
    nothing = Scripted(ok("H1"), guards=ALL_TRUE)
    with pytest.raises(LL.LaunchRefusal, match="spend check has stopped the run"):
        _drive(tmp_path, design, design[1], ["H1"], nothing, app_id="ap-two")
    assert nothing.specs == []
    # money spent outside this ledger that the cap covers, the rehearsals', is in every check, and their apps' bills are read
    tmp = tmp_path / "with"
    tmp.mkdir()
    asked: list[dict] = []

    def rehearsals(bill: dict) -> dict:
        asked.append(bill)
        return {"function_seconds": 1_600.0, "container_lives": 14.0, "billed": bill.get("by_app", {}).get("ap-rehearsal"), "app_ids": ["ap-rehearsal"]}

    paid = Scripted(cheap, bill={"ap-rehearsal": 3.5, "ap-one": 0.25})
    _drive(tmp, design, design[0], ["A1", "A2"], paid, outside=rehearsals)
    c1 = json.loads((tmp / "ledger.json").read_text())["checks"][0]
    assert c1["spent"]["function_seconds"] == 1_800.0 and c1["spent"]["container_lives"] == 16.0 and c1["spent"]["billed"] == 3.75
    assert asked[-1]["by_app"] == {"ap-rehearsal": 3.5, "ap-one": 0.25}


def test_check_c0_is_on_the_runs_ledger_before_its_first_job(tmp_path):
    under = LG.check_c0(SPEC_TIMINGS, LISTED, {"function_seconds": 1_600.0, "container_lives": 14, "billed": None})
    LL.record_c0(tmp_path / "ledger.json", under)
    assert [c["check"] for c in json.loads((tmp_path / "ledger.json").read_text())["checks"]] == ["C0"]
    over = LG.check_c0(SPEC_TIMINGS, LISTED, {"function_seconds": 1_600.0, "container_lives": 14, "billed": None}, cap=90.0)
    with pytest.raises(LL.LaunchRefusal, match="check C0"):
        LL.record_c0(tmp_path / "ledger.json", over)
    ledger = json.loads((tmp_path / "ledger.json").read_text())
    assert [c["check"] for c in ledger["checks"]] == ["C0"] and ledger["checks"][0]["exceeds_cap"] is True  # taken again, it replaces the earlier reading
    design = _design()
    nothing = Scripted({"A1": (5.0, _job("lead|attack|A1", [_unit("a")], 1))})
    with pytest.raises(LL.LaunchRefusal, match="spend check has stopped the run"):  # and over the cap, no stage launches
        _drive(tmp_path, design, design[0], ["A1"], nothing)
    assert nothing.specs == [] and LL.began_at(tmp_path / "ledger.json") is None


def test_the_rehearsals_cost_is_counted_from_their_records(tmp_path):
    """Amendment 4, Section 2: the cap covers the rehearsals. The first is counted from its record, with its
    three container lives; each repeat from its ledger and its assembly."""
    assert LL.rehearsal_counts(tmp_path) == {"function_seconds": 0.0, "container_lives": 0.0, "billed": None, "app_ids": []}
    (tmp_path / "rehearsal").mkdir()
    LL.write_json(tmp_path / "rehearsal" / "rehearsal.json", {"app_id": "ap-first", "function_seconds": 428.6})
    first = LL.rehearsal_counts(tmp_path, {"by_app": {"ap-first": 0.7509}})
    assert first == {"function_seconds": 428.6, "container_lives": 3.0, "billed": 0.7509, "app_ids": ["ap-first"]}
    assert LG.money(first["function_seconds"], first["container_lives"], LISTED, first["billed"])["dollars"] == pytest.approx(1.05, abs=0.005)  # Amendment 4's figure
    design = _design("rehearsal_")
    folder = tmp_path / "rehearsal_2"
    folder.mkdir()
    ok = lambda b: {b: (105.0, _job(f"rehearsal|x|{b}", [_unit(b)], 1, seconds=100.0))}  # noqa: E731
    _drive(folder, design, design[0], ["C1", "C2"], Scripted({**ok("C1"), **ok("C2")}), app_id="ap-a")
    with pytest.raises(LL.LaunchRefusal):
        _drive(folder, design, design[1], ["C1"], Scripted(ok("C1"), guards=ONE_BATCH_ON_BOTH_SIDES), app_id="ap-b")
    LL.write_json(folder / "assemble.json", {"app_id": "ap-c", "arms": {"x": {"seconds": 11.0}, "y": {"seconds": 9.0}}})
    both = LL.rehearsal_counts(tmp_path, {"by_app": {"ap-first": 0.7509, "ap-a": 0.5, "ap-c": 0.01, "ap-unrelated": 50.0}})
    assert both["function_seconds"] == pytest.approx(428.6 + 300.0 + 3.0 + 20.0) and both["container_lives"] == 6.0  # the guards-only pass and the assemblers, as seconds
    assert both["billed"] == pytest.approx(0.7509 + 0.5 + 0.01) and both["app_ids"] == ["ap-a", "ap-b", "ap-c", "ap-first"]
    assert LL.rehearsal_counts(tmp_path)["billed"] is None  # no bill read: none counted


def _returns(stage: str, commit_seconds: float = 600.0) -> dict[str, tuple[float, dict]]:
    """What a deciding stage's containers return, scripted: every unit of each, by its real name."""
    s = LG.stage_named(stage)
    script = {}
    for batch in DECIDING[stage]:
        units = [_unit(f"search|{s.arm}|{batch}|s{k}") for k in LR.STARTS]
        if s.side == "heldout":
            units += [_unit(f"block|{s.arm}|{batch}|{a}|s{k}") for a in LL.BATCHES[s.arm]["attack"] for k in LR.STARTS]
        script[batch] = (commit_seconds + 5.0, _job(f"{s.arm}|{s.side}|{batch}", units, len(units), seconds=commit_seconds))
    return script


def test_the_deciding_runs_commands_in_order_with_a_scripted_cloud(tmp_path, monkeypatch):
    """Plan 4 of the research log, Section 7: the five stages in order, then the plans of what to assemble and what to copy. The containers
    are scripted; what the launcher asks of them, and what it refuses, is the run's."""
    results = tmp_path / "s5_lead"
    commit = "d" * 40
    monkeypatch.setattr(LL, "RESULTS", results)
    monkeypatch.setattr(LL, "check_deciding_commit", lambda c, rehearsal_commit: None)  # the repository's checks have their own test
    assert set(LL.REHEARSAL_EXPECTED_TIMINGS) == set(LG.TIMING_KEYS)
    LL.write_json(results / "rehearsal" / "rehearsal.json", {"app_id": "ap-first", "function_seconds": 428.6})
    with pytest.raises(LL.LaunchRefusal, match="no repeat rehearsal"):  # no deciding stage without a repeat rehearsal that met every outcome
        LL.stage_command("lead_attack", commit, 0, Scripted({}).cloud(), listed_hourly_price=LISTED)
    LL.write_json(results / "rehearsal_2" / "ledger.json", {"stages": {"x": {"launches": [{"app_id": "ap-r", "function_seconds": 1_200.0, "container_lives": 11}]}},
                                                            "guards_pass": {"app_id": "ap-r", "seconds": 4.0}})
    record = {"all_required_outcomes_met": False, "commit": commit, "timings": SPEC_TIMINGS, "check_C0": {"assemble_seconds": 30.0}}
    LL.write_json(results / "rehearsal_2" / "rehearsal.json", record)
    with pytest.raises(LL.LaunchRefusal, match="did not meet"):
        LL.stage_command("lead_attack", commit, 0, Scripted({}).cloud(), listed_hourly_price=LISTED)
    LL.write_json(results / "rehearsal_2" / "rehearsal.json", {**record, "all_required_outcomes_met": True})
    for kw in ({"trigger": "stop"}, {"accept_expected_refusals": True}):  # neither is the run's
        with pytest.raises(LL.LaunchRefusal, match="rehearsal alone"):
            LL.stage_command("lead_attack", commit, 0, Scripted({}).cloud(), listed_hourly_price=LISTED, **kw)
    assert not (results / "ledger.json").exists()

    # 1. the lead's attack side: check C0 first, on the ledger before any job, with the rehearsals' cost and bills; then 16 containers, and check C1
    first = Scripted(_returns("lead_attack", 700.0), bill={"ap-first": 0.7509, "ap-r": 2.2})
    assert LL.stage_command("lead_attack", commit, 0, first.cloud("ap-1"), listed_hourly_price=LISTED)["complete"] is True
    ledger = json.loads((results / "ledger.json").read_text())
    c0, c1 = ledger["checks"]
    assert (c0["check"], c1["check"]) == ("C0", "C1") and c0["assemble_seconds"] == 30.0 and c0["bill_read_at"] == "2026-10-06T18:00:00+00:00"
    assert c0["spent"]["function_seconds"] == pytest.approx(428.6 + 1_204.0) and c0["spent"]["container_lives"] == 14 and c0["spent"]["billed"] == pytest.approx(2.9509)
    assert c0["cap"] == c1["cap"] == 150.0 and c0["run"]["container_lives"] == 48 and set(c0["stages"]) == set(DECIDING)
    assert [s["batch"] for s in first.specs] == DECIDING["lead_attack"] and all(s["mode"] == "deciding" and s["launch"] == "ap-1|lead_attack|1" for s in first.specs)
    assert c1["spent"]["function_seconds"] == pytest.approx(428.6 + 1_204.0 + 16 * 700.0) and c1["spent"]["container_lives"] == 30  # the rehearsals are in every check
    assert c1["remaining"]["container_lives"] == 32 and LL.began_at(results / "ledger.json") == commit
    with pytest.raises(LL.LaunchRefusal, match="began at another commit"):  # one commit for the whole run
        LL.stage_command("lead_heldout_1", "e" * 40, 0, Scripted({}).cloud(), listed_hourly_price=LISTED)
    # 2. wave 1: H1 alone; check C2; the guards-only pass on H1's blocks against all sixteen attack batches' searches
    wave_1 = Scripted(_returns("lead_heldout_1", 1_900.0), guards=ALL_TRUE)
    LL.stage_command("lead_heldout_1", commit, 0, wave_1.cloud("ap-2"), listed_hourly_price=LISTED)
    assert [s["batch"] for s in wave_1.specs] == ["H1"] and wave_1.specs[0]["attack_batches"] == LL.BATCHES["lead"]["attack"]
    assert wave_1.guards_asked == [{"arm": "lead", "units": "/cache/s5_lead/lead/sealed/units", "attack": LL.BATCHES["lead"]["attack"], "heldout": ["H1"],
                                    "starts": [9, 10, 11, 12, 13], "commit": commit, "rehearsal": False}]
    c2 = json.loads((results / "ledger.json").read_text())["checks"][2]
    per_container = LG.stage_seconds("lead_heldout_2", SPEC_TIMINGS)["total"] / 15  # at the table specification's timings, 45 + 611 + 5,975 passes at 0.18 s
    assert c2["check"] == "C2" and c2["remaining"]["container_lives"] == 31 and per_container == pytest.approx(1_731.5)
    assert c2["remaining"]["function_seconds"] >= 15 * 1_900.0  # the other fifteen at this container's seconds, the larger of the two
    # 3. wave 2: the other fifteen; check C3 before the delta-on arm
    wave_2 = Scripted(_returns("lead_heldout_2", 1_900.0))
    LL.stage_command("lead_heldout_2", commit, 0, wave_2.cloud("ap-3"), listed_hourly_price=LISTED)
    assert [s["batch"] for s in wave_2.specs] == DECIDING["lead_heldout_2"] and wave_2.guards_asked == []
    # 4. the delta-on arm
    for k, name in enumerate(("delta_attack", "delta_heldout")):
        s = Scripted(_returns(name))
        LL.stage_command(name, commit, 0, s.cloud(f"ap-{4 + k}"), listed_hourly_price=LISTED)
        assert [x["batch"] for x in s.specs] == DECIDING[name] and all(x["root"] == "/cache/s5_lead/delta_on" for x in s.specs)
    ledger = json.loads((results / "ledger.json").read_text())
    assert [c["check"] for c in ledger["checks"]] == ["C0", "C1", "C2", "C3"] and all(ledger["stages"][n]["complete"] for n in DECIDING)
    assert LL.ledger_counts(ledger)["container_lives"] == 48 and sorted(p.name for p in results.glob("runs_*.json")) == sorted(
        [f"runs_{n}.json" for n in DECIDING] + [f"runs_{n}_launch_1.json" for n in DECIDING])

    # 5. what to assemble: the lead's table and the delta-on arm's, paired with it; every unit's hash as its container returned it
    lead, delta = LL.assemble_plan(commit, 0, results)
    assert (lead["key"], delta["key"], lead["pairs_with"], delta["pairs_with"]) == ("lead", "delta_on", None, "lead") and lead["results"] == results / "lead"
    spec = lead["spec"]
    assert (spec["arm"], spec["units"], spec["table"], spec["starts"], spec["commit"]) == ("lead", "/cache/s5_lead/lead/sealed/units", "table", [9, 10, 11, 12, 13], commit)
    assert spec["attack"] == LL.BATCHES["lead"]["attack"] and spec["heldout"] == LL.BATCHES["lead"]["heldout"] and len(spec["containers"]) == 32
    assert not any(k in spec for k in ("rehearsal", "part_bytes", "pilot", "heldout_units"))  # a deciding table is assembled with nothing a rehearsal's may have
    assert len(spec["returned_sha256"]["attack"]) == 80 and len(spec["returned_sha256"]["heldout"]) == 80 + 1_280  # every search and every block
    assert len(spec["text_ids_H"]) == 16 and len(spec["excluded"]) == 11
    assert len(delta["spec"]["returned_sha256"]["heldout"]) == 40 + 320 and delta["spec"]["heldout"] == LL.BATCHES["delta_on"]["heldout"]
    seen: list[dict] = []

    def assembler(spec: dict) -> dict:
        seen.append(spec)
        core = f"the core file of {spec['arm']}".encode()
        return {"arm": spec["arm"], "files": [{"name": "table_core.npz", "sha256": hashlib.sha256(core).hexdigest()}], "design": {}, "complete": True, "run_commit": commit,
                "outcomes": {"G6": True}, "prep_fp_equal_to_lead": None, "prep_fp": {"attack": {"A1": f"fp-{spec['arm']}"}, "heldout": {}},
                "table_dir": spec["root"] + "/sealed/table", "seconds": 40.0}

    lines: list[dict] = []
    LL.assemble_command(commit, 0, assemble=assembler, read_file=lambda remote: f"the core file of {remote.split('/')[3]}".encode(), app_id="ap-6",
                        log=lambda **f: lines.append(LR.log_record(**f)))
    assert "lead_prep_fp" not in seen[0] and seen[1]["lead_prep_fp"] == {"attack": {"A1": "fp-lead"}, "heldout": {}}  # the delta-on arm is handed the lead's fingerprints
    assert sorted(json.loads((results / "assemble.json").read_text())["arms"]) == ["delta_on", "lead"] and [ln["container"] for ln in lines] == ["lead", "delta_on"]
    for arm in ("lead", "delta_on"):  # each table where the analysis's entry point looks for it, with its notice and its receipt
        assert (results / arm / "sealed" / "table_core.npz").read_bytes() == f"the core file of {arm}".encode()
        assert (results / arm / "sealed" / "DO_NOT_OPEN.md").is_file() and json.loads((results / arm / "receipt.json").read_text())["run_commit"] == commit
    # and what to copy: all 240 searches, by arm
    groups = LL.backup_plan(commit, 0, results)
    assert [(g["name"], g["remote"], len(g["units"])) for g in groups] == [("lead", "/cache/s5_lead/lead/sealed/units", 160), ("delta_on", "/cache/s5_lead/delta_on/sealed/units", 80)]
    files = {f"/cache/s5_lead/{g['name']}/sealed/units/search_{u.split('|')[2]}_{u.split('|')[3]}.npz": u.encode() for g in groups for u in g["units"]}
    monkeypatch.setattr(LL, "BACKUP", tmp_path / "backup")
    with pytest.raises(LL.LaunchRefusal, match="do not have the hash"):  # bytes that are not the ones a container returned
        LL.backup_command(commit, 0, read_file=lambda remote: b"other bytes", log=lambda **f: None)
    # here a unit's bytes are its name, and its returned hash is the hash of its name
    copied = LL.backup_command(commit, 0, read_file=lambda remote: files[remote], log=lambda **f: lines.append(LR.log_record(**f)))
    assert len(copied) == 240 and (tmp_path / "backup" / "run" / "lead" / "search_H16_s13.npz").read_bytes() == b"search|lead|H16|s13"
    assert all((tmp_path / "backup" / "run" / d / "DO_NOT_OPEN.md").read_text() == LR.NOTICE for d in (".", "lead", "delta_on"))
    assert json.loads((results / "backup.json").read_text())["notice"] == "DO_NOT_OPEN.md" and lines[-1] == {"event": "backup_finished", "container": "units", "count": 240}


# ----------------------------------------------------------------------------- the whole repeat rehearsal, on the tiny model


N_TEXTS = 16
COMMIT = "5e" * 20


class Killed(Exception):
    pass


class TinyCloud:
    """The cloud, for the tiny model on a CPU: a folder for the volume, a dictionary for the control dictionary, and
    containers that run `lead_run.run_spec` when asked for their result. A killed container is rerun, as the provider
    reruns an input whose container died. `at_once` makes a container see the stop flag only once its own first unit
    is done, as two containers started together do; without it the second container starts after the first has set it."""

    def __init__(self, at_once: bool) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, self.model.module_to_c[k]) for k in self.model.target_module_paths]
        g = torch.Generator().manual_seed(11)
        self.starts = {1: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in self.lay}}
        self.ids = {"C1": tiny_ids(N_TEXTS, seed=7).numpy(), "C2": tiny_ids(N_TEXTS, seed=8).numpy()}
        self.rows = {b: LR.sha_rows(x) for b, x in self.ids.items()}
        self.strata = {k: np.random.default_rng(5).integers(0, 3, C) for k, C in self.lay}
        self.at_once, self.control, self.lives, self.apps, self.lines, self.tasks = at_once, {}, {}, 0, [], 0

    def pilot(self, batch: str) -> dict:
        """What the pilot's record is to the real rehearsal: the same search by the plain loop and the plain hook."""
        hook = A.SaveHook(steps=P.BUDGETS, thresholds=P.STAGES)
        r = A.run(self.model, A.prepare(self.model, self.ids[batch], "fp32", device="cpu"), self.starts[1], 320, 0.1, save_hook=hook, device="cpu")
        return {"record": r["record"], "saved_sources_sha256": {n: LR.setting_sha256(v) for n, v in hook.saved.items()}, "hook_events": dict(hook.events)}

    def run(self, spec: dict) -> dict:
        key = f"{spec['launch']}|{spec['batch']}"
        while True:
            self.lives[key] = self.lives.get(key, 0) + 1
            self.tasks += 1
            task, mine = f"task-{self.tasks}", {"units": 0}

            def kill() -> None:
                if spec["kill_key"] not in self.control:
                    self.control[spec["kill_key"]] = task
                    raise Killed

            trigger = LR.rehearsal_trigger(spec, set_stop=lambda: self.control.__setitem__(f"stop|{spec['run']}", True), kill=kill)

            def fault(point: str) -> None:
                if point == "between_units":
                    mine["units"] += 1
                if trigger is not None:
                    trigger(point)

            def should_stop() -> bool:
                return bool(self.control.get(f"stop|{spec['run']}")) and (not self.at_once or mine["units"] >= 1)

            LR.check_spec(spec, trigger is not None)
            try:
                out = LR.run_spec(self.model, spec, self.ids[spec["batch"]], self.rows[spec["batch"]], self.starts, self.strata, self.lay,
                                  environment={"task": task}, log=lambda **f: self.lines.append(LR.log_record(**f)), commit_volume=lambda: None,
                                  should_stop=should_stop, fault=fault if (trigger is not None or self.at_once) else None, device="cpu", precision="fp32")
            except Killed:
                continue
            out["attempts"] = self.lives[key]
            return out

    def cloud(self) -> LL.Cloud:
        self.apps += 1
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec

            def get(self, timeout: float) -> dict:
                return me.run(self.spec)

        return LL.Cloud(spawn=Now, set_stop=lambda value: self.control.__setitem__(f"stop|{self.run_key}", bool(value)),
                        attempts=lambda spec: self.lives.get(f"{spec['launch']}|{spec['batch']}", 0),
                        read_bill=lambda apps: {"read_at": "2026-10-06T19:00:00+00:00", "by_app": {a: 0.7509 for a in apps if a == "ap-first"}},
                        guards=lambda spec: {"outcomes": LR.guards_from_spec(spec), "seconds": 0.5}, app_id=f"ap-{self.apps}",
                        log=lambda **f: self.lines.append(LR.log_record(**f)))

    run_key = "rehearsal_2"


@pytest.mark.parametrize("at_once", [True, False])
def test_the_repeat_rehearsal_on_the_tiny_model_through_the_commands(tmp_path, monkeypatch, at_once):
    """Plan 4 of the research log, Section 6: the rehearsal's commands, in order, with the tiny model for the cloud. Every row of its table
    is met, the record is written, and check C0 is computed for the run. What each stage must do is asserted as it goes."""
    tiny = TinyCloud(at_once)
    results, volume = tmp_path / "results" / "s5_lead", tmp_path / "cache" / "s5_lead"
    monkeypatch.setattr(LL, "RESULTS", results)
    monkeypatch.setattr(LL, "BACKUP", tmp_path / "backup")
    monkeypatch.setattr(LL, "VOLUME_S5", str(volume))
    monkeypatch.setattr(LL, "check_rehearsal_commit", lambda commit, earlier: None)  # no repository here
    monkeypatch.setattr(LR, "check_configuration", lambda ctx, starts: None)  # nor a B200
    monkeypatch.setattr(LL, "heldout_texts", lambda heldout: ([[f"{b}_t{k}" for k in range(N_TEXTS)] for b in heldout], []))
    monkeypatch.setattr(LL, "inputs_sha256", lambda: {"manifest": "m", "starts": "s", "strata": "x", "heldout_span_overlap": "o"})
    pilots = {b: tiny.pilot(b) for b in LL.REHEARSAL_BATCHES}
    monkeypatch.setattr(LL, "pilot_search", lambda batch, start: pilots[batch])
    LL.write_json(results / "rehearsal" / "rehearsal.json", {"app_id": "ap-first", "function_seconds": 428.6})  # the first rehearsal's record
    folder = results / "rehearsal_2"
    root = volume / "rehearsal" / f"{COMMIT[:12]}_2" / "sealed"

    def stage(name: str, **kw) -> dict:
        return LL.stage_command(name, COMMIT, 2, tiny.cloud(), listed_hourly_price=LISTED, **kw)

    def ledger() -> dict:
        return json.loads((folder / "ledger.json").read_text())

    # 1. the attack role, C1 and C2 at once
    assert stage("rehearsal_attack")["complete"] is True
    assert sorted(p.name for p in (root / "units_attack").iterdir()) == ["search_C1_s1.npz", "search_C1_s1.npz.done", "search_C2_s1.npz", "search_C2_s1.npz.done"]
    assert (root / "DO_NOT_OPEN.md").read_text() == LR.NOTICE and [c["check"] for c in ledger()["checks"]] == ["C1"]
    with pytest.raises(LL.LaunchRefusal, match="earlier stage"):
        stage("rehearsal_heldout_2", accept_expected_refusals=True)
    # 2. the held-out role, wave 1: C1 alone; then check C2 and the guards-only pass, which must refuse, and the launcher stops
    with pytest.raises(LL.LaunchRefusal) as e:
        stage("rehearsal_heldout_1")
    assert str(e.value) == "the run stops here: the guards-only pass: G11_differs_from_the_heldout_batchs_own, G6. Stop and report"
    assert LL.guards_acceptable(ledger()["guards_pass"]["outcomes"], True) and ledger()["stages"]["rehearsal_heldout_1"]["complete"] is True
    # 3. wave 2: C2 alone, under the flag that accepts exactly those refusals
    with pytest.raises(LL.LaunchRefusal, match="has not passed"):
        stage("rehearsal_heldout_2")
    assert stage("rehearsal_heldout_2", accept_expected_refusals=True)["complete"] is True
    assert [c["check"] for c in ledger()["checks"]] == ["C1", "C2", "C3"]
    # 4. the delta-on attack role, 20 steps
    assert stage("rehearsal_delta_attack")["complete"] is True
    with np.load(root / "units_delta_attack" / "search_C1_s1.npz") as z:
        assert z["record"].shape == (21,)
    # 5. the delta-on held-out role: the stop, then the relaunch with the kill
    with pytest.raises(LL.LaunchRefusal, match="did not finish cleanly"):
        stage("rehearsal_delta_heldout", trigger="stop")
    assert tiny.control["stop|rehearsal_2"] is True
    first = ledger()["stages"]["rehearsal_delta_heldout"]["launches"][0]["calls"]
    assert all(c["stopped"] is True for c in first.values()) and [first[b]["finished_units"] for b in ("C1", "C2")] == ([1, 1] if at_once else [1, 0])
    assert not list((root / "units_delta_heldout").glob("block_*"))
    assert stage("rehearsal_delta_heldout", trigger="kill")["complete"] is True
    assert tiny.control["stop|rehearsal_2"] is False and len([k for k in tiny.control if k.startswith("killed|")]) == 1  # the flag cleared; one kill
    held = ledger()["stages"]["rehearsal_delta_heldout"]["launches"]
    assert (held[1]["calls"]["C1"]["lives"], held[1]["calls"]["C2"]["lives"], held[1]["container_lives"]) == (2, 1, 3)
    with pytest.raises(LL.LaunchRefusal, match="already complete"):
        stage("rehearsal_delta_heldout")
    # the commands after the stages
    cloud = tiny.cloud()
    arms = LL.assemble_command(COMMIT, 2, assemble=lambda spec: {**LR.assemble_from_spec(spec), "seconds": 1.5}, read_file=lambda remote: Path(remote).read_bytes(),
                               app_id=cloud.app_id, log=cloud.log)
    assert sorted(arms) == ["C1_rehearsal", "C1_rehearsal_delta_on", "C2_rehearsal", "C2_rehearsal_delta_on"]
    assert arms["C1_rehearsal_delta_on"]["prep_fp_equal_to_lead"] == {"attack": {"C1": True}, "heldout": {"C1": True}} and arms["C1_rehearsal"]["prep_fp_equal_to_lead"] is None
    assert [f["name"] for f in arms["C2_rehearsal"]["receipt"]["files"]] == ["table_core.npz", "table_per_text_01.npz", "table_per_text_02.npz"]
    assert (folder / "C2_rehearsal" / "sealed" / "DO_NOT_OPEN.md").is_file()
    copied = LL.backup_command(COMMIT, 2, read_file=lambda remote: Path(remote).read_bytes(), log=cloud.log)
    assert len(copied) == 8 and (tmp_path / "backup" / "rehearsal_2" / "DO_NOT_OPEN.md").read_text() == LR.NOTICE
    for name, sha in copied.items():
        assert LT.sha256_file(tmp_path / "backup" / "rehearsal_2" / name) == sha and (tmp_path / "backup" / "rehearsal_2" / Path(name).parent / "DO_NOT_OPEN.md").is_file()
    tiny.lines.clear()
    tables = LL.validate_command(2, log=cloud.log)
    wrong_batch = ["axis_labels", "heldout_ids_differ_from_attack_ids", "carried_differs_from_own_batch_values"]
    assert tables["C1_rehearsal"]["failed"] == wrong_batch and tables["C2_rehearsal"]["failed"] == wrong_batch and tables["C1_rehearsal"]["parts"] == 2
    assert set(wrong_batch) < set(tables["C1_rehearsal_delta_on"]["failed"]) and "fixed_steps" in tables["C1_rehearsal_delta_on"]["failed"]  # a 20-step search has no step 40
    assert len(tiny.lines) == 4 * len(LT.CHECKS + LT.LOADER_CHECKS) and all(set(ln) == {"event", "unit", "guard", "ok"} for ln in tiny.lines)  # names with pass or fail, and no value
    record = LL.record_command(2, listed={"source": "a test"}, listed_hourly_price=LISTED, read_bill=cloud.read_bill, killed=tiny.control.get, log=cloud.log)

    # every row of plan 4 of the research log's Section 6, and plan 2 of the research log's Section 7 with them
    outcomes = record["required_outcomes"]
    assert sorted(outcomes) == sorted([
        "row_1_two_containers_at_once_in_each_role", "row_2_kill_inside_a_unit", "row_3_stop_then_relaunch", "row_4_two_waves_and_the_guards_only_pass",
        "row_5_assemble_and_backup", "row_6_two_per_text_parts", "row_7_validate_only", "row_8_timings", "row_9_search_equal_to_the_pilots",
        "heldout_role_equal_to_the_pilots_and_to_the_attack_role", "every_units_guards_true", "delta_entries_held_in_the_delta_on_searches",
        "assemblers_required_guards_true"])
    assert all(v is True for v in outcomes.values()), {k: v for k, v in outcomes.items() if v is not True}
    assert record["all_required_outcomes_met"] is True and record == json.loads((folder / "rehearsal.json").read_text())
    assert (record["commit"], record["attempt"]) == (COMMIT, 2) and list(record["killed_tasks"]) == [f"killed|rehearsal_2|{COMMIT[:12]}|rehearsal_delta_heldout|C1"]
    assert LL.rehearsal_of_record(results)[0] == 2  # a deciding stage would rest on this record
    # the timings the projection needs, each arm's steady step its own; and check C0 for the run on top of both rehearsals
    assert set(LG.TIMING_KEYS) <= set(record["timings"]) and len(record["timings"]["observations"]["seconds_to_ready"]) == 8 + 2  # every life that returned; the one killed did not
    assert record["delta_on_step"]["delta_on_over_lead"] == pytest.approx(record["timings"]["seconds_per_search_step_delta_on"] / record["timings"]["seconds_per_search_step"])
    spent = record["money_spent_on_rehearsals"]
    mine = record["this_rehearsal"]
    assert mine["container_lives"] == 8 + 2 + 1 and spent["container_lives"] == mine["container_lives"] + 3 and spent["billed"] == 0.7509
    assert spent["function_seconds"] == pytest.approx(428.6 + mine["function_seconds"] + 4 * 1.5)
    c0 = record["check_C0"]
    assert c0["cap"] == 150.0 and c0["spent"]["container_lives"] == spent["container_lives"] and c0["projected_dollars"] == pytest.approx(c0["spent_dollars"] + c0["run_dollars"])
    assert set(c0["stages"]) == set(DECIDING) and c0["assemble_seconds"] == 3.0
    assert [c["check"] for c in record["spend_checks_of_the_rehearsal_itself"]] == ["C1", "C2", "C3"] and all(c["cap"] == 6.0 for c in record["spend_checks_of_the_rehearsal_itself"])
    # nothing sealed is in anything the commands wrote on the open side or logged: no file of the folder but the tables holds a harm
    opened = "".join(p.read_text() for p in folder.glob("*.json") if p.name not in ("rehearsal.json", "ledger.json"))
    assert "own_text" not in opened and "carried" not in opened.replace("carried_differs_from_own_batch_values", "").replace("carried_vector", "")
    assert all(set(ln) <= set(LR.LOG_FIELDS) for ln in tiny.lines)

    # the rows are not met by default: without the relaunch, without the validation's new check, with a guard false
    def outcomes_with(edit) -> dict:
        other = tmp_path / "edited" / "s5_lead" / "rehearsal_2"
        if other.parent.parent.exists():
            shutil.rmtree(other.parent.parent)
        shutil.copytree(folder, other)
        edit(other)
        return LL.rehearsal_outcomes(other)

    def one_launch(f: Path) -> None:
        led = json.loads((f / "ledger.json").read_text())
        led["stages"]["rehearsal_delta_heldout"]["launches"] = led["stages"]["rehearsal_delta_heldout"]["launches"][1:]
        LL.write_json(f / "ledger.json", led)

    def no_new_check(f: Path) -> None:
        v = json.loads((f / "validate.json").read_text())
        v["tables"]["C1_rehearsal"]["failed"] = wrong_batch[:2]
        LL.write_json(f / "validate.json", v)

    def a_guard_false(f: Path) -> None:
        a = json.loads((f / "assemble.json").read_text())
        a["arms"]["C2_rehearsal"]["outcomes"]["G10"] = False
        LL.write_json(f / "assemble.json", a)

    def not_the_pilots(f: Path) -> None:
        a = json.loads((f / "assemble.json").read_text())
        a["arms"]["C1_rehearsal"]["outcomes"]["attack_role_equals_pilot"]["record_equals_pilot"] = False
        LL.write_json(f / "assemble.json", a)

    for edit, rows in ((one_launch, {"row_2_kill_inside_a_unit", "row_3_stop_then_relaunch"}), (no_new_check, {"row_7_validate_only"}),
                       (a_guard_false, {"assemblers_required_guards_true"}), (not_the_pilots, {"row_9_search_equal_to_the_pilots"})):
        got = outcomes_with(edit)
        assert {k for k, v in got.items() if v is not True} == rows, edit.__name__


def test_the_validate_only_command_reads_a_rehearsals_tables_and_refuses_any_other(tmp_path, monkeypatch):
    monkeypatch.setattr(LL, "RESULTS", tmp_path / "s5_lead")
    import lead_cases as C

    table = C.synthetic_table(K_=1, ns=1)
    table["meta"] = {**table["meta"], "kind": "real", "arm": "rehearsal", "rehearsal": True}
    folder = tmp_path / "s5_lead" / "rehearsal_2"
    LT.save_table(table, folder / "C1_rehearsal" / "sealed", part_bytes=LL.REHEARSAL_PART_BYTES)
    out = LL.validate_rehearsal_tables(folder)
    assert out["C1_rehearsal"]["loaded"] is True and out["C1_rehearsal"]["parts"] == 2 and out["C1_rehearsal"]["failed"] == []
    assert list(out["C1_rehearsal"]["checks"]) == list(LT.CHECKS + LT.LOADER_CHECKS) and all(out["C1_rehearsal"]["checks"].values())
    assert not re.search(r"\d+\.\d+", json.dumps(out))  # names with pass or fail, and no value
    # a part that is not the one the core file records: the loader's refusal is the one check that fails
    part = folder / "C1_rehearsal" / "sealed" / "table_per_text_02.npz"
    part.write_bytes(part.read_bytes()[:-1] + b"x")
    broken = LL.validate_rehearsal_tables(folder)["C1_rehearsal"]
    assert broken["loaded"] is False and broken["failed"] == ["per_text_files_match_core_metadata"]
    # any other table is refused, by where it is and by what its own metadata says
    for name, meta in (("lead", {"rehearsal": True, "arm": "rehearsal"}), ("rehearsal_3", {"rehearsal": False, "arm": "rehearsal"}),
                       ("rehearsal_4", {"rehearsal": True, "arm": "lead"})):
        other = dict(table)
        other["meta"] = {**table["meta"], **meta}
        LT.save_table(other, tmp_path / "s5_lead" / name / "x" / "sealed")
        with pytest.raises(LL.LaunchRefusal, match="not a rehearsal's"):
            LL.validate_rehearsal_tables(tmp_path / "s5_lead" / name)
    with pytest.raises(LL.LaunchRefusal, match="not a rehearsal's folder"):
        LL.validate_rehearsal_tables(tmp_path / "elsewhere" / "rehearsal_2")
