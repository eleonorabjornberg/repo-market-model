# Turn-day labels against the month-end label (#959; H5 step 2)

**Development data, not a verdict.** No verdict, no lockbox day scored (decision days with all five targets on or before 2025-12-31), and no published declaration, record or decided value moves. Every figure is read from `docs/research/turn-day-labels-959/result.json` by `scripts/turn_day_labels_959.py report`. The declaration, `metadata/turn_day_labels_959.json`, was committed before any number was computed.

**Questions for Eleonora (not settled here).** (1) Adopt the turn label for B2, and so for scoring protocol v1's B2 and its section 13? The definition of the labels is a data meaning. (2) How does the turn label relate to the open #800 ruling, the two readings of B2's day types?

## What was measured

The labels are functions of the date and the market holiday table (`repo_model.turn_days`): `turn` (the last business day of a month that is not a quarter's last month and the first of the next), `quarter_end_turn` (the quarter's last business day and the first after it), `year_end` (the last business day of December and the first of January), `tax_date` as the calendar column reads it, and `ordinary`: the penultimate and run-up days return to ordinary. 26 December is its own row and pools as ordinary. B2, the mean-reversion model (#686) and H6's calendar benchmark (#693) are unchanged: only the labels they group by are swapped. Skill is mean(d) / mean(S(benchmark)) with d = S(benchmark) − S(candidate), grid CRPS, positive favouring the candidate; the 90% interval is the studentized stationary bootstrap of ruling 1 (#739), seed 959, 10,000 draws. A group of fewer than 20 decision (or target) days is listed and not tested. By day type, a decision day's score is its mean over the leads whose target is of that type.

## (a) B2 relabelled against B2 as is

1900 decision days (2018-04-18 to 2025-12-23); 30 dropped for want of a sample of some lead's type in the trailing year, from every model.

### Relabelled B2 against B2 as is (skill of the relabelled)

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1900 | 2.438 | 2.510 | -3.0% [-13.0, -0.5] | -0.0720 [-0.3257, -0.0110] | candidate worse |
| regime 2018-19 | 407 | 3.865 | 4.151 | -7.4% [-49.4, -0.2] | -0.2860 [-2.0334, -0.0111] | candidate worse |
| regime 2020 | 251 | 2.786 | 2.871 | -3.1% [-5.1, -1.6] | -0.0852 [-0.1590, -0.0403] | candidate worse |
| regime 2021-23 | 748 | 1.481 | 1.508 | -1.8% [-7.5, +0.1] | -0.0269 [-0.1095, +0.0017] | no difference |
| regime 2024 | 250 | 1.378 | 1.341 | +2.7% [+0.9, +5.0] | +0.0373 [+0.0139, +0.0751] | candidate better |
| regime 2025-26 | 244 | 3.724 | 3.676 | +1.3% [-0.3, +3.0] | +0.0484 [+0.0041, +0.0964] | no difference |
| target: december_26 | 22 | 8.312 | 8.435 | -1.5% [-2.2, -0.6] | -0.1238 [-0.2856, +0.0937] | candidate worse |
| target: ordinary | 1900 | 2.008 | 2.016 | -0.4% [-1.4, +0.7] | -0.0079 [-0.0290, +0.0127] | no difference |
| target: penultimate days | 449 | 2.192 | 2.122 | +3.2% [-6.8, +14.6] | +0.0694 [-0.1358, +0.3443] | no difference |
| target: quarter_end_turn | 132 | 4.978 | 5.305 | -6.6% [-36.0, +17.3] | -0.3268 [-1.8732, +0.6597] | no difference |
| target: tax_date | 222 | 7.052 | 7.052 | undefined: the daily difference has no long-run variance; it cannot be studentized | +0.0000 | scores identical |
| target: turn | 366 | 3.398 | 3.334 | +1.9% [-14.5, +11.8] | +0.0644 [-0.4299, +0.4445] | no difference |
| target: turn days (all three labels) | 535 | 3.931 | 4.629 | -17.7% [-88.4, +3.9] | -0.6976 [-3.5522, +0.1209] | no difference |
| target: year_end | 37 | 5.465 | 15.022 | -174.9% [-603.5, +49.3] | -9.5574 [-75.0038, +0.0104] | no difference |

### Relabelled B2 against B1

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1900 | 2.243 | 2.510 | -11.9% [-33.6, +19.1] | -0.2671 [-0.6191, +0.3448] | no difference |
| regime 2018-19 | 407 | 5.182 | 4.151 | +19.9% [-5.3, +51.6] | +1.0317 [-0.2279, +4.2399] | no difference |
| regime 2020 | 251 | 1.644 | 2.871 | -74.7% [-186.8, +3.8] | -1.2274 [-2.9427, -0.3446] | no difference |
| regime 2021-23 | 748 | 0.711 | 1.508 | -112.2% [-172.9, -67.0] | -0.7972 [-1.1568, -0.5200] | candidate worse |
| regime 2024 | 250 | 1.683 | 1.341 | +20.3% [+3.1, +39.4] | +0.3425 [+0.0330, +1.0073] | candidate better |
| regime 2025-26 | 244 | 3.231 | 3.676 | -13.8% [-51.0, +12.2] | -0.4447 [-1.7331, +0.4090] | no difference |
| target: december_26 | 22 | 6.901 | 8.435 | -22.2% [-54.9, +13.4] | -1.5345 [-2.1779, -0.5057] | no difference |
| target: ordinary | 1900 | 1.899 | 2.016 | -6.2% [-27.1, +29.1] | -0.1169 [-0.4316, +0.5663] | no difference |
| target: penultimate days | 449 | 1.450 | 2.122 | -46.4% [-94.4, -6.5] | -0.6727 [-1.3345, -0.1824] | candidate worse |
| target: quarter_end_turn | 132 | 4.389 | 5.305 | -20.9% [-98.4, +19.7] | -0.9157 [-3.4193, +0.9436] | no difference |
| target: tax_date | 222 | 4.787 | 7.052 | -47.3% [-117.0, +54.4] | -2.2657 [-3.7019, -1.4009] | no difference |
| target: turn | 366 | 2.704 | 3.334 | -23.3% [-64.1, +3.1] | -0.6299 [-1.7229, +0.0477] | no difference |
| target: turn days (all three labels) | 535 | 3.119 | 4.629 | -48.4% [-155.4, -8.9] | -1.5098 [-4.5698, -0.3535] | candidate worse |
| target: year_end | 37 | 2.689 | 15.022 | -458.6% [-3451.1, +360.3] | -12.3329 [-117.3930, -0.3803] | no difference |

### B2 as is against B1, for the size of the gap

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1900 | 2.243 | 2.438 | -8.7% [-28.8, +23.1] | -0.1951 [-0.5257, +0.4751] | no difference |
| regime 2018-19 | 407 | 5.182 | 3.865 | +25.4% [+7.4, +61.9] | +1.3177 [+0.1590, +6.1402] | candidate better |
| regime 2020 | 251 | 1.644 | 2.786 | -69.5% [-178.8, +5.4] | -1.1422 [-2.8148, -0.2830] | no difference |
| regime 2021-23 | 748 | 0.711 | 1.481 | -108.4% [-169.6, -63.6] | -0.7703 [-1.1335, -0.4884] | candidate worse |
| regime 2024 | 250 | 1.683 | 1.378 | +18.1% [+1.5, +36.9] | +0.3051 [+0.0106, +0.9363] | candidate better |
| regime 2025-26 | 244 | 3.231 | 3.724 | -15.3% [-50.8, +9.4] | -0.4931 [-1.7382, +0.3265] | no difference |
| target: december_26 | 22 | 6.901 | 8.312 | -20.4% [-54.7, +14.4] | -1.4107 [-2.1542, -0.2396] | no difference |
| target: ordinary | 1900 | 1.899 | 2.008 | -5.7% [-26.9, +29.3] | -0.1091 [-0.4269, +0.5771] | no difference |
| target: penultimate days | 449 | 1.450 | 2.192 | -51.2% [-109.5, -8.5] | -0.7421 [-1.5183, -0.1875] | candidate worse |
| target: quarter_end_turn | 132 | 4.389 | 4.978 | -13.4% [-62.5, +17.8] | -0.5889 [-2.0681, +0.8900] | no difference |
| target: tax_date | 222 | 4.787 | 7.052 | -47.3% [-117.0, +54.4] | -2.2657 [-3.7019, -1.4009] | no difference |
| target: turn | 366 | 2.704 | 3.398 | -25.7% [-56.5, -4.3] | -0.6942 [-1.6977, -0.1673] | candidate worse |
| target: turn days (all three labels) | 535 | 3.119 | 3.931 | -26.0% [-56.4, -1.7] | -0.8122 [-1.6378, -0.1625] | candidate worse |
| target: year_end | 37 | 2.689 | 5.465 | -103.2% [-686.5, +59.7] | -2.7754 [-20.9024, -0.1570] | no difference |

## (b) The mean-reversion level on the turn labels

1855 decision days (2018-07-19 to 2025-12-23). Refits: {"as is": 89, "turn days and tax dates excluded": 89, "turn days only excluded": 89}; decision days skipped for want of history: {"as is": 75, "turn days and tax dates excluded": 75, "turn days only excluded": 75}. The candidate is the #686 base model; the #761 variants pool by the same ordinary set and are not re-walked.

### Level set excluding only turn days (tax dates ordinary) against as is

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1855 | 1.778 | 1.796 | -1.0% [-3.7, +0.1] | -0.0177 [-0.0673, +0.0026] | no difference |
| regime 2018-19 | 362 | 3.820 | 3.881 | -1.6% [-8.9, +0.6] | -0.0611 [-0.3863, +0.0286] | no difference |
| regime 2020 | 251 | 1.550 | 1.543 | +0.5% [-0.9, +1.6] | +0.0071 [-0.0143, +0.0281] | no difference |
| regime 2021-23 | 748 | 0.725 | 0.740 | -2.0% [-7.0, +0.1] | -0.0146 [-0.0557, +0.0001] | no difference |
| regime 2024 | 250 | 1.318 | 1.325 | -0.5% [-2.7, +2.6] | -0.0063 [-0.0326, +0.0285] | no difference |
| regime 2025-26 | 244 | 2.685 | 2.685 | -0.0% [-1.5, +1.5] | -0.0002 [-0.0390, +0.0429] | no difference |
| target: december_26 | 24 | 5.325 | 5.099 | +4.2% [+1.8, +5.9] | +0.2260 [+0.0341, +0.7705] | candidate better |
| target: ordinary | 1855 | 1.374 | 1.397 | -1.7% [-7.3, +0.2] | -0.0234 [-0.1008, +0.0028] | no difference |
| target: penultimate days | 447 | 1.353 | 1.412 | -4.4% [-23.4, +0.2] | -0.0589 [-0.3303, +0.0003] | no difference |
| target: quarter_end_turn | 132 | 4.565 | 4.556 | +0.2% [-2.5, +2.3] | +0.0087 [-0.1004, +0.1189] | no difference |
| target: tax_date | 214 | 4.871 | 4.911 | -0.8% [-1.2, -0.5] | -0.0408 [-0.1562, +0.0006] | candidate worse |
| target: turn | 360 | 2.465 | 2.445 | +0.8% [-0.0, +1.9] | +0.0204 [-0.0015, +0.0535] | no difference |
| target: turn days (all three labels) | 535 | 3.647 | 3.619 | +0.8% [-0.2, +1.6] | +0.0280 [-0.0083, +0.0665] | no difference |
| target: year_end | 43 | 10.722 | 10.571 | +1.4% [+0.2, +2.9] | +0.1512 [+0.0315, +0.4453] | candidate better |

### Level set excluding turn days and tax dates (the sensitivity) against as is

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1855 | 1.778 | 1.781 | -0.1% [-0.5, +0.2] | -0.0022 [-0.0087, +0.0038] | no difference |
| regime 2018-19 | 362 | 3.820 | 3.816 | +0.1% [-0.5, +0.7] | +0.0041 [-0.0184, +0.0210] | no difference |
| regime 2020 | 251 | 1.550 | 1.557 | -0.4% [-1.4, +0.4] | -0.0070 [-0.0227, +0.0068] | no difference |
| regime 2021-23 | 748 | 0.725 | 0.725 | +0.1% [-0.5, +0.7] | +0.0007 [-0.0033, +0.0052] | no difference |
| regime 2024 | 250 | 1.318 | 1.320 | -0.1% [-1.0, +0.8] | -0.0020 [-0.0126, +0.0095] | no difference |
| regime 2025-26 | 244 | 2.685 | 2.701 | -0.6% [-1.8, +0.6] | -0.0160 [-0.0468, +0.0174] | no difference |
| target: december_26 | 24 | 5.325 | 5.389 | -1.2% [-5.1, +0.3] | -0.0640 [-0.4397, +0.0287] | no difference |
| target: ordinary | 1855 | 1.374 | 1.376 | -0.1% [-0.6, +0.3] | -0.0020 [-0.0082, +0.0045] | no difference |
| target: penultimate days | 447 | 1.353 | 1.356 | -0.2% [-0.9, +0.3] | -0.0032 [-0.0117, +0.0037] | no difference |
| target: quarter_end_turn | 132 | 4.565 | 4.546 | +0.4% [+0.2, +0.6] | +0.0188 [+0.0065, +0.0372] | candidate better |
| target: tax_date | 214 | 4.871 | 4.902 | -0.6% [-1.1, -0.1] | -0.0310 [-0.1184, +0.0090] | candidate worse |
| target: turn | 360 | 2.465 | 2.445 | +0.8% [+0.6, +1.2] | +0.0207 [+0.0107, +0.0333] | candidate better |
| target: turn days (all three labels) | 535 | 3.647 | 3.626 | +0.6% [+0.4, +0.8] | +0.0209 [+0.0128, +0.0310] | candidate better |
| target: year_end | 43 | 10.722 | 10.692 | +0.3% [-0.1, +0.7] | +0.0295 [+0.0144, +0.0439] | no difference |

## (c) H6's risk-date set re-read

The risk-date calendar benchmark of #693 (the trailing year's spreads of the target's risk type) on the set in which the quarter-end and month-end types are replaced by the turn labels, against the same benchmark as is. The #693 type × state model is not re-run (the declaration says why). Counts of days by type, to the last scored day:

| set | counts by type |
|---|---|
| as is | month_end: 155, not a risk date: 1535, quarter_end: 31, settlement: 119, tax_date: 95 |
| turn set | not a risk date: 1554, quarter_end_turn: 46, settlement: 101, tax_date: 95, turn: 124, year_end: 15 |

1900 decision days. On each set the calendar benchmark is read against B1 on that set's risk target days (the unit is the target day, as in #693):


### as is: calendar against B1 (1472 cells, 391 target days)

| group | target days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 391 | 3.036 | 4.147 | -36.6% [-87.2, +4.4] | -1.1107 [-2.0138, -0.5064] | no difference |
| regime 2018-19 | 83 | 8.600 | 9.041 | -5.1% [-28.6, +7.1] | -0.4403 [-1.8932, +0.4547] | no difference |
| regime 2020 | 52 | 1.127 | 3.991 | -254.2% [-848.6, -48.8] | -2.8645 [-11.1648, -0.3763] | candidate worse |
| regime 2021-23 | 158 | 0.725 | 1.946 | -168.4% [-365.4, -85.2] | -1.2206 [-2.1503, -0.6548] | candidate worse |
| regime 2024 | 51 | 1.951 | 2.170 | -11.2% [-30.5, +6.1] | -0.2188 [-0.5533, +0.0329] | no difference |
| regime 2025-26 | 47 | 4.268 | 5.220 | -22.3% [-184.2, +54.3] | -0.9524 [-8.7551, +1.7987] | no difference |
| type: month_end | 153 | 2.302 | 2.924 | -27.0% [-63.6, -0.2] | -0.6221 [-1.3985, -0.0656] | candidate worse |
| type: quarter_end | 29 | 5.316 | 6.216 | -16.9% [-100.0, +33.9] | -0.9002 [-3.7571, +2.0024] | no difference |
| type: settlement | 116 | 1.605 | 2.491 | -55.2% [-138.1, +1.9] | -0.8860 [-1.7121, -0.2386] | no difference |
| type: tax_date | 93 | 5.317 | 7.578 | -42.5% [-102.8, +47.1] | -2.2603 [-3.9297, -1.3112] | no difference |

### turn set: calendar against B1 (1450 cells, 370 target days)

| group | target days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 370 | 3.285 | 4.791 | -45.9% [-121.5, -2.0] | -1.5069 [-3.5003, -0.6802] | candidate worse |
| regime 2018-19 | 76 | 9.484 | 10.550 | -11.2% [-96.4, +6.3] | -1.0655 [-6.4784, +0.2480] | no difference |
| regime 2020 | 51 | 1.152 | 5.755 | -399.4% [-1051.8, -98.3] | -4.6028 [-13.7731, -0.3479] | candidate worse |
| regime 2021-23 | 150 | 0.755 | 2.103 | -178.4% [-380.1, -87.5] | -1.3474 [-2.2365, -0.7464] | candidate worse |
| regime 2024 | 47 | 2.460 | 2.758 | -12.1% [-31.6, +5.7] | -0.2981 [-0.7734, +0.0476] | no difference |
| regime 2025-26 | 46 | 4.495 | 5.054 | -12.4% [-157.7, +50.7] | -0.5589 [-7.4103, +1.7921] | no difference |
| type: quarter_end_turn | 44 | 4.361 | 5.311 | -21.8% [-112.3, +35.8] | -0.9497 [-3.5591, +1.6957] | no difference |
| type: settlement | 98 | 1.609 | 2.382 | -48.1% [-136.8, +23.3] | -0.7736 [-1.5442, -0.0585] | no difference |
| type: tax_date | 93 | 5.317 | 7.578 | -42.5% [-102.8, +47.1] | -2.2603 [-3.9297, -1.3112] | no difference |
| type: turn | 122 | 2.693 | 3.336 | -23.9% [-66.2, +3.1] | -0.6430 [-1.6865, +0.0282] | no difference |
| type: year_end | 13 | | | not tested (fewer than 20) | | |

### Turn set against as is, on the 1031 cells both call a risk date

| group | target days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 307 | 4.647 | 4.915 | -5.8% [-14.7, -2.4] | -0.2675 [-0.9039, -0.0803] | candidate worse |
| regime 2018-19 | 64 | 11.028 | 11.934 | -8.2% [-27.5, -0.4] | -0.9060 [-3.9759, -0.0722] | candidate worse |
| regime 2020 | 42 | 4.038 | 4.250 | -5.2% [-9.6, -1.8] | -0.2117 [-0.4306, -0.0874] | candidate worse |
| regime 2021-23 | 124 | 1.996 | 2.125 | -6.5% [-18.5, -1.9] | -0.1297 [-0.3403, -0.0303] | candidate worse |
| regime 2024 | 40 | 2.546 | 2.611 | -2.5% [-8.3, +4.8] | -0.0649 [-0.2957, +0.1318] | no difference |
| regime 2025-26 | 37 | 5.460 | 5.367 | +1.7% [-0.5, +4.0] | +0.0926 [-0.0525, +0.2668] | no difference |

## What the tables show

- (a) pooled, relabelled B2 against B2 as is: skill -3.0% [-13.0, -0.5], candidate worse.
- (a) on the turn days: skill -17.7% [-88.4, +3.9], no difference.
- (a) on the penultimate days: skill +3.2% [-6.8, +14.6], no difference.
- (b) pooled, the level set excluding only turn days against as is: skill -1.0% [-3.7, +0.1], no difference.
- (b) on the turn days: skill +0.8% [-0.2, +1.6], no difference.
- (c) the calendar benchmark on the turn set against B1, pooled: skill -45.9% [-121.5, -2.0], candidate worse.
- (c) the turn set against as is on the common cells, pooled: skill -5.8% [-14.7, -2.4], candidate worse.

B2 samples the trailing year, so by construction the relabelled pools are small: a year holds two `year_end` days and six `quarter_end_turn` days, against about 16 `turn` days (the as-is pools: four `quarter_end` days and about 24 `month_end` days). The `year_end` rows above are scored on those two days' spreads; read them with that in mind. Whether a pooled alternative (for example `year_end` with `quarter_end_turn`) is worth a variant is Eleonora's; it is not run here.

Nothing here is a verdict for a hypothesis; adopting the label is Eleonora's (#959). Development data, not a verdict.
