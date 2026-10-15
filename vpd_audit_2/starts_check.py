"""Session 6, plan 1, Section 2.2: the starts check. How starts 9 to 13 were drawn, beside starts 1 to 8.

One command prints a short report; its output is committed to `results/s6_starts/starts_check.txt`:

    uv run python -m vpd_audit_2.starts_check

  1. Every start 1 to 64 of `results/s4_pilot/starts/starts_1_64.npz`: the SHA-256 of its module arrays' bytes,
     concatenated in the layout's order, recomputed and compared with the json's `sha256`. Starts 1 to 16 compared with
     the committed `data/manifest/starts.npz` entry for entry (dtype, shape, and bytes of every module array).
  2. The json's `generator` field, and the `seed_key` and `seed` of starts 1 to 13. Then every start 1 to 64 drawn again
     from `seed_of("start", s)` with the generator the json names (one CPU torch generator per start, `torch.rand` of
     shape [1, 1, C_l + 1] in float32, module by module in the layout's order), and compared with the file byte for byte;
     and each recorded `seed` compared with `seed_of("start", s)`.
  3. For each start 1 to 13, over all of its entries (the delta entries included), in float64: mean, standard deviation
     (population, ddof = 0), minimum, maximum, the share of entries below 0.5, and the Kolmogorov-Smirnov distance from the
     uniform distribution on [0, 1). Starts 1 to 8 and 9 to 13 as two groups. A start among 9 to 13 is flagged if its mean
     or its KS distance lies outside the range spanned by starts 1 to 8 by more than that range's width.
  4. For each start 1 to 13, its 24 delta entries (the last entry of each module's array): their mean and minimum. A delta
     entry's mask is the raw setting value, with no label under it.
  5. The number of entries per start and the layout's module count.

Description only: the report says what it finds and decides nothing.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env

STARTS_NPZ = env.REPO_ROOT / "results" / "s4_pilot" / "starts" / "starts_1_64.npz"
STARTS_JSON = env.REPO_ROOT / "results" / "s4_pilot" / "starts" / "starts_1_64.json"
MANIFEST_STARTS = env.REPO_ROOT / "data" / "manifest" / "starts.npz"
N_STARTS = 64
N_MANIFEST = 16  # starts 1 to 16 are also in the manifest's own file
PILOT = tuple(range(1, 9))
RUN = tuple(range(9, 14))
FLAG_METRICS = ("mean", "ks")


def _sha_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(npz: Path = STARTS_NPZ, meta_json: Path = STARTS_JSON) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    meta = json.load(open(meta_json))
    with np.load(npz, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    return arrays, meta


def module_arrays(arrays: dict[str, np.ndarray], layout: list, s: int) -> list[np.ndarray]:
    """Start s's module arrays, in the layout's order."""
    return [arrays[f"s{s}|{name}"] for name, _ in layout]


def start_sha256(parts: list[np.ndarray]) -> str:
    """The SHA-256 of the module arrays' bytes, concatenated in order: how `pilot.make_extended_starts` recorded it."""
    return hashlib.sha256(b"".join(np.asarray(p).tobytes() for p in parts)).hexdigest()


def hash_check(arrays: dict[str, np.ndarray], meta: dict[str, Any], n: int = N_STARTS) -> dict[str, Any]:
    layout = meta["layout"]
    got = {s: start_sha256(module_arrays(arrays, layout, s)) for s in range(1, n + 1)}
    mismatched = [s for s in range(1, n + 1) if got[s] != meta["starts"][str(s)]["sha256"]]
    return {"checked": n, "matched": n - len(mismatched), "mismatched": mismatched}


def manifest_check(arrays: dict[str, np.ndarray], manifest_arrays: dict[str, np.ndarray], layout: list, n: int = N_MANIFEST) -> dict[str, Any]:
    """Starts 1 to n against the manifest's file, entry for entry: every module array's dtype, shape, and bytes."""
    differing = []
    for s in range(1, n + 1):
        for name, _ in layout:
            key = f"s{s}|{name}"
            a, b = arrays.get(key), manifest_arrays.get(key)
            if a is None or b is None or a.dtype != b.dtype or a.shape != b.shape or a.tobytes() != b.tobytes():
                differing.append(key)
    return {"checked": n, "equal": n - len({k.split("|")[0] for k in differing}), "differing": differing}


