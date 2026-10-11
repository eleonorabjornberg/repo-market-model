# Tier 1 of the false-alarm controls under readings (a), (b) and (e) (#532)

## Flat rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 1.38 | 1.38 | 0.77 | pass |
| risk_gbm+every_day | 15 of 26 | 0.577 [0.385, 0.760] | 3.00 | 3.00 | 1.22 | fail |
| risk_gbm+every_day+shrunk | 12 of 26 | 0.462 [0.286, 0.650] | 1.27 | 1.27 | 0.56 | fail |
| risk_gbm+every_day+scarce | 15 of 26 | 0.577 [0.389, 0.760] | 3.12 | 3.12 | 1.25 | fail |
| risk_gbm+every_day+persist | 14 of 26 | 0.538 [0.360, 0.715] | 2.96 | 2.96 | 1.23 | fail |
| risk_gbm+every_day+gate | 15 of 26 | 0.577 [0.400, 0.750] | 2.92 | 2.92 | 1.10 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 | 1.50 | 0.97 | pass |
| risk_gbm_base+every_day | 15 of 26 | 0.577 [0.389, 0.769] | 2.96 | 2.96 | 1.23 | fail |
| risk_gbm_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.684] | 2.42 | 2.42 | 1.11 | fail |
| risk_gbm_base+every_day+scarce | 15 of 26 | 0.577 [0.385, 0.769] | 3.00 | 3.00 | 1.26 | fail |
| risk_gbm_base+every_day+persist | 14 of 26 | 0.538 [0.353, 0.737] | 2.88 | 2.88 | 1.24 | fail |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.393, 0.750] | 2.88 | 2.88 | 1.18 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 1.85 | 1.85 | 1.19 | pass |
| risk_logistic+every_day | 14 of 26 | 0.538 [0.375, 0.707] | 2.62 | 2.62 | 1.05 | fail |
| risk_logistic+every_day+shrunk | 15 of 26 | 0.577 [0.407, 0.750] | 2.85 | 2.85 | 1.20 | fail |
| risk_logistic+every_day+scarce | 14 of 26 | 0.538 [0.375, 0.700] | 2.54 | 2.54 | 0.99 | fail |
| risk_logistic+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 3.50 | 3.50 | 1.41 | fail |
| risk_logistic+every_day+gate | 15 of 26 | 0.577 [0.414, 0.742] | 2.96 | 2.96 | 1.17 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 1.81 | 1.81 | 1.18 | pass |
| risk_logistic_base+every_day | 11 of 26 | 0.423 [0.259, 0.593] | 2.31 | 2.31 | 0.94 | fail |
| risk_logistic_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 2.50 | 2.50 | 0.92 | fail |
| risk_logistic_base+every_day+scarce | 11 of 26 | 0.423 [0.250, 0.600] | 2.23 | 2.23 | 0.88 | fail |
| risk_logistic_base+every_day+persist | 13 of 26 | 0.500 [0.333, 0.679] | 1.81 | 1.81 | 0.79 | pass |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.368, 0.714] | 2.88 | 2.88 | 1.14 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 1.81 | 1.81 | 1.20 | pass |
| risk_quantile_skewt_base+every_day | 15 of 26 | 0.577 [0.409, 0.750] | 2.46 | 2.46 | 1.10 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 14 of 26 | 0.538 [0.375, 0.722] | 2.62 | 2.62 | 1.19 | fail |
| risk_quantile_skewt_base+every_day+scarce | 15 of 26 | 0.577 [0.400, 0.739] | 2.38 | 2.38 | 1.04 | fail |
| risk_quantile_skewt_base+every_day+persist | 14 of 26 | 0.538 [0.368, 0.706] | 2.85 | 2.85 | 1.16 | fail |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.741] | 3.15 | 3.15 | 1.33 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 5.00 | 5.00 | 2.80 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 3.42 | 3.42 | 1.17 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 2.12 | 2.12 | 1.45 | fail |
| risk_gbm+every_day | 15 of 26 | 0.577 [0.385, 0.769] | 5.81 | 5.81 | 2.58 | fail |
| risk_gbm+every_day+shrunk | 12 of 26 | 0.462 [0.286, 0.650] | 2.96 | 2.96 | 1.47 | fail |
| risk_gbm+every_day+scarce | 15 of 26 | 0.577 [0.381, 0.759] | 5.65 | 5.65 | 2.51 | fail |
| risk_gbm+every_day+persist | 14 of 26 | 0.538 [0.348, 0.722] | 5.46 | 5.46 | 2.42 | fail |
| risk_gbm+every_day+gate | 15 of 26 | 0.577 [0.400, 0.750] | 5.65 | 5.65 | 2.54 | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.722] | 2.04 | 2.04 | 1.43 | fail |
| risk_gbm_base+every_day | 15 of 26 | 0.577 [0.389, 0.765] | 5.88 | 5.88 | 2.67 | fail |
| risk_gbm_base+every_day+shrunk | 13 of 26 | 0.500 [0.323, 0.677] | 3.73 | 3.73 | 1.92 | fail |
| risk_gbm_base+every_day+scarce | 15 of 26 | 0.577 [0.381, 0.781] | 5.73 | 5.73 | 2.60 | fail |
| risk_gbm_base+every_day+persist | 14 of 26 | 0.538 [0.346, 0.731] | 5.69 | 5.69 | 2.58 | fail |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.400, 0.760] | 5.96 | 5.96 | 2.77 | fail |
| risk_logistic | 14 of 26 | 0.538 [0.364, 0.710] | 2.42 | 2.42 | 1.75 | fail |
| risk_logistic+every_day | 14 of 26 | 0.538 [0.375, 0.692] | 4.77 | 4.77 | 2.15 | fail |
| risk_logistic+every_day+shrunk | 15 of 26 | 0.577 [0.393, 0.759] | 4.38 | 4.38 | 2.04 | fail |
| risk_logistic+every_day+scarce | 14 of 26 | 0.538 [0.375, 0.696] | 4.54 | 4.54 | 2.04 | fail |
| risk_logistic+every_day+persist | 15 of 26 | 0.577 [0.400, 0.762] | 5.15 | 5.15 | 2.18 | fail |
| risk_logistic+every_day+gate | 15 of 26 | 0.577 [0.417, 0.741] | 5.35 | 5.35 | 2.44 | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.320, 0.677] | 2.00 | 2.00 | 1.38 | pass |
| risk_logistic_base+every_day | 11 of 26 | 0.423 [0.250, 0.591] | 4.38 | 4.38 | 1.90 | fail |
| risk_logistic_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 3.73 | 3.73 | 1.54 | fail |
| risk_logistic_base+every_day+scarce | 11 of 26 | 0.423 [0.261, 0.591] | 4.15 | 4.15 | 1.79 | fail |
| risk_logistic_base+every_day+persist | 13 of 26 | 0.500 [0.333, 0.667] | 4.50 | 4.50 | 1.78 | fail |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.367, 0.720] | 5.04 | 5.04 | 2.20 | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.364, 0.720] | 2.50 | 2.50 | 1.76 | fail |
| risk_quantile_skewt_base+every_day | 15 of 26 | 0.577 [0.407, 0.739] | 4.96 | 4.96 | 2.16 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 14 of 26 | 0.538 [0.357, 0.714] | 4.92 | 4.92 | 2.33 | fail |
| risk_quantile_skewt_base+every_day+scarce | 15 of 26 | 0.577 [0.400, 0.737] | 4.77 | 4.77 | 2.07 | fail |
| risk_quantile_skewt_base+every_day+persist | 14 of 26 | 0.538 [0.357, 0.714] | 5.65 | 5.65 | 2.53 | fail |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.742] | 5.15 | 5.15 | 2.32 | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.572] | 5.38 | 5.38 | 2.98 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.107, 0.452] | 5.73 | 5.73 | 2.23 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.67 | 1.67 | 1.22 | fail |
| risk_gbm+every_day | 2 of 9 | 0.222 [0.000, 0.545] | 2.33 | 2.33 | 1.11 | fail |
| risk_gbm+every_day+shrunk | 2 of 9 | 0.222 [–, –] | 1.78 | 1.78 | 1.03 | fail |
| risk_gbm+every_day+scarce | 2 of 9 | 0.222 [0.000, 0.500] | 2.33 | 2.33 | 1.11 | fail |
| risk_gbm+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.78 | 1.78 | 0.89 | fail |
| risk_gbm+every_day+gate | 3 of 9 | 0.333 [0.000, 0.667] | 2.78 | 2.78 | 1.44 | fail |
| risk_gbm_base | 4 of 9 | 0.444 [–, –] | 2.00 | 2.00 | 1.69 | fail |
| risk_gbm_base+every_day | 2 of 9 | 0.222 [–, –] | 2.33 | 2.33 | 1.22 | fail |
| risk_gbm_base+every_day+shrunk | 3 of 9 | 0.333 [–, –] | 2.67 | 2.67 | 1.61 | fail |
| risk_gbm_base+every_day+scarce | 2 of 9 | 0.222 [–, –] | 2.44 | 2.44 | 1.22 | fail |
| risk_gbm_base+every_day+persist | 2 of 9 | 0.222 [–, –] | 2.44 | 2.44 | 1.47 | fail |
| risk_gbm_base+every_day+gate | 3 of 9 | 0.333 [–, –] | 2.89 | 2.89 | 1.58 | fail |
| risk_logistic | 4 of 9 | 0.444 [0.111, 0.750] | 3.11 | 3.11 | 2.78 | fail |
| risk_logistic+every_day | 3 of 9 | 0.333 [–, –] | 2.56 | 2.56 | 1.47 | fail |
| risk_logistic+every_day+shrunk | 3 of 9 | 0.333 [0.000, 0.636] | 2.78 | 2.78 | 1.64 | fail |
| risk_logistic+every_day+scarce | 3 of 9 | 0.333 [0.091, 0.556] | 2.44 | 2.44 | 1.44 | fail |
| risk_logistic+every_day+persist | 2 of 9 | 0.222 [–, –] | 2.00 | 2.00 | 1.33 | fail |
| risk_logistic+every_day+gate | 3 of 9 | 0.333 [–, –] | 2.44 | 2.44 | 1.44 | fail |
| risk_logistic_base | 3 of 9 | 0.333 [–, –] | 2.44 | 2.44 | 2.08 | fail |
| risk_logistic_base+every_day | 2 of 9 | 0.222 [0.000, 0.444] | 2.67 | 2.67 | 1.47 | fail |
| risk_logistic_base+every_day+shrunk | 2 of 9 | 0.222 [0.000, 0.444] | 1.44 | 1.44 | 1.03 | fail |
| risk_logistic_base+every_day+scarce | 2 of 9 | 0.222 [–, –] | 2.33 | 2.33 | 1.33 | fail |
| risk_logistic_base+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.89 | 1.89 | 1.11 | fail |
| risk_logistic_base+every_day+gate | 2 of 9 | 0.222 [–, –] | 2.67 | 2.67 | 1.47 | fail |
| risk_quantile_skewt_base | 4 of 9 | 0.444 [–, –] | 3.11 | 3.11 | 2.64 | fail |
| risk_quantile_skewt_base+every_day | 3 of 9 | 0.333 [0.091, 0.556] | 2.22 | 2.22 | 1.47 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 2 of 9 | 0.222 [0.000, 0.444] | 2.44 | 2.44 | 1.78 | fail |
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
| risk_logistic+every_day | 11 of 17 | 0.647 [0.429, 0.857] | 2.82 | 2.82 | 0.96 | fail |
| risk_logistic+every_day+shrunk | 12 of 17 | 0.706 [0.476, 0.923] | 3.12 | 3.12 | 1.04 | fail |
| risk_logistic+every_day+scarce | 11 of 17 | 0.647 [0.437, 0.867] | 2.82 | 2.82 | 0.96 | fail |
| risk_logistic+every_day+persist | 13 of 17 | 0.765 [0.533, 0.952] | 4.29 | 4.29 | 1.46 | fail |
| risk_logistic+every_day+gate | 12 of 17 | 0.706 [0.500, 0.917] | 3.35 | 3.35 | 1.15 | fail |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.47 | 1.47 | 0.71 | pass |
| risk_logistic_base+every_day | 9 of 17 | 0.529 [0.308, 0.751] | 2.29 | 2.29 | 0.78 | fail |
| risk_logistic_base+every_day+shrunk | 11 of 17 | 0.647 [0.438, 0.850] | 3.06 | 3.06 | 0.96 | fail |
| risk_logistic_base+every_day+scarce | 9 of 17 | 0.529 [0.320, 0.765] | 2.29 | 2.29 | 0.78 | fail |
| risk_logistic_base+every_day+persist | 11 of 17 | 0.647 [0.448, 0.867] | 1.88 | 1.88 | 0.66 | pass |
| risk_logistic_base+every_day+gate | 12 of 17 | 0.706 [0.500, 0.917] | 3.18 | 3.18 | 1.09 | fail |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 1.12 | 1.12 | 0.44 | pass |
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
| risk_gbm | 13 / 1.38 | 8 / 1.08 | 7 / 1.08 | 7 / 0.92 | 7 / 1.04 | pass (h = 1) |
| risk_gbm+every_day | 12 / 1.35 | 8 / 2.92 | 9 / 3.00 | 8 / 2.04 | 7 / 2.54 | fail |
| risk_gbm+every_day+shrunk | 12 / 1.15 | 7 / 1.27 | 7 / 1.04 | 7 / 0.96 | 6 / 1.15 | fail |
| risk_gbm+every_day+scarce | 12 / 1.31 | 8 / 2.92 | 9 / 3.12 | 8 / 2.00 | 7 / 2.46 | fail |
| risk_gbm+every_day+persist | 13 / 1.23 | 8 / 2.73 | 9 / 2.96 | 8 / 2.35 | 6 / 2.12 | pass (h = 1) |
| risk_gbm+every_day+gate | 12 / 0.85 | 7 / 2.58 | 8 / 2.92 | 7 / 2.08 | 8 / 2.46 | fail |
| risk_gbm_base | 13 / 1.50 | 8 / 1.00 | 7 / 1.23 | 7 / 1.12 | 7 / 1.08 | pass (h = 1) |
| risk_gbm_base+every_day | 11 / 2.69 | 7 / 2.96 | 9 / 2.88 | 6 / 1.81 | 6 / 2.62 | fail |
| risk_gbm_base+every_day+shrunk | 13 / 2.42 | 6 / 1.31 | 7 / 1.04 | 7 / 1.12 | 6 / 1.42 | fail |
| risk_gbm_base+every_day+scarce | 11 / 2.65 | 7 / 3.00 | 9 / 3.00 | 6 / 1.88 | 6 / 2.54 | fail |
| risk_gbm_base+every_day+persist | 12 / 2.38 | 7 / 2.81 | 9 / 2.88 | 8 / 2.50 | 6 / 2.38 | fail |
| risk_gbm_base+every_day+gate | 11 / 2.73 | 6 / 2.62 | 8 / 2.88 | 7 / 2.15 | 7 / 2.31 | fail |
| risk_logistic | 13 / 1.85 | 7 / 1.00 | 8 / 1.19 | 9 / 1.62 | 8 / 1.46 | pass (h = 1) |
| risk_logistic+every_day | 8 / 2.38 | 6 / 1.54 | 5 / 1.12 | 5 / 1.15 | 8 / 2.62 | fail |
| risk_logistic+every_day+shrunk | 14 / 2.85 | 6 / 0.92 | 5 / 0.85 | 5 / 0.88 | 6 / 2.35 | fail |
| risk_logistic+every_day+scarce | 8 / 2.35 | 6 / 1.50 | 5 / 1.04 | 5 / 1.08 | 8 / 2.54 | fail |
| risk_logistic+every_day+persist | 12 / 3.50 | 7 / 1.54 | 6 / 1.27 | 6 / 1.65 | 5 / 2.00 | fail |
| risk_logistic+every_day+gate | 9 / 2.35 | 6 / 1.54 | 6 / 1.54 | 5 / 1.12 | 9 / 2.96 | fail |
| risk_logistic_base | 13 / 1.81 | 6 / 1.00 | 6 / 1.00 | 7 / 1.12 | 8 / 1.15 | pass (h = 1) |
| risk_logistic_base+every_day | 7 / 1.65 | 5 / 1.46 | 7 / 1.62 | 6 / 1.50 | 7 / 2.31 | fail |
| risk_logistic_base+every_day+shrunk | 12 / 2.50 | 5 / 0.96 | 6 / 1.23 | 6 / 0.96 | 7 / 1.35 | fail |
| risk_logistic_base+every_day+scarce | 7 / 1.62 | 5 / 1.42 | 7 / 1.54 | 6 / 1.38 | 7 / 2.23 | fail |
| risk_logistic_base+every_day+persist | 9 / 1.77 | 6 / 1.58 | 7 / 1.23 | 8 / 1.81 | 5 / 1.35 | fail |
| risk_logistic_base+every_day+gate | 8 / 1.77 | 5 / 1.46 | 7 / 1.62 | 6 / 1.50 | 9 / 2.88 | fail |
| risk_quantile_skewt_base | 13 / 1.81 | 9 / 1.62 | 9 / 1.46 | 9 / 1.12 | 9 / 1.04 | pass (h = 1) |
| risk_quantile_skewt_base+every_day | 10 / 1.81 | 3 / 1.35 | 9 / 2.00 | 9 / 2.19 | 10 / 2.46 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 11 / 2.58 | 4 / 1.38 | 9 / 2.62 | 9 / 1.46 | 9 / 1.92 | fail |
| risk_quantile_skewt_base+every_day+scarce | 10 / 1.77 | 3 / 1.31 | 9 / 1.96 | 9 / 2.08 | 10 / 2.38 | fail |
| risk_quantile_skewt_base+every_day+persist | 10 / 2.31 | 4 / 1.27 | 9 / 2.38 | 11 / 2.85 | 8 / 2.00 | fail |
| risk_quantile_skewt_base+every_day+gate | 9 / 2.31 | 3 / 1.35 | 8 / 1.96 | 9 / 2.15 | 12 / 3.15 | fail |
| calendar_climatology | 9 / 4.85 | 10 / 4.88 | 10 / 4.92 | 10 / 4.96 | 10 / 5.00 | fail |
| persistence_logistic | 4 / 2.77 | 6 / 3.42 | 6 / 2.81 | 6 / 3.15 | 5 / 2.81 | fail |

