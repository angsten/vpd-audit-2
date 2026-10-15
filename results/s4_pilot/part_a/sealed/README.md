# Sealed: Do Not Open

This folder holds values sealed under the pilot's discipline (session 4, `sessions/004/engineering/plan_6.md`, Section 3). **No one may open, load, print, or summarize them** until the part of the freeze file named below is signed. After that, the freeze file's own rules govern their use.

| File | What it holds | Governed by |
|---|---|---|
| `a3_shuffles.npz` | A3: each saved source's own-batch harm and its 8 frequency-stratified shuffles' harms, batches C1 to C8 | Freeze file, **Part 1** (question 2) |
| `a3_shuffles_C{j}.npz`, if present | The same, one file per batch, as `pilot_a.batch_job` now writes them | Freeze file, **Part 1** (question 2) |

**The one permitted reader before signature** is code that computes the reported noise ratio and writes nothing else: `vpd_audit_2/pilot_a_tables.py`. Neither $D$ nor the shuffled means may be reported.
