"""The price code against the authors' minimality functions, on a small synthetic cache, on the CPU.

The synthetic cache has 12 texts of 512 positions and three modules (C = 5, 7, 4), with labels drawn so that some are
small, some in (0, 1), and some saturated (z > 1). Every reference value is computed with the authors'
`_importance_minimality_loss_update` and `_importance_minimality_loss_compute` on dense tensors.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import prices as P

MODULES = {"a.attn": 5, "b.mlp": 7, "c.mlp": 4}
N_TEXTS = 12


def _synthetic(seed: int = 0) -> tuple[dict[str, np.ndarray], dict]:
    rng = np.random.default_rng(seed)
    order = sorted(MODULES)
    offsets, acc = {}, 0
    for k in order:
        offsets[k] = acc
        acc += MODULES[k]
    n_sub = acc
    n_pos = N_TEXTS * P.SEQ_LEN
    use = rng.uniform(0, 0.4, size=n_sub)  # per-component probability of a label above zero
    use[0] = 0.002  # a rarely used component
    cnt, idx, val, zs = [], [], [], []
    for p in range(n_pos):
        on = np.flatnonzero(rng.uniform(size=n_sub) < use)
        z = np.where(rng.uniform(size=on.size) < 0.5, rng.uniform(1.0001, 6, on.size), 10 ** rng.uniform(-6, 0, on.size)).astype(np.float32)
        cnt.append(on.size)
        idx.append(on.astype(np.uint16))
        zs.append(z)
        val.append(np.clip(z, 0, 1).astype(np.float32))
    cache = {"indptr": np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64), "indices": np.concatenate(idx), "values": np.concatenate(val),
             "z": np.concatenate(zs)}
    meta = {"n_subcomponents": n_sub, "module_order": order, "module_offsets": offsets, "module_to_c": dict(MODULES),
            "sha256": {k: P.sha256_array(v) for k, v in cache.items()}}
    return cache, meta


@pytest.fixture(scope="module")
def syn():
    C = P.constants()
    cache, meta = _synthetic()
    e, c1 = P.entries(cache, meta, C)
    S = P.per_text_sums(e, C)
    tuples = P.companion_tuples(N_TEXTS, P.W_RUN, 16, 123)
    return C, cache, meta, e, c1, S, tuples


def _dense_text(cache, e, meta, texts):
    return P.dense_rank_batch(cache, e, texts, meta["module_order"], meta["module_offsets"], meta["module_to_c"], "cpu")


def test_constants():
    C = P.constants()
    assert (C.lam, C.beta, C.eps, C.p) == (2e-4, 0.5, 1e-12, 0.4)


def test_the_deciding_branch_is_pinned():
    """Plan 5 of the research log, item 7: the deciding prices use W = 16 (plan 2 of the research log's world-size test) and K = 256 (check 8 passed), so three
    companions per tuple; the global column uses 63."""
    assert (P.W_RUN, P.K_DEFAULT) == (16, 256)
    t = P.tuple_sets(1024)
    assert t["W16_K256"].shape == (256, 3) and t["W1_K256"].shape == (256, 63) and t["W16_K1024"].shape == (1024, 3)
    # the deciding tuple set's SHA-256, as committed in results/s4_plan1_prices/prices.json and cited by the freeze file
    assert P.sha256_array(t["W16_K256"]) == "3a4a9b09703cb343366894663c92811608d2d32450b4d8b4a9c7dd69ff847501"


def test_check1_and_its_negative(syn):
    C, cache, meta, e, c1, S, tuples = syn
    assert c1["passes"] and c1["entries_unequal"] == 0
    assert e.saturated.any() and (~e.saturated).any()
    bad = dict(cache)
    bad["values"] = cache["values"].copy()
    bad["values"][np.flatnonzero(e.saturated)[0]] = np.float32(0.999)
    _, c1b = P.entries(bad, meta, C)
    assert not c1b["passes"] and c1b["entries_unequal"] == 1


def test_per_text_sums_equal_the_authors_update(syn):
    C, cache, meta, e, c1, S, tuples = syn
    for i in (0, 5, 11):
        dense = _dense_text(cache, e, meta, [i])
        sums, n = P.authors_update(dense, C)
        assert n == P.SEQ_LEN
        for k in meta["module_order"]:
            o = meta["module_offsets"][k]
            ref = sums[k].numpy()
            ours = S[i, o : o + MODULES[k]]
            assert np.max(np.abs(ours - ref) / ref) < 1e-12


def test_f_w_against_the_authors_compute():
    C = P.constants()
    r = P.check2(C, seed=7, n_draws=300)
    assert r["passes"], r["max_relative_difference"]


def test_check3_passes(syn):
    C, cache, meta, e, c1, S, tuples = syn
    pricer = P.Pricer(S, tuples, P.W_RUN, C)
    r = P.check3(cache, e, pricer, P.text_slices(cache["indptr"], N_TEXTS), meta, C, seed=3, n_labels=30)
    assert r["passes"], r["max_relative_difference"]
    assert r["pi_ref_range"][0] > 0


def test_price_is_the_mean_over_valid_tuples(syn):
    """The workhorse's expectation equals the mean of the single-tuple prices over the tuples without the text."""
    C, cache, meta, e, c1, S, tuples = syn
    pricer = P.Pricer(S, tuples, P.W_RUN, C)
    i = 3
    a, b = P.text_slices(cache["indptr"], N_TEXTS)[i]
    js = np.arange(a, b)[:: max(1, (b - a) // 20)]
    got = pricer.price_text(i, e.comp[js], e.delta[js])
    valid = [k for k in range(tuples.shape[0]) if i not in tuples[k]]
    # Plan 5 of the research log, item 6: at least one tuple excludes text 3 (so the expectation has terms), and at least one contains it
    # (so the exclusion branch is exercised); with this seed text 3 is in tuples 2, 4, 10, 14, and 15.
    assert 0 < len(valid) < tuples.shape[0]
    for j, g in zip(js, got):
        ref = np.mean([pricer.price_on_tuple(i, int(e.comp[j]), float(e.delta[j]), k) for k in valid])
        assert abs(g - ref) <= 1e-12 * abs(ref)


def test_saved_price_of_one_label_is_its_price_and_additive_across_components(syn):
    C, cache, meta, e, c1, S, tuples = syn
    pricer = P.Pricer(S, tuples, P.W_RUN, C)
    i = 7
    a, b = P.text_slices(cache["indptr"], N_TEXTS)[i]
    j1 = a + 10
    j2 = next(j for j in range(a + 11, b) if e.comp[j] != e.comp[j1])
    pi = pricer.price_text(i, e.comp[[j1, j2]], e.delta[[j1, j2]])
    assert abs(pricer.saved_price_T(i, e.comp[[j1]], e.delta[[j1]]) - pi[0]) <= 1e-15 * pi[0] + 1e-20
    T2 = pricer.saved_price_T(i, e.comp[[j1, j2]], e.delta[[j1, j2]])
    assert abs(T2 - pi.sum()) <= 1e-12 * T2


def test_saved_price_against_the_authors_functions_on_dense_rank_batches(syn):
    """T_i for a freed set with several labels of one component: the mean over valid tuples of lambda n times the
    authors' compute on the dense rank batch, with and without the freed labels zeroed, summed over components."""
    C, cache, meta, e, c1, S, tuples = syn
    pricer = P.Pricer(S, tuples, P.W_RUN, C)
    i = 2
    a, b = P.text_slices(cache["indptr"], N_TEXTS)[i]
    comp_counts = np.bincount(e.comp[a:b], minlength=e.n_sub)
    c = int(np.argmax(comp_counts))
    freed = np.arange(a, b)[e.comp[a:b] == c][:6]
    freed = np.concatenate([freed, np.arange(a, b)[e.comp[a:b] != c][:3]])
    T = pricer.saved_price_T(i, e.comp[freed], e.delta[freed])
    n = 4 * P.SEQ_LEN
    order, offsets = meta["module_order"], meta["module_offsets"]
    bounds = np.array([offsets[k] for k in order] + [e.n_sub])
    indptr = cache["indptr"]
    refs = []
    for k in range(tuples.shape[0]):
        if i in tuples[k]:
            continue
        dense = _dense_text(cache, e, meta, [i] + [int(t) for t in tuples[k]])
        zeroed = {kk: v.clone() for kk, v in dense.items()}
        for j in freed:
            cc = int(e.comp[j])
            li = int(np.searchsorted(bounds, cc, side="right") - 1)
            t = int(np.searchsorted(indptr, j, side="right") - 1) - i * P.SEQ_LEN
            zeroed[order[li]][0, t, cc - offsets[order[li]]] = 0.0
        s1, _ = P.authors_update(dense, C)
        s0, _ = P.authors_update(zeroed, C)
        tot = 0.0
        for cc in np.unique(e.comp[freed]):
            li = int(np.searchsorted(bounds, cc, side="right") - 1)
            lay, cl = order[li], int(cc) - offsets[order[li]]
            tot += C.lam * n * float(P.authors_compute({lay: s1[lay][cl : cl + 1]}, n, P.W_RUN, C) - P.authors_compute({lay: s0[lay][cl : cl + 1]}, n, P.W_RUN, C))
        refs.append(tot)
    ref = float(np.mean(refs))
    assert abs(T - ref) <= 1e-9 * ref


def test_price_spec_third_case_numbers():
    """The price specification's worked example (Section 6): f16(1.032) - f16(0.032) = 3.12, and the plug-in difference at X = 14.1 is 5.65."""
    s = torch.tensor([1.032, 0.032, 1.032 + 14.1, 0.032 + 14.1], dtype=torch.float64)
    f = P.f_w(s, 16, 0.5)
    assert abs(float(f[0] - f[1]) - 3.12) < 0.005
    assert abs(float(f[2] - f[3]) - 5.65) < 0.01


def test_old_price_formula(syn):
    C, cache, meta, e, c1, S, tuples = syn
    j = 100
    s = 64 * S[:, e.comp[j]].mean()
    ref = C.lam * e.delta[j] * (1 + 0.5 * math.log2(1 + s) + (0.5 / math.log(2)) * s / (1 + s))
    assert abs(P.old_price(e.comp[[j]], e.delta[[j]], S, C)[0] - ref) <= 1e-14 * ref


def test_plugin_uses_the_mean_of_the_other_texts(syn):
    C, cache, meta, e, c1, S, tuples = syn
    pricer = P.Pricer(S, tuples, P.W_RUN, C)
    i, j = 4, int(P.text_slices(cache["indptr"], N_TEXTS)[4][0]) + 5
    c = int(e.comp[j])
    xbar = 3 * (S[:, c].sum() - S[i, c]) / (N_TEXTS - 1)
    s = S[i, c] + xbar
    f = lambda x: x + 0.5 * x * math.log2(1 + 16 * x)  # noqa: E731
    ref = C.lam * (f(s) - f(s - e.delta[j]))
    got = pricer.plugin_text(i, e.comp[[j]], e.delta[[j]])[0]
    assert abs(got - ref) <= 1e-12 * ref


def test_minimality_forms_against_the_authors_update_on_dense_texts(syn):
    C, cache, meta, e, c1, S, tuples = syn
    forms = P.minimality_forms(S, (0, 8), meta, C, 4)
    dense = _dense_text(cache, e, meta, list(range(8)))
    sums, n = P.authors_update(dense, C)
    whole = float(P.authors_compute(sums, n, 1, C))
    assert abs(forms["whole_batch_world_size_1"] - whole) <= 1e-12 * whole
    shares = []
    for r in range(2):
        d = {k: v[4 * r : 4 * r + 4] for k, v in dense.items()}
        s, nn = P.authors_update(d, C)
        shares.append(float(P.authors_compute(s, nn, 2, C)))
    assert abs(forms["per_process_mean"] - np.mean(shares)) <= 1e-12 * forms["per_process_mean"]


def test_companion_tuples_nest_and_are_distinct():
    t4 = P.companion_tuples(1024, 16, 1024, 99)
    t1 = P.companion_tuples(1024, 16, 256, 99)
    assert np.array_equal(t4[:256], t1)
    assert all(len(set(r)) == 3 for r in t4)
    g = P.companion_tuples(1024, 1, 8, 5)
    assert g.shape == (8, 63) and all(len(set(r)) == 63 for r in g)


def test_check7_amended_runs_and_its_end_to_end_part_passes(syn):
    """On the synthetic cache: 7c's reference calls agree with the workhorse; 7b's prediction is computed per label."""
    C, cache, meta, e, c1, S, tuples = syn
    pricer = P.Pricer(S, tuples, P.W_RUN, C)
    slices = P.text_slices(cache["indptr"], N_TEXTS)
    new, _ = P.price_all(e, pricer, slices, log=lambda *_: None)
    old = P.old_price(e.comp, e.delta, S, C)
    r = P.check7_amended(cache, e, S, new, old, pricer, meta, C)
    assert r["7c"]["passes"]
    assert r["description"]["qualifying_under_the_original_rule"] == r["7a"]["qualifying_components"] + r["7b"]["components"]
