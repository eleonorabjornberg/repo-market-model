# Turn-day labels against the month-end label (#959; H5 step 2)

**Development data, not a verdict.** No verdict, no lockbox day scored (decision days with all five targets on or before 2025-12-31), and no published declaration, record or decided value moves. Every figure is read from `docs/research/turn-day-labels-959/result.json` by `scripts/turn_day_labels_959.py report`. The declaration, `metadata/turn_day_labels_959.json`, was committed before any number was computed.

**Questions for Eleonora (not settled here).** (1) Adopt the turn label for B2, and so for scoring protocol v1's B2 and its section 13? The definition of the labels is a data meaning. (2) How does the turn label relate to the open #800 ruling, the two readings of B2's day types?

## What was measured

The labels are functions of the date and the market holiday table (`repo_model.turn_days`): `turn` (the last business day of a month that is not a quarter's last month and the first of the next), `quarter_end_turn` (the quarter's last business day and the first after it), `year_end` (the last business day of December and the first of January), `tax_date` as the calendar column reads it, and `ordinary`: the penultimate and run-up days return to ordinary. 26 December is its own row and pools as ordinary. B2, the mean-reversion model (#686) and H6's calendar benchmark (#693) are unchanged: only the labels they group by are swapped. Skill is mean(d) / mean(S(benchmark)) with d = S(benchmark) − S(candidate), grid CRPS, positive favouring the candidate; the 90% interval is the studentized stationary bootstrap of ruling 1 (#739), seed 959, 200 draws. A group of fewer than 20 decision (or target) days is listed and not tested. By day type, a decision day's score is its mean over the leads whose target is of that type.

## (a) B2 relabelled against B2 as is

1900 decision days (2018-04-18 to 2025-12-23); 30 dropped for want of a sample of some lead's type in the trailing year, from every model.

### Relabelled B2 against B2 as is (skill of the relabelled)

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1900 | 2.438 | 2.510 | -3.0% [-12.9, -0.5] | -0.0720 [-0.3198, -0.0089] | candidate worse |
| regime 2018-19 | 407 | 3.865 | 4.151 | -7.4% [-45.9, -0.6] | -0.2860 [-2.1126, +0.0003] | candidate worse |
| regime 2020 | 251 | 2.786 | 2.871 | -3.1% [-5.2, -1.8] | -0.0852 [-0.1553, -0.0392] | candidate worse |
| regime 2021-23 | 748 | 1.481 | 1.508 | -1.8% [-7.1, +0.0] | -0.0269 [-0.1037, +0.0004] | no difference |
| regime 2024 | 250 | 1.378 | 1.341 | +2.7% [+0.9, +5.1] | +0.0373 [+0.0131, +0.0743] | candidate better |
| regime 2025-26 | 244 | 3.724 | 3.676 | +1.3% [-0.5, +3.0] | +0.0484 [-0.0007, +0.0988] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| target: december_26 | 22 | 8.312 | 8.435 | -1.5% [-2.3, -0.6] | -0.1238 [-0.3063, +0.0275] | candidate worse |
| target: ordinary | 1900 | 2.008 | 2.016 | -0.4% [-1.4, +0.7] | -0.0079 [-0.0281, +0.0136] | no difference |
| target: penultimate days | 449 | 2.192 | 2.122 | +3.2% [-6.6, +12.6] | +0.0694 [-0.1237, +0.2842] | no difference |
| target: quarter_end_turn | 132 | 4.978 | 5.305 | -6.6% [-28.3, +14.6] | -0.3268 [-1.4707, +0.5633] | no difference |
| target: tax_date | 222 | 7.052 | 7.052 | undefined: the daily difference has no long-run variance; it cannot be studentized | +0.0000 | scores identical |
| target: turn | 366 | 3.398 | 3.334 | +1.9% [-11.3, +11.1] | +0.0644 [-0.3772, +0.4321] | no difference |
| target: turn days (all three labels) | 535 | 3.931 | 4.629 | -17.7% [-88.5, +4.4] | -0.6976 [-3.3522, +0.1525] | no difference |
| target: year_end | 37 | 5.465 | 15.022 | -174.9% [-654.1, +65.5] | -9.5574 [-81.7189, +0.2637] | no difference |

### Relabelled B2 against B1

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1900 | 2.243 | 2.510 | -11.9% [-34.0, +17.3] | -0.2671 [-0.6151, +0.2926] | no difference |
| regime 2018-19 | 407 | 5.182 | 4.151 | +19.9% [-3.1, +54.3] | +1.0317 [-0.1265, +4.4814] | no difference |
| regime 2020 | 251 | 1.644 | 2.871 | -74.7% [-167.9, -13.2] | -1.2274 [-2.9111, -0.4474] | candidate worse |
| regime 2021-23 | 748 | 0.711 | 1.508 | -112.2% [-179.5, -67.2] | -0.7972 [-1.1954, -0.5337] | candidate worse |
| regime 2024 | 250 | 1.683 | 1.341 | +20.3% [+4.2, +39.6] | +0.3425 [+0.0472, +0.9952] | candidate better |
| regime 2025-26 | 244 | 3.231 | 3.676 | -13.8% [-55.3, +9.9] | -0.4447 [-1.8011, +0.3708] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| target: december_26 | 22 | 6.901 | 8.435 | -22.2% [-50.5, +15.4] | -1.5345 [-2.1662, -0.5056] | no difference |
| target: ordinary | 1900 | 1.899 | 2.016 | -6.2% [-29.1, +28.1] | -0.1169 [-0.4688, +0.5422] | no difference |
| target: penultimate days | 449 | 1.450 | 2.122 | -46.4% [-90.7, -2.7] | -0.6727 [-1.2788, -0.1886] | candidate worse |
| target: quarter_end_turn | 132 | 4.389 | 5.305 | -20.9% [-99.7, +16.1] | -0.9157 [-3.3873, +0.5861] | no difference |
| target: tax_date | 222 | 4.787 | 7.052 | -47.3% [-111.9, +57.9] | -2.2657 [-3.9506, -1.3621] | no difference |
| target: turn | 366 | 2.704 | 3.334 | -23.3% [-62.3, +1.3] | -0.6299 [-1.6293, +0.0386] | no difference |
| target: turn days (all three labels) | 535 | 3.119 | 4.629 | -48.4% [-148.4, -9.8] | -1.5098 [-4.4445, -0.3447] | candidate worse |
| target: year_end | 37 | 2.689 | 15.022 | -458.6% [-3670.7, +409.1] | -12.3329 [-119.7755, -1.0716] | no difference |

### B2 as is against B1, for the size of the gap

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1900 | 2.243 | 2.438 | -8.7% [-29.9, +21.1] | -0.1951 [-0.5380, +0.4456] | no difference |
| regime 2018-19 | 407 | 5.182 | 3.865 | +25.4% [+9.2, +67.3] | +1.3177 [+0.2361, +6.9718] | candidate better |
| regime 2020 | 251 | 1.644 | 2.786 | -69.5% [-168.6, -11.9] | -1.1422 [-2.8596, -0.3743] | candidate worse |
| regime 2021-23 | 748 | 0.711 | 1.481 | -108.4% [-171.7, -62.3] | -0.7703 [-1.1595, -0.5190] | candidate worse |
| regime 2024 | 250 | 1.683 | 1.378 | +18.1% [+3.1, +37.4] | +0.3051 [+0.0162, +0.9379] | candidate better |
| regime 2025-26 | 244 | 3.231 | 3.724 | -15.3% [-53.6, +7.6] | -0.4931 [-1.8443, +0.3102] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| target: december_26 | 22 | 6.901 | 8.312 | -20.4% [-52.1, +16.2] | -1.4107 [-2.1278, -0.2836] | no difference |
| target: ordinary | 1900 | 1.899 | 2.008 | -5.7% [-29.2, +27.1] | -0.1091 [-0.4583, +0.5574] | no difference |
| target: penultimate days | 449 | 1.450 | 2.192 | -51.2% [-102.8, -8.5] | -0.7421 [-1.3473, -0.2330] | candidate worse |
| target: quarter_end_turn | 132 | 4.389 | 4.978 | -13.4% [-60.0, +17.6] | -0.5889 [-2.0580, +0.8475] | no difference |
| target: tax_date | 222 | 4.787 | 7.052 | -47.3% [-111.9, +57.9] | -2.2657 [-3.9506, -1.3621] | no difference |
| target: turn | 366 | 2.704 | 3.398 | -25.7% [-55.5, -5.8] | -0.6942 [-1.7114, -0.1479] | candidate worse |
| target: turn days (all three labels) | 535 | 3.119 | 3.931 | -26.0% [-58.9, -1.1] | -0.8122 [-1.6345, -0.1229] | candidate worse |
| target: year_end | 37 | 2.689 | 5.465 | -103.2% [-691.5, +55.8] | -2.7754 [-16.8404, +0.0140] | no difference |

## (b) The mean-reversion level on the turn labels

1855 decision days (2018-07-19 to 2025-12-23). Refits: {"as is": 89, "turn days and tax dates excluded": 89, "turn days only excluded": 89}; decision days skipped for want of history: {"as is": 75, "turn days and tax dates excluded": 75, "turn days only excluded": 75}. The candidate is the #686 base model; the #761 variants pool by the same ordinary set and are not re-walked.

### Level set excluding only turn days (tax dates ordinary) against as is

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1855 | 1.778 | 1.796 | -1.0% [-4.0, +0.2] | -0.0177 [-0.0755, +0.0027] | no difference |
| regime 2018-19 | 362 | 3.820 | 3.881 | -1.6% [-8.9, +0.3] | -0.0611 [-0.3922, +0.0190] | no difference |
| regime 2020 | 251 | 1.550 | 1.543 | +0.5% [-0.9, +1.6] | +0.0071 [-0.0129, +0.0263] | no difference |
| regime 2021-23 | 748 | 0.725 | 0.740 | -2.0% [-7.1, -0.1] | -0.0146 [-0.0559, -0.0007] | candidate worse |
| regime 2024 | 250 | 1.318 | 1.325 | -0.5% [-3.1, +2.5] | -0.0063 [-0.0340, +0.0288] | no difference |
| regime 2025-26 | 244 | 2.685 | 2.685 | -0.0% [-1.6, +1.7] | -0.0002 [-0.0423, +0.0515] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| target: december_26 | 24 | 5.325 | 5.099 | +4.2% [+1.7, +5.4] | +0.2260 [-0.0038, +0.7389] | candidate better |
| target: ordinary | 1855 | 1.374 | 1.397 | -1.7% [-7.9, +0.1] | -0.0234 [-0.1097, +0.0018] | no difference |
| target: penultimate days | 447 | 1.353 | 1.412 | -4.4% [-23.3, -0.2] | -0.0589 [-0.3106, -0.0045] | candidate worse |
| target: quarter_end_turn | 132 | 4.565 | 4.556 | +0.2% [-2.5, +2.1] | +0.0087 [-0.1017, +0.1084] | no difference |
| target: tax_date | 214 | 4.871 | 4.911 | -0.8% [-1.2, -0.5] | -0.0408 [-0.1673, +0.0016] | candidate worse |
| target: turn | 360 | 2.465 | 2.445 | +0.8% [-0.0, +1.8] | +0.0204 [+0.0004, +0.0528] | no difference |
| target: turn days (all three labels) | 535 | 3.647 | 3.619 | +0.8% [-0.2, +1.5] | +0.0280 [-0.0068, +0.0638] | no difference |
| target: year_end | 43 | 10.722 | 10.571 | +1.4% [+0.2, +2.6] | +0.1512 [+0.0350, +0.4449] | candidate better |

### Level set excluding turn days and tax dates (the sensitivity) against as is

| group | decision days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1855 | 1.778 | 1.781 | -0.1% [-0.5, +0.2] | -0.0022 [-0.0091, +0.0037] | no difference |
| regime 2018-19 | 362 | 3.820 | 3.816 | +0.1% [-0.5, +0.6] | +0.0041 [-0.0202, +0.0210] | no difference |
| regime 2020 | 251 | 1.550 | 1.557 | -0.4% [-1.3, +0.5] | -0.0070 [-0.0216, +0.0070] | no difference |
| regime 2021-23 | 748 | 0.725 | 0.725 | +0.1% [-0.4, +0.8] | +0.0007 [-0.0029, +0.0053] | no difference |
| regime 2024 | 250 | 1.318 | 1.320 | -0.1% [-1.0, +0.8] | -0.0020 [-0.0133, +0.0090] | no difference |
| regime 2025-26 | 244 | 2.685 | 2.701 | -0.6% [-1.8, +0.7] | -0.0160 [-0.0463, +0.0220] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| target: december_26 | 24 | 5.325 | 5.389 | -1.2% [-5.2, +0.1] | -0.0640 [-0.4249, +0.0224] | no difference |
| target: ordinary | 1855 | 1.374 | 1.376 | -0.1% [-0.6, +0.3] | -0.0020 [-0.0082, +0.0041] | no difference |
| target: penultimate days | 447 | 1.353 | 1.356 | -0.2% [-0.9, +0.2] | -0.0032 [-0.0117, +0.0032] | no difference |
| target: quarter_end_turn | 132 | 4.565 | 4.546 | +0.4% [+0.2, +0.6] | +0.0188 [+0.0059, +0.0345] | candidate better |
| target: tax_date | 214 | 4.871 | 4.902 | -0.6% [-1.1, -0.1] | -0.0310 [-0.1262, +0.0073] | candidate worse |
| target: turn | 360 | 2.465 | 2.445 | +0.8% [+0.6, +1.1] | +0.0207 [+0.0104, +0.0341] | candidate better |
| target: turn days (all three labels) | 535 | 3.647 | 3.626 | +0.6% [+0.4, +0.8] | +0.0209 [+0.0127, +0.0292] | candidate better |
| target: year_end | 43 | 10.722 | 10.692 | +0.3% [-0.1, +0.6] | +0.0295 [+0.0156, +0.0462] | no difference |

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
| pooled | 391 | 3.036 | 4.147 | -36.6% [-81.0, +5.2] | -1.1107 [-1.9750, -0.4398] | no difference |
| regime 2018-19 | 83 | 8.600 | 9.041 | -5.1% [-30.0, +8.1] | -0.4403 [-1.9045, +0.5065] | no difference |
| regime 2020 | 52 | 1.127 | 3.991 | -254.2% [-871.8, -62.9] | -2.8645 [-12.2812, -0.6097] | candidate worse |
| regime 2021-23 | 158 | 0.725 | 1.946 | -168.4% [-361.9, -81.6] | -1.2206 [-2.1693, -0.6670] | candidate worse |
| regime 2024 | 51 | 1.951 | 2.170 | -11.2% [-26.3, +7.7] | -0.2188 [-0.5419, +0.0720] | no difference |
| regime 2025-26 | 47 | 4.268 | 5.220 | -22.3% [-193.2, +60.1] | -0.9524 [-8.8831, +1.9843] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| type: month_end | 153 | 2.302 | 2.924 | -27.0% [-58.3, -0.9] | -0.6221 [-1.3283, -0.0778] | candidate worse |
| type: quarter_end | 29 | 5.316 | 6.216 | -16.9% [-112.1, +39.7] | -0.9002 [-3.9715, +2.6147] | no difference |
| type: settlement | 116 | 1.605 | 2.491 | -55.2% [-121.4, +0.8] | -0.8860 [-1.5431, -0.1672] | no difference |
| type: tax_date | 93 | 5.317 | 7.578 | -42.5% [-101.6, +48.2] | -2.2603 [-3.7060, -1.4985] | no difference |

### turn set: calendar against B1 (1450 cells, 370 target days)

| group | target days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 370 | 3.285 | 4.791 | -45.9% [-110.9, -5.1] | -1.5069 [-3.4537, -0.7692] | candidate worse |
| regime 2018-19 | 76 | 9.484 | 10.550 | -11.2% [-97.5, +4.2] | -1.0655 [-6.2697, +0.4524] | no difference |
| regime 2020 | 51 | 1.152 | 5.755 | -399.4% [-1361.2, -51.9] | -4.6028 [-19.6904, +0.4244] | candidate worse |
| regime 2021-23 | 150 | 0.755 | 2.103 | -178.4% [-331.3, -94.5] | -1.3474 [-2.1648, -0.7982] | candidate worse |
| regime 2024 | 47 | 2.460 | 2.758 | -12.1% [-30.1, +3.0] | -0.2981 [-0.7391, +0.0029] | no difference |
| regime 2025-26 | 46 | 4.495 | 5.054 | -12.4% [-165.2, +43.5] | -0.5589 [-7.9029, +1.6445] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |
| type: quarter_end_turn | 44 | 4.361 | 5.311 | -21.8% [-114.8, +38.6] | -0.9497 [-3.6182, +1.5298] | no difference |
| type: settlement | 98 | 1.609 | 2.382 | -48.1% [-137.4, +24.7] | -0.7736 [-1.5067, -0.1134] | no difference |
| type: tax_date | 93 | 5.317 | 7.578 | -42.5% [-101.6, +48.2] | -2.2603 [-3.7060, -1.4985] | no difference |
| type: turn | 122 | 2.693 | 3.336 | -23.9% [-62.5, +2.9] | -0.6430 [-1.6008, +0.0581] | no difference |
| type: year_end | 13 | | | not tested (fewer than 20) | | |

### Turn set against as is, on the 1031 cells both call a risk date

| group | target days | benchmark CRPS | candidate CRPS | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 307 | 4.647 | 4.915 | -5.8% [-14.6, -2.5] | -0.2675 [-0.9457, -0.0799] | candidate worse |
| regime 2018-19 | 64 | 11.028 | 11.934 | -8.2% [-24.7, -1.7] | -0.9060 [-3.1235, -0.1682] | candidate worse |
| regime 2020 | 42 | 4.038 | 4.250 | -5.2% [-9.3, -1.9] | -0.2117 [-0.4683, -0.0862] | candidate worse |
| regime 2021-23 | 124 | 1.996 | 2.125 | -6.5% [-16.0, -2.1] | -0.1297 [-0.3097, -0.0367] | candidate worse |
| regime 2024 | 40 | 2.546 | 2.611 | -2.5% [-8.2, +6.2] | -0.0649 [-0.2942, +0.1707] | no difference |
| regime 2025-26 | 37 | 5.460 | 5.367 | +1.7% [-0.3, +3.9] | +0.0926 [-0.0459, +0.2498] | no difference |
| regime 2027 | 0 | | | not tested (fewer than 20) | | |

## What the tables show

- (a) pooled, relabelled B2 against B2 as is: skill -3.0% [-12.9, -0.5], candidate worse.
- (a) on the turn days: skill -17.7% [-88.5, +4.4], no difference.
- (a) on the penultimate days: skill +3.2% [-6.6, +12.6], no difference.
- (b) pooled, the level set excluding only turn days against as is: skill -1.0% [-4.0, +0.2], no difference.
- (b) on the turn days: skill +0.8% [-0.2, +1.5], no difference.
- (c) the calendar benchmark on the turn set against B1, pooled: skill -45.9% [-110.9, -5.1], candidate worse.
- (c) the turn set against as is on the common cells, pooled: skill -5.8% [-14.6, -2.5], candidate worse.

Nothing here is a verdict for a hypothesis; adopting the label is Eleonora's (#959). Development data, not a verdict.
