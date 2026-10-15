# A Plumbing Run of the Made-Up-Data Harness: Not a Result

These four files are the output of one run of `vpd_audit_2/lead_madeup.py` made while the harness was being built, to
check that it ran end to end. They are committed as they were, byte for byte, because Amendment 2
(`freeze/amendment2.md`, Section 1) says what had been seen before it was written, and this is it.

- **Size:** 100 experiments per scenario, 200 for a rerun. The test of record uses 2,000 and 10,000.
- **Seed:** master seed 20261005. The test of record uses 20261006, so none of its experiments is here.
- **Generator:** the one committed in Amendment 1, in which a held-out batch's vulnerability carries its pilot type's
  factor. Amendment 2 removes that factor from the test of record.
- **When:** 5 October 2026, before Amendment 2 was written. The code was not yet committed: the report names commit
  `b410ddb` with `code_clean` false, because `lead_madeup.py` was still an untracked file. It was committed
  afterwards, unchanged in what this run exercises, as `87806e6`.
- **What it showed:** coverage near 0.90 in most core cells with nearly all misses on one side, and near 0.76 at the
  10-nat level. At this size the cell-by-cell figures mean little.

Nothing here sets a multiplier, and `multipliers.json` in this folder must not be copied anywhere. The made-up
experiments are built on the pilot's own-batch searches on calibration batches; no number here is a result of the
lead experiment.

| File | SHA-256 |
|---|---|
| `report.json` | `97c8759f4ade54e00557271f3075b42f1acb3e229a3c5c0376b408def90e4ccf` |
| `summary.md` | `512bec265f4c791887718d28467f86805718ecd98caef0fcb8846bfd04522b97` |
| `multipliers.json` | `05bb8e99865dc7127bf08c686412657be781e3e936802cf19ad7352d2e04852b` |
| `runtime.json` | `0094bdae61f9ebdec1f9e0ad15f161563b5b6caccfafac18c9f4bdb965eb8fc7` |
