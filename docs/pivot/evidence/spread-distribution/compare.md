# Forecast the spread, then apply the +5 bp threshold (#632)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| calendar_climatology | 10 / 5.00 fail | fail | 10 / 5.38 fail | 0 / 3.78 fail |
| ngboost_laplace | 15 / 2.54 fail | fail | 15 / 4.38 fail | 4 / 0.33 fail |
| persistence_logistic | 7 / 3.42 fail | fail | 7 / 5.73 fail | 0 / 2.22 fail |
| risk_gbm | 13 / 1.35 pass | pass (h = 1) | 13 / 2.00 pass | 3 / 1.56 fail |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 17 / 1.35 pass | pass (h = 1) | 17 / 2.62 fail | 5 / 1.33 fail |
| risk_gbm+settle+h41 | 14 / 1.35 pass | pass (h = 1) | 14 / 2.00 pass | 4 / 1.78 fail |
| risk_gbm+settle+h41+dist_roll | 15 / 1.38 pass | pass (h = 1) | 15 / 1.85 pass | 5 / 1.78 pass |
| risk_gbm_base | 14 / 1.50 pass | pass (h = 1) | 14 / 2.04 fail | 4 / 2.00 fail |
| risk_logistic | 14 / 1.85 pass | pass (h = 1) | 14 / 2.42 fail | 4 / 2.89 fail |
| risk_logistic_base | 13 / 1.77 pass | pass (h = 1) | 13 / 2.04 fail | 3 / 2.33 fail |
| risk_quantile_skewt_base | 14 / 1.88 pass | pass (h = 1) | 14 / 2.54 fail | 4 / 3.22 fail |
| spread_q_gbm+settle+h41+dist_roll | 15 / 1.62 pass | pass (h = 1) | 15 / 2.50 fail | 5 / 2.44 fail |
| spread_q_gbm+two_part+settle+h41+dist_roll | 19 / 3.00 fail | fail | 19 / 6.85 fail | 6 / 1.89 pass |

## Tier 1 under weighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| calendar_climatology | 12 / 3.75 fail | fail | 12 / 3.90 fail | 0 / 4.56 fail |
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 5 / 0.50 fail |
| persistence_logistic | 12 / 3.25 fail | fail | 12 / 4.09 fail | 1 / 2.86 fail |
| risk_gbm | 13 / 0.80 pass | pass (h = 1) | 13 / 1.48 pass | 3 / 1.61 fail |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 18 / 1.08 pass | pass (h = 1) | 18 / 1.88 pass | 5 / 1.72 fail |
| risk_gbm+settle+h41 | 14 / 0.88 pass | pass (h = 1) | 14 / 1.44 pass | 4 / 1.72 fail |
| risk_gbm+settle+h41+dist_roll | 15 / 0.88 pass | pass (h = 1) | 15 / 1.27 pass | 5 / 1.53 pass |
| risk_gbm_base | 14 / 0.97 pass | pass (h = 1) | 14 / 1.59 pass | 4 / 2.06 fail |
| risk_logistic | 16 / 1.74 pass | pass (h = 1) | 16 / 2.55 fail | 6 / 4.39 fail |
| risk_logistic_base | 15 / 1.65 pass | pass (h = 1) | 15 / 2.18 fail | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass (h = 1) | 15 / 2.14 fail | 5 / 3.81 fail |
| spread_q_gbm+settle+h41+dist_roll | 15 / 1.55 pass | pass (h = 1) | 15 / 2.23 fail | 5 / 3.19 fail |
| spread_q_gbm+two_part+settle+h41+dist_roll | 20 / 2.80 fail | pass (h = 3) | 20 / 5.35 fail | 7 / 2.36 fail |

## Tier 1 under weighted/before_only

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| calendar_climatology | 12 / 4.55 fail | fail | 12 / 4.70 fail | 0 / 4.44 fail |
| ngboost_laplace | 16 / 2.23 fail | pass (h = 1) | 16 / 3.30 fail | 5 / 0.58 fail |
| persistence_logistic | 10 / 3.23 fail | fail | 10 / 4.50 fail | 1 / 1.75 fail |
| risk_gbm | 13 / 0.95 pass | pass (h = 1) | 13 / 1.64 pass | 3 / 1.78 fail |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 18 / 1.31 pass | pass (h = 1) | 18 / 2.31 fail | 5 / 1.72 fail |
| risk_gbm+settle+h41 | 14 / 1.02 pass | pass (h = 1) | 14 / 1.63 pass | 4 / 1.89 fail |
| risk_gbm+settle+h41+dist_roll | 15 / 1.06 pass | pass (h = 1) | 15 / 1.46 pass | 5 / 1.86 pass |
| risk_gbm_base | 14 / 1.08 pass | pass (h = 1) | 14 / 1.72 pass | 4 / 2.22 fail |
| risk_logistic | 16 / 1.90 pass | pass (h = 1) | 16 / 2.70 fail | 6 / 4.31 fail |
| risk_logistic_base | 14 / 1.78 pass | pass (h = 1) | 14 / 2.26 fail | 4 / 3.58 fail |
| risk_quantile_skewt_base | 15 / 1.81 pass | pass (h = 1) | 15 / 2.22 fail | 5 / 4.14 fail |
| spread_q_gbm+settle+h41+dist_roll | 15 / 1.70 pass | pass (h = 1) | 15 / 2.42 fail | 5 / 3.42 fail |
| spread_q_gbm+two_part+settle+h41+dist_roll | 19 / 2.52 fail | fail | 19 / 5.72 fail | 6 / 2.97 fail |

## The judge's tables under the unweighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.4 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 17 of 26 | 0.654 [0.480, 0.818] | 0.231 | 2.62 flat / 1.48 weighted (tier 1 on the flat count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.00 flat / 1.29 weighted (tier 1 on the flat count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 1.85 flat / 1.18 weighted (tier 1 on the flat count) | 1.7 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted (tier 1 on the flat count) | 1.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 2.04 flat / 1.41 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.231 | 2.54 flat / 1.80 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| spread_q_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.385, 0.758] | 0.231 | 2.50 flat / 1.81 weighted (tier 1 on the flat count) | 1.9 / 1.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| spread_q_gbm+two_part+settle+h41+dist_roll | 19 of 26 | 0.731 [0.560, 0.889] | 0.368 | 6.85 flat / 3.30 weighted (tier 1 on the flat count) | 1.0 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |

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

risk_gbm+every_day+gate+settle+h41+iorb+tailcap75:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.320, 0.667] | 1.038 [0.478, 1.807] | 0.481 [0.227, 0.834] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.600] | 0.769 [0.433, 1.250] | 0.413 [0.214, 0.697] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.571] | 1.346 [0.742, 2.200] | 0.731 [0.392, 1.250] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.235, 0.615] | 1.308 [0.750, 2.059] | 0.702 [0.398, 1.131] |
| lead 5 alone (pass) | 26 | 13 | 0.500 [0.308, 0.688] | 1.346 [0.786, 2.095] | 0.740 [0.430, 1.221] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 2.706 [1.550, 4.500] | 1.132 [0.650, 1.917] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 2.444 (no interval) | 2.139 (no interval) |

Recall with equal weight per regime: 0.501 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

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
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.688] | 1.385 [0.961, 2.053] | 0.788 [0.482, 1.278] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.656] | 0.846 [0.516, 1.346] | 0.433 [0.242, 0.736] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.526] | 0.962 [0.609, 1.529] | 0.529 [0.289, 0.929] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 0.846 [0.520, 1.333] | 0.529 [0.295, 0.891] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 0.885 [0.550, 1.381] | 0.510 [0.281, 0.859] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.367, 0.824] | 1.235 [0.750, 2.083] | 0.544 [0.290, 1.000] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.875] | 3.000 [1.778, 6.500] | 2.389 [1.268, 5.750] |

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

spread_q_gbm+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.758] | 1.615 [1.052, 2.579] | 1.106 [0.635, 1.947] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.714] | 1.231 [0.757, 2.000] | 0.760 [0.402, 1.380] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.652] | 1.231 [0.743, 2.000] | 0.827 [0.423, 1.528] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.310, 0.688] | 1.231 [0.767, 1.952] | 0.769 [0.422, 1.334] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.652] | 1.192 [0.727, 1.895] | 0.721 [0.375, 1.284] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.412 [0.778, 2.444] | 0.676 [0.308, 1.341] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 4.556 (no interval) | 3.944 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

spread_q_gbm+two_part+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.289, 0.632] | 3.000 [1.823, 4.786] | 1.577 [0.719, 2.962] |
| lead 2 alone (fail) | 26 | 13 | 0.500 [0.320, 0.677] | 2.769 [1.793, 4.059] | 1.106 [0.716, 1.620] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.207, 0.571] | 1.808 [0.875, 3.042] | 0.663 [0.325, 1.097] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.621] | 2.615 [1.586, 4.000] | 1.106 [0.677, 1.715] |
| lead 5 alone (fail) | 26 | 14 | 0.538 [0.346, 0.727] | 2.846 [1.792, 4.316] | 1.173 [0.697, 1.826] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 7.941 [5.262, 12.400] | 3.971 [2.325, 6.835] |
| outside 2018-2019 | 9 | 6 | 0.667 [0.333, 0.917] | 4.778 [2.917, 8.500] | 2.028 [1.225, 3.901] |

