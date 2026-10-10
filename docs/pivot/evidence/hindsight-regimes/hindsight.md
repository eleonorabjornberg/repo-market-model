# What the hindsight regime labels contribute (#515)

Onsets flagged of 26 at some horizon 1 to 5 (+5 bp), worst false alarms per onset (the weighted column is the weighted count), tiers 1, 3 and 5, and
onsets flagged by calendar year of the onset under the flat rule.

## Table 1. The calibrated stack, the regime term as declared, removed, and replaced by the as-of scarcity state

| form | flagged, flat | worst FA per onset, flat | tiers 1 / 3 / 5, flat | flagged, weighted | worst FA per onset, weighted count | tiers 1 / 3 / 5, weighted | recall by year, flat rule: 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| calibrated_stack_logistic / declared | 14 of 26 | 3.88 | fail / fail / fail | 15 of 26 | 2.50 | fail / fail / fail | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| calibrated_stack_logistic / no regime | 16 of 26 | 4.65 | fail / fail / pass | 16 of 26 | 3.54 | fail / fail / pass | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| calibrated_stack_logistic / scarcity | 16 of 26 | 3.88 | fail / fail / fail | 16 of 26 | 2.65 | fail / fail / fail | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| calibrated_stack_isotonic / declared | 11 of 26 | 3.04 | fail / fail / fail | 12 of 26 | 2.05 | fail / fail / fail | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| calibrated_stack_isotonic / no regime | 12 of 26 | 3.04 | fail / fail / pass | 13 of 26 | 2.20 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| calibrated_stack_isotonic / scarcity | 11 of 26 | 3.04 | fail / fail / pass | 12 of 26 | 2.12 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |

## Table 2. The per-regime recalibration of each passer: raw, by the declared regime, with no group, and by the as-of scarcity state

| form | flagged, flat | worst FA per onset, flat | tiers 1 / 3 / 5, flat | flagged, weighted | worst FA per onset, weighted count | tiers 1 / 3 / 5, weighted | recall by year, flat rule: 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm / raw | 13 of 26 | 1.35 | pass / fail / fail | 13 of 26 | 0.80 | pass / fail / fail | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm / regime (declared) | 13 of 26 | 2.62 | fail / fail / pass | 13 of 26 | 2.67 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm / no group | 12 of 26 | 3.38 | fail / fail / pass | 12 of 26 | 3.37 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| risk_gbm / scarcity | 12 of 26 | 3.38 | fail / fail / pass | 13 of 26 | 3.17 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| risk_gbm_base / raw | 14 of 26 | 1.50 | pass / fail / fail | 14 of 26 | 0.97 | pass / fail / fail | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_gbm_base / regime (declared) | 13 of 26 | 2.58 | fail / fail / pass | 13 of 26 | 1.87 | pass / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm_base / no group | 12 of 26 | 3.42 | fail / fail / pass | 13 of 26 | 2.70 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| risk_gbm_base / scarcity | 13 of 26 | 3.42 | fail / fail / pass | 13 of 26 | 2.69 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_logistic / raw | 14 of 26 | 1.85 | pass / fail / fail | 16 of 26 | 1.74 | pass / fail / fail | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic / regime (declared) | 14 of 26 | 2.92 | fail / fail / pass | 14 of 26 | 2.42 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_logistic / no group | 11 of 26 | 2.88 | fail / fail / pass | 11 of 26 | 2.90 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_logistic / scarcity | 12 of 26 | 2.92 | fail / fail / pass | 12 of 26 | 2.91 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| risk_logistic_base / raw | 13 of 26 | 1.77 | pass / fail / fail | 15 of 26 | 1.65 | pass / fail / fail | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_logistic_base / regime (declared) | 13 of 26 | 2.35 | fail / fail / pass | 13 of 26 | 1.88 | pass / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_logistic_base / no group | 11 of 26 | 2.46 | fail / fail / pass | 11 of 26 | 2.31 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_logistic_base / scarcity | 12 of 26 | 2.46 | fail / fail / pass | 12 of 26 | 2.31 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 1 of 5 |
| risk_quantile_skewt_base / raw | 14 of 26 | 1.88 | pass / fail / fail | 15 of 26 | 1.62 | pass / fail / fail | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_quantile_skewt_base / regime (declared) | 13 of 26 | 2.65 | fail / fail / pass | 13 of 26 | 1.79 | pass / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_quantile_skewt_base / no group | 11 of 26 | 2.65 | fail / fail / pass | 11 of 26 | 2.45 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_quantile_skewt_base / scarcity | 13 of 26 | 2.65 | fail / fail / pass | 13 of 26 | 2.47 | fail / fail / pass | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |

The declared stack's regime coefficients (h = 1, +5 bp): over its 83 fitted refits the mean is 2018-19 +1.88, 2020 -0.47, 2021-23 -1.26, 2024 -0.09, 2025-26 -0.05; over the 11 fitted refits before 2020 the largest absolute coefficient is 0.00.
