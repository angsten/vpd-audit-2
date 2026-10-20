# Auditing the Released VPD Decomposition, Part Two: Technical Report

## 1. What Was Tested, and How to Read This Report

adVersarial Parameter Decomposition (VPD) [1] rewrites a model's weight matrices as sums of many rank-one components and trains a second network that labels every component, at every token of every input, with how much it is needed there. The paper's central property, mechanistic faithfulness, is that any setting of the components that keeps each one at or above its label should leave the output unchanged. The paper tests that property with an evaluation adversary: a gradient search for one setting of the components, applied at every token of a batch of texts, that does the most harm to the output while keeping every component at or above its label. The paper reports that the released decomposition is not robust to long searches, and sets that aside on two conditions: that what a long search finds is tuned to the texts it searched, and that a practitioner would not apply such a setting in practice.

This report stands behind the post [2], which tests the first condition on the decomposition the paper released for its four-layer, 67M-parameter language model, with the paper's own adversary and the paper's own measure of harm. The post's one result is that the settings the adversary finds carry over to text it never saw, across the whole range of search lengths from 20 to 320 steps, so the defects they exploit belong to the decomposition rather than to the searched texts. Three further measurements follow: what those settings are made of (Section 4); whether the components' contributions keep their sign on new text, which the paper's picture of cancelling noise says they should not (Sections 5.1 to 5.3); and why training is unlikely to have met these settings (Section 5.4). The first post [3] tested the labels under aggregation and deletion; its repository is a submodule here, and its numbers are quoted where the post compares with them.

The repository also holds the gates and the pilot of a second question, whether components labelled as needed are in fact needed, which the post does not report. That question was deferred to a later post: a count of needed labels that can be removed without harm asks a different question from a whole-pattern defect, and no line had been fixed in advance to read such a count against. Its result folders are listed in Section 7's table and appear nowhere else in this report.

**How to read this report.** Section 2 defines every object: the decomposition, the sources and the masks they set, the harm measure, the texts, and the adversary. Sections 3 to 5 give the measurements, each number with its file and line under `results/`. Section 6 gives the statistics as used, Section 7 why the code can be trusted, Section 8 the standing of every number in the post, and Section 9 the limitations. File paths are relative to the repository root. Where the post rounds a number, this report gives the exact value.

**Standing.** The carry-over test, its pass-or-fail rules and its intervals were fixed in `freeze/part1.md` before the lead run, and four amendments record what had been seen when each was written. The later measurements were designed after the lead result, with their possible readings written down before each ran. Every number and every claim in the post carries one standing, tabulated in Section 8:

- **Registered verdict:** read by a rule fixed in `freeze/` before the data existed, by analysis code committed before any result was read.
- **Reading fixed before the run:** a measurement designed after earlier results had been seen, whose possible readings were written down before it ran.
- **Descriptive:** read by no rule. The table says whether the quantity was named in advance or added after a reading.
- **Interpretation:** a sentence of the post that goes beyond what a reading licenses; the table says what the reading licensed.
- **Design:** a fixed feature of an experiment, such as a batch size or a step count.
- **From the paper** or **from the first post:** a number this repository did not measure.

**Where judgement was exercised after the data.** Five decisions were taken after some data had been seen. Each is recorded in a file a reader can open, and each section states what the other choice would have changed:

- Gate G1 stopped on its pre-registered 20-step check; one check was added, with a rule fixed before it ran, and the constant step size was adopted (Section 7, item 2).
- The interval rule's test on made-up data called for widening every row by a factor above the rule's cap; the author chose to widen nothing (Section 6.3, which gives all 23 verdicts as they would read widened).
- The run's cost cap was raised before the run, with the design unchanged (Section 7, item 5).
- Probe 1's registered reading was "do not agree"; we declined the sentence it licensed, and the post compares against a chance level the probe's specification first proposed and then replaced before the run (Section 5.3).
- The readings of Section 4 and the training experiment of Section 5.4 were designed after the lead result, with their readings fixed before each ran; where the post says more than a reading licenses, Section 8 marks the sentence as interpretation.

## 2. Setup

### 2.1 The Decomposition

The target model is the paper's four-layer decoder-only transformer (`LlamaSimpleMLP`): residual width 768, MLP width 3,072, six attention heads, a context of 512 tokens, and a vocabulary of 50,277 (`provenance/runs/t-9d2b8f02/final_config.yaml`, lines 16 to 28). The paper puts it at about 67 million parameters [1]. The decomposition is the released run `s-55ea3f9b` in the WandB project `goodfire/spd`, whose configuration is kept at `provenance/runs/s-55ea3f9b/final_config.yaml`.

VPD writes 24 weight matrices as sums of rank-one *components*: the four attention projections and the two MLP matrices in each of the four layers. Per layer there are 3,072 and 3,584 components in the two MLP matrices, 512 in each of the query and key projections, and 1,024 in each of the value and output projections, 38,912 in all (`vpd_audit_2/run_config.py`, lines 102 to 107 and 168). Each matrix also has a *delta component*, the part of its weights the rank-one components leave over. A *mask* scales each component's contribution at each token by a value in $[0, 1]$: 1 leaves the contribution as it is, and 0 removes it.

### 2.2 Labels, Sources, and Masks

**Labels.** The decomposition's labelling network gives every component $c$ a *label* $\ell_{t,c} \in [0, 1]$ at every token $t$ of a text. The label is the lowest value to which the component's mask may be turned down at that token without changing the output; the paper calls it the causal importance.

The labels are deterministic and clamped to $[0, 1]$, so a value at or below zero before the clamp gives exactly 0 (`provenance/provenance.md`, lines 252 to 254). They are computed from the original model on the unmasked text and are never recomputed under a mask. For each batch of the lead experiment they were computed once, on the whole batch under bfloat16 autocast as the authors' evaluation does. Every search and every source scored on that batch used that same tensor (`freeze/part1.md`, line 31).

**Sources.** The adversary does not set masks directly. It sets one *source* value $s_c \in [0, 1]$ per component, shared by every token of every text in the batch it searches. The mask at token $t$ is then

$$
m_{t,c} = \ell_{t,c} + s_c\,(1 - \ell_{t,c})
$$

(`vpd_audit_2/adversary.py`, lines 6 and 7). Read back for a component the text does not need ($\ell = 0$) and one it does ($\ell = 0.3$):

| Label $\ell$ | Source $s_c$ | Mask $m$ | In words |
|---|---|---|---|
| 0 | 0 | 0 | switched off |
| 0 | 1 | 1 | fully on |
| 0.3 | 0 | 0.3 | turned down to its label |
| 0.3 | 0.5 | 0.65 | halfway between its label and 1 |

A source of 0 holds a component *at its label*, and a source of 1 leaves it *fully on*. Every mask a source produces lies between the text's own label and 1. So every mask a source produces is one the labels permit, on the batch where the source was found and on any batch it is carried to.

A source has 38,936 entries: one per rank-one component and one per delta component (`freeze/amendment1_specs/table_and_run_spec.md`, line 20). The delta components have no label, and their mask is the raw source value (`provenance/provenance.md`, line 153).

Section 1's "setting" is a source. A source rounded to 0 or 1 is a *pattern*; the components a pattern holds at their labels are its *off set* (Section 4.1).

### 2.3 Harm

*Harm* is the KL divergence of the masked model's next-token distribution $Q_t$ from the original model's $P_t$, in nats:

$$
\mathrm{KL}_t = \sum_{v} P_t(v)\,\big[\log P_t(v) - \log Q_t(v)\big].
$$

This is the direction the authors' code computes (`provenance/provenance.md`, line 81). It is averaged over the 512 positions of each text and over a batch's 128 texts (`freeze/part1.md`, line 67; `freeze/amendment1_specs/table_and_run_spec.md`, line 19). The post calls harm "damage" or "divergence".

A batch's harm is the authors' own reduction: the sum over all $128 \times 512$ positions divided by their number (`table_and_run_spec.md`, line 56; `provenance/provenance.md`, lines 156 and 371). Every text has 512 positions, so this equals the mean of the per-text means. Logits are computed under bfloat16 autocast.

Two reference points recur. Every mask at its label gives 0.342 nats on the first post's texts (`results/plan1_smoke/smoke.json`, line 110). A random source, the start of every search, gives 0.22 on every batch (`results/s5_lead/analysis/lead_tables.txt`, line 30). Harm above that 0.22 is *added harm*. Section 7, item 1, gives two further checks.

### 2.4 The Texts

**The data.** The texts come from the authors' tokenized validation split of the Pile (`danbraunai/pile-uncopyrighted-tok-shuffled`, split `val`). It has 2,775,651 rows of 513 token ids, of which the model sees the first 512, and no document field (`provenance/provenance.md`, lines 289 to 292).

**Documents and sides.** We rebuilt the authors' tokenization and reproduced all 2,775,651 rows by hash, which recovers the document behind every row (`data/doc_recovery/recovery.json`, line 112; `provenance/provenance.md`, line 298). One committed manifest, `data/manifest/manifest.json`, then assigns every text to a pool:

- **Excluded:** the first post's texts and every row of their documents.
- **Two sides:** the remaining texts are split into an attack side and a held-out side that share no document (gate G5). The post calls the attack side "searched" and the held-out side "unseen".
- **Pools:** the lead experiment uses attack batches A1 to A16 and held-out batches H1 to H16, 128 texts each (`freeze/part1.md`, lines 53 and 54). Calibration batches C1 to C8 and the small pool CQ, on the attack side, served only the gates and the pilot (line 55).

**Near-duplicates.** A split by document cannot catch near-duplicate text. 11 of the 2,048 held-out texts share a 50-token span with an attack text (`data/manifest/heldout_span_overlap.json`, lines 3, 4, and 7). Every lead result is also recomputed without them (`freeze/part1.md`, line 174).

### 2.5 The Adversary

We run the paper's evaluation adversary through our own loop (Section 7, item 3). Like the paper's adversary, it:

- masks all 24 matrices at every position;
- keeps one source per component for the whole batch;
- optimizes the delta entries too;
- starts from a source drawn uniformly at random in $[0, 1)$.

(`provenance/provenance.md`, lines 151 to 154.) Each step moves every entry by 0.1 in the direction of the sign of the gradient of the batch's harm, then clamps it to $[0, 1]$ (line 156).

**Starts.** The adversary's 64 starting sources are saved in `results/s4_pilot/starts/starts_1_64.npz`. Starts 9 to 13 belong to the lead experiment (`freeze/part1.md`, lines 27 and 59).

**The step size.** Every search uses a constant step of 0.1, the schedule gate G1 chose (Section 7, item 2). A 20-step search is therefore the first 20 steps of a 320-step one, and one search is read at 20, 40, 80, 160, and 320 steps by saving its source at each (`freeze/part1.md`, lines 13, 29, and 69; `vpd_audit_2/lead_run.py`, lines 44 to 47).

**Breakout and the plateau.**
- **Breaking out.** A search *breaks out* when its harm, after staying near one to two nats for some tens of steps, climbs steeply to many nats. When that happens varies with start and batch. The files mark it as the first step at which a search's two-step mean harm reaches 5 nats (`results/s6_followups/CONVENTIONS.md`, line 9). In the pilot, the median search first reached 2, 5, and 10 nats at steps 44, 70, and 83 (`freeze/part1.md`, line 189).
- **The plateau.** A long search's level is stated as its *plateau*, its mean harm over steps 301 to 320 (`freeze/part1.md`, line 77).

