# The structural liquidity model (#542)

> **Correction of 11 October 2026 (#578).** This page was re-scored after the audit's construction fixes: net settlement subtracted the coupon maturities twice when Notes and Bonds settled together (#566), and at h = 1 the model read the decision day's settlement, not the scored day's (#568). Every figure below is the re-score; the first scoring of 11 October is in git history and in the before columns of the linked page. The before-and-after figures are in [`audit-fixes-578-result.md`](../../audit-fixes-578-result.md).

# structural_liquidity

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| structural_liquidity | 10 / 1.42 fail | fail | 10 / 2.42 fail | 0 / 0.33 fail |
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
| structural_liquidity | 11 / 1.00 fail | fail | 11 / 1.69 fail | 0 / 0.83 fail |
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
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 flat / 0.76 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+structural | 10 of 26 | 0.385 [0.212, 0.563] | 0.192 | 2.08 flat / 0.86 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 flat / 0.97 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 1.85 flat / 1.19 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 1.77 flat / 1.16 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.192 | 1.88 flat / 1.25 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| structural_liquidity | 10 of 26 | 0.385 [0.217, 0.552] | 0.154 | 1.42 flat / 0.57 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+structural | 0.40 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.59 (17) | 0.33 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| structural_liquidity | 0.49 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.53 (17) | 0.33 (101) | 0.44 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+structural | +0.0396 [+0.0046, +0.0778] | +0.0286 [+0.0173, +0.0391] | +0.0133 [+0.0116, +0.0152] | +0.0027 [-0.0023, +0.0064] | +0.0290 [+0.0031, +0.0593] | +0.0569 [+0.0330, +0.0829] | +0.0135 [+0.0056, +0.0225] | +0.1155 [+0.0311, +0.1957] | +0.0686 [+0.0416, +0.0951] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| structural_liquidity | +0.0321 [-0.0050, +0.0708] | +0.0268 [+0.0160, +0.0373] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0041, +0.0049] | +0.0231 [+0.0027, +0.0495] | +0.0390 [+0.0091, +0.0702] | +0.0123 [+0.0044, +0.0208] | +0.1343 [+0.0762, +0.1967] | +0.0557 [+0.0113, +0.0996] |


## The judge's tables under the weighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.358 | 6.69 flat / 3.75 weighted (tier 1 on the weighted count) | 2.9 / 4.7 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.380 | 7.04 flat / 3.25 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 flat / 1.73 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.154 | 1.38 flat / 0.80 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+structural | 11 of 26 | 0.423 [0.241, 0.609] | 0.231 | 3.38 flat / 1.63 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 flat / 0.97 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.192 | 2.42 flat / 1.74 weighted (tier 1 on the weighted count) | 3.2 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.192 | 2.31 flat / 1.65 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.192 | 2.31 flat / 1.62 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| structural_liquidity | 11 of 26 | 0.423 [0.250, 0.613] | 0.231 | 2.54 flat / 1.00 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+structural | 0.40 (102) | 0.25 (4) | – | 0.00 (5) | 0.45 (29) | 0.59 (17) | 0.36 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |
| structural_liquidity | 0.54 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.76 (17) | 0.40 (101) | 0.44 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+structural | +0.0396 [+0.0046, +0.0778] | +0.0286 [+0.0173, +0.0391] | +0.0133 [+0.0116, +0.0152] | +0.0027 [-0.0023, +0.0064] | +0.0290 [+0.0031, +0.0593] | +0.0569 [+0.0330, +0.0829] | +0.0135 [+0.0056, +0.0225] | +0.1155 [+0.0311, +0.1957] | +0.0686 [+0.0416, +0.0951] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |
| structural_liquidity | +0.0321 [-0.0050, +0.0708] | +0.0268 [+0.0160, +0.0373] | +0.0133 [+0.0116, +0.0152] | +0.0009 [-0.0041, +0.0049] | +0.0231 [+0.0027, +0.0495] | +0.0390 [+0.0091, +0.0702] | +0.0123 [+0.0044, +0.0208] | +0.1343 [+0.0762, +0.1967] | +0.0557 [+0.0113, +0.0996] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| structural_liquidity | 0 of 4 | 11 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

## Onsets only this row warns

structural_liquidity warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by structural_liquidity and by none of the five passers:

* 2019-08-13 (flagged at h = 1, 2, 3)

Warned by a passer and not by structural_liquidity: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

## Constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 1 | 0 | 6 | 0 | 0 of 1873 | 1127 |
| 2 | 90 | 1 | 0 | 6 | 1 | 0 of 1872 | 1249 |
| 3 | 90 | 1 | 0 | 6 | 0 | 0 of 1871 | 1235 |
| 4 | 90 | 2 | 0 | 6 | 0 | 0 of 1870 | 1233 |
| 5 | 89 | 0 | 0 | 7 | 0 | 0 of 1869 | 1252 |

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


