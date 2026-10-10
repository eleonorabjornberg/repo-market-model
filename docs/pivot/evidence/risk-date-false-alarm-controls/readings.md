# Tier 1 of the false-alarm controls under readings (a), (b) and (e) (#532)

## Flat rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 1.35 | 1.35 | 0.76 | pass |
| risk_gbm+every_day | 15 of 26 | 0.577 [0.385, 0.760] | 2.96 | 2.96 | 1.16 | fail |
| risk_gbm+every_day+shrunk | 13 of 26 | 0.500 [0.324, 0.682] | 1.38 | 1.38 | 0.62 | pass |
| risk_gbm+every_day+scarce | 16 of 26 | 0.615 [0.433, 0.792] | 2.96 | 2.96 | 1.18 | fail |
| risk_gbm+every_day+persist | 15 of 26 | 0.577 [0.406, 0.750] | 2.96 | 2.96 | 1.23 | fail |
| risk_gbm+every_day+gate | 16 of 26 | 0.615 [0.444, 0.778] | 2.96 | 2.96 | 1.13 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 | 1.50 | 0.97 | pass |
| risk_gbm_base+every_day | 15 of 26 | 0.577 [0.389, 0.769] | 2.92 | 2.92 | 1.23 | fail |
| risk_gbm_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 2.15 | 2.15 | 0.92 | fail |
| risk_gbm_base+every_day+scarce | 15 of 26 | 0.577 [0.385, 0.769] | 3.00 | 3.00 | 1.26 | fail |
| risk_gbm_base+every_day+persist | 15 of 26 | 0.577 [0.389, 0.765] | 2.88 | 2.88 | 1.24 | fail |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.400, 0.750] | 2.88 | 2.88 | 1.12 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 1.85 | 1.85 | 1.19 | pass |
| risk_logistic+every_day | 13 of 26 | 0.500 [0.333, 0.667] | 2.69 | 2.69 | 1.10 | fail |
| risk_logistic+every_day+shrunk | 15 of 26 | 0.577 [0.407, 0.750] | 2.85 | 2.85 | 1.20 | fail |
| risk_logistic+every_day+scarce | 13 of 26 | 0.500 [0.333, 0.667] | 2.62 | 2.62 | 1.04 | fail |
| risk_logistic+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 3.50 | 3.50 | 1.44 | fail |
| risk_logistic+every_day+gate | 14 of 26 | 0.538 [0.370, 0.720] | 3.00 | 3.00 | 1.21 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 1.77 | 1.77 | 1.16 | pass |
| risk_logistic_base+every_day | 11 of 26 | 0.423 [0.259, 0.593] | 2.31 | 2.31 | 0.94 | fail |
| risk_logistic_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 2.46 | 2.46 | 0.88 | fail |
| risk_logistic_base+every_day+scarce | 11 of 26 | 0.423 [0.250, 0.600] | 2.23 | 2.23 | 0.88 | fail |
| risk_logistic_base+every_day+persist | 13 of 26 | 0.500 [0.333, 0.679] | 1.81 | 1.81 | 0.79 | pass |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.368, 0.714] | 2.88 | 2.88 | 1.14 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 1.88 | 1.88 | 1.25 | pass |
| risk_quantile_skewt_base+every_day | 15 of 26 | 0.577 [0.409, 0.750] | 2.46 | 2.46 | 1.10 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 15 of 26 | 0.577 [0.400, 0.760] | 2.65 | 2.65 | 1.23 | fail |
| risk_quantile_skewt_base+every_day+scarce | 15 of 26 | 0.577 [0.400, 0.739] | 2.38 | 2.38 | 1.04 | fail |
| risk_quantile_skewt_base+every_day+persist | 14 of 26 | 0.538 [0.368, 0.706] | 2.85 | 2.85 | 1.16 | fail |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.741] | 3.15 | 3.15 | 1.33 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 5.00 | 5.00 | 2.80 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 3.42 | 3.42 | 1.17 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 2.00 | 2.00 | 1.37 | pass |
| risk_gbm+every_day | 15 of 26 | 0.577 [0.385, 0.769] | 5.85 | 5.85 | 2.63 | fail |
| risk_gbm+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.677] | 3.04 | 3.04 | 1.55 | fail |
| risk_gbm+every_day+scarce | 16 of 26 | 0.615 [0.435, 0.788] | 5.73 | 5.73 | 2.58 | fail |
| risk_gbm+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 5.50 | 5.50 | 2.46 | fail |
| risk_gbm+every_day+gate | 16 of 26 | 0.615 [0.452, 0.778] | 5.65 | 5.65 | 2.56 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 2.04 | 2.04 | 1.43 | fail |
| risk_gbm_base+every_day | 15 of 26 | 0.577 [0.389, 0.765] | 6.08 | 6.08 | 2.76 | fail |
| risk_gbm_base+every_day+shrunk | 13 of 26 | 0.500 [0.320, 0.680] | 3.58 | 3.58 | 1.80 | fail |
| risk_gbm_base+every_day+scarce | 15 of 26 | 0.577 [0.381, 0.781] | 5.92 | 5.92 | 2.68 | fail |
| risk_gbm_base+every_day+persist | 15 of 26 | 0.577 [0.391, 0.759] | 5.77 | 5.77 | 2.62 | fail |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.400, 0.762] | 5.77 | 5.77 | 2.58 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.364, 0.710] | 2.42 | 2.42 | 1.75 | fail |
| risk_logistic+every_day | 13 of 26 | 0.500 [0.321, 0.655] | 4.77 | 4.77 | 2.18 | fail |
| risk_logistic+every_day+shrunk | 15 of 26 | 0.577 [0.393, 0.759] | 4.27 | 4.27 | 1.99 | fail |
| risk_logistic+every_day+scarce | 13 of 26 | 0.500 [0.333, 0.667] | 4.54 | 4.54 | 2.07 | fail |
| risk_logistic+every_day+persist | 15 of 26 | 0.577 [0.400, 0.762] | 5.12 | 5.12 | 2.19 | fail |
| risk_logistic+every_day+gate | 14 of 26 | 0.538 [0.368, 0.710] | 5.35 | 5.35 | 2.44 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.320, 0.677] | 2.04 | 2.04 | 1.41 | fail |
| risk_logistic_base+every_day | 11 of 26 | 0.423 [0.250, 0.591] | 4.31 | 4.31 | 1.85 | fail |
| risk_logistic_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 3.73 | 3.73 | 1.54 | fail |
| risk_logistic_base+every_day+scarce | 11 of 26 | 0.423 [0.261, 0.591] | 4.15 | 4.15 | 1.77 | fail |
| risk_logistic_base+every_day+persist | 13 of 26 | 0.500 [0.333, 0.667] | 4.50 | 4.50 | 1.78 | fail |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.367, 0.720] | 4.96 | 4.96 | 2.14 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.364, 0.720] | 2.54 | 2.54 | 1.80 | fail |
| risk_quantile_skewt_base+every_day | 15 of 26 | 0.577 [0.407, 0.739] | 4.65 | 4.65 | 1.97 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 15 of 26 | 0.577 [0.394, 0.750] | 4.85 | 4.85 | 2.28 | fail |
| risk_quantile_skewt_base+every_day+scarce | 15 of 26 | 0.577 [0.400, 0.737] | 4.46 | 4.46 | 1.88 | fail |
| risk_quantile_skewt_base+every_day+persist | 14 of 26 | 0.538 [0.357, 0.714] | 5.38 | 5.38 | 2.26 | fail |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.742] | 5.00 | 5.00 | 2.22 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.572] | 5.38 | 5.38 | 2.98 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.107, 0.452] | 5.73 | 5.73 | 2.23 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.56 | 1.56 | 1.17 | fail |
| risk_gbm+every_day | 2 of 9 | 0.222 [0.000, 0.545] | 2.44 | 2.44 | 1.28 | fail |
| risk_gbm+every_day+shrunk | 3 of 9 | 0.333 [–, –] | 1.78 | 1.78 | 1.17 | fail |
| risk_gbm+every_day+scarce | 3 of 9 | 0.333 [0.000, 0.625] | 2.44 | 2.44 | 1.28 | fail |
| risk_gbm+every_day+persist | 3 of 9 | 0.333 [–, –] | 1.89 | 1.89 | 1.00 | fail |
| risk_gbm+every_day+gate | 4 of 9 | 0.444 [0.167, 0.728] | 2.67 | 2.67 | 1.39 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.00 | 2.00 | 1.72 | fail |
| risk_gbm_base+every_day | 2 of 9 | 0.222 [–, –] | 2.33 | 2.33 | 1.25 | fail |
| risk_gbm_base+every_day+shrunk | 3 of 9 | 0.333 [–, –] | 2.22 | 2.22 | 1.56 | fail |
| risk_gbm_base+every_day+scarce | 2 of 9 | 0.222 [–, –] | 2.44 | 2.44 | 1.22 | fail |
| risk_gbm_base+every_day+persist | 3 of 9 | 0.333 [–, –] | 2.44 | 2.44 | 1.47 | fail |
| risk_gbm_base+every_day+gate | 3 of 9 | 0.333 [–, –] | 2.67 | 2.67 | 1.31 | fail |
| risk_logistic | 4 of 9 | 0.444 [0.111, 0.750] | 2.89 | 2.89 | 2.56 | fail |
| risk_logistic+every_day | 2 of 9 | 0.222 [–, –] | 2.44 | 2.44 | 1.44 | fail |
| risk_logistic+every_day+shrunk | 3 of 9 | 0.333 [0.000, 0.636] | 2.44 | 2.44 | 1.58 | fail |
| risk_logistic+every_day+scarce | 2 of 9 | 0.222 [0.000, 0.444] | 2.33 | 2.33 | 1.42 | fail |
| risk_logistic+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.89 | 1.89 | 1.31 | fail |
| risk_logistic+every_day+gate | 2 of 9 | 0.222 [–, –] | 2.44 | 2.44 | 1.44 | fail |
| risk_logistic_base | 3 of 9 | 0.333 [–, –] | 2.33 | 2.33 | 2.03 | fail |
| risk_logistic_base+every_day | 2 of 9 | 0.222 [0.000, 0.444] | 2.67 | 2.67 | 1.47 | fail |
| risk_logistic_base+every_day+shrunk | 2 of 9 | 0.222 [0.000, 0.444] | 1.44 | 1.44 | 1.03 | fail |
| risk_logistic_base+every_day+scarce | 2 of 9 | 0.222 [–, –] | 2.33 | 2.33 | 1.33 | fail |
| risk_logistic_base+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.78 | 1.78 | 1.11 | fail |
| risk_logistic_base+every_day+gate | 2 of 9 | 0.222 [–, –] | 2.67 | 2.67 | 1.47 | fail |
| risk_quantile_skewt_base | 4 of 9 | 0.444 [–, –] | 3.22 | 3.22 | 2.75 | fail |
| risk_quantile_skewt_base+every_day | 3 of 9 | 0.333 [0.091, 0.556] | 2.22 | 2.22 | 1.47 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 3 of 9 | 0.333 [0.000, 0.636] | 2.22 | 2.22 | 1.53 | fail |
| risk_quantile_skewt_base+every_day+scarce | 3 of 9 | 0.333 [–, –] | 2.00 | 2.00 | 1.31 | fail |
| risk_quantile_skewt_base+every_day+persist | 2 of 9 | 0.222 [–, –] | 2.22 | 2.22 | 1.36 | fail |
| risk_quantile_skewt_base+every_day+gate | 3 of 9 | 0.333 [0.100, 0.545] | 2.22 | 2.22 | 1.47 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 3.78 | 3.78 | 3.67 | fail |
| persistence_logistic | 0 of 9 | 0.000 [0.000, 0.000] | 2.22 | 2.22 | 0.83 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 1.24 | 1.24 | 0.54 | pass |
| risk_gbm+every_day | 13 of 17 | 0.765 [0.538, 0.955] | 3.94 | 3.94 | 1.62 | fail |
| risk_gbm+every_day+shrunk | 10 of 17 | 0.588 [0.375, 0.818] | 1.71 | 1.71 | 0.69 | pass |
| risk_gbm+every_day+scarce | 13 of 17 | 0.765 [0.555, 0.955] | 3.94 | 3.94 | 1.62 | fail |
| risk_gbm+every_day+persist | 12 of 17 | 0.706 [0.478, 0.917] | 3.65 | 3.65 | 1.50 | fail |
| risk_gbm+every_day+gate | 12 of 17 | 0.706 [0.500, 0.917] | 3.12 | 3.12 | 1.06 | fail |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 1.24 | 1.24 | 0.59 | pass |
| risk_gbm_base+every_day | 13 of 17 | 0.765 [0.542, 0.950] | 3.94 | 3.94 | 1.62 | fail |
| risk_gbm_base+every_day+shrunk | 10 of 17 | 0.588 [0.368, 0.800] | 2.29 | 2.29 | 0.84 | fail |
| risk_gbm_base+every_day+scarce | 13 of 17 | 0.765 [0.529, 0.955] | 3.94 | 3.94 | 1.62 | fail |
| risk_gbm_base+every_day+persist | 12 of 17 | 0.706 [0.500, 0.917] | 3.65 | 3.65 | 1.50 | fail |
| risk_gbm_base+every_day+gate | 12 of 17 | 0.706 [0.476, 0.909] | 3.12 | 3.12 | 1.06 | fail |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_logistic+every_day | 11 of 17 | 0.647 [0.429, 0.857] | 2.88 | 2.88 | 0.97 | fail |
| risk_logistic+every_day+shrunk | 12 of 17 | 0.706 [0.476, 0.923] | 3.12 | 3.12 | 1.04 | fail |
| risk_logistic+every_day+scarce | 11 of 17 | 0.647 [0.437, 0.867] | 2.88 | 2.88 | 0.97 | fail |
| risk_logistic+every_day+persist | 13 of 17 | 0.765 [0.533, 0.952] | 4.35 | 4.35 | 1.51 | fail |
| risk_logistic+every_day+gate | 12 of 17 | 0.706 [0.500, 0.917] | 3.35 | 3.35 | 1.15 | fail |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_logistic_base+every_day | 9 of 17 | 0.529 [0.308, 0.751] | 2.29 | 2.29 | 0.78 | fail |
| risk_logistic_base+every_day+shrunk | 11 of 17 | 0.647 [0.438, 0.850] | 3.06 | 3.06 | 0.96 | fail |
| risk_logistic_base+every_day+scarce | 9 of 17 | 0.529 [0.320, 0.765] | 2.29 | 2.29 | 0.78 | fail |
| risk_logistic_base+every_day+persist | 11 of 17 | 0.647 [0.448, 0.867] | 1.88 | 1.88 | 0.66 | pass |
| risk_logistic_base+every_day+gate | 12 of 17 | 0.706 [0.500, 0.917] | 3.18 | 3.18 | 1.09 | fail |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.18 | 1.18 | 0.46 | pass |
| risk_quantile_skewt_base+every_day | 12 of 17 | 0.706 [0.499, 0.923] | 2.59 | 2.59 | 0.90 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 12 of 17 | 0.706 [0.500, 0.909] | 3.18 | 3.18 | 1.09 | fail |
| risk_quantile_skewt_base+every_day+scarce | 12 of 17 | 0.706 [0.500, 0.917] | 2.59 | 2.59 | 0.90 | fail |
| risk_quantile_skewt_base+every_day+persist | 12 of 17 | 0.706 [0.500, 0.917] | 3.18 | 3.18 | 1.25 | fail |
| risk_quantile_skewt_base+every_day+gate | 12 of 17 | 0.706 [0.476, 0.917] | 3.65 | 3.65 | 1.25 | fail |
| calendar_climatology | 10 of 17 | 0.588 [0.353, 0.812] | 5.65 | 5.65 | 2.34 | fail |
| persistence_logistic | 7 of 17 | 0.412 [0.185, 0.647] | 4.24 | 4.24 | 1.46 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 1.35 | 8 / 1.08 | 7 / 1.04 | 7 / 0.88 | 7 / 1.04 | pass (h = 1) |
| risk_gbm+every_day | 12 / 1.35 | 8 / 2.96 | 9 / 2.81 | 8 / 2.31 | 7 / 2.54 | fail |
| risk_gbm+every_day+shrunk | 12 / 1.38 | 8 / 1.31 | 7 / 1.08 | 7 / 1.00 | 7 / 1.23 | fail |
| risk_gbm+every_day+scarce | 12 / 1.31 | 9 / 2.96 | 9 / 2.92 | 8 / 2.27 | 7 / 2.46 | fail |
| risk_gbm+every_day+persist | 13 / 1.23 | 9 / 2.77 | 9 / 2.96 | 8 / 2.38 | 7 / 2.15 | pass (h = 1) |
| risk_gbm+every_day+gate | 12 / 0.85 | 8 / 2.54 | 8 / 2.96 | 7 / 2.15 | 8 / 2.42 | fail |
| risk_gbm_base | 13 / 1.50 | 8 / 0.96 | 7 / 1.27 | 7 / 1.12 | 7 / 1.08 | pass (h = 1) |
| risk_gbm_base+every_day | 11 / 2.92 | 7 / 2.92 | 9 / 2.88 | 6 / 1.81 | 6 / 2.65 | fail |
| risk_gbm_base+every_day+shrunk | 12 / 2.15 | 7 / 1.27 | 7 / 1.08 | 7 / 1.12 | 6 / 1.42 | fail |
| risk_gbm_base+every_day+scarce | 11 / 2.88 | 7 / 3.00 | 9 / 3.00 | 6 / 1.88 | 6 / 2.58 | fail |
| risk_gbm_base+every_day+persist | 12 / 2.50 | 8 / 2.81 | 9 / 2.88 | 8 / 2.50 | 6 / 2.38 | fail |
| risk_gbm_base+every_day+gate | 10 / 2.50 | 7 / 2.62 | 8 / 2.88 | 7 / 2.15 | 7 / 2.35 | fail |
| risk_logistic | 13 / 1.85 | 7 / 1.00 | 7 / 1.19 | 9 / 1.54 | 8 / 1.42 | pass (h = 1) |
| risk_logistic+every_day | 7 / 2.38 | 6 / 1.54 | 5 / 1.15 | 5 / 1.23 | 7 / 2.69 | fail |
| risk_logistic+every_day+shrunk | 14 / 2.85 | 6 / 0.92 | 5 / 0.88 | 5 / 1.00 | 6 / 2.31 | fail |
| risk_logistic+every_day+scarce | 7 / 2.35 | 6 / 1.50 | 5 / 1.08 | 5 / 1.15 | 7 / 2.62 | fail |
| risk_logistic+every_day+persist | 11 / 3.50 | 7 / 1.54 | 6 / 1.31 | 6 / 1.73 | 5 / 1.96 | fail |
| risk_logistic+every_day+gate | 8 / 2.35 | 6 / 1.54 | 6 / 1.58 | 5 / 1.19 | 8 / 3.00 | fail |
| risk_logistic_base | 13 / 1.77 | 6 / 1.00 | 6 / 1.00 | 7 / 1.12 | 8 / 1.15 | pass (h = 1) |
| risk_logistic_base+every_day | 7 / 1.62 | 5 / 1.38 | 7 / 1.62 | 6 / 1.50 | 7 / 2.31 | fail |
| risk_logistic_base+every_day+shrunk | 12 / 2.46 | 5 / 0.92 | 6 / 1.35 | 6 / 0.96 | 7 / 1.35 | fail |
| risk_logistic_base+every_day+scarce | 7 / 1.58 | 5 / 1.38 | 7 / 1.58 | 6 / 1.38 | 7 / 2.23 | fail |
| risk_logistic_base+every_day+persist | 9 / 1.73 | 6 / 1.50 | 7 / 1.31 | 8 / 1.81 | 5 / 1.35 | fail |
| risk_logistic_base+every_day+gate | 8 / 1.73 | 5 / 1.38 | 7 / 1.62 | 6 / 1.50 | 9 / 2.88 | fail |
| risk_quantile_skewt_base | 13 / 1.88 | 9 / 1.65 | 9 / 1.50 | 9 / 1.12 | 9 / 1.04 | pass (h = 1) |
| risk_quantile_skewt_base+every_day | 9 / 1.69 | 3 / 1.23 | 9 / 1.88 | 9 / 2.19 | 10 / 2.46 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 13 / 2.42 | 4 / 1.31 | 9 / 2.65 | 9 / 1.46 | 9 / 1.92 | fail |
| risk_quantile_skewt_base+every_day+scarce | 9 / 1.65 | 3 / 1.19 | 9 / 1.85 | 9 / 2.08 | 10 / 2.38 | fail |
| risk_quantile_skewt_base+every_day+persist | 10 / 2.15 | 4 / 1.23 | 9 / 2.27 | 11 / 2.85 | 8 / 2.00 | fail |
| risk_quantile_skewt_base+every_day+gate | 9 / 2.31 | 3 / 1.23 | 8 / 1.85 | 9 / 2.15 | 12 / 3.15 | fail |
| calendar_climatology | 9 / 4.85 | 10 / 4.88 | 10 / 4.92 | 10 / 4.96 | 10 / 5.00 | fail |
| persistence_logistic | 4 / 2.77 | 6 / 3.42 | 6 / 2.81 | 6 / 3.15 | 5 / 2.81 | fail |

