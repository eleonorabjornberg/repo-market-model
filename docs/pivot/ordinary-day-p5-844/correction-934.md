# Correction of the ordinary-day page (#844, PR #853): the result within each regime (#934)

**Hypothesis and step:** H5 (primary goal), step 3. **Development data only: this is not a verdict** (scoring protocol v1, #640). Dated 19 October 2026, on Eleonora's ruling on #917: the ordinary-day result is reported within each regime, and **no pooled gain is claimed**. What counts as a ranking gain for H5's kill clause stays Eleonora's.

This page corrects how `docs/pivot/ordinary-day-p5-result.md` and `docs/pivot/ordinary-day-p5-844/report.md` read; both stand as published and neither is edited. Nothing is scored again: every figure below is read from `docs/pivot/ordinary-day-p5-844/score.json`, the 90% stationary-bootstrap percentile intervals (block 10, 2000 replications) and the seed of that run. Each cell is the paired AUROC difference from persistence-logistic on ordinary target days (not a risk date under `risk_dates.NON_ORDINARY`); above zero is better than persistence-logistic. `n/a`: fewer than 3 pressure days. `†`: no interval.

## mean reversion (#686)

| lead | 2018-19 | 2020-24 | 2025-26 |
|---|---|---|---|
| 1 | +0.077 [+0.020, +0.143] (61 pressure days) | -0.068 [-0.310, +0.036] (5 pressure days) | +0.015 [+0.000, +0.042] (15 pressure days) |
| 2 | +0.095 [+0.021, +0.177] (61 pressure days) | -0.022 [-0.201, +0.148] (5 pressure days) | +0.037 [+0.010, +0.086] (15 pressure days) |
| 3 | +0.076 [-0.003, +0.161] (61 pressure days) | -0.038 [-0.304, +0.164] (5 pressure days) | +0.038 [+0.008, +0.088] (16 pressure days) |
| 4 | +0.075 [-0.017, +0.161] (61 pressure days) | -0.123 [-0.339, -0.027] (5 pressure days) | +0.033 [+0.001, +0.094] (16 pressure days) |
| 5 | +0.075 [-0.020, +0.164] (61 pressure days) | -0.097 [-0.235, -0.030] (5 pressure days) | +0.026 [-0.007, +0.088] (16 pressure days) |

## (i) context-pooled residuals (#761)

| lead | 2018-19 | 2020-24 | 2025-26 |
|---|---|---|---|
| 1 | +0.083 [+0.026, +0.151] (61 pressure days) | -0.080 [-0.305, +0.038] (5 pressure days) | +0.017 [+0.003, +0.047] (15 pressure days) |
| 2 | +0.109 [+0.039, +0.192] (61 pressure days) | -0.037 [-0.215, +0.142] (5 pressure days) | +0.035 [+0.008, +0.093] (15 pressure days) |
| 3 | +0.078 [-0.002, +0.166] (61 pressure days) | -0.044 [-0.301, +0.162] (5 pressure days) | +0.031 [+0.002, +0.077] (16 pressure days) |
| 4 | +0.076 [-0.015, +0.168] (61 pressure days) | -0.140 [-0.332, -0.055] (5 pressure days) | +0.023 [-0.006, +0.080] (16 pressure days) |
| 5 | +0.082 [-0.013, +0.172] (61 pressure days) | -0.173 [-0.384, -0.057] (5 pressure days) | +0.020 [-0.011, +0.077] (16 pressure days) |

## (c) two-part (#634)

| lead | 2018-19 | 2020-24 | 2025-26 |
|---|---|---|---|
| 1 | -0.009 [-0.074, +0.059] (61 pressure days) | -0.149 [-0.326, +0.102] (5 pressure days) | +0.003 [-0.020, +0.049] (15 pressure days) |
| 2 | +0.011 [-0.096, +0.120] (61 pressure days) | -0.091 [-0.312, +0.197] (5 pressure days) | +0.011 [-0.012, +0.060] (15 pressure days) |
| 3 | -0.024 [-0.118, +0.073] (61 pressure days) | -0.030 [-0.302, +0.522] (5 pressure days) | +0.008 [-0.021, +0.063] (16 pressure days) |
| 4 | -0.067 [-0.138, +0.009] (61 pressure days) | -0.085 [-0.225, -0.022] (5 pressure days) | +0.020 [-0.008, +0.073] (16 pressure days) |
| 5 | -0.061 [-0.149, +0.015] (61 pressure days) | -0.161 [-0.345, -0.060] (5 pressure days) | -0.065 [-0.161, +0.023] (16 pressure days) |

## gbm_funding (#634)

| lead | 2018-19 | 2020-24 | 2025-26 |
|---|---|---|---|
| 1 | +0.031 [-0.028, +0.093] (61 pressure days) | -0.027 [-0.230, +0.099] (5 pressure days) | -0.011 [-0.032, +0.023] (15 pressure days) |
| 2 | +0.078 [+0.003, +0.156] (61 pressure days) | +0.021 [-0.143, +0.221] (5 pressure days) | -0.010 [-0.045, +0.035] (15 pressure days) |
| 3 | +0.075 [-0.008, +0.162] (61 pressure days) | -0.017 [-0.237, +0.210] (5 pressure days) | -0.004 [-0.033, +0.039] (16 pressure days) |
| 4 | +0.063 [-0.011, +0.141] (61 pressure days) | -0.102 [-0.263, -0.027] (5 pressure days) | -0.010 [-0.034, +0.026] (16 pressure days) |
| 5 | +0.068 [-0.029, +0.163] (61 pressure days) | -0.111 [-0.317, +0.001] (5 pressure days) | -0.026 [-0.050, +0.009] (16 pressure days) |

## Tally of regime-by-lead cells (development)

- **mean reversion (#686)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, the paired AUROC difference from persistence-logistic is above zero in 5, covers zero in 8 and is below zero in 2. Development, not a verdict.
- **(i) context-pooled residuals (#761)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, the paired AUROC difference from persistence-logistic is above zero in 5, covers zero in 8 and is below zero in 2. Development, not a verdict.
- **(c) two-part (#634)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, the paired AUROC difference from persistence-logistic is above zero in 0, covers zero in 13 and is below zero in 2. Development, not a verdict.
- **gbm_funding (#634)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, the paired AUROC difference from persistence-logistic is above zero in 1, covers zero in 13 and is below zero in 1. Development, not a verdict.

These lines count cells; they set no threshold.

## Why the pooled rows are not read as a gain (#917)

A pooled paired AUROC difference larger than the difference in every one of its regimes can only come from pairs that cross regimes: a 2018-19 pressure day ranked above a calm day of 2020-24. Most pressure days are in 2018-19 (61 of 81 at lead 1) and 2020-24 has 5, so such a gain reflects the 2018-19 base-rate gap, not ranking within a regime. In 13 of 20 model-by-lead rows below the pooled difference exceeds every regime's. The pooled rows are shown only to show this; they are not claimed.

| model | lead | pooled (not claimed) | largest regime difference | pooled above every regime |
|---|---|---|---|---|
| mean reversion (#686) | 1 | +0.037 [+0.012, +0.069] | +0.077 | no |
| mean reversion (#686) | 2 | +0.074 [+0.036, +0.124] | +0.095 | no |
| mean reversion (#686) | 3 | +0.082 [+0.040, +0.129] | +0.076 | yes |
| mean reversion (#686) | 4 | +0.078 [+0.030, +0.137] | +0.075 | yes |
| mean reversion (#686) | 5 | +0.101 [+0.036, +0.181] | +0.075 | yes |
| (i) context-pooled residuals (#761) | 1 | +0.038 [+0.013, +0.069] | +0.083 | no |
| (i) context-pooled residuals (#761) | 2 | +0.076 [+0.038, +0.126] | +0.109 | no |
| (i) context-pooled residuals (#761) | 3 | +0.080 [+0.037, +0.129] | +0.078 | yes |
| (i) context-pooled residuals (#761) | 4 | +0.074 [+0.026, +0.132] | +0.076 | no |
| (i) context-pooled residuals (#761) | 5 | +0.095 [+0.030, +0.174] | +0.082 | yes |
| (c) two-part (#634) | 1 | +0.012 [-0.017, +0.040] | +0.003 | yes |
| (c) two-part (#634) | 2 | +0.049 [+0.007, +0.103] | +0.011 | yes |
| (c) two-part (#634) | 3 | +0.061 [+0.016, +0.112] | +0.008 | yes |
| (c) two-part (#634) | 4 | +0.051 [+0.011, +0.105] | +0.020 | yes |
| (c) two-part (#634) | 5 | +0.026 [-0.034, +0.107] | -0.061 | yes |
| gbm_funding (#634) | 1 | +0.029 [+0.006, +0.059] | +0.031 | no |
| gbm_funding (#634) | 2 | +0.068 [+0.030, +0.118] | +0.078 | no |
| gbm_funding (#634) | 3 | +0.077 [+0.035, +0.125] | +0.075 | yes |
| gbm_funding (#634) | 4 | +0.073 [+0.028, +0.127] | +0.063 | yes |
| gbm_funding (#634) | 5 | +0.096 [+0.037, +0.169] | +0.068 | yes |
