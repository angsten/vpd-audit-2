"""Plan 1 of the research log, Section 5.4: the entry point of the lead experiment's analysis.

    uv run python -m vpd_audit_2.lead_analysis --lead <folder> [--delta-on <folder>] --out <folder>
        [--multipliers <json>] [--madeup-report <json>] [--repair-note <file>] [--author-ruling <file>]

One command reads a table, or the lead and delta-on tables together, validates, computes every row, and writes the
record (`lead_records.json`), the printed tables (`lead_tables.txt`), and every statistic's bootstrap replicate values
(`lead_replicates.npz`) under the output folder. The printed text is built from the record alone.

All or nothing. Every row of both printed tables, the copy without the overlapping texts, and the delta-on summary are
computed in memory first. Nothing is written or printed unless all of it succeeds. On any failure one line is printed:
the name of the check that failed, or the exception's type and the module and function it came from. That line holds
no digit, and never the exception's own text.

A table is real if its metadata says so, or if any of its files lies under a folder named `sealed`. For a real table
the command refuses to run unless every condition of plan 1 of the research log, Section 5.4, holds (`check_real`). This command is what
lifts the seal. Nothing else in the repository may load a real table.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_reading as LR
from vpd_audit_2 import lead_table as LT

REPO_ROOT = Path(__file__).resolve().parent.parent  # the `vpd-audit-2` folder
# The analysis modules, which must be byte-identical between the run's commit and the commit the analysis runs at
# (plan 1 of the research log, Section 12.1, item 3). `pilot.py` is among them for `crossing`.
ANALYSIS_MODULES = ("vpd_audit_2/lead_table.py", "vpd_audit_2/lead_intervals.py", "vpd_audit_2/lead_reading.py",
                    "vpd_audit_2/lead_analysis.py", "vpd_audit_2/pilot.py")
FREEZE_DIR = "freeze"
MULTIPLIERS_MD = "freeze/amendment1_multipliers.md"
MULTIPLIERS_JSON = "freeze/amendment1_multipliers.json"
MADEUP_REPORT = "results/s5_madeup/report.json"
RECEIPT = "receipt.json"
ROWS = LT.STEP_ROWS + LT.LEVEL_ROWS
MULTIPLIER_GRID = 0.05
OUT_RECORDS, OUT_TEXT, OUT_REPLICATES = "lead_records.json", "lead_tables.txt", "lead_replicates.npz"
RULING_LINE = "The delta-on run is not summarized: it is not complete, and the author's ruling on it is on file."
NO_DELTA_LINE = "No delta-on table was given."
NO_SECOND_COPY_LINE = "Not computed: this made-up table carries no per-text harms."


class Refusal(Exception):
    """A condition for running does not hold. The message is the condition's name and holds no digit."""

    def __init__(self, check: str) -> None:
        assert not any(c.isdigit() for c in check), "a check's name holds no digit"
        self.check = check
        super().__init__(check)


# ----------------------------------------------------------------------------- git


def _git(top: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(top), *args], capture_output=True, text=True)


def git_top(path: Path) -> Path | None:
    r = _git(path, "rev-parse", "--show-toplevel")
    return Path(r.stdout.strip()).resolve() if r.returncode == 0 else None


