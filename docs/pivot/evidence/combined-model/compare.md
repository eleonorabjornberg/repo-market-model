# The combined model (#561)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| risk_gbm+combined | 10 / 1.12 fail | fail | 10 / 1.92 fail | 2 / 0.89 fail |
| risk_gbm+combined_nogate | 11 / 1.69 fail | fail | 11 / 2.65 fail | 3 / 0.44 fail |
| risk_logistic+combined | 11 / 1.31 fail | fail | 11 / 2.50 fail | 4 / 2.11 fail |
| risk_logistic+combined_nogate | 9 / 1.54 fail | fail | 9 / 2.58 fail | 2 / 0.44 fail |
| risk_gbm+combined_no_factor | 10 / 1.08 fail | fail | 10 / 2.04 fail | 2 / 0.89 fail |
| risk_gbm+combined_no_structural | 9 / 0.73 fail | fail | 9 / 1.38 fail | 2 / 0.89 fail |
| risk_gbm+combined_no_projected | 11 / 1.23 fail | fail | 11 / 2.12 fail | 2 / 0.89 fail |
| risk_gbm | 13 / 1.35 pass | pass (h = 1) | 13 / 2.00 pass | 3 / 1.56 fail |
| risk_logistic | 14 / 1.85 pass | pass (h = 1) | 14 / 2.42 fail | 4 / 2.89 fail |
| risk_gbm_base | 14 / 1.50 pass | pass (h = 1) | 14 / 2.04 fail | 4 / 2.00 fail |
| risk_logistic_base | 13 / 1.77 pass | pass (h = 1) | 13 / 2.04 fail | 3 / 2.33 fail |
| risk_quantile_skewt_base | 14 / 1.88 pass | pass (h = 1) | 14 / 2.54 fail | 4 / 3.22 fail |
| ngboost_laplace | 15 / 2.54 fail | fail | 15 / 4.38 fail | 4 / 0.33 fail |
| risk_gbm+settle+h41 | 14 / 1.35 pass | pass (h = 1) | 14 / 2.00 pass | 4 / 1.78 fail |
| risk_logistic+settle+h41 | 15 / 1.81 pass | pass (h = 1) | 15 / 2.42 fail | 5 / 2.78 fail |
| risk_gbm+every_day+gate+settle+h41 | 15 / 2.35 fail | fail | 15 / 4.31 fail | 4 / 3.11 fail |
| risk_logistic+every_day+gate+settle+h41 | 14 / 2.69 fail | fail | 14 / 5.12 fail | 3 / 2.33 fail |
| calendar_climatology | 10 / 5.00 fail | fail | 10 / 5.38 fail | 0 / 3.78 fail |
| persistence_logistic | 7 / 3.42 fail | fail | 7 / 5.73 fail | 0 / 2.22 fail |

## Tier 1 under weighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| risk_gbm+combined | 10 / 1.06 fail | fail | 10 / 1.76 fail | 2 / 1.81 fail |
| risk_gbm+combined_nogate | 13 / 1.78 pass | pass (h = 1) | 13 / 2.41 fail | 3 / 0.61 fail |
| risk_logistic+combined | 11 / 1.86 fail | fail | 11 / 3.07 fail | 4 / 4.39 fail |
| risk_logistic+combined_nogate | 13 / 1.92 pass | fail | 13 / 2.38 fail | 3 / 1.08 fail |
| risk_gbm+combined_no_factor | 10 / 1.01 fail | fail | 10 / 1.79 fail | 2 / 1.81 fail |
| risk_gbm+combined_no_structural | 10 / 0.96 fail | fail | 10 / 1.81 fail | 2 / 1.81 fail |
| risk_gbm+combined_no_projected | 11 / 1.03 fail | fail | 11 / 1.88 fail | 2 / 1.81 fail |
| risk_gbm | 13 / 0.80 pass | pass (h = 1) | 13 / 1.48 pass | 3 / 1.61 fail |
| risk_logistic | 16 / 1.74 pass | pass (h = 1) | 16 / 2.55 fail | 6 / 4.39 fail |
| risk_gbm_base | 14 / 0.97 pass | pass (h = 1) | 14 / 1.59 pass | 4 / 2.06 fail |
| risk_logistic_base | 15 / 1.65 pass | pass (h = 1) | 15 / 2.18 fail | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass (h = 1) | 15 / 2.14 fail | 5 / 3.81 fail |
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 5 / 0.50 fail |
| risk_gbm+settle+h41 | 14 / 0.88 pass | pass (h = 1) | 14 / 1.44 pass | 4 / 1.72 fail |
| risk_logistic+settle+h41 | 16 / 2.12 fail | pass (h = 1) | 16 / 2.83 fail | 6 / 5.08 fail |
| risk_gbm+every_day+gate+settle+h41 | 18 / 1.64 pass | pass (h = 1) | 18 / 3.39 fail | 5 / 2.42 fail |
| risk_logistic+every_day+gate+settle+h41 | 18 / 2.05 fail | fail | 18 / 3.91 fail | 5 / 3.28 fail |
| calendar_climatology | 12 / 3.75 fail | fail | 12 / 3.90 fail | 0 / 4.56 fail |
| persistence_logistic | 12 / 3.25 fail | fail | 12 / 4.09 fail | 1 / 2.86 fail |

## Tier 1 under weighted/before_only

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| risk_gbm+combined | 10 / 0.88 fail | fail | 10 / 1.73 fail | 2 / 1.19 fail |
| risk_gbm+combined_nogate | 13 / 2.09 fail | fail | 13 / 3.15 fail | 3 / 0.69 fail |
| risk_logistic+combined | 11 / 1.40 fail | fail | 11 / 2.64 fail | 4 / 2.92 fail |
| risk_logistic+combined_nogate | 11 / 2.15 fail | fail | 11 / 2.97 fail | 2 / 1.11 fail |
| risk_gbm+combined_no_factor | 10 / 0.85 fail | fail | 10 / 1.81 fail | 2 / 1.08 fail |
| risk_gbm+combined_no_structural | 10 / 0.66 fail | fail | 10 / 1.38 fail | 2 / 0.97 fail |
| risk_gbm+combined_no_projected | 11 / 0.88 fail | fail | 11 / 1.80 fail | 2 / 1.19 fail |
| risk_gbm | 13 / 0.95 pass | pass (h = 1) | 13 / 1.64 pass | 3 / 1.78 fail |
| risk_logistic | 16 / 1.90 pass | pass (h = 1) | 16 / 2.70 fail | 6 / 4.31 fail |
| risk_gbm_base | 14 / 1.08 pass | pass (h = 1) | 14 / 1.72 pass | 4 / 2.22 fail |
| risk_logistic_base | 14 / 1.78 pass | pass (h = 1) | 14 / 2.26 fail | 4 / 3.58 fail |
| risk_quantile_skewt_base | 15 / 1.81 pass | pass (h = 1) | 15 / 2.22 fail | 5 / 4.14 fail |
| ngboost_laplace | 16 / 2.23 fail | pass (h = 1) | 16 / 3.30 fail | 5 / 0.58 fail |
| risk_gbm+settle+h41 | 14 / 1.02 pass | pass (h = 1) | 14 / 1.63 pass | 4 / 1.89 fail |
| risk_logistic+settle+h41 | 16 / 2.14 fail | pass (h = 1) | 16 / 2.91 fail | 6 / 4.92 fail |
| risk_gbm+every_day+gate+settle+h41 | 18 / 2.09 fail | fail | 18 / 4.18 fail | 5 / 2.78 fail |
| risk_logistic+every_day+gate+settle+h41 | 17 / 2.50 fail | fail | 17 / 4.33 fail | 4 / 2.83 fail |
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
| risk_gbm+combined | 10 of 26 | 0.385 [0.212, 0.571] | 0.192 | 1.92 flat / 1.06 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_factor | 10 of 26 | 0.385 [0.212, 0.571] | 0.192 | 2.04 flat / 1.12 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_projected | 11 of 26 | 0.423 [0.235, 0.618] | 0.192 | 2.12 flat / 1.01 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_structural | 9 of 26 | 0.346 [0.190, 0.522] | 0.154 | 1.38 flat / 0.79 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_nogate | 11 of 26 | 0.423 [0.250, 0.600] | 0.231 | 2.65 flat / 1.31 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+every_day+gate+settle+h41 | 15 of 26 | 0.577 [0.417, 0.741] | 0.242 | 4.31 flat / 2.04 weighted (tier 1 on the flat count) | 1.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.00 flat / 1.29 weighted (tier 1 on the flat count) | 0.5 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.04 flat / 1.43 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 2.42 flat / 1.75 weighted (tier 1 on the flat count) | 1.7 / 0.0 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic+combined | 11 of 26 | 0.423 [0.258, 0.606] | 0.231 | 2.50 flat / 1.67 weighted (tier 1 on the flat count) | 1.2 / 1.3 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+combined_nogate | 9 of 26 | 0.346 [0.200, 0.500] | 0.231 | 2.58 flat / 1.31 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+every_day+gate+settle+h41 | 14 of 26 | 0.538 [0.351, 0.708] | 0.269 | 5.12 flat / 2.32 weighted (tier 1 on the flat count) | 1.2 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+settle+h41 | 15 of 26 | 0.577 [0.391, 0.760] | 0.192 | 2.42 flat / 1.77 weighted (tier 1 on the flat count) | 2.2 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
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
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 0.692 [0.353, 1.160] | 0.404 [0.177, 0.738] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 0.808 [0.415, 1.333] | 0.529 [0.230, 0.954] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.154, 0.477] | 1.115 [0.480, 2.030] | 0.702 [0.261, 1.368] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 0.885 [0.414, 1.538] | 0.529 [0.213, 0.981] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.176 [0.952, 4.000] | 1.059 [0.359, 2.195] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_no_factor:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.100, 0.381] | 0.885 [0.474, 1.500] | 0.481 [0.240, 0.859] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 0.615 [0.312, 1.050] | 0.356 [0.156, 0.643] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 0.846 [0.458, 1.375] | 0.538 [0.250, 0.969] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 1.077 [0.483, 1.957] | 0.702 [0.262, 1.395] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 0.962 [0.464, 1.657] | 0.567 [0.243, 1.039] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.700] | 2.294 [1.000, 4.222] | 1.147 [0.400, 2.405] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.556 (no interval) | 1.083 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_no_projected:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.156, 0.476] | 0.846 [0.480, 1.400] | 0.442 [0.228, 0.783] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 0.692 [0.367, 1.172] | 0.375 [0.171, 0.696] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 0.885 [0.514, 1.462] | 0.510 [0.256, 0.938] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 1.038 [0.560, 1.750] | 0.558 [0.293, 0.975] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 1.231 [0.640, 2.087] | 0.567 [0.304, 0.955] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.778] | 2.471 [1.414, 4.154] | 0.985 [0.525, 1.688] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 1.444 (no interval) | 1.056 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_no_structural:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 6 | 0.231 [0.100, 0.385] | 0.423 [0.190, 0.778] | 0.260 [0.107, 0.491] |
| lead 2 alone (fail) | 26 | 6 | 0.231 [0.103, 0.389] | 0.423 [0.200, 0.760] | 0.231 [0.100, 0.438] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.120, 0.440] | 0.615 [0.312, 1.053] | 0.337 [0.143, 0.636] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.166, 0.471] | 0.731 [0.375, 1.280] | 0.471 [0.200, 0.869] |
| lead 5 alone (fail) | 26 | 7 | 0.269 [0.125, 0.423] | 0.654 [0.278, 1.208] | 0.423 [0.159, 0.831] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.211, 0.632] | 1.294 [0.600, 2.333] | 0.632 [0.229, 1.250] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 1.556 [0.667, 3.667] | 1.083 [0.425, 2.833] |

Recall with equal weight per regime: 0.203 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_nogate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 0.885 [0.290, 1.786] | 0.375 [0.131, 0.733] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.214, 0.556] | 1.346 [0.600, 2.467] | 0.663 [0.299, 1.237] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.154, 0.471] | 1.692 [0.889, 2.924] | 0.788 [0.400, 1.363] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 1.462 [0.654, 2.577] | 0.817 [0.365, 1.531] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.200, 0.571] | 0.731 [0.263, 1.429] | 0.481 [0.177, 0.970] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.709] | 3.529 [1.882, 6.201] | 1.515 [0.722, 2.795] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.000 (no interval) | 0.917 (no interval) |

Recall with equal weight per regime: 0.268 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

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

risk_logistic+combined:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.524] | 1.308 [0.805, 2.042] | 0.788 [0.425, 1.329] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.481] | 1.115 [0.667, 1.800] | 0.721 [0.375, 1.250] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.130, 0.429] | 1.154 [0.686, 1.895] | 0.904 [0.490, 1.583] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.156, 0.500] | 1.038 [0.567, 1.750] | 0.692 [0.379, 1.188] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.160, 0.474] | 0.885 [0.481, 1.467] | 0.538 [0.272, 0.922] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.214, 0.643] | 1.765 [1.000, 2.900] | 0.809 [0.383, 1.462] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.889 (no interval) | 3.306 (no interval) |

Recall with equal weight per regime: 0.378 (2018-19 7/17, 2020 0/2, 2024 1/2, 2025-26 3/5).

risk_logistic+combined_nogate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 5 | 0.192 [0.066, 0.333] | 1.500 [0.765, 2.458] | 0.644 [0.318, 1.065] |
| lead 2 alone (fail) | 26 | 3 | 0.115 [0.000, 0.227] | 0.192 [0.043, 0.393] | 0.163 [0.033, 0.350] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.071, 0.333] | 0.654 [0.300, 1.167] | 0.327 [0.157, 0.578] |
| lead 4 alone (fail) | 26 | 7 | 0.269 [0.125, 0.412] | 1.538 [0.679, 2.677] | 0.827 [0.333, 1.531] |
| lead 5 alone (fail) | 26 | 2 | 0.077 [0.000, 0.167] | 0.385 [0.185, 0.667] | 0.221 [0.096, 0.406] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.214, 0.615] | 3.471 [1.889, 5.883] | 1.574 [0.750, 2.795] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 0.889 (no interval) | 0.806 (no interval) |

Recall with equal weight per regime: 0.203 (2018-19 7/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_logistic+every_day+gate+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.185, 0.500] | 2.500 [1.667, 3.720] | 1.125 [0.738, 1.719] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.125, 0.424] | 1.577 [0.765, 2.678] | 0.587 [0.282, 1.000] |
| lead 3 alone (fail) | 26 | 5 | 0.192 [0.074, 0.323] | 0.846 [0.469, 1.369] | 0.423 [0.224, 0.739] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.158, 0.458] | 1.423 [0.810, 2.286] | 0.548 [0.321, 0.864] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.219, 0.562] | 2.692 [1.767, 4.000] | 1.269 [0.847, 1.897] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.417, 0.864] | 5.353 [3.455, 8.308] | 2.162 [1.395, 3.429] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.667 (no interval) | 2.611 (no interval) |

Recall with equal weight per regime: 0.312 (2018-19 11/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.324, 0.682] | 1.731 [1.160, 2.667] | 1.125 [0.687, 1.929] |
| lead 2 alone (pass) | 26 | 14 | 0.538 [0.361, 0.719] | 1.538 [0.972, 2.450] | 1.000 [0.562, 1.763] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.167, 0.530] | 1.192 [0.697, 1.957] | 0.788 [0.425, 1.412] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.296, 0.633] | 1.577 [1.045, 2.444] | 1.048 [0.641, 1.759] |
| lead 5 alone (pass) | 26 | 14 | 0.538 [0.364, 0.714] | 1.808 [1.192, 2.790] | 1.202 [0.725, 2.013] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.810] | 1.471 [0.870, 2.417] | 0.706 [0.359, 1.333] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 4.222 (no interval) | 3.778 (no interval) |

