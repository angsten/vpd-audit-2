"""Session 7, plan 5: probe 1's launch without the cloud (`vpd_audit_2/probe1_run.py`), on the tiny model.

  - The specs and their refusals.
  - The whole run through the commands the cloud module calls: the validation stage, its collection and verdict, the
    320-step stage and the 80-step stage, each collected; one unit rescored independently; a restart skipping finished
    units; and the reading on the collected units.
  - Nothing scores unless the validation passed, nothing launches over the cap, and the projection's arithmetic.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_intervals as LI
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import probe1 as P1
from vpd_audit_2 import probe1_read as RD
from vpd_audit_2 import probe1_run as PR
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR

from tiny_model import tiny_component_model, tiny_ids

LISTED = 6.552504
COMMIT = "c" * 40
ATT, HELD, STARTS = ("A1", "A2"), ("H1", "H2"), (9, 10)
N, CH = 8, 4


def _patch_design(mp: pytest.MonkeyPatch) -> None:
    mp.setattr(PR, "ATTACK", ATT)
    mp.setattr(PR, "HELDOUT", HELD)
    mp.setattr(PR, "STARTS", STARTS)
    mp.setattr(PR, "N_TEXTS", N)
    mp.setattr(PR, "CHUNK", CH)


def test_the_specs_and_their_refusals():
    refs = {b: {"prep_fp": "x"} for b in PR.HELDOUT + PR.ATTACK}
    v = PR.specs("validation", COMMIT, refs, PR.DEFAULT_POINTS["validation"])
    assert len(v) == 1 and v[0]["batches"] == ["H1"] and v[0]["row"] == "n320"
    s = PR.specs("s320", COMMIT, refs, ("intact", "pattern"))
    assert [x["batch"] for x in s] == [f"H{2 * k + 1}+H{2 * k + 2}" for k in range(8)] + ["+".join(f"A{i}" for i in range(1, 9)),
                                                                                         "+".join(f"A{i}" for i in range(9, 17))]
    for x in v + s + PR.specs("s80", COMMIT, refs, ("intact",)):
        PR.check_spec(x)
    for change in ({"batches": ["H1", "H3"], "batch": "H1+H3"}, {"row": "n80"}, {"points": ["pattern"]}, {"root": "/cache/elsewhere"}, {"commit": "x"},
                   {"side": "attack"}, {"refs": {"H1": {}}}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            PR.check_spec({**s[0], **change})
    with pytest.raises(LR.GuardFailure):
        PR.check_spec({**v[0], "points": ["intact"]})
    assert PR.settings_for(s[0], "H1") == [(a, st) for a in PR.ATTACK for st in PR.STARTS] and PR.settings_for(s[-1], "A9") == [("A9", st) for st in PR.STARTS]
    assert len(PR.expected_files("s320")) == 2 * (16 * 80 + 16 * 5) and len(PR.expected_files("validation")) == 1


def test_the_projection_arithmetic():
    t = {"to_ready": 100.0, "prep_batch": 20.0, "prep_batch_count": 1.0, "intact_graph": 3.0, "intact_graph_count": 4.0, "cell_intact_pattern": 10.0,
         "cell_intact_pattern_count": 10.0, "cell_intact": 5.0, "cell_intact_count": 10.0, "unit_write_intact_pattern": 2.0, "unit_write_intact_pattern_count": 10.0,
         "unit_write_intact": 1.0, "unit_write_intact_count": 10.0, "volume_commit": 2.0, "volume_commit_count": 1.0}
    s = PR.stage_seconds("s320", ("intact", "pattern"), t)
    held_units, att_units = 2 * 80 * 2, 8 * 5 * 2
    want = 8 * (80 + 2 * (20 + 2 * 0.75) + held_units * 1.2 + (held_units // 20 + 1) * 2) + 2 * (80 + 8 * (20 + 2 * 0.75) + att_units * 1.2 + (att_units // 20 + 1) * 2)
    assert s["seconds"] == pytest.approx(want) and s["units"] == 8 * held_units + 2 * att_units


class Tiny:
    def __init__(self) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, int(self.model.module_to_c[k])) for k in self.model.target_module_paths]
        E = P1.n_entries(self.lay)
        rng = np.random.default_rng(21)
        self.ids = {b: tiny_ids(N, seed=100 + q).numpy() for q, b in enumerate(HELD + ATT)}
        self.rows = {b: LR.sha_rows(v) for b, v in self.ids.items()}
        self.units = {(a, s): {"hook_names": np.array([LR.SAVED["n80"], LR.SAVED["n320"]]), "settings": rng.random((2, E)).astype(np.float32),
                               "cum_signed": np.zeros((2, E), dtype=np.float32)} for a in ATT for s in STARTS}
        self.refs = {b: {"prep_fp": LR.prep_fingerprint(A.prepare(self.model, v, "fp32", device="cpu"))} for b, v in self.ids.items()}
        self.refs["H1"].update({"lead_carried": 1.5, "s6_rounded": 1.4})
        self.strata = {k: rng.integers(0, 11, c) for k, c in self.lay}

    def read_run_unit(self, attack: str, start: int) -> dict:
        return self.units[(attack, start)]

    def cloud(self, spawned: list | None = None) -> LL.Cloud:
        me = self

        class Now:
            def __init__(self, spec: dict) -> None:
                self.spec = spec
                if spawned is not None:
                    spawned.append(spec)

            def get(self, timeout: float) -> dict:
                PR.check_spec(self.spec)
                root = Path(self.spec["root"])
                ctx = SR.Context(commit=COMMIT, units=root / self.spec["units"], lay=me.lay, device="cpu", precision="fp32", mode="test")
                inputs = {b: (me.ids[b], me.rows[b]) for b in self.spec["batches"]}
                out = PR.job(me.model, ctx, self.spec, inputs, me.read_run_unit, chunk=CH, scratch=root / PR.TIMING, n_texts=4, per_decile=1)
                out["attempts"] = 1
                return out

        return LL.Cloud(spawn=Now, set_stop=lambda value: None, attempts=lambda spec: 1, read_bill=lambda apps: {"read_at": "x", "by_app": {}},
                        guards=lambda spec: {"outcomes": {}, "seconds": 0.0}, app_id="ap-tiny", log=lambda **f: None)

    def inputs(self) -> RD.Inputs:
        codes = B.cells_of(self.lay, self.strata)
        settings = {(a, s, r): B.saved(self.units[(a, s)], r)[0] for a in ATT for s in STARTS for r in ("n320", "n80")}
        return RD.Inputs(lay=self.lay, codes=codes, strata_flat=codes % 12, attack=list(ATT), heldout=list(HELD), starts=list(STARTS),
                         text_ids_H=np.array([[f"{h}_{t}" for t in range(N)] for h in HELD]), settings=settings, s6_rounded=None)


def _paths(mp: pytest.MonkeyPatch, tmp: Path) -> None:
    mp.setattr(PR, "RESULTS", tmp / "results")
    mp.setattr(PR, "VOLUME", str(tmp / "volume"))
    mp.setattr(PR, "LOCAL", tmp / "local")
    mp.setattr(PR, "check_launch_commit", lambda commit: None)
    mp.setattr(PR, "tree_holds_only_this_plans_records", lambda: True)
    mp.setattr(LL, "head_commit", lambda: COMMIT)


@pytest.fixture(scope="module")
def tiny_run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("probe1_run")
    t = Tiny()
    read = lambda remote: Path(remote).read_bytes()  # noqa: E731
    with pytest.MonkeyPatch.context() as mp:
        _patch_design(mp)
        _paths(mp, tmp)
        val = PR.launch_command("validation", COMMIT, t.cloud(), listed_hourly_price=LISTED, refs=t.refs)
        PR.collect_command("validation", COMMIT, read_file=read, log=lambda **f: None, workers=1)
        verdict = PR.validate_command(COMMIT)
        mp.setattr(P1, "PASS_SIGN_SHARE", -1.0)  # the tiny model's logits reach 100: far from linear; the verdict is forced to exercise the rest
        mp.setattr(P1, "PASS_SPEARMAN", -1.0)
        forced = PR.validate_command(COMMIT)
        s320 = PR.launch_command("s320", COMMIT, t.cloud(), listed_hourly_price=LISTED, refs=t.refs)
        files320 = PR.collect_command("s320", COMMIT, read_file=read, log=lambda **f: None, workers=3)
        s80 = PR.launch_command("s80", COMMIT, t.cloud(), listed_hourly_price=LISTED, refs=t.refs)
        files80 = PR.collect_command("s80", COMMIT, read_file=read, log=lambda **f: None, workers=2)
        ledger = json.load(open(tmp / "results" / "ledger.json"))
        out = RD.compute(tmp / "results", units_folder=tmp / "local" / "units", inputs=t.inputs(), indices=LI.make_indices(2))
    return {"tmp": tmp, "t": t, "val": val, "verdict": verdict, "forced": forced, "s320": s320, "s80": s80, "files320": files320, "files80": files80,
            "ledger": ledger, "out": out}


def test_the_validation_stage(tiny_run):
    v, f = tiny_run["verdict"], tiny_run["forced"]
    assert tiny_run["val"]["complete"] is True and tiny_run["val"]["finished_units"] == 1
    assert v["pairs"] == 4 * 10 and set(v["by_component_decile"]) == {str(d) for d in range(10)} and v["null_spread_max"] < 1e-3
    assert f["passes"] is True and f["sign_share_above"] == v["sign_share_above"]
    t = v["timings"]
    for key in ("to_ready", "prep_batch", "intact_graph", "cell_intact_pattern", "cell_intact", "unit_write_intact_pattern", "unit_write_intact", "volume_commit"):
        assert t[key] >= 0 and (key == "to_ready" or t[key + "_count"] > 0), key
    assert not list((tiny_run["tmp"] / "volume" / PR.TIMING).glob("timing_*"))  # the scratch is emptied
    # the exact pushes are the moves themselves: one of them recomputed on its own
    t_ = tiny_run["t"]
    with np.load(tiny_run["tmp"] / "local" / "units" / f"{PR.validation_unit_name()}.npz", allow_pickle=False) as z:
        pairs, exact, texts, first = z["pairs"], z["exact"], z["texts"], z["first"]
    prep = A.prepare(t_.model, t_.ids["H1"], "fp32", device="cpu")
    batch = P1.as_float32_batch(t_.model, prep, t_.lay).take(texts.tolist())
    flat = B.saved(t_.units[("A1", 9)], "n320")[0]
    z_i, _ = P1.forward_at(t_.model, batch, None, grad=False)
    z_p, _ = P1.forward_at(t_.model, batch, P1.pattern_point(flat), grad=False)
    d, _ = P1.reference_direction(z_p, z_i)
    e, x = int(pairs[7, 0]), int(pairs[7, 1])
    sc = P1.scales_at(batch.n_texts, t_.lay, None, device="cpu", dtype=batch.dtype, requires_grad=False)
    name, local = P1.entry_of(e, t_.lay)
    sc[name][x, 0, local] = 1.0
    with torch.no_grad():
        z_m = P1.logits_at(t_.model, batch, {k: 1.0 - v for k, v in sc.items()})
    assert exact[7] == pytest.approx(float(((z_m[x] - z_i[x]) * d[x]).sum()), rel=1e-4, abs=1e-4)
    np.testing.assert_allclose(first, P1.first_order_pushes(t_.model, batch, flat)["intact"], rtol=1e-5, atol=1e-5)


def test_the_scoring_stages_and_one_unit_rescored(tiny_run):
    for s, files, n in ((tiny_run["s320"], tiny_run["files320"], 2 * (2 * 4 + 2 * 2)), (tiny_run["s80"], tiny_run["files80"], 2 * (2 * 4 + 2 * 2))):
        assert s["complete"] is True and s["all_guards_true"] is True and s["finished_units"] == s["expected_units"] == n and len(files) == n
    t = tiny_run["t"]
    with np.load(tiny_run["tmp"] / "local" / "units" / f"{RD.unit_name('s320', 'H2', 'A2', 10, 1)}.npz", allow_pickle=False) as z:
        intact, pattern, kl, texts = z["intact"], z["pattern"], z["pattern_kl"], z["texts"]
        meta = SR.json_field(z, "meta")
    assert texts.tolist() == list(range(CH, 2 * CH)) and meta["points"] == ["intact", "pattern"] and meta["commit"] == COMMIT
    flat = B.saved(t.units[("A2", 10)], "n320")[0]
    assert meta["setting_sha"] == B.sha(flat) and meta["rounded_sha"] == B.sha(P1.rounded(flat))
    prep = A.prepare(t.model, t.ids["H2"], "fp32", device="cpu")
    batch = P1.as_float32_batch(t.model, prep, t.lay).take(slice(CH, 2 * CH))
    alone = P1.first_order_pushes(t.model, batch, flat, ("intact", "pattern"))
    np.testing.assert_allclose(intact, alone["intact"], rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(pattern, alone["pattern"], rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(kl, alone["pattern_kl"], rtol=1e-6)
    with np.load(tiny_run["tmp"] / "local" / "units" / f"{RD.unit_name('s80', 'A1', 'A1', 9, 0)}.npz", allow_pickle=False) as z:
        assert "pattern" not in z.files and SR.json_field(z, "meta")["row"] == "n80"
    checks = [c for c in tiny_run["ledger"]["checks"]]
    assert [c["check"] for c in checks if c["check"].startswith("before_")] == ["before_validation", "before_s320", "before_s80"]
    assert all(not c["exceeds_cap"] for c in checks)
    assert tiny_run["ledger"]["stages"]["s7_probe1_s320"]["points"] == ["intact", "pattern"]


def test_the_reading_on_the_collected_units(tiny_run):
    out = tiny_run["out"]
    assert set(out["rows"]) == {"n320", "n80"} and "full_pattern" in out["rows"]["n320"] and "full_pattern" not in out["rows"]["n80"]
    d = out["row_d"]["components"]
    assert out["rows"]["n320"]["cells"] == 2 * 2 * 2 and 0 < len(d) <= 8 and [c["cell"] for c in d] == sorted((c["cell"] for c in d), key=["off", "on"].index)
    assert out["rows"]["n320"]["checks"]["intact_max_text_kl"] < 1e-6


def test_a_restart_skips_finished_units(tiny_run):
    t = tiny_run["t"]
    with pytest.MonkeyPatch.context() as mp:
        _patch_design(mp)
        _paths(mp, tiny_run["tmp"])
        spec = PR.specs("s320", COMMIT, t.refs, ("intact", "pattern"))[0]
        ctx = SR.Context(commit=COMMIT, units=Path(spec["root"]) / spec["units"], lay=t.lay, device="cpu", precision="fp32", mode="test")
        out = PR.job(t.model, ctx, spec, {b: (t.ids[b], t.rows[b]) for b in spec["batches"]}, t.read_run_unit, chunk=CH)
    assert out["finished_units"] == out["expected_units"] == 2 * 2 * 2 * 2 and all(u["skipped"] for u in out["units"])
    assert "prep_batch" not in out["timings"]  # nothing left to score: the batch was not even prepared


def test_nothing_scores_unless_the_validation_passed_and_nothing_launches_over_the_cap(tiny_run, tmp_path):
    t = tiny_run["t"]
    with pytest.MonkeyPatch.context() as mp:
        _patch_design(mp)
        _paths(mp, tmp_path)
        spawned: list = []
        with pytest.raises(LL.LaunchRefusal, match="validation is not complete"):
            PR.launch_command("s320", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED, refs=t.refs)
        (tmp_path / "results").mkdir()
        ledger = {"stages": {"s7_probe1_validation": {"launches": [], "complete": True, "summary": None}}, "checks": [], "bills": [], "guards_pass": None,
                  "stopped_by": None, "stops": []}
        (tmp_path / "results" / "ledger.json").write_text(json.dumps(ledger))
        v = dict(json.load(open(tiny_run["tmp"] / "results" / "validation.json")))
        (tmp_path / "results" / "validation.json").write_text(json.dumps({**v, "passes": False}))
        with pytest.raises(LL.LaunchRefusal, match="validation has not passed"):
            PR.launch_command("s320", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED, refs=t.refs)
        slow = {**v, "passes": True, "timings": {**v["timings"], "cell_intact_pattern": v["timings"]["cell_intact_pattern"] * 1e6}}
        (tmp_path / "results" / "validation.json").write_text(json.dumps(slow))
        with pytest.raises(LL.LaunchRefusal, match="exceeds the cap"):
            PR.launch_command("s320", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED, refs=t.refs)
        assert spawned == []
        checks = json.load(open(tmp_path / "results" / "ledger.json"))["checks"]
        assert checks[-1]["check"] == "before_s320" and checks[-1]["exceeds_cap"] is True and checks[-1]["projected_dollars"] > 20
        with pytest.raises(LL.LaunchRefusal, match="not allowed"):
            PR.launch_command("validation", COMMIT, t.cloud(spawned), listed_hourly_price=LISTED, refs=t.refs, points=("intact",))


def test_nothing_in_the_driver_prints():
    import re

    for module in ("probe1", "probe1_run", "modal_probe1"):
        text = Path(PR.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", text), module
