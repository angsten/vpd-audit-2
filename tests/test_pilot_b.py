"""Plan 6, Part B's harnesses on the tiny model (CPU) and the synthetic price cache: CQ's price path against the stored
path, the nominal set, the label cache, version (ii) against the authors' `run_adv_pgd`, the freed-label and stochastic
harnesses' identities, and the removal harness against G3's positive control."""

from __future__ import annotations

import json

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import cq_prices as CP
from vpd_audit_2 import freed_label as FL
from vpd_audit_2 import g3
from vpd_audit_2 import prices as P
from vpd_audit_2 import pruning_adv as PA
from vpd_audit_2 import removal as R
from vpd_audit_2.label_cache import LabelCache, cache_from_dense

import test_prices as TP
from tiny_model import SEQ, tiny_component_model, tiny_ids


# ----------------------------------------------------------------------------- CQ's prices


@pytest.fixture(scope="module")
def syn():
    C = P.constants()
    cache, meta = TP._synthetic()
    e, _ = P.entries(cache, meta, C)
    S = P.per_text_sums(e, C)
    tuples = P.companion_tuples(TP.N_TEXTS, P.W_RUN, 16, 123)
    return C, cache, meta, e, S, tuples


Q_IDS = [f"q{k}" for k in range(TP.N_TEXTS)]


def test_external_path_matches_the_stored_path_given_the_same_tuples(syn):
    """The external path's arithmetic is the stored path's: a text outside Q whose labels equal Q text i's, priced against
    tuples that never contain i, gets text i's stored-path T. (Plan 6's version priced the Q text itself on the external
    path; plan 7, item 8 refuses that.)"""
    C, cache, meta, e, S, tuples = syn
    for i in (2, 7):
        t_i = tuples[~(tuples == i).any(axis=1)]
        stored = P.Pricer(S, t_i, P.W_RUN, C)
        ext = CP.ExternalPricer(S, t_i, C, Q_IDS)
        S_i, ei, a = CP.text_sums(cache, meta, i, C)
        assert np.array_equal(S_i, S[i])
        sl = P.text_slices(cache["indptr"], TP.N_TEXTS)[i]
        idx = np.arange(sl[0], sl[1])[::5]
        T_ext = CP.arm_T(ext, cache, meta, i, {"f": idx}, C, text_id="outside")["f"]
        T_st = stored.saved_price_T(i, e.comp[idx], e.delta[idx])
        assert abs(T_ext - T_st) <= 1e-9 * T_st + 1e-13
        local = idx - a
        assert np.allclose(ext.price_labels(S_i, ei.comp[local], ei.delta[local], text_id="outside"), stored.price_text(i, e.comp[idx], e.delta[idx]),
                           rtol=1e-14, atol=0)


def test_a_text_outside_q_uses_every_tuple(syn):
    C, cache, meta, e, S, tuples = syn
    ext = CP.ExternalPricer(S, tuples, C, Q_IDS)
    S_i = S[3] * 1.5
    comp, delta = e.comp[:4], e.delta[:4]
    ref = []
    for c, d in zip(comp, delta):
        s = S_i[c] + ext.inner.X[c].numpy()
        f = lambda x: x + 0.5 * x * np.log2(1 + 16 * x)  # noqa: E731
        ref.append(C.lam * np.mean(f(s) - f(s - d)))
    assert np.allclose(ext.price_labels(S_i, comp, delta, text_id="outside"), ref, rtol=1e-12, atol=0)


