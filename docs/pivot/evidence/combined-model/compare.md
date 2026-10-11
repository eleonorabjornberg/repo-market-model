# The combined model (#561)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| risk_gbm+combined | 10 / 1.08 fail | fail | 10 / 1.88 fail | 2 / 0.89 fail |
| risk_gbm+combined_nogate | 11 / 1.38 fail | fail | 11 / 2.12 fail | 3 / 0.44 fail |
| risk_logistic+combined | 11 / 1.46 fail | fail | 11 / 2.73 fail | 4 / 2.22 fail |
| risk_logistic+combined_nogate | 7 / 1.00 fail | fail | 7 / 1.35 fail | 2 / 0.44 fail |
| risk_gbm+combined_no_factor | 10 / 1.08 fail | fail | 10 / 1.85 fail | 2 / 0.89 fail |
| risk_gbm+combined_no_structural | 9 / 0.85 fail | fail | 9 / 1.65 fail | 2 / 0.89 fail |
| risk_gbm+combined_no_projected | 10 / 1.08 fail | fail | 10 / 2.04 fail | 2 / 0.89 fail |
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
| risk_gbm+combined | 10 / 1.07 fail | fail | 10 / 1.77 fail | 2 / 1.81 fail |
| risk_gbm+combined_nogate | 13 / 1.74 pass | pass (h = 1) | 13 / 2.21 fail | 3 / 0.61 fail |
| risk_logistic+combined | 11 / 1.96 fail | fail | 11 / 3.43 fail | 4 / 4.42 fail |
| risk_logistic+combined_nogate | 10 / 1.15 fail | fail | 10 / 1.85 fail | 2 / 1.06 fail |
| risk_gbm+combined_no_factor | 10 / 1.09 fail | fail | 10 / 1.80 fail | 2 / 1.81 fail |
| risk_gbm+combined_no_structural | 11 / 1.06 fail | fail | 11 / 1.87 fail | 2 / 1.89 fail |
| risk_gbm+combined_no_projected | 10 / 1.07 fail | fail | 10 / 1.92 fail | 2 / 1.81 fail |
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
| risk_gbm+combined | 10 / 1.06 fail | fail | 10 / 1.91 fail | 2 / 1.64 fail |
| risk_gbm+combined_nogate | 11 / 1.48 fail | fail | 11 / 1.85 fail | 3 / 0.69 fail |
| risk_logistic+combined | 11 / 1.87 fail | fail | 11 / 3.72 fail | 4 / 3.81 fail |
| risk_logistic+combined_nogate | 8 / 1.03 fail | fail | 8 / 1.44 fail | 2 / 1.14 fail |
| risk_gbm+combined_no_factor | 10 / 1.06 fail | fail | 10 / 1.96 fail | 2 / 1.64 fail |
| risk_gbm+combined_no_structural | 11 / 0.71 fail | fail | 11 / 1.22 fail | 2 / 0.75 fail |
| risk_gbm+combined_no_projected | 10 / 0.96 fail | fail | 10 / 2.03 fail | 2 / 1.19 fail |
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

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | 1.2 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+combined | 10 of 26 | 0.385 [0.212, 0.571] | 0.115 | 1.08 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_factor | 10 of 26 | 0.385 [0.212, 0.571] | 0.115 | 1.08 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_projected | 10 of 26 | 0.385 [0.200, 0.571] | 0.115 | 1.08 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_structural | 9 of 26 | 0.346 [0.190, 0.522] | 0.115 | 0.85 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_nogate | 11 of 26 | 0.423 [0.250, 0.600] | 0.154 | 1.38 | 0.2 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| risk_gbm+every_day+gate+settle+h41 | 15 of 26 | 0.577 [0.417, 0.741] | 0.192 | 2.35 | 1.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.115 | 1.35 | 0.5 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 1.85 | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic+combined | 11 of 26 | 0.423 [0.258, 0.606] | 0.154 | 1.46 | 0.7 / 0.7 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+combined_nogate | 7 of 26 | 0.269 [0.136, 0.409] | 0.115 | 1.00 | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+every_day+gate+settle+h41 | 14 of 26 | 0.538 [0.351, 0.708] | 0.231 | 2.69 | 1.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_logistic+settle+h41 | 15 of 26 | 0.577 [0.391, 0.760] | 0.192 | 1.81 | 2.9 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 1.77 | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.192 | 1.88 | 0.7 / 0.0 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+combined | 0.38 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.27 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_no_factor | 0.38 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.53 (17) | 0.28 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_no_projected | 0.40 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.53 (17) | 0.31 (101) | 0.44 (9) | 0.46 (13) |
| risk_gbm+combined_no_structural | 0.36 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.27 (101) | 0.33 (9) | 0.46 (13) |
| risk_gbm+combined_nogate | 0.44 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.35 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.33 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.25 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+combined | 0.37 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.27 (101) | 0.67 (9) | 0.62 (13) |
| risk_logistic+combined_nogate | 0.42 (102) | 0.25 (4) | – | 0.20 (5) | 0.21 (29) | 0.47 (17) | 0.31 (101) | 0.56 (9) | 0.54 (13) |
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
| risk_gbm+combined | -0.0031 [-0.0251, +0.0196] | +0.0422 [+0.0346, +0.0500] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0054] | +0.0051 [-0.0041, +0.0154] | +0.0298 [+0.0162, +0.0442] | +0.0068 [+0.0013, +0.0118] | +0.1049 [+0.0102, +0.1953] | +0.0292 [-0.0010, +0.0578] |
| risk_gbm+combined_no_factor | -0.0029 [-0.0257, +0.0183] | +0.0422 [+0.0348, +0.0500] | +0.0138 [+0.0121, +0.0158] | +0.0010 [-0.0047, +0.0052] | +0.0052 [-0.0042, +0.0154] | +0.0298 [+0.0165, +0.0444] | +0.0069 [+0.0017, +0.0116] | +0.1049 [+0.0121, +0.1925] | +0.0292 [-0.0021, +0.0572] |
| risk_gbm+combined_no_projected | +0.0000 [-0.0220, +0.0216] | +0.0422 [+0.0345, +0.0498] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0053] | +0.0046 [-0.0049, +0.0148] | +0.0297 [+0.0173, +0.0432] | +0.0075 [+0.0024, +0.0122] | +0.1049 [+0.0156, +0.1989] | +0.0292 [-0.0021, +0.0579] |
| risk_gbm+combined_no_structural | -0.0041 [-0.0273, +0.0191] | +0.0422 [+0.0349, +0.0497] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0049, +0.0054] | +0.0053 [-0.0036, +0.0155] | +0.0299 [+0.0166, +0.0442] | +0.0066 [+0.0015, +0.0114] | +0.1049 [+0.0149, +0.1995] | +0.0292 [-0.0007, +0.0589] |
| risk_gbm+combined_nogate | +0.0484 [+0.0078, +0.0930] | +0.0221 [+0.0110, +0.0321] | +0.0125 [+0.0108, +0.0142] | +0.0015 [-0.0035, +0.0053] | +0.0231 [+0.0032, +0.0496] | +0.0570 [+0.0336, +0.0824] | +0.0129 [+0.0042, +0.0230] | +0.1247 [+0.0394, +0.2037] | +0.0689 [+0.0407, +0.0977] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic+combined | -0.0066 [-0.0277, +0.0153] | +0.0333 [+0.0240, +0.0412] | +0.0138 [+0.0120, +0.0156] | +0.0048 [+0.0011, +0.0084] | +0.0098 [+0.0014, +0.0207] | +0.0265 [+0.0131, +0.0414] | +0.0059 [+0.0008, +0.0107] | +0.0668 [-0.0140, +0.1429] | +0.0484 [+0.0290, +0.0675] |
| risk_logistic+combined_nogate | +0.0446 [+0.0032, +0.0904] | +0.0105 [-0.0050, +0.0233] | +0.0125 [+0.0109, +0.0142] | +0.0051 [+0.0012, +0.0093] | +0.0182 [+0.0038, +0.0377] | +0.0336 [+0.0072, +0.0615] | +0.0124 [+0.0035, +0.0222] | +0.0906 [+0.0168, +0.1610] | +0.0764 [+0.0457, +0.1128] |
| risk_logistic+every_day+gate+settle+h41 | +0.0382 [+0.0132, +0.0653] | +0.0193 [-0.0049, +0.0375] | +0.0136 [+0.0119, +0.0156] | +0.0021 [-0.0046, +0.0081] | +0.0236 [+0.0017, +0.0507] | +0.0362 [+0.0093, +0.0647] | +0.0129 [+0.0066, +0.0200] | +0.0906 [+0.0222, +0.1607] | +0.0764 [+0.0442, +0.1149] |
| risk_logistic+settle+h41 | -0.0019 [-0.0231, +0.0187] | +0.0266 [+0.0117, +0.0388] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0011, +0.0094] | +0.0125 [+0.0008, +0.0272] | +0.0305 [+0.0038, +0.0576] | +0.0040 [-0.0012, +0.0087] | +0.0906 [+0.0189, +0.1627] | +0.0764 [+0.0461, +0.1173] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.358 | 6.69 | 2.9 / 4.7 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.380 | 7.04 | 1.2 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.154 | 1.38 | 1.5 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+combined | 10 of 26 | 0.385 [0.212, 0.571] | 0.154 | 1.58 | 0.7 / 0.7 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_factor | 10 of 26 | 0.385 [0.212, 0.571] | 0.154 | 1.65 | 0.7 / 0.7 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_projected | 10 of 26 | 0.385 [0.200, 0.571] | 0.154 | 1.62 | 0.7 / 0.7 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_no_structural | 11 of 26 | 0.423 [0.242, 0.609] | 0.192 | 1.92 | 0.2 / 0.3 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+combined_nogate | 13 of 26 | 0.500 [0.308, 0.684] | 0.231 | 3.69 | 0.5 / 0.0 | 2 of 4 | yes, yes | fail (tiers yes / no / yes) | fail (yes / no / yes) |
| risk_gbm+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.524, 0.857] | 0.231 | 3.54 | 2.7 / 0.3 | 3 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 0.154 | 1.38 | 0.7 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.192 | 2.42 | 3.2 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic+combined | 11 of 26 | 0.423 [0.258, 0.606] | 0.231 | 2.73 | 3.7 / 4.7 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_logistic+combined_nogate | 10 of 26 | 0.385 [0.226, 0.556] | 0.231 | 2.77 | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / yes) |
| risk_logistic+every_day+gate+settle+h41 | 18 of 26 | 0.692 [0.519, 0.857] | 0.250 | 4.42 | 3.7 / 0.3 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (yes / no / no) |
| risk_logistic+settle+h41 | 16 of 26 | 0.615 [0.429, 0.800] | 0.231 | 2.73 | 5.1 / 2.7 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.192 | 2.31 | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.192 | 2.31 | 1.0 / 0.7 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+combined | 0.38 (102) | 0.25 (4) | – | 0.00 (5) | 0.24 (29) | 0.53 (17) | 0.27 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_no_factor | 0.38 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.53 (17) | 0.28 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_no_projected | 0.41 (102) | 0.25 (4) | – | 0.00 (5) | 0.55 (29) | 0.59 (17) | 0.38 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_no_structural | 0.43 (102) | 0.25 (4) | – | 0.00 (5) | 0.66 (29) | 0.59 (17) | 0.43 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+combined_nogate | 0.65 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.65 (17) | 0.54 (101) | 0.56 (9) | 0.38 (13) |
| risk_gbm+every_day+gate+settle+h41 | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.72 (29) | 0.82 (17) | 0.52 (101) | 0.56 (9) | 0.62 (13) |
| risk_gbm+settle+h41 | 0.30 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.56 (9) | 0.69 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+combined | 0.38 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.65 (17) | 0.27 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic+combined_nogate | 0.67 (102) | 0.25 (4) | – | 0.20 (5) | 0.24 (29) | 0.59 (17) | 0.52 (101) | 0.67 (9) | 0.62 (13) |
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
| risk_gbm+combined | -0.0031 [-0.0251, +0.0196] | +0.0422 [+0.0346, +0.0500] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0054] | +0.0051 [-0.0041, +0.0154] | +0.0298 [+0.0162, +0.0442] | +0.0068 [+0.0013, +0.0118] | +0.1049 [+0.0102, +0.1953] | +0.0292 [-0.0010, +0.0578] |
| risk_gbm+combined_no_factor | -0.0029 [-0.0257, +0.0183] | +0.0422 [+0.0348, +0.0500] | +0.0138 [+0.0121, +0.0158] | +0.0010 [-0.0047, +0.0052] | +0.0052 [-0.0042, +0.0154] | +0.0298 [+0.0165, +0.0444] | +0.0069 [+0.0017, +0.0116] | +0.1049 [+0.0121, +0.1925] | +0.0292 [-0.0021, +0.0572] |
| risk_gbm+combined_no_projected | +0.0000 [-0.0220, +0.0216] | +0.0422 [+0.0345, +0.0498] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0047, +0.0053] | +0.0046 [-0.0049, +0.0148] | +0.0297 [+0.0173, +0.0432] | +0.0075 [+0.0024, +0.0122] | +0.1049 [+0.0156, +0.1989] | +0.0292 [-0.0021, +0.0579] |
| risk_gbm+combined_no_structural | -0.0041 [-0.0273, +0.0191] | +0.0422 [+0.0349, +0.0497] | +0.0138 [+0.0121, +0.0157] | +0.0010 [-0.0049, +0.0054] | +0.0053 [-0.0036, +0.0155] | +0.0299 [+0.0166, +0.0442] | +0.0066 [+0.0015, +0.0114] | +0.1049 [+0.0149, +0.1995] | +0.0292 [-0.0007, +0.0589] |
| risk_gbm+combined_nogate | +0.0484 [+0.0078, +0.0930] | +0.0221 [+0.0110, +0.0321] | +0.0125 [+0.0108, +0.0142] | +0.0015 [-0.0035, +0.0053] | +0.0231 [+0.0032, +0.0496] | +0.0570 [+0.0336, +0.0824] | +0.0129 [+0.0042, +0.0230] | +0.1247 [+0.0394, +0.2037] | +0.0689 [+0.0407, +0.0977] |
| risk_gbm+every_day+gate+settle+h41 | +0.0420 [+0.0131, +0.0705] | +0.0309 [+0.0152, +0.0451] | +0.0136 [+0.0117, +0.0155] | -0.0015 [-0.0087, +0.0043] | +0.0286 [+0.0022, +0.0591] | +0.0595 [+0.0350, +0.0859] | +0.0134 [+0.0067, +0.0200] | +0.1247 [+0.0406, +0.2112] | +0.0689 [+0.0406, +0.0981] |
| risk_gbm+settle+h41 | +0.0019 [-0.0211, +0.0239] | +0.0382 [+0.0294, +0.0470] | +0.0138 [+0.0120, +0.0156] | +0.0014 [-0.0034, +0.0054] | +0.0174 [+0.0002, +0.0403] | +0.0538 [+0.0302, +0.0783] | +0.0045 [-0.0005, +0.0095] | +0.1247 [+0.0440, +0.2077] | +0.0689 [+0.0408, +0.0969] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic+combined | -0.0066 [-0.0277, +0.0153] | +0.0333 [+0.0240, +0.0412] | +0.0138 [+0.0120, +0.0156] | +0.0048 [+0.0011, +0.0084] | +0.0098 [+0.0014, +0.0207] | +0.0265 [+0.0131, +0.0414] | +0.0059 [+0.0008, +0.0107] | +0.0668 [-0.0140, +0.1429] | +0.0484 [+0.0290, +0.0675] |
| risk_logistic+combined_nogate | +0.0446 [+0.0032, +0.0904] | +0.0105 [-0.0050, +0.0233] | +0.0125 [+0.0109, +0.0142] | +0.0051 [+0.0012, +0.0093] | +0.0182 [+0.0038, +0.0377] | +0.0336 [+0.0072, +0.0615] | +0.0124 [+0.0035, +0.0222] | +0.0906 [+0.0168, +0.1610] | +0.0764 [+0.0457, +0.1128] |
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
| risk_logistic+combined_nogate | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_no_factor | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_no_structural | 0 of 4 | 9 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+combined_no_projected | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
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
| risk_gbm+combined | 0.0601 / 0.5374 | 0.0647 / 0.5987 | 0.0661 / 0.6056 | 0.0665 / 0.6060 | 0.0644 / 0.6057 |
| risk_gbm+combined_nogate | 0.0505 / 0.1948 | 0.0559 / 0.2196 | 0.0577 / 0.2214 | 0.0584 / 0.2326 | 0.0628 / 0.2467 |
| risk_logistic+combined | 0.0608 / 0.5472 | 0.0639 / 0.5908 | 0.0661 / 0.6080 | 0.0666 / 0.5990 | 0.0669 / 0.6152 |
| risk_logistic+combined_nogate | 0.0530 / 0.2119 | 0.0571 / 0.2279 | 0.0559 / 0.2142 | 0.0596 / 0.2364 | 0.0637 / 0.2484 |
| risk_gbm+combined_no_factor | 0.0600 / 0.5369 | 0.0647 / 0.5984 | 0.0659 / 0.6109 | 0.0664 / 0.6044 | 0.0643 / 0.6043 |
| risk_gbm+combined_no_structural | 0.0602 / 0.5038 | 0.0644 / 0.5843 | 0.0650 / 0.6135 | 0.0648 / 0.6177 | 0.0641 / 0.6164 |
| risk_gbm+combined_no_projected | 0.0595 / 0.5386 | 0.0648 / 0.6632 | 0.0668 / 0.6389 | 0.0666 / 0.6369 | 0.0645 / 0.6165 |
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
| 1 | 90 | 1 | 1 | 7 | 0 | 1345 of 1873 | 511 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1360 of 1872 | 493 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1392 of 1871 | 460 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1395 of 1870 | 451 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1383 of 1869 | 464 |

