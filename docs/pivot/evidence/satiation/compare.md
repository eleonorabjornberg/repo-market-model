# Time-varying satiation level (#587)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 10 / 1.42 fail | fail | 10 / 2.42 fail | 0 / 0.33 fail |
| projected_reserves | 8 / 2.35 fail | fail | 8 / 3.35 fail | 0 / 0.44 fail |
| risk_gbm+combined | 10 / 1.12 fail | fail | 10 / 1.85 fail | 2 / 0.89 fail |
| structural_rolling | 11 / 2.62 fail | fail | 11 / 4.19 fail | 4 / 3.22 fail |
| structural_fitted | 10 / 1.42 fail | fail | 10 / 2.42 fail | 0 / 0.33 fail |
| projected_hinge_fixed | 8 / 2.35 fail | fail | 8 / 3.77 fail | 0 / 0.44 fail |
| projected_rolling | 11 / 3.23 fail | fail | 11 / 5.23 fail | 4 / 5.44 fail |
| projected_fitted | 8 / 2.35 fail | fail | 8 / 3.88 fail | 0 / 0.78 fail |
| risk_gbm+combined_hinge_fixed | 10 / 1.08 fail | fail | 10 / 1.81 fail | 2 / 0.89 fail |
| risk_gbm+combined_rolling | 11 / 1.88 fail | fail | 11 / 3.15 fail | 2 / 2.00 fail |
| risk_gbm+combined_fitted | 10 / 1.08 fail | fail | 10 / 1.81 fail | 2 / 0.89 fail |
| risk_gbm | 13 / 1.35 pass | pass (h = 1) | 13 / 2.00 pass | 3 / 1.56 fail |
| risk_logistic | 14 / 1.85 pass | pass (h = 1) | 14 / 2.42 fail | 4 / 2.89 fail |
| risk_gbm_base | 14 / 1.50 pass | pass (h = 1) | 14 / 2.04 fail | 4 / 2.00 fail |
| risk_logistic_base | 13 / 1.77 pass | pass (h = 1) | 13 / 2.04 fail | 3 / 2.33 fail |
| risk_quantile_skewt_base | 14 / 1.88 pass | pass (h = 1) | 14 / 2.54 fail | 4 / 3.22 fail |
| ngboost_laplace | 15 / 2.54 fail | fail | 15 / 4.38 fail | 4 / 0.33 fail |
| risk_gbm+settle+h41 | 14 / 1.35 pass | pass (h = 1) | 14 / 2.00 pass | 4 / 1.78 fail |
| risk_gbm+every_day+gate+settle+h41 | 15 / 2.35 fail | fail | 15 / 4.31 fail | 4 / 3.11 fail |
| calendar_climatology | 10 / 5.00 fail | fail | 10 / 5.38 fail | 0 / 3.78 fail |
| persistence_logistic | 7 / 3.42 fail | fail | 7 / 5.73 fail | 0 / 2.22 fail |

## Tier 1 under weighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 11 / 1.00 fail | fail | 11 / 1.69 fail | 0 / 0.83 fail |
| projected_reserves | 11 / 2.14 fail | fail | 11 / 2.85 fail | 0 / 0.89 fail |
| risk_gbm+combined | 10 / 1.14 fail | fail | 10 / 1.72 fail | 2 / 1.67 fail |
| structural_rolling | 14 / 2.35 fail | pass (h = 2) | 14 / 3.12 fail | 5 / 2.94 fail |
| structural_fitted | 11 / 1.00 fail | fail | 11 / 1.69 fail | 0 / 0.83 fail |
| projected_hinge_fixed | 11 / 2.14 fail | fail | 11 / 2.82 fail | 0 / 1.06 fail |
| projected_rolling | 14 / 3.08 fail | fail | 14 / 5.02 fail | 4 / 6.47 fail |
| projected_fitted | 12 / 2.10 fail | fail | 12 / 3.19 fail | 0 / 2.50 fail |
| risk_gbm+combined_hinge_fixed | 10 / 1.24 fail | fail | 10 / 1.92 fail | 2 / 2.31 fail |
| risk_gbm+combined_rolling | 11 / 1.59 fail | fail | 11 / 2.89 fail | 2 / 3.14 fail |
| risk_gbm+combined_fitted | 10 / 1.10 fail | fail | 10 / 1.71 fail | 2 / 1.75 fail |
| risk_gbm | 13 / 0.80 pass | pass (h = 1) | 13 / 1.48 pass | 3 / 1.61 fail |
| risk_logistic | 16 / 1.74 pass | pass (h = 1) | 16 / 2.55 fail | 6 / 4.39 fail |
| risk_gbm_base | 14 / 0.97 pass | pass (h = 1) | 14 / 1.59 pass | 4 / 2.06 fail |
| risk_logistic_base | 15 / 1.65 pass | pass (h = 1) | 15 / 2.18 fail | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass (h = 1) | 15 / 2.14 fail | 5 / 3.81 fail |
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 5 / 0.50 fail |
| risk_gbm+settle+h41 | 14 / 0.88 pass | pass (h = 1) | 14 / 1.44 pass | 4 / 1.72 fail |
| risk_gbm+every_day+gate+settle+h41 | 18 / 1.64 pass | pass (h = 1) | 18 / 3.39 fail | 5 / 2.42 fail |
| calendar_climatology | 12 / 3.75 fail | fail | 12 / 3.90 fail | 0 / 4.56 fail |
| persistence_logistic | 12 / 3.25 fail | fail | 12 / 4.09 fail | 1 / 2.86 fail |

## Tier 1 under weighted/before_only

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 10 / 1.29 fail | fail | 10 / 2.09 fail | 0 / 0.64 fail |
| projected_reserves | 10 / 2.04 fail | fail | 10 / 3.02 fail | 0 / 0.56 fail |
| risk_gbm+combined | 10 / 0.90 fail | fail | 10 / 1.46 fail | 2 / 0.75 fail |
| structural_rolling | 12 / 2.29 fail | fail | 12 / 3.63 fail | 4 / 2.61 fail |
| structural_fitted | 10 / 1.29 fail | fail | 10 / 2.09 fail | 0 / 0.64 fail |
| projected_hinge_fixed | 10 / 2.07 fail | fail | 10 / 3.15 fail | 0 / 0.56 fail |
| projected_rolling | 11 / 3.04 fail | fail | 11 / 5.08 fail | 4 / 5.83 fail |
| projected_fitted | 10 / 1.96 fail | fail | 10 / 3.22 fail | 0 / 1.56 fail |
| risk_gbm+combined_hinge_fixed | 10 / 1.12 fail | fail | 10 / 1.64 fail | 2 / 1.53 fail |
| risk_gbm+combined_rolling | 11 / 1.48 fail | fail | 11 / 2.82 fail | 2 / 1.78 fail |
| risk_gbm+combined_fitted | 10 / 1.12 fail | fail | 10 / 1.64 fail | 2 / 1.53 fail |
| risk_gbm | 13 / 0.95 pass | pass (h = 1) | 13 / 1.64 pass | 3 / 1.78 fail |
| risk_logistic | 16 / 1.90 pass | pass (h = 1) | 16 / 2.70 fail | 6 / 4.31 fail |
| risk_gbm_base | 14 / 1.08 pass | pass (h = 1) | 14 / 1.72 pass | 4 / 2.22 fail |
| risk_logistic_base | 14 / 1.78 pass | pass (h = 1) | 14 / 2.26 fail | 4 / 3.58 fail |
| risk_quantile_skewt_base | 15 / 1.81 pass | pass (h = 1) | 15 / 2.22 fail | 5 / 4.14 fail |
| ngboost_laplace | 16 / 2.23 fail | pass (h = 1) | 16 / 3.30 fail | 5 / 0.58 fail |
| risk_gbm+settle+h41 | 14 / 1.02 pass | pass (h = 1) | 14 / 1.63 pass | 4 / 1.89 fail |
| risk_gbm+every_day+gate+settle+h41 | 18 / 2.09 fail | fail | 18 / 4.18 fail | 5 / 2.78 fail |
| calendar_climatology | 12 / 4.55 fail | fail | 12 / 4.70 fail | 0 / 4.44 fail |
| persistence_logistic | 10 / 3.23 fail | fail | 10 / 4.50 fail | 1 / 1.75 fail |

## The judge's tables under the unweighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.7 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_fitted | 8 of 26 | 0.308 [0.148, 0.480] | 0.231 | 3.88 flat / 1.75 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| projected_hinge_fixed | 8 of 26 | 0.308 [0.154, 0.462] | 0.231 | 3.77 flat / 1.63 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| projected_reserves | 8 of 26 | 0.308 [0.156, 0.471] | 0.231 | 3.35 flat / 1.41 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_rolling | 11 of 26 | 0.423 [0.261, 0.593] | 0.269 | 5.23 flat / 2.88 weighted (tier 1 on the flat count) | 3.2 / 4.4 | 0 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+combined | 10 of 26 | 0.385 [0.212, 0.571] | 0.192 | 1.85 flat / 1.07 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_fitted | 10 of 26 | 0.385 [0.200, 0.583] | 0.192 | 1.81 flat / 1.06 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_hinge_fixed | 10 of 26 | 0.385 [0.208, 0.571] | 0.192 | 1.81 flat / 1.06 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_rolling | 11 of 26 | 0.423 [0.250, 0.616] | 0.231 | 3.15 flat / 1.58 weighted (tier 1 on the flat count) | 1.7 / 2.4 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 15 of 26 | 0.577 [0.417, 0.741] | 0.242 | 4.31 flat / 2.04 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.00 flat / 1.29 weighted (tier 1 on the flat count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 2.04 flat / 1.41 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.231 | 2.54 flat / 1.80 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| structural_fitted | 10 of 26 | 0.385 [0.217, 0.560] | 0.192 | 2.42 flat / 1.01 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| structural_liquidity | 10 of 26 | 0.385 [0.217, 0.552] | 0.192 | 2.42 flat / 1.01 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| structural_rolling | 11 of 26 | 0.423 [0.259, 0.600] | 0.231 | 4.19 flat / 1.69 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |

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

projected_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.125, 0.432] | 2.308 [1.318, 3.715] | 0.788 [0.446, 1.270] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.087, 0.400] | 2.346 [1.294, 3.926] | 1.058 [0.542, 1.847] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.038 [1.150, 3.305] | 0.971 [0.494, 1.674] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.061, 0.348] | 1.808 [0.933, 3.067] | 0.865 [0.402, 1.567] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.030, 0.226] | 0.885 [0.333, 1.714] | 0.385 [0.144, 0.764] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.263, 0.692] | 5.235 [3.381, 8.252] | 2.074 [1.230, 3.438] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.333 [0.000, 4.168] | 1.139 [0.000, 3.750] |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

projected_hinge_fixed:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.381] | 2.346 [1.333, 3.625] | 0.817 [0.452, 1.283] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 2.231 [1.189, 3.524] | 1.000 [0.500, 1.660] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.364] | 2.077 [1.120, 3.273] | 0.885 [0.467, 1.429] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.095, 0.375] | 1.615 [0.739, 2.690] | 0.683 [0.293, 1.175] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 0.962 [0.379, 1.810] | 0.385 [0.153, 0.721] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.269, 0.667] | 5.294 [3.296, 8.003] | 2.074 [1.183, 3.327] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.889 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

projected_reserves:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.091, 0.370] | 2.346 [1.323, 3.737] | 0.817 [0.450, 1.313] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.885 [0.900, 3.300] | 0.750 [0.360, 1.324] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.346 [0.538, 2.579] | 0.567 [0.237, 1.071] |
| lead 4 alone (fail) | 26 | 6 | 0.231 [0.087, 0.379] | 1.731 [0.818, 3.000] | 0.721 [0.329, 1.241] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.115 [0.458, 2.091] | 0.490 [0.200, 0.957] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.263, 0.692] | 4.647 [2.833, 7.385] | 1.735 [1.000, 2.808] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 0.889 [0.000, 2.750] | 0.806 [0.000, 2.562] |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

projected_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 3.115 [1.928, 4.810] | 1.452 [0.885, 2.365] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.172, 0.455] | 3.077 [1.852, 4.818] | 1.471 [0.879, 2.417] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.593] | 3.231 [1.937, 5.155] | 1.587 [0.922, 2.664] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 3.038 [1.740, 4.889] | 1.317 [0.750, 2.167] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.444] | 2.308 [1.208, 3.875] | 1.048 [0.573, 1.762] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.231, 0.619] | 3.235 [1.789, 5.556] | 1.265 [0.676, 2.251] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 9.000 (no interval) | 5.944 (no interval) |

Recall with equal weight per regime: 0.303 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

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

risk_gbm+combined:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.391] | 0.808 [0.417, 1.348] | 0.462 [0.214, 0.810] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 0.808 [0.316, 1.524] | 0.490 [0.170, 0.972] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.440] | 1.077 [0.483, 1.909] | 0.702 [0.261, 1.366] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.477] | 1.115 [0.478, 2.062] | 0.712 [0.250, 1.396] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.000 [0.379, 1.895] | 0.644 [0.205, 1.302] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.059 [0.827, 4.000] | 1.074 [0.317, 2.292] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.094, 0.391] | 0.808 [0.409, 1.333] | 0.462 [0.211, 0.804] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.389] | 0.808 [0.320, 1.486] | 0.490 [0.173, 0.929] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.115, 0.448] | 1.077 [0.500, 1.870] | 0.702 [0.262, 1.324] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 1.077 [0.455, 2.000] | 0.702 [0.259, 1.367] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 0.846 [0.379, 1.520] | 0.529 [0.212, 1.017] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.722] | 2.000 [0.789, 3.790] | 1.059 [0.321, 2.208] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_hinge_fixed:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.095, 0.391] | 0.808 [0.429, 1.348] | 0.462 [0.226, 0.813] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.094, 0.391] | 0.808 [0.333, 1.455] | 0.490 [0.177, 0.947] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.115, 0.440] | 1.077 [0.517, 1.904] | 0.702 [0.278, 1.352] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 1.077 [0.471, 2.000] | 0.702 [0.260, 1.392] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 0.846 [0.391, 1.517] | 0.529 [0.210, 0.992] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.709] | 2.000 [0.824, 3.833] | 1.059 [0.333, 2.195] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 7 | 0.269 [0.129, 0.429] | 1.462 [0.680, 2.550] | 0.654 [0.336, 1.125] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 1.500 [0.840, 2.481] | 0.779 [0.423, 1.383] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.885 [1.067, 3.048] | 0.952 [0.543, 1.563] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.654 [0.857, 2.733] | 0.721 [0.387, 1.195] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 1.846 [0.944, 3.059] | 0.808 [0.423, 1.364] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.778] | 3.000 [1.389, 5.455] | 1.103 [0.527, 1.983] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.444 (no interval) | 2.472 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

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

structural_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.560] | 1.192 [0.618, 2.046] | 0.404 [0.205, 0.700] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.321] | 1.423 [0.708, 2.385] | 0.567 [0.225, 1.050] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 1.346 [0.571, 2.375] | 0.538 [0.194, 1.000] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.045, 0.276] | 1.077 [0.433, 1.955] | 0.490 [0.147, 0.975] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.045, 0.269] | 0.462 [0.138, 0.929] | 0.192 [0.054, 0.382] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.810] | 3.529 [1.954, 5.877] | 1.500 [0.710, 2.697] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.333 (no interval) | 0.083 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

structural_liquidity:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.217, 0.552] | 1.192 [0.606, 2.105] | 0.404 [0.196, 0.711] |
| lead 2 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 1.423 [0.680, 2.409] | 0.567 [0.220, 1.068] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.100, 0.379] | 1.346 [0.571, 2.438] | 0.538 [0.200, 1.029] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.042, 0.276] | 1.077 [0.433, 1.948] | 0.490 [0.150, 0.987] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 0.462 [0.138, 0.947] | 0.192 [0.054, 0.388] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 3.529 [1.933, 5.941] | 1.500 [0.683, 2.695] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 0.333 [0.000, 0.833] | 0.083 [0.000, 0.208] |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

structural_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.188, 0.519] | 1.654 [1.000, 2.548] | 0.471 [0.269, 0.750] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.188, 0.519] | 2.538 [1.571, 3.846] | 0.923 [0.518, 1.490] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.188, 0.515] | 2.423 [1.500, 3.667] | 0.923 [0.500, 1.475] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 2.615 [1.611, 4.000] | 0.981 [0.580, 1.546] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.118, 0.435] | 1.923 [1.061, 3.150] | 0.798 [0.396, 1.364] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.214, 0.625] | 3.471 [2.000, 5.813] | 1.309 [0.675, 2.275] |
| outside 2018-2019 | 9 | 4 | 0.444 [0.125, 0.750] | 5.556 [2.800, 10.333] | 2.417 [1.033, 5.002] |

Recall with equal weight per regime: 0.303 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| projected_fitted | 0.65 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.47 (101) | 0.44 (9) | 0.62 (13) |
| projected_hinge_fixed | 0.62 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.44 (101) | 0.44 (9) | 0.62 (13) |
| projected_reserves | 0.62 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.44 (101) | 0.44 (9) | 0.62 (13) |
| projected_rolling | 0.48 (102) | 0.00 (4) | – | 0.20 (5) | 0.86 (29) | 0.59 (17) | 0.50 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+combined | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.24 (101) | 0.33 (9) | 0.46 (13) |
| risk_gbm+combined_fitted | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.24 (101) | 0.33 (9) | 0.46 (13) |
| risk_gbm+combined_hinge_fixed | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.24 (101) | 0.33 (9) | 0.46 (13) |
| risk_gbm+combined_rolling | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.41 (29) | 0.53 (17) | 0.41 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| structural_fitted | 0.49 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.53 (17) | 0.33 (101) | 0.44 (9) | 0.62 (13) |
| structural_liquidity | 0.49 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.53 (17) | 0.33 (101) | 0.44 (9) | 0.62 (13) |
| structural_rolling | 0.46 (102) | 0.25 (4) | – | 0.00 (5) | 0.76 (29) | 0.59 (17) | 0.45 (101) | 0.56 (9) | 0.77 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| projected_fitted | +0.0329 [-0.0082, +0.0773] | +0.0179 [+0.0093, +0.0249] | +0.0133 [+0.0117, +0.0151] | +0.0017 [-0.0029, +0.0053] | +0.0111 [+0.0034, +0.0198] | +0.0333 [+0.0132, +0.0555] | +0.0117 [+0.0035, +0.0207] | +0.0664 [+0.0263, +0.1018] | +0.0472 [+0.0137, +0.0831] |
| projected_hinge_fixed | +0.0352 [-0.0047, +0.0752] | +0.0207 [+0.0055, +0.0346] | +0.0137 [+0.0120, +0.0155] | +0.0021 [-0.0020, +0.0053] | +0.0065 [+0.0005, +0.0139] | +0.0314 [+0.0120, +0.0530] | +0.0118 [+0.0038, +0.0203] | +0.0731 [+0.0281, +0.1163] | +0.0554 [+0.0192, +0.0920] |
| projected_reserves | +0.0352 [-0.0021, +0.0787] | +0.0217 [+0.0065, +0.0360] | +0.0138 [+0.0121, +0.0156] | +0.0021 [-0.0020, +0.0053] | +0.0134 [+0.0049, +0.0234] | +0.0330 [+0.0127, +0.0563] | +0.0124 [+0.0047, +0.0213] | +0.0859 [+0.0399, +0.1290] | +0.0591 [+0.0226, +0.0966] |
| projected_rolling | +0.0266 [+0.0051, +0.0513] | +0.0304 [+0.0221, +0.0385] | +0.0103 [+0.0070, +0.0132] | +0.0024 [-0.0015, +0.0052] | +0.0275 [-0.0133, +0.0788] | +0.0397 [+0.0114, +0.0727] | +0.0122 [+0.0057, +0.0196] | +0.1099 [+0.0564, +0.1629] | +0.0435 [+0.0200, +0.0690] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+combined | -0.0020 [-0.0236, +0.0186] | +0.0422 [+0.0346, +0.0500] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0054] | +0.0049 [-0.0043, +0.0151] | +0.0298 [+0.0161, +0.0442] | +0.0071 [+0.0020, +0.0116] | +0.1049 [+0.0102, +0.1953] | +0.0292 [-0.0010, +0.0578] |
| risk_gbm+combined_fitted | -0.0020 [-0.0236, +0.0192] | +0.0422 [+0.0348, +0.0501] | +0.0138 [+0.0121, +0.0156] | +0.0010 [-0.0046, +0.0053] | +0.0047 [-0.0051, +0.0139] | +0.0298 [+0.0171, +0.0432] | +0.0070 [+0.0021, +0.0115] | +0.1049 [+0.0185, +0.1959] | +0.0292 [-0.0008, +0.0572] |
| risk_gbm+combined_hinge_fixed | -0.0020 [-0.0239, +0.0187] | +0.0422 [+0.0350, +0.0504] | +0.0138 [+0.0121, +0.0156] | +0.0010 [-0.0043, +0.0052] | +0.0040 [-0.0052, +0.0135] | +0.0297 [+0.0163, +0.0442] | +0.0069 [+0.0019, +0.0114] | +0.1049 [+0.0146, +0.1996] | +0.0292 [-0.0028, +0.0577] |
| risk_gbm+combined_rolling | +0.0028 [-0.0195, +0.0288] | +0.0422 [+0.0348, +0.0503] | +0.0137 [+0.0119, +0.0157] | +0.0010 [-0.0048, +0.0053] | +0.0113 [+0.0022, +0.0224] | +0.0295 [+0.0167, +0.0442] | +0.0092 [+0.0037, +0.0148] | +0.1049 [+0.0150, +0.1971] | +0.0292 [-0.0031, +0.0578] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| structural_fitted | +0.0321 [-0.0052, +0.0719] | +0.0268 [+0.0154, +0.0377] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0043, +0.0048] | +0.0231 [+0.0031, +0.0482] | +0.0390 [+0.0091, +0.0689] | +0.0123 [+0.0044, +0.0204] | +0.1343 [+0.0722, +0.1947] | +0.0557 [+0.0092, +0.1014] |
| structural_liquidity | +0.0321 [-0.0050, +0.0708] | +0.0268 [+0.0160, +0.0373] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0041, +0.0049] | +0.0231 [+0.0027, +0.0495] | +0.0390 [+0.0091, +0.0702] | +0.0123 [+0.0044, +0.0208] | +0.1343 [+0.0762, +0.1967] | +0.0557 [+0.0113, +0.0996] |
| structural_rolling | +0.0385 [+0.0157, +0.0652] | +0.0325 [+0.0219, +0.0421] | +0.0134 [+0.0116, +0.0152] | +0.0007 [-0.0046, +0.0048] | +0.0467 [+0.0057, +0.0970] | +0.0417 [+0.0140, +0.0742] | +0.0174 [+0.0103, +0.0260] | +0.1586 [+0.0838, +0.2360] | +0.0591 [+0.0322, +0.0852] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.9 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_fitted | 12 of 26 | 0.462 [0.263, 0.667] | 0.288 | 6.12 flat / 3.19 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| projected_hinge_fixed | 11 of 26 | 0.423 [0.241, 0.619] | 0.274 | 5.85 flat / 2.82 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| projected_reserves | 11 of 26 | 0.423 [0.238, 0.611] | 0.274 | 5.85 flat / 2.85 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_rolling | 14 of 26 | 0.538 [0.357, 0.727] | 0.423 | 8.35 flat / 5.02 weighted (tier 1 on the weighted count) | 5.8 / 8.8 | 0 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+combined | 10 of 26 | 0.385 [0.212, 0.571] | 0.231 | 2.62 flat / 1.72 weighted (tier 1 on the weighted count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_fitted | 10 of 26 | 0.385 [0.200, 0.583] | 0.231 | 2.54 flat / 1.71 weighted (tier 1 on the weighted count) | 0.2 / 0.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_hinge_fixed | 10 of 26 | 0.385 [0.208, 0.571] | 0.231 | 3.12 flat / 1.92 weighted (tier 1 on the weighted count) | 0.2 / 0.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_rolling | 11 of 26 | 0.423 [0.250, 0.616] | 0.269 | 5.04 flat / 2.89 weighted (tier 1 on the weighted count) | 3.9 / 5.4 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.524, 0.857] | 0.375 | 6.96 flat / 3.39 weighted (tier 1 on the weighted count) | 2.7 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.15 flat / 1.44 weighted (tier 1 on the weighted count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted (tier 1 on the weighted count) | 3.2 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.231 | 2.88 flat / 2.18 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 2.88 flat / 2.14 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| structural_fitted | 11 of 26 | 0.423 [0.238, 0.613] | 0.231 | 3.92 flat / 1.69 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| structural_liquidity | 11 of 26 | 0.423 [0.250, 0.613] | 0.231 | 3.92 flat / 1.69 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| structural_rolling | 14 of 26 | 0.538 [0.364, 0.727] | 0.353 | 6.62 flat / 3.12 weighted (tier 1 on the weighted count) | 1.2 / 1.3 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |

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

projected_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.227, 0.625] | 4.654 [3.067, 7.037] | 2.096 [1.324, 3.313] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.174, 0.530] | 3.500 [2.099, 5.526] | 1.596 [0.910, 2.667] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.200, 0.583] | 4.077 [2.483, 6.334] | 1.933 [1.083, 3.241] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.114, 0.444] | 3.423 [2.033, 5.471] | 1.865 [0.958, 3.369] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.043, 0.273] | 1.231 [0.522, 2.278] | 0.673 [0.241, 1.389] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.467, 0.938] | 7.529 [5.087, 11.572] | 3.206 [1.975, 5.334] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 3.444 [0.933, 9.500] | 3.167 [0.781, 9.000] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

