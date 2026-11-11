# A shrunk quarter-end scale beside the frozen candidate

Terms such as arm, cell, kill rule, grid CRPS and B1 are defined in the [glossary](glossary.md). Issue numbers and files are in the Record at the end.

## The question

**Does a shrunk residual multiplier on quarter-end target days alone repair the candidate's quarter-end bands?** The candidate's 90% band covers too few outcomes around quarter-ends. This study tests one repair: rescale the band on those days only, and leave every other forecast as it is.

## The answer

Not on the development data: the arm's 90% band covers 0.646 [0.557, 0.733] of the group's cells against 0.601 for the candidate; the gap to 90% is 25.4 percentage points. The arm improved on the candidate's coverage beyond its interval and did not score worse on grid CRPS, so under the rule declared before the run it is not killed.

## Data

The published panel, with every forecast made at the 18:00 decision. Two sets of days are scored and kept apart: the development window, where the kill rule is read, and the 2026 development days, which are shown separately and decide nothing. Each section below opens with its count of days, cells and turn events.

## Method

**The change.** The group is every target day whose type is `quarter_end_turn` or `year_end`: the last business day of each calendar quarter and the first after it. On those days the candidate's residual pool is rescaled about its median by `m = 1 + w (m_raw - 1)`, `w = n / (n + k)`, `k = 20`. `m_raw` is the root-mean-square ratio of the group's training residuals to all of them (per refit and lead, 1 below 10 pairs, clamped to [0.5, 4]), and `n` is the number of the group's training pairs, so a group with few pairs is pulled toward a multiplier of 1. On every other target day every quantile equals the candidate's, bit for bit, and the walk fails if it does not. The center, the calendar terms, the scale and the fit are the candidate's, on direct pairs; the SRF cap is applied after.

**The kill rule.** Declared before any score: the arm is killed if its 90% coverage on the group does not improve on the candidate's beyond its interval (the lower end of the 90% event-cluster interval of the paired difference, arm minus candidate, is not above zero), or if the arm's mean grid CRPS on the group is above the candidate's. Pooled figures cannot pass or fail it alone, since everything outside the group is identical.

**The intervals.** The h = 1-5 forecasts aimed at one turn, and the turn's two days, are one cluster. Intervals on the group are 90% percentile intervals of a cluster bootstrap over turn events (2,000 resamples, seed 1531). The development window holds 30 events: roughly 30 to 44 is small, so every interval is wide. Against the benchmarks the interval is the studentized stationary bootstrap (mean block 10 business days, 10,000 draws, seed 1531, two-sided 90% interval), and the reading is taken from the bound on mean d. Two caveats carry over: which interval method applies to day types has not been ruled on, and the HAC standard error is understated about 2x after 2020. In the paired tables against a benchmark, a positive mean d favors the model named first.

**Design not revised.** The Mechanism section of the quarter-end diagnosis was read before this run. It gives a reason to doubt a single multiplier (the failure is one of shape as well as width) but none to change the declared group or shrinkage rule, so the arm was run as ruled; the doubt is Question 2 below.

## Result on the development window (targets up to 2025-12-31)

Scored decision days: 1,855 (2018-07-19 to 2025-12-23); 89 refits. Group cells: 291, of which the arm changes 251; cells outside the group: 8,984, every one identical to the candidate (the walk fails otherwise). The group holds 30 turn events and 291 cells; **roughly 30 to 44 events is small.**

### Coverage and tail misses on the group, candidate against arm

Read the first row, and in it the column "arm minus candidate": that difference and its interval are what the kill rule reads. A 90% band that works covers 90% of the cells, so the two coverage columns show how far each model is from that. The four tail columns give the share of cells whose outcome fell outside a quantile, candidate first and arm second, with the share a calibrated model would show in brackets in the column head. The rows by lead and by day type hold fewer cells, and their intervals are wider.

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 291 | 30 | 0.601 [0.495, 0.708] | 0.646 [0.557, 0.733] | +0.045 [+0.004, +0.087] | 0.089 / 0.082 | 0.309 / 0.271 | 0.045 / 0.024 | 0.127 / 0.107 |
| group, h = 1 | 58 | 29 | 0.638 [0.534, 0.741] | 0.672 [0.569, 0.776] | +0.034 [-0.017, +0.086] | 0.086 / 0.069 | 0.276 / 0.259 | 0.017 / 0.017 | 0.155 / 0.121 |
| group, h = 2 | 58 | 29 | 0.638 [0.517, 0.741] | 0.655 [0.534, 0.776] | +0.017 [+0.000, +0.052] | 0.086 / 0.069 | 0.276 / 0.276 | 0.034 / 0.000 | 0.103 / 0.103 |
| group, h = 3 | 58 | 29 | 0.621 [0.517, 0.724] | 0.638 [0.534, 0.741] | +0.017 [-0.052, +0.086] | 0.086 / 0.086 | 0.293 / 0.276 | 0.052 / 0.034 | 0.103 / 0.103 |
| group, h = 4 | 58 | 29 | 0.534 [0.414, 0.655] | 0.638 [0.517, 0.741] | +0.103 [+0.034, +0.190] | 0.103 / 0.086 | 0.362 / 0.276 | 0.069 / 0.034 | 0.121 / 0.103 |
| group, h = 5 | 59 | 30 | 0.576 [0.441, 0.712] | 0.627 [0.500, 0.746] | +0.051 [-0.017, +0.121] | 0.085 / 0.102 | 0.339 / 0.271 | 0.051 / 0.034 | 0.153 / 0.102 |
| group, quarter_end_turn only | 220 | 22 | 0.586 [0.464, 0.709] | 0.636 [0.541, 0.732] | +0.050 [-0.005, +0.109] | 0.077 / 0.077 | 0.336 / 0.286 | 0.041 / 0.032 | 0.109 / 0.091 |
| group, year_end only | 71 | 8 | 0.648 [0.435, 0.845] | 0.676 [0.452, 0.871] | +0.028 [+0.000, +0.075] | 0.127 / 0.099 | 0.225 / 0.225 | 0.056 / 0.000 | 0.183 / 0.155 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 146 | 30 | 0.493 [0.359, 0.627] | 0.555 [0.432, 0.673] | +0.062 [+0.007, +0.130] | 0.164 / 0.158 | 0.342 / 0.288 | 0.089 / 0.048 | 0.137 / 0.130 |