def head_commit(top: Path) -> str | None:
    r = _git(top, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    return r.stdout.strip() if r.returncode == 0 else None


def commit_known(top: Path, commit: str) -> bool:
    return bool(commit) and all(c in "0123456789abcdef" for c in commit) and _git(top, "cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


def tree_clean(top: Path, rel: str) -> bool:
    """No change to a tracked file and no untracked file under `rel` (ignored files apart)."""
    r = _git(top, "status", "--porcelain", "--", rel)
    return r.returncode == 0 and r.stdout.strip() == ""


def object_at(top: Path, commit: str, rel: str) -> str | None:
    """The hash of the file or folder `rel` as it stands in `commit`, or None if it is not there."""
    r = _git(top, "rev-parse", "--verify", "--quiet", f"{commit}:{rel}")
    return r.stdout.strip() if r.returncode == 0 else None


def is_committed(top: Path, path: Path) -> bool:
    """`path` is a file in the current commit, and its bytes on disk are the committed ones."""
    path = Path(path).resolve()
    head = head_commit(top)
    if head is None or not path.is_file() or top not in path.parents:
        return False
    rel = path.relative_to(top).as_posix()
    blob = object_at(top, head, rel)
    r = _git(top, "hash-object", "--", str(path))
    return blob is not None and r.returncode == 0 and r.stdout.strip() == blob


# ----------------------------------------------------------------------------- inputs


def parse_multipliers(path: Path) -> dict[str, float]:
    """The machine-readable copy of the multipliers: {"rows": {"n20": 1.0, ..., "h10": 1.0}}, one per row, each at
    least 1 and a multiple of 0.05."""
    try:
        rows = json.loads(Path(path).read_text())["rows"]
        out = {row: float(rows[row]) for row in ROWS}
        ok = set(rows) == set(ROWS) and all(
            math.isfinite(v) and v >= 1.0 and abs(v / MULTIPLIER_GRID - round(v / MULTIPLIER_GRID)) < 1e-9 for v in out.values())
    except Exception:
        raise Refusal("multipliers_copy_parses") from None
    if not ok:
        raise Refusal("multipliers_copy_parses")
    return out


def read_null_range(path: Path) -> dict[str, Any]:
    """The range of the delta-on shares when the delta components do nothing, from the made-up-data test's report."""
    try:
        null = json.loads(Path(path).read_text())["t8_null"]
        for row in LT.STEP_ROWS:
            for share in ("carried_share", "own_share"):
                for version in ("a", "b"):
                    assert len(null[row][share][version]) == 3
    except Exception:
        raise Refusal("made_up_report_parses") from None
    return null


def _receipt_path(folder: Path) -> Path:
    folder = Path(folder)
    return (folder.parent if folder.name == "sealed" else folder) / RECEIPT


def check_real(repo_root: Path, tables: dict[str, dict[str, Any]], *, delta_given: bool, repair_note: Path | None,
               author_ruling: Path | None) -> dict[str, Any]:
    """Every condition for reading a real table (plan 1 of the research log, Section 5.4). Reads no harm. Returns what the output records."""
    repo_root = Path(repo_root).resolve()
    top = git_top(repo_root)
    if top is None:
        raise Refusal("git_tree_clean")
    rel = repo_root.relative_to(top).as_posix()
    head = head_commit(top)
    if head is None or not tree_clean(top, rel):
        raise Refusal("git_tree_clean")

    # one run commit, known to this repository
    commits = {str(t["meta"].get("run_commit", "")) for t in tables.values()}
    if len(commits) != 1 or not commit_known(top, next(iter(commits))):
        raise Refusal("one_run_commit")
    run_commit = next(iter(commits))

    # the rules and the analysis code are those committed before the run
    here, then = object_at(top, head, f"{rel}/{FREEZE_DIR}"), object_at(top, run_commit, f"{rel}/{FREEZE_DIR}")
    if here is None or here != then:
        raise Refusal("freeze_matches_run_commit")
    changed = [m for m in ANALYSIS_MODULES
               if object_at(top, head, f"{rel}/{m}") is None or object_at(top, head, f"{rel}/{m}") != object_at(top, run_commit, f"{rel}/{m}")]
    note_hash = None
    if repair_note is not None:
        if not is_committed(top, repair_note):
            raise Refusal("repair_note_committed")
        note_hash = LT.sha256_file(Path(repair_note))
    if changed and note_hash is None:
        raise Refusal("analysis_code_matches_run_commit")

    # the multipliers, which by the condition on `freeze/` were present at the run's commit
    if not (repo_root / MULTIPLIERS_MD).is_file() or not (repo_root / MULTIPLIERS_JSON).is_file():
        raise Refusal("multipliers_file_present")
    multipliers = parse_multipliers(repo_root / MULTIPLIERS_JSON)

    # each table is the one the assembler wrote
    for t in tables.values():
        receipt_path = _receipt_path(t["folder"])
        if not is_committed(top, receipt_path):
            raise Refusal("receipt_committed")
        try:
            receipt = json.loads(receipt_path.read_text())
            listed = {f["name"]: f["sha256"] for f in receipt["files"]}
            same_commit = receipt["run_commit"] == run_commit
        except Exception:
            raise Refusal("table_matches_receipt") from None
        names = [p.name for p in t["files"]]
        if not same_commit or set(names) != set(listed) or any(not p.is_file() or LT.sha256_file(p) != listed[p.name] for p in t["files"]):
            raise Refusal("table_matches_receipt")
        parts = {p["name"]: p["sha256"] for p in t["meta"].get("per_text_files", [])}
        if not parts or any(listed.get(n) != h for n, h in parts.items()):
            raise Refusal("per_text_files_match_core_metadata")

    # both tables complete, or the author's ruling on the delta-on run
    if tables["lead"]["meta"].get("complete") is not True:
        raise Refusal("lead_table_complete")
    delta_complete = delta_given and tables["delta_on"]["meta"].get("complete") is True
    ruling_hash = None
    if author_ruling is not None:
        if not is_committed(top, author_ruling):
            raise Refusal("ruling_committed")
        ruling_hash = LT.sha256_file(Path(author_ruling))
    if not delta_complete and ruling_hash is None:
        raise Refusal("tables_complete_or_ruling")

    # the made-up-data test's report, which the delta-on summary reads
    if not is_committed(top, repo_root / MADEUP_REPORT):
        raise Refusal("made_up_report_committed")
    return {"analysis_commit": head, "run_commit": run_commit, "multipliers": multipliers, "analysis_modules_changed_since_run": changed,
            "repair_note_sha256": note_hash, "author_ruling_sha256": ruling_hash, "use_delta_on": bool(delta_complete),
            "null_range": read_null_range(repo_root / MADEUP_REPORT), "made_up_report_sha256": LT.sha256_file(repo_root / MADEUP_REPORT)}


# ----------------------------------------------------------------------------- computing


def _plain(x: Any) -> Any:
    """Plain JSON values: numpy numbers become Python numbers, and a number that is not finite becomes null."""
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    if isinstance(x, np.ndarray):
        return _plain(x.tolist())
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return float(x) if math.isfinite(float(x)) else None
    return x


def table_records(table: dict[str, Any], multipliers: dict[str, float], indices: LI.BootstrapIndices, *, batch_part: str = "bootstrap",
                  replicates: dict[str, np.ndarray] | None = None, label: str = "") -> dict[str, Any]:
    """Every row of the step table and of the harm-level table, with the scatter's data."""
    names = [str(x) for x in table["setting_names"]]
    out: dict[str, Any] = {"step": [], "level": [], "scatter": []}
    for row in ROWS:
        if row not in names:
            continue
        arrays = LT.row_arrays(table, row)
        before = LT.row_arrays(table, LT.STEP_BEFORE[row]) if LT.STEP_BEFORE.get(row) in names else None
        rec = LR.row_record(arrays, multiplier=multipliers[row], indices=indices, batch_part=batch_part, before=before,
                            replicates=replicates, label=label)
        out[arrays["table"]].append(rec)
        out["scatter"] += LR.scatter_points(arrays)
    return out


def delta_on_blocks(lead: dict[str, Any], delta: dict[str, Any], multipliers: dict[str, float], indices: LI.BootstrapIndices,
                    null_range: dict[str, Any], *, batch_part: str = "bootstrap", replicates: dict[str, np.ndarray] | None = None,
                    label: str = "") -> list[dict[str, Any]]:
    """The delta-on summary, one block per search length, on the cells the two tables share."""
    blocks = []
    for row in LT.STEP_ROWS:
        d = LT.row_arrays(delta, row)
        m = LR.matched_arrays(LT.row_arrays(lead, row), d)
        blocks.append(LR.delta_on_block(m, d, multiplier=multipliers[row], indices=indices, batch_part=batch_part,
                                        null_range=null_range[row], replicates=replicates, label=label))
    return blocks


def _prep_fp_equal(lead: dict[str, Any], delta: dict[str, Any]) -> dict[str, dict[str, bool]]:
    out: dict[str, dict[str, bool]] = {}
    for side, label, names in (("A", "attack", "attack_names"), ("H", "heldout", "heldout_names")):
        where = {str(n): k for k, n in enumerate(lead[names])}
        out[label] = {str(n): bool(lead[f"prep_fp_{side}"][where[str(n)]] == delta[f"prep_fp_{side}"][k]) for k, n in enumerate(delta[names])}
    return out


def _validated(folder: Path, what: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Load and validate a table, and its copy without the overlapping texts where it has per-text harms."""
    try:
        table = LT.load_table(folder)
        LT.validate(table)
    except LT.TableCheckError as e:
        raise Refusal(f"{what}: {e.check}") from None
    second = None
    if LT.has_per_text(table):
        try:
            second = LT.without_excluded(table)
            LT.validate(second)
        except LT.TableCheckError as e:
            raise Refusal(f"{what}, without the overlapping texts: {e.check}") from None
    return table, second


def compute(lead_dir: Path, delta_dir: Path | None = None, *, multipliers_path: Path | None = None, madeup_report_path: Path | None = None,
            repair_note: Path | None = None, author_ruling: Path | None = None, repo_root: Path | None = None,
            B: int = LI.BOOTSTRAP_B) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Everything the command writes, in memory: the record and the replicate values."""
    repo_root = REPO_ROOT if repo_root is None else Path(repo_root)
    folders = {"lead": Path(lead_dir)}
    if delta_dir is not None:
        folders["delta_on"] = Path(delta_dir)
    tables: dict[str, dict[str, Any]] = {}
    for arm, folder in folders.items():
        if not (folder / LT.CORE_FILE).is_file():
            raise Refusal("table_files_present")
        tables[arm] = {"folder": folder, "files": LT.table_files(folder), "meta": LT.read_meta(folder / LT.CORE_FILE)}
    real = any(LT.is_real(t["meta"], t["files"]) for t in tables.values())

    if real:
        facts = check_real(repo_root, tables, delta_given=delta_dir is not None, repair_note=repair_note, author_ruling=author_ruling)
        multipliers, null_range, use_delta = facts["multipliers"], facts["null_range"], facts["use_delta_on"]
        delta_note = RULING_LINE if not use_delta else None
    else:
        multipliers = parse_multipliers(multipliers_path) if multipliers_path is not None else {row: 1.0 for row in ROWS}
        use_delta = delta_dir is not None
        delta_note = None if use_delta else NO_DELTA_LINE
        null_range = None
        if use_delta:
            if madeup_report_path is None or not Path(madeup_report_path).is_file():
                raise Refusal("made_up_report_present")
            null_range = read_null_range(Path(madeup_report_path))
        top = git_top(Path(repo_root))
        facts = {"analysis_commit": head_commit(top) if top is not None else None, "run_commit": None, "repair_note_sha256": None,
                 "author_ruling_sha256": None, "analysis_modules_changed_since_run": [], "made_up_report_sha256": None}

    lead, lead_second = _validated(folders["lead"], "lead table")
    replicates: dict[str, np.ndarray] = {}
    K = int(lead["meta"]["design"]["K_A"])
    indices = {K: LI.make_indices(K, B)}
    main = table_records(lead, multipliers, indices[K], replicates=replicates, label="main.")
    doc: dict[str, Any] = {
        "header": {"batch_means_added_harm": LT.batch_means_added_harm(lead)},
        "main": {"step": main["step"], "level": main["level"]},
        "scatter": main["scatter"],
        "long_search": LT.long_search_levels(lead),
        "footers": {"step": LR.STEP_FOOTER, "level": list(LR.LEVEL_FOOTERS)},
    }
    if lead_second is not None:
        second = table_records(lead_second, multipliers, indices[K], replicates=replicates, label="second.")
        for kind in ("step", "level"):
            for rec, rec2 in zip(main[kind], second[kind], strict=True):
                LR.mark_recomputed(rec, rec2)
        doc["without_overlapping_texts"] = {"note": LR.SECOND_COPY_NOTE, "excluded_texts": int(lead["excluded_H"].sum()),
                                            "tables": {"step": second["step"], "level": second["level"]}}
    else:
        doc["without_overlapping_texts"] = {"note": NO_SECOND_COPY_LINE, "tables": None}

    if use_delta:
        delta, delta_second = _validated(folders["delta_on"], "delta-on table")
        Kd = int(delta["meta"]["design"]["K_A"])
        if Kd not in indices:
            indices[Kd] = LI.make_indices(Kd, B)
        doc["delta_on"] = {
            "prep_fp_equal": _prep_fp_equal(lead, delta),
            "blocks": delta_on_blocks(lead, delta, multipliers, indices[Kd], null_range, replicates=replicates, label="main."),
            "blocks_without_overlapping_texts": (delta_on_blocks(lead_second, delta_second, multipliers, indices[Kd], null_range,
                                                                 replicates=replicates, label="second.")
                                                 if lead_second is not None and delta_second is not None else None),
        }
    else:
        doc["delta_on"] = {"blocks": None, "note": delta_note}

    meta = lead["meta"]
    doc["provenance"] = {
        "table kind": "real" if real else "made up",
        "analysis commit": facts["analysis_commit"] or "not recorded",
        "tree clean under vpd-audit-2": "yes" if real else "not checked for a made-up table",
        "run commit, from the table": meta.get("run_commit"),
        "run tree clean, from the table": meta.get("run_tree_clean"),
        "arm": meta.get("arm"), "scenario": meta.get("scenario"),
        "starts (seed keys)": [int(x) for x in lead["starts"]],
        "input hashes, from the table": meta.get("sha256"),
        "containers, from the table": meta.get("containers"),
        "multipliers": multipliers,
        "bootstrap": {str(k): {"B": v.B, "seed": list(v.seed), "indices_sha256": v.sha256} for k, v in indices.items()},
        "analysis modules changed since the run": facts["analysis_modules_changed_since_run"],
        "repair note sha256": facts["repair_note_sha256"],
        "author ruling sha256": facts["author_ruling_sha256"],
        "made-up-data report sha256": facts["made_up_report_sha256"],
    }
    doc = json.loads(json.dumps(_plain(doc), allow_nan=False))
    LR.render(doc)  # the text must build before anything is written
    return doc, replicates


def write_outputs(out_dir: Path, doc: dict[str, Any], replicates: dict[str, np.ndarray]) -> str:
    """Write the three files, each under a temporary name first, and return the printed text."""
    from vpd_audit_2.manifest import deterministic_npz

    records = (json.dumps(doc, indent=1, allow_nan=False) + "\n").encode()
    text = LR.render(json.loads(records))  # the printed text is built from the record file's content alone
    payload = {
        OUT_RECORDS: records,
        OUT_TEXT: text.encode(),
        OUT_REPLICATES: deterministic_npz(replicates),
    }
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, data in payload.items():
        (out_dir / (name + ".tmp")).write_bytes(data)
    for name in payload:
        os.replace(out_dir / (name + ".tmp"), out_dir / name)
    return text


def failure_line(exc: BaseException) -> str:
    """One line for a failure: the check's name, or the exception's type and where it came from. No digit, and never
    the exception's own text."""
    if isinstance(exc, Refusal):
        line = f"REFUSED: {exc.check}"
    elif isinstance(exc, LT.TableCheckError):
        line = f"REFUSED: table check: {exc.check}"
    elif isinstance(exc, LI.ClosedFormCheckError):
        line = "FAILED: closed_form_check"
    else:
        where = "unknown"
        for frame in reversed(traceback.extract_tb(exc.__traceback__)):
            if "vpd_audit_2" in Path(frame.filename).parts:
                where = f"{Path(frame.filename).stem}.{frame.name}"
                break
        line = f"FAILED: {type(exc).__name__} in {where}"
    return "".join("#" if c.isdigit() else c for c in line)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The lead experiment's analysis: all or nothing.")
    ap.add_argument("--lead", required=True, type=Path)
    ap.add_argument("--delta-on", type=Path, default=None)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--multipliers", type=Path, default=None, help="made-up tables only; a real table reads the committed file")
    ap.add_argument("--madeup-report", type=Path, default=None, help="made-up tables only; a real table reads the committed report")
    ap.add_argument("--repair-note", type=Path, default=None)
    ap.add_argument("--author-ruling", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        doc, replicates = compute(args.lead, args.delta_on, multipliers_path=args.multipliers, madeup_report_path=args.madeup_report,
                                  repair_note=args.repair_note, author_ruling=args.author_ruling)
        text = write_outputs(args.out, doc, replicates)
    except Exception as exc:  # noqa: BLE001  (every failure becomes one line that holds no number)
        print(failure_line(exc), file=sys.stderr)
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
