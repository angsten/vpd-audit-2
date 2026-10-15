"""Session 5, plans 2 and 4: the lead run's spend ledger and its checks against the PI's cap.

Pure arithmetic, with no cloud call: how much work each stage holds, how long it takes at measured timings, what it
costs, and whether the projection exceeds the cap. The stages are those of the table and run specification's Section
4.1, with the lead's held-out side in two waves (plan 4, Section 4.3). Money is counted as Amendment 4's Section 3 says
(`freeze/amendment4.md`):

  - The cap is $150, covering the session's rehearsals and both arms of the run.
  - Money spent is counted from the run's own clocks. It is the larger of two figures: function hours at $6.80, the
    pilot's billed rate; and the provider's listed price times function seconds plus 50 seconds of billed boot for
    every container life, reruns included. A bill that has posted enters as a third figure, the bill times 1.03. No
    check waits for a bill.
  - What remains is priced as the larger of the same two figures.
  - Check C0 comes after the rehearsals, C1 after the attack side, C2 after the first held-out container, and C3
    before the delta-on arm. C2 takes the rest of the held-out side at the larger of that container's own seconds and
    the rehearsal's projection.

A stage's shape is a `Stage`. The deciding run's five stages are `DESIGN`; the rehearsal's five are `REHEARSAL_DESIGN`,
the same code on two calibration batches, so that the launcher, the ledger, and the checks run once before they matter.

Nothing here reads a harm. The number of scoring passes is taken at its upper bound, every level setting present,
since the count of missing level settings is sealed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CAP_DOLLARS = 150.0  # Amendment 4, Section 2: the PI's cap
FLAT_RATE = 6.80  # dollars per function hour: the pilot's question 2 part, $19.20 for 10,170 function seconds
BOOT_SECONDS = 50.0  # Amendment 4, Section 3: billed boot allowed for every container life
BILLING_LAG = 1.03
N_SHUFFLES = 8
WARM_ITERATIONS = 10  # a search's first iterations are timed apart from the rest (`lead_run.search_unit`)
CHECK_AFTER = {0: "C1", 1: "C2", 2: "C3"}  # by a stage's place in its design


@dataclass(frozen=True)
class Stage:
    """One stage's shape: its containers, and what each of them does."""

    name: str
    arm: str
    side: str  # "attack" or "heldout"
    containers: int  # one per batch
    starts: int  # searches per container
    steps: int  # iterations per search
    settings: int  # scored settings per search, at their upper bound
    shuffled: int  # of them, those that have shuffled copies
    attack_batches: int  # attack batches whose searches each held-out container scores; 0 on the attack side
    delta_held: bool  # the 24 delta entries held at 1


DESIGN = (
    Stage("lead_attack", "lead", "attack", 16, 5, 320, 10, 8, 0, False),
    Stage("lead_heldout_1", "lead", "heldout", 1, 5, 320, 10, 8, 16, False),  # wave 1: H1 alone
    Stage("lead_heldout_2", "lead", "heldout", 15, 5, 320, 10, 8, 16, False),  # wave 2: H2 to H16
    Stage("delta_attack", "delta_on", "attack", 8, 5, 320, 5, 5, 0, True),
    Stage("delta_heldout", "delta_on", "heldout", 8, 5, 320, 5, 5, 8, True),
)
# The rehearsal: two calibration batches, pilot start 1, each held-out role scoring its own batch's attack file alone;
# the delta-on searches run 20 steps (plan 2, Section 7; plan 4, Section 6.1).
REHEARSAL_DESIGN = (
    Stage("rehearsal_attack", "rehearsal", "attack", 2, 1, 320, 10, 8, 0, False),
    Stage("rehearsal_heldout_1", "rehearsal", "heldout", 1, 1, 320, 10, 8, 1, False),
    Stage("rehearsal_heldout_2", "rehearsal", "heldout", 1, 1, 320, 10, 8, 1, False),
    Stage("rehearsal_delta_attack", "rehearsal_delta_on", "attack", 2, 1, 20, 5, 5, 0, True),
    Stage("rehearsal_delta_heldout", "rehearsal_delta_on", "heldout", 2, 1, 20, 5, 5, 1, True),
)
TIMING_KEYS = ("seconds_per_search_step", "seconds_per_search_step_delta_on", "seconds_per_scoring_pass", "seconds_to_ready",
               "seconds_first_search_extra", "seconds_per_search_fixed", "seconds_per_commit_after_search", "seconds_per_commit_after_blocks",
               "seconds_per_shuffle", "seconds_per_search_unit_other", "seconds_per_block_other")