## Weighted rule

### (a) as declared

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.88 | 1.50 | 0.88 | pass |
| risk_gbm+every_day | 16 of 26 | 0.615 [0.429, 0.789] | 2.19 | 5.08 | 2.19 | fail |
| risk_gbm+every_day+shrunk | 16 of 26 | 0.615 [0.438, 0.800] | 2.03 | 4.65 | 2.03 | fail |
| risk_gbm+every_day+scarce | 16 of 26 | 0.615 [0.435, 0.800] | 2.18 | 5.04 | 2.18 | fail |
| risk_gbm+every_day+persist | 15 of 26 | 0.577 [0.387, 0.762] | 2.19 | 5.00 | 2.19 | fail |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.481, 0.818] | 1.67 | 3.92 | 1.67 | pass |
| risk_gbm_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.97 | 1.50 | 0.97 | pass |
| risk_gbm_base+every_day | 17 of 26 | 0.654 [0.478, 0.826] | 2.42 | 5.31 | 2.42 | fail |
| risk_gbm_base+every_day+shrunk | 16 of 26 | 0.615 [0.433, 0.800] | 2.11 | 4.58 | 2.11 | fail |
| risk_gbm_base+every_day+scarce | 17 of 26 | 0.654 [0.474, 0.826] | 2.41 | 5.27 | 2.41 | fail |
| risk_gbm_base+every_day+persist | 16 of 26 | 0.615 [0.428, 0.800] | 2.21 | 4.96 | 2.21 | fail |
| risk_gbm_base+every_day+gate | 17 of 26 | 0.654 [0.481, 0.824] | 1.68 | 3.81 | 1.68 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 1.78 | 2.46 | 1.78 | pass |
| risk_logistic+every_day | 17 of 26 | 0.654 [0.480, 0.826] | 2.28 | 5.35 | 2.28 | fail |
| risk_logistic+every_day+shrunk | 18 of 26 | 0.692 [0.522, 0.852] | 2.42 | 5.23 | 2.42 | fail |
| risk_logistic+every_day+scarce | 17 of 26 | 0.654 [0.476, 0.818] | 2.27 | 5.31 | 2.27 | fail |
| risk_logistic+every_day+persist | 16 of 26 | 0.615 [0.429, 0.790] | 2.42 | 5.31 | 2.42 | fail |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.520, 0.857] | 2.07 | 4.27 | 2.07 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 1.65 | 2.31 | 1.65 | pass |
| risk_logistic_base+every_day | 13 of 26 | 0.500 [0.321, 0.679] | 2.26 | 5.04 | 2.26 | fail |
| risk_logistic_base+every_day+shrunk | 17 of 26 | 0.654 [0.480, 0.821] | 2.34 | 5.12 | 2.34 | fail |
| risk_logistic_base+every_day+scarce | 13 of 26 | 0.500 [0.321, 0.667] | 2.18 | 4.92 | 2.18 | fail |
| risk_logistic_base+every_day+persist | 14 of 26 | 0.538 [0.364, 0.719] | 2.31 | 5.12 | 2.31 | fail |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.815] | 2.03 | 4.12 | 2.03 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 1.61 | 2.27 | 1.61 | pass |
| risk_quantile_skewt_base+every_day | 16 of 26 | 0.615 [0.444, 0.792] | 2.70 | 5.62 | 2.70 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 19 of 26 | 0.731 [0.560, 0.882] | 2.98 | 6.00 | 2.98 | fail |
| risk_quantile_skewt_base+every_day+scarce | 16 of 26 | 0.615 [0.429, 0.781] | 2.71 | 5.62 | 2.71 | fail |
| risk_quantile_skewt_base+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 2.56 | 5.35 | 2.56 | fail |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.467, 0.824] | 2.00 | 4.15 | 2.00 | pass |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 3.75 | 6.69 | 3.75 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 3.25 | 7.04 | 3.25 | fail |