Recall with equal weight per regime: 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5).

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
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+combined | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.24 (101) | 0.33 (9) | 0.46 (13) |
| risk_gbm+combined_no_factor | 0.34 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.53 (17) | 0.26 (101) | 0.33 (9) | 0.46 (13) |
| risk_gbm+combined_no_projected | 0.40 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.53 (17) | 0.31 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_no_structural | 0.23 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.41 (17) | 0.18 (101) | 0.33 (9) | 0.31 (13) |
| risk_gbm+combined_nogate | 0.46 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.37 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+combined | 0.37 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.27 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+combined_nogate | 0.47 (102) | 0.25 (4) | – | 0.20 (5) | 0.21 (29) | 0.53 (17) | 0.35 (101) | 0.56 (9) | 0.54 (13) |
| risk_logistic+every_day+gate+settle+h41 | 0.52 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.65 (17) | 0.40 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+combined | -0.0020 [-0.0236, +0.0186] | +0.0422 [+0.0346, +0.0500] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0054] | +0.0049 [-0.0043, +0.0151] | +0.0298 [+0.0161, +0.0442] | +0.0071 [+0.0020, +0.0116] | +0.1049 [+0.0102, +0.1953] | +0.0292 [-0.0010, +0.0578] |
| risk_gbm+combined_no_factor | -0.0025 [-0.0234, +0.0174] | +0.0422 [+0.0348, +0.0500] | +0.0138 [+0.0121, +0.0158] | +0.0010 [-0.0047, +0.0052] | +0.0050 [-0.0044, +0.0151] | +0.0298 [+0.0165, +0.0444] | +0.0070 [+0.0023, +0.0112] | +0.1049 [+0.0121, +0.1925] | +0.0292 [-0.0021, +0.0572] |
| risk_gbm+combined_no_projected | +0.0005 [-0.0202, +0.0202] | +0.0422 [+0.0345, +0.0498] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0053] | +0.0044 [-0.0051, +0.0146] | +0.0296 [+0.0172, +0.0431] | +0.0076 [+0.0028, +0.0118] | +0.1049 [+0.0156, +0.1989] | +0.0292 [-0.0021, +0.0579] |
| risk_gbm+combined_no_structural | -0.0058 [-0.0284, +0.0163] | +0.0422 [+0.0349, +0.0497] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0049, +0.0054] | +0.0052 [-0.0036, +0.0153] | +0.0299 [+0.0166, +0.0442] | +0.0062 [+0.0010, +0.0110] | +0.1049 [+0.0149, +0.1995] | +0.0292 [-0.0007, +0.0589] |
| risk_gbm+combined_nogate | +0.0486 [+0.0100, +0.0920] | +0.0248 [+0.0141, +0.0346] | +0.0127 [+0.0110, +0.0144] | +0.0015 [-0.0035, +0.0053] | +0.0228 [+0.0030, +0.0491] | +0.0566 [+0.0330, +0.0822] | +0.0134 [+0.0046, +0.0234] | +0.1247 [+0.0394, +0.2037] | +0.0689 [+0.0407, +0.0977] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic+combined | -0.0055 [-0.0246, +0.0131] | +0.0333 [+0.0240, +0.0412] | +0.0138 [+0.0120, +0.0156] | +0.0048 [+0.0011, +0.0084] | +0.0096 [+0.0012, +0.0205] | +0.0265 [+0.0131, +0.0413] | +0.0062 [+0.0016, +0.0105] | +0.0668 [-0.0140, +0.1429] | +0.0484 [+0.0290, +0.0675] |
| risk_logistic+combined_nogate | +0.0448 [+0.0063, +0.0879] | +0.0131 [-0.0023, +0.0258] | +0.0127 [+0.0111, +0.0145] | +0.0051 [+0.0012, +0.0093] | +0.0178 [+0.0037, +0.0369] | +0.0333 [+0.0073, +0.0610] | +0.0129 [+0.0045, +0.0223] | +0.0906 [+0.0168, +0.1610] | +0.0764 [+0.0457, +0.1128] |
| risk_logistic+every_day+gate+settle+h41 | +0.0382 [+0.0132, +0.0653] | +0.0193 [-0.0049, +0.0375] | +0.0136 [+0.0119, +0.0156] | +0.0021 [-0.0046, +0.0081] | +0.0236 [+0.0017, +0.0507] | +0.0362 [+0.0093, +0.0647] | +0.0129 [+0.0066, +0.0200] | +0.0906 [+0.0222, +0.1607] | +0.0764 [+0.0442, +0.1149] |
| risk_logistic+settle+h41 | -0.0019 [-0.0231, +0.0187] | +0.0266 [+0.0117, +0.0388] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0011, +0.0094] | +0.0125 [+0.0008, +0.0272] | +0.0305 [+0.0038, +0.0576] | +0.0040 [-0.0012, +0.0087] | +0.0906 [+0.0189, +0.1627] | +0.0764 [+0.0461, +0.1173] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.269 | 5.31 flat / 2.34 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.192 | 2.12 flat / 1.48 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+combined | 10 of 26 | 0.385 [0.212, 0.571] | 0.231 | 2.77 flat / 1.76 weighted (tier 1 on the weighted count) | 0.7 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_factor | 10 of 26 | 0.385 [0.212, 0.571] | 0.231 | 2.85 flat / 1.79 weighted (tier 1 on the weighted count) | 0.7 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_projected | 11 of 26 | 0.423 [0.235, 0.618] | 0.231 | 3.50 flat / 1.88 weighted (tier 1 on the weighted count) | 0.7 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_structural | 10 of 26 | 0.385 [0.217, 0.562] | 0.231 | 3.27 flat / 1.81 weighted (tier 1 on the weighted count) | 0.7 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_nogate | 13 of 26 | 0.500 [0.308, 0.684] | 0.269 | 5.04 flat / 2.41 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.524, 0.857] | 0.375 | 6.96 flat / 3.39 weighted (tier 1 on the weighted count) | 2.9 / 0.3 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.192 | 2.15 flat / 1.44 weighted (tier 1 on the weighted count) | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.192 | 2.19 flat / 1.59 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 0 of 2 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.231 | 3.31 flat / 2.55 weighted (tier 1 on the weighted count) | 2.9 / 0.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic+combined | 11 of 26 | 0.423 [0.258, 0.606] | 0.231 | 4.04 flat / 3.07 weighted (tier 1 on the weighted count) | 4.8 / 6.4 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+combined_nogate | 13 of 26 | 0.500 [0.333, 0.667] | 0.269 | 4.96 flat / 2.38 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 1 of 2 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.519, 0.857] | 0.401 | 7.73 flat / 3.91 weighted (tier 1 on the weighted count) | 3.9 / 0.3 | 1 of 2 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+settle+h41 | 16 of 26 | 0.615 [0.429, 0.800] | 0.231 | 3.54 flat / 2.83 weighted (tier 1 on the weighted count) | 4.6 / 2.7 | 0 of 2 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
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
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.478] | 1.538 [0.929, 2.500] | 1.058 [0.576, 1.834] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.115 [0.645, 1.790] | 0.750 [0.371, 1.306] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 1.462 [0.750, 2.522] | 0.981 [0.448, 1.772] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.524] | 1.346 [0.769, 2.174] | 0.904 [0.481, 1.533] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.714] | 2.471 [1.214, 4.429] | 1.221 [0.472, 2.412] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 2.778 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_no_factor:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.152, 0.474] | 1.038 [0.611, 1.667] | 0.519 [0.274, 0.895] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.158, 0.474] | 1.462 [0.875, 2.400] | 1.010 [0.540, 1.761] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.182, 0.522] | 1.154 [0.682, 1.857] | 0.760 [0.398, 1.339] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.519] | 1.269 [0.636, 2.185] | 0.827 [0.361, 1.554] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 1.423 [0.800, 2.334] | 0.942 [0.492, 1.647] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.700] | 2.588 [1.286, 4.668] | 1.309 [0.524, 2.604] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 3.333 (no interval) | 2.694 (no interval) |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_no_projected:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.156, 0.476] | 1.500 [0.920, 2.375] | 0.644 [0.386, 1.069] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.476] | 1.538 [0.954, 2.531] | 1.029 [0.575, 1.829] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.214, 0.571] | 1.192 [0.727, 1.924] | 0.731 [0.391, 1.333] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 1.692 [1.031, 2.750] | 0.942 [0.536, 1.621] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.211, 0.571] | 1.808 [1.077, 2.941] | 0.971 [0.562, 1.639] |
| inside 2018-2019 | 17 | 9 | 0.529 [0.294, 0.778] | 2.941 [1.750, 4.848] | 1.206 [0.676, 2.062] |
| outside 2018-2019 | 9 | 2 | 0.222 (no interval) | 4.556 (no interval) | 3.139 (no interval) |

Recall with equal weight per regime: 0.232 (2018-19 9/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_no_structural:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.158, 0.469] | 1.731 [0.905, 2.955] | 0.673 [0.371, 1.120] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.160, 0.471] | 1.346 [0.793, 2.208] | 0.913 [0.474, 1.643] |
| lead 3 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 1.038 [0.618, 1.667] | 0.635 [0.327, 1.125] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.185, 0.520] | 1.231 [0.697, 2.033] | 0.865 [0.435, 1.528] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.179, 0.520] | 1.538 [0.828, 2.524] | 0.962 [0.511, 1.618] |
| inside 2018-2019 | 17 | 8 | 0.471 [0.250, 0.692] | 1.824 [0.941, 3.111] | 0.853 [0.354, 1.583] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.500] | 6.000 [3.250, 12.802] | 3.611 [1.917, 8.439] |

Recall with equal weight per regime: 0.218 (2018-19 8/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

risk_gbm+combined_nogate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 13 | 0.500 [0.308, 0.684] | 3.231 [1.814, 5.316] | 1.481 [0.767, 2.532] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.308, 0.684] | 3.154 [1.844, 5.120] | 1.365 [0.781, 2.236] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.267, 0.655] | 3.615 [2.115, 5.896] | 1.702 [0.948, 2.876] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.267, 0.655] | 3.885 [2.273, 6.218] | 1.779 [0.991, 2.986] |
| lead 5 alone (fail) | 26 | 12 | 0.462 [0.267, 0.655] | 3.654 [2.185, 5.800] | 1.683 [0.974, 2.795] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.346, 0.818] | 6.765 [4.249, 10.843] | 2.971 [1.750, 4.951] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.778 (no interval) | 1.361 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

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

risk_logistic+combined:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.524] | 2.077 [1.300, 3.389] | 1.500 [0.821, 2.667] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.226, 0.565] | 1.692 [1.083, 2.625] | 1.115 [0.636, 1.882] |
| lead 3 alone (fail) | 26 | 8 | 0.308 [0.167, 0.474] | 2.231 [1.333, 3.765] | 1.856 [1.029, 3.279] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.188, 0.526] | 1.538 [0.926, 2.500] | 1.058 [0.605, 1.819] |
| lead 5 alone (fail) | 26 | 9 | 0.346 [0.193, 0.520] | 1.808 [1.091, 3.000] | 1.337 [0.740, 2.309] |
| inside 2018-2019 | 17 | 7 | 0.412 [0.214, 0.643] | 2.059 [1.222, 3.333] | 0.941 [0.453, 1.684] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 7.778 (no interval) | 7.083 (no interval) |

Recall with equal weight per regime: 0.378 (2018-19 7/17, 2020 0/2, 2024 1/2, 2025-26 3/5).

risk_logistic+combined_nogate:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 9 | 0.346 [0.192, 0.500] | 3.654 [2.120, 5.835] | 1.702 [0.958, 2.813] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.167, 0.478] | 2.385 [1.171, 4.167] | 1.173 [0.598, 2.017] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.125, 0.429] | 2.577 [1.318, 4.534] | 1.240 [0.567, 2.292] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.222, 0.548] | 3.923 [2.345, 6.138] | 1.923 [1.100, 3.150] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.161, 0.474] | 2.538 [1.250, 4.317] | 1.202 [0.571, 2.179] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.375, 0.800] | 6.706 [4.273, 10.468] | 2.926 [1.750, 4.834] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 1.667 (no interval) | 1.333 (no interval) |

Recall with equal weight per regime: 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

risk_logistic+every_day+gate+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.280, 0.640] | 3.962 [2.875, 5.619] | 1.990 [1.384, 2.985] |
| lead 2 alone (fail) | 26 | 12 | 0.462 [0.286, 0.632] | 4.154 [2.926, 5.913] | 1.875 [1.326, 2.739] |
| lead 3 alone (fail) | 26 | 7 | 0.269 [0.111, 0.435] | 2.577 [1.600, 3.941] | 1.183 [0.764, 1.838] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.250, 0.591] | 3.385 [2.345, 4.889] | 1.596 [1.116, 2.347] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.412, 0.739] | 4.423 [3.122, 6.267] | 2.048 [1.450, 2.947] |
| inside 2018-2019 | 17 | 13 | 0.765 [0.545, 1.000] | 6.412 [4.304, 9.715] | 2.618 [1.724, 4.051] |
| outside 2018-2019 | 9 | 5 | 0.556 (no interval) | 10.222 (no interval) | 6.361 (no interval) |

Recall with equal weight per regime: 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5).

risk_logistic+settle+h41:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (pass) | 26 | 14 | 0.538 [0.361, 0.719] | 2.385 [1.643, 3.668] | 1.702 [1.098, 2.829] |
| lead 2 alone (pass) | 26 | 16 | 0.615 [0.429, 0.800] | 2.231 [1.500, 3.474] | 1.596 [1.000, 2.675] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.318, 0.696] | 2.462 [1.667, 3.882] | 1.913 [1.235, 3.188] |
| lead 4 alone (pass) | 26 | 13 | 0.500 [0.333, 0.677] | 2.269 [1.529, 3.609] | 1.721 [1.096, 2.896] |
| lead 5 alone (fail) | 26 | 16 | 0.615 [0.429, 0.800] | 2.731 [1.872, 4.250] | 2.125 [1.371, 3.488] |
| inside 2018-2019 | 17 | 10 | 0.588 [0.368, 0.810] | 1.471 [0.870, 2.417] | 0.706 [0.359, 1.333] |
| outside 2018-2019 | 9 | 6 | 0.667 (no interval) | 7.444 (no interval) | 6.833 (no interval) |

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
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+combined | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.27 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_no_factor | 0.37 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.53 (17) | 0.28 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_no_projected | 0.41 (102) | 0.25 (4) | – | 0.00 (5) | 0.52 (29) | 0.59 (17) | 0.37 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_no_structural | 0.38 (102) | 0.25 (4) | – | 0.00 (5) | 0.66 (29) | 0.59 (17) | 0.39 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_nogate | 0.63 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.65 (17) | 0.52 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+combined | 0.38 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.27 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+combined_nogate | 0.63 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.59 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+every_day+gate+settle+h41 | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.66 (29) | 0.76 (17) | 0.54 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.76 (17) | 0.17 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+combined | -0.0020 [-0.0236, +0.0186] | +0.0422 [+0.0346, +0.0500] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0054] | +0.0049 [-0.0043, +0.0151] | +0.0298 [+0.0161, +0.0442] | +0.0071 [+0.0020, +0.0116] | +0.1049 [+0.0102, +0.1953] | +0.0292 [-0.0010, +0.0578] |
| risk_gbm+combined_no_factor | -0.0025 [-0.0234, +0.0174] | +0.0422 [+0.0348, +0.0500] | +0.0138 [+0.0121, +0.0158] | +0.0010 [-0.0047, +0.0052] | +0.0050 [-0.0044, +0.0151] | +0.0298 [+0.0165, +0.0444] | +0.0070 [+0.0023, +0.0112] | +0.1049 [+0.0121, +0.1925] | +0.0292 [-0.0021, +0.0572] |
| risk_gbm+combined_no_projected | +0.0005 [-0.0202, +0.0202] | +0.0422 [+0.0345, +0.0498] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0053] | +0.0044 [-0.0051, +0.0146] | +0.0296 [+0.0172, +0.0431] | +0.0076 [+0.0028, +0.0118] | +0.1049 [+0.0156, +0.1989] | +0.0292 [-0.0021, +0.0579] |
| risk_gbm+combined_no_structural | -0.0058 [-0.0284, +0.0163] | +0.0422 [+0.0349, +0.0497] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0049, +0.0054] | +0.0052 [-0.0036, +0.0153] | +0.0299 [+0.0166, +0.0442] | +0.0062 [+0.0010, +0.0110] | +0.1049 [+0.0149, +0.1995] | +0.0292 [-0.0007, +0.0589] |
| risk_gbm+combined_nogate | +0.0486 [+0.0100, +0.0920] | +0.0248 [+0.0141, +0.0346] | +0.0127 [+0.0110, +0.0144] | +0.0015 [-0.0035, +0.0053] | +0.0228 [+0.0030, +0.0491] | +0.0566 [+0.0330, +0.0822] | +0.0134 [+0.0046, +0.0234] | +0.1247 [+0.0394, +0.2037] | +0.0689 [+0.0407, +0.0977] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic+combined | -0.0055 [-0.0246, +0.0131] | +0.0333 [+0.0240, +0.0412] | +0.0138 [+0.0120, +0.0156] | +0.0048 [+0.0011, +0.0084] | +0.0096 [+0.0012, +0.0205] | +0.0265 [+0.0131, +0.0413] | +0.0062 [+0.0016, +0.0105] | +0.0668 [-0.0140, +0.1429] | +0.0484 [+0.0290, +0.0675] |
| risk_logistic+combined_nogate | +0.0448 [+0.0063, +0.0879] | +0.0131 [-0.0023, +0.0258] | +0.0127 [+0.0111, +0.0145] | +0.0051 [+0.0012, +0.0093] | +0.0178 [+0.0037, +0.0369] | +0.0333 [+0.0073, +0.0610] | +0.0129 [+0.0045, +0.0223] | +0.0906 [+0.0168, +0.1610] | +0.0764 [+0.0457, +0.1128] |
| risk_logistic+every_day+gate+settle+h41 | +0.0382 [+0.0132, +0.0653] | +0.0193 [-0.0049, +0.0375] | +0.0136 [+0.0119, +0.0156] | +0.0021 [-0.0046, +0.0081] | +0.0236 [+0.0017, +0.0507] | +0.0362 [+0.0093, +0.0647] | +0.0129 [+0.0066, +0.0200] | +0.0906 [+0.0222, +0.1607] | +0.0764 [+0.0442, +0.1149] |
| risk_logistic+settle+h41 | -0.0019 [-0.0231, +0.0187] | +0.0266 [+0.0117, +0.0388] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0011, +0.0094] | +0.0125 [+0.0008, +0.0272] | +0.0305 [+0.0038, +0.0576] | +0.0040 [-0.0012, +0.0087] | +0.0906 [+0.0189, +0.1627] | +0.0764 [+0.0461, +0.1173] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| risk_gbm+combined | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_nogate | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_logistic+combined | 0 of 4 | 7 of 13 | 0 of 2 | 1 of 2 | 3 of 5 |
| risk_logistic+combined_nogate | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm+combined_no_factor | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_no_structural | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_no_projected | 0 of 4 | 9 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_gbm+settle+h41 | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic+settle+h41 | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_gbm+every_day+gate+settle+h41 | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic+every_day+gate+settle+h41 | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |

## Brier score and log loss at +5 bp, pooled by horizon

