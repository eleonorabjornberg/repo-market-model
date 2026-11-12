# A per-tail scale by calendar flag, fitted walk-forward (#1555)

**Development, not a verdict.** H5, step 4 (avenue #1546). The arm does not change the frozen candidate (s3c-ann-net); it is in `not_arms` of the H5 registration manifest until Eleonora rules. No lockbox day, no re-score of a published record, nothing registered or published. Every figure is read from `docs/research/calendar-flag-scale-arm-1555/result.json`; the declaration is `metadata/calendar_flag_scale_arm_1555.json`, committed before any score. The forecasts are #1533's walk extension, regenerated bit-identical from the 1363 walk (no refit).

## The arm

On a target day in an arm group, the candidate's quantiles on a side of the median are scaled about q50 by that side's factor. Groups and tails: `dom_19_23` q05 and q95, `coupon_settlement` q95, `post_month_end_window` q95, days with no calendar flag and no pressure-day type q95. Each factor is fitted at each decision day from the group's cells whose target day is strictly before it (#1533's ratio at that tail on the raw quantiles), shrunk as `m = 1 + n/(n + 500) (ratio - 1)`, and 1 with fewer than 100 usable training cells. A day in several groups takes the geometric mean of its flags' factors on each side. Quarter-end days (the flag, or the types quarter_end_turn and year_end) are in no group and keep the candidate's forecast, and their cells are not training cells. The sizes come from the walk, not from #1547's point values. Every other forecast is the candidate's, the same numbers (3394 cells outside the arm groups were checked equal). The arm trains on no fitter of its own: it reads the candidate's cells, so it is not a producer for the provisional register.

The factors the walk gave (the first decision day of each year, and the last of the window):

| group, tail | first decision day of each year | last day | range |
|---|---|---|---|
| coupon_settlement q95 | 2018: 1.00, 2019: 1.00, 2020: 1.34, 2021: 1.15, 2022: 1.11, 2023: 1.17, 2024: 1.27, 2025: 1.25 | 1.23 | 1.00 to 1.37 |
| dom_19_23 q05 | 2018: 1.00, 2019: 1.00, 2020: 1.09, 2021: 1.19, 2022: 1.32, 2023: 1.48, 2024: 1.42, 2025: 1.39 | 1.34 | 1.00 to 1.50 |
| dom_19_23 q95 | 2018: 1.00, 2019: 1.00, 2020: 0.88, 2021: 0.84, 2022: 0.73, 2023: 0.70, 2024: 0.65, 2025: 0.59 | 0.65 | 0.58 to 1.00 |
| no_flag q95 | 2018: 1.00, 2019: 0.85, 2020: 0.79, 2021: 0.84, 2022: 0.71, 2023: 0.75, 2024: 0.78, 2025: 0.78 | 0.82 | 0.69 to 1.00 |
| post_month_end_window q95 | 2018: 1.00, 2019: 1.00, 2020: 1.10, 2021: 1.12, 2022: 1.14, 2023: 1.25, 2024: 1.35, 2025: 1.32 | 1.32 | 0.97 to 1.36 |

## Reading

Pooled over the development window the arm's grid CRPS is +0.003 [-0.001, +0.007] against the candidate and its upper-tail twCRPS +0.003 [-0.000, +0.005] (positive favours the arm): by the declared rule the pooled reading is: undecided. By flag, grid CRPS against the candidate: coupon_settlement +0.001 [-0.014, +0.016]; dom_19_23 +0.005 [-0.016, +0.025]; no_flag +0.014 [+0.007, +0.022]; post_month_end_window -0.014 [-0.026, -0.002].

## Pooled, on scoring protocol v1's studentized stationary bootstrap

One score per decision day (the mean over h = 1 to 5), development window. d = reference score - arm score: positive favours the arm. Two-sided 90% intervals read from the studentized draws of `paired_tests` (mean block 10, 10000 draws, HAC lag 10, seed 1555). The candidate against each benchmark is on the same days and resamples.

### Grid CRPS (primary)

Mean over 1855 decision days: arm 1.598, candidate 1.601.

|  | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|
| arm | +0.003 [-0.001, +0.007] | +0.691 [+0.429, +1.614] | +0.253 [+0.164, +0.358] | +0.917 [+0.676, +1.227] |
| candidate (unchanged) | - | +0.688 [+0.426, +1.613] | +0.249 [+0.162, +0.353] | +0.913 [+0.671, +1.225] |

