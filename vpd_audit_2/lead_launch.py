"""Plans 2 and 4 of the research log: the local side of the lead run, with no cloud call in it.

What each container is handed, the checks a launcher makes before any deciding job, the launcher itself, the ledger it
keeps, the sealed tables' arrival on the local side as bytes, the receipts, and the rehearsal's record. `modal_lead.py`
calls these and hands them what they need of the cloud as plain functions (`Cloud`), so that every piece, the launcher
included, can be tested without the cloud.

One side per container (Amendment 1, Section 6). A container is described by a `spec`: its arm, its side, and the
name of the one batch it holds. Its inputs are built by `container_inputs`, which loads the token ids of that batch
and of no other. A held-out container is given the attack batches' names, so that it can find their searches' saved
settings on the volume; it is never given their token ids.

The deciding run's stages, in order (plan 4 of the research log, Section 7): the lead's attack side; the lead's held-out side in two waves,
H1 alone and then the other fifteen; and the delta-on arm's attack and held-out sides. The rehearsal mirrors them on
calibration batches C1 and C2, each scored on itself only (plan 4 of the research log, Section 6.1).

Nothing on the local side loads a deciding table: `receive_table` checks bytes against a hash and writes them. The one
command that loads a table here, `validate_rehearsal_tables`, reads a rehearsal's and refuses any other.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT

REPO_ROOT = Path(__file__).resolve().parent.parent  # the `vpd-audit-2` folder
RESULTS = REPO_ROOT / "results" / "s5_lead"
VOLUME_S5 = "/cache/s5_lead"  # the run's folder on the cloud volume
BACKUP = REPO_ROOT / ".cache" / "s5_lead_units"  # `.cache/` is ignored by git
PART_A_COMMIT = "c1d256c18f8361557ef82f9b1f801b622b54eb56"  # the first commit of the branch: the signed rules and Amendment 1
STRATA_NPZ = REPO_ROOT / "results" / "s4_pilot" / "part_a" / "strata.npz"
STRATA_JSON = REPO_ROOT / "results" / "s4_pilot" / "part_a" / "strata.json"
STRATA_SHA_ENDS = ("12ce9067", "0af2")  # the strata file's recorded SHA-256 begins and ends so
STARTS_NPZ = REPO_ROOT / "results" / "s4_pilot" / "starts" / "starts_1_64.npz"
PILOT_RUNS = REPO_ROOT / "results" / "s4_pilot" / "part_a" / "runs.json"
OVERLAP_JSON = REPO_ROOT / "data" / "manifest" / "heldout_span_overlap.json"
MULTIPLIERS_MD = REPO_ROOT / "freeze" / "amendment1_multipliers.md"
BATCHES = {
    "lead": {"attack": [f"A{i}" for i in range(1, 17)], "heldout": [f"H{j}" for j in range(1, 17)]},
    "delta_on": {"attack": [f"A{i}" for i in range(1, 9)], "heldout": [f"H{j}" for j in range(1, 9)]},
}
# Each deciding stage's batches. The lead's held-out side runs in two waves: H1 alone, then the other fifteen.
STAGE_BATCHES = {
    "lead_attack": BATCHES["lead"]["attack"], "lead_heldout_1": BATCHES["lead"]["heldout"][:1], "lead_heldout_2": BATCHES["lead"]["heldout"][1:],
    "delta_attack": BATCHES["delta_on"]["attack"], "delta_heldout": BATCHES["delta_on"]["heldout"],
}
# The rehearsal: calibration batches C1 and C2 with pilot start 1; each batch plays both roles and is scored on itself
# only. Each role's units go to a folder of their own, since both roles write a search file of the same name.
REHEARSAL_BATCHES = ("C1", "C2")
REHEARSAL_START = 1
REHEARSAL_DELTA_STEPS = 20
REHEARSAL_STAGE_BATCHES = {
    "rehearsal_attack": ["C1", "C2"], "rehearsal_heldout_1": ["C1"], "rehearsal_heldout_2": ["C2"],
    "rehearsal_delta_attack": ["C1", "C2"], "rehearsal_delta_heldout": ["C1", "C2"],
}
REHEARSAL_UNITS = {("rehearsal", "attack"): "units_attack", ("rehearsal", "heldout"): "units_heldout",
                   ("rehearsal_delta_on", "attack"): "units_delta_attack", ("rehearsal_delta_on", "heldout"): "units_delta_heldout"}
REHEARSAL_PART_BYTES = 1_000  # a part size so small that a one-by-one table's per-text file goes in two parts
REHEARSAL_STOP_DOLLARS = 6.0  # plan 4 of the research log, Section 6.1: stop and report if the repeat rehearsal's counted spend passes this
FIRST_REHEARSAL_LIVES = 3  # the first rehearsal's GPU containers: the one killed, its replacement, and the held-out role's
# What the rehearsal's own spend checks expect a container to take, rounded up from the first rehearsal's record
# (`results/s5_lead/rehearsal/rehearsal.json`). They price the rehearsal itself and nothing else.
REHEARSAL_EXPECTED_TIMINGS = {
    "seconds_per_search_step": 0.39, "seconds_per_search_step_delta_on": 0.50, "seconds_per_scoring_pass": 0.185, "seconds_to_ready": 58.0,
    "seconds_first_search_extra": 2.5, "seconds_per_search_fixed": 0.3, "seconds_per_commit_after_search": 4.9, "seconds_per_commit_after_blocks": 4.9,
    "seconds_per_shuffle": 0.0075, "seconds_per_search_unit_other": 2.1, "seconds_per_block_other": 0.02,
}
TRIGGERS = ("stop", "kill")  # the rehearsal-only triggers of plan 4 of the research log, Section 6, rows 2 and 3
# Every module a container or the assembler runs. The rehearsal covers the deciding run only if each is byte-identical
# between the rehearsal's commit and the run's (plan 2 of the research log, Section 8).
RUN_FILES = ("vpd_audit_2/adversary.py", "vpd_audit_2/pilot.py", "vpd_audit_2/lead_run.py", "vpd_audit_2/lead_table.py", "vpd_audit_2/lead_launch.py",
             "vpd_audit_2/lead_ledger.py", "vpd_audit_2/modal_lead.py", "vpd_audit_2/modal_app.py", "vpd_audit_2/modal_gates.py", "vpd_audit_2/manifest.py",
             "vpd_audit_2/env.py", "pyproject.toml", "uv.lock", "third_party/vpd-audit")
NOTICE = LR.NOTICE  # the do-not-open notice written beside every sealed file, in the cloud and here


class LaunchRefusal(Exception):
    """A condition for launching does not hold, or a stage did not finish cleanly. The message names it and holds no value."""


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1) + "\n")


# ----------------------------------------------------------------------------- what a container is handed


def design_of(rehearsal: int) -> tuple[LG.Stage, ...]:
    return LG.REHEARSAL_DESIGN if rehearsal else LG.DESIGN


def rehearsal_folder(attempt: int) -> Path:
    if attempt < 2:
        raise LaunchRefusal("a repeat rehearsal is numbered from 2; the first rehearsal's record is results/s5_lead/rehearsal")
    return RESULTS / f"rehearsal_{attempt}"


def results_folder(rehearsal: int) -> Path:
    return rehearsal_folder(rehearsal) if rehearsal else RESULTS


def volume_root(arm: str, commit: str, rehearsal: int) -> str:
    """Where an arm's sealed files live on the volume: a folder per arm, or one folder for a rehearsal's attempt."""
    return f"{VOLUME_S5}/rehearsal/{commit[:12]}_{rehearsal}" if rehearsal else f"{VOLUME_S5}/{arm}"


def run_key(rehearsal: int) -> str:
    """The name under which a run keeps its stop flag in the cloud's control dictionary."""
    return f"rehearsal_{rehearsal}" if rehearsal else "run"


