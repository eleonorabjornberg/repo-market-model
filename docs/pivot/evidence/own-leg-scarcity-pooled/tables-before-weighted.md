Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.9 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+every_day | 17 of 26 | 0.654 [0.474, 0.812] | 0.411 | 7.88 flat / 3.79 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.481, 0.818] | 0.385 | 7.35 flat / 3.67 weighted (tier 1 on the weighted count) | 3.4 / 1.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.524, 0.857] | 0.375 | 6.96 flat / 3.39 weighted (tier 1 on the weighted count) | 2.7 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 19 of 26 | 0.731 [0.560, 0.889] | 0.382 | 7.08 flat / 3.46 weighted (tier 1 on the weighted count) | 3.2 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+persist | 16 of 26 | 0.615 [0.435, 0.800] | 0.308 | 6.46 flat / 3.09 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+scarce | 17 of 26 | 0.654 [0.483, 0.818] | 0.392 | 7.58 flat / 3.60 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+shrunk | 16 of 26 | 0.615 [0.438, 0.800] | 0.385 | 7.46 flat / 3.66 weighted (tier 1 on the weighted count) | 1.5 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic | 16 of 26 | 0.615 [0.437, 0.808] | 0.278 | 5.92 flat / 2.77 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.375, 0.778] | 0.284 | 6.04 flat / 2.87 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+settle | 16 of 26 | 0.615 [0.433, 0.792] | 0.286 | 6.08 flat / 2.94 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_isotonic+settle+h41 | 16 of 26 | 0.615 [0.435, 0.800] | 0.269 | 5.77 flat / 2.81 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.760] | 0.306 | 6.42 flat / 3.10 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+h41 | 16 of 26 | 0.615 [0.424, 0.794] | 0.385 | 7.27 flat / 3.88 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+settle | 16 of 26 | 0.615 [0.429, 0.790] | 0.295 | 6.23 flat / 3.04 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_platt+settle+h41 | 16 of 26 | 0.615 [0.423, 0.793] | 0.295 | 6.23 flat / 3.11 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic | 16 of 26 | 0.615 [0.424, 0.800] | 0.271 | 5.81 flat / 2.69 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+h41 | 15 of 26 | 0.577 [0.381, 0.769] | 0.276 | 5.88 flat / 2.84 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+settle | 16 of 26 | 0.615 [0.436, 0.800] | 0.269 | 5.62 flat / 2.62 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 16 of 26 | 0.615 [0.438, 0.790] | 0.269 | 5.42 flat / 2.56 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_platt | 15 of 26 | 0.577 [0.375, 0.760] | 0.269 | 5.69 flat / 2.71 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+h41 | 16 of 26 | 0.615 [0.429, 0.795] | 0.276 | 5.88 flat / 2.83 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+settle | 16 of 26 | 0.615 [0.433, 0.800] | 0.269 | 5.54 flat / 2.59 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_platt+settle+h41 | 16 of 26 | 0.615 [0.435, 0.792] | 0.269 | 5.54 flat / 2.63 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.15 flat / 1.44 weighted (tier 1 on the weighted count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base+every_day | 18 of 26 | 0.692 [0.520, 0.850] | 0.416 | 7.96 flat / 3.85 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+gate | 18 of 26 | 0.692 [0.517, 0.850] | 0.385 | 7.27 flat / 3.64 weighted (tier 1 on the weighted count) | 1.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+persist | 16 of 26 | 0.615 [0.423, 0.800] | 0.358 | 6.69 flat / 3.24 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+scarce | 18 of 26 | 0.692 [0.522, 0.857] | 0.397 | 7.65 flat / 3.65 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+shrunk | 17 of 26 | 0.654 [0.471, 0.833] | 0.385 | 7.35 flat / 3.65 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.767] | 0.308 | 6.46 flat / 3.11 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.368, 0.778] | 0.276 | 5.88 flat / 2.76 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+settle | 15 of 26 | 0.577 [0.368, 0.767] | 0.291 | 6.15 flat / 3.01 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 15 of 26 | 0.577 [0.370, 0.769] | 0.269 | 5.54 flat / 2.65 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt | 15 of 26 | 0.577 [0.375, 0.769] | 0.368 | 6.85 flat / 3.38 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+h41 | 15 of 26 | 0.577 [0.375, 0.774] | 0.349 | 6.54 flat / 3.15 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+settle | 15 of 26 | 0.577 [0.375, 0.773] | 0.299 | 6.31 flat / 3.05 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt+settle+h41 | 15 of 26 | 0.577 [0.381, 0.767] | 0.293 | 6.19 flat / 3.08 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic | 15 of 26 | 0.577 [0.385, 0.778] | 0.280 | 5.96 flat / 2.78 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 15 of 26 | 0.577 [0.389, 0.765] | 0.269 | 5.73 flat / 2.62 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+settle | 15 of 26 | 0.577 [0.384, 0.769] | 0.271 | 5.81 flat / 2.66 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 15 of 26 | 0.577 [0.389, 0.774] | 0.269 | 5.50 flat / 2.55 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.387, 0.769] | 0.271 | 5.81 flat / 2.81 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+h41 | 15 of 26 | 0.577 [0.371, 0.773] | 0.271 | 5.81 flat / 2.78 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.390, 0.774] | 0.269 | 5.50 flat / 2.58 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 15 of 26 | 0.577 [0.381, 0.774] | 0.269 | 5.50 flat / 2.63 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted (tier 1 on the weighted count) | 3.2 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic+every_day | 17 of 26 | 0.654 [0.480, 0.826] | 0.409 | 7.85 flat / 3.67 weighted (tier 1 on the weighted count) | 1.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.520, 0.857] | 0.418 | 8.00 flat / 4.12 weighted (tier 1 on the weighted count) | 3.2 / 1.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+every_day+persist | 17 of 26 | 0.654 [0.481, 0.818] | 0.385 | 7.19 flat / 3.39 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+scarce | 17 of 26 | 0.654 [0.476, 0.818] | 0.389 | 7.54 flat / 3.48 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+shrunk | 18 of 26 | 0.692 [0.522, 0.852] | 0.389 | 7.54 flat / 3.65 weighted (tier 1 on the weighted count) | 1.9 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+hurdle_isotonic | 15 of 26 | 0.577 [0.400, 0.760] | 0.293 | 6.19 flat / 2.94 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.391, 0.750] | 0.278 | 5.92 flat / 2.81 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle | 15 of 26 | 0.577 [0.394, 0.760] | 0.291 | 6.15 flat / 2.96 weighted (tier 1 on the weighted count) | 1.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle+h41 | 16 of 26 | 0.615 [0.423, 0.806] | 0.269 | 5.65 flat / 2.68 weighted (tier 1 on the weighted count) | 1.9 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_platt | 15 of 26 | 0.577 [0.391, 0.762] | 0.351 | 6.58 flat / 3.11 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.358 | 6.69 flat / 3.28 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+settle | 15 of 26 | 0.577 [0.400, 0.762] | 0.363 | 6.77 flat / 3.28 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_platt+settle+h41 | 16 of 26 | 0.615 [0.429, 0.792] | 0.288 | 6.12 flat / 2.88 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic | 15 of 26 | 0.577 [0.400, 0.750] | 0.368 | 6.85 flat / 3.36 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+h41 | 15 of 26 | 0.577 [0.400, 0.760] | 0.349 | 6.54 flat / 3.17 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle | 15 of 26 | 0.577 [0.391, 0.750] | 0.299 | 6.31 flat / 3.05 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 16 of 26 | 0.615 [0.429, 0.800] | 0.269 | 5.58 flat / 2.62 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt | 15 of 26 | 0.577 [0.385, 0.762] | 0.382 | 7.08 flat / 3.57 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+h41 | 15 of 26 | 0.577 [0.391, 0.750] | 0.361 | 6.73 flat / 3.41 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.389, 0.757] | 0.356 | 6.65 flat / 3.25 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt+settle+h41 | 16 of 26 | 0.615 [0.429, 0.792] | 0.269 | 5.62 flat / 2.65 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.231 | 2.88 flat / 2.18 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base+every_day | 13 of 26 | 0.500 [0.321, 0.679] | 0.385 | 7.15 flat / 3.33 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.815] | 0.421 | 8.04 flat / 4.12 weighted (tier 1 on the weighted count) | 3.2 / 1.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+every_day+persist | 14 of 26 | 0.538 [0.364, 0.719] | 0.365 | 6.81 flat / 3.08 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+scarce | 13 of 26 | 0.500 [0.321, 0.667] | 0.368 | 6.85 flat / 3.13 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+shrunk | 17 of 26 | 0.654 [0.480, 0.821] | 0.387 | 7.50 flat / 3.60 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.636] | 0.269 | 5.42 flat / 2.54 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+h41 | 14 of 26 | 0.538 [0.368, 0.720] | 0.280 | 5.96 flat / 2.74 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle | 16 of 26 | 0.615 [0.444, 0.783] | 0.269 | 5.35 flat / 2.60 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 15 of 26 | 0.577 [0.406, 0.750] | 0.293 | 6.19 flat / 2.90 weighted (tier 1 on the weighted count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt | 12 of 26 | 0.462 [0.281, 0.650] | 0.284 | 6.04 flat / 2.81 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.276 | 5.88 flat / 2.63 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+settle | 15 of 26 | 0.577 [0.400, 0.762] | 0.269 | 5.69 flat / 2.66 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt+settle+h41 | 15 of 26 | 0.577 [0.400, 0.762] | 0.295 | 6.23 flat / 2.87 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic | 14 of 26 | 0.538 [0.370, 0.720] | 0.358 | 6.69 flat / 3.21 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 14 of 26 | 0.538 [0.368, 0.714] | 0.358 | 6.69 flat / 3.12 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle | 15 of 26 | 0.577 [0.400, 0.760] | 0.288 | 6.12 flat / 2.97 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 15 of 26 | 0.577 [0.400, 0.758] | 0.297 | 6.27 flat / 2.96 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt | 14 of 26 | 0.538 [0.364, 0.719] | 0.363 | 6.77 flat / 3.29 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.364, 0.714] | 0.349 | 6.54 flat / 3.11 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.394, 0.750] | 0.282 | 6.00 flat / 2.88 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.286 | 6.08 flat / 2.90 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt | 14 of 26 | 0.538 [0.360, 0.719] | 0.269 | 5.08 flat / 4.36 weighted (tier 1 on the weighted count) | 8.3 / 12.1 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 2.88 flat / 2.14 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base+every_day | 16 of 26 | 0.615 [0.444, 0.792] | 0.423 | 8.15 flat / 4.08 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.467, 0.824] | 0.399 | 7.69 flat / 3.90 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 0.413 | 7.92 flat / 4.05 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+scarce | 16 of 26 | 0.615 [0.429, 0.781] | 0.409 | 7.85 flat / 3.88 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+shrunk | 19 of 26 | 0.731 [0.560, 0.882] | 0.423 | 8.73 flat / 4.55 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+hurdle_isotonic | 13 of 26 | 0.500 [0.333, 0.688] | 0.288 | 6.12 flat / 2.94 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 13 of 26 | 0.500 [0.320, 0.680] | 0.351 | 6.58 flat / 3.24 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 16 of 26 | 0.615 [0.429, 0.800] | 0.269 | 5.19 flat / 2.46 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 16 of 26 | 0.615 [0.429, 0.789] | 0.280 | 5.96 flat / 2.70 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt | 14 of 26 | 0.538 [0.364, 0.715] | 0.308 | 6.46 flat / 3.13 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 13 of 26 | 0.500 [0.333, 0.680] | 0.375 | 6.96 flat / 3.38 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle | 16 of 26 | 0.615 [0.435, 0.800] | 0.269 | 5.58 flat / 2.63 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 16 of 26 | 0.615 [0.435, 0.793] | 0.358 | 6.69 flat / 3.22 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.321, 0.677] | 0.385 | 7.19 flat / 3.46 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.310, 0.679] | 0.385 | 7.42 flat / 3.69 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 16 of 26 | 0.615 [0.417, 0.792] | 0.291 | 6.15 flat / 2.93 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 16 of 26 | 0.615 [0.435, 0.800] | 0.365 | 6.81 flat / 3.18 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt | 14 of 26 | 0.538 [0.367, 0.720] | 0.368 | 6.85 flat / 3.35 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 13 of 26 | 0.500 [0.318, 0.682] | 0.385 | 7.12 flat / 3.58 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 16 of 26 | 0.615 [0.417, 0.792] | 0.286 | 6.08 flat / 2.96 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 16 of 26 | 0.615 [0.429, 0.792] | 0.361 | 6.73 flat / 3.30 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |

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
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.760] | 5.115 [3.425, 7.474] | 2.183 [1.371, 3.329] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 5.000 [3.235, 7.369] | 2.067 [1.264, 3.197] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.769 [2.960, 7.251] | 2.058 [1.195, 3.298] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.115 [2.519, 6.334] | 1.702 [0.950, 2.763] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.231 [2.586, 6.471] | 1.942 [1.136, 3.100] |
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
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.680] | 3.538 [2.559, 5.002] | 1.558 [1.070, 2.350] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.650] | 3.269 [2.139, 4.880] | 1.394 [0.947, 2.084] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.244, 0.619] | 3.423 [2.178, 5.167] | 1.442 [0.936, 2.237] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.462 [2.240, 5.222] | 1.500 [1.007, 2.229] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.763] | 3.500 [2.250, 5.287] | 1.644 [1.073, 2.487] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.412 [3.444, 8.601] | 2.015 [1.275, 3.201] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 9.889 [6.562, 18.802] | 6.000 [3.778, 12.818] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm+every_day+gate+settle+h41+iorb:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.367, 0.704] | 3.692 [2.658, 5.143] | 1.635 [1.132, 2.431] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.652] | 3.269 [2.130, 4.741] | 1.394 [0.938, 2.060] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 3.423 [2.174, 5.100] | 1.442 [0.929, 2.209] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.265, 0.667] | 3.462 [2.216, 5.111] | 1.500 [1.000, 2.234] |
| lead 5 alone (pass) | 26 | 15 | 0.577 [0.391, 0.762] | 3.500 [2.219, 5.200] | 1.644 [1.087, 2.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.967] | 5.412 [3.360, 8.309] | 2.015 [1.250, 3.143] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 10.222 (no interval) | 6.194 (no interval) |

Recall with equal weight per regime: 0.641 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 4/5).

