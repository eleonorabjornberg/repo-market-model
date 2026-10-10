| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted |
|---|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no |
| risk_gbm+early_prior | 13/26 / 13/26 | 0.500 [0.320, 0.677] | 0.500 [0.320, 0.677] | 1.35 | 1.17 | yes / no / no | yes / no / no |
| risk_gbm+every_day | 15/26 / 17/26 | 0.577 [0.385, 0.760] | 0.654 [0.474, 0.812] | 2.96 | 2.18 | no / no / yes | no / no / yes |
| risk_gbm+every_day+early_prior | 15/26 / 17/26 | 0.577 [0.375, 0.767] | 0.654 [0.478, 0.824] | 3.08 | 2.20 | no / no / yes | no / no / yes |
| risk_gbm_base | 14/26 / 14/26 | 0.538 [0.360, 0.719] | 0.538 [0.360, 0.719] | 1.50 | 0.97 | yes / no / no | yes / no / no |
| risk_gbm_base+early_prior | 14/26 / 14/26 | 0.538 [0.348, 0.727] | 0.538 [0.348, 0.727] | 1.62 | 1.19 | yes / no / no | yes / no / no |
| risk_gbm_base+every_day | 15/26 / 18/26 | 0.577 [0.389, 0.769] | 0.692 [0.520, 0.850] | 2.92 | 2.28 | no / no / yes | no / no / yes |
| risk_gbm_base+every_day+early_prior | 15/26 / 17/26 | 0.577 [0.364, 0.762] | 0.654 [0.464, 0.821] | 3.19 | 2.34 | no / no / yes | no / no / yes |
| risk_logistic | 14/26 / 16/26 | 0.538 [0.350, 0.724] | 0.615 [0.435, 0.800] | 1.85 | 1.74 | yes / no / no | yes / no / no |
| risk_logistic+early_prior | 14/26 / 16/26 | 0.538 [0.364, 0.714] | 0.615 [0.444, 0.792] | 1.54 | 1.38 | yes / no / no | yes / no / no |
| risk_logistic+every_day | 13/26 / 17/26 | 0.500 [0.333, 0.667] | 0.654 [0.480, 0.826] | 2.69 | 2.28 | no / no / yes | no / no / yes |
| risk_logistic+every_day+early_prior | 15/26 / 17/26 | 0.577 [0.400, 0.750] | 0.654 [0.476, 0.815] | 3.15 | 2.38 | no / no / yes | no / no / yes |
| risk_logistic_base | 13/26 / 15/26 | 0.500 [0.333, 0.680] | 0.577 [0.391, 0.762] | 1.77 | 1.65 | yes / no / no | yes / no / no |
| risk_logistic_base+early_prior | 13/26 / 14/26 | 0.500 [0.333, 0.680] | 0.538 [0.364, 0.714] | 1.46 | 1.37 | yes / no / no | yes / no / no |
| risk_logistic_base+every_day | 11/26 / 13/26 | 0.423 [0.259, 0.593] | 0.500 [0.321, 0.679] | 2.31 | 2.26 | no / no / yes | no / no / yes |
| risk_logistic_base+every_day+early_prior | 14/26 / 16/26 | 0.538 [0.360, 0.706] | 0.615 [0.429, 0.778] | 3.15 | 2.36 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base | 14/26 / 15/26 | 0.538 [0.360, 0.714] | 0.577 [0.391, 0.750] | 1.88 | 1.62 | yes / no / no | yes / no / no |
| risk_quantile_skewt_base+early_prior | 14/26 / 15/26 | 0.538 [0.364, 0.714] | 0.577 [0.400, 0.750] | 1.81 | 1.52 | yes / no / no | yes / no / no |
| risk_quantile_skewt_base+every_day | 15/26 / 16/26 | 0.577 [0.409, 0.750] | 0.615 [0.444, 0.792] | 2.46 | 2.63 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base+every_day+early_prior | 13/26 / 17/26 | 0.500 [0.316, 0.677] | 0.654 [0.469, 0.821] | 3.19 | 2.59 | no / no / yes | no / no / yes |

passes: []
