"""Session 6, plan 2: the spread over texts' statistics on tiny made-up arrays, with hand-computed answers. The module
is not run on real data until the head settles its open questions; its `main` refuses until then."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats as sps

from vpd_audit_2 import s6_spread as S


def test_the_share_above_the_benchmark_counts_only_harm_that_exceeds_it():
    assert S.share_above(np.array([0.5, 0.8, 0.75, 1.0])) == 0.5  # 0.75 itself does not exceed 0.75


def test_the_thirteenth_lowest_text():
    assert S.kth_lowest(np.arange(128.0)[::-1]) == 12.0
    assert S.kth_lowest(np.array([[5.0, 1.0, 3.0], [0.0, -1.0, 2.0]]), k=2).tolist() == [3.0, 0.0]


def test_the_top_share_clips_negative_added_harm_to_zero():
    added = np.array([3.0, 1.0, -2.0, 0.0, 2.0])  # clipped: 3, 1, 0, 0, 2; total 6; the top two carry 5
    assert S.top_share(added, n=2) == pytest.approx(5 / 6)
    assert np.isnan(S.top_share(np.array([-1.0, 0.0, -3.0]), n=2))  # no positive added harm: undefined
    assert S.top_share(np.full(128, 0.4)) == pytest.approx(13 / 128)  # an even spread: about 0.10


def test_the_median_over_the_mean_clips_both():
    assert S.median_over_mean(np.array([-2.0, 1.0, 3.0, 0.0])) == pytest.approx(0.5 / 1.0)  # clipped 0, 1, 3, 0
    assert np.isnan(S.median_over_mean(np.array([-2.0, 0.0])))


def test_the_share_negative():
    assert S.share_negative(np.array([-1.0, 0.0, 2.0, -0.5])) == 0.5


def test_the_summary_over_cells_drops_undefined_cells():
    s = S.summary(np.array([1.0, np.nan, 2.0, 3.0, 4.0, 5.0]))
    assert s["cells"] == 5 and s["median"] == 3.0 and s["p10"] == pytest.approx(1.4) and s["p90"] == pytest.approx(4.6)


def _table(KA: int = 3, KH: int = 2, ns: int = 2, R: int = 2, T: int = 128) -> dict:
    """Every carried cell's added harm is 1, 2, ..., 128 nats on texts 1 to 128; the own searches rank the texts the other
    way; the start's own harm ranks them the other way too; the shuffled copies add nothing. h10 is never reached by
    attack batch 0."""
    from vpd_audit_2 import lead_table as LT

    Q = len(LT.SETTINGS_LEAD)
    init = np.tile(np.linspace(0.4, 0.1, T), (KH, ns, 1))
    up = np.arange(1.0, T + 1.0)
    carried = np.broadcast_to(init[None, :, :, None, :] + up, (KA, KH, ns, Q, T)).copy()
    carried[0, :, :, LT.SETTINGS_LEAD.index("h10"), :] = np.nan
    own = np.broadcast_to(init[:, :, None, :] + up[::-1], (KH, ns, Q, T)).copy()
    shuf = np.broadcast_to(init[None, :, :, None, None, :], (KA, KH, ns, Q, R, T)).copy()
    return {"setting_names": np.array(LT.SETTINGS_LEAD), "has_shuffles": np.array([n not in LT.NO_SHUFFLES for n in LT.SETTINGS_LEAD]),
            "carried_text": carried.astype(np.float32), "init_H_text": init.astype(np.float32), "own_H_text": own.astype(np.float32),
            "shuf_text": shuf.astype(np.float32)}


def test_the_spread_on_a_made_up_table():
    out = S.spread(_table())
    c = out["n80"]["carried"]
    # every harm is above 1.1 and exceeds 0.75; added harm 1 to 128: the top 13 carry (116 + ... + 128) / (1 + ... + 128)
    assert c["share_above_benchmark"]["median"] == 1.0 and c["share_negative"]["median"] == 0.0
    assert c["top_13_share"]["median"] == pytest.approx(13 * (116 + 128) / 2 / (128 * 129 / 2))
    assert c["median_over_mean"]["median"] == pytest.approx(64.5 / 64.5) and c["share_above_benchmark"]["cells"] == 3 * 2 * 2
    # the 13th lowest harm: added 13 on the text whose start harm is linspace(0.4, 0.1, 128)[12]
    assert c["tenth_percentile_text"]["median"] == pytest.approx(13 + np.linspace(0.4, 0.1, 128)[12], abs=1e-5)
    sp = out["n80"]["spearman"]
    assert sp["another_attack_batch_same_start"]["mean"] == pytest.approx(1.0) and sp["same_attack_batch_another_start"]["mean"] == pytest.approx(1.0)
    assert sp["own_search"]["mean"] == pytest.approx(-1.0) and sp["start_own_harm"]["mean"] == pytest.approx(-1.0)
    assert out["n80"]["shuffled_copies"]["top_13_share"]["cells"] == 0  # the copies add nothing: undefined, left out
    assert out["h10"]["carried"]["share_above_benchmark"]["cells"] == 2 * 2 * 2  # attack batch 0 never reached it
    assert out["h10"]["spearman"]["another_attack_batch_same_start"]["cells"] == 2 * 2 * 2
    assert "n159" not in out and "n319" not in out  # the five lengths and three levels only
    assert sp["another_attack_batch_same_start"]["partners"] == {"min": 2, "max": 2, "mean": 2.0}  # 3 attack batches
    assert sp["same_attack_batch_another_start"]["partners"] == {"min": 1, "max": 1, "mean": 1.0}  # 2 starts
    assert out["h10"]["spearman"]["another_attack_batch_same_start"]["partners"]["max"] == 1  # attack batch 0 has no h10 setting
    overlap = {"texts": 11, "intervals_of_ratios": 3, "largest_move_ratios": 0.001, "intervals_of_means": 4, "largest_move_means_nats": 0.02}
    text = S.report(out, overlap)
    assert "the same attack batch, another start: 1.00 (1 partner per cell; 12 cells)" in text
    assert "another attack batch, same start: 1.00 (2 partners per cell; 12 cells)" in text and "the start's own harm: -1.00" in text
    assert "The 11 held-out texts whose spans overlap attack rows are kept" in text


def test_the_overlap_line_reads_the_lead_analysis_as_committed():
    """The lead analysis recomputed both tables without the 11 overlapping texts; its ratio intervals moved by at most
    0.0015 and its intervals in nats by at most 0.0183 (the 10-nat row's own-search margin)."""
    o = S.overlap_effect()
    assert o["texts"] == 11 == o["excluded_in_lead_analysis"]
    assert o["intervals_of_ratios"] == 102 and o["intervals_of_means"] == 120
    assert o["largest_move_ratios"] == pytest.approx(0.0015, abs=0.0001) and o["largest_move_means_nats"] == pytest.approx(0.0183, abs=0.0001)


def test_statistics_1_and_2_on_the_added_harm_when_asked(monkeypatch):
    harm = np.linspace(0.5, 1.5, 128)[None]
    monkeypatch.setattr(S, "STATS_1_2_ON", "added")
    f = S.four(harm, harm - 0.6)  # added harm from -0.1 to 0.9: above 0.75 only on the top part
    assert f["share_above_benchmark"][0] == pytest.approx(np.mean(harm - 0.6 > 0.75))
    monkeypatch.setattr(S, "STATS_1_2_ON", "harm")
    assert S.four(harm, harm - 0.6)["share_above_benchmark"][0] == pytest.approx(np.mean(harm > 0.75))


def test_a_cell_never_reached_is_undefined_in_every_statistic():
    harm = np.full((2, 128), 1.0)
    harm[1, :] = np.nan
    f = S.four(harm, harm - 0.2)
    assert all(np.isfinite(v[0]) and np.isnan(v[1]) for v in f.values())


def test_spearman_against_scipy_with_and_without_ties():
    rng = np.random.default_rng(3)
    for x, y in ((rng.random(128), rng.random(128)), (np.round(rng.random(128), 1), np.round(rng.random(128), 1))):
        assert S.spearman(x, y) == pytest.approx(sps.spearmanr(x, y).statistic, abs=1e-12)
    xs, ys = rng.random((4, 128)), rng.random((4, 128))
    assert np.allclose(S.spearman(xs, ys), [sps.spearmanr(a, b).statistic for a, b in zip(xs, ys)], atol=1e-12)
    assert np.isnan(S.spearman(np.ones(10), np.arange(10.0)))
    assert S.spearman(np.arange(10.0), np.arange(10.0) ** 3) == pytest.approx(1.0)


def test_it_refuses_to_run_while_the_open_questions_are_unsettled(monkeypatch):
    assert S.OPEN_QUESTIONS_SETTLED is True  # the head's answers, session 6
    monkeypatch.setattr(S, "OPEN_QUESTIONS_SETTLED", False)
    with pytest.raises(S.Refusal, match="not settled"):
        S.main()
    monkeypatch.setattr(S, "PARTNER_BATCHES", "the next one")
    with pytest.raises(S.Refusal, match="only every other partner"):
        S.spread(_table())
