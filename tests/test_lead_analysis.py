"""The entry point: what it writes, that it is all or nothing, and every refusal for a real table (plan 1, Sections
5.4 and 6).

The refusals are tested on a made-up table relabelled as real inside the test, in a small git repository built under
the test's temporary folder with the layout of this one (`vpd-audit-2/` below the top, and a path named `head` at the
top, as here).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

import lead_cases as C
from vpd_audit_2 import lead_analysis as LA
from vpd_audit_2 import lead_reading as LR
from vpd_audit_2 import lead_table as LT

CODE = Path(LA.__file__).resolve().parent
NULL = {row: {share: {"a": [0.80, 1.00, 1.25], "b": [0.55, 1.01, 1.80]} for share in ("carried_share", "own_share")} for row in LT.STEP_ROWS}


def _no_digit(text: str) -> bool:
    return not any(c.isdigit() for c in text)


# ----------------------------------------------------------------------------- a made-up table


@pytest.fixture(scope="module")
def lead_folder(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("made_up") / "lead"
    LT.save_table(C.synthetic_table(K_=4, low_attack=2, low_heldout=1), folder)
    return folder


@pytest.fixture(scope="module")
def delta_folder(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("made_up") / "delta_on"
    LT.save_table(C.synthetic_table(K_=4, seed=7, arm="delta_on", setting_names=LT.SETTINGS_DELTA_ON, retention=0.4), folder)
    return folder


@pytest.fixture(scope="module")
def report_file(tmp_path_factory) -> Path:
    path = tmp_path_factory.mktemp("made_up") / "report.json"
    path.write_text(json.dumps({"t8_null": NULL}))
    return path


def test_a_made_up_table_runs_and_writes_the_record_the_text_and_the_replicates(lead_folder, tmp_path, capsys):
    out = tmp_path / "out"
    assert LA.main(["--lead", str(lead_folder), "--out", str(out)]) == 0
    printed = capsys.readouterr()
    assert sorted(p.name for p in out.iterdir()) == ["lead_records.json", "lead_replicates.npz", "lead_tables.txt"]
    text = (out / "lead_tables.txt").read_text()
    doc = json.loads((out / "lead_records.json").read_text())
    assert printed.out == text and printed.err == ""
    assert LR.render(doc) == text  # the printed text is built from the record alone
    assert [r["key"] for r in doc["main"]["step"]] == [20, 40, 80, 160, 320] and [r["key"] for r in doc["main"]["level"]] == [2.0, 5.0, 10.0]
    assert doc["provenance"]["table kind"] == "made up"
    assert doc["provenance"]["multipliers"] == {row: 1.0 for row in LA.ROWS}  # made-up tables default to 1
    # the second copy, with its one line on float32 means
    second = doc["without_overlapping_texts"]
    assert len(second["tables"]["step"]) == 5 and len(second["tables"]["level"]) == 3 and "1e-7" in second["note"]
    assert "SECOND COPY: BOTH TABLES RECOMPUTED WITHOUT THE OVERLAPPING HELD-OUT TEXTS" in text and second["note"] in text
    # headers and footers
    for side in ("attack", "heldout"):
        for row in ("n20", "n40"):
            means = doc["header"]["batch_means_added_harm"][side][row]
            assert len(means) == 4 and means == sorted(means)  # every batch's mean, sorted
    assert LR.STEP_FOOTER in text and all(f in text for f in LR.LEVEL_FOOTERS)
    assert text.count("Description: resolves no cell.") == 16  # every row of both copies
    assert doc["delta_on"] == {"blocks": None, "note": LA.NO_DELTA_LINE}
    assert doc["long_search"]["searches"] == 40 and len(doc["scatter"]) == 20 * 8 - 2 * 2  # two attack searches miss 5 and 10 nats
    # no count of early-breakout batches anywhere in the output (Amendment 1, Section 9, item 2)
    for phrase in ("breakout", "twice the median", "large, with low retention", "large; carry-over ratio undetermined"):
        assert phrase not in text and phrase not in json.dumps(doc)
    # every statistic's replicate values are saved, with the seed and a hash of the index arrays
    with np.load(out / "lead_replicates.npz") as z:
        assert z["main.step.80.carries"].shape == (10_000,) and "second.level.5.depends" in z.files and "main.step.320.before.large" in z.files
    assert doc["provenance"]["bootstrap"]["4"]["seed"] == [20261001, 5001, 4, 10000] and len(doc["provenance"]["bootstrap"]["4"]["indices_sha256"]) == 64
    # a harm-level row never prints a step count
    level_text = text[text.index("HARM-LEVEL TABLE: settings"):text.index("SECOND COPY")]
    assert level_text.count("HARM-LEVEL TABLE: settings") == 3 and "step" not in level_text.replace("20-step", "").replace("step-table cell", "")


def test_a_made_up_multipliers_file_widens_and_flags(lead_folder, tmp_path):
    mult = tmp_path / "multipliers.json"
    mult.write_text(json.dumps({"rows": {**{row: 1.0 for row in LA.ROWS}, "n40": 1.15}}))
    doc, _ = LA.compute(lead_folder, multipliers_path=mult, B=500)
    by_key = {r["key"]: r for r in doc["main"]["step"]}
    assert "F11" in by_key[40]["flags"] and "F11" not in by_key[80]["flags"]
    assert by_key[40]["carries"]["multiplier"] == 1.15 and by_key[40]["retention"]["pooled"]["multiplier"] == 1.15


def test_delta_on_summary_needs_the_made_up_report_and_prints_both_null_ranges(lead_folder, delta_folder, report_file, tmp_path, capsys):
    assert LA.main(["--lead", str(lead_folder), "--delta-on", str(delta_folder), "--out", str(tmp_path / "x")]) == 1
    assert capsys.readouterr().err.strip() == "REFUSED: made_up_report_present" and not (tmp_path / "x").exists()
    doc, replicates = LA.compute(lead_folder, delta_folder, madeup_report_path=report_file, B=500)
    blocks = doc["delta_on"]["blocks"]
    assert [b["key"] for b in blocks] == [20, 40, 80, 160, 320] and len(doc["delta_on"]["blocks_without_overlapping_texts"]) == 5
    assert blocks[2]["null_range"] == NULL["n80"]
    assert doc["delta_on"]["prep_fp_equal"] == {"attack": {f"A{i}": True for i in range(1, 5)}, "heldout": {f"H{i}": True for i in range(1, 5)}}
    assert "main.delta_on.80.carried_share" in replicates and "second.delta_on.20.delta_on.depends" in replicates
    text = LR.render(doc)
    assert text.count("DELTA-ON SUMMARY: ") == 10 and text.count(LR.DELTA_ON_CAUTION) == 10
    assert "attack: A1 true, A2 true, A3 true, A4 true" in text
    assert "carried-over share: same searches, fresh cell noise 0.80 to 1.25; every search redrawn 0.55 to 1.80" in text
    assert "own-search share: same searches, fresh cell noise 0.80 to 1.25; every search redrawn 0.55 to 1.80" in text


def _saved(table: dict, folder: Path) -> Path:
    LT.save_table(table, folder)
    return folder


def test_T12_the_script_refuses_a_broken_table_naming_the_check(tmp_path, capsys):
    good = C.synthetic_table(K_=4)
    nan_cell = dict(good, carried=good["carried"].copy())
    nan_cell["carried"][1, 2, 3, 0] = np.nan
    altered = dict(good, block_ids_sha=good["block_ids_sha"].copy())
    altered["block_ids_sha"][0, 1, 2] = "f" * 64
    reshaped = dict(good, shuf_sha=good["shuf_sha"].reshape(4, 5, 8, 10))
    deleted = {k: v for k, v in good.items() if k != "own_H"}  # a table with one array deleted
    for name, bad, check in (("nan", nan_cell, "nan_exactly_where_setting_missing"), ("ids", altered, "block_ids_match_heldout_ids"),
                             ("shape", reshaped, "arrays_present_with_declared_shapes")):
        folder = _saved(bad, tmp_path / name)
        assert LA.main(["--lead", str(folder), "--out", str(tmp_path / f"out_{name}")]) == 1
        printed = capsys.readouterr()
        assert printed.out == "" and printed.err.strip() == f"REFUSED: lead table: {check}"  # the name of the check, and no harm
        assert _no_digit(printed.err) and not (tmp_path / f"out_{name}").exists()
    with pytest.raises(LT.TableCheckError, match="^arrays_present_with_declared_shapes$"):
        LT.validate(deleted)
    assert LA.main(["--lead", str(tmp_path / "nowhere"), "--out", str(tmp_path / "o")]) == 1
    assert capsys.readouterr().err.strip() == "REFUSED: table_files_present"


def test_a_failure_at_a_late_row_leaves_nothing_written_or_printed(lead_folder, tmp_path, capsys, monkeypatch):
    real = LR.row_record
    calls = {"n": 0}

    def late_failure(arrays, **kwargs):
        calls["n"] += 1
        if kwargs.get("label") == "second." and arrays["table"] == "level" and arrays["key"] == 10.0:
            raise ValueError("carry-over ratio 0.7314 at row 16")  # the exception's own text must never be printed
        return real(arrays, **kwargs)

    monkeypatch.setattr(LR, "row_record", late_failure)
    out = tmp_path / "out"
    assert LA.main(["--lead", str(lead_folder), "--out", str(out)]) == 1
    printed = capsys.readouterr()
    assert calls["n"] == 16  # fifteen rows were computed before the last one failed
    assert printed.out == "" and not out.exists()
    assert printed.err.strip() == "FAILED: ValueError in lead_analysis.table_records"  # the type and the place in the package
    assert _no_digit(printed.err) and "0.7314" not in printed.err and "carry-over" not in printed.err


def test_failure_lines_hold_no_digit_and_never_the_exceptions_text():
    try:
        LT.crossing_steps(np.zeros((1, 1)), 2.0)  # a real error inside the package
    except Exception as exc:  # noqa: BLE001
        line = LA.failure_line(exc)
    assert line.startswith("FAILED: ") and " in lead_table.crossing_steps" in line and _no_digit(line)
    assert LA.failure_line(LA.Refusal("git_tree_clean")) == "REFUSED: git_tree_clean"
    assert LA.failure_line(LT.TableCheckError("complete_flag")) == "REFUSED: table check: complete_flag"
    assert LA.failure_line(LA.LI.ClosedFormCheckError()) == "FAILED: closed_form_check"
    assert LA.failure_line(KeyError("harm 12.5")) == "FAILED: KeyError in unknown"
    with pytest.raises(AssertionError):
        LA.Refusal("check 3")  # a check's name holds no digit


def test_multipliers_copy_must_give_every_row_a_multiple_of_the_grid_at_least_one(tmp_path):
    def parse(rows) -> dict:
        p = tmp_path / "m.json"
        p.write_text(json.dumps({"rows": rows}) if rows is not None else "not json")
        return LA.parse_multipliers(p)

    ones = {row: 1.0 for row in LA.ROWS}
    assert parse({**ones, "n40": 1.15, "h10": 1.5}) == {**ones, "n40": 1.15, "h10": 1.5}
    for bad in (None, {k: v for k, v in ones.items() if k != "h5"}, {**ones, "n40": 0.95}, {**ones, "n40": 1.07}, {**ones, "n640": 1.0},
                {**ones, "n40": "wide"}):
        with pytest.raises(LA.Refusal, match="^multipliers_copy_parses$"):
            parse(bad)


# ----------------------------------------------------------------------------- a real table


def _git(top: Path, *args: str) -> str:
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    r = subprocess.run(["git", "-C", str(top), *args], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _commit(top: Path, message: str) -> str:
    _git(top, "add", "-A")
    _git(top, "commit", "-q", "-m", message)
    return _git(top, "rev-parse", "--verify", "HEAD^{commit}")


def _write_real_table(repo: Path, arm: str, run_commit: str, *, complete: bool = True, seed: int = 0) -> Path:
    """A made-up table relabelled as real, under `results/s5_lead/<arm>/sealed/`, with the assembler's receipt beside."""
    names = LT.SETTINGS_LEAD if arm == "lead" else LT.SETTINGS_DELTA_ON
    table = C.synthetic_table(K_=4, seed=seed, arm=arm, setting_names=names)
    table["meta"].update(kind="real", run_commit=run_commit, complete=complete)
    folder = repo / "results" / "s5_lead" / arm / "sealed"
    files = LT.save_table(table, folder)
    receipt = {"arm": arm, "files": files, "complete": complete, "run_commit": run_commit, "shapes": table["meta"]["design"]}
    (folder.parent / "receipt.json").write_text(json.dumps(receipt, indent=1))
    return folder