### Upper-tail twCRPS (key secondary)

Mean over 1855 decision days: arm 0.842, candidate 0.845.

|  | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|
| arm | +0.003 [-0.000, +0.005] | +0.533 [+0.271, +1.624] | +0.157 [+0.082, +0.267] | +0.291 [+0.168, +0.466] |
| candidate (unchanged) | - | +0.530 [+0.269, +1.626] | +0.154 [+0.080, +0.263] | +0.288 [+0.165, +0.464] |

**Pooled reading by the declared rule: undecided** (loses when the pooled grid-CRPS difference candidate - arm is not above 0, wins when its 90% interval lies wholly above 0). The rule is marked as a question in the pull request.

## Splits

Each row's cells, the share of them the arm changed, and the paired differences (reference - arm, positive favours the arm) with 90% intervals from the stationary bootstrap of the row's target days (mean block 10, 1000 resamples, seed 1555). Flag rows overlap.

### By regime

grid CRPS:

| regime | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| 2018-19 | 1795 | 0.45 | +0.011 [+0.003, +0.018] | +2.173 [+0.936, +3.896] | +0.420 [+0.153, +0.711] | +0.788 [+0.380, +1.229] |
| 2020 | 1255 | 0.66 | +0.003 [-0.005, +0.013] | +0.162 [-0.127, +0.433] | +0.128 [-0.182, +0.448] | +1.424 [+0.725, +2.303] |
| 2021-23 | 3740 | 0.66 | +0.004 [+0.001, +0.007] | +0.068 [+0.038, +0.101] | +0.034 [+0.001, +0.068] | +0.841 [+0.598, +1.116] |
| 2024 | 1250 | 0.66 | +0.005 [-0.004, +0.017] | +0.545 [+0.278, +0.833] | +0.308 [+0.108, +0.547] | +0.284 [+0.107, +0.483] |
| 2025-26 | 1235 | 0.66 | -0.010 [-0.034, +0.012] | +1.112 [+0.717, +1.515] | +0.743 [+0.473, +1.001] | +1.457 [+0.500, +2.616] |

upper-tail twCRPS:

| regime | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| 2018-19 | 1795 | 0.45 | +0.013 [+0.005, +0.020] | +2.099 [+0.864, +3.812] | +0.399 [+0.138, +0.699] | +0.578 [+0.238, +0.958] |
| 2020 | 1255 | 0.66 | +0.002 [-0.005, +0.009] | +0.164 [-0.032, +0.425] | +0.188 [-0.043, +0.492] | +0.745 [+0.423, +1.096] |
| 2021-23 | 3740 | 0.66 | +0.000 [-0.000, +0.001] | +0.002 [+0.000, +0.004] | +0.000 [-0.001, +0.002] | -0.004 [-0.009, -0.000] |
| 2024 | 1250 | 0.66 | +0.001 [-0.001, +0.002] | +0.112 [+0.006, +0.246] | +0.039 [-0.003, +0.096] | +0.017 [-0.007, +0.049] |
| 2025-26 | 1235 | 0.66 | -0.002 [-0.017, +0.012] | +0.665 [+0.249, +1.175] | +0.368 [+0.108, +0.695] | +0.581 [+0.085, +1.243] |

### By calendar flag of the target day

grid CRPS:

| calendar flag of the target day | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| all days | 9275 | 0.62 | +0.003 [-0.001, +0.007] | +0.691 [+0.409, +1.012] | +0.253 [+0.165, +0.352] | +0.917 [+0.689, +1.157] |
| coupon_settlement | 1019 | 0.90 | +0.001 [-0.014, +0.016] | +0.792 [+0.304, +1.366] | +0.691 [+0.266, +1.189] | +1.701 [+1.032, +2.474] |
| dom_19_23 | 1518 | 0.92 | +0.005 [-0.016, +0.025] | +0.988 [+0.248, +2.154] | +0.198 [-0.011, +0.455] | +0.793 [+0.372, +1.224] |
| in no arm group | 3118 | 0.00 | +0.000 [+0.000, +0.000] | +0.602 [+0.279, +0.996] | +0.256 [+0.082, +0.439] | +1.037 [+0.728, +1.386] |
| no_flag | 2530 | 0.96 | +0.014 [+0.007, +0.022] | +0.667 [+0.372, +1.018] | +0.223 [+0.133, +0.318] | +0.621 [+0.347, +0.901] |
| post_month_end_window | 1190 | 0.91 | -0.014 [-0.026, -0.002] | +0.528 [+0.221, +0.879] | +0.042 [-0.157, +0.226] | +0.772 [+0.272, +1.303] |
| quarter_end (reference, in no arm group) | 291 | 0.00 | +0.000 [+0.000, +0.000] | +1.221 [-0.079, +2.674] | +1.099 [-0.163, +2.486] | +1.850 [+0.907, +2.810] |

