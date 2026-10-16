"""Plan 2 of the research log, step 1 (section 3): full document recovery, on the CPU, with no model.

    uv run python -m vpd_audit_2.recovery

Rebuilds the authors' tokenization of every `val` document of `danbraunai/pile-uncopyrighted` (stage 2 of the chain
described in `data_check.py`) and maps every row of the tokenized `val` split to the documents it spans and their Pile
labels (`meta.pile_set_name`).

The tokenization is the authors' `tokenize_and_concatenate` (param_decomp/data.py at 74146b5, the same arithmetic as
spd/data.py at the run's commit 85c6b70): each batch of 1,000 documents is joined by the EOS string, the joined text is
cut into 20 character chunks of `(len - 1) // 20 + 1` characters, each chunk is encoded on its own with
`add_special_tokens=False`, the ids are concatenated, and the stream is cut into 513-token rows, the tail dropped. Here
the chunks are encoded with the same fast tokenizer called with `return_offsets_mapping=True`, which returns the same
ids plus each token's character span; `check_authors_function` confirms the ids equal the authors' own function on a
sample of batches, and the row-hash check below confirms them on every row.

A token's documents are read from its character span: the joined text alternates document k and separator k, and a
token belongs to every document whose characters it covers (a separator, recognised as EOS or broken by a chunk
boundary, belongs to no document). A row's documents run from the lowest to the highest document any of its tokens
covers. Where a batch of n documents has exactly n - 1 EOS tokens, the simpler reading "document k lies between EOS
k-1 and EOS k" is computed too and every token is compared.

The batches are not all 1,000 documents (see STAGE2_NUM_PROC): `map` ran on 160 shards of 6,250 documents, so each
shard holds six batches of 1,000 and one of 250, 1,120 batches in all.

Checks, all recorded in `data/doc_recovery/recovery.json`:
  - every rebuilt row equals the unshuffled split's row at the same index, by SHA-256 of its 513 int32 ids;
  - every shuffled row i equals unshuffled row perm[i], perm = default_rng(42).permutation(2,775,651), by hash;
  - every batch of n documents has exactly n - 1 EOS tokens in its stream; failures are listed with their cause;
  - batch boundaries: the rebuilt batches, concatenated in order, give exactly the unshuffled rows, which confirms
    the boundaries. The table is written only if this holds for every row.

Writes (committed): `data/doc_recovery/rows.parquet`, one row per shuffled position, and `recovery.json`.
Writes (cache, not committed): `<cache>/recovery/row_hashes.npz`, per shuffled position the SHA-256 of the 513 ids and
of the first 512, the first token, and the largest id, for the manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env
from vpd_audit_2.data_check import DOCS_PER_BATCH, RESPLIT, ROW_LEN, SEQ_LEN, SHUFFLE_SEED, SHUFFLED, SPLIT, TOKENIZER, UNSHUFFLED

TOKENIZER_REVISION = "c292233c833e336628618a88a648727eb3dff0a7"  # provenance (k)
N_DOCS = 1_000_000
# `Dataset.map(batched=True, num_proc=P)` cuts the dataset into P contiguous shards and batches of 1,000 within each
# shard, so a batch never crosses a shard boundary. The dataset card says P = 10 (shards of 100,000 documents). The
# first attempt at P = 10 reproduced rows only up to document 6,000; there the authors' batch held exactly the 250
# documents 6,000 to 6,249 (the only count whose chunk length reproduces their stream). That is P = 160 (the stage-3
# script's NUM_PROC): shards of 6,250 documents, each six batches of 1,000 and one of 250. The row-hash check below
# tests this on every row.
STAGE2_NUM_PROC = 160
SHARD_DOCS = N_DOCS // STAGE2_NUM_PROC
N_ROWS = 2_775_651
VOCAB_SIZE = 50277  # provenance/runs/t-9d2b8f02/model_config.yaml: vocab_size
EOS_ID = 0
N_CHUNKS = 20  # tokenize_and_concatenate: num_chunks
BATCHES_PER_TASK = 14
N_WORKERS = 9
AUTHORS_FUNCTION_SAMPLE = (0, 1, 6, 7, 560, 1118, 1119)  # batches re-tokenized with the authors' own function


def tokenization_batches() -> np.ndarray:
    """(n_batches, 2): each batch's first document and one past its last, in order."""
    out = []
    for s in range(STAGE2_NUM_PROC):
        a, b = s * SHARD_DOCS, (s + 1) * SHARD_DOCS
        out += [(d, min(d + DOCS_PER_BATCH, b)) for d in range(a, b, DOCS_PER_BATCH)]
    arr = np.array(out, dtype=np.int64)
    assert arr[0, 0] == 0 and arr[-1, 1] == N_DOCS and np.all(arr[1:, 0] == arr[:-1, 1])
    return arr


