Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.4 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+every_day | 15 of 26 | 0.577 [0.385, 0.760] | 0.274 | 5.85 flat / 2.63 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+gate | 16 of 26 | 0.615 [0.444, 0.778] | 0.269 | 5.65 flat / 2.56 weighted (tier 1 on the flat count) | 1.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 15 of 26 | 0.577 [0.417, 0.741] | 0.246 | 4.35 flat / 2.03 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb | 16 of 26 | 0.615 [0.440, 0.786] | 0.250 | 4.38 flat / 2.07 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+persist | 15 of 26 | 0.577 [0.406, 0.750] | 0.269 | 5.50 flat / 2.46 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+every_day+scarce | 16 of 26 | 0.615 [0.433, 0.792] | 0.269 | 5.62 flat / 2.50 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+shrunk | 13 of 26 | 0.500 [0.324, 0.682] | 0.231 | 3.04 flat / 1.55 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic | 15 of 26 | 0.577 [0.389, 0.783] | 0.231 | 4.08 flat / 1.66 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.375, 0.778] | 0.231 | 3.85 flat / 1.45 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_isotonic+settle | 14 of 26 | 0.538 [0.367, 0.714] | 0.231 | 3.04 flat / 1.35 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.368, 0.719] | 0.231 | 3.23 flat / 1.40 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_platt | 15 of 26 | 0.577 [0.385, 0.760] | 0.269 | 5.23 flat / 2.36 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+h41 | 16 of 26 | 0.615 [0.424, 0.794] | 0.269 | 5.27 flat / 2.34 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_platt+settle | 14 of 26 | 0.538 [0.363, 0.719] | 0.231 | 4.15 flat / 1.97 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_platt+settle+h41 | 14 of 26 | 0.538 [0.351, 0.722] | 0.238 | 4.27 flat / 2.03 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic | 13 of 26 | 0.500 [0.308, 0.704] | 0.231 | 3.92 flat / 1.77 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.304, 0.692] | 0.231 | 3.85 flat / 1.61 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_isotonic+settle | 13 of 26 | 0.500 [0.320, 0.696] | 0.231 | 3.46 flat / 1.68 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 13 of 26 | 0.500 [0.318, 0.682] | 0.231 | 3.46 flat / 1.57 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+hurdle_state_platt | 13 of 26 | 0.500 [0.304, 0.696] | 0.269 | 4.73 flat / 2.33 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+h41 | 13 of 26 | 0.500 [0.304, 0.700] | 0.262 | 4.50 flat / 2.08 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+settle | 13 of 26 | 0.500 [0.312, 0.690] | 0.235 | 4.23 flat / 2.21 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+hurdle_state_platt+settle+h41 | 13 of 26 | 0.500 [0.314, 0.692] | 0.231 | 4.00 flat / 1.95 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+settle+h41 | 13 of 26 | 0.500 [0.320, 0.667] | 0.192 | 2.04 flat / 1.33 weighted (tier 1 on the flat count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_gbm_base+every_day | 17 of 26 | 0.654 [0.476, 0.824] | 0.284 | 6.04 flat / 2.73 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+gate | 16 of 26 | 0.615 [0.429, 0.792] | 0.269 | 5.73 flat / 2.55 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+persist | 16 of 26 | 0.615 [0.429, 0.800] | 0.269 | 5.73 flat / 2.59 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+every_day+scarce | 17 of 26 | 0.654 [0.467, 0.833] | 0.269 | 5.73 flat / 2.57 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+every_day+shrunk | 14 of 26 | 0.538 [0.368, 0.718] | 0.231 | 3.62 flat / 1.81 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic | 15 of 26 | 0.577 [0.385, 0.767] | 0.231 | 3.96 flat / 1.61 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+h41 | 15 of 26 | 0.577 [0.368, 0.778] | 0.231 | 3.96 flat / 1.58 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_isotonic+settle | 13 of 26 | 0.500 [0.308, 0.682] | 0.231 | 3.62 flat / 1.54 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.345, 0.727] | 0.231 | 3.73 flat / 1.54 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt | 16 of 26 | 0.615 [0.423, 0.800] | 0.269 | 5.12 flat / 2.28 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+h41 | 15 of 26 | 0.577 [0.375, 0.774] | 0.269 | 5.08 flat / 2.19 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_platt+settle | 13 of 26 | 0.500 [0.318, 0.680] | 0.262 | 4.50 flat / 2.01 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_platt+settle+h41 | 14 of 26 | 0.538 [0.355, 0.727] | 0.269 | 4.81 flat / 2.16 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic | 11 of 26 | 0.423 [0.235, 0.625] | 0.231 | 3.77 flat / 1.70 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.300, 0.700] | 0.231 | 3.85 flat / 1.61 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_isotonic+settle | 12 of 26 | 0.462 [0.273, 0.655] | 0.231 | 3.88 flat / 1.80 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 12 of 26 | 0.462 [0.276, 0.667] | 0.231 | 3.77 flat / 1.72 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt | 14 of 26 | 0.538 [0.333, 0.731] | 0.269 | 4.73 flat / 2.33 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+h41 | 13 of 26 | 0.500 [0.286, 0.714] | 0.250 | 4.38 flat / 1.97 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base+hurdle_state_platt+settle | 12 of 26 | 0.462 [0.275, 0.667] | 0.258 | 4.46 flat / 2.22 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 12 of 26 | 0.462 [0.278, 0.667] | 0.231 | 3.77 flat / 1.74 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic | 15 of 26 | 0.577 [0.391, 0.769] | 0.192 | 2.31 flat / 1.63 weighted (tier 1 on the flat count) | 1.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic+every_day | 11 of 26 | 0.423 [0.259, 0.600] | 0.265 | 4.54 flat / 2.10 weighted (tier 1 on the flat count) | 1.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+gate | 14 of 26 | 0.538 [0.370, 0.720] | 0.269 | 5.12 flat / 2.35 weighted (tier 1 on the flat count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+every_day+persist | 14 of 26 | 0.538 [0.368, 0.708] | 0.269 | 4.77 flat / 2.02 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+scarce | 11 of 26 | 0.423 [0.259, 0.600] | 0.231 | 4.19 flat / 1.89 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+every_day+shrunk | 14 of 26 | 0.538 [0.367, 0.708] | 0.231 | 4.08 flat / 1.94 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+hurdle_isotonic | 11 of 26 | 0.423 [0.250, 0.594] | 0.231 | 3.35 flat / 1.40 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+h41 | 14 of 26 | 0.538 [0.355, 0.714] | 0.231 | 3.77 flat / 1.58 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle | 12 of 26 | 0.462 [0.296, 0.625] | 0.231 | 3.15 flat / 1.31 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.350, 0.731] | 0.231 | 3.46 flat / 1.38 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+hurdle_platt | 11 of 26 | 0.423 [0.250, 0.607] | 0.269 | 4.65 flat / 2.14 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+h41 | 14 of 26 | 0.538 [0.364, 0.720] | 0.269 | 5.00 flat / 2.29 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_platt+settle | 12 of 26 | 0.462 [0.294, 0.632] | 0.238 | 4.27 flat / 1.91 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_logistic+hurdle_platt+settle+h41 | 13 of 26 | 0.500 [0.320, 0.679] | 0.262 | 4.50 flat / 1.92 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic | 12 of 26 | 0.462 [0.286, 0.650] | 0.231 | 3.58 flat / 1.44 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.333, 0.680] | 0.231 | 3.77 flat / 1.59 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle | 12 of 26 | 0.462 [0.294, 0.633] | 0.231 | 3.38 flat / 1.37 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 13 of 26 | 0.500 [0.320, 0.667] | 0.231 | 3.27 flat / 1.27 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt | 12 of 26 | 0.462 [0.285, 0.647] | 0.242 | 4.31 flat / 1.95 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.357, 0.714] | 0.238 | 4.27 flat / 1.93 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+hurdle_state_platt+settle | 12 of 26 | 0.462 [0.286, 0.632] | 0.254 | 4.42 flat / 1.91 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic+hurdle_state_platt+settle+h41 | 13 of 26 | 0.500 [0.323, 0.680] | 0.231 | 3.27 flat / 1.26 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| risk_logistic_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.192 | 1.92 flat / 1.27 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base+every_day | 10 of 26 | 0.385 [0.219, 0.559] | 0.231 | 4.12 flat / 1.80 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+gate | 13 of 26 | 0.500 [0.333, 0.677] | 0.269 | 4.81 flat / 2.09 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+every_day+persist | 13 of 26 | 0.500 [0.333, 0.679] | 0.269 | 4.58 flat / 1.81 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+scarce | 10 of 26 | 0.385 [0.216, 0.560] | 0.231 | 3.77 flat / 1.60 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_logistic_base+every_day+shrunk | 13 of 26 | 0.500 [0.333, 0.667] | 0.231 | 3.27 flat / 1.37 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic_base+hurdle_isotonic | 8 of 26 | 0.308 [0.154, 0.472] | 0.231 | 3.08 flat / 1.24 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+h41 | 11 of 26 | 0.423 [0.263, 0.600] | 0.231 | 3.38 flat / 1.36 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle | 10 of 26 | 0.385 [0.222, 0.560] | 0.231 | 2.77 flat / 1.15 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 10 of 26 | 0.385 [0.222, 0.556] | 0.192 | 2.42 flat / 0.92 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt | 10 of 26 | 0.385 [0.214, 0.562] | 0.250 | 4.38 flat / 1.99 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+h41 | 13 of 26 | 0.500 [0.333, 0.667] | 0.262 | 4.50 flat / 1.99 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_platt+settle | 12 of 26 | 0.462 [0.300, 0.630] | 0.231 | 3.88 flat / 1.75 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_platt+settle+h41 | 12 of 26 | 0.462 [0.292, 0.640] | 0.231 | 3.54 flat / 1.56 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic | 9 of 26 | 0.346 [0.176, 0.531] | 0.231 | 3.50 flat / 1.39 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.333, 0.682] | 0.231 | 3.85 flat / 1.56 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle | 10 of 26 | 0.385 [0.222, 0.550] | 0.231 | 2.54 flat / 1.01 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 12 of 26 | 0.462 [0.296, 0.636] | 0.231 | 2.88 flat / 1.12 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt | 11 of 26 | 0.423 [0.250, 0.606] | 0.231 | 4.15 flat / 1.82 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.364, 0.714] | 0.250 | 4.38 flat / 1.93 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic_base+hurdle_state_platt+settle | 12 of 26 | 0.462 [0.294, 0.630] | 0.231 | 3.58 flat / 1.65 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 13 of 26 | 0.500 [0.333, 0.667] | 0.231 | 3.62 flat / 1.61 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt | 16 of 26 | 0.615 [0.450, 0.773] | 0.231 | 3.85 flat / 3.11 weighted (tier 1 on the flat count) | 3.6 / 4.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 13 of 26 | 0.500 [0.325, 0.667] | 0.231 | 2.54 flat / 1.84 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base+every_day | 15 of 26 | 0.577 [0.409, 0.750] | 0.269 | 5.23 flat / 2.36 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.741] | 0.269 | 5.19 flat / 2.37 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+persist | 14 of 26 | 0.538 [0.368, 0.706] | 0.269 | 5.46 flat / 2.50 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+scarce | 15 of 26 | 0.577 [0.400, 0.739] | 0.269 | 5.00 flat / 2.24 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+every_day+shrunk | 14 of 26 | 0.538 [0.375, 0.722] | 0.269 | 4.69 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_quantile_skewt_base+hurdle_isotonic | 12 of 26 | 0.462 [0.286, 0.667] | 0.231 | 3.85 flat / 1.47 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 13 of 26 | 0.500 [0.320, 0.680] | 0.231 | 3.81 flat / 1.45 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 14 of 26 | 0.538 [0.360, 0.719] | 0.231 | 3.81 flat / 1.55 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 14 of 26 | 0.538 [0.355, 0.708] | 0.231 | 3.62 flat / 1.45 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt | 13 of 26 | 0.500 [0.321, 0.682] | 0.269 | 5.08 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 13 of 26 | 0.500 [0.333, 0.680] | 0.269 | 5.42 flat / 2.38 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle | 15 of 26 | 0.577 [0.400, 0.759] | 0.269 | 4.62 flat / 1.96 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 16 of 26 | 0.615 [0.435, 0.793] | 0.254 | 4.42 flat / 1.88 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 of 26 | 0.462 [0.276, 0.643] | 0.231 | 3.85 flat / 1.47 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 13 of 26 | 0.500 [0.310, 0.679] | 0.231 | 4.15 flat / 1.65 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 13 of 26 | 0.500 [0.316, 0.667] | 0.231 | 3.65 flat / 1.50 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 4.12 flat / 1.68 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt | 13 of 26 | 0.500 [0.333, 0.688] | 0.269 | 4.73 flat / 2.08 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 14 of 26 | 0.538 [0.360, 0.714] | 0.269 | 5.19 flat / 2.44 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 15 of 26 | 0.577 [0.391, 0.750] | 0.254 | 4.42 flat / 1.99 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 16 of 26 | 0.615 [0.429, 0.792] | 0.262 | 4.50 flat / 1.98 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 1.423 [0.812, 2.278] | 0.606 [0.315, 1.070] |
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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.285, 0.643] | 0.923 [0.545, 1.500] | 0.394 [0.221, 0.667] |
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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 0.769 [0.400, 1.261] | 0.298 [0.149, 0.511] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.231, 0.562] | 1.731 [1.069, 2.696] | 0.692 [0.429, 1.087] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.216, 0.571] | 1.769 [1.105, 2.720] | 0.788 [0.476, 1.263] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.216, 0.571] | 1.577 [0.935, 2.440] | 0.654 [0.393, 1.036] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.292, 0.645] | 2.346 [1.450, 3.667] | 1.135 [0.713, 1.750] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.437, 0.875] | 3.647 [2.111, 6.083] | 1.441 [0.839, 2.423] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.166, 0.714] | 5.667 [3.363, 11.405] | 3.139 [1.812, 6.679] |