## risk_gbm+combined_nogate: onsets only this row warns

risk_gbm+combined_nogate warns 13 of 26 onsets; at least one of the five passers warns 16. 2 are warned by risk_gbm+combined_nogate and by none of the five passers:

* 2019-06-25 (flagged at h = 1, 3)
* 2019-08-13 (flagged at h = 1, 3)

Warned by a passer and not by risk_gbm+combined_nogate: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-10-15

### risk_gbm+combined_nogate: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 2 | 0 of 1873 | 1848 |
| 2 | 90 | 0 | 0 | 7 | 2 | 0 of 1872 | 1847 |
| 3 | 90 | 0 | 0 | 7 | 5 | 0 of 1871 | 1845 |
| 4 | 90 | 1 | 0 | 7 | 2 | 0 of 1870 | 1845 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1844 |

## risk_logistic+combined: onsets only this row warns

risk_logistic+combined warns 11 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_logistic+combined and by none of the five passers:


Warned by a passer and not by risk_logistic+combined: 2019-01-15, 2019-01-31, 2019-03-15, 2025-09-15, 2025-10-15

### risk_logistic+combined: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1345 of 1873 | 529 |
| 2 | 90 | 1 | 1 | 7 | 1 | 1360 of 1872 | 513 |
| 3 | 90 | 1 | 1 | 7 | 2 | 1392 of 1871 | 480 |
| 4 | 90 | 2 | 1 | 7 | 2 | 1395 of 1870 | 476 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1383 of 1869 | 487 |

## risk_logistic+combined_nogate: onsets only this row warns

risk_logistic+combined_nogate warns 10 of 26 onsets; at least one of the five passers warns 16. 2 are warned by risk_logistic+combined_nogate and by none of the five passers:

* 2019-06-25 (flagged at h = 1)
* 2019-08-13 (flagged at h = 1)

Warned by a passer and not by risk_logistic+combined_nogate: 2019-01-15, 2019-01-31, 2019-03-15, 2019-08-30, 2024-09-30, 2025-09-15, 2025-10-15, 2025-12-26

### risk_logistic+combined_nogate: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 3 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 0 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 0 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 1 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1869 |

## risk_gbm+combined_no_factor: onsets only this row warns

risk_gbm+combined_no_factor warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined_no_factor and by none of the five passers:


Warned by a passer and not by risk_gbm+combined_no_factor: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_no_factor: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1335 of 1873 | 521 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1357 of 1872 | 496 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1385 of 1871 | 467 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1383 of 1870 | 463 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1369 of 1869 | 478 |

## risk_gbm+combined_no_structural: onsets only this row warns

risk_gbm+combined_no_structural warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by risk_gbm+combined_no_structural and by none of the five passers:

* 2019-05-28 (flagged at h = 2)

Warned by a passer and not by risk_gbm+combined_no_structural: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_no_structural: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1230 of 1873 | 626 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1260 of 1872 | 593 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1283 of 1871 | 569 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1284 of 1870 | 562 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1295 of 1869 | 552 |

## risk_gbm+combined_no_projected: onsets only this row warns

risk_gbm+combined_no_projected warns 10 of 26 onsets; at least one of the five passers warns 16. 0 are warned by risk_gbm+combined_no_projected and by none of the five passers:


Warned by a passer and not by risk_gbm+combined_no_projected: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+combined_no_projected: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 1 | 7 | 0 | 1421 of 1873 | 434 |
| 2 | 90 | 1 | 1 | 7 | 0 | 1447 of 1872 | 406 |
| 3 | 90 | 1 | 1 | 7 | 1 | 1438 of 1871 | 414 |
| 4 | 90 | 2 | 1 | 7 | 1 | 1427 of 1870 | 419 |
| 5 | 89 | 1 | 1 | 7 | 0 | 1427 of 1869 | 420 |

## risk_gbm+combined against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.004 [-0.002, 0.011] |
| 3 | 0.001 [-0.004, 0.005] |
| 4 | 0.000 [-0.004, 0.004] |
| 5 | 0.005 [-0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.005 [-0.022, 0.012] | 0.002 [-0.021, 0.022] | 0.011 [-0.016, 0.036] |
| 2020 | 251 | 0.003 [-0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.010 [-0.027, 0.002] | 0.003 [-0.002, 0.009] | 0.022 [0.004, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.049, -0.003] | -0.007 [-0.022, 0.007] | 0.019 [0.007, 0.031] |
| ordinary | 1603 | 0.002 [-0.002, 0.006] | 0.002 [-0.003, 0.006] | 0.003 [-0.003, 0.008] |
| quarter_end | 31 | -0.011 [-0.067, 0.049] | -0.002 [-0.061, 0.062] | 0.037 [-0.000, 0.081] |
| tax_date | 89 | -0.039 [-0.073, -0.010] | -0.015 [-0.058, 0.021] | 0.018 [-0.035, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.022 [-0.052, -0.002] | 0.003 [–] | 0.046 [–] |
| 3 | 473 | -0.008 [-0.023, 0.007] | 0.002 [-0.017, 0.018] | 0.016 [-0.006, 0.037] |

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
| 1 | -0.014 [-0.024, -0.006] |
| 2 | -0.008 [-0.017, -0.000] |
| 3 | -0.007 [-0.016, 0.002] |
| 4 | -0.005 [-0.014, 0.003] |
| 5 | -0.001 [-0.009, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.057 [-0.098, -0.022] | -0.036 [-0.081, 0.007] | -0.014 [-0.053, 0.022] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.010, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.041, -0.008] | 0.007 [-0.002, 0.020] | 0.013 [0.001, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.000] | 0.008 [-0.008, 0.025] | 0.023 [0.004, 0.046] |
| ordinary | 1603 | -0.012 [-0.023, -0.004] | -0.008 [-0.018, 0.001] | -0.004 [-0.013, 0.003] |
| quarter_end | 31 | -0.026 [-0.089, 0.029] | -0.011 [-0.074, 0.055] | 0.010 [-0.035, 0.059] |
| tax_date | 89 | -0.038 [-0.076, -0.007] | 0.000 [-0.033, 0.028] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.070 [–] | -0.010 [-0.042, 0.009] | 0.032 [–] |
| 3 | 473 | -0.048 [-0.082, -0.019] | -0.024 [-0.061, 0.010] | -0.006 [-0.040, 0.023] |

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
| 1 | 0.011 [0.006, 0.017] |
| 2 | 0.006 [-0.001, 0.013] |
| 3 | 0.005 [-0.002, 0.011] |
| 4 | 0.004 [-0.002, 0.011] |
| 5 | 0.006 [-0.000, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.003 [-0.026, 0.020] | -0.034 [-0.061, -0.010] | -0.026 [-0.053, -0.003] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.028, 0.048] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.015] | 0.005 [-0.006, 0.018] | 0.008 [-0.002, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.045] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.046] |
| ordinary | 1603 | 0.007 [0.001, 0.012] | -0.000 [-0.007, 0.006] | 0.000 [-0.007, 0.006] |
| quarter_end | 31 | 0.105 [0.012, 0.193] | 0.077 [-0.016, 0.181] | 0.100 [0.003, 0.197] |
| tax_date | 89 | 0.029 [-0.003, 0.058] | 0.038 [0.007, 0.067] | 0.044 [0.014, 0.073] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.023, 0.036] | 0.028 [0.022, 0.034] |
| 2 | 41 | -0.029 [–] | -0.029 [–] | 0.005 [–] |
| 3 | 473 | 0.008 [-0.012, 0.027] | -0.019 [-0.044, 0.003] | -0.014 [-0.037, 0.008] |

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
| 2 | -0.004 [-0.012, 0.004] |
| 3 | -0.002 [-0.009, 0.005] |
| 4 | -0.004 [-0.012, 0.002] |
| 5 | -0.001 [-0.008, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.020 [-0.052, 0.011] | -0.034 [-0.064, -0.006] | -0.024 [-0.054, 0.003] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.026] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.005] | 0.001 [-0.002, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.052, 0.003] | -0.001 [-0.025, 0.020] | 0.000 [-0.023, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.016, 0.031] | 0.011 [-0.001, 0.023] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.006 [-0.014, 0.002] | -0.004 [-0.013, 0.003] | -0.006 [-0.014, 0.002] |
| quarter_end | 31 | 0.045 [-0.007, 0.106] | 0.042 [-0.011, 0.102] | 0.074 [0.019, 0.144] |
| tax_date | 89 | -0.006 [-0.037, 0.017] | 0.011 [-0.008, 0.030] | 0.018 [-0.003, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.119 [–] | -0.074 [–] | -0.071 [-0.145, 0.023] |
| 3 | 473 | -0.013 [-0.039, 0.012] | -0.019 [-0.046, 0.005] | -0.011 [-0.038, 0.012] |

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
| 1 | -0.002 [-0.007, 0.002] |
| 2 | -0.005 [-0.011, 0.001] |
| 3 | -0.005 [-0.010, -0.001] |
| 4 | -0.008 [-0.013, -0.003] |
| 5 | -0.005 [-0.010, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.005 [-0.023, 0.013] | -0.025 [-0.045, -0.007] | -0.029 [-0.050, -0.009] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.004, 0.015] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.012 [-0.029, 0.001] | -0.002 [-0.010, 0.004] | -0.003 [-0.009, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.002] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.002 [-0.002, 0.007] | -0.003 [-0.008, 0.000] | -0.003 [-0.008, 0.001] |
| quarter_end | 31 | -0.020 [-0.077, 0.033] | -0.032 [-0.093, 0.028] | 0.006 [-0.026, 0.047] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.055, 0.023] | -0.036 [-0.083, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.035 [–] | 0.013 [–] | -0.005 [–] |
| 3 | 473 | -0.007 [-0.023, 0.009] | -0.021 [-0.038, -0.006] | -0.020 [-0.039, -0.004] |

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

## risk_gbm+combined against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.005, 0.005] |
| 2 | -0.004 [-0.011, 0.002] |
| 3 | -0.007 [-0.012, -0.002] |
| 4 | -0.006 [-0.012, -0.001] |
| 5 | -0.004 [-0.010, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.021, 0.019] | -0.025 [-0.047, -0.004] | -0.021 [-0.049, 0.003] |
| 2020 | 251 | 0.016 [0.003, 0.032] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.012, 0.000] | -0.004 [-0.013, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.007 [-0.018, 0.001] | -0.010 [-0.025, 0.002] | -0.002 [-0.013, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.029, 0.029] | -0.011 [-0.034, 0.011] | 0.007 [-0.014, 0.030] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | -0.004 [-0.009, -0.001] | -0.003 [-0.008, 0.001] |
| quarter_end | 31 | 0.014 [-0.099, 0.136] | -0.048 [-0.157, 0.059] | -0.040 [-0.135, 0.049] |
| tax_date | 89 | -0.047 [-0.107, 0.003] | -0.036 [-0.096, 0.018] | -0.029 [-0.090, 0.026] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.001, 0.001] |
| 1 | 324 | 0.002 [-0.000, 0.004] | -0.000 [-0.002, 0.001] | -0.001 [-0.003, 0.001] |
| 2 | 41 | -0.032 [–] | -0.050 [–] | -0.022 [–] |
| 3 | 473 | 0.004 [-0.015, 0.022] | -0.022 [-0.041, -0.005] | -0.015 [-0.037, 0.006] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.235, 0.000] |

## risk_gbm+combined against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.019, -0.003] |
| 3 | -0.009 [-0.017, -0.002] |
| 4 | -0.013 [-0.022, -0.005] |
| 5 | -0.011 [-0.019, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.045 [-0.073, -0.019] | -0.049 [-0.083, -0.019] | -0.057 [-0.087, -0.028] |
| 2020 | 251 | 0.011 [0.001, 0.025] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.015] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.023 [-0.051, -0.000] | -0.003 [-0.021, 0.013] | -0.005 [-0.029, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.054, -0.006] | -0.012 [-0.030, 0.006] | -0.014 [-0.025, -0.002] |
| ordinary | 1603 | -0.007 [-0.015, 0.001] | -0.008 [-0.016, -0.001] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | -0.020 [-0.074, 0.031] | -0.032 [-0.095, 0.023] | 0.006 [-0.026, 0.049] |
| tax_date | 89 | -0.040 [-0.075, -0.008] | -0.014 [-0.054, 0.021] | -0.036 [-0.085, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.001, 0.005] |
| 2 | 41 | -0.103 [–] | -0.034 [–] | -0.080 [–] |
| 3 | 473 | -0.036 [-0.063, -0.011] | -0.038 [-0.065, -0.013] | -0.039 [-0.067, -0.012] |

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

## risk_gbm+combined against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, 0.000] |
| 2 | -0.009 [-0.018, -0.001] |
| 3 | -0.011 [-0.019, -0.004] |
| 4 | -0.012 [-0.021, -0.004] |
| 5 | -0.010 [-0.018, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.041 [-0.072, -0.012] | -0.049 [-0.086, -0.015] | -0.049 [-0.083, -0.017] |
| 2020 | 251 | 0.023 [0.004, 0.049] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.004, 0.003] |
| 2025-26 | 249 | -0.019 [-0.043, 0.002] | -0.011 [-0.039, 0.010] | -0.004 [-0.029, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.037, 0.024] | -0.011 [-0.033, 0.012] | 0.005 [-0.018, 0.028] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.009 [-0.018, -0.002] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | 0.014 [-0.098, 0.132] | -0.048 [-0.155, 0.054] | -0.040 [-0.130, 0.052] |
| tax_date | 89 | -0.047 [-0.107, 0.003] | -0.036 [-0.092, 0.020] | -0.029 [-0.092, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.001, 0.002] | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.003] |
| 1 | 324 | 0.003 [0.000, 0.007] | 0.001 [-0.000, 0.003] | 0.001 [-0.001, 0.003] |
| 2 | 41 | -0.100 [–] | -0.098 [-0.184, 0.012] | -0.097 [–] |
| 3 | 473 | -0.025 [-0.054, 0.004] | -0.039 [-0.069, -0.012] | -0.033 [-0.063, -0.005] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.462, -0.130] |