def container_specs(stage: str, commit: str, rehearsal: int = 0, trigger: str | None = None) -> list[dict[str, Any]]:
    """One spec per container of a stage: one batch of one arm. A held-out spec names the attack batches whose saved
    settings it will read from the volume.

    A rehearsal's spec carries what only a rehearsal may: the override of the pool check for its one calibration batch,
    its own unit folders, 20 steps for the delta-on searches, its own batch as the one attack batch it scores, and, where
    asked, one of the two triggers: `stop`, by which every container sets the stop flag after its first unit, so that
    each stops before its second; and `kill`, by which the first batch's container, inside its second unit, commits the
    volume after the unit file's rename and before its marker, and kills itself, once."""
    s = LG.stage_named(stage, design_of(rehearsal))
    if not rehearsal:
        if trigger is not None:
            raise LaunchRefusal("a trigger is for a rehearsal alone")
        specs = []
        for batch in STAGE_BATCHES[stage]:
            spec = {"arm": s.arm, "side": s.side, "batch": batch, "commit": commit, "mode": "deciding", "root": volume_root(s.arm, commit, 0), "units": "units",
                    "run": run_key(0)}
            if s.side == "heldout":
                spec["attack_batches"] = list(BATCHES[s.arm]["attack"])
            specs.append(spec)
        return specs
    if trigger is not None and trigger not in TRIGGERS:
        raise LaunchRefusal("not a trigger")
    specs = []
    for batch in REHEARSAL_STAGE_BATCHES[stage]:
        spec = {"arm": s.arm, "side": s.side, "batch": batch, "commit": commit, "mode": "rehearsal", "root": volume_root(s.arm, commit, rehearsal),
                "units": REHEARSAL_UNITS[(s.arm, s.side)], "run": run_key(rehearsal), "allow_pool": batch}
        if s.side == "heldout":
            spec["attack_batches"] = [batch]
            spec["attack_units"] = REHEARSAL_UNITS[(s.arm, "attack")]
        if s.delta_held:
            spec["n_steps"] = REHEARSAL_DELTA_STEPS
        if trigger == "stop":
            spec["stop_after_first_unit"] = True
        if trigger == "kill" and batch == REHEARSAL_STAGE_BATCHES[stage][0]:
            spec["kill_at"], spec["kill_after"] = "unit_renamed", "between_units"
            spec["kill_key"] = f"killed|{run_key(rehearsal)}|{commit[:12]}|{stage}|{batch}"
        specs.append(spec)
    return specs


def _manifest() -> dict[str, Any]:
    from vpd_audit_2.manifest import OUT_DIR

    return json.load(open(OUT_DIR / "manifest.json"))


def container_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                     pools: dict[str, Any] | None = None) -> tuple[np.ndarray, list[str]]:
    """The token ids of the container's one batch, with each text's SHA-256 from the manifest. The batch must be a
    pool of the container's side, by the manifest and by its name; no other pool's ids are loaded. For a rehearsal the
    batch must be one of its calibration batches, and the spec must name it as its override of the pool check."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = _manifest()["pools"] if pools is None else pools
    batch, side = spec["batch"], spec["side"]
    pool = pools[batch]
    if spec.get("mode") == "rehearsal":
        on_side = pool["pool"] == "C" and batch in REHEARSAL_BATCHES and spec.get("allow_pool") == batch and spec["arm"] in ("rehearsal", "rehearsal_delta_on")
    else:
        on_side = (pool["pool"] == LR.SIDE_PREFIX[side] and pool["side"] == {"attack": "attack", "heldout": "held-out"}[side]
                   and batch in BATCHES[spec["arm"]][side] and "allow_pool" not in spec)
    if not on_side:
        raise LaunchRefusal(f"batch {batch} is not a pool of the {side} side")
    ids, _texts, rows = load_ids(batch)
    return ids, list(rows)


def starts_for(indices: tuple[int, ...] = LR.STARTS) -> dict[int, dict[str, np.ndarray]]:
    """The starting points, from the signed file, checked against its signed SHA-256."""
    from vpd_audit_2 import pilot as P

    if LT.sha256_file(STARTS_NPZ) != LR.SIGNED_SHA256["starts"]:
        raise LaunchRefusal("the starts file is not the signed one")
    return {s: P.load_extended_start(s) for s in indices}


def rehearsal_starts() -> dict[int, dict[str, np.ndarray]]:
    """Pilot start 1, from the signed file, and equal to the manifest's own copy of it."""
    from vpd_audit_2.manifest import load_start

    starts = starts_for(LR.REHEARSAL_STARTS)
    reference = load_start(REHEARSAL_START)
    if not all(np.array_equal(starts[REHEARSAL_START][k], reference[k]) for k in reference):
        raise LaunchRefusal("the start is not the signed one")
    return starts


def strata_by_module() -> tuple[dict[str, np.ndarray], str]:
    """The committed strata, loaded and checked against their recorded SHA-256, never recomputed."""
    from vpd_audit_2 import pilot as P

    meta = json.load(open(STRATA_JSON))
    sha = LT.sha256_file(STRATA_NPZ)
    if sha != meta["file_sha256"] or not (sha.startswith(STRATA_SHA_ENDS[0]) and sha.endswith(STRATA_SHA_ENDS[1])):
        raise LaunchRefusal("the strata file is not the committed one")
    with np.load(STRATA_NPZ) as z:
        stratum = z["stratum"]
    return P.strata_by_module(stratum, meta, P.layout()), sha


def inputs_sha256() -> dict[str, str]:
    from vpd_audit_2.manifest import OUT_DIR

    out = {"manifest": LT.sha256_file(OUT_DIR / "manifest.json"), "starts": LT.sha256_file(STARTS_NPZ), "strata": LT.sha256_file(STRATA_NPZ),
           "heldout_span_overlap": LT.sha256_file(OVERLAP_JSON)}
    if out["manifest"] != LR.SIGNED_SHA256["manifest"] or out["starts"] != LR.SIGNED_SHA256["starts"]:
        raise LaunchRefusal("the manifest or the starts file is not the signed one")
    return out


def heldout_texts(heldout: list[str]) -> tuple[list[list[str]], list[dict[str, Any]]]:
    """Each held-out batch's text ids in the manifest's order, and the committed list of overlapping held-out texts."""
    pools = _manifest()["pools"]
    return [list(pools[name]["texts"]) for name in heldout], list(json.load(open(OVERLAP_JSON))["texts"])


def pilot_search(batch: str, start: int) -> dict[str, Any]:
    """The pilot's stored run of a calibration batch from a pilot start: its record, its saved settings' hashes, and the
    steps they were saved at (`results/s4_pilot/part_a/runs.json`). These are open."""
    run = json.load(open(PILOT_RUNS))["a1"][batch][str(start)]
    return {k: run[k] for k in ("record", "saved_sources_sha256", "hook_events")}


# ----------------------------------------------------------------------------- the checks before a deciding job


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True)


def head_commit() -> str:
    return _git("rev-parse", "--verify", "HEAD^{commit}").stdout.strip()


def tree_is_clean() -> bool:
    """No change to a tracked file and no untracked file under `vpd-audit-2/`."""
    r = _git("status", "--porcelain", "--", ".")
    return r.returncode == 0 and r.stdout.strip() == ""


def blob(commit: str, rel: str) -> str | None:
    top = _git("rev-parse", "--show-toplevel").stdout.strip()
    prefix = REPO_ROOT.resolve().relative_to(Path(top).resolve()).as_posix()
    r = _git("rev-parse", "--verify", "--quiet", f"{commit}:{prefix}/{rel}")
    return r.stdout.strip() if r.returncode == 0 else None


def run_files_changed(since: str, commit: str) -> list[str]:
    return [rel for rel in RUN_FILES if blob(since, rel) is None or blob(since, rel) != blob(commit, rel)]


