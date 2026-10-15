"""Session 6, plan 3, Section 9: the dose-response on the rounded off set, on the GPU, and its local side, with no cloud
call in it. Added at the PI's request, as description.

Cell set S4 (H1, H5, H9, H13), one container each, as Section 8 ran (`s6_dose_run`): the batch's labels and targets
checked to be the run's, the variants' check unit, then one unit per attack search of the run, each scoring 20 flat
passes: at each of the five steps and each fraction f in 0.25, 0.5, 0.75, 0.9, the setting from
`s6_build.dose_rounded_setting`, its draw seeded by `seed_of("s6-dose-rounded", attack batch, start, step, f)`.

The fraction-one point is the rounded setting of plan 2's control (d), already scored; it is not scored again. Before
the launch, `rounded_hash_check` builds every setting at f = 1 from the run's saved settings and checks its hash against
the hash plan 2 recorded for its `d|rounded` pass, on all four batches; one mismatch and nothing launches.

The local side: `launch_command` (the commit and tree checks, the hash check, the projection recorded as check C0,
refused over $6, then `lead_launch.drive_stage`), and `collect_command` (every unit file off the volume as bytes, each
checked against the hash its container returned, to `.cache/s6_dose_rounded/`, with the receipt `backup.json`).
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
from vpd_audit_2 import s6_dose_run as D
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_run as SR

REPO_ROOT = LL.REPO_ROOT
RESULTS = REPO_ROOT / "results" / "s6_dose_rounded"
VOLUME = "/cache/s6_dose_rounded"
LOCAL = REPO_ROOT / ".cache" / "s6_dose_rounded"  # `.cache/` is ignored by git
RUN = "s6_dose_rounded"
PART = "dose_rounded"
ARM = "s6_dose_rounded"
UNITS = "units"
BATCHES = B.S4
STAGE = LG.Stage("s6_dose_rounded", ARM, "heldout", len(BATCHES), 0, 0, 0, 0, 0, False)
DESIGN = (STAGE,)
CAP_DOLLARS = 6.0  # plan 3, Section 9: launch at or under $6; over it, stop and report
READING_FILES = ("vpd_audit_2/s6_dose_rounded_run.py", "vpd_audit_2/modal_s6_dose_rounded.py", "vpd_audit_2/s6_dose_rounded.py", "vpd_audit_2/s6_build.py",
                 "vpd_audit_2/s6_run.py")
RUN_UNITS_LOCAL = REPO_ROOT / ".cache" / "s5_lead_units" / "run" / "lead"


def specs(commit: str, refs: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"part": PART, "arm": ARM, "side": "heldout", "batch": h, "batches": [h], "commit": commit, "mode": SR.MODE, "root": VOLUME, "units": UNITS,
             "run": RUN, "attack_batches": list(SR.ATTACK), "starts": list(SR.STARTS), "refs": {h: refs[h]}} for h in BATCHES]


SPEC_KEYS = D.SPEC_KEYS


def check_spec(spec: dict[str, Any]) -> None:
    ok = (set(spec) - {"launch"} == SPEC_KEYS and spec["part"] == PART and spec["arm"] == ARM and spec["side"] == "heldout" and spec["batch"] in BATCHES
          and spec["batches"] == [spec["batch"]] and spec["mode"] == SR.MODE and spec["root"] == VOLUME and spec["units"] == UNITS and spec["run"] == RUN
          and len(str(spec["commit"])) == 40 and tuple(spec["attack_batches"]) == SR.ATTACK and tuple(spec["starts"]) == SR.STARTS
          and set(spec["refs"]) == {spec["batch"]})
    if not ok:
        raise LR.GuardFailure("configuration", f"container|{spec.get('part')}|{spec.get('batch')}")


def inputs_of(spec: dict[str, Any], load_ids: Callable[[str], tuple[np.ndarray, list[str], list[str]]] | None = None,
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


def job(model: Any, ctx: SR.Context, spec: dict[str, Any], batch_inputs: dict[str, tuple[np.ndarray, list[str]]], inputs: SR.Inputs) -> dict[str, Any]:
    """One S4 batch: its labels checked to be the run's, the check unit, then the 80 searches' passes."""
    SR.check_environment(ctx)
    batch = spec["batch"]
    refs = spec["refs"][batch]
    units = B.dose_rounded_units(batch, list(spec["attack_batches"]), list(spec["starts"]))
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


# ----------------------------------------------------------------------------- the fraction-one point: a hash check, not a re-score


def rounded_hash_check(read_run_unit: Callable[[str, int], dict[str, np.ndarray]] | None = None,
                       recorded: Callable[[str, str], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Every setting at f = 1, built from the run's saved setting, against the hash plan 2 recorded for its rounded
    pass on each S4 batch; and against `rounded` itself."""
    if read_run_unit is None:
        hashes = SR.run_unit_hashes()

        def read_run_unit(attack: str, start: int) -> dict[str, np.ndarray]:
            data = (RUN_UNITS_LOCAL / f"search_{attack}_s{start}.npz").read_bytes()
            if hashlib.sha256(data).hexdigest() != hashes[f"search_{attack}_s{start}.npz"]:
                raise LL.LaunchRefusal(f"search_{attack}_s{start}.npz is not the run's unit")
            return SR.run_unit_from_bytes(data, attack, start)
    if recorded is None:
        from vpd_audit_2 import s6_variants as V

        receipt = json.load(open(SR.RESULTS / "units_receipt.json"))["files"]
        names = [f"controls_{h}_{a}_s{s}" for h in BATCHES for a in SR.ATTACK for s in SR.STARTS]
        units = V.checked_units(SR.LOCAL_UNITS, receipt, names)
        recorded = units.recorded
    compared = equal = equal_to_rounded = 0
    mismatches: list[str] = []
    for a in SR.ATTACK:
        for s in SR.STARTS:
            unit = read_run_unit(a, s)
            for row in B.SPLIT_ROWS:
                flat = B.saved(unit, row)[0]
                built, _, _ = B.dose_rounded_setting(flat, 1.0, B.dose_rounded_seed(a, s, row, 1.0))
                equal_to_rounded += int(np.array_equal(built, B.rounded(flat)))
                sha = B.sha(built)
                for h in BATCHES:
                    compared += 1
                    if recorded(f"controls_{h}_{a}_s{s}", f"d|rounded|{row}")["setting_sha"] == sha:
                        equal += 1
                    else:
                        mismatches.append(f"{h} {a} s{s} {row}")
    return {"compared": compared, "equal": equal, "settings_equal_to_rounded": equal_to_rounded, "settings": len(SR.ATTACK) * len(SR.STARTS) * len(B.SPLIT_ROWS),
            "mismatches": mismatches, "all_equal": equal == compared and not mismatches}


