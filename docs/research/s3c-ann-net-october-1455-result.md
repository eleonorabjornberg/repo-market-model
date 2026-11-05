# (s3c-ann-net) with the 15 October tax-date label at the target day (#1455)

> **Development evidence, not a verdict** (scoring protocol v1: development data never gives one). H5 (primary goal), registration groundwork: the known-limits list. Her ruling of 4 November 2026 (option (a) on finding #1004): the label is tested as a development arm on (s3c-ann-net). Nothing is adopted, the frozen candidate does not change, and the label is a data meaning that stays hers. Made at 18:00 New York time. Declaration: [`metadata/s3c_ann_net_october_1455.json`](../../metadata/s3c_ann_net_october_1455.json), committed before any score.

## What was measured

The control is (s3c-ann-net) as #1288, #1319 and #1314 walk it, on the published panel. The arm, (s3c-ann-net+oct), is the same model on the same decision days and refit days with one change: the `tax_date` flag of its term table is the published flag OR-ed with the October window of #965 (15 October rolled forward off weekends and DC holidays, and the two market days after it), read at the target row on direct pairs. The panel, the turn-day labels behind the model's level and the day-type groups are the control's, so the arm tests the label as a fitted term only.

d is the reference's score less the arm's, so a positive d favours the arm. The interval is the studentized stationary-bootstrap interval of the protocol (`scoring_protocol.paired_tests`, 90%); *gain* is an interval wholly above zero, *cost* wholly below, *undecided* otherwise. The October tax windows are scored on their target days, which are not contiguous: days from different years join into blocks. The reading that can speak to the label leaves out 2019 and 2025, the years whose prints prompted it (#965).

## The development window (targets up to 2025-12-31; #1145, #1241)

1855 decision days, first scored 2018-07-19, last 2025-12-23; 89 refits of the control and 89 of the arm (the same days). The arm's forecast differs from the control's on 1799 scored decision days. October-window target days in this window: 24.

### grid CRPS, development

The October tax windows

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| October-window targets of 2019 and 2025 (the days that prompted the label) | 6 | 6.417 | 5.716 | 10.842 | too small (6 days, minimum 20) |
| October-window targets, not 2019 or 2025 | 18 | 0.715 | 0.831 | 0.960 | too small (18 days, minimum 20) |
| all October-window targets | 24 | 2.140 | 2.052 | 3.431 | +0.088 [-0.090, +0.934] **undecided** |

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 1.601 | 1.598 | 1.843 | +0.003 [+0.000, +0.013] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 1855 | 1.478 | 1.475 | 1.630 | +0.003 [-0.001, +0.012] **undecided** |
| h=2 | 1855 | 1.567 | 1.562 | 1.751 | +0.004 [+0.001, +0.013] **gain** |
| h=3 | 1855 | 1.607 | 1.603 | 1.860 | +0.004 [+0.001, +0.013] **gain** |
| h=4 | 1855 | 1.650 | 1.647 | 1.950 | +0.003 [+0.000, +0.011] **gain** |
| h=5 | 1855 | 1.704 | 1.701 | 2.025 | +0.003 [-0.000, +0.010] **undecided** |

By regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| 2018-19 | 361 | 3.642 | 3.627 | 4.031 | +0.016 [+0.001, +0.195] **gain** |
| 2020 | 251 | 1.490 | 1.490 | 1.641 | -0.000 [-0.015, +0.006] **undecided** |
| 2021-23 | 748 | 0.634 | 0.633 | 0.671 | +0.001 [-0.002, +0.002] **undecided** |
| 2024 | 250 | 1.074 | 1.074 | 1.359 | +0.000 [-0.001, +0.001] **undecided** |
| 2025-26 | 249 | 2.229 | 2.229 | 2.933 | +0.000 [-0.002, +0.003] **undecided** |

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 1591 | 1.287 | 1.285 | 1.464 | +0.002 [-0.001, +0.014] **undecided** |
| quarter_end_turn | 44 | 3.512 | 3.506 | 4.185 | +0.006 [+0.000, +0.034] **gain** |
| tax_date | 89 | 5.083 | 5.061 | 5.386 | +0.021 [+0.005, +0.078] **gain** |
| turn | 120 | 1.687 | 1.682 | 2.356 | +0.004 [-0.002, +0.031] **undecided** |
| year_end | 15 | 8.658 | 8.646 | 10.903 | too small (15 days, minimum 20) |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 1352 | 1.790 | 1.787 | 2.046 | +0.003 [+0.000, +0.008] **gain** |
| dom_19_23 | 305 | 1.139 | 1.138 | 1.327 | +0.000 [-0.003, +0.004] **undecided** |
| fomc_day | 118 | 4.450 | 4.438 | 4.412 | +0.012 [+0.003, +0.078] **gain** |
| iorb_window | 78 | 2.150 | 2.151 | 1.902 | -0.001 [-0.005, +0.004] **undecided** |
| month_end | 180 | 2.281 | 2.277 | 2.894 | +0.003 [-0.001, +0.011] **undecided** |
| ordinary | 507 | 1.116 | 1.111 | 1.326 | +0.005 [-0.001, +0.068] **undecided** |
| post_month_end_window | 267 | 2.032 | 2.030 | 2.146 | +0.002 [+0.001, +0.007] **gain** |
| quarter_end | 30 | 5.336 | 5.320 | 6.752 | +0.015 [-0.001, +0.129] **undecided** |
| settlement | 946 | 1.939 | 1.936 | 2.264 | +0.003 [-0.001, +0.009] **undecided** |
| tax_date | 89 | 5.083 | 5.061 | 5.386 | +0.021 [+0.005, +0.078] **gain** |

Each against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 1.601 | 1.598 | 1.843 | +0.245 [+0.160, +0.345] **gain** |
| 2018-19 | 361 | 3.642 | 3.627 | 4.031 | +0.404 [+0.151, +0.711] **gain** |
| 2020 | 251 | 1.490 | 1.490 | 1.641 | +0.151 [-0.142, +0.477] **undecided** |
| 2021-23 | 748 | 0.634 | 0.633 | 0.671 | +0.038 [-0.001, +0.075] **undecided** |
| 2024 | 250 | 1.074 | 1.074 | 1.359 | +0.285 [+0.118, +0.704] **gain** |
| 2025-26 | 249 | 2.229 | 2.229 | 2.933 | +0.704 [+0.446, +1.019] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 1855 | 1.601 | 1.598 | 1.843 | +0.242 [+0.157, +0.341] **gain** |
| 2018-19 | 361 | 3.642 | 3.627 | 4.031 | +0.388 [+0.138, +0.688] **gain** |
| 2020 | 251 | 1.490 | 1.490 | 1.641 | +0.151 [-0.145, +0.473] **undecided** |
| 2021-23 | 748 | 0.634 | 0.633 | 0.671 | +0.037 [-0.002, +0.074] **undecided** |
| 2024 | 250 | 1.074 | 1.074 | 1.359 | +0.285 [+0.118, +0.704] **gain** |
| 2025-26 | 249 | 2.229 | 2.229 | 2.933 | +0.704 [+0.446, +1.018] **gain** |

### upper-tail twCRPS, development

The October tax windows

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| October-window targets of 2019 and 2025 (the days that prompted the label) | 6 | 6.186 | 5.515 | 10.468 | too small (6 days, minimum 20) |
| October-window targets, not 2019 or 2025 | 18 | 0.113 | 0.193 | 0.076 | too small (18 days, minimum 20) |
| all October-window targets | 24 | 1.631 | 1.524 | 2.674 | +0.107 [-0.038, +2.634] **undecided** |

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.845 | 0.842 | 0.991 | +0.003 [-0.000, +0.011] **undecided** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 1855 | 0.826 | 0.824 | 0.930 | +0.002 [-0.001, +0.013] **undecided** |
| h=2 | 1855 | 0.838 | 0.835 | 0.955 | +0.004 [+0.000, +0.013] **gain** |
| h=3 | 1855 | 0.839 | 0.835 | 0.999 | +0.004 [+0.001, +0.013] **gain** |
| h=4 | 1855 | 0.851 | 0.848 | 1.030 | +0.002 [-0.000, +0.009] **undecided** |
| h=5 | 1855 | 0.869 | 0.867 | 1.040 | +0.002 [-0.000, +0.009] **undecided** |

By regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| 2018-19 | 361 | 3.205 | 3.191 | 3.559 | +0.015 [+0.001, +0.184] **gain** |
| 2020 | 251 | 0.578 | 0.579 | 0.772 | -0.001 [-0.030, +0.006] **undecided** |
| 2021-23 | 748 | 0.007 | 0.007 | 0.008 | +0.000 [+0.000, +0.001] **gain** |
| 2024 | 250 | 0.169 | 0.169 | 0.207 | +0.000 [+0.000, +0.000] **gain** |
| 2025-26 | 249 | 0.926 | 0.926 | 1.281 | +0.001 [-0.001, +0.003] **undecided** |

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 1591 | 0.540 | 0.537 | 0.634 | +0.002 [-0.001, +0.022] **undecided** |
| quarter_end_turn | 44 | 2.136 | 2.132 | 2.606 | +0.004 [-0.000, +0.069] **undecided** |
| tax_date | 89 | 4.365 | 4.353 | 4.626 | +0.012 [-0.000, +0.079] **undecided** |
| turn | 120 | 0.997 | 0.996 | 1.440 | +0.001 [-0.002, +0.008] **undecided** |
| year_end | 15 | 7.997 | 7.988 | 9.751 | too small (15 days, minimum 20) |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 1352 | 1.014 | 1.012 | 1.179 | +0.002 [-0.000, +0.006] **undecided** |
| dom_19_23 | 305 | 0.411 | 0.411 | 0.574 | +0.000 [-0.001, +0.002] **undecided** |
| fomc_day | 118 | 3.609 | 3.601 | 3.588 | +0.008 [+0.002, +0.036] **gain** |
| iorb_window | 78 | 1.405 | 1.406 | 1.167 | -0.001 [-0.009, +0.000] **undecided** |
| month_end | 180 | 1.451 | 1.449 | 1.835 | +0.002 [-0.001, +0.009] **undecided** |
| ordinary | 507 | 0.412 | 0.407 | 0.515 | +0.005 [-0.001, +0.094] **undecided** |
| post_month_end_window | 267 | 1.109 | 1.108 | 1.121 | +0.001 [+0.000, +0.001] **gain** |
| quarter_end | 30 | 4.178 | 4.167 | 5.270 | +0.011 [-0.001, +0.107] **undecided** |
| settlement | 946 | 1.179 | 1.176 | 1.387 | +0.003 [-0.000, +0.009] **undecided** |
| tax_date | 89 | 4.365 | 4.353 | 4.626 | +0.012 [-0.000, +0.079] **undecided** |

Each against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.845 | 0.842 | 0.991 | +0.149 [+0.077, +0.256] **gain** |
| 2018-19 | 361 | 3.205 | 3.191 | 3.559 | +0.368 [+0.105, +0.704] **gain** |
| 2020 | 251 | 0.578 | 0.579 | 0.772 | +0.193 [-0.011, +1.186] **undecided** |
| 2021-23 | 748 | 0.007 | 0.007 | 0.008 | +0.001 [-0.001, +0.002] **undecided** |
| 2024 | 250 | 0.169 | 0.169 | 0.207 | +0.037 [-0.002, +0.519] **undecided** |
| 2025-26 | 249 | 0.926 | 0.926 | 1.281 | +0.355 [+0.099, +0.945] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.845 | 0.842 | 0.991 | +0.146 [+0.075, +0.252] **gain** |
| 2018-19 | 361 | 3.205 | 3.191 | 3.559 | +0.354 [+0.096, +0.679] **gain** |
| 2020 | 251 | 0.578 | 0.579 | 0.772 | +0.194 [-0.009, +1.210] **undecided** |
| 2021-23 | 748 | 0.007 | 0.007 | 0.008 | +0.001 [-0.001, +0.002] **undecided** |
| 2024 | 250 | 0.169 | 0.169 | 0.207 | +0.037 [-0.002, +0.518] **undecided** |
| 2025-26 | 249 | 0.926 | 0.926 | 1.281 | +0.355 [+0.100, +0.939] **gain** |

### Brier P(> +5 bp), development

The October tax windows

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| October-window targets of 2019 and 2025 (the days that prompted the label) | 6 | 0.311 | 0.267 | 0.512 | too small (6 days, minimum 20) |
| October-window targets, not 2019 or 2025 | 18 | 0.003 | 0.004 | 0.001 | too small (18 days, minimum 20) |
| all October-window targets | 24 | 0.080 | 0.070 | 0.129 | +0.009 [-0.003, +0.182] **undecided** |

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.046 | 0.046 | 0.054 | +0.000 [+0.000, +0.001] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 1855 | 0.042 | 0.042 | 0.048 | +0.000 [-0.000, +0.001] **undecided** |
| h=2 | 1855 | 0.044 | 0.044 | 0.051 | +0.000 [+0.000, +0.001] **gain** |
| h=3 | 1855 | 0.047 | 0.047 | 0.056 | +0.000 [+0.000, +0.001] **gain** |
| h=4 | 1855 | 0.048 | 0.048 | 0.058 | +0.000 [+0.000, +0.001] **gain** |
| h=5 | 1855 | 0.049 | 0.049 | 0.058 | +0.000 [+0.000, +0.001] **gain** |

By regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| 2018-19 | 361 | 0.165 | 0.163 | 0.181 | +0.001 [+0.000, +0.006] **gain** |
| 2020 | 251 | 0.023 | 0.023 | 0.032 | -0.000 [-0.001, +0.000] **undecided** |
| 2021-23 | 748 | 0.000 | 0.000 | 0.000 | +0.000 [+0.000, +0.000] **gain** |
| 2024 | 250 | 0.017 | 0.017 | 0.019 | +0.000 [-0.000, +0.000] **undecided** |
| 2025-26 | 249 | 0.066 | 0.066 | 0.096 | -0.000 [-0.002, +0.000] **undecided** |

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 1591 | 0.045 | 0.045 | 0.049 | +0.000 [+0.000, +0.001] **gain** |
| quarter_end_turn | 44 | 0.096 | 0.096 | 0.120 | +0.000 [-0.000, +0.004] **undecided** |
| tax_date | 89 | 0.054 | 0.053 | 0.075 | +0.000 [-0.002, +0.007] **undecided** |
| turn | 120 | 0.039 | 0.039 | 0.075 | -0.000 [-0.000, +0.000] **undecided** |
| year_end | 15 | 0.051 | 0.050 | 0.171 | too small (15 days, minimum 20) |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 1352 | 0.049 | 0.049 | 0.060 | +0.000 [-0.000, +0.001] **undecided** |
| dom_19_23 | 305 | 0.034 | 0.034 | 0.046 | +0.000 [-0.000, +0.000] **undecided** |
| fomc_day | 118 | 0.053 | 0.052 | 0.045 | +0.001 [+0.000, +0.005] **gain** |
| iorb_window | 78 | 0.066 | 0.066 | 0.058 | +0.000 [-0.000, +0.004] **undecided** |
| month_end | 180 | 0.055 | 0.055 | 0.084 | +0.000 [-0.000, +0.000] **undecided** |
| ordinary | 507 | 0.038 | 0.038 | 0.041 | +0.000 [+0.000, +0.005] **gain** |
| post_month_end_window | 267 | 0.065 | 0.065 | 0.064 | +0.000 [-0.000, +0.000] **undecided** |
| quarter_end | 30 | 0.103 | 0.102 | 0.161 | +0.001 [-0.000, +0.014] **undecided** |
| settlement | 946 | 0.049 | 0.049 | 0.065 | +0.000 [-0.000, +0.001] **undecided** |
| tax_date | 89 | 0.054 | 0.053 | 0.075 | +0.000 [-0.002, +0.007] **undecided** |

Each against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.046 | 0.046 | 0.054 | +0.008 [+0.001, +0.016] **gain** |
| 2018-19 | 361 | 0.165 | 0.163 | 0.181 | +0.017 [-0.016, +0.047] **undecided** |
| 2020 | 251 | 0.023 | 0.023 | 0.032 | +0.009 [-0.001, +0.029] **undecided** |
| 2021-23 | 748 | 0.000 | 0.000 | 0.000 | +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 250 | 0.017 | 0.017 | 0.019 | +0.002 [-0.001, +0.219] **undecided** |
| 2025-26 | 249 | 0.066 | 0.066 | 0.096 | +0.030 [+0.005, +0.085] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.046 | 0.046 | 0.054 | +0.008 [+0.001, +0.016] **gain** |
| 2018-19 | 361 | 0.165 | 0.163 | 0.181 | +0.016 [-0.018, +0.046] **undecided** |
| 2020 | 251 | 0.023 | 0.023 | 0.032 | +0.009 [-0.001, +0.030] **undecided** |
| 2021-23 | 748 | 0.000 | 0.000 | 0.000 | +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 250 | 0.017 | 0.017 | 0.019 | +0.002 [-0.001, +0.219] **undecided** |
| 2025-26 | 249 | 0.066 | 0.066 | 0.096 | +0.030 [+0.005, +0.086] **gain** |

### The `tax_date` term at the last refit (2025-12-15)

| lead | control: effect (flagged pairs) | arm: effect (flagged pairs) |
|---|---|---|
| 1 | -0.155 (22) | +0.124 (28) |
| 2 | +0.050 (22) | +0.371 (28) |
| 3 | -0.124 (22) | +0.202 (28) |
| 4 | -0.233 (22) | +0.115 (28) |
| 5 | -0.243 (22) | +0.124 (28) |

## The 2026 development days (targets 2026-01-02 to 2026-09-03; #1229, #1252)

165 decision days, first scored 2025-12-31, last 2026-08-27; 97 refits of the control and 97 of the arm (the same days). The arm's forecast differs from the control's on 165 scored decision days. October-window target days in this window: 0.

### grid CRPS, 2026

The October tax windows

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| October-window targets of 2019 and 2025 (the days that prompted the label) | 0 | | | | no days |
| October-window targets, not 2019 or 2025 | 0 | | | | no days |
| all October-window targets | 0 | | | | no days |

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 1.669 | 1.660 | 1.865 | +0.008 [+0.003, +0.018] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 165 | 1.480 | 1.477 | 1.619 | +0.003 [+0.000, +0.007] **gain** |
| h=2 | 165 | 1.651 | 1.645 | 1.856 | +0.005 [+0.001, +0.012] **gain** |
| h=3 | 165 | 1.715 | 1.704 | 1.945 | +0.010 [+0.004, +0.021] **gain** |
| h=4 | 165 | 1.728 | 1.718 | 1.935 | +0.010 [+0.003, +0.027] **gain** |
| h=5 | 165 | 1.769 | 1.757 | 1.967 | +0.012 [+0.004, +0.026] **gain** |

By regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 146 | 1.712 | 1.709 | 1.809 | +0.003 [-0.001, +0.008] **undecided** |
| quarter_end_turn | 4 | 0.909 | 0.902 | 2.125 | too small (4 days, minimum 20) |
| tax_date | 6 | 1.764 | 1.614 | 3.226 | too small (6 days, minimum 20) |
| turn | 12 | 1.227 | 1.230 | 1.693 | too small (12 days, minimum 20) |
| year_end | 1 | 3.057 | 3.070 | 2.252 | too small (1 days, minimum 20) |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 125 | 1.594 | 1.586 | 1.855 | +0.008 [+0.002, +0.026] **gain** |
| dom_19_23 | 27 | 1.807 | 1.803 | 1.789 | +0.005 [+0.001, +0.022] **gain** |
| fomc_day | 10 | 1.260 | 1.264 | 1.373 | too small (10 days, minimum 20) |
| month_end | 16 | 1.098 | 1.099 | 1.748 | too small (16 days, minimum 20) |
| ordinary | 44 | 1.881 | 1.873 | 1.879 | +0.008 [+0.004, +0.011] **gain** |
| post_month_end_window | 27 | 1.474 | 1.475 | 1.431 | -0.001 [-0.005, +0.002] **undecided** |
| quarter_end | 2 | 0.845 | 0.834 | 2.831 | too small (2 days, minimum 20) |
| settlement | 91 | 1.650 | 1.641 | 2.000 | +0.009 [+0.003, +0.025] **gain** |
| tax_date | 6 | 1.764 | 1.614 | 3.226 | too small (6 days, minimum 20) |

Each against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 1.669 | 1.660 | 1.865 | +0.204 [-0.143, +0.426] **undecided** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 165 | 1.669 | 1.660 | 1.865 | +0.196 [-0.155, +0.418] **undecided** |

### upper-tail twCRPS, 2026

The October tax windows

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| October-window targets of 2019 and 2025 (the days that prompted the label) | 0 | | | | no days |
| October-window targets, not 2019 or 2025 | 0 | | | | no days |
| all October-window targets | 0 | | | | no days |

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.514 | 0.510 | 0.631 | +0.004 [+0.002, +0.007] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 165 | 0.468 | 0.467 | 0.565 | +0.001 [-0.001, +0.003] **undecided** |
| h=2 | 165 | 0.511 | 0.507 | 0.626 | +0.004 [+0.001, +0.007] **gain** |
| h=3 | 165 | 0.528 | 0.523 | 0.651 | +0.005 [+0.003, +0.008] **gain** |
| h=4 | 165 | 0.522 | 0.516 | 0.648 | +0.005 [+0.003, +0.009] **gain** |
| h=5 | 165 | 0.543 | 0.536 | 0.666 | +0.007 [+0.004, +0.011] **gain** |

By regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 146 | 0.482 | 0.478 | 0.543 | +0.004 [+0.002, +0.007] **gain** |
| quarter_end_turn | 4 | 0.646 | 0.641 | 1.084 | too small (4 days, minimum 20) |
| tax_date | 6 | 1.141 | 1.106 | 1.570 | too small (6 days, minimum 20) |
| turn | 12 | 0.717 | 0.716 | 1.229 | too small (12 days, minimum 20) |
| year_end | 1 | 3.024 | 3.036 | 2.245 | too small (1 days, minimum 20) |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 125 | 0.543 | 0.539 | 0.668 | +0.004 [+0.002, +0.007] **gain** |
| dom_19_23 | 27 | 0.156 | 0.157 | 0.472 | -0.001 [-0.025, +0.001] **undecided** |
| fomc_day | 10 | 0.373 | 0.375 | 0.326 | too small (10 days, minimum 20) |
| month_end | 16 | 0.601 | 0.603 | 0.786 | too small (16 days, minimum 20) |
| ordinary | 44 | 0.536 | 0.529 | 0.602 | +0.007 [+0.004, +0.012] **gain** |
| post_month_end_window | 27 | 0.940 | 0.940 | 0.859 | +0.000 [-0.001, +0.002] **undecided** |
| quarter_end | 2 | 0.835 | 0.824 | 1.744 | too small (2 days, minimum 20) |
| settlement | 91 | 0.572 | 0.565 | 0.724 | +0.007 [+0.003, +0.019] **gain** |
| tax_date | 6 | 1.141 | 1.106 | 1.570 | too small (6 days, minimum 20) |

Each against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.514 | 0.510 | 0.631 | +0.122 [+0.037, +0.227] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 165 | 0.514 | 0.510 | 0.631 | +0.117 [+0.033, +0.223] **gain** |

### Brier P(> +5 bp), 2026

The October tax windows

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| October-window targets of 2019 and 2025 (the days that prompted the label) | 0 | | | | no days |
| October-window targets, not 2019 or 2025 | 0 | | | | no days |
| all October-window targets | 0 | | | | no days |

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.035 | 0.035 | 0.044 | +0.000 [+0.000, +0.001] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 165 | 0.035 | 0.035 | 0.039 | +0.000 [-0.000, +0.001] **undecided** |
| h=2 | 165 | 0.036 | 0.036 | 0.043 | +0.000 [+0.000, +0.001] **gain** |
| h=3 | 165 | 0.035 | 0.035 | 0.043 | +0.000 [-0.000, +0.001] **undecided** |
| h=4 | 165 | 0.034 | 0.034 | 0.047 | +0.000 [-0.000, +0.000] **undecided** |
| h=5 | 165 | 0.035 | 0.035 | 0.049 | +0.000 [+0.000, +0.001] **gain** |

By regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 146 | 0.031 | 0.030 | 0.037 | +0.000 [+0.000, +0.001] **gain** |
| quarter_end_turn | 4 | 0.046 | 0.045 | 0.006 | too small (4 days, minimum 20) |
| tax_date | 6 | 0.144 | 0.142 | 0.159 | too small (6 days, minimum 20) |
| turn | 12 | 0.061 | 0.062 | 0.117 | too small (12 days, minimum 20) |
| year_end | 1 | 0.394 | 0.392 | 0.141 | too small (1 days, minimum 20) |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 125 | 0.041 | 0.041 | 0.048 | +0.000 [-0.000, +0.001] **undecided** |
| dom_19_23 | 27 | 0.003 | 0.003 | 0.028 | -0.000 [-0.000, +0.000] **undecided** |
| fomc_day | 10 | 0.010 | 0.010 | 0.009 | too small (10 days, minimum 20) |
| month_end | 16 | 0.034 | 0.034 | 0.047 | too small (16 days, minimum 20) |
| ordinary | 44 | 0.034 | 0.034 | 0.045 | +0.000 [+0.000, +0.001] **gain** |
| post_month_end_window | 27 | 0.084 | 0.085 | 0.069 | -0.001 [-0.004, +0.000] **undecided** |
| quarter_end | 2 | 0.089 | 0.087 | 0.006 | too small (2 days, minimum 20) |
| settlement | 91 | 0.046 | 0.046 | 0.052 | +0.000 [-0.000, +0.001] **undecided** |
| tax_date | 6 | 0.144 | 0.142 | 0.159 | too small (6 days, minimum 20) |

Each against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.035 | 0.035 | 0.044 | +0.010 [+0.000, +0.036] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+oct) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 165 | 0.035 | 0.035 | 0.044 | +0.009 [+0.000, +0.036] **gain** |

### The `tax_date` term at the last refit (2026-08-18)

| lead | control: effect (flagged pairs) | arm: effect (flagged pairs) |
|---|---|---|
| 1 | +0.058 (23) | +0.311 (29) |
| 2 | +0.425 (23) | +0.713 (29) |
| 3 | +0.475 (23) | +0.723 (29) |
| 4 | +0.441 (23) | +0.688 (29) |
| 5 | +0.539 (23) | +0.796 (29) |

## The reading of the label

The declared reading uses the October-window targets of the years but 2019 and 2025 (`supported`: a gain on grid CRPS or on upper-tail twCRPS with no cost on the other; `not supported`: a cost on either, or an identical score; else `undecided`):

| window | reading |
|---|---|
| 2026 | not read (the group is below the minimum size, or an interval is undefined) |
| development | not read (the group is below the minimum size, or an interval is undefined) |

## What this does and does not show

It is development data on days already seen. It does not adopt the label, change the frozen candidate or settle the data meaning of `tax_date`. The October windows are few days (see the group sizes above); a group below the study's minimum is not tested and is listed with its size in `result.json`. The model's level still counts an October-window day as an ordinary day, as the control does; a level that also skips those days is a different arm and was not run. B2 and the calendar ranker, which #965 tested, are not re-run. The label changes the fitted `tax_date` term, so the arm's forecast differs from the control's on days far from any October window (the count is stated under each window's heading); a pooled move is therefore not a move on the October windows, and the October-window rows are the ones that speak to the label. Where the leave-out reading is below the minimum group size it is not read, and the means beside it are descriptive only.

Every figure on this page is in [`result.json`](s3c-ann-net-october-1455/result.json).