Recall with equal weight per regime: 0.566 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 5/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 0.30 (102) | 0.50 (4) | – | 0.00 (5) | 0.28 (29) | 0.71 (17) | 0.18 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm+settle+h41+dist_roll | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| spread_q_gbm+settle+h41+dist_roll | 0.28 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.62 (13) |
| spread_q_gbm+two_part+settle+h41+dist_roll | 0.53 (102) | 0.25 (4) | – | 0.00 (5) | 0.52 (29) | 0.65 (17) | 0.47 (101) | 0.56 (9) | 0.54 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | +0.0041 [-0.0198, +0.0257] | +0.0422 [+0.0351, +0.0497] | +0.0137 [+0.0120, +0.0155] | +0.0014 [-0.0035, +0.0053] | +0.0174 [-0.0004, +0.0399] | +0.0538 [+0.0309, +0.0787] | +0.0056 [+0.0004, +0.0105] | +0.1247 [+0.0400, +0.2085] | +0.0689 [+0.0392, +0.0987] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm+settle+h41+dist_roll | +0.0044 [-0.0178, +0.0255] | +0.0404 [+0.0317, +0.0486] | +0.0137 [+0.0120, +0.0156] | +0.0031 [-0.0007, +0.0058] | +0.0161 [-0.0010, +0.0381] | +0.0520 [+0.0286, +0.0755] | +0.0049 [-0.0004, +0.0101] | +0.1492 [+0.0706, +0.2227] | +0.0722 [+0.0427, +0.0972] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| spread_q_gbm+settle+h41+dist_roll | -0.0034 [-0.0237, +0.0148] | +0.0388 [+0.0312, +0.0465] | +0.0133 [+0.0116, +0.0152] | +0.0031 [-0.0002, +0.0059] | +0.0278 [+0.0111, +0.0475] | +0.0472 [+0.0273, +0.0686] | +0.0055 [+0.0002, +0.0101] | +0.1309 [+0.0528, +0.2067] | +0.0681 [+0.0462, +0.0905] |
| spread_q_gbm+two_part+settle+h41+dist_roll | +0.0557 [+0.0274, +0.0852] | +0.0307 [+0.0185, +0.0417] | +0.0133 [+0.0114, +0.0152] | -0.0007 [-0.0092, +0.0052] | +0.0414 [+0.0102, +0.0797] | +0.0553 [+0.0323, +0.0838] | +0.0189 [+0.0109, +0.0275] | +0.1309 [+0.0532, +0.2092] | +0.0681 [+0.0465, +0.0911] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 18 of 26 | 0.692 [0.522, 0.852] | 0.231 | 3.35 flat / 1.88 weighted (tier 1 on the weighted count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.15 flat / 1.44 weighted (tier 1 on the weighted count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 1.96 flat / 1.27 weighted (tier 1 on the weighted count) | 2.2 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted (tier 1 on the weighted count) | 2.9 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.231 | 2.88 flat / 2.18 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 2.88 flat / 2.14 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| spread_q_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.385, 0.758] | 0.231 | 3.00 flat / 2.23 weighted (tier 1 on the weighted count) | 2.9 / 2.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| spread_q_gbm+two_part+settle+h41+dist_roll | 20 of 26 | 0.769 [0.600, 0.923] | 0.423 | 9.73 flat / 5.35 weighted (tier 1 on the weighted count) | 2.9 / 0.3 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) | fail (no / no / no) |

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

risk_gbm+every_day+gate+settle+h41+iorb+tailcap75:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.370, 0.706] | 1.846 [1.200, 2.800] | 0.962 [0.618, 1.524] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.285, 0.643] | 1.500 [0.828, 2.471] | 0.779 [0.444, 1.271] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.238, 0.600] | 1.962 [1.172, 3.084] | 1.077 [0.629, 1.779] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.269, 0.654] | 1.769 [1.000, 2.833] | 0.894 [0.512, 1.457] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.333, 0.731] | 1.846 [1.067, 2.936] | 1.038 [0.609, 1.719] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.542, 1.000] | 3.176 [1.750, 5.401] | 1.265 [0.706, 2.157] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 3.667 (no interval) | 3.056 (no interval) |

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

risk_gbm+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.323, 0.688] | 1.500 [1.037, 2.211] | 0.875 [0.550, 1.405] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.656] | 0.846 [0.516, 1.346] | 0.433 [0.242, 0.736] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.190, 0.526] | 0.962 [0.609, 1.529] | 0.529 [0.289, 0.929] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 0.846 [0.520, 1.333] | 0.529 [0.295, 0.891] |
| lead 5 alone (fail) | 26 | 11 | 0.423 [0.250, 0.607] | 0.962 [0.611, 1.500] | 0.558 [0.311, 0.950] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.367, 0.824] | 1.235 [0.750, 2.083] | 0.544 [0.290, 1.000] |
| outside 2018-2019 | 9 | 5 | 0.556 [0.200, 0.875] | 3.333 [2.000, 7.010] | 2.639 [1.432, 6.253] |

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

spread_q_gbm+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 15 | 0.577 [0.385, 0.758] | 2.231 [1.478, 3.500] | 1.548 [0.906, 2.672] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.348, 0.714] | 1.308 [0.839, 2.105] | 0.837 [0.469, 1.484] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.652] | 1.500 [0.941, 2.462] | 1.048 [0.568, 1.893] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.310, 0.688] | 1.231 [0.767, 1.952] | 0.769 [0.422, 1.334] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.273, 0.652] | 1.692 [1.117, 2.667] | 1.144 [0.676, 1.953] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.364, 0.818] | 1.471 [0.824, 2.502] | 0.706 [0.327, 1.383] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 5.889 (no interval) | 5.111 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

spread_q_gbm+two_part+settle+h41+dist_roll:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 15 | 0.577 [0.405, 0.742] | 5.077 [3.419, 7.723] | 2.798 [1.640, 4.701] |
| lead 2 alone (fail) | 26 | 15 | 0.577 [0.395, 0.750] | 4.808 [3.419, 6.889] | 2.154 [1.485, 3.213] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.314, 0.682] | 3.885 [2.595, 5.810] | 1.798 [1.218, 2.739] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.312, 0.692] | 4.385 [2.933, 6.593] | 2.144 [1.382, 3.363] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.346, 0.727] | 4.346 [2.833, 6.550] | 2.000 [1.260, 3.132] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.538, 1.000] | 9.529 [6.411, 14.648] | 4.912 [2.920, 8.269] |
| outside 2018-2019 | 9 | 7 | 0.778 [0.500, 1.000] | 10.111 [6.500, 20.200] | 6.167 [3.544, 13.941] |

