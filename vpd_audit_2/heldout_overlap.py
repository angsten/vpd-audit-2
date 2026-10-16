"""Plan 1 of the research log, Part E: the held-out texts that share a 50-token span with an attack text.

    uv run python -m vpd_audit_2.heldout_overlap            (compute, check against the manifest, write the list)
    uv run python -m vpd_audit_2.heldout_overlap --verify   (recompute and compare byte for byte with the committed list)

The signed rules fix as description "every result also recomputed without the 11 held-out texts that share a 50-token
span with an attack text" (`freeze/part1.md`, Section 8). The manifest's `span_overlap` found those texts and kept only
their count. This module repeats its computation, on all A and H pools as the manifest did, and keeps which texts they
are (`freeze/amendment1.md`, entry 2.8; `freeze/amendment1_specs/table_and_run_spec.md`, Section 11.2).

It reads token ids only. No model is run, and `manifest.py` and the files whose hashes the signed rules record are
not changed. The list is written to `data/manifest/heldout_span_overlap.json`: the span length, the manifest's SHA-256,
and for each text its id, its pool, and its index within the pool.
"""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any, Callable

import numpy as np

from vpd_audit_2.manifest import OUT_DIR, SEQ_LEN, SPAN

LIST_FILE = OUT_DIR / "heldout_span_overlap.json"


def _dataset_rows(positions: list[int]) -> np.ndarray:
    from vpd_audit_2.data_check import SHUFFLED, ParquetSplit

    return ParquetSplit(*SHUFFLED, column="input_ids").token_rows(positions)


def flagged_heldout_texts(pools: dict[str, Any], token_rows: Callable[[list[int]], np.ndarray] = _dataset_rows) -> dict[str, Any]:
    """`manifest.span_overlap`'s computation, keeping the texts: every text of an H pool whose first 512 token ids
    contain a run of 50 that also occurs in the first 512 ids of some text of an A pool."""
    attack = [(n, k, t) for n in pools if pools[n]["pool"] == "A" for k, t in enumerate(pools[n]["texts"])]
    heldout = [(n, k, t) for n in pools if pools[n]["pool"] == "H" for k, t in enumerate(pools[n]["texts"])]
    A = token_rows([int(t[1:]) for _, _, t in attack])[:, :SEQ_LEN]
    H = token_rows([int(t[1:]) for _, _, t in heldout])[:, :SEQ_LEN]
    grams = {w.tobytes() for row in A for w in np.lib.stride_tricks.sliding_window_view(row, SPAN)}
    hit = [any(w.tobytes() in grams for w in np.lib.stride_tricks.sliding_window_view(row, SPAN)) for row in H]
    texts = [{"text": t, "pool": n, "index": k} for (n, k, t), flagged in zip(heldout, hit) if flagged]
    return {"span_tokens": SPAN, "over": "the 512 ids the model sees", "attack_rows": len(attack), "held_out_rows": len(heldout),
            "held_out_rows_sharing": len(texts), "texts": texts}


def build() -> dict[str, Any]:
    """The list, checked against the count the manifest recorded."""
    manifest_bytes = (OUT_DIR / "manifest.json").read_bytes()
    man = json.loads(manifest_bytes)
    out = flagged_heldout_texts(man["pools"])
    recorded = man["report"]["held_out_rows_sharing_a_50_token_span_with_an_attack_row"]
    for key in ("span_tokens", "over", "attack_rows", "held_out_rows", "held_out_rows_sharing"):
        assert out[key] == recorded[key], f"the recomputed overlap differs from the manifest's record in {key}"
    out["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    return out


def serialize(out: dict[str, Any]) -> bytes:
    return (json.dumps(out, indent=1, sort_keys=True) + "\n").encode()


def main(verify: bool = False) -> None:
    data = serialize(build())
    if verify:
        same = LIST_FILE.read_bytes() == data
        print(f"[heldout_overlap] recomputed list equals the committed {LIST_FILE.name}: {same}")
        assert same
        return
    LIST_FILE.write_bytes(data)
    print(f"[heldout_overlap] wrote {LIST_FILE}: {json.loads(data)['held_out_rows_sharing']} held-out texts")


if __name__ == "__main__":
    main(verify="--verify" in sys.argv[1:])