## risk_gbm+combined_nogate against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.007 [-0.002, 0.018] |
| 2 | 0.013 [0.001, 0.027] |
| 3 | 0.009 [-0.003, 0.023] |
| 4 | 0.008 [-0.003, 0.021] |
| 5 | 0.007 [-0.006, 0.020] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [0.001, 0.098] | 0.061 [0.002, 0.124] | 0.051 [-0.008, 0.114] |
| 2020 | 251 | -0.017 [-0.026, -0.011] | -0.028 [-0.044, -0.013] | -0.036 [-0.050, -0.025] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | -0.002 [-0.007, 0.000] | 0.000 [-0.000, 0.001] | -0.000 [-0.001, 0.000] |
| 2025-26 | 249 | 0.008 [0.001, 0.015] | 0.009 [0.000, 0.020] | 0.028 [0.008, 0.053] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.004, 0.011] | 0.006 [-0.010, 0.021] | 0.032 [0.014, 0.053] |
| ordinary | 1603 | 0.008 [-0.003, 0.020] | 0.009 [-0.005, 0.025] | 0.001 [-0.012, 0.016] |
| quarter_end | 31 | 0.009 [-0.032, 0.049] | 0.031 [-0.018, 0.087] | 0.031 [-0.001, 0.066] |
| tax_date | 89 | 0.000 [-0.004, 0.004] | -0.000 [-0.027, 0.022] | 0.055 [0.021, 0.094] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, -0.000] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.009 [-0.011, -0.007] | -0.014 [-0.019, -0.009] | -0.021 [-0.027, -0.015] |
| 2 | 41 | 0.030 [-0.001, 0.046] | -0.020 [-0.129, 0.019] | 0.059 [0.003, 0.109] |
| 3 | 473 | 0.034 [-0.004, 0.077] | 0.048 [0.000, 0.099] | 0.041 [-0.008, 0.090] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.182, 0.167] |

## risk_gbm+combined_nogate against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.009, 0.001] |
| 2 | 0.001 [-0.006, 0.008] |
| 3 | 0.002 [-0.007, 0.011] |
| 4 | 0.003 [-0.005, 0.011] |
| 5 | 0.001 [-0.007, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.032, 0.019] | 0.023 [-0.018, 0.065] | 0.027 [-0.007, 0.057] |
| 2020 | 251 | -0.011 [-0.020, -0.002] | -0.029 [-0.041, -0.017] | -0.035 [-0.045, -0.027] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | 0.000 [-0.003, 0.004] | -0.000 [-0.001, -0.000] |
| 2025-26 | 249 | -0.006 [-0.015, 0.003] | 0.013 [-0.002, 0.030] | 0.019 [0.004, 0.037] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.002, 0.020] | 0.022 [0.003, 0.044] | 0.037 [0.016, 0.063] |
| ordinary | 1603 | -0.006 [-0.011, -0.000] | -0.001 [-0.009, 0.007] | -0.005 [-0.012, 0.001] |
| quarter_end | 31 | -0.006 [-0.051, 0.033] | 0.021 [-0.073, 0.103] | 0.005 [-0.061, 0.066] |
| tax_date | 89 | 0.002 [-0.032, 0.033] | 0.014 [-0.020, 0.052] | 0.054 [0.017, 0.100] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.003, -0.000] | -0.001 [-0.002, 0.000] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.008 [-0.013, -0.005] | -0.014 [-0.019, -0.009] | -0.021 [-0.027, -0.014] |
| 2 | 41 | -0.018 [–] | -0.034 [-0.132, 0.012] | 0.045 [–] |
| 3 | 473 | -0.007 [-0.027, 0.014] | 0.022 [-0.012, 0.058] | 0.018 [-0.010, 0.044] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.261, 0.062] |

## risk_gbm+combined_nogate against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.021 [0.012, 0.030] |
| 2 | 0.015 [0.006, 0.025] |
| 3 | 0.013 [0.004, 0.022] |
| 4 | 0.012 [0.004, 0.021] |
| 5 | 0.008 [-0.000, 0.017] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.048 [0.008, 0.090] | 0.025 [-0.020, 0.069] | 0.014 [-0.028, 0.056] |
| 2020 | 251 | 0.022 [0.011, 0.032] | 0.010 [-0.002, 0.021] | 0.000 [-0.012, 0.010] |
| 2021-23 | 748 | 0.012 [0.011, 0.014] | 0.012 [0.010, 0.014] | 0.009 [0.007, 0.010] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.004 [0.000, 0.007] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.023 [0.003, 0.047] | 0.010 [-0.003, 0.028] | 0.013 [0.003, 0.026] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.057 [0.035, 0.082] | 0.033 [0.017, 0.050] | 0.046 [0.029, 0.066] |
| ordinary | 1603 | 0.013 [0.004, 0.022] | 0.007 [-0.003, 0.017] | -0.001 [-0.011, 0.008] |
| quarter_end | 31 | 0.125 [0.043, 0.207] | 0.109 [0.028, 0.193] | 0.094 [0.009, 0.177] |
| tax_date | 89 | 0.069 [0.040, 0.097] | 0.053 [0.028, 0.078] | 0.081 [0.056, 0.107] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.008 [0.006, 0.010] | 0.008 [0.007, 0.010] | 0.007 [0.006, 0.009] |
| 1 | 324 | 0.020 [0.014, 0.027] | 0.015 [0.010, 0.020] | 0.006 [0.002, 0.011] |
| 2 | 41 | 0.023 [–] | -0.052 [–] | 0.018 [–] |
| 3 | 473 | 0.049 [0.017, 0.085] | 0.027 [-0.008, 0.064] | 0.011 [-0.022, 0.044] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.000 [-0.217, 0.231] |

## risk_gbm+combined_nogate against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.006 [-0.001, 0.014] |
| 2 | 0.005 [-0.004, 0.015] |
| 3 | 0.007 [-0.002, 0.015] |
| 4 | 0.004 [-0.004, 0.012] |
| 5 | 0.001 [-0.008, 0.009] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [0.001, 0.066] | 0.025 [-0.019, 0.066] | 0.016 [-0.026, 0.054] |
| 2020 | 251 | -0.001 [-0.012, 0.010] | -0.002 [-0.014, 0.008] | -0.018 [-0.026, -0.009] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | 0.002 [0.002, 0.003] | -0.003 [-0.004, -0.002] |
| 2024 | 250 | 0.002 [-0.001, 0.005] | 0.004 [0.001, 0.008] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.003 [-0.029, 0.021] | 0.004 [-0.018, 0.029] | 0.006 [-0.016, 0.027] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.036 [0.014, 0.060] | 0.024 [0.005, 0.043] | 0.037 [0.017, 0.058] |
| ordinary | 1603 | 0.000 [-0.006, 0.007] | 0.003 [-0.007, 0.011] | -0.007 [-0.016, 0.001] |
| quarter_end | 31 | 0.064 [-0.007, 0.142] | 0.074 [-0.019, 0.164] | 0.068 [-0.012, 0.149] |
| tax_date | 89 | 0.033 [-0.001, 0.075] | 0.025 [-0.011, 0.062] | 0.055 [0.017, 0.099] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, 0.001] | 0.002 [0.001, 0.003] | -0.000 [-0.001, 0.001] |
| 1 | 324 | -0.000 [-0.002, 0.002] | 0.005 [0.002, 0.008] | -0.007 [-0.011, -0.003] |
| 2 | 41 | -0.067 [–] | -0.098 [–] | -0.058 [-0.122, 0.023] |
| 3 | 473 | 0.029 [0.003, 0.058] | 0.027 [-0.009, 0.060] | 0.013 [-0.022, 0.044] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.000 [-0.176, 0.200] |

## risk_gbm+combined_nogate against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.007 [-0.002, 0.019] |
| 2 | 0.003 [-0.006, 0.015] |
| 3 | 0.003 [-0.007, 0.015] |
| 4 | 0.001 [-0.009, 0.010] |
| 5 | -0.003 [-0.013, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [0.000, 0.098] | 0.034 [-0.016, 0.084] | 0.011 [-0.037, 0.066] |
| 2020 | 251 | -0.016 [-0.023, -0.010] | -0.023 [-0.031, -0.015] | -0.031 [-0.039, -0.023] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.006 [0.001, 0.012] | 0.003 [0.000, 0.007] | 0.003 [0.000, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.002, 0.011] | 0.002 [-0.004, 0.009] | 0.002 [-0.003, 0.010] |
| ordinary | 1603 | 0.008 [-0.002, 0.021] | 0.004 [-0.008, 0.017] | -0.004 [-0.015, 0.008] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, -0.000] | -0.001 [-0.001, -0.001] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.009 [-0.011, -0.007] | -0.013 [-0.017, -0.009] | -0.022 [-0.025, -0.017] |
| 2 | 41 | 0.017 [–] | -0.010 [–] | 0.008 [–] |
| 3 | 473 | 0.035 [-0.002, 0.077] | 0.025 [-0.015, 0.067] | 0.004 [-0.034, 0.048] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.176, 0.167] |

