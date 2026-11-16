# The quarter-end correction from an expanding pool of past turns

Terms such as arm, cell, kill rule, grid CRPS and B1 are defined in the [glossary](glossary.md). Issue numbers and files are in the Record at the end.

## The question

**Does drawing the quarter-end correction from every past quarter-end turn, instead of only the turns inside the candidate's two-year fit window, repair the candidate's quarter-end bands?** The earlier quarter-end arms drew on at most eight turns, so the weight they gave the quarter-end evidence stayed under half. This study gives the same correction the whole public history up to the decision. It is H5, step 3, a development study.

Register: settled-questions entry Q9 (the quarter-end family) is the one touched; S5 (a longer history for the whole fit, which lost) is a different question, because here the fit, the centre and the candidate's own pool keep their two-year window and only the quarter-end residuals reach back.

## The answer

**(s3c-ann-net-x), arm (i), expanding pool.** The arm's 90% band covers 0.780 [0.694, 0.863] of the group's cells against 0.601 for the candidate; the gap to 90% is 12.0 percentage points. Coverage gain, arm minus candidate: +0.179 [+0.090, +0.273]. Grid CRPS on the group, arm minus candidate: +0.002 [-0.336, +0.380] bp. Weight w reached (lead 1; every lead reads the same turns): the pool: mean 0.523, greatest 0.750. **Against the declared kill: killed.**

**(s3c-ann-net-xs), arm (ii), separate pools.** The arm's 90% band covers 0.756 [0.667, 0.839] of the group's cells against 0.601 for the candidate; the gap to 90% is 14.4 percentage points. Coverage gain, arm minus candidate: +0.155 [+0.071, +0.247]. Grid CRPS on the group, arm minus candidate: -0.096 [-0.397, +0.244] bp. Weight w reached (lead 1; every lead reads the same turns): quarter end turn pool: mean 0.459, greatest 0.697; year end pool: mean 0.151, greatest 0.412. **Against the declared kill: not killed.**

The regime table under each arm below is the one to read first: older turns come from other regimes, and a gain that sits in one regime or in a few events is not one to lean on.

## Method

On quarter-end and year-end target days the candidate's band is blended with one built from past quarter-end errors, as in #1548; the weight is n / (n + 20), n the number of past pairs at that lead. What changes is n: every past pair up to the decision counts, and an older pair's error is measured with the coefficients and scale of the refit in force at the decision. Arm (i) pools the quarter-end turns and the year-ends. Arm (ii) keeps the year-ends in a pool of their own, apart from the other quarter-ends. Every other forecast is the candidate's, unchanged. Each arm is killed on the rule of #1548: its 90% band does not cover more of the group's outcomes than the candidate's beyond its interval, or its forecasts on those days score worse.

Intervals on the group are 90% percentile intervals of a cluster bootstrap over turn events (2,000 resamples, seed 1548); against the benchmarks they are the studentized stationary bootstrap (10,000 draws, seed 1548). The development window is read; the 2026 development days are shown apart and decide nothing. Nothing here is a verdict, a choice or an adoption, and (s3c-ann-net) stays frozen.

## Result on the development window (targets up to 2025-12-31)

#### (s3c-ann-net-x), arm (i), expanding pool

Group cells 291, of which the arm changes 251; cells outside the group 8,984, every one identical to the candidate (the walk fails otherwise). The group holds 30 turn events. **That is few, so every interval is wide.**

**By regime of the event (read first).** Cells of fewer than 5 events are flagged.

