# The misses after a month-end, by business day 1, 2 and 3 (#1611)

**Development, not a verdict.** H5, known limits of the frozen candidate (s3c-ann-net). No refit, no new arm, no change to the candidate or to the text of the known limit, no lockbox day, no record in `docs/runs/` edited, nothing registered. Implements her ruling of 14 November 2026 on #1605, option (a). Every figure is read from `docs/research/post-month-end-split-1611/result.json`; the script is `scripts/post_month_end_split_1611.py`, the test `tests/test_post_month_end_split_1611.py`. The forecasts are the walks of #1547 and #1555 (the 1363 walk, regenerated and checked against its sha256).

**Prior work** (`docs/research/settled-questions.md`, 14 November). #1275 (failed: its location term acts only at lead 1 on business day 2) and #1547 (a level shift: the median interval holds 0) cover location in aggregate; neither splits the misses by business day. No entry covers this split, so it is a new question.

**What is measured.** A target day is business day b when `derived_features.bday_of_month` is b, the count the candidate's `post_month_end_window` term reads. For each business day and lead: the cells whose outcome fell below the forecast q05 and above its q95 (the strict miss; nominal share 0.05), and the signed error y - q50 in bp, as a median and as a mean. Intervals are 90%, scoring protocol v1's studentized stationary bootstrap (10,000 draws, mean block 10, Newey-West lag 10, seed 1611) on the group's target days in date order; the share's interval is clipped to [0, 1]. A group with no miss has no standard error, so no studentized interval (shown as 'no interval'); a group under 20 target days has none either. The median error has no standard error to studentize by, so its interval is the percentile interval of the resampled medians. A pooled figure alone is not a result: the pooled row sits beside the five leads, and every regime is split below.

## Reading, by business day

Mechanical, from the pooled rows of the development window: whether the interval of each miss share excludes the nominal 0.05, and whether the interval of the median error excludes 0.

| scope | target | days | below q05 share | above q95 share | median error interval |
|---|---|---|---|---|---|
| All month-ends | business day 1 | 89 | holds 0.05 | above 0.05 | holds 0 |
| All month-ends | business day 2 | 89 | holds 0.05 | above 0.05 | holds 0 |
| All month-ends | business day 3 | 89 | above 0.05 | holds 0.05 | excludes 0 |
| After a quarter-end month-end | business day 1 | 29 | no interval | holds 0.05 | excludes 0 |
| After a quarter-end month-end | business day 2 | 29 | holds 0.05 | above 0.05 | excludes 0 |
| After a quarter-end month-end | business day 3 | 29 | holds 0.05 | holds 0.05 | holds 0 |
| After the other month-ends | business day 1 | 60 | holds 0.05 | holds 0.05 | holds 0 |
| After the other month-ends | business day 2 | 60 | holds 0.05 | above 0.05 | holds 0 |
| After the other month-ends | business day 3 | 60 | above 0.05 | holds 0.05 | excludes 0 |

## All month-ends

