# Reserves projected to the scored day (#545)

# projected_reserves

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| projected_reserves | 8 / 2.35 fail | fail | 8 / 3.35 fail | 0 / 0.44 fail |
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
| projected_reserves | 11 / 2.14 fail | fail | 11 / 2.85 fail | 0 / 0.89 fail |
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

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 flat / 2.80 weighted (tier 1 on the flat count) | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 flat / 1.17 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 flat / 1.03 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| projected_reserves | 8 of 26 | 0.308 [0.156, 0.471] | 0.192 | 2.35 flat / 0.82 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 flat / 0.76 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+projected | 11 of 26 | 0.423 [0.240, 0.600] | 0.192 | 2.23 flat / 0.98 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 flat / 0.97 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 1.85 flat / 1.19 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 1.77 flat / 1.16 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.192 | 1.88 flat / 1.25 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

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

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.358 | 6.69 flat / 3.75 weighted (tier 1 on the weighted count) | 2.9 / 4.7 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.380 | 7.04 flat / 3.25 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 flat / 1.73 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| projected_reserves | 11 of 26 | 0.423 [0.238, 0.611] | 0.269 | 4.77 flat / 2.14 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.154 | 1.38 flat / 0.80 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+projected | 13 of 26 | 0.500 [0.308, 0.692] | 0.263 | 4.54 flat / 2.11 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 flat / 0.97 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.192 | 2.42 flat / 1.74 weighted (tier 1 on the weighted count) | 3.2 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.192 | 2.31 flat / 1.65 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.192 | 2.31 flat / 1.62 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

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
| projected_reserves | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

## Onsets only this row warns

projected_reserves warns 11 of 26 onsets; at least one of the five passers warns 16. 2 are warned by projected_reserves and by none of the five passers:

* 2019-06-25 (flagged at h = 1, 2, 3, 4)
* 2019-08-13 (flagged at h = 1, 3, 4)

Warned by a passer and not by projected_reserves: 2019-01-15, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

## Constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 4 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 2 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 3 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 3 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 2 | 0 of 1869 | 1869 |

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

* 2019-05-28 (flagged at h = 3, 4)
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
| 5 | 89 | 0 | 0 | 7 | 2 | 0 of 1869 | 1829 |

## risk_gbm+projected against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.009 [-0.001, 0.020] |
| 2 | 0.010 [-0.001, 0.021] |
| 3 | 0.007 [-0.004, 0.020] |
| 4 | 0.007 [-0.003, 0.019] |
| 5 | 0.005 [-0.006, 0.018] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [-0.001, 0.097] | 0.044 [-0.009, 0.103] | 0.034 [-0.020, 0.093] |
| 2020 | 251 | -0.012 [-0.022, -0.003] | -0.019 [-0.036, -0.003] | -0.016 [-0.030, -0.003] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 2025-26 | 249 | 0.009 [0.001, 0.020] | 0.005 [0.001, 0.010] | 0.006 [0.001, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.005 [-0.001, 0.016] | -0.000 [-0.012, 0.012] | -0.002 [-0.015, 0.010] |
| ordinary | 1603 | 0.010 [-0.002, 0.022] | 0.008 [-0.004, 0.023] | 0.006 [-0.006, 0.020] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.000] |
| 1 | 324 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.001, -0.000] |
| 2 | 41 | 0.038 [-0.002, 0.076] | -0.002 [-0.070, 0.024] | 0.021 [–] |
| 3 | 473 | 0.032 [-0.008, 0.074] | 0.028 [-0.016, 0.077] | 0.020 [-0.024, 0.070] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.048 [-0.150, 0.250] |

