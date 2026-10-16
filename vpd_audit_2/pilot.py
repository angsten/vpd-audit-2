"""Plan 6 of the research log: the pilot's shared pieces (plan 6 of the research log, Section 4).

  - Item 1, the extended starts: starts 1 to 64 by the manifest's keyed scheme (seed (master, "start", s); U[0, 1) on the
    CPU in float32, one torch generator per start, module by module in the manifest's layout, shape [1, 1, C_l + 1]);
    1 to 16 equal the committed `data/manifest/starts.npz`.
  - Item 2, the stage crossings read from a harm record: the first k >= 1 with m_k = (KL(k) + KL(k - 1)) / 2 >= h.
  - Item 4, the frequency strata and the stratified shuffle. Strata, per matrix: among the alive components (mean label
    over Q's positions above 1e-6), ten equal-count deciles of how often the label is above zero on Q (the fresh float32
    cache), by rank, ties broken by component index; the dead components (mean label at most 1e-6) are stratum 10. A
    shuffle permutes a source's rank-one entries within each stratum of each matrix, with one generator seeded
    (master, "pilot-shuffle", batch, start, tag, r), matrices in the layout's order and strata in ascending order; the 24
    delta entries stay in place.
  - Section 3, no carry-over: `score_own` scores a source only on the batch it was searched on, and asserts it.

Source layout: the manifest's `layout`, [(module, C_l)] in `model.target_module_paths` order; a flattened source holds
C_l + 1 entries per module, the delta entry last.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env

BUDGETS = (20, 40, 80, 160, 320)
STAGES = (2.0, 5.0, 10.0)
STAGES_A4 = (1.0, 2.0, 5.0, 10.0)
PILOT_BATCHES = tuple(f"C{j}" for j in range(1, 9))
PILOT_STARTS = tuple(range(1, 9))
N_STARTS_EXT = 64
DEAD_MEAN_LABEL = 1e-6
DEAD_STRATUM = 10
STARTS_DIR = env.REPO_ROOT / "results" / "s4_pilot" / "starts"


def layout() -> list[tuple[str, int]]:
    from vpd_audit_2.manifest import OUT_DIR

    man = json.load(open(OUT_DIR / "manifest.json"))
    return [(k, int(c)) for k, c in man["draws"]["adversary_starts"]["layout"]]


# ----------------------------------------------------------------------------- item 1: the extended starts


def make_extended_starts(n: int = N_STARTS_EXT) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """The manifest's `make_starts` scheme for s = 1..n."""
    import torch

    from vpd_audit_2.manifest import MASTER, seed_of

    lay = layout()
    arrays: dict[str, np.ndarray] = {}
    meta: dict[str, Any] = {"layout": lay, "shape_per_module": "[1, 1, C_l + 1], delta entry last",
                            "generator": "torch.Generator('cpu').manual_seed(seed); torch.rand(shape, generator, dtype=float32) per module in order",
                            "entries_per_start": sum(c + 1 for _, c in lay), "starts": {},
                            "allocation": {"1-8": "gates and pilot", "9-24": "question 2's deciding runs", "25-40": "question 1's freed-label test",
                                           "41-48": "the rerun of the first post's comparison", "49-64": "reserve, by recorded amendment only"}}
    for s in range(1, n + 1):
        g = torch.Generator(device="cpu")
        g.manual_seed(seed_of("start", s))
        parts = []
        for name, c in lay:
            x = torch.rand((1, 1, c + 1), generator=g, dtype=torch.float32).numpy()
            arrays[f"s{s}|{name}"] = x
            parts.append(x.tobytes())
        meta["starts"][str(s)] = {"seed_key": [MASTER, "start", s], "seed": seed_of("start", s), "sha256": hashlib.sha256(b"".join(parts)).hexdigest()}
    return arrays, meta


def write_extended_starts(out_dir: Path = STARTS_DIR) -> dict[str, str]:
    from vpd_audit_2.manifest import deterministic_npz

    arrays, meta = make_extended_starts()
    out_dir.mkdir(parents=True, exist_ok=True)
    npz = deterministic_npz(arrays)
    (out_dir / "starts_1_64.npz").write_bytes(npz)
    js = (json.dumps(meta, indent=1, sort_keys=True) + "\n").encode()
    (out_dir / "starts_1_64.json").write_bytes(js)
    sums = {n: hashlib.sha256((out_dir / n).read_bytes()).hexdigest() for n in ("starts_1_64.npz", "starts_1_64.json")}
    (out_dir / "SHA256SUMS").write_text("".join(f"{h}  {n}\n" for n, h in sums.items()))
    return sums