| row | h = 1 Brier / log loss | h = 2 Brier / log loss | h = 3 Brier / log loss | h = 4 Brier / log loss | h = 5 Brier / log loss |
|---|---|---|---|---|---|
| risk_gbm+combined | 0.0599 / 0.5426 | 0.0628 / 0.5966 | 0.0635 / 0.5899 | 0.0645 / 0.6049 | 0.0627 / 0.6106 |
| risk_gbm+combined_nogate | 0.0501 / 0.1970 | 0.0528 / 0.2115 | 0.0560 / 0.2163 | 0.0549 / 0.2288 | 0.0611 / 0.2666 |
| risk_logistic+combined | 0.0606 / 0.5524 | 0.0621 / 0.5887 | 0.0635 / 0.5923 | 0.0646 / 0.5979 | 0.0651 / 0.6201 |
| risk_logistic+combined_nogate | 0.0525 / 0.2141 | 0.0540 / 0.2198 | 0.0541 / 0.2091 | 0.0561 / 0.2326 | 0.0620 / 0.2683 |
| risk_gbm+combined_no_factor | 0.0599 / 0.5425 | 0.0627 / 0.5863 | 0.0633 / 0.5855 | 0.0641 / 0.6037 | 0.0624 / 0.5982 |
| risk_gbm+combined_no_structural | 0.0606 / 0.5332 | 0.0647 / 0.6017 | 0.0647 / 0.6058 | 0.0652 / 0.6239 | 0.0642 / 0.6203 |
| risk_gbm+combined_no_projected | 0.0594 / 0.5437 | 0.0632 / 0.6453 | 0.0625 / 0.5948 | 0.0629 / 0.5483 | 0.0619 / 0.5739 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |
| risk_gbm+settle+h41 | 0.0579 / 0.6610 | 0.0593 / 0.6688 | 0.0612 / 0.6687 | 0.0589 / 0.6720 | 0.0593 / 0.6740 |
| risk_logistic+settle+h41 | 0.0604 / 0.6780 | 0.0606 / 0.6771 | 0.0593 / 0.6614 | 0.0601 / 0.6758 | 0.0602 / 0.6757 |
| risk_gbm+every_day+gate+settle+h41 | 0.0498 / 0.3819 | 0.0544 / 0.3842 | 0.0570 / 0.4211 | 0.0532 / 0.3661 | 0.0539 / 0.3748 |
| risk_logistic+every_day+gate+settle+h41 | 0.0523 / 0.3990 | 0.0557 / 0.3926 | 0.0551 / 0.4138 | 0.0544 / 0.3699 | 0.0548 / 0.3765 |
| calendar_climatology | 0.0714 / 0.2963 | 0.0711 / 0.2954 | 0.0707 / 0.2943 | 0.0708 / 0.2952 | 0.0709 / 0.2958 |
| persistence_logistic | 0.0563 / 0.2014 | 0.0611 / 0.2184 | 0.0644 / 0.2424 | 0.0624 / 0.2254 | 0.0634 / 0.2394 |

## risk_gbm+combined: onsets only this row warns

risk_gbm+combined warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined and by none of the five passers:


Warned by a passer and not by risk_gbm+combined: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1326 of 1873 | 529 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1369 of 1872 | 484 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1361 of 1871 | 491 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1372 of 1870 | 474 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1368 of 1869 | 479 |

## risk_gbm+combined_nogate: onsets only this row warns

risk_gbm+combined_nogate warns 13 of 26 onsets; at least one of the five passers warns 16. 2 are warned by risk_gbm+combined_nogate and by none of the five passers:

* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_gbm+combined_nogate: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-10-15

### risk_gbm+combined_nogate: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 2 | 0 of 1873 | 1848 |
| 2 | 90 | 0 | 0 | 7 | 3 | 0 of 1872 | 1847 |
| 3 | 90 | 0 | 0 | 7 | 4 | 0 of 1871 | 1845 |
| 4 | 90 | 1 | 0 | 7 | 5 | 0 of 1870 | 1845 |
| 5 | 89 | 0 | 0 | 7 | 2 | 0 of 1869 | 1844 |

## risk_logistic+combined: onsets only this row warns

risk_logistic+combined warns 11 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_logistic+combined and by none of the five passers:


Warned by a passer and not by risk_logistic+combined: 2019-01-15, 2019-01-31, 2019-03-15, 2025-09-15, 2025-10-15

### risk_logistic+combined: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1326 of 1873 | 547 |
| 2 | 90 | 1 | 1 | 7 | 1 | 1369 of 1872 | 504 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1361 of 1871 | 511 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1372 of 1870 | 499 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1368 of 1869 | 502 |

## risk_logistic+combined_nogate: onsets only this row warns

risk_logistic+combined_nogate warns 13 of 26 onsets; at least one of the five passers warns 16. 2 are warned by risk_logistic+combined_nogate and by none of the five passers:

* 2019-06-25 (flagged at h = 4)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_logistic+combined_nogate: 2019-03-15, 2019-08-30, 2024-09-30, 2025-09-15, 2025-10-15

### risk_logistic+combined_nogate: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 3 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 1 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 3 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 6 | 1 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1869 |

## risk_gbm+combined_no_factor: onsets only this row warns

risk_gbm+combined_no_factor warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined_no_factor and by none of the five passers:


Warned by a passer and not by risk_gbm+combined_no_factor: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_no_factor: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1326 of 1873 | 530 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1349 of 1872 | 504 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1342 of 1871 | 510 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1359 of 1870 | 487 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1356 of 1869 | 491 |

## risk_gbm+combined_no_structural: onsets only this row warns

risk_gbm+combined_no_structural warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined_no_structural and by none of the five passers:


Warned by a passer and not by risk_gbm+combined_no_structural: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_no_structural: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1207 of 1873 | 649 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1271 of 1872 | 582 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1287 of 1871 | 565 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1297 of 1870 | 549 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1316 of 1869 | 531 |

## risk_gbm+combined_no_projected: onsets only this row warns

risk_gbm+combined_no_projected warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by risk_gbm+combined_no_projected and by none of the five passers:

* 2019-08-13 (flagged at h = 3, 4, 5)

Warned by a passer and not by risk_gbm+combined_no_projected: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_no_projected: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1416 of 1873 | 439 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1442 of 1872 | 411 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1430 of 1871 | 422 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1383 of 1870 | 463 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1396 of 1869 | 451 |

## risk_gbm+combined against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.006 [0.001, 0.011] |
| 3 | 0.003 [-0.001, 0.007] |
| 4 | 0.002 [-0.001, 0.006] |
| 5 | 0.007 [0.003, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.012] | 0.015 [-0.004, 0.034] | 0.020 [0.005, 0.035] |
| 2020 | 251 | 0.003 [-0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.011 [-0.027, 0.002] | 0.003 [-0.002, 0.009] | 0.022 [0.004, 0.046] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.049, -0.003] | -0.007 [-0.022, 0.007] | 0.019 [0.007, 0.031] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | 0.005 [0.002, 0.009] | 0.005 [0.002, 0.008] |
| quarter_end | 31 | -0.011 [-0.067, 0.049] | -0.002 [-0.061, 0.062] | 0.037 [-0.000, 0.081] |
| tax_date | 89 | -0.039 [-0.073, -0.010] | -0.015 [-0.058, 0.021] | 0.018 [-0.035, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.001] | 0.001 [-0.001, 0.002] |
| 2 | 41 | 0.000 [–] | -0.007 [–] | 0.019 [–] |
| 3 | 478 | -0.008 [-0.023, 0.005] | 0.013 [-0.002, 0.028] | 0.025 [0.010, 0.040] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.095 [-0.227, 0.000] |

## risk_gbm+combined against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.006] |
| 2 | -0.006 [-0.015, 0.002] |
| 3 | -0.004 [-0.013, 0.004] |
| 4 | -0.003 [-0.012, 0.005] |
| 5 | 0.001 [-0.009, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.056 [-0.096, -0.022] | -0.023 [-0.068, 0.019] | -0.005 [-0.052, 0.037] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.010, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.041, -0.008] | 0.007 [-0.002, 0.020] | 0.014 [0.001, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.039, -0.000] | 0.008 [-0.008, 0.025] | 0.024 [0.004, 0.046] |
| ordinary | 1603 | -0.012 [-0.022, -0.003] | -0.005 [-0.015, 0.003] | -0.002 [-0.013, 0.007] |
| quarter_end | 31 | -0.026 [-0.089, 0.029] | -0.011 [-0.074, 0.055] | 0.010 [-0.035, 0.059] |
| tax_date | 89 | -0.038 [-0.076, -0.007] | 0.000 [-0.033, 0.028] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.003] |
| 2 | 41 | -0.057 [–] | -0.017 [–] | 0.008 [–] |
| 3 | 478 | -0.049 [-0.083, -0.020] | -0.013 [-0.050, 0.019] | 0.002 [-0.037, 0.036] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.353, -0.043] |

## risk_gbm+combined against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.006, 0.017] |
| 2 | 0.008 [0.002, 0.014] |
| 3 | 0.007 [0.001, 0.013] |
| 4 | 0.006 [0.000, 0.012] |
| 5 | 0.008 [0.003, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.024, 0.019] | -0.021 [-0.044, 0.000] | -0.018 [-0.039, 0.003] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.028, 0.048] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.015] | 0.005 [-0.006, 0.018] | 0.008 [-0.002, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.045] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.046] |
| ordinary | 1603 | 0.007 [0.002, 0.012] | 0.003 [-0.002, 0.008] | 0.002 [-0.003, 0.007] |
| quarter_end | 31 | 0.105 [0.012, 0.193] | 0.077 [-0.016, 0.181] | 0.100 [0.003, 0.197] |
| tax_date | 89 | 0.029 [-0.003, 0.058] | 0.038 [0.007, 0.067] | 0.044 [0.014, 0.073] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.031 [0.024, 0.038] | 0.029 [0.022, 0.036] |
| 2 | 41 | -0.011 [–] | -0.031 [–] | -0.012 [–] |
| 3 | 478 | 0.006 [-0.012, 0.024] | -0.009 [-0.030, 0.009] | -0.006 [-0.025, 0.012] |

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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.333, 0.158] |

## risk_gbm+combined against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.003] |
| 2 | -0.002 [-0.009, 0.005] |
| 3 | 0.001 [-0.006, 0.007] |
| 4 | -0.002 [-0.009, 0.004] |
| 5 | 0.001 [-0.006, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.051, 0.011] | -0.021 [-0.048, 0.003] | -0.015 [-0.042, 0.010] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.026] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.005] | 0.001 [-0.002, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.053, 0.002] | -0.001 [-0.025, 0.020] | 0.000 [-0.023, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.016, 0.031] | 0.011 [-0.001, 0.023] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.005 [-0.014, 0.002] | -0.001 [-0.009, 0.005] | -0.004 [-0.012, 0.003] |
| quarter_end | 31 | 0.045 [-0.007, 0.106] | 0.042 [-0.011, 0.102] | 0.074 [0.019, 0.144] |
| tax_date | 89 | -0.006 [-0.037, 0.017] | 0.011 [-0.008, 0.030] | 0.018 [-0.003, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.003 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.020 [0.016, 0.024] | 0.014 [0.011, 0.018] |
| 2 | 41 | -0.044 [–] | -0.064 [–] | -0.069 [–] |
| 3 | 478 | -0.018 [-0.047, 0.007] | -0.010 [-0.033, 0.011] | -0.004 [-0.029, 0.017] |

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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.286, 0.143] |

## risk_gbm+combined against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | -0.004 [-0.008, 0.001] |
| 3 | -0.002 [-0.006, 0.001] |
| 4 | -0.006 [-0.009, -0.002] |
| 5 | -0.003 [-0.007, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.020, 0.012] | -0.012 [-0.027, 0.004] | -0.020 [-0.033, -0.008] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.004, 0.015] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.013 [-0.029, 0.001] | -0.002 [-0.010, 0.004] | -0.002 [-0.009, 0.004] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.002] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.003 [-0.001, 0.006] | -0.000 [-0.003, 0.003] | -0.001 [-0.003, 0.001] |
| quarter_end | 31 | -0.020 [-0.077, 0.033] | -0.032 [-0.093, 0.028] | 0.006 [-0.026, 0.047] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.055, 0.023] | -0.036 [-0.083, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.007 [–] | -0.001 [–] | -0.006 [–] |
| 3 | 478 | -0.008 [-0.023, 0.007] | -0.011 [-0.024, 0.003] | -0.013 [-0.024, -0.002] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.004, 0.005] |
| 2 | -0.002 [-0.008, 0.003] |
| 3 | -0.004 [-0.009, -0.000] |
| 4 | -0.004 [-0.009, -0.000] |
| 5 | -0.002 [-0.007, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.000 [-0.019, 0.020] | -0.012 [-0.031, 0.008] | -0.012 [-0.031, 0.005] |
| 2020 | 251 | 0.016 [0.003, 0.032] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.012, 0.000] | -0.004 [-0.013, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.008 [-0.018, 0.001] | -0.010 [-0.025, 0.002] | -0.002 [-0.012, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.029, 0.029] | -0.011 [-0.034, 0.011] | 0.007 [-0.014, 0.030] |
| ordinary | 1603 | 0.003 [-0.000, 0.007] | -0.001 [-0.004, 0.002] | -0.001 [-0.003, 0.001] |
| quarter_end | 31 | 0.014 [-0.099, 0.136] | -0.048 [-0.157, 0.059] | -0.040 [-0.135, 0.049] |
| tax_date | 89 | -0.047 [-0.107, 0.003] | -0.036 [-0.096, 0.018] | -0.029 [-0.090, 0.026] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.001 [-0.000, 0.001] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [-0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | 0.023 [–] | -0.043 [–] | -0.032 [–] |
| 3 | 478 | -0.000 [-0.017, 0.017] | -0.013 [-0.028, 0.003] | -0.007 [-0.022, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.400, -0.077] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.286, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.385, 0.000] |
| quarter_end | 3 | -0.667 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.235, 0.000] |

## risk_gbm+combined against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.008 [-0.016, -0.002] |
| 3 | -0.007 [-0.013, -0.000] |
| 4 | -0.011 [-0.020, -0.004] |
| 5 | -0.009 [-0.017, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.074, -0.017] | -0.036 [-0.064, -0.010] | -0.048 [-0.081, -0.019] |
| 2020 | 251 | 0.011 [0.001, 0.025] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.015] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.024 [-0.052, -0.001] | -0.003 [-0.021, 0.013] | -0.005 [-0.028, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.055, -0.006] | -0.012 [-0.030, 0.006] | -0.014 [-0.025, -0.002] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.005 [-0.012, 0.001] | -0.007 [-0.015, -0.000] |
| quarter_end | 31 | -0.020 [-0.074, 0.031] | -0.032 [-0.095, 0.023] | 0.006 [-0.026, 0.049] |
| tax_date | 89 | -0.040 [-0.075, -0.008] | -0.014 [-0.054, 0.021] | -0.036 [-0.085, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.001, 0.003] | 0.001 [0.000, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.004, 0.003] |
| 2 | 41 | -0.048 [–] | -0.046 [–] | -0.061 [–] |
| 3 | 478 | -0.039 [-0.066, -0.013] | -0.027 [-0.050, -0.006] | -0.033 [-0.062, -0.007] |

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
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.286 [-0.452, -0.125] |

## risk_gbm+combined against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, 0.001] |
| 2 | -0.007 [-0.016, 0.000] |
| 3 | -0.008 [-0.016, -0.002] |
| 4 | -0.010 [-0.019, -0.002] |
| 5 | -0.008 [-0.016, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.040 [-0.073, -0.010] | -0.036 [-0.068, -0.007] | -0.040 [-0.076, -0.011] |
| 2020 | 251 | 0.023 [0.004, 0.049] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.004, 0.003] |
| 2025-26 | 249 | -0.019 [-0.043, 0.002] | -0.011 [-0.039, 0.010] | -0.004 [-0.028, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.037, 0.024] | -0.011 [-0.033, 0.012] | 0.005 [-0.018, 0.028] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.006 [-0.013, 0.000] | -0.007 [-0.016, -0.001] |
| quarter_end | 31 | 0.014 [-0.098, 0.132] | -0.048 [-0.155, 0.054] | -0.040 [-0.130, 0.052] |
| tax_date | 89 | -0.047 [-0.107, 0.003] | -0.036 [-0.092, 0.020] | -0.029 [-0.092, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.001, 0.002] | 0.002 [0.000, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | -0.017 [–] | -0.087 [–] | -0.087 [–] |
| 3 | 478 | -0.031 [-0.060, -0.004] | -0.029 [-0.055, -0.006] | -0.027 [-0.057, -0.002] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.474, -0.158] on 26 onsets.

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
| ordinary | 12 | -0.417 [-0.667, -0.182] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.286 [-0.462, -0.130] |

## risk_gbm+combined_nogate against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [-0.001, 0.018] |
| 2 | 0.016 [0.004, 0.030] |
| 3 | 0.011 [-0.001, 0.024] |
| 4 | 0.012 [0.001, 0.024] |
| 5 | 0.009 [-0.002, 0.021] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [0.003, 0.098] | 0.065 [0.011, 0.125] | 0.061 [0.011, 0.115] |
| 2020 | 251 | -0.015 [-0.022, -0.009] | -0.023 [-0.037, -0.008] | -0.039 [-0.053, -0.027] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | 0.000 [-0.000, 0.001] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.007 [0.001, 0.014] | 0.008 [0.000, 0.019] | 0.028 [0.008, 0.053] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.002 [-0.004, 0.011] | 0.007 [-0.009, 0.021] | 0.033 [0.014, 0.053] |
| ordinary | 1603 | 0.009 [-0.002, 0.021] | 0.011 [-0.002, 0.027] | 0.003 [-0.008, 0.016] |
| quarter_end | 31 | 0.009 [-0.032, 0.049] | 0.031 [-0.018, 0.087] | 0.031 [-0.001, 0.066] |
| tax_date | 89 | 0.000 [-0.004, 0.004] | -0.000 [-0.027, 0.022] | 0.055 [0.021, 0.094] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.000] | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.013 [-0.020, -0.008] | -0.021 [-0.027, -0.014] |
| 2 | 41 | 0.013 [–] | -0.008 [–] | 0.022 [–] |
| 3 | 478 | 0.035 [-0.000, 0.077] | 0.052 [0.007, 0.100] | 0.050 [0.009, 0.095] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.147, 0.143] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.222, 0.214] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.182, 0.167] |