risk_gbm+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.387, 0.762] | 4.115 [2.533, 6.458] | 1.692 [0.962, 2.750] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.462 [2.743, 6.938] | 1.865 [1.091, 3.031] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 5.038 [3.028, 7.834] | 2.231 [1.250, 3.672] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.231 [2.484, 6.640] | 1.654 [0.898, 2.734] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 3.769 [2.178, 6.062] | 1.663 [0.913, 2.778] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.176 [4.470, 11.500] | 3.088 [1.783, 5.222] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.111 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.389, 0.760] | 5.077 [3.428, 7.479] | 2.173 [1.354, 3.397] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 4.923 [3.148, 7.365] | 2.038 [1.231, 3.219] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.615 [2.829, 7.044] | 1.981 [1.153, 3.175] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.962 [2.407, 6.211] | 1.615 [0.902, 2.667] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.115 [2.538, 6.500] | 1.865 [1.104, 3.036] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.786, 11.445] | 3.147 [1.880, 5.250] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.889 (no interval) | 4.444 (no interval) |

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
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.375, 0.778] | 4.038 [2.414, 6.300] | 1.712 [0.948, 2.849] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.577] | 4.923 [3.000, 7.625] | 2.163 [1.176, 3.630] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.613] | 4.385 [2.464, 7.000] | 1.962 [0.954, 3.408] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.769 [1.929, 6.250] | 1.779 [0.780, 3.188] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.565] | 3.923 [2.102, 6.418] | 1.933 [0.904, 3.414] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 7.647 [4.863, 12.333] | 3.309 [1.883, 5.773] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 3.000 [1.374, 6.802] | 2.028 [0.765, 5.108] |

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
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.393, 0.778] | 4.038 [2.389, 6.389] | 1.712 [0.952, 2.870] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.737] | 4.462 [2.562, 7.131] | 1.990 [1.071, 3.352] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.282, 0.667] | 4.423 [2.500, 7.201] | 2.058 [1.077, 3.556] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.808 [2.074, 6.294] | 1.856 [0.909, 3.284] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.667] | 3.577 [1.893, 6.000] | 1.817 [0.871, 3.268] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.556, 1.000] | 7.118 [4.417, 11.445] | 3.103 [1.776, 5.417] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.250 (no interval) |

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
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.462 [2.586, 7.143] | 2.077 [1.125, 3.516] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.318, 6.549] | 1.962 [1.036, 3.393] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.259, 0.667] | 4.038 [2.277, 6.543] | 2.029 [1.054, 3.519] |
| inside 2018-2019 | 17 | 13 | 0.765 (no interval) | 7.118 (no interval) | 3.103 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 2.917 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 16 | 0.615 [0.423, 0.793] | 4.269 [2.675, 6.786] | 1.827 [1.075, 3.036] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.741] | 4.423 [2.583, 7.108] | 1.981 [1.069, 3.330] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.500 [2.609, 7.313] | 2.115 [1.130, 3.589] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.038 [2.304, 6.543] | 1.971 [1.029, 3.394] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.808 [2.179, 6.174] | 1.962 [1.023, 3.370] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.118 [4.444, 11.333] | 3.103 [1.766, 5.401] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.556 (no interval) | 3.111 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.774] | 4.538 [2.727, 7.167] | 1.990 [1.138, 3.328] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.654 [2.839, 7.381] | 2.106 [1.125, 3.605] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.385 [2.433, 7.126] | 1.981 [1.000, 3.511] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.000 [2.184, 6.725] | 1.837 [0.875, 3.366] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.615] | 4.500 [2.565, 7.351] | 2.058 [1.048, 3.641] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.588 [4.889, 11.820] | 3.235 [1.913, 5.306] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 2.444 [0.936, 6.167] | 1.667 [0.500, 4.816] |

Recall with equal weight per regime: 0.416 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.381, 0.769] | 4.577 [2.823, 6.934] | 2.000 [1.125, 3.232] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.176, 0.520] | 4.538 [2.652, 7.040] | 2.106 [1.109, 3.501] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.346 [2.440, 6.854] | 1.942 [0.941, 3.297] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.038 [2.250, 6.522] | 1.846 [0.871, 3.212] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 4.692 [2.738, 7.286] | 2.231 [1.166, 3.733] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.588 [4.867, 11.668] | 3.235 [1.958, 5.328] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 2.083 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.387, 0.769] | 4.538 [2.689, 7.096] | 1.990 [1.121, 3.283] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.312, 0.692] | 4.346 [2.500, 7.000] | 1.981 [1.073, 3.333] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.462 [2.556, 7.167] | 2.058 [1.100, 3.456] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.808 [2.097, 6.250] | 1.837 [0.940, 3.181] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.692 [2.000, 6.143] | 1.817 [0.890, 3.209] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.611, 11.534] | 2.985 [1.750, 5.109] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.917 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.765] | 4.577 [2.692, 7.101] | 2.000 [1.081, 3.240] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.321, 0.688] | 4.385 [2.417, 7.000] | 1.962 [1.033, 3.299] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 4.423 [2.470, 7.076] | 2.048 [1.073, 3.487] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.731 [2.000, 6.235] | 1.808 [0.886, 3.185] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 3.577 [1.884, 6.000] | 1.788 [0.852, 3.191] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.476, 11.364] | 2.985 [1.700, 4.964] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.111 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.760] | 4.577 [2.794, 7.208] | 2.029 [1.169, 3.333] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.577 [2.778, 7.312] | 2.144 [1.208, 3.684] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.346 [2.454, 7.250] | 1.962 [1.000, 3.463] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.000 [2.233, 6.679] | 1.837 [0.875, 3.350] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.579] | 4.462 [2.536, 7.346] | 2.019 [1.019, 3.588] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.588 [5.000, 12.000] | 3.235 [1.987, 5.515] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.111 (no interval) | 1.722 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.795] | 4.692 [2.932, 7.111] | 2.058 [1.185, 3.310] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.536] | 4.500 [2.675, 7.000] | 2.096 [1.129, 3.444] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.308 [2.428, 6.896] | 1.923 [0.955, 3.250] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.077 [2.266, 6.501] | 1.856 [0.894, 3.205] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.654 [2.676, 7.347] | 2.192 [1.167, 3.706] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.588 [4.947, 11.876] | 3.235 [1.964, 5.375] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.781] | 4.577 [2.833, 7.135] | 2.029 [1.188, 3.275] |
| lead 2 alone (fail) | 26 | 14 | 0.538 [0.348, 0.731] | 4.385 [2.606, 7.001] | 2.019 [1.083, 3.407] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.304, 0.704] | 4.423 [2.629, 7.088] | 2.038 [1.081, 3.427] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.769 [2.120, 6.191] | 1.827 [0.932, 3.160] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.731 [2.069, 6.143] | 1.856 [0.913, 3.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.562, 11.375] | 2.985 [1.739, 5.094] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.444 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.435, 0.792] | 4.692 [2.828, 7.091] | 2.058 [1.155, 3.290] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.316, 0.688] | 4.423 [2.515, 6.931] | 1.971 [1.030, 3.240] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.278, 0.654] | 4.500 [2.520, 7.131] | 2.115 [1.137, 3.500] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.731 [2.037, 6.041] | 1.808 [0.901, 3.083] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.577 [1.880, 5.793] | 1.788 [0.871, 3.074] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.412, 11.417] | 2.985 [1.685, 5.028] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.444 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.385 [0.947, 2.048] | 0.750 [0.462, 1.205] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.571, 1.528] | 0.577 [0.309, 0.987] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.385 [0.864, 2.160] | 0.885 [0.471, 1.560] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.154 [0.704, 1.824] | 0.683 [0.370, 1.174] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.600] | 1.115 [0.666, 1.783] | 0.760 [0.393, 1.333] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.556 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.719] | 1.500 [1.000, 2.286] | 0.971 [0.556, 1.633] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.655, 1.778] | 0.644 [0.302, 1.174] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.385 [0.857, 2.227] | 0.913 [0.464, 1.638] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.231 [0.727, 1.955] | 0.760 [0.364, 1.359] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.667 [1.769, 8.500] | 3.306 [1.479, 8.002] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.440, 0.800] | 5.192 [3.444, 7.619] | 2.279 [1.430, 3.600] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.207, 7.400] | 2.029 [1.250, 3.234] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.769 [2.941, 7.392] | 2.058 [1.214, 3.282] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 4.385 [2.710, 6.789] | 1.913 [1.142, 3.070] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.423 [2.703, 6.929] | 2.087 [1.241, 3.395] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.471 [4.773, 11.779] | 3.176 [1.867, 5.251] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 8.889 (no interval) | 5.111 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 3.385 [2.367, 4.929] | 1.567 [1.045, 2.389] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.516] | 3.808 [2.562, 5.653] | 1.558 [1.013, 2.364] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 3.500 [2.233, 5.353] | 1.596 [1.008, 2.500] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 3.808 [2.500, 5.715] | 1.606 [1.050, 2.430] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.210, 0.571] | 3.731 [2.367, 5.600] | 1.625 [1.042, 2.475] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 5.765 [3.759, 9.154] | 2.191 [1.416, 3.568] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.111 (no interval) | 6.389 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.769] | 4.577 [2.937, 7.000] | 1.971 [1.220, 3.155] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.600] | 4.462 [2.733, 7.000] | 1.837 [1.078, 3.068] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 5.000 [3.050, 7.835] | 2.221 [1.238, 3.695] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.385 [2.621, 6.884] | 1.837 [1.060, 3.060] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 3.962 [2.343, 6.391] | 1.808 [1.033, 3.090] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.176 [4.416, 11.400] | 3.088 [1.760, 5.171] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.778 (no interval) | 3.528 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.154 [3.475, 7.500] | 2.269 [1.458, 3.500] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.885 [3.172, 7.250] | 2.000 [1.233, 3.079] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.615 [2.867, 7.074] | 1.981 [1.171, 3.203] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.231 [2.606, 6.417] | 1.827 [1.070, 2.950] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 4.308 [2.647, 6.580] | 2.010 [1.186, 3.202] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.471 [4.909, 11.714] | 3.176 [1.945, 5.269] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 8.000 [5.083, 15.000] | 4.556 [2.731, 9.750] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.763] | 4.615 [3.121, 6.941] | 2.144 [1.371, 3.400] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.229, 0.550] | 4.308 [2.793, 6.467] | 1.692 [1.090, 2.604] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.500 [2.703, 7.046] | 2.010 [1.177, 3.287] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.577 [2.943, 7.000] | 2.058 [1.274, 3.278] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 4.385 [2.760, 6.768] | 2.048 [1.226, 3.328] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.706 [4.080, 10.750] | 2.824 [1.590, 4.767] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.751] | 8.556 [5.545, 17.000] | 5.222 [3.115, 11.301] |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.767] | 4.808 [2.965, 7.319] | 2.183 [1.250, 3.492] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.577] | 4.923 [2.974, 7.546] | 2.135 [1.163, 3.479] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 4.615 [2.658, 7.200] | 2.173 [1.160, 3.550] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 4.038 [2.316, 6.348] | 1.885 [0.950, 3.204] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 3.808 [2.000, 6.185] | 1.837 [0.857, 3.238] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.955] | 7.647 [4.908, 11.932] | 3.309 [1.932, 5.584] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 4.222 [2.143, 9.000] | 2.722 [1.143, 6.562] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

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
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 3.846 [2.000, 6.280] | 1.923 [0.945, 3.275] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.267, 0.654] | 4.077 [2.182, 6.591] | 2.029 [1.007, 3.448] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.118 [4.438, 11.504] | 3.103 [1.771, 5.322] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.833 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.370, 0.769] | 4.692 [2.956, 7.130] | 2.115 [1.236, 3.434] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.423 [2.625, 6.945] | 1.981 [1.083, 3.292] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.300, 0.706] | 4.269 [2.433, 6.850] | 1.952 [1.033, 3.300] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.808 [2.052, 6.211] | 1.904 [0.947, 3.303] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 3.846 [2.130, 6.239] | 1.952 [1.000, 3.350] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.000 [4.368, 11.231] | 3.074 [1.760, 5.143] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.778 (no interval) | 1.861 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.769] | 4.692 [3.000, 7.000] | 2.048 [1.261, 3.250] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.962 [3.000, 7.522] | 2.154 [1.196, 3.460] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.462 [2.484, 6.955] | 2.077 [1.055, 3.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 3.962 [2.219, 6.224] | 1.856 [0.921, 3.161] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.526] | 4.192 [2.395, 6.636] | 2.106 [1.103, 3.554] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 7.647 [4.952, 11.875] | 3.309 [1.985, 5.501] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.333 (no interval) | 3.500 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

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
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.375, 0.773] | 4.692 [3.025, 7.154] | 2.048 [1.224, 3.303] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.615 [2.666, 7.351] | 2.125 [1.169, 3.567] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.296, 0.700] | 4.385 [2.417, 7.100] | 2.058 [1.083, 3.490] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 4.038 [2.250, 6.720] | 2.000 [1.054, 3.450] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.263, 0.656] | 4.269 [2.444, 7.000] | 2.135 [1.129, 3.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.118 [4.500, 11.500] | 3.103 [1.779, 5.413] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.381, 0.767] | 4.885 [3.033, 7.517] | 2.202 [1.315, 3.609] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.577 [2.678, 7.261] | 2.115 [1.177, 3.533] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.300, 0.704] | 4.423 [2.529, 7.104] | 2.067 [1.120, 3.536] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.077 [2.285, 6.644] | 2.029 [1.086, 3.527] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 4.192 [2.429, 6.818] | 2.212 [1.240, 3.773] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.000 [4.350, 11.231] | 3.074 [1.795, 5.264] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.667 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.385, 0.778] | 4.808 [3.034, 7.280] | 2.096 [1.229, 3.387] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 4.462 [2.611, 7.000] | 2.058 [1.112, 3.461] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.462 [2.529, 7.063] | 2.058 [1.062, 3.513] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 4.115 [2.391, 6.580] | 1.846 [0.913, 3.219] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.423 [2.514, 7.048] | 2.010 [1.000, 3.514] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.588 [5.000, 11.917] | 3.235 [1.961, 5.375] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 2.889 [1.250, 7.000] | 1.917 [0.633, 5.167] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.389, 0.765] | 4.692 [2.905, 7.319] | 2.029 [1.162, 3.406] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.526] | 4.423 [2.619, 7.083] | 2.019 [1.067, 3.468] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.346 [2.400, 7.143] | 1.942 [0.968, 3.456] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.038 [2.250, 6.647] | 1.817 [0.870, 3.265] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.538 [2.560, 7.401] | 2.096 [1.065, 3.750] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.588 [4.800, 12.102] | 3.235 [1.928, 5.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.222 [0.833, 5.505] | 1.444 [0.400, 4.250] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.384, 0.769] | 4.808 [3.031, 7.308] | 2.096 [1.242, 3.417] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.305, 0.700] | 4.769 [2.905, 7.354] | 2.154 [1.242, 3.511] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.305, 0.700] | 4.423 [2.600, 6.905] | 2.077 [1.152, 3.450] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 3.846 [2.091, 6.278] | 1.894 [0.975, 3.323] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.038 [2.278, 6.534] | 1.990 [1.015, 3.486] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 7.176 [4.533, 11.538] | 2.985 [1.750, 5.091] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.389, 0.774] | 4.692 [2.806, 7.072] | 2.029 [1.145, 3.312] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.304, 0.708] | 4.462 [2.529, 7.000] | 1.990 [1.034, 3.320] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.304, 0.708] | 4.231 [2.294, 6.750] | 1.933 [0.957, 3.294] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.846 [1.971, 6.300] | 1.913 [0.921, 3.369] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 3.846 [2.037, 6.261] | 1.952 [0.969, 3.375] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.059 [4.294, 11.335] | 2.956 [1.661, 4.980] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 2.556 [1.077, 6.000] | 1.778 [0.573, 4.800] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.387, 0.769] | 4.654 [2.818, 7.195] | 2.058 [1.160, 3.367] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 4.500 [2.631, 7.058] | 2.067 [1.086, 3.476] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.423 [2.457, 7.154] | 2.038 [1.050, 3.488] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.567] | 4.000 [2.208, 6.500] | 1.808 [0.870, 3.191] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 4.538 [2.522, 7.333] | 2.125 [1.056, 3.662] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 7.588 [4.874, 11.716] | 3.235 [1.919, 5.304] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 2.444 [0.916, 6.500] | 2.000 [0.609, 5.752] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.371, 0.773] | 4.654 [2.805, 7.150] | 2.058 [1.152, 3.393] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.167, 0.529] | 4.500 [2.551, 7.106] | 2.125 [1.095, 3.583] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.233, 0.615] | 4.308 [2.299, 6.951] | 1.923 [0.901, 3.340] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.038 [2.148, 6.647] | 1.817 [0.828, 3.240] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.233, 0.615] | 4.615 [2.571, 7.412] | 2.173 [1.083, 3.751] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.588 [4.916, 12.143] | 3.235 [1.913, 5.517] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 2.444 [1.000, 6.000] | 1.917 [0.588, 5.322] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.390, 0.774] | 4.654 [2.851, 7.191] | 2.058 [1.179, 3.364] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.303, 0.708] | 4.615 [2.705, 7.283] | 2.115 [1.183, 3.500] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.303, 0.708] | 4.385 [2.562, 6.955] | 2.058 [1.136, 3.465] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 3.846 [2.107, 6.358] | 1.894 [0.984, 3.325] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 4.038 [2.260, 6.651] | 1.990 [1.022, 3.523] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.550, 11.400] | 2.985 [1.704, 5.096] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.333 (no interval) | 1.806 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.381, 0.774] | 4.654 [2.881, 7.002] | 2.058 [1.194, 3.375] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.308, 0.714] | 4.500 [2.655, 7.048] | 2.029 [1.104, 3.445] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.308, 0.714] | 4.346 [2.500, 6.938] | 1.990 [1.045, 3.458] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.885 [2.148, 6.321] | 1.923 [0.974, 3.422] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.962 [2.250, 6.376] | 2.067 [1.095, 3.659] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.059 [4.400, 11.251] | 2.956 [1.726, 5.015] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 2.556 [1.117, 6.337] | 2.028 [0.725, 5.609] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.357, 0.727] | 2.423 [1.680, 3.696] | 1.740 [1.113, 2.830] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.692 [1.031, 2.706] | 1.279 [0.717, 2.203] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.469] | 1.808 [1.130, 2.905] | 1.337 [0.742, 2.317] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.233, 0.552] | 2.231 [1.432, 3.524] | 1.712 [0.992, 2.912] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.387, 3.364] | 1.577 [0.892, 2.704] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 6.778 (no interval) | 6.028 (no interval) |

