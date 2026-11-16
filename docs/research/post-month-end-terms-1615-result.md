# Day-specific location and scale terms for the post-month-end business days 1 to 3 (#1615)

**Development, not a verdict.** H5, a development arm on the frozen candidate's known limit (post-month-end band coverage). The arms do not change the frozen candidate (s3c-ann-net); they are in `not_arms` of the H5 registration manifest until Eleonora rules. No lockbox day, no re-score of a published record, nothing registered or published. Every figure is read from `docs/research/post-month-end-terms-1615/result.json`; the declaration is `metadata/post_month_end_terms_1615.json`, committed before any score. The forecasts are #1533's walk extension, regenerated bit-identical from the 1363 walk (no refit). The business-day cells reproduce #1547's `post_month_end_window` group (1335 cells).

**Prior work** (`docs/research/settled-questions.md`). S18 (#1275, failed) used a spike-sized carryover term that is non-zero only at lead 1 on business day 2, and names a business-day split of the misses as what would reopen it; #1611 and #1614 made that split. This arm differs from S18: no term reads the month-end spread (not public before business day 2), the terms are by calendar position alone and act at every lead, with a location shift and a scale per group. #1555's `post_month_end_window` q95 scale (one group, one tail) lost on this window.

## The arms

A target day is in one of six groups: business day 1, 2 or 3 of its month (`bday_of_month`) crossed with the kind of the month-end before it (quarter-end when the target falls in January, April, July or October). Each group has a shift in bp (the median of y - q50 on its earlier cells) and a lower and an upper factor (#1533's section 2b ratios on those cells), each shrunk by n / (n + 100) toward 0 or 1 and left at 0 or 1 under 50 usable cells, the same at every lead. A cell is a training cell only if its target day is strictly before the decision day. Three arms: `arm` (shift and factors, the primary), `location` (the shift alone) and `scale` (the factors alone). A quantile set is `q50 + shift + m (q_i - q50)`; the candidate's cap is not undone. Every other forecast is the candidate's, the same numbers (25944 arm cells outside the groups were checked equal). No term reads the month-end spread. The arms call no guarded fitter, so none is a producer for the provisional register.

The terms the walk gave (first decision day of each year, last day of the window, range):

| group, term | first decision day of each year | last day | range | training cells at the last day |
|---|---|---|---|---|
| bd1_other lower | 2018: 1.00, 2019: 1.00, 2020: 0.92, 2021: 0.84, 2022: 0.83, 2023: 0.80, 2024: 0.77, 2025: 0.78 | 0.80 | 0.73 to 1.00 | 300 |
| bd1_other shift | 2018: +0.00, 2019: +0.00, 2020: -0.36, 2021: -0.59, 2022: -0.38, 2023: -0.24, 2024: -0.15, 2025: -0.16 | -0.16 | -0.78 to 0.00 | 300 |
| bd1_other upper | 2018: 1.00, 2019: 1.00, 2020: 1.05, 2021: 0.89, 2022: 0.85, 2023: 1.19, 2024: 1.33, 2025: 1.36 | 1.33 | 0.83 to 1.38 | 300 |
| bd1_quarter lower | 2018: 1.00, 2019: 1.00, 2020: 1.00, 2021: 1.00, 2022: 0.94, 2023: 0.92, 2024: 0.93, 2025: 1.00 | 1.02 | 0.91 to 1.09 | 145 |
| bd1_quarter shift | 2018: +0.00, 2019: +0.00, 2020: +0.00, 2021: +0.00, 2022: -0.07, 2023: +0.01, 2024: +0.31, 2025: +0.45 | 0.58 | -0.08 to 0.58 | 145 |
| bd1_quarter upper | 2018: 1.00, 2019: 1.00, 2020: 1.00, 2021: 1.00, 2022: 1.94, 2023: 1.93, 2024: 1.95, 2025: 2.33 | 2.32 | 1.00 to 2.35 | 145 |
| bd2_other lower | 2018: 1.00, 2019: 1.00, 2020: 0.99, 2021: 1.15, 2022: 1.05, 2023: 1.02, 2024: 0.96, 2025: 0.97 | 0.96 | 0.93 to 1.19 | 300 |
| bd2_other shift | 2018: +0.00, 2019: +0.00, 2020: -0.93, 2021: -0.17, 2022: -0.15, 2023: -0.08, 2024: -0.05, 2025: -0.08 | -0.14 | -0.93 to 0.09 | 300 |
| bd2_other upper | 2018: 1.00, 2019: 1.00, 2020: 1.10, 2021: 1.11, 2022: 1.15, 2023: 1.22, 2024: 1.29, 2025: 1.30 | 1.28 | 1.00 to 1.32 | 300 |
| bd2_quarter lower | 2018: 1.00, 2019: 1.00, 2020: 1.00, 2021: 1.00, 2022: 1.01, 2023: 1.02, 2024: 0.99, 2025: 0.99 | 1.12 | 0.98 to 1.16 | 145 |
| bd2_quarter shift | 2018: +0.00, 2019: +0.00, 2020: +0.00, 2021: +0.00, 2022: +0.15, 2023: +0.25, 2024: +0.23, 2025: +0.50 | 0.65 | 0.00 to 0.65 | 145 |
| bd2_quarter upper | 2018: 1.00, 2019: 1.00, 2020: 1.00, 2021: 1.00, 2022: 1.21, 2023: 1.38, 2024: 1.37, 2025: 1.38 | 1.34 | 1.00 to 1.39 | 145 |
| bd3_other lower | 2018: 1.00, 2019: 1.00, 2020: 0.91, 2021: 1.06, 2022: 1.02, 2023: 0.96, 2024: 0.93, 2025: 1.04 | 1.14 | 0.91 to 1.14 | 300 |
| bd3_other shift | 2018: +0.00, 2019: +0.00, 2020: -1.09, 2021: -0.37, 2022: -0.15, 2023: -0.14, 2024: -0.16, 2025: -0.19 | -0.29 | -1.09 to 0.00 | 300 |
| bd3_other upper | 2018: 1.00, 2019: 1.00, 2020: 1.02, 2021: 1.17, 2022: 1.15, 2023: 1.21, 2024: 1.19, 2025: 1.20 | 1.00 | 0.97 to 1.49 | 300 |
| bd3_quarter lower | 2018: 1.00, 2019: 1.00, 2020: 1.00, 2021: 1.00, 2022: 0.91, 2023: 0.91, 2024: 1.09, 2025: 1.46 | 1.56 | 0.89 to 1.56 | 145 |
| bd3_quarter shift | 2018: +0.00, 2019: +0.00, 2020: +0.00, 2021: +0.00, 2022: -0.04, 2023: +0.08, 2024: +0.08, 2025: -0.06 | -0.05 | -0.08 to 0.12 | 145 |
| bd3_quarter upper | 2018: 1.00, 2019: 1.00, 2020: 1.00, 2021: 1.00, 2022: 1.53, 2023: 1.69, 2024: 1.82, 2025: 1.93 | 1.90 | 1.00 to 1.93 | 145 |

## Reading

On the post-month-end window (1335 development cells, 267 target days) the primary arm's grid CRPS is +0.036 [+0.005, +0.071] against the candidate and its upper-tail twCRPS +0.007 [-0.008, +0.023] (positive favours the arm; 90% interval from the stationary bootstrap of the target days). By the declared rule the window reading is: **wins**. The location arm alone: grid CRPS +0.014 [-0.007, +0.035], twCRPS +0.012 [+0.002, +0.024]. The scale arm alone: grid CRPS +0.022 [+0.002, +0.045], twCRPS -0.004 [-0.015, +0.005].

Pooled over all 1855 development decision days, on the protocol's studentized bootstrap, the primary arm's grid CRPS is +0.005 [+0.001, +0.011] against the candidate and its upper-tail twCRPS +0.001 [-0.001, +0.004]; the pooled reading is **wins**. The pooled figure is diluted by the days the arms leave alone (1035 of 9275 cells changed).

The rule (loses when the difference candidate - arm is not above 0, wins when its 90% interval lies wholly above 0) is marked as a question in the pull request.

**Where the grid-CRPS difference sits** (the primary arm against the candidate; rows whose 90% interval lies wholly above or wholly below 0, development window):

- By business day: interval above 0 for bd1; below 0 for none.
- By group: interval above 0 for bd1_quarter, bd2_quarter; below 0 for bd2_other.
- By regime: interval above 0 for 2024, 2025-26; below 0 for 2020.
- The 2026 days, shown apart and deciding nothing: grid CRPS -0.010, twCRPS -0.037 on 117 post-month-end cells.

## Pooled, on scoring protocol v1's studentized stationary bootstrap

One score per decision day (the mean over h = 1 to 5), development window. d = reference score - arm score: positive favours the arm. Two-sided 90% intervals from the studentized draws of `paired_tests` (mean block 10, 10000 draws, HAC lag 10, seed 1615).

### Grid CRPS (primary)

Mean over the decision days: B1 2.289, B1' 1.851, B2 2.514, arm 1.596, candidate 1.601, location 1.599, scale 1.598.

|  | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|
| arm | +0.005 [+0.001, +0.011] | +0.693 [+0.431, +1.601] | +0.255 [+0.164, +0.359] | +0.918 [+0.668, +1.231] |
| location | +0.002 [-0.001, +0.005] | - | - | - |
| scale | +0.003 [+0.001, +0.008] | - | - | - |
| candidate (unchanged) | - | +0.688 [+0.425, +1.601] | +0.249 [+0.160, +0.353] | +0.913 [+0.662, +1.226] |

### Upper-tail twCRPS (key secondary)

Mean over the decision days: B1 1.375, B1' 0.999, B2 1.133, arm 0.844, candidate 0.845, location 0.843, scale 0.845.

|  | vs candidate | vs B1 | vs B1' | vs B2 |
|---|---|---|---|---|
| arm | +0.001 [-0.001, +0.004] | +0.531 [+0.271, +1.619] | +0.155 [+0.082, +0.264] | +0.289 [+0.163, +0.463] |
| location | +0.002 [+0.000, +0.004] | - | - | - |
| scale | -0.001 [-0.002, +0.001] | - | - | - |
| candidate (unchanged) | - | +0.530 [+0.271, +1.622] | +0.154 [+0.080, +0.263] | +0.288 [+0.162, +0.461] |

## Splits

Each row's cells, the share of them the primary arm changed, and the paired differences (reference - arm, positive favours the arm) with 90% intervals from the stationary bootstrap of the row's target days (mean block 10, 1000 resamples, seed 1615). Rows are the post-month-end cells unless named. The three CRPS columns are against the candidate; the last two are the primary arm against B1' and B2.

### By the window, and all days

| the window | cells | share changed | CRPS arm vs candidate | CRPS location | CRPS scale | twCRPS arm vs candidate | twCRPS location | twCRPS scale | CRPS arm vs B1' | CRPS arm vs B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| all days | 9275 | 0.11 | +0.005 [+0.001, +0.010] | +0.002 [-0.001, +0.005] | +0.003 [+0.000, +0.006] | +0.001 [-0.001, +0.003] | +0.002 [+0.000, +0.003] | -0.001 [-0.002, +0.001] | +0.255 [+0.170, +0.352] | +0.918 [+0.694, +1.174] |
| post_month_end_window | 1335 | 0.78 | +0.036 [+0.005, +0.071] | +0.014 [-0.007, +0.035] | +0.022 [+0.002, +0.045] | +0.007 [-0.008, +0.023] | +0.012 [+0.002, +0.024] | -0.004 [-0.015, +0.005] | +0.167 [-0.067, +0.372] | +0.910 [+0.420, +1.419] |

### By business day

| business day | cells | share changed | CRPS arm vs candidate | CRPS location | CRPS scale | twCRPS arm vs candidate | twCRPS location | twCRPS scale | CRPS arm vs B1' | CRPS arm vs B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| bd1 | 445 | 0.78 | +0.081 [+0.018, +0.149] | +0.023 [-0.010, +0.056] | +0.057 [+0.003, +0.113] | +0.025 [+0.004, +0.050] | +0.013 [+0.001, +0.028] | +0.013 [-0.006, +0.037] | +0.526 [+0.181, +0.875] | +1.573 [+0.825, +2.398] |
| bd2 | 445 | 0.78 | +0.005 [-0.023, +0.030] | +0.005 [-0.019, +0.027] | +0.001 [-0.012, +0.015] | -0.007 [-0.024, +0.011] | +0.006 [-0.005, +0.018] | -0.012 [-0.025, -0.001] | +0.186 [-0.075, +0.433] | +1.008 [+0.417, +1.688] |
| bd3 | 445 | 0.78 | +0.022 [-0.017, +0.062] | +0.013 [-0.018, +0.040] | +0.007 [-0.013, +0.028] | +0.004 [-0.015, +0.024] | +0.017 [+0.002, +0.034] | -0.014 [-0.025, -0.004] | -0.210 [-0.485, +0.052] | +0.149 [-0.284, +0.613] |

### By business day and kind of month-end

| business day and kind of month-end | cells | share changed | CRPS arm vs candidate | CRPS location | CRPS scale | twCRPS arm vs candidate | twCRPS location | twCRPS scale | CRPS arm vs B1' | CRPS arm vs B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| bd1_other | 300 | 0.83 | -0.002 [-0.041, +0.043] | -0.000 [-0.050, +0.053] | -0.010 [-0.028, +0.008] | +0.010 [-0.009, +0.033] | +0.016 [-0.001, +0.038] | -0.007 [-0.017, +0.002] | +0.296 [+0.030, +0.545] | +1.441 [+0.448, +2.411] |
| bd1_quarter | 145 | 0.66 | +0.251 [+0.028, +0.495] | +0.073 [+0.001, +0.154] | +0.196 [+0.033, +0.373] | +0.056 [-0.004, +0.118] | +0.007 [-0.005, +0.020] | +0.054 [-0.003, +0.113] | +1.002 [+0.227, +1.838] | +1.847 [+1.020, +2.757] |
| bd2_other | 300 | 0.83 | -0.026 [-0.047, -0.006] | -0.010 [-0.033, +0.010] | -0.018 [-0.037, -0.001] | -0.005 [-0.026, +0.016] | +0.010 [-0.003, +0.026] | -0.016 [-0.034, -0.001] | +0.022 [-0.134, +0.169] | +0.801 [+0.412, +1.218] |
| bd2_quarter | 145 | 0.66 | +0.068 [+0.011, +0.130] | +0.035 [-0.004, +0.078] | +0.041 [+0.017, +0.067] | -0.009 [-0.027, +0.007] | -0.001 [-0.011, +0.008] | -0.006 [-0.014, +0.001] | +0.524 [-0.063, +1.140] | +1.436 [+0.341, +2.521] |
| bd3_other | 300 | 0.83 | +0.017 [-0.030, +0.058] | +0.023 [-0.022, +0.062] | -0.010 [-0.023, +0.005] | +0.022 [-0.004, +0.054] | +0.025 [+0.001, +0.053] | -0.003 [-0.017, +0.010] | -0.203 [-0.395, -0.000] | +0.195 [-0.164, +0.561] |
| bd3_quarter | 145 | 0.66 | +0.035 [-0.009, +0.085] | -0.009 [-0.014, -0.003] | +0.043 [-0.001, +0.092] | -0.033 [-0.066, -0.004] | +0.001 [-0.000, +0.003] | -0.034 [-0.069, -0.004] | -0.225 [-0.748, +0.261] | +0.053 [-0.679, +0.736] |

### By regime (post-month-end cells)

| regime | cells | share changed | CRPS arm vs candidate | CRPS location | CRPS scale | twCRPS arm vs candidate | twCRPS location | twCRPS scale | CRPS arm vs B1' | CRPS arm vs B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 255 | 0.12 | +0.030 [+0.000, +0.065] | +0.034 [+0.000, +0.074] | -0.005 [-0.012, +0.000] | +0.029 [+0.000, +0.064] | +0.033 [+0.000, +0.072] | -0.005 [-0.011, +0.000] | -0.058 [-1.028, +0.951] | +0.898 [-0.396, +2.257] |
| 2020 | 180 | 0.67 | -0.064 [-0.126, -0.005] | -0.063 [-0.130, +0.004] | -0.011 [-0.024, +0.000] | +0.006 [-0.023, +0.033] | +0.017 [-0.016, +0.046] | -0.014 [-0.020, -0.008] | +0.004 [-0.480, +0.458] | +1.889 [+0.941, +2.758] |
| 2021-23 | 540 | 0.97 | +0.008 [-0.007, +0.023] | -0.005 [-0.023, +0.014] | +0.012 [-0.007, +0.033] | +0.001 [-0.000, +0.004] | +0.002 [+0.000, +0.004] | -0.000 [-0.001, +0.000] | +0.118 [+0.013, +0.214] | +0.653 [+0.094, +1.237] |
| 2024 | 180 | 1.00 | +0.129 [+0.066, +0.200] | +0.062 [+0.045, +0.081] | +0.068 [+0.014, +0.128] | +0.026 [-0.020, +0.073] | +0.002 [-0.002, +0.007] | +0.024 [-0.017, +0.066] | +0.306 [+0.021, +0.619] | +0.685 [+0.340, +1.086] |
| 2025-26 | 180 | 1.00 | +0.134 [+0.021, +0.253] | +0.068 [+0.025, +0.111] | +0.076 [-0.006, +0.165] | -0.022 [-0.095, +0.044] | +0.019 [-0.008, +0.047] | -0.036 [-0.092, +0.015] | +0.657 [+0.327, +1.018] | +0.945 [-0.764, +2.989] |

### By lead (post-month-end cells)

| lead | cells | share changed | CRPS arm vs candidate | CRPS location | CRPS scale | twCRPS arm vs candidate | twCRPS location | twCRPS scale | CRPS arm vs B1' | CRPS arm vs B2 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 267 | 0.78 | +0.028 [-0.004, +0.063] | +0.003 [-0.020, +0.026] | +0.024 [+0.005, +0.045] | +0.005 [-0.012, +0.021] | +0.008 [-0.001, +0.019] | -0.002 [-0.013, +0.008] | +0.035 [-0.212, +0.257] | +0.898 [+0.401, +1.422] |
| 2 | 267 | 0.78 | +0.030 [-0.002, +0.066] | +0.010 [-0.014, +0.034] | +0.019 [+0.000, +0.041] | +0.007 [-0.008, +0.023] | +0.010 [+0.001, +0.022] | -0.003 [-0.012, +0.007] | -0.025 [-0.264, +0.176] | +0.891 [+0.399, +1.389] |
| 3 | 267 | 0.78 | +0.033 [+0.003, +0.066] | +0.014 [-0.007, +0.036] | +0.018 [-0.002, +0.040] | +0.006 [-0.010, +0.022] | +0.012 [+0.001, +0.024] | -0.006 [-0.016, +0.003] | +0.155 [-0.086, +0.374] | +0.992 [+0.499, +1.498] |
| 4 | 267 | 0.78 | +0.042 [+0.011, +0.080] | +0.020 [-0.001, +0.041] | +0.022 [-0.000, +0.048] | +0.009 [-0.008, +0.026] | +0.015 [+0.003, +0.028] | -0.005 [-0.016, +0.005] | +0.260 [-0.004, +0.505] | +0.914 [+0.430, +1.410] |
| 5 | 267 | 0.78 | +0.047 [+0.014, +0.085] | +0.021 [-0.002, +0.043] | +0.026 [+0.002, +0.052] | +0.010 [-0.006, +0.026] | +0.016 [+0.005, +0.030] | -0.006 [-0.017, +0.004] | +0.411 [+0.122, +0.715] | +0.856 [+0.386, +1.359] |

## Coverage of the 90% band, per tail, before and after

Strict share of cells below q05 and above q95 (nominal 0.05 each), the candidate and each arm, with 90% intervals as above.

| scope | cells | below q05, candidate | below q05, arm | below q05, location | below q05, scale | above q95, candidate | above q95, arm | above q95, location | above q95, scale |
|---|---|---|---|---|---|---|---|---|---|
| all days | 9275 | 0.067 [0.051, 0.083] | 0.066 [0.051, 0.082] | 0.066 [0.050, 0.081] | 0.067 [0.052, 0.083] | 0.058 [0.045, 0.071] | 0.053 [0.040, 0.065] | 0.058 [0.045, 0.072] | 0.053 [0.040, 0.065] |
| post_month_end_window | 1335 | 0.091 [0.057, 0.127] | 0.084 [0.052, 0.116] | 0.079 [0.050, 0.112] | 0.092 [0.058, 0.128] | 0.126 [0.085, 0.169] | 0.088 [0.054, 0.124] | 0.127 [0.083, 0.172] | 0.089 [0.055, 0.124] |

| business day | cells | below q05, candidate | below q05, arm | below q05, location | below q05, scale | above q95, candidate | above q95, arm | above q95, location | above q95, scale |
|---|---|---|---|---|---|---|---|---|---|
| bd1 | 445 | 0.043 [0.016, 0.072] | 0.047 [0.018, 0.076] | 0.034 [0.013, 0.056] | 0.054 [0.022, 0.088] | 0.166 [0.085, 0.245] | 0.128 [0.063, 0.196] | 0.164 [0.083, 0.245] | 0.124 [0.061, 0.189] |
| bd2 | 445 | 0.081 [0.036, 0.126] | 0.072 [0.031, 0.112] | 0.072 [0.034, 0.110] | 0.074 [0.034, 0.115] | 0.144 [0.088, 0.204] | 0.092 [0.049, 0.142] | 0.144 [0.088, 0.207] | 0.101 [0.058, 0.151] |
| bd3 | 445 | 0.151 [0.083, 0.220] | 0.133 [0.070, 0.196] | 0.133 [0.067, 0.200] | 0.148 [0.083, 0.216] | 0.067 [0.022, 0.117] | 0.045 [0.016, 0.076] | 0.072 [0.025, 0.124] | 0.043 [0.011, 0.074] |

| group | cells | below q05, candidate | below q05, arm | below q05, location | below q05, scale | above q95, candidate | above q95, arm | above q95, location | above q95, scale |
|---|---|---|---|---|---|---|---|---|---|
| bd1_other | 300 | 0.057 [0.023, 0.097] | 0.060 [0.023, 0.097] | 0.040 [0.017, 0.067] | 0.073 [0.030, 0.120] | 0.113 [0.047, 0.190] | 0.113 [0.043, 0.197] | 0.123 [0.050, 0.207] | 0.107 [0.040, 0.183] |
| bd1_quarter | 145 | 0.014 [0.000, 0.028] | 0.021 [0.000, 0.041] | 0.021 [0.000, 0.041] | 0.014 [0.000, 0.028] | 0.276 [0.138, 0.434] | 0.159 [0.069, 0.248] | 0.248 [0.124, 0.386] | 0.159 [0.069, 0.248] |
| bd2_other | 300 | 0.090 [0.033, 0.143] | 0.077 [0.030, 0.117] | 0.077 [0.033, 0.117] | 0.080 [0.030, 0.127] | 0.083 [0.043, 0.127] | 0.070 [0.037, 0.107] | 0.097 [0.050, 0.147] | 0.070 [0.037, 0.107] |
| bd2_quarter | 145 | 0.062 [0.028, 0.097] | 0.062 [0.028, 0.097] | 0.062 [0.028, 0.097] | 0.062 [0.028, 0.097] | 0.269 [0.179, 0.366] | 0.138 [0.076, 0.200] | 0.241 [0.159, 0.331] | 0.166 [0.097, 0.234] |
| bd3_other | 300 | 0.163 [0.080, 0.240] | 0.140 [0.063, 0.210] | 0.137 [0.060, 0.210] | 0.163 [0.080, 0.240] | 0.043 [0.000, 0.087] | 0.033 [0.000, 0.067] | 0.050 [0.003, 0.103] | 0.030 [0.000, 0.060] |
| bd3_quarter | 145 | 0.124 [0.028, 0.228] | 0.117 [0.034, 0.214] | 0.124 [0.028, 0.228] | 0.117 [0.028, 0.214] | 0.117 [0.034, 0.200] | 0.069 [0.034, 0.103] | 0.117 [0.034, 0.200] | 0.069 [0.034, 0.103] |

## The 2026 days (shown apart, decide nothing)

117 of 825 cells changed. Point values of d (positive favours the arm), grid CRPS and twCRPS of the primary arm against the candidate:

| scope | cells | CRPS, arm vs candidate | twCRPS, arm vs candidate |
|---|---|---|---|
| all days | 825 | -0.001 | -0.005 |
| post_month_end_window | 117 | -0.010 | -0.037 |
| bd1_other | 28 | too few | too few |
| bd1_quarter | 11 | too few | too few |
| bd2_other | 27 | too few | too few |
| bd2_quarter | 12 | too few | too few |
| bd3_other | 26 | too few | too few |
| bd3_quarter | 13 | too few | too few |

## What this does and does not show

- It is development evidence on days already seen. The business days and the kind of month-end were chosen by #1611 and #1614 from the same development window, so the arm is scored on the sample that selected it; the figures flatter it.
- The terms are walk-forward and as-of, but k = 100 cells, the 50-cell minimum and the six groups are this study's choices, marked as questions in the pull request. No other value was run.
- The cap is kept only where it bound on a cell (the walk file does not carry the line itself).
- It does not read the month-end spread, so it does not test S18's carryover again; it tests whether calendar position alone, with a shift and a scale per group, helps.
- No verdict: only prospective confirmation days give one. The 2026 days are shown apart and decide nothing.

## Reproduction

See the header of `scripts/post_month_end_terms_1615.py`; the test is `tests/test_post_month_end_terms_1615.py`. Seed 1615 throughout.

## Dated note, 16 November 2026 (#1630): the cap is not kept on the 2026 days

**The sentence "the candidate's cap is not undone" (in "The arms" above) is wrong.** The line under "What this does and does not show" ("the cap is kept only where it bound on a cell") states the limit correctly. `apply_terms` re-clips an arm only where the candidate's cap had bound on the cell (a final value that differs from its raw one). A cell at full allotment on which the cap did not bind keeps the arm's widened or shifted quantiles above the candidate's line. The text above is left as published; this note corrects it. Nothing in the development window is affected: it has 0 full-allotment cells in the post-month-end groups (50 elsewhere, where the arms are the candidate's own numbers), so its figures stand as published. Development evidence, not a verdict; the page stays in `not_arms`.

**Where the arm is above the line.** On the 2026 days, 29 of the 117 post-month-end cells (all 117 at full allotment) have an arm quantile above `s3c_candidate.cap_line`, on 10 of the 27 post-month-end target days, by up to 12.69 bp. The target days: 2026-02-02, 2026-02-03, 2026-04-01, 2026-04-02, 2026-04-06, 2026-07-01, 2026-07-02, 2026-07-06, 2026-09-01, 2026-09-02.

**The 2026 figures with the primary arm capped at the line,** beside the published ones (paired against the candidate, positive favours the arm; 90% interval from the stationary bootstrap of the target days, mean block 10, 1000 resamples, seed 1615, as the original splits). The published columns are the page's point values (it printed no interval for 2026); their intervals follow.

| scope (2026) | cells | grid CRPS, published | grid CRPS, capped at the line | twCRPS, published | twCRPS, capped at the line |
|---|---|---|---|---|---|
| post_month_end_window | 117 | -0.0096 | -0.0067 [-0.0536, +0.0458] | -0.0369 | -0.0341 [-0.0851, +0.0253] |
| all days | 825 | -0.0014 | -0.0010 [-0.0111, +0.0077] | -0.0052 | -0.0048 [-0.0162, +0.0049] |

Published, with intervals (the same bootstrap, uncapped): grid CRPS -0.0096 [-0.0575, +0.0442], twCRPS -0.0369 [-0.0886, +0.0239] on the window. The location and scale arms capped at the line: grid CRPS +0.0221 [+0.0050, +0.0409] and -0.0204 [-0.0724, +0.0376]; twCRPS +0.0176 [+0.0036, +0.0338] and -0.0461 [-0.0951, +0.0121].

| group (2026), capped at the line | cells | CRPS, arm vs candidate | twCRPS, arm vs candidate |
|---|---|---|---|
| bd1_other | 28 | too few | too few |
| bd1_quarter | 11 | too few | too few |
| bd2_other | 27 | too few | too few |
| bd2_quarter | 12 | too few | too few |
| bd3_other | 26 | too few | too few |
| bd3_quarter | 13 | too few | too few |

**The rule for future arms.** Any development arm built on the frozen candidate applies the candidate's own line at full allotment to its final quantiles, `repo_model.s3c_candidate.cap_arm_quantiles`, and not only where the cap had bound. This page's script applies it in `scripts/post_month_end_terms_1615.py cap-correction`; the arms' published figures are not re-scored in place. Figures: `docs/research/post-month-end-terms-1615/cap-correction.json`.