Recall with equal weight per regime: 0.691 (2018-19 13/17, 2020 2/2, 2024 0/2, 2025-26 5/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 0.32 (102) | 0.50 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.18 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm+settle+h41+dist_roll | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |
| spread_q_gbm+settle+h41+dist_roll | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.77 (13) |
| spread_q_gbm+two_part+settle+h41+dist_roll | 0.57 (102) | 0.50 (4) | – | 0.20 (5) | 0.72 (29) | 0.76 (17) | 0.54 (101) | 0.67 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | +0.0041 [-0.0198, +0.0257] | +0.0422 [+0.0351, +0.0497] | +0.0137 [+0.0120, +0.0155] | +0.0014 [-0.0035, +0.0053] | +0.0174 [-0.0004, +0.0399] | +0.0538 [+0.0309, +0.0787] | +0.0056 [+0.0004, +0.0105] | +0.1247 [+0.0400, +0.2085] | +0.0689 [+0.0392, +0.0987] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm+settle+h41+dist_roll | +0.0044 [-0.0178, +0.0255] | +0.0404 [+0.0317, +0.0486] | +0.0137 [+0.0120, +0.0156] | +0.0031 [-0.0007, +0.0058] | +0.0161 [-0.0010, +0.0381] | +0.0520 [+0.0286, +0.0755] | +0.0049 [-0.0004, +0.0101] | +0.1492 [+0.0706, +0.2227] | +0.0722 [+0.0427, +0.0972] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| spread_q_gbm+settle+h41+dist_roll | -0.0034 [-0.0237, +0.0148] | +0.0388 [+0.0312, +0.0465] | +0.0133 [+0.0116, +0.0152] | +0.0031 [-0.0002, +0.0059] | +0.0278 [+0.0111, +0.0475] | +0.0472 [+0.0273, +0.0686] | +0.0055 [+0.0002, +0.0101] | +0.1309 [+0.0528, +0.2067] | +0.0681 [+0.0462, +0.0905] |
| spread_q_gbm+two_part+settle+h41+dist_roll | +0.0557 [+0.0274, +0.0852] | +0.0307 [+0.0185, +0.0417] | +0.0133 [+0.0114, +0.0152] | -0.0007 [-0.0092, +0.0052] | +0.0414 [+0.0102, +0.0797] | +0.0553 [+0.0323, +0.0838] | +0.0189 [+0.0109, +0.0275] | +0.1309 [+0.0532, +0.2092] | +0.0681 [+0.0465, +0.0911] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| risk_gbm+settle+h41 | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_gbm+settle+h41+dist_roll | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| spread_q_gbm+settle+h41+dist_roll | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| spread_q_gbm+two_part+settle+h41+dist_roll | 0 of 4 | 13 of 13 | 2 of 2 | 0 of 2 | 5 of 5 |

## Brier score and log loss at +5 bp, pooled by horizon

| row | h = 1 Brier / log loss | h = 2 Brier / log loss | h = 3 Brier / log loss | h = 4 Brier / log loss | h = 5 Brier / log loss |
|---|---|---|---|---|---|
| calendar_climatology | 0.0714 / 0.2963 | 0.0711 / 0.2954 | 0.0707 / 0.2943 | 0.0708 / 0.2952 | 0.0709 / 0.2958 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |
| persistence_logistic | 0.0563 / 0.2014 | 0.0611 / 0.2184 | 0.0644 / 0.2424 | 0.0624 / 0.2254 | 0.0634 / 0.2394 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 0.0570 / 0.6422 | 0.0583 / 0.6206 | 0.0608 / 0.6410 | 0.0580 / 0.6185 | 0.0579 / 0.6129 |
| risk_gbm+settle+h41 | 0.0579 / 0.6610 | 0.0593 / 0.6688 | 0.0612 / 0.6687 | 0.0589 / 0.6720 | 0.0593 / 0.6740 |
| risk_gbm+settle+h41+dist_roll | 0.0571 / 0.6553 | 0.0586 / 0.6618 | 0.0594 / 0.6616 | 0.0582 / 0.6621 | 0.0586 / 0.6682 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| spread_q_gbm+settle+h41+dist_roll | 0.0575 / 0.6579 | 0.0575 / 0.6524 | 0.0574 / 0.6567 | 0.0584 / 0.6645 | 0.0593 / 0.6635 |
| spread_q_gbm+two_part+settle+h41+dist_roll | 0.0454 / 0.1877 | 0.0484 / 0.1709 | 0.0494 / 0.1810 | 0.0502 / 0.2415 | 0.0508 / 0.2020 |

## risk_gbm+settle+h41: onsets only this row warns

risk_gbm+settle+h41 warns 14 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+settle+h41 and by none of the five passers:


Warned by a passer and not by risk_gbm+settle+h41: 2024-09-30, 2025-10-15

### risk_gbm+settle+h41: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 0 | 1469 of 1873 | 380 |
| 2 | 90 | 0 | 0 | 7 | 0 | 1471 of 1872 | 377 |
| 3 | 90 | 0 | 0 | 7 | 1 | 1473 of 1871 | 373 |
| 4 | 90 | 1 | 0 | 7 | 1 | 1473 of 1870 | 373 |
| 5 | 89 | 0 | 0 | 7 | 0 | 1472 of 1869 | 373 |

## risk_gbm+settle+h41+dist_roll: onsets only this row warns

risk_gbm+settle+h41+dist_roll warns 15 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+settle+h41+dist_roll and by none of the five passers:


Warned by a passer and not by risk_gbm+settle+h41+dist_roll: 2024-09-30

### risk_gbm+settle+h41+dist_roll: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 0 | 1469 of 1873 | 381 |
| 2 | 90 | 0 | 0 | 7 | 0 | 1471 of 1872 | 376 |
| 3 | 90 | 0 | 0 | 7 | 1 | 1473 of 1871 | 375 |
| 4 | 90 | 1 | 0 | 7 | 1 | 1473 of 1870 | 372 |
| 5 | 89 | 0 | 0 | 7 | 0 | 1472 of 1869 | 374 |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap75: onsets only this row warns

risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 warns 18 of 26 onsets; at least one of the five passers warns 16. 4 are warned by risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 4, 5)
* 2019-08-13 (flagged at h = 5)
* 2020-03-04 (flagged at h = 1)

Warned by a passer and not by risk_gbm+every_day+gate+settle+h41+iorb+tailcap75: 2024-09-30, 2025-10-15

### risk_gbm+every_day+gate+settle+h41+iorb+tailcap75: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 0 | 1394 of 1873 | 447 |
| 2 | 90 | 0 | 0 | 7 | 0 | 1375 of 1872 | 463 |
| 3 | 90 | 0 | 0 | 7 | 1 | 1382 of 1871 | 454 |
| 4 | 90 | 1 | 0 | 7 | 1 | 1375 of 1870 | 463 |
| 5 | 89 | 0 | 0 | 7 | 0 | 1380 of 1869 | 456 |

## spread_q_gbm+settle+h41+dist_roll: onsets only this row warns

spread_q_gbm+settle+h41+dist_roll warns 15 of 26 onsets; at least one of the five passers warns 16. 0 are warned by spread_q_gbm+settle+h41+dist_roll and by none of the five passers:


Warned by a passer and not by spread_q_gbm+settle+h41+dist_roll: 2024-09-30

### spread_q_gbm+settle+h41+dist_roll: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 0 | 1474 of 1873 | 375 |
| 2 | 90 | 0 | 0 | 6 | 0 | 1473 of 1872 | 376 |
| 3 | 90 | 0 | 0 | 7 | 1 | 1477 of 1871 | 370 |
| 4 | 90 | 1 | 0 | 7 | 1 | 1474 of 1870 | 372 |
| 5 | 89 | 0 | 0 | 7 | 0 | 1480 of 1869 | 364 |

## spread_q_gbm+two_part+settle+h41+dist_roll: onsets only this row warns

spread_q_gbm+two_part+settle+h41+dist_roll warns 20 of 26 onsets; at least one of the five passers warns 16. 5 are warned by spread_q_gbm+two_part+settle+h41+dist_roll and by none of the five passers:

* 2019-05-28 (flagged at h = 4, 5)
* 2019-06-25 (flagged at h = 3, 4, 5)
* 2019-08-13 (flagged at h = 2, 3, 4)
* 2020-03-04 (flagged at h = 1)
* 2020-03-12 (flagged at h = 5)

Warned by a passer and not by spread_q_gbm+two_part+settle+h41+dist_roll: 2024-09-30

### spread_q_gbm+two_part+settle+h41+dist_roll: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 1 | 961 of 1873 | 744 |
| 2 | 90 | 0 | 0 | 6 | 1 | 962 of 1872 | 750 |
| 3 | 90 | 0 | 0 | 7 | 2 | 911 of 1871 | 781 |
| 4 | 90 | 1 | 0 | 7 | 1 | 898 of 1870 | 810 |
| 5 | 89 | 0 | 0 | 7 | 0 | 844 of 1869 | 782 |

## risk_gbm+settle+h41 against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.014 [0.008, 0.019] |
| 2 | 0.012 [0.007, 0.016] |
| 3 | 0.010 [0.004, 0.014] |
| 4 | 0.012 [0.007, 0.017] |
| 5 | 0.012 [0.007, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.002 [-0.022, 0.024] | -0.009 [-0.030, 0.010] | 0.002 [-0.017, 0.021] |
| 2020 | 251 | 0.038 [0.030, 0.047] | 0.033 [0.024, 0.041] | 0.031 [0.019, 0.041] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.003, 0.005] | 0.004 [0.000, 0.007] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.017 [-0.001, 0.039] | 0.007 [-0.007, 0.024] | 0.011 [0.000, 0.023] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.054 [0.031, 0.077] | 0.032 [0.015, 0.048] | 0.044 [0.026, 0.062] |
| ordinary | 1603 | 0.005 [-0.001, 0.009] | 0.003 [-0.002, 0.008] | 0.003 [-0.002, 0.008] |
| quarter_end | 31 | 0.125 [0.038, 0.204] | 0.109 [0.029, 0.188] | 0.094 [0.009, 0.176] |
| tax_date | 89 | 0.069 [0.039, 0.098] | 0.053 [0.026, 0.079] | 0.081 [0.055, 0.107] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.028 [0.021, 0.034] | 0.029 [0.023, 0.035] |
| 2 | 41 | -0.003 [–] | -0.030 [–] | -0.005 [–] |
| 3 | 478 | 0.014 [-0.007, 0.033] | 0.001 [-0.018, 0.018] | 0.007 [-0.011, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.125, 0.292] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.091] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.417, 0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.000 [-0.222, 0.231] |

