# The latent funding-stress factor (#543)

## Tier 1 under unweighted

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| latent_factor | 12 / 5.73 fail | fail | 12 / 6.35 fail | 0 / 0.78 fail |
| latent_factor_resid | 12 / 5.73 fail | fail | 12 / 6.31 fail | 0 / 0.78 fail |
| latent_factor_logit | 9 / 3.73 fail | fail | 9 / 6.19 fail | 1 / 2.00 fail |
| risk_gbm+latent_factor | 12 / 3.81 fail | fail | 12 / 5.27 fail | 2 / 0.44 fail |
| risk_gbm+latent_factor_resid | 12 / 3.77 fail | fail | 12 / 5.19 fail | 2 / 0.44 fail |
| risk_gbm+latent_factor_logit | 15 / 2.77 fail | fail | 15 / 5.31 fail | 2 / 2.00 fail |
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
| latent_factor | 13 / 3.65 fail | fail | 13 / 3.82 fail | 0 / 3.11 fail |
| latent_factor_resid | 13 / 3.25 fail | fail | 13 / 3.36 fail | 0 / 1.92 fail |
| latent_factor_logit | 12 / 2.92 fail | fail | 12 / 3.72 fail | 1 / 2.28 fail |
| risk_gbm+latent_factor | 15 / 3.20 fail | pass (h = 1) | 15 / 3.98 fail | 2 / 3.00 fail |
| risk_gbm+latent_factor_resid | 15 / 3.18 fail | pass (h = 1) | 15 / 4.02 fail | 2 / 3.00 fail |
| risk_gbm+latent_factor_logit | 17 / 2.29 fail | fail | 17 / 3.52 fail | 4 / 1.58 fail |
| risk_gbm | 13 / 0.80 pass | pass (h = 1) | 13 / 1.48 pass | 3 / 1.61 fail |
| risk_gbm_base | 14 / 0.97 pass | pass (h = 1) | 14 / 1.59 pass | 4 / 2.06 fail |
| risk_logistic | 16 / 1.74 pass | pass (h = 1) | 16 / 2.55 fail | 6 / 4.39 fail |
| risk_logistic_base | 15 / 1.65 pass | pass (h = 1) | 15 / 2.18 fail | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass (h = 1) | 15 / 2.14 fail | 5 / 3.81 fail |
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 5 / 0.50 fail |
| calendar_climatology | 12 / 3.75 fail | fail | 12 / 3.90 fail | 0 / 4.56 fail |
| persistence_logistic | 12 / 3.25 fail | fail | 12 / 4.09 fail | 1 / 2.86 fail |

## Tier 1 under weighted/before_only

| row | (a) as declared | (b1) best horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| latent_factor | 12 / 3.95 fail | fail | 12 / 4.27 fail | 0 / 0.78 fail |
| latent_factor_resid | 12 / 3.95 fail | fail | 12 / 4.27 fail | 0 / 0.78 fail |
| latent_factor_logit | 11 / 3.37 fail | fail | 11 / 4.49 fail | 1 / 1.64 fail |
| risk_gbm+latent_factor | 13 / 3.46 fail | fail | 13 / 4.12 fail | 2 / 1.00 fail |
| risk_gbm+latent_factor_resid | 13 / 3.42 fail | fail | 13 / 4.01 fail | 2 / 1.00 fail |
| risk_gbm+latent_factor_logit | 17 / 2.94 fail | fail | 17 / 4.37 fail | 4 / 2.19 fail |
| risk_gbm | 13 / 0.95 pass | pass (h = 1) | 13 / 1.64 pass | 3 / 1.78 fail |
| risk_gbm_base | 14 / 1.08 pass | pass (h = 1) | 14 / 1.72 pass | 4 / 2.22 fail |
| risk_logistic | 16 / 1.90 pass | pass (h = 1) | 16 / 2.70 fail | 6 / 4.31 fail |
| risk_logistic_base | 14 / 1.78 pass | pass (h = 1) | 14 / 2.26 fail | 4 / 3.58 fail |
| risk_quantile_skewt_base | 15 / 1.81 pass | pass (h = 1) | 15 / 2.22 fail | 5 / 4.14 fail |
| ngboost_laplace | 16 / 2.23 fail | pass (h = 1) | 16 / 3.30 fail | 5 / 0.58 fail |
| calendar_climatology | 12 / 4.55 fail | fail | 12 / 4.70 fail | 0 / 4.44 fail |
| persistence_logistic | 10 / 3.23 fail | fail | 10 / 4.50 fail | 1 / 1.75 fail |