Recall with equal weight per regime: 0.437 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+gate+settle+h41+iorb:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.677] | 0.808 [0.440, 1.280] | 0.337 [0.173, 0.548] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.216, 0.565] | 1.731 [1.048, 2.650] | 0.692 [0.422, 1.088] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.769 [1.087, 2.760] | 0.788 [0.467, 1.279] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.577 [0.944, 2.423] | 0.654 [0.391, 1.044] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.346 [1.458, 3.643] | 1.135 [0.724, 1.765] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.428, 0.867] | 3.647 [2.125, 5.938] | 1.441 [0.833, 2.400] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.778 (no interval) | 3.250 (no interval) |

Recall with equal weight per regime: 0.562 (2018-19 11/17, 2020 2/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.682] | 1.308 [0.741, 2.167] | 0.558 [0.310, 0.938] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.769 [1.749, 4.185] | 1.096 [0.687, 1.700] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.962 [1.741, 4.697] | 1.231 [0.676, 2.058] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.469] | 2.385 [1.316, 3.929] | 0.846 [0.463, 1.391] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 2.154 [1.316, 3.333] | 0.865 [0.518, 1.381] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 6.353 [3.950, 10.000] | 2.588 [1.526, 4.313] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.889 (no interval) | 2.222 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.647] | 1.385 [0.793, 2.263] | 0.596 [0.312, 1.077] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.923 [1.850, 4.400] | 1.144 [0.708, 1.750] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.923 [1.636, 4.700] | 1.183 [0.603, 2.037] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 2.231 [1.361, 3.529] | 0.769 [0.469, 1.230] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.423 [1.387, 4.000] | 0.856 [0.484, 1.425] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.235 [3.846, 9.834] | 2.632 [1.490, 4.475] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.444 (no interval) | 2.250 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 1.231 [0.731, 2.000] | 0.510 [0.300, 0.853] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.457] | 1.308 [0.824, 2.000] | 0.596 [0.310, 1.030] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.077 [0.667, 1.667] | 0.462 [0.250, 0.779] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.000 [0.615, 1.550] | 0.375 [0.210, 0.625] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.379] | 1.231 [0.774, 1.913] | 0.625 [0.352, 1.060] |
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
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.688] | 1.462 [0.700, 2.579] | 0.635 [0.275, 1.156] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 2.192 [1.097, 3.709] | 0.702 [0.324, 1.214] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.526] | 2.538 [1.300, 4.311] | 0.837 [0.417, 1.432] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 2.000 [0.914, 3.654] | 0.635 [0.271, 1.191] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.000 [0.968, 3.565] | 0.673 [0.320, 1.198] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.536, 1.000] | 5.235 [3.130, 8.571] | 1.971 [1.125, 3.342] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.222 [0.400, 2.714] | 0.472 [0.125, 1.143] |