## risk_gbm+settle+h41 against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.012 [-0.021, -0.003] |
| 2 | -0.003 [-0.011, 0.006] |
| 3 | -0.002 [-0.010, 0.006] |
| 4 | 0.003 [-0.006, 0.011] |
| 5 | 0.004 [-0.005, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.052 [-0.096, -0.013] | -0.011 [-0.052, 0.030] | 0.015 [-0.028, 0.061] |
| 2020 | 251 | 0.005 [0.001, 0.009] | -0.006 [-0.014, 0.001] | -0.005 [-0.014, 0.003] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | 0.000 [-0.003, 0.004] | -0.001 [-0.001, -0.000] |
| 2025-26 | 249 | -0.011 [-0.023, -0.001] | 0.010 [-0.004, 0.026] | 0.016 [0.002, 0.033] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.006 [-0.008, 0.019] | 0.020 [-0.002, 0.044] | 0.035 [0.012, 0.062] |
| ordinary | 1603 | -0.014 [-0.025, -0.005] | -0.005 [-0.014, 0.003] | -0.001 [-0.011, 0.009] |
| quarter_end | 31 | -0.006 [-0.053, 0.034] | 0.021 [-0.070, 0.107] | 0.005 [-0.059, 0.067] |
| tax_date | 89 | 0.002 [-0.031, 0.033] | 0.014 [-0.019, 0.054] | 0.054 [0.017, 0.103] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | -0.003 [-0.009, -0.000] | 0.001 [-0.002, 0.005] |
| 2 | 41 | -0.050 [–] | -0.016 [–] | 0.014 [–] |
| 3 | 478 | -0.041 [-0.078, -0.010] | -0.002 [-0.036, 0.030] | 0.016 [-0.020, 0.052] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.227, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.267, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.500, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.095 [-0.214, 0.000] |

## risk_gbm+settle+h41 against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.010, 0.006] |
| 2 | 0.002 [-0.005, 0.008] |
| 3 | 0.003 [-0.003, 0.009] |
| 4 | 0.003 [-0.003, 0.010] |
| 5 | 0.004 [-0.002, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.015 [-0.051, 0.019] | -0.009 [-0.036, 0.016] | 0.005 [-0.022, 0.028] |
| 2020 | 251 | 0.015 [0.008, 0.022] | 0.021 [0.013, 0.028] | 0.013 [0.003, 0.021] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.002 [-0.001, 0.005] | 0.004 [0.001, 0.008] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.008 [-0.039, 0.018] | 0.001 [-0.023, 0.025] | 0.003 [-0.022, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.033 [0.010, 0.057] | 0.022 [0.003, 0.042] | 0.034 [0.015, 0.056] |
| ordinary | 1603 | -0.008 [-0.018, 0.000] | -0.001 [-0.009, 0.005] | -0.003 [-0.010, 0.004] |
| quarter_end | 31 | 0.064 [-0.014, 0.148] | 0.074 [-0.011, 0.167] | 0.068 [-0.005, 0.151] |
| tax_date | 89 | 0.033 [-0.003, 0.072] | 0.025 [-0.011, 0.063] | 0.055 [0.019, 0.099] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.000, 0.001] | 0.003 [0.002, 0.004] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.017 [0.010, 0.022] | 0.014 [0.011, 0.017] |
| 2 | 41 | -0.036 [–] | -0.063 [–] | -0.062 [–] |
| 3 | 478 | -0.010 [-0.040, 0.018] | 0.001 [-0.023, 0.022] | 0.009 [-0.013, 0.029] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.148, 0.300] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.294, 0.188] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.167 [-0.500, 0.200] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.000 [-0.250, 0.250] |

## risk_gbm+settle+h41 against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.001, 0.001] |
| 2 | 0.009 [0.005, 0.014] |
| 3 | 0.005 [0.001, 0.010] |
| 4 | 0.008 [0.004, 0.012] |
| 5 | 0.010 [0.005, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.000 [-0.001, 0.002] | 0.027 [0.011, 0.044] | 0.039 [0.023, 0.057] |
| 2020 | 251 | -0.001 [-0.003, -0.000] | -0.005 [-0.015, 0.004] | -0.006 [-0.012, -0.000] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | 0.000 [-0.000, 0.001] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.002 [-0.001, 0.006] | 0.006 [-0.001, 0.014] | 0.025 [0.007, 0.047] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.004, 0.002] | 0.004 [-0.011, 0.018] | 0.030 [0.013, 0.049] |
| ordinary | 1603 | -0.000 [-0.001, -0.000] | 0.005 [0.002, 0.010] | 0.006 [0.002, 0.010] |
| quarter_end | 31 | 0.009 [-0.033, 0.048] | 0.031 [-0.018, 0.085] | 0.031 [0.000, 0.067] |
| tax_date | 89 | 0.000 [-0.004, 0.004] | -0.000 [-0.027, 0.022] | 0.055 [0.022, 0.092] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [-0.000, 0.000] | -0.003 [-0.008, 0.000] | 0.000 [-0.003, 0.004] |
| 2 | 41 | 0.007 [–] | -0.006 [–] | 0.026 [–] |
| 3 | 478 | -0.001 [-0.002, 0.001] | 0.024 [0.010, 0.038] | 0.038 [0.022, 0.055] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [0.000, 0.107] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [0.000, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## risk_gbm+settle+h41+dist_roll against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.014 [0.009, 0.020] |
| 2 | 0.012 [0.007, 0.017] |
| 3 | 0.011 [0.006, 0.016] |
| 4 | 0.013 [0.008, 0.018] |
| 5 | 0.012 [0.007, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.004 [-0.017, 0.025] | -0.007 [-0.025, 0.010] | 0.002 [-0.018, 0.022] |
| 2020 | 251 | 0.040 [0.032, 0.049] | 0.037 [0.028, 0.047] | 0.033 [0.020, 0.044] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.003 [-0.001, 0.006] | 0.005 [0.000, 0.009] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.016 [-0.001, 0.038] | 0.012 [-0.006, 0.034] | 0.013 [0.000, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.052 [0.029, 0.077] | 0.033 [0.012, 0.054] | 0.047 [0.028, 0.070] |
| ordinary | 1603 | 0.005 [-0.001, 0.010] | 0.004 [-0.001, 0.009] | 0.004 [-0.002, 0.008] |
| quarter_end | 31 | 0.149 [0.072, 0.232] | 0.107 [0.019, 0.199] | 0.104 [0.027, 0.188] |
| tax_date | 89 | 0.072 [0.045, 0.101] | 0.068 [0.034, 0.102] | 0.078 [0.041, 0.113] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.010] | 0.009 [0.008, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.039] | 0.031 [0.024, 0.038] | 0.033 [0.026, 0.039] |
| 2 | 41 | -0.008 [–] | -0.029 [–] | -0.000 [–] |
| 3 | 478 | 0.017 [-0.003, 0.036] | 0.006 [-0.012, 0.023] | 0.006 [-0.011, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.103, 0.345] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.077] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.375, 0.375] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.219, 0.222] |

## risk_gbm+settle+h41+dist_roll against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.011 [-0.020, -0.003] |
| 2 | -0.002 [-0.011, 0.006] |
| 3 | 0.000 [-0.008, 0.008] |
| 4 | 0.003 [-0.005, 0.012] |
| 5 | 0.005 [-0.004, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.050 [-0.091, -0.011] | -0.009 [-0.050, 0.029] | 0.015 [-0.030, 0.059] |
| 2020 | 251 | 0.007 [0.004, 0.011] | -0.001 [-0.004, 0.001] | -0.002 [-0.012, 0.005] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.003, 0.000] | 0.001 [-0.003, 0.006] | -0.000 [-0.002, 0.001] |
| 2025-26 | 249 | -0.013 [-0.025, -0.002] | 0.015 [-0.004, 0.037] | 0.019 [0.001, 0.040] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.004 [-0.011, 0.017] | 0.022 [-0.003, 0.048] | 0.039 [0.014, 0.066] |
| ordinary | 1603 | -0.014 [-0.024, -0.004] | -0.004 [-0.013, 0.004] | -0.001 [-0.011, 0.009] |
| quarter_end | 31 | 0.018 [-0.008, 0.043] | 0.019 [-0.057, 0.093] | 0.015 [-0.050, 0.077] |
| tax_date | 89 | 0.005 [-0.022, 0.030] | 0.030 [-0.008, 0.075] | 0.052 [0.003, 0.108] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.001, -0.000] | -0.000 [-0.001, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | -0.000 [-0.000, 0.000] | 0.005 [0.001, 0.011] |
| 2 | 41 | -0.055 [–] | -0.015 [–] | 0.019 [–] |
| 3 | 478 | -0.039 [-0.073, -0.008] | 0.002 [-0.032, 0.034] | 0.015 [-0.020, 0.051] |

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
| ordinary | 12 | -0.167 [-0.375, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.222, 0.000] |

## risk_gbm+settle+h41+dist_roll against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.009, 0.007] |
| 2 | 0.002 [-0.004, 0.009] |
| 3 | 0.005 [-0.001, 0.011] |
| 4 | 0.004 [-0.002, 0.010] |
| 5 | 0.005 [-0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.012 [-0.048, 0.022] | -0.007 [-0.035, 0.016] | 0.005 [-0.020, 0.028] |
| 2020 | 251 | 0.017 [0.012, 0.023] | 0.025 [0.020, 0.030] | 0.015 [0.006, 0.023] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.003 [0.001, 0.007] | 0.005 [0.001, 0.010] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.010 [-0.039, 0.016] | 0.006 [-0.017, 0.032] | 0.006 [-0.018, 0.029] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.031 [0.008, 0.056] | 0.024 [0.004, 0.045] | 0.038 [0.018, 0.061] |
| ordinary | 1603 | -0.008 [-0.017, 0.001] | -0.000 [-0.008, 0.006] | -0.002 [-0.010, 0.004] |
| quarter_end | 31 | 0.089 [0.022, 0.165] | 0.073 [-0.004, 0.150] | 0.079 [0.001, 0.163] |
| tax_date | 89 | 0.037 [0.005, 0.072] | 0.041 [-0.000, 0.089] | 0.053 [0.007, 0.104] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.000, 0.002] | 0.003 [0.002, 0.005] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.020 [0.015, 0.024] | 0.018 [0.014, 0.023] |
| 2 | 41 | -0.042 [–] | -0.062 [–] | -0.057 [–] |
| 3 | 478 | -0.008 [-0.040, 0.020] | 0.005 [-0.019, 0.026] | 0.008 [-0.013, 0.029] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.125, 0.348] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.308, 0.176] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.083 [-0.455, 0.294] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.250, 0.238] |