## Weighted rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.80 | 1.38 | 0.80 | pass |
| risk_gbm+every_day | 17 of 26 | 0.654 [0.474, 0.812] | 2.18 | 5.12 | 2.18 | fail |
| risk_gbm+every_day+shrunk | 16 of 26 | 0.615 [0.438, 0.800] | 2.07 | 4.69 | 2.07 | fail |
| risk_gbm+every_day+scarce | 17 of 26 | 0.654 [0.483, 0.818] | 2.17 | 5.08 | 2.17 | fail |
| risk_gbm+every_day+persist | 16 of 26 | 0.615 [0.435, 0.800] | 2.23 | 5.04 | 2.23 | fail |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.481, 0.818] | 1.63 | 3.92 | 1.63 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.97 | 1.50 | 0.97 | pass |
| risk_gbm_base+every_day | 18 of 26 | 0.692 [0.520, 0.850] | 2.28 | 5.19 | 2.28 | fail |
| risk_gbm_base+every_day+shrunk | 17 of 26 | 0.654 [0.471, 0.833] | 2.14 | 4.62 | 2.14 | fail |
| risk_gbm_base+every_day+scarce | 18 of 26 | 0.692 [0.522, 0.857] | 2.27 | 5.15 | 2.27 | fail |
| risk_gbm_base+every_day+persist | 16 of 26 | 0.615 [0.423, 0.800] | 2.22 | 5.00 | 2.22 | fail |
| risk_gbm_base+every_day+gate | 18 of 26 | 0.692 [0.517, 0.850] | 1.62 | 3.81 | 1.62 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 1.74 | 2.42 | 1.74 | pass |
| risk_logistic+every_day | 17 of 26 | 0.654 [0.480, 0.826] | 2.28 | 5.35 | 2.28 | fail |
| risk_logistic+every_day+shrunk | 18 of 26 | 0.692 [0.522, 0.852] | 2.36 | 5.19 | 2.36 | fail |
| risk_logistic+every_day+scarce | 17 of 26 | 0.654 [0.476, 0.818] | 2.27 | 5.31 | 2.27 | fail |
| risk_logistic+every_day+persist | 17 of 26 | 0.654 [0.481, 0.818] | 2.34 | 5.19 | 2.34 | fail |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.520, 0.857] | 2.19 | 4.42 | 2.19 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 1.65 | 2.31 | 1.65 | pass |
| risk_logistic_base+every_day | 13 of 26 | 0.500 [0.321, 0.679] | 2.26 | 5.04 | 2.26 | fail |
| risk_logistic_base+every_day+shrunk | 17 of 26 | 0.654 [0.480, 0.821] | 2.34 | 5.08 | 2.34 | fail |
| risk_logistic_base+every_day+scarce | 13 of 26 | 0.500 [0.321, 0.667] | 2.18 | 4.92 | 2.18 | fail |
| risk_logistic_base+every_day+persist | 14 of 26 | 0.538 [0.364, 0.719] | 2.31 | 5.12 | 2.31 | fail |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.815] | 2.01 | 4.12 | 2.01 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 1.62 | 2.31 | 1.62 | pass |
| risk_quantile_skewt_base+every_day | 16 of 26 | 0.615 [0.444, 0.792] | 2.63 | 5.62 | 2.63 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 19 of 26 | 0.731 [0.560, 0.882] | 3.02 | 6.04 | 3.02 | fail |
| risk_quantile_skewt_base+every_day+scarce | 16 of 26 | 0.615 [0.429, 0.781] | 2.56 | 5.46 | 2.56 | fail |
| risk_quantile_skewt_base+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 2.46 | 5.35 | 2.46 | fail |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.467, 0.824] | 2.00 | 4.15 | 2.00 | pass |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 3.75 | 6.69 | 3.75 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 3.25 | 7.04 | 3.25 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 1.48 | 2.12 | 1.48 | pass |
| risk_gbm+every_day | 17 of 26 | 0.654 [0.480, 0.818] | 3.79 | 7.88 | 3.79 | fail |
| risk_gbm+every_day+shrunk | 16 of 26 | 0.615 [0.429, 0.792] | 3.66 | 7.46 | 3.66 | fail |
| risk_gbm+every_day+scarce | 17 of 26 | 0.654 [0.480, 0.815] | 3.60 | 7.58 | 3.60 | fail |
| risk_gbm+every_day+persist | 16 of 26 | 0.615 [0.429, 0.792] | 3.09 | 6.46 | 3.09 | fail |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.480, 0.818] | 3.67 | 7.35 | 3.67 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 1.59 | 2.19 | 1.59 | pass |
| risk_gbm_base+every_day | 18 of 26 | 0.692 [0.522, 0.846] | 3.85 | 7.96 | 3.85 | fail |
| risk_gbm_base+every_day+shrunk | 17 of 26 | 0.654 [0.471, 0.833] | 3.65 | 7.35 | 3.65 | fail |
| risk_gbm_base+every_day+scarce | 18 of 26 | 0.692 [0.522, 0.857] | 3.65 | 7.65 | 3.65 | fail |
| risk_gbm_base+every_day+persist | 16 of 26 | 0.615 [0.429, 0.793] | 3.24 | 6.69 | 3.24 | fail |
| risk_gbm_base+every_day+gate | 18 of 26 | 0.692 [0.519, 0.857] | 3.64 | 7.27 | 3.64 | fail |
| risk_logistic | 16 of 26 | 0.615 [0.440, 0.800] | 2.55 | 3.31 | 2.55 | fail |
| risk_logistic+every_day | 17 of 26 | 0.654 [0.472, 0.818] | 3.67 | 7.85 | 3.67 | fail |
| risk_logistic+every_day+shrunk | 18 of 26 | 0.692 [0.519, 0.857] | 3.65 | 7.54 | 3.65 | fail |
| risk_logistic+every_day+scarce | 17 of 26 | 0.654 [0.480, 0.818] | 3.48 | 7.54 | 3.48 | fail |
| risk_logistic+every_day+persist | 17 of 26 | 0.654 [0.480, 0.826] | 3.39 | 7.19 | 3.39 | fail |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.516, 0.842] | 4.12 | 8.00 | 4.12 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.759] | 2.18 | 2.88 | 2.18 | fail |
| risk_logistic_base+every_day | 13 of 26 | 0.500 [0.321, 0.679] | 3.33 | 7.15 | 3.33 | fail |
| risk_logistic_base+every_day+shrunk | 17 of 26 | 0.654 [0.481, 0.818] | 3.60 | 7.50 | 3.60 | fail |
| risk_logistic_base+every_day+scarce | 13 of 26 | 0.500 [0.333, 0.667] | 3.13 | 6.85 | 3.13 | fail |
| risk_logistic_base+every_day+persist | 14 of 26 | 0.538 [0.370, 0.710] | 3.08 | 6.81 | 3.08 | fail |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.478, 0.824] | 4.12 | 8.04 | 4.12 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.400, 0.759] | 2.14 | 2.88 | 2.14 | fail |
| risk_quantile_skewt_base+every_day | 16 of 26 | 0.615 [0.440, 0.778] | 4.08 | 8.15 | 4.08 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 19 of 26 | 0.731 [0.550, 0.880] | 4.55 | 8.73 | 4.55 | fail |
| risk_quantile_skewt_base+every_day+scarce | 16 of 26 | 0.615 [0.444, 0.778] | 3.88 | 7.85 | 3.88 | fail |
| risk_quantile_skewt_base+every_day+persist | 15 of 26 | 0.577 [0.393, 0.750] | 4.05 | 7.92 | 4.05 | fail |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.818] | 3.90 | 7.69 | 3.90 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.278, 0.650] | 3.90 | 6.85 | 3.90 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.276, 0.667] | 4.09 | 8.46 | 4.09 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.61 | 1.89 | 1.61 | fail |
| risk_gbm+every_day | 4 of 9 | 0.444 [0.167, 0.714] | 1.75 | 3.33 | 1.75 | fail |
| risk_gbm+every_day+shrunk | 3 of 9 | 0.333 [–, –] | 1.97 | 3.33 | 1.97 | fail |
| risk_gbm+every_day+scarce | 4 of 9 | 0.444 [0.143, 0.714] | 1.53 | 3.22 | 1.53 | fail |
| risk_gbm+every_day+persist | 3 of 9 | 0.333 [–, –] | 1.44 | 2.44 | 1.44 | fail |
| risk_gbm+every_day+gate | 4 of 9 | 0.444 [0.167, 0.728] | 2.58 | 4.56 | 2.58 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.06 | 2.33 | 2.06 | fail |
| risk_gbm_base+every_day | 5 of 9 | 0.556 [–, –] | 2.14 | 3.78 | 2.14 | fail |
| risk_gbm_base+every_day+shrunk | 4 of 9 | 0.444 [–, –] | 2.22 | 3.78 | 2.22 | fail |
| risk_gbm_base+every_day+scarce | 5 of 9 | 0.556 [–, –] | 1.92 | 3.33 | 1.92 | fail |
| risk_gbm_base+every_day+persist | 3 of 9 | 0.333 [–, –] | 1.50 | 2.56 | 1.50 | fail |
| risk_gbm_base+every_day+gate | 5 of 9 | 0.556 [–, –] | 2.61 | 4.44 | 2.61 | fail |
| risk_logistic | 6 of 9 | 0.667 [0.307, 1.000] | 4.39 | 4.89 | 4.39 | fail |
| risk_logistic+every_day | 4 of 9 | 0.444 [–, –] | 1.97 | 3.56 | 1.97 | fail |
| risk_logistic+every_day+shrunk | 5 of 9 | 0.556 [0.250, 0.824] | 2.31 | 4.00 | 2.31 | fail |
| risk_logistic+every_day+scarce | 4 of 9 | 0.444 [0.167, 0.700] | 1.92 | 3.44 | 1.92 | fail |
| risk_logistic+every_day+persist | 4 of 9 | 0.444 [–, –] | 1.47 | 2.56 | 1.47 | fail |
| risk_logistic+every_day+gate | 5 of 9 | 0.556 [–, –] | 3.56 | 5.33 | 3.56 | fail |
| risk_logistic_base | 5 of 9 | 0.556 [–, –] | 3.67 | 4.00 | 3.67 | fail |
| risk_logistic_base+every_day | 3 of 9 | 0.333 [0.091, 0.556] | 2.14 | 3.67 | 2.14 | fail |
| risk_logistic_base+every_day+shrunk | 4 of 9 | 0.444 [0.143, 0.714] | 2.33 | 3.89 | 2.33 | fail |
| risk_logistic_base+every_day+scarce | 3 of 9 | 0.333 [–, –] | 1.92 | 3.33 | 1.92 | fail |
| risk_logistic_base+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.39 | 2.56 | 1.39 | fail |
| risk_logistic_base+every_day+gate | 4 of 9 | 0.444 [–, –] | 3.17 | 5.00 | 3.17 | fail |
| risk_quantile_skewt_base | 5 of 9 | 0.556 [–, –] | 3.81 | 4.44 | 3.81 | fail |
| risk_quantile_skewt_base+every_day | 4 of 9 | 0.444 [0.167, 0.700] | 2.56 | 4.33 | 2.56 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 6 of 9 | 0.667 [0.375, 0.909] | 3.50 | 5.33 | 3.50 | fail |
| risk_quantile_skewt_base+every_day+scarce | 4 of 9 | 0.444 [–, –] | 2.53 | 4.22 | 2.53 | fail |
| risk_quantile_skewt_base+every_day+persist | 3 of 9 | 0.333 [–, –] | 2.06 | 3.00 | 2.06 | fail |
| risk_quantile_skewt_base+every_day+gate | 4 of 9 | 0.444 [0.167, 0.727] | 3.22 | 4.89 | 3.22 | fail |
| calendar_climatology | 0 of 9 | 0.000 [0.000, 0.000] | 4.56 | 4.67 | 4.56 | fail |
| persistence_logistic | 1 of 9 | 0.111 [0.000, 0.333] | 2.86 | 4.89 | 2.86 | fail |

