"""Plan 6 of the research log, review of report 2 of the research log: B1's original-label arm, printed (report 3 of the research log).

    uv run python -m vpd_audit_2.pilot_b_original     (reads part_b/sealed/b1_raw.json; writes part_b/original_arm.json)

A ruling recorded before the pilot: the original-label arm is a measurement plan 6 of the research log's Section 4 allows, being neither V nor a freed arm. This
module reads the original arm only: the per-text harms under the keys "original|s{s}|n{n}" (versions (i) and (iii), one
shared-source search per set and seed, read at 20, 40, and 80 steps) and v2["t{i}|s{s}"]["harm"]["original"] (version
(ii), per text). It reads no freed arm, no J, no G, and no stochastic value, and writes no difference between arms.
Harms are position means of the float64 KL, in nats per token.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np

from vpd_audit_2 import env

PILOT = env.REPO_ROOT / "results" / "s4_pilot"
READINGS = (20, 40, 80)
N_TEXTS = 32


def _sd(x: np.ndarray, axis: int) -> np.ndarray:
    return np.std(x, axis=axis, ddof=1)


def _range(x: np.ndarray) -> dict[str, float]:
    return {"mean": float(np.mean(x)), "min": float(np.min(x)), "max": float(np.max(x))}


def set_versions(raw: dict[str, Any]) -> dict[str, Any]:
    """Versions (i) and (iii): per reading, H[text, partition, seed], each set's mean per seed, and the SDs over seeds."""
    parts = raw["partitions"]
    seeds = sorted({int(k.split("|")[1][1:]) for k in parts["1"]["set0"]["harm"] if k.startswith("original|")})
    out: dict[str, Any] = {"seeds": seeds}
    for n in READINGS:
        H = np.full((N_TEXTS, 4, len(seeds)), np.nan)
        sets = {}
        for p in range(1, 5):
            for sk in ("set0", "set1"):
                d = parts[str(p)][sk]
                vals = np.array([d["harm"][f"original|s{s}|n{n}"] for s in seeds])  # [seed, text in set]
                H[d["texts"], p - 1, :] = vals.T
                m = vals.mean(axis=1)
                sets[f"p{p}|{sk}"] = {"texts": list(d["texts"]), "mean_per_seed": m.tolist(), "sd_over_seeds": float(_sd(m, 0))}
        assert not np.isnan(H).any()
        sd_tp = _sd(H, 2)  # [text, partition]: the SD over seeds of one text's harm within one partition
        pooled = np.sqrt(np.mean(sd_tp ** 2, axis=1))  # per text, pooled over its 4 partitions
        text_mean = H.mean(axis=(1, 2))
        set_sd = np.array([v["sd_over_seeds"] for v in sets.values()])
        out[str(n)] = {
            "per_text_per_seed": {str(i): {f"p{p + 1}": H[i, p].tolist() for p in range(4)} for i in range(N_TEXTS)},
            "sd_over_seeds_per_text": {str(i): {f"p{p + 1}": float(sd_tp[i, p]) for p in range(4)} for i in range(N_TEXTS)},
            "sd_over_seeds_per_text_pooled": [float(x) for x in pooled],
            "text_mean": [float(x) for x in text_mean],
            "per_set": sets,
            "summary": {
                "text_mean_over_texts": _range(text_mean),
                "sd_over_seeds_per_text_pooled": _range(pooled),
                "sd_over_seeds_per_text_partition": _range(sd_tp),
                "set_mean_sd_over_seeds": _range(set_sd),
                "all_values": _range(H),
            },
        }
    return out


def version_ii(raw: dict[str, Any], partitions: dict[str, Any] | None = None) -> dict[str, Any]:
    """Version (ii): per text and seed, the original arm's harm in the fill form (deciding) and the zero form."""
    v2 = raw["v2"]
    seeds = sorted({int(k.split("|")[1][1:]) for k in v2 if k.startswith("t0|")})
    out: dict[str, Any] = {"seeds": seeds}
    for form in ("fill", "zero"):
        H = np.array([[v2[f"t{i}|s{s}"]["harm"]["original"][form] for s in seeds] for i in range(N_TEXTS)])  # [text, seed]
        sd = _sd(H, 1)
        rec: dict[str, Any] = {
            "per_text_per_seed": {str(i): H[i].tolist() for i in range(N_TEXTS)},
            "sd_over_seeds_per_text": [float(x) for x in sd],
            "text_mean": [float(x) for x in H.mean(axis=1)],
            "mean_over_32_per_seed": H.mean(axis=0).tolist(),
            "summary": {"text_mean_over_texts": _range(H.mean(axis=1)), "sd_over_seeds_per_text": _range(sd), "all_values": _range(H)},
        }
        if partitions is not None:  # version (ii) searches per text; partition 1's sets are given for comparison only
            rec["partition1_sets"] = {}
            for sk in ("set0", "set1"):
                m = H[partitions["1"][sk]].mean(axis=0)
                rec["partition1_sets"][sk] = {"mean_per_seed": m.tolist(), "sd_over_seeds": float(_sd(m, 0))}
        out[form] = rec
    return out


def original_arm(raw: dict[str, Any]) -> dict[str, Any]:
    return {"versions_i_iii": set_versions(raw), "version_ii": version_ii(raw, raw.get("partition_definition")),
            "units": "nats per token (position mean of the float64 KL)", "arm": "original labels only",
            "source": "results/s4_pilot/part_b/sealed/b1_raw.json"}


def main() -> None:
    pb = PILOT / "part_b"
    raw = json.load(open(pb / "sealed" / "b1_raw.json"))
    out = original_arm(raw)
    with open(pb / "original_arm.json", "w") as f:
        json.dump(out, f, indent=1)
    s = out["versions_i_iii"]
    for n in READINGS:
        m = s[str(n)]["summary"]
        print(f"(i)/(iii) at {n}: text means {m['text_mean_over_texts']}; per-text seed SD (pooled) {m['sd_over_seeds_per_text_pooled']}; "
              f"set-mean seed SD {m['set_mean_sd_over_seeds']}")
    for form in ("fill", "zero"):
        m = out["version_ii"][form]["summary"]
        print(f"(ii) {form}: text means {m['text_mean_over_texts']}; per-text seed SD {m['sd_over_seeds_per_text']}")
    print(f"wrote {pb / 'original_arm.json'}")


if __name__ == "__main__":
    main()
