"""Session 6, plan 2: the reading scripts on made-up units, before any GPU result exists.

A small design (attack batches A1 to A4, held-out H1 to H4, starts 9 and 10; H1 is S4's) with harms built from formulas,
so that each pooled share, count, and outcome is known by hand: the split's Part Z keeps about 0.6 of the carried added
harm and Part P about 0.3; the kept share of the top k is min(1, k / 1,000); and so on. The readers refuse an
incomplete set of units and name what is missing.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_controls as C
from vpd_audit_2 import s6_exploited as E
from vpd_audit_2 import s6_read as R
from vpd_audit_2 import s6_run as SR
from vpd_audit_2 import s6_split as S
from vpd_audit_2.manifest import deterministic_npz

ATT, HELD, STARTS, T = ("A1", "A2", "A3", "A4"), ("H1", "H2", "H3", "H4"), (9, 10), 4
KS = B.GRID


def write_unit(folder: Path, name: str, passes: list[tuple[str, float, dict]], meta: dict | None = None) -> None:
    arrays = {"pass_ids": np.array([p for p, _, _ in passes]), "harm": np.array([h for _, h, _ in passes], dtype=np.float64),
              "per_text": np.tile(np.array([[h] for _, h, _ in passes], dtype=np.float32), (1, T)),
              "recorded": np.array(json.dumps([r for _, _, r in passes])), "meta": np.array(json.dumps({"unit": name, **(meta or {})}))}
    LR.write_unit(folder / f"{name}.npz", arrays)


def kept(k: int) -> float:
    return min(1.0, k / 1000)


@pytest.fixture(scope="module")
def made_up(tmp_path_factory):
    rng = np.random.default_rng(1)
    folder = tmp_path_factory.mktemp("units")
    Q = len(LT.SETTINGS_LEAD)
    q = {n: k for k, n in enumerate(LT.SETTINGS_LEAD)}
    lead = {"attack_names": np.array(ATT), "heldout_names": np.array(HELD), "starts": np.array(STARTS), "setting_names": np.array(LT.SETTINGS_LEAD),
            "init_H": 0.2 + 0.01 * rng.random((4, 2)), "init_A": 0.2 + 0.01 * rng.random((4, 2)),
            "carried": 10 + 20 * rng.random((4, 4, 2, Q)), "own_A": 10 + 20 * rng.random((4, 2, Q)), "step_A": np.full((4, 2, Q), -1)}
    lead["step_A"][:, :, q["h5"]] = np.array([[50, 100], [70, 300], [-1, 60], [90, 85]])  # past 5 nats by 80 steps: 50, 70, 60
    for j, h in enumerate(HELD):
        write_unit(folder, f"check_{h}", [("check|s_everywhere", 1.0, {"bits_equal": True}), ("check|s0_everywhere", 0.2, {"bits_equal": True})],
                   {"label_stats": {"positive_below_1e-3_per_position": 3.0 + j, "zero_per_position": 30000.0}})
        for i, a in enumerate(ATT):
            for k, s in enumerate(STARTS):
                base = lead["init_H"][j, k]
                passes = []
                for row in B.SPLIT_ROWS:
                    full = lead["carried"][i, j, k, q[row]] - base
                    passes += [(f"Z|{row}", base + (0.6 + 0.005 * rng.standard_normal()) * full, {}),
                               (f"P|{row}", base + (0.3 + 0.005 * rng.standard_normal()) * full, {})]
                write_unit(folder, f"split_{h}_{a}_s{s}", passes)
        for k, s in enumerate(STARTS):
            base = lead["init_H"][j, k]
            for row in B.EXPLOIT_ROWS:
                full = lead["carried"][j, j, k, q[row]] - base
                p = [("top|0", base, {})]
                for kk in KS:
                    p += [(f"top|{kk}", base + kept(kk) * full, {}), (f"matched|{kk}|1", base + 0.5 * kept(kk) * full, {})]
                if row == "n320":
                    p += [(f"matched|3000|{d}", base + m * full, {}) for d, m in ((2, 0.3), (3, 0.4))]
                    p = [(pid, base + 0.5 * full, r) if pid == "matched|3000|1" else (pid, h_, r) for pid, h_, r in p]  # draws 0.5, 0.3, 0.4
                    p += [("uniform|3000", base + 0.1 * full, {})] + [(f"absg|{kk}", base + 0.8 * kept(kk) * full, {}) for kk in KS]
                    p += [(f"near_off|{kk}", base + 0.7 * kept(kk) * full, {}) for kk in KS] + [(f"near_on|{kk}", base + 0.2 * kept(kk) * full, {}) for kk in KS]
                if row in B.OFFON_ROWS:
                    p += [(f"off|{kk}", base + 0.6 * kept(kk) * full, {}) for kk in KS] + [(f"on|{kk}", base + 0.1 * kept(kk) * full, {}) for kk in KS]
                    p += [(f"bg1|{kk}", 7.0, {}) for kk in KS]
                write_unit(folder, f"exploit_{h}_s{s}_{row}", p)
        write_unit(folder, f"ones_{h}", [("ones", 5.0 + j, {})])
        write_unit(folder, f"b_{h}", [("b1", 0.3 + 0.01 * j, {})] + [(f"b2|r{r}_d{d}", (0.9 if r == 64 else 0.5) + 0.01 * d, {})
                                                                    for r, n in B.B2_RUNGS for d in range(1, n + 1)])
        if h in B.S4:
            for i, a in enumerate(ATT):
                for k, s in enumerate(STARTS):
                    base = lead["init_H"][j, k]
                    passes = []
                    for row in B.SPLIT_ROWS:
                        full = lead["carried"][i, j, k, q[row]] - base
                        passes += [(f"a|{row}", 1.0 + 0.9 * full, {}),
                                   (f"c|alive_and_never_needed|{row}", 0.31, {"moved_alive_over_half": 0.4, "zeros_on_never_needed": 0.7}),
                                   (f"c|whole_matrix|{row}", 0.5, {"moved_alive_over_half": 0.5, "zeros_on_never_needed": 0.75}),
                                   (f"d|rounded|{row}", base + 0.8 * full, {}), (f"d|snapped|{row}", base + 0.9 * full, {})]
                    write_unit(folder, f"controls_{h}_{a}_s{s}", passes)
            write_unit(folder, f"control_starts_{h}", [p for s in STARTS for p in ((f"a_start|{s}", 1.0, {}), (f"d_start|{s}", 0.25, {}))])
    for i, a in enumerate(ATT):
        base = lead["init_A"][i]
        write_unit(folder, f"check_{a}", [("check|s_everywhere", 1.0, {"bits_equal": True}), ("check|s0_everywhere", 0.2, {"bits_equal": False})],
                   {"label_stats": {"positive_below_1e-3_per_position": 1.0, "zero_per_position": 2.0}})
        for k, s in enumerate(STARTS):
            write_unit(folder, f"split_{a}_{a}_s{s}", [(f"{part}|{row}", base[k] + f * (lead["own_A"][i, k, q[row]] - base[k]), {})
                                                     for row in B.SPLIT_ROWS for part, f in (("Z", 0.7), ("P", 0.2))])
        write_unit(folder, f"b1_{a}", [("b1", 0.4, {})])
    b2 = {"settings": {f"r{r}_d{d}": {"union_size": 4000 + d if r == 64 else 1000 + d} for r, n in B.B2_RUNGS for d in range(1, n + 1)}}
    return {"folder": folder, "lead": lead, "b2": b2}


@pytest.fixture()
def design(monkeypatch):
    monkeypatch.setattr(SR, "HELDOUT", HELD)
    monkeypatch.setattr(SR, "ATTACK", ATT)
    monkeypatch.setattr(SR, "STARTS", STARTS)


def test_every_unit_is_there_and_a_missing_one_is_named(made_up, design, tmp_path):
    names = R.all_unit_names()
    R.Units(made_up["folder"]).require(names)
    sub = tmp_path / "sub"
    sub.mkdir()
    for n in names:
        if n != "split_H3_A2_s10":
            (sub / f"{n}.npz").write_bytes((made_up["folder"] / f"{n}.npz").read_bytes())
    with pytest.raises(R.Refusal, match="1 units missing: split_H3_A2_s10$"):
        R.Units(sub).require(names)


def test_the_split(made_up, design):
    units = R.Units(made_up["folder"])
    res = S.split(units, made_up["lead"], B_reps=400)
    for row in B.SPLIT_ROWS:
        z, p = res[row]["Z"], res[row]["P"]
        assert abs(z["share"] - 0.6) < 0.05 and abs(p["share"] - 0.3) < 0.05
        assert z["interval"][0] < z["share"] < z["interval"][1] and z["word"] == "above" and p["word"] == "below"
        assert res[row]["case"].startswith("Part Z above half and Part P below half")
    own = S.own_batch(units, made_up["lead"])
    assert own["n80"]["Z"]["share"] == pytest.approx(0.7) and own["n80"]["P"]["by_start"]["10"] == pytest.approx(0.2)
    labels = S.labels_and_checks(units)
    assert labels["H3"]["positive_below_1e-3_per_position"] == 5.0 and labels["A1"]["checks_bit_equal"] == [True, False]
    text = S.report(res, own, labels)
    assert "above half" in text and "below half" in text and "Reading: Part Z above half and Part P below half" in text
    assert S.word(0.51, 0.7) == "above" and S.word(0.2, 0.49) == "below" and S.word(0.4, 0.6) == "undetermined"
    assert S.case("undetermined", "above") == "A part is undetermined: the split is undetermined."


def test_exploited_components_and_off_or_on(made_up, design):
    units = R.Units(made_up["folder"])
    res = E.exploited(units, made_up["lead"], layout=None)
    r80, r320 = res["n80"], res["n320"]
    assert r80["curves"]["top"][500] == pytest.approx(0.5) and r80["curves"]["matched"][1000] == pytest.approx(0.5)
    assert r80["pooled_count"] == 1000 and r80["half_count"] == 500 and r80["by_start"] == {"9": 1000, "10": 1000}
    assert r80["per_setting"]["median"] == 1000 and r80["per_setting"]["settings"] == 8
    assert r80["past_5_nats"]["settings"] == 3  # crossings at 50, 70, and 60 steps; 85 and 90 come after 80
    assert res["n320"]["past_5_nats"]["settings"] == 7  # every crossing but the missing one
    assert r80["trigger_numbers"] == {"top_3000": pytest.approx(1.0), "matched_3000": pytest.approx(0.5)}
    t = r320["trigger"]
    assert t["top_3000"] == pytest.approx(1.0) and t["matched_3000_mean_of_three"] == pytest.approx(0.4) and t["fires"] is True
    assert r320["curves"]["uniform_3000"] == pytest.approx(0.1) and t["absg_3000"] == pytest.approx(0.8)
    oo = r320["off_on"]["pooled_count"]
    assert oo["k"] == 1000 and oo["off_share"] == pytest.approx(0.6) and oo["on_share"] == pytest.approx(0.1)
    assert oo["near_off_share"] == pytest.approx(0.7) and oo["near_on_share"] == pytest.approx(0.2)
    assert oo["background_of_one_harm"] == 7.0 and oo["all_ones_harm"] == pytest.approx(np.mean([5.0, 6.0, 7.0, 8.0]))
    assert "near_off_share" not in r80["off_on"]["3000"] and "off_on" not in res["n40"]
    text = E.report(res, B.GRID)
    assert "it fires" in text and "9,972" in text and "9,948" in text and "The pooled count: at most 1000" in text


def test_the_full_off_or_on_curves_at_every_k(made_up, design):
    """Plan 3, Section 7: the off and on parts, the background of 1, and at 320 steps the near parts, at every grid k."""
    units = R.Units(made_up["folder"])
    res = E.exploited(units, made_up["lead"], layout=None)
    for row in B.OFFON_ROWS:
        c = res[row]["off_on_curves"]
        assert sorted(c, key=int) == [str(k) for k in B.GRID]
        for k in B.GRID:
            assert c[str(k)]["off_share"] == pytest.approx(0.6) and c[str(k)]["on_share"] == pytest.approx(0.1)
            assert c[str(k)]["background_of_one_harm"] == 7.0
            assert (c[str(k)].get("near_off_share") == pytest.approx(0.7)) if row == "n320" else ("near_off_share" not in c[str(k)])
        for label, x in res[row]["off_on"].items():  # the committed reading's two points are two of the curve's
            assert {k: v for k, v in x.items() if k != "k"} == c[str(x["k"])]
    assert "off_on_curves" not in res["n40"]
    lines = E.report(res, B.GRID).splitlines()
    i = lines.index("n320: the kept share against k (k = 0 keeps 0.00).")
    # the curve's four rows at 320 steps (k, top, matched, |G|), then the note and the added rows
    assert lines[i + 4].startswith("    |G|:") and lines[i + 5] == E.OFF_ON_CURVES_NOTE
    assert "added after the readings, as description" in E.OFF_ON_CURVES_NOTE.lower()
    assert lines[i + 6].startswith("    off:     ") and lines[i + 8].startswith("    near-off:") and lines[i + 10].startswith("    bg of 1: ")
    assert len(lines[i + 6]) == len(lines[i + 1])  # aligned with the curve's k row


def test_the_controls(made_up, design):
    units = R.Units(made_up["folder"])
    lead = made_up["lead"]
    a = C.delta_share(units, lead)
    # (1 + 0.9 full) - 1 over full, summed: exactly 0.9
    assert a["n320"]["share"] == pytest.approx(0.9) and a["n20"]["by_start"]["9"] == pytest.approx(0.9)
    b = C.b_controls(units, made_up["b2"])
    assert b["b1"]["mean_heldout"] == pytest.approx(0.315) and b["b1"]["mean_attack"] == pytest.approx(0.4)
    assert b["b2"]["64"]["mean"] == pytest.approx(0.9 + 0.045) and b["b2"]["16"]["draw_range"] == pytest.approx([0.51, 0.58])
    assert b["b2"]["64"]["union_size_range"] == [4001, 4008]
    c = C.coarse(units, lead)
    assert c["whole_matrix"]["n80"] == {"mean_harm": 0.5, "moved_alive_over_half": 0.5, "zeros_on_never_needed": 0.75}
    d = C.rounding(units, lead)
    assert d["n160"]["rounded"] == pytest.approx(0.8) and d["n160"]["snapped"] == pytest.approx(0.9) and d["rounded_start_harm"] == 0.25
    deltas = {row: {"exactly_0": 1, "exactly_1": 2, "between": 3} for row in B.SPLIT_ROWS}
    text = C.report(a, deltas, b, c, d)
    assert "snapped (at most 0.2 to 0, at least 0.8 to 1) 0.90" in text and "beside the start's 0.22 and the first post's 0.34" in text


@pytest.mark.skipif(not C.RUN_UNITS_LOCAL.is_dir(), reason="the run's unit files are on this machine only")
def test_the_delta_entry_counts_cover_every_saved_delta_entry():
    lead = SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT)
    counts = C.delta_entry_values(lead)
    assert all(sum(v.values()) == 80 * 24 for v in counts.values())
