# Erratum to the Table and Run Specification

Lena, session 5, written right after `sessions/005/notes/lena/table_and_run_spec.md` and before any deciding run. Notes cannot be edited, so the corrections are here. None changes a requirement or a conclusion.

## Wrong Cross-References

1. **Section 1** says "Section 11 lists the points where I depart from the draft or need a decision." Those points are in **Section 12**.
2. **Section 3.3,** in the row for `excluded_H`, points to "Section 7". The overlapping texts are specified in **Section 11.2**.

## Wrong Numbers

3. **Section 6, verification item 2,** says "about 2,600 bitwise comparisons across the two arms". The count is about **2,240**: in the lead arm, 160 searches each with the start and 10 scored settings (1,760, less any missing level settings); in the delta-on arm, 80 searches each with the start and 5 scored settings (480).
4. **Section 9.1** says "Scoring is 45 percent of the time, so a scoring pass 10 percent slower than 0.18 seconds uses \$3.50". From the table in that section, scoring is about 20,075 of 52,920 seconds, which is **38 percent**, and a 10 percent slowdown costs about **\$3.80**.
5. **Section 9.1, the overhead column.** The text gives a held-out container 45 + 15 + 30 = 90 seconds of overhead, which would be 1,440 seconds for the lead's 16 and 720 for the delta-on arm's 8. The table shows 1,480 and 560, from a finer guess (fewer shuffles and commits in the delta-on arm). The two differ by under \$0.40 in total. The total of about 14.7 function hours, and so about \$100 at \$6.80 per function hour and about \$110 at \$7.50, stands either way. All overhead figures are guesses until the rehearsal measures them.

## A Statement That Is an Inference

6. **Section 7, "Copying",** says the pilot's byte-copy pattern "was written after the pilot's question 2 part ran and has not yet run in the cloud". I did not check the commit history. I infer it from two sources: the session 4 checkpoint's Section 12, which warns of "the first cloud use of the new step that copies sealed files, which has not yet run in the cloud", and the docstring of `vpd-audit-2/vpd_audit_2/pilot_a.py`, which attributes the job-writes-its-own-sealed-file design to plan 7, a plan later than the one that ran the pilot's question 2 part. The engineer will know which it is. The rehearsal is worth running in either case.

## A Clarification

7. **Section 6.** The wrapper repeats the authors' `recon_loss_kl` line for line; it does not call it. The claim that the batch harm "stays the authors' own" therefore rests on the two bitwise checks listed there (against the authors' function on the same logits, and against the search's record on every own-batch re-score), not on the authors' code being executed. If the head prefers that the authors' function be literally called, the cost is a second KL computation on every scoring pass, which the rehearsal can time before a decision.
