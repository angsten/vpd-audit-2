"""Session 4, plan 6, Part B: question 1's nuisance scales on the 32 calibration texts CQ (`sessions/004/engineering/plan_6.md`,
Sections 4 and 6). The container jobs:

  - `prep_job`: CQ's float32 labels with z (the fresh path); the nominal sets; CQ's sums, per-label prices, and T_i per arm
    against Q's tuples (item 5), with the price-path test on two Q texts outside Q1; version (ii)'s reference check (item 6);
    the removal harness's reproduction of G3's positive controls (item 8); B3's timings (the sweep and pruning on one
    text, float32 all on, times only; the float64 single-label passes; [N8] on this GPU).
  - `n8_job`: [N8], the 16-text float32 shared-source search's seconds per step, on another GPU type.
  - `b1_partition_job`: versions (i) and (iii) on one partition's two sets, 4 arms, 8 seeds.
  - `b1_v2_stoch_job`: version (ii) on every text, 4 arms, 8 seeds; the stochastic half, 8 draws.
  - `b2_job`: removal effects of label-zero components in the strata given.

Sealing (Section 3): B1's harms leave the job only in its return value, which the local entrypoint writes to the sealed
file; nothing here logs a harm, a G, a J, or a V. B3.1 keeps times only: its effects are computed and dropped.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import adversary as A

ARMS = ("original", "nominal", "saturated", "unsaturated")
FREED_ARMS = ARMS[1:]


def _sync(device: str) -> None:
    import torch

    if device == "cuda":
        torch.cuda.synchronize()


def load_cq(vol: Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    from vpd_audit_2 import prices

    return prices.load_cache(vol / "CQ_fp32.npz")


def open_lc(vol: Path) -> Any:
    """CQ's label cache from the volume, with its sequence length (512 for CQ; smaller for the tiny model's tests)."""
    from vpd_audit_2.label_cache import LabelCache

    cache, meta = load_cq(vol)
    return LabelCache(cache, meta, int(meta.get("seq_len", 512)))


def load_nominal(vol: Path, n: int) -> dict[str, dict[str, np.ndarray]]:
    with np.load(vol / "nominal.npz") as z:
        return {str(i): {a: z[f"{i}|{a}"] for a in FREED_ARMS} for i in range(n)}


def arm_entries(nominal: dict[str, Any], texts: list[int]) -> dict[str, np.ndarray]:
    """The arms' entries restricted to the given texts (global CQ cache entry indices)."""
    out = {"original": np.zeros(0, np.int64)}
    for arm in FREED_ARMS:
        out[arm] = np.concatenate([np.asarray(nominal[str(i)][arm], dtype=np.int64) for i in texts])
    return out


# ----------------------------------------------------------------------------- prices for Q texts (plan 7, item 8)


