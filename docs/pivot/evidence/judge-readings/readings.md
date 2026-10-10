# Tier 1 under the readings the audit questioned (#523)

## Unweighted rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 1.35 | 1.35 | 0.76 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 | 1.50 | 0.97 | pass |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 1.85 | 1.85 | 1.19 | pass |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 1.77 | 1.77 | 1.16 | pass |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 1.88 | 1.88 | 1.25 | pass |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 2.46 | 2.46 | 1.07 | fail |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 2.54 | 2.54 | 1.03 | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 3.65 | 3.65 | 1.31 | fail |
| settlement_quantile_timing | 15 of 26 | 0.577 [0.391, 0.750] | 3.65 | 3.65 | 1.68 | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 3.23 | 3.23 | 1.23 | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 3.23 | 3.23 | 1.23 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 5.00 | 5.00 | 2.80 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 3.42 | 3.42 | 1.17 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 2.00 | 2.00 | 1.37 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 2.04 | 2.04 | 1.43 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.364, 0.710] | 2.42 | 2.42 | 1.75 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.320, 0.677] | 2.04 | 2.04 | 1.41 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.364, 0.720] | 2.54 | 2.54 | 1.80 | fail |
| two_part_gbm | 15 of 26 | 0.577 [0.375, 0.750] | 4.12 | 4.12 | 1.73 | fail |
| ngboost_laplace | 15 of 26 | 0.577 [0.393, 0.765] | 4.38 | 4.38 | 1.84 | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.407, 0.750] | 5.27 | 5.27 | 2.05 | fail |
| settlement_quantile_timing | 15 of 26 | 0.577 [0.400, 0.750] | 7.04 | 7.04 | 3.38 | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 4.92 | 4.92 | 1.90 | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.316, 0.700] | 4.54 | 4.54 | 1.77 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.572] | 5.38 | 5.38 | 2.98 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.107, 0.452] | 5.73 | 5.73 | 2.23 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.56 | 1.56 | 1.17 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.00 | 2.00 | 1.72 | fail |
| risk_logistic | 4 of 9 | 0.444 [0.111, 0.750] | 2.89 | 2.89 | 2.56 | fail |
| risk_logistic_base | 3 of 9 | 0.333 [–, –] | 2.33 | 2.33 | 2.03 | fail |
| risk_quantile_skewt_base | 4 of 9 | 0.444 [–, –] | 3.22 | 3.22 | 2.75 | fail |
| two_part_gbm | 3 of 9 | 0.333 [0.000, 0.626] | 0.44 | 0.44 | 0.36 | fail |
| ngboost_laplace | 4 of 9 | 0.444 [–, –] | 0.33 | 0.33 | 0.17 | fail |
| hierarchical_logistic | 3 of 9 | 0.333 [–, –] | 1.44 | 1.44 | 0.50 | fail |
| settlement_quantile_timing | 1 of 9 | 0.111 [–, –] | 4.44 | 4.44 | 3.11 | fail |
| scarcity_logistic_interactions | 2 of 9 | 0.222 [–, –] | 1.44 | 1.44 | 0.42 | fail |
| scarcity_logistic | 3 of 9 | 0.333 [–, –] | 1.44 | 1.44 | 0.50 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 3.78 | 3.78 | 3.67 | fail |
| persistence_logistic | 0 of 9 | 0.000 [0.000, 0.000] | 2.22 | 2.22 | 0.83 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 1.24 | 1.24 | 0.54 | pass |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 1.24 | 1.24 | 0.59 | pass |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.18 | 1.18 | 0.46 | pass |
| two_part_gbm | 12 of 17 | 0.706 [0.471, 0.909] | 3.53 | 3.53 | 1.44 | fail |
| ngboost_laplace | 11 of 17 | 0.647 [0.421, 0.846] | 3.88 | 3.88 | 1.57 | fail |
| hierarchical_logistic | 12 of 17 | 0.706 [0.500, 0.923] | 5.35 | 5.35 | 1.91 | fail |
| settlement_quantile_timing | 14 of 17 | 0.824 [0.647, 1.000] | 3.71 | 3.71 | 1.28 | fail |
| scarcity_logistic_interactions | 12 of 17 | 0.706 [0.471, 0.917] | 4.71 | 4.71 | 1.85 | fail |
| scarcity_logistic | 10 of 17 | 0.588 [0.357, 0.818] | 4.71 | 4.71 | 1.85 | fail |
| calendar_climatology | 10 of 17 | 0.588 [0.353, 0.812] | 5.65 | 5.65 | 2.34 | fail |
| persistence_logistic | 7 of 17 | 0.412 [0.185, 0.647] | 4.24 | 4.24 | 1.46 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 1.35 | 8 / 1.08 | 7 / 1.04 | 7 / 0.88 | 7 / 1.04 | pass (h = 1) |
| risk_gbm_base | 13 / 1.50 | 8 / 0.96 | 7 / 1.27 | 7 / 1.12 | 7 / 1.08 | pass (h = 1) |
| risk_logistic | 13 / 1.85 | 7 / 1.00 | 7 / 1.19 | 9 / 1.54 | 8 / 1.42 | pass (h = 1) |
| risk_logistic_base | 13 / 1.77 | 6 / 1.00 | 6 / 1.00 | 7 / 1.12 | 8 / 1.15 | pass (h = 1) |
| risk_quantile_skewt_base | 13 / 1.88 | 9 / 1.65 | 9 / 1.50 | 9 / 1.12 | 9 / 1.04 | pass (h = 1) |
| two_part_gbm | 9 / 0.23 | 1 / 1.15 | 4 / 1.58 | 6 / 1.35 | 5 / 2.46 | fail |
| ngboost_laplace | 10 / 1.69 | 3 / 1.73 | 3 / 1.42 | 6 / 2.54 | 2 / 1.58 | fail |
| hierarchical_logistic | 13 / 3.08 | 8 / 1.81 | 8 / 3.15 | 11 / 3.00 | 12 / 3.65 | fail |
| settlement_quantile_timing | 10 / 2.92 | 5 / 2.69 | 9 / 3.50 | 8 / 3.54 | 9 / 3.65 | fail |
| scarcity_logistic_interactions | 14 / 3.19 | 8 / 2.00 | 8 / 3.15 | 11 / 3.00 | 10 / 3.23 | fail |
| scarcity_logistic | 13 / 2.85 | 8 / 2.00 | 8 / 3.15 | 11 / 3.00 | 10 / 3.23 | fail |
| calendar_climatology | 9 / 4.85 | 10 / 4.88 | 10 / 4.92 | 10 / 4.96 | 10 / 5.00 | fail |
| persistence_logistic | 4 / 2.77 | 6 / 3.42 | 6 / 2.81 | 6 / 3.15 | 5 / 2.81 | fail |

