"""Plan 2 of the research log: the on-or-off histogram (`results/s6_followups/CONVENTIONS.md`, Section 3). Description; no GPU.

    uv run python -m vpd_audit_2.s6_histogram

Settings: all 160 searches of the lead experiment (80 attack and 80 held-out, starts 9 to 13), their saved settings at
20, 40, 80, 160, and 320 steps and the one-step-earlier copies at 160 and 320, read from the run's unit files under
`.cache/s5_lead_units/run/lead/`, each checked against the hash the earlier backup recorded. Attack and held-out sides
are reported apart.

Bins: exactly 0; exactly 1; and the open interval (0, 1) in ten equal bins, bin k holding the values v with
floor(10 v) = k, computed in float64 on the stored float32 value (so a stored 0.9, which is 0.89999998, is in bin 8).
Three groups of entries: never-needed components (the strata's dead stratum, mean label at most 1e-6 on the first
post's 1,024 texts), ever-needed components (the alive strata), and the 24 delta entries.

Untouched: an entry whose saved absolute gradient sum at that step is exactly zero. It then equals its start; this is
checked, and a failure stops the script. Turned: an interior entry (strictly between 0 and 1) that is not untouched.
Both counts are printed.

The output is counts, with each bin's share of its group's entries at two decimals; every count goes to
`results/s6_followups/record.json` under "histogram".
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import pilot as P

UNITS = env.REPO_ROOT / ".cache" / "s5_lead_units" / "run" / "lead"
BACKUP = env.REPO_ROOT / "results" / "s5_lead" / "backup.json"
SIDES = {"attack": tuple(f"A{i}" for i in range(1, 17)), "heldout": tuple(f"H{j}" for j in range(1, 17))}
STARTS = LR.STARTS
ROWS = (("n20", "step_20"), ("n40", "step_40"), ("n80", "step_80"), ("n160", "step_160"), ("n320", "step_320"),
        ("n159", "step_159"), ("n319", "step_319"))
GROUPS = ("never_needed", "ever_needed", "delta")
N_BINS = 10
BIN_NAMES = ("exactly 0",) + tuple(f"({k / 10:.1f}, {(k + 1) / 10:.1f})" for k in range(N_BINS)) + ("exactly 1",)


class Refusal(Exception):
    """The unit files are not the run's complete set, or not what they say they are."""


def unit_paths(units: Path | None = None, backup: Path | None = None) -> dict[tuple[str, str, int], Path]:
    """Every search unit of the lead arm, each present and with the hash the backup recorded; else a refusal that names
    every unit missing or changed."""
    units = UNITS if units is None else Path(units)
    recorded = json.load(open(BACKUP if backup is None else backup))["files"]
    paths, missing, changed = {}, [], []
    for side, batches in SIDES.items():
        for b in batches:
            for s in STARTS:
                p = LR.search_file(units, b, s)
                if not p.is_file():
                    missing.append(p.name)
                elif hashlib.sha256(p.read_bytes()).hexdigest() != recorded.get(f"lead/{p.name}"):
                    changed.append(p.name)
                else:
                    paths[(side, b, s)] = p
    if missing or changed:
        raise Refusal("missing: " + (", ".join(missing) or "none") + "; not the recorded hash: " + (", ".join(changed) or "none"))
    return paths