def stage_named(name: str, design: tuple[Stage, ...] = DESIGN) -> Stage:
    return next(s for s in design if s.name == name)


def stage_work(stage: Stage | str) -> dict[str, int]:
    """What a stage holds: containers, searches, search steps, scoring passes (own-batch re-scores, and for a held-out
    stage the carried settings with their shuffled copies, at the upper bound), shuffled copies made, scoring blocks,
    and volume commits (one after each search unit, and one after each attack batch's blocks)."""
    s = stage_named(stage) if isinstance(stage, str) else stage
    searches = s.containers * s.starts
    passes = searches * (1 + s.settings)  # the start and each scored setting, re-scored on the batch searched
    blocks = s.containers * s.attack_batches * s.starts
    shuffles = blocks * s.shuffled * N_SHUFFLES
    passes += blocks * s.settings + shuffles
    after_blocks = s.containers * s.attack_batches
    return {"containers": s.containers, "searches": searches, "search_steps": searches * s.steps, "scoring_passes": passes, "shuffles_made": shuffles,
            "blocks": blocks, "commits": searches + after_blocks, "commits_after_search": searches, "commits_after_blocks": after_blocks}


def stage_seconds(stage: Stage | str, timings: dict[str, float]) -> dict[str, float]:
    """A stage's function seconds at the given timings, in three parts: searching, scoring, and everything else.

    A search is its steps at the steady rate of its arm, plus a fixed part (its last harm and its return). The first
    search of a container pays a warm-up once, counted with the container's start."""
    s = stage_named(stage) if isinstance(stage, str) else stage
    w = stage_work(s)
    t = timings
    search = w["search_steps"] * (t["seconds_per_search_step_delta_on"] if s.delta_held else t["seconds_per_search_step"])
    scoring = w["scoring_passes"] * t["seconds_per_scoring_pass"]
    overhead = (w["containers"] * (t["seconds_to_ready"] + t["seconds_first_search_extra"])
                + w["searches"] * (t["seconds_per_search_fixed"] + t["seconds_per_search_unit_other"])
                + w["commits_after_search"] * t["seconds_per_commit_after_search"] + w["commits_after_blocks"] * t["seconds_per_commit_after_blocks"]
                + w["shuffles_made"] * t["seconds_per_shuffle"] + w["blocks"] * t["seconds_per_block_other"])
    return {"search": search, "scoring": scoring, "overhead": overhead, "total": search + scoring + overhead}


def money(function_seconds: float, lives: float, listed_hourly_price: float, billed: float | None = None) -> dict[str, Any]:
    """Amendment 4, Section 3, item 1. The larger of two figures: function hours at $6.80; and the listed price times
    function seconds plus 50 seconds of billed boot for every container life. A bill that has posted (`billed`) enters
    as a third figure, the bill times 1.03; `None` is a bill not read or not posted."""
    flat = function_seconds / 3600.0 * FLAT_RATE
    with_boot = (function_seconds + BOOT_SECONDS * lives) / 3600.0 * float(listed_hourly_price)
    figures = [flat, with_boot] + ([billed * BILLING_LAG] if billed is not None else [])
    return {"function_seconds": float(function_seconds), "container_lives": float(lives), "at_the_flat_rate": flat,
            "at_the_listed_price_with_boot": with_boot, "billed": billed, "dollars": max(figures)}


def add(*counts: dict[str, Any]) -> dict[str, Any]:
    """Function seconds, container lives, and posted bills, added over several runs. The bill is `None` where no run's
    bill has posted, and otherwise the sum of those that have: a part of the whole, which can only be too low."""
    posted = [c["billed"] for c in counts if c.get("billed") is not None]
    return {"function_seconds": float(sum(c["function_seconds"] for c in counts)), "container_lives": float(sum(c["container_lives"] for c in counts)),
            "billed": float(sum(posted)) if posted else None}