**The delta components.** They carry no label, so no label constrains what the adversary does with them. A companion run held all 24 delta masks at 1 (A1 to A8 against H1 to H8, with the same starts; `freeze/part1.md`, line 61). It kept 0.97, 1.09, 0.92, 1.00, and 0.98 of the lead's carried added harm at 20, 40, 80, 160, and 320 steps (`results/s5_lead/analysis/lead_tables.txt`, lines 537, 549, 561, 573, and 585). The carried harm does not need them.

## 3. The Lead Experiment

### 3.1 Design

A search is as Section 2.5 defines it, and harm and added harm as Section 2.3. Each search runs for 320 steps and its source is recorded after 20, 40, 80, 160, and 320 steps; at 160 and 320 the source after step $n-1$ is also scored, as a check on sources that alternate between two values (`freeze/part1.md`, Section 3, "Source after $n$ steps"). The texts are the sixteen attack batches A1 to A16 and the sixteen held-out batches H1 to H16 of Section 2.4.

**Searches and cells.** Every batch on both sides was searched from the same five starting sources, starts 9 to 13 (`freeze/part1.md`, Section 6, "Frozen"): 80 attack searches and 80 held-out searches. Each attack search's recorded source was applied, unchanged, to all sixteen held-out batches and scored there. One attack batch, one held-out batch, and one start make a **cell**: 1,280 carried-over cells and 80 own-search cells at each step count (`results/s5_lead/analysis/lead_tables.txt`, line 28). The machine that scored a held-out batch (one container per side, Section 7, item 6) never received the token ids of an attack batch, so no source could be scored on the batch it was found on, and the tables' own checks confirm it (Section 7). The design, 16 batches per side with 5 starts, was chosen by a rule fixed before the pilot, from the pilot's variance components under a cost cap (`freeze/part1.md`, Section 6).

**Shuffled copies.** A component is **alive** when its mean label over the first post's 1,024 texts is above $10^{-6}$, and **never-needed** otherwise (`freeze/part1.md`, line 76; `results/s6_followups/CONVENTIONS.md`, line 5); Section 4's histogram calls the alive components **ever-needed**. Within each weight matrix the alive components are sorted into ten equal-count deciles of how often their label is above zero, the **usage bands**, with the never-needed components as an eleventh group. For each recorded source, eight copies were made in which the same values are dealt out at random among components of the same matrix and the same band; the 24 delta entries stay in place (`freeze/part1.md`, Section 3, "Shuffle strata"). A copy therefore turns down as many components as the original, in each matrix and at each level of usage, but different ones: a copy moves 41 to 44 percent of the alive entries by more than 0.5 (`lead_tables.txt`, lines 50, 80, 110, 140, 174). The copies were scored on the same held-out batches.

### 3.2 The Rules Fixed Before the Data

The rules below were fixed in `freeze/part1.md` before any deciding batch was touched, and the run was sealed and rehearsed as Section 7, items 4 to 6, describes. At each step count they ask three questions, each read from a 95 percent interval against a line fixed in advance (`freeze/part1.md`, Section 4):

- **Carries over.** The **carry-over ratio** $\tau_n$ is the carried sources' mean added harm on the held-out batches divided by the held-out batches' own searches' mean added harm, pooled over cells. The line is 0.2, a convention.
- **Large.** From 40 steps on, the carried harm minus the held-out batches' own 20-step harm, 0.75 nats, must lie above zero. That 0.75 is the **yardstick** below: the paper's "somewhat robust" level, measured on our texts.
- **Depends on the choice.** The **shuffled ratio** $\tau^{\mathrm{shuf}}_n$ is the carry-over ratio with the shuffled copies' mean harm in place of the start's harm in numerator and denominator; the line is 0.2.

A verdict is "yes" or "no" when the interval lies wholly on one side of its line and "undetermined" when it straddles it; a straddling 40- or 80-step entry stays undetermined and nothing outside the step table resolves it (`freeze/part1.md`, Section 4). The **step table** reads every search's source after 20, 40, 80, 160, and 320 steps: 14 verdicts, "large" not being asked at 20 steps. The **harm-level table** reads each search's source at the first step where its own two-step mean harm reaches 2, 5, or 10 nats, with the same three questions: 9 verdicts, which may support the step table but never replace it (`freeze/part1.md`, Section 4, "The stage table"). The sentence the post may use for each combination of step-table verdicts was fixed with the lines; for "large" and "depends on the choice" together it reads: "The search found a choice of components whose harm carries to text in general: by the paper's own test [...], a systematic defect" (`freeze/part1.md`, Section 4, the step table; the omitted parenthesis cites line numbers of a private copy of the paper).

### 3.3 The Two Tables: All 23 Verdicts Are Yes

The step table, scored on the held-out batches, with 95 percent intervals (`lead_tables.txt`, lines 27 to 181):

| Steps | Start (nats) | Shuffled copies (nats) | Carried over (nats) | Own search (nats) | Carries over: $\tau_n$ | Large: carried minus the 0.75 yardstick (nats) | Depends on the choice: $\tau^{\mathrm{shuf}}_n$ | `lead_tables.txt` lines |
|---|---|---|---|---|---|---|---|---|
| 20 | 0.22 | 0.32 | 0.60 | 0.75 | 0.72 [0.56, 0.87]: yes | not asked | 0.65 [0.48, 0.82]: yes | 30, 33, 34 |
| 40 | 0.22 | 0.31 | 1.77 | 2.24 | 0.77 [0.45, 1.09]: yes | +1.02 [0.46, 1.58]: yes | 0.76 [0.42, 1.09]: yes | 57, 59 to 61 |
| 80 | 0.22 | 0.31 | 16.78 | 16.39 | 1.02 [0.73, 1.32]: yes | +16.03 [6.60, 25.45]: yes | 1.02 [0.73, 1.32]: yes | 87, 89 to 91 |
| 160 | 0.22 | 0.30 | 28.77 | 32.07 | 0.90 [0.80, 0.99]: yes | +28.02 [22.15, 33.89]: yes | 0.90 [0.80, 0.99]: yes | 117, 119 to 121 |
| 320 | 0.22 | 0.30 | 32.79 | 34.72 | 0.94 [0.88, 1.01]: yes | +32.04 [27.24, 36.85]: yes | 0.94 [0.88, 1.01]: yes | 151, 153 to 155 |

The harm-level table (`lead_tables.txt`, lines 184 to 272):

| Own harm first reaches | Carried over (nats) | Own search (nats) | Carries over | Large (nats) | Depends on the choice | Searches never reaching the level, attack and held-out | `lead_tables.txt` lines |
|---|---|---|---|---|---|---|---|
| 2 nats | 1.77 | 2.13 | 0.81 [0.72, 0.90]: yes | +1.02 [0.80, 1.25]: yes | 0.80 [0.71, 0.90]: yes | 0 and 0 | 190, 193 to 195 |
| 5 nats | 4.82 | 5.49 | 0.87 [0.82, 0.93]: yes | +4.08 [3.77, 4.38]: yes | 0.87 [0.81, 0.93]: yes | 1 and 1 | 220, 223 to 225 |
| 10 nats | 10.26 | 11.58 | 0.88 [0.83, 0.93]: yes | +9.52 [8.88, 10.16]: yes | 0.88 [0.83, 0.93]: yes | 2 and 3 | 250, 253 to 255 |

Every step row from 40 steps on gives the combination "large" and "depends on the choice", whose fixed sentence names a systematic defect by the paper's own test (`lead_tables.txt`, lines 67 to 68 and the corresponding lines of each later row); every harm level gives the same two verdicts, though no sentence is defined for that table (`freeze/part1.md`, Section 4, "The stage table"). At 20 steps the two ratio verdicts hold, "carries over" and "depends on the choice", but "large" is not asked there, so the post's "from twenty steps on" rests on carry-over alone, and the fixed sentence naming a systematic defect exists from 40 steps on.

The carry-over ratio above 1 at 80 steps, and the width of the 40- and 80-step intervals, come from the timing of breakout. At those step counts some searches have broken out and others have not, on each side separately: by step 80, 79 percent of the attack searches and 78 percent of the held-out searches had passed 5 nats (line 108), and the attack batches' own searches did 18.17 nats against the held-out batches' 16.39 (lines 87 to 88). The carried sources bring the attack side's timing with them, while the ratio's denominator carries the held-out side's, so $\tau$ at 80 steps is 16.56 over 16.17 nats of added harm (line 90). Section 6.5 gives the identity that ties $\tau$ to the retention of Section 3.4 through the ratio of the two sides' own-search harm.

### 3.4 Retention

**Retention** is a source's carried-over added harm, averaged over the sixteen held-out batches, divided by its added harm on the batch it was found on. The **pooled retention** over the 80 sources is the sum of the numerators over the sum of the denominators (`freeze/amendment1_specs/output_and_reading_spec.md`, Section 4.3, line 240). The post calls it the "share kept". It was named before the data as a description beside the carry-over ratio, and it changes no verdict (`freeze/part1.md`, Section 8; `freeze/amendment1.md`, Section 9, item 6). Its values, with 95 percent intervals (`lead_tables.txt`, lines 43, 73, 103, 133, 167):

| Steps | 20 | 40 | 80 | 160 | 320 |
|---|---|---|---|---|---|
| Pooled retention | 0.78 [0.68, 0.88] | 0.82 [0.74, 0.89] | 0.92 [0.90, 0.94] | 0.94 [0.92, 0.96] | 0.95 [0.94, 0.96] |

The post's "fifth" and "tenth" are $1 - 0.78$ and $1 - 0.92$. Retention compares a source with itself, so the timing of breakout cancels within it, and the file prints it split by whether the search had passed 5 nats of own harm by the scored step (`lead_tables.txt`, lines 41 to 42, 71 to 72, 101 to 102, 131 to 132, 165 to 166):

| Steps | Searches past 5 nats: number, pooled retention | Searches not past 5 nats: number, pooled retention |
|---|---|---|
| 20 | 0 | 80, 0.78 |
| 40 | 3, 0.74 | 77, 0.83 |
| 80 | 63, 0.93 | 17, 0.76 |
| 160 | 75, 0.94 | 5, 0.41 |
| 320 | 79, 0.95 | 1, 0.11 |

The few searches that have not broken out by 160 or 320 steps keep little; from 80 steps on, the searches that have keep 0.93 or more. Section 6.6 gives the retention at 80 steps start by start.

### 3.5 A Carried 20-Step Source Does 0.60 Nats; From 40 Steps Almost Every One Beats 0.75

A source carried from a 20-step search on another batch does 0.60 nats on average on the held-out batches, against the 0.75 their own 20-step searches do (`lead_tables.txt`, line 30). The post's "from 40 steps on, almost every carried source exceeds the 0.75 nat reference" is a count over the 80 carried sources at each step count, from `results/post/figure1_carry_over.csv`, column `unseen_harm_mean`, each source's mean over the sixteen held-out batches:

| Steps | Sources above 0.75 nats | The rows at or below it (line: value) |
|---|---|---|
| 40 | 75 of 80 | 83: 0.69; 85: 0.56; 119: 0.69; 153: 0.49; 154: 0.47 (the `n40` rows are lines 82 to 161) |
| 80 | 77 of 80 | 165: 0.69; 199: 0.68; 234: 0.52 (lines 162 to 241) |
| 160 | 78 of 80 | 279: 0.71; 314: 0.52 (lines 242 to 321) |
| 320 | 79 of 80 | 383: 0.66 (lines 322 to 401) |

