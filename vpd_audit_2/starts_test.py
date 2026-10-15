"""Session 6, plan 1, Section 2.4: the starts test's reading, fixed before the data (`sessions/005/checkpoint.md`,
Appendix G).

The test searched the pilot's eight calibration batches, C1 to C8, from the run's five starts, 9 to 13: 40 searches of
320 steps, each scored on its own batch only; and C1 from start 1 once more, as a guard. Their records are in
`results/s6_starts/records.json` (written by `starts_run`). The pilot's 64 searches, C1 to C8 from starts 1 to 8, are
the `record` arrays of `results/s4_pilot/part_a/runs.json`, key `a1`.

    uv run python -m vpd_audit_2.starts_test                 (the reading; its output goes to results/s6_starts/reading.txt)
    uv run python -m vpd_audit_2.starts_test --pilot-only    (the pilot's 64 records alone, for checking this script)

A search's added harm at step k is `record[k] - record[0]`. Its final level is its mean harm over its last 20 steps,
`record[301]` to `record[320]` (checkpoint, Section 7). The reading prints, in this order, after the guard:

  1. The deciding statistic, the mean added harm after step 320 over the 40 test searches, with the reading fixed in
     Appendix G (at or above 31 nats, Starts; at or below 29, Something else; between, Undetermined) and the two
     reference values beside it: the pilot's 25.5 and the run's 34.5. Beside the pilot's 25.5, its exact value from
     `runs.json`, 25.4485, and one line saying the checkpoint's figure was rounded twice; the thresholds are untouched.
  2. Each start's mean added harm at 80, 160, and 320 steps over the eight batches.
  3. Each batch's mean at 80, 160, and 320 steps over starts 9 to 13, beside the pilot's over starts 1 to 8.
  4. The 8 by 13 tables of added harm at 80, 160, and 320 steps, the pilot's 64 searches joined with the test's 40, each
     with a two-way analysis of variance on batch and start (`pilot_a_tables.anova_two_way`, the pilot's own): the mean
     squares for batch, start, and residual, the variance components, and the start's share of variance, its component
     over the sum of the three.
  5. Description: each search's final level; the median, quartiles, and range over the 40; and how many are at or above
     40.2 nats, the paper's 320-step value, counted two ways, each labelled: by the harm after step 320 (as the
     checkpoint's Section 7 counted its 12.5 and 31 percent, the like-for-like comparison), and by the final level.
  6. Description: each search's breakout step, the first step k at which its two-step mean harm,
     (record[k - 1] + record[k]) / 2, reaches 5 nats (`pilot.crossing`, the harm-level table's rule), in a table by
     batch and start; and by start and by batch, the median breakout step (a search that never breaks out counted as
     later than any that does) and how many never break out within 320 steps.

`--pilot-only` prints the same items on the pilot's 64 searches, with no reading.

The guard comes first: the guard search's record must equal the pilot's C1 from start 1 bit for bit. If it does not,
the script prints that and stops, reading nothing else, and exits with status 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from vpd_audit_2 import env
from vpd_audit_2 import pilot as P
from vpd_audit_2.pilot_a_tables import anova_two_way

PILOT_RUNS = env.REPO_ROOT / "results" / "s4_pilot" / "part_a" / "runs.json"
RECORDS = env.REPO_ROOT / "results" / "s6_starts" / "records.json"
BATCHES = tuple(f"C{j}" for j in range(1, 9))
PILOT_STARTS = tuple(range(1, 9))
TEST_STARTS = tuple(range(9, 14))
GUARD = ("C1", 1)
N_STEPS = 320
STEPS = (80, 160, 320)
STARTS_AT = 31.0  # Appendix G: at or above, Starts
ELSE_AT = 29.0  # at or below, Something else; between, Undetermined
PILOT_REFERENCE = 25.5  # Appendix G: the pilot's mean added harm at 320 steps, C1 to C8 from starts 1 to 8
RUN_REFERENCE = 34.5  # Appendix G: the run's, held-out side from starts 9 to 13
PAPER_320 = 40.2  # the paper's 320-step value, in nats
FINAL_FIRST, FINAL_LAST = 301, 320  # a search's final level: its mean harm over steps 301 to 320
BREAKOUT_NATS = 5.0  # a search breaks out at the first step its two-step mean harm reaches 5 nats


class ReadingRefusal(Exception):
    """The records are not the test's complete set, or are not what they say they are."""