def tree_holds_only_the_runs_records() -> bool:
    """No change to a tracked file under `vpd-audit-2/`, and no untracked file there but the run's own records under
    `results/s5_lead/`. A run's stages write their records as they go, and the whole run carries one commit, so the
    records cannot be committed between its stages; they are the one thing the tree may hold."""
    top = Path(_git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    allowed = (RESULTS.resolve().relative_to(top)).as_posix() + "/"
    r = _git("status", "--porcelain", "--untracked-files=all", "--", ".")
    return r.returncode == 0 and all(line.startswith("?? ") and line[3:].strip('"').startswith(allowed) for line in r.stdout.splitlines())


def check_rehearsal_commit(commit: str, earlier: str | None) -> None:
    """Before a rehearsal's job: the current commit is the one named, the tree holds nothing but the rehearsal's own
    records, and the rehearsal began at this commit (`earlier`: the commit of its first job, if it has had one)."""
    if not tree_holds_only_the_runs_records():
        raise LaunchRefusal("the tree is not clean under vpd-audit-2")
    if head_commit() != commit or len(commit) != 40:
        raise LaunchRefusal("the current commit is not the one named")
    if earlier is not None and earlier != commit:
        raise LaunchRefusal("the rehearsal began at another commit")


def check_deciding_commit(commit: str, rehearsal_commit: str) -> None:
    """Before any deciding job (plan 2 of the research log, Sections 5.3 and 8): the tree is clean at the commit the go-ahead named, but
    for the run's own records; that commit descends from Part A; every module the run imports is byte-identical to the
    rehearsal's; and the multipliers file is committed."""
    if not tree_holds_only_the_runs_records():
        raise LaunchRefusal("the tree is not clean under vpd-audit-2")
    if head_commit() != commit or len(commit) != 40:
        raise LaunchRefusal("the current commit is not the one named")
    if _git("merge-base", "--is-ancestor", PART_A_COMMIT, commit).returncode != 0:
        raise LaunchRefusal("the commit does not descend from the Part A commit")
    changed = run_files_changed(rehearsal_commit, commit)
    if changed:
        raise LaunchRefusal("the rehearsal does not cover the code that runs: changed since it: " + ", ".join(changed))
    if blob(commit, "freeze/amendment1_multipliers.md") is None or not MULTIPLIERS_MD.is_file():
        raise LaunchRefusal("the multipliers file is not committed")


def rehearsal_of_record(results: Path | None = None) -> tuple[int, dict[str, Any]]:
    """The latest repeat rehearsal's record. A deciding stage rests on it: it must have met every required outcome, and
    its commit must cover the code that runs."""
    results = RESULTS if results is None else results
    attempts = sorted(int(p.name.split("_")[1]) for p in results.glob("rehearsal_*") if p.name.split("_")[1].isdigit() and (p / "ledger.json").is_file())
    if not attempts:
        raise LaunchRefusal("there is no repeat rehearsal")
    path = results / f"rehearsal_{attempts[-1]}" / "rehearsal.json"
    if not path.is_file():
        raise LaunchRefusal("the latest rehearsal has no record")
    record = json.load(open(path))
    if record.get("all_required_outcomes_met") is not True:
        raise LaunchRefusal("the latest rehearsal did not meet every required outcome")
    return attempts[-1], record


# ----------------------------------------------------------------------------- the ledger


def read_ledger(path: Path) -> dict[str, Any]:
    return json.load(open(path)) if Path(path).is_file() else {"stages": {}, "checks": [], "bills": [], "guards_pass": None, "stopped_by": None, "stops": []}


def counted(wait: float, returned: dict[str, Any] | None) -> float:
    """What a container's call adds to its stage's function seconds: the container's own seconds where its first life
    returned them; the launcher's whole wait for it where the result came from a later life, or never came."""
    if returned is not None and returned.get("attempts") == 1:
        return float(returned["seconds"])
    return float(wait)


def close_open_launches(ledger: dict[str, Any], allowance: float) -> None:
    """A launch whose launcher died wrote no end. Its calls that had not come back are counted from their start to the
    launcher's last sign of life, plus the time between two signs."""
    for stage in ledger["stages"].values():
        for launch in stage["launches"]:
            if launch["ended"] is not None:
                continue
            for batch, at in launch["spawned"].items():
                if batch not in launch["calls"]:
                    wait = max(0.0, launch["last_alive"] - at) + allowance
                    launch["calls"][batch] = {"outcome": "unreturned", "wait_seconds": wait, "returned_seconds": None, "attempts": None, "lives": 1,
                                              "counted_seconds": wait, "error": None, "stopped": None, "finished_units": None, "expected_units": None}
            launch["ended"] = "closed by a later launch"
            launch["function_seconds"] = sum(c["counted_seconds"] for c in launch["calls"].values())
            launch["container_lives"] = sum(c["lives"] for c in launch["calls"].values())


def ledger_counts(ledger: dict[str, Any], bill: dict[str, Any] | None = None) -> dict[str, Any]:
    """A ledger's function seconds and container lives over every launch of every stage, with the seconds of its
    guards-only pass; and its bill, where one has posted for any of its apps."""
    launches = [x for s in ledger["stages"].values() for x in s["launches"]]
    seconds = sum(x.get("function_seconds") or 0.0 for x in launches) + ((ledger.get("guards_pass") or {}).get("seconds") or 0.0)
    lives = sum(x.get("container_lives") or 0 for x in launches)
    apps = ledger_apps(ledger)
    posted = [v for k, v in (bill or {}).get("by_app", {}).items() if k in apps]
    return {"function_seconds": float(seconds), "container_lives": float(lives), "billed": float(sum(posted)) if posted else None}


def ledger_apps(ledger: dict[str, Any]) -> list[str]:
    apps = [x["app_id"] for s in ledger["stages"].values() for x in s["launches"]]
    apps += [a for a in [(ledger.get("guards_pass") or {}).get("app_id")] if a]
    return sorted(set(apps))


def stage_seconds_on(ledger: dict[str, Any], name: str) -> float:
    return float(sum(x.get("function_seconds") or 0.0 for x in ledger["stages"].get(name, {}).get("launches", [])))


def rehearsal_counts(results: Path | None = None, bill: dict[str, Any] | None = None) -> dict[str, Any]:
    """What the rehearsals have cost, in function seconds and container lives, which the cap covers
    (Amendment 4, Section 2): the first rehearsal from its record, and each repeat from its ledger and its assembly."""
    results = RESULTS if results is None else results
    by_app = (bill or {}).get("by_app", {})
    parts, apps = [], []
    first = results / "rehearsal" / "rehearsal.json"
    if first.is_file():
        r = json.load(open(first))
        apps.append(r["app_id"])
        parts.append({"function_seconds": r["function_seconds"], "container_lives": FIRST_REHEARSAL_LIVES, "billed": by_app.get(r["app_id"])})
    for folder in sorted(results.glob("rehearsal_*")):
        if not (folder / "ledger.json").is_file():
            continue
        ledger = json.load(open(folder / "ledger.json"))
        c = ledger_counts(ledger, bill)
        apps += ledger_apps(ledger)
        if (folder / "assemble.json").is_file():
            a = json.load(open(folder / "assemble.json"))
            c["function_seconds"] += sum(x["seconds"] for x in a["arms"].values())
            apps.append(a["app_id"])
            if a["app_id"] in by_app:
                c["billed"] = (c["billed"] or 0.0) + by_app[a["app_id"]]
        parts.append(c)
    return {**LG.add(*parts), "app_ids": sorted(set(apps))} if parts else {"function_seconds": 0.0, "container_lives": 0.0, "billed": None, "app_ids": []}


# ----------------------------------------------------------------------------- the launcher


@dataclass
class Cloud:
    """What the launcher needs of the cloud, as plain functions, so that the launcher can be tested without it."""

    spawn: Callable[[dict[str, Any]], Any]  # a spec to a call; `call.get(timeout=seconds)` returns the container's return, raises the built-in TimeoutError while it runs, or raises what the container raised
    set_stop: Callable[[bool], None]  # this run's stop flag
    attempts: Callable[[dict[str, Any]], int]  # how many lives a spec's container has had in this launch; 0 if unknown
    read_bill: Callable[[list[str]], dict[str, Any]]  # app ids to {"read_at", "by_app": {app id: dollars posted}}
    guards: Callable[[dict[str, Any]], dict[str, Any]]  # the guards-only pass: a spec to {"outcomes": {guard: true or false}, "seconds"}
    app_id: str
    log: Callable[..., None]
    clock: Callable[[], float] = time.time


def stage_summary(stage: str, returns: list[dict[str, Any]]) -> dict[str, Any]:
    """What a finished stage leaves on the open record (plan 2 of the research log, Section 8): counts of finished units against the
    expected counts, one hash per unit file, seconds per container, and guard outcomes as true or false."""
    units = [u for r in returns for u in r["units"]]
    return {"stage": stage, "containers": len(returns), "finished_units": sum(r["finished_units"] for r in returns),
            "expected_units": sum(r["expected_units"] for r in returns), "stopped": any(r["stopped"] for r in returns),
            "function_seconds": sum(r["seconds"] for r in returns), "all_guards_true": all(all(u["guards"].values()) for u in units),
            "complete": all(r["finished_units"] == r["expected_units"] and not r["stopped"] for r in returns)}


def guards_acceptable(outcomes: dict[str, bool], accept_expected_refusals: bool) -> bool:
    """The guards-only pass must find every cross-unit guard true. A rehearsal, with one batch on both sides, must find
    the two wrong-batch guards false and every other true, with every carried vector reported equal; under its flag
    that pattern, and no other, is accepted."""
    required_true = all(outcomes.get(g) is True for g in LR.REQUIRED_GUARDS)
    if not accept_expected_refusals:
        return required_true and all(outcomes.get(g) is True for g in LR.WRONG_BATCH_GUARDS)
    return (required_true and all(outcomes.get(g) is False for g in LR.WRONG_BATCH_GUARDS) and outcomes.get("G6_reports_every_carried_vector_equal") is True
            and outcomes.get("G11_reports_every_carried_vector_equal_to_the_heldout_own") is True)


def take_guards_pass(ledger: dict[str, Any], cloud: Cloud, guards_spec: dict[str, Any] | None) -> list[str]:
    """Run the guards-only pass and put what it found on the ledger: each guard's name with true or false. Returns what
    was not found true: the guards' names, or, if the pass itself failed, its failure by guard and unit or by type."""
    found: dict[str, Any] = {"at": utc_now(), "app_id": cloud.app_id, "outcomes": {}, "seconds": 0.0, "error": None}
    try:
        g = cloud.guards(guards_spec or {})
        found.update(outcomes=g["outcomes"], seconds=float(g["seconds"]))
    except (LR.GuardFailure, LR.ContainerFailure) as exc:
        found["error"] = str(exc)
    except Exception as exc:  # noqa: BLE001  (by its type alone; the pass is taken again before wave 2)
        found["error"] = f"{type(exc).__name__} outside the pass's own code"
    ledger["guards_pass"] = found
    if found["error"]:
        return [found["error"]]
    return sorted(k for k in LR.REQUIRED_GUARDS + LR.WRONG_BATCH_GUARDS if found["outcomes"].get(k) is not True)


def drive_stage(stage: LG.Stage, specs: list[dict[str, Any]], cloud: Cloud, *, ledger_path: Path, runs_path: Path, design: tuple[LG.Stage, ...],
                timings: dict[str, float], listed_hourly_price: float, cap: float, outside: Callable[[dict[str, Any]], dict[str, Any]], commit: str,
                guards_spec: dict[str, Any] | None = None, accept_expected_refusals: bool = False, trigger: str | None = None,
                poll_seconds: float = 20.0) -> dict[str, Any]:
    """Launch one stage's containers at once, wait for them, and keep the ledger (plan 4 of the research log, Sections 4.1 to 4.3).

      - A container's failure is recorded by its guard and unit, or by its error's type and place, and the other
        containers finish.
      - Each launch of a stage is added to the stage's entry. A container whose first life did not return is counted
        by the launcher's wait for it, and every life is counted for its boot.
      - After the design's first stage comes check C1. After its second, the one held-out container of wave 1, come
        check C2 and the guards-only pass. After its third comes check C3. A check over the cap, or a guard found
        false, stops the run here: the stage is recorded, and no later stage will launch.

    `outside(bill)` gives the money spent outside this ledger that the cap covers: function seconds, container lives,
    the posted bill, and the app ids to read bills for."""
    idx = design.index(stage)
    if (accept_expected_refusals or trigger is not None) and not stage.arm.startswith("rehearsal"):
        raise LaunchRefusal("a trigger, or a refusal accepted, is for a rehearsal alone")
    ledger = read_ledger(ledger_path)
    close_open_launches(ledger, poll_seconds)
    done = {name: bool(s.get("complete")) for name, s in ledger["stages"].items()}
    if any(not done.get(s.name) for s in design[:idx]):
        raise LaunchRefusal("an earlier stage is not complete")
    if done.get(stage.name):
        raise LaunchRefusal("the stage is already complete")
    if any(c["exceeds_cap"] for c in ledger["checks"]):
        raise LaunchRefusal("a spend check has stopped the run")
    if idx == 2:  # wave 2 waits for the guards-only pass; a pass that never ran, or failed to run, is taken now
        if ledger.get("guards_pass") is None or ledger["guards_pass"].get("error"):
            take_guards_pass(ledger, cloud, guards_spec)
            write_json(ledger_path, ledger)
        if not guards_acceptable(ledger["guards_pass"]["outcomes"], accept_expected_refusals):
            raise LaunchRefusal("the guards-only pass has not passed")

    entry = ledger["stages"].setdefault(stage.name, {"launches": [], "complete": False, "summary": None})
    launch = {"launch": f"{cloud.app_id}|{stage.name}|{len(entry['launches']) + 1}", "app_id": cloud.app_id, "commit": commit, "began": utc_now(),
              "last_alive": cloud.clock(), "ended": None, "trigger": trigger, "accepted_expected_refusals": bool(accept_expected_refusals and idx == 2),
              "spawned": {}, "calls": {}, "function_seconds": None, "container_lives": None}
    entry["launches"].append(launch)
    ledger["stopped_by"] = None
    cloud.set_stop(False)
    pending: dict[str, tuple[dict[str, Any], Any]] = {}
    for spec in specs:
        spec = {**spec, "launch": launch["launch"]}
        pending[spec["batch"]] = (spec, cloud.spawn(spec))
        launch["spawned"][spec["batch"]] = cloud.clock()
    write_json(ledger_path, ledger)
    cloud.log(event="stage_started", container=stage.name, count=len(pending))

    returns: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}

    def settle(batch: str, out: dict[str, Any] | None, error: str | None, outcome: str) -> None:
        spec, _ = pending.pop(batch)
        wait = cloud.clock() - launch["spawned"][batch]
        attempts = int(out.get("attempts") or 0) if out is not None else 0
        lives = max(1, attempts or cloud.attempts(spec))
        launch["calls"][batch] = {"outcome": outcome, "wait_seconds": wait, "returned_seconds": float(out["seconds"]) if out is not None else None,
                                  "attempts": attempts or None, "lives": lives, "counted_seconds": counted(wait, out), "error": error,
                                  "stopped": bool(out["stopped"]) if out is not None else None,
                                  "finished_units": int(out["finished_units"]) if out is not None else None,
                                  "expected_units": int(out["expected_units"]) if out is not None else None}

    try:
        while pending:
            for batch, (_, call) in list(pending.items()):
                try:
                    out = call.get(timeout=max(1.0, poll_seconds / len(pending)))
                except TimeoutError:
                    out = None
                except (LR.GuardFailure, LR.ContainerFailure) as exc:  # the guard and its unit, or the error's type and place
                    errors[batch] = str(exc)
                    settle(batch, None, errors[batch], "error")
                    continue
                except Exception as exc:  # noqa: BLE001  (anything else, by its type alone: the other containers go on)
                    errors[batch] = f"{type(exc).__name__} outside the container's own code"
                    settle(batch, None, errors[batch], "error")
                    continue
                finally:
                    launch["last_alive"] = cloud.clock()
                    write_json(ledger_path, ledger)
                if out is not None:
                    returns[batch] = out
                    settle(batch, out, None, "returned")
    finally:  # however the wait ends, what was launched is counted
        for batch in list(pending):
            settle(batch, None, None, "unreturned")
        launch["ended"] = utc_now()
        launch["function_seconds"] = sum(c["counted_seconds"] for c in launch["calls"].values())
        launch["container_lives"] = sum(c["lives"] for c in launch["calls"].values())
        write_json(ledger_path, ledger)

    summary = stage_summary(stage.name, list(returns.values()))
    summary["errors"] = errors
    summary["complete"] = bool(summary["complete"] and not errors and len(returns) == len(specs))
    entry["summary"], entry["complete"] = summary, summary["complete"]
    # the stage's record: this launch's returns, kept under the launch's number as well, so that a relaunch loses nothing
    run = {"stage": stage.name, "commit": commit, "app_id": cloud.app_id, "launch": launch["launch"], "summary": summary,
           "containers": [returns[b] for b in sorted(returns)]}
    write_json(runs_path, run)
    write_json(runs_path.with_name(f"{runs_path.stem}_launch_{len(entry['launches'])}.json"), run)

    stopped_by: list[str] = []
    if summary["complete"] and idx in LG.CHECK_AFTER:
        measured = {s.name: stage_seconds_on(ledger, s.name) for s in design if ledger["stages"].get(s.name, {}).get("complete")}
        rest = design[idx + 1:]
        if idx == 1:  # check C2: the rest of the held-out side at the larger of this container's seconds and the projection
            remaining = LG.remaining_after_first_heldout(design, timings, measured, measured[stage.name])
        else:
            remaining = LG.remaining_seconds(rest, timings, measured, design)
        bill = cloud.read_bill(sorted(set(ledger_apps(ledger) + outside({})["app_ids"])))
        ledger["bills"].append(bill)
        spent = LG.add(ledger_counts(ledger, bill), outside(bill))
        check = LG.check_later(LG.CHECK_AFTER[idx], spent_so_far=spent, remaining_seconds=remaining, remaining_lives=sum(s.containers for s in rest),
                               listed_hourly_price=listed_hourly_price, cap=cap)
        check.update({"at": utc_now(), "after_stage": stage.name, "bill_read_at": bill.get("read_at"), "measured_seconds": measured})
        ledger["checks"].append(check)
        if check["exceeds_cap"]:
            stopped_by.append(check["check"])
        if idx == 1:  # the guards-only pass: the assembler's cross-unit guards on this container's blocks, true or false
            false = take_guards_pass(ledger, cloud, guards_spec)
            if false:
                stopped_by.append("the guards-only pass: " + ", ".join(false))
    ledger["stopped_by"] = stopped_by or None
    if stopped_by:
        ledger["stops"].append({"at": utc_now(), "after_stage": stage.name, "by": stopped_by})
    write_json(ledger_path, ledger)
    cloud.log(event="stage_finished", container=stage.name, count=summary["finished_units"], ok=bool(summary["complete"] and not stopped_by))
    if errors or not summary["complete"]:
        raise LaunchRefusal("the stage did not finish cleanly: see the ledger and the stage's record, and report")
    if stopped_by:
        raise LaunchRefusal("the run stops here: " + "; ".join(stopped_by) + ". Stop and report")
    return summary


