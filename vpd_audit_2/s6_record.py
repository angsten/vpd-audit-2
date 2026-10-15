"""Session 6, plan 2: the one machine-readable record of the follow-up analyses, `results/s6_followups/record.json`.
Each reading script writes its own section and leaves the others as they are."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vpd_audit_2 import env

RECORD = env.REPO_ROOT / "results" / "s6_followups" / "record.json"


def update(section: str, data: Any, path: Path | None = None) -> None:
    path = RECORD if path is None else Path(path)
    record = json.loads(path.read_text()) if path.is_file() else {}
    record[section] = data
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
