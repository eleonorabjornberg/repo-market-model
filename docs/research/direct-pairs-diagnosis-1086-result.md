# Why the direct-pairs variant loses in 2021-23 (#1086): the training-pair checks and the decomposition. Development data, not a verdict

**Serves:** H5 step 3 (the 2021-23 diagnosis). Declaration `metadata/direct_pairs_diagnosis_1086.json`, committed before any number; script `scripts/direct_pairs_diagnosis_1086.py`; test `tests/test_direct_pairs_diagnosis_1086.py`; figures `docs/research/direct-pairs-diagnosis-1086/training.json`, `decompose.json` and the headline `result.json`. Nothing was refitted, no published figure moves, no day after 2025-12-31 and no locked day is read.

**Status.** Both criteria are done. Criterion 2 (three declared checks on the training pairs) and criterion 1 (the decomposition of #1036's walks by lead, target-day type, calendar year and quantile level, run on Eleonora's Mac against `~/rmm-1027/WALKS`, figures in `docs/research/direct-pairs-diagnosis-1086/decompose.json`) are below. No refit was made (criterion 3 is addressed at the end).

**Headline of the decomposition (read first).** In 2021-23 the loss of `gbm_funding_cal_direct` to `gbm_funding` sits in the **centre of the distribution** (levels 0.25 to 0.75 carry +0.147 of the +0.197 mean excess grid CRPS, about three quarters), at **every lead** (lead 1 +0.159 rising to lead 5 +0.252), and in **calendar year 2022** (+0.455 against +0.121 in 2021 and +0.014 in 2023). It is the same on ordinary and settlement days (about +0.19), so it is not a calendar-day effect. The aligned variant's lead over direct (-0.141 in the same units) sits in the same place: centre (-0.104 of it), every lead, and 2022 (-0.312).

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

### Reading of the decomposition (words, not thresholds)

Units are mean excess grid CRPS per target-day-and-lead cell (candidate minus reference; positive is a loss of the candidate); the 3,740 cells are 748 days times five leads. As a check on the reading, the +0.197 of direct over `gbm_funding` is the figure behind #1036's -27.8% grid CRPS skill. **These cell means carry no interval**: the walks are not committed and the declared decomposition has no resampling, so the intervals of #1036's headline rows (above) are the only ones; a split of a loss by band, year or day type here is a description of where the mean sits, not a tested difference. The small groups (quarter-end 60 cells, tax dates 180) are the noisiest.

1. **Centre or tails: the centre.** Direct over `gbm_funding`: centre +0.147, lower shoulder +0.008, upper shoulder +0.020, lower tail +0.011, upper tail +0.011. The tails are not where it is lost. (Outside 2021-23 the direct variant gains in every band except the lower shoulder, mostly in the upper shoulder and tail: that is #1036's gain on pressure days.)
2. **Leads: all of them, rising with the lead.** +0.159, +0.182, +0.192, +0.198, +0.252 for leads 1 to 5. Lead 1 already loses (a lead-1 direct pair is the one-step pair with the calendar columns read at the anchor row), so the loss is not only a long-lead artefact of the h-step target; lead 5 is the worst, in the centre (+0.183).
3. **Year: 2022.** +0.455 in 2022, +0.121 in 2021, +0.014 in 2023. Almost the whole loss is the year the spread left the floor regime (the policy-rate rise); 2023 is level with the control. The first months of 2021, where a tree trained on 3 to 66 floor-regime pairs, are inside the 2021 figure but do not dominate the three years.
4. **Day type: not the calendar days.** Ordinary +0.194, settlement +0.193, month-end +0.174, tax dates +0.259, quarter-end +0.305 (60 cells). The calendar-day cells are no better than ordinary days in 2021-23, which says the direct variant's calendar columns do not buy in the regime what they buy outside it. In the lower tail and lower shoulder the calendar-day cells lose more than ordinary days do (quarter-end +0.062 and +0.041).
5. **Aligned over direct, 2021-23: the same place.** -0.141 overall, centre -0.104, upper shoulder -0.018, upper tail -0.018, every lead (-0.116 to -0.189, largest at lead 5), 2022 -0.312, 2021 -0.096, 2023 -0.014. Aligned recovers about 72% of direct's loss to `gbm_funding`; its own remaining loss (+0.056) is centre again (+0.043) and 2022 (+0.143).

### Which explanation holds, and does it explain aligned over direct

- **Of the three declared candidates, none holds.** The two training sets have the same size, effective sample, target variance and floor-regime coverage (checks above), and the loss does not sit in the early-2021 refits where the leaf could bite. They do not explain the 15.6% by which aligned leads direct.
- **What the data support** (development data, not a verdict): the loss is a **centre-of-the-distribution loss in 2022 at all leads**, and the aligned variant's lead over direct is the **same loss, smaller**, not a different one: same band, same year, same leads, same ordinary-day size. That is consistent with a single cause that the pairing sets and that the aligned pairing halves in effect: a direct pair reads its features as of the decision instant h days before its target and the calendar columns at the target day, so in a regime where the spread moves by a few bp around a shifting level and the calendar columns carry little, the direct model has a larger h-step residual to fit (checked above: 27 to 37 percent larger) and a centre that is placed less well. An aligned pair at lead 1 reads row p with the calendar columns of row p + 1 and trains on a smaller change. This is a reading, not a demonstrated cause: this step refits nothing, and the pairing, the leaf (5 against 20) and the added inputs change together against `gbm_funding`, so aligned over direct isolates the pairing and direct over `gbm_funding` does not.
- **Whether aligned's lead over direct is the same cause as direct's loss to `gbm_funding`:** the locus is identical, so there is no evidence of two causes; only a refit can separate pairing from leaf and inputs.
- **Outside 2021-23 the aligned variant is worse than direct on the calendar days** (month-end +0.149, quarter-end +0.462 in 2018-20 and 2024-25 pooled), which is #1036's finding that direct is the better of the two on pressure days. Whatever is chosen has to be chosen on both regimes; this page does not choose.
- **Criterion 3 (a refit).** Not declared. The trigger written above (excess at leads 2 to 5 or in early 2021) is half met: the excess is at all leads and in 2022, not in early 2021. The refit that would separate the pairing from the leaf and the inputs is the direct variant at leaf 20, with and without the added inputs, on the 2021-23 refits; it runs on direct pairs, reads the calendar columns at the target day, and goes to the Mac overnight (`needs-mac:`). Whether to spend it is for Eleonora.

### Not checked

Any refit (so the pairing, the leaf and the added inputs are not separated); intervals on the decomposition cells; whether the 2022 concentration is the policy-rate rise or a property of the refits that fall in 2022; the training-pair checks use a scratch panel built from current main, the decomposition one the Mac's own `AUG3.csv` (digest in `decompose.json`, `f9fae9dc...`), so the two sets of figures are on different scratch builds with the same published panel `4ddc3882...`. Development data only; no verdict for H5.

## Decomposition (criterion 1): tables

### gbm_funding_cal_aligned over gbm_funding

Target days 2021-23. Mean excess grid CRPS (candidate minus reference; positive is a loss of the candidate), and its share in each band of levels.

| group | cells | excess | lower_tail | lower_shoulder | centre | upper_shoulder | upper_tail |
|---|---|---|---|---|---|---|---|
| all | 3740 | +0.0559 | +0.0114 | +0.0052 | +0.0434 | +0.0023 | -0.0063 |
| lead 1 | 748 | +0.0426 | +0.0068 | +0.0014 | +0.0378 | +0.0010 | -0.0044 |
| lead 2 | 748 | +0.0545 | +0.0108 | +0.0060 | +0.0447 | +0.0012 | -0.0083 |
| lead 3 | 748 | +0.0571 | +0.0116 | +0.0060 | +0.0443 | +0.0022 | -0.0071 |
| lead 4 | 748 | +0.0621 | +0.0129 | +0.0061 | +0.0464 | +0.0032 | -0.0064 |
| lead 5 | 748 | +0.0634 | +0.0150 | +0.0066 | +0.0437 | +0.0036 | -0.0055 |
| month_end | 300 | +0.0384 | +0.0123 | +0.0011 | +0.0302 | +0.0003 | -0.0055 |
| ordinary | 1665 | +0.0538 | +0.0132 | +0.0061 | +0.0405 | +0.0008 | -0.0068 |
| quarter_end | 60 | +0.0924 | +0.0100 | +0.0279 | +0.1495 | -0.0133 | -0.0817 |
| settlement | 1535 | +0.0462 | +0.0080 | +0.0036 | +0.0350 | +0.0040 | -0.0044 |
| tax_date | 180 | +0.1757 | +0.0231 | +0.0100 | +0.1281 | +0.0091 | +0.0055 |
| year 2021 | 1250 | +0.0244 | +0.0070 | +0.0017 | +0.0102 | +0.0046 | +0.0010 |
| year 2022 | 1245 | +0.1433 | +0.0224 | +0.0083 | +0.1159 | +0.0066 | -0.0100 |
| year 2023 | 1245 | +0.0003 | +0.0049 | +0.0057 | +0.0042 | -0.0045 | -0.0100 |

Target days outside 2021-23. Mean excess grid CRPS (candidate minus reference; positive is a loss of the candidate), and its share in each band of levels.

| group | cells | excess | lower_tail | lower_shoulder | centre | upper_shoulder | upper_tail |
|---|---|---|---|---|---|---|---|
| all | 5535 | -0.0721 | +0.0144 | +0.0051 | -0.0625 | -0.0182 | -0.0107 |
| lead 1 | 1107 | -0.1280 | +0.0132 | +0.0045 | -0.1038 | -0.0260 | -0.0158 |
| lead 2 | 1107 | -0.0427 | +0.0138 | +0.0056 | -0.0421 | -0.0137 | -0.0064 |
| lead 3 | 1107 | -0.0691 | +0.0141 | +0.0053 | -0.0598 | -0.0171 | -0.0116 |
| lead 4 | 1107 | -0.0713 | +0.0144 | +0.0044 | -0.0578 | -0.0186 | -0.0137 |
| lead 5 | 1107 | -0.0491 | +0.0164 | +0.0055 | -0.0491 | -0.0158 | -0.0061 |
| month_end | 447 | -0.6283 | +0.0006 | -0.0068 | -0.4245 | -0.1145 | -0.0832 |
| ordinary | 2563 | +0.0206 | +0.0174 | +0.0065 | -0.0078 | -0.0025 | +0.0070 |
| quarter_end | 86 | -1.2470 | +0.0086 | +0.0102 | -0.2731 | -0.2404 | -0.7523 |
| settlement | 2174 | -0.0187 | +0.0144 | +0.0065 | -0.0379 | -0.0087 | +0.0070 |
| tax_date | 265 | -0.0864 | +0.0106 | -0.0029 | -0.1153 | -0.0138 | +0.0350 |
| year 2018 | 545 | -0.0937 | +0.0087 | -0.0059 | -0.0880 | -0.0351 | +0.0267 |
| year 2019 | 1250 | -0.0730 | +0.0256 | +0.0154 | -0.0512 | -0.0206 | -0.0421 |
| year 2020 | 1255 | +0.0454 | +0.0099 | +0.0055 | +0.0228 | +0.0065 | +0.0007 |
| year 2024 | 1250 | -0.0779 | +0.0093 | +0.0055 | -0.0542 | -0.0188 | -0.0197 |
| year 2025 | 1235 | -0.1749 | +0.0153 | -0.0014 | -0.1578 | -0.0329 | +0.0020 |

### gbm_funding_cal_aligned over gbm_funding_cal_direct

Target days 2021-23. Mean excess grid CRPS (candidate minus reference; positive is a loss of the candidate), and its share in each band of levels.

| group | cells | excess | lower_tail | lower_shoulder | centre | upper_shoulder | upper_tail |
|---|---|---|---|---|---|---|---|
| all | 3740 | -0.1407 | +0.0007 | -0.0025 | -0.1036 | -0.0177 | -0.0175 |
| lead 1 | 748 | -0.1159 | -0.0034 | -0.0043 | -0.0823 | -0.0122 | -0.0138 |
| lead 2 | 748 | -0.1279 | +0.0023 | -0.0023 | -0.0988 | -0.0154 | -0.0137 |
| lead 3 | 748 | -0.1351 | -0.0010 | -0.0028 | -0.0985 | -0.0171 | -0.0156 |
| lead 4 | 748 | -0.1359 | +0.0021 | -0.0022 | -0.0988 | -0.0176 | -0.0194 |
| lead 5 | 748 | -0.1887 | +0.0034 | -0.0012 | -0.1396 | -0.0263 | -0.0250 |
| month_end | 300 | -0.1356 | -0.0093 | -0.0120 | -0.0841 | -0.0109 | -0.0193 |
| ordinary | 1665 | -0.1400 | +0.0055 | -0.0005 | -0.1083 | -0.0191 | -0.0176 |
| quarter_end | 60 | -0.2130 | -0.0519 | -0.0127 | -0.1187 | -0.0134 | -0.0164 |
| settlement | 1535 | -0.1463 | +0.0010 | -0.0017 | -0.1085 | -0.0190 | -0.0180 |
| tax_date | 180 | -0.0832 | -0.0125 | -0.0096 | -0.0451 | -0.0059 | -0.0100 |
| year 2021 | 1250 | -0.0964 | +0.0029 | -0.0078 | -0.0706 | -0.0080 | -0.0128 |
| year 2022 | 1245 | -0.3117 | -0.0034 | -0.0041 | -0.2307 | -0.0408 | -0.0326 |
| year 2023 | 1245 | -0.0141 | +0.0026 | +0.0043 | -0.0096 | -0.0043 | -0.0072 |

Target days outside 2021-23. Mean excess grid CRPS (candidate minus reference; positive is a loss of the candidate), and its share in each band of levels.

| group | cells | excess | lower_tail | lower_shoulder | centre | upper_shoulder | upper_tail |
|---|---|---|---|---|---|---|---|
| all | 5535 | -0.0162 | +0.0134 | -0.0001 | -0.0472 | +0.0021 | +0.0156 |
| lead 1 | 1107 | -0.0301 | +0.0072 | -0.0008 | -0.0438 | -0.0035 | +0.0109 |
| lead 2 | 1107 | +0.0151 | +0.0084 | -0.0027 | -0.0285 | +0.0068 | +0.0312 |
| lead 3 | 1107 | -0.0328 | +0.0102 | -0.0013 | -0.0564 | +0.0021 | +0.0126 |
| lead 4 | 1107 | -0.0424 | +0.0176 | +0.0015 | -0.0558 | -0.0033 | -0.0024 |
| lead 5 | 1107 | +0.0091 | +0.0238 | +0.0030 | -0.0515 | +0.0084 | +0.0256 |
| month_end | 447 | +0.1490 | -0.0130 | -0.0074 | +0.0439 | +0.0441 | +0.0814 |
| ordinary | 2563 | -0.0010 | +0.0303 | +0.0080 | -0.0386 | -0.0006 | -0.0001 |
| quarter_end | 86 | +0.4624 | -0.0653 | -0.0412 | +0.1947 | +0.1248 | +0.2494 |
| settlement | 2174 | -0.0639 | +0.0039 | -0.0053 | -0.0803 | -0.0052 | +0.0230 |
| tax_date | 265 | -0.2067 | -0.0013 | -0.0095 | -0.0923 | -0.0228 | -0.0808 |
| year 2018 | 545 | -0.2221 | +0.0085 | -0.0109 | -0.1440 | -0.0324 | -0.0433 |
| year 2019 | 1250 | -0.2473 | +0.0115 | -0.0153 | -0.2291 | -0.0136 | -0.0008 |
| year 2020 | 1255 | -0.0702 | -0.0193 | -0.0115 | -0.0475 | -0.0016 | +0.0097 |
| year 2024 | 1250 | +0.1649 | +0.0386 | +0.0268 | +0.0620 | +0.0093 | +0.0283 |
| year 2025 | 1235 | +0.1801 | +0.0255 | +0.0045 | +0.0693 | +0.0297 | +0.0511 |

### gbm_funding_cal_direct over gbm_funding

Target days 2021-23. Mean excess grid CRPS (candidate minus reference; positive is a loss of the candidate), and its share in each band of levels.

| group | cells | excess | lower_tail | lower_shoulder | centre | upper_shoulder | upper_tail |
|---|---|---|---|---|---|---|---|
| all | 3740 | +0.1966 | +0.0108 | +0.0078 | +0.1470 | +0.0200 | +0.0112 |
| lead 1 | 748 | +0.1585 | +0.0102 | +0.0057 | +0.1201 | +0.0132 | +0.0094 |
| lead 2 | 748 | +0.1823 | +0.0085 | +0.0083 | +0.1435 | +0.0166 | +0.0054 |
| lead 3 | 748 | +0.1922 | +0.0126 | +0.0089 | +0.1429 | +0.0193 | +0.0085 |
| lead 4 | 748 | +0.1980 | +0.0108 | +0.0083 | +0.1452 | +0.0208 | +0.0130 |
| lead 5 | 748 | +0.2521 | +0.0116 | +0.0077 | +0.1833 | +0.0299 | +0.0195 |
| month_end | 300 | +0.1740 | +0.0216 | +0.0132 | +0.1143 | +0.0112 | +0.0138 |
| ordinary | 1665 | +0.1939 | +0.0077 | +0.0067 | +0.1488 | +0.0199 | +0.0107 |
| quarter_end | 60 | +0.3054 | +0.0619 | +0.0406 | +0.2681 | +0.0001 | -0.0654 |
| settlement | 1535 | +0.1925 | +0.0070 | +0.0052 | +0.1436 | +0.0231 | +0.0136 |
| tax_date | 180 | +0.2589 | +0.0356 | +0.0196 | +0.1732 | +0.0150 | +0.0155 |
| year 2021 | 1250 | +0.1208 | +0.0042 | +0.0095 | +0.0808 | +0.0126 | +0.0137 |
| year 2022 | 1245 | +0.4550 | +0.0258 | +0.0124 | +0.3467 | +0.0474 | +0.0226 |
| year 2023 | 1245 | +0.0144 | +0.0023 | +0.0014 | +0.0138 | -0.0002 | -0.0029 |

Target days outside 2021-23. Mean excess grid CRPS (candidate minus reference; positive is a loss of the candidate), and its share in each band of levels.

| group | cells | excess | lower_tail | lower_shoulder | centre | upper_shoulder | upper_tail |
|---|---|---|---|---|---|---|---|
| all | 5535 | -0.0558 | +0.0009 | +0.0051 | -0.0153 | -0.0203 | -0.0263 |
| lead 1 | 1107 | -0.0979 | +0.0060 | +0.0053 | -0.0600 | -0.0225 | -0.0267 |
| lead 2 | 1107 | -0.0578 | +0.0055 | +0.0083 | -0.0136 | -0.0204 | -0.0376 |
| lead 3 | 1107 | -0.0363 | +0.0039 | +0.0066 | -0.0033 | -0.0193 | -0.0242 |
| lead 4 | 1107 | -0.0289 | -0.0032 | +0.0029 | -0.0019 | -0.0153 | -0.0114 |
| lead 5 | 1107 | -0.0582 | -0.0074 | +0.0025 | +0.0024 | -0.0241 | -0.0316 |
| month_end | 447 | -0.7773 | +0.0136 | +0.0007 | -0.4683 | -0.1586 | -0.1646 |
| ordinary | 2563 | +0.0216 | -0.0130 | -0.0015 | +0.0308 | -0.0019 | +0.0071 |
| quarter_end | 86 | -1.7094 | +0.0740 | +0.0515 | -0.4679 | -0.3652 | -1.0018 |
| settlement | 2174 | +0.0452 | +0.0105 | +0.0118 | +0.0424 | -0.0035 | -0.0160 |
| tax_date | 265 | +0.1204 | +0.0119 | +0.0066 | -0.0230 | +0.0090 | +0.1159 |
| year 2018 | 545 | +0.1284 | +0.0002 | +0.0050 | +0.0559 | -0.0026 | +0.0700 |
| year 2019 | 1250 | +0.1743 | +0.0141 | +0.0307 | +0.1779 | -0.0070 | -0.0414 |
| year 2020 | 1255 | +0.1156 | +0.0292 | +0.0170 | +0.0703 | +0.0081 | -0.0090 |
| year 2024 | 1250 | -0.2428 | -0.0293 | -0.0213 | -0.1162 | -0.0281 | -0.0480 |
| year 2025 | 1235 | -0.3550 | -0.0102 | -0.0060 | -0.2272 | -0.0626 | -0.0491 |