**The arm's 90% band covers 0.646 [0.557, 0.733] of the group's cells against 0.601 for the candidate; the gap to 90% is 25.4 percentage points.**

### Accuracy of the distribution on the group (paired, same cells)

Both scores are in bp and lower is better, so a negative difference favors the arm. The first row holds the grid CRPS difference the kill rule reads.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 4.722 | 4.616 | -0.105 [-0.184, -0.037] | 3.511 | 3.451 | -0.060 [-0.113, -0.014] |
| group, h = 1 | 4.509 | 4.434 | -0.075 [-0.148, -0.008] | 3.449 | 3.408 | -0.041 [-0.092, +0.009] |
| group, h = 2 | 4.490 | 4.413 | -0.077 [-0.138, -0.025] | 3.527 | 3.483 | -0.044 [-0.084, -0.009] |
| group, h = 3 | 4.724 | 4.622 | -0.102 [-0.178, -0.032] | 3.526 | 3.466 | -0.059 [-0.116, -0.009] |
| group, h = 4 | 4.932 | 4.792 | -0.140 [-0.232, -0.060] | 3.522 | 3.439 | -0.083 [-0.150, -0.027] |
| group, h = 5 | 4.949 | 4.817 | -0.132 [-0.224, -0.055] | 3.530 | 3.458 | -0.073 [-0.139, -0.020] |
| group, quarter_end_turn only | 3.512 | 3.370 | -0.142 [-0.244, -0.053] | 2.136 | 2.051 | -0.085 [-0.156, -0.024] |
| group, year_end only | 8.469 | 8.480 | +0.010 [-0.040, +0.073] | 7.771 | 7.788 | +0.017 [-0.016, +0.054] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 5.153 | 5.038 | -0.115 [-0.194, -0.047] | 3.964 | 3.881 | -0.083 [-0.145, -0.032] |

### The declared kill

Coverage on the group: +0.045 [+0.004, +0.087] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is above zero, so the arm improves beyond its interval. Grid CRPS on the group: -0.105 [-0.184, -0.037] bp (arm minus candidate). The arm's is not above the candidate's, so the arm does not lose. **Against the declared kill: not killed.**

### The multipliers (shrunk), over the window's refits

The table shows how large the adjustment was at each lead. `m_raw` is the ratio before shrinkage, `w` the weight it receives and `m` the multiplier applied; an `m` above 1 widens the band. The fallback is the `m_raw` of 1 used below 10 pairs, and a bound is 0.5 or 4.

| lead | group pairs n: mean (least to greatest) | m_raw: mean (least to greatest) | w: mean | m: mean (least to greatest) | share of refits at the fallback | share at a bound |
|---|---|---|---|---|---|---|
| h=1 | 14.1 (2 to 16) | 1.539 (0.500 to 3.107) | 0.403 | 1.233 (0.778 to 1.777) | 0.13 | 0.09 |
| h=2 | 14.1 (2 to 16) | 1.328 (0.500 to 2.972) | 0.403 | 1.138 (0.778 to 1.657) | 0.13 | 0.07 |
| h=3 | 14.1 (2 to 16) | 1.445 (0.530 to 3.044) | 0.403 | 1.190 (0.791 to 1.785) | 0.13 | 0.00 |
| h=4 | 14.1 (2 to 16) | 1.539 (0.612 to 2.956) | 0.403 | 1.233 (0.834 to 1.870) | 0.13 | 0.00 |
| h=5 | 14.1 (2 to 16) | 1.516 (0.736 to 2.873) | 0.403 | 1.224 (0.887 to 1.832) | 0.13 | 0.00 |