## The judge's tables under the unweighted rule

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 flat / 2.80 weighted (tier 1 on the flat count) | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 flat / 1.17 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor | 12 of 26 | 0.462 [0.286, 0.652] | 0.269 | 5.73 flat / 2.69 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor_logit | 9 of 26 | 0.346 [0.174, 0.519] | 0.231 | 3.73 flat / 1.60 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor_resid | 12 of 26 | 0.462 [0.269, 0.643] | 0.269 | 5.73 flat / 2.69 weighted (tier 1 on the flat count) | 0.0 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 flat / 1.03 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 flat / 0.76 weighted (tier 1 on the flat count) | 1.2 / 0.3 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+latent_factor | 12 of 26 | 0.462 [0.278, 0.667] | 0.231 | 3.81 flat / 1.68 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+latent_factor_logit | 15 of 26 | 0.577 [0.385, 0.769] | 0.231 | 2.77 flat / 1.03 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+latent_factor_resid | 12 of 26 | 0.462 [0.273, 0.667] | 0.231 | 3.77 flat / 1.66 weighted (tier 1 on the flat count) | 0.2 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 flat / 0.97 weighted (tier 1 on the flat count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 0.192 | 1.85 flat / 1.19 weighted (tier 1 on the flat count) | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 0.192 | 1.77 flat / 1.16 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 0.192 | 1.88 flat / 1.25 weighted (tier 1 on the flat count) | 0.7 / 0.0 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| latent_factor | 0.05 (102) | 0.25 (4) | – | 0.00 (5) | 0.00 (29) | 0.12 (17) | 0.04 (101) | 0.00 (9) | 0.00 (13) |
| latent_factor_logit | 0.48 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.47 (17) | 0.49 (101) | 0.44 (9) | 0.31 (13) |
| latent_factor_resid | 0.05 (102) | 0.25 (4) | – | 0.00 (5) | 0.00 (29) | 0.12 (17) | 0.04 (101) | 0.00 (9) | 0.00 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+latent_factor | 0.31 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.22 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+latent_factor_logit | 0.46 (102) | 0.25 (4) | – | 0.00 (5) | 0.34 (29) | 0.71 (17) | 0.35 (101) | 0.44 (9) | 0.54 (13) |
| risk_gbm+latent_factor_resid | 0.31 (102) | 0.25 (4) | – | 0.00 (5) | 0.28 (29) | 0.59 (17) | 0.22 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.16 (101) | 0.56 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.76 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.76 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| latent_factor | +0.0269 [-0.0093, +0.0659] | -0.1132 [-0.1233, -0.1027] | -0.0445 [-0.0516, -0.0379] | -0.0171 [-0.0194, -0.0138] | +0.0130 [-0.0099, +0.0423] | -0.0204 [-0.0378, -0.0007] | -0.0325 [-0.0446, -0.0199] | +0.0404 [-0.0399, +0.1262] | +0.0142 [-0.0004, +0.0316] |
| latent_factor_logit | +0.0177 [-0.0019, +0.0407] | +0.0229 [+0.0126, +0.0322] | +0.0128 [+0.0112, +0.0145] | +0.0021 [-0.0011, +0.0047] | +0.0253 [+0.0022, +0.0567] | +0.0202 [+0.0030, +0.0412] | +0.0129 [+0.0080, +0.0191] | +0.0651 [-0.0317, +0.1711] | +0.0343 [+0.0097, +0.0566] |
| latent_factor_resid | +0.0276 [-0.0102, +0.0689] | -0.1134 [-0.1227, -0.1021] | -0.0449 [-0.0524, -0.0384] | -0.0175 [-0.0199, -0.0140] | +0.0128 [-0.0113, +0.0451] | -0.0201 [-0.0383, -0.0005] | -0.0327 [-0.0448, -0.0199] | +0.0419 [-0.0334, +0.1250] | +0.0148 [-0.0016, +0.0338] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+latent_factor | +0.0483 [+0.0053, +0.0942] | -0.0799 [-0.0943, -0.0651] | -0.0323 [-0.0384, -0.0267] | -0.0133 [-0.0165, -0.0095] | +0.0222 [-0.0082, +0.0580] | +0.0537 [+0.0272, +0.0809] | -0.0260 [-0.0391, -0.0125] | +0.1155 [+0.0352, +0.1937] | +0.0686 [+0.0400, +0.0954] |
| risk_gbm+latent_factor_logit | +0.0532 [+0.0269, +0.0804] | +0.0243 [+0.0138, +0.0347] | +0.0129 [+0.0113, +0.0147] | +0.0033 [-0.0005, +0.0061] | +0.0295 [+0.0021, +0.0640] | +0.0592 [+0.0349, +0.0861] | +0.0158 [+0.0094, +0.0229] | +0.1155 [+0.0285, +0.1939] | +0.0686 [+0.0429, +0.0951] |
| risk_gbm+latent_factor_resid | +0.0483 [+0.0048, +0.0925] | -0.0801 [-0.0952, -0.0645] | -0.0326 [-0.0388, -0.0271] | -0.0136 [-0.0168, -0.0096] | +0.0219 [-0.0095, +0.0613] | +0.0537 [+0.0266, +0.0818] | -0.0263 [-0.0385, -0.0134] | +0.1155 [+0.0353, +0.1963] | +0.0686 [+0.0405, +0.0934] |
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
| latent_factor | 13 of 26 | 0.500 [0.314, 0.700] | 0.418 | 6.96 flat / 3.65 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor_logit | 12 of 26 | 0.462 [0.267, 0.654] | 0.334 | 6.27 flat / 2.92 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| latent_factor_resid | 13 of 26 | 0.500 [0.300, 0.684] | 0.386 | 6.81 flat / 3.25 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 flat / 1.73 weighted (tier 1 on the weighted count) | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.154 | 1.38 flat / 0.80 weighted (tier 1 on the weighted count) | 1.5 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_gbm+latent_factor | 15 of 26 | 0.577 [0.375, 0.762] | 0.308 | 6.12 flat / 3.20 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm+latent_factor_logit | 17 of 26 | 0.654 [0.476, 0.821] | 0.269 | 5.15 flat / 2.29 weighted (tier 1 on the weighted count) | 0.7 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| risk_gbm+latent_factor_resid | 15 of 26 | 0.577 [0.382, 0.778] | 0.306 | 6.08 flat / 3.18 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 4 | no, no | fail (tiers no / no / no) | fail (no / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 flat / 0.97 weighted (tier 1 on the weighted count) | 0.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.192 | 2.42 flat / 1.74 weighted (tier 1 on the weighted count) | 3.2 / 0.7 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.192 | 2.31 flat / 1.65 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 2 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.192 | 2.31 flat / 1.62 weighted (tier 1 on the weighted count) | 1.0 / 0.7 | 1 of 4 | no, yes | fail (tiers yes / no / no) | fail (yes / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| latent_factor | 0.86 (102) | 0.25 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.68 (101) | 0.33 (9) | 0.62 (13) |
| latent_factor_logit | 0.81 (102) | 0.50 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.76 (101) | 0.56 (9) | 0.54 (13) |
| latent_factor_resid | 0.86 (102) | 0.25 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.68 (101) | 0.33 (9) | 0.62 (13) |
| ngboost_laplace | 0.61 (102) | 0.25 (4) | – | 0.20 (5) | 0.38 (29) | 0.71 (17) | 0.49 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.71 (17) | 0.15 (101) | 0.67 (9) | 0.69 (13) |
| risk_gbm+latent_factor | 0.64 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.53 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm+latent_factor_logit | 0.80 (102) | 0.25 (4) | – | 0.20 (5) | 0.55 (29) | 0.82 (17) | 0.71 (101) | 0.67 (9) | 0.62 (13) |
| risk_gbm+latent_factor_resid | 0.64 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.53 (101) | 0.44 (9) | 0.38 (13) |
| risk_gbm_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.71 (17) | 0.16 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_logistic_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.45 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.69 (13) |
| risk_quantile_skewt_base | 0.30 (102) | 0.25 (4) | – | 0.20 (5) | 0.48 (29) | 0.76 (17) | 0.18 (101) | 0.67 (9) | 0.77 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| latent_factor | +0.0269 [-0.0093, +0.0659] | -0.1132 [-0.1233, -0.1027] | -0.0445 [-0.0516, -0.0379] | -0.0171 [-0.0194, -0.0138] | +0.0130 [-0.0099, +0.0423] | -0.0204 [-0.0378, -0.0007] | -0.0325 [-0.0446, -0.0199] | +0.0404 [-0.0399, +0.1262] | +0.0142 [-0.0004, +0.0316] |
| latent_factor_logit | +0.0177 [-0.0019, +0.0407] | +0.0229 [+0.0126, +0.0322] | +0.0128 [+0.0112, +0.0145] | +0.0021 [-0.0011, +0.0047] | +0.0253 [+0.0022, +0.0567] | +0.0202 [+0.0030, +0.0412] | +0.0129 [+0.0080, +0.0191] | +0.0651 [-0.0317, +0.1711] | +0.0343 [+0.0097, +0.0566] |
| latent_factor_resid | +0.0276 [-0.0102, +0.0689] | -0.1134 [-0.1227, -0.1021] | -0.0449 [-0.0524, -0.0384] | -0.0175 [-0.0199, -0.0140] | +0.0128 [-0.0113, +0.0451] | -0.0201 [-0.0383, -0.0005] | -0.0327 [-0.0448, -0.0199] | +0.0419 [-0.0334, +0.1250] | +0.0148 [-0.0016, +0.0338] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| risk_gbm | +0.0016 [-0.0200, +0.0242] | +0.0396 [+0.0307, +0.0483] | +0.0138 [+0.0120, +0.0155] | +0.0037 [-0.0002, +0.0067] | +0.0155 [-0.0024, +0.0394] | +0.0543 [+0.0303, +0.0787] | +0.0049 [-0.0002, +0.0099] | +0.1155 [+0.0314, +0.2020] | +0.0686 [+0.0412, +0.0953] |
| risk_gbm+latent_factor | +0.0483 [+0.0053, +0.0942] | -0.0799 [-0.0943, -0.0651] | -0.0323 [-0.0384, -0.0267] | -0.0133 [-0.0165, -0.0095] | +0.0222 [-0.0082, +0.0580] | +0.0537 [+0.0272, +0.0809] | -0.0260 [-0.0391, -0.0125] | +0.1155 [+0.0352, +0.1937] | +0.0686 [+0.0400, +0.0954] |
| risk_gbm+latent_factor_logit | +0.0532 [+0.0269, +0.0804] | +0.0243 [+0.0138, +0.0347] | +0.0129 [+0.0113, +0.0147] | +0.0033 [-0.0005, +0.0061] | +0.0295 [+0.0021, +0.0640] | +0.0592 [+0.0349, +0.0861] | +0.0158 [+0.0094, +0.0229] | +0.1155 [+0.0285, +0.1939] | +0.0686 [+0.0429, +0.0951] |
| risk_gbm+latent_factor_resid | +0.0483 [+0.0048, +0.0925] | -0.0801 [-0.0952, -0.0645] | -0.0326 [-0.0388, -0.0271] | -0.0136 [-0.0168, -0.0096] | +0.0219 [-0.0095, +0.0613] | +0.0537 [+0.0266, +0.0818] | -0.0263 [-0.0385, -0.0134] | +0.1155 [+0.0353, +0.1963] | +0.0686 [+0.0405, +0.0934] |
| risk_gbm_base | -0.0015 [-0.0206, +0.0159] | +0.0329 [+0.0223, +0.0434] | +0.0138 [+0.0121, +0.0156] | +0.0038 [+0.0001, +0.0070] | +0.0158 [+0.0016, +0.0330] | +0.0339 [+0.0115, +0.0566] | +0.0052 [+0.0001, +0.0097] | +0.1101 [+0.0294, +0.1928] | +0.0681 [+0.0463, +0.0927] |
| risk_logistic | -0.0026 [-0.0240, +0.0179] | +0.0252 [+0.0095, +0.0381] | +0.0138 [+0.0120, +0.0157] | +0.0050 [+0.0008, +0.0096] | +0.0133 [+0.0003, +0.0294] | +0.0282 [+0.0011, +0.0563] | +0.0040 [-0.0012, +0.0088] | +0.0892 [+0.0158, +0.1596] | +0.0774 [+0.0463, +0.1124] |
| risk_logistic_base | -0.0024 [-0.0224, +0.0166] | +0.0298 [+0.0202, +0.0383] | +0.0138 [+0.0120, +0.0157] | +0.0040 [+0.0003, +0.0070] | +0.0168 [+0.0040, +0.0338] | +0.0352 [+0.0096, +0.0600] | +0.0047 [-0.0004, +0.0092] | +0.0954 [+0.0396, +0.1520] | +0.0711 [+0.0381, +0.1107] |
| risk_quantile_skewt_base | -0.0169 [-0.0413, +0.0085] | +0.0220 [+0.0121, +0.0313] | +0.0136 [+0.0119, +0.0156] | +0.0015 [-0.0048, +0.0055] | +0.0242 [+0.0051, +0.0465] | +0.0244 [-0.0130, +0.0627] | +0.0028 [-0.0028, +0.0082] | +0.0724 [-0.0002, +0.1368] | +0.0602 [+0.0207, +0.1034] |


## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5), weighted rule

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| latent_factor | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| latent_factor_resid | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| latent_factor_logit | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| risk_gbm+latent_factor | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+latent_factor_resid | 0 of 4 | 13 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| risk_gbm+latent_factor_logit | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |

## Brier score and log loss at +5 bp, pooled by horizon

| row | h = 1 Brier / log loss | h = 2 Brier / log loss | h = 3 Brier / log loss | h = 4 Brier / log loss | h = 5 Brier / log loss |
|---|---|---|---|---|---|
| latent_factor | 0.0995 / 0.3705 | 0.1091 / 0.3975 | 0.1125 / 0.4061 | 0.1144 / 0.4030 | 0.1152 / 0.4042 |
| latent_factor_resid | 0.0997 / 0.3691 | 0.1092 / 0.3961 | 0.1127 / 0.4050 | 0.1145 / 0.4017 | 0.1153 / 0.4029 |
| latent_factor_logit | 0.0561 / 0.2024 | 0.0609 / 0.2190 | 0.0642 / 0.2427 | 0.0625 / 0.2262 | 0.0630 / 0.2360 |
| risk_gbm+latent_factor | 0.0842 / 0.3241 | 0.1028 / 0.3775 | 0.1037 / 0.3770 | 0.1053 / 0.3755 | 0.1086 / 0.3880 |
| risk_gbm+latent_factor_resid | 0.0844 / 0.3246 | 0.1030 / 0.3769 | 0.1039 / 0.3766 | 0.1054 / 0.3750 | 0.1088 / 0.3875 |
| risk_gbm+latent_factor_logit | 0.0480 / 0.1853 | 0.0608 / 0.2208 | 0.0611 / 0.2330 | 0.0595 / 0.2189 | 0.0626 / 0.2374 |
| risk_gbm | 0.0577 / 0.6598 | 0.0687 / 0.8020 | 0.0667 / 0.7889 | 0.0668 / 0.7921 | 0.0696 / 0.8044 |
| risk_gbm_base | 0.0592 / 0.6599 | 0.0691 / 0.8045 | 0.0677 / 0.7914 | 0.0668 / 0.7890 | 0.0696 / 0.8085 |
| risk_logistic | 0.0606 / 0.6775 | 0.0676 / 0.8012 | 0.0689 / 0.8060 | 0.0688 / 0.8073 | 0.0690 / 0.8166 |
| risk_logistic_base | 0.0596 / 0.6638 | 0.0672 / 0.7968 | 0.0689 / 0.7996 | 0.0689 / 0.8122 | 0.0687 / 0.8139 |
| risk_quantile_skewt_base | 0.0630 / 0.7127 | 0.0687 / 0.8316 | 0.0670 / 0.7958 | 0.0669 / 0.8027 | 0.0670 / 0.7932 |
| ngboost_laplace | 0.0462 / 0.1682 | 0.0568 / 0.2092 | 0.0595 / 0.2245 | 0.0615 / 0.2523 | 0.0637 / 0.2666 |
| calendar_climatology | 0.0714 / 0.2963 | 0.0711 / 0.2954 | 0.0707 / 0.2943 | 0.0708 / 0.2952 | 0.0709 / 0.2958 |
| persistence_logistic | 0.0563 / 0.2014 | 0.0611 / 0.2184 | 0.0644 / 0.2424 | 0.0624 / 0.2254 | 0.0634 / 0.2394 |

## latent_factor: onsets only this row warns

latent_factor warns 13 of 26 onsets; at least one of the five passers warns 16. 3 are warned by latent_factor and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by latent_factor: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### latent_factor: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 11 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 6 | 11 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 6 | 11 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 6 | 12 | 0 of 1869 | 1869 |

## latent_factor_resid: onsets only this row warns

latent_factor_resid warns 13 of 26 onsets; at least one of the five passers warns 16. 3 are warned by latent_factor_resid and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by latent_factor_resid: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### latent_factor_resid: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 6 | 11 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 6 | 11 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 6 | 11 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 6 | 11 | 0 of 1869 | 1869 |

## latent_factor_logit: onsets only this row warns

latent_factor_logit warns 12 of 26 onsets; at least one of the five passers warns 16. 4 are warned by latent_factor_logit and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)
* 2020-03-12 (flagged at h = 1, 5)

Warned by a passer and not by latent_factor_logit: 2019-01-15, 2019-01-31, 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15, 2025-12-15, 2025-12-26

### latent_factor_logit: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 7 | 9 | 0 of 1873 | 1873 |
| 2 | 90 | 0 | 0 | 7 | 9 | 0 of 1872 | 1872 |
| 3 | 90 | 0 | 0 | 7 | 10 | 0 of 1871 | 1871 |
| 4 | 90 | 1 | 0 | 7 | 9 | 0 of 1870 | 1870 |
| 5 | 89 | 0 | 0 | 7 | 10 | 0 of 1869 | 1869 |

## risk_gbm+latent_factor: onsets only this row warns

risk_gbm+latent_factor warns 15 of 26 onsets; at least one of the five passers warns 16. 3 are warned by risk_gbm+latent_factor and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_gbm+latent_factor: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+latent_factor: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 3 | 0 of 1873 | 1850 |
| 2 | 90 | 0 | 0 | 7 | 8 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 7 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 8 | 0 of 1869 | 1829 |

## risk_gbm+latent_factor_resid: onsets only this row warns

risk_gbm+latent_factor_resid warns 15 of 26 onsets; at least one of the five passers warns 16. 3 are warned by risk_gbm+latent_factor_resid and by none of the five passers:

* 2019-05-28 (flagged at h = 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)

Warned by a passer and not by risk_gbm+latent_factor_resid: 2024-09-30, 2025-09-15, 2025-09-30, 2025-10-15

### risk_gbm+latent_factor_resid: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 3 | 0 of 1873 | 1850 |
| 2 | 90 | 0 | 0 | 7 | 8 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 7 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 8 | 0 of 1869 | 1829 |

## risk_gbm+latent_factor_logit: onsets only this row warns

risk_gbm+latent_factor_logit warns 17 of 26 onsets; at least one of the five passers warns 16. 4 are warned by risk_gbm+latent_factor_logit and by none of the five passers:

* 2019-05-28 (flagged at h = 1, 2, 3, 4, 5)
* 2019-06-25 (flagged at h = 1, 2, 3, 4, 5)
* 2019-08-13 (flagged at h = 1, 2, 3, 4, 5)
* 2020-03-12 (flagged at h = 5)

Warned by a passer and not by risk_gbm+latent_factor_logit: 2024-09-30, 2025-09-15, 2025-10-15

### risk_gbm+latent_factor_logit: constant or degenerate refits

| h | refits | probability constant | all zero | cut-off flags nothing | cut-off flags every day | days at probability 0 | distinct probabilities |
|---|---|---|---|---|---|---|---|
| 1 | 90 | 0 | 0 | 5 | 5 | 0 of 1873 | 1850 |
| 2 | 90 | 0 | 0 | 7 | 8 | 0 of 1872 | 1830 |
| 3 | 90 | 0 | 0 | 7 | 9 | 0 of 1871 | 1822 |
| 4 | 90 | 1 | 0 | 7 | 7 | 0 of 1870 | 1824 |
| 5 | 89 | 0 | 0 | 7 | 7 | 0 of 1869 | 1829 |

## latent_factor against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.042 [-0.055, -0.027] |
| 2 | -0.040 [-0.056, -0.023] |
| 3 | -0.046 [-0.061, -0.029] |
| 4 | -0.048 [-0.062, -0.031] |
| 5 | -0.046 [-0.061, -0.029] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.025 [-0.022, 0.077] | 0.049 [-0.001, 0.104] | 0.048 [0.003, 0.097] |
| 2020 | 251 | -0.153 [-0.163, -0.140] | -0.161 [-0.175, -0.142] | -0.161 [-0.176, -0.143] |
| 2021-23 | 748 | -0.058 [-0.067, -0.050] | -0.076 [-0.085, -0.067] | -0.080 [-0.089, -0.071] |
| 2024 | 250 | -0.021 [-0.025, -0.016] | -0.027 [-0.031, -0.021] | -0.026 [-0.032, -0.017] |
| 2025-26 | 249 | -0.002 [-0.028, 0.028] | -0.001 [-0.023, 0.024] | 0.013 [-0.013, 0.045] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.075 [-0.093, -0.057] | -0.060 [-0.075, -0.044] | -0.050 [-0.066, -0.031] |
| ordinary | 1603 | -0.037 [-0.052, -0.021] | -0.043 [-0.060, -0.024] | -0.046 [-0.062, -0.027] |
| quarter_end | 31 | -0.075 [-0.138, -0.012] | -0.057 [-0.103, -0.010] | -0.052 [-0.103, -0.000] |
| tax_date | 89 | -0.054 [-0.085, -0.021] | -0.061 [-0.089, -0.032] | -0.038 [-0.074, 0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.038 [-0.044, -0.033] | -0.052 [-0.059, -0.045] | -0.054 [-0.061, -0.048] |
| 1 | 324 | -0.122 [-0.137, -0.104] | -0.133 [-0.148, -0.112] | -0.134 [-0.150, -0.114] |
| 2 | 41 | 0.073 [–] | 0.081 [–] | 0.093 [–] |
| 3 | 473 | -0.004 [-0.048, 0.043] | 0.016 [-0.031, 0.065] | 0.023 [-0.023, 0.069] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.174, 0.172] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.353] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [-0.111, 0.455] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.048 [-0.158, 0.250] |

## latent_factor against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.053 [-0.064, -0.044] |
| 2 | -0.052 [-0.063, -0.041] |
| 3 | -0.053 [-0.065, -0.040] |
| 4 | -0.053 [-0.066, -0.040] |
| 5 | -0.051 [-0.064, -0.038] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.027 [-0.053, -0.002] | 0.011 [-0.022, 0.049] | 0.024 [-0.009, 0.061] |
| 2020 | 251 | -0.146 [-0.157, -0.132] | -0.162 [-0.173, -0.148] | -0.160 [-0.169, -0.147] |
| 2021-23 | 748 | -0.058 [-0.067, -0.050] | -0.076 [-0.085, -0.067] | -0.080 [-0.089, -0.071] |
| 2024 | 250 | -0.021 [-0.025, -0.017] | -0.027 [-0.031, -0.021] | -0.026 [-0.032, -0.017] |
| 2025-26 | 249 | -0.016 [-0.034, 0.004] | 0.003 [-0.019, 0.030] | 0.004 [-0.019, 0.033] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.068 [-0.082, -0.055] | -0.044 [-0.063, -0.023] | -0.045 [-0.064, -0.024] |
| ordinary | 1603 | -0.051 [-0.062, -0.041] | -0.054 [-0.066, -0.042] | -0.052 [-0.065, -0.039] |
| quarter_end | 31 | -0.090 [-0.129, -0.051] | -0.067 [-0.099, -0.032] | -0.078 [-0.112, -0.043] |
| tax_date | 89 | -0.053 [-0.073, -0.033] | -0.046 [-0.070, -0.018] | -0.039 [-0.065, -0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.039 [-0.044, -0.034] | -0.052 [-0.059, -0.046] | -0.054 [-0.062, -0.047] |
| 1 | 324 | -0.121 [-0.134, -0.105] | -0.133 [-0.149, -0.113] | -0.134 [-0.149, -0.114] |
| 2 | 41 | 0.025 [–] | 0.068 [-0.066, 0.146] | 0.079 [–] |
| 3 | 473 | -0.044 [-0.070, -0.020] | -0.010 [-0.042, 0.025] | 0.000 [-0.032, 0.034] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.333, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
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
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.211, 0.091] |

## latent_factor against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.028 [-0.038, -0.016] |
| 2 | -0.038 [-0.049, -0.027] |
| 3 | -0.042 [-0.052, -0.031] |
| 4 | -0.044 [-0.054, -0.033] |
| 5 | -0.044 [-0.055, -0.034] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.027 [-0.010, 0.067] | 0.013 [-0.022, 0.047] | 0.011 [-0.019, 0.042] |
| 2020 | 251 | -0.113 [-0.123, -0.103] | -0.123 [-0.133, -0.112] | -0.125 [-0.134, -0.113] |
| 2021-23 | 748 | -0.044 [-0.052, -0.037] | -0.062 [-0.070, -0.055] | -0.066 [-0.074, -0.058] |
| 2024 | 250 | -0.017 [-0.020, -0.014] | -0.023 [-0.026, -0.020] | -0.024 [-0.027, -0.020] |
| 2025-26 | 249 | 0.013 [-0.010, 0.043] | 0.001 [-0.015, 0.021] | -0.001 [-0.017, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.020 [-0.038, -0.002] | -0.033 [-0.046, -0.019] | -0.036 [-0.049, -0.022] |
| ordinary | 1603 | -0.032 [-0.044, -0.019] | -0.046 [-0.057, -0.034] | -0.048 [-0.059, -0.036] |
| quarter_end | 31 | 0.040 [-0.039, 0.122] | 0.021 [-0.059, 0.108] | 0.011 [-0.076, 0.096] |
| tax_date | 89 | 0.014 [-0.000, 0.032] | -0.008 [-0.014, -0.001] | -0.012 [-0.019, -0.005] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.030 [-0.034, -0.026] | -0.043 [-0.048, -0.038] | -0.045 [-0.051, -0.040] |
| 1 | 324 | -0.093 [-0.104, -0.079] | -0.104 [-0.115, -0.089] | -0.107 [-0.118, -0.091] |
| 2 | 41 | 0.066 [–] | 0.050 [–] | 0.052 [-0.026, 0.094] |
| 3 | 473 | 0.011 [-0.022, 0.049] | -0.005 [-0.036, 0.026] | -0.007 [-0.036, 0.021] |

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
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.136] |

## latent_factor against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.043 [-0.053, -0.033] |
| 2 | -0.048 [-0.059, -0.037] |
| 3 | -0.048 [-0.058, -0.038] |
| 4 | -0.052 [-0.063, -0.041] |
| 5 | -0.052 [-0.062, -0.041] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.010 [-0.016, 0.037] | 0.013 [-0.013, 0.040] | 0.014 [-0.013, 0.042] |
| 2020 | 251 | -0.137 [-0.149, -0.121] | -0.135 [-0.143, -0.124] | -0.142 [-0.152, -0.130] |
| 2021-23 | 748 | -0.057 [-0.066, -0.049] | -0.072 [-0.080, -0.064] | -0.078 [-0.086, -0.069] |
| 2024 | 250 | -0.017 [-0.024, -0.008] | -0.023 [-0.028, -0.016] | -0.024 [-0.030, -0.016] |
| 2025-26 | 249 | -0.013 [-0.021, -0.004] | -0.006 [-0.017, 0.007] | -0.009 [-0.020, 0.006] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.042 [-0.057, -0.025] | -0.042 [-0.057, -0.027] | -0.045 [-0.060, -0.030] |
| ordinary | 1603 | -0.045 [-0.055, -0.035] | -0.050 [-0.060, -0.040] | -0.054 [-0.064, -0.043] |
| quarter_end | 31 | -0.020 [-0.055, 0.016] | -0.013 [-0.047, 0.023] | -0.014 [-0.051, 0.026] |
| tax_date | 89 | -0.021 [-0.046, 0.006] | -0.035 [-0.059, -0.010] | -0.038 [-0.063, -0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.038 [-0.044, -0.032] | -0.049 [-0.056, -0.043] | -0.053 [-0.060, -0.046] |
| 1 | 324 | -0.113 [-0.127, -0.096] | -0.114 [-0.127, -0.098] | -0.120 [-0.133, -0.102] |
| 2 | 41 | -0.024 [–] | 0.004 [–] | -0.024 [–] |
| 3 | 473 | -0.009 [-0.035, 0.017] | -0.005 [-0.032, 0.022] | -0.005 [-0.033, 0.025] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.080, 0.161] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.273] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.000 [-0.188, 0.222] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.100, 0.200] |