## Weighted rule in force

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.80 | 1.38 | 0.80 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.97 | 1.50 | 0.97 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 1.74 | 2.42 | 1.74 | pass |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 1.65 | 2.31 | 1.65 | pass |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 1.62 | 2.31 | 1.62 | pass |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 2.55 | 4.81 | 2.55 | fail |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 1.73 | 4.08 | 1.73 | pass |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 2.91 | 6.23 | 2.91 | fail |
| settlement_quantile_timing | 16 of 26 | 0.615 [0.444, 0.778] | 3.41 | 6.38 | 3.41 | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 2.39 | 5.50 | 2.39 | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 2.09 | 4.73 | 2.09 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 3.75 | 6.69 | 3.75 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 3.25 | 7.04 | 3.25 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 1.48 | 2.12 | 1.48 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 1.59 | 2.19 | 1.59 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.440, 0.800] | 2.55 | 3.31 | 2.55 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.759] | 2.18 | 2.88 | 2.18 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.400, 0.759] | 2.14 | 2.88 | 2.14 | fail |
| two_part_gbm | 15 of 26 | 0.577 [0.375, 0.750] | 3.74 | 7.31 | 3.74 | fail |
| ngboost_laplace | 17 of 26 | 0.654 [0.454, 0.840] | 2.34 | 5.31 | 2.34 | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.407, 0.750] | 3.38 | 7.15 | 3.38 | fail |
| settlement_quantile_timing | 16 of 26 | 0.615 [0.444, 0.783] | 5.59 | 10.00 | 5.59 | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 3.01 | 6.54 | 3.01 | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.316, 0.700] | 2.87 | 6.12 | 2.87 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.278, 0.650] | 3.90 | 6.85 | 3.90 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.276, 0.667] | 4.09 | 8.46 | 4.09 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.61 | 1.89 | 1.61 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.06 | 2.33 | 2.06 | fail |
| risk_logistic | 6 of 9 | 0.667 [0.307, 1.000] | 4.39 | 4.89 | 4.39 | fail |
| risk_logistic_base | 5 of 9 | 0.556 [–, –] | 3.67 | 4.00 | 3.67 | fail |
| risk_quantile_skewt_base | 5 of 9 | 0.556 [–, –] | 3.81 | 4.44 | 3.81 | fail |
| two_part_gbm | 3 of 9 | 0.333 [0.000, 0.626] | 2.89 | 3.11 | 2.89 | fail |
| ngboost_laplace | 5 of 9 | 0.556 [–, –] | 0.50 | 0.67 | 0.50 | fail |
| hierarchical_logistic | 3 of 9 | 0.333 [–, –] | 1.69 | 3.11 | 1.69 | fail |
| settlement_quantile_timing | 2 of 9 | 0.222 [–, –] | 4.97 | 6.89 | 4.97 | fail |
| scarcity_logistic_interactions | 2 of 9 | 0.222 [–, –] | 0.94 | 1.89 | 0.94 | fail |
| scarcity_logistic | 3 of 9 | 0.333 [–, –] | 0.94 | 1.89 | 0.94 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 4.56 | 4.67 | 4.56 | fail |
| persistence_logistic | 1 of 9 | 0.111 [0.000, 0.333] | 2.86 | 4.89 | 2.86 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 0.54 | 1.24 | 0.54 | pass |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 0.59 | 1.24 | 0.59 | pass |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.46 | 1.18 | 0.46 | pass |
| two_part_gbm | 12 of 17 | 0.706 [0.471, 0.909] | 2.37 | 5.71 | 2.37 | fail |
| ngboost_laplace | 12 of 17 | 0.706 [0.476, 0.917] | 2.65 | 6.24 | 2.65 | fail |
| hierarchical_logistic | 12 of 17 | 0.706 [0.500, 0.923] | 3.81 | 8.59 | 3.81 | fail |
| settlement_quantile_timing | 14 of 17 | 0.824 [0.647, 1.000] | 2.68 | 6.65 | 2.68 | fail |
| scarcity_logistic_interactions | 12 of 17 | 0.706 [0.471, 0.917] | 3.21 | 7.41 | 3.21 | fail |
| scarcity_logistic | 10 of 17 | 0.588 [0.357, 0.818] | 2.94 | 6.53 | 2.94 | fail |
| calendar_climatology | 12 of 17 | 0.706 [0.474, 0.900] | 3.32 | 7.76 | 3.32 | fail |
| persistence_logistic | 11 of 17 | 0.647 [0.412, 0.889] | 3.54 | 8.18 | 3.54 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 0.80 | 8 / 0.68 | 7 / 0.59 | 7 / 0.47 | 7 / 0.76 | pass (h = 1) |
| risk_gbm_base | 14 / 0.97 | 8 / 0.64 | 7 / 0.91 | 7 / 0.66 | 7 / 0.76 | pass (h = 1) |
| risk_logistic | 14 / 1.74 | 7 / 1.28 | 8 / 1.34 | 10 / 1.71 | 9 / 1.58 | pass (h = 1) |
| risk_logistic_base | 14 / 1.65 | 8 / 1.22 | 7 / 1.16 | 7 / 1.01 | 8 / 1.47 | pass (h = 1) |
| risk_quantile_skewt_base | 15 / 1.62 | 9 / 1.44 | 9 / 1.00 | 9 / 0.56 | 9 / 0.51 | pass (h = 1) |
| two_part_gbm | 9 / 0.78 | 7 / 1.69 | 12 / 1.74 | 6 / 0.90 | 8 / 2.55 | fail |
| ngboost_laplace | 15 / 1.41 | 7 / 1.42 | 9 / 1.29 | 9 / 1.60 | 10 / 1.73 | pass (h = 1) |
| hierarchical_logistic | 13 / 2.31 | 11 / 1.75 | 11 / 1.62 | 11 / 2.06 | 13 / 2.91 | fail |
| settlement_quantile_timing | 13 / 3.12 | 11 / 3.13 | 11 / 2.99 | 11 / 3.32 | 12 / 3.41 | fail |
| scarcity_logistic_interactions | 14 / 2.39 | 11 / 1.75 | 11 / 1.62 | 11 / 2.04 | 11 / 2.09 | fail |
| scarcity_logistic | 13 / 2.05 | 11 / 1.75 | 11 / 1.62 | 11 / 2.04 | 11 / 2.09 | fail |
| calendar_climatology | 12 / 3.75 | 10 / 3.17 | 10 / 3.21 | 10 / 3.25 | 10 / 3.29 | fail |
| persistence_logistic | 11 / 3.25 | 7 / 2.07 | 10 / 2.68 | 8 / 2.38 | 8 / 1.86 | fail |