### Pooled, against B1, B1' and B2 (studentized stationary bootstrap)

This table places both models in the scoring protocol's frame, on all decision days. Each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero. A note in brackets says where the interval of the skill reads differently. Everything outside the group is identical, so the arm and the candidate differ against a benchmark only through the group, and their rows are close: the comparison that separates them is the group's, above.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +30.0% [+24.1%, +42.8%]; d +0.688 [+0.428, +1.631]: **gain** | +38.6% [+31.2%, +52.2%]; d +0.530 [+0.275, +1.644]: **gain** |
| (s3c-ann-net) against B1' | +13.5% [+8.4%, +17.9%]; d +0.249 [+0.162, +0.354]: **gain** | +15.5% [+6.3%, +23.6%]; d +0.154 [+0.081, +0.265]: **gain** |
| (s3c-ann-net) against B2 | +36.3% [+25.6%, +45.0%]; d +0.913 [+0.669, +1.226]: **gain** | +25.4% [+10.2%, +38.0%]; d +0.288 [+0.165, +0.460]: **gain** |
| (s3c-ann-net-qe) against B1 | +30.2% [+24.3%, +43.0%]; d +0.691 [+0.432, +1.638]: **gain** | +38.7% [+31.3%, +52.3%]; d +0.532 [+0.277, +1.646]: **gain** |
| (s3c-ann-net-qe) against B1' | +13.7% [+8.6%, +18.1%]; d +0.253 [+0.165, +0.358]: **gain** | +15.6% [+6.4%, +23.8%]; d +0.156 [+0.083, +0.268]: **gain** |
| (s3c-ann-net-qe) against B2 | +36.5% [+25.6%, +45.2%]; d +0.917 [+0.672, +1.229]: **gain** | +25.6% [+10.3%, +38.1%]; d +0.290 [+0.167, +0.462]: **gain** |

### The same comparison, split

A pooled development figure is not a result on its own, so the comparison is repeated by regime and by pressure-day type of the target day. These are reference tables. For each benchmark the candidate's table comes first and the arm's second; the two differ only through the group's cells, so look at the rows that hold quarter-end and year-end days. The cells read as in the pooled table.

#### By regime: (s3c-ann-net) against B1

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +37.1% [+27.9%, +57.5%]; d +2.149 [+0.948, +8.905]: **gain** | +39.3% [+29.4%, +58.4%]; d +2.074 [+0.855, +8.800]: **gain** | n/a |
| 2020 | 251 | +9.6% [-17.8%, +21.1%]; d +0.158 [-0.146, +0.401]: **undecided** | +21.9% [+5.8%, +45.5%]; d +0.162 [-0.006, +0.922]: **undecided (skill interval: gain)** | n/a |
| 2021-23 | 748 | +9.2% [+3.6%, +13.8%]; d +0.064 [+0.030, +0.096]: **gain** | +23.0% [-33.9%, +47.9%]; d +0.002 [-0.001, +0.004]: **undecided** | n/a |
| 2024 | 250 | +33.4% [+26.7%, +42.1%]; d +0.539 [+0.283, +1.174]: **gain** | +39.6% [+21.2%, +79.0%]; d +0.111 [+0.011, +1.169]: **gain** | n/a |
| 2025-26 | 249 | +33.6% [+25.6%, +42.0%]; d +1.128 [+0.722, +1.697]: **gain** | +42.2% [+31.2%, +53.3%]; d +0.676 [+0.240, +1.629]: **gain** | n/a |

#### By regime: (s3c-ann-net-qe) against B1

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +37.1% [+27.9%, +57.5%]; d +2.151 [+0.949, +8.898]: **gain** | +39.3% [+29.4%, +58.4%]; d +2.076 [+0.856, +8.805]: **gain** | n/a |
| 2020 | 251 | +10.0% [-16.2%, +21.2%]; d +0.164 [-0.126, +0.408]: **undecided** | +22.1% [+6.3%, +46.1%]; d +0.164 [-0.004, +0.937]: **undecided (skill interval: gain)** | n/a |
| 2021-23 | 748 | +9.2% [+3.6%, +13.8%]; d +0.064 [+0.031, +0.096]: **gain** | +22.3% [-34.7%, +47.3%]; d +0.002 [-0.001, +0.004]: **undecided** | n/a |
| 2024 | 250 | +33.9% [+26.8%, +42.9%]; d +0.547 [+0.285, +1.196]: **gain** | +41.5% [+22.7%, +84.5%]; d +0.116 [+0.011, +0.961]: **gain** | n/a |
| 2025-26 | 249 | +33.8% [+25.8%, +42.1%]; d +1.136 [+0.728, +1.705]: **gain** | +42.5% [+31.2%, +53.5%]; d +0.680 [+0.244, +1.631]: **gain** | n/a |