These counts are read by no rule.

### 3.6 Which Components, Not How Many

The shuffled copies do 0.30 to 0.32 nats at every step count (lines 30, 57, 87, 117, 151), a tenth of a nat above the random start, against carried sources from 0.60 to 32.79 nats; they never reach the 0.75 yardstick (lines 66, 96, 126, 160). Of the carried sources' added harm, the copies reproduce 26 percent at 20 steps, 6 percent at 40, and 1 percent or less from 80 steps on (lines 38, 65, 95, 125, 159, "composition share" 0.74, 0.94, 0.99, 1.00, 1.00). From 40 steps on, "carries over" and "depends on the choice" are one finding, since the copies do so little that the two ratios coincide.

### 3.7 At 40 and 80 Steps, Where the Paper Is Silent

The paper does not say what step size produced its 40- to 320-step rows (Section 9), so our searches at those step counts may not be the paper's. The harm-level table, which reads each source by the harm it has done rather than the steps it took, is the comparison that does not depend on that: the paper's 80-step value, 3.84 nats, lies between the 2- and 5-nat rows, where the scored sources' own harm is 2.13 and 5.49 and every verdict is yes; its 40-step value, 1.35, lies between the 20-step row and the 2-nat row, both yes on "carries over" and "depends on the choice", with "large" not asked at 20 steps. One verdict, "large" at 80 steps, depends on the decision to widen nothing; Section 6.3 gives the arithmetic.

### 3.8 The Spread Over Texts

After the lead result, we read whether a carried source harms a few texts or most as description with no line, under a convention committed before the analysis ran (`results/s6_followups/CONVENTIONS.md`, Section 6). For each of the 1,280 cells at a step count, the 128 per-text harms saved by the run give the share of texts above 0.75 nats, the harm of the 13th-lowest text, and the share of the added harm carried by the 13 most-harmed texts (0.10 if even); the table gives the median over cells with the 10th and 90th percentiles (`results/s6_followups/spread.txt`):

| Steps | Share of texts above 0.75 nats | Harm of the 13th-lowest text (nats) | Share of harm on the 13 most-harmed | `spread.txt` lines |
|---|---|---|---|---|
| 20 | 0.10 (0.02 to 0.30) | 0.41 (0.31 to 0.49) | 0.15 (0.14 to 0.20) | 11 to 13 |
| 40 | 0.97 (0.36 to 1.00) | 1.00 (0.39 to 1.60) | 0.16 (0.14 to 0.40) | 36 to 38 |
| 80 | 1.00 (0.84 to 1.00) | 9.93 (0.60 to 23.88) | 0.14 (0.13 to 0.27) | 61 to 63 |
| 160 | 1.00 (0.98 to 1.00) | 22.86 (2.06 to 32.04) | 0.13 (0.12 to 0.18) | 86 to 88 |
| 320 | 1.00 (1.00 to 1.00) | 26.87 (9.63 to 35.68) | 0.12 (0.12 to 0.14) | 111 to 113 |

A shuffled copy puts 0.14 of its harm on the top tenth of texts (lines 25 and 75), so from 80 steps a carried source's harm is spread over texts as evenly as a shuffled copy's. The 0.75 here is the mean over the sixteen held-out batches, not each batch's own value. A text's harm is a mean over its 512 positions, so these numbers say nothing about how the harm falls within a text.

## 4. What the Harmful Sources Are Made Of

Section 3 shows that a source found on one batch keeps most of its harm on text it never saw. This section describes what such a source is, using only what the lead experiment saved. Unless stated otherwise, each analysis scores the 80 sources found on the attack batches at a given step count, carried to held-out batches. Each analysis's convention is in `results/s6_followups/CONVENTIONS.md`, which was committed before any GPU analysis ran, with one addendum after the histogram (line 94). Two thresholds, one half for the token-level split and 90 percent for the ranked count, were fixed in `freeze/part1.md` (line 113) before the lead data existed. The two readings against them are therefore registered verdicts. Everything else in this section is descriptive.

### 4.1 An On-or-Off Pattern

A source has one value $s_c \in [0, 1]$ per component $c$. At a position where component $c$ has label $\ell$, its mask is $m = \ell + s_c (1 - \ell)$:
- $s_c = 0$ holds the mask at the label, which switches the component off wherever its label is 0;
- $s_c = 1$ leaves the component fully on.

The values the adversary finds sit almost entirely at the two ends (`results/s6_followups/histogram.txt`; descriptive, named in advance):

| Group | Steps | Exactly 0 | Exactly 1 | `histogram.txt` line |
|---|---|---|---|---|
| never-needed | 80 | 0.37 | 0.50 | 23 |
| ever-needed | 80 | 0.40 | 0.47 | 25 |
| never-needed | 320 | 0.36 | 0.53 | 37 |
| ever-needed | 320 | 0.38 | 0.46 | 39 |

These are attack-side searches; the held-out side matches to within 0.01 (lines 74, 76, 88, 90). Most of the remaining values sit one step, 0.1, from an end.

Rounding every value to 0 or 1 keeps all of a carried source's harm above the random start: 1.01 to 1.11 of it at every step count (`results/s6_followups/controls.txt` lines 33 to 37). Rounding the start itself raises its harm from 0.22 to 0.32 nats (line 32).

A harmful source is therefore, in effect, an **off set** of components below one half, held at their labels, with every other component fully on. At 320 steps the off set averages 16,412 components and the rest average 22,500 of 38,912 (57.8 percent). At 80 steps the averages are 17,099 and 21,813 (`results/s7_probe1/reading.txt` lines 25 and 42). The post's "about two fifths" and "about 60 percent fully on" are these figures.

### 4.2 The Harm Needs Both Kinds of Position

A source can act where a component's label is zero, by switching it off, or where the label is positive, by turning the component down to its label. The token-level split applies the source at only one kind of position, with every other value at its random starting value. It reads each part's share of the carried harm against the registered threshold of one half (`results/s6_followups/split.txt`):
- **At 80 steps:** the zero-label part keeps 0.43 [0.38, 0.47] and the positive-label part 0.00. Both are below half, which reads as "the harm needs both kinds of position together" (lines 15 to 18).
- **At 40, 160 and 320 steps:** the zero-label part's interval reaches one half, so the reading is undetermined (lines 10 to 13 and 20 to 28).
- **At 20 steps:** the reading is "the components the labels call free" (lines 5 to 8), but with so little harm above the start the split is fragile. A variant added after the readings holds every other value at 1 instead of its starting value; in it the positive-label part alone does 1.25 times the whole source's added harm (`results/s6_followups/variants.txt` line 16). What the split attributes to each kind of position depends on what the rest is held at, so at this scale it cannot say where a pattern acts.

### 4.3 No Small Set Carries the Harm

The ranked count orders a source's entries by their estimated contribution and keeps the top $k$ (`results/s6_followups/exploited.txt`; a registered verdict against the threshold of 90 percent). At 320 steps:
- the top 10,000 entries keep 0.02 of the added harm and the top 20,000 keep 0.56 (line 58);
- a random set of entries of the same size keeps 0.00 at every size short of the whole (line 59);
- the smallest $k$ that keeps 90 percent is the whole source, pooled and from every start (lines 68 and 69);
- the follow-up test did not trigger, since its trigger needed the top 3,000 to keep at least 0.90 and they keep 0.00 (line 72).

A dose-response, added after the readings at the author's request (`results/s6_followups/dose_rounded.txt`), switches off a random fraction of the rounded off set and leaves everything else on. At 320 steps:

| Fraction of the off set switched off | 0.75 | 0.9 | 1 |
|---|---|---|---|
| Harm, nats (`dose_rounded.txt` line 29) | 1.52 | 14.03 | 33.52 |
| Fraction of the whole pattern's added harm (`dose_rounded.txt` line 21) | 0.04 | 0.42 | 1.02 |

The harm arrives almost entirely with the last quarter of the pattern. The share of the added harm depends on the length of the search: with 0.75 of the off set switched off it is 0.660 at 20 steps, 0.298 at 40, 0.046 at 80, 0.041 at 160, and 0.040 at 320 (`dose_rounded.txt`, lines 17 to 21), so the concentration in the last quarter is a property of the longer searches.

### 4.4 Many Patterns, Not One

Two sources *agree* on an entry when both are below one half or both are at or above it. Agreement beyond chance is $\kappa = (a - a_0)/(1 - a_0)$, where $a$ is the observed agreement and $a_0$ the chance level. At 320 steps (`results/s6_followups/agreement.txt`; descriptive, named in advance):
- sources from different starts on different batches agree at $\kappa = 0.052$ (line 17);
- sources from different starts on the same batch agree at $\kappa = 0.068$ (line 13);
- sources from the same start agree more, $\kappa = 0.199$ (line 9), an echo of their shared starting values.

Different searches thus find nearly unrelated patterns, and each carries over to held-out text (Section 3).

### 4.5 The First Post's Comparison, on the Same Texts

The first post compared its pooled explanations with the paper's 20-step adversary, but the paper had measured that adversary on other texts. The pooled explanations turn fully on every component needed at any of 64 positions drawn from other texts, with the rest held at the text's own labels. Their harm was 0.80 nats, against the paper's 0.83.

To make the comparison on the same texts, we ran the paper's 20-step adversary on the first post's 1,024 texts, under a clause fixed in `freeze/part1.md` (its Section 7, line 163): "about as much" if $0.80/A$ lies within a factor of 1.25 of 1. The result is $A = 0.696$ nats, 95 percent interval 0.637 to 0.756 (`results/s6_followups/rerun.txt` lines 5 and 9). That gives $0.80/A = 1.149$, which reads "about as much" (line 21), a registered verdict.

Rebuilt on new text, the pooled explanations again do 0.80 nats. Of that, 0.46 is above the 0.34 that holding every mask at its label already does (`results/s6_followups/controls.txt` lines 12 and 15).

The pooled masking has the adversary's form, fully on for some components and at the label for the rest, but on a much smaller set:
- the pooled masking turns fully on about 4,544 components by the first post's count, and 4,393 (4,197 to 4,753) in the rebuild (line 15);
- the adversary's source keeps 22,500 of 38,912 at or above one half at 320 steps (Section 4.1).

## 5. The Contributions Keep Their Sign, and Why Training Left These Defects

### 5.1 What the Toy Picture Assumes

The paper sets aside interference-noise failures as tuned to particular inputs. That reasoning needs one premise the paper does not state: the sign of each unneeded component's contribution must change from text to text. If it did not, a set the adversary sorted by sign on one text would stay sorted on the next. Probe 1 measures that premise.

### 5.2 A First-Order Push per Component, Matching Exact Moves in Sign

Probe 1 uses the 80 attack-side sources at 320 steps, each rounded to its on-or-off pattern. For a text $x$, let $\hat\Delta(x, t)$ be the pattern's shift of the logits at position $t$, centred over the vocabulary and scaled to unit length. A component's **push** is the first-order change in the logits along that shift when its mask moves from 1 to its label, taken at the intact model:

$$
p_c(x) = \sum_t \left\langle \frac{\partial z(x, t)}{\partial a_c}, \hat\Delta(x, t) \right\rangle ,
$$

