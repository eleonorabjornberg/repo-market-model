# Kinked elasticity in the structural model (#626)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 10 / 1.42 fail | fail | 10 / 2.42 fail | 0 / 0.33 fail |
| structural_liquidity+h41 | 10 / 1.23 fail | fail | 10 / 2.15 fail | 0 / 0.33 fail |
| structural_kinked_fitted | 10 / 1.31 fail | fail | 10 / 2.69 fail | 0 / 1.44 fail |
| structural_kinked_rolling | 11 / 2.54 fail | fail | 11 / 4.85 fail | 3 / 4.78 fail |
| risk_gbm | 13 / 1.35 pass | pass (h = 1) | 13 / 2.00 pass | 3 / 1.56 fail |
| risk_logistic | 14 / 1.85 pass | pass (h = 1) | 14 / 2.42 fail | 4 / 2.89 fail |
| risk_gbm_base | 14 / 1.50 pass | pass (h = 1) | 14 / 2.04 fail | 4 / 2.00 fail |
| risk_logistic_base | 13 / 1.77 pass | pass (h = 1) | 13 / 2.04 fail | 3 / 2.33 fail |
| risk_quantile_skewt_base | 14 / 1.88 pass | pass (h = 1) | 14 / 2.54 fail | 4 / 3.22 fail |
| ngboost_laplace | 15 / 2.54 fail | fail | 15 / 4.38 fail | 4 / 0.33 fail |
| risk_gbm+settle+h41 | 14 / 1.35 pass | pass (h = 1) | 14 / 2.00 pass | 4 / 1.78 fail |
| risk_gbm+settle+h41+dist_roll | 15 / 1.27 pass | pass (h = 1) | 15 / 1.81 pass | 5 / 1.78 pass |
| calendar_climatology | 10 / 5.00 fail | fail | 10 / 5.38 fail | 0 / 3.78 fail |
| persistence_logistic | 7 / 3.42 fail | fail | 7 / 5.73 fail | 0 / 2.22 fail |

## Tier 1 under weighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 11 / 1.00 fail | fail | 11 / 1.69 fail | 0 / 0.83 fail |
| structural_liquidity+h41 | 10 / 0.91 fail | fail | 10 / 1.48 fail | 0 / 0.22 fail |
| structural_kinked_fitted | 10 / 1.14 fail | fail | 10 / 2.12 fail | 0 / 1.61 fail |
| structural_kinked_rolling | 15 / 3.10 fail | fail | 15 / 4.64 fail | 5 / 5.11 fail |
| risk_gbm | 13 / 0.80 pass | pass (h = 1) | 13 / 1.48 pass | 3 / 1.61 fail |
| risk_logistic | 16 / 1.74 pass | pass (h = 1) | 16 / 2.55 fail | 6 / 4.39 fail |
| risk_gbm_base | 14 / 0.97 pass | pass (h = 1) | 14 / 1.59 pass | 4 / 2.06 fail |
| risk_logistic_base | 15 / 1.65 pass | pass (h = 1) | 15 / 2.18 fail | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass (h = 1) | 15 / 2.14 fail | 5 / 3.81 fail |
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 5 / 0.50 fail |
| risk_gbm+settle+h41 | 14 / 0.88 pass | pass (h = 1) | 14 / 1.44 pass | 4 / 1.72 fail |
| risk_gbm+settle+h41+dist_roll | 15 / 0.73 pass | pass (h = 1) | 15 / 1.17 pass | 5 / 1.28 pass |
| calendar_climatology | 12 / 3.75 fail | fail | 12 / 3.90 fail | 0 / 4.56 fail |
| persistence_logistic | 12 / 3.25 fail | fail | 12 / 4.09 fail | 1 / 2.86 fail |

## Tier 1 under weighted/before_only

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 10 / 1.29 fail | fail | 10 / 2.09 fail | 0 / 0.64 fail |
| structural_liquidity+h41 | 10 / 1.18 fail | fail | 10 / 1.71 fail | 0 / 0.44 fail |
| structural_kinked_fitted | 10 / 1.40 fail | fail | 10 / 2.29 fail | 0 / 1.67 fail |
| structural_kinked_rolling | 15 / 2.93 fail | fail | 15 / 4.67 fail | 5 / 4.83 fail |
| risk_gbm | 13 / 0.95 pass | pass (h = 1) | 13 / 1.64 pass | 3 / 1.78 fail |
| risk_logistic | 16 / 1.90 pass | pass (h = 1) | 16 / 2.70 fail | 6 / 4.31 fail |
| risk_gbm_base | 14 / 1.08 pass | pass (h = 1) | 14 / 1.72 pass | 4 / 2.22 fail |
| risk_logistic_base | 14 / 1.78 pass | pass (h = 1) | 14 / 2.26 fail | 4 / 3.58 fail |
| risk_quantile_skewt_base | 15 / 1.81 pass | pass (h = 1) | 15 / 2.22 fail | 5 / 4.14 fail |
| ngboost_laplace | 16 / 2.23 fail | pass (h = 1) | 16 / 3.30 fail | 5 / 0.58 fail |
| risk_gbm+settle+h41 | 14 / 1.02 pass | pass (h = 1) | 14 / 1.63 pass | 4 / 1.89 fail |
| risk_gbm+settle+h41+dist_roll | 15 / 0.88 pass | pass (h = 1) | 15 / 1.37 pass | 5 / 1.61 pass |
| calendar_climatology | 12 / 4.55 fail | fail | 12 / 4.70 fail | 0 / 4.44 fail |
| persistence_logistic | 10 / 3.23 fail | fail | 10 / 4.50 fail | 1 / 1.75 fail |

## The judge's tables under the unweighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.4 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.00 flat / 1.29 weighted (tier 1 on the flat count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 1.81 flat / 1.17 weighted (tier 1 on the flat count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted (tier 1 on the flat count) | 1.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 2.04 flat / 1.41 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.231 | 2.54 flat / 1.80 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| structural_kinked_fitted | 10 of 26 | 0.385 [0.219, 0.571] | 0.231 | 2.69 flat / 1.41 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| structural_kinked_rolling | 11 of 26 | 0.423 [0.250, 0.607] | 0.269 | 4.85 flat / 2.97 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| structural_liquidity | 10 of 26 | 0.385 [0.217, 0.552] | 0.192 | 2.42 flat / 1.01 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| structural_liquidity+h41 | 10 of 26 | 0.385 [0.208, 0.556] | 0.192 | 2.15 flat / 0.92 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

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

risk_gbm+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.688] | 1.269 [0.865, 1.900] | 0.731 [0.452, 1.188] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 0.846 [0.519, 1.320] | 0.433 [0.250, 0.726] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 1.231 [0.833, 1.864] | 0.692 [0.414, 1.118] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 0.846 [0.512, 1.375] | 0.510 [0.277, 0.898] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 0.731 [0.429, 1.167] | 0.452 [0.235, 0.774] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.367, 0.824] | 1.176 [0.696, 2.000] | 0.529 [0.281, 1.000] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.875] | 3.000 [1.777, 6.400] | 2.389 [1.300, 5.750] |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

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

structural_kinked_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.219, 0.571] | 1.077 [0.552, 1.900] | 0.625 [0.258, 1.240] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.045, 0.267] | 1.192 [0.600, 2.042] | 0.558 [0.214, 1.072] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.069, 0.321] | 1.308 [0.625, 2.238] | 0.519 [0.202, 0.959] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.069, 0.321] | 1.308 [0.500, 2.412] | 0.615 [0.167, 1.266] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.029, 0.226] | 0.692 [0.240, 1.375] | 0.250 [0.087, 0.500] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 3.176 [1.667, 5.601] | 1.382 [0.588, 2.673] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.778 [0.500, 4.802] | 1.472 [0.275, 4.281] |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

structural_kinked_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 2.538 [1.520, 4.160] | 1.577 [0.843, 2.813] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.136, 0.419] | 2.346 [1.312, 3.938] | 1.298 [0.518, 2.625] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.158, 0.472] | 2.077 [1.069, 3.612] | 1.202 [0.426, 2.519] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.472] | 2.462 [1.250, 4.239] | 1.452 [0.569, 2.957] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.200, 0.516] | 2.308 [1.161, 4.096] | 1.519 [0.625, 3.060] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.765 [1.474, 5.000] | 1.088 [0.545, 1.983] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 8.778 (no interval) | 6.528 (no interval) |

Recall with equal weight per regime: 0.268 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

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