#### By regime: (s3c-ann-net) against B1'

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +10.0% [+0.4%, +17.6%]; d +0.406 [+0.142, +0.720]: **gain** | +10.7% [-1.0%, +19.6%]; d +0.384 [+0.115, +0.722]: **gain (skill interval: undecided)** | n/a |
| 2020 | 251 | +7.7% [-17.6%, +22.8%]; d +0.125 [-0.170, +0.475]: **undecided** | +24.3% [+7.4%, +52.2%]; d +0.186 [-0.024, +1.352]: **undecided (skill interval: gain)** | n/a |
| 2021-23 | 748 | +4.6% [-1.1%, +9.9%]; d +0.030 [-0.005, +0.067]: **undecided** | +2.2% [-38.1%, +25.0%]; d +0.000 [-0.003, +0.002]: **undecided** | n/a |
| 2024 | 250 | +22.0% [+13.8%, +33.5%]; d +0.302 [+0.128, +0.735]: **gain** | +18.4% [+0.4%, +56.6%]; d +0.038 [-0.002, +0.551]: **undecided (skill interval: gain)** | n/a |
| 2025-26 | 249 | +25.5% [+17.7%, +33.3%]; d +0.764 [+0.490, +1.102]: **gain** | +29.3% [+17.2%, +43.8%]; d +0.383 [+0.113, +1.001]: **gain** | n/a |

#### By regime: (s3c-ann-net-qe) against B1'

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +10.1% [+0.4%, +17.6%]; d +0.407 [+0.144, +0.722]: **gain** | +10.7% [-1.0%, +19.7%]; d +0.386 [+0.118, +0.724]: **gain (skill interval: undecided)** | n/a |
| 2020 | 251 | +8.1% [-16.2%, +23.1%]; d +0.130 [-0.156, +0.488]: **undecided** | +24.6% [+7.9%, +52.8%]; d +0.188 [-0.022, +1.368]: **undecided (skill interval: gain)** | n/a |
| 2021-23 | 748 | +4.6% [-1.1%, +9.9%]; d +0.030 [-0.005, +0.068]: **undecided** | +1.4% [-38.4%, +24.0%]; d +0.000 [-0.003, +0.001]: **undecided** | n/a |
| 2024 | 250 | +22.5% [+14.8%, +33.1%]; d +0.310 [+0.134, +0.740]: **gain** | +21.0% [+9.7%, +42.6%]; d +0.044 [+0.000, +0.647]: **gain** | n/a |
| 2025-26 | 249 | +25.8% [+17.8%, +33.6%]; d +0.772 [+0.495, +1.110]: **gain** | +29.6% [+17.5%, +44.0%]; d +0.387 [+0.117, +1.002]: **gain** | n/a |

#### By regime: (s3c-ann-net) against B2

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +17.6% [+2.8%, +30.8%]; d +0.779 [+0.321, +1.317]: **gain** | +14.9% [+0.9%, +27.4%]; d +0.561 [+0.191, +1.001]: **gain** | n/a |
| 2020 | 251 | +48.8% [+25.7%, +68.8%]; d +1.421 [+0.635, +2.931]: **gain** | +56.2% [-5.5%, +81.4%]; d +0.743 [+0.378, +1.173]: **gain (skill interval: undecided)** | n/a |
| 2021-23 | 748 | +56.9% [+44.3%, +68.1%]; d +0.837 [+0.540, +1.216]: **gain** | -133.3% [-539.9%, -38.0%]; d -0.004 [-0.035, +0.000]: **undecided (skill interval: loss)** | n/a |
| 2024 | 250 | +20.6% [+8.6%, +30.4%]; d +0.279 [+0.092, +0.517]: **gain** | skill undefined; d +0.016 [-0.006, +0.311]: **undecided (skill interval: skill undefined)** | n/a |
| 2025-26 | 249 | +40.2% [+18.8%, +57.8%]; d +1.496 [+0.414, +3.428]: **gain** | +39.6% [+28.9%, +54.8%]; d +0.607 [+0.116, +2.342]: **gain** | n/a |

#### By regime: (s3c-ann-net-qe) against B2

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +17.7% [+2.8%, +30.9%]; d +0.781 [+0.323, +1.318]: **gain** | +14.9% [+0.9%, +27.4%]; d +0.563 [+0.193, +1.004]: **gain** | n/a |
| 2020 | 251 | +49.0% [+26.0%, +68.9%]; d +1.427 [+0.636, +2.932]: **gain** | +56.4% [-5.6%, +81.4%]; d +0.745 [+0.377, +1.176]: **gain (skill interval: undecided)** | n/a |
| 2021-23 | 748 | +56.9% [+44.3%, +68.1%]; d +0.838 [+0.540, +1.216]: **gain** | -135.3% [-538.4%, -40.6%]; d -0.004 [-0.035, +0.000]: **undecided (skill interval: loss)** | n/a |
| 2024 | 250 | +21.2% [+9.2%, +30.8%]; d +0.287 [+0.098, +0.527]: **gain** | skill undefined; d +0.022 [-0.003, +0.422]: **undecided (skill interval: skill undefined)** | n/a |
| 2025-26 | 249 | +40.4% [+19.2%, +57.9%]; d +1.504 [+0.427, +3.445]: **gain** | +39.8% [+29.4%, +55.1%]; d +0.611 [+0.122, +2.362]: **gain** | n/a |