## (d) weighted rule, discount for alarms before an episode only

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.95 | 1.38 | 0.95 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 1.08 | 1.50 | 1.08 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 1.90 | 2.42 | 1.90 | pass |
| risk_logistic_base | 14 of 26 | 0.538 [0.360, 0.714] | 1.78 | 2.27 | 1.78 | pass |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 1.81 | 2.31 | 1.81 | pass |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 2.22 | 3.42 | 2.22 | fail |
| ngboost_laplace | 16 of 26 | 0.615 [0.429, 0.793] | 2.23 | 3.46 | 2.23 | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 3.45 | 5.42 | 3.45 | fail |
| settlement_quantile_timing | 16 of 26 | 0.615 [0.444, 0.778] | 3.81 | 5.62 | 3.81 | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 2.53 | 4.19 | 2.53 | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 2.53 | 4.19 | 2.53 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 4.55 | 6.54 | 4.55 | fail |
| persistence_logistic | 10 of 26 | 0.385 [0.217, 0.556] | 3.23 | 5.15 | 3.23 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 1.64 | 2.12 | 1.64 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 1.72 | 2.19 | 1.72 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.440, 0.800] | 2.70 | 3.27 | 2.70 | fail |
| risk_logistic_base | 14 of 26 | 0.538 [0.360, 0.714] | 2.26 | 2.77 | 2.26 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.400, 0.759] | 2.22 | 2.77 | 2.22 | fail |
| two_part_gbm | 15 of 26 | 0.577 [0.375, 0.750] | 3.61 | 5.54 | 3.61 | fail |
| ngboost_laplace | 16 of 26 | 0.615 [0.429, 0.800] | 3.30 | 4.96 | 3.30 | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.407, 0.750] | 4.09 | 6.31 | 4.09 | fail |
| settlement_quantile_timing | 16 of 26 | 0.615 [0.444, 0.783] | 6.12 | 8.62 | 6.12 | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 3.23 | 5.23 | 3.23 | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.316, 0.700] | 2.96 | 4.85 | 2.96 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.278, 0.650] | 4.70 | 6.69 | 4.70 | fail |
| persistence_logistic | 10 of 26 | 0.385 [0.214, 0.571] | 4.50 | 6.96 | 4.50 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.78 | 1.89 | 1.78 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.22 | 2.33 | 2.22 | fail |
| risk_logistic | 6 of 9 | 0.667 [0.307, 1.000] | 4.31 | 4.56 | 4.31 | fail |
| risk_logistic_base | 4 of 9 | 0.444 [–, –] | 3.58 | 3.78 | 3.58 | fail |
| risk_quantile_skewt_base | 5 of 9 | 0.556 [–, –] | 4.14 | 4.44 | 4.14 | fail |
| two_part_gbm | 3 of 9 | 0.333 [0.000, 0.626] | 1.06 | 1.22 | 1.06 | fail |
| ngboost_laplace | 5 of 9 | 0.556 [–, –] | 0.58 | 0.67 | 0.58 | fail |
| hierarchical_logistic | 3 of 9 | 0.333 [–, –] | 1.19 | 1.67 | 1.19 | fail |
| settlement_quantile_timing | 2 of 9 | 0.222 [–, –] | 4.53 | 5.44 | 4.53 | fail |
| scarcity_logistic_interactions | 2 of 9 | 0.222 [–, –] | 1.08 | 1.56 | 1.08 | fail |
| scarcity_logistic | 3 of 9 | 0.333 [–, –] | 1.08 | 1.56 | 1.08 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 4.44 | 4.56 | 4.44 | fail |
| persistence_logistic | 1 of 9 | 0.111 [0.000, 0.333] | 1.75 | 2.56 | 1.75 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 0.65 | 1.24 | 0.65 | pass |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 0.66 | 1.24 | 0.66 | pass |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 0.82 | 1.47 | 0.82 | pass |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.82 | 1.47 | 0.82 | pass |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.57 | 1.18 | 0.57 | pass |
| two_part_gbm | 12 of 17 | 0.706 [0.471, 0.909] | 2.84 | 4.59 | 2.84 | fail |
| ngboost_laplace | 11 of 17 | 0.647 [0.421, 0.846] | 3.41 | 5.29 | 3.41 | fail |
| hierarchical_logistic | 12 of 17 | 0.706 [0.500, 0.923] | 5.04 | 8.00 | 5.04 | fail |
| settlement_quantile_timing | 14 of 17 | 0.824 [0.647, 1.000] | 3.46 | 5.71 | 3.46 | fail |
| scarcity_logistic_interactions | 12 of 17 | 0.706 [0.471, 0.917] | 3.57 | 6.12 | 3.57 | fail |
| scarcity_logistic | 10 of 17 | 0.588 [0.357, 0.818] | 3.57 | 6.12 | 3.57 | fail |
| calendar_climatology | 12 of 17 | 0.706 [0.474, 0.900] | 4.78 | 7.76 | 4.78 | fail |
| persistence_logistic | 9 of 17 | 0.529 [0.308, 0.769] | 4.41 | 7.18 | 4.41 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 0.95 | 8 / 0.82 | 7 / 0.72 | 7 / 0.61 | 7 / 0.89 | pass (h = 1) |
| risk_gbm_base | 13 / 1.08 | 8 / 0.78 | 7 / 1.05 | 7 / 0.80 | 7 / 0.89 | pass (h = 1) |
| risk_logistic | 14 / 1.90 | 7 / 1.18 | 8 / 1.34 | 10 / 1.76 | 9 / 1.77 | pass (h = 1) |
| risk_logistic_base | 14 / 1.78 | 7 / 1.30 | 7 / 1.14 | 7 / 1.03 | 8 / 1.34 | pass (h = 1) |
| risk_quantile_skewt_base | 15 / 1.81 | 9 / 1.52 | 9 / 1.16 | 9 / 0.69 | 9 / 0.64 | pass (h = 1) |
| two_part_gbm | 9 / 0.95 | 6 / 1.81 | 7 / 1.58 | 6 / 1.12 | 7 / 2.22 | fail |
| ngboost_laplace | 14 / 1.53 | 6 / 1.80 | 6 / 1.78 | 9 / 2.23 | 6 / 2.10 | pass (h = 1) |
| hierarchical_logistic | 13 / 2.37 | 11 / 2.55 | 11 / 2.36 | 11 / 2.32 | 13 / 3.45 | fail |
| settlement_quantile_timing | 12 / 2.90 | 10 / 2.97 | 10 / 3.23 | 11 / 3.79 | 12 / 3.81 | fail |
| scarcity_logistic_interactions | 14 / 2.38 | 11 / 2.53 | 11 / 2.36 | 11 / 2.30 | 11 / 2.28 | fail |
| scarcity_logistic | 13 / 2.15 | 11 / 2.53 | 11 / 2.36 | 11 / 2.30 | 11 / 2.28 | fail |
| calendar_climatology | 12 / 4.55 | 10 / 3.89 | 10 / 3.93 | 10 / 3.97 | 10 / 4.01 | fail |
| persistence_logistic | 7 / 3.16 | 6 / 2.15 | 9 / 3.23 | 7 / 2.73 | 8 / 2.62 | fail |

