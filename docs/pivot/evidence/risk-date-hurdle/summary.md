| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no | no / no |
| risk_gbm+hurdle_platt | 15/26 / 15/26 | 0.577 [0.385, 0.760] | 0.577 [0.385, 0.760] | 3.08 | 2.23 | no / no / yes | no / no / yes | no / no |
| risk_gbm+hurdle_isotonic | 15/26 / 16/26 | 0.577 [0.389, 0.783] | 0.615 [0.437, 0.808] | 2.62 | 2.13 | no / no / yes | no / no / yes | no / no |
| risk_gbm+hurdle_state_platt | 15/26 / 15/26 | 0.577 [0.375, 0.760] | 0.577 [0.375, 0.760] | 3.54 | 2.14 | no / no / yes | no / no / yes | no / no |
| risk_gbm+hurdle_state_isotonic | 15/26 / 16/26 | 0.577 [0.385, 0.774] | 0.615 [0.424, 0.800] | 2.46 | 2.11 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base | 14/26 / 14/26 | 0.538 [0.360, 0.719] | 0.538 [0.360, 0.719] | 1.50 | 0.97 | yes / no / no | yes / no / no | no / no |
| risk_gbm_base+hurdle_platt | 15/26 / 15/26 | 0.577 [0.375, 0.769] | 0.577 [0.375, 0.769] | 3.04 | 2.15 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+hurdle_isotonic | 15/26 / 15/26 | 0.577 [0.385, 0.767] | 0.577 [0.385, 0.767] | 2.54 | 2.18 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+hurdle_state_platt | 15/26 / 15/26 | 0.577 [0.387, 0.769] | 0.577 [0.387, 0.769] | 3.58 | 2.12 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+hurdle_state_isotonic | 13/26 / 15/26 | 0.500 [0.304, 0.700] | 0.577 [0.385, 0.778] | 2.69 | 2.10 | no / no / yes | no / no / yes | no / no |
| risk_logistic | 14/26 / 16/26 | 0.538 [0.350, 0.724] | 0.615 [0.435, 0.800] | 1.85 | 1.74 | yes / no / no | yes / no / no | no / no |
| risk_logistic+hurdle_platt | 13/26 / 15/26 | 0.500 [0.333, 0.667] | 0.577 [0.391, 0.762] | 3.19 | 2.39 | no / no / yes | no / no / yes | no / no |
| risk_logistic+hurdle_isotonic | 13/26 / 15/26 | 0.500 [0.333, 0.667] | 0.577 [0.400, 0.760] | 2.35 | 2.14 | no / no / yes | no / no / yes | no / no |
| risk_logistic+hurdle_state_platt | 14/26 / 15/26 | 0.538 [0.357, 0.714] | 0.577 [0.385, 0.762] | 3.77 | 2.92 | no / no / yes | no / no / yes | no / no |
| risk_logistic+hurdle_state_isotonic | 12/26 / 15/26 | 0.462 [0.290, 0.640] | 0.577 [0.400, 0.750] | 2.88 | 2.62 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base | 13/26 / 15/26 | 0.500 [0.333, 0.680] | 0.577 [0.391, 0.762] | 1.77 | 1.65 | yes / no / no | yes / no / no | no / no |
| risk_logistic_base+hurdle_platt | 11/26 / 12/26 | 0.423 [0.250, 0.600] | 0.462 [0.281, 0.650] | 2.85 | 2.13 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+hurdle_isotonic | 8/26 / 12/26 | 0.308 [0.158, 0.471] | 0.462 [0.286, 0.636] | 2.00 | 2.12 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+hurdle_state_platt | 13/26 / 14/26 | 0.500 [0.320, 0.690] | 0.538 [0.364, 0.719] | 2.96 | 2.61 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+hurdle_state_isotonic | 11/26 / 14/26 | 0.423 [0.250, 0.611] | 0.538 [0.370, 0.720] | 2.46 | 2.45 | no / no / yes | no / no / yes | no / no |
| risk_quantile_skewt_base | 14/26 / 15/26 | 0.538 [0.360, 0.714] | 0.577 [0.391, 0.750] | 1.88 | 1.62 | yes / no / no | yes / no / no | no / no |
| risk_quantile_skewt_base+hurdle_platt | 13/26 / 14/26 | 0.500 [0.321, 0.682] | 0.538 [0.364, 0.715] | 3.15 | 2.48 | no / no / no | no / no / no | no / no |
| risk_quantile_skewt_base+hurdle_isotonic | 12/26 / 13/26 | 0.462 [0.286, 0.667] | 0.500 [0.333, 0.688] | 2.92 | 2.36 | no / no / yes | no / no / yes | no / no |
| risk_quantile_skewt_base+hurdle_state_platt | 13/26 / 14/26 | 0.500 [0.333, 0.688] | 0.538 [0.367, 0.720] | 3.50 | 2.57 | no / no / yes | no / no / yes | no / no |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12/26 / 13/26 | 0.462 [0.276, 0.643] | 0.500 [0.321, 0.677] | 2.88 | 2.61 | no / no / yes | no / no / yes | no / no |
