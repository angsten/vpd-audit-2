"""Plan 3 of the research log, Section 4: the reading of the first post's comparison rerun, as the research log's
Appendix G.2 and the freeze file's Part 1, Section 7 fix it. Committed before the launch.

    uv run python -m vpd_audit_2.s6_rerun > results/s6_followups/rerun.txt

Cells: pool Q's eight batches of 128 (QB1 to QB8) by starts 41 to 45, in each arm. A cell's value is the harm, in nats,
of the setting the search held after 20 steps, scored on its own batch (the unit's own-batch re-score, which equals the
search's record at step 20 bit for bit; checked). It is the harm, not the harm added above the start: the freeze file's
"the mean A over cells" of the cells' harm.

  - Per arm, the mean A over the 40 cells, with the interval of the two-factor construction: from the two-way analysis
    of variance of the 8 by 5 cells (`pilot_a_tables.anova_two_way`), the mean squares MS_B (batches, 7 df), MS_S
    (starts, 4 df), and MS_E (residual, 28 df). The batch and start components, (MS_B - MS_E)/5 and (MS_S - MS_E)/8,
    are each truncated at zero. Untruncated, the variance of the mean is (MS_B + MS_S - MS_E)/(K n_s); after
    truncation it is built from the mean squares that survive: a truncated component's mean square drops out, and MS_E
    keeps the coefficient that makes the sum the variance (-1 with both components, 0 with one, +1 with none). The
    degrees of freedom are Welch-Satterthwaite's on those mean squares, and the interval is A +/- t(0.975, df) sqrt(V).
    The three mean squares, both variances, and the df are printed.
  - The delta components' share, 1 - A_held / A_searched, with both means and their difference; called a share only
    when it is positive, and otherwise the difference is printed and said to be harm added by holding the deltas at 0.
    Beside it, the freeze file's "paired difference's interval": the same construction on the 40 cells of
    (searched - held at 0), each cell's two searches sharing a batch and a start.
  - The clause beside the first post's 0.80, from the searched arm (plan 3 of the research log fixes the arm before the data, since the
    paper's 0.83 came with the delta components searched): "about as much" if 0.80/A lies within a factor of 1.25 of 1
    (from 1/1.25 to 1.25, both included), "less" if below 1/1.25, "more" if above 1.25; 0.80/A printed to three
    decimals. The held-at-0 arm's clause beside it, as description.
  - Description: each batch's mean and each start's mean, per arm; the paper's 0.83 beside A.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_plan3_run as R3
from vpd_audit_2.pilot_a_tables import anova_two_way

FIRST_POST = 0.80  # the first post's aggregated explanations, on its own 1,024 texts
PAPER = 0.83  # the paper's 20-step adversary, on other texts
BAND = 1.25
ROW = "n20"


class Refusal(Exception):
    pass


def interval(Y: np.ndarray) -> dict[str, Any]:
    """The mean of a batches-by-starts table of cells, with the two-factor interval (this module's docstring)."""
    from scipy.stats import t as student

    Y = np.asarray(Y, dtype=np.float64)
    K, ns = Y.shape
    a = anova_two_way(Y)
    ms = {"B": a["MS_B"], "S": a["MS_S"], "E": a["MS_R"]}
    df = {"B": K - 1, "S": ns - 1, "E": (K - 1) * (ns - 1)}
    batch_u, start_u = (ms["B"] - ms["E"]) / ns, (ms["S"] - ms["E"]) / K
    coef = {"B": 1.0 if batch_u > 0 else 0.0, "S": 1.0 if start_u > 0 else 0.0}
    coef["E"] = 1.0 - coef["B"] - coef["S"]
    combination = sum(coef[k] * ms[k] for k in ms)
    v = combination / (K * ns)
    terms = {k: coef[k] * ms[k] for k in ms if coef[k] != 0}
    denom = sum(x ** 2 / df[k] for k, x in terms.items())
    nu = combination ** 2 / denom if denom > 0 else float("inf")
    half = float(student.ppf(0.975, nu) * np.sqrt(v)) if v > 0 and np.isfinite(nu) else 0.0
    mean = float(Y.mean())
    return {"mean": mean, "MS_B": ms["B"], "MS_S": ms["S"], "MS_E": ms["E"], "df": df,
            "batch_component_untruncated": float(batch_u), "start_component_untruncated": float(start_u),
            "surviving": [k for k in ("B", "S") if coef[k] == 1.0], "coefficients": coef,
            "variance_untruncated": float((ms["B"] + ms["S"] - ms["E"]) / (K * ns)), "variance": float(v), "df_welch_satterthwaite": float(nu),
            "half_width": half, "interval": [mean - half, mean + half]}


def clause(ratio: float) -> str:
    if ratio < 1.0 / BAND:
        return "less"
    if ratio > BAND:
        return "more"
    return "about as much"


def delta_share(searched: float, held: float) -> dict[str, Any]:
    share = 1.0 - held / searched
    return {"searched": searched, "held_at_0": held, "difference": searched - held, "share": share if share > 0 else None,
            "holding_at_0_added_harm": bool(held > searched)}


def load(folder: Path | None = None, backup_path: Path | None = None, starts_json: Path | None = None) -> dict[str, np.ndarray]:
    """Per arm, the 8 by 5 table of cells, from the local copy; every file checked against the receipt, and every unit
    against its batch, start, arm, steps, delta entries, the launch's commit, and the signed start's hash."""
    folder = R3.LOCAL if folder is None else Path(folder)
    backup = json.load(open(R3.RESULTS / "backup.json" if backup_path is None else backup_path))
    starts = json.load(open(R3.STARTS_JSON if starts_json is None else starts_json))["starts"]
    out = {}
    for arm in R3.ARMS:
        Y = np.full((len(R3.BATCHES), len(R3.STARTS)), np.nan)
        for i, b in enumerate(R3.BATCHES):
            for k, s in enumerate(R3.STARTS):
                rel = f"{R3.RERUN}/{arm}/search_{b}_s{s}.npz"
                data = (folder / rel).read_bytes()
                if hashlib.sha256(data).hexdigest() != backup["files"].get(rel):
                    raise Refusal(f"{rel} is not the file the receipt records")
                path = folder / rel
                meta = LR.unit_meta(path)
                held = arm == "held_at_0"
                ok = (meta["kind"] == "search" and meta["arm"] == R3.ARM_NAME[arm] and meta["batch"] == b and meta["start"] == s and meta["side"] == R3.RERUN_SIDE
                      and meta["n_steps"] == R3.N_STEPS and meta["commit"] == backup["commit"] and meta["start_sha256"] == starts[str(s)]["sha256"]
                      and meta["delta_held"] is held and (meta.get("delta_value") == R3.HELD_VALUE if held else "delta_value" not in meta))
                if not ok:
                    raise Refusal(f"{rel} is not the {arm} search of {b} from start {s} at the launch's commit")
                with np.load(path, allow_pickle=False) as z:
                    scored = [str(x) for x in z["scored_names"]]
                    steps = dict(zip((str(x) for x in z["hook_names"]), (int(x) for x in z["hook_steps"])))
                    h = float(z["own"][scored.index(ROW)])
                    record = z["record"]
                if steps[LR.SAVED[ROW]] != R3.N_STEPS or len(record) != R3.N_STEPS + 1 or np.float64(h).tobytes() != np.float64(record[R3.N_STEPS]).tobytes():
                    raise Refusal(f"{rel}: the own-batch harm at 20 steps is not the record's")
                Y[i, k] = h
        out[arm] = Y
    return out


def rerun(cells: dict[str, np.ndarray]) -> dict[str, Any]:
    arms = {arm: interval(Y) for arm, Y in cells.items()}
    for arm, Y in cells.items():
        arms[arm]["by_batch"] = {b: float(x) for b, x in zip(R3.BATCHES, Y.mean(axis=1))}
        arms[arm]["by_start"] = {str(s): float(x) for s, x in zip(R3.STARTS, Y.mean(axis=0))}
        arms[arm]["ratio"] = FIRST_POST / arms[arm]["mean"]
        arms[arm]["clause"] = clause(arms[arm]["ratio"])
    paired = interval(cells["searched"] - cells["held_at_0"])
    return {"arms": arms, "delta": {**delta_share(arms["searched"]["mean"], arms["held_at_0"]["mean"]), "paired_difference": paired}}


def _interval_lines(x: dict[str, Any], unit: str = "nats") -> list[str]:
    df = x["df"]
    trunc = {"B": "batch", "S": "start"}
    kept = ", ".join(trunc[k] for k in x["surviving"]) or "neither"
    return [f"    mean squares: MS_B {x['MS_B']:.6f} ({df['B']} df), MS_S {x['MS_S']:.6f} ({df['S']} df), MS_E {x['MS_E']:.6f} ({df['E']} df)",
            f"    components before truncation: batch {x['batch_component_untruncated']:.6f}, start {x['start_component_untruncated']:.6f}; surviving: {kept}",
            f"    variance of the mean: untruncated {x['variance_untruncated']:.6g}, after truncation {x['variance']:.6g}; Welch-Satterthwaite df "
            f"{x['df_welch_satterthwaite']:.2f}",
            f"    95 percent interval: {x['interval'][0]:.3f} to {x['interval'][1]:.3f} {unit} (half-width {x['half_width']:.3f})"]


def report(res: dict[str, Any]) -> str:
    a, d = res["arms"], res["delta"]
    L = ["The first post's comparison rerun (plan 3 of the research log, Section 4; the research log, Appendix G.2; the freeze file, Part 1, Section 7).",
         "Pool Q, the first post's 1,024 texts, as eight batches of 128 in the manifest's order; starts 41 to 45; 20 steps; each search scored on its",
         "own batch only. A cell is the harm (nats) of the setting after step 20 on its batch. 40 cells per arm.", ""]
    for arm, label in (("searched", "Delta components searched, as the paper does"), ("held_at_0", "Delta components held at 0, as the first post's aggregations did")):
        x = a[arm]
        L.append(f"{label}: A = {x['mean']:.3f} nats, beside the paper's {PAPER:.2f}.")
        L += _interval_lines(x)
        L.append("    by batch: " + ", ".join(f"{b} {v:.3f}" for b, v in x["by_batch"].items()))
        L.append("    by start: " + ", ".join(f"s{s} {v:.3f}" for s, v in x["by_start"].items()))
        L.append("")
    s = a["searched"]
    L.append(f"The clause beside the first post's {FIRST_POST:.2f}, from the searched arm: 0.80/A = {s['ratio']:.3f}; the clause is \"{s['clause']}\".")
    h = a["held_at_0"]
    L.append(f"  As description, the held-at-0 arm's: 0.80/A = {h['ratio']:.3f}; its clause would be \"{h['clause']}\".")
    L.append("")
    L.append(f"The delta components: searched {d['searched']:.3f}, held at 0 {d['held_at_0']:.3f}, difference {d['difference']:.3f} nats.")
    if d["share"] is not None:
        L.append(f"  Their share, 1 - A_held / A_searched: {d['share']:.3f}.")
    else:
        L.append("  Not a share: holding the delta components at 0 " + ("added harm" if d["holding_at_0_added_harm"] else "changed nothing")
                 + f"; the difference is {d['difference']:.3f} nats.")
    L.append("  The paired difference (searched - held at 0, cell by cell), its interval by the same construction:")
    L += _interval_lines(d["paired_difference"])
    return "\n".join(L) + "\n"


def main() -> int:
    from vpd_audit_2 import s6_record

    res = rerun(load())
    sys.stdout.write(report(res))
    s6_record.update("rerun", res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
