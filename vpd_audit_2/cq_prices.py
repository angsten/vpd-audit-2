"""Session 4, plan 6, Section 4, item 5, and plan 7, item 8: prices routed by pool (Riku's reviews).

Texts in Q (the deciding sets Q1 among them) are priced from the stored path (`QPrices`): the stored S row of `prices.Pricer`
and each label's Delta read from Q's full cache, the arrays the stored S was summed from, so the pruning stop rule and Pi
use identical numbers.

Texts outside Q (CQ; next session's re-test) are priced by `ExternalPricer`, exactly as a text of Q is, with their own
per-text sums S_i computed from their own label cache (the float32 fresh path, with z), the companions' sums X_ck from Q's
stored S and Q's committed W = 16, K = 256 tuples, and every tuple valid (no tuple contains a text outside Q). A Q text
that reaches the external path is refused with an error: its recomputed S_i need not equal the stored row bit for bit.

`Router` sends each text to its path by whether its id is in Q. Freed sets are passed as entry indices into the cache the
path reads Delta from (Q's full cache, or the outside text's own cache), so each label's change in its term is read from
the same cache as the sums it is compared with.

The nominal set (B1): on each CQ text, at each position in order, 10 percent of the labels above zero, rounded half up
(floor(0.1 n + 0.5)) with at least one when any exist, drawn without replacement by one generator seeded
(master, "pilot-nominal", text_id). Its saturated part is the nominal labels with z > 1; its unsaturated part the rest.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from vpd_audit_2 import prices as P


class QTextOnExternalPath(ValueError):
    """A text in Q reached the external path; Q texts are priced from the stored path (plan 7, item 8)."""


class ExternalPricer:
    """Prices a text outside Q, given by its own S_i (float64 vector over components), against Q's sums and tuples, every
    tuple valid. `q_text_ids` are Q's text ids in the stored S's row order; a Q text id is refused."""

    def __init__(self, S_Q: np.ndarray, tuples: np.ndarray, C: P.Constants, q_text_ids: list[str], device: str = "cpu", W: int = P.W_RUN):
        assert len(q_text_ids) == S_Q.shape[0], "q_text_ids must list Q's texts in the stored S's row order"
        self.inner = P.Pricer(S_Q, tuples, W, C, device)
        self.torch = self.inner.torch
        self.q_text_ids = frozenset(q_text_ids)

    def refuse_q(self, text_id: str) -> None:
        if text_id in self.q_text_ids:
            raise QTextOnExternalPath(f"{text_id} is in Q: price it from the stored path (QPrices), not the external path")

    def _expect(self, S_i: np.ndarray, comp: np.ndarray, q: np.ndarray) -> Any:
        torch = self.torch
        dev = self.inner.device
        c = torch.from_numpy(np.asarray(comp, dtype=np.int64)).to(dev)
        s_own = torch.from_numpy(np.asarray(S_i, dtype=np.float64)).to(dev)[c]
        X = self.inner.X[c][:, torch.ones(self.inner.K, dtype=torch.bool, device=dev)]  # every tuple valid (as the pilot ran)
        s = s_own[:, None] + X
        qq = torch.from_numpy(np.asarray(q, dtype=np.float64)).to(dev)
        d = P.f_w(s, self.inner.W, self.inner.C.beta) - P.f_w(s - qq[:, None], self.inner.W, self.inner.C.beta)
        return self.inner.C.lam * d.mean(dim=1)

    def price_labels(self, S_i: np.ndarray, comp: np.ndarray, delta: np.ndarray, *, text_id: str) -> np.ndarray:
        """Each label's own price (Riku's rule 3), every other label at its value."""
        self.refuse_q(text_id)
        return self._expect(S_i, comp, delta).cpu().numpy() if np.asarray(comp).size else np.zeros(0)

    def saved_price_T(self, S_i: np.ndarray, comp: np.ndarray, delta: np.ndarray, *, text_id: str) -> float:
        """T_i for a set of the text's labels freed together."""
        self.refuse_q(text_id)
        comp = np.asarray(comp, dtype=np.int64)
        if comp.size == 0:
            return 0.0
        uc, inv = np.unique(comp, return_inverse=True)
        q = np.bincount(inv, weights=np.asarray(delta, dtype=np.float64))
        return float(self._expect(S_i, uc, q).sum())