Recall with equal weight per regime: 0.291 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 1.538 [0.733, 2.630] | 0.712 [0.333, 1.224] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 1.962 [0.928, 3.459] | 0.779 [0.400, 1.320] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 2.038 [1.018, 3.458] | 0.798 [0.409, 1.323] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.517] | 1.846 [0.857, 3.222] | 0.692 [0.328, 1.183] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.000 [0.978, 3.421] | 0.798 [0.416, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.875] | 3.824 [2.035, 6.727] | 1.559 [0.812, 2.751] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.556 [0.600, 3.400] | 0.944 [0.300, 2.425] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.696] | 1.462 [0.686, 2.586] | 0.635 [0.279, 1.172] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 2.154 [1.052, 3.800] | 0.827 [0.430, 1.413] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 2.115 [1.031, 3.728] | 0.827 [0.427, 1.427] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.219, 0.571] | 1.962 [0.952, 3.389] | 0.779 [0.387, 1.359] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 1.885 [0.850, 3.357] | 0.769 [0.375, 1.336] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 4.059 [2.312, 7.000] | 1.618 [0.920, 2.896] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.667 (no interval) | 1.000 (no interval) |

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
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.571] | 1.692 [0.842, 3.000] | 0.731 [0.390, 1.250] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.231 [1.231, 3.773] | 0.933 [0.534, 1.538] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.227, 0.619] | 2.808 [1.429, 4.900] | 1.269 [0.589, 2.330] |
| inside 2018-2019 | 17 | 11 | 0.647 (no interval) | 5.000 (no interval) | 2.279 (no interval) |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 1.389 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.321, 0.676] | 1.538 [0.919, 2.500] | 0.673 [0.366, 1.171] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 2.154 [1.094, 3.778] | 0.837 [0.462, 1.424] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 1.962 [1.000, 3.375] | 0.827 [0.452, 1.397] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.038 [1.129, 3.444] | 0.846 [0.466, 1.423] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.625] | 2.692 [1.367, 4.728] | 1.240 [0.565, 2.296] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.435, 0.875] | 5.176 [2.920, 9.000] | 2.324 [1.183, 4.364] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.556 (no interval) | 1.472 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.655] | 2.269 [1.130, 3.870] | 1.183 [0.550, 2.137] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.447] | 2.654 [1.414, 4.401] | 0.913 [0.469, 1.523] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.535] | 2.462 [1.192, 4.191] | 0.827 [0.400, 1.417] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 2.308 [1.095, 3.957] | 0.779 [0.369, 1.346] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.111, 0.447] | 2.269 [1.091, 3.900] | 0.769 [0.367, 1.320] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.882] | 5.353 [2.952, 9.078] | 2.353 [1.211, 4.250] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 1.222 [0.500, 2.857] | 0.667 [0.229, 1.701] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.654] | 1.962 [0.933, 3.333] | 0.904 [0.413, 1.625] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.115, 0.435] | 2.346 [1.237, 3.867] | 0.827 [0.417, 1.388] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.147, 0.481] | 2.308 [1.048, 3.900] | 0.731 [0.310, 1.263] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 2.346 [1.132, 4.000] | 0.788 [0.385, 1.352] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.192 [1.077, 3.769] | 0.750 [0.361, 1.300] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 5.176 [2.950, 8.701] | 2.088 [1.169, 3.700] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.333 (no interval) | 0.694 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 2.269 [1.125, 3.929] | 1.183 [0.519, 2.261] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.258, 0.609] | 1.885 [0.861, 3.500] | 0.750 [0.370, 1.333] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.577] | 2.269 [1.125, 3.895] | 0.885 [0.458, 1.489] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 2.000 [0.933, 3.667] | 0.731 [0.350, 1.313] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.625] | 1.692 [0.750, 3.131] | 0.683 [0.328, 1.212] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 4.588 [2.428, 8.101] | 2.176 [1.073, 4.096] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.750 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.276, 0.650] | 1.962 [0.914, 3.400] | 0.904 [0.392, 1.643] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.647] | 1.885 [0.889, 3.231] | 0.779 [0.390, 1.300] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.038 [0.963, 3.600] | 0.798 [0.407, 1.352] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.962 [1.000, 3.371] | 0.769 [0.409, 1.310] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 1.962 [0.921, 3.464] | 0.788 [0.395, 1.371] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.842] | 4.588 [2.571, 7.889] | 1.971 [1.091, 3.500] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.333 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 3.385 [1.808, 5.684] | 1.760 [0.850, 3.125] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.151, 0.471] | 3.077 [1.714, 5.044] | 1.337 [0.681, 2.324] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.611] | 3.692 [2.037, 6.106] | 1.500 [0.750, 2.625] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.423 [1.216, 4.051] | 0.837 [0.420, 1.410] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.172, 0.529] | 3.115 [1.625, 5.278] | 1.308 [0.607, 2.371] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 6.588 [3.952, 11.118] | 3.118 [1.666, 5.918] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.833 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.667] | 3.077 [1.625, 5.042] | 1.481 [0.698, 2.542] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.148, 0.500] | 3.000 [1.639, 4.842] | 1.288 [0.630, 2.227] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.500 [1.833, 5.632] | 1.365 [0.643, 2.341] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.565] | 2.462 [1.217, 4.094] | 0.827 [0.401, 1.389] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.188, 0.522] | 2.923 [1.500, 4.815] | 1.269 [0.580, 2.250] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 6.294 [3.643, 10.455] | 2.824 [1.525, 4.947] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.667 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.655] | 3.385 [1.833, 5.633] | 1.760 [0.865, 3.147] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.609] | 1.500 [0.656, 2.800] | 0.615 [0.295, 1.096] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.615] | 2.077 [1.081, 3.542] | 0.856 [0.474, 1.406] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.619] | 2.538 [1.292, 4.421] | 1.183 [0.527, 2.185] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.619] | 2.769 [1.423, 4.800] | 1.260 [0.587, 2.298] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.833] | 5.706 [3.143, 9.572] | 2.882 [1.512, 5.366] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.444 (no interval) | 0.944 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 3.077 [1.606, 5.143] | 1.481 [0.702, 2.600] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 2.000 [0.900, 3.467] | 0.798 [0.400, 1.352] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.212, 0.571] | 2.615 [1.208, 4.565] | 1.202 [0.533, 2.220] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 1.885 [0.925, 3.269] | 0.750 [0.375, 1.294] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.615] | 2.654 [1.235, 4.646] | 1.231 [0.550, 2.250] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 5.647 [3.091, 9.546] | 2.647 [1.367, 4.751] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 0.889 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.346 [0.900, 2.000] | 0.740 [0.457, 1.190] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 0.962 [0.594, 1.516] | 0.548 [0.302, 0.926] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.115 [0.679, 1.750] | 0.663 [0.345, 1.161] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.038 [0.606, 1.650] | 0.567 [0.288, 0.980] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.207, 0.563] | 1.038 [0.621, 1.667] | 0.712 [0.371, 1.250] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.824] | 1.412 [0.824, 2.375] | 0.647 [0.328, 1.215] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.222 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.333, 0.679] | 1.462 [0.962, 2.222] | 0.933 [0.532, 1.563] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 0.962 [0.542, 1.524] | 0.490 [0.212, 0.917] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.269 [0.760, 2.042] | 0.798 [0.391, 1.445] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.172, 0.458] | 1.115 [0.666, 1.800] | 0.663 [0.307, 1.225] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.424] | 1.077 [0.630, 1.684] | 0.606 [0.276, 1.107] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.800, 2.417] | 0.676 [0.312, 1.286] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 3.222 [1.500, 7.400] | 2.861 [1.222, 7.000] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.300, 0.636] | 2.846 [1.853, 4.264] | 1.144 [0.695, 1.818] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 2.923 [1.806, 4.462] | 1.154 [0.707, 1.792] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.885 [1.636, 4.643] | 1.231 [0.636, 2.087] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 2.000 [1.151, 3.222] | 0.663 [0.385, 1.065] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.387] | 2.654 [1.538, 4.304] | 1.038 [0.600, 1.667] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.118 [3.749, 9.819] | 2.574 [1.428, 4.340] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 5.889 (no interval) | 3.028 (no interval) |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.588] | 2.423 [1.600, 3.652] | 0.904 [0.570, 1.408] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.615 [1.633, 3.950] | 1.029 [0.631, 1.563] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.885 [1.739, 4.500] | 1.115 [0.686, 1.750] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 2.231 [1.375, 3.455] | 0.865 [0.543, 1.370] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.121, 0.435] | 2.346 [1.400, 3.696] | 0.990 [0.591, 1.583] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 5.000 [3.056, 8.167] | 1.882 [1.125, 3.200] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.111 (no interval) | 3.806 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.680] | 2.462 [1.538, 3.824] | 1.019 [0.629, 1.588] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.462] | 2.808 [1.775, 4.300] | 1.106 [0.685, 1.750] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 2.885 [1.667, 4.696] | 1.240 [0.666, 2.145] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.500 [1.390, 4.087] | 0.933 [0.500, 1.525] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.385 [1.517, 3.692] | 1.048 [0.635, 1.671] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.923] | 6.471 [4.000, 10.309] | 2.632 [1.538, 4.438] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 4.333 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.292, 0.636] | 2.769 [1.793, 4.143] | 1.125 [0.700, 1.786] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.962 [1.862, 4.445] | 1.163 [0.741, 1.794] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 3.000 [1.750, 4.778] | 1.260 [0.690, 2.103] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.923 [1.051, 3.154] | 0.625 [0.343, 1.019] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.375] | 2.538 [1.417, 4.087] | 0.942 [0.524, 1.518] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 6.118 [3.818, 9.909] | 2.574 [1.515, 4.344] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.750] | 5.000 [2.997, 9.500] | 2.556 [1.438, 5.375] |

