# Where the direct-pairs variant loses in 2021-23 (#1086): a decomposition of #1036's walks. Development data, not a verdict

**Serves:** H5 step 3 (the 2021-23 diagnosis), criterion 1 only, on Eleonora's ruling of 11 November 2026 (relayed by the orchestrating session; docket card "Give the gradient-boosted model a fair calendar test?", option (a)). Declaration `metadata/direct_pairs_diagnosis_1086.json` (committed before any number), script `scripts/direct_pairs_diagnosis_1086.py` (`decompose`), figures `docs/research/direct-pairs-diagnosis-1086/decompose.json` and the headline `result.json`, tests `tests/test_direct_pairs_diagnosis_1086.py` and `tests/test_decomposition_page_1086.py`.

**Settled questions** (`docs/research/settled-questions.md`, her rule of 9 November 2026). The one entry this touches is S9, the one-step fit (a spread model reads the calendar at the target day, on direct pairs); this study keeps it. Nothing there settles gradient-boosted quantiles against mean reversion. Related, not re-run: #1197 (s3 against `gbm_funding`), #1027 and #1032 (calendar-aware GBM scores). Calendar first: both variants read the calendar columns at the target day; the control `gbm_funding` is calendar-blind and is only the reference of the excess.

**Where the figures come from.** Nothing was refitted and no walk was read in this session. The decomposition was run on Eleonora's Mac against #1036's walks (`~/rmm-1027/WALKS`) in the closed draft #1092 (commit `6a05a8bc`); the walks are not in the repository, so the cloud cannot re-run it. This page reuses that output unchanged, with the script and declaration it was computed under. `tests/test_decomposition_page_1086.py` checks that the output is internally consistent (bands and levels sum to each total; the three pairs add up cell for cell) and that this page quotes it. The published panel digest is `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, the scratch panel (the Mac's own) `f9fae9dce43341f2816d19c76d9562f9773f0bff5891bd051f52eac0ffecb8f3`. No day after 2025-12-31 and no locked day is read.

## What is measured

The excess is candidate minus reference of the grid CRPS (`scoring_protocol.grid_crps`, twice the mean pinball loss over the 23 levels), so a positive excess is a loss of the candidate. It is split exactly: a level's share of a cell is twice its pinball loss over 23, and the shares sum to the cell's score. Cells are target day by lead (h = 1 to 5) over the 2021-23 target days of #1036's regime cut. The levels are grouped into five declared bands, a description of where the loss sits and not a threshold: lower tail (level 0.10 or below), lower shoulder, centre (0.25 to 0.75), upper shoulder, upper tail (0.90 or above). Three pairs: `gbm_funding_cal_direct` over `gbm_funding` (#1036's headline pair; it differs in the pairing, the leaf, 5 against 20, and the added inputs), `gbm_funding_cal_aligned` over `gbm_funding_cal_direct` (the pairing alone), and aligned over `gbm_funding`. Units are bp of grid CRPS per cell.

**No interval is attached.** The walks are not committed and the declared decomposition has no resampling, so these are descriptions of where a mean sits, not tested differences. The intervals that exist are #1036's headline ones (`docs/research/aligned-calendar-1027/report.md`): direct over `gbm_funding` -27.8% [-41.5%, -17.0%], aligned over `gbm_funding` -7.9% [-14.3%, -2.1%], aligned over direct +15.6% [+10.9%, +20.7%], grid CRPS skill over 748 days. The small groups (quarter-end, tax dates) are the noisiest.

## Findings

**Direct over `gbm_funding`, 2021-23: mean excess +0.1966.**

