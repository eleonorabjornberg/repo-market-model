Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+every_day | 17 of 26 | 0.654 [0.474, 0.812] | 0.411 | 7.88 flat / 3.79 weighted (tier 1 on the weighted count) | 1.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.481, 0.818] | 0.385 | 7.35 flat / 3.67 weighted (tier 1 on the weighted count) | 3.6 / 1.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.524, 0.857] | 0.375 | 6.96 flat / 3.39 weighted (tier 1 on the weighted count) | 2.9 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 19 of 26 | 0.731 [0.560, 0.889] | 0.382 | 7.08 flat / 3.46 weighted (tier 1 on the weighted count) | 3.4 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+persist | 16 of 26 | 0.615 [0.435, 0.800] | 0.306 | 6.42 flat / 3.08 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+scarce | 17 of 26 | 0.654 [0.483, 0.818] | 0.385 | 7.38 flat / 3.49 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+shrunk | 16 of 26 | 0.615 [0.438, 0.800] | 0.385 | 7.46 flat / 3.66 weighted (tier 1 on the weighted count) | 1.7 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic | 16 of 26 | 0.615 [0.437, 0.808] | 0.278 | 5.92 flat / 2.77 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.375, 0.778] | 0.282 | 6.00 flat / 2.83 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+settle | 16 of 26 | 0.615 [0.433, 0.792] | 0.286 | 6.08 flat / 2.94 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_isotonic+settle+h41 | 16 of 26 | 0.615 [0.435, 0.800] | 0.269 | 5.73 flat / 2.74 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.760] | 0.306 | 6.42 flat / 3.10 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+h41 | 16 of 26 | 0.615 [0.424, 0.794] | 0.385 | 7.27 flat / 3.88 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+settle | 16 of 26 | 0.615 [0.429, 0.790] | 0.293 | 6.19 flat / 3.00 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_platt+settle+h41 | 16 of 26 | 0.615 [0.423, 0.793] | 0.295 | 6.23 flat / 3.08 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic | 14 of 26 | 0.538 [0.355, 0.735] | 0.297 | 6.27 flat / 3.15 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.304, 0.692] | 0.274 | 5.85 flat / 2.93 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+settle | 14 of 26 | 0.538 [0.351, 0.739] | 0.286 | 6.08 flat / 3.05 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 14 of 26 | 0.538 [0.355, 0.727] | 0.269 | 5.62 flat / 2.80 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_platt | 14 of 26 | 0.538 [0.350, 0.739] | 0.297 | 6.27 flat / 3.34 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.346, 0.727] | 0.306 | 6.42 flat / 3.54 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+settle | 14 of 26 | 0.538 [0.348, 0.731] | 0.282 | 6.00 flat / 3.17 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+settle+h41 | 14 of 26 | 0.538 [0.348, 0.727] | 0.291 | 6.15 flat / 3.43 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.19 flat / 1.48 weighted (tier 1 on the weighted count) | 1.0 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base+every_day | 18 of 26 | 0.692 [0.520, 0.850] | 0.411 | 7.88 flat / 3.77 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+gate | 18 of 26 | 0.692 [0.517, 0.850] | 0.385 | 7.27 flat / 3.64 weighted (tier 1 on the weighted count) | 2.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+persist | 17 of 26 | 0.654 [0.464, 0.833] | 0.358 | 6.69 flat / 3.24 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+scarce | 18 of 26 | 0.692 [0.522, 0.857] | 0.385 | 7.38 flat / 3.47 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+shrunk | 17 of 26 | 0.654 [0.471, 0.833] | 0.385 | 7.35 flat / 3.63 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic | 16 of 26 | 0.615 [0.437, 0.792] | 0.351 | 6.58 flat / 3.13 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.368, 0.778] | 0.276 | 5.88 flat / 2.76 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+settle | 15 of 26 | 0.577 [0.368, 0.767] | 0.291 | 6.15 flat / 3.01 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 15 of 26 | 0.577 [0.370, 0.769] | 0.269 | 5.54 flat / 2.65 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt | 17 of 26 | 0.654 [0.458, 0.826] | 0.368 | 6.85 flat / 3.36 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+h41 | 15 of 26 | 0.577 [0.375, 0.774] | 0.349 | 6.54 flat / 3.15 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+settle | 17 of 26 | 0.654 [0.471, 0.826] | 0.297 | 6.27 flat / 3.01 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt+settle+h41 | 15 of 26 | 0.577 [0.381, 0.767] | 0.293 | 6.19 flat / 3.08 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic | 14 of 26 | 0.538 [0.350, 0.731] | 0.306 | 6.42 flat / 3.19 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.300, 0.700] | 0.276 | 5.88 flat / 2.80 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+settle | 13 of 26 | 0.500 [0.305, 0.700] | 0.297 | 6.27 flat / 3.12 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 13 of 26 | 0.500 [0.304, 0.708] | 0.269 | 5.65 flat / 2.75 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.375, 0.769] | 0.346 | 6.50 flat / 3.51 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.333, 0.739] | 0.299 | 6.31 flat / 3.45 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.385, 0.774] | 0.288 | 6.12 flat / 3.21 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 14 of 26 | 0.538 [0.345, 0.742] | 0.282 | 6.00 flat / 3.32 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.23 flat / 2.47 weighted (tier 1 on the weighted count) | 2.7 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic+every_day | 14 of 26 | 0.538 [0.364, 0.718] | 0.385 | 7.23 flat / 3.40 weighted (tier 1 on the weighted count) | 1.9 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+gate | 17 of 26 | 0.654 [0.478, 0.818] | 0.418 | 8.00 flat / 4.06 weighted (tier 1 on the weighted count) | 2.9 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+every_day+persist | 15 of 26 | 0.577 [0.419, 0.741] | 0.373 | 6.92 flat / 3.23 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+scarce | 14 of 26 | 0.538 [0.364, 0.714] | 0.361 | 6.73 flat / 3.11 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+shrunk | 18 of 26 | 0.692 [0.522, 0.852] | 0.397 | 7.65 flat / 3.69 weighted (tier 1 on the weighted count) | 2.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+hurdle_isotonic | 12 of 26 | 0.462 [0.281, 0.636] | 0.271 | 5.81 flat / 2.80 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.391, 0.750] | 0.286 | 6.08 flat / 2.89 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle | 14 of 26 | 0.538 [0.368, 0.714] | 0.269 | 4.92 flat / 2.30 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle+h41 | 15 of 26 | 0.577 [0.387, 0.762] | 0.269 | 5.54 flat / 2.54 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_platt | 12 of 26 | 0.462 [0.282, 0.650] | 0.269 | 5.69 flat / 2.68 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.373 | 6.92 flat / 3.42 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+settle | 14 of 26 | 0.538 [0.367, 0.715] | 0.276 | 5.88 flat / 2.78 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_logistic+hurdle_platt+settle+h41 | 15 of 26 | 0.577 [0.393, 0.750] | 0.346 | 6.50 flat / 3.02 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic | 12 of 26 | 0.462 [0.286, 0.650] | 0.284 | 6.04 flat / 3.00 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+h41 | 15 of 26 | 0.577 [0.400, 0.760] | 0.274 | 5.85 flat / 2.79 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle | 14 of 26 | 0.538 [0.364, 0.714] | 0.269 | 5.69 flat / 2.61 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 15 of 26 | 0.577 [0.391, 0.750] | 0.269 | 5.58 flat / 2.70 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt | 12 of 26 | 0.462 [0.285, 0.647] | 0.301 | 6.35 flat / 3.38 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+h41 | 15 of 26 | 0.577 [0.391, 0.750] | 0.373 | 6.92 flat / 3.84 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+settle | 14 of 26 | 0.538 [0.350, 0.714] | 0.276 | 5.88 flat / 2.92 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt+settle+h41 | 14 of 26 | 0.538 [0.360, 0.719] | 0.297 | 6.27 flat / 3.44 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.231 | 2.81 flat / 2.08 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base+every_day | 14 of 26 | 0.538 [0.360, 0.722] | 0.385 | 7.12 flat / 3.29 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.815] | 0.404 | 7.77 flat / 3.86 weighted (tier 1 on the weighted count) | 2.9 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+every_day+persist | 14 of 26 | 0.538 [0.364, 0.719] | 0.365 | 6.81 flat / 3.08 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+scarce | 14 of 26 | 0.538 [0.360, 0.719] | 0.353 | 6.62 flat / 2.99 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+shrunk | 17 of 26 | 0.654 [0.480, 0.821] | 0.385 | 7.35 flat / 3.48 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.636] | 0.269 | 5.38 flat / 2.53 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+h41 | 14 of 26 | 0.538 [0.368, 0.720] | 0.269 | 5.50 flat / 2.56 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle | 15 of 26 | 0.577 [0.407, 0.739] | 0.269 | 4.73 flat / 2.38 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.370, 0.714] | 0.269 | 4.73 flat / 2.35 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt | 12 of 26 | 0.462 [0.281, 0.650] | 0.276 | 5.88 flat / 2.77 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.280 | 5.96 flat / 2.79 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+settle | 14 of 26 | 0.538 [0.375, 0.710] | 0.269 | 5.19 flat / 2.57 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt+settle+h41 | 14 of 26 | 0.538 [0.360, 0.722] | 0.269 | 5.04 flat / 2.38 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic | 12 of 26 | 0.462 [0.281, 0.650] | 0.269 | 5.54 flat / 2.60 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 14 of 26 | 0.538 [0.368, 0.714] | 0.269 | 5.73 flat / 2.64 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle | 14 of 26 | 0.538 [0.370, 0.714] | 0.269 | 4.85 flat / 2.38 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 14 of 26 | 0.538 [0.364, 0.722] | 0.269 | 4.73 flat / 2.27 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt | 12 of 26 | 0.462 [0.286, 0.640] | 0.269 | 5.65 flat / 2.85 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.364, 0.714] | 0.293 | 6.19 flat / 3.33 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+settle | 14 of 26 | 0.538 [0.360, 0.711] | 0.269 | 4.81 flat / 2.51 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 14 of 26 | 0.538 [0.364, 0.714] | 0.269 | 5.15 flat / 2.82 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt | 16 of 26 | 0.615 [0.450, 0.773] | 0.269 | 5.00 flat / 4.26 weighted (tier 1 on the weighted count) | 7.5 / 10.8 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 2.81 flat / 2.11 weighted (tier 1 on the weighted count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base+every_day | 16 of 26 | 0.615 [0.444, 0.792] | 0.418 | 8.00 flat / 3.90 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.467, 0.824] | 0.421 | 8.04 flat / 4.21 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 0.394 | 7.62 flat / 3.94 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+scarce | 16 of 26 | 0.615 [0.429, 0.781] | 0.387 | 7.50 flat / 3.61 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+shrunk | 17 of 26 | 0.654 [0.499, 0.815] | 0.423 | 8.12 flat / 4.21 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+hurdle_isotonic | 13 of 26 | 0.500 [0.333, 0.688] | 0.293 | 6.19 flat / 3.03 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 13 of 26 | 0.500 [0.320, 0.680] | 0.291 | 6.15 flat / 2.99 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 16 of 26 | 0.615 [0.429, 0.800] | 0.269 | 5.73 flat / 2.74 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 16 of 26 | 0.615 [0.429, 0.789] | 0.269 | 5.31 flat / 2.54 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt | 14 of 26 | 0.538 [0.364, 0.715] | 0.356 | 6.65 flat / 3.24 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 14 of 26 | 0.538 [0.367, 0.714] | 0.303 | 6.38 flat / 3.08 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle | 16 of 26 | 0.615 [0.435, 0.800] | 0.269 | 5.62 flat / 2.66 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 16 of 26 | 0.615 [0.435, 0.793] | 0.269 | 5.65 flat / 2.77 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.321, 0.677] | 0.308 | 6.46 flat / 3.10 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 14 of 26 | 0.538 [0.350, 0.704] | 0.297 | 6.27 flat / 2.98 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 16 of 26 | 0.615 [0.417, 0.792] | 0.269 | 5.62 flat / 2.62 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 16 of 26 | 0.615 [0.435, 0.800] | 0.269 | 5.73 flat / 2.67 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt | 14 of 26 | 0.538 [0.367, 0.720] | 0.301 | 6.35 flat / 3.29 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.360, 0.714] | 0.363 | 6.77 flat / 3.79 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 16 of 26 | 0.615 [0.417, 0.792] | 0.269 | 5.50 flat / 2.83 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 16 of 26 | 0.615 [0.429, 0.792] | 0.280 | 5.96 flat / 3.27 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

Table 1b. Tier 1 at each lead alone, inside and outside the early years, and the recall with equal weight per regime: reported for every model, not part of the pass rule.

calendar_climatology:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.667] | 6.692 [4.583, 10.002] | 3.750 [2.485, 5.938] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.538 [3.440, 8.668] | 3.173 [1.975, 5.211] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.577 [3.464, 8.734] | 3.212 [1.990, 5.282] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.615 [3.500, 8.739] | 3.250 [2.012, 5.360] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.654 [3.516, 8.811] | 3.288 [2.033, 5.400] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.765 [5.086, 12.286] | 3.324 [2.034, 5.576] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 5.111 (no interval) | 5.000 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

ngboost_laplace:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.760] | 3.308 [1.966, 5.211] | 1.413 [0.780, 2.348] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 3.462 [2.053, 5.334] | 1.423 [0.784, 2.283] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.189, 0.515] | 3.269 [1.914, 5.167] | 1.288 [0.694, 2.090] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 3.577 [2.095, 5.591] | 1.596 [0.833, 2.630] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.546] | 4.077 [2.484, 6.222] | 1.731 [0.970, 2.782] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.647 [5.161, 11.572] | 3.265 [2.039, 5.319] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 0.889 (no interval) | 0.583 (no interval) |

Recall with equal weight per regime: 0.426 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

persistence_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.233, 0.609] | 7.038 [4.823, 10.000] | 3.250 [2.032, 4.952] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 4.769 [2.961, 7.201] | 2.067 [1.193, 3.329] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.567] | 5.923 [3.750, 8.714] | 2.683 [1.527, 4.207] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.136, 0.500] | 5.385 [3.275, 8.160] | 2.375 [1.310, 3.931] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.481] | 4.538 [2.761, 7.000] | 1.856 [1.083, 2.962] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.880] | 8.471 [5.500, 13.182] | 3.706 [2.208, 6.083] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 8.444 (no interval) | 4.806 (no interval) |

Recall with equal weight per regime: 0.287 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 0/5).

risk_gbm:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.310, 0.667] | 1.385 [0.914, 2.053] | 0.798 [0.500, 1.286] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.455] | 1.154 [0.667, 1.909] | 0.683 [0.327, 1.292] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.038 [0.606, 1.714] | 0.587 [0.282, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 0.923 [0.543, 1.500] | 0.471 [0.232, 0.888] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.231 [0.731, 2.002] | 0.760 [0.379, 1.398] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.800] | 1.353 [0.800, 2.250] | 0.618 [0.321, 1.167] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.556 [1.800, 8.200] | 3.111 [1.477, 7.568] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.433, 0.789] | 5.077 [3.407, 7.410] | 2.173 [1.370, 3.322] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 5.000 [3.235, 7.369] | 2.067 [1.264, 3.197] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.769 [2.960, 7.251] | 2.058 [1.195, 3.298] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.115 [2.519, 6.334] | 1.702 [0.950, 2.763] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.565] | 4.231 [2.586, 6.471] | 1.942 [1.136, 3.100] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.826, 11.455] | 3.147 [1.920, 5.200] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 8.778 [5.769, 16.603] | 5.000 [3.050, 10.314] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 3.577 [2.567, 5.000] | 1.625 [1.119, 2.375] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.923 [2.615, 5.737] | 1.635 [1.075, 2.453] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.458] | 3.500 [2.222, 5.260] | 1.577 [0.981, 2.434] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.172, 0.517] | 3.654 [2.386, 5.400] | 1.481 [0.975, 2.167] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.692 [2.394, 5.500] | 1.606 [1.045, 2.417] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.706 [3.629, 8.833] | 2.132 [1.359, 3.321] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.444 (no interval) | 6.583 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.680] | 3.500 [2.515, 5.000] | 1.548 [1.057, 2.338] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.650] | 3.308 [2.182, 4.913] | 1.404 [0.960, 2.097] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.244, 0.619] | 3.462 [2.214, 5.208] | 1.452 [0.949, 2.250] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.462 [2.240, 5.222] | 1.500 [1.007, 2.229] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.763] | 3.500 [2.250, 5.287] | 1.644 [1.073, 2.487] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.412 [3.444, 8.601] | 2.015 [1.275, 3.201] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 9.889 [6.562, 18.802] | 6.000 [3.778, 12.818] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm+every_day+gate+settle+h41+iorb:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.367, 0.704] | 3.654 [2.621, 5.105] | 1.625 [1.121, 2.425] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.652] | 3.308 [2.171, 4.786] | 1.404 [0.946, 2.063] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 3.462 [2.216, 5.159] | 1.452 [0.942, 2.219] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.265, 0.667] | 3.462 [2.216, 5.111] | 1.500 [1.000, 2.234] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.762] | 3.500 [2.219, 5.200] | 1.644 [1.087, 2.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.967] | 5.412 [3.360, 8.309] | 2.015 [1.250, 3.143] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 10.222 (no interval) | 6.194 (no interval) |