## latent_factor_resid against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.042 [-0.056, -0.026] |
| 2 | -0.041 [-0.056, -0.024] |
| 3 | -0.046 [-0.061, -0.029] |
| 4 | -0.048 [-0.063, -0.032] |
| 5 | -0.046 [-0.060, -0.029] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.026 [-0.023, 0.077] | 0.050 [0.003, 0.103] | 0.049 [0.002, 0.099] |
| 2020 | 251 | -0.153 [-0.163, -0.140] | -0.161 [-0.175, -0.142] | -0.161 [-0.176, -0.140] |
| 2021-23 | 748 | -0.059 [-0.067, -0.051] | -0.076 [-0.086, -0.068] | -0.080 [-0.089, -0.071] |
| 2024 | 250 | -0.021 [-0.025, -0.016] | -0.027 [-0.032, -0.021] | -0.026 [-0.032, -0.018] |
| 2025-26 | 249 | -0.003 [-0.026, 0.027] | -0.001 [-0.024, 0.026] | 0.013 [-0.014, 0.044] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.074 [-0.092, -0.057] | -0.060 [-0.075, -0.044] | -0.049 [-0.067, -0.031] |
| ordinary | 1603 | -0.038 [-0.053, -0.020] | -0.044 [-0.060, -0.025] | -0.046 [-0.062, -0.028] |
| quarter_end | 31 | -0.074 [-0.131, -0.012] | -0.056 [-0.103, -0.007] | -0.051 [-0.103, 0.003] |
| tax_date | 89 | -0.054 [-0.083, -0.018] | -0.060 [-0.089, -0.029] | -0.037 [-0.074, 0.007] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.039 [-0.044, -0.034] | -0.052 [-0.059, -0.046] | -0.055 [-0.062, -0.048] |
| 1 | 324 | -0.122 [-0.137, -0.102] | -0.133 [-0.149, -0.112] | -0.134 [-0.150, -0.114] |
| 2 | 41 | 0.074 [-0.080, 0.171] | 0.082 [–] | 0.094 [-0.024, 0.153] |
| 3 | 473 | -0.003 [-0.048, 0.045] | 0.017 [-0.028, 0.066] | 0.023 [-0.021, 0.068] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.176, 0.176] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.357] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [-0.125, 0.455] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.048 [-0.158, 0.250] |