Recall with equal weight per regime: 0.391 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_gbm_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 2.346 [1.655, 3.500] | 0.971 [0.651, 1.513] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 1.269 [0.815, 1.957] | 0.558 [0.300, 0.957] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.000 [0.581, 1.619] | 0.442 [0.214, 0.816] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.115 [0.682, 1.727] | 0.462 [0.250, 0.786] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 1.423 [0.912, 2.263] | 0.769 [0.430, 1.307] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.812] | 2.706 [1.636, 4.556] | 1.044 [0.604, 1.808] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.111, 0.751] | 5.333 [3.222, 10.750] | 3.250 [1.795, 7.125] |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

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
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.278, 0.647] | 3.077 [1.742, 4.862] | 1.183 [0.674, 1.889] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.379] | 2.269 [1.148, 3.728] | 0.808 [0.402, 1.357] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.111, 0.448] | 2.462 [1.185, 4.139] | 0.817 [0.383, 1.398] |
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
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 2.077 [0.960, 3.750] | 0.837 [0.419, 1.463] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.238, 0.606] | 1.962 [1.036, 3.333] | 0.798 [0.435, 1.326] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 4.529 [2.562, 7.644] | 1.824 [1.042, 3.146] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.889 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.273, 0.640] | 3.077 [1.724, 5.000] | 1.183 [0.667, 1.920] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.269 [1.153, 4.000] | 0.837 [0.437, 1.438] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.538 [0.667, 2.840] | 0.606 [0.286, 1.088] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 1.885 [0.896, 3.318] | 0.769 [0.392, 1.326] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.235, 0.611] | 2.115 [1.000, 3.775] | 0.808 [0.413, 1.389] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.882 [2.850, 8.314] | 1.926 [1.104, 3.312] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.556 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.731 [1.667, 4.182] | 1.106 [0.670, 1.776] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.615 [1.454, 4.059] | 0.981 [0.539, 1.529] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.538 [1.272, 4.227] | 0.913 [0.472, 1.517] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.161, 0.471] | 2.385 [1.241, 4.050] | 0.817 [0.414, 1.375] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 3.038 [1.520, 5.159] | 1.308 [0.609, 2.380] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.533, 0.957] | 6.412 [3.900, 10.211] | 2.735 [1.571, 4.728] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.667 (no interval) | 1.417 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

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
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.115 [1.087, 3.652] | 0.894 [0.484, 1.522] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.609] | 2.769 [1.406, 4.750] | 1.269 [0.581, 2.316] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.857] | 5.706 [3.400, 9.445] | 2.544 [1.438, 4.470] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.222 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.680] | 3.423 [2.080, 5.302] | 1.337 [0.796, 2.119] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 2.000 [1.094, 3.375] | 0.760 [0.432, 1.260] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.692 [0.823, 3.035] | 0.673 [0.340, 1.202] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 1.962 [1.000, 3.400] | 0.827 [0.453, 1.398] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 3.115 [1.700, 5.269] | 1.423 [0.737, 2.488] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.917] | 6.000 [3.625, 9.779] | 2.632 [1.500, 4.625] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.556 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.172, 0.542] | 3.077 [1.667, 5.168] | 1.423 [0.716, 2.580] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 2.231 [1.111, 3.826] | 0.798 [0.380, 1.364] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.105, 0.444] | 2.500 [1.207, 4.250] | 0.865 [0.412, 1.481] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.115, 0.441] | 2.000 [0.947, 3.522] | 0.663 [0.302, 1.161] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.083, 0.400] | 1.846 [0.810, 3.286] | 0.625 [0.274, 1.125] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.278, 0.778] | 5.118 [2.840, 8.820] | 2.250 [1.178, 4.234] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 1.222 [0.462, 2.864] | 0.667 [0.187, 1.834] |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.210, 0.571] | 2.923 [1.538, 4.945] | 1.212 [0.629, 2.092] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.118, 0.438] | 2.077 [1.000, 3.619] | 0.760 [0.364, 1.334] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.111, 0.455] | 2.423 [1.200, 4.209] | 0.788 [0.368, 1.400] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 2.308 [1.142, 4.000] | 0.760 [0.366, 1.318] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.467] | 2.269 [1.154, 3.950] | 0.827 [0.422, 1.432] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.900] | 5.235 [3.000, 9.000] | 2.147 [1.163, 3.851] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.222 [0.500, 2.750] | 0.583 [0.200, 1.466] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.526] | 3.077 [1.667, 5.040] | 1.423 [0.724, 2.538] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.273, 0.655] | 2.538 [1.286, 4.177] | 0.990 [0.538, 1.587] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.038 [0.950, 3.556] | 0.827 [0.424, 1.392] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.115 [1.043, 3.643] | 0.837 [0.446, 1.393] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.611] | 2.077 [1.045, 3.500] | 0.817 [0.425, 1.350] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.333, 0.833] | 5.059 [2.736, 8.900] | 2.309 [1.188, 4.319] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 0.833 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.571] | 2.923 [1.518, 4.783] | 1.212 [0.600, 2.011] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.276, 0.667] | 2.692 [1.417, 4.421] | 1.000 [0.538, 1.619] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.462 [0.606, 2.700] | 0.577 [0.258, 1.021] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 1.731 [0.828, 3.002] | 0.750 [0.385, 1.287] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 2.385 [1.237, 4.050] | 1.010 [0.545, 1.695] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.348, 0.846] | 4.882 [2.714, 8.364] | 2.118 [1.158, 3.635] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.501] | 1.667 [0.764, 3.500] | 0.972 [0.406, 2.250] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.588] | 3.308 [1.867, 5.400] | 1.519 [0.806, 2.703] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.120, 0.423] | 2.885 [1.500, 4.773] | 1.250 [0.583, 2.207] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 3.769 [2.087, 6.044] | 1.577 [0.817, 2.673] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 2.500 [1.261, 4.268] | 0.856 [0.425, 1.457] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.529] | 3.115 [1.600, 5.087] | 1.308 [0.605, 2.315] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 6.588 [3.762, 10.889] | 3.118 [1.618, 5.625] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 1.222 [0.500, 3.000] | 0.833 [0.250, 2.334] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_gbm_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.192, 0.571] | 3.231 [1.788, 5.222] | 1.356 [0.739, 2.289] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.440] | 2.923 [1.457, 4.862] | 1.260 [0.565, 2.250] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.167, 0.528] | 3.538 [1.846, 5.751] | 1.404 [0.648, 2.423] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 2.462 [1.194, 4.158] | 0.827 [0.395, 1.414] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 2.538 [1.233, 4.324] | 0.990 [0.454, 1.733] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.389, 0.895] | 6.294 [3.600, 10.692] | 2.824 [1.472, 5.072] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.545] | 0.778 [0.250, 1.625] | 0.361 [0.100, 0.875] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.214, 0.577] | 3.308 [1.903, 5.412] | 1.519 [0.806, 2.657] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.275, 0.667] | 3.000 [1.559, 5.000] | 1.356 [0.656, 2.375] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.615 [1.333, 4.435] | 1.240 [0.620, 2.182] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.077 [1.000, 3.637] | 0.865 [0.452, 1.474] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.240, 0.619] | 2.731 [1.371, 4.600] | 1.260 [0.583, 2.283] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.346, 0.834] | 6.176 [3.524, 10.584] | 3.000 [1.565, 5.584] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.750 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.208, 0.576] | 3.231 [1.826, 5.131] | 1.356 [0.717, 2.233] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.278, 0.667] | 2.269 [1.176, 3.688] | 0.865 [0.467, 1.398] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 1.808 [0.827, 3.200] | 0.702 [0.344, 1.229] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 1.962 [0.963, 3.455] | 0.817 [0.423, 1.391] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.242, 0.619] | 2.269 [1.172, 3.923] | 0.933 [0.490, 1.586] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.833] | 5.118 [2.905, 8.617] | 2.265 [1.226, 3.924] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.222 [0.500, 2.667] | 0.750 [0.288, 1.875] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.357, 0.727] | 1.654 [1.105, 2.550] | 1.029 [0.617, 1.728] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 0.962 [0.520, 1.637] | 0.548 [0.225, 1.060] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 1.154 [0.667, 1.895] | 0.712 [0.339, 1.296] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.538 [0.943, 2.481] | 1.077 [0.566, 1.904] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.385 [0.833, 2.238] | 0.894 [0.450, 1.594] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.818] | 1.471 [0.882, 2.462] | 0.706 [0.361, 1.344] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 3.889 (no interval) | 3.389 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