Recall with equal weight per regime: 0.641 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 4/5).

risk_gbm+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.387, 0.762] | 3.923 [2.333, 6.167] | 1.644 [0.917, 2.703] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.462 [2.743, 6.938] | 1.865 [1.091, 3.031] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 5.038 [3.028, 7.834] | 2.231 [1.250, 3.672] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.231 [2.484, 6.640] | 1.654 [0.898, 2.734] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 3.769 [2.178, 6.062] | 1.663 [0.913, 2.778] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.176 [4.470, 11.500] | 3.088 [1.783, 5.222] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.000 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.433, 0.792] | 5.000 [3.355, 7.364] | 2.154 [1.333, 3.370] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 4.885 [3.121, 7.305] | 2.019 [1.213, 3.205] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.577 [2.807, 6.966] | 1.962 [1.138, 3.154] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.923 [2.375, 6.168] | 1.596 [0.889, 2.656] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.560] | 4.077 [2.500, 6.436] | 1.827 [1.077, 3.000] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.786, 11.445] | 3.147 [1.880, 5.250] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.333 (no interval) | 4.139 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.400, 0.762] | 4.462 [3.034, 6.625] | 1.933 [1.262, 2.958] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.556] | 4.346 [2.875, 6.500] | 1.712 [1.129, 2.584] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.692 [2.966, 7.250] | 2.029 [1.250, 3.228] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.385 [2.812, 6.715] | 1.894 [1.144, 3.023] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.385 [2.793, 6.721] | 2.067 [1.243, 3.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.647 [4.050, 10.778] | 2.765 [1.566, 4.844] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 9.000 (no interval) | 5.361 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.389, 0.783] | 4.077 [2.514, 6.401] | 1.750 [0.993, 2.903] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.630] | 4.923 [2.966, 7.680] | 2.135 [1.154, 3.562] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.259, 0.630] | 4.423 [2.513, 7.106] | 2.000 [1.041, 3.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.226, 0.583] | 3.731 [1.895, 6.231] | 1.769 [0.796, 3.219] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.577] | 3.846 [2.000, 6.381] | 1.856 [0.848, 3.329] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.647 [4.909, 11.833] | 3.309 [1.981, 5.614] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.416 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.778] | 4.000 [2.370, 6.250] | 1.673 [0.916, 2.800] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.577] | 4.923 [3.000, 7.625] | 2.163 [1.176, 3.630] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.613] | 4.385 [2.464, 7.000] | 1.962 [0.954, 3.408] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.769 [1.929, 6.250] | 1.779 [0.780, 3.188] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.923 [2.102, 6.418] | 1.933 [0.904, 3.414] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 7.647 [4.863, 12.333] | 3.309 [1.883, 5.773] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.889 [1.285, 6.500] | 1.917 [0.659, 4.917] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.381, 0.765] | 4.077 [2.424, 6.412] | 1.750 [0.982, 2.920] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.350, 0.731] | 4.385 [2.500, 7.042] | 1.990 [1.044, 3.393] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.538 [2.613, 7.228] | 2.115 [1.156, 3.542] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.962 [2.239, 6.348] | 1.933 [1.008, 3.299] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.769 [2.040, 6.239] | 1.865 [0.938, 3.313] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.118 [4.429, 11.468] | 3.103 [1.750, 5.232] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 4.111 [2.071, 9.250] | 2.639 [1.087, 6.450] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.393, 0.778] | 4.000 [2.345, 6.305] | 1.673 [0.911, 2.816] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.737] | 4.423 [2.524, 7.106] | 1.981 [1.058, 3.342] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.282, 0.667] | 4.385 [2.451, 7.167] | 2.019 [1.043, 3.486] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.808 [2.074, 6.294] | 1.856 [0.909, 3.284] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.615 [1.937, 6.034] | 1.827 [0.884, 3.273] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.556, 1.000] | 7.118 [4.417, 11.445] | 3.103 [1.776, 5.417] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.760] | 4.231 [2.529, 6.465] | 1.817 [1.033, 2.868] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.238, 0.609] | 5.038 [3.067, 7.828] | 2.231 [1.242, 3.717] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.609] | 4.346 [2.310, 7.000] | 1.962 [0.952, 3.422] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.962 [2.117, 6.421] | 1.885 [0.890, 3.329] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 4.038 [2.182, 6.500] | 1.962 [0.942, 3.442] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.647 [4.944, 12.251] | 3.309 [1.943, 5.662] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.111 (no interval) | 2.694 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.424, 0.794] | 4.269 [2.677, 6.468] | 1.827 [1.070, 2.902] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 5.000 [3.038, 7.667] | 2.221 [1.249, 3.625] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.308 [2.366, 6.900] | 1.923 [0.948, 3.313] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 4.731 [2.709, 7.560] | 2.596 [1.269, 4.530] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 4.192 [2.379, 6.706] | 2.115 [1.103, 3.608] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.647 [5.035, 11.824] | 3.309 [2.000, 5.445] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.556 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.762] | 4.231 [2.548, 6.625] | 1.817 [1.030, 3.011] |
| lead 2 alone (fail) | 26 | 14 | 0.538 [0.343, 0.731] | 4.462 [2.583, 7.160] | 2.048 [1.096, 3.513] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.423 [2.555, 7.106] | 2.038 [1.101, 3.463] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.318, 6.549] | 1.962 [1.036, 3.393] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.277, 6.543] | 2.029 [1.054, 3.519] |
| inside 2018-2019 | 17 | 13 | 0.765 (no interval) | 7.118 (no interval) | 3.103 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 2.806 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.423, 0.793] | 4.269 [2.675, 6.786] | 1.827 [1.075, 3.036] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.741] | 4.385 [2.555, 7.077] | 1.971 [1.062, 3.321] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.300, 0.710] | 4.462 [2.571, 7.279] | 2.106 [1.125, 3.583] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.038 [2.304, 6.543] | 1.971 [1.029, 3.394] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.808 [2.178, 6.158] | 1.933 [1.000, 3.337] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.118 [4.444, 11.333] | 3.103 [1.766, 5.401] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 3.028 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.308, 0.704] | 4.731 [2.828, 7.500] | 2.346 [1.326, 3.929] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 5.231 [3.273, 8.173] | 2.298 [1.316, 3.793] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.385 [2.433, 7.126] | 1.981 [1.000, 3.511] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 3.769 [1.963, 6.391] | 1.779 [0.808, 3.270] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.615] | 4.577 [2.652, 7.421] | 2.077 [1.073, 3.661] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.882] | 7.824 [4.856, 12.500] | 3.735 [2.152, 6.398] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 3.333 [1.444, 8.000] | 2.056 [0.797, 5.572] |

Recall with equal weight per regime: 0.387 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.692] | 4.538 [2.730, 7.002] | 2.125 [1.173, 3.515] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.885 [2.956, 7.467] | 2.183 [1.167, 3.597] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.308 [2.399, 6.852] | 1.923 [0.926, 3.290] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.808 [2.038, 6.232] | 1.788 [0.812, 3.125] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.260, 6.579] | 2.029 [1.015, 3.530] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.529 [4.737, 11.938] | 3.441 [2.014, 5.887] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.706] | 4.731 [2.833, 7.501] | 2.346 [1.274, 3.917] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.320, 0.696] | 4.269 [2.483, 6.915] | 1.990 [1.069, 3.381] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.154 [2.390, 6.765] | 1.952 [1.040, 3.329] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.885 [2.173, 6.349] | 1.856 [0.963, 3.196] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.769 [2.071, 6.261] | 1.837 [0.906, 3.224] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.900] | 7.471 [4.615, 12.385] | 3.529 [1.966, 6.313] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.444 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.308, 0.692] | 4.538 [2.576, 7.143] | 2.125 [1.129, 3.538] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 4.000 [2.185, 6.475] | 1.856 [0.938, 3.167] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.308, 0.692] | 4.615 [2.608, 7.320] | 2.154 [1.157, 3.611] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.808 [2.091, 6.269] | 1.827 [0.899, 3.222] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.692 [2.026, 6.065] | 1.846 [0.913, 3.278] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.176 [4.333, 11.670] | 3.235 [1.818, 5.650] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.350, 0.739] | 4.885 [3.038, 7.824] | 2.413 [1.360, 4.075] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.885 [3.033, 7.783] | 2.212 [1.275, 3.750] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.385 [2.500, 7.278] | 1.971 [1.009, 3.471] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.115 [2.233, 6.952] | 2.087 [0.981, 3.837] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 4.462 [2.536, 7.346] | 2.019 [1.019, 3.588] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.824 [5.000, 12.923] | 3.735 [2.132, 6.876] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.333 (no interval) | 2.583 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.346, 0.727] | 4.769 [2.905, 7.286] | 2.298 [1.310, 3.648] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.579] | 4.808 [2.903, 7.424] | 2.163 [1.194, 3.533] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.385 [2.476, 7.002] | 2.000 [1.008, 3.380] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.538 [2.441, 7.421] | 2.490 [1.148, 4.529] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 3.846 [2.057, 6.217] | 1.856 [0.875, 3.226] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.529 [4.749, 12.071] | 3.441 [2.021, 5.778] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.731] | 4.885 [3.040, 7.625] | 2.413 [1.383, 4.001] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 3.962 [2.286, 6.529] | 1.865 [0.979, 3.221] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.115 [2.387, 6.744] | 1.933 [1.016, 3.303] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.038 [2.312, 6.600] | 2.096 [1.062, 3.659] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.731 [2.069, 6.143] | 1.856 [0.913, 3.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.471 [4.571, 12.111] | 3.529 [1.984, 6.233] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.727] | 4.769 [2.844, 7.334] | 2.298 [1.316, 3.684] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 3.962 [2.167, 6.391] | 1.837 [0.928, 3.089] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.303, 0.704] | 4.615 [2.636, 7.263] | 2.144 [1.155, 3.536] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.385 [2.417, 7.183] | 2.462 [1.167, 4.472] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.192 [2.280, 6.867] | 2.433 [1.152, 4.420] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.882] | 7.176 [4.260, 11.636] | 3.235 [1.775, 5.611] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 3.806 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.423 [0.974, 2.091] | 0.760 [0.477, 1.217] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.594, 1.516] | 0.548 [0.302, 0.926] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.385 [0.864, 2.160] | 0.885 [0.471, 1.560] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.154 [0.704, 1.824] | 0.683 [0.370, 1.174] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.600] | 1.115 [0.666, 1.783] | 0.760 [0.393, 1.333] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.667 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.719] | 1.500 [1.000, 2.286] | 0.971 [0.556, 1.633] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.655, 1.778] | 0.644 [0.302, 1.174] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.385 [0.857, 2.227] | 0.913 [0.464, 1.638] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.231 [0.727, 1.955] | 0.760 [0.364, 1.359] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.667 [1.769, 8.500] | 3.306 [1.479, 8.002] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.440, 0.800] | 5.077 [3.348, 7.455] | 2.192 [1.351, 3.461] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.207, 7.400] | 2.029 [1.250, 3.234] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.692 [2.889, 7.286] | 2.038 [1.194, 3.274] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.263, 0.600] | 4.385 [2.710, 6.789] | 1.913 [1.142, 3.070] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 4.423 [2.703, 6.929] | 2.087 [1.241, 3.395] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.471 [4.773, 11.779] | 3.176 [1.867, 5.251] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 8.667 (no interval) | 4.889 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 3.462 [2.429, 5.100] | 1.644 [1.108, 2.528] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.516] | 3.808 [2.562, 5.653] | 1.558 [1.013, 2.364] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 3.500 [2.233, 5.353] | 1.596 [1.008, 2.500] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.567] | 3.808 [2.500, 5.715] | 1.606 [1.050, 2.430] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.731 [2.367, 5.600] | 1.625 [1.042, 2.475] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 5.765 [3.759, 9.154] | 2.191 [1.416, 3.568] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.111 (no interval) | 6.389 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.428, 0.800] | 4.577 [2.931, 7.000] | 1.971 [1.213, 3.163] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.600] | 4.462 [2.733, 7.000] | 1.837 [1.078, 3.068] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.923 [2.967, 7.740] | 2.202 [1.213, 3.667] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.637] | 4.385 [2.621, 6.884] | 1.837 [1.060, 3.060] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 3.962 [2.343, 6.391] | 1.808 [1.033, 3.090] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.176 [4.416, 11.400] | 3.088 [1.760, 5.171] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 5.778 (no interval) | 3.528 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.115 [3.455, 7.417] | 2.212 [1.401, 3.400] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.846 [3.138, 7.211] | 1.981 [1.217, 3.063] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.500 [2.743, 6.960] | 1.942 [1.141, 3.136] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.192 [2.555, 6.365] | 1.808 [1.048, 2.917] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.269 [2.617, 6.534] | 1.971 [1.154, 3.153] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.471 [4.909, 11.714] | 3.176 [1.945, 5.269] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 7.222 [4.437, 13.600] | 4.028 [2.346, 8.625] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.763] | 4.577 [3.085, 6.882] | 2.106 [1.336, 3.323] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.229, 0.550] | 4.308 [2.793, 6.467] | 1.692 [1.090, 2.604] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.615 [2.842, 7.157] | 2.058 [1.217, 3.342] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.577 [2.943, 7.000] | 2.058 [1.274, 3.278] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.385 [2.760, 6.768] | 2.048 [1.226, 3.328] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.706 [4.080, 10.750] | 2.824 [1.590, 4.767] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.751] | 8.556 [5.599, 16.750] | 5.167 [3.143, 11.000] |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.767] | 4.808 [2.965, 7.319] | 2.183 [1.250, 3.492] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.607] | 4.885 [2.954, 7.500] | 2.125 [1.146, 3.476] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 4.615 [2.658, 7.200] | 2.173 [1.160, 3.550] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.231 [2.474, 6.650] | 1.933 [0.988, 3.268] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 3.808 [2.000, 6.185] | 1.837 [0.857, 3.238] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.955] | 7.647 [4.908, 11.932] | 3.309 [1.932, 5.584] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 4.556 [2.333, 9.752] | 2.806 [1.204, 6.720] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.368, 0.778] | 4.692 [2.853, 7.080] | 2.115 [1.202, 3.375] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 4.731 [2.760, 7.333] | 2.058 [1.064, 3.408] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.607] | 4.423 [2.416, 6.953] | 2.000 [1.000, 3.363] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.564] | 3.808 [2.000, 6.108] | 1.788 [0.836, 3.100] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.564] | 3.885 [2.065, 6.269] | 1.885 [0.879, 3.303] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.958] | 7.647 [4.857, 11.616] | 3.309 [1.946, 5.364] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.556 [1.143, 6.168] | 1.722 [0.573, 4.750] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.368, 0.767] | 4.808 [2.913, 7.350] | 2.183 [1.240, 3.529] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.304, 0.700] | 4.808 [2.869, 7.486] | 2.202 [1.230, 3.607] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.304, 0.700] | 4.577 [2.633, 7.251] | 2.192 [1.180, 3.635] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 3.808 [1.958, 6.224] | 1.913 [0.939, 3.274] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 4.077 [2.182, 6.591] | 2.029 [1.007, 3.448] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.118 [4.438, 11.504] | 3.103 [1.771, 5.322] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.370, 0.769] | 4.692 [2.956, 7.130] | 2.115 [1.236, 3.434] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.462 [2.652, 7.000] | 1.990 [1.089, 3.292] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.192 [2.333, 6.750] | 1.933 [1.018, 3.284] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.808 [2.052, 6.211] | 1.904 [0.947, 3.303] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.923 [2.194, 6.321] | 1.971 [1.017, 3.381] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.000 [4.368, 11.231] | 3.074 [1.760, 5.143] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.778 (no interval) | 1.861 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.419, 0.800] | 4.654 [2.969, 6.947] | 2.010 [1.230, 3.191] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.238, 0.600] | 4.923 [2.963, 7.478] | 2.144 [1.196, 3.460] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.462 [2.484, 6.955] | 2.077 [1.055, 3.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 4.077 [2.333, 6.435] | 1.904 [0.982, 3.219] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 4.192 [2.395, 6.636] | 2.106 [1.103, 3.554] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 7.647 [4.952, 11.875] | 3.309 [1.985, 5.501] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 5.333 (no interval) | 3.444 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.774] | 4.885 [3.057, 7.550] | 2.202 [1.280, 3.597] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.588] | 4.962 [2.998, 7.783] | 2.212 [1.219, 3.751] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.233, 0.625] | 4.308 [2.344, 7.056] | 1.923 [0.932, 3.375] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.577] | 4.000 [2.207, 6.546] | 1.865 [0.932, 3.313] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.577] | 4.192 [2.346, 6.833] | 2.106 [1.068, 3.707] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.647 [4.832, 12.105] | 3.309 [1.929, 5.776] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 4.444 [2.308, 10.000] | 2.861 [1.300, 7.250] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 4.654 [2.970, 7.125] | 2.010 [1.198, 3.250] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.615 [2.666, 7.351] | 2.125 [1.169, 3.567] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.385 [2.417, 7.100] | 2.058 [1.083, 3.490] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.308, 0.682] | 4.000 [2.195, 6.688] | 1.990 [1.043, 3.441] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 4.269 [2.444, 7.000] | 2.135 [1.129, 3.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.118 [4.500, 11.500] | 3.103 [1.779, 5.413] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.667 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.381, 0.767] | 4.885 [3.033, 7.517] | 2.202 [1.315, 3.609] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.577 [2.666, 7.251] | 2.087 [1.169, 3.476] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.346 [2.437, 7.002] | 2.048 [1.102, 3.520] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.077 [2.285, 6.644] | 2.029 [1.086, 3.527] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.269 [2.500, 6.886] | 2.231 [1.260, 3.780] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.000 [4.350, 11.231] | 3.074 [1.795, 5.264] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.667 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.308, 0.704] | 5.115 [3.214, 7.800] | 2.481 [1.433, 4.084] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 5.000 [3.107, 7.751] | 2.192 [1.237, 3.645] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.462 [2.529, 7.063] | 2.058 [1.062, 3.513] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.962 [2.249, 6.356] | 1.808 [0.875, 3.173] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.500 [2.580, 7.179] | 2.029 [1.018, 3.530] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.385, 0.895] | 7.824 [4.951, 12.618] | 3.735 [2.178, 6.573] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 3.778 [1.667, 9.000] | 2.167 [0.833, 5.627] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.300, 0.700] | 4.808 [2.900, 7.656] | 2.221 [1.255, 3.742] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.207, 0.579] | 4.769 [2.814, 7.637] | 2.096 [1.137, 3.552] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.346 [2.400, 7.143] | 1.942 [0.968, 3.456] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.885 [2.077, 6.445] | 1.779 [0.837, 3.250] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.962 [2.142, 6.601] | 1.904 [0.917, 3.536] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.529 [4.583, 12.357] | 3.441 [1.962, 6.017] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.778 [1.118, 7.000] | 1.583 [0.500, 4.550] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.305, 0.700] | 5.115 [3.193, 7.901] | 2.481 [1.426, 4.174] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.654 [2.889, 7.222] | 2.144 [1.240, 3.540] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.115 [2.381, 6.525] | 1.971 [1.069, 3.334] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 3.885 [2.130, 6.287] | 1.904 [0.981, 3.318] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.115 [2.357, 6.667] | 2.010 [1.028, 3.490] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.391, 0.889] | 7.471 [4.651, 12.455] | 3.529 [1.986, 6.400] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.000 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.708] | 4.808 [2.878, 7.334] | 2.221 [1.232, 3.598] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 4.192 [2.363, 6.560] | 1.913 [0.977, 3.207] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.304, 0.708] | 4.346 [2.406, 6.927] | 1.962 [0.981, 3.343] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.846 [1.971, 6.300] | 1.913 [0.921, 3.369] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 4.000 [2.219, 6.391] | 1.990 [1.006, 3.438] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 7.059 [4.111, 11.638] | 3.206 [1.739, 5.567] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 3.000 [1.333, 6.800] | 1.889 [0.656, 4.952] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.333, 0.741] | 5.077 [3.090, 7.880] | 2.500 [1.398, 4.195] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.243, 0.607] | 4.769 [2.789, 7.483] | 2.125 [1.143, 3.550] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.462 [2.500, 7.235] | 2.077 [1.080, 3.536] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 4.077 [2.192, 6.667] | 2.038 [0.941, 3.636] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 4.538 [2.522, 7.333] | 2.125 [1.056, 3.662] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.824 [4.857, 12.369] | 3.735 [2.111, 6.377] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.083, 0.778] | 4.000 [1.583, 10.000] | 3.083 [1.018, 8.709] |