@pytest.fixture(scope="module")
def base_repo(tmp_path_factory) -> Path:
    """The state a real analysis runs in: the rules, the analysis code, the multipliers, and the made-up-data report
    committed at the run's commit; the two tables and their receipts committed after it."""
    top = tmp_path_factory.mktemp("repo")
    repo = top / "vpd-audit-2"
    (repo / "vpd_audit_2").mkdir(parents=True)
    for module in LA.ANALYSIS_MODULES:
        shutil.copy(CODE.parent / module, repo / module)
    shutil.copytree(CODE.parent / "freeze", repo / "freeze")
    (repo / LA.MULTIPLIERS_MD).write_text("# Multipliers\n\nAll rows 1 but 40 steps.\n")
    (repo / LA.MULTIPLIERS_JSON).write_text(json.dumps({"rows": {**{row: 1.0 for row in LA.ROWS}, "n40": 1.15}}))
    (repo / LA.MADEUP_REPORT).parent.mkdir(parents=True)
    (repo / LA.MADEUP_REPORT).write_text(json.dumps({"t8_null": NULL}))
    (top / "head").write_text("a path named head, as in this repository\n")
    (top / "sessions").mkdir()
    (top / "sessions" / "notes.md").write_text("the session's own files\n")
    _git(top, "init", "-q")
    run_commit = _commit(top, "the run's commit")
    _write_real_table(repo, "lead", run_commit)
    _write_real_table(repo, "delta_on", run_commit, seed=7)
    _commit(top, "the sealed tables and their receipts")
    return top