risk_logistic+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.130, 0.419] | 2.154 [1.280, 3.353] | 0.923 [0.523, 1.464] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.500 [0.896, 2.375] | 0.654 [0.359, 1.125] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.192 [0.704, 1.938] | 0.577 [0.293, 1.062] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.269 [0.731, 2.067] | 0.587 [0.295, 1.073] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.731 [1.629, 4.274] | 1.135 [0.661, 1.826] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.312, 0.750] | 3.824 [2.125, 6.333] | 1.368 [0.750, 2.250] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.889 (no interval) | 3.472 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.167, 0.462] | 2.231 [1.448, 3.263] | 1.038 [0.652, 1.609] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.385] | 1.462 [0.844, 2.305] | 0.635 [0.348, 1.073] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 1.615 [0.898, 2.652] | 0.702 [0.375, 1.216] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.231 [0.684, 2.000] | 0.577 [0.284, 1.038] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.478] | 3.038 [1.792, 4.750] | 1.250 [0.740, 1.983] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.481, 0.920] | 4.765 [2.849, 7.502] | 1.765 [1.062, 2.834] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.778 (no interval) | 3.444 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 2.038 [1.241, 3.095] | 0.913 [0.568, 1.440] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.133, 0.409] | 1.808 [1.125, 2.864] | 0.760 [0.420, 1.320] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.094, 0.375] | 1.269 [0.643, 2.222] | 0.577 [0.260, 1.080] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.105, 0.364] | 1.769 [0.895, 3.105] | 0.740 [0.347, 1.354] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.080, 0.313] | 2.000 [1.161, 3.214] | 0.750 [0.400, 1.292] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.917] | 5.294 [3.333, 8.385] | 1.765 [1.107, 2.789] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 3.778 [1.941, 8.337] | 2.500 [1.192, 6.051] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 2.077 [1.250, 3.261] | 0.904 [0.530, 1.455] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.577 [0.920, 2.522] | 0.663 [0.363, 1.147] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.077 [0.625, 1.750] | 0.529 [0.250, 0.982] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.316] | 1.154 [0.619, 1.913] | 0.538 [0.258, 0.987] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.128, 0.429] | 2.615 [1.500, 4.200] | 1.038 [0.586, 1.681] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.786] | 3.824 [2.125, 6.502] | 1.368 [0.731, 2.341] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.889 (no interval) | 2.889 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.294, 0.640] | 2.538 [1.666, 3.740] | 1.115 [0.717, 1.730] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 1.038 [0.581, 1.737] | 0.510 [0.227, 0.978] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.808 [0.429, 1.364] | 0.442 [0.184, 0.875] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 0.577 [0.250, 1.046] | 0.346 [0.108, 0.740] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.379] | 2.231 [1.258, 3.650] | 0.942 [0.510, 1.583] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 4.059 [2.440, 6.571] | 1.485 [0.898, 2.426] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 4.111 [2.076, 9.168] | 2.806 [1.317, 6.752] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.037, 0.292] | 1.500 [0.667, 2.591] | 0.587 [0.258, 1.022] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 1.308 [0.543, 2.440] | 0.529 [0.215, 0.971] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.269 [0.571, 2.286] | 0.615 [0.243, 1.147] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.577 [0.697, 2.700] | 0.654 [0.280, 1.163] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.133, 0.421] | 2.385 [1.200, 4.000] | 0.913 [0.469, 1.544] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.750] | 4.176 [2.166, 7.078] | 1.441 [0.729, 2.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.778 [0.438, 4.429] | 1.333 [0.281, 3.537] |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.147, 0.471] | 2.385 [1.200, 3.867] | 0.952 [0.500, 1.538] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.423 [0.571, 2.608] | 0.471 [0.181, 0.891] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.043, 0.290] | 1.231 [0.514, 2.185] | 0.500 [0.213, 0.896] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.318] | 1.500 [0.632, 2.636] | 0.577 [0.242, 1.057] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.308 [1.188, 3.934] | 0.933 [0.481, 1.600] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.929] | 4.765 [2.786, 7.700] | 1.691 [0.999, 2.727] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.889 (no interval) | 1.361 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.038, 0.304] | 1.500 [0.654, 2.625] | 0.587 [0.261, 1.038] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 1.231 [0.483, 2.231] | 0.500 [0.208, 0.908] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 0.808 [0.300, 1.527] | 0.375 [0.146, 0.700] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.193, 0.500] | 1.577 [0.809, 2.667] | 0.654 [0.359, 1.078] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.154 [1.083, 3.647] | 0.865 [0.464, 1.453] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.384, 0.800] | 4.235 [2.412, 7.143] | 1.529 [0.900, 2.531] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.445] | 1.111 [0.231, 2.881] | 0.889 [0.182, 2.358] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.478] | 2.385 [1.285, 3.810] | 0.952 [0.518, 1.511] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.269 [0.515, 2.251] | 0.471 [0.214, 0.821] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 0.808 [0.294, 1.563] | 0.375 [0.144, 0.697] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.385 [0.600, 2.444] | 0.500 [0.216, 0.880] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 1.769 [0.833, 3.048] | 0.712 [0.353, 1.211] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.706 [2.700, 7.385] | 1.676 [0.987, 2.615] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.626] | 1.111 [0.200, 3.000] | 0.806 [0.115, 2.286] |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.885 [0.974, 3.091] | 0.750 [0.402, 1.243] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.375] | 1.846 [0.970, 3.053] | 0.808 [0.420, 1.375] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 1.462 [0.720, 2.478] | 0.654 [0.299, 1.163] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.367] | 1.269 [0.619, 2.258] | 0.606 [0.274, 1.119] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.471] | 3.231 [1.778, 5.348] | 1.481 [0.757, 2.620] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.762] | 5.353 [2.998, 9.154] | 2.162 [1.088, 4.002] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 3.333 [1.571, 7.200] | 2.111 [0.937, 4.877] |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.269, 0.588] | 2.923 [1.756, 4.588] | 1.154 [0.710, 1.786] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.654 [0.833, 2.762] | 0.644 [0.312, 1.100] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.048, 0.273] | 1.038 [0.478, 1.880] | 0.433 [0.194, 0.783] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.320] | 1.231 [0.591, 2.209] | 0.558 [0.258, 1.033] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.469] | 3.154 [1.656, 5.269] | 1.490 [0.733, 2.636] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.485, 0.923] | 5.882 [3.500, 9.462] | 2.397 [1.303, 4.162] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 3.333 [1.727, 7.405] | 2.083 [0.967, 5.083] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 1.885 [0.969, 3.154] | 0.750 [0.402, 1.268] |
| lead 2 alone (fail) | 26 | 2 | 0.077 [0.000, 0.174] | 0.885 [0.312, 1.667] | 0.365 [0.134, 0.698] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 0.654 [0.333, 1.131] | 0.356 [0.167, 0.650] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.166, 0.462] | 1.500 [0.733, 2.539] | 0.606 [0.315, 1.023] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.480] | 2.846 [1.412, 4.774] | 1.221 [0.522, 2.195] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.381, 0.800] | 5.588 [3.262, 9.003] | 2.338 [1.277, 4.050] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.778 [0.800, 4.333] | 1.111 [0.442, 2.950] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 2.923 [1.750, 4.467] | 1.154 [0.702, 1.722] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 0.923 [0.312, 1.750] | 0.337 [0.128, 0.619] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 0.654 [0.333, 1.104] | 0.327 [0.155, 0.570] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.150, 0.467] | 1.846 [0.871, 3.177] | 0.654 [0.301, 1.130] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.379] | 2.500 [1.107, 4.305] | 1.135 [0.457, 2.100] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.416, 0.867] | 6.000 [3.583, 9.600] | 2.456 [1.353, 4.206] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.667 [0.765, 3.571] | 0.917 [0.350, 2.209] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.059, 0.346] | 1.462 [0.625, 2.593] | 0.606 [0.268, 1.098] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.292] | 1.500 [0.621, 2.840] | 0.577 [0.241, 1.081] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.269 [0.556, 2.348] | 0.606 [0.250, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.136, 0.412] | 1.769 [0.828, 3.188] | 0.702 [0.309, 1.263] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.150, 0.478] | 2.885 [1.441, 4.953] | 1.048 [0.520, 1.800] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.360, 0.833] | 4.647 [2.450, 7.858] | 1.588 [0.816, 2.717] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.556 (no interval) | 1.167 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 2.231 [1.138, 3.727] | 0.875 [0.458, 1.457] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.300] | 1.462 [0.625, 2.750] | 0.510 [0.216, 0.958] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 1.231 [0.500, 2.222] | 0.471 [0.200, 0.845] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.077, 0.333] | 1.385 [0.606, 2.435] | 0.567 [0.250, 1.015] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.136, 0.417] | 2.308 [1.120, 3.938] | 0.981 [0.486, 1.713] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.824 [2.808, 7.842] | 1.735 [1.008, 2.850] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.778 [0.533, 4.667] | 1.306 [0.250, 3.669] |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.065, 0.350] | 1.462 [0.636, 2.584] | 0.606 [0.267, 1.058] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.250] | 1.231 [0.476, 2.211] | 0.500 [0.202, 0.881] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.105, 0.368] | 0.846 [0.292, 1.652] | 0.385 [0.136, 0.735] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.227, 0.546] | 1.846 [0.865, 3.143] | 0.721 [0.363, 1.192] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.226, 0.563] | 2.654 [1.363, 4.286] | 0.981 [0.517, 1.563] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 4.765 [2.647, 7.617] | 1.765 [1.012, 2.786] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.778 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.212, 0.565] | 2.231 [1.080, 3.616] | 0.875 [0.435, 1.400] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.269 [0.531, 2.250] | 0.538 [0.227, 0.944] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.333] | 0.769 [0.222, 1.533] | 0.337 [0.103, 0.663] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 1.808 [0.818, 3.118] | 0.644 [0.292, 1.113] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.692 [0.700, 3.056] | 0.635 [0.267, 1.132] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.588 [2.588, 7.429] | 1.647 [0.940, 2.672] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.778 (no interval) | 0.556 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.037, 0.294] | 1.731 [0.773, 3.150] | 0.683 [0.309, 1.217] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 2.038 [0.893, 3.619] | 1.067 [0.435, 1.929] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.062, 0.333] | 2.115 [1.030, 3.697] | 1.106 [0.472, 2.029] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.136, 0.412] | 1.615 [0.833, 2.778] | 0.692 [0.347, 1.220] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 3.808 [2.083, 6.179] | 1.644 [0.841, 2.706] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.350, 0.833] | 5.824 [3.389, 9.586] | 2.294 [1.192, 3.908] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.455] | 1.444 [0.375, 3.881] | 1.306 [0.333, 3.562] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.167, 0.526] | 2.615 [1.316, 4.300] | 0.981 [0.500, 1.615] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.808 [0.786, 3.250] | 0.856 [0.316, 1.672] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.037, 0.281] | 1.423 [0.469, 2.657] | 0.731 [0.203, 1.487] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 1.192 [0.518, 2.158] | 0.529 [0.226, 0.966] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.412] | 2.462 [1.250, 4.151] | 1.067 [0.534, 1.810] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.926] | 5.765 [3.294, 9.539] | 2.324 [1.207, 4.013] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.038, 0.292] | 1.731 [0.722, 3.000] | 0.683 [0.292, 1.181] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.242] | 0.615 [0.105, 1.294] | 0.298 [0.062, 0.596] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 0.577 [0.194, 1.111] | 0.240 [0.093, 0.438] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.517] | 1.923 [1.000, 3.191] | 0.721 [0.394, 1.160] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.214, 0.562] | 3.769 [2.160, 5.842] | 1.567 [0.829, 2.525] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 6.471 [4.087, 10.252] | 2.676 [1.587, 4.475] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 0.556 [0.000, 1.583] | 0.472 [0.000, 1.396] |

Recall with equal weight per regime: 0.247 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.174, 0.542] | 2.615 [1.350, 4.316] | 0.981 [0.500, 1.606] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.286] | 0.692 [0.167, 1.452] | 0.279 [0.072, 0.568] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.276] | 0.423 [0.115, 0.840] | 0.173 [0.050, 0.330] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 1.962 [0.897, 3.501] | 0.673 [0.306, 1.200] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 1.692 [0.682, 3.156] | 0.635 [0.259, 1.177] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.867] | 4.647 [2.600, 7.700] | 1.662 [0.930, 2.765] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.667 (no interval) | 0.500 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.360, 0.714] | 1.692 [1.114, 2.591] | 1.038 [0.618, 1.738] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.038 [0.542, 1.722] | 0.625 [0.250, 1.198] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.077 [0.555, 1.792] | 0.663 [0.262, 1.295] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.421] | 1.115 [0.583, 1.857] | 0.702 [0.293, 1.361] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.154 [0.625, 1.900] | 0.683 [0.279, 1.326] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.812] | 1.471 [0.857, 2.456] | 0.706 [0.345, 1.346] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 2.778 (no interval) | 2.333 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_logistic_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 1.115 [0.600, 1.792] | 0.452 [0.217, 0.774] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.077, 0.321] | 1.231 [0.687, 1.962] | 0.442 [0.233, 0.721] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.577 [0.880, 2.593] | 0.663 [0.338, 1.167] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.379] | 1.500 [0.900, 2.421] | 0.702 [0.368, 1.232] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.423 [1.393, 3.895] | 1.058 [0.589, 1.771] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.235, 0.706] | 3.235 [1.571, 5.688] | 1.088 [0.523, 1.900] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.778 (no interval) | 3.139 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.174, 0.462] | 1.462 [0.886, 2.250] | 0.635 [0.371, 1.019] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.324] | 1.231 [0.692, 2.048] | 0.442 [0.239, 0.768] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 1.577 [0.833, 2.727] | 0.663 [0.324, 1.230] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.375] | 1.500 [0.875, 2.501] | 0.702 [0.371, 1.286] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.526] | 3.000 [1.774, 4.844] | 1.260 [0.750, 2.105] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.440, 0.882] | 4.353 [2.611, 7.000] | 1.588 [0.963, 2.575] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 5.667 (no interval) | 3.028 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.167, 0.455] | 1.346 [0.645, 2.333] | 0.596 [0.282, 1.050] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.133, 0.409] | 1.769 [1.115, 2.762] | 0.702 [0.410, 1.167] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.467] | 1.308 [0.667, 2.273] | 0.558 [0.265, 1.018] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.467] | 1.808 [0.946, 3.105] | 0.788 [0.389, 1.417] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.061, 0.333] | 1.500 [0.786, 2.501] | 0.625 [0.300, 1.141] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 5.235 [3.285, 8.154] | 1.721 [1.062, 2.688] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 1.972 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.103, 0.364] | 1.154 [0.611, 1.924] | 0.462 [0.220, 0.810] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.308 [0.706, 2.200] | 0.452 [0.234, 0.781] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.118, 0.429] | 1.462 [0.714, 2.455] | 0.615 [0.280, 1.141] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.346 [0.739, 2.209] | 0.635 [0.301, 1.188] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.308 [1.257, 3.818] | 0.962 [0.500, 1.663] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.706] | 3.235 [1.625, 5.612] | 1.088 [0.550, 1.893] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 2.556 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.227, 0.548] | 1.615 [0.974, 2.588] | 0.625 [0.367, 1.026] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.038 [0.586, 1.688] | 0.471 [0.224, 0.880] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 0.846 [0.450, 1.444] | 0.423 [0.177, 0.852] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.100, 0.370] | 0.962 [0.516, 1.636] | 0.510 [0.218, 1.012] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.500 [0.727, 2.629] | 0.644 [0.278, 1.216] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.857] | 3.353 [1.889, 5.700] | 1.088 [0.588, 1.875] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.031, 0.226] | 0.615 [0.281, 1.100] | 0.240 [0.110, 0.427] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.065, 0.320] | 1.423 [0.577, 2.600] | 0.500 [0.194, 0.943] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 2.308 [1.091, 4.000] | 0.885 [0.407, 1.557] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.276] | 1.731 [0.759, 3.096] | 0.750 [0.319, 1.379] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.115 [0.962, 3.786] | 0.875 [0.400, 1.594] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.200, 0.640] | 3.824 [1.840, 6.867] | 1.294 [0.625, 2.297] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.667 (no interval) | 1.139 (no interval) |