# ----------------------------------------------------------------------------- the arithmetic


def added(record: list[float] | np.ndarray, k: int) -> float:
    """A search's added harm at step k: its harm after step k less its harm at the start."""
    return float(record[k]) - float(record[0])


def final_level(record: list[float] | np.ndarray) -> float:
    """A search's mean harm over its last 20 steps, steps 301 to 320."""
    return float(np.mean(np.asarray(record, dtype=np.float64)[FINAL_FIRST : FINAL_LAST + 1]))


def reading(statistic: float) -> str:
    if statistic >= STARTS_AT:
        return "Starts"
    if statistic <= ELSE_AT:
        return "Something else"
    return "Undetermined"


def bit_equal(a: list[float], b: list[float]) -> bool:
    """Two records equal bit for bit, as float64."""
    x, y = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return x.shape == y.shape and x.tobytes() == y.tobytes()


Searches = dict[tuple[str, int], list[float]]


def mean_added(searches: Searches, keys: list[tuple[str, int]], k: int) -> float:
    return float(np.mean([added(searches[key], k) for key in keys]))


def by_start(searches: Searches, starts: tuple[int, ...], k: int) -> dict[int, float]:
    return {s: mean_added(searches, [(b, s) for b in BATCHES], k) for s in starts}


def by_batch(searches: Searches, starts: tuple[int, ...], k: int) -> dict[str, float]:
    return {b: mean_added(searches, [(b, s) for s in starts], k) for b in BATCHES}


def table(searches: Searches, starts: tuple[int, ...], k: int) -> np.ndarray:
    """Added harm at step k, rows the batches C1 to C8, columns the starts in the order given."""
    return np.array([[added(searches[(b, s)], k) for s in starts] for b in BATCHES], dtype=np.float64)


def anova(Y: np.ndarray) -> dict[str, Any]:
    """The pilot's two-way analysis of variance without replication (rows batches, columns starts), with the start's
    share of variance: its component over the sum of the batch's, the start's, and the residual's."""
    a = anova_two_way(Y)
    total = a["sigma2_b"] + a["sigma2_c"] + a["sigma2_int"]
    return {**a, "start_share": a["sigma2_c"] / total if total > 0 else float("nan")}


def breakout(record: list[float]) -> int | None:
    """The first step k >= 1 at which (record[k - 1] + record[k]) / 2 reaches 5 nats, by the harm-level table's own
    rule (`pilot.crossing`); None if it never does."""
    return P.crossing([float(x) for x in record], BREAKOUT_NATS)["k"]


def median_breakout(steps: list[int | None]) -> float:
    """The median breakout step, a search that never breaks out counted as later than any that does (infinite)."""
    return float(np.median([np.inf if k is None else float(k) for k in steps]))


def finals(searches: Searches, keys: list[tuple[str, int]]) -> dict[str, Any]:
    """The final levels, and the count at or above the paper's 40.2 nats two ways: by the harm after step 320 (as the
    checkpoint's Section 7 counted) and by the final level."""
    f = np.array([final_level(searches[key]) for key in keys], dtype=np.float64)
    at_320 = np.array([float(searches[key][N_STEPS]) for key in keys], dtype=np.float64)
    q1, med, q3 = np.percentile(f, [25, 50, 75])
    return {"n": int(f.size), "median": float(med), "q1": float(q1), "q3": float(q3), "min": float(f.min()), "max": float(f.max()),
            "at_or_above_paper_by_320": int(np.sum(at_320 >= PAPER_320)), "at_or_above_paper_by_final": int(np.sum(f >= PAPER_320)),
            "by_search": {key: float(v) for key, v in zip(keys, f)}}


# ----------------------------------------------------------------------------- the records


def _check_record(record: Any, what: str) -> list[float]:
    r = [float(x) for x in record]
    if len(r) != N_STEPS + 1 or not np.all(np.isfinite(r)):
        raise ReadingRefusal(f"{what}: not a finite record of {N_STEPS + 1} values")
    return r