def groups_of(lay: list[tuple[str, int]], strata: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Flat positions of each group: the never-needed and ever-needed components of every module, and the delta entries."""
    out: dict[str, list[np.ndarray]] = {g: [] for g in GROUPS}
    off = 0
    for name, C in lay:
        st = np.asarray(strata[name])
        assert st.shape == (C,)
        idx = off + np.arange(C)
        out["never_needed"].append(idx[st == P.DEAD_STRATUM])
        out["ever_needed"].append(idx[st != P.DEAD_STRATUM])
        out["delta"].append(np.array([off + C]))
        off += C + 1
    return {g: np.concatenate(v).astype(np.int64) for g, v in out.items()}


def bin_counts(values: np.ndarray) -> np.ndarray:
    """Counts in the twelve bins: exactly 0, the ten open-interval bins by floor(10 v) in float64, exactly 1."""
    v = np.asarray(values, dtype=np.float64)
    if ((v < 0) | (v > 1) | ~np.isfinite(v)).any():
        raise Refusal("a setting value outside [0, 1]")
    interior = (v > 0) & (v < 1)
    k = np.clip(np.floor(10.0 * v[interior]).astype(np.int64), 0, N_BINS - 1)
    return np.concatenate([[int((v == 0).sum())], np.bincount(k, minlength=N_BINS), [int((v == 1).sum())]]).astype(np.int64)


def one_setting(setting: np.ndarray, start: np.ndarray, cum_abs: np.ndarray, groups: dict[str, np.ndarray], what: str) -> dict[str, dict[str, Any]]:
    """Per group: entries, bin counts, untouched, turned. Untouched entries must equal their start."""
    untouched = np.asarray(cum_abs) == 0
    if not np.array_equal(setting[untouched], start[untouched]):
        raise Refusal(f"{what}: an untouched entry differs from its start")
    interior = (setting > 0) & (setting < 1)
    out = {}
    for g, idx in groups.items():
        out[g] = {"entries": int(idx.size), "bins": bin_counts(setting[idx]), "untouched": int(untouched[idx].sum()),
                  "turned": int((interior[idx] & ~untouched[idx]).sum())}
    return out


def histogram(paths: dict[tuple[str, str, int], Path], starts: dict[int, np.ndarray], groups: dict[str, np.ndarray]) -> dict[str, Any]:
    """Counts summed over each side's searches, by row and group. Each unit must be the lead search of its batch and
    start, from the signed start of that index."""
    total = {side: {row: {g: {"entries": 0, "bins": np.zeros(N_BINS + 2, dtype=np.int64), "untouched": 0, "turned": 0} for g in GROUPS}
                    for row, _ in ROWS} for side in SIDES}
    searches = {side: 0 for side in SIDES}
    for (side, b, s), path in sorted(paths.items()):
        meta = LR.unit_meta(path)
        if (meta["batch"], meta["start"], meta["arm"], meta["delta_held"]) != (b, s, "lead", False) or meta["start_sha256"] != LR.setting_sha256(starts[s]):
            raise Refusal(f"{path.name} is not the lead search of {b} from start {s}")
        with np.load(path, allow_pickle=False) as z:
            names = [str(x) for x in z["hook_names"]]
            settings, cum_abs = z["settings"], z["cum_abs"]
        searches[side] += 1
        for row, name in ROWS:
            if name not in names:
                raise Refusal(f"{path.name} has no setting {name}")
            k = names.index(name)
            one = one_setting(settings[k], starts[s], cum_abs[k], groups, f"{path.name} {name}")
            for g in GROUPS:
                t = total[side][row][g]
                t["entries"] += one[g]["entries"]
                t["bins"] += one[g]["bins"]
                t["untouched"] += one[g]["untouched"]
                t["turned"] += one[g]["turned"]
    return {"searches": searches, "counts": total}


def load_inputs() -> tuple[dict[tuple[str, str, int], Path], dict[int, np.ndarray], dict[str, np.ndarray]]:
    from vpd_audit_2 import lead_launch as LL

    lay = P.layout()
    starts = {s: LR.flat_start(st, lay, False) for s, st in LL.starts_for(STARTS).items()}
    strata, _ = LL.strata_by_module()
    return unit_paths(), starts, groups_of(lay, strata)


def report(h: dict[str, Any]) -> str:
    L = ["The on-or-off histogram (plan 2 of the research log; conventions, Section 3). Description only.",
         "Settings: the lead experiment's 160 searches, starts 9 to 13, attack and held-out sides apart. Counts are summed over a",
         "side's searches; each bin's share of its group's entries is in parentheses, at two decimals. Bin (a, b) holds the values",
         "v with floor(10 v) = 10 a, on the stored float32 value. Untouched: saved absolute gradient sum exactly zero (each checked",
         "equal to its start). Turned: strictly between 0 and 1, and not untouched.", ""]
    for side in SIDES:
        L.append(f"{side.capitalize()} side, {h['searches'][side]} searches.")
        for row, _ in ROWS:
            L.append(f"  {row}:")
            for g in GROUPS:
                t = h["counts"][side][row][g]
                n = t["entries"]
                bins = "  ".join(f"{name} {c} ({c / n:.2f})" for name, c in zip(BIN_NAMES, t["bins"]))
                L.append(f"    {g.replace('_', '-')}, {n} entries: {bins}")
                L.append(f"      untouched {t['untouched']} ({t['untouched'] / n:.2f}); turned {t['turned']} ({t['turned'] / n:.2f})")
        L.append("")
    return "\n".join(L)


def record_of(h: dict[str, Any]) -> dict[str, Any]:
    return {"searches": h["searches"], "bin_names": list(BIN_NAMES),
            "counts": {side: {row: {g: {**{k: v for k, v in t.items() if k != "bins"}, "bins": [int(x) for x in t["bins"]]} for g, t in r.items()}
                              for row, r in rows.items()} for side, rows in h["counts"].items()}}


def main() -> int:
    from vpd_audit_2 import s6_record

    paths, starts, groups = load_inputs()
    h = histogram(paths, starts, groups)
    sys.stdout.write(report(h))
    s6_record.update("histogram", record_of(h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
