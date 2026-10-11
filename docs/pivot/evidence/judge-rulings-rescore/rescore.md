## Weighted rule in force

Tier 1 at lead of at least 1, pooled: a day flagged at any horizon is one false alarm. The limit reads the weighted count. Then tier 3 (calibration tested only in regimes with at least 20 pressure days), tier 5 and the full rule.

| row | onsets warned | recall [90%] | false alarms per onset, flat | weighted | tier 1 | tier 3 | tier 5 | full rule |
|---|---|---|---|---|---|---|---|---|
| **The five risk-date passers** | | | | | | | | |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 2.12 | 1.48 | pass | fail | fail | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 2.19 | 1.59 | pass | fail | fail | fail |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 3.31 | 2.55 | fail | fail | fail | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 2.88 | 2.18 | fail | fail | fail | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 2.88 | 2.14 | fail | fail | fail | fail |
| **The six best-recall rows (#461)** | | | | | | | | |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 7.31 | 3.74 | fail | fail | fail | fail |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 5.31 | 2.34 | fail | fail | fail | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 7.15 | 3.38 | fail | pass | fail | fail |
| settlement_quantile_timing | 16 of 26 | 0.615 [0.444, 0.778] | 10.00 | 5.59 | fail | fail | pass | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 6.54 | 3.01 | fail | pass | fail | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 6.12 | 2.87 | fail | pass | fail | fail |
| **The `+gate` rows (#534)** | | | | | | | | |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.481, 0.818] | 7.35 | 3.67 | fail | fail | fail | fail |
| risk_gbm_base+every_day+gate | 18 of 26 | 0.692 [0.517, 0.850] | 7.27 | 3.64 | fail | fail | fail | fail |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.520, 0.857] | 8.00 | 4.12 | fail | fail | fail | fail |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.815] | 8.04 | 4.12 | fail | fail | fail | fail |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.467, 0.824] | 7.69 | 3.90 | fail | fail | pass | fail |
| **The benchmarks** | | | | | | | | |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 6.85 | 3.90 | fail | fail | fail | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 8.46 | 4.09 | fail | fail | fail | fail |

### Tier 1 at each lead alone

Onsets warned by that horizon alone / false alarms per onset that horizon raises (weighted count) and the tier 1 verdict at that lead.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm | 13 / 0.80 pass | 8 / 0.68 fail | 7 / 0.59 fail | 7 / 0.47 fail | 7 / 0.76 fail |
| risk_gbm_base | 14 / 0.97 pass | 8 / 0.64 fail | 7 / 0.91 fail | 7 / 0.66 fail | 7 / 0.76 fail |
| risk_logistic | 14 / 1.74 pass | 7 / 1.28 fail | 8 / 1.34 fail | 10 / 1.71 fail | 9 / 1.58 fail |
| risk_logistic_base | 14 / 1.65 pass | 8 / 1.22 fail | 7 / 1.16 fail | 7 / 1.01 fail | 8 / 1.47 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | 9 / 1.44 fail | 9 / 1.00 fail | 9 / 0.56 fail | 9 / 0.51 fail |
| two_part_gbm | 9 / 0.78 fail | 7 / 1.69 fail | 12 / 1.74 fail | 6 / 0.90 fail | 8 / 2.55 fail |
| ngboost_laplace | 15 / 1.41 pass | 7 / 1.42 fail | 9 / 1.29 fail | 9 / 1.60 fail | 10 / 1.73 fail |
| hierarchical_logistic | 13 / 2.31 fail | 11 / 1.75 fail | 11 / 1.62 fail | 11 / 2.06 fail | 13 / 2.91 fail |
| settlement_quantile_timing | 13 / 3.12 fail | 11 / 3.13 fail | 11 / 2.99 fail | 11 / 3.32 fail | 12 / 3.41 fail |
| scarcity_logistic_interactions | 14 / 2.39 fail | 11 / 1.75 fail | 11 / 1.62 fail | 11 / 2.04 fail | 11 / 2.09 fail |
| scarcity_logistic | 13 / 2.05 fail | 11 / 1.75 fail | 11 / 1.62 fail | 11 / 2.04 fail | 11 / 2.09 fail |
| risk_gbm+every_day+gate | 13 / 1.62 pass | 9 / 1.63 fail | 8 / 1.58 fail | 9 / 1.48 fail | 11 / 1.61 fail |
| risk_gbm_base+every_day+gate | 13 / 1.57 pass | 9 / 1.56 fail | 8 / 1.60 fail | 9 / 1.61 fail | 10 / 1.62 fail |
| risk_logistic+every_day+gate | 12 / 1.79 fail | 8 / 1.60 fail | 8 / 1.58 fail | 8 / 1.89 fail | 12 / 2.19 fail |
| risk_logistic_base+every_day+gate | 13 / 2.01 fail | 9 / 1.56 fail | 9 / 1.67 fail | 9 / 1.71 fail | 13 / 1.91 pass |
| risk_quantile_skewt_base+every_day+gate | 13 / 1.87 pass | 8 / 1.46 fail | 10 / 1.76 fail | 10 / 1.87 fail | 13 / 2.00 pass |
| calendar_climatology | 12 / 3.75 fail | 10 / 3.17 fail | 10 / 3.21 fail | 10 / 3.25 fail | 10 / 3.29 fail |
| persistence_logistic | 11 / 3.25 fail | 7 / 2.07 fail | 10 / 2.68 fail | 8 / 2.38 fail | 8 / 1.86 fail |