## risk_gbm+settle+h41+dist_roll against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.000, 0.002] |
| 2 | 0.010 [0.006, 0.015] |
| 3 | 0.007 [0.004, 0.011] |
| 4 | 0.009 [0.004, 0.013] |
| 5 | 0.011 [0.006, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.003 [-0.001, 0.007] | 0.029 [0.015, 0.044] | 0.039 [0.022, 0.057] |
| 2020 | 251 | 0.001 [-0.002, 0.004] | -0.000 [-0.005, 0.004] | -0.003 [-0.010, 0.002] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.002, 0.000] | 0.001 [-0.000, 0.003] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.001 [-0.004, 0.005] | 0.010 [-0.003, 0.027] | 0.028 [0.008, 0.052] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.002 [-0.006, 0.001] | 0.006 [-0.011, 0.023] | 0.034 [0.014, 0.057] |
| ordinary | 1603 | 0.000 [-0.001, 0.001] | 0.007 [0.003, 0.010] | 0.006 [0.002, 0.011] |
| quarter_end | 31 | 0.034 [0.000, 0.076] | 0.029 [-0.010, 0.084] | 0.041 [0.014, 0.075] |
| tax_date | 89 | 0.004 [-0.009, 0.020] | 0.015 [-0.018, 0.051] | 0.052 [0.023, 0.084] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | 0.000 [-0.000, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.004 [0.001, 0.010] |
| 2 | 41 | 0.002 [–] | -0.005 [–] | 0.031 [–] |
| 3 | 478 | 0.002 [-0.001, 0.006] | 0.028 [0.016, 0.042] | 0.038 [0.022, 0.054] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.176] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.014 [0.009, 0.020] |
| 2 | 0.013 [0.008, 0.017] |
| 3 | 0.010 [0.005, 0.015] |
| 4 | 0.013 [0.008, 0.018] |
| 5 | 0.013 [0.009, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.004 [-0.018, 0.026] | -0.007 [-0.027, 0.012] | 0.010 [-0.009, 0.027] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.033 [0.023, 0.041] | 0.031 [0.018, 0.041] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.013 [0.012, 0.015] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.004 [-0.000, 0.007] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.017 [0.001, 0.039] | 0.007 [-0.007, 0.025] | 0.011 [0.001, 0.023] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.054 [0.031, 0.078] | 0.032 [0.014, 0.049] | 0.046 [0.028, 0.064] |
| ordinary | 1603 | 0.006 [0.001, 0.010] | 0.004 [-0.001, 0.008] | 0.005 [-0.000, 0.009] |
| quarter_end | 31 | 0.125 [0.039, 0.209] | 0.109 [0.028, 0.186] | 0.094 [0.008, 0.175] |
| tax_date | 89 | 0.069 [0.040, 0.098] | 0.053 [0.027, 0.079] | 0.081 [0.056, 0.108] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.008 [0.006, 0.010] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.028 [0.021, 0.034] | 0.029 [0.023, 0.034] |
| 2 | 41 | -0.003 [–] | -0.030 [–] | -0.005 [–] |
| 3 | 478 | 0.018 [-0.003, 0.037] | 0.003 [-0.014, 0.020] | 0.012 [-0.004, 0.028] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.231 [0.097, 0.387] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.000, 0.455] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.190 [0.048, 0.357] |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.011 [-0.021, -0.003] |
| 2 | -0.001 [-0.009, 0.006] |
| 3 | -0.001 [-0.010, 0.007] |
| 4 | 0.004 [-0.005, 0.012] |
| 5 | 0.006 [-0.003, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.050 [-0.092, -0.012] | -0.009 [-0.050, 0.031] | 0.022 [-0.021, 0.062] |
| 2020 | 251 | 0.009 [0.002, 0.018] | -0.006 [-0.014, 0.000] | -0.005 [-0.013, 0.003] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.001, 0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | 0.000 [-0.003, 0.004] | -0.001 [-0.001, -0.000] |
| 2025-26 | 249 | -0.011 [-0.023, -0.001] | 0.010 [-0.004, 0.027] | 0.016 [0.003, 0.032] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.006 [-0.008, 0.019] | 0.020 [-0.002, 0.042] | 0.037 [0.015, 0.062] |
| ordinary | 1603 | -0.013 [-0.024, -0.004] | -0.005 [-0.013, 0.003] | 0.000 [-0.009, 0.009] |
| quarter_end | 31 | -0.006 [-0.053, 0.033] | 0.021 [-0.074, 0.106] | 0.005 [-0.058, 0.069] |
| tax_date | 89 | 0.002 [-0.033, 0.033] | 0.014 [-0.020, 0.053] | 0.054 [0.016, 0.100] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | -0.003 [-0.009, -0.000] | 0.001 [-0.002, 0.005] |
| 2 | 41 | -0.050 [–] | -0.016 [–] | 0.014 [–] |
| 3 | 478 | -0.038 [-0.072, -0.007] | -0.000 [-0.034, 0.032] | 0.021 [-0.014, 0.054] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.071, 0.154] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | 0.095 [0.000, 0.211] |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.009, 0.007] |
| 2 | 0.003 [-0.004, 0.009] |
| 3 | 0.004 [-0.003, 0.010] |
| 4 | 0.004 [-0.002, 0.010] |
| 5 | 0.005 [-0.000, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.013 [-0.051, 0.021] | -0.007 [-0.033, 0.018] | 0.012 [-0.013, 0.036] |
| 2020 | 251 | 0.019 [0.011, 0.029] | 0.021 [0.013, 0.028] | 0.013 [0.004, 0.021] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.001, 0.003] |
| 2024 | 250 | 0.002 [-0.001, 0.005] | 0.004 [0.001, 0.008] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.008 [-0.039, 0.018] | 0.001 [-0.024, 0.026] | 0.003 [-0.021, 0.025] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.033 [0.009, 0.059] | 0.022 [0.003, 0.042] | 0.036 [0.018, 0.058] |
| ordinary | 1603 | -0.007 [-0.016, 0.001] | -0.001 [-0.008, 0.006] | -0.001 [-0.008, 0.005] |
| quarter_end | 31 | 0.064 [-0.012, 0.143] | 0.074 [-0.010, 0.161] | 0.068 [-0.009, 0.152] |
| tax_date | 89 | 0.033 [-0.004, 0.072] | 0.025 [-0.010, 0.063] | 0.055 [0.017, 0.099] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | 0.003 [0.001, 0.004] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.017 [0.011, 0.021] | 0.014 [0.011, 0.017] |
| 2 | 41 | -0.036 [–] | -0.063 [–] | -0.062 [–] |
| 3 | 478 | -0.006 [-0.038, 0.022] | 0.003 [-0.020, 0.024] | 0.014 [-0.006, 0.034] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.231 [0.071, 0.419] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.286] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.800 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.167 [–] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.190 [0.000, 0.391] |

## risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.001, 0.002] |
| 2 | 0.010 [0.005, 0.016] |
| 3 | 0.006 [0.002, 0.011] |
| 4 | 0.009 [0.004, 0.014] |
| 5 | 0.012 [0.006, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.003 [-0.002, 0.008] | 0.030 [0.013, 0.048] | 0.047 [0.027, 0.068] |
| 2020 | 251 | 0.003 [-0.002, 0.009] | -0.005 [-0.015, 0.004] | -0.006 [-0.012, -0.000] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | 0.000 [-0.000, 0.001] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.002 [-0.001, 0.006] | 0.006 [-0.001, 0.014] | 0.025 [0.006, 0.050] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.004, 0.002] | 0.004 [-0.010, 0.018] | 0.032 [0.015, 0.052] |
| ordinary | 1603 | 0.001 [-0.001, 0.002] | 0.006 [0.002, 0.011] | 0.007 [0.002, 0.012] |
| quarter_end | 31 | 0.009 [-0.032, 0.050] | 0.031 [-0.017, 0.087] | 0.031 [-0.000, 0.067] |
| tax_date | 89 | 0.000 [-0.004, 0.004] | -0.000 [-0.025, 0.024] | 0.055 [0.021, 0.095] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.001, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [-0.000, 0.000] | -0.003 [-0.008, 0.000] | 0.000 [-0.002, 0.004] |
| 2 | 41 | 0.007 [–] | -0.006 [–] | 0.026 [–] |
| 3 | 478 | 0.003 [-0.001, 0.009] | 0.026 [0.012, 0.042] | 0.044 [0.026, 0.064] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.192 [0.071, 0.333] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.350] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.333 [0.111, 0.556] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.190 [0.059, 0.350] |

## spread_q_gbm+settle+h41+dist_roll against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.014 [0.009, 0.019] |
| 2 | 0.014 [0.008, 0.018] |
| 3 | 0.013 [0.008, 0.018] |
| 4 | 0.012 [0.007, 0.017] |
| 5 | 0.012 [0.007, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.003 [-0.023, 0.015] | -0.003 [-0.021, 0.014] | -0.004 [-0.024, 0.016] |
| 2020 | 251 | 0.039 [0.031, 0.047] | 0.037 [0.028, 0.046] | 0.032 [0.021, 0.042] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.013 [0.012, 0.015] | 0.014 [0.012, 0.015] |
| 2024 | 250 | 0.003 [-0.000, 0.006] | 0.003 [-0.000, 0.005] | 0.002 [-0.002, 0.005] |
| 2025-26 | 249 | 0.028 [0.011, 0.050] | 0.024 [0.007, 0.046] | 0.018 [0.007, 0.033] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.047 [0.027, 0.070] | 0.041 [0.023, 0.064] | 0.038 [0.021, 0.058] |
| ordinary | 1603 | 0.006 [0.000, 0.010] | 0.005 [-0.000, 0.010] | 0.003 [-0.002, 0.008] |
| quarter_end | 31 | 0.131 [0.052, 0.209] | 0.120 [0.035, 0.208] | 0.119 [0.038, 0.203] |
| tax_date | 89 | 0.068 [0.047, 0.090] | 0.082 [0.059, 0.105] | 0.078 [0.057, 0.101] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.010] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.031 [0.025, 0.037] | 0.030 [0.023, 0.036] | 0.030 [0.024, 0.036] |
| 2 | 41 | 0.037 [–] | 0.022 [–] | 0.028 [–] |
| 3 | 478 | 0.012 [-0.007, 0.031] | 0.011 [-0.007, 0.029] | 0.004 [-0.014, 0.020] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.104, 0.333] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.077] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.364, 0.364] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.214, 0.211] |