#### By pressure-day type of the target day: (s3c-ann-net) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +34.1% [+24.0%, +60.0%]; d +0.666 [+0.382, +1.699]: **gain** | +49.9% [+35.9%, +76.9%]; d +0.537 [+0.252, +1.715]: **gain** | n/a |
| quarter_end_turn | 44 | +19.5% [-18.7%, +30.8%]; d +0.849 [-0.265, +2.076]: **undecided** | skill undefined; d +0.537 [-0.008, +2.554]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +7.5% [-4.8%, +18.7%]; d +0.414 [-0.004, +1.144]: **undecided** | +6.4% [-8.6%, +17.1%]; d +0.298 [+0.009, +1.417]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +35.2% [+21.3%, +51.0%]; d +0.916 [+0.222, +2.174]: **gain** | +31.5% [+12.2%, +52.2%]; d +0.458 [-0.010, +2.085]: **undecided (skill interval: gain)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net-qe) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +34.1% [+24.0%, +60.0%]; d +0.666 [+0.382, +1.699]: **gain** | +49.9% [+35.9%, +76.9%]; d +0.537 [+0.252, +1.715]: **gain** | n/a |
| quarter_end_turn | 44 | +22.7% [-16.9%, +35.0%]; d +0.991 [-0.205, +2.440]: **undecided** | skill undefined; d +0.622 [+0.019, +2.415]: **gain (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +7.5% [-4.8%, +18.7%]; d +0.414 [-0.004, +1.144]: **undecided** | +6.4% [-8.6%, +17.1%]; d +0.298 [+0.009, +1.417]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +35.2% [+21.3%, +51.0%]; d +0.916 [+0.222, +2.174]: **gain** | +31.5% [+12.2%, +52.2%]; d +0.458 [-0.010, +2.085]: **undecided (skill interval: gain)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +12.3% [+6.8%, +17.1%]; d +0.180 [+0.093, +0.277]: **gain** | +15.8% [+3.2%, +26.2%]; d +0.101 [+0.020, +0.206]: **gain** | n/a |
| quarter_end_turn | 44 | +17.0% [-23.6%, +28.9%]; d +0.721 [-0.378, +1.829]: **undecided** | skill undefined; d +0.493 [-0.010, +2.328]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +5.9% [-0.2%, +11.7%]; d +0.320 [-0.022, +1.053]: **undecided** | +6.1% [-4.2%, +12.9%]; d +0.281 [+0.015, +1.444]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +29.5% [+18.9%, +40.0%]; d +0.705 [+0.180, +1.490]: **gain** | +31.8% [+9.4%, +43.9%]; d +0.466 [+0.073, +1.395]: **gain** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net-qe) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +12.3% [+6.8%, +17.1%]; d +0.180 [+0.093, +0.277]: **gain** | +15.8% [+3.2%, +26.2%]; d +0.101 [+0.020, +0.206]: **gain** | n/a |
| quarter_end_turn | 44 | +20.4% [-21.2%, +33.3%]; d +0.863 [-0.302, +2.195]: **undecided** | skill undefined; d +0.578 [+0.018, +2.209]: **gain (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +5.9% [-0.2%, +11.7%]; d +0.320 [-0.022, +1.053]: **undecided** | +6.1% [-4.2%, +12.9%]; d +0.281 [+0.015, +1.444]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +29.5% [+18.9%, +40.0%]; d +0.705 [+0.180, +1.490]: **gain** | +31.8% [+9.4%, +43.9%]; d +0.466 [+0.073, +1.395]: **gain** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +36.2% [+26.8%, +44.9%]; d +0.731 [+0.493, +1.024]: **gain** | +21.9% [+6.2%, +34.6%]; d +0.151 [+0.044, +0.281]: **gain** | n/a |
| quarter_end_turn | 44 | +30.0% [-11.4%, +49.0%]; d +1.502 [-0.027, +2.869]: **undecided** | skill undefined; d +0.670 [-0.098, +4.629]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +34.3% [-69.3%, +59.3%]; d +2.655 [+1.495, +4.902]: **gain (skill interval: undecided)** | skill undefined; d +1.295 [+0.117, +4.524]: **gain (skill interval: skill undefined)** | n/a |
| turn | 120 | +49.2% [+29.9%, +69.1%]; d +1.634 [+0.807, +3.930]: **gain** | +50.4% [-3.3%, +85.8%]; d +1.013 [+0.226, +3.799]: **gain (skill interval: undecided)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net-qe) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +36.2% [+26.8%, +44.9%]; d +0.731 [+0.493, +1.024]: **gain** | +21.9% [+6.2%, +34.6%]; d +0.151 [+0.044, +0.281]: **gain** | n/a |
| quarter_end_turn | 44 | +32.8% [-4.3%, +49.9%]; d +1.645 [+0.343, +2.985]: **gain (skill interval: undecided)** | skill undefined; d +0.755 [-0.006, +4.572]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +34.3% [-69.3%, +59.3%]; d +2.655 [+1.495, +4.902]: **gain (skill interval: undecided)** | skill undefined; d +1.295 [+0.117, +4.524]: **gain (skill interval: skill undefined)** | n/a |
| turn | 120 | +49.2% [+29.9%, +69.1%]; d +1.634 [+0.807, +3.930]: **gain** | +50.4% [-3.3%, +85.8%]; d +1.013 [+0.226, +3.799]: **gain (skill interval: undecided)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### By pressure-day type: the arm against the candidate (identical outside the group)

