| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 -> 1.38 | 0.80 -> 0.88 | yes / no / no | yes / no / no | no / no |
| risk_gbm+every_day | 15/26 / 17/26 -> 15/26 / 16/26 | 0.577 [0.385, 0.760] | 0.654 [0.474, 0.812] -> 0.615 [0.429, 0.789] | 2.96 -> 3.00 | 2.18 -> 2.19 | no / no / yes | no / no / yes | no / no |
| risk_gbm+every_day+gate | 16/26 / 17/26 -> 15/26 / 17/26 | 0.615 [0.444, 0.778] -> 0.577 [0.400, 0.750] | 0.654 [0.481, 0.818] | 2.96 -> 2.92 | 1.63 -> 1.67 | no / no / no | yes / no / no | no / no |
| risk_gbm_base | 14/26 / 14/26 -> 14/26 / 15/26 | 0.538 [0.360, 0.719] | 0.538 [0.360, 0.719] -> 0.577 [0.391, 0.762] | 1.50 | 0.97 | yes / no / no | yes / no / no | no / no |
| risk_gbm_base+every_day | 15/26 / 18/26 -> 15/26 / 17/26 | 0.577 [0.389, 0.769] | 0.692 [0.520, 0.850] -> 0.654 [0.478, 0.826] | 2.92 -> 2.96 | 2.28 -> 2.42 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+every_day+gate | 15/26 / 18/26 -> 15/26 / 17/26 | 0.577 [0.400, 0.750] -> 0.577 [0.393, 0.750] | 0.692 [0.517, 0.850] -> 0.654 [0.481, 0.824] | 2.88 | 1.62 -> 1.68 | no / no / no | yes / no / no | no / no |
| risk_logistic | 14/26 / 16/26 | 0.538 [0.350, 0.724] | 0.615 [0.435, 0.800] | 1.85 | 1.74 -> 1.78 | yes / no / no | yes / no / no | no / no |
| risk_logistic+every_day | 13/26 / 17/26 -> 14/26 / 17/26 | 0.500 [0.333, 0.667] -> 0.538 [0.375, 0.707] | 0.654 [0.480, 0.826] | 2.69 -> 2.62 | 2.28 | no / no / yes | no / no / yes | no / no |
| risk_logistic+every_day+gate | 14/26 / 18/26 -> 15/26 / 18/26 | 0.538 [0.370, 0.720] -> 0.577 [0.414, 0.742] | 0.692 [0.520, 0.857] | 3.00 -> 2.96 | 2.19 -> 2.07 | no / no / no | no / no / no | no / no |
| risk_logistic_base | 13/26 / 15/26 | 0.500 [0.333, 0.680] | 0.577 [0.391, 0.762] | 1.77 -> 1.81 | 1.65 | yes / no / no | yes / no / no | no / no |
| risk_logistic_base+every_day | 11/26 / 13/26 | 0.423 [0.259, 0.593] | 0.500 [0.321, 0.679] | 2.31 | 2.26 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+every_day+gate | 14/26 / 17/26 | 0.538 [0.368, 0.714] | 0.654 [0.476, 0.815] | 2.88 | 2.01 -> 2.03 | no / no / no | no / no / no | no / no |
| risk_quantile_skewt_base | 14/26 / 15/26 | 0.538 [0.360, 0.714] | 0.577 [0.391, 0.750] | 1.88 -> 1.81 | 1.62 -> 1.61 | yes / no / no | yes / no / no | no / no |
| risk_quantile_skewt_base+every_day | 15/26 / 16/26 | 0.577 [0.409, 0.750] | 0.615 [0.444, 0.792] | 2.46 | 2.63 -> 2.70 | no / no / yes | no / no / yes | no / no |
| risk_quantile_skewt_base+every_day+gate | 15/26 / 17/26 | 0.577 [0.407, 0.741] | 0.654 [0.467, 0.824] | 3.15 | 2.00 | no / no / yes | yes / no / yes | no / no |