projected_hinge_fixed:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.241, 0.619] | 4.769 [3.096, 7.002] | 2.144 [1.308, 3.312] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.962 [2.368, 6.137] | 1.942 [1.080, 3.126] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.572] | 4.115 [2.438, 6.292] | 1.865 [1.039, 2.971] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.524] | 3.654 [2.129, 5.680] | 1.731 [0.940, 2.815] |
| lead 5 alone (fail) | 26 | 5 | 0.192 [0.077, 0.318] | 1.154 [0.514, 2.105] | 0.548 [0.210, 1.056] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.889] | 7.765 [5.166, 11.468] | 3.279 [1.987, 5.250] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 2.222 (no interval) | 1.944 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

projected_reserves:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.769 [3.000, 7.154] | 2.144 [1.273, 3.355] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.474] | 3.154 [1.750, 5.161] | 1.654 [0.839, 2.869] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 3.692 [2.121, 5.893] | 1.740 [0.926, 2.940] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 3.846 [2.238, 6.039] | 1.788 [0.982, 2.966] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.103, 0.375] | 2.308 [1.166, 3.905] | 1.125 [0.529, 1.977] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.409, 0.882] | 7.824 [5.117, 11.923] | 3.353 [2.024, 5.411] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 2.111 [0.500, 5.669] | 1.889 [0.361, 5.335] |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

projected_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.241, 0.615] | 6.077 [4.036, 9.002] | 3.077 [1.994, 4.807] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.808 [3.067, 7.318] | 2.625 [1.647, 4.207] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.294, 0.636] | 4.962 [3.178, 7.600] | 2.904 [1.861, 4.645] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.176, 0.519] | 4.038 [2.480, 6.333] | 2.250 [1.414, 3.637] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.568] | 4.231 [2.606, 6.593] | 2.288 [1.411, 3.663] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.357, 0.818] | 5.471 [3.055, 9.167] | 2.338 [1.184, 4.268] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 13.778 (no interval) | 10.083 (no interval) |

Recall with equal weight per regime: 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5).

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

risk_gbm+combined:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 0.962 [0.560, 1.524] | 0.500 [0.250, 0.850] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 1.423 [0.769, 2.389] | 0.990 [0.506, 1.732] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.346 [0.708, 2.259] | 0.913 [0.417, 1.654] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 1.692 [0.929, 2.810] | 1.144 [0.567, 2.025] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.462 [0.743, 2.471] | 1.019 [0.484, 1.799] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.294 [1.000, 4.267] | 1.221 [0.426, 2.500] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.222 (no interval) | 2.667 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.154, 0.483] | 0.962 [0.556, 1.500] | 0.500 [0.257, 0.844] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.154, 0.481] | 1.346 [0.703, 2.263] | 0.942 [0.451, 1.652] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.179, 0.542] | 1.346 [0.714, 2.240] | 0.913 [0.408, 1.604] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.174, 0.536] | 1.577 [0.833, 2.633] | 1.096 [0.527, 1.965] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.174, 0.533] | 1.500 [0.865, 2.409] | 1.048 [0.553, 1.797] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.722] | 2.235 [1.000, 4.063] | 1.206 [0.441, 2.417] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.111 (no interval) | 2.667 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_hinge_fixed:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 1.538 [0.875, 2.542] | 0.712 [0.391, 1.167] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.480] | 1.346 [0.714, 2.280] | 0.942 [0.471, 1.647] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.529] | 1.346 [0.714, 2.292] | 0.913 [0.413, 1.650] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.577 [0.840, 2.682] | 1.096 [0.534, 1.959] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.182, 0.519] | 2.000 [1.148, 3.235] | 1.240 [0.707, 2.048] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.709] | 2.235 [1.000, 4.083] | 1.206 [0.420, 2.375] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.778 (no interval) | 3.278 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.182, 0.530] | 2.538 [1.518, 4.048] | 1.125 [0.679, 1.824] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 2.538 [1.485, 4.200] | 1.587 [0.843, 2.842] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 2.385 [1.428, 3.715] | 1.250 [0.743, 2.042] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.210, 0.571] | 2.462 [1.480, 3.890] | 1.250 [0.765, 2.034] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.222, 0.571] | 2.538 [1.464, 4.000] | 1.202 [0.716, 1.917] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.778] | 3.765 [1.926, 6.584] | 1.412 [0.734, 2.450] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 7.444 (no interval) | 5.694 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

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

structural_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.238, 0.613] | 2.346 [1.500, 3.616] | 1.000 [0.592, 1.612] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 2.538 [1.500, 3.945] | 0.952 [0.474, 1.583] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.520] | 2.231 [1.176, 3.636] | 0.904 [0.398, 1.574] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.000 [1.125, 3.207] | 0.788 [0.380, 1.338] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.045, 0.269] | 0.731 [0.304, 1.400] | 0.308 [0.125, 0.560] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.875] | 4.529 [2.708, 7.333] | 1.882 [0.984, 3.278] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 2.778 (no interval) | 1.333 (no interval) |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

structural_liquidity:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.613] | 2.346 [1.500, 3.625] | 1.000 [0.583, 1.618] |
| lead 2 alone (fail) | 26 | 9 | 0.346 [0.190, 0.522] | 2.538 [1.476, 4.000] | 0.952 [0.477, 1.615] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.522] | 2.231 [1.139, 3.693] | 0.904 [0.392, 1.625] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 2.000 [1.091, 3.273] | 0.788 [0.385, 1.364] |
| lead 5 alone (fail) | 26 | 4 | 0.154 [0.043, 0.286] | 0.731 [0.310, 1.375] | 0.308 [0.130, 0.554] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.429, 0.867] | 4.529 [2.631, 7.400] | 1.882 [0.958, 3.266] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 2.778 [1.374, 5.858] | 1.333 [0.545, 3.050] |

Recall with equal weight per regime: 0.162 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

structural_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.652] | 3.654 [2.303, 5.619] | 1.433 [0.803, 2.438] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.364, 0.727] | 4.692 [3.158, 6.787] | 1.962 [1.237, 3.011] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.286, 0.643] | 4.923 [3.361, 7.258] | 2.346 [1.456, 3.619] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.259, 0.600] | 3.154 [2.030, 4.762] | 1.240 [0.743, 1.945] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.219, 0.560] | 2.846 [1.750, 4.334] | 1.144 [0.661, 1.842] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.300, 0.769] | 5.706 [3.416, 9.250] | 2.456 [1.330, 4.188] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.875] | 8.333 [5.100, 14.842] | 4.389 [2.423, 8.702] |

Recall with equal weight per regime: 0.382 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| projected_fitted | 0.80 (102) | 0.00 (4) | – | 0.00 (5) | 0.10 (29) | 0.59 (17) | 0.62 (101) | 0.44 (9) | 0.62 (13) |
| projected_hinge_fixed | 0.80 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| projected_reserves | 0.80 (102) | 0.00 (4) | – | 0.00 (5) | 0.10 (29) | 0.59 (17) | 0.62 (101) | 0.44 (9) | 0.62 (13) |
| projected_rolling | 0.64 (102) | 0.00 (4) | – | 0.20 (5) | 0.93 (29) | 0.76 (17) | 0.63 (101) | 0.67 (9) | 0.77 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+combined | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.27 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_fitted | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.27 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_hinge_fixed | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.41 (29) | 0.59 (17) | 0.31 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_rolling | 0.48 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.53 (17) | 0.44 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |
| structural_fitted | 0.54 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.76 (17) | 0.40 (101) | 0.44 (9) | 0.62 (13) |
| structural_liquidity | 0.54 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.76 (17) | 0.40 (101) | 0.44 (9) | 0.62 (13) |
| structural_rolling | 0.64 (102) | 0.25 (4) | – | 0.20 (5) | 0.83 (29) | 0.71 (17) | 0.62 (101) | 0.67 (9) | 0.77 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| projected_fitted | +0.0329 [-0.0082, +0.0773] | +0.0179 [+0.0093, +0.0249] | +0.0133 [+0.0117, +0.0151] | +0.0017 [-0.0029, +0.0053] | +0.0111 [+0.0034, +0.0198] | +0.0333 [+0.0132, +0.0555] | +0.0117 [+0.0035, +0.0207] | +0.0664 [+0.0263, +0.1018] | +0.0472 [+0.0137, +0.0831] |
| projected_hinge_fixed | +0.0352 [-0.0047, +0.0752] | +0.0207 [+0.0055, +0.0346] | +0.0137 [+0.0120, +0.0155] | +0.0021 [-0.0020, +0.0053] | +0.0065 [+0.0005, +0.0139] | +0.0314 [+0.0120, +0.0530] | +0.0118 [+0.0038, +0.0203] | +0.0731 [+0.0281, +0.1163] | +0.0554 [+0.0192, +0.0920] |
| projected_reserves | +0.0352 [-0.0021, +0.0787] | +0.0217 [+0.0065, +0.0360] | +0.0138 [+0.0121, +0.0156] | +0.0021 [-0.0020, +0.0053] | +0.0134 [+0.0049, +0.0234] | +0.0330 [+0.0127, +0.0563] | +0.0124 [+0.0047, +0.0213] | +0.0859 [+0.0399, +0.1290] | +0.0591 [+0.0226, +0.0966] |
| projected_rolling | +0.0266 [+0.0051, +0.0513] | +0.0304 [+0.0221, +0.0385] | +0.0103 [+0.0070, +0.0132] | +0.0024 [-0.0015, +0.0052] | +0.0275 [-0.0133, +0.0788] | +0.0397 [+0.0114, +0.0727] | +0.0122 [+0.0057, +0.0196] | +0.1099 [+0.0564, +0.1629] | +0.0435 [+0.0200, +0.0690] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+combined | -0.0020 [-0.0236, +0.0186] | +0.0422 [+0.0346, +0.0500] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0054] | +0.0049 [-0.0043, +0.0151] | +0.0298 [+0.0161, +0.0442] | +0.0071 [+0.0020, +0.0116] | +0.1049 [+0.0102, +0.1953] | +0.0292 [-0.0010, +0.0578] |
| risk_gbm+combined_fitted | -0.0020 [-0.0236, +0.0192] | +0.0422 [+0.0348, +0.0501] | +0.0138 [+0.0121, +0.0156] | +0.0010 [-0.0046, +0.0053] | +0.0047 [-0.0051, +0.0139] | +0.0298 [+0.0171, +0.0432] | +0.0070 [+0.0021, +0.0115] | +0.1049 [+0.0185, +0.1959] | +0.0292 [-0.0008, +0.0572] |
| risk_gbm+combined_hinge_fixed | -0.0020 [-0.0239, +0.0187] | +0.0422 [+0.0350, +0.0504] | +0.0138 [+0.0121, +0.0156] | +0.0010 [-0.0043, +0.0052] | +0.0040 [-0.0052, +0.0135] | +0.0297 [+0.0163, +0.0442] | +0.0069 [+0.0019, +0.0114] | +0.1049 [+0.0146, +0.1996] | +0.0292 [-0.0028, +0.0577] |
| risk_gbm+combined_rolling | +0.0028 [-0.0195, +0.0288] | +0.0422 [+0.0348, +0.0503] | +0.0137 [+0.0119, +0.0157] | +0.0010 [-0.0048, +0.0053] | +0.0113 [+0.0022, +0.0224] | +0.0295 [+0.0167, +0.0442] | +0.0092 [+0.0037, +0.0148] | +0.1049 [+0.0150, +0.1971] | +0.0292 [-0.0031, +0.0578] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| structural_fitted | +0.0321 [-0.0052, +0.0719] | +0.0268 [+0.0154, +0.0377] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0043, +0.0048] | +0.0231 [+0.0031, +0.0482] | +0.0390 [+0.0091, +0.0689] | +0.0123 [+0.0044, +0.0204] | +0.1343 [+0.0722, +0.1947] | +0.0557 [+0.0092, +0.1014] |
| structural_liquidity | +0.0321 [-0.0050, +0.0708] | +0.0268 [+0.0160, +0.0373] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0041, +0.0049] | +0.0231 [+0.0027, +0.0495] | +0.0390 [+0.0091, +0.0702] | +0.0123 [+0.0044, +0.0208] | +0.1343 [+0.0762, +0.1967] | +0.0557 [+0.0113, +0.0996] |
| structural_rolling | +0.0385 [+0.0157, +0.0652] | +0.0325 [+0.0219, +0.0421] | +0.0134 [+0.0116, +0.0152] | +0.0007 [-0.0046, +0.0048] | +0.0467 [+0.0057, +0.0970] | +0.0417 [+0.0140, +0.0742] | +0.0174 [+0.0103, +0.0260] | +0.1586 [+0.0838, +0.2360] | +0.0591 [+0.0322, +0.0852] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| structural_liquidity | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| projected_reserves | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm+combined | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| structural_rolling | 0 of 4 | 9 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| structural_fitted | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| projected_hinge_fixed | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| projected_rolling | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| projected_fitted | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm+combined_hinge_fixed | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_rolling | 0 of 4 | 9 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_fitted | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_gbm+settle+h41 | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_gbm+every_day+gate+settle+h41 | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |

## Brier score and log loss at +5 bp, pooled by horizon

| row | h = 1 Brier / log loss | h = 2 Brier / log loss | h = 3 Brier / log loss | h = 4 Brier / log loss | h = 5 Brier / log loss |
|---|---|---|---|---|---|
| structural_liquidity | 0.0529 / 0.2195 | 0.0645 / 0.2592 | 0.0691 / 0.2952 | 0.0703 / 0.2868 | 0.0730 / 0.2965 |
| projected_reserves | 0.0539 / 0.1793 | 0.0588 / 0.1934 | 0.0617 / 0.2056 | 0.0613 / 0.2036 | 0.0639 / 0.2161 |
| risk_gbm+combined | 0.0599 / 0.5426 | 0.0641 / 0.5958 | 0.0656 / 0.5902 | 0.0683 / 0.6380 | 0.0672 / 0.6318 |
| structural_rolling | 0.0477 / 0.1809 | 0.0567 / 0.2056 | 0.0593 / 0.2270 | 0.0589 / 0.2132 | 0.0601 / 0.2243 |
| structural_fitted | 0.0529 / 0.2195 | 0.0645 / 0.2592 | 0.0691 / 0.2952 | 0.0703 / 0.2868 | 0.0730 / 0.2965 |
| projected_hinge_fixed | 0.0550 / 0.1917 | 0.0598 / 0.2091 | 0.0625 / 0.2248 | 0.0630 / 0.2228 | 0.0703 / 0.2552 |
| projected_rolling | 0.0539 / 0.1958 | 0.0566 / 0.2106 | 0.0606 / 0.2307 | 0.0589 / 0.2158 | 0.0628 / 0.2340 |
| projected_fitted | 0.0554 / 0.1955 | 0.0596 / 0.2120 | 0.0638 / 0.2313 | 0.0634 / 0.2256 | 0.0722 / 0.2603 |
| risk_gbm+combined_hinge_fixed | 0.0600 / 0.5643 | 0.0643 / 0.6234 | 0.0657 / 0.6177 | 0.0684 / 0.6601 | 0.0668 / 0.6618 |
| risk_gbm+combined_rolling | 0.0581 / 0.4897 | 0.0598 / 0.5312 | 0.0590 / 0.5017 | 0.0596 / 0.5066 | 0.0590 / 0.4915 |
| risk_gbm+combined_fitted | 0.0599 / 0.5436 | 0.0643 / 0.6023 | 0.0657 / 0.5965 | 0.0683 / 0.6343 | 0.0668 / 0.6373 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |
| risk_gbm+settle+h41 | 0.0579 / 0.6610 | 0.0593 / 0.6688 | 0.0612 / 0.6687 | 0.0589 / 0.6720 | 0.0593 / 0.6740 |
| risk_gbm+every_day+gate+settle+h41 | 0.0498 / 0.3819 | 0.0544 / 0.3842 | 0.0570 / 0.4211 | 0.0532 / 0.3661 | 0.0539 / 0.3748 |
| calendar_climatology | 0.0714 / 0.2963 | 0.0711 / 0.2954 | 0.0707 / 0.2943 | 0.0708 / 0.2952 | 0.0709 / 0.2958 |
| persistence_logistic | 0.0563 / 0.2014 | 0.0611 / 0.2184 | 0.0644 / 0.2424 | 0.0624 / 0.2254 | 0.0634 / 0.2394 |

## structural_liquidity: onsets only this row warns

structural_liquidity warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by structural_liquidity and by none of the five passers:

* 2019-08-13 (flagged at h = 1, 2, 3)

Warned by a passer and not by structural_liquidity: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### structural_liquidity: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 0 | 0 of 1873 | 1127 |
| 2 | 90 | 1 | 0 | 6 | 1 | 0 of 1872 | 1249 |
| 3 | 90 | 1 | 0 | 6 | 0 | 0 of 1871 | 1235 |
| 4 | 90 | 2 | 0 | 6 | 0 | 0 of 1870 | 1233 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1252 |

## projected_reserves: onsets only this row warns

projected_reserves warns 11 of 26 onsets; at least one of the five passers warns 16. 2 are warned by projected_reserves and by none of the five passers:

* 2019-06-25 (flagged at h = 1, 2, 3, 4)
* 2019-08-13 (flagged at h = 1, 3, 4)

Warned by a passer and not by projected_reserves: 2019-01-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### projected_reserves: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 4 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 2 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 3 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 3 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 2 | 0 of 1869 | 1869 |

## risk_gbm+combined: onsets only this row warns

risk_gbm+combined warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined and by none of the five passers:


Warned by a passer and not by risk_gbm+combined: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1326 of 1873 | 529 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1360 of 1872 | 493 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1381 of 1871 | 471 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1388 of 1870 | 458 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1368 of 1869 | 479 |

## structural_rolling: onsets only this row warns

structural_rolling warns 14 of 26 onsets; at least one of the five passers warns 16. 2 are warned by structural_rolling and by none of the five passers:

* 2019-05-28 (flagged at h = 2)
* 2019-08-13 (flagged at h = 1, 2, 3)

Warned by a passer and not by structural_rolling: 2019-01-15, 2019-01-31, 2019-03-15, 2024-09-30

### structural_rolling: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 3 | 0 of 1873 | 1173 |
| 2 | 90 | 1 | 0 | 6 | 4 | 0 of 1872 | 1284 |
| 3 | 90 | 1 | 0 | 6 | 2 | 0 of 1871 | 1274 |
| 4 | 90 | 2 | 0 | 6 | 1 | 0 of 1870 | 1273 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1289 |

## structural_fitted: onsets only this row warns

structural_fitted warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by structural_fitted and by none of the five passers:

* 2019-08-13 (flagged at h = 1, 2, 3)

Warned by a passer and not by structural_fitted: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### structural_fitted: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 0 | 0 of 1873 | 1126 |
| 2 | 90 | 1 | 0 | 6 | 1 | 0 of 1872 | 1249 |
| 3 | 90 | 1 | 0 | 6 | 0 | 0 of 1871 | 1236 |
| 4 | 90 | 2 | 0 | 6 | 0 | 0 of 1870 | 1233 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1251 |

## projected_hinge_fixed: onsets only this row warns

projected_hinge_fixed warns 11 of 26 onsets; at least one of the five passers warns 16. 2 are warned by projected_hinge_fixed and by none of the five passers:

* 2019-06-25 (flagged at h = 1, 2, 3, 4)
* 2019-08-13 (flagged at h = 1, 2, 3, 4)

Warned by a passer and not by projected_hinge_fixed: 2019-01-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### projected_hinge_fixed: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 4 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 4 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 4 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 2 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1869 |

## projected_rolling: onsets only this row warns

projected_rolling warns 14 of 26 onsets; at least one of the five passers warns 16. 2 are warned by projected_rolling and by none of the five passers:

* 2019-06-25 (flagged at h = 3)
* 2019-08-13 (flagged at h = 1)

Warned by a passer and not by projected_rolling: 2019-02-28, 2019-03-15, 2024-09-30, 2025-12-26

### projected_rolling: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 5 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 6 | 3 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 6 | 4 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 4 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 4 | 0 of 1869 | 1869 |

## projected_fitted: onsets only this row warns

projected_fitted warns 12 of 26 onsets; at least one of the five passers warns 16. 3 are warned by projected_fitted and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3)
* 2019-06-25 (flagged at h = 1, 2, 3, 4)
* 2019-08-13 (flagged at h = 1, 2, 3, 4)

Warned by a passer and not by projected_fitted: 2019-01-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### projected_fitted: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 4 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 4 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 3 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 2 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1869 |

## risk_gbm+combined_hinge_fixed: onsets only this row warns

risk_gbm+combined_hinge_fixed warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined_hinge_fixed and by none of the five passers:


Warned by a passer and not by risk_gbm+combined_hinge_fixed: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_hinge_fixed: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1412 of 1873 | 443 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1418 of 1872 | 435 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1423 of 1871 | 429 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1430 of 1870 | 416 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1431 of 1869 | 416 |

## risk_gbm+combined_rolling: onsets only this row warns

risk_gbm+combined_rolling warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by risk_gbm+combined_rolling and by none of the five passers:

* 2019-08-13 (flagged at h = 1, 3, 4, 5)

Warned by a passer and not by risk_gbm+combined_rolling: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_rolling: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1344 of 1873 | 511 |
| 2 | 90 | 1 | 1 | 7 | 1 | 1346 of 1872 | 507 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1360 of 1871 | 492 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1371 of 1870 | 475 |
| 5 | 89 | 1 | 1 | 7 | 1 | 1372 of 1869 | 475 |

## risk_gbm+combined_fitted: onsets only this row warns

risk_gbm+combined_fitted warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined_fitted and by none of the five passers:


Warned by a passer and not by risk_gbm+combined_fitted: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_fitted: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1378 of 1873 | 477 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1387 of 1872 | 466 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1408 of 1871 | 444 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1408 of 1870 | 438 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1396 of 1869 | 451 |

## structural_liquidity against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.004, 0.014] |
| 2 | 0.004 [-0.007, 0.016] |
| 3 | -0.002 [-0.016, 0.011] |
| 4 | -0.003 [-0.016, 0.009] |
| 5 | -0.003 [-0.018, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.030 [-0.011, 0.073] | 0.003 [-0.063, 0.073] | -0.021 [-0.091, 0.044] |
| 2020 | 251 | -0.013 [-0.019, -0.008] | -0.015 [-0.023, -0.007] | -0.010 [-0.017, -0.003] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.007, -0.000] | -0.003 [-0.007, -0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | 0.008 [-0.014, 0.030] | 0.001 [-0.017, 0.017] | 0.019 [0.001, 0.039] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.035, 0.003] | -0.028 [-0.061, 0.001] | -0.009 [-0.029, 0.010] |
| ordinary | 1603 | 0.007 [-0.002, 0.018] | -0.000 [-0.015, 0.015] | -0.005 [-0.021, 0.009] |
| quarter_end | 31 | 0.019 [-0.039, 0.078] | 0.009 [-0.074, 0.094] | 0.019 [-0.040, 0.080] |
| tax_date | 89 | -0.013 [-0.065, 0.040] | -0.004 [-0.040, 0.033] | 0.025 [-0.015, 0.073] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, 0.001] | -0.001 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.004 [-0.006, -0.002] | -0.009 [-0.011, -0.007] | -0.006 [-0.007, -0.004] |
| 2 | 41 | 0.081 [–] | 0.051 [–] | 0.084 [–] |
| 3 | 473 | 0.016 [-0.019, 0.053] | -0.005 [-0.058, 0.050] | -0.015 [-0.070, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.226, 0.056] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.222, 0.097] |

## structural_liquidity against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.007 [-0.013, -0.000] |
| 2 | -0.008 [-0.017, 0.001] |
| 3 | -0.010 [-0.022, 0.002] |
| 4 | -0.009 [-0.020, 0.002] |
| 5 | -0.009 [-0.019, 0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.022 [-0.049, 0.007] | -0.035 [-0.093, 0.024] | -0.045 [-0.090, 0.001] |
| 2020 | 251 | -0.006 [-0.012, -0.001] | -0.016 [-0.022, -0.012] | -0.009 [-0.013, -0.005] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.006 [-0.023, 0.014] | 0.005 [-0.005, 0.018] | 0.010 [-0.005, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.009 [-0.033, 0.013] | -0.013 [-0.048, 0.020] | -0.004 [-0.028, 0.022] |
| ordinary | 1603 | -0.006 [-0.012, -0.001] | -0.011 [-0.023, 0.000] | -0.012 [-0.021, -0.003] |
| quarter_end | 31 | 0.003 [-0.065, 0.073] | -0.000 [-0.098, 0.100] | -0.008 [-0.060, 0.053] |
| tax_date | 89 | -0.011 [-0.053, 0.038] | 0.010 [-0.038, 0.070] | 0.024 [-0.030, 0.087] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.003 [-0.006, -0.001] | -0.009 [-0.011, -0.007] | -0.005 [-0.007, -0.004] |
| 2 | 41 | 0.032 [-0.059, 0.126] | 0.037 [-0.030, 0.085] | 0.070 [–] |
| 3 | 473 | -0.025 [-0.046, -0.001] | -0.031 [-0.078, 0.015] | -0.038 [-0.074, -0.002] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.419, -0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.238, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.545, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.333, 0.002] |

## structural_liquidity against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.019 [0.010, 0.027] |
| 2 | 0.007 [-0.003, 0.017] |
| 3 | 0.002 [-0.010, 0.013] |
| 4 | 0.001 [-0.013, 0.012] |
| 5 | -0.002 [-0.016, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [-0.006, 0.073] | -0.033 [-0.091, 0.023] | -0.058 [-0.116, -0.004] |
| 2020 | 251 | 0.027 [0.016, 0.037] | 0.022 [0.013, 0.031] | 0.026 [0.017, 0.035] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.012 [0.010, 0.013] | 0.013 [0.011, 0.015] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.001 [-0.003, 0.004] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.023 [0.003, 0.049] | 0.003 [-0.004, 0.010] | 0.004 [-0.006, 0.016] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.039 [0.007, 0.070] | -0.001 [-0.034, 0.029] | 0.005 [-0.015, 0.024] |
| ordinary | 1603 | 0.012 [0.005, 0.021] | -0.002 [-0.015, 0.009] | -0.007 [-0.022, 0.005] |
| quarter_end | 31 | 0.134 [0.073, 0.197] | 0.088 [0.025, 0.150] | 0.082 [-0.005, 0.168] |
| tax_date | 89 | 0.056 [0.013, 0.103] | 0.049 [0.002, 0.099] | 0.051 [0.004, 0.095] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.008 [0.007, 0.010] | 0.008 [0.006, 0.009] | 0.008 [0.006, 0.010] |
| 1 | 324 | 0.025 [0.019, 0.031] | 0.020 [0.015, 0.025] | 0.022 [0.017, 0.027] |
| 2 | 41 | 0.073 [–] | 0.019 [-0.018, 0.054] | 0.043 [–] |
| 3 | 473 | 0.031 [0.001, 0.063] | -0.026 [-0.073, 0.018] | -0.046 [-0.095, -0.003] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.158, 0.071] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.167] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.091] |

## structural_liquidity against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.003, 0.010] |
| 2 | -0.003 [-0.013, 0.006] |
| 3 | -0.005 [-0.017, 0.007] |
| 4 | -0.008 [-0.020, 0.003] |
| 5 | -0.010 [-0.022, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.015 [-0.015, 0.048] | -0.033 [-0.092, 0.026] | -0.055 [-0.113, -0.004] |
| 2020 | 251 | 0.003 [-0.001, 0.008] | 0.010 [0.005, 0.014] | 0.009 [0.004, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.002 [0.001, 0.002] | 0.001 [0.001, 0.002] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.002] |
| 2025-26 | 249 | -0.003 [-0.009, 0.003] | -0.003 [-0.013, 0.004] | -0.003 [-0.014, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.018 [-0.010, 0.048] | -0.011 [-0.045, 0.020] | -0.004 [-0.026, 0.017] |
| ordinary | 1603 | -0.000 [-0.006, 0.005] | -0.007 [-0.019, 0.004] | -0.013 [-0.027, -0.002] |
| quarter_end | 31 | 0.074 [0.001, 0.155] | 0.053 [-0.036, 0.141] | 0.056 [0.007, 0.117] |
| tax_date | 89 | 0.020 [-0.024, 0.072] | 0.021 [-0.033, 0.083] | 0.025 [-0.028, 0.086] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.001] | 0.001 [0.001, 0.001] | 0.001 [0.001, 0.001] |
| 1 | 324 | 0.005 [0.003, 0.006] | 0.010 [0.008, 0.012] | 0.008 [0.007, 0.010] |
| 2 | 41 | -0.016 [–] | -0.027 [–] | -0.033 [–] |
| 3 | 473 | 0.011 [-0.013, 0.038] | -0.026 [-0.072, 0.021] | -0.043 [-0.090, -0.003] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.200, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.222, 0.222] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.167 [-0.444, 0.125] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.250, 0.158] |

## structural_liquidity against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.004, 0.015] |
| 2 | -0.005 [-0.016, 0.006] |
| 3 | -0.008 [-0.020, 0.005] |
| 4 | -0.011 [-0.025, 0.001] |
| 5 | -0.014 [-0.027, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.030 [-0.011, 0.076] | -0.024 [-0.083, 0.037] | -0.060 [-0.123, -0.005] |
| 2020 | 251 | -0.011 [-0.017, -0.007] | -0.010 [-0.017, -0.002] | -0.004 [-0.012, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.001 [-0.002, 0.001] | -0.003 [-0.008, 0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.006 [-0.017, 0.031] | -0.004 [-0.025, 0.014] | -0.006 [-0.024, 0.009] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.035, 0.002] | -0.033 [-0.062, -0.010] | -0.039 [-0.061, -0.020] |
| ordinary | 1603 | 0.008 [-0.002, 0.019] | -0.006 [-0.018, 0.007] | -0.011 [-0.025, 0.002] |
| quarter_end | 31 | 0.010 [-0.055, 0.077] | -0.021 [-0.124, 0.072] | -0.012 [-0.088, 0.055] |
| tax_date | 89 | -0.013 [-0.068, 0.035] | -0.004 [-0.046, 0.039] | -0.030 [-0.072, 0.007] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.004 [-0.006, -0.001] | -0.008 [-0.010, -0.005] | -0.006 [-0.008, -0.003] |
| 2 | 41 | 0.067 [–] | 0.061 [–] | 0.032 [–] |
| 3 | 473 | 0.017 [-0.018, 0.055] | -0.028 [-0.076, 0.021] | -0.052 [-0.104, -0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.286, 0.042] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.176] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.217, 0.100] |

## structural_liquidity against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.009, 0.004] |
| 2 | -0.010 [-0.019, -0.002] |
| 3 | -0.012 [-0.023, -0.002] |
| 4 | -0.017 [-0.030, -0.006] |
| 5 | -0.019 [-0.032, -0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.010 [-0.038, 0.022] | -0.048 [-0.099, 0.002] | -0.088 [-0.138, -0.041] |
| 2020 | 251 | -0.004 [-0.011, 0.004] | -0.010 [-0.017, -0.001] | -0.004 [-0.011, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | 0.002 [0.000, 0.005] | -0.001 [-0.006, 0.003] | 0.002 [0.001, 0.004] |
| 2025-26 | 249 | -0.005 [-0.020, 0.007] | -0.005 [-0.022, 0.010] | -0.008 [-0.024, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.040, -0.003] | -0.033 [-0.063, -0.008] | -0.041 [-0.062, -0.022] |
| ordinary | 1603 | -0.001 [-0.006, 0.005] | -0.011 [-0.021, -0.000] | -0.017 [-0.030, -0.006] |
| quarter_end | 31 | 0.010 [-0.052, 0.076] | -0.021 [-0.128, 0.072] | -0.012 [-0.087, 0.056] |
| tax_date | 89 | -0.013 [-0.067, 0.041] | -0.004 [-0.046, 0.040] | -0.030 [-0.073, 0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.000 [-0.001, 0.001] | 0.001 [-0.000, 0.002] |
| 1 | 324 | -0.003 [-0.005, 0.001] | -0.007 [-0.010, -0.003] | -0.005 [-0.007, -0.002] |
| 2 | 41 | -0.000 [-0.044, 0.037] | 0.013 [–] | -0.043 [–] |
| 3 | 473 | -0.013 [-0.036, 0.014] | -0.045 [-0.085, -0.006] | -0.071 [-0.114, -0.032] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.563, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.409, -0.077] |

## projected_reserves against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.007, 0.015] |
| 2 | 0.010 [-0.001, 0.022] |
| 3 | 0.005 [-0.007, 0.018] |
| 4 | 0.006 [-0.007, 0.018] |
| 5 | 0.006 [-0.006, 0.019] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.034 [-0.018, 0.086] | 0.045 [-0.010, 0.102] | 0.035 [-0.020, 0.097] |
| 2020 | 251 | -0.018 [-0.034, -0.005] | -0.027 [-0.050, -0.006] | -0.027 [-0.052, -0.007] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.002 [-0.006, 0.001] | -0.002 [-0.007, 0.001] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.002 [-0.021, 0.013] | -0.001 [-0.013, 0.009] | 0.017 [0.005, 0.032] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.041, -0.004] | -0.007 [-0.029, 0.016] | 0.000 [-0.020, 0.021] |
| ordinary | 1603 | 0.008 [-0.003, 0.019] | 0.007 [-0.005, 0.022] | 0.006 [-0.007, 0.020] |
| quarter_end | 31 | -0.030 [-0.114, 0.053] | -0.007 [-0.095, 0.085] | 0.027 [-0.038, 0.094] |
| tax_date | 89 | -0.009 [-0.056, 0.036] | -0.015 [-0.043, 0.012] | 0.004 [-0.046, 0.053] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.002] | -0.000 [-0.001, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [-0.000, 0.003] | 0.000 [-0.001, 0.001] | 0.000 [-0.001, 0.002] |
| 2 | 41 | 0.044 [–] | -0.009 [–] | 0.007 [-0.127, 0.059] |
| 3 | 473 | 0.010 [-0.033, 0.057] | 0.020 [-0.025, 0.071] | 0.022 [-0.025, 0.074] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.238, 0.091] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.100, 0.231] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.278, 0.273] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.238, 0.143] |

## projected_reserves against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.014, -0.002] |
| 2 | -0.002 [-0.008, 0.005] |
| 3 | -0.002 [-0.011, 0.007] |
| 4 | 0.000 [-0.008, 0.010] |
| 5 | -0.000 [-0.009, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.045, 0.010] | 0.007 [-0.033, 0.050] | 0.011 [-0.031, 0.058] |
| 2020 | 251 | -0.011 [-0.027, 0.001] | -0.028 [-0.051, -0.008] | -0.026 [-0.049, -0.007] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | -0.002 [-0.005, -0.000] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.015 [-0.030, -0.003] | 0.003 [0.000, 0.007] | 0.008 [0.002, 0.016] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.034, 0.005] | 0.009 [-0.012, 0.033] | 0.005 [-0.016, 0.027] |
| ordinary | 1603 | -0.006 [-0.011, -0.001] | -0.003 [-0.010, 0.004] | -0.001 [-0.009, 0.007] |
| quarter_end | 31 | -0.045 [-0.137, 0.041] | -0.017 [-0.132, 0.094] | 0.001 [-0.081, 0.078] |
| tax_date | 89 | -0.008 [-0.045, 0.030] | -0.001 [-0.041, 0.042] | 0.003 [-0.056, 0.067] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.000] | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.001, 0.005] | -0.000 [-0.002, 0.001] | 0.001 [-0.000, 0.002] |
| 2 | 41 | -0.005 [–] | -0.022 [-0.119, 0.018] | -0.007 [-0.126, 0.044] |
| 3 | 473 | -0.030 [-0.052, -0.007] | -0.006 [-0.040, 0.030] | -0.001 [-0.036, 0.037] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.414, -0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.222, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.545, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.333, 0.038] |

## projected_reserves against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.018 [0.010, 0.026] |
| 2 | 0.012 [0.004, 0.021] |
| 3 | 0.009 [0.000, 0.018] |
| 4 | 0.009 [0.001, 0.018] |
| 5 | 0.007 [-0.002, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.035 [-0.002, 0.077] | 0.008 [-0.033, 0.051] | -0.002 [-0.045, 0.043] |
| 2020 | 251 | 0.022 [0.005, 0.035] | 0.011 [-0.012, 0.030] | 0.009 [-0.015, 0.030] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.002 [-0.002, 0.005] | 0.002 [-0.004, 0.005] | 0.002 [-0.003, 0.005] |
| 2025-26 | 249 | 0.013 [0.005, 0.024] | 0.001 [-0.003, 0.004] | 0.003 [0.000, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.033 [0.014, 0.055] | 0.020 [0.002, 0.041] | 0.014 [-0.006, 0.033] |
| ordinary | 1603 | 0.012 [0.005, 0.021] | 0.005 [-0.004, 0.014] | 0.004 [-0.007, 0.013] |
| quarter_end | 31 | 0.086 [0.038, 0.130] | 0.071 [0.027, 0.117] | 0.090 [0.041, 0.139] |
| tax_date | 89 | 0.059 [0.020, 0.097] | 0.038 [0.000, 0.074] | 0.030 [-0.018, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.031 [0.024, 0.037] | 0.029 [0.023, 0.035] | 0.028 [0.022, 0.034] |
| 2 | 41 | 0.036 [–] | -0.040 [–] | -0.034 [–] |
| 3 | 473 | 0.026 [-0.004, 0.059] | -0.001 [-0.034, 0.035] | -0.008 [-0.042, 0.028] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.148, 0.062] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.227, 0.105] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.143] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.182, 0.080] |

## projected_reserves against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.004, 0.010] |
| 2 | 0.002 [-0.006, 0.011] |
| 3 | 0.003 [-0.006, 0.011] |
| 4 | 0.001 [-0.007, 0.010] |
| 5 | -0.000 [-0.010, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.018 [-0.012, 0.050] | 0.008 [-0.032, 0.048] | 0.001 [-0.041, 0.043] |
| 2020 | 251 | -0.002 [-0.016, 0.010] | -0.001 [-0.024, 0.019] | -0.008 [-0.033, 0.013] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | 0.001 [-0.000, 0.003] | 0.002 [0.000, 0.004] |
| 2025-26 | 249 | -0.012 [-0.035, 0.006] | -0.005 [-0.024, 0.009] | -0.005 [-0.027, 0.014] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.014, 0.041] | 0.011 [-0.011, 0.035] | 0.005 [-0.017, 0.027] |
| ordinary | 1603 | -0.000 [-0.005, 0.005] | 0.001 [-0.007, 0.009] | -0.002 [-0.011, 0.007] |
| quarter_end | 31 | 0.025 [-0.087, 0.135] | 0.037 [-0.075, 0.144] | 0.065 [-0.035, 0.168] |
| tax_date | 89 | 0.024 [-0.012, 0.069] | 0.010 [-0.036, 0.057] | 0.004 [-0.056, 0.069] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.003 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.008, 0.013] | 0.019 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.053 [-0.146, 0.051] | -0.086 [–] | -0.110 [–] |
| 3 | 473 | 0.005 [-0.020, 0.033] | -0.001 [-0.033, 0.032] | -0.006 [-0.040, 0.030] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.154, 0.074] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.143, 0.143] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.167 [-0.333, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.190, 0.091] |