## (c) the cut-off rule's training-window check beside the realised count

### unweighted

| row | realised, worst horizon | check at the last refit | largest check | median check |
|---|---|---|---|---|
| risk_gbm | 1.35 | 2.00 (h = 1) | 2.00 | 2.00 |
| risk_gbm_base | 1.50 | 1.92 (h = 5) | 2.00 | 1.42 |
| risk_logistic | 1.85 | 1.96 (h = 2) | 2.00 | 1.95 |
| risk_logistic_base | 1.77 | 1.96 (h = 1) | 2.00 | 1.85 |
| risk_quantile_skewt_base | 1.88 | 1.92 (h = 1) | 2.00 | 1.89 |
| two_part_gbm | 2.46 | 1.92 (h = 3) | 2.00 | 1.11 |
| ngboost_laplace | 2.54 | 2.00 (h = 2) | 2.00 | 1.90 |
| hierarchical_logistic | 3.65 | 1.71 (h = 5) | 2.00 | 1.89 |
| settlement_quantile_timing | 3.65 | 1.96 (h = 1) | 2.00 | 1.95 |
| scarcity_logistic_interactions | 3.23 | 1.83 (h = 5) | 2.00 | 1.80 |
| scarcity_logistic | 3.23 | 1.83 (h = 5) | 2.00 | 1.75 |
| calendar_climatology | 5.00 | 1.88 (h = 5) | 2.00 | 1.75 |
| persistence_logistic | 3.42 | 2.00 (h = 3) | 2.00 | 1.95 |