# risk_gbm+structural

## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| risk_gbm+structural | 0 of 4 | 9 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

## Onsets only this row warns

risk_gbm+structural warns 11 of 26 onsets; at least one of the five passers warns 16. 1 are warned by risk_gbm+structural and by none of the five passers:

* 2019-08-13 (flagged at h = 2, 3)

Warned by a passer and not by risk_gbm+structural: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

## Constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 0 | 0 of 1873 | 1215 |
| 2 | 90 | 1 | 0 | 6 | 1 | 0 of 1872 | 1247 |
| 3 | 90 | 1 | 0 | 6 | 0 | 0 of 1871 | 1234 |
| 4 | 90 | 2 | 0 | 7 | 0 | 0 of 1870 | 1242 |
| 5 | 89 | 0 | 0 | 8 | 0 | 0 of 1869 | 1257 |

## risk_gbm+structural against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [-0.000, 0.017] |
| 2 | 0.004 [-0.007, 0.016] |
| 3 | 0.002 [-0.011, 0.014] |
| 4 | -0.000 [-0.012, 0.011] |
| 5 | -0.003 [-0.015, 0.010] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.038 [-0.000, 0.080] | 0.014 [-0.050, 0.074] | -0.012 [-0.074, 0.054] |
| 2020 | 251 | -0.011 [-0.017, -0.006] | -0.013 [-0.021, -0.005] | -0.010 [-0.017, -0.004] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.002, -0.002] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.013 [-0.001, 0.033] | 0.010 [-0.000, 0.022] | 0.011 [-0.001, 0.026] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.003 [-0.002, 0.008] | -0.002 [-0.016, 0.010] | -0.003 [-0.013, 0.003] |
| ordinary | 1603 | 0.009 [-0.000, 0.020] | 0.002 [-0.013, 0.016] | -0.003 [-0.018, 0.012] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, -0.000] | -0.001 [-0.001, -0.001] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.004 [-0.005, -0.003] | -0.008 [-0.010, -0.007] | -0.006 [-0.007, -0.004] |
| 2 | 41 | 0.065 [–] | 0.042 [–] | 0.063 [–] |
| 3 | 473 | 0.028 [-0.002, 0.063] | 0.011 [-0.039, 0.059] | -0.012 [-0.062, 0.040] |

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

## risk_gbm+structural against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.004 [-0.009, 0.001] |
| 2 | -0.008 [-0.016, -0.000] |
| 3 | -0.006 [-0.016, 0.004] |
| 4 | -0.005 [-0.016, 0.004] |
| 5 | -0.009 [-0.017, -0.001] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.015 [-0.041, 0.012] | -0.024 [-0.076, 0.025] | -0.037 [-0.075, 0.001] |
| 2020 | 251 | -0.004 [-0.011, 0.001] | -0.014 [-0.019, -0.010] | -0.009 [-0.014, -0.005] |
| 2021-23 | 748 | -0.000 [-0.001, -0.000] | -0.002 [-0.002, -0.001] | -0.001 [-0.001, -0.001] |
| 2024 | 250 | -0.001 [-0.003, -0.000] | -0.000 [-0.004, 0.003] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.000 [-0.012, 0.014] | 0.014 [-0.002, 0.032] | 0.002 [-0.016, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.009 [-0.003, 0.022] | 0.013 [-0.006, 0.034] | 0.002 [-0.012, 0.017] |
| ordinary | 1603 | -0.005 [-0.011, 0.000] | -0.008 [-0.020, 0.002] | -0.010 [-0.019, -0.002] |
| quarter_end | 31 | -0.015 [-0.063, 0.029] | -0.010 [-0.075, 0.052] | -0.026 [-0.083, 0.027] |
| tax_date | 89 | 0.002 [-0.030, 0.031] | 0.015 [-0.011, 0.042] | -0.001 [-0.042, 0.038] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.001 [-0.003, -0.000] | -0.001 [-0.001, -0.000] |
| 1 | 324 | -0.003 [-0.007, -0.000] | -0.009 [-0.010, -0.007] | -0.005 [-0.007, -0.004] |
| 2 | 41 | 0.016 [–] | 0.029 [–] | 0.049 [–] |
| 3 | 473 | -0.012 [-0.032, 0.009] | -0.016 [-0.057, 0.024] | -0.034 [-0.065, -0.004] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.231 [-0.417, -0.048] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.400, 0.053] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.250 [-0.571, 0.003] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.143 [-0.320, 0.042] |

