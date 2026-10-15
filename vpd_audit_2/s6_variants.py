"""Session 6, plan 3, Section 7: three intact-background variants on cell set S4. Added after the readings, as
description; nothing here has a line. Committed before the launch.

    uv run python -m vpd_audit_2.s6_variants > results/s6_followups/variants.txt

Cell set S4: the run's 400 carried settings (80 attack searches at 20, 40, 80, 160, and 320 steps) on H1, H5, H9, and
H13, 320 cells per length. Each setting scored three ways (`s6_build`):

  - V1, the zeros alone on an intact model: every entry at exactly 0 stays 0, every other entry 1, delta entries included;
  - V2, Part Z on an intact model: where the label is zero the mask is s_c, where it is positive the mask is 1; the delta
    entries at s, as in Part Z;
  - V3, Part P on an intact model: where the label is positive the mask is l + s_c (1 - l), where it is zero the mask
    is 1; the delta entries at 1.

Per variant and length: the pooled share of carried added harm kept, measured above the saved start as Section 8(d)
of the conventions measures it, the sum over cells of (the variant's harm - the saved start's harm) over the sum of
(the saved carried harm - the saved start's harm); and the variant's mean harm in nats over the cells, beside the
all-ones harm (plan 2's `ones` pass on the same four batches, their mean). The check units' outcomes are printed first.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_run as SR

NOTE = "Added after the readings, as description (plan 3, Section 7); no line."


def checked_units(folder: Path, receipt: dict[str, str], names: list[str], prefix: str = "") -> R.Units:
    """The named units, each file checked against the receipt first."""
    for n in names:
        rel = f"{prefix}{n}.npz"
        if hashlib.sha256((folder / f"{n}.npz").read_bytes()).hexdigest() != receipt.get(rel):
            raise R.Refusal(f"{rel} is not the file the receipt records")
    return R.Units(folder)


def checks(units: R.Units) -> dict[str, Any]:
    out = {}
    for h in R3.VARIANT_BATCHES:
        u = units.get(f"variants_check_{h}")["passes"]
        out[h] = {pid: {"harm": v[0], "reference": v[2]["reference"], "bits_equal": bool(np.float64(v[0]).tobytes() == np.float64(v[2]["reference"]).tobytes())}
                  for pid, v in u.items()}
    return out


def variants(units: R.Units, plan2: R.Units, lead: dict[str, Any]) -> dict[str, Any]:
    att = list(enumerate(str(x) for x in lead["attack_names"]))
    held = [(j, str(h)) for j, h in enumerate(str(x) for x in lead["heldout_names"]) if h in R3.VARIANT_BATCHES]
    starts = list(enumerate(int(x) for x in lead["starts"]))
    if [h for _, h in held] != list(R3.VARIANT_BATCHES):
        raise R.Refusal("the run's table does not hold S4's four held-out batches")
    ones = {h: plan2.harm(f"ones_{h}", "ones") for _, h in held}
    out: dict[str, Any] = {"all_ones_harm": float(np.mean(list(ones.values()))), "all_ones_by_batch": ones, "rows": {}}
    for row in B.SPLIT_ROWS:
        q = R.row_index(lead, row)
        den = 0.0
        num = {v: 0.0 for v in B.VARIANTS}
        harms: dict[str, list[float]] = {v: [] for v in B.VARIANTS}
        cells = 0
        for i, a in att:
            for j, h in held:
                for k, s in starts:
                    base = float(lead["init_H"][j, k])
                    den += float(lead["carried"][i, j, k, q]) - base
                    cells += 1
                    for v in B.VARIANTS:
                        x = units.harm(f"variants_{h}_{a}_s{s}", f"{v}|{row}")
                        num[v] += x - base
                        harms[v].append(x)
        out["rows"][row] = {"cells": cells, **{v: {"kept_share": float(num[v] / den), "mean_harm": float(np.mean(harms[v]))} for v in B.VARIANTS}}
    return out


def report(res: dict[str, Any], chk: dict[str, Any]) -> str:
    L = ["Three intact-background variants on cell set S4 (session 6, plan 3, Section 7). " + NOTE,
         "S4: the 400 carried settings on H1, H5, H9, and H13, 320 cells per length. Kept share: the sum over cells of (variant's harm - saved start",
         "harm) over the sum of (saved carried harm - saved start harm), as the conventions' Section 8(d). V1: entries at exactly 0 stay 0, every other",
         "entry 1. V2: mask s where the label is zero, 1 where positive, delta entries s. V3: mask l + s(1 - l) where the label is positive, 1 where zero,",
         "delta entries 1.", "", "The checks, per batch (the full setting on the split's path and the flat path, and the start on the split's path):"]
    for h, x in chk.items():
        L.append(f"  {h}: " + "; ".join(f"{pid} {v['harm']:.6f} against {v['reference']:.6f}, bit for bit {'yes' if v['bits_equal'] else 'no'}"
                                       for pid, v in x.items()))
    L += ["", f"The all-ones harm on the four batches: {res['all_ones_harm']:.4f} nats (" + ", ".join(f"{h} {v:.4f}" for h, v in res["all_ones_by_batch"].items()) + ").",
          "", "    length   cells   " + "   ".join(f"{v}: kept share, mean harm" for v in B.VARIANTS)]
    for row, x in res["rows"].items():
        L.append(f"    {row:<7}  {x['cells']:>5}   " + "   ".join(f"{v}: {x[v]['kept_share']:>10.3f}, {x[v]['mean_harm']:>9.3f}" for v in B.VARIANTS))
    return "\n".join(L) + "\n"


def main() -> int:
    from vpd_audit_2 import s6_record

    backup = json.load(open(R3.RESULTS / "backup.json"))["files"]
    names = [n for h in R3.VARIANT_BATCHES for n, _, _ in B.variant_units(h, list(SR.ATTACK), list(SR.STARTS))]
    units = checked_units(R3.LOCAL / R3.VARIANTS, backup, names, prefix=f"{R3.VARIANTS}/")
    plan2_receipt = json.load(open(SR.RESULTS / "units_receipt.json"))["files"]
    plan2 = checked_units(SR.LOCAL_UNITS, plan2_receipt, [f"ones_{h}" for h in R3.VARIANT_BATCHES])
    lead, _ = R.tables()
    res = variants(units, plan2, lead)
    chk = checks(units)
    sys.stdout.write(report(res, chk))
    s6_record.update("variants", {"note": NOTE, "checks": chk, **res})
    return 0


if __name__ == "__main__":
    sys.exit(main())