## risk_gbm+combined_nogate against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.009, 0.001] |
| 2 | 0.004 [-0.003, 0.011] |
| 3 | 0.004 [-0.004, 0.012] |
| 4 | 0.007 [-0.000, 0.015] |
| 5 | 0.003 [-0.003, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.030, 0.019] | 0.027 [-0.009, 0.065] | 0.036 [0.013, 0.060] |
| 2020 | 251 | -0.008 [-0.017, 0.000] | -0.024 [-0.035, -0.013] | -0.038 [-0.048, -0.029] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | 0.000 [-0.003, 0.004] | -0.000 [-0.001, -0.000] |
| 2025-26 | 249 | -0.006 [-0.015, 0.003] | 0.012 [-0.002, 0.030] | 0.019 [0.004, 0.037] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.002, 0.020] | 0.022 [0.002, 0.045] | 0.037 [0.016, 0.063] |
| ordinary | 1603 | -0.005 [-0.011, -0.000] | 0.001 [-0.006, 0.008] | -0.003 [-0.009, 0.001] |
| quarter_end | 31 | -0.006 [-0.051, 0.033] | 0.021 [-0.073, 0.103] | 0.005 [-0.061, 0.066] |
| tax_date | 89 | 0.002 [-0.032, 0.033] | 0.014 [-0.020, 0.052] | 0.054 [0.017, 0.100] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.003, -0.000] | -0.001 [-0.002, 0.000] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.004 [-0.006, -0.003] | -0.013 [-0.020, -0.008] | -0.021 [-0.027, -0.013] |
| 2 | 41 | -0.044 [–] | -0.018 [–] | 0.010 [–] |
| 3 | 478 | -0.005 [-0.025, 0.014] | 0.025 [-0.005, 0.058] | 0.028 [0.006, 0.048] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.308, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.077] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.444, 0.100] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.261, 0.062] |

## risk_gbm+combined_nogate against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.021 [0.013, 0.031] |
| 2 | 0.018 [0.010, 0.028] |
| 3 | 0.015 [0.007, 0.024] |
| 4 | 0.016 [0.009, 0.023] |
| 5 | 0.010 [0.003, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.049 [0.009, 0.089] | 0.029 [-0.010, 0.071] | 0.024 [-0.009, 0.059] |
| 2020 | 251 | 0.025 [0.014, 0.034] | 0.015 [0.004, 0.026] | -0.002 [-0.014, 0.008] |
| 2021-23 | 748 | 0.013 [0.011, 0.015] | 0.013 [0.011, 0.014] | 0.009 [0.007, 0.011] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.004 [0.000, 0.007] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.023 [0.003, 0.047] | 0.010 [-0.004, 0.028] | 0.013 [0.003, 0.026] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.057 [0.035, 0.082] | 0.034 [0.018, 0.051] | 0.046 [0.029, 0.066] |
| ordinary | 1603 | 0.013 [0.005, 0.023] | 0.009 [0.000, 0.019] | 0.001 [-0.007, 0.009] |
| quarter_end | 31 | 0.125 [0.043, 0.207] | 0.109 [0.028, 0.193] | 0.094 [0.009, 0.177] |
| tax_date | 89 | 0.069 [0.040, 0.097] | 0.053 [0.028, 0.078] | 0.081 [0.056, 0.107] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.008 [0.006, 0.010] | 0.009 [0.007, 0.011] | 0.007 [0.006, 0.009] |
| 1 | 313 | 0.024 [0.018, 0.030] | 0.018 [0.012, 0.024] | 0.007 [0.002, 0.013] |
| 2 | 41 | 0.002 [–] | -0.032 [–] | -0.009 [–] |
| 3 | 478 | 0.050 [0.018, 0.083] | 0.029 [-0.001, 0.063] | 0.019 [-0.008, 0.046] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.143, 0.227] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.333, 0.083] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.273, 0.300] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.000 [-0.217, 0.231] |

## risk_gbm+combined_nogate against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.006 [-0.001, 0.014] |
| 2 | 0.008 [0.000, 0.017] |
| 3 | 0.008 [0.000, 0.016] |
| 4 | 0.008 [0.000, 0.015] |
| 5 | 0.002 [-0.005, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [0.003, 0.063] | 0.029 [-0.007, 0.065] | 0.026 [-0.005, 0.056] |
| 2020 | 251 | 0.001 [-0.008, 0.012] | 0.003 [-0.008, 0.012] | -0.020 [-0.029, -0.011] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | 0.003 [0.002, 0.004] | -0.003 [-0.004, -0.002] |
| 2024 | 250 | 0.002 [-0.001, 0.005] | 0.004 [0.001, 0.008] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.003 [-0.029, 0.021] | 0.004 [-0.018, 0.028] | 0.006 [-0.016, 0.027] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.035 [0.013, 0.059] | 0.024 [0.006, 0.043] | 0.037 [0.017, 0.058] |
| ordinary | 1603 | 0.001 [-0.006, 0.008] | 0.005 [-0.003, 0.012] | -0.005 [-0.012, 0.002] |
| quarter_end | 31 | 0.064 [-0.007, 0.142] | 0.074 [-0.019, 0.164] | 0.068 [-0.012, 0.149] |
| tax_date | 89 | 0.033 [-0.001, 0.075] | 0.025 [-0.011, 0.062] | 0.055 [0.017, 0.099] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | 0.003 [0.001, 0.004] | -0.000 [-0.001, 0.000] |
| 1 | 313 | 0.002 [-0.000, 0.004] | 0.007 [0.000, 0.011] | -0.008 [-0.012, -0.003] |
| 2 | 41 | -0.031 [–] | -0.064 [–] | -0.066 [–] |
| 3 | 478 | 0.026 [0.000, 0.053] | 0.029 [-0.001, 0.058] | 0.021 [-0.006, 0.047] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.115, 0.208] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.177, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.308, 0.182] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.000 [-0.176, 0.200] |

## risk_gbm+combined_nogate against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [-0.001, 0.019] |
| 2 | 0.007 [-0.003, 0.018] |
| 3 | 0.005 [-0.004, 0.016] |
| 4 | 0.004 [-0.004, 0.014] |
| 5 | -0.002 [-0.010, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [0.001, 0.097] | 0.038 [-0.007, 0.085] | 0.021 [-0.020, 0.068] |
| 2020 | 251 | -0.013 [-0.020, -0.008] | -0.018 [-0.024, -0.010] | -0.033 [-0.042, -0.024] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.005 [0.001, 0.011] | 0.003 [0.000, 0.006] | 0.003 [0.000, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.003, 0.011] | 0.002 [-0.002, 0.008] | 0.003 [-0.003, 0.011] |
| ordinary | 1603 | 0.009 [-0.002, 0.021] | 0.006 [-0.005, 0.018] | -0.002 [-0.012, 0.009] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.000, -0.000] | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.010 [-0.013, -0.007] | -0.022 [-0.026, -0.017] |
| 2 | 41 | 0.005 [–] | -0.001 [–] | -0.004 [–] |
| 3 | 478 | 0.036 [-0.000, 0.077] | 0.028 [-0.008, 0.068] | 0.012 [-0.020, 0.050] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.195, 0.120] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.222, 0.214] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.176, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | 0.000 [-0.176, 0.167] |

## risk_gbm+combined_nogate against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.000, 0.023] |
| 2 | 0.008 [-0.002, 0.019] |
| 3 | 0.003 [-0.006, 0.014] |
| 4 | 0.005 [-0.004, 0.015] |
| 5 | -0.001 [-0.010, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.050 [0.003, 0.104] | 0.038 [-0.006, 0.085] | 0.029 [-0.013, 0.076] |
| 2020 | 251 | -0.002 [-0.015, 0.014] | -0.023 [-0.035, -0.011] | -0.036 [-0.046, -0.027] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | -0.004 [-0.011, 0.000] | -0.001 [-0.003, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | 0.010 [0.001, 0.021] | -0.005 [-0.016, 0.005] | 0.004 [-0.006, 0.012] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.026 [0.008, 0.048] | 0.003 [-0.012, 0.018] | 0.021 [0.003, 0.041] |
| ordinary | 1603 | 0.009 [-0.002, 0.023] | 0.005 [-0.005, 0.017] | -0.003 [-0.012, 0.009] |
| quarter_end | 31 | 0.034 [-0.065, 0.129] | -0.016 [-0.091, 0.060] | -0.045 [-0.121, 0.022] |
| tax_date | 89 | -0.008 [-0.050, 0.031] | -0.022 [-0.056, 0.012] | 0.008 [-0.021, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.003, -0.000] | -0.000 [-0.001, 0.000] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.006 [-0.008, -0.003] | -0.013 [-0.020, -0.008] | -0.024 [-0.030, -0.018] |
| 2 | 41 | 0.036 [–] | -0.043 [–] | -0.030 [–] |
| 3 | 478 | 0.044 [0.007, 0.087] | 0.026 [-0.009, 0.065] | 0.019 [-0.015, 0.057] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.290, 0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.214, 0.214] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.300, 0.286] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | 0.000 [-0.176, 0.167] |