Recall with equal weight per regime: 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.333, 0.739] | 4.654 [2.739, 7.308] | 2.221 [1.211, 3.702] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.808 [2.771, 7.525] | 2.192 [1.141, 3.667] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.233, 0.615] | 4.308 [2.299, 6.951] | 1.923 [0.901, 3.340] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.577 [2.417, 7.648] | 2.529 [1.134, 4.613] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 3.846 [1.952, 6.500] | 1.846 [0.790, 3.372] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.895] | 7.529 [4.611, 12.429] | 3.441 [1.922, 6.036] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.000 [1.077, 10.750] | 3.472 [0.611, 10.102] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.346, 0.743] | 5.077 [3.166, 8.000] | 2.500 [1.454, 4.167] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.308 [2.536, 6.889] | 2.029 [1.121, 3.375] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.077 [2.350, 6.561] | 1.952 [1.066, 3.350] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.312, 0.696] | 4.077 [2.261, 6.709] | 2.154 [1.120, 3.845] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.038 [2.260, 6.651] | 1.990 [1.022, 3.523] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.909] | 7.471 [4.524, 12.377] | 3.529 [1.966, 6.344] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.556 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.345, 0.742] | 4.654 [2.817, 7.174] | 2.221 [1.257, 3.646] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.077 [2.371, 6.500] | 1.875 [1.000, 3.261] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.308, 0.714] | 4.500 [2.640, 7.112] | 2.087 [1.132, 3.555] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.500 [2.500, 7.612] | 2.567 [1.202, 4.786] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.500 [2.533, 7.588] | 2.548 [1.204, 4.678] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.409, 0.900] | 7.059 [4.333, 11.455] | 3.206 [1.804, 5.525] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.000 [1.250, 11.200] | 3.528 [0.841, 10.752] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.769] | 2.192 [1.500, 3.408] | 1.538 [0.960, 2.548] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.846 [1.162, 2.923] | 1.375 [0.789, 2.352] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.469] | 1.769 [1.138, 2.778] | 1.221 [0.700, 2.111] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.233, 0.552] | 2.115 [1.368, 3.360] | 1.625 [0.942, 2.750] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.387, 3.364] | 1.577 [0.892, 2.704] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 6.556 (no interval) | 5.806 (no interval) |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

risk_logistic+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.560] | 4.269 [2.615, 6.543] | 1.875 [1.089, 3.013] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.205, 7.364] | 2.067 [1.250, 3.264] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 4.615 [2.846, 7.113] | 2.029 [1.182, 3.250] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.269 [2.615, 6.551] | 1.885 [1.081, 3.092] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.645] | 4.962 [3.103, 7.519] | 2.202 [1.312, 3.501] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.824] | 6.471 [3.949, 10.267] | 2.574 [1.425, 4.376] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.667 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.645] | 3.808 [2.750, 5.313] | 1.750 [1.212, 2.562] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 3.846 [2.577, 5.601] | 1.558 [1.033, 2.326] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.462] | 3.423 [2.182, 5.211] | 1.510 [0.951, 2.360] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.419] | 3.731 [2.535, 5.438] | 1.817 [1.192, 2.750] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.321, 0.680] | 4.269 [2.857, 6.292] | 2.067 [1.398, 3.070] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.765 [4.545, 10.167] | 2.750 [1.815, 4.173] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.333 (no interval) | 6.528 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.630] | 4.731 [3.000, 7.044] | 2.212 [1.350, 3.448] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.759, 6.953] | 1.875 [1.060, 3.074] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.263, 0.588] | 4.269 [2.588, 6.700] | 1.846 [1.052, 3.063] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.500 [2.749, 6.875] | 2.115 [1.203, 3.393] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.640] | 5.154 [3.240, 7.786] | 2.298 [1.365, 3.632] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.917] | 7.941 [5.222, 12.375] | 3.368 [2.016, 5.614] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.100, 0.556] | 5.000 [2.667, 10.667] | 2.972 [1.515, 6.876] |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.192 [2.552, 6.522] | 1.856 [1.083, 3.060] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.846 [3.093, 7.333] | 2.019 [1.225, 3.250] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 4.423 [2.708, 6.923] | 1.933 [1.143, 3.210] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.077 [2.440, 6.429] | 1.779 [1.012, 2.956] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.808 [2.961, 7.417] | 2.087 [1.212, 3.368] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.833] | 6.471 [3.765, 10.714] | 2.574 [1.381, 4.526] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.222 (no interval) | 4.111 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.759] | 5.154 [3.479, 7.600] | 2.279 [1.464, 3.515] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.257, 0.606] | 4.923 [3.193, 7.456] | 2.115 [1.281, 3.355] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 4.154 [2.444, 6.600] | 1.856 [1.045, 3.114] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.385 [2.758, 6.793] | 2.010 [1.214, 3.250] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.231 [3.353, 7.895] | 2.394 [1.507, 3.781] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.588, 11.365] | 2.926 [1.720, 5.002] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 8.556 [5.375, 16.671] | 5.139 [2.979, 11.381] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_logistic+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.444] | 3.885 [2.069, 6.319] | 1.769 [0.871, 3.001] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.385 [2.667, 6.734] | 1.798 [1.015, 2.888] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.524] | 3.846 [2.182, 6.087] | 1.683 [0.898, 2.792] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 3.462 [1.926, 5.589] | 1.606 [0.841, 2.700] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.524, 7.385] | 2.183 [1.131, 3.733] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.818] | 6.706 [3.909, 10.734] | 2.735 [1.467, 4.765] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.111 [2.000, 9.603] | 2.917 [1.179, 7.292] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 5.115 [3.227, 7.643] | 2.202 [1.286, 3.444] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.610] | 4.077 [2.400, 6.364] | 1.596 [0.855, 2.625] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.654 [1.938, 5.870] | 1.490 [0.741, 2.531] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 3.077 [1.542, 5.137] | 1.356 [0.629, 2.407] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.610] | 4.692 [2.733, 7.455] | 2.308 [1.235, 3.922] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.706 [5.000, 12.000] | 3.191 [1.889, 5.209] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.440] | 3.885 [2.125, 6.364] | 1.769 [0.885, 3.054] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.062, 0.350] | 3.538 [1.812, 5.910] | 1.683 [0.808, 2.973] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.480] | 3.731 [2.000, 6.177] | 1.721 [0.845, 3.052] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.550] | 3.500 [2.000, 5.600] | 1.500 [0.804, 2.531] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.571] | 3.346 [1.815, 5.500] | 1.481 [0.760, 2.548] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.444, 0.867] | 6.588 [4.000, 10.616] | 2.735 [1.536, 4.688] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.778 [0.538, 4.500] | 1.472 [0.375, 4.000] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.654] | 5.115 [3.267, 7.609] | 2.202 [1.331, 3.490] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.500] | 4.038 [2.154, 6.584] | 1.827 [0.930, 3.162] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.484] | 3.500 [1.786, 5.924] | 1.663 [0.793, 3.017] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.560] | 3.615 [1.941, 5.923] | 1.712 [0.833, 3.047] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.000 [1.467, 5.042] | 1.365 [0.636, 2.413] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 7.471 [4.882, 11.235] | 3.044 [1.879, 4.861] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.626] | 1.889 [0.500, 5.000] | 1.583 [0.375, 4.500] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 3.808 [2.185, 6.067] | 1.740 [0.987, 2.903] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.462 [2.700, 6.914] | 1.856 [1.070, 3.034] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 3.885 [2.160, 6.227] | 1.702 [0.930, 2.863] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.516] | 3.462 [1.933, 5.667] | 1.596 [0.853, 2.775] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.192 [2.389, 6.696] | 1.856 [1.043, 3.084] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.826] | 6.294 [3.750, 10.232] | 2.500 [1.386, 4.417] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.556 [2.461, 9.252] | 3.028 [1.525, 6.702] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.370, 0.714] | 5.038 [3.319, 7.616] | 2.173 [1.350, 3.410] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.231 [2.500, 6.774] | 1.644 [0.905, 2.737] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.769 [2.071, 6.239] | 1.587 [0.826, 2.726] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.577 [2.000, 5.834] | 1.615 [0.850, 2.800] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.885 [2.823, 7.775] | 2.413 [1.299, 4.055] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.706 [5.071, 11.900] | 3.191 [1.916, 5.250] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.444 [2.857, 12.254] | 3.861 [1.775, 9.438] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.520] | 3.808 [2.212, 6.002] | 1.740 [0.960, 2.840] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.480] | 4.038 [2.286, 6.438] | 1.971 [1.048, 3.262] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 3.423 [1.895, 5.566] | 1.519 [0.774, 2.611] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.261, 0.585] | 3.885 [2.316, 6.143] | 1.740 [1.000, 2.844] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.226, 0.562] | 3.731 [2.107, 5.959] | 1.721 [0.944, 2.869] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 6.588 [3.937, 10.644] | 2.735 [1.511, 4.695] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.556 [2.500, 10.143] | 2.861 [1.500, 7.002] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.357, 0.714] | 5.038 [3.300, 7.385] | 2.173 [1.367, 3.322] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.613] | 4.500 [2.583, 7.059] | 2.077 [1.125, 3.433] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.476] | 3.154 [1.600, 5.226] | 1.423 [0.700, 2.475] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.258, 0.583] | 4.038 [2.320, 6.421] | 2.019 [1.086, 3.399] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 3.385 [1.844, 5.501] | 1.606 [0.854, 2.712] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.917] | 7.471 [4.823, 11.500] | 3.044 [1.849, 4.956] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.667 [2.467, 9.800] | 2.972 [1.400, 7.000] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.444] | 4.038 [2.278, 6.542] | 1.837 [0.965, 3.125] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 4.423 [2.708, 6.962] | 1.837 [1.061, 3.065] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.531] | 4.462 [2.583, 7.150] | 2.106 [1.140, 3.575] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.471] | 3.385 [1.818, 5.600] | 1.529 [0.779, 2.690] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 5.269 [3.296, 8.143] | 2.606 [1.526, 4.227] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.833] | 7.588 [4.857, 11.728] | 3.353 [2.032, 5.438] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.240, 0.606] | 4.808 [2.961, 7.316] | 2.260 [1.298, 3.609] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.115 [2.458, 6.371] | 1.635 [0.906, 2.723] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.538] | 3.577 [1.937, 5.826] | 1.452 [0.727, 2.528] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.433] | 3.115 [1.588, 5.167] | 1.365 [0.647, 2.427] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 3.385 [1.786, 5.574] | 1.577 [0.767, 2.764] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 7.706 [4.957, 11.815] | 3.324 [1.982, 5.361] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 2.333 [0.800, 6.144] | 1.778 [0.487, 4.793] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.440] | 4.038 [2.281, 6.441] | 1.837 [0.956, 3.074] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.154, 0.483] | 3.962 [2.250, 6.390] | 1.894 [1.008, 3.175] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.483] | 3.462 [1.808, 5.773] | 1.644 [0.794, 2.954] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.654 [2.037, 5.844] | 1.538 [0.802, 2.540] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.885 [2.999, 7.446] | 2.192 [1.231, 3.632] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.864] | 7.235 [4.500, 11.184] | 3.015 [1.761, 4.938] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.778 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.241, 0.613] | 4.808 [2.816, 7.361] | 2.260 [1.228, 3.647] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.176, 0.533] | 4.154 [2.266, 6.708] | 1.894 [0.943, 3.250] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.114, 0.444] | 3.423 [1.677, 5.818] | 1.606 [0.701, 2.935] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 3.615 [1.909, 6.000] | 1.702 [0.776, 3.063] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 3.115 [1.647, 5.167] | 1.394 [0.696, 2.470] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 7.353 [4.636, 11.590] | 3.250 [1.866, 5.500] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.222 (no interval) | 1.667 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 3.846 [2.178, 6.161] | 1.750 [0.967, 2.838] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 4.231 [2.478, 6.609] | 1.808 [1.022, 2.880] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.210, 0.572] | 4.500 [2.545, 7.209] | 2.144 [1.139, 3.581] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 3.615 [2.000, 5.920] | 1.788 [0.937, 2.956] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 5.231 [3.103, 8.134] | 2.596 [1.468, 4.201] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.350, 0.833] | 7.588 [4.857, 12.000] | 3.353 [1.989, 5.520] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 4.000 [1.667, 10.008] | 3.444 [1.288, 9.200] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.679] | 4.654 [2.904, 7.053] | 2.212 [1.295, 3.511] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.500 [2.625, 6.883] | 1.846 [1.014, 2.975] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.846 [2.080, 6.125] | 1.663 [0.884, 2.775] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 4.000 [2.222, 6.571] | 2.173 [1.086, 3.800] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 3.885 [2.040, 6.370] | 2.000 [0.963, 3.531] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.824 [4.944, 12.072] | 3.441 [2.033, 5.607] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.222 (no interval) | 4.583 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 3.846 [2.238, 6.067] | 1.750 [0.968, 2.864] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 3.538 [1.838, 5.846] | 1.683 [0.800, 2.960] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.529] | 3.692 [1.999, 6.106] | 1.846 [0.932, 3.193] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.632] | 4.038 [2.344, 6.335] | 1.875 [1.024, 3.053] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.636] | 4.962 [3.000, 7.556] | 2.327 [1.320, 3.786] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 7.235 [4.625, 11.310] | 3.015 [1.833, 4.958] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 3.333 [1.332, 8.000] | 2.750 [0.893, 7.301] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.686] | 4.654 [2.925, 6.900] | 2.212 [1.320, 3.438] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.138, 0.500] | 4.077 [2.178, 6.619] | 1.837 [0.904, 3.159] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.474] | 3.077 [1.555, 5.137] | 1.433 [0.681, 2.525] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 4.346 [2.333, 7.143] | 2.433 [1.106, 4.393] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.423] | 3.462 [1.677, 5.889] | 1.692 [0.731, 3.060] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.471, 0.923] | 7.353 [4.550, 11.584] | 3.250 [1.864, 5.353] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.222 (no interval) | 3.806 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.762] | 2.192 [1.464, 3.419] | 1.538 [0.921, 2.600] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.469] | 1.769 [1.094, 2.883] | 1.269 [0.684, 2.271] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.577 [0.880, 2.640] | 1.163 [0.571, 2.121] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.423 [0.771, 2.381] | 1.010 [0.449, 1.889] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.038 [1.297, 3.294] | 1.462 [0.804, 2.600] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.333 (no interval) | 4.667 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