def load_extended_start(s: int, out_dir: Path = STARTS_DIR) -> dict[str, np.ndarray]:
    meta = json.load(open(out_dir / "starts_1_64.json"))
    lay = meta["layout"]
    with np.load(out_dir / "starts_1_64.npz") as z:
        start = {name: z[f"s{s}|{name}"] for name, _ in lay}
    got = hashlib.sha256(b"".join(start[name].tobytes() for name, _ in lay)).hexdigest()
    assert got == meta["starts"][str(s)]["sha256"], f"start {s}: hash mismatch"
    return start


# ----------------------------------------------------------------------------- item 2: stage crossings


def crossing(record: list[float], h: float) -> dict[str, Any]:
    """The first k >= 1 with m_k = (KL(k) + KL(k - 1)) / 2 >= h, with KL(k) and m_k; or missing."""
    for k in range(1, len(record)):
        m = 0.5 * (record[k] + record[k - 1])
        if m >= h:
            return {"k": k, "KL_k": record[k], "m_k": m, "missing": False}
    return {"k": None, "KL_k": None, "m_k": None, "missing": True}


# ----------------------------------------------------------------------------- item 4: strata and shuffles


def strata_from_cache(cache: dict[str, np.ndarray], meta: dict[str, Any]) -> dict[str, Any]:
    """Per component in the cache's global index (sorted module order): the frequency of a label above zero over Q's
    positions, the mean label, and the stratum (0 to 9 the alive deciles of frequency within the matrix, 10 dead)."""
    n_pos = int(cache["indptr"].size - 1)
    n_sub = int(meta["n_subcomponents"])
    comp = cache["indices"].astype(np.int64)
    freq = np.bincount(comp, minlength=n_sub) / n_pos
    mean_label = np.bincount(comp, weights=cache["values"].astype(np.float64), minlength=n_sub) / n_pos
    stratum = np.full(n_sub, DEAD_STRATUM, dtype=np.int64)
    for k in meta["module_order"]:
        o, C = int(meta["module_offsets"][k]), int(meta["module_to_c"][k])
        alive = np.flatnonzero(mean_label[o : o + C] > DEAD_MEAN_LABEL)
        order = alive[np.lexsort((alive, freq[o + alive]))]  # by frequency, ties by component index
        n = order.size
        stratum[o + order] = (10 * np.arange(n)) // n
    return {"freq": freq, "mean_label": mean_label, "stratum": stratum, "n_positions": n_pos,
            "definition": "per matrix: alive (mean label > 1e-6) components in ten equal-count deciles of label-above-zero frequency on Q "
                          "by rank, ties by component index (0 = least frequent); dead components stratum 10"}


def strata_by_module(stratum_global: np.ndarray, meta: dict[str, Any], lay: list[tuple[str, int]]) -> dict[str, np.ndarray]:
    """The strata in the source layout: per module (layout order), the stratum of each of its C_l components."""
    out = {}
    for k, C in lay:
        o = int(meta["module_offsets"][k])
        assert int(meta["module_to_c"][k]) == C
        out[k] = stratum_global[o : o + C].copy()
    return out


def shuffle_source(flat: np.ndarray, lay: list[tuple[str, int]], strata: dict[str, np.ndarray], key: tuple[Any, ...],
                   label: str = "pilot-shuffle") -> np.ndarray:
    """A frequency-stratified shuffle of one flattened source; `key` = (batch, start, tag, r) after "pilot-shuffle".
    The lead run passes a seed label of its own (plan 2 of the research log, Section 5.1); the pilot's seeds are unchanged."""
    from vpd_audit_2.manifest import seed_of

    rng = np.random.default_rng(seed_of(label, *key))
    out = flat.copy()
    off = 0
    for k, C in lay:
        block = flat[off : off + C]
        new = block.copy()
        st = strata[k]
        for v in np.unique(st):
            idx = np.flatnonzero(st == v)
            new[idx] = block[idx[rng.permutation(idx.size)]]
        out[off : off + C] = new  # the delta entry, at off + C, is left in place
        off += C + 1
    assert off == flat.size
    return out


def unflatten(flat: np.ndarray, lay: list[tuple[str, int]]) -> dict[str, np.ndarray]:
    out, off = {}, 0
    for k, C in lay:
        out[k] = flat[off : off + C + 1].reshape(1, 1, C + 1).astype(np.float32).copy()
        off += C + 1
    return out


# ----------------------------------------------------------------------------- Section 3: no carry-over


def score_own(model: Any, source: dict[str, np.ndarray], prep: Any, source_batch: str, prep_batch: str, device: str = "cuda") -> float:
    """Pilot mode: a source is scored only on the batch it was searched on."""
    from vpd_audit_2 import adversary as A

    assert source_batch == prep_batch, f"carry-over is not allowed in the pilot: a source from {source_batch} scored on {prep_batch}"
    return A.score(model, source, prep, device=device)
