Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.7 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+every_day | 15 of 26 | 0.577 [0.385, 0.760] | 0.274 | 5.85 flat / 2.63 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+gate | 16 of 26 | 0.615 [0.444, 0.778] | 0.269 | 5.65 flat / 2.56 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 15 of 26 | 0.577 [0.417, 0.741] | 0.242 | 4.31 flat / 2.04 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 16 of 26 | 0.615 [0.440, 0.786] | 0.246 | 4.35 flat / 2.08 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+persist | 15 of 26 | 0.577 [0.406, 0.750] | 0.269 | 5.50 flat / 2.46 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+scarce | 16 of 26 | 0.615 [0.433, 0.792] | 0.269 | 5.73 flat / 2.58 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+shrunk | 13 of 26 | 0.500 [0.324, 0.682] | 0.231 | 3.04 flat / 1.55 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic | 15 of 26 | 0.577 [0.389, 0.783] | 0.231 | 4.08 flat / 1.66 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.375, 0.778] | 0.231 | 3.88 flat / 1.49 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+settle | 14 of 26 | 0.538 [0.367, 0.714] | 0.231 | 3.00 flat / 1.34 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.368, 0.719] | 0.231 | 3.31 flat / 1.48 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.760] | 0.269 | 5.23 flat / 2.36 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+h41 | 16 of 26 | 0.615 [0.424, 0.794] | 0.269 | 5.27 flat / 2.34 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+settle | 14 of 26 | 0.538 [0.363, 0.719] | 0.231 | 4.19 flat / 2.01 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_platt+settle+h41 | 14 of 26 | 0.538 [0.351, 0.722] | 0.238 | 4.27 flat / 2.03 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic | 15 of 26 | 0.577 [0.385, 0.774] | 0.231 | 3.73 flat / 1.42 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+h41 | 15 of 26 | 0.577 [0.381, 0.769] | 0.231 | 3.77 flat / 1.42 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+settle | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 3.35 flat / 1.37 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.42 flat / 1.44 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_platt | 15 of 26 | 0.577 [0.375, 0.760] | 0.258 | 4.46 flat / 1.91 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+h41 | 16 of 26 | 0.615 [0.429, 0.795] | 0.269 | 4.62 flat / 1.99 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.400, 0.765] | 0.231 | 4.08 flat / 1.87 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_platt+settle+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 4.19 flat / 1.92 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.00 flat / 1.29 weighted (tier 1 on the flat count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_gbm_base+every_day | 15 of 26 | 0.577 [0.389, 0.769] | 0.286 | 6.08 flat / 2.76 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.400, 0.750] | 0.269 | 5.77 flat / 2.58 weighted (tier 1 on the flat count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+persist | 15 of 26 | 0.577 [0.389, 0.765] | 0.269 | 5.77 flat / 2.62 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+scarce | 15 of 26 | 0.577 [0.385, 0.769] | 0.278 | 5.92 flat / 2.68 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 0.231 | 3.58 flat / 1.80 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.767] | 0.231 | 3.96 flat / 1.61 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.368, 0.778] | 0.231 | 3.96 flat / 1.58 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+settle | 13 of 26 | 0.500 [0.308, 0.682] | 0.231 | 3.62 flat / 1.54 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.345, 0.727] | 0.231 | 3.77 flat / 1.58 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt | 15 of 26 | 0.577 [0.375, 0.769] | 0.269 | 5.12 flat / 2.28 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+h41 | 15 of 26 | 0.577 [0.375, 0.774] | 0.269 | 5.08 flat / 2.19 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+settle | 13 of 26 | 0.500 [0.318, 0.680] | 0.262 | 4.50 flat / 2.01 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt+settle+h41 | 14 of 26 | 0.538 [0.355, 0.727] | 0.269 | 4.81 flat / 2.16 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic | 13 of 26 | 0.500 [0.304, 0.700] | 0.231 | 3.31 flat / 1.28 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 15 of 26 | 0.577 [0.389, 0.765] | 0.231 | 3.58 flat / 1.30 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+settle | 15 of 26 | 0.577 [0.384, 0.769] | 0.231 | 3.77 flat / 1.47 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 15 of 26 | 0.577 [0.389, 0.774] | 0.231 | 3.62 flat / 1.41 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt | 15 of 26 | 0.577 [0.387, 0.769] | 0.258 | 4.46 flat / 1.91 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+h41 | 15 of 26 | 0.577 [0.371, 0.773] | 0.246 | 4.35 flat / 1.80 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.390, 0.774] | 0.246 | 4.35 flat / 1.87 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 15 of 26 | 0.577 [0.381, 0.774] | 0.238 | 4.27 flat / 1.88 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic+every_day | 13 of 26 | 0.500 [0.333, 0.667] | 0.269 | 4.77 flat / 2.18 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+gate | 14 of 26 | 0.538 [0.370, 0.720] | 0.269 | 5.35 flat / 2.44 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+every_day+persist | 15 of 26 | 0.577 [0.400, 0.750] | 0.269 | 5.12 flat / 2.19 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+scarce | 13 of 26 | 0.500 [0.333, 0.667] | 0.265 | 4.54 flat / 2.07 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+shrunk | 15 of 26 | 0.577 [0.407, 0.750] | 0.238 | 4.27 flat / 1.99 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+hurdle_isotonic | 13 of 26 | 0.500 [0.333, 0.667] | 0.231 | 3.35 flat / 1.39 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+h41 | 14 of 26 | 0.538 [0.346, 0.720] | 0.231 | 3.92 flat / 1.59 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle | 12 of 26 | 0.462 [0.296, 0.625] | 0.231 | 3.65 flat / 1.45 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle+h41 | 13 of 26 | 0.500 [0.320, 0.690] | 0.231 | 3.65 flat / 1.47 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_platt | 13 of 26 | 0.500 [0.333, 0.667] | 0.269 | 4.73 flat / 2.18 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.269 | 5.15 flat / 2.33 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+settle | 12 of 26 | 0.462 [0.294, 0.632] | 0.269 | 4.81 flat / 2.12 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_platt+settle+h41 | 12 of 26 | 0.462 [0.276, 0.640] | 0.269 | 4.69 flat / 2.03 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic | 12 of 26 | 0.462 [0.290, 0.640] | 0.231 | 4.08 flat / 1.65 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.320, 0.688] | 0.231 | 3.85 flat / 1.52 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle | 11 of 26 | 0.423 [0.250, 0.593] | 0.231 | 3.62 flat / 1.44 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 12 of 26 | 0.462 [0.280, 0.643] | 0.231 | 3.23 flat / 1.27 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt | 14 of 26 | 0.538 [0.357, 0.714] | 0.269 | 4.88 flat / 2.17 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.333, 0.722] | 0.269 | 4.69 flat / 2.07 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+settle | 11 of 26 | 0.423 [0.250, 0.600] | 0.265 | 4.54 flat / 1.94 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt+settle+h41 | 12 of 26 | 0.462 [0.280, 0.647] | 0.242 | 4.31 flat / 1.88 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 2.04 flat / 1.41 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base+every_day | 11 of 26 | 0.423 [0.259, 0.593] | 0.242 | 4.31 flat / 1.85 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.368, 0.714] | 0.269 | 4.96 flat / 2.14 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+every_day+persist | 13 of 26 | 0.500 [0.333, 0.679] | 0.262 | 4.50 flat / 1.78 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+scarce | 11 of 26 | 0.423 [0.250, 0.600] | 0.231 | 4.15 flat / 1.77 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 0.231 | 3.73 flat / 1.54 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+hurdle_isotonic | 8 of 26 | 0.308 [0.158, 0.471] | 0.231 | 3.04 flat / 1.20 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+h41 | 10 of 26 | 0.385 [0.222, 0.560] | 0.231 | 3.12 flat / 1.19 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle | 12 of 26 | 0.462 [0.280, 0.657] | 0.231 | 3.23 flat / 1.28 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 10 of 26 | 0.385 [0.226, 0.548] | 0.231 | 3.46 flat / 1.36 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt | 11 of 26 | 0.423 [0.250, 0.600] | 0.250 | 4.38 flat / 1.95 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+h41 | 12 of 26 | 0.462 [0.286, 0.640] | 0.231 | 4.19 flat / 1.74 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+settle | 13 of 26 | 0.500 [0.320, 0.667] | 0.258 | 4.46 flat / 1.94 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt+settle+h41 | 10 of 26 | 0.385 [0.231, 0.545] | 0.231 | 3.96 flat / 1.54 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic | 11 of 26 | 0.423 [0.250, 0.611] | 0.231 | 4.04 flat / 1.54 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 11 of 26 | 0.423 [0.258, 0.609] | 0.231 | 3.81 flat / 1.45 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle | 12 of 26 | 0.462 [0.278, 0.640] | 0.231 | 3.35 flat / 1.36 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 10 of 26 | 0.385 [0.214, 0.562] | 0.231 | 3.35 flat / 1.29 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt | 13 of 26 | 0.500 [0.320, 0.690] | 0.269 | 4.81 flat / 2.04 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+h41 | 13 of 26 | 0.500 [0.318, 0.688] | 0.269 | 4.62 flat / 1.92 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+settle | 14 of 26 | 0.538 [0.360, 0.714] | 0.258 | 4.46 flat / 1.90 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 11 of 26 | 0.423 [0.240, 0.600] | 0.250 | 4.38 flat / 1.80 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt | 13 of 26 | 0.500 [0.333, 0.680] | 0.231 | 4.12 flat / 3.39 weighted (tier 1 on the flat count) | 4.1 / 4.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.231 | 2.54 flat / 1.80 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base+every_day | 15 of 26 | 0.577 [0.409, 0.750] | 0.269 | 4.65 flat / 1.97 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.741] | 0.269 | 5.00 flat / 2.22 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+persist | 14 of 26 | 0.538 [0.368, 0.706] | 0.269 | 5.38 flat / 2.26 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+scarce | 15 of 26 | 0.577 [0.400, 0.739] | 0.258 | 4.46 flat / 1.88 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+shrunk | 15 of 26 | 0.577 [0.400, 0.760] | 0.269 | 4.85 flat / 2.28 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.667] | 0.231 | 3.77 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 12 of 26 | 0.462 [0.280, 0.652] | 0.231 | 3.62 flat / 1.32 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 13 of 26 | 0.500 [0.316, 0.680] | 0.231 | 3.42 flat / 1.39 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 13 of 26 | 0.500 [0.333, 0.667] | 0.231 | 3.62 flat / 1.37 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt | 13 of 26 | 0.500 [0.321, 0.682] | 0.269 | 5.00 flat / 2.19 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 13 of 26 | 0.500 [0.333, 0.680] | 0.269 | 5.50 flat / 2.48 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle | 14 of 26 | 0.538 [0.364, 0.714] | 0.231 | 4.08 flat / 1.62 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 15 of 26 | 0.577 [0.400, 0.750] | 0.269 | 4.85 flat / 1.95 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 of 26 | 0.462 [0.276, 0.643] | 0.235 | 4.23 flat / 1.60 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 11 of 26 | 0.423 [0.241, 0.593] | 0.231 | 4.00 flat / 1.51 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 13 of 26 | 0.500 [0.304, 0.682] | 0.231 | 3.73 flat / 1.54 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 13 of 26 | 0.500 [0.333, 0.682] | 0.231 | 3.88 flat / 1.47 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt | 13 of 26 | 0.500 [0.333, 0.688] | 0.269 | 5.04 flat / 2.18 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 13 of 26 | 0.500 [0.318, 0.682] | 0.269 | 5.42 flat / 2.46 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.391, 0.750] | 0.269 | 4.73 flat / 2.08 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 14 of 26 | 0.538 [0.364, 0.710] | 0.269 | 4.96 flat / 2.11 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |

Table 1b. Tier 1 at each lead alone, inside and outside the early years, and the recall with equal weight per regime: reported for every model, not part of the pass rule.

calendar_climatology:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.536] | 4.846 [3.129, 7.438] | 2.798 [1.804, 4.484] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 4.885 [3.069, 7.601] | 2.712 [1.716, 4.351] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 4.923 [3.100, 7.667] | 2.731 [1.728, 4.392] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 4.962 [3.115, 7.709] | 2.750 [1.743, 4.441] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.000 [3.125, 7.751] | 2.769 [1.750, 4.472] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.846] | 6.235 [3.684, 10.417] | 2.618 [1.433, 4.614] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 3.778 (no interval) | 3.667 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

ngboost_laplace:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 1.692 [0.886, 2.895] | 0.538 [0.279, 0.923] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.235] | 1.731 [0.863, 2.833] | 0.731 [0.304, 1.325] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.030, 0.226] | 1.423 [0.611, 2.579] | 0.481 [0.219, 0.860] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.091, 0.381] | 2.538 [1.384, 4.048] | 1.029 [0.524, 1.750] |
| lead 5 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 1.577 [0.571, 2.923] | 0.692 [0.213, 1.357] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.875] | 6.529 [4.217, 10.143] | 2.721 [1.604, 4.534] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 0.333 (no interval) | 0.167 (no interval) |

Recall with equal weight per regime: 0.362 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

persistence_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.038, 0.300] | 2.769 [1.708, 4.218] | 0.875 [0.522, 1.347] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.077, 0.400] | 3.423 [2.087, 5.167] | 1.173 [0.742, 1.750] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.080, 0.393] | 2.808 [1.524, 4.517] | 1.115 [0.576, 1.855] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 3.154 [1.848, 5.000] | 1.173 [0.676, 1.888] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.061, 0.345] | 2.808 [1.467, 4.684] | 1.125 [0.558, 1.921] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.188, 0.667] | 6.176 [3.625, 10.183] | 2.441 [1.336, 4.208] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 4.889 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.103 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_gbm:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.310, 0.667] | 1.346 [0.889, 2.000] | 0.760 [0.480, 1.216] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.455] | 1.077 [0.618, 1.778] | 0.606 [0.282, 1.136] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.038 [0.606, 1.714] | 0.587 [0.282, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 0.885 [0.519, 1.450] | 0.462 [0.226, 0.875] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.414] | 1.038 [0.611, 1.690] | 0.567 [0.273, 1.068] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.800] | 1.353 [0.800, 2.250] | 0.618 [0.321, 1.167] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.222 [1.625, 7.333] | 2.778 [1.286, 6.750] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 1.346 [0.758, 2.179] | 0.587 [0.299, 1.046] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.962 [1.815, 4.467] | 1.163 [0.726, 1.786] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.808 [1.515, 4.530] | 1.154 [0.570, 1.975] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.308 [1.419, 3.501] | 0.808 [0.500, 1.239] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.538 [1.444, 4.000] | 0.952 [0.552, 1.500] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.833, 9.910] | 2.632 [1.517, 4.469] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 5.111 [3.000, 10.008] | 2.639 [1.519, 5.438] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.285, 0.643] | 0.846 [0.500, 1.360] | 0.375 [0.210, 0.638] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.538 [1.600, 3.790] | 1.000 [0.614, 1.566] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.458] | 2.962 [1.815, 4.474] | 1.135 [0.712, 1.700] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.409] | 2.154 [1.304, 3.348] | 0.798 [0.491, 1.250] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.423 [1.478, 3.778] | 1.029 [0.620, 1.652] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.000 [3.000, 7.924] | 1.882 [1.118, 3.096] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 6.889 (no interval) | 3.833 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 0.808 [0.435, 1.321] | 0.337 [0.176, 0.575] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.231, 0.562] | 1.654 [1.000, 2.609] | 0.663 [0.397, 1.056] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.531] | 1.808 [1.138, 2.770] | 0.798 [0.484, 1.275] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.216, 0.571] | 1.577 [0.935, 2.440] | 0.654 [0.393, 1.036] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.645] | 2.346 [1.457, 3.667] | 1.135 [0.703, 1.784] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.437, 0.875] | 3.647 [2.111, 6.083] | 1.441 [0.839, 2.423] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 5.556 [3.153, 11.337] | 3.167 [1.786, 6.801] |

Recall with equal weight per regime: 0.437 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate+settle+h41+iorb:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.677] | 0.846 [0.476, 1.333] | 0.375 [0.203, 0.616] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.216, 0.565] | 1.654 [0.973, 2.600] | 0.663 [0.391, 1.059] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.808 [1.128, 2.800] | 0.798 [0.478, 1.286] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.577 [0.944, 2.423] | 0.654 [0.391, 1.044] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.346 [1.444, 3.654] | 1.135 [0.724, 1.780] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.428, 0.867] | 3.647 [2.125, 5.938] | 1.441 [0.833, 2.400] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.667 (no interval) | 3.278 (no interval) |

