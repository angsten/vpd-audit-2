"""Plan 2 of the research log, Section 6: the lead run on the tiny model, on a CPU.

The table specification's T1 (a small arm end to end against a brute-force reference), T2 (the saved settings' steps), T14 (kill and
restart at three points), T15 (nothing printed, logged, or returned holds a harm), T16 (the delta-on arm); each guard
G1 to G11 failing on its made-up input with a message that names it and carries no value; one commit; the per-text
parts; the two bit-identity proofs of plan 2 of the research log's Section 4; and the per-text wrapper (the table specification's Section 6, items 1 and 3).
"""

from __future__ import annotations

import hashlib
import io
import json
import re
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import numpy as np
import pytest
import torch

from vpd_audit_2 import env  # noqa: F401  (cache paths first)
from vpd_audit_2 import adversary as A
from vpd_audit_2 import g2
from vpd_audit_2 import lead_run as LR
from vpd_audit_2 import lead_table as LT
from vpd_audit_2 import pilot as P

from tiny_model import tiny_component_model, tiny_ids

DEV = "cpu"
N_TEXTS = 16
N_STEPS = 320  # the tiny arm's searches run the full length, so every fixed setting exists
COMMIT = "f" * 40


class Fixture:
    def __init__(self, tmp: Path, arm: str = "lead", starts: tuple[int, ...] = (9, 10)) -> None:
        torch.use_deterministic_algorithms(True)
        self.model = tiny_component_model()
        self.lay = [(k, self.model.module_to_c[k]) for k in self.model.target_module_paths]
        g = torch.Generator().manual_seed(11)
        self.starts = {s: {k: torch.rand((1, 1, C + 1), generator=g).numpy() for k, C in self.lay} for s in starts}
        self.ids = {name: tiny_ids(N_TEXTS, seed=seed).numpy() for name, seed in (("A1", 3), ("A2", 4), ("H1", 5), ("H2", 6), ("C1", 7))}
        self.rows = {name: LR.sha_rows(ids) for name, ids in self.ids.items()}
        self.strata = {k: np.random.default_rng(5).integers(0, 3, C) for k, C in self.lay}
        self.arm = arm
        self.tmp = tmp
        self.lines: list[str] = []

    def context(self, units: Path, **kw) -> LR.Context:
        args = {"arm": self.arm, "units": units, "commit": COMMIT, "lay": self.lay, "precision": "fp32", "device": DEV, "n_steps": N_STEPS,
                "mode": "test", "log": LR.Log(sink=self.lines.append), **kw}
        return LR.Context(**args)


@pytest.fixture(scope="module")
def fx(tmp_path_factory) -> Fixture:
    return Fixture(tmp_path_factory.mktemp("lead"))


@pytest.fixture(scope="module")
def small_arm(fx):
    """The lead arm on the tiny model: 2 attack batches, 2 held-out batches, 2 starts, through search, scoring, and assembly."""
    units = fx.tmp / "units"
    attack = {name: LR.attack_job(fx.model, fx.context(units), name, fx.ids[name], fx.rows[name], fx.starts) for name in ("A1", "A2")}
    heldout = {name: LR.heldout_job(fx.model, fx.context(units), name, fx.ids[name], fx.rows[name], fx.starts, ["A1", "A2"], fx.strata)
               for name in ("H1", "H2")}
    out = LR.assemble(units, fx.tmp / "table", "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], text_ids_H=[[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)],
                      excluded=[{"pool": "H2", "index": 3}], inputs_sha256={"manifest": "x"}, containers=[], expect_commit=COMMIT)
    return {"units": units, "attack": attack, "heldout": heldout, "assembled": out, "table": LT.load_table(fx.tmp / "table")}


# ----------------------------------------------------------------------------- plan 2 of the research log, Section 4: the additions change nothing


def test_the_per_text_wrapper_and_cumulative_gradients_leave_the_search_bit_identical(fx):
    prep = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
    start = fx.starts[9]
    plain_hook = A.SaveHook(steps=(10, 20), thresholds=(0.5, 2.0))
    cum_hook = A.SaveHook(steps=(10, 20), thresholds=(0.5, 2.0))
    plain = A.run(fx.model, prep, start, 20, 0.1, save_hook=plain_hook, record_sources=True, record_grads=True, device=DEV)
    withcum = A.run(fx.model, prep, start, 20, 0.1, save_hook=cum_hook, cum_grads=True, record_sources=True, record_grads=True, device=DEV)
    assert plain["record"] == withcum["record"]  # every record entry
    assert np.array_equal(plain["source_record"].view(np.uint32), withcum["source_record"].view(np.uint32))  # every step's sources
    assert sorted(plain_hook.saved) == sorted(cum_hook.saved) and plain_hook.events == cum_hook.events
    for name in plain_hook.saved:  # every saved setting
        assert np.array_equal(plain_hook.saved[name].view(np.uint32), cum_hook.saved[name].view(np.uint32))
    # the cumulative gradients are the signed sum and the sum of absolute values over iterations 0 to k - 1
    for name, k in cum_hook.events.items():
        signed, absolute = cum_hook.cum[name]
        assert signed.dtype == absolute.dtype == np.float32
        expect_signed = plain["grad_record"][:k].astype(np.float64).sum(axis=0)
        expect_abs = np.abs(plain["grad_record"][:k].astype(np.float64)).sum(axis=0)
        assert np.allclose(signed, expect_signed, rtol=1e-6, atol=1e-7) and np.allclose(absolute, expect_abs, rtol=1e-6, atol=1e-7)
        if k > 0:
            assert (absolute >= np.abs(signed) - 1e-6).all()
    assert cum_hook.cum["step_10"][0].shape == (sum(c + 1 for _, c in fx.lay),)
    # and the search still equals the authors' loop bit for bit
    theirs = g2.authors_loop(fx.model, prep, start, 20, device=DEV)
    c = g2.compare_runs(theirs, withcum)
    assert c["sources_bitwise_equal_every_step"] and c["harm_bitwise_equal_every_step"]


def test_the_wrapper_equals_the_authors_function_bit_for_bit_and_its_values_are_per_text(fx):
    from param_decomp.models.batch_and_loss_fns import recon_loss_kl

    prep = A.prepare(fx.model, fx.ids["H1"], "fp32", device=DEV)
    found = A.run(fx.model, A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV), fx.starts[9], 8, 0.1, device=DEV)
    src = {k: torch.from_numpy(v) for k, v in found["sources"].items()}
    # item 1: the same sum as the authors' function on the same logits
    with torch.no_grad():
        s_authors, n_authors = A._forward(fx.model, prep.ids, src, prep.labels, prep.target_out, prep.weight_deltas)
        wrapper = A.KLWithPerText()
        s_ours, n_ours = A._forward(fx.model, prep.ids, src, prep.labels, prep.target_out, prep.weight_deltas, reconstruction_loss=wrapper)
    assert n_authors == n_ours and s_authors.detach().numpy().tobytes() == s_ours.detach().numpy().tobytes()
    assert A._forward.__defaults__ == (None,)  # the default is the authors' function: the search path is untouched
    harm, per_text = A.score_per_text(fx.model, found["sources"], prep, device=DEV)
    assert harm == A.score(fx.model, found["sources"], prep, device=DEV)
    assert per_text.shape == (N_TEXTS,) and per_text.dtype == np.float64
    assert abs(per_text.mean() - harm) <= 1e-5 * harm  # G5
    # item 3: each text's value equals its harm scored alone as a batch of one
    for t in (0, 5, 15):
        alone = A.prepare(fx.model, fx.ids["H1"][t : t + 1], "fp32", device=DEV)
        assert abs(A.score(fx.model, found["sources"], alone, device=DEV) - per_text[t]) <= 1e-5 * per_text[t]
    # reordering the texts reorders the vector the same way
    perm = np.random.default_rng(1).permutation(N_TEXTS)
    _, shuffled = A.score_per_text(fx.model, found["sources"], A.prepare(fx.model, fx.ids["H1"][perm], "fp32", device=DEV), device=DEV)
    assert np.allclose(shuffled, per_text[perm], rtol=1e-6)
    # the tiny batch has as many texts as positions (16), so a mean along the wrong axis has the right shape: it must
    # still fail the check above. Here it is computed from the same tensor and shown to differ from the per-text values.
    class BothAxes(A.KLWithPerText):
        def __call__(self, pred, target):
            out = super().__call__(pred, target)
            import torch.nn.functional as F

            kl = F.kl_div(torch.log_softmax(pred, dim=-1), torch.softmax(target, dim=-1), reduction="none").sum(dim=-1)
            self.per_position = kl.double().mean(dim=0)
            return out

    both = BothAxes()
    with torch.no_grad():
        A._forward(fx.model, prep.ids, src, prep.labels, prep.target_out, prep.weight_deltas, reconstruction_loss=both)
    assert both.per_position.shape == both.per_text.shape == (N_TEXTS,)
    assert np.allclose(both.per_text.numpy(), per_text) and not np.allclose(both.per_position.numpy(), per_text, rtol=1e-3)
    alone0 = A.score(fx.model, found["sources"], A.prepare(fx.model, fx.ids["H1"][0:1], "fp32", device=DEV), device=DEV)
    assert abs(both.per_position.numpy()[0] - alone0) > 1e-3 * alone0  # the wrong axis fails item 3
    assert A.KLWithPerText.__doc__ and "line for line" in A.KLWithPerText.__doc__


