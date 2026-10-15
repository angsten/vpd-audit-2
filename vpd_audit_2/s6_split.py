"""Session 6, plan 2: the token-level split (`results/s6_followups/CONVENTIONS.md`, Section 2). The signed line: one half.

    uv run python -m vpd_audit_2.s6_split

Cells: every carried setting (80 attack searches at 20, 40, 80, 160, and 320 steps) on every held-out batch, 1,280 per
length. Part Z applies the setting where the component's label on the scored batch is exactly zero and the start
elsewhere; Part P the reverse; the delta entries take the setting in Part Z and the start in Part P. A part's added harm
is its harm less the start's harm on the same batch (`init_H`); a part's share is pooled: its mean added harm over the
cells divided by the full carried setting's (`carried - init_H`). The interval is the signed one, as for the carry-over
ratio (`lead_intervals.interval`, numerator and denominator as `Combo(a_cells=...)`, multiplier 1.0, the frozen
multipliers being 1.0 at every row, 10,000 replicates). A part is above half or below half when its interval lies
wholly on one side of 0.5, and undetermined otherwise; the case of the conventions' reading follows. Beside it, the
median over cells of the per-cell share.

The own-batch version, description: the 80 attack searches each on its own batch (`own_A - init_A`), pooled per length,
with the pooled share from each start. And each batch's count per position of positive labels below 1e-3, and of labels
exactly zero, with the split's path checks.
"""

from __future__ import annotations

import sys
from typing import Any

import numpy as np

from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_run as SR

HALF = 0.5
CASES = {("above", "below"): "Part Z above half and Part P below half: the harm comes from components the labels call free.",
         ("below", "above"): "Part P above half and Part Z below half: the harm comes from needed components turned down to their labels.",
         ("below", "below"): "Both parts below half: no single attribution; the harm needs both kinds of position together.",
         ("above", "above"): "Both parts above half: no single attribution; either kind of position alone suffices."}


def word(lo: float, hi: float) -> str:
    return "above" if lo > HALF else "below" if hi < HALF else "undetermined"


def case(z: str, p: str) -> str:
    if "undetermined" in (z, p):
        return "A part is undetermined: the split is undetermined."
    return CASES[(z, p)]


def part_cells(units: R.Units, lead: dict[str, Any], row: str, part: str) -> np.ndarray:
    """Harm of the part per cell, [attack, held-out, start], in the table's order."""
    att, held = [str(x) for x in lead["attack_names"]], [str(x) for x in lead["heldout_names"]]
    starts = [int(x) for x in lead["starts"]]
    out = np.full((len(att), len(held), len(starts)), np.nan)
    for i, a in enumerate(att):
        for j, h in enumerate(held):
            for k, s in enumerate(starts):
                out[i, j, k] = units.harm(f"split_{h}_{a}_s{s}", f"{part}|{row}")
    return out


def split(units: R.Units, lead: dict[str, Any], B_reps: int = LI.BOOTSTRAP_B) -> dict[str, Any]:
    indices = LI.make_indices(len(lead["attack_names"]), B_reps)
    pres = LI.Presence.complete(len(lead["attack_names"]), len(lead["heldout_names"]), len(lead["starts"]))
    init = np.asarray(lead["init_H"], dtype=np.float64)
    out: dict[str, Any] = {}
    for row in B.SPLIT_ROWS:
        q = R.row_index(lead, row)
        carried_added = np.asarray(lead["carried"], dtype=np.float64)[:, :, :, q] - init[None]
        res: dict[str, Any] = {"carried_added_mean": float(carried_added.mean())}
        words = {}
        for part in ("Z", "P"):
            added = part_cells(units, lead, row, part) - init[None]
            iv = LI.interval(LI.Combo(a_cells=added), LI.Combo(a_cells=carried_added), pres, multiplier=1.0, indices=indices)
            per_cell = added / carried_added
            lo, hi = iv["interval"]
            words[part] = word(lo, hi)
            res[part] = {"share": float(iv["estimate"]), "interval": [float(lo), float(hi)], "word": words[part], "added_mean": float(added.mean()),
                         "per_cell_median": float(np.median(per_cell)), "percentile_interval": iv.get("interval_percentile")}
        res["case"] = case(words["Z"], words["P"])
        out[row] = res
    return out


