# Width, shape or location by the target day's calendar flag, one tail at a time (#1547)

**Development, not a verdict.** H5, step 3 (avenue #1546, first of two steps). No candidate change, no lockbox day, no re-score of a published record, nothing registered. Every figure is read from `docs/research/calendar-tail-diagnostic-1547/result.json`; the declaration is `metadata/calendar_tail_diagnostic_1547.json`, committed before any figure. The forecasts are #1533's walk extension, regenerated bit-identical from the 1363 walk; the quarter-end group of #1533 is recomputed here and equals its section 2b to 1e-5.

## Reading

| group | cells | target days | reading | tails, one at a time |
|---|---|---|---|---|
| dom_19_23 | 1518 | 305 | shape | q01 too thin, q05 too thin, q95 too wide, q99 too wide |
| coupon_settlement | 1205 | 242 | shape | q01 in line, q05 in line, q95 too thin, q99 in line |
| post_month_end_window | 1335 | 267 | shape | q01 in line, q05 in line, q95 too thin, q99 too thin |
| quarter_end (flag, reference) | 146 | 30 | width | q05 too thin, q95 too thin |
| no calendar flag, no pressure type | 2530 | 507 | one tail off, not separable from width | q01 in line, q05 in line, q95 too wide, q99 too wide |
| quarter-end group of #1533 (reference) | 291 | 59 | shape; location | q05 too thin, q95 too thin |

The reading rule is this study's operational version of the words in `metadata/qe_diagnosis_1533.json` (a ratio 'common' to both sides is width; ratios that differ by side or level are shape; the median shift is location). A tail is 'too thin' when the 90% interval of its ratio lies wholly above 1 and 'too wide' when wholly below 1. The pull request marks the rule as a question.

## Ratios by tail

The ratio is the realised distance from the realised median over the forecast law's, on z = (y - q50)/(q95 - q05) of the raw quantiles (#1533 section 2b). Intervals: stationary bootstrap of the group's target days (mean block 10), whole events for the #1533 group; 90%, seed 1547. 'too few': under 500 cells, so under five expected misses at the 1% level.

| group | median z (shift) | q01 | q05 | q95 | q99 | q95 - q05 |
|---|---|---|---|---|---|---|
| dom_19_23 | 0.03 [-0.01, 0.06] | 1.51 [1.04, 1.71] | 1.45 [1.10, 1.95] | 0.53 [0.36, 0.67] | 0.40 [0.32, 0.52] | -0.92 [-1.43, -0.53] |
| coupon_settlement | 0.02 [-0.02, 0.11] | 1.06 [0.81, 1.29] | 1.02 [0.79, 1.30] | 1.67 [1.29, 2.20] | 1.43 [0.92, 1.84] | 0.65 [0.13, 1.25] |
| post_month_end_window | -0.04 [-0.06, 0.01] | 1.10 [0.92, 1.27] | 1.01 [0.82, 1.31] | 1.66 [1.31, 2.24] | 1.53 [1.05, 1.71] | 0.65 [0.18, 1.22] |
| quarter_end (flag, reference) | 0.20 [-0.12, 0.55] | too few | 2.28 [1.41, 3.04] | 3.05 [1.97, 3.65] | too few | 0.77 [-0.65, 2.00] |
| no calendar flag, no pressure type | 0.00 [-0.00, 0.00] | 1.25 [0.78, 1.62] | 0.99 [0.82, 1.13] | 0.79 [0.63, 0.94] | 0.66 [0.50, 0.79] | -0.20 [-0.39, 0.02] |
| quarter-end group of #1533 (reference) | 0.19 [0.01, 0.37] | too few | 1.74 [1.24, 2.28] | 3.14 [1.96, 3.46] | too few | 1.40 [0.19, 1.98] |

## Paired figures and misses

Candidate minus benchmark on the same cells (negative favours the candidate); B1' and B2 of the 1363 walk. Misses are the strict share below q05 and above q95 against the nominal 0.05.

| group | CRPS - B1' | CRPS - B2 | twCRPS - B1' | twCRPS - B2 | below q05 | above q95 |
|---|---|---|---|---|---|---|
| dom_19_23 | -0.193 [-0.469, 0.010] | -0.788 [-1.231, -0.370] | -0.169 [-0.392, 0.001] | -0.050 [-0.214, 0.117] | 0.092 [0.057, 0.136] | 0.008 [0.002, 0.016] |
| coupon_settlement | -0.791 [-1.354, -0.328] | -1.727 [-2.426, -1.138] | -0.542 [-1.025, -0.152] | -0.892 [-1.558, -0.325] | 0.064 [0.035, 0.099] | 0.134 [0.088, 0.181] |
| post_month_end_window | -0.131 [-0.334, 0.079] | -0.874 [-1.369, -0.375] | -0.023 [-0.197, 0.153] | -0.361 [-0.680, -0.069] | 0.091 [0.056, 0.128] | 0.126 [0.086, 0.175] |
| quarter_end (flag, reference) | -1.445 [-3.233, 0.249] | -2.103 [-3.138, -1.121] | -1.090 [-2.423, 0.136] | -1.299 [-2.528, -0.116] | 0.164 [0.021, 0.307] | 0.342 [0.193, 0.493] |
| no calendar flag, no pressure type | -0.208 [-0.316, -0.119] | -0.607 [-0.902, -0.336] | -0.105 [-0.195, -0.033] | -0.105 [-0.207, -0.012] | 0.043 [0.028, 0.060] | 0.032 [0.022, 0.044] |
| quarter-end group of #1533 (reference) | -1.099 [-2.208, 0.133] | -1.850 [-2.920, -0.949] | -0.798 [-1.863, 0.142] | -1.039 [-1.993, -0.287] | 0.089 [0.034, 0.151] | 0.309 [0.203, 0.420] |

## The splits

Point values; a split with fewer than 30 usable cells is 'too few'. Cells, median shift, ratio at q05 and at q95.

### By regime

| group | regime | cells | median z | q05 | q95 |
|---|---|---|---|---|---|
| dom_19_23 | 2018-19 | 288 | 0.06 | 1.24 | 0.67 |
| dom_19_23 | 2020 | 205 | -0.01 | 1.57 | 0.59 |
| dom_19_23 | 2021-23 | 625 | 0.04 | 1.77 | 0.30 |
| dom_19_23 | 2024 | 205 | 0.05 | 1.19 | 0.18 |
| dom_19_23 | 2025-26 | 195 | -0.01 | 0.67 | 0.72 |
| coupon_settlement | 2018-19 | 230 | 0.25 | 1.25 | 2.57 |
| coupon_settlement | 2020 | 170 | -0.12 | 1.58 | 1.02 |
| coupon_settlement | 2021-23 | 495 | -0.00 | 0.71 | 1.82 |
| coupon_settlement | 2024 | 160 | 0.09 | 0.85 | 1.37 |
| coupon_settlement | 2025-26 | 150 | 0.09 | 1.03 | 1.21 |
| post_month_end_window | 2018-19 | 255 | -0.05 | 1.11 | 1.71 |
| post_month_end_window | 2020 | 180 | -0.03 | 1.02 | 1.22 |
| post_month_end_window | 2021-23 | 540 | -0.03 | 0.61 | 1.88 |
| post_month_end_window | 2024 | 180 | -0.05 | 1.43 | 2.10 |
| post_month_end_window | 2025-26 | 180 | -0.05 | 1.66 | 1.22 |
| quarter_end (flag, reference) | 2018-19 | 30 | 0.74 | 3.62 | 2.03 |
| quarter_end (flag, reference) | 2020 | 20 | too few | too few | too few |
| quarter_end (flag, reference) | 2021-23 | 60 | 0.01 | 0.77 | 4.08 |
| quarter_end (flag, reference) | 2024 | 20 | too few | too few | too few |
| quarter_end (flag, reference) | 2025-26 | 16 | too few | too few | too few |
| no calendar flag, no pressure type | 2018-19 | 552 | -0.04 | 0.98 | 0.61 |
| no calendar flag, no pressure type | 2020 | 325 | 0.04 | 0.93 | 0.85 |
| no calendar flag, no pressure type | 2021-23 | 960 | 0.00 | 1.01 | 0.72 |
| no calendar flag, no pressure type | 2024 | 350 | 0.00 | 1.11 | 0.86 |
| no calendar flag, no pressure type | 2025-26 | 343 | -0.02 | 0.83 | 0.91 |
| quarter-end group of #1533 (reference) | 2018-19 | 55 | 0.56 | 2.92 | 2.65 |
| quarter-end group of #1533 (reference) | 2020 | 40 | -0.32 | 1.51 | 0.75 |
| quarter-end group of #1533 (reference) | 2021-23 | 120 | 0.06 | 0.79 | 2.41 |
| quarter-end group of #1533 (reference) | 2024 | 40 | 0.63 | 1.71 | 2.73 |
| quarter-end group of #1533 (reference) | 2025-26 | 36 | 0.40 | 1.33 | 1.44 |

### By pressure-day type of the target

| group | pressure-day type of the target | cells | median z | q05 | q95 |
|---|---|---|---|---|---|
| dom_19_23 | ordinary | 1438 | 0.03 | 1.44 | 0.48 |
| dom_19_23 | tax_date | 80 | 0.01 | 2.09 | 0.73 |
| coupon_settlement | ordinary | 484 | -0.00 | 0.75 | 1.24 |
| coupon_settlement | quarter_end_turn | 140 | 0.33 | 2.61 | 2.80 |
| coupon_settlement | tax_date | 145 | 0.06 | 0.89 | 1.17 |
| coupon_settlement | turn | 390 | 0.03 | 1.05 | 1.47 |
| coupon_settlement | year_end | 46 | 0.04 | 1.30 | 3.01 |
| post_month_end_window | ordinary | 890 | -0.04 | 1.28 | 1.45 |
| post_month_end_window | quarter_end_turn | 110 | 0.20 | 1.14 | 2.51 |
| post_month_end_window | turn | 300 | -0.05 | 0.73 | 1.45 |
| post_month_end_window | year_end | 35 | 0.06 | 0.53 | 3.88 |
| quarter_end (flag, reference) | quarter_end_turn | 110 | 0.33 | 2.66 | 2.85 |
| quarter_end (flag, reference) | year_end | 36 | -0.03 | 1.26 | 3.14 |
| no calendar flag, no pressure type | ordinary | 2530 | 0.00 | 0.99 | 0.79 |
| quarter-end group of #1533 (reference) | quarter_end_turn | 220 | 0.27 | 1.93 | 2.94 |
| quarter-end group of #1533 (reference) | year_end | 71 | 0.00 | 1.25 | 3.75 |

### By lead

| group | lead | cells | median z | q05 | q95 |
|---|---|---|---|---|---|
| dom_19_23 | 1 | 305 | 0.02 | 1.52 | 0.51 |
| dom_19_23 | 2 | 304 | 0.02 | 1.49 | 0.49 |
| dom_19_23 | 3 | 303 | 0.02 | 1.42 | 0.47 |
| dom_19_23 | 4 | 303 | 0.04 | 1.42 | 0.53 |
| dom_19_23 | 5 | 303 | 0.05 | 1.42 | 0.54 |
| coupon_settlement | 1 | 240 | 0.01 | 0.84 | 1.68 |
| coupon_settlement | 2 | 241 | 0.02 | 1.00 | 1.55 |
| coupon_settlement | 3 | 241 | 0.02 | 1.07 | 1.73 |
| coupon_settlement | 4 | 241 | 0.04 | 1.06 | 1.60 |
| coupon_settlement | 5 | 242 | 0.04 | 1.03 | 1.64 |
| post_month_end_window | 1 | 267 | -0.04 | 1.57 | 1.75 |
| post_month_end_window | 2 | 267 | -0.06 | 1.10 | 1.48 |
| post_month_end_window | 3 | 267 | -0.04 | 0.82 | 1.46 |
| post_month_end_window | 4 | 267 | -0.04 | 0.79 | 1.55 |
| post_month_end_window | 5 | 267 | -0.02 | 0.88 | 1.83 |
| quarter_end (flag, reference) | 1 | 29 | too few | too few | too few |
| quarter_end (flag, reference) | 2 | 29 | too few | too few | too few |
| quarter_end (flag, reference) | 3 | 29 | too few | too few | too few |
| quarter_end (flag, reference) | 4 | 29 | too few | too few | too few |
| quarter_end (flag, reference) | 5 | 30 | 0.23 | 2.61 | 2.59 |
| no calendar flag, no pressure type | 1 | 506 | 0.00 | 0.95 | 0.79 |
| no calendar flag, no pressure type | 2 | 506 | 0.00 | 0.93 | 0.74 |
| no calendar flag, no pressure type | 3 | 507 | 0.00 | 0.99 | 0.83 |
| no calendar flag, no pressure type | 4 | 506 | 0.00 | 1.10 | 0.74 |
| no calendar flag, no pressure type | 5 | 505 | 0.00 | 0.94 | 0.75 |
| quarter-end group of #1533 (reference) | 1 | 58 | 0.13 | 1.33 | 3.54 |
| quarter-end group of #1533 (reference) | 2 | 58 | 0.13 | 1.35 | 2.90 |
| quarter-end group of #1533 (reference) | 3 | 58 | 0.21 | 1.91 | 2.99 |
| quarter-end group of #1533 (reference) | 4 | 58 | 0.21 | 2.08 | 3.02 |
| quarter-end group of #1533 (reference) | 5 | 59 | 0.19 | 1.83 | 2.90 |

## The 2026 days (shown apart, decide nothing)

| group | cells | median z | q05 | q95 |
|---|---|---|---|---|
| dom_19_23 | 135 | 0.04 | 2.36 | 0.45 |
| coupon_settlement | 119 | 0.05 | 0.78 | 0.82 |
| post_month_end_window | 117 | -0.02 | 0.72 | 0.87 |
| quarter_end (flag, reference) | 10 | too few | too few | too few |
| no calendar flag, no pressure type | 219 | -0.12 | 1.05 | 1.41 |
| quarter-end group of #1533 (reference) | 21 | too few | too few | too few |

## Overlap of the flag groups

| group | target days | share of days with another listed flag | share of cells in the #1533 group |
|---|---|---|---|
| coupon_settlement | 242 | 0.24 | 0.15 |
| dom_19_23 | 305 | 0.01 | 0.00 |
| no calendar flag, no pressure type | 507 | 0.00 | 0.00 |
| post_month_end_window | 267 | 0.10 | 0.11 |
| quarter_end (flag, reference) | 30 | 1.00 | 1.00 |

## The per-tail arm the evidence supports

By the declared arm rule: a scale of one tail where that tail is off, or a shift where the location interval excludes 0, and in either case the point value on the same side in a majority of the regimes with at least 30 cells. No size is chosen here.

| group | supported | otherwise |
|---|---|---|
| dom_19_23 | scale q05 by flag (point 1.45; 2026 same side: True); scale q95 by flag (point 0.53; 2026 same side: True) | location interval holds 0 |
| coupon_settlement | scale q95 by flag (point 1.67; 2026 same side: False) | q05 in line (interval holds 1); location interval holds 0 |
| post_month_end_window | scale q95 by flag (point 1.66; 2026 same side: False) | q05 in line (interval holds 1); location interval holds 0 |
| quarter_end (flag, reference) | scale q95 by flag (point 3.05; 2026 same side: None) | q05 too thin but the regimes do not agree; location interval holds 0 |
| no calendar flag, no pressure type | scale q95 by flag (point 0.79; 2026 same side: False) | q05 in line (interval holds 1); location interval holds 0 |
| quarter-end group of #1533 (reference) | scale q05 by flag (point 1.74; 2026 same side: None); scale q95 by flag (point 3.14; 2026 same side: None); shift by flag (point 0.19; 2026 same side: None) |  |

## Limits and what was not checked

- Development data on seen days, never a verdict; the 2026 days decide nothing.
- The flag groups overlap, so a day in two groups counts in both; the table above gives the share. The groups are not exclusive arms.
- The ratio is descriptive and is inflated by any location shift the median removes imperfectly. Intervals from a few dozen target days are wide.
- #1523's hit counts are lead 1 against a regime-expected rate fitted in sample; this study pools five leads at the candidate's own nominal levels, so the two do not compare one to one.
- No arm is fitted or scored; the size of any scale or shift is the second step's, after review.

## Reproduction

See the header of `scripts/calendar_tail_diagnostic_1547.py`; the test is `tests/test_calendar_tail_diagnostic_1547.py`. Seed 1547 throughout, 1533 for the reproduction check.