1. **Centre or tails: the centre.** Centre +0.1470 of the +0.1966 (about three quarters); lower shoulder +0.0078, upper shoulder +0.0200, lower tail +0.0108, upper tail +0.0112. The centre is 11 of 23 levels, so the band share is partly a count; the level table below shows it directly: the excess is a hump around the median (about 0.016 per level from 0.40 to 0.60), about 0.004 per level from 0.025 to 0.20, and nil at 0.01 and 0.99.
2. **Leads: every lead, rising.** +0.1585, +0.1823, +0.1922, +0.1980, +0.2521 for h = 1 to 5. Lead 1 already loses, so it is not only a long-lead artefact of the h-step target; lead 5 is the worst, and in the centre (+0.1833).
3. **Year: 2022.** +0.4550 in 2022, +0.1208 in 2021, +0.0144 in 2023. Almost all of it is the year the spread left the floor regime; 2023 is level with the control.
4. **Target-day type: not the calendar days.** Ordinary +0.1939, settlement +0.1925, month-end +0.1740, tax dates +0.2589, quarter-end +0.3054 (the smallest group). The loss is as large on ordinary days as anywhere, so the variant's calendar columns do not buy in this regime what they buy outside it.
5. **Contrast, outside 2021-23.** The direct variant gains over `gbm_funding` (-0.0558), most in 2024 (-0.2428) and 2025 (-0.3550), and on month-end and quarter-end days: that is #1036's gain on pressure days. The 2021-23 loss does not come from the calendar columns misfiring on pressure days.

**Aligned over direct, 2021-23: mean excess -0.1407** (aligned is ahead). It sits in the same place: centre -0.1036, every lead (-0.1159 to -0.1887, largest at lead 5), and 2022 (-0.3117; 2021 -0.0964, 2023 -0.0141); ordinary days -0.1400. Aligned over `gbm_funding` is +0.0559: aligned recovers about 72% of direct's loss, and what it keeps is again the centre (+0.0434) and 2022 (+0.1433).

## Does the cause look fixable?

**Not yet.** This step locates the loss; it does not name a cause. The locus is narrow and the same for both variants: the middle of the predictive distribution, at every lead, in 2022, on ordinary and calendar days alike. That makes a defect in the tails or in the calendar columns unlikely. It is consistent with one cause that the pairing sets and the aligned pairing roughly halves, for instance a direct pair carrying a larger h-step change to fit in a regime where the spread moves a few bp around a level that shifts in 2022. That is a reading, not a demonstrated cause. The pairing, the leaf (5 against 20) and the added inputs all change together between direct and `gbm_funding`; aligned over direct isolates the pairing, and direct over `gbm_funding` does not. Only a refit can separate them (for example the direct variant at leaf 20, with and without the added inputs, on the 2021-23 refits), and a refit is criterion 3, out of scope by the ruling. Whether to spend it is hers. The training-set checks of criterion 2 (effective sample, target variance, leaf against floor-regime days) are also out of scope and were not re-read or re-run here; the earlier ones are on the closed #1092.

Which explanation holds: none is established. Whether aligned's lead over direct has the same cause as direct's loss to `gbm_funding`: the locus is identical, so there is no evidence of two causes, and no test that there is one.

## Not checked

Intervals on any decomposition cell; any refit; criterion 2's checks and criterion 3; #1124's walks; whether the 2022 concentration is the policy-rate rise or a property of the refits that fall in 2022; whether another regime shows the same centre loss. The decomposition could not be re-run in this session (the walks are on the Mac), so its reproduction rests on the declared command and the digests it carries. Development data only; no verdict for H5, and nothing here changes the candidate.

## Tables

The levels (direct over `gbm_funding`, 2021-23, all cells):

| level | 0.01 | 0.025 | 0.05 | 0.1 | 0.15 | 0.2 | 0.25 | 0.3 | 0.35 | 0.4 | 0.45 | 0.5 | 0.55 | 0.6 | 0.65 | 0.7 | 0.75 | 0.8 | 0.85 | 0.9 | 0.95 | 0.975 | 0.99 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mean excess | -0.0002 | +0.0035 | +0.0039 | +0.0036 | +0.0038 | +0.0040 | +0.0053 | +0.0067 | +0.0119 | +0.0161 | +0.0169 | +0.0168 | +0.0165 | +0.0162 | +0.0149 | +0.0137 | +0.0120 | +0.0111 | +0.0088 | +0.0065 | +0.0028 | +0.0018 | +0.0001 |

### gbm_funding_cal_direct over gbm_funding

Target days 2021-23.

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

Target days outside 2021-23.

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

### gbm_funding_cal_aligned over gbm_funding_cal_direct

Target days 2021-23.

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

Target days outside 2021-23.

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

### gbm_funding_cal_aligned over gbm_funding

Target days 2021-23.

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

Target days outside 2021-23.

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
