"""Plan 2 of the research log: what the reading scripts share. The scored units, loaded by name from the local copy (refusing an
incomplete set and naming every unit missing), and the run's tables, each checked against its receipt."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR

PAPER_ALIVE = 9972  # the paper's count on its own data, from table `tab:num-components-per-layer` in its 'Target language model' section
STRATA_ALIVE = 9948  # the strata's count on the first post's 1,024 texts (results/s4_pilot/part_a/strata.npz)
ALIVE_LINE = ("Counts are set beside two alive counts: 9,972 is the paper's count on its own data; 9,948 is the strata's count on the "
              "first post's 1,024 texts.")


class Refusal(Exception):
    pass


class Units:
    """The scored units, by name; each a mapping of pass id to (harm, per-text harms, what was recorded)."""

    def __init__(self, folder: Path | None = None) -> None:
        self.folder = SR.LOCAL_UNITS if folder is None else Path(folder)
        self._cache: dict[str, dict[str, Any]] = {}

    def require(self, names: list[str]) -> None:
        missing = [n for n in names if not (self.folder / f"{n}.npz").is_file()]
        if missing:
            raise Refusal(f"{len(missing)} units missing: " + ", ".join(missing))

    def get(self, name: str) -> dict[str, Any]:
        if name not in self._cache:
            with np.load(self.folder / f"{name}.npz", allow_pickle=False) as z:
                ids = [str(x) for x in z["pass_ids"]]
                rec = SR.json_field(z, "recorded")
                self._cache[name] = {"passes": {p: (float(h), t, r) for p, h, t, r in zip(ids, z["harm"], z["per_text"], rec)},
                                     "meta": SR.json_field(z, "meta")}
        return self._cache[name]

    def harm(self, name: str, pass_id: str) -> float:
        return self.get(name)["passes"][pass_id][0]

    def recorded(self, name: str, pass_id: str) -> dict[str, Any]:
        return self.get(name)["passes"][pass_id][2]


def all_unit_names() -> list[str]:
    names = [u[0] for h in SR.HELDOUT for u in B.heldout_units(h, list(SR.ATTACK), list(SR.STARTS), "A1")]
    return names + [u[0] for a in SR.ATTACK for u in B.attack_units(a, list(SR.STARTS))]


def tables() -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        return SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT), SR.load_table_checked(SR.DELTA_TABLE, SR.DELTA_RECEIPT)
    except Exception as e:  # noqa: BLE001
        raise Refusal(f"the run's tables: {e}") from None


def row_index(table: dict[str, Any], row: str) -> int:
    return [str(x) for x in table["setting_names"]].index(row)


def f2(x: float | None) -> str:
    return "undefined" if x is None or not np.isfinite(x) else f"{x:.2f}"
