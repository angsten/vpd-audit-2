"""Session 5, plan 1, Section 5.3: from intervals to verdict words, the printed rows, and the record.

The rules: `freeze/part1.md`, Sections 4 and 8 (signed); `freeze/amendment1.md` (Amendment 1); and the binding
specification `freeze/amendment1_specs/output_and_reading_spec.md` ("the output specification"), Sections 3, 4, 6, 7.
Amendment 1 governs where they differ: flags F1 and F1b print its sentences, no count of early-breakout batches is
printed, and the pooled retention keeps its interval and is always followed by "Description: resolves no cell."

  - `verdict_large`, `verdict_ratio`, `shuffled_reading`, `step_cell`: the decision logic on a given interval.
  - `nine_statistics`: the nine statistics of the output specification's Section 2.2 as means of the two kinds.
  - `row_record`: one function from a row's arrays to its record. Every verdict is read from the deciding interval.
  - `delta_on_block`, `scatter_points`: the delta-on summary and the scatter's data.
  - `render`: the printed text, built from the record alone.

Signed sentences are printed verbatim. Everything beside them is description with no line. A flag never changes a
verdict.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2.lead_intervals import Combo, Presence

LINE = 0.2  # the signed line of both ratios
MISSING_ALLOWANCE_DIVISOR = 8  # signed: a level is Undetermined if more than one eighth of a side's searches are missing

# The signed sentences, verbatim (output specification, Section 3.7).
SENTENCES = {
    "a": "The carried-over harm depends on which components the adversary chose, beyond how often they are needed",
    "b": "Mostly harm from extreme masks on components of that usage, whichever ones receive them, with a small part that depends on the choice; the exploited-components count is reported with that caveat",
    "c": "The harm comes from extreme masks on components of that usage, whichever ones receive them; the exploited-components count is dropped from the post",
    "d": "Undetermined between the first two readings; this takes precedence when a wide interval also includes zero",
    "C-LD": "The search found a choice of components whose harm carries to text in general: by the paper's own test (lines 2019 to 2022), a systematic defect",
    "C-LN": "A random permitted setting that switches off and on as many components at each level of usage also hurts unseen text; the search's particular choice is fitted to its batch",
    "C-ND": "The choice carries over, at no more harm on unseen text than the 20-step adversary does to its own batch",
    "C-NN": "The harm carries over through extreme masks on components of that usage, within the 20-step level",
    "C-X": "The search's harm is fitted to its batch: the case line 2022 describes as noise-tuned (either column)",
}
SIGNED_CAVEAT = "Negative ones are reported with the bias of taking a setting at its first crossing stated: downward, of unknown size."
STEP_FOOTER = "A straddling 40- or 80-step cell stays Undetermined, and nothing outside the step table resolves it."
LEVEL_FOOTERS = ("Only positive verdicts are confirmatory.", "The harm-level table is printed in full and never resolves a step-table cell.")
CARRIES_WORD = {"yes": "Carries over", "no": "Batch-specific", "undetermined": "Undetermined"}
ROW_NAMES = {"L": "Large", "N": "Not large, but carries over", "X": "Does not carry over"}
COLUMN_NAMES = {"yes": "Depends on the choice", "no": "Does not depend on the choice"}
VERDICT_NAMES = {"large": "large", "carries": "carries over", "depends": "depends on the choice"}
RETENTION_FOOTER = "Description: resolves no cell."
DELTA_ON_CAUTION = ("The delta-on searches follow different paths from the lead's, so a share differs from 1 by chance. "
                    "Compare it with the range on line 7 before reading it as the delta components' contribution.")
# Two fixed sentences whose wording the amendment leaves to the script (plan 1, Section 12.1, item 7).
MISSING_WORDING = "This row holds for searches that reached the level; searches that never reach it are left out, and they are the ones that stall low."
STEP_BEFORE_LABEL = "step n - 1: description; step n decides"
STEP_BEFORE_WORDING = "The setting after step n - 1 has no shuffled copies, so this sub-row carries the \"large\" difference and the carry-over ratio only."
HELDOUT_MEANS_NOTE = "Description, with no line: whether a batch sits far above the rest is a judgement."
SECOND_COPY_NOTE = ("Each held-out batch's harm is here the mean of its per-text harms over the texts not excluded; no search is rerun, "
                    "and the level-crossing steps stay as they were. Per-text harms are stored in float32, so their mean differs from "
                    "the batch value at about 1e-7 even for a batch with no excluded text.")

FLAG_TEXTS = {
    "F1": {"step": "Collision: the signed line \"'does not carry over' when the interval of tau_n lies below 0.2\" also applies to these data.",
           "level": "Collision: \"large\" is yes and \"carries over\" is no at this harm level."},
    "F1b": "The carry-over ratio is undetermined against 0.2.",
    "F2": "no reading defined: the shuffled ratio's interval lies wholly below zero",
    "F3": "the own search's margin over shuffled copies is not distinguishable from zero; the shuffled ratio is not reliable in this row; read the two margins",
    "F4": "shuffled copies do at least as much harm as the own search; the shuffled ratio's meaning is inverted in this row; read the two margins",
    "F5": "carried-over settings do less harm than their shuffled copies",
    "F6": "carried-over added harm is not distinguishable from zero; composition share not defined",
    "F7": "percentile interval gives a different verdict for: {names}; the signed interval decides",
    "F8": "step n - 1 gives a different verdict for: {names}; step n decides",
    "F9": "recomputation without the 11 overlapping texts gives a different verdict for: {names}; the main reading decides",
    "F10": "level Undetermined: {a} of {na} attack searches and {b} of {nb} held-out searches missing; allowance {allow} per side",
    "F11": "interval widened by {multiplier} under the pre-run amendment",
}
FLAG_ORDER = ("F1", "F1b", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11")


# ----------------------------------------------------------------------------- the decision logic


def verdict_large(L: float, U: float) -> str:
    """Amendment 1, entry 2.1: yes if the interval lies above zero, no if at or below zero."""
    if L > 0:
        return "yes"
    if U <= 0:
        return "no"
    return "undetermined"


def verdict_ratio(L: float, U: float) -> str:
    """Amendment 1, entry 2.1: yes if the interval lies at or above 0.2, no if below."""
    if L >= LINE:
        return "yes"
    if U < LINE:
        return "no"
    return "undetermined"


def shuffled_reading(L: float, U: float) -> str:
    """Amendment 1, entry 2.2: the four signed readings in their order of test, and "none" for an interval wholly
    below zero."""
    if L >= LINE:
        return "a"
    if U >= LINE:
        return "d"
    if U < 0:
        return "none"
    if L > 0:
        return "b"
    return "c"


def _candidates(codes: list[str]) -> str:
    quoted = [f'"{ROW_NAMES[c]}"' for c in codes]
    if len(quoted) == 2:
        return f"{quoted[0]} and {quoted[1]}"
    return f"{quoted[0]}, {quoted[1]}, and {quoted[2]}"


def step_cell(large: str, carries: str, depends: str) -> dict[str, Any]:
    """The step-table cell from the three verdicts (output specification, Section 3.4; "large" is asked first)."""
    rows = {("yes", "yes"): ["L"], ("yes", "undetermined"): ["L"], ("yes", "no"): ["L"],
            ("no", "yes"): ["N"], ("no", "no"): ["X"], ("no", "undetermined"): ["N", "X"],
            ("undetermined", "yes"): ["L", "N"], ("undetermined", "no"): ["L", "X"],
            ("undetermined", "undetermined"): ["L", "N", "X"]}[(large, carries)]
    column = COLUMN_NAMES.get(depends)
    settled = len(rows) == 1
    if settled:
        row_state = ROW_NAMES[rows[0]]
    elif len(rows) == 2:
        row_state = f"Unsettled between {_candidates(rows)}"
    else:
        row_state = "Unsettled between all three"
    code = None
    if settled and rows[0] == "X":
        code = "C-X"
    elif settled and column is not None:
        code = {("L", "yes"): "C-LD", ("L", "no"): "C-LN", ("N", "yes"): "C-ND", ("N", "no"): "C-NN"}[(rows[0], depends)]
    if code is not None:
        printed = SENTENCES[code]
    elif settled:
        printed = f"Row: {row_state}. Column undetermined at this search length."
    elif column is not None:
        printed = f"Column: {column}. Row undetermined between {_candidates(rows)}."
    else:
        printed = "Undetermined at this search length."
    return {"row_state": row_state, "row_settled": settled, "column_state": column if column is not None else "Unsettled",
            "column_settled": column is not None, "sentence_code": code, "printed": printed}


def collision_flags(table: str, large: str | None, carries: str) -> dict[str, str]:
    """Amendment 1, fault 3.1: F1 when "large" is yes and "carries over" is no, F1b when "large" is yes and "carries
    over" is undetermined, with the amendment's sentences. `table` is "step" or "level"."""
    out: dict[str, str] = {}
    if large == "yes" and carries == "no":
        out["F1"] = FLAG_TEXTS["F1"][table]
    if large == "yes" and carries == "undetermined":
        out["F1b"] = FLAG_TEXTS["F1b"]
    return out