# ----------------------------------------------------------------------------- before the launch: the commit and the cost


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


def projection(listed_hourly_price: float, *, dose_record: Path | None = None) -> dict[str, Any]:
    """The cost before the launch, from Section 8's four containers, which ran the same check unit and 80 units of 15
    flat passes on the same batches: their mean time to ready, their check unit's mean seconds, their dose units' mean
    seconds per pass for every pass, and a volume commit every ten units. Every container life adds 50 seconds of boot."""
    record = json.load(open(D.RESULTS / "runs_s6_dose.json" if dose_record is None else dose_record))
    t = [c["timings"] for c in record["containers"]]
    if len(t) != len(BATCHES):
        raise LL.LaunchRefusal("Section 8's record does not hold its four containers")
    ready = float(np.mean([x["to_ready"] for x in t]))
    per_pass = R3._mean_rate(t, "unit_dose")
    check = float(np.mean([x["unit_variants_check"] for x in t]))
    commit_s = R3._mean_rate(t, "volume_commit")
    n_units = 1 + len(SR.ATTACK) * len(SR.STARTS)
    passes = len(SR.ATTACK) * len(SR.STARTS) * B.n_passes("dose_rounded")
    seconds = len(BATCHES) * (ready + check + passes * per_pass + commit_s * (n_units // SR.COMMIT_EVERY + 1))
    money = LG.money(seconds, len(BATCHES), listed_hourly_price)
    return {"check": "C0", "listed_hourly_price": float(listed_hourly_price), "containers": len(BATCHES), "passes": len(BATCHES) * (passes + 3),
            "seconds_to_ready": ready, "seconds_per_pass": per_pass, "seconds_per_check_unit": check, "seconds_per_volume_commit": commit_s, **money,
            "projected_dollars": money["dollars"], "cap": CAP_DOLLARS, "exceeds_cap": bool(money["dollars"] > CAP_DOLLARS)}


def launch_command(commit: str, cloud: LL.Cloud, *, listed_hourly_price: float, refs: dict[str, Any] | None = None,
                   hash_check: Callable[[], dict[str, Any]] | None = None) -> dict[str, Any]:
    """The checks, the fraction-one hash check (written to `rounded_check.json`; any mismatch and nothing launches), the
    projection recorded as check C0 (over $6, nothing launches), then the four containers at once."""
    check_launch_commit(commit)
    ledger_path = RESULTS / "ledger.json"
    earlier = LL.began_at(ledger_path)
    if earlier is not None and earlier != commit:
        raise LL.LaunchRefusal("the dose-response on the rounded off set began at another commit")
    if earlier is None:
        hc = (rounded_hash_check if hash_check is None else hash_check)()
        LL.write_json(RESULTS / "rounded_check.json", {**hc, "at": LL.utc_now(), "commit": commit})
        if not hc["all_equal"]:
            raise LL.LaunchRefusal("the builder at f = 1 does not reproduce the rounded setting's hash: report to the head")
        LL.record_c0(ledger_path, projection(listed_hourly_price))
    if refs is None:
        refs = SR.references(SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT), SR.load_table_checked(SR.DELTA_TABLE, SR.DELTA_RECEIPT))
    return LL.drive_stage(STAGE, specs(commit, refs), cloud, ledger_path=ledger_path, runs_path=RESULTS / f"runs_{STAGE.name}.json", design=DESIGN,
                          timings={}, listed_hourly_price=listed_hourly_price, cap=CAP_DOLLARS, outside=LL.no_spend_outside, commit=commit)


def expected_files() -> dict[str, str]:
    return {name: f"{UNITS}/{name}.npz" for h in BATCHES for name, _, _ in B.dose_rounded_units(h, list(SR.ATTACK), list(SR.STARTS))}


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
