# Tier 1 of the hurdle variants under readings (a), (b) and (e) (#539)

## Flat rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 1.35 | 1.35 | 0.76 | pass |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.760] | 3.08 | 3.08 | 1.33 | fail |
| risk_gbm+hurdle_isotonic | 15 of 26 | 0.577 [0.389, 0.783] | 2.62 | 2.62 | 0.90 | fail |
| risk_gbm+hurdle_state_platt | 15 of 26 | 0.577 [0.375, 0.760] | 3.54 | 3.54 | 1.43 | fail |
| risk_gbm+hurdle_state_isotonic | 15 of 26 | 0.577 [0.385, 0.774] | 2.46 | 2.46 | 0.87 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 | 1.50 | 0.97 | pass |
| risk_gbm_base+hurdle_platt | 15 of 26 | 0.577 [0.375, 0.769] | 3.04 | 3.04 | 1.31 | fail |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.767] | 2.54 | 2.54 | 1.00 | fail |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.387, 0.769] | 3.58 | 3.58 | 1.47 | fail |
| risk_gbm_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.304, 0.700] | 2.69 | 2.69 | 0.99 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 1.85 | 1.85 | 1.19 | pass |
| risk_logistic+hurdle_platt | 13 of 26 | 0.500 [0.333, 0.667] | 3.19 | 3.19 | 1.44 | fail |
| risk_logistic+hurdle_isotonic | 13 of 26 | 0.500 [0.333, 0.667] | 2.35 | 2.35 | 0.88 | fail |
| risk_logistic+hurdle_state_platt | 14 of 26 | 0.538 [0.357, 0.714] | 3.77 | 3.77 | 1.61 | fail |
| risk_logistic+hurdle_state_isotonic | 12 of 26 | 0.462 [0.290, 0.640] | 2.88 | 2.88 | 1.03 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 1.77 | 1.77 | 1.16 | pass |
| risk_logistic_base+hurdle_platt | 11 of 26 | 0.423 [0.250, 0.600] | 2.85 | 2.85 | 1.31 | fail |
| risk_logistic_base+hurdle_isotonic | 8 of 26 | 0.308 [0.158, 0.471] | 2.00 | 2.00 | 0.76 | fail |
| risk_logistic_base+hurdle_state_platt | 13 of 26 | 0.500 [0.320, 0.690] | 2.96 | 2.96 | 1.32 | fail |
| risk_logistic_base+hurdle_state_isotonic | 11 of 26 | 0.423 [0.250, 0.611] | 2.46 | 2.46 | 0.88 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 1.88 | 1.88 | 1.25 | pass |
| risk_quantile_skewt_base+hurdle_platt | 13 of 26 | 0.500 [0.321, 0.682] | 3.15 | 3.15 | 1.50 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.667] | 2.92 | 2.92 | 1.11 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 13 of 26 | 0.500 [0.333, 0.688] | 3.50 | 3.50 | 1.57 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 of 26 | 0.462 [0.276, 0.643] | 2.88 | 2.88 | 1.10 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 5.00 | 5.00 | 2.80 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 3.42 | 3.42 | 1.17 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 2.00 | 2.00 | 1.37 | pass |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.767] | 5.23 | 5.23 | 2.36 | fail |
| risk_gbm+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.783] | 4.08 | 4.08 | 1.66 | fail |
| risk_gbm+hurdle_state_platt | 15 of 26 | 0.577 [0.370, 0.762] | 4.46 | 4.46 | 1.91 | fail |
| risk_gbm+hurdle_state_isotonic | 15 of 26 | 0.577 [0.381, 0.773] | 3.73 | 3.73 | 1.42 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 2.04 | 2.04 | 1.43 | fail |
| risk_gbm_base+hurdle_platt | 15 of 26 | 0.577 [0.375, 0.773] | 5.12 | 5.12 | 2.28 | fail |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.762] | 3.96 | 3.96 | 1.61 | fail |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.391, 0.758] | 4.46 | 4.46 | 1.91 | fail |
| risk_gbm_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.308, 0.688] | 3.31 | 3.31 | 1.28 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.364, 0.710] | 2.42 | 2.42 | 1.75 | fail |
| risk_logistic+hurdle_platt | 13 of 26 | 0.500 [0.333, 0.667] | 4.73 | 4.73 | 2.18 | fail |
| risk_logistic+hurdle_isotonic | 13 of 26 | 0.500 [0.333, 0.682] | 3.35 | 3.35 | 1.39 | fail |
| risk_logistic+hurdle_state_platt | 14 of 26 | 0.538 [0.368, 0.722] | 4.88 | 4.88 | 2.17 | fail |
| risk_logistic+hurdle_state_isotonic | 12 of 26 | 0.462 [0.286, 0.640] | 4.08 | 4.08 | 1.65 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.320, 0.677] | 2.04 | 2.04 | 1.41 | fail |
| risk_logistic_base+hurdle_platt | 11 of 26 | 0.423 [0.263, 0.611] | 4.38 | 4.38 | 1.95 | fail |
| risk_logistic_base+hurdle_isotonic | 8 of 26 | 0.308 [0.156, 0.478] | 3.04 | 3.04 | 1.20 | fail |
| risk_logistic_base+hurdle_state_platt | 13 of 26 | 0.500 [0.320, 0.682] | 4.81 | 4.81 | 2.04 | fail |
| risk_logistic_base+hurdle_state_isotonic | 11 of 26 | 0.423 [0.250, 0.615] | 4.04 | 4.04 | 1.54 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.364, 0.720] | 2.54 | 2.54 | 1.80 | fail |
| risk_quantile_skewt_base+hurdle_platt | 13 of 26 | 0.500 [0.320, 0.682] | 5.00 | 5.00 | 2.19 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.645] | 3.77 | 3.77 | 1.43 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 13 of 26 | 0.500 [0.333, 0.682] | 5.04 | 5.04 | 2.18 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 of 26 | 0.462 [0.286, 0.650] | 4.23 | 4.23 | 1.60 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.572] | 5.38 | 5.38 | 2.98 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.107, 0.452] | 5.73 | 5.73 | 2.23 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.56 | 1.56 | 1.17 | fail |
| risk_gbm+hurdle_platt | 2 of 9 | 0.222 [0.000, 0.500] | 1.22 | 1.22 | 0.61 | fail |
| risk_gbm+hurdle_isotonic | 2 of 9 | 0.222 [0.000, 0.545] | 0.78 | 0.78 | 0.39 | fail |
| risk_gbm+hurdle_state_platt | 2 of 9 | 0.222 [–, –] | 0.44 | 0.44 | 0.28 | fail |
| risk_gbm+hurdle_state_isotonic | 2 of 9 | 0.222 [0.000, 0.500] | 0.67 | 0.67 | 0.36 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.00 | 2.00 | 1.72 | fail |
| risk_gbm_base+hurdle_platt | 2 of 9 | 0.222 [–, –] | 1.11 | 1.11 | 0.50 | fail |
| risk_gbm_base+hurdle_isotonic | 2 of 9 | 0.222 [–, –] | 0.56 | 0.56 | 0.36 | fail |
| risk_gbm_base+hurdle_state_platt | 2 of 9 | 0.222 [–, –] | 0.56 | 0.56 | 0.31 | fail |
| risk_gbm_base+hurdle_state_isotonic | 2 of 9 | 0.222 [0.000, 0.539] | 0.44 | 0.44 | 0.28 | fail |
| risk_logistic | 4 of 9 | 0.444 [0.111, 0.750] | 2.89 | 2.89 | 2.56 | fail |
| risk_logistic+hurdle_platt | 2 of 9 | 0.222 [0.000, 0.444] | 1.33 | 1.33 | 0.89 | fail |
| risk_logistic+hurdle_isotonic | 2 of 9 | 0.222 [–, –] | 0.67 | 0.67 | 0.61 | fail |
| risk_logistic+hurdle_state_platt | 2 of 9 | 0.222 [0.000, 0.455] | 0.56 | 0.56 | 0.56 | fail |
| risk_logistic+hurdle_state_isotonic | 1 of 9 | 0.111 [–, –] | 0.56 | 0.56 | 0.56 | fail |
| risk_logistic_base | 3 of 9 | 0.333 [–, –] | 2.33 | 2.33 | 2.03 | fail |
| risk_logistic_base+hurdle_platt | 2 of 9 | 0.222 [–, –] | 1.11 | 1.11 | 0.72 | fail |
| risk_logistic_base+hurdle_isotonic | 0 of 9 | 0.000 [–, –] | 0.67 | 0.67 | 0.61 | fail |
| risk_logistic_base+hurdle_state_platt | 1 of 9 | 0.111 [0.000, 0.333] | 0.56 | 0.56 | 0.56 | fail |
| risk_logistic_base+hurdle_state_isotonic | 0 of 9 | 0.000 [–, –] | 0.67 | 0.67 | 0.61 | fail |
| risk_quantile_skewt_base | 4 of 9 | 0.444 [–, –] | 3.22 | 3.22 | 2.75 | fail |
| risk_quantile_skewt_base+hurdle_platt | 1 of 9 | 0.111 [–, –] | 1.22 | 1.22 | 1.03 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 0 of 9 | 0.000 [–, –] | 1.00 | 1.00 | 0.58 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 1 of 9 | 0.111 [–, –] | 0.89 | 0.89 | 0.78 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0 of 9 | 0.000 [–, –] | 1.00 | 1.00 | 0.58 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 3.78 | 3.78 | 3.67 | fail |
| persistence_logistic | 0 of 9 | 0.000 [0.000, 0.000] | 2.22 | 2.22 | 0.83 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 1.24 | 1.24 | 0.54 | pass |
| risk_gbm+hurdle_platt | 13 of 17 | 0.765 [0.550, 0.950] | 4.29 | 4.29 | 1.84 | fail |
| risk_gbm+hurdle_isotonic | 13 of 17 | 0.765 [0.545, 0.952] | 3.59 | 3.59 | 1.18 | fail |
| risk_gbm+hurdle_state_platt | 13 of 17 | 0.765 [0.545, 1.000] | 5.35 | 5.35 | 2.13 | fail |
| risk_gbm+hurdle_state_isotonic | 13 of 17 | 0.765 [0.538, 1.000] | 3.65 | 3.65 | 1.24 | fail |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 1.24 | 1.24 | 0.59 | pass |
| risk_gbm_base+hurdle_platt | 13 of 17 | 0.765 [0.538, 0.955] | 4.35 | 4.35 | 1.85 | fail |
| risk_gbm_base+hurdle_isotonic | 13 of 17 | 0.765 [0.533, 0.950] | 3.59 | 3.59 | 1.43 | fail |
| risk_gbm_base+hurdle_state_platt | 13 of 17 | 0.765 [0.538, 0.950] | 5.35 | 5.35 | 2.13 | fail |
| risk_gbm_base+hurdle_state_isotonic | 11 of 17 | 0.647 [0.412, 0.875] | 3.88 | 3.88 | 1.41 | fail |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_logistic+hurdle_platt | 11 of 17 | 0.647 [0.429, 0.867] | 4.41 | 4.41 | 1.84 | fail |
| risk_logistic+hurdle_isotonic | 11 of 17 | 0.647 [0.435, 0.857] | 3.35 | 3.35 | 1.10 | fail |
| risk_logistic+hurdle_state_platt | 12 of 17 | 0.706 [0.500, 0.923] | 5.53 | 5.53 | 2.22 | fail |
| risk_logistic+hurdle_state_isotonic | 11 of 17 | 0.647 [0.438, 0.858] | 4.24 | 4.24 | 1.40 | fail |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_logistic_base+hurdle_platt | 9 of 17 | 0.529 [0.308, 0.750] | 3.88 | 3.88 | 1.66 | fail |
| risk_logistic_base+hurdle_isotonic | 8 of 17 | 0.471 [0.273, 0.692] | 2.82 | 2.82 | 0.93 | fail |
| risk_logistic_base+hurdle_state_platt | 12 of 17 | 0.706 [0.500, 0.917] | 4.35 | 4.35 | 1.82 | fail |
| risk_logistic_base+hurdle_state_isotonic | 11 of 17 | 0.647 [0.429, 0.857] | 3.71 | 3.71 | 1.28 | fail |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.18 | 1.18 | 0.46 | pass |
| risk_quantile_skewt_base+hurdle_platt | 12 of 17 | 0.706 [0.500, 0.923] | 4.18 | 4.18 | 1.75 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 12 of 17 | 0.706 [0.500, 0.909] | 4.18 | 4.18 | 1.43 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 12 of 17 | 0.706 [0.500, 0.917] | 5.06 | 5.06 | 2.10 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 of 17 | 0.706 [0.500, 0.917] | 4.24 | 4.24 | 1.44 | fail |
| calendar_climatology | 10 of 17 | 0.588 [0.353, 0.812] | 5.65 | 5.65 | 2.34 | fail |
| persistence_logistic | 7 of 17 | 0.412 [0.185, 0.647] | 4.24 | 4.24 | 1.46 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 1.35 | 8 / 1.08 | 7 / 1.04 | 7 / 0.88 | 7 / 1.04 | pass (h = 1) |
| risk_gbm+hurdle_platt | 12 / 1.50 | 7 / 3.04 | 10 / 2.58 | 9 / 2.38 | 8 / 3.08 | fail |
| risk_gbm+hurdle_isotonic | 13 / 1.54 | 6 / 2.62 | 9 / 2.50 | 8 / 1.96 | 7 / 2.19 | pass (h = 1) |
| risk_gbm+hurdle_state_platt | 13 / 2.12 | 8 / 3.04 | 10 / 3.54 | 9 / 2.73 | 9 / 3.12 | fail |
| risk_gbm+hurdle_state_isotonic | 14 / 2.23 | 6 / 1.92 | 9 / 2.46 | 9 / 2.00 | 7 / 2.27 | fail |
| risk_gbm_base | 13 / 1.50 | 8 / 0.96 | 7 / 1.27 | 7 / 1.12 | 7 / 1.08 | pass (h = 1) |
| risk_gbm_base+hurdle_platt | 11 / 2.73 | 6 / 2.65 | 9 / 2.54 | 8 / 2.38 | 8 / 3.04 | fail |
| risk_gbm_base+hurdle_isotonic | 10 / 2.42 | 5 / 2.19 | 8 / 2.54 | 6 / 1.77 | 7 / 2.04 | fail |
| risk_gbm_base+hurdle_state_platt | 12 / 3.19 | 7 / 2.65 | 10 / 3.58 | 8 / 2.81 | 9 / 3.12 | fail |
| risk_gbm_base+hurdle_state_isotonic | 12 / 2.69 | 6 / 1.85 | 7 / 2.50 | 6 / 1.69 | 6 / 1.85 | fail |
| risk_logistic | 13 / 1.85 | 7 / 1.00 | 7 / 1.19 | 9 / 1.54 | 8 / 1.42 | pass (h = 1) |
| risk_logistic+hurdle_platt | 7 / 2.46 | 7 / 1.81 | 5 / 1.23 | 6 / 1.23 | 8 / 3.19 | fail |
| risk_logistic+hurdle_isotonic | 6 / 1.88 | 4 / 1.19 | 5 / 1.19 | 6 / 1.58 | 7 / 2.35 | fail |
| risk_logistic+hurdle_state_platt | 7 / 3.00 | 5 / 1.92 | 4 / 1.23 | 6 / 1.42 | 9 / 3.77 | fail |
| risk_logistic+hurdle_state_isotonic | 7 / 2.50 | 4 / 1.19 | 4 / 1.15 | 6 / 1.92 | 7 / 2.88 | fail |
| risk_logistic_base | 13 / 1.77 | 6 / 1.00 | 6 / 1.00 | 7 / 1.12 | 8 / 1.15 | pass (h = 1) |
| risk_logistic_base+hurdle_platt | 5 / 1.50 | 6 / 1.73 | 7 / 1.73 | 7 / 1.85 | 7 / 2.85 | fail |
| risk_logistic_base+hurdle_isotonic | 5 / 1.00 | 4 / 1.35 | 5 / 1.88 | 4 / 1.65 | 5 / 2.00 | fail |
| risk_logistic_base+hurdle_state_platt | 7 / 2.65 | 4 / 1.65 | 7 / 2.85 | 6 / 1.77 | 8 / 2.96 | fail |
| risk_logistic_base+hurdle_state_isotonic | 8 / 2.46 | 4 / 1.19 | 5 / 1.92 | 4 / 1.69 | 7 / 2.38 | fail |
| risk_quantile_skewt_base | 13 / 1.88 | 9 / 1.65 | 9 / 1.50 | 9 / 1.12 | 9 / 1.04 | pass (h = 1) |
| risk_quantile_skewt_base+hurdle_platt | 7 / 1.65 | 2 / 1.08 | 9 / 2.31 | 9 / 2.54 | 10 / 3.15 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 7 / 1.77 | 1 / 1.08 | 11 / 2.92 | 7 / 2.27 | 7 / 1.96 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 8 / 2.65 | 1 / 1.31 | 11 / 3.50 | 9 / 2.50 | 11 / 3.35 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 8 / 2.85 | 2 / 1.23 | 10 / 2.88 | 7 / 2.27 | 8 / 2.08 | fail |
| calendar_climatology | 9 / 4.85 | 10 / 4.88 | 10 / 4.92 | 10 / 4.96 | 10 / 5.00 | fail |
| persistence_logistic | 4 / 2.77 | 6 / 3.42 | 6 / 2.81 | 6 / 3.15 | 5 / 2.81 | fail |