def check_c0(timings: dict[str, float], listed_hourly_price: float, spent_so_far: dict[str, Any], assemble_seconds: float = 0.0,
             design: tuple[Stage, ...] = DESIGN, cap: float = CAP_DOLLARS) -> dict[str, Any]:
    """Check C0, after the rehearsals: the whole run projected from the rehearsal's timings, priced as the larger of the
    two figures, on top of what the rehearsals have cost (`spent_so_far`: their function seconds, container lives, and
    posted bills, which the cap covers). A rehearsal's bill is money already spent and is never used as a rate."""
    stages = {s.name: stage_seconds(s, timings) for s in design}
    seconds = sum(x["total"] for x in stages.values()) + assemble_seconds
    lives = sum(s.containers for s in design)
    run = money(seconds, lives, listed_hourly_price)
    spent = money(spent_so_far["function_seconds"], spent_so_far["container_lives"], listed_hourly_price, spent_so_far.get("billed"))
    projected = spent["dollars"] + run["dollars"]
    return {"check": "C0", "flat_rate": FLAT_RATE, "listed_hourly_price": float(listed_hourly_price), "boot_seconds": BOOT_SECONDS, "stages": stages,
            "assemble_seconds": assemble_seconds, "function_hours": seconds / 3600.0, "run": run, "run_dollars": run["dollars"], "spent": spent,
            "spent_dollars": spent["dollars"], "projected_dollars": projected, "cap": cap, "exceeds_cap": projected > cap}


def check_later(name: str, *, spent_so_far: dict[str, Any], remaining_seconds: float, remaining_lives: float, listed_hourly_price: float,
                cap: float = CAP_DOLLARS) -> dict[str, Any]:
    """Checks C1 to C3: money spent, plus what remains priced as the larger of the two figures."""
    spent = money(spent_so_far["function_seconds"], spent_so_far["container_lives"], listed_hourly_price, spent_so_far.get("billed"))
    remaining = money(remaining_seconds, remaining_lives, listed_hourly_price)
    projected = spent["dollars"] + remaining["dollars"]
    return {"check": name, "flat_rate": FLAT_RATE, "listed_hourly_price": float(listed_hourly_price), "boot_seconds": BOOT_SECONDS, "spent": spent,
            "spent_dollars": spent["dollars"], "remaining": remaining, "remaining_dollars": remaining["dollars"], "projected_dollars": projected,
            "cap": cap, "exceeds_cap": projected > cap}


def remaining_seconds(rest: tuple[Stage | str, ...], timings: dict[str, float], measured: dict[str, float], design: tuple[Stage, ...] = DESIGN) -> float:
    """The function seconds of the stages still to run, at this run's own measured timings: each stage's seconds at the
    rehearsal's timings, times the ratio of measured to predicted seconds over the stages of its side that have run
    (`measured`: stage name to its function seconds), and where none of its side has run, over every stage that has."""
    def scale(stages: list[Stage]) -> float:
        predicted = sum(stage_seconds(s, timings)["total"] for s in stages)
        return sum(measured[s.name] for s in stages) / predicted if predicted > 0 else 0.0

    ran = [s for s in design if s.name in measured]
    total = 0.0
    for x in rest:
        stage = stage_named(x, design) if isinstance(x, str) else x
        s = scale([r for r in ran if r.side == stage.side]) or scale(ran) or 1.0
        total += stage_seconds(stage, timings)["total"] * s
    return total


def remaining_after_first_heldout(design: tuple[Stage, ...], timings: dict[str, float], measured: dict[str, float], first_container_seconds: float) -> float:
    """What remains at check C2, after the one held-out container of wave 1 (plan 4, Section 4.3): wave 2 at the larger
    of that container's seconds and the rehearsal's projection for a container, since one container is a single reading
    and the first to finish is the fastest; then the later stages as `remaining_seconds` gives them."""
    wave_2 = design[2]
    predicted = stage_seconds(wave_2, timings)["total"] / wave_2.containers
    return wave_2.containers * max(float(first_container_seconds), predicted) + remaining_seconds(design[3:], timings, measured, design)