# ----------------------------------------------------------------------------- T1: the small arm against a brute-force reference


def test_T1_the_small_arm_equals_a_brute_force_reference(fx, small_arm):
    table = small_arm["table"]
    LT.validate(table)
    names = list(LT.SETTINGS_LEAD)
    starts = [9, 10]
    for side, batches in (("A", ["A1", "A2"]), ("H", ["H1", "H2"])):
        for b, batch in enumerate(batches):
            prep = A.prepare(fx.model, fx.ids[batch], "fp32", device=DEV)
            for s, start in enumerate(starts):
                hook = A.SaveHook(steps=P.BUDGETS, thresholds=P.STAGES)
                ref = A.run(fx.model, prep, fx.starts[start], N_STEPS, 0.1, save_hook=hook, device=DEV)
                assert table[f"rec_{side}"][b, s].tolist() == ref["record"]  # the search's own record, bit for bit
                assert table[f"init_{side}"][b, s] == ref["record"][0]
                for q, name in enumerate(names):
                    tag = LR.SAVED[name]
                    if tag in hook.saved:
                        k = hook.events[tag]
                        assert table[f"step_{side}"][b, s, q] == k
                        assert table[f"own_{side}"][b, s, q] == ref["record"][k]
                        assert table[f"setting_sha_{side}"][b, s, q] == LR.setting_sha256(hook.saved[tag])
                    else:
                        assert table[f"step_{side}"][b, s, q] == -1 and np.isnan(table[f"own_{side}"][b, s, q])
    # carried and shuffled harms: plain loops over the saved settings, scored on the other side's batch
    for i, ab in enumerate(["A1", "A2"]):
        prep_a = A.prepare(fx.model, fx.ids[ab], "fp32", device=DEV)
        for s, start in enumerate(starts):
            hook = A.SaveHook(steps=P.BUDGETS, thresholds=P.STAGES)
            A.run(fx.model, prep_a, fx.starts[start], N_STEPS, 0.1, save_hook=hook, device=DEV)
            for j, hb in enumerate(["H1", "H2"]):
                prep_h = A.prepare(fx.model, fx.ids[hb], "fp32", device=DEV)
                for q, name in enumerate(names):
                    if table["step_A"][i, s, q] == -1:
                        continue
                    flat = hook.saved[LR.SAVED[name]]
                    expect = A.score(fx.model, P.unflatten(flat, fx.lay), prep_h, device=DEV)
                    assert table["carried"][i, j, s, q] == expect
                    assert table["carried"][i, j, s, q] != table["own_A"][i, s, q]  # `carried` differs from `own_A` everywhere
                    if name in LT.NO_SHUFFLES:  # steps 159 and 319 have no shuffled copies
                        assert np.isnan(table["shuf"][i, j, s, q]).all() and (table["shuf_sha"][i, s, q] == "").all()
                        continue
                    for r in range(1, 9):
                        copy = P.shuffle_source(flat, fx.lay, fx.strata, ("lead", ab, start, name, r), label=LR.SHUFFLE_LABEL)
                        assert table["shuf"][i, j, s, q, r - 1] == A.score(fx.model, P.unflatten(copy, fx.lay), prep_h, device=DEV)
                        assert table["shuf_sha"][i, s, q, r - 1] == LR.setting_sha256(copy)
    assert small_arm["assembled"]["outcomes"]["G6"] and small_arm["assembled"]["outcomes"]["G11_setting_is_the_attack_searchs"]
    assert small_arm["assembled"]["outcomes"]["table_checks_failed"] == []
    assert table["excluded_H"].sum() == 1 and table["excluded_H"][1, 3]
    assert table["meta"]["run_commit"] == COMMIT and table["meta"]["kind"] == "real"
    # the return value: names, hashes, sizes, and outcomes, and no pass count
    assert set(small_arm["assembled"]) == {"arm", "files", "design", "complete", "run_commit", "outcomes", "prep_fp_equal_to_lead", "prep_fp"}
    assert "n_scoring_passes" not in json.dumps(small_arm["assembled"])


def test_T2_every_saved_settings_first_entry_encodes_its_step(fx, tmp_path):
    """A record with entry k equal to k, and settings whose first entry encodes the step: the hook's saved steps equal
    the setting's first entry, through the unit file."""
    n_entries = sum(c + 1 for _, c in fx.lay)

    def fake_run(model, prep, start, n_steps, step_size, *, save_hook, cum_grads, device, frozen=None, **kw):
        record = []
        sources = {k: torch.zeros((1, 1, c + 1)) for k, c in fx.lay}
        first = next(iter(sources))
        for k in range(n_steps + 1):
            record.append(float(k))
            sources[first][..., 0] = float(k)  # the first entry encodes the step
            save_hook(k, record, sources, (np.zeros(n_entries), np.zeros(n_entries)))
        return {"record": record, "sources": {k: v.numpy() for k, v in sources.items()}}

    units = tmp_path / "units"
    ctx = fx.context(units, run=fake_run)
    prep = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
    # the re-scores cannot equal a fake record, so G4 fires; the hook's saving is checked before that
    with pytest.raises(LR.GuardFailure) as e:
        LR.search_unit(fx.model, prep, ctx, "attack", "A1", 9, fx.starts[9], "ids", "fp")
    assert e.value.guard == "G4"
    hook = A.SaveHook(steps=P.BUDGETS, thresholds=P.STAGES)
    fake_run(None, None, None, N_STEPS, 0.1, save_hook=hook, cum_grads=True, device=DEV)
    for name, k in hook.events.items():
        assert hook.saved[name][0] == float(k), name  # every saved setting's first entry equals its step
    # with entry k equal to k, the two-step mean at step k is k - 1/2, so it first reaches h at step h + 1
    expected = {f"step_{k}": k for n in P.BUDGETS for k in (n - 1, n)}
    assert hook.events == {**expected, "two_step_mean_reaches_2": 3, "two_step_mean_reaches_5": 6, "two_step_mean_reaches_10": 11}
    assert all(P.crossing(list(range(N_STEPS + 1)), h)["k"] == hook.events[f"two_step_mean_reaches_{h:g}"] for h in P.STAGES)


# ----------------------------------------------------------------------------- T14: kill and restart


