"""Plan 2, step 4 (section 6): the one fixed manifest of text pools, and the random draws keyed by text.

    uv run python -m vpd_audit_2.manifest            (build, assert, write data/manifest/)
    uv run python -m vpd_audit_2.manifest --verify   (rebuild in memory and compare byte for byte with the committed files)

Inputs: the document-recovery table `data/doc_recovery/rows.parquet`, the row hashes cached by `vpd_audit_2.recovery`,
the world-size test's batches `results/plan2_world_size/batches.json` (pool WS), the first post's row hashes
`results/plan1_smoke/first_post_rows.csv` (pools Q and DU), and the model's module layout recorded by the world-size GPU run
`results/plan2_world_size/metrics.json` (for the adversary starts).

A text is a row of the shuffled `val` split at revision 6f141f6e; its ID is `v<position>`, the position in stream order.
Every seed is `seed_from_tuple((MASTER, purpose, ...))` from the earlier harness (`vpd_audit/masks.py:42-47 @ b6d3bac`).
Every permutation is `numpy.random.default_rng(seed).permutation`, and the manifest stores the positions drawn.

Writes `data/manifest/manifest.json` (pools, texts, exclusions, seeds, assertions, report) and
`data/manifest/starts.npz` (the sixteen adversary starts), with `data/manifest/SHA256SUMS`.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env

MASTER = 20261001
CONTENT_HASH = "sha512"  # the 512 ids the model sees (the head, 1 Oct); the 513-id counts are reported beside
PROSE_LABELS = ("Pile-CC", "Wikipedia (en)")  # 64 + 64 in each prose batch, mixed rows excluded (the head, 1 Oct)
CODE_LABEL = "Github"
DU_ROWS = (1024, 2048)  # pool DU: the first post's donors, for G4's reproduction of D_unif_main only (the head, 1 Oct)
DOM_BATCHES = {"attack": 3, "held-out": 1}
BATCH = 128
N_CALIBRATION, N_ATTACK, N_HELD_OUT = 16, 16, 16
N_CQ, N_RESERVE = 32, 1024
Q_ROWS = (0, 1024)
FIRST_POST_ROWS = (0, 2048)
N_STARTS = 16
SPAN = 50
OUT_DIR = env.REPO_ROOT / "data" / "manifest"
SEQ_LEN = 512


def seed_of(*parts: Any) -> int:
    from vpd_audit.masks import seed_from_tuple

    return seed_from_tuple((MASTER, *parts))


def perm(n: int, *parts: Any) -> np.ndarray:
    return np.random.default_rng(seed_of(*parts)).permutation(n)


def _rows_touching(docs_marked: np.ndarray, first: np.ndarray, last: np.ndarray) -> np.ndarray:
    """Rows whose document range [first, last] contains a marked document."""
    cs = np.concatenate([[0], np.cumsum(docs_marked.astype(np.int64))])
    return (cs[last + 1] - cs[first]) > 0


def _void(a: np.ndarray) -> np.ndarray:
    """(N, 32) uint8 digests as N comparable scalars."""
    return np.ascontiguousarray(a).view(np.dtype((np.void, a.shape[1]))).ravel()


def exclusions(content: np.ndarray, base: np.ndarray, length: np.ndarray, max_id: np.ndarray, vocab: int) -> tuple[np.ndarray, dict[str, int]]:
    """Section 6.2 after the row-and-document exclusions `base`: rows with the content hash of an excluded row, then
    duplicates among the rest (the lowest position kept), then integrity failures. Returns eligibility and counts."""
    excl = base.copy()
    counts: dict[str, int] = {}
    key = _void(content)
    step = np.isin(key, np.unique(key[excl])) & ~excl
    counts["rows_with_the_content_hash_of_an_excluded_row"] = int(step.sum())
    excl |= step
    rest = np.flatnonzero(~excl)
    _, first_idx = np.unique(key[rest], return_index=True)
    dup = np.ones(rest.size, dtype=bool)
    dup[first_idx] = False  # np.unique returns the first occurrence, which is the lowest position since rest is sorted
    counts["duplicates_by_content_hash_among_the_rest_keeping_the_lowest_position"] = int(dup.sum())
    excl[rest[dup]] = True
    bad = (length != 513) | (max_id >= vocab)
    counts["integrity_failures"] = int((bad & ~excl).sum())
    excl |= bad
    counts["eligible"] = int((~excl).sum())
    return ~excl, counts


def build() -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    import pyarrow.parquet as pq

    from vpd_audit_2.recovery import ROW_HASHES, ROWS_PARQUET, VOCAB_SIZE

    t = pq.read_table(ROWS_PARQUET).sort_by("position")
    N = t.num_rows
    assert np.array_equal(t.column("position").to_numpy(), np.arange(N))
    batch_of = t.column("tokenization_batch").to_numpy().astype(np.int64)
    first = t.column("first_doc").to_numpy().astype(np.int64)
    last = t.column("last_doc").to_numpy().astype(np.int64)
    labels = np.asarray(t.column("pile_labels").to_pylist(), dtype=object)
    mixed = t.column("mixed").to_numpy(zero_copy_only=False)
    H = np.load(ROW_HASHES)
    sha513, sha512, first_tok, max_id, length = H["sha513"], H["sha512"], H["first"], H["max_id"], H["length"]
    assert sha512.shape == sha513.shape == (N, 32)
    n_docs = int(last.max()) + 1
    ws_json = env.REPO_ROOT / "results" / "plan2_world_size" / "batches.json"
    ws_metrics = env.REPO_ROOT / "results" / "plan2_world_size" / "metrics.json"
    fp_csv = env.REPO_ROOT / "results" / "plan1_smoke" / "first_post_rows.csv"

    def sha_file(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    man: dict[str, Any] = {
        "version": 1, "master_seed": MASTER,
        "seed_function": "vpd_audit.masks.seed_from_tuple @ b6d3bac: SHA-256 of repr(tuple), first 8 bytes little-endian, masked to 63 bits; key (master, purpose, ...)",
        "permutation": "numpy.random.default_rng(seed).permutation",
        "dataset": {"repo": "danbraunai/pile-uncopyrighted-tok-shuffled", "revision": "6f141f6e4edc32fea842f2ece0d3477b15c3dc90", "split": "val", "rows": int(N)},
        "text_id": "v<position>: the row's position in stream order (files in name order, rows in file order), as the earlier harness reads it",
        "text_hashes": "sha256_513: SHA-256 of the row's 513 int32 ids; sha256_512: of the first 512, the ids the model sees",
        "content_hash": f"{CONTENT_HASH}: the hash used for the exclusions and the deduplication",
        "tokenization_batches": "1,120 batches: 160 shards of 6,250 documents, each six batches of 1,000 and one of 250 (data/doc_recovery/recovery.json)",
        "inputs": {"data/doc_recovery/rows.parquet": sha_file(ROWS_PARQUET), "results/plan2_world_size/batches.json": sha_file(ws_json),
                   "results/plan2_world_size/metrics.json": sha_file(ws_metrics), "results/plan1_smoke/first_post_rows.csv": sha_file(fp_csv)},
    }

    # --- 6.2 exclusions, in order
    excl = np.zeros(N, dtype=bool)
    counts: dict[str, int] = {}
    fp = np.zeros(N, dtype=bool)
    fp[FIRST_POST_ROWS[0] : FIRST_POST_ROWS[1]] = True
    docs = np.zeros(n_docs, dtype=bool)
    for r in np.flatnonzero(fp):
        docs[first[r] : last[r] + 1] = True
    step = fp | _rows_touching(docs, first, last)
    counts["first_post_rows_0_to_2047_and_every_row_of_their_documents"] = int((step & ~excl).sum())
    counts["first_post_documents"] = int(docs.sum())
    excl |= step

    ws = json.load(open(ws_json))
    ws_pos: dict[str, list[int]] = {}
    for W in ("8", "16", "32"):
        texts = ws["candidates"][W]["texts"]
        assert all(len(x["positions"]) >= 1 for x in texts), f"W={W}: a rebuilt text not found in the split"
        ws_pos[f"WS_W{W}"] = [min(x["positions"]) for x in texts]
    ws_rows = np.zeros(N, dtype=bool)
    ws_rows[np.concatenate([np.asarray(v) for v in ws_pos.values()])] = True
    docs_ws = np.zeros(n_docs, dtype=bool)
    for r in np.flatnonzero(ws_rows):
        docs_ws[first[r] : last[r] + 1] = True
    step = ws_rows | _rows_touching(docs_ws, first, last)
    counts["ws_rows_and_every_row_of_their_documents"] = int((step & ~excl).sum())
    counts["ws_documents"] = int(docs_ws.sum())
    excl |= step

    eligible, rest_counts = exclusions({"sha512": sha512, "sha513": sha513}[CONTENT_HASH], excl, length, max_id, VOCAB_SIZE)
    man["exclusions"] = {**counts, **rest_counts}
    other = "sha513" if CONTENT_HASH == "sha512" else "sha512"
    eligible_other, other_counts = exclusions({"sha512": sha512, "sha513": sha513}[other], excl, length, max_id, VOCAB_SIZE)
    man["exclusions_with_the_other_hash_for_comparison"] = {"content_hash": other, **counts, **other_counts,
                                                            "rows_eligible_under_one_hash_only": int((eligible != eligible_other).sum())}

    # exact duplicates in the split, for the report
    man["duplicates_in_split"] = {}
    for name, h in (("sha512", sha512), ("sha513", sha513)):
        _, cnt = np.unique(_void(h), return_counts=True)
        man["duplicates_in_split"][name] = {"groups": int((cnt > 1).sum()), "rows_beyond_first": int((cnt - 1).sum()), "largest_group": int(cnt.max())}

    # --- 6.3 split by tokenization batch
    n_batches = int(batch_of.max()) + 1
    bp = perm(n_batches, "batch-split")
    attack_batches = np.sort(bp[: n_batches // 2])
    is_attack_batch = np.zeros(n_batches, dtype=bool)
    is_attack_batch[attack_batches] = True
    side_attack = is_attack_batch[batch_of]
    man["batch_split"] = {"seed_key": [MASTER, "batch-split"], "seed": seed_of("batch-split"), "n_batches": n_batches,
                          "attack_batches": attack_batches.tolist(), "held_out_batches": np.sort(bp[n_batches // 2 :]).tolist(),
                          "eligible_rows_attack": int((eligible & side_attack).sum()), "eligible_rows_held_out": int((eligible & ~side_attack).sum())}

    # --- 6.4 pools
    pools: dict[str, dict[str, Any]] = {}
    for name, pos in ws_pos.items():
        pools[name] = {"pool": "WS", "side": None, "positions": pos, "note": f"the authors' loader at world size {name[4:]}, rank order"}
    q = list(range(*Q_ROWS))
    pools["Q"] = {"pool": "Q", "side": None, "positions": q, "note": "the first post's recipients, rows 0 to 1,023, as they are"}
    qp = perm(len(q), "q1-sets")
    pools["Q1_set1"] = {"pool": "Q1", "side": None, "positions": [q[i] for i in qp[:16]], "seed_key": [MASTER, "q1-sets"], "inside": "Q"}
    pools["Q1_set2"] = {"pool": "Q1", "side": None, "positions": [q[i] for i in qp[16:32]], "seed_key": [MASTER, "q1-sets"], "inside": "Q"}
    pools["DU"] = {"pool": "DU", "side": None, "positions": list(range(*DU_ROWS)),
                   "note": "the first post's donors D_unif, rows 1,024 to 2,047, as they are; used only by G4's reproduction of D_unif_main. Its rows and their documents are excluded from every other pool"}

    att = np.flatnonzero(eligible & side_attack)
    att = att[perm(att.size, "perm", "attack")]
    k = 0

    def take(arr: np.ndarray, n: int) -> list[int]:
        nonlocal k
        out = arr[k : k + n].tolist()
        assert len(out) == n
        k += n
        return out

    for j in range(1, N_CALIBRATION + 1):
        pools[f"C{j}"] = {"pool": "C", "side": "attack", "positions": take(att, BATCH)}
    pools["CQ"] = {"pool": "CQ", "side": "attack", "positions": take(att, N_CQ)}
    for j in range(1, N_ATTACK + 1):
        pools[f"A{j}"] = {"pool": "A", "side": "attack", "positions": take(att, BATCH)}
    pools["R"] = {"pool": "R", "side": "attack", "positions": take(att, N_RESERVE)}
    rest_attack = att[k:]
    k = 0
    held = np.flatnonzero(eligible & ~side_attack)
    held = held[perm(held.size, "perm", "held-out")]
    for j in range(1, N_HELD_OUT + 1):
        pools[f"H{j}"] = {"pool": "H", "side": "held-out", "positions": take(held, BATCH)}
    rest_held = held[k:]
    man["slicing"] = {"attack": {"seed_key": [MASTER, "perm", "attack"], "seed": seed_of("perm", "attack"), "order": "C1..C16, CQ, A1..A16, R"},
                      "held-out": {"seed_key": [MASTER, "perm", "held-out"], "seed": seed_of("perm", "held-out"), "order": "H1..H16"}}

    dom_seeds = {}
    for side_name, rest in (("attack", rest_attack), ("held-out", rest_held)):
        remaining = np.sort(rest)
        for domain in ("code", "prose"):
            for i in range(1, DOM_BATCHES[side_name] + 1):
                key = ("dom", domain, side_name, i)
                rng = np.random.default_rng(seed_of(*key))
                dom_seeds["|".join(map(str, key))] = seed_of(*key)
                if domain == "code":
                    cand = remaining[(labels[remaining] == CODE_LABEL) & ~mixed[remaining]]
                    chosen = cand[rng.permutation(cand.size)[:BATCH]]
                else:
                    chosen_parts = []
                    for lab in PROSE_LABELS:
                        cand = remaining[(labels[remaining] == lab) & ~mixed[remaining]]
                        chosen_parts.append(cand[rng.permutation(cand.size)[: BATCH // len(PROSE_LABELS)]])
                    chosen = np.concatenate(chosen_parts)
                assert chosen.size == BATCH
                pools[f"DOM_{domain}_{side_name}_{i}"] = {"pool": "DOM", "side": side_name, "positions": chosen.tolist(),
                                                          "seed_key": [MASTER, *key], "labels": [CODE_LABEL] if domain == "code" else list(PROSE_LABELS)}
                remaining = np.setdiff1d(remaining, chosen, assume_unique=True)
    man["dom_seeds"] = dom_seeds

    # --- texts
    used = sorted({p for v in pools.values() for p in v["positions"]})
    man["texts"] = {f"v{p}": {"sha256_513": sha513[p].tobytes().hex(), "sha256_512": sha512[p].tobytes().hex(), "tokenization_batch": int(batch_of[p]),
                              "first_doc": int(first[p]), "last_doc": int(last[p]), "pile_labels": str(labels[p]), "mixed": bool(mixed[p]),
                              "batch_side": ("attack" if side_attack[p] else "held-out"), "begins_with_eos": bool(first_tok[p] == 0)} for p in used}
    for v in pools.values():
        v["texts"] = [f"v{p}" for p in v.pop("positions")]
    man["pools"] = pools
    man["pool_notes"] = {"A9_to_A16_and_H9_to_H16": "unused unless the freeze file enlarges question 2's design to 16 x 16",
                         "DOM": "drawn from the rows left on each side after R (attack) and H16 (held-out); code: 128 Github rows; prose: 64 Pile-CC and 64 Wikipedia (en) rows; mixed rows excluded",
                         "sides": "WS, Q, Q1, and DU have no side; their rows and documents are excluded from every sided pool"}

    # --- 6.6 assertions
    man["assertions"] = assertions(man, pools, eligible, side_attack, first, last)
    # --- report
    man["report"] = {
        "share_beginning_with_eos": {name: float(np.mean([man["texts"][t]["begins_with_eos"] for t in v["texts"]])) for name, v in pools.items()},
        "held_out_rows_sharing_a_50_token_span_with_an_attack_row": span_overlap(pools),
    }

    # --- 6.5 draws keyed by text
    starts, starts_meta = make_starts()
    man["draws"] = {
        "adversary_starts": starts_meta,
        "routing": {"seed_key": "(master, 'routing', s, text_id, draw)", "use": "a torch.Generator seeded with seed_from_tuple(key), passed as `generator` to the authors' samplers"},
        "stochastic": {"seed_key": "(master, 'stoch', s, text_id, draw)", "use": "as routing"},
    }
    return man, starts


def assertions(man: dict[str, Any], pools: dict[str, Any], eligible: np.ndarray, side_attack: np.ndarray, first: np.ndarray, last: np.ndarray) -> dict[str, Any]:
    names = list(pools)
    pos = {n: [int(t[1:]) for t in pools[n]["texts"]] for n in names}
    out: dict[str, Any] = {}
    nested = {("Q1_set1", "Q"), ("Q1_set2", "Q")}
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            if (a, b) in nested or (b, a) in nested:
                continue
            sa, sb = set(pos[a]), set(pos[b])
            assert not (sa & sb), f"pools {a} and {b} share a text"
            ha = {man["texts"][f"v{p}"]["sha256_512"] for p in sa} | {man["texts"][f"v{p}"]["sha256_513"] for p in sa}
            hb = {man["texts"][f"v{p}"]["sha256_512"] for p in sb} | {man["texts"][f"v{p}"]["sha256_513"] for p in sb}
            assert not (ha & hb), f"pools {a} and {b} share a content hash"
    out["pairwise_disjoint_by_text_id_and_hash"] = True
    for name in pos:
        assert len(set(pos[name])) == len(pos[name]), f"{name} repeats a text"
    att = [n for n in names if pools[n]["side"] == "attack"]
    hel = [n for n in names if pools[n]["side"] == "held-out"]

    def docs(ns: list[str]) -> set[int]:
        s: set[int] = set()
        for n in ns:
            for p in pos[n]:
                s.update(range(int(first[p]), int(last[p]) + 1))
        return s

    assert not (docs(att) & docs(hel)), "pools on opposite sides share a document"
    out["no_document_shared_across_sides"] = True
    unsided = [n for n in names if pools[n]["side"] is None]
    assert not (docs(unsided) & docs(att + hel)), "a document of WS, Q, or DU lies in a sided pool"
    out["no_document_of_WS_Q_DU_in_a_sided_pool"] = True
    fp: dict[str, dict[int, str]] = {"E": {}, "D_unif": {}}
    with open(env.REPO_ROOT / "results" / "plan1_smoke" / "first_post_rows.csv") as f:
        for r in csv.DictReader(f):
            fp[r["set"]][int(r["row"])] = r["sha256_int32_512"]
    assert pos["Q"] == list(range(*Q_ROWS)) and [fp["E"][p] for p in pos["Q"]] == [man["texts"][f"v{p}"]["sha256_512"] for p in pos["Q"]]
    out["Q_equals_first_post_recipients_row_for_row"] = True
    assert pos["DU"] == list(range(*DU_ROWS)) and [fp["D_unif"][p] for p in pos["DU"]] == [man["texts"][f"v{p}"]["sha256_512"] for p in pos["DU"]]
    out["DU_equals_first_post_donors_row_for_row"] = True
    for n in names:
        if pools[n]["pool"] in ("C", "A", "H", "DOM", "WS"):
            assert len(pos[n]) == BATCH, (n, len(pos[n]))
    out["every_batch_holds_128_rows"] = True
    for n in names:
        if pools[n]["pool"] not in ("WS", "Q", "Q1", "DU"):
            assert all(eligible[p] for p in pos[n]), f"{n} holds an ineligible row"
            assert all(side_attack[p] == (pools[n]["side"] == "attack") for p in pos[n]), f"{n} holds a row of the other side"
    out["every_new_row_eligible_and_on_its_side"] = True
    return out


def span_overlap(pools: dict[str, Any]) -> dict[str, Any]:
    from vpd_audit_2.data_check import SHUFFLED, ParquetSplit

    sp = ParquetSplit(*SHUFFLED, column="input_ids")
    a_pos = [int(t[1:]) for n in pools if pools[n]["pool"] == "A" for t in pools[n]["texts"]]
    h_pos = [int(t[1:]) for n in pools if pools[n]["pool"] == "H" for t in pools[n]["texts"]]
    A = sp.token_rows(a_pos)[:, :SEQ_LEN]
    Hh = sp.token_rows(h_pos)[:, :SEQ_LEN]
    grams = {w.tobytes() for row in A for w in np.lib.stride_tricks.sliding_window_view(row, SPAN)}
    hit = [any(w.tobytes() in grams for w in np.lib.stride_tricks.sliding_window_view(row, SPAN)) for row in Hh]
    return {"span_tokens": SPAN, "over": "the 512 ids the model sees", "attack_rows": len(a_pos), "held_out_rows": len(h_pos),
            "held_out_rows_sharing": int(sum(hit)), "share": float(np.mean(hit))}


def make_starts() -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Sixteen starts from U[0, 1), seed (master, 'start', s), drawn on the CPU in float32 with one torch generator per
    start, module by module in model.target_module_paths order, shape [1, 1, C_l + 1] (delta entry last)."""
    import torch

    layout = json.load(open(env.REPO_ROOT / "results" / "plan2_world_size" / "metrics.json"))["module_layout"]
    assert len(layout) == 24 and sum(c for _, c in layout) == 38912, layout
    arrays: dict[str, np.ndarray] = {}
    meta: dict[str, Any] = {"file": "starts.npz", "layout": layout, "shape_per_module": "[1, 1, C_l + 1], delta entry last",
                            "generator": "torch.Generator('cpu').manual_seed(seed); torch.rand(shape, generator, dtype=float32) per module in order",
                            "entries_per_start": sum(c + 1 for _, c in layout), "starts": {}}
    for s in range(1, N_STARTS + 1):
        g = torch.Generator(device="cpu")
        g.manual_seed(seed_of("start", s))
        parts = []
        for name, c in layout:
            x = torch.rand((1, 1, c + 1), generator=g, dtype=torch.float32).numpy()
            arrays[f"s{s}|{name}"] = x
            parts.append(x.tobytes())
        meta["starts"][str(s)] = {"seed_key": [MASTER, "start", s], "seed": seed_of("start", s), "sha256": hashlib.sha256(b"".join(parts)).hexdigest()}
    return arrays, meta