## risk_gbm+combined_nogate against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [-0.000, 0.022] |
| 2 | 0.005 [-0.006, 0.016] |
| 3 | 0.002 [-0.009, 0.012] |
| 4 | 0.002 [-0.008, 0.012] |
| 5 | -0.003 [-0.013, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.050 [0.001, 0.106] | 0.034 [-0.015, 0.086] | 0.019 [-0.032, 0.072] |
| 2020 | 251 | -0.004 [-0.018, 0.012] | -0.028 [-0.042, -0.015] | -0.034 [-0.043, -0.025] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | -0.004 [-0.011, 0.000] | -0.001 [-0.003, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | 0.011 [0.001, 0.022] | -0.005 [-0.016, 0.005] | 0.003 [-0.006, 0.012] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.027 [0.009, 0.048] | 0.003 [-0.013, 0.018] | 0.021 [0.003, 0.041] |
| ordinary | 1603 | 0.009 [-0.003, 0.023] | 0.003 [-0.009, 0.015] | -0.005 [-0.016, 0.007] |
| quarter_end | 31 | 0.034 [-0.065, 0.129] | -0.016 [-0.091, 0.060] | -0.045 [-0.121, 0.022] |
| tax_date | 89 | -0.008 [-0.050, 0.031] | -0.022 [-0.056, 0.012] | 0.008 [-0.021, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.003, -0.000] | -0.001 [-0.001, 0.000] | -0.002 [-0.003, -0.000] |
| 1 | 324 | -0.008 [-0.011, -0.005] | -0.015 [-0.020, -0.010] | -0.022 [-0.028, -0.017] |
| 2 | 41 | 0.020 [–] | -0.073 [–] | -0.009 [-0.074, 0.032] |
| 3 | 473 | 0.046 [0.006, 0.090] | 0.024 [-0.015, 0.066] | 0.010 [-0.031, 0.052] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.000 [-0.176, 0.167] |

## risk_gbm+combined_nogate against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.007, 0.006] |
| 2 | -0.001 [-0.009, 0.006] |
| 3 | -0.001 [-0.009, 0.007] |
| 4 | -0.005 [-0.013, 0.002] |
| 5 | -0.009 [-0.017, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.006 [-0.021, 0.036] | 0.010 [-0.027, 0.047] | -0.017 [-0.051, 0.018] |
| 2020 | 251 | -0.009 [-0.022, 0.009] | -0.022 [-0.031, -0.014] | -0.030 [-0.039, -0.022] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.003 [0.001, 0.007] | 0.002 [0.001, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.005 [-0.020, 0.007] | 0.003 [-0.013, 0.017] | 0.001 [-0.020, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.003 [-0.007, 0.001] | 0.002 [-0.003, 0.009] | 0.000 [-0.003, 0.004] |
| ordinary | 1603 | -0.001 [-0.008, 0.007] | -0.001 [-0.010, 0.008] | -0.010 [-0.019, -0.002] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.002] | 0.001 [-0.000, 0.002] | -0.000 [-0.001, 0.001] |
| 1 | 324 | -0.007 [-0.010, -0.004] | -0.011 [-0.016, -0.007] | -0.020 [-0.024, -0.015] |
| 2 | 41 | -0.051 [–] | -0.058 [–] | -0.067 [-0.133, 0.006] |
| 3 | 473 | 0.005 [-0.018, 0.031] | 0.008 [-0.022, 0.038] | -0.015 [-0.044, 0.015] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.190 [-0.350, -0.053] |

## risk_gbm+combined_nogate against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.005, 0.009] |
| 2 | -0.000 [-0.008, 0.008] |
| 3 | -0.003 [-0.011, 0.005] |
| 4 | -0.004 [-0.012, 0.003] |
| 5 | -0.008 [-0.016, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.010 [-0.018, 0.039] | 0.010 [-0.027, 0.048] | -0.009 [-0.049, 0.029] |
| 2020 | 251 | 0.003 [-0.017, 0.027] | -0.027 [-0.042, -0.014] | -0.033 [-0.042, -0.026] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | -0.001 [-0.009, 0.005] | 0.001 [-0.001, 0.003] | 0.000 [-0.004, 0.003] |
| 2025-26 | 249 | -0.001 [-0.019, 0.016] | -0.006 [-0.030, 0.015] | 0.001 [-0.021, 0.022] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.021 [0.005, 0.041] | 0.003 [-0.013, 0.018] | 0.019 [0.001, 0.037] |
| ordinary | 1603 | -0.000 [-0.007, 0.008] | -0.002 [-0.011, 0.007] | -0.011 [-0.020, -0.002] |
| quarter_end | 31 | 0.034 [-0.062, 0.126] | -0.016 [-0.095, 0.064] | -0.045 [-0.117, 0.025] |
| tax_date | 89 | -0.008 [-0.047, 0.030] | -0.022 [-0.056, 0.012] | 0.008 [-0.022, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.001] | 0.001 [-0.000, 0.002] | -0.000 [-0.001, 0.001] |
| 1 | 324 | -0.007 [-0.010, -0.003] | -0.013 [-0.019, -0.008] | -0.021 [-0.027, -0.015] |
| 2 | 41 | -0.048 [–] | -0.121 [–] | -0.084 [–] |
| 3 | 473 | 0.016 [-0.009, 0.043] | 0.007 [-0.023, 0.038] | -0.009 [-0.041, 0.021] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.190 [-0.353, -0.053] |

## risk_gbm+combined_nogate against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.001, 0.019] |
| 2 | 0.009 [-0.001, 0.020] |
| 3 | 0.008 [-0.002, 0.020] |
| 4 | 0.008 [-0.002, 0.019] |
| 5 | 0.002 [-0.008, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.051 [0.009, 0.096] | 0.059 [0.010, 0.114] | 0.040 [-0.004, 0.088] |
| 2020 | 251 | -0.020 [-0.030, -0.012] | -0.028 [-0.043, -0.013] | -0.037 [-0.048, -0.027] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.000 [-0.000, 0.001] | 0.003 [-0.000, 0.009] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.018 [0.002, 0.038] | 0.005 [-0.003, 0.015] | 0.005 [-0.001, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.027 [0.005, 0.053] | 0.013 [-0.007, 0.034] | 0.014 [0.001, 0.028] |
| ordinary | 1603 | 0.006 [-0.003, 0.017] | 0.007 [-0.004, 0.020] | -0.001 [-0.011, 0.010] |
| quarter_end | 31 | 0.020 [-0.032, 0.079] | 0.032 [-0.021, 0.090] | -0.006 [-0.047, 0.027] |
| tax_date | 89 | 0.040 [0.009, 0.077] | 0.014 [-0.021, 0.054] | 0.036 [-0.005, 0.083] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.000 [-0.002, 0.001] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.010 [-0.012, -0.008] | -0.014 [-0.019, -0.009] | -0.022 [-0.028, -0.015] |
| 2 | 41 | 0.052 [–] | -0.023 [–] | 0.013 [–] |
| 3 | 473 | 0.042 [0.007, 0.079] | 0.046 [0.006, 0.091] | 0.024 [-0.012, 0.065] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.095 [0.000, 0.211] |

## risk_logistic+combined against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.007, 0.001] |
| 2 | 0.005 [-0.001, 0.011] |
| 3 | 0.001 [-0.004, 0.004] |
| 4 | 0.000 [-0.004, 0.004] |
| 5 | 0.003 [-0.003, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.008 [-0.028, 0.012] | -0.003 [-0.026, 0.014] | -0.000 [-0.026, 0.021] |
| 2020 | 251 | -0.006 [-0.016, 0.002] | 0.000 [-0.000, 0.001] | 0.002 [-0.001, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | -0.001 [-0.003, 0.001] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | -0.006 [-0.020, 0.005] | 0.009 [-0.001, 0.021] | 0.020 [0.006, 0.037] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.028 [-0.049, -0.009] | -0.007 [-0.025, 0.010] | 0.006 [-0.015, 0.026] |
| ordinary | 1603 | 0.001 [-0.003, 0.005] | 0.001 [-0.004, 0.005] | 0.001 [-0.005, 0.005] |
| quarter_end | 31 | -0.049 [-0.129, 0.026] | 0.006 [-0.063, 0.083] | 0.029 [-0.035, 0.101] |
| tax_date | 89 | -0.020 [-0.042, -0.001] | -0.002 [-0.030, 0.024] | 0.024 [-0.020, 0.068] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | -0.001 [-0.004, 0.001] | 0.000 [-0.000, 0.001] | 0.000 [-0.001, 0.001] |
| 2 | 41 | 0.003 [–] | 0.044 [0.004, 0.077] | 0.054 [–] |
| 3 | 473 | -0.014 [-0.031, 0.003] | -0.002 [-0.020, 0.012] | 0.006 [-0.015, 0.024] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.286, 0.000] |

## risk_logistic+combined against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.015 [-0.024, -0.006] |
| 2 | -0.007 [-0.016, 0.001] |
| 3 | -0.007 [-0.017, 0.002] |
| 4 | -0.005 [-0.015, 0.003] |
| 5 | -0.003 [-0.012, 0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.061 [-0.101, -0.025] | -0.042 [-0.088, 0.003] | -0.025 [-0.068, 0.017] |
| 2020 | 251 | 0.000 [-0.009, 0.007] | -0.001 [-0.006, 0.004] | 0.003 [-0.004, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.001 [-0.000, 0.002] | -0.001 [-0.003, 0.001] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.019 [-0.033, -0.006] | 0.013 [0.003, 0.026] | 0.011 [0.003, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.022 [-0.041, -0.004] | 0.009 [-0.009, 0.029] | 0.011 [-0.011, 0.034] |
| ordinary | 1603 | -0.013 [-0.022, -0.004] | -0.009 [-0.020, 0.000] | -0.006 [-0.015, 0.002] |
| quarter_end | 31 | -0.064 [-0.142, 0.005] | -0.004 [-0.091, 0.084] | 0.002 [-0.070, 0.068] |
| tax_date | 89 | -0.019 [-0.044, 0.004] | 0.013 [-0.007, 0.035] | 0.023 [-0.009, 0.066] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.001] | -0.000 [-0.001, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.000 [-0.004, 0.003] | -0.000 [-0.001, 0.000] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.046 [–] | 0.031 [0.001, 0.066] | 0.040 [–] |
| 3 | 473 | -0.054 [-0.087, -0.025] | -0.029 [-0.067, 0.007] | -0.017 [-0.051, 0.016] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.400, -0.083] |

## risk_logistic+combined against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.005, 0.015] |
| 2 | 0.007 [-0.000, 0.014] |
| 3 | 0.005 [-0.002, 0.011] |
| 4 | 0.004 [-0.003, 0.011] |
| 5 | 0.004 [-0.003, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.007 [-0.028, 0.015] | -0.040 [-0.065, -0.016] | -0.038 [-0.065, -0.012] |
| 2020 | 251 | 0.033 [0.024, 0.042] | 0.038 [0.028, 0.047] | 0.038 [0.027, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.005 [0.001, 0.009] | 0.003 [-0.000, 0.005] | 0.001 [-0.004, 0.005] |
| 2025-26 | 249 | 0.010 [0.001, 0.020] | 0.011 [0.003, 0.021] | 0.005 [-0.002, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.027 [0.012, 0.041] | 0.021 [0.006, 0.036] | 0.019 [0.000, 0.039] |
| ordinary | 1603 | 0.006 [0.001, 0.011] | -0.001 [-0.008, 0.006] | -0.002 [-0.008, 0.005] |
| quarter_end | 31 | 0.067 [-0.013, 0.144] | 0.084 [0.015, 0.148] | 0.092 [-0.008, 0.193] |
| tax_date | 89 | 0.048 [0.029, 0.068] | 0.051 [0.031, 0.070] | 0.050 [0.026, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.010 [0.008, 0.011] | 0.009 [0.008, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.029 [0.022, 0.035] | 0.029 [0.022, 0.035] | 0.028 [0.022, 0.034] |
| 2 | 41 | -0.005 [–] | 0.013 [-0.015, 0.055] | 0.013 [–] |
| 3 | 473 | 0.002 [-0.017, 0.020] | -0.024 [-0.045, -0.002] | -0.024 [-0.047, -0.002] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.143 [-0.375, 0.095] |

## risk_logistic+combined against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.002] |
| 2 | -0.003 [-0.011, 0.005] |
| 3 | -0.002 [-0.010, 0.006] |
| 4 | -0.004 [-0.012, 0.003] |
| 5 | -0.003 [-0.011, 0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.023 [-0.057, 0.004] | -0.040 [-0.071, -0.008] | -0.035 [-0.065, -0.008] |
| 2020 | 251 | 0.010 [0.000, 0.018] | 0.026 [0.018, 0.033] | 0.020 [0.012, 0.027] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.005 [0.001, 0.011] | 0.003 [0.002, 0.005] | 0.002 [-0.000, 0.004] |
| 2025-26 | 249 | -0.016 [-0.042, 0.005] | 0.005 [-0.013, 0.021] | -0.002 [-0.025, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.005 [-0.012, 0.023] | 0.011 [-0.001, 0.024] | 0.010 [-0.010, 0.030] |
| ordinary | 1603 | -0.007 [-0.015, 0.001] | -0.005 [-0.015, 0.003] | -0.008 [-0.016, 0.001] |
| quarter_end | 31 | 0.006 [-0.104, 0.111] | 0.049 [-0.042, 0.138] | 0.066 [-0.025, 0.163] |
| tax_date | 89 | 0.013 [-0.013, 0.038] | 0.024 [0.008, 0.040] | 0.024 [0.002, 0.057] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.002 [0.001, 0.003] | 0.003 [0.002, 0.004] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.008 [0.005, 0.011] | 0.019 [0.015, 0.023] | 0.014 [0.011, 0.018] |
| 2 | 41 | -0.094 [–] | -0.033 [-0.097, 0.049] | -0.063 [–] |
| 3 | 473 | -0.019 [-0.045, 0.003] | -0.024 [-0.051, 0.003] | -0.022 [-0.047, 0.002] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.143 [-0.357, 0.083] |

## risk_logistic+combined against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.008, 0.002] |
| 2 | -0.005 [-0.011, 0.001] |
| 3 | -0.005 [-0.010, -0.001] |
| 4 | -0.008 [-0.013, -0.003] |
| 5 | -0.008 [-0.013, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.009 [-0.029, 0.013] | -0.031 [-0.052, -0.011] | -0.040 [-0.060, -0.020] |
| 2020 | 251 | -0.005 [-0.014, 0.003] | 0.005 [-0.004, 0.015] | 0.007 [0.001, 0.014] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.003 [-0.000, 0.010] | -0.001 [-0.004, 0.001] | 0.000 [-0.000, 0.001] |
| 2025-26 | 249 | -0.008 [-0.021, 0.004] | 0.004 [-0.007, 0.014] | -0.005 [-0.017, 0.004] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.027 [-0.048, -0.008] | -0.011 [-0.032, 0.009] | -0.024 [-0.042, -0.009] |
| ordinary | 1603 | 0.001 [-0.003, 0.006] | -0.004 [-0.009, 0.000] | -0.005 [-0.010, -0.001] |
| quarter_end | 31 | -0.058 [-0.146, 0.027] | -0.025 [-0.073, 0.025] | -0.002 [-0.068, 0.067] |
| tax_date | 89 | -0.020 [-0.043, 0.000] | -0.002 [-0.035, 0.028] | -0.030 [-0.062, -0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.000 [-0.001, 0.001] | 0.000 [0.000, 0.000] |
| 1 | 324 | -0.001 [-0.004, 0.002] | 0.001 [-0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.011 [-0.042, 0.007] | 0.055 [–] | 0.003 [–] |
| 3 | 473 | -0.013 [-0.031, 0.005] | -0.026 [-0.044, -0.009] | -0.031 [-0.049, -0.014] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.292, 0.000] |

## risk_logistic+combined against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.004, 0.004] |
| 2 | -0.003 [-0.009, 0.003] |
| 3 | -0.007 [-0.012, -0.003] |
| 4 | -0.006 [-0.011, -0.002] |
| 5 | -0.007 [-0.012, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.005 [-0.024, 0.014] | -0.030 [-0.052, -0.011] | -0.032 [-0.056, -0.012] |
| 2020 | 251 | 0.007 [-0.000, 0.015] | 0.000 [-0.004, 0.005] | 0.004 [-0.000, 0.010] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.002 [-0.007, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.003 [-0.008, 0.002] | -0.004 [-0.012, 0.003] | -0.005 [-0.012, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.004 [-0.023, 0.015] | -0.010 [-0.027, 0.006] | -0.005 [-0.018, 0.007] |
| ordinary | 1603 | 0.002 [-0.002, 0.006] | -0.005 [-0.009, -0.001] | -0.005 [-0.010, -0.001] |
| quarter_end | 31 | -0.024 [-0.088, 0.024] | -0.041 [-0.113, 0.020] | -0.048 [-0.120, 0.014] |
| tax_date | 89 | -0.028 [-0.068, 0.006] | -0.023 [-0.070, 0.016] | -0.023 [-0.065, 0.015] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | 0.000 [-0.001, 0.001] | 0.000 [-0.001, 0.001] |
| 1 | 324 | 0.000 [-0.000, 0.000] | -0.001 [-0.002, 0.000] | -0.001 [-0.002, 0.000] |
| 2 | 41 | -0.008 [–] | -0.009 [–] | -0.014 [–] |
| 3 | 473 | -0.002 [-0.018, 0.014] | -0.027 [-0.044, -0.011] | -0.025 [-0.045, -0.008] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.143 [-0.292, 0.000] |

## risk_logistic+combined against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.011 [-0.019, -0.004] |
| 2 | -0.009 [-0.018, -0.002] |
| 3 | -0.009 [-0.018, -0.002] |
| 4 | -0.013 [-0.022, -0.005] |
| 5 | -0.013 [-0.022, -0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.049 [-0.082, -0.020] | -0.055 [-0.091, -0.022] | -0.068 [-0.098, -0.037] |
| 2020 | 251 | 0.002 [-0.008, 0.014] | 0.006 [-0.003, 0.016] | 0.007 [-0.000, 0.017] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.006 [0.001, 0.014] | 0.001 [-0.002, 0.004] | 0.003 [0.001, 0.006] |
| 2025-26 | 249 | -0.019 [-0.044, 0.002] | 0.003 [-0.011, 0.018] | -0.008 [-0.033, 0.015] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.033 [-0.056, -0.012] | -0.011 [-0.030, 0.008] | -0.026 [-0.044, -0.010] |
| ordinary | 1603 | -0.007 [-0.016, -0.000] | -0.009 [-0.018, -0.001] | -0.011 [-0.019, -0.003] |
| quarter_end | 31 | -0.058 [-0.150, 0.026] | -0.025 [-0.076, 0.026] | -0.002 [-0.068, 0.066] |
| tax_date | 89 | -0.020 [-0.043, 0.000] | -0.002 [-0.033, 0.030] | -0.030 [-0.060, -0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.002 [0.001, 0.004] | 0.002 [0.001, 0.003] | 0.001 [0.001, 0.003] |
| 1 | 324 | 0.001 [-0.003, 0.005] | 0.003 [0.000, 0.006] | 0.001 [-0.002, 0.005] |
| 2 | 41 | -0.078 [–] | 0.007 [-0.065, 0.104] | -0.072 [–] |
| 3 | 473 | -0.042 [-0.071, -0.017] | -0.043 [-0.072, -0.015] | -0.050 [-0.078, -0.022] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.333 [-0.500, -0.167] |

## risk_logistic+combined against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.009 [-0.016, -0.001] |
| 2 | -0.008 [-0.017, -0.001] |
| 3 | -0.011 [-0.020, -0.004] |
| 4 | -0.012 [-0.021, -0.004] |
| 5 | -0.012 [-0.020, -0.005] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.045 [-0.074, -0.015] | -0.055 [-0.091, -0.023] | -0.060 [-0.090, -0.030] |
| 2020 | 251 | 0.014 [0.001, 0.030] | 0.001 [-0.003, 0.005] | 0.004 [-0.002, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.003 [0.000, 0.007] | 0.000 [-0.004, 0.004] | 0.000 [-0.004, 0.004] |
| 2025-26 | 249 | -0.014 [-0.037, 0.004] | -0.005 [-0.024, 0.011] | -0.007 [-0.032, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.010 [-0.030, 0.011] | -0.010 [-0.027, 0.007] | -0.007 [-0.020, 0.005] |
| ordinary | 1603 | -0.007 [-0.015, 0.000] | -0.010 [-0.019, -0.002] | -0.011 [-0.020, -0.004] |
| quarter_end | 31 | -0.024 [-0.086, 0.024] | -0.041 [-0.113, 0.018] | -0.048 [-0.124, 0.015] |
| tax_date | 89 | -0.028 [-0.069, 0.006] | -0.023 [-0.071, 0.015] | -0.023 [-0.064, 0.014] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.002 [0.001, 0.003] | 0.002 [0.001, 0.003] |
| 1 | 324 | 0.001 [0.000, 0.004] | 0.001 [-0.000, 0.002] | 0.001 [-0.001, 0.002] |
| 2 | 41 | -0.075 [–] | -0.057 [-0.136, 0.032] | -0.089 [–] |
| 3 | 473 | -0.031 [-0.058, -0.004] | -0.043 [-0.074, -0.017] | -0.044 [-0.072, -0.018] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.333 [-0.500, -0.167] |

## risk_logistic+combined_nogate against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.006, 0.017] |
| 2 | 0.012 [-0.002, 0.026] |
| 3 | 0.011 [-0.002, 0.025] |
| 4 | 0.007 [-0.005, 0.019] |
| 5 | 0.006 [-0.006, 0.019] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.043 [-0.008, 0.097] | 0.061 [0.002, 0.124] | 0.043 [-0.015, 0.104] |
| 2020 | 251 | -0.029 [-0.048, -0.014] | -0.023 [-0.034, -0.011] | -0.033 [-0.046, -0.022] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.001 [-0.000, 0.004] | 0.002 [-0.000, 0.004] | 0.002 [-0.000, 0.005] |
| 2025-26 | 249 | 0.003 [-0.008, 0.013] | 0.017 [0.001, 0.036] | 0.027 [0.006, 0.052] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.021 [-0.040, -0.003] | 0.005 [-0.017, 0.028] | 0.014 [-0.014, 0.040] |
| ordinary | 1603 | 0.008 [-0.004, 0.021] | 0.010 [-0.004, 0.026] | 0.002 [-0.012, 0.016] |
| quarter_end | 31 | -0.025 [-0.111, 0.056] | 0.046 [-0.049, 0.144] | 0.076 [0.001, 0.155] |
| tax_date | 89 | 0.008 [-0.030, 0.046] | 0.021 [-0.007, 0.052] | 0.047 [0.008, 0.094] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.001 [-0.002, 0.000] | -0.002 [-0.003, -0.001] |
| 1 | 324 | -0.010 [-0.013, -0.006] | -0.012 [-0.016, -0.007] | -0.020 [-0.025, -0.015] |
| 2 | 41 | 0.027 [–] | 0.043 [–] | 0.077 [–] |
| 3 | 473 | 0.023 [-0.021, 0.069] | 0.049 [0.001, 0.102] | 0.035 [-0.014, 0.084] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.286, 0.048] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.364, 0.125] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.083 [-0.417, 0.222] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.350, 0.059] |

## risk_logistic+combined_nogate against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.007 [-0.013, 0.000] |
| 2 | -0.000 [-0.008, 0.007] |
| 3 | 0.004 [-0.005, 0.014] |
| 4 | 0.002 [-0.006, 0.010] |
| 5 | 0.000 [-0.008, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.010 [-0.037, 0.021] | 0.023 [-0.021, 0.069] | 0.019 [-0.017, 0.055] |
| 2020 | 251 | -0.022 [-0.040, -0.007] | -0.024 [-0.031, -0.017] | -0.032 [-0.041, -0.026] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.001 [-0.000, 0.003] | 0.001 [-0.002, 0.007] | 0.002 [-0.000, 0.005] |
| 2025-26 | 249 | -0.011 [-0.017, -0.005] | 0.021 [0.003, 0.042] | 0.018 [0.004, 0.036] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.014 [-0.039, 0.008] | 0.021 [-0.001, 0.045] | 0.018 [-0.008, 0.047] |
| ordinary | 1603 | -0.006 [-0.012, -0.001] | -0.000 [-0.009, 0.008] | -0.005 [-0.011, 0.001] |
| quarter_end | 31 | -0.040 [-0.140, 0.048] | 0.037 [-0.079, 0.152] | 0.050 [-0.040, 0.138] |
| tax_date | 89 | 0.009 [-0.023, 0.048] | 0.036 [-0.008, 0.088] | 0.046 [-0.006, 0.108] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.001, 0.000] | -0.001 [-0.002, 0.000] | -0.002 [-0.003, -0.001] |
| 1 | 324 | -0.009 [-0.012, -0.005] | -0.012 [-0.017, -0.008] | -0.020 [-0.024, -0.015] |
| 2 | 41 | -0.021 [–] | 0.030 [–] | 0.062 [–] |
| 3 | 473 | -0.018 [-0.042, 0.009] | 0.022 [-0.013, 0.060] | 0.012 [-0.017, 0.042] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.435, -0.105] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.455, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.333 [-0.643, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.421, -0.053] |

## risk_logistic+combined_nogate against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.018 [0.010, 0.028] |
| 2 | 0.014 [0.005, 0.023] |
| 3 | 0.015 [0.006, 0.025] |
| 4 | 0.011 [0.003, 0.019] |
| 5 | 0.007 [-0.001, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.045 [0.004, 0.090] | 0.025 [-0.022, 0.070] | 0.006 [-0.036, 0.049] |
| 2020 | 251 | 0.010 [-0.005, 0.025] | 0.015 [0.005, 0.024] | 0.003 [-0.010, 0.014] |
| 2021-23 | 748 | 0.012 [0.011, 0.014] | 0.012 [0.011, 0.014] | 0.009 [0.007, 0.011] |
| 2024 | 250 | 0.005 [0.001, 0.009] | 0.005 [0.002, 0.009] | 0.003 [0.000, 0.006] |
| 2025-26 | 249 | 0.018 [0.003, 0.037] | 0.018 [0.003, 0.036] | 0.013 [0.003, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.034 [0.007, 0.062] | 0.032 [0.011, 0.055] | 0.027 [0.003, 0.053] |
| ordinary | 1603 | 0.012 [0.004, 0.022] | 0.008 [-0.002, 0.018] | -0.001 [-0.010, 0.009] |
| quarter_end | 31 | 0.091 [0.009, 0.165] | 0.125 [0.066, 0.186] | 0.139 [0.068, 0.212] |
| tax_date | 89 | 0.076 [0.045, 0.114] | 0.074 [0.037, 0.115] | 0.073 [0.031, 0.114] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.008 [0.007, 0.010] | 0.007 [0.006, 0.009] |
| 1 | 324 | 0.020 [0.015, 0.026] | 0.017 [0.012, 0.022] | 0.007 [0.003, 0.012] |
| 2 | 41 | 0.020 [–] | 0.012 [–] | 0.035 [–] |
| 3 | 473 | 0.038 [0.004, 0.077] | 0.028 [-0.007, 0.065] | 0.005 [-0.028, 0.039] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.242, 0.077] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.417, -0.067] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.167 [-0.364, 0.000] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.143 [-0.333, 0.000] |

## risk_logistic+combined_nogate against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.003 [-0.004, 0.012] |
| 2 | 0.004 [-0.005, 0.013] |
| 3 | 0.009 [-0.000, 0.018] |
| 4 | 0.003 [-0.006, 0.011] |
| 5 | -0.000 [-0.009, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.028 [-0.006, 0.064] | 0.025 [-0.018, 0.069] | 0.008 [-0.033, 0.047] |
| 2020 | 251 | -0.013 [-0.031, 0.003] | 0.003 [-0.003, 0.008] | -0.015 [-0.024, -0.006] |
| 2021-23 | 748 | -0.001 [-0.001, -0.000] | 0.002 [0.002, 0.003] | -0.003 [-0.004, -0.002] |
| 2024 | 250 | 0.005 [0.001, 0.012] | 0.005 [0.002, 0.011] | 0.003 [0.001, 0.007] |
| 2025-26 | 249 | -0.007 [-0.030, 0.011] | 0.012 [-0.005, 0.032] | 0.005 [-0.017, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.011, 0.038] | 0.023 [0.003, 0.045] | 0.018 [-0.009, 0.044] |
| ordinary | 1603 | -0.000 [-0.007, 0.006] | 0.003 [-0.005, 0.013] | -0.007 [-0.016, 0.001] |
| quarter_end | 31 | 0.030 [-0.091, 0.151] | 0.090 [-0.035, 0.221] | 0.114 [0.004, 0.227] |
| tax_date | 89 | 0.041 [0.005, 0.089] | 0.047 [-0.001, 0.106] | 0.047 [-0.002, 0.105] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.001, 0.002] | 0.002 [0.000, 0.004] | -0.000 [-0.001, 0.001] |
| 1 | 324 | -0.001 [-0.004, 0.002] | 0.007 [0.005, 0.009] | -0.006 [-0.009, -0.003] |
| 2 | 41 | -0.070 [-0.179, 0.041] | -0.034 [–] | -0.040 [–] |
| 3 | 473 | 0.018 [-0.011, 0.048] | 0.027 [-0.007, 0.063] | 0.007 [-0.028, 0.039] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.235, 0.080] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.333, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.462, -0.056] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | -0.143 [-0.316, 0.000] |

## risk_logistic+combined_nogate against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.005 [-0.006, 0.017] |
| 2 | 0.002 [-0.008, 0.013] |
| 3 | 0.005 [-0.005, 0.017] |
| 4 | -0.001 [-0.010, 0.010] |
| 5 | -0.004 [-0.015, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.043 [-0.007, 0.095] | 0.034 [-0.018, 0.089] | 0.004 [-0.048, 0.055] |
| 2020 | 251 | -0.028 [-0.045, -0.014] | -0.018 [-0.026, -0.010] | -0.028 [-0.039, -0.016] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.004 [-0.000, 0.011] | 0.001 [-0.000, 0.003] | 0.002 [-0.000, 0.007] |
| 2025-26 | 249 | 0.001 [-0.010, 0.010] | 0.011 [-0.001, 0.027] | 0.002 [-0.005, 0.011] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.020 [-0.040, -0.002] | 0.001 [-0.014, 0.017] | -0.016 [-0.037, 0.002] |
| ordinary | 1603 | 0.008 [-0.003, 0.020] | 0.005 [-0.007, 0.018] | -0.004 [-0.015, 0.008] |
| quarter_end | 31 | -0.034 [-0.133, 0.061] | 0.016 [-0.059, 0.091] | 0.045 [-0.023, 0.118] |
| tax_date | 89 | 0.008 [-0.028, 0.047] | 0.022 [-0.012, 0.056] | -0.008 [-0.039, 0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.002] | -0.001 [-0.002, -0.000] | -0.002 [-0.003, -0.000] |
| 1 | 324 | -0.009 [-0.014, -0.005] | -0.011 [-0.015, -0.006] | -0.021 [-0.024, -0.017] |
| 2 | 41 | 0.014 [-0.034, 0.039] | 0.054 [-0.043, 0.106] | 0.025 [–] |
| 3 | 473 | 0.024 [-0.019, 0.069] | 0.025 [-0.015, 0.070] | -0.002 [-0.043, 0.039] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.333, 0.026] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.364, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.083 [-0.417, 0.235] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.143 [-0.353, 0.059] |

## risk_logistic+combined_nogate against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.007 [-0.002, 0.019] |
| 2 | 0.003 [-0.007, 0.015] |
| 3 | 0.003 [-0.006, 0.015] |
| 4 | 0.001 [-0.008, 0.010] |
| 5 | -0.003 [-0.014, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [0.001, 0.100] | 0.034 [-0.014, 0.087] | 0.011 [-0.039, 0.063] |
| 2020 | 251 | -0.016 [-0.023, -0.009] | -0.023 [-0.031, -0.015] | -0.031 [-0.039, -0.022] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.006 [0.001, 0.012] | 0.003 [0.000, 0.006] | 0.003 [0.000, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.002, 0.011] | 0.002 [-0.003, 0.009] | 0.002 [-0.003, 0.011] |
| ordinary | 1603 | 0.008 [-0.003, 0.022] | 0.004 [-0.007, 0.017] | -0.004 [-0.016, 0.009] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, -0.000] | -0.001 [-0.001, -0.001] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.009 [-0.010, -0.007] | -0.013 [-0.017, -0.008] | -0.022 [-0.025, -0.017] |
| 2 | 41 | 0.017 [–] | -0.010 [–] | 0.008 [–] |
| 3 | 473 | 0.035 [-0.002, 0.079] | 0.025 [-0.014, 0.067] | 0.004 [-0.036, 0.045] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.423, -0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.353, 0.118] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.167 [-0.500, 0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.143 [-0.348, 0.062] |

## risk_logistic+combined_nogate against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.010, 0.005] |
| 2 | -0.003 [-0.010, 0.005] |
| 3 | 0.001 [-0.007, 0.009] |
| 4 | -0.006 [-0.014, 0.002] |
| 5 | -0.010 [-0.018, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.003 [-0.030, 0.037] | 0.010 [-0.031, 0.050] | -0.024 [-0.061, 0.012] |
| 2020 | 251 | -0.020 [-0.039, -0.003] | -0.017 [-0.025, -0.009] | -0.027 [-0.040, -0.015] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.000] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.007 [0.001, 0.015] | 0.004 [0.001, 0.007] | 0.005 [0.001, 0.009] |
| 2025-26 | 249 | -0.010 [-0.026, 0.004] | 0.011 [-0.004, 0.026] | -0.000 [-0.023, 0.022] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.026 [-0.045, -0.008] | 0.001 [-0.014, 0.016] | -0.019 [-0.039, -0.002] |
| ordinary | 1603 | -0.001 [-0.008, 0.007] | -0.000 [-0.010, 0.009] | -0.010 [-0.019, -0.001] |
| quarter_end | 31 | -0.034 [-0.125, 0.059] | 0.016 [-0.061, 0.090] | 0.045 [-0.022, 0.121] |
| tax_date | 89 | 0.008 [-0.031, 0.048] | 0.022 [-0.011, 0.057] | -0.008 [-0.039, 0.021] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.003] | 0.001 [-0.001, 0.002] | -0.000 [-0.002, 0.002] |
| 1 | 324 | -0.008 [-0.013, -0.003] | -0.009 [-0.014, -0.004] | -0.019 [-0.023, -0.015] |
| 2 | 41 | -0.054 [-0.120, 0.002] | 0.006 [-0.085, 0.097] | -0.050 [–] |
| 3 | 473 | -0.006 [-0.033, 0.024] | 0.009 [-0.024, 0.039] | -0.021 [-0.051, 0.010] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.460, -0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.118] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.417 [-0.647, -0.182] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.333 [-0.500, -0.167] |

## risk_logistic+combined_nogate against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.001 [-0.006, 0.006] |
| 2 | -0.001 [-0.009, 0.006] |
| 3 | -0.001 [-0.009, 0.007] |
| 4 | -0.005 [-0.012, 0.002] |
| 5 | -0.009 [-0.017, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.006 [-0.019, 0.038] | 0.010 [-0.029, 0.045] | -0.017 [-0.052, 0.019] |
| 2020 | 251 | -0.009 [-0.022, 0.008] | -0.022 [-0.031, -0.013] | -0.030 [-0.039, -0.022] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.001 [-0.002, -0.000] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.003 [0.001, 0.007] | 0.002 [0.001, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.005 [-0.022, 0.006] | 0.003 [-0.013, 0.016] | 0.001 [-0.020, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.003 [-0.007, 0.001] | 0.002 [-0.003, 0.009] | 0.000 [-0.003, 0.004] |
| ordinary | 1603 | -0.001 [-0.007, 0.007] | -0.001 [-0.010, 0.008] | -0.010 [-0.019, -0.002] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.002] | 0.001 [-0.000, 0.002] | -0.000 [-0.001, 0.001] |
| 1 | 324 | -0.007 [-0.010, -0.004] | -0.011 [-0.016, -0.006] | -0.020 [-0.024, -0.015] |
| 2 | 41 | -0.051 [–] | -0.058 [–] | -0.067 [–] |
| 3 | 473 | 0.005 [-0.017, 0.031] | 0.008 [-0.024, 0.037] | -0.015 [-0.044, 0.014] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.464, -0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.294 [-0.500, -0.111] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.333 [–] |
| ordinary | 12 | -0.417 [-0.636, -0.182] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.333 [-0.500, -0.167] |

## risk_logistic+combined_nogate against risk_logistic+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [-0.001, 0.018] |
| 2 | 0.007 [-0.003, 0.018] |
| 3 | 0.010 [-0.001, 0.023] |
| 4 | 0.007 [-0.003, 0.019] |
| 5 | 0.003 [-0.007, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.051 [0.009, 0.096] | 0.065 [0.011, 0.124] | 0.044 [-0.003, 0.096] |
| 2020 | 251 | -0.023 [-0.035, -0.011] | -0.023 [-0.034, -0.012] | -0.035 [-0.047, -0.023] |
| 2021-23 | 748 | -0.001 [-0.002, -0.001] | -0.002 [-0.002, -0.001] | -0.005 [-0.007, -0.003] |
| 2024 | 250 | 0.000 [-0.000, 0.001] | 0.002 [-0.000, 0.007] | 0.002 [-0.000, 0.006] |
| 2025-26 | 249 | 0.008 [-0.000, 0.018] | 0.007 [-0.001, 0.017] | 0.007 [-0.001, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.007 [-0.013, 0.027] | 0.012 [-0.005, 0.029] | 0.008 [-0.006, 0.023] |
| ordinary | 1603 | 0.006 [-0.003, 0.017] | 0.009 [-0.003, 0.022] | 0.001 [-0.010, 0.013] |
| quarter_end | 31 | 0.024 [-0.025, 0.089] | 0.041 [-0.021, 0.112] | 0.048 [-0.013, 0.125] |
| tax_date | 89 | 0.028 [-0.006, 0.070] | 0.023 [-0.016, 0.070] | 0.023 [-0.014, 0.064] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.001 [-0.002, 0.000] | -0.002 [-0.003, -0.001] |
| 1 | 324 | -0.009 [-0.011, -0.007] | -0.012 [-0.016, -0.008] | -0.021 [-0.025, -0.015] |
| 2 | 41 | 0.024 [-0.004, 0.039] | -0.001 [–] | 0.022 [–] |
| 3 | 473 | 0.037 [0.001, 0.075] | 0.051 [0.008, 0.099] | 0.029 [-0.009, 0.073] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.182, 0.095] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.100, 0.217] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | -0.500 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.317] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.158, 0.154] |

## risk_gbm+combined_no_factor against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.004 [-0.002, 0.010] |
| 3 | 0.001 [-0.004, 0.005] |
| 4 | 0.000 [-0.004, 0.005] |
| 5 | 0.005 [-0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.005 [-0.021, 0.013] | 0.004 [-0.021, 0.025] | 0.011 [-0.015, 0.035] |
| 2020 | 251 | 0.003 [-0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.003, 0.004] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.010 [-0.028, 0.002] | 0.003 [-0.002, 0.008] | 0.022 [0.004, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.050, -0.002] | -0.007 [-0.022, 0.007] | 0.019 [0.008, 0.032] |
| ordinary | 1603 | 0.002 [-0.002, 0.006] | 0.002 [-0.003, 0.007] | 0.003 [-0.003, 0.008] |
| quarter_end | 31 | -0.011 [-0.067, 0.044] | -0.002 [-0.066, 0.064] | 0.037 [0.000, 0.080] |
| tax_date | 89 | -0.039 [-0.077, -0.012] | -0.015 [-0.058, 0.022] | 0.018 [-0.036, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.022 [–] | 0.002 [–] | 0.046 [–] |
| 3 | 473 | -0.008 [-0.023, 0.008] | 0.003 [-0.016, 0.020] | 0.017 [-0.006, 0.037] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_factor against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.006] |
| 2 | -0.008 [-0.017, 0.000] |
| 3 | -0.006 [-0.016, 0.003] |
| 4 | -0.005 [-0.014, 0.003] |
| 5 | -0.001 [-0.009, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.057 [-0.097, -0.023] | -0.034 [-0.079, 0.011] | -0.013 [-0.053, 0.026] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.041, -0.009] | 0.007 [-0.002, 0.020] | 0.014 [0.000, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.007, 0.025] | 0.024 [0.004, 0.047] |
| ordinary | 1603 | -0.012 [-0.021, -0.004] | -0.008 [-0.018, 0.001] | -0.004 [-0.013, 0.004] |
| quarter_end | 31 | -0.026 [-0.093, 0.026] | -0.011 [-0.075, 0.055] | 0.010 [-0.039, 0.057] |
| tax_date | 89 | -0.038 [-0.073, -0.008] | 0.000 [-0.034, 0.028] | 0.017 [-0.013, 0.049] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.070 [-0.098, -0.021] | -0.011 [–] | 0.032 [–] |
| 3 | 473 | -0.048 [-0.081, -0.020] | -0.023 [-0.060, 0.013] | -0.006 [-0.037, 0.026] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.346, -0.053] |

## risk_gbm+combined_no_factor against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.006, 0.016] |
| 2 | 0.006 [-0.002, 0.013] |
| 3 | 0.005 [-0.002, 0.011] |
| 4 | 0.004 [-0.003, 0.011] |
| 5 | 0.007 [0.000, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.003 [-0.025, 0.020] | -0.033 [-0.059, -0.006] | -0.026 [-0.053, -0.001] |
| 2020 | 251 | 0.042 [0.034, 0.050] | 0.038 [0.028, 0.047] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.015] | 0.005 [-0.007, 0.018] | 0.008 [-0.002, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.045] | 0.020 [0.011, 0.028] | 0.032 [0.020, 0.047] |
| ordinary | 1603 | 0.007 [0.002, 0.012] | 0.000 [-0.007, 0.007] | 0.000 [-0.006, 0.006] |
| quarter_end | 31 | 0.105 [0.018, 0.199] | 0.077 [-0.018, 0.173] | 0.100 [0.003, 0.194] |
| tax_date | 89 | 0.029 [-0.003, 0.057] | 0.038 [0.007, 0.065] | 0.044 [0.013, 0.073] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.023, 0.036] | 0.028 [0.021, 0.034] |
| 2 | 41 | -0.029 [–] | -0.029 [–] | 0.005 [–] |
| 3 | 473 | 0.008 [-0.011, 0.027] | -0.018 [-0.043, 0.005] | -0.013 [-0.037, 0.008] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.334, 0.154] |

## risk_gbm+combined_no_factor against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.012, 0.004] |
| 2 | -0.004 [-0.012, 0.004] |
| 3 | -0.002 [-0.009, 0.006] |
| 4 | -0.004 [-0.011, 0.003] |
| 5 | -0.001 [-0.008, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.020 [-0.054, 0.011] | -0.033 [-0.063, -0.001] | -0.023 [-0.051, 0.005] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.026] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.004] | 0.001 [-0.001, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.020 [-0.051, 0.003] | -0.001 [-0.026, 0.021] | 0.000 [-0.023, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.016, 0.033] | 0.011 [-0.002, 0.023] | 0.023 [0.009, 0.041] |
| ordinary | 1603 | -0.006 [-0.015, 0.002] | -0.004 [-0.013, 0.004] | -0.006 [-0.014, 0.002] |
| quarter_end | 31 | 0.045 [-0.009, 0.106] | 0.042 [-0.012, 0.103] | 0.074 [0.018, 0.143] |
| tax_date | 89 | -0.006 [-0.036, 0.018] | 0.011 [-0.008, 0.032] | 0.018 [-0.003, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.119 [–] | -0.075 [–] | -0.071 [–] |
| 3 | 473 | -0.013 [-0.041, 0.012] | -0.018 [-0.045, 0.009] | -0.011 [-0.035, 0.014] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.300, 0.125] |

## risk_gbm+combined_no_factor against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | -0.005 [-0.011, 0.000] |
| 3 | -0.005 [-0.010, -0.000] |
| 4 | -0.007 [-0.013, -0.003] |
| 5 | -0.005 [-0.010, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.005 [-0.022, 0.013] | -0.023 [-0.046, -0.004] | -0.028 [-0.050, -0.009] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.003, 0.014] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.012 [-0.029, 0.001] | -0.002 [-0.011, 0.004] | -0.003 [-0.009, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.046, -0.001] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.000] |
| ordinary | 1603 | 0.002 [-0.001, 0.007] | -0.003 [-0.008, 0.001] | -0.003 [-0.008, 0.001] |
| quarter_end | 31 | -0.020 [-0.077, 0.033] | -0.032 [-0.093, 0.026] | 0.006 [-0.026, 0.050] |
| tax_date | 89 | -0.040 [-0.075, -0.008] | -0.014 [-0.054, 0.022] | -0.036 [-0.083, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.035 [–] | 0.012 [–] | -0.005 [–] |
| 3 | 473 | -0.007 [-0.022, 0.009] | -0.020 [-0.039, -0.004] | -0.020 [-0.038, -0.004] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_factor against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.004, 0.005] |
| 2 | -0.004 [-0.011, 0.002] |
| 3 | -0.007 [-0.012, -0.002] |
| 4 | -0.006 [-0.012, -0.001] |
| 5 | -0.004 [-0.010, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.022, 0.019] | -0.023 [-0.046, -0.002] | -0.020 [-0.049, 0.003] |
| 2020 | 251 | 0.016 [0.003, 0.032] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.012, 0.000] | -0.004 [-0.012, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.007 [-0.018, 0.002] | -0.010 [-0.025, 0.002] | -0.002 [-0.013, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.029, 0.028] | -0.011 [-0.032, 0.011] | 0.007 [-0.013, 0.029] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | -0.004 [-0.008, -0.000] | -0.003 [-0.008, 0.000] |
| quarter_end | 31 | 0.014 [-0.099, 0.131] | -0.048 [-0.155, 0.058] | -0.040 [-0.133, 0.048] |
| tax_date | 89 | -0.047 [-0.106, 0.003] | -0.036 [-0.091, 0.016] | -0.029 [-0.090, 0.026] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.001, 0.001] |
| 1 | 324 | 0.002 [-0.000, 0.004] | -0.000 [-0.002, 0.001] | -0.001 [-0.003, 0.001] |
| 2 | 41 | -0.032 [–] | -0.051 [–] | -0.022 [–] |
| 3 | 473 | 0.004 [-0.014, 0.022] | -0.021 [-0.040, -0.003] | -0.014 [-0.037, 0.005] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.231, 0.000] |

## risk_gbm+combined_no_factor against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.018, -0.003] |
| 3 | -0.009 [-0.017, -0.002] |
| 4 | -0.013 [-0.022, -0.005] |
| 5 | -0.010 [-0.019, -0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.045 [-0.076, -0.018] | -0.047 [-0.079, -0.016] | -0.056 [-0.086, -0.029] |
| 2020 | 251 | 0.011 [0.002, 0.026] | 0.006 [-0.002, 0.015] | 0.007 [-0.000, 0.015] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.007] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.023 [-0.053, -0.001] | -0.003 [-0.022, 0.011] | -0.005 [-0.029, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.055, -0.006] | -0.012 [-0.031, 0.007] | -0.014 [-0.026, -0.002] |
| ordinary | 1603 | -0.007 [-0.015, 0.001] | -0.008 [-0.016, -0.001] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | -0.020 [-0.079, 0.033] | -0.032 [-0.094, 0.025] | 0.006 [-0.027, 0.047] |
| tax_date | 89 | -0.040 [-0.077, -0.009] | -0.014 [-0.056, 0.024] | -0.036 [-0.080, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.002, 0.005] |
| 2 | 41 | -0.102 [–] | -0.035 [-0.109, 0.076] | -0.080 [-0.155, 0.011] |
| 3 | 473 | -0.036 [-0.063, -0.011] | -0.037 [-0.064, -0.012] | -0.039 [-0.066, -0.013] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.458, -0.120] |

## risk_gbm+combined_no_factor against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, 0.001] |
| 2 | -0.009 [-0.018, -0.001] |
| 3 | -0.011 [-0.020, -0.003] |
| 4 | -0.012 [-0.021, -0.004] |
| 5 | -0.010 [-0.018, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.041 [-0.072, -0.011] | -0.047 [-0.083, -0.014] | -0.048 [-0.084, -0.015] |
| 2020 | 251 | 0.023 [0.004, 0.048] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.005, 0.003] |
| 2025-26 | 249 | -0.018 [-0.043, 0.002] | -0.011 [-0.038, 0.010] | -0.004 [-0.029, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.037, 0.024] | -0.011 [-0.032, 0.010] | 0.005 [-0.016, 0.028] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.009 [-0.017, -0.001] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | 0.014 [-0.097, 0.132] | -0.048 [-0.158, 0.057] | -0.040 [-0.132, 0.055] |
| tax_date | 89 | -0.047 [-0.107, 0.005] | -0.036 [-0.095, 0.016] | -0.029 [-0.090, 0.030] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.002, 0.002] | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.007] | 0.001 [-0.000, 0.002] | 0.001 [-0.001, 0.003] |
| 2 | 41 | -0.099 [–] | -0.099 [–] | -0.097 [–] |
| 3 | 473 | -0.025 [-0.054, 0.005] | -0.038 [-0.067, -0.010] | -0.033 [-0.062, -0.003] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.455, -0.125] |

## risk_gbm+combined_no_factor against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.000, 0.000] |
| 2 | -0.000 [-0.000, 0.000] |
| 3 | 0.000 [-0.000, 0.001] |
| 4 | 0.000 [-0.000, 0.000] |
| 5 | 0.000 [-0.000, 0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.000 [-0.001, 0.001] | 0.002 [-0.001, 0.005] | 0.001 [-0.000, 0.001] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2025-26 | 249 | 0.000 [0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [0.000, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| ordinary | 1603 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.001] | 0.000 [-0.000, 0.000] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] |
| 1 | 324 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2 | 41 | 0.000 [–] | -0.001 [–] | 0.000 [–] |
| 3 | 473 | 0.000 [-0.001, 0.001] | 0.001 [-0.001, 0.004] | 0.000 [-0.000, 0.001] |

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

## risk_gbm+combined_no_structural against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.007, 0.002] |
| 2 | 0.004 [-0.000, 0.008] |
| 3 | 0.002 [-0.001, 0.005] |
| 4 | 0.002 [-0.001, 0.005] |
| 5 | 0.005 [0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.029, 0.016] | 0.008 [-0.005, 0.022] | 0.012 [-0.006, 0.031] |
| 2020 | 251 | 0.003 [0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.003, 0.004] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.008, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.010 [-0.027, 0.002] | 0.003 [-0.002, 0.009] | 0.022 [0.004, 0.046] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.001] | -0.007 [-0.022, 0.007] | 0.019 [0.008, 0.032] |
| ordinary | 1603 | 0.002 [-0.003, 0.007] | 0.003 [0.001, 0.006] | 0.003 [-0.001, 0.007] |
| quarter_end | 31 | -0.011 [-0.068, 0.044] | -0.002 [-0.061, 0.064] | 0.037 [0.002, 0.081] |
| tax_date | 89 | -0.039 [-0.074, -0.010] | -0.015 [-0.058, 0.022] | 0.018 [-0.035, 0.075] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.021 [-0.051, -0.001] | 0.003 [–] | 0.046 [–] |
| 3 | 473 | -0.009 [-0.028, 0.010] | 0.007 [-0.004, 0.018] | 0.018 [0.001, 0.036] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.207, 0.050] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.238, 0.125] |
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

## risk_gbm+combined_no_structural against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.014 [-0.023, -0.007] |
| 2 | -0.008 [-0.017, -0.000] |
| 3 | -0.005 [-0.015, 0.003] |
| 4 | -0.003 [-0.013, 0.005] |
| 5 | -0.000 [-0.010, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.058 [-0.095, -0.027] | -0.030 [-0.076, 0.010] | -0.012 [-0.061, 0.032] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.005, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.023 [-0.042, -0.008] | 0.007 [-0.002, 0.021] | 0.014 [0.000, 0.030] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.037, -0.001] | 0.008 [-0.008, 0.025] | 0.024 [0.003, 0.047] |
| ordinary | 1603 | -0.012 [-0.022, -0.005] | -0.007 [-0.017, 0.001] | -0.004 [-0.014, 0.005] |
| quarter_end | 31 | -0.026 [-0.088, 0.027] | -0.011 [-0.076, 0.052] | 0.010 [-0.041, 0.060] |
| tax_date | 89 | -0.038 [-0.076, -0.006] | 0.000 [-0.034, 0.029] | 0.017 [-0.013, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.001, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.070 [-0.097, -0.019] | -0.010 [–] | 0.032 [–] |
| 3 | 473 | -0.049 [-0.081, -0.022] | -0.020 [-0.056, 0.013] | -0.005 [-0.043, 0.031] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.400, -0.083] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.364, 0.000] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.500, -0.062] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.300, 0.000] |

## risk_gbm+combined_no_structural against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.011 [0.006, 0.017] |
| 2 | 0.007 [0.001, 0.012] |
| 3 | 0.006 [-0.000, 0.011] |
| 4 | 0.006 [-0.000, 0.011] |
| 5 | 0.007 [0.001, 0.013] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.004 [-0.028, 0.018] | -0.028 [-0.052, -0.007] | -0.025 [-0.047, -0.001] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.027, 0.047] | 0.037 [0.026, 0.048] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.004, 0.016] | 0.005 [-0.006, 0.018] | 0.008 [-0.002, 0.020] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.043] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.047] |
| ordinary | 1603 | 0.007 [0.002, 0.011] | 0.001 [-0.004, 0.006] | 0.001 [-0.005, 0.006] |
| quarter_end | 31 | 0.105 [0.015, 0.195] | 0.077 [-0.019, 0.173] | 0.100 [0.007, 0.193] |
| tax_date | 89 | 0.029 [-0.003, 0.058] | 0.038 [0.008, 0.066] | 0.044 [0.013, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.022, 0.036] | 0.028 [0.022, 0.034] |
| 2 | 41 | -0.029 [-0.048, -0.001] | -0.028 [-0.050, 0.013] | 0.005 [–] |
| 3 | 473 | 0.007 [-0.014, 0.026] | -0.014 [-0.035, 0.005] | -0.012 [-0.032, 0.009] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.222, 0.152] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.391, 0.002] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.385, 0.232] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.267, 0.188] |

