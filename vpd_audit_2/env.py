"""Cache paths for this repository. Import this module before anything from `vpd_audit` or `param_decomp`.

`vpd_audit.env` takes its project root to be the folder above its package, so by default it would put
its cache in `third_party/vpd-audit/.cache/`, inside the submodule. This module sets
`VPD_AUDIT_CACHE_DIR` explicitly before `vpd_audit.env` is imported:

- locally, to `<this repository>/.cache/` (ignored by git);
- on Modal, to the volume mount `/cache`, which the image passes in as `VPD_AUDIT_2_CACHE_DIR`.

Any other value already in the environment is overwritten, not honoured. After the import it asserts that
`vpd_audit.env` resolved the same directory, so a cache can never land inside the submodule silently.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
THIRD_PARTY: Path = REPO_ROOT / "third_party"
VPD_AUDIT_DIR: Path = THIRD_PARTY / "vpd-audit"
PARAM_DECOMP_DIR: Path = VPD_AUDIT_DIR / "third_party" / "param-decomp"
PROVENANCE_DIR: Path = REPO_ROOT / "provenance"

VPD_AUDIT_COMMIT = "b6d3bac16ae4d1cfa7a6a46fcaf446059c2c8291"
PARAM_DECOMP_COMMIT = "74146b555f3eb3cd2bc639c3789fd3b7a099094a"

CACHE_DIR: Path = Path(os.environ.get("VPD_AUDIT_2_CACHE_DIR", str(REPO_ROOT / ".cache"))).resolve()

if "vpd_audit.env" in sys.modules:
    _already = Path(sys.modules["vpd_audit.env"].CACHE_DIR).resolve()
    assert _already == CACHE_DIR, (
        f"vpd_audit.env was imported before vpd_audit_2.env and resolved its cache to {_already}, not {CACHE_DIR}"
    )

os.environ["VPD_AUDIT_CACHE_DIR"] = str(CACHE_DIR)
os.environ["PARAM_DECOMP_OUT_DIR"] = str(CACHE_DIR / "out")
os.environ["HF_HOME"] = str(CACHE_DIR / "hf")

from vpd_audit import env as _vpd_env  # noqa: E402  (must follow the variables above)

assert Path(_vpd_env.CACHE_DIR).resolve() == CACHE_DIR, (_vpd_env.CACHE_DIR, CACHE_DIR)
assert not Path(_vpd_env.CACHE_DIR).resolve().is_relative_to(VPD_AUDIT_DIR.resolve()), "the cache must not lie inside the submodule"

ARTIFACTS_DIR: Path = _vpd_env.ARTIFACTS_DIR
SETS_DIR: Path = _vpd_env.SETS_DIR
HF_DIR: Path = _vpd_env.HF_DIR
