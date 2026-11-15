# Quarter-end band failure of (s3c-ann-net): event influence, tail-support provenance and same-target paths (#1533)

**Development, not a verdict.** H5, step 3 (diagnosis of the calendar-day band failure of (s3c-ann-net)). No candidate change, no lockbox day, no re-score of a published record, nothing registered. Every figure below is read from `docs/research/qe-diagnosis-1533/result.json`; the declaration is `metadata/qe_diagnosis_1533.json`, committed before any figure. Her ruling of 9 November 2026 asked for the three diagnostics together and a named mechanism.

## Mechanism

Development data on the development window, not a verdict. Read under the rules declared in `metadata/qe_diagnosis_1533.json` before any figure.

**Reading: the evidence points to a shape problem (with a location shift), not to a width problem alone. The repair it points to is, under her 9 November ruling on `h5-family-1109`, an event-conditional distribution model in place of B. A (#1531) applies one multiplier, and the ratios of point 3 say that no single multiplier fits every level. Stale support (C) is not supported. The evidence does not say what sets the 98% band's outer edge, because too few events support it.** The reading rests on a majority rule declared here (see the marked question in the pull request); at q95 it is met in 97% of the group's cells and at q99 in 60%.

The figures behind it:

1. **The failure recurs and sits in the upper tail.** On the quarter-end group the 90% band covers 0.601 [0.498, 0.701] against 0.90 and the 98% band 0.828 [0.746, 0.900] against 0.98. The upper tail misses 0.309 [0.203, 0.418] of the time against 0.05; the lower tail 0.089 [0.035, 0.149]. 18 of 30 events have coverage below 0.90 by more than one cell's worth. Leaving out any one event moves the group's 90% coverage only between 0.587 (without 2019-09) and 0.623 (without 2025-06); removing the three most influential reaches 0.670. Coverage is not a few events' doing. The scores are: three events (2018-12, 2020-03, 2024-09) carry 54% of the group's grid CRPS, against 10% if events were equal.

2. **The tails are set by ordinary-day residuals.** Quarter-end-event targets are 3.1% of the residual pool. At q95 the members that set the quantile and their neighbours are quarter-end targets 9.4% of the time; in 97% of the group's cells most of them are ordinary-day or other-turn residuals. The tail zone beyond q95 is enriched 6.7 times in quarter-end targets and is still 20% quarter-end. At q99 the setters are 31% quarter-end (60% of cells have an ordinary-day majority; the declared rule, a majority at both q95 and q99 in the median cell, is met), and the zone is 27% quarter-end. The pool does hold the signal: the root-mean-square residual of its quarter-end members is 1.45 to 1.72 times the whole pool's (median over refits, by lead), diluted by the other members.

3. **One multiplier does not fit all levels.** For the group's cells z = (y - q50)/(q95 - q05), the outcome in units of the forecast's own 90% span; the realised distance from the median over the forecast's, by level: q01 1.45, q05 1.74, q25 2.50, q75 3.87, q95 3.14 [1.93, 3.46], q99 1.54 [1.34, 1.71]. A pure width problem gives one ratio. These differ by a factor of 2.7 and by side, and the q95 and q99 intervals do not overlap. The realised median sits 0.19 span units above the forecast median [0.02, 0.38]. On ordinary-day cells, the control, the ratios are 1.11 to 1.18 in the body and median shift 0.00.

4. **Support is stale only mildly, and sparse at q99.** The tail setters are about as old as a typical pool member (the share of the pool older than a setter is 0.45 to 0.51, 0.5 being typical). The share of the tail zone from another regime than the refit's is 0.49 to 0.57 against 0.43 for the pool. That is no case for C. At q99 the zone holds about 5 members from a median of 4 distinct events; the time-block bootstrap interval of that quantile is 3.9 times the interquartile interval's width, 12.1 [7.3, 17.5] bp wide in the group's cells, against 3.7 [2.4, 5.0] bp at q95.

5. **The forecasts do not improve much as information arrives.** On quarter-end targets the absolute error changes by -0.55 [-1.26, 0.10] bp from h = 5 to h = 1, against -0.36 [-0.48, -0.23] bp on ordinary targets. 45% of quarter-end targets keep the sign and at least 80% of the size of their h = 5 error, and 22% miss the 90% band at every lead. Neither a refit nor a new settlement announcement shows a worsening, on 19 refit steps and 8 announcement steps (too few to read). At h = 1 the forecast median is no closer to the outcome than the last public spread on quarter-end targets: the model's absolute error minus persistence's is -0.25 [-1.31, 0.90] bp (ordinary targets -0.46 [-0.86, -0.17]).

**What each repair gets from this.** A (a shrunk quarter-end scale) targets the width signal of point 3 and the sparse support of point 4, and the failure that recurs (point 1); it fixes one multiplier, and the ratios say none fits every level. B (regularized quantile corrections) corrects levels one by one and would inherit the same sparse support at the outer levels. An event-conditional distribution model gives the quarter-end days their own shape and location; it is what points 2 and 3 call for. C (older or other-regime support) has no support in point 4. What the evidence cannot say: whether the outer edge (q99) is wrong in shape or only unsupported, since a median of 4 distinct events sets it; and how much of the miss any public information could have prevented (section 3 gives the last public spread beside each path).

## The same forecasts

The study regenerates the walk of `scripts/candidate_calibration_1363.py` unchanged (it only keeps the `Walk` object) and refuses to go on unless the file's sha256 and refit count equal `walk_files` in `docs/research/candidate-calibration-1363/result.json`. They do, for both windows:

| window | walk sha256 | refits | extension sha256 (not committed) |
|---|---|---|---|
| 2026 | `e409d28c54974510f215fcd5cf8644d1dd4c41dc887d7feafe90e3e612773270` | 97 | `325730d3638bb75f…` |
| development | `435375425e64d83124edb559d0574cbe7949f5ed2dd5f00f03dad7ea4f318127` | 89 | `35d8555e7b14f59a…` |

Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`. The extension holds each refit's coefficients, Huber iteration counts and residual pool, and each cell's raw (pre-cap) quantiles; it adds no forecast. Quarter-end event: every cell whose target has pressure-day type `quarter_end_turn` or `year_end`, grouped by the quarter-end it belongs to; all five leads and both turn days are one cluster. The development window has 30 events and 291 cells in the group.

## 1. Event influence

The forecasts are fixed; each event is left out of the summaries in turn. Intervals are 90% percentile intervals: whole events resampled for the group (iid, 2,000 resamples); the stationary bootstrap of target days (mean block 10) for the rest, the current day-type method with #1221's caveat that #1228 has not ruled. Paired differences are candidate minus benchmark on the same cells; negative favours the candidate.

| set | cells | 90% coverage | 98% coverage | miss < q05 | miss > q95 | miss < q01 | miss > q99 |
|---|---|---|---|---|---|---|---|
| quarter-end group | 291 | 0.601 [0.498, 0.701] | 0.828 [0.746, 0.900] | 0.089 [0.035, 0.149] | 0.309 [0.203, 0.418] | 0.045 [0.013, 0.083] | 0.127 [0.060, 0.206] |
| all other cells | 8984 | 0.884 [0.861, 0.903] | 0.969 [0.957, 0.978] | 0.067 [0.052, 0.083] | 0.050 [0.038, 0.063] | 0.019 [0.012, 0.027] | 0.013 [0.008, 0.018] |
| all cells | 9275 | 0.875 [0.852, 0.897] | 0.964 [0.953, 0.973] | 0.067 [0.052, 0.083] | 0.058 [0.045, 0.072] | 0.019 [0.013, 0.027] | 0.016 [0.011, 0.023] |

| set | grid CRPS | twCRPS | CRPS minus B1' | CRPS minus B2 | twCRPS minus B1' | twCRPS minus B2 |
|---|---|---|---|---|---|---|
| quarter-end group | 4.72 [2.42, 7.84] | 3.51 [1.29, 6.69] | -1.10 [-2.22, 0.06] | -1.85 [-2.83, -0.95] | -0.80 [-1.82, 0.07] | -1.04 [-1.93, -0.25] |
| all other cells | 1.50 [1.15, 1.96] | 0.76 [0.42, 1.22] | -0.22 [-0.31, -0.14] | -0.88 [-1.12, -0.65] | -0.13 [-0.21, -0.06] | -0.26 [-0.39, -0.15] |
| all cells | 1.60 [1.25, 2.06] | 0.84 [0.50, 1.32] | -0.25 [-0.34, -0.16] | -0.91 [-1.16, -0.69] | -0.15 [-0.24, -0.08] | -0.29 [-0.42, -0.17] |

By lead, the quarter-end group:

| h | cells | 90% coverage | 98% coverage | miss > q95 | miss < q05 | miss > q99 | miss < q01 | grid CRPS | CRPS minus B1' |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 58 | 0.638 [0.534, 0.741] | 0.828 [0.724, 0.914] | 0.276 [0.172, 0.397] | 0.086 [0.034, 0.155] | 0.155 [0.069, 0.259] | 0.017 [0.000, 0.052] | 4.51 [2.24, 7.86] | -0.67 [-1.80, 0.33] |
| 2 | 58 | 0.638 [0.534, 0.741] | 0.862 [0.776, 0.931] | 0.276 [0.172, 0.397] | 0.086 [0.034, 0.155] | 0.103 [0.034, 0.190] | 0.034 [0.000, 0.069] | 4.49 [2.22, 7.86] | -0.33 [-1.14, 0.50] |
| 3 | 58 | 0.621 [0.517, 0.724] | 0.845 [0.759, 0.914] | 0.293 [0.190, 0.397] | 0.086 [0.034, 0.138] | 0.103 [0.034, 0.172] | 0.052 [0.017, 0.103] | 4.72 [2.47, 7.98] | -1.08 [-2.25, 0.05] |
| 4 | 58 | 0.534 [0.414, 0.655] | 0.810 [0.724, 0.897] | 0.362 [0.224, 0.500] | 0.103 [0.034, 0.172] | 0.121 [0.052, 0.207] | 0.069 [0.017, 0.121] | 4.93 [2.74, 8.07] | -1.57 [-2.99, -0.15] |
| 5 | 59 | 0.576 [0.450, 0.707] | 0.797 [0.695, 0.883] | 0.339 [0.203, 0.467] | 0.085 [0.017, 0.155] | 0.153 [0.067, 0.250] | 0.051 [0.017, 0.102] | 4.95 [2.68, 7.83] | -1.83 [-3.33, -0.32] |

Leaving one event out (range over the left-out events, the event at each end named). This is a range, not an interval.

| group figure, pooled over leads | all events | lowest | highest |
|---|---|---|---|
| 90% coverage | 0.601 | 0.587 (without 2019-09) | 0.623 (without 2025-06) |
| miss > q95 | 0.309 | 0.285 (without 2018-12) | 0.320 (without 2025-09) |
| miss > q99 | 0.127 | 0.096 (without 2018-12) | 0.132 (without 2025-09) |
| miss < q05 | 0.089 | 0.068 (without 2020-03) | 0.093 (without 2025-09) |
| grid CRPS | 4.722 | 3.115 (without 2018-12) | 4.884 (without 2021-12) |
| twCRPS | 3.511 | 1.863 (without 2018-12) | 3.636 (without 2024-03) |
| CRPS minus B1' | -1.099 | -1.582 (without 2020-03) | -0.739 (without 2018-12) |
| CRPS minus B2 | -1.850 | -2.107 (without 2025-06) | -1.513 (without 2019-09) |

Dropping the events that move the group's 90% coverage most, one at a time: 2025-06 (0.623), then 2024-09 (0.646), then 2018-12 (0.670).

| h | 90% coverage | miss > q95 | miss > q99 | CRPS minus B1' (group) |
|---|---|---|---|---|
| 1 | 0.625 to 0.661 | 0.250 to 0.286 | 0.125 to 0.161 | -1.025 to -0.177 |
| 2 | 0.625 to 0.661 | 0.250 to 0.286 | 0.071 to 0.107 | -0.700 to -0.045 |
| 3 | 0.607 to 0.643 | 0.268 to 0.304 | 0.071 to 0.107 | -1.566 to -0.730 |
| 4 | 0.518 to 0.554 | 0.339 to 0.375 | 0.089 to 0.125 | -2.156 to -1.115 |
| 5 | 0.561 to 0.596 | 0.316 to 0.351 | 0.123 to 0.158 | -2.447 to -1.359 |

Leaving each event out of **all** cells (the other cells kept): the overall figure moves in this range.

|  | 90% coverage | 98% coverage | miss > q95 | miss > q99 | grid CRPS |
|---|---|---|---|---|---|
| pooled | 0.875 to 0.876 | 0.964 to 0.965 | 0.057 to 0.058 | 0.015 to 0.016 | 1.549 to 1.603 |
| h1 | 0.881 to 0.882 | 0.965 to 0.967 | 0.053 to 0.055 | 0.016 to 0.017 | 1.424 to 1.479 |
| h2 | 0.879 to 0.880 | 0.966 to 0.967 | 0.054 to 0.055 | 0.015 to 0.016 | 1.513 to 1.568 |
| h3 | 0.873 to 0.874 | 0.964 to 0.965 | 0.056 to 0.057 | 0.014 to 0.015 | 1.554 to 1.609 |
| h4 | 0.869 to 0.870 | 0.964 to 0.965 | 0.061 to 0.062 | 0.015 to 0.016 | 1.600 to 1.652 |
| h5 | 0.872 to 0.873 | 0.962 to 0.963 | 0.060 to 0.061 | 0.016 to 0.017 | 1.655 to 1.705 |

Concentration: the three events with the largest summed grid CRPS (2018-12, 2020-03, 2024-09) carry 54% of the group's total, and the three with the largest twCRPS (2018-12, 2019-09, 2024-09) 68%; equal events would carry 10%.

By pressure-day type (the group's labels are resampled by event):

| type | cells | 90% coverage | 98% coverage | miss > q95 | grid CRPS | CRPS minus B1' |
|---|---|---|---|---|---|---|
| ordinary | 7939 | 0.890 [0.867, 0.911] | 0.971 [0.961, 0.981] | 0.044 [0.032, 0.057] | 1.29 [1.10, 1.49] | -0.18 [-0.27, -0.09] |
| quarter_end_turn | 220 | 0.586 [0.473, 0.695] | 0.850 [0.773, 0.923] | 0.336 [0.214, 0.459] | 3.51 [2.31, 4.92] | -0.72 [-2.08, 0.66] |
| tax_date | 445 | 0.840 [0.769, 0.910] | 0.944 [0.910, 0.975] | 0.076 [0.029, 0.124] | 5.08 [0.96, 12.44] | -0.32 [-0.66, -0.01] |
| turn | 600 | 0.833 [0.792, 0.875] | 0.957 [0.928, 0.983] | 0.110 [0.052, 0.167] | 1.69 [1.01, 2.53] | -0.71 [-1.14, -0.29] |
| year_end | 71 | 0.648 [0.419, 0.845] | 0.761 [0.528, 0.925] | 0.225 [0.014, 0.500] | 8.47 [1.26, 20.59] | -2.27 [-5.08, 0.10] |

By regime of the event (the group) and of the target (the rest):

| regime | events | group 90% coverage | group miss > q95 | group CRPS minus B1' | rest 90% coverage | rest CRPS minus B1' |
|---|---|---|---|---|---|---|
| 2018-19 | 6 | 0.455 [0.222, 0.683] | 0.455 [0.200, 0.683] | -4.60 [-8.15, -0.96] | 0.880 [0.846, 0.916] | -0.28 [-0.52, -0.02] |
| 2020 | 5 | 0.550 [0.371, 0.756] | 0.000 [0.000, 0.000] | 3.49 [0.14, 7.64] | 0.875 [0.816, 0.933] | -0.24 [-0.55, -0.01] |
| 2021-23 | 13 | 0.758 [0.608, 0.896] | 0.217 [0.088, 0.360] | -0.18 [-0.37, -0.01] | 0.878 [0.836, 0.918] | -0.03 [-0.06, 0.01] |
| 2024 | 5 | 0.375 [0.140, 0.667] | 0.625 [0.333, 0.860] | -2.47 [-4.11, -0.99] | 0.898 [0.849, 0.936] | -0.23 [-0.46, -0.07] |
| 2025-26 | 5 | 0.611 [0.244, 0.933] | 0.389 [0.067, 0.756] | -2.41 [-3.28, -1.69] | 0.900 [0.856, 0.934] | -0.70 [-0.99, -0.44] |

Per event (all five leads, both turn days):

| event | regime | cells | 90% cov | 98% cov | miss > q95 | miss < q05 | miss > q99 | grid CRPS | minus B1' | minus B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018-09 | 2018-19 | 10 | 0.40 | 0.80 | 0.60 | 0.00 | 0.20 | 2.77 | -0.56 | 1.43 |
| 2018-12 | 2018-19 | 10 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 | 49.87 | -11.21 | -6.63 |
| 2019-03 | 2018-19 | 10 | 0.50 | 0.50 | 0.50 | 0.00 | 0.50 | 8.82 | -2.11 | 1.28 |
| 2019-06 | 2018-19 | 10 | 0.60 | 1.00 | 0.40 | 0.00 | 0.00 | 2.60 | -1.51 | 0.17 |
| 2019-09 | 2018-19 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 9.89 | -11.13 | -11.33 |
| 2019-12 | 2018-19 | 10 | 0.50 | 0.80 | 0.00 | 0.50 | 0.00 | 2.24 | 1.06 | -8.21 |
| 2020-03 | 2020 | 10 | 0.30 | 0.50 | 0.00 | 0.70 | 0.00 | 13.29 | 12.47 | -5.30 |
| 2020-06 | 2020 | 10 | 0.80 | 1.00 | 0.00 | 0.20 | 0.00 | 1.34 | -0.02 | -2.81 |
| 2020-09 | 2020 | 10 | 0.50 | 0.60 | 0.00 | 0.50 | 0.00 | 1.57 | 0.83 | -0.96 |
| 2020-12 | 2020 | 10 | 0.60 | 0.80 | 0.00 | 0.40 | 0.00 | 1.75 | 0.67 | 0.53 |
| 2021-03 | 2021-23 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.36 | -0.13 | -3.02 |
| 2021-06 | 2021-23 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.43 | 0.07 | -3.70 |
| 2021-09 | 2021-23 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.22 | 0.01 | -0.75 |
| 2021-12 | 2021-23 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.15 | 0.00 | 0.06 |
| 2022-03 | 2021-23 | 10 | 0.80 | 0.90 | 0.20 | 0.00 | 0.10 | 0.68 | -0.62 | 0.10 |
| 2022-06 | 2021-23 | 10 | 0.50 | 1.00 | 0.50 | 0.00 | 0.00 | 1.77 | -1.07 | -1.95 |
| 2022-09 | 2021-23 | 10 | 0.50 | 0.90 | 0.20 | 0.30 | 0.10 | 1.09 | 0.15 | -2.41 |
| 2022-12 | 2021-23 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.28 | -0.11 | -2.28 |
| 2023-03 | 2021-23 | 10 | 0.10 | 0.30 | 0.90 | 0.00 | 0.70 | 3.36 | 0.34 | -4.27 |
| 2023-06 | 2021-23 | 10 | 0.50 | 0.80 | 0.50 | 0.00 | 0.20 | 1.56 | -0.08 | -1.27 |
| 2023-09 | 2021-23 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.39 | -0.13 | -0.79 |
| 2023-12 | 2021-23 | 10 | 0.50 | 0.80 | 0.50 | 0.00 | 0.20 | 2.88 | -0.82 | -1.82 |
| 2024-03 | 2024 | 10 | 0.10 | 1.00 | 0.90 | 0.00 | 0.00 | 1.52 | -0.57 | 0.66 |
| 2024-06 | 2024 | 10 | 0.60 | 1.00 | 0.40 | 0.00 | 0.00 | 2.23 | -1.22 | -1.12 |
| 2024-09 | 2024 | 10 | 0.00 | 0.50 | 1.00 | 0.00 | 0.50 | 11.46 | -4.07 | -3.36 |
| 2024-12 | 2024 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.76 | -5.46 | -1.99 |
| 2025-03 | 2025-26 | 10 | 0.70 | 1.00 | 0.30 | 0.00 | 0.00 | 2.66 | -2.17 | 0.83 |
| 2025-06 | 2025-26 | 10 | 0.00 | 0.90 | 1.00 | 0.00 | 0.10 | 7.31 | -1.17 | 5.37 |
| 2025-09 | 2025-26 | 10 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.95 | -3.14 | 0.16 |
| 2025-12 | 2025-26 | 1 | 0.00 | 0.00 | 1.00 | 0.00 | 1.00 | 12.00 | -2.52 | -4.40 |

**What it informs.** Does A address a recurring failure, or is its apparent benefit dominated by a few exceptional events? The coverage failure recurs: 18 of 30 events fall below 0.90 and no single event moves the group's coverage by more than 0.021. The CRPS and twCRPS are concentrated in a few events, so a benefit read from CRPS alone, on this group, can be dominated by them; a benefit read from coverage cannot. With about thirty events the intervals are wide, and the group's CRPS difference to B1' has an interval that includes zero.

## 2. Tail-support provenance

The candidate's quantiles are `centre + scale * (shift + pool)`: the tails are the pool's order statistics, interpolated as `protocol_benchmarks.empirical_quantiles`. For every refit in force on a scored day and every lead, `docs/research/qe-diagnosis-1533/tail-support.json` lists, for q01, q05, q95 and q99, the setters (the one or two members at the interpolated ranks), their neighbours (the ranks just outside), their dates, day types and regimes, the members of the tail zone beyond the quantile, the distinct events among them, and the time-block bootstrap interval of the quantile. The pool is the training pairs of the refit (about 500 pairs per lead at the median refit; the first refits are smaller).

The group's cells, each read at the refit in force at its decision and its lead (intervals resample events):

| tail | cells | setters and neighbours that are quarter-end targets | cells with an ordinary-day majority | tail zone that is quarter-end | zone enrichment (x the pool's share) | distinct events in zone (median) | share of pool older than a setter |
|---|---|---|---|---|---|---|---|
| q01 | 291 | 0.021 [0.009, 0.036] | 100% | 0.019 [0.007, 0.033] | 0.6 [0.2, 1.0] | 3 | 0.48 |
| q05 | 291 | 0.009 [0.003, 0.016] | 100% | 0.020 [0.013, 0.026] | 0.6 [0.4, 0.8] | 10 | 0.48 |
| q95 | 291 | 0.094 [0.070, 0.116] | 97% | 0.199 [0.164, 0.233] | 6.7 [5.3, 8.1] | 12 | 0.46 |
| q99 | 291 | 0.312 [0.236, 0.393] | 60% | 0.272 [0.204, 0.347] | 9.5 [6.7, 12.7] | 4 | 0.46 |

The uncertainty of each tail of the pool (time-block bootstrap of the pool in target order, 500 resamples, mean block 10 declared before any figure; widths of the 90% interval, in scale units, median over refits; the same at mean blocks 5 and 20 beside):

| tail | h | width (block 10) | block 5 | block 20 | x the IQR's width | median's width | zone members | distinct events (median) | range |
|---|---|---|---|---|---|---|---|---|---|
| q01 | 1 | 1.52 | 1.48 | 1.51 | 1.21 | 0.08 | 5 | 4 | 1 to 5 |
| q01 | 3 | 2.03 | 1.87 | 2.09 | 1.06 | 0.25 | 5 | 3 | 1 to 5 |
| q01 | 5 | 2.21 | 2.09 | 2.20 | 1.15 | 0.33 | 5 | 3 | 1 to 5 |
| q05 | 1 | 1.17 | 1.12 | 1.21 | 0.71 | 0.08 | 25 | 11 | 1 to 15 |
| q05 | 3 | 1.23 | 1.14 | 1.21 | 0.85 | 0.25 | 25 | 9 | 2 to 15 |
| q05 | 5 | 1.45 | 1.26 | 1.47 | 0.81 | 0.33 | 25 | 8 | 2 to 16 |
| q95 | 1 | 1.98 | 1.91 | 1.96 | 1.53 | 0.08 | 25 | 15 | 2 to 18 |
| q95 | 3 | 2.62 | 2.46 | 2.45 | 1.42 | 0.25 | 25 | 12 | 2 to 18 |
| q95 | 5 | 2.94 | 2.70 | 2.73 | 1.49 | 0.33 | 25 | 11 | 2 to 17 |
| q99 | 1 | 5.41 | 5.41 | 5.24 | 3.66 | 0.08 | 5 | 4 | 1 to 5 |
| q99 | 3 | 6.44 | 6.23 | 6.36 | 3.90 | 0.25 | 5 | 4 | 1 to 5 |
| q99 | 5 | 7.14 | 6.94 | 7.10 | 4.42 | 0.33 | 5 | 4 | 1 to 5 |

In basis points, for the group's cells (width x the scale the forecast used): q01 3.3 [2.4, 4.3]; q05 2.0 [1.4, 2.6]; q95 3.7 [2.4, 5.0]; q99 12.1 [7.3, 17.5]. The median pool in those cells has 499 members (smallest 91).

Staleness and regime: by tail and lead (mean over refits):

| tail | h | setters+neighbours quarter-end | zone quarter-end | pool quarter-end | older-than-setter share | zone from another regime | pool from another regime |
|---|---|---|---|---|---|---|---|
| q95 | 1 | 8.4% | 20.6% | 3.2% | 0.46 | 51% | 43% |
| q95 | 2 | 9.8% | 19.3% | 3.2% | 0.47 | 52% | 43% |
| q95 | 3 | 7.6% | 20.5% | 3.2% | 0.46 | 51% | 43% |
| q95 | 4 | 9.6% | 23.3% | 3.2% | 0.48 | 50% | 43% |
| q95 | 5 | 13.2% | 23.1% | 3.2% | 0.50 | 49% | 43% |
| q99 | 1 | 32.6% | 35.8% | 3.2% | 0.49 | 56% | 43% |
| q99 | 2 | 26.1% | 23.2% | 3.2% | 0.51 | 57% | 43% |
| q99 | 3 | 29.5% | 27.8% | 3.2% | 0.46 | 57% | 43% |
| q99 | 4 | 30.6% | 28.3% | 3.2% | 0.45 | 57% | 43% |
| q99 | 5 | 38.8% | 28.5% | 3.2% | 0.48 | 56% | 43% |

The candidate is the pool's quantile clipped at the full-allotment line. In the group the clip changes q95 in 1 of 291 cells and q99 in 1; so the group's tails are the pool's. Outside the group it changes q99 in 49 cells.

Pool composition: the root-mean-square residual of the quarter-end members over that of the whole pool (the `m_raw` of #1402), by lead, median and range over refits:

| h | median | range |
|---|---|---|
| 1 | 1.72 | [0.38, 4.66] |
| 2 | 1.45 | [0.39, 4.51] |
| 3 | 1.57 | [0.53, 4.69] |
| 4 | 1.65 | [0.61, 4.74] |
| 5 | 1.60 | [0.74, 4.72] |

**Huber iterations (a fact only; the stricter replay is her item 7).** Of 445 fits (refit x lead) in force on scored days, 9 ended at the iteration cap of 50 (a fit that converged on exactly the last allowed iteration is counted with them); the median fit took 18 iterations. By lead: h = 1: 2 of 89, h = 2: 3 of 89, h = 3: 2 of 89, h = 4: 1 of 89, h = 5: 1 of 89.

**What it informs.** Sparse support favours shrinkage or partial pooling (A-type); stale support strengthens C. The tails of the quarter-end forecasts are set by ordinary-day members, with the quarter-end members enriched in the tail zone but a minority of it; the q99 rests on a handful of members from a handful of events; the setters are not older than typical and the regime mix of the zone differs only mildly.

## 2b. Width or shape (her docket ruling h5-family-1109)

For the group's cells, z = (y - q50) / (q95 - q05) on the raw (pre-cap) quantiles: the outcome in units of the forecast's own 90% span. The forecast law has its own z at each level; the ratio is the realised distance from the realised median over the law's. A pure width problem has one ratio at every level and on both sides; a shape problem has ratios that change with the level or the side. Intervals resample whole events (the control, stationary blocks of target days).

| set | cells | median z (shift) | q01 | q05 | q25 | q75 | q95 | q99 |
|---|---|---|---|---|---|---|---|---|
| quarter-end group | 291 | 0.19 [0.02, 0.38] | 1.45 [1.06, 1.67] | 1.74 [1.19, 2.30] | 2.50 [1.56, 3.69] | 3.87 [2.65, 6.32] | 3.14 [1.93, 3.46] | 1.54 [1.34, 1.71] |
| ordinary days (control) | 7939 | 0.00 [-0.01, 0.00] | 1.37 [1.00, 1.61] | 1.11 [0.98, 1.28] | 1.18 [0.96, 1.31] | 0.90 [0.77, 1.01] | 0.89 [0.75, 1.03] | 0.80 [0.63, 1.04] |

The law's z by level for the group: q01 -0.74, q05 -0.42, q25 -0.12, q75 0.13, q95 0.58, q99 1.36; the realised, from the realised median: q01 -1.08, q05 -0.73, q25 -0.29, q75 0.50, q95 1.83, q99 2.10.

By regime of the event, label and lead (point values; events are few, so no interval is shown):

| split | cells | median z (shift) | q01 | q05 | q25 | q75 | q95 | q99 |
|---|---|---|---|---|---|---|---|---|
| 2018-19 (6 events) | 55 | 0.56 | 1.87 | 2.92 | 4.06 | 7.14 | 2.65 | 1.21 |
| 2020 (5 events) | 40 | -0.32 | 1.06 | 1.51 | 1.85 | 1.28 | 0.75 | 0.49 |
| 2021-23 (13 events) | 120 | 0.06 | 1.10 | 0.79 | 1.34 | 2.98 | 2.41 | 1.81 |
| 2024 (5 events) | 40 | 0.63 | 0.90 | 1.71 | 2.89 | 4.30 | 2.73 | 1.31 |
| 2025-26 (5 events) | 36 | 0.40 | 1.12 | 1.33 | 0.67 | 2.63 | 1.44 | 0.70 |
| quarter_end_turn (22 events) | 220 | 0.27 | 1.56 | 1.93 | 3.30 | 3.42 | 2.94 | 1.40 |
| year_end (8 events) | 71 | 0.00 | 0.83 | 1.25 | 0.65 | 2.81 | 3.75 | 1.80 |
| h = 1 | 58 | 0.13 | 0.96 | 1.33 | 2.30 | 4.62 | 3.54 | 1.73 |
| h = 2 | 58 | 0.13 | 1.00 | 1.35 | 2.20 | 3.72 | 2.90 | 1.48 |
| h = 3 | 58 | 0.21 | 1.37 | 1.91 | 2.28 | 3.50 | 2.99 | 1.47 |
| h = 4 | 58 | 0.21 | 1.47 | 2.08 | 2.38 | 3.77 | 3.02 | 1.47 |
| h = 5 | 59 | 0.19 | 1.42 | 1.83 | 2.74 | 3.74 | 2.90 | 1.45 |

The reading is descriptive: no multiplier is fitted or scored here, about thirty events is small, and the ratios in the body are inflated by any shift in location that the median removes imperfectly.

## 3. Same-target paths

For each target day with all five leads, the forecast at h = 5, 4, 3, 2, 1: median, q05, q95, q01, q99 and the eventual error y - median. Each step from h + 1 to h is marked: new refit (the fit in force differs), new settlement announcement (the settlement flags or sizes the forecast read differ, from `metadata/settlement_announcement_dating.json` as served by `repo_model.s3c_announced`), new spread (always one panel day). The full paths of every quarter-end target are in `result.json` (`item3.failed_events` for the failed events).

| targets | n | mean |error| h=5 | h=3 | h=1 | 90% miss h=5 | h=1 | |error| h=1 minus h=5 | keeps sign and 80% of size | misses at every h |
|---|---|---|---|---|---|---|---|---|---|
| quarter-end group | 58 | 6.37 [3.66, 9.99] | 6.15 [3.40, 10.01] | 5.82 [3.08, 9.82] | 0.41 [0.29, 0.55] | 0.36 [0.26, 0.47] | -0.55 [-1.26, 0.10] | 0.45 [0.33, 0.57] | 0.22 [0.12, 0.33] |
| ordinary | 1584 | 1.99 [1.69, 2.31] | 1.84 [1.58, 2.16] | 1.63 [1.37, 1.94] | 0.11 [0.09, 0.14] | 0.10 [0.08, 0.12] | -0.36 [-0.48, -0.23] | 0.38 [0.35, 0.40] | 0.05 [0.04, 0.07] |
| tax_date | 89 | 6.16 [1.47, 14.62] | 6.00 [1.36, 14.32] | 5.85 [1.26, 13.91] | 0.12 [0.06, 0.20] | 0.20 [0.12, 0.28] | -0.31 [-0.79, 0.15] | 0.58 [0.49, 0.67] | 0.09 [0.03, 0.15] |
| turn | 120 | 2.57 [1.62, 3.75] | 2.47 [1.56, 3.60] | 2.26 [1.31, 3.45] | 0.17 [0.12, 0.23] | 0.16 [0.10, 0.22] | -0.31 [-0.57, -0.08] | 0.42 [0.33, 0.50] | 0.08 [0.04, 0.12] |
|   quarter_end_turn | 44 | 5.08 [3.34, 7.17] | 4.83 [3.13, 6.76] | 4.63 [3.10, 6.35] | 0.43 [0.27, 0.59] | 0.39 [0.27, 0.50] | -0.45 [-1.27, 0.19] | 0.48 [0.32, 0.61] | 0.23 [0.11, 0.34] |
|   year_end | 14 | 10.39 [1.80, 25.36] | 10.30 [1.49, 26.43] | 9.54 [0.67, 26.27] | 0.36 [0.07, 0.64] | 0.29 [0.07, 0.50] | -0.85 [-2.58, 0.96] | 0.36 [0.14, 0.57] | 0.21 [0.00, 0.43] |
|   group, 2018-19 (6 events) | 11 | 16.68 [5.62, 29.97] | 17.87 [6.15, 31.77] | 17.58 [5.65, 31.44] | 0.55 [0.25, 0.88] | 0.45 [0.18, 0.70] | 0.90 [-0.04, 1.70] | 0.91 [0.67, 1.00] | 0.36 [0.09, 0.64] |
|   group, 2020 (5 events) | 8 | 6.81 [1.73, 13.03] | 5.74 [1.53, 11.05] | 5.32 [1.87, 9.09] | 0.38 [0.00, 0.67] | 0.50 [0.33, 0.62] | -1.49 [-4.46, 1.42] | 0.25 [0.00, 0.50] | 0.25 [0.00, 0.44] |
|   group, 2021-23 (13 events) | 24 | 1.67 [0.98, 2.49] | 1.35 [0.81, 2.00] | 1.06 [0.67, 1.51] | 0.29 [0.12, 0.50] | 0.21 [0.08, 0.38] | -0.60 [-1.22, -0.13] | 0.25 [0.12, 0.38] | 0.08 [0.00, 0.17] |
|   group, 2024 (5 events) | 8 | 6.47 [3.41, 10.66] | 5.18 [2.21, 9.64] | 5.25 [1.29, 10.41] | 0.75 [0.50, 1.00] | 0.50 [0.17, 0.75] | -1.22 [-3.86, 0.29] | 0.62 [0.29, 0.89] | 0.38 [0.00, 0.70] |
|   group, 2025-26 (4 events) | 7 | 5.64 [2.48, 8.10] | 5.78 [3.62, 8.22] | 4.86 [2.76, 6.44] | 0.29 [0.00, 0.67] | 0.43 [0.00, 0.75] | -0.77 [-2.56, 0.77] | 0.43 [0.00, 0.75] | 0.29 [0.00, 0.67] |
|   non-event, 2018-19 | 346 | 4.75 [3.29, 6.91] | 4.45 [2.97, 6.65] | 4.29 [2.70, 6.71] | 0.12 [0.08, 0.16] | 0.13 [0.10, 0.17] | -0.46 [-0.78, -0.05] | 0.42 [0.37, 0.47] | 0.06 [0.04, 0.09] |
|   non-event, 2020 | 243 | 2.16 [1.48, 3.08] | 1.99 [1.33, 2.86] | 1.71 [1.13, 2.50] | 0.15 [0.07, 0.23] | 0.10 [0.05, 0.15] | -0.45 [-0.62, -0.31] | 0.39 [0.34, 0.45] | 0.07 [0.02, 0.11] |
|   non-event, 2021-23 | 724 | 0.94 [0.71, 1.19] | 0.84 [0.65, 1.04] | 0.64 [0.51, 0.79] | 0.12 [0.08, 0.17] | 0.11 [0.08, 0.15] | -0.29 [-0.43, -0.17] | 0.35 [0.31, 0.39] | 0.07 [0.04, 0.10] |
|   non-event, 2024 | 242 | 1.37 [0.94, 1.90] | 1.43 [0.99, 1.95] | 1.38 [0.96, 1.90] | 0.07 [0.04, 0.12] | 0.12 [0.07, 0.17] | 0.02 [-0.17, 0.18] | 0.45 [0.40, 0.51] | 0.02 [0.00, 0.05] |
|   non-event, 2025-26 | 238 | 3.48 [2.77, 4.29] | 3.26 [2.69, 3.90] | 2.81 [2.29, 3.39] | 0.11 [0.07, 0.15] | 0.08 [0.05, 0.12] | -0.67 [-1.02, -0.36] | 0.41 [0.35, 0.46] | 0.04 [0.01, 0.06] |

How a step changes the absolute error, by what the step brought (group first, then every other target):

| set | the step brought | steps | share where |error| rises | mean change (bp) |
|---|---|---|---|---|
| quarter-end group | neither | 204 | 43% | -0.154 |
| quarter-end group | refit | 19 | 58% | -0.001 |
| quarter-end group | announcement | 8 | 25% | -0.048 |
| quarter-end group | both | 1 | 100% | 0.207 |
| other targets | neither | 6654 | 40% | -0.087 |
| other targets | refit | 323 | 43% | -0.128 |
| other targets | announcement | 186 | 48% | -0.072 |
| other targets | both | 9 | 22% | -0.412 |

By step, the group's mean change of |error| (h + 1 to h): to h = 4: 0.11 [-0.08, 0.31]; to h = 3: -0.32 [-0.54, -0.10]; to h = 2: -0.26 [-0.55, 0.00]; to h = 1: -0.08 [-0.34, 0.17].

Failed events (at least half of the cells outside the closed 90% band): 14 of 29. The path of each target, as error at h = 5, 4, 3, 2, 1 in bp (`*` marks a miss of the 90% band; `R` a new refit, `A` a new settlement announcement on that step):

| event | regime | target | label | outcome | h=5 | h=4 | h=3 | h=2 | h=1 | last public spread at h=1 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018-09 | 2018-19 | 2018-09-28 | quarter_end_turn | 5 | +5.3* | +5.5* | +5.5* | +5.7* | +5.7 | -3 |
| 2018-09 | 2018-19 | 2018-10-01 | quarter_end_turn | 2 | +2.4* | +2.3* | +2.4 | +1.9 | +3.2 | -4 |
| 2018-12 | 2018-19 | 2018-12-31 | year_end | 60 | +48.7* | +49.9* | +52.3* | +52.9* | +51.9* | 4 |
| 2018-12 | 2018-19 | 2019-01-02 | year_end | 75 | +64.2* | +66.4* | +66.7* | +68.0* | +68.4* | 6 |
| 2019-03 | 2018-19 | 2019-03-29 | quarter_end_turn | 25 | +19.6* | +19.9*R | +20.3* | +20.6* | +20.5* | 0 |
| 2019-03 | 2018-19 | 2019-04-01 | quarter_end_turn | 6 | +1.4 | +1.7 | +1.8 | +2.2 | +1.8 | 3 |
| 2019-12 | 2018-19 | 2019-12-31 | year_end | 0 | -6.1* | -6.3*RA | -5.6* | -4.4* | -4.0* | -2 |
| 2019-12 | 2018-19 | 2020-01-02 | year_end | -1 | -1.8 | -1.2A | -0.6 | -0.5 | -0.4 | -1 |
| 2020-03 | 2020 | 2020-03-31 | quarter_end_turn | -9 | -28.7* | -28.2* | -25.9*R | -21.1* | -20.6*A | -9 |
| 2020-03 | 2020 | 2020-04-01 | quarter_end_turn | -9 | -14.1* | -12.0*R | -8.9 | -8.8A | -6.6 | -9 |
| 2020-09 | 2020 | 2020-09-30 | quarter_end_turn | -2 | -3.5* | -3.2*R | -3.0* | -3.1* | -2.7* | -2 |
| 2020-09 | 2020 | 2020-10-01 | quarter_end_turn | -2 | -1.5 | -1.5 | -1.2 | -0.8 | -0.6 | -3 |
| 2022-06 | 2021-23 | 2022-06-30 | quarter_end_turn | -15 | +2.4* | +3.4* | +3.5* | +0.9 | -1.0 | -13 |
| 2022-06 | 2021-23 | 2022-07-01 | quarter_end_turn | -13 | +4.7* | +4.8* | +2.5 | +1.1 | +1.6 | -14 |
| 2022-09 | 2021-23 | 2022-09-30 | quarter_end_turn | -17 | -2.7* | -2.5* | -1.9* | -0.6 | -0.2 | -17 |
| 2022-09 | 2021-23 | 2022-10-03 | quarter_end_turn | -15 | -0.7 | -0.2 | +0.9 | +1.4* | +3.5*R | -19 |
| 2023-03 | 2021-23 | 2023-03-31 | quarter_end_turn | -3 | +6.8* | +6.8* | +6.1* | +3.6* | +4.3* | -7 |
| 2023-03 | 2021-23 | 2023-04-03 | quarter_end_turn | -6 | +3.6* | +2.9* | +0.7 | +1.3* | +2.2* | -8 |
| 2023-06 | 2021-23 | 2023-06-30 | quarter_end_turn | -6 | +3.7* | +3.6* | +3.7* | +3.7* | +3.1* | -9 |
| 2023-06 | 2021-23 | 2023-07-03 | quarter_end_turn | -9 | +0.5 | +0.5 | +0.5 | -0.1 | +0.0 | -9 |
| 2023-12 | 2021-23 | 2023-12-29 | year_end | -2 | +5.5* | +5.7* | +5.3* | +2.5 | -0.6 | -1 |
| 2023-12 | 2021-23 | 2024-01-02 | year_end | 0 | +7.0* | +6.6*A | +3.1 | +0.2 | -0.2 | 0 |
| 2024-03 | 2024 | 2024-03-28 | quarter_end_turn | -6 | +2.3* | +2.3* | +2.4* | +2.5* | +2.1* | -8 |
| 2024-03 | 2024 | 2024-04-01 | quarter_end_turn | -5 | +2.2* | +2.3* | +2.4* | +1.9* | +1.3 | -7 |
| 2024-09 | 2024 | 2024-09-30 | quarter_end_turn | 6 | +8.2* | +7.9* | +7.5* | +7.8* | +9.4* | -7 |
| 2024-09 | 2024 | 2024-10-01 | quarter_end_turn | 15 | +19.6* | +19.5* | +19.4* | +20.3* | +20.7* | -6 |
| 2025-06 | 2025-26 | 2025-06-30 | quarter_end_turn | 5 | +9.5* | +8.9* | +8.8* | +8.1* | +6.1* | 0 |
| 2025-06 | 2025-26 | 2025-07-01 | quarter_end_turn | 4 | +13.0* | +12.5* | +11.6* | +10.4* | +9.9* | -1 |

**What it informs.** Whether the forecasts improve as information arrives, stay misplaced, or worsen after one update; the tables separate an information limit from a fitting problem only as far as these rows go. Quarter-end targets: the error changes little from h = 5 to h = 1 and its interval includes zero, while on ordinary targets it shrinks clearly. The last public spread, compared with the forecast median:

| targets | h | model |error| minus persistence |error| (bp) | share where persistence is closer |
|---|---|---|---|
| quarter-end group | 5 | -1.69 [-3.20, 0.07] | 0.28 [0.16, 0.40] |
| quarter-end group | 1 | -0.25 [-1.31, 0.90] | 0.52 [0.40, 0.64] |
| ordinary targets | 5 | -0.69 [-1.15, -0.32] | 0.48 [0.46, 0.51] |
| ordinary targets | 1 | -0.46 [-0.86, -0.17] | 0.51 [0.48, 0.53] |

## The 2026 days (shown apart, decide nothing)

The 2026 window has 3 quarter-end events and 21 group cells, against 804 others. Group 90% coverage 0.952 [0.833, 1.000], 98% coverage 0.952 [0.833, 1.000], miss > q95 0.048 [0.000, 0.167]. The full tables are in `result.json` under `windows.2026`. They were already seen by earlier studies and are too few to read.

## Limits and what was not checked

- Development data on seen days, never a verdict. The development window has about thirty quarter-end events; every interval from it is wide and every split by regime has five to thirteen events.
- The diagnosis reads the candidate's own walk. It fits and scores nothing new, tunes nothing, and registers nothing.
- The Huber iteration counts are a fact; whether stricter convergence changes any forecast is her item 7, not done. Her items 4 (out-of-sample predictability of misses), 5 (error against fit age) and 6 (interval-score decomposition) are a later package.
- The same-target step table separates a new refit and a new settlement announcement from a plain step, but a step also carries one new public spread and other inputs this study does not isolate.
- The mechanism reading depends on the majority rule declared here for 'set by ordinary-day residuals'. It is met at q95 in nearly every cell and at q99 in a bit over half of them. The pull request marks it as a question for her.
- B4 (#1360) is not compared. The 98% band is q01 to q99, closed.

## Reproduction

See the header of `scripts/qe_diagnosis_1533.py`; the test is `tests/test_qe_diagnosis_1533.py`. Seed 1533 throughout.