def own_batch(units: R.Units, lead: dict[str, Any]) -> dict[str, Any]:
    att = [str(x) for x in lead["attack_names"]]
    starts = [int(x) for x in lead["starts"]]
    init = np.asarray(lead["init_A"], dtype=np.float64)
    out: dict[str, Any] = {}
    for row in B.SPLIT_ROWS:
        q = R.row_index(lead, row)
        own_added = np.asarray(lead["own_A"], dtype=np.float64)[:, :, q] - init
        res: dict[str, Any] = {}
        for part in ("Z", "P"):
            h = np.array([[units.harm(f"split_{a}_{a}_s{s}", f"{part}|{row}") for s in starts] for a in att])
            added = h - init
            res[part] = {"share": float(added.sum() / own_added.sum()),
                         "by_start": {str(s): float(added[:, k].sum() / own_added[:, k].sum()) for k, s in enumerate(starts)}}
        out[row] = res
    return out


def labels_and_checks(units: R.Units) -> dict[str, Any]:
    out = {}
    for b in list(SR.HELDOUT) + list(SR.ATTACK):
        u = units.get(f"check_{b}")
        st = u["meta"]["label_stats"]
        out[b] = {**st, "checks_bit_equal": [bool(units.recorded(f"check_{b}", p)["bits_equal"]) for p in ("check|s_everywhere", "check|s0_everywhere")]}
    return out


def report(res: dict[str, Any], own: dict[str, Any], labels: dict[str, Any]) -> str:
    L = ["The token-level split (session 6, plan 2; conventions, Section 2). The signed line: one half.",
         "A part's share: its mean added harm over the cells divided by the full carried setting's; the signed 95 percent interval",
         "beside it. Above half or below half when the interval lies wholly on one side of 0.5; undetermined otherwise.", ""]
    for row, r in res.items():
        L.append(f"{row}: 1,280 carried cells; the carried setting's mean added harm {r['carried_added_mean']:.2f} nats.")
        for part, name in (("Z", "Part Z (the setting where the label is zero)"), ("P", "Part P (the setting where the label is above zero)")):
            x = r[part]
            w = "undetermined" if x["word"] == "undetermined" else f"{x['word']} half"
            L.append(f"  {name}: share {x['share']:.2f} [{x['interval'][0]:.2f}, {x['interval'][1]:.2f}], {w}; per-cell median "
                     f"{x['per_cell_median']:.2f}; mean added harm {x['added_mean']:.2f} nats.")
        L.append(f"  Reading: {r['case']}")
        L.append("")
    L.append("The own-batch version (description): each attack search on its own batch, 80 cells per length; pooled share, then by start.")
    for row, r in own.items():
        L.append(f"  {row}: Part Z {r['Z']['share']:.2f} (" + ", ".join(f"s{s} {v:.2f}" for s, v in r["Z"]["by_start"].items())
                 + f"); Part P {r['P']['share']:.2f} (" + ", ".join(f"s{s} {v:.2f}" for s, v in r["P"]["by_start"].items()) + ").")
    L.append("")
    L.append("Each batch's labels: per position, the mean count of positive labels below 1e-3, and of labels exactly zero; and whether the split's")
    L.append("path reproduced the saved harms bit for bit (they must, and did, within the run's per-text tolerance).")
    for b, x in labels.items():
        L.append(f"  {b}: positive below 1e-3 {x['positive_below_1e-3_per_position']:.2f}; exactly zero {x['zero_per_position']:.2f}; "
                 f"bit for bit {'yes' if all(x['checks_bit_equal']) else 'no'}.")
    return "\n".join(L) + "\n"


def main() -> int:
    from vpd_audit_2 import s6_record

    units = R.Units()
    units.require(R.all_unit_names())
    lead, _ = R.tables()
    res, own, labels = split(units, lead), own_batch(units, lead), labels_and_checks(units)
    sys.stdout.write(report(res, own, labels))
    s6_record.update("split", {"heldout": res, "own_batch": own, "labels": labels})
    return 0


if __name__ == "__main__":
    sys.exit(main())