@pytest.fixture()
def repo(base_repo, tmp_path) -> Path:
    shutil.copytree(base_repo, tmp_path / "top")
    return tmp_path / "top" / "vpd-audit-2"


def _run(repo: Path, *, delta: bool = True, **kwargs):
    lead = repo / "results" / "s5_lead" / "lead" / "sealed"
    delta_dir = repo / "results" / "s5_lead" / "delta_on" / "sealed" if delta else None
    return LA.compute(lead, delta_dir, repo_root=repo, B=300, **kwargs)


def _refused(repo: Path, check: str, **kwargs) -> None:
    with pytest.raises(LA.Refusal) as e:
        _run(repo, **kwargs)
    assert e.value.check == check, e.value.check
    assert _no_digit(LA.failure_line(e.value))  # a message containing no number


def test_a_real_table_runs_when_every_condition_holds(repo):
    doc, _ = _run(repo)
    top = repo.parent
    p = doc["provenance"]
    assert p["table kind"] == "real" and p["analysis commit"] == _git(top, "rev-parse", "--verify", "HEAD^{commit}")
    assert p["run commit, from the table"] == _git(top, "rev-parse", "--verify", "HEAD~1^{commit}")
    assert p["multipliers"]["n40"] == 1.15  # read from the committed file, never defaulted
    assert p["analysis modules changed since the run"] == [] and p["repair note sha256"] is None
    assert p["made-up-data report sha256"] == LT.sha256_file(repo / LA.MADEUP_REPORT)
    assert doc["delta_on"]["blocks"][1]["multiplier"] == 1.15  # the delta-on run at the same search length
    assert "F11" in {r["key"]: r for r in doc["main"]["step"]}[40]["flags"]
    # the session's own files outside `vpd-audit-2/` do not make the tree dirty
    (top / "sessions" / "notes.md").write_text("changed during the session\n")
    (top / "sessions" / "new.md").write_text("untracked\n")
    _run(repo)