def _verdict(kind: str, interval: list[float] | None) -> str:
    if interval is None:
        return "undetermined"
    return verdict_large(*interval) if kind == "large" else verdict_ratio(*interval)


# ----------------------------------------------------------------------------- the statistics


def shuffled_mean(shuffled: np.ndarray) -> np.ndarray:
    """The mean of a cell's 8 shuffled harms, summed pairwise so that 8 equal harms give exactly that harm."""
    assert shuffled.shape[-1] == 8
    s = shuffled
    return (((s[..., 0] + s[..., 1]) + (s[..., 2] + s[..., 3])) + ((s[..., 4] + s[..., 5]) + (s[..., 6] + s[..., 7]))) / 8.0


def nine_statistics(arrays: dict[str, Any]) -> dict[str, tuple[Combo, Combo | None]]:
    """The statistics of the output specification's Section 2.2, each as (numerator, denominator or None).

    Keys: `large` (1), `carries` (2), `depends` (3), `carried_margin` (4), `own_margin` (5), `kappa` (6),
    `shuffled_vs_yardstick` (7), `carried_added` (8), `pooled_retention` (9). The five that need shuffled copies are
    absent when the row has none."""
    start, own, own20, carried = arrays["start"], arrays["own"], arrays["own20"], arrays["carried"]
    k = start[None, :, :]
    q = own20[None, :, :]
    attack_added = (arrays["attack_own"] - arrays["attack_start"])[:, None, :]
    stats: dict[str, tuple[Combo, Combo | None]] = {
        "large": (Combo(a_cells=carried - q), None),
        "carries": (Combo(a_cells=carried - k), Combo(h_cells=own - start)),
        "carried_added": (Combo(a_cells=carried - k), None),
        "pooled_retention": (Combo(a_cells=carried - k), Combo(a_cells=attack_added)),
    }
    shuf = arrays.get("shuffled_mean")
    if shuf is None and arrays.get("shuffled") is not None:
        shuf = shuffled_mean(arrays["shuffled"])
    if shuf is not None:
        stats["depends"] = (Combo(a_cells=carried - shuf), Combo(a_cells=-shuf, h_cells=own))
        stats["carried_margin"] = (Combo(a_cells=carried - shuf), None)
        stats["own_margin"] = (Combo(a_cells=-shuf, h_cells=own), None)
        stats["kappa"] = (Combo(a_cells=carried - shuf), Combo(a_cells=carried - k))
        stats["shuffled_vs_yardstick"] = (Combo(a_cells=shuf - q), None)
    return stats


def presence_of(arrays: dict[str, Any]) -> Presence:
    return Presence(arrays["attack_present"], arrays["heldout_present"])


def _masked_mean(x: np.ndarray, mask: np.ndarray) -> float | None:
    n = int(mask.sum())
    return float(np.where(mask, x, 0.0).sum() / n) if n else None


def _block(res: dict[str, Any]) -> dict[str, Any]:
    return LI.record_of(res)