## projected_reserves against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.006, 0.016] |
| 2 | 0.001 [-0.009, 0.011] |
| 3 | -0.001 [-0.011, 0.010] |
| 4 | -0.002 [-0.013, 0.009] |
| 5 | -0.005 [-0.015, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.033 [-0.017, 0.087] | 0.018 [-0.033, 0.068] | -0.004 [-0.056, 0.052] |
| 2020 | 251 | -0.017 [-0.032, -0.004] | -0.022 [-0.042, -0.006] | -0.021 [-0.047, -0.000] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.001 [-0.000, 0.001] | -0.002 [-0.008, 0.001] | 0.001 [-0.000, 0.002] |
| 2025-26 | 249 | -0.004 [-0.021, 0.010] | -0.006 [-0.023, 0.006] | -0.008 [-0.019, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.038, -0.003] | -0.012 [-0.029, 0.006] | -0.030 [-0.050, -0.010] |
| ordinary | 1603 | 0.008 [-0.002, 0.020] | 0.002 [-0.009, 0.013] | 0.000 [-0.011, 0.013] |
| quarter_end | 31 | -0.039 [-0.121, 0.039] | -0.038 [-0.121, 0.038] | -0.003 [-0.060, 0.057] |
| tax_date | 89 | -0.010 [-0.057, 0.040] | -0.015 [-0.049, 0.015] | -0.051 [-0.104, -0.006] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.001] | -0.000 [-0.001, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 324 | 0.002 [-0.000, 0.005] | 0.001 [0.000, 0.003] | 0.000 [-0.003, 0.003] |
| 2 | 41 | 0.030 [-0.014, 0.071] | 0.001 [–] | -0.044 [-0.183, 0.029] |
| 3 | 473 | 0.011 [-0.031, 0.058] | -0.003 [-0.045, 0.039] | -0.015 [-0.057, 0.030] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.300, 0.059] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.105, 0.231] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.286, 0.286] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.235, 0.150] |

## projected_reserves against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.011, 0.003] |
| 2 | -0.004 [-0.012, 0.002] |
| 3 | -0.005 [-0.013, 0.003] |
| 4 | -0.008 [-0.017, 0.000] |
| 5 | -0.010 [-0.020, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.007 [-0.038, 0.028] | -0.006 [-0.041, 0.029] | -0.032 [-0.072, 0.007] |
| 2020 | 251 | -0.009 [-0.022, 0.002] | -0.021 [-0.040, -0.005] | -0.021 [-0.046, -0.001] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.004 [0.001, 0.008] | 0.000 [-0.006, 0.004] | 0.003 [0.001, 0.006] |
| 2025-26 | 249 | -0.015 [-0.039, 0.004] | -0.007 [-0.026, 0.010] | -0.010 [-0.035, 0.010] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.026 [-0.045, -0.010] | -0.012 [-0.028, 0.005] | -0.032 [-0.052, -0.013] |
| ordinary | 1603 | -0.001 [-0.007, 0.006] | -0.003 [-0.011, 0.005] | -0.006 [-0.015, 0.003] |
| quarter_end | 31 | -0.039 [-0.124, 0.038] | -0.038 [-0.118, 0.040] | -0.003 [-0.064, 0.053] |
| tax_date | 89 | -0.010 [-0.055, 0.037] | -0.015 [-0.046, 0.017] | -0.051 [-0.105, -0.007] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.002 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.002 [0.001, 0.003] |
| 1 | 324 | 0.003 [0.000, 0.007] | 0.003 [0.001, 0.005] | 0.002 [-0.001, 0.005] |
| 2 | 41 | -0.037 [–] | -0.046 [-0.132, 0.033] | -0.119 [–] |
| 3 | 473 | -0.018 [-0.045, 0.009] | -0.020 [-0.049, 0.011] | -0.034 [-0.067, -0.001] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.258, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.556, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.412, -0.083] |

## risk_gbm+combined against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.005 [-0.001, 0.011] |
| 3 | 0.001 [-0.005, 0.007] |
| 4 | -0.001 [-0.007, 0.004] |
| 5 | 0.002 [-0.005, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.012] | 0.005 [-0.028, 0.035] | -0.003 [-0.037, 0.027] |
| 2020 | 251 | 0.003 [-0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.011 [-0.027, 0.002] | 0.003 [-0.002, 0.009] | 0.022 [0.004, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.049, -0.003] | -0.007 [-0.022, 0.007] | 0.019 [0.007, 0.031] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | 0.003 [-0.004, 0.009] | -0.001 [-0.008, 0.006] |
| quarter_end | 31 | -0.011 [-0.067, 0.049] | -0.002 [-0.061, 0.062] | 0.037 [-0.000, 0.081] |
| tax_date | 89 | -0.039 [-0.073, -0.010] | -0.015 [-0.058, 0.021] | 0.018 [-0.035, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.022 [-0.052, -0.002] | 0.003 [–] | 0.046 [–] |
| 3 | 473 | -0.007 [-0.021, 0.007] | 0.004 [-0.022, 0.028] | 0.006 [-0.024, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.231, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.280, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.227, 0.000] |

## risk_gbm+combined against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.006] |
| 2 | -0.007 [-0.016, 0.000] |
| 3 | -0.006 [-0.016, 0.003] |
| 4 | -0.007 [-0.016, 0.002] |
| 5 | -0.003 [-0.013, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.056 [-0.096, -0.022] | -0.033 [-0.081, 0.013] | -0.027 [-0.072, 0.012] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.010, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.041, -0.008] | 0.007 [-0.002, 0.020] | 0.013 [0.001, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.039, -0.000] | 0.008 [-0.008, 0.025] | 0.023 [0.004, 0.046] |
| ordinary | 1603 | -0.012 [-0.022, -0.003] | -0.008 [-0.018, 0.002] | -0.007 [-0.018, 0.001] |
| quarter_end | 31 | -0.026 [-0.089, 0.029] | -0.011 [-0.074, 0.055] | 0.010 [-0.035, 0.059] |
| tax_date | 89 | -0.038 [-0.076, -0.007] | 0.000 [-0.033, 0.028] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.071 [–] | -0.010 [-0.042, 0.010] | 0.032 [–] |
| 3 | 473 | -0.047 [-0.081, -0.019] | -0.022 [-0.062, 0.014] | -0.017 [-0.053, 0.015] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.435, -0.107] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.429, -0.053] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.571, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.353, -0.043] |

## risk_gbm+combined against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.006, 0.017] |
| 2 | 0.007 [-0.000, 0.014] |
| 3 | 0.005 [-0.002, 0.012] |
| 4 | 0.003 [-0.005, 0.010] |
| 5 | 0.004 [-0.005, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.024, 0.019] | -0.031 [-0.065, -0.001] | -0.040 [-0.076, -0.009] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.028, 0.048] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.015] | 0.005 [-0.006, 0.018] | 0.008 [-0.003, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.045] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.046] |
| ordinary | 1603 | 0.007 [0.002, 0.012] | 0.001 [-0.007, 0.008] | -0.003 [-0.013, 0.005] |
| quarter_end | 31 | 0.105 [0.012, 0.193] | 0.077 [-0.016, 0.181] | 0.100 [0.003, 0.197] |
| tax_date | 89 | 0.029 [-0.003, 0.058] | 0.038 [0.007, 0.067] | 0.044 [0.014, 0.073] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.023, 0.036] | 0.028 [0.022, 0.034] |
| 2 | 41 | -0.030 [–] | -0.028 [–] | 0.005 [–] |
| 3 | 473 | 0.008 [-0.010, 0.026] | -0.017 [-0.045, 0.009] | -0.024 [-0.055, 0.003] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.273, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.462, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.500, 0.200] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.333, 0.158] |

## risk_gbm+combined against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.003] |
| 2 | -0.003 [-0.011, 0.005] |
| 3 | -0.001 [-0.009, 0.006] |
| 4 | -0.006 [-0.015, 0.002] |
| 5 | -0.004 [-0.013, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.051, 0.011] | -0.031 [-0.065, 0.000] | -0.037 [-0.076, -0.002] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.026] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.005] | 0.001 [-0.002, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.053, 0.002] | -0.001 [-0.025, 0.020] | 0.000 [-0.024, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.016, 0.031] | 0.011 [-0.001, 0.023] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.005 [-0.014, 0.002] | -0.004 [-0.013, 0.004] | -0.009 [-0.020, 0.000] |
| quarter_end | 31 | 0.045 [-0.007, 0.106] | 0.042 [-0.011, 0.102] | 0.074 [0.019, 0.144] |
| tax_date | 89 | -0.006 [-0.037, 0.017] | 0.011 [-0.008, 0.030] | 0.018 [-0.003, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.119 [–] | -0.074 [–] | -0.071 [-0.145, 0.024] |
| 3 | 473 | -0.012 [-0.038, 0.012] | -0.017 [-0.046, 0.010] | -0.022 [-0.055, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.238, 0.111] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.353, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.534, 0.083] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.286, 0.143] |

## risk_gbm+combined against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | -0.005 [-0.010, 0.001] |
| 3 | -0.004 [-0.011, 0.001] |
| 4 | -0.009 [-0.016, -0.004] |
| 5 | -0.008 [-0.015, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.020, 0.012] | -0.022 [-0.052, 0.003] | -0.042 [-0.074, -0.017] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.004, 0.015] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.013 [-0.029, 0.001] | -0.002 [-0.010, 0.004] | -0.003 [-0.009, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.002] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.003 [-0.001, 0.006] | -0.003 [-0.009, 0.003] | -0.006 [-0.014, -0.001] |
| quarter_end | 31 | -0.020 [-0.077, 0.033] | -0.032 [-0.093, 0.028] | 0.006 [-0.026, 0.047] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.055, 0.023] | -0.036 [-0.083, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.036 [–] | 0.013 [–] | -0.005 [–] |
| 3 | 473 | -0.006 [-0.021, 0.008] | -0.019 [-0.043, 0.002] | -0.031 [-0.057, -0.010] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.304, -0.038] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.286, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.018, -0.002] |
| 3 | -0.009 [-0.016, -0.002] |
| 4 | -0.015 [-0.025, -0.007] |
| 5 | -0.013 [-0.023, -0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.074, -0.017] | -0.046 [-0.081, -0.016] | -0.070 [-0.109, -0.033] |
| 2020 | 251 | 0.011 [0.001, 0.025] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.015] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.024 [-0.052, -0.001] | -0.003 [-0.021, 0.013] | -0.005 [-0.029, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.055, -0.006] | -0.012 [-0.030, 0.006] | -0.014 [-0.025, -0.002] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.008 [-0.016, -0.000] | -0.012 [-0.022, -0.003] |
| quarter_end | 31 | -0.020 [-0.074, 0.031] | -0.032 [-0.095, 0.023] | 0.006 [-0.026, 0.049] |
| tax_date | 89 | -0.040 [-0.075, -0.008] | -0.014 [-0.054, 0.021] | -0.036 [-0.085, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.001, 0.005] |
| 2 | 41 | -0.103 [–] | -0.034 [–] | -0.080 [–] |
| 3 | 473 | -0.035 [-0.062, -0.010] | -0.036 [-0.064, -0.011] | -0.050 [-0.083, -0.017] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.462, -0.154] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.111] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.417 [-0.667, -0.176] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.452, -0.125] |

## structural_rolling against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.001, 0.020] |
| 2 | 0.012 [0.001, 0.023] |
| 3 | 0.007 [-0.003, 0.019] |
| 4 | 0.008 [-0.002, 0.018] |
| 5 | 0.010 [-0.000, 0.021] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.037 [0.005, 0.072] | 0.041 [0.008, 0.077] | 0.040 [0.009, 0.073] |
| 2020 | 251 | -0.007 [-0.015, -0.001] | -0.005 [-0.009, 0.001] | -0.001 [-0.006, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.008, 0.000] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.031 [-0.006, 0.080] | 0.007 [-0.055, 0.077] | 0.015 [-0.042, 0.081] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.013 [-0.033, 0.008] | -0.013 [-0.050, 0.023] | 0.029 [0.002, 0.064] |
| ordinary | 1603 | 0.013 [0.003, 0.024] | 0.010 [-0.000, 0.021] | 0.007 [-0.003, 0.018] |
| quarter_end | 31 | 0.043 [-0.016, 0.109] | 0.045 [-0.038, 0.136] | 0.047 [-0.020, 0.119] |
| tax_date | 89 | -0.009 [-0.042, 0.029] | -0.019 [-0.052, 0.009] | 0.008 [-0.018, 0.034] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.001] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.007 [-0.012, -0.003] | -0.020 [-0.045, -0.005] | -0.016 [-0.039, -0.002] |
| 2 | 41 | 0.198 [–] | 0.125 [-0.194, 0.384] | 0.188 [–] |
| 3 | 473 | 0.028 [0.001, 0.056] | 0.036 [0.009, 0.066] | 0.034 [0.006, 0.062] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.131, 0.222] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.267, 0.182] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.222, 0.400] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.048 [-0.219, 0.137] |

## structural_rolling against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.008, 0.006] |
| 2 | 0.000 [-0.009, 0.010] |
| 3 | 0.000 [-0.011, 0.012] |
| 4 | 0.003 [-0.007, 0.013] |
| 5 | 0.004 [-0.006, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.016 [-0.038, 0.004] | 0.003 [-0.031, 0.039] | 0.016 [-0.018, 0.048] |
| 2020 | 251 | -0.000 [-0.007, 0.005] | -0.006 [-0.008, -0.003] | -0.000 [-0.005, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.006, -0.001] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.018 [-0.011, 0.059] | 0.011 [-0.053, 0.082] | 0.006 [-0.054, 0.067] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.028, 0.016] | 0.003 [-0.039, 0.046] | 0.034 [0.005, 0.067] |
| ordinary | 1603 | -0.001 [-0.008, 0.006] | -0.000 [-0.010, 0.009] | 0.000 [-0.010, 0.010] |
| quarter_end | 31 | 0.028 [-0.014, 0.077] | 0.035 [-0.027, 0.101] | 0.021 [-0.032, 0.076] |
| tax_date | 89 | -0.008 [-0.030, 0.010] | -0.005 [-0.032, 0.022] | 0.007 [-0.027, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.002 [-0.003, -0.001] | -0.000 [-0.001, -0.000] |
| 1 | 324 | -0.006 [-0.014, 0.000] | -0.020 [-0.045, -0.005] | -0.015 [-0.037, -0.002] |
| 2 | 41 | 0.150 [-0.005, 0.296] | 0.112 [–] | 0.174 [-0.145, 0.391] |
| 3 | 473 | -0.013 [-0.031, 0.004] | 0.009 [-0.019, 0.040] | 0.011 [-0.018, 0.039] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.261, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.385, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.455, 0.100] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.318, 0.000] |

## structural_rolling against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.024 [0.016, 0.032] |
| 2 | 0.014 [0.005, 0.024] |
| 3 | 0.011 [0.002, 0.021] |
| 4 | 0.012 [0.004, 0.020] |
| 5 | 0.011 [0.002, 0.020] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.039 [0.015, 0.063] | 0.005 [-0.018, 0.031] | 0.003 [-0.015, 0.023] |
| 2020 | 251 | 0.032 [0.022, 0.042] | 0.033 [0.026, 0.040] | 0.035 [0.027, 0.043] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.012 [0.010, 0.014] | 0.013 [0.012, 0.015] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.004, 0.005] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.047 [0.006, 0.096] | 0.009 [-0.053, 0.073] | 0.001 [-0.053, 0.057] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.042 [0.013, 0.071] | 0.014 [-0.028, 0.055] | 0.043 [0.018, 0.074] |
| ordinary | 1603 | 0.017 [0.011, 0.025] | 0.008 [0.000, 0.016] | 0.005 [-0.003, 0.013] |
| quarter_end | 31 | 0.159 [0.085, 0.243] | 0.123 [0.045, 0.204] | 0.110 [0.006, 0.213] |
| tax_date | 89 | 0.059 [0.033, 0.085] | 0.034 [-0.001, 0.065] | 0.034 [-0.005, 0.068] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.008 [0.006, 0.010] | 0.007 [0.006, 0.009] | 0.008 [0.007, 0.010] |
| 1 | 324 | 0.023 [0.011, 0.032] | 0.009 [-0.019, 0.028] | 0.012 [-0.015, 0.029] |
| 2 | 41 | 0.191 [0.021, 0.332] | 0.094 [–] | 0.147 [–] |
| 3 | 473 | 0.043 [0.022, 0.065] | 0.014 [-0.007, 0.038] | 0.003 [-0.015, 0.022] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.129, 0.300] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.357, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.286, 0.300] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | -0.048 [-0.250, 0.160] |

## structural_rolling against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.009 [0.004, 0.014] |
| 2 | 0.004 [-0.003, 0.012] |
| 3 | 0.005 [-0.003, 0.014] |
| 4 | 0.003 [-0.004, 0.010] |
| 5 | 0.003 [-0.003, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.022 [0.004, 0.041] | 0.005 [-0.016, 0.028] | 0.006 [-0.010, 0.023] |
| 2020 | 251 | 0.009 [0.007, 0.011] | 0.021 [0.017, 0.024] | 0.017 [0.014, 0.021] |
| 2021-23 | 748 | 0.000 [0.000, 0.001] | 0.002 [0.001, 0.003] | 0.002 [0.001, 0.002] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [-0.000, 0.002] | 0.001 [-0.000, 0.003] |
| 2025-26 | 249 | 0.021 [0.001, 0.045] | 0.002 [-0.050, 0.058] | -0.007 [-0.051, 0.040] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.021 [-0.000, 0.042] | 0.005 [-0.032, 0.043] | 0.034 [0.011, 0.059] |
| ordinary | 1603 | 0.005 [0.001, 0.010] | 0.003 [-0.003, 0.011] | -0.001 [-0.008, 0.005] |
| quarter_end | 31 | 0.098 [0.037, 0.168] | 0.089 [0.022, 0.161] | 0.085 [0.023, 0.156] |
| tax_date | 89 | 0.024 [0.002, 0.047] | 0.006 [-0.028, 0.044] | 0.008 [-0.029, 0.049] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.001] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.002 [-0.005, 0.007] | -0.001 [-0.026, 0.016] | -0.002 [-0.025, 0.014] |
| 2 | 41 | 0.101 [–] | 0.048 [–] | 0.071 [–] |
| 3 | 473 | 0.023 [0.008, 0.039] | 0.014 [-0.006, 0.036] | 0.006 [-0.009, 0.021] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.115, 0.292] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.250, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.400, 0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | -0.048 [-0.226, 0.143] |

## structural_rolling against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.001, 0.020] |
| 2 | 0.003 [-0.007, 0.013] |
| 3 | 0.002 [-0.007, 0.012] |
| 4 | -0.000 [-0.008, 0.010] |
| 5 | -0.001 [-0.010, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.037 [0.004, 0.072] | 0.014 [-0.013, 0.044] | 0.001 [-0.025, 0.029] |
| 2020 | 251 | -0.006 [-0.013, 0.000] | 0.000 [-0.007, 0.007] | 0.004 [-0.002, 0.012] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | -0.001 [-0.002, 0.001] | -0.003 [-0.009, 0.000] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | 0.029 [-0.007, 0.077] | 0.001 [-0.053, 0.065] | -0.010 [-0.062, 0.049] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.012 [-0.033, 0.007] | -0.017 [-0.052, 0.019] | -0.001 [-0.023, 0.024] |
| ordinary | 1603 | 0.013 [0.004, 0.024] | 0.005 [-0.005, 0.015] | 0.001 [-0.008, 0.011] |
| quarter_end | 31 | 0.034 [-0.010, 0.083] | 0.014 [-0.074, 0.106] | 0.017 [-0.061, 0.100] |
| tax_date | 89 | -0.010 [-0.042, 0.025] | -0.019 [-0.061, 0.019] | -0.047 [-0.088, -0.011] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.001] | -0.000 [-0.001, -0.000] |
| 1 | 324 | -0.006 [-0.012, -0.002] | -0.019 [-0.042, -0.003] | -0.016 [-0.040, -0.001] |
| 2 | 41 | 0.185 [–] | 0.136 [–] | 0.137 [–] |
| 3 | 473 | 0.029 [0.002, 0.057] | 0.012 [-0.011, 0.037] | -0.003 [-0.028, 0.022] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.167, 0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.294, 0.182] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.250, 0.400] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.048 [-0.233, 0.143] |