structural_liquidity+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.208, 0.556] | 0.808 [0.384, 1.433] | 0.279 [0.135, 0.489] |
| lead 2 alone (fail) | 26 | 4 | 0.154 [0.042, 0.273] | 1.000 [0.417, 1.750] | 0.385 [0.125, 0.769] |
| lead 3 alone (fail) | 26 | 4 | 0.154 [0.042, 0.280] | 1.154 [0.500, 2.000] | 0.462 [0.156, 0.895] |
| lead 4 alone (fail) | 26 | 4 | 0.154 [0.042, 0.280] | 1.231 [0.417, 2.320] | 0.587 [0.136, 1.250] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.024, 0.226] | 0.654 [0.192, 1.290] | 0.269 [0.073, 0.529] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.812] | 3.118 [1.600, 5.353] | 1.368 [0.568, 2.583] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 0.333 (no interval) | 0.083 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm+settle+h41+dist_roll | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| structural_kinked_fitted | 0.47 (102) | 0.25 (4) | – | 0.00 (5) | 0.07 (29) | 0.53 (17) | 0.31 (101) | 0.33 (9) | 0.62 (13) |
| structural_kinked_rolling | 0.50 (102) | 0.25 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.43 (101) | 0.56 (9) | 0.54 (13) |
| structural_liquidity | 0.49 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.53 (17) | 0.33 (101) | 0.44 (9) | 0.62 (13) |
| structural_liquidity+h41 | 0.46 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.53 (17) | 0.29 (101) | 0.33 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm+settle+h41+dist_roll | +0.0049 [-0.0172, +0.0261] | +0.0404 [+0.0316, +0.0489] | +0.0137 [+0.0121, +0.0157] | +0.0029 [-0.0009, +0.0056] | +0.0132 [-0.0037, +0.0350] | +0.0495 [+0.0271, +0.0720] | +0.0052 [-0.0001, +0.0104] | +0.1399 [+0.0543, +0.2200] | +0.0695 [+0.0361, +0.0979] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| structural_kinked_fitted | +0.0343 [-0.0022, +0.0742] | -0.0041 [-0.0317, +0.0195] | +0.0132 [+0.0115, +0.0150] | +0.0010 [-0.0041, +0.0048] | +0.0223 [+0.0031, +0.0460] | +0.0306 [-0.0022, +0.0656] | +0.0098 [+0.0015, +0.0189] | +0.1158 [+0.0488, +0.1846] | +0.0401 [-0.0040, +0.0870] |
| structural_kinked_rolling | +0.0419 [+0.0171, +0.0686] | -0.0228 [-0.0610, +0.0043] | +0.0131 [+0.0114, +0.0149] | +0.0002 [-0.0055, +0.0049] | +0.0456 [+0.0121, +0.0857] | +0.0299 [-0.0034, +0.0669] | +0.0123 [+0.0044, +0.0203] | +0.1193 [+0.0399, +0.1990] | +0.0362 [+0.0047, +0.0665] |
| structural_liquidity | +0.0321 [-0.0050, +0.0708] | +0.0268 [+0.0160, +0.0373] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0041, +0.0049] | +0.0231 [+0.0027, +0.0495] | +0.0390 [+0.0091, +0.0702] | +0.0123 [+0.0044, +0.0208] | +0.1343 [+0.0762, +0.1967] | +0.0557 [+0.0113, +0.0996] |
| structural_liquidity+h41 | +0.0277 [-0.0113, +0.0675] | +0.0270 [+0.0160, +0.0373] | +0.0133 [+0.0117, +0.0151] | +0.0010 [-0.0036, +0.0048] | +0.0224 [+0.0029, +0.0466] | +0.0384 [+0.0052, +0.0723] | +0.0112 [+0.0033, +0.0194] | +0.1354 [+0.0740, +0.2041] | +0.0561 [+0.0136, +0.1007] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.15 flat / 1.44 weighted (tier 1 on the weighted count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 1.81 flat / 1.17 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted (tier 1 on the weighted count) | 2.9 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.231 | 2.88 flat / 2.18 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 2.88 flat / 2.14 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| structural_kinked_fitted | 10 of 26 | 0.385 [0.219, 0.571] | 0.235 | 4.23 flat / 2.12 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| structural_kinked_rolling | 15 of 26 | 0.577 [0.400, 0.762] | 0.397 | 7.65 flat / 4.64 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| structural_liquidity | 11 of 26 | 0.423 [0.250, 0.613] | 0.231 | 3.92 flat / 1.69 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / yes) |
| structural_liquidity+h41 | 10 of 26 | 0.385 [0.208, 0.556] | 0.231 | 3.58 flat / 1.48 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

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

risk_gbm+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.688] | 1.269 [0.865, 1.900] | 0.731 [0.452, 1.188] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.611] | 0.885 [0.559, 1.367] | 0.442 [0.258, 0.734] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.261, 0.600] | 1.231 [0.833, 1.864] | 0.692 [0.414, 1.118] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 0.846 [0.512, 1.375] | 0.510 [0.277, 0.898] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 0.731 [0.429, 1.167] | 0.452 [0.235, 0.774] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.367, 0.824] | 1.176 [0.696, 2.000] | 0.529 [0.281, 1.000] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.875] | 3.000 [1.777, 6.400] | 2.389 [1.300, 5.750] |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

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

structural_kinked_fitted:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.219, 0.571] | 1.923 [1.030, 3.333] | 0.942 [0.450, 1.713] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.100, 0.375] | 2.346 [1.364, 3.846] | 1.144 [0.510, 2.203] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 1.923 [1.000, 3.193] | 0.808 [0.342, 1.483] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.160, 0.467] | 2.308 [1.263, 3.790] | 0.942 [0.430, 1.661] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.029, 0.226] | 1.462 [0.645, 2.619] | 0.721 [0.263, 1.396] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 4.706 [2.741, 7.813] | 1.941 [0.969, 3.517] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 3.333 [1.125, 8.500] | 2.472 [0.700, 6.794] |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

structural_kinked_rolling:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.692] | 4.115 [2.618, 6.389] | 2.404 [1.410, 4.098] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.650] | 5.500 [3.600, 8.334] | 3.096 [1.822, 5.159] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 4.577 [2.853, 7.137] | 2.519 [1.405, 4.262] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.188, 0.520] | 3.808 [2.208, 6.131] | 2.221 [1.100, 4.010] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.265, 0.591] | 4.269 [2.515, 6.818] | 2.481 [1.280, 4.424] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.353, 0.833] | 5.529 [3.300, 8.934] | 2.353 [1.283, 4.037] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 11.667 (no interval) | 8.972 (no interval) |

Recall with equal weight per regime: 0.472 (2018-19 10/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

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

structural_liquidity+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.208, 0.556] | 1.654 [0.778, 2.909] | 0.606 [0.260, 1.092] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.097, 0.370] | 1.923 [1.094, 3.000] | 0.673 [0.344, 1.120] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.148, 0.467] | 2.077 [1.088, 3.400] | 0.875 [0.371, 1.579] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.130, 0.414] | 2.231 [1.200, 3.601] | 0.913 [0.405, 1.638] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.024, 0.226] | 0.769 [0.294, 1.414] | 0.317 [0.117, 0.583] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.812] | 4.647 [2.667, 7.556] | 1.941 [0.964, 3.430] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 1.556 (no interval) | 0.611 (no interval) |