Recall with equal weight per regime: 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5).

risk_logistic+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.393, 0.750] | 5.346 [3.621, 7.688] | 2.279 [1.458, 3.456] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.885 [3.138, 7.278] | 2.019 [1.218, 3.182] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 4.577 [2.806, 7.050] | 2.019 [1.172, 3.250] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.231 [2.591, 6.500] | 1.846 [1.058, 3.016] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.645] | 4.962 [3.105, 7.530] | 2.202 [1.329, 3.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.548, 0.957] | 7.294 [4.809, 11.091] | 2.868 [1.750, 4.625] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.889 (no interval) | 5.194 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.645] | 3.692 [2.600, 5.185] | 1.788 [1.188, 2.688] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.467] | 3.885 [2.604, 5.653] | 1.596 [1.059, 2.382] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.462] | 3.462 [2.193, 5.250] | 1.577 [0.994, 2.464] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.148, 0.462] | 3.808 [2.589, 5.556] | 1.894 [1.242, 2.881] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 4.423 [2.967, 6.474] | 2.192 [1.484, 3.294] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.765 [4.545, 10.167] | 2.750 [1.815, 4.173] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.333 (no interval) | 6.694 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_logistic+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 4.885 [3.185, 7.313] | 2.154 [1.359, 3.389] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.423 [2.677, 6.875] | 1.827 [1.023, 3.011] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.263, 0.588] | 4.192 [2.500, 6.609] | 1.817 [1.027, 3.034] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.462 [2.724, 6.833] | 2.077 [1.180, 3.348] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.640] | 5.192 [3.269, 7.813] | 2.337 [1.417, 3.640] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.118 [5.350, 12.502] | 3.471 [2.083, 5.700] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.167, 0.728] | 5.444 [3.000, 11.432] | 3.250 [1.678, 7.500] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.394, 0.759] | 5.308 [3.600, 7.707] | 2.269 [1.464, 3.517] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.808 [3.074, 7.308] | 1.990 [1.210, 3.177] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 4.423 [2.708, 6.920] | 1.942 [1.155, 3.217] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 4.077 [2.444, 6.417] | 1.760 [1.000, 2.914] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.846 [3.000, 7.455] | 2.125 [1.278, 3.386] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.294 [4.759, 11.417] | 2.868 [1.714, 4.806] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.000 (no interval) | 4.639 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.759] | 4.769 [3.100, 7.150] | 2.163 [1.361, 3.395] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.645] | 5.154 [3.416, 7.685] | 2.240 [1.389, 3.513] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 4.231 [2.526, 6.706] | 1.875 [1.080, 3.111] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.346 [2.730, 6.750] | 1.971 [1.190, 3.183] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.192 [3.323, 7.819] | 2.356 [1.483, 3.713] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.176 [4.571, 11.335] | 2.912 [1.687, 4.979] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.250, 0.833] | 8.222 [5.143, 16.200] | 5.056 [2.917, 11.375] |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_logistic+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 4.846 [3.000, 7.400] | 2.077 [1.202, 3.310] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.231 [2.517, 6.600] | 1.750 [0.961, 2.833] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.524] | 3.846 [2.182, 6.087] | 1.683 [0.898, 2.792] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 3.423 [1.903, 5.563] | 1.567 [0.817, 2.625] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.480, 7.263] | 2.144 [1.104, 3.698] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.529 [4.904, 11.468] | 3.029 [1.783, 5.001] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.667 [1.538, 9.000] | 2.778 [1.050, 7.127] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 4.692 [2.842, 7.114] | 2.038 [1.134, 3.250] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 4.692 [2.788, 7.273] | 2.048 [1.092, 3.388] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.654 [1.938, 5.870] | 1.490 [0.741, 2.531] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.467] | 3.000 [1.478, 5.000] | 1.279 [0.571, 2.296] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.610] | 4.615 [2.643, 7.353] | 2.231 [1.169, 3.804] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.471 [4.761, 11.701] | 3.059 [1.750, 5.100] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 4.846 [3.000, 7.392] | 2.077 [1.215, 3.369] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.062, 0.350] | 3.654 [1.909, 6.120] | 1.712 [0.842, 3.024] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.519] | 4.000 [2.383, 6.312] | 2.000 [1.120, 3.280] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.594] | 3.731 [2.125, 5.890] | 1.567 [0.847, 2.618] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.571] | 3.346 [1.815, 5.500] | 1.481 [0.760, 2.548] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 8.000 [5.300, 12.154] | 3.485 [2.150, 5.667] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 2.667 [1.200, 6.200] | 1.972 [0.750, 5.000] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.654] | 4.692 [2.897, 7.168] | 2.038 [1.156, 3.338] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.171, 0.542] | 4.154 [2.280, 6.714] | 1.856 [0.954, 3.199] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.484] | 3.346 [1.784, 5.501] | 1.558 [0.800, 2.685] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.560] | 3.769 [2.045, 6.188] | 1.808 [0.907, 3.185] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.077 [1.500, 5.167] | 1.413 [0.669, 2.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.941 [4.333, 10.714] | 2.838 [1.658, 4.626] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.626] | 3.222 [1.583, 8.000] | 2.389 [1.019, 6.375] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.316, 0.677] | 5.308 [3.485, 7.965] | 2.394 [1.500, 3.772] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.385 [2.625, 6.826] | 1.808 [1.026, 2.955] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 3.885 [2.160, 6.227] | 1.702 [0.930, 2.863] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.516] | 3.423 [1.904, 5.615] | 1.558 [0.823, 2.714] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.154 [2.357, 6.656] | 1.817 [1.030, 3.046] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.471 [4.956, 11.600] | 2.971 [1.819, 5.036] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.889 [2.667, 10.000] | 3.361 [1.670, 7.458] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.682] | 4.615 [2.926, 7.091] | 2.010 [1.194, 3.211] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.308 [2.566, 6.875] | 1.760 [0.987, 2.926] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.654 [2.000, 6.096] | 1.500 [0.757, 2.613] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.471] | 3.346 [1.769, 5.537] | 1.481 [0.741, 2.605] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.808 [2.788, 7.667] | 2.337 [1.250, 3.941] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 7.471 [4.800, 11.668] | 3.059 [1.793, 5.135] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.222 [2.733, 11.750] | 3.694 [1.704, 9.064] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.682] | 5.308 [3.444, 7.900] | 2.394 [1.477, 3.765] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.424] | 4.077 [2.304, 6.526] | 2.029 [1.090, 3.382] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.187, 0.517] | 3.808 [2.161, 6.000] | 1.846 [0.989, 3.115] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.632] | 4.115 [2.444, 6.421] | 1.808 [1.050, 2.925] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.226, 0.562] | 3.731 [2.107, 5.959] | 1.721 [0.944, 2.869] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.000 [5.348, 12.126] | 3.485 [2.150, 5.635] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.444 [2.453, 10.000] | 2.889 [1.479, 7.002] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.310, 0.682] | 4.615 [2.879, 6.948] | 2.010 [1.208, 3.147] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.200, 0.565] | 4.577 [2.636, 7.174] | 2.154 [1.192, 3.524] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.476] | 3.077 [1.529, 5.168] | 1.375 [0.653, 2.417] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 4.115 [2.333, 6.524] | 2.010 [1.078, 3.395] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 3.385 [1.818, 5.524] | 1.577 [0.815, 2.663] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.941 [4.263, 10.909] | 2.838 [1.631, 4.767] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 4.556 [2.417, 9.667] | 2.944 [1.386, 6.941] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.654] | 5.769 [3.773, 8.612] | 2.615 [1.619, 4.066] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 4.385 [2.703, 6.840] | 1.865 [1.106, 3.070] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.531] | 3.808 [2.100, 6.251] | 1.663 [0.884, 2.888] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.471] | 4.000 [2.350, 6.429] | 1.942 [1.076, 3.231] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.611] | 5.154 [3.200, 7.952] | 2.548 [1.478, 4.133] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 9.059 [6.278, 13.200] | 3.941 [2.548, 6.058] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 2.250 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.658] | 4.962 [3.161, 7.429] | 2.135 [1.259, 3.393] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.586] | 4.885 [3.042, 7.558] | 2.173 [1.260, 3.542] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.538] | 3.577 [1.958, 5.833] | 1.433 [0.717, 2.500] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.467] | 3.769 [2.151, 6.074] | 1.760 [0.907, 2.964] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.577 [2.615, 7.375] | 2.192 [1.115, 3.737] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 8.588 [5.786, 12.728] | 3.765 [2.327, 5.922] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 2.667 [0.941, 6.400] | 2.056 [0.614, 5.252] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.652] | 5.769 [3.680, 8.391] | 2.615 [1.530, 4.012] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.091, 0.400] | 3.654 [1.965, 6.000] | 1.779 [0.909, 3.026] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.520] | 3.885 [2.194, 6.106] | 1.962 [1.058, 3.177] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.731 [2.130, 5.941] | 1.567 [0.826, 2.570] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.846 [2.941, 7.410] | 2.183 [1.217, 3.625] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.647 [5.750, 13.000] | 3.735 [2.304, 5.964] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.889 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.655] | 4.962 [3.132, 7.485] | 2.135 [1.240, 3.434] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.167, 0.538] | 4.192 [2.343, 6.721] | 1.904 [0.961, 3.263] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.478] | 3.154 [1.610, 5.333] | 1.490 [0.716, 2.645] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 3.808 [2.064, 6.239] | 1.817 [0.875, 3.188] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 3.615 [1.833, 6.106] | 1.788 [0.833, 3.239] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 7.176 [4.636, 11.317] | 2.941 [1.731, 4.975] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 2.000 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 6.192 [4.133, 9.111] | 2.923 [1.845, 4.397] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 4.346 [2.600, 6.721] | 1.856 [1.055, 2.944] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.210, 0.572] | 3.808 [2.107, 6.185] | 1.683 [0.894, 2.730] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 3.962 [2.241, 6.276] | 1.923 [1.028, 3.173] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.244, 0.621] | 5.154 [3.047, 8.002] | 2.548 [1.416, 4.118] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 9.059 [6.316, 13.563] | 3.941 [2.531, 6.208] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 3.333 [1.384, 8.000] | 2.861 [1.083, 7.375] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.314, 0.680] | 4.654 [2.999, 6.944] | 2.048 [1.271, 3.159] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.385 [2.528, 6.793] | 1.846 [1.066, 2.927] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.654 [1.926, 5.858] | 1.500 [0.741, 2.550] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.152, 0.474] | 3.885 [2.165, 6.167] | 1.846 [0.991, 3.103] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 4.577 [2.535, 7.250] | 2.192 [1.112, 3.705] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.588 [5.727, 12.717] | 3.765 [2.338, 5.947] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 2.750 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.682] | 6.192 [4.071, 8.945] | 2.923 [1.830, 4.387] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.114, 0.438] | 3.808 [2.074, 6.139] | 1.904 [0.985, 3.230] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 3.769 [2.161, 5.870] | 1.837 [0.983, 3.047] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.632] | 3.846 [2.200, 6.000] | 1.654 [0.914, 2.672] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.636] | 5.000 [3.035, 7.578] | 2.337 [1.327, 3.792] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.647 [5.857, 13.077] | 3.735 [2.347, 6.001] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 2.889 [1.214, 6.505] | 2.333 [0.857, 5.667] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.692] | 4.654 [2.963, 6.905] | 2.048 [1.257, 3.213] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 4.346 [2.423, 6.917] | 2.058 [1.089, 3.438] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.474] | 3.038 [1.513, 5.092] | 1.365 [0.643, 2.400] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.552] | 3.885 [2.111, 6.321] | 1.894 [0.950, 3.260] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.500] | 3.692 [1.882, 6.227] | 1.837 [0.854, 3.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 7.176 [4.588, 11.300] | 2.941 [1.716, 4.932] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.714] | 2.308 [1.515, 3.625] | 1.654 [0.984, 2.776] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.469] | 1.692 [1.000, 2.789] | 1.221 [0.643, 2.175] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.577 [0.880, 2.640] | 1.163 [0.571, 2.121] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.423 [0.771, 2.381] | 1.010 [0.449, 1.889] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.962 [1.192, 3.211] | 1.471 [0.801, 2.617] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.556 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

risk_logistic_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.242, 0.609] | 4.577 [2.808, 6.901] | 1.971 [1.159, 3.072] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.808 [3.059, 7.143] | 1.962 [1.188, 3.018] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.615 [2.846, 7.000] | 2.000 [1.192, 3.179] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.192 [2.588, 6.476] | 1.885 [1.077, 2.989] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.647] | 5.038 [3.190, 7.524] | 2.260 [1.386, 3.486] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.818, 10.167] | 2.574 [1.379, 4.334] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 8.444 (no interval) | 4.750 (no interval) |

Recall with equal weight per regime: 0.372 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.684] | 4.077 [2.931, 5.864] | 2.010 [1.393, 3.060] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.846 [2.566, 5.778] | 1.558 [1.045, 2.364] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 3.615 [2.306, 5.714] | 1.673 [1.040, 2.750] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.654 [2.472, 5.476] | 1.712 [1.121, 2.650] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.316, 0.679] | 4.115 [2.750, 6.200] | 1.913 [1.284, 2.929] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.765 [4.500, 10.252] | 2.750 [1.787, 4.251] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.444 (no interval) | 6.722 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.682] | 4.500 [2.763, 6.819] | 1.856 [1.095, 2.950] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 4.346 [2.631, 6.765] | 1.769 [1.023, 2.881] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 4.192 [2.500, 6.593] | 1.788 [1.029, 2.947] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.538 [2.800, 6.955] | 2.144 [1.250, 3.429] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.643] | 5.115 [3.320, 7.637] | 2.308 [1.424, 3.588] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.059 [5.524, 12.250] | 3.441 [2.180, 5.500] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 2.389 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.538 [2.821, 6.906] | 1.962 [1.166, 3.076] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.731 [2.968, 7.095] | 1.933 [1.160, 3.033] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 4.462 [2.666, 6.923] | 1.923 [1.088, 3.073] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 4.077 [2.387, 6.369] | 1.808 [0.992, 2.950] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 4.923 [3.038, 7.455] | 2.183 [1.276, 3.409] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 6.471 [3.846, 10.067] | 2.574 [1.389, 4.263] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 7.556 (no interval) | 4.194 (no interval) |

