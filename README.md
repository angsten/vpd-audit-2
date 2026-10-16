# vpd-audit-2: A Follow-Up Audit of the Released VPD Decomposition

This repository holds the code for a follow-up to [`vpd-audit`](https://github.com/angsten/vpd-audit), which audited the released adVersarial Parameter Decomposition (VPD) of a four-layer, 67M-parameter language model (WandB run `goodfire/spd/s-55ea3f9b`). It asks two questions that audit left open:
- how often a component's causal-importance label says it is needed when removing it would not matter;
- whether the masks an adversary finds on some texts also damage texts it never saw.

It uses the earlier harness as a library, through a submodule pinned at the commit the published post links to, and never runs that harness's own analysis commands.

This code was developed inside a private research log, and docstrings, tests, and result files cite it in places as "the research log", together with commit hashes and branch names of that log's repository; neither is public. `freeze/` holds the rules fixed before each measurement, and its amendments record what had been seen when each was written. The files under `freeze/`, the docstrings and tests, and the text of several committed results were reworded after the runs; only wording changed (research log, merge commit `67eb50b8ad69d49efd5211ffed229acbdc8e5ac5`, 16 October 2026). The analysis entry point (`lead_analysis.py`) and the launchers check files against run commits that are not in this copy's history, so they refuse to run here; the committed tables and readings are the record.

## Setup

You need Python 3.13 and [uv](https://docs.astral.sh/uv/). Clone with submodules, then sync:

```
git clone --recurse-submodules <this repository>
cd vpd-audit-2
uv sync
```

`third_party/vpd-audit` is pinned at `b6d3bac`, and inside it the authors' code `goodfire-ai/param-decomp` at `74146b5` (the `vpd-paper` tag). Check both with `git submodule status --recursive`. The submodule is registered in this repository's own `.gitmodules`. The lockfile pins every registry package to the version in `vpd-audit`'s own lockfile, so the environment matches the one the earlier numbers were measured in.

Always import `vpd_audit_2.env` before anything from `vpd_audit` or `param_decomp`. It points `VPD_AUDIT_CACHE_DIR`, `HF_HOME`, and `PARAM_DECOMP_OUT_DIR` at this repository's `.cache/`, which git ignores, instead of a folder inside the submodule. On Modal they point at the volume `vpd-audit-2-cache`.

The WandB key is read from `WANDB_API_KEY` or from a `.env` file in this folder or the one above it. Modal must be logged in (`uv run modal token new`). GPU work runs through `vpd_audit_2/modal_app.py`:

```
uv run modal run vpd_audit_2/modal_app.py::main --stage prepare   # fetch the model and the decomposition, build the first post's text sets
uv run modal run vpd_audit_2/modal_app.py::main --stage smoke     # plan 1 of the research log's smoke test; writes results/plan1_smoke/
```

## Provenance

`provenance/provenance.md` records what the authors' code and the released run actually did: which commit produced each run, how the evaluation adversary routes and starts, the step-size question behind the paper's adversarial-attack table, the training terms and their routing, the minimality term's exact form and constants, the number of processes, and where the validation texts come from. Every answer cites a file, commit, and lines, or a WandB run and field.

Beside it are the raw sources:
- `provenance/runs/<run_id>/`: each run's `final_config.yaml`, summary, file listing, and selected loss histories, with SHA-256 in `provenance/runs/sha256.txt`. They are fetched by `vpd_audit_2/wandb_provenance.py`.
- `provenance/data/data_check.json`: the data checks of `vpd_audit_2/data_check.py`.

`vpd_audit_2/run_config.py` asserts every value the provenance file records from the released run's raw configuration. Later code imports it, so a mismatch fails at import.

## Where Each Number in the Post Comes From

| Post section | Numbers | Source |
|---|---|---|
| Methods; Results; Limitations | The reference points (0.22 nats for a random source, 0.75 for the paper's 20-step search on our batches) and the shuffled copies' make-up; almost every search past 5 nats within 160 steps (shares 0.94 on the attack side, 0.96 on the held-out side); the 40-step searches' 2.1 nats on their own batches | `results/s5_lead/analysis/lead_tables.txt`: the 5-nat shares at line 138, the 2.1 (2.12) at line 58 |
| Methods; What This Means | The first post's numbers (0.34 for every mask at its label, 0.80 for pooling 64 tokens' worth, about 4,500 components) | The first post's repository, `third_party/vpd-audit` |
| Results; figure one | Share kept, the shuffled copies, 0.60, 75 of 80 | `results/s5_lead/analysis/lead_tables.txt` and `results/post/figure1_carry_over.csv` |
| Results; figure one | From 40 steps on, almost every carried-over source does more than the 0.75-nat reference: 75 of 80 at 40 steps, five at or below it | `results/post/figure1_carry_over.csv`, column `unseen_harm_mean`, the 80 rows whose `row` is `n40` |
| Results | The per-text numbers (97 percent of texts above 0.75 at 40 steps, 36 percent in the worst tenth, every text from 80 steps) | `results/s6_followups/spread.txt` |
| Results; figure two's caption | What the damaging sources are made of (about two fifths of components at 0, the rest fully on; most source values at 0 or 1) | `results/s6_followups/histogram.txt`, read with `results/s6_followups/CONVENTIONS.md` |
| The section on interference noise | Probe 1 | `results/s7_probe1/reading.txt` |
| The section on why training left these defects | The three-arm experiment | `results/s7_three_arm/reading.txt` |
| What This Means | The paper's 20-step adversary run on the first post's own texts (0.70 nats) | `results/s6_followups/rerun.txt` |
| Limitations | Where long searches end (2 to 61 nats across 200 searches; 26 nats on the pilot's eight batches against 34.5 on the main run's sixteen) | Each search's mean harm over its final 20 steps (steps 301 to 320): the lead run's 160 searches, 2.40 to 60.63 nats, `results/s5_lead/analysis/lead_tables.txt`, line 655; the starts test's 40, 4.73 to 45.22, `results/s6_starts/reading.txt`, line 81. The 26 and the 34.5: `results/s6_starts/reading.txt`, lines 7 and 9. The lead searches' harm at step 320 itself is also in the lead table, `own_A` and `own_H` at the setting `n320` in `results/s5_lead/lead/sealed/table_core.npz` (2.42 to 60.96) |

The post's three figures are drawn into `results/post/` by `vpd_audit_2/post_figure.py`, `post_schematic.py`, and `post_interference.py` (each run as `uv run python -m vpd_audit_2.<module>`), and the post shows `figure1_carry_over_62.png`, `figure2_carry_over_schematic_50.png`, and `figure3_interference_50.png`.