## spread_q_gbm+settle+h41+dist_roll against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.011 [-0.022, -0.003] |
| 2 | -0.001 [-0.009, 0.007] |
| 3 | 0.002 [-0.007, 0.011] |
| 4 | 0.003 [-0.006, 0.012] |
| 5 | 0.004 [-0.004, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.058 [-0.101, -0.018] | -0.004 [-0.048, 0.036] | 0.009 [-0.034, 0.050] |
| 2020 | 251 | 0.006 [0.003, 0.009] | -0.002 [-0.006, 0.002] | -0.004 [-0.012, 0.003] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.001 [-0.003, 0.000] | -0.001 [-0.003, 0.001] | 0.001 [-0.000, 0.002] |
| 2025-26 | 249 | -0.001 [-0.007, 0.005] | 0.026 [0.007, 0.051] | 0.024 [0.006, 0.044] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.013, 0.010] | 0.030 [0.007, 0.057] | 0.029 [0.007, 0.056] |
| ordinary | 1603 | -0.013 [-0.025, -0.004] | -0.003 [-0.013, 0.005] | -0.001 [-0.011, 0.009] |
| quarter_end | 31 | 0.000 [-0.014, 0.013] | 0.032 [-0.009, 0.079] | 0.030 [-0.005, 0.071] |
| tax_date | 89 | 0.001 [-0.008, 0.010] | 0.043 [0.016, 0.076] | 0.051 [0.020, 0.088] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.001, -0.000] | -0.001 [-0.001, -0.000] | -0.000 [-0.000, -0.000] |
| 1 | 313 | 0.003 [0.001, 0.005] | -0.002 [-0.004, -0.000] | 0.002 [-0.001, 0.008] |
| 2 | 41 | -0.010 [–] | 0.036 [–] | 0.047 [–] |
| 3 | 478 | -0.043 [-0.080, -0.011] | 0.007 [-0.028, 0.040] | 0.013 [-0.022, 0.046] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.182, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.286, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.385, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.227, 0.000] |

## spread_q_gbm+settle+h41+dist_roll against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.009, 0.006] |
| 2 | 0.004 [-0.003, 0.010] |
| 3 | 0.007 [0.001, 0.013] |
| 4 | 0.004 [-0.002, 0.010] |
| 5 | 0.004 [-0.002, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.020 [-0.055, 0.011] | -0.003 [-0.028, 0.021] | -0.001 [-0.026, 0.024] |
| 2020 | 251 | 0.015 [0.010, 0.022] | 0.025 [0.018, 0.030] | 0.014 [0.004, 0.022] |
| 2021-23 | 748 | 0.000 [-0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.001, 0.003] |
| 2024 | 250 | 0.003 [-0.000, 0.008] | 0.003 [0.001, 0.005] | 0.002 [0.001, 0.004] |
| 2025-26 | 249 | 0.002 [-0.021, 0.024] | 0.017 [-0.004, 0.043] | 0.011 [-0.010, 0.032] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.026 [0.009, 0.044] | 0.032 [0.014, 0.052] | 0.029 [0.010, 0.048] |
| ordinary | 1603 | -0.007 [-0.016, 0.001] | 0.001 [-0.007, 0.007] | -0.003 [-0.010, 0.004] |
| quarter_end | 31 | 0.071 [0.014, 0.135] | 0.085 [0.033, 0.143] | 0.093 [0.031, 0.156] |
| tax_date | 89 | 0.033 [0.013, 0.055] | 0.054 [0.022, 0.089] | 0.052 [0.022, 0.087] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.000, 0.002] | 0.003 [0.002, 0.003] | 0.001 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.006, 0.011] | 0.019 [0.015, 0.022] | 0.015 [0.012, 0.020] |
| 2 | 41 | 0.003 [–] | -0.011 [–] | -0.029 [–] |
| 3 | 478 | -0.012 [-0.041, 0.014] | 0.010 [-0.011, 0.032] | 0.006 [-0.016, 0.027] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.111, 0.360] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.300, 0.182] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | -0.083 [-0.444, 0.333] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.000 [-0.250, 0.261] |

## spread_q_gbm+settle+h41+dist_roll against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.002, 0.003] |
| 2 | 0.011 [0.007, 0.016] |
| 3 | 0.009 [0.006, 0.014] |
| 4 | 0.008 [0.004, 0.013] |
| 5 | 0.010 [0.006, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.005 [-0.015, 0.005] | 0.034 [0.022, 0.048] | 0.033 [0.020, 0.048] |
| 2020 | 251 | -0.001 [-0.003, 0.002] | -0.001 [-0.004, 0.002] | -0.005 [-0.010, -0.001] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.001 [-0.002, 0.001] | -0.001 [-0.003, 0.000] | 0.001 [-0.000, 0.001] |
| 2025-26 | 249 | 0.012 [0.001, 0.024] | 0.022 [0.007, 0.039] | 0.033 [0.010, 0.062] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.007 [-0.017, 0.003] | 0.014 [-0.001, 0.031] | 0.025 [0.007, 0.046] |
| ordinary | 1603 | 0.001 [-0.001, 0.002] | 0.007 [0.004, 0.011] | 0.006 [0.002, 0.009] |
| quarter_end | 31 | 0.015 [-0.023, 0.060] | 0.042 [-0.010, 0.100] | 0.056 [0.023, 0.096] |
| tax_date | 89 | -0.000 [-0.028, 0.031] | 0.029 [0.008, 0.052] | 0.052 [0.018, 0.091] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.000 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 313 | -0.001 [-0.001, -0.000] | -0.001 [-0.003, 0.000] | 0.002 [-0.002, 0.007] |
| 2 | 41 | 0.047 [–] | 0.046 [–] | 0.059 [–] |
| 3 | 478 | -0.003 [-0.011, 0.006] | 0.034 [0.023, 0.046] | 0.035 [0.021, 0.050] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.182] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.000 [0.000, 0.000] |

