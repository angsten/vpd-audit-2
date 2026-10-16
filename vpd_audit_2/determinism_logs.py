"""Plan 5 of the research log, item 1: did any determinism warning fire in the runs recorded before deterministic algorithms were
made strict? Those runs set `torch.use_deterministic_algorithms(True, warn_only=True)`, under which an operation with no
deterministic implementation prints a UserWarning ("... does not have a deterministic implementation, but you set
'torch.use_deterministic_algorithms(True, warn_only=True)'") to the container's stderr, which Modal keeps in the app's log.

    uv run python -m vpd_audit_2.determinism_logs      (writes results/s4_plan5/determinism_logs.json)

For each of the Modal apps it fetches `modal app logs <app id>`, checks that the log is the run named (by a
line only that run prints, where it prints one), and counts determinism warnings and warnings of any kind. A probe app
(`ap-pk94FyyIFTq6OiPVioEB0X`, a scratch script outside the repository) triggered one such warning on purpose with
`torch.histc` on a CUDA tensor; its log is checked too, as the positive control that the warning reaches the log.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from vpd_audit_2 import env

PATTERN = "does not have a deterministic implementation"
RUNS: list[dict[str, Any]] = [
    {"app": "ap-GVsHBwgpR0y5VY3Ujhk9tY", "run": "prices --stage inputs", "results": ["s4_plan1_prices/price_inputs.json"], "marker": "[prices] bf16 pass"},
    {"app": "ap-7ZxpAgC0VLIV13b4lXMWaX", "run": "prices --stage prices", "results": ["s4_plan1_prices/prices.json"], "marker": "[prices] Q_fp32"},
    {"app": "ap-6fRfwOPYMOfl8LqFewo7XU", "run": "check7_diagnostic", "results": ["s4_plan1_prices/check7_diagnostic.json"], "marker": None},
    {"app": "ap-LiKm6cNUbuYt8KrAHJYDcH", "run": "check7_amended", "results": ["s4_plan1_prices/check7_amended.json"], "marker": None},
    {"app": "ap-tXip4Eu4Wmt0o7JvrNLz8m", "run": "g3", "results": ["s4_plan1_g3/g3.json"], "marker": "[g3] all_on"},
    {"app": "ap-MoeDszy67M9EdldbA9nEii", "run": "g2", "results": ["s4_plan1_g2/g2.json"], "marker": "[g2] step 0"},
    {"app": "ap-zx9PavnAoHEYP5m4pZ2D2S", "run": "recorded", "results": ["s4_plan1_g2/recorded_320.json"], "marker": "[recorded]"},
    {"app": "ap-b5YUL8GwY8YtcTup4bMvHS", "run": "g3_float64", "results": ["s4_plan1_g3/g3_float64_diagnostic.json"], "marker": "[g3-f64]"},
    {"app": "ap-avrdqSLc58CbAHoqsuFZBn", "run": "diagnose --stage d1", "results": ["s4_plan4/d1.json"], "marker": "[d1]"},
    {"app": "ap-bjr0iC5RgW45PnlwhuaPbl", "run": "diagnose --stage d5", "results": ["s4_plan4/d5.json"], "marker": "[d5]"},
    {"app": "ap-W306RULBuY5Dek6q1j5wCY", "run": "diagnose --stage d234", "results": ["s4_plan4/d2.json", "s4_plan4/d3.json", "s4_plan4/d4.json"], "marker": "[diag] D4|perm8"},
    {"app": "ap-LO3tnGQJPgBjaCnGAIANVc", "run": "diagnose --stage d4void", "results": ["s4_plan4/d4_void_case.json"], "marker": "[diag] D4void"},
]
PROBE = {"app": "ap-pk94FyyIFTq6OiPVioEB0X", "run": "positive control: torch.histc on CUDA under warn_only=True", "marker": "[warncheck]"}


def fetch(app: str, timeout: int = 180) -> str:
    p = subprocess.Popen(["modal", "app", "logs", app], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
    return out


def check(entry: dict[str, Any]) -> dict[str, Any]:
    log = fetch(entry["app"])
    lines = log.splitlines()
    return {**entry, "log_lines": len(lines), "log_complete": any("Stopping app" in x or "entrypoint completed" in x for x in lines),
            "marker_found": None if entry["marker"] is None else any(entry["marker"] in x for x in lines),
            "determinism_warnings": sum(PATTERN in x for x in lines), "warning_lines_of_any_kind": sum("Warning" in x for x in lines)}


def main() -> None:
    out_dir = env.REPO_ROOT / "results" / "s4_plan5"
    out_dir.mkdir(parents=True, exist_ok=True)
    runs = [check(e) for e in RUNS]
    probe = check(PROBE)
    res = {"pattern": PATTERN, "runs": runs, "positive_control": probe,
           "any_determinism_warning_in_the_runs": any(r["determinism_warnings"] for r in runs),
           "every_log_complete_and_identified": all(r["log_complete"] and r["marker_found"] is not False for r in runs),
           "positive_control_warning_seen": probe["determinism_warnings"] > 0}
    with open(out_dir / "determinism_logs.json", "w") as f:
        json.dump(res, f, indent=1)
    for r in runs:
        print(f"{r['app']}  {r['run']:<26} lines {r['log_lines']:>3}  complete {r['log_complete']}  marker {r['marker_found']}  "
              f"determinism warnings {r['determinism_warnings']}  any warnings {r['warning_lines_of_any_kind']}")
    print(f"probe: determinism warnings {probe['determinism_warnings']}")
    print(f"any determinism warning in the runs: {res['any_determinism_warning_in_the_runs']}; logs complete and identified: "
          f"{res['every_log_complete_and_identified']}; positive control seen: {res['positive_control_warning_seen']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
