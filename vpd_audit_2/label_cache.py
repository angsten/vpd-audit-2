"""A sparse label cache (fresh_cache's layout) as dense label tensors and entry masks, for Part B's harnesses.

Question 1's labels are the cache's float32 values (plan 3 of the research log, decision 7; plan 6 of the research log, Section 6). The harnesses take their
labels from here, never by recomputing them on another batch, so a freed set given as cache entry indices zeroes exactly
the labels its prices were computed from. Dense tensors follow the cache's module order (sorted), which is the order of the
labels dict the CI function returns and in which the stochastic draws are made.
"""

from __future__ import annotations

from typing import Any

import numpy as np


class LabelCache:
    def __init__(self, cache: dict[str, np.ndarray], meta: dict[str, Any], seq_len: int):
        self.c, self.meta, self.T = cache, meta, seq_len
        self.order = list(meta["module_order"])
        self.offsets = {k: int(v) for k, v in meta["module_offsets"].items()}
        self.m2c = {k: int(v) for k, v in meta["module_to_c"].items()}
        self.n_pos = int(cache["indptr"].size - 1)
        self.bounds = np.array([self.offsets[k] for k in self.order] + [sum(self.m2c.values())])
        self.pos_of_entry = np.repeat(np.arange(self.n_pos, dtype=np.int64), np.diff(cache["indptr"]))

    @property
    def n_texts(self) -> int:
        return self.n_pos // self.T

    def locate(self, entries: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """(text, position, module index in order, component within module) of each entry."""
        entries = np.asarray(entries, dtype=np.int64)
        pos = self.pos_of_entry[entries]
        comp = self.c["indices"][entries].astype(np.int64)
        li = np.searchsorted(self.bounds, comp, side="right") - 1
        return pos // self.T, pos % self.T, li, comp - self.bounds[li]

    def dense(self, texts: list[int], device: str, dtype: Any = None) -> dict[str, Any]:
        """Dense labels [len(texts), T, C_l] per module, zero where no label is stored."""
        import torch

        out = {k: torch.zeros((len(texts), self.T, self.m2c[k]), dtype=torch.float32) for k in self.order}
        for r, i in enumerate(texts):
            a, b = int(self.c["indptr"][i * self.T]), int(self.c["indptr"][(i + 1) * self.T])
            idx = np.arange(a, b)
            _, t, li, cl = self.locate(idx)
            vals = torch.from_numpy(self.c["values"][a:b])
            for j, k in enumerate(self.order):
                m = li == j
                if m.any():
                    out[k][r, torch.from_numpy(t[m]), torch.from_numpy(cl[m])] = vals[torch.from_numpy(m)]
        return {k: v.to(device=device, dtype=dtype or torch.float32) for k, v in out.items()}

    def mask(self, texts: list[int], entries: np.ndarray, device: str) -> dict[str, Any]:
        """Boolean masks [len(texts), T, C_l] marking the given entries (which must lie in these texts)."""
        import torch

        row = {i: r for r, i in enumerate(texts)}
        out = {k: torch.zeros((len(texts), self.T, self.m2c[k]), dtype=torch.bool) for k in self.order}
        tx, t, li, cl = self.locate(entries)
        for e in range(len(tx)):
            out[self.order[li[e]]][row[int(tx[e])], int(t[e]), int(cl[e])] = True
        return {k: v.to(device) for k, v in out.items()}

    def freed(self, labels: dict[str, Any], fmask: dict[str, Any]) -> dict[str, Any]:
        """The labels with the masked entries set to zero (the override G2 checks)."""
        return {k: labels[k].masked_fill(fmask[k], 0.0) for k in labels}


def cache_from_dense(labels: dict[str, Any], z: dict[str, Any] | None = None) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """A sparse cache from dense labels [n, T, C_l] in the dict's (sorted) order: for tests on the tiny model."""
    import torch

    from vpd_audit.donors import module_offsets

    order = sorted(labels)
    n, T = labels[order[0]].shape[:2]
    m2c = {k: int(labels[k].shape[-1]) for k in order}
    L = torch.cat([labels[k].reshape(n * T, -1) for k in order], dim=1).cpu()
    Z = torch.cat([z[k].reshape(n * T, -1) for k in order], dim=1).cpu() if z is not None else L
    pos = L > 0
    idx = torch.nonzero(pos)
    cache = {"indptr": np.concatenate([[0], np.cumsum(pos.sum(1).numpy())]).astype(np.int64), "indices": idx[:, 1].numpy().astype(np.uint16),
             "values": L[idx[:, 0], idx[:, 1]].numpy().astype(np.float32), "z": Z[idx[:, 0], idx[:, 1]].numpy().astype(np.float32)}
    meta = {"module_order": order, "module_offsets": module_offsets(m2c), "module_to_c": m2c, "n_subcomponents": sum(m2c.values()),
            "n_positions": n * T}
    return cache, meta
