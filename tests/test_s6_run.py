"""Session 6, plan 2: the GPU re-scoring's container job on the tiny model, on a CPU, and its local side.

The job runs an S4 held-out batch (H1, with the delta-on free check) and an attack pair, on made-up run units, with every
reference value scored independently through `adversary.score_per_text`; then a restart skips every unit; wrong references
and wrong labels stop it. The per-position sources are checked against a construction in numpy. The local side: the specs,
the projection from the committed ledger, the refusals before a launch, and the copy.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import lead_launch as LL
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import s6_build as B
from vpd_audit_2 import s6_run as SR

from tiny_model import tiny_component_model, tiny_ids

N_TEXTS = 8
COMMIT = "c" * 40
ATT = ["A1", "A2"]
STARTS = [9, 10]


class Tiny:
    def __init__(self) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, int(self.model.module_to_c[k])) for k in self.model.target_module_paths]
        self.n = sum(c + 1 for _, c in self.lay)
        rng = np.random.default_rng(4)
        self.starts = {s: rng.random(self.n).astype(np.float32) for s in STARTS}
        self.strata = {k: rng.integers(0, 11, c) for k, c in self.lay}
        self.ids = {b: tiny_ids(N_TEXTS, seed=30 + i).numpy() for i, b in enumerate(["H1"] + ATT)}
        self.rows = {b: LR.sha_rows(x) for b, x in self.ids.items()}
        self.units = {}
        for a in ATT:
            for s in STARTS:
                settings, cum = [], []
                for _ in B.SPLIT_ROWS:
                    u, v = rng.random(self.n), rng.random(self.n)
                    settings.append(np.where(u < 0.3, 0.0, np.where(u > 0.7, 1.0, v)).astype(np.float32))
                    cum.append(rng.normal(size=self.n).astype(np.float32))
                self.units[(a, s)] = {"hook_names": np.array([LR.SAVED[r] for r in B.SPLIT_ROWS]), "settings": np.stack(settings), "cum_signed": np.stack(cum)}
        self.b2 = {f"r{r}_d{d}": (rng.random(self.n) < 0.5).astype(np.float32) for r, d in ((64, 1), (16, 1))}
        self.preps = {b: A.prepare(self.model, self.ids[b], "fp32", device="cpu") for b in self.ids}

    def score(self, batch: str, flat: np.ndarray) -> float:
        return SR.score_flat(self.model, flat, self.preps[batch], self.lay, "cpu")[0]

    def refs(self) -> dict:
        out = {}
        st = {str(s): self.score("H1", self.starts[s]) for s in STARTS}
        out["H1"] = {"prep_fp": LR.prep_fingerprint(self.preps["H1"]), "own_attack": "A1", "check_attack": "A1",
                     "check_carried": self.score("H1", B.saved(self.units[("A1", 9)], "n320")[0]), "check_start": st["9"], "start": st,
                     "exploit_carried": {f"{s}|{row}": self.score("H1", B.saved(self.units[("A1", s)], row)[0]) for s in STARTS for row in B.EXPLOIT_ROWS},
                     "delta_on_start": {str(s): self.score("H1", B.delta_reset(self.starts[s], self.lay)) for s in STARTS}}
        for a in ATT:
            out[a] = {"prep_fp": LR.prep_fingerprint(self.preps[a]), "own_attack": a, "check_attack": a,
                      "check_carried": self.score(a, B.saved(self.units[(a, 9)], "n320")[0]), "check_start": self.score(a, self.starts[9]),
                      "start": {}, "exploit_carried": {}, "delta_on_start": None}
        return out

    def inputs(self, side: str) -> SR.Inputs:
        return SR.Inputs(starts=self.starts, strata=self.strata, read_run_unit=lambda a, s: self.units[(a, s)], b2=self.b2 if side == "heldout" else None)

    def spec(self, side: str, refs: dict) -> dict:
        batches = ["H1"] if side == "heldout" else ATT
        return {"arm": "s6", "side": side, "batch": "+".join(batches), "batches": batches, "commit": COMMIT, "mode": "s6", "root": "", "units": "",
                "run": "s6_followups", "attack_batches": ATT, "starts": STARTS, "refs": {b: refs[b] for b in batches}}

    def ctx(self, units: Path, lines: list) -> SR.Context:
        return SR.Context(commit=COMMIT, units=units, lay=self.lay, device="cpu", precision="fp32", mode="test", log=LR.Log(sink=lines.append))


@pytest.fixture(scope="module")
def tiny():
    return Tiny()


@pytest.fixture(scope="module")
def ran(tiny, tmp_path_factory):
    units = tmp_path_factory.mktemp("s6units")
    refs = tiny.refs()
    lines: list = []
    held = SR.job(tiny.model, tiny.ctx(units, lines), tiny.spec("heldout", refs), {"H1": (tiny.ids["H1"], tiny.rows["H1"])}, tiny.inputs("heldout"))
    att = SR.job(tiny.model, tiny.ctx(units, lines), tiny.spec("attack", refs), {a: (tiny.ids[a], tiny.rows[a]) for a in ATT}, tiny.inputs("attack"))
    return {"units": units, "refs": refs, "held": held, "att": att, "lines": lines}


def _load(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {"ids": [str(x) for x in z["pass_ids"]], "harm": z["harm"], "per_text": z["per_text"], "recorded": SR.json_field(z, "recorded"),
                "meta": SR.json_field(z, "meta")}


def test_a_run_unit_is_read_from_its_bytes_and_checked():
    """The container reads the run's search units through `run_unit_from_bytes`: here on a committed-format unit."""
    p = SR.LL.REPO_ROOT / ".cache" / "s5_lead_units" / "run" / "lead" / "search_A3_s11.npz"
    if not p.is_file():
        pytest.skip("the run's unit files are on this machine only")
    u = SR.run_unit_from_bytes(p.read_bytes(), "A3", 11)
    assert u["settings"].shape[1] == 38936 and "step_320" in [str(x) for x in u["hook_names"]]
    with pytest.raises(SR.S6Failure):
        SR.run_unit_from_bytes(p.read_bytes(), "A3", 12)