## risk_gbm+structural against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.021 [0.013, 0.030] |
| 2 | 0.006 [-0.003, 0.015] |
| 3 | 0.006 [-0.005, 0.016] |
| 4 | 0.004 [-0.007, 0.014] |
| 5 | -0.002 [-0.014, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.040 [0.004, 0.078] | -0.022 [-0.075, 0.030] | -0.050 [-0.104, -0.002] |
| 2020 | 251 | 0.029 [0.018, 0.039] | 0.025 [0.016, 0.033] | 0.026 [0.018, 0.034] |
| 2021-23 | 748 | 0.013 [0.012, 0.015] | 0.012 [0.010, 0.013] | 0.013 [0.011, 0.015] |
| 2024 | 250 | 0.003 [-0.002, 0.006] | 0.003 [-0.000, 0.006] | 0.001 [-0.003, 0.005] |
| 2025-26 | 249 | 0.029 [0.003, 0.061] | 0.011 [-0.000, 0.026] | -0.004 [-0.021, 0.008] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.057 [0.032, 0.084] | 0.025 [0.007, 0.044] | 0.011 [-0.001, 0.020] |
| ordinary | 1603 | 0.014 [0.006, 0.022] | -0.000 [-0.013, 0.011] | -0.005 [-0.019, 0.006] |
| quarter_end | 31 | 0.116 [0.034, 0.196] | 0.078 [-0.010, 0.160] | 0.063 [-0.024, 0.149] |
| tax_date | 89 | 0.069 [0.042, 0.096] | 0.053 [0.025, 0.081] | 0.026 [-0.016, 0.060] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.008 [0.006, 0.010] | 0.008 [0.006, 0.009] | 0.008 [0.007, 0.010] |
| 1 | 324 | 0.025 [0.019, 0.032] | 0.021 [0.015, 0.026] | 0.022 [0.016, 0.027] |
| 2 | 41 | 0.057 [–] | 0.011 [–] | 0.022 [–] |
| 3 | 473 | 0.044 [0.014, 0.077] | -0.010 [-0.051, 0.031] | -0.042 [-0.087, -0.004] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.222, 0.158] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.176 [-0.400, 0.048] |
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
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.280, 0.194] |

## risk_gbm+structural against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.006 [0.000, 0.013] |
| 2 | -0.004 [-0.013, 0.005] |
| 3 | -0.001 [-0.012, 0.009] |
| 4 | -0.005 [-0.015, 0.005] |
| 5 | -0.009 [-0.020, -0.000] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.023 [-0.006, 0.052] | -0.022 [-0.073, 0.026] | -0.047 [-0.093, -0.004] |
| 2020 | 251 | 0.005 [-0.001, 0.010] | 0.013 [0.009, 0.016] | 0.008 [0.003, 0.012] |
| 2021-23 | 748 | 0.000 [0.000, 0.001] | 0.002 [0.002, 0.003] | 0.001 [0.001, 0.002] |
| 2024 | 250 | 0.003 [0.000, 0.007] | 0.003 [0.001, 0.008] | 0.001 [0.000, 0.003] |
| 2025-26 | 249 | 0.003 [-0.014, 0.021] | 0.005 [-0.011, 0.024] | -0.011 [-0.027, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.036 [0.012, 0.061] | 0.015 [-0.003, 0.034] | 0.001 [-0.013, 0.016] |
| ordinary | 1603 | 0.001 [-0.004, 0.007] | -0.005 [-0.016, 0.006] | -0.011 [-0.023, -0.002] |
| quarter_end | 31 | 0.055 [-0.017, 0.129] | 0.044 [-0.013, 0.105] | 0.038 [-0.018, 0.097] |
| tax_date | 89 | 0.033 [-0.002, 0.067] | 0.026 [-0.006, 0.061] | 0.000 [-0.046, 0.041] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | 0.002 [0.000, 0.003] | 0.001 [0.001, 0.001] |
| 1 | 324 | 0.005 [0.003, 0.007] | 0.011 [0.008, 0.013] | 0.008 [0.006, 0.011] |
| 2 | 41 | -0.033 [-0.095, 0.032] | -0.035 [-0.076, 0.013] | -0.054 [-0.097, -0.004] |
| 3 | 473 | 0.024 [0.000, 0.048] | -0.011 [-0.053, 0.028] | -0.039 [-0.077, -0.005] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.185, 0.125] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.118 [-0.267, 0.000] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.167 [-0.417, 0.111] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | -0.048 [-0.235, 0.160] |


## Fitted coefficients by refit (+5 bp, in the columns' own units)

Positive is the sign the mechanism says for every coefficient but the intercept. `standardized` is the last refit's, on standardized columns (comparable across terms).

h = 1: 90 refits with both classes of the label, of 90.