### weighted

| row | realised, worst horizon | check at the last refit | largest check | median check |
|---|---|---|---|---|
| risk_gbm | 0.80 | 1.95 (h = 4) | 1.95 | 1.59 |
| risk_gbm_base | 0.97 | 1.77 (h = 1) | 1.98 | 1.91 |
| risk_logistic | 1.74 | 1.92 (h = 1) | 1.99 | 1.80 |
| risk_logistic_base | 1.65 | 1.85 (h = 3) | 1.99 | 1.62 |
| risk_quantile_skewt_base | 1.62 | 1.74 (h = 1) | 2.00 | 1.79 |
| two_part_gbm | 2.55 | 2.00 (h = 3) | 2.00 | 1.96 |
| ngboost_laplace | 1.73 | 1.64 (h = 2) | 2.00 | 1.95 |
| hierarchical_logistic | 2.91 | 1.96 (h = 5) | 2.00 | 1.86 |
| settlement_quantile_timing | 3.41 | 1.82 (h = 5) | 2.00 | 1.82 |
| scarcity_logistic_interactions | 2.39 | 1.44 (h = 2) | 2.00 | 1.80 |
| scarcity_logistic | 2.09 | 1.44 (h = 2) | 2.00 | 1.80 |
| calendar_climatology | 3.75 | 1.61 (h = 5) | 2.00 | 1.76 |
| persistence_logistic | 3.25 | 1.86 (h = 1) | 2.00 | 1.97 |