where $z$ are the logits and $a_c$ scales the component's move (`vpd_audit_2/probe1.py` docstring, lines 10 to 21). The sign is positive when switching the component off moves the output along the pattern's shift. The first-order signs were checked against exact one-at-a-time moves on 1,600 component-text pairs; outside the smallest decile of push size the signs match for 0.9528 of them, with a Spearman correlation of 0.9175 (`results/s7_probe1/reading.txt` line 6).

The statistic compares two signs for each component in the off set $O$:
- the sign of its push summed over the 128 texts of the batch the source was found on;
- the sign of its push on each held-out text.

Agreement is weighted by the size of the push:

$$
g(y) = \frac{\sum_{c \in O} |p_c(y)| \, [\operatorname{sign} p_c(y) = \operatorname{sign} P_c(A)]}{\sum_{c \in O} |p_c(y)|}.
$$

Here the bracket is 1 when the two signs match and 0 otherwise, and $P_c(A)$ is the summed push on the attack batch $A$ (`vpd_audit_2/probe1_read.py` docstring, lines 15 to 17). The statistic is pooled over the 128 texts of each of the 1,280 pairings of a source with a held-out batch (line 22).

The chance level fixed before the run was the same statistic over **matched kept components**: components the source left on, drawn to match the off set within each weight matrix and usage band, in eight draws (lines 18 to 21). The reading was fixed on $\kappa = (\bar g - \bar g_0)/(1 - \bar g_0)$, with $\bar g$ the off set's mean agreement and $\bar g_0$ the matched kept components' (lines 27 to 30): an interval reaching zero reads "do not agree". The probe's specification had its own numbered amendments, fixed before it ran. A gate, the probe's amendment 5, asked whether the off set's signs agree more within the attack batch than across to held-out text; if not, the reading licensed the sentence that the pushes are specific to each input. The chance level above replaced an earlier one before the run, and Section 5.3 sets out the sequence.

### 5.3 The Switched-Off Components Keep Their Sign No More Often Than the Rest, and Both Far More Often Than Reshuffled Signs