## spread_q_gbm+settle+h41+dist_roll against risk_gbm+every_day+gate+settle+h41+iorb+tailcap75

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.004, 0.002] |
| 2 | 0.001 [-0.002, 0.004] |
| 3 | 0.003 [0.001, 0.006] |
| 4 | -0.000 [-0.003, 0.002] |
| 5 | -0.001 [-0.004, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.008 [-0.019, 0.004] | 0.004 [-0.005, 0.013] | -0.013 [-0.023, -0.004] |
| 2020 | 251 | -0.003 [-0.010, 0.002] | 0.004 [-0.004, 0.013] | 0.001 [-0.004, 0.006] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.002 [-0.001, 0.006] | -0.001 [-0.004, 0.000] | 0.001 [-0.000, 0.003] |
| 2025-26 | 249 | 0.010 [0.001, 0.022] | 0.016 [0.004, 0.030] | 0.008 [0.002, 0.016] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.007 [-0.017, 0.003] | 0.010 [-0.003, 0.025] | -0.008 [-0.016, 0.001] |
| ordinary | 1603 | -0.000 [-0.002, 0.002] | 0.001 [-0.001, 0.003] | -0.001 [-0.003, 0.001] |
| quarter_end | 31 | 0.006 [-0.031, 0.049] | 0.011 [-0.043, 0.069] | 0.025 [-0.010, 0.065] |
| tax_date | 89 | -0.001 [-0.034, 0.034] | 0.029 [0.008, 0.053] | -0.003 [-0.018, 0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.002] | -0.000 [-0.001, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | -0.001 [-0.001, -0.000] | 0.002 [-0.002, 0.008] | 0.001 [-0.001, 0.004] |
| 2 | 41 | 0.040 [–] | 0.052 [–] | 0.033 [–] |
| 3 | 478 | -0.006 [-0.016, 0.004] | 0.008 [-0.001, 0.017] | -0.009 [-0.017, -0.001] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.267, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.350, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.556, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | -0.190 [-0.348, -0.053] |

## spread_q_gbm+settle+h41+dist_roll against risk_gbm+settle+h41+dist_roll

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.003, 0.002] |
| 2 | 0.001 [-0.001, 0.003] |
| 3 | 0.002 [0.000, 0.004] |
| 4 | -0.000 [-0.002, 0.001] |
| 5 | -0.001 [-0.002, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.008 [-0.015, -0.000] | 0.005 [-0.001, 0.011] | -0.006 [-0.012, 0.000] |
| 2020 | 251 | -0.002 [-0.004, -0.000] | -0.001 [-0.004, 0.003] | -0.001 [-0.005, 0.003] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] |
| 2024 | 250 | 0.000 [-0.002, 0.001] | -0.002 [-0.006, 0.000] | 0.001 [-0.000, 0.002] |
| 2025-26 | 249 | 0.012 [0.001, 0.024] | 0.011 [0.001, 0.023] | 0.005 [-0.003, 0.015] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.005 [-0.015, 0.006] | 0.008 [-0.003, 0.020] | -0.009 [-0.017, -0.003] |
| ordinary | 1603 | 0.001 [-0.001, 0.002] | 0.001 [-0.000, 0.002] | -0.000 [-0.001, 0.001] |
| quarter_end | 31 | -0.018 [-0.039, 0.003] | 0.013 [-0.032, 0.057] | 0.014 [-0.019, 0.055] |
| tax_date | 89 | -0.004 [-0.029, 0.024] | 0.013 [-0.011, 0.042] | -0.001 [-0.022, 0.025] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | -0.001 [-0.001, 0.000] | -0.000 [-0.001, 0.000] |
| 1 | 313 | -0.001 [-0.001, -0.000] | -0.001 [-0.003, 0.000] | -0.003 [-0.004, -0.001] |
| 2 | 41 | 0.045 [–] | 0.051 [–] | 0.028 [–] |
| 3 | 478 | -0.005 [-0.012, 0.003] | 0.005 [-0.000, 0.012] | -0.003 [-0.009, 0.004] |

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

## spread_q_gbm+two_part+settle+h41+dist_roll against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.026 [0.018, 0.036] |
| 2 | 0.023 [0.017, 0.029] |
| 3 | 0.021 [0.015, 0.028] |
| 4 | 0.021 [0.015, 0.028] |
| 5 | 0.020 [0.014, 0.027] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.056 [0.028, 0.087] | 0.036 [0.017, 0.057] | 0.034 [0.013, 0.058] |
| 2020 | 251 | 0.031 [0.018, 0.042] | 0.034 [0.024, 0.044] | 0.031 [0.022, 0.040] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.013 [0.012, 0.015] | 0.013 [0.012, 0.015] |
| 2024 | 250 | -0.001 [-0.009, 0.005] | -0.001 [-0.006, 0.004] | -0.001 [-0.006, 0.003] |
| 2025-26 | 249 | 0.041 [0.010, 0.083] | 0.032 [0.006, 0.065] | 0.029 [0.003, 0.060] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.055 [0.031, 0.084] | 0.044 [0.025, 0.066] | 0.044 [0.026, 0.065] |
| ordinary | 1603 | 0.019 [0.011, 0.028] | 0.014 [0.009, 0.020] | 0.013 [0.007, 0.019] |
| quarter_end | 31 | 0.131 [0.051, 0.211] | 0.120 [0.042, 0.205] | 0.119 [0.041, 0.199] |
| tax_date | 89 | 0.068 [0.047, 0.092] | 0.082 [0.060, 0.105] | 0.078 [0.057, 0.098] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.007 [0.005, 0.010] | 0.007 [0.005, 0.010] | 0.008 [0.006, 0.010] |
| 1 | 313 | 0.031 [0.025, 0.037] | 0.029 [0.022, 0.036] | 0.030 [0.023, 0.036] |
| 2 | 41 | 0.076 [–] | 0.080 [–] | 0.089 [–] |
| 3 | 478 | 0.059 [0.032, 0.089] | 0.042 [0.025, 0.059] | 0.035 [0.018, 0.054] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.308 [0.133, 0.500] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 1.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.417 [0.143, 0.667] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.238 [0.062, 0.429] |

## spread_q_gbm+two_part+settle+h41+dist_roll against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.003, 0.005] |
| 2 | 0.008 [0.003, 0.015] |
| 3 | 0.010 [0.004, 0.018] |
| 4 | 0.011 [0.004, 0.020] |
| 5 | 0.013 [0.006, 0.022] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.001 [-0.011, 0.013] | 0.035 [0.012, 0.061] | 0.047 [0.023, 0.074] |
| 2020 | 251 | -0.002 [-0.010, 0.004] | -0.005 [-0.009, -0.001] | -0.004 [-0.009, 0.000] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] |
| 2024 | 250 | -0.005 [-0.011, -0.001] | -0.005 [-0.009, -0.001] | -0.002 [-0.005, 0.001] |
| 2025-26 | 249 | 0.013 [-0.004, 0.036] | 0.035 [0.004, 0.074] | 0.034 [0.002, 0.073] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.007 [-0.002, 0.018] | 0.033 [0.011, 0.058] | 0.035 [0.013, 0.062] |
| ordinary | 1603 | 0.000 [-0.004, 0.004] | 0.006 [0.000, 0.012] | 0.008 [0.002, 0.016] |
| quarter_end | 31 | 0.000 [-0.013, 0.013] | 0.032 [-0.010, 0.079] | 0.030 [-0.005, 0.073] |
| tax_date | 89 | 0.001 [-0.008, 0.010] | 0.043 [0.016, 0.076] | 0.051 [0.018, 0.087] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.002 [-0.004, -0.001] | -0.002 [-0.004, -0.001] | -0.002 [-0.002, -0.001] |
| 1 | 313 | 0.003 [0.001, 0.004] | -0.002 [-0.004, -0.000] | 0.002 [-0.002, 0.007] |
| 2 | 41 | 0.030 [–] | 0.094 [–] | 0.109 [–] |
| 3 | 478 | 0.004 [-0.008, 0.017] | 0.038 [0.018, 0.061] | 0.044 [0.021, 0.067] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [0.000, 0.250] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 1.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.000, 0.500] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.143 [0.000, 0.300] |

## spread_q_gbm+two_part+settle+h41+dist_roll against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.006, 0.016] |
| 2 | 0.013 [0.008, 0.018] |
| 3 | 0.015 [0.010, 0.020] |
| 4 | 0.012 [0.007, 0.017] |
| 5 | 0.013 [0.008, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.039 [0.021, 0.059] | 0.036 [0.019, 0.054] | 0.037 [0.018, 0.057] |
| 2020 | 251 | 0.007 [0.001, 0.012] | 0.022 [0.015, 0.027] | 0.014 [0.008, 0.019] |
| 2021-23 | 748 | 0.000 [-0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.001, 0.002] |
| 2024 | 250 | -0.000 [-0.004, 0.004] | -0.001 [-0.005, 0.002] | -0.000 [-0.003, 0.001] |
| 2025-26 | 249 | 0.016 [0.001, 0.031] | 0.026 [0.006, 0.052] | 0.021 [0.004, 0.040] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.034 [0.017, 0.052] | 0.035 [0.016, 0.055] | 0.035 [0.015, 0.056] |
| ordinary | 1603 | 0.006 [0.002, 0.010] | 0.010 [0.006, 0.014] | 0.007 [0.003, 0.011] |
| quarter_end | 31 | 0.071 [0.010, 0.135] | 0.085 [0.035, 0.146] | 0.093 [0.034, 0.159] |
| tax_date | 89 | 0.033 [0.013, 0.055] | 0.054 [0.024, 0.090] | 0.052 [0.020, 0.091] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.000] | 0.001 [-0.000, 0.002] | 0.000 [-0.001, 0.001] |
| 1 | 313 | 0.008 [0.006, 0.011] | 0.018 [0.014, 0.021] | 0.015 [0.011, 0.019] |
| 2 | 41 | 0.043 [–] | 0.047 [–] | 0.032 [–] |
| 3 | 478 | 0.035 [0.020, 0.051] | 0.041 [0.025, 0.057] | 0.037 [0.021, 0.054] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.308 [0.143, 0.484] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.276] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.333 [0.111, 0.571] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 1.000 [–] |
| 3 | 21 | 0.238 [0.080, 0.429] |

## spread_q_gbm+two_part+settle+h41+dist_roll against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.002, 0.023] |
| 2 | 0.020 [0.010, 0.031] |
| 3 | 0.017 [0.008, 0.028] |
| 4 | 0.017 [0.007, 0.028] |
| 5 | 0.019 [0.009, 0.030] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.054 [0.012, 0.098] | 0.073 [0.035, 0.112] | 0.072 [0.032, 0.116] |
| 2020 | 251 | -0.009 [-0.019, -0.001] | -0.004 [-0.009, 0.001] | -0.005 [-0.012, 0.002] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] |
| 2024 | 250 | -0.004 [-0.010, -0.000] | -0.004 [-0.009, -0.001] | -0.002 [-0.005, 0.000] |
| 2025-26 | 249 | 0.026 [0.002, 0.057] | 0.031 [0.003, 0.065] | 0.043 [0.009, 0.086] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.001 [-0.013, 0.017] | 0.017 [0.002, 0.035] | 0.030 [0.010, 0.055] |
| ordinary | 1603 | 0.014 [0.003, 0.026] | 0.016 [0.006, 0.027] | 0.015 [0.005, 0.027] |
| quarter_end | 31 | 0.015 [-0.021, 0.060] | 0.042 [-0.008, 0.101] | 0.056 [0.023, 0.093] |
| tax_date | 89 | -0.000 [-0.031, 0.033] | 0.029 [0.007, 0.053] | 0.052 [0.018, 0.090] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.002 [-0.003, -0.000] | -0.002 [-0.003, -0.001] | -0.001 [-0.002, -0.001] |
| 1 | 313 | -0.001 [-0.001, -0.000] | -0.002 [-0.004, -0.000] | 0.001 [-0.002, 0.006] |
| 2 | 41 | 0.087 [–] | 0.104 [–] | 0.120 [–] |
| 3 | 478 | 0.045 [0.009, 0.084] | 0.064 [0.032, 0.097] | 0.066 [0.035, 0.102] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.269 [0.120, 0.423] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.357] |
| 2020 | 2 | 1.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.500 [0.222, 0.750] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.667 [–] |
| 3 | 21 | 0.238 [0.074, 0.417] |