risk_logistic_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.154 [2.500, 6.347] | 1.798 [1.033, 2.875] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.885 [3.133, 7.251] | 2.010 [1.227, 3.105] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.654 [2.864, 7.073] | 2.010 [1.191, 3.191] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.231 [2.611, 6.500] | 1.894 [1.087, 3.007] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.647] | 5.038 [3.184, 7.571] | 2.260 [1.346, 3.510] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.818, 10.167] | 2.574 [1.379, 4.334] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.333 (no interval) | 4.639 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.684] | 4.000 [2.878, 5.750] | 1.913 [1.323, 2.870] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.808 [2.545, 5.706] | 1.519 [1.018, 2.316] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.423 [2.162, 5.385] | 1.481 [0.920, 2.410] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.654 [2.472, 5.476] | 1.712 [1.121, 2.650] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.316, 0.679] | 4.154 [2.788, 6.259] | 1.952 [1.308, 3.039] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.765 [4.500, 10.252] | 2.750 [1.787, 4.251] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.667 (no interval) | 5.944 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.588] | 4.115 [2.499, 6.294] | 1.750 [1.010, 2.794] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 4.423 [2.709, 6.843] | 1.817 [1.062, 2.942] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 4.231 [2.536, 6.653] | 1.798 [1.024, 2.950] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.800, 6.955] | 2.144 [1.250, 3.429] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 5.115 [3.318, 7.636] | 2.308 [1.405, 3.592] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.059 [5.524, 12.250] | 3.441 [2.180, 5.500] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 2.389 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.500, 6.333] | 1.779 [1.033, 2.834] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.769 [3.000, 7.126] | 1.962 [1.173, 3.074] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.462 [2.667, 6.864] | 1.913 [1.065, 3.100] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.381, 6.351] | 1.798 [0.983, 2.947] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.885 [2.999, 7.371] | 2.144 [1.224, 3.389] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.846, 10.067] | 2.574 [1.389, 4.263] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.889 (no interval) | 3.778 (no interval) |

Recall with equal weight per regime: 0.422 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.038 [3.378, 7.591] | 2.163 [1.372, 3.465] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 5.000 [3.280, 7.619] | 2.087 [1.307, 3.322] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.423 [2.722, 7.000] | 1.952 [1.150, 3.250] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.385 [2.727, 6.813] | 2.010 [1.183, 3.243] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 5.038 [3.208, 7.847] | 2.375 [1.469, 3.766] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 0.952] | 7.000 [4.399, 11.000] | 2.838 [1.647, 4.694] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.000 (no interval) | 4.694 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.429] | 3.692 [2.030, 6.000] | 1.663 [0.808, 2.859] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 4.731 [2.808, 7.458] | 2.058 [1.106, 3.407] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 3.923 [2.228, 6.317] | 1.673 [0.889, 2.802] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.560] | 3.885 [2.054, 6.423] | 1.981 [0.971, 3.425] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.615 [2.636, 7.401] | 2.231 [1.161, 3.789] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.824] | 6.706 [4.042, 10.801] | 2.735 [1.483, 4.667] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.889 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.258, 0.600] | 3.885 [2.192, 6.360] | 1.769 [0.904, 3.114] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.654 [2.783, 7.409] | 1.981 [1.060, 3.422] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.257, 0.619] | 3.846 [2.139, 6.301] | 1.596 [0.846, 2.758] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.538] | 3.769 [2.000, 6.500] | 1.865 [0.893, 3.415] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.257, 0.619] | 4.154 [2.448, 6.667] | 1.827 [1.000, 3.084] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.929] | 6.824 [4.273, 11.085] | 2.765 [1.533, 4.840] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.167 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.444] | 3.692 [1.970, 6.072] | 1.663 [0.812, 2.900] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.438] | 3.615 [1.833, 6.044] | 1.644 [0.757, 2.886] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 3.423 [1.913, 5.589] | 1.558 [0.828, 2.660] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.300, 0.636] | 4.115 [2.323, 6.600] | 2.058 [1.103, 3.448] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.923 [2.167, 6.336] | 1.990 [1.007, 3.417] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.706 [3.262, 9.500] | 2.485 [1.307, 4.404] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 2.889 (no interval) | 2.194 (no interval) |

Recall with equal weight per regime: 0.437 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.885 [2.120, 6.200] | 1.769 [0.902, 3.011] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.435] | 3.500 [1.731, 5.889] | 1.615 [0.726, 2.838] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.462 [1.217, 4.188] | 0.990 [0.509, 1.650] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 4.231 [2.478, 6.800] | 2.096 [1.114, 3.567] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.808 [2.000, 6.302] | 1.923 [0.903, 3.367] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.857] | 5.647 [3.185, 9.401] | 2.412 [1.234, 4.266] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.000 (no interval) | 2.222 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.885 [2.108, 6.314] | 1.769 [0.890, 2.941] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.962 [2.961, 7.667] | 2.183 [1.186, 3.590] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.281, 0.650] | 3.923 [2.129, 6.276] | 1.683 [0.860, 2.785] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.615 [2.000, 5.957] | 1.673 [0.869, 2.834] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.269 [2.458, 6.778] | 1.904 [1.049, 3.104] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.833] | 6.706 [3.879, 10.934] | 2.735 [1.428, 4.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.300, 0.632] | 4.000 [2.222, 6.309] | 1.827 [0.949, 3.033] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.600] | 4.577 [2.742, 7.039] | 1.817 [1.018, 2.973] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.731 [2.000, 6.050] | 1.519 [0.750, 2.605] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.522] | 3.577 [1.928, 5.720] | 1.654 [0.878, 2.808] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.423 [2.621, 6.876] | 2.010 [1.150, 3.229] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.824 [4.040, 11.000] | 2.765 [1.500, 4.806] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.517] | 3.885 [2.148, 6.375] | 1.769 [0.935, 3.054] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.568] | 3.538 [1.963, 5.849] | 1.567 [0.814, 2.707] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.375, 0.710] | 3.500 [1.974, 5.769] | 1.625 [0.893, 2.750] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.300, 0.625] | 4.308 [2.517, 6.963] | 2.135 [1.202, 3.590] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 3.538 [1.999, 5.833] | 1.673 [0.904, 2.848] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 5.706 [3.230, 9.627] | 2.485 [1.302, 4.375] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.722 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.636] | 4.000 [2.150, 6.476] | 1.827 [0.875, 3.132] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 3.500 [1.894, 5.801] | 1.558 [0.808, 2.631] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 2.500 [1.231, 4.278] | 1.000 [0.510, 1.693] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.636] | 3.692 [2.125, 5.959] | 1.683 [0.929, 2.800] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.577 [1.909, 5.909] | 1.712 [0.905, 2.875] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.423, 0.875] | 5.647 [3.055, 9.251] | 2.412 [1.176, 4.270] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 3.889 [2.077, 8.000] | 2.333 [1.167, 5.188] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.444] | 3.731 [1.969, 6.105] | 1.702 [0.845, 2.913] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.962 [2.966, 7.708] | 2.183 [1.200, 3.552] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.243, 0.613] | 4.038 [2.250, 6.421] | 1.788 [0.936, 2.943] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 3.962 [2.047, 6.544] | 1.971 [0.943, 3.450] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.692 [2.641, 7.481] | 2.250 [1.179, 3.778] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.765 [4.000, 11.000] | 2.794 [1.513, 4.771] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.222 [1.294, 7.750] | 2.222 [0.729, 5.688] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.263, 0.593] | 3.885 [2.138, 6.250] | 1.769 [0.926, 2.948] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 5.000 [3.095, 7.629] | 2.115 [1.196, 3.417] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.846 [2.148, 6.121] | 1.615 [0.830, 2.732] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 3.808 [2.030, 6.251] | 1.875 [0.905, 3.208] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 3.500 [1.944, 5.728] | 1.606 [0.827, 2.719] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.882 [4.181, 10.929] | 2.824 [1.559, 4.733] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.556 (no interval) | 2.306 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 3.731 [2.025, 6.231] | 1.702 [0.853, 3.001] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 4.038 [2.294, 6.579] | 1.913 [1.015, 3.276] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.333, 0.677] | 3.346 [1.869, 5.550] | 1.538 [0.792, 2.704] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.304, 0.632] | 4.192 [2.417, 6.739] | 2.048 [1.104, 3.474] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.478] | 3.962 [2.207, 6.520] | 1.990 [1.029, 3.479] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.870] | 5.706 [3.210, 9.762] | 2.485 [1.323, 4.550] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.194 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.885 [2.174, 6.471] | 1.769 [0.900, 3.066] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.923 [2.181, 6.584] | 1.846 [0.943, 3.214] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.189, 0.520] | 3.115 [1.542, 5.502] | 1.423 [0.659, 2.629] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.115 [2.333, 6.790] | 1.990 [1.018, 3.479] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.846 [2.071, 6.543] | 1.933 [0.960, 3.453] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.529 [3.038, 9.472] | 2.353 [1.147, 4.319] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.512] | 3.923 [2.250, 6.300] | 1.837 [0.966, 3.110] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.769 [2.857, 7.400] | 2.154 [1.216, 3.528] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 3.923 [2.258, 6.224] | 1.683 [0.910, 2.808] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.556] | 3.846 [2.222, 6.305] | 1.942 [1.055, 3.338] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.562] | 4.615 [2.740, 7.313] | 2.202 [1.212, 3.712] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.824] | 6.765 [4.130, 10.929] | 2.794 [1.567, 4.793] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.556 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.296, 0.629] | 4.000 [2.285, 6.500] | 1.856 [0.989, 3.158] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 4.654 [2.806, 7.314] | 2.010 [1.106, 3.355] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.616] | 3.731 [2.038, 6.134] | 1.519 [0.781, 2.616] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 4.115 [2.342, 6.850] | 2.269 [1.125, 4.013] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.038 [2.273, 6.800] | 2.067 [1.040, 3.572] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.941 [4.266, 11.154] | 2.882 [1.643, 4.893] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 4.167 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.184, 0.520] | 3.923 [2.172, 6.333] | 1.837 [0.947, 3.112] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.615] | 3.846 [2.077, 6.333] | 1.856 [0.935, 3.179] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 4.038 [2.286, 6.500] | 2.019 [1.065, 3.368] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.300, 0.625] | 4.423 [2.528, 7.044] | 2.337 [1.206, 3.977] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 3.308 [1.782, 5.522] | 1.529 [0.771, 2.677] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 5.706 [3.142, 9.468] | 2.485 [1.276, 4.350] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.111 [1.111, 7.750] | 2.556 [0.708, 7.003] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.625] | 4.000 [2.241, 6.556] | 1.856 [0.954, 3.227] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 3.923 [2.122, 6.550] | 1.885 [0.950, 3.284] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 3.154 [1.593, 5.333] | 1.423 [0.692, 2.529] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.625] | 4.077 [2.265, 6.750] | 2.202 [1.081, 3.989] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 3.808 [2.038, 6.467] | 1.952 [0.965, 3.442] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.529 [3.000, 9.235] | 2.353 [1.136, 4.227] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 3.694 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.407, 0.739] | 2.769 [1.812, 4.381] | 2.106 [1.243, 3.609] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 2.269 [1.500, 3.571] | 1.712 [1.033, 2.917] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 2.269 [1.500, 3.584] | 1.692 [1.008, 2.900] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 3.308 [2.205, 5.227] | 2.731 [1.720, 4.588] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.269 [1.459, 3.619] | 1.692 [0.969, 2.965] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.529, 0.882] | 1.294 [0.762, 2.154] | 0.559 [0.287, 1.024] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 12.000 (no interval) | 11.250 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_quantile_skewt_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.750] | 2.346 [1.517, 3.751] | 1.692 [0.963, 2.938] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.166, 0.458] | 1.846 [1.158, 2.900] | 1.260 [0.660, 2.203] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.538 [0.937, 2.375] | 0.981 [0.481, 1.724] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.705, 1.684] | 0.558 [0.276, 0.988] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.176 [0.667, 1.909] | 0.471 [0.224, 0.865] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.889 (no interval) | 5.194 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

risk_quantile_skewt_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.758] | 5.269 [3.541, 7.714] | 2.462 [1.565, 3.767] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 5.038 [3.344, 7.502] | 2.067 [1.304, 3.196] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.679] | 5.077 [3.300, 7.619] | 2.212 [1.387, 3.443] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.643] | 4.577 [2.973, 7.000] | 2.048 [1.267, 3.259] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 5.192 [3.384, 7.800] | 2.308 [1.461, 3.584] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 7.000 [4.500, 10.909] | 2.779 [1.678, 4.625] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.889 (no interval) | 6.028 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.676] | 3.654 [2.550, 5.400] | 1.817 [1.148, 2.967] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 4.115 [2.870, 5.947] | 1.663 [1.143, 2.473] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.227, 0.536] | 3.731 [2.441, 5.706] | 1.788 [1.142, 2.848] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.542] | 3.923 [2.733, 5.778] | 1.913 [1.277, 2.946] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.321, 0.667] | 4.115 [2.742, 6.105] | 1.962 [1.282, 3.044] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [4.083, 9.786] | 2.441 [1.562, 3.834] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.167, 0.714] | 11.444 [7.444, 23.750] | 7.556 [4.481, 17.881] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 4.615 [2.938, 7.067] | 2.240 [1.383, 3.599] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.767, 6.953] | 1.865 [1.080, 3.033] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.077 [3.077, 7.957] | 2.385 [1.327, 4.087] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 4.731 [3.000, 7.223] | 2.250 [1.341, 3.594] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.269 [3.348, 7.875] | 2.385 [1.483, 3.739] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.000 [5.214, 12.500] | 3.559 [2.145, 5.887] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.889 (no interval) | 4.667 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.391, 0.750] | 5.192 [3.417, 7.715] | 2.442 [1.537, 3.868] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.923 [3.205, 7.354] | 2.019 [1.250, 3.163] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.316, 0.677] | 4.885 [3.115, 7.368] | 2.115 [1.288, 3.375] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.423 [2.774, 6.808] | 1.952 [1.156, 3.125] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.316, 0.680] | 5.038 [3.233, 7.525] | 2.192 [1.351, 3.459] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 7.000 [4.498, 10.910] | 2.779 [1.625, 4.700] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.444 (no interval) | 5.167 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.364, 0.714] | 4.885 [3.230, 7.533] | 2.510 [1.579, 4.149] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.320, 0.688] | 5.500 [3.781, 8.167] | 2.394 [1.586, 3.760] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.324, 0.680] | 5.385 [3.595, 8.214] | 2.567 [1.630, 4.066] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.846 [3.150, 7.445] | 2.365 [1.475, 3.870] |
| lead 5 alone (fail) | 26 | 14 | 0.538 [0.375, 0.714] | 5.423 [3.562, 8.200] | 2.625 [1.652, 4.162] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.765 [4.315, 10.847] | 2.706 [1.591, 4.688] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.249, 0.833] | 10.667 [6.818, 21.750] | 7.056 [4.022, 16.189] |