| set | regime of the event | events | cells | flag | 90% coverage: cand. / arm; d [interval] | above q95 (5%): cand. / arm; d [interval] | below q01 (1%): cand. / arm; d [interval] | grid CRPS: cand. / arm; d [interval] (negative favours the arm) | upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm) |
|---|---|---|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 30 | 291 |  | 0.601 / 0.780; d +0.179 [+0.090, +0.273] | 0.309 / 0.117; d -0.192 [-0.284, -0.107] | 0.045 / 0.072; d +0.027 [+0.007, +0.053] | 4.722 / 4.723; d +0.002 [-0.336, +0.380] | 3.511 / 3.642; d +0.131 [-0.130, +0.435] |
| group (turns and year-ends) | 2018-19 | 6 | 60 |  | 0.500 / 0.483; d -0.017 [-0.050, +0.000] | 0.417 / 0.417; d +0.000 [+0.000, +0.000] | 0.033 / 0.067; d +0.033 [+0.000, +0.100] | 12.697 / 12.860; d +0.163 [-0.226, +0.714] | 12.612 / 12.762; d +0.150 [-0.223, +0.673] |
| group (turns and year-ends) | 2020 | 4 | 40 | **few events (4)** | 0.550 / 0.525; d -0.025 [-0.075, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.275 / 0.350; d +0.075 [+0.000, +0.150] | 4.485 / 5.913; d +1.428 [+0.388, +3.368] | 2.076 / 3.402; d +1.326 [+0.410, +3.003] |
| group (turns and year-ends) | 2021-23 | 12 | 120 |  | 0.742 / 0.933; d +0.192 [+0.075, +0.317] | 0.233 / 0.025; d -0.208 [-0.325, -0.100] | 0.000 / 0.025; d +0.025 [+0.000, +0.075] | 1.097 / 0.983; d -0.114 [-0.336, +0.085] | 0.003 / 0.020; d +0.017 [+0.000, +0.049] |
| group (turns and year-ends) | 2024 | 4 | 40 | **few events (4)** | 0.425 / 0.875; d +0.450 [+0.200, +0.700] | 0.575 / 0.125; d -0.450 [-0.700, -0.200] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 4.245 / 3.575; d -0.671 [-1.893, +0.296] | 2.724 / 2.374; d -0.350 [-1.464, +0.402] |
| group (turns and year-ends) | 2025-26 | 4 | 31 | **few events (4)** | 0.548 / 0.968; d +0.419 [+0.000, +0.909] | 0.452 / 0.032; d -0.419 [-0.909, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 4.233 / 3.397; d -0.836 [-1.916, -0.120] | 2.340 / 1.958; d -0.383 [-0.979, +0.099] |
| quarter-end turns | all regimes | 22 | 220 |  | 0.586 / 0.800; d +0.214 [+0.100, +0.332] | 0.336 / 0.105; d -0.232 [-0.345, -0.127] | 0.041 / 0.059; d +0.018 [+0.000, +0.041] | 3.512 / 3.380; d -0.132 [-0.555, +0.322] | 2.136 / 2.165; d +0.029 [-0.302, +0.380] |
| quarter-end turns | 2018-19 | 4 | 40 | **few events (4)** | 0.625 / 0.600; d -0.025 [-0.050, +0.000] | 0.375 / 0.375; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 6.018 / 5.848; d -0.170 [-0.339, +0.000] | 5.950 / 5.782; d -0.168 [-0.335, +0.000] |
| quarter-end turns | 2020 | 3 | 30 | **few events (3)** | 0.533 / 0.500; d -0.033 [-0.067, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.300 / 0.333; d +0.033 [+0.000, +0.067] | 5.398 / 7.118; d +1.720 [+0.364, +3.077] | 2.621 / 4.177; d +1.557 [+0.381, +2.733] |
| quarter-end turns | 2021-23 | 9 | 90 |  | 0.711 / 0.911; d +0.200 [+0.067, +0.333] | 0.256 / 0.033; d -0.222 [-0.344, -0.100] | 0.000 / 0.033; d +0.033 [+0.000, +0.100] | 1.095 / 0.971; d -0.125 [-0.389, +0.111] | 0.000 / 0.000; d +0.000 [+0.000, +0.001] |
| quarter-end turns | 2024 | 3 | 30 | **few events (3)** | 0.233 / 0.833; d +0.600 [+0.433, +0.767] | 0.767 / 0.167; d -0.600 [-0.767, -0.433] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 5.073 / 3.855; d -1.218 [-2.041, -0.394] | 3.092 / 2.372; d -0.720 [-1.470, +0.029] |
| quarter-end turns | 2025-26 | 3 | 30 | **few events (3)** | 0.567 / 1.000; d +0.433 [+0.100, +0.767] | 0.433 / 0.000; d -0.433 [-0.767, -0.100] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 3.974 / 3.104; d -0.870 [-1.536, -0.205] | 2.018 / 1.617; d -0.401 [-0.798, -0.005] |
| year-ends | all regimes | 8 | 71 |  | 0.648 / 0.718; d +0.070 [+0.000, +0.189] | 0.225 / 0.155; d -0.070 [-0.189, +0.000] | 0.056 / 0.113; d +0.056 [+0.000, +0.113] | 8.469 / 8.885; d +0.415 [+0.024, +0.830] | 7.771 / 8.219; d +0.447 [+0.128, +0.800] |
| year-ends | 2018-19 | 2 | 20 | **few events (2)** | 0.250 / 0.250; d +0.000 [+0.000, +0.000] | 0.500 / 0.500; d +0.000 [+0.000, +0.000] | 0.100 / 0.200; d +0.100 [+0.000, +0.200] | 26.056 / 26.883; d +0.827 [+0.000, +1.655] | 25.937 / 26.722; d +0.785 [+0.000, +1.570] |
| year-ends | 2020 | 1 | 10 | **few events (1)** | 0.600 / 0.600; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.200 / 0.400; d +0.200 [+0.200, +0.200] | 1.748 / 2.300; d +0.551 [+0.551, +0.551] | 0.441 / 1.075; d +0.633 [+0.633, +0.633] |
| year-ends | 2021-23 | 3 | 30 | **few events (3)** | 0.833 / 1.000; d +0.167 [+0.000, +0.333] | 0.167 / 0.000; d -0.167 [-0.333, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.103 / 1.020; d -0.083 [-0.376, +0.210] | 0.013 / 0.079; d +0.065 [+0.000, +0.131] |
| year-ends | 2024 | 1 | 10 | **few events (1)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.764 / 2.734; d +0.970 [+0.970, +0.970] | 1.619 / 2.380; d +0.761 [+0.761, +0.761] |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 12.001 / 12.200; d +0.199 [+0.199, +0.199] | 12.001 / 12.171; d +0.170 [+0.170, +0.170] |

**Coverage and tail misses on the group, candidate against arm.**

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 291 | 30 | 0.601 [0.498, 0.703] | 0.780 [0.694, 0.863] | +0.179 [+0.090, +0.273] | 0.089 / 0.103 | 0.309 / 0.117 | 0.045 / 0.072 | 0.127 / 0.086 |
| group, h = 1 | 58 | 29 | 0.638 [0.534, 0.741] | 0.810 [0.724, 0.897] | +0.172 [+0.069, +0.276] | 0.086 / 0.103 | 0.276 / 0.086 | 0.017 / 0.052 | 0.155 / 0.069 |
| group, h = 2 | 58 | 29 | 0.638 [0.517, 0.741] | 0.810 [0.724, 0.897] | +0.172 [+0.086, +0.276] | 0.086 / 0.086 | 0.276 / 0.103 | 0.034 / 0.069 | 0.103 / 0.069 |
| group, h = 3 | 58 | 29 | 0.621 [0.517, 0.724] | 0.776 [0.690, 0.862] | +0.155 [+0.069, +0.259] | 0.086 / 0.103 | 0.293 / 0.121 | 0.052 / 0.086 | 0.103 / 0.086 |
| group, h = 4 | 58 | 29 | 0.534 [0.414, 0.655] | 0.741 [0.621, 0.862] | +0.207 [+0.103, +0.328] | 0.103 / 0.121 | 0.362 / 0.138 | 0.069 / 0.086 | 0.121 / 0.103 |
| group, h = 5 | 59 | 30 | 0.576 [0.446, 0.700] | 0.763 [0.655, 0.867] | +0.186 [+0.083, +0.305] | 0.085 / 0.102 | 0.339 / 0.136 | 0.051 / 0.068 | 0.153 / 0.102 |
| group, quarter_end_turn only | 220 | 22 | 0.586 [0.468, 0.705] | 0.800 [0.714, 0.886] | +0.214 [+0.100, +0.332] | 0.077 / 0.095 | 0.336 / 0.105 | 0.041 / 0.059 | 0.109 / 0.064 |
| group, year_end only | 71 | 8 | 0.648 [0.419, 0.845] | 0.718 [0.484, 0.915] | +0.070 [+0.000, +0.189] | 0.127 / 0.127 | 0.225 / 0.155 | 0.056 / 0.113 | 0.183 / 0.155 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 146 | 30 | 0.493 [0.359, 0.627] | 0.671 [0.547, 0.793] | +0.178 [+0.070, +0.300] | 0.164 / 0.178 | 0.342 / 0.151 | 0.089 / 0.144 | 0.137 / 0.103 |

**The arm's 90% band covers 0.780 [0.694, 0.863] of the group's cells against 0.601 for the candidate; the gap to 90% is 12.0 percentage points.**

**Accuracy on the group (paired, same cells).** Negative favors the arm.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 4.722 | 4.723 | +0.002 [-0.336, +0.380] | 3.511 | 3.642 | +0.131 [-0.130, +0.435] |
| group, h = 1 | 4.509 | 4.507 | -0.002 [-0.340, +0.356] | 3.449 | 3.566 | +0.116 [-0.122, +0.383] |
| group, h = 2 | 4.490 | 4.596 | +0.105 [-0.197, +0.456] | 3.527 | 3.683 | +0.156 [-0.084, +0.436] |
| group, h = 3 | 4.724 | 4.764 | +0.040 [-0.300, +0.431] | 3.526 | 3.684 | +0.158 [-0.116, +0.479] |
| group, h = 4 | 4.932 | 4.878 | -0.053 [-0.432, +0.381] | 3.522 | 3.644 | +0.122 [-0.163, +0.473] |
| group, h = 5 | 4.949 | 4.868 | -0.080 [-0.435, +0.317] | 3.530 | 3.634 | +0.104 [-0.157, +0.424] |
| group, quarter_end_turn only | 3.512 | 3.380 | -0.132 [-0.555, +0.322] | 2.136 | 2.165 | +0.029 [-0.302, +0.380] |
| group, year_end only | 8.469 | 8.885 | +0.415 [+0.024, +0.830] | 7.771 | 8.219 | +0.447 [+0.128, +0.800] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 5.153 | 4.991 | -0.161 [-0.779, +0.374] | 3.964 | 3.878 | -0.086 [-0.669, +0.419] |

**The weight w the event pool reached, per lead, over the window's refits.**

Event pool: one pool of quarter-end turns and year-ends.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 31.0 (2 to 60) | 0.523 (0.000 to 0.750) | 0.13 | +1.094 | 2.987 |
| h=2 | 31.0 (2 to 60) | 0.523 (0.000 to 0.750) | 0.13 | +1.009 | 2.614 |
| h=3 | 31.0 (2 to 60) | 0.523 (0.000 to 0.750) | 0.13 | +1.436 | 2.602 |
| h=4 | 31.0 (2 to 60) | 0.523 (0.000 to 0.750) | 0.13 | +1.948 | 2.542 |
| h=5 | 31.0 (2 to 60) | 0.523 (0.000 to 0.750) | 0.13 | +1.827 | 2.367 |

**The declared kill (that of #1548, applied to this arm on its own).** Coverage on the group: +0.179 [+0.090, +0.273] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is above zero, so the arm improves beyond its interval. Grid CRPS on the group: +0.002 [-0.336, +0.380] bp (arm minus candidate). The arm's is above the candidate's, so the arm loses. **Against the declared kill: killed.**

#### (s3c-ann-net-xs), arm (ii), separate pools

Group cells 291, of which the arm changes 201; cells outside the group 8,984, every one identical to the candidate (the walk fails otherwise). The group holds 30 turn events. **That is few, so every interval is wide.**

**By regime of the event (read first).** Cells of fewer than 5 events are flagged.

| set | regime of the event | events | cells | flag | 90% coverage: cand. / arm; d [interval] | above q95 (5%): cand. / arm; d [interval] | below q01 (1%): cand. / arm; d [interval] | grid CRPS: cand. / arm; d [interval] (negative favours the arm) | upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm) |
|---|---|---|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 30 | 291 |  | 0.601 / 0.756; d +0.155 [+0.071, +0.247] | 0.309 / 0.141; d -0.168 [-0.259, -0.089] | 0.045 / 0.062; d +0.017 [+0.003, +0.038] | 4.722 / 4.626; d -0.096 [-0.397, +0.244] | 3.511 / 3.552; d +0.041 [-0.168, +0.300] |
| group (turns and year-ends) | 2018-19 | 6 | 60 |  | 0.500 / 0.500; d +0.000 [+0.000, +0.000] | 0.417 / 0.417; d +0.000 [+0.000, +0.000] | 0.033 / 0.033; d +0.000 [+0.000, +0.000] | 12.697 / 12.697; d +0.000 [+0.000, +0.000] | 12.612 / 12.612; d +0.000 [+0.000, +0.000] |
| group (turns and year-ends) | 2020 | 4 | 40 | **few events (4)** | 0.550 / 0.500; d -0.050 [-0.150, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.275 / 0.325; d +0.050 [+0.000, +0.100] | 4.485 / 5.714; d +1.228 [+0.095, +3.260] | 2.076 / 3.125; d +1.049 [+0.138, +2.712] |
| group (turns and year-ends) | 2021-23 | 12 | 120 |  | 0.742 / 0.883; d +0.142 [+0.042, +0.250] | 0.233 / 0.075; d -0.158 [-0.267, -0.058] | 0.000 / 0.025; d +0.025 [+0.000, +0.075] | 1.097 / 0.967; d -0.131 [-0.328, +0.041] | 0.003 / 0.009; d +0.006 [+0.000, +0.017] |
| group (turns and year-ends) | 2024 | 4 | 40 | **few events (4)** | 0.425 / 0.850; d +0.425 [+0.150, +0.700] | 0.575 / 0.150; d -0.425 [-0.700, -0.150] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 4.245 / 3.459; d -0.787 [-1.867, -0.075] | 2.724 / 2.299; d -0.425 [-1.355, +0.071] |
| group (turns and year-ends) | 2025-26 | 4 | 31 | **few events (4)** | 0.548 / 0.968; d +0.419 [+0.000, +0.909] | 0.452 / 0.032; d -0.419 [-0.909, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 4.233 / 3.269; d -0.964 [-1.973, -0.307] | 2.340 / 1.901; d -0.439 [-0.940, +0.048] |
| quarter-end turns | all regimes | 22 | 220 |  | 0.586 / 0.791; d +0.205 [+0.100, +0.323] | 0.336 / 0.114; d -0.223 [-0.336, -0.123] | 0.041 / 0.064; d +0.023 [+0.005, +0.045] | 3.512 / 3.387; d -0.125 [-0.535, +0.315] | 2.136 / 2.183; d +0.047 [-0.246, +0.368] |
| quarter-end turns | 2018-19 | 4 | 40 | **few events (4)** | 0.625 / 0.625; d +0.000 [+0.000, +0.000] | 0.375 / 0.375; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 6.018 / 6.018; d +0.000 [+0.000, +0.000] | 5.950 / 5.950; d +0.000 [+0.000, +0.000] |
| quarter-end turns | 2020 | 3 | 30 | **few events (3)** | 0.533 / 0.467; d -0.067 [-0.133, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.300 / 0.367; d +0.067 [+0.033, +0.100] | 5.398 / 7.035; d +1.638 [+0.252, +3.023] | 2.621 / 4.020; d +1.399 [+0.286, +2.513] |
| quarter-end turns | 2021-23 | 9 | 90 |  | 0.711 / 0.900; d +0.189 [+0.056, +0.311] | 0.256 / 0.044; d -0.211 [-0.322, -0.100] | 0.000 / 0.033; d +0.033 [+0.000, +0.100] | 1.095 / 0.950; d -0.145 [-0.392, +0.078] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | 2024 | 3 | 30 | **few events (3)** | 0.233 / 0.800; d +0.567 [+0.367, +0.767] | 0.767 / 0.200; d -0.567 [-0.767, -0.367] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 5.073 / 3.955; d -1.117 [-1.851, -0.384] | 3.092 / 2.488; d -0.604 [-1.229, +0.021] |
| quarter-end turns | 2025-26 | 3 | 30 | **few events (3)** | 0.567 / 1.000; d +0.433 [+0.100, +0.767] | 0.433 / 0.000; d -0.433 [-0.767, -0.100] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 3.974 / 2.977; d -0.997 [-1.615, -0.379] | 2.018 / 1.564; d -0.454 [-0.819, -0.090] |
| year-ends | all regimes | 8 | 71 |  | 0.648 / 0.648; d +0.000 [+0.000, +0.000] | 0.225 / 0.225; d +0.000 [+0.000, +0.000] | 0.056 / 0.056; d +0.000 [+0.000, +0.000] | 8.469 / 8.462; d -0.007 [-0.083, +0.067] | 7.771 / 7.796; d +0.025 [+0.000, +0.053] |
| year-ends | 2018-19 | 2 | 20 | **few events (2)** | 0.250 / 0.250; d +0.000 [+0.000, +0.000] | 0.500 / 0.500; d +0.000 [+0.000, +0.000] | 0.100 / 0.100; d +0.000 [+0.000, +0.000] | 26.056 / 26.056; d +0.000 [+0.000, +0.000] | 25.937 / 25.937; d +0.000 [+0.000, +0.000] |
| year-ends | 2020 | 1 | 10 | **few events (1)** | 0.600 / 0.600; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.200 / 0.200; d +0.000 [+0.000, +0.000] | 1.748 / 1.748; d +0.000 [+0.000, +0.000] | 0.441 / 0.441; d +0.000 [+0.000, +0.000] |
| year-ends | 2021-23 | 3 | 30 | **few events (3)** | 0.833 / 0.833; d +0.000 [+0.000, +0.000] | 0.167 / 0.167; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.103 / 1.017; d -0.086 [-0.172, +0.000] | 0.013 / 0.036; d +0.022 [+0.000, +0.045] |
| year-ends | 2024 | 1 | 10 | **few events (1)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.764 / 1.970; d +0.206 [+0.206, +0.206] | 1.619 / 1.730; d +0.111 [+0.111, +0.111] |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 12.001 / 12.019; d +0.018 [+0.018, +0.018] | 12.001 / 12.019; d +0.018 [+0.018, +0.018] |

**Coverage and tail misses on the group, candidate against arm.**

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 291 | 30 | 0.601 [0.498, 0.703] | 0.756 [0.667, 0.839] | +0.155 [+0.071, +0.247] | 0.089 / 0.103 | 0.309 / 0.141 | 0.045 / 0.062 | 0.127 / 0.089 |
| group, h = 1 | 58 | 29 | 0.638 [0.534, 0.741] | 0.776 [0.690, 0.862] | +0.138 [+0.052, +0.224] | 0.086 / 0.103 | 0.276 / 0.121 | 0.017 / 0.034 | 0.155 / 0.069 |
| group, h = 2 | 58 | 29 | 0.638 [0.517, 0.741] | 0.793 [0.707, 0.879] | +0.155 [+0.052, +0.259] | 0.086 / 0.103 | 0.276 / 0.103 | 0.034 / 0.034 | 0.103 / 0.069 |
| group, h = 3 | 58 | 29 | 0.621 [0.517, 0.724] | 0.759 [0.655, 0.845] | +0.138 [+0.052, +0.241] | 0.086 / 0.103 | 0.293 / 0.138 | 0.052 / 0.069 | 0.103 / 0.103 |
| group, h = 4 | 58 | 29 | 0.534 [0.414, 0.655] | 0.724 [0.603, 0.828] | +0.190 [+0.086, +0.293] | 0.103 / 0.103 | 0.362 / 0.172 | 0.069 / 0.086 | 0.121 / 0.103 |
| group, h = 5 | 59 | 30 | 0.576 [0.446, 0.700] | 0.729 [0.617, 0.833] | +0.153 [+0.051, +0.267] | 0.085 / 0.102 | 0.339 / 0.169 | 0.051 / 0.085 | 0.153 / 0.102 |
| group, quarter_end_turn only | 220 | 22 | 0.586 [0.468, 0.705] | 0.791 [0.700, 0.877] | +0.205 [+0.100, +0.323] | 0.077 / 0.095 | 0.336 / 0.114 | 0.041 / 0.064 | 0.109 / 0.068 |
| group, year_end only | 71 | 8 | 0.648 [0.419, 0.845] | 0.648 [0.419, 0.845] | +0.000 [+0.000, +0.000] | 0.127 / 0.127 | 0.225 / 0.225 | 0.056 / 0.056 | 0.183 / 0.155 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 146 | 30 | 0.493 [0.359, 0.627] | 0.644 [0.514, 0.767] | +0.151 [+0.048, +0.267] | 0.164 / 0.178 | 0.342 / 0.178 | 0.089 / 0.116 | 0.137 / 0.110 |

**The arm's 90% band covers 0.756 [0.667, 0.839] of the group's cells against 0.601 for the candidate; the gap to 90% is 14.4 percentage points.**

**Accuracy on the group (paired, same cells).** Negative favors the arm.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 4.722 | 4.626 | -0.096 [-0.397, +0.244] | 3.511 | 3.552 | +0.041 [-0.168, +0.300] |
| group, h = 1 | 4.509 | 4.338 | -0.171 [-0.466, +0.126] | 3.449 | 3.431 | -0.019 [-0.200, +0.167] |
| group, h = 2 | 4.490 | 4.440 | -0.050 [-0.327, +0.259] | 3.527 | 3.559 | +0.032 [-0.155, +0.251] |
| group, h = 3 | 4.724 | 4.652 | -0.072 [-0.376, +0.278] | 3.526 | 3.586 | +0.061 [-0.163, +0.330] |
| group, h = 4 | 4.932 | 4.836 | -0.096 [-0.440, +0.319] | 3.522 | 3.586 | +0.064 [-0.193, +0.396] |
| group, h = 5 | 4.949 | 4.859 | -0.090 [-0.410, +0.287] | 3.530 | 3.599 | +0.069 [-0.158, +0.370] |
| group, quarter_end_turn only | 3.512 | 3.387 | -0.125 [-0.535, +0.315] | 2.136 | 2.183 | +0.047 [-0.246, +0.368] |
| group, year_end only | 8.469 | 8.462 | -0.007 [-0.083, +0.067] | 7.771 | 7.796 | +0.025 [+0.000, +0.053] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 5.153 | 5.142 | -0.011 [-0.301, +0.343] | 3.964 | 4.047 | +0.082 [-0.153, +0.391] |

**The weight w the event pool reached, per lead, over the window's refits.**

Event pool: pool of quarter-end turns.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 23.5 (2 to 46) | 0.459 (0.000 to 0.697) | 0.17 | +1.149 | 2.672 |
| h=2 | 23.5 (2 to 46) | 0.459 (0.000 to 0.697) | 0.17 | +0.923 | 2.388 |
| h=3 | 23.5 (2 to 46) | 0.459 (0.000 to 0.697) | 0.17 | +1.365 | 2.465 |
| h=4 | 23.5 (2 to 46) | 0.459 (0.000 to 0.697) | 0.17 | +1.961 | 2.488 |
| h=5 | 23.5 (2 to 46) | 0.459 (0.000 to 0.697) | 0.17 | +2.132 | 2.386 |

Event pool: pool of year-ends.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 7.5 (0 to 14) | 0.151 (0.000 to 0.412) | 0.60 | -0.029 | 3.170 |
| h=2 | 7.5 (0 to 14) | 0.151 (0.000 to 0.412) | 0.60 | -0.385 | 2.681 |
| h=3 | 7.5 (0 to 14) | 0.151 (0.000 to 0.412) | 0.60 | -0.319 | 2.670 |
| h=4 | 7.5 (0 to 14) | 0.151 (0.000 to 0.412) | 0.60 | -0.158 | 2.441 |
| h=5 | 7.5 (0 to 14) | 0.151 (0.000 to 0.412) | 0.60 | -0.213 | 2.021 |

**The declared kill (that of #1548, applied to this arm on its own).** Coverage on the group: +0.155 [+0.071, +0.247] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is above zero, so the arm improves beyond its interval. Grid CRPS on the group: -0.096 [-0.397, +0.244] bp (arm minus candidate). The arm's is not above the candidate's, so the arm does not lose. **Against the declared kill: not killed.**

## The 2026 development days (targets 2026-01-02 to 2026-09-03; they decide nothing)

#### (s3c-ann-net-x), arm (i), expanding pool

Group cells 21, of which the arm changes 21; cells outside the group 804, every one identical to the candidate (the walk fails otherwise). The group holds 3 turn events. **That is few, so every interval is wide.**

**By regime of the event (read first).** Cells of fewer than 5 events are flagged.

| set | regime of the event | events | cells | flag | 90% coverage: cand. / arm; d [interval] | above q95 (5%): cand. / arm; d [interval] | below q01 (1%): cand. / arm; d [interval] | grid CRPS: cand. / arm; d [interval] (negative favours the arm) | upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm) |
|---|---|---|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 3 | 21 | **few events (3)** | 0.952 / 0.952; d +0.000 [+0.000, +0.000] | 0.048 / 0.048; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.011 / 1.357; d +0.346 [+0.052, +0.475] | 0.759 / 1.056; d +0.296 [+0.023, +0.406] |
| group (turns and year-ends) | 2018-19 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2020 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2021-23 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2024 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2025-26 | 3 | 21 | **few events (3)** | 0.952 / 0.952; d +0.000 [+0.000, +0.000] | 0.048 / 0.048; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.011 / 1.357; d +0.346 [+0.052, +0.475] | 0.759 / 1.056; d +0.296 [+0.023, +0.406] |
| quarter-end turns | all regimes | 2 | 20 | **few events (2)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.909 / 1.328; d +0.419 [+0.284, +0.554] | 0.646 / 1.020; d +0.374 [+0.278, +0.470] |
| quarter-end turns | 2018-19 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2020 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2021-23 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2024 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2025-26 | 2 | 20 | **few events (2)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.909 / 1.328; d +0.419 [+0.284, +0.554] | 0.646 / 1.020; d +0.374 [+0.278, +0.470] |
| year-ends | all regimes | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 3.057 / 1.951; d -1.106 [-1.106, -1.106] | 3.024 / 1.767; d -1.256 [-1.256, -1.256] |
| year-ends | 2018-19 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2020 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2021-23 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2024 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 3.057 / 1.951; d -1.106 [-1.106, -1.106] | 3.024 / 1.767; d -1.256 [-1.256, -1.256] |

**Coverage and tail misses on the group, candidate against arm.**

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 21 | 3 | 0.952 [0.833, 1.000] | 0.952 [0.833, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.048 / 0.048 | 0.000 / 0.000 | 0.048 / 0.048 |
| group, h = 1 | 5 | 3 | 0.800 [0.500, 1.000] | 0.800 [0.500, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.200 / 0.200 | 0.000 / 0.000 | 0.200 / 0.200 |
| group, h = 2 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 3 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 4 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 5 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, quarter_end_turn only | 20 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, year_end only | 1 | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 1.000 / 1.000 | 0.000 / 0.000 | 1.000 / 1.000 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 10 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |

**The arm's 90% band covers 0.952 [0.833, 1.000] of the group's cells against 0.952 for the candidate; the gap to 90% is -5.2 percentage points (negative: the band covers more than 90%).**

**Accuracy on the group (paired, same cells).** Negative favors the arm.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 1.011 | 1.357 | +0.346 [+0.052, +0.475] | 0.759 | 1.056 | +0.296 [+0.023, +0.406] |
| group, h = 1 | 1.435 | 1.307 | -0.128 [-0.653, +0.222] | 1.002 | 0.957 | -0.045 [-0.622, +0.340] |
| group, h = 2 | 0.889 | 1.206 | +0.317 [+0.151, +0.484] | 0.569 | 0.890 | +0.322 [+0.211, +0.432] |
| group, h = 3 | 0.856 | 1.354 | +0.498 [+0.446, +0.549] | 0.698 | 1.097 | +0.400 [+0.380, +0.419] |
| group, h = 4 | 0.875 | 1.464 | +0.588 [+0.513, +0.664] | 0.715 | 1.179 | +0.464 [+0.416, +0.513] |
| group, h = 5 | 0.894 | 1.469 | +0.575 [+0.510, +0.640] | 0.752 | 1.179 | +0.427 [+0.373, +0.482] |
| group, quarter_end_turn only | 0.909 | 1.328 | +0.419 [+0.284, +0.554] | 0.646 | 1.020 | +0.374 [+0.278, +0.470] |
| group, year_end only | 3.057 | 1.951 | -1.106 [-1.106, -1.106] | 3.024 | 1.767 | -1.256 [-1.256, -1.256] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 0.845 | 1.328 | +0.482 [+0.461, +0.504] | 0.835 | 1.245 | +0.410 [+0.406, +0.414] |

**The weight w the event pool reached, per lead, over the window's refits.**

Event pool: one pool of quarter-end turns and year-ends.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 33.7 (2 to 66) | 0.543 (0.000 to 0.767) | 0.12 | +1.086 | 3.004 |
| h=2 | 33.7 (2 to 66) | 0.543 (0.000 to 0.767) | 0.12 | +0.991 | 2.656 |
| h=3 | 33.7 (2 to 66) | 0.543 (0.000 to 0.767) | 0.12 | +1.380 | 2.639 |
| h=4 | 33.7 (2 to 66) | 0.543 (0.000 to 0.767) | 0.12 | +1.849 | 2.579 |
| h=5 | 33.7 (2 to 66) | 0.543 (0.000 to 0.767) | 0.12 | +1.728 | 2.422 |

**The declared kill (that of #1548, applied to this arm on its own).** Coverage on the group: +0.000 [+0.000, +0.000] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is not above zero, so the arm does not improve beyond its interval. Grid CRPS on the group: +0.346 [+0.052, +0.475] bp over 3 events (arm minus candidate): an interval that does not span zero. **The declared kill is read on the development window only; it is not called on these days.**

#### (s3c-ann-net-xs), arm (ii), separate pools

Group cells 21, of which the arm changes 21; cells outside the group 804, every one identical to the candidate (the walk fails otherwise). The group holds 3 turn events. **That is few, so every interval is wide.**

**By regime of the event (read first).** Cells of fewer than 5 events are flagged.

| set | regime of the event | events | cells | flag | 90% coverage: cand. / arm; d [interval] | above q95 (5%): cand. / arm; d [interval] | below q01 (1%): cand. / arm; d [interval] | grid CRPS: cand. / arm; d [interval] (negative favours the arm) | upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm) |
|---|---|---|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 3 | 21 | **few events (3)** | 0.952 / 0.952; d +0.000 [+0.000, +0.000] | 0.048 / 0.048; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.011 / 1.452; d +0.441 [+0.264, +0.614] | 0.759 / 1.179; d +0.420 [+0.273, +0.551] |
| group (turns and year-ends) | 2018-19 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2020 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2021-23 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2024 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| group (turns and year-ends) | 2025-26 | 3 | 21 | **few events (3)** | 0.952 / 0.952; d +0.000 [+0.000, +0.000] | 0.048 / 0.048; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.011 / 1.452; d +0.441 [+0.264, +0.614] | 0.759 / 1.179; d +0.420 [+0.273, +0.551] |
| quarter-end turns | all regimes | 2 | 20 | **few events (2)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.909 / 1.360; d +0.451 [+0.270, +0.633] | 0.646 / 1.079; d +0.433 [+0.295, +0.570] |
| quarter-end turns | 2018-19 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2020 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2021-23 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2024 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| quarter-end turns | 2025-26 | 2 | 20 | **few events (2)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.909 / 1.360; d +0.451 [+0.270, +0.633] | 0.646 / 1.079; d +0.433 [+0.295, +0.570] |
| year-ends | all regimes | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 3.057 / 3.291; d +0.234 [+0.234, +0.234] | 3.024 / 3.184; d +0.160 [+0.160, +0.160] |
| year-ends | 2018-19 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2020 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2021-23 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2024 | 0 | 0 | none | n/a | n/a | n/a | n/a | n/a |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 3.057 / 3.291; d +0.234 [+0.234, +0.234] | 3.024 / 3.184; d +0.160 [+0.160, +0.160] |

**Coverage and tail misses on the group, candidate against arm.**

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 21 | 3 | 0.952 [0.833, 1.000] | 0.952 [0.833, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.048 / 0.048 | 0.000 / 0.000 | 0.048 / 0.048 |
| group, h = 1 | 5 | 3 | 0.800 [0.500, 1.000] | 0.800 [0.500, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.200 / 0.200 | 0.000 / 0.000 | 0.200 / 0.200 |
| group, h = 2 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 3 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 4 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 5 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, quarter_end_turn only | 20 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, year_end only | 1 | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 1.000 / 1.000 | 0.000 / 0.000 | 1.000 / 1.000 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 10 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |

**The arm's 90% band covers 0.952 [0.833, 1.000] of the group's cells against 0.952 for the candidate; the gap to 90% is -5.2 percentage points (negative: the band covers more than 90%).**

**Accuracy on the group (paired, same cells).** Negative favors the arm.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 1.011 | 1.452 | +0.441 [+0.264, +0.614] | 0.759 | 1.179 | +0.420 [+0.273, +0.551] |
| group, h = 1 | 1.435 | 1.575 | +0.140 [-0.165, +0.445] | 1.002 | 1.287 | +0.285 [+0.042, +0.527] |
| group, h = 2 | 0.889 | 1.244 | +0.355 [+0.133, +0.576] | 0.569 | 0.968 | +0.399 [+0.240, +0.559] |
| group, h = 3 | 0.856 | 1.396 | +0.541 [+0.422, +0.660] | 0.698 | 1.171 | +0.473 [+0.395, +0.552] |
| group, h = 4 | 0.875 | 1.493 | +0.618 [+0.525, +0.710] | 0.715 | 1.223 | +0.508 [+0.449, +0.568] |
| group, h = 5 | 0.894 | 1.522 | +0.628 [+0.537, +0.719] | 0.752 | 1.218 | +0.467 [+0.381, +0.553] |
| group, quarter_end_turn only | 0.909 | 1.360 | +0.451 [+0.270, +0.633] | 0.646 | 1.079 | +0.433 [+0.295, +0.570] |
| group, year_end only | 3.057 | 3.291 | +0.234 [+0.234, +0.234] | 3.024 | 3.184 | +0.160 [+0.160, +0.160] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 0.845 | 1.404 | +0.559 [+0.546, +0.572] | 0.835 | 1.327 | +0.492 [+0.453, +0.531] |

**The weight w the event pool reached, per lead, over the window's refits.**

Event pool: pool of quarter-end turns.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 25.5 (2 to 50) | 0.479 (0.000 to 0.714) | 0.15 | +1.218 | 2.691 |
| h=2 | 25.5 (2 to 50) | 0.479 (0.000 to 0.714) | 0.15 | +0.957 | 2.431 |
| h=3 | 25.5 (2 to 50) | 0.479 (0.000 to 0.714) | 0.15 | +1.357 | 2.505 |
| h=4 | 25.5 (2 to 50) | 0.479 (0.000 to 0.714) | 0.15 | +1.894 | 2.522 |
| h=5 | 25.5 (2 to 50) | 0.479 (0.000 to 0.714) | 0.15 | +2.009 | 2.438 |

Event pool: pool of year-ends.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 8.2 (0 to 16) | 0.175 (0.000 to 0.444) | 0.55 | +0.033 | 3.156 |
| h=2 | 8.2 (0 to 16) | 0.175 (0.000 to 0.444) | 0.55 | -0.308 | 2.730 |
| h=3 | 8.2 (0 to 16) | 0.175 (0.000 to 0.444) | 0.55 | -0.302 | 2.709 |
| h=4 | 8.2 (0 to 16) | 0.175 (0.000 to 0.444) | 0.55 | -0.069 | 2.484 |
| h=5 | 8.2 (0 to 16) | 0.175 (0.000 to 0.444) | 0.55 | -0.085 | 2.054 |

**The declared kill (that of #1548, applied to this arm on its own).** Coverage on the group: +0.000 [+0.000, +0.000] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is not above zero, so the arm does not improve beyond its interval. Grid CRPS on the group: +0.441 [+0.264, +0.614] bp over 3 events (arm minus candidate): an interval that does not span zero. **The declared kill is read on the development window only; it is not called on these days.**

## Against the benchmarks

### Development window

#### (s3c-ann-net-x), arm (i), expanding pool: pooled, against B1, B1' and B2

Studentized stationary bootstrap. each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +30.0% [+24.0%, +42.5%]; d +0.688 [+0.424, +1.597]: **gain** | +38.6% [+31.0%, +51.9%]; d +0.530 [+0.268, +1.611]: **gain** |
| (s3c-ann-net) against B1' | +13.5% [+8.4%, +17.9%]; d +0.249 [+0.161, +0.353]: **gain** | +15.5% [+6.3%, +23.6%]; d +0.154 [+0.079, +0.264]: **gain** |
| (s3c-ann-net) against B2 | +36.3% [+25.7%, +45.4%]; d +0.913 [+0.668, +1.229]: **gain** | +25.4% [+10.8%, +38.1%]; d +0.288 [+0.166, +0.458]: **gain** |
| (s3c-ann-net-ev) against B1 | n/a | n/a |
| (s3c-ann-net-ev) against B1' | n/a | n/a |
| (s3c-ann-net-ev) against B2 | n/a | n/a |

##### By regime of the decision day: (s3c-ann-net-x), arm (i), expanding pool against B1

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +37.1% [+27.9%, +57.7%]; d +2.147 [+0.973, +9.083]: **gain** | +39.3% [+29.1%, +58.9%]; d +2.072 [+0.886, +8.923]: **gain** | n/a |
| 2020 | 251 | +6.6% [-29.9%, +19.8%]; d +0.109 [-0.308, +0.355]: **undecided** | +15.9% [-6.8%, +40.2%]; d +0.117 [-0.053, +0.659]: **undecided** | n/a |
| 2021-23 | 748 | +9.5% [+4.1%, +14.1%]; d +0.066 [+0.033, +0.100]: **gain** | +12.1% [-57.4%, +38.9%]; d +0.001 [-0.002, +0.003]: **undecided** | n/a |
| 2024 | 250 | +35.2% [+27.1%, +44.9%]; d +0.568 [+0.294, +1.270]: **gain** | +44.6% [+21.2%, +98.8%]; d +0.125 [+0.008, +1.098]: **gain** | n/a |
| 2025-26 | 249 | +34.0% [+26.2%, +42.1%]; d +1.143 [+0.740, +1.700]: **gain** | +42.5% [+31.0%, +53.6%]; d +0.681 [+0.241, +1.661]: **gain** | n/a |

##### By regime of the decision day: (s3c-ann-net-x), arm (i), expanding pool against B1'

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +10.0% [+0.8%, +17.6%]; d +0.404 [+0.141, +0.728]: **gain** | +10.6% [-0.6%, +19.6%]; d +0.382 [+0.113, +0.727]: **gain (skill interval: undecided)** | n/a |
| 2020 | 251 | +4.7% [-28.9%, +21.0%]; d +0.075 [-0.298, +0.395]: **undecided** | +18.5% [-5.7%, +47.6%]; d +0.142 [-0.070, +0.994]: **undecided** | n/a |
| 2021-23 | 748 | +4.9% [-0.6%, +10.0%]; d +0.033 [-0.003, +0.069]: **undecided** | -11.6% [-61.2%, +12.0%]; d -0.001 [-0.006, +0.001]: **undecided** | n/a |
| 2024 | 250 | +24.1% [+16.2%, +33.2%]; d +0.331 [+0.145, +0.763]: **gain** | +25.2% [+19.5%, +34.0%]; d +0.052 [+0.005, +0.840]: **gain** | n/a |
| 2025-26 | 249 | +26.0% [+17.9%, +34.0%]; d +0.779 [+0.503, +1.118]: **gain** | +29.6% [+17.8%, +44.5%]; d +0.388 [+0.117, +1.031]: **gain** | n/a |

##### By regime of the decision day: (s3c-ann-net-x), arm (i), expanding pool against B2

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +17.6% [+3.2%, +30.4%]; d +0.778 [+0.317, +1.294]: **gain** | +14.9% [+1.3%, +26.9%]; d +0.559 [+0.186, +0.990]: **gain** | n/a |
| 2020 | 251 | +47.1% [+23.4%, +68.8%]; d +1.372 [+0.597, +2.840]: **gain** | +52.9% [-6.3%, +81.0%]; d +0.699 [+0.343, +1.146]: **gain (skill interval: undecided)** | n/a |
| 2021-23 | 748 | +57.1% [+44.8%, +68.4%]; d +0.840 [+0.549, +1.209]: **gain** | -166.3% [-527.8%, -79.9%]; d -0.005 [-0.042, -0.000]: **loss** | n/a |
| 2024 | 250 | +22.7% [+10.7%, +32.3%]; d +0.308 [+0.112, +0.555]: **gain** | skill undefined; d +0.031 [-0.001, +0.527]: **undecided (skill interval: skill undefined)** | n/a |
| 2025-26 | 249 | +40.6% [+19.4%, +57.8%]; d +1.511 [+0.425, +3.469]: **gain** | +39.9% [+29.5%, +55.7%]; d +0.612 [+0.121, +2.463]: **gain** | n/a |

##### By pressure-day type of the target day: (s3c-ann-net-x), arm (i), expanding pool against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +34.1% [+24.2%, +59.6%]; d +0.666 [+0.389, +1.678]: **gain** | +49.9% [+36.4%, +76.7%]; d +0.537 [+0.259, +1.682]: **gain** | n/a |
| quarter_end_turn | 44 | +22.5% [-86.6%, +43.5%]; d +0.981 [-1.042, +2.624]: **undecided** | +19.0% [-47.2%, +33.8%]; d +0.508 [-0.283, +1.662]: **undecided** | n/a |
| tax_date | 89 | +7.5% [-5.3%, +18.3%]; d +0.414 [-0.016, +1.129]: **undecided** | +6.4% [-8.8%, +17.1%]; d +0.298 [+0.006, +1.408]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +35.2% [+21.1%, +50.8%]; d +0.916 [+0.220, +2.129]: **gain** | +31.5% [+12.5%, +52.6%]; d +0.458 [-0.005, +2.058]: **undecided (skill interval: gain)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-x), arm (i), expanding pool against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +12.3% [+6.8%, +17.1%]; d +0.180 [+0.094, +0.278]: **gain** | +15.8% [+3.2%, +25.8%]; d +0.101 [+0.022, +0.203]: **gain** | n/a |
| quarter_end_turn | 44 | +20.1% [-91.6%, +42.2%]; d +0.853 [-1.196, +2.432]: **undecided** | +17.7% [-49.7%, +32.7%]; d +0.464 [-0.298, +1.530]: **undecided** | n/a |
| tax_date | 89 | +5.9% [-0.2%, +11.6%]; d +0.320 [-0.032, +1.043]: **undecided** | +6.1% [-4.4%, +12.8%]; d +0.281 [+0.008, +1.407]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +29.5% [+18.6%, +40.1%]; d +0.705 [+0.190, +1.485]: **gain** | +31.8% [+9.4%, +44.0%]; d +0.466 [+0.082, +1.393]: **gain** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-x), arm (i), expanding pool against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +36.2% [+26.5%, +44.9%]; d +0.731 [+0.485, +1.028]: **gain** | +21.9% [+5.6%, +34.5%]; d +0.151 [+0.041, +0.284]: **gain** | n/a |
| quarter_end_turn | 44 | +32.6% [+8.8%, +47.6%]; d +1.634 [+0.792, +2.367]: **gain** | skill undefined; d +0.641 [+0.108, +2.401]: **gain (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +34.3% [-69.4%, +59.4%]; d +2.655 [+1.475, +4.923]: **gain (skill interval: undecided)** | skill undefined; d +1.295 [+0.091, +4.495]: **gain (skill interval: skill undefined)** | n/a |
| turn | 120 | +49.2% [+29.5%, +68.8%]; d +1.634 [+0.809, +3.999]: **gain** | +50.4% [-4.9%, +86.5%]; d +1.013 [+0.234, +4.061]: **gain (skill interval: undecided)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type: (s3c-ann-net-x), arm (i), expanding pool against the candidate (identical outside the group)

The arm scored against the candidate, so a positive d favors the arm.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | identical | identical | n/a |
| quarter_end_turn | 44 | +3.8% [-54.5%, +24.6%]; d +0.132 [-1.001, +0.786]: **undecided** | skill undefined; d -0.029 [-0.694, +0.337]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | identical | identical | n/a |
| turn | 120 | identical | identical | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### (s3c-ann-net-xs), arm (ii), separate pools: pooled, against B1, B1' and B2

Studentized stationary bootstrap. each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +30.0% [+24.0%, +42.5%]; d +0.688 [+0.424, +1.597]: **gain** | +38.6% [+31.0%, +51.9%]; d +0.530 [+0.268, +1.611]: **gain** |
| (s3c-ann-net) against B1' | +13.5% [+8.4%, +17.9%]; d +0.249 [+0.161, +0.353]: **gain** | +15.5% [+6.3%, +23.6%]; d +0.154 [+0.079, +0.264]: **gain** |
| (s3c-ann-net) against B2 | +36.3% [+25.7%, +45.4%]; d +0.913 [+0.668, +1.229]: **gain** | +25.4% [+10.8%, +38.1%]; d +0.288 [+0.166, +0.458]: **gain** |
| (s3c-ann-net-ev) against B1 | n/a | n/a |
| (s3c-ann-net-ev) against B1' | n/a | n/a |
| (s3c-ann-net-ev) against B2 | n/a | n/a |

##### By regime of the decision day: (s3c-ann-net-xs), arm (ii), separate pools against B1

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +37.1% [+28.0%, +57.4%]; d +2.149 [+0.977, +9.098]: **gain** | +39.3% [+29.2%, +58.7%]; d +2.074 [+0.891, +8.932]: **gain** | n/a |
| 2020 | 251 | +7.2% [-30.6%, +20.3%]; d +0.119 [-0.307, +0.366]: **undecided** | +17.4% [-4.4%, +39.9%]; d +0.129 [-0.041, +0.705]: **undecided** | n/a |
| 2021-23 | 748 | +9.7% [+4.2%, +14.3%]; d +0.068 [+0.034, +0.101]: **gain** | +22.3% [-32.8%, +47.3%]; d +0.002 [-0.001, +0.004]: **undecided** | n/a |
| 2024 | 250 | +35.1% [+27.1%, +44.7%]; d +0.567 [+0.294, +1.265]: **gain** | +44.6% [+23.6%, +90.0%]; d +0.125 [+0.010, +1.080]: **gain** | n/a |
| 2025-26 | 249 | +34.3% [+26.5%, +42.3%]; d +1.151 [+0.744, +1.703]: **gain** | +42.8% [+31.1%, +53.8%]; d +0.686 [+0.244, +1.656]: **gain** | n/a |

##### By regime of the decision day: (s3c-ann-net-xs), arm (ii), separate pools against B1'

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +10.0% [+0.5%, +17.9%]; d +0.406 [+0.145, +0.728]: **gain** | +10.7% [-0.9%, +19.9%]; d +0.384 [+0.118, +0.729]: **gain (skill interval: undecided)** | n/a |
| 2020 | 251 | +5.3% [-28.5%, +21.2%]; d +0.086 [-0.285, +0.401]: **undecided** | +20.0% [-2.7%, +47.6%]; d +0.153 [-0.056, +1.077]: **undecided** | n/a |
| 2021-23 | 748 | +5.2% [-0.4%, +10.3%]; d +0.034 [-0.001, +0.070]: **undecided** | +1.4% [-38.2%, +24.0%]; d +0.000 [-0.003, +0.001]: **undecided** | n/a |
| 2024 | 250 | +24.0% [+16.1%, +33.4%]; d +0.330 [+0.144, +0.764]: **gain** | +25.2% [+18.8%, +35.9%]; d +0.052 [+0.004, +0.841]: **gain** | n/a |
| 2025-26 | 249 | +26.3% [+18.3%, +34.1%]; d +0.786 [+0.511, +1.124]: **gain** | +30.0% [+17.8%, +44.5%]; d +0.393 [+0.121, +1.033]: **gain** | n/a |

##### By regime of the decision day: (s3c-ann-net-xs), arm (ii), separate pools against B2

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +17.6% [+3.0%, +30.8%]; d +0.779 [+0.318, +1.305]: **gain** | +14.9% [+1.0%, +27.3%]; d +0.561 [+0.185, +0.995]: **gain** | n/a |
| 2020 | 251 | +47.5% [+23.5%, +68.9%]; d +1.382 [+0.609, +2.828]: **gain** | +53.7% [-7.0%, +81.8%]; d +0.710 [+0.352, +1.157]: **gain (skill interval: undecided)** | n/a |
| 2021-23 | 748 | +57.2% [+44.9%, +68.5%]; d +0.841 [+0.551, +1.211]: **gain** | -135.4% [-551.3%, -40.7%]; d -0.004 [-0.034, -0.000]: **loss** | n/a |
| 2024 | 250 | +22.6% [+10.5%, +32.2%]; d +0.306 [+0.110, +0.553]: **gain** | skill undefined; d +0.031 [-0.000, +0.643]: **undecided (skill interval: skill undefined)** | n/a |
| 2025-26 | 249 | +40.8% [+19.8%, +57.8%]; d +1.518 [+0.434, +3.475]: **gain** | +40.2% [+30.2%, +55.6%]; d +0.617 [+0.125, +2.444]: **gain** | n/a |

##### By pressure-day type of the target day: (s3c-ann-net-xs), arm (ii), separate pools against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +34.1% [+24.2%, +59.6%]; d +0.666 [+0.389, +1.678]: **gain** | +49.9% [+36.4%, +76.7%]; d +0.537 [+0.259, +1.682]: **gain** | n/a |
| quarter_end_turn | 44 | +22.3% [-103.5%, +43.8%]; d +0.973 [-1.036, +2.603]: **undecided** | +18.4% [-38.2%, +31.2%]; d +0.491 [-0.246, +1.529]: **undecided** | n/a |
| tax_date | 89 | +7.5% [-5.3%, +18.3%]; d +0.414 [-0.016, +1.129]: **undecided** | +6.4% [-8.8%, +17.1%]; d +0.298 [+0.006, +1.408]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +35.2% [+21.1%, +50.8%]; d +0.916 [+0.220, +2.129]: **gain** | +31.5% [+12.5%, +52.6%]; d +0.458 [-0.005, +2.058]: **undecided (skill interval: gain)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-xs), arm (ii), separate pools against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +12.3% [+6.8%, +17.1%]; d +0.180 [+0.094, +0.278]: **gain** | +15.8% [+3.2%, +25.8%]; d +0.101 [+0.022, +0.203]: **gain** | n/a |
| quarter_end_turn | 44 | +20.0% [-109.7%, +42.6%]; d +0.845 [-1.196, +2.427]: **undecided** | +17.0% [-41.5%, +29.9%]; d +0.447 [-0.262, +1.395]: **undecided** | n/a |
| tax_date | 89 | +5.9% [-0.2%, +11.6%]; d +0.320 [-0.032, +1.043]: **undecided** | +6.1% [-4.4%, +12.8%]; d +0.281 [+0.008, +1.407]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +29.5% [+18.6%, +40.1%]; d +0.705 [+0.190, +1.485]: **gain** | +31.8% [+9.4%, +44.0%]; d +0.466 [+0.082, +1.393]: **gain** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-xs), arm (ii), separate pools against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +36.2% [+26.5%, +44.9%]; d +0.731 [+0.485, +1.028]: **gain** | +21.9% [+5.6%, +34.5%]; d +0.151 [+0.041, +0.284]: **gain** | n/a |
| quarter_end_turn | 44 | +32.4% [+8.5%, +48.4%]; d +1.627 [+0.727, +2.309]: **gain** | skill undefined; d +0.624 [+0.105, +2.341]: **gain (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +34.3% [-69.4%, +59.4%]; d +2.655 [+1.475, +4.923]: **gain (skill interval: undecided)** | skill undefined; d +1.295 [+0.091, +4.495]: **gain (skill interval: skill undefined)** | n/a |
| turn | 120 | +49.2% [+29.5%, +68.8%]; d +1.634 [+0.809, +3.999]: **gain** | +50.4% [-4.9%, +86.5%]; d +1.013 [+0.234, +4.061]: **gain (skill interval: undecided)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type: (s3c-ann-net-xs), arm (ii), separate pools against the candidate (identical outside the group)

The arm scored against the candidate, so a positive d favors the arm.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | identical | identical | n/a |
| quarter_end_turn | 44 | +3.5% [-56.8%, +28.9%]; d +0.125 [-0.967, +0.840]: **undecided** | skill undefined; d -0.047 [-0.708, +0.330]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | identical | identical | n/a |
| turn | 120 | identical | identical | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### The 2026 development days

#### (s3c-ann-net-x), arm (i), expanding pool: pooled, against B1, B1' and B2

Studentized stationary bootstrap. each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +22.7% [-0.2%, +35.8%]; d +0.491 [+0.133, +0.814]: **gain (skill interval: undecided)** | +37.7% [+23.8%, +51.8%]; d +0.311 [+0.134, +0.681]: **gain** |
| (s3c-ann-net) against B1' | +10.7% [-12.9%, +22.7%]; d +0.200 [-0.143, +0.428]: **undecided** | +17.2% [+4.4%, +27.9%]; d +0.107 [+0.016, +0.224]: **gain** |
| (s3c-ann-net) against B2 | +22.6% [+3.9%, +41.4%]; d +0.486 [+0.120, +0.940]: **gain** | +19.1% [-6.4%, +36.9%]; d +0.122 [-0.041, +0.240]: **undecided** |
| (s3c-ann-net-ev) against B1 | n/a | n/a |
| (s3c-ann-net-ev) against B1' | n/a | n/a |
| (s3c-ann-net-ev) against B2 | n/a | n/a |

##### By pressure-day type of the target day: (s3c-ann-net-x), arm (i), expanding pool against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +20.1% [-7.3%, +38.3%]; d +0.432 [+0.023, +0.871]: **gain (skill interval: undecided)** | +41.5% [+23.9%, +61.9%]; d +0.342 [+0.120, +1.048]: **gain** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-x), arm (i), expanding pool against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +5.8% [-23.1%, +19.3%]; d +0.105 [-0.326, +0.352]: **undecided** | +11.0% [-7.6%, +25.2%]; d +0.059 [-0.042, +0.191]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-x), arm (i), expanding pool against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +19.6% [-0.6%, +38.8%]; d +0.419 [+0.015, +0.866]: **gain (skill interval: undecided)** | -1.7% [-44.2%, +22.4%]; d -0.008 [-0.213, +0.111]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type: (s3c-ann-net-x), arm (i), expanding pool against the candidate (identical outside the group)

The arm scored against the candidate, so a positive d favors the arm.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | identical | identical | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### (s3c-ann-net-xs), arm (ii), separate pools: pooled, against B1, B1' and B2

Studentized stationary bootstrap. each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +22.7% [-0.2%, +35.8%]; d +0.491 [+0.133, +0.814]: **gain (skill interval: undecided)** | +37.7% [+23.8%, +51.8%]; d +0.311 [+0.134, +0.681]: **gain** |
| (s3c-ann-net) against B1' | +10.7% [-12.9%, +22.7%]; d +0.200 [-0.143, +0.428]: **undecided** | +17.2% [+4.4%, +27.9%]; d +0.107 [+0.016, +0.224]: **gain** |
| (s3c-ann-net) against B2 | +22.6% [+3.9%, +41.4%]; d +0.486 [+0.120, +0.940]: **gain** | +19.1% [-6.4%, +36.9%]; d +0.122 [-0.041, +0.240]: **undecided** |
| (s3c-ann-net-ev) against B1 | n/a | n/a |
| (s3c-ann-net-ev) against B1' | n/a | n/a |
| (s3c-ann-net-ev) against B2 | n/a | n/a |

##### By pressure-day type of the target day: (s3c-ann-net-xs), arm (ii), separate pools against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +20.1% [-7.3%, +38.3%]; d +0.432 [+0.023, +0.871]: **gain (skill interval: undecided)** | +41.5% [+23.9%, +61.9%]; d +0.342 [+0.120, +1.048]: **gain** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-xs), arm (ii), separate pools against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +5.8% [-23.1%, +19.3%]; d +0.105 [-0.326, +0.352]: **undecided** | +11.0% [-7.6%, +25.2%]; d +0.059 [-0.042, +0.191]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-xs), arm (ii), separate pools against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +19.6% [-0.6%, +38.8%]; d +0.419 [+0.015, +0.866]: **gain (skill interval: undecided)** | -1.7% [-44.2%, +22.4%]; d -0.008 [-0.213, +0.111]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type: (s3c-ann-net-xs), arm (ii), separate pools against the candidate (identical outside the group)

The arm scored against the candidate, so a positive d favors the arm.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | identical | identical | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

## What it means, and its limits

The page shows what a longer quarter-end history does to the candidate's coverage, tail misses and CRPS on days that were already seen. It is development data: no verdict, no adoption, and no registration follows from it. Older turns come from other regimes, so the table by regime of the event is the one to read first; a gain that sits in one regime, or in a few events, is not a gain that will recur. The year-ends are too few to decide alone. The two arms are not tested against each other, and the figures of #1531 and #1548 are not re-run here. What to do with the quarter-end family next is hers.

## Record

Declaration: `metadata/qe_expanding_pool_1622.json` (committed before any score). Panel digest: `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`. Decision instant 18:00 New York. Candidate reproduced to 1e-9: 2026 (1.668524 here, 1.668524 in the 1314 record), development (1.601162 here, 1.601162 in the 1314 record).