# ----------------------------------------------------------------------------- sealed tables, as bytes


def receive_table(arm_dir: Path, name: str, data: bytes, expected_sha256: str) -> None:
    """Write one file of a sealed table under `<arm>/sealed/`, after checking its bytes against the assembler's hash.
    The bytes are never parsed."""
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise LaunchRefusal(f"the bytes of {name} do not have the hash the assembler returned")
    sealed = arm_dir / "sealed"
    sealed.mkdir(parents=True, exist_ok=True)
    (sealed / "DO_NOT_OPEN.md").write_text(NOTICE)
    (sealed / name).write_bytes(data)


def write_receipt(arm_dir: Path, assembled: dict[str, Any]) -> dict[str, Any]:
    """The unsealed receipt beside a sealed table: each file's name and SHA-256, the declared sizes, the completeness
    flag, and the run's commit. The analysis's entry point checks the table against it."""
    for f in assembled["files"]:
        if LT.sha256_file(arm_dir / "sealed" / f["name"]) != f["sha256"]:
            raise LaunchRefusal(f"the copy of {f['name']} does not have the hash the assembler returned")
    receipt = {"arm": assembled["arm"], "files": [{"name": f["name"], "sha256": f["sha256"]} for f in assembled["files"]],
               "shapes": assembled["design"], "complete": assembled["complete"], "run_commit": assembled["run_commit"]}
    (arm_dir / "receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")
    return receipt


