"""The recorded runs' readings: first step above 5 nats, first relative difference above 1 percent, odd and even steps."""

from __future__ import annotations

from vpd_audit_2 import recorded as R


def test_readings():
    g1 = [(k + 1) / 10 for k in range(321)]
    a = list(g1)
    a[50] *= 1.02
    b = list(g1)
    out = R.readings({"a": a, "b": b}, g1)
    assert out["first_step_above_5_nats"]["G1 (authors' loop, whole batch, B200)"] == 50
    assert out["first_step_differing_from_G1_by_1pct"] == {"a": 50, "b": None}
    assert out["pairs"] == {"a vs b": 50}
    assert out["harm"]["a"]["19"] == g1[19] and out["harm"]["a"]["320"] == g1[320]