def _run_arm(fx, units: Path, out: Path, fault=None, attack_units=None) -> list[dict]:
    files = []
    for name in ("A1", "A2"):
        LR.attack_job(fx.model, fx.context(units, fault=fault), name, fx.ids[name], fx.rows[name], fx.starts)
    for name in ("H1", "H2"):
        LR.heldout_job(fx.model, fx.context(units, fault=fault), name, fx.ids[name], fx.rows[name], fx.starts, ["A1", "A2"], fx.strata)
    res = LR.assemble(units, out, "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], text_ids_H=[[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)],
                      excluded=[{"pool": "H2", "index": 3}], inputs_sha256={"manifest": "x"}, containers=[], expect_commit=COMMIT)
    return res["files"]


class Kill(Exception):
    pass


def test_T14_kill_and_restart_at_three_points_give_identical_table_bytes(fx, small_arm, tmp_path):
    reference = small_arm["assembled"]["files"]
    for point, nth in (("between_units", 3), ("unit_renamed", 2), ("in_block", 2)):
        units, out = tmp_path / point / "units", tmp_path / point / "table"
        seen = {"n": 0}

        def fault(where: str, point=point, nth=nth) -> None:
            if where == point:
                seen["n"] += 1
                if seen["n"] == nth:
                    raise Kill(where)

        with pytest.raises(Kill):
            _run_arm(fx, units, out, fault=fault)
        if point == "unit_renamed":  # a file renamed but without its marker
            dangling = [p for p in units.iterdir() if p.suffix == ".npz" and not LR.marker(p).exists()]
            assert len(dangling) == 1
        if point == "in_block":  # killed inside the first scoring block: every search is on disk and no block is
            assert sum(p.name.startswith("search_") and p.suffix == ".npz" for p in units.iterdir()) == 6
            assert not any(p.name.startswith("block_") for p in units.iterdir())
        before = sorted(p.name for p in units.iterdir())
        files = _run_arm(fx, units, out)  # the restart
        assert files == reference, point  # identical table bytes
        # the restart skipped every finished unit and redid the unfinished one
        skipped = [json.loads(ln) for ln in fx.lines if '"unit_skipped"' in ln]
        assert skipped and all(s["guard"] == "G3" and s["ok"] for s in skipped)
        assert not any(p.name.endswith(".tmp") for p in units.iterdir())
        assert len(before) <= len(list(units.iterdir()))


def test_G3_restart_stops_when_one_label_differs_by_one_unit(fx, small_arm, tmp_path):
    """G3 (the table specification's row): perturb one label by one unit after a restart, and the container stops. A finished unit rests on
    a fingerprint the restarted container must reproduce bit for bit."""
    import shutil

    units = tmp_path / "units"
    units.mkdir()
    for s in (9, 10):  # the attack container of A1 has finished its two units
        for p in (LR.search_file(small_arm["units"], "A1", s), LR.marker(LR.search_file(small_arm["units"], "A1", s))):
            shutil.copy(p, units / p.name)
    again = LR.attack_job(fx.model, fx.context(units), "A1", fx.ids["A1"], fx.rows["A1"], fx.starts)  # an honest restart
    assert [u["skipped"] for u in again["units"]] == [True, True] and all(u["guards"] == {"G3": True} for u in again["units"])

    def one_unit_off(model, ids, precision, device):
        prep = A.prepare(model, ids, precision, device=device)
        k = next(iter(prep.labels))
        x = prep.labels[k].clone()
        x[3, 5, 1] = torch.nextafter(x[3, 5, 1], torch.tensor(2.0))  # one label, the smallest step
        prep.labels[k] = x
        return prep

    with pytest.raises(LR.GuardFailure) as e:
        LR.attack_job(fx.model, fx.context(units, prepare=one_unit_off), "A1", fx.ids["A1"], fx.rows["A1"], fx.starts)
    assert (e.value.guard, e.value.unit) == ("G3", "search|lead|A1|s9") and str(e.value) == "guard G3 failed in unit search|lead|A1|s9"
    # a unit left by another commit is refused at once, not at the end of the run
    other = fx.context(units)
    other.commit = "e" * 40
    with pytest.raises(LR.GuardFailure) as e:
        LR.attack_job(fx.model, other, "A1", fx.ids["A1"], fx.rows["A1"], fx.starts)
    assert e.value.guard == "one_commit"


def test_the_fingerprint_is_bit_exact(fx):
    """Any one entry changed by its smallest step, in the labels, the target, or the weight deltas, changes it; so do a
    change of sign of a zero and two entries exchanged. The same tensors give the same fingerprint."""
    prep = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
    base = LR.prep_fingerprint(prep)
    assert base == LR.prep_fingerprint(A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)) and len(base) == 64
    assert base != LR.prep_fingerprint(A.prepare(fx.model, fx.ids["A2"], "fp32", device=DEV))

    def changed(edit) -> str:
        p = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
        edit(p)
        return LR.prep_fingerprint(p)

    def bump(t, index):
        t = t.clone()
        t[index] = torch.nextafter(t[index], torch.tensor(float("inf")))
        return t

    last = list(prep.labels)[-1]
    deltas = list(prep.weight_deltas)
    edits = {
        "the first label": lambda p: p.labels.__setitem__(list(p.labels)[0], bump(p.labels[list(p.labels)[0]], (0, 0, 0))),
        "the last label": lambda p: p.labels.__setitem__(last, bump(p.labels[last], (-1, -1, -1))),
        "one target logit": lambda p: setattr(p, "target_out", bump(p.target_out, (7, 3, 11))),
        "one weight delta": lambda p: p.weight_deltas.__setitem__(deltas[2], bump(p.weight_deltas[deltas[2]], (1, 1))),
    }
    seen = {base}
    for name, edit in edits.items():
        fp = changed(edit)
        assert fp not in seen, name
        seen.add(fp)

    def swap(p):
        t = p.target_out.clone()
        a, b = t[0, 0, 0].clone(), t[0, 0, 1].clone()
        assert a != b
        t[0, 0, 0], t[0, 0, 1] = b, a
        p.target_out = t

    assert changed(swap) not in seen
    # the checksum reads bits: zero and minus zero differ, and its sums are exact whatever the order of the entries' addition
    z = torch.zeros(5)
    assert LR.tensor_checksum(z) != LR.tensor_checksum(-z) and LR.tensor_checksum(z) == (0, 0)
    x = torch.randn(1000, generator=torch.Generator().manual_seed(0))
    assert LR.tensor_checksum(x) == LR.tensor_checksum(x.clone().reshape(10, 100)) != LR.tensor_checksum(x.flip(0))
    big = torch.randn(3 * 7, generator=torch.Generator().manual_seed(1)).to(torch.bfloat16)
    old = LR.FP_CHUNK
    try:
        LR.FP_CHUNK = 4  # the same sums whatever the chunk
        chunked = LR.tensor_checksum(big)
    finally:
        LR.FP_CHUNK = old
    assert chunked == LR.tensor_checksum(big)


# ----------------------------------------------------------------------------- T15: nothing printed, logged, or returned holds a harm