def pilot_searches(path: Path = PILOT_RUNS) -> Searches:
    """The pilot's 64 records, C1 to C8 from starts 1 to 8."""
    a1 = json.load(open(path))["a1"]
    return {(b, s): _check_record(a1[b][str(s)]["record"], f"pilot {b} s{s}") for b in BATCHES for s in PILOT_STARTS}


def load_test_searches(path: Path = RECORDS) -> tuple[Searches, list[float]]:
    """The test's 40 records, C1 to C8 from starts 9 to 13, one each and nothing missing; and the guard's record.
    (Not named `test_...`: pytest collects this file by its name, `*_test.py`, when run over the whole folder.)"""
    data = json.load(open(path))
    test: Searches = {}
    guards = []
    for x in data["searches"]:
        key = (str(x["batch"]), int(x["start"]))
        if x["role"] == "guard":
            if key != GUARD:
                raise ReadingRefusal(f"a guard search of {key[0]} from start {key[1]}")
            guards.append(_check_record(x["record"], "guard"))
        elif x["role"] == "test":
            if key[0] not in BATCHES or key[1] not in TEST_STARTS or key in test:
                raise ReadingRefusal(f"the test search {key[0]} from start {key[1]} is not one of the 40, or is there twice")
            test[key] = _check_record(x["record"], f"test {key[0]} s{key[1]}")
        else:
            raise ReadingRefusal(f"a search of role {x['role']!r}")
    if len(test) != len(BATCHES) * len(TEST_STARTS) or len(guards) != 1:
        raise ReadingRefusal(f"{len(test)} test searches and {len(guards)} guard searches; the test has 40 and 1")
    return test, guards[0]


# ----------------------------------------------------------------------------- the printout


def _row(values: list[float], fmt: str = "{:>8.2f}") -> str:
    return "".join(fmt.format(v) for v in values)


def _anova_lines(a: dict[str, Any]) -> list[str]:
    d = a["df"]
    return [f"   Mean squares: batch {a['MS_B']:.2f} (df {d['B']}), start {a['MS_S']:.2f} (df {d['S']}), residual {a['MS_R']:.2f} (df {d['R']}).",
            f"   Variance components: batch {a['sigma2_b']:.2f}, start {a['sigma2_c']:.2f} (untruncated {a['sigma2_c_untruncated']:.2f}), "
            f"residual {a['sigma2_int']:.2f}. The start's share: {a['start_share']:.3f}."]


def _tables(searches: Searches, starts: tuple[int, ...]) -> list[str]:
    L = []
    for k in STEPS:
        Y = table(searches, starts, k)
        L.append(f"   Added harm at {k} steps:")
        L.append("   " + f"{'':>6}" + "".join(f"{'s' + str(s):>8}" for s in starts))
        for b, row in zip(BATCHES, Y):
            L.append("   " + f"{b:>6}" + _row(list(row)))
        L += _anova_lines(anova(Y))
    return L


def _finals_lines(f: dict[str, Any], who: str) -> list[str]:
    L = [f"   Each search's final level, its mean harm over steps {FINAL_FIRST} to {FINAL_LAST} ({who}):",
         "   " + f"{'':>6}" + "".join(f"{'s' + str(s):>8}" for s in sorted({s for _, s in f['by_search']}))]
    for b in BATCHES:
        L.append("   " + f"{b:>6}" + _row([v for (bb, _), v in sorted(f["by_search"].items(), key=lambda kv: kv[0][1]) if bb == b]))
    L.append(f"   Over the {f['n']}: median {f['median']:.2f}, quartiles {f['q1']:.2f} and {f['q3']:.2f} (numpy's linear interpolation), "
             f"range {f['min']:.2f} to {f['max']:.2f}.")
    n = f["n"]
    L.append(f"   At or above {PAPER_320} nats, the paper's 320-step value, by the harm after step {N_STEPS} (as the checkpoint's Section 7 "
             f"counted its 12.5 and 31 percent): {f['at_or_above_paper_by_320']} of {n} ({100 * f['at_or_above_paper_by_320'] / n:.1f} percent).")
    L.append(f"   At or above {PAPER_320} nats, by the final level: {f['at_or_above_paper_by_final']} of {n} "
             f"({100 * f['at_or_above_paper_by_final'] / n:.1f} percent).")
    return L


