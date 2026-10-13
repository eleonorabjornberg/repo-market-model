# Reserves projected to the scored day (#545)

# projected_reserves

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| projected_reserves | 8 / 2.50 fail | fail | 8 / 3.85 fail | 0 / 0.67 fail |
| risk_gbm | 13 / 1.35 pass | pass (h = 1) | 13 / 2.00 pass | 3 / 1.56 fail |
| risk_gbm_base | 14 / 1.50 pass | pass (h = 1) | 14 / 2.04 fail | 4 / 2.00 fail |
| risk_logistic | 14 / 1.85 pass | pass (h = 1) | 14 / 2.42 fail | 4 / 2.89 fail |
| risk_logistic_base | 13 / 1.77 pass | pass (h = 1) | 13 / 2.04 fail | 3 / 2.33 fail |
| risk_quantile_skewt_base | 14 / 1.88 pass | pass (h = 1) | 14 / 2.54 fail | 4 / 3.22 fail |
| ngboost_laplace | 15 / 2.54 fail | fail | 15 / 4.38 fail | 4 / 0.33 fail |
| calendar_climatology | 10 / 5.00 fail | fail | 10 / 5.38 fail | 0 / 3.78 fail |
| persistence_logistic | 7 / 3.42 fail | fail | 7 / 5.73 fail | 0 / 2.22 fail |

## Tier 1 under weighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| projected_reserves | 12 / 2.14 fail | fail | 12 / 2.84 fail | 0 / 0.89 fail |
| risk_gbm | 13 / 0.80 pass | pass (h = 1) | 13 / 1.48 pass | 3 / 1.61 fail |
| risk_gbm_base | 14 / 0.97 pass | pass (h = 1) | 14 / 1.59 pass | 4 / 2.06 fail |
| risk_logistic | 16 / 1.74 pass | pass (h = 1) | 16 / 2.55 fail | 6 / 4.39 fail |
| risk_logistic_base | 15 / 1.65 pass | pass (h = 1) | 15 / 2.18 fail | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass (h = 1) | 15 / 2.14 fail | 5 / 3.81 fail |
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 5 / 0.50 fail |
| calendar_climatology | 12 / 3.75 fail | fail | 12 / 3.90 fail | 0 / 4.56 fail |
| persistence_logistic | 12 / 3.25 fail | fail | 12 / 4.09 fail | 1 / 2.86 fail |

## The judge's tables under the unweighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.38 flat / 2.98 weighted (tier 1 on the flat count) | 2.4 / 4.4 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.269 | 5.73 flat / 2.23 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.250 | 4.38 flat / 1.84 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_reserves | 8 of 26 | 0.308 [0.156, 0.471] | 0.231 | 3.85 flat / 1.65 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.00 flat / 1.37 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+projected | 11 of 26 | 0.423 [0.240, 0.600] | 0.231 | 3.85 flat / 1.82 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted (tier 1 on the flat count) | 1.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 2.04 flat / 1.41 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.231 | 2.54 flat / 1.80 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |

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

projected_reserves:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.091, 0.370] | 2.346 [1.323, 3.737] | 0.817 [0.450, 1.313] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.095, 0.389] | 1.885 [0.900, 3.300] | 0.750 [0.360, 1.324] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 1.462 [0.697, 2.601] | 0.663 [0.281, 1.238] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.500 [1.312, 4.147] | 1.048 [0.558, 1.736] |
| lead 5 alone (fail) | 26 | 6 | 0.231 [0.103, 0.375] | 2.038 [1.000, 3.500] | 0.865 [0.424, 1.500] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.263, 0.692] | 5.353 [3.385, 8.267] | 2.044 [1.240, 3.225] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 1.000 [0.000, 3.154] | 0.917 [0.000, 2.959] |

Recall with equal weight per regime: 0.118 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

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