def test_refuses_when_the_tree_is_not_clean(repo):
    (repo / "scratch.txt").write_text("an untracked file\n")
    _refused(repo, "git_tree_clean")
    (repo / "scratch.txt").unlink()
    _run(repo)
    (repo / "vpd_audit_2" / "pilot.py").write_text((repo / "vpd_audit_2" / "pilot.py").read_text() + "\n# edited, not committed\n")
    _refused(repo, "git_tree_clean")


def test_refuses_when_the_analysis_code_is_not_the_code_committed_before_the_run(repo):
    top = repo.parent
    reading = repo / "vpd_audit_2" / "lead_reading.py"
    reading.write_text(reading.read_text() + "\n# repaired after the run\n")
    _commit(top, "a repair")
    _refused(repo, "analysis_code_matches_run_commit")  # a clean tree alone does not show "committed in advance"
    # a committed note that names the change is accepted, and its hash is recorded
    note = repo / "freeze_notes" / "repair_1.md"
    note.parent.mkdir()
    note.write_text("Changed: a comment in lead_reading.py. Reason: a test.\n")
    _refused(repo, "git_tree_clean", repair_note=note)  # the note is not committed yet
    _commit(top, "the repair's note")
    doc, _ = _run(repo, repair_note=note)
    assert doc["provenance"]["repair note sha256"] == LT.sha256_file(note)
    assert doc["provenance"]["analysis modules changed since the run"] == ["vpd_audit_2/lead_reading.py"]
    # a note outside the commit is refused
    outside = repo.parent.parent / "note.md"
    outside.write_text("not in the repository\n")
    _refused(repo, "repair_note_committed", repair_note=outside)


