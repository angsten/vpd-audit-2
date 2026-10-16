"""Question (k) and gate G5 of plan 1 of the research log: where the validation rows come from, on the CPU, with no model.

    uv run python -m vpd_audit_2.data_check

The tokenized split is built in three public stages (dataset card of the shuffled split, and
`scripts/shuffle_and_reupload_dataset.py` at the run's commit 85c6b70):
  1. `monology/pile-uncopyrighted`, split "train" -> `danbraunai/pile-uncopyrighted`: the last 100K
     documents become `test`, the 1M before them `val`;
  2. -> `danbraunai/pile-uncopyrighted-tok`: `tokenize_and_concatenate` with the GPT-NeoX-20B tokenizer,
     batches of 1,000 documents joined by EOS, cut into 513-token rows, the tail of each batch dropped;
  3. -> `danbraunai/pile-uncopyrighted-tok-shuffled`: `Dataset.shuffle(seed=42)`.

This module checks the chain on a handful of rows and measures what the leakage bound needs:
  - the shuffled `val` rows i equal the unshuffled rows perm[i], perm = default_rng(42).permutation(N);
  - tokenizing the first 2,000 `val` documents the authors' way reproduces the first unshuffled rows;
  - every first-post row (shuffled rows 0 to 2,047) gets its unshuffled index, and the few that land in
    the two tokenized batches get their documents and Pile subsets;
  - the first-post sets E (rows 0 to 1,023) and D_unif (1,024 to 2,047), cut to 512 tokens, hash to the
    earlier project's recorded SHA-256;
  - every `val` document's length in characters and its Pile subset, for the bound of plan section 5.

Writes provenance/data/data_check.json (committed); the parquet files and the per-document lengths stay
under <cache>/hf and <cache>/data_check/. Nothing here builds a text pool.
"""

from __future__ import annotations

import collections
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env

SHUFFLED = ("danbraunai/pile-uncopyrighted-tok-shuffled", "6f141f6e4edc32fea842f2ece0d3477b15c3dc90")
UNSHUFFLED = ("danbraunai/pile-uncopyrighted-tok", "234360bcd482f77c2760b743c2bca70da1c4bdfd")
RESPLIT = ("danbraunai/pile-uncopyrighted", "188e502a27a7d7d7def4568f68447decf647072c")
MONOLOGY = ("monology/pile-uncopyrighted", "3be90335b66f24456a5d6659d9c8d208c0357119")
TOKENIZER = "EleutherAI/gpt-neox-20b"
SPLIT = "val"
ROW_LEN = 513
SEQ_LEN = 512
SHUFFLE_SEED = 42
DOCS_PER_BATCH = 1000  # `datasets.map(batched=True)` default batch size, as stage 2 ran it
N_TOKENIZED_BATCHES = 2
FIRST_POST = {"E": (0, 1024, "81f8b75b4c31fc95836841062b0c49c4237b3e83dce43397b8ad7e927c18d103"),
              "D_unif": (1024, 2048, "1807c12e26c0baec8065381127ee9b049d22aa85670680e03ea5e9b56ac8ed20")}
SAMPLE_SEED = 20261001
POOL_SIZES = (1024, 1024)

OUT_JSON = env.PROVENANCE_DIR / "data" / "data_check.json"
WORK = env.CACHE_DIR / "data_check"


def log(msg: str) -> None:
    print(f"[data-check] {msg}", flush=True)


# ----------------------------------------------------------------------------- parquet access