risk_gbm+projected:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.211, 0.556] | 1.077 [0.435, 1.955] | 0.404 [0.183, 0.710] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.222] | 2.231 [1.194, 3.643] | 0.981 [0.480, 1.670] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.419] | 2.308 [1.268, 3.667] | 1.038 [0.537, 1.706] |
| lead 4 alone (fail) | 26 | 5 | 0.192 [0.067, 0.333] | 2.077 [0.896, 3.611] | 0.942 [0.413, 1.632] |
| lead 5 alone (fail) | 26 | 3 | 0.115 [0.000, 0.227] | 2.269 [1.111, 3.750] | 0.981 [0.440, 1.698] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.286, 0.765] | 5.118 [3.000, 8.063] | 2.147 [1.172, 3.517] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.194 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

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

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| projected_reserves | 0.62 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.44 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+projected | 0.41 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.32 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| projected_reserves | +0.0352 [-0.0021, +0.0787] | +0.0217 [+0.0065, +0.0360] | +0.0138 [+0.0121, +0.0156] | +0.0021 [-0.0020, +0.0053] | +0.0134 [+0.0049, +0.0234] | +0.0330 [+0.0127, +0.0563] | +0.0124 [+0.0047, +0.0213] | +0.0859 [+0.0399, +0.1290] | +0.0591 [+0.0226, +0.0966] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+projected | +0.0483 [+0.0117, +0.0907] | +0.0274 [+0.0157, +0.0392] | +0.0138 [+0.0121, +0.0156] | +0.0037 [+0.0001, +0.0068] | +0.0249 [+0.0023, +0.0539] | +0.0596 [+0.0349, +0.0851] | +0.0149 [+0.0066, +0.0244] | +0.1155 [+0.0348, +0.1930] | +0.0686 [+0.0413, +0.0967] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_reserves | 12 of 26 | 0.462 [0.267, 0.654] | 0.274 | 5.85 flat / 2.84 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+projected | 13 of 26 | 0.500 [0.308, 0.692] | 0.271 | 5.81 flat / 2.90 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted (tier 1 on the weighted count) | 2.9 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.231 | 2.88 flat / 2.18 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 2.88 flat / 2.14 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |

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

projected_reserves:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.238, 0.611] | 4.769 [3.000, 7.154] | 2.144 [1.273, 3.355] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.143, 0.474] | 3.154 [1.750, 5.161] | 1.654 [0.839, 2.869] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.176, 0.522] | 3.731 [2.125, 5.942] | 1.837 [0.975, 3.141] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 4.077 [2.367, 6.421] | 1.913 [1.060, 3.130] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.158, 0.476] | 3.731 [2.081, 6.040] | 1.692 [0.879, 2.844] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.458, 0.929] | 7.824 [5.100, 11.895] | 3.338 [2.000, 5.375] |
| outside 2018-2019 | 9 | 0 | 0.000 [0.000, 0.000] | 2.111 [0.500, 5.750] | 1.889 [0.368, 5.333] |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

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

risk_gbm+projected:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.269, 0.650] | 3.192 [1.692, 5.112] | 1.529 [0.794, 2.533] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.600] | 4.538 [2.764, 6.800] | 2.106 [1.202, 3.300] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.211, 0.556] | 4.269 [2.484, 6.476] | 1.971 [1.100, 3.135] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.241, 0.607] | 4.154 [2.423, 6.354] | 1.923 [1.062, 3.060] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.167, 0.524] | 4.192 [2.392, 6.501] | 1.875 [0.974, 3.036] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.889] | 7.294 [4.571, 11.084] | 3.176 [1.803, 5.091] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.000 (no interval) | 2.389 (no interval) |