## risk_gbm+combined_nogate against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.007, 0.006] |
| 2 | 0.002 [-0.005, 0.008] |
| 3 | 0.001 [-0.006, 0.008] |
| 4 | -0.002 [-0.008, 0.005] |
| 5 | -0.007 [-0.014, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.007 [-0.023, 0.035] | 0.014 [-0.017, 0.046] | -0.007 [-0.033, 0.020] |
| 2020 | 251 | -0.006 [-0.018, 0.011] | -0.017 [-0.024, -0.009] | -0.033 [-0.042, -0.024] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.001 [-0.001, 0.000] | -0.005 [-0.006, -0.003] |
| 2024 | 250 | 0.003 [0.001, 0.007] | 0.002 [0.001, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.006 [-0.021, 0.006] | 0.002 [-0.013, 0.017] | 0.001 [-0.020, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.003 [-0.008, 0.001] | 0.002 [-0.002, 0.008] | 0.000 [-0.003, 0.004] |
| ordinary | 1603 | -0.000 [-0.007, 0.007] | 0.001 [-0.007, 0.009] | -0.008 [-0.016, -0.001] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.003] | -0.001 [-0.002, 0.001] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.010 [-0.012, -0.007] | -0.022 [-0.026, -0.017] |
| 2 | 41 | -0.035 [–] | -0.046 [–] | -0.059 [–] |
| 3 | 478 | 0.005 [-0.020, 0.029] | 0.011 [-0.014, 0.038] | -0.008 [-0.031, 0.016] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.333, -0.067] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.357, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.445, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.190 [-0.350, -0.053] |

## risk_gbm+combined_nogate against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.004, 0.009] |
| 2 | 0.003 [-0.004, 0.011] |
| 3 | -0.001 [-0.008, 0.006] |
| 4 | -0.000 [-0.007, 0.006] |
| 5 | -0.006 [-0.013, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.010 [-0.019, 0.040] | 0.014 [-0.016, 0.047] | 0.001 [-0.027, 0.032] |
| 2020 | 251 | 0.005 [-0.014, 0.030] | -0.022 [-0.035, -0.010] | -0.036 [-0.045, -0.027] |
| 2021-23 | 748 | -0.001 [-0.002, -0.000] | -0.001 [-0.001, 0.000] | -0.005 [-0.006, -0.003] |
| 2024 | 250 | -0.001 [-0.009, 0.005] | 0.001 [-0.001, 0.003] | 0.000 [-0.004, 0.003] |
| 2025-26 | 249 | -0.001 [-0.020, 0.016] | -0.006 [-0.030, 0.015] | 0.001 [-0.020, 0.022] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.020 [0.004, 0.041] | 0.003 [-0.012, 0.018] | 0.019 [0.002, 0.037] |
| ordinary | 1603 | 0.000 [-0.007, 0.008] | 0.000 [-0.007, 0.008] | -0.009 [-0.016, -0.001] |
| quarter_end | 31 | 0.034 [-0.062, 0.126] | -0.016 [-0.095, 0.064] | -0.045 [-0.117, 0.025] |
| tax_date | 89 | -0.008 [-0.047, 0.030] | -0.022 [-0.056, 0.012] | 0.008 [-0.022, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | 0.001 [0.000, 0.003] | -0.000 [-0.001, 0.002] |
| 1 | 313 | -0.006 [-0.008, -0.003] | -0.013 [-0.020, -0.008] | -0.024 [-0.030, -0.017] |
| 2 | 41 | -0.004 [–] | -0.087 [–] | -0.084 [–] |
| 3 | 478 | 0.012 [-0.012, 0.037] | 0.009 [-0.016, 0.037] | -0.001 [-0.026, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.333, -0.067] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.357, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.455, -0.053] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.190 [-0.353, -0.053] |

## risk_gbm+combined_nogate against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.001, 0.019] |
| 2 | 0.010 [0.000, 0.021] |
| 3 | 0.008 [-0.002, 0.018] |
| 4 | 0.010 [-0.000, 0.021] |
| 5 | 0.002 [-0.008, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.051 [0.010, 0.093] | 0.050 [0.004, 0.100] | 0.041 [-0.002, 0.093] |
| 2020 | 251 | -0.017 [-0.027, -0.010] | -0.023 [-0.037, -0.009] | -0.039 [-0.051, -0.028] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.000 [-0.000, 0.001] | 0.003 [-0.000, 0.009] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.018 [0.002, 0.038] | 0.005 [-0.003, 0.015] | 0.005 [-0.001, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.027 [0.005, 0.052] | 0.014 [-0.007, 0.034] | 0.014 [0.002, 0.028] |
| ordinary | 1603 | 0.006 [-0.003, 0.017] | 0.006 [-0.004, 0.018] | -0.001 [-0.011, 0.011] |
| quarter_end | 31 | 0.020 [-0.032, 0.079] | 0.032 [-0.021, 0.090] | -0.006 [-0.047, 0.027] |
| tax_date | 89 | 0.040 [0.009, 0.077] | 0.014 [-0.021, 0.054] | 0.036 [-0.005, 0.083] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.001] | -0.002 [-0.003, -0.002] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.013 [-0.020, -0.008] | -0.022 [-0.028, -0.015] |
| 2 | 41 | 0.013 [–] | -0.000 [–] | 0.002 [–] |
| 3 | 478 | 0.044 [0.010, 0.079] | 0.039 [0.001, 0.078] | 0.025 [-0.011, 0.067] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [0.000, 0.226] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.250] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [0.000, 0.364] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.095 [0.000, 0.211] |

## risk_logistic+combined against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.007, 0.001] |
| 2 | 0.007 [0.002, 0.012] |
| 3 | 0.003 [-0.000, 0.007] |
| 4 | 0.002 [-0.001, 0.005] |
| 5 | 0.004 [0.001, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.007 [-0.024, 0.011] | 0.010 [-0.006, 0.025] | 0.008 [-0.006, 0.021] |
| 2020 | 251 | -0.006 [-0.016, 0.002] | 0.000 [-0.000, 0.001] | 0.002 [-0.001, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | -0.001 [-0.003, 0.001] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | -0.006 [-0.021, 0.005] | 0.009 [-0.001, 0.021] | 0.020 [0.006, 0.037] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.028 [-0.049, -0.009] | -0.007 [-0.025, 0.010] | 0.006 [-0.015, 0.026] |
| ordinary | 1603 | 0.001 [-0.002, 0.005] | 0.004 [0.001, 0.008] | 0.003 [0.001, 0.005] |
| quarter_end | 31 | -0.049 [-0.129, 0.026] | 0.006 [-0.063, 0.083] | 0.029 [-0.035, 0.101] |
| tax_date | 89 | -0.020 [-0.042, -0.001] | -0.002 [-0.030, 0.024] | 0.024 [-0.020, 0.068] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 313 | -0.002 [-0.004, 0.000] | 0.000 [-0.000, 0.001] | 0.001 [-0.001, 0.002] |
| 2 | 41 | -0.016 [–] | 0.018 [–] | 0.044 [–] |
| 3 | 478 | -0.011 [-0.025, 0.004] | 0.010 [-0.003, 0.024] | 0.013 [0.000, 0.025] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.211, 0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.350, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.375, 0.000] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.286, 0.000] |

## risk_logistic+combined against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.007] |
| 2 | -0.005 [-0.013, 0.002] |
| 3 | -0.004 [-0.014, 0.005] |
| 4 | -0.003 [-0.013, 0.005] |
| 5 | -0.001 [-0.012, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.060 [-0.099, -0.025] | -0.028 [-0.075, 0.015] | -0.016 [-0.069, 0.032] |
| 2020 | 251 | 0.000 [-0.009, 0.007] | -0.001 [-0.006, 0.004] | 0.003 [-0.004, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.001 [-0.000, 0.002] | -0.001 [-0.003, 0.001] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.019 [-0.033, -0.006] | 0.013 [0.003, 0.026] | 0.011 [0.003, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.022 [-0.041, -0.004] | 0.009 [-0.009, 0.029] | 0.011 [-0.011, 0.034] |
| ordinary | 1603 | -0.013 [-0.022, -0.004] | -0.006 [-0.017, 0.003] | -0.004 [-0.015, 0.005] |
| quarter_end | 31 | -0.064 [-0.142, 0.005] | -0.004 [-0.091, 0.084] | 0.002 [-0.070, 0.068] |
| tax_date | 89 | -0.019 [-0.044, 0.004] | 0.013 [-0.007, 0.035] | 0.023 [-0.009, 0.066] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [0.000, 0.001] | -0.000 [-0.001, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.002 [-0.001, 0.004] | -0.000 [-0.001, 0.000] | 0.001 [0.000, 0.003] |
| 2 | 41 | -0.073 [–] | 0.008 [–] | 0.033 [–] |
| 3 | 478 | -0.052 [-0.083, -0.023] | -0.016 [-0.055, 0.019] | -0.009 [-0.052, 0.029] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.393, -0.056] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.417 [-0.667, -0.167] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.238 [-0.400, -0.083] |

## risk_logistic+combined against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.006, 0.015] |
| 2 | 0.009 [0.003, 0.014] |
| 3 | 0.007 [0.001, 0.013] |
| 4 | 0.006 [0.000, 0.012] |
| 5 | 0.006 [-0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.025, 0.014] | -0.027 [-0.049, -0.005] | -0.029 [-0.054, -0.005] |
| 2020 | 251 | 0.033 [0.024, 0.042] | 0.038 [0.028, 0.047] | 0.038 [0.027, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.005 [0.001, 0.009] | 0.003 [-0.000, 0.005] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.010 [0.001, 0.020] | 0.011 [0.003, 0.021] | 0.005 [-0.001, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.026 [0.012, 0.041] | 0.021 [0.006, 0.036] | 0.019 [0.000, 0.039] |
| ordinary | 1603 | 0.006 [0.001, 0.010] | 0.002 [-0.004, 0.007] | 0.000 [-0.006, 0.006] |
| quarter_end | 31 | 0.067 [-0.013, 0.144] | 0.084 [0.015, 0.148] | 0.092 [-0.008, 0.193] |
| tax_date | 89 | 0.048 [0.029, 0.068] | 0.051 [0.031, 0.070] | 0.050 [0.026, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.010 [0.008, 0.011] | 0.010 [0.008, 0.011] | 0.010 [0.008, 0.011] |
| 1 | 313 | 0.030 [0.024, 0.036] | 0.031 [0.024, 0.037] | 0.029 [0.022, 0.036] |
| 2 | 41 | -0.026 [–] | -0.006 [–] | 0.014 [–] |
| 3 | 478 | 0.003 [-0.013, 0.019] | -0.013 [-0.032, 0.007] | -0.018 [-0.040, 0.002] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.250, 0.182] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.556, 0.003] |
| quarter_end | 3 | 0.667 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | -0.143 [-0.375, 0.095] |

## risk_logistic+combined against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.002] |
| 2 | -0.001 [-0.008, 0.005] |
| 3 | 0.001 [-0.006, 0.007] |
| 4 | -0.002 [-0.010, 0.004] |
| 5 | -0.002 [-0.009, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.022 [-0.053, 0.004] | -0.027 [-0.056, 0.001] | -0.026 [-0.055, 0.001] |
| 2020 | 251 | 0.010 [0.000, 0.018] | 0.026 [0.018, 0.033] | 0.020 [0.012, 0.027] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.005 [0.001, 0.011] | 0.003 [0.002, 0.005] | 0.002 [-0.000, 0.004] |
| 2025-26 | 249 | -0.016 [-0.043, 0.005] | 0.005 [-0.013, 0.021] | -0.002 [-0.025, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.005 [-0.012, 0.023] | 0.011 [-0.001, 0.024] | 0.010 [-0.010, 0.030] |
| ordinary | 1603 | -0.006 [-0.015, 0.001] | -0.002 [-0.011, 0.005] | -0.006 [-0.013, 0.002] |
| quarter_end | 31 | 0.006 [-0.104, 0.111] | 0.049 [-0.042, 0.138] | 0.066 [-0.025, 0.163] |
| tax_date | 89 | 0.013 [-0.013, 0.038] | 0.024 [0.008, 0.040] | 0.024 [0.002, 0.057] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.001, 0.003] | 0.003 [0.003, 0.004] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.008 [0.005, 0.010] | 0.020 [0.016, 0.023] | 0.014 [0.011, 0.018] |
| 2 | 41 | -0.060 [–] | -0.039 [–] | -0.044 [–] |
| 3 | 478 | -0.021 [-0.048, 0.002] | -0.013 [-0.038, 0.010] | -0.016 [-0.042, 0.006] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.227, 0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.417, -0.071] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.333 [-0.600, 0.000] |
| quarter_end | 3 | 0.667 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | -0.143 [-0.357, 0.083] |

## risk_logistic+combined against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.007, 0.001] |
| 2 | -0.003 [-0.007, 0.002] |
| 3 | -0.002 [-0.007, 0.002] |
| 4 | -0.006 [-0.010, -0.002] |
| 5 | -0.006 [-0.010, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.007 [-0.026, 0.011] | -0.017 [-0.035, -0.000] | -0.031 [-0.048, -0.016] |
| 2020 | 251 | -0.005 [-0.014, 0.003] | 0.005 [-0.004, 0.015] | 0.007 [0.001, 0.014] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.003 [-0.000, 0.010] | -0.001 [-0.004, 0.001] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.008 [-0.021, 0.003] | 0.004 [-0.007, 0.014] | -0.005 [-0.016, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.027 [-0.048, -0.008] | -0.011 [-0.032, 0.009] | -0.024 [-0.042, -0.009] |
| ordinary | 1603 | 0.002 [-0.002, 0.006] | -0.001 [-0.005, 0.003] | -0.003 [-0.006, -0.000] |
| quarter_end | 31 | -0.058 [-0.146, 0.027] | -0.025 [-0.073, 0.025] | -0.002 [-0.068, 0.067] |
| tax_date | 89 | -0.020 [-0.043, 0.000] | -0.002 [-0.035, 0.028] | -0.030 [-0.062, -0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.003] | 0.000 [-0.001, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 313 | -0.002 [-0.005, 0.000] | 0.003 [-0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.023 [–] | 0.024 [–] | 0.019 [–] |
| 3 | 478 | -0.010 [-0.026, 0.005] | -0.014 [-0.029, 0.001] | -0.025 [-0.039, -0.011] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.258, 0.038] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.353, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.364, 0.000] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.143 [-0.292, 0.000] |

## risk_logistic+combined against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.004, 0.004] |
| 2 | -0.002 [-0.006, 0.003] |
| 3 | -0.004 [-0.008, -0.001] |
| 4 | -0.004 [-0.008, -0.001] |
| 5 | -0.005 [-0.009, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.021, 0.015] | -0.017 [-0.035, 0.001] | -0.023 [-0.038, -0.009] |
| 2020 | 251 | 0.007 [-0.000, 0.015] | 0.000 [-0.004, 0.005] | 0.004 [-0.000, 0.010] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.002 [-0.007, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.003 [-0.009, 0.002] | -0.004 [-0.012, 0.003] | -0.004 [-0.011, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.004 [-0.023, 0.015] | -0.010 [-0.027, 0.006] | -0.005 [-0.018, 0.007] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | -0.002 [-0.006, 0.002] | -0.003 [-0.006, -0.001] |
| quarter_end | 31 | -0.024 [-0.088, 0.024] | -0.041 [-0.113, 0.020] | -0.048 [-0.120, 0.014] |
| tax_date | 89 | -0.028 [-0.068, 0.006] | -0.023 [-0.070, 0.016] | -0.023 [-0.065, 0.015] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | 0.000 [-0.001, 0.001] | 0.001 [0.000, 0.001] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.002 [-0.005, 0.000] |
| 2 | 41 | 0.007 [–] | -0.017 [–] | -0.007 [–] |
| 3 | 478 | -0.003 [-0.017, 0.012] | -0.016 [-0.031, -0.002] | -0.019 [-0.031, -0.007] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.333, -0.065] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.357, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.500, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.143 [-0.292, 0.000] |

## risk_logistic+combined against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.011 [-0.019, -0.004] |
| 2 | -0.008 [-0.015, -0.001] |
| 3 | -0.007 [-0.014, -0.000] |
| 4 | -0.011 [-0.020, -0.004] |
| 5 | -0.011 [-0.020, -0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.047 [-0.080, -0.020] | -0.042 [-0.074, -0.015] | -0.059 [-0.095, -0.027] |
| 2020 | 251 | 0.002 [-0.008, 0.014] | 0.006 [-0.003, 0.016] | 0.007 [-0.000, 0.017] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.006 [0.001, 0.014] | 0.001 [-0.002, 0.004] | 0.003 [0.001, 0.006] |
| 2025-26 | 249 | -0.019 [-0.045, 0.002] | 0.003 [-0.011, 0.018] | -0.007 [-0.033, 0.016] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.033 [-0.056, -0.012] | -0.011 [-0.030, 0.008] | -0.026 [-0.044, -0.010] |
| ordinary | 1603 | -0.007 [-0.016, -0.000] | -0.006 [-0.014, 0.000] | -0.009 [-0.017, -0.001] |
| quarter_end | 31 | -0.058 [-0.150, 0.026] | -0.025 [-0.076, 0.026] | -0.002 [-0.068, 0.066] |
| tax_date | 89 | -0.020 [-0.043, 0.000] | -0.002 [-0.033, 0.030] | -0.030 [-0.060, -0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.003 [0.001, 0.005] | 0.002 [0.001, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | -0.002 [-0.004, 0.000] | 0.003 [-0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.063 [–] | -0.020 [–] | -0.036 [–] |
| 3 | 478 | -0.042 [-0.069, -0.017] | -0.030 [-0.057, -0.007] | -0.045 [-0.075, -0.018] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.438, -0.095] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.353 [-0.545, -0.167] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.500 [-0.727, -0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.333 [-0.500, -0.167] |

## risk_logistic+combined against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, -0.001] |
| 2 | -0.006 [-0.014, 0.001] |
| 3 | -0.008 [-0.016, -0.002] |
| 4 | -0.010 [-0.018, -0.003] |
| 5 | -0.010 [-0.019, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.073, -0.014] | -0.041 [-0.074, -0.014] | -0.051 [-0.084, -0.022] |
| 2020 | 251 | 0.014 [0.001, 0.030] | 0.001 [-0.003, 0.005] | 0.004 [-0.002, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.003 [0.000, 0.007] | 0.000 [-0.004, 0.004] | 0.000 [-0.004, 0.004] |
| 2025-26 | 249 | -0.014 [-0.037, 0.004] | -0.005 [-0.024, 0.011] | -0.007 [-0.031, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.010 [-0.030, 0.011] | -0.010 [-0.027, 0.007] | -0.007 [-0.020, 0.005] |
| ordinary | 1603 | -0.007 [-0.015, 0.000] | -0.007 [-0.015, -0.000] | -0.009 [-0.018, -0.002] |
| quarter_end | 31 | -0.024 [-0.086, 0.024] | -0.041 [-0.113, 0.018] | -0.048 [-0.124, 0.015] |
| tax_date | 89 | -0.028 [-0.069, 0.006] | -0.023 [-0.071, 0.015] | -0.023 [-0.064, 0.014] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.001, 0.003] | 0.002 [0.001, 0.003] | 0.002 [0.001, 0.004] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | -0.002 [-0.006, 0.000] |
| 2 | 41 | -0.033 [–] | -0.061 [–] | -0.061 [–] |
| 3 | 478 | -0.034 [-0.059, -0.008] | -0.032 [-0.059, -0.010] | -0.039 [-0.068, -0.013] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.433, -0.095] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.353 [-0.550, -0.167] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.500 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.500 [-0.750, -0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.333 [-0.500, -0.167] |

## risk_logistic+combined_nogate against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.005, 0.017] |
| 2 | 0.015 [0.002, 0.029] |
| 3 | 0.013 [0.001, 0.026] |
| 4 | 0.011 [-0.000, 0.023] |
| 5 | 0.008 [-0.003, 0.020] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.043 [-0.006, 0.093] | 0.065 [0.011, 0.125] | 0.053 [0.003, 0.105] |
| 2020 | 251 | -0.026 [-0.045, -0.012] | -0.018 [-0.028, -0.006] | -0.036 [-0.049, -0.024] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.001 [-0.000, 0.004] | 0.002 [-0.000, 0.004] | 0.002 [-0.000, 0.005] |
| 2025-26 | 249 | 0.002 [-0.009, 0.012] | 0.016 [0.001, 0.036] | 0.027 [0.007, 0.052] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.040, -0.003] | 0.006 [-0.016, 0.028] | 0.014 [-0.014, 0.040] |
| ordinary | 1603 | 0.008 [-0.003, 0.021] | 0.012 [-0.001, 0.027] | 0.004 [-0.008, 0.017] |
| quarter_end | 31 | -0.025 [-0.111, 0.056] | 0.046 [-0.049, 0.144] | 0.076 [0.001, 0.155] |
| tax_date | 89 | 0.008 [-0.030, 0.046] | 0.021 [-0.007, 0.052] | 0.047 [0.008, 0.094] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | -0.000 [-0.001, 0.000] | -0.002 [-0.003, -0.002] |
| 1 | 313 | -0.009 [-0.013, -0.006] | -0.010 [-0.013, -0.007] | -0.019 [-0.024, -0.013] |
| 2 | 41 | -0.017 [–] | 0.034 [–] | 0.047 [–] |
| 3 | 478 | 0.028 [-0.013, 0.070] | 0.054 [0.009, 0.103] | 0.044 [0.002, 0.087] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.125, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.188, 0.191] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.158, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.154, 0.154] |

## risk_logistic+combined_nogate against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.006 [-0.012, -0.000] |
| 2 | 0.003 [-0.004, 0.010] |
| 3 | 0.005 [-0.003, 0.015] |
| 4 | 0.005 [-0.002, 0.014] |
| 5 | 0.002 [-0.005, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.010 [-0.034, 0.017] | 0.027 [-0.011, 0.068] | 0.029 [0.003, 0.057] |
| 2020 | 251 | -0.020 [-0.037, -0.005] | -0.019 [-0.025, -0.013] | -0.035 [-0.044, -0.027] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [-0.002, 0.007] | 0.002 [-0.000, 0.005] |
| 2025-26 | 249 | -0.011 [-0.018, -0.005] | 0.021 [0.003, 0.042] | 0.018 [0.004, 0.036] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.015 [-0.039, 0.008] | 0.021 [-0.001, 0.046] | 0.019 [-0.008, 0.047] |
| ordinary | 1603 | -0.006 [-0.011, -0.001] | 0.002 [-0.006, 0.009] | -0.003 [-0.008, 0.001] |
| quarter_end | 31 | -0.040 [-0.140, 0.048] | 0.037 [-0.079, 0.152] | 0.050 [-0.040, 0.138] |
| tax_date | 89 | 0.009 [-0.023, 0.048] | 0.036 [-0.008, 0.088] | 0.046 [-0.006, 0.108] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.001, 0.000] | -0.001 [-0.002, 0.001] | -0.003 [-0.003, -0.002] |
| 1 | 313 | -0.006 [-0.009, -0.004] | -0.010 [-0.013, -0.008] | -0.018 [-0.024, -0.011] |
| 2 | 41 | -0.074 [–] | 0.024 [–] | 0.036 [–] |
| 3 | 478 | -0.013 [-0.033, 0.009] | 0.027 [-0.004, 0.061] | 0.021 [-0.002, 0.046] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.296, -0.029] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.300, 0.067] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.444, 0.105] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.243, 0.050] |

## risk_logistic+combined_nogate against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.019 [0.010, 0.028] |
| 2 | 0.017 [0.009, 0.026] |
| 3 | 0.017 [0.009, 0.026] |
| 4 | 0.015 [0.008, 0.022] |
| 5 | 0.009 [0.002, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.045 [0.007, 0.087] | 0.029 [-0.011, 0.070] | 0.016 [-0.016, 0.049] |
| 2020 | 251 | 0.013 [-0.002, 0.027] | 0.020 [0.011, 0.029] | 0.001 [-0.012, 0.013] |
| 2021-23 | 748 | 0.013 [0.011, 0.014] | 0.013 [0.011, 0.014] | 0.009 [0.007, 0.011] |
| 2024 | 250 | 0.005 [0.001, 0.009] | 0.005 [0.002, 0.009] | 0.003 [0.000, 0.006] |
| 2025-26 | 249 | 0.018 [0.003, 0.036] | 0.018 [0.003, 0.035] | 0.013 [0.003, 0.025] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.033 [0.007, 0.062] | 0.033 [0.012, 0.055] | 0.027 [0.004, 0.053] |
| ordinary | 1603 | 0.013 [0.005, 0.023] | 0.010 [0.001, 0.019] | 0.001 [-0.006, 0.009] |
| quarter_end | 31 | 0.091 [0.009, 0.165] | 0.125 [0.066, 0.186] | 0.139 [0.068, 0.212] |
| tax_date | 89 | 0.076 [0.045, 0.114] | 0.074 [0.037, 0.115] | 0.073 [0.031, 0.114] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.007 [0.005, 0.008] |
| 1 | 313 | 0.022 [0.017, 0.028] | 0.021 [0.016, 0.027] | 0.010 [0.005, 0.015] |
| 2 | 41 | -0.028 [–] | 0.010 [–] | 0.016 [–] |
| 3 | 478 | 0.042 [0.011, 0.077] | 0.031 [-0.001, 0.066] | 0.012 [-0.013, 0.040] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.118, 0.192] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.267, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.000 [-0.176, 0.177] |

## risk_logistic+combined_nogate against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.004 [-0.003, 0.012] |
| 2 | 0.007 [-0.001, 0.016] |
| 3 | 0.010 [0.003, 0.019] |
| 4 | 0.006 [-0.001, 0.014] |
| 5 | 0.001 [-0.006, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.028 [-0.003, 0.061] | 0.029 [-0.008, 0.067] | 0.018 [-0.013, 0.050] |
| 2020 | 251 | -0.010 [-0.028, 0.005] | 0.008 [0.003, 0.012] | -0.017 [-0.027, -0.008] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | 0.003 [0.002, 0.004] | -0.003 [-0.004, -0.002] |
| 2024 | 250 | 0.005 [0.001, 0.012] | 0.005 [0.002, 0.011] | 0.003 [0.001, 0.007] |
| 2025-26 | 249 | -0.008 [-0.030, 0.011] | 0.012 [-0.006, 0.031] | 0.005 [-0.017, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.012, 0.037] | 0.024 [0.003, 0.045] | 0.018 [-0.009, 0.044] |
| ordinary | 1603 | 0.000 [-0.006, 0.007] | 0.005 [-0.002, 0.013] | -0.005 [-0.012, 0.002] |
| quarter_end | 31 | 0.030 [-0.091, 0.151] | 0.090 [-0.035, 0.221] | 0.114 [0.004, 0.227] |
| tax_date | 89 | 0.041 [0.005, 0.089] | 0.047 [-0.001, 0.106] | 0.047 [-0.002, 0.105] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.000, 0.003] | 0.002 [0.001, 0.004] | -0.001 [-0.002, 0.000] |
| 1 | 313 | -0.000 [-0.003, 0.002] | 0.010 [0.008, 0.011] | -0.005 [-0.009, -0.001] |
| 2 | 41 | -0.061 [–] | -0.023 [–] | -0.041 [–] |
| 3 | 478 | 0.018 [-0.007, 0.045] | 0.030 [0.001, 0.062] | 0.014 [-0.012, 0.041] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.174, 0.241] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.300, 0.176] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.400, 0.250] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.333 [–] |
| 3 | 21 | 0.000 [-0.241, 0.250] |

## risk_logistic+combined_nogate against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.005, 0.017] |
| 2 | 0.005 [-0.004, 0.016] |
| 3 | 0.007 [-0.002, 0.018] |
| 4 | 0.003 [-0.006, 0.013] |
| 5 | -0.003 [-0.012, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.043 [-0.006, 0.094] | 0.038 [-0.009, 0.089] | 0.013 [-0.030, 0.060] |
| 2020 | 251 | -0.025 [-0.042, -0.012] | -0.013 [-0.020, -0.005] | -0.030 [-0.042, -0.018] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.004 [-0.000, 0.011] | 0.001 [-0.000, 0.003] | 0.002 [-0.000, 0.007] |
| 2025-26 | 249 | 0.000 [-0.010, 0.009] | 0.011 [-0.001, 0.027] | 0.002 [-0.005, 0.011] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.041, -0.002] | 0.001 [-0.013, 0.017] | -0.016 [-0.037, 0.003] |
| ordinary | 1603 | 0.008 [-0.002, 0.021] | 0.007 [-0.004, 0.019] | -0.002 [-0.012, 0.009] |
| quarter_end | 31 | -0.034 [-0.133, 0.061] | 0.016 [-0.059, 0.091] | 0.045 [-0.023, 0.118] |
| tax_date | 89 | 0.008 [-0.028, 0.047] | 0.022 [-0.012, 0.056] | -0.008 [-0.039, 0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.002] | -0.000 [-0.001, 0.000] | -0.003 [-0.003, -0.002] |
| 1 | 313 | -0.009 [-0.013, -0.006] | -0.007 [-0.011, -0.001] | -0.019 [-0.024, -0.014] |
| 2 | 41 | -0.025 [–] | 0.040 [–] | 0.022 [–] |
| 3 | 478 | 0.028 [-0.011, 0.070] | 0.030 [-0.008, 0.071] | 0.006 [-0.030, 0.043] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.174, 0.100] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.182, 0.190] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | 0.000 [-0.150, 0.154] |

## risk_logistic+combined_nogate against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [-0.001, 0.019] |
| 2 | 0.007 [-0.003, 0.018] |
| 3 | 0.005 [-0.004, 0.015] |
| 4 | 0.004 [-0.004, 0.014] |
| 5 | -0.002 [-0.010, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [0.001, 0.098] | 0.038 [-0.005, 0.087] | 0.021 [-0.021, 0.068] |
| 2020 | 251 | -0.013 [-0.019, -0.007] | -0.018 [-0.025, -0.011] | -0.033 [-0.042, -0.024] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.005 [0.000, 0.011] | 0.003 [0.000, 0.006] | 0.003 [0.000, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.003, 0.010] | 0.002 [-0.002, 0.008] | 0.003 [-0.003, 0.011] |
| ordinary | 1603 | 0.009 [-0.002, 0.022] | 0.006 [-0.004, 0.017] | -0.002 [-0.012, 0.009] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.000, -0.000] | -0.000 [-0.001, -0.000] | -0.002 [-0.003, -0.001] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.010 [-0.013, -0.007] | -0.022 [-0.026, -0.017] |
| 2 | 41 | 0.005 [–] | -0.001 [–] | -0.004 [–] |
| 3 | 478 | 0.036 [0.000, 0.078] | 0.028 [-0.007, 0.068] | 0.012 [-0.021, 0.050] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.286, 0.042] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.000 [-0.182, 0.200] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.286, 0.286] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | 0.000 [-0.150, 0.154] |