### Inside and outside 2018-19, and the recall with equal weight per regime

Reported, not part of the pass rule. Recall with its 90% interval; false alarms per onset (weighted) with its interval where the onset count allows one.

| row | inside: warned | recall [90%] | false alarms per onset [90%] | outside: warned | recall [90%] | false alarms per onset [90%] | equal-weight recall by regime |
|---|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.364, 0.800] | 0.62 [0.32, 1.17] | 3 of 9 | 0.333 [0.000, 0.625] | 3.11 [1.48, 7.57] | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm_base | 10 of 17 | 0.588 [0.364, 0.818] | 0.68 [0.31, 1.29] | 4 of 9 | 0.444 [0.125, 0.750] | 3.31 [1.48, 8.00] | 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic | 10 of 17 | 0.588 [0.360, 0.818] | 0.71 [0.36, 1.34] | 6 of 9 | 0.667 (no interval) | 6.03 (no interval) | 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5) |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.812] | 0.71 [0.35, 1.35] | 5 of 9 | 0.556 (no interval) | 4.97 (no interval) | 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5) |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.364, 0.810] | 0.53 [0.25, 0.97] | 5 of 9 | 0.556 (no interval) | 5.19 (no interval) | 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5) |
| two_part_gbm | 12 of 17 | 0.706 [0.483, 0.923] | 3.46 [2.12, 5.38] | 3 of 9 | 0.333 (no interval) | 4.28 (no interval) | 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5) |
| ngboost_laplace | 12 of 17 | 0.706 [0.500, 0.923] | 3.26 [2.04, 5.32] | 5 of 9 | 0.556 (no interval) | 0.58 (no interval) | 0.426 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 5/5) |
| hierarchical_logistic | 12 of 17 | 0.706 [0.500, 0.909] | 3.88 [2.40, 6.15] | 3 of 9 | 0.333 (no interval) | 2.42 (no interval) | 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| settlement_quantile_timing | 14 of 17 | 0.824 [0.632, 1.000] | 3.65 [2.25, 5.73] | 2 of 9 | 0.222 (no interval) | 9.25 (no interval) | 0.381 (2018-19 14/17, 2020 1/2, 2024 0/2, 2025-26 1/5) |
| scarcity_logistic_interactions | 12 of 17 | 0.706 [0.500, 0.923] | 3.72 [2.21, 6.17] | 2 of 9 | 0.222 [0.000, 0.556] | 1.67 [0.58, 4.31] | 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5) |
| scarcity_logistic | 10 of 17 | 0.588 [0.357, 0.833] | 3.51 [2.02, 5.88] | 3 of 9 | 0.333 (no interval) | 1.64 (no interval) | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm+every_day+gate | 13 of 17 | 0.765 [0.538, 1.000] | 2.13 [1.36, 3.32] | 4 of 9 | 0.444 (no interval) | 6.58 (no interval) | 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm_base+every_day+gate | 13 of 17 | 0.765 [0.529, 1.000] | 2.19 [1.42, 3.57] | 5 of 9 | 0.556 (no interval) | 6.39 (no interval) | 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic+every_day+gate | 13 of 17 | 0.765 [0.533, 1.000] | 2.75 [1.81, 4.17] | 5 of 9 | 0.556 (no interval) | 6.69 (no interval) | 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic_base+every_day+gate | 13 of 17 | 0.765 [0.545, 1.000] | 2.75 [1.79, 4.25] | 4 of 9 | 0.444 (no interval) | 6.72 (no interval) | 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| risk_quantile_skewt_base+every_day+gate | 13 of 17 | 0.765 [0.538, 1.000] | 2.50 [1.63, 3.95] | 4 of 9 | 0.444 [0.167, 0.714] | 6.56 [3.89, 15.38] | 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| calendar_climatology | 12 of 17 | 0.706 [0.500, 0.923] | 3.32 [2.03, 5.58] | 0 of 9 | 0.000 (no interval) | 5.00 (no interval) | 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5) |
| persistence_logistic | 11 of 17 | 0.647 [0.400, 0.880] | 3.71 [2.21, 6.08] | 1 of 9 | 0.111 (no interval) | 4.81 (no interval) | 0.287 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 0/5) |

