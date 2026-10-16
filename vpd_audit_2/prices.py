"""Plan 1 of the research log (the earlier plan 3 of the research log): label prices under per-process training.

Specification: the price specification (research log), with the decisions of the earlier plan 3 of the research log, Section 3,
and the amendments of the earlier plan 2 of the research log (check 3's rule, check 4's tie, check 7's rule, check 8's threshold).

Units. A label's price pi is in summed nats; the saved price Pi of a freed set is in nats per token.

The arithmetic, all in float64 (torch, on any device):
  - g_up = the authors' `upper_leaky_hard_sigmoid` applied to the stored pre-sigmoid value z (float32, as training
    computed it), then cast to float64;
  - S[i, c] = sum over text i's 512 positions of (g_up + eps)^p: the stored positive labels' terms plus
    (512 - n_pos) eps^p for the positions the sparse cache omits (label zero, so g_up = 0);
  - Delta = (g_up + eps)^p - eps^p, the drop in S when the label is set to zero;
  - f_W(s) = s + beta s log2(1 + W s), the same expression as the authors' `_importance_minimality_loss_compute`
    (`importance_minimality_loss.py:89-114`) times n;
  - the price pi = lambda E_X[f_W(S[i,c] + X_c) - f_W(S[i,c] + X_c - Delta)], X_c the sum of S over B_loc - 1
    companion texts, the expectation over the K stored companion tuples that do not contain text i;
  - the plug-in (description): X_c replaced by (B_loc - 1) times the mean of S[j, c] over the texts j != i;
  - the project plan's price (description, check 7): lambda Delta [1 + beta log2(1+s) + (beta/ln 2) s/(1+s)],
    s = 64 * mean_i S[i, c], with the eps floor and the uncapped g_up (plan 2 of the research log, item 2);
  - T_i, the saved price of a set of freed labels on text i, and Pi = sum_i T_i / (512 n_texts).

Companion tuples: drawn one tuple at a time with `numpy.random.default_rng(seed_of("price-companions", W))`, each
`rng.choice(n_texts, B_loc - 1, replace=False)`, so the first K tuples of a longer draw are the K-tuple set.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

SEQ_LEN = 512
N_TEXTS_BATCH = 64  # the training batch (run config batch_size)
W_RUN = 16  # confirmed by plan 2 of the research log's world-size test
K_DEFAULT = 256
LOGGED_EVAL_MINIMALITY = 1158.31591796875  # summary.json eval/loss/ImportanceMinimalityLoss, step 400,000
PLAN1_WHOLE_64 = 1092.94580078125  # results/plan1_smoke/smoke.json: rows 0 to 63, world size 1, bf16
PLAN1_PER_PROCESS_64 = 1123.8996772766113  # the same, 16 shares of 4 texts, world size 16
LOGGED_TRAIN_STEPS = tuple(range(398_200, 400_001, 200))  # the last 10 logged training values


@dataclass(frozen=True)
class Constants:
    lam: float
    beta: float
    eps: float
    p: float
    pnorm: float
    p_anneal_start_frac: float
    p_anneal_final_p: float
    p_anneal_end_frac: float


def constants() -> Constants:
    """lambda, beta, eps from the raw config (asserted by run_config at import); p from the authors' annealing at
    current_frac_of_training = 1.0, asserted to be 0.4 exactly."""
    from vpd_audit_2.run_config import loss_entry

    from param_decomp.metrics.importance_minimality_loss import _get_linear_annealed_p

    cfg = loss_entry("ImportanceMinimalityLoss")
    p = _get_linear_annealed_p(1.0, cfg["pnorm"], cfg["p_anneal_start_frac"], cfg["p_anneal_final_p"], cfg["p_anneal_end_frac"])
    assert p == 0.4, p
    return Constants(lam=float(cfg["coeff"]), beta=float(cfg["beta"]), eps=float(cfg["eps"]), p=float(p), pnorm=float(cfg["pnorm"]),
                     p_anneal_start_frac=float(cfg["p_anneal_start_frac"]), p_anneal_final_p=float(cfg["p_anneal_final_p"]),
                     p_anneal_end_frac=float(cfg["p_anneal_end_frac"]))


def f_w(s: Any, W: int, beta: float) -> Any:
    """f_W(s) = s + beta s log2(1 + W s), for a float64 torch tensor."""
    import torch

    return s + beta * s * torch.log2(1 + W * s)


def sha256_array(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


# ----------------------------------------------------------------------------- the cache


def load_cache(path: Path, keys: tuple[str, ...] = ("indptr", "indices", "values", "z")) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """A sparse label cache (fresh_cache's layout) and its manifest; each array loaded is checked against its SHA-256."""
    meta = json.load(open(path.with_suffix(".json")))
    out = {}
    with np.load(path) as zf:
        for k in keys:
            out[k] = zf[k]
            assert sha256_array(out[k]) == meta["sha256"][k], f"{path.name}: {k} hash mismatch"
    return out, meta


def upper_leaky(z: np.ndarray) -> np.ndarray:
    """The authors' upper-leaky output on float32 z, as a float32 array."""
    import torch

    from param_decomp.models.sigmoids import upper_leaky_hard_sigmoid

    assert z.dtype == np.float32
    return upper_leaky_hard_sigmoid(torch.from_numpy(z)).numpy()


@dataclass
class Entries:
    """Per stored entry (a label above zero): its text, component, label, z, g_up, Delta, and the saturation flag."""
    text: np.ndarray  # int64
    comp: np.ndarray  # int64, the global subcomponent index
    g: np.ndarray  # float32
    z: np.ndarray  # float32
    g_up: np.ndarray  # float32
    delta: np.ndarray  # float64
    term: np.ndarray  # float64: (g_up + eps)^p
    saturated: np.ndarray  # bool: z > 1
    n_texts: int
    n_sub: int


def entries(cache: dict[str, np.ndarray], meta: dict[str, Any], C: Constants) -> tuple[Entries, dict[str, Any]]:
    """Check 1 (exact): clamp(g_up, 0, 1) equals the stored label for every stored entry."""
    indptr, n_sub = cache["indptr"], int(meta["n_subcomponents"])
    n_pos = indptr.size - 1
    assert n_pos % SEQ_LEN == 0
    n_texts = n_pos // SEQ_LEN
    g, z = cache["values"], cache["z"]
    assert g.dtype == np.float32 and z.dtype == np.float32
    assert np.all(g > 0), "the cache holds labels above zero only"
    g_up = upper_leaky(z)
    clamped = np.clip(g_up, 0, 1)
    n_bad = int((clamped != g).sum())
    check1 = {"rule": "clamp(upper_leaky(z), 0, 1) equals the stored label exactly, for every stored entry", "entries": int(g.size),
              "entries_unequal": n_bad, "passes": n_bad == 0}
    pos = np.repeat(np.arange(n_pos, dtype=np.int64), np.diff(indptr))
    term = (g_up.astype(np.float64) + C.eps) ** C.p
    floor = C.eps ** C.p
    e = Entries(text=pos // SEQ_LEN, comp=cache["indices"].astype(np.int64), g=g, z=z, g_up=g_up, delta=term - floor, term=term,
                saturated=z > 1, n_texts=n_texts, n_sub=n_sub)
    return e, check1


def per_text_sums(e: Entries, C: Constants, eps: float | None = None) -> np.ndarray:
    """S[i, c] = sum over the stored entries of (g_up + eps)^p, plus (512 - n_pos[i, c]) eps^p, in float64."""
    eps = C.eps if eps is None else eps
    key = e.text * e.n_sub + e.comp
    term = e.term if eps == C.eps else (e.g_up.astype(np.float64) + eps) ** C.p
    n = e.n_texts * e.n_sub
    s = np.bincount(key, weights=term, minlength=n)
    cnt = np.bincount(key, minlength=n)
    floor = eps ** C.p if eps > 0 else 0.0
    return (s + (SEQ_LEN - cnt) * floor).reshape(e.n_texts, e.n_sub)


def companion_tuples(n_texts: int, W: int, K: int, seed: int) -> np.ndarray:
    """K tuples of 64/W - 1 distinct texts, drawn one at a time from default_rng(seed)."""
    b_loc = N_TEXTS_BATCH // W
    rng = np.random.default_rng(seed)
    return np.stack([np.sort(rng.choice(n_texts, size=b_loc - 1, replace=False)) for _ in range(K)]).astype(np.int64)


# ----------------------------------------------------------------------------- the workhorse


class Pricer:
    """Prices labels and freed sets for one cache, one W, one tuple set. Every array lives on `device` in float64."""

    def __init__(self, S: np.ndarray, tuples: np.ndarray, W: int, C: Constants, device: str = "cpu"):
        import torch

        self.torch = torch
        self.W, self.C, self.device = W, C, device
        self.n_texts, self.n_sub = S.shape
        self.S = torch.from_numpy(S).to(device)
        self.tuples = tuples
        self.K = tuples.shape[0]
        St = self.S.T.contiguous()  # [n_sub, n_texts]
        self.X = torch.stack([St[:, t].sum(dim=1) for t in torch.from_numpy(tuples).to(device)], dim=1)  # [n_sub, K]
        contains = np.zeros((self.n_texts, self.K), dtype=bool)
        for k, t in enumerate(tuples):
            contains[t, k] = True
        self.valid = torch.from_numpy(~contains).to(device)  # [n_texts, K]: the tuples usable for text i
        self.S_total = self.S.sum(dim=0)  # [n_sub]

    def _expect(self, i: int, comp: Any, s_own: Any, q: Any) -> Any:
        """lambda * mean over text i's valid tuples of f(s_own + X) - f(s_own + X - q), per row."""
        torch = self.torch
        v = self.valid[i]
        X = self.X[comp][:, v]  # [n, K_i]
        s = s_own[:, None] + X
        d = f_w(s, self.W, self.C.beta) - f_w(s - q[:, None], self.W, self.C.beta)
        return self.C.lam * d.mean(dim=1)

    def price_text(self, i: int, comp: np.ndarray, delta: np.ndarray, chunk: int = 200_000) -> np.ndarray:
        torch = self.torch
        out = []
        for a in range(0, comp.size, chunk):
            c = torch.from_numpy(comp[a : a + chunk]).to(self.device)
            q = torch.from_numpy(delta[a : a + chunk]).to(self.device)
            out.append(self._expect(i, c, self.S[i, c], q).cpu().numpy())
        return np.concatenate(out) if out else np.zeros(0)

    def plugin_text(self, i: int, comp: np.ndarray, delta: np.ndarray) -> np.ndarray:
        """X_c = (B_loc - 1) * mean over texts j != i of S[j, c]."""
        torch = self.torch
        c = torch.from_numpy(comp).to(self.device)
        q = torch.from_numpy(delta).to(self.device)
        b_loc = N_TEXTS_BATCH // self.W
        s_own = self.S[i, c]
        Xbar = (b_loc - 1) * (self.S_total[c] - s_own) / (self.n_texts - 1)
        s = s_own + Xbar
        return (self.C.lam * (f_w(s, self.W, self.C.beta) - f_w(s - q, self.W, self.C.beta))).cpu().numpy()

    def price_on_tuple(self, i: int, comp: int, delta: float, k: int) -> float:
        s = self.S[i, comp] + self.X[comp, k]
        q = self.torch.tensor(delta, dtype=self.S.dtype, device=self.device)
        return float(self.C.lam * (f_w(s, self.W, self.C.beta) - f_w(s - q, self.W, self.C.beta)))

    def saved_price_T(self, i: int, comp: np.ndarray, delta: np.ndarray) -> float:
        """T_i: lambda * sum over components of the expected exact difference with all of text i's freed labels removed
        together; `comp` and `delta` list the freed labels (one row per freed (position, component) entry)."""
        torch = self.torch
        if comp.size == 0:
            return 0.0
        uc, inv = np.unique(comp, return_inverse=True)
        q = np.bincount(inv, weights=delta)
        c = torch.from_numpy(uc).to(self.device)
        return float(self._expect(i, c, self.S[i, c], torch.from_numpy(q).to(self.device)).sum())


def old_price(e_comp: np.ndarray, e_delta: np.ndarray, S: np.ndarray, C: Constants) -> np.ndarray:
    """The project plan's price with the eps floor and g_up: lambda Delta [1 + beta log2(1+s) + (beta/ln2) s/(1+s)],
    s = 64 * mean over the cache's texts of S[i, c]."""
    s = N_TEXTS_BATCH * S.mean(axis=0)[e_comp]
    bracket = 1 + C.beta * np.log2(1 + s) + (C.beta / math.log(2)) * s / (1 + s)
    return C.lam * e_delta * bracket


def text_slices(indptr: np.ndarray, n_texts: int) -> list[tuple[int, int]]:
    return [(int(indptr[i * SEQ_LEN]), int(indptr[(i + 1) * SEQ_LEN])) for i in range(n_texts)]


def price_all(e: Entries, pricer: Pricer, slices: list[tuple[int, int]], plugin: bool = False, log: Any = print) -> tuple[np.ndarray, np.ndarray | None]:
    price = np.empty(e.comp.size, dtype=np.float64)
    plug = np.empty(e.comp.size, dtype=np.float64) if plugin else None
    for i, (a, b) in enumerate(slices):
        price[a:b] = pricer.price_text(i, e.comp[a:b], e.delta[a:b])
        if plugin:
            plug[a:b] = pricer.plugin_text(i, e.comp[a:b], e.delta[a:b])
        if i % 256 == 0:
            log(f"[prices] W={pricer.W}: text {i}")
    return price, plug


# ----------------------------------------------------------------------------- the authors' functions


def authors_compute(sums: dict[str, Any], n: int, W: int, C: Constants) -> Any:
    """`_importance_minimality_loss_compute` under float64 default dtype, the result asserted float64."""
    import torch

    from param_decomp.metrics.importance_minimality_loss import _importance_minimality_loss_compute

    prev = torch.get_default_dtype()
    torch.set_default_dtype(torch.float64)
    try:
        out = _importance_minimality_loss_compute(per_component_sums=sums, n_examples=n, beta=C.beta, world_size=W)
    finally:
        torch.set_default_dtype(prev)
    assert out.dtype == torch.float64, out.dtype
    return out


def authors_update(g_up: dict[str, Any], C: Constants, eps: float | None = None) -> tuple[dict[str, Any], int]:
    from param_decomp.metrics.importance_minimality_loss import _importance_minimality_loss_update

    return _importance_minimality_loss_update(ci_upper_leaky=g_up, pnorm=C.pnorm, eps=C.eps if eps is None else eps,
                                              p_anneal_start_frac=C.p_anneal_start_frac, p_anneal_final_p=C.p_anneal_final_p,
                                              p_anneal_end_frac=C.p_anneal_end_frac, current_frac_of_training=1.0)


def minimality_from_sums(S_rows: np.ndarray, W: int, n: int, module_order: list[str], offsets: dict[str, int], module_to_c: dict[str, int],
                         C: Constants) -> float:
    """The authors' `_compute` on per-component sums given in the global layout (one rank batch's sum over its texts)."""
    import torch

    s = torch.from_numpy(np.ascontiguousarray(S_rows, dtype=np.float64))
    sums = {k: s[offsets[k] : offsets[k] + module_to_c[k]] for k in module_order}
    return float(authors_compute(sums, n, W, C))


# ----------------------------------------------------------------------------- checks


def check2(C: Constants, seed: int, n_draws: int = 1000) -> dict[str, Any]:
    """Vectorized f_W / n against the authors' `_compute` on 1,000 random (s, W, n), s near 0 and above 5,000 included.
    Passes if every relative difference is below 1e-12."""
    import torch

    rng = np.random.default_rng(seed)
    s = np.concatenate([10 ** rng.uniform(-10, 5, n_draws - 100), 10 ** rng.uniform(-14, -6, 50), rng.uniform(5_000, 1e6, 50)])
    Ws = rng.choice([1, 2, 4, 8, 16, 32, 64], size=n_draws)
    ns = rng.choice([512, 1024, 2048, 4096, 32768, 65536], size=n_draws)
    rel = np.empty(n_draws)
    for j in range(n_draws):
        st = torch.tensor([s[j]], dtype=torch.float64)
        ours = float(f_w(st, int(Ws[j]), C.beta)[0]) / int(ns[j])
        ref = float(authors_compute({"layer": st}, int(ns[j]), int(Ws[j]), C))
        rel[j] = abs(ours - ref) / abs(ref)
    return {"draws": n_draws, "s_range": [float(s.min()), float(s.max())], "n_s_below_1e-6": int((s < 1e-6).sum()),
            "n_s_above_5000": int((s > 5000).sum()), "max_relative_difference": float(rel.max()), "rule": "every relative difference below 1e-12",
            "passes": bool(rel.max() < 1e-12)}


def dense_rank_batch(cache: dict[str, np.ndarray], e: Entries, texts: list[int], module_order: list[str], offsets: dict[str, int],
                     module_to_c: dict[str, int], device: str) -> dict[str, Any]:
    """The rank batch's g_up as dense float64 tensors [len(texts), 512, C_l] per layer; zero where no label is stored."""
    import torch

    indptr = cache["indptr"]
    out = {k: torch.zeros((len(texts), SEQ_LEN, module_to_c[k]), dtype=torch.float64, device=device) for k in module_order}
    bounds = np.array([offsets[k] for k in module_order] + [e.n_sub])
    for b, i in enumerate(texts):
        a, z = int(indptr[i * SEQ_LEN]), int(indptr[(i + 1) * SEQ_LEN])
        t = np.repeat(np.arange(SEQ_LEN), np.diff(indptr[i * SEQ_LEN : (i + 1) * SEQ_LEN + 1]))
        comp, gu = e.comp[a:z], e.g_up[a:z].astype(np.float64)
        layer = np.searchsorted(bounds, comp, side="right") - 1
        for li, k in enumerate(module_order):
            m = layer == li
            if m.any():
                out[k][b, torch.from_numpy(t[m]).to(device), torch.from_numpy(comp[m] - offsets[k]).to(device)] = torch.from_numpy(gu[m]).to(device)
    return out


def check3(cache: dict[str, np.ndarray], e: Entries, pricer: Pricer, slices: list[tuple[int, int]], meta: dict[str, Any], C: Constants,
           seed: int, n_labels: int = 200, device: str = "cpu") -> dict[str, Any]:
    """Finite difference: for 200 random labels, the authors' `_update` on the dense rank batch (the label's text plus one
    stored tuple not containing it), with and without the label zeroed, then `_compute` on that label's (layer,
    component) sums as one-element tensors, times lambda n. Pass per label (plan 2 of the research log, item 6):
    |pi_ref - pi_work| <= 1e-9 pi_ref + 1e-13 summed nats. The difference of `_compute` over all 24 layers is recorded beside."""
    import torch

    order, offsets, m2c = meta["module_order"], meta["module_offsets"], meta["module_to_c"]
    bounds = np.array([offsets[k] for k in order] + [e.n_sub])
    rng = np.random.default_rng(seed)
    picks = np.sort(rng.choice(e.comp.size, size=n_labels, replace=False))
    n = (N_TEXTS_BATCH // pricer.W) * SEQ_LEN
    rows = []
    for j in picks:
        i, c = int(e.text[j]), int(e.comp[j])
        valid = np.flatnonzero(pricer.valid[i].cpu().numpy())
        k = int(rng.choice(valid))
        texts = [i] + [int(t) for t in pricer.tuples[k]]
        dense = dense_rank_batch(cache, e, texts, order, offsets, m2c, device)
        li = int(np.searchsorted(bounds, c, side="right") - 1)
        layer, cl = order[li], c - offsets[order[li]]
        a = int(cache["indptr"][i * SEQ_LEN])
        t = int(np.searchsorted(cache["indptr"], j, side="right") - 1) - i * SEQ_LEN
        assert a <= j and float(dense[layer][0, t, cl]) == float(e.g_up[j])
        sums_with, n_with = authors_update(dense, C)
        zeroed = dict(dense)
        zeroed[layer] = dense[layer].clone()
        zeroed[layer][0, t, cl] = 0.0
        sums_without, n_without = authors_update(zeroed, C)
        assert n_with == n_without == n, (n_with, n)
        one_with = {layer: sums_with[layer][cl : cl + 1]}
        one_without = {layer: sums_without[layer][cl : cl + 1]}
        pi_ref = C.lam * n * float(authors_compute(one_with, n, pricer.W, C) - authors_compute(one_without, n, pricer.W, C))
        pi_all = C.lam * n * float(authors_compute(sums_with, n, pricer.W, C) - authors_compute(sums_without, n, pricer.W, C))
        pi_work = pricer.price_on_tuple(i, c, float(e.delta[j]), k)
        bound = 1e-9 * abs(pi_ref) + 1e-13
        rows.append({"entry": int(j), "text": i, "component": c, "layer": layer, "position": t, "tuple": k, "g_up": float(e.g_up[j]),
                     "pi_ref": pi_ref, "pi_work": pi_work, "abs_difference": abs(pi_ref - pi_work), "bound": bound,
                     "passes": abs(pi_ref - pi_work) <= bound, "pi_all_terms": pi_all, "abs_difference_all_terms": abs(pi_all - pi_work)})
        del dense, zeroed, sums_with, sums_without
    rel = np.array([r["abs_difference"] / abs(r["pi_ref"]) for r in rows])
    return {"labels": n_labels, "rule": "|pi_ref - pi_work| <= 1e-9 pi_ref + 1e-13 summed nats, per label (plan 2 of the research log, item 6)",
            "passes": all(r["passes"] for r in rows), "n_failing": sum(not r["passes"] for r in rows),
            "max_relative_difference": float(rel.max()), "max_abs_difference": float(max(r["abs_difference"] for r in rows)),
            "pi_ref_range": [float(min(r["pi_ref"] for r in rows)), float(max(r["pi_ref"] for r in rows))],
            "all_terms_max_abs_difference": float(max(r["abs_difference_all_terms"] for r in rows)),
            "all_terms_max_relative_difference": float(max(r["abs_difference_all_terms"] / abs(r["pi_ref"]) for r in rows)), "rows": rows}


def minimality_forms(S: np.ndarray, rows: tuple[int, int], meta: dict[str, Any], C: Constants, per_process_texts: int) -> dict[str, float]:
    """The minimality on texts rows[0]..rows[1]-1 in two forms, through the authors' `_compute`: the whole-batch form
    (sums over all the texts, world size 1) and the per-process form (consecutive shares of `per_process_texts` texts,
    world size n_texts / per_process_texts, the mean over shares)."""
    order, offsets, m2c = meta["module_order"], meta["module_offsets"], meta["module_to_c"]
    a, b = rows
    n_t = b - a
    whole = minimality_from_sums(S[a:b].sum(axis=0), 1, n_t * SEQ_LEN, order, offsets, m2c, C)
    W = n_t // per_process_texts
    shares = [minimality_from_sums(S[a + r * per_process_texts : a + (r + 1) * per_process_texts].sum(axis=0), W, per_process_texts * SEQ_LEN,
                                   order, offsets, m2c, C) for r in range(W)]
    return {"whole_batch_world_size_1": whole, "per_process_mean": float(np.mean(shares)), "per_process_world_size": W,
            "texts_per_process": per_process_texts}


def check5(S: np.ndarray, meta: dict[str, Any], C: Constants) -> dict[str, Any]:
    forms = minimality_forms(S, (0, 64), meta, C, 4)
    rel_w = forms["whole_batch_world_size_1"] / PLAN1_WHOLE_64 - 1
    rel_p = forms["per_process_mean"] / PLAN1_PER_PROCESS_64 - 1
    return {**forms, "plan1_whole": PLAN1_WHOLE_64, "plan1_per_process": PLAN1_PER_PROCESS_64, "relative_difference_whole": rel_w,
            "relative_difference_per_process": rel_p, "within_0.2pct": bool(abs(rel_w) <= 0.002 and abs(rel_p) <= 0.002)}


def logged_training_values(provenance_dir: Path) -> list[float]:
    import csv

    vals = {}
    with open(provenance_dir / "runs" / "s-55ea3f9b" / "loss_history.csv") as f:
        for row in csv.DictReader(f):
            if row["key"] == "train/loss/ImportanceMinimalityLoss":
                vals[int(row["step"])] = float(row["value"])
    return [vals[s] for s in LOGGED_TRAIN_STEPS]


def check6(S: np.ndarray, meta: dict[str, Any], C: Constants, provenance_dir: Path, n_pseudo: int = 128) -> dict[str, Any]:
    """128 pseudo-batches of 64 Q texts, seed (master, 'price-check', m), each split into 16 rank batches of 4 texts in
    the drawn order; per-rank `_compute` at world size 16, averaged over ranks. Report only; flag a gap above 5 percent."""
    from vpd_audit_2.manifest import perm

    order, offsets, m2c = meta["module_order"], meta["module_offsets"], meta["module_to_c"]
    b_loc = N_TEXTS_BATCH // W_RUN
    vals = []
    for m in range(n_pseudo):
        texts = perm(S.shape[0], "price-check", m)[:N_TEXTS_BATCH]
        ranks = [minimality_from_sums(S[texts[r * b_loc : (r + 1) * b_loc]].sum(axis=0), W_RUN, b_loc * SEQ_LEN, order, offsets, m2c, C)
                 for r in range(W_RUN)]
        vals.append(float(np.mean(ranks)))
    logged = logged_training_values(provenance_dir)
    gap = float(np.mean(vals) / np.mean(logged) - 1)
    return {"pseudo_batches": n_pseudo, "seed_key": "(master, 'price-check', m)", "mean": float(np.mean(vals)), "sd": float(np.std(vals, ddof=1)),
            "min": float(np.min(vals)), "max": float(np.max(vals)), "logged_steps": list(LOGGED_TRAIN_STEPS), "logged_values": logged,
            "logged_mean": float(np.mean(logged)), "logged_sd": float(np.std(logged, ddof=1)), "relative_gap": gap,
            "gap_above_5pct": bool(abs(gap) > 0.05), "note": "report only: train and validation text differ, and this check cannot separate W = 16 from W = 1"}


def check7(e: Entries, S: np.ndarray, price_new: np.ndarray, price_old: np.ndarray) -> dict[str, Any]:
    """Components whose per-text S has a coefficient of variation (population SD over mean, across the cache's texts)
    below 0.2. Pass (plan 2 of the research log, item 2): for every qualifying component, the median over its labels of new / old lies in
    [0.98, 1.02]. Label-level 1st and 99th percentiles reported as description."""
    cv = S.std(axis=0) / S.mean(axis=0)
    qual = np.flatnonzero(cv < 0.2)
    if qual.size == 0:
        return {"qualifying_components": 0, "skipped": True, "passes": True}
    m = np.isin(e.comp, qual)
    ratio = price_new[m] / price_old[m]
    comp = e.comp[m]
    order = np.argsort(comp, kind="stable")
    comp_s, ratio_s = comp[order], ratio[order]
    starts = np.flatnonzero(np.r_[True, comp_s[1:] != comp_s[:-1]])
    ends = np.r_[starts[1:], comp_s.size]
    medians = np.array([np.median(ratio_s[a:b]) for a, b in zip(starts, ends)])
    comps = comp_s[starts]
    bad = (medians < 0.98) | (medians > 1.02)
    return {"qualifying_components": int(qual.size), "qualifying_components_with_labels": int(comps.size), "labels": int(m.sum()),
            "cv_definition": "population SD of S[i, c] across the cache's texts over its mean",
            "rule": "for every qualifying component, the median over its labels of new / old price lies in [0.98, 1.02]",
            "component_median_ratio": {"min": float(medians.min()), "median": float(np.median(medians)), "max": float(medians.max())},
            "components_outside": [{"component": int(c), "median_ratio": float(r)} for c, r in zip(comps[bad], medians[bad])],
            "label_ratio_percentiles": {"p1": float(np.percentile(ratio, 1)), "p50": float(np.percentile(ratio, 50)), "p99": float(np.percentile(ratio, 99))},
            "passes": not bool(bad.any())}


def price_entries(pricer: Pricer, e: Entries, idx: np.ndarray, delta: np.ndarray | None = None) -> np.ndarray:
    """Prices of the entries `idx` (any texts), grouped by text; `delta` overrides e.delta[idx] (check 9)."""
    d = e.delta[idx] if delta is None else delta
    out = np.empty(idx.size, dtype=np.float64)
    texts = e.text[idx]
    for i in np.unique(texts):
        m = texts == i
        out[m] = pricer.price_text(int(i), e.comp[idx[m]], d[m])
    return out


def check8(e: Entries, S: np.ndarray, price_k256: np.ndarray, tuples_k1024: np.ndarray, sample: np.ndarray, C: Constants, device: str) -> dict[str, Any]:
    """Convergence in K: the sample's prices with the K = 1,024 tuples, whose first 256 are the K = 256 set (nested).
    The nested difference has sqrt(3/4) of the K = 256 error's SD, so the threshold is 0.87 percent at the 99th
    percentile (plan 2 of the research log, item 12). Above it, K = 1,024 is used throughout."""
    p1024 = price_entries(Pricer(S, tuples_k1024, W_RUN, C, device), e, sample)
    rel = np.abs(price_k256[sample] / p1024 - 1)
    p99 = float(np.percentile(rel, 99))
    return {"sample": int(sample.size), "K": [K_DEFAULT, int(tuples_k1024.shape[0])], "nested": True,
            "relative_difference": {"p50": float(np.median(rel)), "p99": p99, "max": float(rel.max())},
            "rule": "99th percentile of |pi_256 / pi_1024 - 1| below 0.87 percent (1 percent scaled by sqrt(3/4) for nesting)",
            "passes": bool(p99 < 0.0087), "K_used": K_DEFAULT if p99 < 0.0087 else int(tuples_k1024.shape[0])}


def check9(e: Entries, price: np.ndarray, tuples: np.ndarray, sample: np.ndarray, C: Constants, device: str) -> dict[str, Any]:
    """eps sensitivity: the sample's prices recomputed with eps = 0 (S without the floor, Delta = g_up^p), same tuples.
    Report: the median relative change, against 0.1 percent."""
    S0 = per_text_sums(e, C, eps=0.0)
    d0 = e.g_up[sample].astype(np.float64) ** C.p
    p0 = price_entries(Pricer(S0, tuples, W_RUN, C, device), e, sample, delta=d0)
    rel = np.abs(p0 / price[sample] - 1)
    return {"sample": int(sample.size), "relative_change": {"p50": float(np.median(rel)), "p99": float(np.percentile(rel, 99)), "max": float(rel.max())},
            "rule": "median relative change below 0.1 percent (report)", "median_below_0.1pct": bool(np.median(rel) < 0.001)}


def check7_diagnostic(e: Entries, S: np.ndarray, price_new: np.ndarray, price_old: np.ndarray, C: Constants) -> dict[str, Any]:
    """Description only, after check 7 failed: the qualifying components grouped by their mean per-text sum S-bar, which
    the eps floor (512 eps^p = 0.0081 per text) sets for components with few or no labels. Per group: components, labels,
    how many medians lie in [0.98, 1.02], the medians' range, and the median over components of the median Delta / (4 S-bar),
    a label's share of its rank batch's sum at even use. Changes no rule."""
    floor = SEQ_LEN * C.eps ** C.p
    Sbar = S.mean(axis=0)
    cv = S.std(axis=0) / Sbar
    qual = cv < 0.2
    n_lab = np.bincount(e.comp, minlength=e.n_sub)
    m = qual[e.comp]
    comp, ratio, rel = e.comp[m], price_new[m] / price_old[m], e.delta[m] / (4 * Sbar[e.comp[m]])
    order = np.argsort(comp, kind="stable")
    comp_s, ratio_s, rel_s = comp[order], ratio[order], rel[order]
    starts = np.flatnonzero(np.r_[True, comp_s[1:] != comp_s[:-1]])
    ends = np.r_[starts[1:], comp_s.size]
    comps = comp_s[starts]
    med = np.array([np.median(ratio_s[a:b]) for a, b in zip(starts, ends)])
    med_rel = np.array([np.median(rel_s[a:b]) for a, b in zip(starts, ends)])
    groups = {}
    edges = [(0, 2 * floor), (2 * floor, 0.1), (0.1, 1), (1, 10), (10, np.inf)]
    for lo, hi in edges:
        g = (Sbar[comps] >= lo) & (Sbar[comps] < hi)
        inside = (med[g] >= 0.98) & (med[g] <= 1.02)
        groups[f"S-bar in [{lo:.4g}, {hi:.4g})"] = {
            "components": int(g.sum()), "labels": int(n_lab[comps[g]].sum()), "medians_inside": int(inside.sum()),
            "median_ratio_range": [float(med[g].min()), float(med[g].max())] if g.any() else None,
            "median_of_median_delta_over_4_Sbar": float(np.median(med_rel[g])) if g.any() else None}
    return {"floor_per_text": floor, "qualifying": int(qual.sum()), "qualifying_without_labels": int((qual & (n_lab == 0)).sum()),
            "qualifying_with_labels": int(comps.size), "groups_by_S_bar": groups,
            "note": "description only; check 7's rule and its qualifying set are unchanged"}


def bracket(s: np.ndarray, C: Constants) -> np.ndarray:
    """The old formula's bracket b(s) = 1 + beta log2(1+s) + (beta/ln 2) s/(1+s)."""
    return 1 + C.beta * np.log2(1 + s) + (C.beta / math.log(2)) * s / (1 + s)


def _component_medians(comp: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if comp.size == 0:
        return comp[:0], np.zeros(0)
    order = np.argsort(comp, kind="stable")
    cs, xs = comp[order], x[order]
    starts = np.flatnonzero(np.r_[True, cs[1:] != cs[:-1]])
    ends = np.r_[starts[1:], cs.size]
    return cs[starts], np.array([np.median(xs[a:b]) for a, b in zip(starts, ends)])


def check7_amended(cache: dict[str, np.ndarray], e: Entries, S: np.ndarray, price_new: np.ndarray, price_old: np.ndarray, pricer: Pricer,
                   meta: dict[str, Any], C: Constants, device: str = "cpu") -> dict[str, Any]:
    """Check 7 as amended by the earlier plan 3 of the research log, Section 2, after the original failed (registered as made after the result).

    m_c = median over component c's labels of Delta / (4 S-bar_c).
      7a: components with CV < 0.2, m_c < 0.05 and a label on Q; pass if each component's median new/old is in [0.98, 1.02].
      7b: components with CV < 0.2, m_c >= 0.05 and a label on Q; per label rho_pred = [f16(S_ic + 3 S-bar) - f16(S_ic + 3 S-bar
          - Delta)] / [Delta b(64 S-bar)]; pass if each component's median of (new/old) / rho_pred is in [0.98, 1.02].
      7c: 100 labels drawn from each excluded group (near-dead: S-bar below twice the floor; the rest of the excluded set), seed
          (master, 'price-check7c', group); check 3's rule on each, the tuple drawn from the same generator as in check 3.
    The stored prices are read; none is recomputed."""
    import torch

    from vpd_audit_2.manifest import seed_of

    floor = SEQ_LEN * C.eps ** C.p
    Sbar = S.mean(axis=0)
    cv = S.std(axis=0) / Sbar
    n_lab = np.bincount(e.comp, minlength=e.n_sub)
    share = e.delta / (4 * Sbar[e.comp])
    comps_all, m_all = _component_medians(e.comp, share)
    m = np.full(e.n_sub, np.nan)
    m[comps_all] = m_all
    has = n_lab > 0
    q7a = (cv < 0.2) & has & (m < 0.05)
    q7b = (cv < 0.2) & has & (m >= 0.05)
    ratio = price_new / price_old
    out: dict[str, Any] = {"floor_per_text": floor, "registered": "amended after the result (plan 3 of the research log)"}

    sel = q7a[e.comp]
    ca, meda = _component_medians(e.comp[sel], ratio[sel])
    bad = (meda < 0.98) | (meda > 1.02)
    out["7a"] = {"qualifying_components": int(q7a.sum()), "labels": int(sel.sum()),
                 "rule": "CV < 0.2, m_c < 0.05, a label on Q: each component's median new/old in [0.98, 1.02]",
                 "median_ratio_range": [float(meda.min()), float(meda.max())] if meda.size else None,
                 "components_outside": [{"component": int(c), "median_ratio": float(r)} for c, r in zip(ca[bad], meda[bad])],
                 "passes": bool(meda.size > 0 and not bad.any())}

    sel = q7b[e.comp]
    s_own = S[e.text[sel], e.comp[sel]]
    xbar3 = 3 * Sbar[e.comp[sel]]
    d = e.delta[sel]
    st = torch.from_numpy(s_own + xbar3)
    num = (f_w(st, W_RUN, C.beta) - f_w(st - torch.from_numpy(d), W_RUN, C.beta)).numpy()
    rho = num / (d * bracket(N_TEXTS_BATCH * Sbar[e.comp[sel]], C))
    cb, medb = _component_medians(e.comp[sel], ratio[sel] / rho)
    _, medrho = _component_medians(e.comp[sel], rho)
    _, medratio = _component_medians(e.comp[sel], ratio[sel])
    badb = (medb < 0.98) | (medb > 1.02)
    near = Sbar[cb] < 2 * floor
    out["7b"] = {"components": int(q7b.sum()), "labels": int(sel.sum()),
                 "rule": "CV < 0.2, m_c >= 0.05, a label on Q: each component's median of (new/old) / rho_pred in [0.98, 1.02]",
                 "median_of_ratio_over_prediction_range": [float(medb.min()), float(medb.max())] if medb.size else None,
                 "median_new_over_old_range": [float(medratio.min()), float(medratio.max())] if medratio.size else None,
                 "median_rho_pred_range": [float(medrho.min()), float(medrho.max())] if medrho.size else None,
                 "by_group": {"near_dead": {"components": int(near.sum()), "range": [float(medb[near].min()), float(medb[near].max())] if near.any() else None},
                              "rest": {"components": int((~near).sum()), "range": [float(medb[~near].min()), float(medb[~near].max())] if (~near).any() else None}},
                 "components_outside": [{"component": int(c), "median": float(r)} for c, r in zip(cb[badb], medb[badb])],
                 "passes": bool(not badb.any())}

    order, offsets, m2c = meta["module_order"], meta["module_offsets"], meta["module_to_c"]
    bounds = np.array([offsets[k] for k in order] + [e.n_sub])
    n = (N_TEXTS_BATCH // pricer.W) * SEQ_LEN
    groups = {"near-dead": q7b & (Sbar < 2 * floor), "rest": q7b & (Sbar >= 2 * floor)}
    out["7c"] = {"rule": "check 3's rule on each label: |pi_ref - pi_work| <= 1e-9 pi_ref + 1e-13", "groups": {}}
    for gname, gmask in groups.items():
        pool = np.flatnonzero(gmask[e.comp])
        rng = np.random.default_rng(seed_of("price-check7c", gname))
        picks = np.sort(rng.choice(pool, size=min(100, pool.size), replace=False)) if pool.size else pool
        rows = []
        for j in picks:
            i, c = int(e.text[j]), int(e.comp[j])
            k = int(rng.choice(np.flatnonzero(pricer.valid[i].cpu().numpy())))
            dense = dense_rank_batch(cache, e, [i] + [int(t) for t in pricer.tuples[k]], order, offsets, m2c, device)
            li = int(np.searchsorted(bounds, c, side="right") - 1)
            layer, cl = order[li], c - offsets[order[li]]
            t = int(np.searchsorted(cache["indptr"], j, side="right") - 1) - i * SEQ_LEN
            assert float(dense[layer][0, t, cl]) == float(e.g_up[j])
            s1, _ = authors_update(dense, C)
            zeroed = dict(dense)
            zeroed[layer] = dense[layer].clone()
            zeroed[layer][0, t, cl] = 0.0
            s0, _ = authors_update(zeroed, C)
            pi_ref = C.lam * n * float(authors_compute({layer: s1[layer][cl : cl + 1]}, n, pricer.W, C)
                                       - authors_compute({layer: s0[layer][cl : cl + 1]}, n, pricer.W, C))
            pi_work = pricer.price_on_tuple(i, c, float(e.delta[j]), k)
            bound = 1e-9 * abs(pi_ref) + 1e-13
            rows.append({"entry": int(j), "component": c, "pi_ref": pi_ref, "pi_work": pi_work, "abs_difference": abs(pi_ref - pi_work),
                         "passes": abs(pi_ref - pi_work) <= bound})
            del dense, zeroed, s1, s0
        out["7c"]["groups"][gname] = {"labels_in_group": int(pool.size), "drawn": int(picks.size), "seed_key": f"(master, 'price-check7c', '{gname}')",
                                      "n_failing": sum(not r["passes"] for r in rows),
                                      "max_relative_difference": float(max(r["abs_difference"] / abs(r["pi_ref"]) for r in rows)) if rows else None,
                                      "max_abs_difference": float(max(r["abs_difference"] for r in rows)) if rows else None,
                                      "passes": all(r["passes"] for r in rows), "rows": rows}
    out["7c"]["passes"] = all(g["passes"] for g in out["7c"]["groups"].values())

    mq = m[(cv < 0.2) & has]
    out["description"] = {
        "qualifying_under_the_original_rule": int(((cv < 0.2) & has).sum()), "without_labels": int(((cv < 0.2) & ~has).sum()),
        "m_c_percentiles_over_qualifying_with_labels": percentiles(mq, (1, 5, 25, 50, 75, 95, 99)),
        "m_c_histogram": {f"[{a:g}, {b:g})": int(((mq >= a) & (mq < b)).sum()) for a, b in
                          [(0, 0.001), (0.001, 0.01), (0.01, 0.05), (0.05, 0.1), (0.1, 0.25), (0.25, 0.5), (0.5, 1), (1, 2), (2, np.inf)]},
        "groups": {g: {"components": int(v.sum()), "labels": int(v[e.comp].sum())} for g, v in groups.items()}}
    out["passes"] = bool(out["7a"]["passes"] and out["7b"]["passes"] and out["7c"]["passes"])
    return out


def percentiles(x: np.ndarray, qs: tuple[float, ...] = (1, 5, 50, 95)) -> dict[str, float]:
    if x.size == 0:
        return {"n": 0}
    v = np.percentile(x, qs)
    return {"n": int(x.size), **{f"p{q:g}": float(a) for q, a in zip(qs, v)}}


def distribution(price: np.ndarray, e: Entries) -> dict[str, Any]:
    """Percentiles 1, 5, 50, 95 over labels above 0 and above 0.1, all and split by saturation."""
    out = {}
    for name, m in (("above_0", np.ones(e.g.size, dtype=bool)), ("above_0.1", e.g > 0.1)):
        out[name] = {"all": percentiles(price[m]), "unsaturated": percentiles(price[m & ~e.saturated]), "saturated": percentiles(price[m & e.saturated])}
    return out


def ratio_histogram(new: np.ndarray, old: np.ndarray) -> dict[str, Any]:
    r = new / old
    edges = np.array([0, 0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 1.02, 1.05, 1.1, 1.2, 1.3, 1.5, 2, 4, np.inf])
    h = np.histogram(r, bins=edges)[0]
    return {"bins": [f"[{a:g}, {b:g})" for a, b in zip(edges[:-1], edges[1:])], "counts": [int(x) for x in h],
            "shares": [float(x / r.size) for x in h], "percentiles": percentiles(r, (1, 5, 25, 50, 75, 95, 99)),
            "share_below_1": float((r < 1).mean()), "mean": float(r.mean())}


# ----------------------------------------------------------------------------- one cache, end to end


def tuple_sets(n_texts: int) -> dict[str, np.ndarray]:
    """The committed companion tuples: W = 16 with K = 256 (deciding) and K = 1,024 (check 8, nesting the 256), and
    W = 1 with K = 256 (the global reading's column). Seeds (master, 'price-companions', W)."""
    from vpd_audit_2.manifest import seed_of

    t16 = companion_tuples(n_texts, W_RUN, 1024, seed_of("price-companions", W_RUN))
    t16_256 = companion_tuples(n_texts, W_RUN, K_DEFAULT, seed_of("price-companions", W_RUN))
    assert np.array_equal(t16[:K_DEFAULT], t16_256), "the K = 1,024 draw does not nest the K = 256 set"
    t1 = companion_tuples(n_texts, 1, K_DEFAULT, seed_of("price-companions", 1))
    return {"W16_K256": t16_256, "W16_K1024": t16, "W1_K256": t1}


def price_cache(cache_path: Path, name: str, out_dir: Path, device: str, provenance_dir: Path, deciding: bool,
                log: Any = print) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Every price column of one cache, its checks, and its distributions. Writes `<out_dir>/<name>_prices.npz` (columns
    aligned with the cache's entries) and `<name>_S.npy`; returns the summary."""
    import time

    from vpd_audit_2.manifest import seed_of

    t0 = time.time()
    C = constants()
    cache, meta = load_cache(cache_path)
    e, c1 = entries(cache, meta, C)
    log(f"[prices] {name}: {e.g.size} labels on {e.n_texts} texts; check 1 {c1['passes']}")
    S = per_text_sums(e, C)
    tuples = tuple_sets(e.n_texts)
    slices = text_slices(cache["indptr"], e.n_texts)
    p16 = Pricer(S, tuples["W16_K256"], W_RUN, C, device)
    price, plug = price_all(e, p16, slices, plugin=True, log=log)
    price_w1, _ = price_all(e, Pricer(S, tuples["W1_K256"], 1, C, device), slices, log=log)
    old = old_price(e.comp, e.delta, S, C)
    out: dict[str, Any] = {
        "cache": {"path": str(cache_path), "sha256": meta["sha256"], "precision": meta["precision"], "labels": int(e.g.size), "texts": e.n_texts},
        "constants": {"lambda": C.lam, "beta": C.beta, "eps": C.eps, "p": C.p, "W": W_RUN, "branch": "W = 16 confirmed (plan 2 of the research log's world-size test)",
                      "B_loc": N_TEXTS_BATCH // W_RUN, "K": K_DEFAULT},
        "tuples_sha256": {k: sha256_array(v) for k, v in tuples.items()},
        "check1": c1, "check5": check5(S, meta, C), "check6": check6(S, meta, C, provenance_dir),
        "distribution": {"price_W16": distribution(price, e), "plugin_W16": distribution(plug, e), "price_W1_global": distribution(price_w1, e),
                         "old_formula": distribution(old, e)},
        "pi_5": float(np.percentile(price, 5)), "pi_5_W1_global": float(np.percentile(price_w1, 5)),
        "ratio_new_to_old": ratio_histogram(price, old), "ratio_plugin_to_expectation": percentiles(plug / price, (1, 5, 50, 95, 99)),
        "ratio_W1_to_W16": percentiles(price_w1 / price, (1, 5, 50, 95, 99)),
        "saturated": {"labels": int(e.saturated.sum()), "share": float(e.saturated.mean())},
    }
    if deciding:
        out["check2"] = check2(C, seed_of("price-check2"))
        out["check3"] = check3(cache, e, p16, slices, meta, C, seed_of("price-check3"), device=device)
        out["check7"] = check7(e, S, price, old)
        sample = np.sort(np.random.default_rng(seed_of("price-convergence")).choice(e.g.size, size=10_000, replace=False))
        out["check8"] = check8(e, S, price, tuples["W16_K1024"], sample, C, device)
        out["check9"] = check9(e, price, tuples["W16_K256"], sample, C, device)
        if out["check8"]["K_used"] != K_DEFAULT:
            log("[prices] check 8: K = 1,024 throughout")
            p16 = Pricer(S, tuples["W16_K1024"], W_RUN, C, device)
            price, plug = price_all(e, p16, slices, plugin=True, log=log)
            out["distribution"]["price_W16"] = distribution(price, e)
            out["pi_5"] = float(np.percentile(price, 5))
            out["ratio_new_to_old"] = ratio_histogram(price, old)
            out["check7"] = check7(e, S, price, old)
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / f"{name}_S.npy", S)
    arrays = {"price_W16": price, "plugin_W16": plug, "price_W1_global": price_w1, "price_old_formula": old, "saturated": e.saturated}
    with open(out_dir / f"{name}_prices.npz.tmp", "wb") as f:
        np.savez(f, **arrays)
    (out_dir / f"{name}_prices.npz.tmp").replace(out_dir / f"{name}_prices.npz")
    out["files"] = {"prices": f"{name}_prices.npz", "S": f"{name}_S.npy", "columns": {k: str(v.dtype) for k, v in arrays.items()},
                    "sha256": {**{k: sha256_array(v) for k, v in arrays.items()}, "S": sha256_array(S)},
                    "aligned_with": "the cache's entries (labels above zero), in its CSR order"}
    out["seconds"] = time.time() - t0
    log(f"[prices] {name}: pi_5 {out['pi_5']:.4g}; check 5 {out['check5']['within_0.2pct']}; {out['seconds']:.0f} s")
    return out, tuples