class ParquetSplit:
    """The `val` parquet files of one dataset at a pinned revision, downloaded once into the cache, with
    row access by global index (files in name order, rows in file order: the streaming order)."""

    def __init__(self, repo: str, revision: str, column: str) -> None:
        import pyarrow.parquet as pq
        from huggingface_hub import HfApi, hf_hub_download

        self.repo, self.revision, self.column = repo, revision, column
        info = HfApi().dataset_info(repo, revision=revision, files_metadata=True)
        names = sorted(s.rfilename for s in info.siblings if s.rfilename.startswith(f"data/{SPLIT}-"))
        assert names, f"no {SPLIT} files in {repo}@{revision}"
        self.files = [Path(hf_hub_download(repo, n, repo_type="dataset", revision=revision)) for n in names]
        self.names = names
        self.pq = [pq.ParquetFile(f) for f in self.files]
        self.file_rows = np.array([p.metadata.num_rows for p in self.pq], dtype=np.int64)
        self.file_start = np.concatenate([[0], np.cumsum(self.file_rows)[:-1]])
        self.n_rows = int(self.file_rows.sum())
        self.rg_rows = [[p.metadata.row_group(g).num_rows for g in range(p.metadata.num_row_groups)] for p in self.pq]
        self._cache: dict[tuple[int, int], Any] = {}

    def _locate(self, i: int) -> tuple[int, int, int]:
        f = int(np.searchsorted(self.file_start, i, side="right") - 1)
        r = i - int(self.file_start[f])
        g = 0
        while r >= self.rg_rows[f][g]:
            r -= self.rg_rows[f][g]
            g += 1
        return f, g, r

    def _row_group(self, f: int, g: int) -> Any:
        key = (f, g)
        if key not in self._cache:
            if len(self._cache) >= 4:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = self.pq[f].read_row_group(g, columns=[self.column]).column(self.column).combine_chunks()
        return self._cache[key]

    def token_rows(self, indices: list[int] | np.ndarray) -> np.ndarray:
        out = np.empty((len(indices), ROW_LEN), dtype=np.int32)
        order = sorted(range(len(indices)), key=lambda k: self._locate(int(indices[k]))[:2])
        for k in order:
            f, g, r = self._locate(int(indices[k]))
            row = np.asarray(self._row_group(f, g)[r].values.to_numpy(zero_copy_only=False), dtype=np.int32)
            assert row.shape == (ROW_LEN,), (self.repo, int(indices[k]), row.shape)
            out[k] = row
        return out

    def token_block(self, start: int, stop: int) -> np.ndarray:
        return self.token_rows(np.arange(start, stop))


def hash_ids(ids: np.ndarray) -> str:
    """The earlier project's set hash: SHA-256 of the C-contiguous int32 bytes (vpd_audit/data.py hash_ids)."""
    return hashlib.sha256(np.ascontiguousarray(ids, dtype=np.int32).tobytes()).hexdigest()


# ----------------------------------------------------------------------------- checks


def check_hf_shuffle_semantics() -> dict[str, Any]:
    """`Dataset.shuffle(seed)` in the installed `datasets` uses np.random.default_rng(seed).permutation(len)."""
    import datasets

    n = 5000
    ds = datasets.Dataset.from_dict({"i": np.arange(n)}).shuffle(seed=SHUFFLE_SEED)
    got = np.asarray(ds["i"])
    want = np.random.default_rng(SHUFFLE_SEED).permutation(n)
    return {"datasets_version": datasets.__version__, "n": n, "equal": bool(np.array_equal(got, want))}


def monology_train_files() -> dict[str, Any]:
    """Which files `load_dataset("monology/pile-uncopyrighted", split="train")` resolves to (no data download)."""
    from datasets import load_dataset_builder

    b = load_dataset_builder(MONOLOGY[0], revision=MONOLOGY[1])
    files = {str(split): sorted(str(p).split("/")[-2] + "/" + str(p).split("/")[-1] for p in v) for split, v in b.config.data_files.items()}
    return {"splits": {k: (v if len(v) <= 4 else v[:2] + ["..."] + v[-2:]) for k, v in files.items()},
            "n_files": {k: len(v) for k, v in files.items()},
            "val_or_test_file_in_train": any(("val" in f or "test" in f) for f in files.get("train", []))}


def tokenizer_info() -> tuple[Any, dict[str, Any]]:
    from huggingface_hub import HfApi
    from transformers import AutoTokenizer

    rev = HfApi().model_info(TOKENIZER).sha
    tok = AutoTokenizer.from_pretrained(TOKENIZER, revision=rev)
    return tok, {"name": TOKENIZER, "revision": rev, "eos_token": tok.eos_token, "eos_token_id": tok.eos_token_id,
                 "vocab_size": tok.vocab_size, "len": len(tok)}