upper-tail twCRPS:

| calendar flag of the target day | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| all days | 9275 | 0.62 | +0.003 [-0.000, +0.005] | +0.533 [+0.257, +0.848] | +0.157 [+0.081, +0.243] | +0.291 [+0.170, +0.424] |
| coupon_settlement | 1019 | 0.90 | -0.001 [-0.014, +0.013] | +0.462 [+0.079, +0.909] | +0.474 [+0.115, +0.876] | +0.867 [+0.234, +1.598] |
| dom_19_23 | 1518 | 0.92 | +0.006 [-0.002, +0.013] | +0.906 [+0.172, +2.113] | +0.175 [+0.009, +0.382] | +0.055 [-0.109, +0.216] |
| in no arm group | 3118 | 0.00 | +0.000 [+0.000, +0.000] | +0.467 [+0.173, +0.846] | +0.171 [+0.049, +0.321] | +0.378 [+0.186, +0.580] |
| no_flag | 2530 | 0.96 | +0.015 [+0.008, +0.021] | +0.511 [+0.198, +0.878] | +0.119 [+0.047, +0.207] | +0.120 [+0.025, +0.212] |
| post_month_end_window | 1190 | 0.91 | -0.021 [-0.031, -0.011] | +0.342 [+0.051, +0.691] | -0.056 [-0.225, +0.093] | +0.290 [-0.014, +0.633] |
| quarter_end (reference, in no arm group) | 291 | 0.00 | +0.000 [+0.000, +0.000] | +0.837 [-0.108, +1.944] | +0.798 [-0.106, +1.862] | +1.039 [+0.113, +2.119] |

### By pressure-day type of the target

grid CRPS:

| pressure-day type of the target | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| ordinary | 7939 | 0.63 | +0.003 [-0.002, +0.008] | +0.670 [+0.383, +1.038] | +0.183 [+0.099, +0.275] | +0.730 [+0.525, +0.956] |
| quarter_end_turn | 220 | 0.00 | +0.000 [+0.000, +0.000] | +0.849 [-0.255, +1.911] | +0.721 [-0.344, +1.740] | +1.502 [+0.308, +2.656] |
| tax_date | 445 | 0.45 | +0.014 [-0.004, +0.034] | +0.427 [+0.077, +0.802] | +0.333 [+0.014, +0.673] | +2.669 [+1.606, +3.802] |
| turn | 600 | 0.88 | -0.001 [-0.016, +0.014] | +0.915 [+0.353, +1.511] | +0.704 [+0.305, +1.098] | +1.633 [+0.792, +2.598] |
| year_end | 71 | 0.00 | +0.000 [+0.000, +0.000] | +2.374 [+0.616, +4.492] | +2.270 [+0.553, +4.330] | +2.927 [+1.688, +4.286] |

upper-tail twCRPS:

| pressure-day type of the target | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| ordinary | 7939 | 0.63 | +0.003 [-0.001, +0.006] | +0.540 [+0.258, +0.912] | +0.103 [+0.029, +0.190] | +0.152 [+0.056, +0.264] |
| quarter_end_turn | 220 | 0.00 | +0.000 [+0.000, +0.000] | +0.537 [-0.190, +1.313] | +0.493 [-0.194, +1.230] | +0.670 [-0.125, +1.599] |
| tax_date | 445 | 0.45 | +0.012 [-0.004, +0.035] | +0.310 [+0.016, +0.640] | +0.294 [+0.014, +0.611] | +1.308 [+0.317, +2.446] |
| turn | 600 | 0.88 | -0.007 [-0.020, +0.006] | +0.451 [+0.028, +0.944] | +0.458 [+0.127, +0.834] | +1.006 [+0.223, +1.885] |
| year_end | 71 | 0.00 | +0.000 [+0.000, +0.000] | +1.768 [+0.255, +3.628] | +1.743 [+0.258, +3.562] | +2.180 [+0.628, +3.832] |