| target | lead | days | cells | below q05: misses (share) [90%] | above q95: misses (share) [90%] | median error, bp [90%] | mean error, bp [90%] |
|---|---|---|---|---|---|---|---|
| business day 1 | 1 | 89 | 89 | 2 (0.022) | 16 (0.180) [0.074, 0.289] | 0.10 [-0.25, 1.00] | 1.68 [0.29, 5.43] |
| business day 1 | 2 | 89 | 89 | 1 (0.011) | 14 (0.157) [0.067, 0.275] | -0.14 [-0.37, 0.64] | 1.17 [-0.06, 4.36] |
| business day 1 | 3 | 89 | 89 | 3 (0.034) [0.014, 0.066] | 13 (0.146) [0.063, 0.251] | 0.17 [-0.41, 0.67] | 1.01 [-0.27, 3.66] |
| business day 1 | 4 | 89 | 89 | 6 (0.067) [0.024, 0.135] | 16 (0.180) [0.060, 0.319] | -0.12 [-0.50, 0.77] | 1.14 [-0.36, 3.78] |
| business day 1 | 5 | 89 | 89 | 7 (0.079) [0.028, 0.162] | 15 (0.169) [0.066, 0.297] | -0.02 [-0.38, 1.07] | 1.13 [-0.57, 3.55] |
| business day 1 | pooled | 89 | 445 | 19 (0.043) [0.016, 0.087] | 74 (0.166) [0.065, 0.277] | 0.11 [-0.39, 0.88] | 1.23 [-0.16, 4.07] |
| business day 2 | 1 | 89 | 89 | 16 (0.180) [0.086, 0.292] | 10 (0.112) [0.055, 0.241] | -0.21 [-0.35, 0.07] | -0.57 [-1.45, 0.08] |
| business day 2 | 2 | 89 | 89 | 4 (0.045) [0.014, 0.118] | 14 (0.157) [0.098, 0.234] | 0.20 [-0.17, 0.58] | 0.61 [0.01, 1.44] |
| business day 2 | 3 | 89 | 89 | 4 (0.045) [0.014, 0.116] | 12 (0.135) [0.089, 0.199] | -0.07 [-0.25, 0.36] | 0.26 [-0.35, 0.96] |
| business day 2 | 4 | 89 | 89 | 5 (0.056) [0.017, 0.125] | 13 (0.146) [0.091, 0.220] | 0.04 [-0.23, 0.48] | 0.27 [-0.39, 0.91] |
| business day 2 | 5 | 89 | 89 | 7 (0.079) [0.022, 0.186] | 15 (0.169) [0.096, 0.279] | 0.02 [-0.25, 0.65] | 0.33 [-0.49, 1.00] |
| business day 2 | pooled | 89 | 445 | 36 (0.081) [0.037, 0.170] | 64 (0.144) [0.090, 0.216] | 0.11 [-0.20, 0.25] | 0.18 [-0.43, 0.75] |
| business day 3 | 1 | 89 | 89 | 18 (0.202) [0.104, 0.348] | 4 (0.045) [0.012, 0.120] | -0.30 [-1.07, -0.22] | -1.34 [-2.96, -0.24] |
| business day 3 | 2 | 89 | 89 | 19 (0.213) [0.090, 0.353] | 7 (0.079) [0.024, 0.189] | -0.45 [-1.71, -0.25] | -1.45 [-3.16, -0.24] |
| business day 3 | 3 | 89 | 89 | 10 (0.112) [0.043, 0.217] | 6 (0.067) [0.018, 0.186] | -0.21 [-0.59, -0.13] | -0.63 [-1.78, 0.19] |
| business day 3 | 4 | 89 | 89 | 10 (0.112) [0.043, 0.214] | 7 (0.079) [0.024, 0.189] | -0.17 [-0.53, -0.11] | -0.76 [-1.90, 0.05] |
| business day 3 | 5 | 89 | 89 | 10 (0.112) [0.051, 0.205] | 6 (0.067) [0.021, 0.159] | -0.18 [-0.50, -0.06] | -0.84 [-1.84, -0.10] |
| business day 3 | pooled | 89 | 445 | 67 (0.151) [0.071, 0.249] | 30 (0.067) [0.021, 0.153] | -0.29 [-0.87, -0.18] | -1.00 [-2.29, -0.09] |

## After a quarter-end month-end (target in January, April, July or October)