## risk_gbm+projected against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.003 [-0.008, 0.003] |
| 2 | -0.002 [-0.008, 0.003] |
| 3 | -0.000 [-0.008, 0.008] |
| 4 | 0.002 [-0.005, 0.010] |
| 5 | -0.001 [-0.008, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.031, 0.019] | 0.006 [-0.027, 0.044] | 0.009 [-0.026, 0.048] |
| 2020 | 251 | -0.005 [-0.017, 0.004] | -0.020 [-0.037, -0.006] | -0.015 [-0.028, -0.004] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [-0.000, 0.000] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | -0.000 [-0.001, -0.000] | 0.000 [-0.003, 0.004] | 0.000 [-0.001, 0.001] |
| 2025-26 | 249 | -0.004 [-0.015, 0.007] | 0.009 [-0.002, 0.024] | -0.003 [-0.015, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.012 [-0.001, 0.024] | 0.015 [-0.001, 0.035] | 0.003 [-0.009, 0.017] |
| ordinary | 1603 | -0.004 [-0.009, 0.001] | -0.002 [-0.009, 0.005] | -0.000 [-0.008, 0.008] |
| quarter_end | 31 | -0.015 [-0.063, 0.026] | -0.010 [-0.073, 0.049] | -0.026 [-0.082, 0.025] |
| tax_date | 89 | 0.002 [-0.032, 0.031] | 0.015 [-0.010, 0.043] | -0.001 [-0.041, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.001] | 0.000 [-0.000, 0.000] |
| 1 | 324 | 0.001 [-0.004, 0.004] | -0.000 [-0.001, -0.000] | -0.000 [-0.001, 0.001] |
| 2 | 41 | -0.011 [-0.048, 0.035] | -0.015 [-0.089, 0.022] | 0.007 [–] |
| 3 | 473 | -0.008 [-0.028, 0.014] | 0.002 [-0.028, 0.033] | -0.003 [-0.033, 0.031] |

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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.200, 0.091] |

## risk_gbm+projected against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.023 [0.014, 0.032] |
| 2 | 0.012 [0.005, 0.020] |
| 3 | 0.011 [0.003, 0.019] |
| 4 | 0.011 [0.004, 0.019] |
| 5 | 0.007 [-0.002, 0.016] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.048 [0.011, 0.088] | 0.008 [-0.030, 0.047] | -0.003 [-0.044, 0.040] |
| 2020 | 251 | 0.027 [0.015, 0.038] | 0.019 [0.002, 0.034] | 0.020 [0.005, 0.033] |
| 2021-23 | 748 | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] | 0.014 [0.012, 0.016] |
| 2024 | 250 | 0.004 [-0.000, 0.007] | 0.004 [-0.000, 0.007] | 0.002 [-0.003, 0.005] |
| 2025-26 | 249 | 0.025 [0.003, 0.055] | 0.007 [-0.004, 0.021] | -0.008 [-0.021, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.060 [0.035, 0.085] | 0.027 [0.012, 0.043] | 0.012 [-0.002, 0.024] |
| ordinary | 1603 | 0.015 [0.006, 0.024] | 0.006 [-0.003, 0.015] | 0.004 [-0.005, 0.014] |
| quarter_end | 31 | 0.116 [0.034, 0.195] | 0.078 [-0.009, 0.167] | 0.063 [-0.023, 0.156] |
| tax_date | 89 | 0.069 [0.041, 0.096] | 0.053 [0.026, 0.080] | 0.026 [-0.017, 0.058] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] | 0.009 [0.007, 0.011] |
| 1 | 324 | 0.030 [0.022, 0.036] | 0.029 [0.022, 0.036] | 0.027 [0.020, 0.033] |
| 2 | 41 | 0.030 [–] | -0.033 [–] | -0.020 [-0.040, 0.011] |
| 3 | 473 | 0.048 [0.014, 0.082] | 0.007 [-0.023, 0.039] | -0.010 [-0.044, 0.024] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.143, 0.250] |