## latent_factor_resid against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.053 [-0.063, -0.044] |
| 2 | -0.052 [-0.064, -0.041] |
| 3 | -0.053 [-0.065, -0.040] |
| 4 | -0.053 [-0.065, -0.040] |
| 5 | -0.052 [-0.065, -0.038] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.027 [-0.053, -0.001] | 0.012 [-0.019, 0.048] | 0.025 [-0.008, 0.063] |
| 2020 | 251 | -0.146 [-0.158, -0.132] | -0.162 [-0.172, -0.148] | -0.160 [-0.170, -0.148] |
| 2021-23 | 748 | -0.059 [-0.067, -0.051] | -0.076 [-0.085, -0.068] | -0.080 [-0.089, -0.072] |
| 2024 | 250 | -0.022 [-0.025, -0.017] | -0.027 [-0.031, -0.022] | -0.026 [-0.033, -0.017] |
| 2025-26 | 249 | -0.016 [-0.033, 0.005] | 0.003 [-0.019, 0.031] | 0.004 [-0.019, 0.033] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.068 [-0.081, -0.055] | -0.044 [-0.063, -0.024] | -0.045 [-0.063, -0.025] |
| ordinary | 1603 | -0.051 [-0.062, -0.041] | -0.054 [-0.066, -0.041] | -0.053 [-0.066, -0.039] |
| quarter_end | 31 | -0.089 [-0.132, -0.049] | -0.066 [-0.097, -0.031] | -0.077 [-0.109, -0.040] |
| tax_date | 89 | -0.052 [-0.070, -0.032] | -0.046 [-0.070, -0.018] | -0.038 [-0.065, -0.002] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.040 [-0.045, -0.035] | -0.053 [-0.059, -0.046] | -0.055 [-0.062, -0.048] |
| 1 | 324 | -0.121 [-0.134, -0.105] | -0.134 [-0.149, -0.113] | -0.134 [-0.150, -0.114] |
| 2 | 41 | 0.025 [–] | 0.069 [–] | 0.080 [–] |
| 3 | 473 | -0.044 [-0.069, -0.020] | -0.010 [-0.042, 0.025] | 0.001 [-0.032, 0.038] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.154 [-0.345, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.182] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | -0.083 [-0.333, 0.167] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.048 [-0.211, 0.100] |

## latent_factor_resid against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.028 [-0.039, -0.017] |
| 2 | -0.038 [-0.049, -0.027] |
| 3 | -0.042 [-0.052, -0.031] |
| 4 | -0.044 [-0.053, -0.033] |
| 5 | -0.044 [-0.055, -0.034] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.028 [-0.009, 0.070] | 0.013 [-0.021, 0.046] | 0.012 [-0.018, 0.044] |
| 2020 | 251 | -0.113 [-0.123, -0.103] | -0.123 [-0.134, -0.112] | -0.125 [-0.135, -0.113] |
| 2021-23 | 748 | -0.045 [-0.052, -0.038] | -0.063 [-0.070, -0.055] | -0.066 [-0.074, -0.059] |
| 2024 | 250 | -0.018 [-0.020, -0.014] | -0.023 [-0.026, -0.020] | -0.025 [-0.027, -0.021] |
| 2025-26 | 249 | 0.013 [-0.011, 0.044] | 0.000 [-0.016, 0.021] | -0.002 [-0.017, 0.017] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.020 [-0.038, -0.000] | -0.033 [-0.046, -0.018] | -0.036 [-0.049, -0.023] |
| ordinary | 1603 | -0.033 [-0.045, -0.021] | -0.046 [-0.057, -0.034] | -0.048 [-0.059, -0.037] |
| quarter_end | 31 | 0.042 [-0.038, 0.124] | 0.022 [-0.062, 0.108] | 0.012 [-0.073, 0.099] |
| tax_date | 89 | 0.015 [0.000, 0.033] | -0.007 [-0.014, -0.001] | -0.012 [-0.019, -0.004] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.030 [-0.034, -0.026] | -0.043 [-0.049, -0.038] | -0.046 [-0.052, -0.041] |
| 1 | 324 | -0.093 [-0.104, -0.080] | -0.104 [-0.116, -0.088] | -0.107 [-0.119, -0.091] |
| 2 | 41 | 0.066 [–] | 0.050 [-0.039, 0.108] | 0.053 [-0.028, 0.094] |
| 3 | 473 | 0.012 [-0.020, 0.048] | -0.005 [-0.035, 0.027] | -0.007 [-0.036, 0.023] |

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
| ordinary | 12 | 0.083 [0.000, 0.250] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.133] |