| target | lead | days | cells | below q05: misses (share) [90%] | above q95: misses (share) [90%] | median error, bp [90%] | mean error, bp [90%] |
|---|---|---|---|---|---|---|---|
| business day 1 | 1 | 29 | 29 | 0 (0.000) | 8 (0.276) [0.041, 0.492] | 0.98 [0.04, 2.19] | 4.12 [0.78, 17.89] |
| business day 1 | 2 | 29 | 29 | 0 (0.000) | 7 (0.241) [0.030, 0.395] | 0.95 [-0.14, 1.95] | 3.56 [0.36, 17.10] |
| business day 1 | 3 | 29 | 29 | 0 (0.000) | 6 (0.207) [0.000, 0.840] | 0.94 [0.53, 2.40] | 3.71 [0.45, 15.96] |
| business day 1 | 4 | 29 | 29 | 1 (0.034) | 10 (0.345) [0.003, 0.795] | 0.97 [-0.15, 2.33] | 4.09 [0.51, 14.65] |
| business day 1 | 5 | 29 | 29 | 1 (0.034) | 9 (0.310) [0.015, 0.650] | 1.38 [-0.07, 2.39] | 4.00 [0.25, 13.56] |
| business day 1 | pooled | 29 | 145 | 2 (0.014) | 40 (0.276) [0.011, 0.585] | 0.98 [0.28, 2.45] | 3.90 [0.50, 15.79] |
| business day 2 | 1 | 29 | 29 | 4 (0.138) [0.066, 0.248] | 5 (0.172) [0.070, 0.441] | 0.45 [-0.22, 0.54] | -0.23 [-1.20, 0.58] |
| business day 2 | 2 | 29 | 29 | 1 (0.034) | 9 (0.310) [0.164, 0.449] | 1.11 [0.39, 1.75] | 1.57 [0.46, 3.31] |
| business day 2 | 3 | 29 | 29 | 1 (0.034) | 7 (0.241) [0.173, 0.309] | 0.96 [0.05, 1.83] | 1.29 [0.30, 2.98] |
| business day 2 | 4 | 29 | 29 | 1 (0.034) | 8 (0.276) [0.069, 0.416] | 1.41 [0.36, 2.78] | 1.55 [0.44, 3.13] |
| business day 2 | 5 | 29 | 29 | 2 (0.069) [0.021, 0.109] | 10 (0.345) [0.063, 0.618] | 1.98 [0.49, 2.62] | 1.81 [0.31, 3.34] |
| business day 2 | pooled | 29 | 145 | 9 (0.062) [0.022, 0.178] | 39 (0.269) [0.129, 0.380] | 1.32 [0.23, 1.79] | 1.20 [0.24, 2.38] |
| business day 3 | 1 | 29 | 29 | 7 (0.241) [0.000, 0.918] | 2 (0.069) [0.033, 0.106] | -0.25 [-0.63, -0.02] | -2.08 [-4.90, -0.16] |
| business day 3 | 2 | 29 | 29 | 5 (0.172) [0.000, 0.397] | 4 (0.138) [0.051, 0.373] | -0.23 [-1.09, 0.30] | -1.54 [-3.47, 0.22] |
| business day 3 | 3 | 29 | 29 | 2 (0.069) | 4 (0.138) [0.051, 0.373] | 0.29 [-0.29, 0.60] | -0.29 [-1.39, 0.71] |
| business day 3 | 4 | 29 | 29 | 2 (0.069) | 4 (0.138) [0.051, 0.373] | 0.01 [-0.28, 0.28] | -0.34 [-1.34, 0.52] |
| business day 3 | 5 | 29 | 29 | 2 (0.069) [0.000, 0.122] | 3 (0.103) [0.045, 0.215] | 0.18 [0.03, 0.48] | -0.25 [-1.09, 0.60] |
| business day 3 | pooled | 29 | 145 | 18 (0.124) [0.000, 0.475] | 17 (0.117) [0.048, 0.268] | -0.07 [-0.57, 0.34] | -0.90 [-2.29, 0.33] |

## After the other month-ends