def _breakout_lines(searches: Searches, starts: tuple[int, ...], who: str) -> list[str]:
    def step(k: int | None) -> str:
        return "-" if k is None else str(k)

    def med(v: float) -> str:
        return f"> {N_STEPS}" if np.isinf(v) else f"{v:g}"

    steps = {(b, s): breakout(searches[(b, s)]) for b in BATCHES for s in starts}
    span = f"{starts[0]} to {starts[-1]}"
    L = [f"   Each search's breakout step, the first step k at which (record[k - 1] + record[k]) / 2 reaches {BREAKOUT_NATS:g} nats",
         f"   (pilot.crossing, the harm-level table's rule), {who}; \"-\" where it never does within {N_STEPS} steps:",
         "   " + f"{'':>6}" + "".join(f"{'s' + str(s):>8}" for s in starts)]
    for b in BATCHES:
        L.append("   " + f"{b:>6}" + "".join(f"{step(steps[(b, s)]):>8}" for s in starts))
    L.append(f"   By start, over the eight batches: the median breakout step (a search that never breaks out counted as later than any")
    L.append("   that does), and how many never break out.")
    L.append("   " + f"{'start':>6}{'median':>10}{'never':>8}")
    for s in starts:
        col = [steps[(b, s)] for b in BATCHES]
        L.append("   " + f"{s:>6}{med(median_breakout(col)):>10}{sum(k is None for k in col):>8}")
    L.append(f"   By batch, over starts {span}: the median breakout step, and how many never break out.")
    L.append("   " + f"{'batch':>6}{'median':>10}{'never':>8}")
    for b in BATCHES:
        row = [steps[(b, s)] for s in starts]
        L.append("   " + f"{b:>6}{med(median_breakout(row)):>10}{sum(k is None for k in row):>8}")
    return L


def _reference_lines(pilot: Searches) -> list[str]:
    """Appendix G's quoted reference values, with the pilot's exact value beside its 25.5."""
    exact = mean_added(pilot, [(b, s) for b in BATCHES for s in PILOT_STARTS], N_STEPS)
    return [f"   For reference (Appendix G): the pilot's {PILOT_REFERENCE} (C1 to C8 from starts 1 to 8; exactly {exact:.4f} from runs.json); "
            f"the run's {RUN_REFERENCE} (held-out side, 16 batches, from starts 9 to 13).",
            f"   The checkpoint's {PILOT_REFERENCE} was rounded twice ({exact:.4f} to {exact:.2f}, then to {PILOT_REFERENCE}); rounded once it is "
            f"{exact:.1f}. The thresholds, {STARTS_AT:g} and {ELSE_AT:g}, are untouched."]