def test_q_texts_are_priced_from_the_stored_path_and_refused_externally(syn, tmp_path):
    """Plan 7, item 8: the router sends Q texts to the stored path (the stored S row, Delta from Q's full cache), equal bit
    for bit to `prices.Pricer` on the full cache's entries; a Q text on the external path is refused; a text outside Q goes
    to the external path with its own cache."""
    C, cache, meta, e, S, tuples = syn
    qp = CP.QPrices(S, tuples, C, Q_IDS, cache, meta)
    ext = CP.ExternalPricer(S, tuples, C, Q_IDS)
    router = CP.Router(Q_IDS, stored=qp, external=ext, C=C)
    stored = P.Pricer(S, tuples, P.W_RUN, C)
    slices = P.text_slices(cache["indptr"], TP.N_TEXTS)
    for i in (2, 7):
        a, b = slices[i]
        idx = np.arange(a, b)[::7]
        assert router.path(Q_IDS[i]) == "stored"
        assert router.saved_price_T(Q_IDS[i], idx) == stored.saved_price_T(i, e.comp[idx], e.delta[idx])
        assert np.array_equal(qp.price_labels(Q_IDS[i], idx), stored.price_text(i, e.comp[idx], e.delta[idx]))
        with pytest.raises(CP.QTextOnExternalPath):
            ext.saved_price_T(S[i], e.comp[idx], e.delta[idx], text_id=Q_IDS[i])
        with pytest.raises(CP.QTextOnExternalPath):
            CP.arm_T(ext, cache, meta, i, {"f": idx}, C, text_id=Q_IDS[i])
        with pytest.raises(AssertionError, match="outside the text's range"):
            qp.saved_price_T(Q_IDS[i], np.array([b]))
    # the Modal stage's check function, end to end on the synthetic cache written in the cache's layout
    from vpd_audit_2 import pilot_b as PB

    tmp = tmp_path
    (tmp / "labels").mkdir()
    np.savez(tmp / "labels" / "Q_fp32.npz", **cache)
    json.dump(meta, open(tmp / "labels" / "Q_fp32.json", "w"))
    want = {}
    for i in (2, 7):
        a, b = slices[i]
        idx = a + np.arange(0, b - a, 7)
        want[i] = stored.saved_price_T(i, e.comp[idx], e.delta[idx])
    chk = PB.q_stored_path_check(tmp, S, tuples, C, Q_IDS, [2, 7], want, device="cpu")
    assert chk["passes"] and all(t["refused_on_external_path"] and t["equals_expected"] and t["components_equal"] for t in chk["texts"])
    bad = {**want, 7: float(np.nextafter(want[7], 0.0))}
    assert not PB.q_stored_path_check(tmp, S, tuples, C, Q_IDS, [2, 7], bad, device="cpu")["passes"]
    a, b = slices[3]
    idx = np.arange(a, b)[::7]
    assert router.path("outside") == "external"
    assert router.saved_price_T("outside", idx, own=(cache, meta, 3)) == CP.arm_T(ext, cache, meta, 3, {"f": idx}, C, text_id="outside")["f"]
    with pytest.raises(KeyError):
        qp.saved_price_T("outside", idx)
    # the row order: Q's cache records its texts as a string, and its ids' hash must match the one given
    m2 = {**meta, "texts": f"manifest pool Q: {Q_IDS[0]} to {Q_IDS[-1]}", "set_hash_ids_512": "abc"}
    CP.QPrices(S, tuples, C, Q_IDS, cache, m2, ids_sha256="abc")
    with pytest.raises(AssertionError, match="not the given texts"):
        CP.QPrices(S, tuples, C, Q_IDS, cache, m2, ids_sha256="abd")
    with pytest.raises(AssertionError, match="records its texts"):
        CP.QPrices(S, tuples, C, Q_IDS, cache, {**m2, "texts": "manifest pool Q: q5 to q9"})


def test_nominal_set_is_a_tenth_per_position_rounded_half_up(syn):
    C, cache, meta, e, S, tuples = syn
    a = CP.nominal_set(cache, 4, "vX")
    b = CP.nominal_set(cache, 4, "vX")
    assert np.array_equal(a["nominal"], b["nominal"])
    assert not np.array_equal(a["nominal"], CP.nominal_set(cache, 4, "vY")["nominal"])
    pos = np.searchsorted(cache["indptr"], a["nominal"], side="right") - 1
    for t in range(4 * 512, 5 * 512):
        n = int(cache["indptr"][t + 1] - cache["indptr"][t])
        k = int((pos == t).sum())
        assert k == (max(1, int(np.floor(0.1 * n + 0.5))) if n else 0)
    assert set(a["saturated"]) | set(a["unsaturated"]) == set(a["nominal"])
    assert np.all(cache["z"][a["saturated"]] > 1) and np.all(cache["z"][a["unsaturated"]] <= 1)


# ----------------------------------------------------------------------------- the tiny model