def returned_hashes(runs: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Each unit's SHA-256 as its container returned it, by side, from the stages' records."""
    out: dict[str, dict[str, str]] = {"attack": {}, "heldout": {}}
    for run in runs:
        for c in run["containers"]:
            side = c["container"].split("|")[1]
            out[side].update({u["unit"]: u["sha256"] for u in c["units"]})
    return out


def assemble_arms(arms: list[dict[str, Any]], *, assemble: Callable[[dict[str, Any]], dict[str, Any]], read_file: Callable[[str], bytes], out_path: Path,
                  commit: str, app_id: str, log: Callable[..., None]) -> dict[str, Any]:
    """Assemble each arm's table on the volume, copy it to the local side as bytes, and write its receipt. Each arm is
    `{"key", "spec", "results"}`: the assembler's spec and the local folder for the table. An arm with `pairs_with`
    is handed that arm's fingerprints of labels and targets, for the cross-arm pairing check (plan 2 of the research log, Section 5.1)."""
    record: dict[str, Any] = {}
    fingerprints: dict[str, Any] = {}
    for arm in arms:
        spec = dict(arm["spec"])
        if arm.get("pairs_with"):
            spec["lead_prep_fp"] = fingerprints[arm["pairs_with"]]
        out = assemble(spec)
        fingerprints[arm["key"]] = out["prep_fp"]
        for f in out["files"]:
            receive_table(arm["results"], f["name"], read_file(f"{out['table_dir']}/{f['name']}"), f["sha256"])
        receipt = write_receipt(arm["results"], out)
        record[arm["key"]] = {"receipt": receipt, "outcomes": out["outcomes"], "prep_fp_equal_to_lead": out["prep_fp_equal_to_lead"], "seconds": out["seconds"]}
        log(event="table_copied", container=arm["key"], count=len(receipt["files"]), ok=bool(out["complete"]))
    write_json(out_path, {"commit": commit, "app_id": app_id, "at": utc_now(), "arms": record})
    return record


def backup_units(groups: list[dict[str, Any]], *, read_file: Callable[[str], bytes], dest: Path, out_path: Path, commit: str, log: Callable[..., None]) -> dict[str, str]:
    """One copy of every search unit's file off the volume, as bytes, unopened, to a local folder that git ignores, with
    a do-not-open notice in it. Each group is `{"name", "remote", "units"}`: a folder's name here, the folder on the
    volume, and each search unit's SHA-256 as its container returned it, which the bytes must have."""
    hashes: dict[str, str] = {}
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "DO_NOT_OPEN.md").write_text(NOTICE)
    for group in groups:
        (dest / group["name"]).mkdir(parents=True, exist_ok=True)
        (dest / group["name"] / "DO_NOT_OPEN.md").write_text(NOTICE)
        for unit, sha in sorted(group["units"].items()):
            _, _, batch, s = unit.split("|")
            name = LR.search_file(Path("."), batch, int(s[1:])).name
            data = read_file(f"{group['remote']}/{name}")
            if hashlib.sha256(data).hexdigest() != sha:
                raise LaunchRefusal(f"the bytes of {name} do not have the hash its container returned")
            (dest / group["name"] / name).write_bytes(data)
            hashes[f"{group['name']}/{name}"] = sha
            del data
    write_json(out_path, {"commit": commit, "at": utc_now(), "folder": str(dest.relative_to(REPO_ROOT)) if dest.is_relative_to(REPO_ROOT) else str(dest),
                          "notice": "DO_NOT_OPEN.md", "files": hashes})
    log(event="backup_finished", container="units", count=len(hashes))
    return hashes


def search_units_by_group(runs: list[dict[str, Any]], remote_of: Callable[[dict[str, Any]], tuple[str, str]]) -> list[dict[str, Any]]:
    """The search units of the stages' records, grouped by the folder they are in: `remote_of(container's return)` gives
    a group's name and its folder on the volume."""
    groups: dict[str, dict[str, Any]] = {}
    for run in runs:
        for c in run["containers"]:
            name, remote = remote_of(c)
            g = groups.setdefault(name, {"name": name, "remote": remote, "units": {}})
            g["units"].update({u["unit"]: u["sha256"] for u in c["units"] if u["unit"].startswith("search|")})
    return [groups[k] for k in sorted(groups)]


# ----------------------------------------------------------------------------- what the commands are to do


def stage_runs(folder: Path, names: list[str]) -> list[dict[str, Any]]:
    """The latest record of each named stage, as `drive_stage` wrote it."""
    missing = [n for n in names if not (folder / f"runs_{n}.json").is_file()]
    if missing:
        raise LaunchRefusal("a stage has no record: " + ", ".join(missing))
    return [json.load(open(folder / f"runs_{n}.json")) for n in names]


def _only(runs: list[dict[str, Any]], batch: str | None = None) -> list[dict[str, Any]]:
    """The records with their containers narrowed to one batch's."""
    return [{**r, "containers": [c for c in r["containers"] if batch is None or c["container"].split("|")[2] == batch]} for r in runs]


def _containers(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"container": c["container"], "seconds": c["seconds"], "environment": c["environment"]} for r in runs for c in r["containers"]]