Recall with equal weight per regime: 0.562 (2018-19 11/17, 2020 2/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 1.231 [0.679, 2.056] | 0.538 [0.292, 0.909] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.769 [1.749, 4.185] | 1.096 [0.687, 1.700] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.962 [1.741, 4.697] | 1.231 [0.676, 2.058] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.469] | 2.385 [1.316, 3.929] | 0.846 [0.463, 1.391] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.417] | 2.154 [1.316, 3.333] | 0.865 [0.518, 1.381] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.353 [3.950, 10.000] | 2.588 [1.526, 4.313] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.889 (no interval) | 2.222 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.647] | 1.308 [0.737, 2.131] | 0.577 [0.296, 1.042] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.962 [1.895, 4.451] | 1.163 [0.732, 1.784] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.923 [1.636, 4.700] | 1.183 [0.603, 2.037] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 2.269 [1.393, 3.572] | 0.788 [0.491, 1.250] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.462 [1.400, 4.040] | 0.894 [0.514, 1.453] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.846, 9.834] | 2.632 [1.490, 4.475] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.778 (no interval) | 2.472 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 1.385 [0.848, 2.188] | 0.548 [0.333, 0.893] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.457] | 1.308 [0.824, 2.000] | 0.596 [0.310, 1.030] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.077 [0.667, 1.667] | 0.462 [0.250, 0.779] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.000 [0.615, 1.550] | 0.375 [0.210, 0.625] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.231 [0.774, 1.913] | 0.625 [0.352, 1.060] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.812] | 2.412 [1.500, 4.077] | 0.971 [0.579, 1.688] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.222 (no interval) | 2.639 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.696] | 1.538 [0.738, 2.706] | 0.712 [0.331, 1.288] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.393] | 2.615 [1.391, 4.300] | 0.904 [0.476, 1.519] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.538] | 2.500 [1.292, 4.214] | 0.856 [0.439, 1.438] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.478] | 1.962 [0.869, 3.500] | 0.625 [0.256, 1.145] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.444] | 2.192 [1.077, 3.769] | 0.779 [0.380, 1.357] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 5.353 [3.217, 8.500] | 2.059 [1.197, 3.375] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 0.917 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.688] | 1.500 [0.731, 2.612] | 0.673 [0.304, 1.196] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 2.192 [1.097, 3.709] | 0.702 [0.324, 1.214] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 2.538 [1.300, 4.311] | 0.837 [0.417, 1.432] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 2.000 [0.914, 3.654] | 0.635 [0.271, 1.191] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.000 [0.968, 3.565] | 0.673 [0.320, 1.198] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 5.235 [3.130, 8.571] | 1.971 [1.125, 3.342] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.333 [0.498, 3.000] | 0.583 [0.175, 1.393] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 1.538 [0.733, 2.630] | 0.712 [0.333, 1.224] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 1.962 [0.928, 3.459] | 0.779 [0.400, 1.320] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 2.000 [1.000, 3.429] | 0.788 [0.398, 1.320] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.560] | 1.846 [0.857, 3.222] | 0.692 [0.328, 1.183] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.000 [0.978, 3.421] | 0.798 [0.416, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 3.824 [2.035, 6.727] | 1.559 [0.812, 2.751] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.444 [0.500, 3.333] | 0.917 [0.262, 2.393] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.696] | 1.500 [0.727, 2.625] | 0.673 [0.311, 1.242] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.154 [1.052, 3.800] | 0.827 [0.430, 1.413] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 2.154 [1.050, 3.783] | 0.865 [0.452, 1.471] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.219, 0.571] | 1.962 [0.952, 3.389] | 0.779 [0.387, 1.359] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 1.885 [0.850, 3.357] | 0.769 [0.375, 1.336] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 4.059 [2.312, 7.000] | 1.618 [0.920, 2.896] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.889 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.640] | 1.500 [0.875, 2.438] | 0.663 [0.361, 1.167] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.038 [1.743, 4.810] | 1.125 [0.638, 1.817] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.567] | 2.577 [1.308, 4.400] | 0.894 [0.460, 1.523] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 2.385 [1.208, 4.116] | 0.856 [0.442, 1.466] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.476] | 3.077 [1.564, 5.125] | 1.327 [0.613, 2.329] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.412 [3.867, 10.501] | 2.735 [1.517, 4.786] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 1.639 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.686] | 1.538 [0.958, 2.474] | 0.673 [0.386, 1.144] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.481] | 3.077 [1.811, 4.801] | 1.135 [0.650, 1.792] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 2.538 [1.294, 4.223] | 0.856 [0.420, 1.422] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.519] | 2.423 [1.267, 4.100] | 0.827 [0.429, 1.406] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.519] | 3.115 [1.666, 5.242] | 1.375 [0.675, 2.445] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.412 [4.000, 10.200] | 2.735 [1.573, 4.657] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 1.583 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.650] | 1.500 [0.875, 2.476] | 0.663 [0.353, 1.163] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.923 [0.900, 3.500] | 0.760 [0.383, 1.319] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 1.731 [0.867, 3.040] | 0.769 [0.417, 1.306] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.231 [1.231, 3.773] | 0.933 [0.534, 1.538] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.808 [1.429, 4.900] | 1.269 [0.589, 2.330] |
| inside 2018-2019 | 17 | 11 | 0.647 (no interval) | 5.000 (no interval) | 2.279 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.500 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.676] | 1.538 [0.919, 2.500] | 0.673 [0.366, 1.171] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 2.154 [1.094, 3.778] | 0.837 [0.462, 1.424] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.577] | 1.962 [1.000, 3.375] | 0.827 [0.452, 1.397] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.038 [1.129, 3.444] | 0.846 [0.466, 1.423] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.692 [1.367, 4.728] | 1.240 [0.565, 2.296] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.875] | 5.176 [2.920, 9.000] | 2.324 [1.183, 4.364] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 1.472 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.353, 0.737] | 2.231 [1.207, 3.667] | 0.865 [0.490, 1.398] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.080, 0.400] | 1.923 [0.909, 3.294] | 0.692 [0.315, 1.188] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.535] | 2.462 [1.207, 4.185] | 0.837 [0.417, 1.417] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.524] | 2.000 [0.857, 3.606] | 0.663 [0.276, 1.198] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.447] | 2.269 [1.091, 3.900] | 0.769 [0.367, 1.320] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 5.059 [2.954, 8.214] | 1.809 [1.054, 2.922] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 1.222 [0.444, 2.800] | 0.694 [0.225, 1.750] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.733] | 2.154 [1.171, 3.455] | 0.817 [0.457, 1.304] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.115, 0.435] | 2.269 [1.185, 3.762] | 0.808 [0.398, 1.370] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.147, 0.481] | 2.269 [1.038, 3.857] | 0.721 [0.308, 1.250] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.038 [0.952, 3.587] | 0.673 [0.296, 1.207] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.480] | 2.231 [1.100, 3.808] | 0.750 [0.364, 1.289] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.176 [3.142, 8.375] | 1.838 [1.107, 3.000] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.348, 0.727] | 2.231 [1.200, 3.692] | 0.865 [0.475, 1.417] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.258, 0.609] | 1.385 [0.633, 2.545] | 0.596 [0.293, 1.040] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 2.308 [1.161, 3.953] | 0.904 [0.474, 1.513] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.579] | 1.923 [0.886, 3.530] | 0.712 [0.333, 1.299] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 1.923 [0.875, 3.353] | 0.769 [0.395, 1.292] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.917] | 4.412 [2.478, 7.286] | 1.662 [0.961, 2.775] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.355, 0.722] | 2.154 [1.138, 3.600] | 0.817 [0.432, 1.359] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 1.846 [0.840, 3.160] | 0.769 [0.380, 1.287] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.077 [1.000, 3.637] | 0.837 [0.437, 1.408] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.923 [0.965, 3.334] | 0.760 [0.396, 1.302] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 1.846 [0.852, 3.222] | 0.750 [0.387, 1.273] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.529 [2.704, 7.385] | 1.691 [1.000, 2.764] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.972 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.310, 0.682] | 2.115 [1.190, 3.355] | 0.817 [0.467, 1.316] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 3.038 [1.666, 5.000] | 1.221 [0.629, 2.088] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.538 [1.929, 5.895] | 1.433 [0.704, 2.510] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.522] | 2.731 [1.321, 4.783] | 1.144 [0.470, 2.170] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.529] | 3.115 [1.625, 5.278] | 1.308 [0.607, 2.371] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.294 [3.913, 10.183] | 2.574 [1.484, 4.412] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.000 (no interval) | 0.667 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.391, 0.760] | 2.615 [1.536, 4.067] | 1.019 [0.609, 1.594] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.483] | 3.115 [1.692, 5.000] | 1.269 [0.641, 2.120] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.462 [1.812, 5.561] | 1.356 [0.633, 2.321] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.188, 0.522] | 2.808 [1.367, 4.715] | 1.163 [0.487, 2.107] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 3.154 [1.680, 5.143] | 1.356 [0.653, 2.348] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.294 [3.818, 10.201] | 2.574 [1.440, 4.450] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 0.889 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.696] | 2.115 [1.242, 3.364] | 0.817 [0.487, 1.309] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.609] | 1.808 [0.857, 3.292] | 0.731 [0.371, 1.279] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.346 [1.265, 3.936] | 0.971 [0.547, 1.602] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.619] | 2.654 [1.318, 4.650] | 1.192 [0.536, 2.203] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.000 [1.604, 5.035] | 1.346 [0.674, 2.384] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.471 [3.214, 8.858] | 2.353 [1.308, 4.083] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 0.944 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 2.615 [1.500, 4.136] | 1.019 [0.600, 1.602] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.462 [1.231, 4.167] | 0.962 [0.515, 1.600] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.212, 0.571] | 2.077 [0.947, 3.680] | 0.827 [0.419, 1.435] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 2.423 [1.200, 4.162] | 1.154 [0.512, 2.151] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 2.923 [1.473, 4.880] | 1.327 [0.645, 2.352] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.913] | 5.647 [3.285, 9.125] | 2.397 [1.292, 4.179] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 1.028 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.346 [0.912, 2.000] | 0.712 [0.438, 1.150] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.571, 1.528] | 0.577 [0.309, 0.987] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.077 [0.636, 1.720] | 0.654 [0.336, 1.156] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.038 [0.606, 1.650] | 0.567 [0.288, 0.980] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.600] | 1.038 [0.607, 1.690] | 0.712 [0.357, 1.263] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.111 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 1.500 [1.000, 2.286] | 0.971 [0.556, 1.633] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 0.962 [0.542, 1.524] | 0.490 [0.212, 0.917] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.269 [0.760, 2.042] | 0.798 [0.391, 1.445] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.077 [0.630, 1.684] | 0.606 [0.276, 1.107] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.222 [1.500, 7.400] | 2.861 [1.222, 7.000] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.923 [1.909, 4.364] | 1.192 [0.727, 1.904] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.923 [1.806, 4.462] | 1.154 [0.707, 1.792] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.885 [1.636, 4.643] | 1.231 [0.636, 2.087] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.808 [1.034, 2.900] | 0.606 [0.342, 0.977] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.387] | 2.654 [1.538, 4.304] | 1.038 [0.600, 1.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.118 [3.749, 9.819] | 2.574 [1.428, 4.340] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.000 (no interval) | 3.111 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 2.500 [1.655, 3.765] | 0.952 [0.613, 1.477] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.615 [1.633, 3.950] | 1.029 [0.631, 1.563] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.885 [1.739, 4.500] | 1.115 [0.686, 1.750] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 2.154 [1.333, 3.333] | 0.837 [0.520, 1.338] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.121, 0.435] | 2.346 [1.400, 3.696] | 0.990 [0.591, 1.583] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 5.000 [3.056, 8.167] | 1.882 [1.125, 3.200] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 7.222 (no interval) | 3.889 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.650] | 2.500 [1.560, 3.870] | 1.058 [0.661, 1.641] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.462] | 2.808 [1.775, 4.300] | 1.106 [0.685, 1.750] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 2.885 [1.667, 4.696] | 1.240 [0.666, 2.145] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.474] | 2.500 [1.390, 4.087] | 0.933 [0.500, 1.525] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.385 [1.517, 3.692] | 1.048 [0.635, 1.671] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 6.471 [4.000, 10.309] | 2.632 [1.538, 4.438] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.885 [1.882, 4.295] | 1.183 [0.750, 1.893] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.000 [1.906, 4.522] | 1.183 [0.761, 1.813] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 3.000 [1.750, 4.778] | 1.260 [0.690, 2.103] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.885 [1.038, 3.077] | 0.615 [0.341, 1.000] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.577 [1.448, 4.131] | 0.981 [0.558, 1.565] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.118 [3.818, 9.909] | 2.574 [1.515, 4.344] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 5.556 [3.286, 10.573] | 2.889 [1.682, 6.000] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.290, 0.645] | 2.154 [1.457, 3.263] | 0.923 [0.609, 1.457] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 1.269 [0.815, 1.957] | 0.558 [0.300, 0.957] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.077 [0.636, 1.714] | 0.462 [0.236, 0.831] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.115 [0.682, 1.727] | 0.462 [0.250, 0.786] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.100, 0.379] | 1.423 [0.912, 2.263] | 0.769 [0.430, 1.307] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.812] | 2.706 [1.636, 4.556] | 1.044 [0.604, 1.808] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 5.222 [3.111, 10.667] | 3.222 [1.750, 7.083] |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 2.423 [1.333, 3.965] | 1.000 [0.558, 1.681] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.192 [1.087, 3.724] | 0.788 [0.389, 1.344] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.481] | 2.538 [1.273, 4.209] | 0.894 [0.461, 1.478] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.769 [0.744, 3.154] | 0.548 [0.212, 1.010] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 2.038 [0.950, 3.538] | 0.712 [0.327, 1.250] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.955] | 5.176 [3.059, 8.429] | 1.971 [1.150, 3.316] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.667 [0.692, 3.857] | 0.917 [0.318, 2.333] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.077 [1.742, 4.862] | 1.183 [0.674, 1.889] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.379] | 2.269 [1.148, 3.728] | 0.808 [0.402, 1.357] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.136, 0.483] | 2.462 [1.185, 4.139] | 0.817 [0.383, 1.398] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.378] | 1.846 [0.842, 3.218] | 0.625 [0.284, 1.119] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.154 [1.062, 3.694] | 0.769 [0.378, 1.327] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.958] | 5.176 [3.083, 8.385] | 1.971 [1.148, 3.306] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.667 [0.750, 3.625] | 0.833 [0.333, 1.959] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.556] | 2.423 [1.314, 4.000] | 1.000 [0.547, 1.656] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 1.731 [0.833, 3.059] | 0.692 [0.352, 1.182] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 2.115 [1.000, 3.750] | 0.856 [0.444, 1.475] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 2.115 [1.000, 3.783] | 0.846 [0.432, 1.467] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 1.962 [1.036, 3.333] | 0.798 [0.435, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 4.529 [2.562, 7.644] | 1.824 [1.042, 3.146] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.889 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 3.077 [1.724, 5.000] | 1.183 [0.667, 1.920] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.231 [1.100, 3.950] | 0.827 [0.425, 1.427] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.615 [0.725, 2.900] | 0.625 [0.307, 1.109] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.885 [0.896, 3.318] | 0.769 [0.392, 1.326] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.077 [0.968, 3.750] | 0.827 [0.423, 1.429] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.882 [2.850, 8.314] | 1.926 [1.104, 3.312] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 0.917 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.731 [1.667, 4.182] | 1.106 [0.670, 1.776] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 2.654 [1.500, 4.084] | 0.990 [0.552, 1.539] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.538 [1.272, 4.227] | 0.913 [0.472, 1.517] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.471] | 2.385 [1.241, 4.050] | 0.817 [0.414, 1.375] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 3.038 [1.520, 5.159] | 1.308 [0.609, 2.380] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 6.412 [3.900, 10.211] | 2.735 [1.571, 4.728] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.667 (no interval) | 1.417 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.696] | 3.423 [2.111, 5.333] | 1.337 [0.800, 2.135] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 2.577 [1.412, 4.209] | 0.971 [0.518, 1.602] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.172, 0.529] | 2.500 [1.241, 4.261] | 0.817 [0.389, 1.430] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.308 [1.143, 4.000] | 0.769 [0.367, 1.353] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.115 [1.580, 5.282] | 1.356 [0.632, 2.517] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 6.412 [3.818, 10.637] | 2.735 [1.509, 4.902] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 2.556 [1.300, 5.337] | 1.167 [0.577, 2.583] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.594] | 2.731 [1.680, 4.308] | 1.106 [0.655, 1.792] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.192 [1.125, 3.810] | 0.856 [0.463, 1.431] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 1.962 [0.957, 3.423] | 0.798 [0.409, 1.364] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.154 [1.129, 3.692] | 0.904 [0.493, 1.524] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.846 [1.474, 4.824] | 1.288 [0.606, 2.333] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.706 [3.400, 9.445] | 2.544 [1.438, 4.470] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.222 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.680] | 3.423 [2.080, 5.302] | 1.337 [0.796, 2.119] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.962 [1.058, 3.353] | 0.750 [0.420, 1.250] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.769 [0.906, 3.087] | 0.692 [0.364, 1.213] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.962 [1.000, 3.400] | 0.827 [0.453, 1.398] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 3.077 [1.666, 5.276] | 1.442 [0.750, 2.524] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 6.000 [3.625, 9.779] | 2.632 [1.500, 4.625] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.556 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.654] | 2.692 [1.438, 4.400] | 0.990 [0.554, 1.593] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 1.846 [0.826, 3.200] | 0.702 [0.310, 1.235] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.105, 0.444] | 2.500 [1.227, 4.231] | 0.875 [0.425, 1.500] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.692 [0.750, 3.126] | 0.548 [0.227, 1.050] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 1.846 [0.810, 3.286] | 0.625 [0.274, 1.125] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.882] | 4.471 [2.588, 7.333] | 1.603 [0.940, 2.659] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 1.111 [0.312, 2.667] | 0.667 [0.156, 1.875] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.636] | 3.115 [1.765, 5.100] | 1.106 [0.628, 1.803] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.118, 0.438] | 1.923 [0.919, 3.364] | 0.721 [0.341, 1.271] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.143, 0.500] | 2.423 [1.200, 4.200] | 0.798 [0.379, 1.403] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.692 [0.764, 3.092] | 0.548 [0.235, 1.022] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 1.923 [0.893, 3.381] | 0.644 [0.292, 1.147] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.000 [2.956, 8.250] | 1.794 [1.080, 2.978] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 0.889 [0.200, 2.000] | 0.361 [0.075, 0.900] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.285, 0.647] | 2.692 [1.469, 4.348] | 0.990 [0.546, 1.574] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 2.115 [1.000, 3.549] | 0.846 [0.444, 1.375] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.038 [0.950, 3.556] | 0.827 [0.424, 1.392] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.077 [1.000, 3.566] | 0.827 [0.431, 1.375] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 2.385 [1.280, 3.846] | 0.923 [0.508, 1.464] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 5.000 [2.909, 8.274] | 1.838 [1.087, 3.031] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 0.778 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 3.115 [1.658, 5.000] | 1.106 [0.600, 1.750] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 2.615 [1.333, 4.333] | 0.981 [0.523, 1.600] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.500 [0.633, 2.737] | 0.587 [0.271, 1.028] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.923 [0.917, 3.334] | 0.779 [0.402, 1.345] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 2.231 [1.033, 3.834] | 0.856 [0.426, 1.447] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 4.941 [2.833, 8.333] | 1.824 [1.042, 3.025] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 1.111 [0.444, 2.500] | 0.639 [0.212, 1.625] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.655] | 3.192 [1.818, 5.000] | 1.183 [0.702, 1.864] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 2.654 [1.385, 4.349] | 1.115 [0.552, 1.907] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 3.577 [1.923, 5.750] | 1.471 [0.733, 2.524] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.471] | 2.808 [1.360, 4.715] | 1.163 [0.478, 2.125] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 3.115 [1.600, 5.087] | 1.308 [0.605, 2.315] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.550, 1.000] | 6.294 [3.772, 10.004] | 2.574 [1.433, 4.376] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.539] | 1.000 [0.332, 2.432] | 0.667 [0.146, 1.938] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.304, 0.692] | 3.231 [1.846, 5.106] | 1.135 [0.639, 1.800] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 2.615 [1.292, 4.348] | 1.106 [0.509, 1.935] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.167, 0.528] | 3.500 [1.833, 5.667] | 1.394 [0.641, 2.411] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 2.846 [1.323, 4.875] | 1.173 [0.466, 2.181] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 3.192 [1.600, 5.316] | 1.356 [0.593, 2.441] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.294 [3.818, 10.336] | 2.574 [1.417, 4.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 0.667 [0.231, 1.400] | 0.333 [0.083, 0.822] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.654] | 3.192 [1.800, 5.137] | 1.183 [0.677, 1.881] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 2.038 [0.963, 3.500] | 0.827 [0.428, 1.398] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.000 [0.909, 3.567] | 0.808 [0.398, 1.412] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.615 [1.333, 4.429] | 1.260 [0.597, 2.267] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 3.038 [1.643, 5.000] | 1.365 [0.680, 2.389] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.059 [3.599, 9.883] | 2.515 [1.396, 4.308] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.316, 0.696] | 3.231 [1.875, 5.143] | 1.135 [0.651, 1.784] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 2.846 [1.500, 4.637] | 1.269 [0.610, 2.205] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 1.962 [0.933, 3.485] | 0.740 [0.366, 1.294] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 2.538 [1.270, 4.364] | 1.231 [0.583, 2.239] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.115 [1.692, 5.150] | 1.442 [0.750, 2.482] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.941 [3.524, 9.702] | 2.485 [1.400, 4.292] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.111 [0.500, 2.500] | 0.722 [0.271, 1.812] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.684] | 1.846 [1.243, 2.833] | 1.192 [0.727, 1.989] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.000 [0.536, 1.707] | 0.587 [0.236, 1.156] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.192 [0.694, 1.960] | 0.779 [0.387, 1.413] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.538 [0.943, 2.481] | 1.077 [0.566, 1.904] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.423 [0.871, 2.300] | 0.933 [0.483, 1.643] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.222 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_logistic+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.417] | 2.385 [1.556, 3.563] | 1.000 [0.625, 1.547] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.538 [0.937, 2.455] | 0.663 [0.375, 1.125] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.154 [0.656, 1.889] | 0.567 [0.283, 1.056] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.231 [0.710, 2.000] | 0.548 [0.286, 0.974] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.692 [1.613, 4.207] | 1.096 [0.648, 1.741] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.437, 0.867] | 3.941 [2.411, 6.358] | 1.368 [0.812, 2.215] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.333 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.346 [1.583, 3.435] | 1.029 [0.664, 1.615] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.385] | 1.538 [0.928, 2.412] | 0.663 [0.375, 1.110] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 1.577 [0.862, 2.633] | 0.692 [0.367, 1.207] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.192 [0.677, 1.944] | 0.538 [0.275, 0.950] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.478] | 3.000 [1.756, 4.667] | 1.212 [0.720, 1.903] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.481, 0.920] | 4.824 [2.866, 7.667] | 1.765 [1.062, 2.840] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.333 (no interval) | 3.722 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 3.500 [2.276, 5.144] | 1.442 [0.967, 2.143] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.133, 0.409] | 1.538 [0.917, 2.429] | 0.635 [0.342, 1.090] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.094, 0.375] | 1.308 [0.656, 2.286] | 0.587 [0.268, 1.088] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.364] | 1.731 [0.862, 3.039] | 0.702 [0.336, 1.265] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.080, 0.313] | 1.962 [1.143, 3.158] | 0.712 [0.388, 1.184] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.882 [3.714, 9.236] | 2.059 [1.292, 3.192] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 3.667 [1.857, 8.168] | 2.444 [1.154, 5.917] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.138, 0.409] | 2.346 [1.545, 3.480] | 0.990 [0.640, 1.536] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.500 [0.909, 2.392] | 0.644 [0.359, 1.100] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.077 [0.618, 1.750] | 0.538 [0.259, 1.000] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.316] | 1.154 [0.643, 1.900] | 0.519 [0.260, 0.929] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.128, 0.429] | 2.615 [1.500, 4.191] | 1.038 [0.600, 1.650] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.428, 0.867] | 3.941 [2.357, 6.462] | 1.368 [0.802, 2.250] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.667 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.368, 0.714] | 2.846 [1.928, 4.201] | 1.202 [0.790, 1.855] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 0.923 [0.500, 1.526] | 0.442 [0.193, 0.844] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.885 [0.469, 1.482] | 0.471 [0.208, 0.920] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 1.000 [0.478, 1.765] | 0.452 [0.196, 0.852] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.379] | 2.308 [1.343, 3.773] | 1.019 [0.586, 1.685] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 3.824 [2.214, 6.357] | 1.294 [0.765, 2.135] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.667] | 5.111 [2.823, 11.000] | 3.306 [1.694, 7.875] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.368] | 1.885 [0.941, 3.177] | 0.721 [0.362, 1.221] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.192 [0.469, 2.294] | 0.500 [0.190, 0.941] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.192 [0.500, 2.212] | 0.567 [0.211, 1.083] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.577 [0.697, 2.700] | 0.654 [0.280, 1.163] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 2.346 [1.160, 3.924] | 0.875 [0.447, 1.482] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 4.294 [2.500, 6.900] | 1.456 [0.830, 2.375] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.556 [0.250, 4.000] | 1.278 [0.214, 3.500] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.524] | 2.654 [1.375, 4.250] | 1.019 [0.550, 1.631] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.048, 0.286] | 1.423 [0.577, 2.619] | 0.500 [0.203, 0.927] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.577 [0.629, 2.839] | 0.548 [0.225, 0.988] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.364] | 1.423 [0.571, 2.534] | 0.500 [0.193, 0.909] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.391] | 2.038 [1.037, 3.476] | 0.837 [0.417, 1.438] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 1.000] | 5.118 [3.000, 8.273] | 1.779 [1.045, 2.844] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.667 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.241 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 1.885 [0.958, 3.259] | 0.721 [0.348, 1.250] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 1.308 [0.571, 2.348] | 0.519 [0.226, 0.935] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.045, 0.281] | 0.808 [0.300, 1.520] | 0.375 [0.155, 0.688] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.231, 0.550] | 1.962 [1.037, 3.269] | 0.769 [0.431, 1.261] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.154 [1.083, 3.647] | 0.865 [0.464, 1.453] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.384, 0.800] | 4.882 [2.935, 7.947] | 1.721 [1.037, 2.792] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 1.333 [0.389, 3.400] | 0.944 [0.235, 2.500] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.176, 0.530] | 2.654 [1.428, 4.149] | 1.019 [0.562, 1.596] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.385 [0.606, 2.380] | 0.500 [0.240, 0.852] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 0.808 [0.292, 1.560] | 0.375 [0.148, 0.702] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.308 [0.555, 2.391] | 0.519 [0.230, 0.923] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.731 [0.792, 3.000] | 0.702 [0.342, 1.202] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.824 [2.824, 7.467] | 1.691 [1.000, 2.614] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.444 [0.455, 3.750] | 1.056 [0.303, 2.876] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 2.462 [1.437, 3.800] | 0.990 [0.589, 1.569] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.808 [0.956, 2.953] | 0.798 [0.412, 1.356] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 1.231 [0.500, 2.214] | 0.538 [0.197, 1.024] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.367] | 1.231 [0.592, 2.188] | 0.567 [0.261, 1.039] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.471] | 3.192 [1.750, 5.304] | 1.442 [0.730, 2.533] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.471 [3.300, 9.188] | 2.176 [1.174, 3.908] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.333 [1.571, 7.333] | 2.194 [0.970, 5.125] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.565] | 3.192 [1.931, 4.955] | 1.250 [0.762, 1.938] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.654 [0.821, 2.778] | 0.673 [0.329, 1.154] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.324] | 1.731 [0.788, 3.056] | 0.635 [0.302, 1.094] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.103, 0.367] | 1.154 [0.545, 2.100] | 0.481 [0.228, 0.875] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.469] | 3.077 [1.583, 5.182] | 1.442 [0.693, 2.553] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 6.235 [3.720, 10.000] | 2.485 [1.387, 4.318] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 3.111 [1.538, 7.200] | 2.028 [0.928, 5.002] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.415] | 2.462 [1.444, 3.941] | 0.990 [0.586, 1.592] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 1.000 [0.394, 1.844] | 0.394 [0.161, 0.731] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 0.654 [0.323, 1.118] | 0.356 [0.161, 0.645] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 1.731 [0.857, 2.947] | 0.683 [0.360, 1.141] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.114, 0.444] | 2.885 [1.444, 4.815] | 1.231 [0.536, 2.204] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.800] | 6.118 [3.700, 9.500] | 2.485 [1.413, 4.182] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 2.333 [1.143, 5.504] | 1.444 [0.656, 3.608] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.560] | 3.192 [1.912, 4.790] | 1.250 [0.759, 1.880] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.077 [0.434, 1.917] | 0.375 [0.160, 0.667] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.280] | 0.654 [0.333, 1.120] | 0.327 [0.155, 0.594] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 1.846 [0.909, 3.154] | 0.702 [0.359, 1.194] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.056, 0.334] | 2.538 [1.159, 4.345] | 1.144 [0.467, 2.125] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.416, 0.867] | 6.176 [3.722, 9.818] | 2.500 [1.387, 4.250] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.333] | 1.889 [0.875, 4.167] | 1.139 [0.458, 2.786] |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 2.500 [1.265, 4.080] | 1.000 [0.528, 1.625] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.292] | 1.192 [0.467, 2.286] | 0.500 [0.190, 0.950] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.273] | 1.154 [0.441, 2.200] | 0.519 [0.170, 1.024] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.923 [0.893, 3.438] | 0.750 [0.333, 1.361] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 2.885 [1.418, 4.955] | 1.029 [0.509, 1.776] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.867] | 5.647 [3.399, 8.801] | 1.971 [1.172, 3.068] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.111 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 2.808 [1.548, 4.455] | 1.058 [0.603, 1.673] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.346 [0.517, 2.607] | 0.481 [0.189, 0.934] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.000, 0.233] | 1.115 [0.429, 2.167] | 0.394 [0.145, 0.781] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.133, 0.417] | 1.462 [0.640, 2.625] | 0.519 [0.228, 0.941] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.087, 0.385] | 2.269 [1.111, 3.857] | 0.856 [0.404, 1.486] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.235 [3.167, 8.182] | 1.794 [1.098, 2.818] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.333] | 1.222 [0.200, 3.333] | 1.000 [0.147, 2.917] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.500 [1.289, 4.034] | 1.000 [0.529, 1.586] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.303] | 1.154 [0.500, 2.000] | 0.577 [0.260, 0.988] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.050, 0.280] | 0.808 [0.259, 1.618] | 0.346 [0.112, 0.693] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.546] | 2.154 [1.136, 3.556] | 0.827 [0.452, 1.324] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.188, 0.526] | 2.654 [1.364, 4.278] | 0.981 [0.516, 1.566] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 5.176 [3.000, 8.215] | 1.882 [1.087, 2.946] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.667 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.207, 0.565] | 2.808 [1.500, 4.393] | 1.058 [0.575, 1.625] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.087, 0.407] | 1.692 [0.733, 3.000] | 0.702 [0.321, 1.205] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.059, 0.346] | 1.115 [0.400, 2.000] | 0.462 [0.175, 0.824] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 1.308 [0.556, 2.333] | 0.519 [0.229, 0.913] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.036, 0.294] | 1.385 [0.517, 2.462] | 0.548 [0.226, 0.964] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.412 [2.545, 7.000] | 1.574 [0.926, 2.472] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.000 (no interval) | 0.694 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 3.000 [1.640, 4.764] | 1.154 [0.648, 1.829] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.923 [0.889, 3.393] | 0.923 [0.402, 1.641] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.273] | 1.231 [0.517, 2.278] | 0.538 [0.192, 1.038] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 1.423 [0.704, 2.486] | 0.615 [0.304, 1.084] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 3.769 [2.055, 6.118] | 1.606 [0.805, 2.670] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.483, 0.917] | 6.824 [4.307, 10.445] | 2.676 [1.555, 4.334] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.222 [0.300, 3.400] | 1.222 [0.300, 3.400] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.207, 0.579] | 3.346 [1.921, 5.222] | 1.250 [0.742, 1.948] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 1.731 [0.750, 3.137] | 0.827 [0.337, 1.550] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.026, 0.227] | 1.192 [0.444, 2.269] | 0.413 [0.148, 0.793] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.385 [0.655, 2.421] | 0.548 [0.265, 0.948] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 3.000 [1.538, 5.042] | 1.375 [0.677, 2.400] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.471 [3.923, 10.273] | 2.544 [1.437, 4.250] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.333 (no interval) | 1.167 (no interval) |