Recall with equal weight per regime: 0.147 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm+settle+h41+dist_roll | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |
| structural_kinked_fitted | 0.53 (102) | 0.25 (4) | – | 0.00 (5) | 0.07 (29) | 0.53 (17) | 0.37 (101) | 0.33 (9) | 0.62 (13) |
| structural_kinked_rolling | 0.60 (102) | 0.25 (4) | – | 0.00 (5) | 0.69 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.54 (13) |
| structural_liquidity | 0.54 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.76 (17) | 0.40 (101) | 0.44 (9) | 0.62 (13) |
| structural_liquidity+h41 | 0.53 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.40 (101) | 0.44 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm+settle+h41+dist_roll | +0.0049 [-0.0172, +0.0261] | +0.0404 [+0.0316, +0.0489] | +0.0137 [+0.0121, +0.0157] | +0.0029 [-0.0009, +0.0056] | +0.0132 [-0.0037, +0.0350] | +0.0495 [+0.0271, +0.0720] | +0.0052 [-0.0001, +0.0104] | +0.1399 [+0.0543, +0.2200] | +0.0695 [+0.0361, +0.0979] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| structural_kinked_fitted | +0.0343 [-0.0022, +0.0742] | -0.0041 [-0.0317, +0.0195] | +0.0132 [+0.0115, +0.0150] | +0.0010 [-0.0041, +0.0048] | +0.0223 [+0.0031, +0.0460] | +0.0306 [-0.0022, +0.0656] | +0.0098 [+0.0015, +0.0189] | +0.1158 [+0.0488, +0.1846] | +0.0401 [-0.0040, +0.0870] |
| structural_kinked_rolling | +0.0419 [+0.0171, +0.0686] | -0.0228 [-0.0610, +0.0043] | +0.0131 [+0.0114, +0.0149] | +0.0002 [-0.0055, +0.0049] | +0.0456 [+0.0121, +0.0857] | +0.0299 [-0.0034, +0.0669] | +0.0123 [+0.0044, +0.0203] | +0.1193 [+0.0399, +0.1990] | +0.0362 [+0.0047, +0.0665] |
| structural_liquidity | +0.0321 [-0.0050, +0.0708] | +0.0268 [+0.0160, +0.0373] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0041, +0.0049] | +0.0231 [+0.0027, +0.0495] | +0.0390 [+0.0091, +0.0702] | +0.0123 [+0.0044, +0.0208] | +0.1343 [+0.0762, +0.1967] | +0.0557 [+0.0113, +0.0996] |
| structural_liquidity+h41 | +0.0277 [-0.0113, +0.0675] | +0.0270 [+0.0160, +0.0373] | +0.0133 [+0.0117, +0.0151] | +0.0010 [-0.0036, +0.0048] | +0.0224 [+0.0029, +0.0466] | +0.0384 [+0.0052, +0.0723] | +0.0112 [+0.0033, +0.0194] | +0.1354 [+0.0740, +0.2041] | +0.0561 [+0.0136, +0.1007] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| structural_liquidity | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| structural_liquidity+h41 | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| structural_kinked_fitted | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| structural_kinked_rolling | 0 of 4 | 10 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_gbm+settle+h41 | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_gbm+settle+h41+dist_roll | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |

## Brier score and log loss at +5 bp, pooled by horizon

| row | h = 1 Brier / log loss | h = 2 Brier / log loss | h = 3 Brier / log loss | h = 4 Brier / log loss | h = 5 Brier / log loss |
|---|---|---|---|---|---|
| structural_liquidity | 0.0529 / 0.2195 | 0.0645 / 0.2592 | 0.0691 / 0.2952 | 0.0703 / 0.2868 | 0.0730 / 0.2965 |
| structural_liquidity+h41 | 0.0538 / 0.2253 | 0.0656 / 0.2603 | 0.0672 / 0.2882 | 0.0661 / 0.2874 | 0.0709 / 0.2980 |
| structural_kinked_fitted | 0.0567 / 0.2324 | 0.0694 / 0.2695 | 0.0673 / 0.2877 | 0.0656 / 0.2849 | 0.0697 / 0.2937 |
| structural_kinked_rolling | 0.0548 / 0.2022 | 0.0610 / 0.2240 | 0.0652 / 0.2498 | 0.0644 / 0.2349 | 0.0651 / 0.2423 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |
| risk_gbm+settle+h41 | 0.0579 / 0.6610 | 0.0593 / 0.6688 | 0.0612 / 0.6687 | 0.0589 / 0.6720 | 0.0593 / 0.6740 |
| risk_gbm+settle+h41+dist_roll | 0.0574 / 0.6579 | 0.0588 / 0.6633 | 0.0593 / 0.6621 | 0.0588 / 0.6660 | 0.0578 / 0.6661 |
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

## structural_liquidity+h41: onsets only this row warns

structural_liquidity+h41 warns 10 of 26 onsets; at least one of the five passers warns 16. 1 are warned by structural_liquidity+h41 and by none of the five passers:

* 2019-08-13 (flagged at h = 1)

Warned by a passer and not by structural_liquidity+h41: 2019-03-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### structural_liquidity+h41: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 0 | 0 of 1873 | 1195 |
| 2 | 90 | 1 | 0 | 6 | 0 | 0 of 1872 | 1311 |
| 3 | 90 | 1 | 0 | 6 | 0 | 0 of 1871 | 1308 |
| 4 | 90 | 2 | 0 | 6 | 0 | 0 of 1870 | 1297 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1306 |

## structural_kinked_fitted: onsets only this row warns

structural_kinked_fitted warns 10 of 26 onsets; at least one of the five passers warns 16. 1 are warned by structural_kinked_fitted and by none of the five passers:

* 2019-08-13 (flagged at h = 1)

Warned by a passer and not by structural_kinked_fitted: 2019-03-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### structural_kinked_fitted: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 0 | 0 of 1873 | 1144 |
| 2 | 90 | 1 | 0 | 6 | 0 | 0 of 1872 | 1263 |
| 3 | 90 | 1 | 0 | 6 | 0 | 0 of 1871 | 1259 |
| 4 | 90 | 2 | 0 | 6 | 0 | 0 of 1870 | 1251 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1257 |

## structural_kinked_rolling: onsets only this row warns

structural_kinked_rolling warns 15 of 26 onsets; at least one of the five passers warns 16. 3 are warned by structural_kinked_rolling and by none of the five passers:

* 2019-05-28 (flagged at h = 2)
* 2019-08-13 (flagged at h = 1, 2, 3)
* 2020-03-04 (flagged at h = 5)

Warned by a passer and not by structural_kinked_rolling: 2019-01-15, 2019-01-31, 2024-09-30, 2025-12-26

### structural_kinked_rolling: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 0 | 0 of 1873 | 1148 |
| 2 | 90 | 1 | 0 | 6 | 3 | 0 of 1872 | 1257 |
| 3 | 90 | 1 | 0 | 6 | 2 | 0 of 1871 | 1254 |
| 4 | 90 | 2 | 0 | 6 | 1 | 0 of 1870 | 1255 |
| 5 | 89 | 0 | 0 | 7 | 1 | 0 of 1869 | 1253 |

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
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.005 [-0.006, -0.004] | -0.009 [-0.011, -0.008] | -0.005 [-0.007, -0.003] |
| 2 | 41 | 0.038 [–] | 0.031 [–] | 0.058 [–] |
| 3 | 478 | 0.020 [-0.015, 0.057] | -0.003 [-0.055, 0.052] | -0.014 [-0.068, 0.037] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
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
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.002 [-0.003, -0.001] | -0.010 [-0.012, -0.008] | -0.005 [-0.007, -0.003] |
| 2 | 41 | -0.019 [–] | 0.021 [–] | 0.047 [–] |
| 3 | 478 | -0.021 [-0.043, 0.003] | -0.029 [-0.075, 0.017] | -0.036 [-0.072, -0.000] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
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
| 0 | 1041 | 0.009 [0.007, 0.010] | 0.008 [0.006, 0.009] | 0.009 [0.007, 0.010] |
| 1 | 313 | 0.027 [0.021, 0.033] | 0.021 [0.016, 0.027] | 0.023 [0.017, 0.029] |
| 2 | 41 | 0.027 [–] | 0.007 [–] | 0.027 [–] |
| 3 | 478 | 0.034 [0.003, 0.068] | -0.025 [-0.071, 0.018] | -0.045 [-0.094, -0.003] |

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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
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
| 0 | 1041 | 0.001 [0.000, 0.001] | 0.001 [0.001, 0.002] | 0.001 [0.001, 0.001] |
| 1 | 313 | 0.004 [0.003, 0.005] | 0.010 [0.008, 0.012] | 0.008 [0.006, 0.010] |
| 2 | 41 | -0.006 [–] | -0.025 [–] | -0.030 [–] |
| 3 | 478 | 0.010 [-0.014, 0.037] | -0.026 [-0.071, 0.020] | -0.043 [-0.089, -0.003] |

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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
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
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.005 [-0.006, -0.004] | -0.007 [-0.010, -0.001] | -0.006 [-0.009, -0.003] |
| 2 | 41 | 0.030 [–] | 0.038 [–] | 0.032 [–] |
| 3 | 478 | 0.020 [-0.014, 0.058] | -0.027 [-0.073, 0.022] | -0.052 [-0.104, -0.009] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.048 [-0.217, 0.100] |