def retention(arrays: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """Per attack setting (i, s): its carried-over added harm averaged over held-out batches, and its added harm on its
    own batch (output specification, Section 4.3). NaN where the setting does not exist."""
    num = (arrays["carried"] - arrays["start"][None, :, :]).mean(axis=1)
    den = arrays["attack_own"] - arrays["attack_start"]
    a = arrays["attack_present"]
    return np.where(a, num, np.nan), np.where(a, den, np.nan)


def heldout_batch_means(arrays: dict[str, Any]) -> dict[str, Any]:
    """Amendment 2, Section 7: each held-out batch's mean carried-over added harm, over the carried settings that exist,
    each relative to the mean of the batches' means, sorted. Description with no line: it never changes an interval of
    record or a verdict word, and whether a batch sits far above the rest is a judgement."""
    a = np.asarray(arrays["attack_present"], dtype=bool)
    added = np.where(a[:, None, :], arrays["carried"] - arrays["start"][None, :, :], 0.0)  # [K_A, K_H, n_s]
    n = int(a.sum())
    names = arrays.get("heldout_names") or [f"H{j + 1}" for j in range(added.shape[1])]
    out: dict[str, Any] = {"note": HELDOUT_MEANS_NOTE, "mean_of_batch_means": None, "sorted": None}
    if n == 0:
        return out
    means = added.sum(axis=(0, 2)) / n  # [K_H]
    overall = float(means.mean())
    out["mean_of_batch_means"] = overall
    if overall == 0.0:
        return out
    relative = means / overall
    order = np.argsort(relative, kind="stable")
    out["sorted"] = [{"batch": names[j], "relative": float(relative[j]), "mean": float(means[j])} for j in order]
    return out


def _retention_group(num: np.ndarray, den: np.ndarray, mask: np.ndarray) -> dict[str, Any]:
    n = int(mask.sum())
    out: dict[str, Any] = {"settings": n, "pooled": None, "median": None, "p10": None, "p90": None, "undefined": 0}
    if n == 0:
        return out
    nu, de = num[mask], den[mask]
    total = float(de.sum())
    out["pooled"] = float(nu.sum() / total) if total != 0.0 else None
    ok = de != 0.0
    out["undefined"] = int((~ok).sum())
    if ok.any():
        r = nu[ok] / de[ok]
        out["median"] = float(np.median(r))
        out["p10"], out["p90"] = (float(x) for x in np.percentile(r, [10, 90]))
    return out


# ----------------------------------------------------------------------------- one row


def row_record(arrays: dict[str, Any], *, multiplier: float = 1.0, indices: LI.BootstrapIndices | None = None,
               batch_part: str = "bootstrap", before: dict[str, Any] | None = None,
               replicates: dict[str, np.ndarray] | None = None, label: str = "") -> dict[str, Any]:
    """One row's record from its arrays (the names of the output specification's Section 2.1).

    `before` holds the arrays of the setting after step n - 1, at 160 and 320 steps. If `replicates` is given, each
    statistic's bootstrap replicate values are stored in it under `label`."""
    table, key = arrays["table"], arrays["key"]
    pres = presence_of(arrays)
    K_A, K_H, n_s = pres.K_A, pres.K_H, pres.n_s
    a, b = pres.a, pres.b
    stats = nine_statistics(arrays)
    asked_large = not (table == "step" and key == 20)
    if not asked_large:
        del stats["large"]
        stats.pop("shuffled_vs_yardstick", None)  # at 20 steps the yardstick is the own search itself

    res: dict[str, dict[str, Any]] = {}
    for name, (num, den) in stats.items():
        res[name] = LI.interval(num, den, pres, multiplier=multiplier, indices=indices, batch_part=batch_part)
        if replicates is not None and res[name]["replicates"] is not None:
            replicates[f"{label}{table}.{key:g}.{name}"] = res[name]["replicates"]

    # the missing count decides first, at a harm level
    missing_a, missing_b = int((~a).sum()), int((~b).sum())
    total_a, total_b = K_A * n_s, K_H * n_s
    level_undetermined = table == "level" and (missing_a * MISSING_ALLOWANCE_DIVISOR > total_a or missing_b * MISSING_ALLOWANCE_DIVISOR > total_b)

    def read(name: str, which: str) -> str:
        if level_undetermined:
            return "undetermined"
        return _verdict(name, res[name][which])

    verdicts = {name: read(name, "interval") for name in ("large", "carries", "depends") if name in res}
    has_shuffles = "depends" in res

    def verdict_block(name: str) -> dict[str, Any]:
        blk = _block(res[name])
        v = verdicts[name]
        blk["verdict"] = v
        blk["forced_by_missing_count"] = bool(level_undetermined)
        if table == "level":
            blk["tag"] = "confirmatory" if v == "yes" else None
            blk["caveat"] = SIGNED_CAVEAT if v == "no" else None
        return blk

    record: dict[str, Any] = {
        "table": table, "key": key, "multiplier": multiplier,
        "counts": {"attack_batches": K_A, "heldout_batches": K_H, "starts": n_s,
                   "carried_cells": int(K_H * a.sum()), "own_cells": int(b.sum())},
    }
    shuf = arrays.get("shuffled_mean")
    if shuf is None and arrays.get("shuffled") is not None:
        shuf = shuffled_mean(arrays["shuffled"])
    a3 = np.broadcast_to(a[:, None, :], (K_A, K_H, n_s))
    record["means_raw"] = {
        "start": float(np.mean(arrays["start"])),
        "shuffled": _masked_mean(shuf, a3) if shuf is not None else None,
        "carried": _masked_mean(arrays["carried"], a3),
        "own": _masked_mean(arrays["own"], b),
        "own20": float(np.mean(arrays["own20"])) if asked_large else None,
    }
    record["attack_side"] = {"start": float(np.mean(arrays["attack_start"])), "own": _masked_mean(arrays["attack_own"], a)}

    if asked_large:
        record["large"] = verdict_block("large")
        record["large"]["asked"] = True
    else:
        record["large"] = {"asked": False, "verdict": "not asked", "printed": "not asked at 20 steps"}
    record["carries"] = verdict_block("carries")
    record["carries"]["added_harm"] = [res["carries"]["numerator"], res["carries"]["denominator"]]
    if not asked_large:
        record["carries"]["word"] = CARRIES_WORD[verdicts["carries"]]

    flags: dict[str, str] = {}
    if has_shuffles:
        dep = verdict_block("depends")
        if level_undetermined:
            dep["reading"], dep["sentence"] = "not read", "not read: level Undetermined"
        elif res["depends"]["interval"] is None:
            dep["reading"], dep["sentence"] = "none", "no reading defined"
        else:
            reading = shuffled_reading(*res["depends"]["interval"])
            dep["reading"] = reading
            dep["sentence"] = SENTENCES[reading] if reading != "none" else "no reading defined"
        record["depends"] = dep
        record["carried_margin"] = _block(res["carried_margin"])
        own_margin = _block(res["own_margin"])
        se = res["own_margin"]["standard_error"]
        own_margin["z"] = (res["own_margin"]["estimate"] / se) if se is not None and se > 0 else None  # z_D, unwidened
        record["own_margin"] = own_margin
        added = res["carried_added"]
        f6 = added["interval"] is not None and added["interval"][0] <= 0
        kappa = _block(res["kappa"])
        kappa["defined"] = bool(not f6 and res["kappa"]["defined"])
        if added["estimate"] is not None and res["carried_margin"]["estimate"] is not None:
            kappa["nats"] = {"carried_added": added["estimate"], "not_reproduced": res["carried_margin"]["estimate"],
                             "reproduced": added["estimate"] - res["carried_margin"]["estimate"]}
        else:
            kappa["nats"] = None
        record["kappa"] = kappa
        if "shuffled_vs_yardstick" in res:
            svy = _block(res["shuffled_vs_yardstick"])
            iv7 = res["shuffled_vs_yardstick"]["interval"]
            if iv7 is None:
                svy["relation"] = None
            else:
                svy["relation"] = "exceed" if iv7[0] > 0 else ("do not exceed" if iv7[1] <= 0 else "are not distinguishable from")
            record["shuffled_vs_yardstick"] = svy
        # flags triggered by the sign of an interval
        iv3, iv4, iv5 = res["depends"]["interval"], res["carried_margin"]["interval"], res["own_margin"]["interval"]
        if iv3 is not None and iv3[1] < 0:
            flags["F2"] = FLAG_TEXTS["F2"]
        if iv5 is not None and iv5[0] <= 0 < iv5[1]:
            flags["F3"] = FLAG_TEXTS["F3"]
        if iv5 is not None and iv5[1] <= 0:
            flags["F4"] = FLAG_TEXTS["F4"]
        if iv4 is not None and iv4[1] < 0:
            flags["F5"] = FLAG_TEXTS["F5"]
        if f6:
            flags["F6"] = FLAG_TEXTS["F6"]
    record["carried_added"] = _block(res["carried_added"])

    # the collision of fault 3.1
    flags.update(collision_flags(table, verdicts.get("large"), verdicts["carries"]))

    # tie-breaks: the deciding interval decides over the percentile interval and over the unwidened one
    if not level_undetermined:
        differ = [VERDICT_NAMES[n] for n in verdicts
                  if res[n]["interval_percentile"] is not None and _verdict(n, res[n]["interval_percentile"]) != verdicts[n]]
        if differ:
            flags["F7"] = FLAG_TEXTS["F7"].format(names=", ".join(differ))
        if multiplier > 1.0:
            text = FLAG_TEXTS["F11"].format(multiplier=f"{multiplier:.2f}")
            differ = [VERDICT_NAMES[n] for n in verdicts if _verdict(n, res[n]["interval_unwidened"]) != verdicts[n]]
            if differ:
                text += "; unwidened interval gives a different verdict for: " + ", ".join(differ)
            flags["F11"] = text
    if level_undetermined:
        flags["F10"] = FLAG_TEXTS["F10"].format(a=missing_a, na=total_a, b=missing_b, nb=total_b, allow=total_a // MISSING_ALLOWANCE_DIVISOR)

    # the step-table cell, from 40 steps
    if table == "step" and asked_large and has_shuffles:
        record["cell"] = step_cell(verdicts["large"], verdicts["carries"], verdicts["depends"])
    else:
        record["cell"] = None

    # each setting against itself
    num, den = retention(arrays)
    pooled = _block(res["pooled_retention"])
    ret: dict[str, Any] = {"pooled": pooled, "footer": RETENTION_FOOTER}
    if table == "step":
        past5 = arrays["attack_past"][5.0]
        ret["groups"] = {"past_5_nats": _retention_group(num, den, a & past5), "not_past_5_nats": _retention_group(num, den, a & ~past5)}
    else:
        ret["groups"] = {"all": _retention_group(num, den, a)}
    ret["settings"] = int(a.sum())
    record["retention"] = ret
    record["heldout_batch_means"] = heldout_batch_means(arrays)

    if table == "step":
        record["past_levels"] = {side: {str(int(level)): float(np.mean(arrays[f"{side}_past"][level])) for level in (2.0, 5.0, 10.0)}
                                 for side in ("attack", "heldout")}
        record["cycling"] = {side: float(np.mean(arrays[f"{side}_cycling"])) for side in ("attack", "heldout")}
    else:
        record["past_levels"] = None
        record["cycling"] = None
        names = {"attack": arrays["attack_names"], "heldout": arrays["heldout_names"]}
        masks = {"attack": a, "heldout": b}
        own = {"attack": arrays["attack_own"], "heldout": arrays["own"]}
        level: dict[str, Any] = {"undetermined": bool(level_undetermined), "allowance": total_a // MISSING_ALLOWANCE_DIVISOR,
                                 "subtable": {"attack_batches": int(pres.sub_a.size), "heldout_batches": int(pres.sub_h.size), "starts": n_s},
                                 "wording": MISSING_WORDING if (missing_a or missing_b) else None}
        for side in ("attack", "heldout"):
            m = masks[side]
            scored = own[side][m]
            level[side] = {
                "missing": int((~m).sum()), "searches": int(m.size),
                "missing_by_batch": {names[side][i]: int((~m[i]).sum()) for i in range(m.shape[0]) if (~m[i]).any()},
                "own_harm_median": float(np.median(scored)) if scored.size else None,
                "own_harm_max": float(np.max(scored)) if scored.size else None,
            }
        record["level"] = level

    if has_shuffles:
        record["shuffle_moved"] = {"moved_share": _masked_mean(arrays["moved_share"], a), "mean_abs_change": _masked_mean(arrays["mean_abs_change"], a)}
    else:
        record["shuffle_moved"] = None

    # the setting after step n - 1, at 160 and 320 steps
    record["step_before"] = None
    if before is not None:
        b_stats = nine_statistics({**before, "shuffled": None, "shuffled_mean": None})
        b_pres = presence_of(before)
        sub: dict[str, Any] = {"label": STEP_BEFORE_LABEL, "wording": STEP_BEFORE_WORDING, "key": before["key"]}
        differ = []
        for name in ("large", "carries"):
            num_c, den_c = b_stats[name]
            r = LI.interval(num_c, den_c, b_pres, multiplier=multiplier, indices=indices, batch_part=batch_part)
            if replicates is not None and r["replicates"] is not None:
                replicates[f"{label}{table}.{key:g}.before.{name}"] = r["replicates"]
            blk = _block(r)
            blk["verdict"] = _verdict(name, r["interval"])
            sub[name] = blk
            if blk["verdict"] != verdicts[name]:
                differ.append(VERDICT_NAMES[name])
        sub["carries"]["added_harm"] = [sub["carries"]["numerator"], sub["carries"]["denominator"]]
        if differ:
            flags["F8"] = FLAG_TEXTS["F8"].format(names=", ".join(differ))
        record["step_before"] = sub

    record["verdicts"] = verdicts
    record["flags"] = [f for f in FLAG_ORDER if f in flags]
    record["flag_texts"] = {f: flags[f] for f in record["flags"]}
    return record


def mark_recomputed(main: dict[str, Any], recomputed: dict[str, Any]) -> None:
    """Flag F9 on a main row: a verdict differs in the recomputation without the overlapping texts. The main reading
    decides."""
    differ = [VERDICT_NAMES[n] for n in main["verdicts"] if recomputed["verdicts"].get(n) != main["verdicts"][n]]
    if differ:
        texts = dict(main["flag_texts"])
        texts["F9"] = FLAG_TEXTS["F9"].format(names=", ".join(differ))
        main["flags"] = [f for f in FLAG_ORDER if f in texts]
        main["flag_texts"] = {f: texts[f] for f in main["flags"]}


# ----------------------------------------------------------------------------- the delta-on summary


def matched_arrays(lead: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    """The lead's row arrays on the cells it shares with the delta-on run, matched by batch name and start."""
    ia = [lead["attack_names"].index(n) for n in delta["attack_names"]]
    jh = [lead["heldout_names"].index(n) for n in delta["heldout_names"]]
    ss = [lead["starts"].index(s) for s in delta["starts"]]
    out = {k: v for k, v in lead.items() if k not in ("attack_past", "heldout_past", "attack_cycling", "heldout_cycling")}
    out["attack_names"], out["heldout_names"], out["starts"] = list(delta["attack_names"]), list(delta["heldout_names"]), list(delta["starts"])
    for name in ("start", "own", "own20", "heldout_present", "heldout_missing"):
        out[name] = lead[name][np.ix_(jh, ss)]
    for name in ("attack_start", "attack_own", "attack_present", "attack_missing", "moved_share", "mean_abs_change"):
        if lead.get(name) is not None:
            out[name] = lead[name][np.ix_(ia, ss)]
    out["carried"] = lead["carried"][np.ix_(ia, jh, ss)]
    if lead.get("shuffled") is not None:
        out["shuffled"] = lead["shuffled"][np.ix_(ia, jh, ss)]
    return out


def delta_on_block(lead: dict[str, Any], delta: dict[str, Any], *, multiplier: float = 1.0, indices: LI.BootstrapIndices | None = None,
                   batch_part: str = "bootstrap", null_range: dict[str, Any] | None = None,
                   replicates: dict[str, np.ndarray] | None = None, label: str = "") -> dict[str, Any]:
    """One search length of the delta-on summary (output specification, Section 6): description only, no verdict word.
    `lead` and `delta` are row arrays on the same cells."""
    key = delta["key"]
    block: dict[str, Any] = {"key": key, "multiplier": multiplier, "null_range": null_range, "caution": DELTA_ON_CAUTION}
    pres = presence_of(delta)
    for arm, arrays in (("lead", lead), ("delta_on", delta)):
        stats = nine_statistics(arrays)
        a3 = np.broadcast_to(pres.a[:, None, :], arrays["carried"].shape)
        arm_block: dict[str, Any] = {"means_raw": {"start": float(np.mean(arrays["start"])),
                                                    "shuffled": _masked_mean(shuffled_mean(arrays["shuffled"]), a3),
                                                    "carried": _masked_mean(arrays["carried"], a3),
                                                    "own": _masked_mean(arrays["own"], pres.b)}}
        for name in ("carries", "depends"):
            r = LI.interval(*stats[name], pres, multiplier=multiplier, indices=indices, batch_part=batch_part)
            if replicates is not None and r["replicates"] is not None:
                replicates[f"{label}delta_on.{key:g}.{arm}.{name}"] = r["replicates"]
            arm_block[name] = _block(r)
        block[arm] = arm_block
    shares = {
        "carried_share": (Combo(a_cells=delta["carried"] - delta["start"][None]), Combo(a_cells=lead["carried"] - lead["start"][None])),
        "own_share": (Combo(h_cells=delta["own"] - delta["start"]), Combo(h_cells=lead["own"] - lead["start"])),
    }
    for name, (num, den) in shares.items():
        r = LI.interval(num, den, pres, multiplier=multiplier, indices=indices, batch_part=batch_part)
        if replicates is not None and r["replicates"] is not None:
            replicates[f"{label}delta_on.{key:g}.{name}"] = r["replicates"]
        block[name] = _block(r)
    return block


def scatter_points(arrays: dict[str, Any]) -> list[dict[str, Any]]:
    """The scatter's data for one row (signed Section 8): for every scored attack setting, its carried-over added harm
    averaged over held-out batches and its added harm on its own batch."""
    num, den = retention(arrays)
    out = []
    for i, name in enumerate(arrays["attack_names"]):
        for s, start in enumerate(arrays["starts"]):
            if arrays["attack_present"][i, s]:
                out.append({"table": arrays["table"], "key": arrays["key"], "attack_batch": name, "start": start,
                            "carried_added": float(num[i, s]), "own_added": float(den[i, s])})
    return out


# ----------------------------------------------------------------------------- the printed text


def _f(x: float | None, digits: int = 2, signed: bool = False) -> str:
    if x is None:
        return "undefined"
    x = x + 0.0
    return f"{x:+.{digits}f}" if signed else f"{x:.{digits}f}"


def _iv(interval: list[float] | None, digits: int = 2) -> str:
    if interval is None:
        return "[undefined]"
    return f"[{_f(interval[0], digits)}, {_f(interval[1], digits)}]"


def _verdict_text(blk: dict[str, Any]) -> str:
    out = blk["verdict"]
    if blk.get("tag"):
        out += f" ({blk['tag']})"
    return out


def _quote(text: str) -> str:
    return f'      "{text}"'


def _row_lines(rec: dict[str, Any]) -> list[str]:
    table, key = rec["table"], rec["key"]
    c, m = rec["counts"], rec["means_raw"]
    out: list[str] = []
    if table == "step":
        out.append(f"STEP TABLE: {key} steps")
    else:
        out.append(f"HARM-LEVEL TABLE: settings taken where each search's own harm first reaches {key:g} nats")
    line = (f" 1  Cells: {c['attack_batches']} attack x {c['heldout_batches']} held-out batches x {c['starts']} starts; "
            f"{c['carried_cells']} carried-over cells, {c['own_cells']} own-search cells")
    out.append(line)
    if table == "level":
        lv = rec["level"]
        for side, word in (("attack", "attack"), ("heldout", "held-out")):
            by = ", ".join(f"{n} ({k})" for n, k in lv[side]["missing_by_batch"].items()) or "none"
            out.append(f"    Missing {word} searches: {lv[side]['missing']} of {lv[side]['searches']} (allowance {lv['allowance']}); batches: {by}")
        st = lv["subtable"]
        out.append(f"    Start part computed on the complete sub-table: {st['attack_batches']} attack x {st['heldout_batches']} held-out batches x {st['starts']} starts")
        if lv["wording"]:
            out.append(f"    {lv['wording']}")
    out.append(" 2  Mean harm on held-out batches (raw nats):")
    parts = [f"start {_f(m['start'])}", f"shuffled copies {_f(m['shuffled'])}" if m["shuffled"] is not None else "shuffled copies none",
             f"carried over {_f(m['carried'])}", f"own search {_f(m['own'])}"]
    if m["own20"] is not None:
        parts.append(f"own 20-step search (yardstick) {_f(m['own20'])}")
    out.append("      " + " | ".join(parts))
    if table == "level":
        lv = rec["level"]
        out.append(f"      Own harm of the scored settings: attack median {_f(lv['attack']['own_harm_median'])}, maximum {_f(lv['attack']['own_harm_max'])}; "
                   f"held-out median {_f(lv['heldout']['own_harm_median'])}, maximum {_f(lv['heldout']['own_harm_max'])}")
    out.append(f" 2b Attack side on its own batches: start {_f(rec['attack_side']['start'])} | own search {_f(rec['attack_side']['own'])}")
    lg = rec["large"]
    if lg["asked"]:
        out.append(f" 3  Large: carried over - yardstick = {_f(lg['estimate'], signed=True)} {_iv(lg['interval'])}    {_verdict_text(lg)}")
        if lg.get("caveat"):
            out.append(f"      {lg['caveat']}")
    else:
        out.append(f" 3  Large: {lg['printed']}")
    ca = rec["carries"]
    word = f"{ca['verdict']} ({ca['word']})" if "word" in ca else _verdict_text(ca)
    out.append(f" 4  Carries over: ratio {_f(ca['estimate'])} {_iv(ca['interval'])}  (added harm {_f(ca['added_harm'][0])} over {_f(ca['added_harm'][1])})    {word}")
    if ca.get("caveat"):
        out.append(f"      {ca['caveat']}")
    if "depends" in rec:
        de = rec["depends"]
        out.append(f" 5  Depends on the choice: shuffled ratio {_f(de['estimate'])} {_iv(de['interval'])}    {_verdict_text(de)}")
        if de.get("caveat"):
            out.append(f"      {de['caveat']}")
        out.append(_quote(de["sentence"]) if de["reading"] in SENTENCES else f"      {de['sentence']}")
        cm, om, ka = rec["carried_margin"], rec["own_margin"], rec["kappa"]
        out.append(f" 6a Carried over - shuffled copies = {_f(cm['estimate'], signed=True)} {_iv(cm['interval'])} nats")
        z = _f(om["z"], 1) if om["z"] is not None else "undefined"
        out.append(f" 6b The own search beats its shuffled copies by {_f(om['estimate'])} nats {_iv(om['interval'])}, {z} standard errors from zero.")
        if ka["defined"]:
            k = ka["estimate"]
            n = ka["nats"]
            out.append(f" 6c Of the carried-over added harm of {_f(n['carried_added'])} nats, shuffled copies reproduce {_f(n['reproduced'])} nats "
                       f"({100 * (1 - k):.0f} percent) and do not reproduce {_f(n['not_reproduced'])} nats ({100 * k:.0f} percent).  "
                       f"Composition share {_f(k)} {_iv(ka['interval'])}")
        elif "F6" in rec["flags"]:
            out.append(f" 6c {FLAG_TEXTS['F6']}")
        else:
            out.append(" 6c Composition share undefined")
        if "shuffled_vs_yardstick" in rec:
            sv = rec["shuffled_vs_yardstick"]
            relation = f"they {sv['relation']} the yardstick" if sv["relation"] is not None else "the comparison is undefined"
            out.append(f" 6d Shuffled copies do {_f(m['shuffled'])} nats against a 20-step yardstick of {_f(m['own20'])} nats: {relation}.")
    else:
        out.append(" 5  Depends on the choice: not read; this setting has no shuffled copies")
    if rec["cell"] is not None:
        cell = rec["cell"]
        if cell["sentence_code"] is not None:
            head = f"{cell['row_state']} x {cell['column_state']}" if cell["sentence_code"] != "C-X" else cell["row_state"]
            out.append(f" 7  Step-table cell: {head}")
            out.append(_quote(cell["printed"]))
        else:
            out.append(f" 7  Step-table cell: {cell['printed']}")
    if rec["flags"]:
        out.append(" 8  Flags: " + rec["flag_texts"][rec["flags"][0]])
        out += [f"           {rec['flag_texts'][f]}" for f in rec["flags"][1:]]
    else:
        out.append(" 8  Flags: none")
    ret = rec["retention"]
    out.append(" 9  Each setting against itself (carried-over added harm / added harm on its own batch):")
    labels = {"past_5_nats": "own harm past 5 nats", "not_past_5_nats": "own harm not past 5 nats", "all": "settings that reached the level"}
    for name in ("past_5_nats", "not_past_5_nats", "all"):
        if name not in ret["groups"]:
            continue
        g = ret["groups"][name]
        if g["settings"]:
            out.append(f"      {labels[name]:<33}{g['settings']} settings | pooled {_f(g['pooled'])} | median {_f(g['median'])} | "
                       f"10th to 90th percentile {_f(g['p10'])} to {_f(g['p90'])}")
        else:
            out.append(f"      {labels[name]:<33}0 settings")
    out.append(f"      all {ret['settings']} settings           pooled {_f(ret['pooled']['estimate'])} {_iv(ret['pooled']['interval'])}")
    out.append(f"      {ret['footer']}")
    hb = rec["heldout_batch_means"]
    out.append(" 9b Held-out batches, each batch's mean carried-over added harm over the mean of all the batches' means, sorted:")
    if hb["sorted"] is None:
        out.append("      undefined")
    else:
        out.append("      " + ", ".join(f"{b['batch']} {_f(b['relative'])}" for b in hb["sorted"]))
    out.append(f"      {hb['note']}")
    if table == "step":
        pl, cy = rec["past_levels"], rec["cycling"]
        out.append("10  Searches past 2 / 5 / 10 nats by this step: "
                   + "; ".join(f"{word} {_f(pl[side]['2'])} / {_f(pl[side]['5'])} / {_f(pl[side]['10'])}" for side, word in (("attack", "attack"), ("heldout", "held-out"))))
        out.append(f"    Cycling settings: attack {_f(cy['attack'])}; held-out {_f(cy['heldout'])}")
    if rec["shuffle_moved"] is not None and rec["shuffle_moved"]["moved_share"] is not None:
        sm = rec["shuffle_moved"]
        out.append(f"11  Shuffle: a shuffled copy moves {100 * sm['moved_share']:.0f} percent of alive entries by more than 0.5; "
                   f"mean absolute change {_f(sm['mean_abs_change'])}")
    three = [(n, rec[n]) for n in ("large", "carries", "depends") if n in rec and rec[n].get("asked", True)]
    out.append("12  Percentile intervals (batches only): " + "; ".join(
        f"{VERDICT_NAMES[n]} {_iv(blk['interval_percentile'])}" + (" (unreliable)" if blk["percentile"] and blk["percentile"]["unreliable"] else "")
        for n, blk in three))
    if rec["multiplier"] > 1.0:
        unw = f"Unwidened (multiplier {rec['multiplier']:.2f}): " + "; ".join(f"{VERDICT_NAMES[n]} {_iv(blk['interval_unwidened'])}" for n, blk in three) + "."
    else:
        unw = "Unwidened: identical (no widening recorded)."
    out.append(f"    {unw} Start term's share of variance: " + ", ".join(_f(blk["start_share"]) for _, blk in three)
               + ". Degrees of freedom: " + ", ".join(_f(blk["nu"], 1) for _, blk in three))
    sb = rec["step_before"]
    if sb is not None:
        out.append(f"13  {sb['label']} (the setting after step {sb['key']})")
        out.append(f"      {sb['wording']}")
        out.append(f"      Large: carried over - yardstick = {_f(sb['large']['estimate'], signed=True)} {_iv(sb['large']['interval'])}    {sb['large']['verdict']}")
        out.append(f"      Carries over: ratio {_f(sb['carries']['estimate'])} {_iv(sb['carries']['interval'])}  "
                   f"(added harm {_f(sb['carries']['added_harm'][0])} over {_f(sb['carries']['added_harm'][1])})    {sb['carries']['verdict']}")
    return out


def _delta_lines(block: dict[str, Any]) -> list[str]:
    out = [f"DELTA-ON SUMMARY: {block['key']} steps (description only; no verdict word)"]
    for n, (arm, word) in enumerate((("lead", "Lead, on the matched cells"), ("delta_on", "Delta-on")), start=1):
        m = block[arm]["means_raw"]
        tail = " (its start harm is that of the starting point with the delta entries at 1)" if arm == "delta_on" else ""
        out.append(f" {n}  {word}, mean raw harm: start {_f(m['start'])} | shuffled copies {_f(m['shuffled'])} | carried over {_f(m['carried'])} | own search {_f(m['own'])}{tail}")
    for n, (name, word) in enumerate((("carries", "Carry-over ratio"), ("depends", "Shuffled ratio")), start=3):
        le, de = block["lead"][name], block["delta_on"][name]
        out.append(f" {n}  {word}: lead on the matched cells {_f(le['estimate'])} {_iv(le['interval'])}; delta-on {_f(de['estimate'])} {_iv(de['interval'])}")
    cs, os_ = block["carried_share"], block["own_share"]
    out.append(f" 5  Share of carried-over harm remaining (delta-on over lead, added harm): {_f(cs['estimate'])} {_iv(cs['interval'])}")
    out.append(f" 6  Share of own-search harm remaining (delta-on over lead, added harm): {_f(os_['estimate'])} {_iv(os_['interval'])}")
    nr = block["null_range"]
    out.append(" 7  Range of each share when the delta components do nothing (made-up-data test, scenario T8; 2.5th to 97.5th percentile):")
    for name, word in (("carried_share", "carried-over share"), ("own_share", "own-search share")):
        if nr is None:
            out.append(f"      {word}: not available")
            continue
        out.append(f"      {word}: " + "; ".join(
            f"{label} {_f(nr[name][v][0])} to {_f(nr[name][v][2])}" for v, label in (("a", "same searches, fresh cell noise"), ("b", "every search redrawn"))))
    out.append(f" 8  {block['caution']}")
    return out


def _detail_lines(title: str, name: str, blk: dict[str, Any]) -> list[str]:
    if not blk.get("defined", False):
        return [f"  {title} | {name}: undefined"]
    ms = blk["mean_squares"]
    cf = blk["closed_form"]
    pct = blk["percentile"]
    out = [f"  {title} | {name}: estimate {_f(blk['estimate'], 4)}; deciding {_iv(blk['interval'], 4)}; unwidened {_iv(blk['interval_unwidened'], 4)}; "
           f"percentile, batches only {_iv(blk['interval_percentile'], 4)}"
           + (f" (left out {pct['replicates_left_out']}; denominator at or below zero in {_f(pct['denominator_nonpositive_share'], 4)} of replicates"
              + ("; unreliable" if pct["unreliable"] else "") + ")" if pct and pct["denominator_nonpositive_share"] is not None else "")]
    out.append("      each start alone: " + ", ".join(_f(v, 4) for v in blk["per_start"])
               + (f"; denominator's distance from zero {_f(blk['denom_z'], 1)} standard errors" if blk["kind"] == "ratio" else ""))
    msq = ("mean squares S, AS, BS, ABS: " + ", ".join(f"{ms[k]:.6g}" for k in ("S", "AS", "BS", "ABS"))) if ms is not None else "start part not estimable"
    out.append(f"      {msq}; start variance before truncation {_g(blk['sigma_c_sq_untruncated'])}; V_PB {_g(blk['v_pb'])}; V_c {_g(blk['v_c'])}; "
               f"share {_f(blk['start_share'])}; nu_c {_f(blk['nu_c'], 2)}; nu {_f(blk['nu'], 2)}; "
               f"bootstrap variance over closed form {_f(cf['ratio'], 4) if cf and cf['ratio'] is not None else 'exact zero'}"
               + ("; zero_variance" if blk["zero_variance"] else ""))
    return out


def _g(x: float | None) -> str:
    return "undefined" if x is None else f"{x:.6g}"


ROW_STATISTICS = ("large", "carries", "depends", "carried_margin", "own_margin", "kappa", "shuffled_vs_yardstick", "carried_added")


def _row_details(rec: dict[str, Any]) -> list[str]:
    title = f"{rec['table']} {rec['key']:g}"
    out: list[str] = []
    for name in ROW_STATISTICS:
        if name in rec and rec[name].get("asked", True):
            out += _detail_lines(title, name, rec[name])
    out += _detail_lines(title, "pooled_retention", rec["retention"]["pooled"])
    if rec["step_before"] is not None:
        for name in ("large", "carries"):
            out += _detail_lines(f"{title}, step before", name, rec["step_before"][name])
    return out


def _tables_lines(tables: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for rec in tables["step"]:
        out += _row_lines(rec) + [""]
    if tables["step"]:
        out += [STEP_FOOTER, ""]
    for rec in tables["level"]:
        out += _row_lines(rec) + [""]
    if tables["level"]:
        out += list(LEVEL_FOOTERS) + [""]
    return out


def render(doc: dict[str, Any]) -> str:
    """The printed tables, from the record alone."""
    out: list[str] = ["LEAD EXPERIMENT (QUESTION 2): THE STEP TABLE AND THE HARM-LEVEL TABLE", ""]
    out.append("Provenance")
    for k, v in doc["provenance"].items():
        out.append(f"  {k}: {v}")
    out.append("")
    hd = doc["header"]["batch_means_added_harm"]
    out.append("Own-search added harm, each batch's mean over its starts, sorted (raw nats minus the start's harm)")
    for side, word in (("attack", "attack"), ("heldout", "held-out")):
        for row, steps in (("n20", 20), ("n40", 40)):
            out.append(f"  {word}, {steps} steps: " + " ".join(_f(x) for x in hd[side][row]))
    out.append("")
    out += _tables_lines(doc["main"])
    second = doc["without_overlapping_texts"]
    out.append("SECOND COPY: BOTH TABLES RECOMPUTED WITHOUT THE OVERLAPPING HELD-OUT TEXTS (description; the main copy decides)")
    if second.get("tables") is None:
        out += [f"  {second['note']}", ""]
    else:
        out += [f"  Excluded texts: {second['excluded_texts']}. {second['note']}", ""]
        out += _tables_lines(second["tables"])
    dl = doc["delta_on"]
    if dl.get("blocks") is None:
        out += ["DELTA-ON SUMMARY", f"  {dl['note']}", ""]
    else:
        out.append("Delta-on run: the same labels, targets, and weight deltas as the lead on each shared batch (fingerprint equal)")
        for side, word in (("attack", "attack"), ("heldout", "held-out")):
            out.append(f"  {word}: " + ", ".join(f"{n} {'true' if ok else 'false'}" for n, ok in dl["prep_fp_equal"][side].items()))
        out.append("")
        for block in dl["blocks"]:
            out += _delta_lines(block) + [""]
        if dl.get("blocks_without_overlapping_texts"):
            out += ["DELTA-ON SUMMARY, RECOMPUTED WITHOUT THE OVERLAPPING HELD-OUT TEXTS (description)", ""]
            for block in dl["blocks_without_overlapping_texts"]:
                out += _delta_lines(block) + [""]
    ls = doc["long_search"]
    out.append("Long-search levels as a distribution (description)")
    out.append(f"  Over {ls['searches']} searches, {ls['plateau_definition']}: minimum {_f(ls['min'])}, lower quartile {_f(ls['lower_quartile'])}, "
               f"median {_f(ls['median'])}, upper quartile {_f(ls['upper_quartile'])}, maximum {_f(ls['max'])}")
    out.append(f"  Share of searches at or above the paper's {ls['paper_level']} after step 320: {_f(ls['share_at_or_above_paper_level_after_step_320'])}")
    out.append(f"  The scatter's data ({len(doc['scatter'])} scored settings) are in the record file.")
    out.append("")
    out.append("INTERVAL DETAILS (every interval above; description)")
    for rec in doc["main"]["step"] + doc["main"]["level"]:
        out += _row_details(rec)
    if second.get("tables") is not None:
        out.append("  -- second copy --")
        for rec in second["tables"]["step"] + second["tables"]["level"]:
            out += _row_details(rec)
    if dl.get("blocks") is not None:
        out.append("  -- delta-on --")
        for block in dl["blocks"] + (dl.get("blocks_without_overlapping_texts") or []):
            for arm in ("lead", "delta_on"):
                for name in ("carries", "depends"):
                    out += _detail_lines(f"delta-on {block['key']}, {arm}", name, block[arm][name])
            for name in ("carried_share", "own_share"):
                out += _detail_lines(f"delta-on {block['key']}", name, block[name])
    return "\n".join(out) + "\n"