@pytest.fixture(scope="module")
def tiny():
    torch.use_deterministic_algorithms(True)
    model = tiny_component_model()
    ids = tiny_ids(32, seed=4).numpy()
    prep = A.prepare(model, ids, "fp32", device="cpu")
    with torch.no_grad():
        o = model(prep.ids, cache_type="input")
        ci = model.calc_causal_importances(o.cache, sampling="continuous", detach_inputs=False)
    cache, meta = cache_from_dense(ci.lower_leaky, ci.pre_sigmoid)
    lc = LabelCache(cache, meta, SEQ)
    return model, ids, prep, cache, meta, lc


def test_label_cache_round_trip(tiny):
    model, ids, prep, cache, meta, lc = tiny
    d = lc.dense(list(range(32)), "cpu")
    assert all(torch.equal(d[k], prep.labels[k]) for k in prep.labels) and list(d) == list(prep.labels)
    idx = np.array([0, 5, 77, int(cache["indptr"][-1]) - 1])
    m = lc.mask(list(range(32)), idx, "cpu")
    assert sum(int(v.sum()) for v in m.values()) == 4
    freed = lc.freed(d, m)
    assert all(torch.equal(freed[k][~m[k]], d[k][~m[k]]) and bool((freed[k][m[k]] == 0).all()) for k in d)