BATCHES = tokenization_batches()
N_BATCHES = BATCHES.shape[0]

WORK = env.CACHE_DIR / "recovery"
OUT_DIR = env.REPO_ROOT / "data" / "doc_recovery"
ROWS_PARQUET = OUT_DIR / "rows.parquet"
SUMMARY_JSON = OUT_DIR / "recovery.json"
ROW_HASHES = WORK / "row_hashes.npz"


def log(msg: str) -> None:
    print(f"[recovery] {msg}", flush=True)


def split_files(repo_rev: tuple[str, str]) -> list[Path]:
    """The cached `val` parquet files of a dataset at its pinned revision, in name order (the streaming order)."""
    repo, rev = repo_rev
    snap = env.HF_DIR / "hub" / ("datasets--" + repo.replace("/", "--")) / "snapshots" / rev / "data"
    files = sorted(snap.glob(f"{SPLIT}-*.parquet"))
    assert len(files) == 12, (repo, rev, len(files), "run `python -m vpd_audit_2.data_check` first to download the files")
    return files


# ----------------------------------------------------------------------------- hashing a tokenized split


def _hash_file(path: Path) -> dict[str, np.ndarray]:
    """Per row of one parquet file: SHA-256 of the int32 bytes of its ids (all, and the first 512), its length, its
    first id, and its largest id."""
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    col = pq.ParquetFile(path).read(columns=["input_ids"]).column("input_ids").combine_chunks()
    lengths = pc.list_value_length(col).to_numpy().astype(np.int64)
    flat = np.ascontiguousarray(pc.list_flatten(col).to_numpy(), dtype=np.int32)
    n = lengths.size
    sha_all = np.empty((n, 32), dtype=np.uint8)
    sha_512 = np.empty((n, 32), dtype=np.uint8)
    first = np.empty(n, dtype=np.int32)
    max_id = np.empty(n, dtype=np.int32)
    starts = np.concatenate([[0], np.cumsum(lengths)[:-1]])
    for i in range(n):
        row = flat[starts[i] : starts[i] + lengths[i]]
        sha_all[i] = np.frombuffer(hashlib.sha256(row.tobytes()).digest(), dtype=np.uint8)
        sha_512[i] = np.frombuffer(hashlib.sha256(row[:SEQ_LEN].tobytes()).digest(), dtype=np.uint8)
        first[i] = row[0] if row.size else -1
        max_id[i] = row.max() if row.size else -1
    return {"sha513": sha_all, "sha512": sha_512, "length": lengths.astype(np.int32), "first": first, "max_id": max_id}


def hash_split(repo_rev: tuple[str, str]) -> dict[str, np.ndarray]:
    files = split_files(repo_rev)
    with Pool(min(N_WORKERS, len(files))) as pool:
        parts = pool.map(_hash_file, files)
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


# ----------------------------------------------------------------------------- rebuilding the tokenization

_TOK: Any = None
_DOCS: Any = None


class _DocReader:
    """Documents of the re-split `val` split by global index, read by row group."""

    def __init__(self) -> None:
        import pyarrow.parquet as pq

        self.pq = [pq.ParquetFile(f) for f in split_files(RESPLIT)]
        spans = []
        start = 0
        for f, p in enumerate(self.pq):
            for g in range(p.metadata.num_row_groups):
                n = p.metadata.row_group(g).num_rows
                spans.append((start, start + n, f, g))
                start += n
        assert start == N_DOCS, start
        self.spans = spans

    def read(self, d0: int, d1: int) -> tuple[list[str], list[str]]:
        texts: list[str] = []
        labels: list[str] = []
        for a, b, f, g in self.spans:
            if b <= d0 or a >= d1:
                continue
            t = self.pq[f].read_row_group(g, columns=["text", "meta"])
            lo, hi = max(d0, a) - a, min(d1, b) - a
            texts += t.column("text").to_pylist()[lo:hi]
            labels += t.column("meta").combine_chunks().field("pile_set_name").to_pylist()[lo:hi]
        assert len(texts) == d1 - d0
        return texts, labels