## structural_liquidity against risk_gbm+settle+h41+dist_roll

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.005, 0.015] |
| 2 | -0.006 [-0.016, 0.005] |
| 3 | -0.010 [-0.023, 0.002] |
| 4 | -0.011 [-0.025, 0.001] |
| 5 | -0.015 [-0.029, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.027 [-0.017, 0.074] | -0.025 [-0.092, 0.036] | -0.061 [-0.122, -0.002] |
| 2020 | 251 | -0.014 [-0.020, -0.008] | -0.016 [-0.021, -0.011] | -0.010 [-0.016, -0.003] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.002 [-0.005, -0.000] | -0.003 [-0.010, 0.000] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.010 [-0.011, 0.034] | -0.011 [-0.033, 0.006] | -0.010 [-0.031, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.011 [-0.029, 0.008] | -0.036 [-0.065, -0.012] | -0.043 [-0.064, -0.025] |
| ordinary | 1603 | 0.007 [-0.003, 0.018] | -0.007 [-0.020, 0.006] | -0.011 [-0.026, 0.002] |
| quarter_end | 31 | -0.006 [-0.073, 0.063] | -0.035 [-0.141, 0.060] | -0.022 [-0.092, 0.042] |
| tax_date | 89 | -0.014 [-0.069, 0.032] | -0.013 [-0.056, 0.034] | -0.037 [-0.088, 0.006] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.005 [-0.006, -0.004] | -0.010 [-0.011, -0.008] | -0.009 [-0.014, -0.006] |
| 2 | 41 | 0.038 [–] | 0.029 [–] | 0.032 [–] |
| 3 | 478 | 0.018 [-0.018, 0.056] | -0.031 [-0.082, 0.016] | -0.056 [-0.104, -0.009] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.333, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.176] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.154] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.208, 0.095] |

## structural_liquidity+h41 against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.006, 0.014] |
| 2 | 0.003 [-0.010, 0.016] |
| 3 | -0.001 [-0.015, 0.013] |
| 4 | 0.001 [-0.014, 0.016] |
| 5 | -0.001 [-0.016, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.026 [-0.019, 0.076] | 0.013 [-0.061, 0.081] | -0.010 [-0.085, 0.068] |
| 2020 | 251 | -0.013 [-0.019, -0.008] | -0.015 [-0.023, -0.007] | -0.010 [-0.017, -0.003] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.007, -0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | 0.007 [-0.016, 0.032] | 0.001 [-0.018, 0.018] | 0.018 [0.002, 0.040] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.016 [-0.037, 0.005] | -0.037 [-0.072, -0.004] | -0.011 [-0.036, 0.011] |
| ordinary | 1603 | 0.006 [-0.003, 0.017] | 0.003 [-0.014, 0.017] | -0.002 [-0.019, 0.015] |
| quarter_end | 31 | 0.020 [-0.036, 0.087] | 0.017 [-0.063, 0.096] | 0.032 [-0.042, 0.107] |
| tax_date | 89 | -0.012 [-0.065, 0.036] | -0.003 [-0.039, 0.034] | 0.025 [-0.014, 0.067] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.005 [-0.006, -0.004] | -0.009 [-0.011, -0.007] | -0.005 [-0.007, -0.003] |
| 2 | 41 | 0.037 [–] | 0.030 [–] | 0.056 [–] |
| 3 | 478 | 0.016 [-0.020, 0.056] | 0.005 [-0.053, 0.057] | -0.005 [-0.065, 0.056] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.261, 0.037] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.133, 0.154] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.154] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.095 [-0.267, 0.067] |

## structural_liquidity+h41 against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.014, -0.002] |
| 2 | -0.009 [-0.017, -0.000] |
| 3 | -0.008 [-0.019, 0.004] |
| 4 | -0.005 [-0.017, 0.008] |
| 5 | -0.007 [-0.020, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.027 [-0.053, 0.002] | -0.025 [-0.081, 0.036] | -0.034 [-0.095, 0.027] |
| 2020 | 251 | -0.006 [-0.012, -0.001] | -0.016 [-0.021, -0.012] | -0.009 [-0.013, -0.005] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.006 [-0.023, 0.011] | 0.005 [-0.005, 0.017] | 0.010 [-0.005, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.010 [-0.035, 0.015] | -0.021 [-0.055, 0.012] | -0.006 [-0.038, 0.023] |
| ordinary | 1603 | -0.007 [-0.013, -0.002] | -0.008 [-0.019, 0.003] | -0.009 [-0.022, 0.002] |
| quarter_end | 31 | 0.005 [-0.063, 0.075] | 0.008 [-0.079, 0.103] | 0.005 [-0.058, 0.076] |
| tax_date | 89 | -0.011 [-0.057, 0.034] | 0.012 [-0.035, 0.066] | 0.024 [-0.031, 0.086] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.002 [-0.003, -0.000] | -0.010 [-0.012, -0.008] | -0.005 [-0.007, -0.003] |
| 2 | 41 | -0.020 [–] | 0.020 [–] | 0.045 [–] |
| 3 | 478 | -0.025 [-0.047, -0.001] | -0.021 [-0.065, 0.026] | -0.027 [-0.075, 0.020] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.457, -0.083] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.300, 0.083] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.625, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.375, 0.000] |

## structural_liquidity+h41 against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.018 [0.010, 0.027] |
| 2 | 0.006 [-0.005, 0.016] |
| 3 | 0.003 [-0.009, 0.015] |
| 4 | 0.005 [-0.009, 0.017] |
| 5 | 0.000 [-0.014, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.028 [-0.009, 0.071] | -0.023 [-0.083, 0.034] | -0.047 [-0.111, 0.020] |
| 2020 | 251 | 0.027 [0.016, 0.038] | 0.022 [0.013, 0.032] | 0.026 [0.018, 0.035] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.012 [0.010, 0.013] | 0.013 [0.011, 0.015] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.001 [-0.003, 0.004] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.022 [0.004, 0.047] | 0.003 [-0.004, 0.009] | 0.004 [-0.005, 0.014] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.038 [0.006, 0.073] | -0.010 [-0.042, 0.021] | 0.003 [-0.024, 0.028] |
| ordinary | 1603 | 0.011 [0.004, 0.020] | 0.000 [-0.012, 0.012] | -0.005 [-0.020, 0.009] |
| quarter_end | 31 | 0.135 [0.071, 0.203] | 0.096 [0.030, 0.156] | 0.095 [0.026, 0.163] |
| tax_date | 89 | 0.056 [0.010, 0.101] | 0.050 [0.005, 0.096] | 0.051 [0.003, 0.097] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.010] | 0.008 [0.006, 0.009] | 0.009 [0.007, 0.010] |
| 1 | 313 | 0.027 [0.021, 0.033] | 0.022 [0.016, 0.027] | 0.023 [0.017, 0.029] |
| 2 | 41 | 0.027 [–] | 0.006 [–] | 0.025 [–] |
| 3 | 478 | 0.030 [0.000, 0.066] | -0.018 [-0.064, 0.026] | -0.036 [-0.090, 0.016] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.179, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.375, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.222, 0.000] |

## structural_liquidity+h41 against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.004, 0.010] |
| 2 | -0.004 [-0.014, 0.005] |
| 3 | -0.003 [-0.014, 0.009] |
| 4 | -0.004 [-0.016, 0.008] |
| 5 | -0.007 [-0.021, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.011 [-0.020, 0.045] | -0.023 [-0.081, 0.035] | -0.044 [-0.111, 0.019] |
| 2020 | 251 | 0.003 [-0.001, 0.007] | 0.011 [0.006, 0.014] | 0.009 [0.004, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.002 [0.001, 0.002] | 0.001 [0.001, 0.002] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.002] |
| 2025-26 | 249 | -0.003 [-0.011, 0.003] | -0.004 [-0.013, 0.004] | -0.004 [-0.013, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.017 [-0.015, 0.051] | -0.019 [-0.054, 0.013] | -0.007 [-0.036, 0.022] |
| ordinary | 1603 | -0.001 [-0.007, 0.004] | -0.004 [-0.015, 0.007] | -0.011 [-0.026, 0.002] |
| quarter_end | 31 | 0.075 [0.006, 0.158] | 0.061 [-0.023, 0.146] | 0.069 [-0.008, 0.160] |
| tax_date | 89 | 0.021 [-0.021, 0.074] | 0.023 [-0.029, 0.082] | 0.025 [-0.032, 0.089] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.001] | 0.001 [0.001, 0.002] | 0.001 [0.001, 0.001] |
| 1 | 313 | 0.004 [0.003, 0.006] | 0.010 [0.008, 0.012] | 0.008 [0.006, 0.010] |
| 2 | 41 | -0.006 [–] | -0.026 [–] | -0.032 [–] |
| 3 | 478 | 0.006 [-0.018, 0.034] | -0.018 [-0.063, 0.026] | -0.034 [-0.086, 0.015] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.240, 0.091] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.286, 0.182] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.250 [-0.545, 0.063] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.308, 0.115] |