def test_T15_no_harm_in_anything_printed_logged_or_returned(fx, tmp_path, small_arm):
    fx.lines.clear()
    out, err = io.StringIO(), io.StringIO()
    units = tmp_path / "units"
    with redirect_stdout(out), redirect_stderr(err):
        res = [LR.attack_job(fx.model, fx.context(units), "A1", fx.ids["A1"], fx.rows["A1"], fx.starts),
               LR.heldout_job(fx.model, fx.context(units), "H1", fx.ids["H1"], fx.rows["H1"], fx.starts, ["A1"], fx.strata)]
        assembled = LR.assemble(units, tmp_path / "t", "lead", ["A1"], ["H1"], [9, 10], text_ids_H=[[f"t{k}" for k in range(N_TEXTS)]], excluded=[],
                                inputs_sha256={}, containers=[], expect_commit=COMMIT)
    assert out.getvalue() == "" and err.getvalue() == ""  # the jobs print nothing themselves; the log's sink is the caller's
    # a job returns the container's name, its units, two counts, whether it was stopped, its seconds, and the environment
    for job in res:
        assert set(job) == {"container", "units", "finished_units", "expected_units", "stopped", "seconds", "environment"}
        assert type(job["seconds"]) is float and job["finished_units"] == job["expected_units"] == len(job["units"]) and job["stopped"] is False
    assert [job["expected_units"] for job in res] == [2, 4]
    # no floating-point number anywhere outside the per-container `seconds` field; hashes are hexadecimal, not numbers
    logged = [json.loads(ln) for ln in fx.lines]
    assert all(("seconds" not in rec) or ("container" in rec and rec["event"] == "container_finished") for rec in logged)
    without_seconds = [{k: v for k, v in x.items() if k != "seconds"} for x in res + logged]
    captured = json.dumps(without_seconds) + json.dumps(assembled)
    floats = re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", re.sub(r"[0-9a-f]{64}", "", captured))
    assert floats == [], floats[:5]

    def holds_a_float(x) -> bool:  # by type, so that a float in any notation counts (1e-05, nan, inf)
        if isinstance(x, dict):
            return any(holds_a_float(v) for v in x.values())
        if isinstance(x, (list, tuple)):
            return any(holds_a_float(v) for v in x)
        return isinstance(x, (float, np.floating))

    assert not holds_a_float(without_seconds) and not holds_a_float(assembled)
    assert holds_a_float(res)  # the walk does see the seconds it was spared
    # no per-setting hash, pass count, or file size in a return value, and no timing finer than a container
    returned = json.dumps(res) + json.dumps(assembled)
    for word in ("n_scoring_passes", "size", "passes", "timings", "per_step", "setting_sha"):
        assert word not in returned, word
    for unit in res[0]["units"] + res[1]["units"]:
        assert set(unit) == {"unit", "sha256", "guards", "skipped"} and all(isinstance(v, bool) for v in unit["guards"].values())
    with pytest.raises(TypeError):  # a unit's return with anything else in it is refused
        LR.job_return(fx.context(units), "c", [{"unit": "u", "sha256": "0" * 64, "guards": {}, "skipped": False, "harm": 1.5}], 1, False)
    # timings by kind are returned for a calibration batch alone
    ctx = fx.context(units, mode="rehearsal")
    ctx.tick("search", 2.5, 320)
    assert LR.job_return(ctx, "c", [], 0, False)["timings"] == {"search": 2.5, "search_count": 320.0}
    # every log line holds permitted fields only
    for rec in logged:
        assert set(rec) <= set(LR.LOG_FIELDS)
    # the log refuses anything else
    for bad in ({"harm": 1.5}, {"event": "x", "seconds": 2.0}, {"sha256": "abc"}, {"count": 1.5}, {"unit": 3}):
        with pytest.raises(TypeError):
            LR.log_record(**bad)
    # no bare print in the lead modules
    for module in ("lead_run", "lead_launch", "lead_ledger", "modal_lead"):
        src = Path(LR.__file__).with_name(module + ".py").read_text()
        assert not re.search(r"(?<![\w.])print\(", src), module


# ----------------------------------------------------------------------------- T16: the delta-on arm


def test_T16_delta_on_holds_the_delta_entries_at_1(tmp_path):
    fx2 = Fixture(tmp_path, arm="delta_on")
    units = tmp_path / "units"
    LR.attack_job(fx2.model, fx2.context(units), "A1", fx2.ids["A1"], fx2.rows["A1"], fx2.starts)
    LR.heldout_job(fx2.model, fx2.context(units), "H1", fx2.ids["H1"], fx2.rows["H1"], fx2.starts, ["A1"], fx2.strata)
    dpos = LR.delta_positions(fx2.lay)
    for batch in ("A1", "H1"):
        for s in (9, 10):
            with np.load(LR.search_file(units, batch, s), allow_pickle=False) as z:
                assert (z["settings"][:, dpos] == 1.0).all()  # every saved setting has its 24 delta entries at 1
                assert LR.unit_meta(LR.search_file(units, batch, s))["delta_held"] is True
                # the starting harm is that of the start with the delta entries at 1
                prep = A.prepare(fx2.model, fx2.ids[batch], "fp32", device=DEV)
                held = LR.flat_start(fx2.starts[s], fx2.lay, True)
                assert z["init"][0] == A.score(fx2.model, P.unflatten(held, fx2.lay), prep, device=DEV) == z["record"][0]
                assert z["init"][0] != A.score(fx2.model, P.unflatten(LR.flat_start(fx2.starts[s], fx2.lay, False), fx2.lay), prep, device=DEV)
    res = LR.assemble(units, tmp_path / "t", "delta_on", ["A1"], ["H1"], [9, 10], text_ids_H=[[f"t{k}" for k in range(N_TEXTS)]], excluded=[],
                      inputs_sha256={}, containers=[], expect_commit=COMMIT, lead_prep_fp={"attack": {"A1": "other"}, "heldout": {"H1": "x"}})
    table = LT.load_table(tmp_path / "t")
    assert [str(x) for x in table["setting_names"]] == list(LT.SETTINGS_DELTA_ON)
    assert res["prep_fp_equal_to_lead"] == {"attack": {"A1": False}, "heldout": {"H1": False}}  # recorded, not stopping the run
    # shuffled copies leave the delta entries at 1
    for s in (9, 10):
        with np.load(LR.search_file(units, "A1", s), allow_pickle=False) as z:
            flat = z["settings"][0]
        for r in range(1, 9):
            copy = P.shuffle_source(flat, fx2.lay, fx2.strata, ("delta_on", "A1", s, "n20", r), label=LR.SHUFFLE_LABEL)
            assert (copy[dpos] == 1.0).all()


# ----------------------------------------------------------------------------- the guards, one by one


def _no_value(msg: str) -> bool:
    return re.search(r"\d+\.\d+", msg) is None


def test_G1_a_heldout_container_refuses_an_attack_pool_or_other_ids(fx, tmp_path):
    ctx = fx.context(tmp_path / "u")
    with pytest.raises(LR.GuardFailure) as e:
        LR.guard_batch(ctx, "heldout", "A1", fx.ids["A1"], fx.rows["A1"])  # an attack pool's name on the held-out side
    assert e.value.guard == "G1" and _no_value(str(e.value))
    with pytest.raises(LR.GuardFailure):
        LR.guard_batch(ctx, "heldout", "H1", fx.ids["A1"], fx.rows["H1"])  # ids that are not the batch's
    with pytest.raises(LR.GuardFailure):
        LR.guard_batch(ctx, "attack", "C1", fx.ids["C1"], fx.rows["C1"])  # a calibration batch outside the rehearsal
    LR.guard_batch(ctx, "heldout", "H1", fx.ids["H1"], fx.rows["H1"])
    ctx.mode = "rehearsal"
    LR.guard_batch(ctx, "heldout", "C1", fx.ids["C1"], fx.rows["C1"], allow_pool="C1")  # the rehearsal's override, for one named batch
    with pytest.raises(LR.GuardFailure):
        LR.guard_batch(ctx, "heldout", "C2", fx.ids["C1"], fx.rows["C1"], allow_pool="C1")
    ctx.mode = "deciding"
    with pytest.raises(LR.GuardFailure):  # never in a deciding container
        LR.guard_batch(ctx, "heldout", "C1", fx.ids["C1"], fx.rows["C1"], allow_pool="C1")


def test_G2_a_heldout_job_receives_no_attack_ids(fx):
    import inspect

    params = inspect.signature(LR.heldout_job).parameters
    assert "attack_batches" in params and not any("ids" in p and p != "ids" for p in params)
    assert list(params)[:5] == ["model", "ctx", "batch", "ids", "expected_rows"]  # one batch's ids: its own