Recall with equal weight per regime: 0.372 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 5.077 [3.393, 7.634] | 2.269 [1.458, 3.603] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 5.038 [3.316, 7.641] | 2.125 [1.345, 3.364] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 4.577 [2.871, 7.182] | 1.990 [1.191, 3.283] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 4.385 [2.727, 6.813] | 2.010 [1.183, 3.243] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.633] | 5.000 [3.185, 7.765] | 2.337 [1.463, 3.695] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 0.952] | 7.059 [4.474, 11.000] | 2.868 [1.690, 4.717] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.333 (no interval) | 4.972 (no interval) |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.172, 0.542] | 4.077 [2.222, 6.572] | 1.769 [0.881, 2.987] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.211, 0.579] | 4.808 [2.889, 7.539] | 2.077 [1.120, 3.438] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.579] | 3.923 [2.228, 6.317] | 1.673 [0.889, 2.802] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.528] | 3.846 [2.031, 6.336] | 1.942 [0.949, 3.392] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.576] | 4.500 [2.500, 7.226] | 2.115 [1.097, 3.609] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.824] | 6.706 [4.042, 10.801] | 2.735 [1.483, 4.667] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.167 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 3.808 [2.135, 6.273] | 1.692 [0.846, 2.990] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.962 [3.097, 7.714] | 2.096 [1.173, 3.542] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.257, 0.619] | 3.962 [2.281, 6.410] | 1.663 [0.900, 2.828] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.538] | 3.462 [1.916, 5.741] | 1.519 [0.790, 2.642] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.545] | 3.923 [2.207, 6.421] | 1.702 [0.898, 2.908] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.929] | 6.941 [4.408, 11.202] | 2.838 [1.619, 4.904] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.111 (no interval) | 2.556 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 4.077 [2.237, 6.602] | 1.769 [0.905, 3.029] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.438] | 4.077 [2.310, 6.460] | 1.933 [1.019, 3.250] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 3.731 [2.190, 6.000] | 1.760 [1.009, 2.945] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.320, 0.682] | 4.077 [2.286, 6.579] | 2.010 [1.067, 3.355] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.885 [2.136, 6.286] | 1.952 [0.965, 3.367] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.353 [3.762, 10.385] | 2.662 [1.473, 4.641] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.444 (no interval) | 2.472 (no interval) |

Recall with equal weight per regime: 0.416 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.212, 0.560] | 3.808 [2.080, 6.104] | 1.692 [0.836, 2.869] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.640] | 5.192 [3.281, 7.850] | 2.317 [1.348, 3.671] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 3.346 [1.806, 5.500] | 1.558 [0.821, 2.706] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 4.346 [2.516, 6.926] | 2.163 [1.162, 3.644] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.526] | 3.808 [2.000, 6.296] | 1.923 [0.922, 3.375] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 7.176 [4.600, 11.143] | 2.971 [1.784, 4.876] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.778 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 4.115 [2.351, 6.458] | 1.731 [0.928, 2.813] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.607] | 4.885 [2.875, 7.550] | 2.135 [1.135, 3.529] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.618] | 3.885 [2.083, 6.263] | 1.673 [0.851, 2.767] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.615 [2.000, 5.957] | 1.673 [0.869, 2.834] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.154 [2.333, 6.601] | 1.788 [0.956, 2.917] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.833] | 6.706 [3.879, 10.934] | 2.735 [1.428, 4.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 2.944 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 3.846 [2.259, 6.000] | 1.683 [0.933, 2.763] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.600] | 4.308 [2.525, 6.667] | 1.663 [0.910, 2.761] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.692 [1.969, 6.000] | 1.481 [0.722, 2.558] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.522] | 3.423 [1.829, 5.501] | 1.500 [0.771, 2.584] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.167, 0.533] | 4.231 [2.429, 6.682] | 1.904 [1.075, 3.071] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.706 [4.042, 10.734] | 2.706 [1.518, 4.617] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.333 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.115 [2.400, 6.643] | 1.731 [0.969, 2.914] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.194, 0.517] | 3.462 [1.893, 5.778] | 1.538 [0.800, 2.663] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.292, 0.643] | 3.615 [2.083, 5.880] | 1.635 [0.906, 2.766] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 4.385 [2.615, 7.000] | 2.144 [1.219, 3.607] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 3.500 [1.952, 5.808] | 1.635 [0.875, 2.811] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.353 [3.769, 10.463] | 2.662 [1.461, 4.584] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.444 (no interval) | 2.667 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.846 [2.231, 6.106] | 1.683 [0.904, 2.751] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.333, 0.686] | 4.577 [2.815, 6.875] | 1.923 [1.132, 3.046] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.174, 0.545] | 3.115 [1.545, 5.381] | 1.385 [0.643, 2.409] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.385 [2.500, 6.900] | 2.163 [1.150, 3.633] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.538] | 3.538 [1.882, 5.822] | 1.702 [0.896, 2.875] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.929] | 7.176 [4.391, 11.273] | 2.971 [1.710, 4.917] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 4.444 [2.400, 9.202] | 2.667 [1.271, 6.250] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.280, 0.654] | 5.385 [3.360, 8.158] | 2.452 [1.422, 3.882] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.207, 0.583] | 5.038 [3.073, 7.770] | 2.212 [1.234, 3.579] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.583] | 3.885 [2.160, 6.263] | 1.654 [0.850, 2.750] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.575] | 4.615 [2.647, 7.333] | 2.394 [1.287, 3.953] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 4.500 [2.499, 7.240] | 2.115 [1.080, 3.588] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.941 [6.148, 13.333] | 3.897 [2.444, 6.058] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 2.444 [0.875, 6.008] | 1.917 [0.558, 5.100] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.567] | 4.923 [3.087, 7.333] | 2.260 [1.292, 3.522] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.962 [3.079, 7.542] | 2.135 [1.204, 3.435] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 3.885 [2.200, 6.161] | 1.635 [0.848, 2.738] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.567] | 4.077 [2.444, 6.303] | 1.904 [1.055, 3.037] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.533] | 3.962 [2.266, 6.306] | 1.712 [0.911, 2.868] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.706 [6.000, 13.000] | 3.779 [2.368, 5.900] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.889 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.645] | 5.385 [3.409, 8.200] | 2.452 [1.408, 3.955] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 4.615 [2.778, 7.228] | 2.135 [1.208, 3.563] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.258, 0.600] | 3.615 [2.105, 5.883] | 1.702 [0.935, 2.917] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 4.115 [2.367, 6.620] | 2.000 [1.060, 3.376] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.478] | 3.846 [2.103, 6.364] | 1.933 [0.969, 3.419] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 8.059 [5.312, 12.636] | 3.544 [2.144, 5.834] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.444 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.923 [3.000, 7.522] | 2.260 [1.258, 3.603] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 5.115 [3.159, 7.833] | 2.279 [1.326, 3.650] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.481] | 3.154 [1.583, 5.552] | 1.462 [0.682, 2.683] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.192 [2.423, 6.852] | 2.067 [1.103, 3.531] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.167, 0.533] | 3.577 [1.838, 6.131] | 1.750 [0.808, 3.193] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.118 [5.235, 12.447] | 3.559 [2.156, 5.750] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.778 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.281, 0.650] | 5.654 [3.565, 8.208] | 2.606 [1.559, 3.950] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 4.923 [3.000, 7.546] | 2.212 [1.273, 3.587] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.846 [2.193, 6.177] | 1.635 [0.847, 2.766] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.593] | 4.154 [2.400, 6.391] | 2.038 [1.131, 3.269] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.562] | 4.462 [2.593, 7.134] | 2.077 [1.115, 3.531] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 8.941 [6.000, 13.154] | 3.897 [2.409, 6.000] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 5.154 [3.321, 7.750] | 2.462 [1.484, 3.931] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 4.808 [2.931, 7.566] | 2.096 [1.198, 3.424] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.616] | 3.692 [2.000, 6.101] | 1.481 [0.750, 2.552] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.567] | 4.000 [2.343, 6.407] | 1.885 [1.046, 3.120] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.546] | 3.923 [2.194, 6.389] | 1.673 [0.879, 2.869] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 8.706 [5.938, 13.223] | 3.779 [2.385, 6.025] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.444 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 5.654 [3.559, 8.280] | 2.606 [1.535, 4.015] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.636] | 4.115 [2.458, 6.450] | 1.808 [1.026, 2.948] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.593] | 3.538 [2.000, 5.667] | 1.615 [0.875, 2.708] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 4.231 [2.448, 6.708] | 2.058 [1.101, 3.426] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.481] | 3.269 [1.756, 5.474] | 1.490 [0.741, 2.611] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.059 [5.071, 12.154] | 3.544 [2.015, 5.656] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 2.111 [0.800, 5.000] | 1.639 [0.500, 4.250] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 5.154 [3.200, 7.760] | 2.462 [1.399, 3.938] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.333, 0.679] | 4.769 [2.903, 7.311] | 2.067 [1.200, 3.307] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.150, 0.472] | 3.077 [1.543, 5.273] | 1.375 [0.646, 2.462] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 4.154 [2.332, 6.751] | 2.048 [1.062, 3.488] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 3.731 [1.968, 6.365] | 1.875 [0.885, 3.320] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.118 [5.200, 12.432] | 3.559 [2.102, 5.825] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.222 (no interval) | 1.667 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.360, 0.719] | 2.692 [1.743, 4.250] | 2.048 [1.194, 3.531] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.517] | 2.462 [1.631, 3.812] | 1.846 [1.093, 3.150] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.423 [1.600, 3.833] | 1.846 [1.106, 3.150] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 3.423 [2.286, 5.438] | 2.846 [1.793, 4.812] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.136, 0.429] | 2.500 [1.613, 4.063] | 2.010 [1.161, 3.476] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 1.412 [0.833, 2.400] | 0.706 [0.352, 1.375] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 12.000 (no interval) | 11.250 (no interval) |

Recall with equal weight per regime: 0.382 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

risk_quantile_skewt_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.391, 0.750] | 2.308 [1.517, 3.625] | 1.615 [0.942, 2.803] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 2.000 [1.243, 3.214] | 1.442 [0.774, 2.534] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 1.500 [0.900, 2.400] | 1.000 [0.500, 1.781] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.719, 1.667] | 0.558 [0.286, 0.991] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.294 [0.731, 2.091] | 0.529 [0.250, 0.969] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.889 (no interval) | 5.194 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

risk_quantile_skewt_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.758] | 4.846 [3.153, 7.292] | 2.231 [1.396, 3.459] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 4.269 [2.806, 6.391] | 1.587 [1.043, 2.381] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.679] | 5.615 [3.652, 8.500] | 2.635 [1.603, 4.195] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.643] | 4.577 [2.967, 7.002] | 2.048 [1.266, 3.251] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 5.231 [3.428, 7.858] | 2.365 [1.500, 3.671] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 7.118 [4.416, 11.182] | 2.926 [1.703, 4.940] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 10.111 (no interval) | 6.250 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.676] | 3.885 [2.774, 5.696] | 1.865 [1.227, 2.989] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 3.538 [2.285, 5.333] | 1.462 [0.932, 2.271] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.227, 0.536] | 3.654 [2.333, 5.572] | 1.760 [1.099, 2.800] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.542] | 3.846 [2.679, 5.651] | 1.865 [1.250, 2.868] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.321, 0.667] | 4.154 [2.800, 6.177] | 2.000 [1.318, 3.096] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.412 [4.250, 9.900] | 2.500 [1.629, 3.947] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.167, 0.714] | 10.111 [6.498, 21.250] | 6.556 [3.886, 15.381] |

Recall with equal weight per regime: 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 4.846 [3.119, 7.257] | 2.231 [1.410, 3.536] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.423 [2.645, 6.842] | 1.827 [1.040, 2.968] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 5.038 [3.000, 7.924] | 2.404 [1.348, 4.146] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 4.769 [3.031, 7.333] | 2.288 [1.378, 3.688] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.643] | 5.346 [3.405, 8.002] | 2.462 [1.535, 3.909] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.588 [5.812, 13.000] | 3.794 [2.359, 6.146] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.667 (no interval) | 4.528 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.391, 0.750] | 4.808 [3.114, 7.273] | 2.221 [1.370, 3.554] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 4.192 [2.733, 6.263] | 1.558 [1.020, 2.334] |
| lead 3 alone (fail) | 26 | 13 | 0.500 [0.316, 0.677] | 5.462 [3.454, 8.421] | 2.558 [1.490, 4.161] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 4.462 [2.800, 6.812] | 1.971 [1.180, 3.134] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.316, 0.680] | 5.154 [3.348, 7.667] | 2.308 [1.446, 3.632] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 7.118 [4.454, 11.309] | 2.926 [1.658, 4.972] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.222 (no interval) | 5.694 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 17 | 0.654 [0.471, 0.833] | 5.500 [3.791, 8.182] | 2.663 [1.750, 4.260] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.292, 0.652] | 5.308 [3.590, 8.060] | 2.337 [1.520, 3.714] |
| lead 3 alone (fail) | 26 | 14 | 0.538 [0.364, 0.720] | 6.038 [4.062, 9.084] | 3.019 [1.898, 4.844] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.333, 0.677] | 4.885 [3.226, 7.435] | 2.308 [1.470, 3.708] |
| lead 5 alone (fail) | 26 | 14 | 0.538 [0.375, 0.714] | 5.385 [3.531, 8.150] | 2.587 [1.664, 4.047] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 0.963] | 7.353 [4.824, 11.602] | 3.015 [1.809, 5.156] |
| outside 2018-2019 | 9 | 6 | 0.667 [0.333, 0.938] | 11.333 [7.428, 22.752] | 7.444 [4.400, 16.750] |

Recall with equal weight per regime: 0.566 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 5/5).