## structural_liquidity+h41 against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.006, 0.015] |
| 2 | -0.006 [-0.018, 0.005] |
| 3 | -0.006 [-0.018, 0.006] |
| 4 | -0.007 [-0.021, 0.006] |
| 5 | -0.012 [-0.026, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.026 [-0.020, 0.074] | -0.014 [-0.077, 0.046] | -0.049 [-0.119, 0.020] |
| 2020 | 251 | -0.011 [-0.017, -0.007] | -0.010 [-0.018, -0.003] | -0.004 [-0.011, 0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.000 [-0.002, 0.001] | -0.003 [-0.008, 0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.005 [-0.016, 0.028] | -0.005 [-0.024, 0.013] | -0.007 [-0.023, 0.009] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.037, 0.003] | -0.041 [-0.071, -0.015] | -0.041 [-0.065, -0.018] |
| ordinary | 1603 | 0.007 [-0.003, 0.018] | -0.003 [-0.016, 0.010] | -0.008 [-0.024, 0.007] |
| quarter_end | 31 | 0.011 [-0.054, 0.074] | -0.013 [-0.105, 0.079] | 0.001 [-0.072, 0.072] |
| tax_date | 89 | -0.013 [-0.065, 0.037] | -0.002 [-0.043, 0.038] | -0.030 [-0.076, 0.007] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.005 [-0.006, -0.004] | -0.006 [-0.010, -0.001] | -0.006 [-0.009, -0.003] |
| 2 | 41 | 0.030 [–] | 0.037 [–] | 0.030 [–] |
| 3 | 478 | 0.017 [-0.021, 0.057] | -0.019 [-0.068, 0.028] | -0.043 [-0.099, 0.011] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.318, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.143, 0.143] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.143] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.278, 0.063] |

## structural_liquidity+h41 against risk_gbm+settle+h41+dist_roll

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.006, 0.015] |
| 2 | -0.007 [-0.018, 0.005] |
| 3 | -0.008 [-0.021, 0.005] |
| 4 | -0.007 [-0.021, 0.007] |
| 5 | -0.013 [-0.027, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.023 [-0.024, 0.074] | -0.015 [-0.081, 0.048] | -0.050 [-0.120, 0.021] |
| 2020 | 251 | -0.013 [-0.020, -0.008] | -0.015 [-0.021, -0.010] | -0.009 [-0.015, -0.003] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.002 [-0.004, -0.000] | -0.003 [-0.010, 0.000] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.009 [-0.010, 0.033] | -0.011 [-0.034, 0.006] | -0.010 [-0.029, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.011 [-0.033, 0.008] | -0.044 [-0.076, -0.017] | -0.045 [-0.070, -0.023] |
| ordinary | 1603 | 0.006 [-0.004, 0.018] | -0.004 [-0.018, 0.009] | -0.009 [-0.025, 0.007] |
| quarter_end | 31 | -0.005 [-0.076, 0.067] | -0.027 [-0.128, 0.066] | -0.009 [-0.078, 0.061] |
| tax_date | 89 | -0.013 [-0.065, 0.034] | -0.011 [-0.055, 0.032] | -0.038 [-0.086, 0.006] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.005 [-0.006, -0.004] | -0.010 [-0.011, -0.007] | -0.009 [-0.014, -0.006] |
| 2 | 41 | 0.038 [–] | 0.028 [–] | 0.030 [–] |
| 3 | 478 | 0.014 [-0.024, 0.057] | -0.023 [-0.075, 0.026] | -0.047 [-0.100, 0.009] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.379, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.143, 0.150] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.444, 0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.278, 0.071] |

## structural_liquidity+h41 against structural_liquidity

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.004, 0.001] |
| 2 | -0.001 [-0.004, 0.002] |
| 3 | 0.002 [-0.001, 0.005] |
| 4 | 0.004 [0.000, 0.009] |
| 5 | 0.002 [-0.003, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.008] | 0.010 [-0.004, 0.023] | 0.011 [-0.013, 0.040] |
| 2020 | 251 | 0.000 [-0.001, 0.001] | 0.000 [-0.000, 0.001] | 0.000 [-0.000, 0.001] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.001 [-0.002, 0.000] | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.011, 0.009] | -0.008 [-0.022, 0.004] | -0.002 [-0.017, 0.009] |
| ordinary | 1603 | -0.001 [-0.004, 0.001] | 0.003 [0.000, 0.006] | 0.003 [-0.002, 0.008] |
| quarter_end | 31 | 0.001 [-0.005, 0.009] | 0.008 [-0.000, 0.021] | 0.013 [-0.026, 0.056] |
| tax_date | 89 | 0.000 [-0.001, 0.002] | 0.002 [-0.000, 0.005] | -0.000 [-0.001, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2 | 41 | -0.000 [–] | -0.001 [–] | -0.002 [–] |
| 3 | 478 | -0.004 [-0.015, 0.006] | 0.008 [-0.003, 0.018] | 0.009 [-0.010, 0.032] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.111, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.167, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.136, 0.000] |

## structural_kinked_fitted against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.010, 0.012] |
| 2 | -0.001 [-0.014, 0.013] |
| 3 | -0.001 [-0.015, 0.014] |
| 4 | 0.001 [-0.014, 0.015] |
| 5 | -0.000 [-0.017, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.033 [-0.014, 0.079] | 0.014 [-0.058, 0.090] | -0.003 [-0.087, 0.072] |
| 2020 | 251 | -0.044 [-0.076, -0.019] | -0.018 [-0.025, -0.009] | -0.011 [-0.018, -0.004] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.007, -0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | 0.007 [-0.016, 0.031] | 0.001 [-0.017, 0.018] | 0.018 [0.001, 0.038] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.048, -0.002] | -0.036 [-0.069, -0.005] | -0.004 [-0.024, 0.015] |
| ordinary | 1603 | 0.005 [-0.006, 0.017] | 0.002 [-0.012, 0.019] | -0.002 [-0.020, 0.016] |
| quarter_end | 31 | 0.000 [-0.066, 0.069] | 0.017 [-0.057, 0.096] | 0.033 [-0.038, 0.106] |
| tax_date | 89 | -0.029 [-0.084, 0.025] | -0.004 [-0.037, 0.034] | 0.024 [-0.015, 0.068] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.002, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.031 [-0.059, -0.012] | -0.011 [-0.014, -0.009] | -0.007 [-0.008, -0.004] |
| 2 | 41 | 0.038 [–] | 0.030 [–] | 0.056 [–] |
| 3 | 478 | 0.022 [-0.017, 0.060] | 0.006 [-0.050, 0.064] | 0.000 [-0.067, 0.060] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.286, 0.036] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.143, 0.143] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.143] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.095 [-0.286, 0.071] |

## structural_kinked_fitted against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.017, -0.003] |
| 2 | -0.013 [-0.022, -0.003] |
| 3 | -0.008 [-0.020, 0.003] |
| 4 | -0.004 [-0.016, 0.008] |
| 5 | -0.006 [-0.018, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.020 [-0.045, 0.008] | -0.024 [-0.081, 0.035] | -0.027 [-0.085, 0.040] |
| 2020 | 251 | -0.037 [-0.071, -0.011] | -0.019 [-0.024, -0.014] | -0.010 [-0.014, -0.007] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.006 [-0.023, 0.010] | 0.005 [-0.005, 0.018] | 0.010 [-0.005, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.017 [-0.045, 0.009] | -0.020 [-0.053, 0.010] | 0.001 [-0.023, 0.028] |
| ordinary | 1603 | -0.009 [-0.015, -0.003] | -0.008 [-0.020, 0.002] | -0.008 [-0.021, 0.003] |
| quarter_end | 31 | -0.015 [-0.089, 0.060] | 0.008 [-0.080, 0.105] | 0.007 [-0.057, 0.078] |
| tax_date | 89 | -0.027 [-0.077, 0.026] | 0.011 [-0.038, 0.068] | 0.023 [-0.030, 0.088] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.028 [-0.057, -0.007] | -0.012 [-0.014, -0.009] | -0.006 [-0.008, -0.004] |
| 2 | 41 | -0.019 [–] | 0.020 [–] | 0.045 [–] |
| 3 | 478 | -0.019 [-0.039, 0.003] | -0.021 [-0.066, 0.024] | -0.022 [-0.068, 0.030] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.464, -0.086] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.312, 0.077] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.667, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.391, 0.000] |