def tokenize_batches(tok: Any, docs: list[str]) -> tuple[np.ndarray, list[int], list[np.ndarray]]:
    """The authors' `tokenize_and_concatenate` (param_decomp/data.py at 74146b5, unchanged from spd/data.py at 85c6b70
    apart from a collate argument) on `docs`, one call per batch of 1,000 documents as `map(batched=True)` makes them.
    Returns the rows, the row count per batch, and each batch's full token stream (before the tail is dropped)."""
    import datasets

    from param_decomp.data import tokenize_and_concatenate

    rows, counts, streams = [], [], []
    for b in range(0, len(docs), DOCS_PER_BATCH):
        chunk = docs[b : b + DOCS_PER_BATCH]
        assert len(chunk) == DOCS_PER_BATCH
        ds = datasets.Dataset.from_dict({"text": chunk})
        out = tokenize_and_concatenate(ds, tok, column_name="text", max_length=ROW_LEN, add_bos_token=False, num_proc=1, to_lower=False)
        r = np.stack([np.asarray(x["input_ids"]) for x in out]).astype(np.int32)
        rows.append(r)
        counts.append(r.shape[0])
        # the same stream, recomputed here to locate documents: EOS-joined, 20 character chunks, encoded separately
        full = tok.eos_token.join(chunk)
        n = 20
        cl = (len(full) - 1) // n + 1
        streams.append(np.concatenate([tok.encode(full[i * cl : (i + 1) * cl], add_special_tokens=False) for i in range(n)]).astype(np.int32))
        assert np.array_equal(streams[-1][: r.size], r.reshape(-1)), "stream and rows disagree"
    return np.concatenate(rows), counts, streams


def documents_of_row(stream: np.ndarray, row_in_batch: int, eos_id: int, first_doc: int) -> list[int]:
    """The documents (indices in the `val` split) that row `row_in_batch` of a batch's stream covers: document k of
    the batch spans the tokens between its (k-1)-th and k-th EOS."""
    eos_pos = np.flatnonzero(stream == eos_id)
    a, b = row_in_batch * ROW_LEN, (row_in_batch + 1) * ROW_LEN
    d_start = int(np.searchsorted(eos_pos, a, side="left"))  # EOS tokens before position a
    d_end = int(np.searchsorted(eos_pos, b - 1, side="left"))
    return list(range(first_doc + d_start, first_doc + d_end + 1))


# ----------------------------------------------------------------------------- the leakage bound


def document_lengths(resplit: ParquetSplit) -> tuple[np.ndarray, list[str]]:
    import pyarrow.compute as pc

    WORK.mkdir(parents=True, exist_ok=True)
    cache = WORK / "val_document_chars.npz"
    if cache.is_file():
        z = np.load(cache, allow_pickle=False)
        return z["chars"], list(z["subset"])
    chars, subsets = [], []
    for k, p in enumerate(resplit.pq):
        t = p.read(columns=["text", "meta"])
        chars.append(pc.utf8_length(t.column("text")).to_numpy().astype(np.int64))
        subsets += t.column("meta").combine_chunks().field("pile_set_name").to_pylist()
        log(f"lengths: file {k + 1}/{len(resplit.pq)}")
    c = np.concatenate(chars)
    np.savez(cache, chars=c, subset=np.asarray(subsets))
    return c, subsets