Recall with equal weight per regime: 0.262 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

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

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| projected_reserves | 0.80 (102) | 0.00 (4) | – | 0.00 (5) | 0.10 (29) | 0.59 (17) | 0.62 (101) | 0.44 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+projected | 0.60 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.51 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| projected_reserves | +0.0352 [-0.0021, +0.0787] | +0.0217 [+0.0065, +0.0360] | +0.0138 [+0.0121, +0.0156] | +0.0021 [-0.0020, +0.0053] | +0.0134 [+0.0049, +0.0234] | +0.0330 [+0.0127, +0.0563] | +0.0124 [+0.0047, +0.0213] | +0.0859 [+0.0399, +0.1290] | +0.0591 [+0.0226, +0.0966] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+projected | +0.0483 [+0.0117, +0.0907] | +0.0274 [+0.0157, +0.0392] | +0.0138 [+0.0121, +0.0156] | +0.0037 [+0.0001, +0.0068] | +0.0249 [+0.0023, +0.0539] | +0.0596 [+0.0349, +0.0851] | +0.0149 [+0.0066, +0.0244] | +0.1155 [+0.0348, +0.1930] | +0.0686 [+0.0413, +0.0967] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| projected_reserves | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

## Onsets only this row warns

projected_reserves warns 12 of 26 onsets; at least one of the five passers warns 16. 3 are warned by projected_reserves and by none of the five passers:

* 2019-05-28 (flagged at h = 4)
* 2019-06-25 (flagged at h = 1, 2, 3, 4)
* 2019-08-13 (flagged at h = 1, 3, 4, 5)

Warned by a passer and not by projected_reserves: 2019-01-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

## Constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 4 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 2 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 3 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 4 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 2 | 0 of 1869 | 1869 |

## projected_reserves against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.007, 0.015] |
| 2 | 0.010 [-0.001, 0.022] |
| 3 | 0.004 [-0.007, 0.018] |
| 4 | 0.007 [-0.005, 0.019] |
| 5 | 0.008 [-0.003, 0.021] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.034 [-0.018, 0.086] | 0.045 [-0.010, 0.102] | 0.042 [-0.010, 0.099] |
| 2020 | 251 | -0.018 [-0.034, -0.005] | -0.031 [-0.059, -0.007] | -0.017 [-0.034, -0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.002 [-0.006, 0.001] | -0.002 [-0.007, 0.001] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.002 [-0.021, 0.013] | -0.001 [-0.013, 0.009] | 0.017 [0.004, 0.032] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.041, -0.004] | -0.007 [-0.029, 0.016] | 0.004 [-0.012, 0.020] |
| ordinary | 1603 | 0.008 [-0.003, 0.019] | 0.007 [-0.005, 0.021] | 0.008 [-0.004, 0.021] |
| quarter_end | 31 | -0.030 [-0.114, 0.053] | -0.013 [-0.103, 0.084] | 0.014 [-0.045, 0.071] |
| tax_date | 89 | -0.009 [-0.056, 0.036] | -0.016 [-0.044, 0.011] | 0.017 [-0.021, 0.063] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.002] | -0.000 [-0.001, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | -0.000 [-0.000, 0.000] | -0.003 [-0.010, 0.000] | -0.001 [-0.006, 0.002] |
| 2 | 41 | -0.015 [–] | -0.045 [–] | 0.011 [–] |
| 3 | 478 | 0.016 [-0.025, 0.062] | 0.024 [-0.021, 0.073] | 0.032 [-0.011, 0.078] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.214, 0.148] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [-0.077, 0.316] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [-0.231, 0.400] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | 0.000 [-0.211, 0.217] |