## structural_kinked_fitted against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.015 [0.006, 0.024] |
| 2 | 0.002 [-0.009, 0.012] |
| 3 | 0.003 [-0.009, 0.014] |
| 4 | 0.005 [-0.007, 0.017] |
| 5 | 0.001 [-0.013, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.034 [-0.003, 0.074] | -0.022 [-0.082, 0.035] | -0.040 [-0.109, 0.027] |
| 2020 | 251 | -0.004 [-0.035, 0.019] | 0.020 [0.012, 0.028] | 0.025 [0.016, 0.033] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.012 [0.010, 0.013] | 0.013 [0.011, 0.015] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.001 [-0.003, 0.004] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.022 [0.003, 0.047] | 0.003 [-0.004, 0.009] | 0.004 [-0.005, 0.014] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.031 [-0.002, 0.065] | -0.008 [-0.040, 0.020] | 0.010 [-0.010, 0.032] |
| ordinary | 1603 | 0.010 [0.001, 0.018] | 0.000 [-0.012, 0.011] | -0.004 [-0.020, 0.010] |
| quarter_end | 31 | 0.116 [0.046, 0.188] | 0.096 [0.030, 0.160] | 0.096 [0.025, 0.169] |
| tax_date | 89 | 0.040 [-0.005, 0.085] | 0.049 [0.004, 0.096] | 0.050 [0.004, 0.097] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.010] | 0.008 [0.006, 0.009] | 0.009 [0.007, 0.010] |
| 1 | 313 | 0.001 [-0.026, 0.018] | 0.020 [0.015, 0.024] | 0.022 [0.016, 0.028] |
| 2 | 41 | 0.027 [–] | 0.006 [–] | 0.025 [–] |
| 3 | 478 | 0.036 [0.005, 0.068] | -0.017 [-0.065, 0.026] | -0.031 [-0.087, 0.022] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.176, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.364, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.217, 0.000] |

## structural_kinked_fitted against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.008, 0.007] |
| 2 | -0.008 [-0.019, 0.002] |
| 3 | -0.003 [-0.014, 0.009] |
| 4 | -0.003 [-0.016, 0.009] |
| 5 | -0.006 [-0.020, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.017 [-0.012, 0.049] | -0.022 [-0.079, 0.036] | -0.037 [-0.103, 0.025] |
| 2020 | 251 | -0.028 [-0.062, -0.002] | 0.008 [0.004, 0.012] | 0.007 [0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.002 [0.001, 0.002] | 0.001 [0.001, 0.001] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.003] |
| 2025-26 | 249 | -0.003 [-0.011, 0.003] | -0.004 [-0.014, 0.004] | -0.004 [-0.014, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.025, 0.044] | -0.018 [-0.050, 0.013] | 0.001 [-0.022, 0.026] |
| ordinary | 1603 | -0.003 [-0.009, 0.003] | -0.004 [-0.016, 0.007] | -0.010 [-0.024, 0.003] |
| quarter_end | 31 | 0.055 [-0.023, 0.147] | 0.061 [-0.020, 0.150] | 0.071 [-0.005, 0.159] |
| tax_date | 89 | 0.005 [-0.041, 0.061] | 0.022 [-0.032, 0.083] | 0.024 [-0.030, 0.091] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.001] | 0.001 [0.001, 0.002] | 0.001 [0.001, 0.001] |
| 1 | 313 | -0.022 [-0.052, -0.001] | 0.008 [0.007, 0.010] | 0.007 [0.005, 0.009] |
| 2 | 41 | -0.006 [–] | -0.026 [–] | -0.032 [–] |
| 3 | 478 | 0.012 [-0.011, 0.038] | -0.018 [-0.063, 0.028] | -0.029 [-0.081, 0.020] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.238, 0.091] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.286, 0.182] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.250 [-0.533, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.300, 0.111] |

## structural_kinked_fitted against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.009, 0.013] |
| 2 | -0.010 [-0.022, 0.002] |
| 3 | -0.006 [-0.019, 0.006] |
| 4 | -0.007 [-0.021, 0.007] |
| 5 | -0.010 [-0.025, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [-0.013, 0.080] | -0.013 [-0.072, 0.049] | -0.042 [-0.113, 0.027] |
| 2020 | 251 | -0.042 [-0.073, -0.018] | -0.013 [-0.020, -0.005] | -0.006 [-0.013, 0.003] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.000 [-0.002, 0.001] | -0.003 [-0.008, 0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.005 [-0.017, 0.028] | -0.005 [-0.024, 0.013] | -0.007 [-0.025, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.023 [-0.047, -0.002] | -0.040 [-0.069, -0.014] | -0.034 [-0.053, -0.016] |
| ordinary | 1603 | 0.005 [-0.005, 0.017] | -0.003 [-0.016, 0.010] | -0.007 [-0.023, 0.009] |
| quarter_end | 31 | -0.009 [-0.078, 0.067] | -0.013 [-0.101, 0.083] | 0.002 [-0.073, 0.073] |
| tax_date | 89 | -0.029 [-0.085, 0.026] | -0.004 [-0.045, 0.039] | -0.031 [-0.074, 0.007] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.031 [-0.058, -0.011] | -0.008 [-0.012, -0.003] | -0.007 [-0.010, -0.005] |
| 2 | 41 | 0.030 [–] | 0.036 [–] | 0.030 [–] |
| 3 | 478 | 0.022 [-0.014, 0.060] | -0.018 [-0.066, 0.032] | -0.038 [-0.093, 0.018] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.318, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.133, 0.143] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.269, 0.077] |

## structural_kinked_fitted against risk_gbm+settle+h41+dist_roll

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.010, 0.012] |
| 2 | -0.011 [-0.022, 0.001] |
| 3 | -0.008 [-0.021, 0.005] |
| 4 | -0.007 [-0.021, 0.006] |
| 5 | -0.012 [-0.027, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.029 [-0.016, 0.078] | -0.014 [-0.074, 0.049] | -0.043 [-0.115, 0.028] |
| 2020 | 251 | -0.045 [-0.075, -0.020] | -0.018 [-0.023, -0.013] | -0.011 [-0.017, -0.004] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.002 [-0.004, -0.000] | -0.003 [-0.010, 0.000] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.009 [-0.012, 0.033] | -0.011 [-0.033, 0.006] | -0.010 [-0.031, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.019 [-0.042, 0.002] | -0.043 [-0.071, -0.016] | -0.038 [-0.058, -0.020] |
| ordinary | 1603 | 0.005 [-0.006, 0.016] | -0.004 [-0.017, 0.009] | -0.008 [-0.024, 0.008] |
| quarter_end | 31 | -0.024 [-0.095, 0.053] | -0.027 [-0.121, 0.063] | -0.007 [-0.075, 0.058] |
| tax_date | 89 | -0.029 [-0.085, 0.023] | -0.012 [-0.056, 0.031] | -0.038 [-0.087, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 313 | -0.031 [-0.059, -0.011] | -0.012 [-0.014, -0.009] | -0.010 [-0.015, -0.007] |
| 2 | 41 | 0.038 [–] | 0.028 [–] | 0.030 [–] |
| 3 | 478 | 0.020 [-0.017, 0.061] | -0.023 [-0.070, 0.030] | -0.041 [-0.099, 0.014] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.375, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.133, 0.158] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.429, 0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.273, 0.071] |

## structural_kinked_fitted against structural_liquidity+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.007, 0.001] |
| 2 | -0.004 [-0.010, 0.000] |
| 3 | -0.000 [-0.001, 0.000] |
| 4 | 0.001 [-0.000, 0.001] |
| 5 | 0.001 [-0.000, 0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.007 [0.002, 0.012] | 0.001 [-0.001, 0.003] | 0.007 [0.001, 0.015] |
| 2020 | 251 | -0.031 [-0.063, -0.006] | -0.002 [-0.004, -0.001] | -0.001 [-0.002, -0.001] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.008 [-0.020, 0.001] | 0.001 [-0.002, 0.006] | 0.007 [-0.001, 0.019] |
| ordinary | 1603 | -0.001 [-0.005, 0.002] | -0.000 [-0.000, 0.000] | 0.001 [-0.000, 0.002] |
| quarter_end | 31 | -0.020 [-0.054, -0.001] | -0.000 [-0.001, 0.001] | 0.002 [-0.001, 0.006] |
| tax_date | 89 | -0.016 [-0.037, -0.000] | -0.001 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 313 | -0.026 [-0.052, -0.006] | -0.002 [-0.003, -0.001] | -0.001 [-0.002, -0.001] |
| 2 | 41 | 0.000 [–] | -0.000 [–] | 0.000 [–] |
| 3 | 478 | 0.006 [0.002, 0.010] | 0.001 [-0.000, 0.002] | 0.005 [0.001, 0.012] |

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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## structural_kinked_fitted against structural_liquidity

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.009, 0.001] |
| 2 | -0.005 [-0.011, 0.001] |
| 3 | 0.002 [-0.001, 0.005] |
| 4 | 0.005 [0.001, 0.009] |
| 5 | 0.003 [-0.001, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.002 [-0.013, 0.017] | 0.011 [-0.003, 0.025] | 0.018 [-0.007, 0.045] |
| 2020 | 251 | -0.031 [-0.064, -0.005] | -0.002 [-0.004, -0.001] | -0.001 [-0.002, -0.000] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.001 [-0.002, 0.000] | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.008 [-0.024, 0.005] | -0.007 [-0.021, 0.005] | 0.005 [-0.003, 0.014] |
| ordinary | 1603 | -0.002 [-0.007, 0.002] | 0.003 [-0.000, 0.006] | 0.003 [-0.002, 0.009] |
| quarter_end | 31 | -0.019 [-0.053, 0.004] | 0.008 [-0.001, 0.022] | 0.015 [-0.022, 0.054] |
| tax_date | 89 | -0.016 [-0.037, 0.001] | 0.000 [-0.003, 0.004] | -0.001 [-0.002, -0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | -0.026 [-0.054, -0.005] | -0.002 [-0.003, -0.001] | -0.001 [-0.002, -0.001] |
| 2 | 41 | -0.000 [–] | -0.001 [–] | -0.002 [–] |
| 3 | 478 | 0.002 [-0.011, 0.014] | 0.009 [-0.003, 0.020] | 0.014 [-0.005, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.107, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.167, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.130, 0.000] |

## structural_kinked_rolling against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.008, 0.013] |
| 2 | 0.008 [-0.005, 0.020] |
| 3 | 0.001 [-0.012, 0.015] |
| 4 | 0.002 [-0.013, 0.016] |
| 5 | 0.005 [-0.010, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.040 [0.006, 0.076] | 0.048 [0.016, 0.087] | 0.055 [0.019, 0.094] |
| 2020 | 251 | -0.062 [-0.103, -0.032] | -0.085 [-0.162, -0.032] | -0.089 [-0.161, -0.032] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.004 [-0.005, -0.003] | -0.002 [-0.002, -0.001] |
| 2024 | 250 | -0.003 [-0.008, -0.000] | -0.003 [-0.007, -0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.030 [0.001, 0.069] | 0.039 [0.002, 0.085] | 0.047 [0.005, 0.100] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.049, 0.000] | -0.018 [-0.048, 0.012] | 0.008 [-0.028, 0.043] |
| ordinary | 1603 | 0.007 [-0.003, 0.018] | 0.006 [-0.008, 0.019] | 0.005 [-0.008, 0.019] |
| quarter_end | 31 | 0.004 [-0.073, 0.087] | 0.036 [-0.032, 0.108] | 0.065 [-0.008, 0.150] |
| tax_date | 89 | -0.032 [-0.082, 0.014] | -0.058 [-0.116, -0.014] | -0.032 [-0.091, 0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.001] | -0.003 [-0.005, -0.002] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.048 [-0.085, -0.022] | -0.066 [-0.127, -0.023] | -0.065 [-0.125, -0.019] |
| 2 | 41 | 0.093 [–] | 0.126 [–] | 0.200 [–] |
| 3 | 478 | 0.036 [0.006, 0.068] | 0.045 [0.016, 0.077] | 0.047 [0.019, 0.080] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.111, 0.267] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.227, 0.222] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.182, 0.500] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.000 [-0.208, 0.214] |

## structural_kinked_rolling against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.009 [-0.017, -0.001] |
| 2 | -0.004 [-0.016, 0.007] |
| 3 | -0.006 [-0.019, 0.007] |
| 4 | -0.003 [-0.018, 0.011] |
| 5 | -0.001 [-0.016, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.012 [-0.032, 0.008] | 0.010 [-0.022, 0.044] | 0.031 [-0.010, 0.076] |
| 2020 | 251 | -0.056 [-0.097, -0.024] | -0.086 [-0.160, -0.032] | -0.088 [-0.167, -0.031] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.004 [-0.005, -0.003] | -0.002 [-0.002, -0.001] |
| 2024 | 250 | -0.004 [-0.009, -0.000] | -0.003 [-0.005, -0.001] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.017 [-0.004, 0.044] | 0.043 [0.005, 0.093] | 0.039 [-0.001, 0.094] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.046, 0.009] | -0.002 [-0.037, 0.035] | 0.012 [-0.024, 0.053] |
| ordinary | 1603 | -0.006 [-0.014, 0.000] | -0.005 [-0.017, 0.007] | -0.002 [-0.015, 0.012] |
| quarter_end | 31 | -0.012 [-0.067, 0.051] | 0.026 [-0.027, 0.086] | 0.039 [-0.013, 0.099] |
| tax_date | 89 | -0.031 [-0.064, -0.003] | -0.043 [-0.099, 0.002] | -0.033 [-0.093, 0.019] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.003, -0.000] | -0.003 [-0.004, -0.002] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.044 [-0.081, -0.018] | -0.066 [-0.127, -0.023] | -0.064 [-0.131, -0.018] |
| 2 | 41 | 0.036 [–] | 0.116 [–] | 0.188 [–] |
| 3 | 478 | -0.005 [-0.023, 0.014] | 0.018 [-0.010, 0.049] | 0.025 [-0.008, 0.062] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.240, 0.083] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.091] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.429, 0.222] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.294, 0.105] |