| target | lead | days | cells | below q05: misses (share) [90%] | above q95: misses (share) [90%] | median error, bp [90%] | mean error, bp [90%] |
|---|---|---|---|---|---|---|---|
| business day 1 | 1 | 60 | 60 | 2 (0.033) [0.003, 0.054] | 8 (0.133) [0.054, 0.243] | -0.07 [-0.38, 0.64] | 0.51 [-0.44, 1.26] |
| business day 1 | 2 | 60 | 60 | 1 (0.017) | 7 (0.117) [0.033, 0.260] | -0.26 [-0.47, 0.40] | 0.01 [-0.69, 0.64] |
| business day 1 | 3 | 60 | 60 | 3 (0.050) [0.023, 0.092] | 7 (0.117) [0.033, 0.260] | -0.24 [-0.99, 0.47] | -0.30 [-1.48, 0.55] |
| business day 1 | 4 | 60 | 60 | 5 (0.083) [0.034, 0.145] | 6 (0.100) [0.001, 0.267] | -0.22 [-1.40, 0.36] | -0.29 [-1.82, 0.64] |
| business day 1 | 5 | 60 | 60 | 6 (0.100) [0.038, 0.191] | 6 (0.100) [0.030, 0.205] | -0.20 [-1.48, 0.39] | -0.26 [-1.97, 0.82] |
| business day 1 | pooled | 60 | 300 | 17 (0.057) [0.023, 0.105] | 34 (0.113) [0.033, 0.262] | -0.25 [-0.80, 0.48] | -0.07 [-1.26, 0.74] |
| business day 2 | 1 | 60 | 60 | 12 (0.200) [0.054, 0.359] | 5 (0.083) [0.045, 0.141] | -0.26 [-0.98, -0.12] | -0.73 [-2.05, 0.01] |
| business day 2 | 2 | 60 | 60 | 3 (0.050) [0.015, 0.105] | 5 (0.083) [0.048, 0.131] | -0.02 [-0.22, 0.28] | 0.14 [-0.20, 0.45] |
| business day 2 | 3 | 60 | 60 | 3 (0.050) [0.016, 0.105] | 5 (0.083) [0.048, 0.131] | -0.18 [-0.75, 0.17] | -0.24 [-0.92, 0.20] |
| business day 2 | 4 | 60 | 60 | 4 (0.067) [0.016, 0.188] | 5 (0.083) [0.048, 0.131] | -0.24 [-0.58, 0.37] | -0.34 [-1.00, 0.14] |
| business day 2 | 5 | 60 | 60 | 5 (0.083) [0.025, 0.180] | 5 (0.083) [0.048, 0.131] | -0.18 [-0.62, 0.02] | -0.38 [-1.06, 0.17] |
| business day 2 | pooled | 60 | 300 | 27 (0.090) [0.032, 0.175] | 25 (0.083) [0.051, 0.128] | -0.17 [-0.54, 0.22] | -0.31 [-0.95, 0.14] |
| business day 3 | 1 | 60 | 60 | 11 (0.183) [0.101, 0.254] | 2 (0.033) | -0.60 [-1.19, -0.24] | -0.99 [-2.76, 0.14] |
| business day 3 | 2 | 60 | 60 | 14 (0.233) [0.057, 0.385] | 3 (0.050) [0.009, 0.115] | -0.65 [-2.55, -0.26] | -1.41 [-3.87, -0.02] |
| business day 3 | 3 | 60 | 60 | 8 (0.133) [0.029, 0.287] | 2 (0.033) [0.006, 0.054] | -0.24 [-1.21, -0.20] | -0.79 [-2.76, 0.17] |
| business day 3 | 4 | 60 | 60 | 8 (0.133) [0.033, 0.268] | 3 (0.050) [0.009, 0.115] | -0.37 [-1.31, -0.14] | -0.96 [-3.08, 0.04] |
| business day 3 | 5 | 60 | 60 | 8 (0.133) [0.033, 0.268] | 3 (0.050) [0.009, 0.115] | -0.40 [-1.51, -0.07] | -1.13 [-2.88, -0.18] |
| business day 3 | pooled | 60 | 300 | 49 (0.163) [0.055, 0.289] | 13 (0.043) [0.008, 0.108] | -0.65 [-1.33, -0.19] | -1.06 [-3.05, -0.00] |

## By regime (leads pooled)

All month-ends, one row per business day and regime; the lead rows beside are points (misses of cells at that lead). A regime with under 20 target days has no interval.