Recall with equal weight per regime: 0.241 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 3.000 [1.645, 4.722] | 1.154 [0.644, 1.816] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.242] | 0.846 [0.240, 1.613] | 0.356 [0.110, 0.673] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.000, 0.229] | 0.769 [0.226, 1.556] | 0.298 [0.090, 0.592] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.517] | 2.577 [1.355, 4.211] | 1.163 [0.555, 2.065] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.769 [2.148, 5.843] | 1.567 [0.827, 2.538] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 6.706 [4.266, 10.557] | 2.735 [1.632, 4.570] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.308] | 0.444 [0.000, 1.333] | 0.444 [0.000, 1.333] |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.205, 0.579] | 3.346 [1.954, 5.148] | 1.250 [0.750, 1.942] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.053, 0.348] | 1.385 [0.485, 2.556] | 0.510 [0.188, 0.954] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.034, 0.292] | 1.077 [0.363, 1.968] | 0.413 [0.140, 0.760] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.501] | 2.538 [1.286, 4.333] | 1.173 [0.540, 2.141] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.059, 0.333] | 2.500 [1.136, 4.291] | 1.135 [0.463, 2.087] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 6.118 [3.695, 9.751] | 2.485 [1.380, 4.222] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.889 (no interval) | 0.722 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.680] | 1.769 [1.167, 2.750] | 1.163 [0.698, 1.952] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.000 [0.513, 1.667] | 0.615 [0.239, 1.188] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.389] | 1.000 [0.481, 1.714] | 0.644 [0.237, 1.277] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.115 [0.583, 1.857] | 0.702 [0.293, 1.361] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.154 [0.625, 1.900] | 0.683 [0.279, 1.326] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 2.750 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.615 [0.909, 2.526] | 0.587 [0.326, 0.947] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.077, 0.321] | 1.385 [0.826, 2.125] | 0.529 [0.312, 0.842] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.615 [0.921, 2.647] | 0.673 [0.350, 1.177] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 1.500 [0.900, 2.421] | 0.702 [0.368, 1.232] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.308 [1.316, 3.668] | 0.942 [0.537, 1.512] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.750] | 3.353 [1.687, 5.750] | 1.132 [0.562, 1.955] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.111 (no interval) | 3.194 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.174, 0.462] | 1.731 [1.064, 2.612] | 0.702 [0.420, 1.107] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.324] | 1.385 [0.846, 2.250] | 0.529 [0.317, 0.869] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.615 [0.879, 2.737] | 0.673 [0.337, 1.226] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.500 [0.875, 2.501] | 0.702 [0.371, 1.286] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 2.885 [1.714, 4.630] | 1.144 [0.685, 1.837] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.412 [2.667, 7.000] | 1.603 [0.976, 2.591] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 6.000 (no interval) | 3.167 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.731 [0.913, 2.905] | 0.702 [0.375, 1.192] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.368] | 1.500 [0.913, 2.368] | 0.587 [0.330, 0.985] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.308 [0.636, 2.286] | 0.558 [0.265, 1.020] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.467] | 1.808 [0.946, 3.105] | 0.788 [0.389, 1.417] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.061, 0.333] | 1.346 [0.684, 2.300] | 0.500 [0.250, 0.864] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 5.118 [3.181, 8.000] | 1.676 [1.026, 2.625] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.129, 0.414] | 1.577 [0.857, 2.520] | 0.577 [0.315, 0.945] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.385 [0.800, 2.222] | 0.529 [0.306, 0.869] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.429] | 1.577 [0.838, 2.611] | 0.663 [0.326, 1.193] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.385 [0.762, 2.278] | 0.654 [0.318, 1.221] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.231 [1.200, 3.616] | 0.885 [0.471, 1.469] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.308, 0.765] | 3.353 [1.722, 5.727] | 1.132 [0.580, 1.958] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.667 (no interval) | 2.972 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.294, 0.621] | 2.462 [1.643, 3.737] | 0.885 [0.571, 1.364] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 0.923 [0.536, 1.471] | 0.385 [0.192, 0.688] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.346 [0.684, 2.321] | 0.577 [0.271, 1.068] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 0.962 [0.516, 1.636] | 0.510 [0.218, 1.012] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.346 [0.607, 2.400] | 0.519 [0.215, 0.958] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 4.059 [2.470, 6.701] | 1.353 [0.810, 2.229] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.000 [0.409, 1.846] | 0.346 [0.160, 0.607] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.286] | 1.346 [0.536, 2.481] | 0.481 [0.179, 0.903] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.062, 0.321] | 1.885 [0.875, 3.217] | 0.740 [0.320, 1.323] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.276] | 1.654 [0.698, 2.945] | 0.673 [0.292, 1.219] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.000 [0.875, 3.572] | 0.760 [0.345, 1.350] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.261, 0.684] | 3.882 [1.923, 6.813] | 1.309 [0.661, 2.304] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.444 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_logistic_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.538 [0.687, 2.813] | 0.548 [0.250, 0.992] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.222] | 1.269 [0.552, 2.412] | 0.433 [0.177, 0.833] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.885 [0.903, 3.287] | 0.625 [0.286, 1.100] |
| lead 4 alone (fail) | 26 | 3 | 0.115 [0.030, 0.226] | 1.077 [0.409, 2.070] | 0.385 [0.141, 0.750] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 2.038 [1.000, 3.608] | 0.808 [0.400, 1.429] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.385, 0.810] | 4.059 [2.300, 6.923] | 1.353 [0.766, 2.304] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.333 (no interval) | 0.889 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_logistic_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.000 [0.433, 1.870] | 0.346 [0.167, 0.619] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.032, 0.233] | 0.692 [0.167, 1.500] | 0.250 [0.066, 0.516] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.769 [0.966, 2.968] | 0.750 [0.429, 1.239] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.565] | 1.846 [0.880, 3.192] | 0.712 [0.368, 1.194] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.069, 0.346] | 2.115 [1.080, 3.579] | 0.856 [0.460, 1.409] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.353 [2.461, 7.188] | 1.529 [0.882, 2.481] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.111 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.538 [0.695, 2.834] | 0.548 [0.250, 1.000] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.962 [0.955, 3.231] | 0.731 [0.375, 1.205] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 0.808 [0.316, 1.571] | 0.375 [0.151, 0.706] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.464] | 1.154 [0.500, 2.091] | 0.481 [0.215, 0.870] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.075, 0.333] | 1.692 [0.769, 3.000] | 0.750 [0.370, 1.323] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.316, 0.750] | 4.706 [2.750, 7.625] | 1.647 [0.973, 2.692] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.111 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.500 [0.784, 2.519] | 0.567 [0.304, 0.943] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.385] | 1.731 [0.889, 2.958] | 0.692 [0.338, 1.182] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.435] | 1.731 [0.867, 2.867] | 0.702 [0.336, 1.208] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.846 [0.947, 3.131] | 0.779 [0.383, 1.352] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 2.846 [1.394, 4.838] | 1.308 [0.575, 2.348] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.296, 0.769] | 5.059 [2.600, 8.752] | 2.029 [0.904, 3.875] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 1.806 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.474] | 2.154 [1.151, 3.500] | 0.827 [0.444, 1.339] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.808 [0.929, 2.955] | 0.663 [0.336, 1.096] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.409] | 1.885 [0.900, 3.200] | 0.654 [0.315, 1.094] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.103, 0.367] | 1.731 [0.791, 2.952] | 0.644 [0.305, 1.100] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 2.308 [1.217, 3.783] | 0.971 [0.509, 1.588] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 4.882 [2.800, 8.084] | 1.794 [0.984, 3.072] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 2.889 (no interval) | 1.639 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.071, 0.346] | 1.500 [0.788, 2.536] | 0.567 [0.309, 0.952] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.233] | 0.654 [0.167, 1.500] | 0.231 [0.060, 0.521] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.193, 0.500] | 2.038 [1.148, 3.286] | 0.904 [0.537, 1.445] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.269, 0.591] | 2.538 [1.428, 4.219] | 1.000 [0.595, 1.614] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 2.769 [1.375, 4.750] | 1.221 [0.537, 2.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.875] | 5.588 [3.294, 9.333] | 2.294 [1.259, 4.001] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.333 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.154 [1.133, 3.594] | 0.827 [0.450, 1.368] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 2.115 [1.100, 3.438] | 0.760 [0.404, 1.238] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 0.654 [0.308, 1.133] | 0.356 [0.149, 0.640] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.077 [1.194, 3.304] | 0.933 [0.546, 1.484] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.577 [0.567, 3.000] | 0.577 [0.214, 1.078] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.733] | 5.000 [2.923, 8.000] | 1.779 [1.029, 2.862] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.333] | 2.000 [1.000, 4.333] | 1.083 [0.482, 2.608] |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.151, 0.485] | 2.462 [1.258, 4.043] | 0.875 [0.456, 1.442] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.192 [0.461, 2.261] | 0.442 [0.161, 0.856] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.333] | 1.923 [0.946, 3.270] | 0.750 [0.349, 1.324] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 1.692 [0.741, 3.050] | 0.683 [0.293, 1.250] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.444] | 2.385 [1.154, 4.174] | 0.885 [0.435, 1.521] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.434, 0.867] | 5.647 [3.478, 9.003] | 1.926 [1.171, 3.075] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.000 [0.167, 2.750] | 0.806 [0.083, 2.350] |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_logistic_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.481] | 2.269 [1.125, 3.667] | 0.846 [0.433, 1.343] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.077 [0.364, 2.048] | 0.385 [0.129, 0.741] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.846 [0.840, 3.177] | 0.577 [0.250, 1.014] |
| lead 4 alone (fail) | 26 | 3 | 0.115 [0.029, 0.231] | 0.962 [0.308, 1.875] | 0.346 [0.102, 0.695] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.083, 0.394] | 2.385 [1.151, 4.000] | 0.904 [0.438, 1.546] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.857] | 5.471 [3.332, 8.584] | 1.897 [1.147, 2.967] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.667 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_logistic_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.462 [1.289, 4.044] | 0.875 [0.458, 1.440] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.385] | 1.577 [0.731, 2.783] | 0.712 [0.375, 1.210] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 1.692 [0.833, 2.867] | 0.663 [0.346, 1.095] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.219, 0.552] | 2.077 [1.077, 3.483] | 0.808 [0.448, 1.327] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.038, 0.286] | 1.654 [0.714, 2.945] | 0.596 [0.263, 1.071] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 4.765 [2.800, 7.668] | 1.750 [1.038, 2.884] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.667 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.212 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.148, 0.481] | 2.269 [1.125, 3.773] | 0.846 [0.435, 1.400] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.421] | 2.154 [1.153, 3.500] | 0.846 [0.474, 1.346] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.280] | 0.731 [0.189, 1.591] | 0.327 [0.098, 0.694] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.467] | 1.346 [0.591, 2.552] | 0.529 [0.231, 0.982] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.385 [0.526, 2.690] | 0.519 [0.214, 0.984] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.370, 0.810] | 4.824 [2.857, 7.668] | 1.750 [1.050, 2.783] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.556 (no interval) | 0.417 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_logistic_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.435] | 2.654 [1.435, 4.177] | 0.942 [0.489, 1.466] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.292] | 1.654 [0.692, 2.955] | 0.769 [0.287, 1.431] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.435] | 2.846 [1.485, 4.667] | 1.317 [0.621, 2.334] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.769 [0.895, 3.077] | 0.760 [0.379, 1.342] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.480] | 2.962 [1.548, 4.924] | 1.308 [0.617, 2.334] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 6.882 [4.333, 10.701] | 2.691 [1.568, 4.322] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.889 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 2.808 [1.552, 4.467] | 1.010 [0.562, 1.594] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.577 [0.628, 2.889] | 0.721 [0.257, 1.397] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 2.962 [1.469, 5.048] | 1.192 [0.510, 2.188] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.654 [0.750, 2.917] | 0.625 [0.285, 1.109] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.143, 0.485] | 3.000 [1.591, 5.091] | 1.365 [0.660, 2.433] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.706 [4.250, 10.500] | 2.632 [1.553, 4.432] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.667 (no interval) | 0.583 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.435] | 2.654 [1.478, 4.231] | 0.942 [0.524, 1.513] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.962 [0.250, 1.883] | 0.356 [0.096, 0.716] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.692 [0.889, 2.813] | 0.625 [0.344, 1.019] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.632] | 3.346 [1.846, 5.481] | 1.519 [0.790, 2.560] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 2.654 [1.270, 4.591] | 1.173 [0.492, 2.179] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.529 [4.000, 10.154] | 2.662 [1.516, 4.478] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 0.556 [0.182, 1.333] | 0.472 [0.125, 1.208] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.136, 0.469] | 2.808 [1.500, 4.409] | 1.010 [0.538, 1.580] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.615 [0.700, 2.789] | 0.596 [0.271, 1.010] |
| lead 3 alone (fail) | 26 | 3 | 0.115 [0.031, 0.222] | 0.731 [0.200, 1.500] | 0.288 [0.091, 0.593] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.150, 0.458] | 2.577 [1.267, 4.421] | 1.183 [0.509, 2.190] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.429] | 2.538 [1.133, 4.451] | 1.115 [0.428, 2.129] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 6.588 [4.053, 10.202] | 2.676 [1.536, 4.430] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.222 (no interval) | 0.139 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_quantile_skewt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.680] | 2.423 [1.555, 3.824] | 1.798 [1.029, 3.097] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 1.538 [0.964, 2.424] | 0.981 [0.500, 1.750] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.414] | 1.577 [0.938, 2.579] | 1.106 [0.554, 1.968] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.538 [1.697, 4.000] | 1.962 [1.209, 3.319] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.136, 0.429] | 1.846 [1.132, 3.000] | 1.375 [0.750, 2.500] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 1.412 [0.833, 2.400] | 0.706 [0.352, 1.375] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.222 (no interval) | 8.472 (no interval) |