## structural_kinked_rolling against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.017 [0.008, 0.026] |
| 2 | 0.010 [-0.000, 0.020] |
| 3 | 0.005 [-0.005, 0.016] |
| 4 | 0.006 [-0.006, 0.018] |
| 5 | 0.006 [-0.007, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.042 [0.018, 0.069] | 0.012 [-0.011, 0.037] | 0.018 [-0.007, 0.047] |
| 2020 | 251 | -0.023 [-0.059, 0.005] | -0.047 [-0.111, 0.003] | -0.053 [-0.129, 0.002] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.010 [0.009, 0.011] | 0.012 [0.011, 0.014] |
| 2024 | 250 | 0.000 [-0.005, 0.005] | 0.001 [-0.003, 0.004] | 0.001 [-0.004, 0.004] |
| 2025-26 | 249 | 0.046 [0.012, 0.085] | 0.041 [0.007, 0.083] | 0.033 [0.001, 0.077] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [-0.004, 0.066] | 0.009 [-0.022, 0.044] | 0.021 [-0.011, 0.055] |
| ordinary | 1603 | 0.012 [0.004, 0.020] | 0.004 [-0.006, 0.013] | 0.003 [-0.009, 0.013] |
| quarter_end | 31 | 0.119 [0.042, 0.198] | 0.114 [0.041, 0.197] | 0.128 [0.046, 0.217] |
| tax_date | 89 | 0.036 [0.004, 0.066] | -0.005 [-0.052, 0.034] | -0.006 [-0.054, 0.035] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.008 [0.006, 0.010] | 0.006 [0.005, 0.008] | 0.008 [0.006, 0.009] |
| 1 | 313 | -0.016 [-0.047, 0.007] | -0.035 [-0.088, 0.005] | -0.036 [-0.100, 0.007] |
| 2 | 41 | 0.082 [–] | 0.102 [–] | 0.169 [–] |
| 3 | 478 | 0.050 [0.026, 0.077] | 0.022 [0.001, 0.045] | 0.016 [-0.006, 0.040] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.094, 0.333] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.318, 0.072] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.236, 0.400] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.200, 0.207] |

## structural_kinked_rolling against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.006, 0.008] |
| 2 | 0.000 [-0.009, 0.009] |
| 3 | -0.001 [-0.012, 0.009] |
| 4 | -0.002 [-0.015, 0.009] |
| 5 | -0.002 [-0.015, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.025 [0.007, 0.045] | 0.012 [-0.008, 0.035] | 0.021 [-0.004, 0.047] |
| 2020 | 251 | -0.046 [-0.089, -0.014] | -0.059 [-0.128, -0.007] | -0.071 [-0.147, -0.014] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.001, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.000 [-0.001, 0.002] | 0.001 [0.000, 0.001] | 0.001 [-0.000, 0.002] |
| 2025-26 | 249 | 0.020 [0.007, 0.035] | 0.034 [0.009, 0.066] | 0.025 [0.004, 0.053] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.018, 0.038] | -0.000 [-0.030, 0.032] | 0.012 [-0.021, 0.043] |
| ordinary | 1603 | -0.000 [-0.006, 0.005] | -0.001 [-0.010, 0.008] | -0.003 [-0.014, 0.006] |
| quarter_end | 31 | 0.059 [-0.024, 0.143] | 0.079 [0.025, 0.141] | 0.103 [0.024, 0.191] |
| tax_date | 89 | 0.001 [-0.040, 0.035] | -0.032 [-0.092, 0.020] | -0.032 [-0.097, 0.026] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [0.000, 0.001] | -0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] |
| 1 | 313 | -0.038 [-0.075, -0.012] | -0.046 [-0.104, -0.005] | -0.051 [-0.112, -0.006] |
| 2 | 41 | 0.049 [–] | 0.070 [–] | 0.112 [–] |
| 3 | 478 | 0.026 [0.012, 0.042] | 0.021 [0.001, 0.043] | 0.018 [-0.002, 0.039] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.045, 0.294] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.167, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.250, 0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.143, 0.148] |