def guards_plan(commit: str, rehearsal: int) -> dict[str, Any]:
    """The guards-only pass after wave 1 (plan 4 of the research log, Section 4.3): the lead's one held-out batch of wave 1 against every
    attack search. In a rehearsal, the first calibration batch against itself."""
    if rehearsal:
        root, batch = volume_root("rehearsal", commit, rehearsal), REHEARSAL_STAGE_BATCHES["rehearsal_heldout_1"][0]
        return {"arm": "rehearsal", "units": f"{root}/sealed/{REHEARSAL_UNITS[('rehearsal', 'attack')]}",
                "heldout_units": f"{root}/sealed/{REHEARSAL_UNITS[('rehearsal', 'heldout')]}", "attack": [batch], "heldout": [batch],
                "starts": list(LR.REHEARSAL_STARTS), "commit": commit, "rehearsal": True}
    return {"arm": "lead", "units": f"{volume_root('lead', commit, 0)}/sealed/units", "attack": list(BATCHES["lead"]["attack"]),
            "heldout": list(STAGE_BATCHES["lead_heldout_1"]), "starts": list(LR.STARTS), "commit": commit, "rehearsal": False}


def assemble_plan(commit: str, rehearsal: int, folder: Path) -> list[dict[str, Any]]:
    """The arms `assemble_arms` is to build, from the records the stages wrote. The run has two: the lead's table, and
    the delta-on arm's, paired with it. A rehearsal has two for each calibration batch, each a table of one batch on
    both sides, written with the rehearsal's small part size."""
    inputs = inputs_sha256()
    if not rehearsal:
        arms = []
        for arm, stages in (("lead", ["lead_attack", "lead_heldout_1", "lead_heldout_2"]), ("delta_on", ["delta_attack", "delta_heldout"])):
            runs = stage_runs(folder, stages)
            heldout = list(BATCHES[arm]["heldout"])
            text_ids, excluded = heldout_texts(heldout)
            root = volume_root(arm, commit, 0)
            spec = {"arm": arm, "root": root, "table": "table", "units": f"{root}/sealed/units", "attack": list(BATCHES[arm]["attack"]), "heldout": heldout,
                    "starts": list(LR.STARTS), "text_ids_H": text_ids, "excluded": excluded, "inputs_sha256": inputs, "containers": _containers(runs),
                    "commit": commit, "returned_sha256": returned_hashes(runs)}
            arms.append({"key": arm, "spec": spec, "results": folder / arm, "pairs_with": "lead" if arm == "delta_on" else None})
        return arms
    arms = []
    for batch in REHEARSAL_BATCHES:
        for arm, stages in (("rehearsal", ["rehearsal_attack", "rehearsal_heldout_1", "rehearsal_heldout_2"]),
                            ("rehearsal_delta_on", ["rehearsal_delta_attack", "rehearsal_delta_heldout"])):
            runs = _only(stage_runs(folder, stages), batch)
            text_ids, excluded = heldout_texts([batch])
            root = volume_root(arm, commit, rehearsal)
            key = f"{batch}_{arm}"
            spec = {"arm": arm, "root": root, "table": f"table_{key}", "units": f"{root}/sealed/{REHEARSAL_UNITS[(arm, 'attack')]}",
                    "heldout_units": f"{root}/sealed/{REHEARSAL_UNITS[(arm, 'heldout')]}", "attack": [batch], "heldout": [batch],
                    "starts": list(LR.REHEARSAL_STARTS), "text_ids_H": text_ids, "excluded": excluded, "inputs_sha256": inputs, "containers": _containers(runs),
                    "commit": commit, "returned_sha256": returned_hashes(runs), "rehearsal": True, "part_bytes": REHEARSAL_PART_BYTES,
                    "pilot": pilot_search(batch, REHEARSAL_START) if arm == "rehearsal" else None}
            arms.append({"key": key, "spec": spec, "results": folder / key, "pairs_with": f"{batch}_rehearsal" if arm == "rehearsal_delta_on" else None})
    return arms


def backup_plan(commit: str, rehearsal: int, folder: Path) -> list[dict[str, Any]]:
    """The folders of search units `backup_units` is to copy, with each unit's hash as its container returned it."""
    if not rehearsal:
        groups = []
        for arm, stages in (("lead", ["lead_attack", "lead_heldout_1", "lead_heldout_2"]), ("delta_on", ["delta_attack", "delta_heldout"])):
            groups += search_units_by_group(stage_runs(folder, stages), lambda c, arm=arm: (arm, f"{volume_root(arm, commit, 0)}/sealed/units"))
        return groups
    root = volume_root("rehearsal", commit, rehearsal)

    def of(c: dict[str, Any]) -> tuple[str, str]:
        arm, side, _ = c["container"].split("|")
        return REHEARSAL_UNITS[(arm, side)], f"{root}/sealed/{REHEARSAL_UNITS[(arm, side)]}"

    return search_units_by_group(stage_runs(folder, [s.name for s in LG.REHEARSAL_DESIGN]), of)


def record_c0(ledger_path: Path, c0: dict[str, Any]) -> None:
    """Check C0 on the run's ledger, before its first job. Over the cap, the run does not start."""
    ledger = read_ledger(ledger_path)
    ledger["checks"] = [c for c in ledger["checks"] if c["check"] != "C0"] + [{**c0, "at": utc_now()}]
    write_json(ledger_path, ledger)
    if c0["exceeds_cap"]:
        raise LaunchRefusal("check C0: the projection exceeds the cap. Do not start; report")


def began_at(ledger_path: Path) -> str | None:
    """The commit of a ledger's first launch, if it has had one."""
    launches = [x for s in read_ledger(ledger_path)["stages"].values() for x in s["launches"]]
    return launches[0]["commit"] if launches else None


def no_spend_outside(bill: dict[str, Any]) -> dict[str, Any]:
    return {"function_seconds": 0.0, "container_lives": 0.0, "billed": None, "app_ids": []}


def stage_command(name: str, commit: str, rehearsal: int, cloud: Cloud, *, listed_hourly_price: float, trigger: str | None = None,
                  accept_expected_refusals: bool = False) -> dict[str, Any]:
    """The `stage` command: the checks before a stage's jobs, then `drive_stage`.

    A deciding stage rests on the latest repeat rehearsal: its record must have met every required outcome, no file
    the run imports may have changed since its commit, and its timings are the projection's. Before the run's first job
    check C0 is taken again, with the rehearsals' bills as they then stand. A rehearsal's stage prices the rehearsal
    itself, against the figure at which it stops and reports."""
    design = design_of(rehearsal)
    stage = LG.stage_named(name, design)
    folder = results_folder(rehearsal)
    ledger_path = folder / "ledger.json"
    earlier = began_at(ledger_path)
    if rehearsal:
        check_rehearsal_commit(commit, earlier)
        timings, cap, outside = REHEARSAL_EXPECTED_TIMINGS, REHEARSAL_STOP_DOLLARS, no_spend_outside
    else:
        if trigger or accept_expected_refusals:
            raise LaunchRefusal("a trigger, or a refusal accepted, is for a rehearsal alone")
        _, reh = rehearsal_of_record()
        check_deciding_commit(commit, reh["commit"])
        if earlier is not None and earlier != commit:
            raise LaunchRefusal("the run began at another commit")
        timings, cap = {k: reh["timings"][k] for k in LG.TIMING_KEYS}, LG.CAP_DOLLARS

        def outside(bill: dict[str, Any]) -> dict[str, Any]:
            return rehearsal_counts(RESULTS, bill)

        if earlier is None:
            bill = cloud.read_bill(outside({})["app_ids"])
            c0 = LG.check_c0(timings, listed_hourly_price, outside(bill), assemble_seconds=reh["check_C0"]["assemble_seconds"])
            record_c0(ledger_path, {**c0, "bill_read_at": bill.get("read_at")})
    return drive_stage(stage, container_specs(name, commit, rehearsal, trigger), cloud, ledger_path=ledger_path, runs_path=folder / f"runs_{name}.json",
                       design=design, timings=timings, listed_hourly_price=listed_hourly_price, cap=cap, outside=outside, commit=commit,
                       guards_spec=guards_plan(commit, rehearsal), accept_expected_refusals=accept_expected_refusals, trigger=trigger)


