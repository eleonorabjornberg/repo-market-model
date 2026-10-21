# Why the direct-pairs variant loses in 2021-23 (#1086): the training-pair checks, the decomposition still owed. Development data, not a verdict

**Serves:** H5 step 3 (the 2021-23 diagnosis). Declaration `metadata/direct_pairs_diagnosis_1086.json`, committed before any number; script `scripts/direct_pairs_diagnosis_1086.py`; test `tests/test_direct_pairs_diagnosis_1086.py`; figures `docs/research/direct-pairs-diagnosis-1086/training.json`. Nothing was refitted, no published figure moves, no day after 2025-12-31 and no locked day is read.

**Status.** Criterion 2 (the three declared checks on the training pairs) is done and is below. Criterion 1 (the decomposition of #1036's walks by lead, day type and quantile level) is **not** done: the walks exist only on Eleonora's Mac (`~/rmm-1027/WALKS`; walks are never committed), so the command is handed to her as a `needs-mac:` comment on the pull request. It takes seconds and fits nothing. The section "Decomposition" below is filled when its `decompose.json` lands on this branch. Until then this page does not say where in the distribution the loss sits.

## What #1036 found (the loss to explain)

2021-23, grid CRPS skill, 748 days (from `docs/research/aligned-calendar-1027/report.md`): `gbm_funding_cal_direct` over `gbm_funding` -27.8% [-41.5%, -17.0%]; `gbm_funding_cal_aligned` over `gbm_funding` -7.9% [-14.3%, -2.1%]; aligned over direct +15.6% [+10.9%, +20.7%].

The two variants share their inputs, their leaf (5), their seed, their refit cadence and their quantile grid. They differ in the pairing only. So the **15.6% gap between them** is a pairing effect. The rest of the direct variant's loss to `gbm_funding` (the aligned variant also loses to it, by 7.9%) comes from what both variants change against `gbm_funding`: the leaf (5 against 20), the added inputs (the target-row calendar columns and the net-settlement columns), and the target-row alignment of the calendar columns. The checks below separate what they can.

## Check results (criterion 2): the training pairs, 2021-23 refits

Panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, scratch panel `d6dca7edabd0d12b2746d7c3d8298c4a08c49a99b2afd101aa412f331acda91e`. Means over the refits whose first scored day is in 2021-23 (refits per lead in the first column). `one-step` is the set `gbm_funding` trains on, `direct` the set of `gbm_funding_cal_direct`; both from the same training frame.

| lead | refits | set | pairs | effective sample | target variance | h-step residual variance | floor-regime pairs | floor pairs per leaf of 5 | per leaf of 20 | floor-regime target variance |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 36 | one-step | 1,057.5 | 383.7 | 160.6 | 176.0 | 370.5 | 74.1 | 18.5 | 6.08 |
| 1 | 36 | direct | 1,053.5 | 382.3 | 161.3 | 223.4 | 370.5 | 74.1 | 18.5 | 6.08 |
| 2 | 36 | one-step | 1,057.5 | 383.7 | 160.6 | 176.0 | 370.5 | 74.1 | 18.5 | 6.08 |
| 2 | 36 | direct | 1,052.5 | 381.9 | 161.4 | 235.1 | 370.5 | 74.1 | 18.5 | 6.08 |
| 3 | 36 | one-step | 1,057.5 | 383.7 | 160.6 | 176.0 | 370.5 | 74.1 | 18.5 | 6.08 |
| 3 | 36 | direct | 1,051.5 | 381.5 | 161.6 | 241.8 | 370.5 | 74.1 | 18.5 | 6.08 |
| 4 | 36 | one-step | 1,057.5 | 383.7 | 160.6 | 176.0 | 370.5 | 74.1 | 18.5 | 6.08 |
| 4 | 36 | direct | 1,050.5 | 381.2 | 161.8 | 238.8 | 370.5 | 74.1 | 18.5 | 6.08 |
| 5 | 36 | one-step | 1,057.5 | 383.7 | 160.6 | 176.0 | 370.5 | 74.1 | 18.5 | 6.08 |
| 5 | 36 | direct | 1,049.5 | 380.8 | 161.9 | 238.7 | 370.5 | 74.1 | 18.5 | 6.08 |

Floor-regime pairs in the training set at lead 1, by refit (the first scored day of the refit; direct set):

| first scored day | pairs | floor-regime pairs | floor-regime target variance |
|---|---|---|---|
| 2021-01-08 | 686 | 3 | 0.22 |
| 2021-04-12 | 749 | 66 | 8.80 |
| 2021-07-12 | 812 | 129 | 6.97 |
| 2021-10-08 | 875 | 192 | 5.89 |
| 2022-01-11 | 938 | 255 | 5.02 |
| 2022-04-12 | 1001 | 318 | 4.53 |
| 2022-07-14 | 1064 | 381 | 7.41 |
| 2022-10-13 | 1127 | 444 | 7.69 |
| 2023-01-17 | 1190 | 507 | 6.91 |
| 2023-04-18 | 1253 | 570 | 6.38 |
| 2023-07-19 | 1316 | 633 | 5.85 |
| 2023-10-18 | 1379 | 696 | 5.39 |


The scratch panel used here was built from current `origin/main` (digest above); #1036's report was built from an earlier main and carries a different scratch digest. The training sets depend on the dates, the spreads and the calendar columns, which that change does not touch as far as these figures go, but the decomposition must read the Mac's own `PUB.csv` and `AUG3.csv`, whose digests the walks carry (the command refuses a mismatch).

### Reading (words, not thresholds)

1. **Effective sample per lead: not the cause.** The direct set holds within about one percent of the pairs of the one-step set at every lead (a direct pair is dropped only when its target has no as-of read), and its effective sample is within about one percent too. The roughly 380 effective pairs out of about 1,050 say that both sets are strongly autocorrelated, equally. A smaller training set does not explain a loss to a model trained on the same days.
2. **Variance of the target: not the cause, with one real difference.** The targets of the two sets have the same variance (about 161) and the same floor-regime variance (about 6 bp squared), because they are the same days' spreads. What differs is the h-step residual, the target minus the spread at the pair's anchor: it is 27 to 37 percent larger in the direct set (223 to 242 against 176), and grows with the lead as an h-step change should. This is the pairing doing what it is built to do. Whether it hurts a tree in a regime where the spread sits within a few bp of its level is a question for the decomposition and for a refit; this check does not answer it.
3. **Leaf size against the floor-regime days: not the cause on average, but it bites in 2021.** Averaged over the refits, a tree has about 74 floor-regime pairs per leaf of 5 (18 per leaf of 20), the same in both sets. The average hides the entry into the regime: the refit of 2021-01-08 trains on 3 floor-regime pairs and the next, in April 2021, on 66, among a training set of about 700 pairs whose targets still carry the 2018-20 spikes. For those refits a leaf of 5 can put a handful of days on a side. This is the same for both variants, so it cannot by itself explain the 15.6% by which direct is behind aligned; it could explain part of both variants' loss to `gbm_funding` (leaf 20) in 2021.

### Which explanation holds, and does it explain aligned over direct

- Of the three declared candidates, none separates the direct training set from the one-step set in size, target variance or leaf coverage. The only difference these checks find is the h-step residual variance. **They do not explain the 15.6% by which aligned leads direct**: the two sets have the same days, the same inputs and the same leaf, and the checks above are properties of the days.
- What does differ is which features go with which target: a direct pair reads its features as of the decision instant h days before its target, an aligned one-step pair reads row p with the calendar columns of row p + 1. That is a property of the pairing, not of the sample, and the checks here cannot see it. Whether it is the cause needs the decomposition (does the excess sit in the centre or the tails, at long leads rather than lead 1, in 2021 rather than 2022-23) and, to confirm it, a refit.
- **Criterion 3 (a refit).** Not declared yet. A refit is worth declaring only once the decomposition says where the excess sits; declaring one now would be guessing. If the decomposition puts the excess at leads 2 to 5 or in the first months of 2021, the refit to declare is the direct variant at leaf 20 on 2021-23 refits, with and without the added inputs; it runs on direct pairs, reads the calendar columns at the target day, and goes to the Mac overnight (`needs-mac:`).

### Not checked

The decomposition (criterion 1); whether the aligned variant's lead over direct comes from the same cause as the direct variant's loss to `gbm_funding` (the pairing effect is isolated by aligned against direct, the rest by the leaf and the inputs; only the decomposition and a refit can tell them apart); any refit. Development data only; no verdict for H5.

## Decomposition (criterion 1): owed

`python3 scripts/direct_pairs_diagnosis_1086.py decompose` on the Mac, against the walks of #1036. It reports, for 2021-23 target days and for the days outside as contrast, the excess grid CRPS of `gbm_funding_cal_direct` over `gbm_funding`, of aligned against direct and of aligned over `gbm_funding`, by lead, by target day type, by calendar year and by quantile level, grouped into the declared bands (lower tail, lower shoulder, centre, upper shoulder, upper tail). Level shares sum to the cell's grid CRPS exactly.