## projected_reserves against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.014, -0.002] |
| 2 | -0.002 [-0.008, 0.005] |
| 3 | -0.003 [-0.012, 0.006] |
| 4 | 0.001 [-0.007, 0.011] |
| 5 | 0.002 [-0.006, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.045, 0.010] | 0.007 [-0.033, 0.051] | 0.017 [-0.022, 0.061] |
| 2020 | 251 | -0.011 [-0.027, 0.001] | -0.032 [-0.060, -0.009] | -0.016 [-0.030, -0.005] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | -0.002 [-0.005, -0.000] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.015 [-0.030, -0.003] | 0.003 [0.000, 0.007] | 0.008 [0.002, 0.015] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.034, 0.005] | 0.009 [-0.012, 0.034] | 0.008 [-0.007, 0.026] |
| ordinary | 1603 | -0.006 [-0.011, -0.001] | -0.003 [-0.011, 0.004] | 0.001 [-0.006, 0.009] |
| quarter_end | 31 | -0.045 [-0.137, 0.041] | -0.023 [-0.140, 0.093] | -0.012 [-0.086, 0.055] |
| tax_date | 89 | -0.008 [-0.045, 0.030] | -0.002 [-0.041, 0.039] | 0.016 [-0.035, 0.078] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.002, 0.000] | -0.000 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | -0.004 [-0.011, 0.000] | -0.001 [-0.005, 0.002] |
| 2 | 41 | -0.072 [–] | -0.055 [–] | -0.001 [–] |
| 3 | 478 | -0.025 [-0.047, -0.002] | -0.003 [-0.034, 0.032] | 0.010 [-0.023, 0.045] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.379, -0.029] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.143, 0.143] |
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
| 3 | 21 | -0.095 [-0.273, 0.062] |

## projected_reserves against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.018 [0.010, 0.026] |
| 2 | 0.012 [0.004, 0.021] |
| 3 | 0.008 [-0.000, 0.018] |
| 4 | 0.011 [0.002, 0.020] |
| 5 | 0.010 [0.001, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.035 [-0.002, 0.077] | 0.009 [-0.032, 0.051] | 0.005 [-0.034, 0.046] |
| 2020 | 251 | 0.022 [0.005, 0.035] | 0.007 [-0.020, 0.029] | 0.019 [0.004, 0.033] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.002 [-0.002, 0.005] | 0.001 [-0.004, 0.005] | 0.002 [-0.003, 0.005] |
| 2025-26 | 249 | 0.013 [0.005, 0.024] | 0.001 [-0.003, 0.004] | 0.002 [-0.001, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.033 [0.014, 0.055] | 0.020 [0.002, 0.041] | 0.017 [0.002, 0.032] |
| ordinary | 1603 | 0.012 [0.005, 0.021] | 0.005 [-0.004, 0.014] | 0.006 [-0.003, 0.015] |
| quarter_end | 31 | 0.086 [0.038, 0.130] | 0.065 [0.018, 0.114] | 0.078 [0.021, 0.131] |
| tax_date | 89 | 0.059 [0.020, 0.097] | 0.037 [-0.001, 0.073] | 0.043 [0.004, 0.085] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.028 [0.021, 0.034] | 0.027 [0.020, 0.034] |
| 2 | 41 | -0.026 [–] | -0.069 [–] | -0.020 [–] |
| 3 | 478 | 0.030 [0.000, 0.063] | 0.001 [-0.032, 0.036] | 0.001 [-0.029, 0.033] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.087, 0.088] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.133, 0.143] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.107, 0.111] |

## projected_reserves against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.004, 0.010] |
| 2 | 0.002 [-0.006, 0.011] |
| 3 | 0.002 [-0.007, 0.011] |
| 4 | 0.002 [-0.006, 0.011] |
| 5 | 0.002 [-0.006, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.018 [-0.012, 0.050] | 0.009 [-0.032, 0.049] | 0.007 [-0.030, 0.045] |
| 2020 | 251 | -0.002 [-0.016, 0.010] | -0.005 [-0.033, 0.019] | 0.001 [-0.015, 0.015] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | 0.001 [-0.000, 0.003] | 0.002 [0.000, 0.004] |
| 2025-26 | 249 | -0.012 [-0.035, 0.006] | -0.005 [-0.024, 0.009] | -0.005 [-0.027, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.014, 0.041] | 0.011 [-0.012, 0.035] | 0.008 [-0.010, 0.027] |
| ordinary | 1603 | -0.000 [-0.005, 0.005] | 0.000 [-0.007, 0.008] | -0.000 [-0.008, 0.007] |
| quarter_end | 31 | 0.025 [-0.087, 0.135] | 0.031 [-0.083, 0.142] | 0.052 [-0.041, 0.149] |
| tax_date | 89 | 0.024 [-0.012, 0.069] | 0.009 [-0.037, 0.056] | 0.017 [-0.035, 0.078] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.001, 0.002] | 0.003 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.016 [0.009, 0.022] | 0.012 [0.007, 0.017] |
| 2 | 41 | -0.059 [–] | -0.102 [–] | -0.077 [–] |
| 3 | 478 | 0.006 [-0.019, 0.033] | 0.000 [-0.031, 0.033] | 0.003 [-0.026, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.097, 0.091] on 26 onsets.

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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.120, 0.115] |


