"""Plan 3 of the research log, Section 8: the dose-response on an intact model. Added after the readings, as description; nothing
here has a line. Committed before the launch.

    uv run python -m vpd_audit_2.s6_dose > results/s6_followups/dose.txt

Cell set S4: the run's 400 carried settings (80 attack searches at 20, 40, 80, 160, and 320 steps) on H1, H5, H9, and
H13, 320 cells per length. For each setting, length, and fraction f in 0.25, 0.5, 0.75: a uniformly random subset of
the setting's entries at exactly 0 (the delta entries included, as V1 treats them), of f times their number rounded half
up, stays 0, and every other entry is 1 (`s6_build.dose_setting`). One draw per (setting, length, f), shared by the four
batches, seeded by seed_of("s6-dose", attack batch, start, length, f), with f as the string "0.25", "0.5", or "0.75",
since `seed_of` takes ints and strings only.

Read as `s6_variants` reads V1. Per length and fraction: the pooled kept share, the sum over cells of (the harm - the
saved start's harm) over the sum of (the saved carried harm - the saved start's harm), and the mean harm in nats over the
cells. Beside them, as f = 1, V1's figures from plan 3 of the research log's variants units, and as f = 0, the all-ones harm (plan 2 of the research log's
`ones` pass, one value per batch, the same on each of its cells). At 320 steps, the kept share per batch at each f. The
check units' outcomes are printed first.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import numpy as np

from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_dose_run as D
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_run as SR
from vpd_audit_2 import s6_variants as V

NOTE = "Added after the readings, as description (plan 3 of the research log, Section 8); no line."
FRACTIONS = (0.0,) + B.DOSE_FRACTIONS + (1.0,)
PER_BATCH_ROW = "n320"


def checks(units: R.Units) -> dict[str, Any]:
    out = {}
    for h in D.BATCHES:
        u = units.get(f"dose_check_{h}")["passes"]
        out[h] = {pid: {"harm": v[0], "reference": v[2]["reference"], "bits_equal": bool(np.float64(v[0]).tobytes() == np.float64(v[2]["reference"]).tobytes())}
                  for pid, v in u.items()}
    return out


def _harm(f: float, h: str, a: str, s: int, row: str, units: R.Units, variants: R.Units, ones: dict[str, float]) -> float:
    if f == 0.0:
        return ones[h]
    if f == 1.0:
        return variants.harm(f"variants_{h}_{a}_s{s}", f"V1|{row}")
    return units.harm(f"dose_{h}_{a}_s{s}", f"D{B.dose_key(f)}|{row}")


def dose(units: R.Units, variants: R.Units, plan2: R.Units, lead: dict[str, Any]) -> dict[str, Any]:
    att = list(enumerate(str(x) for x in lead["attack_names"]))
    held = [(j, str(h)) for j, h in enumerate(str(x) for x in lead["heldout_names"]) if h in D.BATCHES]
    starts = list(enumerate(int(x) for x in lead["starts"]))
    if [h for _, h in held] != list(D.BATCHES):
        raise R.Refusal("the run's table does not hold S4's four held-out batches")
    ones = {h: plan2.harm(f"ones_{h}", "ones") for _, h in held}
    out: dict[str, Any] = {"fractions": list(FRACTIONS), "rows": {}, "per_batch_at_320": {}}
    for row in B.SPLIT_ROWS:
        q = R.row_index(lead, row)
        den = {h: 0.0 for _, h in held}
        num = {f: {h: 0.0 for _, h in held} for f in FRACTIONS}
        harms: dict[float, list[float]] = {f: [] for f in FRACTIONS}
        for i, a in att:
            for j, h in held:
                for k, s in starts:
                    base = float(lead["init_H"][j, k])
                    den[h] += float(lead["carried"][i, j, k, q]) - base
                    for f in FRACTIONS:
                        x = _harm(f, h, a, s, row, units, variants, ones)
                        num[f][h] += x - base
                        harms[f].append(x)
        total = sum(den.values())
        out["rows"][row] = {"cells": len(harms[FRACTIONS[0]]),
                            **{B.dose_key(f): {"kept_share": float(sum(num[f].values()) / total), "mean_harm": float(np.mean(harms[f]))} for f in FRACTIONS}}
        if row == PER_BATCH_ROW:
            out["per_batch_at_320"] = {h: {B.dose_key(f): float(num[f][h] / den[h]) for f in FRACTIONS} for _, h in held}
    return out


def report(res: dict[str, Any], chk: dict[str, Any]) -> str:
    keys = [B.dose_key(f) for f in FRACTIONS]
    L = ["A dose-response on an intact model, on cell set S4 (plan 3 of the research log, Section 8). " + NOTE,
         "S4: the 400 carried settings on H1, H5, H9, and H13, 320 cells per length. At fraction f, a random f of the setting's entries at exactly 0",
         "(delta entries included) stays 0 and every other entry is 1; f = 1 is V1 (plan 3 of the research log's variants units), f = 0 is all ones (plan 2 of the research log's ones pass).",
         "Kept share: the sum over cells of (harm - saved start harm) over the sum of (saved carried harm - saved start harm), as V1 is read.", "",
         "The checks, per batch (the full setting on the split's path and the flat path, and the start on the split's path):"]
    for h, x in chk.items():
        L.append(f"  {h}: " + "; ".join(f"{pid} {v['harm']:.6f} against {v['reference']:.6f}, bit for bit {'yes' if v['bits_equal'] else 'no'}"
                                       for pid, v in x.items()))
    L += ["", "Kept share, by length and fraction f:", "    length   cells" + "".join(f"{'f = ' + k:>12}" for k in keys)]
    for row, x in res["rows"].items():
        L.append(f"    {row:<7}  {x['cells']:>5}" + "".join(f"{x[k]['kept_share']:>12.3f}" for k in keys))
    L += ["", "Mean harm in nats, by length and fraction f:", "    length   cells" + "".join(f"{'f = ' + k:>12}" for k in keys)]
    for row, x in res["rows"].items():
        L.append(f"    {row:<7}  {x['cells']:>5}" + "".join(f"{x[k]['mean_harm']:>12.3f}" for k in keys))
    L += ["", "At 320 steps, the kept share per batch (80 cells each):", "    batch    " + "".join(f"{'f = ' + k:>12}" for k in keys)]
    for h, x in res["per_batch_at_320"].items():
        L.append(f"    {h:<8} " + "".join(f"{x[k]:>12.3f}" for k in keys))
    return "\n".join(L) + "\n"


def main() -> int:
    from vpd_audit_2 import s6_record

    backup = json.load(open(D.RESULTS / "backup.json"))["files"]
    names = [n for h in D.BATCHES for n, _, _ in B.dose_units(h, list(SR.ATTACK), list(SR.STARTS))]
    units = V.checked_units(D.LOCAL / D.UNITS, backup, names, prefix=f"{D.UNITS}/")
    plan3 = json.load(open(R3.RESULTS / "backup.json"))["files"]
    v_names = [f"variants_{h}_{a}_s{s}" for h in D.BATCHES for a in SR.ATTACK for s in SR.STARTS]
    variants = V.checked_units(R3.LOCAL / R3.VARIANTS, plan3, v_names, prefix=f"{R3.VARIANTS}/")
    plan2 = V.checked_units(SR.LOCAL_UNITS, json.load(open(SR.RESULTS / "units_receipt.json"))["files"], [f"ones_{h}" for h in D.BATCHES])
    lead, _ = R.tables()
    res = dose(units, variants, plan2, lead)
    chk = checks(units)
    sys.stdout.write(report(res, chk))
    s6_record.update("dose", {"note": NOTE, "checks": chk, **res})
    return 0


if __name__ == "__main__":
    sys.exit(main())
