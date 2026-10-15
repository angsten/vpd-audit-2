"""Plan 2, section 8.3 and 8.4: gate G1's readings, recomputed from the committed trajectories alone.

    uv run python -m vpd_audit_2.g1_readings [results/plan2_g1/trajectories.json]

Inputs: `results/plan2_g1/trajectories.json` (every run's harm after every step) and the released run's logged 20-step
values (`provenance/runs/s-55ea3f9b/loss_history.csv`). Output: `results/plan2_g1/readings.json`, and a printed table.

Conventions (section 8.2): entry k of a run's record is the harm after k updates; A_c's harm at n steps is entry n of its
320-step run; A_s's harm at n is the last entry of its n-step run; at 20 steps the two candidates are the same search
(2/20 = 0.1), so A_s at 20 is A_c's entry 20.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from vpd_audit_2 import env

BUDGETS = (20, 40, 80, 160, 320)
PAPER = {20: 0.8280, 40: 1.3539, 80: 3.8381, 160: 25.2560, 320: 40.2200}  # paper lines 395-399
LOGGED_ANCHOR = 0.6522506475448608  # s-55ea3f9b summary: eval/loss/PGDReconLoss at step 400,000 (the plan's 0.6523)
LN125 = math.log(1.25)
OUT_DIR = env.REPO_ROOT / "results" / "plan2_g1"


def harm(runs: dict[str, Any], candidate: str, batch: str, n: int) -> float:
    if candidate == "A_c" or n == 20:
        return runs[f"A_c|{batch}|320"]["record"][n]
    return runs[f"A_s|{batch}|{n}"]["record"][-1]


def check_a_anchor(anchor_runs: list[float]) -> dict[str, Any]:
    y = np.log(np.asarray(anchor_runs))
    k = y.size
    t = stats.t.ppf(0.995, k - 1)
    half = max(t * y.std(ddof=1) * math.sqrt(1 + 1 / k), LN125)
    gap = abs(math.log(LOGGED_ANCHOR) - y.mean())
    return {"form": "preferred: the step-400,000 evaluation batch", "harms": anchor_runs, "mean_log": float(y.mean()), "sd_log": float(y.std(ddof=1)),
            "geometric_mean": float(math.exp(y.mean())), "logged": LOGGED_ANCHOR, "abs_log_gap": gap, "t_0.995": float(t),
            "prediction_half_width": float(t * y.std(ddof=1) * math.sqrt(1 + 1 / k)), "half_width_used": float(half), "passes": bool(gap <= half)}


def logged_late_20_step() -> list[float]:
    vals = []
    with open(env.PROVENANCE_DIR / "runs" / "s-55ea3f9b" / "loss_history.csv") as f:
        for r in csv.DictReader(f):
            if r["key"] == "eval/loss/PGDReconLoss" and 360000 <= int(r["step"]) <= 400000:
                vals.append(float(r["value"]))
    assert len(vals) == 41, len(vals)
    return vals


def check_a_distribution(ours: list[float]) -> dict[str, Any]:
    logged = np.log(logged_late_20_step())
    y = np.log(np.asarray(ours))
    d = y.mean() - logged.mean()
    v1, v2 = y.var(ddof=1) / y.size, logged.var(ddof=1) / logged.size
    df = (v1 + v2) ** 2 / (v1**2 / (y.size - 1) + v2**2 / (logged.size - 1))
    t = stats.t.ppf(0.975, df)
    lo, hi = d - t * math.sqrt(v1 + v2), d + t * math.sqrt(v1 + v2)
    within = abs(d) <= LN125
    return {"form": "otherwise: the logged late-training distribution (41 values, steps 360,000 to 400,000)",
            "logged_geometric_mean": float(math.exp(logged.mean())), "logged_log_sd": float(logged.std(ddof=1)),
            "ours_geometric_mean": float(math.exp(y.mean())), "ours_log_sd": float(y.std(ddof=1)), "ratio": float(math.exp(d)),
            "ratio_95pct_interval": [float(math.exp(lo)), float(math.exp(hi))], "interval": "Welch t on the difference of mean logs", "welch_df": float(df),
            "within_factor_1.25": bool(within), "interval_includes_1": bool(lo <= 0 <= hi), "passes": bool(within and lo <= 0 <= hi)}


def readings(traj: dict[str, Any]) -> dict[str, Any]:
    runs = traj["runs"]
    batches = traj["calibration_batches"]
    k = len(batches)
    out: dict[str, Any] = {"batches": batches, "k": k, "paper": PAPER}
    anchor = traj.get("check_a_anchor_harms")
    out["check_a"] = check_a_anchor(anchor) if anchor else check_a_distribution([harm(runs, "A_c", b, 20) for b in batches])
    t995 = stats.t.ppf(0.995, k - 1)
    t975 = stats.t.ppf(0.975, k - 1)
    table: dict[str, Any] = {}
    for cand in ("A_c", "A_s"):
        table[cand] = {}
        for n in BUDGETS:
            y = np.log([harm(runs, cand, b, n) for b in batches])
            half = t995 * y.std(ddof=1) * math.sqrt(1 + 1 / k)
            lo, hi = y.mean() - half, y.mean() + half
            table[cand][n] = {"harms": [float(math.exp(v)) for v in y], "mean_log": float(y.mean()), "sd_log": float(y.std(ddof=1)),
                              "interval_nats": [float(math.exp(lo)), float(math.exp(hi))], "paper": PAPER[n],
                              "consistent": bool(lo <= math.log(PAPER[n]) <= hi)}
        table[cand]["consistent_at_all_budgets"] = all(table[cand][n]["consistent"] for n in BUDGETS)
    out["intervals"] = table
    paired: dict[int, Any] = {}
    for n in BUDGETS[1:]:
        d = np.log([harm(runs, "A_c", b, n) for b in batches]) - np.log([harm(runs, "A_s", b, n) for b in batches])
        half = t975 * d.std(ddof=1) / math.sqrt(k)
        paired[n] = {"d": d.tolist(), "mean": float(d.mean()), "ci95": [float(d.mean() - half), float(d.mean() + half)],
                     "ratio_ci95": [float(math.exp(d.mean() - half)), float(math.exp(d.mean() + half))],
                     "within_ln_1.25": bool(-LN125 <= d.mean() - half and d.mean() + half <= LN125)}
    out["paired_differences"] = paired
    agree = all(paired[n]["within_ln_1.25"] for n in BUDGETS[1:])
    cons = {c: table[c]["consistent_at_all_budgets"] for c in ("A_c", "A_s")}
    fits20 = any(table[c][20]["consistent"] for c in ("A_c", "A_s"))
    out["schedules_agree"] = agree
    out["consistent"] = cons
    if not out["check_a"]["passes"]:
        decision = ("Check A fails", "stop and report; do not run the long budgets")
    elif agree and any(cons.values()):
        decision = ("schedules agree, at least one candidate consistent", "adopt A_c; G1 passes")
    elif sum(cons.values()) == 1:
        c = next(c for c, v in cons.items() if v)
        decision = (f"exactly one candidate consistent: {c}", f"adopt {c}; G1 passes")
    elif all(cons.values()):
        decision = ("both consistent, schedules not agreeing", "escalate once to C9 to C16 (k = 16); if still not settled, G1 ends 'run both'")
    elif fits20:
        decision = ("neither consistent, 20 steps fitting at least one", "G1 ends 'not reproduced'; report, do not stop the plan")
    else:
        decision = ("20 steps fits neither candidate", "stop and report")
    out["decision"] = {"result": decision[0], "next": decision[1]}
    return out


SPREAD_BATCHES = ("C1", "C2", "C3")
SPREAD_STARTS = tuple(range(1, 9))


def start_spread(traj: dict[str, Any]) -> dict[str, Any]:
    """The head's follow-up of 1 October: the 20-step spread due to the start. s_w is the pooled within-batch SD of log
    harm over starts 1 to 8 on C1, C2, and C3 (21 degrees of freedom); s_8 the SD over C1 to C8, one start each;
    s = max(s_8, s_w); the interval is ybar_8 +- t_{0.995,7} s sqrt(1 + 1/8)."""
    runs = traj["runs"]
    per: dict[str, Any] = {}
    ss, df = 0.0, 0
    for b in SPREAD_BATCHES:
        h = [runs[f"A_c|{b}|20|s{s}"]["record"][20] for s in SPREAD_STARTS]
        y = np.log(h)
        per[b] = {"harms": h, "mean_log": float(y.mean()), "geometric_mean": float(math.exp(y.mean())), "sd_log": float(y.std(ddof=1))}
        ss += float(((y - y.mean()) ** 2).sum())
        df += y.size - 1
    s_w = math.sqrt(ss / df)
    y8 = np.log([harm(runs, "A_c", f"C{j}", 20) for j in range(1, 9)])
    s_8 = float(y8.std(ddof=1))
    s = max(s_8, s_w)
    t = float(stats.t.ppf(0.995, 7))
    half = t * s * math.sqrt(1 + 1 / 8)
    lo, hi = y8.mean() - half, y8.mean() + half
    inside = bool(lo <= math.log(PAPER[20]) <= hi)
    dup = {f"{b}|s{j}": runs[f"A_c|{b}|20|s{j}"]["record"][20] == runs[f"A_c|{b}|320"]["record"][20] for j, b in enumerate(SPREAD_BATCHES, start=1)}
    return {"per_batch": per, "s_w_pooled": s_w, "s_w_df": df, "s_8": s_8, "s_used": s, "variance_ratio_s_w2_over_s_82": s_w**2 / s_8**2,
            "sd_ratio_s_w_over_s_8": s_w / s_8, "ybar_8": float(y8.mean()), "t_0.995_7": t, "half_width": half,
            "interval_nats": [math.exp(lo), math.exp(hi)], "paper_20_step": PAPER[20], "paper_inside": inside,
            "repeat_runs_equal_the_320_step_records_at_step_20": dup,
            "reading": ("constant step adopted; the paper's 20-step value lies within the released checkpoint's spread over batch and start" if inside
                        else "constant step adopted; the paper's 20-step level is not reproduced from the released checkpoint"),
            "a_c_consistent_at_all_five_budgets": inside}


def main(path: Path = OUT_DIR / "trajectories.json") -> dict[str, Any]:
    traj = json.load(open(path))
    out = readings(traj)
    with open(path.parent / "readings.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"Check A ({out['check_a']['form']}): passes {out['check_a']['passes']}")
    print(f"{'budget':>6} {'paper':>8}  {'A_c interval (nats)':>24} {'ok':>3}  {'A_s interval (nats)':>24} {'ok':>3}  {'A_c/A_s 95% CI':>18}")
    for n in BUDGETS:
        c, s = out["intervals"]["A_c"][n], out["intervals"]["A_s"][n]
        pr = out["paired_differences"].get(n)
        pd = f"[{pr['ratio_ci95'][0]:.3f}, {pr['ratio_ci95'][1]:.3f}]" if pr else "same search"
        print(f"{n:>6} {PAPER[n]:>8.4f}  [{c['interval_nats'][0]:>9.4f}, {c['interval_nats'][1]:>9.4f}] {'y' if c['consistent'] else 'n':>3}  "
              f"[{s['interval_nats'][0]:>9.4f}, {s['interval_nats'][1]:>9.4f}] {'y' if s['consistent'] else 'n':>3}  {pd:>18}")
    print(f"decision: {out['decision']}")
    return out


def main_spread(path: Path = OUT_DIR / "trajectories.json") -> dict[str, Any]:
    out = start_spread(json.load(open(path)))
    with open(path.parent / "start_spread.json", "w") as f:
        json.dump(out, f, indent=1)
    for b, v in out["per_batch"].items():
        print(f"{b}: harms {[round(h, 4) for h in v['harms']]}; sd_log {v['sd_log']:.4f}")
    print(f"s_w {out['s_w_pooled']:.4f} ({out['s_w_df']} df); s_8 {out['s_8']:.4f}; variance ratio {out['variance_ratio_s_w2_over_s_82']:.2f}; "
          f"interval {out['interval_nats'][0]:.4f} to {out['interval_nats'][1]:.4f}; 0.828 inside: {out['paper_inside']}")
    print(f"repeat runs equal: {out['repeat_runs_equal_the_320_step_records_at_step_20']}")
    print(f"reading: {out['reading']}")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    p = Path(args[0]) if args else OUT_DIR / "trajectories.json"
    main_spread(p) if "--start-spread" in sys.argv[1:] else main(p)
