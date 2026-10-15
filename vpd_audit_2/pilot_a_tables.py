"""Session 4, plan 6, A4: Part A's derived tables, computed mechanically from the stored records
(`sessions/004/engineering/plan_6.md`, Sections 5 and 7).

    uv run python -m vpd_audit_2.pilot_a_tables      (reads results/s4_pilot/part_a/, writes tables.json there)

Sealing (Section 3): from the shuffles (A3) only the noise ratio (s_sh / sqrt 8) / |D| is written, as its median over the
8 batches per source type; never D, the shuffled means, or a shuffle's harm.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env
from vpd_audit_2 import pilot as P

PART_A = env.REPO_ROOT / "results" / "s4_pilot" / "part_a"
SEC_PER_STEP = 0.39
SEC_PER_PASS = 0.18
RATES = (6.25, 7.50)
PASSES_PER_CELL = 74
DF_PASSES_PER_CELL = 45
DESIGNS = [(8, 3), (8, 5), (8, 8), (16, 3), (16, 5), (16, 8)]


# ----------------------------------------------------------------------------- per run


def alternation_onset(record: list[float], run: int = 10) -> int | None:
    """The first k >= 2 such that the one-step change flips sign at every step from k to k + run - 1."""
    d = np.diff(np.asarray(record, dtype=np.float64))  # d[k - 1] = KL(k) - KL(k - 1)
    s = np.sign(d)
    for k in range(2, len(record) - run + 1):
        if all(s[i - 1] != 0 and s[i - 2] != 0 and s[i - 1] == -s[i - 2] for i in range(k, k + run)):
            return k
    return None


def per_run(record: list[float]) -> dict[str, Any]:
    out: dict[str, Any] = {"KL0": record[0], "plateau": float(np.mean(record[301:321])), "alternation_onset": alternation_onset(record)}
    for h in P.STAGES_A4:
        c = P.crossing(record, h)
        out[f"k_{h:g}"] = c["k"]
        out[f"overshoot_{h:g}"] = None if c["missing"] else c["KL_k"] - h
        out[f"stage_denominator_{h:g}"] = None if c["missing"] else c["KL_k"] - record[0]
    for n in P.BUDGETS:
        a, b = record[n], record[n - 1]
        out[f"KL_{n}"], out[f"KL_{n - 1}"] = a, b
        out[f"amplitude_{n}"] = abs(a - b)
        out[f"cycling_{n}"] = bool(abs(a - b) > 0.1 * max(abs(a), abs(b)))
    out["added_20"] = record[20] - record[0]
    return out


# ----------------------------------------------------------------------------- estimators


def anova_two_way(Y: np.ndarray) -> dict[str, Any]:
    """Two-way analysis of variance without replication, rows = batches, columns = starts."""
    Y = np.asarray(Y, dtype=np.float64)
    nb, ns = Y.shape
    mu = Y.mean()
    rb, cs = Y.mean(axis=1), Y.mean(axis=0)
    ms_b = ns * ((rb - mu) ** 2).sum() / (nb - 1)
    ms_s = nb * ((cs - mu) ** 2).sum() / (ns - 1)
    resid = Y - rb[:, None] - cs[None, :] + mu
    ms_r = (resid ** 2).sum() / ((nb - 1) * (ns - 1))
    b_u, c_u = (ms_b - ms_r) / ns, (ms_s - ms_r) / nb
    return {"mean": float(mu), "MS_B": float(ms_b), "MS_S": float(ms_s), "MS_R": float(ms_r), "df": {"B": nb - 1, "S": ns - 1, "R": (nb - 1) * (ns - 1)},
            "sigma2_int": float(ms_r), "sigma2_b": float(max(0.0, b_u)), "sigma2_c": float(max(0.0, c_u)),
            "sigma2_b_untruncated": float(b_u), "sigma2_c_untruncated": float(c_u)}


def pooled_variance(groups: list[list[float]]) -> dict[str, Any]:
    v = [float(np.var(g, ddof=1)) for g in groups]
    return {"per_group": v, "pooled": float(np.mean(v)), "df": int(sum(len(g) - 1 for g in groups))}


def width(mu: float, s2b: float, s2int: float, s2c: float, K: int, ns: int) -> dict[str, float]:
    from scipy.stats import t

    p = 2 * s2b / K + 2 * s2int / (K * ns)
    s = s2c / ns
    if p + s == 0:
        return {"w": 0.0, "nu": float("inf"), "P": p, "S": s}
    nu = (p + s) ** 2 / ((p ** 2 / (K - 1) if p else 0.0) + (s ** 2 / (ns - 1) if s else 0.0))
    return {"w": float(t.ppf(0.975, nu) * math.sqrt(p + s) / mu), "nu": float(nu), "P": p, "S": s}


def cost(K: int, ns: int) -> dict[str, Any]:
    lead = (2 * K * ns * 320 * SEC_PER_STEP + PASSES_PER_CELL * K * K * ns * SEC_PER_PASS) / 3600
    df = (2 * 8 * ns * 320 * SEC_PER_STEP + DF_PASSES_PER_CELL * 64 * ns * SEC_PER_PASS) / 3600
    return {"search_steps": 2 * K * ns * 320, "scoring_passes": PASSES_PER_CELL * K * K * ns, "B200_hours": lead,
            "lead_cost": [lead * r for r in RATES], "delta_frozen_8x8_B200_hours": df, "delta_frozen_cost": [df * r for r in RATES],
            "total_cost": [(lead + df) * r for r in RATES]}


def design_table(components: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for K, ns in DESIGNS:
        ws = {n: width(c["mean"], c["sigma2_b"], c["sigma2_int"], c["sigma2_c"], K, ns) for n, c in components.items()}
        floor = any(c["sigma2_c"] > 0.1 * 2 * c["sigma2_int"] / K for c in components.values())
        row = {"K": K, "n_s": ns, "w": {n: v["w"] for n, v in ws.items()}, "nu": {n: v["nu"] for n, v in ws.items()},
               "start_floor_binds": bool(floor), "start_floor_met": bool(ns >= 5 or not floor), **cost(K, ns)}
        row["meets_w40_and_w80"] = bool(ws["40"]["w"] <= 0.25 and ws["80"]["w"] <= 0.25)
        row["qualifies"] = bool(row["meets_w40_and_w80"] and row["start_floor_met"])
        rows.append(row)
    return rows


# ----------------------------------------------------------------------------- the tables


def load(part_a: Path = PART_A) -> dict[str, Any]:
    """The runs and the sealed shuffle harms, for A4's ratio only. The sealed files are the pilot's merged
    `a3_shuffles.npz` or one `a3_shuffles_C{j}.npz` per batch (plan 7, item 5); their keys are batch-prefixed and disjoint."""
    runs = json.load(open(part_a / "runs.json"))
    sealed: dict[str, np.ndarray] = {}
    files = sorted((part_a / "sealed").glob("a3_shuffles*.npz"))
    assert files, "no sealed shuffle file"
    for path in files:
        with np.load(path) as z:
            assert not set(z.files) & set(sealed), f"{path.name}: keys already loaded"
            sealed.update({k: z[k] for k in z.files})
    return {"runs": runs, "sealed": sealed}


def tables(data: dict[str, Any]) -> dict[str, Any]:
    runs = data["runs"]
    a1 = {(b, int(s)): r for b, v in runs["a1"].items() for s, r in v.items()}
    batches, starts = list(P.PILOT_BATCHES), list(P.PILOT_STARTS)
    derived = {f"{b}|s{s}": per_run(a1[(b, s)]["record"]) for b in batches for s in starts}
    a2 = {(b, r0): v["accepted"] for b, d in runs["a2"].items() for r0, v in d.items()}
    derived.update({f"{b}|s{int(b[1:])}|perturb{v['start_key'][-1]}": per_run(v["record"]) for (b, r0), v in a2.items() if v is not None})
    out: dict[str, Any] = {"per_run": derived}

    def U(rec: list[float], n: int) -> float:
        return rec[n] - rec[0]

    comps = {}
    for n in P.BUDGETS:
        Y = np.array([[U(a1[(b, s)]["record"], n) for s in starts] for b in batches])
        comps[str(n)] = anova_two_way(Y)
    Yp = np.array([[derived[f"{b}|s{s}"]["plateau"] - a1[(b, s)]["record"][0] for s in starts] for b in batches])
    out["variance_components"] = {"budgets": comps, "plateau": anova_two_way(Yp),
                                  "note": "U = KL(n) - KL(0) over the 8 x 8 table; rows batches C1..C8, columns starts 1..8"}
    stages = {}
    for h in P.STAGES:
        ks = np.array([[derived[f"{b}|s{s}"][f"k_{h:g}"] for s in starts] for b in batches], dtype=object)
        missing = int(sum(v is None for v in ks.ravel()))
        entry: dict[str, Any] = {"missing": missing}
        if missing == 0:
            entry["log_k"] = anova_two_way(np.log(ks.astype(np.float64)))
            den = np.array([[derived[f"{b}|s{s}"][f"stage_denominator_{h:g}"] for s in starts] for b in batches])
            entry["stage_denominator"] = {"mean": float(den.mean()), "sd": float(den.std(ddof=1)), "anova": anova_two_way(den)}
        stages[f"{h:g}"] = entry
    k5 = [derived[f"{b}|s{s}"]["k_5"] for b in batches for s in starts]
    edges = list(range(0, 330, 10))
    stages["histogram_k5"] = {"bin_edges": edges, "counts": np.histogram([k for k in k5 if k is not None], bins=edges)[0].tolist(),
                              "missing": int(sum(k is None for k in k5))}
    out["stages"] = stages

    cells = {}
    for b in batches:
        j = int(b[1:])
        trio = [a1[(b, j)]["record"]] + [a2[(b, r0)]["record"] for r0 in ("1", "2") if a2.get((b, r0)) is not None]
        cells[b] = trio
    path: dict[str, Any] = {}
    for n in P.BUDGETS:
        pv = pooled_variance([[U(r, n) for r in trio] for trio in cells.values()])
        s2int = comps[str(n)]["sigma2_int"]
        path[str(n)] = {"sigma2_path": pv["pooled"], "df": pv["df"], "per_cell": pv["per_group"], "sigma2_int": s2int,
                        "pairing_net_of_path_noise": max(0.0, s2int - pv["pooled"])}
    plats = {b: [float(np.mean(r[301:321])) - r[0] for r in trio] for b, trio in cells.items()}
    pvp = pooled_variance(list(plats.values()))
    path["plateau"] = {"sigma2_path": pvp["pooled"], "df": pvp["df"], "per_cell": pvp["per_group"],
                       "sigma2_int": out["variance_components"]["plateau"]["sigma2_int"],
                       "pairing_net_of_path_noise": max(0.0, out["variance_components"]["plateau"]["sigma2_int"] - pvp["pooled"])}
    for h in P.STAGES:
        groups = []
        for trio in cells.values():
            ks = [P.crossing(r, h)["k"] for r in trio]
            if all(k is not None for k in ks):
                groups.append([math.log(k) for k in ks])
        pv = pooled_variance(groups) if groups else {"pooled": None, "df": 0, "per_group": []}
        path[f"log_k_{h:g}"] = {"sigma2_path": pv["pooled"], "df": pv["df"], "cells_complete": len(groups),
                                "sigma2_int": stages[f"{h:g}"].get("log_k", {}).get("sigma2_int")}
    path["plateau_range_per_cell"] = {b: [float(min(np.mean(r[301:321]) for r in trio)), float(max(np.mean(r[301:321]) for r in trio))]
                                      for b, trio in cells.items()}
    out["path_noise"] = path

    out["design_table"] = {"rows": design_table(comps), "rule": "cheapest design with w40 <= 0.25 and w80 <= 0.25; n_s >= 5 where the start "
                           "floor binds (sigma2_c > 0.1 x 2 sigma2_int / K at any budget, with the candidate's own K); else the smallest w80 "
                           "under the PI's cap. Reported; the team applies the rule.",
                           "timings": {"seconds_per_step": SEC_PER_STEP, "seconds_per_pass": SEC_PER_PASS, "rates_per_B200_hour": list(RATES)}}

    sealed = data["sealed"]
    ratios = {}
    for tag in ("n20", "n40", "n80", "n160", "n320", "h2", "h5", "h10"):
        per_batch = []
        for b in batches:
            key = f"{b}|{tag}|shuffles"
            if key not in sealed:
                continue
            sh = sealed[key].astype(np.float64)
            own = float(sealed[f"{b}|{tag}|own"][0])
            per_batch.append((np.std(sh, ddof=1) / math.sqrt(sh.size)) / abs(own - sh.mean()))
        ratios[tag] = {"median_over_batches": float(np.median(per_batch)) if per_batch else None, "batches": len(per_batch)}
    out["shuffle_noise_ratio"] = {"ratios": ratios, "rule": "keep 8 shuffles if the median is at most 0.1 at every budget and stage, else 16",
                                  "sealed": "only the ratio is reported; D and the shuffled means are not"}

    k0 = {k: v["KL0"] for k, v in derived.items() if "perturb" not in k}
    a20 = {k: v["added_20"] for k, v in derived.items() if "perturb" not in k}
    out["starting_harm"] = {"KL0": k0, "added_20": a20, "smallest_KL0": min(k0.values()), "smallest_added_20": min(a20.values())}
    out["cycling_share"] = {str(n): float(np.mean([derived[f"{b}|s{s}"][f"cycling_{n}"] for b in batches for s in starts])) for n in P.BUDGETS}
    return out


def main() -> None:
    out = tables(load())
    with open(PART_A / "tables.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {PART_A / 'tables.json'}")


if __name__ == "__main__":
    main()