## latent_factor_resid against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.043 [-0.053, -0.033] |
| 2 | -0.048 [-0.059, -0.037] |
| 3 | -0.048 [-0.059, -0.038] |
| 4 | -0.052 [-0.063, -0.040] |
| 5 | -0.052 [-0.063, -0.041] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.011 [-0.015, 0.039] | 0.013 [-0.014, 0.042] | 0.015 [-0.013, 0.041] |
| 2020 | 251 | -0.137 [-0.149, -0.120] | -0.135 [-0.143, -0.124] | -0.142 [-0.152, -0.130] |
| 2021-23 | 748 | -0.058 [-0.067, -0.050] | -0.072 [-0.080, -0.064] | -0.078 [-0.087, -0.070] |
| 2024 | 250 | -0.017 [-0.024, -0.009] | -0.024 [-0.029, -0.017] | -0.024 [-0.031, -0.017] |
| 2025-26 | 249 | -0.013 [-0.022, -0.004] | -0.006 [-0.017, 0.007] | -0.009 [-0.020, 0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.041 [-0.058, -0.024] | -0.042 [-0.057, -0.027] | -0.045 [-0.061, -0.029] |
| ordinary | 1603 | -0.045 [-0.055, -0.035] | -0.050 [-0.061, -0.040] | -0.054 [-0.065, -0.044] |
| quarter_end | 31 | -0.018 [-0.054, 0.019] | -0.012 [-0.047, 0.025] | -0.013 [-0.052, 0.029] |
| tax_date | 89 | -0.021 [-0.045, 0.007] | -0.035 [-0.058, -0.009] | -0.037 [-0.063, -0.010] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.038 [-0.044, -0.033] | -0.050 [-0.056, -0.043] | -0.053 [-0.060, -0.046] |
| 1 | 324 | -0.113 [-0.127, -0.096] | -0.114 [-0.126, -0.097] | -0.120 [-0.134, -0.101] |
| 2 | 41 | -0.023 [–] | 0.005 [-0.055, 0.045] | -0.023 [-0.086, 0.014] |
| 3 | 473 | -0.008 [-0.034, 0.019] | -0.005 [-0.033, 0.025] | -0.004 [-0.033, 0.022] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.038 [-0.077, 0.167] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.273] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.000 [-0.188, 0.200] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.048 [-0.097, 0.200] |

## latent_factor_logit against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.002 [-0.006, 0.010] |
| 2 | 0.008 [0.000, 0.016] |
| 3 | 0.002 [-0.005, 0.011] |
| 4 | 0.004 [-0.002, 0.012] |
| 5 | 0.007 [-0.000, 0.014] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.016 [-0.018, 0.053] | 0.037 [0.008, 0.071] | 0.037 [0.009, 0.070] |
| 2020 | 251 | -0.017 [-0.024, -0.011] | -0.025 [-0.032, -0.017] | -0.019 [-0.026, -0.009] |
| 2021-23 | 748 | -0.001 [-0.001, -0.001] | -0.004 [-0.005, -0.003] | -0.002 [-0.003, -0.002] |
| 2024 | 250 | -0.002 [-0.004, 0.000] | -0.003 [-0.007, -0.000] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | 0.010 [-0.014, 0.038] | 0.004 [-0.017, 0.028] | 0.021 [-0.001, 0.049] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.034 [-0.059, -0.010] | -0.018 [-0.035, -0.004] | -0.004 [-0.017, 0.010] |
| ordinary | 1603 | 0.008 [-0.001, 0.018] | 0.007 [-0.002, 0.017] | 0.009 [0.001, 0.018] |
| quarter_end | 31 | -0.050 [-0.125, 0.019] | -0.041 [-0.099, 0.016] | -0.037 [-0.095, 0.019] |
| tax_date | 89 | -0.034 [-0.073, 0.002] | -0.025 [-0.061, 0.005] | 0.001 [-0.041, 0.042] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.000 [-0.001, 0.001] | -0.003 [-0.004, -0.002] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.010 [-0.012, -0.007] | -0.019 [-0.022, -0.015] | -0.014 [-0.017, -0.011] |
| 2 | 41 | 0.092 [–] | 0.075 [–] | 0.113 [–] |
| 3 | 473 | 0.006 [-0.022, 0.036] | 0.022 [-0.003, 0.050] | 0.030 [0.007, 0.057] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.038 [-0.250, 0.179] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [-0.176, 0.308] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.167 [-0.200, 0.500] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.000 [-0.250, 0.261] |

## latent_factor_logit against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.010 [-0.014, -0.005] |
| 2 | -0.004 [-0.009, 0.001] |
| 3 | -0.005 [-0.010, 0.001] |
| 4 | -0.001 [-0.007, 0.005] |
| 5 | 0.001 [-0.005, 0.007] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.037 [-0.053, -0.021] | -0.001 [-0.024, 0.023] | 0.013 [-0.014, 0.040] |
| 2020 | 251 | -0.010 [-0.016, -0.004] | -0.026 [-0.029, -0.022] | -0.018 [-0.022, -0.013] |
| 2021-23 | 748 | -0.001 [-0.001, -0.001] | -0.004 [-0.005, -0.003] | -0.002 [-0.003, -0.002] |
| 2024 | 250 | -0.002 [-0.005, -0.000] | -0.003 [-0.005, -0.002] | -0.001 [-0.002, 0.000] |
| 2025-26 | 249 | -0.003 [-0.023, 0.018] | 0.008 [-0.007, 0.028] | 0.013 [-0.007, 0.039] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.028 [-0.047, -0.010] | -0.002 [-0.015, 0.011] | 0.001 [-0.011, 0.013] |
| ordinary | 1603 | -0.006 [-0.010, -0.002] | -0.004 [-0.009, 0.002] | 0.002 [-0.005, 0.010] |
| quarter_end | 31 | -0.066 [-0.122, -0.011] | -0.050 [-0.091, -0.017] | -0.063 [-0.110, -0.022] |
| tax_date | 89 | -0.033 [-0.056, -0.012] | -0.010 [-0.027, 0.003] | 0.000 [-0.016, 0.017] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.000] | -0.003 [-0.004, -0.002] | -0.002 [-0.002, -0.001] |
| 1 | 324 | -0.009 [-0.012, -0.006] | -0.019 [-0.023, -0.015] | -0.014 [-0.017, -0.011] |
| 2 | 41 | 0.044 [–] | 0.061 [–] | 0.099 [-0.013, 0.180] |
| 3 | 473 | -0.035 [-0.048, -0.022] | -0.004 [-0.023, 0.015] | 0.007 [-0.014, 0.030] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.192 [-0.400, 0.000] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.125] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -1.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | -0.083 [-0.429, 0.222] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.400 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | -0.095 [-0.318, 0.111] |

## latent_factor_logit against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.015 [0.010, 0.021] |
| 2 | 0.010 [0.006, 0.014] |
| 3 | 0.007 [0.003, 0.010] |
| 4 | 0.008 [0.005, 0.012] |
| 5 | 0.008 [0.004, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.018 [-0.002, 0.040] | 0.001 [-0.015, 0.016] | -0.000 [-0.014, 0.014] |
| 2020 | 251 | 0.023 [0.013, 0.032] | 0.012 [0.006, 0.020] | 0.017 [0.011, 0.025] |
| 2021-23 | 748 | 0.013 [0.011, 0.015] | 0.010 [0.008, 0.011] | 0.011 [0.010, 0.013] |
| 2024 | 250 | 0.002 [-0.001, 0.005] | 0.001 [-0.003, 0.003] | 0.001 [-0.004, 0.004] |
| 2025-26 | 249 | 0.025 [0.002, 0.053] | 0.006 [-0.005, 0.020] | 0.007 [-0.008, 0.025] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.020 [0.004, 0.040] | 0.009 [0.003, 0.017] | 0.009 [0.002, 0.017] |
| ordinary | 1603 | 0.013 [0.008, 0.019] | 0.004 [0.001, 0.008] | 0.006 [0.003, 0.010] |
| quarter_end | 31 | 0.065 [-0.039, 0.169] | 0.038 [-0.070, 0.145] | 0.026 [-0.088, 0.136] |
| tax_date | 89 | 0.034 [0.010, 0.057] | 0.028 [0.006, 0.048] | 0.027 [0.004, 0.048] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.009 [0.007, 0.010] | 0.006 [0.005, 0.008] | 0.007 [0.006, 0.009] |
| 1 | 324 | 0.020 [0.014, 0.026] | 0.010 [0.006, 0.015] | 0.013 [0.009, 0.018] |
| 2 | 41 | 0.085 [–] | 0.043 [–] | 0.072 [-0.003, 0.133] |
| 3 | 473 | 0.021 [0.004, 0.040] | 0.001 [-0.012, 0.013] | -0.000 [-0.012, 0.012] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.143, 0.133] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | -0.059 [-0.250, 0.118] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | -0.167 [–] |
| ordinary | 12 | 0.083 [-0.154, 0.308] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.000 [-0.174, 0.167] |