Here the candidate takes the benchmark's place, so a positive d favors the arm. A row reads "identical" where the arm changes nothing.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | identical | identical | n/a |
| quarter_end_turn | 44 | +4.1% [+1.5%, +9.6%]; d +0.142 [+0.018, +0.361]: **gain** | skill undefined; d +0.085 [+0.007, +0.225] (11 of 10000 resamples dropped): **gain (skill interval: skill undefined)** | n/a |
| tax_date | 89 | identical | identical | n/a |
| turn | 120 | identical | identical | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### Against B3 (the published record's five levels, grid CRPS on those five)

B3 is the published model. It forecasts five quantile levels, so grid CRPS (bp) is computed on those five for all three models. The comparison is reported and carries no decision rule.

| decision days | days | B3 | (s3c-ann-net) | (s3c-ann-net-qe) | (s3c-ann-net) against B3 | (s3c-ann-net-qe) against B3 |
|---|---|---|---|---|---|---|
| 2018-19 | 362 | 4.078 | 3.635 | 3.634 | +10.9% [+0.6%, +18.3%]; d +0.443 [+0.211, +0.676]: **gain** | +10.9% [+0.6%, +18.3%]; d +0.444 [+0.212, +0.676]: **gain** |
| 2020 | 251 | 1.437 | 1.490 | 1.484 | -3.7% [-26.4%, +7.1%]; d -0.053 [-0.384, +0.099]: **undecided** | -3.3% [-24.9%, +7.3%]; d -0.047 [-0.359, +0.102]: **undecided** |
| 2021-23 | 748 | 0.741 | 0.646 | 0.645 | +12.8% [+3.3%, +22.0%]; d +0.095 [+0.025, +0.190]: **gain** | +12.9% [+3.4%, +22.1%]; d +0.096 [+0.026, +0.191]: **gain** |
| 2024 | 250 | 1.356 | 1.117 | 1.110 | +17.6% [+11.3%, +22.7%]; d +0.239 [+0.121, +0.474]: **gain** | +18.1% [+11.2%, +24.1%]; d +0.246 [+0.122, +0.496]: **gain** |
| 2025-26 | 244 | 2.581 | 2.112 | 2.100 | +18.2% [+10.2%, +25.3%]; d +0.469 [+0.243, +0.723]: **gain** | +18.6% [+10.5%, +25.7%]; d +0.481 [+0.252, +0.734]: **gain** |
| all decision days | 1855 | 1.811 | 1.600 | 1.596 | +11.7% [+6.6%, +16.0%]; d +0.212 [+0.137, +0.292]: **gain** | +11.9% [+6.7%, +16.3%]; d +0.215 [+0.140, +0.296]: **gain** |

Groups of fewer than 20 days, listed and not tested: pressure_day_type/year_end (15).

## The 2026 development days (targets 2026-01-02 to 2026-09-03)

These days are kept apart from the development window. The kill rule is not read on them and they decide nothing.

Scored decision days: 165 (2025-12-31 to 2026-08-27); 97 refits. Group cells: 21, of which the arm changes 21; cells outside the group: 804, every one identical to the candidate (the walk fails otherwise). The group holds 3 turn events and 21 cells; **roughly 30 to 44 events is small.**

### Coverage and tail misses on the group, candidate against arm

Read the first row, and in it the column "arm minus candidate": that difference and its interval are what the kill rule reads. A 90% band that works covers 90% of the cells, so the two coverage columns show how far each model is from that. The four tail columns give the share of cells whose outcome fell outside a quantile, candidate first and arm second, with the share a calibrated model would show in brackets in the column head. The rows by lead and by day type hold fewer cells, and their intervals are wider.

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

### Accuracy of the distribution on the group (paired, same cells)

