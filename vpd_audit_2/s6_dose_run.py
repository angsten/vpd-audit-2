"""Plan 3 of the research log, Section 8: the dose-response on an intact model, on the GPU, and its local side, with no cloud call
in it. Added after the readings, as description.

Cell set S4 (H1, H5, H9, H13), one container each, as the variants ran (`s6_plan3_run`): the batch's labels and targets
checked to be the run's, the variants' check unit (the full setting on the split path within the run's per-text
tolerance, its bit equality recorded, and on the flat path bit for bit; the start on the split path), then one unit per
attack search of the run, each scoring 15 flat passes: at each of the five lengths and each fraction f in 0.25, 0.5,
0.75, the setting from `s6_build.dose_setting` with its draw seeded by `seed_of("s6-dose", attack batch, start, length,
f)` (`s6_build.dose_seed`).

The local side: `launch_command` (the commit and tree checks, the projection recorded as check C0, refused over $8,
then `lead_launch.drive_stage`), and `collect_command` (every unit file off the volume as bytes, each checked against
the hash its container returned, to `.cache/s6_dose/`, with the receipt `backup.json`).
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_ledger as LG
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_run as SR

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s6_dose"
VOLUME = "/cache/s6_dose"
LOCAL = REPO_ROOT / ".cache" / "s6_dose"  # `.cache/` is ignored by git
RUN = "s6_dose"
PART = "dose"
ARM = "s6_dose"
UNITS = "units"
BATCHES = B.S4
STAGE = LG.Stage("s6_dose", ARM, "heldout", len(BATCHES), 0, 0, 0, 0, 0, False)
DESIGN = (STAGE,)
CAP_DOLLARS = 8.0  # plan 3 of the research log, Section 8: launch at or under $8; over it, stop and report
READING_FILES = ("vpd_audit_2/s6_dose_run.py", "vpd_audit_2/modal_s6_dose.py", "vpd_audit_2/s6_dose.py", "vpd_audit_2/s6_build.py", "vpd_audit_2/s6_run.py")


def specs(commit: str, refs: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"part": PART, "arm": ARM, "side": "heldout", "batch": h, "batches": [h], "commit": commit, "mode": SR.MODE, "root": VOLUME, "units": UNITS,
             "run": RUN, "attack_batches": list(SR.ATTACK), "starts": list(SR.STARTS), "refs": {h: refs[h]}} for h in BATCHES]


SPEC_KEYS = {"part", "arm", "side", "batch", "batches", "commit", "mode", "root", "units", "run", "attack_batches", "starts", "refs"}


def check_spec(spec: dict[str, Any]) -> None:
    ok = (set(spec) - {"launch"} == SPEC_KEYS and spec["part"] == PART and spec["arm"] == ARM and spec["side"] == "heldout" and spec["batch"] in BATCHES
          and spec["batches"] == [spec["batch"]] and spec["mode"] == SR.MODE and spec["root"] == VOLUME and spec["units"] == UNITS and spec["run"] == RUN
          and len(str(spec["commit"])) == 40 and tuple(spec["attack_batches"]) == SR.ATTACK and tuple(spec["starts"]) == SR.STARTS
          and set(spec["refs"]) == {spec["batch"]})
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('part')}|{spec.get('batch')}")


def dose_inputs(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
                pools: dict[str, Any] | None = None) -> dict[str, tuple[np.ndarray, list[str]]]:
    """A container's one S4 batch, a held-out pool; no other batch's ids."""
    if load_ids is None:
        from vpd_audit_2.manifest import pool_ids as load_ids
    pools = LL._manifest()["pools"] if pools is None else pools
    h = spec["batch"]
    if spec.get("part") != PART or h not in BATCHES or pools[h]["pool"] != "H":
        raise LL.LaunchRefusal(f"batch {h} is not one of S4's held-out batches")
    ids, _texts, rows = load_ids(h)
    return {h: (ids, list(rows))}


def dose_job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]], inputs: SR.Inputs) -> dict[str, Any]:
    """One S4 batch: its labels checked to be the run's, the check unit, then the 80 searches' dose passes."""
    SR.check_environment(ctx)
    batch = spec["batch"]
    refs = spec["refs"][batch]
    units = B.dose_units(batch, list(spec["attack_batches"]), list(spec["starts"]))
    removed = SR.clean_unfinished(ctx, [u[0] for u in units])
    ids, rows = batch_inputs[batch]
    prep, fp, zero = SR.prepare_batch(model, ctx, batch, ids, rows, refs["prep_fp"])
    ctx.tick("to_ready", time.time() - ctx.t0)
    ctx.log(event="container_started", container=f"{ARM}|{batch}", count=removed)
    done, stopped = SR.run_units(model, ctx, batch, units, prep, fp, zero, inputs, refs)
    ctx.commit_volume()
    out = {"container": f"{ARM}|heldout|{batch}", "units": done, "finished_units": len(done), "expected_units": len(units), "stopped": bool(stopped),
           "seconds": float(time.time() - ctx.t0), "environment": dict(ctx.environment), "timings": {k: float(v) for k, v in ctx.timings.items()},
           "removed_unfinished": int(removed)}
    ctx.log(event="container_finished", container=out["container"], count=len(done), seconds=out["seconds"])
    return out


def tree_holds_only_this_plans_records() -> bool:
    top = Path(LL._git("rev-parse", "--show-toplevel").stdout.strip()).resolve()
    allowed = (RESULTS.resolve().relative_to(top)).as_posix() + "/"
    r = LL._git("status", "--porcelain", "--untracked-files=all", "--", ".")
    return r.returncode == 0 and all(line.startswith("?? ") and line[3:].strip('"').startswith(allowed) for line in r.stdout.splitlines())


def check_launch_commit(commit: str) -> None:
    if not tree_holds_only_this_plans_records():
        raise LL.LaunchRefusal("the tree is not clean under vpd-audit-2")
    if LL.head_commit() != commit or len(commit) != 40:
        raise LL.LaunchRefusal("the current commit is not the one named")
    missing = [rel for rel in READING_FILES if LL.blob(commit, rel) is None]
    if missing:
        raise LL.LaunchRefusal("not committed: " + ", ".join(missing))
    changed = LL.run_files_changed(SR.RUN_COMMIT, commit)
    if changed:
        raise LL.LaunchRefusal("the search path has changed since the lead run: " + ", ".join(changed))


def projection(listed_hourly_price: float, *, plan3_record: Path | None = None) -> dict[str, Any]:
    """The cost before the launch, from plan 3 of the research log's four variants containers, which ran the same check unit and 80 units of
    15 passes on the same batches: their mean time to ready; their check unit's mean seconds; every pass at their
    variant units' mean seconds per pass (two thirds of those passes were split passes, about 7 percent slower than a
    flat pass, so this leans high); and a volume commit every ten units. Every container life adds 50 seconds of boot."""
    record = json.load(open(R3.RESULTS / "runs_s6_plan3.json" if plan3_record is None else plan3_record))
    t = [c["timings"] for c in record["containers"] if c["container"].startswith(f"{R3.VARIANT_ARM}|")]
    if len(t) != len(BATCHES):
        raise LL.LaunchRefusal("plan 3 of the research log's record does not hold its four variants containers")
    ready = float(np.mean([x["to_ready"] for x in t]))
    per_pass = R3._mean_rate(t, "unit_variants")
    check = float(np.mean([x["unit_variants_check"] for x in t]))
    commit_s = R3._mean_rate(t, "volume_commit")
    n_units = 1 + len(SR.ATTACK) * len(SR.STARTS)
    passes = len(SR.ATTACK) * len(SR.STARTS) * B.n_passes("dose")
    seconds = len(BATCHES) * (ready + check + passes * per_pass + commit_s * (n_units // SR.COMMIT_EVERY + 1))
    money = LG.money(seconds, len(BATCHES), listed_hourly_price)
    return {"check": "C0", "listed_hourly_price": float(listed_hourly_price), "containers": len(BATCHES), "passes": len(BATCHES) * (passes + 3),
            "seconds_to_ready": ready, "seconds_per_pass": per_pass, "seconds_per_check_unit": check, "seconds_per_volume_commit": commit_s, **money,
            "projected_dollars": money["dollars"], "cap": CAP_DOLLARS, "exceeds_cap": bool(money["dollars"] > CAP_DOLLARS)}


def launch_command(commit: str, cloud: LL.Cloud, *, listed_hourly_price: float, refs: dict[str, Any] | None = None) -> dict[str, Any]:
    """The checks, the projection recorded as check C0 (over $8, nothing launches), then the four containers at once."""
    check_launch_commit(commit)
    ledger_path = RESULTS / "ledger.json"
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("the dose-response began at another commit")
    if earlier is None:
        LL.record_c0(ledger_path, projection(listed_hourly_price))
    if refs is None:
        refs = SR.references(SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT), SR.load_table_checked(SR.DELTA_TABLE, SR.DELTA_RECEIPT))
    return LL.drive_stage(STAGE, specs(commit, refs), cloud, ledger_path=ledger_path, runs_path=RESULTS / f"runs_{STAGE.name}.json", design=DESIGN,
                          timings={}, listed_hourly_price=listed_hourly_price, cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


def expected_files() -> dict[str, str]:
    return {name: f"{UNITS}/{name}.npz" for h in BATCHES for name, _, _ in B.dose_units(h, list(SR.ATTACK), list(SR.STARTS))}


def collect_command(commit: str, *, read_file: Callable[[str], bytes], log: Callable[..., None], dest: Path | None = None) -> dict[str, str]:
    if not tree_holds_only_this_plans_records() or LL.head_commit() != commit:
        raise LL.LaunchRefusal("the tree or the commit is not the launch's")
    run = json.load(open(RESULTS / f"runs_{STAGE.name}.json"))
    if run["commit"] != commit or not run["summary"]["complete"]:
        raise LL.LaunchRefusal("the stage is not complete at this commit")
    returned = {u["unit"]: u["sha256"] for c in run["containers"] for u in c["units"]}
    expected = expected_files()
    if set(returned) != set(expected):
        raise LL.LaunchRefusal(f"the stage's record holds {len(returned)} units; the plan has {len(expected)}")
    dest = LOCAL if dest is None else dest
    files: dict[str, str] = {}
    for unit in sorted(expected):
        rel = expected[unit]
        data = read_file(f"{VOLUME}/{rel}")
        if hashlib.sha256(data).hexdigest() != returned[unit]:
            raise LL.LaunchRefusal(f"the bytes of {rel} do not have the hash its container returned")
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_bytes(data)
        files[rel] = returned[unit]
    LL.write_json(RESULTS / "backup.json", {"commit": commit, "at": LL.utc_now(),
                                            "folder": str(dest.relative_to(REPO_ROOT)) if dest.is_relative_to(REPO_ROOT) else str(dest), "files": files})
    log(event="backup_finished", container="units", count=len(files))
    return files