def redraw(arrays: dict[str, np.ndarray], meta: dict[str, Any], n: int = N_STARTS) -> dict[str, Any]:
    """Every start 1 to n drawn again from `seed_of("start", s)` by the scheme the json names, and compared with the file
    byte for byte (dtype, shape, and bytes of every module array); and each recorded seed against `seed_of("start", s)`."""
    import torch

    from vpd_audit_2.manifest import seed_of

    layout = meta["layout"]
    differing, seed_differs = [], []
    for s in range(1, n + 1):
        seed = seed_of("start", s)
        if seed != meta["starts"][str(s)]["seed"]:
            seed_differs.append(s)
        g = torch.Generator(device="cpu")
        g.manual_seed(seed)
        for name, c in layout:
            x = torch.rand((1, 1, int(c) + 1), generator=g, dtype=torch.float32).numpy()
            a = arrays[f"s{s}|{name}"]
            if x.dtype != a.dtype or x.shape != a.shape or x.tobytes() != a.tobytes():
                differing.append(s)
                break
    return {"checked": n, "identical": n - len(differing), "differing": differing, "seed_differs": seed_differs, "torch": str(torch.__version__)}


def delta_entries(arrays: dict[str, np.ndarray], layout: list, s: int) -> np.ndarray:
    """Start s's 24 delta entries: the last entry of each module's array, in the layout's order, in float64."""
    return np.array([float(np.asarray(arrays[f"s{s}|{name}"]).reshape(-1)[-1]) for name, _ in layout], dtype=np.float64)


def ks_uniform(x: np.ndarray) -> float:
    """The Kolmogorov-Smirnov distance between the sample's empirical distribution and the uniform one on [0, 1):
    sup over x of |F_n(x) - x|, attained at a sample point from one side or the other."""
    v = np.sort(np.asarray(x, dtype=np.float64).ravel())
    n = v.size
    i = np.arange(1, n + 1, dtype=np.float64)
    return float(max(np.max(i / n - v), np.max(v - (i - 1) / n)))


def describe(flat: np.ndarray) -> dict[str, float]:
    v = np.asarray(flat, dtype=np.float64).ravel()
    return {"n": int(v.size), "mean": float(v.mean()), "sd": float(v.std(ddof=0)), "min": float(v.min()), "max": float(v.max()),
            "below_half": float(np.mean(v < 0.5)), "ks": ks_uniform(v)}


def flags(stats: dict[int, dict[str, float]], reference: tuple[int, ...] = PILOT, candidates: tuple[int, ...] = RUN,
          metrics: tuple[str, ...] = FLAG_METRICS) -> dict[str, dict[str, Any]]:
    """For each metric: the range [lo, hi] spanned by the reference starts, its width w, and the candidates whose value is
    below lo - w or above hi + w."""
    out = {}
    for m in metrics:
        vals = [stats[s][m] for s in reference]
        lo, hi = min(vals), max(vals)
        w = hi - lo
        out[m] = {"lo": lo, "hi": hi, "width": w, "flagged": [s for s in candidates if stats[s][m] < lo - w or stats[s][m] > hi + w]}
    return out


def check(npz: Path = STARTS_NPZ, meta_json: Path = STARTS_JSON, manifest_npz: Path = MANIFEST_STARTS) -> dict[str, Any]:
    arrays, meta = load(npz, meta_json)
    layout = meta["layout"]
    with np.load(manifest_npz, allow_pickle=False) as z:
        manifest_arrays = {k: z[k] for k in z.files}
    stats = {s: describe(np.concatenate([p.reshape(-1) for p in module_arrays(arrays, layout, s)])) for s in PILOT + RUN}
    return {
        "files": {str(Path(p).relative_to(env.REPO_ROOT)) if Path(p).is_relative_to(env.REPO_ROOT) else str(p): _sha_file(p)
                  for p in (npz, meta_json, manifest_npz)},
        "hashes": hash_check(arrays, meta),
        "manifest": manifest_check(arrays, manifest_arrays, layout),
        "generator": meta["generator"],
        "seeds": {s: {"seed_key": meta["starts"][str(s)]["seed_key"], "seed": meta["starts"][str(s)]["seed"]} for s in PILOT + RUN},
        "redraw": redraw(arrays, meta),
        "stats": stats,
        "deltas": {s: {"n": int(d.size), "mean": float(d.mean()), "min": float(d.min())} for s in PILOT + RUN for d in [delta_entries(arrays, layout, s)]},
        "flags": flags(stats),
        "entries_per_start": {s: int(sum(p.size for p in module_arrays(arrays, layout, s))) for s in range(1, N_STARTS + 1)},
        "entries_per_start_json": int(meta["entries_per_start"]),
        "modules": len(layout),
        "arrays_in_npz": len(arrays),
        "arrays_in_manifest_npz": len(manifest_arrays),
    }