## risk_gbm+projected against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [0.001, 0.015] |
| 2 | 0.002 [-0.005, 0.009] |
| 3 | 0.005 [-0.003, 0.012] |
| 4 | 0.003 [-0.004, 0.011] |
| 5 | -0.001 [-0.010, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.032 [0.003, 0.061] | 0.008 [-0.027, 0.043] | -0.001 [-0.042, 0.038] |
| 2020 | 251 | 0.004 [-0.007, 0.014] | 0.007 [-0.009, 0.021] | 0.003 [-0.012, 0.015] |
| 2021-23 | 748 | 0.001 [0.000, 0.001] | 0.004 [0.003, 0.005] | 0.002 [0.002, 0.003] |
| 2024 | 250 | 0.004 [0.000, 0.009] | 0.004 [0.001, 0.008] | 0.002 [0.000, 0.003] |
| 2025-26 | 249 | -0.001 [-0.025, 0.021] | 0.001 [-0.021, 0.022] | -0.016 [-0.040, 0.003] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.038 [0.015, 0.062] | 0.017 [0.000, 0.034] | 0.002 [-0.014, 0.017] |
| ordinary | 1603 | 0.002 [-0.004, 0.009] | 0.002 [-0.006, 0.009] | -0.002 [-0.011, 0.007] |
| quarter_end | 31 | 0.055 [-0.016, 0.132] | 0.044 [-0.013, 0.101] | 0.038 [-0.016, 0.092] |
| tax_date | 89 | 0.033 [-0.001, 0.069] | 0.026 [-0.006, 0.062] | 0.000 [-0.044, 0.045] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.002] | 0.003 [0.002, 0.004] | 0.002 [0.001, 0.002] |
| 1 | 324 | 0.009 [0.006, 0.012] | 0.019 [0.015, 0.023] | 0.014 [0.010, 0.017] |
| 2 | 41 | -0.059 [–] | -0.079 [–] | -0.096 [-0.163, -0.017] |
| 3 | 473 | 0.027 [0.003, 0.053] | 0.007 [-0.023, 0.036] | -0.008 [-0.040, 0.023] |

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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.091, 0.211] |


## Onsets warned at each horizon (weighted rule, 26 onsets)

The ceiling: 12 of 26 onsets at any single horizon of 2 or more, the risk-date passers' best (docs/pivot/desk-standard.md section 4): the recall of each row at h = 2 to 5 is reported against it.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| projected_reserves | 11 | 8 | 9 | 9 | 6 |
| risk_gbm+projected | 12 | 11 | 11 | 11 | 9 |
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
| projected_reserves | 0.0539 / 0.1793 | 0.0588 / 0.1934 | 0.0617 / 0.2056 | 0.0613 / 0.2036 | 0.0639 / 0.2161 |
| risk_gbm+projected | 0.0488 / 0.1720 | 0.0590 / 0.1980 | 0.0597 / 0.2002 | 0.0594 / 0.2017 | 0.0642 / 0.2233 |
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
| 3 | 384 | -36.6 | 71.0 | 129.8 | -5.7 | 86.5 | 121.8 |
| 4 | 384 | -50.6 | 80.8 | 138.9 | -5.7 | 86.5 | 121.8 |
| 5 | 384 | -40.2 | 84.5 | 138.8 | -5.5 | 86.7 | 121.9 |

By calendar year (MAE, projected / carried forward):

| h | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| 1 | 19 / 27 | 24 / 31 | 104 / 64 | 61 / 59 | 40 / 61 | 46 / 71 | 37 / 62 | 49 / 47 |
| 2 | 23 / 38 | 37 / 48 | 170 / 118 | 78 / 96 | 58 / 102 | 62 / 101 | 47 / 84 | 48 / 78 |
| 3 | 21 / 38 | 40 / 48 | 181 / 118 | 91 / 96 | 50 / 102 | 54 / 101 | 55 / 84 | 50 / 78 |
| 4 | 25 / 38 | 48 / 48 | 200 / 118 | 99 / 96 | 52 / 102 | 63 / 101 | 63 / 84 | 67 / 78 |
| 5 | 32 / 38 | 53 / 48 | 203 / 118 | 88 / 96 | 60 / 102 | 73 / 101 | 70 / 84 | 69 / 78 |