## latent_factor_logit against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.000 [-0.000, 0.001] |
| 2 | 0.000 [-0.000, 0.001] |
| 3 | 0.000 [-0.001, 0.001] |
| 4 | -0.000 [-0.001, 0.001] |
| 5 | 0.000 [-0.001, 0.002] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.001 [-0.001, 0.003] | 0.001 [-0.003, 0.004] | 0.003 [-0.003, 0.008] |
| 2020 | 251 | -0.001 [-0.001, 0.000] | 0.001 [0.000, 0.001] | -0.000 [-0.001, 0.000] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] | -0.000 [-0.000, -0.000] |
| 2024 | 250 | 0.002 [-0.000, 0.006] | 0.000 [-0.000, 0.001] | 0.001 [-0.000, 0.003] |
| 2025-26 | 249 | -0.000 [-0.003, 0.002] | -0.000 [-0.002, 0.001] | -0.001 [-0.003, 0.002] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.003, 0.001] | -0.000 [-0.001, 0.000] | -0.000 [-0.002, 0.002] |
| ordinary | 1603 | 0.000 [-0.000, 0.001] | 0.000 [-0.001, 0.001] | 0.000 [-0.001, 0.002] |
| quarter_end | 31 | 0.005 [-0.000, 0.011] | 0.003 [0.001, 0.005] | 0.001 [-0.001, 0.003] |
| tax_date | 89 | -0.001 [-0.003, 0.001] | 0.001 [-0.000, 0.002] | 0.001 [-0.000, 0.003] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.001 [-0.000, 0.001] | 0.000 [-0.000, 0.000] | 0.000 [-0.000, 0.001] |
| 1 | 324 | -0.001 [-0.001, -0.000] | 0.000 [0.000, 0.001] | -0.000 [-0.001, 0.000] |
| 2 | 41 | -0.005 [-0.018, 0.007] | -0.003 [–] | -0.004 [-0.014, 0.007] |
| 3 | 473 | 0.001 [-0.001, 0.002] | 0.001 [-0.002, 0.003] | 0.002 [-0.003, 0.006] |

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

## risk_gbm+latent_factor against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.026 [-0.040, -0.012] |
| 2 | -0.034 [-0.048, -0.018] |
| 3 | -0.037 [-0.052, -0.023] |
| 4 | -0.038 [-0.053, -0.023] |
| 5 | -0.039 [-0.053, -0.024] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [-0.004, 0.101] | 0.049 [-0.001, 0.102] | 0.049 [0.002, 0.101] |
| 2020 | 251 | -0.120 [-0.132, -0.106] | -0.136 [-0.152, -0.116] | -0.137 [-0.154, -0.117] |
| 2021-23 | 748 | -0.046 [-0.053, -0.040] | -0.065 [-0.074, -0.057] | -0.069 [-0.078, -0.061] |
| 2024 | 250 | -0.017 [-0.020, -0.014] | -0.022 [-0.026, -0.016] | -0.023 [-0.028, -0.017] |
| 2025-26 | 249 | 0.007 [-0.015, 0.033] | 0.004 [-0.017, 0.028] | 0.003 [-0.017, 0.027] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.009, 0.010] | -0.009 [-0.017, 0.001] | -0.010 [-0.018, -0.001] |
| ordinary | 1603 | -0.031 [-0.046, -0.015] | -0.042 [-0.059, -0.026] | -0.045 [-0.060, -0.027] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.031 [-0.035, -0.027] | -0.045 [-0.050, -0.039] | -0.047 [-0.053, -0.041] |
| 1 | 324 | -0.095 [-0.107, -0.081] | -0.114 [-0.128, -0.096] | -0.117 [-0.130, -0.100] |
| 2 | 41 | 0.063 [–] | 0.066 [–] | 0.073 [–] |
| 3 | 473 | 0.023 [-0.021, 0.068] | 0.023 [-0.021, 0.071] | 0.022 [-0.020, 0.068] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.056, 0.219] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.364] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.000, 0.500] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.143 [0.000, 0.300] |

## risk_gbm+latent_factor against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.038 [-0.047, -0.028] |
| 2 | -0.046 [-0.056, -0.036] |
| 3 | -0.044 [-0.056, -0.032] |
| 4 | -0.044 [-0.055, -0.032] |
| 5 | -0.045 [-0.057, -0.033] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.033, 0.025] | 0.011 [-0.023, 0.048] | 0.024 [-0.012, 0.061] |
| 2020 | 251 | -0.113 [-0.127, -0.098] | -0.137 [-0.150, -0.123] | -0.137 [-0.148, -0.123] |
| 2021-23 | 748 | -0.046 [-0.053, -0.039] | -0.065 [-0.074, -0.057] | -0.069 [-0.077, -0.060] |
| 2024 | 250 | -0.017 [-0.020, -0.015] | -0.022 [-0.027, -0.015] | -0.023 [-0.028, -0.016] |
| 2025-26 | 249 | -0.007 [-0.025, 0.014] | 0.008 [-0.017, 0.037] | -0.006 [-0.026, 0.018] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.006 [-0.007, 0.018] | 0.007 [-0.012, 0.029] | -0.005 [-0.017, 0.010] |
| ordinary | 1603 | -0.045 [-0.054, -0.034] | -0.053 [-0.065, -0.041] | -0.051 [-0.065, -0.038] |
| quarter_end | 31 | -0.015 [-0.062, 0.027] | -0.010 [-0.074, 0.050] | -0.026 [-0.083, 0.026] |
| tax_date | 89 | 0.002 [-0.031, 0.031] | 0.015 [-0.009, 0.043] | -0.001 [-0.045, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.032 [-0.036, -0.028] | -0.045 [-0.051, -0.039] | -0.047 [-0.053, -0.040] |
| 1 | 324 | -0.094 [-0.105, -0.081] | -0.114 [-0.128, -0.097] | -0.116 [-0.130, -0.099] |
| 2 | 41 | 0.015 [–] | 0.052 [–] | 0.059 [–] |
| 3 | 473 | -0.018 [-0.042, 0.011] | -0.003 [-0.036, 0.033] | -0.001 [-0.038, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.233, 0.057] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.176] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [-0.201, 0.200] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.137] |

## risk_gbm+latent_factor against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.013 [-0.024, 0.000] |
| 2 | -0.032 [-0.042, -0.021] |
| 3 | -0.033 [-0.043, -0.022] |
| 4 | -0.034 [-0.044, -0.025] |
| 5 | -0.038 [-0.047, -0.028] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.048 [0.006, 0.093] | 0.013 [-0.020, 0.049] | 0.012 [-0.021, 0.042] |
| 2020 | 251 | -0.080 [-0.094, -0.065] | -0.099 [-0.113, -0.084] | -0.101 [-0.115, -0.087] |
| 2021-23 | 748 | -0.032 [-0.038, -0.026] | -0.052 [-0.059, -0.045] | -0.055 [-0.062, -0.048] |
| 2024 | 250 | -0.013 [-0.016, -0.009] | -0.018 [-0.023, -0.012] | -0.022 [-0.024, -0.018] |
| 2025-26 | 249 | 0.022 [-0.008, 0.059] | 0.006 [-0.014, 0.030] | -0.012 [-0.026, 0.004] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.054 [0.029, 0.081] | 0.018 [0.004, 0.035] | 0.004 [-0.004, 0.013] |
| ordinary | 1603 | -0.026 [-0.038, -0.013] | -0.045 [-0.056, -0.032] | -0.047 [-0.058, -0.036] |
| quarter_end | 31 | 0.116 [0.037, 0.195] | 0.078 [-0.010, 0.168] | 0.063 [-0.020, 0.151] |
| tax_date | 89 | 0.069 [0.043, 0.095] | 0.053 [0.026, 0.080] | 0.026 [-0.014, 0.060] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.022 [-0.026, -0.019] | -0.035 [-0.040, -0.031] | -0.038 [-0.043, -0.033] |
| 1 | 324 | -0.066 [-0.076, -0.054] | -0.085 [-0.096, -0.072] | -0.089 [-0.100, -0.075] |
| 2 | 41 | 0.056 [–] | 0.034 [–] | 0.032 [–] |
| 3 | 473 | 0.038 [0.001, 0.077] | 0.002 [-0.029, 0.035] | -0.009 [-0.039, 0.020] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [0.000, 0.250] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [0.000, 0.375] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.143 [0.000, 0.300] |

## risk_gbm+latent_factor against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.028 [-0.038, -0.017] |
| 2 | -0.042 [-0.052, -0.031] |
| 3 | -0.039 [-0.049, -0.029] |
| 4 | -0.043 [-0.053, -0.033] |
| 5 | -0.045 [-0.055, -0.035] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.031 [-0.001, 0.066] | 0.013 [-0.017, 0.043] | 0.014 [-0.015, 0.044] |
| 2020 | 251 | -0.103 [-0.118, -0.086] | -0.110 [-0.121, -0.099] | -0.119 [-0.130, -0.107] |
| 2021-23 | 748 | -0.045 [-0.052, -0.039] | -0.061 [-0.069, -0.054] | -0.067 [-0.075, -0.059] |
| 2024 | 250 | -0.013 [-0.019, -0.006] | -0.019 [-0.025, -0.010] | -0.021 [-0.026, -0.015] |
| 2025-26 | 249 | -0.003 [-0.020, 0.016] | -0.001 [-0.019, 0.022] | -0.019 [-0.032, -0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.032 [0.008, 0.058] | 0.009 [-0.007, 0.027] | -0.005 [-0.018, 0.008] |
| ordinary | 1603 | -0.038 [-0.048, -0.028] | -0.049 [-0.059, -0.039] | -0.053 [-0.064, -0.042] |
| quarter_end | 31 | 0.055 [-0.018, 0.130] | 0.044 [-0.012, 0.101] | 0.038 [-0.018, 0.095] |
| tax_date | 89 | 0.033 [-0.001, 0.069] | 0.026 [-0.006, 0.062] | 0.000 [-0.045, 0.044] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.030 [-0.035, -0.026] | -0.042 [-0.048, -0.036] | -0.045 [-0.051, -0.039] |
| 1 | 324 | -0.086 [-0.097, -0.073] | -0.095 [-0.106, -0.081] | -0.102 [-0.114, -0.087] |
| 2 | 41 | -0.034 [–] | -0.012 [–] | -0.044 [-0.099, 0.003] |
| 3 | 473 | 0.018 [-0.014, 0.050] | 0.002 [-0.027, 0.031] | -0.006 [-0.035, 0.022] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.038, 0.280] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.286] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.083 [-0.154, 0.334] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.143 [-0.050, 0.345] |

