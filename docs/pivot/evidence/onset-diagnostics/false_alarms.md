# Where the false alarms fall (#429)

Declaration `metadata/onset_diagnostics.json` (commit `1ec7f160e91d`), the judge's flags (declaration sha256 `00d54925784b…`), +5 bp, scored days 2018-07-06 to 2025-12-31 (1869 days every horizon scores, 26 onsets). A false alarm is a flag on a day that is not a pressure day; the day is the flagged (target) day.

Table A. False alarms by horizon: the count, and per onset (Table 1 of the re-judge reports the worst horizon).

| row | h=1 | h=2 | h=3 | h=4 | h=5 | all horizons | onsets flagged |
|---|---|---|---|---|---|---|---|
| two_part_gbm | 6 (0.23) | 30 (1.15) | 41 (1.58) | 35 (1.35) | 64 (2.46) | 176 (6.77) | 15 of 26 |
| ngboost_laplace | 44 (1.69) | 45 (1.73) | 37 (1.42) | 66 (2.54) | 41 (1.58) | 233 (8.96) | 15 of 26 |
| hierarchical_logistic | 80 (3.08) | 47 (1.81) | 82 (3.15) | 78 (3.00) | 95 (3.65) | 382 (14.69) | 15 of 26 |
| settlement_quantile_timing | 76 (2.92) | 70 (2.69) | 91 (3.50) | 92 (3.54) | 95 (3.65) | 424 (16.31) | 15 of 26 |
| scarcity_logistic_interactions | 83 (3.19) | 52 (2.00) | 82 (3.15) | 78 (3.00) | 84 (3.23) | 379 (14.58) | 14 of 26 |

Table B. False alarms (all five horizons together) by the flagged day's realised spread (whole basis points). The first row is the non-pressure days a flag could fall on, summed over the five horizons; a cell is the count and the share of that row's false alarms.

| row | +4 to +5 bp | +1 to +3 bp | 0 bp or below | total |
|---|---|---|---|---|
| non-pressure days (flag-days available) | 315 (4%) | 585 (7%) | 7755 (90%) | 8655 |
| two_part_gbm | 48 (27%) | 50 (28%) | 78 (44%) | 176 |
| ngboost_laplace | 75 (32%) | 89 (38%) | 69 (30%) | 233 |
| hierarchical_logistic | 147 (38%) | 158 (41%) | 77 (20%) | 382 |
| settlement_quantile_timing | 129 (30%) | 141 (33%) | 154 (36%) | 424 |
| scarcity_logistic_interactions | 150 (40%) | 159 (42%) | 70 (18%) | 379 |

Table C. False alarms (all five horizons together) by the flagged day's distance to the nearest pressure day (panel days). The first row is the non-pressure days a flag could fall on, summed over the five horizons; a cell is the count and the share of that row's false alarms.

| row | 1 day | 2 to 5 days | 6 to 20 days | 21 days or more | total |
|---|---|---|---|---|---|
| non-pressure days (flag-days available) | 420 (5%) | 855 (10%) | 825 (10%) | 6555 (76%) | 8655 |
| two_part_gbm | 62 (35%) | 97 (55%) | 13 (7%) | 4 (2%) | 176 |
| ngboost_laplace | 81 (35%) | 133 (57%) | 18 (8%) | 1 (0%) | 233 |
| hierarchical_logistic | 147 (38%) | 216 (57%) | 19 (5%) | 0 (0%) | 382 |
| settlement_quantile_timing | 141 (33%) | 203 (48%) | 19 (4%) | 61 (14%) | 424 |
| scarcity_logistic_interactions | 148 (39%) | 208 (55%) | 23 (6%) | 0 (0%) | 379 |

Table D. False alarms (all five horizons together) by the flagged day's type. The first row is the non-pressure days a flag could fall on, summed over the five horizons; a cell is the count and the share of that row's false alarms.

| row | month_end | ordinary | quarter_end | tax_date | total |
|---|---|---|---|---|---|
| non-pressure days (flag-days available) | 665 (8%) | 7500 (87%) | 110 (1%) | 380 (4%) | 8655 |
| two_part_gbm | 15 (9%) | 153 (87%) | 0 (0%) | 8 (5%) | 176 |
| ngboost_laplace | 15 (6%) | 213 (91%) | 0 (0%) | 5 (2%) | 233 |
| hierarchical_logistic | 25 (7%) | 321 (84%) | 6 (2%) | 30 (8%) | 382 |
| settlement_quantile_timing | 39 (9%) | 326 (77%) | 49 (12%) | 10 (2%) | 424 |
| scarcity_logistic_interactions | 25 (7%) | 318 (84%) | 6 (2%) | 30 (8%) | 379 |

Table E. False alarms (all five horizons together) by the flagged day's regime. The first row is the non-pressure days a flag could fall on, summed over the five horizons; a cell is the count and the share of that row's false alarms.

| row | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 | total |
|---|---|---|---|---|---|---|
| non-pressure days (flag-days available) | 1355 (16%) | 1235 (14%) | 3740 (43%) | 1225 (14%) | 1100 (13%) | 8655 |
| two_part_gbm | 160 (91%) | 11 (6%) | 0 (0%) | 0 (0%) | 5 (3%) | 176 |
| ngboost_laplace | 230 (99%) | 2 (1%) | 0 (0%) | 0 (0%) | 1 (0%) | 233 |
| hierarchical_logistic | 352 (92%) | 4 (1%) | 0 (0%) | 0 (0%) | 26 (7%) | 382 |
| settlement_quantile_timing | 256 (60%) | 60 (14%) | 24 (6%) | 9 (2%) | 75 (18%) | 424 |
| scarcity_logistic_interactions | 349 (92%) | 4 (1%) | 0 (0%) | 0 (0%) | 26 (7%) | 379 |

Table F. Flag rate by the flagged day's distance to the nearest pressure day: false alarms divided by the non-pressure days in the group (all five horizons).

| row | 1 day | 2 to 5 days | 6 to 20 days | 21 days or more |
|---|---|---|---|---|
| two_part_gbm | 0.148 | 0.113 | 0.016 | 0.001 |
| ngboost_laplace | 0.193 | 0.156 | 0.022 | 0.000 |
| hierarchical_logistic | 0.350 | 0.253 | 0.023 | 0.000 |
| settlement_quantile_timing | 0.336 | 0.237 | 0.023 | 0.009 |
| scarcity_logistic_interactions | 0.352 | 0.243 | 0.028 | 0.000 |

Check against Table 1 of the re-judge (onsets flagged, worst false alarms per onset): two_part_gbm matches; ngboost_laplace matches; hierarchical_logistic matches; settlement_quantile_timing matches; scarcity_logistic_interactions matches.