def pool_ids(name: str) -> tuple[np.ndarray, list[str], list[str]]:
    """A pool's token ids as the model sees them (n, 512) int32, in the manifest's order, read from the cached parquet
    files and checked against the manifest's hashes; with the text IDs and their 512-id SHA-256."""
    from vpd_audit_2.data_check import SHUFFLED, ParquetSplit

    man = json.load(open(OUT_DIR / "manifest.json"))
    texts = man["pools"][name]["texts"]
    rows = ParquetSplit(*SHUFFLED, column="input_ids").token_rows([int(t[1:]) for t in texts])
    sha = [man["texts"][t]["sha256_512"] for t in texts]
    for k, t in enumerate(texts):
        assert hashlib.sha256(rows[k].tobytes()).hexdigest() == man["texts"][t]["sha256_513"], t
        assert hashlib.sha256(rows[k, :SEQ_LEN].tobytes()).hexdigest() == sha[k], t
    return np.ascontiguousarray(rows[:, :SEQ_LEN]), texts, sha


def load_start(s: int, path: Path = OUT_DIR / "starts.npz") -> dict[str, np.ndarray]:
    man = json.load(open(OUT_DIR / "manifest.json"))
    layout = man["draws"]["adversary_starts"]["layout"]
    with np.load(path) as z:
        start = {name: z[f"s{s}|{name}"] for name, _ in layout}
    got = hashlib.sha256(b"".join(start[name].tobytes() for name, _ in layout)).hexdigest()
    assert got == man["draws"]["adversary_starts"]["starts"][str(s)]["sha256"], f"start {s}: hash mismatch"
    return start