def test_every_unit_of_both_containers_is_written_and_its_checks_hold(tiny, ran):
    held, att = ran["held"], ran["att"]
    want_h = B.heldout_units("H1", ATT, STARTS, "A1")
    assert held["finished_units"] == held["expected_units"] == len(want_h) and not held["stopped"]
    assert att["finished_units"] == att["expected_units"] == 2 * len(B.attack_units("A1", STARTS))
    assert all(all(u["guards"].values()) for u in held["units"] + att["units"])
    g = {u["unit"]: u["guards"] for u in held["units"]}
    assert g["check_H1"] == {"split_path_s_everywhere": True, "split_path_s0_everywhere": True}
    assert g["exploit_H1_s9_n320"] == {"k0_is_the_saved_start": True, "kn_is_the_saved_carried": True}
    assert g["control_starts_H1"] == {"reset_start_9_is_the_delta_on_arms": True, "reset_start_10_is_the_delta_on_arms": True}
    for name, kind, params in want_h:
        u = _load(ran["units"] / f"{name}.npz")
        n = B.n_passes(kind, params.get("row"), tiny.n, n_starts=len(STARTS))
        if kind == "b":
            n = 1 + len(tiny.b2)
        assert len(u["ids"]) == u["harm"].size == u["per_text"].shape[0] == n, name
        assert u["per_text"].shape[1] == N_TEXTS and u["meta"]["commit"] == COMMIT
        assert np.allclose(u["per_text"].astype(np.float64).mean(axis=1), u["harm"], rtol=1e-5), name  # each pass's texts average to its harm


def test_the_split_paths_check_is_exact_on_the_cpu_and_the_label_counts_are_recorded(tiny, ran):
    u = _load(ran["units"] / "check_H1.npz")
    assert u["ids"] == ["check|s_everywhere", "check|s0_everywhere"]
    assert all(r["bits_equal"] for r in u["recorded"])  # the per-position path equals the broadcast one, bit for bit
    st = u["meta"]["label_stats"]
    labels = torch.cat([v.reshape(-1) for v in tiny.preps["H1"].labels.values()])
    assert st["zero_total"] == int((labels == 0).sum()) > 0 and st["positions"] == N_TEXTS * tiny.ids["H1"].shape[1]


def test_a_flat_pass_is_the_runs_scoring_and_the_endpoints_are_the_saved_harms(tiny, ran):
    u = _load(ran["units"] / "exploit_H1_s10_n80.npz")
    i0, i_n = u["ids"].index("top|0"), u["ids"].index(f"top|{tiny.n}")
    assert u["harm"][i0] == ran["refs"]["H1"]["start"]["10"] and u["harm"][i_n] == ran["refs"]["H1"]["exploit_carried"]["10|n80"]
    # a pass rebuilt from the same inputs scores what the unit recorded
    cells = B.cells_of(tiny.lay, tiny.strata)
    s, G = B.saved(tiny.units[("A1", 10)], "n80")
    rebuilt = {pid: f for pid, f, _ in B.exploit_passes(s, tiny.starts[10], G, cells, "A1", 10, "n80")}
    k = u["ids"].index("off|10")
    assert u["harm"][k] == tiny.score("H1", rebuilt["off|10"]) and u["recorded"][k]["setting_sha"] == B.sha(rebuilt["off|10"])