# risk_gbm+projected

## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| risk_gbm+projected | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

## Onsets only this row warns

risk_gbm+projected warns 13 of 26 onsets; at least one of the five passers warns 16. 3 are warned by risk_gbm+projected and by none of the five passers:

* 2019-05-28 (flagged at h = 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_gbm+projected: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

## Constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 2 | 0 of 1873 | 1850 |
| 2 | 90 | 0 | 0 | 7 | 5 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 4 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 4 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 5 | 0 of 1869 | 1829 |

## risk_gbm+projected against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.009 [-0.001, 0.020] |
| 2 | 0.010 [-0.001, 0.021] |
| 3 | 0.007 [-0.004, 0.019] |
| 4 | 0.008 [-0.002, 0.020] |
| 5 | 0.007 [-0.003, 0.019] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [-0.001, 0.097] | 0.045 [-0.008, 0.103] | 0.039 [-0.012, 0.097] |
| 2020 | 251 | -0.012 [-0.022, -0.003] | -0.022 [-0.043, -0.004] | -0.011 [-0.023, -0.001] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.009 [0.001, 0.020] | 0.005 [0.001, 0.010] | 0.006 [0.001, 0.012] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.005 [-0.001, 0.016] | -0.001 [-0.013, 0.012] | -0.001 [-0.013, 0.010] |
| ordinary | 1603 | 0.010 [-0.002, 0.022] | 0.008 [-0.005, 0.022] | 0.008 [-0.003, 0.022] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | -0.000 [-0.000, -0.000] | -0.001 [-0.003, 0.000] | -0.000 [-0.000, -0.000] |
| 2 | 41 | -0.009 [–] | -0.055 [–] | -0.006 [–] |
| 3 | 478 | 0.036 [-0.003, 0.078] | 0.031 [-0.011, 0.079] | 0.029 [-0.012, 0.076] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.167, 0.174] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.190, 0.300] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.125, 0.455] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | 0.048 [-0.150, 0.250] |

## risk_gbm+projected against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.008, 0.003] |
| 2 | -0.002 [-0.008, 0.003] |
| 3 | -0.001 [-0.008, 0.008] |
| 4 | 0.003 [-0.004, 0.011] |
| 5 | 0.001 [-0.006, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.031, 0.019] | 0.006 [-0.026, 0.043] | 0.015 [-0.020, 0.052] |
| 2020 | 251 | -0.005 [-0.017, 0.004] | -0.023 [-0.045, -0.007] | -0.010 [-0.019, -0.003] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, -0.000] | 0.000 [-0.003, 0.004] | 0.000 [-0.001, 0.001] |
| 2025-26 | 249 | -0.004 [-0.015, 0.007] | 0.009 [-0.002, 0.024] | -0.003 [-0.015, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.001, 0.024] | 0.015 [-0.002, 0.035] | 0.004 [-0.008, 0.018] |
| ordinary | 1603 | -0.004 [-0.009, 0.001] | -0.003 [-0.010, 0.005] | 0.002 [-0.006, 0.009] |
| quarter_end | 31 | -0.015 [-0.063, 0.026] | -0.010 [-0.073, 0.049] | -0.026 [-0.082, 0.025] |
| tax_date | 89 | 0.002 [-0.032, 0.031] | 0.015 [-0.010, 0.043] | -0.001 [-0.041, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | -0.002 [-0.004, 0.000] | 0.001 [-0.001, 0.002] |
| 2 | 41 | -0.066 [–] | -0.065 [–] | -0.018 [–] |
| 3 | 478 | -0.005 [-0.024, 0.017] | 0.005 [-0.022, 0.036] | 0.006 [-0.021, 0.037] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.333, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.143] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.091] |