## structural_kinked_rolling against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.008, 0.014] |
| 2 | -0.002 [-0.013, 0.009] |
| 3 | -0.004 [-0.017, 0.008] |
| 4 | -0.005 [-0.020, 0.007] |
| 5 | -0.006 [-0.020, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.040 [0.005, 0.077] | 0.021 [-0.007, 0.053] | 0.016 [-0.016, 0.048] |
| 2020 | 251 | -0.061 [-0.101, -0.031] | -0.080 [-0.149, -0.030] | -0.084 [-0.159, -0.023] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.004 [-0.005, -0.003] | -0.002 [-0.002, -0.001] |
| 2024 | 250 | -0.001 [-0.003, 0.001] | -0.003 [-0.007, -0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.028 [-0.000, 0.066] | 0.033 [-0.000, 0.078] | 0.023 [-0.014, 0.067] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.048, 0.000] | -0.023 [-0.054, 0.009] | -0.023 [-0.052, 0.004] |
| ordinary | 1603 | 0.008 [-0.003, 0.019] | 0.000 [-0.012, 0.013] | -0.000 [-0.014, 0.012] |
| quarter_end | 31 | -0.005 [-0.076, 0.064] | 0.005 [-0.075, 0.089] | 0.035 [-0.039, 0.110] |
| tax_date | 89 | -0.033 [-0.079, 0.016] | -0.058 [-0.107, -0.015] | -0.087 [-0.147, -0.034] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.003 [-0.005, -0.002] | -0.002 [-0.004, -0.001] |
| 1 | 313 | -0.048 [-0.083, -0.022] | -0.063 [-0.121, -0.023] | -0.065 [-0.128, -0.019] |
| 2 | 41 | 0.085 [–] | 0.133 [–] | 0.174 [–] |
| 3 | 478 | 0.037 [0.008, 0.069] | 0.021 [-0.005, 0.049] | 0.009 [-0.017, 0.036] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.143, 0.217] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.214, 0.222] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.182, 0.500] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.000 [-0.208, 0.217] |

## structural_kinked_rolling against risk_gbm+settle+h41+dist_roll

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.008, 0.013] |
| 2 | -0.002 [-0.013, 0.009] |
| 3 | -0.006 [-0.020, 0.006] |
| 4 | -0.006 [-0.020, 0.007] |
| 5 | -0.007 [-0.022, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.037 [0.004, 0.074] | 0.020 [-0.009, 0.052] | 0.015 [-0.015, 0.046] |
| 2020 | 251 | -0.063 [-0.103, -0.032] | -0.085 [-0.156, -0.032] | -0.089 [-0.169, -0.030] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.004 [-0.005, -0.003] | -0.002 [-0.002, -0.001] |
| 2024 | 250 | -0.003 [-0.006, -0.000] | -0.004 [-0.009, -0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.032 [0.004, 0.068] | 0.027 [-0.003, 0.065] | 0.019 [-0.016, 0.065] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.020 [-0.045, 0.005] | -0.025 [-0.054, 0.002] | -0.027 [-0.056, -0.002] |
| ordinary | 1603 | 0.007 [-0.003, 0.018] | -0.001 [-0.013, 0.011] | -0.001 [-0.015, 0.011] |
| quarter_end | 31 | -0.021 [-0.083, 0.048] | -0.009 [-0.084, 0.068] | 0.025 [-0.038, 0.100] |
| tax_date | 89 | -0.033 [-0.078, 0.005] | -0.066 [-0.128, -0.018] | -0.095 [-0.165, -0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.001] | -0.003 [-0.005, -0.002] | -0.002 [-0.004, -0.001] |
| 1 | 313 | -0.048 [-0.084, -0.022] | -0.066 [-0.127, -0.024] | -0.068 [-0.133, -0.022] |
| 2 | 41 | 0.093 [–] | 0.124 [–] | 0.174 [–] |
| 3 | 478 | 0.034 [0.006, 0.067] | 0.016 [-0.007, 0.044] | 0.005 [-0.020, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.161, 0.174] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.214, 0.231] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.231, 0.400] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.200, 0.217] |

## structural_kinked_rolling against structural_liquidity+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.009, 0.006] |
| 2 | 0.005 [-0.007, 0.016] |
| 3 | 0.002 [-0.013, 0.016] |
| 4 | 0.002 [-0.014, 0.018] |
| 5 | 0.006 [-0.011, 0.022] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.014 [-0.008, 0.036] | 0.035 [-0.008, 0.085] | 0.065 [0.012, 0.121] |
| 2020 | 251 | -0.050 [-0.093, -0.019] | -0.070 [-0.140, -0.016] | -0.080 [-0.154, -0.020] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | -0.001 [-0.002, 0.000] | -0.000 [-0.001, 0.001] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.023 [0.007, 0.042] | 0.038 [0.007, 0.074] | 0.029 [0.001, 0.065] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.008 [-0.031, 0.015] | 0.019 [-0.020, 0.056] | 0.019 [-0.017, 0.054] |
| ordinary | 1603 | 0.001 [-0.006, 0.007] | 0.003 [-0.010, 0.017] | 0.008 [-0.008, 0.024] |
| quarter_end | 31 | -0.016 [-0.081, 0.058] | 0.018 [-0.045, 0.092] | 0.034 [-0.032, 0.105] |
| tax_date | 89 | -0.020 [-0.082, 0.038] | -0.055 [-0.126, 0.005] | -0.057 [-0.132, 0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.000] | -0.001 [-0.002, -0.001] | -0.001 [-0.003, -0.000] |
| 1 | 313 | -0.043 [-0.079, -0.017] | -0.057 [-0.115, -0.015] | -0.059 [-0.121, -0.012] |
| 2 | 41 | 0.055 [–] | 0.096 [–] | 0.144 [–] |
| 3 | 478 | 0.020 [0.002, 0.039] | 0.040 [0.004, 0.079] | 0.052 [0.010, 0.099] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.192 [0.000, 0.391] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.214, 0.218] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.250 [0.000, 0.500] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.095 [-0.111, 0.300] |

## structural_kinked_rolling against structural_liquidity

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.010, 0.005] |
| 2 | 0.004 [-0.008, 0.015] |
| 3 | 0.004 [-0.011, 0.018] |
| 4 | 0.006 [-0.010, 0.021] |
| 5 | 0.008 [-0.008, 0.025] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.010 [-0.011, 0.030] | 0.045 [0.001, 0.094] | 0.076 [0.027, 0.130] |
| 2020 | 251 | -0.050 [-0.093, -0.018] | -0.070 [-0.139, -0.016] | -0.079 [-0.156, -0.022] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.001, -0.000] |
| 2024 | 250 | -0.001 [-0.002, 0.000] | -0.000 [-0.001, 0.001] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.022 [0.007, 0.040] | 0.038 [0.007, 0.078] | 0.029 [0.001, 0.066] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.009 [-0.031, 0.012] | 0.010 [-0.026, 0.049] | 0.016 [-0.018, 0.050] |
| ordinary | 1603 | 0.000 [-0.007, 0.006] | 0.006 [-0.007, 0.019] | 0.010 [-0.005, 0.027] |
| quarter_end | 31 | -0.015 [-0.083, 0.055] | 0.026 [-0.045, 0.108] | 0.047 [-0.014, 0.123] |
| tax_date | 89 | -0.019 [-0.079, 0.037] | -0.054 [-0.124, 0.009] | -0.057 [-0.128, 0.009] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.000] | -0.001 [-0.002, -0.001] | -0.001 [-0.003, -0.000] |
| 1 | 313 | -0.042 [-0.078, -0.016] | -0.057 [-0.117, -0.014] | -0.059 [-0.123, -0.014] |
| 2 | 41 | 0.055 [–] | 0.095 [-0.000, 0.225] | 0.142 [–] |
| 3 | 478 | 0.016 [-0.001, 0.033] | 0.047 [0.012, 0.088] | 0.061 [0.023, 0.104] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.154 [-0.038, 0.368] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.133] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.100, 0.429] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.048 [-0.143, 0.250] |