Recall with equal weight per regime: 0.153 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.421] | 1.846 [0.857, 3.269] | 0.663 [0.315, 1.175] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.292] | 1.308 [0.556, 2.500] | 0.442 [0.179, 0.865] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.391] | 1.654 [0.733, 2.955] | 0.596 [0.268, 1.080] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.231 [0.478, 2.334] | 0.452 [0.167, 0.870] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.308 [1.212, 4.000] | 0.962 [0.488, 1.703] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.385, 0.810] | 4.176 [2.333, 7.201] | 1.397 [0.750, 2.429] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.889 (no interval) | 1.278 (no interval) |

Recall with equal weight per regime: 0.197 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.032, 0.233] | 0.615 [0.280, 1.114] | 0.240 [0.112, 0.429] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.032, 0.233] | 0.769 [0.231, 1.591] | 0.269 [0.083, 0.542] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.500 [0.760, 2.600] | 0.673 [0.364, 1.143] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.269 [0.567, 2.294] | 0.529 [0.250, 0.935] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.100, 0.390] | 2.115 [1.074, 3.601] | 0.856 [0.454, 1.422] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.318, 0.737] | 3.412 [1.827, 5.751] | 1.235 [0.688, 2.050] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.556 (no interval) | 1.000 (no interval) |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.846 [0.846, 3.334] | 0.663 [0.302, 1.195] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.045, 0.278] | 0.769 [0.231, 1.571] | 0.298 [0.100, 0.583] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.324] | 0.808 [0.312, 1.583] | 0.404 [0.167, 0.750] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.346 [0.565, 2.486] | 0.500 [0.217, 0.910] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.471] | 1.577 [0.666, 2.895] | 0.635 [0.290, 1.157] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.273, 0.692] | 3.118 [1.519, 5.636] | 1.074 [0.500, 1.967] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.107, 0.364] | 1.115 [0.579, 1.905] | 0.490 [0.250, 0.850] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.385] | 1.808 [0.929, 3.072] | 0.731 [0.357, 1.250] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.400] | 1.692 [0.815, 2.864] | 0.692 [0.321, 1.211] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.167, 0.467] | 1.923 [0.999, 3.233] | 0.827 [0.388, 1.461] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.480] | 2.962 [1.483, 5.002] | 1.413 [0.633, 2.500] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.238, 0.722] | 5.000 [2.533, 8.751] | 2.015 [0.875, 3.875] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 1.944 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.189, 0.500] | 2.038 [1.087, 3.295] | 0.769 [0.403, 1.280] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.369] | 1.654 [0.800, 2.750] | 0.615 [0.283, 1.050] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 1.846 [0.852, 3.131] | 0.663 [0.304, 1.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.421] | 2.000 [1.000, 3.318] | 0.798 [0.395, 1.350] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 2.962 [1.565, 4.846] | 1.423 [0.700, 2.500] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.438, 0.867] | 5.176 [2.850, 8.801] | 2.044 [1.000, 3.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 1.889 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.115 [0.593, 2.000] | 0.490 [0.250, 0.860] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.233] | 0.423 [0.115, 0.889] | 0.135 [0.040, 0.275] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.278, 0.583] | 1.808 [1.000, 3.039] | 0.837 [0.483, 1.391] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.241, 0.538] | 2.192 [1.281, 3.583] | 0.942 [0.567, 1.517] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 2.692 [1.292, 4.651] | 1.183 [0.500, 2.203] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.318, 0.750] | 4.765 [2.643, 8.251] | 2.044 [1.014, 3.750] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.222 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.038 [1.088, 3.400] | 0.769 [0.405, 1.286] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.281] | 0.462 [0.148, 0.944] | 0.173 [0.058, 0.347] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.371] | 0.692 [0.333, 1.182] | 0.394 [0.175, 0.685] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.237, 0.536] | 2.077 [1.125, 3.429] | 0.865 [0.476, 1.413] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.190, 0.526] | 2.423 [1.067, 4.353] | 1.115 [0.439, 2.102] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 4.412 [2.179, 7.693] | 1.853 [0.786, 3.501] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.636] | 1.889 [0.867, 4.200] | 1.000 [0.431, 2.375] |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.043, 0.280] | 0.846 [0.395, 1.500] | 0.327 [0.156, 0.573] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.069, 0.333] | 1.577 [0.650, 2.941] | 0.538 [0.213, 1.009] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.846 [0.844, 3.250] | 0.721 [0.318, 1.289] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 1.538 [0.692, 2.737] | 0.692 [0.288, 1.264] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.500] | 3.000 [1.533, 5.048] | 1.163 [0.590, 1.938] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.241, 0.727] | 4.529 [2.357, 8.077] | 1.559 [0.809, 2.750] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.300] | 1.556 [0.500, 3.800] | 1.083 [0.250, 3.000] |

Recall with equal weight per regime: 0.168 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 2.308 [1.161, 3.773] | 0.846 [0.419, 1.375] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.286] | 1.308 [0.517, 2.409] | 0.442 [0.167, 0.828] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.389] | 1.731 [0.769, 3.000] | 0.577 [0.250, 1.029] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.462 [0.611, 2.650] | 0.577 [0.223, 1.083] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.476] | 2.423 [1.240, 4.048] | 1.038 [0.510, 1.781] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.941 [2.808, 8.083] | 1.735 [0.958, 2.889] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.778 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 4 | 0.154 [0.045, 0.286] | 0.846 [0.414, 1.500] | 0.327 [0.164, 0.583] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.030, 0.231] | 1.115 [0.364, 2.286] | 0.394 [0.139, 0.800] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.464] | 1.269 [0.536, 2.312] | 0.490 [0.216, 0.880] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 1.385 [0.625, 2.517] | 0.587 [0.288, 1.018] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.038, 0.286] | 1.654 [0.714, 2.945] | 0.596 [0.263, 1.071] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.333, 0.750] | 3.471 [1.888, 6.112] | 1.265 [0.706, 2.208] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 0.778 (no interval) | 0.528 (no interval) |

Recall with equal weight per regime: 0.182 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_logistic_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.522] | 2.308 [1.166, 4.000] | 0.846 [0.427, 1.461] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.320] | 1.000 [0.414, 1.929] | 0.481 [0.219, 0.865] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.692 [0.161, 1.549] | 0.288 [0.070, 0.629] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 1.846 [0.812, 3.474] | 0.692 [0.320, 1.292] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.154, 0.471] | 1.769 [0.714, 3.433] | 0.683 [0.300, 1.286] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.318, 0.741] | 3.824 [1.968, 6.688] | 1.368 [0.691, 2.417] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.111 (no interval) | 0.639 (no interval) |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.032, 0.222] | 1.077 [0.419, 2.087] | 0.365 [0.144, 0.713] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.043, 0.269] | 1.846 [0.739, 3.333] | 0.894 [0.308, 1.750] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.435] | 2.423 [1.143, 4.125] | 1.154 [0.478, 2.125] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.423] | 2.077 [0.943, 3.697] | 1.096 [0.444, 2.114] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.212, 0.562] | 3.654 [2.036, 5.864] | 1.615 [0.833, 2.719] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.286, 0.789] | 5.706 [3.190, 9.708] | 2.265 [1.163, 3.969] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.222 (no interval) | 0.972 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.227, 0.556] | 2.538 [1.353, 4.282] | 0.962 [0.523, 1.625] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.105, 0.375] | 1.885 [0.810, 3.560] | 0.856 [0.300, 1.763] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.524] | 2.769 [1.444, 4.616] | 1.192 [0.556, 2.167] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.097, 0.381] | 1.692 [0.833, 3.002] | 0.721 [0.342, 1.292] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 3.038 [1.580, 5.162] | 1.413 [0.667, 2.552] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 5.824 [3.350, 9.702] | 2.294 [1.196, 4.119] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 1.250 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 3 | 0.115 [0.026, 0.227] | 1.077 [0.435, 2.053] | 0.365 [0.147, 0.697] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.026, 0.227] | 1.308 [0.305, 2.800] | 0.692 [0.130, 1.580] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.267, 0.579] | 1.846 [0.967, 3.120] | 0.837 [0.466, 1.355] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.238, 0.526] | 2.269 [1.241, 3.722] | 0.942 [0.546, 1.500] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 2.654 [1.270, 4.591] | 1.173 [0.492, 2.179] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.316, 0.733] | 4.824 [2.583, 8.274] | 2.059 [1.000, 3.751] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.222 [0.500, 2.750] | 0.889 [0.325, 2.278] |

Recall with equal weight per regime: 0.282 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.542] | 2.538 [1.291, 4.179] | 0.962 [0.500, 1.573] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.048, 0.276] | 1.346 [0.324, 2.790] | 0.702 [0.138, 1.558] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.111, 0.364] | 0.385 [0.097, 0.821] | 0.135 [0.033, 0.283] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.231, 0.542] | 2.269 [1.118, 3.952] | 1.125 [0.500, 2.120] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.469] | 1.808 [0.771, 3.318] | 0.692 [0.312, 1.262] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 4.882 [2.621, 8.134] | 2.029 [0.955, 3.679] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.222 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.364, 0.700] | 2.115 [1.324, 3.385] | 1.529 [0.816, 2.682] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.129, 0.423] | 1.423 [0.852, 2.300] | 0.981 [0.493, 1.790] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.455] | 1.769 [1.130, 2.847] | 1.269 [0.707, 2.238] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.500 [1.667, 3.905] | 1.923 [1.169, 3.237] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 2.000 [1.286, 3.191] | 1.423 [0.796, 2.465] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.529, 0.882] | 1.294 [0.762, 2.154] | 0.559 [0.287, 1.024] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 8.667 (no interval) | 7.917 (no interval) |