def _init_worker() -> None:
    global _TOK, _DOCS
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    from transformers import AutoTokenizer

    _TOK = AutoTokenizer.from_pretrained(TOKENIZER, revision=TOKENIZER_REVISION)
    assert _TOK.eos_token_id == EOS_ID and _TOK.eos_token == "<|endoftext|>"
    _DOCS = _DocReader()


def tokenize_batch(tok: Any, docs: list[str]) -> tuple[np.ndarray, np.ndarray, int]:
    """The authors' stream for one batch: ids (int32) and each token's character span [start, end) in the joined text."""
    eos = tok.eos_token
    full = eos.join(docs)
    cl = (len(full) - 1) // N_CHUNKS + 1
    chunks = [full[i * cl : (i + 1) * cl] for i in range(N_CHUNKS)]
    enc = tok(chunks, add_special_tokens=False, return_offsets_mapping=True)
    ids = np.concatenate([np.asarray(x, dtype=np.int32) for x in enc["input_ids"]])
    spans = np.concatenate([np.asarray(o, dtype=np.int64).reshape(-1, 2) + i * cl for i, o in enumerate(enc["offset_mapping"])])
    assert spans.shape == (ids.size, 2)
    return ids, spans, cl


def _rebuild_task(task: tuple[int, int, list[str]]) -> list[dict[str, Any]]:
    b0, b1, label_names = task
    bit = {name: i for i, name in enumerate(label_names)}
    D0, D1 = int(BATCHES[b0, 0]), int(BATCHES[b1 - 1, 1])
    texts, labels = _DOCS.read(D0, D1)
    eos = _TOK.eos_token
    out = []
    for b in range(b0, b1):
        d_first, d_stop = int(BATCHES[b, 0]), int(BATCHES[b, 1])
        n_docs = d_stop - d_first
        lo_d = d_first - D0
        docs = texts[lo_d : lo_d + n_docs]
        doc_bits = np.array([1 << bit[x] for x in labels[lo_d : lo_d + n_docs]], dtype=np.int64)
        ids, spans, _ = tokenize_batch(_TOK, docs)
        n_rows = ids.size // ROW_LEN
        rows = ids[: n_rows * ROW_LEN].reshape(n_rows, ROW_LEN)
        sha = np.empty((n_rows, 32), dtype=np.uint8)
        for r in range(n_rows):
            sha[r] = np.frombuffer(hashlib.sha256(rows[r].tobytes()).digest(), dtype=np.uint8)

        # regions of the joined text: document k is [R[2k], R[2k+1]), separator k is [R[2k+1], R[2k+2])
        lens = np.array([len(d) for d in docs], dtype=np.int64)
        starts = np.concatenate([[0], np.cumsum(lens + len(eos))[:-1]])
        R = np.empty(2 * n_docs, dtype=np.int64)
        R[0::2] = starts
        R[1::2] = starts + lens
        s, e = spans[:, 0], spans[:, 1]
        e_last = np.maximum(e - 1, s)
        rs = np.searchsorted(R, s, side="right") - 1
        re_ = np.searchsorted(R, e_last, side="right") - 1
        tok_lo = np.where(rs % 2 == 0, rs // 2, (rs + 1) // 2)
        tok_hi = np.where(re_ % 2 == 0, re_ // 2, (re_ - 1) // 2)
        has_doc = tok_lo <= tok_hi
        straddling = int((has_doc & (tok_hi > tok_lo)).sum())
        assert int((tok_hi - tok_lo)[has_doc].max(initial=0)) <= 1, "a token covers characters of more than two documents"
        tok_lo = tok_lo[: n_rows * ROW_LEN]
        tok_hi = tok_hi[: n_rows * ROW_LEN]
        hd = has_doc[: n_rows * ROW_LEN]
        BIG = np.int64(1 << 40)
        row_first = np.where(hd, tok_lo, BIG).reshape(n_rows, ROW_LEN).min(axis=1)
        row_last = np.where(hd, tok_hi, -1).reshape(n_rows, ROW_LEN).max(axis=1)
        tok_bits = np.where(hd, doc_bits[np.clip(tok_lo, 0, n_docs - 1)] | doc_bits[np.clip(tok_hi, 0, n_docs - 1)], 0)
        row_bits = np.bitwise_or.reduce(tok_bits.reshape(n_rows, ROW_LEN), axis=1)
        no_doc = row_last < 0

        # the EOS reading, where the batch of n documents has exactly n - 1 EOS tokens
        is_eos = ids == EOS_ID
        eos_count = int(is_eos.sum())
        sep_tokens_exact = int(((ids == EOS_ID) & ~has_doc).sum())  # EOS tokens lying exactly on a separator
        eos_in_docs = int((is_eos & has_doc).sum())  # literal EOS inside a document's text
        literal_docs = [d_first + k for k, d in enumerate(docs) if eos in d]
        xcheck: dict[str, Any] = {"applied": eos_count == n_docs - 1}
        if xcheck["applied"]:
            eos_doc = np.cumsum(is_eos) - is_eos  # EOS tokens strictly before each token
            nonsep = ~is_eos
            lo_all = np.where(rs % 2 == 0, rs // 2, (rs + 1) // 2)
            hi_all = np.where(re_ % 2 == 0, re_ // 2, (re_ - 1) // 2)
            agree = has_doc[nonsep] & (lo_all[nonsep] == eos_doc[nonsep]) & (hi_all[nonsep] == eos_doc[nonsep])
            xcheck["tokens_compared"] = int(nonsep.sum())
            xcheck["tokens_disagreeing"] = int((~agree).sum())
            xcheck["eos_tokens_not_on_a_separator"] = int((is_eos & has_doc).sum())
        out.append({
            "batch": b, "first_doc_of_batch": d_first, "n_docs": n_docs, "n_rows": n_rows, "n_tokens": int(ids.size), "eos_count": eos_count,
            "eos_on_separators": sep_tokens_exact, "eos_inside_documents": eos_in_docs,
            "documents_with_literal_eos": literal_docs,
            "straddling_tokens": straddling, "rows_without_document": int(no_doc.sum()), "xcheck": xcheck,
            "sha513": sha, "first_doc": (row_first + d_first).astype(np.int32),
            "last_doc": (row_last + d_first).astype(np.int32), "label_bits": row_bits.astype(np.int64),
        })
    return out


def check_authors_function(batches: tuple[int, ...] = AUTHORS_FUNCTION_SAMPLE) -> dict[str, Any]:
    """On a sample of batches, the authors' own `tokenize_and_concatenate` gives the same rows as `tokenize_batch`."""
    import datasets

    from param_decomp.data import tokenize_and_concatenate

    _init_worker()
    res = {}
    for b in batches:
        docs, _ = _DOCS.read(int(BATCHES[b, 0]), int(BATCHES[b, 1]))
        ds = datasets.Dataset.from_dict({"text": docs})
        theirs = tokenize_and_concatenate(ds, _TOK, column_name="text", max_length=ROW_LEN, add_bos_token=False, num_proc=1, to_lower=False)
        theirs = np.stack([np.asarray(x["input_ids"]) for x in theirs]).astype(np.int32)
        ids, _, _ = tokenize_batch(_TOK, docs)
        ours = ids[: (ids.size // ROW_LEN) * ROW_LEN].reshape(-1, ROW_LEN)
        res[str(b)] = {"rows": int(theirs.shape[0]), "equal": bool(theirs.shape == ours.shape and np.array_equal(theirs, ours))}
        log(f"authors' function on batch {b}: {res[str(b)]}")
    return res


# ----------------------------------------------------------------------------- main


def main() -> dict[str, Any]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    t0 = time.time()
    WORK.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Any] = {"sources": {"shuffled": list(SHUFFLED), "unshuffled": list(UNSHUFFLED), "resplit": list(RESPLIT),
                                       "tokenizer": [TOKENIZER, TOKENIZER_REVISION]},
                           "conventions": {
                               "position": "row index of the shuffled `val` split in stream order (files in name order, rows in file order)",
                               "unshuffled_index": "row index of the unshuffled `val` split; shuffled row i is unshuffled row perm[i]",
                               "document": "row index of the re-split `val` split of danbraunai/pile-uncopyrighted (0 to 999,999)",
                               "tokenization_batch": "index of the authors' tokenization batch (0 to 1,119): 160 shards of 6,250 documents, each cut into six batches of 1,000 and one of 250; every row lies inside one batch",
                               "row documents": "first_doc to last_doc: the lowest and highest document any token of the row covers by its character span; EOS separators belong to no document",
                               "pile_labels": "the distinct meta.pile_set_name of the documents the row's tokens cover, sorted, joined by '|'",
                               "hash": "SHA-256 of the row's int32 ids as little-endian bytes (the earlier project's hash_ids)"}}

    out["tokenization_batches"] = {
        "stage2_num_proc_inferred": STAGE2_NUM_PROC, "shard_documents": SHARD_DOCS, "documents_per_batch": DOCS_PER_BATCH,
        "n_batches": N_BATCHES, "batch_sizes": {str(k): int(v) for k, v in zip(*np.unique(BATCHES[:, 1] - BATCHES[:, 0], return_counts=True))},
        "evidence": ("The dataset card's num_proc = 10 (shards of 100,000, batches at multiples of 1,000) reproduced the first 17,402 "
                     "unshuffled rows only (documents 0 to 6,008; 2,775,708 rows rebuilt against 2,775,651). In the authors' stream the "
                     "batch starting at document 6,000 has its first chunk boundary at character 81,626, which among 1 to 1,000 "
                     "documents only a batch of 250 (documents 6,000 to 6,249) produces; that batch reproduces its 820 rows exactly. "
                     "num_proc = 160 gives shards of 6,250, hence this batch. The row-hash check below tests it on every row."),
        "num_proc_10_attempt": {"rows_rebuilt": 2775708, "rows_equal_from_the_start": 17402, "first_mismatch_unshuffled_index": 17399,
                                "log": "<cache>/logs/recovery.log of the first run (not committed)"},
    }
    out["authors_function_check"] = check_authors_function()

    t = time.time()
    shuf = hash_split(SHUFFLED)
    log(f"hashed the shuffled split: {shuf['sha513'].shape[0]} rows in {time.time() - t:.0f} s")
    t = time.time()
    unshuf = hash_split(UNSHUFFLED)
    log(f"hashed the unshuffled split: {unshuf['sha513'].shape[0]} rows in {time.time() - t:.0f} s")
    N = shuf["sha513"].shape[0]
    assert N == unshuf["sha513"].shape[0] == N_ROWS, (N, unshuf["sha513"].shape[0])
    np.savez(ROW_HASHES, sha513=shuf["sha513"], sha512=shuf["sha512"], length=shuf["length"], first=shuf["first"], max_id=shuf["max_id"],
             unshuffled_sha513=unshuf["sha513"])

    perm = np.random.default_rng(SHUFFLE_SEED).permutation(N)
    inv = np.empty(N, dtype=np.int64)
    inv[perm] = np.arange(N)
    perm_eq = np.all(shuf["sha513"] == unshuf["sha513"][perm], axis=1)
    out["permutation_check"] = {"seed": SHUFFLE_SEED, "rows_compared": int(N), "rows_equal": int(perm_eq.sum()),
                                "first_mismatches_shuffled_position": np.flatnonzero(~perm_eq)[:50].tolist()}
    log(f"permutation: {int(perm_eq.sum())}/{N} shuffled rows equal unshuffled perm[i]")
    out["integrity_shuffled"] = {"rows_not_513_ids": int((shuf["length"] != ROW_LEN).sum()),
                                 "rows_with_id_at_or_above_vocab": int((shuf["max_id"] >= VOCAB_SIZE).sum()), "vocab_size": VOCAB_SIZE}

    # labels known over all documents
    from vpd_audit_2.data_check import WORK as DC_WORK

    z = np.load(DC_WORK / "val_document_chars.npz", allow_pickle=False)
    doc_labels_all = list(z["subset"])
    label_names = sorted(set(doc_labels_all))
    assert len(label_names) < 63, len(label_names)
    out["label_names"] = label_names

    t = time.time()
    tasks = [(b, min(b + BATCHES_PER_TASK, N_BATCHES), label_names) for b in range(0, N_BATCHES, BATCHES_PER_TASK)]
    results: list[dict[str, Any]] = []
    with Pool(N_WORKERS, initializer=_init_worker) as pool:
        for k, res in enumerate(pool.imap(_rebuild_task, tasks)):
            results += res
            if (k + 1) % 10 == 0:
                log(f"rebuilt {len(results)}/{N_BATCHES} batches ({time.time() - t:.0f} s)")
    out["rebuild_seconds"] = time.time() - t
    assert [r["batch"] for r in results] == list(range(N_BATCHES))

    counts = np.array([r["n_rows"] for r in results])
    batch_start = np.concatenate([[0], np.cumsum(counts)])
    out["rows_rebuilt"] = int(counts.sum())
    sha_re = np.concatenate([r["sha513"] for r in results])
    n_cmp = min(sha_re.shape[0], N)
    row_eq = np.all(sha_re[:n_cmp] == unshuf["sha513"][:n_cmp], axis=1)
    bad_rows = np.flatnonzero(~row_eq)
    out["row_hash_check"] = {
        "rows_rebuilt": int(sha_re.shape[0]), "rows_in_unshuffled_split": int(N), "rows_compared": int(n_cmp), "rows_equal": int(row_eq.sum()),
        "mismatches": [{"unshuffled_index": int(j), "batch": int(np.searchsorted(batch_start, j, side="right") - 1)} for j in bad_rows[:200]],
        "batches_with_mismatches": sorted({int(np.searchsorted(batch_start, j, side="right") - 1) for j in bad_rows}),
        "batch_boundaries_confirmed": bool(sha_re.shape[0] == N and row_eq.all()),
    }
    log(f"row hashes: {int(row_eq.sum())}/{n_cmp} rebuilt rows equal the unshuffled split; rebuilt {sha_re.shape[0]}, split {N}")

    eos_fail = [r for r in results if r["eos_count"] != r["n_docs"] - 1]
    out["eos_check"] = {
        "batches": N_BATCHES, "batches_with_n_minus_1_eos": N_BATCHES - len(eos_fail),
        "failing_batches": [{"batch": r["batch"], "first_doc_of_batch": r["first_doc_of_batch"], "n_docs": r["n_docs"], "eos_count": r["eos_count"],
                             "eos_on_separators": r["eos_on_separators"], "eos_inside_documents": r["eos_inside_documents"],
                             "documents_with_literal_eos": r["documents_with_literal_eos"],
                             "separators_not_encoded_as_eos": r["n_docs"] - 1 - r["eos_on_separators"]} for r in eos_fail],
        "note": ("the plan's check, for a batch of n documents: n - 1 EOS tokens. A failing batch's documents are still assigned exactly, "
                 "by character span; the EOS reading would misassign them"),
    }
    xs = [r["xcheck"] for r in results if r["xcheck"]["applied"]]
    out["eos_reading_cross_check"] = {"batches": len(xs), "tokens_compared": int(sum(x["tokens_compared"] for x in xs)),
                                      "tokens_disagreeing": int(sum(x["tokens_disagreeing"] for x in xs)),
                                      "eos_tokens_not_on_a_separator": int(sum(x["eos_tokens_not_on_a_separator"] for x in xs))}
    out["straddling_tokens"] = int(sum(r["straddling_tokens"] for r in results))
    out["rows_without_document"] = int(sum(r["rows_without_document"] for r in results))
    log(f"EOS: {out['eos_check']['batches_with_n_minus_1_eos']}/{N_BATCHES} batches with n - 1; cross-check {out['eos_reading_cross_check']}")

    if not out["row_hash_check"]["batch_boundaries_confirmed"]:
        out["seconds"] = time.time() - t0
        with open(SUMMARY_JSON, "w") as f:
            json.dump(out, f, indent=1)
        raise SystemExit(f"the rebuilt rows do not reproduce the split; no table written. See {SUMMARY_JSON}")

    # the table, by shuffled position
    first_doc = np.concatenate([r["first_doc"] for r in results])[:N]
    last_doc = np.concatenate([r["last_doc"] for r in results])[:N]
    bits = np.concatenate([r["label_bits"] for r in results])[:N]
    uniq_bits, inverse = np.unique(bits, return_inverse=True)
    bit_names = {int(u): "|".join(label_names[i] for i in range(len(label_names)) if (int(u) >> i) & 1) for u in uniq_bits}
    labels_u = np.array([bit_names[int(u)] for u in uniq_bits], dtype=object)
    labels = labels_u[inverse]
    mixed = np.array([bin(int(u)).count("1") > 1 for u in uniq_bits])[inverse]
    assert np.all(first_doc >= 0) and np.all(last_doc >= first_doc), "a row without a document"
    batch_of = (np.searchsorted(BATCHES[:, 0], first_doc, side="right") - 1).astype(np.int16)
    assert np.all(np.searchsorted(BATCHES[:, 0], last_doc, side="right") - 1 == batch_of), "a row crosses a tokenization batch"
    assert np.all(np.repeat(np.arange(N_BATCHES), counts)[:N] == batch_of), "row batch from documents disagrees with batch order"
    # stored in document order (unshuffled index), where four columns are monotone and delta-encode to almost nothing;
    # `position` (the shuffled position, the number in a text ID) is a permutation and dominates the size
    table = pa.table({
        "unshuffled_index": pa.array(np.arange(N, dtype=np.int32)),
        "position": pa.array(inv.astype(np.int32)),
        "tokenization_batch": pa.array(batch_of),
        "first_doc": pa.array(first_doc.astype(np.int32)),
        "last_doc": pa.array(last_doc.astype(np.int32)),
        "pile_labels": pa.array(labels.tolist()).dictionary_encode(),
        "mixed": pa.array(mixed),
    })
    pq.write_table(table, ROWS_PARQUET, compression="zstd", compression_level=19, use_dictionary=["pile_labels"],
                   column_encoding={"unshuffled_index": "DELTA_BINARY_PACKED", "position": "PLAIN", "tokenization_batch": "DELTA_BINARY_PACKED",
                                    "first_doc": "DELTA_BINARY_PACKED", "last_doc": "DELTA_BINARY_PACKED", "mixed": "RLE"})
    order = perm  # unshuffled index of each shuffled position
    out["table"] = {"file": str(ROWS_PARQUET.relative_to(env.REPO_ROOT)), "rows": int(N), "bytes": ROWS_PARQUET.stat().st_size,
                    "sha256": hashlib.sha256(ROWS_PARQUET.read_bytes()).hexdigest(), "sorted_by": "unshuffled_index (document order)",
                    "mixed_rows": int(mixed.sum()), "rows_by_label_set": {str(k): int(v) for k, v in zip(*np.unique(labels.astype(str), return_counts=True))}}
    log(f"wrote {ROWS_PARQUET} ({out['table']['bytes'] / 1e6:.1f} MB); mixed rows {out['table']['mixed_rows']}")

    # agreement with plan 1 of the research log's data check on the first-post rows it identified
    dc = json.load(open(env.PROVENANCE_DIR / "data" / "data_check.json"))
    agree = []
    for r in dc["first_post_rows_identified"]:
        j = int(order[r["shuffled"]])
        agree.append({"shuffled": r["shuffled"], "data_check_documents": [r["documents"][0], r["documents"][-1]],
                      "here": [int(first_doc[j]), int(last_doc[j])], "equal": [r["documents"][0], r["documents"][-1]] == [int(first_doc[j]), int(last_doc[j])]})
    out["plan1_data_check_rows"] = agree
    out["seconds"] = time.time() - t0
    with open(SUMMARY_JSON, "w") as f:
        json.dump(out, f, indent=1)
    log(f"wrote {SUMMARY_JSON} in {out['seconds']:.0f} s")
    return out


if __name__ == "__main__":
    main()