### (b2) warnings and false alarms pooled across horizons

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.333, 0.682] | 1.57 | 2.23 | 1.57 | pass |
| risk_gbm+every_day | 16 of 26 | 0.615 [0.429, 0.792] | 3.79 | 7.88 | 3.79 | fail |
| risk_gbm+every_day+shrunk | 16 of 26 | 0.615 [0.429, 0.792] | 3.63 | 7.46 | 3.63 | fail |
| risk_gbm+every_day+scarce | 16 of 26 | 0.615 [0.429, 0.786] | 3.60 | 7.58 | 3.60 | fail |
| risk_gbm+every_day+persist | 15 of 26 | 0.577 [0.385, 0.767] | 3.04 | 6.38 | 3.04 | fail |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.480, 0.818] | 3.76 | 7.46 | 3.76 | fail |
| risk_gbm_base | 15 of 26 | 0.577 [0.391, 0.760] | 1.60 | 2.23 | 1.60 | pass |
| risk_gbm_base+every_day | 17 of 26 | 0.654 [0.478, 0.821] | 3.96 | 8.08 | 3.96 | fail |
| risk_gbm_base+every_day+shrunk | 16 of 26 | 0.615 [0.423, 0.800] | 3.65 | 7.35 | 3.65 | fail |
| risk_gbm_base+every_day+scarce | 17 of 26 | 0.654 [0.474, 0.828] | 3.77 | 7.77 | 3.77 | fail |
| risk_gbm_base+every_day+persist | 16 of 26 | 0.615 [0.429, 0.800] | 3.40 | 6.88 | 3.40 | fail |
| risk_gbm_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.829] | 3.68 | 7.31 | 3.68 | fail |
| risk_logistic | 16 of 26 | 0.615 [0.440, 0.800] | 2.66 | 3.42 | 2.66 | fail |
| risk_logistic+every_day | 17 of 26 | 0.654 [0.472, 0.818] | 3.71 | 7.88 | 3.71 | fail |
| risk_logistic+every_day+shrunk | 18 of 26 | 0.692 [0.519, 0.857] | 3.77 | 7.65 | 3.77 | fail |
| risk_logistic+every_day+scarce | 17 of 26 | 0.654 [0.480, 0.818] | 3.52 | 7.58 | 3.52 | fail |
| risk_logistic+every_day+persist | 16 of 26 | 0.615 [0.433, 0.800] | 3.59 | 7.42 | 3.59 | fail |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.516, 0.842] | 4.23 | 8.12 | 4.23 | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.759] | 2.18 | 2.88 | 2.18 | fail |
| risk_logistic_base+every_day | 13 of 26 | 0.500 [0.321, 0.679] | 3.33 | 7.15 | 3.33 | fail |
| risk_logistic_base+every_day+shrunk | 17 of 26 | 0.654 [0.481, 0.818] | 3.67 | 7.58 | 3.67 | fail |
| risk_logistic_base+every_day+scarce | 13 of 26 | 0.500 [0.333, 0.667] | 3.13 | 6.85 | 3.13 | fail |
| risk_logistic_base+every_day+persist | 14 of 26 | 0.538 [0.370, 0.710] | 3.12 | 6.85 | 3.12 | fail |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.478, 0.824] | 4.16 | 8.08 | 4.16 | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.400, 0.759] | 2.26 | 3.00 | 2.26 | fail |
| risk_quantile_skewt_base+every_day | 16 of 26 | 0.615 [0.440, 0.778] | 3.92 | 7.96 | 3.92 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 19 of 26 | 0.731 [0.550, 0.880] | 4.55 | 8.73 | 4.55 | fail |
| risk_quantile_skewt_base+every_day+scarce | 16 of 26 | 0.615 [0.444, 0.778] | 3.81 | 7.77 | 3.81 | fail |
| risk_quantile_skewt_base+every_day+persist | 15 of 26 | 0.577 [0.393, 0.750] | 3.97 | 7.85 | 3.97 | fail |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.818] | 4.02 | 7.88 | 4.02 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.278, 0.650] | 3.90 | 6.85 | 3.90 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.276, 0.667] | 4.09 | 8.46 | 4.09 | fail |