## risk_gbm+latent_factor_resid against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.027 [-0.040, -0.012] |
| 2 | -0.034 [-0.049, -0.019] |
| 3 | -0.037 [-0.052, -0.021] |
| 4 | -0.039 [-0.053, -0.023] |
| 5 | -0.039 [-0.053, -0.023] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.047 [-0.004, 0.099] | 0.050 [-0.001, 0.104] | 0.049 [0.002, 0.100] |
| 2020 | 251 | -0.120 [-0.132, -0.107] | -0.136 [-0.152, -0.116] | -0.138 [-0.154, -0.120] |
| 2021-23 | 748 | -0.046 [-0.054, -0.040] | -0.066 [-0.075, -0.058] | -0.069 [-0.078, -0.061] |
| 2024 | 250 | -0.017 [-0.020, -0.014] | -0.023 [-0.027, -0.016] | -0.023 [-0.028, -0.017] |
| 2025-26 | 249 | 0.006 [-0.015, 0.032] | 0.004 [-0.017, 0.030] | 0.003 [-0.017, 0.028] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | -0.001 [-0.009, 0.010] | -0.009 [-0.017, 0.001] | -0.010 [-0.018, -0.000] |
| ordinary | 1603 | -0.031 [-0.047, -0.015] | -0.043 [-0.059, -0.024] | -0.045 [-0.061, -0.026] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.031 [-0.036, -0.027] | -0.045 [-0.051, -0.039] | -0.047 [-0.053, -0.041] |
| 1 | 324 | -0.096 [-0.107, -0.081] | -0.114 [-0.128, -0.096] | -0.117 [-0.131, -0.099] |
| 2 | 41 | 0.064 [–] | 0.066 [–] | 0.074 [-0.022, 0.124] |
| 3 | 473 | 0.023 [-0.022, 0.069] | 0.024 [-0.023, 0.074] | 0.022 [-0.020, 0.068] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.077 [-0.050, 0.216] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.357] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.200 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.000, 0.500] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.143 [0.000, 0.286] |

## risk_gbm+latent_factor_resid against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.038 [-0.047, -0.029] |
| 2 | -0.046 [-0.057, -0.035] |
| 3 | -0.044 [-0.056, -0.032] |
| 4 | -0.044 [-0.055, -0.031] |
| 5 | -0.045 [-0.057, -0.033] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.006 [-0.033, 0.023] | 0.011 [-0.021, 0.048] | 0.025 [-0.011, 0.063] |
| 2020 | 251 | -0.113 [-0.128, -0.098] | -0.137 [-0.150, -0.123] | -0.137 [-0.148, -0.123] |
| 2021-23 | 748 | -0.046 [-0.054, -0.040] | -0.066 [-0.074, -0.057] | -0.069 [-0.077, -0.061] |
| 2024 | 250 | -0.018 [-0.020, -0.015] | -0.023 [-0.028, -0.015] | -0.023 [-0.028, -0.017] |
| 2025-26 | 249 | -0.007 [-0.024, 0.014] | 0.008 [-0.017, 0.038] | -0.006 [-0.027, 0.019] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.006 [-0.007, 0.018] | 0.007 [-0.011, 0.027] | -0.005 [-0.017, 0.009] |
| ordinary | 1603 | -0.045 [-0.055, -0.035] | -0.053 [-0.065, -0.041] | -0.052 [-0.065, -0.039] |
| quarter_end | 31 | -0.015 [-0.063, 0.026] | -0.010 [-0.071, 0.048] | -0.026 [-0.084, 0.026] |
| tax_date | 89 | 0.002 [-0.030, 0.030] | 0.015 [-0.009, 0.042] | -0.001 [-0.041, 0.038] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.032 [-0.036, -0.028] | -0.045 [-0.051, -0.039] | -0.047 [-0.053, -0.041] |
| 1 | 324 | -0.095 [-0.105, -0.082] | -0.115 [-0.128, -0.097] | -0.116 [-0.130, -0.100] |
| 2 | 41 | 0.015 [-0.085, 0.094] | 0.053 [-0.068, 0.127] | 0.060 [-0.049, 0.121] |
| 3 | 473 | -0.018 [-0.044, 0.009] | -0.003 [-0.036, 0.033] | -0.001 [-0.036, 0.035] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: -0.077 [-0.231, 0.053] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.176] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.000 [–] |
| quarter_end | 3 | -0.333 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -1.000 [–] |
| 3 | 21 | 0.048 [0.000, 0.143] |

## risk_gbm+latent_factor_resid against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.013 [-0.025, -0.000] |
| 2 | -0.032 [-0.042, -0.022] |
| 3 | -0.033 [-0.043, -0.023] |
| 4 | -0.035 [-0.044, -0.025] |
| 5 | -0.038 [-0.047, -0.028] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.048 [0.008, 0.095] | 0.013 [-0.021, 0.048] | 0.012 [-0.020, 0.044] |
| 2020 | 251 | -0.080 [-0.094, -0.065] | -0.099 [-0.113, -0.084] | -0.101 [-0.114, -0.087] |
| 2021-23 | 748 | -0.033 [-0.039, -0.027] | -0.052 [-0.060, -0.045] | -0.055 [-0.063, -0.048] |
| 2024 | 250 | -0.014 [-0.017, -0.010] | -0.019 [-0.023, -0.013] | -0.022 [-0.025, -0.019] |
| 2025-26 | 249 | 0.022 [-0.008, 0.061] | 0.005 [-0.015, 0.029] | -0.012 [-0.028, 0.005] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.054 [0.028, 0.081] | 0.018 [0.004, 0.035] | 0.004 [-0.005, 0.012] |
| ordinary | 1603 | -0.026 [-0.039, -0.012] | -0.045 [-0.056, -0.033] | -0.047 [-0.058, -0.036] |
| quarter_end | 31 | 0.116 [0.035, 0.202] | 0.078 [-0.008, 0.166] | 0.063 [-0.028, 0.153] |
| tax_date | 89 | 0.069 [0.043, 0.096] | 0.053 [0.025, 0.080] | 0.026 [-0.015, 0.061] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.023 [-0.026, -0.019] | -0.036 [-0.041, -0.031] | -0.038 [-0.043, -0.033] |
| 1 | 324 | -0.066 [-0.076, -0.054] | -0.085 [-0.097, -0.072] | -0.089 [-0.101, -0.075] |
| 2 | 41 | 0.056 [–] | 0.035 [–] | 0.033 [–] |
| 3 | 473 | 0.038 [-0.001, 0.080] | 0.002 [-0.030, 0.034] | -0.008 [-0.038, 0.021] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [0.000, 0.241] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.167 [0.000, 0.364] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.143 [0.000, 0.300] |

## risk_gbm+latent_factor_resid against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.028 [-0.038, -0.017] |
| 2 | -0.042 [-0.052, -0.032] |
| 3 | -0.040 [-0.049, -0.030] |
| 4 | -0.043 [-0.053, -0.033] |
| 5 | -0.045 [-0.056, -0.035] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.031 [0.000, 0.065] | 0.013 [-0.015, 0.043] | 0.015 [-0.016, 0.044] |
| 2020 | 251 | -0.104 [-0.118, -0.088] | -0.111 [-0.120, -0.099] | -0.119 [-0.130, -0.107] |
| 2021-23 | 748 | -0.046 [-0.052, -0.039] | -0.062 [-0.069, -0.055] | -0.067 [-0.075, -0.059] |
| 2024 | 250 | -0.013 [-0.019, -0.006] | -0.019 [-0.025, -0.010] | -0.022 [-0.027, -0.016] |
| 2025-26 | 249 | -0.004 [-0.021, 0.016] | -0.001 [-0.019, 0.022] | -0.020 [-0.033, -0.007] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.032 [0.009, 0.058] | 0.009 [-0.007, 0.027] | -0.005 [-0.019, 0.008] |
| ordinary | 1603 | -0.039 [-0.049, -0.029] | -0.049 [-0.059, -0.039] | -0.053 [-0.064, -0.042] |
| quarter_end | 31 | 0.055 [-0.019, 0.129] | 0.044 [-0.014, 0.102] | 0.038 [-0.019, 0.096] |
| tax_date | 89 | 0.033 [-0.001, 0.070] | 0.026 [-0.006, 0.061] | 0.000 [-0.044, 0.046] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.031 [-0.035, -0.026] | -0.042 [-0.048, -0.037] | -0.045 [-0.052, -0.039] |
| 1 | 324 | -0.087 [-0.097, -0.073] | -0.095 [-0.106, -0.082] | -0.103 [-0.115, -0.088] |
| 2 | 41 | -0.034 [-0.115, 0.024] | -0.011 [-0.060, 0.035] | -0.043 [–] |
| 3 | 473 | 0.018 [-0.014, 0.048] | 0.002 [-0.027, 0.032] | -0.006 [-0.036, 0.023] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.115 [-0.036, 0.276] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.286] |
| 2020 | 2 | -0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.083 [-0.143, 0.333] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.143 [-0.045, 0.333] |