## spread_q_gbm+two_part+settle+h41+dist_roll against risk_gbm+every_day+gate+settle+h41+iorb+tailcap75

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.002, 0.021] |
| 2 | 0.010 [0.003, 0.018] |
| 3 | 0.011 [0.004, 0.020] |
| 4 | 0.008 [0.001, 0.016] |
| 5 | 0.007 [0.000, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.052 [0.011, 0.096] | 0.043 [0.014, 0.077] | 0.025 [-0.003, 0.058] |
| 2020 | 251 | -0.011 [-0.025, -0.002] | 0.001 [-0.006, 0.010] | 0.001 [-0.005, 0.008] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | -0.002 [-0.008, 0.004] | -0.005 [-0.009, -0.001] | -0.002 [-0.005, 0.002] |
| 2025-26 | 249 | 0.024 [-0.000, 0.053] | 0.025 [0.000, 0.058] | 0.018 [-0.006, 0.049] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.001 [-0.012, 0.017] | 0.013 [-0.001, 0.028] | -0.002 [-0.011, 0.009] |
| ordinary | 1603 | 0.013 [0.002, 0.025] | 0.010 [0.003, 0.019] | 0.008 [0.000, 0.017] |
| quarter_end | 31 | 0.006 [-0.029, 0.051] | 0.011 [-0.042, 0.070] | 0.025 [-0.012, 0.066] |
| tax_date | 89 | -0.001 [-0.032, 0.035] | 0.029 [0.008, 0.053] | -0.003 [-0.017, 0.009] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.003, -0.000] | -0.002 [-0.003, -0.000] | -0.001 [-0.002, -0.001] |
| 1 | 313 | -0.001 [-0.001, -0.001] | 0.001 [-0.003, 0.007] | 0.001 [-0.002, 0.003] |
| 2 | 41 | 0.079 [–] | 0.110 [–] | 0.094 [–] |
| 3 | 478 | 0.042 [0.006, 0.079] | 0.038 [0.015, 0.066] | 0.023 [-0.001, 0.050] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [0.000, 0.172] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [0.000, 0.357] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.048 [0.000, 0.136] |

## spread_q_gbm+two_part+settle+h41+dist_roll against risk_gbm+settle+h41+dist_roll

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.002, 0.022] |
| 2 | 0.010 [0.002, 0.020] |
| 3 | 0.010 [0.003, 0.019] |
| 4 | 0.008 [0.001, 0.016] |
| 5 | 0.008 [0.001, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.051 [0.011, 0.095] | 0.044 [0.014, 0.077] | 0.032 [0.000, 0.065] |
| 2020 | 251 | -0.010 [-0.018, -0.003] | -0.004 [-0.008, 0.000] | -0.002 [-0.007, 0.005] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] | -0.000 [-0.001, -0.000] |
| 2024 | 250 | -0.004 [-0.009, 0.000] | -0.005 [-0.010, -0.001] | -0.002 [-0.005, 0.001] |
| 2025-26 | 249 | 0.025 [0.001, 0.056] | 0.020 [-0.002, 0.048] | 0.015 [-0.007, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.010, 0.019] | 0.011 [-0.000, 0.024] | -0.003 [-0.013, 0.009] |
| ordinary | 1603 | 0.014 [0.003, 0.026] | 0.010 [0.002, 0.019] | 0.009 [0.001, 0.019] |
| quarter_end | 31 | -0.018 [-0.042, 0.003] | 0.013 [-0.035, 0.060] | 0.014 [-0.019, 0.054] |
| tax_date | 89 | -0.004 [-0.030, 0.024] | 0.013 [-0.011, 0.043] | -0.001 [-0.022, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.002 [-0.003, -0.001] | -0.002 [-0.004, -0.001] | -0.001 [-0.002, -0.001] |
| 1 | 313 | -0.001 [-0.002, -0.001] | -0.002 [-0.004, -0.000] | -0.003 [-0.005, -0.002] |
| 2 | 41 | 0.085 [–] | 0.109 [–] | 0.089 [–] |
| 3 | 478 | 0.043 [0.010, 0.081] | 0.036 [0.012, 0.063] | 0.028 [0.003, 0.055] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.192 [0.056, 0.356] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.364] |
| 2020 | 2 | 1.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.417 [0.143, 0.668] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.238 [0.071, 0.429] |


## Predicted against realised rate of a pressure day (+5 bp), by regime and day type, pooled over h = 1 to 5

### ngboost_laplace

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0539 | 0.0741 |
| day type month_end | 750 | 0.0566 | 0.1133 |
| day type ordinary | 8009 | 0.0514 | 0.0627 |
| day type quarter_end | 151 | 0.1082 | 0.2715 |
| day type tax_date | 445 | 0.0759 | 0.1461 |
| regime 2018-19 | 1865 | 0.2217 | 0.2697 |
| regime 2020 | 1255 | 0.0456 | 0.0159 |
| regime 2021-23 | 3740 | 0.0005 | 0.0000 |
| regime 2024 | 1250 | 0.0021 | 0.0200 |
| regime 2025-26 | 1245 | 0.0229 | 0.1165 |

### risk_gbm

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0176 | 0.0741 |
| day type month_end | 750 | 0.0780 | 0.1133 |
| day type ordinary | 8009 | 0.0042 | 0.0627 |
| day type quarter_end | 151 | 0.1467 | 0.2715 |
| day type tax_date | 445 | 0.1138 | 0.1461 |
| regime 2018-19 | 1865 | 0.0637 | 0.2697 |
| regime 2020 | 1255 | 0.0128 | 0.0159 |
| regime 2021-23 | 3740 | 0.0005 | 0.0000 |
| regime 2024 | 1250 | 0.0013 | 0.0200 |
| regime 2025-26 | 1245 | 0.0212 | 0.1165 |

### risk_gbm+every_day+gate+settle+h41+iorb+tailcap75

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0308 | 0.0741 |
| day type month_end | 750 | 0.0920 | 0.1133 |
| day type ordinary | 8009 | 0.0171 | 0.0627 |
| day type quarter_end | 151 | 0.1996 | 0.2715 |
| day type tax_date | 445 | 0.1168 | 0.1461 |
| regime 2018-19 | 1865 | 0.1114 | 0.2697 |
| regime 2020 | 1255 | 0.0213 | 0.0159 |
| regime 2021-23 | 3740 | 0.0038 | 0.0000 |
| regime 2024 | 1250 | 0.0014 | 0.0200 |
| regime 2025-26 | 1245 | 0.0302 | 0.1165 |

### risk_gbm+settle+h41

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0264 | 0.0741 |
| day type month_end | 750 | 0.0915 | 0.1133 |
| day type ordinary | 8009 | 0.0120 | 0.0627 |
| day type quarter_end | 151 | 0.1996 | 0.2715 |
| day type tax_date | 445 | 0.1168 | 0.1461 |
| regime 2018-19 | 1865 | 0.0963 | 0.2697 |
| regime 2020 | 1255 | 0.0205 | 0.0159 |
| regime 2021-23 | 3740 | 0.0006 | 0.0000 |
| regime 2024 | 1250 | 0.0013 | 0.0200 |
| regime 2025-26 | 1245 | 0.0301 | 0.1165 |

### risk_gbm+settle+h41+dist_roll

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0254 | 0.0741 |
| day type month_end | 750 | 0.0909 | 0.1133 |
| day type ordinary | 8009 | 0.0111 | 0.0627 |
| day type quarter_end | 151 | 0.1899 | 0.2715 |
| day type tax_date | 445 | 0.1167 | 0.1461 |
| regime 2018-19 | 1865 | 0.0888 | 0.2697 |
| regime 2020 | 1255 | 0.0112 | 0.0159 |
| regime 2021-23 | 3740 | 0.0007 | 0.0000 |
| regime 2024 | 1250 | 0.0030 | 0.0200 |
| regime 2025-26 | 1245 | 0.0418 | 0.1165 |

### spread_q_gbm+settle+h41+dist_roll

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0272 | 0.0741 |
| day type month_end | 750 | 0.1055 | 0.1133 |
| day type ordinary | 8009 | 0.0120 | 0.0627 |
| day type quarter_end | 151 | 0.1807 | 0.2715 |
| day type tax_date | 445 | 0.1170 | 0.1461 |
| regime 2018-19 | 1865 | 0.0762 | 0.2697 |
| regime 2020 | 1255 | 0.0232 | 0.0159 |
| regime 2021-23 | 3740 | 0.0074 | 0.0000 |
| regime 2024 | 1250 | 0.0064 | 0.0200 |
| regime 2025-26 | 1245 | 0.0380 | 0.1165 |

### spread_q_gbm+two_part+settle+h41+dist_roll

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0701 | 0.0741 |
| day type month_end | 750 | 0.1123 | 0.1133 |
| day type ordinary | 8009 | 0.0615 | 0.0627 |
| day type quarter_end | 151 | 0.1807 | 0.2715 |
| day type tax_date | 445 | 0.1170 | 0.1461 |
| regime 2018-19 | 1865 | 0.2168 | 0.2697 |
| regime 2020 | 1255 | 0.0569 | 0.0159 |
| regime 2021-23 | 3740 | 0.0084 | 0.0000 |
| regime 2024 | 1250 | 0.0203 | 0.0200 |
| regime 2025-26 | 1245 | 0.0992 | 0.1165 |