## risk_gbm+projected against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.023 [0.014, 0.032] |
| 2 | 0.012 [0.005, 0.020] |
| 3 | 0.011 [0.003, 0.019] |
| 4 | 0.012 [0.005, 0.020] |
| 5 | 0.008 [0.000, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.048 [0.011, 0.088] | 0.008 [-0.029, 0.048] | 0.002 [-0.036, 0.042] |
| 2020 | 251 | 0.027 [0.015, 0.038] | 0.015 [-0.005, 0.033] | 0.025 [0.014, 0.035] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.004 [-0.000, 0.007] | 0.004 [-0.000, 0.007] | 0.002 [-0.003, 0.005] |
| 2025-26 | 249 | 0.025 [0.003, 0.055] | 0.007 [-0.005, 0.021] | -0.008 [-0.022, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.060 [0.035, 0.085] | 0.027 [0.011, 0.043] | 0.013 [-0.001, 0.024] |
| ordinary | 1603 | 0.015 [0.006, 0.024] | 0.005 [-0.003, 0.015] | 0.006 [-0.002, 0.015] |
| quarter_end | 31 | 0.116 [0.034, 0.195] | 0.078 [-0.009, 0.167] | 0.063 [-0.023, 0.156] |
| tax_date | 89 | 0.069 [0.041, 0.096] | 0.053 [0.026, 0.080] | 0.026 [-0.017, 0.058] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.030 [0.023, 0.036] | 0.028 [0.021, 0.034] |
| 2 | 41 | -0.020 [–] | -0.079 [–] | -0.037 [–] |
| 3 | 478 | 0.050 [0.018, 0.084] | 0.009 [-0.020, 0.041] | -0.003 [-0.033, 0.029] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.118, 0.207] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.238, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.143, 0.250] |

## risk_gbm+projected against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [0.001, 0.015] |
| 2 | 0.002 [-0.005, 0.009] |
| 3 | 0.004 [-0.003, 0.012] |
| 4 | 0.004 [-0.003, 0.011] |
| 5 | 0.001 [-0.007, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [0.003, 0.061] | 0.008 [-0.027, 0.044] | 0.005 [-0.030, 0.039] |
| 2020 | 251 | 0.004 [-0.007, 0.014] | 0.003 [-0.017, 0.020] | 0.008 [-0.002, 0.017] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.004 [0.000, 0.009] | 0.004 [0.001, 0.008] | 0.002 [0.000, 0.003] |
| 2025-26 | 249 | -0.001 [-0.025, 0.021] | 0.001 [-0.021, 0.022] | -0.016 [-0.040, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.038 [0.015, 0.062] | 0.017 [0.000, 0.034] | 0.003 [-0.012, 0.018] |
| ordinary | 1603 | 0.002 [-0.004, 0.009] | 0.001 [-0.007, 0.009] | 0.000 [-0.008, 0.008] |
| quarter_end | 31 | 0.055 [-0.016, 0.132] | 0.044 [-0.013, 0.101] | 0.038 [-0.016, 0.092] |
| tax_date | 89 | 0.033 [-0.001, 0.069] | 0.026 [-0.006, 0.062] | 0.000 [-0.044, 0.045] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.000, 0.002] | 0.003 [0.002, 0.004] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.018 [0.014, 0.022] | 0.014 [0.010, 0.017] |
| 2 | 41 | -0.053 [–] | -0.112 [–] | -0.094 [–] |
| 3 | 478 | 0.026 [0.002, 0.051] | 0.008 [-0.021, 0.037] | -0.001 [-0.029, 0.027] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.077, 0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [0.000, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.182, 0.201] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.091, 0.211] |


## Onsets warned at each horizon (weighted rule, 26 onsets)