def report(r: dict[str, Any]) -> str:
    L: list[str] = []
    add = L.append
    add("The starts check (session 6, plan 1, Section 2.2). Description only: it reports what it finds and decides nothing.")
    add("")
    add("Files read, with their SHA-256:")
    for name, sha in r["files"].items():
        add(f"  {name}  {sha}")
    add("")
    h, m = r["hashes"], r["manifest"]
    add("1. Hashes. Each start's SHA-256 recomputed over its module arrays' bytes, concatenated in the layout's order, and compared")
    add("   with the json's `sha256`.")
    add(f"   Starts checked: {h['checked']}. Matching: {h['matched']}. Mismatched: {', '.join(map(str, h['mismatched'])) or 'none'}.")
    add(f"   Starts 1 to {m['checked']} against data/manifest/starts.npz, entry for entry (dtype, shape, and bytes of every module array):")
    add(f"   equal: {m['equal']} of {m['checked']}. Differing arrays: {', '.join(m['differing']) or 'none'}.")
    add("")
    add("2. The generator. The json's `generator` field:")
    add(f"   {r['generator']}")
    add("   Each start's `seed_key` and `seed`:")
    add(f"   {'start':>5}  {'seed_key':<26}  seed")
    for s, v in r["seeds"].items():
        add(f"   {s:>5}  {json.dumps(v['seed_key']):<26}  {v['seed']}")
    same_form = all(v["seed_key"][1:] == ["start", s] and v["seed_key"][0] == r["seeds"][1]["seed_key"][0] for s, v in r["seeds"].items())
    add(f"   Every seed key above is [{r['seeds'][1]['seed_key'][0]}, \"start\", s] with s the start's own index: {'yes' if same_form else 'no'}.")
    d = r["redraw"]
    add(f"   Every start 1 to {d['checked']} drawn again from seed_of(\"start\", s) by that scheme (torch {d['torch']}, on this machine's CPU),")
    add("   and compared with the file byte for byte, every module array's dtype, shape, and bytes:")
    add(f"   bit-identical: {d['identical']} of {d['checked']}. Differing: {', '.join(map(str, d['differing'])) or 'none'}.")
    add(f"   Recorded `seed` equal to seed_of(\"start\", s): {d['checked'] - len(d['seed_differs'])} of {d['checked']}. "
        f"Differing: {', '.join(map(str, d['seed_differs'])) or 'none'}.")
    add("")
    add("3. Each start's entries, all of them (the delta entries included), in float64. sd is the population standard deviation")
    add("   (ddof = 0). KS is the Kolmogorov-Smirnov distance from the uniform distribution on [0, 1), sup |F_n(x) - x|.")
    head = f"   {'start':>5}  {'entries':>7}  {'mean':>9}  {'sd':>9}  {'min':>11}  {'max':>11}  {'share < 0.5':>11}  {'KS':>9}"
    for title, group in (("Starts 1 to 8", PILOT), ("Starts 9 to 13", RUN)):
        add(f"   {title}")
        add(head)
        for s in group:
            x = r["stats"][s]
            add(f"   {s:>5}  {x['n']:>7}  {x['mean']:>9.6f}  {x['sd']:>9.6f}  {x['min']:>11.8f}  {x['max']:>11.8f}  {x['below_half']:>11.6f}  {x['ks']:>9.6f}")
    add("   The flag: a start among 9 to 13 whose mean or KS distance lies outside the range spanned by starts 1 to 8 by more than")
    add("   that range's width, that is below lo - width or above hi + width.")
    for metric, f in r["flags"].items():
        name = {"mean": "Mean", "ks": "KS distance"}[metric]
        add(f"   {name}: starts 1 to 8 span [{f['lo']:.6f}, {f['hi']:.6f}], width {f['width']:.6f}; flagged outside "
            f"[{f['lo'] - f['width']:.6f}, {f['hi'] + f['width']:.6f}]: {', '.join(map(str, f['flagged'])) or 'none'}.")
    add("")
    add("4. Each start's 24 delta entries (the last entry of each module's array), in float64: their mean and minimum. A delta")
    add("   entry's mask is the raw setting value, with no label under it.")
    for title, group in (("Starts 1 to 8", PILOT), ("Starts 9 to 13", RUN)):
        add(f"   {title}")
        add(f"   {'start':>5}  {'entries':>7}  {'mean':>9}  {'minimum':>11}")
        for s in group:
            x = r["deltas"][s]
            add(f"   {s:>5}  {x['n']:>7}  {x['mean']:>9.6f}  {x['min']:>11.8f}")
    add("")
    per = sorted(set(r["entries_per_start"].values()))
    add("5. For the record.")
    add(f"   Entries per start: {', '.join(map(str, per))} (every start 1 to {len(r['entries_per_start'])}); the json's `entries_per_start`: "
        f"{r['entries_per_start_json']}.")
    add(f"   Modules in the layout: {r['modules']}. Arrays in starts_1_64.npz: {r['arrays_in_npz']}; in data/manifest/starts.npz: "
        f"{r['arrays_in_manifest_npz']}.")
    return "\n".join(L) + "\n"


def main() -> None:
    print(report(check()), end="")


if __name__ == "__main__":
    main()