def q_stored_path_check(cache_dir: Path, S_Q: np.ndarray, tuples: np.ndarray, C: Any, q_text_ids: list[str], q_free_texts: list[int],
                        expected: dict[int, float] | None, device: str = "cuda", ids_sha256: str | None = None) -> dict[str, Any]:
    """On Q texts outside Q1, T_i from the stored path (`cq_prices.QPrices`: the stored S row, Delta from Q's full cache),
    with every seventh of the text's entries freed, as the pilot's price-path test froze them; against `expected` (the
    pilot's stored-path values in `prep.json`), exactly. Beside it: the pilot's construction (Delta from the text's own
    sub-cache), whether the two Deltas are bitwise equal, and that the external path refuses the text."""
    from vpd_audit_2 import cq_prices as CP
    from vpd_audit_2 import prices

    qcache, qmeta = prices.load_cache(cache_dir / "labels" / "Q_fp32.npz")
    qp = CP.QPrices(S_Q, tuples, C, q_text_ids, qcache, qmeta, device, ids_sha256=ids_sha256)
    ext = CP.ExternalPricer(S_Q, tuples, C, q_text_ids, device)
    tests = []
    for i in q_free_texts:
        tid = q_text_ids[i]
        _, e_sub, a = CP.text_sums(qcache, qmeta, i, C)
        n = e_sub.comp.size
        idx = a + np.arange(0, n, 7)
        T_new = qp.saved_price_T(tid, idx)
        T_sub = qp.pricer.saved_price_T(i, e_sub.comp[idx - a], e_sub.delta[idx - a])  # the pilot's stored-path construction
        try:
            ext.saved_price_T(S_Q[i], np.zeros(0, np.int64), np.zeros(0), text_id=tid)
            refused = False
        except CP.QTextOnExternalPath:
            refused = True
        rec = {"q_text": i, "text_id": tid, "freed_entries": int(idx.size), "T_stored_path": T_new, "T_stored_path_sub_cache_delta": T_sub,
               "components_equal": bool(np.array_equal(qp.e.comp[a : a + n], e_sub.comp)),
               "delta_full_equals_sub_cache": bool(np.array_equal(qp.e.delta[a : a + n], e_sub.delta)),
               "delta_entries_unequal": int((qp.e.delta[a : a + n] != e_sub.delta).sum()), "refused_on_external_path": refused}
        if expected is not None:
            rec.update({"T_expected": expected[i], "equals_expected": T_new == expected[i], "sub_cache_equals_expected": T_sub == expected[i]})
        tests.append(rec)
    del qcache, qp
    passes = all(t["refused_on_external_path"] for t in tests) and (expected is None or all(t["equals_expected"] for t in tests))
    return {"texts": tests, "passes": passes, "rows_verified_by_ids_sha256": ids_sha256 is not None,
            "rule": "T from the stored path (stored S, Delta from Q's full cache) equals the pilot's stored-path T exactly"}


# ----------------------------------------------------------------------------- sealing the prerequisites (plan 7, item 1)

SEALED_PREREQ = "v2_reference_check_freed_harm.json"
_ARM_KEYS = ("freed", "nominal", "saturated", "unsaturated")


def freed_harm_leaves(obj: Any, path: tuple[str, ...] = ()) -> list[str]:
    """The leaves of an open record that could carry a freed arm's harm: any key "harm_ours" or "harm_theirs", and any
    float under a key naming a freed arm (or "freed"), except the reference check's difference (ours minus theirs) and
    the empty freed set's exact zeros. Booleans and integer counts are not harms."""
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("harm_ours", "harm_theirs"):
                out.append("/".join(path + (k,)))
            else:
                out += freed_harm_leaves(v, path + (str(k),))
    elif isinstance(obj, list):
        for j, v in enumerate(obj):
            out += freed_harm_leaves(v, path + (str(j),))
    elif isinstance(obj, float) and any(any(a in p for a in _ARM_KEYS) for p in path):
        if path[-1] != "harm_difference_ours_minus_theirs" and not ("identity_empty_freed_set" in path and obj == 0.0):
            out.append("/".join(path))
    return out