### By lead

grid CRPS:

| lead | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| 1 | 1855 | 0.62 | +0.004 [+0.001, +0.008] | +0.544 [+0.299, +0.864] | +0.177 [+0.081, +0.268] | +1.001 [+0.772, +1.250] |
| 2 | 1855 | 0.62 | +0.005 [+0.001, +0.009] | +0.653 [+0.369, +1.031] | +0.197 [+0.109, +0.286] | +0.940 [+0.715, +1.193] |
| 3 | 1855 | 0.62 | +0.003 [-0.001, +0.007] | +0.733 [+0.429, +1.130] | +0.260 [+0.154, +0.358] | +0.914 [+0.694, +1.161] |
| 4 | 1855 | 0.62 | +0.002 [-0.003, +0.007] | +0.760 [+0.439, +1.166] | +0.306 [+0.191, +0.417] | +0.882 [+0.671, +1.129] |
| 5 | 1855 | 0.62 | +0.003 [-0.002, +0.008] | +0.765 [+0.439, +1.176] | +0.324 [+0.212, +0.440] | +0.846 [+0.640, +1.093] |

upper-tail twCRPS:

| lead | cells | share changed | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|---|---|
| 1 | 1855 | 0.62 | +0.004 [+0.001, +0.006] | +0.461 [+0.219, +0.775] | +0.130 [+0.041, +0.217] | +0.289 [+0.155, +0.423] |
| 2 | 1855 | 0.62 | +0.003 [+0.001, +0.006] | +0.518 [+0.234, +0.891] | +0.126 [+0.047, +0.208] | +0.292 [+0.174, +0.423] |
| 3 | 1855 | 0.62 | +0.002 [-0.001, +0.005] | +0.561 [+0.262, +0.952] | +0.167 [+0.078, +0.257] | +0.299 [+0.184, +0.429] |
| 4 | 1855 | 0.62 | +0.002 [-0.002, +0.004] | +0.569 [+0.253, +0.981] | +0.187 [+0.090, +0.282] | +0.291 [+0.176, +0.419] |
| 5 | 1855 | 0.62 | +0.002 [-0.001, +0.005] | +0.555 [+0.241, +0.969] | +0.175 [+0.082, +0.270] | +0.284 [+0.174, +0.410] |

## Coverage of the 90% band, per tail and per flag, before and after

Strict share of cells below q05 and above q95 (nominal 0.05 each), the candidate and the arm, with 90% intervals as above.

| calendar flag | cells | below q05, candidate | below q05, arm | above q95, candidate | above q95, arm | band, candidate | band, arm |
|---|---|---|---|---|---|---|---|
| all days | 9275 | 0.067 [0.052, 0.084] | 0.064 [0.049, 0.080] | 0.058 [0.044, 0.072] | 0.062 [0.048, 0.076] | 0.875 | 0.874 |
| coupon_settlement | 1019 | 0.052 [0.027, 0.079] | 0.052 [0.027, 0.079] | 0.098 [0.057, 0.140] | 0.078 [0.042, 0.113] | 0.850 | 0.870 |
| dom_19_23 | 1518 | 0.092 [0.054, 0.131] | 0.072 [0.041, 0.107] | 0.008 [0.002, 0.016] | 0.030 [0.015, 0.048] | 0.901 | 0.898 |
| in no arm group | 3118 | 0.068 [0.049, 0.089] | 0.068 [0.049, 0.089] | 0.071 [0.051, 0.092] | 0.071 [0.051, 0.092] | 0.861 | 0.861 |
| no_flag | 2530 | 0.043 [0.028, 0.059] | 0.043 [0.028, 0.059] | 0.032 [0.021, 0.044] | 0.055 [0.037, 0.074] | 0.925 | 0.902 |
| post_month_end_window | 1190 | 0.101 [0.064, 0.140] | 0.101 [0.064, 0.140] | 0.108 [0.064, 0.155] | 0.082 [0.043, 0.125] | 0.792 | 0.818 |
| quarter_end (reference, in no arm group) | 291 | 0.089 [0.010, 0.176] | 0.089 [0.010, 0.176] | 0.309 [0.158, 0.460] | 0.309 [0.158, 0.460] | 0.601 | 0.601 |