| target | regime | days | cells | below q05: misses (share) [90%] | above q95: misses (share) [90%] | median error, bp [90%] | low/up misses by lead |
|---|---|---|---|---|---|---|---|
| business day 1 | 2018-19 | 17 | 85 | 4 (0.047) | 11 (0.129) | 0.67 (no interval) | h1: 1/2 of 17; h2: 0/2 of 17; h3: 1/2 of 17; h4: 1/2 of 17; h5: 1/3 of 17 |
| business day 1 | 2020 | 12 | 60 | 4 (0.067) | 0 (0.000) | -1.16 (no interval) | h1: 0/0 of 12; h2: 0/0 of 12; h3: 0/0 of 12; h4: 2/0 of 12; h5: 2/0 of 12 |
| business day 1 | 2021-23 | 36 | 180 | 6 (0.033) | 34 (0.189) [0.034, 0.334] | 0.36 [-0.21, 0.69] | h1: 1/8 of 36; h2: 1/8 of 36; h3: 1/5 of 36; h4: 1/7 of 36; h5: 2/6 of 36 |
| business day 1 | 2024 | 12 | 60 | 3 (0.050) | 20 (0.333) | 1.71 (no interval) | h1: 0/3 of 12; h2: 0/3 of 12; h3: 1/4 of 12; h4: 1/5 of 12; h5: 1/5 of 12 |
| business day 1 | 2025-26 | 12 | 60 | 2 (0.033) | 9 (0.150) | 1.47 (no interval) | h1: 0/3 of 12; h2: 0/1 of 12; h3: 0/2 of 12; h4: 1/2 of 12; h5: 1/1 of 12 |
| business day 2 | 2018-19 | 17 | 85 | 12 (0.141) | 13 (0.153) | 0.11 (no interval) | h1: 6/1 of 17; h2: 1/3 of 17; h3: 1/3 of 17; h4: 2/3 of 17; h5: 2/3 of 17 |
| business day 2 | 2020 | 12 | 60 | 6 (0.100) | 5 (0.083) | 0.32 (no interval) | h1: 1/1 of 12; h2: 1/1 of 12; h3: 1/1 of 12; h4: 1/1 of 12; h5: 2/1 of 12 |
| business day 2 | 2021-23 | 36 | 180 | 3 (0.017) [0.000, 0.045] | 34 (0.189) [0.071, 0.323] | -0.03 [-0.21, 0.36] | h1: 3/7 of 36; h2: 0/8 of 36; h3: 0/6 of 36; h4: 0/6 of 36; h5: 0/7 of 36 |
| business day 2 | 2024 | 12 | 60 | 6 (0.100) | 8 (0.133) | 0.28 (no interval) | h1: 3/1 of 12; h2: 0/1 of 12; h3: 1/1 of 12; h4: 1/2 of 12; h5: 1/3 of 12 |
| business day 2 | 2025-26 | 12 | 60 | 9 (0.150) | 4 (0.067) | -1.37 (no interval) | h1: 3/0 of 12; h2: 2/1 of 12; h3: 1/1 of 12; h4: 1/1 of 12; h5: 2/1 of 12 |
| business day 3 | 2018-19 | 17 | 85 | 18 (0.212) | 5 (0.059) | -2.15 (no interval) | h1: 4/1 of 17; h2: 5/1 of 17; h3: 3/1 of 17; h4: 3/1 of 17; h5: 3/1 of 17 |
| business day 3 | 2020 | 12 | 60 | 5 (0.083) | 9 (0.150) | 0.11 (no interval) | h1: 1/2 of 12; h2: 1/2 of 12; h3: 1/1 of 12; h4: 1/2 of 12; h5: 1/2 of 12 |
| business day 3 | 2021-23 | 36 | 180 | 9 (0.050) [0.003, 0.232] | 16 (0.089) [0.000, 0.246] | -0.18 [-0.29, -0.14] | h1: 4/1 of 36; h2: 4/4 of 36; h3: 0/4 of 36; h4: 0/4 of 36; h5: 1/3 of 36 |
| business day 3 | 2024 | 12 | 60 | 18 (0.300) | 0 (0.000) | -1.30 (no interval) | h1: 6/0 of 12; h2: 5/0 of 12; h3: 2/0 of 12; h4: 3/0 of 12; h5: 2/0 of 12 |
| business day 3 | 2025-26 | 12 | 60 | 17 (0.283) | 0 (0.000) | -2.78 (no interval) | h1: 3/0 of 12; h2: 4/0 of 12; h3: 4/0 of 12; h4: 3/0 of 12; h5: 3/0 of 12 |