## risk_gbm+latent_factor_logit against risk_gbm

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.010 [0.002, 0.019] |
| 2 | 0.008 [0.000, 0.017] |
| 3 | 0.006 [-0.001, 0.014] |
| 4 | 0.007 [0.000, 0.015] |
| 5 | 0.007 [0.000, 0.015] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.052 [0.018, 0.090] | 0.045 [0.014, 0.077] | 0.045 [0.016, 0.078] |
| 2020 | 251 | -0.015 [-0.022, -0.011] | -0.022 [-0.029, -0.014] | -0.018 [-0.025, -0.010] |
| 2021-23 | 748 | -0.001 [-0.001, -0.001] | -0.004 [-0.005, -0.003] | -0.002 [-0.003, -0.002] |
| 2024 | 250 | -0.000 [-0.001, -0.000] | -0.001 [-0.002, -0.000] | -0.000 [-0.001, 0.001] |
| 2025-26 | 249 | 0.014 [-0.002, 0.035] | 0.010 [-0.003, 0.027] | 0.011 [-0.006, 0.031] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.005 [-0.001, 0.012] | 0.002 [-0.002, 0.006] | 0.002 [-0.002, 0.006] |
| ordinary | 1603 | 0.011 [0.002, 0.021] | 0.006 [-0.002, 0.016] | 0.008 [-0.000, 0.017] |
| quarter_end | 31 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| tax_date | 89 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.001, -0.000] | -0.002 [-0.003, -0.002] | -0.001 [-0.002, -0.001] |
| 1 | 324 | -0.008 [-0.010, -0.006] | -0.017 [-0.020, -0.014] | -0.013 [-0.016, -0.011] |
| 2 | 41 | 0.069 [–] | 0.056 [–] | 0.083 [–] |
| 3 | 473 | 0.039 [0.011, 0.071] | 0.034 [0.008, 0.062] | 0.033 [0.008, 0.061] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.154 [0.043, 0.280] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.176 [0.000, 0.357] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.000 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.333 [0.111, 0.562] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | 0.000 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.000 [–] |
| 3 | 21 | 0.190 [0.056, 0.346] |

## risk_gbm+latent_factor_logit against ngboost_laplace

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | -0.002 [-0.005, 0.002] |
| 2 | -0.004 [-0.008, 0.000] |
| 3 | -0.002 [-0.007, 0.005] |
| 4 | 0.002 [-0.004, 0.008] |
| 5 | 0.001 [-0.005, 0.008] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | -0.001 [-0.015, 0.013] | 0.006 [-0.017, 0.034] | 0.021 [-0.006, 0.051] |
| 2020 | 251 | -0.009 [-0.015, -0.003] | -0.023 [-0.027, -0.019] | -0.017 [-0.022, -0.013] |
| 2021-23 | 748 | -0.001 [-0.001, -0.001] | -0.004 [-0.005, -0.003] | -0.002 [-0.003, -0.002] |
| 2024 | 250 | -0.001 [-0.001, -0.001] | -0.001 [-0.004, 0.002] | -0.000 [-0.002, 0.001] |
| 2025-26 | 249 | 0.001 [-0.014, 0.017] | 0.014 [-0.004, 0.035] | 0.002 [-0.020, 0.026] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.011 [-0.000, 0.023] | 0.017 [-0.000, 0.037] | 0.006 [-0.006, 0.020] |
| ordinary | 1603 | -0.003 [-0.006, 0.000] | -0.004 [-0.009, 0.001] | 0.001 [-0.005, 0.008] |
| quarter_end | 31 | -0.015 [-0.063, 0.027] | -0.010 [-0.070, 0.051] | -0.026 [-0.083, 0.027] |
| tax_date | 89 | 0.002 [-0.032, 0.030] | 0.015 [-0.010, 0.042] | -0.001 [-0.044, 0.040] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | -0.001 [-0.002, -0.001] | -0.003 [-0.004, -0.002] | -0.001 [-0.002, -0.001] |
| 1 | 324 | -0.007 [-0.011, -0.004] | -0.017 [-0.020, -0.014] | -0.013 [-0.016, -0.010] |
| 2 | 41 | 0.020 [–] | 0.042 [–] | 0.069 [–] |
| 3 | 473 | -0.001 [-0.013, 0.010] | 0.008 [-0.012, 0.030] | 0.011 [-0.012, 0.036] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.000 [-0.136, 0.130] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | -0.400 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.083 [-0.167, 0.308] |
| quarter_end | 3 | 0.000 [–] |
| tax_date | 5 | -0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | -1.000 [–] |
| 2 | 2 | -0.500 [–] |
| 3 | 21 | 0.095 [0.000, 0.208] |

## risk_gbm+latent_factor_logit against calendar_climatology

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.023 [0.017, 0.031] |
| 2 | 0.010 [0.006, 0.015] |
| 3 | 0.010 [0.006, 0.014] |
| 4 | 0.011 [0.008, 0.015] |
| 5 | 0.008 [0.004, 0.012] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.053 [0.027, 0.082] | 0.008 [-0.008, 0.024] | 0.008 [-0.005, 0.022] |
| 2020 | 251 | 0.024 [0.014, 0.035] | 0.015 [0.008, 0.023] | 0.018 [0.011, 0.025] |
| 2021-23 | 748 | 0.013 [0.011, 0.015] | 0.010 [0.009, 0.012] | 0.012 [0.010, 0.013] |
| 2024 | 250 | 0.003 [-0.000, 0.006] | 0.003 [-0.001, 0.006] | 0.001 [-0.003, 0.004] |
| 2025-26 | 249 | 0.029 [0.003, 0.059] | 0.012 [-0.002, 0.029] | -0.003 [-0.023, 0.013] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.059 [0.034, 0.087] | 0.029 [0.017, 0.044] | 0.015 [0.008, 0.023] |
| ordinary | 1603 | 0.016 [0.010, 0.023] | 0.004 [0.001, 0.008] | 0.006 [0.003, 0.009] |
| quarter_end | 31 | 0.116 [0.031, 0.194] | 0.078 [-0.012, 0.170] | 0.063 [-0.028, 0.151] |
| tax_date | 89 | 0.069 [0.042, 0.096] | 0.053 [0.025, 0.082] | 0.026 [-0.018, 0.060] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.008 [0.006, 0.010] | 0.007 [0.005, 0.008] | 0.008 [0.006, 0.009] |
| 1 | 324 | 0.022 [0.015, 0.028] | 0.012 [0.007, 0.018] | 0.014 [0.009, 0.019] |
| 2 | 41 | 0.061 [–] | 0.024 [–] | 0.042 [–] |
| 3 | 473 | 0.055 [0.032, 0.080] | 0.013 [-0.001, 0.027] | 0.003 [-0.011, 0.016] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.192 [0.071, 0.333] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.059 [0.000, 0.167] |
| 2020 | 2 | 0.500 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.000 [–] |
| ordinary | 12 | 0.250 [0.071, 0.462] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.190 [0.053, 0.357] |

## risk_gbm+latent_factor_logit against persistence_logistic

Brier difference, reference minus row (positive: the row is better), 90% interval.

| h | pooled |
|---|---|
| 1 | 0.008 [0.004, 0.013] |
| 2 | 0.000 [-0.003, 0.003] |
| 3 | 0.003 [0.000, 0.006] |
| 4 | 0.003 [0.001, 0.005] |
| 5 | 0.001 [-0.002, 0.004] |

By regime, Brier difference at h = 1 / 3 / 5:

| regime | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 2018-19 | 375 | 0.036 [0.020, 0.054] | 0.008 [-0.003, 0.019] | 0.011 [-0.001, 0.023] |
| 2020 | 251 | 0.001 [-0.003, 0.004] | 0.004 [0.002, 0.005] | 0.000 [-0.002, 0.002] |
| 2021-23 | 748 | -0.000 [-0.000, -0.000] | 0.000 [0.000, 0.001] | -0.000 [-0.000, 0.000] |
| 2024 | 250 | 0.003 [-0.000, 0.008] | 0.002 [-0.000, 0.007] | 0.001 [-0.000, 0.003] |
| 2025-26 | 249 | 0.004 [-0.011, 0.021] | 0.005 [-0.008, 0.021] | -0.011 [-0.023, -0.001] |

By day_type, Brier difference at h = 1 / 3 / 5:

| day_type | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| month_end | 150 | 0.038 [0.015, 0.064] | 0.019 [0.005, 0.035] | 0.006 [-0.008, 0.019] |
| ordinary | 1603 | 0.003 [0.000, 0.006] | -0.000 [-0.001, 0.001] | -0.000 [-0.002, 0.001] |
| quarter_end | 31 | 0.055 [-0.014, 0.129] | 0.044 [-0.015, 0.103] | 0.038 [-0.015, 0.096] |
| tax_date | 89 | 0.033 [-0.002, 0.070] | 0.026 [-0.006, 0.061] | 0.000 [-0.044, 0.045] |

By scarcity_state, Brier difference at h = 1 / 3 / 5:

| scarcity_state | days | h = 1 | h = 3 | h = 5 |
|---|---|---|---|---|
| 0 | 1035 | 0.000 [-0.001, 0.001] | 0.000 [-0.001, 0.002] | 0.000 [-0.000, 0.001] |
| 1 | 324 | 0.001 [-0.000, 0.002] | 0.002 [0.001, 0.004] | 0.001 [-0.001, 0.002] |
| 2 | 41 | -0.028 [–] | -0.022 [–] | -0.034 [–] |
| 3 | 473 | 0.034 [0.020, 0.050] | 0.013 [0.002, 0.023] | 0.005 [-0.006, 0.016] |

Onset recall difference, row minus reference (each at its own cut-offs, any horizon), pooled: 0.192 [0.050, 0.348] on 26 onsets.

| regime | onsets | recall difference [90%] |
|---|---|---|
| 2018-19 | 17 | 0.118 [0.000, 0.281] |
| 2020 | 2 | 0.000 [–] |
| 2021-23 | 0 | – [–] |
| 2024 | 2 | 0.000 [–] |
| 2025-26 | 5 | 0.600 [–] |

| day_type | onsets | recall difference [90%] |
|---|---|---|
| month_end | 6 | 0.167 [–] |
| ordinary | 12 | 0.167 [0.000, 0.375] |
| quarter_end | 3 | 0.333 [–] |
| tax_date | 5 | 0.200 [–] |

| scarcity_state | onsets | recall difference [90%] |
|---|---|---|
| 0 | 2 | 0.000 [–] |
| 1 | 1 | 0.000 [–] |
| 2 | 2 | 0.500 [–] |
| 3 | 21 | 0.190 [0.040, 0.381] |