def leakage_bound(chars: np.ndarray, n_rows: int, eos_tokens: int) -> dict[str, Any]:
    """Plan section 5: n_d from characters times tokens per character over 513; m = sum n_d^2 / sum n_d;
    expected cross-pool same-document row pairs ~ a b (m - 1) / N. Beside it, the same count with the rows a
    document touches, k_d, in place of the fraction it fills (k_d >= 1, with a random start offset)."""
    total_tokens = n_rows * ROW_LEN  # the dropped batch tails (under 513 tokens each, 1,000 batches) are left out
    tokens_per_char = (total_tokens - eos_tokens) / float(chars.sum())
    L = chars * tokens_per_char + 1.0  # each document's tokens, its EOS included
    n_d = L / ROW_LEN
    m = float((n_d**2).sum() / n_d.sum())
    a, b = POOL_SIZES
    plan_bound = a * b * (m - 1) / n_rows
    # rows touched: L - 1 = 513 u + v; k = u + 1, or u + 2 with probability v / 513
    Lm1 = np.maximum(np.rint(L) - 1, 0)
    u, v = np.floor_divide(Lm1, ROW_LEN), np.mod(Lm1, ROW_LEN)
    pv = v / ROW_LEN
    ek_km1 = (1 - pv) * (u + 1) * u + pv * (u + 2) * (u + 1)
    touched_bound = a * b * float(ek_km1.sum()) / n_rows**2
    q = np.quantile(n_d, [0.5, 0.9, 0.99, 0.999])
    order = np.argsort(-n_d)
    share_sq_top = float((n_d[order[:100]] ** 2).sum() / (n_d**2).sum())
    return {
        "n_documents": int(chars.size), "N_rows": n_rows, "total_chars": int(chars.sum()), "tokens_per_char": tokens_per_char,
        "eos_tokens_assumed": eos_tokens, "sum_n_d": float(n_d.sum()),
        "m": m, "pool_sizes": [a, b], "expected_cross_pool_same_document_pairs_plan_formula": plan_bound,
        "expected_cross_pool_same_document_pairs_rows_touched": touched_bound,
        "n_d_quantiles_50_90_99_999": [float(x) for x in q], "n_d_max": float(n_d.max()),
        "share_of_rows_in_documents_longer_than_one_row": float(n_d[n_d > 1].sum() / n_d.sum()),
        "share_of_sum_n_d_squared_from_100_longest_documents": share_sq_top,
    }


# ----------------------------------------------------------------------------- main