Both scores are in bp and lower is better, so a negative difference favors the arm. The first row holds the grid CRPS difference the kill rule reads.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 1.011 | 1.162 | +0.151 [+0.101, +0.171] | 0.759 | 0.849 | +0.090 [+0.034, +0.112] |
| group, h = 1 | 1.435 | 1.507 | +0.072 [-0.080, +0.173] | 1.002 | 1.029 | +0.027 [-0.146, +0.143] |
| group, h = 2 | 0.889 | 1.045 | +0.156 [+0.121, +0.191] | 0.569 | 0.682 | +0.114 [+0.101, +0.126] |
| group, h = 3 | 0.856 | 1.049 | +0.193 [+0.154, +0.232] | 0.698 | 0.811 | +0.114 [+0.081, +0.146] |
| group, h = 4 | 0.875 | 1.054 | +0.179 [+0.148, +0.210] | 0.715 | 0.827 | +0.112 [+0.086, +0.138] |
| group, h = 5 | 0.894 | 1.067 | +0.173 [+0.144, +0.202] | 0.752 | 0.851 | +0.099 [+0.088, +0.110] |
| group, quarter_end_turn only | 0.909 | 1.077 | +0.168 [+0.160, +0.176] | 0.646 | 0.756 | +0.110 [+0.102, +0.117] |
| group, year_end only | 3.057 | 2.864 | -0.193 [-0.193, -0.193] | 3.024 | 2.716 | -0.308 [-0.308, -0.308] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 0.845 | 1.018 | +0.172 [+0.082, +0.262] | 0.835 | 0.974 | +0.139 [+0.069, +0.209] |

### The declared kill (shown apart; the kill is read on the development window only, and these days decide nothing)

Coverage on the group: +0.000 [+0.000, +0.000] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is not above zero, so the arm does not improve beyond its interval. Grid CRPS on the group: +0.151 [+0.101, +0.171] bp (arm minus candidate). The arm's is above the candidate's, so the arm loses. **Against the declared kill: killed.**

### The multipliers (shrunk), over the window's refits

The table shows how large the adjustment was at each lead. `m_raw` is the ratio before shrinkage, `w` the weight it receives and `m` the multiplier applied; an `m` above 1 widens the band. The fallback is the `m_raw` of 1 used below 10 pairs, and a bound is 0.5 or 4.

| lead | group pairs n: mean (least to greatest) | m_raw: mean (least to greatest) | w: mean | m: mean (least to greatest) | share of refits at the fallback | share at a bound |
|---|---|---|---|---|---|---|
| h=1 | 14.2 (2 to 16) | 1.627 (0.500 to 3.107) | 0.406 | 1.273 (0.778 to 1.781) | 0.12 | 0.08 |
| h=2 | 14.2 (2 to 16) | 1.413 (0.500 to 2.972) | 0.406 | 1.177 (0.778 to 1.664) | 0.12 | 0.06 |
| h=3 | 14.2 (2 to 16) | 1.528 (0.530 to 3.044) | 0.406 | 1.228 (0.791 to 1.785) | 0.12 | 0.00 |
| h=4 | 14.2 (2 to 16) | 1.610 (0.612 to 2.956) | 0.406 | 1.265 (0.834 to 1.870) | 0.12 | 0.00 |
| h=5 | 14.2 (2 to 16) | 1.585 (0.736 to 2.873) | 0.406 | 1.255 (0.887 to 1.832) | 0.12 | 0.00 |

### Pooled, against B1, B1' and B2 (studentized stationary bootstrap)

This table places both models in the scoring protocol's frame, on all decision days. Each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero. A note in brackets says where the interval of the skill reads differently. Everything outside the group is identical, so the arm and the candidate differ against a benchmark only through the group, and their rows are close: the comparison that separates them is the group's, above.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +22.7% [-0.1%, +35.9%]; d +0.491 [+0.140, +0.815]: **gain (skill interval: undecided)** | +37.7% [+23.7%, +51.6%]; d +0.311 [+0.134, +0.681]: **gain** |
| (s3c-ann-net) against B1' | +10.7% [-13.3%, +22.7%]; d +0.200 [-0.149, +0.432]: **undecided** | +17.2% [+4.6%, +28.1%]; d +0.107 [+0.016, +0.224]: **gain** |
| (s3c-ann-net) against B2 | +22.6% [+3.8%, +42.1%]; d +0.486 [+0.110, +0.954]: **gain** | +19.1% [-6.6%, +36.4%]; d +0.122 [-0.044, +0.238]: **undecided** |
| (s3c-ann-net-qe) against B1 | +22.6% [-0.1%, +35.7%]; d +0.487 [+0.138, +0.811]: **gain (skill interval: undecided)** | +37.4% [+23.4%, +51.5%]; d +0.309 [+0.132, +0.683]: **gain** |
| (s3c-ann-net-qe) against B1' | +10.5% [-13.2%, +22.4%]; d +0.197 [-0.150, +0.427]: **undecided** | +16.9% [+4.4%, +27.7%]; d +0.105 [+0.014, +0.223]: **gain** |
| (s3c-ann-net-qe) against B2 | +22.4% [+3.6%, +42.1%]; d +0.482 [+0.108, +0.955]: **gain** | +18.8% [-6.8%, +35.9%]; d +0.119 [-0.044, +0.235]: **undecided** |

### The same comparison, split

A pooled development figure is not a result on its own, so the comparison is repeated by regime and by pressure-day type of the target day. These are reference tables. For each benchmark the candidate's table comes first and the arm's second; the two differ only through the group's cells, so look at the rows that hold quarter-end and year-end days. The cells read as in the pooled table.