def check_command_commit(commit: str, rehearsal: int) -> None:
    if rehearsal:
        check_rehearsal_commit(commit, began_at(results_folder(rehearsal) / "ledger.json"))
    else:
        check_deciding_commit(commit, rehearsal_of_record()[1]["commit"])


def assemble_command(commit: str, rehearsal: int, *, assemble: Callable[[dict[str, Any]], dict[str, Any]], read_file: Callable[[str], bytes], app_id: str,
                     log: Callable[..., None]) -> dict[str, Any]:
    """The `assemble` command: each arm's table from the units the stages recorded, copied as bytes, with its receipt."""
    check_command_commit(commit, rehearsal)
    folder = results_folder(rehearsal)
    return assemble_arms(assemble_plan(commit, rehearsal, folder), assemble=assemble, read_file=read_file, out_path=folder / "assemble.json", commit=commit,
                         app_id=app_id, log=log)


def backup_command(commit: str, rehearsal: int, *, read_file: Callable[[str], bytes], log: Callable[..., None]) -> dict[str, str]:
    """The `backup` command: every search unit's file off the volume, as bytes, with a do-not-open notice."""
    check_command_commit(commit, rehearsal)
    folder = results_folder(rehearsal)
    return backup_units(backup_plan(commit, rehearsal, folder), read_file=read_file, dest=BACKUP / run_key(rehearsal), out_path=folder / "backup.json",
                        commit=commit, log=log)


# ----------------------------------------------------------------------------- the rehearsal's tables, validated


def validate_rehearsal_tables(folder: Path) -> dict[str, Any]:
    """Load each of a rehearsal's copied tables with plan 1 of the research log's loader and run plan 1 of the research log's checks on it, giving every check's
    name with pass or fail and no value (plan 4 of the research log, Section 6, row 7). It reads a rehearsal's tables and refuses any
    other: the folder must be a repeat rehearsal's, and each table's own metadata must say it is a rehearsal's."""
    folder = Path(folder)
    if folder.parent.resolve() != RESULTS.resolve() or not folder.name.startswith("rehearsal_"):
        raise LaunchRefusal("not a rehearsal's folder")
    out: dict[str, Any] = {}
    for sealed in sorted(folder.glob("*/sealed")):
        meta = LT.read_meta(sealed / LT.CORE_FILE)
        if meta.get("rehearsal") is not True or not str(meta.get("arm", "")).startswith("rehearsal"):
            raise LaunchRefusal("not a rehearsal's table")
        try:
            table = LT.load_table(sealed)
            failed = LT.failed_checks(table)
            loaded = True
        except LT.TableCheckError as exc:  # the loader's own refusal: a part out of order, or not the one recorded
            failed, loaded = [exc.check], False
        names = LT.CHECKS + tuple(c for c in LT.LOADER_CHECKS)
        out[sealed.parent.name] = {"loaded": loaded, "parts": len(meta.get("per_text_files", [])), "checks": {name: name not in failed for name in names},
                                   "failed": [name for name in names if name in failed]}
    return out


# ----------------------------------------------------------------------------- the rehearsal's record


def _all(xs: Any) -> bool:
    xs = list(xs)
    return bool(xs) and all(x is True for x in xs)


def rehearsal_outcomes(folder: Path) -> dict[str, Any]:
    """Each row of plan 4 of the research log's Section 6 as met or not, from the files the rehearsal's commands left in its folder: the
    ledger, each stage's record, the assembly's, the backup's, and the validation's. True or false, and nothing else."""
    ledger = json.load(open(folder / "ledger.json"))
    names = [s.name for s in LG.REHEARSAL_DESIGN]
    runs = {n: json.load(open(folder / f"runs_{n}.json")) for n in names}
    every_launch = every_launchs_containers(folder)
    assembled = json.load(open(folder / "assemble.json"))["arms"]
    backup = json.load(open(folder / "backup.json"))
    validated = json.load(open(folder / "validate.json"))["tables"]
    stages = ledger["stages"]

    def launch_calls(stage: str, k: int) -> dict[str, Any]:
        return stages[stage]["launches"][k]["calls"]

    def at_once(stage: str, k: int) -> bool:
        at = list(stages[stage]["launches"][k]["spawned"].values())
        return len(at) == 2 and abs(at[0] - at[1]) < 30.0

    lead_keys = [f"{b}_rehearsal" for b in REHEARSAL_BATCHES]
    delta_keys = [f"{b}_rehearsal_delta_on" for b in REHEARSAL_BATCHES]
    out: dict[str, Any] = {}

    # row 1: two containers at once in each role, both finishing, and the ledger holding the stage with both
    out["row_1_two_containers_at_once_in_each_role"] = (
        all(stages[n]["complete"] is True for n in names) and at_once("rehearsal_attack", 0) and sorted(launch_calls("rehearsal_attack", 0)) == ["C1", "C2"]
        and at_once("rehearsal_delta_heldout", -1) and sorted(launch_calls("rehearsal_delta_heldout", -1)) == ["C1", "C2"]
        and all(c["finished_units"] == c["expected_units"] for n in names for c in runs[n]["containers"]))

    # rows 2 and 3 are the delta-on held-out stage's two launches: the stop, then the relaunch with the kill
    held = stages["rehearsal_delta_heldout"]["launches"]
    two = len(held) == 2 and held[0]["trigger"] == "stop" and held[1]["trigger"] == "kill"
    first = held[0]["calls"] if two else {}
    by_batch = {c["container"].split("|")[2]: c for c in runs["rehearsal_delta_heldout"]["containers"]}

    def unit_of(batch: str, kind: str) -> dict[str, Any]:
        return next(u for u in by_batch[batch]["units"] if u["unit"].startswith(kind + "|"))

    # Every container sets the flag after its first unit and stops before its second. One that was still loading when
    # the other set the flag stops before its first, with none finished; the one that set it first always has one.
    out["row_3_stop_then_relaunch"] = bool(
        two and stages["rehearsal_delta_heldout"]["complete"] is True and sorted(first) == ["C1", "C2"] and sorted(by_batch) == ["C1", "C2"]
        and _all(c["outcome"] == "returned" and c["stopped"] is True and c["finished_units"] in (0, 1) and c["expected_units"] == 2 for c in first.values())
        and any(c["finished_units"] == 1 for c in first.values()) and held[0]["function_seconds"] > 0
        and _all(unit_of(b, "search")["skipped"] is True and unit_of(b, "search")["guards"] == {"G3": True} for b in first if first[b]["finished_units"] == 1 or b == "C1")
        and _all(unit_of(b, "block")["skipped"] is False for b in first)
        and abs(stage_seconds_on(ledger, "rehearsal_delta_heldout") - (held[0]["function_seconds"] + held[1]["function_seconds"])) < 1e-6)
    killed = held[1]["calls"].get("C1", {}) if two else {}
    out["row_2_kill_inside_a_unit"] = bool(
        two and killed.get("attempts") == 2 and killed.get("lives") == 2 and killed.get("counted_seconds") == killed.get("wait_seconds")
        and killed["wait_seconds"] > killed["returned_seconds"] and held[1]["container_lives"] == 3
        and by_batch["C1"].get("removed_unfinished") == 1 and by_batch["C2"].get("removed_unfinished") == 0
        and _all(assembled[k]["outcomes"].get("units_are_the_ones_their_containers_returned") is True for k in lead_keys + delta_keys))

    # row 4: the two waves, check C2, and the guards-only pass, which must refuse as the first rehearsal's assembler did
    g = (ledger.get("guards_pass") or {}).get("outcomes", {})
    wave_2 = stages["rehearsal_heldout_2"]["launches"]
    out["row_4_two_waves_and_the_guards_only_pass"] = bool(
        guards_acceptable(g, True) and not guards_acceptable(g, False) and [c["check"] for c in ledger["checks"]] == ["C1", "C2", "C3"]
        and not any(c["exceeds_cap"] for c in ledger["checks"])
        and _all(x["accepted_expected_refusals"] is True for x in wave_2)
        and any(s["after_stage"] == "rehearsal_heldout_1" and any(b.startswith("the guards-only pass") for b in s["by"]) for s in ledger["stops"]))

    # row 5: the assemble and backup commands
    searches = {f"{REHEARSAL_UNITS[key]}/search_{b}_s{REHEARSAL_START}.npz" for key in REHEARSAL_UNITS for b in REHEARSAL_BATCHES}
    out["row_5_assemble_and_backup"] = bool(sorted(assembled) == sorted(lead_keys + delta_keys) and set(backup["files"]) == searches and backup["notice"] == "DO_NOT_OPEN.md")

    # row 6: the per-text file in two parts, through the assembler, the byte copy, and plan 1 of the research log's loader
    def copied(key: str) -> bool:
        return all(LT.sha256_file(folder / key / "sealed" / f["name"]) == f["sha256"] for f in assembled[key]["receipt"]["files"])

    out["row_6_two_per_text_parts"] = bool(all(len(assembled[k]["receipt"]["files"]) == 3 and copied(k) and validated[k]["loaded"] is True and validated[k]["parts"] == 2
                                                for k in lead_keys + delta_keys))

    # row 7: the validate-only command: the new check fails beside the two that failed before, and nothing else does
    expected = ["axis_labels", "heldout_ids_differ_from_attack_ids", "carried_differs_from_own_batch_values"]
    out["row_7_validate_only"] = bool(all(validated[k]["failed"] == expected for k in lead_keys) and all(set(expected) <= set(validated[k]["failed"]) for k in delta_keys))

    # row 8: the end of preparation in every container, and a search's parts in every container that searched
    ran_a_search = [c for c in every_launch if any(u["unit"].startswith("search|") and not u["skipped"] for u in c["units"])]
    delta_searches = [c for c in ran_a_search if c["container"].split("|")[0] == "rehearsal_delta_on"]
    out["row_8_timings"] = bool(every_launch and all("to_ready" in c["timings"] for c in every_launch) and len(delta_searches) >= 2
                                and all(c["timings"].get(k + "_count") for c in ran_a_search for k in ("search_iteration_0", "search_iterations_warm", "search_iterations_after_warm")))

    # row 9, and plan 2 of the research log's Section 7: bit-identity with the pilot and between the two roles; the guards of every unit
    out["row_9_search_equal_to_the_pilots"] = bool(all(_all(assembled[k]["outcomes"]["attack_role_equals_pilot"].values()) for k in lead_keys))
    out["heldout_role_equal_to_the_pilots_and_to_the_attack_role"] = bool(
        all(_all(assembled[k]["outcomes"]["heldout_role_equals_pilot"].values()) and _all(assembled[k]["outcomes"]["containers_agree"].values()) for k in lead_keys)
        and all(_all(assembled[k]["outcomes"]["containers_agree"].values()) for k in delta_keys))
    ran = [u for c in every_launch for u in c["units"] if not u["skipped"]]
    searched = [u for u in ran if u["unit"].startswith("search|")]
    out["every_units_guards_true"] = bool(_all(all(u["guards"].values()) for u in ran)
                                          and _all(all(u["guards"].get(x) is True for x in ("G4", "G5", "G7", "wrapper_equals_authors")) for u in searched)
                                          and _all(all(u["guards"].get(x) is True for x in ("G5", "G8", "G10")) for u in ran if u["unit"].startswith("block|")))
    # four delta-on searches run; one's return is lost if its container is the one killed, which then returns it as skipped
    delta_units = [u for u in searched if u["unit"].split("|")[1] == "rehearsal_delta_on"]
    out["delta_entries_held_in_the_delta_on_searches"] = bool(len(delta_units) >= 3 and _all(u["guards"].get("delta_entries_held") is True for u in delta_units))
    out["assemblers_required_guards_true"] = bool(all(_all(assembled[k]["outcomes"].get(x) is True for x in LR.REQUIRED_GUARDS) for k in lead_keys + delta_keys))
    return out