def main() -> dict[str, Any]:
    t0 = time.time()
    out: dict[str, Any] = {"revisions": {name: {"repo": r, "revision": v} for name, (r, v) in
                                         {"shuffled": SHUFFLED, "unshuffled": UNSHUFFLED, "resplit": RESPLIT, "monology": MONOLOGY}.items()}}
    out["hf_shuffle_semantics"] = check_hf_shuffle_semantics()
    log(f"shuffle semantics: {out['hf_shuffle_semantics']}")
    out["monology_train_split_files"] = monology_train_files()
    log(f"monology train split: {out['monology_train_split_files']['n_files']}")

    shuf = ParquetSplit(*SHUFFLED, column="input_ids")
    unshuf = ParquetSplit(*UNSHUFFLED, column="input_ids")
    resplit = ParquetSplit(*RESPLIT, column="text")
    out["val_rows"] = {"shuffled": shuf.n_rows, "unshuffled": unshuf.n_rows, "resplit_documents": resplit.n_rows,
                       "shuffled_files": shuf.names, "shuffled_rows_per_file": shuf.file_rows.tolist(),
                       "shuffled_row_groups_per_file": [len(x) for x in shuf.rg_rows]}
    assert shuf.n_rows == unshuf.n_rows
    N = shuf.n_rows
    perm = np.random.default_rng(SHUFFLE_SEED).permutation(N)

    # first-post rows: E and D_unif in stream order, cut to 512, against the earlier project's hashes
    first = shuf.token_block(0, 2048)
    out["first_post_sets"] = {}
    for name, (a, b, want) in FIRST_POST.items():
        got = hash_ids(first[a:b, :SEQ_LEN])
        out["first_post_sets"][name] = {"rows": [a, b - 1], "sha256_ids_512": got, "earlier_project_sha256": want, "equal": got == want}
        log(f"{name}: rows {a}..{b - 1} hash equal to the earlier project's: {got == want}")
    out["first_post_rows_all_513_tokens"] = bool(first.shape == (2048, ROW_LEN))

    # the permutation, on a handful of rows
    rng = np.random.default_rng(SAMPLE_SEED)
    sample = sorted(set([0, 1, 2, 3, 4, 1023, 1024, 2047] + rng.integers(0, N, size=8).tolist()))
    a_rows = shuf.token_rows(sample)
    b_rows = unshuf.token_rows(perm[sample])
    eq = [bool(np.array_equal(a_rows[k], b_rows[k])) for k in range(len(sample))]
    out["permutation_check"] = {"seed": SHUFFLE_SEED, "rows": [{"shuffled": int(i), "unshuffled": int(perm[i]), "equal": e} for i, e in zip(sample, eq)],
                                "all_equal": all(eq)}
    log(f"permutation: {sum(eq)}/{len(eq)} rows equal")

    # the tokenization, on the first two batches of 1,000 documents
    tok, tok_info = tokenizer_info()
    out["tokenizer"] = tok_info
    docs_tbl = resplit.pq[0].read_row_group(0, columns=["text", "meta"])
    docs = docs_tbl.column("text").to_pylist()[: N_TOKENIZED_BATCHES * DOCS_PER_BATCH]
    subsets_first = docs_tbl.column("meta").combine_chunks().field("pile_set_name").to_pylist()[: len(docs)]
    t1 = time.time()
    rows, counts, streams = tokenize_batches(tok, docs)
    tok_seconds = time.time() - t1
    ref = unshuf.token_block(0, rows.shape[0])
    row_eq = [bool(np.array_equal(rows[k], ref[k])) for k in range(rows.shape[0])]
    out["tokenization_check"] = {"documents": [0, len(docs) - 1], "batches": N_TOKENIZED_BATCHES, "rows_per_batch": counts,
                                 "rows_compared": len(row_eq), "rows_equal": int(sum(row_eq)), "all_equal": all(row_eq),
                                 "first_unequal_row": next((k for k, e in enumerate(row_eq) if not e), None),
                                 "seconds": tok_seconds, "documents_per_second": len(docs) / tok_seconds}
    log(f"tokenization: {sum(row_eq)}/{len(row_eq)} unshuffled rows reproduced from documents 0..{len(docs) - 1}")

    # first-post rows: unshuffled index of each, documents of those inside the tokenized batches
    batch_start = np.concatenate([[0], np.cumsum(counts)])
    mapped = []
    for i in range(2048):
        j = int(perm[i])
        rec: dict[str, Any] = {"shuffled": i, "unshuffled": j}
        if j < batch_start[-1]:
            bi = int(np.searchsorted(batch_start, j, side="right") - 1)
            docs_ix = documents_of_row(streams[bi], j - int(batch_start[bi]), tok.eos_token_id, bi * DOCS_PER_BATCH)
            rec["documents"] = docs_ix
            rec["pile_set_names"] = [subsets_first[d] for d in docs_ix]
        mapped.append(rec)
    out["first_post_rows_unshuffled_index"] = [r["unshuffled"] for r in mapped]
    out["first_post_rows_identified"] = [r for r in mapped if "documents" in r]
    log(f"first-post rows inside the tokenized batches: {len(out['first_post_rows_identified'])}")

    # the bound
    chars, subsets = document_lengths(resplit)
    eos_tokens = (DOCS_PER_BATCH - 1) * (resplit.n_rows // DOCS_PER_BATCH)
    out["leakage_bound"] = leakage_bound(chars, N, eos_tokens)
    out["pile_set_name_counts_val_documents"] = dict(collections.Counter(subsets).most_common())
    out["full_recovery_estimate"] = {
        "what": "tokenize all 1,000,000 val documents in batches of 1,000 the authors' way, giving each unshuffled row's documents; then shuffled row i -> unshuffled perm[i]",
        "documents_per_second_single_process_here": len(docs) / tok_seconds,
        "hours_single_process": resplit.n_rows / (len(docs) / tok_seconds) / 3600,
    }
    out["seconds"] = time.time() - t0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1)
    log(f"bound: {json.dumps(out['leakage_bound'])}")
    log(f"wrote {OUT_JSON} in {out['seconds']:.0f} s")
    return out


if __name__ == "__main__":
    main()