The ceiling: 12 of 26 onsets at any single horizon of 2 or more, the risk-date passers' best (docs/pivot/desk-standard.md section 4): the recall of each row at h = 2 to 5 is reported against it.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| projected_reserves | 11 | 8 | 9 | 10 | 8 |
| risk_gbm+projected | 12 | 11 | 10 | 11 | 9 |
| risk_gbm | 13 | 8 | 7 | 7 | 7 |
| risk_gbm_base | 14 | 8 | 7 | 7 | 7 |
| risk_logistic | 14 | 7 | 8 | 10 | 9 |
| risk_logistic_base | 14 | 8 | 7 | 7 | 8 |
| risk_quantile_skewt_base | 15 | 9 | 9 | 9 | 9 |
| calendar_climatology | 12 | 10 | 10 | 10 | 10 |
| persistence_logistic | 11 | 7 | 10 | 8 | 8 |
| ngboost_laplace | 15 | 7 | 9 | 9 | 10 |

## Brier score and log loss at +5 bp (pooled over the scored days; log loss floors a probability at 1e-6)

| row | h = 1: Brier / log loss | h = 2: Brier / log loss | h = 3: Brier / log loss | h = 4: Brier / log loss | h = 5: Brier / log loss |
|---|---|---|---|---|---|
| projected_reserves | 0.0539 / 0.1793 | 0.0588 / 0.1934 | 0.0622 / 0.2067 | 0.0602 / 0.2033 | 0.0614 / 0.2140 |
| risk_gbm+projected | 0.0488 / 0.1720 | 0.0590 / 0.1980 | 0.0601 / 0.2008 | 0.0586 / 0.2011 | 0.0625 / 0.2212 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| calendar_climatology | 0.0714 / 0.2963 | 0.0711 / 0.2954 | 0.0707 / 0.2943 | 0.0708 / 0.2952 | 0.0709 / 0.2958 |
| persistence_logistic | 0.0563 / 0.2014 | 0.0611 / 0.2184 | 0.0644 / 0.2424 | 0.0624 / 0.2254 | 0.0634 / 0.2394 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |

## Projection error against the H.4.1 level of the scored Wednesdays (USD billions)

Error is projected (or carried-forward) minus realised. The comparator carries the as-of level forward unchanged.

| h | Wednesdays | projected: mean | MAE | RMSE | carried forward: mean | MAE | RMSE |
|---|---|---|---|---|---|---|---|
| 1 | 384 | -22.5 | 49.7 | 83.8 | -2.4 | 54.5 | 76.5 |
| 2 | 384 | -26.2 | 68.3 | 125.9 | -5.7 | 86.5 | 121.8 |
| 3 | 384 | -36.7 | 71.0 | 130.1 | -5.7 | 86.5 | 121.8 |
| 4 | 384 | -50.8 | 81.0 | 140.0 | -5.7 | 86.5 | 121.8 |
| 5 | 384 | -41.1 | 85.1 | 141.4 | -5.5 | 86.7 | 121.9 |

By calendar year (MAE, projected / carried forward):

| h | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| 1 | 19 / 27 | 24 / 31 | 104 / 64 | 61 / 59 | 40 / 61 | 46 / 71 | 37 / 62 | 49 / 47 |
| 2 | 23 / 38 | 37 / 48 | 170 / 118 | 78 / 96 | 58 / 102 | 62 / 101 | 47 / 84 | 48 / 78 |
| 3 | 21 / 38 | 40 / 48 | 181 / 118 | 91 / 96 | 50 / 102 | 54 / 101 | 55 / 84 | 50 / 78 |
| 4 | 25 / 38 | 48 / 48 | 201 / 118 | 99 / 96 | 52 / 102 | 63 / 101 | 63 / 84 | 67 / 78 |
| 5 | 32 / 38 | 53 / 48 | 207 / 118 | 88 / 96 | 60 / 102 | 73 / 101 | 70 / 84 | 69 / 78 |