### Tier 3: the regimes tested

Pressure days (+5 bp) in each regime at h = 1; a regime is tested when it has at least 20. "ok" is that the regime's calibration interval covers zero.

| row | tested (pressure days, ok) at h = 1 | reported only (pressure days) | tier 3 at each horizon |
|---|---|---|---|
| risk_gbm | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_gbm_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_quantile_skewt_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| two_part_gbm | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / fail / fail / fail / fail |
| ngboost_laplace | 2018-19 (102, ok), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| hierarchical_logistic | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| settlement_quantile_timing | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| scarcity_logistic_interactions | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| scarcity_logistic | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| risk_gbm+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_gbm_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_quantile_skewt_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| calendar_climatology | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| persistence_logistic | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |

## Flat rule (for scale)

Tier 1 at lead of at least 1, pooled: a day flagged at any horizon is one false alarm. The limit reads the flat count. Then tier 3 (calibration tested only in regimes with at least 20 pressure days), tier 5 and the full rule.

| row | onsets warned | recall [90%] | false alarms per onset, flat | weighted | tier 1 | tier 3 | tier 5 | full rule |
|---|---|---|---|---|---|---|---|---|
| **The five risk-date passers** | | | | | | | | |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 2.00 | 1.37 | pass | fail | fail | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 2.04 | 1.43 | fail | fail | fail | fail |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 2.42 | 1.75 | fail | fail | fail | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 2.04 | 1.41 | fail | fail | fail | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 2.54 | 1.80 | fail | fail | fail | fail |
| **The six best-recall rows (#461)** | | | | | | | | |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 4.12 | 1.73 | fail | fail | fail | fail |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 4.38 | 1.84 | fail | fail | fail | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 5.27 | 2.05 | fail | pass | fail | fail |
| settlement_quantile_timing | 15 of 26 | 0.577 [0.391, 0.750] | 7.04 | 3.38 | fail | fail | pass | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 4.92 | 1.90 | fail | pass | fail | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 4.54 | 1.77 | fail | pass | fail | fail |
| **The `+gate` rows (#534)** | | | | | | | | |
| risk_gbm+every_day+gate | 16 of 26 | 0.615 [0.444, 0.778] | 5.65 | 2.56 | fail | fail | fail | fail |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.400, 0.750] | 5.77 | 2.58 | fail | fail | fail | fail |
| risk_logistic+every_day+gate | 14 of 26 | 0.538 [0.370, 0.720] | 5.35 | 2.44 | fail | fail | fail | fail |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.368, 0.714] | 4.96 | 2.14 | fail | fail | fail | fail |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.741] | 5.00 | 2.22 | fail | fail | pass | fail |
| **The benchmarks** | | | | | | | | |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 5.38 | 2.98 | fail | fail | fail | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 5.73 | 2.23 | fail | fail | fail | fail |

### Tier 1 at each lead alone