| Quantity | Value | Standing | Where |
|---|---|---|---|
| Off set's sign agreement, weighted by size | 0.7430 | reading fixed before the run | `reading.txt` line 9 |
| Matched kept components' agreement (the chance level fixed in advance) | 0.7434 | reading fixed before the run | `reading.txt` line 9 |
| $\kappa$ against that chance level | $-0.0015\ [-0.0222,\ 0.0193]$: "do not agree" | reading fixed before the run | `reading.txt` lines 10 and 11 |
| Within-batch $\kappa$, each attack text against the summed push of the other 127 (the probe's amendment 5, the gate of Section 5.2) | $-0.0053\ [-0.0265,\ 0.0158]$: at or below the cross-batch upper end, so the gate held and the licensed sentence is "first-order pushes are specific to each input while the damage still carries over" | reading fixed before the run | `reading.txt` lines 12, 14 and 21; the rule, `probe1_read.py` docstring lines 39 to 40, and lines 89 to 99 and 217 to 224 |
| Off set's sign balance on the attack batch (positive share of its push mass) | mean 0.6553, range 0.5683 to 0.8294 | descriptive, named in advance | `reading.txt` line 16 |
| The specification's original chance level: the off set's attack-batch signs permuted within weight matrix and usage band, eight times | 0.5455; $\kappa$ $0.4346\ [0.4121,\ 0.4572]$, "partly agree" under the registered thresholds | descriptive, added after the reading | `reading.txt` line 13; `probe1_read.py` docstring lines 47 to 51, and lines 81 to 83 and 141 to 152 |
| Share of off-set push mass along the shift, held-out texts | 0.5803 against 0.5364 for matched kept; difference 0.0439 [0.0279, 0.0599] | descriptive, added after the reading | `reading.txt` line 18 |
| First-order sum as a share of the shift, held-out (attack batch) | 0.2651 (0.2353) | descriptive, named in advance | `reading.txt` line 22 |

The comparison the post quotes is not the one the registered reading used. Three steps connect them:
1. **Before the run, the probe's amendment 2 replaced the specification's original chance level with the matched kept components** (`probe1_read.py` docstring, line 18). The amendment's reason is recorded in the same docstring, in the sentence that follows. The concern was degeneracy: if the search had left the off set's attack-batch signs mostly one way, the permutation would change nothing, and agreement beyond chance would read near zero by construction. No public file states what agreement the kept components were expected to show. The code names their agreement the chance level, which treats it as the agreement of signs that owe nothing to the adversary's choice.
2. **We declined the licence of the registered reading.** The kept components keep their sign as often as the off set does, 0.7434 against 0.7430. A $\kappa$ of zero against them therefore says that the adversary's selection adds nothing to how stable the signs are, not that the signs are specific to each input. The gate does not separate the two either: within the attack batch both sets agree at about 0.745 (0.7445 against 0.7459, `reading.txt` line 21).
3. **The original chance level was brought back as description, after the reading** (line 13: "POST HOC ... Not the reading"). The degeneracy that the probe's amendment 2 guarded against did not occur. The off set's attack-batch signs are not mostly one way: their balance averages 0.6553 and reaches at most 0.8294.

The post's footnote 1 says the left-on components keep their sign just as often, so the sign is largely a property of the component. It quotes a registered number, 0.7434, and adds a post-hoc interpretation.

Two more facts bound the claim:
- **The adversary sorts by sign only slightly.** About 58 percent of the off set's push mass points along the shift, against about 54 percent for comparable left-on components. That is a tilt, not the toy's clean split.
- **The first-order pushes account for only about a quarter of the shift.** The rest comes from interactions that a first-order probe cannot see.

The probe therefore tests the premise of the toy picture, not the mechanism of the harm.

**Figure 3's rows (d) and (e)** are schematic. They do not show individual measured components, and stand for two measured facts:
- **Signs.** In row (e) one of the four switched-off cells flips sign, against the size-weighted 0.743 that keep their sign.
- **Net arrows.** Row (e)'s net arrow is 0.95 of row (d)'s: the pooled retention at 320 steps, 0.9468 [0.9353, 0.9583] (`results/s5_lead/analysis/lead_tables.txt` line 792). Retention is a ratio of added KL divergence, not of logit-shift length.

### 5.4 Why Training Left These Defects

VPD trained its decomposition against a *persistent* adversary, one whose source values carry from batch to batch with three ascent steps on each, for 400,000 batches. In training's own log that adversary stays at or below 1.814 nats after the first 40,000 steps (`results/s7_three_arm/reading.txt` line 29). Yet the evaluation adversary finds a pattern that carries over within tens of steps from a random start.

To test whether too little signal per step explains the miss, we ran the authors' own training adversary, `PersistentPGDState`, unchanged and at its released settings, against the released decomposition held frozen. Only the scope of a source varied (`vpd_audit_2/three_arm.py` docstring, lines 6 to 10):
- arm 1: one per text slot and position, as released, $64 \times 512$ per component;
- arm 2: one per text;
- arm 3: one for the batch, as the evaluation adversary uses.

Each arm masked all 24 weight matrices at every step, as the released configuration specifies: its random-subset routing of the matrices is set for the stochastic reconstruction loss only, and none is set for the persistent adversary's loss (`provenance/runs/s-55ea3f9b/final_config.yaml`), although the paper's training-recipe appendix says both reconstruction losses use it [1].

Our step matched the authors' training code bit for bit, with 0 mismatches in 1,272,135,829 gradient entries (`results/s7_three_arm/reading.txt` line 6). At the start, 0.456 of arm 1's gradient entries sat below Adam's epsilon, so those values barely moved (`results/s7_three_arm/gate.json` line 40).

An arm **breaks out** when its harm on a fresh batch, before any ascent and averaged over two consecutive batches, reaches 5 nats. The readings were fixed before the run (`vpd_audit_2/three_arm_read.py` docstring, lines 18 to 26); the one that applies is the file's "reading 2" (`results/s7_three_arm/reading.txt`):
- **Arm 1:**
  - It did not break out in 1,230 batches (seed 1) or 1,000 (seed 2), which is 10.0 and 11.4 times the 123 and 88 batches at which arm 3 broke out (lines 9 and 10).
  - Its harm on fresh batches rose from a mean of 0.2318 over the first 200 batches to 0.2634 and 0.2609 over the last 200.
  - Training's own loss on the batch being stepped on, taken after two of the three ascents, rose from 0.4225 to 0.4713 and 0.4662 (lines 23 to 26). The post's "0.23 to 0.26" and "0.47" are these figures.
- **Arm 2:** it broke out at batches 374 and 325 (line 11).
- **Arm 3:** it broke out at batches 123 and 88 (lines 19 and 20).

**What reading 2 licenses, and what the post adds.** Reading 2's fixed wording is: "within N batches, arm 1 did not reach the pattern that the yardstick reached at batch b" (the docstring's "yardstick" is arm 3, not Section 3.2's 0.75 nats). The wording for arm 2 asks "whether sharing alone reaches it", and the docstring adds that "the post never says 'cannot reach'" (`three_arm_read.py` docstring, lines 23 to 25; filled in at `reading.txt` lines 9 and 10). The post's sentence, "This shows that pooling the gradient over more positions per step is what helps find systematically damaging source patterns", goes one step further and attributes the difference to the pooling. The design supports that attribution, since the three arms differ only in the scope of a source, but the reading does not state it. Its standing is interpretation, and so is the post's next sentence, that too little signal per step could on its own explain why training never met these patterns.

Four cautions bound the conclusion:
- **Scale.** We ran 1,000 batches against training's 400,000, so "cannot reach" is never claimed (line 9). Whether the decomposition also moved away from its adversary during training, or trapped it, is not ruled out.
- **The two seeds share their texts** and differ only in starting values. With about 1.3 billion values in arm 1, its two seeds are closer to one run than to two.
- **No resumed start.** The released checkpoint holds no persistent sources, so arm 1 started from scratch (line 41).
- **The newer recipe was not run.** The authors' newer recipe [4], per-document sharing with a pool of particles, is arm 4, and it was not run (line 43).

## 6. Statistics as Used

### 6.1 What Is Measured, and Paired

Every measurement is one forward pass of the masked model over one batch of 128 texts of 512 tokens. It records the KL divergence from the original model's next-token distribution at every position, averaged over the batch's 65,536 positions, in nats. Per-text means are saved beside every batch mean; per-position harm is not (`freeze/amendment1.md`, Section 6). 

Every quantity is paired within the held-out batch. **Added harm** is harm minus the start's harm on the same batch, so a batch that is easier to harm does not inflate a ratio; the start's harm is 0.22 nats on every batch (line 30). The three signed statistics at a row are (`freeze/amendment1.md`, lines 42 and 61)

$$
\tau = \frac{\bar X - \mathrm{KL}_0}{\bar Y - \mathrm{KL}_0}, \qquad
\tau^{\mathrm{shuf}} = \frac{\bar X - \bar S}{\bar Y - \bar S}, \qquad
\text{large} = \bar X - \bar Y^{20},
$$

where $\bar X$ is the mean carried-over harm, $\bar Y$ the mean harm of the held-out batches' own searches, $\bar S$ the mean harm of the shuffled copies, $\bar Y^{20}$ the mean harm of the held-out batches' own 20-step searches, and $\mathrm{KL}_0$ the start's harm. *Worked example*, the plan's own illustration (`freeze/amendment1.md`, line 196): start 0.24, own search 0.83, carried 0.70, shuffled 0.60 give $\tau = 0.46/0.59 = 0.78$ and $\tau^{\mathrm{shuf}} = 0.10/0.23 = 0.43$. The first says that 78 percent of the own search's added harm is still there on held-out text; the second, that of the margin by which the own search beats a shuffled copy, 43 percent carries over.

### 6.2 What Is Resampled, and What Is Held Fixed

**The sampling unit is the batch.** Write $K = 16$ for the number of batches on each side and $n_s = 5$ for the number of starts. Each cell is first turned into a linearized value $W_{ijs} = (N_{ijs} - \hat\theta D_{ijs})/\hat D$, with $N$ and $D$ the cell's numerator and denominator and $\hat\theta$, $\hat D$ fixed from the whole table (`freeze/amendment1_specs/interval_spec.md`, Section 4.1); for a plain mean such as "large", $W$ is the cell's own value. The five starts are averaged into a 16 by 16 table, and 10,000 replicates redraw 16 attack and 16 held-out batches independently with replacement, Owen's pigeonhole bootstrap [5], the variance scaled by $K/(K-1)$.

**What resampling batches cannot see is a start's effect on every batch alike,** since all 32 batches share the same five starts. That term is added from a three-way analysis of variance of the cells: $\hat\sigma_c^2$ is the estimated variance of the start effect, the part of a cell's variation that a start contributes to every batch alike, and $V_c = \hat\sigma_c^2 / n_s$ is the variance that effect leaves in a mean over the five starts. Its degrees of freedom are Welch–Satterthwaite, bounded to $[1, n_s - 1]$ (`freeze/part1.md`, Section 5; `interval_spec.md`, Section 4.3). The start term's share of the variance is printed beside every interval: 0.21 to 0.24 at 20 steps, 0.52 for "large" at 40, 0.85 for "large" at 80, and 0.69 for "large" at 160 and 320 (lines 52, 82, 112, 142, 176), where the effective degrees of freedom fall to 2.1 to 4.5. An interval from batches alone would be 3.7 times too narrow for "large" at 80 steps (its percentile interval $[13.34, 18.46]$ against the deciding $[6.60, 25.45]$, lines 111 and 89).

**Held fixed:** the five starts; the eight shuffled copies per source (one seeded draw each); the texts within each batch; and the 24 delta components, which every shuffle leaves in place (`freeze/amendment1.md`, fault 3.5).

### 6.3 The Interval Rule, Its Test, and the Multipliers

The interval is $\hat\theta \pm \lambda_r\, t_{0.975,\nu}\sqrt{V_{\mathrm{PB}} + V_c}$, with $V_{\mathrm{PB}}$ the corrected bootstrap variance, $\nu$ the combined degrees of freedom, and $\lambda_r$ a per-row multiplier (`interval_spec.md`, Section 4.4). Before any deciding run, the rule was tested on made-up experiments built from the pilot's 64 real searches with invented carry-over whose truth was known by enumeration: 13 core scenarios and 8 stress scenarios, 2,000 experiments each, a case failing below 92.5 percent coverage or, with the truth on a line, with more than 3.75 percent of intervals wholly on one side of it (`freeze/amendment1.md`, Section 5). Two checks with exact answers passed: coverage 0.9505 against 0.95, and a bootstrap variance 2.9316 times the true variance against 2.9375 (`results/s5_madeup/summary.md`, lines 9 and 10). Of 299 core cases, 50 failed, 37 of them "large" (`freeze/amendment3.md`, line 29).

The rule's repair, a multiplier on each row's half-width, computed 1.90, 1.65, 1.85, 2.15, and 2.15 at 20 to 320 steps and 2.55, 2.60, and 3.20 at 2, 5, and 10 nats (`summary.md`, lines 326 to 333), every one above the cap of 1.5 that sends a row to the author. **The author chose to widen nothing**, and $\lambda_r = 1$ in every row (`freeze/amendment1_multipliers.md`, lines 7 to 14; `freeze/amendment3.md`, Section 3). The reason: the shortfall was confined to samples holding no batch whose own 20-step search runs well above the rest, the test's "early-breakout" kind, which the rule had named before the test as a limit to state rather than repair. In such samples the yardstick $\bar Y^{20}$ reads about 0.08 nats low and the "large" interval is narrow; the test's coverage of "large" was 0.527 with no such batch on the held-out side and 0.928 or better with one or more (`amendment3.md`, line 51; the rounded wording at lines 76 and 77). On the real data the held-out side holds two: their own 20-step searches did 0.92 and 0.94 nats of added harm, against 0.43 to 0.56 for the other fourteen (line 24). The lowest end of any "large" interval is 0.46 nats (line 59, the 40-step row), nearly six times the bias. Every printed interval records "Unwidened: identical (no widening recorded)" (lines 52, 82, 112, 142, 176).

**What the declined multipliers would have changed.** The table below applies each row's computed multiplier to the half-width of every verdict interval, taken unrounded from the interval-details block of `lead_tables.txt`, and reads the widened interval against its line: "large" is yes when its lower end is above 0; the two ratios are yes when the lower end is at or above 0.2, and undetermined when the interval straddles the line (`freeze/amendment1.md`, Section 2.1). A widened interval is $\hat\theta \pm \lambda_r h$, with $h$ the unwidened half-width.

| Row | Verdict | Estimate | Unwidened interval | $\lambda_r$ | Widened interval | Reads | `lead_tables.txt` line |
|---|---|---|---|---|---|---|---|
| 20 steps | carries over | 0.7175 | $[0.5649, 0.8702]$ | 1.90 | $[0.428, 1.008]$ | yes | 660 |
| 20 steps | depends on the choice | 0.6525 | $[0.4846, 0.8204]$ | 1.90 | $[0.334, 0.972]$ | yes | 663 |
| 40 steps | large | 1.0176 | $[0.4590, 1.5762]$ | 1.65 | $[0.096, 1.939]$ | yes | 681 |
| 40 steps | carries over | 0.7671 | $[0.4465, 1.0878]$ | 1.65 | $[0.238, 1.296]$ | yes | 684 |
| 40 steps | depends on the choice | 0.7556 | $[0.4223, 1.0890]$ | 1.65 | $[0.206, 1.306]$ | yes, by 0.006 | 687 |
| 80 steps | large | 16.0289 | $[6.6042, 25.4536]$ | 1.85 | $[-1.41, 33.46]$ | **undetermined** | 708 |
| 80 steps | carries over | 1.0243 | $[0.7291, 1.3195]$ | 1.85 | $[0.478, 1.570]$ | yes | 711 |
| 80 steps | depends on the choice | 1.0244 | $[0.7276, 1.3212]$ | 1.85 | $[0.475, 1.574]$ | yes | 714 |
| 160 steps | large | 28.0168 | $[22.1462, 33.8874]$ | 2.15 | $[15.40, 40.64]$ | yes | 735 |
| 160 steps | carries over | 0.8962 | $[0.7981, 0.9943]$ | 2.15 | $[0.685, 1.107]$ | yes | 738 |
| 160 steps | depends on the choice | 0.8959 | $[0.7975, 0.9942]$ | 2.15 | $[0.684, 1.107]$ | yes | 741 |
| 320 steps | large | 32.0424 | $[27.2390, 36.8459]$ | 2.15 | $[21.72, 42.37]$ | yes | 768 |
| 320 steps | carries over | 0.9440 | $[0.8767, 1.0114]$ | 2.15 | $[0.799, 1.089]$ | yes | 771 |
| 320 steps | depends on the choice | 0.9439 | $[0.8764, 1.0114]$ | 2.15 | $[0.799, 1.089]$ | yes | 774 |
| 2 nats | large | 1.0246 | $[0.8017, 1.2476]$ | 2.55 | $[0.456, 1.593]$ | yes | 801 |
| 2 nats | carries over | 0.8123 | $[0.7233, 0.9012]$ | 2.55 | $[0.586, 1.039]$ | yes | 804 |
| 2 nats | depends on the choice | 0.8026 | $[0.7096, 0.8955]$ | 2.55 | $[0.566, 1.040]$ | yes | 807 |
| 5 nats | large | 4.0759 | $[3.7694, 4.3824]$ | 2.60 | $[3.279, 4.873]$ | yes | 828 |
| 5 nats | carries over | 0.8728 | $[0.8157, 0.9300]$ | 2.60 | $[0.724, 1.021]$ | yes | 831 |
| 5 nats | depends on the choice | 0.8707 | $[0.8127, 0.9287]$ | 2.60 | $[0.720, 1.022]$ | yes | 834 |
| 10 nats | large | 9.5171 | $[8.8767, 10.1575]$ | 3.20 | $[7.468, 11.566]$ | yes | 855 |
| 10 nats | carries over | 0.8838 | $[0.8338, 0.9338]$ | 3.20 | $[0.724, 1.044]$ | yes | 858 |
| 10 nats | depends on the choice | 0.8830 | $[0.8326, 0.9333]$ | 3.20 | $[0.722, 1.044]$ | yes | 861 |

Twenty-two of the 23 verdicts survive the declined multipliers. The one that does not is "large" at 80 steps, whose widened interval straddles zero; with both ratios still yes there, the step table's 80-step entry would read "undetermined between Large and Not large, but carries over" (`freeze/amendment1.md`, Section 2.1), and the registered sentence naming a systematic defect, which needs "large" and "depends on the choice" together, would not be printed at 80 steps. It would still be printed at 160 and 320 steps, where the widened "large" intervals clear zero by 15 and 22 nats. At 40 steps all three verdicts stay yes, two by little. "Large" clears zero by 0.10 nats. The shuffled ratio's lower end, 0.206, clears its line by 0.006, about one and a half times the Monte Carlo error of a widened half-width of that size (0.7 percent of it; `interval_spec.md`, Section 4.2). A repeat of the resampling could erase that margin. The nine harm-level verdicts survive with room to spare, the widened "large" intervals reaching down to 0.46, 3.28, and 7.47 nats; they carry no fixed sentence of their own and count as confirmation only (`freeze/part1.md`, line 110). Section 3.7 names the one verdict that depends on the decision; this table is the arithmetic behind it.

### 6.4 Levels, Lines, and the 23 Verdicts

The 23 verdicts of Section 3.3 are each read at 95 percent, with no correction for their number (`freeze/amendment1.md`, line 236). They are not independent: every row scores the same 80 sources from the same five starts. All 23 are yes (Section 3.3). The closest to their lines are the three at 40 steps and "large" at 80 steps, each 1.7 to 1.8 half-widths away: for instance $\tau$ at 40 steps is 0.77 $[0.45, 1.09]$, 0.57 above its line with a half-width of 0.32 (line 60). The two 20-step ratios probably read about 8 percent low: the attack side's own 20-step searches did 0.71 nats against the held-out side's 0.75 (lines 30 and 31; added harm 0.49 against 0.53), the early-breakout batches of Section 6.3, here on the attack side, and the sources it hands over carry correspondingly less. That bias runs against the finding.

### 6.5 The Retention and the Signed Ratio

The retention of Section 3.4 divides each source's carried-over added harm by its added harm on its own batch; the signed ratio $\tau$ divides instead by the held-out batches' own searches. So at 40 and 80 steps, where breakout timing, which differs between the two sides, adds separate noise to numerator and denominator, $\tau$'s interval is the wider (Section 3.3). The two estimate the same population quantity, since the manifest splits the two sides at random from one corpus, and they are tied by an identity: $\hat\tau$ equals the retention times the ratio of the attack side's mean own-search added harm to the held-out side's, whose true value is 1. The retention is the steadier of the two and is the quantity the post's sentence describes; every verdict rests on $\tau$.

### 6.6 What the Intervals Do Not Cover

- **Runs that are not independent.** Both sides' 160 searches share five starts. The start term rests on at most four degrees of freedom, drives the width from 80 steps on, and no interval was computed for a single start; by start alone the retention at 80 steps is 0.9215, 0.9222, 0.9213, 0.8925, and 0.9377 (line 733), so no verdict rides on one start.
- **A rare kind of batch.** Sixteen batches per side cannot resample a kind they do not hold. In the test's stress scenarios the retention's coverage fell as low as 0.78 with carried cells that jump to 40 nats and 0.86 with a rare batch kind that carries over differently (`results/s5_madeup/summary.md`, lines 552 and 483); stated, not repaired.
- **The test's carried-over model is invented.** The made-up data built carried harm from the pilot's own-batch searches, not the run's, and `interval_spec.md`, line 364, says of the test that it "can show under-coverage caused by real own-search tails and by the scenarios' structure, not by structure in real carried-over cells that nobody has imagined".
- **The shuffled ratio's denominator.** Its interval is reliable only where $\bar Y - \bar S$ is far from zero; the distance is printed beside every reading, 7.9 standard errors at 20 steps and 4.8 at 80 (lines 37 and 94), where the test's coverage in the matching bin was 0.9288 and 0.9119 (`summary.md`, lines 632 and 636). The plain margins carry the point without a ratio: carried sources beat their shuffled copies by 0.28 nats $[0.25, 0.32]$ at 20 steps and 16.47 $[6.99, 25.96]$ at 80 (lines 36 and 93).

## 7. Why the Code Can Be Trusted

A measurement that contradicts a paper is only as good as the instrument that made it. Each item below names a check, what it found, and the committed file where it can be read. Items 1 to 3 ask whether the code computes what the authors' code computes. Items 4 to 7 ask whether the rules and the run could have been shaped by the results. Item 8 says what the checks do not cover.

**1. The decomposition, configuration, and process count are the released run's.**
- **Configuration.** `vpd_audit_2/run_config.py` asserts the released configuration's SHA-256 on import, and every value the provenance file records from it. Examples: 400,000 training steps, batches of 64, and an evaluation adversary of 20 steps at step 0.1 shared across the batch (lines 26, 32, 56 to 77, 131, and 159 to 172).
- **Code.** The run was produced by the authors' commit `85c6b70`, whose adversary, routing, and mask code match the paper's release tag `74146b5` [4] up to a refactor with the same arithmetic (`provenance/provenance.md`, lines 11, 13, and 38).
- **Known numbers.** A first run reproduced them:
  - every mask at 1 gives $-1.6 \times 10^{-9}$ nats;
  - every mask at its label gives 0.342, against 0.34 in the first post;
  - there are 203.4 labels above zero per token, against the paper's 205;
  - every matrix zeroed gives 67.10 nats, against the paper's 67.24.

  (`results/plan1_smoke/smoke.json`, lines 98, 110, 125, and 140.)
- **Process count.** Training ran on 16 processes, each holding 4 of the batch's 64 texts. We rebuilt the authors' final evaluation batch as their loader would for 8, 16, and 32 processes. Only the 16-process batch reproduces their logged per-matrix label counts: a largest relative difference of 0.00043, against 0.026 and 0.073 for the others (`results/plan2_world_size/metrics.json`, lines 338, 398, and 458).

**2. Gate G1, the step size.**
- **The question.**
  - The released run configures one adversary: 20 steps at step 0.1 (`provenance/provenance.md`, line 170).
  - Nothing from the paper's time records how its 40- to 320-step rows were run (line 169).
  - The paper's own heuristic points to a step of $2/n$ for $n$ steps (line 182).
  - The two schedules coincide at 20 steps and differ beyond.
- **Check A.** Our 20-step search from eight starts on the rebuilt final evaluation batch gives a geometric mean of 0.679 nats, against the logged 0.652 (`results/plan2_g1/readings.json`, lines 34 and 35).
- **The two schedules, on batches C1 to C8.**
  - With step $2/n$, the geometric mean stays between 0.74 and 0.80 nats from 40 to 320 steps, while the paper's rows rise from 1.35 to 40.2.
  - With the constant step it reaches 21.5 and 23.1 nats at 160 and 320 steps (same file, lines 55 to 238, as mean log harm).
  - From 40 steps on, step $2/n$ is excluded outright: at 40 steps its 99 percent prediction interval is 0.656 to 0.824 nats, against the paper's 1.354 (lines 178 to 185).
  - The choice of schedule therefore rests on the longer budgets.
- **The stop and the amendment.**
  - **The original rule.** The pre-registered check at 20 steps asked whether the paper's 0.828 lies within a 99 percent prediction interval built from our eight one-start runs. That interval was 0.613 to 0.779 nats, from a log standard deviation of 0.032 (lines 55 to 62). It failed, and the gate stopped (lines 346 and 347).
  - **The amended rule.** After the stop, one added check, interpreted by a rule fixed before it ran, measured the spread over starts. That spread is a pooled within-batch log standard deviation of 0.1875, 5.8 times the one first used (`results/plan2_g1/start_spread.json`, lines 49 to 54). It widened the interval to 0.344 to 1.385 nats around the same centre of 0.691. That interval contains the paper's 0.83, and the constant step was adopted (lines 55 to 60 and 69).
  - **The amended check is weak.** An interval spanning a factor of four could hardly have excluded anything. And at 20 steps the two schedules are the same search (`readings.json`, lines 45 to 53 and 148 to 156 hold the same eight harms), so the check never bore on the choice between them. It says only that the paper's 20-step value lies within the spread our setup produces.
- **Why this does not touch the post.**
  - Every verdict compares searches made at one fixed step size, in one configuration. How well the schedule matches the paper's longer rows therefore moves no ratio.
  - The post compares with the paper only at 20 steps, where Check A matched the logged 0.652 to within 4 percent.
  - The post quotes the paper's 0.83 beside our own 0.75 rather than claiming to reproduce it.

**3. Gate G2: our loop is the authors' loop.**
- On all 128 texts of batch C1, in float32 over 20 steps, sources, harms, and gradients are bitwise equal at every step (`results/s4_plan1_g2/g2.json`, lines 3, 5, 8, 32, 57, and 796).
- Diagnostic D1 extends the equality to bfloat16 over 320 steps (`results/s4_plan4/d1.json`, lines 2 to 14).
- The lead experiment uses exactly that path, in one configuration: the whole batch in one pass, bfloat16 autocast, strict deterministic algorithms, and one B200 GPU per search (`freeze/part1.md`, line 29).

Gates G3 and G4 concern the precision of single labels, which matters for the needed-labels question and not for the post (`results/s4_plan1_g3/g3.json`; `results/plan2_labels/g4.json`). The lead experiment computes its labels as the authors' evaluation does and is unaffected (`freeze/part1.md`, line 44). Gate G5, the document split, is Section 2.4.

**4. The rules were fixed before the data.**
- `freeze/part1.md` was signed on 5 October 2026 (line 34), before any source had been scored on a batch other than its own (line 9). It fixes the design, the three questions and their lines, the interval, and the starts.
- **Input hashes.** It records the SHA-256 of the manifest and the starts (lines 26 and 27), and the launcher checks them (`vpd_audit_2/lead_run.py`, lines 60 to 62).
- **Freeze-file hashes.** `freeze/SHA256SUMS` and `tests/test_freeze.py` pin the hashes of all twelve frozen files (lines 31 to 48 and 61). The files were reworded for publication after the runs and their pins regenerated once; only wording changed (lines 15 to 18).

**5. Four amendments, each committed before the step it governs.** None moves a line, threshold, sample size, seed, pool, or start.
- **Amendment 1** (5 October). Four independent reviews of the signed rules found nine gaps, each given a convention, and eleven faults. Each fault is recorded, with its signed reading left alone and a description printed beside it (`freeze/amendment1.md`, Sections 2 and 3, lines 51 to 168 and 178 to 248).
- **Amendment 2** (5 October). One invented factor in the made-up-data generator would have decided the test of the intervals. It was removed, and the original version kept as a second run (`freeze/amendment2.md`, lines 3 and 7).
- **Amendment 3** (6 October). Every row's computed widening exceeded the cap of 1.5, so by the rule each went to the author, who chose to widen nothing (`freeze/amendment3.md`, lines 7 and 9). The analysis records the multipliers as 1 (`lead_tables.txt`, line 14).
- **Amendment 4** (6 October). The first rehearsal's automatic check projected \$103.96, within the \$105 cap (`results/s5_lead/rehearsal/rehearsal.json`, lines 402 to 406). Counted with scoring passes at their upper bound and the measured start-up times, the projection was \$105.20 to \$107.30, so the run waited for the author, who raised the cap to \$150 with the design unchanged (`freeze/amendment4.md`, lines 7, 9, 37, and 41).

**6. The run: sealed, rehearsed, one side per container.**
- **Sealing.** No carry-over number was printed until the analysis script, committed in advance, had run on the complete tables (`freeze/part1.md`, line 196; `results/s5_lead/lead/sealed/DO_NOT_OPEN.md`, lines 1 to 5). The analysis refuses sealed files that do not match their receipts (`vpd_audit_2/lead_analysis.py`, line 195).
- **One side per container.** A container holding a held-out batch never receives an attack batch's token ids, and the reverse (`freeze/amendment1_specs/table_and_run_spec.md`, line 165). Each score records the hash of the ids it was computed on (lines 76 and 118).
- **Rehearsals.** Two rehearsals on calibration batches reproduced the pilot's stored searches (`results/s5_lead/rehearsal/rehearsal.json`, lines 163 to 165; `rehearsal_2/rehearsal.json`, lines 16 and 17). The second rehearsal also scored each batch on itself on purpose: the wrong-batch guards fired and stopped it (lines 2, 27 to 30, and 45).

**7. Tests and guards.**
- The repository's tests run with a plain `pytest` (`tests/`): 643 tests. On a fresh clone of this copy, 638 pass and 5 skip: one needs the private history, and four need run files kept only on the machine that ran them.
- The analysis entry point and the launchers refuse to run in this copy, with one stated exception (`README.md`, line 9).

**8. What the checks do not cover.**
- **The paper's table.** It is not checked that the paper's table came from this checkpoint. Its 20-step value of 0.8280 matches no logged step of the released run (`provenance/provenance.md`, line 174).
- **One long search for many.** It is not checked that one long search stands for others. A single long search is a wide draw: two starts that differ by the smallest representable amount can end far apart (Section 9).

**The results folders.** Each folder under `results/` is listed with what it holds and where this report uses it. Folders the post does not use are marked.

| Folder | What it holds | Used in |
|---|---|---|
| `plan1_smoke/` | The first run's reference numbers | 2.3; 7, item 1 |
| `plan2_world_size/` | Rebuilt final evaluation batches for 8, 16, and 32 processes | 7, item 1 (not in the post) |
| `plan2_g1/` | Gate G1's readings, start spread, and trajectories | 7, item 2 |
| `plan2_labels/` | Gate G4 and the fresh float32 labels | 7, item 3; the deferred question of Section 1 (not in the post) |
| `s4_plan1_g2/` | Gate G2 | 7, item 3 |
| `s4_plan1_g3/` | Gate G3, with a float64 diagnostic | 7, item 3; the deferred question (not in the post) |
| `s4_plan1_prices/` | Every label's price under 16-process training, and its checks | The deferred question of Section 1 (not in the post) |
| `s4_plan4/` | Long-search diagnostics D1 to D5 | 7, item 3 (D1); 9 |
| `s4_pilot/` | The pilot: part A sized the lead experiment, part B the deferred question (sealed); the 64 starts | 2.5; 3.1 |
| `s5_madeup/` | The made-up-data test of the intervals | 6.3; 7, item 5 |
| `s5_lead/` | The lead experiment: sealed tables, receipts, ledger, rehearsals, and `analysis/lead_tables.txt` | 3; 6; 7, items 5 and 6; 8 |
| `s6_starts/` | The starts test: why long searches ended higher than in the pilot | 9 |
| `s6_followups/` | Follow-up readings and the conventions fixed before them | 3.8; 4 |
| `s7_probe1/` | The sign-agreement probe | 5.1 to 5.3 |
| `s7_three_arm/` | The training adversary against the frozen decomposition, in three sharing scopes | 5.4 |
| `post/` | The three figures and their data | The post's figures; 3.5 |
| Other folders | `plan2_sister_runs/`: the provenance of the paper's table. `s4_plan5/`: a scan of the logs for non-deterministic operations. `s6_plan3/`, `s6_dose/`, `s6_dose_rounded/`: the run records behind the readings in `s6_followups/` | Not cited (not in the post) |

## 8. The Standing of Every Number in the Post

Every row carries one of the standings Section 1 defines. For descriptive rows, "named in advance" marks a quantity the freeze file or a committed convention named before it was computed, and "added after the reading" one computed after a planned reading had been made. The first column keeps the post's words; line numbers are the files' on the public commit.

| Post claim | Exact value | Standing | File, line |
|---|---|---|---|
| a four-layer, 67M-parameter language model | 67M parameters, four layers | from the paper | the paper, "Introduction" |
| the paper's table: 0.83 nats at 20 steps, 40.2 at 320; its 40-step row 1.35 | 0.8280, 1.3539, 3.8381, 25.2560, 40.2200 | from the paper | the paper, "The decomposition model behaves similarly to the target model" |
| zeroing every weight matrix: about 67 nats | 67.2449 | from the paper | the paper, footnote to the same table |
| the training adversary takes three steps per batch; 400,000 batches | $n_{\text{adv}} = 3$; 400,000 steps at batch size 64 | from the paper | the paper, "Adversarial reconstruction loss"; "Training Details and Hyperparameters" |
| batches of 128 texts of 512 tokens; sixteen searched and sixteen unseen; five searches per batch; 80 searches; sources at 20, 40, 80, 160, 320 steps; eight shuffled copies | as stated | design | `freeze/part1.md`, Sections 3 and 6 |
| a random source causes 0.22 nats | 0.22 | descriptive | `results/s5_lead/analysis/lead_tables.txt`, line 30 |
| the paper's 20-step search on our unseen batches: 0.75 nats (the dashed line) | 0.75 held-out side; 0.71 attack side | descriptive, named in advance as the yardstick of the registered "large" verdicts (`freeze/part1.md`, Section 4) | `lead_tables.txt`, lines 30 to 31, 57 |
| seen and unseen damage within 20% at every step count (figure one's caption) | held-out over attack, raw: 0.60/0.71, 1.77/2.12, 16.78/18.17, 28.77/30.60, 32.79/34.62, that is 0.85, 0.83, 0.92, 0.94, 0.95 | descriptive | `lead_tables.txt`, lines 30 to 31, 57 to 58, 87 to 88, 117 to 118, 151 to 152 |
| the dots hug the diagonal: most of the divergence carries over | carry-over ratio 0.72 [0.56, 0.87], 0.77 [0.45, 1.09], 1.02 [0.73, 1.32], 0.90 [0.80, 0.99], 0.94 [0.88, 1.01], all "carries over" | registered verdict, five of 23 | `lead_tables.txt`, lines 33, 60, 90, 120, 154 |
| from twenty steps on, the defects systematically transfer (TL;DR) | at 20 steps the registered verdicts are "carries over", 0.72 [0.56, 0.87], and "depends on the choice", 0.65 [0.48, 0.82]; "large" is not asked at 20 steps, so the fixed sentence naming a systematic defect exists from 40 steps on | registered verdict, two of 23 at 20 steps; the sentence from 40 steps | `lead_tables.txt`, lines 32 to 34; `freeze/part1.md`, Section 4 |
| share kept 78% at 20 steps (95 percent interval 0.68 to 0.88), 82% at 40, 92% at 80, about 95% at 160 and 320 | pooled retention 0.78 [0.68, 0.88], 0.82 [0.74, 0.89], 0.92 [0.90, 0.94], 0.94 [0.92, 0.96], 0.95 [0.94, 0.96] | descriptive, named in advance (`freeze/part1.md`, Section 8); the interval changes no verdict | `lead_tables.txt`, lines 43, 73, 103, 133, 167 |
| about a fifth at 20 steps and under a tenth from 80 steps on | $1 - 0.78$, $1 - 0.92$ | descriptive | same |
| a carried 20-step source does 0.60 nats on average | 0.60 | descriptive | `lead_tables.txt`, line 30 |
| from 40 steps on, almost every carried source exceeds 0.75 nats | 75, 77, 78, and 79 of 80 at 40, 80, 160, and 320 steps | descriptive | `results/post/figure1_carry_over.csv`, column `unseen_harm_mean`; the rows at or below 0.75 are lines 83, 85, 119, 153, 154 (40 steps), 165, 199, 234 (80), 279, 314 (160), 383 (320) |
| the carried damage is large from 40 steps on | carried minus the yardstick: +1.02 [0.46, 1.58], +16.03 [6.60, 25.45], +28.02 [22.15, 33.89], +32.04 [27.24, 36.85], all "large" | registered verdict, four of 23; the 80-step one would be undetermined under the declined multipliers (Section 6.3) | `lead_tables.txt`, lines 59, 89, 119, 153; the multipliers, `freeze/amendment1_multipliers.md`, lines 8 to 9 |
| at 40 steps 97 percent of a batch's texts end above 0.75; every text from 80 steps | median share of texts 0.97 (10th to 90th percentile 0.36 to 1.00) at 40; 1.00 (0.84 to 1.00) at 80 | descriptive, named in advance (convention with no line, `results/s6_followups/CONVENTIONS.md`, Section 6) | `results/s6_followups/spread.txt`, lines 36, 61 |
| by the paper's own definition, systematic defects | the fixed sentence for "large" with "depends on the choice" | registered verdict | `freeze/part1.md`, Section 4; `lead_tables.txt`, lines 67 to 68 |
| the shuffled copies cause 0.30 to 0.32 nats at every step count | 0.32, 0.31, 0.31, 0.30, 0.30 | descriptive, beside the registered shuffled ratio: 0.65 [0.48, 0.82], 0.76 [0.42, 1.09], 1.02 [0.73, 1.32], 0.90 [0.80, 0.99], 0.94 [0.88, 1.01], all "depends on the choice", five of 23 | `lead_tables.txt`, lines 30, 57, 87, 117, 151; the ratios at lines 34, 61, 91, 121, 155 |
| which components, not how many | composition share 0.74, 0.94, 0.99, 1.00, 1.00 | descriptive | `lead_tables.txt`, lines 38, 65, 95, 125, 159 |
| a search finds these patterns from any starting point (a sentence the post no longer carries; kept for the record) | retention at 80 steps, start by start: 0.9215, 0.9222, 0.9213, 0.8925, 0.9377; searches past 5 nats by 160 steps, 0.94 and 0.96 | descriptive | `lead_tables.txt`, lines 733, 138 |
| sources found from different random starts on different batches agree on which components to turn down only slightly more often than chance (an agreement beyond chance of 0.05) | at 320 steps, 29,648 pairs: agreement 0.555 against an independence chance level of 0.531, $\kappa = 0.052$; at 20 and 40 steps $\kappa$ is 0.083 and 0.067 | descriptive, named in advance (the conventions file's Section 7, `results/s6_followups/CONVENTIONS.md`, line 51; Section 4.4) | `results/s6_followups/agreement.txt`, lines 17, 140, and 164 |
| turning down a random three quarters of the components in a pattern causes only 4% of its damage, and nearly all of the damage arrives with the last quarter | kept share with 0.75 of the off set switched off: 0.040 at 320 steps; 0.660, 0.298, 0.046, and 0.041 at 20, 40, 80, and 160; with 0.9 switched off, 0.424 at 320 | descriptive, added after the readings at the author's request (Section 4.3); it holds from 80 steps on and not at 20 or 40 | `results/s6_followups/dose_rounded.txt`, lines 17 to 21 |
| most of the values the adversary finds end up at exactly 0 or 1 (figure two's caption) | shares at exactly 0 plus exactly 1: 0.87 and 0.87 at 80 steps (never-needed and ever-needed components), 0.89 and 0.84 at 320 | descriptive | `results/s6_followups/histogram.txt`, lines 23, 25, 37, 39 |
| the harm-level table (not quoted in the post, but behind "both short and long searches") | nine verdicts, all yes | registered verdict, confirmatory, nine of 23 | `lead_tables.txt`, lines 193 to 195, 223 to 225, 253 to 255 |
| 74% of the switched-off components keep their sign, weighted by size | 0.7430 | reading fixed before the run: the chance level fixed in advance was the matched left-on components' agreement, 0.7434, giving agreement beyond chance $-0.0015$ $[-0.0222, 0.0193]$, read "do not agree"; the within-batch gate held, so the reading licensed the input-specific sentence, and that licence was declined (Section 5.3). The post gives 74 against the reshuffled 55 and the left-on 74 in footnote 1; the registered reading is in the file and in Section 5.3 | `results/s7_probe1/reading.txt`, lines 9 to 12, 14, 21 |
| reshuffled signs would agree about 55% of the time | 0.5455; agreement beyond it 0.4346 [0.4121, 0.4572], "partly agree" | descriptive, added after the reading; it is the specification's original chance level, replaced before the run by the probe's amendment 2 and brought back as description after the registered reading (Section 5.3) | `reading.txt`, line 13; `vpd_audit_2/probe1_read.py`, lines 18 and 47 to 51 |
| the components left on keep their sign just as often, also 74% (footnote 1) | 0.7434 | reading fixed before the run (it was the planned chance level) | `reading.txt`, line 9 |
| footnote 1's inference: "this stability is not created by the adversary's selection ... the sign is, to a large extent, a property of the component itself" | the two agreements, 0.7430 and 0.7434, against the reshuffled 0.5455 | interpretation, added after the reading; no reading of the probe licenses a sentence about what the sign is a property of (Section 5.3) | `reading.txt`, lines 9 and 13 |
| 80 sources at 320 steps; a text the adversary never saw | 1,280 held-out cells, each a source on a batch of 128 texts, the agreement pooled over all 128 | design | `reading.txt`, line 8; `vpd_audit_2/probe1_read.py`, line 22 |
| the net arrow in (e) is 95 percent as large as in (d) (figure three's caption) | pooled retention at 320 steps, 0.95 [0.94, 0.96], over all 80 sources (0.9468 [0.9353, 0.9583] unrounded, `lead_tables.txt`, line 792) | descriptive, named in advance | `lead_tables.txt`, lines 167 and 792 |
| the net contribution depends on interactions, not only the first-order contributions | first-order sum over the off set is 0.2651 of the pattern's shift on held-out text (0.2353 on the attack batch) | descriptive, named in advance (a planned description of probe 1) | `reading.txt`, line 22 |
| "We observe the same for the sources found at 80 steps" (the sign agreement) | 0.7428 against the matched left-on components' 0.7425; $\kappa = 0.0009$ $[-0.0273, 0.0291]$ | descriptive; the probe's reading file marks the 80-step row "description only; nothing is licensed by this row" | `results/s7_probe1/reading.txt`, lines 29 to 32 |
| the one-at-a-time contributions add up to only about a quarter of the pattern's total output shift at 320 steps, and about two fifths at 80 | 0.2651; 0.4140 | descriptive, named in advance (a planned description of probe 1) | `results/s7_probe1/reading.txt`, lines 22 and 39 |
| pooling 64 tokens' worth of other texts' explanations: 0.80 nats over 1,024 texts; 0.34 from the text's own explanation; about 4,500 components fully on | 0.7993; 0.3417; 4,544 | from the first post | `third_party/vpd-audit/REPORT.md`, Section 8.1 |
| the paper's 20-step adversary on those same texts: 0.70 nats, "about as much" as 0.80 | 0.696 [0.637, 0.756] with the delta components searched; 0.690 [0.631, 0.749] held at 0; $0.80/A = 1.149$, within the factor of 1.25 fixed in advance | registered verdict: the clause was frozen in `freeze/part1.md`, Section 7, before the lead data | `results/s6_followups/rerun.txt`, lines 5, 9, 13, 21 |
| the adversary leaves about 60% of the 38,912 components fully on | the kept set at 320 steps, mean over the 80 sources, is 22,499.8 of 38,912, that is 0.578. Entries at or above one half: 0.590 of the never-needed and 0.544 of the ever-needed components; exactly 1: 0.53 and 0.46. The post's "fully on" is the rounded pattern | descriptive | `results/s7_probe1/reading.txt`, line 25; `results/s6_followups/histogram.txt`, lines 37 and 39; the rounding convention, `CONVENTIONS.md`, Section 3 |
| the evaluation adversary finds a carrying-over pattern within 20 steps; one doing 5 nats in almost every search within 160 | pooled retention 0.78 at 20 steps; searches past 5 nats by 160 steps, 0.94 attack, 0.96 held-out | descriptive, named in advance (the shares past levels, `freeze/part1.md`, Section 8) | `lead_tables.txt`, lines 43, 138 |
| per position: no damaging pattern in 1,000 batches; fresh-batch divergence crept from 0.23 to 0.26; 0.47 on the batch just optimized on | never, in 1,230 and 1,000 batches; means of the first and last 200 batches 0.2318 to 0.2634 and 0.2609 (fresh), 0.4225 to 0.4713 and 0.4662 (own) | reading fixed before the run ("Reading 2"); the trends are descriptive | `results/s7_three_arm/reading.txt`, lines 9 to 10, 15 to 16, 23 to 26 |
| per document: 374 and 325 batches; across the batch: 123 and 88 | as stated, on the governing series (349 and 316, 123 and 87 on training's own loss series) | reading fixed before the run | `reading.txt`, lines 11, 17 to 20 |
| sharing per document took about three times as many batches to find a damaging pattern as sharing across the whole batch | 374 and 325 against 123 and 88, ratios 3.0 and 3.7 | descriptive, a comparison of two readings fixed before the run | `results/s7_three_arm/reading.txt`, lines 11 and 17 to 20 |
| "This suggests that pooling the gradient over more positions per step is what helps find systematically damaging source patterns" | reading 2's licensed wording is "within N batches, arm 1 did not reach the pattern that the yardstick reached at batch b", with arm 2 saying "whether sharing alone reaches it"; the design supports the attribution, since the arms differ only in the scope of a source, but the reading does not state it (Section 5.4) | interpretation; the reading licenses the breakout comparison, not the cause, so the post's "suggests" is what it supports | `vpd_audit_2/three_arm_read.py`, lines 23 to 25; `results/s7_three_arm/reading.txt`, lines 9 to 11 |
| "too little signal per step could, on its own, explain why training never encountered these problematic patterns" | the same reading; it names neither the signal per step nor an explanation, and "the post never says 'cannot reach'", training having run 400,000 batches against the 1,000 here | interpretation, hedged; the reading licenses the comparison over 1,000 batches, not an explanation of training (Section 5.4) | `three_arm_read.py`, lines 23 to 27; `reading.txt`, line 9 |
| the rule: 5 nats averaged over two consecutive fresh batches, before any steps on them | as stated | reading fixed before the run (the rule itself) | `reading.txt`, lines 3 to 4 |
| 1,000 batches of 64 texts, two starts; the released checkpoint holds no adversarial values (footnote 2) | 1,000 (1,230 for one start); 159 keys, no persistent sources | design; the checkpoint check is descriptive | `reading.txt`, lines 1 to 2, 41 |
| the authors' newer code shares each value across a document, keeps a pool of persistent adversarial values, and doubles the source learning rate | "Each document samples one particle and uses its per-site vectors at every position"; pool size 2,064, source learning rate 0.02 | from the paper's authors' repository (`docs/skill.md` at commit 5ffc73d), not a measurement here | the repository file the post links |
| Lee Sharkey's diagnosis: the procedure for finding strong adversarial ablations "isn't getting good enough coverage of ablation-space" | verbatim | from the comment thread [7], not a measurement here | the comment the post links [7] |
| the authors' newer decomposition is "significantly improved, though still imperfect" and "more robust to the evaluation adversary", and is not publicly released | by the authors' write-up [6], every harm of the first audit is smaller: hard delete 0.16 nats against 1.28, union +0.10 against +0.46, self-aggregation +0.30 against +1.03, all still above the 0.05-nat bar; the batch-shared search raises its KL by 1.2 nats after 80 steps and 1.3 after 1,280, over a CI-masked 0.21, where the paper's table has the released decomposition at 3.84 after 80 steps and 40.2 after 320 | from the authors' write-up, not a measurement here; the newer run is not in the authors' public WandB project, where the released run's configuration downloads (checked 19 October 2026) | the write-up [6], Table 1, the section "How the new decomposition fares on each claim" (the CI-masked 0.21), and its last section ("What remains open") |
| our searches do 2.1 nats at 40 steps | 2.12 on the attack batches (2.24 on the held-out batches) | descriptive | `lead_tables.txt`, lines 58, 57 |

## 9. Limitations

- **One released decomposition of one small model,** and only text of the kind the paper evaluates on. Nothing here was applied to other seeds, sizes, kinds of text, or the authors' newer training recipe.
- **A long search's level is one draw from a wide distribution.** Eight runs of the authors' own loop from starts differing by one bfloat16 unit in one entry ended at plateaus of 30.08 to 52.34 nats on one batch (`results/s4_plan4/d4_void_case.json`, lines 10 and 16), against 28.43 unperturbed (`results/s4_plan4/d4.json`, line 5360). The geometric mean of about 22 nats at 320 steps from gate G1's trajectories (`results/plan2_g1/readings.json`; Section 7, item 2) served only to choose the schedule; it is not quoted as a typical level, and none is. Over the 200 searches from the run's five starts, each search's mean harm over steps 301 to 320 runs from 2.40 to 60.63 nats for the run's 160 (`results/s5_lead/analysis/lead_tables.txt`, line 655; 31 percent at or above the paper's 40.2 after step 320, line 656) and from 4.73 to 45.22 for the pilot batches' 40 (`results/s6_starts/reading.txt`, line 81).
- **The paper's step size for its longer rows is unknown.** Section 7, item 2, gives the test that excludes the paper's own rule of thumb for the longer rows and why the post compares directly only with the paper's 20-step value.
- **The run's long searches did more harm than the pilot's, for a reason not found.** On the pilot's eight batches the run's five starts ended at 26.06 nats of added harm at 320 steps, where the pilot's eight starts ended at 25.45; on the run's sixteen batches the same five starts ended at 34.5 (`results/s6_starts/reading.txt`, lines 7 and 9). The starting point sets when a search breaks out, not where it ends: it explains 23 percent of the variance in harm at 80 steps and none at 320 (lines 44 and 68). No verdict depends on the gap, since every ratio is formed within the run from the same starts on both sides, and no long-search level is set against the paper's 40.2.
- **What the lead result does not show.** It names no component. Pooled over sources, the 20,000 top-ranked entries keep only 0.55 to 0.71 of the harm (`results/s6_followups/exploited.txt`, lines 7, 16, and 58), and most sources need all 38,936 entries to keep 90 percent of theirs (lines 11, 24, and 70); a ranking by gradient can also miss a smaller set that gradients do not show. It says nothing about how the harm falls within a text, since a text's harm is a mean over its 512 positions.
- **Near-duplicate text.** The two sides share no document, but 11 of the 2,048 held-out texts repeat a 50-token span of an attack text. Recomputed without them, no ratio interval moves by more than 0.0015 at either end and no interval in nats by more than 0.018 (`results/s6_followups/spread.txt`, lines 6 and 7; `lead_tables.txt`, lines 276 and 277).
- **The training experiment is short.** It ran 1,000 batches against training's 400,000, under the four cautions of Section 5.4, and does not rule out that the decomposition also moved away from its adversary during training, or trapped it.

## References

[1] L. Bushnaq, D. Braun, O. Clive-Griffin, B. Bussmann, N. Hu, M. Ivanitskiy, L. Linsefors, and L. Sharkey. Interpreting Language Model Parameters (adVersarial Parameter Decomposition). Goodfire, May 2026. https://www.goodfire.ai/research/interpreting-lm-parameters

[2] T. Angsten. VPD's Evaluation Adversary Finds Systematic Defects in the Released Decomposition. LessWrong, October 2026. https://www.lesswrong.com/posts/tGdKJPmyaiHnqkLem/vpd-s-evaluation-adversary-finds-systematic-defects-in-the

[3] T. Angsten. Do VPD's Explanations Aggregate? An Audit of the Released Decomposition. LessWrong, 30 September 2026. https://www.lesswrong.com/posts/KeBccWBGXnNXzZFBp/do-vpd-s-explanations-aggregate-an-audit-of-the-released-1. Code and technical report: https://github.com/angsten/vpd-audit, included here as the submodule `third_party/vpd-audit`.

[4] Goodfire. param-decomp, the authors' code. https://github.com/goodfire-ai/param-decomp. Pinned here at commit `74146b5` inside `third_party/vpd-audit`; the newer recipe's description is `docs/skill.md` at commit `5ffc73d`.

[5] A. B. Owen. The Pigeonhole Bootstrap. The Annals of Applied Statistics 1(2), 386–411, 2007. DOI 10.1214/07-AOAS122.

[6] Angsten's audit of VPD, claim by claim, on the team's new decomposition. Written for L. Sharkey and the Goodfire parameter-decomposition team, 17 October 2026. https://drive.google.com/file/d/1px6owOIAbXEPyCNT4dmnuFNjhUYC6Ta1/view

[7] L. Sharkey. Comment on [3]. LessWrong, 17 October 2026. https://www.lesswrong.com/posts/KeBccWBGXnNXzZFBp/do-vpd-s-explanations-aggregate-an-audit-of-the-released-1?commentId=r3bS4ciM6jN6ZoHiN