## structural_rolling against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.004, 0.008] |
| 2 | -0.002 [-0.010, 0.006] |
| 3 | -0.002 [-0.011, 0.007] |
| 4 | -0.006 [-0.013, 0.002] |
| 5 | -0.006 [-0.014, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.003 [-0.028, 0.022] | -0.010 [-0.033, 0.014] | -0.027 [-0.051, -0.002] |
| 2020 | 251 | 0.002 [-0.005, 0.009] | 0.001 [-0.006, 0.009] | 0.005 [-0.002, 0.012] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.001 [-0.002, -0.001] | -0.000 [-0.001, -0.000] |
| 2024 | 250 | 0.002 [0.000, 0.005] | -0.001 [-0.006, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | 0.018 [-0.006, 0.049] | 0.001 [-0.052, 0.059] | -0.012 [-0.057, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.037, 0.003] | -0.017 [-0.056, 0.019] | -0.003 [-0.025, 0.020] |
| ordinary | 1603 | 0.004 [-0.002, 0.010] | -0.000 [-0.008, 0.008] | -0.005 [-0.013, 0.003] |
| quarter_end | 31 | 0.034 [-0.013, 0.083] | 0.014 [-0.070, 0.105] | 0.017 [-0.061, 0.102] |
| tax_date | 89 | -0.010 [-0.043, 0.027] | -0.019 [-0.060, 0.020] | -0.047 [-0.088, -0.012] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | -0.000 [-0.001, 0.001] | 0.001 [0.000, 0.002] |
| 1 | 324 | -0.005 [-0.010, -0.000] | -0.017 [-0.039, -0.002] | -0.015 [-0.039, 0.001] |
| 2 | 41 | 0.117 [–] | 0.088 [–] | 0.062 [–] |
| 3 | 473 | -0.001 [-0.020, 0.020] | -0.005 [-0.024, 0.017] | -0.022 [-0.043, -0.000] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.300, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.421, -0.067] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.500, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.238 [-0.400, -0.091] |

## structural_rolling against structural_liquidity

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.000, 0.011] |
| 2 | 0.008 [-0.003, 0.018] |
| 3 | 0.010 [-0.001, 0.023] |
| 4 | 0.011 [0.000, 0.023] |
| 5 | 0.013 [0.001, 0.026] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.006 [-0.016, 0.028] | 0.038 [-0.006, 0.087] | 0.061 [0.011, 0.111] |
| 2020 | 251 | 0.006 [0.002, 0.010] | 0.010 [0.007, 0.015] | 0.009 [0.006, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.001, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | 0.024 [-0.000, 0.052] | 0.006 [-0.047, 0.064] | -0.004 [-0.049, 0.044] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.014, 0.019] | 0.015 [-0.022, 0.056] | 0.038 [0.012, 0.070] |
| ordinary | 1603 | 0.005 [0.000, 0.010] | 0.010 [-0.001, 0.022] | 0.012 [-0.000, 0.025] |
| quarter_end | 31 | 0.024 [-0.028, 0.082] | 0.035 [-0.034, 0.115] | 0.029 [-0.042, 0.108] |
| tax_date | 89 | 0.003 [-0.040, 0.050] | -0.015 [-0.062, 0.028] | -0.017 [-0.076, 0.030] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 324 | -0.002 [-0.009, 0.002] | -0.011 [-0.036, 0.005] | -0.010 [-0.031, 0.004] |
| 2 | 41 | 0.117 [0.008, 0.182] | 0.075 [–] | 0.104 [–] |
| 3 | 473 | 0.012 [-0.006, 0.030] | 0.040 [0.006, 0.081] | 0.049 [0.008, 0.091] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.107, 0.345] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.320, 0.091] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.231, 0.417] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.214, 0.227] |

## structural_fitted against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.004, 0.015] |
| 2 | 0.004 [-0.008, 0.017] |
| 3 | -0.002 [-0.016, 0.012] |
| 4 | -0.003 [-0.018, 0.009] |
| 5 | -0.003 [-0.018, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.030 [-0.011, 0.079] | 0.003 [-0.063, 0.073] | -0.021 [-0.092, 0.046] |
| 2020 | 251 | -0.013 [-0.019, -0.008] | -0.015 [-0.023, -0.007] | -0.010 [-0.017, -0.003] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.007, -0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | 0.008 [-0.016, 0.031] | 0.001 [-0.017, 0.018] | 0.019 [0.001, 0.039] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.036, 0.004] | -0.028 [-0.062, 0.000] | -0.009 [-0.028, 0.009] |
| ordinary | 1603 | 0.007 [-0.002, 0.019] | -0.000 [-0.015, 0.014] | -0.005 [-0.020, 0.010] |
| quarter_end | 31 | 0.019 [-0.037, 0.088] | 0.009 [-0.072, 0.094] | 0.019 [-0.043, 0.082] |
| tax_date | 89 | -0.013 [-0.066, 0.039] | -0.004 [-0.040, 0.034] | 0.025 [-0.014, 0.068] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, 0.001] | -0.001 [-0.003, -0.000] | -0.001 [-0.001, -0.001] |
| 1 | 324 | -0.004 [-0.006, -0.003] | -0.009 [-0.011, -0.007] | -0.006 [-0.007, -0.004] |
| 2 | 41 | 0.081 [-0.024, 0.175] | 0.051 [-0.001, 0.087] | 0.084 [–] |
| 3 | 473 | 0.016 [-0.018, 0.056] | -0.005 [-0.059, 0.050] | -0.015 [-0.072, 0.038] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.222, 0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.217, 0.091] |

## structural_fitted against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.007 [-0.013, -0.001] |
| 2 | -0.008 [-0.017, 0.001] |
| 3 | -0.010 [-0.022, 0.002] |
| 4 | -0.009 [-0.019, 0.002] |
| 5 | -0.009 [-0.019, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.022 [-0.049, 0.006] | -0.035 [-0.093, 0.022] | -0.045 [-0.091, 0.001] |
| 2020 | 251 | -0.006 [-0.012, -0.001] | -0.016 [-0.022, -0.012] | -0.009 [-0.013, -0.005] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.006 [-0.023, 0.011] | 0.005 [-0.005, 0.019] | 0.010 [-0.005, 0.029] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.009 [-0.032, 0.013] | -0.013 [-0.049, 0.019] | -0.004 [-0.028, 0.022] |
| ordinary | 1603 | -0.006 [-0.012, -0.001] | -0.011 [-0.023, -0.001] | -0.012 [-0.021, -0.003] |
| quarter_end | 31 | 0.003 [-0.065, 0.071] | -0.000 [-0.094, 0.101] | -0.008 [-0.058, 0.054] |
| tax_date | 89 | -0.011 [-0.057, 0.036] | 0.010 [-0.037, 0.069] | 0.024 [-0.032, 0.088] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.003 [-0.007, -0.001] | -0.009 [-0.011, -0.007] | -0.005 [-0.007, -0.004] |
| 2 | 41 | 0.032 [-0.058, 0.120] | 0.037 [-0.026, 0.084] | 0.070 [–] |
| 3 | 473 | -0.025 [-0.047, -0.002] | -0.031 [-0.078, 0.015] | -0.038 [-0.074, -0.002] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.429, -0.045] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.235, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.556, 0.003] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.333, 0.040] |

## structural_fitted against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.019 [0.011, 0.027] |
| 2 | 0.007 [-0.004, 0.016] |
| 3 | 0.002 [-0.012, 0.013] |
| 4 | 0.001 [-0.012, 0.012] |
| 5 | -0.002 [-0.014, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [-0.006, 0.073] | -0.033 [-0.092, 0.025] | -0.058 [-0.115, -0.004] |
| 2020 | 251 | 0.027 [0.015, 0.037] | 0.022 [0.013, 0.031] | 0.026 [0.018, 0.035] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.012 [0.010, 0.013] | 0.013 [0.011, 0.015] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.001 [-0.003, 0.004] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.023 [0.003, 0.050] | 0.003 [-0.003, 0.010] | 0.004 [-0.005, 0.015] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.039 [0.010, 0.070] | -0.001 [-0.034, 0.028] | 0.005 [-0.015, 0.024] |
| ordinary | 1603 | 0.012 [0.004, 0.021] | -0.002 [-0.016, 0.009] | -0.007 [-0.021, 0.005] |
| quarter_end | 31 | 0.134 [0.073, 0.198] | 0.088 [0.026, 0.149] | 0.082 [-0.003, 0.178] |
| tax_date | 89 | 0.056 [0.014, 0.102] | 0.049 [-0.001, 0.096] | 0.051 [0.001, 0.097] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.008 [0.007, 0.010] | 0.008 [0.006, 0.009] | 0.008 [0.006, 0.010] |
| 1 | 324 | 0.025 [0.019, 0.031] | 0.020 [0.015, 0.025] | 0.022 [0.017, 0.027] |
| 2 | 41 | 0.073 [–] | 0.019 [–] | 0.043 [–] |
| 3 | 473 | 0.031 [0.000, 0.065] | -0.026 [-0.073, 0.020] | -0.046 [-0.092, -0.003] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.154, 0.074] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.167] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.091] |

## structural_fitted against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.003, 0.010] |
| 2 | -0.003 [-0.013, 0.006] |
| 3 | -0.005 [-0.017, 0.006] |
| 4 | -0.008 [-0.020, 0.003] |
| 5 | -0.010 [-0.021, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.015 [-0.016, 0.048] | -0.033 [-0.091, 0.019] | -0.055 [-0.110, -0.004] |
| 2020 | 251 | 0.003 [-0.002, 0.007] | 0.010 [0.006, 0.014] | 0.009 [0.004, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.002 [0.001, 0.002] | 0.001 [0.001, 0.002] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.002] |
| 2025-26 | 249 | -0.003 [-0.010, 0.003] | -0.003 [-0.013, 0.004] | -0.003 [-0.013, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.018 [-0.011, 0.047] | -0.011 [-0.044, 0.021] | -0.004 [-0.026, 0.017] |
| ordinary | 1603 | -0.000 [-0.006, 0.005] | -0.007 [-0.020, 0.004] | -0.013 [-0.026, -0.002] |
| quarter_end | 31 | 0.074 [0.003, 0.155] | 0.053 [-0.030, 0.152] | 0.056 [0.005, 0.119] |
| tax_date | 89 | 0.020 [-0.026, 0.072] | 0.021 [-0.034, 0.083] | 0.025 [-0.029, 0.087] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.001] | 0.001 [0.001, 0.001] | 0.001 [0.001, 0.001] |
| 1 | 324 | 0.005 [0.003, 0.006] | 0.010 [0.008, 0.012] | 0.008 [0.006, 0.010] |
| 2 | 41 | -0.016 [–] | -0.027 [–] | -0.033 [–] |
| 3 | 473 | 0.011 [-0.014, 0.037] | -0.026 [-0.072, 0.016] | -0.043 [-0.087, -0.003] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.190, 0.111] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.222, 0.214] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.167 [-0.429, 0.125] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.235, 0.136] |

## structural_fitted against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.004, 0.015] |
| 2 | -0.005 [-0.016, 0.006] |
| 3 | -0.008 [-0.021, 0.004] |
| 4 | -0.011 [-0.024, 0.001] |
| 5 | -0.014 [-0.027, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.030 [-0.012, 0.075] | -0.024 [-0.085, 0.035] | -0.060 [-0.121, -0.001] |
| 2020 | 251 | -0.011 [-0.017, -0.007] | -0.010 [-0.018, -0.002] | -0.004 [-0.012, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.001 [-0.002, 0.001] | -0.003 [-0.008, 0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.006 [-0.016, 0.029] | -0.004 [-0.024, 0.013] | -0.006 [-0.024, 0.009] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.034, 0.002] | -0.033 [-0.063, -0.009] | -0.039 [-0.060, -0.020] |
| ordinary | 1603 | 0.008 [-0.002, 0.019] | -0.006 [-0.019, 0.006] | -0.011 [-0.025, 0.002] |
| quarter_end | 31 | 0.010 [-0.055, 0.075] | -0.021 [-0.120, 0.077] | -0.012 [-0.085, 0.054] |
| tax_date | 89 | -0.013 [-0.066, 0.036] | -0.004 [-0.047, 0.037] | -0.030 [-0.073, 0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.004 [-0.006, -0.001] | -0.008 [-0.010, -0.005] | -0.006 [-0.009, -0.003] |
| 2 | 41 | 0.067 [–] | 0.061 [–] | 0.032 [–] |
| 3 | 473 | 0.017 [-0.017, 0.054] | -0.028 [-0.077, 0.018] | -0.052 [-0.101, -0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.286, 0.038] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.176] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.222, 0.100] |

## structural_fitted against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.009, 0.003] |
| 2 | -0.010 [-0.019, -0.002] |
| 3 | -0.012 [-0.023, -0.002] |
| 4 | -0.017 [-0.029, -0.007] |
| 5 | -0.019 [-0.031, -0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.010 [-0.037, 0.020] | -0.048 [-0.102, 0.001] | -0.088 [-0.138, -0.039] |
| 2020 | 251 | -0.004 [-0.011, 0.004] | -0.010 [-0.016, -0.001] | -0.004 [-0.012, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | 0.002 [0.000, 0.005] | -0.001 [-0.006, 0.003] | 0.002 [0.001, 0.004] |
| 2025-26 | 249 | -0.005 [-0.021, 0.008] | -0.005 [-0.021, 0.009] | -0.008 [-0.024, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.040, -0.002] | -0.033 [-0.062, -0.008] | -0.041 [-0.062, -0.022] |
| ordinary | 1603 | -0.001 [-0.007, 0.005] | -0.011 [-0.022, -0.001] | -0.017 [-0.029, -0.005] |
| quarter_end | 31 | 0.010 [-0.052, 0.074] | -0.021 [-0.118, 0.079] | -0.012 [-0.086, 0.061] |
| tax_date | 89 | -0.013 [-0.064, 0.038] | -0.004 [-0.047, 0.039] | -0.030 [-0.073, 0.009] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.000 [-0.001, 0.001] | 0.001 [-0.000, 0.002] |
| 1 | 324 | -0.003 [-0.005, 0.001] | -0.007 [-0.010, -0.003] | -0.005 [-0.007, -0.002] |
| 2 | 41 | -0.000 [–] | 0.013 [–] | -0.043 [-0.096, 0.015] |
| 3 | 473 | -0.013 [-0.036, 0.013] | -0.045 [-0.087, -0.006] | -0.071 [-0.113, -0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.435, -0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.571, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.429, -0.083] |

## structural_fitted against structural_liquidity

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.000, 0.000] |
| 2 | 0.000 [0.000, 0.000] |
| 3 | -0.000 [-0.000, 0.000] |
| 4 | 0.000 [-0.000, 0.000] |
| 5 | 0.000 [-0.000, 0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2020 | 251 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| ordinary | 1603 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| quarter_end | 31 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| tax_date | 89 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2 | 41 | 0.000 [–] | 0.000 [–] | 0.000 [–] |
| 3 | 473 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [0.000, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [0.000, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## projected_hinge_fixed against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.008, 0.014] |
| 2 | 0.009 [-0.003, 0.022] |
| 3 | 0.004 [-0.008, 0.017] |
| 4 | 0.004 [-0.007, 0.018] |
| 5 | -0.001 [-0.015, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.034 [-0.015, 0.084] | 0.047 [-0.009, 0.106] | 0.009 [-0.064, 0.080] |
| 2020 | 251 | -0.019 [-0.034, -0.006] | -0.028 [-0.052, -0.008] | -0.028 [-0.053, -0.008] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.002 [-0.005, 0.001] | -0.002 [-0.006, 0.001] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.009 [-0.027, 0.005] | -0.009 [-0.024, 0.003] | 0.010 [0.001, 0.022] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.023 [-0.042, -0.004] | -0.006 [-0.027, 0.017] | -0.009 [-0.038, 0.015] |
| ordinary | 1603 | 0.007 [-0.003, 0.019] | 0.007 [-0.006, 0.021] | -0.000 [-0.015, 0.015] |
| quarter_end | 31 | -0.042 [-0.126, 0.037] | -0.028 [-0.115, 0.055] | 0.012 [-0.049, 0.070] |
| tax_date | 89 | -0.013 [-0.060, 0.035] | -0.020 [-0.049, 0.009] | 0.000 [-0.046, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.001, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.000 [-0.001, 0.002] | -0.001 [-0.002, -0.000] | -0.001 [-0.002, 0.000] |
| 2 | 41 | 0.014 [–] | -0.020 [–] | -0.080 [–] |
| 3 | 473 | 0.009 [-0.033, 0.053] | 0.019 [-0.030, 0.070] | 0.005 [-0.051, 0.062] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.235, 0.087] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.107, 0.250] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.286, 0.286] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.238, 0.138] |

## projected_hinge_fixed against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.009 [-0.015, -0.002] |
| 2 | -0.003 [-0.009, 0.004] |
| 3 | -0.003 [-0.012, 0.006] |
| 4 | -0.001 [-0.009, 0.008] |
| 5 | -0.007 [-0.018, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.048, 0.010] | 0.009 [-0.031, 0.053] | -0.015 [-0.068, 0.044] |
| 2020 | 251 | -0.012 [-0.027, 0.001] | -0.029 [-0.053, -0.010] | -0.027 [-0.051, -0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | -0.002 [-0.005, -0.000] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.022 [-0.040, -0.008] | -0.005 [-0.009, -0.000] | 0.001 [-0.003, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.017 [-0.037, 0.003] | 0.009 [-0.011, 0.033] | -0.004 [-0.033, 0.023] |
| ordinary | 1603 | -0.007 [-0.012, -0.002] | -0.003 [-0.011, 0.004] | -0.007 [-0.017, 0.004] |
| quarter_end | 31 | -0.058 [-0.152, 0.027] | -0.037 [-0.144, 0.076] | -0.014 [-0.092, 0.059] |
| tax_date | 89 | -0.012 [-0.049, 0.028] | -0.005 [-0.044, 0.039] | -0.001 [-0.060, 0.064] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [-0.002, 0.004] | -0.001 [-0.003, -0.000] | -0.001 [-0.001, 0.000] |
| 2 | 41 | -0.034 [–] | -0.033 [-0.110, -0.001] | -0.094 [–] |
| 3 | 473 | -0.031 [-0.056, -0.006] | -0.007 [-0.041, 0.030] | -0.017 [-0.057, 0.030] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.429, -0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.231, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.545, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.333, 0.002] |

## projected_hinge_fixed against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.016 [0.009, 0.025] |
| 2 | 0.011 [0.003, 0.020] |
| 3 | 0.008 [-0.000, 0.018] |
| 4 | 0.008 [-0.001, 0.017] |
| 5 | 0.001 [-0.011, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.035 [-0.003, 0.074] | 0.010 [-0.031, 0.055] | -0.028 [-0.086, 0.027] |
| 2020 | 251 | 0.021 [0.005, 0.035] | 0.010 [-0.012, 0.029] | 0.008 [-0.016, 0.028] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.015] | 0.014 [0.012, 0.015] |
| 2024 | 250 | 0.002 [-0.002, 0.005] | 0.002 [-0.003, 0.005] | 0.002 [-0.002, 0.005] |
| 2025-26 | 249 | 0.006 [0.000, 0.014] | -0.007 [-0.016, 0.001] | -0.005 [-0.011, 0.001] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.031 [0.012, 0.052] | 0.021 [0.003, 0.043] | 0.005 [-0.024, 0.029] |
| ordinary | 1603 | 0.012 [0.004, 0.020] | 0.005 [-0.004, 0.015] | -0.003 [-0.014, 0.009] |
| quarter_end | 31 | 0.073 [0.029, 0.115] | 0.051 [0.002, 0.096] | 0.075 [0.022, 0.130] |
| tax_date | 89 | 0.055 [0.019, 0.093] | 0.033 [-0.005, 0.070] | 0.026 [-0.020, 0.070] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.036] | 0.028 [0.022, 0.034] | 0.027 [0.021, 0.032] |
| 2 | 41 | 0.007 [–] | -0.051 [–] | -0.121 [–] |
| 3 | 473 | 0.025 [-0.006, 0.057] | -0.002 [-0.035, 0.035] | -0.025 [-0.067, 0.018] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.143, 0.069] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.222, 0.105] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.167] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.179, 0.087] |

## projected_hinge_fixed against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.006, 0.009] |
| 2 | 0.001 [-0.007, 0.010] |
| 3 | 0.002 [-0.007, 0.011] |
| 4 | -0.001 [-0.009, 0.009] |
| 5 | -0.007 [-0.018, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.018 [-0.011, 0.051] | 0.010 [-0.029, 0.051] | -0.025 [-0.079, 0.026] |
| 2020 | 251 | -0.003 [-0.017, 0.009] | -0.002 [-0.025, 0.018] | -0.010 [-0.036, 0.012] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.001, 0.003] |
| 2024 | 250 | 0.002 [0.000, 0.006] | 0.002 [0.000, 0.003] | 0.002 [0.001, 0.004] |
| 2025-26 | 249 | -0.019 [-0.050, 0.003] | -0.013 [-0.034, 0.003] | -0.012 [-0.036, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.010 [-0.016, 0.039] | 0.012 [-0.011, 0.038] | -0.005 [-0.034, 0.022] |
| ordinary | 1603 | -0.001 [-0.007, 0.005] | 0.000 [-0.008, 0.009] | -0.009 [-0.019, 0.002] |
| quarter_end | 31 | 0.013 [-0.096, 0.128] | 0.016 [-0.097, 0.116] | 0.049 [-0.042, 0.148] |
| tax_date | 89 | 0.020 [-0.015, 0.062] | 0.006 [-0.042, 0.055] | 0.000 [-0.061, 0.066] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.009 [0.007, 0.011] | 0.018 [0.014, 0.022] | 0.013 [0.010, 0.016] |
| 2 | 41 | -0.083 [–] | -0.097 [–] | -0.197 [–] |
| 3 | 473 | 0.004 [-0.021, 0.033] | -0.002 [-0.035, 0.032] | -0.023 [-0.062, 0.018] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.154, 0.071] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.154, 0.143] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.167 [-0.353, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.191, 0.087] |