def test_the_per_position_sources_are_the_parts_the_conventions_define(tiny):
    prep = tiny.preps["H1"]
    zero = SR.zero_masks(prep)
    s, _ = B.saved(tiny.units[("A2", 9)], "n40")
    s0 = tiny.starts[9]
    z = SR.split_sources(zero, s, s0, s, tiny.lay, "cpu")
    p = SR.split_sources(zero, s0, s, s0, tiny.lay, "cpu")
    off = 0
    for name, C in tiny.lay:
        lab = prep.labels[name].numpy()
        want_z = np.where(lab == 0, s[off : off + C], s0[off : off + C])
        want_p = np.where(lab > 0, s[off : off + C], s0[off : off + C])
        assert np.array_equal(z[name][..., :C].numpy(), want_z) and np.array_equal(p[name][..., :C].numpy(), want_p)
        assert (z[name][..., C].numpy() == s[off + C]).all() and (p[name][..., C].numpy() == s0[off + C]).all()  # the delta entry
        off += C + 1
    # with s = s0, either part is the start
    h, _ = SR.score_split(tiny.model, prep, zero, "Z", s0, s0, tiny.lay, "cpu")
    assert h == tiny.score("H1", s0)


def test_a_restart_skips_every_finished_unit(tiny, ran):
    lines: list = []
    again = SR.job(tiny.model, tiny.ctx(ran["units"], lines), tiny.spec("heldout", ran["refs"]), {"H1": (tiny.ids["H1"], tiny.rows["H1"])}, tiny.inputs("heldout"))
    assert all(u["skipped"] for u in again["units"]) and {u["unit"]: u["sha256"] for u in again["units"]} == {u["unit"]: u["sha256"] for u in ran["held"]["units"]}


def test_wrong_references_or_labels_stop_the_container(tiny, tmp_path):
    refs = tiny.refs()
    bad = json.loads(json.dumps(refs))
    bad["H1"]["exploit_carried"]["9|n40"] = float(np.nextafter(bad["H1"]["exploit_carried"]["9|n40"], 1e9))
    with pytest.raises(SR.S6Failure, match="endpoints"):
        SR.job(tiny.model, tiny.ctx(tmp_path / "u1", []), tiny.spec("heldout", bad), {"H1": (tiny.ids["H1"], tiny.rows["H1"])}, tiny.inputs("heldout"))
    bad = json.loads(json.dumps(refs))
    bad["H1"]["check_carried"] *= 1.001
    with pytest.raises(SR.S6Failure, match="split's path"):
        SR.job(tiny.model, tiny.ctx(tmp_path / "u2", []), tiny.spec("heldout", bad), {"H1": (tiny.ids["H1"], tiny.rows["H1"])}, tiny.inputs("heldout"))
    bad = json.loads(json.dumps(refs))
    bad["H1"]["delta_on_start"]["10"] += 1e-9
    with pytest.raises(SR.S6Failure, match="delta-on"):
        SR.job(tiny.model, tiny.ctx(tmp_path / "u3", []), tiny.spec("heldout", bad), {"H1": (tiny.ids["H1"], tiny.rows["H1"])}, tiny.inputs("heldout"))
    with pytest.raises(LR.GuardFailure, match="prep_fp"):
        SR.job(tiny.model, tiny.ctx(tmp_path / "u4", []), tiny.spec("heldout", refs), {"H1": (tiny.ids["A1"], tiny.rows["A1"])}, tiny.inputs("heldout"))


# ----------------------------------------------------------------------------- the local side


def test_the_specs_and_their_check():
    refs = {b: {"x": 1} for b in SR.HELDOUT + SR.ATTACK}
    sp = SR.specs(COMMIT, refs)
    assert len(sp) == 24 and [s["batch"] for s in sp][-1] == "A15+A16" and sp[0]["refs"] == {"H1": {"x": 1}}
    for s in sp:
        SR.check_spec(s)
        SR.check_spec({**s, "launch": "ap|s6_wave1|1"})
    assert [s["batch"] for s in SR.specs(COMMIT, refs, 1)] == ["H1"] and len(SR.specs(COMMIT, refs, 2)) == 23
    for change in ({"side": "attack"}, {"batch": "A1"}, {"starts": [9, 10]}, {"root": "/cache/s5_lead"}, {"mode": "deciding"}, {"extra": 1}):
        with pytest.raises(LR.GuardFailure):
            SR.check_spec({**sp[0], **change})