| coefficient | first refit | median | last refit | min | max | refits positive | standardized (last) |
|---|---|---|---|---|---|---|---|
| intercept | -3.808 | -2.663 | -2.686 | -4.509 | -1.75 | 0% | -3.390 |
| spread_bps | -0.0192 | 0.1431 | 0.1796 | -0.08098 | 0.1803 | 94% | 1.854 |
| e_x_shortfall | 0.07788 | 0.004152 | 0.004286 | 0.003068 | 0.07788 | 100% | 0.604 |
| e_x_tga_up | -0.01694 | 5.716e-05 | -5.588e-05 | -0.01694 | 0.02932 | 97% | -0.018 |
| e_x_tax_date | -1.747 | 0.1084 | 0.105 | -1.747 | 0.8037 | 93% | 0.198 |
| e_x_window | 2.16 | 0.01538 | 0.01378 | -0.09222 | 2.16 | 96% | 0.042 |

h = 2: 90 refits with both classes of the label, of 90.

| coefficient | first refit | median | last refit | min | max | refits positive | standardized (last) |
|---|---|---|---|---|---|---|---|
| intercept | -4.054 | -2.628 | -2.655 | -4.692 | -1.613 | 0% | -3.191 |
| spread_bps | 0.1113 | 0.1106 | 0.1434 | -0.1247 | 0.1455 | 96% | 1.480 |
| e_x_shortfall | 0.06171 | 0.0009746 | 0.001004 | 0.0005191 | 0.06171 | 100% | 0.353 |
| e_x_tga_up | -0.01942 | -4.451e-05 | -0.0001814 | -0.01942 | 0.02911 | 40% | -0.060 |
| e_x_tax_date | -0.7761 | 0.1227 | 0.1228 | -0.9344 | 0.8433 | 93% | 0.231 |
| e_x_window | 2.048 | 0.03233 | 0.03109 | -0.07646 | 2.048 | 98% | 0.094 |

h = 3: 90 refits with both classes of the label, of 90.

| coefficient | first refit | median | last refit | min | max | refits positive | standardized (last) |
|---|---|---|---|---|---|---|---|
| intercept | -3.737 | -2.689 | -2.705 | -4.603 | -1.543 | 0% | -2.981 |
| spread_bps | 0.2073 | 0.05803 | 0.09273 | -0.07822 | 0.2073 | 96% | 0.957 |
| e_x_shortfall | 0.06062 | 0.001231 | 0.001274 | 0.0006454 | 0.06062 | 100% | 0.448 |
| e_x_tga_up | -0.02019 | 8.283e-05 | -0.0001314 | -0.02019 | 0.03076 | 93% | -0.044 |
| e_x_tax_date | -0.7404 | 0.1159 | 0.1146 | -0.7725 | 0.818 | 93% | 0.217 |
| e_x_window | 2.343 | 0.03339 | 0.03016 | 0.01622 | 2.545 | 100% | 0.087 |

h = 4: 90 refits with both classes of the label, of 90.

| coefficient | first refit | median | last refit | min | max | refits positive | standardized (last) |
|---|---|---|---|---|---|---|---|
| intercept | -3.936 | -2.698 | -2.701 | -4.484 | -1.683 | 0% | -3.157 |
| spread_bps | 0.06692 | 0.1004 | 0.1287 | -0.09361 | 0.1309 | 94% | 1.329 |
| e_x_shortfall | 0.06074 | 0.001383 | 0.001392 | 0.0008705 | 0.06341 | 100% | 0.490 |
| e_x_tga_up | -0.02116 | -0.0004236 | -0.0005911 | -0.02116 | 0.01461 | 13% | -0.196 |
| e_x_tax_date | -1.251 | 0.111 | 0.1096 | -1.251 | 0.7957 | 93% | 0.207 |
| e_x_window | 1.758 | 0.04442 | 0.0427 | 0.02146 | 3.263 | 100% | 0.121 |

h = 5: 89 refits with both classes of the label, of 89.

| coefficient | first refit | median | last refit | min | max | refits positive | standardized (last) |
|---|---|---|---|---|---|---|---|
| intercept | -5.955 | -2.724 | -2.763 | -5.955 | -1.697 | 0% | -3.223 |
| spread_bps | -0.2678 | 0.09246 | 0.1284 | -0.3442 | 0.1284 | 89% | 1.321 |
| e_x_shortfall | 0.08093 | 0.001365 | 0.001378 | 0.0001388 | 0.08093 | 100% | 0.488 |
| e_x_tga_up | -0.01567 | -0.0003796 | -0.0005376 | -0.02932 | 0.003409 | 9% | -0.179 |
| e_x_tax_date | -1.323 | 0.1144 | 0.1125 | -1.655 | 0.8136 | 93% | 0.214 |
| e_x_window | 1.068 | 0.06577 | 0.06436 | 0.03691 | 2.452 | 100% | 0.176 |