class QPrices:
    """The stored path for texts in Q: `prices.Pricer` on the stored S, with each label's Delta read from Q's full cache
    (`prices.entries` over the whole cache, the arrays the stored S was summed from). Freed sets are global entry indices
    into Q's cache, each inside its text's range."""

    def __init__(self, S_Q: np.ndarray, tuples: np.ndarray, C: P.Constants, q_text_ids: list[str], q_cache: dict[str, np.ndarray],
                 q_meta: dict[str, Any], device: str = "cpu", W: int = P.W_RUN, ids_sha256: str | None = None):
        """`ids_sha256`, when given, is the SHA-256 of Q's token ids (int32, [n, 512]) in `q_text_ids`' order; it must equal
        the cache's `set_hash_ids_512`, which proves the cache's rows (and the stored S's) are those texts in that order."""
        assert len(q_text_ids) == S_Q.shape[0], "q_text_ids must list Q's texts in the stored S's row order"
        listed = q_meta.get("texts")
        if isinstance(listed, list):
            assert listed == list(q_text_ids), "Q's cache lists its texts in another order"
        elif listed is not None:  # Q's cache records "manifest pool Q: v0 to v1023"
            assert listed == f"manifest pool Q: {q_text_ids[0]} to {q_text_ids[-1]}", f"Q's cache records its texts as {listed!r}"
        if ids_sha256 is not None:
            assert q_meta["set_hash_ids_512"] == ids_sha256, "Q's cache rows are not the given texts in this order"
        self.pricer = P.Pricer(S_Q, tuples, W, C, device)
        self.index = {t: i for i, t in enumerate(q_text_ids)}
        self.e, check1 = P.entries(q_cache, q_meta, C)
        assert check1["passes"] and self.e.n_texts == len(q_text_ids)
        self.slices = P.text_slices(q_cache["indptr"], len(q_text_ids))

    def _rows(self, text_id: str, freed: np.ndarray) -> tuple[int, np.ndarray]:
        if text_id not in self.index:
            raise KeyError(f"{text_id} is not in Q; the stored path prices Q texts only")
        i = self.index[text_id]
        a, b = self.slices[i]
        idx = np.asarray(freed, dtype=np.int64)
        assert np.all((idx >= a) & (idx < b)), f"{text_id}: freed entries outside the text's range in Q's cache"
        return i, idx

    def saved_price_T(self, text_id: str, freed: np.ndarray) -> float:
        i, idx = self._rows(text_id, freed)
        return self.pricer.saved_price_T(i, self.e.comp[idx], self.e.delta[idx])

    def price_labels(self, text_id: str, entries: np.ndarray) -> np.ndarray:
        i, idx = self._rows(text_id, entries)
        return self.pricer.price_text(i, self.e.comp[idx], self.e.delta[idx])


class Router:
    """T_i by pool: a text in Q from the stored path, any other from the external path (plan 7, item 8). `own` is the
    outside text's (cache, meta, row) for the external path."""

    def __init__(self, q_text_ids: list[str], stored: QPrices | None = None, external: ExternalPricer | None = None, C: P.Constants | None = None):
        self.q_text_ids = frozenset(q_text_ids)
        self.stored, self.external, self.C = stored, external, C

    def path(self, text_id: str) -> str:
        return "stored" if text_id in self.q_text_ids else "external"

    def saved_price_T(self, text_id: str, freed: np.ndarray, own: tuple[dict[str, np.ndarray], dict[str, Any], int] | None = None) -> float:
        if self.path(text_id) == "stored":
            assert self.stored is not None, f"{text_id} is in Q and needs the stored path (QPrices)"
            return self.stored.saved_price_T(text_id, freed)
        assert self.external is not None and own is not None and self.C is not None, f"{text_id} needs the external path and its own cache"
        cache, meta, row = own
        return arm_T(self.external, cache, meta, row, {"f": freed}, self.C, text_id=text_id)["f"]


def text_cache(cache: dict[str, np.ndarray], i: int, seq_len: int = P.SEQ_LEN) -> tuple[dict[str, np.ndarray], int]:
    """The sub-cache of text i alone (its 512 positions), and the global entry index of its first entry."""
    a, b = int(cache["indptr"][i * seq_len]), int(cache["indptr"][(i + 1) * seq_len])
    sub = {"indptr": cache["indptr"][i * seq_len : (i + 1) * seq_len + 1] - a}
    for k in ("indices", "values", "z"):
        sub[k] = cache[k][a:b]
    return sub, a


def text_sums(cache: dict[str, np.ndarray], meta: dict[str, Any], i: int, C: P.Constants) -> tuple[np.ndarray, P.Entries, int]:
    """S_i of text i from its own entries alone, with its Entries and global entry offset."""
    sub, a = text_cache(cache, i)
    e, check1 = P.entries(sub, meta, C)
    assert check1["passes"]
    return P.per_text_sums(e, C)[0], e, a


def nominal_set(cache: dict[str, np.ndarray], i: int, text_id: str, seq_len: int = P.SEQ_LEN) -> dict[str, np.ndarray]:
    """The nominal set of text i as global entry indices into the cache, with its saturated and unsaturated parts."""
    from vpd_audit_2.manifest import seed_of

    rng = np.random.default_rng(seed_of("pilot-nominal", text_id))
    picked = []
    for t in range(seq_len):
        a, b = int(cache["indptr"][i * seq_len + t]), int(cache["indptr"][i * seq_len + t + 1])
        n = b - a
        if n == 0:
            continue
        m = max(1, int(np.floor(0.1 * n + 0.5)))
        picked.append(a + np.sort(rng.choice(n, size=m, replace=False)))
    nom = np.concatenate(picked).astype(np.int64) if picked else np.zeros(0, np.int64)
    sat = cache["z"][nom] > 1
    return {"nominal": nom, "saturated": nom[sat], "unsaturated": nom[~sat]}


def arm_T(pricer: ExternalPricer, cache: dict[str, np.ndarray], meta: dict[str, Any], i: int, arms: dict[str, np.ndarray],
          C: P.Constants, *, text_id: str) -> dict[str, float]:
    """T_i for each arm's freed entries (global entry indices into the outside text's own cache), each arm alone."""
    pricer.refuse_q(text_id)
    S_i, e, a = text_sums(cache, meta, i, C)
    out = {}
    for name, idx in arms.items():
        local = np.asarray(idx, dtype=np.int64) - a
        assert np.all((local >= 0) & (local < e.comp.size)), f"{name}: entries outside text {i}"
        out[name] = pricer.saved_price_T(S_i, e.comp[local], e.delta[local], text_id=text_id)
    return out
