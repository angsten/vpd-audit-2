"""Plan 2 of the research log: three cheap controls and the rounding check (`results/s6_followups/CONVENTIONS.md`, Section 8, with
the addendum's item 2). Description.

    uv run python -m vpd_audit_2.s6_controls

Cell set S4: every carried setting the run saved (80 attack searches at five lengths) on H1, H5, H9, and H13; the saved
harms of the same settings (`carried`) and of the five starts (`init_H`) on those batches are the reference.

  - (a) The delta components' share: per length, the sum over cells of (setting with its delta entries at 1 - start with
    its delta entries at 1) over the sum of (saved setting - saved start); the same from each start alone; and from the
    saved settings, the delta entries at exactly 0, exactly 1, and between.
  - (b1) Every mask at its label: the mean over the 16 held-out and 16 attack batches, beside the start's 0.22 and the first
    post's 0.34 on its own texts.
  - (b2) The first post's aggregated explanations: per rung (64 positions and 16), the mean harm over draws and held-out
    batches, the added harm above (b1), the draw-to-draw range of the draws' means, and the union's size, beside the first
    post's 0.80, 0.46, and about 4,544 components.
  - (c) Two coarser shuffles, per kind and length: the copies' mean harm, beside the start's 0.22 and the run's band-matched
    0.30 to 0.32; the share of alive entries moved by more than 0.5; for the whole-matrix kind, the share of the setting's
    zeros that land on never-needed components.
  - (d) Rounding, per length: the share of carried added harm remaining, pooled, for the rounded setting and for the snap
    (at most 0.2 to 0, at least 0.8 to 1, the rest kept; the addendum, item 2), each against the saved start; the rounded
    start's harm beside.
"""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

import numpy as np

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import pilot as P
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_run as SR

START_HARM = 0.22  # the conventions' quoted figures
FIRST_POST_B1 = 0.34
FIRST_POST_B2 = (0.80, 0.46, 4544)
BAND_MATCHED = (0.30, 0.32)
RUN_UNITS_LOCAL = SR.REPO_ROOT / ".cache" / "s5_lead_units" / "run" / "lead"


def _cells(lead: dict[str, Any]) -> tuple[list[tuple[int, str]], list[tuple[int, str]], list[tuple[int, int]]]:
    att = list(enumerate(str(x) for x in lead["attack_names"]))
    held = [(j, str(h)) for j, h in enumerate(str(x) for x in lead["heldout_names"]) if h in B.S4]
    starts = list(enumerate(int(x) for x in lead["starts"]))
    return att, held, starts


def delta_share(units: R.Units, lead: dict[str, Any]) -> dict[str, Any]:
    att, held, starts = _cells(lead)
    out = {}
    for row in B.SPLIT_ROWS:
        q = R.row_index(lead, row)
        num = np.zeros(len(starts))
        den = np.zeros(len(starts))
        for i, a in att:
            for j, h in held:
                for k, s in starts:
                    num[k] += units.harm(f"controls_{h}_{a}_s{s}", f"a|{row}") - units.harm(f"control_starts_{h}", f"a_start|{s}")
                    den[k] += float(lead["carried"][i, j, k, q]) - float(lead["init_H"][j, k])
        out[row] = {"share": float(num.sum() / den.sum()), "by_start": {str(s): float(num[k] / den[k]) for k, s in starts}}
    return out