def timings_from_rehearsal(containers: list[dict[str, Any]]) -> dict[str, Any]:
    """The projection's timings from the rehearsal's containers. Each is `{"arm", "timings"}`, the timings being a
    container's seconds and counts by kind (`lead_run.Context.tick`). Every container that returned is used.

      - Seconds per search step: the steady rate, over the iterations after a search's first ten; the lead's from the
        320-step searches, the delta-on arm's from its own 20-step searches.
      - The first search of a container: what its first ten iterations took beyond ten at its arm's steady rate.
      - A search's fixed part: its last harm and its return.
      - Seconds to ready: from the function's start to the end of preparation, whether or not a search follows.
      - A volume commit: those made after a unit was written, by kind; a commit with nothing new is left out.
      - A search unit's other seconds leave out the check of the wrapper against the authors' function, which only a
        rehearsal runs.

    Each is a mean over what was observed; `observations` holds the values the means are of."""
    def is_delta(c: dict[str, Any]) -> bool:
        return c["arm"].endswith("delta_on")

    def total(cs: list[dict[str, Any]], kind: str) -> float:
        return float(sum(c["timings"].get(kind, 0.0) for c in cs))

    def per(cs: list[dict[str, Any]], kind: str) -> float:
        n = total(cs, kind + "_count")
        if n <= 0:
            raise ValueError(f"the rehearsal has no timing of the kind {kind}")
        return total(cs, kind) / n

    def mean(xs: list[float], kind: str) -> float:
        if not xs:
            raise ValueError(f"the rehearsal has no timing of the kind {kind}")
        return float(sum(xs) / len(xs))

    def steady(c: dict[str, Any]) -> float:
        return c["timings"]["search_iterations_after_warm"] / c["timings"]["search_iterations_after_warm_count"]

    lead = [c for c in containers if not is_delta(c)]
    delta = [c for c in containers if is_delta(c)]
    step = {False: per(lead, "search_iterations_after_warm"), True: per(delta, "search_iterations_after_warm")}
    searched = [c for c in containers if c["timings"].get("search_iteration_0_count")]
    extra = [c["timings"]["search_iteration_0"] + c["timings"]["search_iterations_warm"] - WARM_ITERATIONS * step[is_delta(c)] for c in searched]
    fixed = [c["timings"]["search_final_harm"] + c["timings"]["search_tail"] for c in searched if not is_delta(c)]
    ready = [c["timings"]["to_ready"] for c in containers if "to_ready" in c["timings"]]
    with_units = [c for c in lead if c["timings"].get("search_unit_whole_count")]
    unit_other = (total(with_units, "search_unit_whole") - total(with_units, "search") - total(with_units, "scoring_in_search_units")
                  - total(with_units, "wrapper_check")) / max(total(with_units, "search_unit_whole_count"), 1.0)
    with_blocks = [c for c in lead if c["timings"].get("block_whole_count")]
    block_other = (total(with_blocks, "block_whole") - total(with_blocks, "scoring_in_blocks") - total(with_blocks, "making_shuffles")) / max(
        total(with_blocks, "block_whole_count"), 1.0)
    return {
        "seconds_per_search_step": step[False],
        "seconds_per_search_step_delta_on": step[True],
        "seconds_per_scoring_pass": per(lead, "scoring"),
        "seconds_to_ready": mean(ready, "to_ready"),
        "seconds_first_search_extra": max(mean(extra, "search_iteration_0"), 0.0),
        "seconds_per_search_fixed": mean(fixed, "search_final_harm"),
        "seconds_per_commit_after_search": per(containers, "volume_commit_after_search"),
        "seconds_per_commit_after_blocks": per(containers, "volume_commit_after_blocks"),
        "seconds_per_shuffle": per(lead, "making_shuffles"),
        "seconds_per_search_unit_other": max(unit_other, 0.0),
        "seconds_per_block_other": max(block_other, 0.0),
        "observations": {
            "seconds_to_ready": ready, "seconds_first_search_extra": extra, "seconds_per_search_fixed": fixed,
            "seconds_per_search_step_by_search": [steady(c) for c in searched if not is_delta(c)],
            "seconds_per_search_step_delta_on_by_search": [steady(c) for c in searched if is_delta(c)],
            "seconds_of_the_first_iteration": [c["timings"]["search_iteration_0"] for c in searched],
            "seconds_per_iteration_in_the_rest_of_the_first_ten": [c["timings"]["search_iterations_warm"] / c["timings"]["search_iterations_warm_count"]
                                                                  for c in searched],
            "of_the_delta_on_arm": [is_delta(c) for c in searched],
        },
    }