Recall with equal weight per regime: 0.501 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_quantile_skewt_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.688] | 4.692 [2.889, 7.273] | 2.135 [1.200, 3.462] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 4.308 [2.613, 6.667] | 1.721 [0.976, 2.875] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.923 [2.920, 7.682] | 2.260 [1.240, 3.742] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.231 [2.450, 6.824] | 2.125 [1.121, 3.611] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.652] | 4.885 [2.931, 7.685] | 2.356 [1.302, 3.888] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 7.353 [4.750, 11.309] | 2.985 [1.733, 4.950] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 4.000 (no interval) | 3.111 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.154 [2.444, 6.573] | 1.952 [1.080, 3.250] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.846 [2.939, 7.557] | 2.144 [1.188, 3.548] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.231 [2.517, 6.715] | 1.846 [1.075, 3.039] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 4.231 [2.562, 6.697] | 1.942 [1.136, 3.179] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.522] | 3.538 [1.999, 5.810] | 1.663 [0.900, 2.846] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.176 [4.476, 11.438] | 2.971 [1.694, 5.021] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.222 [2.235, 9.500] | 3.028 [1.400, 7.460] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 4.692 [2.893, 7.287] | 2.135 [1.216, 3.552] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.308 [2.514, 6.955] | 2.115 [1.167, 3.590] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.308 [1.783, 5.528] | 1.538 [0.798, 2.706] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.290, 0.636] | 3.615 [2.088, 5.945] | 1.712 [0.973, 2.871] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.296, 0.639] | 3.231 [1.697, 5.410] | 1.462 [0.740, 2.579] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.471 [3.933, 10.563] | 2.676 [1.488, 4.701] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.861 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.633] | 4.154 [2.384, 6.462] | 1.952 [1.067, 3.143] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.300, 0.629] | 3.692 [2.143, 5.824] | 1.663 [0.908, 2.750] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.304, 0.684] | 3.846 [2.130, 6.000] | 1.721 [0.935, 2.817] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.548] | 3.615 [1.833, 6.043] | 1.798 [0.839, 3.137] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.269 [1.667, 5.353] | 1.548 [0.759, 2.621] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.639, 10.183] | 2.618 [1.395, 4.472] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.601] | 3.556 [1.818, 7.505] | 2.389 [0.950, 5.833] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.682] | 4.269 [2.555, 6.591] | 1.846 [1.022, 3.047] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.423 [2.667, 6.913] | 1.760 [0.968, 2.917] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.846 [2.786, 7.683] | 2.221 [1.175, 3.788] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 4.423 [2.600, 7.125] | 2.202 [1.177, 3.833] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 5.115 [3.045, 7.955] | 2.481 [1.380, 4.153] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 7.353 [4.591, 11.572] | 2.985 [1.697, 5.119] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.333 [2.867, 12.000] | 3.722 [1.854, 9.083] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.231 [2.540, 6.480] | 1.971 [1.094, 3.191] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.773, 6.826] | 1.894 [1.091, 2.990] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.231 [2.478, 6.600] | 1.885 [1.043, 3.042] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.462 [2.690, 6.895] | 2.135 [1.250, 3.388] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 3.731 [2.146, 5.913] | 1.788 [0.989, 2.951] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.118 [4.520, 11.100] | 2.912 [1.679, 4.792] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.000 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 4.269 [2.718, 6.601] | 1.846 [1.091, 3.011] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 4.308 [2.577, 6.920] | 2.144 [1.236, 3.542] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 3.462 [2.000, 5.667] | 1.654 [0.885, 2.778] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.625] | 3.577 [2.100, 5.847] | 1.721 [1.018, 2.880] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.565] | 3.077 [1.591, 5.279] | 1.365 [0.667, 2.408] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 6.471 [4.048, 10.444] | 2.676 [1.525, 4.715] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.000 (no interval) | 2.639 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.645] | 4.231 [2.521, 6.612] | 1.971 [1.107, 3.211] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 3.654 [2.071, 5.895] | 1.654 [0.913, 2.739] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.364, 0.714] | 4.000 [2.289, 6.334] | 1.837 [1.053, 3.014] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.257, 0.600] | 4.115 [2.310, 6.700] | 2.183 [1.193, 3.649] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.385 [1.785, 5.576] | 1.615 [0.840, 2.751] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.615, 10.385] | 2.618 [1.432, 4.590] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 4.769 [3.000, 7.368] | 2.144 [1.239, 3.500] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.550] | 4.500 [2.815, 6.957] | 1.808 [1.076, 2.892] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.654 [2.792, 7.334] | 2.154 [1.163, 3.631] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.583] | 4.346 [2.600, 6.801] | 2.125 [1.164, 3.561] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.636] | 4.923 [3.031, 7.667] | 2.356 [1.338, 3.903] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.353 [4.667, 11.500] | 3.029 [1.764, 5.017] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.778 [2.417, 11.000] | 3.222 [1.484, 8.056] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.281, 0.630] | 4.385 [2.580, 6.731] | 2.010 [1.088, 3.222] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.885 [2.920, 7.501] | 2.183 [1.196, 3.547] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.572] | 3.923 [2.193, 6.214] | 1.721 [0.914, 2.781] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.586] | 4.269 [2.466, 6.514] | 1.923 [1.068, 3.055] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 3.423 [1.786, 5.501] | 1.654 [0.830, 2.750] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.235 [4.688, 11.167] | 3.029 [1.768, 4.951] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.444 [2.214, 9.603] | 2.889 [1.312, 6.786] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.312, 0.680] | 4.769 [2.892, 7.264] | 2.144 [1.191, 3.501] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.320, 0.679] | 4.385 [2.562, 6.897] | 2.135 [1.175, 3.544] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.606] | 3.808 [2.000, 6.218] | 1.904 [0.921, 3.265] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.285, 0.630] | 3.500 [2.000, 5.581] | 1.625 [0.891, 2.713] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 3.115 [1.607, 5.112] | 1.375 [0.660, 2.375] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 0.960] | 6.412 [3.818, 10.401] | 2.662 [1.427, 4.594] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.111 (no interval) | 2.528 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.385 [2.636, 6.751] | 2.010 [1.133, 3.185] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 3.769 [2.120, 5.917] | 1.683 [0.902, 2.731] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.312, 0.692] | 4.115 [2.363, 6.465] | 1.856 [1.027, 2.982] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 3.731 [1.967, 6.091] | 1.827 [0.886, 3.102] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 3.385 [1.815, 5.526] | 1.606 [0.808, 2.712] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.529 [3.833, 10.308] | 2.706 [1.500, 4.451] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.688] | 4.115 [2.423, 6.410] | 1.827 [1.016, 2.963] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.308 [2.556, 6.704] | 1.760 [1.000, 2.859] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.769 [2.724, 7.667] | 2.288 [1.198, 3.902] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.462 [2.499, 7.351] | 2.356 [1.162, 4.120] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.846 [2.799, 7.700] | 2.317 [1.217, 3.977] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.353 [4.619, 11.917] | 3.029 [1.711, 5.271] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 3.778 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.192 [2.516, 6.526] | 2.019 [1.150, 3.293] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 5.038 [3.083, 7.619] | 2.394 [1.392, 3.824] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.000 [2.290, 6.407] | 1.817 [1.023, 2.964] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.579] | 5.000 [3.031, 7.864] | 2.750 [1.534, 4.700] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 4.000 [2.214, 6.410] | 2.096 [1.073, 3.588] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 7.235 [4.609, 11.364] | 3.029 [1.812, 4.929] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 5.889 [2.554, 16.000] | 5.222 [1.982, 14.875] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.682] | 4.115 [2.470, 6.334] | 1.827 [1.030, 2.974] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 4.154 [2.333, 6.558] | 2.067 [1.134, 3.412] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 3.962 [2.190, 6.350] | 2.029 [1.067, 3.469] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.630] | 3.692 [2.081, 5.895] | 1.933 [1.062, 3.250] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.115 [1.512, 5.133] | 1.375 [0.661, 2.355] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.412 [3.772, 10.429] | 2.662 [1.458, 4.688] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.778 [1.599, 9.333] | 3.139 [1.091, 8.418] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.637] | 4.192 [2.454, 6.709] | 2.019 [1.131, 3.420] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 4.115 [2.333, 6.715] | 2.000 [1.092, 3.421] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.357, 0.714] | 4.231 [2.538, 6.700] | 1.962 [1.160, 3.266] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.346 [2.351, 7.462] | 2.500 [1.223, 4.668] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.257, 0.600] | 3.192 [1.645, 5.385] | 1.500 [0.759, 2.675] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.529 [4.000, 10.771] | 2.706 [1.535, 4.750] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.889 (no interval) | 4.333 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+every_day | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.66 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm+every_day+gate | 0.57 (102) | 0.25 (4) | – | 0.20 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.59 (102) | 0.50 (4) | – | 0.00 (5) | 0.69 (29) | 0.82 (17) | 0.54 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+persist | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.76 (17) | 0.62 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+every_day+scarce | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.66 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm+every_day+shrunk | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.63 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+hurdle_isotonic | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_isotonic+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_isotonic+settle | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_isotonic+settle+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.76 (17) | 0.60 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt+settle | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.76 (17) | 0.60 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt+settle+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_isotonic | 0.72 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_isotonic+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.59 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_isotonic+settle | 0.72 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.59 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_platt | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.59 (101) | 0.67 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_platt+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.59 (101) | 0.56 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_platt+settle | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.59 (101) | 0.67 (9) | 0.54 (13) |
| risk_gbm+hurdle_state_platt+settle+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.59 (101) | 0.56 (9) | 0.54 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base+every_day | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.67 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+gate | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.53 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+persist | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.52 (29) | 0.76 (17) | 0.66 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+scarce | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.67 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+shrunk | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.64 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.76 (17) | 0.58 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.76 (17) | 0.58 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.61 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.76 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.61 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.76 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.62 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.62 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.62 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.62 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.62 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.62 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.77 (13) |
| risk_logistic+every_day | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.66 (29) | 0.71 (17) | 0.60 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+gate | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.69 (29) | 0.82 (17) | 0.54 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+persist | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.52 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+scarce | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.66 (29) | 0.71 (17) | 0.60 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+shrunk | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.67 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_isotonic | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.53 (17) | 0.51 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_isotonic+h41 | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.59 (17) | 0.65 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_isotonic+settle | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.53 (17) | 0.51 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_isotonic+settle+h41 | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.59 (17) | 0.65 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.53 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_platt+h41 | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.67 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_platt+settle | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.53 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_platt+settle+h41 | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.67 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_state_isotonic | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.53 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+h41 | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.59 (17) | 0.55 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+settle | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.53 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.59 (17) | 0.55 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_platt | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.54 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_state_platt+h41 | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.57 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_state_platt+settle | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.54 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_state_platt+settle+h41 | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.57 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |
| risk_logistic_base+every_day | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.66 (29) | 0.65 (17) | 0.55 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+every_day+gate | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.76 (29) | 0.88 (17) | 0.56 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+persist | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.65 (17) | 0.52 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+every_day+scarce | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.66 (29) | 0.65 (17) | 0.55 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+every_day+shrunk | 0.79 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.88 (17) | 0.69 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_isotonic | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.53 (17) | 0.47 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_isotonic+h41 | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_isotonic+settle | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.53 (17) | 0.47 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.59 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+h41 | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.76 (17) | 0.52 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_platt+settle | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.59 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+settle+h41 | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.76 (17) | 0.52 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_state_isotonic | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.53 (17) | 0.46 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.53 (17) | 0.46 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt | 0.58 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.47 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt+h41 | 0.68 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.52 (101) | 0.78 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_state_platt+settle | 0.58 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.47 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 0.68 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.52 (101) | 0.78 (9) | 0.69 (13) |
| risk_quantile_skewt | 0.31 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.92 (13) |
| risk_quantile_skewt_base | 0.29 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.77 (13) |
| risk_quantile_skewt_base+every_day | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.76 (17) | 0.63 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+gate | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.69 (29) | 0.88 (17) | 0.53 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+persist | 0.68 (102) | 0.25 (4) | – | 0.20 (5) | 0.52 (29) | 0.71 (17) | 0.58 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+scarce | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.76 (17) | 0.63 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+shrunk | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.53 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+hurdle_isotonic | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.56 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.56 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.58 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.51 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.58 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.51 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.61 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.52 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.61 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.52 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.60 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.60 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 0.65 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.50 (101) | 0.67 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0173 [-0.0006, +0.0406] | +0.0545 [+0.0304, +0.0791] | +0.0049 [-0.0002, +0.0099] | +0.1280 [+0.0435, +0.2143] | +0.0685 [+0.0410, +0.0950] |
| risk_gbm+every_day | +0.0573 [+0.0304, +0.0862] | +0.0233 [+0.0097, +0.0348] | +0.0131 [+0.0114, +0.0151] | +0.0006 [-0.0060, +0.0056] | +0.0293 [+0.0021, +0.0606] | +0.0597 [+0.0358, +0.0874] | +0.0160 [+0.0093, +0.0240] | +0.1280 [+0.0510, +0.2060] | +0.0685 [+0.0421, +0.0961] |
| risk_gbm+every_day+gate | +0.0417 [+0.0143, +0.0703] | +0.0323 [+0.0157, +0.0454] | +0.0136 [+0.0118, +0.0155] | +0.0007 [-0.0068, +0.0057] | +0.0284 [+0.0031, +0.0604] | +0.0602 [+0.0346, +0.0877] | +0.0138 [+0.0076, +0.0208] | +0.1280 [+0.0438, +0.2071] | +0.0685 [+0.0418, +0.0955] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0310 [+0.0152, +0.0451] | +0.0135 [+0.0117, +0.0155] | -0.0013 [-0.0085, +0.0043] | +0.0279 [+0.0027, +0.0580] | +0.0579 [+0.0340, +0.0836] | +0.0134 [+0.0067, +0.0199] | +0.1309 [+0.0507, +0.2140] | +0.0683 [+0.0392, +0.0981] |
| risk_gbm+every_day+gate+settle+h41+iorb | +0.0442 [+0.0158, +0.0733] | +0.0350 [+0.0212, +0.0466] | +0.0136 [+0.0118, +0.0154] | -0.0056 [-0.0171, +0.0035] | +0.0258 [+0.0024, +0.0550] | +0.0579 [+0.0339, +0.0839] | +0.0135 [+0.0073, +0.0208] | +0.1309 [+0.0525, +0.2116] | +0.0683 [+0.0375, +0.0976] |
| risk_gbm+every_day+persist | +0.0498 [+0.0240, +0.0771] | +0.0291 [+0.0201, +0.0387] | +0.0133 [+0.0116, +0.0150] | +0.0027 [-0.0017, +0.0060] | +0.0283 [+0.0050, +0.0582] | +0.0588 [+0.0341, +0.0842] | +0.0154 [+0.0094, +0.0222] | +0.1280 [+0.0488, +0.2053] | +0.0685 [+0.0420, +0.0959] |
| risk_gbm+every_day+scarce | +0.0573 [+0.0292, +0.0859] | +0.0233 [+0.0105, +0.0359] | +0.0135 [+0.0118, +0.0154] | +0.0037 [-0.0003, +0.0066] | +0.0318 [+0.0046, +0.0646] | +0.0598 [+0.0356, +0.0871] | +0.0170 [+0.0102, +0.0242] | +0.1280 [+0.0472, +0.2084] | +0.0685 [+0.0413, +0.0938] |
| risk_gbm+every_day+shrunk | +0.0429 [+0.0257, +0.0603] | +0.0366 [+0.0281, +0.0449] | +0.0136 [+0.0118, +0.0155] | +0.0030 [-0.0012, +0.0062] | +0.0299 [+0.0055, +0.0612] | +0.0575 [+0.0328, +0.0848] | +0.0156 [+0.0111, +0.0202] | +0.1280 [+0.0496, +0.2077] | +0.0685 [+0.0414, +0.0970] |
| risk_gbm+hurdle_isotonic | +0.0131 [-0.0304, +0.0570] | -0.0040 [-0.0240, +0.0127] | +0.0120 [+0.0107, +0.0135] | +0.0025 [-0.0025, +0.0064] | +0.0286 [+0.0036, +0.0581] | +0.0570 [+0.0317, +0.0837] | +0.0012 [-0.0092, +0.0114] | +0.1280 [+0.0503, +0.2063] | +0.0685 [+0.0410, +0.0947] |
| risk_gbm+hurdle_isotonic+h41 | +0.0133 [-0.0301, +0.0543] | -0.0054 [-0.0268, +0.0126] | +0.0119 [+0.0105, +0.0134] | +0.0005 [-0.0055, +0.0050] | +0.0281 [+0.0054, +0.0560] | +0.0547 [+0.0325, +0.0782] | +0.0008 [-0.0095, +0.0108] | +0.1309 [+0.0470, +0.2071] | +0.0683 [+0.0387, +0.0976] |
| risk_gbm+hurdle_isotonic+settle | +0.0131 [-0.0284, +0.0549] | -0.0040 [-0.0226, +0.0126] | +0.0120 [+0.0105, +0.0134] | +0.0025 [-0.0025, +0.0064] | +0.0286 [+0.0048, +0.0604] | +0.0570 [+0.0330, +0.0845] | +0.0012 [-0.0087, +0.0115] | +0.1280 [+0.0471, +0.2088] | +0.0685 [+0.0416, +0.0956] |
| risk_gbm+hurdle_isotonic+settle+h41 | +0.0133 [-0.0292, +0.0558] | -0.0054 [-0.0262, +0.0109] | +0.0119 [+0.0105, +0.0134] | +0.0005 [-0.0050, +0.0050] | +0.0281 [+0.0049, +0.0583] | +0.0547 [+0.0307, +0.0797] | +0.0008 [-0.0095, +0.0112] | +0.1309 [+0.0496, +0.2096] | +0.0683 [+0.0387, +0.0979] |
| risk_gbm+hurdle_platt | +0.0391 [+0.0075, +0.0714] | -0.0020 [-0.0137, +0.0099] | +0.0103 [+0.0086, +0.0119] | +0.0026 [-0.0022, +0.0065] | +0.0265 [+0.0030, +0.0554] | +0.0563 [+0.0319, +0.0831] | +0.0066 [-0.0009, +0.0146] | +0.1280 [+0.0462, +0.2080] | +0.0685 [+0.0402, +0.0966] |
| risk_gbm+hurdle_platt+h41 | +0.0393 [+0.0063, +0.0741] | -0.0034 [-0.0161, +0.0083] | +0.0103 [+0.0087, +0.0119] | +0.0005 [-0.0052, +0.0051] | +0.0259 [+0.0045, +0.0515] | +0.0540 [+0.0316, +0.0791] | +0.0062 [-0.0014, +0.0143] | +0.1309 [+0.0518, +0.2102] | +0.0683 [+0.0379, +0.0976] |
| risk_gbm+hurdle_platt+settle | +0.0391 [+0.0085, +0.0728] | -0.0020 [-0.0133, +0.0092] | +0.0103 [+0.0087, +0.0118] | +0.0026 [-0.0025, +0.0066] | +0.0265 [+0.0041, +0.0552] | +0.0563 [+0.0325, +0.0810] | +0.0066 [-0.0006, +0.0148] | +0.1280 [+0.0469, +0.2050] | +0.0685 [+0.0412, +0.0968] |
| risk_gbm+hurdle_platt+settle+h41 | +0.0393 [+0.0072, +0.0745] | -0.0034 [-0.0161, +0.0077] | +0.0103 [+0.0086, +0.0118] | +0.0005 [-0.0054, +0.0050] | +0.0259 [+0.0048, +0.0531] | +0.0540 [+0.0323, +0.0775] | +0.0062 [-0.0012, +0.0144] | +0.1309 [+0.0513, +0.2113] | +0.0683 [+0.0387, +0.0972] |
| risk_gbm+hurdle_state_isotonic | +0.0169 [-0.0246, +0.0564] | +0.0174 [-0.0067, +0.0366] | +0.0138 [+0.0121, +0.0157] | +0.0037 [-0.0000, +0.0067] | +0.0277 [+0.0050, +0.0578] | +0.0577 [+0.0326, +0.0840] | +0.0063 [-0.0035, +0.0156] | +0.1280 [+0.0490, +0.2079] | +0.0685 [+0.0410, +0.0955] |
| risk_gbm+hurdle_state_isotonic+h41 | +0.0153 [-0.0252, +0.0560] | +0.0156 [-0.0099, +0.0360] | +0.0137 [+0.0120, +0.0156] | +0.0016 [-0.0034, +0.0054] | +0.0273 [+0.0067, +0.0557] | +0.0558 [+0.0329, +0.0823] | +0.0054 [-0.0048, +0.0149] | +0.1309 [+0.0542, +0.2064] | +0.0683 [+0.0383, +0.0976] |
| risk_gbm+hurdle_state_isotonic+settle | +0.0169 [-0.0237, +0.0566] | +0.0174 [-0.0071, +0.0375] | +0.0138 [+0.0120, +0.0157] | +0.0037 [-0.0003, +0.0067] | +0.0277 [+0.0047, +0.0555] | +0.0577 [+0.0329, +0.0831] | +0.0063 [-0.0039, +0.0154] | +0.1280 [+0.0483, +0.2074] | +0.0685 [+0.0427, +0.0968] |
| risk_gbm+hurdle_state_isotonic+settle+h41 | +0.0153 [-0.0263, +0.0564] | +0.0156 [-0.0107, +0.0359] | +0.0137 [+0.0119, +0.0156] | +0.0016 [-0.0033, +0.0052] | +0.0273 [+0.0054, +0.0563] | +0.0558 [+0.0323, +0.0818] | +0.0054 [-0.0047, +0.0153] | +0.1309 [+0.0543, +0.2097] | +0.0683 [+0.0390, +0.0977] |
| risk_gbm+hurdle_state_platt | +0.0457 [+0.0147, +0.0775] | +0.0209 [+0.0043, +0.0353] | +0.0134 [+0.0118, +0.0152] | +0.0037 [-0.0000, +0.0068] | +0.0300 [+0.0055, +0.0612] | +0.0584 [+0.0347, +0.0842] | +0.0137 [+0.0063, +0.0213] | +0.1280 [+0.0485, +0.2109] | +0.0685 [+0.0409, +0.0981] |
| risk_gbm+hurdle_state_platt+h41 | +0.0447 [+0.0131, +0.0776] | +0.0193 [+0.0030, +0.0347] | +0.0134 [+0.0117, +0.0152] | +0.0016 [-0.0030, +0.0053] | +0.0296 [+0.0063, +0.0590] | +0.0561 [+0.0322, +0.0814] | +0.0130 [+0.0058, +0.0216] | +0.1309 [+0.0526, +0.2114] | +0.0683 [+0.0373, +0.0988] |
| risk_gbm+hurdle_state_platt+settle | +0.0457 [+0.0136, +0.0778] | +0.0209 [+0.0043, +0.0354] | +0.0134 [+0.0118, +0.0151] | +0.0037 [-0.0002, +0.0067] | +0.0300 [+0.0052, +0.0623] | +0.0584 [+0.0337, +0.0833] | +0.0137 [+0.0064, +0.0215] | +0.1280 [+0.0491, +0.2110] | +0.0685 [+0.0424, +0.0948] |
| risk_gbm+hurdle_state_platt+settle+h41 | +0.0447 [+0.0133, +0.0778] | +0.0193 [+0.0024, +0.0338] | +0.0134 [+0.0117, +0.0151] | +0.0016 [-0.0031, +0.0053] | +0.0296 [+0.0065, +0.0605] | +0.0561 [+0.0309, +0.0812] | +0.0130 [+0.0055, +0.0211] | +0.1309 [+0.0542, +0.2103] | +0.0683 [+0.0380, +0.0994] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0137 [+0.0119, +0.0155] | +0.0016 [-0.0030, +0.0054] | +0.0168 [+0.0005, +0.0385] | +0.0522 [+0.0290, +0.0759] | +0.0045 [-0.0005, +0.0095] | +0.1309 [+0.0527, +0.2129] | +0.0683 [+0.0393, +0.0972] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0335 [+0.0228, +0.0443] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0199 [+0.0032, +0.0405] | +0.0379 [+0.0140, +0.0624] | +0.0054 [+0.0003, +0.0099] | +0.1126 [+0.0332, +0.1946] | +0.0706 [+0.0489, +0.0946] |
| risk_gbm_base+every_day | +0.0542 [+0.0257, +0.0845] | +0.0173 [+0.0016, +0.0307] | +0.0132 [+0.0114, +0.0151] | +0.0008 [-0.0060, +0.0057] | +0.0318 [+0.0048, +0.0663] | +0.0430 [+0.0192, +0.0694] | +0.0165 [+0.0094, +0.0245] | +0.1126 [+0.0371, +0.1936] | +0.0706 [+0.0492, +0.0951] |
| risk_gbm_base+every_day+gate | +0.0386 [+0.0127, +0.0658] | +0.0263 [+0.0081, +0.0404] | +0.0136 [+0.0118, +0.0155] | +0.0009 [-0.0065, +0.0059] | +0.0310 [+0.0055, +0.0607] | +0.0436 [+0.0174, +0.0694] | +0.0143 [+0.0078, +0.0210] | +0.1126 [+0.0341, +0.1908] | +0.0706 [+0.0492, +0.0952] |
| risk_gbm_base+every_day+persist | +0.0484 [+0.0229, +0.0773] | +0.0229 [+0.0100, +0.0348] | +0.0133 [+0.0116, +0.0152] | +0.0029 [-0.0014, +0.0062] | +0.0320 [+0.0078, +0.0614] | +0.0422 [+0.0179, +0.0686] | +0.0165 [+0.0103, +0.0237] | +0.1126 [+0.0372, +0.1918] | +0.0706 [+0.0489, +0.0935] |
| risk_gbm_base+every_day+scarce | +0.0542 [+0.0277, +0.0836] | +0.0173 [+0.0018, +0.0320] | +0.0136 [+0.0119, +0.0154] | +0.0038 [-0.0002, +0.0069] | +0.0343 [+0.0077, +0.0644] | +0.0431 [+0.0173, +0.0690] | +0.0175 [+0.0106, +0.0249] | +0.1126 [+0.0335, +0.1904] | +0.0706 [+0.0492, +0.0931] |
| risk_gbm_base+every_day+shrunk | +0.0397 [+0.0236, +0.0565] | +0.0305 [+0.0195, +0.0408] | +0.0137 [+0.0119, +0.0156] | +0.0032 [-0.0013, +0.0065] | +0.0324 [+0.0085, +0.0609] | +0.0408 [+0.0165, +0.0652] | +0.0161 [+0.0117, +0.0208] | +0.1126 [+0.0374, +0.1919] | +0.0706 [+0.0483, +0.0935] |
| risk_gbm_base+hurdle_isotonic | +0.0099 [-0.0341, +0.0495] | -0.0101 [-0.0343, +0.0089] | +0.0120 [+0.0106, +0.0135] | +0.0027 [-0.0027, +0.0066] | +0.0312 [+0.0072, +0.0606] | +0.0404 [+0.0156, +0.0675] | +0.0017 [-0.0087, +0.0113] | +0.1126 [+0.0339, +0.1905] | +0.0706 [+0.0492, +0.0923] |
| risk_gbm_base+hurdle_isotonic+h41 | +0.0093 [-0.0342, +0.0504] | -0.0092 [-0.0323, +0.0093] | +0.0120 [+0.0106, +0.0135] | -0.0001 [-0.0066, +0.0051] | +0.0318 [+0.0097, +0.0597] | +0.0435 [+0.0219, +0.0664] | +0.0011 [-0.0098, +0.0114] | +0.1129 [+0.0365, +0.1928] | +0.0711 [+0.0475, +0.0943] |
| risk_gbm_base+hurdle_isotonic+settle | +0.0099 [-0.0329, +0.0526] | -0.0101 [-0.0344, +0.0092] | +0.0120 [+0.0106, +0.0135] | +0.0027 [-0.0021, +0.0067] | +0.0312 [+0.0066, +0.0611] | +0.0404 [+0.0156, +0.0658] | +0.0017 [-0.0088, +0.0114] | +0.1126 [+0.0359, +0.1919] | +0.0706 [+0.0483, +0.0945] |
| risk_gbm_base+hurdle_isotonic+settle+h41 | +0.0093 [-0.0343, +0.0511] | -0.0092 [-0.0313, +0.0102] | +0.0120 [+0.0105, +0.0136] | -0.0001 [-0.0062, +0.0050] | +0.0318 [+0.0096, +0.0601] | +0.0435 [+0.0210, +0.0666] | +0.0011 [-0.0096, +0.0114] | +0.1129 [+0.0325, +0.1916] | +0.0711 [+0.0475, +0.0970] |
| risk_gbm_base+hurdle_platt | +0.0360 [+0.0036, +0.0687] | -0.0081 [-0.0241, +0.0060] | +0.0104 [+0.0088, +0.0120] | +0.0027 [-0.0030, +0.0065] | +0.0290 [+0.0078, +0.0550] | +0.0396 [+0.0167, +0.0640] | +0.0071 [-0.0005, +0.0153] | +0.1126 [+0.0356, +0.1888] | +0.0706 [+0.0484, +0.0944] |
| risk_gbm_base+hurdle_platt+h41 | +0.0353 [+0.0025, +0.0716] | -0.0072 [-0.0222, +0.0072] | +0.0104 [+0.0087, +0.0119] | -0.0000 [-0.0064, +0.0050] | +0.0297 [+0.0090, +0.0552] | +0.0427 [+0.0224, +0.0653] | +0.0065 [-0.0011, +0.0153] | +0.1129 [+0.0307, +0.1935] | +0.0711 [+0.0475, +0.0966] |
| risk_gbm_base+hurdle_platt+settle | +0.0360 [+0.0036, +0.0706] | -0.0081 [-0.0243, +0.0055] | +0.0104 [+0.0088, +0.0119] | +0.0027 [-0.0022, +0.0067] | +0.0290 [+0.0070, +0.0552] | +0.0396 [+0.0164, +0.0653] | +0.0071 [-0.0006, +0.0155] | +0.1126 [+0.0339, +0.1887] | +0.0706 [+0.0478, +0.0937] |
| risk_gbm_base+hurdle_platt+settle+h41 | +0.0353 [+0.0035, +0.0676] | -0.0072 [-0.0222, +0.0062] | +0.0104 [+0.0088, +0.0119] | -0.0000 [-0.0062, +0.0050] | +0.0297 [+0.0093, +0.0557] | +0.0427 [+0.0207, +0.0658] | +0.0065 [-0.0010, +0.0148] | +0.1129 [+0.0329, +0.1885] | +0.0711 [+0.0481, +0.0952] |
| risk_gbm_base+hurdle_state_isotonic | +0.0138 [-0.0278, +0.0533] | +0.0113 [-0.0168, +0.0345] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0002, +0.0070] | +0.0302 [+0.0088, +0.0588] | +0.0411 [+0.0185, +0.0658] | +0.0068 [-0.0033, +0.0166] | +0.1126 [+0.0383, +0.1920] | +0.0706 [+0.0481, +0.0937] |
| risk_gbm_base+hurdle_state_isotonic+h41 | +0.0113 [-0.0310, +0.0525] | +0.0118 [-0.0144, +0.0351] | +0.0138 [+0.0121, +0.0157] | +0.0011 [-0.0041, +0.0053] | +0.0311 [+0.0100, +0.0572] | +0.0446 [+0.0230, +0.0701] | +0.0056 [-0.0046, +0.0156] | +0.1129 [+0.0331, +0.1941] | +0.0711 [+0.0477, +0.0955] |
| risk_gbm_base+hurdle_state_isotonic+settle | +0.0138 [-0.0264, +0.0547] | +0.0113 [-0.0177, +0.0349] | +0.0138 [+0.0121, +0.0158] | +0.0038 [+0.0000, +0.0070] | +0.0302 [+0.0089, +0.0569] | +0.0411 [+0.0176, +0.0659] | +0.0068 [-0.0030, +0.0163] | +0.1126 [+0.0335, +0.1895] | +0.0706 [+0.0493, +0.0935] |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | +0.0113 [-0.0297, +0.0504] | +0.0118 [-0.0167, +0.0348] | +0.0138 [+0.0120, +0.0157] | +0.0011 [-0.0043, +0.0053] | +0.0311 [+0.0103, +0.0572] | +0.0446 [+0.0225, +0.0699] | +0.0056 [-0.0047, +0.0155] | +0.1129 [+0.0355, +0.1932] | +0.0711 [+0.0488, +0.0956] |
| risk_gbm_base+hurdle_state_platt | +0.0425 [+0.0112, +0.0777] | +0.0148 [-0.0056, +0.0328] | +0.0135 [+0.0118, +0.0154] | +0.0038 [+0.0003, +0.0068] | +0.0325 [+0.0094, +0.0629] | +0.0418 [+0.0186, +0.0685] | +0.0142 [+0.0067, +0.0227] | +0.1126 [+0.0390, +0.1911] | +0.0706 [+0.0478, +0.0949] |
| risk_gbm_base+hurdle_state_platt+h41 | +0.0407 [+0.0093, +0.0725] | +0.0155 [-0.0048, +0.0334] | +0.0135 [+0.0118, +0.0152] | +0.0011 [-0.0042, +0.0054] | +0.0333 [+0.0106, +0.0610] | +0.0449 [+0.0232, +0.0695] | +0.0132 [+0.0059, +0.0213] | +0.1129 [+0.0320, +0.1895] | +0.0711 [+0.0481, +0.0958] |
| risk_gbm_base+hurdle_state_platt+settle | +0.0425 [+0.0109, +0.0762] | +0.0148 [-0.0050, +0.0317] | +0.0135 [+0.0118, +0.0153] | +0.0038 [+0.0001, +0.0071] | +0.0325 [+0.0098, +0.0625] | +0.0418 [+0.0172, +0.0681] | +0.0142 [+0.0068, +0.0228] | +0.1126 [+0.0328, +0.1876] | +0.0706 [+0.0483, +0.0931] |
| risk_gbm_base+hurdle_state_platt+settle+h41 | +0.0407 [+0.0091, +0.0712] | +0.0155 [-0.0040, +0.0334] | +0.0135 [+0.0118, +0.0153] | +0.0011 [-0.0050, +0.0054] | +0.0333 [+0.0108, +0.0615] | +0.0449 [+0.0227, +0.0693] | +0.0132 [+0.0058, +0.0211] | +0.1129 [+0.0286, +0.1963] | +0.0711 [+0.0478, +0.0962] |
| risk_logistic | -0.0038 [-0.0245, +0.0163] | +0.0266 [+0.0104, +0.0402] | +0.0138 [+0.0120, +0.0157] | +0.0049 [+0.0006, +0.0095] | +0.0183 [+0.0033, +0.0374] | +0.0284 [+0.0008, +0.0576] | +0.0043 [-0.0009, +0.0090] | +0.1030 [+0.0321, +0.1692] | +0.0798 [+0.0478, +0.1161] |
| risk_logistic+every_day | +0.0519 [+0.0244, +0.0802] | +0.0103 [-0.0136, +0.0275] | +0.0132 [+0.0114, +0.0151] | +0.0019 [-0.0051, +0.0080] | +0.0303 [+0.0036, +0.0614] | +0.0335 [+0.0050, +0.0634] | +0.0153 [+0.0084, +0.0225] | +0.1030 [+0.0288, +0.1764] | +0.0798 [+0.0482, +0.1158] |
| risk_logistic+every_day+gate | +0.0363 [+0.0110, +0.0633] | +0.0193 [-0.0051, +0.0387] | +0.0136 [+0.0119, +0.0156] | +0.0020 [-0.0056, +0.0083] | +0.0294 [+0.0050, +0.0613] | +0.0340 [+0.0044, +0.0651] | +0.0131 [+0.0069, +0.0202] | +0.1030 [+0.0283, +0.1744] | +0.0798 [+0.0501, +0.1180] |
| risk_logistic+every_day+persist | +0.0463 [+0.0212, +0.0731] | +0.0160 [-0.0038, +0.0306] | +0.0133 [+0.0115, +0.0152] | +0.0041 [-0.0004, +0.0087] | +0.0299 [+0.0064, +0.0589] | +0.0326 [+0.0030, +0.0610] | +0.0153 [+0.0092, +0.0221] | +0.1030 [+0.0303, +0.1713] | +0.0798 [+0.0477, +0.1164] |
| risk_logistic+every_day+scarce | +0.0519 [+0.0251, +0.0810] | +0.0103 [-0.0121, +0.0280] | +0.0136 [+0.0119, +0.0155] | +0.0049 [+0.0006, +0.0091] | +0.0327 [+0.0063, +0.0644] | +0.0336 [+0.0051, +0.0659] | +0.0164 [+0.0097, +0.0239] | +0.1030 [+0.0305, +0.1698] | +0.0798 [+0.0490, +0.1171] |
| risk_logistic+every_day+shrunk | +0.0375 [+0.0206, +0.0547] | +0.0235 [+0.0056, +0.0375] | +0.0137 [+0.0119, +0.0156] | +0.0043 [-0.0005, +0.0090] | +0.0309 [+0.0077, +0.0603] | +0.0313 [+0.0035, +0.0611] | +0.0149 [+0.0107, +0.0195] | +0.1030 [+0.0272, +0.1714] | +0.0798 [+0.0487, +0.1176] |
| risk_logistic+hurdle_isotonic | +0.0077 [-0.0373, +0.0503] | -0.0171 [-0.0410, +0.0042] | +0.0120 [+0.0106, +0.0136] | +0.0038 [-0.0017, +0.0089] | +0.0296 [+0.0061, +0.0580] | +0.0309 [+0.0033, +0.0610] | +0.0006 [-0.0096, +0.0107] | +0.1030 [+0.0319, +0.1731] | +0.0798 [+0.0493, +0.1168] |
| risk_logistic+hurdle_isotonic+h41 | +0.0083 [-0.0374, +0.0521] | -0.0171 [-0.0421, +0.0044] | +0.0120 [+0.0106, +0.0136] | +0.0038 [-0.0014, +0.0092] | +0.0291 [+0.0061, +0.0562] | +0.0317 [+0.0021, +0.0620] | +0.0007 [-0.0099, +0.0107] | +0.1049 [+0.0330, +0.1761] | +0.0774 [+0.0446, +0.1173] |
| risk_logistic+hurdle_isotonic+settle | +0.0077 [-0.0387, +0.0504] | -0.0171 [-0.0424, +0.0041] | +0.0120 [+0.0107, +0.0135] | +0.0038 [-0.0019, +0.0089] | +0.0296 [+0.0061, +0.0595] | +0.0309 [+0.0025, +0.0617] | +0.0006 [-0.0105, +0.0100] | +0.1030 [+0.0291, +0.1744] | +0.0798 [+0.0483, +0.1183] |
| risk_logistic+hurdle_isotonic+settle+h41 | +0.0083 [-0.0344, +0.0524] | -0.0171 [-0.0419, +0.0042] | +0.0120 [+0.0106, +0.0135] | +0.0038 [-0.0017, +0.0088] | +0.0291 [+0.0060, +0.0568] | +0.0317 [+0.0025, +0.0617] | +0.0007 [-0.0092, +0.0110] | +0.1049 [+0.0318, +0.1744] | +0.0774 [+0.0436, +0.1153] |
| risk_logistic+hurdle_platt | +0.0337 [+0.0011, +0.0689] | -0.0150 [-0.0358, +0.0017] | +0.0104 [+0.0089, +0.0119] | +0.0038 [-0.0017, +0.0091] | +0.0275 [+0.0065, +0.0547] | +0.0301 [+0.0016, +0.0583] | +0.0060 [-0.0012, +0.0144] | +0.1030 [+0.0303, +0.1752] | +0.0798 [+0.0478, +0.1178] |
| risk_logistic+hurdle_platt+h41 | +0.0343 [+0.0014, +0.0700] | -0.0150 [-0.0373, +0.0023] | +0.0104 [+0.0088, +0.0119] | +0.0039 [-0.0016, +0.0088] | +0.0269 [+0.0062, +0.0515] | +0.0309 [+0.0029, +0.0603] | +0.0061 [-0.0015, +0.0144] | +0.1049 [+0.0345, +0.1698] | +0.0774 [+0.0452, +0.1168] |
| risk_logistic+hurdle_platt+settle | +0.0337 [+0.0025, +0.0666] | -0.0150 [-0.0345, +0.0020] | +0.0104 [+0.0088, +0.0119] | +0.0038 [-0.0016, +0.0088] | +0.0275 [+0.0061, +0.0541] | +0.0301 [+0.0021, +0.0589] | +0.0060 [-0.0011, +0.0141] | +0.1030 [+0.0314, +0.1735] | +0.0798 [+0.0495, +0.1160] |
| risk_logistic+hurdle_platt+settle+h41 | +0.0343 [+0.0003, +0.0670] | -0.0150 [-0.0355, +0.0019] | +0.0104 [+0.0088, +0.0119] | +0.0039 [-0.0017, +0.0091] | +0.0269 [+0.0062, +0.0510] | +0.0309 [+0.0031, +0.0602] | +0.0061 [-0.0015, +0.0142] | +0.1049 [+0.0307, +0.1769] | +0.0774 [+0.0445, +0.1144] |
| risk_logistic+hurdle_state_isotonic | +0.0115 [-0.0306, +0.0550] | +0.0043 [-0.0257, +0.0296] | +0.0138 [+0.0121, +0.0157] | +0.0049 [+0.0004, +0.0094] | +0.0286 [+0.0068, +0.0559] | +0.0315 [+0.0031, +0.0597] | +0.0057 [-0.0036, +0.0153] | +0.1030 [+0.0311, +0.1756] | +0.0798 [+0.0496, +0.1176] |
| risk_logistic+hurdle_state_isotonic+h41 | +0.0103 [-0.0327, +0.0542] | +0.0040 [-0.0266, +0.0295] | +0.0138 [+0.0121, +0.0157] | +0.0050 [+0.0006, +0.0093] | +0.0283 [+0.0066, +0.0550] | +0.0327 [+0.0036, +0.0638] | +0.0053 [-0.0047, +0.0150] | +0.1049 [+0.0309, +0.1746] | +0.0774 [+0.0437, +0.1152] |
| risk_logistic+hurdle_state_isotonic+settle | +0.0115 [-0.0324, +0.0533] | +0.0043 [-0.0261, +0.0292] | +0.0138 [+0.0121, +0.0157] | +0.0049 [+0.0006, +0.0091] | +0.0286 [+0.0067, +0.0547] | +0.0315 [+0.0027, +0.0605] | +0.0057 [-0.0045, +0.0157] | +0.1030 [+0.0298, +0.1679] | +0.0798 [+0.0494, +0.1163] |
| risk_logistic+hurdle_state_isotonic+settle+h41 | +0.0103 [-0.0349, +0.0517] | +0.0040 [-0.0254, +0.0300] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0006, +0.0094] | +0.0283 [+0.0072, +0.0540] | +0.0327 [+0.0042, +0.0614] | +0.0053 [-0.0049, +0.0149] | +0.1049 [+0.0341, +0.1752] | +0.0774 [+0.0446, +0.1141] |
| risk_logistic+hurdle_state_platt | +0.0403 [+0.0081, +0.0735] | +0.0078 [-0.0154, +0.0276] | +0.0135 [+0.0118, +0.0152] | +0.0049 [+0.0008, +0.0092] | +0.0309 [+0.0084, +0.0595] | +0.0322 [+0.0053, +0.0616] | +0.0131 [+0.0055, +0.0212] | +0.1030 [+0.0304, +0.1708] | +0.0798 [+0.0479, +0.1161] |
| risk_logistic+hurdle_state_platt+h41 | +0.0396 [+0.0091, +0.0730] | +0.0076 [-0.0164, +0.0283] | +0.0135 [+0.0118, +0.0152] | +0.0050 [+0.0005, +0.0095] | +0.0305 [+0.0086, +0.0572] | +0.0330 [+0.0037, +0.0637] | +0.0129 [+0.0059, +0.0209] | +0.1049 [+0.0345, +0.1711] | +0.0774 [+0.0451, +0.1169] |
| risk_logistic+hurdle_state_platt+settle | +0.0403 [+0.0089, +0.0724] | +0.0078 [-0.0158, +0.0276] | +0.0135 [+0.0118, +0.0152] | +0.0049 [+0.0007, +0.0093] | +0.0309 [+0.0072, +0.0586] | +0.0322 [+0.0038, +0.0616] | +0.0131 [+0.0057, +0.0213] | +0.1030 [+0.0309, +0.1698] | +0.0798 [+0.0477, +0.1165] |
| risk_logistic+hurdle_state_platt+settle+h41 | +0.0396 [+0.0073, +0.0736] | +0.0076 [-0.0161, +0.0291] | +0.0135 [+0.0118, +0.0153] | +0.0050 [+0.0006, +0.0096] | +0.0305 [+0.0076, +0.0585] | +0.0330 [+0.0045, +0.0626] | +0.0129 [+0.0053, +0.0210] | +0.1049 [+0.0348, +0.1781] | +0.0774 [+0.0446, +0.1156] |
| risk_logistic_base | -0.0032 [-0.0226, +0.0153] | +0.0308 [+0.0204, +0.0398] | +0.0138 [+0.0120, +0.0157] | +0.0036 [+0.0001, +0.0064] | +0.0218 [+0.0063, +0.0409] | +0.0357 [+0.0082, +0.0629] | +0.0051 [+0.0001, +0.0096] | +0.0996 [+0.0457, +0.1509] | +0.0731 [+0.0406, +0.1119] |
| risk_logistic_base+every_day | +0.0525 [+0.0247, +0.0816] | +0.0146 [-0.0007, +0.0280] | +0.0132 [+0.0115, +0.0151] | +0.0006 [-0.0058, +0.0051] | +0.0338 [+0.0068, +0.0687] | +0.0408 [+0.0128, +0.0719] | +0.0162 [+0.0093, +0.0239] | +0.0996 [+0.0482, +0.1478] | +0.0731 [+0.0408, +0.1102] |
| risk_logistic_base+every_day+gate | +0.0369 [+0.0121, +0.0653] | +0.0236 [+0.0057, +0.0384] | +0.0136 [+0.0119, +0.0155] | +0.0007 [-0.0062, +0.0054] | +0.0329 [+0.0055, +0.0636] | +0.0414 [+0.0138, +0.0709] | +0.0140 [+0.0077, +0.0211] | +0.0996 [+0.0498, +0.1498] | +0.0731 [+0.0420, +0.1104] |
| risk_logistic_base+every_day+persist | +0.0468 [+0.0227, +0.0724] | +0.0202 [+0.0089, +0.0305] | +0.0133 [+0.0116, +0.0151] | +0.0027 [-0.0012, +0.0058] | +0.0335 [+0.0081, +0.0657] | +0.0400 [+0.0130, +0.0693] | +0.0162 [+0.0102, +0.0229] | +0.0996 [+0.0446, +0.1511] | +0.0731 [+0.0406, +0.1074] |
| risk_logistic_base+every_day+scarce | +0.0525 [+0.0258, +0.0815] | +0.0146 [-0.0009, +0.0276] | +0.0136 [+0.0119, +0.0155] | +0.0036 [-0.0001, +0.0064] | +0.0362 [+0.0088, +0.0721] | +0.0409 [+0.0132, +0.0708] | +0.0173 [+0.0107, +0.0251] | +0.0996 [+0.0428, +0.1521] | +0.0731 [+0.0417, +0.1100] |
| risk_logistic_base+every_day+shrunk | +0.0380 [+0.0234, +0.0555] | +0.0278 [+0.0179, +0.0372] | +0.0137 [+0.0119, +0.0156] | +0.0029 [-0.0015, +0.0061] | +0.0344 [+0.0106, +0.0651] | +0.0386 [+0.0114, +0.0690] | +0.0158 [+0.0118, +0.0207] | +0.0996 [+0.0478, +0.1514] | +0.0731 [+0.0413, +0.1099] |
| risk_logistic_base+hurdle_isotonic | +0.0082 [-0.0350, +0.0508] | -0.0128 [-0.0340, +0.0052] | +0.0120 [+0.0106, +0.0135] | +0.0025 [-0.0026, +0.0060] | +0.0331 [+0.0092, +0.0656] | +0.0382 [+0.0115, +0.0670] | +0.0015 [-0.0086, +0.0117] | +0.0996 [+0.0463, +0.1489] | +0.0731 [+0.0411, +0.1107] |
| risk_logistic_base+hurdle_isotonic+h41 | +0.0089 [-0.0381, +0.0531] | -0.0120 [-0.0332, +0.0064] | +0.0120 [+0.0106, +0.0136] | +0.0025 [-0.0031, +0.0062] | +0.0325 [+0.0081, +0.0629] | +0.0383 [+0.0101, +0.0686] | +0.0017 [-0.0088, +0.0115] | +0.0979 [+0.0469, +0.1465] | +0.0745 [+0.0438, +0.1105] |
| risk_logistic_base+hurdle_isotonic+settle | +0.0082 [-0.0367, +0.0517] | -0.0128 [-0.0357, +0.0061] | +0.0120 [+0.0107, +0.0135] | +0.0025 [-0.0027, +0.0062] | +0.0331 [+0.0079, +0.0646] | +0.0382 [+0.0104, +0.0702] | +0.0015 [-0.0086, +0.0117] | +0.0996 [+0.0463, +0.1508] | +0.0731 [+0.0412, +0.1083] |
| risk_logistic_base+hurdle_isotonic+settle+h41 | +0.0089 [-0.0382, +0.0539] | -0.0120 [-0.0344, +0.0058] | +0.0120 [+0.0106, +0.0135] | +0.0025 [-0.0027, +0.0062] | +0.0325 [+0.0076, +0.0626] | +0.0383 [+0.0102, +0.0683] | +0.0017 [-0.0091, +0.0123] | +0.0979 [+0.0474, +0.1469] | +0.0745 [+0.0424, +0.1142] |
| risk_logistic_base+hurdle_platt | +0.0342 [+0.0043, +0.0702] | -0.0108 [-0.0251, +0.0020] | +0.0104 [+0.0088, +0.0119] | +0.0025 [-0.0025, +0.0062] | +0.0310 [+0.0087, +0.0577] | +0.0374 [+0.0114, +0.0673] | +0.0069 [-0.0002, +0.0154] | +0.0996 [+0.0501, +0.1483] | +0.0731 [+0.0420, +0.1101] |
| risk_logistic_base+hurdle_platt+h41 | +0.0350 [+0.0016, +0.0689] | -0.0099 [-0.0240, +0.0027] | +0.0104 [+0.0088, +0.0119] | +0.0026 [-0.0024, +0.0061] | +0.0304 [+0.0082, +0.0563] | +0.0375 [+0.0103, +0.0658] | +0.0070 [-0.0007, +0.0154] | +0.0979 [+0.0466, +0.1439] | +0.0745 [+0.0446, +0.1114] |
| risk_logistic_base+hurdle_platt+settle | +0.0342 [+0.0036, +0.0693] | -0.0108 [-0.0252, +0.0015] | +0.0104 [+0.0088, +0.0118] | +0.0025 [-0.0025, +0.0063] | +0.0310 [+0.0081, +0.0583] | +0.0374 [+0.0101, +0.0665] | +0.0069 [-0.0005, +0.0148] | +0.0996 [+0.0466, +0.1500] | +0.0731 [+0.0407, +0.1105] |
| risk_logistic_base+hurdle_platt+settle+h41 | +0.0350 [+0.0007, +0.0689] | -0.0099 [-0.0234, +0.0031] | +0.0104 [+0.0088, +0.0120] | +0.0026 [-0.0024, +0.0062] | +0.0304 [+0.0085, +0.0558] | +0.0375 [+0.0089, +0.0673] | +0.0070 [-0.0006, +0.0151] | +0.0979 [+0.0459, +0.1466] | +0.0745 [+0.0436, +0.1100] |
| risk_logistic_base+hurdle_state_isotonic | +0.0120 [-0.0311, +0.0540] | +0.0086 [-0.0194, +0.0308] | +0.0138 [+0.0120, +0.0157] | +0.0036 [-0.0002, +0.0065] | +0.0321 [+0.0093, +0.0610] | +0.0389 [+0.0110, +0.0686] | +0.0065 [-0.0039, +0.0165] | +0.0996 [+0.0463, +0.1499] | +0.0731 [+0.0408, +0.1101] |
| risk_logistic_base+hurdle_state_isotonic+h41 | +0.0109 [-0.0337, +0.0521] | +0.0091 [-0.0177, +0.0319] | +0.0138 [+0.0121, +0.0156] | +0.0037 [-0.0001, +0.0064] | +0.0318 [+0.0094, +0.0586] | +0.0393 [+0.0095, +0.0699] | +0.0062 [-0.0042, +0.0159] | +0.0979 [+0.0475, +0.1473] | +0.0745 [+0.0425, +0.1110] |
| risk_logistic_base+hurdle_state_isotonic+settle | +0.0120 [-0.0302, +0.0532] | +0.0086 [-0.0190, +0.0310] | +0.0138 [+0.0121, +0.0156] | +0.0036 [-0.0000, +0.0064] | +0.0321 [+0.0099, +0.0596] | +0.0389 [+0.0117, +0.0689] | +0.0065 [-0.0034, +0.0165] | +0.0996 [+0.0466, +0.1495] | +0.0731 [+0.0398, +0.1107] |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | +0.0109 [-0.0334, +0.0545] | +0.0091 [-0.0188, +0.0316] | +0.0138 [+0.0121, +0.0156] | +0.0037 [+0.0002, +0.0066] | +0.0318 [+0.0089, +0.0605] | +0.0393 [+0.0106, +0.0694] | +0.0062 [-0.0044, +0.0163] | +0.0979 [+0.0480, +0.1453] | +0.0745 [+0.0429, +0.1115] |
| risk_logistic_base+hurdle_state_platt | +0.0408 [+0.0093, +0.0724] | +0.0121 [-0.0077, +0.0283] | +0.0135 [+0.0119, +0.0154] | +0.0036 [-0.0001, +0.0064] | +0.0345 [+0.0094, +0.0662] | +0.0395 [+0.0109, +0.0692] | +0.0140 [+0.0065, +0.0222] | +0.0996 [+0.0458, +0.1491] | +0.0731 [+0.0418, +0.1090] |
| risk_logistic_base+hurdle_state_platt+h41 | +0.0403 [+0.0075, +0.0741] | +0.0127 [-0.0058, +0.0301] | +0.0135 [+0.0118, +0.0152] | +0.0037 [-0.0001, +0.0064] | +0.0340 [+0.0099, +0.0637] | +0.0396 [+0.0110, +0.0709] | +0.0138 [+0.0064, +0.0221] | +0.0979 [+0.0430, +0.1462] | +0.0745 [+0.0431, +0.1134] |
| risk_logistic_base+hurdle_state_platt+settle | +0.0408 [+0.0099, +0.0756] | +0.0121 [-0.0068, +0.0290] | +0.0135 [+0.0118, +0.0154] | +0.0036 [+0.0001, +0.0064] | +0.0345 [+0.0094, +0.0650] | +0.0395 [+0.0122, +0.0696] | +0.0140 [+0.0064, +0.0221] | +0.0996 [+0.0460, +0.1502] | +0.0731 [+0.0428, +0.1100] |
| risk_logistic_base+hurdle_state_platt+settle+h41 | +0.0403 [+0.0076, +0.0757] | +0.0127 [-0.0078, +0.0293] | +0.0135 [+0.0118, +0.0153] | +0.0037 [+0.0002, +0.0064] | +0.0340 [+0.0093, +0.0646] | +0.0396 [+0.0112, +0.0694] | +0.0138 [+0.0061, +0.0220] | +0.0979 [+0.0456, +0.1459] | +0.0745 [+0.0425, +0.1129] |
| risk_quantile_skewt | -0.0111 [-0.0320, +0.0100] | +0.0047 [-0.0118, +0.0203] | +0.0136 [+0.0119, +0.0155] | +0.0018 [-0.0033, +0.0056] | +0.0227 [+0.0039, +0.0475] | +0.0214 [-0.0122, +0.0556] | +0.0008 [-0.0048, +0.0059] | +0.0945 [+0.0001, +0.1888] | +0.0663 [+0.0181, +0.1187] |
| risk_quantile_skewt_base | -0.0214 [-0.0472, +0.0047] | +0.0165 [+0.0051, +0.0274] | +0.0136 [+0.0119, +0.0156] | +0.0014 [-0.0050, +0.0055] | +0.0232 [+0.0036, +0.0459] | +0.0138 [-0.0251, +0.0536] | +0.0022 [-0.0035, +0.0076] | +0.0712 [-0.0019, +0.1363] | +0.0525 [+0.0089, +0.0978] |
| risk_quantile_skewt_base+every_day | +0.0343 [+0.0002, +0.0683] | +0.0002 [-0.0148, +0.0139] | +0.0130 [+0.0112, +0.0149] | -0.0016 [-0.0088, +0.0039] | +0.0351 [+0.0021, +0.0751] | +0.0189 [-0.0231, +0.0600] | +0.0133 [+0.0059, +0.0211] | +0.0712 [-0.0034, +0.1375] | +0.0525 [+0.0098, +0.1012] |
| risk_quantile_skewt_base+every_day+gate | +0.0187 [-0.0118, +0.0504] | +0.0093 [-0.0083, +0.0254] | +0.0135 [+0.0116, +0.0153] | -0.0015 [-0.0094, +0.0043] | +0.0343 [+0.0031, +0.0715] | +0.0195 [-0.0207, +0.0625] | +0.0111 [+0.0044, +0.0185] | +0.0712 [+0.0011, +0.1382] | +0.0525 [+0.0092, +0.0984] |
| risk_quantile_skewt_base+every_day+persist | +0.0275 [-0.0047, +0.0596] | +0.0054 [-0.0058, +0.0168] | +0.0132 [+0.0115, +0.0149] | +0.0007 [-0.0050, +0.0046] | +0.0352 [+0.0057, +0.0727] | +0.0153 [-0.0248, +0.0562] | +0.0133 [+0.0068, +0.0204] | +0.0712 [-0.0019, +0.1378] | +0.0525 [+0.0096, +0.1022] |
| risk_quantile_skewt_base+every_day+scarce | +0.0343 [-0.0011, +0.0666] | +0.0002 [-0.0144, +0.0143] | +0.0134 [+0.0117, +0.0153] | +0.0014 [-0.0049, +0.0053] | +0.0376 [+0.0057, +0.0784] | +0.0190 [-0.0252, +0.0599] | +0.0143 [+0.0069, +0.0223] | +0.0712 [-0.0002, +0.1350] | +0.0525 [+0.0102, +0.0997] |
| risk_quantile_skewt_base+every_day+shrunk | +0.0198 [-0.0072, +0.0437] | +0.0135 [+0.0019, +0.0245] | +0.0135 [+0.0118, +0.0154] | +0.0008 [-0.0057, +0.0051] | +0.0357 [+0.0066, +0.0714] | +0.0167 [-0.0255, +0.0558] | +0.0129 [+0.0080, +0.0179] | +0.0712 [+0.0003, +0.1362] | +0.0525 [+0.0086, +0.1013] |
| risk_quantile_skewt_base+hurdle_isotonic | -0.0100 [-0.0551, +0.0358] | -0.0271 [-0.0463, -0.0094] | +0.0119 [+0.0105, +0.0133] | +0.0003 [-0.0063, +0.0050] | +0.0344 [+0.0052, +0.0718] | +0.0163 [-0.0259, +0.0584] | -0.0015 [-0.0118, +0.0085] | +0.0712 [+0.0005, +0.1352] | +0.0525 [+0.0098, +0.0993] |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | +0.0012 [-0.0435, +0.0435] | -0.0200 [-0.0404, -0.0017] | +0.0118 [+0.0105, +0.0134] | +0.0006 [-0.0056, +0.0051] | +0.0345 [+0.0051, +0.0705] | +0.0304 [-0.0017, +0.0652] | +0.0001 [-0.0101, +0.0102] | +0.0954 [+0.0303, +0.1580] | +0.0603 [+0.0163, +0.1065] |
| risk_quantile_skewt_base+hurdle_isotonic+settle | -0.0100 [-0.0553, +0.0370] | -0.0271 [-0.0472, -0.0088] | +0.0119 [+0.0104, +0.0134] | +0.0003 [-0.0061, +0.0050] | +0.0344 [+0.0052, +0.0733] | +0.0163 [-0.0234, +0.0572] | -0.0015 [-0.0117, +0.0086] | +0.0712 [+0.0010, +0.1361] | +0.0525 [+0.0103, +0.0964] |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | +0.0012 [-0.0405, +0.0420] | -0.0200 [-0.0414, -0.0020] | +0.0118 [+0.0105, +0.0134] | +0.0006 [-0.0056, +0.0051] | +0.0345 [+0.0052, +0.0721] | +0.0304 [-0.0015, +0.0625] | +0.0001 [-0.0097, +0.0100] | +0.0954 [+0.0221, +0.1551] | +0.0603 [+0.0176, +0.1040] |
| risk_quantile_skewt_base+hurdle_platt | +0.0161 [-0.0193, +0.0531] | -0.0251 [-0.0390, -0.0110] | +0.0102 [+0.0086, +0.0117] | +0.0003 [-0.0059, +0.0050] | +0.0323 [+0.0068, +0.0663] | +0.0155 [-0.0248, +0.0562] | +0.0039 [-0.0037, +0.0121] | +0.0712 [+0.0005, +0.1381] | +0.0525 [+0.0074, +0.0991] |
| risk_quantile_skewt_base+hurdle_platt+h41 | +0.0272 [-0.0050, +0.0612] | -0.0180 [-0.0316, -0.0051] | +0.0102 [+0.0085, +0.0117] | +0.0007 [-0.0057, +0.0051] | +0.0324 [+0.0057, +0.0639] | +0.0296 [-0.0022, +0.0624] | +0.0055 [-0.0025, +0.0131] | +0.0954 [+0.0261, +0.1579] | +0.0603 [+0.0192, +0.1066] |
| risk_quantile_skewt_base+hurdle_platt+settle | +0.0161 [-0.0203, +0.0557] | -0.0251 [-0.0392, -0.0111] | +0.0102 [+0.0087, +0.0117] | +0.0003 [-0.0060, +0.0051] | +0.0323 [+0.0053, +0.0657] | +0.0155 [-0.0251, +0.0532] | +0.0039 [-0.0036, +0.0122] | +0.0712 [+0.0039, +0.1379] | +0.0525 [+0.0111, +0.0986] |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | +0.0272 [-0.0041, +0.0590] | -0.0180 [-0.0321, -0.0043] | +0.0102 [+0.0085, +0.0118] | +0.0007 [-0.0054, +0.0051] | +0.0324 [+0.0055, +0.0642] | +0.0296 [-0.0031, +0.0637] | +0.0055 [-0.0015, +0.0138] | +0.0954 [+0.0252, +0.1564] | +0.0603 [+0.0173, +0.1059] |
| risk_quantile_skewt_base+hurdle_state_isotonic | -0.0061 [-0.0513, +0.0369] | -0.0057 [-0.0299, +0.0142] | +0.0136 [+0.0119, +0.0154] | +0.0014 [-0.0045, +0.0054] | +0.0335 [+0.0066, +0.0689] | +0.0170 [-0.0236, +0.0575] | +0.0036 [-0.0067, +0.0134] | +0.0712 [+0.0003, +0.1339] | +0.0525 [+0.0085, +0.0969] |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | +0.0032 [-0.0371, +0.0429] | +0.0010 [-0.0252, +0.0228] | +0.0136 [+0.0119, +0.0155] | +0.0018 [-0.0039, +0.0054] | +0.0338 [+0.0072, +0.0668] | +0.0314 [+0.0002, +0.0670] | +0.0047 [-0.0051, +0.0140] | +0.0954 [+0.0272, +0.1583] | +0.0603 [+0.0190, +0.1068] |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | -0.0061 [-0.0496, +0.0402] | -0.0057 [-0.0294, +0.0155] | +0.0136 [+0.0119, +0.0155] | +0.0014 [-0.0046, +0.0054] | +0.0335 [+0.0058, +0.0684] | +0.0170 [-0.0234, +0.0566] | +0.0036 [-0.0067, +0.0135] | +0.0712 [+0.0003, +0.1381] | +0.0525 [+0.0086, +0.0978] |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | +0.0032 [-0.0382, +0.0447] | +0.0010 [-0.0244, +0.0221] | +0.0136 [+0.0118, +0.0155] | +0.0018 [-0.0041, +0.0055] | +0.0338 [+0.0065, +0.0691] | +0.0314 [-0.0009, +0.0656] | +0.0047 [-0.0056, +0.0141] | +0.0954 [+0.0249, +0.1560] | +0.0603 [+0.0188, +0.1050] |
| risk_quantile_skewt_base+hurdle_state_platt | +0.0226 [-0.0131, +0.0612] | -0.0022 [-0.0195, +0.0139] | +0.0133 [+0.0115, +0.0151] | +0.0014 [-0.0047, +0.0054] | +0.0358 [+0.0065, +0.0715] | +0.0176 [-0.0254, +0.0569] | +0.0110 [+0.0038, +0.0191] | +0.0712 [-0.0026, +0.1398] | +0.0525 [+0.0087, +0.0981] |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | +0.0326 [+0.0009, +0.0651] | +0.0047 [-0.0129, +0.0210] | +0.0133 [+0.0116, +0.0150] | +0.0018 [-0.0043, +0.0054] | +0.0360 [+0.0065, +0.0723] | +0.0317 [-0.0013, +0.0663] | +0.0123 [+0.0050, +0.0202] | +0.0954 [+0.0243, +0.1554] | +0.0603 [+0.0193, +0.1048] |
| risk_quantile_skewt_base+hurdle_state_platt+settle | +0.0226 [-0.0129, +0.0600] | -0.0022 [-0.0189, +0.0130] | +0.0133 [+0.0116, +0.0152] | +0.0014 [-0.0044, +0.0054] | +0.0358 [+0.0072, +0.0730] | +0.0176 [-0.0239, +0.0571] | +0.0110 [+0.0036, +0.0193] | +0.0712 [-0.0006, +0.1383] | +0.0525 [+0.0119, +0.1001] |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | +0.0326 [+0.0023, +0.0655] | +0.0047 [-0.0130, +0.0195] | +0.0133 [+0.0116, +0.0150] | +0.0018 [-0.0043, +0.0055] | +0.0360 [+0.0071, +0.0710] | +0.0317 [-0.0015, +0.0670] | +0.0123 [+0.0052, +0.0200] | +0.0954 [+0.0260, +0.1590] | +0.0603 [+0.0197, +0.1058] |