def delta_entry_values(lead: dict[str, Any]) -> dict[str, Any]:
    """From the saved settings of the 80 attack searches: their delta entries at exactly 0, exactly 1, and between."""
    lay = P.layout()
    pos = LR.delta_positions(lay)
    hashes = SR.run_unit_hashes()
    att, _, starts = _cells(lead)
    out = {row: {"exactly_0": 0, "exactly_1": 0, "between": 0} for row in B.SPLIT_ROWS}
    for _, a in att:
        for _, s in starts:
            name = f"search_{a}_s{s}.npz"
            data = (RUN_UNITS_LOCAL / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != hashes[name]:
                raise R.Refusal(f"{name} is not the run's unit")
            unit = SR.run_unit_from_bytes(data, a, s)
            for row in B.SPLIT_ROWS:
                d = B.saved(unit, row)[0][pos]
                out[row]["exactly_0"] += int((d == 0).sum())
                out[row]["exactly_1"] += int((d == 1).sum())
                out[row]["between"] += int(((d > 0) & (d < 1)).sum())
    return out


def b_controls(units: R.Units, b2_record: dict[str, Any]) -> dict[str, Any]:
    held = [units.harm(f"b_{h}", "b1") for h in SR.HELDOUT]
    att = [units.harm(f"b1_{a}", "b1") for a in SR.ATTACK]
    b1_held = float(np.mean(held))
    out: dict[str, Any] = {"b1": {"mean_all": float(np.mean(held + att)), "mean_heldout": b1_held, "mean_attack": float(np.mean(att))}, "b2": {}}
    for rung, draws in B.B2_RUNGS:
        keys = [f"r{rung}_d{d}" for d in range(1, draws + 1)]
        per_draw = [float(np.mean([units.harm(f"b_{h}", f"b2|{key}") for h in SR.HELDOUT])) for key in keys]
        sizes = [int(b2_record["settings"][key]["union_size"]) for key in keys]
        out["b2"][str(rung)] = {"mean": float(np.mean(per_draw)), "added_above_b1": float(np.mean(per_draw) - b1_held),
                                "draw_range": [min(per_draw), max(per_draw)], "union_size_mean": float(np.mean(sizes)), "union_size_range": [min(sizes), max(sizes)]}
    return out


def coarse(units: R.Units, lead: dict[str, Any]) -> dict[str, Any]:
    att, held, starts = _cells(lead)
    out: dict[str, Any] = {}
    for kind in B.COARSE_KINDS:
        out[kind] = {}
        for row in B.SPLIT_ROWS:
            harms, moved, zeros = [], [], []
            for _, a in att:
                for _, h in held:
                    for _, s in starts:
                        pid = f"c|{kind}|{row}"
                        harms.append(units.harm(f"controls_{h}_{a}_s{s}", pid))
                        rec = units.recorded(f"controls_{h}_{a}_s{s}", pid)
                        moved.append(rec["moved_alive_over_half"])
                        zeros.append(rec["zeros_on_never_needed"])
            out[kind][row] = {"mean_harm": float(np.mean(harms)), "moved_alive_over_half": float(np.mean(moved)),
                              "zeros_on_never_needed": float(np.nanmean(zeros))}
    return out


def rounding(units: R.Units, lead: dict[str, Any]) -> dict[str, Any]:
    att, held, starts = _cells(lead)
    out: dict[str, Any] = {"rounded_start_harm": float(np.mean([units.harm(f"control_starts_{h}", f"d_start|{s}") for _, h in held for _, s in starts]))}
    for row in B.SPLIT_ROWS:
        q = R.row_index(lead, row)
        den = 0.0
        num = {"rounded": 0.0, "snapped": 0.0}
        for i, a in att:
            for j, h in held:
                for k, s in starts:
                    base = float(lead["init_H"][j, k])
                    den += float(lead["carried"][i, j, k, q]) - base
                    for v in num:
                        num[v] += units.harm(f"controls_{h}_{a}_s{s}", f"d|{v}|{row}") - base
        out[row] = {v: float(num[v] / den) for v in num}
    return out


def report(a: dict[str, Any], deltas: dict[str, Any], b: dict[str, Any], c: dict[str, Any], d: dict[str, Any]) -> str:
    L = ["Three cheap controls and the rounding check (plan 2 of the research log; conventions, Section 8, with the addendum). Description only.",
         "Cell set S4: the 400 carried settings on H1, H5, H9, and H13 (320 cells per length).", "",
         "(a) The delta components' share of carried added harm remaining with the 24 delta entries at 1; from each start alone; and the saved",
         "    settings' delta entries (80 settings by 24 entries) at exactly 0, exactly 1, and between."]
    for row, x in a.items():
        de = deltas[row]
        L.append(f"  {row}: {x['share']:.2f} (by start: " + ", ".join(f"s{s} {v:.2f}" for s, v in x["by_start"].items())
                 + f"); delta entries at 0 {de['exactly_0']}, at 1 {de['exactly_1']}, between {de['between']}.")
    L += ["", f"(b1) Every mask at its label: mean harm {b['b1']['mean_all']:.2f} over the 32 batches (held-out {b['b1']['mean_heldout']:.2f}, attack "
          f"{b['b1']['mean_attack']:.2f}), beside the start's {START_HARM} and the first post's {FIRST_POST_B1} on its own texts.", "",
          f"(b2) The first post's aggregated explanations, drawn from its recipient texts; beside its {FIRST_POST_B2[0]:.2f}, {FIRST_POST_B2[1]:.2f}, and "
          f"about {FIRST_POST_B2[2]:,} components:"]
    for rung, x in b["b2"].items():
        L.append(f"  {rung} positions: mean harm {x['mean']:.2f}; added above (b1) {x['added_above_b1']:.2f}; draws' means from {x['draw_range'][0]:.2f} to "
                 f"{x['draw_range'][1]:.2f}; union size {x['union_size_mean']:.0f} ({x['union_size_range'][0]} to {x['union_size_range'][1]}).")
    L += ["", f"(c) Two coarser shuffles: the copies' mean harm, beside the start's {START_HARM:.2f} and the run's band-matched {BAND_MATCHED[0]:.2f} to "
          f"{BAND_MATCHED[1]:.2f}; the share of alive entries moved by more than 0.5; for the whole matrix, the share of zeros landing on never-needed components."]
    for kind, rows in c.items():
        L.append(f"  {'within alive and never-needed' if kind == 'alive_and_never_needed' else 'over the whole matrix'}:")
        for row, x in rows.items():
            L.append(f"    {row}: mean harm {x['mean_harm']:.2f}; alive moved by more than 0.5: {x['moved_alive_over_half']:.2f}"
                     + (f"; zeros on never-needed: {x['zeros_on_never_needed']:.2f}" if kind == "whole_matrix" else "") + ".")
    L += ["", f"(d) Rounding: the share of carried added harm remaining against the saved start; the rounded start's harm {d['rounded_start_harm']:.2f}."]
    for row in B.SPLIT_ROWS:
        L.append(f"  {row}: rounded {d[row]['rounded']:.2f}; snapped (at most 0.2 to 0, at least 0.8 to 1) {d[row]['snapped']:.2f}.")
    return "\n".join(L) + "\n"


def main() -> int:
    from vpd_audit_2 import s6_record

    units = R.Units()
    units.require(R.all_unit_names())
    lead, _ = R.tables()
    b2_record = json.load(open(SR.B2_RECORD))
    a, deltas, b, c, d = delta_share(units, lead), delta_entry_values(lead), b_controls(units, b2_record), coarse(units, lead), rounding(units, lead)
    sys.stdout.write(report(a, deltas, b, c, d))
    s6_record.update("controls", {"a": a, "delta_entries": deltas, "b": b, "c": c, "d": d})
    return 0


if __name__ == "__main__":
    sys.exit(main())