### (e) in 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.381, 0.812] | 0.54 | 1.24 | 0.54 | pass |
| risk_gbm+every_day | 13 of 17 | 0.765 [0.538, 0.955] | 2.59 | 6.06 | 2.59 | fail |
| risk_gbm+every_day+shrunk | 13 of 17 | 0.765 [0.538, 1.000] | 2.22 | 5.53 | 2.22 | fail |
| risk_gbm+every_day+scarce | 13 of 17 | 0.765 [0.555, 0.955] | 2.59 | 6.06 | 2.59 | fail |
| risk_gbm+every_day+persist | 13 of 17 | 0.765 [0.533, 0.952] | 2.65 | 6.41 | 2.65 | fail |
| risk_gbm+every_day+gate | 13 of 17 | 0.765 [0.545, 1.000] | 1.26 | 3.71 | 1.26 | pass |
| risk_gbm_base | 10 of 17 | 0.588 [0.381, 0.812] | 0.59 | 1.24 | 0.59 | pass |
| risk_gbm_base+every_day | 13 of 17 | 0.765 [0.542, 0.950] | 2.65 | 6.18 | 2.65 | fail |
| risk_gbm_base+every_day+shrunk | 13 of 17 | 0.765 [0.550, 0.950] | 2.22 | 5.53 | 2.22 | fail |
| risk_gbm_base+every_day+scarce | 13 of 17 | 0.765 [0.529, 0.955] | 2.65 | 6.18 | 2.65 | fail |
| risk_gbm_base+every_day+persist | 13 of 17 | 0.765 [0.550, 0.952] | 2.65 | 6.41 | 2.65 | fail |
| risk_gbm_base+every_day+gate | 13 of 17 | 0.765 [0.538, 0.945] | 1.26 | 3.71 | 1.26 | pass |
| risk_logistic | 10 of 17 | 0.588 [0.368, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_logistic+every_day | 13 of 17 | 0.765 [0.533, 1.000] | 2.46 | 6.29 | 2.46 | fail |
| risk_logistic+every_day+shrunk | 13 of 17 | 0.765 [0.533, 0.947] | 2.40 | 6.06 | 2.40 | fail |
| risk_logistic+every_day+scarce | 13 of 17 | 0.765 [0.542, 0.955] | 2.46 | 6.29 | 2.46 | fail |
| risk_logistic+every_day+persist | 13 of 17 | 0.765 [0.533, 0.952] | 2.82 | 6.59 | 2.82 | fail |
| risk_logistic+every_day+gate | 13 of 17 | 0.765 [0.552, 0.955] | 1.47 | 3.94 | 1.47 | pass |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_logistic_base+every_day | 10 of 17 | 0.588 [0.363, 0.824] | 2.32 | 6.00 | 2.32 | fail |
| risk_logistic_base+every_day+shrunk | 13 of 17 | 0.765 [0.538, 0.947] | 2.40 | 6.06 | 2.40 | fail |
| risk_logistic_base+every_day+scarce | 10 of 17 | 0.588 [0.364, 0.833] | 2.32 | 6.00 | 2.32 | fail |
| risk_logistic_base+every_day+persist | 12 of 17 | 0.706 [0.500, 0.929] | 2.79 | 6.53 | 2.79 | fail |
| risk_logistic_base+every_day+gate | 13 of 17 | 0.765 [0.550, 0.952] | 1.47 | 3.94 | 1.47 | pass |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.46 | 1.18 | 0.46 | pass |
| risk_quantile_skewt_base+every_day | 12 of 17 | 0.706 [0.499, 0.923] | 2.74 | 6.59 | 2.74 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 13 of 17 | 0.765 [0.550, 0.947] | 2.76 | 6.71 | 2.76 | fail |
| risk_quantile_skewt_base+every_day+scarce | 12 of 17 | 0.706 [0.500, 0.917] | 2.74 | 6.59 | 2.74 | fail |
| risk_quantile_skewt_base+every_day+persist | 12 of 17 | 0.706 [0.500, 0.917] | 2.91 | 6.76 | 2.91 | fail |
| risk_quantile_skewt_base+every_day+gate | 13 of 17 | 0.765 [0.545, 0.955] | 1.44 | 3.82 | 1.44 | pass |
| calendar_climatology | 12 of 17 | 0.706 [0.474, 0.900] | 3.32 | 7.76 | 3.32 | fail |
| persistence_logistic | 11 of 17 | 0.647 [0.412, 0.889] | 3.54 | 8.18 | 3.54 | fail |

### (b1) one horizon alone: onsets warned / false alarms per onset at each horizon

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | passes at some horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 13 / 0.80 | 8 / 0.68 | 7 / 0.59 | 7 / 0.47 | 7 / 0.76 | pass (h = 1) |
| risk_gbm+every_day | 15 / 2.18 | 12 / 2.07 | 11 / 2.06 | 10 / 1.70 | 11 / 1.94 | fail |
| risk_gbm+every_day+shrunk | 15 / 1.93 | 10 / 1.71 | 11 / 2.03 | 10 / 1.89 | 10 / 2.07 | pass (h = 1) |
| risk_gbm+every_day+scarce | 15 / 2.17 | 12 / 2.04 | 11 / 1.98 | 10 / 1.62 | 11 / 1.87 | fail |
| risk_gbm+every_day+persist | 15 / 1.69 | 12 / 1.87 | 11 / 2.23 | 11 / 1.65 | 9 / 1.66 | pass (h = 1) |
| risk_gbm+every_day+gate | 13 / 1.62 | 9 / 1.63 | 8 / 1.58 | 9 / 1.48 | 11 / 1.61 | pass (h = 1) |
| risk_gbm_base | 14 / 0.97 | 8 / 0.64 | 7 / 0.91 | 7 / 0.66 | 7 / 0.76 | pass (h = 1) |
| risk_gbm_base+every_day | 16 / 2.28 | 11 / 2.03 | 11 / 2.06 | 10 / 1.91 | 10 / 2.09 | fail |
| risk_gbm_base+every_day+shrunk | 15 / 2.14 | 10 / 1.69 | 11 / 2.01 | 10 / 2.06 | 9 / 2.05 | fail |
| risk_gbm_base+every_day+scarce | 16 / 2.27 | 11 / 2.00 | 11 / 1.98 | 10 / 1.83 | 10 / 2.01 | fail |
| risk_gbm_base+every_day+persist | 15 / 1.97 | 11 / 1.84 | 11 / 2.22 | 11 / 1.84 | 8 / 1.81 | pass (h = 1) |
| risk_gbm_base+every_day+gate | 13 / 1.57 | 9 / 1.56 | 8 / 1.60 | 9 / 1.61 | 10 / 1.62 | pass (h = 1) |
| risk_logistic | 14 / 1.74 | 7 / 1.28 | 8 / 1.34 | 10 / 1.71 | 9 / 1.58 | pass (h = 1) |
| risk_logistic+every_day | 15 / 2.28 | 11 / 2.02 | 11 / 2.02 | 9 / 1.85 | 12 / 2.20 | fail |
| risk_logistic+every_day+shrunk | 15 / 2.16 | 12 / 2.24 | 10 / 1.88 | 11 / 1.97 | 13 / 2.36 | fail |
| risk_logistic+every_day+scarce | 15 / 2.27 | 11 / 1.99 | 11 / 1.94 | 9 / 1.76 | 12 / 2.12 | fail |
| risk_logistic+every_day+persist | 15 / 2.15 | 11 / 1.83 | 11 / 1.82 | 9 / 2.08 | 12 / 2.34 | fail |
| risk_logistic+every_day+gate | 12 / 1.79 | 8 / 1.60 | 8 / 1.58 | 8 / 1.89 | 12 / 2.19 | fail |
| risk_logistic_base | 14 / 1.65 | 8 / 1.22 | 7 / 1.16 | 7 / 1.01 | 8 / 1.47 | pass (h = 1) |
| risk_logistic_base+every_day | 11 / 1.97 | 11 / 1.96 | 12 / 2.00 | 10 / 1.88 | 12 / 2.26 | fail |
| risk_logistic_base+every_day+shrunk | 16 / 2.27 | 12 / 2.12 | 12 / 1.99 | 10 / 2.01 | 12 / 2.34 | fail |
| risk_logistic_base+every_day+scarce | 11 / 1.96 | 11 / 1.93 | 12 / 1.92 | 10 / 1.81 | 12 / 2.18 | fail |
| risk_logistic_base+every_day+persist | 13 / 1.86 | 11 / 1.77 | 12 / 1.79 | 11 / 2.14 | 12 / 2.31 | pass (h = 1) |
| risk_logistic_base+every_day+gate | 13 / 2.01 | 9 / 1.56 | 9 / 1.67 | 9 / 1.71 | 13 / 1.91 | pass (h = 5) |
| risk_quantile_skewt_base | 15 / 1.62 | 9 / 1.44 | 9 / 1.00 | 9 / 0.56 | 9 / 0.51 | pass (h = 1) |
| risk_quantile_skewt_base+every_day | 15 / 2.23 | 11 / 1.59 | 13 / 2.63 | 12 / 2.05 | 13 / 2.37 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 17 / 2.66 | 12 / 2.34 | 14 / 3.02 | 13 / 2.31 | 14 / 2.59 | fail |
| risk_quantile_skewt_base+every_day+scarce | 15 / 2.22 | 11 / 1.56 | 13 / 2.56 | 12 / 1.97 | 13 / 2.31 | fail |
| risk_quantile_skewt_base+every_day+persist | 15 / 2.23 | 11 / 1.83 | 13 / 2.40 | 12 / 2.29 | 12 / 2.46 | fail |
| risk_quantile_skewt_base+every_day+gate | 13 / 1.87 | 8 / 1.46 | 10 / 1.76 | 10 / 1.87 | 13 / 2.00 | pass (h = 1) |
| calendar_climatology | 12 / 3.75 | 10 / 3.17 | 10 / 3.21 | 10 / 3.25 | 10 / 3.29 | fail |
| persistence_logistic | 11 / 3.25 | 7 / 2.07 | 10 / 2.68 | 8 / 2.38 | 8 / 1.86 | fail |