## The ceiling at lead of at least 2 (#511): the judge's own rows

### unweighted

| row | judge: lead >= 1 warned | judge: lead >= 3 warned | onsets on a risk date (grid label) | onsets forecast above 0 at some h >= 2 | flagged at h >= 2 (on / off a risk date) |
|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 7 of 26 | 20 of 26 | 13 of 26 | 8 (8 / 0) |
| risk_gbm_base | 14 of 26 | 7 of 26 | 20 of 26 | 13 of 26 | 8 (8 / 0) |
| risk_logistic | 14 of 26 | 9 of 26 | 20 of 26 | 13 of 26 | 9 (9 / 0) |
| risk_logistic_base | 13 of 26 | 8 of 26 | 20 of 26 | 13 of 26 | 8 (8 / 0) |
| risk_quantile_skewt_base | 14 of 26 | 10 of 26 | 20 of 26 | 13 of 26 | 10 (10 / 0) |
| two_part_gbm | 15 of 26 | 9 of 26 | 20 of 26 | 26 of 26 | 9 (6 / 3) |
| ngboost_laplace | 15 of 26 | 9 of 26 | 20 of 26 | 26 of 26 | 10 (9 / 1) |
| hierarchical_logistic | 15 of 26 | 13 of 26 | 20 of 26 | 26 of 26 | 13 (10 / 3) |
| settlement_quantile_timing | 15 of 26 | 11 of 26 | 20 of 26 | 26 of 26 | 11 (8 / 3) |
| scarcity_logistic_interactions | 14 of 26 | 11 of 26 | 20 of 26 | 26 of 26 | 11 (8 / 3) |
| scarcity_logistic | 13 of 26 | 11 of 26 | 20 of 26 | 26 of 26 | 11 (8 / 3) |
| calendar_climatology | 10 of 26 | 10 of 26 | 20 of 26 | 25 of 26 | 10 (7 / 3) |
| persistence_logistic | 7 of 26 | 7 of 26 | 20 of 26 | 26 of 26 | 7 (4 / 3) |