def every_launchs_containers(folder: Path) -> list[dict[str, Any]]:
    """Every container's return from every launch of every stage of a rehearsal, from the per-launch records."""
    out = []
    for s in LG.REHEARSAL_DESIGN:
        for path in sorted(folder.glob(f"runs_{s.name}_launch_*.json")):
            out += json.load(open(path))["containers"]
    return out


def rehearsal_record(folder: Path, *, listed: dict[str, Any], listed_hourly_price: float, bill: dict[str, Any], commit: str, attempt: int) -> dict[str, Any]:
    """The rehearsal's open record: each required outcome as met or not, the timings with what they are means of,
    whether the delta-on search's steady step is slower than the lead's, and check C0 for the run against the cap, on
    top of what every rehearsal has cost. It holds true or false, hashes, and seconds, and no sealed value."""
    outcomes = rehearsal_outcomes(folder)
    returns = every_launchs_containers(folder)
    timings = LG.timings_from_rehearsal([{"arm": c["container"].split("|")[0], "timings": c["timings"]} for c in returns])
    ledger = json.load(open(folder / "ledger.json"))
    assembled = json.load(open(folder / "assemble.json"))
    spent = rehearsal_counts(folder.parent, bill)
    lead_assemblers = [v["seconds"] for k, v in assembled["arms"].items() if k.endswith("_rehearsal")]
    c0 = LG.check_c0({k: timings[k] for k in LG.TIMING_KEYS}, listed_hourly_price, spent, assemble_seconds=2 * max(lead_assemblers))
    ratio = timings["seconds_per_search_step_delta_on"] / timings["seconds_per_search_step"]
    return {
        "what": "The repeat rehearsal of the lead run on calibration batches C1 and C2 with pilot start 1 (plan 4 of the research log, Section 6). Each batch was scored "
                "on itself only. Its sealed values stay sealed; this file holds outcomes as true or false, hashes, and timings.",
        "commit": commit, "attempt": attempt, "written": utc_now(), "volume_root": volume_root("rehearsal", commit, attempt),
        "required_outcomes": outcomes, "all_required_outcomes_met": all(v is True for v in outcomes.values()),
        "guards_only_pass": ledger["guards_pass"], "stops": ledger["stops"],
        "spend_checks_of_the_rehearsal_itself": [{k: c[k] for k in ("check", "after_stage", "spent_dollars", "remaining_dollars", "projected_dollars", "cap", "exceeds_cap")}
                                                 for c in ledger["checks"]],
        "timings": timings,
        "delta_on_step": {"steady_seconds_per_step_lead": timings["seconds_per_search_step"], "steady_seconds_per_step_delta_on": timings["seconds_per_search_step_delta_on"],
                          "delta_on_over_lead": ratio, "slower_step": bool(ratio > 1.05),
                          "rule": "a slower step if the delta-on searches' steady rate, over their iterations after the first ten, exceeds the lead's by more than 5 percent; "
                                  "otherwise the first rehearsal's 0.493 s per step over 20 steps was warm-up"},
        "listed_prices": listed, "bill": bill, "money_spent_on_rehearsals": spent, "this_rehearsal": ledger_counts(ledger, bill), "check_C0": c0,
    }


def validate_command(rehearsal: int, *, log: Callable[..., None]) -> dict[str, Any]:
    """The `validate` command: every check's name with pass or fail, for each of a rehearsal's copied tables."""
    folder = rehearsal_folder(rehearsal)
    tables = validate_rehearsal_tables(folder)
    write_json(folder / "validate.json", {"at": utc_now(), "tables": tables})
    for key, t in tables.items():
        for name, ok in t["checks"].items():
            log(event="table_check", unit=key, guard=name, ok=bool(ok))
    return tables


def record_command(rehearsal: int, *, listed: dict[str, Any], listed_hourly_price: float, read_bill: Callable[[list[str]], dict[str, Any]],
                   killed: Callable[[str], Any], log: Callable[..., None]) -> dict[str, Any]:
    """The `record` command: the rehearsal's record, with the bills as they stand and the tasks that were killed."""
    folder = rehearsal_folder(rehearsal)
    commit = began_at(folder / "ledger.json")
    if commit is None:
        raise LaunchRefusal("the rehearsal has not run")
    bill = read_bill(rehearsal_counts(folder.parent)["app_ids"])
    out = rehearsal_record(folder, listed=listed, listed_hourly_price=listed_hourly_price, bill=bill, commit=commit, attempt=rehearsal)
    keys = [s["kill_key"] for name in REHEARSAL_STAGE_BATCHES for s in container_specs(name, commit, rehearsal, "kill") if "kill_key" in s]
    out["killed_tasks"] = {k: v for k, v in ((k, killed(k)) for k in keys) if v is not None}
    write_json(folder / "rehearsal.json", out)
    log(event="rehearsal_recorded", container=run_key(rehearsal), ok=bool(out["all_required_outcomes_met"] and not out["check_C0"]["exceeds_cap"]))
    return out