### (e) outside 2018-19

| row | onsets warned | recall [90%] | false alarms per onset, as the rule counts them | flat count | weighted count | tier 1 |
|---|---|---|---|---|---|---|
| risk_gbm | 3 of 9 | 0.333 [0.000, 0.636] | 1.53 | 2.00 | 1.53 | fail |
| risk_gbm+every_day | 3 of 9 | 0.333 [0.000, 0.636] | 1.64 | 3.22 | 1.64 | fail |
| risk_gbm+every_day+shrunk | 3 of 9 | 0.333 [–, –] | 1.86 | 3.44 | 1.86 | fail |
| risk_gbm+every_day+scarce | 3 of 9 | 0.333 [0.000, 0.625] | 1.42 | 3.11 | 1.42 | fail |
| risk_gbm+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.33 | 2.33 | 1.33 | fail |
| risk_gbm+every_day+gate | 4 of 9 | 0.444 [0.167, 0.728] | 2.72 | 4.78 | 2.72 | fail |
| risk_gbm_base | 5 of 9 | 0.556 [–, –] | 2.08 | 2.44 | 2.08 | fail |
| risk_gbm_base+every_day | 4 of 9 | 0.444 [–, –] | 2.14 | 3.78 | 2.14 | fail |
| risk_gbm_base+every_day+shrunk | 3 of 9 | 0.333 [–, –] | 2.11 | 3.67 | 2.11 | fail |
| risk_gbm_base+every_day+scarce | 4 of 9 | 0.444 [–, –] | 1.97 | 3.56 | 1.97 | fail |
| risk_gbm_base+every_day+persist | 3 of 9 | 0.333 [–, –] | 1.81 | 3.11 | 1.81 | fail |
| risk_gbm_base+every_day+gate | 4 of 9 | 0.444 [–, –] | 2.67 | 4.44 | 2.67 | fail |
| risk_logistic | 6 of 9 | 0.667 [0.307, 1.000] | 4.50 | 5.00 | 4.50 | fail |
| risk_logistic+every_day | 4 of 9 | 0.444 [–, –] | 1.94 | 3.56 | 1.94 | fail |
| risk_logistic+every_day+shrunk | 5 of 9 | 0.556 [0.250, 0.824] | 2.50 | 4.11 | 2.50 | fail |
| risk_logistic+every_day+scarce | 4 of 9 | 0.444 [0.167, 0.700] | 1.92 | 3.44 | 1.92 | fail |
| risk_logistic+every_day+persist | 3 of 9 | 0.333 [–, –] | 1.47 | 2.44 | 1.47 | fail |
| risk_logistic+every_day+gate | 5 of 9 | 0.556 [–, –] | 3.19 | 4.89 | 3.19 | fail |
| risk_logistic_base | 5 of 9 | 0.556 [–, –] | 3.67 | 4.00 | 3.67 | fail |
| risk_logistic_base+every_day | 3 of 9 | 0.333 [0.091, 0.556] | 2.14 | 3.67 | 2.14 | fail |
| risk_logistic_base+every_day+shrunk | 4 of 9 | 0.444 [0.143, 0.714] | 2.36 | 4.11 | 2.36 | fail |
| risk_logistic_base+every_day+scarce | 3 of 9 | 0.333 [–, –] | 1.92 | 3.33 | 1.92 | fail |
| risk_logistic_base+every_day+persist | 2 of 9 | 0.222 [–, –] | 1.44 | 2.67 | 1.44 | fail |
| risk_logistic_base+every_day+gate | 4 of 9 | 0.444 [–, –] | 3.22 | 5.11 | 3.22 | fail |
| risk_quantile_skewt_base | 5 of 9 | 0.556 [–, –] | 3.92 | 4.44 | 3.92 | fail |
| risk_quantile_skewt_base+every_day | 4 of 9 | 0.444 [0.167, 0.700] | 2.64 | 4.22 | 2.64 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 6 of 9 | 0.667 [0.375, 0.909] | 3.39 | 5.33 | 3.39 | fail |
| risk_quantile_skewt_base+every_day+scarce | 4 of 9 | 0.444 [–, –] | 2.67 | 4.11 | 2.67 | fail |
| risk_quantile_skewt_base+every_day+persist | 3 of 9 | 0.333 [–, –] | 2.50 | 3.44 | 2.50 | fail |
| risk_quantile_skewt_base+every_day+gate | 4 of 9 | 0.444 [0.167, 0.727] | 3.22 | 4.78 | 3.22 | fail |
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
| risk_logistic+every_day+persist | 13 of 17 | 0.765 [0.533, 0.952] | 3.00 | 6.88 | 3.00 | fail |
| risk_logistic+every_day+gate | 13 of 17 | 0.765 [0.552, 0.955] | 1.47 | 3.94 | 1.47 | pass |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.71 | 1.47 | 0.71 | pass |
| risk_logistic_base+every_day | 10 of 17 | 0.588 [0.363, 0.824] | 2.32 | 6.00 | 2.32 | fail |
| risk_logistic_base+every_day+shrunk | 13 of 17 | 0.765 [0.538, 0.947] | 2.40 | 6.06 | 2.40 | fail |
| risk_logistic_base+every_day+scarce | 10 of 17 | 0.588 [0.364, 0.833] | 2.32 | 6.00 | 2.32 | fail |
| risk_logistic_base+every_day+persist | 12 of 17 | 0.706 [0.500, 0.929] | 2.79 | 6.53 | 2.79 | fail |
| risk_logistic_base+every_day+gate | 13 of 17 | 0.765 [0.550, 0.952] | 1.47 | 3.94 | 1.47 | pass |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.375, 0.800] | 0.44 | 1.12 | 0.44 | pass |
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
| risk_gbm | 13 / 0.88 | 8 / 0.68 | 7 / 0.62 | 7 / 0.47 | 7 / 0.72 | pass (h = 1) |
| risk_gbm+every_day | 15 / 2.19 | 11 / 2.03 | 11 / 2.02 | 10 / 1.70 | 10 / 1.90 | fail |
| risk_gbm+every_day+shrunk | 15 / 1.93 | 10 / 1.71 | 11 / 1.99 | 10 / 1.90 | 9 / 2.03 | pass (h = 1) |
| risk_gbm+every_day+scarce | 15 / 2.18 | 11 / 2.00 | 11 / 1.94 | 10 / 1.62 | 10 / 1.83 | fail |
| risk_gbm+every_day+persist | 15 / 1.62 | 11 / 1.83 | 11 / 2.19 | 11 / 1.65 | 8 / 1.62 | pass (h = 1) |
| risk_gbm+every_day+gate | 13 / 1.67 | 8 / 1.63 | 8 / 1.54 | 9 / 1.48 | 10 / 1.61 | pass (h = 1) |
| risk_gbm_base | 13 / 0.97 | 8 / 0.64 | 9 / 0.92 | 7 / 0.66 | 7 / 0.76 | pass (h = 1) |
| risk_gbm_base+every_day | 16 / 2.42 | 10 / 2.07 | 11 / 2.05 | 10 / 1.91 | 10 / 2.09 | fail |
| risk_gbm_base+every_day+shrunk | 15 / 2.11 | 9 / 1.67 | 11 / 2.00 | 10 / 2.06 | 9 / 2.05 | fail |
| risk_gbm_base+every_day+scarce | 16 / 2.41 | 10 / 2.04 | 11 / 1.97 | 10 / 1.83 | 10 / 2.01 | fail |
| risk_gbm_base+every_day+persist | 16 / 2.21 | 10 / 1.88 | 11 / 2.21 | 11 / 1.84 | 8 / 1.81 | fail |
| risk_gbm_base+every_day+gate | 13 / 1.68 | 8 / 1.56 | 8 / 1.60 | 9 / 1.61 | 10 / 1.62 | pass (h = 1) |
| risk_logistic | 15 / 1.78 | 7 / 1.36 | 8 / 1.38 | 10 / 1.75 | 9 / 1.62 | pass (h = 1) |
| risk_logistic+every_day | 15 / 2.28 | 11 / 2.02 | 11 / 2.02 | 9 / 1.84 | 12 / 2.16 | fail |
| risk_logistic+every_day+shrunk | 15 / 2.16 | 12 / 2.24 | 10 / 1.88 | 11 / 2.04 | 13 / 2.42 | fail |
| risk_logistic+every_day+scarce | 15 / 2.27 | 11 / 1.99 | 11 / 1.94 | 9 / 1.75 | 12 / 2.09 | fail |
| risk_logistic+every_day+persist | 15 / 2.15 | 11 / 1.83 | 11 / 1.82 | 9 / 2.07 | 11 / 2.42 | fail |
| risk_logistic+every_day+gate | 12 / 1.83 | 8 / 1.60 | 8 / 1.58 | 8 / 1.81 | 12 / 2.07 | fail |
| risk_logistic_base | 14 / 1.65 | 8 / 1.22 | 7 / 1.16 | 7 / 1.01 | 8 / 1.47 | pass (h = 1) |
| risk_logistic_base+every_day | 11 / 1.97 | 11 / 2.01 | 12 / 1.96 | 10 / 1.92 | 12 / 2.26 | fail |
| risk_logistic_base+every_day+shrunk | 16 / 2.31 | 12 / 2.12 | 12 / 1.99 | 10 / 2.09 | 12 / 2.34 | fail |
| risk_logistic_base+every_day+scarce | 11 / 1.96 | 11 / 1.98 | 12 / 1.88 | 10 / 1.84 | 12 / 2.18 | fail |
| risk_logistic_base+every_day+persist | 13 / 1.89 | 11 / 1.82 | 12 / 1.75 | 11 / 2.18 | 12 / 2.31 | pass (h = 1) |
| risk_logistic_base+every_day+gate | 13 / 2.03 | 9 / 1.56 | 9 / 1.63 | 9 / 1.71 | 13 / 1.91 | pass (h = 5) |
| risk_quantile_skewt_base | 15 / 1.61 | 9 / 1.56 | 9 / 0.96 | 9 / 0.56 | 9 / 0.51 | pass (h = 1) |
| risk_quantile_skewt_base+every_day | 14 / 2.19 | 11 / 1.59 | 13 / 2.70 | 12 / 2.05 | 13 / 2.37 | fail |
| risk_quantile_skewt_base+every_day+shrunk | 18 / 2.64 | 12 / 2.34 | 14 / 2.98 | 13 / 2.24 | 14 / 2.59 | fail |
| risk_quantile_skewt_base+every_day+scarce | 14 / 2.18 | 11 / 1.56 | 13 / 2.71 | 12 / 1.97 | 13 / 2.31 | fail |
| risk_quantile_skewt_base+every_day+persist | 14 / 2.19 | 11 / 1.83 | 13 / 2.56 | 12 / 2.25 | 12 / 2.46 | fail |
| risk_quantile_skewt_base+every_day+gate | 13 / 1.82 | 9 / 1.68 | 10 / 1.76 | 10 / 1.84 | 12 / 2.00 | pass (h = 1) |
| calendar_climatology | 12 / 3.75 | 10 / 3.17 | 10 / 3.21 | 10 / 3.25 | 10 / 3.29 | fail |
| persistence_logistic | 11 / 3.25 | 7 / 2.07 | 10 / 2.68 | 8 / 2.38 | 8 / 1.86 | fail |