### weighted

| row | judge: lead >= 1 warned | judge: lead >= 3 warned | onsets on a risk date (grid label) | onsets forecast above 0 at some h >= 2 | flagged at h >= 2 (on / off a risk date) |
|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 7 of 26 | 20 of 26 | 13 of 26 | 8 (8 / 0) |
| risk_gbm_base | 14 of 26 | 7 of 26 | 20 of 26 | 13 of 26 | 8 (8 / 0) |
| risk_logistic | 16 of 26 | 10 of 26 | 20 of 26 | 13 of 26 | 10 (10 / 0) |
| risk_logistic_base | 15 of 26 | 8 of 26 | 20 of 26 | 13 of 26 | 9 (9 / 0) |
| risk_quantile_skewt_base | 15 of 26 | 10 of 26 | 20 of 26 | 13 of 26 | 10 (10 / 0) |
| two_part_gbm | 15 of 26 | 14 of 26 | 20 of 26 | 26 of 26 | 14 (11 / 3) |
| ngboost_laplace | 17 of 26 | 12 of 26 | 20 of 26 | 26 of 26 | 12 (10 / 2) |
| hierarchical_logistic | 15 of 26 | 13 of 26 | 20 of 26 | 26 of 26 | 13 (10 / 3) |
| settlement_quantile_timing | 16 of 26 | 12 of 26 | 20 of 26 | 26 of 26 | 12 (8 / 4) |
| scarcity_logistic_interactions | 14 of 26 | 11 of 26 | 20 of 26 | 26 of 26 | 11 (8 / 3) |
| scarcity_logistic | 13 of 26 | 11 of 26 | 20 of 26 | 26 of 26 | 11 (8 / 3) |
| calendar_climatology | 12 of 26 | 10 of 26 | 20 of 26 | 25 of 26 | 10 (7 / 3) |
| persistence_logistic | 12 of 26 | 11 of 26 | 20 of 26 | 26 of 26 | 11 (7 / 4) |

## 2020 false-alarm days by as-of scarcity state

### unweighted

| row | worst horizon | false alarms there | by state | flagged at any horizon | by state |
|---|---|---|---|---|---|
| risk_gbm | 2 | 11 | {'1': 5, '2': 1, '3': 5} | 21 | {'1': 10, '2': 1, '3': 10} |
| risk_gbm_base | 1 | 15 | {'1': 8, '3': 7} | 25 | {'1': 15, '3': 10} |
| risk_logistic | 4 | 19 | {'1': 10, '2': 2, '3': 7} | 25 | {'1': 12, '2': 2, '3': 11} |
| risk_logistic_base | 1 | 17 | {'1': 9, '3': 8} | 24 | {'1': 14, '3': 10} |
| risk_quantile_skewt_base | 1 | 24 | {'1': 17, '3': 7} | 36 | {'1': 26, '3': 10} |

### weighted

| row | worst horizon | false alarms there | by state | flagged at any horizon | by state |
|---|---|---|---|---|---|
| risk_gbm | 5 | 13 | {'1': 5, '2': 2, '3': 6} | 21 | {'1': 8, '2': 2, '3': 11} |
| risk_gbm_base | 3 | 18 | {'1': 12, '2': 1, '3': 5} | 29 | {'1': 18, '2': 1, '3': 10} |
| risk_logistic | 4 | 30 | {'1': 21, '2': 2, '3': 7} | 36 | {'1': 23, '2': 2, '3': 11} |
| risk_logistic_base | 1 | 30 | {'1': 20, '3': 10} | 41 | {'1': 30, '3': 11} |
| risk_quantile_skewt_base | 1 | 32 | {'1': 25, '3': 7} | 42 | {'1': 32, '3': 10} |