Recall with equal weight per regime: 0.376 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

risk_quantile_skewt_base:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.325, 0.667] | 1.962 [1.273, 3.125] | 1.365 [0.759, 2.406] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.166, 0.458] | 1.500 [0.931, 2.333] | 0.913 [0.462, 1.609] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.538 [0.937, 2.375] | 0.981 [0.481, 1.724] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.115 [0.705, 1.684] | 0.558 [0.276, 0.988] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.038 [0.640, 1.591] | 0.510 [0.244, 0.907] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.810] | 1.176 [0.667, 1.909] | 0.471 [0.224, 0.865] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.111 (no interval) | 4.417 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+every_day:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.226, 0.556] | 2.423 [1.552, 3.640] | 0.952 [0.574, 1.520] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.069, 0.316] | 1.423 [0.864, 2.280] | 0.538 [0.316, 0.871] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.531] | 2.577 [1.571, 4.084] | 1.087 [0.663, 1.750] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.192 [1.400, 3.412] | 0.933 [0.583, 1.524] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.231, 0.550] | 2.462 [1.533, 3.895] | 1.096 [0.676, 1.767] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 4.824 [2.842, 7.750] | 1.706 [1.000, 2.769] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 6.000 (no interval) | 3.583 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+gate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.193, 0.514] | 2.115 [1.438, 3.131] | 0.885 [0.536, 1.467] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.071, 0.321] | 1.423 [0.846, 2.200] | 0.538 [0.315, 0.847] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.152, 0.471] | 2.577 [1.576, 4.000] | 1.087 [0.654, 1.733] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.200, 0.500] | 2.154 [1.381, 3.381] | 0.923 [0.562, 1.510] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.280, 0.632] | 3.154 [2.000, 4.824] | 1.327 [0.845, 2.094] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 4.765 [2.899, 7.638] | 1.721 [1.011, 2.813] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.091, 0.571] | 6.000 [3.583, 12.810] | 3.583 [1.954, 8.752] |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+persist:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.222, 0.556] | 2.308 [1.520, 3.474] | 1.010 [0.625, 1.619] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.080, 0.318] | 1.769 [0.963, 2.905] | 0.625 [0.336, 1.045] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.265, 0.595] | 2.692 [1.610, 4.258] | 1.288 [0.708, 2.197] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.267, 0.594] | 2.808 [1.706, 4.348] | 1.125 [0.680, 1.778] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.167, 0.458] | 2.038 [1.282, 3.150] | 0.837 [0.509, 1.360] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.824 [3.583, 9.357] | 2.206 [1.272, 3.751] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 3.056 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+scarce:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.562] | 2.385 [1.533, 3.611] | 0.942 [0.571, 1.516] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.074, 0.320] | 1.346 [0.800, 2.137] | 0.500 [0.286, 0.823] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.593] | 2.654 [1.667, 4.062] | 1.115 [0.695, 1.724] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.038 [1.276, 3.143] | 0.865 [0.520, 1.400] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.538] | 2.385 [1.435, 3.704] | 1.038 [0.628, 1.658] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.923] | 4.824 [2.869, 7.714] | 1.706 [1.000, 2.806] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 5.333 (no interval) | 3.250 (no interval) |

Recall with equal weight per regime: 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+every_day+shrunk:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.227, 0.543] | 2.077 [1.359, 3.200] | 1.000 [0.577, 1.688] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.419] | 1.462 [0.916, 2.280] | 0.558 [0.326, 0.914] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 2.500 [1.538, 3.889] | 1.173 [0.693, 1.932] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.207, 0.500] | 1.462 [0.965, 2.250] | 0.712 [0.407, 1.236] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 1.962 [1.171, 3.200] | 0.875 [0.493, 1.465] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 4.353 [2.533, 7.134] | 1.500 [0.875, 2.500] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 5.333 [2.917, 11.802] | 3.611 [1.725, 8.716] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.419] | 2.115 [1.208, 3.450] | 0.798 [0.458, 1.310] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.227] | 1.346 [0.727, 2.188] | 0.510 [0.278, 0.833] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.619] | 3.077 [1.720, 5.000] | 1.106 [0.608, 1.804] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.154 [1.028, 3.778] | 0.721 [0.337, 1.292] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.419] | 1.962 [0.933, 3.438] | 0.635 [0.300, 1.114] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.476, 0.917] | 4.882 [2.833, 8.000] | 1.618 [0.916, 2.654] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.889 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_quantile_skewt_base+hurdle_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.148, 0.471] | 2.077 [1.047, 3.522] | 0.808 [0.430, 1.359] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.105, 0.364] | 2.308 [1.303, 3.759] | 0.798 [0.444, 1.308] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.077, 0.387] | 1.923 [0.885, 3.296] | 0.673 [0.304, 1.152] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.062, 0.348] | 2.308 [1.133, 3.934] | 0.846 [0.420, 1.438] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.091, 0.385] | 1.423 [0.609, 2.650] | 0.529 [0.229, 0.989] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 4.882 [3.000, 7.786] | 1.647 [1.000, 2.611] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 1.778 [0.786, 4.000] | 1.083 [0.389, 2.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.433] | 2.115 [1.207, 3.429] | 0.798 [0.444, 1.330] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 2.423 [1.333, 3.934] | 1.058 [0.592, 1.732] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.531] | 1.538 [0.828, 2.500] | 0.779 [0.414, 1.322] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.194, 0.500] | 2.000 [0.917, 3.563] | 0.788 [0.390, 1.381] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.143, 0.414] | 1.346 [0.548, 2.500] | 0.577 [0.261, 1.025] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.481, 0.923] | 4.765 [2.792, 7.770] | 1.676 [0.973, 2.717] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 2.000 (no interval) | 1.306 (no interval) |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 2.077 [1.033, 3.429] | 0.808 [0.419, 1.317] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.227, 0.545] | 2.269 [1.160, 3.722] | 0.904 [0.492, 1.441] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.517] | 2.423 [1.281, 3.826] | 1.019 [0.583, 1.594] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.115, 0.417] | 1.731 [0.682, 3.091] | 0.683 [0.306, 1.180] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.318] | 1.808 [0.815, 3.150] | 0.779 [0.359, 1.346] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.920] | 4.529 [2.450, 7.546] | 1.588 [0.897, 2.641] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.444] | 1.889 [0.850, 4.200] | 1.194 [0.417, 3.051] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.464] | 2.423 [1.370, 3.762] | 0.885 [0.510, 1.393] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.045, 0.278] | 1.346 [0.735, 2.258] | 0.538 [0.293, 0.905] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 2.615 [1.412, 4.200] | 1.010 [0.558, 1.625] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.522] | 2.654 [1.500, 4.333] | 1.087 [0.612, 1.803] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.562] | 3.154 [1.690, 5.238] | 1.500 [0.758, 2.667] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.480, 0.923] | 6.059 [3.545, 10.000] | 2.382 [1.278, 4.282] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.300] | 3.222 [1.727, 7.000] | 1.944 [0.944, 4.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 2.538 [1.461, 3.952] | 0.962 [0.550, 1.512] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.105, 0.360] | 2.192 [1.375, 3.263] | 0.865 [0.509, 1.355] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.108, 0.444] | 1.808 [0.931, 3.101] | 0.808 [0.414, 1.385] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 3.115 [1.861, 4.842] | 1.394 [0.821, 2.221] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.423 [0.806, 2.305] | 0.740 [0.403, 1.250] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.235 [4.000, 9.701] | 2.324 [1.438, 3.627] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 3.889 (no interval) | 2.500 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 2.423 [1.414, 4.000] | 0.885 [0.519, 1.462] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 3.308 [2.026, 5.251] | 1.510 [0.896, 2.429] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 1.269 [0.679, 2.050] | 0.644 [0.333, 1.080] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.267, 0.577] | 2.077 [1.118, 3.450] | 0.913 [0.528, 1.512] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.129, 0.414] | 1.923 [0.857, 3.419] | 0.760 [0.365, 1.313] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.412 [3.321, 8.883] | 2.074 [1.218, 3.521] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.111 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.478] | 2.538 [1.441, 4.080] | 0.962 [0.552, 1.544] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.303, 0.636] | 2.654 [1.526, 4.143] | 1.144 [0.677, 1.810] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.292, 0.630] | 2.577 [1.439, 4.111] | 1.115 [0.658, 1.767] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.188, 0.519] | 2.385 [1.160, 4.091] | 0.923 [0.479, 1.554] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.189, 0.517] | 1.577 [0.800, 2.789] | 0.788 [0.410, 1.421] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.176 [3.000, 8.572] | 1.941 [1.104, 3.273] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.000 (no interval) | 1.750 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_isotonic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.121, 0.429] | 1.962 [1.029, 3.267] | 0.750 [0.402, 1.262] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.040, 0.280] | 1.346 [0.679, 2.261] | 0.510 [0.259, 0.845] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 2.615 [1.353, 4.296] | 0.952 [0.490, 1.579] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 2.308 [1.167, 3.875] | 0.846 [0.419, 1.413] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.176, 0.524] | 2.615 [1.333, 4.250] | 0.875 [0.440, 1.429] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 5.059 [2.909, 8.150] | 1.676 [0.944, 2.750] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.556 [0.667, 3.603] | 1.083 [0.417, 2.786] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