## risk_logistic+combined_nogate against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.010, 0.005] |
| 2 | 0.000 [-0.006, 0.008] |
| 3 | 0.003 [-0.004, 0.010] |
| 4 | -0.003 [-0.009, 0.004] |
| 5 | -0.008 [-0.015, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.003 [-0.027, 0.035] | 0.014 [-0.020, 0.048] | -0.015 [-0.044, 0.014] |
| 2020 | 251 | -0.018 [-0.035, -0.001] | -0.012 [-0.019, -0.004] | -0.030 [-0.043, -0.018] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.000 [-0.001, 0.000] | -0.005 [-0.006, -0.003] |
| 2024 | 250 | 0.007 [0.001, 0.015] | 0.004 [0.001, 0.007] | 0.005 [0.001, 0.009] |
| 2025-26 | 249 | -0.011 [-0.026, 0.003] | 0.010 [-0.004, 0.026] | -0.000 [-0.023, 0.022] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.026 [-0.045, -0.009] | 0.001 [-0.013, 0.017] | -0.019 [-0.039, -0.002] |
| ordinary | 1603 | -0.000 [-0.007, 0.007] | 0.002 [-0.006, 0.010] | -0.008 [-0.015, -0.001] |
| quarter_end | 31 | -0.034 [-0.125, 0.059] | 0.016 [-0.061, 0.090] | 0.045 [-0.022, 0.121] |
| tax_date | 89 | 0.008 [-0.031, 0.048] | 0.022 [-0.011, 0.057] | -0.008 [-0.039, 0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.000, 0.004] | 0.001 [-0.000, 0.003] | -0.001 [-0.002, 0.001] |
| 1 | 313 | -0.009 [-0.013, -0.006] | -0.007 [-0.011, -0.001] | -0.019 [-0.024, -0.014] |
| 2 | 41 | -0.065 [–] | -0.004 [–] | -0.033 [–] |
| 3 | 478 | -0.003 [-0.029, 0.025] | 0.013 [-0.015, 0.040] | -0.014 [-0.039, 0.011] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.324, -0.077] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.346, -0.048] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.462, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.190 [-0.333, -0.059] |

## risk_logistic+combined_nogate against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.006, 0.006] |
| 2 | 0.002 [-0.005, 0.008] |
| 3 | 0.001 [-0.006, 0.008] |
| 4 | -0.002 [-0.007, 0.004] |
| 5 | -0.007 [-0.013, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.007 [-0.019, 0.037] | 0.014 [-0.018, 0.043] | -0.007 [-0.033, 0.020] |
| 2020 | 251 | -0.006 [-0.018, 0.010] | -0.017 [-0.024, -0.009] | -0.033 [-0.042, -0.024] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | -0.001 [-0.001, 0.000] | -0.005 [-0.006, -0.003] |
| 2024 | 250 | 0.003 [0.001, 0.007] | 0.002 [0.001, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.006 [-0.023, 0.006] | 0.002 [-0.013, 0.016] | 0.001 [-0.020, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.003 [-0.008, 0.001] | 0.002 [-0.002, 0.008] | 0.000 [-0.003, 0.004] |
| ordinary | 1603 | -0.000 [-0.006, 0.008] | 0.001 [-0.007, 0.009] | -0.008 [-0.015, -0.001] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.001 [0.000, 0.003] | -0.001 [-0.002, 0.001] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.010 [-0.012, -0.007] | -0.022 [-0.026, -0.017] |
| 2 | 41 | -0.035 [–] | -0.046 [–] | -0.059 [–] |
| 3 | 478 | 0.005 [-0.017, 0.030] | 0.011 [-0.015, 0.036] | -0.008 [-0.030, 0.015] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.321, -0.077] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.333, -0.042] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.455, -0.077] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.190 [-0.333, -0.062] |

## risk_logistic+combined_nogate against risk_logistic+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [-0.001, 0.018] |
| 2 | 0.008 [-0.002, 0.020] |
| 3 | 0.009 [-0.001, 0.021] |
| 4 | 0.009 [-0.001, 0.020] |
| 5 | 0.003 [-0.007, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.050 [0.009, 0.096] | 0.055 [0.007, 0.110] | 0.045 [-0.002, 0.099] |
| 2020 | 251 | -0.020 [-0.032, -0.009] | -0.018 [-0.028, -0.008] | -0.037 [-0.050, -0.025] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.004] |
| 2024 | 250 | 0.000 [-0.000, 0.001] | 0.002 [-0.000, 0.007] | 0.002 [-0.000, 0.006] |
| 2025-26 | 249 | 0.008 [-0.000, 0.018] | 0.007 [-0.001, 0.016] | 0.007 [-0.001, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.007 [-0.014, 0.027] | 0.012 [-0.004, 0.029] | 0.008 [-0.006, 0.023] |
| ordinary | 1603 | 0.007 [-0.003, 0.018] | 0.008 [-0.003, 0.021] | 0.001 [-0.009, 0.013] |
| quarter_end | 31 | 0.024 [-0.025, 0.089] | 0.041 [-0.021, 0.112] | 0.048 [-0.013, 0.125] |
| tax_date | 89 | 0.028 [-0.006, 0.070] | 0.023 [-0.016, 0.070] | 0.023 [-0.014, 0.064] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, -0.000] | -0.001 [-0.002, 0.001] | -0.003 [-0.004, -0.002] |
| 1 | 313 | -0.008 [-0.009, -0.006] | -0.010 [-0.013, -0.008] | -0.019 [-0.025, -0.013] |
| 2 | 41 | -0.002 [–] | 0.016 [–] | 0.003 [–] |
| 3 | 478 | 0.039 [0.004, 0.075] | 0.044 [0.004, 0.088] | 0.031 [-0.008, 0.076] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.080, 0.222] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.389] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.067, 0.462] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.143 [0.000, 0.308] |

## risk_gbm+combined_no_factor against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.006 [0.001, 0.011] |
| 3 | 0.003 [-0.000, 0.007] |
| 4 | 0.003 [-0.000, 0.006] |
| 5 | 0.007 [0.003, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.019, 0.013] | 0.016 [-0.001, 0.034] | 0.021 [0.007, 0.036] |
| 2020 | 251 | 0.003 [-0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.003, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.010 [-0.028, 0.002] | 0.003 [-0.002, 0.009] | 0.022 [0.004, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.050, -0.002] | -0.007 [-0.022, 0.007] | 0.019 [0.008, 0.032] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | 0.005 [0.002, 0.010] | 0.005 [0.002, 0.008] |
| quarter_end | 31 | -0.011 [-0.067, 0.044] | -0.002 [-0.066, 0.064] | 0.037 [0.000, 0.080] |
| tax_date | 89 | -0.039 [-0.077, -0.012] | -0.015 [-0.058, 0.022] | 0.018 [-0.036, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.001 [-0.001, 0.002] |
| 2 | 41 | 0.000 [–] | -0.007 [–] | 0.019 [–] |
| 3 | 478 | -0.009 [-0.024, 0.006] | 0.014 [0.000, 0.028] | 0.026 [0.012, 0.041] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.233, 0.000] on 26 onsets.

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
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_factor against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.006] |
| 2 | -0.006 [-0.014, 0.001] |
| 3 | -0.004 [-0.013, 0.005] |
| 4 | -0.003 [-0.011, 0.005] |
| 5 | 0.001 [-0.008, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.057 [-0.096, -0.023] | -0.022 [-0.066, 0.020] | -0.004 [-0.049, 0.039] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.042, -0.009] | 0.007 [-0.002, 0.020] | 0.014 [0.001, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.007, 0.025] | 0.024 [0.004, 0.047] |
| ordinary | 1603 | -0.012 [-0.021, -0.004] | -0.005 [-0.014, 0.003] | -0.002 [-0.012, 0.007] |
| quarter_end | 31 | -0.026 [-0.093, 0.026] | -0.011 [-0.075, 0.055] | 0.010 [-0.039, 0.057] |
| tax_date | 89 | -0.038 [-0.073, -0.008] | 0.000 [-0.034, 0.028] | 0.017 [-0.013, 0.049] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.003] |
| 2 | 41 | -0.057 [–] | -0.017 [–] | 0.008 [–] |
| 3 | 478 | -0.050 [-0.081, -0.022] | -0.012 [-0.048, 0.021] | 0.003 [-0.033, 0.038] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.111] on 26 onsets.

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
| ordinary | 12 | -0.333 [-0.583, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.346, -0.053] |

## risk_gbm+combined_no_factor against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.007, 0.016] |
| 2 | 0.008 [0.002, 0.014] |
| 3 | 0.007 [0.001, 0.013] |
| 4 | 0.007 [0.001, 0.012] |
| 5 | 0.008 [0.003, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.023, 0.018] | -0.020 [-0.043, 0.001] | -0.016 [-0.039, 0.004] |
| 2020 | 251 | 0.042 [0.034, 0.050] | 0.038 [0.028, 0.047] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.015] | 0.005 [-0.007, 0.018] | 0.008 [-0.002, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.045] | 0.020 [0.011, 0.028] | 0.032 [0.020, 0.047] |
| ordinary | 1603 | 0.007 [0.002, 0.011] | 0.003 [-0.002, 0.008] | 0.003 [-0.003, 0.007] |
| quarter_end | 31 | 0.105 [0.018, 0.199] | 0.077 [-0.018, 0.173] | 0.100 [0.003, 0.194] |
| tax_date | 89 | 0.029 [-0.003, 0.057] | 0.038 [0.007, 0.065] | 0.044 [0.013, 0.073] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.031 [0.025, 0.038] | 0.029 [0.021, 0.036] |
| 2 | 41 | -0.010 [–] | -0.031 [–] | -0.012 [–] |
| 3 | 478 | 0.006 [-0.011, 0.023] | -0.009 [-0.030, 0.010] | -0.006 [-0.025, 0.012] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.273, 0.120] on 26 onsets.

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
| ordinary | 12 | -0.167 [-0.500, 0.182] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.334, 0.154] |

## risk_gbm+combined_no_factor against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.003] |
| 2 | -0.002 [-0.009, 0.005] |
| 3 | 0.001 [-0.006, 0.007] |
| 4 | -0.002 [-0.008, 0.004] |
| 5 | 0.001 [-0.005, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.019 [-0.052, 0.009] | -0.020 [-0.047, 0.005] | -0.014 [-0.040, 0.011] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.026] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.004] | 0.001 [-0.001, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.052, 0.003] | -0.001 [-0.026, 0.021] | 0.000 [-0.023, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.016, 0.033] | 0.011 [-0.002, 0.023] | 0.023 [0.009, 0.041] |
| ordinary | 1603 | -0.006 [-0.014, 0.002] | -0.001 [-0.009, 0.006] | -0.003 [-0.011, 0.003] |
| quarter_end | 31 | 0.045 [-0.009, 0.106] | 0.042 [-0.012, 0.103] | 0.074 [0.018, 0.143] |
| tax_date | 89 | -0.006 [-0.036, 0.018] | 0.011 [-0.008, 0.032] | 0.018 [-0.003, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.003 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.020 [0.016, 0.024] | 0.014 [0.010, 0.018] |
| 2 | 41 | -0.044 [–] | -0.064 [–] | -0.069 [–] |
| 3 | 478 | -0.018 [-0.047, 0.007] | -0.009 [-0.033, 0.012] | -0.004 [-0.026, 0.018] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.242, 0.103] on 26 onsets.

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
| ordinary | 12 | -0.250 [-0.530, 0.072] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.300, 0.125] |