## risk_gbm+combined_no_structural against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.011, 0.003] |
| 2 | -0.003 [-0.010, 0.003] |
| 3 | -0.001 [-0.008, 0.005] |
| 4 | -0.002 [-0.009, 0.004] |
| 5 | -0.001 [-0.008, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.021 [-0.049, 0.006] | -0.028 [-0.056, -0.004] | -0.022 [-0.051, 0.004] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.010, 0.026] |
| 2021-23 | 748 | 0.001 [0.001, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.004] | 0.001 [-0.002, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.020 [-0.051, 0.003] | -0.001 [-0.024, 0.020] | 0.000 [-0.024, 0.025] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.017, 0.032] | 0.011 [-0.002, 0.023] | 0.023 [0.008, 0.041] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.003 [-0.011, 0.004] | -0.005 [-0.014, 0.002] |
| quarter_end | 31 | 0.045 [-0.007, 0.108] | 0.042 [-0.011, 0.107] | 0.074 [0.019, 0.141] |
| tax_date | 89 | -0.006 [-0.036, 0.017] | 0.011 [-0.007, 0.030] | 0.018 [-0.002, 0.043] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.023] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.119 [–] | -0.074 [–] | -0.071 [–] |
| 3 | 473 | -0.013 [-0.038, 0.009] | -0.015 [-0.038, 0.007] | -0.010 [-0.035, 0.012] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.184, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.250, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.429, 0.100] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.231, 0.150] |

