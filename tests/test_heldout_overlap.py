"""Session 5, plan 1, Part E: the committed list of held-out texts that share a 50-token span with an attack text.

The list itself is checked without the dataset: 11 entries, equal to the manifest's recorded count, all in held-out
pools. The computation is checked on a made-up input with a known answer. Recomputing the list from the token ids is
the command `python -m vpd_audit_2.heldout_overlap --verify`, which needs the dataset.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np

from vpd_audit_2 import heldout_overlap as HO
from vpd_audit_2.manifest import OUT_DIR, SEQ_LEN, SPAN


def test_the_committed_list_has_11_texts_all_in_heldout_pools():
    listed = json.loads(HO.LIST_FILE.read_text())
    manifest_bytes = (OUT_DIR / "manifest.json").read_bytes()
    man = json.loads(manifest_bytes)
    recorded = man["report"]["held_out_rows_sharing_a_50_token_span_with_an_attack_row"]
    texts = listed["texts"]
    assert len(texts) == 11  # the signed rules' 11 held-out texts
    assert len(texts) == listed["held_out_rows_sharing"] == recorded["held_out_rows_sharing"]  # the manifest's recorded count
    assert listed["span_tokens"] == recorded["span_tokens"] == 50
    assert (listed["attack_rows"], listed["held_out_rows"]) == (recorded["attack_rows"], recorded["held_out_rows"]) == (2048, 2048)
    assert listed["manifest_sha256"] == hashlib.sha256(manifest_bytes).hexdigest()
    assert listed["manifest_sha256"].startswith("29d709c9") and listed["manifest_sha256"].endswith("7d71")  # the signed manifest
    assert len({t["text"] for t in texts}) == 11
    heldout_pools = {f"H{j}" for j in range(1, 17)}
    for t in texts:
        pool = man["pools"][t["pool"]]
        assert t["pool"] in heldout_pools and pool["pool"] == "H" and pool["side"] == "held-out"  # every text is in a held-out pool
        assert pool["texts"][t["index"]] == t["text"] and 0 <= t["index"] < 128  # its index within the pool
        assert man["texts"][t["text"]]["batch_side"] == "held-out"
    assert HO.LIST_FILE.read_bytes() == HO.serialize(listed)  # written as the module writes it


def test_the_computation_flags_exactly_the_heldout_texts_that_share_a_span_of_50():
    rng = np.random.default_rng(0)
    rows = rng.integers(0, 50_000, size=(8, SEQ_LEN + 1)).astype(np.int32)  # rows 0 to 3 attack, 4 to 7 held-out
    rows[4, 100 : 100 + SPAN] = rows[1, 300 : 300 + SPAN]  # a span of exactly 50 shared with an attack text
    rows[5, 0 : SPAN - 1] = rows[2, 10 : 10 + SPAN - 1]  # only 49 shared: not flagged
    rows[6, SEQ_LEN - SPAN + 1 : SEQ_LEN + 1] = rows[3, 0:SPAN]  # 50 shared, but the last lies beyond the 512 ids the model sees
    rows[7, 200 : 200 + SPAN] = rows[4, 400 : 400 + SPAN]  # shared with another held-out text only
    pools = {
        "A1": {"pool": "A", "texts": ["v0", "v1"]}, "A2": {"pool": "A", "texts": ["v2", "v3"]},
        "H1": {"pool": "H", "texts": ["v4", "v5"]}, "H2": {"pool": "H", "texts": ["v6", "v7"]},
        "C1": {"pool": "C", "texts": ["v1"]},  # other pools take no part
    }
    asked: list[list[int]] = []

    def token_rows(positions: list[int]) -> np.ndarray:
        asked.append(list(positions))
        return rows[positions]

    out = HO.flagged_heldout_texts(pools, token_rows)
    assert asked == [[0, 1, 2, 3], [4, 5, 6, 7]]  # the A pools, then the H pools, and nothing else
    assert out["texts"] == [{"text": "v4", "pool": "H1", "index": 0}]
    assert (out["attack_rows"], out["held_out_rows"], out["held_out_rows_sharing"], out["span_tokens"]) == (4, 4, 1, 50)
    rows[6, SEQ_LEN - SPAN : SEQ_LEN] = rows[3, 0:SPAN]  # moved one token earlier, the span lies within the 512
    assert [t["text"] for t in HO.flagged_heldout_texts(pools, token_rows)["texts"]] == ["v4", "v6"]
