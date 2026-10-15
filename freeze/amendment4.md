# Freeze File, Part 1: Amendment 4

*Session 5, 6 October 2026. Written by Ines, recording the PI's decision on the spending cap after the first rehearsal measured the run's real costs. Written before any deciding run.*

## What This Amendment Does

Part 1 caps the lead experiment at \$105, "the PI's", and requires: "if projected spend would exceed \$105, work stops and goes to the PI. Nothing is trimmed silently." The first rehearsal, on a calibration batch, measured the run's timings on the real hardware. The projection then exceeded \$105, so by that rule the run did not start and the question went to the PI. This amendment records the PI's new cap and how spend is counted against it.

**The design does not change:** the same batches, starts, steps, scored settings, and shuffles. No signed line or threshold changes. Nothing is added to the design to use the room under the new cap.

**No carry-over number existed when this was written.**

## 0. Identity

| Entry | Value |
|---|---|
| Amends | The cap of Part 1 (its essentials, Section 6, and Section 10, item 3) and the spend paragraph of Amendment 1's Section 6 |
| Amendment | 4 |
| Date | 6 October 2026, session 5 |
| Commit | A commit of its own on `session-005-lead`, carrying this file as `vpd-audit-2/freeze/amendment4.md`, pushed before any deciding run |
| The PI's decision | "Yes, cap can be 150", in the session 5 transcript on 6 October 2026, in answer to a request for a cap that covers the rehearsals. The team had recommended \$120 |

## 1. What the Rehearsal Measured

The rehearsal ran two B200 containers on calibration batch C1 at commit `e41dc95` and scored nothing on another batch. At the pilot's billed rate of \$6.80 per function hour:

| Item | Count | Seconds each | Dollars |
|---|---|---|---|
| Search steps | 76,800 | 0.3877 | 56.24 |
| Scoring passes, at their upper bound | 111,360 | 0.1842 | 38.76 |
| Commits of the cloud volume | 560 | 4.54 | 4.80 |
| Container start to first search step | 48 | 34.7 to 57.9 | 3.14 to 5.25 |
| Making shuffled copies | 94,720 | 0.0074 | 1.33 |
| Everything else | | | 0.12 |
| **The run** | | | **104.39 to 106.49** |

With the rehearsal's own \$0.81, the projection is \$105.20 to \$107.30. Searching and scoring came in within 2.4 percent of the estimate behind the \$105 cap. The estimate's \$5 of margin went on overhead that had only been guessed, chiefly commits of the volume: 95 seconds per held-out container of the lead arm against a guessed 30.

## 2. The Cap

**\$150, covering the session's rehearsals and both arms of the run.**

The expected spend is about \$109: the run at about \$105, the first rehearsal at \$0.75 as billed, and a repeat rehearsal at about \$3. The risks the team could size add up to \$9 to \$14: slower commits when 16 containers write at once, a few lost containers, a billed rate a few percent above \$6.80, slow start-up, and, until the repeat rehearsal settles it, slower search steps in the delta-on arm.

The cap is a ceiling and not a budget. It still stops a silent or runaway overspend: scoring passes twice as slow would add \$39. What it no longer does is stop the run inside the lead arm, with sealed files half written, for want of a dollar.

## 3. How Spend Is Counted Against It

The rule itself is unchanged: **if projected spend would exceed the cap, work stops and goes to the PI, and nothing is trimmed silently.** Three details change, because the provider's bill posts by the hour and had not posted 37 minutes after the rehearsal finished.

1. **Money spent is counted from the run's own clocks, not from the bill.** It is the larger of two figures: function hours at \$6.80; and the provider's listed price times function seconds plus an allowance of 50 seconds of billed boot time for every container life, reruns included. The bill is read whenever it has posted, with the time, and enters as the larger of the two figures and the bill times 1.03. No check waits for a bill.
2. **The boot allowance is conservative, and is kept.** The 50 seconds comes from the pilot's bill: \$19.20 at the listed \$6.5525 per hour is 10,549 billed seconds against 10,170 function seconds over 8 containers. The first rehearsal's bill has since posted: \$0.7509, read at 16:12 UTC on 6 October, below both of the ledger's figures for that rehearsal (\$0.81 and \$1.05). It implies at most about 4 seconds of billed boot per container life. So the allowance overstates the run by about \$4, which the cap absorbs.
3. **One held-out container runs to completion before the other fifteen start.** The attack stage is 90 percent searching, so the check after it cannot see slow scoring or slow commits, which are 63 percent of the held-out stage. The check after the first held-out container can, and with one container run first it stops the run at about \$25 spent and not \$80. It projects the held-out stage from the larger of that container's seconds and the rehearsal's projection, since the first container to finish is the fastest.

The checks fall where Amendment 1 put them: after the rehearsals, after the attack side, after the first held-out container, and before the delta-on arm, which still goes last.

## 4. What Does Not Change

The design; every reading, line, and threshold; the sealing; the order of the arms; and the rule that a stop goes to the PI.