## risk_gbm+combined_no_structural against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.007, 0.002] |
| 2 | -0.005 [-0.009, -0.001] |
| 3 | -0.004 [-0.007, -0.000] |
| 4 | -0.006 [-0.010, -0.002] |
| 5 | -0.005 [-0.009, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.028, 0.015] | -0.019 [-0.034, -0.005] | -0.027 [-0.043, -0.011] |
| 2020 | 251 | 0.004 [0.000, 0.008] | 0.005 [-0.003, 0.014] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.012 [-0.028, 0.001] | -0.002 [-0.010, 0.004] | -0.003 [-0.008, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.047, -0.001] | -0.012 [-0.030, 0.007] | -0.011 [-0.023, -0.001] |
| ordinary | 1603 | 0.002 [-0.003, 0.007] | -0.002 [-0.005, 0.001] | -0.003 [-0.006, 0.000] |
| quarter_end | 31 | -0.020 [-0.075, 0.032] | -0.032 [-0.091, 0.029] | 0.006 [-0.027, 0.046] |
| tax_date | 89 | -0.040 [-0.074, -0.008] | -0.014 [-0.055, 0.024] | -0.036 [-0.082, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.035 [–] | 0.013 [–] | -0.005 [–] |
| 3 | 473 | -0.008 [-0.026, 0.011] | -0.017 [-0.029, -0.004] | -0.019 [-0.033, -0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.115 [-0.276, 0.033] on 26 onsets.

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.048 [-0.211, 0.095] |

## risk_gbm+combined_no_structural against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.005, 0.006] |
| 2 | -0.004 [-0.009, 0.001] |
| 3 | -0.006 [-0.010, -0.002] |
| 4 | -0.005 [-0.009, -0.001] |
| 5 | -0.004 [-0.009, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.028, 0.022] | -0.019 [-0.037, -0.000] | -0.019 [-0.042, 0.003] |
| 2020 | 251 | 0.016 [0.003, 0.032] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.011, 0.000] | -0.004 [-0.012, 0.000] | -0.002 [-0.007, 0.000] |
| 2025-26 | 249 | -0.007 [-0.017, 0.001] | -0.010 [-0.025, 0.002] | -0.002 [-0.013, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.031, 0.029] | -0.011 [-0.033, 0.011] | 0.007 [-0.013, 0.029] |
| ordinary | 1603 | 0.003 [-0.002, 0.007] | -0.003 [-0.006, 0.000] | -0.003 [-0.007, 0.000] |
| quarter_end | 31 | 0.014 [-0.099, 0.132] | -0.048 [-0.155, 0.056] | -0.040 [-0.131, 0.051] |
| tax_date | 89 | -0.047 [-0.109, 0.002] | -0.036 [-0.094, 0.018] | -0.029 [-0.087, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.001, 0.001] |
| 1 | 324 | 0.002 [-0.000, 0.005] | -0.000 [-0.002, 0.001] | -0.001 [-0.002, 0.001] |
| 2 | 41 | -0.032 [–] | -0.050 [–] | -0.022 [-0.074, 0.017] |
| 3 | 473 | 0.003 [-0.019, 0.024] | -0.017 [-0.033, -0.003] | -0.013 [-0.033, 0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.364, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.192, 0.100] |

## risk_gbm+combined_no_structural against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.018, -0.003] |
| 3 | -0.008 [-0.016, -0.001] |
| 4 | -0.012 [-0.020, -0.004] |
| 5 | -0.010 [-0.019, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.046 [-0.073, -0.018] | -0.043 [-0.074, -0.015] | -0.055 [-0.088, -0.026] |
| 2020 | 251 | 0.011 [0.001, 0.026] | 0.006 [-0.003, 0.015] | 0.007 [-0.001, 0.016] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.003 [-0.000, 0.007] | -0.001 [-0.008, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.023 [-0.051, -0.000] | -0.003 [-0.020, 0.013] | -0.005 [-0.029, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.056, -0.005] | -0.012 [-0.030, 0.008] | -0.014 [-0.025, -0.003] |
| ordinary | 1603 | -0.007 [-0.014, 0.000] | -0.007 [-0.015, -0.000] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | -0.020 [-0.079, 0.030] | -0.032 [-0.094, 0.025] | 0.006 [-0.027, 0.050] |
| tax_date | 89 | -0.040 [-0.076, -0.009] | -0.014 [-0.056, 0.022] | -0.036 [-0.082, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.001, 0.005] |
| 2 | 41 | -0.102 [–] | -0.034 [–] | -0.080 [-0.153, 0.011] |
| 3 | 473 | -0.037 [-0.063, -0.011] | -0.034 [-0.060, -0.010] | -0.038 [-0.067, -0.011] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.429, -0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.429, -0.067] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [–] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.400, -0.083] |

## risk_gbm+combined_no_structural against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.008 [-0.016, -0.000] |
| 2 | -0.009 [-0.017, -0.001] |
| 3 | -0.010 [-0.018, -0.003] |
| 4 | -0.010 [-0.019, -0.003] |
| 5 | -0.009 [-0.018, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.042 [-0.072, -0.014] | -0.043 [-0.076, -0.013] | -0.047 [-0.082, -0.014] |
| 2020 | 251 | 0.023 [0.005, 0.048] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.004, 0.003] |
| 2025-26 | 249 | -0.018 [-0.043, 0.002] | -0.011 [-0.037, 0.010] | -0.004 [-0.030, 0.021] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.037, 0.023] | -0.011 [-0.032, 0.011] | 0.005 [-0.016, 0.028] |
| ordinary | 1603 | -0.006 [-0.014, 0.000] | -0.008 [-0.016, -0.001] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | 0.014 [-0.103, 0.126] | -0.048 [-0.156, 0.059] | -0.040 [-0.133, 0.047] |
| tax_date | 89 | -0.047 [-0.110, 0.002] | -0.036 [-0.096, 0.016] | -0.029 [-0.089, 0.027] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.002, 0.002] | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.007] | 0.001 [-0.000, 0.002] | 0.001 [-0.001, 0.003] |
| 2 | 41 | -0.099 [–] | -0.098 [–] | -0.097 [–] |
| 3 | 473 | -0.026 [-0.056, 0.000] | -0.034 [-0.062, -0.010] | -0.032 [-0.062, -0.004] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.423, -0.125] on 26 onsets.

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
| ordinary | 12 | -0.333 [-0.556, -0.111] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.238 [-0.393, -0.091] |