def test_refuses_when_the_rules_changed_after_the_run_note_or_no_note(repo):
    top = repo.parent
    amendment = repo / "freeze" / "amendment1.md"
    amendment.write_text(amendment.read_text() + "\nA line added after the run.\n")
    note = repo / "note.md"
    note.write_text("Changed the amendment.\n")
    _commit(top, "an edit to the rules")
    _refused(repo, "freeze_matches_run_commit")
    _refused(repo, "freeze_matches_run_commit", repair_note=note)  # the note waives the analysis modules only, never `freeze/`


def test_refuses_without_the_multipliers_file_or_its_machine_readable_copy(base_repo, tmp_path):
    def variant(change) -> Path:
        """A repository in which the multipliers were already as `change` leaves them at the run's commit."""
        top = tmp_path / f"v{len(list(tmp_path.iterdir()))}"
        repo = top / "vpd-audit-2"
        shutil.copytree(base_repo / "vpd-audit-2", repo, ignore=shutil.ignore_patterns("s5_lead"))
        change(repo)
        _git(top, "init", "-q")
        run_commit = _commit(top, "the run's commit")
        _write_real_table(repo, "lead", run_commit)
        _write_real_table(repo, "delta_on", run_commit, seed=7)
        _commit(top, "tables")
        return repo

    _refused(variant(lambda r: (r / LA.MULTIPLIERS_MD).unlink()), "multipliers_file_present")
    _refused(variant(lambda r: (r / LA.MULTIPLIERS_JSON).unlink()), "multipliers_file_present")
    _refused(variant(lambda r: (r / LA.MULTIPLIERS_JSON).write_text("{\"rows\": {\"n20\": 1.0}}")), "multipliers_copy_parses")
    # a multipliers file added after the run is a change to `freeze/`
    late = variant(lambda r: (r / LA.MULTIPLIERS_MD).unlink())
    (late / LA.MULTIPLIERS_MD).write_text("# Multipliers, written after the run\n")
    _commit(late.parent, "multipliers after the run")
    _refused(late, "freeze_matches_run_commit")


def test_refuses_when_a_table_is_not_the_one_the_assembler_wrote(repo):
    top = repo.parent
    sealed = repo / "results" / "s5_lead" / "lead" / "sealed"
    original = (sealed / "table_core.npz").read_bytes()
    table = LT.load_table(sealed)
    table["carried"][0, 0, 0, 0] += 1e-9  # one harm changed after the receipt was written
    LT.save_table(table, sealed)
    assert (sealed / "table_core.npz").read_bytes() != original
    _commit(top, "a changed table")
    _refused(repo, "table_matches_receipt")


def test_refuses_when_the_receipt_is_missing_or_not_committed_or_of_another_commit(repo):
    top = repo.parent
    receipt = repo / "results" / "s5_lead" / "delta_on" / "receipt.json"
    text = receipt.read_text()
    receipt.unlink()
    _commit(top, "no receipt")
    _refused(repo, "receipt_committed")
    receipt.write_text(text.replace(json.loads(text)["run_commit"], "0" * 40))
    _commit(top, "a receipt of another commit")
    _refused(repo, "table_matches_receipt")


def test_refuses_when_a_per_text_file_is_not_the_one_the_core_file_records(repo):
    top = repo.parent
    sealed = repo / "results" / "s5_lead" / "lead" / "sealed"
    table = LT.load_table(sealed)
    files = LT.save_table(table, sealed)
    from vpd_audit_2.manifest import deterministic_npz

    with np.load(sealed / "table_core.npz") as z:
        core = {k: z[k] for k in z.files}
    meta = LT.read_meta(sealed / "table_core.npz")
    meta["per_text_files"][0]["sha256"] = "0" * 64  # the core file records another per-text file
    core["meta"] = np.array(json.dumps(meta, sort_keys=True))
    (sealed / "table_core.npz").write_bytes(deterministic_npz(core))
    files[0]["sha256"] = LT.sha256_file(sealed / "table_core.npz")
    receipt = json.loads((sealed.parent / "receipt.json").read_text())
    (sealed.parent / "receipt.json").write_text(json.dumps({**receipt, "files": files}))
    _commit(top, "a core file that records another per-text file")
    _refused(repo, "per_text_files_match_core_metadata")