def seal_prerequisites(prereq: dict[str, Any], context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split the prerequisites record into its open part (`prerequisites.json`) and its sealed part (`sealed/`): version
    (ii)'s reference check's freed-arm harms go to the sealed part, and the open part keeps their difference (ours minus
    theirs) and the pass flag. Takes the current record (the harms under "sealed") or the pilot's record as committed at
    a3b8ec2 (the harms inside "freed"). Fails if the open part would still hold a freed-arm harm."""
    import copy

    pub = copy.deepcopy(prereq)
    rc = pub["v2_reference_check"]
    sealed = rc.pop("sealed", None)
    fr = rc["freed"]
    if "harm_ours" in fr:  # the pilot's record as committed
        assert sealed is None
        h_o, h_t = fr.pop("harm_ours"), fr.pop("harm_theirs")
        fr.pop("harm_abs_difference", None)
        fr["harm_difference_ours_minus_theirs"] = h_o - h_t
        sealed = {"freed_arm_harm": {"harm_ours": h_o, "harm_theirs": h_t, "precision": "bf16", "form": "fill"}}
    assert sealed is not None and "harm_difference_ours_minus_theirs" in fr, "no freed-arm harm to seal"
    sealed["freed_arm_harm"].update(context)
    leaks = freed_harm_leaves(pub)
    assert not leaks, f"the open record still holds a freed-arm harm: {leaks}"
    return pub, sealed


def time_search_step(model: Any, prep: A.Prepared, start: dict[str, np.ndarray], device: str, n: int = 10) -> dict[str, float]:
    A.run(model, prep, start, 2, 0.1, device=device)  # warm-up
    _sync(device)
    t0 = time.time()
    A.run(model, prep, start, n, 0.1, device=device)
    _sync(device)
    return {"seconds_per_step": (time.time() - t0) / n, "steps_timed": n}


# ----------------------------------------------------------------------------- preparation


def prep_job(model: Any, cq_ids: np.ndarray, cq_texts: list[str], q_free_texts: list[int], vol: Path, cache_dir: Path,
             g3_controls: dict[str, Any], start1: dict[str, np.ndarray], tuples_sha: str, q_text_ids: list[str], log: Any = print,
             device: str = "cuda") -> dict[str, Any]:
    import json

    import torch

    from vpd_audit_2 import cq_prices as CP
    from vpd_audit_2 import labels as L
    from vpd_audit_2 import prices
    from vpd_audit_2 import pruning_adv as PA
    from vpd_audit_2 import removal as R
    from vpd_audit_2.label_cache import LabelCache
    from vpd_audit_2.manifest import seed_of

    out: dict[str, Any] = {}
    vol.mkdir(parents=True, exist_ok=True)
    # 1. CQ's labels, the fresh float32 path with z
    meta = L.fresh_cache(model, cq_ids, vol / "CQ_fp32.npz", {"pool": "CQ", "texts": cq_texts}, log=log, band=False)
    cache, meta = load_cq(vol)
    lc = LabelCache(cache, meta, 512)
    prep = A.prepare(model, cq_ids, "fp32", device=device)
    dense = lc.dense(list(range(32)), device)
    out["cq_cache"] = {"sha256": meta["sha256"], "labels_per_position": meta["mean_count_above_0_per_position"],
                       "dense_equals_prepare_labels": all(torch.equal(dense[k], prep.labels[k]) for k in prep.labels),
                       "count_z_above_1": meta["count_z_above_1"], "nnz": meta["nnz"]}
    # 2. the nominal sets
    nominal = {str(i): CP.nominal_set(cache, i, cq_texts[i]) for i in range(32)}
    out["nominal"] = {"per_text": {str(i): {a: int(v[a].size) for a in FREED_ARMS} for i, v in nominal.items()},
                      "total": {a: int(sum(v[a].size for v in nominal.values())) for a in FREED_ARMS}, "labels_above_zero": int(cache["indptr"][-1])}
    np.savez(vol / "nominal.npz", **{f"{i}|{a}": v[a] for i, v in nominal.items() for a in FREED_ARMS})
    # 3. prices against Q's tuples and sums
    C = prices.constants()
    tuples = prices.tuple_sets(1024)["W16_K256"]
    assert prices.sha256_array(tuples) == tuples_sha, "not the committed deciding tuples"
    S_Q = np.load(cache_dir / "prices" / "Q_fp32_S.npy")
    ext = CP.ExternalPricer(S_Q, tuples, C, q_text_ids, device)
    S_CQ, per_label, T = [], np.zeros(cache["values"].size), {}
    for i in range(32):
        S_i, e, a = CP.text_sums(cache, meta, i, C)
        S_CQ.append(S_i)
        per_label[a : a + e.comp.size] = ext.price_labels(S_i, e.comp, e.delta, text_id=cq_texts[i])
        T[str(i)] = CP.arm_T(ext, cache, meta, i, nominal[str(i)], C, text_id=cq_texts[i])
    np.save(vol / "S_CQ.npy", np.stack(S_CQ))
    np.save(vol / "price_CQ.npy", per_label)
    out["T"] = T
    out["prices_cq"] = {"sha256_S": prices.sha256_array(np.stack(S_CQ)), "sha256_per_label": prices.sha256_array(per_label),
                        "per_label_percentiles": prices.percentiles(per_label, (1, 5, 50, 95))}
    # 4. Q texts outside Q1 from the stored path (plan 7, item 8). The pilot ran this step at b26f56d as a comparison of the
    #    external path with the stored path on these texts; a Q text on the external path is now refused.
    out["price_path_test"] = q_stored_path_check(cache_dir, S_Q, tuples, C, q_text_ids, q_free_texts, None, device)
    log(f"[pilot-b] prices: Q texts from the stored path, external path refused: {out['price_path_test']['passes']}")
    # 5. version (ii)'s reference check, bf16, on CQ's first text with its nominal set
    from param_decomp.utils.general_utils import bf16_autocast

    tok = prep.ids[0:1]
    lab0 = lc.dense([0], device)
    fm0 = lc.mask([0], nominal["0"]["nominal"], device)
    with torch.no_grad(), bf16_autocast():
        target_bf16 = model(tok)
    s_seed, f_seed = seed_of("pruning-start", 1, cq_texts[0]), seed_of("pruning-fill", 1, cq_texts[0])
    out["v2_reference_check"] = PA.reference_check(model, tok, lab0, fm0, target_bf16, s_seed, f_seed)
    alive0 = {k: v > 0 for k, v in lab0.items()}
    gap = {}
    for prec, tgt in (("bf16", target_bf16), ("fp32", prep.target_out[0:1])):
        tr = PA.text_run(model, tok, lab0, {"original": {k: torch.zeros_like(v) for k, v in fm0.items()}, "nominal": fm0}, tgt,
                         PA.draw_start(lab0, s_seed), PA.draw_fill(alive0, f_seed), prec)
        gap[prec] = {"harm_original_fill": tr["harm"]["original"]["fill"]}
    out["v2_precision_gap_original_arm"] = gap
    log(f"[pilot-b] version (ii) reference check: {out['v2_reference_check']['passes']}")
    # 6. the removal harness against G3's positive controls (float32)
    draw = A.stochastic_draw(list(dense), model.module_to_c, cq_texts, 1, 0, 512, routing=True)
    h = R.Harness(model, cq_ids, dense, draw, device)
    out["g3_controls_reproduced"] = R.reproduce_g3_controls(h, g3_controls["chosen"], g3_controls["backgrounds"])
    log(f"[pilot-b] G3 controls reproduced: {out['g3_controls_reproduced']['passes']}")
    # 7. B3: timings, times only
    out["b3"] = b3_timings(model, h, lc, per_label, cq_ids, start1, device, log)
    h.release()
    del h, draw
    with open(vol / "prep_summary.json", "w") as f:
        json.dump({k: v for k, v in out.items() if k in ("cq_cache", "nominal", "prices_cq")}, f, indent=1)
    return out


def b3_timings(model: Any, h: Any, lc: Any, per_label: np.ndarray, cq_ids: np.ndarray, start1: dict[str, np.ndarray], device: str,
               log: Any = print) -> dict[str, Any]:
    """B3.1 (sweep and deciding-order pruning, text 0, positions 0..31, all on, float32): times only. B3.3: float64 single-
    label passes. B3.2: [N8] on this GPU."""
    from vpd_audit_2 import freed_label as FL

    out: dict[str, Any] = {}
    h.set_precision("fp32")
    i = 0
    n_sweep = n_prune = 0
    t_sweep = t_prune = 0.0
    for t in range(32):
        a, b = int(lc.c["indptr"][t]), int(lc.c["indptr"][t + 1])
        _, _, li, cl = lc.locate(np.arange(a, b))
        changes = [(t, lc.order[li[k]], int(cl[k]), 0.0) for k in range(b - a)]
        _sync(device)
        t0 = time.time()
        eff = h.effects_with_base("all_on", i, changes, 32)
        _sync(device)
        t_sweep += time.time() - t0
        n_sweep += len(changes)
        order = np.argsort(np.asarray(eff) / per_label[a:b], kind="stable")
        _sync(device)
        t0 = time.time()
        for c0 in range(0, len(order), 31):
            rows = [(i, [])] + [(i, [changes[k] for k in order[: c1 + 1]]) for c1 in range(c0, min(c0 + 31, len(order)))]
            lg = h.logits("all_on", rows)
            _ = [h.effect(lg[r], lg[0], i, t) for r in range(1, len(rows))]
            del lg
        _sync(device)
        t_prune += time.time() - t0
        n_prune += len(order)
        del eff
    out["b3_1"] = {"text": 0, "positions": [0, 31], "background": "all on, float32", "sweep": {"removals": n_sweep, "seconds": t_sweep,
                   "seconds_per_removal": t_sweep / n_sweep}, "pruning": {"removals": n_prune, "seconds": t_prune, "seconds_per_removal": t_prune / n_prune},
                   "extrapolated_hours_for_16_texts_x_512_positions": (t_sweep + t_prune) / 32 * 512 * 16 / 3600,
                   "note": "times only: no effect, set, or share is kept"}
    log(f"[pilot-b] B3.1: sweep {t_sweep / n_sweep * 1000:.1f} ms, pruning {t_prune / n_prune * 1000:.1f} ms per removal")
    h.set_precision("fp64")
    k0 = lc.order[0]
    b33 = {}
    for bg, val in (("at_labels", 1.0), ("stochastic", 0.0)):
        for rows in (2, 16):
            ch = [(100 + r, k0, r, val) for r in range(rows - 1)]
            h.effects_with_base(bg, 1, ch, rows)  # warm-up
            _sync(device)
            t0 = time.time()
            h.effects_with_base(bg, 1, ch, rows)
            _sync(device)
            dt = time.time() - t0
            b33[f"{bg}|rows{rows}"] = {"seconds_per_pass": dt, "seconds_per_removal": dt / (rows - 1)}
    out["b3_3_float64"] = b33
    h.set_precision("fp32")
    labels16 = lc.dense(list(range(16)), device)
    p16 = FL.prepare(model, cq_ids[:16], labels16, device)
    out["n8"] = time_search_step(model, p16, start1, device)
    log(f"[pilot-b] N8 on this GPU: {out['n8']['seconds_per_step']:.3f} s per step")
    return out


def n8_job(model: Any, cq_ids: np.ndarray, vol: Path, start1: dict[str, np.ndarray], device: str = "cuda") -> dict[str, Any]:
    from vpd_audit_2 import freed_label as FL

    lc = open_lc(vol)
    p16 = FL.prepare(model, cq_ids[:16], lc.dense(list(range(16)), device), device)
    return time_search_step(model, p16, start1, device)


# ----------------------------------------------------------------------------- B1


def b1_partition_job(model: Any, cq_ids: np.ndarray, sets: list[list[int]], vol: Path, starts: dict[int, dict[str, np.ndarray]],
                     lay: list[tuple[str, int]], log: Any = print, device: str = "cuda", tag: str = "") -> dict[str, Any]:
    from vpd_audit_2 import freed_label as FL

    lc = open_lc(vol)
    nominal = load_nominal(vol, lc.n_texts)
    out = {}
    for si, rows in enumerate(sets):
        labels = lc.dense(rows, device)
        prep = FL.prepare(model, cq_ids[rows], labels, device)
        ents = arm_entries(nominal, rows)
        masks = {a: lc.mask(rows, ents[a], device) for a in ARMS}
        out[f"set{si}"] = {"texts": rows, **FL.set_job(model, prep, labels, masks, starts, lay, device, log=log, tag=f"{tag} set{si}")}
    return out


def b1_v2_stoch_job(model: Any, cq_ids: np.ndarray, cq_texts: list[str], vol: Path, n_seeds: int = 8, n_draws: int = 8, log: Any = print,
                    device: str = "cuda") -> dict[str, Any]:
    import torch

    from vpd_audit_2 import freed_label as FL
    from vpd_audit_2 import pruning_adv as PA
    from vpd_audit_2.manifest import seed_of

    lc = open_lc(vol)
    n = lc.n_texts
    nominal = load_nominal(vol, n)
    labels = lc.dense(list(range(n)), device)
    prep = FL.prepare(model, cq_ids, labels, device)
    out: dict[str, Any] = {"v2": {}, "v2_seconds": {}}
    for i in range(n):
        tok = prep.ids[i : i + 1]
        lab = {k: v[i : i + 1] for k, v in labels.items()}
        alive = {k: v > 0 for k, v in lab.items()}
        arms = {"original": {k: torch.zeros_like(v) for k, v in alive.items()}}
        arms.update({a: lc.mask([i], nominal[str(i)][a], device) for a in FREED_ARMS})
        t0 = time.time()
        for s in range(1, n_seeds + 1):
            start = PA.draw_start(lab, seed_of("pruning-start", s, cq_texts[i]))
            fill = PA.draw_fill(alive, seed_of("pruning-fill", s, cq_texts[i]))
            out["v2"][f"t{i}|s{s}"] = PA.text_run(model, tok, lab, arms, prep.target_out[i : i + 1], start, fill, "fp32")
        out["v2_seconds"][str(i)] = time.time() - t0
        if i % 8 == 7:
            log(f"[b1] version (ii): text {i + 1} of {n}")
    masks = {a: lc.mask(list(range(n)), arm_entries(nominal, list(range(n)))[a], device) for a in ARMS}
    t0 = time.time()
    out["stochastic"] = FL.stochastic_job(model, prep, labels, masks, cq_texts, n_draws, device)
    out["stochastic_seconds"] = time.time() - t0
    log("[b1] stochastic half done")
    return out


# ----------------------------------------------------------------------------- B2


def b2_strata(model: Any, alive_global: np.ndarray, offsets: dict[str, int], m2c: dict[str, int]) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Per matrix: the weight-norm decile of each component (equal-count by rank over all its components, ties by index)."""
    from vpd_audit.weight_norms import weight_norms

    norms, nmeta = weight_norms(model)
    dec = {}
    for k in sorted(m2c):
        o, C = offsets[k], m2c[k]
        order = np.lexsort((np.arange(C), norms[o : o + C]))
        d = np.empty(C, dtype=np.int64)
        d[order] = (10 * np.arange(C)) // C
        dec[k] = d
    return dec, {"weight_norms_sha256": nmeta["sha256"]}


def b2_sample(lc: Any, labels_np: dict[str, np.ndarray], dec: dict[str, np.ndarray], alive_global: np.ndarray, offsets: dict[str, int],
              stratum: tuple[int, str, int, int], n: int, max_tries: int = 200_000) -> list[tuple[int, int, int]]:
    """n triples (text, position, component) with the label exactly zero, uniform over the stratum's eligible triples by
    rejection, seeded (master, "pilot-p4", stratum)."""
    from vpd_audit_2.manifest import seed_of

    alive, k, d, blk = stratum
    comps = np.flatnonzero((dec[k] == d) & (alive_global[offsets[k] : offsets[k] + dec[k].size] == bool(alive)))
    if comps.size == 0:
        return []
    rng = np.random.default_rng(seed_of("pilot-p4", f"{'alive' if alive else 'dead'}|{k}|{d}|{blk}"))
    got: list[tuple[int, int, int]] = []
    seen = set()
    block = lc.T // 4  # position blocks of 128 tokens on 512
    for _ in range(max_tries):
        if len(got) == n:
            break
        i, t, c = int(rng.integers(0, lc.n_texts)), int(blk * block + rng.integers(0, block)), int(comps[rng.integers(0, comps.size)])
        if (i, t, c) in seen or labels_np[k][i, t, c] != 0:
            continue
        seen.add((i, t, c))
        got.append((i, t, c))
    return got


def b2_job(model: Any, cq_ids: np.ndarray, cq_texts: list[str], vol: Path, alive_global: np.ndarray, strata: list[list], n_per: int,
           log: Any = print, device: str = "cuda") -> dict[str, Any]:
    from vpd_audit_2 import removal as R

    lc = open_lc(vol)
    offsets, m2c = lc.offsets, lc.m2c
    dense = lc.dense(list(range(lc.n_texts)), device)
    labels_np = {k: v.cpu().numpy() for k, v in dense.items()}
    dec, nmeta = b2_strata(model, alive_global, offsets, m2c)
    triples = {}
    for st in strata:
        key = f"{'alive' if st[0] else 'dead'}|{st[1]}|{st[2]}|{st[3]}"
        triples[key] = b2_sample(lc, labels_np, dec, alive_global, offsets, (st[0], st[1], st[2], st[3]), n_per)
    draw = A.stochastic_draw(list(dense), model.module_to_c, cq_texts, 1, 0, lc.T, routing=False)
    h = R.Harness(model, cq_ids, dense, draw, device)
    by_text: dict[int, list[tuple[str, int, int, str, int]]] = {}
    for key, lst in triples.items():
        k = key.split("|")[1]
        for j, (i, t, c) in enumerate(lst):
            by_text.setdefault(i, []).append((key, j, t, k, c))
    effects: dict[str, dict[str, list[float | None]]] = {key: {bg: [None] * len(lst) for bg in R.BACKGROUNDS} for key, lst in triples.items()}
    times = {}
    for bg, rows_per, val in (("all_on", 32, 0.0), ("at_labels", 16, 1.0), ("stochastic", 16, 0.0)):
        h.set_precision(R.PRECISION[bg])
        t0 = time.time()
        for i, lst in sorted(by_text.items()):
            eff = h.effects_with_base(bg, i, [(t, k, c, val) for _, _, t, k, c in lst], rows_per)
            for (key, j, _, _, _), e in zip(lst, eff):
                effects[key][bg][j] = e
        _sync(device)
        times[bg] = time.time() - t0
        log(f"[b2] {bg}: {sum(len(v) for v in by_text.values())} removals in {times[bg]:.0f} s")
    h.release()
    return {"triples": {k: [list(x) for x in v] for k, v in triples.items()}, "effects": effects, "seconds": times,
            "weight_norms": nmeta, "removal_value": {"all_on": 0.0, "at_labels": 1.0, "stochastic": 0.0}}


# ----------------------------------------------------------------------------- report 3: Daniel's check


def original_arm_check(model: Any, cq_ids: np.ndarray, vol: Path, start: dict[str, np.ndarray], lay: list[tuple[str, int]],
                       stored: dict[str, Any] | None, rows: list[int], s: int = 1, n: int = 20, device: str = "cuda") -> dict[str, Any]:
    """On one CQ set, the harness's original-label arm against the plain loop for one seed, bitwise at n steps.

    Harness: B1's path. `freed_label.prepare` (the cache's float32 labels, a float32 target and deltas), the original
    arm's all-false mask, `freed_label.set_job` (80 steps, read at 20, 40, 80). Its sources after step n come from a second
    run of the same call with the hook kept (`adversary.run` with the labels override), since `set_job` drops them.
    Plain: `adversary.prepare(..., "fp32")` (labels computed by the model on this batch of rows) and `adversary.run` for n
    steps, no override. Plain with the cache's labels: the same prepare, the cache's labels passed as the override; this
    separates the labels' source (the cache's labels come from one 32-text batch, `labels.CHUNK`) from everything else.
    Compared: the inputs, the harm record, the sources after step n, and each text's harm at n under the harness's
    scoring; and the harness rerun against B1's stored original-arm values (`stored`), when given. Original arm only."""
    import torch

    from vpd_audit_2 import freed_label as FL
    from vpd_audit_2 import pilot as P

    lc = open_lc(vol)
    labels = lc.dense(rows, device)
    prep_h = FL.prepare(model, cq_ids[rows], labels, device)
    empty = lc.mask(rows, np.zeros(0, np.int64), device)
    lab_h = {k: labels[k].masked_fill(empty[k], 0.0) for k in labels}
    t0 = time.time()
    sj = FL.set_job(model, prep_h, labels, {"original": empty}, {s: start}, lay, device, log=lambda *_: None)
    hook = A.SaveHook(steps=(n,), thresholds=())
    rh = A.run(model, prep_h, start, n, FL.STEP, labels=lab_h, save_hook=hook, device=device)
    src_h = hook.saved[f"step_{n}"]
    prep_p = A.prepare(model, cq_ids[rows], "fp32", device)
    rec_sj = sj["records"][f"original|s{s}"]
    harm_sj = sj["harm"][f"original|s{s}|n{n}"]
    harm_h = FL.kl64_per_text(FL.adv_logits(model, prep_h, lab_h, P.unflatten(src_h, lay)), prep_h.target_out)

    def compare(labels_override: dict[str, Any] | None) -> tuple[dict[str, Any], list[float], list[float]]:
        rp = A.run(model, prep_p, start, n, FL.STEP, labels=labels_override, device=device)
        src_p = np.concatenate([v.reshape(-1) for v in rp["sources"].values()])
        lab = prep_p.labels if labels_override is None else labels_override
        harm_p = FL.kl64_per_text(FL.adv_logits(model, prep_p, lab, P.unflatten(src_p, lay)), prep_p.target_out)
        r = {"record_equal": rh["record"] == rp["record"],
             "set_job_record_first_n_equal": rec_sj[:n] == rp["record"][:n],
             "set_job_record_step_n_equals_final": rec_sj[n] == rp["record"][n],
             "sources_equal": bool(np.array_equal(src_h, src_p)),
             "per_text_harm_equal": bool(np.array_equal(harm_h, harm_p)),
             "set_job_per_text_harm_equal": harm_sj == harm_p.tolist(),
             "record_max_abs_difference": float(np.max(np.abs(np.array(rh["record"]) - np.array(rp["record"])))),
             "sources_max_abs_difference": float(np.max(np.abs(src_h - src_p))),
             "per_text_harm_max_abs_difference": float(np.max(np.abs(harm_h - harm_p)))}
        r["all_equal"] = all(r[k] for k in ("record_equal", "set_job_record_first_n_equal", "sources_equal", "per_text_harm_equal",
                                            "set_job_per_text_harm_equal"))
        return r, rp["record"], harm_p.tolist()

    plain, rec_p, harm_p = compare(None)
    with_cache, _, _ = compare(lab_h)
    _sync(device)

    def eq(a: Any, b: Any) -> bool:
        return bool(torch.equal(a, b))

    diff = [(lab_h[k] != prep_p.labels[k]) for k in lab_h]
    inputs = {"labels_equal": all(eq(lab_h[k], prep_p.labels[k]) for k in lab_h) and list(lab_h) == list(prep_p.labels),
              "labels_entries_differing": int(sum(int(d.sum()) for d in diff)),
              "labels_entries_total": int(sum(d.numel() for d in diff)),
              "labels_max_abs_difference": float(max(float((lab_h[k] - prep_p.labels[k]).abs().max()) for k in lab_h)),
              "target_equal": eq(prep_h.target_out, prep_p.target_out),
              "weight_deltas_equal": all(eq(prep_h.weight_deltas[k], prep_p.weight_deltas[k]) for k in prep_h.weight_deltas)}
    out: dict[str, Any] = {"rows": list(rows), "seed": s, "n": n, "seconds": time.time() - t0, "inputs": inputs,
                           "plain": plain, "plain_with_cache_labels": with_cache,
                           "record_plain": rec_p, "per_text_harm_plain": harm_p, "per_text_harm_harness": harm_h.tolist()}
    if stored is not None:
        out["rerun_equals_b1"] = {f"n{m}": sj["harm"][f"original|s{s}|n{m}"] == stored["harm"][f"n{m}"] for m in FL.READINGS}
        out["rerun_equals_b1"]["record"] = rec_sj == stored["record"]
    rerun_ok = stored is None or all(out["rerun_equals_b1"].values())
    out["passes_as_stated"] = inputs["labels_equal"] and inputs["target_equal"] and inputs["weight_deltas_equal"] and plain["all_equal"] and rerun_ok
    out["passes_given_cache_labels"] = inputs["target_equal"] and inputs["weight_deltas_equal"] and with_cache["all_equal"] and rerun_ok
    return out