def reading_text(test: Searches, guard: list[float], pilot: Searches) -> tuple[str, bool]:
    """The reading as printed, and whether the guard held. A guard that fails stops it after the guard's line."""
    L: list[str] = ["The starts test, read as fixed in advance (sessions/005/checkpoint.md, Appendix G; sessions/006/engineering/plan_1.md, Section 2.4).",
                    "Added harm at step k is record[k] - record[0], in nats.", ""]
    ok = bit_equal(guard, pilot[GUARD])
    L.append(f"The guard: C1 from start 1, searched again in this test, {'equals' if ok else 'DOES NOT EQUAL'} the pilot's record "
             f"(runs.json, a1, C1, start 1) bit for bit, all {N_STEPS + 1} values.")
    if not ok:
        L.append("The guard failed. Nothing else is read. Stop and report.")
        return "\n".join(L) + "\n", False
    keys = [(b, s) for b in BATCHES for s in TEST_STARTS]
    stat = mean_added(test, keys, N_STEPS)
    L += ["", f"1. The deciding statistic: the mean added harm after step {N_STEPS} over the {len(keys)} searches of C1 to C8 from starts 9 to 13.",
          f"   {stat:.4f} nats. Reading: {reading(stat)}.",
          f"   The reading fixed in advance: at or above {STARTS_AT:g} nats, Starts; at or below {ELSE_AT:g} nats, Something else; between, Undetermined."]
    L += _reference_lines(pilot)
    L += ["", "2. Each start's mean added harm over the eight batches C1 to C8:", "   " + f"{'start':>6}" + "".join(f"{str(k) + ' steps':>12}" for k in STEPS)]
    bs = {k: by_start(test, TEST_STARTS, k) for k in STEPS}
    for s in TEST_STARTS:
        L.append("   " + f"{s:>6}" + _row([bs[k][s] for k in STEPS], "{:>12.2f}"))
    L += ["", "3. Each batch's mean added harm over starts 9 to 13 (this test), beside the pilot's over starts 1 to 8:",
          "   " + f"{'batch':>6}" + "".join(f"{str(k) + ', 9-13':>12}{str(k) + ', 1-8':>12}" for k in STEPS)]
    tb = {k: by_batch(test, TEST_STARTS, k) for k in STEPS}
    pb = {k: by_batch(pilot, PILOT_STARTS, k) for k in STEPS}
    for b in BATCHES:
        L.append("   " + f"{b:>6}" + "".join(f"{tb[k][b]:>12.2f}{pb[k][b]:>12.2f}" for k in STEPS))
    joined = {**pilot, **test}
    L += ["", "4. The 8 by 13 tables: the pilot's 64 searches (starts 1 to 8) joined with this test's 40 (starts 9 to 13), with a two-way",
          "   analysis of variance on batch and start. The start's share is its variance component over the sum of the three."]
    L += _tables(joined, PILOT_STARTS + TEST_STARTS)
    L += ["", "5. Description."]
    L += _finals_lines(finals(test, keys), "the 40 searches of this test")
    L += ["", "6. Description: the breakout step."]
    L += _breakout_lines(test, TEST_STARTS, "the 40 searches of this test")
    return "\n".join(L) + "\n", True


def pilot_only_text(pilot: Searches) -> str:
    """The same sections on the pilot's 64 records alone, for checking this script against Appendix G. No reading."""
    keys = [(b, s) for b in BATCHES for s in PILOT_STARTS]
    stat = mean_added(pilot, keys, N_STEPS)
    L = ["The starts test's reading script, run on the pilot's 64 records alone (results/s4_pilot/part_a/runs.json, key a1), to check it.",
         "No test record is read and no reading is given. Added harm at step k is record[k] - record[0], in nats.", "",
         f"1. The pilot's mean added harm after step {N_STEPS} over its {len(keys)} searches of C1 to C8 from starts 1 to 8: {stat:.4f} nats."]
    L += _reference_lines(pilot)
    L += ["", "2. Each start's mean added harm over the eight batches C1 to C8:", "   " + f"{'start':>6}" + "".join(f"{str(k) + ' steps':>12}" for k in STEPS)]
    bs = {k: by_start(pilot, PILOT_STARTS, k) for k in STEPS}
    for s in PILOT_STARTS:
        L.append("   " + f"{s:>6}" + _row([bs[k][s] for k in STEPS], "{:>12.2f}"))
    L += ["", "3. Each batch's mean added harm over starts 1 to 8:", "   " + f"{'batch':>6}" + "".join(f"{str(k) + ', 1-8':>12}" for k in STEPS)]
    pb = {k: by_batch(pilot, PILOT_STARTS, k) for k in STEPS}
    for b in BATCHES:
        L.append("   " + f"{b:>6}" + "".join(f"{pb[k][b]:>12.2f}" for k in STEPS))
    L += ["", "4. The pilot's 8 by 8 tables, with the two-way analysis of variance on batch and start."]
    L += _tables(pilot, PILOT_STARTS)
    L += ["", "5. Description."]
    L += _finals_lines(finals(pilot, keys), "the pilot's 64 searches")
    L += ["", "6. Description: the breakout step."]
    L += _breakout_lines(pilot, PILOT_STARTS, "the pilot's 64 searches")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pilot-only", action="store_true", help="read only the pilot's runs.json, to check this script")
    ap.add_argument("--records", type=Path, default=RECORDS)
    ap.add_argument("--pilot-runs", type=Path, default=PILOT_RUNS)
    args = ap.parse_args(argv)
    pilot = pilot_searches(args.pilot_runs)
    if args.pilot_only:
        sys.stdout.write(pilot_only_text(pilot))
        return 0
    test, guard = load_test_searches(args.records)
    text, ok = reading_text(test, guard, pilot)
    sys.stdout.write(text)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