def test_refuses_an_incomplete_delta_on_table_without_the_pi_ruling(base_repo, tmp_path):
    top = tmp_path / "top"
    repo = top / "vpd-audit-2"
    shutil.copytree(base_repo / "vpd-audit-2", repo, ignore=shutil.ignore_patterns("s5_lead"))
    (top / "head").write_text("head\n")
    _git(top, "init", "-q")
    run_commit = _commit(top, "the run's commit")
    _write_real_table(repo, "lead", run_commit)
    _commit(top, "the lead's table alone, after a spend stop")
    _refused(repo, "tables_complete_or_ruling", delta=False)
    ruling = repo / "results" / "s5_lead" / "pi_ruling_delta_on.md"
    ruling.write_text("The PI rules: analyse the lead without the delta-on run.\n")
    _refused(repo, "git_tree_clean", delta=False, pi_ruling=ruling)
    _commit(top, "the PI's ruling")
    doc, _ = _run(repo, delta=False, pi_ruling=ruling)
    assert doc["delta_on"] == {"blocks": None, "note": LA.RULING_LINE}  # the summary is replaced by one fixed line
    assert doc["provenance"]["PI ruling sha256"] == LT.sha256_file(ruling)
    assert f"DELTA-ON SUMMARY\n  {LA.RULING_LINE}" in LR.render(doc)
    outside = tmp_path / "ruling.md"
    outside.write_text("not committed\n")
    _refused(repo, "ruling_committed", delta=False, pi_ruling=outside)
    # an incomplete delta-on table that is given is no better than none
    _write_real_table(repo, "delta_on", run_commit, complete=False, seed=7)
    _commit(top, "an incomplete delta-on table")
    _refused(repo, "tables_complete_or_ruling")
    # and an incomplete lead is refused whatever the ruling
    _write_real_table(repo, "lead", run_commit, complete=False)
    _commit(top, "an incomplete lead")
    _refused(repo, "lead_table_complete", delta=False, pi_ruling=ruling)


def test_refuses_without_the_committed_report_of_the_made_up_data_test(repo):
    top = repo.parent
    report = repo / LA.MADEUP_REPORT
    report.write_text(json.dumps({"t8_null": NULL, "edited": True}))
    _refused(repo, "git_tree_clean")  # present but not as committed
    report.unlink()
    _commit(top, "no report")
    _refused(repo, "made_up_report_committed")


def test_refuses_tables_of_an_unknown_run_commit_or_of_two(repo):
    top = repo.parent
    _write_real_table(repo, "delta_on", "1" * 40, seed=7)
    _commit(top, "a delta-on table from another commit")
    _refused(repo, "one_run_commit")
    _write_real_table(repo, "lead", "1" * 40)
    _commit(top, "both tables from a commit this repository does not have")
    _refused(repo, "one_run_commit")


def test_refuses_outside_a_git_repository(tmp_path):
    table = C.synthetic_table(K_=4)
    table["meta"]["kind"] = "real"
    folder = _saved(table, tmp_path / "t")
    with pytest.raises(LA.Refusal, match="^git_tree_clean$"):
        LA.compute(folder, repo_root=tmp_path, B=300)


def test_a_made_up_table_under_a_folder_named_sealed_is_treated_as_real(repo, tmp_path, capsys):
    table = C.synthetic_table(K_=4)
    assert table["meta"]["kind"] == "made_up"
    plain = _saved(table, tmp_path / "plain" / "lead")
    LA.compute(plain, repo_root=tmp_path, B=300)  # a made-up table runs without any of the conditions
    hidden = _saved(table, tmp_path / "sealed" / "lead")
    with pytest.raises(LA.Refusal, match="^git_tree_clean$"):
        LA.compute(hidden, repo_root=tmp_path, B=300)  # the same table under `sealed` must meet them
    # in the repository it meets the conditions of a real table one by one: its run commit is not a commit
    inside = _saved(table, repo / "results" / "s5_lead" / "mislabelled" / "sealed")
    _commit(repo.parent, "a mislabelled table")
    with pytest.raises(LA.Refusal, match="^one_run_commit$"):
        LA.compute(inside, repo_root=repo, B=300)
    assert LA.main(["--lead", str(hidden), "--out", str(tmp_path / "o")]) == 1  # and through the command, in this repository
    printed = capsys.readouterr()
    assert printed.out == "" and printed.err.startswith("REFUSED: ") and _no_digit(printed.err) and not (tmp_path / "o").exists()