| regime | cells | below q05, candidate | below q05, arm | above q95, candidate | above q95, arm | band, candidate | band, arm |
|---|---|---|---|---|---|---|---|
| 2018-19 | 1795 | 0.071 [0.044, 0.101] | 0.070 [0.043, 0.101] | 0.062 [0.037, 0.091] | 0.062 [0.037, 0.091] | 0.867 | 0.867 |
| 2020 | 1255 | 0.094 [0.046, 0.148] | 0.090 [0.045, 0.142] | 0.041 [0.009, 0.081] | 0.046 [0.013, 0.087] | 0.865 | 0.864 |
| 2021-23 | 3740 | 0.063 [0.037, 0.092] | 0.058 [0.033, 0.085] | 0.062 [0.040, 0.087] | 0.067 [0.044, 0.091] | 0.875 | 0.875 |
| 2024 | 1250 | 0.066 [0.036, 0.095] | 0.062 [0.034, 0.090] | 0.054 [0.030, 0.078] | 0.054 [0.030, 0.078] | 0.881 | 0.885 |
| 2025-26 | 1235 | 0.049 [0.027, 0.075] | 0.049 [0.027, 0.075] | 0.059 [0.029, 0.099] | 0.072 [0.040, 0.109] | 0.891 | 0.879 |

## The 2026 days (shown apart, decide nothing)

Pooled point values, arm against candidate (positive favours the arm): grid CRPS -0.004, upper-tail twCRPS +0.004; 549 of 825 cells changed.

| flag | cells | CRPS, candidate - arm | twCRPS, candidate - arm | below q05, candidate to arm | above q95, candidate to arm |
|---|---|---|---|---|---|
| all days | 825 | -0.004 | +0.004 | 0.078 to 0.076 | 0.030 to 0.034 |
| coupon_settlement | 109 | -0.001 | -0.015 | 0.046 to 0.046 | 0.028 to 0.028 |
| dom_19_23 | 135 | -0.001 | +0.045 | 0.111 to 0.104 | 0.000 to 0.015 |
| in no arm group | 276 | +0.000 | +0.000 | 0.076 to 0.076 | 0.025 to 0.025 |
| no_flag | 219 | +0.014 | +0.031 | 0.096 to 0.096 | 0.068 to 0.073 |
| post_month_end_window | 106 | -0.048 | -0.075 | 0.019 to 0.019 | 0.000 to 0.000 |
| quarter_end (reference, in no arm group) | 21 | too few | too few | too few | too few |

## What this does and does not show

- It is development evidence on days already seen. The flags and tails were chosen from the whole development window by #1547, so the arm is scored on the sample that selected it; the figures flatter it.
- The sizes are walk-forward and as-of, but shrinkage k = 500 cells and the 100-cell minimum, the geometric-mean overlap rule and the quarter-end exclusion are this study's choices, marked as questions in the pull request. No other value was run.
- S13 (partially pooled day-type shapes) is untested; this arm does not settle it. #1402's S2 was a symmetric, unshrunk scale for every pressure-day type; this arm is one tail at a time, by calendar flag, shrunk, and leaves the other flags unchanged. Q3 and the quarter-end studies (#1531, #1548) are different questions.
- No verdict: only prospective confirmation days give one. The 2026 days are shown apart and decide nothing.

## Reproduction

See the header of `scripts/calendar_flag_scale_arm_1555.py`; the test is `tests/test_calendar_flag_scale_arm_1555.py`. Seed 1555 throughout.

## Note of 12 November 2026 (#1592)

On `post_month_end_window` (business days 1 to 3, quarter-end days excluded) the arm is worse than the candidate: grid CRPS -0.014 [-0.026, -0.002] and upper-tail twCRPS -0.021 [-0.031, -0.011], the only two group intervals on this page wholly below zero. The share below q05 is 0.101 [0.064, 0.140] for the candidate and the same for the arm, and the 90% band holds 0.792 of outcomes, then 0.818. The arm scaled only q95 because #1547 read q05 as in line on its ratio alone; under her ruling of 12 November 2026 on #1592 that tail is not in line (its miss share excludes 0.05). Width repairs on these days (this arm and #1402's symmetric scale) have raised coverage and lost CRPS, so location or the timing of the spike within the three days is the open question; it is a later step. These figures are those of the tables above, unchanged.