risk_quantile_skewt_base+hurdle_state_isotonic+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.467] | 2.077 [1.040, 3.522] | 0.808 [0.428, 1.353] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.478] | 2.192 [1.182, 3.478] | 0.788 [0.426, 1.261] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.086, 0.400] | 1.923 [0.857, 3.353] | 0.663 [0.284, 1.164] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.120, 0.440] | 2.692 [1.385, 4.429] | 0.981 [0.519, 1.603] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.389] | 1.577 [0.759, 2.714] | 0.615 [0.295, 1.042] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.909] | 5.471 [3.439, 8.572] | 1.926 [1.200, 3.039] |
| outside 2018-2019 | 9 | 1 | 0.111 [0.000, 0.286] | 1.667 [0.714, 3.600] | 1.139 [0.389, 2.750] |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 1.962 [1.031, 3.303] | 0.750 [0.395, 1.294] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.565] | 2.423 [1.300, 3.960] | 1.058 [0.589, 1.765] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.478] | 1.654 [0.774, 2.833] | 0.769 [0.375, 1.348] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.552] | 2.308 [1.115, 3.905] | 0.904 [0.468, 1.481] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.417] | 1.346 [0.545, 2.546] | 0.577 [0.259, 1.024] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.421, 0.867] | 4.706 [2.625, 7.846] | 1.662 [0.941, 2.804] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.667 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 2.077 [1.042, 3.448] | 0.808 [0.419, 1.317] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.259, 0.593] | 2.346 [1.222, 3.833] | 0.923 [0.508, 1.490] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.121, 0.444] | 2.115 [1.136, 3.545] | 0.875 [0.509, 1.417] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.520] | 2.192 [1.077, 3.778] | 0.875 [0.460, 1.473] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.227, 0.556] | 2.192 [1.083, 3.728] | 1.010 [0.516, 1.719] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 5.176 [3.000, 8.365] | 1.882 [1.083, 3.040] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 2.111 (no interval) | 1.306 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_platt:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.115, 0.438] | 1.769 [0.962, 2.858] | 0.663 [0.366, 1.077] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.286] | 1.654 [0.690, 3.002] | 0.827 [0.283, 1.675] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 3.538 [2.000, 5.625] | 1.538 [0.812, 2.565] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.226, 0.556] | 3.038 [1.593, 5.048] | 1.433 [0.686, 2.513] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.615] | 3.692 [2.038, 5.889] | 1.529 [0.783, 2.584] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 6.294 [3.722, 10.184] | 2.456 [1.312, 4.322] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 1.778 (no interval) | 1.361 (no interval) |

Recall with equal weight per regime: 0.226 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 1/5).

risk_quantile_skewt_base+hurdle_state_platt+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.517] | 2.615 [1.462, 4.193] | 0.981 [0.559, 1.587] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.417] | 2.115 [1.108, 3.520] | 1.067 [0.479, 1.938] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.115, 0.448] | 2.500 [1.296, 4.305] | 1.231 [0.611, 2.195] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.476] | 3.077 [1.791, 4.934] | 1.385 [0.821, 2.275] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.097, 0.369] | 1.462 [0.800, 2.401] | 0.788 [0.417, 1.327] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.474, 0.923] | 6.588 [4.190, 10.400] | 2.662 [1.574, 4.403] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.429] | 2.556 [1.235, 6.000] | 2.028 [0.805, 5.250] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_quantile_skewt_base+hurdle_state_platt+settle:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.120, 0.417] | 1.769 [0.950, 2.867] | 0.663 [0.367, 1.088] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.321, 0.677] | 3.115 [1.800, 4.864] | 1.413 [0.812, 2.278] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.174, 0.519] | 2.308 [1.071, 4.000] | 1.192 [0.530, 2.190] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.261, 0.593] | 2.462 [1.278, 4.118] | 1.212 [0.597, 2.163] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.130, 0.412] | 1.885 [0.833, 3.278] | 0.750 [0.355, 1.275] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 5.765 [3.333, 9.527] | 2.338 [1.265, 4.157] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 1.889 [0.818, 4.333] | 1.333 [0.432, 3.500] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_quantile_skewt_base+hurdle_state_platt+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.182, 0.500] | 2.615 [1.406, 4.286] | 0.981 [0.540, 1.606] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.294, 0.625] | 2.385 [1.370, 3.760] | 1.048 [0.612, 1.660] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 2.346 [1.333, 4.000] | 1.163 [0.602, 2.121] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.184, 0.517] | 2.308 [1.058, 4.054] | 0.894 [0.438, 1.529] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.235, 0.556] | 1.808 [0.875, 3.257] | 0.827 [0.417, 1.450] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 5.941 [3.625, 9.868] | 2.382 [1.328, 4.150] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.778 (no interval) | 1.222 (no interval) |

Recall with equal weight per regime: 0.341 (2018-19 13/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+every_day | 0.52 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.65 (17) | 0.45 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.65 (17) | 0.26 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb | 0.34 (102) | 0.50 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+persist | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.71 (17) | 0.27 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+every_day+scarce | 0.52 (102) | 0.25 (4) | – | 0.00 (5) | 0.38 (29) | 0.65 (17) | 0.45 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+shrunk | 0.44 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.33 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+hurdle_isotonic | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_isotonic+h41 | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_isotonic+settle | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_isotonic+settle+h41 | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.27 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.34 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt+h41 | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.34 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt+settle | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.34 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_platt+settle+h41 | 0.42 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.34 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic | 0.51 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.41 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic+h41 | 0.51 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.41 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic+settle | 0.51 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.41 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_isotonic+settle+h41 | 0.51 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.41 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.48 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt+h41 | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.48 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt+settle | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.48 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+hurdle_state_platt+settle+h41 | 0.58 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.48 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.55 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+gate | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.46 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+persist | 0.56 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.71 (17) | 0.46 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm_base+every_day+scarce | 0.66 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.55 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+every_day+shrunk | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.71 (17) | 0.41 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_isotonic | 0.62 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.50 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_isotonic+h41 | 0.72 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.57 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_isotonic+settle | 0.62 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.65 (17) | 0.50 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_isotonic+settle+h41 | 0.72 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.57 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_platt | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.56 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_platt+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.65 (17) | 0.59 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_platt+settle | 0.68 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.65 (17) | 0.56 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_platt+settle+h41 | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.65 (17) | 0.59 (101) | 0.44 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_isotonic | 0.65 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.53 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_isotonic+h41 | 0.69 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.55 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle | 0.65 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.53 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm_base+hurdle_state_isotonic+settle+h41 | 0.69 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.55 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_state_platt | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.53 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+h41 | 0.69 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.55 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm_base+hurdle_state_platt+settle | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.53 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base+hurdle_state_platt+settle+h41 | 0.69 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.59 (17) | 0.55 (101) | 0.44 (9) | 0.62 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day | 0.57 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.53 (17) | 0.47 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+gate | 0.48 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.59 (17) | 0.37 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+persist | 0.49 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.59 (17) | 0.38 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+scarce | 0.57 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.53 (17) | 0.47 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+every_day+shrunk | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.38 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_isotonic | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.47 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_isotonic+h41 | 0.64 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.50 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_isotonic+settle | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.47 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_isotonic+settle+h41 | 0.64 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.50 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_platt | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.47 (17) | 0.50 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_platt+h41 | 0.70 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.59 (17) | 0.56 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_platt+settle | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.47 (17) | 0.50 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_platt+settle+h41 | 0.70 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.59 (17) | 0.56 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+hurdle_state_isotonic | 0.43 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.47 (17) | 0.30 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+h41 | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.40 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+settle | 0.43 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.47 (17) | 0.30 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_isotonic+settle+h41 | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.40 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic+hurdle_state_platt | 0.49 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.47 (17) | 0.37 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt+h41 | 0.60 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.46 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt+settle | 0.49 (102) | 0.25 (4) | – | 0.20 (5) | 0.17 (29) | 0.47 (17) | 0.37 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+hurdle_state_platt+settle+h41 | 0.60 (102) | 0.25 (4) | – | 0.20 (5) | 0.14 (29) | 0.53 (17) | 0.46 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+every_day | 0.31 (102) | 0.25 (4) | – | 0.00 (5) | 0.45 (29) | 0.47 (17) | 0.26 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+every_day+gate | 0.27 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.53 (17) | 0.21 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+every_day+persist | 0.27 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.53 (17) | 0.20 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+every_day+scarce | 0.31 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.47 (17) | 0.26 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+every_day+shrunk | 0.42 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.65 (17) | 0.30 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base+hurdle_isotonic | 0.28 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.35 (17) | 0.19 (101) | 0.44 (9) | 0.46 (13) |
| risk_logistic_base+hurdle_isotonic+h41 | 0.55 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.53 (17) | 0.40 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_isotonic+settle | 0.28 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.35 (17) | 0.19 (101) | 0.44 (9) | 0.46 (13) |
| risk_logistic_base+hurdle_isotonic+settle+h41 | 0.55 (102) | 0.00 (4) | – | 0.00 (5) | 0.17 (29) | 0.53 (17) | 0.40 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_platt | 0.35 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.27 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.44 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+settle | 0.35 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.27 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_platt+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.44 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic | 0.43 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.35 (17) | 0.33 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+h41 | 0.60 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.44 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle | 0.43 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.35 (17) | 0.33 (101) | 0.44 (9) | 0.54 (13) |
| risk_logistic_base+hurdle_state_isotonic+settle+h41 | 0.60 (102) | 0.25 (4) | – | 0.00 (5) | 0.17 (29) | 0.59 (17) | 0.44 (101) | 0.56 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt | 0.49 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.41 (17) | 0.40 (101) | 0.44 (9) | 0.46 (13) |
| risk_logistic_base+hurdle_state_platt+h41 | 0.62 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.46 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic_base+hurdle_state_platt+settle | 0.49 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.41 (17) | 0.40 (101) | 0.44 (9) | 0.46 (13) |
| risk_logistic_base+hurdle_state_platt+settle+h41 | 0.62 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.65 (17) | 0.46 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt | 0.31 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.85 (13) |
| risk_quantile_skewt_base | 0.29 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base+every_day | 0.57 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.47 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+gate | 0.47 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.37 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+persist | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.42 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+scarce | 0.57 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.47 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+every_day+shrunk | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.40 (101) | 0.67 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_isotonic | 0.47 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.36 (101) | 0.44 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+h41 | 0.53 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.41 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle | 0.47 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.36 (101) | 0.44 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_isotonic+settle+h41 | 0.53 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.41 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.45 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt+h41 | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.49 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.45 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_platt+settle+h41 | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.49 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0.49 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.38 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+h41 | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle | 0.49 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.38 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_isotonic+settle+h41 | 0.54 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_platt | 0.50 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.39 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+h41 | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle | 0.50 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.39 (101) | 0.56 (9) | 0.54 (13) |
| risk_quantile_skewt_base+hurdle_state_platt+settle+h41 | 0.62 (102) | 0.25 (4) | – | 0.20 (5) | 0.28 (29) | 0.65 (17) | 0.49 (101) | 0.56 (9) | 0.62 (13) |

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