risk_quantile_skewt_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.688] | 4.269 [2.435, 6.783] | 1.904 [0.990, 3.210] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.618] | 4.500 [2.778, 6.950] | 1.846 [1.081, 3.050] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.308 [2.575, 6.750] | 1.875 [1.083, 3.125] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 4.231 [2.450, 6.824] | 2.125 [1.121, 3.611] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.652] | 4.885 [2.931, 7.685] | 2.356 [1.302, 3.888] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 7.059 [4.478, 11.000] | 2.868 [1.635, 4.797] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 4.333 (no interval) | 3.083 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.680] | 4.846 [3.079, 7.375] | 2.077 [1.210, 3.365] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 4.269 [2.576, 6.769] | 1.740 [0.977, 2.921] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 4.077 [2.360, 6.542] | 1.673 [0.927, 2.812] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.178, 0.524] | 3.769 [2.206, 6.063] | 1.808 [1.022, 2.989] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.609] | 5.038 [3.000, 7.936] | 2.567 [1.448, 4.242] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 7.647 [5.056, 11.901] | 3.118 [1.848, 5.179] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.556 [2.364, 10.500] | 3.472 [1.583, 8.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.682] | 4.269 [2.439, 6.850] | 1.904 [1.015, 3.270] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.962 [2.189, 6.527] | 1.894 [0.981, 3.309] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 3.423 [1.886, 5.700] | 1.625 [0.875, 2.808] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.350, 0.714] | 3.462 [1.964, 5.692] | 1.567 [0.867, 2.679] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.296, 0.639] | 3.231 [1.697, 5.410] | 1.462 [0.740, 2.579] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.412 [3.869, 10.556] | 2.676 [1.477, 4.709] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.889 (no interval) | 2.056 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.680] | 4.846 [2.969, 7.235] | 2.077 [1.189, 3.250] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.300, 0.629] | 4.115 [2.312, 6.500] | 1.952 [1.037, 3.214] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.269, 0.647] | 4.231 [2.499, 6.458] | 1.808 [1.039, 2.852] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.280, 0.636] | 4.192 [2.235, 6.654] | 1.933 [0.969, 3.218] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.364, 0.710] | 3.538 [1.931, 5.652] | 1.635 [0.850, 2.715] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.833, 11.500] | 3.000 [1.807, 4.855] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.601] | 3.222 [1.615, 7.000] | 2.139 [0.807, 5.201] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.682] | 4.385 [2.455, 6.955] | 1.933 [1.008, 3.290] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 4.346 [2.566, 6.843] | 1.788 [0.979, 2.984] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.231 [2.422, 6.750] | 1.837 [1.000, 3.092] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.292, 0.640] | 4.423 [2.600, 7.125] | 2.202 [1.177, 3.833] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 5.115 [3.045, 7.955] | 2.481 [1.380, 4.153] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 7.059 [4.286, 11.250] | 2.868 [1.607, 4.965] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 5.333 [2.889, 11.671] | 3.639 [1.805, 8.833] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.680] | 5.000 [3.200, 7.322] | 2.115 [1.238, 3.357] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.500 [2.789, 6.800] | 1.894 [1.100, 2.976] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.115 [2.357, 6.412] | 1.769 [0.955, 2.860] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.560] | 3.846 [2.281, 6.000] | 1.846 [1.054, 2.986] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 5.269 [3.250, 7.962] | 2.683 [1.529, 4.295] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.647 [5.050, 11.573] | 3.118 [1.854, 4.992] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 5.667 (no interval) | 3.861 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 4.385 [2.585, 6.955] | 1.933 [1.066, 3.182] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 4.231 [2.522, 6.800] | 2.087 [1.176, 3.466] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 3.538 [2.045, 5.808] | 1.702 [0.937, 2.814] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.360, 0.714] | 3.654 [2.172, 5.932] | 1.692 [0.966, 2.800] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.565] | 3.077 [1.591, 5.279] | 1.365 [0.667, 2.408] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.555, 1.000] | 6.412 [3.947, 10.333] | 2.676 [1.523, 4.698] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.000 (no interval) | 2.556 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.316, 0.680] | 5.000 [3.218, 7.572] | 2.115 [1.250, 3.334] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 3.615 [2.030, 5.858] | 1.654 [0.917, 2.760] |
| lead 3 alone (pass) | 26 | 14 | 0.538 [0.364, 0.714] | 4.385 [2.619, 6.750] | 1.923 [1.143, 3.053] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.323, 0.679] | 4.731 [2.828, 7.421] | 2.356 [1.354, 3.875] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.367, 0.715] | 3.846 [2.270, 6.106] | 1.827 [1.038, 3.026] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.412 [4.833, 11.728] | 3.000 [1.819, 5.026] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.333 (no interval) | 3.639 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 5.692 [3.667, 8.317] | 2.606 [1.562, 4.056] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 3.538 [2.136, 5.381] | 1.337 [0.810, 2.046] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.269 [2.560, 6.709] | 1.865 [1.070, 3.072] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.583] | 4.962 [3.032, 7.594] | 2.567 [1.461, 4.238] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.281, 0.636] | 4.846 [2.939, 7.579] | 2.337 [1.310, 3.888] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 8.941 [6.066, 13.401] | 3.897 [2.410, 6.167] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 3.889 [1.857, 8.842] | 2.639 [1.135, 6.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.310, 0.679] | 5.923 [3.913, 8.501] | 2.644 [1.616, 3.990] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 4.577 [2.806, 6.846] | 1.894 [1.087, 2.900] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.572] | 3.769 [2.050, 6.000] | 1.548 [0.776, 2.534] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.167, 0.524] | 4.654 [2.880, 6.876] | 2.298 [1.348, 3.539] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.572] | 4.769 [2.778, 7.502] | 2.337 [1.262, 3.925] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 9.059 [6.166, 13.267] | 3.971 [2.486, 6.160] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 4.333 [2.100, 10.000] | 3.167 [1.386, 8.000] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.312, 0.680] | 5.692 [3.695, 8.250] | 2.606 [1.559, 4.022] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.647] | 3.846 [2.066, 6.182] | 1.865 [0.939, 3.143] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.606] | 3.462 [1.857, 5.592] | 1.663 [0.850, 2.816] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.348, 0.714] | 3.423 [1.866, 5.462] | 1.529 [0.807, 2.553] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 3.038 [1.529, 5.045] | 1.356 [0.639, 2.353] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 0.960] | 8.000 [5.142, 12.095] | 3.529 [2.087, 5.784] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.806 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.688] | 5.923 [3.925, 8.601] | 2.644 [1.599, 4.019] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 4.077 [2.233, 6.438] | 1.933 [1.015, 3.134] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 4.500 [2.842, 6.889] | 1.913 [1.148, 3.021] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.278, 0.654] | 4.154 [2.214, 6.616] | 1.913 [0.952, 3.177] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 3.692 [2.088, 5.834] | 1.692 [0.900, 2.786] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 8.706 [5.889, 12.688] | 3.750 [2.344, 5.834] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.688] | 5.538 [3.500, 8.212] | 2.567 [1.510, 4.014] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 4.423 [2.648, 6.870] | 1.885 [1.083, 3.022] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 4.077 [2.303, 6.500] | 1.712 [0.917, 2.869] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.290, 0.643] | 4.885 [2.880, 7.600] | 2.548 [1.388, 4.190] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 4.846 [2.799, 7.700] | 2.317 [1.217, 3.977] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 8.941 [5.879, 13.572] | 3.897 [2.382, 6.296] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.889 (no interval) | 2.306 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 5.846 [3.937, 8.515] | 2.625 [1.630, 4.023] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.577 [2.862, 6.950] | 1.990 [1.202, 3.110] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.212, 0.583] | 3.731 [2.061, 6.002] | 1.529 [0.800, 2.596] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 4.538 [2.846, 6.792] | 2.260 [1.346, 3.510] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.962 [3.000, 7.643] | 2.510 [1.443, 4.125] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 9.059 [6.133, 13.314] | 3.971 [2.517, 6.137] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 3.444 [1.625, 8.333] | 2.833 [1.156, 7.352] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.682] | 5.538 [3.441, 8.042] | 2.567 [1.500, 3.897] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 4.000 [2.206, 6.348] | 2.019 [1.083, 3.376] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 3.462 [1.875, 5.539] | 1.654 [0.875, 2.772] |
| lead 4 alone (pass) | 26 | 14 | 0.538 [0.355, 0.714] | 3.423 [1.826, 5.446] | 1.548 [0.817, 2.587] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.115 [1.512, 5.133] | 1.375 [0.661, 2.355] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 8.000 [5.176, 12.224] | 3.529 [2.113, 5.823] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 2.444 [1.083, 5.667] | 1.889 [0.672, 4.834] |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.320, 0.679] | 5.846 [3.928, 8.530] | 2.625 [1.630, 4.031] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.323, 0.667] | 3.423 [1.848, 5.667] | 1.538 [0.824, 2.672] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.316, 0.682] | 4.500 [2.821, 7.000] | 1.933 [1.163, 3.112] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.321, 0.667] | 4.462 [2.556, 7.182] | 2.221 [1.239, 3.789] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.333, 0.667] | 3.692 [2.129, 6.000] | 1.692 [0.926, 2.885] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 8.706 [6.000, 13.183] | 3.750 [2.381, 6.045] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.000 (no interval) | 2.444 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+every_day | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.66 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+gate | 0.57 (102) | 0.25 (4) | – | 0.20 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.59 (102) | 0.50 (4) | – | 0.00 (5) | 0.69 (29) | 0.82 (17) | 0.54 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+persist | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.76 (17) | 0.65 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+every_day+scarce | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.66 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+every_day+shrunk | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.63 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+hurdle_isotonic | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_isotonic+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_isotonic+settle | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_isotonic+settle+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.76 (17) | 0.60 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt+settle | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.76 (17) | 0.60 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_platt+settle+h41 | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_isotonic | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.59 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_isotonic+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.59 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_isotonic+settle | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.59 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.59 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_platt | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.59 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_platt+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.59 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_platt+settle | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.76 (17) | 0.59 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm+hurdle_state_platt+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.59 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base+every_day | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.67 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+gate | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.53 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+persist | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.65 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+scarce | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.82 (17) | 0.67 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+shrunk | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.64 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.58 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.71 (17) | 0.60 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.60 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.59 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.59 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+settle | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.59 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.59 (101) | 0.44 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.76 (17) | 0.70 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+gate | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.76 (17) | 0.51 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+persist | 0.76 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.71 (17) | 0.65 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+scarce | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.76 (17) | 0.70 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+shrunk | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.71 (17) | 0.61 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_isotonic | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.53 (17) | 0.60 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_isotonic+h41 | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.65 (17) | 0.61 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_isotonic+settle | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.53 (17) | 0.60 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_isotonic+settle+h41 | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.65 (17) | 0.61 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.63 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt+h41 | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.63 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt+settle | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.63 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt+settle+h41 | 0.77 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.63 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.53 (17) | 0.64 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+h41 | 0.78 (102) | 0.25 (4) | – | 0.20 (5) | 0.21 (29) | 0.65 (17) | 0.63 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+settle | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.53 (17) | 0.64 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 0.78 (102) | 0.25 (4) | – | 0.20 (5) | 0.21 (29) | 0.65 (17) | 0.63 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_platt | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.65 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_platt+h41 | 0.78 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.62 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_platt+settle | 0.81 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.65 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_platt+settle+h41 | 0.78 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.71 (17) | 0.62 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day | 0.69 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.76 (17) | 0.61 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+gate | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.76 (29) | 0.88 (17) | 0.56 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+persist | 0.70 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.56 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+scarce | 0.69 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.76 (17) | 0.61 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+shrunk | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.64 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_isotonic | 0.69 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.47 (17) | 0.51 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_isotonic+h41 | 0.67 (102) | 0.00 (4) | – | 0.00 (5) | 0.21 (29) | 0.71 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_isotonic+settle | 0.69 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.47 (17) | 0.51 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 0.67 (102) | 0.00 (4) | – | 0.00 (5) | 0.21 (29) | 0.71 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt | 0.69 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.55 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_platt+h41 | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.51 (101) | 0.78 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+settle | 0.69 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.55 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_platt+settle+h41 | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.51 (101) | 0.78 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic | 0.74 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.59 (17) | 0.54 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 0.67 (102) | 0.00 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.50 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle | 0.74 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.59 (17) | 0.54 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 0.67 (102) | 0.00 (4) | – | 0.00 (5) | 0.24 (29) | 0.71 (17) | 0.50 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.76 (17) | 0.56 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt+h41 | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.71 (17) | 0.50 (101) | 0.78 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt+settle | 0.74 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.76 (17) | 0.56 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.71 (17) | 0.50 (101) | 0.78 (9) | 0.62 (13) |
| risk_quantile_skewt | 0.29 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.77 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |
| risk_quantile_skewt_base+every_day | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.76 (17) | 0.63 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+gate | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.69 (29) | 0.88 (17) | 0.54 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+persist | 0.69 (102) | 0.25 (4) | – | 0.20 (5) | 0.52 (29) | 0.71 (17) | 0.59 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+scarce | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.76 (17) | 0.63 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day+shrunk | 0.73 (102) | 0.25 (4) | – | 0.20 (5) | 0.62 (29) | 0.76 (17) | 0.65 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+hurdle_isotonic | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.56 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.60 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.56 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.60 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.58 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.62 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.58 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 0.75 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.62 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0.73 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.58 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 0.79 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.65 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 0.73 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.58 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 0.79 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.65 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt | 0.73 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.57 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 0.79 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.64 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 0.73 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.57 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 0.79 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.76 (17) | 0.64 (101) | 0.67 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+every_day | +0.0573 [+0.0304, +0.0862] | +0.0233 [+0.0097, +0.0348] | +0.0131 [+0.0114, +0.0151] | +0.0006 [-0.0060, +0.0056] | +0.0275 [+0.0002, +0.0591] | +0.0595 [+0.0357, +0.0870] | +0.0160 [+0.0093, +0.0239] | +0.1155 [+0.0378, +0.1950] | +0.0686 [+0.0421, +0.0963] |
| risk_gbm+every_day+gate | +0.0417 [+0.0143, +0.0703] | +0.0323 [+0.0157, +0.0454] | +0.0136 [+0.0118, +0.0155] | +0.0007 [-0.0068, +0.0057] | +0.0266 [+0.0009, +0.0587] | +0.0600 [+0.0346, +0.0873] | +0.0138 [+0.0076, +0.0208] | +0.1155 [+0.0326, +0.1953] | +0.0686 [+0.0419, +0.0958] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+every_day+gate+settle+h41+iorb | +0.0442 [+0.0158, +0.0733] | +0.0350 [+0.0212, +0.0466] | +0.0136 [+0.0119, +0.0155] | -0.0058 [-0.0174, +0.0034] | +0.0264 [+0.0024, +0.0563] | +0.0595 [+0.0347, +0.0862] | +0.0136 [+0.0073, +0.0208] | +0.1247 [+0.0432, +0.2095] | +0.0689 [+0.0395, +0.0976] |
| risk_gbm+every_day+persist | +0.0498 [+0.0240, +0.0771] | +0.0291 [+0.0201, +0.0387] | +0.0133 [+0.0116, +0.0150] | +0.0027 [-0.0017, +0.0060] | +0.0264 [+0.0028, +0.0561] | +0.0586 [+0.0341, +0.0839] | +0.0154 [+0.0093, +0.0222] | +0.1155 [+0.0375, +0.1956] | +0.0686 [+0.0421, +0.0963] |
| risk_gbm+every_day+scarce | +0.0573 [+0.0292, +0.0859] | +0.0233 [+0.0105, +0.0358] | +0.0135 [+0.0118, +0.0154] | +0.0037 [-0.0002, +0.0066] | +0.0284 [+0.0006, +0.0621] | +0.0595 [+0.0355, +0.0867] | +0.0167 [+0.0098, +0.0240] | +0.1155 [+0.0353, +0.1964] | +0.0686 [+0.0413, +0.0941] |
| risk_gbm+every_day+shrunk | +0.0429 [+0.0257, +0.0603] | +0.0366 [+0.0281, +0.0449] | +0.0136 [+0.0118, +0.0155] | +0.0030 [-0.0012, +0.0062] | +0.0281 [+0.0036, +0.0597] | +0.0572 [+0.0328, +0.0846] | +0.0155 [+0.0111, +0.0202] | +0.1155 [+0.0360, +0.1988] | +0.0686 [+0.0415, +0.0975] |
| risk_gbm+hurdle_isotonic | +0.0131 [-0.0304, +0.0570] | -0.0040 [-0.0240, +0.0127] | +0.0120 [+0.0107, +0.0135] | +0.0025 [-0.0025, +0.0064] | +0.0268 [+0.0013, +0.0566] | +0.0568 [+0.0315, +0.0835] | +0.0012 [-0.0092, +0.0113] | +0.1155 [+0.0346, +0.1936] | +0.0686 [+0.0412, +0.0950] |
| risk_gbm+hurdle_isotonic+h41 | +0.0133 [-0.0301, +0.0543] | -0.0054 [-0.0268, +0.0126] | +0.0120 [+0.0106, +0.0135] | +0.0003 [-0.0060, +0.0050] | +0.0287 [+0.0051, +0.0574] | +0.0563 [+0.0334, +0.0804] | +0.0009 [-0.0095, +0.0109] | +0.1247 [+0.0355, +0.2028] | +0.0689 [+0.0401, +0.0975] |
| risk_gbm+hurdle_isotonic+settle | +0.0131 [-0.0284, +0.0549] | -0.0040 [-0.0226, +0.0126] | +0.0120 [+0.0105, +0.0134] | +0.0025 [-0.0025, +0.0064] | +0.0268 [+0.0030, +0.0587] | +0.0568 [+0.0329, +0.0841] | +0.0012 [-0.0087, +0.0115] | +0.1155 [+0.0351, +0.1989] | +0.0686 [+0.0417, +0.0961] |
| risk_gbm+hurdle_isotonic+settle+h41 | +0.0133 [-0.0292, +0.0558] | -0.0054 [-0.0262, +0.0109] | +0.0120 [+0.0106, +0.0135] | +0.0003 [-0.0054, +0.0050] | +0.0287 [+0.0049, +0.0601] | +0.0563 [+0.0321, +0.0818] | +0.0009 [-0.0095, +0.0113] | +0.1247 [+0.0397, +0.2077] | +0.0689 [+0.0400, +0.0982] |
| risk_gbm+hurdle_platt | +0.0391 [+0.0075, +0.0714] | -0.0020 [-0.0137, +0.0099] | +0.0103 [+0.0086, +0.0119] | +0.0026 [-0.0022, +0.0065] | +0.0247 [+0.0015, +0.0539] | +0.0561 [+0.0318, +0.0827] | +0.0066 [-0.0009, +0.0146] | +0.1155 [+0.0345, +0.1949] | +0.0686 [+0.0402, +0.0966] |
| risk_gbm+hurdle_platt+h41 | +0.0393 [+0.0063, +0.0741] | -0.0034 [-0.0161, +0.0082] | +0.0103 [+0.0087, +0.0120] | +0.0003 [-0.0055, +0.0051] | +0.0266 [+0.0041, +0.0537] | +0.0556 [+0.0327, +0.0812] | +0.0062 [-0.0013, +0.0143] | +0.1247 [+0.0412, +0.2055] | +0.0689 [+0.0391, +0.0975] |
| risk_gbm+hurdle_platt+settle | +0.0391 [+0.0085, +0.0728] | -0.0020 [-0.0133, +0.0092] | +0.0103 [+0.0087, +0.0118] | +0.0026 [-0.0025, +0.0066] | +0.0247 [+0.0021, +0.0541] | +0.0561 [+0.0325, +0.0806] | +0.0066 [-0.0007, +0.0148] | +0.1155 [+0.0340, +0.1947] | +0.0686 [+0.0412, +0.0969] |
| risk_gbm+hurdle_platt+settle+h41 | +0.0393 [+0.0072, +0.0745] | -0.0034 [-0.0161, +0.0077] | +0.0103 [+0.0088, +0.0119] | +0.0003 [-0.0057, +0.0050] | +0.0266 [+0.0046, +0.0550] | +0.0556 [+0.0332, +0.0799] | +0.0062 [-0.0012, +0.0144] | +0.1247 [+0.0381, +0.2092] | +0.0689 [+0.0398, +0.0971] |
| risk_gbm+hurdle_state_isotonic | +0.0058 [-0.0440, +0.0510] | +0.0115 [-0.0117, +0.0298] | +0.0128 [+0.0112, +0.0145] | +0.0037 [-0.0000, +0.0067] | +0.0229 [+0.0014, +0.0521] | +0.0573 [+0.0322, +0.0838] | +0.0018 [-0.0100, +0.0124] | +0.1155 [+0.0372, +0.1973] | +0.0686 [+0.0409, +0.0959] |
| risk_gbm+hurdle_state_isotonic+h41 | +0.0061 [-0.0406, +0.0508] | +0.0101 [-0.0143, +0.0293] | +0.0128 [+0.0112, +0.0146] | +0.0014 [-0.0038, +0.0054] | +0.0248 [+0.0042, +0.0524] | +0.0569 [+0.0339, +0.0832] | +0.0015 [-0.0105, +0.0120] | +0.1247 [+0.0450, +0.2039] | +0.0689 [+0.0395, +0.0976] |
| risk_gbm+hurdle_state_isotonic+settle | +0.0058 [-0.0429, +0.0510] | +0.0115 [-0.0122, +0.0306] | +0.0128 [+0.0111, +0.0145] | +0.0037 [-0.0003, +0.0067] | +0.0229 [+0.0014, +0.0502] | +0.0573 [+0.0325, +0.0825] | +0.0018 [-0.0101, +0.0122] | +0.1155 [+0.0320, +0.1961] | +0.0686 [+0.0427, +0.0969] |
| risk_gbm+hurdle_state_isotonic+settle+h41 | +0.0061 [-0.0439, +0.0532] | +0.0101 [-0.0149, +0.0296] | +0.0128 [+0.0111, +0.0145] | +0.0014 [-0.0036, +0.0052] | +0.0248 [+0.0036, +0.0528] | +0.0569 [+0.0334, +0.0829] | +0.0015 [-0.0104, +0.0124] | +0.1247 [+0.0424, +0.2057] | +0.0689 [+0.0398, +0.0977] |
| risk_gbm+hurdle_state_platt | +0.0371 [+0.0034, +0.0705] | +0.0112 [-0.0039, +0.0241] | +0.0125 [+0.0110, +0.0142] | +0.0037 [-0.0000, +0.0068] | +0.0261 [+0.0027, +0.0556] | +0.0573 [+0.0338, +0.0828] | +0.0095 [+0.0015, +0.0172] | +0.1155 [+0.0349, +0.1997] | +0.0686 [+0.0411, +0.0981] |
| risk_gbm+hurdle_state_platt+h41 | +0.0374 [+0.0036, +0.0721] | +0.0098 [-0.0062, +0.0242] | +0.0125 [+0.0109, +0.0142] | +0.0014 [-0.0033, +0.0053] | +0.0281 [+0.0048, +0.0562] | +0.0569 [+0.0325, +0.0828] | +0.0092 [+0.0015, +0.0177] | +0.1247 [+0.0409, +0.2097] | +0.0689 [+0.0389, +0.0989] |
| risk_gbm+hurdle_state_platt+settle | +0.0371 [+0.0030, +0.0714] | +0.0112 [-0.0046, +0.0247] | +0.0125 [+0.0110, +0.0141] | +0.0037 [-0.0002, +0.0067] | +0.0261 [+0.0029, +0.0561] | +0.0573 [+0.0332, +0.0822] | +0.0095 [+0.0017, +0.0175] | +0.1155 [+0.0324, +0.2003] | +0.0686 [+0.0424, +0.0952] |
| risk_gbm+hurdle_state_platt+settle+h41 | +0.0374 [+0.0029, +0.0721] | +0.0098 [-0.0062, +0.0234] | +0.0125 [+0.0109, +0.0143] | +0.0014 [-0.0035, +0.0053] | +0.0281 [+0.0055, +0.0587] | +0.0569 [+0.0320, +0.0820] | +0.0092 [+0.0013, +0.0175] | +0.1247 [+0.0427, +0.2059] | +0.0689 [+0.0389, +0.0993] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_gbm_base+every_day | +0.0542 [+0.0257, +0.0845] | +0.0166 [+0.0011, +0.0300] | +0.0132 [+0.0114, +0.0151] | +0.0008 [-0.0060, +0.0057] | +0.0278 [+0.0022, +0.0605] | +0.0390 [+0.0158, +0.0634] | +0.0163 [+0.0092, +0.0242] | +0.1101 [+0.0330, +0.1908] | +0.0681 [+0.0467, +0.0928] |
| risk_gbm_base+every_day+gate | +0.0386 [+0.0127, +0.0658] | +0.0256 [+0.0080, +0.0396] | +0.0136 [+0.0118, +0.0155] | +0.0009 [-0.0065, +0.0059] | +0.0269 [+0.0031, +0.0546] | +0.0395 [+0.0145, +0.0650] | +0.0141 [+0.0076, +0.0209] | +0.1101 [+0.0304, +0.1894] | +0.0681 [+0.0458, +0.0933] |
| risk_gbm_base+every_day+persist | +0.0484 [+0.0229, +0.0773] | +0.0222 [+0.0095, +0.0341] | +0.0133 [+0.0116, +0.0152] | +0.0029 [-0.0014, +0.0062] | +0.0279 [+0.0056, +0.0558] | +0.0381 [+0.0148, +0.0630] | +0.0163 [+0.0102, +0.0236] | +0.1101 [+0.0330, +0.1898] | +0.0681 [+0.0457, +0.0916] |
| risk_gbm_base+every_day+scarce | +0.0542 [+0.0277, +0.0836] | +0.0166 [+0.0013, +0.0311] | +0.0136 [+0.0119, +0.0154] | +0.0038 [-0.0002, +0.0069] | +0.0286 [+0.0038, +0.0577] | +0.0391 [+0.0146, +0.0638] | +0.0171 [+0.0102, +0.0245] | +0.1101 [+0.0303, +0.1887] | +0.0681 [+0.0458, +0.0909] |
| risk_gbm_base+every_day+shrunk | +0.0397 [+0.0236, +0.0565] | +0.0298 [+0.0191, +0.0399] | +0.0137 [+0.0119, +0.0156] | +0.0032 [-0.0013, +0.0065] | +0.0284 [+0.0062, +0.0551] | +0.0368 [+0.0140, +0.0590] | +0.0159 [+0.0116, +0.0206] | +0.1101 [+0.0335, +0.1910] | +0.0681 [+0.0447, +0.0917] |
| risk_gbm_base+hurdle_isotonic | +0.0099 [-0.0341, +0.0495] | -0.0107 [-0.0348, +0.0082] | +0.0120 [+0.0106, +0.0135] | +0.0027 [-0.0027, +0.0066] | +0.0271 [+0.0049, +0.0550] | +0.0364 [+0.0123, +0.0617] | +0.0016 [-0.0087, +0.0111] | +0.1101 [+0.0293, +0.1890] | +0.0681 [+0.0460, +0.0905] |
| risk_gbm_base+hurdle_isotonic+h41 | +0.0093 [-0.0342, +0.0504] | -0.0092 [-0.0324, +0.0093] | +0.0120 [+0.0106, +0.0135] | +0.0000 [-0.0063, +0.0051] | +0.0266 [+0.0053, +0.0525] | +0.0404 [+0.0198, +0.0623] | +0.0008 [-0.0099, +0.0110] | +0.0993 [+0.0190, +0.1808] | +0.0713 [+0.0482, +0.0942] |
| risk_gbm_base+hurdle_isotonic+settle | +0.0099 [-0.0329, +0.0526] | -0.0107 [-0.0349, +0.0084] | +0.0120 [+0.0106, +0.0135] | +0.0027 [-0.0021, +0.0067] | +0.0271 [+0.0046, +0.0541] | +0.0364 [+0.0131, +0.0593] | +0.0016 [-0.0090, +0.0113] | +0.1101 [+0.0319, +0.1905] | +0.0681 [+0.0459, +0.0921] |
| risk_gbm_base+hurdle_isotonic+settle+h41 | +0.0093 [-0.0343, +0.0511] | -0.0092 [-0.0314, +0.0102] | +0.0120 [+0.0105, +0.0136] | +0.0000 [-0.0058, +0.0050] | +0.0266 [+0.0053, +0.0536] | +0.0404 [+0.0188, +0.0624] | +0.0008 [-0.0098, +0.0110] | +0.0993 [+0.0160, +0.1802] | +0.0713 [+0.0478, +0.0970] |
| risk_gbm_base+hurdle_platt | +0.0360 [+0.0036, +0.0687] | -0.0087 [-0.0246, +0.0052] | +0.0104 [+0.0088, +0.0120] | +0.0027 [-0.0030, +0.0065] | +0.0249 [+0.0060, +0.0489] | +0.0356 [+0.0138, +0.0591] | +0.0069 [-0.0006, +0.0151] | +0.1101 [+0.0322, +0.1868] | +0.0681 [+0.0453, +0.0927] |
| risk_gbm_base+hurdle_platt+h41 | +0.0353 [+0.0025, +0.0716] | -0.0072 [-0.0222, +0.0071] | +0.0104 [+0.0087, +0.0119] | +0.0001 [-0.0062, +0.0050] | +0.0245 [+0.0054, +0.0483] | +0.0396 [+0.0202, +0.0613] | +0.0062 [-0.0013, +0.0149] | +0.0993 [+0.0159, +0.1835] | +0.0713 [+0.0482, +0.0967] |
| risk_gbm_base+hurdle_platt+settle | +0.0360 [+0.0036, +0.0706] | -0.0087 [-0.0247, +0.0048] | +0.0104 [+0.0088, +0.0119] | +0.0027 [-0.0022, +0.0067] | +0.0249 [+0.0049, +0.0488] | +0.0356 [+0.0139, +0.0587] | +0.0069 [-0.0007, +0.0153] | +0.1101 [+0.0311, +0.1868] | +0.0681 [+0.0445, +0.0914] |
| risk_gbm_base+hurdle_platt+settle+h41 | +0.0353 [+0.0035, +0.0676] | -0.0072 [-0.0222, +0.0061] | +0.0104 [+0.0088, +0.0119] | +0.0001 [-0.0059, +0.0050] | +0.0245 [+0.0051, +0.0482] | +0.0396 [+0.0185, +0.0613] | +0.0062 [-0.0013, +0.0146] | +0.0993 [+0.0179, +0.1780] | +0.0713 [+0.0485, +0.0953] |
| risk_gbm_base+hurdle_state_isotonic | +0.0027 [-0.0475, +0.0470] | +0.0048 [-0.0218, +0.0271] | +0.0128 [+0.0112, +0.0145] | +0.0038 [+0.0002, +0.0070] | +0.0232 [+0.0050, +0.0471] | +0.0369 [+0.0150, +0.0607] | +0.0022 [-0.0100, +0.0129] | +0.1101 [+0.0346, +0.1904] | +0.0681 [+0.0455, +0.0919] |
| risk_gbm_base+hurdle_state_isotonic+h41 | +0.0021 [-0.0475, +0.0484] | +0.0063 [-0.0187, +0.0282] | +0.0128 [+0.0112, +0.0145] | +0.0012 [-0.0038, +0.0053] | +0.0227 [+0.0047, +0.0459] | +0.0409 [+0.0199, +0.0652] | +0.0015 [-0.0106, +0.0123] | +0.0993 [+0.0197, +0.1816] | +0.0713 [+0.0481, +0.0956] |
| risk_gbm_base+hurdle_state_isotonic+settle | +0.0027 [-0.0467, +0.0491] | +0.0048 [-0.0228, +0.0272] | +0.0128 [+0.0112, +0.0145] | +0.0038 [+0.0000, +0.0070] | +0.0232 [+0.0055, +0.0452] | +0.0369 [+0.0144, +0.0602] | +0.0022 [-0.0099, +0.0130] | +0.1101 [+0.0298, +0.1879] | +0.0681 [+0.0459, +0.0920] |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | +0.0021 [-0.0475, +0.0464] | +0.0063 [-0.0206, +0.0282] | +0.0128 [+0.0111, +0.0146] | +0.0012 [-0.0040, +0.0053] | +0.0227 [+0.0055, +0.0456] | +0.0409 [+0.0197, +0.0646] | +0.0015 [-0.0106, +0.0124] | +0.0993 [+0.0191, +0.1811] | +0.0713 [+0.0494, +0.0954] |
| risk_gbm_base+hurdle_state_platt | +0.0340 [+0.0000, +0.0712] | +0.0045 [-0.0151, +0.0211] | +0.0126 [+0.0110, +0.0143] | +0.0038 [+0.0002, +0.0068] | +0.0264 [+0.0066, +0.0525] | +0.0369 [+0.0147, +0.0613] | +0.0099 [+0.0020, +0.0186] | +0.1101 [+0.0355, +0.1896] | +0.0681 [+0.0452, +0.0924] |
| risk_gbm_base+hurdle_state_platt+h41 | +0.0334 [+0.0003, +0.0672] | +0.0060 [-0.0134, +0.0223] | +0.0126 [+0.0110, +0.0142] | +0.0012 [-0.0039, +0.0054] | +0.0259 [+0.0066, +0.0513] | +0.0409 [+0.0204, +0.0639] | +0.0091 [+0.0013, +0.0172] | +0.0993 [+0.0167, +0.1783] | +0.0713 [+0.0486, +0.0957] |
| risk_gbm_base+hurdle_state_platt+settle | +0.0340 [-0.0004, +0.0697] | +0.0045 [-0.0145, +0.0204] | +0.0126 [+0.0110, +0.0143] | +0.0038 [+0.0001, +0.0071] | +0.0264 [+0.0071, +0.0525] | +0.0369 [+0.0134, +0.0615] | +0.0099 [+0.0021, +0.0185] | +0.1101 [+0.0299, +0.1854] | +0.0681 [+0.0457, +0.0911] |
| risk_gbm_base+hurdle_state_platt+settle+h41 | +0.0334 [-0.0013, +0.0655] | +0.0060 [-0.0118, +0.0225] | +0.0126 [+0.0110, +0.0143] | +0.0012 [-0.0046, +0.0054] | +0.0259 [+0.0064, +0.0506] | +0.0409 [+0.0194, +0.0637] | +0.0091 [+0.0010, +0.0169] | +0.0993 [+0.0152, +0.1835] | +0.0713 [+0.0488, +0.0963] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic+every_day | +0.0531 [+0.0255, +0.0814] | +0.0089 [-0.0140, +0.0258] | +0.0132 [+0.0114, +0.0151] | +0.0019 [-0.0049, +0.0081] | +0.0252 [+0.0011, +0.0534] | +0.0333 [+0.0061, +0.0619] | +0.0151 [+0.0083, +0.0221] | +0.0892 [+0.0129, +0.1670] | +0.0774 [+0.0469, +0.1125] |
| risk_logistic+every_day+gate | +0.0375 [+0.0124, +0.0643] | +0.0179 [-0.0056, +0.0369] | +0.0136 [+0.0119, +0.0156] | +0.0020 [-0.0055, +0.0083] | +0.0244 [+0.0024, +0.0530] | +0.0339 [+0.0051, +0.0632] | +0.0129 [+0.0068, +0.0197] | +0.0892 [+0.0134, +0.1635] | +0.0774 [+0.0481, +0.1152] |
| risk_logistic+every_day+persist | +0.0475 [+0.0222, +0.0737] | +0.0146 [-0.0046, +0.0285] | +0.0133 [+0.0115, +0.0151] | +0.0042 [-0.0000, +0.0088] | +0.0246 [+0.0036, +0.0502] | +0.0325 [+0.0041, +0.0599] | +0.0150 [+0.0090, +0.0217] | +0.0892 [+0.0140, +0.1626] | +0.0774 [+0.0454, +0.1144] |
| risk_logistic+every_day+scarce | +0.0531 [+0.0259, +0.0821] | +0.0089 [-0.0128, +0.0260] | +0.0136 [+0.0119, +0.0155] | +0.0050 [+0.0008, +0.0092] | +0.0261 [+0.0025, +0.0547] | +0.0334 [+0.0058, +0.0639] | +0.0158 [+0.0092, +0.0233] | +0.0892 [+0.0150, +0.1628] | +0.0774 [+0.0471, +0.1144] |
| risk_logistic+every_day+shrunk | +0.0386 [+0.0216, +0.0559] | +0.0221 [+0.0043, +0.0353] | +0.0137 [+0.0119, +0.0156] | +0.0043 [-0.0003, +0.0090] | +0.0258 [+0.0050, +0.0523] | +0.0311 [+0.0043, +0.0591] | +0.0146 [+0.0106, +0.0191] | +0.0892 [+0.0131, +0.1635] | +0.0774 [+0.0467, +0.1146] |
| risk_logistic+hurdle_isotonic | +0.0088 [-0.0363, +0.0522] | -0.0185 [-0.0417, +0.0021] | +0.0120 [+0.0106, +0.0135] | +0.0038 [-0.0015, +0.0090] | +0.0245 [+0.0037, +0.0501] | +0.0307 [+0.0041, +0.0593] | +0.0003 [-0.0099, +0.0103] | +0.0892 [+0.0155, +0.1627] | +0.0774 [+0.0473, +0.1139] |
| risk_logistic+hurdle_isotonic+h41 | +0.0095 [-0.0359, +0.0536] | -0.0171 [-0.0401, +0.0028] | +0.0120 [+0.0106, +0.0136] | +0.0039 [-0.0011, +0.0092] | +0.0238 [+0.0036, +0.0482] | +0.0330 [+0.0058, +0.0603] | +0.0004 [-0.0103, +0.0105] | +0.0906 [+0.0144, +0.1657] | +0.0764 [+0.0442, +0.1162] |
| risk_logistic+hurdle_isotonic+settle | +0.0088 [-0.0379, +0.0515] | -0.0185 [-0.0436, +0.0024] | +0.0120 [+0.0107, +0.0135] | +0.0038 [-0.0017, +0.0089] | +0.0245 [+0.0035, +0.0513] | +0.0307 [+0.0035, +0.0600] | +0.0003 [-0.0108, +0.0096] | +0.0892 [+0.0148, +0.1625] | +0.0774 [+0.0470, +0.1154] |
| risk_logistic+hurdle_isotonic+settle+h41 | +0.0095 [-0.0332, +0.0536] | -0.0171 [-0.0404, +0.0029] | +0.0120 [+0.0106, +0.0135] | +0.0039 [-0.0014, +0.0089] | +0.0238 [+0.0034, +0.0481] | +0.0330 [+0.0064, +0.0614] | +0.0004 [-0.0094, +0.0106] | +0.0906 [+0.0134, +0.1624] | +0.0764 [+0.0436, +0.1134] |
| risk_logistic+hurdle_platt | +0.0349 [+0.0022, +0.0700] | -0.0164 [-0.0369, -0.0002] | +0.0104 [+0.0089, +0.0119] | +0.0039 [-0.0015, +0.0091] | +0.0224 [+0.0038, +0.0467] | +0.0299 [+0.0021, +0.0566] | +0.0057 [-0.0015, +0.0140] | +0.0892 [+0.0151, +0.1614] | +0.0774 [+0.0461, +0.1146] |
| risk_logistic+hurdle_platt+h41 | +0.0356 [+0.0024, +0.0708] | -0.0150 [-0.0348, +0.0013] | +0.0104 [+0.0088, +0.0119] | +0.0040 [-0.0013, +0.0089] | +0.0217 [+0.0035, +0.0436] | +0.0322 [+0.0066, +0.0593] | +0.0058 [-0.0018, +0.0141] | +0.0906 [+0.0181, +0.1607] | +0.0764 [+0.0450, +0.1158] |
| risk_logistic+hurdle_platt+settle | +0.0349 [+0.0036, +0.0675] | -0.0164 [-0.0354, -0.0001] | +0.0104 [+0.0088, +0.0119] | +0.0039 [-0.0015, +0.0089] | +0.0224 [+0.0036, +0.0463] | +0.0299 [+0.0035, +0.0574] | +0.0057 [-0.0014, +0.0137] | +0.0892 [+0.0156, +0.1616] | +0.0774 [+0.0475, +0.1137] |
| risk_logistic+hurdle_platt+settle+h41 | +0.0356 [+0.0019, +0.0681] | -0.0150 [-0.0332, +0.0004] | +0.0104 [+0.0088, +0.0119] | +0.0040 [-0.0014, +0.0092] | +0.0217 [+0.0041, +0.0427] | +0.0322 [+0.0061, +0.0587] | +0.0058 [-0.0017, +0.0138] | +0.0906 [+0.0150, +0.1665] | +0.0764 [+0.0439, +0.1136] |
| risk_logistic+hurdle_state_isotonic | +0.0016 [-0.0505, +0.0527] | -0.0029 [-0.0314, +0.0207] | +0.0128 [+0.0112, +0.0145] | +0.0050 [+0.0007, +0.0095] | +0.0206 [+0.0035, +0.0430] | +0.0312 [+0.0032, +0.0576] | +0.0009 [-0.0104, +0.0121] | +0.0892 [+0.0125, +0.1653] | +0.0774 [+0.0477, +0.1144] |
| risk_logistic+hurdle_state_isotonic+h41 | +0.0023 [-0.0477, +0.0515] | -0.0016 [-0.0294, +0.0214] | +0.0128 [+0.0111, +0.0145] | +0.0051 [+0.0010, +0.0094] | +0.0199 [+0.0029, +0.0408] | +0.0335 [+0.0073, +0.0623] | +0.0010 [-0.0105, +0.0116] | +0.0906 [+0.0144, +0.1665] | +0.0764 [+0.0430, +0.1143] |
| risk_logistic+hurdle_state_isotonic+settle | +0.0016 [-0.0519, +0.0501] | -0.0029 [-0.0318, +0.0205] | +0.0128 [+0.0112, +0.0146] | +0.0050 [+0.0008, +0.0092] | +0.0206 [+0.0036, +0.0419] | +0.0312 [+0.0033, +0.0582] | +0.0009 [-0.0110, +0.0122] | +0.0892 [+0.0141, +0.1580] | +0.0774 [+0.0479, +0.1124] |
| risk_logistic+hurdle_state_isotonic+settle+h41 | +0.0023 [-0.0494, +0.0499] | -0.0016 [-0.0283, +0.0220] | +0.0128 [+0.0112, +0.0146] | +0.0051 [+0.0009, +0.0096] | +0.0199 [+0.0036, +0.0399] | +0.0335 [+0.0070, +0.0599] | +0.0010 [-0.0105, +0.0117] | +0.0906 [+0.0192, +0.1643] | +0.0764 [+0.0440, +0.1125] |
| risk_logistic+hurdle_state_platt | +0.0329 [-0.0034, +0.0693] | -0.0033 [-0.0249, +0.0152] | +0.0126 [+0.0110, +0.0143] | +0.0050 [+0.0010, +0.0092] | +0.0239 [+0.0054, +0.0474] | +0.0312 [+0.0054, +0.0596] | +0.0086 [+0.0007, +0.0169] | +0.0892 [+0.0127, +0.1598] | +0.0774 [+0.0463, +0.1137] |
| risk_logistic+hurdle_state_platt+h41 | +0.0336 [+0.0011, +0.0692] | -0.0019 [-0.0230, +0.0162] | +0.0126 [+0.0109, +0.0142] | +0.0051 [+0.0008, +0.0095] | +0.0231 [+0.0055, +0.0454] | +0.0335 [+0.0067, +0.0618] | +0.0087 [+0.0013, +0.0169] | +0.0906 [+0.0178, +0.1621] | +0.0764 [+0.0438, +0.1156] |
| risk_logistic+hurdle_state_platt+settle | +0.0329 [-0.0021, +0.0680] | -0.0033 [-0.0247, +0.0159] | +0.0126 [+0.0109, +0.0142] | +0.0050 [+0.0009, +0.0093] | +0.0239 [+0.0046, +0.0475] | +0.0312 [+0.0041, +0.0591] | +0.0086 [+0.0009, +0.0169] | +0.0892 [+0.0160, +0.1619] | +0.0774 [+0.0454, +0.1136] |
| risk_logistic+hurdle_state_platt+settle+h41 | +0.0336 [-0.0021, +0.0703] | -0.0019 [-0.0227, +0.0174] | +0.0126 [+0.0110, +0.0142] | +0.0051 [+0.0010, +0.0097] | +0.0231 [+0.0049, +0.0463] | +0.0335 [+0.0068, +0.0604] | +0.0087 [+0.0006, +0.0170] | +0.0906 [+0.0178, +0.1659] | +0.0764 [+0.0440, +0.1140] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_logistic_base+every_day | +0.0533 [+0.0256, +0.0823] | +0.0135 [-0.0012, +0.0264] | +0.0132 [+0.0115, +0.0151] | +0.0009 [-0.0055, +0.0058] | +0.0288 [+0.0041, +0.0593] | +0.0404 [+0.0147, +0.0692] | +0.0158 [+0.0089, +0.0234] | +0.0954 [+0.0435, +0.1499] | +0.0711 [+0.0381, +0.1090] |
| risk_logistic_base+every_day+gate | +0.0377 [+0.0125, +0.0659] | +0.0225 [+0.0051, +0.0368] | +0.0136 [+0.0119, +0.0155] | +0.0010 [-0.0058, +0.0060] | +0.0279 [+0.0032, +0.0559] | +0.0409 [+0.0150, +0.0670] | +0.0136 [+0.0073, +0.0205] | +0.0954 [+0.0427, +0.1489] | +0.0711 [+0.0394, +0.1092] |
| risk_logistic_base+every_day+persist | +0.0476 [+0.0233, +0.0731] | +0.0189 [+0.0086, +0.0289] | +0.0133 [+0.0116, +0.0151] | +0.0031 [-0.0009, +0.0065] | +0.0282 [+0.0057, +0.0561] | +0.0395 [+0.0145, +0.0670] | +0.0157 [+0.0098, +0.0222] | +0.0954 [+0.0386, +0.1499] | +0.0711 [+0.0380, +0.1071] |
| risk_logistic_base+every_day+scarce | +0.0533 [+0.0268, +0.0818] | +0.0135 [-0.0018, +0.0260] | +0.0136 [+0.0119, +0.0155] | +0.0040 [+0.0002, +0.0071] | +0.0296 [+0.0050, +0.0625] | +0.0404 [+0.0151, +0.0675] | +0.0165 [+0.0101, +0.0243] | +0.0954 [+0.0374, +0.1520] | +0.0711 [+0.0386, +0.1084] |
| risk_logistic_base+every_day+shrunk | +0.0388 [+0.0239, +0.0559] | +0.0267 [+0.0175, +0.0357] | +0.0137 [+0.0119, +0.0156] | +0.0033 [-0.0011, +0.0068] | +0.0293 [+0.0085, +0.0567] | +0.0382 [+0.0122, +0.0657] | +0.0153 [+0.0114, +0.0201] | +0.0954 [+0.0398, +0.1512] | +0.0711 [+0.0382, +0.1094] |
| risk_logistic_base+hurdle_isotonic | +0.0090 [-0.0339, +0.0519] | -0.0138 [-0.0348, +0.0039] | +0.0120 [+0.0106, +0.0135] | +0.0028 [-0.0023, +0.0066] | +0.0281 [+0.0069, +0.0562] | +0.0377 [+0.0126, +0.0635] | +0.0010 [-0.0090, +0.0111] | +0.0954 [+0.0400, +0.1487] | +0.0711 [+0.0385, +0.1092] |
| risk_logistic_base+hurdle_isotonic+h41 | +0.0107 [-0.0365, +0.0546] | -0.0126 [-0.0342, +0.0051] | +0.0120 [+0.0106, +0.0136] | +0.0029 [-0.0025, +0.0068] | +0.0275 [+0.0065, +0.0546] | +0.0403 [+0.0146, +0.0679] | +0.0011 [-0.0094, +0.0111] | +0.0964 [+0.0464, +0.1425] | +0.0736 [+0.0417, +0.1102] |
| risk_logistic_base+hurdle_isotonic+settle | +0.0090 [-0.0360, +0.0530] | -0.0138 [-0.0362, +0.0045] | +0.0120 [+0.0107, +0.0135] | +0.0028 [-0.0022, +0.0068] | +0.0281 [+0.0056, +0.0557] | +0.0377 [+0.0123, +0.0662] | +0.0010 [-0.0089, +0.0112] | +0.0954 [+0.0403, +0.1494] | +0.0711 [+0.0387, +0.1082] |
| risk_logistic_base+hurdle_isotonic+settle+h41 | +0.0107 [-0.0360, +0.0556] | -0.0126 [-0.0343, +0.0048] | +0.0120 [+0.0106, +0.0135] | +0.0029 [-0.0023, +0.0067] | +0.0275 [+0.0060, +0.0539] | +0.0403 [+0.0134, +0.0679] | +0.0011 [-0.0097, +0.0115] | +0.0964 [+0.0459, +0.1450] | +0.0736 [+0.0403, +0.1137] |
| risk_logistic_base+hurdle_platt | +0.0350 [+0.0048, +0.0709] | -0.0118 [-0.0256, +0.0004] | +0.0104 [+0.0088, +0.0119] | +0.0029 [-0.0022, +0.0069] | +0.0259 [+0.0065, +0.0493] | +0.0370 [+0.0118, +0.0646] | +0.0064 [-0.0005, +0.0150] | +0.0954 [+0.0433, +0.1471] | +0.0711 [+0.0389, +0.1082] |
| risk_logistic_base+hurdle_platt+h41 | +0.0367 [+0.0030, +0.0701] | -0.0106 [-0.0241, +0.0012] | +0.0104 [+0.0088, +0.0119] | +0.0029 [-0.0020, +0.0068] | +0.0254 [+0.0060, +0.0476] | +0.0395 [+0.0138, +0.0665] | +0.0065 [-0.0012, +0.0147] | +0.0964 [+0.0460, +0.1407] | +0.0736 [+0.0423, +0.1115] |
| risk_logistic_base+hurdle_platt+settle | +0.0350 [+0.0041, +0.0699] | -0.0118 [-0.0254, -0.0001] | +0.0104 [+0.0088, +0.0118] | +0.0029 [-0.0022, +0.0070] | +0.0259 [+0.0057, +0.0500] | +0.0370 [+0.0113, +0.0640] | +0.0064 [-0.0010, +0.0143] | +0.0954 [+0.0396, +0.1506] | +0.0711 [+0.0377, +0.1093] |
| risk_logistic_base+hurdle_platt+settle+h41 | +0.0367 [+0.0032, +0.0705] | -0.0106 [-0.0239, +0.0020] | +0.0104 [+0.0088, +0.0120] | +0.0029 [-0.0021, +0.0068] | +0.0254 [+0.0063, +0.0474] | +0.0395 [+0.0139, +0.0668] | +0.0065 [-0.0009, +0.0145] | +0.0964 [+0.0465, +0.1429] | +0.0736 [+0.0426, +0.1105] |
| risk_logistic_base+hurdle_state_isotonic | +0.0018 [-0.0510, +0.0508] | +0.0017 [-0.0245, +0.0223] | +0.0128 [+0.0111, +0.0146] | +0.0040 [+0.0001, +0.0072] | +0.0242 [+0.0067, +0.0464] | +0.0382 [+0.0115, +0.0657] | +0.0017 [-0.0106, +0.0128] | +0.0954 [+0.0398, +0.1503] | +0.0711 [+0.0382, +0.1087] |
| risk_logistic_base+hurdle_state_isotonic+h41 | +0.0035 [-0.0474, +0.0484] | +0.0029 [-0.0224, +0.0236] | +0.0128 [+0.0112, +0.0146] | +0.0040 [+0.0002, +0.0070] | +0.0236 [+0.0065, +0.0443] | +0.0408 [+0.0139, +0.0690] | +0.0018 [-0.0104, +0.0126] | +0.0964 [+0.0473, +0.1441] | +0.0736 [+0.0406, +0.1106] |
| risk_logistic_base+hurdle_state_isotonic+settle | +0.0018 [-0.0497, +0.0508] | +0.0017 [-0.0241, +0.0225] | +0.0128 [+0.0112, +0.0145] | +0.0040 [+0.0003, +0.0071] | +0.0242 [+0.0064, +0.0470] | +0.0382 [+0.0124, +0.0666] | +0.0017 [-0.0103, +0.0129] | +0.0954 [+0.0391, +0.1510] | +0.0711 [+0.0367, +0.1093] |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | +0.0035 [-0.0478, +0.0524] | +0.0029 [-0.0224, +0.0237] | +0.0128 [+0.0112, +0.0145] | +0.0040 [+0.0005, +0.0072] | +0.0236 [+0.0061, +0.0466] | +0.0408 [+0.0149, +0.0683] | +0.0018 [-0.0104, +0.0132] | +0.0964 [+0.0477, +0.1427] | +0.0736 [+0.0406, +0.1119] |
| risk_logistic_base+hurdle_state_platt | +0.0330 [-0.0021, +0.0683] | +0.0014 [-0.0168, +0.0162] | +0.0126 [+0.0110, +0.0143] | +0.0040 [+0.0002, +0.0071] | +0.0274 [+0.0071, +0.0533] | +0.0383 [+0.0115, +0.0658] | +0.0093 [+0.0016, +0.0178] | +0.0954 [+0.0396, +0.1501] | +0.0711 [+0.0387, +0.1075] |
| risk_logistic_base+hurdle_state_platt+h41 | +0.0348 [-0.0003, +0.0707] | +0.0026 [-0.0142, +0.0183] | +0.0126 [+0.0110, +0.0143] | +0.0040 [+0.0002, +0.0070] | +0.0268 [+0.0076, +0.0506] | +0.0408 [+0.0150, +0.0694] | +0.0094 [+0.0015, +0.0180] | +0.0964 [+0.0443, +0.1443] | +0.0736 [+0.0413, +0.1136] |
| risk_logistic_base+hurdle_state_platt+settle | +0.0330 [-0.0004, +0.0702] | +0.0014 [-0.0162, +0.0167] | +0.0126 [+0.0110, +0.0144] | +0.0040 [+0.0003, +0.0072] | +0.0274 [+0.0072, +0.0531] | +0.0383 [+0.0121, +0.0653] | +0.0093 [+0.0014, +0.0178] | +0.0954 [+0.0393, +0.1501] | +0.0711 [+0.0405, +0.1094] |
| risk_logistic_base+hurdle_state_platt+settle+h41 | +0.0348 [+0.0000, +0.0727] | +0.0026 [-0.0159, +0.0173] | +0.0126 [+0.0110, +0.0143] | +0.0040 [+0.0005, +0.0070] | +0.0268 [+0.0073, +0.0513] | +0.0408 [+0.0146, +0.0681] | +0.0094 [+0.0012, +0.0179] | +0.0964 [+0.0461, +0.1405] | +0.0736 [+0.0412, +0.1126] |
| risk_quantile_skewt | -0.0090 [-0.0307, +0.0131] | +0.0085 [-0.0055, +0.0225] | +0.0136 [+0.0119, +0.0155] | +0.0019 [-0.0033, +0.0056] | +0.0239 [+0.0054, +0.0480] | +0.0234 [-0.0109, +0.0571] | +0.0014 [-0.0042, +0.0066] | +0.1102 [+0.0260, +0.1974] | +0.0706 [+0.0331, +0.1124] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| risk_quantile_skewt_base+every_day | +0.0388 [+0.0076, +0.0711] | +0.0057 [-0.0080, +0.0179] | +0.0130 [+0.0112, +0.0149] | -0.0015 [-0.0086, +0.0039] | +0.0361 [+0.0035, +0.0761] | +0.0296 [-0.0091, +0.0687] | +0.0139 [+0.0066, +0.0216] | +0.0724 [-0.0026, +0.1384] | +0.0602 [+0.0211, +0.1061] |
| risk_quantile_skewt_base+every_day+gate | +0.0232 [-0.0055, +0.0539] | +0.0147 [-0.0015, +0.0294] | +0.0134 [+0.0115, +0.0153] | -0.0014 [-0.0092, +0.0043] | +0.0353 [+0.0043, +0.0720] | +0.0301 [-0.0079, +0.0701] | +0.0117 [+0.0052, +0.0190] | +0.0724 [+0.0022, +0.1388] | +0.0602 [+0.0201, +0.1035] |
| risk_quantile_skewt_base+every_day+persist | +0.0320 [+0.0027, +0.0622] | +0.0109 [+0.0007, +0.0208] | +0.0131 [+0.0115, +0.0149] | +0.0008 [-0.0048, +0.0046] | +0.0362 [+0.0072, +0.0731] | +0.0259 [-0.0105, +0.0645] | +0.0139 [+0.0074, +0.0209] | +0.0724 [+0.0001, +0.1384] | +0.0602 [+0.0207, +0.1073] |
| risk_quantile_skewt_base+every_day+scarce | +0.0388 [+0.0065, +0.0699] | +0.0057 [-0.0089, +0.0183] | +0.0134 [+0.0117, +0.0152] | +0.0015 [-0.0047, +0.0053] | +0.0370 [+0.0052, +0.0781] | +0.0296 [-0.0099, +0.0687] | +0.0147 [+0.0075, +0.0225] | +0.0724 [+0.0018, +0.1358] | +0.0602 [+0.0217, +0.1047] |
| risk_quantile_skewt_base+every_day+shrunk | +0.0244 [+0.0004, +0.0463] | +0.0189 [+0.0093, +0.0279] | +0.0135 [+0.0118, +0.0154] | +0.0008 [-0.0056, +0.0051] | +0.0367 [+0.0080, +0.0722] | +0.0273 [-0.0104, +0.0649] | +0.0135 [+0.0088, +0.0185] | +0.0724 [+0.0015, +0.1362] | +0.0602 [+0.0194, +0.1048] |
| risk_quantile_skewt_base+hurdle_isotonic | -0.0054 [-0.0501, +0.0398] | -0.0216 [-0.0408, -0.0044] | +0.0118 [+0.0104, +0.0133] | +0.0004 [-0.0060, +0.0050] | +0.0355 [+0.0064, +0.0731] | +0.0269 [-0.0124, +0.0662] | -0.0008 [-0.0111, +0.0090] | +0.0724 [+0.0026, +0.1363] | +0.0602 [+0.0216, +0.1041] |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | -0.0022 [-0.0471, +0.0405] | -0.0169 [-0.0378, +0.0016] | +0.0118 [+0.0104, +0.0134] | +0.0006 [-0.0056, +0.0051] | +0.0345 [+0.0053, +0.0705] | +0.0251 [-0.0090, +0.0616] | -0.0001 [-0.0104, +0.0098] | +0.1011 [+0.0334, +0.1645] | +0.0655 [+0.0208, +0.1143] |
| risk_quantile_skewt_base+hurdle_isotonic+settle | -0.0054 [-0.0510, +0.0403] | -0.0216 [-0.0411, -0.0044] | +0.0118 [+0.0104, +0.0134] | +0.0004 [-0.0060, +0.0050] | +0.0355 [+0.0066, +0.0734] | +0.0269 [-0.0085, +0.0653] | -0.0008 [-0.0111, +0.0093] | +0.0724 [+0.0032, +0.1372] | +0.0602 [+0.0224, +0.1026] |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | -0.0022 [-0.0447, +0.0399] | -0.0169 [-0.0388, +0.0015] | +0.0118 [+0.0105, +0.0134] | +0.0006 [-0.0056, +0.0051] | +0.0345 [+0.0053, +0.0720] | +0.0251 [-0.0096, +0.0583] | -0.0001 [-0.0101, +0.0097] | +0.1011 [+0.0258, +0.1621] | +0.0655 [+0.0204, +0.1113] |
| risk_quantile_skewt_base+hurdle_platt | +0.0206 [-0.0133, +0.0563] | -0.0196 [-0.0328, -0.0070] | +0.0102 [+0.0085, +0.0117] | +0.0004 [-0.0057, +0.0050] | +0.0333 [+0.0080, +0.0665] | +0.0261 [-0.0130, +0.0655] | +0.0045 [-0.0029, +0.0125] | +0.0724 [+0.0018, +0.1389] | +0.0602 [+0.0185, +0.1041] |
| risk_quantile_skewt_base+hurdle_platt+h41 | +0.0238 [-0.0083, +0.0582] | -0.0149 [-0.0288, -0.0014] | +0.0102 [+0.0085, +0.0117] | +0.0007 [-0.0057, +0.0052] | +0.0323 [+0.0057, +0.0636] | +0.0243 [-0.0105, +0.0590] | +0.0052 [-0.0025, +0.0129] | +0.1011 [+0.0295, +0.1667] | +0.0655 [+0.0225, +0.1139] |
| risk_quantile_skewt_base+hurdle_platt+settle | +0.0206 [-0.0142, +0.0588] | -0.0196 [-0.0326, -0.0071] | +0.0102 [+0.0087, +0.0117] | +0.0004 [-0.0059, +0.0051] | +0.0333 [+0.0067, +0.0663] | +0.0261 [-0.0118, +0.0629] | +0.0045 [-0.0028, +0.0128] | +0.0724 [+0.0045, +0.1386] | +0.0602 [+0.0207, +0.1033] |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | +0.0238 [-0.0082, +0.0567] | -0.0149 [-0.0294, -0.0011] | +0.0102 [+0.0085, +0.0118] | +0.0007 [-0.0054, +0.0051] | +0.0323 [+0.0056, +0.0640] | +0.0243 [-0.0110, +0.0607] | +0.0052 [-0.0017, +0.0135] | +0.1011 [+0.0304, +0.1641] | +0.0655 [+0.0206, +0.1138] |
| risk_quantile_skewt_base+hurdle_state_isotonic | -0.0127 [-0.0664, +0.0371] | -0.0061 [-0.0292, +0.0134] | +0.0126 [+0.0110, +0.0143] | +0.0015 [-0.0043, +0.0054] | +0.0315 [+0.0072, +0.0624] | +0.0274 [-0.0107, +0.0664] | -0.0002 [-0.0126, +0.0107] | +0.0724 [+0.0015, +0.1352] | +0.0602 [+0.0206, +0.1019] |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | -0.0095 [-0.0592, +0.0356] | -0.0014 [-0.0273, +0.0198] | +0.0126 [+0.0110, +0.0143] | +0.0018 [-0.0040, +0.0055] | +0.0305 [+0.0065, +0.0608] | +0.0256 [-0.0086, +0.0628] | +0.0005 [-0.0109, +0.0110] | +0.1011 [+0.0320, +0.1660] | +0.0655 [+0.0217, +0.1150] |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | -0.0127 [-0.0621, +0.0398] | -0.0061 [-0.0290, +0.0141] | +0.0126 [+0.0110, +0.0143] | +0.0015 [-0.0045, +0.0055] | +0.0315 [+0.0065, +0.0630] | +0.0274 [-0.0098, +0.0673] | -0.0002 [-0.0120, +0.0111] | +0.0724 [+0.0018, +0.1388] | +0.0602 [+0.0199, +0.1039] |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | -0.0095 [-0.0595, +0.0368] | -0.0014 [-0.0261, +0.0190] | +0.0126 [+0.0109, +0.0144] | +0.0018 [-0.0041, +0.0055] | +0.0305 [+0.0058, +0.0620] | +0.0256 [-0.0077, +0.0613] | +0.0005 [-0.0119, +0.0109] | +0.1011 [+0.0284, +0.1659] | +0.0655 [+0.0223, +0.1114] |
| risk_quantile_skewt_base+hurdle_state_platt | +0.0186 [-0.0157, +0.0573] | -0.0064 [-0.0229, +0.0089] | +0.0124 [+0.0107, +0.0140] | +0.0015 [-0.0045, +0.0054] | +0.0348 [+0.0074, +0.0672] | +0.0274 [-0.0106, +0.0639] | +0.0075 [-0.0002, +0.0159] | +0.0724 [-0.0004, +0.1404] | +0.0602 [+0.0192, +0.1024] |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | +0.0218 [-0.0125, +0.0566] | -0.0017 [-0.0188, +0.0139] | +0.0124 [+0.0108, +0.0141] | +0.0018 [-0.0043, +0.0055] | +0.0338 [+0.0064, +0.0672] | +0.0256 [-0.0086, +0.0616] | +0.0081 [+0.0005, +0.0162] | +0.1011 [+0.0275, +0.1636] | +0.0655 [+0.0224, +0.1118] |
| risk_quantile_skewt_base+hurdle_state_platt+settle | +0.0186 [-0.0182, +0.0570] | -0.0064 [-0.0223, +0.0080] | +0.0124 [+0.0107, +0.0141] | +0.0015 [-0.0043, +0.0054] | +0.0348 [+0.0085, +0.0689] | +0.0274 [-0.0099, +0.0667] | +0.0075 [-0.0005, +0.0160] | +0.0724 [+0.0001, +0.1390] | +0.0602 [+0.0220, +0.1040] |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | +0.0218 [-0.0114, +0.0571] | -0.0017 [-0.0197, +0.0129] | +0.0124 [+0.0108, +0.0140] | +0.0018 [-0.0044, +0.0055] | +0.0338 [+0.0067, +0.0666] | +0.0256 [-0.0087, +0.0618] | +0.0081 [+0.0005, +0.0162] | +0.1011 [+0.0304, +0.1662] | +0.0655 [+0.0227, +0.1139] |
