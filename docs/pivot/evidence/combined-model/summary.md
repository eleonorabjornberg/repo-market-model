| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |
|---|---|---|---|---|---|---|---|---|
| risk_gbm+combined | 10/26 / 10/26 | 0.385 [0.212, 0.571] | 0.385 [0.212, 0.571] | 1.12 | 1.06 | no / no / no | no / no / no | no / no |
| risk_gbm+combined_nogate | 12/26 / 13/26 | 0.462 [0.276, 0.650] | 0.500 [0.308, 0.684] | 1.92 | 1.84 | no / no / yes | no / no / yes | no / no |
| risk_logistic+combined | 10/26 / 11/26 | 0.385 [0.227, 0.565] | 0.423 [0.258, 0.606] | 1.62 | 1.67 | no / no / no | no / no / no | no / no |
| risk_logistic+combined_nogate | 10/26 / 13/26 | 0.385 [0.238, 0.533] | 0.500 [0.333, 0.667] | 1.58 | 1.93 | no / no / no | no / no / no | no / no |
| risk_gbm+combined_no_factor | 10/26 / 10/26 | 0.385 [0.212, 0.571] | 0.385 [0.212, 0.571] | 1.12 | 1.01 | no / no / no | no / no / no | no / no |
| risk_gbm+combined_no_structural | 10/26 / 10/26 | 0.385 [0.217, 0.562] | 0.385 [0.217, 0.562] | 0.88 | 0.94 | no / no / no | no / no / no | no / no |
| risk_gbm+combined_no_projected | 11/26 / 11/26 | 0.423 [0.235, 0.618] | 0.423 [0.235, 0.618] | 1.31 | 1.06 | no / no / no | no / no / no | no / no |
| risk_gbm+settle+h41 | 14/26 / 14/26 | 0.538 [0.353, 0.710] | 0.538 [0.353, 0.710] | 1.35 | 0.88 | yes / no / no | yes / no / no | no / no |
| risk_logistic+settle+h41 | 15/26 / 16/26 | 0.577 [0.391, 0.760] | 0.615 [0.429, 0.800] | 1.81 | 2.12 | no / no / no | no / no / no | no / no |
| risk_gbm+every_day+gate+settle+h41 | 15/26 / 18/26 | 0.577 [0.417, 0.741] | 0.692 [0.524, 0.857] | 2.35 | 1.64 | no / no / no | no / no / no | no / no |
| risk_logistic+every_day+gate+settle+h41 | 14/26 / 18/26 | 0.538 [0.351, 0.708] | 0.692 [0.519, 0.857] | 2.69 | 2.05 | no / no / yes | no / no / yes | no / no |
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no | no / no |
| ngboost_laplace | 15/26 / 17/26 | 0.577 [0.400, 0.759] | 0.654 [0.467, 0.826] | 2.54 | 1.73 | no / no / no | no / no / no | no / no |
| calendar_climatology | 10/26 / 12/26 | 0.385 [0.208, 0.588] | 0.462 [0.286, 0.667] | 5.00 | 3.75 | no / no / no | no / no / no | no / no |
| persistence_logistic | 7/26 / 12/26 | 0.269 [0.111, 0.444] | 0.462 [0.273, 0.650] | 3.42 | 3.25 | no / no / no | no / no / no | no / no |