def _freed_mask(lc: LabelCache, texts: list[int], seed: int) -> dict:
    rng = np.random.default_rng(seed)
    a, b = int(lc.c["indptr"][texts[0] * SEQ]), int(lc.c["indptr"][(texts[-1] + 1) * SEQ])
    idx = np.sort(rng.choice(np.arange(a, b), size=max(1, (b - a) // 10), replace=False))
    return lc.mask(texts, idx, "cpu")


def test_version_ii_matches_the_authors_run_adv_pgd(tiny):
    model, ids, prep, cache, meta, lc = tiny
    tok = prep.ids[0:1]
    labels = lc.dense([0], "cpu")
    fm = _freed_mask(lc, [0], 3)
    from param_decomp.utils.general_utils import bf16_autocast

    with torch.no_grad(), bf16_autocast():
        target = model(tok)
    r = PA.reference_check(model, tok, labels, fm, target, seed=11, fill_seed=12)
    assert r["freed"]["passes"] and r["original"]["passes"] and r["identity_empty_freed_set"]["passes"], r
    assert r["freed"]["authors_reproducible"]
    # plan 7, item 1: the freed arm's harms leave only under "sealed"
    assert {"harm_ours", "harm_theirs"} <= set(r["sealed"]["freed_arm_harm"]) and r["freed"]["harm_difference_ours_minus_theirs"] == 0.0
    from vpd_audit_2 import pilot_b as PB

    assert PB.freed_harm_leaves({k: v for k, v in r.items() if k != "sealed"}) == []


def test_seal_prerequisites_moves_the_freed_harm():
    """Plan 7, item 4: both the current record and the pilot's committed one split into an open part without a freed-arm
    harm (the difference and the flag kept) and a sealed part with both harms; a leak is caught."""
    from vpd_audit_2 import pilot_b as PB

    gap = {"bf16": {"harm_original_fill": 0.4455}, "fp32": {"harm_original_fill": 0.4454}}
    ident = {"G": {"fill": 0.0, "zero": 0.0}, "J": {"fill": 0.0, "zero": 0.0}, "passes": True}
    old = {"v2_reference_check": {"freed": {"passes": True, "freed_entries": 10, "n_steps": 4, "harm_ours": 1.25, "harm_theirs": 1.25,
                                            "harm_abs_difference": 0.0}, "original": {"passes": True, "n_steps": 4},
                                  "identity_empty_freed_set": ident, "passes": True},
           "v2_precision_gap_original_arm": gap, "g3_controls_reproduced": {"all_on": {"max_abs_difference": 0.0}}, "environment": {}}
    new = {**old, "v2_reference_check": {**old["v2_reference_check"],
                                         "freed": {"passes": True, "freed_entries": 10, "n_steps": 4, "harm_difference_ours_minus_theirs": 0.0},
                                         "sealed": {"freed_arm_harm": {"harm_ours": 1.25, "harm_theirs": 1.25}}}}
    for rec in (old, new):
        assert PB.freed_harm_leaves(rec) != []
        pub, sealed = PB.seal_prerequisites(rec, {"arm": "nominal", "seed": 1})
        assert PB.freed_harm_leaves(pub) == [] and "1.25" not in json.dumps(pub)
        assert sealed["freed_arm_harm"]["harm_ours"] == 1.25 and sealed["freed_arm_harm"]["seed"] == 1
        assert pub["v2_reference_check"]["freed"]["harm_difference_ours_minus_theirs"] == 0.0 and pub["v2_reference_check"]["freed"]["passes"]
        assert pub["v2_precision_gap_original_arm"] == gap
    leak = {**new, "v2_reference_check": {**new["v2_reference_check"], "freed": {**new["v2_reference_check"]["freed"], "harm_fill": 1.25}}}
    with pytest.raises(AssertionError, match="freed-arm harm"):
        PB.seal_prerequisites(leak, {})


def test_committed_prerequisites_hold_no_freed_arm_harm():
    """Plan 7, item 4: the committed `prerequisites.json` holds no freed-arm harm; the moved values sit in `sealed/`
    (checked by key only, never read here)."""
    from vpd_audit_2 import pilot_b as PB

    pb = env.REPO_ROOT / "results" / "s4_pilot" / "part_b"
    prereq = json.load(open(pb / "prerequisites.json"))
    assert PB.freed_harm_leaves(prereq) == []
    assert prereq["v2_reference_check"]["passes"] and "harm_difference_ours_minus_theirs" in prereq["v2_reference_check"]["freed"]
    assert set(json.load(open(pb / "sealed" / PB.SEALED_PREREQ))["freed_arm_harm"]) >= {"harm_ours", "harm_theirs"}


def test_version_ii_empty_arm_gives_zero_g_and_j(tiny):
    model, ids, prep, cache, meta, lc = tiny
    tok = prep.ids[1:2]
    labels = lc.dense([1], "cpu")
    fm = _freed_mask(lc, [1], 5)
    empty = {k: torch.zeros_like(v) for k, v in fm.items()}
    alive = {k: v > 0 for k, v in labels.items()}
    out = PA.text_run(model, tok, labels, {"original": empty, "empty": empty, "freed": fm}, prep.target_out[1:2],
                      PA.draw_start(labels, 21), PA.draw_fill(alive, 22), "fp32")
    assert all(v == 0.0 for v in out["G"]["empty"].values()) and all(v == 0.0 for v in out["J"]["empty"].values())
    assert np.isfinite(out["G"]["freed"]["fill"]) and np.isfinite(out["J"]["freed"]["fill"])


def test_freed_label_harness_identities(tiny):
    model, ids, prep, cache, meta, lc = tiny
    texts = list(range(16))
    labels = lc.dense(texts, "cpu")
    p16 = FL.prepare(model, ids[:16], labels, "cpu")
    fm = _freed_mask(lc, texts, 7)
    empty = {k: torch.zeros_like(v) for k, v in fm.items()}
    lay = [(k, model.module_to_c[k]) for k in model.target_module_paths]
    g = torch.Generator().manual_seed(1)
    starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay} for s in (1, 2)}
    out = FL.set_job(model, p16, labels, {"original": empty, "empty": empty, "freed": fm}, starts, lay, "cpu", log=lambda *_: None)
    for s in (1, 2):
        for n in FL.READINGS:
            assert out["harm"][f"empty|s{s}|n{n}"] == out["harm"][f"original|s{s}|n{n}"]
            assert all(v == 0.0 for v in out["J"][f"empty|s{s}|n{n}"])
            assert len(out["harm"][f"freed|s{s}|n{n}"]) == 16
    # the scoring path builds the same masks as the authors' forward
    from param_decomp.metrics.pgd_utils import _construct_mask_infos_from_adv_sources
    from vpd_audit_2 import pilot as PL

    src = PL.unflatten(np.concatenate([starts[1][k].reshape(-1) for k, _ in lay]), lay)
    t = {k: torch.from_numpy(v) for k, v in src.items()}
    with torch.no_grad():
        ref = model(p16.ids, mask_infos=_construct_mask_infos_from_adv_sources(t, labels, p16.weight_deltas, "all", labels[next(iter(labels))].shape[:-1]))
    assert torch.equal(FL.adv_logits(model, p16, labels, src), ref)
    st = FL.stochastic_job(model, p16, labels, {"original": empty, "empty": empty}, [f"v{i}" for i in texts], 2, "cpu")
    assert st["empty|d0"] == st["original|d0"] and st["empty|d1"] == st["original|d1"]


def test_j_equals_scoring_with_the_freed_masks_zeroed_explicitly(tiny):
    """Plan 7, item 11 (Riku): J at the original arm's endpoint equals scoring that endpoint's masks, built by the authors'
    `_construct_mask_infos_from_adv_sources` with the deltas, then the freed entries set to 0 by index assignment, minus
    the endpoint's own harm; bit for bit, at every reading."""
    from param_decomp.metrics.pgd_utils import _construct_mask_infos_from_adv_sources

    from vpd_audit_2 import pilot as PL

    model, ids, prep, cache, meta, lc = tiny
    texts = list(range(16))
    labels = lc.dense(texts, "cpu")
    p16 = FL.prepare(model, ids[:16], labels, "cpu")
    fm = _freed_mask(lc, texts, 9)
    empty = {k: torch.zeros_like(v) for k, v in fm.items()}
    lay = [(k, model.module_to_c[k]) for k in model.target_module_paths]
    g = torch.Generator().manual_seed(4)
    start = {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay}
    out = FL.set_job(model, p16, labels, {"original": empty, "freed": fm}, {1: start}, lay, "cpu", log=lambda *_: None)
    hook = A.SaveHook(steps=FL.READINGS, thresholds=())
    A.run(model, p16, start, FL.N_STEPS, FL.STEP, labels=labels, save_hook=hook, device="cpu")
    batch_dims = labels[next(iter(labels))].shape[:-1]
    for n in FL.READINGS:
        src = {k: torch.from_numpy(v) for k, v in PL.unflatten(hook.saved[f"step_{n}"], lay).items()}
        mi = _construct_mask_infos_from_adv_sources(src, labels, p16.weight_deltas, "all", batch_dims)
        for k in mi:
            cm = mi[k].component_mask.clone()
            cm[fm[k]] = 0.0
            mi[k].component_mask = cm
        with torch.no_grad():
            j = FL.kl64_per_text(model(p16.ids, mask_infos=mi), p16.target_out) - np.array(out["harm"][f"original|s1|n{n}"])
        assert j.tolist() == out["J"][f"freed|s1|n{n}"], n
        assert np.any(j != 0.0)


def test_removal_harness_reproduces_g3_controls_and_runs_float64(tiny):
    model, ids, prep, cache, meta, lc = tiny
    text_ids = [f"v{i}" for i in range(32)]
    out = g3.run_g3(model, ids, text_ids, 1e-6, device="cpu", log=lambda *_: None)
    draw = A.stochastic_draw(list(prep.labels), model.module_to_c, text_ids, 1, 0, SEQ, routing=True)
    h = R.Harness(model, ids, lc.dense(list(range(32)), "cpu"), draw, "cpu")
    rep = R.reproduce_g3_controls(h, out["controls"]["chosen"], out["controls"]["backgrounds"])
    assert rep["passes"], rep
    k = model.target_module_paths[0]
    e32 = h.effects_with_base("all_on", 3, [(5, k, 0, 0.0), (7, k, 1, 0.0)], 4)
    h.set_precision("fp64")
    e64 = h.effects_with_base("at_labels", 3, [(5, k, 0, 1.0)], 4)
    es = h.effects_with_base("stochastic", 3, [(5, k, 0, 0.0)], 4)
    h.release()
    assert len(e32) == 2 and np.isfinite(e64[0]) and np.isfinite(es[0])
    assert next(model.parameters()).dtype == torch.float32


def test_b1_and_b2_jobs_run_on_a_tiny_cache(tiny, tmp_path):
    """The container jobs end to end on the tiny model, from a cache written in the fresh path's format."""
    import json

    from vpd_audit_2 import pilot_b as PB

    model, ids, prep, cache, meta, lc = tiny
    meta = {**meta, "seq_len": SEQ, "sha256": {k: P.sha256_array(v) for k, v in cache.items()}}
    np.savez(tmp_path / "CQ_fp32.npz", **cache)
    json.dump(meta, open(tmp_path / "CQ_fp32.json", "w"))
    texts = [f"v{i}" for i in range(32)]
    nominal = {str(i): CP.nominal_set(cache, i, texts[i], seq_len=SEQ) for i in range(32)}
    np.savez(tmp_path / "nominal.npz", **{f"{i}|{a}": v[a] for i, v in nominal.items() for a in PB.FREED_ARMS})
    lay = [(k, model.module_to_c[k]) for k in model.target_module_paths]
    g = torch.Generator().manual_seed(2)
    starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay} for s in (1, 2)}
    b1 = PB.b1_partition_job(model, ids, [[0, 1, 2, 3], [4, 5, 6, 7]], tmp_path, starts, lay, log=lambda *_: None, device="cpu")
    assert set(b1) == {"set0", "set1"} and len(b1["set0"]["harm"]["nominal|s1|n20"]) == 4
    v2 = PB.b1_v2_stoch_job(model, ids, texts, tmp_path, n_seeds=2, n_draws=2, log=lambda *_: None, device="cpu")
    assert len(v2["v2"]) == 64 and len(v2["stochastic"]["nominal|d1"]) == 32
    alive = np.ones(sum(model.module_to_c.values()), dtype=bool)
    alive[::3] = False
    mods = sorted(model.module_to_c)
    b2 = PB.b2_job(model, ids, texts, tmp_path, alive, [[1, mods[0], 0, 0], [0, mods[1], 0, 2], [1, mods[2], 9, 3]], 3, log=lambda *_: None, device="cpu")
    assert next(model.parameters()).dtype == torch.float32
    for key, lst in b2["triples"].items():
        for bg in ("all_on", "at_labels", "stochastic"):
            assert len(b2["effects"][key][bg]) == len(lst) and all(e is not None for e in b2["effects"][key][bg])