def test_G4_and_G5_fail_on_a_wrong_setting_or_a_wrong_axis(fx, tmp_path):
    prep = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
    # G4: a setting saved under the wrong step's name does not re-score to the record at that step
    real = A.run

    def wrong_step(model, p, start, n_steps, step_size, *, save_hook, **kw):
        out = real(model, p, start, n_steps, step_size, save_hook=save_hook, **kw)
        save_hook.saved["step_20"] = save_hook.saved["step_19"]
        return out

    with pytest.raises(LR.GuardFailure) as e:
        LR.search_unit(fx.model, prep, fx.context(tmp_path / "a", run=wrong_step), "attack", "A1", 9, fx.starts[9], "ids", "fp")
    assert e.value.guard == "G4" and _no_value(str(e.value))
    # G5: per-position sums along the wrong axis
    with pytest.raises(LR.GuardFailure) as e:
        LR._g5(0.5, np.array([0.5] * 8 + [0.9] * 8), "unit")
    assert e.value.guard == "G5"
    LR._g5(0.7, np.array([0.5] * 8 + [0.9] * 8), "unit")


def test_G6_and_G11_the_assembler_refuses_a_setting_scored_on_its_own_batch(fx, small_arm, tmp_path):
    """G6: a table in which a carried cell is the attack search's own-batch value. G11: a block that scored the held-out
    batch's own setting in place of the attack setting; each of its two halves is made to fail alone, the hash of the
    setting as scored, and the per-text values equal to the held-out batch's own."""
    import shutil

    for guard, source, forge_hash in (("G6", "A1", False), ("G11_setting_is_the_attack_searchs", "H1", True),
                                      ("G11_differs_from_the_heldout_batchs_own", "H1", False)):
        units = tmp_path / guard
        shutil.copytree(small_arm["units"], units)
        block = LR.block_file(units, "H1", "A1", 9)
        with np.load(block, allow_pickle=False) as z:
            arrays = {k: z[k] for k in z.files}
        with np.load(LR.search_file(units, source, 9), allow_pickle=False) as z:
            own_text, own_setting = z["own_text"], z["settings"]
            hook_names, scored = [str(x) for x in z["hook_names"]], [str(x) for x in z["scored_names"]]
        for k, name in enumerate(str(x) for x in arrays["names"]):
            arrays["carried_text"][k] = own_text[scored.index(name)]
            if forge_hash:
                arrays["scored_sha"][k] = hashlib.sha256(b"".join(P.unflatten(own_setting[hook_names.index(LR.SAVED[name])], fx.lay)[m].tobytes()
                                                                   for m, _ in fx.lay)).hexdigest()
        LR.write_unit(block, arrays)
        with pytest.raises(LR.GuardFailure) as e:
            LR.assemble(units, tmp_path / guard / "t", "lead", ["A1", "A2"], ["H1", "H2"], [9, 10],
                        text_ids_H=[[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)], excluded=[], inputs_sha256={}, containers=[], expect_commit=COMMIT)
        assert e.value.guard == guard and _no_value(str(e.value))


def test_G7_a_record_alternating_across_a_level(fx, tmp_path):
    """The hook and the crossing rule must agree and be missing together; a hook that recorded another step fails."""
    real = A.run

    def other_step(model, p, start, n_steps, step_size, *, save_hook, **kw):
        out = real(model, p, start, n_steps, step_size, save_hook=save_hook, **kw)
        key = next((k for k in save_hook.events if k.startswith("two_step")), None)
        if key is None:  # the tiny search reaches no level: pretend it did
            save_hook.events["two_step_mean_reaches_2"] = 3
            save_hook.saved["two_step_mean_reaches_2"] = save_hook.saved["step_19"]
        else:
            save_hook.events[key] += 1
        return out

    prep = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
    with pytest.raises(LR.GuardFailure) as e:
        LR.search_unit(fx.model, prep, fx.context(tmp_path / "u", run=other_step), "attack", "A1", 9, fx.starts[9], "ids", "fp")
    assert e.value.guard == "G7" and _no_value(str(e.value))
    rec = [0.2, 3.9, 0.5, 3.9, 0.5] + [0.6] * 20  # alternation across the 2-nat level
    hook = A.SaveHook(steps=(), thresholds=(2.0,))
    for k in range(len(rec)):
        hook(k, rec[: k + 1], {"m": torch.zeros((1, 1, 2))})
    assert hook.events["two_step_mean_reaches_2"] == P.crossing(rec, 2.0)["k"] == 1


def test_G8_a_setting_constant_within_every_stratum(fx):
    strata = {k: np.array([v % 3 for v in range(C)]) for k, C in fx.lay}
    flat = np.concatenate([np.array([0.1 * (v % 3) for v in range(C)] + [0.5], dtype=np.float32) for _, C in fx.lay])
    copies = [P.shuffle_source(flat, fx.lay, strata, ("lead", "A1", 9, "n20", r), label=LR.SHUFFLE_LABEL) for r in range(1, 9)]
    for copy in copies:
        assert LR.check_shuffle(flat, copy, fx.lay, strata)  # the two asserted parts hold
        assert np.array_equal(copy, flat)  # the third part would fail: recorded as a count, not asserted
    broken = copies[0].copy()
    broken[0], broken[1] = broken[1] + 0.05, broken[0]
    assert not LR.check_shuffle(flat, broken, fx.lay, strata)
    moved_delta = copies[0].copy()
    moved_delta[LR.delta_positions(fx.lay)[0]] = 0.9
    assert not LR.check_shuffle(flat, moved_delta, fx.lay, strata)