## The 2026 days (shown apart, decide nothing)

Points only: no interval, and no bootstrap is run on these days.

| target | lead | days | cells | below q05 | above q95 | median error, bp |
|---|---|---|---|---|---|---|
| business day 1 | 1 | 8 | 8 | 0 (0.000) | 1 (0.125) | 2.54 |
| business day 1 | 2 | 7 | 7 | 0 (0.000) | 0 (0.000) | 1.13 |
| business day 1 | 3 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.42 |
| business day 1 | 4 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.34 |
| business day 1 | 5 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.76 |
| business day 1 | pooled | 9 | 39 | 0 (0.000) | 1 (0.111) | 1.13 |
| business day 2 | 1 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.02 |
| business day 2 | 2 | 8 | 8 | 0 (0.000) | 0 (0.000) | 1.20 |
| business day 2 | 3 | 7 | 7 | 0 (0.000) | 0 (0.000) | 1.26 |
| business day 2 | 4 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.06 |
| business day 2 | 5 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.05 |
| business day 2 | pooled | 9 | 39 | 0 (0.000) | 0 (0.000) | -0.05 |
| business day 3 | 1 | 8 | 8 | 0 (0.000) | 0 (0.000) | -1.62 |
| business day 3 | 2 | 8 | 8 | 1 (0.125) | 0 (0.000) | -1.93 |
| business day 3 | 3 | 8 | 8 | 0 (0.000) | 0 (0.000) | -1.76 |
| business day 3 | 4 | 7 | 7 | 0 (0.000) | 0 (0.000) | -1.38 |
| business day 3 | 5 | 8 | 8 | 1 (0.125) | 0 (0.000) | -1.28 |
| business day 3 | pooled | 9 | 39 | 2 (0.059) | 0 (0.000) | -1.64 |

## Limits and what was not checked

- Development data on days already seen, never a verdict; the 2026 days decide nothing.
- The five leads of one target day are not independent, so the pooled and regime rows count a target day once in the resample and the cell counts are not the effective sample.
- Per business day and lead a group holds under one hundred target days, so under five expected misses at the 0.05 level in most cells: an interval that holds 0.05 is not evidence that the share is 0.05.
- The studentized bootstrap is the protocol's interval for a mean of paired daily differences; applied to a rare-event share and to a series of non-consecutive days it is this study's reading, not a calibrated one (the calibration of #656 did not cover it).
- The error is the outcome less the published (capped) forecast median; the shape ratios of #1547 are not recomputed here.
- No arm is fitted or scored. If a figure here pointed at a change to the candidate or its registration (#1511), that goes to Eleonora, not into code.

## Note of 15 November 2026 (#1613, #1614)

This page's miss-share intervals dropped every bootstrap resample that drew no miss, and reported an interval while at least 90% of the resamples were left; scoring protocol v1's scorer refuses such a resample instead. Its 2026 table also printed the mean of each day's own share beside the cell count (1 of 39 shows as 0.111). The page is re-issued with every resample kept, the 2026 share as misses over cells, and a second, exploratory interval beside each share, in `docs/research/post-month-end-corrected-1614-result.md`. The figures on this page are unchanged and stand as published; the pooled rows of its "Reading, by business day" table keep their readings, and the lower tail of business day 2 in 2021-23, shown here wholly below 0.05, reads [0.000, 1.000] there.