def deterministic_npz(arrays: dict[str, np.ndarray]) -> bytes:
    """An .npz archive (readable by numpy.load) with fixed entry timestamps, so the same arrays give the same bytes;
    `numpy.savez` stamps each entry with the current time."""
    import io
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_STORED) as zf:
        for k in sorted(arrays):
            b = io.BytesIO()
            np.lib.format.write_array(b, np.ascontiguousarray(arrays[k]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{k}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o600 << 16
            zf.writestr(info, b.getvalue())
    return buf.getvalue()


def serialize(man: dict[str, Any], starts: dict[str, np.ndarray]) -> tuple[bytes, bytes]:
    js = (json.dumps(man, indent=1, sort_keys=True) + "\n").encode()
    return js, deterministic_npz(starts)


def main(verify: bool = False) -> None:
    man, starts = build()
    js, npz = serialize(man, starts)
    if verify:
        same_js = (OUT_DIR / "manifest.json").read_bytes() == js
        same_npz = (OUT_DIR / "starts.npz").read_bytes() == npz
        print(f"[manifest] rebuild equals the committed manifest.json: {same_js}; starts.npz: {same_npz}")
        assert same_js and same_npz
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "manifest.json").write_bytes(js)
    (OUT_DIR / "starts.npz").write_bytes(npz)
    sums = "".join(f"{hashlib.sha256((OUT_DIR / n).read_bytes()).hexdigest()}  {n}\n" for n in ("manifest.json", "starts.npz"))
    (OUT_DIR / "SHA256SUMS").write_text(sums)
    print(f"[manifest] exclusions {man['exclusions']}")
    print(f"[manifest] wrote {OUT_DIR}:\n{sums}")


if __name__ == "__main__":
    main(verify="--verify" in sys.argv[1:])