#### By pressure-day type of the target day: (s3c-ann-net) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +20.1% [-7.0%, +38.2%]; d +0.432 [+0.017, +0.874]: **gain (skill interval: undecided)** | +41.5% [+24.7%, +62.2%]; d +0.342 [+0.118, +1.031]: **gain** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net-qe) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +20.1% [-7.0%, +38.2%]; d +0.432 [+0.017, +0.874]: **gain (skill interval: undecided)** | +41.5% [+24.7%, +62.2%]; d +0.342 [+0.118, +1.031]: **gain** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +5.8% [-23.4%, +19.3%]; d +0.105 [-0.326, +0.349]: **undecided** | +11.0% [-8.0%, +25.2%]; d +0.059 [-0.044, +0.191]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net-qe) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +5.8% [-23.4%, +19.3%]; d +0.105 [-0.326, +0.349]: **undecided** | +11.0% [-8.0%, +25.2%]; d +0.059 [-0.044, +0.191]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +19.6% [-0.3%, +38.4%]; d +0.419 [+0.021, +0.864]: **gain (skill interval: undecided)** | -1.7% [-43.2%, +22.1%]; d -0.008 [-0.211, +0.110]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type of the target day: (s3c-ann-net-qe) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +19.6% [-0.3%, +38.4%]; d +0.419 [+0.021, +0.864]: **gain (skill interval: undecided)** | -1.7% [-43.2%, +22.1%]; d -0.008 [-0.211, +0.110]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### By pressure-day type: the arm against the candidate (identical outside the group)

Here the candidate takes the benchmark's place, so a positive d favors the arm. A row reads "identical" where the arm changes nothing.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | identical | identical | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### Against B3 (the published record's five levels, grid CRPS on those five)

B3 is the published model. It forecasts five quantile levels, so grid CRPS (bp) is computed on those five for all three models. The comparison is reported and carries no decision rule.

The published record holds no decision day of this window with all five leads, so B3 is not scored here.


Groups of fewer than 20 days, listed and not tested: pressure_day_type/quarter_end_turn (4), pressure_day_type/tax_date (6), pressure_day_type/turn (12), pressure_day_type/year_end (1).

## What it means, and its limits

The page shows what one width multiplier on the quarter-end group does to the candidate's coverage, tail misses and CRPS on development days. It does not show a verdict, an adoption, or what a distribution with its own shape on those days would do. "Not killed" means the arm did not fail the declared rule; the candidate stays frozen and nothing is adopted, registered or published. The 2026 days are shown apart and decide nothing.

## Question for Eleonora (marked; the default changes no claim)

**Question 1. What is the shrinkage constant k?** The rule is `w = n / (n + k)`, `n` the group's training pairs at a refit and lead (a turn gives two pairs per lead). It is written in the declaration before any score and was not tuned on scores: this page uses k = 20, ten turns' worth of pairs, where the raw ratio is trusted by half. It is a judgment call, so it is yours.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **k = 20** (default). Half weight at ten turns, three fifths at thirty. This page.
2. **k = 10.** Less shrinkage: half weight at five turns. A fresh run with a fresh declaration.
3. **k = 40.** More shrinkage: half weight at twenty turns, about two fifths at thirty. A fresh run with a fresh declaration.

**Question 2. Does the arm go on?** The Mechanism section of the quarter-end diagnosis reads the failure as a shape problem with a location shift, and says no single multiplier fits every level. The design was run as ruled and not revised. Whether a width-only arm closes anything, or the work moves to B or to an event-conditional distribution model, is yours; adopting the arm is not in scope and the 2 November freeze holds.

**Options:** 1. **Read this page, then decide B or the event-conditional model** (default; no claim changes). 2. **Re-run with k = 10 or 40** (option 2 or 3 above). 3. **Stop the family here.**

## Record

- Study: #1531. Hypothesis and step: H5 (primary goal), step 3, arm A of her ruling of 9 November 2026.
- Status: **development data, not a verdict** (scoring protocol v1, #640). (s3c-ann-net) stays frozen; nothing is adopted, registered or published and no claim changes.
- Generated by `scripts/qe_shrunk_scale_1531.py page` from `docs/research/qe-shrunk-scale-1531/result.json`, not edited by hand; declared in `metadata/qe_shrunk_scale_1531.json` before any score.
- Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`.
- Reproduction: the candidate's pooled mean grid CRPS equals #1314's 18:00 record to 1e-9 (development 1.601162, 2026 1.668524), or the script refused to write this record.
- Where the parts come from: the target-day labels, #959; the raw multiplier, #1402; the quarter-end diagnosis, #1533; the `quarter_end` group and its 49.3% figure, #1363; the development window, #1145 and #1241; the 2026 development days, #1229 and #1252.
- Open or inherited rulings: the day-type interval method, where #1228 has not ruled; the reading from the mean-d bound, her ruling on #1009; the understated HAC standard error, #958.