## projected_hinge_fixed against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.007, 0.015] |
| 2 | -0.001 [-0.010, 0.011] |
| 3 | -0.001 [-0.011, 0.010] |
| 4 | -0.004 [-0.015, 0.008] |
| 5 | -0.011 [-0.024, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.033 [-0.014, 0.086] | 0.020 [-0.028, 0.072] | -0.030 [-0.092, 0.032] |
| 2020 | 251 | -0.017 [-0.032, -0.005] | -0.023 [-0.042, -0.006] | -0.023 [-0.047, -0.003] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.001 [-0.000, 0.002] | -0.002 [-0.008, 0.001] | 0.001 [-0.000, 0.002] |
| 2025-26 | 249 | -0.011 [-0.029, 0.003] | -0.014 [-0.034, 0.001] | -0.015 [-0.030, -0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.022 [-0.041, -0.004] | -0.011 [-0.028, 0.007] | -0.039 [-0.068, -0.013] |
| ordinary | 1603 | 0.007 [-0.003, 0.019] | 0.002 [-0.009, 0.013] | -0.006 [-0.019, 0.008] |
| quarter_end | 31 | -0.052 [-0.139, 0.031] | -0.058 [-0.143, 0.021] | -0.019 [-0.072, 0.036] |
| tax_date | 89 | -0.013 [-0.061, 0.033] | -0.019 [-0.054, 0.010] | -0.055 [-0.107, -0.009] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.000 [-0.001, 0.003] | 0.000 [-0.001, 0.002] | -0.001 [-0.004, 0.002] |
| 2 | 41 | 0.001 [–] | -0.009 [–] | -0.132 [–] |
| 3 | 473 | 0.010 [-0.031, 0.055] | -0.004 [-0.043, 0.040] | -0.032 [-0.080, 0.019] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.308, 0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.106, 0.231] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.294, 0.286] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.241, 0.136] |

## projected_hinge_fixed against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.005 [-0.013, 0.003] |
| 2 | -0.005 [-0.013, 0.002] |
| 3 | -0.006 [-0.014, 0.002] |
| 4 | -0.010 [-0.019, -0.001] |
| 5 | -0.016 [-0.029, -0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.007 [-0.038, 0.027] | -0.004 [-0.040, 0.033] | -0.058 [-0.113, -0.010] |
| 2020 | 251 | -0.010 [-0.023, 0.001] | -0.022 [-0.041, -0.006] | -0.022 [-0.047, -0.001] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [0.000, 0.001] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.004 [0.001, 0.008] | 0.000 [-0.005, 0.004] | 0.003 [0.001, 0.006] |
| 2025-26 | 249 | -0.022 [-0.050, 0.000] | -0.015 [-0.039, 0.006] | -0.017 [-0.045, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.028 [-0.048, -0.011] | -0.011 [-0.028, 0.006] | -0.041 [-0.070, -0.017] |
| ordinary | 1603 | -0.002 [-0.008, 0.005] | -0.003 [-0.011, 0.005] | -0.012 [-0.023, -0.001] |
| quarter_end | 31 | -0.052 [-0.132, 0.029] | -0.058 [-0.139, 0.017] | -0.019 [-0.075, 0.031] |
| tax_date | 89 | -0.013 [-0.059, 0.034] | -0.019 [-0.051, 0.011] | -0.055 [-0.106, -0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.002 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.003] |
| 1 | 324 | 0.002 [-0.001, 0.005] | 0.002 [-0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.067 [–] | -0.057 [–] | -0.207 [–] |
| 3 | 473 | -0.019 [-0.047, 0.010] | -0.021 [-0.051, 0.010] | -0.051 [-0.091, -0.013] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.120] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.250, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.556, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.417, -0.083] |

## projected_hinge_fixed against projected_reserves

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.002, -0.000] |
| 2 | -0.001 [-0.002, -0.000] |
| 3 | -0.001 [-0.002, 0.000] |
| 4 | -0.002 [-0.003, -0.001] |
| 5 | -0.006 [-0.013, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.000 [-0.001, 0.001] | 0.002 [-0.001, 0.007] | -0.026 [-0.056, -0.003] |
| 2020 | 251 | -0.001 [-0.001, -0.001] | -0.001 [-0.001, -0.000] | -0.001 [-0.002, -0.001] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.007 [-0.013, -0.002] | -0.008 [-0.014, -0.003] | -0.007 [-0.013, -0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.002 [-0.005, 0.001] | 0.001 [-0.004, 0.007] | -0.009 [-0.022, -0.001] |
| ordinary | 1603 | -0.001 [-0.001, -0.000] | -0.000 [-0.001, 0.000] | -0.006 [-0.012, -0.001] |
| quarter_end | 31 | -0.013 [-0.030, -0.000] | -0.020 [-0.043, -0.001] | -0.016 [-0.040, 0.006] |
| tax_date | 89 | -0.004 [-0.007, -0.001] | -0.005 [-0.008, -0.002] | -0.004 [-0.006, -0.002] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | -0.001 [-0.002, -0.000] | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] |
| 2 | 41 | -0.030 [–] | -0.011 [–] | -0.088 [-0.282, -0.019] |
| 3 | 473 | -0.001 [-0.002, 0.000] | -0.001 [-0.004, 0.001] | -0.017 [-0.037, -0.002] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [0.000, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [0.000, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## projected_rolling against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.005, 0.014] |
| 2 | 0.012 [0.003, 0.023] |
| 3 | 0.006 [-0.004, 0.017] |
| 4 | 0.008 [-0.001, 0.019] |
| 5 | 0.007 [-0.003, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.025 [-0.008, 0.062] | 0.052 [0.023, 0.084] | 0.034 [-0.004, 0.074] |
| 2020 | 251 | -0.009 [-0.017, -0.003] | -0.007 [-0.012, -0.002] | -0.016 [-0.027, -0.006] |
| 2021-23 | 748 | -0.003 [-0.006, -0.001] | -0.013 [-0.024, -0.006] | -0.006 [-0.010, -0.003] |
| 2024 | 250 | -0.001 [-0.003, -0.000] | -0.002 [-0.005, 0.000] | 0.000 [-0.001, 0.002] |
| 2025-26 | 249 | 0.012 [-0.026, 0.060] | 0.016 [-0.027, 0.069] | 0.033 [-0.012, 0.096] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.037, 0.007] | 0.005 [-0.016, 0.031] | 0.007 [-0.022, 0.043] |
| ordinary | 1603 | 0.007 [-0.001, 0.018] | 0.008 [-0.002, 0.019] | 0.008 [-0.003, 0.019] |
| quarter_end | 31 | -0.006 [-0.080, 0.076] | 0.001 [-0.099, 0.106] | 0.018 [-0.066, 0.105] |
| tax_date | 89 | -0.025 [-0.060, 0.016] | -0.023 [-0.044, -0.002] | -0.010 [-0.045, 0.030] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.003 [-0.005, -0.001] | -0.009 [-0.017, -0.004] | -0.004 [-0.007, -0.002] |
| 1 | 324 | -0.010 [-0.015, -0.006] | -0.014 [-0.021, -0.009] | -0.014 [-0.021, -0.009] |
| 2 | 41 | 0.137 [–] | 0.164 [–] | 0.118 [-0.274, 0.354] |
| 3 | 473 | 0.015 [-0.012, 0.046] | 0.040 [0.015, 0.067] | 0.036 [0.005, 0.067] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.143, 0.226] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.211, 0.222] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.236, 0.400] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.048 [-0.235, 0.150] |

## projected_rolling against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, 0.000] |
| 2 | 0.000 [-0.008, 0.009] |
| 3 | -0.001 [-0.012, 0.010] |
| 4 | 0.003 [-0.006, 0.013] |
| 5 | 0.001 [-0.010, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.028 [-0.059, 0.001] | 0.014 [-0.023, 0.049] | 0.010 [-0.035, 0.054] |
| 2020 | 251 | -0.003 [-0.008, 0.003] | -0.008 [-0.012, -0.004] | -0.015 [-0.026, -0.006] |
| 2021-23 | 748 | -0.004 [-0.006, -0.001] | -0.013 [-0.024, -0.005] | -0.006 [-0.009, -0.003] |
| 2024 | 250 | -0.002 [-0.004, -0.000] | -0.002 [-0.003, -0.001] | 0.000 [-0.001, 0.002] |
| 2025-26 | 249 | -0.001 [-0.038, 0.043] | 0.020 [-0.023, 0.078] | 0.025 [-0.020, 0.081] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.008 [-0.032, 0.013] | 0.021 [-0.008, 0.055] | 0.012 [-0.019, 0.046] |
| ordinary | 1603 | -0.006 [-0.015, 0.001] | -0.003 [-0.013, 0.007] | 0.001 [-0.010, 0.012] |
| quarter_end | 31 | -0.021 [-0.090, 0.048] | -0.008 [-0.106, 0.091] | -0.009 [-0.085, 0.075] |
| tax_date | 89 | -0.023 [-0.044, -0.006] | -0.009 [-0.029, 0.013] | -0.011 [-0.044, 0.022] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.003 [-0.005, -0.001] | -0.010 [-0.017, -0.004] | -0.004 [-0.007, -0.002] |
| 1 | 324 | -0.009 [-0.018, -0.003] | -0.014 [-0.022, -0.009] | -0.014 [-0.021, -0.009] |
| 2 | 41 | 0.089 [–] | 0.150 [–] | 0.104 [–] |
| 3 | 473 | -0.025 [-0.052, -0.002] | 0.013 [-0.016, 0.042] | 0.013 [-0.021, 0.047] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.265, 0.033] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.083] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.455, 0.100] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.320, 0.042] |

## projected_rolling against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.017 [0.010, 0.026] |
| 2 | 0.014 [0.007, 0.023] |
| 3 | 0.010 [0.002, 0.019] |
| 4 | 0.012 [0.005, 0.020] |
| 5 | 0.008 [-0.001, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.027 [0.005, 0.050] | 0.016 [-0.005, 0.039] | -0.003 [-0.033, 0.025] |
| 2020 | 251 | 0.030 [0.022, 0.038] | 0.031 [0.024, 0.037] | 0.021 [0.011, 0.029] |
| 2021-23 | 748 | 0.010 [0.007, 0.013] | 0.001 [-0.010, 0.008] | 0.008 [0.004, 0.011] |
| 2024 | 250 | 0.002 [-0.002, 0.005] | 0.002 [-0.001, 0.004] | 0.002 [-0.002, 0.004] |
| 2025-26 | 249 | 0.028 [-0.013, 0.081] | 0.018 [-0.021, 0.071] | 0.019 [-0.021, 0.069] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.040 [0.011, 0.074] | 0.032 [0.009, 0.060] | 0.021 [-0.008, 0.051] |
| ordinary | 1603 | 0.012 [0.006, 0.020] | 0.006 [-0.002, 0.014] | 0.005 [-0.003, 0.014] |
| quarter_end | 31 | 0.110 [0.056, 0.161] | 0.080 [0.016, 0.138] | 0.081 [0.024, 0.136] |
| tax_date | 89 | 0.044 [0.020, 0.069] | 0.029 [0.003, 0.059] | 0.016 [-0.012, 0.046] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.006 [0.004, 0.009] | -0.000 [-0.008, 0.006] | 0.005 [0.002, 0.007] |
| 1 | 324 | 0.020 [0.010, 0.028] | 0.015 [0.003, 0.024] | 0.014 [0.003, 0.022] |
| 2 | 41 | 0.130 [-0.092, 0.341] | 0.132 [-0.111, 0.349] | 0.077 [–] |
| 3 | 473 | 0.031 [0.012, 0.052] | 0.019 [0.001, 0.038] | 0.006 [-0.016, 0.029] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.094, 0.259] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.267, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.214] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.091] |

## projected_rolling against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.004, 0.008] |
| 2 | 0.004 [-0.002, 0.012] |
| 3 | 0.004 [-0.004, 0.012] |
| 4 | 0.003 [-0.003, 0.010] |
| 5 | 0.001 [-0.006, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.010 [-0.016, 0.034] | 0.016 [-0.010, 0.041] | -0.000 [-0.032, 0.031] |
| 2020 | 251 | 0.007 [0.003, 0.011] | 0.019 [0.013, 0.024] | 0.003 [-0.009, 0.013] |
| 2021-23 | 748 | -0.003 [-0.006, -0.000] | -0.009 [-0.020, -0.001] | -0.004 [-0.008, -0.001] |
| 2024 | 250 | 0.003 [0.000, 0.006] | 0.002 [0.001, 0.003] | 0.002 [0.000, 0.004] |
| 2025-26 | 249 | 0.002 [-0.018, 0.024] | 0.012 [-0.019, 0.048] | 0.011 [-0.015, 0.043] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.018 [0.000, 0.039] | 0.023 [0.002, 0.049] | 0.011 [-0.014, 0.036] |
| ordinary | 1603 | -0.000 [-0.006, 0.005] | 0.001 [-0.006, 0.008] | -0.001 [-0.008, 0.006] |
| quarter_end | 31 | 0.049 [-0.046, 0.155] | 0.045 [-0.062, 0.155] | 0.055 [-0.054, 0.164] |
| tax_date | 89 | 0.008 [-0.010, 0.027] | 0.002 [-0.025, 0.040] | -0.010 [-0.047, 0.032] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.002 [-0.004, 0.000] | -0.007 [-0.015, -0.001] | -0.003 [-0.005, -0.000] |
| 1 | 324 | -0.001 [-0.007, 0.004] | 0.005 [-0.004, 0.012] | 0.000 [-0.008, 0.006] |
| 2 | 41 | 0.040 [-0.075, 0.148] | 0.086 [–] | 0.001 [–] |
| 3 | 473 | 0.011 [-0.010, 0.030] | 0.018 [-0.002, 0.039] | 0.008 [-0.013, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.143, 0.296] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.305, 0.176] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.385, 0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | -0.048 [-0.280, 0.176] |

## projected_rolling against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.005, 0.014] |
| 2 | 0.003 [-0.006, 0.012] |
| 3 | 0.001 [-0.009, 0.010] |
| 4 | 0.000 [-0.008, 0.009] |
| 5 | -0.003 [-0.012, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.025 [-0.008, 0.061] | 0.025 [-0.001, 0.053] | -0.005 [-0.039, 0.030] |
| 2020 | 251 | -0.008 [-0.015, -0.002] | -0.002 [-0.009, 0.006] | -0.010 [-0.024, 0.002] |
| 2021-23 | 748 | -0.004 [-0.006, -0.001] | -0.013 [-0.023, -0.006] | -0.006 [-0.009, -0.003] |
| 2024 | 250 | 0.001 [-0.001, 0.005] | -0.002 [-0.006, 0.000] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | 0.010 [-0.028, 0.060] | 0.011 [-0.032, 0.065] | 0.008 [-0.031, 0.062] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.014 [-0.035, 0.008] | 0.001 [-0.021, 0.024] | -0.023 [-0.051, 0.004] |
| ordinary | 1603 | 0.008 [-0.001, 0.018] | 0.002 [-0.007, 0.012] | 0.002 [-0.007, 0.013] |
| quarter_end | 31 | -0.015 [-0.089, 0.061] | -0.029 [-0.122, 0.070] | -0.013 [-0.087, 0.067] |
| tax_date | 89 | -0.025 [-0.062, 0.014] | -0.023 [-0.058, 0.008] | -0.065 [-0.106, -0.030] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.002 [-0.004, -0.000] | -0.009 [-0.017, -0.004] | -0.004 [-0.007, -0.002] |
| 1 | 324 | -0.009 [-0.014, -0.005] | -0.013 [-0.020, -0.007] | -0.014 [-0.023, -0.008] |
| 2 | 41 | 0.124 [–] | 0.174 [–] | 0.067 [–] |
| 3 | 473 | 0.016 [-0.011, 0.046] | 0.016 [-0.006, 0.040] | -0.001 [-0.027, 0.027] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.167, 0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.231, 0.200] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.250, 0.400] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.048 [-0.250, 0.136] |

## projected_rolling against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.004] |
| 2 | -0.002 [-0.010, 0.006] |
| 3 | -0.004 [-0.012, 0.005] |
| 4 | -0.006 [-0.012, 0.001] |
| 5 | -0.009 [-0.016, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.015 [-0.049, 0.017] | 0.001 [-0.027, 0.029] | -0.033 [-0.064, -0.003] |
| 2020 | 251 | -0.001 [-0.008, 0.009] | -0.001 [-0.008, 0.006] | -0.010 [-0.024, 0.002] |
| 2021-23 | 748 | -0.003 [-0.006, -0.001] | -0.013 [-0.023, -0.005] | -0.006 [-0.009, -0.003] |
| 2024 | 250 | 0.004 [0.000, 0.009] | 0.000 [-0.003, 0.004] | 0.003 [0.001, 0.006] |
| 2025-26 | 249 | -0.001 [-0.028, 0.030] | 0.010 [-0.022, 0.048] | 0.006 [-0.020, 0.041] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.020 [-0.041, 0.001] | 0.001 [-0.021, 0.026] | -0.025 [-0.051, 0.002] |
| ordinary | 1603 | -0.001 [-0.009, 0.006] | -0.002 [-0.011, 0.005] | -0.004 [-0.012, 0.004] |
| quarter_end | 31 | -0.015 [-0.090, 0.061] | -0.029 [-0.124, 0.068] | -0.013 [-0.088, 0.072] |
| tax_date | 89 | -0.025 [-0.061, 0.015] | -0.023 [-0.057, 0.010] | -0.065 [-0.105, -0.029] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.004, 0.001] | -0.008 [-0.016, -0.002] | -0.003 [-0.006, -0.000] |
| 1 | 324 | -0.008 [-0.012, -0.005] | -0.011 [-0.018, -0.007] | -0.013 [-0.021, -0.007] |
| 2 | 41 | 0.056 [–] | 0.126 [–] | -0.008 [–] |
| 3 | 473 | -0.013 [-0.040, 0.013] | -0.000 [-0.023, 0.023] | -0.020 [-0.043, 0.004] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.308, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.357, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.533, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.238 [-0.400, -0.091] |

## projected_rolling against projected_hinge_fixed

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.008, 0.010] |
| 2 | 0.003 [-0.006, 0.013] |
| 3 | 0.002 [-0.009, 0.014] |
| 4 | 0.004 [-0.006, 0.015] |
| 5 | 0.008 [-0.003, 0.019] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.009 [-0.043, 0.023] | 0.005 [-0.035, 0.041] | 0.025 [-0.017, 0.067] |
| 2020 | 251 | 0.010 [-0.002, 0.024] | 0.021 [0.002, 0.043] | 0.013 [-0.001, 0.029] |
| 2021-23 | 748 | -0.003 [-0.006, -0.001] | -0.013 [-0.023, -0.005] | -0.006 [-0.009, -0.003] |
| 2024 | 250 | 0.000 [-0.002, 0.003] | 0.000 [-0.001, 0.002] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.021 [-0.016, 0.070] | 0.025 [-0.018, 0.085] | 0.024 [-0.019, 0.078] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.008 [-0.016, 0.036] | 0.012 [-0.016, 0.045] | 0.016 [-0.011, 0.048] |
| ordinary | 1603 | 0.000 [-0.008, 0.009] | 0.001 [-0.010, 0.012] | 0.008 [-0.003, 0.019] |
| quarter_end | 31 | 0.037 [-0.027, 0.103] | 0.029 [-0.049, 0.109] | 0.006 [-0.056, 0.076] |
| tax_date | 89 | -0.012 [-0.045, 0.021] | -0.004 [-0.041, 0.033] | -0.010 [-0.049, 0.026] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.003 [-0.005, -0.001] | -0.009 [-0.017, -0.003] | -0.004 [-0.007, -0.002] |
| 1 | 324 | -0.010 [-0.016, -0.005] | -0.013 [-0.020, -0.008] | -0.013 [-0.020, -0.008] |
| 2 | 41 | 0.123 [-0.098, 0.324] | 0.183 [–] | 0.199 [–] |
| 3 | 473 | 0.006 [-0.023, 0.033] | 0.021 [-0.014, 0.053] | 0.031 [-0.006, 0.066] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.067, 0.300] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.263, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.154, 0.333] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.176, 0.167] |

## projected_rolling against projected_reserves

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.008, 0.009] |
| 2 | 0.002 [-0.007, 0.012] |
| 3 | 0.001 [-0.009, 0.012] |
| 4 | 0.002 [-0.007, 0.012] |
| 5 | 0.001 [-0.009, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.009 [-0.039, 0.022] | 0.007 [-0.029, 0.043] | -0.001 [-0.041, 0.037] |
| 2020 | 251 | 0.009 [-0.003, 0.023] | 0.020 [0.001, 0.042] | 0.011 [-0.003, 0.028] |
| 2021-23 | 748 | -0.004 [-0.006, -0.001] | -0.013 [-0.023, -0.006] | -0.006 [-0.010, -0.003] |
| 2024 | 250 | 0.000 [-0.002, 0.003] | 0.000 [-0.001, 0.003] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.014 [-0.021, 0.058] | 0.017 [-0.026, 0.069] | 0.016 [-0.024, 0.069] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.007 [-0.016, 0.033] | 0.012 [-0.014, 0.041] | 0.007 [-0.019, 0.037] |
| ordinary | 1603 | -0.000 [-0.008, 0.008] | 0.000 [-0.010, 0.011] | 0.002 [-0.008, 0.012] |
| quarter_end | 31 | 0.024 [-0.027, 0.087] | 0.009 [-0.060, 0.077] | -0.010 [-0.061, 0.038] |
| tax_date | 89 | -0.016 [-0.052, 0.017] | -0.008 [-0.046, 0.026] | -0.014 [-0.051, 0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.003 [-0.005, -0.001] | -0.009 [-0.017, -0.004] | -0.004 [-0.007, -0.002] |
| 1 | 324 | -0.011 [-0.017, -0.006] | -0.014 [-0.022, -0.009] | -0.014 [-0.022, -0.009] |
| 2 | 41 | 0.093 [–] | 0.173 [–] | 0.111 [–] |
| 3 | 473 | 0.005 [-0.021, 0.032] | 0.019 [-0.012, 0.049] | 0.014 [-0.017, 0.044] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.069, 0.312] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.333] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 1.000 [–] |
| 2 | 2 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.182, 0.176] |