## risk_gbm+combined_no_factor against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | -0.003 [-0.008, 0.001] |
| 3 | -0.002 [-0.006, 0.001] |
| 4 | -0.005 [-0.009, -0.002] |
| 5 | -0.003 [-0.006, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.020, 0.013] | -0.011 [-0.026, 0.006] | -0.019 [-0.031, -0.007] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.003, 0.014] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.012 [-0.029, 0.001] | -0.002 [-0.010, 0.004] | -0.002 [-0.009, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.046, -0.001] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.000] |
| ordinary | 1603 | 0.002 [-0.001, 0.006] | -0.000 [-0.003, 0.003] | -0.001 [-0.003, 0.001] |
| quarter_end | 31 | -0.020 [-0.077, 0.033] | -0.032 [-0.093, 0.026] | 0.006 [-0.026, 0.050] |
| tax_date | 89 | -0.040 [-0.075, -0.008] | -0.014 [-0.054, 0.022] | -0.036 [-0.083, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.007 [–] | -0.001 [–] | -0.006 [–] |
| 3 | 478 | -0.008 [-0.023, 0.007] | -0.010 [-0.023, 0.004] | -0.012 [-0.024, -0.001] |

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
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_factor against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.004, 0.005] |
| 2 | -0.002 [-0.007, 0.003] |
| 3 | -0.004 [-0.008, 0.000] |
| 4 | -0.004 [-0.008, -0.000] |
| 5 | -0.002 [-0.006, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.021, 0.020] | -0.011 [-0.029, 0.008] | -0.011 [-0.029, 0.006] |
| 2020 | 251 | 0.016 [0.003, 0.032] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.012, 0.000] | -0.004 [-0.012, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.007 [-0.018, 0.001] | -0.010 [-0.025, 0.002] | -0.002 [-0.013, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.029, 0.028] | -0.011 [-0.032, 0.011] | 0.007 [-0.013, 0.029] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | -0.001 [-0.004, 0.002] | -0.001 [-0.003, 0.001] |
| quarter_end | 31 | 0.014 [-0.099, 0.131] | -0.048 [-0.155, 0.058] | -0.040 [-0.133, 0.048] |
| tax_date | 89 | -0.047 [-0.106, 0.003] | -0.036 [-0.091, 0.016] | -0.029 [-0.090, 0.026] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.001 [-0.000, 0.001] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [-0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | 0.023 [–] | -0.042 [–] | -0.032 [–] |
| 3 | 478 | -0.000 [-0.018, 0.017] | -0.012 [-0.028, 0.003] | -0.006 [-0.021, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.394, -0.083] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.294, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.364, 0.000] |
| quarter_end | 3 | -0.667 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_factor against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.008 [-0.015, -0.002] |
| 3 | -0.006 [-0.013, -0.001] |
| 4 | -0.011 [-0.020, -0.004] |
| 5 | -0.009 [-0.017, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.076, -0.017] | -0.035 [-0.063, -0.010] | -0.047 [-0.079, -0.018] |
| 2020 | 251 | 0.011 [0.002, 0.026] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.015] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.007] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.024 [-0.053, -0.001] | -0.003 [-0.022, 0.012] | -0.005 [-0.029, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.055, -0.006] | -0.012 [-0.031, 0.007] | -0.014 [-0.026, -0.002] |
| ordinary | 1603 | -0.006 [-0.015, 0.001] | -0.005 [-0.012, 0.001] | -0.007 [-0.015, -0.000] |
| quarter_end | 31 | -0.020 [-0.079, 0.033] | -0.032 [-0.094, 0.025] | 0.006 [-0.027, 0.047] |
| tax_date | 89 | -0.040 [-0.077, -0.009] | -0.014 [-0.056, 0.024] | -0.036 [-0.080, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.001, 0.003] | 0.001 [0.000, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.047 [–] | -0.045 [–] | -0.061 [–] |
| 3 | 478 | -0.039 [-0.067, -0.014] | -0.027 [-0.050, -0.006] | -0.032 [-0.061, -0.007] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.469, -0.160] on 26 onsets.

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
| ordinary | 12 | -0.417 [-0.648, -0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.286 [-0.458, -0.120] |

## risk_gbm+combined_no_factor against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, 0.001] |
| 2 | -0.007 [-0.015, 0.000] |
| 3 | -0.008 [-0.016, -0.001] |
| 4 | -0.010 [-0.018, -0.002] |
| 5 | -0.008 [-0.015, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.041 [-0.073, -0.009] | -0.035 [-0.067, -0.006] | -0.039 [-0.072, -0.008] |
| 2020 | 251 | 0.023 [0.004, 0.048] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.005, 0.003] |
| 2025-26 | 249 | -0.019 [-0.044, 0.002] | -0.011 [-0.038, 0.010] | -0.004 [-0.029, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.037, 0.024] | -0.011 [-0.032, 0.010] | 0.005 [-0.016, 0.028] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.006 [-0.013, 0.001] | -0.007 [-0.015, -0.001] |
| quarter_end | 31 | 0.014 [-0.097, 0.132] | -0.048 [-0.158, 0.057] | -0.040 [-0.132, 0.055] |
| tax_date | 89 | -0.047 [-0.107, 0.005] | -0.036 [-0.095, 0.016] | -0.029 [-0.090, 0.030] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.001, 0.002] | 0.001 [0.000, 0.003] | 0.002 [0.001, 0.004] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | -0.017 [–] | -0.087 [–] | -0.087 [–] |
| 3 | 478 | -0.032 [-0.061, -0.003] | -0.029 [-0.055, -0.005] | -0.026 [-0.055, 0.001] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.465, -0.156] on 26 onsets.

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
| ordinary | 12 | -0.417 [-0.648, -0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.286 [-0.455, -0.125] |

## risk_gbm+combined_no_factor against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.001, 0.001] |
| 2 | 0.000 [-0.000, 0.000] |
| 3 | 0.000 [-0.000, 0.001] |
| 4 | 0.000 [-0.000, 0.001] |
| 5 | 0.000 [0.000, 0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.003, 0.003] | 0.001 [-0.001, 0.003] | 0.001 [0.000, 0.002] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2025-26 | 249 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [0.000, 0.000] |
| ordinary | 1603 | -0.000 [-0.001, 0.001] | 0.000 [-0.000, 0.001] | 0.000 [0.000, 0.001] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2 | 41 | 0.000 [–] | 0.000 [–] | 0.000 [–] |
| 3 | 478 | -0.000 [-0.003, 0.002] | 0.001 [-0.001, 0.002] | 0.001 [0.000, 0.002] |

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

## risk_gbm+combined_no_structural against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.007, 0.001] |
| 2 | 0.004 [-0.000, 0.008] |
| 3 | 0.002 [-0.001, 0.005] |
| 4 | 0.002 [-0.001, 0.005] |
| 5 | 0.005 [0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.007 [-0.027, 0.011] | 0.010 [-0.004, 0.024] | 0.012 [-0.008, 0.031] |
| 2020 | 251 | 0.003 [0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.003, 0.004] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.008, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.010 [-0.027, 0.002] | 0.003 [-0.002, 0.009] | 0.022 [0.004, 0.046] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.001] | -0.007 [-0.022, 0.007] | 0.019 [0.008, 0.032] |
| ordinary | 1603 | 0.001 [-0.003, 0.006] | 0.004 [0.001, 0.007] | 0.003 [-0.001, 0.007] |
| quarter_end | 31 | -0.011 [-0.068, 0.044] | -0.002 [-0.061, 0.064] | 0.037 [0.002, 0.081] |
| tax_date | 89 | -0.039 [-0.074, -0.010] | -0.015 [-0.058, 0.022] | 0.018 [-0.035, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.001 [-0.001, 0.002] |
| 2 | 41 | 0.001 [–] | -0.007 [–] | 0.019 [–] |
| 3 | 478 | -0.011 [-0.029, 0.005] | 0.009 [-0.003, 0.020] | 0.019 [0.002, 0.037] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.227, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.235, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.095 [-0.226, 0.000] |

## risk_gbm+combined_no_structural against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.025, -0.006] |
| 2 | -0.008 [-0.017, -0.000] |
| 3 | -0.005 [-0.015, 0.003] |
| 4 | -0.004 [-0.013, 0.005] |
| 5 | -0.000 [-0.010, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.060 [-0.102, -0.025] | -0.029 [-0.074, 0.011] | -0.013 [-0.061, 0.031] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.005, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, -0.000] |
| 2025-26 | 249 | -0.024 [-0.042, -0.008] | 0.008 [-0.002, 0.021] | 0.014 [0.000, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.008, 0.025] | 0.024 [0.003, 0.047] |
| ordinary | 1603 | -0.012 [-0.023, -0.004] | -0.007 [-0.017, 0.001] | -0.004 [-0.015, 0.005] |
| quarter_end | 31 | -0.026 [-0.088, 0.027] | -0.011 [-0.076, 0.052] | 0.010 [-0.041, 0.060] |
| tax_date | 89 | -0.038 [-0.076, -0.006] | 0.000 [-0.034, 0.029] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.003] |
| 2 | 41 | -0.056 [–] | -0.017 [–] | 0.008 [–] |
| 3 | 478 | -0.052 [-0.086, -0.023] | -0.018 [-0.054, 0.014] | -0.004 [-0.042, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.440, -0.120] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.438, -0.067] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.600, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.350, -0.055] |

## risk_gbm+combined_no_structural against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.005, 0.016] |
| 2 | 0.006 [0.000, 0.012] |
| 3 | 0.006 [0.000, 0.012] |
| 4 | 0.006 [-0.001, 0.011] |
| 5 | 0.007 [0.001, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.029, 0.016] | -0.027 [-0.051, -0.006] | -0.025 [-0.048, -0.002] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.027, 0.047] | 0.037 [0.026, 0.048] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.016] | 0.005 [-0.006, 0.019] | 0.008 [-0.002, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.043] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.047] |
| ordinary | 1603 | 0.006 [0.001, 0.011] | 0.002 [-0.004, 0.006] | 0.000 [-0.006, 0.006] |
| quarter_end | 31 | 0.105 [0.015, 0.195] | 0.077 [-0.019, 0.173] | 0.100 [0.007, 0.193] |
| tax_date | 89 | 0.029 [-0.003, 0.058] | 0.038 [0.008, 0.066] | 0.044 [0.013, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.031 [0.024, 0.038] | 0.029 [0.022, 0.036] |
| 2 | 41 | -0.010 [–] | -0.031 [–] | -0.012 [–] |
| 3 | 478 | 0.003 [-0.017, 0.021] | -0.014 [-0.035, 0.005] | -0.013 [-0.033, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.267, 0.120] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.474, 0.000] |
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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.333, 0.150] |

## risk_gbm+combined_no_structural against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.003] |
| 2 | -0.004 [-0.011, 0.003] |
| 3 | -0.000 [-0.007, 0.006] |
| 4 | -0.003 [-0.010, 0.004] |
| 5 | -0.001 [-0.008, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.023 [-0.054, 0.006] | -0.027 [-0.054, -0.003] | -0.023 [-0.052, 0.003] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.010, 0.026] |
| 2021-23 | 748 | 0.001 [0.001, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.004] | 0.001 [-0.002, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.020 [-0.052, 0.003] | -0.001 [-0.024, 0.020] | 0.000 [-0.024, 0.025] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.017, 0.032] | 0.011 [-0.002, 0.023] | 0.023 [0.008, 0.041] |
| ordinary | 1603 | -0.006 [-0.015, 0.001] | -0.003 [-0.011, 0.004] | -0.006 [-0.014, 0.002] |
| quarter_end | 31 | 0.045 [-0.007, 0.108] | 0.042 [-0.011, 0.107] | 0.074 [0.019, 0.141] |
| tax_date | 89 | -0.006 [-0.036, 0.017] | 0.011 [-0.007, 0.030] | 0.018 [-0.002, 0.043] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.003 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.020 [0.016, 0.024] | 0.014 [0.010, 0.018] |
| 2 | 41 | -0.043 [–] | -0.064 [–] | -0.069 [–] |
| 3 | 478 | -0.021 [-0.049, 0.004] | -0.015 [-0.038, 0.006] | -0.011 [-0.035, 0.011] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.235, 0.095] on 26 onsets.

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
| ordinary | 12 | -0.250 [-0.545, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.294, 0.125] |

## risk_gbm+combined_no_structural against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.007, 0.001] |
| 2 | -0.005 [-0.010, -0.001] |
| 3 | -0.004 [-0.007, 0.000] |
| 4 | -0.006 [-0.010, -0.003] |
| 5 | -0.005 [-0.009, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.008 [-0.027, 0.010] | -0.018 [-0.032, -0.004] | -0.028 [-0.044, -0.011] |
| 2020 | 251 | 0.004 [0.000, 0.008] | 0.005 [-0.003, 0.014] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.012 [-0.028, 0.001] | -0.002 [-0.010, 0.004] | -0.002 [-0.008, 0.004] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.001] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.002 [-0.002, 0.006] | -0.002 [-0.004, 0.001] | -0.003 [-0.006, 0.000] |
| quarter_end | 31 | -0.020 [-0.075, 0.032] | -0.032 [-0.091, 0.029] | 0.006 [-0.027, 0.046] |
| tax_date | 89 | -0.040 [-0.074, -0.008] | -0.014 [-0.055, 0.024] | -0.036 [-0.082, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.004, 0.003] |
| 2 | 41 | -0.007 [–] | -0.001 [–] | -0.006 [–] |
| 3 | 478 | -0.011 [-0.027, 0.006] | -0.015 [-0.028, -0.003] | -0.019 [-0.033, -0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.296, -0.037] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.280, 0.000] |
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
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_structural against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.005, 0.005] |
| 2 | -0.004 [-0.009, 0.001] |
| 3 | -0.005 [-0.010, -0.001] |
| 4 | -0.005 [-0.010, -0.001] |
| 5 | -0.004 [-0.009, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.027, 0.018] | -0.017 [-0.036, 0.001] | -0.020 [-0.043, 0.003] |
| 2020 | 251 | 0.016 [0.003, 0.032] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.011, 0.000] | -0.004 [-0.012, 0.000] | -0.002 [-0.007, 0.000] |
| 2025-26 | 249 | -0.007 [-0.017, 0.001] | -0.010 [-0.025, 0.002] | -0.002 [-0.013, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.031, 0.029] | -0.011 [-0.033, 0.011] | 0.007 [-0.013, 0.029] |
| ordinary | 1603 | 0.002 [-0.002, 0.007] | -0.002 [-0.005, 0.000] | -0.003 [-0.007, 0.000] |
| quarter_end | 31 | 0.014 [-0.099, 0.132] | -0.048 [-0.155, 0.056] | -0.040 [-0.131, 0.051] |
| tax_date | 89 | -0.047 [-0.109, 0.002] | -0.036 [-0.094, 0.018] | -0.029 [-0.087, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.001 [-0.000, 0.001] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [-0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | 0.024 [–] | -0.042 [–] | -0.032 [–] |
| 3 | 478 | -0.003 [-0.022, 0.015] | -0.017 [-0.033, -0.002] | -0.013 [-0.033, 0.006] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.391, -0.077] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.273, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.167 [-0.364, 0.000] |
| quarter_end | 3 | -0.667 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.222, 0.000] |

## risk_gbm+combined_no_structural against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.011 [-0.019, -0.003] |
| 2 | -0.010 [-0.019, -0.003] |
| 3 | -0.008 [-0.015, -0.001] |
| 4 | -0.012 [-0.020, -0.004] |
| 5 | -0.010 [-0.019, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.048 [-0.080, -0.018] | -0.042 [-0.073, -0.014] | -0.056 [-0.088, -0.026] |
| 2020 | 251 | 0.011 [0.001, 0.026] | 0.006 [-0.003, 0.015] | 0.007 [-0.001, 0.016] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.003 [-0.000, 0.007] | -0.001 [-0.008, 0.004] | 0.002 [0.001, 0.004] |
| 2025-26 | 249 | -0.023 [-0.051, -0.000] | -0.003 [-0.020, 0.013] | -0.005 [-0.029, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.056, -0.005] | -0.012 [-0.030, 0.008] | -0.014 [-0.026, -0.003] |
| ordinary | 1603 | -0.007 [-0.015, 0.000] | -0.006 [-0.014, -0.000] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | -0.020 [-0.079, 0.030] | -0.032 [-0.094, 0.025] | 0.006 [-0.027, 0.050] |
| tax_date | 89 | -0.040 [-0.076, -0.009] | -0.014 [-0.056, 0.022] | -0.036 [-0.082, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.001, 0.003] | 0.001 [0.000, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.047 [–] | -0.045 [–] | -0.061 [–] |
| 3 | 478 | -0.042 [-0.070, -0.015] | -0.032 [-0.058, -0.009] | -0.039 [-0.068, -0.012] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.474, -0.154] on 26 onsets.

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
| ordinary | 12 | -0.417 [–] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.286 [-0.455, -0.120] |

## risk_gbm+combined_no_structural against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.017, -0.001] |
| 2 | -0.009 [-0.018, -0.001] |
| 3 | -0.010 [-0.017, -0.002] |
| 4 | -0.011 [-0.020, -0.003] |
| 5 | -0.009 [-0.018, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.044 [-0.077, -0.014] | -0.042 [-0.074, -0.012] | -0.048 [-0.082, -0.015] |
| 2020 | 251 | 0.023 [0.005, 0.048] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.004, 0.003] |
| 2025-26 | 249 | -0.018 [-0.044, 0.002] | -0.011 [-0.037, 0.010] | -0.004 [-0.030, 0.021] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.037, 0.023] | -0.011 [-0.032, 0.011] | 0.005 [-0.016, 0.028] |
| ordinary | 1603 | -0.007 [-0.015, 0.000] | -0.007 [-0.015, -0.001] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | 0.014 [-0.103, 0.126] | -0.048 [-0.156, 0.059] | -0.040 [-0.133, 0.047] |
| tax_date | 89 | -0.047 [-0.110, 0.002] | -0.036 [-0.096, 0.016] | -0.029 [-0.089, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.001, 0.002] | 0.002 [0.000, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | -0.017 [–] | -0.086 [–] | -0.087 [–] |
| 3 | 478 | -0.034 [-0.065, -0.008] | -0.034 [-0.062, -0.009] | -0.033 [-0.062, -0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.467, -0.158] on 26 onsets.

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
| ordinary | 12 | -0.417 [-0.643, -0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.286 [-0.462, -0.125] |

## risk_gbm+combined_no_structural against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.003, 0.001] |
| 2 | -0.002 [-0.005, 0.001] |
| 3 | -0.001 [-0.004, 0.001] |
| 4 | -0.001 [-0.002, 0.000] |
| 5 | -0.002 [-0.004, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.014, 0.005] | -0.006 [-0.020, 0.006] | -0.008 [-0.019, -0.000] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2025-26 | 249 | 0.000 [0.000, 0.001] | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| ordinary | 1603 | -0.001 [-0.003, 0.001] | -0.001 [-0.005, 0.001] | -0.002 [-0.004, -0.000] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2 | 41 | 0.001 [–] | 0.001 [–] | 0.000 [–] |
| 3 | 478 | -0.003 [-0.011, 0.004] | -0.005 [-0.016, 0.004] | -0.006 [-0.015, -0.000] |

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

## risk_gbm+combined_no_projected against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.005 [0.000, 0.011] |
| 3 | 0.004 [-0.000, 0.009] |
| 4 | 0.004 [0.001, 0.007] |
| 5 | 0.008 [0.004, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.018, 0.017] | 0.021 [-0.001, 0.047] | 0.024 [0.010, 0.039] |
| 2020 | 251 | 0.003 [0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.011 [-0.028, 0.002] | 0.002 [-0.002, 0.008] | 0.022 [0.004, 0.046] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.048, -0.003] | -0.007 [-0.023, 0.007] | 0.019 [0.007, 0.032] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | 0.006 [0.002, 0.012] | 0.006 [0.002, 0.009] |
| quarter_end | 31 | -0.011 [-0.068, 0.044] | -0.002 [-0.067, 0.058] | 0.037 [0.001, 0.079] |
| tax_date | 89 | -0.039 [-0.075, -0.009] | -0.015 [-0.059, 0.023] | 0.018 [-0.035, 0.078] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.001 [-0.001, 0.002] |
| 2 | 41 | -0.002 [–] | -0.010 [–] | 0.017 [–] |
| 3 | 478 | -0.007 [-0.021, 0.009] | 0.018 [0.000, 0.038] | 0.028 [0.014, 0.043] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.214, 0.050] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.000 [-0.222, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.333 [–] |
| 3 | 21 | -0.048 [-0.211, 0.095] |

## risk_gbm+combined_no_projected against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.013 [-0.022, -0.006] |
| 2 | -0.006 [-0.015, 0.001] |
| 3 | -0.003 [-0.013, 0.006] |
| 4 | -0.001 [-0.010, 0.006] |
| 5 | 0.002 [-0.007, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.054 [-0.094, -0.020] | -0.017 [-0.065, 0.025] | -0.000 [-0.046, 0.039] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.043, -0.008] | 0.007 [-0.003, 0.019] | 0.013 [0.001, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.007, 0.026] | 0.023 [0.004, 0.045] |
| ordinary | 1603 | -0.011 [-0.021, -0.003] | -0.004 [-0.014, 0.005] | -0.001 [-0.011, 0.008] |
| quarter_end | 31 | -0.026 [-0.090, 0.028] | -0.011 [-0.078, 0.057] | 0.010 [-0.037, 0.058] |
| tax_date | 89 | -0.038 [-0.076, -0.007] | 0.000 [-0.035, 0.027] | 0.017 [-0.012, 0.049] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.001 [-0.002, 0.000] | -0.001 [-0.002, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 313 | 0.003 [0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.003] |
| 2 | 41 | -0.059 [–] | -0.020 [–] | 0.005 [–] |
| 3 | 478 | -0.047 [-0.079, -0.020] | -0.009 [-0.048, 0.025] | 0.006 [-0.032, 0.038] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.412, -0.061] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.391, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.562, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.333, 0.000] |

## risk_gbm+combined_no_projected against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.007, 0.017] |
| 2 | 0.008 [0.001, 0.014] |
| 3 | 0.008 [0.002, 0.014] |
| 4 | 0.008 [0.003, 0.013] |
| 5 | 0.009 [0.004, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.000 [-0.020, 0.020] | -0.015 [-0.042, 0.011] | -0.013 [-0.032, 0.006] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.027, 0.047] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.004 [-0.005, 0.015] | 0.004 [-0.007, 0.018] | 0.007 [-0.003, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.044] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.046] |
| ordinary | 1603 | 0.008 [0.003, 0.012] | 0.004 [-0.002, 0.010] | 0.003 [-0.002, 0.008] |
| quarter_end | 31 | 0.105 [0.017, 0.195] | 0.077 [-0.022, 0.175] | 0.100 [0.002, 0.200] |
| tax_date | 89 | 0.029 [-0.002, 0.058] | 0.038 [0.009, 0.068] | 0.044 [0.011, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.008, 0.011] |
| 1 | 313 | 0.032 [0.025, 0.038] | 0.031 [0.025, 0.038] | 0.029 [0.022, 0.036] |
| 2 | 41 | -0.013 [–] | -0.034 [–] | -0.014 [–] |
| 3 | 478 | 0.008 [-0.010, 0.024] | -0.005 [-0.027, 0.017] | -0.003 [-0.020, 0.014] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.222, 0.143] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.400, 0.042] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.400, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.280, 0.182] |