## risk_gbm+combined_no_structural against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.000 [-0.003, 0.002] |
| 2 | 0.000 [-0.004, 0.005] |
| 3 | 0.001 [-0.002, 0.005] |
| 4 | 0.002 [-0.001, 0.005] |
| 5 | 0.000 [-0.003, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.014, 0.011] | 0.006 [-0.009, 0.024] | 0.002 [-0.015, 0.022] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| ordinary | 1603 | -0.000 [-0.003, 0.003] | 0.001 [-0.002, 0.005] | 0.000 [-0.004, 0.005] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 324 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2 | 41 | 0.001 [–] | 0.000 [-0.000, 0.000] | 0.000 [–] |
| 3 | 473 | -0.001 [-0.011, 0.009] | 0.005 [-0.007, 0.019] | 0.001 [-0.012, 0.017] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [0.000, 0.115] on 26 onsets.

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
| ordinary | 12 | 0.083 [0.000, 0.235] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.143] |

## risk_gbm+combined_no_projected against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.002] |
| 2 | 0.004 [-0.002, 0.010] |
| 3 | -0.000 [-0.005, 0.004] |
| 4 | 0.000 [-0.005, 0.004] |
| 5 | 0.005 [-0.001, 0.011] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.019, 0.018] | -0.001 [-0.025, 0.021] | 0.011 [-0.017, 0.037] |
| 2020 | 251 | 0.003 [0.000, 0.006] | 0.000 [-0.001, 0.001] | 0.001 [-0.002, 0.004] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | -0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.008, 0.000] | -0.003 [-0.009, 0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.011 [-0.027, 0.002] | 0.003 [-0.002, 0.008] | 0.022 [0.004, 0.046] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.025 [-0.048, -0.003] | -0.007 [-0.023, 0.007] | 0.019 [0.007, 0.032] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | 0.001 [-0.004, 0.005] | 0.003 [-0.004, 0.008] |
| quarter_end | 31 | -0.011 [-0.068, 0.044] | -0.002 [-0.067, 0.058] | 0.037 [0.001, 0.079] |
| tax_date | 89 | -0.039 [-0.075, -0.009] | -0.015 [-0.059, 0.023] | 0.018 [-0.035, 0.078] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.002] | 0.000 [-0.000, 0.001] | 0.001 [0.000, 0.001] |
| 2 | 41 | -0.023 [–] | -0.001 [–] | 0.044 [–] |
| 3 | 473 | -0.005 [-0.021, 0.011] | -0.000 [-0.020, 0.016] | 0.016 [-0.008, 0.039] |

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
| ordinary | 12 | -0.083 [-0.250, 0.000] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.095 [-0.235, 0.000] |

## risk_gbm+combined_no_projected against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.013 [-0.022, -0.006] |
| 2 | -0.008 [-0.017, 0.000] |
| 3 | -0.007 [-0.017, 0.001] |
| 4 | -0.005 [-0.014, 0.002] |
| 5 | -0.001 [-0.009, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.054 [-0.094, -0.021] | -0.039 [-0.086, 0.002] | -0.013 [-0.054, 0.023] |
| 2020 | 251 | 0.009 [0.005, 0.014] | -0.001 [-0.006, 0.003] | 0.002 [-0.006, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.003 [-0.009, 0.000] | -0.003 [-0.007, 0.000] | -0.001 [-0.001, 0.000] |
| 2025-26 | 249 | -0.024 [-0.042, -0.008] | 0.007 [-0.003, 0.019] | 0.013 [0.001, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.018 [-0.038, -0.001] | 0.008 [-0.007, 0.026] | 0.023 [0.004, 0.045] |
| ordinary | 1603 | -0.011 [-0.021, -0.003] | -0.009 [-0.020, -0.000] | -0.004 [-0.013, 0.004] |
| quarter_end | 31 | -0.026 [-0.090, 0.028] | -0.011 [-0.078, 0.057] | 0.010 [-0.037, 0.058] |
| tax_date | 89 | -0.038 [-0.076, -0.007] | 0.000 [-0.035, 0.027] | 0.017 [-0.012, 0.049] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, 0.000] | -0.001 [-0.002, 0.000] | -0.000 [-0.000, 0.000] |
| 1 | 324 | 0.002 [-0.002, 0.005] | 0.000 [-0.000, 0.000] | 0.001 [0.000, 0.002] |
| 2 | 41 | -0.072 [–] | -0.014 [–] | 0.030 [–] |
| 3 | 473 | -0.046 [-0.078, -0.018] | -0.027 [-0.066, 0.007] | -0.006 [-0.039, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.269 [-0.435, -0.118] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.235 [-0.423, -0.071] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.333 [-0.600, -0.117] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.190 [-0.353, -0.053] |

## risk_gbm+combined_no_projected against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.012 [0.007, 0.017] |
| 2 | 0.006 [-0.001, 0.013] |
| 3 | 0.004 [-0.004, 0.010] |
| 4 | 0.004 [-0.003, 0.011] |
| 5 | 0.006 [-0.000, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.000 [-0.022, 0.021] | -0.037 [-0.066, -0.013] | -0.026 [-0.052, -0.002] |
| 2020 | 251 | 0.042 [0.035, 0.050] | 0.038 [0.027, 0.047] | 0.037 [0.026, 0.047] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.001 [-0.004, 0.005] | 0.001 [-0.005, 0.005] | 0.001 [-0.005, 0.005] |
| 2025-26 | 249 | 0.005 [-0.005, 0.015] | 0.004 [-0.007, 0.018] | 0.007 [-0.003, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.030 [0.017, 0.044] | 0.020 [0.011, 0.029] | 0.032 [0.020, 0.046] |
| ordinary | 1603 | 0.008 [0.002, 0.012] | -0.001 [-0.008, 0.005] | 0.000 [-0.007, 0.006] |
| quarter_end | 31 | 0.105 [0.017, 0.195] | 0.077 [-0.022, 0.175] | 0.100 [0.002, 0.200] |
| tax_date | 89 | 0.029 [-0.002, 0.058] | 0.038 [0.009, 0.068] | 0.044 [0.011, 0.074] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.023, 0.037] | 0.029 [0.023, 0.036] | 0.028 [0.022, 0.034] |
| 2 | 41 | -0.031 [-0.050, -0.000] | -0.032 [-0.053, 0.014] | 0.003 [–] |
| 3 | 473 | 0.010 [-0.009, 0.028] | -0.022 [-0.048, 0.001] | -0.014 [-0.037, 0.008] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.269, 0.118] on 26 onsets.

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.333, 0.148] |

## risk_gbm+combined_no_projected against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.011, 0.004] |
| 2 | -0.004 [-0.012, 0.004] |
| 3 | -0.002 [-0.010, 0.005] |
| 4 | -0.004 [-0.012, 0.002] |
| 5 | -0.001 [-0.008, 0.006] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.017 [-0.049, 0.013] | -0.037 [-0.066, -0.009] | -0.024 [-0.053, 0.003] |
| 2020 | 251 | 0.019 [0.013, 0.026] | 0.026 [0.018, 0.032] | 0.020 [0.011, 0.027] |
| 2021-23 | 748 | 0.001 [0.001, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.001 [-0.002, 0.005] | 0.001 [-0.001, 0.002] | 0.001 [-0.001, 0.003] |
| 2025-26 | 249 | -0.021 [-0.054, 0.003] | -0.002 [-0.026, 0.019] | -0.000 [-0.025, 0.024] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.008 [-0.017, 0.033] | 0.011 [-0.001, 0.024] | 0.023 [0.008, 0.040] |
| ordinary | 1603 | -0.005 [-0.014, 0.003] | -0.005 [-0.014, 0.003] | -0.006 [-0.014, 0.002] |
| quarter_end | 31 | 0.045 [-0.011, 0.104] | 0.042 [-0.012, 0.103] | 0.074 [0.016, 0.138] |
| tax_date | 89 | -0.006 [-0.035, 0.018] | 0.011 [-0.009, 0.030] | 0.018 [-0.002, 0.043] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.002] | 0.002 [0.002, 0.003] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.010 [0.007, 0.012] | 0.020 [0.015, 0.024] | 0.015 [0.011, 0.018] |
| 2 | 41 | -0.120 [–] | -0.078 [–] | -0.073 [–] |
| 3 | 473 | -0.010 [-0.036, 0.014] | -0.022 [-0.048, 0.003] | -0.011 [-0.037, 0.011] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.241, 0.095] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.357, -0.038] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.250 [-0.538, 0.000] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.095 [-0.312, 0.118] |