Onsets warned by that horizon alone / false alarms per onset that horizon raises (flat count) and the tier 1 verdict at that lead.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm | 13 / 1.35 pass | 8 / 1.08 fail | 7 / 1.04 fail | 7 / 0.88 fail | 7 / 1.04 fail |
| risk_gbm_base | 13 / 1.50 pass | 8 / 0.96 fail | 7 / 1.27 fail | 7 / 1.12 fail | 7 / 1.08 fail |
| risk_logistic | 13 / 1.85 pass | 7 / 1.00 fail | 7 / 1.19 fail | 9 / 1.54 fail | 8 / 1.42 fail |
| risk_logistic_base | 13 / 1.77 pass | 6 / 1.00 fail | 6 / 1.00 fail | 7 / 1.12 fail | 8 / 1.15 fail |
| risk_quantile_skewt_base | 13 / 1.88 pass | 9 / 1.65 fail | 9 / 1.50 fail | 9 / 1.12 fail | 9 / 1.04 fail |
| two_part_gbm | 9 / 0.23 fail | 1 / 1.15 fail | 4 / 1.58 fail | 6 / 1.35 fail | 5 / 2.46 fail |
| ngboost_laplace | 10 / 1.69 fail | 3 / 1.73 fail | 3 / 1.42 fail | 6 / 2.54 fail | 2 / 1.58 fail |
| hierarchical_logistic | 13 / 3.08 fail | 8 / 1.81 fail | 8 / 3.15 fail | 11 / 3.00 fail | 12 / 3.65 fail |
| settlement_quantile_timing | 10 / 2.92 fail | 5 / 2.69 fail | 9 / 3.50 fail | 8 / 3.54 fail | 9 / 3.65 fail |
| scarcity_logistic_interactions | 14 / 3.19 fail | 8 / 2.00 fail | 8 / 3.15 fail | 11 / 3.00 fail | 10 / 3.23 fail |
| scarcity_logistic | 13 / 2.85 fail | 8 / 2.00 fail | 8 / 3.15 fail | 11 / 3.00 fail | 10 / 3.23 fail |
| risk_gbm+every_day+gate | 12 / 0.85 fail | 8 / 2.54 fail | 8 / 2.96 fail | 7 / 2.15 fail | 8 / 2.42 fail |
| risk_gbm_base+every_day+gate | 10 / 2.50 fail | 7 / 2.62 fail | 8 / 2.88 fail | 7 / 2.15 fail | 7 / 2.35 fail |
| risk_logistic+every_day+gate | 8 / 2.35 fail | 6 / 1.54 fail | 6 / 1.58 fail | 5 / 1.19 fail | 8 / 3.00 fail |
| risk_logistic_base+every_day+gate | 8 / 1.73 fail | 5 / 1.38 fail | 7 / 1.62 fail | 6 / 1.50 fail | 9 / 2.88 fail |
| risk_quantile_skewt_base+every_day+gate | 9 / 2.31 fail | 3 / 1.23 fail | 8 / 1.85 fail | 9 / 2.15 fail | 12 / 3.15 fail |
| calendar_climatology | 9 / 4.85 fail | 10 / 4.88 fail | 10 / 4.92 fail | 10 / 4.96 fail | 10 / 5.00 fail |
| persistence_logistic | 4 / 2.77 fail | 6 / 3.42 fail | 6 / 2.81 fail | 6 / 3.15 fail | 5 / 2.81 fail |

### Inside and outside 2018-19, and the recall with equal weight per regime

Reported, not part of the pass rule. Recall with its 90% interval; false alarms per onset (flat) with its interval where the onset count allows one.

