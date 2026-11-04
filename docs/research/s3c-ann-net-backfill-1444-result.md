# (s3c-ann-net) trained on the 2014-18 back-filled history: a scratch measurement (#1444)

> **Development evidence, not a verdict** (scoring protocol v1: development data never gives one). H4 (longer history fixes part of 2018-19), step 3, measured on the H5 candidate (s3c-ann-net). A scratch measurement under her ruling of 26 October 2026 (ledger item 56, #1223; `docs/decisions/information-set.md`, back-fill amendment, item 3): nothing is adopted and the frozen candidate does not change. Made at 18:00 New York time. Declaration: [`metadata/s3c_ann_net_backfill_1444.json`](../../metadata/s3c_ann_net_backfill_1444.json), committed before any score.

## What was measured

The control is (s3c-ann-net) as #1288, #1319 and #1314 walk it, on the published panel (from 2018-04-03). The arm, (s3c-ann-net+bf), is the same model on the same decision days and refit days with the 899 back-filled rows (2014-08-22 to 2018-03-29) before the published rows in every training frame. A back-filled row carries SOFR, IORB, TGCR, BGCR and the calendar columns only; every fit reads the series iorb, sofr, admitted from 2018-05-17T00:00:00. The two settlement terms and the two market-holiday terms (`month_end`, `post_month_end_window`; the pinned holiday table starts on 2018-01-01) are **not fitted on back-filled rows**: they are fitted on published targets only, and the three terms a back-filled row carries (`quarter_end`, `tax_date`, `dom_19_23`) are then fitted on every pair, net of those effects. A back-filled settlement or month-end day is therefore not flagged and its residual stays in the pool and in the three fits: that is a cost the measurement includes, not one it removes.

d is the reference's score less the arm's, so a positive d favours the arm. The interval is the studentized stationary-bootstrap interval of the protocol (`scoring_protocol.paired_tests`, 90%); *gain* is an interval wholly above zero, *cost* wholly below, *undecided* otherwise. Day-type groups are scored on their own days as #1288 scores them, so a group that is not contiguous joins days that were months apart into one block.

## The development window (targets up to 2025-12-31; #1145, #1241)

1855 decision days, first scored 2018-07-19, last 2025-12-23; 89 refits of the control and 89 of the arm (the same days). The arm had no forecast on 0 days before the control's first.

### grid CRPS, development

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 1.601 | 1.615 | 1.843 | -0.014 [-0.034, +0.002] **undecided** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 1855 | 1.478 | 1.496 | 1.630 | -0.018 [-0.047, -0.003] **cost** |
| h=2 | 1855 | 1.567 | 1.591 | 1.751 | -0.024 [-0.057, -0.005] **cost** |
| h=3 | 1855 | 1.607 | 1.626 | 1.860 | -0.019 [-0.043, +0.001] **undecided** |
| h=4 | 1855 | 1.650 | 1.660 | 1.950 | -0.010 [-0.028, +0.009] **undecided** |
| h=5 | 1855 | 1.704 | 1.703 | 2.025 | +0.000 [-0.018, +0.027] **undecided** |

By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| 2018 H2 | 111 | 2.234 | 2.183 | 2.679 | +0.051 [-0.123, +0.353] **undecided** |
| 2018-19 | 361 | 3.642 | 3.704 | 4.031 | -0.062 [-0.154, +0.024] **undecided** |
| 2020 | 251 | 1.490 | 1.504 | 1.641 | -0.014 [-0.077, +0.006] **undecided** |
| 2021-23 | 748 | 0.634 | 0.634 | 0.671 | +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 250 | 1.074 | 1.074 | 1.359 | -0.000 [-0.000, +0.000] **undecided** |
| 2025-26 | 249 | 2.229 | 2.229 | 2.933 | +0.000 [-0.000, +0.000] **undecided** |

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 1591 | 1.287 | 1.324 | 1.464 | -0.038 [-0.086, -0.014] **cost** |
| quarter_end_turn | 44 | 3.512 | 3.276 | 4.185 | +0.236 [-0.049, +31994286.011] **undecided** |
| tax_date | 89 | 5.083 | 4.990 | 5.386 | +0.093 [-0.006, +7.527] **undecided** |
| turn | 120 | 1.687 | 1.685 | 2.356 | +0.002 [-0.024, +0.040] **undecided** |
| year_end | 15 | 8.658 | 7.650 | 10.903 | group too small |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 1352 | 1.790 | 1.794 | 2.046 | -0.004 [-0.022, +0.018] **undecided** |
| dom_19_23 | 305 | 1.139 | 1.176 | 1.327 | -0.037 [-0.255, -0.002] **cost** |
| fomc_day | 118 | 4.450 | 4.433 | 4.412 | +0.017 [-0.021, +0.130] **undecided** |
| iorb_window | 78 | 2.150 | 2.284 | 1.902 | -0.134 [-1.763, +0.031] **undecided** |
| month_end | 180 | 2.281 | 2.153 | 2.894 | +0.127 [-0.012, +0.964] **undecided** |
| ordinary | 507 | 1.116 | 1.157 | 1.326 | -0.041 [-0.149, -0.010] **cost** |
| post_month_end_window | 267 | 2.032 | 2.077 | 2.146 | -0.045 [-0.128, -0.007] **cost** |
| quarter_end | 30 | 5.336 | 4.557 | 6.752 | +0.778 [-0.228, +48649640.420] **undecided** |
| settlement | 946 | 1.939 | 1.921 | 2.264 | +0.018 [-0.003, +0.071] **undecided** |
| tax_date | 89 | 5.083 | 4.990 | 5.386 | +0.093 [-0.006, +7.527] **undecided** |

Each arm against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 1.601 | 1.615 | 1.843 | +0.228 [+0.137, +0.327] **gain** |
| 2018 H2 | 111 | 2.234 | 2.183 | 2.679 | +0.497 [-0.073, +1.141] **undecided** |
| 2018-19 | 361 | 3.642 | 3.704 | 4.031 | +0.326 [+0.041, +0.655] **gain** |
| 2020 | 251 | 1.490 | 1.504 | 1.641 | +0.137 [-0.191, +0.455] **undecided** |
| 2021-23 | 748 | 0.634 | 0.634 | 0.671 | +0.037 [-0.002, +0.074] **undecided** |
| 2024 | 250 | 1.074 | 1.074 | 1.359 | +0.285 [+0.118, +0.704] **gain** |
| 2025-26 | 249 | 2.229 | 2.229 | 2.933 | +0.704 [+0.446, +1.018] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 1855 | 1.601 | 1.615 | 1.843 | +0.242 [+0.157, +0.341] **gain** |
| 2018 H2 | 111 | 2.234 | 2.183 | 2.679 | +0.445 [+0.054, +0.941] **gain** |
| 2018-19 | 361 | 3.642 | 3.704 | 4.031 | +0.388 [+0.138, +0.688] **gain** |
| 2020 | 251 | 1.490 | 1.504 | 1.641 | +0.151 [-0.145, +0.473] **undecided** |
| 2021-23 | 748 | 0.634 | 0.634 | 0.671 | +0.037 [-0.002, +0.074] **undecided** |
| 2024 | 250 | 1.074 | 1.074 | 1.359 | +0.285 [+0.118, +0.704] **gain** |
| 2025-26 | 249 | 2.229 | 2.229 | 2.933 | +0.704 [+0.446, +1.018] **gain** |

### upper-tail twCRPS, development

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.845 | 0.860 | 0.991 | -0.015 [-0.034, -0.000] **cost** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 1855 | 0.826 | 0.844 | 0.930 | -0.017 [-0.049, -0.003] **cost** |
| h=2 | 1855 | 0.838 | 0.860 | 0.955 | -0.022 [-0.056, -0.004] **cost** |
| h=3 | 1855 | 0.839 | 0.857 | 0.999 | -0.018 [-0.040, -0.001] **cost** |
| h=4 | 1855 | 0.851 | 0.863 | 1.030 | -0.013 [-0.029, +0.004] **undecided** |
| h=5 | 1855 | 0.869 | 0.874 | 1.040 | -0.004 [-0.021, +0.022] **undecided** |

By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| 2018 H2 | 111 | 1.271 | 1.226 | 1.671 | +0.045 [-0.095, +0.473] **undecided** |
| 2018-19 | 361 | 3.205 | 3.271 | 3.559 | -0.066 [-0.149, +0.012] **undecided** |
| 2020 | 251 | 0.578 | 0.593 | 0.772 | -0.015 [-0.072, +0.001] **undecided** |
| 2021-23 | 748 | 0.007 | 0.007 | 0.008 | +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 250 | 0.169 | 0.169 | 0.207 | -0.000 [-0.000, +0.000] **undecided** |
| 2025-26 | 249 | 0.926 | 0.926 | 1.281 | identical |

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 1591 | 0.540 | 0.577 | 0.634 | -0.038 [-0.092, -0.015] **cost** |
| quarter_end_turn | 44 | 2.136 | 1.899 | 2.606 | +0.237 [-0.046, +707457617.373] **undecided** |
| tax_date | 89 | 4.365 | 4.282 | 4.626 | +0.083 [-0.006, +7.523] **undecided** |
| turn | 120 | 0.997 | 0.996 | 1.440 | +0.001 [-0.022, +0.035] **undecided** |
| year_end | 15 | 7.997 | 6.990 | 9.751 | group too small |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 1352 | 1.014 | 1.018 | 1.179 | -0.004 [-0.020, +0.018] **undecided** |
| dom_19_23 | 305 | 0.411 | 0.441 | 0.574 | -0.030 [-0.345, +0.006] **undecided** |
| fomc_day | 118 | 3.609 | 3.595 | 3.588 | +0.014 [-0.016, +0.095] **undecided** |
| iorb_window | 78 | 1.405 | 1.542 | 1.167 | -0.137 [-1.992, +0.026] **undecided** |
| month_end | 180 | 1.451 | 1.323 | 1.835 | +0.128 [-0.009, +1.032] **undecided** |
| ordinary | 507 | 0.412 | 0.457 | 0.515 | -0.044 [-0.185, -0.012] **cost** |
| post_month_end_window | 267 | 1.109 | 1.148 | 1.121 | -0.039 [-0.108, -0.006] **cost** |
| quarter_end | 30 | 4.178 | 3.406 | 5.270 | +0.773 [-0.220, +552612986.296] **undecided** |
| settlement | 946 | 1.179 | 1.163 | 1.387 | +0.016 [-0.005, +0.068] **undecided** |
| tax_date | 89 | 4.365 | 4.282 | 4.626 | +0.083 [-0.006, +7.523] **undecided** |

Each arm against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.845 | 0.860 | 0.991 | +0.131 [+0.058, +0.232] **gain** |
| 2018 H2 | 111 | 1.271 | 1.226 | 1.671 | +0.444 [-0.036, +1.614] **undecided** |
| 2018-19 | 361 | 3.205 | 3.271 | 3.559 | +0.288 [+0.008, +0.632] **gain** |
| 2020 | 251 | 0.578 | 0.593 | 0.772 | +0.179 [-0.024, +1.117] **undecided** |
| 2021-23 | 748 | 0.007 | 0.007 | 0.008 | +0.001 [-0.001, +0.002] **undecided** |
| 2024 | 250 | 0.169 | 0.169 | 0.207 | +0.037 [-0.002, +0.518] **undecided** |
| 2025-26 | 249 | 0.926 | 0.926 | 1.281 | +0.355 [+0.100, +0.939] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.845 | 0.860 | 0.991 | +0.146 [+0.075, +0.252] **gain** |
| 2018 H2 | 111 | 1.271 | 1.226 | 1.671 | +0.400 [+0.019, +1.221] **gain** |
| 2018-19 | 361 | 3.205 | 3.271 | 3.559 | +0.354 [+0.096, +0.679] **gain** |
| 2020 | 251 | 0.578 | 0.593 | 0.772 | +0.194 [-0.009, +1.210] **undecided** |
| 2021-23 | 748 | 0.007 | 0.007 | 0.008 | +0.001 [-0.001, +0.002] **undecided** |
| 2024 | 250 | 0.169 | 0.169 | 0.207 | +0.037 [-0.002, +0.518] **undecided** |
| 2025-26 | 249 | 0.926 | 0.926 | 1.281 | +0.355 [+0.100, +0.939] **gain** |

### Brier P(> +5 bp), development

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.046 | 0.047 | 0.054 | -0.001 [-0.003, +0.001] **undecided** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 1855 | 0.042 | 0.042 | 0.048 | -0.001 [-0.002, +0.001] **undecided** |
| h=2 | 1855 | 0.044 | 0.045 | 0.051 | -0.001 [-0.002, +0.001] **undecided** |
| h=3 | 1855 | 0.047 | 0.048 | 0.056 | -0.001 [-0.003, +0.001] **undecided** |
| h=4 | 1855 | 0.048 | 0.049 | 0.058 | -0.001 [-0.004, +0.001] **undecided** |
| h=5 | 1855 | 0.049 | 0.049 | 0.058 | -0.001 [-0.003, +0.001] **undecided** |

By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| 2018 H2 | 111 | 0.063 | 0.068 | 0.104 | -0.005 [-0.011, +0.001] **undecided** |
| 2018-19 | 361 | 0.165 | 0.168 | 0.181 | -0.004 [-0.014, +0.007] **undecided** |
| 2020 | 251 | 0.023 | 0.023 | 0.032 | -0.001 [-0.002, +0.000] **undecided** |
| 2021-23 | 748 | 0.000 | 0.000 | 0.000 | identical |
| 2024 | 250 | 0.017 | 0.017 | 0.019 | identical |
| 2025-26 | 249 | 0.066 | 0.066 | 0.096 | identical |

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 1591 | 0.045 | 0.047 | 0.049 | -0.002 [-0.004, +0.000] **undecided** |
| quarter_end_turn | 44 | 0.096 | 0.084 | 0.120 | +0.012 [-0.001, +26864273.145] **undecided** |
| tax_date | 89 | 0.054 | 0.044 | 0.075 | +0.009 [-0.001, +1.378] **undecided** |
| turn | 120 | 0.039 | 0.038 | 0.075 | +0.001 [-0.001, +0.005] **undecided** |
| year_end | 15 | 0.051 | 0.062 | 0.171 | group too small |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 1352 | 0.049 | 0.049 | 0.060 | +0.000 [-0.001, +0.003] **undecided** |
| dom_19_23 | 305 | 0.034 | 0.033 | 0.046 | +0.001 [+0.000, +0.006] **gain** |
| fomc_day | 118 | 0.053 | 0.053 | 0.045 | +0.001 [-0.001, +0.008] **undecided** |
| iorb_window | 78 | 0.066 | 0.067 | 0.058 | -0.001 [-0.009, +0.000] **undecided** |
| month_end | 180 | 0.055 | 0.053 | 0.084 | +0.002 [-0.004, +0.015] **undecided** |
| ordinary | 507 | 0.038 | 0.042 | 0.041 | -0.004 [-0.012, -0.001] **cost** |
| post_month_end_window | 267 | 0.065 | 0.065 | 0.064 | -0.000 [-0.003, +0.003] **undecided** |
| quarter_end | 30 | 0.103 | 0.098 | 0.161 | +0.005 [-0.008, +5188096.239] **undecided** |
| settlement | 946 | 0.049 | 0.049 | 0.065 | +0.001 [-0.001, +0.003] **undecided** |
| tax_date | 89 | 0.054 | 0.044 | 0.075 | +0.009 [-0.001, +1.378] **undecided** |

Each arm against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.046 | 0.047 | 0.054 | +0.007 [-0.000, +0.015] **undecided** |
| 2018 H2 | 111 | 0.063 | 0.068 | 0.104 | +0.036 [-0.010, +0.138] **undecided** |
| 2018-19 | 361 | 0.165 | 0.168 | 0.181 | +0.012 [-0.023, +0.045] **undecided** |
| 2020 | 251 | 0.023 | 0.023 | 0.032 | +0.009 [-0.002, +0.028] **undecided** |
| 2021-23 | 748 | 0.000 | 0.000 | 0.000 | +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 250 | 0.017 | 0.017 | 0.019 | +0.002 [-0.001, +0.219] **undecided** |
| 2025-26 | 249 | 0.066 | 0.066 | 0.096 | +0.030 [+0.005, +0.086] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 1855 | 0.046 | 0.047 | 0.054 | +0.008 [+0.001, +0.016] **gain** |
| 2018 H2 | 111 | 0.063 | 0.068 | 0.104 | +0.041 [-0.000, +0.154] **undecided** |
| 2018-19 | 361 | 0.165 | 0.168 | 0.181 | +0.016 [-0.018, +0.046] **undecided** |
| 2020 | 251 | 0.023 | 0.023 | 0.032 | +0.009 [-0.001, +0.030] **undecided** |
| 2021-23 | 748 | 0.000 | 0.000 | 0.000 | +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 250 | 0.017 | 0.017 | 0.019 | +0.002 [-0.001, +0.219] **undecided** |
| 2025-26 | 249 | 0.066 | 0.066 | 0.096 | +0.030 [+0.005, +0.086] **gain** |

### Coverage of the central 90% band

| group | days | control | arm | move (arm less control) |
|---|---|---|---|---|
| pooled/all decision days | 1855 | 0.875 | 0.878 | +0.003 [+0.001, +0.006] |
| regime/2018 H2 | 111 | 0.892 | 0.895 | +0.004 [-0.022, +0.027] |
| regime/2018-19 | 361 | 0.868 | 0.884 | +0.016 [+0.004, +0.028] |

(The interval of a move in coverage is the unstudentized 90% stationary-bootstrap percentile interval; no reading is taken from it.)

### The named quarter-ends

| target | decision day | lead | outcome (bp) | control q05 / q50 / q95 | arm q05 / q50 / q95 | control CRPS | arm CRPS | control quarter-end effect (flagged) | arm quarter-end effect (flagged) |
|---|---|---|---|---|---|---|---|---|---|
| 2018-09-28 | 2018-09-21 | 5 | 5.0 | -2.0 / -0.3 / 2.9 | -0.8 / 1.0 / 5.3 | 3.849 | 2.409 | not in fit | +2.02 (8) |
| 2018-09-28 | 2018-09-24 | 4 | 5.0 | -1.7 / -0.5 / 1.5 | -1.0 / 0.3 / 2.9 | 4.513 | 3.482 | not in fit | +2.15 (8) |
| 2018-09-28 | 2018-09-25 | 3 | 5.0 | -1.8 / -0.5 / 1.7 | -0.0 / 1.2 / 3.6 | 4.393 | 2.671 | not in fit | +2.56 (8) |
| 2018-09-28 | 2018-09-26 | 2 | 5.0 | -2.1 / -0.7 / 2.7 | -0.4 / 1.2 / 4.6 | 4.149 | 2.389 | not in fit | +2.48 (8) |
| 2018-09-28 | 2018-09-27 | 1 | 5.0 | -3.0 / -0.7 / 5.8 | -0.1 / 3.0 / 9.2 | 3.538 | 1.038 | not in fit | +2.27 (8) |
| 2018-12-31 | 2018-12-21 | 5 | 60.0 | -3.2 / 11.3 / 31.1 | 6.6 / 22.3 / 51.7 | 39.356 | 24.923 | not in fit | +2.03 (8) |
| 2018-12-31 | 2018-12-24 | 4 | 60.0 | -4.8 / 10.1 / 29.9 | 6.5 / 21.6 / 47.9 | 39.544 | 26.378 | not in fit | +2.12 (8) |
| 2018-12-31 | 2018-12-26 | 3 | 60.0 | -4.3 / 7.7 / 24.5 | 7.9 / 20.6 / 41.2 | 43.490 | 29.802 | not in fit | +2.59 (8) |
| 2018-12-31 | 2018-12-27 | 2 | 60.0 | -4.8 / 7.1 / 25.0 | 10.2 / 21.0 / 39.4 | 43.887 | 29.775 | not in fit | +2.52 (8) |
| 2018-12-31 | 2018-12-28 | 1 | 60.0 | -1.1 / 8.1 / 23.6 | 10.2 / 20.8 / 38.7 | 43.376 | 30.664 | not in fit | +2.19 (8) |

### The first refit at which `quarter_end` entered the fit

| lead | control | arm |
|---|---|---|
| 1 | 2019-01-23 | 2018-07-19 |
| 2 | 2019-01-23 | 2018-07-19 |
| 3 | 2019-01-23 | 2018-07-19 |
| 4 | 2019-01-23 | 2018-07-19 |
| 5 | 2019-01-23 | 2018-07-19 |

The back-filled rows are in the training frame of 21 of the arm's 89 refits, the last on 2020-03-26: the model trains on a trailing two years (`spread_mean_reversion.TRAIN_YEARS`), so a refit from about April 2020 on holds no back-filled row and the arm's forecast is the control's up to the two-stage arithmetic (differences of rounding size are read as identical, tolerance 1e-9).

## The 2026 development days (targets 2026-01-02 to 2026-09-03; #1229, #1252)

165 decision days, first scored 2025-12-31, last 2026-08-27; 97 refits of the control and 97 of the arm (the same days). The arm had no forecast on 0 days before the control's first.

### grid CRPS, 2026

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 1.669 | 1.669 | 1.865 | +0.000 [-0.000, +0.000] **undecided** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 165 | 1.480 | 1.480 | 1.619 | +0.000 [+0.000, +0.000] **gain** |
| h=2 | 165 | 1.651 | 1.651 | 1.856 | -0.000 [-0.000, +0.000] **undecided** |
| h=3 | 165 | 1.715 | 1.715 | 1.945 | +0.000 [-0.000, +0.000] **undecided** |
| h=4 | 165 | 1.728 | 1.728 | 1.935 | -0.000 [-0.000, +0.000] **undecided** |
| h=5 | 165 | 1.769 | 1.769 | 1.967 | -0.000 [-0.000, +0.000] **undecided** |

By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 146 | 1.712 | 1.712 | 1.809 | +0.000 [-0.000, +0.000] **undecided** |
| quarter_end_turn | 4 | 0.909 | 0.909 | 2.125 | group too small |
| tax_date | 6 | 1.764 | 1.764 | 3.226 | group too small |
| turn | 12 | 1.227 | 1.227 | 1.693 | group too small |
| year_end | 1 | 3.057 | 3.057 | 2.252 | group too small |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 125 | 1.594 | 1.594 | 1.855 | -0.000 [-0.000, +0.000] **undecided** |
| dom_19_23 | 27 | 1.807 | 1.807 | 1.789 | -0.000 [-0.000, +0.000] **undecided** |
| fomc_day | 10 | 1.260 | 1.260 | 1.373 | group too small |
| month_end | 16 | 1.098 | 1.098 | 1.748 | group too small |
| ordinary | 44 | 1.881 | 1.881 | 1.879 | identical |
| post_month_end_window | 27 | 1.474 | 1.474 | 1.431 | identical |
| quarter_end | 2 | 0.845 | 0.845 | 2.831 | group too small |
| settlement | 91 | 1.650 | 1.650 | 2.000 | -0.000 [-0.000, +0.000] **undecided** |
| tax_date | 6 | 1.764 | 1.764 | 3.226 | group too small |

Each arm against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 1.669 | 1.669 | 1.865 | +0.196 [-0.155, +0.418] **undecided** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 165 | 1.669 | 1.669 | 1.865 | +0.196 [-0.155, +0.418] **undecided** |

### upper-tail twCRPS, 2026

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.514 | 0.514 | 0.631 | identical |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 165 | 0.468 | 0.468 | 0.565 | +0.000 [+0.000, +0.000] **gain** |
| h=2 | 165 | 0.511 | 0.511 | 0.626 | identical |
| h=3 | 165 | 0.528 | 0.528 | 0.651 | identical |
| h=4 | 165 | 0.522 | 0.522 | 0.648 | -0.000 [-0.000, +0.000] **undecided** |
| h=5 | 165 | 0.543 | 0.543 | 0.666 | +0.000 [-0.000, +0.000] **undecided** |

By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 146 | 0.482 | 0.482 | 0.543 | identical |
| quarter_end_turn | 4 | 0.646 | 0.646 | 1.084 | group too small |
| tax_date | 6 | 1.141 | 1.141 | 1.570 | group too small |
| turn | 12 | 0.717 | 0.717 | 1.229 | group too small |
| year_end | 1 | 3.024 | 3.024 | 2.245 | group too small |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 125 | 0.543 | 0.543 | 0.668 | identical |
| dom_19_23 | 27 | 0.156 | 0.156 | 0.472 | identical |
| fomc_day | 10 | 0.373 | 0.373 | 0.326 | group too small |
| month_end | 16 | 0.601 | 0.601 | 0.786 | group too small |
| ordinary | 44 | 0.536 | 0.536 | 0.602 | identical |
| post_month_end_window | 27 | 0.940 | 0.940 | 0.859 | identical |
| quarter_end | 2 | 0.835 | 0.835 | 1.744 | group too small |
| settlement | 91 | 0.572 | 0.572 | 0.724 | identical |
| tax_date | 6 | 1.141 | 1.141 | 1.570 | group too small |

Each arm against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.514 | 0.514 | 0.631 | +0.117 [+0.033, +0.223] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 165 | 0.514 | 0.514 | 0.631 | +0.117 [+0.033, +0.223] **gain** |

### Brier P(> +5 bp), 2026

Pooled and by lead

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.035 | 0.035 | 0.044 | identical |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| h=1 | 165 | 0.035 | 0.035 | 0.039 | identical |
| h=2 | 165 | 0.036 | 0.036 | 0.043 | identical |
| h=3 | 165 | 0.035 | 0.035 | 0.043 | identical |
| h=4 | 165 | 0.034 | 0.034 | 0.047 | identical |
| h=5 | 165 | 0.035 | 0.035 | 0.049 | identical |

By regime (2018-19 is the headline; 2018 H2 is a declared sub-window of it)

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|

By pressure-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| ordinary | 146 | 0.031 | 0.031 | 0.037 | identical |
| quarter_end_turn | 4 | 0.046 | 0.046 | 0.006 | group too small |
| tax_date | 6 | 0.144 | 0.144 | 0.159 | group too small |
| turn | 12 | 0.061 | 0.061 | 0.117 | group too small |
| year_end | 1 | 0.394 | 0.394 | 0.141 | group too small |

By target-day type

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, control less arm |
|---|---|---|---|---|---|
| calendar_days | 125 | 0.041 | 0.041 | 0.048 | identical |
| dom_19_23 | 27 | 0.003 | 0.003 | 0.028 | identical |
| fomc_day | 10 | 0.010 | 0.010 | 0.009 | group too small |
| month_end | 16 | 0.034 | 0.034 | 0.047 | group too small |
| ordinary | 44 | 0.034 | 0.034 | 0.045 | identical |
| post_month_end_window | 27 | 0.084 | 0.084 | 0.069 | identical |
| quarter_end | 2 | 0.089 | 0.089 | 0.006 | group too small |
| settlement | 91 | 0.046 | 0.046 | 0.052 | identical |
| tax_date | 6 | 0.144 | 0.144 | 0.159 | group too small |

Each arm against B1'* (the arm, then the control), pooled and by regime

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less arm |
|---|---|---|---|---|---|
| all decision days | 165 | 0.035 | 0.035 | 0.044 | +0.009 [+0.000, +0.036] **gain** |

| group | days | (s3c-ann-net) | (s3c-ann-net+bf) | B1'* | d, B1'* less control |
|---|---|---|---|---|---|
| all decision days | 165 | 0.035 | 0.035 | 0.044 | +0.009 [+0.000, +0.036] **gain** |

### Coverage of the central 90% band

| group | days | control | arm | move (arm less control) |
|---|---|---|---|---|
| pooled/all decision days | 165 | 0.892 | 0.892 | +0.000 [+0.000, +0.000] |

(The interval of a move in coverage is the unstudentized 90% stationary-bootstrap percentile interval; no reading is taken from it.)

### The first refit at which `quarter_end` entered the fit

| lead | control | arm |
|---|---|---|
| 1 | 2019-01-23 | 2018-07-19 |
| 2 | 2019-01-23 | 2018-07-19 |
| 3 | 2019-01-23 | 2018-07-19 |
| 4 | 2019-01-23 | 2018-07-19 |
| 5 | 2019-01-23 | 2018-07-19 |

The back-filled rows are in the training frame of 21 of the arm's 97 refits, the last on 2020-03-26: the model trains on a trailing two years (`spread_mean_reversion.TRAIN_YEARS`), so a refit from about April 2020 on holds no back-filled row and the arm's forecast is the control's up to the two-stage arithmetic (differences of rounding size are read as identical, tolerance 1e-9).

## What this does and does not show

It is a scratch measurement on development data. It does not adopt the back-fill, change the frozen candidate, or settle whether IORB on back-filled rows stays admitted beyond training history. The 2014-18 floor period was calm with a negative spread, so its residuals can make the 2018-19 bands too narrow; the coverage table is the check. The result goes to the validation report's known limits. Skipped groups, with their sizes, are in `result.json`. The intervals of the small day-type groups (quarter-end, tax date) can run very far above the point value: the studentized interval of #1288's method divides by a standard error that a resample of a few days can make near zero.

Every figure on this page is in [`result.json`](s3c-ann-net-backfill-1444/result.json).