Recall with equal weight per regime: 0.332 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_quantile_skewt_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.325, 0.667] | 1.885 [1.222, 2.952] | 1.250 [0.704, 2.179] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.500] | 1.654 [1.000, 2.579] | 1.096 [0.559, 1.943] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 1.500 [0.900, 2.400] | 1.000 [0.500, 1.781] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.719, 1.667] | 0.558 [0.286, 0.991] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.294 [0.731, 2.091] | 0.529 [0.250, 0.969] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.889 (no interval) | 4.194 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_quantile_skewt_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.692 [1.000, 2.696] | 0.606 [0.348, 0.974] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.029, 0.222] | 1.231 [0.708, 2.042] | 0.538 [0.296, 0.898] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.531] | 1.885 [1.000, 3.235] | 0.750 [0.407, 1.272] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.192 [1.400, 3.412] | 0.933 [0.583, 1.524] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.231, 0.550] | 2.462 [1.533, 3.895] | 1.096 [0.676, 1.767] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 4.529 [2.600, 7.300] | 1.588 [0.924, 2.600] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.889 (no interval) | 2.694 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.193, 0.514] | 2.308 [1.481, 3.429] | 1.000 [0.613, 1.583] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.031, 0.227] | 1.231 [0.708, 1.955] | 0.538 [0.297, 0.900] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.471] | 1.846 [0.970, 3.107] | 0.731 [0.393, 1.229] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.381, 3.381] | 0.923 [0.562, 1.510] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.632] | 3.154 [2.000, 4.824] | 1.327 [0.845, 2.094] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.765 [2.956, 7.584] | 1.676 [1.016, 2.705] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.091, 0.571] | 5.444 [3.286, 11.667] | 3.250 [1.821, 7.753] |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.556] | 2.154 [1.310, 3.350] | 0.808 [0.483, 1.298] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.050, 0.276] | 1.231 [0.666, 2.091] | 0.490 [0.258, 0.859] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.526] | 2.269 [1.187, 3.808] | 1.038 [0.518, 1.857] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.267, 0.594] | 2.846 [1.743, 4.421] | 1.163 [0.704, 1.830] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.000 [1.250, 3.105] | 0.827 [0.500, 1.342] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.294 [4.052, 9.695] | 2.338 [1.406, 3.817] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.667 (no interval) | 2.111 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.190, 0.519] | 1.654 [1.000, 2.656] | 0.596 [0.356, 0.974] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.024, 0.227] | 1.192 [0.686, 1.952] | 0.519 [0.295, 0.891] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 1.846 [0.964, 3.074] | 0.740 [0.396, 1.250] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.077 [1.310, 3.185] | 0.885 [0.536, 1.421] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.538] | 2.385 [1.435, 3.704] | 1.038 [0.628, 1.658] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 4.529 [2.667, 7.286] | 1.588 [0.926, 2.584] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.417 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.667] | 2.423 [1.618, 3.692] | 1.058 [0.646, 1.732] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.048, 0.280] | 1.308 [0.731, 2.150] | 0.558 [0.293, 0.971] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.529] | 2.654 [1.600, 4.167] | 1.231 [0.728, 2.022] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.207, 0.500] | 1.462 [0.964, 2.250] | 0.712 [0.406, 1.219] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.923 [1.143, 3.167] | 0.865 [0.484, 1.457] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.706 [2.857, 7.583] | 1.647 [1.009, 2.667] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 5.111 [2.778, 11.500] | 3.472 [1.643, 8.439] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 1.769 [0.912, 3.000] | 0.673 [0.350, 1.147] |
| lead 2 alone (fail) | 26 | 1 | 0.038 [0.000, 0.107] | 1.077 [0.500, 1.862] | 0.404 [0.189, 0.684] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 2.923 [1.599, 4.792] | 1.106 [0.603, 1.800] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.269 [1.118, 3.938] | 0.837 [0.412, 1.459] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.419] | 1.962 [0.933, 3.438] | 0.635 [0.300, 1.114] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 4.824 [2.765, 7.884] | 1.618 [0.905, 2.667] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.778 (no interval) | 1.083 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_quantile_skewt_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.425] | 1.654 [0.964, 2.586] | 0.625 [0.356, 1.008] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.615 [0.719, 3.000] | 0.529 [0.231, 0.989] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.062, 0.333] | 1.769 [0.852, 3.059] | 0.596 [0.284, 1.033] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.273] | 2.000 [0.960, 3.474] | 0.721 [0.359, 1.250] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 1.731 [0.818, 3.133] | 0.615 [0.290, 1.111] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 4.706 [2.764, 7.563] | 1.559 [0.893, 2.536] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.556 [0.749, 3.400] | 0.861 [0.357, 2.101] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_quantile_skewt_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.433] | 1.769 [0.900, 3.036] | 0.673 [0.341, 1.175] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.538] | 2.192 [1.182, 3.609] | 0.875 [0.474, 1.441] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.519] | 1.692 [0.857, 2.909] | 0.817 [0.425, 1.405] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.152, 0.480] | 1.462 [0.680, 2.563] | 0.625 [0.315, 1.068] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.143, 0.414] | 1.346 [0.548, 2.500] | 0.577 [0.261, 1.025] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.235 [2.454, 6.889] | 1.500 [0.896, 2.417] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.889 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 1.654 [0.917, 2.522] | 0.625 [0.344, 0.982] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.227, 0.545] | 2.308 [1.200, 3.765] | 0.942 [0.538, 1.500] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.231 [1.241, 3.523] | 0.904 [0.517, 1.427] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.517] | 1.385 [0.522, 2.522] | 0.529 [0.217, 0.933] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.467] | 1.808 [0.872, 3.074] | 0.712 [0.366, 1.182] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.423, 0.857] | 4.706 [2.800, 7.462] | 1.632 [1.000, 2.601] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.556 [0.714, 3.250] | 0.861 [0.327, 2.036] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.654 [0.923, 2.750] | 0.606 [0.352, 1.000] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 1.077 [0.500, 1.893] | 0.433 [0.197, 0.771] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 2.308 [1.226, 3.778] | 0.933 [0.508, 1.542] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.538 [1.417, 4.116] | 0.971 [0.554, 1.580] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.562] | 3.154 [1.690, 5.238] | 1.500 [0.758, 2.667] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 6.000 [3.368, 9.923] | 2.382 [1.261, 4.278] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.300] | 3.111 [1.667, 6.750] | 1.833 [0.885, 4.417] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.438] | 1.885 [1.133, 2.867] | 0.692 [0.397, 1.078] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.409] | 2.077 [1.185, 3.320] | 0.846 [0.451, 1.375] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.387] | 1.385 [0.719, 2.334] | 0.567 [0.297, 0.967] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.067, 0.321] | 2.308 [1.357, 3.567] | 1.077 [0.637, 1.712] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.469] | 3.115 [1.690, 5.100] | 1.519 [0.762, 2.605] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.471 [4.000, 10.059] | 2.559 [1.450, 4.250] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 3.667 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 1.654 [0.954, 2.773] | 0.606 [0.353, 1.013] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.222, 0.545] | 2.231 [1.217, 3.700] | 0.894 [0.518, 1.489] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.193, 0.500] | 1.346 [0.667, 2.417] | 0.663 [0.329, 1.205] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.242, 0.600] | 2.000 [1.037, 3.276] | 0.856 [0.465, 1.400] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.414] | 1.923 [0.857, 3.419] | 0.760 [0.365, 1.313] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.941 [3.000, 8.111] | 1.765 [1.091, 2.885] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.444 (no interval) | 1.333 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.435] | 1.885 [1.091, 2.938] | 0.692 [0.398, 1.109] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 2.846 [1.607, 4.485] | 1.212 [0.692, 1.938] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.385 [1.351, 3.773] | 0.971 [0.573, 1.530] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.187, 0.522] | 2.038 [1.033, 3.445] | 0.750 [0.393, 1.270] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.680] | 2.654 [1.538, 4.227] | 1.154 [0.682, 1.895] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.929] | 5.882 [3.667, 9.418] | 2.176 [1.341, 3.556] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.889 (no interval) | 1.528 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.476] | 2.846 [1.615, 4.412] | 1.096 [0.621, 1.703] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 1.231 [0.541, 2.134] | 0.442 [0.205, 0.750] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.560] | 2.885 [1.540, 4.723] | 1.058 [0.562, 1.718] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.269 [1.138, 3.843] | 0.837 [0.408, 1.403] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.471] | 2.077 [1.042, 3.429] | 0.692 [0.347, 1.145] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 5.706 [3.562, 8.917] | 1.926 [1.176, 2.976] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.444 [0.625, 3.337] | 0.972 [0.350, 2.500] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_quantile_skewt_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.111, 0.424] | 2.577 [1.500, 3.905] | 1.010 [0.592, 1.522] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.577 [0.679, 2.895] | 0.519 [0.220, 0.967] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 1.808 [0.838, 3.072] | 0.606 [0.277, 1.040] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.056, 0.343] | 2.192 [1.091, 3.638] | 0.779 [0.391, 1.288] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.115, 0.438] | 2.038 [1.000, 3.429] | 0.731 [0.379, 1.225] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.800] | 5.471 [3.466, 8.267] | 1.912 [1.183, 2.912] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 1.222 [0.600, 2.667] | 0.750 [0.292, 1.850] |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.136, 0.480] | 2.846 [1.607, 4.445] | 1.096 [0.633, 1.714] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 1.923 [0.957, 3.273] | 0.808 [0.420, 1.350] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 1.423 [0.650, 2.579] | 0.683 [0.315, 1.242] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.136, 0.478] | 1.462 [0.690, 2.600] | 0.625 [0.316, 1.069] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.120, 0.424] | 1.346 [0.545, 2.546] | 0.577 [0.259, 1.024] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.917] | 4.882 [2.889, 7.601] | 1.779 [1.071, 2.781] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.556 (no interval) | 1.083 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 2.577 [1.571, 3.876] | 1.010 [0.611, 1.544] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.593] | 2.308 [1.185, 3.765] | 0.942 [0.518, 1.516] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.385] | 1.769 [0.906, 2.958] | 0.760 [0.420, 1.240] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 1.962 [0.827, 3.462] | 0.731 [0.323, 1.286] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 2.077 [1.050, 3.464] | 0.798 [0.425, 1.312] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.294 [3.385, 8.182] | 1.897 [1.194, 2.917] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.667 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.486] | 2.654 [1.500, 4.161] | 1.029 [0.587, 1.600] |
| lead 2 alone (fail) | 26 | 1 | 0.038 [0.000, 0.107] | 1.308 [0.462, 2.462] | 0.625 [0.195, 1.264] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 3.500 [1.923, 5.637] | 1.567 [0.804, 2.661] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.187, 0.522] | 2.500 [1.290, 4.243] | 0.952 [0.500, 1.598] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 3.346 [1.863, 5.389] | 1.538 [0.787, 2.630] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.882 [4.295, 10.833] | 2.691 [1.533, 4.517] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.556 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.118, 0.435] | 2.615 [1.565, 4.000] | 1.010 [0.607, 1.548] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.419] | 2.077 [1.066, 3.534] | 0.981 [0.467, 1.734] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.438] | 2.308 [1.083, 4.000] | 0.990 [0.402, 1.913] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 2.923 [1.625, 4.737] | 1.442 [0.780, 2.441] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.560] | 3.346 [1.951, 5.308] | 1.596 [0.879, 2.667] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 7.235 [4.799, 11.067] | 2.912 [1.800, 4.667] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 2.000 [1.000, 4.750] | 1.611 [0.632, 4.250] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.136, 0.478] | 2.654 [1.435, 4.147] | 1.029 [0.567, 1.606] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 2.077 [1.042, 3.400] | 0.846 [0.442, 1.391] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.458] | 1.808 [0.848, 3.000] | 0.817 [0.395, 1.382] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.594] | 2.385 [1.097, 4.054] | 1.183 [0.533, 2.143] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.151, 0.467] | 1.885 [0.833, 3.278] | 0.750 [0.355, 1.275] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.529, 1.000] | 6.529 [4.045, 10.250] | 2.647 [1.545, 4.469] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.333 [0.571, 3.000] | 1.000 [0.308, 2.625] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.107, 0.429] | 2.615 [1.567, 4.000] | 1.010 [0.603, 1.570] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.595] | 2.654 [1.368, 4.477] | 1.067 [0.598, 1.750] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.121, 0.423] | 1.885 [1.034, 3.077] | 0.779 [0.457, 1.250] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.606] | 2.500 [1.238, 4.167] | 0.913 [0.465, 1.544] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.269 [1.820, 5.350] | 1.481 [0.774, 2.566] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 7.000 [4.615, 11.091] | 2.809 [1.712, 4.688] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.778 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+every_day | 0.52 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.44 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.34 (102) | 0.50 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+persist | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.25 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+every_day+scarce | 0.52 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.44 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+shrunk | 0.44 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.71 (17) | 0.34 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+hurdle_isotonic | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_isotonic+h41 | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_isotonic+settle | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_isotonic+settle+h41 | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.34 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt+h41 | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.34 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt+settle | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.34 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt+settle+h41 | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.34 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.46 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.46 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic+settle | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.46 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.46 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.47 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt+h41 | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.48 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt+settle | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.47 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt+settle+h41 | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.48 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.59 (17) | 0.56 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+gate | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.59 (17) | 0.47 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+persist | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.65 (17) | 0.46 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm_base+every_day+scarce | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.59 (17) | 0.56 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+shrunk | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.40 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic | 0.62 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.50 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_isotonic+h41 | 0.72 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.57 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_isotonic+settle | 0.62 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.50 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 0.72 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.57 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_platt | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.56 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_platt+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.65 (17) | 0.59 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+settle | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.56 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_platt+settle+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.65 (17) | 0.59 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic | 0.66 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.53 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.58 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle | 0.66 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.53 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.58 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_platt | 0.70 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.57 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_platt+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_state_platt+settle | 0.70 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.57 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.58 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.44 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+every_day+gate | 0.49 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.37 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+every_day+persist | 0.69 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.56 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+every_day+scarce | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.44 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+every_day+shrunk | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_isotonic | 0.51 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.41 (17) | 0.37 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_isotonic+h41 | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.41 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_isotonic+settle | 0.51 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.41 (17) | 0.37 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_isotonic+settle+h41 | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.41 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_platt | 0.58 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.53 (17) | 0.46 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt+h41 | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.21 (29) | 0.53 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt+settle | 0.58 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.53 (17) | 0.46 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_platt+settle+h41 | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.21 (29) | 0.53 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.41 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_isotonic+h41 | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.51 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_isotonic+settle | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.41 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.51 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.53 (17) | 0.48 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt+h41 | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.57 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt+settle | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.53 (17) | 0.48 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt+settle+h41 | 0.72 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.57 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day | 0.40 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.47 (17) | 0.31 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+gate | 0.35 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.53 (17) | 0.25 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+persist | 0.34 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.53 (17) | 0.24 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+scarce | 0.40 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.47 (17) | 0.31 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day+shrunk | 0.63 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_isotonic | 0.38 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.29 (17) | 0.24 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_isotonic+h41 | 0.53 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.41 (17) | 0.37 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_isotonic+settle | 0.38 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.29 (17) | 0.24 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 0.53 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.41 (17) | 0.37 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_platt | 0.44 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.41 (17) | 0.34 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+h41 | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.46 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+settle | 0.44 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.41 (17) | 0.34 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+settle+h41 | 0.59 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.46 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic | 0.62 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.41 (17) | 0.47 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 0.55 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.47 (17) | 0.38 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle | 0.62 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.41 (17) | 0.47 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 0.55 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.47 (17) | 0.38 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_platt | 0.66 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.53 (17) | 0.51 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_platt+h41 | 0.60 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.44 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_platt+settle | 0.66 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.53 (17) | 0.51 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 0.60 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.44 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt | 0.29 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.77 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day | 0.50 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.59 (17) | 0.41 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+gate | 0.44 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.71 (17) | 0.33 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+persist | 0.46 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.36 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+scarce | 0.50 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.59 (17) | 0.41 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+shrunk | 0.58 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.71 (17) | 0.47 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+hurdle_isotonic | 0.42 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.31 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 0.36 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.25 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 0.42 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.31 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 0.36 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.25 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt | 0.48 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.39 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 0.41 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.32 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle | 0.48 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.39 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 0.41 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.32 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0.47 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.35 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.44 (101) | 0.56 (9) | 0.46 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 0.47 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.35 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.44 (101) | 0.56 (9) | 0.46 (13) |
| risk_quantile_skewt_base+hurdle_state_platt | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.40 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 0.60 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.49 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.40 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 0.60 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.49 (101) | 0.56 (9) | 0.54 (13) |

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