| row | inside: warned | recall [90%] | false alarms per onset [90%] | outside: warned | recall [90%] | false alarms per onset [90%] | equal-weight recall by regime |
|---|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.364, 0.800] | 1.35 [0.80, 2.25] | 3 of 9 | 0.333 [0.000, 0.625] | 3.22 [1.62, 7.33] | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm_base | 10 of 17 | 0.588 [0.364, 0.818] | 1.41 [0.80, 2.42] | 4 of 9 | 0.444 [0.125, 0.750] | 3.22 [1.50, 7.40] | 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic | 10 of 17 | 0.588 [0.360, 0.818] | 1.47 [0.88, 2.46] | 4 of 9 | 0.444 (no interval) | 4.22 (no interval) | 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.812] | 1.47 [0.86, 2.46] | 3 of 9 | 0.333 (no interval) | 3.11 (no interval) | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.364, 0.810] | 1.29 [0.73, 2.09] | 4 of 9 | 0.444 (no interval) | 4.89 (no interval) | 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5) |
| two_part_gbm | 12 of 17 | 0.706 [0.483, 0.923] | 5.53 [3.44, 8.36] | 3 of 9 | 0.333 (no interval) | 1.44 (no interval) | 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5) |
| ngboost_laplace | 11 of 17 | 0.647 [0.421, 0.875] | 6.53 [4.22, 10.14] | 4 of 9 | 0.444 (no interval) | 0.33 (no interval) | 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5) |
| hierarchical_logistic | 12 of 17 | 0.706 [0.500, 0.909] | 7.00 [4.44, 10.89] | 3 of 9 | 0.333 (no interval) | 2.00 (no interval) | 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| settlement_quantile_timing | 14 of 17 | 0.824 [0.632, 1.000] | 5.94 [3.83, 9.12] | 1 of 9 | 0.111 (no interval) | 9.11 (no interval) | 0.256 (2018-19 14/17, 2020 0/2, 2024 0/2, 2025-26 1/5) |
| scarcity_logistic_interactions | 12 of 17 | 0.706 [0.500, 0.923] | 6.47 [3.94, 10.62] | 2 of 9 | 0.222 [0.000, 0.556] | 2.00 [0.67, 4.43] | 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5) |
| scarcity_logistic | 10 of 17 | 0.588 [0.357, 0.833] | 5.94 [3.39, 9.93] | 3 of 9 | 0.333 (no interval) | 1.89 (no interval) | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm+every_day+gate | 12 of 17 | 0.706 [0.500, 0.923] | 5.00 [3.00, 7.92] | 4 of 9 | 0.444 (no interval) | 6.89 (no interval) | 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm_base+every_day+gate | 12 of 17 | 0.706 [0.476, 0.923] | 5.00 [3.06, 8.17] | 3 of 9 | 0.333 (no interval) | 7.22 (no interval) | 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_logistic+every_day+gate | 12 of 17 | 0.706 [0.481, 0.920] | 4.82 [2.87, 7.67] | 2 of 9 | 0.222 (no interval) | 6.33 (no interval) | 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5) |
| risk_logistic_base+every_day+gate | 12 of 17 | 0.706 [0.500, 0.923] | 4.41 [2.67, 7.00] | 2 of 9 | 0.222 (no interval) | 6.00 (no interval) | 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5) |
| risk_quantile_skewt_base+every_day+gate | 12 of 17 | 0.706 [0.500, 0.917] | 4.76 [2.96, 7.58] | 3 of 9 | 0.333 [0.091, 0.571] | 5.44 [3.29, 11.67] | 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5) |
| calendar_climatology | 10 of 17 | 0.588 [0.333, 0.846] | 6.24 [3.68, 10.42] | 0 of 9 | 0.000 (no interval) | 3.78 (no interval) | 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5) |
| persistence_logistic | 7 of 17 | 0.412 [0.188, 0.667] | 6.18 [3.62, 10.18] | 0 of 9 | 0.000 (no interval) | 4.89 (no interval) | 0.103 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 0/5) |

### Tier 3: the regimes tested

Pressure days (+5 bp) in each regime at h = 1; a regime is tested when it has at least 20. "ok" is that the regime's calibration interval covers zero.

| row | tested (pressure days, ok) at h = 1 | reported only (pressure days) | tier 3 at each horizon |
|---|---|---|---|
| risk_gbm | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_gbm_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_quantile_skewt_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| two_part_gbm | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / fail / fail / fail / fail |
| ngboost_laplace | 2018-19 (102, ok), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| hierarchical_logistic | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| settlement_quantile_timing | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| scarcity_logistic_interactions | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| scarcity_logistic | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| risk_gbm+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_gbm_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_quantile_skewt_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| calendar_climatology | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| persistence_logistic | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |

## Cross-check against readings (b) and (e) of #523

Where the new rules coincide with readings (b1) (each horizon alone), (b2) (pooled) and (e) (onsets warned and recall outside 2018-19), the figures reproduce. 546 of 546 compared figures agree to 1e-6 over the 13 rows both pages score, under both rules.