def test_G9_and_G10_files_are_whole_and_the_attack_file_is_the_one_written(fx, small_arm, tmp_path):
    import shutil

    units = tmp_path / "units"
    shutil.copytree(small_arm["units"], units)
    src = LR.search_file(units, "A1", 9)
    data = src.read_bytes()
    src.write_bytes(data[: len(data) // 2])  # truncated
    assert not LR.finished(src)
    prep = A.prepare(fx.model, fx.ids["H1"], "fp32", device=DEV)
    block = LR.block_file(units, "H1", "A1", 9)
    block.unlink()
    LR.marker(block).unlink()
    with pytest.raises(LR.GuardFailure) as e:
        LR.scoring_block(fx.model, prep, fx.context(units), "H1", "A1", 9, fx.strata, "ids", "fp")
    assert e.value.guard == "G10" and _no_value(str(e.value))
    # the restart of A1's container removes its truncated file with its marker, its temporary file, and its marker
    # without a file; and leaves alone what other containers, writing to the same folder, have there
    (units / "search_A1_s10.npz.tmp").write_bytes(b"x")
    (units / "search_A1_s77.npz.done").write_text("0" * 64)
    (units / "block_H2_A1_s9.npz.tmp").write_bytes(b"another container's file, half written")
    (units / "search_A2_s10.npz.tmp").write_bytes(b"and another's")
    before = {p.name for p in units.iterdir()}
    removed = LR.clean_unfinished(units, "A1")
    assert removed == 4 and not src.exists() and not LR.marker(src).exists()
    assert before - {p.name for p in units.iterdir()} == {"search_A1_s9.npz", "search_A1_s9.npz.done", "search_A1_s10.npz.tmp", "search_A1_s77.npz.done"}
    assert LR.finished(LR.search_file(units, "A1", 10)) and (units / "block_H2_A1_s9.npz.tmp").exists()
    assert LR.clean_unfinished(units, "H2") == 1 and not (units / "block_H2_A1_s9.npz.tmp").exists()
    assert LR.own_unit("block_H1_A1_s9.npz", "H1") and not LR.own_unit("block_H1_A1_s9.npz", "A1") and not LR.own_unit("search_A10_s9.npz", "A1")


def test_one_commit_the_assembler_refuses_units_of_two_commits(fx, small_arm, tmp_path):
    import shutil

    units = tmp_path / "units"
    shutil.copytree(small_arm["units"], units)
    path = LR.search_file(units, "H2", 10)  # a held-out search: rewriting an attack search's file would trip G10 first
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    meta = LR.unit_meta(path)
    meta["commit"] = "e" * 40
    arrays["meta"] = np.array(json.dumps(meta, sort_keys=True))
    LR.write_unit(path, arrays)
    with pytest.raises(LR.GuardFailure) as e:
        LR.assemble(units, tmp_path / "t", "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], text_ids_H=[[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)],
                    excluded=[], inputs_sha256={}, containers=[], expect_commit=COMMIT)
    assert e.value.guard == "one_commit"


def test_parts_and_the_per_text_check_through_the_assembler(fx, small_arm, tmp_path):
    """Plan 2 of the research log, Section 6, "Parts": the loader refuses parts joined in the wrong order, and validate refuses a per-text
    array whose mean disagrees with its core value. Both are plan 1 of the research log's checks; here they are reached from an assembled table."""
    import shutil

    from vpd_audit_2.manifest import deterministic_npz

    folder = tmp_path / "t"
    table = small_arm["table"]
    LT.save_table(table, folder, part_bytes=1_000)  # the arrays with no attack axis in a part of their own, then one attack batch per part
    meta = LT.read_meta(folder / "table_core.npz")
    assert [p["attack_names"] for p in meta["per_text_files"]] == [[], ["A1"], ["A2"]]
    LT.validate(LT.load_table(folder))
    with np.load(folder / "table_core.npz") as z:
        core = {k: z[k] for k in z.files}
    meta["per_text_files"] = meta["per_text_files"][::-1]  # the parts listed in the wrong order
    core["meta"] = np.array(json.dumps(meta, sort_keys=True))
    (folder / "table_core.npz").write_bytes(deterministic_npz(core))
    with pytest.raises(LT.TableCheckError, match="^per_text_parts_in_attack_order$"):
        LT.load_table(folder)
    bad = dict(table)
    bad["carried_text"] = table["carried_text"] * np.float32(1.001)
    with pytest.raises(LT.TableCheckError, match="^per_text_matches_core$"):
        LT.validate(bad)


def test_configuration_is_asserted_in_a_deciding_container(fx, tmp_path):
    good = {"gpu": "NVIDIA B200", "deterministic_algorithms": True, "deterministic_warn_only": False, "allow_tf32_matmul": False,
            "allow_tf32_cudnn": False, "cublas_workspace_config": ":4096:8", "vpd_audit_2_commit": COMMIT, "vpd_audit_2_dirty": "0"}
    ctx = LR.Context(arm="lead", units=tmp_path, commit=COMMIT, lay=fx.lay, precision="bf16", device="cuda", mode="deciding", environment=good)
    LR.check_configuration(ctx, LR.STARTS)
    for change in ({"gpu": "NVIDIA A100-80GB"}, {"deterministic_warn_only": True}, {"allow_tf32_matmul": True}, {"vpd_audit_2_dirty": "1"},
                   {"vpd_audit_2_commit": "0" * 40}, {"cublas_workspace_config": None}):
        bad = LR.Context(arm="lead", units=tmp_path, commit=COMMIT, lay=fx.lay, precision="bf16", device="cuda", mode="deciding", environment={**good, **change})
        with pytest.raises(LR.GuardFailure, match="configuration"):
            LR.check_configuration(bad, LR.STARTS)
    for starts in ((9, 10, 11, 12), (9, 10, 11, 12, 14), (1,)):  # starts are 9 to 13, hard-coded; the run refuses any other
        with pytest.raises(LR.GuardFailure, match="configuration"):
            LR.check_configuration(ctx, starts)
    rehearsal = LR.Context(arm="rehearsal", units=tmp_path, commit=COMMIT, lay=fx.lay, precision="bf16", device="cuda", mode="rehearsal", environment=good)
    LR.check_configuration(rehearsal, (1,))  # the rehearsal alone uses pilot start 1
    assert LR.STARTS == (9, 10, 11, 12, 13)


def test_rehearsal_mode_records_the_wrong_batch_refusals_and_still_writes_the_table(tmp_path):
    """Plan 2 of the research log, Section 7: one calibration batch on both sides. G6 must report every carried vector equal to the own-batch
    one, the ids check must fail, and the table is written all the same."""
    fx2 = Fixture(tmp_path, arm="rehearsal", starts=(1,))
    units_a, units_h = tmp_path / "attack_units", tmp_path / "heldout_units"
    LR.attack_job(fx2.model, fx2.context(units_a), "C1", fx2.ids["C1"], fx2.rows["C1"], fx2.starts, allow_pool="C1")
    LR.heldout_job(fx2.model, fx2.context(units_h, attack_units=units_a), "C1", fx2.ids["C1"], fx2.rows["C1"], fx2.starts, ["C1"],
                   fx2.strata, allow_pool="C1")
    same = LR.compare_search_units(LR.search_file(units_a, "C1", 1), LR.search_file(units_h, "C1", 1))
    assert same == {"record_equal": True, "saved_settings_equal": True, "prep_fp_equal": True}
    res = LR.assemble(units_a, tmp_path / "t", "rehearsal", ["C1"], ["C1"], [1], text_ids_H=[[f"t{k}" for k in range(N_TEXTS)]], excluded=[],
                      inputs_sha256={}, containers=[], expect_commit=COMMIT, rehearsal=True, heldout_units=units_h)
    o = res["outcomes"]
    assert o["G6"] is False and o["G6_reports_every_carried_vector_equal"] is True
    assert o["G11_differs_from_the_heldout_batchs_own"] is False and o["G11_reports_every_carried_vector_equal_to_the_heldout_own"] is True
    assert o["G10"] and o["G11_setting_is_the_attack_searchs"] and o["one_commit"]
    assert "heldout_ids_differ_from_attack_ids" in o["table_checks_failed"] and "axis_labels" in o["table_checks_failed"]
    assert (tmp_path / "t" / "table_core.npz").is_file()  # written for the copy test
    with pytest.raises(LR.GuardFailure):  # the same units are refused outside rehearsal mode
        LR.assemble(units_a, tmp_path / "t2", "rehearsal", ["C1"], ["C1"], [1], text_ids_H=[[f"t{k}" for k in range(N_TEXTS)]], excluded=[],
                    inputs_sha256={}, containers=[], expect_commit=COMMIT, rehearsal=False, heldout_units=units_h)


def test_the_spend_stop_is_obeyed_between_units_and_a_relaunch_finishes_the_rest(fx, small_arm, tmp_path):
    """Check C2's stop (the table specification's Section 9.2): a container asked to stop finishes what it is on, returns `stopped`, and
    leaves whole files; a later launch skips them, does the rest, and the table's bytes are those of an unbroken run."""
    import shutil

    # an attack container asked to stop before its first search does none
    none = LR.attack_job(fx.model, fx.context(tmp_path / "a", should_stop=lambda: True), "A1", fx.ids["A1"], fx.rows["A1"], fx.starts)
    assert (none["units"], none["finished_units"], none["expected_units"], none["stopped"]) == ([], 0, 2, True)
    assert not list((tmp_path / "a").glob("search_*"))

    units = tmp_path / "units"
    shutil.copytree(small_arm["units"], units)
    for p in list(units.iterdir()):  # H1's container has its two searches and none of its four blocks
        if p.name.startswith("block_H1_"):
            p.unlink()
    asked = {"n": 0}

    def stop_after_the_first_attack_batch() -> bool:
        asked["n"] += 1  # asked before each search (2), then once per attack batch
        return asked["n"] >= 4

    part = LR.heldout_job(fx.model, fx.context(units, should_stop=stop_after_the_first_attack_batch), "H1", fx.ids["H1"], fx.rows["H1"], fx.starts,
                          ["A1", "A2"], fx.strata)
    assert (part["finished_units"], part["expected_units"], part["stopped"]) == (4, 6, True)
    assert [u["unit"] for u in part["units"]] == ["search|lead|H1|s9", "search|lead|H1|s10", "block|lead|H1|A1|s9", "block|lead|H1|A1|s10"]
    assert [u["skipped"] for u in part["units"]] == [True, True, False, False]
    assert sorted(p.name for p in units.iterdir() if p.name.startswith("block_H1_")) == [
        "block_H1_A1_s10.npz", "block_H1_A1_s10.npz.done", "block_H1_A1_s9.npz", "block_H1_A1_s9.npz.done"]  # whole files, and A2's not begun
    with pytest.raises(LR.GuardFailure) as e:  # a stopped arm is not assembled
        LR.assemble(units, tmp_path / "early", "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], text_ids_H=[[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)],
                    excluded=[{"pool": "H2", "index": 3}], inputs_sha256={"manifest": "x"}, containers=[], expect_commit=COMMIT)
    assert e.value.guard == "units_complete"
    rest = LR.heldout_job(fx.model, fx.context(units), "H1", fx.ids["H1"], fx.rows["H1"], fx.starts, ["A1", "A2"], fx.strata)
    assert (rest["finished_units"], rest["expected_units"], rest["stopped"]) == (6, 6, False)
    assert [u["skipped"] for u in rest["units"]] == [True, True, True, True, False, False]
    res = LR.assemble(units, tmp_path / "t", "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], text_ids_H=[[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)],
                      excluded=[{"pool": "H2", "index": 3}], inputs_sha256={"manifest": "x"}, containers=[], expect_commit=COMMIT)
    assert res["files"] == small_arm["assembled"]["files"]  # identical table bytes


def test_a_failure_crosses_from_a_container_to_the_launcher_with_its_name_and_no_value():
    """A guard's failure and any other error in a container reach the launcher through pickling: the same class, the
    guard or the error's kind, the unit or the container, and a message with no value in it."""
    import pickle

    g = pickle.loads(pickle.dumps(LR.GuardFailure("G4", "search|lead|A1|s9")))
    assert type(g) is LR.GuardFailure and (g.guard, g.unit) == ("G4", "search|lead|A1|s9") and str(g) == "guard G4 failed in unit search|lead|A1|s9"
    c = pickle.loads(pickle.dumps(LR.ContainerFailure("ValueError at lead_run.search_unit line 400", "lead|attack|A1")))
    assert type(c) is LR.ContainerFailure and (c.kind, c.container) == ("ValueError at lead_run.search_unit line 400", "lead|attack|A1")
    assert str(c) == "ValueError at lead_run.search_unit line 400 in container lead|attack|A1" and _no_value(str(c)) and _no_value(str(g))


# ----------------------------------------------------------------------------- plan 4 of the research log: what the reviews added

TEXT_IDS = [[f"t{j}_{k}" for k in range(N_TEXTS)] for j in range(2)]


def _assemble(units: Path, out: Path, **kw) -> dict:
    return LR.assemble(units, out, "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], text_ids_H=TEXT_IDS, excluded=[{"pool": "H2", "index": 3}],
                       inputs_sha256={"manifest": "x"}, containers=[], expect_commit=COMMIT, **kw)


def _rewrite(path: Path, edit) -> None:
    """Rewrite a unit file with its arrays or metadata changed, marker and all."""
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    meta = LR.unit_meta(path)
    edit(arrays, meta)
    arrays["meta"] = np.array(json.dumps(meta, sort_keys=True))
    LR.write_unit(path, arrays)


def test_the_guards_only_pass_is_the_assemblers_reading_of_one_heldout_batch(fx, small_arm, tmp_path):
    """Plan 4 of the research log, Section 4.3: the assembler's cross-unit guards on one held-out batch's blocks against every attack search,
    as true or false and nothing else. It needs no other held-out batch's units, and it writes nothing."""
    import shutil

    names = set(LR.REQUIRED_GUARDS + LR.WRONG_BATCH_GUARDS)
    assert names == {"G6", "G10", "G11_setting_is_the_attack_searchs", "G11_differs_from_the_heldout_batchs_own", "shuffles_the_same_in_every_container",
                     "one_commit", "block_prep_fp_is_the_heldout_batchs"}
    units = tmp_path / "wave_1"
    shutil.copytree(small_arm["units"], units)
    for p in list(units.iterdir()):  # wave 1: H2's container has not run
        if p.name.startswith(("block_H2_", "search_H2_")):
            p.unlink()
    before = sorted(p.name for p in units.iterdir())
    out = LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H1"], [9, 10], expect_commit=COMMIT)
    assert set(out) == names and all(v is True for v in out.values())
    assert sorted(p.name for p in units.iterdir()) == before and not floats_in(out)
    with pytest.raises(LR.GuardFailure) as e:  # with H2 named, its missing units stop the pass by name
        LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H1", "H2"], [9, 10], expect_commit=COMMIT)
    assert e.value.guard == "units_complete" and e.value.unit == "guards|lead"
    assert LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H1"], [9, 10], expect_commit="e" * 40)["one_commit"] is False
    # a guard found false is returned as false, by name: here H1's own per-text values in one carried cell (the half of G11 that compares vectors)
    with np.load(LR.search_file(units, "H1", 9), allow_pickle=False) as z:
        own_text, scored = z["own_text"], [str(x) for x in z["scored_names"]]

    def as_own(arrays, meta):
        for k, name in enumerate(str(x) for x in arrays["names"]):
            arrays["carried_text"][k] = own_text[scored.index(name)]

    _rewrite(LR.block_file(units, "H1", "A1", 9), as_own)
    bad = LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H1"], [9, 10], expect_commit=COMMIT)
    assert bad["G11_differs_from_the_heldout_batchs_own"] is False and bad["G6"] is True and bad["G10"] is True
    # a rehearsal's pass says also whether every carried vector was equal, which with one batch on both sides it must be
    assert "G6_reports_every_carried_vector_equal" not in bad
    reh = LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H1"], [9, 10], expect_commit=COMMIT, rehearsal=True)
    assert reh["G6_reports_every_carried_vector_equal"] is False and reh["G11_reports_every_carried_vector_equal_to_the_heldout_own"] is False


def floats_in(x) -> bool:
    if isinstance(x, dict):
        return any(floats_in(v) for v in x.values())
    if isinstance(x, (list, tuple)):
        return any(floats_in(v) for v in x)
    return isinstance(x, (float, np.floating))


def test_a_blocks_labels_and_targets_are_its_heldout_batchs(fx, small_arm, tmp_path):
    """Plan 4 of the research log, Section 4.5 (the plan's review, Section 7): the assembler compares each block's fingerprint of labels and
    targets with its held-out batch's, so that the denominator and the carried cell are checked to rest on one tensor."""
    import shutil

    units = tmp_path / "units"
    shutil.copytree(small_arm["units"], units)
    assert small_arm["assembled"]["outcomes"]["block_prep_fp_is_the_heldout_batchs"] is True
    _rewrite(LR.block_file(units, "H2", "A1", 10), lambda arrays, meta: meta.update(prep_fp="0" * 64))
    with pytest.raises(LR.GuardFailure) as e:
        _assemble(units, tmp_path / "t")
    assert e.value.guard == "block_prep_fp_is_the_heldout_batchs" and _no_value(str(e.value))
    assert LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H2"], [9, 10], expect_commit=COMMIT)["block_prep_fp_is_the_heldout_batchs"] is False
    assert LR.cross_unit_guards(units, "lead", ["A1", "A2"], ["H1"], [9, 10], expect_commit=COMMIT)["block_prep_fp_is_the_heldout_batchs"] is True


def test_every_unit_file_is_the_one_its_container_returned(fx, small_arm, tmp_path):
    """Plan 4 of the research log, Section 6, row 2: the assembler checks each unit file's marker against the hash its container returned,
    so that a file another container deleted or rewrote after the return is seen."""
    import shutil

    returned = {"attack": {u["unit"]: u["sha256"] for job in small_arm["attack"].values() for u in job["units"]},
                "heldout": {u["unit"]: u["sha256"] for job in small_arm["heldout"].values() for u in job["units"]}}
    assert len(returned["attack"]) == 4 and len(returned["heldout"]) == 4 + 8
    res = _assemble(small_arm["units"], tmp_path / "t", returned_sha256=returned)
    assert res["outcomes"]["units_are_the_ones_their_containers_returned"] is True and res["files"] == small_arm["assembled"]["files"]
    assert "units_are_the_ones_their_containers_returned" not in small_arm["assembled"]["outcomes"]  # without the hashes there is nothing to compare
    units = tmp_path / "units"
    shutil.copytree(small_arm["units"], units)
    _rewrite(LR.block_file(units, "H1", "A2", 10), lambda arrays, meta: meta.update(note="rewritten after its container returned"))
    with pytest.raises(LR.GuardFailure) as e:
        _assemble(units, tmp_path / "u", returned_sha256=returned)
    assert e.value.guard == "units_are_the_ones_their_containers_returned"
    with pytest.raises(LR.GuardFailure):  # a unit its container never returned
        _assemble(small_arm["units"], tmp_path / "v", returned_sha256={"attack": returned["attack"], "heldout": {k: v for k, v in returned["heldout"].items() if "A2|s10" not in k}})
    with pytest.raises(LR.GuardFailure, match="configuration"):  # the small part size is a rehearsal's alone
        _assemble(small_arm["units"], tmp_path / "w", part_bytes=1_000)


def test_a_search_is_timed_by_part_and_the_timing_hook_saves_what_the_plain_hook_saves(fx, tmp_path, monkeypatch):
    """Plan 4 of the research log, Section 4.1: the end of preparation and the first search step are timed under their own names. The hook
    that notes the clock saves exactly what the plain hook saves, and the search with it is bit-identical."""
    prep = A.prepare(fx.model, fx.ids["A1"], "fp32", device=DEV)
    plain, timed = A.SaveHook(steps=(10, 20), thresholds=(0.5, 2.0)), LR.TimedHook(steps=(10, 20), thresholds=(0.5, 2.0))
    a = A.run(fx.model, prep, fx.starts[9], 20, 0.1, save_hook=plain, cum_grads=True, record_sources=True, device=DEV)
    b = A.run(fx.model, prep, fx.starts[9], 20, 0.1, save_hook=timed, cum_grads=True, record_sources=True, device=DEV)
    assert a["record"] == b["record"] and np.array_equal(a["source_record"].view(np.uint32), b["source_record"].view(np.uint32))
    assert plain.events == timed.events and sorted(plain.saved) == sorted(timed.saved)
    for name in plain.saved:
        assert np.array_equal(plain.saved[name].view(np.uint32), timed.saved[name].view(np.uint32))
        assert all(np.array_equal(x.view(np.uint32), y.view(np.uint32)) for x, y in zip(plain.cum[name], timed.cum[name]))
    assert len(timed.at) == 21 and timed.at == sorted(timed.at)  # once per iteration, and once after the last harm

    # a rehearsal's container returns its seconds by kind; the tiny model runs on a CPU, so the hardware check is set aside
    monkeypatch.setattr(LR, "check_configuration", lambda ctx, starts: None)
    fx1 = Fixture(tmp_path, arm="rehearsal", starts=(1,))
    units_a, units_h = tmp_path / "a", tmp_path / "h"
    first = LR.attack_job(fx1.model, fx1.context(units_a, mode="rehearsal"), "C1", fx1.ids["C1"], fx1.rows["C1"], fx1.starts, allow_pool="C1")
    t = first["timings"]
    assert first["removed_unfinished"] == 0 and t["to_ready_count"] == 1.0 and 0 < t["to_ready"] <= first["seconds"]
    parts = ("search_iteration_0", "search_iterations_warm", "search_iterations_after_warm", "search_final_harm", "search_tail")
    assert [t[p + "_count"] for p in parts] == [1.0, 9.0, 310.0, 1.0, 1.0] and t["search_count"] == 320.0
    assert sum(t[p] for p in parts) == pytest.approx(t["search"], rel=1e-9)
    assert t["wrapper_check_count"] == t["scoring_count"] == t["scoring_in_search_units_count"]  # one pass of the authors' function per re-score
    assert t["volume_commit_after_search_count"] == 1.0 and "volume_commit_nothing_new" not in t and "volume_commit_after_blocks" not in t
    again = LR.attack_job(fx1.model, fx1.context(units_a, mode="rehearsal"), "C1", fx1.ids["C1"], fx1.rows["C1"], fx1.starts, allow_pool="C1")
    assert again["units"][0]["skipped"] and "search" not in again["timings"] and again["timings"]["to_ready_count"] == 1.0
    assert again["timings"]["volume_commit_nothing_new_count"] == 1.0 and "volume_commit_after_search" not in again["timings"]
    held = LR.heldout_job(fx1.model, fx1.context(units_h, mode="rehearsal", attack_units=units_a), "C1", fx1.ids["C1"], fx1.rows["C1"], fx1.starts, ["C1"],
                          fx1.strata, allow_pool="C1")
    assert held["timings"]["volume_commit_after_search_count"] == 1.0 and held["timings"]["volume_commit_after_blocks_count"] == 1.0
    # a restarted container says how many unfinished files of its own it deleted, and leaves another container's alone
    block = LR.block_file(units_h, "C1", "C1", 1)
    LR.marker(block).unlink()  # renamed, and killed before its marker
    (units_h / "block_C2_C2_s1.npz").write_bytes(b"another container's file, not yet marked")
    back = LR.heldout_job(fx1.model, fx1.context(units_h, mode="rehearsal", attack_units=units_a), "C1", fx1.ids["C1"], fx1.rows["C1"], fx1.starts, ["C1"],
                          fx1.strata, allow_pool="C1")
    assert back["removed_unfinished"] == 1 and [u["skipped"] for u in back["units"]] == [True, False] and back["units"][0]["guards"] == {"G3": True}
    assert (units_h / "block_C2_C2_s1.npz").read_bytes() == b"another container's file, not yet marked"
    # the ledger's timings come from such returns: every kind it needs is there
    delta = Fixture(tmp_path / "d", arm="rehearsal_delta_on", starts=(1,))
    d = LR.attack_job(delta.model, delta.context(tmp_path / "d" / "u", mode="rehearsal", n_steps=20), "C1", delta.ids["C1"], delta.rows["C1"], delta.starts, allow_pool="C1")
    assert [d["timings"][p + "_count"] for p in parts] == [1.0, 9.0, 10.0, 1.0, 1.0]
    from vpd_audit_2 import lead_ledger as LG

    timings = LG.timings_from_rehearsal([{"arm": "rehearsal", "timings": x["timings"]} for x in (first, again, held, back)] + [{"arm": "rehearsal_delta_on", "timings": d["timings"]}])
    assert set(LG.TIMING_KEYS) <= set(timings) and all(timings[k] >= 0 for k in LG.TIMING_KEYS)
    assert len(timings["observations"]["seconds_to_ready"]) == 5 and len(timings["observations"]["seconds_first_search_extra"]) == 3


def test_a_deciding_spec_carries_nothing_that_only_a_rehearsal_may():
    deciding = {"arm": "lead", "side": "heldout", "batch": "H1", "commit": COMMIT, "mode": "deciding", "root": "/x", "units": "units", "run": "run",
                "attack_batches": ["A1"]}
    LR.check_spec(deciding, False)
    for key in LR.REHEARSAL_ONLY:
        with pytest.raises(LR.GuardFailure, match="configuration"):
            LR.check_spec({**deciding, key: "anything"}, False)
    for bad in ({**deciding, "units": "units_attack"}, {**deciding, "arm": "rehearsal"}, {**deciding, "mode": "test"}, {**deciding, "side": "both"}):
        with pytest.raises(LR.GuardFailure, match="configuration"):
            LR.check_spec(bad, False)
    with pytest.raises(LR.GuardFailure, match="configuration"):  # a trigger in a deciding container
        LR.check_spec(deciding, True)
    rehearsal = {**deciding, "arm": "rehearsal", "mode": "rehearsal", "units": "units_heldout", "attack_units": "units_attack", "allow_pool": "C1", "kill_at": "unit_renamed"}
    LR.check_spec(rehearsal, True)
    with pytest.raises(LR.GuardFailure, match="configuration"):  # a rehearsal never writes under a deciding arm's name
        LR.check_spec({**rehearsal, "arm": "lead"}, True)