## Weighted rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.80 | 1.38 | 0.80 | pass |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.760] | 2.23 | 5.04 | 2.23 | fail |
| risk_gbm+hurdle_isotonic | 16 of 26 | 0.615 [0.437, 0.808] | 2.13 | 4.92 | 2.13 | fail |
| risk_gbm+hurdle_state_platt | 15 of 26 | 0.577 [0.375, 0.760] | 2.14 | 4.58 | 2.14 | fail |
| risk_gbm+hurdle_state_isotonic | 16 of 26 | 0.615 [0.424, 0.800] | 2.11 | 4.65 | 2.11 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.97 | 1.50 | 0.97 | pass |
| risk_gbm_base+hurdle_platt | 15 of 26 | 0.577 [0.375, 0.769] | 2.15 | 4.96 | 2.15 | fail |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.767] | 2.18 | 4.92 | 2.18 | fail |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.387, 0.769] | 2.12 | 4.65 | 2.12 | fail |
| risk_gbm_base+hurdle_state_isotonic | 15 of 26 | 0.577 [0.385, 0.778] | 2.10 | 4.81 | 2.10 | fail |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 1.74 | 2.42 | 1.74 | pass |
| risk_logistic+hurdle_platt | 15 of 26 | 0.577 [0.391, 0.762] | 2.39 | 5.31 | 2.39 | fail |
| risk_logistic+hurdle_isotonic | 15 of 26 | 0.577 [0.400, 0.760] | 2.14 | 4.85 | 2.14 | fail |
| risk_logistic+hurdle_state_platt | 15 of 26 | 0.577 [0.385, 0.762] | 2.92 | 6.19 | 2.92 | fail |
| risk_logistic+hurdle_state_isotonic | 15 of 26 | 0.577 [0.400, 0.750] | 2.62 | 5.77 | 2.62 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 1.65 | 2.31 | 1.65 | pass |
| risk_logistic_base+hurdle_platt | 12 of 26 | 0.462 [0.281, 0.650] | 2.13 | 4.88 | 2.13 | fail |
| risk_logistic_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.636] | 2.12 | 4.81 | 2.12 | fail |
| risk_logistic_base+hurdle_state_platt | 14 of 26 | 0.538 [0.364, 0.719] | 2.61 | 5.65 | 2.61 | fail |
| risk_logistic_base+hurdle_state_isotonic | 14 of 26 | 0.538 [0.370, 0.720] | 2.45 | 5.38 | 2.45 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 1.62 | 2.31 | 1.62 | pass |
| risk_quantile_skewt_base+hurdle_platt | 14 of 26 | 0.538 [0.364, 0.715] | 2.48 | 5.12 | 2.48 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 13 of 26 | 0.500 [0.333, 0.688] | 2.36 | 4.88 | 2.36 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 14 of 26 | 0.538 [0.367, 0.720] | 2.57 | 5.54 | 2.57 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.321, 0.677] | 2.61 | 5.69 | 2.61 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 3.75 | 6.69 | 3.75 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 3.25 | 7.04 | 3.25 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 1.48 | 2.12 | 1.48 | pass |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.767] | 3.10 | 6.42 | 3.10 | fail |
| risk_gbm+hurdle_isotonic | 16 of 26 | 0.615 [0.423, 0.806] | 2.77 | 5.92 | 2.77 | fail |
| risk_gbm+hurdle_state_platt | 15 of 26 | 0.577 [0.370, 0.762] | 2.71 | 5.69 | 2.71 | fail |
| risk_gbm+hurdle_state_isotonic | 16 of 26 | 0.615 [0.423, 0.800] | 2.69 | 5.81 | 2.69 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 1.59 | 2.19 | 1.59 | pass |
| risk_gbm_base+hurdle_platt | 15 of 26 | 0.577 [0.375, 0.773] | 3.38 | 6.85 | 3.38 | fail |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.762] | 3.11 | 6.46 | 3.11 | fail |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.391, 0.758] | 2.81 | 5.81 | 2.81 | fail |
| risk_gbm_base+hurdle_state_isotonic | 15 of 26 | 0.577 [0.385, 0.769] | 2.78 | 5.96 | 2.78 | fail |
| risk_logistic | 16 of 26 | 0.615 [0.440, 0.800] | 2.55 | 3.31 | 2.55 | fail |
| risk_logistic+hurdle_platt | 15 of 26 | 0.577 [0.400, 0.750] | 3.11 | 6.58 | 3.11 | fail |
| risk_logistic+hurdle_isotonic | 15 of 26 | 0.577 [0.400, 0.762] | 2.94 | 6.19 | 2.94 | fail |
| risk_logistic+hurdle_state_platt | 15 of 26 | 0.577 [0.400, 0.750] | 3.57 | 7.08 | 3.57 | fail |
| risk_logistic+hurdle_state_isotonic | 15 of 26 | 0.577 [0.400, 0.759] | 3.36 | 6.85 | 3.36 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.759] | 2.18 | 2.88 | 2.18 | fail |
| risk_logistic_base+hurdle_platt | 12 of 26 | 0.462 [0.286, 0.667] | 2.81 | 6.04 | 2.81 | fail |
| risk_logistic_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.650] | 2.54 | 5.42 | 2.54 | fail |
| risk_logistic_base+hurdle_state_platt | 14 of 26 | 0.538 [0.364, 0.714] | 3.29 | 6.77 | 3.29 | fail |
| risk_logistic_base+hurdle_state_isotonic | 14 of 26 | 0.538 [0.368, 0.714] | 3.21 | 6.69 | 3.21 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.400, 0.759] | 2.14 | 2.88 | 2.14 | fail |
| risk_quantile_skewt_base+hurdle_platt | 14 of 26 | 0.538 [0.372, 0.714] | 3.13 | 6.46 | 3.13 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 13 of 26 | 0.500 [0.323, 0.679] | 2.94 | 6.12 | 2.94 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 14 of 26 | 0.538 [0.364, 0.719] | 3.35 | 6.85 | 3.35 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.333, 0.682] | 3.46 | 7.19 | 3.46 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.278, 0.650] | 3.90 | 6.85 | 3.90 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.276, 0.667] | 4.09 | 8.46 | 4.09 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.61 | 1.89 | 1.61 | fail |
| risk_gbm+hurdle_platt | 2 of 9 | 0.222 [0.000, 0.500] | 1.31 | 1.78 | 1.31 | fail |
| risk_gbm+hurdle_isotonic | 3 of 9 | 0.333 [0.000, 0.625] | 1.00 | 1.44 | 1.00 | fail |
| risk_gbm+hurdle_state_platt | 2 of 9 | 0.222 [–, –] | 1.00 | 1.22 | 1.00 | fail |
| risk_gbm+hurdle_state_isotonic | 3 of 9 | 0.333 [0.000, 0.616] | 0.94 | 1.44 | 0.94 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.06 | 2.33 | 2.06 | fail |
| risk_gbm_base+hurdle_platt | 2 of 9 | 0.222 [–, –] | 1.69 | 2.11 | 1.69 | fail |
| risk_gbm_base+hurdle_isotonic | 2 of 9 | 0.222 [–, –] | 1.31 | 1.78 | 1.31 | fail |
| risk_gbm_base+hurdle_state_platt | 2 of 9 | 0.222 [–, –] | 1.14 | 1.22 | 1.14 | fail |
| risk_gbm_base+hurdle_state_isotonic | 2 of 9 | 0.222 [0.000, 0.539] | 0.94 | 1.44 | 0.94 | fail |
| risk_logistic | 6 of 9 | 0.667 [0.307, 1.000] | 4.39 | 4.89 | 4.39 | fail |
| risk_logistic+hurdle_platt | 2 of 9 | 0.222 [0.000, 0.444] | 1.64 | 2.22 | 1.64 | fail |
| risk_logistic+hurdle_isotonic | 2 of 9 | 0.222 [–, –] | 1.33 | 1.33 | 1.33 | fail |
| risk_logistic+hurdle_state_platt | 2 of 9 | 0.222 [0.000, 0.455] | 1.56 | 1.89 | 1.56 | fail |
| risk_logistic+hurdle_state_isotonic | 2 of 9 | 0.222 [–, –] | 1.25 | 1.33 | 1.25 | fail |
| risk_logistic_base | 5 of 9 | 0.556 [–, –] | 3.67 | 4.00 | 3.67 | fail |
| risk_logistic_base+hurdle_platt | 2 of 9 | 0.222 [–, –] | 1.22 | 1.78 | 1.22 | fail |
| risk_logistic_base+hurdle_isotonic | 2 of 9 | 0.222 [–, –] | 1.33 | 1.33 | 1.33 | fail |
| risk_logistic_base+hurdle_state_platt | 2 of 9 | 0.222 [0.000, 0.444] | 1.14 | 1.22 | 1.14 | fail |
| risk_logistic_base+hurdle_state_isotonic | 2 of 9 | 0.222 [–, –] | 1.25 | 1.33 | 1.25 | fail |
| risk_quantile_skewt_base | 5 of 9 | 0.556 [–, –] | 3.81 | 4.44 | 3.81 | fail |
| risk_quantile_skewt_base+hurdle_platt | 2 of 9 | 0.222 [–, –] | 2.08 | 2.44 | 2.08 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 1 of 9 | 0.111 [–, –] | 1.72 | 1.78 | 1.72 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 2 of 9 | 0.222 [–, –] | 1.61 | 1.67 | 1.61 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 1 of 9 | 0.111 [–, –] | 1.67 | 1.78 | 1.67 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 4.56 | 4.67 | 4.56 | fail |
| persistence_logistic | 1 of 9 | 0.111 [0.000, 0.333] | 2.86 | 4.89 | 2.86 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 0.54 | 1.24 | 0.54 | pass |
| risk_gbm+hurdle_platt | 13 of 17 | 0.765 [0.550, 0.950] | 2.79 | 6.76 | 2.79 | fail |
| risk_gbm+hurdle_isotonic | 13 of 17 | 0.765 [0.545, 0.952] | 2.79 | 6.76 | 2.79 | fail |
| risk_gbm+hurdle_state_platt | 13 of 17 | 0.765 [0.545, 1.000] | 2.78 | 6.59 | 2.78 | fail |
| risk_gbm+hurdle_state_isotonic | 13 of 17 | 0.765 [0.538, 1.000] | 2.78 | 6.59 | 2.78 | fail |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 0.59 | 1.24 | 0.59 | pass |
| risk_gbm_base+hurdle_platt | 13 of 17 | 0.765 [0.538, 0.955] | 2.79 | 6.76 | 2.79 | fail |
| risk_gbm_base+hurdle_isotonic | 13 of 17 | 0.765 [0.533, 0.950] | 2.96 | 6.76 | 2.96 | fail |
| risk_gbm_base+hurdle_state_platt | 13 of 17 | 0.765 [0.538, 0.950] | 2.78 | 6.59 | 2.78 | fail |
| risk_gbm_base+hurdle_state_isotonic | 13 of 17 | 0.765 [0.538, 0.952] | 2.78 | 6.59 | 2.78 | fail |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_logistic+hurdle_platt | 13 of 17 | 0.765 [0.550, 0.950] | 2.79 | 6.94 | 2.79 | fail |
| risk_logistic+hurdle_isotonic | 13 of 17 | 0.765 [0.538, 0.947] | 2.79 | 6.94 | 2.79 | fail |
| risk_logistic+hurdle_state_platt | 13 of 17 | 0.765 [0.550, 0.947] | 3.65 | 8.47 | 3.65 | fail |
| risk_logistic+hurdle_state_isotonic | 13 of 17 | 0.765 [0.550, 1.000] | 3.65 | 8.47 | 3.65 | fail |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_logistic_base+hurdle_platt | 10 of 17 | 0.588 [0.353, 0.833] | 2.74 | 6.71 | 2.74 | fail |
| risk_logistic_base+hurdle_isotonic | 10 of 17 | 0.588 [0.364, 0.833] | 2.74 | 6.71 | 2.74 | fail |
| risk_logistic_base+hurdle_state_platt | 12 of 17 | 0.706 [0.500, 0.917] | 3.51 | 8.00 | 3.51 | fail |
| risk_logistic_base+hurdle_state_isotonic | 12 of 17 | 0.706 [0.500, 0.909] | 3.51 | 8.00 | 3.51 | fail |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.46 | 1.18 | 0.46 | pass |
| risk_quantile_skewt_base+hurdle_platt | 12 of 17 | 0.706 [0.500, 0.923] | 2.69 | 6.53 | 2.69 | fail |
| risk_quantile_skewt_base+hurdle_isotonic | 12 of 17 | 0.706 [0.500, 0.909] | 2.69 | 6.53 | 2.69 | fail |
| risk_quantile_skewt_base+hurdle_state_platt | 12 of 17 | 0.706 [0.500, 0.917] | 3.44 | 7.76 | 3.44 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 of 17 | 0.706 [0.500, 0.917] | 3.44 | 7.76 | 3.44 | fail |
| calendar_climatology | 12 of 17 | 0.706 [0.474, 0.900] | 3.32 | 7.76 | 3.32 | fail |
| persistence_logistic | 11 of 17 | 0.647 [0.412, 0.889] | 3.54 | 8.18 | 3.54 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 0.80 | 8 / 0.68 | 7 / 0.59 | 7 / 0.47 | 7 / 0.76 | pass (h = 1) |
| risk_gbm+hurdle_platt | 15 / 1.82 | 11 / 2.23 | 11 / 1.96 | 10 / 1.88 | 9 / 1.96 | pass (h = 1) |
| risk_gbm+hurdle_isotonic | 15 / 1.75 | 11 / 2.13 | 11 / 2.00 | 10 / 1.77 | 10 / 1.86 | pass (h = 1) |
| risk_gbm+hurdle_state_platt | 15 / 2.03 | 10 / 2.14 | 11 / 1.96 | 10 / 1.84 | 10 / 2.02 | fail |
| risk_gbm+hurdle_state_isotonic | 15 / 1.99 | 10 / 2.11 | 11 / 1.98 | 10 / 1.84 | 11 / 2.06 | pass (h = 1) |
| risk_gbm_base | 14 / 0.97 | 8 / 0.64 | 7 / 0.91 | 7 / 0.66 | 7 / 0.76 | pass (h = 1) |
| risk_gbm_base+hurdle_platt | 15 / 2.05 | 10 / 2.15 | 11 / 2.08 | 10 / 1.86 | 9 / 2.11 | fail |
| risk_gbm_base+hurdle_isotonic | 15 / 2.18 | 10 / 2.13 | 11 / 2.17 | 10 / 1.88 | 9 / 1.84 | fail |
| risk_gbm_base+hurdle_state_platt | 15 / 2.06 | 9 / 2.07 | 11 / 2.04 | 10 / 1.81 | 10 / 2.12 | fail |
| risk_gbm_base+hurdle_state_isotonic | 15 / 2.10 | 9 / 2.06 | 11 / 2.06 | 10 / 1.85 | 10 / 2.01 | fail |
| risk_logistic | 14 / 1.74 | 7 / 1.28 | 8 / 1.34 | 10 / 1.71 | 9 / 1.58 | pass (h = 1) |
| risk_logistic+hurdle_platt | 13 / 2.39 | 11 / 1.81 | 10 / 1.70 | 9 / 1.56 | 11 / 1.82 | fail |
| risk_logistic+hurdle_isotonic | 12 / 2.08 | 11 / 1.75 | 9 / 1.68 | 8 / 1.57 | 11 / 2.14 | fail |
| risk_logistic+hurdle_state_platt | 13 / 2.92 | 11 / 1.86 | 10 / 1.68 | 9 / 1.92 | 11 / 2.55 | fail |
| risk_logistic+hurdle_state_isotonic | 12 / 2.62 | 11 / 1.87 | 9 / 1.66 | 8 / 1.94 | 11 / 2.55 | fail |
| risk_logistic_base | 14 / 1.65 | 8 / 1.22 | 7 / 1.16 | 7 / 1.01 | 8 / 1.47 | pass (h = 1) |
| risk_logistic_base+hurdle_platt | 11 / 1.73 | 11 / 2.13 | 11 / 1.67 | 10 / 1.67 | 10 / 1.79 | fail |
| risk_logistic_base+hurdle_isotonic | 9 / 1.77 | 10 / 2.08 | 10 / 1.67 | 9 / 1.94 | 10 / 2.12 | fail |
| risk_logistic_base+hurdle_state_platt | 12 / 2.61 | 11 / 2.21 | 10 / 1.63 | 11 / 2.04 | 10 / 2.08 | fail |
| risk_logistic_base+hurdle_state_isotonic | 12 / 2.45 | 10 / 2.21 | 10 / 1.65 | 10 / 2.39 | 10 / 2.12 | fail |
| risk_quantile_skewt_base | 15 / 1.62 | 9 / 1.44 | 9 / 1.00 | 9 / 0.56 | 9 / 0.51 | pass (h = 1) |
| risk_quantile_skewt_base+hurdle_platt | 13 / 1.93 | 11 / 1.79 | 12 / 1.84 | 12 / 2.20 | 12 / 2.48 | pass (h = 1) |
| risk_quantile_skewt_base+hurdle_isotonic | 13 / 1.90 | 11 / 1.85 | 11 / 1.88 | 11 / 2.12 | 12 / 2.36 | pass (h = 1) |
| risk_quantile_skewt_base+hurdle_state_platt | 13 / 2.57 | 10 / 1.88 | 11 / 1.71 | 12 / 2.55 | 12 / 2.32 | fail |
| risk_quantile_skewt_base+hurdle_state_isotonic | 13 / 2.61 | 9 / 1.34 | 11 / 1.87 | 11 / 2.57 | 12 / 2.34 | fail |
| calendar_climatology | 12 / 3.75 | 10 / 3.17 | 10 / 3.21 | 10 / 3.25 | 10 / 3.29 | fail |
| persistence_logistic | 11 / 3.25 | 7 / 2.07 | 10 / 2.68 | 8 / 2.38 | 8 / 1.86 | fail |