## projected_fitted against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.008, 0.014] |
| 2 | 0.009 [-0.002, 0.021] |
| 3 | 0.003 [-0.009, 0.016] |
| 4 | 0.003 [-0.009, 0.017] |
| 5 | -0.003 [-0.017, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.031 [-0.019, 0.087] | 0.054 [0.001, 0.110] | 0.014 [-0.053, 0.085] |
| 2020 | 251 | -0.022 [-0.032, -0.013] | -0.044 [-0.074, -0.021] | -0.052 [-0.092, -0.023] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.003, -0.001] |
| 2024 | 250 | -0.002 [-0.006, 0.001] | -0.002 [-0.007, 0.000] | 0.000 [-0.001, 0.001] |
| 2025-26 | 249 | -0.004 [-0.023, 0.010] | -0.004 [-0.017, 0.006] | 0.016 [0.005, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.039, -0.003] | -0.008 [-0.031, 0.014] | -0.010 [-0.038, 0.015] |
| ordinary | 1603 | 0.007 [-0.004, 0.019] | 0.007 [-0.005, 0.020] | -0.001 [-0.016, 0.014] |
| quarter_end | 31 | -0.049 [-0.126, 0.030] | -0.033 [-0.124, 0.056] | 0.005 [-0.059, 0.070] |
| tax_date | 89 | -0.021 [-0.066, 0.026] | -0.034 [-0.073, -0.001] | -0.014 [-0.071, 0.039] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.001 [-0.002, 0.000] | -0.000 [-0.001, -0.000] |
| 1 | 324 | -0.010 [-0.014, -0.005] | -0.022 [-0.032, -0.013] | -0.021 [-0.035, -0.012] |
| 2 | 41 | 0.030 [–] | -0.017 [-0.119, 0.020] | -0.072 [–] |
| 3 | 473 | 0.013 [-0.028, 0.059] | 0.030 [-0.015, 0.077] | 0.011 [-0.041, 0.068] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.214, 0.158] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [-0.071, 0.333] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [-0.222, 0.429] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.000 [-0.214, 0.222] |

## projected_fitted against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.009 [-0.016, -0.003] |
| 2 | -0.003 [-0.010, 0.004] |
| 3 | -0.004 [-0.013, 0.006] |
| 4 | -0.002 [-0.011, 0.008] |
| 5 | -0.009 [-0.020, 0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.021 [-0.051, 0.007] | 0.016 [-0.021, 0.057] | -0.010 [-0.066, 0.045] |
| 2020 | 251 | -0.015 [-0.024, -0.007] | -0.045 [-0.074, -0.023] | -0.051 [-0.089, -0.023] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.003, -0.001] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | -0.002 [-0.005, -0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.018 [-0.032, -0.005] | 0.000 [-0.003, 0.003] | 0.007 [0.002, 0.014] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.034, 0.004] | 0.008 [-0.011, 0.031] | -0.005 [-0.035, 0.022] |
| ordinary | 1603 | -0.007 [-0.012, -0.002] | -0.004 [-0.012, 0.004] | -0.008 [-0.018, 0.002] |
| quarter_end | 31 | -0.064 [-0.150, 0.018] | -0.042 [-0.146, 0.067] | -0.021 [-0.098, 0.051] |
| tax_date | 89 | -0.020 [-0.058, 0.019] | -0.020 [-0.069, 0.027] | -0.014 [-0.075, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.000] |
| 1 | 324 | -0.009 [-0.012, -0.005] | -0.022 [-0.032, -0.014] | -0.021 [-0.034, -0.012] |
| 2 | 41 | -0.018 [–] | -0.030 [–] | -0.086 [–] |
| 3 | 473 | -0.027 [-0.052, -0.003] | 0.003 [-0.028, 0.038] | -0.011 [-0.052, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.385, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.136, 0.150] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.462, 0.100] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.278, 0.062] |

## projected_fitted against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.016 [0.008, 0.025] |
| 2 | 0.011 [0.003, 0.020] |
| 3 | 0.007 [-0.001, 0.016] |
| 4 | 0.007 [-0.001, 0.016] |
| 5 | -0.001 [-0.013, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.033 [-0.007, 0.076] | 0.017 [-0.022, 0.060] | -0.023 [-0.080, 0.034] |
| 2020 | 251 | 0.018 [0.009, 0.025] | -0.006 [-0.033, 0.013] | -0.016 [-0.049, 0.011] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.011 [0.010, 0.012] | 0.012 [0.011, 0.014] |
| 2024 | 250 | 0.002 [-0.003, 0.005] | 0.001 [-0.003, 0.005] | 0.001 [-0.003, 0.005] |
| 2025-26 | 249 | 0.011 [0.004, 0.020] | -0.002 [-0.009, 0.003] | 0.002 [-0.002, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.033 [0.013, 0.055] | 0.020 [0.002, 0.040] | 0.003 [-0.024, 0.028] |
| ordinary | 1603 | 0.012 [0.003, 0.020] | 0.004 [-0.004, 0.013] | -0.004 [-0.016, 0.008] |
| quarter_end | 31 | 0.066 [0.028, 0.102] | 0.046 [0.008, 0.076] | 0.068 [0.021, 0.119] |
| tax_date | 89 | 0.047 [0.014, 0.083] | 0.018 [-0.021, 0.055] | 0.012 [-0.040, 0.058] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.008 [0.007, 0.010] | 0.009 [0.007, 0.010] |
| 1 | 324 | 0.020 [0.016, 0.023] | 0.007 [-0.001, 0.014] | 0.006 [-0.007, 0.015] |
| 2 | 41 | 0.023 [-0.005, 0.060] | -0.048 [–] | -0.113 [–] |
| 3 | 473 | 0.028 [-0.004, 0.063] | 0.008 [-0.023, 0.044] | -0.019 [-0.061, 0.025] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.094, 0.087] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.143, 0.143] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.214, 0.200] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.111, 0.111] |

## projected_fitted against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.006, 0.009] |
| 2 | 0.001 [-0.007, 0.010] |
| 3 | 0.001 [-0.007, 0.010] |
| 4 | -0.001 [-0.010, 0.008] |
| 5 | -0.009 [-0.021, 0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.016 [-0.015, 0.049] | 0.017 [-0.020, 0.058] | -0.021 [-0.075, 0.032] |
| 2020 | 251 | -0.006 [-0.013, 0.001] | -0.018 [-0.049, 0.004] | -0.033 [-0.074, -0.004] |
| 2021-23 | 748 | 0.000 [0.000, 0.001] | 0.001 [-0.000, 0.002] | 0.001 [-0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.001, 0.005] | 0.001 [-0.000, 0.003] | 0.002 [0.000, 0.003] |
| 2025-26 | 249 | -0.014 [-0.039, 0.005] | -0.009 [-0.029, 0.007] | -0.006 [-0.029, 0.012] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.013, 0.040] | 0.010 [-0.011, 0.036] | -0.006 [-0.037, 0.021] |
| ordinary | 1603 | -0.001 [-0.007, 0.005] | -0.000 [-0.008, 0.008] | -0.010 [-0.021, 0.001] |
| quarter_end | 31 | 0.006 [-0.099, 0.115] | 0.011 [-0.087, 0.116] | 0.043 [-0.052, 0.140] |
| tax_date | 89 | 0.012 [-0.025, 0.056] | -0.009 [-0.063, 0.046] | -0.014 [-0.083, 0.054] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.001, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | -0.001 [-0.004, 0.002] | -0.003 [-0.012, 0.004] | -0.007 [-0.020, 0.002] |
| 2 | 41 | -0.067 [-0.164, 0.035] | -0.094 [–] | -0.189 [–] |
| 3 | 473 | 0.008 [-0.017, 0.036] | 0.008 [-0.021, 0.041] | -0.017 [-0.058, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.091, 0.091] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.083 [-0.222, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.118, 0.111] |

## projected_fitted against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.008, 0.013] |
| 2 | -0.000 [-0.010, 0.010] |
| 3 | -0.003 [-0.013, 0.008] |
| 4 | -0.005 [-0.016, 0.007] |
| 5 | -0.013 [-0.027, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.031 [-0.017, 0.084] | 0.027 [-0.019, 0.075] | -0.025 [-0.089, 0.036] |
| 2020 | 251 | -0.020 [-0.031, -0.012] | -0.039 [-0.065, -0.019] | -0.046 [-0.085, -0.018] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.002, -0.001] |
| 2024 | 250 | 0.000 [-0.000, 0.001] | -0.002 [-0.008, 0.000] | 0.001 [-0.000, 0.001] |
| 2025-26 | 249 | -0.006 [-0.023, 0.007] | -0.010 [-0.027, 0.004] | -0.009 [-0.021, 0.001] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.038, -0.004] | -0.012 [-0.030, 0.005] | -0.040 [-0.070, -0.016] |
| ordinary | 1603 | 0.007 [-0.003, 0.019] | 0.001 [-0.010, 0.012] | -0.007 [-0.021, 0.007] |
| quarter_end | 31 | -0.058 [-0.132, 0.018] | -0.064 [-0.144, 0.013] | -0.026 [-0.077, 0.029] |
| tax_date | 89 | -0.022 [-0.068, 0.023] | -0.034 [-0.068, -0.000] | -0.068 [-0.126, -0.020] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.001 [-0.002, 0.000] | -0.000 [-0.001, 0.000] |
| 1 | 324 | -0.009 [-0.014, -0.004] | -0.020 [-0.029, -0.014] | -0.022 [-0.035, -0.012] |
| 2 | 41 | 0.017 [-0.027, 0.054] | -0.006 [-0.063, 0.017] | -0.123 [–] |
| 3 | 473 | 0.014 [-0.027, 0.058] | 0.006 [-0.033, 0.047] | -0.025 [-0.074, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.280, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [-0.084, 0.333] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [-0.250, 0.400] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.000 [-0.211, 0.217] |

## projected_fitted against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.006 [-0.013, 0.002] |
| 2 | -0.005 [-0.012, 0.001] |
| 3 | -0.007 [-0.014, 0.001] |
| 4 | -0.010 [-0.019, -0.002] |
| 5 | -0.018 [-0.030, -0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.009 [-0.043, 0.025] | 0.003 [-0.029, 0.034] | -0.053 [-0.105, -0.005] |
| 2020 | 251 | -0.013 [-0.022, -0.004] | -0.038 [-0.063, -0.018] | -0.046 [-0.087, -0.018] |
| 2021-23 | 748 | -0.000 [-0.001, 0.000] | -0.002 [-0.004, -0.001] | -0.001 [-0.002, -0.000] |
| 2024 | 250 | 0.003 [0.001, 0.007] | -0.000 [-0.006, 0.004] | 0.003 [0.001, 0.005] |
| 2025-26 | 249 | -0.017 [-0.042, 0.003] | -0.010 [-0.031, 0.008] | -0.011 [-0.036, 0.010] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.026 [-0.044, -0.009] | -0.012 [-0.029, 0.004] | -0.042 [-0.069, -0.019] |
| ordinary | 1603 | -0.002 [-0.009, 0.005] | -0.004 [-0.011, 0.004] | -0.013 [-0.025, -0.002] |
| quarter_end | 31 | -0.058 [-0.136, 0.015] | -0.064 [-0.144, 0.010] | -0.026 [-0.079, 0.030] |
| tax_date | 89 | -0.022 [-0.065, 0.023] | -0.034 [-0.067, -0.004] | -0.068 [-0.126, -0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [-0.001, 0.002] | 0.001 [0.000, 0.002] |
| 1 | 324 | -0.008 [-0.013, -0.002] | -0.019 [-0.028, -0.012] | -0.020 [-0.034, -0.011] |
| 2 | 41 | -0.050 [–] | -0.054 [–] | -0.198 [–] |
| 3 | 473 | -0.015 [-0.044, 0.014] | -0.011 [-0.039, 0.017] | -0.044 [-0.083, -0.007] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.387, -0.083] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.167, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.462, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.190 [-0.353, -0.048] |

## projected_fitted against projected_hinge_fixed

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.002, 0.001] |
| 2 | 0.000 [-0.002, 0.003] |
| 3 | -0.001 [-0.005, 0.002] |
| 4 | -0.000 [-0.005, 0.004] |
| 5 | -0.002 [-0.006, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.006, 0.001] | 0.007 [-0.001, 0.016] | 0.005 [-0.002, 0.013] |
| 2020 | 251 | -0.003 [-0.012, 0.008] | -0.016 [-0.033, 0.000] | -0.024 [-0.045, -0.006] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.002, -0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.005 [0.002, 0.008] | 0.005 [0.002, 0.008] | 0.006 [0.002, 0.011] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.002 [-0.002, 0.006] | -0.001 [-0.006, 0.004] | -0.001 [-0.007, 0.004] |
| ordinary | 1603 | -0.000 [-0.001, 0.001] | -0.000 [-0.003, 0.002] | -0.001 [-0.005, 0.002] |
| quarter_end | 31 | -0.007 [-0.034, 0.020] | -0.005 [-0.033, 0.020] | -0.007 [-0.033, 0.020] |
| tax_date | 89 | -0.008 [-0.017, -0.001] | -0.015 [-0.036, 0.004] | -0.014 [-0.026, -0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, 0.000] | -0.001 [-0.001, -0.000] | -0.000 [-0.001, -0.000] |
| 1 | 324 | -0.010 [-0.013, -0.006] | -0.021 [-0.030, -0.014] | -0.020 [-0.033, -0.011] |
| 2 | 41 | 0.016 [–] | 0.003 [–] | 0.008 [–] |
| 3 | 473 | 0.004 [-0.001, 0.009] | 0.010 [0.002, 0.019] | 0.006 [-0.000, 0.013] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [0.000, 0.115] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.136] |

## projected_fitted against projected_reserves

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.003, 0.000] |
| 2 | -0.001 [-0.004, 0.002] |
| 3 | -0.002 [-0.005, 0.001] |
| 4 | -0.002 [-0.006, 0.002] |
| 5 | -0.008 [-0.016, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.007, 0.001] | 0.009 [0.000, 0.019] | -0.021 [-0.055, 0.004] |
| 2020 | 251 | -0.004 [-0.013, 0.007] | -0.017 [-0.034, -0.001] | -0.025 [-0.047, -0.006] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.003, -0.001] |
| 2024 | 250 | -0.000 [-0.001, -0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2025-26 | 249 | -0.002 [-0.004, -0.001] | -0.003 [-0.006, -0.001] | -0.001 [-0.002, -0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.000 [-0.003, 0.004] | -0.000 [-0.007, 0.007] | -0.011 [-0.024, 0.000] |
| ordinary | 1603 | -0.001 [-0.002, 0.001] | -0.001 [-0.003, 0.002] | -0.007 [-0.015, -0.001] |
| quarter_end | 31 | -0.019 [-0.043, 0.007] | -0.026 [-0.051, -0.003] | -0.022 [-0.047, -0.000] |
| tax_date | 89 | -0.012 [-0.021, -0.004] | -0.019 [-0.041, -0.001] | -0.018 [-0.029, -0.007] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, -0.000] | -0.001 [-0.001, -0.000] | -0.000 [-0.001, -0.000] |
| 1 | 324 | -0.011 [-0.014, -0.007] | -0.022 [-0.031, -0.015] | -0.022 [-0.034, -0.012] |
| 2 | 41 | -0.013 [–] | -0.008 [–] | -0.080 [-0.314, -0.006] |
| 3 | 473 | 0.003 [-0.002, 0.008] | 0.009 [0.001, 0.018] | -0.010 [-0.033, 0.007] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [0.000, 0.111] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [0.000, 0.231] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.143] |

## risk_gbm+combined_hinge_fixed against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.004 [-0.001, 0.011] |
| 3 | 0.001 [-0.006, 0.007] |
| 4 | -0.002 [-0.008, 0.003] |
| 5 | 0.003 [-0.004, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.013] | 0.005 [-0.030, 0.037] | -0.001 [-0.034, 0.027] |
| 2020 | 251 | 0.003 [0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.003, 0.004] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.012 [-0.029, 0.002] | 0.003 [-0.003, 0.008] | 0.022 [0.003, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.048, -0.002] | -0.007 [-0.022, 0.007] | 0.019 [0.007, 0.031] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | 0.003 [-0.005, 0.009] | -0.000 [-0.008, 0.006] |
| quarter_end | 31 | -0.011 [-0.069, 0.045] | -0.002 [-0.059, 0.061] | 0.037 [0.000, 0.079] |
| tax_date | 89 | -0.039 [-0.075, -0.011] | -0.015 [-0.058, 0.022] | 0.018 [-0.034, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.026 [–] | -0.001 [–] | 0.043 [0.003, 0.089] |
| 3 | 473 | -0.007 [-0.021, 0.007] | 0.004 [-0.024, 0.030] | 0.007 [-0.022, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.231, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.286, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.236, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.235, 0.000] |

## risk_gbm+combined_hinge_fixed against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.006] |
| 2 | -0.008 [-0.016, 0.001] |
| 3 | -0.006 [-0.017, 0.003] |
| 4 | -0.007 [-0.017, 0.002] |
| 5 | -0.003 [-0.012, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.056 [-0.096, -0.022] | -0.033 [-0.082, 0.012] | -0.025 [-0.069, 0.015] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.010, 0.000] | -0.003 [-0.006, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.025 [-0.043, -0.009] | 0.007 [-0.003, 0.018] | 0.013 [0.000, 0.029] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.007, 0.026] | 0.023 [0.005, 0.045] |
| ordinary | 1603 | -0.012 [-0.022, -0.003] | -0.008 [-0.019, 0.001] | -0.007 [-0.017, 0.002] |
| quarter_end | 31 | -0.026 [-0.096, 0.027] | -0.011 [-0.078, 0.051] | 0.010 [-0.035, 0.058] |
| tax_date | 89 | -0.038 [-0.076, -0.009] | 0.000 [-0.035, 0.030] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.074 [–] | -0.014 [–] | 0.029 [–] |
| 3 | 473 | -0.048 [-0.081, -0.019] | -0.022 [-0.062, 0.014] | -0.015 [-0.051, 0.018] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.435, -0.107] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.417, -0.067] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.589, -0.100] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.353, -0.050] |

## risk_gbm+combined_hinge_fixed against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.006, 0.016] |
| 2 | 0.007 [-0.001, 0.014] |
| 3 | 0.005 [-0.003, 0.012] |
| 4 | 0.002 [-0.005, 0.010] |
| 5 | 0.004 [-0.004, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.024, 0.019] | -0.032 [-0.065, 0.000] | -0.038 [-0.072, -0.007] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.028, 0.047] | 0.037 [0.026, 0.048] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.004 [-0.005, 0.014] | 0.004 [-0.008, 0.017] | 0.007 [-0.003, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.043] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.046] |
| ordinary | 1603 | 0.007 [0.002, 0.011] | 0.000 [-0.008, 0.007] | -0.003 [-0.011, 0.005] |
| quarter_end | 31 | 0.105 [0.012, 0.193] | 0.077 [-0.018, 0.167] | 0.100 [0.002, 0.200] |
| tax_date | 89 | 0.029 [-0.001, 0.057] | 0.038 [0.008, 0.065] | 0.044 [0.012, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.023, 0.036] | 0.028 [0.022, 0.034] |
| 2 | 41 | -0.034 [–] | -0.032 [-0.053, 0.012] | 0.002 [–] |
| 3 | 473 | 0.008 [-0.011, 0.026] | -0.017 [-0.046, 0.010] | -0.023 [-0.052, 0.004] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.267, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.462, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.500, 0.182] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.322, 0.158] |

## risk_gbm+combined_hinge_fixed against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.003] |
| 2 | -0.003 [-0.012, 0.004] |
| 3 | -0.001 [-0.010, 0.006] |
| 4 | -0.006 [-0.015, 0.002] |
| 5 | -0.003 [-0.012, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.052, 0.009] | -0.032 [-0.069, 0.001] | -0.035 [-0.070, -0.002] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.010, 0.026] |
| 2021-23 | 748 | 0.001 [0.001, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.005] | 0.001 [-0.001, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.022 [-0.055, 0.003] | -0.002 [-0.026, 0.020] | -0.000 [-0.026, 0.022] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.008 [-0.017, 0.033] | 0.011 [-0.002, 0.023] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.006 [-0.014, 0.002] | -0.004 [-0.014, 0.004] | -0.009 [-0.019, 0.000] |
| quarter_end | 31 | 0.045 [-0.010, 0.109] | 0.042 [-0.010, 0.107] | 0.074 [0.018, 0.137] |
| tax_date | 89 | -0.006 [-0.036, 0.017] | 0.011 [-0.007, 0.029] | 0.018 [-0.003, 0.041] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.123 [–] | -0.078 [–] | -0.074 [–] |
| 3 | 473 | -0.012 [-0.039, 0.011] | -0.017 [-0.049, 0.010] | -0.021 [-0.052, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.240, 0.104] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.364, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.526, 0.051] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.296, 0.125] |