def test_the_projection_from_the_committed_records():
    p = SR.projection(6.552504)
    assert p["passes"] == 12 * 1975 + 4 * 3985 + 8 * 106 == 40488  # by hand from the plan's units
    assert 0.18 < p["per_pass_seconds"] < 0.21 and p["exceeds_cap"] is False and p["cap"] == 45.0
    assert SR.projection(6.552504, split_factor=1.0)["projected_dollars"] < p["projected_dollars"] < 45.0


def test_a_launch_is_refused_over_the_cap_or_out_of_order(tmp_path, monkeypatch):
    monkeypatch.setattr(SR, "RESULTS", tmp_path)
    monkeypatch.setattr(SR, "check_launch_commit", lambda commit: None)
    spawned = []
    cloud = LL.Cloud(spawn=spawned.append, set_stop=lambda v: None, attempts=lambda s: 0, read_bill=lambda apps: {}, guards=lambda s: {}, app_id="ap-x",
                     log=lambda **f: None)
    with pytest.raises(LL.LaunchRefusal, match="wave 1 is not complete"):
        SR.launch_command(COMMIT, 2, cloud, listed_hourly_price=6.55)
    monkeypatch.setattr(SR, "CAP_DOLLARS", 1.0)
    with pytest.raises(LL.LaunchRefusal, match="C0"):
        SR.launch_command(COMMIT, 1, cloud, listed_hourly_price=6.55)
    assert spawned == [] and json.load(open(tmp_path / "ledger.json"))["checks"][0]["exceeds_cap"] is True


def test_the_references_are_read_from_the_runs_tables():
    lead = SR.load_table_checked(SR.LEAD_TABLE, SR.LEAD_RECEIPT)
    delta = SR.load_table_checked(SR.DELTA_TABLE, SR.DELTA_RECEIPT)
    r = SR.references(lead, delta)
    assert set(r) == set(SR.HELDOUT + SR.ATTACK)
    assert r["H1"]["delta_on_start"] is not None and r["H5"]["delta_on_start"] is not None and r["H9"]["delta_on_start"] is None
    assert r["H3"]["own_attack"] == "A3" and r["H3"]["check_carried"] == float(lead["carried"][2, 2, 0, list(lead["setting_names"]).index("n320")])
    assert r["H1"]["delta_on_start"]["9"] == float(delta["init_H"][0, 0]) and r["A7"]["check_start"] == float(lead["init_A"][6, 0])
    assert len(SR.run_unit_hashes()) == 160


def test_the_copy_checks_every_unit_against_its_containers_hash(tiny, ran, tmp_path, monkeypatch):
    monkeypatch.setattr(SR, "HELDOUT", ("H1",))
    monkeypatch.setattr(SR, "ATTACK", tuple(ATT))
    monkeypatch.setattr(SR, "STARTS", tuple(STARTS))
    monkeypatch.setattr(SR, "RESULTS", tmp_path)
    monkeypatch.setattr(SR, "VOLUME", str(ran["units"].parent))
    monkeypatch.setattr(SR, "UNITS", ran["units"].name)
    monkeypatch.setattr(SR, "tree_holds_only_this_plans_records", lambda: True)
    monkeypatch.setattr(LL, "head_commit", lambda: COMMIT)
    for w, containers in ((1, [ran["held"]]), (2, [ran["att"]])):
        LL.write_json(tmp_path / f"runs_{SR.STAGES[w].name}.json", {"commit": COMMIT, "summary": {"complete": True}, "containers": containers})
    got = SR.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes(), log=lambda **f: None, dest=tmp_path / "copy")
    assert len(got) == len(list((tmp_path / "copy").glob("*.npz"))) == ran["held"]["finished_units"] + ran["att"]["finished_units"]
    assert all(hashlib.sha256((tmp_path / "copy" / f"{k}.npz").read_bytes()).hexdigest() == v for k, v in got.items())
    with pytest.raises(LL.LaunchRefusal, match="do not have the hash"):
        SR.collect_command(COMMIT, read_file=lambda remote: Path(remote).read_bytes() + b"x", log=lambda **f: None, dest=tmp_path / "copy2")