## risk_gbm+combined_no_projected against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.011, 0.004] |
| 2 | -0.002 [-0.010, 0.004] |
| 3 | 0.002 [-0.005, 0.008] |
| 4 | -0.001 [-0.007, 0.005] |
| 5 | 0.002 [-0.005, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.016 [-0.047, 0.012] | -0.015 [-0.043, 0.010] | -0.010 [-0.036, 0.012] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.027] |
| 2021-23 | 748 | 0.001 [0.001, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.005] | 0.001 [-0.001, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.054, 0.003] | -0.002 [-0.026, 0.019] | -0.000 [-0.025, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.008 [-0.018, 0.033] | 0.011 [-0.001, 0.024] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.005 [-0.013, 0.003] | -0.000 [-0.007, 0.007] | -0.003 [-0.010, 0.004] |
| quarter_end | 31 | 0.045 [-0.011, 0.104] | 0.042 [-0.012, 0.103] | 0.074 [0.016, 0.138] |
| tax_date | 89 | -0.006 [-0.035, 0.018] | 0.011 [-0.009, 0.030] | 0.018 [-0.002, 0.043] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [0.000, 0.002] | 0.003 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 313 | 0.009 [0.007, 0.012] | 0.020 [0.016, 0.024] | 0.014 [0.011, 0.018] |
| 2 | 41 | -0.046 [–] | -0.067 [–] | -0.071 [–] |
| 3 | 478 | -0.016 [-0.043, 0.009] | -0.006 [-0.030, 0.016] | -0.001 [-0.024, 0.019] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.200, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.278, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.444, 0.111] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.250, 0.158] |

## risk_gbm+combined_no_projected against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.003] |
| 2 | -0.004 [-0.009, 0.001] |
| 3 | -0.001 [-0.006, 0.004] |
| 4 | -0.004 [-0.008, -0.001] |
| 5 | -0.003 [-0.005, 0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.017, 0.016] | -0.006 [-0.026, 0.017] | -0.015 [-0.028, -0.003] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.003, 0.015] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.013 [-0.029, 0.000] | -0.003 [-0.011, 0.003] | -0.003 [-0.010, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.048, -0.003] | -0.012 [-0.030, 0.007] | -0.012 [-0.022, -0.000] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | 0.001 [-0.003, 0.006] | -0.000 [-0.002, 0.002] |
| quarter_end | 31 | -0.020 [-0.077, 0.030] | -0.032 [-0.092, 0.026] | 0.006 [-0.027, 0.048] |
| tax_date | 89 | -0.040 [-0.076, -0.009] | -0.014 [-0.054, 0.022] | -0.036 [-0.083, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.009 [–] | -0.004 [–] | -0.009 [–] |
| 3 | 478 | -0.006 [-0.021, 0.010] | -0.006 [-0.024, 0.012] | -0.010 [-0.020, 0.001] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.269, 0.040] on 26 onsets.

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
| ordinary | 12 | 0.000 [-0.200, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.048 [-0.207, 0.095] |

## risk_gbm+combined_no_projected against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.004, 0.006] |
| 2 | -0.003 [-0.009, 0.003] |
| 3 | -0.003 [-0.008, 0.002] |
| 4 | -0.003 [-0.007, 0.001] |
| 5 | -0.002 [-0.006, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.002 [-0.017, 0.023] | -0.006 [-0.028, 0.018] | -0.007 [-0.027, 0.012] |
| 2020 | 251 | 0.016 [0.003, 0.033] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.012, 0.000] | -0.004 [-0.013, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.008 [-0.019, 0.001] | -0.011 [-0.027, 0.002] | -0.003 [-0.013, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.029, 0.029] | -0.011 [-0.033, 0.011] | 0.007 [-0.014, 0.029] |
| ordinary | 1603 | 0.004 [-0.000, 0.008] | 0.000 [-0.004, 0.005] | -0.000 [-0.003, 0.002] |
| quarter_end | 31 | 0.014 [-0.099, 0.131] | -0.048 [-0.162, 0.055] | -0.040 [-0.134, 0.056] |
| tax_date | 89 | -0.047 [-0.106, 0.003] | -0.036 [-0.095, 0.016] | -0.029 [-0.089, 0.028] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.001 [-0.000, 0.001] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [-0.000, 0.001] | -0.002 [-0.006, 0.001] |
| 2 | 41 | 0.021 [–] | -0.045 [–] | -0.034 [–] |
| 3 | 478 | 0.002 [-0.014, 0.019] | -0.008 [-0.027, 0.010] | -0.003 [-0.019, 0.012] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.367, -0.034] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.111] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.154] |
| quarter_end | 3 | -0.667 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.084] |

## risk_gbm+combined_no_projected against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.009 [-0.016, -0.002] |
| 3 | -0.005 [-0.012, 0.000] |
| 4 | -0.010 [-0.018, -0.003] |
| 5 | -0.008 [-0.016, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.041 [-0.072, -0.014] | -0.030 [-0.062, -0.005] | -0.043 [-0.074, -0.017] |
| 2020 | 251 | 0.011 [0.002, 0.026] | 0.006 [-0.002, 0.015] | 0.007 [-0.001, 0.016] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.007] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.024 [-0.052, -0.001] | -0.004 [-0.021, 0.012] | -0.005 [-0.031, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.056, -0.006] | -0.012 [-0.030, 0.007] | -0.014 [-0.025, -0.003] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.004 [-0.011, 0.002] | -0.006 [-0.014, 0.000] |
| quarter_end | 31 | -0.020 [-0.075, 0.033] | -0.032 [-0.094, 0.022] | 0.006 [-0.026, 0.045] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.053, 0.025] | -0.036 [-0.083, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.002 [0.001, 0.003] | 0.001 [0.001, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.003 [0.000, 0.009] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.049 [–] | -0.048 [–] | -0.064 [–] |
| 3 | 478 | -0.037 [-0.065, -0.012] | -0.023 [-0.049, -0.002] | -0.030 [-0.056, -0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.118] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.417, -0.067] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.571, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.238 [-0.400, -0.091] |

## risk_gbm+combined_no_projected against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.007 [-0.015, 0.000] |
| 2 | -0.007 [-0.015, -0.000] |
| 3 | -0.007 [-0.015, -0.001] |
| 4 | -0.008 [-0.017, -0.001] |
| 5 | -0.007 [-0.015, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.038 [-0.071, -0.008] | -0.030 [-0.061, -0.003] | -0.035 [-0.067, -0.006] |
| 2020 | 251 | 0.023 [0.004, 0.048] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.005, 0.003] |
| 2025-26 | 249 | -0.019 [-0.046, 0.002] | -0.012 [-0.039, 0.010] | -0.005 [-0.031, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.007 [-0.038, 0.024] | -0.011 [-0.033, 0.010] | 0.005 [-0.017, 0.029] |
| ordinary | 1603 | -0.005 [-0.013, 0.001] | -0.005 [-0.012, 0.001] | -0.006 [-0.014, -0.000] |
| quarter_end | 31 | 0.014 [-0.097, 0.130] | -0.048 [-0.154, 0.056] | -0.040 [-0.134, 0.054] |
| tax_date | 89 | -0.047 [-0.111, 0.003] | -0.036 [-0.097, 0.016] | -0.029 [-0.092, 0.028] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.001 [-0.001, 0.002] | 0.002 [0.000, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 313 | 0.002 [0.000, 0.005] | 0.000 [0.000, 0.001] | -0.002 [-0.006, 0.000] |
| 2 | 41 | -0.019 [–] | -0.089 [–] | -0.089 [–] |
| 3 | 478 | -0.029 [-0.059, -0.003] | -0.025 [-0.051, -0.003] | -0.023 [-0.051, 0.002] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.120] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.421, -0.062] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.571, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 0 | – [–] |
| 2 | 3 | -0.667 [–] |
| 3 | 21 | -0.238 [-0.400, -0.080] |

## risk_gbm+combined_no_projected against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.000, 0.001] |
| 2 | -0.000 [-0.002, 0.001] |
| 3 | 0.001 [-0.001, 0.003] |
| 4 | 0.002 [0.000, 0.003] |
| 5 | 0.001 [-0.000, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.002 [-0.000, 0.006] | 0.006 [-0.004, 0.015] | 0.005 [-0.002, 0.011] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2025-26 | 249 | -0.001 [-0.001, -0.000] | -0.001 [-0.002, -0.000] | -0.001 [-0.002, -0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| ordinary | 1603 | 0.001 [-0.000, 0.001] | 0.001 [-0.001, 0.003] | 0.001 [-0.001, 0.003] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1041 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 313 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2 | 41 | -0.002 [–] | -0.002 [-0.006, 0.000] | -0.002 [–] |
| 3 | 478 | 0.002 [-0.000, 0.005] | 0.004 [-0.003, 0.012] | 0.003 [-0.002, 0.009] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [0.000, 0.115] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.176] |
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
| 1 | 0 | – [–] |
| 2 | 3 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.143] |


## Predicted against realised rate of a pressure day (+5 bp), by regime and day type, pooled over h = 1 to 5

### risk_gbm+combined

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0150 | 0.0741 |
| day type month_end | 750 | 0.0386 | 0.1133 |
| day type ordinary | 8009 | 0.0096 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0573 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0010 | 0.0000 |
| regime 2024 | 1250 | 0.0001 | 0.0200 |
| regime 2025-26 | 1245 | 0.0171 | 0.1165 |

### risk_gbm+combined_nogate

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0953 | 0.0741 |
| day type month_end | 750 | 0.1021 | 0.1133 |
| day type ordinary | 8009 | 0.0915 | 0.0627 |
| day type quarter_end | 151 | 0.1996 | 0.2715 |
| day type tax_date | 445 | 0.1168 | 0.1461 |
| regime 2018-19 | 1865 | 0.2776 | 0.2697 |
| regime 2020 | 1255 | 0.1538 | 0.0159 |
| regime 2021-23 | 3740 | 0.0321 | 0.0000 |
| regime 2024 | 1250 | 0.0064 | 0.0200 |
| regime 2025-26 | 1245 | 0.0423 | 0.1165 |

### risk_logistic+combined

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0158 | 0.0741 |
| day type month_end | 750 | 0.0391 | 0.1133 |
| day type ordinary | 8009 | 0.0078 | 0.0627 |
| day type quarter_end | 151 | 0.2212 | 0.2715 |
| day type tax_date | 445 | 0.0510 | 0.1461 |
| regime 2018-19 | 1865 | 0.0570 | 0.2697 |
| regime 2020 | 1255 | 0.0085 | 0.0159 |
| regime 2021-23 | 3740 | 0.0010 | 0.0000 |
| regime 2024 | 1250 | 0.0022 | 0.0200 |
| regime 2025-26 | 1245 | 0.0197 | 0.1165 |

### risk_logistic+combined_nogate

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0981 | 0.0741 |
| day type month_end | 750 | 0.1023 | 0.1133 |
| day type ordinary | 8009 | 0.0914 | 0.0627 |
| day type quarter_end | 151 | 0.3278 | 0.2715 |
| day type tax_date | 445 | 0.1338 | 0.1461 |
| regime 2018-19 | 1865 | 0.2879 | 0.2697 |
| regime 2020 | 1255 | 0.1531 | 0.0159 |
| regime 2021-23 | 3740 | 0.0322 | 0.0000 |
| regime 2024 | 1250 | 0.0106 | 0.0200 |
| regime 2025-26 | 1245 | 0.0440 | 0.1165 |

### risk_gbm+combined_no_factor

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0149 | 0.0741 |
| day type month_end | 750 | 0.0387 | 0.1133 |
| day type ordinary | 8009 | 0.0094 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0559 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0012 | 0.0000 |
| regime 2024 | 1250 | 0.0001 | 0.0200 |
| regime 2025-26 | 1245 | 0.0171 | 0.1165 |

### risk_gbm+combined_no_structural

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0154 | 0.0741 |
| day type month_end | 750 | 0.0382 | 0.1133 |
| day type ordinary | 8009 | 0.0101 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0598 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0003 | 0.0000 |
| regime 2024 | 1250 | 0.0003 | 0.0200 |
| regime 2025-26 | 1245 | 0.0178 | 0.1165 |

### risk_gbm+combined_no_projected

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0153 | 0.0741 |
| day type month_end | 750 | 0.0386 | 0.1133 |
| day type ordinary | 8009 | 0.0100 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0617 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0002 | 0.0000 |
| regime 2024 | 1250 | 0.0001 | 0.0200 |
| regime 2025-26 | 1245 | 0.0151 | 0.1165 |

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

### risk_logistic+settle+h41

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0292 | 0.0741 |
| day type month_end | 750 | 0.0917 | 0.1133 |
| day type ordinary | 8009 | 0.0119 | 0.0627 |
| day type quarter_end | 151 | 0.3278 | 0.2715 |
| day type tax_date | 445 | 0.1338 | 0.1461 |
| regime 2018-19 | 1865 | 0.1066 | 0.2697 |
| regime 2020 | 1255 | 0.0198 | 0.0159 |
| regime 2021-23 | 3740 | 0.0007 | 0.0000 |
| regime 2024 | 1250 | 0.0054 | 0.0200 |
| regime 2025-26 | 1245 | 0.0318 | 0.1165 |

### risk_gbm+every_day+gate+settle+h41

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0521 | 0.0741 |
| day type month_end | 750 | 0.0928 | 0.1133 |
| day type ordinary | 8009 | 0.0419 | 0.0627 |
| day type quarter_end | 151 | 0.1996 | 0.2715 |
| day type tax_date | 445 | 0.1168 | 0.1461 |
| regime 2018-19 | 1865 | 0.1652 | 0.2697 |
| regime 2020 | 1255 | 0.0253 | 0.0159 |
| regime 2021-23 | 3740 | 0.0056 | 0.0000 |
| regime 2024 | 1250 | 0.0145 | 0.0200 |
| regime 2025-26 | 1245 | 0.0871 | 0.1165 |

### risk_logistic+every_day+gate+settle+h41

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0549 | 0.0741 |
| day type month_end | 750 | 0.0930 | 0.1133 |
| day type ordinary | 8009 | 0.0418 | 0.0627 |
| day type quarter_end | 151 | 0.3278 | 0.2715 |
| day type tax_date | 445 | 0.1338 | 0.1461 |
| regime 2018-19 | 1865 | 0.1755 | 0.2697 |
| regime 2020 | 1255 | 0.0246 | 0.0159 |
| regime 2021-23 | 3740 | 0.0057 | 0.0000 |
| regime 2024 | 1250 | 0.0187 | 0.0200 |
| regime 2025-26 | 1245 | 0.0889 | 0.1165 |

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