## risk_gbm+combined_hinge_fixed against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | -0.005 [-0.011, 0.000] |
| 3 | -0.005 [-0.011, 0.001] |
| 4 | -0.009 [-0.016, -0.004] |
| 5 | -0.008 [-0.014, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.012] | -0.022 [-0.052, 0.005] | -0.040 [-0.069, -0.016] |
| 2020 | 251 | 0.004 [0.001, 0.009] | 0.005 [-0.004, 0.014] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.010, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.013 [-0.031, -0.000] | -0.003 [-0.011, 0.003] | -0.003 [-0.010, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.002] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.002 [-0.001, 0.007] | -0.003 [-0.010, 0.003] | -0.006 [-0.013, -0.000] |
| quarter_end | 31 | -0.020 [-0.076, 0.030] | -0.032 [-0.096, 0.024] | 0.006 [-0.026, 0.047] |
| tax_date | 89 | -0.040 [-0.075, -0.008] | -0.014 [-0.055, 0.022] | -0.036 [-0.082, 0.002] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.040 [–] | 0.010 [-0.007, 0.056] | -0.008 [-0.021, 0.002] |
| 3 | 473 | -0.006 [-0.021, 0.008] | -0.019 [-0.044, 0.003] | -0.030 [-0.053, -0.009] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.296, -0.036] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.235, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.222, 0.000] |

## risk_gbm+combined_hinge_fixed against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.019, -0.003] |
| 3 | -0.009 [-0.017, -0.001] |
| 4 | -0.015 [-0.025, -0.007] |
| 5 | -0.013 [-0.023, -0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.076, -0.018] | -0.046 [-0.081, -0.014] | -0.068 [-0.106, -0.033] |
| 2020 | 251 | 0.011 [0.002, 0.025] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.016] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.025 [-0.054, 0.000] | -0.004 [-0.022, 0.012] | -0.006 [-0.030, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.055, -0.006] | -0.012 [-0.030, 0.007] | -0.014 [-0.026, -0.002] |
| ordinary | 1603 | -0.006 [-0.015, 0.000] | -0.008 [-0.016, 0.000] | -0.012 [-0.022, -0.003] |
| quarter_end | 31 | -0.020 [-0.076, 0.033] | -0.032 [-0.091, 0.025] | 0.006 [-0.027, 0.044] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.057, 0.023] | -0.036 [-0.081, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.002, 0.005] |
| 2 | 41 | -0.107 [-0.183, -0.016] | -0.038 [–] | -0.083 [–] |
| 3 | 473 | -0.036 [-0.064, -0.012] | -0.036 [-0.064, -0.010] | -0.048 [-0.080, -0.016] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.464, -0.154] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.105] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.417 [-0.667, -0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.455, -0.125] |

## risk_gbm+combined_hinge_fixed against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.000, -0.000] |
| 2 | -0.000 [-0.000, -0.000] |
| 3 | -0.000 [-0.000, -0.000] |
| 4 | -0.000 [-0.000, 0.000] |
| 5 | 0.000 [-0.000, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.002 [-0.000, 0.006] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2025-26 | 249 | -0.001 [-0.002, -0.000] | -0.001 [-0.002, -0.000] | -0.001 [-0.001, -0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| ordinary | 1603 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.001] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 324 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2 | 41 | -0.004 [–] | -0.004 [–] | -0.003 [-0.005, 0.000] |
| 3 | 473 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.002 [-0.000, 0.004] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [0.000, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [–] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## risk_gbm+combined_rolling against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.006, 0.005] |
| 2 | 0.009 [0.004, 0.015] |
| 3 | 0.008 [0.003, 0.013] |
| 4 | 0.007 [0.002, 0.013] |
| 5 | 0.011 [0.004, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.001 [-0.022, 0.027] | 0.034 [0.014, 0.058] | 0.040 [0.019, 0.062] |
| 2020 | 251 | 0.003 [0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.004 [-0.022, 0.010] | 0.011 [0.000, 0.026] | 0.021 [-0.014, 0.055] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.049, -0.002] | -0.007 [-0.023, 0.007] | 0.019 [0.007, 0.031] |
| ordinary | 1603 | 0.004 [-0.001, 0.011] | 0.010 [0.005, 0.017] | 0.009 [0.003, 0.016] |
| quarter_end | 31 | -0.011 [-0.067, 0.047] | -0.002 [-0.062, 0.063] | 0.037 [0.001, 0.077] |
| tax_date | 89 | -0.039 [-0.075, -0.010] | -0.015 [-0.062, 0.022] | 0.018 [-0.033, 0.080] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, 0.001] | -0.001 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | -0.008 [-0.023, 0.001] |
| 2 | 41 | 0.013 [-0.043, 0.056] | 0.051 [–] | 0.102 [–] |
| 3 | 473 | -0.003 [-0.023, 0.018] | 0.027 [0.011, 0.046] | 0.039 [0.020, 0.060] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.208, 0.048] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.200, 0.100] |

## risk_gbm+combined_rolling against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.012 [-0.021, -0.004] |
| 2 | -0.003 [-0.011, 0.004] |
| 3 | 0.001 [-0.009, 0.009] |
| 4 | 0.002 [-0.007, 0.009] |
| 5 | 0.005 [-0.005, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.052 [-0.092, -0.017] | -0.005 [-0.049, 0.035] | 0.015 [-0.029, 0.055] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.017 [-0.033, -0.004] | 0.015 [0.000, 0.033] | 0.012 [-0.019, 0.041] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.019 [-0.038, -0.000] | 0.009 [-0.007, 0.026] | 0.023 [0.004, 0.046] |
| ordinary | 1603 | -0.010 [-0.019, -0.001] | -0.000 [-0.010, 0.008] | 0.002 [-0.008, 0.011] |
| quarter_end | 31 | -0.026 [-0.095, 0.029] | -0.011 [-0.076, 0.057] | 0.010 [-0.037, 0.059] |
| tax_date | 89 | -0.038 [-0.074, -0.008] | 0.000 [-0.034, 0.028] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.002, -0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | -0.000 [-0.001, 0.000] | -0.008 [-0.023, 0.001] |
| 2 | 41 | -0.035 [–] | 0.038 [-0.039, 0.095] | 0.088 [-0.027, 0.164] |
| 3 | 473 | -0.043 [-0.076, -0.014] | 0.001 [-0.034, 0.032] | 0.017 [-0.018, 0.049] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.421, -0.056] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.400, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.571, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.333, 0.000] |

## risk_gbm+combined_rolling against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.013 [0.008, 0.019] |
| 2 | 0.011 [0.006, 0.017] |
| 3 | 0.012 [0.006, 0.017] |
| 4 | 0.011 [0.006, 0.016] |
| 5 | 0.012 [0.006, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.003 [-0.020, 0.026] | -0.003 [-0.027, 0.021] | 0.002 [-0.017, 0.020] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.027, 0.047] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.013 [0.012, 0.015] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.004, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.011 [0.002, 0.023] | 0.013 [0.002, 0.027] | 0.006 [-0.019, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.029 [0.017, 0.044] | 0.020 [0.012, 0.030] | 0.032 [0.019, 0.046] |
| ordinary | 1603 | 0.009 [0.004, 0.014] | 0.008 [0.003, 0.013] | 0.007 [0.001, 0.012] |
| quarter_end | 31 | 0.105 [0.012, 0.196] | 0.077 [-0.019, 0.173] | 0.100 [0.004, 0.193] |
| tax_date | 89 | 0.029 [-0.002, 0.057] | 0.038 [0.007, 0.066] | 0.044 [0.011, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.010] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.022, 0.036] | 0.020 [0.000, 0.033] |
| 2 | 41 | 0.006 [–] | 0.020 [–] | 0.061 [–] |
| 3 | 473 | 0.013 [-0.007, 0.032] | 0.006 [-0.015, 0.027] | 0.009 [-0.007, 0.025] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.222, 0.148] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.400, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.400, 0.223] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.273, 0.184] |

## risk_gbm+combined_rolling against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.009, 0.005] |
| 2 | 0.001 [-0.006, 0.008] |
| 3 | 0.005 [-0.001, 0.011] |
| 4 | 0.003 [-0.003, 0.007] |
| 5 | 0.004 [-0.001, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.014 [-0.048, 0.016] | -0.003 [-0.030, 0.022] | 0.005 [-0.019, 0.026] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.017, 0.032] | 0.020 [0.010, 0.026] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.004] | 0.001 [-0.002, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.014 [-0.039, 0.005] | 0.007 [-0.008, 0.022] | -0.001 [-0.025, 0.023] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.008 [-0.016, 0.033] | 0.011 [-0.001, 0.024] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.003 [-0.012, 0.004] | 0.004 [-0.003, 0.010] | 0.001 [-0.006, 0.007] |
| quarter_end | 31 | 0.045 [-0.009, 0.107] | 0.042 [-0.011, 0.106] | 0.074 [0.018, 0.140] |
| tax_date | 89 | -0.006 [-0.035, 0.017] | 0.011 [-0.008, 0.030] | 0.018 [-0.002, 0.041] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.001] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.019 [0.015, 0.023] | 0.006 [-0.011, 0.017] |
| 2 | 41 | -0.084 [–] | -0.026 [–] | -0.015 [–] |
| 3 | 473 | -0.008 [-0.035, 0.017] | 0.006 [-0.017, 0.027] | 0.011 [-0.009, 0.029] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.192, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.263, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.438, 0.111] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.238, 0.154] |

## risk_gbm+combined_rolling against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.005, 0.006] |
| 2 | -0.000 [-0.006, 0.005] |
| 3 | 0.002 [-0.002, 0.007] |
| 4 | -0.001 [-0.005, 0.004] |
| 5 | 0.000 [-0.004, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.001 [-0.023, 0.028] | 0.007 [-0.012, 0.029] | 0.000 [-0.016, 0.020] |
| 2020 | 251 | 0.004 [0.000, 0.009] | 0.005 [-0.003, 0.015] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.010, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.006 [-0.023, 0.009] | 0.006 [-0.006, 0.021] | -0.004 [-0.028, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.048, -0.002] | -0.011 [-0.029, 0.008] | -0.012 [-0.022, -0.000] |
| ordinary | 1603 | 0.005 [-0.001, 0.011] | 0.005 [0.000, 0.011] | 0.003 [-0.002, 0.009] |
| quarter_end | 31 | -0.020 [-0.080, 0.032] | -0.032 [-0.093, 0.024] | 0.006 [-0.027, 0.048] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.056, 0.023] | -0.036 [-0.083, 0.006] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.001 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.001 [-0.000, 0.004] | -0.008 [-0.024, 0.003] |
| 2 | 41 | -0.000 [–] | 0.062 [-0.000, 0.117] | 0.051 [–] |
| 3 | 473 | -0.002 [-0.022, 0.020] | 0.004 [-0.012, 0.021] | 0.002 [-0.012, 0.019] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.269, 0.038] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.222, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.208, 0.100] |

## risk_gbm+combined_rolling against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.017, -0.001] |
| 2 | -0.005 [-0.013, 0.001] |
| 3 | -0.002 [-0.009, 0.003] |
| 4 | -0.006 [-0.013, -0.001] |
| 5 | -0.005 [-0.013, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.039 [-0.077, -0.007] | -0.018 [-0.048, 0.008] | -0.028 [-0.060, 0.001] |
| 2020 | 251 | 0.011 [0.001, 0.026] | 0.006 [-0.003, 0.015] | 0.007 [-0.001, 0.016] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.017 [-0.041, 0.003] | 0.005 [-0.005, 0.015] | -0.007 [-0.032, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.056, -0.005] | -0.011 [-0.030, 0.007] | -0.014 [-0.026, -0.002] |
| ordinary | 1603 | -0.004 [-0.013, 0.004] | 0.000 [-0.007, 0.006] | -0.003 [-0.011, 0.004] |
| quarter_end | 31 | -0.020 [-0.076, 0.033] | -0.032 [-0.093, 0.024] | 0.006 [-0.026, 0.049] |
| tax_date | 89 | -0.040 [-0.079, -0.010] | -0.014 [-0.054, 0.023] | -0.036 [-0.080, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [-0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.002 [0.000, 0.006] | 0.003 [0.001, 0.006] | -0.007 [-0.024, 0.004] |
| 2 | 41 | -0.068 [–] | 0.014 [–] | -0.024 [–] |
| 3 | 473 | -0.031 [-0.063, -0.003] | -0.013 [-0.038, 0.008] | -0.016 [-0.043, 0.007] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.412, -0.136] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.412, -0.071] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.556, -0.118] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.391, -0.091] |

## risk_gbm+combined_rolling against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.001, 0.005] |
| 2 | 0.004 [0.001, 0.009] |
| 3 | 0.007 [0.002, 0.013] |
| 4 | 0.009 [0.003, 0.016] |
| 5 | 0.008 [0.002, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.005 [-0.009, 0.020] | 0.029 [0.008, 0.054] | 0.042 [0.013, 0.075] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.006 [-0.000, 0.015] | 0.008 [-0.001, 0.021] | -0.002 [-0.024, 0.021] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.001] | -0.000 [-0.000, 0.000] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | 0.008 [0.002, 0.015] | 0.010 [0.002, 0.019] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, -0.000] | -0.000 [-0.001, -0.000] | 0.000 [-0.000, 0.000] |
| 1 | 324 | -0.000 [-0.000, -0.000] | -0.000 [-0.001, -0.000] | -0.008 [-0.023, -0.000] |
| 2 | 41 | 0.035 [–] | 0.048 [–] | 0.056 [–] |
| 3 | 473 | 0.004 [-0.007, 0.016] | 0.023 [0.006, 0.043] | 0.034 [0.010, 0.060] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [0.000, 0.111] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.174] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [0.000, 0.231] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.143] |

## risk_gbm+combined_fitted against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.004 [-0.002, 0.011] |
| 3 | 0.001 [-0.006, 0.007] |
| 4 | -0.001 [-0.008, 0.004] |
| 5 | 0.003 [-0.004, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.012] | 0.005 [-0.029, 0.036] | -0.001 [-0.031, 0.028] |
| 2020 | 251 | 0.003 [-0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.011 [-0.028, 0.002] | 0.003 [-0.002, 0.008] | 0.022 [0.004, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.049, -0.002] | -0.007 [-0.023, 0.007] | 0.019 [0.008, 0.031] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | 0.003 [-0.005, 0.010] | -0.000 [-0.007, 0.006] |
| quarter_end | 31 | -0.011 [-0.069, 0.046] | -0.002 [-0.064, 0.064] | 0.037 [0.002, 0.076] |
| tax_date | 89 | -0.039 [-0.075, -0.009] | -0.015 [-0.059, 0.021] | 0.018 [-0.035, 0.076] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.023 [–] | 0.002 [–] | 0.045 [–] |
| 3 | 473 | -0.007 [-0.022, 0.007] | 0.004 [-0.022, 0.029] | 0.007 [-0.019, 0.032] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.231, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.278, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_fitted against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.022, -0.006] |
| 2 | -0.007 [-0.016, 0.000] |
| 3 | -0.006 [-0.017, 0.003] |
| 4 | -0.007 [-0.016, 0.002] |
| 5 | -0.003 [-0.013, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.056 [-0.094, -0.022] | -0.033 [-0.081, 0.011] | -0.025 [-0.072, 0.016] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.008] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.042, -0.009] | 0.007 [-0.002, 0.021] | 0.013 [0.000, 0.029] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.008, 0.025] | 0.023 [0.005, 0.045] |
| ordinary | 1603 | -0.012 [-0.021, -0.004] | -0.008 [-0.019, 0.001] | -0.007 [-0.017, 0.002] |
| quarter_end | 31 | -0.026 [-0.096, 0.029] | -0.011 [-0.078, 0.059] | 0.010 [-0.035, 0.059] |
| tax_date | 89 | -0.038 [-0.075, -0.006] | 0.000 [-0.033, 0.028] | 0.017 [-0.012, 0.049] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.072 [–] | -0.012 [–] | 0.031 [–] |
| 3 | 473 | -0.047 [-0.079, -0.019] | -0.022 [-0.062, 0.013] | -0.015 [-0.052, 0.017] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.438, -0.115] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.421, -0.062] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.583, -0.105] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.353, -0.050] |

## risk_gbm+combined_fitted against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.006, 0.016] |
| 2 | 0.007 [-0.001, 0.014] |
| 3 | 0.005 [-0.003, 0.012] |
| 4 | 0.003 [-0.006, 0.010] |
| 5 | 0.004 [-0.004, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.023, 0.019] | -0.032 [-0.065, -0.000] | -0.038 [-0.071, -0.006] |
| 2020 | 251 | 0.042 [0.034, 0.050] | 0.038 [0.027, 0.047] | 0.037 [0.026, 0.048] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.005, 0.015] | 0.005 [-0.006, 0.018] | 0.008 [-0.002, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.044] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.047] |
| ordinary | 1603 | 0.007 [0.002, 0.012] | 0.000 [-0.008, 0.008] | -0.003 [-0.011, 0.005] |
| quarter_end | 31 | 0.105 [0.013, 0.196] | 0.077 [-0.024, 0.174] | 0.100 [0.002, 0.197] |
| tax_date | 89 | 0.029 [-0.003, 0.057] | 0.038 [0.008, 0.067] | 0.044 [0.014, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.022, 0.036] | 0.028 [0.021, 0.034] |
| 2 | 41 | -0.031 [–] | -0.030 [–] | 0.004 [–] |
| 3 | 473 | 0.008 [-0.010, 0.026] | -0.017 [-0.046, 0.010] | -0.023 [-0.052, 0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.267, 0.131] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.467, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.530, 0.200] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.333, 0.167] |

## risk_gbm+combined_fitted against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.003] |
| 2 | -0.003 [-0.012, 0.004] |
| 3 | -0.001 [-0.010, 0.006] |
| 4 | -0.006 [-0.015, 0.002] |
| 5 | -0.003 [-0.011, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.053, 0.009] | -0.032 [-0.068, 0.001] | -0.035 [-0.069, -0.003] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.026] |
| 2021-23 | 748 | 0.001 [0.001, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.004] | 0.001 [-0.001, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.052, 0.002] | -0.002 [-0.026, 0.020] | -0.000 [-0.025, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.015, 0.033] | 0.011 [-0.002, 0.023] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.005 [-0.014, 0.002] | -0.004 [-0.014, 0.004] | -0.009 [-0.018, 0.000] |
| quarter_end | 31 | 0.045 [-0.008, 0.106] | 0.042 [-0.012, 0.104] | 0.074 [0.017, 0.140] |
| tax_date | 89 | -0.006 [-0.036, 0.018] | 0.011 [-0.009, 0.030] | 0.018 [-0.003, 0.041] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.121 [–] | -0.076 [–] | -0.072 [–] |
| 3 | 473 | -0.012 [-0.039, 0.012] | -0.017 [-0.049, 0.011] | -0.021 [-0.051, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.250, 0.105] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.364, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.538, 0.067] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.308, 0.133] |

## risk_gbm+combined_fitted against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | -0.005 [-0.011, 0.001] |
| 3 | -0.005 [-0.011, 0.001] |
| 4 | -0.009 [-0.016, -0.004] |
| 5 | -0.007 [-0.014, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.012] | -0.022 [-0.051, 0.005] | -0.040 [-0.070, -0.016] |
| 2020 | 251 | 0.004 [0.001, 0.009] | 0.005 [-0.004, 0.014] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.010, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.013 [-0.029, 0.000] | -0.002 [-0.010, 0.004] | -0.003 [-0.009, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.046, -0.002] | -0.012 [-0.031, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | -0.003 [-0.009, 0.003] | -0.006 [-0.013, -0.001] |
| quarter_end | 31 | -0.020 [-0.079, 0.035] | -0.032 [-0.094, 0.025] | 0.006 [-0.026, 0.049] |
| tax_date | 89 | -0.040 [-0.076, -0.009] | -0.014 [-0.054, 0.021] | -0.036 [-0.081, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.037 [–] | 0.012 [–] | -0.006 [–] |
| 3 | 473 | -0.006 [-0.021, 0.008] | -0.019 [-0.043, 0.003] | -0.030 [-0.056, -0.010] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.292, -0.036] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.278, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.231, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.222, 0.000] |

## risk_gbm+combined_fitted against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.018, -0.003] |
| 3 | -0.009 [-0.017, -0.002] |
| 4 | -0.015 [-0.025, -0.006] |
| 5 | -0.013 [-0.022, -0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.075, -0.017] | -0.046 [-0.081, -0.015] | -0.068 [-0.105, -0.032] |
| 2020 | 251 | 0.011 [0.002, 0.026] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.015] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.004] |
| 2025-26 | 249 | -0.024 [-0.053, -0.000] | -0.003 [-0.021, 0.012] | -0.005 [-0.028, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.055, -0.007] | -0.012 [-0.030, 0.008] | -0.014 [-0.025, -0.002] |
| ordinary | 1603 | -0.006 [-0.015, 0.001] | -0.008 [-0.016, -0.000] | -0.012 [-0.021, -0.003] |
| quarter_end | 31 | -0.020 [-0.080, 0.033] | -0.032 [-0.092, 0.026] | 0.006 [-0.027, 0.046] |
| tax_date | 89 | -0.040 [-0.078, -0.008] | -0.014 [-0.053, 0.023] | -0.036 [-0.082, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.001, 0.005] |
| 2 | 41 | -0.104 [–] | -0.036 [–] | -0.081 [-0.150, 0.012] |
| 3 | 473 | -0.035 [-0.062, -0.011] | -0.036 [-0.065, -0.010] | -0.048 [-0.079, -0.017] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.458, -0.158] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.105] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.417 [-0.643, -0.188] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.450, -0.133] |

## risk_gbm+combined_fitted against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.000, 0.000] |
| 2 | -0.000 [-0.000, -0.000] |
| 3 | -0.000 [-0.000, -0.000] |
| 4 | -0.000 [-0.000, 0.000] |
| 5 | 0.000 [-0.000, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.002 [-0.000, 0.006] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2025-26 | 249 | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.000, -0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| ordinary | 1603 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.001] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 324 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2 | 41 | -0.001 [–] | -0.001 [-0.002, 0.000] | -0.001 [–] |
| 3 | 473 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | 0.002 [-0.000, 0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [0.000, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [0.000, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