## risk_gbm+combined_no_projected against risk_gbm+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.006, 0.003] |
| 2 | -0.006 [-0.011, 0.000] |
| 3 | -0.006 [-0.011, -0.001] |
| 4 | -0.008 [-0.013, -0.003] |
| 5 | -0.005 [-0.010, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.002 [-0.019, 0.017] | -0.028 [-0.050, -0.008] | -0.028 [-0.050, -0.009] |
| 2020 | 251 | 0.004 [0.001, 0.008] | 0.005 [-0.003, 0.015] | 0.007 [0.002, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, 0.000] | -0.003 [-0.009, 0.000] | -0.000 [-0.000, 0.000] |
| 2025-26 | 249 | -0.013 [-0.029, 0.000] | -0.003 [-0.011, 0.003] | -0.003 [-0.010, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.024 [-0.048, -0.003] | -0.012 [-0.030, 0.007] | -0.012 [-0.022, -0.000] |
| ordinary | 1603 | 0.003 [-0.001, 0.007] | -0.004 [-0.009, -0.000] | -0.003 [-0.008, 0.001] |
| quarter_end | 31 | -0.020 [-0.077, 0.030] | -0.032 [-0.092, 0.026] | 0.006 [-0.027, 0.048] |
| tax_date | 89 | -0.040 [-0.076, -0.009] | -0.014 [-0.054, 0.022] | -0.036 [-0.083, 0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [0.000, 0.003] | 0.002 [0.000, 0.004] | 0.000 [-0.003, 0.003] |
| 2 | 41 | -0.037 [-0.073, -0.007] | 0.010 [–] | -0.007 [–] |
| 3 | 473 | -0.005 [-0.020, 0.012] | -0.024 [-0.043, -0.007] | -0.020 [-0.039, -0.003] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.296, -0.036] on 26 onsets.

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
| 3 | 21 | -0.095 [-0.227, 0.000] |

## risk_gbm+combined_no_projected against risk_logistic+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.003, 0.006] |
| 2 | -0.004 [-0.011, 0.002] |
| 3 | -0.008 [-0.013, -0.002] |
| 4 | -0.006 [-0.012, -0.001] |
| 5 | -0.004 [-0.010, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.002 [-0.016, 0.022] | -0.028 [-0.051, -0.005] | -0.021 [-0.048, 0.005] |
| 2020 | 251 | 0.016 [0.003, 0.033] | 0.000 [-0.004, 0.003] | 0.004 [-0.000, 0.009] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.004 [-0.012, 0.000] | -0.004 [-0.013, 0.000] | -0.002 [-0.006, 0.000] |
| 2025-26 | 249 | -0.008 [-0.018, 0.001] | -0.011 [-0.026, 0.002] | -0.003 [-0.013, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.029, 0.029] | -0.011 [-0.033, 0.011] | 0.007 [-0.014, 0.029] |
| ordinary | 1603 | 0.003 [-0.000, 0.008] | -0.005 [-0.010, -0.001] | -0.003 [-0.008, 0.001] |
| quarter_end | 31 | 0.014 [-0.099, 0.131] | -0.048 [-0.162, 0.055] | -0.040 [-0.134, 0.056] |
| tax_date | 89 | -0.047 [-0.106, 0.003] | -0.036 [-0.095, 0.016] | -0.029 [-0.089, 0.028] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.002, 0.001] | -0.000 [-0.002, 0.001] | 0.000 [-0.001, 0.001] |
| 1 | 324 | 0.002 [-0.000, 0.004] | -0.000 [-0.002, 0.001] | -0.001 [-0.003, 0.001] |
| 2 | 41 | -0.034 [–] | -0.054 [–] | -0.025 [–] |
| 3 | 473 | 0.006 [-0.011, 0.025] | -0.025 [-0.044, -0.007] | -0.015 [-0.037, 0.006] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.387, -0.083] on 26 onsets.

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
| ordinary | 12 | -0.167 [-0.375, 0.000] |
| quarter_end | 3 | -0.667 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | -0.500 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.227, 0.000] |

## risk_gbm+combined_no_projected against risk_gbm+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.018, -0.003] |
| 2 | -0.010 [-0.018, -0.003] |
| 3 | -0.010 [-0.018, -0.003] |
| 4 | -0.013 [-0.023, -0.005] |
| 5 | -0.011 [-0.019, -0.003] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.042 [-0.073, -0.014] | -0.052 [-0.085, -0.022] | -0.056 [-0.086, -0.027] |
| 2020 | 251 | 0.011 [0.002, 0.026] | 0.006 [-0.002, 0.015] | 0.007 [-0.001, 0.016] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.001] |
| 2024 | 250 | 0.002 [-0.000, 0.007] | -0.001 [-0.007, 0.004] | 0.002 [0.001, 0.005] |
| 2025-26 | 249 | -0.024 [-0.052, -0.001] | -0.004 [-0.021, 0.012] | -0.005 [-0.031, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.030 [-0.056, -0.006] | -0.012 [-0.030, 0.007] | -0.014 [-0.025, -0.003] |
| ordinary | 1603 | -0.006 [-0.014, 0.001] | -0.009 [-0.017, -0.002] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | -0.020 [-0.075, 0.033] | -0.032 [-0.094, 0.022] | 0.006 [-0.026, 0.045] |
| tax_date | 89 | -0.040 [-0.076, -0.008] | -0.014 [-0.053, 0.025] | -0.036 [-0.083, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [0.000, 0.003] | 0.001 [0.000, 0.002] | 0.001 [0.001, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.006] | 0.003 [0.001, 0.006] | 0.002 [-0.001, 0.005] |
| 2 | 41 | -0.104 [-0.180, -0.021] | -0.038 [–] | -0.082 [–] |
| 3 | 473 | -0.034 [-0.061, -0.008] | -0.041 [-0.069, -0.016] | -0.039 [-0.066, -0.012] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.458, -0.158] on 26 onsets.

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.457, -0.133] |

## risk_gbm+combined_no_projected against risk_logistic+every_day+gate+settle+h41

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.007 [-0.015, 0.000] |
| 2 | -0.009 [-0.018, -0.001] |
| 3 | -0.012 [-0.021, -0.004] |
| 4 | -0.012 [-0.021, -0.004] |
| 5 | -0.010 [-0.018, -0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.038 [-0.071, -0.009] | -0.052 [-0.087, -0.021] | -0.049 [-0.082, -0.016] |
| 2020 | 251 | 0.023 [0.004, 0.048] | 0.001 [-0.003, 0.004] | 0.004 [-0.003, 0.011] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.001 [0.000, 0.001] | 0.000 [0.000, 0.000] |
| 2024 | 250 | -0.001 [-0.010, 0.005] | -0.002 [-0.010, 0.003] | -0.000 [-0.005, 0.003] |
| 2025-26 | 249 | -0.019 [-0.046, 0.002] | -0.012 [-0.039, 0.010] | -0.005 [-0.031, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.006 [-0.038, 0.024] | -0.011 [-0.033, 0.010] | 0.005 [-0.017, 0.029] |
| ordinary | 1603 | -0.005 [-0.013, 0.002] | -0.010 [-0.019, -0.003] | -0.009 [-0.017, -0.002] |
| quarter_end | 31 | 0.014 [-0.097, 0.130] | -0.048 [-0.154, 0.056] | -0.040 [-0.134, 0.054] |
| tax_date | 89 | -0.047 [-0.111, 0.003] | -0.036 [-0.097, 0.016] | -0.029 [-0.092, 0.028] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.002, 0.002] | 0.001 [-0.000, 0.003] | 0.001 [0.000, 0.002] |
| 1 | 324 | 0.003 [0.000, 0.007] | 0.001 [-0.000, 0.003] | 0.001 [-0.001, 0.003] |
| 2 | 41 | -0.101 [–] | -0.101 [-0.188, 0.008] | -0.100 [-0.171, 0.000] |
| 3 | 473 | -0.023 [-0.053, 0.004] | -0.041 [-0.071, -0.016] | -0.033 [-0.063, -0.006] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.308 [-0.469, -0.154] on 26 onsets.

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | -0.286 [-0.458, -0.125] |

## risk_gbm+combined_no_projected against risk_gbm+combined

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.001 [-0.000, 0.001] |
| 2 | -0.000 [-0.001, 0.001] |
| 3 | -0.001 [-0.002, 0.000] |
| 4 | -0.000 [-0.000, 0.000] |
| 5 | -0.000 [-0.002, 0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.003 [-0.000, 0.007] | -0.003 [-0.009, 0.002] | 0.000 [-0.007, 0.006] |
| 2020 | 251 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2021-23 | 748 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2024 | 250 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2025-26 | 249 | -0.000 [-0.001, 0.000] | -0.001 [-0.002, -0.000] | -0.001 [-0.001, -0.000] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| ordinary | 1603 | 0.001 [-0.000, 0.002] | -0.001 [-0.002, 0.000] | -0.000 [-0.002, 0.001] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 1 | 324 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| 2 | 41 | -0.001 [-0.004, 0.001] | -0.003 [–] | -0.002 [–] |
| 3 | 473 | 0.002 [-0.000, 0.006] | -0.003 [-0.007, 0.001] | 0.000 [-0.006, 0.005] |

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


## Predicted against realised rate of a pressure day (+5 bp), by regime and day type, pooled over h = 1 to 5

### risk_gbm+combined

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0164 | 0.0741 |
| day type month_end | 750 | 0.0386 | 0.1133 |
| day type ordinary | 8009 | 0.0112 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0647 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0007 | 0.0000 |
| regime 2024 | 1250 | 0.0001 | 0.0200 |
| regime 2025-26 | 1245 | 0.0171 | 0.1165 |

### risk_gbm+combined_nogate

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.1022 | 0.0741 |
| day type month_end | 750 | 0.1032 | 0.1133 |
| day type ordinary | 8009 | 0.0995 | 0.0627 |
| day type quarter_end | 151 | 0.1996 | 0.2715 |
| day type tax_date | 445 | 0.1168 | 0.1461 |
| regime 2018-19 | 1865 | 0.2972 | 0.2697 |
| regime 2020 | 1255 | 0.1640 | 0.0159 |
| regime 2021-23 | 3740 | 0.0354 | 0.0000 |
| regime 2024 | 1250 | 0.0077 | 0.0200 |
| regime 2025-26 | 1245 | 0.0433 | 0.1165 |

### risk_logistic+combined

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0172 | 0.0741 |
| day type month_end | 750 | 0.0391 | 0.1133 |
| day type ordinary | 8009 | 0.0094 | 0.0627 |
| day type quarter_end | 151 | 0.2212 | 0.2715 |
| day type tax_date | 445 | 0.0510 | 0.1461 |
| regime 2018-19 | 1865 | 0.0644 | 0.2697 |
| regime 2020 | 1255 | 0.0085 | 0.0159 |
| regime 2021-23 | 3740 | 0.0008 | 0.0000 |
| regime 2024 | 1250 | 0.0022 | 0.0200 |
| regime 2025-26 | 1245 | 0.0197 | 0.1165 |

### risk_logistic+combined_nogate

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.1050 | 0.0741 |
| day type month_end | 750 | 0.1035 | 0.1133 |
| day type ordinary | 8009 | 0.0993 | 0.0627 |
| day type quarter_end | 151 | 0.3278 | 0.2715 |
| day type tax_date | 445 | 0.1338 | 0.1461 |
| regime 2018-19 | 1865 | 0.3074 | 0.2697 |
| regime 2020 | 1255 | 0.1633 | 0.0159 |
| regime 2021-23 | 3740 | 0.0356 | 0.0000 |
| regime 2024 | 1250 | 0.0119 | 0.0200 |
| regime 2025-26 | 1245 | 0.0451 | 0.1165 |

### risk_gbm+combined_no_factor

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0165 | 0.0741 |
| day type month_end | 750 | 0.0387 | 0.1133 |
| day type ordinary | 8009 | 0.0113 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0646 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0009 | 0.0000 |
| regime 2024 | 1250 | 0.0001 | 0.0200 |
| regime 2025-26 | 1245 | 0.0171 | 0.1165 |

### risk_gbm+combined_no_structural

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0157 | 0.0741 |
| day type month_end | 750 | 0.0383 | 0.1133 |
| day type ordinary | 8009 | 0.0105 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0614 | 0.2697 |
| regime 2020 | 1255 | 0.0071 | 0.0159 |
| regime 2021-23 | 3740 | 0.0003 | 0.0000 |
| regime 2024 | 1250 | 0.0003 | 0.0200 |
| regime 2025-26 | 1245 | 0.0177 | 0.1165 |

### risk_gbm+combined_no_projected

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9355 | 0.0164 | 0.0741 |
| day type month_end | 750 | 0.0386 | 0.1133 |
| day type ordinary | 8009 | 0.0112 | 0.0627 |
| day type quarter_end | 151 | 0.1053 | 0.2715 |
| day type tax_date | 445 | 0.0423 | 0.1461 |
| regime 2018-19 | 1865 | 0.0670 | 0.2697 |
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