def test_original_arm_check_passes_and_has_teeth(tiny, tmp_path):
    """Report 3, Daniel's check, on the tiny model. On all 32 texts (the batch the cache's labels came from) the harness's
    original arm equals the plain loop bitwise at 20 steps. On a set of 16 it equals the plain loop given the cache's
    labels (on CPU the tiny model's labels differ in the last bits between a 32- and a 16-text batch). The rerun equals a
    stored B1 partition job's original arm, and a one-ulp change to the stored value fails it."""
    import json

    from vpd_audit_2 import pilot_b as PB

    model, ids, prep, cache, meta, lc = tiny
    meta = {**meta, "seq_len": SEQ, "sha256": {k: P.sha256_array(v) for k, v in cache.items()}}
    np.savez(tmp_path / "CQ_fp32.npz", **cache)
    json.dump(meta, open(tmp_path / "CQ_fp32.json", "w"))
    texts = [f"v{i}" for i in range(32)]
    nominal = {str(i): CP.nominal_set(cache, i, texts[i], seq_len=SEQ) for i in range(32)}
    np.savez(tmp_path / "nominal.npz", **{f"{i}|{a}": v[a] for i, v in nominal.items() for a in PB.FREED_ARMS})
    lay = [(k, model.module_to_c[k]) for k in model.target_module_paths]
    g = torch.Generator().manual_seed(3)
    start = {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in lay}
    show = lambda r: {k: v for k, v in r.items() if not k.startswith(("record_plain", "per_text_harm"))}  # noqa: E731
    r32 = PB.original_arm_check(model, ids, tmp_path, start, lay, None, list(range(32)), s=1, n=20, device="cpu")
    assert r32["passes_as_stated"] and r32["inputs"]["labels_equal"], show(r32)
    rows = list(range(16))
    b1 = PB.b1_partition_job(model, ids, [rows], tmp_path, {1: start}, lay, log=lambda *_: None, device="cpu")["set0"]
    stored = {"harm": {f"n{m}": b1["harm"][f"original|s1|n{m}"] for m in FL.READINGS}, "record": b1["records"]["original|s1"]}
    r = PB.original_arm_check(model, ids, tmp_path, start, lay, stored, rows, s=1, n=20, device="cpu")
    assert r["passes_given_cache_labels"] and all(r["rerun_equals_b1"].values()), show(r)
    assert r["passes_as_stated"] == (r["inputs"]["labels_equal"] and r["plain"]["all_equal"])
    bad = {**stored, "harm": {**stored["harm"], "n20": [float(np.nextafter(stored["harm"]["n20"][0], 1.0))] + stored["harm"]["n20"][1:]}}
    r2 = PB.original_arm_check(model, ids, tmp_path, start, lay, bad, rows, s=1, n=20, device="cpu")
    assert not r2["passes_given_cache_labels"] and not r2["rerun_equals_b1"]["n20"]
